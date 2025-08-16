"""Test the fixed Intelligence Agent errors"""
import asyncio
from app.agents.intelligence_agent_enhanced import IntelligenceAgentEnhanced

async def test_fixes():
    print("Testing fixed Intelligence Agent errors...\n")
    
    agent = IntelligenceAgentEnhanced()
    
    # Test the two previously failing queries
    queries = [
        "What are Scoot Henderson's stats?",
        "Is Paolo Banchero a breakout candidate?"
    ]
    
    for query in queries:
        print(f"\nTesting: {query}")
        print("-" * 50)
        
        try:
            response = await agent.process_message(query)
            if response.content:
                if "error" in response.content.lower() and "iteration" not in response.content.lower():
                    print(f"ERROR: {response.content[:300]}")
                elif "iteration limit" in response.content.lower() or "time limit" in response.content.lower():
                    print(f"ITERATION LIMIT HIT - Still failing")
                else:
                    print(f"SUCCESS: {response.content[:300]}...")
            else:
                print("No response")
        except Exception as e:
            print(f"EXCEPTION: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_fixes())