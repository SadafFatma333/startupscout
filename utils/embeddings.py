# utils/embeddings.py
from __future__ import annotations

import os
import re
from functools import lru_cache
from typing import List, Tuple, Optional

from utils.logger import setup_logger
from config.settings import EMBEDDING_BACKEND, OPENAI_API_KEY

logger = setup_logger("startupscout.embeddings")

# ------------------------------------------------------------------------------
# Configurable Models
# ------------------------------------------------------------------------------

# Prefer env-configurable models, fallback to defaults
_OPENAI_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")   # 1536-dim
_OPENAI_DIM = int(os.getenv("EMBED_DIM", "1536"))

# Local fallback model (upgrade from MiniLM)
_LOCAL_MODEL = os.getenv("LOCAL_EMBED_MODEL", "all-mpnet-base-v2")   # 768-dim
_LOCAL_DIM = int(os.getenv("LOCAL_EMBED_DIM", "768"))

# Safety cap for text length
_MAX_EMBED_CHARS = int(os.getenv("EMBED_MAX_CHARS", "4000"))

# Lazy singletons
_openai_client = None
_local_model = None


# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------
def _normalize(text: str) -> str:
    """Normalize text and truncate to safe length."""
    text = (text or "").strip()
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    if len(text) > _MAX_EMBED_CHARS:
        text = text[:_MAX_EMBED_CHARS]
    return text


def _init_openai():
    global _openai_client
    if _openai_client is not None:
        return _openai_client
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set but EMBEDDING_BACKEND=openai.")
    from openai import OpenAI  # Lazy import
    _openai_client = OpenAI(api_key=OPENAI_API_KEY)
    return _openai_client


def _init_local_model():
    global _local_model
    if _local_model is not None:
        return _local_model
    logger.warning("Local embeddings disabled - using OpenAI embeddings only")
    _local_model = "disabled"
    return _local_model


def get_embedding_dim() -> int:
    return _OPENAI_DIM if EMBEDDING_BACKEND == "openai" else _LOCAL_DIM


# ------------------------------------------------------------------------------
# Cached embedding functions
# ------------------------------------------------------------------------------
@lru_cache(maxsize=2048)
def _embed_openai_cached(text: str) -> Tuple[List[float], str]:
    client = _init_openai()
    resp = client.embeddings.create(input=text, model=_OPENAI_MODEL)
    return resp.data[0].embedding, _OPENAI_MODEL


@lru_cache(maxsize=2048)
def _embed_local_cached(text: str) -> Tuple[List[float], str]:
    # Local embeddings disabled - this should not be called when EMBEDDING_BACKEND=openai
    logger.error("Local embeddings called but disabled - check EMBEDDING_BACKEND setting")
    return [0.0] * _LOCAL_DIM, f"{_LOCAL_MODEL}-disabled"


# ------------------------------------------------------------------------------
# Main embedding API
# ------------------------------------------------------------------------------
def get_embedding(text: str) -> Tuple[List[float], str]:
    """
    Return (embedding_vector, model_name) for the given text.

    - Uses OpenAI or local backend depending on EMBEDDING_BACKEND.
    - Falls back to local if OpenAI fails.
    - Returns a zero-vector for empty text.
    """
    norm = _normalize(text)
    if not norm:
        dim = get_embedding_dim()
        return [0.0] * dim, "empty_text"

    # OpenAI as primary backend
    if EMBEDDING_BACKEND == "openai":
        try:
            return _embed_openai_cached(norm)
        except Exception as e:
            logger.warning("OpenAI embedding failed, falling back to local: %s", e)
            try:
                return _embed_local_cached(norm)
            except Exception as e2:
                logger.error("Local fallback also failed: %s", e2)
                return [0.0] * _OPENAI_DIM, f"{_OPENAI_MODEL}-failed"

    # Local backend only
    try:
        return _embed_local_cached(norm)
    except Exception as e:
        logger.error("Local embedding failed: %s", e)
        return [0.0] * _LOCAL_DIM, f"{_LOCAL_MODEL}-failed"
