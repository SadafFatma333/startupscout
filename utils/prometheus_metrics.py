"""
Custom Prometheus metrics for StartupScout
"""
from prometheus_client import Counter, Histogram, Gauge, Summary
import time

# Request metrics
REQUEST_COUNT = Counter(
    'startupscout_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'startupscout_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

# RAG pipeline metrics
RAG_QUERIES_TOTAL = Counter(
    'startupscout_rag_queries_total',
    'Total number of RAG queries',
    ['model', 'status']
)

RAG_DURATION = Histogram(
    'startupscout_rag_duration_seconds',
    'RAG pipeline duration in seconds',
    ['model']
)

# Vector search metrics
VECTOR_SEARCH_DURATION = Histogram(
    'startupscout_vector_search_duration_seconds',
    'Vector search duration in seconds'
)

VECTOR_SEARCH_RESULTS = Histogram(
    'startupscout_vector_search_results_count',
    'Number of results from vector search',
    buckets=(1, 2, 3, 4, 5, 10, 15, 20, 30, 50, float('inf'))
)

# Keyword search metrics
KEYWORD_SEARCH_DURATION = Histogram(
    'startupscout_keyword_search_duration_seconds',
    'Keyword search duration in seconds'
)

KEYWORD_SEARCH_RESULTS = Histogram(
    'startupscout_keyword_search_results_count',
    'Number of results from keyword search',
    buckets=(1, 2, 3, 4, 5, 10, 15, 20, 30, 50, float('inf'))
)

# Reranking metrics
RERANK_DURATION = Histogram(
    'startupscout_rerank_duration_seconds',
    'Reranking duration in seconds'
)

RERANK_CANDIDATES = Histogram(
    'startupscout_rerank_candidates_count',
    'Number of candidates before reranking',
    buckets=(1, 5, 10, 15, 20, 30, 50, 100, float('inf'))
)

# LLM metrics
LLM_CALLS_TOTAL = Counter(
    'startupscout_llm_calls_total',
    'Total number of LLM calls',
    ['model', 'status']
)

LLM_DURATION = Histogram(
    'startupscout_llm_duration_seconds',
    'LLM call duration in seconds',
    ['model']
)

LLM_COST_USD = Counter(
    'startupscout_llm_cost_usd_total',
    'Total LLM cost in USD',
    ['model']
)

LLM_TOKENS = Counter(
    'startupscout_llm_tokens_total',
    'Total LLM tokens used',
    ['model', 'token_type']  # token_type: prompt, completion, total
)

LLM_TOKENS_PER_SECOND = Gauge(
    'startupscout_llm_tokens_per_second',
    'LLM tokens per second',
    ['model']
)

LLM_COST_PER_1K_TOKENS = Gauge(
    'startupscout_llm_cost_per_1k_tokens',
    'LLM cost per 1000 tokens in USD',
    ['model']
)

# Database metrics
DB_CONNECTIONS_ACTIVE = Gauge(
    'startupscout_db_connections_active',
    'Number of active database connections'
)

DB_QUERY_DURATION = Histogram(
    'startupscout_db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type']
)

