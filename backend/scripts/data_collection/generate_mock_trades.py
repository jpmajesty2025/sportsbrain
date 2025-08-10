"""
Generate mock trade documents for the 2024-25 NBA season
Creates multiple document variations from base trades to reach 250+ documents
"""
import sys
import os
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import hashlib

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradeDocumentGenerator:
    def __init__(self):
        self.base_trades = self._create_base_trades()
        self.generated_documents = []
        
    def _create_base_trades(self) -> List[Dict]:
        """Create 15 realistic base trades for 2024-25 season"""
        trades = [
            {
                "trade_id": "trade_2024_001",
                "date": "2024-07-01",
                "headline": "Damian Lillard Traded to Miami Heat",
                "teams": ["POR", "MIA", "PHI"],
                "players": {
                    "to_MIA": ["Damian Lillard"],
                    "to_POR": ["Tyler Herro", "Duncan Robinson", "2025 First Round Pick"],
                    "to_PHI": ["Jusuf Nurkic"],
                    "from_PHI": ["Tobias Harris"]
                },
                "type": "blockbuster",
                "fantasy_impact": {
                    "Damian Lillard": {"usage": -2.5, "assists": 1.2, "value": 0.05},
                    "Tyler Herro": {"usage": 4.5, "shots": 3.2, "value": 0.25},
                    "Jimmy Butler": {"usage": -3.0, "assists": 0.8, "value": -0.10},
                    "Bam Adebayo": {"usage": -1.0, "rebounds": 0.5, "value": 0.0}
                }
            },
            {
                "trade_id": "trade_2024_002",
                "date": "2024-07-15",
                "headline": "Pascal Siakam Joins Indiana Pacers",
                "teams": ["TOR", "IND"],
                "players": {
                    "to_IND": ["Pascal Siakam"],
                    "to_TOR": ["Bruce Brown", "Jordan Nwora", "2024 First Round Pick", "2026 First Round Pick"]
                },
                "type": "star_move",
                "fantasy_impact": {
                    "Pascal Siakam": {"usage": 2.0, "assists": 0.5, "value": 0.10},
                    "Tyrese Haliburton": {"usage": -2.0, "assists": -0.5, "value": -0.05},
                    "Scottie Barnes": {"usage": 3.5, "assists": 1.5, "value": 0.20}
                }
            },
            {
                "trade_id": "trade_2024_003",
                "date": "2024-12-15",
                "headline": "Zach LaVine Traded to Lakers",
                "teams": ["CHI", "LAL"],
                "players": {
                    "to_LAL": ["Zach LaVine"],
                    "to_CHI": ["Rui Hachimura", "Gabe Vincent", "2025 First Round Pick", "2027 First Round Pick"]
                },
                "type": "contender_addition",
                "fantasy_impact": {
                    "Zach LaVine": {"usage": -3.5, "efficiency": 2.0, "value": -0.05},
                    "LeBron James": {"usage": -2.0, "assists": 1.0, "value": 0.0},
                    "Anthony Davis": {"usage": 0.5, "rebounds": 0.3, "value": 0.05},
                    "DeMar DeRozan": {"usage": 3.0, "shots": 2.5, "value": 0.15}
                }
            },
            {
                "trade_id": "trade_2024_004",
                "date": "2024-12-20",
                "headline": "OG Anunoby to New York Knicks",
                "teams": ["TOR", "NYK"],
                "players": {
                    "to_NYK": ["OG Anunoby", "Precious Achiuwa"],
                    "to_TOR": ["RJ Barrett", "Immanuel Quickley", "2024 Second Round Pick"]
                },
                "type": "win_now",
                "fantasy_impact": {
                    "OG Anunoby": {"usage": -1.0, "defensive_stats": 0.5, "value": 0.05},
                    "Jalen Brunson": {"usage": 0.5, "assists": 0.3, "value": 0.05},
                    "Julius Randle": {"usage": -1.0, "efficiency": 1.0, "value": 0.0},
                    "RJ Barrett": {"usage": 4.0, "shots": 3.0, "value": 0.20}
                }
            },
            {
                "trade_id": "trade_2024_005",
                "date": "2025-01-15",
                "headline": "Karl-Anthony Towns Shakes Up Eastern Conference",
                "teams": ["MIN", "BKN"],
                "players": {
                    "to_BKN": ["Karl-Anthony Towns"],
                    "to_MIN": ["Mikal Bridges", "Nic Claxton", "2025 First Round Pick"]
                },
                "type": "franchise_shift",
                "fantasy_impact": {
                    "Karl-Anthony Towns": {"usage": 1.5, "rebounds": -0.5, "value": 0.10},
                    "Anthony Edwards": {"usage": 3.0, "shots": 2.5, "value": 0.20},
                    "Rudy Gobert": {"rebounds": 1.5, "blocks": 0.3, "value": 0.10}
                }
            },
            {
                "trade_id": "trade_2024_006",
                "date": "2025-01-20",
                "headline": "Dejounte Murray Heads to Lakers",
                "teams": ["ATL", "LAL"],
                "players": {
                    "to_LAL": ["Dejounte Murray"],
                    "to_ATL": ["D'Angelo Russell", "Jarred Vanderbilt", "2026 First Round Pick"]
                },
                "type": "playoff_push",
                "fantasy_impact": {
                    "Dejounte Murray": {"usage": -2.0, "assists": -1.0, "value": -0.10},
                    "Trae Young": {"usage": 2.5, "assists": 1.5, "value": 0.15},
                    "LeBron James": {"usage": -1.5, "assists": -0.5, "value": -0.05}
                }
            },
            {
                "trade_id": "trade_2024_007",
                "date": "2025-02-01",
                "headline": "Myles Turner Bolsters Boston's Frontcourt",
                "teams": ["IND", "BOS"],
                "players": {
                    "to_BOS": ["Myles Turner"],
                    "to_IND": ["Robert Williams III", "Payton Pritchard", "2025 First Round Pick"]
                },
                "type": "deadline_deal",
                "fantasy_impact": {
                    "Myles Turner": {"usage": -1.0, "blocks": 0.5, "value": 0.05},
                    "Jayson Tatum": {"usage": 0.5, "efficiency": 1.0, "value": 0.05},
                    "Kristaps Porzingis": {"minutes": -3.0, "value": -0.10}
                }
            },
            {
                "trade_id": "trade_2024_008",
                "date": "2025-02-06",
                "headline": "Brandon Ingram Joins Sacramento Kings",
                "teams": ["NOP", "SAC"],
                "players": {
                    "to_SAC": ["Brandon Ingram"],
                    "to_NOP": ["Harrison Barnes", "Davion Mitchell", "2025 First Round Pick", "2027 First Round Pick"]
                },
                "type": "small_market_move",
                "fantasy_impact": {
                    "Brandon Ingram": {"usage": -1.5, "assists": 0.5, "value": 0.0},
                    "De'Aaron Fox": {"usage": -2.0, "assists": -0.5, "value": -0.05},
                    "Domantas Sabonis": {"usage": 0.5, "assists": 0.5, "value": 0.05},
                    "Zion Williamson": {"usage": 3.5, "shots": 3.0, "value": 0.25}
                }
            },
            {
                "trade_id": "trade_2024_009",
                "date": "2025-02-08",
                "headline": "Clippers Trade Paul George to Philadelphia",
                "teams": ["LAC", "PHI"],
                "players": {
                    "to_PHI": ["Paul George"],
                    "to_LAC": ["Tobias Harris", "De'Anthony Melton", "2025 First Round Pick", "2026 Pick Swap"]
                },
                "type": "championship_pursuit",
                "fantasy_impact": {
                    "Paul George": {"usage": 1.0, "assists": 0.5, "value": 0.10},
                    "Joel Embiid": {"usage": -2.0, "efficiency": 1.5, "value": 0.05},
                    "Kawhi Leonard": {"usage": 3.0, "shots": 2.5, "value": 0.20},
                    "James Harden": {"usage": 2.0, "assists": 1.0, "value": 0.15}
                }
            },
            {
                "trade_id": "trade_2024_010",
                "date": "2024-08-10",
                "headline": "Darius Garland Traded to San Antonio",
                "teams": ["CLE", "SAS"],
                "players": {
                    "to_SAS": ["Darius Garland"],
                    "to_CLE": ["Keldon Johnson", "Zach Collins", "2025 First Round Pick", "2027 First Round Pick"]
                },
                "type": "rebuild_move",
                "fantasy_impact": {
                    "Darius Garland": {"usage": 3.0, "assists": 2.0, "value": 0.25},
                    "Victor Wembanyama": {"usage": -1.0, "assists": 0.5, "value": 0.05},
                    "Donovan Mitchell": {"usage": 2.5, "assists": 1.0, "value": 0.15}
                }
            },
            {
                "trade_id": "trade_2024_011",
                "date": "2024-09-15",
                "headline": "Klay Thompson Signs-and-Trade to Orlando",
                "teams": ["GSW", "ORL"],
                "players": {
                    "to_ORL": ["Klay Thompson"],
                    "to_GSW": ["Jonathan Isaac", "Cole Anthony", "2025 First Round Pick"]
                },
                "type": "veteran_move",
                "fantasy_impact": {
                    "Klay Thompson": {"usage": 2.0, "shots": 2.5, "value": 0.15},
                    "Paolo Banchero": {"usage": -1.5, "efficiency": 1.0, "value": 0.05},
                    "Stephen Curry": {"usage": 2.0, "shots": 1.5, "value": 0.10}
                }
            },
            {
                "trade_id": "trade_2024_012",
                "date": "2024-10-01",
                "headline": "Jaren Jackson Jr. to Golden State",
                "teams": ["MEM", "GSW"],
                "players": {
                    "to_GSW": ["Jaren Jackson Jr."],
                    "to_MEM": ["Andrew Wiggins", "Moses Moody", "2025 First Round Pick", "2027 First Round Pick"]
                },
                "type": "defensive_upgrade",
                "fantasy_impact": {
                    "Jaren Jackson Jr.": {"usage": -1.0, "blocks": 0.3, "value": 0.05},
                    "Stephen Curry": {"usage": -0.5, "efficiency": 1.0, "value": 0.05},
                    "Ja Morant": {"usage": 1.5, "assists": 0.5, "value": 0.10}
                }
            },
            {
                "trade_id": "trade_2024_013",
                "date": "2024-11-20",
                "headline": "CJ McCollum Returns to Portland",
                "teams": ["NOP", "POR"],
                "players": {
                    "to_POR": ["CJ McCollum"],
                    "to_NOP": ["Anfernee Simons", "Jusuf Nurkic", "2025 Second Round Pick"]
                },
                "type": "homecoming",
                "fantasy_impact": {
                    "CJ McCollum": {"usage": 2.5, "shots": 2.0, "value": 0.15},
                    "Scoot Henderson": {"usage": -2.0, "assists": -0.5, "value": -0.10},
                    "Zion Williamson": {"usage": 1.5, "efficiency": 1.0, "value": 0.10}
                }
            },
            {
                "trade_id": "trade_2024_014",
                "date": "2024-12-01",
                "headline": "Rudy Gobert Traded to Dallas",
                "teams": ["MIN", "DAL"],
                "players": {
                    "to_DAL": ["Rudy Gobert"],
                    "to_MIN": ["Christian Wood", "Richaun Holmes", "2025 First Round Pick", "2026 First Round Pick"]
                },
                "type": "defensive_anchor",
                "fantasy_impact": {
                    "Rudy Gobert": {"rebounds": -1.0, "blocks": -0.2, "value": -0.05},
                    "Luka Dončić": {"usage": -0.5, "assists": 0.5, "value": 0.05},
                    "Karl-Anthony Towns": {"rebounds": 2.0, "blocks": 0.5, "value": 0.15}
                }
            },
            {
                "trade_id": "trade_2024_015",
                "date": "2025-01-25",
                "headline": "Trae Young Shocks NBA, Heads to Spurs",
                "teams": ["ATL", "SAS"],
                "players": {
                    "to_SAS": ["Trae Young"],
                    "to_ATL": ["Devin Vassell", "Tre Jones", "2025 First Round Pick", "2026 First Round Pick", "2027 First Round Pick"]
                },
                "type": "franchise_altering",
                "fantasy_impact": {
                    "Trae Young": {"usage": -2.0, "assists": -1.5, "value": -0.15},
                    "Victor Wembanyama": {"usage": -2.0, "efficiency": 2.0, "value": 0.10},
                    "Dejounte Murray": {"usage": 4.0, "assists": 3.0, "value": 0.35}
                }
            }
        ]
        return trades
    
    def _generate_trade_document(self, trade: Dict, doc_type: str, variation: int = 0) -> Dict:
        """Generate a specific type of document for a trade"""
        
        doc_id = hashlib.md5(f"{trade['trade_id']}_{doc_type}_{variation}".encode()).hexdigest()[:12]
        
        base_doc = {
            "doc_id": doc_id,
            "trade_id": trade['trade_id'],
            "doc_type": doc_type,
            "source": random.choice(["reddit", "twitter", "espn", "the_athletic", "bleacher_report"]),
            "date_posted": (datetime.strptime(trade['date'], "%Y-%m-%d") + timedelta(days=variation)).isoformat(),
            "trade_date": trade['date'],
            "teams_involved": trade['teams'],
            "headline": trade['headline']
        }
        
        if doc_type == "breaking_news":
            return self._create_breaking_news(trade, base_doc)
        elif doc_type == "woj_tweet":
            return self._create_woj_tweet(trade, base_doc)
        elif doc_type == "reddit_thread":
            return self._create_reddit_thread(trade, base_doc)
        elif doc_type == "player_impact":
            return self._create_player_impact(trade, base_doc, variation)
        elif doc_type == "fantasy_analysis":
            return self._create_fantasy_analysis(trade, base_doc)
        elif doc_type == "team_perspective":
            return self._create_team_perspective(trade, base_doc, variation)
        elif doc_type == "winners_losers":
            return self._create_winners_losers(trade, base_doc)
        elif doc_type == "community_reaction":
            return self._create_community_reaction(trade, base_doc)
        elif doc_type == "expert_breakdown":
            return self._create_expert_breakdown(trade, base_doc)
        elif doc_type == "one_month_later":
            return self._create_one_month_later(trade, base_doc)
        else:
            return base_doc
    
    def _create_breaking_news(self, trade: Dict, base_doc: Dict) -> Dict:
        """Create initial breaking news document"""
        doc = base_doc.copy()
        doc["title"] = f"BREAKING: {trade['headline']}"
        doc["text"] = f"""
        BREAKING NEWS: The NBA landscape has shifted dramatically with the announcement that {trade['headline']}.
        
        In a {trade['type'].replace('_', ' ')} move, the following teams are involved: {', '.join(trade['teams'])}.
        
        Key players on the move:
        {self._format_player_movement(trade)}
        
        This trade is expected to have significant implications for the upcoming season, particularly 
        for fantasy basketball managers who will need to reassess player values.
        
        Initial reactions from around the league suggest this could be one of the most impactful trades
        of the 2024-25 season. Stay tuned for more analysis as details emerge.
        """
        doc["metadata"] = {
            "sentiment": random.uniform(0.6, 0.9),
            "urgency": "high",
            "credibility": 0.95
        }
        return doc
    
    def _create_woj_tweet(self, trade: Dict, base_doc: Dict) -> Dict:
        """Create Woj-style tweet document"""
        doc = base_doc.copy()
        doc["title"] = f"Woj: {trade['headline']}"
        doc["source"] = "twitter"
        doc["text"] = f"""
        Sources: {trade['headline']}. Deal includes multiple players and draft compensation.
        {', '.join(trade['teams'])} finalizing deal that will reshape their rosters for 2024-25 season.
        Fantasy impact expected to be significant. Full details emerging.
        """
        doc["metadata"] = {
            "author": "Adrian Wojnarowski",
            "retweets": random.randint(5000, 50000),
            "likes": random.randint(10000, 100000),
            "verified": True
        }
        return doc
    
    def _create_reddit_thread(self, trade: Dict, base_doc: Dict) -> Dict:
        """Create Reddit discussion thread"""
        doc = base_doc.copy()
        doc["title"] = f"[Wojnarowski] {trade['headline']} - r/fantasybball Discussion"
        doc["source"] = "reddit"
        doc["text"] = f"""
        **[Wojnarowski] {trade['headline']}**
        
        Holy shit, this actually happened! Let's discuss the fantasy implications.
        
        **My Initial Takes:**
        
        Winners from a fantasy perspective:
        {self._get_fantasy_winners(trade)}
        
        Losers from a fantasy perspective:
        {self._get_fantasy_losers(trade)}
        
        What do you all think? Who should I be targeting/trading away?
        
        **EDIT**: Wow, this blew up! Thanks for the awards!
        
        **EDIT 2**: For those asking about keeper league implications, I think this makes 
        some of these players much more valuable long-term.
        """
        doc["metadata"] = {
            "subreddit": "r/fantasybball",
            "upvotes": random.randint(500, 3000),
            "comments": random.randint(50, 500),
            "awards": random.randint(0, 10),
            "author_flair": random.choice(["10 Team H2H", "12 Team 9CAT", "Dynasty League", "Points League"])
        }
        return doc
    
    def _create_player_impact(self, trade: Dict, base_doc: Dict, player_index: int) -> Dict:
        """Create player-specific impact analysis"""
        doc = base_doc.copy()
        
        # Get a specific player from the trade
        all_players = []
        for players_list in trade['players'].values():
            if isinstance(players_list, list):
                all_players.extend([p for p in players_list if "Pick" not in p])
        
        if player_index >= len(all_players):
            player_index = 0
        
        player = all_players[player_index] if all_players else "Unknown Player"
        
        doc["title"] = f"How {trade['headline'].split()[0]} Trade Affects {player}'s Fantasy Value"
        doc["text"] = f"""
        **Deep Dive: {player}'s Fantasy Outlook Post-Trade**
        
        The recent trade sending players to new destinations has significant implications for {player}'s 
        fantasy basketball value. Let's break down what this means for fantasy managers.
        
        **Statistical Impact:**
        {self._get_player_stat_impact(trade, player)}
        
        **Usage Rate Changes:**
        With this new situation, we expect {player}'s usage rate to shift significantly. 
        The presence of new teammates and different offensive systems will create new opportunities.
        
        **Category Analysis:**
        - Points: Expected to {random.choice(['increase', 'decrease', 'remain stable'])}
        - Assists: Likely {random.choice(['up', 'down', 'unchanged'])} due to role change
        - Rebounds: Should see {random.choice(['minor', 'major', 'no'])} impact
        - Defensive stats: {random.choice(['Improved', 'Diminished', 'Steady'])} outlook
        
        **Fantasy Recommendation:**
        {random.choice(['BUY LOW', 'SELL HIGH', 'HOLD', 'MONITOR CLOSELY'])} - 
        This trade {random.choice(['significantly improves', 'slightly improves', 'negatively impacts', 'minimally affects'])} 
        {player}'s rest-of-season outlook.
        
        **Dynasty/Keeper Implications:**
        Long-term, this move {random.choice(['elevates', 'maintains', 'diminishes'])} {player}'s keeper value.
        """
        
        doc["metadata"] = {
            "player_focus": player,
            "impact_score": random.uniform(-0.3, 0.3),
            "confidence": random.uniform(0.6, 0.9)
        }
        return doc
    
    def _create_fantasy_analysis(self, trade: Dict, base_doc: Dict) -> Dict:
        """Create comprehensive fantasy analysis"""
        doc = base_doc.copy()
        doc["title"] = f"Fantasy Basketball Analysis: Breaking Down the {trade['headline'].split()[0]} Trade"
        doc["text"] = f"""
        **Comprehensive Fantasy Impact Analysis**
        
        The {trade['headline']} will have ripple effects across fantasy basketball leagues. 
        Here's everything you need to know:
        
        **Immediate Impacts:**
        {self._get_immediate_impacts(trade)}
        
        **Rest of Season Projections:**
        Based on this trade, here are updated ROS rankings shifts:
        {self._get_ros_projections(trade)}
        
        **DFS Implications:**
        For daily fantasy players, this trade creates several interesting opportunities:
        - Target these players in good matchups
        - Fade these players initially as they adjust
        - Stack opportunities with new teammate combinations
        
        **Category League Impacts:**
        - Punt FT%: {random.choice(['More viable', 'Less viable', 'Unchanged'])}
        - Punt AST: {random.choice(['More viable', 'Less viable', 'Unchanged'])}
        - Balanced builds: {random.choice(['Slightly affected', 'Majorly affected', 'Minimally affected'])}
        
        **Action Items for Fantasy Managers:**
        1. {random.choice(['Immediately try to trade for affected players', 'Wait for values to settle', 'Make no rash moves'])}
        2. {random.choice(['Adjust waiver priorities', 'Hold current roster', 'Look for buy-low opportunities'])}
        3. {random.choice(['Monitor first few games closely', 'Make immediate roster moves', 'Prepare contingency plans'])}
        """
        doc["metadata"] = {
            "analysis_depth": "comprehensive",
            "categories_affected": random.randint(3, 9)
        }
        return doc
    
    def _create_team_perspective(self, trade: Dict, base_doc: Dict, team_index: int) -> Dict:
        """Create team-specific perspective"""
        doc = base_doc.copy()
        team = trade['teams'][team_index % len(trade['teams'])]
        doc["title"] = f"{team} Perspective: Why This Trade Makes Sense"
        doc["text"] = f"""
        **From the {team} Front Office: Strategic Analysis**
        
        The {team} organization has made a bold move in this trade. Here's why it works for them:
        
        **Roster Construction:**
        This trade addresses key needs for the {team}, particularly in terms of 
        {random.choice(['shooting', 'defense', 'playmaking', 'rebounding', 'depth'])}.
        
        **Cap Implications:**
        Financially, this move {random.choice(['creates flexibility', 'uses cap space wisely', 'sets up future moves'])}.
        
        **Championship Window:**
        The {team} are clearly {random.choice(['in win-now mode', 'building for the future', 'maintaining flexibility'])}.
        
        **Fantasy Implications for {team} Players:**
        - Increased opportunities for role players
        - Shifted offensive hierarchy
        - New lineup combinations to monitor
        
        **What This Means for Fantasy:**
        {team} games should now be {random.choice(['higher scoring', 'more defensive', 'more balanced'])}. 
        Target {team} players in {random.choice(['DFS', 'season-long', 'dynasty'])} formats.
        """
        doc["metadata"] = {
            "team_focus": team,
            "organizational_impact": random.choice(["positive", "negative", "neutral"])
        }
        return doc
    
    def _create_winners_losers(self, trade: Dict, base_doc: Dict) -> Dict:
        """Create winners and losers analysis"""
        doc = base_doc.copy()
        doc["title"] = f"Trade Winners and Losers: {trade['headline'].split()[0]} Deal"
        doc["text"] = f"""
        **Winners and Losers from the {trade['headline']}**
        
        **WINNERS:**
        
        🏆 **Biggest Winner:** {self._get_biggest_winner(trade)}
        - Why: Significantly increased role and opportunity
        - Fantasy impact: +{random.randint(3, 8)} spots in rankings
        
        📈 **Also Winning:**
        {self._get_other_winners(trade)}
        
        **LOSERS:**
        
        📉 **Biggest Loser:** {self._get_biggest_loser(trade)}
        - Why: Reduced role and usage
        - Fantasy impact: -{random.randint(3, 8)} spots in rankings
        
        📊 **Also Losing Value:**
        {self._get_other_losers(trade)}
        
        **NEUTRAL:**
        Some players see minimal impact from this trade and maintain their current value.
        
        **The Verdict:**
        Overall, this trade creates {random.randint(3, 7)} buy-low opportunities and 
        {random.randint(2, 5)} sell-high situations for savvy fantasy managers.
        """
        doc["metadata"] = {
            "analysis_type": "winners_losers",
            "clarity": random.uniform(0.7, 0.95)
        }
        return doc
    
    def _create_community_reaction(self, trade: Dict, base_doc: Dict) -> Dict:
        """Create community reaction compilation"""
        doc = base_doc.copy()
        doc["title"] = f"NBA Twitter Reacts to {trade['headline']}"
        doc["source"] = "twitter"
        doc["text"] = f"""
        **Best Reactions from NBA Twitter:**
        
        @FantasyGuru: "This trade just broke my league. {random.choice(['RIP', 'WOW', 'HISTORIC'])}"
        
        @NBAAnalyst: "People are sleeping on how this affects role players. Watch for breakout candidates."
        
        @DynastyDan: "In dynasty leagues, this is {random.choice(['massive', 'huge', 'game-changing'])}. 
        Adjust your rankings accordingly."
        
        @StatsMatter: "The numbers say this trade {random.choice(['heavily favors', 'slightly favors', 'is even for'])} 
        {random.choice(trade['teams'])}"
        
        @CasualFan: "{random.choice(['I cant believe this happened', 'Called it!', 'This is why we F5'])}"
        
        @PodcastHost: "Emergency pod dropping tonight to break this down!"
        
        **Reddit Hot Takes:**
        - "This is either genius or the worst trade ever, no in between"
        - "Fantasy managers in shambles"
        - "Just traded for one of these guys yesterday, AMA"
        
        **Overall Sentiment:** {random.choice(['Shocked', 'Excited', 'Confused', 'Mixed'])}
        """
        doc["metadata"] = {
            "viral_score": random.randint(1000, 10000),
            "engagement_rate": random.uniform(0.05, 0.15)
        }
        return doc
    
    def _create_expert_breakdown(self, trade: Dict, base_doc: Dict) -> Dict:
        """Create expert analysis document"""
        doc = base_doc.copy()
        doc["title"] = f"Expert Breakdown: {trade['headline']} - A Deep Dive"
        doc["source"] = "the_athletic"
        doc["text"] = f"""
        **Expert Analysis by Senior NBA Writer**
        
        The {trade['headline']} represents a significant shift in the NBA landscape. Let me break down 
        the nuances that casual fans might miss:
        
        **Strategic Motivations:**
        {random.choice(trade['teams'])} initiated this trade to address their 
        {random.choice(['offensive struggles', 'defensive deficiencies', 'depth issues', 'championship aspirations'])}.
        
        **Scheme Fit Analysis:**
        From a basketball perspective, this trade makes sense because:
        - Offensive system compatibility: {random.choice(['Excellent', 'Good', 'Questionable'])}
        - Defensive scheme fit: {random.choice(['Perfect', 'Adequate', 'Concerning'])}
        - Overall roster balance: {random.choice(['Improved', 'Maintained', 'Worsened'])}
        
        **Fantasy Basketball Deep Dive:**
        The fantasy implications go beyond surface-level usage changes:
        
        1. **Efficiency Metrics:** Expect {random.choice(['improved', 'decreased', 'maintained'])} efficiency
        2. **Pace Factors:** Team pace likely to {random.choice(['increase', 'decrease', 'stay stable'])}
        3. **Rotation Patterns:** New rotations will {random.choice(['benefit', 'hurt', 'not affect'])} fantasy value
        
        **Historical Context:**
        Similar trades in the past have resulted in {random.choice(['mixed results', 'clear success', 'notable failures'])}.
        
        **Grade:** {random.choice(['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+'])}
        """
        doc["metadata"] = {
            "author_credentials": "15+ years covering NBA",
            "analysis_depth": "expert",
            "paywall": True
        }
        return doc
    
    def _create_one_month_later(self, trade: Dict, base_doc: Dict) -> Dict:
        """Create retrospective analysis document"""
        doc = base_doc.copy()
        one_month_date = (datetime.strptime(trade['date'], "%Y-%m-%d") + timedelta(days=30)).strftime("%Y-%m-%d")
        doc["date_posted"] = one_month_date
        doc["title"] = f"One Month Later: Revisiting the {trade['headline'].split()[0]} Trade"
        doc["text"] = f"""
        **30 Days Post-Trade: What We've Learned**
        
        It's been a month since {trade['headline']}, and we now have enough data to properly evaluate 
        the trade's impact on fantasy basketball.
        
        **Statistical Changes (Actual vs. Projected):**
        {self._get_one_month_stats(trade)}
        
        **Biggest Surprises:**
        1. {random.choice(['Role player emergence', 'Unexpected chemistry issues', 'Better fit than expected'])}
        2. {random.choice(['Usage distribution', 'Defensive improvements', 'Offensive struggles'])}
        3. {random.choice(['Injury concerns', 'Rotation changes', 'Coaching adjustments'])}
        
        **Fantasy Impact Assessment:**
        - Initial projections: {random.choice(['Too optimistic', 'Too pessimistic', 'Spot on'])}
        - Actual impact: {random.choice(['Better than expected', 'Worse than expected', 'As predicted'])}
        - ROS outlook: {random.choice(['Bullish', 'Bearish', 'Neutral'])}
        
        **Lessons Learned:**
        This trade teaches us that {random.choice([
            'team fit matters more than talent',
            'usage rates dont always translate linearly',
            'system changes take time to manifest',
            'chemistry is unpredictable'
        ])}.
        
        **Updated Recommendations:**
        Based on one month of data, fantasy managers should {random.choice([
            'continue buying low on affected players',
            'start selling high while values peak',
            'hold and reassess in another month'
        ])}.
        """
        doc["metadata"] = {
            "retrospective": True,
            "sample_size": "10-15 games",
            "confidence": random.uniform(0.7, 0.9)
        }
        return doc
    
    # Helper methods
    def _format_player_movement(self, trade: Dict) -> str:
        movements = []
        for destination, players in trade['players'].items():
            team = destination.replace('to_', '').replace('from_', '')
            player_list = [p for p in players if isinstance(p, str) and "Pick" not in p]
            if player_list:
                movements.append(f"• To {team}: {', '.join(player_list[:2])}")
        return '\n'.join(movements)
    
    def _get_fantasy_winners(self, trade: Dict) -> str:
        winners = []
        for player, impact in list(trade['fantasy_impact'].items())[:3]:
            if impact['value'] > 0:
                winners.append(f"• {player}: +{impact['value']*100:.0f}% value")
        return '\n'.join(winners) if winners else "• Still analyzing..."
    
    def _get_fantasy_losers(self, trade: Dict) -> str:
        losers = []
        for player, impact in trade['fantasy_impact'].items():
            if impact['value'] < 0:
                losers.append(f"• {player}: {impact['value']*100:.0f}% value")
        return '\n'.join(losers) if losers else "• Minimal negative impact"
    
    def _get_player_stat_impact(self, trade: Dict, player: str) -> str:
        if player in trade['fantasy_impact']:
            impact = trade['fantasy_impact'][player]
            return f"""
            - Usage Rate: {impact.get('usage', 0):+.1f}%
            - Scoring: Projected {impact.get('usage', 0)*0.8:+.1f} PPG
            - Assists: {impact.get('assists', 0):+.1f} APG
            - Overall Fantasy Value: {impact.get('value', 0)*100:+.0f}%
            """
        return "Impact data still being analyzed"
    
    def _get_immediate_impacts(self, trade: Dict) -> str:
        impacts = []
        for player, data in list(trade['fantasy_impact'].items())[:4]:
            direction = "📈" if data['value'] > 0 else "📉" if data['value'] < 0 else "➡️"
            impacts.append(f"{direction} {player}: {abs(data['value']*100):.0f}% value change")
        return '\n'.join(impacts)
    
    def _get_ros_projections(self, trade: Dict) -> str:
        projections = []
        for player in list(trade['fantasy_impact'].keys())[:3]:
            old_rank = random.randint(10, 100)
            change = random.randint(-20, 20)
            new_rank = max(1, old_rank + change)
            projections.append(f"• {player}: #{old_rank} → #{new_rank}")
        return '\n'.join(projections)
    
    def _get_biggest_winner(self, trade: Dict) -> str:
        return max(trade['fantasy_impact'].items(), key=lambda x: x[1]['value'])[0]
    
    def _get_biggest_loser(self, trade: Dict) -> str:
        return min(trade['fantasy_impact'].items(), key=lambda x: x[1]['value'])[0]
    
    def _get_other_winners(self, trade: Dict) -> str:
        winners = [f"• {p}" for p, d in trade['fantasy_impact'].items() if d['value'] > 0.05]
        return '\n'.join(winners[1:4]) if len(winners) > 1 else "• Role players seeing increased opportunity"
    
    def _get_other_losers(self, trade: Dict) -> str:
        losers = [f"• {p}" for p, d in trade['fantasy_impact'].items() if d['value'] < -0.05]
        return '\n'.join(losers[1:4]) if len(losers) > 1 else "• Bench players losing minutes"
    
    def _get_one_month_stats(self, trade: Dict) -> str:
        stats = []
        for player in list(trade['fantasy_impact'].keys())[:3]:
            projected = random.uniform(40, 50)
            actual = projected + random.uniform(-5, 5)
            stats.append(f"• {player}: Projected {projected:.1f} → Actual {actual:.1f} fantasy PPG")
        return '\n'.join(stats)
    
    def generate_all_documents(self) -> List[Dict]:
        """Generate all trade documents"""
        documents = []
        doc_types = [
            "breaking_news",
            "woj_tweet", 
            "reddit_thread",
            "fantasy_analysis",
            "winners_losers",
            "community_reaction",
            "expert_breakdown",
            "one_month_later"
        ]
        
        for trade in self.base_trades:
            # Generate standard document types
            for doc_type in doc_types:
                doc = self._generate_trade_document(trade, doc_type)
                documents.append(doc)
            
            # Generate player-specific impacts (3 per trade)
            for i in range(3):
                doc = self._generate_trade_document(trade, "player_impact", i)
                documents.append(doc)
            
            # Generate team perspectives (2 per trade)
            for i in range(2):
                doc = self._generate_trade_document(trade, "team_perspective", i)
                documents.append(doc)
        
        logger.info(f"Generated {len(documents)} trade documents from {len(self.base_trades)} base trades")
        return documents
    
    def save_documents(self, documents: List[Dict]) -> str:
        """Save generated documents to JSON"""
        output_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'data', 'mock_trades'
        )
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, 'trade_documents_2024_25.json')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "season": "2024-25",
                "generated_at": datetime.now().isoformat(),
                "total_documents": len(documents),
                "base_trades": len(self.base_trades),
                "documents": documents
            }, f, indent=2)
        
        logger.info(f"Saved {len(documents)} documents to {output_file}")
        return output_file


def main():
    """Main function to generate all trade documents"""
    print("=" * 60)
    print("Trade Document Generation Script")
    print("=" * 60)
    
    generator = TradeDocumentGenerator()
    
    print(f"\nGenerating documents from {len(generator.base_trades)} base trades...")
    documents = generator.generate_all_documents()
    
    print(f"\n[OK] Generated {len(documents)} trade documents")
    print(f"  - Average {len(documents) // len(generator.base_trades)} documents per trade")
    
    print("\nSaving documents...")
    output_file = generator.save_documents(documents)
    
    print("\n" + "=" * 60)
    print("Trade Generation Complete!")
    print(f"[OK] {len(documents)} trade documents created")
    print(f"[OK] Saved to: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()