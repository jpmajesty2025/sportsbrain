"""
Fetch real FT% data from NBA API for all players in our database
Saves to JSON file for later loading to avoid repeated API calls
"""

import sys
import os
import json
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(r'C:\Projects\nba_api\src')

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats

def get_player_ft_from_api(player_name):
    """Get FT% for a player using NBA API"""
    try:
        # Find player
        nba_players = players.find_players_by_full_name(player_name)
        
        if not nba_players:
            # Try to find by last name and partial first name match
            parts = player_name.split()
            if len(parts) >= 2:
                last_name = parts[-1]
                first_name = parts[0]
                
                # Handle special cases
                if player_name == "OG Anunoby":
                    nba_players = [p for p in players.get_players() if p['full_name'] == "OG Anunoby"]
                elif "Jr." in player_name or "III" in player_name:
                    # Handle Jr. and III suffixes
                    base_name = player_name.replace(" Jr.", "").replace(" III", "")
                    nba_players = players.find_players_by_full_name(base_name)
                    if not nba_players:
                        nba_players = players.find_players_by_last_name(last_name)
                        nba_players = [p for p in nba_players if first_name.lower() in p['full_name'].lower()]
                else:
                    nba_players = players.find_players_by_last_name(last_name)
                    nba_players = [p for p in nba_players if first_name.lower() in p['full_name'].lower()]
        
        if not nba_players:
            display_name = player_name.encode('ascii', 'replace').decode('ascii')
            print(f"  [WARNING] Player not found in NBA API: {display_name}")
            return None
            
        player_id = nba_players[0]['id']
        
        # Get career stats
        career = playercareerstats.PlayerCareerStats(player_id=player_id)
        time.sleep(0.6)  # Rate limiting - NBA API requires delays
        
        # Get the data frames
        data_frames = career.get_data_frames()
        
        # CareerTotalsRegularSeason is at index 1
        career_totals = data_frames[1]
        
        if not career_totals.empty and 'FT_PCT' in career_totals.columns:
            # Last row contains career totals
            career_row = career_totals.iloc[-1]
            
            ft_pct = career_row['FT_PCT']
            fta = career_row['FTA']  # Free throw attempts
            ftm = career_row['FTM']  # Free throws made
            
            if ft_pct is not None and ft_pct > 0:
                return {
                    'ft_pct': float(ft_pct),
                    'ft_attempts': int(fta),
                    'ft_made': int(ftm),
                    'nba_player_id': player_id
                }
        
        display_name = player_name.encode('ascii', 'replace').decode('ascii')
        print(f"  [WARNING] No FT data found for: {display_name}")
        return None
        
    except Exception as e:
        display_name = player_name.encode('ascii', 'replace').decode('ascii')
        print(f"  [ERROR] Error fetching {display_name}: {e}")
        return None

