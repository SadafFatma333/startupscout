# utils/enhanced_rerank.py
from __future__ import annotations
from typing import List, Tuple
import re
import math
from collections import Counter

def enhanced_rerank(question: str, candidates: List[Tuple[str, str]], batch_size: int = 16) -> List[float]:
    """
    Enhanced keyword-based reranking that can replace cross-encoder.
    Uses multiple scoring signals for better quality than simple keyword matching.
    
    Args:
        question: The search question
        candidates: List of (title, text) tuples to rerank
        batch_size: Ignored (for compatibility with cross-encoder API)
    
    Returns:
        List of scores (0-1, higher=better) for each candidate
    """
    if not candidates:
        return []
    
    # Extract enhanced keywords from question
    question_keywords = _extract_enhanced_keywords(question)
    
    scores = []
    for title, text in candidates:
        content = f"{title} {text}".lower()
        
        # Multiple scoring signals
        keyword_score = _calculate_keyword_score(content, question_keywords)
        semantic_score = _calculate_semantic_score(question, title, text)
        position_score = _calculate_position_score(content, question_keywords)
        length_score = _calculate_length_score(content)
        evidence_score = _calculate_evidence_score(content)
        
        # Weighted combination (tuned for startup content)
        final_score = (
            keyword_score * 0.35 +      # Keyword matching (most important)
            semantic_score * 0.25 +     # Semantic similarity
            position_score * 0.20 +     # Keyword position importance
            evidence_score * 0.15 +     # Concrete data bonus
            length_score * 0.05         # Length penalty
        )
        
        scores.append(min(1.0, max(0.0, final_score)))
    
    # Normalize scores to 0-1 range
    if scores:
        min_score = min(scores)
        max_score = max(scores)
        if max_score > min_score:
            scores = [(s - min_score) / (max_score - min_score) for s in scores]
        else:
            scores = [0.5] * len(scores)
    
    return scores

def _extract_enhanced_keywords(question: str) -> dict:
    """Extract keywords with different weights and types."""
    question_lower = question.lower()
    
    # Startup-specific important terms
    startup_terms = {
        'funding', 'investment', 'investor', 'vc', 'venture', 'capital',
        'startup', 'founder', 'co-founder', 'ceo', 'cto',
        'revenue', 'profit', 'growth', 'scale', 'scaling',
        'product', 'market', 'customer', 'user', 'traction',
        'pitch', 'deck', 'presentation', 'demo',
        'series a', 'series b', 'seed', 'angel', 'round',
        'valuation', 'equity', 'shares', 'stock',
        'saas', 'b2b', 'b2c', 'enterprise', 'consumer'
    }
    
    # Extract all words
    words = re.findall(r'\b\w+\b', question_lower)
    word_counts = Counter(words)
    
    keywords = {}
    for word in words:
        if len(word) < 3:  # Skip short words
            continue
            
        # Weight by importance
        weight = 1.0
        if word in startup_terms:
            weight = 2.0  # Double weight for startup terms
        elif word_counts[word] > 1:
            weight = 1.5  # Slight boost for repeated words
            
        keywords[word] = weight
    
    # Add bigrams (two-word phrases)
    for i in range(len(words) - 1):
        bigram = f"{words[i]} {words[i+1]}"
        if bigram in startup_terms:
            keywords[bigram] = 3.0  # Triple weight for important bigrams
    
    return keywords

def _calculate_keyword_score(content: str, keywords: dict) -> float:
    """Calculate keyword matching score with weights."""
    if not keywords:
        return 0.5
    
    total_weight = 0.0
    matched_weight = 0.0
    
    for keyword, weight in keywords.items():
        total_weight += weight
        if keyword in content:
            matched_weight += weight
            # Bonus for multiple occurrences
            matches = content.count(keyword)
            if matches > 1:
                matched_weight += weight * 0.5 * (matches - 1)
    
    return matched_weight / total_weight if total_weight > 0 else 0.0

