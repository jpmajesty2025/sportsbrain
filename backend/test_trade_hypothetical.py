"""Test TradeImpact Agent with hypothetical trades"""
import asyncio
from app.agents.trade_impact_agent_tools import TradeImpactAgent

async def test_hypothetical_trades():
    print("Testing TradeImpact Agent with hypothetical trades...\n")
    
    agent = TradeImpactAgent()
    
    # Test queries including the failing one from production
    queries = [
        "How would a hypothetical Donovan Mitchell to Miami trade affect Bam Adebayo?",
        "What if LeBron was traded to Boston? Impact on Tatum?",
        "How does the Porzingis trade affect Tatum?",  # Real trade for comparison
        "Hypothetical Butler to Lakers trade impact"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 80)
        try:
            response = await agent.process_message(query)
            if response.content:
                # Show first 500 chars to see if it's working
                print(f"Response preview: {response.content[:500]}...")
                print(f"Full response length: {len(response.content)} characters")
                print(f"Confidence: {response.confidence}")
            else:
                print("No response content")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_hypothetical_trades())