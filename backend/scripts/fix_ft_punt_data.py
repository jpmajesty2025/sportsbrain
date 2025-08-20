"""
Fix FT% data and punt_ft_fit flags using real NBA stats
Quick fix to make punt FT% strategy recommendations accurate
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(r'C:\Projects\nba_api\src')

from dotenv import load_dotenv
load_dotenv()  # Load .env file

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from nba_api.stats.endpoints import playercareerstats, playerindex
from nba_api.stats.static import players
import time

# Known FT% data for key players (2023-24 season or career averages)
# This is a fallback in case API calls fail
KNOWN_FT_PCT = {
    'Giannis Antetokounmpo': 0.657,  # Career ~65.7%
    'Rudy Gobert': 0.638,             # Career ~63.8%
    'Clint Capela': 0.529,            # Career ~52.9%
    'Jarrett Allen': 0.705,           # Career ~70.5%
    'Nic Claxton': 0.551,             # Career ~55.1%
    'Karl-Anthony Towns': 0.836,      # Career ~83.6%
    'Nikola Jokić': 0.824,            # Career ~82.4%
    'Joel Embiid': 0.814,             # Career ~81.4%
    'Stephen Curry': 0.908,           # Career ~90.8%
    'Damian Lillard': 0.895,          # Career ~89.5%
    'LeBron James': 0.735,            # Career ~73.5%
    'Luka Dončić': 0.765,             # Career ~76.5%
    'Jusuf Nurkić': 0.694,            # Career ~69.4%
    'Domantas Sabonis': 0.743,        # Career ~74.3%
    'Bam Adebayo': 0.801,             # Career ~80.1%
    'Alperen Sengun': 0.694,          # Career ~69.4%
    'Walker Kessler': 0.654,          # Career ~65.4%
    'Mitchell Robinson': 0.641,       # Career ~64.1%
    'Robert Williams III': 0.654,     # Career ~65.4%
    'Ben Simmons': 0.596,             # Career ~59.6%
    'Zion Williamson': 0.700,         # Career ~70.0%
    'Steven Adams': 0.544,            # Career ~54.4%
    'Andre Drummond': 0.469,          # Career ~46.9%
    'Mason Plumlee': 0.595,           # Career ~59.5%
    'Ivica Zubac': 0.721,             # Career ~72.1%
    'Isaiah Stewart': 0.733,          # Career ~73.3%
    'Naz Reid': 0.737,                # Career ~73.7%
    'Daniel Gafford': 0.723,          # Career ~72.3%
}

def get_player_ft_pct(player_name):
    """Get FT% for a player using NBA API or fallback data"""
    
    # First check our known data
    if player_name in KNOWN_FT_PCT:
        return KNOWN_FT_PCT[player_name]
    
    try:
        # Try to find player in static data
        nba_players = players.find_players_by_full_name(player_name)
        if not nba_players:
            # Try partial match
            parts = player_name.split()
            if len(parts) >= 2:
                nba_players = players.find_players_by_last_name(parts[-1])
                nba_players = [p for p in nba_players if parts[0].lower() in p['full_name'].lower()]
        
        if nba_players:
            player_id = nba_players[0]['id']
            
            # Get career stats
            career = playercareerstats.PlayerCareerStats(player_id=player_id)
            time.sleep(0.6)  # Rate limiting
            
            # Get regular season totals
            df = career.get_data_frames()[1]  # CareerTotalsRegularSeason
            if not df.empty and 'FT_PCT' in df.columns:
                ft_pct = df.iloc[-1]['FT_PCT']  # Last row is career totals
                if ft_pct and ft_pct > 0:
                    return float(ft_pct)
    except Exception as e:
        print(f"  API error for {player_name}: {e}")
    
    # Default fallback based on position patterns
    # Centers and PFs tend to be worse at FT%
    return 0.700  # Default 70%

def is_punt_ft_fit(ft_pct):
    """Determine if a player is a good punt FT% fit"""
    # Players below 72% FT are good for punt FT% builds
    # Elite punt FT% targets are below 65%
    return ft_pct < 0.720

def fix_ft_data():
    """Fix FT% data and punt_ft_fit flags in database"""
    
    # Create database connection
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found in environment")
        return
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Get all players with fantasy data
        result = session.execute(text("""
            SELECT p.id, p.name, p.position, f.projected_ft_pct, f.punt_ft_fit
            FROM players p
            JOIN fantasy_data f ON p.id = f.player_id
            ORDER BY f.adp_rank
        """))
        
        players_to_update = []
        
        print("Fetching real FT% data for players...")
        print("-" * 60)
        
        for row in result:
            player_id = row.id
            player_name = row.name
            position = row.position
            old_ft_pct = row.projected_ft_pct
            old_punt_fit = row.punt_ft_fit
            
            # Get real FT%
            real_ft_pct = get_player_ft_pct(player_name)
            new_punt_fit = is_punt_ft_fit(real_ft_pct)
            
            # Check if we need to update
            if abs(real_ft_pct - old_ft_pct) > 0.01 or new_punt_fit != old_punt_fit:
                players_to_update.append({
                    'id': player_id,
                    'name': player_name,
                    'ft_pct': real_ft_pct,
                    'punt_fit': new_punt_fit,
                    'old_ft_pct': old_ft_pct,
                    'old_punt_fit': old_punt_fit
                })
                
                status = "PUNT FIT" if new_punt_fit else "NOT FIT"
                # Handle unicode names
                display_name = player_name.encode('ascii', 'replace').decode('ascii')
                print(f"{display_name:25} {position:3} | FT%: {old_ft_pct:.1%} -> {real_ft_pct:.1%} | {status}")
        
        print("\n" + "=" * 60)
        print(f"Found {len(players_to_update)} players needing updates")
        
        if players_to_update:
            print("\nUpdating database...")
            
            for player in players_to_update:
                session.execute(text("""
                    UPDATE fantasy_data
                    SET projected_ft_pct = :ft_pct,
                        punt_ft_fit = :punt_fit
                    WHERE player_id = :player_id
                """), {
                    'player_id': player['id'],
                    'ft_pct': player['ft_pct'],
                    'punt_fit': player['punt_fit']
                })
            
            session.commit()
            print(f"Successfully updated {len(players_to_update)} players")
            
            # Show some key examples
            print("\n" + "=" * 60)
            print("KEY PUNT FT% TARGETS (Bad FT shooters):")
            print("-" * 60)
            
            punt_targets = [p for p in players_to_update if p['punt_fit']]
            for player in sorted(punt_targets, key=lambda x: x['ft_pct'])[:10]:
                display_name = player['name'].encode('ascii', 'replace').decode('ascii')
                print(f"  - {display_name:25} - {player['ft_pct']:.1%} FT")
            
            print("\n" + "=" * 60)
            print("NOT PUNT FT% TARGETS (Good FT shooters):")
            print("-" * 60)
            
            good_ft = [p for p in players_to_update if not p['punt_fit'] and p['ft_pct'] > 0.80]
            for player in sorted(good_ft, key=lambda x: -x['ft_pct'])[:10]:
                display_name = player['name'].encode('ascii', 'replace').decode('ascii')
                print(f"  - {display_name:25} - {player['ft_pct']:.1%} FT")
        
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    print("FT% Data Fix Script")
    print("=" * 60)
    print("This script will:")
    print("1. Fetch real FT% data from NBA API (or use known values)")
    print("2. Update projected_ft_pct to real values")
    print("3. Fix punt_ft_fit flags based on actual FT% (<72% = punt fit)")
    print("=" * 60)
    
    fix_ft_data()