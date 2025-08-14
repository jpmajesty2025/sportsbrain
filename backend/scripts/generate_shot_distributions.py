"""
Generate shot distribution data for all players
This script analyzes existing game_stats and uses projections to create shot distributions
"""

import os
import sys
import json
import io
from datetime import datetime
from typing import Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse
from dotenv import load_dotenv

# Fix Unicode encoding issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

# Archetype-based shot distributions
ARCHETYPE_DISTRIBUTIONS = {
    # Guards
    ('PG', 'Playmaker'): {'3PT': 0.35, 'midrange': 0.30, 'paint': 0.35},
    ('PG', 'Shooter'): {'3PT': 0.45, 'midrange': 0.25, 'paint': 0.30},
    ('PG', 'Slasher'): {'3PT': 0.25, 'midrange': 0.25, 'paint': 0.50},
    ('SG', 'Shooter'): {'3PT': 0.55, 'midrange': 0.25, 'paint': 0.20},
    ('SG', 'Slasher'): {'3PT': 0.30, 'midrange': 0.25, 'paint': 0.45},
    ('SG', 'Versatile'): {'3PT': 0.40, 'midrange': 0.30, 'paint': 0.30},
    
    # Forwards  
    ('SF', 'Versatile'): {'3PT': 0.38, 'midrange': 0.27, 'paint': 0.35},
    ('SF', 'Shooter'): {'3PT': 0.48, 'midrange': 0.22, 'paint': 0.30},
    ('SF', 'Slasher'): {'3PT': 0.28, 'midrange': 0.27, 'paint': 0.45},
    ('PF', 'Stretch'): {'3PT': 0.42, 'midrange': 0.23, 'paint': 0.35},
    ('PF', 'Traditional'): {'3PT': 0.15, 'midrange': 0.25, 'paint': 0.60},
    ('PF', 'Versatile'): {'3PT': 0.30, 'midrange': 0.30, 'paint': 0.40},
    
    # Centers
    ('C', 'Modern'): {'3PT': 0.25, 'midrange': 0.20, 'paint': 0.55},
    ('C', 'Traditional'): {'3PT': 0.05, 'midrange': 0.15, 'paint': 0.80},
    ('C', 'Stretch'): {'3PT': 0.40, 'midrange': 0.20, 'paint': 0.40},
}

# Position defaults if archetype not found
POSITION_DEFAULTS = {
    'PG': {'3PT': 0.35, 'midrange': 0.30, 'paint': 0.35},
    'SG': {'3PT': 0.42, 'midrange': 0.28, 'paint': 0.30},
    'SF': {'3PT': 0.35, 'midrange': 0.30, 'paint': 0.35},
    'PF': {'3PT': 0.25, 'midrange': 0.30, 'paint': 0.45},
    'C': {'3PT': 0.15, 'midrange': 0.20, 'paint': 0.65},
    'G': {'3PT': 0.38, 'midrange': 0.29, 'paint': 0.33},  # Generic guard
    'F': {'3PT': 0.30, 'midrange': 0.30, 'paint': 0.40},  # Generic forward
}

# Specific player overrides based on known play styles
PLAYER_SPECIFIC_DISTRIBUTIONS = {
    'Jordan Poole': {'3PT': 0.48, 'midrange': 0.22, 'paint': 0.30},
    'Alperen Sengun': {'3PT': 0.08, 'midrange': 0.32, 'paint': 0.60},
    'Gary Trent Jr.': {'3PT': 0.52, 'midrange': 0.18, 'paint': 0.30},
    'Stephen Curry': {'3PT': 0.58, 'midrange': 0.17, 'paint': 0.25},
    'Giannis Antetokounmpo': {'3PT': 0.12, 'midrange': 0.18, 'paint': 0.70},
    'Nikola Jokic': {'3PT': 0.20, 'midrange': 0.35, 'paint': 0.45},
    'Joel Embiid': {'3PT': 0.25, 'midrange': 0.35, 'paint': 0.40},
    'Damian Lillard': {'3PT': 0.48, 'midrange': 0.22, 'paint': 0.30},
    'Jayson Tatum': {'3PT': 0.40, 'midrange': 0.28, 'paint': 0.32},
    'Luka Doncic': {'3PT': 0.38, 'midrange': 0.27, 'paint': 0.35},
}

def calculate_shot_distribution_from_stats(player_data: Dict) -> Dict[str, float]:
    """Calculate shot distribution from actual game stats"""
    
    fga = float(player_data.get('avg_fga', 0) or 0)
    three_pa = float(player_data.get('avg_3pa', 0) or 0)
    
    if fga == 0:
        return None
    
    # Calculate 3PT rate
    three_pt_rate = three_pa / fga if fga > 0 else 0
    
    # Estimate 2PT distribution based on position
    two_pt_attempts = fga - three_pa
    two_pt_rate = two_pt_attempts / fga if fga > 0 else 0
    
    position = player_data.get('position', 'G')
    
    # Centers and PFs tend to shoot more in the paint
    if position in ['C', 'PF']:
        paint_portion = 0.70  # 70% of 2PT shots are in paint
        midrange_portion = 0.30
    elif position in ['PG', 'SG']:
        paint_portion = 0.45  # Guards shoot more midrange
        midrange_portion = 0.55
    else:
        paint_portion = 0.50
        midrange_portion = 0.50
    
    return {
        '3PT': round(three_pt_rate, 2),
        'midrange': round(two_pt_rate * midrange_portion, 2),
        'paint': round(two_pt_rate * paint_portion, 2)
    }

