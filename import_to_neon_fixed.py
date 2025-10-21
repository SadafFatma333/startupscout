#!/usr/bin/env python3
"""
Fixed import script that properly handles data type conversions.
"""

import json
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

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
            
            # Handle tags - convert string to array if needed
            tags = None
            if record['tags']:
                if isinstance(record['tags'], list):
                    tags = record['tags']
                elif isinstance(record['tags'], str) and record['tags'].strip():
                    # Convert comma-separated string to array
                    tags = [tag.strip() for tag in record['tags'].split(',') if tag.strip()]
            
            # Handle auto_tags - should already be an array
            auto_tags = None
            if record['auto_tags']:
                if isinstance(record['auto_tags'], list):
                    auto_tags = record['auto_tags']
                elif isinstance(record['auto_tags'], str) and record['auto_tags'].strip():
                    try:
                        auto_tags = json.loads(record['auto_tags'])
                    except:
                        auto_tags = None
            
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
