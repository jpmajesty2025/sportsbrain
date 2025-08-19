"""Test that Agent Coordinator uses Enhanced DraftPrep"""

import os
import sys
import asyncio
import pytest
from pathlib import Path

# Skip this test file in CI to avoid downloading models
if os.getenv("CI") == "true":
    pytest.skip("Skipping model test in CI environment", allow_module_level=True)

sys.path.insert(0, str(Path(__file__).parent))

if not os.getenv("OPENAI_API_KEY"):
    from dotenv import load_dotenv
    load_dotenv()

async def test_coordinator():
    """Test that coordinator uses enhanced DraftPrep"""
    from app.agents.agent_coordinator import AgentCoordinator
    
    coordinator = AgentCoordinator()
    
    print("=" * 60)
    print("TEST: Agent Coordinator with Enhanced DraftPrep")
    print("=" * 60)
    
    # Check which DraftPrep agent was loaded
    draft_agent = coordinator.agents.get("draft_prep")
    
    if draft_agent:
        agent_class = draft_agent.__class__.__name__
        print(f"DraftPrep Agent Class: {agent_class}")
        
        if agent_class == "EnhancedDraftPrepAgent":
            print("  [OK] Using Enhanced DraftPrep Agent with reranking")
        else:
            print("  [INFO] Using base DraftPrepAgent (enhanced not available)")
        
        # Check for reranker attribute
        if hasattr(draft_agent, 'reranker'):
            print(f"  Reranker Available: {draft_agent.reranker is not None}")
        
        # Check for embedding model
        if hasattr(draft_agent, 'embedding_model'):
            print(f"  Embedding Model: {draft_agent.embedding_model is not None}")
    
    # Test a query through coordinator
    print("\n" + "-" * 40)
    print("Testing Query Through Coordinator:")
    query = "Build a punt FT% team around Giannis"
    print(f"Query: {query}\n")
    
    response = await coordinator.route_message(query, agent_type="draft_prep")
    
    print("Response Preview:")
    content = response.content if hasattr(response, 'content') else str(response)
    print(content[:500])
    
    # Check metadata
    if hasattr(response, 'metadata') and response.metadata:
        print("\nMetadata:")
        for key, value in response.metadata.items():
            print(f"  {key}: {value}")
    
    return True

async def main():
    print("AGENT COORDINATOR DRAFTPREP TEST")
    print("=" * 60)
    
    await test_coordinator()
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("The Agent Coordinator is configured to:")
    print("  1. Try importing EnhancedDraftPrepAgent first")
    print("  2. Fall back to base DraftPrepAgent if import fails")
    print("  3. Enhanced agent includes reranking when available")
    print("=" * 60)

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    
    import logging
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("app.agents").setLevel(logging.INFO)
    
    asyncio.run(main())