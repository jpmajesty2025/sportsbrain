"""
Fantasy data enrichment for NBA players
Adds ADP, rankings, and keeper values to player data
"""
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

class FantasyDataEnricher:
    def __init__(self):
        # Load fantasy data from JSON file
        data_path = Path(__file__).parent.parent.parent / "data" / "fantasy_data_2024.json"
        
        self.fantasy_data = {}
        if data_path.exists():
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.fantasy_data = data.get('players', {})
    
    def enrich_player_metadata(self, player_name: str, current_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Add fantasy-specific data to player metadata"""
        
        # Copy existing metadata
        enriched = current_metadata.copy()
        
        # Add fantasy data if available
        if player_name in self.fantasy_data:
            fantasy_info = self.fantasy_data[player_name]
            enriched['fantasy'] = {
                'adp': fantasy_info.get('adp', 999),
                'ranking': fantasy_info.get('fantasy_ranking', 999),
                'keeper_round_value': fantasy_info.get('keeper_round_value', 15),
                'position_rank': fantasy_info.get('position_rank', 'NA'),
                'categories': self._determine_categories(current_metadata)
            }
        else:
            # Default values for players not in top rankings
            enriched['fantasy'] = {
                'adp': 200 + (hash(player_name) % 100),  # Rough estimate
                'ranking': 200 + (hash(player_name) % 100),
                'keeper_round_value': 15,  # Not keeper-worthy
                'categories': self._determine_categories(current_metadata)
            }
        
        # Add experience data
        enriched['experience'] = self._calculate_experience(current_metadata)
        
        # Add breakout score for young players
        if enriched['experience']['player_type'] in ['rookie', 'sophomore']:
            enriched['historical_stats'] = {
                'breakout_score': self._calculate_breakout_score(player_name, current_metadata)
            }
        
        return enriched
    
    def _determine_categories(self, metadata: Dict[str, Any]) -> list:
        """Determine player's strong fantasy categories based on stats"""
        categories = []
        stats = metadata.get('stats', {})
        
        if stats.get('ppg', 0) > 20:
            categories.append('PTS')
        if stats.get('rpg', 0) > 8:
            categories.append('REB')
        if stats.get('apg', 0) > 6:
            categories.append('AST')
        if stats.get('spg', 0) > 1.3:
            categories.append('STL')
        if stats.get('bpg', 0) > 1.3:
            categories.append('BLK')
        if stats.get('three_pct', 0) > 0.37:
            categories.append('3PM')
        if stats.get('ft_pct', 0) > 0.82:
            categories.append('FT%')
        
        return categories
    
    def _calculate_experience(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate player experience level"""
        # This is simplified - in production would use actual draft data
        age = metadata.get('age', 25)
        
        # Rough estimation based on age
        if age <= 21:
            years_in_league = 1
            player_type = "rookie"
        elif age == 22:
            years_in_league = 2
            player_type = "sophomore"
        elif age <= 25:
            years_in_league = age - 19
            player_type = "young"
        else:
            years_in_league = age - 19
            player_type = "veteran"
        
        return {
            'years_in_league': years_in_league,
            'player_type': player_type,
            'draft_year': 2024 - years_in_league
        }
    
    def _calculate_breakout_score(self, player_name: str, metadata: Dict[str, Any]) -> float:
        """Calculate breakout potential for young players"""
        # Simplified scoring - in production would use ML model
        score = 0.5  # Base score
        
        stats = metadata.get('stats', {})
        
        # High usage is good for breakout
        if stats.get('min_per_game', 0) > 28:
            score += 0.2
        
        # Improving efficiency
        if stats.get('fg_pct', 0) > 0.48:
            score += 0.1
        
        # Already showing fantasy relevance
        if stats.get('ppg', 0) > 15:
            score += 0.2
        
        # Known breakout candidates get boost
        breakout_candidates = ['Alperen Şengün', 'Paolo Banchero', 'Jalen Williams']
        if player_name in breakout_candidates:
            score = min(score + 0.3, 0.95)
        
        return round(score, 2)


# Example usage in player_loader.py:
def enrich_player_data_example():
    enricher = FantasyDataEnricher()
    
    # Sample metadata from NBA API
    current_metadata = {
        'team': 'BOS',
        'season': '2023-24',
        'stats': {
            'ppg': 27.5,
            'rpg': 8.1,
            'apg': 4.8
        },
        'age': 26
    }
    
    # Enrich with fantasy data
    enriched = enricher.enrich_player_metadata('Jayson Tatum', current_metadata)
    
    print(json.dumps(enriched, indent=2))