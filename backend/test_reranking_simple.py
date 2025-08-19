"""Simple test to check if reranking is actually called"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

if not os.getenv("OPENAI_API_KEY"):
    from dotenv import load_dotenv
    load_dotenv()

def main():
    from app.agents.trade_impact_agent_fixed import FixedTradeImpactAgent
    
    agent = FixedTradeImpactAgent()
    
    print("=" * 60)
    print("CHECKING RERANKING IN TRADEIMPACT AGENT")
    print("=" * 60)
    
    # Check 1: Is reranker initialized?
    print(f"\n1. Reranker initialized: {agent.reranker is not None}")
    
    # Check 2: Test _search_trade_documents (called by LangChain tools)
    print("\n2. Testing _search_trade_documents (used by tools):")
    result = agent._search_trade_documents("Porzingis trade")
    has_doc = "[DOC]" in result
    has_reranking = "Enhanced with Reranking" in result
    print(f"   - Has [DOC] marker: {has_doc}")
    print(f"   - Has 'Enhanced with Reranking': {has_reranking}")
    print(f"   - Result preview: {result[:100]}...")
    
    # Check 3: Test analyze_trade_impact (direct method)
    print("\n3. Testing analyze_trade_impact (direct method):")
    result2 = agent.analyze_trade_impact("Porzingis trade")
    has_reranking2 = "Enhanced with Reranking" in result2
    print(f"   - Has 'Enhanced with Reranking': {has_reranking2}")
    print(f"   - Result preview: {result2[:100]}...")
    
    print("\n" + "=" * 60)
    print("CONCLUSION:")
    if not has_reranking and not has_reranking2:
        print("[PROBLEM] Reranking is NOT being used by TradeImpact agent!")
        print("- LangChain tools call _search_trade_documents which doesn't use reranking")
        print("- Only analyze_trade_impact uses reranking, but tools don't call it")
    elif has_reranking:
        print("[SUCCESS] Reranking IS being used by LangChain tools!")
    else:
        print("[PARTIAL] Reranking works for direct calls but not through tools")
    print("=" * 60)

if __name__ == "__main__":
    main()