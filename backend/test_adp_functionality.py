"""Test what ADP analysis actually works"""
import asyncio
from app.agents.draft_prep_agent_tools import DraftPrepAgent

async def test_adp():
    agent = DraftPrepAgent()
    
    # Test various ADP queries
    queries = [
        "Who are the best value picks in rounds 3-5?",  # Current Dashboard example
        "Show me ADP value picks",
        "Which players are undervalued?",
        "Find ADP steals",
        "What's the current ADP rankings?",
        "Show top 10 ADP",
    ]
    
    print("Testing ADP Analysis Capabilities")
    print("=" * 80)
    
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 40)
        try:
            response = await asyncio.wait_for(
                agent.process_message(query),
                timeout=30.0
            )
            # Show first 300 chars to see what kind of response we get
            preview = response.content[:300] + "..." if len(response.content) > 300 else response.content
            print(f"Response: {preview}")
            
            # Check if it contains ADP info
            if "ADP" in response.content or "Round" in response.content:
                print("✓ Contains ADP information")
            else:
                print("✗ May not contain ADP analysis")
                
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_adp())