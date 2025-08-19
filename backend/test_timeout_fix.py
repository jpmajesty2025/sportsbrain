"""Test that TradeImpact agent doesn't timeout on demo queries"""

import os
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

if not os.getenv("OPENAI_API_KEY"):
    from dotenv import load_dotenv
    load_dotenv()

async def test_demo_queries():
    """Test the key demo queries that were timing out"""
    from app.agents.trade_impact_agent_fixed import FixedTradeImpactAgent
    
    agent = FixedTradeImpactAgent()
    
    # Reduce verbosity for cleaner output
    if hasattr(agent, 'agent_executor'):
        agent.agent_executor.verbose = False
    
    test_queries = [
        "How does Porzingis trade affect Tatum?",
        "Which players benefited from the Lillard to Bucks trade?",
        "How did Lillard trade affect Giannis usage rate?"
    ]
    
    print("=" * 60)
    print("TESTING TRADEIMPACT AGENT TIMEOUT FIXES")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n[TEST] {query}")
        print("-" * 40)
        
        try:
            response = await agent.process_message(query)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Check for timeout message
            if "Agent stopped due to iteration limit" in content:
                print("[FAIL] Still hitting iteration limit!")
            elif "timeout" in content.lower() and "error" in str(response.metadata if hasattr(response, 'metadata') else {}):
                print("[FAIL] Hit timeout!")
            else:
                print("[PASS] Got proper response")
                print(f"Response preview: {content[:200]}...")
                
        except Exception as e:
            print(f"[ERROR] {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    
    # Suppress verbose logging
    import logging
    logging.getLogger("app").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)
    
    asyncio.run(test_demo_queries())