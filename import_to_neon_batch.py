#!/usr/bin/env python3
"""
Batch import script with fresh connections to avoid transaction abort issues.
"""

import json
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

def import_batch(records, batch_start):
    """Import a batch of records with a fresh connection."""
    neon_url = "postgresql://neondb_owner:npg_RNg6m8SzUJLP@ep-long-smoke-adxam0qu-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    
    try:
        neon_conn = psycopg.connect(neon_url)
        cur = neon_conn.cursor()
        
        imported = 0
        errors = 0
        
        for i, record in enumerate(records):
            try:
                # Handle data conversion safely
                comments = None
                if record['comments']:
                    try:
                        comments = json.dumps(record['comments'])
                    except:
                        comments = None
                
                meta = None
                if record['meta']:
                    try:
                        meta = json.dumps(record['meta'])
                    except:
                        meta = None
                
                # Handle array fields
                tags = None
                if record['tags']:
                    if isinstance(record['tags'], list):
                        tags = record['tags']
                    elif isinstance(record['tags'], str) and record['tags'].strip():
                        try:
                            tags = json.loads(record['tags'])
                        except:
                            tags = None
                
                auto_tags = None
                if record['auto_tags']:
                    if isinstance(record['auto_tags'], list):
                        auto_tags = record['auto_tags']
                    elif isinstance(record['auto_tags'], str) and record['auto_tags'].strip():
                        try:
                            auto_tags = json.loads(record['auto_tags'])
                        except:
                            auto_tags = None
                
                # Insert record
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
                
                imported += 1
                
            except Exception as e:
                errors += 1
                if errors <= 5:  # Show first 5 errors per batch
                    print(f"Error in batch {batch_start + i}: {e}")
        
        # Commit the batch
        neon_conn.commit()
        neon_conn.close()
        
        return imported, errors
        
    except Exception as e:
        print(f"Batch connection error: {e}")
        return 0, len(records)

def import_to_neon():
    """Import all data from local database to Neon database."""
    
    # Load exported data
    print("Loading exported data...")
    with open("local_db_export.json", "r") as f:
        data = json.load(f)
    
    print(f"Importing {len(data)} records to Neon database in batches...")
    
    # Clear existing data first
    neon_url = "postgresql://neondb_owner:npg_RNg6m8SzUJLP@ep-long-smoke-adxam0qu-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    neon_conn = psyconeg.connect(neon_url)
    cur = neon_conn.cursor()
    cur.execute("DELETE FROM decisions")
    cur.execute("ALTER SEQUENCE decisions_id_seq RESTART WITH 1")
    neon_conn.commit()
    neon_conn.close()
    print("Cleared existing data from Neon database...")
    
    # Import in batches of 100
    batch_size = 100
    total_imported = 0
    total_errors = 0
    
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(data) + batch_size - 1) // batch_size
        
        print(f"Processing batch {batch_num}/{total_batches} (records {i+1}-{min(i+batch_size, len(data))})...")
        
        imported, errors = import_batch(batch, i)
        total_imported += imported
        total_errors += errors
        
        print(f"Batch {batch_num}: {imported} imported, {errors} errors")
    
    print(f"\n✅ Import complete!")
    print(f"Total records imported: {total_imported}")
    print(f"Total errors: {total_errors}")
    
    # Verify final count
    neon_conn = psycopg.connect(neon_url)
    cur = neon_conn.cursor()
    cur.execute("SELECT COUNT(*) FROM decisions")
    final_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM decisions WHERE embedding IS NOT NULL")
    embedding_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM decisions WHERE tsv IS NOT NULL")
    tsv_count = cur.fetchone()[0]
    
    print(f"Final count in Neon: {final_count}")
    print(f"Records with embeddings: {embedding_count}")
    print(f"Records with TSV: {tsv_count}")
    
    neon_conn.close()

if __name__ == "__main__":
    import_to_neon()
