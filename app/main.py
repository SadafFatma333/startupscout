# app/main.py
import os
import time
import uuid
import traceback
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone

from fastapi import FastAPI, Query, Request, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from psycopg.errors import DatabaseError
from psycopg_pool import ConnectionPool
from openai import OpenAI

from config.settings import DB_CONFIG, OPENAI_API_KEY
from app.search import router as search_router
from app.auth import router as auth_router
from utils.embeddings import get_embedding
from utils.logger import setup_logger
from utils.cache import cache_result, cache_get_stats, cache_clear
from utils.chat_store import ensure_session, add_message, get_history, clear_history
from utils.rerank import derive_keywords, keyword_score, evidence_bonus
from utils.cross_rerank import rerank as cross_rerank
from utils.auth import verify_jwt


app = FastAPI(title="StartupScout API", version="1.0.0")
logger = setup_logger("startupscout.api")

# CORS
_default_origins = ["http://127.0.0.1:5173", "http://localhost:5173"]
_allowed_origins = os.getenv("ALLOWED_ORIGINS")
allow_origins = (
    [o.strip() for o in _allowed_origins.split(",")] if _allowed_origins else _default_origins
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Routers
app.include_router(search_router)
app.include_router(auth_router)

# Metrics
START_TIME = time.time()
REQUEST_COUNT = 0

# Admin key
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "changeme")

# Session cookie
SESSION_COOKIE = "scout_sid"
SESSION_TTL_SEC = 7 * 24 * 3600
IS_PROD = os.getenv("ENV") == "prod"

# OpenAI client
oai_client = OpenAI(api_key=OPENAI_API_KEY)

STYLE_SYSTEM = (
    "You are StartupScout, a pragmatic startup advisor. Write in crisp, confident, non-generic language. "
    "Prefer short sentences. Lead with specifics. Avoid hedging and filler. "
    "Use bullets when listing. Keep quotes ≤ 10 words. Include [n] citations matching the provided context."
)

def _build_conninfo(cfg: Dict[str, Any]) -> str:
    if "dsn" in cfg and cfg["dsn"]:
        return cfg["dsn"]
    host = cfg.get("host", "localhost")
    port = cfg.get("port", 5432)
    dbname = cfg.get("dbname") or cfg.get("database") or "postgres"
    user = cfg.get("user") or cfg.get("username") or "postgres"
    password = cfg.get("password", "")
    return f"host={host} port={port} dbname={dbname} user={user} password={password}"


POOL: Optional[ConnectionPool] = None
try:
    POOL = ConnectionPool(
        conninfo=_build_conninfo(DB_CONFIG),
        min_size=int(os.getenv("DB_POOL_MIN", "1")),
        max_size=int(os.getenv("DB_POOL_MAX", "10")),
        timeout=int(os.getenv("DB_POOL_TIMEOUT_SEC", "10")),
        max_idle=int(os.getenv("DB_POOL_MAX_IDLE", "30")),
    )
    logger.info("Database connection pool initialized.")
except Exception as e:
    logger.exception("Failed to initialize DB pool: %s", e)


def _get_session_id(request: Request) -> str:
    return request.cookies.get(SESSION_COOKIE, "anon")


@app.middleware("http")
async def ensure_session_cookie(request: Request, call_next):
    global REQUEST_COUNT
    REQUEST_COUNT += 1

    sid = request.cookies.get(SESSION_COOKIE)
    new_sid: Optional[str] = None
    if not sid:
        new_sid = uuid.uuid4().hex

    response = await call_next(request)

    if new_sid:
        response.set_cookie(
            key=SESSION_COOKIE,
            value=new_sid,
            max_age=SESSION_TTL_SEC,
            path="/",
            secure=IS_PROD,
            httponly=True,
            samesite="Lax",
        )
    return response


@app.exception_handler(Exception)
async def all_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error at %s: %s", request.url.path, exc)
    traceback.print_exc()
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


@app.get("/health")
def health_check():
    db_status = "unreachable"
    if POOL is not None:
        try:
            with POOL.connection() as conn, conn.cursor() as cur:
                cur.execute("SELECT 1;")
                cur.fetchone()
            db_status = "connected"
        except Exception:
            db_status = "unreachable"

    uptime = round(time.time() - START_TIME, 1)
    return {"status": "ok", "uptime_sec": uptime, "db": db_status}


@app.get("/stats")
def stats():
    return {
        "requests": REQUEST_COUNT,
        "uptime_sec": round(time.time() - START_TIME, 1),
        "cache": cache_get_stats(),
    }


