# app/graph.py
from typing import TypedDict, List, Tuple, Any, Dict
from langgraph.graph import StateGraph, END
from datetime import datetime
from utils.embeddings import get_embedding
from utils.rerank import derive_keywords, keyword_score
from utils.logger import setup_logger
from psycopg_pool import ConnectionPool
import os

logger = setup_logger("startupscout.graph")

class RAGState(TypedDict, total=False):
    question: str
    q_vec: List[float]
    fetch_k: int
    min_sim: float
    kws: List[str]
    vec_rows: List[tuple]
    bm25_rows: List[tuple]
    kw_rows: List[tuple]
    candidates: List[tuple]
    ce_scores: List[float]
    final_rows: List[tuple]
    context_str: str
    prompt: str
    answer: str

def node_embed(state: RAGState) -> RAGState:
    q = state["question"]
    vec, _ = get_embedding(q)
    state["q_vec"] = vec
    return state

def node_keywords(state: RAGState) -> RAGState:
    state["kws"] = derive_keywords(state["question"])
    return state

def node_fetch(pool: ConnectionPool):
    def _inner(state: RAGState) -> RAGState:
        q_vec = state["q_vec"]
        fetch_k = state["fetch_k"]
        kws = state["kws"]
        kw_patterns = [f"%{kw}%" for kw in kws][:8] or [f"%{state['question'][:32]}%"]
        with pool.connection() as conn, conn.cursor() as cur:
            # vector
            cur.execute("""
                SELECT id,title,decision,summary,content,comments,tags,stage,source,url,
                       1 - (embedding <=> %s::vector) AS sim, fetched_at
                FROM decisions
                WHERE embedding IS NOT NULL
                ORDER BY embedding <-> %s::vector
                LIMIT %s;""", (q_vec, q_vec, fetch_k))
            state["vec_rows"] = cur.fetchall()
            # bm25/ts_rank
            lang = os.getenv("TS_LANG","english")
            tsv = f"to_tsvector('{lang}', coalesce(title,'')||' '||coalesce(decision,'')||' '||coalesce(content,''))"
            tsq = f"websearch_to_tsquery('{lang}', %s)"
            cur.execute(f"""
                SELECT id,title,decision,summary,content,comments,tags,stage,source,url,
                       0.0 AS sim, fetched_at,
                       COALESCE((SELECT 1 FROM pg_extension WHERE extname='pg_bm25'),0) AS has_bm25,
                       CASE WHEN EXISTS(SELECT 1 FROM pg_extension WHERE extname='pg_bm25')
                            THEN bm25({tsv}, {tsq})
                            ELSE ts_rank({tsv}, {tsq})
                       END AS bm25_score
                FROM decisions
                WHERE {tsv} @@ {tsq}
                ORDER BY bm25_score DESC
                LIMIT %s;""", (state["question"], state["question"], fetch_k))
            state["bm25_rows"] = cur.fetchall()
            # keyword
            cur.execute("""
                SELECT id,title,decision,summary,content,comments,tags,stage,source,url,
                       0.0 AS sim, fetched_at
                FROM decisions
                WHERE (title ILIKE ANY(%s) OR decision ILIKE ANY(%s) OR content ILIKE ANY(%s))
                ORDER BY fetched_at DESC NULLS LAST
                LIMIT %s;""", (kw_patterns, kw_patterns, kw_patterns, fetch_k))
            state["kw_rows"] = cur.fetchall()
        return state
    return _inner

def node_merge_and_rank(state: RAGState) -> RAGState:
    # Merge + simple RRF + recency + keyword (same logic as in /ask)
    def key_of(r): return (r[9] or (r[1], r[8]))
    vec, bm25, kw = state["vec_rows"], state["bm25_rows"], state["kw_rows"]
    rrf_k = int(os.getenv("RRF_K","60"))
    def rank_map(rows): return {key_of(r): i+1 for i,r in enumerate(rows)}
    vec_rank, bm25_rank, kw_rank = rank_map(vec), rank_map(bm25), rank_map(kw)
    merged: Dict[Any, Dict[str,Any]] = {}
    for src_rows, tag in [(vec,"vec"),(bm25,"bm25"),(kw,"kw")]:
        for r in src_rows:
            k = key_of(r)
            ent = merged.setdefault(k, {"row": r, "sim": float(r[10]), "vec_rank": None, "bm25_rank": None, "kw_rank": None})
            if float(r[10]) > ent["sim"]:
                ent["row"] = r; ent["sim"] = float(r[10])
            if tag == "vec": ent["vec_rank"] = vec_rank.get(k)
            if tag == "bm25": ent["bm25_rank"] = bm25_rank.get(k)
            if tag == "kw": ent["kw_rank"] = kw_rank.get(k)
    def rrf(rank): return 0.0 if rank is None else 1.0/(rrf_k+rank)
    kws = state["kws"]
    cands = []
    for ent in merged.values():
        r = ent["row"]
        title, decision, summary, content = r[1], r[2], r[3], r[4]
        text = " ".join(t for t in (title,decision,summary,content) if t)
        kw_s = keyword_score(text, kws)
        rec = 0.0
        fa = r[11]
        if isinstance(fa, datetime):
            rec = 1.0
        score = 0.22*(rrf(ent["vec_rank"])+rrf(ent["bm25_rank"])+rrf(ent["kw_rank"])) + 0.18*ent["sim"] + 0.07*kw_s + 0.03*rec
        cands.append((score,r))
    cands.sort(key=lambda x:x[0], reverse=True)
    state["candidates"] = [r for _,r in cands]
    return state

def build_graph(pool: ConnectionPool):
    g = StateGraph(RAGState)
    g.add_node("embed", node_embed)
    g.add_node("keywords", node_keywords)
    g.add_node("fetch", node_fetch(pool))
    g.add_node("merge_rank", node_merge_and_rank)
    g.add_edge("embed", "keywords")
    g.add_edge("keywords", "fetch")
    g.add_edge("fetch", "merge_rank")
    g.set_entry_point("embed")
    g.set_finish_point("merge_rank")
    return g.compile()
