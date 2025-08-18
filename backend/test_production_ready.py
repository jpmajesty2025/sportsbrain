"""Final test to verify Enhanced TradeImpact Agent is production ready"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.agent_coordinator import AgentCoordinator


async def test_production_ready():
    """Test that Enhanced TradeImpact is production ready"""
    
    print("=" * 60)
    print("PRODUCTION READINESS TEST - Enhanced TradeImpact Agent")
    print("=" * 60)
    
    # Initialize coordinator (this is what the API uses)
    coordinator = AgentCoordinator()
    
    # Test queries
    queries = [
        "How does the Porzingis trade affect Tatum's fantasy value?",
        "What's the impact of Lillard to Milwaukee on Giannis?",
        "Analyze OG Anunoby trade impact for the Knicks"
    ]
    
    all_passed = True
    
    for i, query in enumerate(queries, 1):
        print(f"\nTest {i}: {query}")
        print("-" * 40)
        
        try:
            # Route through coordinator like the API does
            response = await coordinator.route_message(
                message=query,
                agent_type="trade_impact"
            )
            
            # Check we got a response
            if response and response.content:
                # Check for reranking indicator
                if "Enhanced with Reranking" in response.content:
                    print("[OK] Reranking active")
                else:
                    print("[OK] Response received")
                
                # Check response quality
                if len(response.content) > 100:
                    print("[OK] Substantial response")
                else:
                    print("[WARNING] Response seems short")
                    all_passed = False
                
                # Show preview
                preview = response.content[:200].replace('\n', ' ')
                print(f"[OK] Preview: {preview}...")
                
            else:
                print("[ERROR] No response received")
                all_passed = False
                
        except Exception as e:
            print(f"[ERROR] Error: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] ALL TESTS PASSED - Ready for Production!")
    else:
        print("[WARNING] Some tests failed - Review before deploying")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(test_production_ready())
    sys.exit(0 if success else 1)