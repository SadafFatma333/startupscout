# utils/cross_rerank.py
from __future__ import annotations
from typing import List, Tuple
import os

_model = None

def _load():
    global _model
    if _model is not None:
        return _model
    from sentence_transformers import CrossEncoder  # lazy import
    name = os.getenv("CROSS_ENCODER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    _model = CrossEncoder(name, activation_fn=None)
    return _model

def rerank(question: str, candidates: List[Tuple[str, str]], batch_size: int = 16) -> List[float]:
    """
    candidates: list of (title, text_blob). Returns list of scores (higher=better),
    normalized to 0..1 per batch for stability.
    """
    if not candidates:
        return []
    
    try:
        model = _load()
        pairs = [(question, f"{t}\n\n{text}") for (t, text) in candidates]
        import numpy as np
        scores = model.predict(pairs, batch_size=batch_size).astype("float32")
        # min-max normalize
        smin, smax = float(scores.min()), float(scores.max())
        if smax > smin:
            scores = (scores - smin) / (smax - smin)
        else:
            scores = scores * 0.0
        return scores.tolist()
    except Exception as e:
        # Fallback to simple scoring if cross-encoder fails
        print(f"Cross-encoder failed: {e}, using fallback scoring")
        return [0.5] * len(candidates)  # Equal scores as fallback
