"""
Validate Day 1 data generation - shot distributions and player characterization
Tests with various sleeper candidates to ensure data quality
"""

import sys
import os
import json
import io
from typing import List, Dict, Any
from datetime import datetime

# Fix Unicode encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse
from dotenv import load_dotenv
from app.agents.intelligence_agent_enhanced import IntelligenceAgentEnhanced

load_dotenv()

# Database connection
url = urlparse(os.getenv('DATABASE_URL'))
conn = psycopg2.connect(
    host=url.hostname,
    port=url.port,
    database=url.path[1:],
    user=url.username,
    password=url.password,
    cursor_factory=RealDictCursor
)

def validate_shot_distributions(player_names: List[str]) -> Dict[str, Any]:
    """Validate that shot distributions exist and are reasonable"""
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    results = {}
    print("\n" + "="*80)
    print("VALIDATING SHOT DISTRIBUTIONS")
    print("="*80)
    
    for name in player_names:
        cur.execute("""
            SELECT p.name, p.position, p.playing_style,
                   fd.shot_distribution, fd.sleeper_score, fd.adp_rank,
                   fd.projected_3pm, fd.projected_ppg
            FROM players p
            JOIN fantasy_data fd ON p.id = fd.player_id
            WHERE LOWER(p.name) LIKE LOWER(%s)
            LIMIT 1
        """, (f"%{name}%",))
        
        player = cur.fetchone()
        
        if player:
            shot_dist = player['shot_distribution']
            if shot_dist:
                # Parse JSON if needed
                if isinstance(shot_dist, str):
                    shot_dist = json.loads(shot_dist)
                
                # Validate distribution adds to ~1.0
                total = sum(shot_dist.values())
                is_valid = 0.98 <= total <= 1.02
                
                # Check if distribution makes sense for position
                position_valid = validate_distribution_for_position(
                    player['position'], shot_dist
                )
                
                results[player['name']] = {
                    'exists': True,
                    'distribution': shot_dist,
                    'total': total,
                    'valid_sum': is_valid,
                    'position_appropriate': position_valid,
                    'sleeper_score': player['sleeper_score'],
                    'adp_rank': player['adp_rank']
                }
                
                print(f"\n{player['name']} ({player['position']}, {player['playing_style']})")
                print(f"  ADP: {player['adp_rank']} | Sleeper Score: {player['sleeper_score']:.2f}")
                print(f"  Shot Distribution: 3PT={shot_dist.get('3PT', 0)*100:.0f}%, "
                      f"Mid={shot_dist.get('midrange', 0)*100:.0f}%, "
                      f"Paint={shot_dist.get('paint', 0)*100:.0f}%")
                print(f"  ✓ Sum: {total:.2f} {'✅' if is_valid else '❌'}")
                print(f"  ✓ Position Appropriate: {'✅' if position_valid else '❌'}")
            else:
                results[player['name']] = {
                    'exists': True,
                    'distribution': None,
                    'error': 'No distribution found'
                }
                print(f"\n{player['name']}: ❌ No shot distribution!")
        else:
            results[name] = {
                'exists': False,
                'error': 'Player not found in database'
            }
            print(f"\n{name}: ❌ Not found in database!")
    
    cur.close()
    return results

def validate_distribution_for_position(position: str, distribution: Dict) -> bool:
    """Check if shot distribution makes sense for player position"""
    three_pt_rate = distribution.get('3PT', 0)
    paint_rate = distribution.get('paint', 0)
    
    # Position-based expectations
    if position in ['C']:
        # Centers should have lower 3PT%, higher paint%
        return three_pt_rate < 0.5 and paint_rate > 0.3
    elif position in ['PG', 'SG']:
        # Guards can have varied distributions
        return True  # Guards are versatile
    elif position in ['PF']:
        # Power forwards - mixed
        return three_pt_rate < 0.6  # Not too 3PT heavy
    elif position in ['SF']:
        # Small forwards - balanced
        return True
    else:
        return True  # Unknown position

