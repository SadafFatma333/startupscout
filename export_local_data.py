#!/usr/bin/env python3
"""
Export all data from local PostgreSQL database to JSON file
"""

import psycopg
import json
import os
from dotenv import load_dotenv

load_dotenv()

def export_local_data():
    """Export all data from local database to JSON file."""
    
    # Connect to local database using .env.dev credentials
    local_conn = psycopg.connect(
        host="localhost",
        port="5432",
        dbname="startupscout",
        user="postgres",
        password="postgres"
    )
    
    cur = local_conn.cursor()
    
    # Export all data including embeddings and TSV
    print("Exporting data from local database...")
    cur.execute("""
        SELECT 
            id, title, decision, summary, content, source, stage, tags, 
            created_at, embedding, embedding_model, comments, url, meta, 
            fetched_at, score, auto_tags, auto_summary, embedding_checksum, 
            embedding_updated_at, tsv
        FROM decisions 
        ORDER BY id
    """)
    
    records = cur.fetchall()
    print(f"Found {len(records)} records in local database")
    
    # Convert to list of dictionaries
    data = []
    for record in records:
        data.append({
            'id': record[0],
            'title': record[1],
            'decision': record[2],
            'summary': record[3],
            'content': record[4],
            'source': record[5],
            'stage': record[6],
            'tags': record[7],
            'created_at': record[8].isoformat() if record[8] else None,
            'embedding': record[9],  # This will be the actual embedding vector
            'embedding_model': record[10],
            'comments': record[11],
            'url': record[12],
            'meta': record[13],
            'fetched_at': record[14].isoformat() if record[14] else None,
            'score': record[15],
            'auto_tags': record[16],
            'auto_summary': record[17],
            'embedding_checksum': record[18],
            'embedding_updated_at': record[19].isoformat() if record[19] else None,
            'tsv': record[20]  # This will be the actual TSV vector
        })
    
    # Save to JSON file
    with open('local_data_export.json', 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"Exported {len(data)} records to local_data_export.json")
    
    cur.close()
    local_conn.close()
    
    return len(data)

if __name__ == "__main__":
    count = export_local_data()
    print(f"✅ Export complete! {count} records exported.")
