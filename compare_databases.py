#!/usr/bin/env python3
"""
Compare local Docker database with Neon database to identify missing components
"""

import psycopg
import sys
import os

# Add project root to path
sys.path.append('.')
from config.settings import DB_CONFIG

def check_local_db():
    """Check local Docker database"""
    print("=== LOCAL DATABASE (Docker) ===")
    
    # Connect to local Docker database
    local_config = {
        "host": "localhost",
        "port": 5432,
        "dbname": "startupscout", 
        "user": "postgres",
        "password": "postgres"
    }
    
    try:
        conn = psycopg.connect(**local_config)
        cur = conn.cursor()
        
        # Check extensions
        cur.execute("SELECT extname FROM pg_extension ORDER BY extname")
        extensions = [row[0] for row in cur.fetchall()]
        print(f"Extensions: {extensions}")
        
        # Check table structure
        cur.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'decisions' 
            ORDER BY ordinal_position
        """)
        columns = cur.fetchall()
        print(f"Columns ({len(columns)}):")
        for col_name, col_type, nullable in columns:
            print(f"  {col_name}: {col_type} {'NULL' if nullable == 'YES' else 'NOT NULL'}")
        
        # Check indexes
        cur.execute("SELECT indexname FROM pg_indexes WHERE tablename = 'decisions' ORDER BY indexname")
        indexes = [row[0] for row in cur.fetchall()]
        print(f"Indexes ({len(indexes)}):")
        for idx in indexes:
            print(f"  {idx}")
        
        # Check record counts
        cur.execute("SELECT COUNT(*) FROM decisions")
        total = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM decisions WHERE embedding IS NOT NULL")
        with_emb = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM decisions WHERE tsv IS NOT NULL")
        with_tsv = cur.fetchone()[0]
        
        print(f"Records: {total} total, {with_emb} with embeddings, {with_tsv} with tsv")
        
        conn.close()
        return {
            "extensions": extensions,
            "columns": len(columns),
            "indexes": len(indexes),
            "records": total,
            "with_embeddings": with_emb,
            "with_tsv": with_tsv
        }
        
    except Exception as e:
        print(f"Local DB error: {e}")
        return None

def check_neon_db():
    """Check Neon database"""
    print("\n=== NEON DATABASE ===")
    
    try:
        conn = psycopg.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Check extensions
        cur.execute("SELECT extname FROM pg_extension ORDER BY extname")
        extensions = [row[0] for row in cur.fetchall()]
        print(f"Extensions: {extensions}")
        
        # Check table structure
        cur.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'decisions' 
            ORDER BY ordinal_position
        """)
        columns = cur.fetchall()
        print(f"Columns ({len(columns)}):")
        for col_name, col_type, nullable in columns:
            print(f"  {col_name}: {col_type} {'NULL' if nullable == 'YES' else 'NOT NULL'}")
        
        # Check indexes
        cur.execute("SELECT indexname FROM pg_indexes WHERE tablename = 'decisions' ORDER BY indexname")
        indexes = [row[0] for row in cur.fetchall()]
        print(f"Indexes ({len(indexes)}):")
        for idx in indexes:
            print(f"  {idx}")
        
        # Check record counts
        cur.execute("SELECT COUNT(*) FROM decisions")
        total = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM decisions WHERE embedding IS NOT NULL")
        with_emb = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM decisions WHERE tsv IS NOT NULL")
        with_tsv = cur.fetchone()[0]
        
        print(f"Records: {total} total, {with_emb} with embeddings, {with_tsv} with tsv")
        
        conn.close()
        return {
            "extensions": extensions,
            "columns": len(columns),
            "indexes": len(indexes),
            "records": total,
            "with_embeddings": with_emb,
            "with_tsv": with_tsv
        }
        
    except Exception as e:
        print(f"Neon DB error: {e}")
        return None

if __name__ == "__main__":
    local = check_local_db()
    neon = check_neon_db()
    
    if local and neon:
        print("\n=== COMPARISON ===")
        print(f"Extensions: Local {local['extensions']} vs Neon {neon['extensions']}")
        print(f"Columns: Local {local['columns']} vs Neon {neon['columns']}")
        print(f"Indexes: Local {local['indexes']} vs Neon {neon['indexes']}")
        print(f"Records: Local {local['records']} vs Neon {neon['records']}")
        print(f"With embeddings: Local {local['with_embeddings']} vs Neon {neon['with_embeddings']}")
        print(f"With tsv: Local {local['with_tsv']} vs Neon {neon['with_tsv']}")
