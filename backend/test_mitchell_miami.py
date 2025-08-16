"""Debug Mitchell to Miami query"""
import asyncio
from app.agents.trade_impact_agent_tools import TradeImpactAgent

async def test_mitchell_miami():
    agent = TradeImpactAgent()
    
    query = "How would a hypothetical Donovan Mitchell to Miami trade affect Bam Adebayo?"
    
    print("Testing detection logic:")
    print("-" * 80)
    
    # Check what the detection logic sees
    query_lower = query.lower()
    is_hypothetical = any(word in query_lower for word in ["hypothetical", "would", "if", "potential", "possible", "what if"])
    print(f"is_hypothetical: {is_hypothetical}")
    
    has_known_trade = any(trade in query_lower for trade in ["porzingis", "lillard", "towns", "og", "anunoby"])
    print(f"has_known_trade: {has_known_trade}")
    
    mentions_miami = "miami" in query_lower or "heat" in query_lower
    mentions_mitchell = "mitchell" in query_lower or "donovan" in query_lower
    mentions_trae = "trae" in query_lower or ("young" in query_lower and "trae" in query_lower)
    
    is_unknown_trade = (mentions_mitchell and mentions_miami)
    print(f"is_unknown_trade (Mitchell + Miami): {is_unknown_trade}")
    
    should_use_hypothetical = (is_hypothetical or is_unknown_trade) and not has_known_trade
    print(f"Should use hypothetical analysis: {should_use_hypothetical}")
    
    print("\nDirect tool test:")
    print("-" * 80)
    # Test the tool directly
    result = agent._analyze_trade_impact(query)
    print(f"Direct result preview: {result[:500]}...")
    
    print("\nAgent test with verbose:")
    print("-" * 80)
    # Test through agent with shorter timeout to see what happens
    import asyncio
    try:
        response = await asyncio.wait_for(
            agent.process_message(query),
            timeout=10.0  # 10 second timeout to see what happens
        )
        print(f"Agent response: {response.content[:500] if response.content else 'None'}")
    except asyncio.TimeoutError:
        print("Agent timed out after 10 seconds")

if __name__ == "__main__":
    asyncio.run(test_mitchell_miami())