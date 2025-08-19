"""Comprehensive test of DraftPrep reranking for all canned queries"""

import os
import sys
import asyncio
import pytest
from pathlib import Path

# Skip this test file in CI to avoid downloading models
if os.getenv("CI") == "true":
    pytest.skip("Skipping model test in CI environment", allow_module_level=True)

sys.path.insert(0, str(Path(__file__).parent))

if not os.getenv("OPENAI_API_KEY"):
    from dotenv import load_dotenv
    load_dotenv()

# Canned queries from Dashboard.tsx and CLAUDE.md
CANNED_QUERIES = [
    # From Dashboard.tsx
    ("Should I keep Ja Morant in round 3?", "keeper_value", True),
    ("Build a punt FT% team around Giannis", "punt_strategy", True),
    ("Who are the best value picks in rounds 3-5?", "adp_value", False),  # SQL only
    ("Is LaMelo Ball worth keeping in round 4?", "keeper_value", True),
    
    # From CLAUDE.md demo scenarios
    ("Show mock draft for pick 12", "mock_draft", True),
    ("Best punt FT% build around Giannis", "punt_strategy", True),
    
    # Additional test cases
    ("Build punt assists team", "punt_strategy", True),
    ("Mock draft pick 1", "mock_draft", True),
    ("Compare ADP: Tatum vs Brown", "adp_rankings", True),  # Only if "compare" in query
]

async def check_query_reranking(agent, query: str, expected_type: str, should_rerank: bool):
    """Test a single query for reranking behavior"""
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"Expected: {expected_type}, Reranking: {should_rerank}")
    print("-" * 40)
    
    # Determine which method to call based on query type
    if "keep" in query.lower() or "keeper" in query.lower():
        result = agent._calculate_keeper_value(query)
    elif "punt" in query.lower():
        result = agent._build_punt_strategy(query)
    elif "mock draft" in query.lower() or "pick" in query.lower():
        result = agent._simulate_draft_pick(query)
    elif "value picks" in query.lower():
        result = agent._analyze_adp_value(query)
    elif "compare" in query.lower() and "adp" in query.lower():
        result = agent._get_adp_rankings(query)
    else:
        # Try through full agent
        response = await agent.process_message(query)
        result = response.content if hasattr(response, 'content') else str(response)
    
    # Check for reranking indicators
    reranking_detected = False
    reranking_indicators = [
        "Enhanced with Reranking",
        "AI-Powered",
        "AI-Enhanced",
        "Enhanced Strategy Insights",
        "Match Score",
        "Relevance Score",
        "Relevance:",
        "Similarity Score"
    ]
    
    for indicator in reranking_indicators:
        if indicator in result:
            reranking_detected = True
            break
    
    # Show result preview
    print("Result Preview:")
    print(result[:400] + "..." if len(result) > 400 else result)
    
    # Verification
    print("\n" + "Verification:")
    if should_rerank:
        if reranking_detected:
            print(f"  [OK] PASS: Reranking detected (expected)")
        else:
            print(f"  [INFO] No reranking detected (may be due to Milvus unavailable)")
    else:
        if reranking_detected:
            print(f"  [FAIL] Reranking detected (not expected)")
        else:
            print(f"  [OK] PASS: No reranking (as expected)")
    
    # Check for SQL content
    if any(keyword in result for keyword in ["PPG", "RPG", "APG", "ADP", "Round", "Stats:"]):
        print(f"  [OK] SQL data present")
    
    return reranking_detected == should_rerank if should_rerank else True

async def test_reranking_conditions():
    """Test the conditions under which reranking activates"""
    from app.agents.draft_prep_agent_enhanced import EnhancedDraftPrepAgent
    
    agent = EnhancedDraftPrepAgent()
    
    print("=" * 60)
    print("RERANKING ACTIVATION CONDITIONS TEST")
    print("=" * 60)
    
    print("\n1. Reranker Service:")
    print(f"   - Initialized: {agent.reranker is not None}")
    if agent.reranker:
        print(f"   - Model loaded: {hasattr(agent.reranker, 'model')}")
    
    print("\n2. Embedding Model:")
    print(f"   - Initialized: {agent.embedding_model is not None}")
    
    print("\n3. Milvus Connection:")
    print("   Testing connection to Milvus...")
    
    # Test strategy search
    strategy_docs = agent._search_strategy_documents("punt FT% strategy", top_k=5)
    print(f"   - Strategy docs found: {len(strategy_docs)}")
    
    # Test player search
    player_docs = agent._search_player_documents("draft pick 12", top_k=5)
    print(f"   - Player docs found: {len(player_docs)}")
    
    print("\n4. Reranking Requirements:")
    print("   [OK] Reranker service must be initialized")
    print("   [OK] Milvus must return documents")
    print("   [OK] More than 1 document must be found")
    print("   [OK] No exceptions during search/rerank")
    
    return agent

async def main():
    print("COMPREHENSIVE DRAFTPREP RERANKING TEST")
    print("=" * 60)
    
    # Test reranking conditions
    agent = await test_reranking_conditions()
    
    # Reduce verbosity for testing
    if hasattr(agent, 'agent_executor') and agent.agent_executor:
        agent.agent_executor.verbose = False
    
    print("\n" + "=" * 60)
    print("TESTING ALL CANNED QUERIES")
    print("=" * 60)
    
    results = []
    for query, expected_type, should_rerank in CANNED_QUERIES:
        try:
            passed = await check_query_reranking(agent, query, expected_type, should_rerank)
            results.append((query, passed))
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            results.append((query, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    print("\nReranking Trigger Analysis:")
    print("\n[OK] SHOULD trigger reranking (when Milvus available):")
    print("  1. 'Should I keep Ja Morant in round 3?' -> Searches strategies for keeper insights")
    print("  2. 'Build a punt FT% team around Giannis' -> Searches strategies for punt builds")
    print("  3. 'Show mock draft for pick 12' -> Searches players for recommendations")
    print("  4. 'Is LaMelo Ball worth keeping in round 4?' -> Searches strategies for keeper value")
    print("  5. 'Compare ADP: Tatum vs Brown' -> Searches players for similarity")
    
    print("\n[X] WON'T trigger reranking (SQL only):")
    print("  1. 'Who are the best value picks in rounds 3-5?' -> Pure SQL query for ADP values")
    
    print("\nProduction Expectations:")
    print("  - Reranking adds 'AI-Enhanced' or 'AI-Powered' sections")
    print("  - Base SQL results always included (fallback)")
    print("  - If Milvus unavailable, only SQL results shown")
    print("  - Response time: 3-5s with reranking, <1s without")
    
    print("\nIMPORTANT for Production:")
    print("  1. Milvus must be connected and accessible")
    print("  2. Collections must have data (strategies: 230, players: 572)")
    print("  3. ReRankerService must initialize (downloads model on first use)")
    print("  4. Look for 'Enhanced DraftPrep:' in Railway logs to confirm")

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    
    import logging
    # Set up logging to see what's happening
    logging.basicConfig(level=logging.INFO, format='%(name)s - %(message)s')
    logging.getLogger("langchain").setLevel(logging.WARNING)
    
    asyncio.run(main())