# Cache metrics
CACHE_HITS = Counter(
    'startupscout_cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

CACHE_MISSES = Counter(
    'startupscout_cache_misses_total',
    'Total cache misses',
    ['cache_type']
)

CACHE_SIZE = Gauge(
    'startupscout_cache_size',
    'Cache size in bytes',
    ['cache_type']
)

# Business metrics
ANSWERS_GENERATED = Counter(
    'startupscout_answers_generated_total',
    'Total answers generated',
    ['model']
)

REFERENCES_RETURNED = Histogram(
    'startupscout_references_returned_count',
    'Number of references returned per answer',
    buckets=(0, 1, 2, 3, 4, 5, 10, float('inf'))
)

# Quality metrics
ANSWER_LENGTH = Histogram(
    'startupscout_answer_length_chars',
    'Answer length in characters',
    buckets=(50, 100, 200, 500, 1000, 2000, float('inf'))
)

CONTEXT_UTILIZATION = Histogram(
    'startupscout_context_utilization_ratio',
    'Ratio of context used vs available',
    buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
)

# Error metrics
ERRORS_TOTAL = Counter(
    'startupscout_errors_total',
    'Total errors',
    ['error_type', 'component']
)

# System metrics
ACTIVE_SESSIONS = Gauge(
    'startupscout_active_sessions',
    'Number of active user sessions'
)

def record_request(method: str, endpoint: str, status: int, duration: float):
    """Record request metrics"""
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
    REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

def record_rag_query(model: str, status: str, duration: float):
    """Record RAG query metrics"""
    RAG_QUERIES_TOTAL.labels(model=model, status=status).inc()
    RAG_DURATION.labels(model=model).observe(duration)

def record_vector_search(duration: float, results_count: int):
    """Record vector search metrics"""
    VECTOR_SEARCH_DURATION.observe(duration)
    VECTOR_SEARCH_RESULTS.observe(results_count)

def record_keyword_search(duration: float, results_count: int):
    """Record keyword search metrics"""
    KEYWORD_SEARCH_DURATION.observe(duration)
    KEYWORD_SEARCH_RESULTS.observe(results_count)

def record_rerank(duration: float, candidates_count: int):
    """Record reranking metrics"""
    RERANK_DURATION.observe(duration)
    RERANK_CANDIDATES.observe(candidates_count)

def record_llm_call(model: str, status: str, duration: float, 
                   prompt_tokens: int, completion_tokens: int, 
                   cost_usd: float):
    """Record LLM call metrics"""
    total_tokens = prompt_tokens + completion_tokens
    tokens_per_second = total_tokens / duration if duration > 0 else 0
    cost_per_1k_tokens = cost_usd / (total_tokens / 1000) if total_tokens > 0 else 0
    
    LLM_CALLS_TOTAL.labels(model=model, status=status).inc()
    LLM_DURATION.labels(model=model).observe(duration)
    LLM_COST_USD.labels(model=model).inc(cost_usd)
    LLM_TOKENS.labels(model=model, token_type='prompt').inc(prompt_tokens)
    LLM_TOKENS.labels(model=model, token_type='completion').inc(completion_tokens)
    LLM_TOKENS.labels(model=model, token_type='total').inc(total_tokens)
    LLM_TOKENS_PER_SECOND.labels(model=model).set(tokens_per_second)
    LLM_COST_PER_1K_TOKENS.labels(model=model).set(cost_per_1k_tokens)

def record_db_query(query_type: str, duration: float):
    """Record database query metrics"""
    DB_QUERY_DURATION.labels(query_type=query_type).observe(duration)

def record_cache_hit(cache_type: str):
    """Record cache hit"""
    CACHE_HITS.labels(cache_type=cache_type).inc()

def record_cache_miss(cache_type: str):
    """Record cache miss"""
    CACHE_MISSES.labels(cache_type=cache_type).inc()

def record_answer_generated(model: str, answer_length: int, references_count: int, 
                          context_utilization: float):
    """Record answer generation metrics"""
    ANSWERS_GENERATED.labels(model=model).inc()
    ANSWER_LENGTH.observe(answer_length)
    REFERENCES_RETURNED.observe(references_count)
    CONTEXT_UTILIZATION.observe(context_utilization)

def record_error(error_type: str, component: str):
    """Record error metrics"""
    ERRORS_TOTAL.labels(error_type=error_type, component=component).inc()

def set_active_sessions(count: int):
    """Set active sessions count"""
    ACTIVE_SESSIONS.set(count)

def set_db_connections_active(count: int):
    """Set active database connections count"""
    DB_CONNECTIONS_ACTIVE.set(count)

def set_cache_size(cache_type: str, size_bytes: int):
    """Set cache size"""
    CACHE_SIZE.labels(cache_type=cache_type).set(size_bytes)
