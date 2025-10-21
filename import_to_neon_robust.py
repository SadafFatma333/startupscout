#!/usr/bin/env python3
"""
Robust import script to transfer exact data from local database to Neon database.
Handles all data type conversions and edge cases.
"""

import json
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

def safe_json_parse(value):
    """Safely parse JSON values, handling None, empty strings, and invalid JSON."""
    if value is None or value == "":
        return None
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return None

def safe_array_parse(value):
    """Safely parse array values for PostgreSQL."""
    if value is None or value == "":
        return None
    if isinstance(value, list):
        return value
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return parsed
        return None
    except (json.JSONDecodeError, TypeError):
        return None

def import_to_neon():
    """Import exact data from local database to Neon database."""
    
    # Connect to Neon database using the actual Neon DATABASE_URL
    neon_url = "postgresql://neondb_owner:npg_RNg6m8SzUJLP@ep-long-smoke-adxam0qu-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    neon_conn = psycopg.connect(neon_url)
    cur = neon_conn.cursor()
    
    # Clear existing data
    print("Clearing existing data from Neon database...")
    cur.execute("DELETE FROM decisions")
    cur.execute("ALTER SEQUENCE decisions_id_seq RESTART WITH 1")
    neon_conn.commit()
    
    # Load exported data
    print("Loading exported data...")
    with open("local_db_export.json", "r") as f:
        data = json.load(f)
    
    print(f"Importing {len(data)} records to Neon database...")
    
    # Import each record exactly as it was
    imported_count = 0
    error_count = 0
    
    for i, record in enumerate(data):
        try:
            # Convert dict fields to JSON strings safely
            comments = json.dumps(record['comments']) if record['comments'] else None
            meta = json.dumps(record['meta']) if record['meta'] else None
            
            # Handle array fields properly - convert to PostgreSQL array format
            tags = safe_array_parse(record['tags'])
            auto_tags = safe_array_parse(record['auto_tags'])
            
            cur.execute("""
                INSERT INTO decisions (
                    id, title, decision, summary, content, source, stage, tags, 
                    created_at, embedding, embedding_model, comments, url, meta, 
                    fetched_at, score, auto_tags, auto_summary, embedding_checksum, 
                    embedding_updated_at, tsv
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                record['id'], record['title'], record['decision'], record['summary'], 
                record['content'], record['source'], record['stage'], tags,
                record['created_at'], record['embedding'], record['embedding_model'], 
                comments, record['url'], meta, record['fetched_at'],
                record['score'], auto_tags, record['auto_summary'], 
                record['embedding_checksum'], record['embedding_updated_at'], record['tsv']
            ))
            
            imported_count += 1
            
            if (i + 1) % 100 == 0:
                print(f"Imported {i + 1} records...")
                
        except Exception as e:
            error_count += 1
            if error_count <= 10:  # Only show first 10 errors
                print(f"Error importing record {i + 1}: {e}")
            elif error_count == 11:
                print("... (suppressing further error messages)")
    
    # Commit all changes
    neon_conn.commit()
    
    # Verify import
    cur.execute("SELECT COUNT(*) FROM decisions")
    total_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM decisions WHERE embedding IS NOT NULL")
    embedding_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM decisions WHERE tsv IS NOT NULL")
    tsv_count = cur.fetchone()[0]
    
    print(f"\n✅ Import complete!")
    print(f"Total records: {total_count}")
    print(f"Records with embeddings: {embedding_count}")
    print(f"Records with TSV: {tsv_count}")
    print(f"Import errors: {error_count}")
    print(f"✅ Import complete! {imported_count} records imported to Neon.")
    
    neon_conn.close()

if __name__ == "__main__":
    import_to_neon()
