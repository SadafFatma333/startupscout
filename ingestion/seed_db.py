import json
import psycopg
import sys
import os

# Add project root to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import DB_CONFIG, STARTUP_DATA_FILE, EMBEDDING_BACKEND

# Decide embedding vector dimension based on backend
if EMBEDDING_BACKEND == "openai":
    VECTOR_DIM = 1536
else:  # MiniLM
    VECTOR_DIM = 384

def seed_database(json_path=None, wipe_existing=True):
    if json_path is None:
        json_path = STARTUP_DATA_FILE
    
    # Load JSON data
    with open(json_path, "r") as f:
        data = json.load(f)

    # Connect to Postgres
    conn = psycopg.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Ensure pgvector extension exists
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Ensure table exists (with embedding column + model tracking)
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS decisions (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            source TEXT,
            decision TEXT NOT NULL,
            tags TEXT,
            stage TEXT,
            embedding VECTOR({VECTOR_DIM}), -- pgvector column
            embedding_model TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    if wipe_existing:
        cur.execute("TRUNCATE decisions RESTART IDENTITY")

    # Insert data
    for entry in data:
        try:
            cur.execute("""
                INSERT INTO decisions (title, source, decision, tags, stage)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                entry["title"],
                entry.get("source", ""),
                entry["decision"],
                ",".join(entry["tags"]) if "tags" in entry else "",
                entry.get("stage", "")
            ))
        except Exception as e:
            print(f"Error inserting entry {entry.get('title', 'Unknown')}: {e}")

    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {len(data)} records into PostgreSQL database.")

if __name__ == "__main__":
    seed_database()
