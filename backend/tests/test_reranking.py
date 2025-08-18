"""Test suite for reranking functionality"""
import os
import pytest

# Skip this test in CI environment to avoid downloading large models
if os.getenv("CI") == "true":
    pytest.skip("Skipping reranking tests in CI environment", allow_module_level=True)

from app.services.reranker_service import ReRankerService, RerankResult

class TestReranking:
    
    def test_reranker_initialization(self):
        """Test that reranker initializes correctly"""
        reranker = ReRankerService()
        assert reranker is not None
        assert reranker.model_loaded == True
    
    def test_reranking_improves_relevance(self):
        """Test that reranking improves result relevance"""
        reranker = ReRankerService()
        
        query = "Should I keep Ja Morant in round 3?"
        
        # Mock documents (what Milvus might return)
        documents = [
            {
                "content": "Ja Morant highlights reel 2024 showcasing amazing dunks", 
                "score": 0.89,
                "metadata": {"type": "highlights"}
            },
            {
                "content": "Ja Morant ADP is round 2, keeper value analysis shows poor value in round 3", 
                "score": 0.85,
                "metadata": {"type": "keeper_analysis"}
            },
            {
                "content": "Memphis Grizzlies schedule for upcoming season", 
                "score": 0.83,
                "metadata": {"type": "schedule"}
            },
            {
                "content": "Round 3 keeper strategy guide for fantasy basketball managers", 
                "score": 0.82,
                "metadata": {"type": "strategy"}
            },
            {
                "content": "Ja Morant injury history and risk assessment for fantasy", 
                "score": 0.80,
                "metadata": {"type": "injury"}
            }
        ]
        
        reranked = reranker.rerank(query, documents, top_k=3)
        
        # The keeper value analysis should rank higher
        assert "keeper value" in reranked[0].content.lower()
        assert reranked[0].metadata.get("type") == "keeper_analysis"
        
        # Highlights reel should rank lower (not in top 3)
        highlights_in_top3 = any("highlights" in r.content.lower() for r in reranked)
        assert not highlights_in_top3, "Highlights should not be in top 3 after reranking"
    
    def test_fallback_when_model_fails(self):
        """Test graceful fallback when reranker fails"""
        # Try to load invalid model
        reranker = ReRankerService(model_name="invalid_model_name_that_doesnt_exist")
        
        assert reranker.model_loaded == False
        
        documents = [
            {"content": "test doc 1", "score": 0.5, "metadata": {}},
            {"content": "test doc 2", "score": 0.3, "metadata": {}}
        ]
        
        results = reranker.rerank("query", documents, top_k=2)
        
        # Should return results even with failed model
        assert len(results) == 2
        assert all(isinstance(r, RerankResult) for r in results)
        
        # Should maintain original order (no rank changes)
        assert results[0].rank_change == 0
        assert results[1].rank_change == 0
    
    def test_empty_documents(self):
        """Test handling of empty document list"""
        reranker = ReRankerService()
        results = reranker.rerank("query", [], top_k=5)
        assert results == []
    
    def test_rank_change_calculation(self):
        """Test that rank changes are calculated correctly"""
        reranker = ReRankerService()
        
        query = "punt FT% build with Giannis"
        
        documents = [
            {
                "content": "General Giannis stats and achievements",
                "score": 0.9,
                "metadata": {"id": "doc1"}
            },
            {
                "content": "Punt FT% strategy with Giannis as centerpiece, target Gobert and Simmons",
                "score": 0.7,
                "metadata": {"id": "doc2"}
            },
            {
                "content": "Bucks team news and updates",
                "score": 0.8,
                "metadata": {"id": "doc3"}
            }
        ]
        
        reranked = reranker.rerank(query, documents, top_k=3)
        
        # The punt FT% document should move up
        punt_doc = next((r for r in reranked if r.metadata.get("id") == "doc2"), None)
        assert punt_doc is not None
        assert punt_doc.rank_change > 0, "Punt FT% doc should move up in ranking"
    
    def test_reranking_with_trade_queries(self):
        """Test reranking specifically for trade impact queries"""
        reranker = ReRankerService()
        
        query = "How does Porzingis trade affect Tatum's fantasy value?"
        
        documents = [
            {
                "content": "Porzingis career statistics and injury history",
                "score": 0.88,
                "metadata": {"type": "player_stats"}
            },
            {
                "content": "Tatum usage rate increases with Porzingis spacing, expect +2-3 assists",
                "score": 0.82,
                "metadata": {"type": "trade_impact"}
            },
            {
                "content": "Boston Celtics championship odds after trade",
                "score": 0.85,
                "metadata": {"type": "team_news"}
            },
            {
                "content": "Fantasy impact: Tatum benefits from Porzingis floor spacing, +5% usage",
                "score": 0.80,
                "metadata": {"type": "fantasy_analysis"}
            }
        ]
        
        reranked = reranker.rerank(query, documents, top_k=2)
        
        # Trade impact and fantasy analysis should rank highest
        top_types = [r.metadata.get("type") for r in reranked]
        assert "trade_impact" in top_types or "fantasy_analysis" in top_types
        assert "team_news" not in top_types  # Less relevant for fantasy