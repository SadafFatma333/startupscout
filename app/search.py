from fastapi import APIRouter, Query
from psycopg import connect
from config.settings import DB_CONFIG
from utils.embeddings import get_embedding  # reuse your existing embedding function

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/")
def search(
    query: str = Query(..., description="Search across startup decisions"),
    top_k: int = 5
):
    """Return top matching startup decisions from Postgres using pgvector similarity"""

    # 1. Generate embedding for query
    q_vec, _ = get_embedding(query)

    # 2. Connect to Postgres
    conn = connect(**DB_CONFIG)
    cur = conn.cursor()

    # 3. Execute vector similarity search
    cur.execute(
        """
        SELECT title, decision, tags, stage,
               1 - (embedding <#> %s::vector) AS score
        FROM decisions
        ORDER BY embedding <-> %s::vector
        LIMIT %s;
        """,
        (q_vec, q_vec, top_k)
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()

    # 4. Format results
    results = [
        {
            "title": r[0],
            "decision": r[1],
            "tags": r[2],
            "stage": r[3],
            "score": float(r[4])
        }
        for r in rows
    ]

    return {"query": query, "results": results}
