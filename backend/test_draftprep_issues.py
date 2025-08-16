"""Test DraftPrep Agent issues"""
import asyncio
from app.agents.draft_prep_agent_tools import DraftPrepAgent

async def test_queries():
    print("Testing DraftPrep Agent issues...\n")
    
    agent = DraftPrepAgent()
    
    queries = [
        "Is LaMelo Ball worth keeping in round 4?",
        "What's LaMelo Ball's ADP?",
        "Build me a complete draft strategy for pick 12",
        "Can you help me find a job?"
    ]
    
    for query in queries:
        print(f"\nTesting: {query}")
        print("-" * 50)
        try:
            response = await agent.process_message(query)
            if response.content:
                print(f"Response: {response.content[:300]}...")
            else:
                print("No response")
        except Exception as e:
            print(f"Exception: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_queries())