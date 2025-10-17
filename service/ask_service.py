import json
import numpy as np
import os
import sqlite3
from openai import OpenAI
from utils.logger import setup_logger
from services.cache import cache_result  # your existing cache decorator

logger = setup_logger("startupscout.ask_service")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")


# ---------------------------------------------------------
# Query Embedding
# ---------------------------------------------------------
@cache_result(ttl=600)
def create_query_vector(query: str):
    logger.info("Creating embedding for query.")
    resp = client.embeddings.create(model=EMBED_MODEL, input=query)
    return np.array(resp.data[0].embedding, dtype=np.float32)


# ---------------------------------------------------------
# Vector Search
# ---------------------------------------------------------
def search_contexts(conn: sqlite3.Connection, query_vector, top_k: int = 5):
    logger.info(f"Searching vector store (top_k={top_k})...")
    query_vector_str = json.dumps(query_vector.tolist())

    rows = conn.execute(
        """
        SELECT id, source, text, 1 - (embedding <=> json(?)) AS score
        FROM documents
        ORDER BY score DESC
        LIMIT ?
        """,
        (query_vector_str, top_k)
    ).fetchall()

    return [
        {"id": r["id"], "source": r["source"], "text": r["text"], "score": r["score"]}
        for r in rows
    ]


# ---------------------------------------------------------
# Prompt Construction
# ---------------------------------------------------------
def build_prompt(query: str, contexts: list):
    joined_context = "\n\n".join(
        [f"Source {i+1}: {c['text']}" for i, c in enumerate(contexts)]
    )
    return f"""
You are StartupScout — an AI assistant that summarizes startup learnings.

Use only the provided sources to answer accurately and concisely.

Context:
{joined_context}

User question:
{query}

Answer:
"""


# ---------------------------------------------------------
# LLM Generation
# ---------------------------------------------------------
def call_llm(prompt: str):
    logger.info("Calling LLM to generate response.")
    resp = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()


# ---------------------------------------------------------
# Main Ask Function
# ---------------------------------------------------------
@cache_result(ttl=600)
def ask(conn: sqlite3.Connection, query: str, top_k: int = 5):
    logger.info(f"Received user query: {query}")
    vector = create_query_vector(query)
    contexts = search_contexts(conn, vector, top_k)
    prompt = build_prompt(query, contexts)
    answer = call_llm(prompt)
    logger.info("Answer generated successfully.")
    return answer