def estimate_distribution_from_projections(player_data: Dict) -> Dict[str, float]:
    """Estimate shot distribution from fantasy projections"""
    
    projected_3pm = float(player_data.get('projected_3pm', 0) or 0)
    projected_ppg = float(player_data.get('projected_ppg', 0) or 0)
    position = player_data.get('position', 'G')
    playing_style = player_data.get('playing_style', 'Versatile')
    
    # Estimate 3PA from 3PM (assuming 36% shooting)
    estimated_3pa = projected_3pm / 0.36 if projected_3pm > 0 else 0
    
    # Estimate total FGA from PPG (assuming 2.1 points per FGA)
    estimated_fga = projected_ppg / 2.1 if projected_ppg > 0 else 10
    
    # Calculate 3PT rate
    three_pt_rate = min(estimated_3pa / estimated_fga, 0.65) if estimated_fga > 0 else 0.20
    
    # Adjust based on archetype
    archetype = (position, playing_style)
    if archetype in ARCHETYPE_DISTRIBUTIONS:
        base_dist = ARCHETYPE_DISTRIBUTIONS[archetype]
        # Blend estimated 3PT rate with archetype
        three_pt_rate = (three_pt_rate + base_dist['3PT']) / 2
    
    # Distribute remaining shots
    remaining = 1.0 - three_pt_rate
    if position in ['C', 'PF']:
        return {
            '3PT': round(three_pt_rate, 2),
            'midrange': round(remaining * 0.35, 2),
            'paint': round(remaining * 0.65, 2)
        }
    else:
        return {
            '3PT': round(three_pt_rate, 2),
            'midrange': round(remaining * 0.45, 2),
            'paint': round(remaining * 0.55, 2)
        }

def main():
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    print("Generating shot distributions for all players...")
    
    # Step 1: Process players with game_stats data
    print("\n1. Processing players with game stats...")
    cur.execute("""
        SELECT 
            p.id, p.name, p.position, p.playing_style,
            AVG(gs.field_goals_attempted) as avg_fga,
            AVG(gs.three_pointers_attempted) as avg_3pa,
            fd.projected_3pm, fd.projected_ppg
        FROM players p
        LEFT JOIN game_stats gs ON p.id = gs.player_id
        LEFT JOIN fantasy_data fd ON p.id = fd.player_id
        WHERE gs.id IS NOT NULL
        GROUP BY p.id, p.name, p.position, p.playing_style, fd.projected_3pm, fd.projected_ppg
    """)
    
    players_with_stats = cur.fetchall()
    distributions_from_stats = {}
    
    for player in players_with_stats:
        dist = calculate_shot_distribution_from_stats(player)
        if dist:
            distributions_from_stats[player['name']] = dist
            print(f"  {player['name']}: {dist}")
    
    print(f"  Processed {len(distributions_from_stats)} players with game stats")
    
    # Step 2: Process all fantasy-relevant players using projections
    print("\n2. Processing all fantasy-relevant players...")
    cur.execute("""
        SELECT 
            p.id, p.name, p.position, p.playing_style,
            fd.projected_3pm, fd.projected_ppg, fd.projected_rpg, fd.projected_apg
        FROM players p
        JOIN fantasy_data fd ON p.id = fd.player_id
        ORDER BY fd.adp_rank
    """)
    
    all_players = cur.fetchall()
    all_distributions = {}
    
    for player in all_players:
        name = player['name']
        
        # Check for specific override first
        if name in PLAYER_SPECIFIC_DISTRIBUTIONS:
            all_distributions[name] = PLAYER_SPECIFIC_DISTRIBUTIONS[name]
            print(f"  {name}: Using specific override")
        # Use calculated stats if available
        elif name in distributions_from_stats:
            all_distributions[name] = distributions_from_stats[name]
            print(f"  {name}: Using calculated from stats")
        # Otherwise estimate from projections
        else:
            dist = estimate_distribution_from_projections(player)
            all_distributions[name] = dist
            print(f"  {name}: Estimated from projections")
    
    # Step 3: Add shot distribution to database
    print("\n3. Adding shot distributions to database...")
    
    # Add column if it doesn't exist
    try:
        cur.execute("""
            ALTER TABLE fantasy_data 
            ADD COLUMN IF NOT EXISTS shot_distribution JSONB
        """)
        conn.commit()
        print("  Added shot_distribution column to fantasy_data table")
    except Exception as e:
        print(f"  Column may already exist: {e}")
        conn.rollback()
    
    # Update all players with distributions
    for player_name, distribution in all_distributions.items():
        try:
            cur.execute("""
                UPDATE fantasy_data fd
                SET shot_distribution = %s
                FROM players p
                WHERE fd.player_id = p.id AND p.name = %s
            """, (json.dumps(distribution), player_name))
        except Exception as e:
            print(f"  Error updating {player_name}: {e}")
    
    conn.commit()
    print(f"\n✅ Successfully generated shot distributions for {len(all_distributions)} players")
    
    # Step 4: Verify some key players
    print("\n4. Verifying key players...")
    test_players = ['Jordan Poole', 'Alperen Sengun', 'Gary Trent Jr.', 'Jayson Tatum']
    for name in test_players:
        if name in all_distributions:
            print(f"  {name}: {all_distributions[name]}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()