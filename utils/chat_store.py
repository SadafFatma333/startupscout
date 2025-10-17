# utils/chat_store.py
from typing import Any, Dict, List, Optional, Tuple
from psycopg import connect
from config.settings import DB_CONFIG

def ensure_session(session_id: str, user_id: int | None = None):
    with connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO chat_sessions (id) VALUES (%s)
                ON CONFLICT (id) DO UPDATE
                SET last_seen_at = NOW()
                """,
                (session_id,)
            )
            return

def add_message(session_id: str, role: str, content: str, ts_ms: int, refs: Optional[Dict]=None) -> None:
    with connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO chat_messages (session_id, role, content, refs, ts_ms)
                VALUES (%s, %s, %s, %s::jsonb, %s)
                """,
                (session_id, role, content, (None if refs is None else json_dumps(refs)), ts_ms)
            )

def get_history(session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    with connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT role, content, COALESCE(refs, '{}'::jsonb), ts_ms
                FROM chat_messages
                WHERE session_id = %s
                ORDER BY id ASC
                LIMIT %s
                """,
                (session_id, limit)
            )
            rows = cur.fetchall()
    return [
        {"role": r[0], "content": r[1], "refs": r[2], "ts": int(r[3])}
        for r in rows
    ]

def clear_history(session_id: str) -> None:
    with connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM chat_messages WHERE session_id = %s", (session_id,))

# small helper (no extra deps)
import json
def json_dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)
