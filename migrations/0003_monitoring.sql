-- Prometheus is handled via /metrics. This SQL adds RAG telemetry tables.

CREATE TABLE IF NOT EXISTS rag_events (
  id BIGSERIAL PRIMARY KEY,
  ts TIMESTAMPTZ DEFAULT now(),
  req_id TEXT,
  question TEXT,
  top_k INT,
  fetch_k INT,
  candidates INT,
  used INT,
  min_sim NUMERIC,
  avg_sim NUMERIC,
  avg_ce NUMERIC,
  avg_kw NUMERIC,
  recency_bonus NUMERIC,
  answer_tokens INT,
  prompt_tokens INT,
  model TEXT,
  duration_ms INT,
  cost_usd NUMERIC(10, 6) DEFAULT 0,
  tokens_per_second NUMERIC(10, 2),
  cost_per_1k_tokens NUMERIC(10, 6),
  no_context BOOLEAN DEFAULT FALSE,
  error TEXT
);

CREATE TABLE IF NOT EXISTS rag_items (
  event_id BIGINT REFERENCES rag_events(id) ON DELETE CASCADE,
  rank INT,
  url TEXT,
  title TEXT,
  source TEXT,
  sim NUMERIC,
  ce NUMERIC,
  kw NUMERIC,
  rrf NUMERIC
);

CREATE TABLE IF NOT EXISTS rag_feedback (
  event_id BIGINT REFERENCES rag_events(id) ON DELETE CASCADE,
  rating SMALLINT,        -- -1, 0, 1
  note TEXT,
  ts TIMESTAMPTZ DEFAULT now()
);
