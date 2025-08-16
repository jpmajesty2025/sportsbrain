"""Test the mock draft functionality"""
import asyncio
from app.agents.draft_prep_agent_tools import DraftPrepAgent

async def test_mock_draft():
    agent = DraftPrepAgent()
    
    queries = [
        "Show mock draft for pick 12",
        "Mock draft for pick 1",
        "Best available at pick 24",
        "Who should I draft with pick 8?"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 80)
        try:
            response = await asyncio.wait_for(
                agent.process_message(query),
                timeout=30.0
            )
            print(f"Response preview: {response.content[:600]}...")
            if "Trae Young is the best available" in response.content:
                print("WARNING: Got oversimplified response!")
            else:
                print("Success: Detailed mock draft provided")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_mock_draft())