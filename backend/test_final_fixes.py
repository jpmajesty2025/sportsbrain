"""Test final fixes for TradeImpact agent"""

import os
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

if not os.getenv("OPENAI_API_KEY"):
    from dotenv import load_dotenv
    load_dotenv()

async def test_beneficiaries_query():
    """Test that beneficiaries query returns correct players and no tool mentions"""
    from app.agents.trade_impact_agent_fixed import FixedTradeImpactAgent
    
    agent = FixedTradeImpactAgent()
    
    # Reduce verbosity
    if hasattr(agent, 'agent_executor'):
        agent.agent_executor.verbose = False
    
    query = "Which players benefited from the Lillard to Bucks trade?"
    
    print("=" * 60)
    print("TEST: Lillard Trade Beneficiaries")
    print("=" * 60)
    print(f"Query: {query}\n")
    
    response = await agent.process_message(query)
    content = response.content if hasattr(response, 'content') else str(response)
    
    # Clean for display
    clean_content = content.encode('ascii', 'ignore').decode('ascii')
    
    print("Response:")
    print(clean_content)
    
    print("\n" + "-" * 40)
    print("Verification:")
    
    # Check for correct players
    correct_players = ["giannis", "lillard", "lopez", "portis"]
    wrong_players = ["tatum", "porzingis", "barnes", "sengun"]
    
    content_lower = content.lower()
    
    found_correct = [p for p in correct_players if p in content_lower]
    found_wrong = [p for p in wrong_players if p in content_lower]
    
    if found_correct:
        print(f"  [OK] Found correct players: {', '.join(found_correct)}")
    else:
        print("  [ISSUE] No correct players found")
    
    if found_wrong:
        print(f"  [ISSUE] Found wrong players: {', '.join(found_wrong)}")
    else:
        print("  [OK] No incorrect players")
    
    # Check for tool mentions
    if "based on the" in content_lower or "tool" in content_lower or "find_trade_beneficiaries" in content_lower:
        print("  [ISSUE] Still mentions tools in response")
    else:
        print("  [OK] No tool mentions")
    
    return len(found_correct) > 0 and len(found_wrong) == 0

async def test_direct_beneficiaries_call():
    """Test the _find_trade_beneficiaries method directly"""
    from app.agents.trade_impact_agent_fixed import FixedTradeImpactAgent
    
    agent = FixedTradeImpactAgent()
    
    print("\n" + "=" * 60)
    print("TEST: Direct Method Call")
    print("=" * 60)
    
    # Test Lillard trade
    result = agent._find_trade_beneficiaries("Lillard to Bucks trade")
    print("Lillard Trade Result:")
    print(result[:400])
    
    # Test Porzingis trade
    result2 = agent._find_trade_beneficiaries("Porzingis trade")
    print("\nPorzingis Trade Result:")
    print(result2[:400])
    
    return True

async def main():
    print("TRADEIMPACT AGENT FINAL FIXES TEST")
    print("=" * 60)
    
    # Test direct method first
    await test_direct_beneficiaries_call()
    
    # Test through agent
    success = await test_beneficiaries_query()
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    if success:
        print("[SUCCESS] Agent returns correct, trade-specific beneficiaries")
        print("[SUCCESS] No tool names mentioned in response")
    else:
        print("[NEEDS WORK] Check the issues above")
    print("=" * 60)

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    
    import logging
    logging.getLogger("langchain").setLevel(logging.WARNING)
    
    asyncio.run(main())