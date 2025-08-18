"""Simple verification that reranking is working"""
import os
import sys
import pytest

# Skip this test in CI environment to avoid downloading large models
if os.getenv("CI") == "true":
    pytest.skip("Skipping reranking verification test in CI environment", allow_module_level=True)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.trade_impact_agent_enhanced import EnhancedTradeImpactAgent
import logging

# Suppress warnings
logging.basicConfig(level=logging.ERROR)

def test_reranking():
    print("Testing if reranking is working...")
    print("-" * 40)
    
    agent = EnhancedTradeImpactAgent()
    
    # Check reranker loaded
    if agent.reranker and agent.reranker.model_loaded:
        print("[OK] Reranker model loaded")
    else:
        print("[ERROR] Reranker not loaded")
        return False
    
    # Test query
    result = agent.analyze_trade_impact("How does Porzingis trade affect Tatum?")
    
    # Check if result indicates reranking was used
    if "Enhanced with Reranking" in result:
        print("[OK] Reranking was applied!")
        print("\nFirst 300 chars of result:")
        print(result[:300])
        return True
    else:
        print("[WARNING] Reranking may not have been applied")
        print("\nFirst 300 chars of result:")
        print(result[:300])
        return False

if __name__ == "__main__":
    success = test_reranking()
    print("\n" + "=" * 40)
    if success:
        print("RERANKING IS WORKING!")
    else:
        print("Reranking needs investigation")