# utils/user_manager.py
from __future__ import annotations

import os
import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from psycopg_pool import ConnectionPool
from passlib.hash import pbkdf2_sha256

from utils.auth import hash_password, verify_password, create_jwt, verify_jwt
from utils.rate_limiter import get_rate_limit_info, RateLimitInfo
from utils.logger import setup_logger

logger = setup_logger(__name__)


class UserManager:
    """Manages user authentication and session handling."""
    
    def __init__(self, pool: ConnectionPool):
        self.pool = pool
        self._init_user_table()
    
    def _init_user_table(self):
        """Initialize user table if it doesn't exist."""
        with self.pool.connection() as conn, conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW(),
                    last_login TIMESTAMPTZ,
                    login_count INTEGER DEFAULT 0
                );
            """)
            
            # Create indexes
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
                CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
                CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);
            """)
            
            # Create default admin user if no users exist
            cur.execute("SELECT COUNT(*) FROM users")
            if cur.fetchone()[0] == 0:
                self._create_default_admin()
    
    def _create_default_admin(self):
        """Create default admin user."""
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_email = os.getenv("ADMIN_EMAIL", "admin@startupscout.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        
        try:
            self.create_user(
                username=admin_username,
                email=admin_email,
                password=admin_password,
                is_admin=True
            )
            logger.info(f"Created default admin user: {admin_username}")
        except Exception as e:
            logger.error(f"Failed to create default admin user: {e}")
    
    def create_user(
        self, 
        username: str, 
        email: str, 
        password: str,
        is_admin: bool = False
    ) -> Dict[str, Any]:
        """Create a new user."""
        try:
            password_hash = hash_password(password)
            
            with self.pool.connection() as conn, conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO users (username, email, password_hash, is_admin)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, username, email, is_active, is_admin, created_at;
                """, (username, email, password_hash, is_admin))
                
                user_data = cur.fetchone()
                
                return {
                    "id": str(user_data[0]),
                    "username": user_data[1],
                    "email": user_data[2],
                    "is_active": user_data[3],
                    "is_admin": user_data[4],
                    "created_at": user_data[5].isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to create user {username}: {e}")
            raise ValueError(f"Failed to create user: {e}")
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with username and password."""
        try:
            with self.pool.connection() as conn, conn.cursor() as cur:
                cur.execute("""
                    SELECT id, username, email, password_hash, is_active, is_admin, login_count
                    FROM users 
                    WHERE (username = %s OR email = %s) AND is_active = TRUE;
                """, (username, username))
                
                user_data = cur.fetchone()
                if not user_data:
                    return None
                
                user_id, username, email, password_hash, is_active, is_admin, login_count = user_data
                
                if not verify_password(password, password_hash):
                    return None
                
                # Update login count and last login
                cur.execute("""
                    UPDATE users 
                    SET login_count = login_count + 1, last_login = NOW()
                    WHERE id = %s;
                """, (user_id,))
                
                # Create JWT token
                token = create_jwt({
                    "user_id": str(user_id),
                    "username": username,
                    "email": email,
                    "is_admin": is_admin
                })
                
                return {
                    "id": str(user_id),
                    "username": username,
                    "email": email,
                    "is_active": is_active,
                    "is_admin": is_admin,
                    "login_count": login_count + 1,
                    "token": token
                }
                
        except Exception as e:
            logger.error(f"Authentication failed for {username}: {e}")
            return None
    
    def get_user_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user information from JWT token."""
        try:
            payload = verify_jwt(token)
            if not payload:
                return None
            
            user_id = payload.get("user_id")
            if not user_id:
                return None
            
            with self.pool.connection() as conn, conn.cursor() as cur:
                cur.execute("""
                    SELECT id, username, email, is_active, is_admin, created_at, last_login, login_count
                    FROM users 
                    WHERE id = %s AND is_active = TRUE;
                """, (user_id,))
                
                user_data = cur.fetchone()
                if not user_data:
                    return None
                
                return {
                    "id": str(user_data[0]),
                    "username": user_data[1],
                    "email": user_data[2],
                    "is_active": user_data[3],
                    "is_admin": user_data[4],
                    "created_at": user_data[5].isoformat() if user_data[5] else None,
                    "last_login": user_data[6].isoformat() if user_data[6] else None,
                    "login_count": user_data[7]
                }
                
        except Exception as e:
            logger.error(f"Failed to get user by token: {e}")
            return None
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics."""
        try:
            with self.pool.connection() as conn, conn.cursor() as cur:
                # Get user info
                cur.execute("""
                    SELECT username, email, created_at, last_login, login_count
                    FROM users WHERE id = %s;
                """, (user_id,))
                
                user_data = cur.fetchone()
                if not user_data:
                    return {}
                
                username, email, created_at, last_login, login_count = user_data
                
                # Get query count from rag_events
                cur.execute("""
                    SELECT COUNT(*), 
                           COUNT(DISTINCT DATE(ts)) as active_days,
                           AVG(duration_ms) as avg_duration,
                           SUM(cost_usd) as total_cost
                    FROM rag_events 
                    WHERE req_id LIKE %s;
                """, (f"{user_id}%",))
                
                stats_data = cur.fetchone()
                query_count, active_days, avg_duration, total_cost = stats_data
                
                return {
                    "username": username,
                    "email": email,
                    "created_at": created_at.isoformat() if created_at else None,
                    "last_login": last_login.isoformat() if last_login else None,
                    "login_count": login_count,
                    "query_count": query_count or 0,
                    "active_days": active_days or 0,
                    "avg_duration_ms": round(float(avg_duration or 0), 2),
                    "total_cost_usd": round(float(total_cost or 0), 6)
                }
                
        except Exception as e:
            logger.error(f"Failed to get user stats: {e}")
            return {}
    
    def update_user_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Update user password."""
        try:
            with self.pool.connection() as conn, conn.cursor() as cur:
                # Verify old password
                cur.execute("""
                    SELECT password_hash FROM users WHERE id = %s;
                """, (user_id,))
                
                password_hash = cur.fetchone()
                if not password_hash or not verify_password(old_password, password_hash[0]):
                    return False
                
                # Update password
                new_password_hash = hash_password(new_password)
                cur.execute("""
                    UPDATE users 
                    SET password_hash = %s, updated_at = NOW()
                    WHERE id = %s;
                """, (new_password_hash, user_id))
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to update password: {e}")
            return False
    
    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account."""
        try:
            with self.pool.connection() as conn, conn.cursor() as cur:
                cur.execute("""
                    UPDATE users 
                    SET is_active = FALSE, updated_at = NOW()
                    WHERE id = %s;
                """, (user_id,))
                
                return cur.rowcount > 0
                
        except Exception as e:
            logger.error(f"Failed to deactivate user: {e}")
            return False
