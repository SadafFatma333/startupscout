# utils/cross_rerank.py
from __future__ import annotations
from typing import List, Tuple

# Import our enhanced reranking system
from utils.enhanced_rerank import enhanced_rerank

def rerank(question: str, candidates: List[Tuple[str, str]], batch_size: int = 16) -> List[float]:
    """
    Enhanced reranking that replaces cross-encoder with intelligent keyword-based scoring.
    Maintains high quality while eliminating heavy ML dependencies.
    """
    if not candidates:
        return []
    
    # Use our enhanced reranking system (no ML dependencies)
    return enhanced_rerank(question, candidates, batch_size)