def _clip(s: Optional[str], n: int) -> str:
    if not s:
        return ""
    s2 = " ".join(s.split())
    return (s2[:n] + "…") if len(s2) > n else s2


def _comments_top(c: Any, k: int = 3) -> str:
    if not c:
        return ""
    if isinstance(c, list):
        c = c[:k]
        return "\n".join(f"- {str(x)[:200]}" for x in c)
    return ""


def _prepare_session(cur) -> None:
    timeout_ms = int(os.getenv("PG_STMT_TIMEOUT_MS", "3000"))
    cur.execute(f"SET LOCAL statement_timeout = '{timeout_ms}ms';")


def _recency_score(fetched_at) -> float:
    if not fetched_at or not isinstance(fetched_at, datetime):
        return 0.0
    try:
        fa = fetched_at if fetched_at.tzinfo else fetched_at.replace(tzinfo=timezone.utc)
        age_days = (datetime.now(timezone.utc) - fa).days
    except Exception:
        return 0.0
    if age_days <= 0:
        return 1.0
    if age_days >= 365:
        return 0.3
    return max(0.3, 1.0 - (age_days / 365.0) * 0.7)


def _bm25_available(cur) -> bool:
    try:
        cur.execute("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname='pg_bm25');")
        return bool(cur.fetchone()[0])
    except Exception:
        return False


def _build_tsquery(cur, q: str) -> Tuple[str, str]:
    lang = os.getenv("TS_LANG", "english")
    tsv = f"to_tsvector('{lang}', coalesce(title,'') || ' ' || coalesce(decision,'') || ' ' || coalesce(content,''))"
    tsq = f"websearch_to_tsquery('{lang}', %s)"
    return tsv, tsq


