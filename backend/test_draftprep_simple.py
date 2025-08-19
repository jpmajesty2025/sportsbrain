"""Simple test to verify DraftPrep reranking triggers"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

if not os.getenv("OPENAI_API_KEY"):
    from dotenv import load_dotenv
    load_dotenv()

def test_reranking_status():
    """Check if reranking would trigger in production"""
    from app.agents.draft_prep_agent_enhanced import EnhancedDraftPrepAgent
    
    agent = EnhancedDraftPrepAgent()
    
    print("DRAFTPREP RERANKING STATUS CHECK")
    print("=" * 60)
    
    # Check components
    print("\n1. Components Status:")
    print(f"   Reranker: {'YES' if agent.reranker else 'NO'}")
    print(f"   Embedding Model: {'YES' if agent.embedding_model else 'NO'}")
    
    # Test each method
    print("\n2. Testing Each Query Type:")
    
    # 1. Keeper value - should search strategies
    print("\n   Keeper Value Query:")
    query = "Should I keep Ja Morant in round 3?"
    result = agent._calculate_keeper_value(query)
    has_ai = "AI-Powered" in result or "Enhanced" in result
    print(f"   - Query: {query}")
    print(f"   - Has AI section: {'YES' if has_ai else 'NO (Milvus not available)'}")
    
    # 2. Punt strategy - should search strategies  
    print("\n   Punt Strategy Query:")
    query = "Build a punt FT% team around Giannis"
    result = agent._build_punt_strategy(query)
    has_ai = "AI-Powered" in result or "Enhanced" in result
    print(f"   - Query: {query}")
    print(f"   - Has AI section: {'YES' if has_ai else 'NO (Milvus not available)'}")
    
    # 3. Mock draft - should search players
    print("\n   Mock Draft Query:")
    query = "Show mock draft for pick 12"
    result = agent._simulate_draft_pick(query)
    has_ai = "AI-Enhanced" in result or "Match Score" in result
    print(f"   - Query: {query}")
    print(f"   - Has AI section: {'YES' if has_ai else 'NO (Milvus not available)'}")
    
    # 4. ADP comparison - should search players if "compare" in query
    print("\n   ADP Comparison Query:")
    query = "Compare ADP: Tatum vs Brown"
    result = agent._get_adp_rankings(query)
    has_ai = "Similar Players" in result or "Similarity Score" in result
    print(f"   - Query: {query}")
    print(f"   - Has AI section: {'YES' if has_ai else 'NO (only triggers with compare keyword)'}")
    
    # 5. Value picks - SQL only
    print("\n   Value Picks Query:")
    query = "Who are the best value picks in rounds 3-5?"
    result = agent._analyze_adp_value(query)
    has_ai = "AI" in result or "Enhanced" in result
    print(f"   - Query: {query}")
    print(f"   - Has AI section: {'YES (unexpected!)' if has_ai else 'NO (SQL only - expected)'}")
    
    print("\n" + "=" * 60)
    print("PRODUCTION EXPECTATIONS:")
    print("=" * 60)
    
    print("\nWHEN MILVUS IS AVAILABLE IN PRODUCTION:")
    print("  [YES] 'Should I keep Ja Morant in round 3?' - Adds AI keeper insights")
    print("  [YES] 'Build a punt FT% team around Giannis' - Adds AI strategy insights")
    print("  [YES] 'Show mock draft for pick 12' - Adds AI player recommendations")
    print("  [YES] 'Is LaMelo Ball worth keeping in round 4?' - Adds AI keeper insights")
    print("  [YES] 'Compare ADP: Tatum vs Brown' - Adds similar player analysis")
    print("  [NO]  'Who are the best value picks in rounds 3-5?' - SQL only")
    
    print("\nHOW TO VERIFY IN PRODUCTION:")
    print("  1. Check Railway logs for 'Enhanced DraftPrep:'")
    print("  2. Look for 'AI-Enhanced' or 'AI-Powered' sections in responses")
    print("  3. Response time will be 3-5s with reranking vs <1s without")
    print("  4. Base SQL results are ALWAYS included (fallback)")

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    test_reranking_status()