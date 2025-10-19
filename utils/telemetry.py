from typing import List, Dict, Any
from psycopg_pool import ConnectionPool

def record_event(pool: ConnectionPool, ev: Dict[str, Any]) -> int:
    with pool.connection() as conn, conn.cursor() as cur:
        cur.execute("""
          INSERT INTO rag_events
          (req_id, question, top_k, fetch_k, candidates, used, min_sim,
           avg_sim, avg_ce, avg_kw, recency_bonus, answer_tokens, prompt_tokens,
           model, duration_ms, cost_usd, tokens_per_second, cost_per_1k_tokens,
           no_context, error)
          VALUES (%(req_id)s, %(question)s, %(top_k)s, %(fetch_k)s, %(candidates)s, %(used)s,
                  %(min_sim)s, %(avg_sim)s, %(avg_ce)s, %(avg_kw)s, %(recency_bonus)s,
                  %(answer_tokens)s, %(prompt_tokens)s, %(model)s, %(duration_ms)s,
                  %(cost_usd)s, %(tokens_per_second)s, %(cost_per_1k_tokens)s,
                  %(no_context)s, %(error)s)
          RETURNING id;
        """, ev)
        return cur.fetchone()[0]

def record_items(pool: ConnectionPool, event_id: int, items: List[Dict[str, Any]]) -> None:
    if not items: return
    with pool.connection() as conn, conn.cursor() as cur:
        cur.executemany("""
          INSERT INTO rag_items(event_id, rank, url, title, source, sim, ce, kw, rrf)
          VALUES (%(event_id)s, %(rank)s, %(url)s, %(title)s, %(source)s, %(sim)s,
                  %(ce)s, %(kw)s, %(rrf)s);
        """, [{**it, "event_id": event_id} for it in items])
