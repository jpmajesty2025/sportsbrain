"""Test DraftPrep tools directly"""
from app.agents.draft_prep_agent_tools import DraftPrepAgent

agent = DraftPrepAgent()

print("Testing simulate_draft_pick directly:")
print("-" * 50)
result = agent._simulate_draft_pick("pick 12")
print(f"Length of result: {len(result)} characters")
print(f"First 500 chars: {result[:500]}...")
print(f"Last 500 chars: ...{result[-500:]}")

print("\n\nTesting build_punt_strategy directly:")
print("-" * 50)
result2 = agent._build_punt_strategy("punt FT%")
print(f"Length of result: {len(result2)} characters")
print(f"First 500 chars: {result2[:500]}...")