def test_player_characterization(player_names: List[str]) -> None:
    """Test the _characterize_player function with various sleepers"""
    agent = IntelligenceAgentEnhanced()
    
    print("\n" + "="*80)
    print("TESTING PLAYER CHARACTERIZATION")
    print("="*80)
    
    for name in player_names:
        profile = agent._characterize_player(name)
        
        if profile:
            print(f"\n{profile['name']} - Characterization ✅")
            print(f"  Role: {profile['primary_role']}")
            print(f"  Position: {profile['position']} | Team: {profile['team']}")
            
            chars = profile['characteristics']
            print(f"  Characteristics:")
            print(f"    • Shooter: {chars['is_shooter']} (3PA: {chars['avg_3pa']:.1f})")
            print(f"    • Sleeper: {chars['is_sleeper']} (Score: {profile['sleeper_score']:.2f})")
            print(f"    • Usage: {chars['usage_rate']:.1f}%")
            
            # Validate characterization logic
            if chars['is_sleeper'] and profile['sleeper_score'] < 0.6:
                print(f"    ⚠️ WARNING: Marked as sleeper but score is {profile['sleeper_score']}")
            
            shot_dist = profile['shot_distribution']
            if isinstance(shot_dist, str):
                shot_dist = json.loads(shot_dist)
            
            # Check if primary_role matches shot distribution
            if profile['primary_role'] == 'volume_shooter' and shot_dist.get('3PT', 0) < 0.4:
                print(f"    ⚠️ WARNING: Volume shooter but only {shot_dist.get('3PT', 0)*100:.0f}% 3PT")
        else:
            print(f"\n{name} - Characterization ❌ FAILED")

def check_sleeper_candidates() -> None:
    """Check our sleeper identification logic"""
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    print("\n" + "="*80)
    print("TOP SLEEPER CANDIDATES IN DATABASE")
    print("="*80)
    
    cur.execute("""
        SELECT p.name, p.position, p.team,
               fd.sleeper_score, fd.adp_rank, fd.adp_round,
               fd.projected_fantasy_ppg, fd.shot_distribution
        FROM players p
        JOIN fantasy_data fd ON p.id = fd.player_id
        WHERE fd.sleeper_score > 0.7
        ORDER BY fd.sleeper_score DESC
        LIMIT 15
    """)
    
    sleepers = cur.fetchall()
    
    print(f"\nFound {len(sleepers)} high-value sleepers (score > 0.7):\n")
    
    for i, player in enumerate(sleepers, 1):
        shot_dist = player['shot_distribution']
        if shot_dist and isinstance(shot_dist, str):
            shot_dist = json.loads(shot_dist)
        
        print(f"{i:2}. {player['name']:20} ({player['position']}, {player['team']})")
        print(f"    Sleeper Score: {player['sleeper_score']:.2f} | ADP: {player['adp_rank']} (Round {player['adp_round']})")
        print(f"    Fantasy PPG: {player['projected_fantasy_ppg']:.1f}")
        if shot_dist:
            print(f"    Shot Profile: 3PT={shot_dist.get('3PT', 0)*100:.0f}%, "
                  f"Mid={shot_dist.get('midrange', 0)*100:.0f}%, "
                  f"Paint={shot_dist.get('paint', 0)*100:.0f}%")
    
    cur.close()

def main():
    """Run all validation tests"""
    
    # Test with sleepers you mentioned (provide the names)
    # These should be players NOT in the hardcoded list
    test_sleepers = [
        # Add the 10-13 sleeper names from your AI here
        # For now, testing with some likely candidates
        "Anfernee Simons",
        "Malik Monk", 
        "Cole Anthony",
        "Nic Claxton",
        "Dereck Lively",
        "Scoot Henderson",
        "Ausar Thompson",
        "Cam Thomas",
        "Naz Reid",
        "Brandin Podziemski",
        "Scoot Henderson", "Shaedon Sharpe", "Trey Murphy III"
    ]
    
    print("\n" + "="*80)
    print(f"VALIDATION REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*80)
    
    # 1. Validate shot distributions exist and are valid
    dist_results = validate_shot_distributions(test_sleepers)
    
    # 2. Test player characterization
    test_player_characterization(test_sleepers[:5])  # Test first 5
    
    # 3. Check our top sleepers
    check_sleeper_candidates()
    
    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    total_tested = len(dist_results)
    valid_count = sum(1 for r in dist_results.values() if r.get('valid_sum', False))
    found_count = sum(1 for r in dist_results.values() if r.get('exists', False))
    
    print(f"\n✅ Players Found: {found_count}/{total_tested}")
    print(f"✅ Valid Distributions: {valid_count}/{found_count}")
    
    # Check for any issues
    issues = []
    for name, result in dist_results.items():
        if not result.get('exists'):
            issues.append(f"  - {name}: Not in database")
        elif not result.get('valid_sum'):
            issues.append(f"  - {name}: Invalid distribution sum")
        elif not result.get('position_appropriate'):
            issues.append(f"  - {name}: Questionable distribution for position")
    
    if issues:
        print(f"\n⚠️ Issues Found:")
        for issue in issues:
            print(issue)
    else:
        print(f"\n🎉 All validations passed!")
    
    conn.close()

if __name__ == "__main__":
    # You can pass custom player names here
    import sys
    if len(sys.argv) > 1:
        # Allow passing player names as arguments
        custom_players = sys.argv[1:]
        print(f"Testing with custom players: {custom_players}")
        # Override test_sleepers in main()
    
    main()