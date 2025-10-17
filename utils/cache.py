import os
import time
import json
import hashlib
import functools
import threading
import redis
from utils.logger import setup_logger

ENV = os.getenv("ENV", "dev")
_KEY_PREFIX = f"startupscout:{ENV}:"

_CACHE_HITS = 0
_CACHE_MISSES = 0

logger = setup_logger("startupscout.cache")

# ------------------------------------------------------------
# Redis initialization
# ------------------------------------------------------------
REDIS_URL = os.getenv("REDIS_URL")
_USE_REDIS = bool(REDIS_URL)
_REDIS = None
if _USE_REDIS:
    try:
        _REDIS = redis.from_url(REDIS_URL, decode_responses=True)
        _REDIS.ping()
        logger.info("Connected to Redis cache.")
    except Exception as e:
        logger.warning(f"Redis unavailable, falling back to in-memory cache: {e}")
        _USE_REDIS = False

# ------------------------------------------------------------
# Local in-memory fallback cache
# ------------------------------------------------------------
_CACHE = {}
_LOCK = threading.Lock()


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def _normalize_question(val: str) -> str:
    """Normalize question text to make cache key stable."""
    if not isinstance(val, str):
        return ""
    return " ".join(val.strip().split()).lower()


def _stable_key(func_name: str, args: tuple, kwargs: dict) -> str:
    """Deterministic cache key generation."""
    # Special-case ask(question=...)
    if "question" in kwargs and isinstance(kwargs["question"], str):
        norm_q = _normalize_question(kwargs["question"])
        return f"{_KEY_PREFIX}{func_name}:question:{norm_q}"

    # Generic case → hash args/kwargs
    blob = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
    digest = hashlib.sha1(blob.encode()).hexdigest()
    return f"{_KEY_PREFIX}{func_name}:h:{digest}"


# ------------------------------------------------------------
# Core decorator
# ------------------------------------------------------------
def cache_result(ttl: int = 300):
    """
    Decorator for caching results.
    Uses Redis if available; otherwise an in-memory dict with TTL.
    Tracks cache hits/misses for /stats endpoint.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            global _CACHE_HITS, _CACHE_MISSES
            key = _stable_key(func.__name__, args, kwargs)

            # --- Redis path ---
            if _USE_REDIS and _REDIS:
                try:
                    cached = _REDIS.get(key)
                    if cached is not None:
                        _CACHE_HITS += 1
                        logger.debug(f"Redis cache hit for {key}")
                        return json.loads(cached)
                except Exception as e:
                    logger.warning(f"Redis read failed: {e}")

            # --- In-memory fallback ---
            now = time.time()
            with _LOCK:
                if key in _CACHE:
                    value, ts = _CACHE[key]
                    if now - ts < ttl:
                        _CACHE_HITS += 1
                        logger.debug(f"Memory cache hit for {key}")
                        return value

            _CACHE_MISSES += 1  # only increment once if both misses

            # --- Compute result ---
            result = func(*args, **kwargs)

            # --- Store result ---
            if _USE_REDIS and _REDIS:
                try:
                    _REDIS.setex(key, ttl, json.dumps(result, ensure_ascii=False))
                except Exception as e:
                    logger.warning(f"Redis write failed: {e}")
            else:
                with _LOCK:
                    _CACHE[key] = (result, time.time())

            return result
        return wrapper
    return decorator


# ------------------------------------------------------------
# Stats and Clear
# ------------------------------------------------------------
def cache_get_stats():
    """Return cache stats for /stats endpoint."""
    global _CACHE_HITS, _CACHE_MISSES
    stats = {
        "redis_used": _USE_REDIS,
        "hits": _CACHE_HITS,
        "misses": _CACHE_MISSES,
    }

    if _USE_REDIS and _REDIS:
        try:
            info = _REDIS.info()
            stats["keys"] = info.get("db0", {}).get("keys", 0)
        except Exception:
            stats["keys"] = "unknown"
    else:
        with _LOCK:
            stats["entries"] = len(_CACHE)
    return stats


def cache_clear():
    """Clear all cache entries and reset counters."""
    global _CACHE_HITS, _CACHE_MISSES
    if _USE_REDIS and _REDIS:
        try:
            cursor = 0
            while True:
                cursor, keys = _REDIS.scan(cursor=cursor, match=f"{_KEY_PREFIX}*", count=500)
                if keys:
                    _REDIS.delete(*keys)
                if cursor == 0:
                    break
            logger.info("Redis cache cleared (prefix only).")
        except Exception as e:
            logger.warning(f"Redis flush failed: {e}")
    else:
        with _LOCK:
            _CACHE.clear()
            logger.info("In-memory cache cleared.")

    _CACHE_HITS = 0
    _CACHE_MISSES = 0
