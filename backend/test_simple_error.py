"""Test the new simple error messages"""
import asyncio
from app.agents.error_messages import get_friendly_error_message

# Test the error message function directly
print("Testing Error Messages")
print("=" * 80)

# Test different scenarios
test_cases = [
    ("intelligence", "Compare all players and find sleepers", "timeout"),
    ("draft_prep", "Complete mock draft all rounds", "iteration_limit"),
    ("trade_impact", "Analyze all hypothetical trades", "timeout"),
]

for agent_type, query, error_type in test_cases:
    print(f"\nAgent: {agent_type}")
    print(f"Query: {query}")
    print(f"Error Type: {error_type}")
    print(f"Message: {get_friendly_error_message(agent_type, query, error_type)}")
    print("-" * 80)