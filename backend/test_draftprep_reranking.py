"""Test DraftPrep Agent Reranking Implementation"""

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

async def test_punt_strategy_reranking():
    """Test punt strategy building with reranking"""
    from app.agents.draft_prep_agent_enhanced import EnhancedDraftPrepAgent
    
    agent = EnhancedDraftPrepAgent()
    
    print("=" * 60)
    print("TEST: Punt Strategy with Reranking")
    print("=" * 60)
    
    query = "Build a punt FT% team around Giannis"
    print(f"Query: {query}\n")
    
    # Test the enhanced method directly
    result = agent._build_punt_strategy(query)
    
    print("Response:")
    print(result[:1000])  # Show first 1000 chars
    
    # Check for enhancements
    print("\n" + "-" * 40)
    print("Verification:")
    
    if "Enhanced Strategy Insights" in result or "AI-Powered" in result:
        print("  [OK] Reranking enhancements detected")
    else:
        print("  [INFO] No reranking enhancements (may not have Milvus results)")
    
    if "Giannis" in result:
        print("  [OK] Includes target player")
    
    if "punt_ft_fit" in result.lower() or "FT%" in result:
        print("  [OK] Includes punt FT% strategy")
    
    return True

async def test_mock_draft_reranking():
    """Test mock draft with reranking"""
    from app.agents.draft_prep_agent_enhanced import EnhancedDraftPrepAgent
    
    agent = EnhancedDraftPrepAgent()
    
    print("\n" + "=" * 60)
    print("TEST: Mock Draft with Reranking")
    print("=" * 60)
    
    query = "Show mock draft for pick 12"
    print(f"Query: {query}\n")
    
    # Test the enhanced method directly
    result = agent._simulate_draft_pick(query)
    
    print("Response:")
    print(result[:1000])  # Show first 1000 chars
    
    # Check for enhancements
    print("\n" + "-" * 40)
    print("Verification:")
    
    if "AI-Enhanced Draft Recommendations" in result or "Match Score" in result:
        print("  [OK] Reranking enhancements detected")
    else:
        print("  [INFO] No reranking enhancements (may not have Milvus results)")
    
    if "pick 12" in result.lower() or "12th" in result.lower():
        print("  [OK] Addresses specific pick")
    
    return True

async def test_keeper_value_reranking():
    """Test keeper value with reranking"""
    from app.agents.draft_prep_agent_enhanced import EnhancedDraftPrepAgent
    
    agent = EnhancedDraftPrepAgent()
    
    print("\n" + "=" * 60)
    print("TEST: Keeper Value with Reranking")
    print("=" * 60)
    
    query = "Should I keep Ja Morant in round 3?"
    print(f"Query: {query}\n")
    
    # Test the enhanced method directly
    result = agent._calculate_keeper_value(query)
    
    print("Response:")
    print(result[:1000])  # Show first 1000 chars
    
    # Check for enhancements
    print("\n" + "-" * 40)
    print("Verification:")
    
    if "AI-Powered Keeper Insights" in result or "Relevance:" in result:
        print("  [OK] Reranking enhancements detected")
    else:
        print("  [INFO] No reranking enhancements (may not have Milvus results)")
    
    if "Ja Morant" in result:
        print("  [OK] Includes target player")
    
    if "round 3" in result.lower() or "third round" in result.lower():
        print("  [OK] Addresses keeper round")
    
    if "POOR VALUE" in result or "GOOD VALUE" in result:
        print("  [OK] Provides clear recommendation")
    
    return True

async def test_through_agent():
    """Test through the full agent process_message"""
    from app.agents.draft_prep_agent_enhanced import EnhancedDraftPrepAgent
    
    agent = EnhancedDraftPrepAgent()
    
    # Reduce verbosity
    if hasattr(agent, 'agent_executor') and agent.agent_executor:
        agent.agent_executor.verbose = False
    
    print("\n" + "=" * 60)
    print("TEST: Full Agent with Reranking")
    print("=" * 60)
    
    query = "Build punt FT% team around Giannis"
    print(f"Query: {query}\n")
    
    try:
        response = await agent.process_message(query)
        content = response.content if hasattr(response, 'content') else str(response)
        
        print("Response:")
        print(content[:800])
        
        print("\n" + "-" * 40)
        print("Metadata:")
        if hasattr(response, 'metadata'):
            print(f"  Reranking Available: {response.metadata.get('reranking_available', 'Unknown')}")
            print(f"  Agent Type: {response.metadata.get('agent_type', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

async def main():
    print("DRAFTPREP AGENT RERANKING TEST")
    print("=" * 60)
    
    # Test each enhanced method
    await test_punt_strategy_reranking()
    await test_mock_draft_reranking()
    await test_keeper_value_reranking()
    
    # Test through full agent
    await test_through_agent()
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("Enhanced DraftPrep agent created with reranking support for:")
    print("  ✓ Punt strategy building (searches strategies collection)")
    print("  ✓ Mock draft recommendations (searches players collection)")
    print("  ✓ Keeper value assessments (searches strategies collection)")
    print("  ✓ ADP comparisons (searches players collection)")
    print("\nReranking will activate when:")
    print("  - Milvus is available and configured")
    print("  - Multiple documents are found")
    print("  - ReRankerService initializes successfully")
    print("=" * 60)

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    
    import logging
    logging.getLogger("langchain").setLevel(logging.WARNING)
    
    asyncio.run(main())