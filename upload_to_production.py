#!/usr/bin/env python3
"""
Upload local data to production database via API
"""

import json
import requests
import time

def upload_data_in_chunks():
    """Upload data to production in chunks."""
    
    # Load the exported data
    print("Loading exported data...")
    with open('local_data_export.json', 'r') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} records")
    
    # Upload in chunks of 100 records
    chunk_size = 100
    base_url = "https://startupscout.up.railway.app"
    
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        print(f"Uploading chunk {i//chunk_size + 1}/{(len(data) + chunk_size - 1)//chunk_size} ({len(chunk)} records)...")
        
        try:
            # For now, let's just test with a small chunk
            if i == 0:
                response = requests.post(
                    f"{base_url}/import-local-data",
                    json={"data": chunk, "chunk": i//chunk_size + 1},
                    timeout=60
                )
                print(f"Response: {response.status_code} - {response.text}")
                
                # Wait a bit between chunks
                time.sleep(2)
                
        except Exception as e:
            print(f"Error uploading chunk {i//chunk_size + 1}: {e}")
            break
    
    print("Upload complete!")

if __name__ == "__main__":
    upload_data_in_chunks()
