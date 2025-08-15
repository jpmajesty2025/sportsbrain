"""
Test agent with mocked database responses to simulate production behavior
"""

import asyncio
import sys
import os
from unittest.mock import Mock, patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock the database response
mock_sleepers_data = [
    Mock(
        name="Gary Trent Jr.",
        position="SG",
        team="MIL",
        age=25,
        adp_rank=140,
        adp_round=12,
        sleeper_score=0.90,
        projected_fantasy_ppg=21.2,
        consistency_rating=0.75,
        injury_risk="Low",
        projected_ppg=14.5,
        projected_rpg=3.2,
        projected_apg=1.8,
        shot_distribution='{"3PT": 0.52, "midrange": 0.18, "paint": 0.30}',
        sleeper_reason="Late-round value"
    ),
    Mock(
        name="Taylor Hendricks",
        position="PF",
        team="UTA",
        age=20,
        adp_rank=126,
        adp_round=11,
        sleeper_score=0.88,
        projected_fantasy_ppg=21.4,
        consistency_rating=0.68,
        injury_risk="Low",
        projected_ppg=13.8,
        projected_rpg=6.2,
        projected_apg=1.5,
        shot_distribution='{"3PT": 0.64, "midrange": 0.13, "paint": 0.23}',
        sleeper_reason="Young player development"
    ),
    Mock(
        name="Scoot Henderson",
        position="PG",
        team="POR",
        age=20,
        adp_rank=121,
        adp_round=11,
        sleeper_score=0.87,
        projected_fantasy_ppg=19.2,
        consistency_rating=0.65,
        injury_risk="Medium",
        projected_ppg=15.2,
        projected_rpg=4.1,
        projected_apg=5.8,
        shot_distribution='{"3PT": 0.65, "midrange": 0.16, "paint": 0.19}',
        sleeper_reason="Young player development"
    )
]

@patch('app.db.database.get_db')
async def test_with_mock_data(mock_get_db):
    """Test agent with mocked database"""
    
    # Setup mock database
    mock_db = Mock()
    mock_result = Mock()
    mock_result.fetchall.return_value = mock_sleepers_data
    mock_db.execute.return_value = mock_result
    mock_get_db.return_value = iter([mock_db])
    
    from app.agents.intelligence_agent_enhanced import IntelligenceAgentEnhanced
    
    agent = IntelligenceAgentEnhanced()
    
    print("="*70)
    print("TESTING AGENT WITH MOCK DATA")
    print("="*70)
    
    print("\nQuery: 'Find me sleeper candidates'")
    print("-"*50)
    
    response = await agent.process_message("Find me sleeper candidates")
    
    print(f"\n📊 Response Info:")
    print(f"  - Length: {len(response.content)} characters")
    print(f"  - Confidence: {response.confidence}")
    
    print(f"\n📝 Full Response:")
    print("="*50)
    print(response.content)
    print("="*50)
    
    # Check if response contains expected elements
    print("\n✅ Validation Checks:")
    checks = [
        ("Contains 'Gary Trent Jr.'", "Gary Trent Jr." in response.content),
        ("Contains sleeper scores", "0.90" in response.content or "0.87" in response.content),
        ("Contains ADP info", "ADP" in response.content or "140" in response.content),
        ("Contains shot distributions", "3PT" in response.content or "52%" in response.content),
        ("Response > 500 chars", len(response.content) > 500),
        ("Response > 1000 chars", len(response.content) > 1000),
        ("Response > 2000 chars", len(response.content) > 2000)
    ]
    
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"  {status} {check_name}")

if __name__ == "__main__":
    asyncio.run(test_with_mock_data())