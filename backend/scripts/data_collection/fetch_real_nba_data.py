"""
Fetch real NBA data from nba_api for performances and matchups
This will provide authentic data for Neo4j nodes
"""
import sys
import os
import json
from datetime import datetime
from typing import List, Dict, Any
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from nba_api.stats.endpoints import playergamelog, teamgamelog, leaguegamefinder
from nba_api.stats.static import players, teams
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NBADataFetcher:
    def __init__(self, season="2024-25"):
        self.season = season
        self.top_players = []
        self.all_teams = teams.get_teams()
        
    def get_top_fantasy_players(self, limit=50) -> List[Dict]:
        """Get top fantasy-relevant players for 2024-25 season"""
        # Top fantasy players by consensus rankings (mock for 2024-25)
        top_player_names = [
            "Nikola Jokić", "Giannis Antetokounmpo", "Luka Dončić", "Joel Embiid",
            "Jayson Tatum", "Stephen Curry", "Shai Gilgeous-Alexander", "Damian Lillard",
            "LeBron James", "Anthony Davis", "Kevin Durant", "Trae Young",
            "Tyrese Haliburton", "Donovan Mitchell", "Anthony Edwards", "Karl-Anthony Towns",
            "Jaylen Brown", "Paul George", "Devin Booker", "Jimmy Butler",
            "Ja Morant", "Domantas Sabonis", "De'Aaron Fox", "Julius Randle",
            "Pascal Siakam", "Lauri Markkanen", "Kyrie Irving", "Bradley Beal",
            "Zion Williamson", "Bam Adebayo", "Khris Middleton", "Jrue Holiday",
            "DeMar DeRozan", "CJ McCollum", "Brandon Ingram", "Jaren Jackson Jr.",
            "Alperen Sengun", "Paolo Banchero", "Scottie Barnes", "Evan Mobley",
            "Cade Cunningham", "Franz Wagner", "Tyrese Maxey", "Jalen Brunson",
            "Dejounte Murray", "Fred VanVleet", "Darius Garland", "LaMelo Ball",
            "Kawhi Leonard", "Zach LaVine"
        ]
        
        all_players = players.get_active_players()
        top_players = []
        
        for name in top_player_names[:limit]:
            for player in all_players:
                if player['full_name'] == name:
                    top_players.append(player)
                    break
        
        logger.info(f"Found {len(top_players)} top fantasy players")
        return top_players
    
    def fetch_player_performances(self, player_id: int, player_name: str, games_limit: int = 10) -> List[Dict]:
        """Fetch top performances for a player from 2023-24 season (since 2024-25 is ongoing)"""
        performances = []
        
        try:
            # Using 2023-24 season as most recent complete season
            gamelog = playergamelog.PlayerGameLog(
                player_id=player_id,
                season="2023-24"  # Most recent complete season
            )
            
            games_df = gamelog.get_data_frames()[0]
            
            if games_df.empty:
                logger.warning(f"No games found for {player_name}")
                return performances
            
            # Calculate fantasy points for each game
            games_df['FANTASY_PTS'] = (
                games_df['PTS'] * 1.0 +
                games_df['REB'] * 1.2 +
                games_df['AST'] * 1.5 +
                games_df['STL'] * 3.0 +
                games_df['BLK'] * 3.0 -
                games_df['TOV'] * 1.0
            )
            
            # Get top performances by fantasy points
            top_games = games_df.nlargest(games_limit, 'FANTASY_PTS')
            
            for _, game in top_games.iterrows():
                performance = {
                    "performance_id": f"{player_id}_{game['Game_ID']}",
                    "player_id": player_id,
                    "player_name": player_name,
                    "game_date": game['GAME_DATE'],
                    "matchup": game['MATCHUP'],
                    "wl": game['WL'],
                    "minutes": game['MIN'],
                    "points": game['PTS'],
                    "rebounds": game['REB'],
                    "assists": game['AST'],
                    "steals": game['STL'],
                    "blocks": game['BLK'],
                    "turnovers": game['TOV'],
                    "fg_made": game['FGM'],
                    "fg_attempted": game['FGA'],
                    "fg_pct": game['FG_PCT'],
                    "three_made": game['FG3M'],
                    "three_attempted": game['FG3A'],
                    "three_pct": game['FG3_PCT'],
                    "ft_made": game['FTM'],
                    "ft_attempted": game['FTA'],
                    "ft_pct": game['FT_PCT'],
                    "fantasy_points": round(game['FANTASY_PTS'], 1),
                    "plus_minus": game['PLUS_MINUS']
                }
                performances.append(performance)
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            logger.error(f"Error fetching performances for {player_name}: {e}")
        
        return performances
    
    def fetch_all_player_performances(self) -> List[Dict]:
        """Fetch performances for all top players"""
        self.top_players = self.get_top_fantasy_players(50)
        all_performances = []
        
        for i, player in enumerate(self.top_players):
            logger.info(f"Fetching performances for {player['full_name']} ({i+1}/{len(self.top_players)})")
            performances = self.fetch_player_performances(
                player['id'],
                player['full_name'],
                games_limit=10
            )
            all_performances.extend(performances)
            
            # Progress update
            if (i + 1) % 10 == 0:
                logger.info(f"Completed {i+1}/{len(self.top_players)} players")
        
        logger.info(f"Total performances collected: {len(all_performances)}")
        return all_performances
    
    def fetch_team_matchups(self, team_id: int, team_name: str, games_limit: int = 20) -> List[Dict]:
        """Fetch team matchup data"""
        matchups = []
        
        try:
            # Using 2023-24 season
            gamelog = teamgamelog.TeamGameLog(
                team_id=team_id,
                season="2023-24"
            )
            
            games_df = gamelog.get_data_frames()[0]
            
            if games_df.empty:
                logger.warning(f"No games found for {team_name}")
                return matchups
            
            # Get first N games
            games = games_df.head(games_limit)
            
            for _, game in games.iterrows():
                matchup = {
                    "matchup_id": f"{team_id}_{game['Game_ID']}",
                    "game_date": game['GAME_DATE'],
                    "team": team_name,
                    "matchup": game['MATCHUP'],
                    "wl": game['WL'],
                    "team_points": game['PTS'],
                    "team_rebounds": game['REB'],
                    "team_assists": game['AST'],
                    "team_steals": game['STL'],
                    "team_blocks": game['BLK'],
                    "team_turnovers": game['TOV'],
                    "team_fg_pct": game['FG_PCT'],
                    "team_three_pct": game['FG3_PCT'],
                    "team_ft_pct": game['FT_PCT'],
                    "plus_minus": game['PLUS_MINUS']
                }
                matchups.append(matchup)
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            logger.error(f"Error fetching matchups for {team_name}: {e}")
        
        return matchups
    
    def fetch_all_team_matchups(self) -> List[Dict]:
        """Fetch matchups for top teams"""
        all_matchups = []
        
        # Get matchups for top 20 teams
        top_teams = self.all_teams[:20]
        
        for i, team in enumerate(top_teams):
            logger.info(f"Fetching matchups for {team['full_name']} ({i+1}/{len(top_teams)})")
            matchups = self.fetch_team_matchups(
                team['id'],
                team['abbreviation'],
                games_limit=20
            )
            all_matchups.extend(matchups)
        
        logger.info(f"Total matchups collected: {len(all_matchups)}")
        return all_matchups
    
    def save_data(self, performances: List[Dict], matchups: List[Dict]):
        """Save collected data to JSON files"""
        output_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'data', 'real_nba_data'
        )
        os.makedirs(output_dir, exist_ok=True)
        
        # Save performances
        performances_file = os.path.join(output_dir, 'player_performances_2023_24.json')
        with open(performances_file, 'w', encoding='utf-8') as f:
            json.dump({
                "season": "2023-24",
                "generated_at": datetime.now().isoformat(),
                "total_performances": len(performances),
                "performances": performances
            }, f, indent=2)
        logger.info(f"Saved {len(performances)} performances to {performances_file}")
        
        # Save matchups
        matchups_file = os.path.join(output_dir, 'team_matchups_2023_24.json')
        with open(matchups_file, 'w', encoding='utf-8') as f:
            json.dump({
                "season": "2023-24",
                "generated_at": datetime.now().isoformat(),
                "total_matchups": len(matchups),
                "matchups": matchups
            }, f, indent=2)
        logger.info(f"Saved {len(matchups)} matchups to {matchups_file}")
        
        # Create summary
        summary = {
            "data_collection_summary": {
                "date": datetime.now().isoformat(),
                "season": "2023-24",
                "performances": {
                    "total": len(performances),
                    "players": len(self.top_players),
                    "avg_per_player": len(performances) / len(self.top_players) if self.top_players else 0
                },
                "matchups": {
                    "total": len(matchups),
                    "teams": 20,
                    "avg_per_team": len(matchups) / 20
                }
            }
        }
        
        summary_file = os.path.join(output_dir, 'collection_summary.json')
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        return output_dir


def main():
    """Main function to fetch all real NBA data"""
    print("=" * 60)
    print("NBA Data Collection Script")
    print("=" * 60)
    
    fetcher = NBADataFetcher(season="2023-24")
    
    # Fetch player performances
    print("\n[1/2] Fetching player performances...")
    performances = fetcher.fetch_all_player_performances()
    print(f"✓ Collected {len(performances)} performances")
    
    # Fetch team matchups
    print("\n[2/2] Fetching team matchups...")
    matchups = fetcher.fetch_all_team_matchups()
    print(f"✓ Collected {len(matchups)} matchups")
    
    # Save data
    print("\nSaving data...")
    output_dir = fetcher.save_data(performances, matchups)
    
    print("\n" + "=" * 60)
    print("Data Collection Complete!")
    print(f"✓ {len(performances)} player performances")
    print(f"✓ {len(matchups)} team matchups")
    print(f"✓ Data saved to: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()