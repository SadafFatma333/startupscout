#!/usr/bin/env python3
"""
Quick script to fix Neon database schema
Run this on Railway to add missing columns
"""

import psycopg
import os
import sys

# Add project root to path
sys.path.append('.')
from config.settings import DB_CONFIG

def fix_schema():
    """Add missing columns to the decisions table"""
    print("Connecting to Neon database...")
    conn = psycopg.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    try:
        print("Adding missing columns...")
        
        # Add missing columns if they don't exist
        columns_to_add = [
            "ALTER TABLE decisions ADD COLUMN IF NOT EXISTS summary TEXT",
            "ALTER TABLE decisions ADD COLUMN IF NOT EXISTS content TEXT", 
            "ALTER TABLE decisions ADD COLUMN IF NOT EXISTS comments TEXT",
            "ALTER TABLE decisions ADD COLUMN IF NOT EXISTS url TEXT",
            "ALTER TABLE decisions ADD COLUMN IF NOT EXISTS fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ]
        
        for sql in columns_to_add:
            print(f"Executing: {sql}")
            cur.execute(sql)
        
        conn.commit()
        print("✅ Schema updated successfully!")
        
        # Check current schema
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'decisions' 
            ORDER BY ordinal_position
        """)
        columns = cur.fetchall()
        print("\nCurrent table schema:")
        for col_name, col_type in columns:
            print(f"  {col_name}: {col_type}")
            
        # Check record count
        cur.execute("SELECT COUNT(*) FROM decisions")
        count = cur.fetchone()[0]
        print(f"\nRecords in database: {count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_schema()
