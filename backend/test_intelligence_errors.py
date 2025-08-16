"""Debug Intelligence Agent errors"""
import asyncio
import logging
from app.agents.intelligence_agent_enhanced import IntelligenceAgentEnhanced

# Enable verbose logging
logging.basicConfig(level=logging.DEBUG)

async def test_errors():
    print("Testing Intelligence Agent errors...\n")
    
    agent = IntelligenceAgentEnhanced()
    
    # Test the two failing queries
    queries = [
        "What are Scoot Henderson's stats?",
        "Is Paolo Banchero a breakout candidate?"
    ]
    
    for query in queries:
        print(f"\nTesting: {query}")
        print("-" * 50)
        
        # Test the tools directly first
        if "stats" in query.lower():
            print("\nDirect tool test - analyze_player_stats:")
            try:
                result = agent._analyze_player_stats_enhanced("Scoot Henderson")
                print(f"Result: {result[:200]}...")
            except Exception as e:
                print(f"Error: {e}")
        
        if "breakout" in query.lower():
            print("\nDirect tool test - identify_breakout_candidates:")
            try:
                result = agent._identify_breakout_candidates_enhanced("Paolo Banchero")
                print(f"Result: {result[:200]}...")
            except Exception as e:
                print(f"Error: {e}")
        
        # Now test through the agent
        print(f"\nAgent test:")
        try:
            response = await agent.process_message(query)
            print(f"Response: {response.content[:500] if response.content else 'No content'}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_errors())