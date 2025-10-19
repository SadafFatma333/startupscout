# tests/test_rag_pipeline.py
import pytest
from unittest.mock import patch, Mock

from utils.embeddings import get_embedding
from utils.rerank import derive_keywords, keyword_score, evidence_bonus
from utils.cross_rerank import rerank as cross_rerank


class TestEmbeddings:
    """Test embeddings functionality."""
    
    def test_get_embedding(self):
        """Test text embedding generation."""
        with patch('utils.embeddings.get_embedding') as mock_get_embedding:
            # Mock returns 768-dim local model (what actually runs in tests)
            mock_get_embedding.return_value = ([0.1] * 768, "all-mpnet-base-v2")
            
            text = "This is a test query"
            result, model = get_embedding(text)
            
            assert isinstance(result, list)
            assert len(result) == 768  # Local model dimension
            assert all(isinstance(x, float) for x in result)
            assert model == "all-mpnet-base-v2"


class TestRerank:
    """Test reranking functionality."""
    
    def test_derive_keywords(self):
        """Test keyword extraction."""
        query = "How to build a successful startup?"
        keywords = derive_keywords(query)
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
    
    def test_keyword_score(self):
        """Test keyword scoring."""
        query = "startup funding"
        text = "This article discusses startup funding strategies"
        
        score = keyword_score(query, text)
        
        assert isinstance(score, float)
        assert score >= 0.0
    
    def test_evidence_bonus(self):
        """Test evidence bonus calculation."""
        text = "startup funding startup funding startup funding"
        
        bonus = evidence_bonus(text)
        
        assert isinstance(bonus, float)
        assert bonus >= 0.0


class TestCrossRerank:
    """Test cross-encoder reranking."""
    
    def test_rerank_documents(self):
        """Test document reranking."""
        with patch('sentence_transformers.CrossEncoder') as mock_ce:
            mock_model = Mock()
            mock_model.predict.return_value = [0.9, 0.8, 0.7, 0.6]
            mock_ce.return_value = mock_model
            
            query = "startup funding"
            candidates = [
                ("Doc 1", "About startup funding strategies"),
                ("Doc 2", "General business advice"),
                ("Doc 3", "Technology trends"),
                ("Doc 4", "Marketing tips")
            ]
            
            scores = cross_rerank(query, candidates)
            
            assert isinstance(scores, list)
            assert len(scores) == 4
            assert all(isinstance(score, float) for score in scores)