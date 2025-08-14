"""Test the _characterize_player function"""

import sys
import os
import json
from pprint import pprint

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.intelligence_agent_enhanced import IntelligenceAgentEnhanced

def test_characterize_player():
    """Test player characterization for key players"""
    
    agent = IntelligenceAgentEnhanced()
    
    test_players = [
        'Jordan Poole',
        'Alperen Sengun',
        'Gary Trent Jr.',
        'Jayson Tatum',
        'Giannis Antetokounmpo'
    ]
    
    print("Testing _characterize_player function:\n")
    print("=" * 80)
    
    for player_name in test_players:
        print(f"\nCharacterizing: {player_name}")
        print("-" * 40)
        
        profile = agent._characterize_player(player_name)
        
        if profile:
            print(f"Name: {profile['name']}")
            print(f"Position: {profile['position']} | Team: {profile['team']}")
            print(f"Primary Role: {profile['primary_role']}")
            print(f"ADP: Round {profile['adp_round']} (Pick {profile['adp_rank']})")
            print(f"Sleeper Score: {profile['sleeper_score']:.2f}")
            
            print("\nProjections:")
            proj = profile['projections']
            print(f"  {proj['ppg']:.1f} PPG, {proj['rpg']:.1f} RPG, {proj['apg']:.1f} APG")
            print(f"  {proj['3pm']:.1f} 3PM, Fantasy: {proj['fantasy_ppg']:.1f}")
            
            print("\nCharacteristics:")
            chars = profile['characteristics']
            print(f"  Shooter: {chars['is_shooter']} (3PA: {chars['avg_3pa']:.1f})")
            print(f"  Playmaker: {chars['is_playmaker']}")
            print(f"  High Usage: {chars['is_high_usage']} ({chars['usage_rate']:.1f}%)")
            print(f"  Sleeper: {chars['is_sleeper']}")
            print(f"  Breakout: {chars['is_breakout']}")
            
            print("\nShot Distribution:")
            shot_dist = profile['shot_distribution']
            if isinstance(shot_dist, str):
                shot_dist = json.loads(shot_dist)
            print(f"  3PT: {shot_dist.get('3PT', 0)*100:.0f}%")
            print(f"  Midrange: {shot_dist.get('midrange', 0)*100:.0f}%")
            print(f"  Paint: {shot_dist.get('paint', 0)*100:.0f}%")
        else:
            print(f"  ERROR: Could not characterize {player_name}")
    
    print("\n" + "=" * 80)
    print("Test complete!")

if __name__ == "__main__":
    test_characterize_player()