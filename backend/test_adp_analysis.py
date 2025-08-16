"""Test ADP analysis capabilities"""
import asyncio
from app.agents.draft_prep_agent_tools import DraftPrepAgent

async def test_adp_analysis():
    agent = DraftPrepAgent()
    
    # Realistic ADP analysis queries
    queries = [
        "Who are the best ADP value picks?",
        "Which players are undervalued by ADP?",
        "Show me players falling in drafts",
        "What are the top ADP steals?",
        "Which players should I avoid as reaches?",
        "What's Trae Young's ADP?",
        "Show current ADP rankings"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 80)
        try:
            response = await asyncio.wait_for(
                agent.process_message(query),
                timeout=30.0
            )
            # Print first 500 chars to see if we get meaningful responses
            print(f"Response preview: {response.content[:500]}...")
            
            # Check for quality indicators
            if "ADP" in response.content or "Round" in response.content or "value" in response.content.lower():
                print("✓ Contains ADP analysis")
            else:
                print("✗ May not contain proper ADP analysis")
                
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_adp_analysis())