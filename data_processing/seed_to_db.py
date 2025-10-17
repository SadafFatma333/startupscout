# data_processing/seed_to_db.py
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Json  # for jsonb adaptation

from config.settings import DB_CONFIG
from utils.logger import setup_logger

logger = setup_logger("startupscout.seed_to_db")

# Prefer enriched; fall back to clean
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENRICHED = PROJECT_ROOT / "data/processed/startup_posts_enriched.json"
CLEAN = PROJECT_ROOT / "data/processed/startup_posts_clean.json"
INPUT = ENRICHED if ENRICHED.exists() else CLEAN


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _safe_json(value: Any) -> Any:
    """Return a psycopg-serializable JSON value (Json wrapper) or None."""
    if value is None:
        return None
    if isinstance(value, (list, dict)):
        return Json(value)
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        try:
            parsed = json.loads(s)
            if isinstance(parsed, (list, dict)):
                return Json(parsed)
        except Exception:
            return None
    return None


def _norm_tags(raw_tags: Any) -> Tuple[str | None, List[str] | None]:
    """
    Return (tags_csv, auto_tags_array).
    Keep backward-compatible 'tags' as CSV TEXT, and 'auto_tags' as TEXT[].
    """
    if raw_tags is None:
        return None, None
    if isinstance(raw_tags, list):
        arr = [str(t).strip() for t in raw_tags if str(t).strip()]
        csv = ",".join(arr) if arr else None
        return csv, arr if arr else None
    if isinstance(raw_tags, str):
        s = raw_tags.strip()
        if not s:
            return None, None
        csv = s
        arr = [t.strip() for t in s.split(",") if t.strip()]
        return csv, arr if arr else None
    return None, None


def _coalesce_text(*vals: Any) -> str:
    for v in vals:
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def _parse_timestamp(ts: Any) -> str | None:
    if not ts:
        return None
    if isinstance(ts, (int, float)):
        # epoch seconds or ms
        if ts > 10_000_000_000:
            ts = ts / 1000.0
        return datetime.utcfromtimestamp(ts).isoformat()
    if isinstance(ts, str):
        s = ts.strip()
        if not s:
            return None
        return s  # let Postgres parse timestamptz-compatible strings
    return None


