"""
Production-Ready Data Pipeline with Integrated Quality Checks
Shows how data quality should be enforced during data collection/ingestion
"""
import sys
import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from abc import ABC, abstractmethod
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataQualityValidator(ABC):
    """Abstract base class for data validators"""
    
    @abstractmethod
    def validate(self, data: Dict) -> Tuple[bool, List[str]]:
        """Validate data and return (is_valid, list_of_issues)"""
        pass
    
    @abstractmethod
    def clean(self, data: Dict) -> Dict:
        """Clean/transform data to meet quality standards"""
        pass


class TradeDataValidator(DataQualityValidator):
    """Validator for trade data from external sources"""
    
    def validate(self, data: Dict) -> Tuple[bool, List[str]]:
        """Validate trade data BEFORE it enters our system"""
        issues = []
        
        # CHECK 1: Required fields
        required_fields = ['headline', 'date', 'source', 'content']
        for field in required_fields:
            if field not in data or not data[field]:
                issues.append(f"Missing required field: {field}")
        
        # CHECK 2: Date validation
        if 'date' in data:
            try:
                # Parse various date formats from external sources
                date_str = data['date']
                if isinstance(date_str, str):
                    # Handle different formats: "2024-07-01", "07/01/2024", "July 1, 2024"
                    for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%B %d, %Y']:
                        try:
                            dt = datetime.strptime(date_str, fmt)
                            # Ensure date is within reasonable range
                            if dt.year < 2020 or dt.year > 2026:
                                issues.append(f"Date out of range: {date_str}")
                            break
                        except:
                            continue
                    else:
                        issues.append(f"Invalid date format: {date_str}")
            except Exception as e:
                issues.append(f"Date validation error: {e}")
        
        # CHECK 3: Content quality
        if 'content' in data:
            content = data['content']
            if len(content) < 100:
                issues.append(f"Content too short: {len(content)} chars (min 100)")
            if len(content) > 100000:
                issues.append(f"Content too long: {len(content)} chars (max 100000)")
            
            # Check for spam/junk indicators
            if content.count('http') > 10:
                issues.append("Too many URLs - possible spam")
            if re.search(r'(.)\1{10,}', content):  # Repeated characters
                issues.append("Suspicious repeated characters - possible junk data")
        
        # CHECK 4: Source validation
        if 'source' in data:
            valid_sources = ['espn', 'reddit', 'twitter', 'nba.com', 'the_athletic', 
                           'bleacher_report', 'yahoo', 'cbs_sports']
            source = data['source'].lower().replace(' ', '_')
            if source not in valid_sources:
                issues.append(f"Unknown source: {data['source']}")
        
        # CHECK 5: Player/Team extraction
        if 'content' in data:
            # Ensure we can extract meaningful entities
            nba_teams = ['Lakers', 'Celtics', 'Warriors', 'Heat', 'Bucks', 'Suns', 
                        'Nets', 'Clippers', 'Nuggets', 'Sixers']
            teams_mentioned = [team for team in nba_teams if team.lower() in data['content'].lower()]
            if len(teams_mentioned) == 0:
                issues.append("No NBA teams detected in content")
        
        is_valid = len(issues) == 0
        return is_valid, issues
    
    def clean(self, data: Dict) -> Dict:
        """Clean and standardize trade data"""
        cleaned = data.copy()
        
        # Standardize date format
        if 'date' in cleaned:
            date_str = cleaned['date']
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%B %d, %Y']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    cleaned['date_posted'] = dt.isoformat()
                    break
                except:
                    continue
        
        # Clean source field
        if 'source' in cleaned:
            cleaned['source'] = cleaned['source'].lower().replace(' ', '_')[:50]
        
        # Truncate content if needed for Milvus
        if 'content' in cleaned:
            cleaned['text'] = cleaned.pop('content')[:65535]
        
        # Extract metadata
        cleaned['metadata'] = {
            'original_source': data.get('source', 'unknown'),
            'ingestion_time': datetime.now().isoformat(),
            'quality_checked': True
        }
        
        return cleaned


