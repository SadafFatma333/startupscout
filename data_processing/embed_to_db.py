# data_processing/embed_to_db.py
from __future__ import annotations

import os
import time
import psycopg
from typing import List, Tuple

from config.settings import DB_CONFIG, EMBEDDING_BACKEND
from utils.embeddings import get_embedding, get_embedding_dim
from utils.logger import setup_logger

logger = setup_logger("startupscout.embed_to_db")


def _fetch_batch(cur, batch_size: int) -> List[Tuple[int, str]]:
    cur.execute(
        """
        SELECT id, decision
        FROM decisions
        WHERE embedding IS NULL
        ORDER BY id
        LIMIT %s
        """,
        (batch_size,),
    )
    return cur.fetchall()


def process_embeddings(batch_size: int = 50, sleep_between_calls: float = 0.0) -> None:
    """
    Populate 'embedding' and 'embedding_model' for rows in 'decisions'
    where embedding IS NULL. Deterministic batches; safe to resume.
    """
    logger.info(
        "Embedding job start (backend=%s, dim=%d, batch=%d)",
        EMBEDDING_BACKEND, get_embedding_dim(), batch_size,
    )

    processed_total = 0
    failures_total = 0

    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            while True:
                batch = _fetch_batch(cur, batch_size)
                if not batch:
                    break

                updated = 0
                for row_id, decision in batch:
                    text = (decision or "").strip()
                    if not text:
                        empty_vec = [0.0] * get_embedding_dim()
                        cur.execute(
                            """
                            UPDATE decisions
                            SET embedding = %s::vector, embedding_model = %s
                            WHERE id = %s
                            """,
                            (empty_vec, f"{EMBEDDING_BACKEND}-empty", row_id),
                        )
                        updated += 1
                        continue

                    try:
                        embedding, model_name = get_embedding(text)
                        cur.execute(
                            """
                            UPDATE decisions
                            SET embedding = %s::vector, embedding_model = %s
                            WHERE id = %s
                            """,
                            (embedding, model_name, row_id),
                        )
                        updated += 1
                        if sleep_between_calls > 0:
                            time.sleep(sleep_between_calls)
                    except Exception as e:
                        failures_total += 1
                        logger.warning("Embedding failed for id=%s: %s", row_id, e)

                conn.commit()
                processed_total += len(batch)
                logger.info(
                    "Committed batch: updated=%d, batch_size=%d, total_processed=%d, failures=%d",
                    updated, len(batch), processed_total, failures_total,
                )

    logger.info(
        "Embedding job complete. total_processed=%d failures=%d",
        processed_total, failures_total,
    )


if __name__ == "__main__":
    sleep = 0.0
    if EMBEDDING_BACKEND == "openai":
        sleep = float(os.getenv("EMBED_CALL_SLEEP", "0.0"))  # bump to 0.05–0.1 if you ever see 429s
    batch = int(os.getenv("EMBED_BATCH_SIZE", "50"))
    process_embeddings(batch_size=batch, sleep_between_calls=sleep)