def _calculate_semantic_score(question: str, title: str, text: str) -> float:
    """Calculate semantic similarity using word overlap and synonyms."""
    question_words = set(re.findall(r'\b\w+\b', question.lower()))
    content_words = set(re.findall(r'\b\w+\b', f"{title} {text}".lower()))
    
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'if', 'then', 'else', 'for', 'of', 'to',
        'in', 'on', 'at', 'with', 'without', 'by', 'from', 'is', 'are', 'was', 'were',
        'be', 'been', 'being', 'as', 'about', 'into', 'over', 'under', 'it', 'its',
        'this', 'that', 'these', 'those', 'you', 'your', 'we', 'our', 'they', 'their'
    }
    
    question_words = {w for w in question_words if w not in stop_words and len(w) > 2}
    content_words = {w for w in content_words if w not in stop_words and len(w) > 2}
    
    if not question_words:
        return 0.5
    
    # Basic overlap
    overlap = len(question_words & content_words)
    basic_score = overlap / len(question_words)
    
    # Synonym matching (simple heuristic)
    synonym_bonus = 0.0
    for q_word in question_words:
        for c_word in content_words:
            if _are_synonyms(q_word, c_word):
                synonym_bonus += 0.1
    
    return min(1.0, basic_score + synonym_bonus)

def _are_synonyms(word1: str, word2: str) -> bool:
    """Simple synonym detection for startup terms."""
    synonyms = {
        'funding': ['money', 'capital', 'investment', 'cash'],
        'startup': ['company', 'business', 'venture', 'firm'],
        'founder': ['creator', 'owner', 'entrepreneur'],
        'revenue': ['income', 'sales', 'earnings'],
        'customer': ['client', 'user', 'buyer'],
        'product': ['service', 'solution', 'offering'],
        'market': ['industry', 'sector', 'space'],
        'growth': ['expansion', 'scaling', 'increase'],
        'pitch': ['presentation', 'demo', 'proposal'],
        'valuation': ['worth', 'value', 'price']
    }
    
    for key, values in synonyms.items():
        if (word1 == key and word2 in values) or (word2 == key and word1 in values):
            return True
    return False

def _calculate_position_score(content: str, keywords: dict) -> float:
    """Score based on keyword position (title > beginning > end)."""
    if not keywords:
        return 0.5
    
    # Split content into title and body (rough approximation)
    lines = content.split('\n')
    title = lines[0] if lines else ""
    body = ' '.join(lines[1:]) if len(lines) > 1 else content
    
    score = 0.0
    total_weight = 0.0
    
    for keyword, weight in keywords.items():
        total_weight += weight
        
        # Title gets highest weight
        if keyword in title.lower():
            score += weight * 1.0
        # Beginning of body gets medium weight
        elif body.lower().find(keyword) < len(body) * 0.3:
            score += weight * 0.7
        # End gets lower weight
        else:
            score += weight * 0.3
    
    return score / total_weight if total_weight > 0 else 0.0

def _calculate_length_score(content: str) -> float:
    """Penalize very short or very long content."""
    length = len(content)
    
    # Optimal length is around 200-800 characters
    if 200 <= length <= 800:
        return 1.0
    elif length < 100:
        return 0.3  # Too short
    elif length > 2000:
        return 0.7  # Too long
    else:
        return 0.8  # Acceptable

def _calculate_evidence_score(content: str) -> float:
    """Score based on concrete evidence (numbers, percentages, etc.)."""
    score = 0.0
    
    # Percentages
    if re.search(r'\b\d{1,3}(?:\.\d+)?\s*%', content):
        score += 0.3
    
    # Money amounts
    if re.search(r'\$\s?\d{1,3}(?:[,\d]{0,3})*(?:\.\d+)?\b', content):
        score += 0.3
    
    # Large numbers (counts, metrics)
    if re.search(r'\b\d{2,}\b', content):
        score += 0.2
    
    # Time periods
    if re.search(r'\b(?:\d{1,2}\s*(?:day|week|month|quarter|year)s?)\b', content, re.I):
        score += 0.2
    
    return min(1.0, score)
