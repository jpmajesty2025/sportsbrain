"""Test to verify TradeImpact agent now uses reranking through tools"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Set up logging to capture reranking messages
logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Set environment variables if not already set
if not os.getenv("OPENAI_API_KEY"):
    from dotenv import load_dotenv
    load_dotenv()

async def test_tool_method():
    """Test _analyze_trade_impact (called by LangChain tools)"""
    print("\n" + "=" * 60)
    print("Testing _analyze_trade_impact (LangChain tool method)")
    print("=" * 60)
    
    from app.agents.trade_impact_agent_fixed import FixedTradeImpactAgent
    
    agent = FixedTradeImpactAgent()
    
    # Test the method that tools actually call
    result = agent._analyze_trade_impact("What was the fantasy impact of the Porzingis trade?")
    
    print("\nResult preview:")
    print(result[:500] if result else "No result")
    
    # Check for reranking indicators
    has_enhanced = "Enhanced with Reranking" in result
    has_relevance = "Relevance Score" in result
    has_doc = "[DOC]" in result
    
    print("\n" + "-" * 40)
    print("Verification:")
    print(f"  Contains 'Enhanced with Reranking': {has_enhanced}")
    print(f"  Contains 'Relevance Score': {has_relevance}")
    print(f"  Contains '[DOC]' (non-reranked): {has_doc}")
    
    if has_enhanced and has_relevance:
        print("\n[SUCCESS] Reranking IS working through tools!")
    elif has_doc:
        print("\n[FAILED] Still using non-reranked path")
    else:
        print("\n[UNKNOWN] Unclear if reranking is working")
    
    return has_enhanced

async def test_full_agent():
    """Test full agent execution through LangChain"""
    print("\n" + "=" * 60)
    print("Testing Full Agent Execution (LangChain AgentExecutor)")
    print("=" * 60)
    
    from app.agents.trade_impact_agent_fixed import FixedTradeImpactAgent
    
    agent = FixedTradeImpactAgent()
    
    # Suppress verbose output for cleaner test
    if hasattr(agent, 'agent_executor'):
        agent.agent_executor.verbose = False
    
    response = await agent.process_message("How does Porzingis trade affect Tatum?")
    
    content = response.content if hasattr(response, 'content') else str(response)
    
    print("\nAgent response preview:")
    print(content[:500] if content else "No response")
    
    # Check for reranking indicators
    has_enhanced = "Enhanced with Reranking" in content
    has_relevance = "Relevance Score" in content
    
    print("\n" + "-" * 40)
    print("Verification:")
    print(f"  Contains 'Enhanced with Reranking': {has_enhanced}")
    print(f"  Contains 'Relevance Score': {has_relevance}")
    
    return has_enhanced or has_relevance

async def test_direct_method():
    """Test analyze_trade_impact (direct method, not through tools)"""
    print("\n" + "=" * 60)
    print("Testing analyze_trade_impact (direct method)")
    print("=" * 60)
    
    from app.agents.trade_impact_agent_fixed import FixedTradeImpactAgent
    
    agent = FixedTradeImpactAgent()
    
    result = agent.analyze_trade_impact("Porzingis trade impact")
    
    print("\nDirect method result preview:")
    print(result[:300] if result else "No result")
    
    has_enhanced = "Enhanced with Reranking" in result
    print(f"\n  Contains 'Enhanced with Reranking': {has_enhanced}")
    
    return has_enhanced

async def main():
    print("=" * 60)
    print("TRADEIMPACT AGENT RERANKING VERIFICATION")
    print("=" * 60)
    
    # Test 1: Tool method (most important)
    tool_works = await test_tool_method()
    
    # Test 2: Full agent
    full_works = await test_full_agent()
    
    # Test 3: Direct method (for comparison)
    direct_works = await test_direct_method()
    
    # Summary
    print("\n" + "=" * 60)
    print("FINAL VERIFICATION SUMMARY:")
    print("=" * 60)
    print(f"Tool method (_analyze_trade_impact): {'[PASS] Uses reranking' if tool_works else '[FAIL] No reranking'}")
    print(f"Full agent execution: {'[PASS] Uses reranking' if full_works else '[FAIL] No reranking'}")
    print(f"Direct method: {'[PASS] Uses reranking' if direct_works else '[FAIL] No reranking'}")
    
    if tool_works:
        print("\n[SUCCESS] TradeImpact agent NOW properly uses reranking!")
        print("The fix is complete and working correctly.")
    else:
        print("\n[PROBLEM] Reranking still not working through tools")
        print("Additional debugging needed.")
    
    print("=" * 60)

if __name__ == "__main__":
    # Run with less verbosity
    import warnings
    warnings.filterwarnings("ignore")
    
    asyncio.run(main())