class StrategyDataValidator(DataQualityValidator):
    """Validator for strategy content from external sources"""
    
    def validate(self, data: Dict) -> Tuple[bool, List[str]]:
        """Validate strategy data from Reddit/forums/blogs"""
        issues = []
        
        # CHECK 1: Content structure
        if 'content' not in data or not data['content']:
            issues.append("Missing strategy content")
        else:
            content = data['content']
            
            # Check for minimum structure
            if len(content) < 300:
                issues.append(f"Strategy too short: {len(content)} chars")
            
            # Check for strategy indicators
            strategy_keywords = ['draft', 'punt', 'build', 'target', 'avoid', 
                               'round', 'category', 'player', 'team']
            keyword_count = sum(1 for kw in strategy_keywords if kw in content.lower())
            if keyword_count < 3:
                issues.append("Content doesn't appear to be strategy-related")
        
        # CHECK 2: Title/Type classification
        if 'title' in data:
            title = data['title'].lower()
            # Classify strategy type based on title/content
            if any(punt in title for punt in ['punt ft', 'punt fg', 'punt ast']):
                data['detected_type'] = 'punt_strategy'
            elif any(term in title for term in ['rookie', 'sleeper', 'breakout']):
                data['detected_type'] = 'player_targets'
            elif any(term in title for term in ['dfs', 'daily', 'fanduel', 'draftkings']):
                data['detected_type'] = 'dfs_strategy'
        
        # CHECK 3: Author credibility (if available)
        if 'author' in data:
            # Check for bot/spam indicators
            author = data['author']
            if re.match(r'^user\d{10}$', author):  # Generic bot pattern
                issues.append("Suspicious author name pattern")
            
            # Could check author history/karma if available
            if 'author_karma' in data and data['author_karma'] < 10:
                issues.append("Low author credibility score")
        
        # CHECK 4: Freshness
        if 'date' in data:
            try:
                dt = datetime.fromisoformat(data['date'])
                age_days = (datetime.now() - dt).days
                if age_days > 365:
                    issues.append(f"Content too old: {age_days} days")
            except:
                pass
        
        is_valid = len(issues) == 0
        return is_valid, issues
    
    def clean(self, data: Dict) -> Dict:
        """Clean and enrich strategy data"""
        cleaned = data.copy()
        
        # Extract and structure content
        if 'content' in cleaned:
            cleaned['text'] = cleaned.pop('content')
            
            # Auto-detect strategy type if not provided
            if 'strategy_type' not in cleaned and 'detected_type' in cleaned:
                cleaned['strategy_type'] = cleaned.pop('detected_type')
            elif 'strategy_type' not in cleaned:
                cleaned['strategy_type'] = 'general'
        
        # Add quality metadata
        cleaned['metadata'] = {
            'source': data.get('source', 'unknown'),
            'author': data.get('author', 'anonymous'),
            'ingestion_time': datetime.now().isoformat(),
            'quality_score': self._calculate_quality_score(data)
        }
        
        return cleaned
    
    def _calculate_quality_score(self, data: Dict) -> float:
        """Calculate a quality score for ranking/filtering"""
        score = 0.5  # Base score
        
        # Length bonus
        if 'content' in data:
            length = len(data['content'])
            if length > 1000:
                score += 0.1
            if length > 2000:
                score += 0.1
        
        # Author credibility
        if 'author_karma' in data:
            if data['author_karma'] > 1000:
                score += 0.2
        
        # Engagement metrics
        if 'upvotes' in data and data['upvotes'] > 50:
            score += 0.1
        
        return min(score, 1.0)


