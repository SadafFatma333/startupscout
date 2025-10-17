# utils/rerank.py
from __future__ import annotations
import re
from typing import List

__all__ = [
    "derive_keywords",
    "keyword_score",
    "blended_score",
    "evidence_bonus",
]

_STOP = {
    "the","a","an","and","or","but","if","then","else","for","of","to","in","on","at",
    "with","without","by","from","is","are","was","were","be","been","being","as",
    "about","into","over","under","it","its","this","that","these","those","you","your"
}
_TOKEN_RE = re.compile(r"[A-Za-z0-9\-]+")

def _tokens(text: str) -> List[str]:
    if not text:
        return []
    return [t.lower() for t in _TOKEN_RE.findall(text)]

def _normalize_token(t: str) -> str:
    if len(t) <= 3:
        return t
    if t.endswith("ies") and len(t) > 4:
        return t[:-3] + "y"
    if t.endswith("s") and not t.endswith("ss"):
        return t[:-1]
    return t

def derive_keywords(question: str) -> List[str]:
    toks = [_normalize_token(t) for t in _tokens(question)]
    unigrams = [t for t in toks if t and t not in _STOP and len(t) >= 3]
    bigrams = [f"{unigrams[i]} {unigrams[i+1]}" for i in range(len(unigrams) - 1)]
    seen, out = set(), []
    for k in (*unigrams, *bigrams):
        if k and k not in seen:
            seen.add(k)
            out.append(k)
    return out

def keyword_score(text: str, keywords: List[str]) -> float:
    if not text or not keywords:
        return 0.0
    t = text.lower()
    hits = 0
    phrases = [k for k in keywords if " " in k]
    unigrams = [k for k in keywords if " " not in k]
    for p in phrases:
        hits += t.count(p)
    for u in unigrams:
        hits += t.count(u)
    return min(1.0, hits / 5.0)

def blended_score(semantic_sim: float, kw_score: float) -> float:
    """(Kept for compatibility) Semantic dominates; keywords get small weight."""
    if kw_score <= 0.0:
        return float(semantic_sim)
    kw_w = min(0.15 + 0.20 * kw_score, 0.35)
    sem_w = 1.0 - kw_w
    return float(sem_w * semantic_sim + kw_w * kw_score)

# -------- Evidence bonus (small nudge for grounded, numeric content) --------
_PCT = re.compile(r"\b\d{1,3}(?:\.\d+)?\s*%")
_MONEY = re.compile(r"\$\s?\d{1,3}(?:[,\d]{0,3})*(?:\.\d+)?\b")
_COUNT = re.compile(r"\b\d{2,}\b")  # 2+ digit counts (e.g., 120 users, 500 signups)
_TIME = re.compile(r"\b(?:\d{1,2}\s*(?:day|week|month|quarter|year)s?)\b", re.I)

def evidence_bonus(text: str) -> float:
    """
    Return 0..0.05 bonus if the chunk contains concrete evidence:
    percentages, dollar amounts, sizable counts, or short time windows.
    This is intentionally tiny so it never dominates ranking.
    """
    if not text:
        return 0.0
    score = 0.0
    if _PCT.search(text):
        score += 0.02
    if _MONEY.search(text):
        score += 0.02
    if _COUNT.search(text):
        score += 0.01
    if _TIME.search(text):
        score += 0.01
    return min(0.05, score)
