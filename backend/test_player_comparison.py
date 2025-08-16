"""Test player comparison functionality"""
import asyncio
from app.agents.intelligence_agent_enhanced import IntelligenceAgentEnhanced

async def test_player_comparison():
    agent = IntelligenceAgentEnhanced()
    
    queries = [
        "Compare Scottie Barnes vs Paolo Banchero",
        "Who is better: Barnes or Banchero?",
        "Compare Barnes and Banchero"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 80)
        try:
            response = await asyncio.wait_for(
                agent.process_message(query),
                timeout=30.0
            )
            print(f"Response length: {len(response.content)} chars")
            print(f"Response:\n{response.content}")
            
            # Check for quality indicators
            if "vs" in response.content or "ADP" in response.content or "Stats" in response.content:
                print("\n✓ Contains comparison details")
            else:
                print("\n✗ Missing comparison details - may be truncated")
                
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_player_comparison())