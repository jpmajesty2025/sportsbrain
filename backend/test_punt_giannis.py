"""Test the punt FT% Giannis query"""
import asyncio
from app.agents.draft_prep_agent_tools import DraftPrepAgent

async def test_punt_giannis():
    agent = DraftPrepAgent()
    
    queries = [
        "Build a punt FT% team around Giannis",
        "Build punt FT% team",
        "What's the best punt strategy for Giannis?"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 80)
        try:
            response = await asyncio.wait_for(
                agent.process_message(query),
                timeout=30.0
            )
            print(f"Response: {response.content[:500]}...")  # First 500 chars
            print(f"Success: Yes")
        except Exception as e:
            print(f"Error: {str(e)}")
            print(f"Success: No")

if __name__ == "__main__":
    asyncio.run(test_punt_giannis())