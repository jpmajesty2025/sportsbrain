"""
Load PostgreSQL with 2024-25 fantasy basketball draft prep data
Focus: Off-season (August 2025) draft preparation
"""
import sys
import os
import json
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any
from dotenv import load_dotenv

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

# Load environment variables from root .env file
root_dir = os.path.dirname(backend_dir)
env_path = os.path.join(root_dir, '.env')
load_dotenv(env_path)

# Now import database components (they will use the loaded env vars)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import Team, Player, Game, GameStats, FantasyData
from nba_api.stats.static import teams, players
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DraftDataLoader:
    def __init__(self):
        # Create database session using env var
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL not found in environment variables")
        
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self.session = SessionLocal()
        self.teams_data = []
        self.players_data = []
        
    def load_teams(self):
        """Load all 30 NBA teams"""
        logger.info("Loading NBA teams...")
        
        # Check if teams already exist
        existing_count = self.session.query(Team).count()
        if existing_count > 0:
            logger.info(f"Teams already exist ({existing_count}). Loading existing teams...")
            self.teams_data = self.session.query(Team).all()
            return
        
        nba_teams = teams.get_teams()
        
        for team_data in nba_teams:
            team = Team(
                name=team_data['full_name'],
                city=team_data['city'],
                abbreviation=team_data['abbreviation'],
                conference="Eastern" if team_data['abbreviation'] in [
                    'ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DET', 'IND',
                    'MIA', 'MIL', 'NYK', 'ORL', 'PHI', 'TOR', 'WAS'
                ] else "Western",
                division=self._get_division(team_data['abbreviation']),
                founded_year=1946,  # Default for most teams
                pace_factor=random.uniform(98.0, 103.0),  # Team pace
                offensive_style_rating=random.uniform(105.0, 115.0),
                defensive_style_rating=random.uniform(105.0, 115.0),
                is_active=True
            )
            self.session.add(team)
            self.session.flush()  # Flush to get the ID
            self.teams_data.append(team)
        
        self.session.commit()
        logger.info(f"Loaded {len(nba_teams)} teams")
        
    def _get_division(self, abbreviation: str) -> str:
        """Get division for team"""
        divisions = {
            'Atlantic': ['BOS', 'BKN', 'NYK', 'PHI', 'TOR'],
            'Central': ['CHI', 'CLE', 'DET', 'IND', 'MIL'],
            'Southeast': ['ATL', 'CHA', 'MIA', 'ORL', 'WAS'],
            'Northwest': ['DEN', 'MIN', 'OKC', 'POR', 'UTA'],
            'Pacific': ['GSW', 'LAC', 'LAL', 'PHX', 'SAC'],
            'Southwest': ['DAL', 'HOU', 'MEM', 'NOP', 'SAS']
        }
        
        for division, teams in divisions.items():
            if abbreviation in teams:
                return division
        return "Unknown"
    
    def load_players(self):
        """Load top 150 fantasy-relevant players with 2024-25 projections"""
        logger.info("Loading fantasy-relevant players...")
        
        # Check if players already exist
        existing_count = self.session.query(Player).count()
        if existing_count > 0:
            logger.info(f"Players already exist ({existing_count}). Loading existing players...")
            players = self.session.query(Player).all()
            # Create simple ADP mapping
            for i, player in enumerate(players[:150]):
                self.players_data.append((player, i + 1))
            return
        
        # Top 150 fantasy players for 2024-25 season
        top_fantasy_players = [
            # Top 10 - Elite tier
            {"name": "Nikola Jokić", "team": "DEN", "position": "C", "adp": 1},
            {"name": "Giannis Antetokounmpo", "team": "MIL", "position": "PF", "adp": 2},
            {"name": "Luka Dončić", "team": "DAL", "position": "PG", "adp": 3},
            {"name": "Joel Embiid", "team": "PHI", "position": "C", "adp": 4},
            {"name": "Jayson Tatum", "team": "BOS", "position": "SF", "adp": 5},
            {"name": "Stephen Curry", "team": "GSW", "position": "PG", "adp": 6},
            {"name": "Shai Gilgeous-Alexander", "team": "OKC", "position": "SG", "adp": 7},
            {"name": "Damian Lillard", "team": "MIL", "position": "PG", "adp": 8},
            {"name": "LeBron James", "team": "LAL", "position": "SF", "adp": 9},
            {"name": "Anthony Davis", "team": "LAL", "position": "PF", "adp": 10},
            
            # 11-30 - First/Second round
            {"name": "Kevin Durant", "team": "PHX", "position": "SF", "adp": 11},
            {"name": "Trae Young", "team": "ATL", "position": "PG", "adp": 12},
            {"name": "Tyrese Haliburton", "team": "IND", "position": "PG", "adp": 13},
            {"name": "Donovan Mitchell", "team": "CLE", "position": "SG", "adp": 14},
            {"name": "Anthony Edwards", "team": "MIN", "position": "SG", "adp": 15},
            {"name": "Karl-Anthony Towns", "team": "NYK", "position": "C", "adp": 16},
            {"name": "Jaylen Brown", "team": "BOS", "position": "SG", "adp": 17},
            {"name": "Paul George", "team": "PHI", "position": "SF", "adp": 18},
            {"name": "Devin Booker", "team": "PHX", "position": "SG", "adp": 19},
            {"name": "Jimmy Butler", "team": "MIA", "position": "SF", "adp": 20},
            {"name": "Ja Morant", "team": "MEM", "position": "PG", "adp": 21},
            {"name": "Domantas Sabonis", "team": "SAC", "position": "C", "adp": 22},
            {"name": "De'Aaron Fox", "team": "SAC", "position": "PG", "adp": 23},
            {"name": "Julius Randle", "team": "MIN", "position": "PF", "adp": 24},
            {"name": "Pascal Siakam", "team": "IND", "position": "PF", "adp": 25},
            {"name": "Lauri Markkanen", "team": "UTA", "position": "PF", "adp": 26},
            {"name": "Kyrie Irving", "team": "DAL", "position": "PG", "adp": 27},
            {"name": "Bradley Beal", "team": "PHX", "position": "SG", "adp": 28},
            {"name": "Zion Williamson", "team": "NOP", "position": "PF", "adp": 29},
            {"name": "Bam Adebayo", "team": "MIA", "position": "C", "adp": 30},
            
            # 31-60 - Rounds 3-4
            {"name": "Kristaps Porzingis", "team": "BOS", "position": "C", "adp": 31},
            {"name": "Jrue Holiday", "team": "BOS", "position": "PG", "adp": 32},
            {"name": "DeMar DeRozan", "team": "SAC", "position": "SF", "adp": 33},
            {"name": "CJ McCollum", "team": "NOP", "position": "SG", "adp": 34},
            {"name": "Brandon Ingram", "team": "NOP", "position": "SF", "adp": 35},
            {"name": "Jaren Jackson Jr.", "team": "MEM", "position": "PF", "adp": 36},
            {"name": "Alperen Sengun", "team": "HOU", "position": "C", "adp": 37},
            {"name": "Paolo Banchero", "team": "ORL", "position": "PF", "adp": 38},
            {"name": "Scottie Barnes", "team": "TOR", "position": "SF", "adp": 39},
            {"name": "Evan Mobley", "team": "CLE", "position": "C", "adp": 40},
            {"name": "Cade Cunningham", "team": "DET", "position": "PG", "adp": 41},
            {"name": "Franz Wagner", "team": "ORL", "position": "SF", "adp": 42},
            {"name": "Tyrese Maxey", "team": "PHI", "position": "SG", "adp": 43},
            {"name": "Jalen Brunson", "team": "NYK", "position": "PG", "adp": 44},
            {"name": "Dejounte Murray", "team": "NOP", "position": "PG", "adp": 45},
            {"name": "Fred VanVleet", "team": "HOU", "position": "PG", "adp": 46},
            {"name": "Darius Garland", "team": "CLE", "position": "PG", "adp": 47},
            {"name": "LaMelo Ball", "team": "CHA", "position": "PG", "adp": 48},
            {"name": "Kawhi Leonard", "team": "LAC", "position": "SF", "adp": 49},
            {"name": "Zach LaVine", "team": "CHI", "position": "SG", "adp": 50},
            {"name": "Rudy Gobert", "team": "MIN", "position": "C", "adp": 51},
            {"name": "Myles Turner", "team": "IND", "position": "C", "adp": 52},
            {"name": "OG Anunoby", "team": "NYK", "position": "SF", "adp": 53},
            {"name": "Nikola Vucevic", "team": "CHI", "position": "C", "adp": 54},
            {"name": "Mikal Bridges", "team": "NYK", "position": "SF", "adp": 55},
            {"name": "Chet Holmgren", "team": "OKC", "position": "C", "adp": 56},
            {"name": "Victor Wembanyama", "team": "SAS", "position": "C", "adp": 57},
            {"name": "Walker Kessler", "team": "UTA", "position": "C", "adp": 58},
            {"name": "Nic Claxton", "team": "BKN", "position": "C", "adp": 59},
            {"name": "Desmond Bane", "team": "MEM", "position": "SG", "adp": 60},
            
            # 61-90 - Rounds 5-6 (mid-round values)
            {"name": "Tyler Herro", "team": "MIA", "position": "SG", "adp": 61},
            {"name": "Anfernee Simons", "team": "POR", "position": "SG", "adp": 62},
            {"name": "Jalen Williams", "team": "OKC", "position": "SF", "adp": 63},
            {"name": "Jamal Murray", "team": "DEN", "position": "PG", "adp": 64},
            {"name": "Khris Middleton", "team": "MIL", "position": "SF", "adp": 65},
            {"name": "Michael Porter Jr.", "team": "DEN", "position": "SF", "adp": 66},
            {"name": "John Collins", "team": "UTA", "position": "PF", "adp": 67},
            {"name": "Clint Capela", "team": "ATL", "position": "C", "adp": 68},
            {"name": "Jonas Valanciunas", "team": "WAS", "position": "C", "adp": 69},
            {"name": "Brook Lopez", "team": "MIL", "position": "C", "adp": 70},
            {"name": "Derrick White", "team": "BOS", "position": "PG", "adp": 71},
            {"name": "Jordan Poole", "team": "WAS", "position": "SG", "adp": 72},
            {"name": "Jaden Ivey", "team": "DET", "position": "SG", "adp": 73},
            {"name": "Ausar Thompson", "team": "DET", "position": "SF", "adp": 74},
            {"name": "Keegan Murray", "team": "SAC", "position": "PF", "adp": 75},
            {"name": "Bennedict Mathurin", "team": "IND", "position": "SG", "adp": 76},
            {"name": "Jabari Smith Jr.", "team": "HOU", "position": "PF", "adp": 77},
            {"name": "Jalen Green", "team": "HOU", "position": "SG", "adp": 78},
            {"name": "RJ Barrett", "team": "TOR", "position": "SG", "adp": 79},
            {"name": "Marcus Smart", "team": "MEM", "position": "PG", "adp": 80},
            {"name": "Terry Rozier", "team": "MIA", "position": "PG", "adp": 81},
            {"name": "Mike Conley", "team": "MIN", "position": "PG", "adp": 82},
            {"name": "D'Angelo Russell", "team": "LAL", "position": "PG", "adp": 83},
            {"name": "Kyle Kuzma", "team": "WAS", "position": "PF", "adp": 84},
            {"name": "Tobias Harris", "team": "DET", "position": "PF", "adp": 85},
            {"name": "Jerami Grant", "team": "POR", "position": "PF", "adp": 86},
            {"name": "Deandre Ayton", "team": "POR", "position": "C", "adp": 87},
            {"name": "Jusuf Nurkic", "team": "PHX", "position": "C", "adp": 88},
            {"name": "Robert Williams III", "team": "POR", "position": "C", "adp": 89},
            {"name": "Mitchell Robinson", "team": "NYK", "position": "C", "adp": 90},
            
            # 91-120 - Late rounds (sleepers and value picks)
            {"name": "Amen Thompson", "team": "HOU", "position": "PG", "adp": 91},
            {"name": "Shaedon Sharpe", "team": "POR", "position": "SG", "adp": 92},
            {"name": "Jonathan Kuminga", "team": "GSW", "position": "PF", "adp": 93},
            {"name": "Cam Thomas", "team": "BKN", "position": "SG", "adp": 94},
            {"name": "Collin Sexton", "team": "UTA", "position": "SG", "adp": 95},
            {"name": "Bogdan Bogdanovic", "team": "ATL", "position": "SG", "adp": 96},
            {"name": "Spencer Dinwiddie", "team": "DAL", "position": "PG", "adp": 97},
            {"name": "Immanuel Quickley", "team": "TOR", "position": "PG", "adp": 98},
            {"name": "Donte DiVincenzo", "team": "NYK", "position": "SG", "adp": 99},
            {"name": "Herbert Jones", "team": "NOP", "position": "SF", "adp": 100},
            {"name": "Alex Caruso", "team": "OKC", "position": "SG", "adp": 101},
            {"name": "Coby White", "team": "CHI", "position": "PG", "adp": 102},
            {"name": "Jalen Suggs", "team": "ORL", "position": "PG", "adp": 103},
            {"name": "Cole Anthony", "team": "ORL", "position": "PG", "adp": 104},
            {"name": "Keldon Johnson", "team": "SAS", "position": "SF", "adp": 105},
            {"name": "Devin Vassell", "team": "SAS", "position": "SG", "adp": 106},
            {"name": "Isaiah Stewart", "team": "DET", "position": "C", "adp": 107},
            {"name": "Wendell Carter Jr.", "team": "ORL", "position": "C", "adp": 108},
            {"name": "Jakob Poeltl", "team": "TOR", "position": "C", "adp": 109},
            {"name": "Ivica Zubac", "team": "LAC", "position": "C", "adp": 110},
            {"name": "Daniel Gafford", "team": "DAL", "position": "C", "adp": 111},
            {"name": "Jarrett Allen", "team": "CLE", "position": "C", "adp": 112},
            {"name": "Mark Williams", "team": "CHA", "position": "C", "adp": 113},
            {"name": "Alperen Şengün", "team": "HOU", "position": "C", "adp": 114},
            {"name": "Bobby Portis", "team": "MIL", "position": "PF", "adp": 115},
            {"name": "P.J. Washington", "team": "DAL", "position": "PF", "adp": 116},
            {"name": "Aaron Gordon", "team": "DEN", "position": "PF", "adp": 117},
            {"name": "Draymond Green", "team": "GSW", "position": "PF", "adp": 118},
            {"name": "Harrison Barnes", "team": "SAS", "position": "SF", "adp": 119},
            {"name": "Andrew Wiggins", "team": "GSW", "position": "SF", "adp": 120},
            
            # 121-150 - Deep sleepers
            {"name": "Scoot Henderson", "team": "POR", "position": "PG", "adp": 121},
            {"name": "Josh Giddey", "team": "CHI", "position": "PG", "adp": 122},
            {"name": "Tari Eason", "team": "HOU", "position": "PF", "adp": 123},
            {"name": "Cam Whitmore", "team": "HOU", "position": "SF", "adp": 124},
            {"name": "Dereck Lively II", "team": "DAL", "position": "C", "adp": 125},
            {"name": "Taylor Hendricks", "team": "UTA", "position": "PF", "adp": 126},
            {"name": "Gradey Dick", "team": "TOR", "position": "SG", "adp": 127},
            {"name": "Jaime Jaquez Jr.", "team": "MIA", "position": "SF", "adp": 128},
            {"name": "Brandin Podziemski", "team": "GSW", "position": "SG", "adp": 129},
            {"name": "Keyonte George", "team": "UTA", "position": "PG", "adp": 130},
            {"name": "Bilal Coulibaly", "team": "WAS", "position": "SF", "adp": 131},
            {"name": "Cason Wallace", "team": "OKC", "position": "PG", "adp": 132},
            {"name": "Nick Smith Jr.", "team": "CHA", "position": "PG", "adp": 133},
            {"name": "Kobe Bufkin", "team": "ATL", "position": "PG", "adp": 134},
            {"name": "Marcus Sasser", "team": "DET", "position": "PG", "adp": 135},
            {"name": "Chris Paul", "team": "SAS", "position": "PG", "adp": 136},
            {"name": "Russell Westbrook", "team": "DEN", "position": "PG", "adp": 137},
            {"name": "Malcolm Brogdon", "team": "WAS", "position": "PG", "adp": 138},
            {"name": "Norman Powell", "team": "LAC", "position": "SG", "adp": 139},
            {"name": "Gary Trent Jr.", "team": "MIL", "position": "SG", "adp": 140},
            {"name": "Malik Monk", "team": "SAC", "position": "SG", "adp": 141},
            {"name": "Austin Reaves", "team": "LAL", "position": "SG", "adp": 142},
            {"name": "Josh Hart", "team": "NYK", "position": "SG", "adp": 143},
            {"name": "Kentavious Caldwell-Pope", "team": "ORL", "position": "SG", "adp": 144},
            {"name": "Bruce Brown", "team": "TOR", "position": "SG", "adp": 145},
            {"name": "Matisse Thybulle", "team": "POR", "position": "SF", "adp": 146},
            {"name": "Dorian Finney-Smith", "team": "BKN", "position": "PF", "adp": 147},
            {"name": "Grant Williams", "team": "CHA", "position": "PF", "adp": 148},
            {"name": "Naz Reid", "team": "MIN", "position": "C", "adp": 149},
            {"name": "Onyeka Okongwu", "team": "ATL", "position": "C", "adp": 150}
        ]
        
        for player_data in top_fantasy_players:
            # Get NBA API player info if available
            nba_players = players.get_active_players()
            player_info = None
            for p in nba_players:
                if p['full_name'] == player_data['name']:
                    player_info = p
                    break
            
            player = Player(
                name=player_data['name'],
                team=player_data['team'],
                position=player_data['position'],
                jersey_number=random.randint(0, 99),
                height=random.uniform(72, 84) if not player_info else 78,  # inches
                weight=random.uniform(180, 280) if not player_info else 220,  # pounds
                is_active=True,
                playing_style=self._get_playing_style(player_data['position']),
                career_start=datetime(2015, 10, 1)  # Default
            )
            self.session.add(player)
            self.session.flush()  # Flush to get the ID
            self.players_data.append((player, player_data['adp']))
        
        self.session.commit()
        logger.info(f"Loaded {len(top_fantasy_players)} players")
    
    def _get_playing_style(self, position: str) -> str:
        """Get playing style based on position"""
        styles = {
            'PG': ['Playmaker', 'Scorer', 'Two-Way', 'Floor General'],
            'SG': ['Shooter', 'Slasher', 'Two-Way', '3-and-D'],
            'SF': ['Versatile', 'Shooter', 'Defender', 'Point Forward'],
            'PF': ['Stretch', 'Post', 'Defensive', 'Face-up'],
            'C': ['Traditional', 'Stretch', 'Defensive Anchor', 'Athletic']
        }
        return random.choice(styles.get(position, ['Versatile']))
    
    def load_reference_games(self):
        """Load reference games from 2023-24 season for historical context"""
        logger.info("Loading reference games from 2023-24 season...")
        
        # Generate 100 reference games from last season
        start_date = datetime(2023, 10, 24)  # 2023-24 season start
        
        for i in range(100):
            game_date = start_date + timedelta(days=random.randint(0, 180))
            
            # Pick two random teams
            home_team = random.choice(self.teams_data)
            away_team = random.choice([t for t in self.teams_data if t.id != home_team.id])
            
            # Generate score
            home_score = random.randint(95, 130)
            away_score = random.randint(95, 130)
            
            game = Game(
                date=game_date,
                home_team=home_team.abbreviation,
                away_team=away_team.abbreviation,
                home_score=home_score,
                away_score=away_score,
                status="completed",
                venue=f"{home_team.city} Arena",
                season_type="2023-24",
                season_year=2024,
                game_type="regular",
                pace=random.uniform(96.0, 104.0),
                overtime=random.random() < 0.05  # 5% chance of OT
            )
            self.session.add(game)
        
        self.session.commit()
        logger.info("Loaded 100 reference games")
    
    def load_game_stats(self):
        """Load sample game stats for reference"""
        logger.info("Loading game stats...")
        
        # Get all games and top 30 players
        games = self.session.query(Game).limit(20).all()
        top_players = [p[0] for p in self.players_data[:30]]
        
        stats_count = 0
        for game in games:
            # Each game has 10-15 players with stats
            players_in_game = random.sample(top_players, min(12, len(top_players)))
            
            for player in players_in_game:
                # Generate realistic stats based on position
                stats = self._generate_game_stats(player.position)
                
                game_stat = GameStats(
                    player_id=player.id,
                    game_id=game.id,
                    points=stats['points'],
                    assists=stats['assists'],
                    rebounds=stats['rebounds'],
                    steals=stats['steals'],
                    blocks=stats['blocks'],
                    turnovers=stats['turnovers'],
                    field_goals_made=stats['fgm'],
                    field_goals_attempted=stats['fga'],
                    three_pointers_made=stats['3pm'],
                    three_pointers_attempted=stats['3pa'],
                    free_throws_made=stats['ftm'],
                    free_throws_attempted=stats['fta'],
                    minutes_played=stats['minutes'],
                    plus_minus=random.randint(-20, 20),
                    usage_rate=stats['usage_rate'],
                    fantasy_points=stats['fantasy_points']
                )
                self.session.add(game_stat)
                stats_count += 1
        
        self.session.commit()
        logger.info(f"Loaded {stats_count} game stats")
    
    def _generate_game_stats(self, position: str) -> Dict:
        """Generate realistic stats based on position"""
        base_stats = {
            'PG': {'points': (8, 25), 'assists': (4, 12), 'rebounds': (2, 6), 
                   'steals': (0, 3), 'blocks': (0, 1), 'turnovers': (1, 4)},
            'SG': {'points': (10, 28), 'assists': (2, 6), 'rebounds': (2, 5),
                   'steals': (0, 2), 'blocks': (0, 1), 'turnovers': (1, 3)},
            'SF': {'points': (8, 24), 'assists': (2, 5), 'rebounds': (3, 8),
                   'steals': (0, 2), 'blocks': (0, 2), 'turnovers': (1, 3)},
            'PF': {'points': (8, 22), 'assists': (1, 4), 'rebounds': (5, 10),
                   'steals': (0, 2), 'blocks': (0, 3), 'turnovers': (1, 3)},
            'C': {'points': (6, 20), 'assists': (1, 3), 'rebounds': (6, 12),
                  'steals': (0, 1), 'blocks': (1, 3), 'turnovers': (1, 3)}
        }
        
        stats = base_stats.get(position, base_stats['SF'])
        
        points = random.randint(*stats['points'])
        assists = random.randint(*stats['assists'])
        rebounds = random.randint(*stats['rebounds'])
        steals = random.randint(*stats['steals'])
        blocks = random.randint(*stats['blocks'])
        turnovers = random.randint(*stats['turnovers'])
        
        # Calculate shooting
        fgm = int(points * 0.4)  # Rough estimate
        fga = int(fgm * 2.2)  # ~45% FG
        three_pm = random.randint(0, min(5, int(points * 0.15)))
        three_pa = int(three_pm * 2.5) if three_pm > 0 else 0
        ftm = points - (fgm * 2) - (three_pm * 3)
        ftm = max(0, ftm)
        fta = int(ftm * 1.25) if ftm > 0 else 0
        
        # Calculate fantasy points (standard scoring)
        fantasy_points = (points * 1.0 + rebounds * 1.2 + assists * 1.5 + 
                         steals * 3.0 + blocks * 3.0 - turnovers * 1.0)
        
        return {
            'points': points,
            'assists': assists,
            'rebounds': rebounds,
            'steals': steals,
            'blocks': blocks,
            'turnovers': turnovers,
            'fgm': fgm,
            'fga': fga,
            '3pm': three_pm,
            '3pa': three_pa,
            'ftm': ftm,
            'fta': fta,
            'minutes': random.uniform(20, 36),
            'usage_rate': random.uniform(15, 35),
            'fantasy_points': round(fantasy_points, 1)
        }
    
    def load_fantasy_data(self):
        """Load fantasy-specific data for draft prep"""
        logger.info("Loading fantasy draft data...")
        
        for player, adp in self.players_data:
            # Determine round based on ADP (12-team league)
            adp_round = ((adp - 1) // 12) + 1
            
            # Calculate keeper round (usually 1-2 rounds earlier than ADP)
            keeper_round = max(1, adp_round - random.randint(1, 2))
            
            # Generate projections based on ADP tier
            if adp <= 10:  # Elite tier
                ppg = random.uniform(22, 30)
                rpg = random.uniform(5, 12) if player.position in ['PF', 'C'] else random.uniform(3, 6)
                apg = random.uniform(5, 10) if player.position == 'PG' else random.uniform(2, 5)
                fantasy_ppg = random.uniform(45, 60)
            elif adp <= 30:  # First/second round
                ppg = random.uniform(18, 25)
                rpg = random.uniform(4, 10) if player.position in ['PF', 'C'] else random.uniform(3, 5)
                apg = random.uniform(4, 8) if player.position == 'PG' else random.uniform(2, 4)
                fantasy_ppg = random.uniform(35, 45)
            elif adp <= 60:  # Mid rounds
                ppg = random.uniform(14, 20)
                rpg = random.uniform(3, 8) if player.position in ['PF', 'C'] else random.uniform(2, 4)
                apg = random.uniform(3, 6) if player.position == 'PG' else random.uniform(1, 3)
                fantasy_ppg = random.uniform(28, 38)
            elif adp <= 100:  # Late rounds
                ppg = random.uniform(10, 16)
                rpg = random.uniform(3, 7) if player.position in ['PF', 'C'] else random.uniform(2, 4)
                apg = random.uniform(2, 5) if player.position == 'PG' else random.uniform(1, 2)
                fantasy_ppg = random.uniform(22, 30)
            else:  # Deep sleepers
                ppg = random.uniform(8, 14)
                rpg = random.uniform(2, 6)
                apg = random.uniform(1, 4)
                fantasy_ppg = random.uniform(18, 25)
            
            # Determine punt build fits
            punt_ft = player.position == 'C' and random.random() < 0.3  # Centers often bad at FT
            punt_fg = player.position in ['PG', 'SG'] and random.random() < 0.2  # Guards take more 3s
            punt_ast = player.position in ['C', 'PF'] and random.random() < 0.4  # Bigs don't assist much
            punt_3pm = player.position in ['C', 'PF'] and random.random() < 0.5  # Bigs don't shoot 3s
            
            # Sleeper/breakout potential (younger players, late ADP)
            is_sleeper = adp > 80 and random.random() < 0.3
            is_breakout = player.name in [
                'Paolo Banchero', 'Chet Holmgren', 'Alperen Sengun', 'Walker Kessler',
                'Scottie Barnes', 'Evan Mobley', 'Franz Wagner', 'Jalen Williams',
                'Amen Thompson', 'Ausar Thompson', 'Scoot Henderson', 'Victor Wembanyama'
            ]
            
            # Injury risk assessment
            injury_risks = {
                'Zion Williamson': 'High',
                'Kawhi Leonard': 'High', 
                'Anthony Davis': 'Medium',
                'Joel Embiid': 'Medium',
                'Kristaps Porzingis': 'Medium',
                'Karl-Anthony Towns': 'Medium',
                'Ja Morant': 'Medium',  # Suspension/injury history
                'LeBron James': 'Medium',  # Age
                'Chris Paul': 'High',  # Age + history
                'Stephen Curry': 'Low',
                'Kevin Durant': 'Medium'
            }
            injury_risk = injury_risks.get(player.name, 'Low')
            
            fantasy = FantasyData(
                player_id=player.id,
                season="2024-25",
                adp_rank=adp,
                adp_round=adp_round,
                yahoo_rank=adp + random.randint(-5, 5),
                espn_rank=adp + random.randint(-5, 5),
                keeper_round=keeper_round,
                dynasty_value=adp + random.randint(-10, 10),
                projected_ppg=round(ppg, 1),
                projected_rpg=round(rpg, 1),
                projected_apg=round(apg, 1),
                projected_spg=round(random.uniform(0.5, 2.0), 1),
                projected_bpg=round(random.uniform(0.3, 2.5) if player.position in ['C', 'PF'] else random.uniform(0.1, 0.8), 1),
                projected_fg_pct=round(random.uniform(0.42, 0.55) if player.position in ['C', 'PF'] else random.uniform(0.40, 0.48), 3),
                projected_ft_pct=round(random.uniform(0.65, 0.90), 3),
                projected_3pm=round(random.uniform(0.5, 3.5) if player.position in ['PG', 'SG', 'SF'] else random.uniform(0.0, 1.5), 1),
                projected_fantasy_ppg=round(fantasy_ppg, 1),
                punt_ft_fit=punt_ft,
                punt_fg_fit=punt_fg,
                punt_ast_fit=punt_ast,
                punt_3pm_fit=punt_3pm,
                sleeper_score=random.uniform(0.6, 0.9) if is_sleeper else random.uniform(0.1, 0.5),
                breakout_candidate=is_breakout,
                injury_risk=injury_risk,
                consistency_rating=random.uniform(0.65, 0.95) if adp <= 30 else random.uniform(0.45, 0.75)
            )
            self.session.add(fantasy)
        
        self.session.commit()
        logger.info(f"Loaded fantasy data for {len(self.players_data)} players")
    
    def verify_data(self):
        """Verify all data was loaded correctly"""
        logger.info("\nVerifying loaded data...")
        
        teams_count = self.session.query(Team).count()
        players_count = self.session.query(Player).count()
        games_count = self.session.query(Game).count()
        stats_count = self.session.query(GameStats).count()
        fantasy_count = self.session.query(FantasyData).count()
        
        print("\n" + "="*60)
        print("DATA LOADING SUMMARY")
        print("="*60)
        print(f"[OK] Teams loaded: {teams_count}")
        print(f"[OK] Players loaded: {players_count}")
        print(f"[OK] Games loaded: {games_count}")
        print(f"[OK] Game stats loaded: {stats_count}")
        print(f"[OK] Fantasy data loaded: {fantasy_count}")
        
        # Sample queries to verify
        print("\n" + "-"*60)
        print("SAMPLE DATA VERIFICATION")
        print("-"*60)
        
        # Top 5 players by ADP
        top_players = self.session.query(Player, FantasyData)\
            .join(FantasyData)\
            .order_by(FantasyData.adp_rank)\
            .limit(5)\
            .all()
        
        print("\nTop 5 Players by ADP:")
        for player, fantasy in top_players:
            print(f"  {fantasy.adp_rank}. {player.name} ({player.team}) - "
                  f"Projected: {fantasy.projected_ppg} PPG, {fantasy.projected_fantasy_ppg} FP")
        
        # Sleeper candidates
        sleepers = self.session.query(Player, FantasyData)\
            .join(FantasyData)\
            .filter(FantasyData.sleeper_score > 0.7)\
            .limit(5)\
            .all()
        
        print("\nTop Sleeper Candidates:")
        for player, fantasy in sleepers:
            print(f"  {player.name} (ADP: {fantasy.adp_rank}) - Sleeper Score: {fantasy.sleeper_score:.2f}")
        
        # Breakout candidates
        breakouts = self.session.query(Player, FantasyData)\
            .join(FantasyData)\
            .filter(FantasyData.breakout_candidate == True)\
            .limit(5)\
            .all()
        
        print("\nBreakout Candidates:")
        for player, fantasy in breakouts:
            print(f"  {player.name} (ADP: {fantasy.adp_rank})")
        
        print("\n" + "="*60)
        print("[SUCCESS] All data loaded successfully for 2024-25 draft prep!")
        print("="*60)

def main():
    """Main function to load all data"""
    print("="*60)
    print("SPORTSBRAIN POSTGRESQL DATA LOADER")
    print("Loading 2024-25 Fantasy Basketball Draft Data")
    print("="*60)
    
    loader = DraftDataLoader()
    
    try:
        # Load data in order
        loader.load_teams()
        loader.load_players()
        loader.load_reference_games()
        loader.load_game_stats()
        loader.load_fantasy_data()
        
        # Verify everything loaded
        loader.verify_data()
        
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        loader.session.rollback()
        raise
    finally:
        loader.session.close()

if __name__ == "__main__":
    main()