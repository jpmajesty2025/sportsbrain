"""
Test the TradeImpact agent
"""
import sys
import os
import io
import pytest

# Set UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Skip these tests in CI as they require Milvus/Neo4j services
pytestmark = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="Skipping in CI - requires Milvus and Neo4j services"
)

import asyncio
from app.agents.agent_coordinator import AgentCoordinator


async def test_trade_agent():
    """Test the TradeImpact agent with various queries"""
    coordinator = AgentCoordinator()
    
    # Test queries - including the key demo scenario
    queries = [
        "How does Porzingis trade affect Tatum?",
        "Who are the trade winners from recent deals?",
        "How does the Lillard trade impact Giannis?",
        "What are the team dynamics after the Celtics trade?"
    ]
    
    print("Testing TradeImpact Agent")
    print("=" * 60)
    
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 60)
        
        try:
            response = await coordinator.route_message(query)
            print(f"Agent: {response.metadata.get('agent', 'Unknown') if response.metadata else 'Unknown'}")
            print(f"Confidence: {response.confidence}")
            print(f"\nResponse:\n{response.content}")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Show agent capabilities
    print("\n" + "=" * 60)
    print("Agent Capabilities:")
    capabilities = coordinator.get_agent_capabilities()
    for agent_name, caps in capabilities.items():
        print(f"\n{agent_name}: {caps['description']}")
        print(f"Supported tasks: {caps['supported_tasks']}")


if __name__ == "__main__":
    asyncio.run(test_trade_agent())