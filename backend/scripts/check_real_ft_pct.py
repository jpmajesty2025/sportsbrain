"""
Check real FT% from NBA API for specific players
"""
import sys
sys.path.append(r'C:\Projects\nba_api\src')

from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats
import time

def get_career_ft_pct(player_name):
    """Get career FT% for a player from NBA API"""
    try:
        # Find player
        nba_players = players.find_players_by_full_name(player_name)
        if not nba_players:
            print(f"Player not found: {player_name}")
            return None
        
        player_id = nba_players[0]['id']
        print(f"\nFound {player_name} (ID: {player_id})")
        
        # Get career stats
        career = playercareerstats.PlayerCareerStats(player_id=player_id)
        time.sleep(0.6)  # Rate limiting
        
        # Get the data frames
        data_frames = career.get_data_frames()
        
        # CareerTotalsRegularSeason is at index 1
        career_totals = data_frames[1]
        
        if not career_totals.empty:
            # Last row contains career totals
            career_row = career_totals.iloc[-1]
            
            ft_pct = career_row['FT_PCT']
            fta = career_row['FTA']  # Free throw attempts
            ftm = career_row['FTM']  # Free throws made
            
            print(f"  Career FT%: {ft_pct:.3f} ({ft_pct*100:.1f}%)")
            print(f"  Career FTM/FTA: {ftm}/{fta}")
            
            # Also show last few seasons
            if len(career_totals) > 3:
                print(f"\n  Recent seasons FT%:")
                for i in range(-4, -1):
                    if abs(i) <= len(career_totals):
                        season = career_totals.iloc[i]
                        print(f"    {season['SEASON_ID']}: {season['FT_PCT']:.3f} ({season['FT_PCT']*100:.1f}%)")
            
            return ft_pct
        
    except Exception as e:
        print(f"Error for {player_name}: {e}")
        return None

# Check the three players with wrong FT% data
players_to_check = [
    "Tyler Herro",
    "Anfernee Simons", 
    "Bradley Beal"
]

print("="*60)
print("NBA API Career FT% Check")
print("="*60)

for player in players_to_check:
    get_career_ft_pct(player)
    print("-"*40)