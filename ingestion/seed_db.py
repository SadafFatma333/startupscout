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
            summary TEXT,
            content TEXT,
            comments TEXT,
            tags TEXT,
            stage TEXT,
            url TEXT,
            embedding VECTOR({VECTOR_DIM}), -- pgvector column
            embedding_model TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    if wipe_existing:
        cur.execute("TRUNCATE decisions RESTART IDENTITY")

    # Insert data
    for entry in data:
        try:
            cur.execute("""
                INSERT INTO decisions (title, source, decision, summary, content, comments, tags, stage, url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                entry["title"],
                entry.get("source", ""),
                entry["decision"],
                entry.get("summary", ""),
                entry.get("content", ""),
                entry.get("comments", ""),
                ",".join(entry["tags"]) if "tags" in entry else "",
                entry.get("stage", ""),
                entry.get("url", "")
            ))
        except Exception as e:
            print(f"Error inserting entry {entry.get('title', 'Unknown')}: {e}")

    # Generate embeddings for all records
    print("Generating embeddings...")
    from utils.embeddings import get_embedding
    
    cur.execute("SELECT id, title, decision, summary, content FROM decisions WHERE embedding IS NULL")
    records = cur.fetchall()
    
    for record_id, title, decision, summary, content in records:
        try:
            # Combine text for embedding
            text = f"{title} {decision}"
            if summary:
                text += f" {summary}"
            if content:
                text += f" {content}"
            
            embedding, model = get_embedding(text)
            
            # Update record with embedding
            cur.execute(
                "UPDATE decisions SET embedding = %s, embedding_model = %s WHERE id = %s",
                (embedding, model, record_id)
            )
            
        except Exception as e:
            print(f"Error generating embedding for record {record_id}: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {len(data)} records into PostgreSQL database with embeddings.")

if __name__ == "__main__":
    seed_database()
