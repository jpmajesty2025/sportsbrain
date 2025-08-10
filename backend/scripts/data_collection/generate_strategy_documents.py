"""
Generate fantasy basketball strategy documents for various build types
Creates 200+ strategy documents for the sportsbrain_strategies collection
"""
import sys
import os
import json
import random
from datetime import datetime
from typing import List, Dict, Any
import hashlib

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StrategyDocumentGenerator:
    def __init__(self):
        self.strategy_count = 0
        self.player_pools = self._initialize_player_pools()
        
    def _initialize_player_pools(self) -> Dict[str, List[str]]:
        """Initialize player pools for different strategy types"""
        return {
            "punt_ft": {
                "elite": ["Giannis Antetokounmpo", "Zion Williamson", "Ben Simmons"],
                "good": ["Rudy Gobert", "Jarrett Allen", "Nic Claxton", "Jakob Poeltl"],
                "value": ["Kevon Looney", "Isaiah Stewart", "Jalen Duren", "Steven Adams"]
            },
            "punt_fg": {
                "elite": ["Damian Lillard", "Trae Young", "LaMelo Ball"],
                "good": ["Terry Rozier", "Jordan Poole", "Anfernee Simons", "Cole Anthony"],
                "value": ["Bones Hyland", "Malik Monk", "Gary Trent Jr.", "Kevin Huerter"]
            },
            "punt_ast": {
                "elite": ["Jayson Tatum", "Kevin Durant", "Anthony Davis"],
                "good": ["Myles Turner", "Brook Lopez", "Kristaps Porzingis", "Jaren Jackson Jr."],
                "value": ["Robert Williams III", "Mitchell Robinson", "Onyeka Okongwu"]
            },
            "punt_pts": {
                "elite": ["Draymond Green", "Marcus Smart", "Ben Simmons"],
                "good": ["Alex Caruso", "Dillon Brooks", "Matisse Thybulle", "Derrick White"],
                "value": ["Andre Drummond", "Kevon Looney", "Larry Nance Jr."]
            },
            "punt_3pm": {
                "elite": ["Giannis Antetokounmpo", "Zion Williamson", "Jimmy Butler"],
                "good": ["DeMar DeRozan", "Russell Westbrook", "Ben Simmons", "Ja Morant"],
                "value": ["Nic Claxton", "Clint Capela", "Jonas Valančiūnas"]
            },
            "punt_reb": {
                "elite": ["Stephen Curry", "Damian Lillard", "Kyrie Irving"],
                "good": ["Chris Paul", "Mike Conley", "Jrue Holiday", "Fred VanVleet"],
                "value": ["Immanuel Quickley", "Tre Jones", "Monte Morris"]
            },
            "punt_blk": {
                "elite": ["Luka Dončić", "Trae Young", "LaMelo Ball"],
                "good": ["Darius Garland", "Tyrese Maxey", "Jalen Brunson", "De'Aaron Fox"],
                "value": ["Dennis Schröder", "Coby White", "Jordan Clarkson"]
            },
            "punt_stl": {
                "elite": ["Nikola Jokić", "Karl-Anthony Towns", "Domantas Sabonis"],
                "good": ["Jonas Valančiūnas", "Alperen Sengun", "Jusuf Nurkić", "Nikola Vučević"],
                "value": ["Thomas Bryant", "Jalen Smith", "Isaiah Jackson"]
            },
            "punt_to": {
                "elite": ["Luka Dončić", "James Harden", "Russell Westbrook"],
                "good": ["Julius Randle", "Draymond Green", "LaMelo Ball", "Ben Simmons"],
                "value": ["Kyle Lowry", "Darius Garland", "Cade Cunningham"]
            },
            "balanced": {
                "elite": ["Nikola Jokić", "Joel Embiid", "Jayson Tatum", "Shai Gilgeous-Alexander"],
                "good": ["Anthony Edwards", "Paolo Banchero", "Scottie Barnes", "Evan Mobley"],
                "value": ["Franz Wagner", "Alperen Sengun", "Tyrese Maxey", "Desmond Bane"]
            }
        }
    
    def _generate_strategy_id(self, strategy_type: str, variation: int) -> str:
        """Generate unique strategy ID"""
        return hashlib.md5(f"{strategy_type}_{variation}_{self.strategy_count}".encode()).hexdigest()[:12]
    
    def generate_punt_strategy(self, punt_category: str, variation: int = 0) -> Dict:
        """Generate a punt strategy document"""
        self.strategy_count += 1
        
        player_pool = self.player_pools.get(f"punt_{punt_category.lower()}", self.player_pools["balanced"])
        
        # Create variations in player recommendations
        elite_players = random.sample(player_pool["elite"], min(2, len(player_pool["elite"])))
        good_players = random.sample(player_pool["good"], min(3, len(player_pool["good"])))
        value_players = random.sample(player_pool["value"], min(3, len(player_pool["value"])))
        
        doc = {
            "strategy_id": self._generate_strategy_id(f"punt_{punt_category}", variation),
            "title": f"Punt {punt_category.upper()}% Build Guide - Variation #{variation + 1}",
            "strategy_type": f"punt_{punt_category.lower()}",
            "difficulty": random.choice(["beginner", "intermediate", "advanced"]),
            "text": f"""
            **The Ultimate Punt {punt_category.upper()}% Strategy Guide for 2024-25**
            
            **Overview:**
            Punting {punt_category} is one of the most {random.choice(['popular', 'effective', 'underrated'])} strategies 
            in category leagues. By completely ignoring {punt_category}, you can focus on dominating the remaining 
            8 categories while your opponents waste resources trying to be competitive in all 9.
            
            **Why Punt {punt_category.upper()}%?**
            {self._get_punt_rationale(punt_category)}
            
            **Core Build Philosophy:**
            This build focuses on maximizing value in categories that typically oppose {punt_category}. 
            You'll be targeting players who excel everywhere except {punt_category}, which often makes them 
            undervalued in standard drafts.
            
            **Draft Strategy by Round:**
            
            **Round 1-2: Elite Foundation**
            Target: {', '.join(elite_players)}
            These players provide elite production across multiple categories while being weak in {punt_category}.
            Their {punt_category} weakness actually becomes a strength in this build, as it doesn't hurt you 
            while providing elite value elsewhere.
            
            **Round 3-5: Core Contributors**
            Target: {', '.join(good_players)}
            These players complement your elite picks perfectly. They maintain the punt while contributing 
            solid numbers in your target categories.
            
            **Round 6-9: Specialists**
            Look for players who excel in 1-2 categories while being particularly weak in {punt_category}.
            This is where you can find tremendous value as other managers avoid these "flawed" players.
            
            **Round 10+: Value Adds**
            Target: {', '.join(value_players)}
            Late-round players who fit the build and can provide streaming value or upside.
            
            **Categories You'll Dominate:**
            {self._get_strong_categories(punt_category)}
            
            **Categories to Monitor:**
            {self._get_competitive_categories(punt_category)}
            
            **Key Synergies:**
            {self._get_player_synergies(elite_players, good_players)}
            
            **Common Mistakes to Avoid:**
            1. Don't accidentally draft good {punt_category} players out of habit
            2. Don't panic if you're last in {punt_category} - that's the plan!
            3. Don't trade for players who hurt your punt strategy
            4. Don't overlook specialists who are elite in your target categories
            
            **Waiver Wire Strategy:**
            Focus on streaming players who:
            - Are terrible at {punt_category} (this is good!)
            - Excel in your target categories
            - Have favorable matchups for counting stats
            - Get consistent minutes despite {punt_category} weakness
            
            **Trade Targets:**
            Players to acquire: Those with poor {punt_category} but elite elsewhere
            Players to trade away: Any accidental {punt_category} specialists you drafted
            
            **Success Metrics:**
            - Winning 6-3 or better weekly
            - Top 3 in your strong categories
            - Dead last in {punt_category} (this means it's working!)
            - Consistent week-to-week performance
            
            **Expert Tip:**
            {self._get_expert_tip(punt_category)}
            """,
            "metadata": {
                "season": "2024-25",
                "categories": {
                    "punt": [punt_category.upper()],
                    "strong": self._get_strong_categories_list(punt_category),
                    "competitive": self._get_competitive_categories_list(punt_category)
                },
                "key_players": elite_players + good_players[:2],
                "draft_targets": {
                    "round_1_2": elite_players,
                    "round_3_5": good_players,
                    "round_6_9": ["Category specialists"],
                    "round_10_plus": value_players
                },
                "synergy_matrix": self._generate_synergy_matrix(elite_players, good_players),
                "author": random.choice(["FantasyPro", "BasketballMonster", "HashtagBasketball", "Reddit Expert"]),
                "rating": round(random.uniform(4.3, 4.9), 1),
                "views": random.randint(500, 10000),
                "success_rate": round(random.uniform(0.65, 0.85), 2)
            }
        }
        
        return doc
    
    def generate_balanced_strategy(self, variation: int = 0) -> Dict:
        """Generate a balanced build strategy"""
        self.strategy_count += 1
        
        player_pool = self.player_pools["balanced"]
        elite_players = random.sample(player_pool["elite"], 2)
        good_players = random.sample(player_pool["good"], 3)
        value_players = random.sample(player_pool["value"], 3)
        
        doc = {
            "strategy_id": self._generate_strategy_id("balanced", variation),
            "title": f"Balanced Build Strategy - The Safe Approach #{variation + 1}",
            "strategy_type": "balanced",
            "difficulty": "beginner",
            "text": f"""
            **The Balanced Build: Competing in All Categories**
            
            **Philosophy:**
            The balanced build aims to be competitive in all 9 categories without punting any. 
            This strategy provides flexibility and consistency but requires careful roster management.
            
            **Core Principles:**
            1. Draft best player available early
            2. Address weaknesses in middle rounds
            3. Maintain category balance throughout
            4. Stay flexible for trades and adjustments
            
            **Target Players:**
            Round 1-2: {', '.join(elite_players)}
            Round 3-5: {', '.join(good_players)}
            Round 6+: {', '.join(value_players)}
            
            **Category Management:**
            - Monitor all 9 categories weekly
            - Use streaming spots to address weaknesses
            - Make trades to balance roster
            - Avoid category specialists who hurt balance
            
            **Advantages:**
            - Flexibility to adjust strategy mid-season
            - No automatic losses in any category
            - Easier to make trades
            - Less dependent on specific players
            
            **Challenges:**
            - Harder to dominate categories
            - Requires more active management
            - May lose to specialized builds
            
            **Success Tips:**
            {self._get_balanced_tips()}
            """,
            "metadata": {
                "season": "2024-25",
                "categories": {
                    "punt": [],
                    "strong": ["Balanced across all"],
                    "competitive": ["All 9 categories"]
                },
                "key_players": elite_players + good_players[:2],
                "difficulty": "beginner",
                "flexibility": "high",
                "author": random.choice(["FantasyPro", "ESPN Fantasy", "Yahoo Fantasy"]),
                "rating": round(random.uniform(4.0, 4.5), 1)
            }
        }
        
        return doc
    
    def generate_position_strategy(self, position_focus: str, variation: int = 0) -> Dict:
        """Generate position-heavy strategy"""
        self.strategy_count += 1
        
        position_players = {
            "guard": ["Stephen Curry", "Damian Lillard", "Trae Young", "Tyrese Haliburton", "LaMelo Ball"],
            "wing": ["Jayson Tatum", "Kevin Durant", "Paul George", "Jaylen Brown", "Mikal Bridges"],
            "big": ["Joel Embiid", "Nikola Jokić", "Anthony Davis", "Domantas Sabonis", "Bam Adebayo"]
        }
        
        players = random.sample(position_players.get(position_focus, position_players["guard"]), 4)
        
        doc = {
            "strategy_id": self._generate_strategy_id(f"position_{position_focus}", variation),
            "title": f"{position_focus.title()}-Heavy Build Strategy #{variation + 1}",
            "strategy_type": f"position_{position_focus}",
            "difficulty": "intermediate",
            "text": f"""
            **The {position_focus.title()}-Heavy Build for 2024-25**
            
            **Core Concept:**
            Load up on elite {position_focus}s early and often, dominating their typical categories 
            while finding value at other positions later.
            
            **Why Go {position_focus.title()}-Heavy?**
            {self._get_position_rationale(position_focus)}
            
            **Draft Strategy:**
            - Rounds 1-4: Target 3-4 elite {position_focus}s
            - Rounds 5-8: Fill other positions with specialists
            - Rounds 9+: Handcuffs and upside plays
            
            **Target Players:**
            {', '.join(players)}
            
            **Categories to Dominate:**
            {self._get_position_categories(position_focus)}
            
            **Streaming Strategy:**
            Use your streaming spots for positions you're weak at, while your {position_focus} 
            core provides consistent production.
            """,
            "metadata": {
                "season": "2024-25",
                "position_focus": position_focus,
                "key_players": players,
                "categories": self._get_position_categories_dict(position_focus),
                "author": random.choice(["PositionExpert", "DraftKings", "FanDuel"]),
                "rating": round(random.uniform(4.1, 4.6), 1)
            }
        }
        
        return doc
    
    def generate_keeper_strategy(self, variation: int = 0) -> Dict:
        """Generate keeper league strategy"""
        self.strategy_count += 1
        
        young_players = ["Paolo Banchero", "Scottie Barnes", "Evan Mobley", "Cade Cunningham", 
                        "Franz Wagner", "Alperen Sengun", "Jalen Green", "Anthony Edwards"]
        keepers = random.sample(young_players, 4)
        
        doc = {
            "strategy_id": self._generate_strategy_id("keeper", variation),
            "title": f"Keeper League Strategy Guide #{variation + 1}",
            "strategy_type": "keeper",
            "difficulty": "advanced",
            "text": f"""
            **Keeper League Strategy for 2024-25 and Beyond**
            
            **Long-Term Vision:**
            In keeper leagues, you're not just building for this year - you're constructing a dynasty.
            
            **Core Keeper Targets:**
            {', '.join(keepers)}
            
            **Age vs Production Matrix:**
            - Under 23: High upside, accept current limitations
            - 23-26: Prime keeper territory 
            - 27-29: Win-now pieces
            - 30+: Trade for picks
            
            **Keeper Value Calculation:**
            {self._get_keeper_value_formula()}
            
            **Trade Strategy:**
            - Always consider keeper implications
            - Trade aging stars for young talent + picks
            - Package picks to move up in rookie drafts
            
            **This Year vs Future:**
            Balance competing now with building for the future. The sweet spot is having 
            2-3 young keepers while competing for a title.
            """,
            "metadata": {
                "season": "2024-25",
                "strategy_type": "keeper",
                "time_horizon": "3-5 years",
                "key_players": keepers,
                "author": "DynastyGuru",
                "rating": round(random.uniform(4.4, 4.8), 1)
            }
        }
        
        return doc
    
    def generate_dfs_strategy(self, variation: int = 0) -> Dict:
        """Generate DFS strategy document"""
        self.strategy_count += 1
        
        doc = {
            "strategy_id": self._generate_strategy_id("dfs", variation),
            "title": f"DFS Strategy: Maximizing Daily Fantasy Success #{variation + 1}",
            "strategy_type": "dfs",
            "difficulty": "intermediate",
            "text": f"""
            **Daily Fantasy Basketball Strategy Guide**
            
            **Core DFS Principles:**
            1. Target pace-up spots
            2. Find value in injuries/rest
            3. Stack correlated players
            4. Differentiate in tournaments
            
            **Slate Analysis Approach:**
            - Check injury reports 30 min before lock
            - Identify games with highest totals
            - Find value plays under 20% ownership
            - Build multiple lineup variations
            
            **Cash Game Strategy:**
            - Floor over ceiling
            - Avoid risky plays
            - High minute players only
            - Chalk is ok
            
            **GPP Strategy:**
            - Embrace variance
            - Target low ownership
            - Stack teammates
            - Bet on blowouts
            
            **Bankroll Management:**
            - 80% cash games
            - 20% tournaments
            - Never risk more than 10% on one slate
            """,
            "metadata": {
                "season": "2024-25",
                "platform": random.choice(["DraftKings", "FanDuel", "Yahoo"]),
                "strategy_type": "dfs",
                "author": "DFSPro",
                "rating": round(random.uniform(4.2, 4.7), 1)
            }
        }
        
        return doc
    
    def generate_auction_strategy(self, variation: int = 0) -> Dict:
        """Generate auction draft strategy"""
        self.strategy_count += 1
        
        doc = {
            "strategy_id": self._generate_strategy_id("auction", variation),
            "title": f"Auction Draft Mastery Guide #{variation + 1}",
            "strategy_type": "auction",
            "difficulty": "advanced",
            "text": f"""
            **Auction Draft Strategy for 2024-25**
            
            **Budget Allocation Models:**
            
            **Stars and Scrubs:**
            - 70% on 3 elite players
            - 20% on mid-tier
            - 10% on $1 players
            
            **Balanced Approach:**
            - 50% on 4 good players
            - 40% on 5 solid players  
            - 10% on value plays
            
            **Nomination Strategy:**
            - Nominate players you don't want early
            - Save targets for middle of draft
            - Create bidding wars on popular players
            
            **Price Enforcement:**
            - Know player values
            - Don't get attached
            - Be willing to walk away
            
            **End Game:**
            - Save $1 for each roster spot
            - Target upside in final rounds
            - Don't overpay for last starter
            """,
            "metadata": {
                "season": "2024-25",
                "strategy_type": "auction",
                "budget": 200,
                "author": "AuctionExpert",
                "rating": round(random.uniform(4.3, 4.8), 1)
            }
        }
        
        return doc
    
    # Helper methods
    def _get_punt_rationale(self, category: str) -> str:
        rationales = {
            "ft": "Free throw percentage is concentrated among a small pool of players. By punting it, you gain access to elite players like Giannis, Gobert, and Simmons at a discount.",
            "fg": "Field goal percentage allows you to load up on high-volume three-point shooters who provide elite scoring, threes, and assists.",
            "ast": "Assists are concentrated among point guards. Punting them lets you focus on wings and bigs who dominate other categories.",
            "pts": "Points are overvalued by casual players. Punting them lets you win with defense, efficiency, and hustle stats.",
            "3pm": "Three-pointers have become ubiquitous. Punting them lets you dominate traditional categories with old-school players.",
            "reb": "Rebounds are dominated by bigs. Punting them lets you go guard-heavy and dominate assists, steals, and threes.",
            "blk": "Blocks are rare and concentrated. Punting them gives you roster flexibility and guard options.",
            "stl": "Steals are volatile. Punting them provides consistency in other categories.",
            "to": "Turnovers are a negative category. 'Punting' them means embracing high-usage players."
        }
        return rationales.get(category, "This category can be effectively punted with the right strategy.")
    
    def _get_strong_categories(self, punt_category: str) -> str:
        strong_cats = {
            "ft": "FG%, REB, BLK, STL, TO",
            "fg": "FT%, 3PM, PTS, AST",
            "ast": "FG%, REB, BLK, PTS",
            "pts": "FG%, FT%, REB, AST, STL",
            "3pm": "FG%, REB, BLK, FT%",
            "reb": "FT%, 3PM, AST, STL",
            "blk": "3PM, AST, FT%, PTS",
            "stl": "REB, BLK, FG%, PTS",
            "to": "All positive categories"
        }
        return strong_cats.get(punt_category, "Multiple categories")
    
    def _get_strong_categories_list(self, punt_category: str) -> List[str]:
        return self._get_strong_categories(punt_category).split(", ")
    
    def _get_competitive_categories(self, punt_category: str) -> str:
        competitive = {
            "ft": "PTS, AST, 3PM",
            "fg": "REB, BLK, STL",
            "ast": "STL, 3PM, TO",
            "pts": "BLK, 3PM, TO",
            "3pm": "AST, STL, PTS",
            "reb": "BLK, FG%, TO",
            "blk": "REB, STL, TO",
            "stl": "AST, 3PM, FT%",
            "to": "None - dominate everything!"
        }
        return competitive.get(punt_category, "Various categories")
    
    def _get_competitive_categories_list(self, punt_category: str) -> List[str]:
        result = self._get_competitive_categories(punt_category)
        if "None" in result:
            return []
        return result.split(", ")
    
    def _get_player_synergies(self, elite: List[str], good: List[str]) -> str:
        synergies = []
        if len(elite) >= 2:
            synergies.append(f"{elite[0]} + {elite[1]}: Elite combo that perfectly complements each other")
        if elite and good:
            synergies.append(f"{elite[0]} + {good[0]}: Strong pairing with excellent category coverage")
        return "\n".join(synergies) if synergies else "Multiple strong combinations available"
    
    def _generate_synergy_matrix(self, elite: List[str], good: List[str]) -> Dict:
        matrix = {}
        all_players = elite + good[:2]
        for i, p1 in enumerate(all_players):
            for p2 in all_players[i+1:]:
                matrix[f"{p1}+{p2}"] = round(random.uniform(0.75, 0.95), 2)
        return matrix
    
    def _get_expert_tip(self, category: str) -> str:
        tips = {
            "ft": "Don't be afraid to be DEAD LAST in FT%. The worse you are, the better the strategy works!",
            "fg": "Load up on volume three-point shooters. Their 'bad' FG% is your competitive advantage.",
            "ast": "Focus on wings and bigs who can pass. Players like Jokić and Sabonis still provide some assists.",
            "pts": "Win with hustle stats. Players like Draymond Green become elite in this build.",
            "3pm": "Target players from the 90s/00s era playing style. They're undervalued in today's game.",
            "reb": "Go all-in on guard stats. You can win REB 1 week out of 10 and still make playoffs.",
            "blk": "Small-ball is your friend. Modern NBA trends support this punt strategy.",
            "stl": "Focus on consistency over variance. Steady producers win championships.",
            "to": "This is actually 'punt nothing' - embrace high usage players who produce everywhere."
        }
        return tips.get(category, "Stay committed to the punt all season long!")
    
    def _get_balanced_tips(self) -> str:
        tips = [
            "Stream aggressively based on weekly matchups",
            "Make 2-for-1 trades to open streaming spots",
            "Monitor category standings daily",
            "Be ready to pivot if injuries strike",
            "Use playoffs schedule as tiebreaker in draft"
        ]
        return "\n- ".join(random.sample(tips, 3))
    
    def _get_position_rationale(self, position: str) -> str:
        rationales = {
            "guard": "Guards dominate assists, steals, threes, and free throw percentage. Loading up on them creates an insurmountable advantage in these categories.",
            "wing": "Wings provide the best balance of scoring, defensive stats, and efficiency. They're the most versatile players in fantasy.",
            "big": "Bigs dominate rebounds, blocks, and field goal percentage. A big-heavy build creates unbeatable advantages in these scarce categories."
        }
        return rationales.get(position, "This position provides unique strategic advantages.")
    
    def _get_position_categories(self, position: str) -> str:
        categories = {
            "guard": "AST, STL, 3PM, FT%, PTS",
            "wing": "PTS, 3PM, REB, STL, FG%",
            "big": "REB, BLK, FG%, PTS, TO"
        }
        return categories.get(position, "Multiple categories")
    
    def _get_position_categories_dict(self, position: str) -> Dict:
        return {
            "strong": self._get_position_categories(position).split(", "),
            "weak": ["Various"],
            "competitive": ["Others"]
        }
    
    def _get_keeper_value_formula(self) -> str:
        return """
        Keeper Value = (Current Production × 0.4) + (Age Factor × 0.3) + (Upside × 0.3)
        
        Where:
        - Current Production = Fantasy ranking
        - Age Factor = (30 - Age) / 10
        - Upside = Projected improvement probability
        """
    
    def generate_all_strategies(self) -> List[Dict]:
        """Generate all strategy documents"""
        strategies = []
        
        # Punt strategies (9 categories × 20 variations = 180)
        punt_categories = ["ft", "fg", "ast", "pts", "3pm", "reb", "blk", "stl", "to"]
        for category in punt_categories:
            for i in range(20):
                strategies.append(self.generate_punt_strategy(category, i))
        
        # Balanced strategies (10)
        for i in range(10):
            strategies.append(self.generate_balanced_strategy(i))
        
        # Position strategies (3 positions × 3 variations = 9)
        for position in ["guard", "wing", "big"]:
            for i in range(3):
                strategies.append(self.generate_position_strategy(position, i))
        
        # Keeper strategies (5)
        for i in range(5):
            strategies.append(self.generate_keeper_strategy(i))
        
        # DFS strategies (4)
        for i in range(4):
            strategies.append(self.generate_dfs_strategy(i))
        
        # Auction strategies (2)
        for i in range(2):
            strategies.append(self.generate_auction_strategy(i))
        
        logger.info(f"Generated {len(strategies)} strategy documents")
        return strategies
    
    def save_strategies(self, strategies: List[Dict]) -> str:
        """Save strategy documents to JSON"""
        output_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'data', 'strategies'
        )
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, 'strategy_documents_2024_25.json')
        
        # Create summary statistics
        strategy_types = {}
        for strategy in strategies:
            stype = strategy.get('strategy_type', 'unknown')
            strategy_types[stype] = strategy_types.get(stype, 0) + 1
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "season": "2024-25",
                "generated_at": datetime.now().isoformat(),
                "total_strategies": len(strategies),
                "strategy_breakdown": strategy_types,
                "strategies": strategies
            }, f, indent=2)
        
        logger.info(f"Saved {len(strategies)} strategies to {output_file}")
        return output_file


def main():
    """Main function to generate all strategy documents"""
    print("=" * 60)
    print("Strategy Document Generation Script")
    print("=" * 60)
    
    generator = StrategyDocumentGenerator()
    
    print("\nGenerating strategy documents...")
    strategies = generator.generate_all_strategies()
    
    print(f"\n✓ Generated {len(strategies)} strategy documents")
    
    # Show breakdown
    strategy_types = {}
    for strategy in strategies:
        stype = strategy.get('strategy_type', 'unknown')
        strategy_types[stype] = strategy_types.get(stype, 0) + 1
    
    print("\nStrategy Breakdown:")
    for stype, count in sorted(strategy_types.items()):
        print(f"  - {stype}: {count}")
    
    print("\nSaving strategies...")
    output_file = generator.save_strategies(strategies)
    
    print("\n" + "=" * 60)
    print("Strategy Generation Complete!")
    print(f"✓ {len(strategies)} strategy documents created")
    print(f"✓ Saved to: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()