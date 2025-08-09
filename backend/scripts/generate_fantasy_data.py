"""
Generate fantasy data for all NBA players
Creates a complete fantasy_data_2024.json file with ADP and rankings
"""
import json
import random
from pathlib import Path
from nba_api.stats.static import players

def generate_fantasy_data():
    """Generate fantasy data for all active players"""
    
    # Get all active players
    all_players = players.get_active_players()
    print(f"Found {len(all_players)} active players")
    
    # Top 150 players get realistic ADPs
    # Everyone else gets 151-300 range
    fantasy_data = {
        "last_updated": "2024-08-01",
        "source": "Generated based on typical fantasy basketball patterns",
        "note": "Top 50 ADPs are semi-realistic, 51+ are estimated",
        "players": {}
    }
    
    # Manually set top 50 with realistic ADPs
    top_50_adps = {
        "Nikola Jokić": 1.2,
        "Giannis Antetokounmpo": 2.5,
        "Luka Dončić": 3.8,
        "Joel Embiid": 4.2,
        "Shai Gilgeous-Alexander": 5.1,
        "Jayson Tatum": 8.5,
        "Damian Lillard": 9.3,
        "Tyrese Haliburton": 10.7,
        "Stephen Curry": 12.3,
        "Anthony Davis": 13.8,
        "LeBron James": 15.8,
        "Domantas Sabonis": 16.4,
        "Trae Young": 18.2,
        "Donovan Mitchell": 19.5,
        "Karl-Anthony Towns": 21.3,
        "Anthony Edwards": 22.7,
        "Devin Booker": 24.1,
        "Kevin Durant": 25.8,
        "Ja Morant": 28.5,
        "De'Aaron Fox": 29.2,
        "Bam Adebayo": 31.4,
        "Jaylen Brown": 32.8,
        "Jimmy Butler": 34.2,
        "Paul George": 35.6,
        "Kawhi Leonard": 37.1,
        "Alperen Şengün": 38.7,
        "Chet Holmgren": 40.2,
        "Scottie Barnes": 41.8,
        "Dejounte Murray": 43.1,
        "Kristaps Porziņģis": 45.2,
        "Zion Williamson": 46.8,
        "Jaren Jackson Jr.": 48.3,
        "Pascal Siakam": 49.7,
        "Lauri Markkanen": 51.2,
        "Jalen Brunson": 52.6,
        "Julius Randle": 54.1,
        "Nikola Vučević": 55.8,
        "Myles Turner": 57.2,
        "Rudy Gobert": 58.9,
        "Darius Garland": 60.3,
        "CJ McCollum": 61.7,
        "Fred VanVleet": 63.2,
        "Kyrie Irving": 64.8,
        "Evan Mobley": 66.3,
        "Brandon Ingram": 67.9,
        "Mikal Bridges": 69.4,
        "Paolo Banchero": 70.8,
        "Jrue Holiday": 72.3,
        "Bradley Beal": 73.9,
        "Deandre Ayton": 75.4
    }
    
    # Sort players to ensure top players are processed first
    # Create a list with top players first
    top_player_names = list(top_50_adps.keys())
    other_players = [p for p in all_players if p['full_name'] not in top_player_names]
    
    # Sort top players by their ADP
    top_players = [p for p in all_players if p['full_name'] in top_player_names]
    top_players.sort(key=lambda x: top_50_adps.get(x['full_name'], 999))
    
    # Combine: top players first, then others
    sorted_players = top_players + other_players
    
    # Process all players
    for i, player in enumerate(sorted_players):
        player_name = player['full_name']
        
        if player_name in top_50_adps:
            # Use manual ADP for top 50
            adp = top_50_adps[player_name]
            ranking = int(adp)
        elif i < 150:
            # Players 51-150: Generate reasonable ADPs
            base_adp = 50 + (i - 50) * 1.0
            adp = round(base_adp + random.uniform(-2, 2), 1)
            ranking = i + 1
        else:
            # Players 151+: Late round/undrafted
            base_adp = 150 + (i - 150) * 0.5
            adp = round(min(base_adp + random.uniform(-5, 5), 300), 1)
            ranking = i + 1
        
        # Calculate keeper round value
        keeper_round = min(int(adp / 12) + 1, 15)
        if adp <= 24:  # First 2 rounds
            keeper_round = 1
        elif adp <= 48:  # Rounds 3-4
            keeper_round = int(adp / 12)
        
        # Determine position rank
        position = player.get('position', 'G')
        position_rank = f"{position}{min(int(adp/5) + 1, 30)}"
        
        fantasy_data["players"][player_name] = {
            "adp": adp,
            "fantasy_ranking": ranking,
            "keeper_round_value": keeper_round,
            "position_rank": position_rank
        }
        
        # Add notes for special cases
        if player_name == "Ja Morant":
            fantasy_data["players"][player_name]["notes"] = "Suspension risk factored into ADP"
        elif player_name in ["Alperen Şengün", "Paolo Banchero", "Chet Holmgren"]:
            fantasy_data["players"][player_name]["notes"] = "Breakout candidate"
        elif player_name in ["Kawhi Leonard", "Zion Williamson", "Kyrie Irving"]:
            fantasy_data["players"][player_name]["notes"] = "Injury risk factored into ADP"
    
    # Save to file
    output_path = Path(__file__).parent.parent / "data" / "fantasy_data_2024.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(fantasy_data, f, indent=2, ensure_ascii=False)
    
    print(f"Generated fantasy data for {len(fantasy_data['players'])} players")
    print(f"Saved to: {output_path}")
    
    # Print sample
    print("\nSample entries:")
    sample_players = ["Nikola Jokić", "Jayson Tatum", "Alperen Şengün"]
    for name in sample_players:
        if name in fantasy_data["players"]:
            data = fantasy_data["players"][name]
            print(f"  {name}: ADP={data['adp']}, Keeper Round={data['keeper_round_value']}")


if __name__ == "__main__":
    generate_fantasy_data()