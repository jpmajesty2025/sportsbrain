"""Test keeper value responses"""
import asyncio
from app.agents.draft_prep_agent_tools import DraftPrepAgent

async def test_keeper_value():
    agent = DraftPrepAgent()
    
    queries = [
        "Should I keep Ja Morant in round 3?",
        "Is LaMelo Ball worth keeping in round 4?"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 80)
        try:
            response = await asyncio.wait_for(
                agent.process_message(query),
                timeout=30.0
            )
            print(f"Response:\n{response.content}")
            
            # Check for quality indicators
            if "based on the analysis" in response.content.lower() or "tool" in response.content.lower():
                print("\n✗ ERROR: Still mentions tools!")
            elif "ADP" in response.content and ("VALUE" in response.content or "recommend" in response.content.lower()):
                print("\n✓ Good: Contains detailed keeper analysis")
            else:
                print("\n✗ Warning: May be too brief")
                
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_keeper_value())