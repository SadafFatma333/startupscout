# scripts/process_embeddings.py
from __future__ import annotations

import os
from data_processing.embed_to_db import process_embeddings
from config.settings import EMBEDDING_BACKEND

if __name__ == "__main__":
    sleep = 0.0
    if EMBEDDING_BACKEND == "openai":
        sleep = float(os.getenv("EMBED_CALL_SLEEP", "0.0"))
    batch = int(os.getenv("EMBED_BATCH_SIZE", "50"))
    process_embeddings(batch_size=batch, sleep_between_calls=sleep)
