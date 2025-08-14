"""
Test the new similarity matching functionality
"""

import sys
import os
import io
import json

# Fix Unicode encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse
from dotenv import load_dotenv

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

def test_similarity_matching():
    """Test the find_similar_players functionality by directly querying"""
    cur = conn.cursor()
    
    print("="*80)
    print("TESTING SIMILARITY MATCHING")
    print("="*80)
    
    # First, let's see what players we actually have
    cur.execute("""
        SELECT name FROM players 
        WHERE name IN ('Anfernee Simons', 'Scoot Henderson', 'Alperen Sengun')
    """)
    available = cur.fetchall()
    print(f"\nAvailable test players: {[p['name'] for p in available]}")
    
    # Use players we know exist
    test_players = [
        "Scoot Henderson",  # We know this exists from validation
        "Gary Trent Jr.",   # Top sleeper
        "Naz Reid"          # Another known sleeper
    ]
    
    for ref_player in test_players:
        print(f"\n\nFinding players similar to {ref_player}:")
        print("-"*60)
        
        # Get reference player info
        cur.execute("""
            SELECT p.*, fd.shot_distribution, fd.sleeper_score
            FROM players p
            JOIN fantasy_data fd ON p.id = fd.player_id
            WHERE p.name = %s
        """, (ref_player,))
        
        ref = cur.fetchone()
        if not ref:
            print(f"Player {ref_player} not found!")
            continue
            
        ref_dist = json.loads(ref['shot_distribution']) if isinstance(ref['shot_distribution'], str) else ref['shot_distribution']
        
        print(f"Reference: {ref['position']}, {ref['playing_style']}")
        print(f"Shot Profile: 3PT={ref_dist.get('3PT',0)*100:.0f}%, Mid={ref_dist.get('midrange',0)*100:.0f}%, Paint={ref_dist.get('paint',0)*100:.0f}%")
        
        # Find similar players
        cur.execute("""
            WITH similarity_scores AS (
                SELECT 
                    p.name, p.position, p.team, p.playing_style,
                    fd.sleeper_score, fd.adp_rank, fd.shot_distribution,
                    CASE 
                        WHEN p.position = %(ref_pos)s THEN 0.3
                        WHEN p.position IN ('PG', 'SG') AND %(ref_pos)s IN ('PG', 'SG') THEN 0.2
                        WHEN p.position IN ('SF', 'PF') AND %(ref_pos)s IN ('SF', 'PF') THEN 0.2
                        ELSE 0
                    END +
                    CASE WHEN p.playing_style = %(ref_style)s THEN 0.3 ELSE 0 END +
                    fd.sleeper_score * 0.4 as total_similarity
                FROM players p
                JOIN fantasy_data fd ON p.id = fd.player_id
                WHERE p.name != %(ref_name)s
                    AND fd.sleeper_score >= 0.6
                    AND fd.shot_distribution IS NOT NULL
            )
            SELECT * FROM similarity_scores
            ORDER BY total_similarity DESC
            LIMIT 5
        """, {
            'ref_name': ref_player,
            'ref_pos': ref['position'],
            'ref_style': ref['playing_style']
        })
        
        similar = cur.fetchall()
        
        print(f"\nTop 5 Similar Sleepers:")
        for i, player in enumerate(similar, 1):
            p_dist = json.loads(player['shot_distribution']) if isinstance(player['shot_distribution'], str) else player['shot_distribution']
            
            # Calculate shot similarity
            import math
            distance = math.sqrt(
                (ref_dist.get('3PT', 0) - p_dist.get('3PT', 0))**2 +
                (ref_dist.get('midrange', 0) - p_dist.get('midrange', 0))**2 +
                (ref_dist.get('paint', 0) - p_dist.get('paint', 0))**2
            )
            shot_sim = max(0, 1 - distance)
            
            print(f"\n{i}. {player['name']} ({player['position']}, {player['team']})")
            print(f"   Sleeper Score: {player['sleeper_score']:.2f} | ADP: #{player['adp_rank']}")
            print(f"   Style: {player['playing_style']}")
            print(f"   Shot: 3PT={p_dist.get('3PT',0)*100:.0f}%, Mid={p_dist.get('midrange',0)*100:.0f}%, Paint={p_dist.get('paint',0)*100:.0f}%")
            print(f"   Shot Similarity: {shot_sim:.0%}")
    
    cur.close()

if __name__ == "__main__":
    test_similarity_matching()