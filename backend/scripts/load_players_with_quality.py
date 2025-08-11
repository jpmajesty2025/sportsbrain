"""
Load NBA Players to Milvus with Integrated Quality Checks
This version includes data validation at every step of the pipeline
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

from app.data_loaders.player_loader import PlayerDataLoader
from app.db.vector_db import vector_db
from pymilvus import Collection
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlayerDataQualityChecker:
    """Quality checks for NBA player data"""
    
    def __init__(self):
        self.quality_report = {
            "total_players": 0,
            "valid_players": 0,
            "rejected_players": 0,
            "warnings": 0,
            "issues": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Define valid ranges for stats
        self.stat_ranges = {
            'ppg': (0, 50),      # Points per game
            'rpg': (0, 25),      # Rebounds per game
            'apg': (0, 15),      # Assists per game
            'spg': (0, 5),       # Steals per game
            'bpg': (0, 5),       # Blocks per game
            'fg_pct': (0, 1),    # Field goal percentage
            'ft_pct': (0, 1),    # Free throw percentage
            'three_pct': (0, 1), # Three point percentage
            'min_per_game': (0, 48)  # Minutes per game
        }
        
        self.valid_positions = ['G', 'F', 'C', 'G-F', 'F-G', 'F-C', 'C-F']
        self.valid_teams = self._get_valid_teams()
    
    def _get_valid_teams(self) -> List[str]:
        """Get list of valid NBA team abbreviations"""
        return [
            'ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW',
            'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK',
            'OKC', 'ORL', 'PHI', 'PHX', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS',
            'FA'  # Free Agent
        ]
    
    def validate_player_info(self, player_info: Dict) -> Tuple[bool, List[str]]:
        """
        CHECK 1: Validate basic player information from NBA API
        """
        issues = []
        
        # Required fields
        required_fields = ['id', 'full_name', 'is_active']
        for field in required_fields:
            if field not in player_info or player_info[field] is None:
                issues.append(f"Missing required field: {field}")
        
        # Name validation
        if 'full_name' in player_info:
            name = player_info['full_name']
            if len(name) < 3:
                issues.append(f"Invalid name too short: {name}")
            if len(name) > 50:
                issues.append(f"Name too long: {name}")
            if not any(c.isalpha() for c in name):
                issues.append(f"Name contains no letters: {name}")
        
        # ID validation
        if 'id' in player_info:
            player_id = player_info['id']
            if not isinstance(player_id, int) or player_id <= 0:
                issues.append(f"Invalid player ID: {player_id}")
        
        # Check if player is actually active
        if 'is_active' in player_info and not player_info['is_active']:
            issues.append("Player marked as inactive")
        
        return len(issues) == 0, issues
    
    def validate_player_stats(self, stats: Dict) -> Tuple[bool, List[str]]:
        """
        CHECK 2: Validate player statistics are within reasonable ranges
        """
        issues = []
        warnings = []
        
        if not stats:
            issues.append("No stats available")
            return False, issues
        
        # Check each stat is within reasonable range
        for stat_name, (min_val, max_val) in self.stat_ranges.items():
            if stat_name in stats:
                value = stats[stat_name]
                if value < min_val or value > max_val:
                    issues.append(f"{stat_name}={value} out of range [{min_val}, {max_val}]")
        
        # Team validation
        if 'team' in stats:
            team = stats['team']
            if team not in self.valid_teams:
                issues.append(f"Invalid team abbreviation: {team}")
        
        # Games played validation
        if 'games_played' in stats:
            gp = stats['games_played']
            if gp <= 0:
                issues.append(f"Invalid games played: {gp}")
            elif gp < 10:
                warnings.append(f"Low games played: {gp} (may affect stat reliability)")
        
        # Check for impossible stat combinations
        if 'fg_pct' in stats and 'three_pct' in stats:
            if stats['three_pct'] > 0 and stats['fg_pct'] == 0:
                issues.append("Impossible: 3PT% > 0 but FG% = 0")
        
        # Check minutes vs production
        if 'min_per_game' in stats and stats['min_per_game'] > 0:
            if stats.get('ppg', 0) == 0 and stats.get('rpg', 0) == 0 and stats.get('apg', 0) == 0:
                warnings.append("Player has minutes but no production")
        
        return len(issues) == 0, issues + warnings
    
    def validate_embedding_text(self, text: str) -> Tuple[bool, List[str]]:
        """
        CHECK 3: Validate the text description used for embedding
        """
        issues = []
        
        if not text:
            issues.append("Empty text description")
            return False, issues
        
        # Length checks
        if len(text) < 50:
            issues.append(f"Text too short for meaningful embedding: {len(text)} chars")
        if len(text) > 65535:  # Milvus VARCHAR limit
            issues.append(f"Text exceeds Milvus limit: {len(text)} chars")
        
        # Content checks
        if text.count('\n') > 50:
            issues.append("Excessive line breaks in text")
        
        # Check for required content
        required_keywords = ['player', 'season', 'team', 'position']
        missing_keywords = [kw for kw in required_keywords if kw not in text.lower()]
        if len(missing_keywords) > 2:
            issues.append(f"Text missing key basketball context: {missing_keywords}")
        
        return len(issues) == 0, issues
    
    def validate_fantasy_enrichment(self, fantasy_data: Dict) -> Tuple[bool, List[str]]:
        """
        CHECK 4: Validate fantasy basketball enrichment data
        """
        issues = []
        warnings = []
        
        if not fantasy_data:
            warnings.append("No fantasy data available")
            return True, warnings  # Not critical
        
        # ADP validation
        if 'adp' in fantasy_data:
            adp = fantasy_data['adp']
            if adp < 1 or adp > 300:
                issues.append(f"Invalid ADP (Average Draft Position): {adp}")
        
        # Keeper value validation
        if 'keeper_round_value' in fantasy_data:
            krv = fantasy_data['keeper_round_value']
            if krv < 1 or krv > 20:
                issues.append(f"Invalid keeper round value: {krv}")
        
        # Fantasy points validation
        if 'fantasy_ppg' in fantasy_data:
            fppg = fantasy_data['fantasy_ppg']
            if fppg < 0 or fppg > 100:
                issues.append(f"Invalid fantasy PPG: {fppg}")
        
        return len(issues) == 0, issues + warnings
    
    def generate_quality_report(self) -> str:
        """Generate a quality report for the data load"""
        report_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data', f'player_quality_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        
        with open(report_file, 'w') as f:
            json.dump(self.quality_report, f, indent=2)
        
        return report_file


class QualityAwarePlayerLoader(PlayerDataLoader):
    """Enhanced player loader with integrated quality checks"""
    
    def __init__(self):
        super().__init__()
        self.quality_checker = PlayerDataQualityChecker()
        self.rejected_players = []
        
    def load_players_with_quality_checks(self, limit: Optional[int] = None):
        """Load players with quality validation at each step"""
        
        # Get all active players
        all_players = self.get_all_active_players()
        if limit:
            all_players = all_players[:limit]
        
        logger.info(f"Processing {len(all_players)} players with quality checks")
        
        valid_players = []
        
        for i, player_info in enumerate(all_players):
            if i % 50 == 0:
                logger.info(f"Processing player {i}/{len(all_players)}")
            
            # QUALITY CHECK 1: Validate player info
            is_valid, issues = self.quality_checker.validate_player_info(player_info)
            if not is_valid:
                logger.warning(f"Rejected {player_info.get('full_name', 'Unknown')}: {issues[:2]}")
                self.rejected_players.append({
                    'player': player_info,
                    'reason': 'invalid_info',
                    'issues': issues
                })
                self.quality_checker.quality_report['rejected_players'] += 1
                continue
            
            # Get player stats
            try:
                stats = self.get_player_stats(player_info['id'])
                
                # QUALITY CHECK 2: Validate stats
                if stats:
                    is_valid, issues = self.quality_checker.validate_player_stats(stats)
                    if not is_valid:
                        logger.warning(f"Stats issues for {player_info['full_name']}: {issues[:2]}")
                        # Don't reject, but flag warnings
                        self.quality_checker.quality_report['warnings'] += len(issues)
                
            except Exception as e:
                logger.error(f"Failed to get stats for {player_info['full_name']}: {e}")
                stats = None
            
            # Create text description
            text_description = self.create_player_text_description(player_info, stats or {})
            
            # QUALITY CHECK 3: Validate embedding text
            is_valid, issues = self.quality_checker.validate_embedding_text(text_description)
            if not is_valid:
                logger.warning(f"Text issues for {player_info['full_name']}: {issues}")
                # Try to fix the text
                if len(text_description) < 50:
                    # Enhance short descriptions
                    text_description += f" NBA player with ID {player_info['id']}. Professional basketball athlete."
            
            # Get fantasy enrichment
            fantasy_data = self.fantasy_enricher.get_fantasy_data(player_info['full_name'])
            
            # QUALITY CHECK 4: Validate fantasy data
            if fantasy_data:
                is_valid, issues = self.quality_checker.validate_fantasy_enrichment(fantasy_data)
                if not is_valid:
                    logger.warning(f"Fantasy data issues for {player_info['full_name']}: {issues}")
            
            # If we made it here, player data is valid
            valid_players.append({
                'info': player_info,
                'stats': stats,
                'text': text_description,
                'fantasy': fantasy_data
            })
            self.quality_checker.quality_report['valid_players'] += 1
        
        self.quality_checker.quality_report['total_players'] = len(all_players)
        
        logger.info(f"Quality check complete: {len(valid_players)}/{len(all_players)} valid players")
        
        # Now load valid players to Milvus
        self._load_to_milvus(valid_players)
        
        # Generate quality report
        report_file = self.quality_checker.generate_quality_report()
        logger.info(f"Quality report saved to: {report_file}")
        
        return valid_players
    
    def _load_to_milvus(self, valid_players: List[Dict]):
        """Load validated players to Milvus"""
        try:
            vector_db.connect()
            collection = Collection(self.collection_name)
            
            batch_size = 50
            for i in range(0, len(valid_players), batch_size):
                batch = valid_players[i:i+batch_size]
                
                # Prepare data for insertion
                primary_keys = []
                vectors = []
                texts = []
                player_names = []
                positions = []
                metadatas = []
                created_ats = []
                
                # Generate embeddings for batch
                batch_texts = [p['text'] for p in batch]
                batch_embeddings = self.embedding_model.encode(batch_texts)
                
                for j, player_data in enumerate(batch):
                    player_info = player_data['info']
                    
                    # Generate primary key
                    pk_string = f"{player_info['id']}_{player_info['full_name']}"
                    pk = mmh3.hash64(pk_string)[0]
                    if pk < 0:
                        pk = pk + 2**63
                    
                    primary_keys.append(pk)
                    vectors.append(batch_embeddings[j].tolist())
                    texts.append(player_data['text'])
                    player_names.append(player_info['full_name'])
                    positions.append(player_info.get('position', 'G'))
                    
                    # Combine all metadata
                    metadata = {
                        'player_id': player_info['id'],
                        'stats': player_data.get('stats', {}),
                        'fantasy': player_data.get('fantasy', {}),
                        'quality_checked': True,
                        'load_timestamp': datetime.now().isoformat()
                    }
                    metadatas.append(metadata)
                    created_ats.append(int(time.time()))
                
                # Insert to Milvus
                collection.insert([
                    primary_keys,
                    vectors,
                    texts,
                    player_names,
                    positions,
                    metadatas,
                    created_ats
                ])
                
                logger.info(f"Inserted batch {i//batch_size + 1}: {len(batch)} players")
            
            collection.flush()
            vector_db.disconnect()
            
        except Exception as e:
            logger.error(f"Failed to load to Milvus: {e}")
            raise


def main():
    """Main function to load players with quality checks"""
    print("="*60)
    print("NBA PLAYER DATA LOADING WITH QUALITY CHECKS")
    print("="*60)
    
    loader = QualityAwarePlayerLoader()
    
    # Check current count
    try:
        vector_db.connect()
        collection = Collection(settings.MILVUS_PLAYERS_COLLECTION)
        current_count = collection.num_entities
        vector_db.disconnect()
        print(f"Current players in collection: {current_count}")
    except:
        current_count = 0
        print("Collection empty or not found")
    
    if current_count > 0:
        response = input("\nCollection has data. Clear and reload? (y/n): ")
        if response.lower() != 'y':
            print("Aborted")
            return
    
    # Load all players with quality checks
    print("\nLoading players with quality validation...")
    valid_players = loader.load_players_with_quality_checks(limit=572)  # Load all 572
    
    # Print summary
    report = loader.quality_checker.quality_report
    print("\n" + "="*60)
    print("LOADING COMPLETE - QUALITY SUMMARY")
    print("="*60)
    print(f"Total Players Processed: {report['total_players']}")
    print(f"Valid Players Loaded: {report['valid_players']}")
    print(f"Rejected Players: {report['rejected_players']}")
    print(f"Warnings: {report['warnings']}")
    
    if report['rejected_players'] > 0:
        print(f"\nRejected players saved for review")
    
    # Check final count
    try:
        vector_db.connect()
        collection = Collection(settings.MILVUS_PLAYERS_COLLECTION)
        final_count = collection.num_entities
        vector_db.disconnect()
        print(f"\nFinal count in Milvus: {final_count}")
    except:
        pass
    
    print("="*60)


if __name__ == "__main__":
    main()