@app.get("/ask")
@cache_result(ttl=60)
def ask(
    request: Request,
    question: str = Query(..., description="Ask a startup-related question"),
    top_k: int = Query(5, ge=1, le=10, description="Top-K similar items to return"),
    x_auth_token: Optional[str] = Header(default=None, convert_underscores=False),
):
    # Normalize input
    q = (question or "").strip()
    if not q:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    if len(q) > 1000:
        q = q[:1000]
    q = " ".join(q.split())

    # Optional user id
    user_id: Optional[int] = None
    if x_auth_token:
        payload = verify_jwt(x_auth_token)
        if payload:
            try:
                user_id = int(payload["sub"])
            except Exception:
                user_id = None

    # Embedding
    try:
        q_vec, _ = get_embedding(q)
        if not q_vec:
            raise ValueError("Empty embedding returned.")
    except Exception as e:
        logger.error("Embedding generation failed: %s", e)
        raise HTTPException(status_code=500, detail="Embedding generation failed.")

    if POOL is None:
        raise HTTPException(status_code=503, detail="Database unavailable.")

    # Recall + floors
    fetch_k = min(20, max(top_k * 3, top_k + 7))
    min_sim = float(os.getenv("MIN_SIMILARITY", "0.35"))
    rrf_k = int(os.getenv("RRF_K", "60"))

    kws = derive_keywords(q)
    kw_patterns = [f"%{kw}%" for kw in kws][:8] or [f"%{q[:32]}%"]

    # Hybrid candidate fetch: vector + BM25 (or ts_rank) + ILIKE
    try:
        with POOL.connection() as conn, conn.cursor() as cur:
            _prepare_session(cur)

            # Vector ANN
            cur.execute(
                """
                SELECT
                    id, title, decision, summary, content, comments, tags, stage, source, url,
                    1 - (embedding <=> %s::vector) AS sim, fetched_at
                FROM decisions
                WHERE embedding IS NOT NULL
                ORDER BY embedding <-> %s::vector
                LIMIT %s;
                """,
                (q_vec, q_vec, fetch_k),
            )
            vec_rows = cur.fetchall()

            # BM25 (if available) else ts_rank
            has_bm25 = _bm25_available(cur)
            tsv, tsq = _build_tsquery(cur, q)
            if has_bm25:
                bm25_sql = f"""
                    SELECT
                        id, title, decision, summary, content, comments, tags, stage, source, url,
                        0.0 AS sim, fetched_at,
                        bm25({tsv}, {tsq}) AS bm25_score
                    FROM decisions
                    WHERE {tsv} @@ {tsq}
                    ORDER BY bm25_score DESC
                    LIMIT %s;
                """
            else:
                bm25_sql = f"""
                    SELECT
                        id, title, decision, summary, content, comments, tags, stage, source, url,
                        0.0 AS sim, fetched_at,
                        ts_rank({tsv}, {tsq}) AS bm25_score
                    FROM decisions
                    WHERE {tsv} @@ {tsq}
                    ORDER BY bm25_score DESC
                    LIMIT %s;
                """
            # tsq appears twice → two %s plus LIMIT
            cur.execute(bm25_sql, (q, q, fetch_k))
            bm25_rows = cur.fetchall()

            # Keyword ILIKE (broad)
            cur.execute(
                """
                SELECT
                    id, title, decision, summary, content, comments, tags, stage, source, url,
                    0.0 AS sim, fetched_at
                FROM decisions
                WHERE (title ILIKE ANY(%s) OR decision ILIKE ANY(%s) OR content ILIKE ANY(%s))
                ORDER BY fetched_at DESC NULLS LAST
                LIMIT %s;
                """,
                (kw_patterns, kw_patterns, kw_patterns, fetch_k),
            )
            kw_rows = cur.fetchall()
    except DatabaseError as e:
        logger.error("Database error in /ask: %s", e)
        raise HTTPException(status_code=500, detail="Database query failed.")
    except Exception as e:
        logger.error("Unexpected DB error in /ask: %s", e)
        raise HTTPException(status_code=500, detail="Database query failed.")

    if not (vec_rows or bm25_rows or kw_rows):
        return {"question": q, "answer": "No related startup cases found.", "references": []}

    # Build rank maps for RRF
    def _rank_map(rows: List[tuple]) -> Dict[Any, int]:
        return {(r[9] or (r[1], r[8])): i + 1 for i, r in enumerate(rows)}

    vec_rank = _rank_map(vec_rows)
    bm25_rank = _rank_map(bm25_rows)
    kw_rank = _rank_map(kw_rows)

    # Merge by key and keep best vector sim per key
    merged: Dict[Any, Dict[str, Any]] = {}
    for source_rows, tag in [(vec_rows, "vec"), (bm25_rows, "bm25"), (kw_rows, "kw")]:
        for r in source_rows:
            key = (r[9] or (r[1], r[8]))
            if key not in merged:
                merged[key] = {
                    "row": r,
                    "sim": float(r[10]),
                    "bm25": 0.0,
                    "vec_rank": vec_rank.get(key),
                    "bm25_rank": bm25_rank.get(key),
                    "kw_rank": kw_rank.get(key),
                }
            else:
                if float(r[10]) > merged[key]["sim"]:
                    merged[key]["row"] = r
                    merged[key]["sim"] = float(r[10])
                if tag == "vec":
                    merged[key]["vec_rank"] = vec_rank.get(key)
                elif tag == "bm25":
                    merged[key]["bm25_rank"] = bm25_rank.get(key)
                else:
                    merged[key]["kw_rank"] = kw_rank.get(key)

    # Attach bm25 score
    bm25_scores: Dict[Any, float] = {}
    for r in bm25_rows:
        key = (r[9] or (r[1], r[8]))
        bm25_scores[key] = float(r[12]) if len(r) > 12 and r[12] is not None else 0.0
    for k in merged.keys():
        merged[k]["bm25"] = bm25_scores.get(k, 0.0)

    # Cross-encoder inputs
    candidates = list(merged.values())
    blobs: List[Tuple[str, str]] = []
    for c in candidates:
        r = c["row"]
        title, decision, summary, content = r[1], r[2], r[3], r[4]
        blob = " ".join(t for t in (decision, summary, content) if t)[:2000]
        blobs.append((title or "", blob or ""))

    try:
        ce_scores = cross_rerank(q, blobs)  # 0..1 list aligned to candidates
    except Exception as e:
        logger.warning("Cross-encoder rerank failed, falling back to zeros: %s", e)
        ce_scores = [0.0] * len(candidates)

    def rrf(rank: Optional[int]) -> float:
        if rank is None:
            return 0.0
        return 1.0 / (rrf_k + rank)

    # Score and rank
    scored: List[Tuple[float, tuple]] = []
    for (c, ce) in zip(candidates, ce_scores):
        r = c["row"]
        title, decision, summary, content = r[1], r[2], r[3], r[4]
        sim = float(c["sim"])
        rec = _recency_score(r[11])
        text = " ".join(t for t in (title, decision, summary, content) if t)
        kw = keyword_score(text, kws)               # 0..1
        ev = evidence_bonus(text)                   # 0..0.05
        rrf_score = rrf(c["vec_rank"]) + rrf(c["bm25_rank"]) + rrf(c["kw_rank"])

        # Weighted hybrid + small evidence nudge
        score = (0.50 * ce) + (0.22 * rrf_score) + (0.18 * sim) + (0.07 * kw) + (0.03 * rec) + ev
        scored.append((score, r))

    scored.sort(key=lambda x: x[0], reverse=True)
    rows = [r for _, r in scored[:max(top_k * 2, top_k + 3)]]

    # Real similarity floor (fixes earlier 'or True')
    rows = [r for r in rows if float(r[10]) >= min_sim]
    rows = rows[:top_k]
    if not rows:
        return {"question": q, "answer": "Not enough relevant context found.", "references": []}

    # Build context
    blocks = []
    for i, r in enumerate(rows, start=1):
        _id, title, decision, summary, content, comments, tags, stage, source, url, sim, fetched_at = r
        block = (
            f"[{i}] {title} | source: {source or '-'} | tags: {tags or '-'} | "
            f"stage: {stage or '-'} | sim≈{float(sim):.2f}\n"
            f"Decision: {_clip(decision, 700)}\n"
            f"Summary:  {_clip(summary, 400)}\n"
            f"Content:  {_clip(content, 600)}\n"
            f"Comments:\n{_comments_top(comments)}"
        )
        blocks.append(block)
    context_str = "\n\n".join(blocks)

    prompt = (
        "Use ONLY the context. If it's insufficient, say so briefly and ask a pointed follow-up.\n\n"
        f"Context:\n{context_str}\n\n"
        f"User question:\n{q}\n\n"
        "Respond with exactly this structure:\n"
        "1) 3–5 bullet insights (each ends with [n] and one short quote \"...\") \n"
        "2) One-line takeaway\n"
        "Rules: short sentences; no fluff; contrast viewpoints when present."
    )

    llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    llm_temp = float(os.getenv("LLM_TEMPERATURE", "0.18"))
    max_tokens = int(os.getenv("LLM_MAX_TOKENS", "600"))
    client = oai_client.with_options(timeout=int(os.getenv("OPENAI_TIMEOUT_SEC", "20")))

    try:
        response = client.chat.completions.create(
            model=llm_model,
            messages=[
                {"role": "system", "content": STYLE_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            temperature=llm_temp,
            max_tokens=max_tokens,
        )
        answer = (response.choices[0].message.content or "").strip()
        if not answer:
            answer = "Not enough grounded context to answer confidently."
        # Keep newlines; avoid collapsing bullets
    except Exception as e:
        logger.error("OpenAI API call failed: %s", e)
        raise HTTPException(status_code=502, detail="Failed to fetch answer from LLM.")

    # References
    slim_refs: List[Dict[str, Any]] = [
        {
            "id": r[0],
            "title": r[1],
            "tags": r[6],
            "stage": r[7],
            "source": r[8],
            "url": r[9],
            "similarity": round(float(r[10]), 4),
        }
        for r in rows
    ]

    # Persist chat turns (best-effort)
    sid = _get_session_id(request)
    try:
        ensure_session(sid, user_id=user_id)
        now_ms = int(time.time() * 1000)
        add_message(sid, "user", q, now_ms, None, user_id=user_id)
        add_message(
            sid,
            "assistant",
            answer,
            now_ms + 1,
            {"references": slim_refs},
            user_id=user_id,
        )
    except Exception as e:
        logger.warning("Chat persistence failed: %s", e)

    try:
        logger.info(
            f"/ask ok qlen={len(q)} top_k={top_k} fetch_k={fetch_k} min_sim={min_sim} used={len(rows)} model={llm_model}"
        )
    except Exception:
        pass

    return {"question": q, "answer": answer, "references": slim_refs}


@app.get("/chat/history")
def chat_history(request: Request, limit: int = 100):
    sid = _get_session_id(request)
    try:
        ensure_session(sid)
        turns = get_history(sid, limit=max(1, min(limit, 200)))
    except Exception as e:
        logger.error("Failed to load chat history: %s", e)
        turns = []

    if not turns:
        turns = [{
            "role": "system",
            "content": "Ask anything about growth, pricing, fundraising, or product decisions.",
            "ts": int(time.time() * 1000),
        }]
    return {"turns": turns}


@app.post("/chat/clear")
def chat_clear(request: Request):
    sid = _get_session_id(request)
    try:
        clear_history(sid)
    except Exception as e:
        logger.error("Failed to clear chat history: %s", e)
        raise HTTPException(status_code=500, detail="Failed to clear history.")
    return {"status": "ok"}


@app.post("/admin/cache/clear")
def clear_cache_admin(x_api_key: str = Header(..., description="Admin API key")):
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    cache_clear()
    logger.info("Cache cleared via admin endpoint.")
    return {"status": "ok", "message": "Cache cleared."}
