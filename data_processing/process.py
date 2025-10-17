import psycopg
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import DB_CONFIG
from utils.embeddings import get_embedding

def process_embeddings(batch_size=20):
    conn = psycopg.connect(**DB_CONFIG)
    cur = conn.cursor()

    processed_total = 0

    while True:
        # Select rows without embeddings
        cur.execute("""
            SELECT id, decision FROM decisions
            WHERE embedding IS NULL
            LIMIT %s
        """, (batch_size,))
        rows = cur.fetchall()

        if not rows:
            break  # no more rows left

        for row_id, decision in rows:
            embedding, model_name = get_embedding(decision)

            # psycopg3 can directly map Python lists to Postgres arrays
            cur.execute("""
                UPDATE decisions
                SET embedding = %s::vector, embedding_model = %s
                WHERE id = %s
            """, (embedding, model_name, row_id))

        conn.commit()
        processed_total += len(rows)
        print(f"✅ Processed batch of {len(rows)} rows (total: {processed_total})")

    cur.close()
    conn.close()
    print(f"🎉 Finished processing embeddings. Total: {processed_total} rows.")

if __name__ == "__main__":
    process_embeddings()
