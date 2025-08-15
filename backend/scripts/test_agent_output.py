"""
Test the Intelligence Agent output directly
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.intelligence_agent_enhanced import IntelligenceAgentEnhanced

async def test_agent_output():
    """Test the agent's actual output"""
    agent = IntelligenceAgentEnhanced()
    
    print("="*80)
    print("TESTING INTELLIGENCE AGENT OUTPUT")
    print("="*80)
    
    # Test the exact query the user used
    query = "Find me sleeper candidates"
    
    print(f"\nQuery: '{query}'")
    print("-"*60)
    
    # Test the tool directly
    print("\n1. Direct tool call (_find_sleeper_candidates_enhanced):")
    direct_result = agent._find_sleeper_candidates_enhanced("")
    print(direct_result[:1000])  # First 1000 chars
    
    print("\n" + "="*80)
    print("\n2. Through agent executor:")
    response = await agent.process_message(query)
    print(f"Response content length: {len(response.content)}")
    print(f"First 1000 chars:\n{response.content[:1000]}")

if __name__ == "__main__":
    asyncio.run(test_agent_output())