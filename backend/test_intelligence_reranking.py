"""Test script to verify Intelligence Agent reranking functionality"""
import asyncio
import logging
import sys
import os
from dotenv import load_dotenv

# Set up logging to see reranking activity
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.intelligence_agent_enhanced_with_reranking import IntelligenceAgentWithReranking


def test_direct_reranking():
    """Test reranking directly without going through LangChain"""
    
    print("=" * 60)
    print("DIRECT TEST OF RERANKING IN INTELLIGENCE AGENT")
    print("=" * 60)
    
    # Initialize enhanced agent
    agent = IntelligenceAgentWithReranking()
    
    # Check reranker status
    print(f"\n1. Reranker Status:")
    print(f"   - Reranker initialized: {agent.reranker is not None}")
    if agent.reranker:
        print(f"   - Model loaded: {agent.reranker.model_loaded}")
    
    # Test queries that should trigger reranking
    test_queries = [
        ("Find sleepers like Sengun", "_find_sleeper_candidates_enhanced"),
        ("Analyze Paolo Banchero's stats", "_analyze_player_stats_enhanced"),
        ("Compare Barnes vs Banchero", "_compare_players_enhanced")
    ]
    
    print(f"\n2. Testing Intelligence Agent Methods:")
    print("-" * 40)
    
    for query, method_name in test_queries:
        print(f"\nQuery: {query}")
        print(f"Method: {method_name}")
        
        try:
            # Get the method
            method = getattr(agent, method_name)
            
            # Call the method with appropriate arguments
            if method_name == "_find_sleeper_candidates_enhanced":
                result = method(query)
            elif method_name == "_analyze_player_stats_enhanced":
                result = method("Paolo Banchero")
            elif method_name == "_compare_players_enhanced":
                result = method("Barnes vs Banchero")
            else:
                result = method(query)
            
            # Check if reranking was mentioned or enhanced
            if "Enhanced with Reranking" in result or "AI-Enhanced" in result:
                print("   [OK] Reranking was applied!")
            else:
                print("   [INFO] Check logs for reranking activity")
            
            # Show result preview
            print(f"   Result preview (first 200 chars):")
            print(f"   {result[:200]}...")
            
        except Exception as e:
            print(f"   [ERROR] Query failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


async def test_through_coordinator():
    """Test Intelligence Agent through the coordinator"""
    
    print("\n" + "=" * 60)
    print("TESTING INTELLIGENCE AGENT THROUGH COORDINATOR")
    print("=" * 60)
    
    from app.agents.agent_coordinator import AgentCoordinator
    
    # Initialize coordinator
    coordinator = AgentCoordinator()
    
    # Verify we have the enhanced agent
    intel_agent = coordinator.agents.get("intelligence")
    print(f"\n1. Agent Type: {type(intel_agent).__name__}")
    
    # Check if it's the enhanced version
    if hasattr(intel_agent, 'reranker'):
        print("   [OK] Enhanced agent detected (has reranker attribute)")
        if intel_agent.reranker and hasattr(intel_agent.reranker, 'model_loaded'):
            if intel_agent.reranker.model_loaded:
                print("   [OK] Reranker model loaded successfully")
            else:
                print("   [WARNING] Reranker model not loaded")
        else:
            print("   [WARNING] Reranker not initialized")
    else:
        print("   [ERROR] Not using enhanced agent!")
        return False
    
    # Test queries
    test_queries = [
        "Find me sleepers like last year's Sengun",
        "Analyze Paolo Banchero's performance",
        "Compare Scottie Barnes vs Paolo Banchero"
    ]
    
    print("\n2. Testing Intelligence Queries:")
    print("-" * 40)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        
        try:
            # Process through coordinator
            response = await coordinator.route_message(
                message=query,
                agent_type="intelligence"
            )
            
            # Check response
            if response and response.content:
                # Look for signs of reranking
                if "Enhanced" in response.content or "AI-Enhanced" in response.content:
                    print("   [OK] Reranking mentioned in response")
                else:
                    print("   [INFO] Response received (check logs for reranking)")
                
                # Show first 200 chars
                print(f"   Response preview: {response.content[:200]}...")
            else:
                print("   [WARNING] Empty response")
                
        except Exception as e:
            print(f"   [ERROR] Query failed: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("Check the logs above for 'Applying reranking' messages")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    # Test direct reranking first
    test_direct_reranking()
    
    # Then test through coordinator
    success = asyncio.run(test_through_coordinator())
    sys.exit(0 if success else 1)