def _load_records(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"No input file found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        data = list(data.values())

    recs: List[Dict[str, Any]] = []
    for r in data:
        title = _coalesce_text(r.get("title"))
        # decision is the short/main text we always keep
        decision = _coalesce_text(
            r.get("decision"),
            r.get("content"),
            r.get("text"),
            r.get("summary"),
        )
        if not title or not decision:
            continue

        source = _coalesce_text(r.get("source"))
        url = _coalesce_text(r.get("url"), r.get("id")) or None  # id may be a URL
        stage = _coalesce_text(r.get("stage"))
        score = r.get("score")
        fetched_at = _parse_timestamp(r.get("fetched_at"))
        summary = _coalesce_text(r.get("summary"))
        content = _coalesce_text(r.get("content"))
        comments = _safe_json(r.get("comments"))
        meta = _safe_json(r.get("meta"))
        # tags from either 'auto_tags' (preferred) or 'tags'
        tags_csv, auto_tags = _norm_tags(r.get("auto_tags") or r.get("tags"))

        recs.append(
            {
                "title": title,
                "source": source or None,
                "url": url,
                "stage": stage or None,
                "decision": decision,
                "summary": summary or None,
                "content": content or None,
                "comments": comments,  # Json(...) or None
                "meta": meta,          # Json(...) or None
                "fetched_at": fetched_at,
                "score": int(score) if isinstance(score, (int, float)) else None,
                "tags_csv": tags_csv,
                "auto_tags": auto_tags,  # list[str] or None (maps to text[])
                "auto_summary": r.get("auto_summary") or None,
            }
        )
    return recs


# ---------------------------------------------------------------------------
# Main seeding
# ---------------------------------------------------------------------------
def seed(truncate: bool = False, batch_size: int = 500) -> None:
    """
    Seed (or upsert) records into 'decisions' table.
    - Does NOT re-embed.
    - Adds/updates enriched fields safely.
    - Uses URL as a stable unique key when available.
    """
    logger.info("Seeding from %s", INPUT)
    rows = _load_records(INPUT)
    logger.info("Loaded %d candidate rows", len(rows))
    if not rows:
        logger.warning("Nothing to insert; aborting.")
        return

    with psycopg.connect(**DB_CONFIG) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        # Ensure base table exists
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS decisions (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                source TEXT,
                decision TEXT NOT NULL,
                tags TEXT,
                stage TEXT,
                embedding VECTOR(1536),
                embedding_model TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        # Ensure enriched columns & UNIQUE(url) exist (idempotent)
        conn.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                               WHERE table_name='decisions' AND column_name='summary') THEN
                    ALTER TABLE decisions ADD COLUMN summary TEXT;
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                               WHERE table_name='decisions' AND column_name='content') THEN
                    ALTER TABLE decisions ADD COLUMN content TEXT;
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                               WHERE table_name='decisions' AND column_name='url') THEN
                    ALTER TABLE decisions ADD COLUMN url TEXT;
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                               WHERE table_name='decisions' AND column_name='comments') THEN
                    ALTER TABLE decisions ADD COLUMN comments JSONB;
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                               WHERE table_name='decisions' AND column_name='meta') THEN
                    ALTER TABLE decisions ADD COLUMN meta JSONB;
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                               WHERE table_name='decisions' AND column_name='fetched_at') THEN
                    ALTER TABLE decisions ADD COLUMN fetched_at TIMESTAMPTZ;
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                               WHERE table_name='decisions' AND column_name='score') THEN
                    ALTER TABLE decisions ADD COLUMN score INTEGER;
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                               WHERE table_name='decisions' AND column_name='auto_tags') THEN
                    ALTER TABLE decisions ADD COLUMN auto_tags TEXT[];
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                               WHERE table_name='decisions' AND column_name='auto_summary') THEN
                    ALTER TABLE decisions ADD COLUMN auto_summary TEXT;
                END IF;
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conrelid = 'decisions'::regclass
                      AND conname = 'decisions_url_uk'
                ) THEN
                    BEGIN
                        ALTER TABLE decisions ADD CONSTRAINT decisions_url_uk UNIQUE (url);
                    EXCEPTION WHEN duplicate_table THEN
                        -- ignore race conditions
                        NULL;
                    END;
                END IF;
            END $$;
            """
        )

        if truncate:
            logger.warning("TRUNCATE requested. This will delete existing rows.")
            conn.execute("TRUNCATE decisions RESTART IDENTITY;")

        # Split rows by presence of URL to enable ON CONFLICT upsert
        rows_with_url = [r for r in rows if r["url"]]
        rows_no_url = [r for r in rows if not r["url"]]

        # Upsert for rows that have a URL (named placeholders match dict keys)
        if rows_with_url:
            logger.info("Upserting %d rows with URL (ON CONFLICT url DO UPDATE)...", len(rows_with_url))
            upsert_sql = """
                INSERT INTO decisions (
                    title, source, decision, tags, stage,
                    url, summary, content, comments, meta,
                    fetched_at, score, auto_tags, auto_summary
                )
                VALUES (
                    %(title)s, %(source)s, %(decision)s, %(tags_csv)s, %(stage)s,
                    %(url)s, %(summary)s, %(content)s, %(comments)s, %(meta)s,
                    %(fetched_at)s, %(score)s, %(auto_tags)s, %(auto_summary)s
                )
                ON CONFLICT (url) DO UPDATE SET
                    title        = EXCLUDED.title,
                    source       = COALESCE(EXCLUDED.source, decisions.source),
                    decision     = EXCLUDED.decision,
                    tags         = EXCLUDED.tags,
                    stage        = EXCLUDED.stage,
                    summary      = EXCLUDED.summary,
                    content      = EXCLUDED.content,
                    comments     = EXCLUDED.comments,
                    meta         = EXCLUDED.meta,
                    fetched_at   = COALESCE(EXCLUDED.fetched_at, decisions.fetched_at),
                    score        = EXCLUDED.score,
                    auto_tags    = EXCLUDED.auto_tags,
                    auto_summary = EXCLUDED.auto_summary;
            """
            with conn.cursor() as cur:
                for i in range(0, len(rows_with_url), batch_size):
                    batch = rows_with_url[i : i + batch_size]
                    cur.executemany(upsert_sql, batch)
                conn.commit()

        # Insert best-effort for rows without URL (no upsert key)
        if rows_no_url:
            logger.info(
                "Inserting %d rows without URL (no de-dup key; duplicates possible).",
                len(rows_no_url),
            )
            insert_sql = """
                INSERT INTO decisions (
                    title, source, decision, tags, stage,
                    summary, content, comments, meta,
                    fetched_at, score, auto_tags, auto_summary
                )
                VALUES (
                    %(title)s, %(source)s, %(decision)s, %(tags_csv)s, %(stage)s,
                    %(summary)s, %(content)s, %(comments)s, %(meta)s,
                    %(fetched_at)s, %(score)s, %(auto_tags)s, %(auto_summary)s
                )
                ON CONFLICT DO NOTHING;
            """
            with conn.cursor() as cur:
                for i in range(0, len(rows_no_url), batch_size):
                    batch = rows_no_url[i : i + batch_size]
                    cur.executemany(insert_sql, batch)
                conn.commit()

        # Simple report
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT COUNT(*) AS n FROM decisions;")
            total = cur.fetchone()["n"]
        logger.info("Seeding complete. decisions rows now: %d", total)


if __name__ == "__main__":
    # Safer default: do NOT truncate in normal runs.
    seed(truncate=False)
