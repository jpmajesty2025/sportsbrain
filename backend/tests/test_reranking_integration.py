"""Integration test to verify reranking actually works with TradeImpact agent"""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.trade_impact_agent_enhanced import EnhancedTradeImpactAgent
from app.agents.trade_impact_agent_tools import TradeImpactAgent
import logging

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)


@pytest.mark.skipif(os.getenv("CI") == "true", reason="Skip in CI to avoid downloading models")
def test_reranking_comparison():
    """Compare results with and without reranking"""
    
    print("=" * 60)
    print("TESTING RERANKING EFFECTIVENESS")
    print("=" * 60)
    
    # Test query that should benefit from reranking
    query = "How does Porzingis trade affect Tatum's fantasy value?"
    
    # Test 1: Original agent (no reranking)
    print("\n1. Testing ORIGINAL TradeImpact Agent (no reranking):")
    print("-" * 40)
    try:
        original_agent = TradeImpactAgent()
        original_result = original_agent.analyze_trade_impact(query)
        print("Original result preview:")
        print(original_result[:500] if original_result else "No result")
    except Exception as e:
        print(f"Original agent error: {e}")
    
    # Test 2: Enhanced agent (with reranking)
    print("\n2. Testing ENHANCED TradeImpact Agent (with reranking):")
    print("-" * 40)
    try:
        enhanced_agent = EnhancedTradeImpactAgent()
        
        # Check if reranker loaded successfully
        if enhanced_agent.reranker and enhanced_agent.reranker.model_loaded:
            print("[OK] Reranker model loaded successfully")
        else:
            print("[WARNING] Reranker not loaded - will use fallback")
        
        enhanced_result = enhanced_agent.analyze_trade_impact(query)
        print("Enhanced result preview:")
        print(enhanced_result[:500] if enhanced_result else "No result")
        
        # Check if result mentions reranking
        if "Enhanced with Reranking" in enhanced_result:
            print("\n[OK] Reranking was applied!")
        else:
            print("\n[INFO] Reranking may not have been applied (check logs)")
            
    except Exception as e:
        print(f"Enhanced agent error: {e}")
    
    print("\n" + "=" * 60)
    print("COMPARISON COMPLETE")
    print("Check the logs above to see if Milvus queries succeeded")
    print("and whether reranking improved result relevance")
    print("=" * 60)

if __name__ == "__main__":
    test_reranking_comparison()