class RealTimeDataPipeline:
    """Production data pipeline with integrated quality checks"""
    
    def __init__(self):
        self.trade_validator = TradeDataValidator()
        self.strategy_validator = StrategyDataValidator()
        self.stats = {
            'total_processed': 0,
            'valid_data': 0,
            'rejected_data': 0,
            'warnings': 0
        }
    
    def ingest_trade_data(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Ingest trade data from external API/scraper
        This would be called by your data collection scheduled job
        """
        clean_data = []
        
        for item in raw_data:
            self.stats['total_processed'] += 1
            
            # Validate BEFORE processing
            is_valid, issues = self.trade_validator.validate(item)
            
            if not is_valid:
                logger.warning(f"Rejected trade data: {issues[:2]}")  # Log first 2 issues
                self.stats['rejected_data'] += 1
                
                # Could save to dead letter queue for manual review
                self._save_to_dead_letter(item, issues)
                continue
            
            # Clean and transform
            cleaned = self.trade_validator.clean(item)
            
            # Additional enrichment could happen here
            cleaned = self._enrich_trade_data(cleaned)
            
            clean_data.append(cleaned)
            self.stats['valid_data'] += 1
            
            logger.info(f"Processed trade: {cleaned.get('headline', 'Unknown')[:50]}")
        
        # Log statistics
        logger.info(f"Trade ingestion stats: {self.stats}")
        
        return clean_data
    
    def ingest_strategy_data(self, raw_data: List[Dict]) -> List[Dict]:
        """Ingest strategy content from Reddit API, forums, etc."""
        clean_data = []
        
        for item in raw_data:
            self.stats['total_processed'] += 1
            
            # Validate
            is_valid, issues = self.strategy_validator.validate(item)
            
            if not is_valid:
                # Some issues might be warnings, not failures
                critical_issues = [i for i in issues if 'too old' not in i.lower()]
                
                if critical_issues:
                    logger.warning(f"Rejected strategy: {critical_issues[:2]}")
                    self.stats['rejected_data'] += 1
                    self._save_to_dead_letter(item, critical_issues)
                    continue
                else:
                    # Just warnings - process but flag
                    self.stats['warnings'] += 1
            
            # Clean and transform
            cleaned = self.strategy_validator.clean(item)
            clean_data.append(cleaned)
            self.stats['valid_data'] += 1
        
        return clean_data
    
    def _enrich_trade_data(self, data: Dict) -> Dict:
        """Enrich trade data with additional context"""
        # This would call other services/APIs
        
        # Example: Extract player entities using NER
        if 'text' in data:
            # In production, use spaCy or similar
            players = self._extract_player_names(data['text'])
            data['metadata']['players_mentioned'] = players
        
        # Example: Sentiment analysis
        data['metadata']['sentiment'] = self._analyze_sentiment(data.get('text', ''))
        
        return data
    
    def _extract_player_names(self, text: str) -> List[str]:
        """Mock player extraction - would use NER in production"""
        # This would use spaCy or similar NER model
        known_players = ['LeBron James', 'Stephen Curry', 'Kevin Durant', 
                        'Giannis Antetokounmpo', 'Luka Dončić']
        found = [p for p in known_players if p in text]
        return found
    
    def _analyze_sentiment(self, text: str) -> float:
        """Mock sentiment analysis - would use ML model in production"""
        # This would use TextBlob, VADER, or transformer model
        positive_words = ['great', 'excellent', 'win', 'upgrade', 'better']
        negative_words = ['bad', 'worse', 'lose', 'downgrade', 'terrible']
        
        pos_count = sum(1 for word in positive_words if word in text.lower())
        neg_count = sum(1 for word in negative_words if word in text.lower())
        
        if pos_count + neg_count == 0:
            return 0.5
        return pos_count / (pos_count + neg_count)
    
    def _save_to_dead_letter(self, data: Dict, issues: List[str]):
        """Save rejected data for manual review"""
        # In production, this would write to a dead letter queue (SQS, Kafka, etc.)
        # or a database table for manual review
        
        dead_letter_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'data', 'dead_letter'
        )
        os.makedirs(dead_letter_dir, exist_ok=True)
        
        filename = f"rejected_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(data)}.json"
        filepath = os.path.join(dead_letter_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'data': data,
                'issues': issues,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
    
    def get_pipeline_health(self) -> Dict:
        """Get pipeline health metrics"""
        total = self.stats['total_processed']
        if total == 0:
            return {'status': 'idle', 'stats': self.stats}
        
        success_rate = self.stats['valid_data'] / total
        
        return {
            'status': 'healthy' if success_rate > 0.8 else 'degraded',
            'success_rate': success_rate,
            'stats': self.stats,
            'last_updated': datetime.now().isoformat()
        }


def example_real_world_usage():
    """Example of how this would be used in production"""
    
    # This would typically be called by a scheduled job (Airflow, Cron, etc.)
    pipeline = RealTimeDataPipeline()
    
    # Simulate data from external sources
    
    # 1. Trade data from ESPN API (mock)
    raw_trades = [
        {
            'headline': 'Lakers Trade Russell Westbrook to Jazz',
            'date': '2024-07-15',
            'source': 'ESPN',
            'content': 'The Los Angeles Lakers have traded Russell Westbrook to the Utah Jazz...' * 20,
            'author': 'Adrian Wojnarowski'
        },
        {
            'headline': 'Invalid Trade',
            'date': 'invalid-date',
            'source': 'FakeNews',
            'content': 'Too short'  # Will be rejected
        }
    ]
    
    # Process trades with quality checks
    clean_trades = pipeline.ingest_trade_data(raw_trades)
    print(f"Processed {len(clean_trades)} valid trades")
    
    # 2. Strategy data from Reddit (mock)
    raw_strategies = [
        {
            'title': 'My Punt FT% Build for 2024-25',
            'content': 'Here is my detailed punt FT% strategy...' * 50,
            'author': 'FantasyGuru123',
            'author_karma': 5000,
            'upvotes': 125,
            'date': datetime.now().isoformat(),
            'source': 'reddit'
        },
        {
            'title': 'Random Post',
            'content': 'Not about fantasy',  # Will be rejected
            'author': 'user1234567890',  # Suspicious pattern
            'source': 'reddit'
        }
    ]
    
    # Process strategies with quality checks
    clean_strategies = pipeline.ingest_strategy_data(raw_strategies)
    print(f"Processed {len(clean_strategies)} valid strategies")
    
    # Check pipeline health
    health = pipeline.get_pipeline_health()
    print(f"\nPipeline Health: {health['status']}")
    print(f"Success Rate: {health['success_rate']*100:.1f}%")
    print(f"Stats: {health['stats']}")
    
    # The clean data would then be:
    # 1. Vectorized using embedding model
    # 2. Stored in Milvus
    # 3. Relationships created in Neo4j
    
    return clean_trades, clean_strategies


if __name__ == "__main__":
    print("="*60)
    print("PRODUCTION DATA PIPELINE WITH QUALITY CHECKS")
    print("="*60)
    
    trades, strategies = example_real_world_usage()
    
    print("\n" + "="*60)
    print("SAMPLE CLEANED DATA")
    print("="*60)
    
    if trades:
        print("\nSample Trade:")
        print(json.dumps(trades[0], indent=2)[:500])
    
    if strategies:
        print("\nSample Strategy:")
        print(json.dumps(strategies[0], indent=2)[:500])