def fetch_all_player_ft_data():
    """Fetch FT% data for all players in our database"""
    
    # Create database connection to get player list
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found in environment")
        return
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Get all players with fantasy data, ordered by ADP
        result = session.execute(text("""
            SELECT p.id, p.name, p.position, f.adp_rank, f.projected_ft_pct
            FROM players p
            JOIN fantasy_data f ON p.id = f.player_id
            ORDER BY f.adp_rank
        """))
        
        all_players = list(result)
        total_players = len(all_players)
        
        print(f"Found {total_players} players in database")
        print("=" * 70)
        
        # Load existing data if file exists (for resuming)
        output_file = "player_ft_data.json"
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                ft_data = json.load(f)
            print(f"Loaded existing data for {len(ft_data)} players")
        else:
            ft_data = {}
        
        # Process in batches
        batch_size = 10
        batch_num = 0
        
        for i in range(0, total_players, batch_size):
            batch = all_players[i:i+batch_size]
            batch_num += 1
            
            print(f"\nBatch {batch_num} (Players {i+1}-{min(i+batch_size, total_players)}):")
            print("-" * 50)
            
            for row in batch:
                player_id = row.id
                player_name = row.name
                position = row.position
                adp_rank = row.adp_rank
                current_ft_pct = row.projected_ft_pct
                
                # Skip if we already have data for this player
                if player_name in ft_data:
                    display_name = player_name.encode('ascii', 'replace').decode('ascii')
                    print(f"  [OK] Already have data for: {display_name}")
                    continue
                
                display_name = player_name.encode('ascii', 'replace').decode('ascii')
                print(f"  Fetching ADP #{adp_rank:3} - {display_name} ({position})...")
                
                api_data = get_player_ft_from_api(player_name)
                
                if api_data:
                    ft_data[player_name] = {
                        'db_player_id': player_id,
                        'name': player_name,
                        'position': position,
                        'adp_rank': adp_rank,
                        'current_db_ft_pct': float(current_ft_pct),
                        'real_ft_pct': api_data['ft_pct'],
                        'ft_attempts': api_data['ft_attempts'],
                        'ft_made': api_data['ft_made'],
                        'nba_player_id': api_data['nba_player_id'],
                        'fetched_at': datetime.now().isoformat()
                    }
                    
                    # Display comparison
                    diff = abs(api_data['ft_pct'] - float(current_ft_pct))
                    if diff > 0.05:
                        status = "[BIG DIFF]"
                    else:
                        status = "[OK]"
                    
                    print(f"    -> FT%: {api_data['ft_pct']:.3f} (was {current_ft_pct:.3f}) {status}")
                else:
                    # Store that we couldn't find this player
                    ft_data[player_name] = {
                        'db_player_id': player_id,
                        'name': player_name,
                        'position': position,
                        'adp_rank': adp_rank,
                        'current_db_ft_pct': float(current_ft_pct),
                        'real_ft_pct': None,  # Couldn't fetch
                        'ft_attempts': None,
                        'ft_made': None,
                        'nba_player_id': None,
                        'fetched_at': datetime.now().isoformat(),
                        'error': 'Player not found in NBA API'
                    }
            
            # Save after each batch
            with open(output_file, 'w') as f:
                json.dump(ft_data, f, indent=2)
            
            print(f"\n  Saved progress: {len(ft_data)}/{total_players} players")
            
            # Longer delay between batches
            if i + batch_size < total_players:
                print(f"  Waiting 3 seconds before next batch...")
                time.sleep(3)
        
        # Final summary
        print("\n" + "=" * 70)
        print("FETCH COMPLETE")
        print("=" * 70)
        
        successful = len([p for p in ft_data.values() if p.get('real_ft_pct') is not None])
        failed = len([p for p in ft_data.values() if p.get('real_ft_pct') is None])
        
        print(f"[SUCCESS] Successfully fetched: {successful} players")
        print(f"[FAILED] Failed to fetch: {failed} players")
        print(f"Total processed: {len(ft_data)} players")
        print(f"\nData saved to: {output_file}")
        
        # Show some examples of big differences
        print("\n" + "=" * 70)
        print("BIGGEST FT% DIFFERENCES FOUND:")
        print("-" * 70)
        
        differences = []
        for player_data in ft_data.values():
            if player_data.get('real_ft_pct') is not None:
                diff = abs(player_data['real_ft_pct'] - player_data['current_db_ft_pct'])
                differences.append((player_data['name'], player_data['current_db_ft_pct'], 
                                  player_data['real_ft_pct'], diff, player_data['adp_rank']))
        
        differences.sort(key=lambda x: x[3], reverse=True)
        
        for name, old_ft, new_ft, diff, adp in differences[:15]:
            display_name = name.encode('ascii', 'replace').decode('ascii')
            print(f"ADP #{adp:3} - {display_name:25} | DB: {old_ft:.1%} -> Real: {new_ft:.1%} | Diff: {diff:.1%}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    print("=" * 70)
    print("NBA API FT% Data Fetcher")
    print("=" * 70)
    print("This script will:")
    print("1. Get all 151 players from our database")
    print("2. Fetch real FT% from NBA API for each player")
    print("3. Save data to player_ft_data.json")
    print("4. Process in batches with rate limiting")
    print("=" * 70)
    print()
    
    fetch_all_player_ft_data()