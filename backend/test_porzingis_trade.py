"""Test Porzingis trade query"""
import asyncio
from app.agents.trade_impact_agent_tools import TradeImpactAgent

async def test_porzingis():
    agent = TradeImpactAgent()
    
    queries = [
        "What was the fantasy impact of the Porzingis trade?",
        "How does the Porzingis trade affect Tatum?",
        "Porzingis trade impact"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 80)
        
        # Test the tool directly first
        print("Direct _analyze_trade_impact call:")
        result = agent._analyze_trade_impact(query)
        print(f"Result preview: {result[:500]}...")
        
        print("\nThrough agent:")
        response = await agent.process_message(query)
        print(f"Response: {response.content[:500] if response.content else 'No content'}...")

if __name__ == "__main__":
    asyncio.run(test_porzingis())