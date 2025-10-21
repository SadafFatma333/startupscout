#!/usr/bin/env python3
"""
Export all data from local database to JSON file.
"""

import json
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

def export_local_db():
    """Export all data from local database to JSON file."""
    
    # Connect to local Docker database
    local_conn = psycopg.connect("postgresql://postgres:postgres@localhost:5432/startupscout")
    cur = local_conn.cursor()
    
    print("Exporting data from local database...")
    
    # Get all records from decisions table
    cur.execute("SELECT * FROM decisions ORDER BY id")
    records = cur.fetchall()
    
    # Get column names
    column_names = [desc[0] for desc in cur.description]
    
    print(f"Found {len(records)} records in local database")
    
    # Convert to list of dictionaries
    data = []
    for record in records:
        record_dict = dict(zip(column_names, record))
        data.append(record_dict)
    
    # Save to JSON file
    with open("local_db_export.json", "w") as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"✅ Exported {len(data)} records to local_db_export.json")
    
    local_conn.close()

if __name__ == "__main__":
    export_local_db()
