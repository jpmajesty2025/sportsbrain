"""Test one query in detail"""

import os
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

if not os.getenv("OPENAI_API_KEY"):
    from dotenv import load_dotenv
    load_dotenv()

async def test_single_query():
    from app.agents.trade_impact_agent_fixed import FixedTradeImpactAgent
    
    agent = FixedTradeImpactAgent()
    
    # Enable verbose to see what's happening
    if hasattr(agent, 'agent_executor'):
        agent.agent_executor.verbose = True
    
    query = "How does Porzingis trade affect Tatum?"
    
    print("Testing:", query)
    print("=" * 60)
    
    response = await agent.process_message(query)
    content = response.content if hasattr(response, 'content') else str(response)
    
    print("\n" + "=" * 60)
    print("FINAL RESPONSE:")
    print("=" * 60)
    # Clean unicode for Windows
    clean_content = content.encode('ascii', 'ignore').decode('ascii')
    print(clean_content)
    
    print("\n" + "=" * 60)
    if "Agent stopped" not in content and "timeout" not in content.lower():
        print("[SUCCESS] Query completed without timeout!")
    else:
        print("[PROBLEM] Still has issues")

if __name__ == "__main__":
    asyncio.run(test_single_query())