#!/usr/bin/env python3
"""
Test connection to Neon database
"""

import psycopg
import os

def test_connection():
    """Test connection to Neon database."""
    
    # Try to connect using the DATABASE_URL
    try:
        print("Testing connection to production database...")
        conn = psycopg.connect(os.getenv("DATABASE_URL"))
        cur = conn.cursor()
        
        # Test query
        cur.execute("SELECT COUNT(*) FROM decisions")
        count = cur.fetchone()[0]
        print(f"✅ Connected successfully! Found {count} records in decisions table.")
        
        # Check extensions
        cur.execute("SELECT extname FROM pg_extension WHERE extname IN ('vector', 'pg_trgm')")
        extensions = [row[0] for row in cur.fetchall()]
        print(f"✅ Extensions: {extensions}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
