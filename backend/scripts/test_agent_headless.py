"""
Headless testing of Intelligence Agent with production database
"""

import asyncio
import sys
import os
import io
from datetime import datetime

# Fix Unicode encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment variables if needed
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')

from app.agents.intelligence_agent_enhanced import IntelligenceAgentEnhanced
from app.agents.agent_coordinator import AgentCoordinator

async def test_intelligence_agent():
    """Test the Intelligence Agent directly"""
    print("="*80)
    print("TESTING INTELLIGENCE AGENT (HEADLESS)")
    print(f"Timestamp: {datetime.now()}")
    print("="*80)
    
    # Initialize the agent
    try:
        agent = IntelligenceAgentEnhanced()
        print("✓ Agent initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize agent: {e}")
        return
    
    # Test queries
    test_queries = [
        "Find me sleeper candidates",
        "Who are the top breakout candidates?",
        "Analyze Scoot Henderson's stats",
        "Find players like Gary Trent Jr",
        "Compare LeBron James vs Kevin Durant"
    ]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"QUERY: '{query}'")
        print("-"*80)
        
        try:
            # Test the agent
            response = await agent.process_message(query)
            
            print(f"\n📊 Response Metadata:")
            print(f"  - Confidence: {response.confidence}")
            print(f"  - Tools used: {response.tools_used}")
            print(f"  - Method: {response.metadata.get('method', 'agent_executor')}")
            
            print(f"\n📝 Response Content (length: {len(response.content)} chars):")
            print("-"*40)
            
            # Show first 2000 characters to see if we're getting detailed output
            if len(response.content) > 2000:
                print(response.content[:2000])
                print(f"\n... [{len(response.content) - 2000} more characters] ...")
            else:
                print(response.content)
                
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*80}")
    print("TEST COMPLETE")
    print("="*80)

async def test_through_coordinator():
    """Test through the agent coordinator (simulates production routing)"""
    print("\n\n")
    print("="*80)
    print("TESTING THROUGH AGENT COORDINATOR")
    print("="*80)
    
    coordinator = AgentCoordinator()
    
    query = "Find me sleeper candidates"
    print(f"\nQuery: '{query}'")
    print("-"*40)
    
    try:
        # Route to appropriate agent
        agent = coordinator.route_to_agent(query)
        print(f"Routed to: {agent.name}")
        
        # Process message
        response = await agent.process_message(query)
        
        print(f"\n📊 Response via Coordinator:")
        print(f"  - Length: {len(response.content)} chars")
        print(f"  - First 1000 chars:")
        print("-"*40)
        print(response.content[:1000])
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run all tests"""
    
    # Check if we have OpenAI key
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️ WARNING: OPENAI_API_KEY not set. Agent may not work properly.")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        print()
    
    # Test direct agent
    await test_intelligence_agent()
    
    # Test through coordinator
    await test_through_coordinator()

if __name__ == "__main__":
    asyncio.run(main())