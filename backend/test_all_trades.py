"""Test all trade queries"""
import asyncio
from app.agents.trade_impact_agent_tools import TradeImpactAgent

async def test_all_trades():
    agent = TradeImpactAgent()
    
    queries = [
        # General trade queries
        "What was the fantasy impact of the Porzingis trade?",
        "What was the fantasy impact of the Lillard trade?",
        
        # Specific player impact
        "How does the Porzingis trade affect Tatum?",
        "How does the Lillard trade affect Giannis?",
        
        # Hypothetical trades
        "If the Lakers trade for Trae Young, what happens to Austin Reaves?",
        "How would a hypothetical Donovan Mitchell to Miami trade affect Bam Adebayo?",
    ]
    
    for query in queries:
        print(f"\n{'='*80}")
        print(f"Query: {query}")
        print('-'*80)
        
        try:
            response = await agent.process_message(query)
            if response.content:
                # Check for errors
                if "iteration limit" in response.content.lower() or "time limit" in response.content.lower():
                    print(f"FAILED: {response.content}")
                else:
                    print(f"SUCCESS: {response.content[:200]}...")
            else:
                print("FAILED: No response content")
        except Exception as e:
            print(f"ERROR: {str(e)}")
    
    print(f"\n{'='*80}")
    print("All trade queries tested!")

if __name__ == "__main__":
    asyncio.run(test_all_trades())