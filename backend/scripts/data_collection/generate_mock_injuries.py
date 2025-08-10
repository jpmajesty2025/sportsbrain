"""
Generate mock injury history data for NBA players
Creates 300+ injury records for Neo4j graph population
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


class InjuryDataGenerator:
    def __init__(self):
        self.injury_count = 0
        self.injury_types = self._initialize_injury_types()
        self.player_injury_profiles = self._initialize_player_profiles()
        
    def _initialize_injury_types(self) -> Dict:
        """Initialize injury types and their characteristics"""
        return {
            "ankle_sprain": {
                "name": "Ankle Sprain",
                "severity_distribution": {"minor": 0.6, "moderate": 0.3, "major": 0.1},
                "games_missed": {"minor": (2, 5), "moderate": (7, 14), "major": (15, 30)},
                "recovery_time": {"minor": "1-2 weeks", "moderate": "2-4 weeks", "major": "4-8 weeks"},
                "recurrence_rate": 0.25,
                "position_bias": ["guard", "wing"]
            },
            "knee_injury": {
                "name": "Knee Injury",
                "severity_distribution": {"minor": 0.4, "moderate": 0.4, "major": 0.2},
                "games_missed": {"minor": (5, 10), "moderate": (15, 30), "major": (40, 82)},
                "recovery_time": {"minor": "2-3 weeks", "moderate": "4-8 weeks", "major": "3-12 months"},
                "recurrence_rate": 0.35,
                "position_bias": ["big", "wing"]
            },
            "hamstring_strain": {
                "name": "Hamstring Strain",
                "severity_distribution": {"minor": 0.5, "moderate": 0.35, "major": 0.15},
                "games_missed": {"minor": (3, 7), "moderate": (10, 20), "major": (25, 40)},
                "recovery_time": {"minor": "1-2 weeks", "moderate": "3-5 weeks", "major": "6-10 weeks"},
                "recurrence_rate": 0.4,
                "position_bias": ["guard", "wing"]
            },
            "back_spasms": {
                "name": "Back Spasms",
                "severity_distribution": {"minor": 0.7, "moderate": 0.25, "major": 0.05},
                "games_missed": {"minor": (1, 3), "moderate": (5, 10), "major": (15, 25)},
                "recovery_time": {"minor": "3-7 days", "moderate": "2-3 weeks", "major": "4-6 weeks"},
                "recurrence_rate": 0.45,
                "position_bias": ["big"]
            },
            "concussion": {
                "name": "Concussion",
                "severity_distribution": {"minor": 0.6, "moderate": 0.3, "major": 0.1},
                "games_missed": {"minor": (3, 7), "moderate": (10, 14), "major": (20, 30)},
                "recovery_time": {"minor": "1-2 weeks", "moderate": "2-3 weeks", "major": "4-6 weeks"},
                "recurrence_rate": 0.15,
                "position_bias": []  # No position bias
            },
            "shoulder_injury": {
                "name": "Shoulder Injury",
                "severity_distribution": {"minor": 0.5, "moderate": 0.35, "major": 0.15},
                "games_missed": {"minor": (3, 7), "moderate": (10, 20), "major": (30, 50)},
                "recovery_time": {"minor": "1-2 weeks", "moderate": "3-5 weeks", "major": "2-4 months"},
                "recurrence_rate": 0.3,
                "position_bias": ["wing", "big"]
            },
            "calf_strain": {
                "name": "Calf Strain",
                "severity_distribution": {"minor": 0.6, "moderate": 0.3, "major": 0.1},
                "games_missed": {"minor": (2, 5), "moderate": (7, 14), "major": (20, 30)},
                "recovery_time": {"minor": "1-2 weeks", "moderate": "2-4 weeks", "major": "5-8 weeks"},
                "recurrence_rate": 0.35,
                "position_bias": ["guard"]
            },
            "hip_injury": {
                "name": "Hip Injury",
                "severity_distribution": {"minor": 0.5, "moderate": 0.35, "major": 0.15},
                "games_missed": {"minor": (4, 8), "moderate": (12, 20), "major": (25, 40)},
                "recovery_time": {"minor": "2-3 weeks", "moderate": "3-5 weeks", "major": "6-10 weeks"},
                "recurrence_rate": 0.3,
                "position_bias": ["big"]
            },
            "wrist_injury": {
                "name": "Wrist Injury",
                "severity_distribution": {"minor": 0.6, "moderate": 0.3, "major": 0.1},
                "games_missed": {"minor": (2, 5), "moderate": (8, 15), "major": (20, 35)},
                "recovery_time": {"minor": "1-2 weeks", "moderate": "3-4 weeks", "major": "6-10 weeks"},
                "recurrence_rate": 0.2,
                "position_bias": ["guard"]
            },
            "rest": {
                "name": "Rest/Load Management",
                "severity_distribution": {"minor": 1.0, "moderate": 0, "major": 0},
                "games_missed": {"minor": (1, 2), "moderate": (0, 0), "major": (0, 0)},
                "recovery_time": {"minor": "1-2 games", "moderate": "N/A", "major": "N/A"},
                "recurrence_rate": 0.8,  # High because it's recurring strategy
                "position_bias": []
            }
        }
    
    def _initialize_player_profiles(self) -> Dict:
        """Initialize injury-prone player profiles"""
        return {
            # High injury risk players
            "Anthony Davis": {
                "injury_prone": True,
                "injury_multiplier": 2.5,
                "common_injuries": ["knee_injury", "back_spasms", "shoulder_injury"],
                "position": "big",
                "games_played_avg": 56
            },
            "Kawhi Leonard": {
                "injury_prone": True,
                "injury_multiplier": 2.2,
                "common_injuries": ["knee_injury", "rest", "hip_injury"],
                "position": "wing",
                "games_played_avg": 52
            },
            "Kyrie Irving": {
                "injury_prone": True,
                "injury_multiplier": 2.0,
                "common_injuries": ["knee_injury", "shoulder_injury", "back_spasms"],
                "position": "guard",
                "games_played_avg": 54
            },
            "Zion Williamson": {
                "injury_prone": True,
                "injury_multiplier": 2.8,
                "common_injuries": ["knee_injury", "hamstring_strain", "hip_injury"],
                "position": "big",
                "games_played_avg": 45
            },
            "Joel Embiid": {
                "injury_prone": True,
                "injury_multiplier": 2.0,
                "common_injuries": ["knee_injury", "rest", "back_spasms"],
                "position": "big",
                "games_played_avg": 58
            },
            "Karl-Anthony Towns": {
                "injury_prone": True,
                "injury_multiplier": 1.8,
                "common_injuries": ["calf_strain", "knee_injury", "wrist_injury"],
                "position": "big",
                "games_played_avg": 62
            },
            "Ben Simmons": {
                "injury_prone": True,
                "injury_multiplier": 2.3,
                "common_injuries": ["back_spasms", "knee_injury", "rest"],
                "position": "guard",
                "games_played_avg": 48
            },
            "Bradley Beal": {
                "injury_prone": True,
                "injury_multiplier": 1.9,
                "common_injuries": ["hamstring_strain", "back_spasms", "hip_injury"],
                "position": "guard",
                "games_played_avg": 55
            },
            "Paul George": {
                "injury_prone": True,
                "injury_multiplier": 1.7,
                "common_injuries": ["knee_injury", "shoulder_injury", "ankle_sprain"],
                "position": "wing",
                "games_played_avg": 60
            },
            "Kristaps Porzingis": {
                "injury_prone": True,
                "injury_multiplier": 2.1,
                "common_injuries": ["knee_injury", "ankle_sprain", "back_spasms"],
                "position": "big",
                "games_played_avg": 53
            }
        }
    
    def _get_other_players(self) -> List[str]:
        """Get list of regular players for minor injuries"""
        return [
            "Nikola Jokić", "Giannis Antetokounmpo", "Luka Dončić", "Jayson Tatum",
            "Stephen Curry", "Shai Gilgeous-Alexander", "Damian Lillard", "LeBron James",
            "Kevin Durant", "Trae Young", "Tyrese Haliburton", "Donovan Mitchell",
            "Anthony Edwards", "Jaylen Brown", "Devin Booker", "Jimmy Butler",
            "Ja Morant", "Domantas Sabonis", "De'Aaron Fox", "Julius Randle",
            "Pascal Siakam", "Lauri Markkanen", "DeMar DeRozan", "CJ McCollum",
            "Brandon Ingram", "Jaren Jackson Jr.", "Alperen Sengun", "Paolo Banchero",
            "Scottie Barnes", "Evan Mobley", "Cade Cunningham", "Franz Wagner",
            "Tyrese Maxey", "Jalen Brunson", "Dejounte Murray", "Fred VanVleet",
            "Darius Garland", "LaMelo Ball", "Zach LaVine", "Khris Middleton",
            "Jrue Holiday", "Bam Adebayo", "Rudy Gobert", "Myles Turner",
            "Brook Lopez", "Nikola Vučević", "Jonas Valančiūnas", "Clint Capela",
            "Jarrett Allen", "Mitchell Robinson", "Robert Williams III", "Jakob Poeltl",
            "OG Anunoby", "Mikal Bridges", "Andrew Wiggins", "Harrison Barnes",
            "Tobias Harris", "Jerami Grant", "Aaron Gordon", "Kyle Kuzma",
            "RJ Barrett", "Tyler Herro", "Jordan Poole", "Anfernee Simons",
            "Terry Rozier", "Coby White", "Immanuel Quickley", "Jalen Green",
            "Josh Giddey", "Bennedict Mathurin", "Shaedon Sharpe", "Jaden Ivey",
            "Walker Kessler", "Nic Claxton", "Onyeka Okongwu", "Isaiah Stewart",
            "Jalen Duren", "Mark Williams", "Alperen Şengün", "Jabari Smith Jr.",
            "Keegan Murray", "Jeremy Sochan", "Jalen Williams", "Tari Eason",
            "AJ Griffin", "Ochai Agbaji", "Nikola Jović", "Patrick Williams",
            "Jonathan Kuminga", "Moses Moody", "Ziaire Williams", "Trey Murphy III",
            "Herbert Jones", "Isaiah Jackson", "Day'Ron Sharpe", "Kai Jones",
            "Bones Hyland", "Ayo Dosunmu", "Quentin Grimes", "Cam Thomas",
            "Jaden McDaniels", "Desmond Bane", "Cole Anthony", "Tyrese Haliburton",
            "Donte DiVincenzo", "Gary Trent Jr.", "Malik Monk", "Kevin Huerter",
            "Bogdan Bogdanović", "Buddy Hield", "Duncan Robinson", "Joe Harris",
            "Seth Curry", "Patty Mills", "Goran Dragić", "Ricky Rubio",
            "Marcus Smart", "Derrick White", "Alex Caruso", "Matisse Thybulle",
            "Dillon Brooks", "Bruce Brown", "Josh Hart", "Draymond Green"
        ]
    
    def _generate_injury_id(self, player_name: str, date: str) -> str:
        """Generate unique injury ID"""
        return hashlib.md5(f"{player_name}_{date}_{self.injury_count}".encode()).hexdigest()[:12]
    
    def _select_severity(self, injury_type: Dict) -> str:
        """Select injury severity based on distribution"""
        dist = injury_type["severity_distribution"]
        rand = random.random()
        cumulative = 0
        for severity, prob in dist.items():
            cumulative += prob
            if rand <= cumulative:
                return severity
        return "minor"
    
    def _generate_injury_date(self, season_year: int = 2024) -> str:
        """Generate random injury date within season"""
        # NBA season runs October to April (plus playoffs)
        start_date = datetime(season_year, 10, 15)
        end_date = datetime(season_year + 1, 4, 15)
        
        random_days = random.randint(0, (end_date - start_date).days)
        injury_date = start_date + timedelta(days=random_days)
        
        return injury_date.strftime("%Y-%m-%d")
    
    def generate_injury_record(self, player_name: str, injury_type_key: str = None, 
                              severity: str = None, season: int = 2024) -> Dict:
        """Generate a single injury record"""
        self.injury_count += 1
        
        # Select injury type
        if injury_type_key is None:
            injury_type_key = random.choice(list(self.injury_types.keys()))
        injury_type = self.injury_types[injury_type_key]
        
        # Select severity
        if severity is None:
            severity = self._select_severity(injury_type)
        
        # Calculate games missed
        games_range = injury_type["games_missed"][severity]
        games_missed = random.randint(games_range[0], games_range[1]) if games_range[0] > 0 else 0
        
        # Generate dates
        injury_date = self._generate_injury_date(season)
        injury_datetime = datetime.strptime(injury_date, "%Y-%m-%d")
        return_date = (injury_datetime + timedelta(days=games_missed * 2)).strftime("%Y-%m-%d")
        
        # Fantasy impact calculation
        if severity == "major":
            fantasy_impact = round(random.uniform(-15, -25), 1)
        elif severity == "moderate":
            fantasy_impact = round(random.uniform(-8, -15), 1)
        else:
            fantasy_impact = round(random.uniform(-2, -8), 1)
        
        return {
            "injury_id": self._generate_injury_id(player_name, injury_date),
            "player_name": player_name,
            "injury_type": injury_type["name"],
            "injury_key": injury_type_key,
            "severity": severity,
            "injury_date": injury_date,
            "return_date": return_date,
            "games_missed": games_missed,
            "recovery_time": injury_type["recovery_time"][severity],
            "season": f"{season}-{str(season+1)[2:]}",
            "description": self._generate_injury_description(player_name, injury_type["name"], severity),
            "fantasy_impact": fantasy_impact,
            "fantasy_notes": self._generate_fantasy_notes(player_name, injury_type["name"], games_missed),
            "status_updates": self._generate_status_updates(injury_date, return_date, severity),
            "recurrence_risk": injury_type["recurrence_rate"],
            "previous_instances": random.randint(0, 3) if injury_type["recurrence_rate"] > 0.3 else 0
        }
    
    def _generate_injury_description(self, player_name: str, injury_type: str, severity: str) -> str:
        """Generate injury description"""
        descriptions = {
            "minor": [
                f"{player_name} suffered a minor {injury_type.lower()} during practice.",
                f"{player_name} is dealing with a slight {injury_type.lower()}.",
                f"{player_name} tweaked his {injury_type.lower().split()[0]} in the game.",
                f"Minor {injury_type.lower()} for {player_name}, day-to-day."
            ],
            "moderate": [
                f"{player_name} sustained a moderate {injury_type.lower()} in the third quarter.",
                f"{player_name} will miss time with a {injury_type.lower()}.",
                f"MRI confirms {injury_type.lower()} for {player_name}, multiple weeks expected.",
                f"{player_name} left the game with a concerning {injury_type.lower()}."
            ],
            "major": [
                f"{player_name} suffered a significant {injury_type.lower()}, extended absence expected.",
                f"Season-threatening {injury_type.lower()} for {player_name}.",
                f"{player_name} will undergo surgery for {injury_type.lower()}.",
                f"Major setback: {player_name} out indefinitely with {injury_type.lower()}."
            ]
        }
        return random.choice(descriptions.get(severity, descriptions["minor"]))
    
    def _generate_fantasy_notes(self, player_name: str, injury_type: str, games_missed: int) -> str:
        """Generate fantasy-relevant notes"""
        if games_missed == 0:
            return f"{player_name} should play through the {injury_type.lower()}. No fantasy impact expected."
        elif games_missed < 5:
            return f"Minor impact. Consider holding {player_name} if you have IL spots. Stream his backup for {games_missed} games."
        elif games_missed < 15:
            return f"Significant absence. {player_name}'s backup becomes a must-add. Consider IL stash if available."
        elif games_missed < 30:
            return f"Extended absence for {player_name}. Drop in shallow leagues, hold in deep/keeper formats. Backup is season-long add."
        else:
            return f"Season-altering injury. {player_name} droppable in most formats. Complete pivot needed for fantasy rosters."
    
    def _generate_status_updates(self, injury_date: str, return_date: str, severity: str) -> List[Dict]:
        """Generate status updates throughout injury"""
        updates = []
        
        if severity == "minor":
            updates.append({
                "date": injury_date,
                "status": "OUT",
                "note": "Initial injury report"
            })
            updates.append({
                "date": return_date,
                "status": "AVAILABLE",
                "note": "Cleared to play"
            })
        else:
            # More complex timeline for moderate/major injuries
            injury_dt = datetime.strptime(injury_date, "%Y-%m-%d")
            return_dt = datetime.strptime(return_date, "%Y-%m-%d")
            
            updates.append({
                "date": injury_date,
                "status": "OUT",
                "note": "Initial injury, evaluation pending"
            })
            
            # MRI/evaluation update
            eval_date = (injury_dt + timedelta(days=1)).strftime("%Y-%m-%d")
            updates.append({
                "date": eval_date,
                "status": "OUT",
                "note": f"MRI confirms {severity} injury"
            })
            
            # Mid-recovery update
            if severity == "moderate":
                mid_date = (injury_dt + timedelta(days=7)).strftime("%Y-%m-%d")
                updates.append({
                    "date": mid_date,
                    "status": "OUT",
                    "note": "Re-evaluated in one week"
                })
            elif severity == "major":
                mid_date = (injury_dt + timedelta(days=14)).strftime("%Y-%m-%d")
                updates.append({
                    "date": mid_date,
                    "status": "OUT",
                    "note": "Beginning rehabilitation"
                })
            
            # Return timeline update
            pre_return = (return_dt - timedelta(days=3)).strftime("%Y-%m-%d")
            updates.append({
                "date": pre_return,
                "status": "QUESTIONABLE",
                "note": "Nearing return, game-time decision"
            })
            
            updates.append({
                "date": return_date,
                "status": "AVAILABLE",
                "note": "Cleared for full contact"
            })
        
        return updates
    
    def generate_player_injury_history(self, player_name: str, profile: Dict = None) -> List[Dict]:
        """Generate injury history for a specific player"""
        injuries = []
        
        if profile and profile.get("injury_prone"):
            # Injury-prone player - more injuries
            num_injuries = random.randint(3, 6)
            common_injuries = profile.get("common_injuries", list(self.injury_types.keys()))
            
            for i in range(num_injuries):
                # Mix of seasons
                season = 2024 - (i // 2)  # Spread across 2-3 seasons
                
                # Higher chance of their common injuries
                if random.random() < 0.7:
                    injury_type = random.choice(common_injuries)
                else:
                    injury_type = random.choice(list(self.injury_types.keys()))
                
                # Higher chance of moderate/major injuries
                severity_weights = {"minor": 0.3, "moderate": 0.5, "major": 0.2}
                severity = random.choices(
                    list(severity_weights.keys()),
                    weights=list(severity_weights.values())
                )[0]
                
                injury = self.generate_injury_record(
                    player_name=player_name,
                    injury_type_key=injury_type,
                    severity=severity,
                    season=season
                )
                injuries.append(injury)
        else:
            # Regular player - fewer injuries
            num_injuries = random.randint(0, 2)
            
            for i in range(num_injuries):
                season = 2024 - i
                injury = self.generate_injury_record(
                    player_name=player_name,
                    season=season
                )
                injuries.append(injury)
        
        return injuries
    
    def generate_all_injuries(self) -> List[Dict]:
        """Generate all injury records"""
        all_injuries = []
        
        # High injury-risk players
        logger.info("Generating injuries for high-risk players...")
        for player_name, profile in self.player_injury_profiles.items():
            player_injuries = self.generate_player_injury_history(player_name, profile)
            all_injuries.extend(player_injuries)
            logger.info(f"  {player_name}: {len(player_injuries)} injuries")
        
        # Regular players
        logger.info("Generating injuries for other players...")
        other_players = self._get_other_players()
        
        for player_name in other_players:
            # Most players have 0-2 injuries
            player_injuries = self.generate_player_injury_history(player_name)
            if player_injuries:
                all_injuries.extend(player_injuries)
        
        logger.info(f"Total injuries generated: {len(all_injuries)}")
        return all_injuries
    
    def generate_injury_report(self, injuries: List[Dict]) -> Dict:
        """Generate summary injury report"""
        report = {
            "total_injuries": len(injuries),
            "by_severity": {},
            "by_type": {},
            "by_season": {},
            "most_injured_players": {},
            "average_games_missed": 0
        }
        
        # Count by severity
        for injury in injuries:
            severity = injury["severity"]
            report["by_severity"][severity] = report["by_severity"].get(severity, 0) + 1
            
            # Count by type
            injury_type = injury["injury_type"]
            report["by_type"][injury_type] = report["by_type"].get(injury_type, 0) + 1
            
            # Count by season
            season = injury["season"]
            report["by_season"][season] = report["by_season"].get(season, 0) + 1
            
            # Track player injury counts
            player = injury["player_name"]
            report["most_injured_players"][player] = report["most_injured_players"].get(player, 0) + 1
            
            # Sum games missed
            report["average_games_missed"] += injury["games_missed"]
        
        # Calculate average
        if injuries:
            report["average_games_missed"] = round(report["average_games_missed"] / len(injuries), 1)
        
        # Sort most injured players
        report["most_injured_players"] = dict(
            sorted(report["most_injured_players"].items(), 
                  key=lambda x: x[1], reverse=True)[:10]
        )
        
        return report
    
    def save_injuries(self, injuries: List[Dict]) -> str:
        """Save injury data to JSON"""
        output_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'data', 'injuries'
        )
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate report
        report = self.generate_injury_report(injuries)
        
        # Save main injury file
        output_file = os.path.join(output_dir, 'injury_history_2024_25.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "generated_at": datetime.now().isoformat(),
                "seasons_covered": ["2022-23", "2023-24", "2024-25"],
                "total_injuries": len(injuries),
                "injury_report": report,
                "injuries": injuries
            }, f, indent=2)
        
        logger.info(f"Saved {len(injuries)} injuries to {output_file}")
        
        # Save report separately
        report_file = os.path.join(output_dir, 'injury_report.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        return output_file


def main():
    """Main function to generate all injury data"""
    print("=" * 60)
    print("Injury Data Generation Script")
    print("=" * 60)
    
    generator = InjuryDataGenerator()
    
    print("\nGenerating injury records...")
    injuries = generator.generate_all_injuries()
    
    print(f"\n✓ Generated {len(injuries)} injury records")
    
    # Show breakdown
    report = generator.generate_injury_report(injuries)
    
    print("\nInjury Breakdown:")
    print(f"  By Severity:")
    for severity, count in report["by_severity"].items():
        print(f"    - {severity}: {count}")
    
    print(f"\n  Top 5 Most Injured Players:")
    for player, count in list(report["most_injured_players"].items())[:5]:
        print(f"    - {player}: {count} injuries")
    
    print(f"\n  Average Games Missed: {report['average_games_missed']}")
    
    print("\nSaving injury data...")
    output_file = generator.save_injuries(injuries)
    
    print("\n" + "=" * 60)
    print("Injury Generation Complete!")
    print(f"✓ {len(injuries)} injury records created")
    print(f"✓ Saved to: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()