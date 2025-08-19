"""Test enhanced DraftPrep with direct Milvus queries"""

import os
import sys
import pytest
from pathlib import Path
from dotenv import load_dotenv

# Skip this test file in CI to avoid downloading models
if os.getenv("CI") == "true":
    pytest.skip("Skipping model test in CI environment", allow_module_level=True)

sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables BEFORE importing app modules
load_dotenv()

# Verify env vars are loaded
print("Environment Check:")
print(f"MILVUS_HOST: {os.getenv('MILVUS_HOST')[:50]}..." if os.getenv('MILVUS_HOST') else "NOT SET")
print(f"MILVUS_TOKEN: {os.getenv('MILVUS_TOKEN')[:20]}..." if os.getenv('MILVUS_TOKEN') else "NOT SET")

# Now import app modules
from app.core.config import settings

print(f"\nSettings Check:")
print(f"settings.MILVUS_HOST: {settings.MILVUS_HOST[:50]}..." if settings.MILVUS_HOST else "NOT SET")
print(f"settings.MILVUS_TOKEN: {settings.MILVUS_TOKEN[:20]}..." if settings.MILVUS_TOKEN else "NOT SET")

def test_strategy_search():
    """Test strategy search directly"""
    from app.agents.draft_prep_agent_enhanced import EnhancedDraftPrepAgent
    
    agent = EnhancedDraftPrepAgent()
    
    print("\n" + "=" * 60)
    print("TESTING STRATEGY SEARCH")
    print("=" * 60)
    
    # Test strategy search
    docs = agent._search_strategy_documents("punt FT% strategy Giannis", top_k=5)
    print(f"Strategy documents found: {len(docs)}")
    
    if docs:
        print("\nFirst document preview:")
        print(f"  Score: {docs[0]['score']:.3f}")
        print(f"  Content: {docs[0]['content'][:100]}...")
    
    return len(docs) > 0

def test_player_search():
    """Test player search directly"""
    from app.agents.draft_prep_agent_enhanced import EnhancedDraftPrepAgent
    
    agent = EnhancedDraftPrepAgent()
    
    print("\n" + "=" * 60)
    print("TESTING PLAYER SEARCH")
    print("=" * 60)
    
    # Test player search
    docs = agent._search_player_documents("mock draft pick 12", top_k=5)
    print(f"Player documents found: {len(docs)}")
    
    if docs:
        print("\nFirst document preview:")
        print(f"  Score: {docs[0]['score']:.3f}")
        print(f"  Content: {docs[0]['content'][:100]}...")
    
    return len(docs) > 0

def test_full_reranking():
    """Test full reranking flow"""
    from app.agents.draft_prep_agent_enhanced import EnhancedDraftPrepAgent
    
    agent = EnhancedDraftPrepAgent()
    
    print("\n" + "=" * 60)
    print("TESTING FULL RERANKING FLOW")
    print("=" * 60)
    
    queries = [
        ("Build a punt FT% team around Giannis", "_build_punt_strategy"),
        ("Show mock draft for pick 12", "_simulate_draft_pick"),
        ("Should I keep Ja Morant in round 3?", "_calculate_keeper_value"),
    ]
    
    for query, method_name in queries:
        print(f"\nQuery: {query}")
        method = getattr(agent, method_name)
        result = method(query)
        
        # Check for AI enhancement
        has_ai = any(indicator in result for indicator in [
            "AI-Powered", "AI-Enhanced", "Enhanced", "Relevance", "Match Score"
        ])
        
        print(f"  AI Enhancement: {'YES' if has_ai else 'NO'}")
        
        if has_ai:
            # Find the AI section
            for marker in ["Enhanced Strategy Insights", "AI-Enhanced", "AI-Powered"]:
                if marker in result:
                    start = result.find(marker)
                    preview = result[start:start+200]
                    print(f"  Preview: {preview}...")
                    break

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    
    import logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(name)s - %(levelname)s - %(message)s')
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    
    # Run tests
    strategy_ok = test_strategy_search()
    player_ok = test_player_search()
    
    if strategy_ok or player_ok:
        test_full_reranking()
    else:
        print("\n[WARNING] Milvus searches not working - check connection")