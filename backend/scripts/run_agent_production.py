"""
Test Intelligence Agent with production database connection
"""

import asyncio
import sys
import os
import io
from pathlib import Path

# Fix Unicode
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment from root .env file
from dotenv import load_dotenv
root_dir = Path(__file__).parent.parent.parent  # Go up to sportsbrain root
env_path = root_dir / '.env'
print(f"Loading .env from: {env_path}")
load_dotenv(env_path, override=True)

# Verify environment is loaded
print(f"DATABASE_URL loaded: {'Yes' if os.getenv('DATABASE_URL') else 'No'}")
print(f"OPENAI_API_KEY loaded: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")

# Now import the agent (after env is loaded)
from app.agents.intelligence_agent_enhanced import IntelligenceAgentEnhanced

async def test_sleeper_query():
    """Test the 'Find me sleeper candidates' query"""
    
    print("\n" + "="*70)
    print("TESTING INTELLIGENCE AGENT WITH PRODUCTION DATABASE")
    print("="*70)
    
    # Initialize agent
    agent = IntelligenceAgentEnhanced()
    print("✓ Agent initialized")
    
    # Test query
    query = "Find me sleeper candidates"
    print(f"\n📝 Query: '{query}'")
    print("-"*50)
    
    try:
        response = await agent.process_message(query)
        
        print(f"\n📊 Response Metadata:")
        print(f"  - Confidence: {response.confidence}")
        print(f"  - Tools used: {response.tools_used}")
        print(f"  - Response length: {len(response.content)} characters")
        
        print(f"\n📝 Response Content:")
        print("="*50)
        print(response.content)
        print("="*50)
        
        # Validation checks
        print("\n✅ Content Validation:")
        checks = [
            ("Contains player names", any(name in response.content for name in ["Gary Trent Jr", "Henderson", "Hendricks"])),
            ("Contains sleeper scores", "0." in response.content and ("sleeper" in response.content.lower() or "score" in response.content.lower())),
            ("Contains ADP info", "ADP" in response.content or "round" in response.content.lower()),
            ("Contains projections", "PPG" in response.content or "points" in response.content.lower()),
            ("Contains shot distributions", any(x in response.content for x in ["3PT", "3-Point", "midrange", "paint", "%"])),
            ("Response > 500 chars", len(response.content) > 500),
            ("Response > 1000 chars", len(response.content) > 1000),
            ("Response > 2000 chars", len(response.content) > 2000)
        ]
        
        for check_name, result in checks:
            status = "✓" if result else "✗"
            print(f"  {status} {check_name}")
            
        # Check if response is being summarized
        if len(response.content) < 1000:
            print("\n⚠️ WARNING: Response appears to be summarized (< 1000 chars)")
            print("The agent may be condensing the tool output.")
        else:
            print("\n✅ Response appears to be detailed (> 1000 chars)")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_sleeper_query())