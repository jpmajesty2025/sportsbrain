"""Test specific Trae Young to Lakers query"""
import asyncio
from app.agents.trade_impact_agent_tools import TradeImpactAgent

async def test_trae_reaves():
    agent = TradeImpactAgent()
    
    # Test the tool directly first
    print("Testing _analyze_hypothetical_trade directly:")
    print("-" * 80)
    result = agent._analyze_hypothetical_trade("If the Lakers trade for Trae Young, what happens to Austin Reaves?")
    print(result[:1000])  # First 1000 chars
    
    print("\n\nTesting through agent:")
    print("-" * 80)
    query = "If the Lakers trade for Trae Young, what happens to Austin Reaves?"
    response = await agent.process_message(query)
    print(f"Response:\n{response.content}")

if __name__ == "__main__":
    asyncio.run(test_trae_reaves())