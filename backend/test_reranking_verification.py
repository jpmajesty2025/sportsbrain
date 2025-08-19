"""Verify if reranking is actually being called in TradeImpact agent"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Set up logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set environment variables if not already set
if not os.getenv("OPENAI_API_KEY"):
    from dotenv import load_dotenv
    load_dotenv()

async def test_direct_analyze_trade_impact():
    """Test the analyze_trade_impact method directly (not through LangChain)"""
    print("\n" + "=" * 60)
    print("TEST 1: Direct analyze_trade_impact method")
    print("=" * 60)
    
    from app.agents.trade_impact_agent_fixed import FixedTradeImpactAgent
    
    agent = FixedTradeImpactAgent()
    
    # This should call reranking if it's working
    result = agent.analyze_trade_impact("How does Porzingis trade affect Tatum?")
    
    print("\nDirect method result:")
    print(result[:500])
    
    # Check for reranking indicators
    has_reranking = "Enhanced with Reranking" in result
    print(f"\n[CHECK] Contains 'Enhanced with Reranking': {has_reranking}")
    
    return has_reranking

async def test_langchain_tool_call():
    """Test through LangChain tools (what actually gets called)"""
    print("\n" + "=" * 60)
    print("TEST 2: LangChain Tool Call (_analyze_trade_impact)")
    print("=" * 60)
    
    from app.agents.trade_impact_agent_fixed import FixedTradeImpactAgent
    
    agent = FixedTradeImpactAgent()
    
    # This is what the LangChain tools actually call
    result = agent._analyze_trade_impact("Porzingis trade impact")
    
    print("\nLangChain tool method result:")
    print(result[:500])
    
    # Check for reranking indicators
    has_reranking = "Enhanced with Reranking" in result
    has_doc_marker = "[DOC]" in result
    
    print(f"\n[CHECK] Contains 'Enhanced with Reranking': {has_reranking}")
    print(f"[CHECK] Contains '[DOC]' marker: {has_doc_marker}")
    
    return has_reranking

async def test_full_agent_execution():
    """Test full agent execution through LangChain"""
    print("\n" + "=" * 60)
    print("TEST 3: Full Agent Execution (through LangChain)")
    print("=" * 60)
    
    from app.agents.trade_impact_agent_fixed import FixedTradeImpactAgent
    
    agent = FixedTradeImpactAgent()
    
    # Process through the full agent
    response = await agent.process_message("How does Porzingis trade affect Tatum?")
    
    content = response.content if hasattr(response, 'content') else str(response)
    print("\nFull agent response:")
    print(content[:500])
    
    # Check for reranking indicators
    has_reranking = "Enhanced with Reranking" in content
    has_doc_marker = "[DOC]" in content
    
    print(f"\n[CHECK] Contains 'Enhanced with Reranking': {has_reranking}")
    print(f"[CHECK] Contains '[DOC]' marker: {has_doc_marker}")
    
    return has_reranking

async def test_search_methods():
    """Test the search methods to see what they return"""
    print("\n" + "=" * 60)
    print("TEST 4: Search Methods Comparison")
    print("=" * 60)
    
    from app.agents.trade_impact_agent_fixed import FixedTradeImpactAgent
    
    agent = FixedTradeImpactAgent()
    
    # Test _search_trade_documents_raw (with fixed Hit.get)
    print("\n_search_trade_documents_raw output:")
    raw_results = agent._search_trade_documents_raw("Porzingis trade", top_k=5)
    print(f"  Returns: {type(raw_results)}")
    print(f"  Count: {len(raw_results) if raw_results else 0}")
    if raw_results:
        print(f"  First result keys: {raw_results[0].keys()}")
    
    # Test _search_trade_documents (called by tools)
    print("\n_search_trade_documents output:")
    formatted_results = agent._search_trade_documents("Porzingis trade")
    print(f"  Returns: {type(formatted_results)}")
    print(f"  Length: {len(formatted_results) if formatted_results else 0}")
    print(f"  Preview: {formatted_results[:200] if formatted_results else 'None'}")
    
    return True

async def check_reranker_initialization():
    """Check if reranker is initialized"""
    print("\n" + "=" * 60)
    print("TEST 5: Reranker Initialization Check")
    print("=" * 60)
    
    from app.agents.trade_impact_agent_fixed import FixedTradeImpactAgent
    
    agent = FixedTradeImpactAgent()
    
    has_reranker = agent.reranker is not None
    print(f"[CHECK] Reranker initialized: {has_reranker}")
    
    if has_reranker:
        print(f"  Reranker type: {type(agent.reranker)}")
        print(f"  Reranker class: {agent.reranker.__class__.__name__}")
    
    return has_reranker

async def main():
    """Run all tests"""
    print("=" * 60)
    print("RERANKING VERIFICATION FOR TRADEIMPACT AGENT")
    print("=" * 60)
    
    # Check initialization
    reranker_exists = await check_reranker_initialization()
    
    # Test search methods
    await test_search_methods()
    
    # Test direct method (should have reranking)
    direct_has_reranking = await test_direct_analyze_trade_impact()
    
    # Test LangChain tool method (what actually gets called)
    tool_has_reranking = await test_langchain_tool_call()
    
    # Test full agent
    full_has_reranking = await test_full_agent_execution()
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY:")
    print("=" * 60)
    print(f"Reranker Initialized: {reranker_exists}")
    print(f"Direct method uses reranking: {direct_has_reranking}")
    print(f"LangChain tool uses reranking: {tool_has_reranking}")
    print(f"Full agent uses reranking: {full_has_reranking}")
    
    if not tool_has_reranking:
        print("\n[WARNING] LangChain tools are NOT using reranking!")
        print("The tools call _analyze_trade_impact which doesn't use the reranker.")
        print("Only direct calls to analyze_trade_impact use reranking.")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())