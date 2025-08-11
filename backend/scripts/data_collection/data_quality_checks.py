"""
Data Quality Checks for SportsBrain Vectorized Data
Implements 2+ quality checks for each data source as per rubric requirements
"""
import sys
import os
import json
import numpy as np
from typing import List, Dict, Any, Tuple
from datetime import datetime
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataQualityChecker:
    """Comprehensive data quality checks for all data sources"""
    
    def __init__(self):
        self.data_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'data'
        )
        self.quality_report = {
            "timestamp": datetime.now().isoformat(),
            "sources_checked": [],
            "total_issues": 0,
            "critical_issues": 0,
            "warnings": 0,
            "passed_checks": 0
        }
    
    # ==================== STRATEGY DATA CHECKS ====================
    
    def check_strategy_data(self) -> Dict:
        """Quality checks for strategy documents"""
        logger.info("\n" + "="*60)
        logger.info("CHECKING STRATEGY DATA QUALITY")
        logger.info("="*60)
        
        results = {
            "source": "strategies",
            "file_paths": [],
            "total_documents": 0,
            "checks": {},
            "issues": [],
            "warnings": []
        }
        
        # Load all strategy files
        strategy_files = [
            'strategies/strategy_documents_2024_25.json',
            'supplemental/supplemental_strategies.json'
        ]
        
        all_strategies = []
        for file_path in strategy_files:
            full_path = os.path.join(self.data_dir, file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_strategies.extend(data.get('strategies', []))
                    results["file_paths"].append(file_path)
        
        results["total_documents"] = len(all_strategies)
        
        # CHECK 1: Text Length and Quality
        logger.info("\n[Check 1] Text Length and Quality")
        text_issues = []
        min_length = 500  # Minimum characters for meaningful strategy
        max_length = 65535  # Milvus VARCHAR limit
        
        for i, strategy in enumerate(all_strategies):
            text = strategy.get('text', '')
            
            # Length check
            if len(text) < min_length:
                text_issues.append(f"Strategy {i}: Text too short ({len(text)} chars)")
            elif len(text) > max_length:
                text_issues.append(f"Strategy {i}: Text exceeds limit ({len(text)} chars)")
            
            # Content quality checks
            if not re.search(r'\*\*[^*]+\*\*', text):  # Check for markdown headers
                text_issues.append(f"Strategy {i}: No markdown formatting found")
            
            if text.count('\n') < 5:  # Check for proper structure
                text_issues.append(f"Strategy {i}: Insufficient text structure")
        
        results["checks"]["text_quality"] = {
            "passed": len(text_issues) == 0,
            "issues_found": len(text_issues),
            "details": text_issues[:5]  # Show first 5 issues
        }
        
        if text_issues:
            results["issues"].extend(text_issues[:3])
        
        logger.info(f"  - Text quality issues: {len(text_issues)}")
        logger.info(f"  - Average text length: {np.mean([len(s.get('text', '')) for s in all_strategies]):.0f} chars")
        
        # CHECK 2: Metadata Completeness
        logger.info("\n[Check 2] Metadata Completeness")
        required_fields = ['strategy_type', 'difficulty', 'metadata']
        metadata_subfields = ['season', 'categories', 'key_players']
        metadata_issues = []
        
        for i, strategy in enumerate(all_strategies):
            # Check required top-level fields
            for field in required_fields:
                if field not in strategy or strategy[field] is None:
                    metadata_issues.append(f"Strategy {i}: Missing {field}")
            
            # Check metadata subfields
            metadata = strategy.get('metadata', {})
            for subfield in metadata_subfields:
                if subfield not in metadata:
                    metadata_issues.append(f"Strategy {i}: Missing metadata.{subfield}")
        
        results["checks"]["metadata_completeness"] = {
            "passed": len(metadata_issues) == 0,
            "issues_found": len(metadata_issues),
            "details": metadata_issues[:5]
        }
        
        if metadata_issues:
            results["warnings"].extend(metadata_issues[:3])
        
        logger.info(f"  - Metadata issues: {len(metadata_issues)}")
        
        # CHECK 3: Strategy Type Validation
        logger.info("\n[Check 3] Strategy Type Validation")
        valid_types = ['punt_ft', 'punt_fg', 'punt_ast', 'punt_pts', 'punt_3pm', 
                      'punt_reb', 'punt_blk', 'punt_stl', 'punt_to', 'balanced',
                      'position_guard', 'position_wing', 'position_big', 'keeper',
                      'dfs', 'auction', 'rookie_focus', 'dfs_advanced']
        type_issues = []
        
        type_distribution = {}
        for strategy in all_strategies:
            stype = strategy.get('strategy_type', 'unknown')
            type_distribution[stype] = type_distribution.get(stype, 0) + 1
            
            if stype not in valid_types:
                type_issues.append(f"Invalid strategy type: {stype}")
        
        results["checks"]["type_validation"] = {
            "passed": len(type_issues) == 0,
            "issues_found": len(type_issues),
            "type_distribution": type_distribution
        }
        
        logger.info(f"  - Type validation issues: {len(type_issues)}")
        logger.info(f"  - Unique strategy types: {len(type_distribution)}")
        
        return results
    
    # ==================== TRADE DATA CHECKS ====================
    
    def check_trade_data(self) -> Dict:
        """Quality checks for trade documents"""
        logger.info("\n" + "="*60)
        logger.info("CHECKING TRADE DATA QUALITY")
        logger.info("="*60)
        
        results = {
            "source": "trades",
            "file_paths": [],
            "total_documents": 0,
            "checks": {},
            "issues": [],
            "warnings": []
        }
        
        # Load all trade files
        trade_files = [
            'mock_trades/trade_documents_2024_25.json',
            'supplemental/supplemental_trades.json'
        ]
        
        all_trades = []
        for file_path in trade_files:
            full_path = os.path.join(self.data_dir, file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    docs = data.get('documents', data.get('trades', []))
                    all_trades.extend(docs)
                    results["file_paths"].append(file_path)
        
        results["total_documents"] = len(all_trades)
        
        # CHECK 1: Date Validation
        logger.info("\n[Check 1] Date Validation")
        date_issues = []
        
        for i, trade in enumerate(all_trades):
            date_posted = trade.get('date_posted', '')
            
            # Check date format
            try:
                if 'T' in date_posted:
                    datetime.fromisoformat(date_posted.replace('T', ' '))
                else:
                    datetime.strptime(date_posted, '%Y-%m-%d')
            except:
                date_issues.append(f"Trade {i}: Invalid date format: {date_posted}")
            
            # Check date range (should be 2024-2025 season)
            try:
                if 'T' in date_posted:
                    dt = datetime.fromisoformat(date_posted.replace('T', ' '))
                else:
                    dt = datetime.strptime(date_posted, '%Y-%m-%d')
                
                if dt.year < 2024 or dt.year > 2025:
                    date_issues.append(f"Trade {i}: Date out of season range: {date_posted}")
            except:
                pass
        
        results["checks"]["date_validation"] = {
            "passed": len(date_issues) == 0,
            "issues_found": len(date_issues),
            "details": date_issues[:5]
        }
        
        if date_issues:
            results["issues"].extend(date_issues[:3])
        
        logger.info(f"  - Date validation issues: {len(date_issues)}")
        
        # CHECK 2: Source Field Validation
        logger.info("\n[Check 2] Source Field Validation")
        valid_sources = ['reddit', 'twitter', 'espn', 'bleacher_report', 'the_athletic']
        source_issues = []
        source_distribution = {}
        
        for i, trade in enumerate(all_trades):
            source = trade.get('source', '')
            
            # Check source exists and length
            if not source:
                source_issues.append(f"Trade {i}: Missing source")
            elif len(source) > 50:  # Milvus field limit
                source_issues.append(f"Trade {i}: Source exceeds 50 chars: {source}")
            
            # Track distribution
            source_distribution[source] = source_distribution.get(source, 0) + 1
        
        results["checks"]["source_validation"] = {
            "passed": len(source_issues) == 0,
            "issues_found": len(source_issues),
            "source_distribution": source_distribution
        }
        
        if source_issues:
            results["issues"].extend(source_issues[:3])
        
        logger.info(f"  - Source validation issues: {len(source_issues)}")
        logger.info(f"  - Unique sources: {len(source_distribution)}")
        
        # CHECK 3: Content Coherence
        logger.info("\n[Check 3] Content Coherence")
        content_issues = []
        
        for i, trade in enumerate(all_trades):
            text = trade.get('text', '')
            headline = trade.get('headline', '')
            
            # Check text length
            if len(text) < 200:
                content_issues.append(f"Trade {i}: Text too short ({len(text)} chars)")
            
            # Check headline exists
            if not headline:
                content_issues.append(f"Trade {i}: Missing headline")
            
            # Check for player mentions in text
            if 'players_mentioned' in trade.get('metadata', {}):
                players = trade['metadata']['players_mentioned']
                if isinstance(players, list):
                    for player in players[:2]:  # Check first 2 players
                        if player not in text:
                            content_issues.append(f"Trade {i}: Player '{player}' in metadata but not in text")
        
        results["checks"]["content_coherence"] = {
            "passed": len(content_issues) == 0,
            "issues_found": len(content_issues),
            "avg_text_length": np.mean([len(t.get('text', '')) for t in all_trades]),
            "details": content_issues[:5]
        }
        
        if content_issues:
            results["warnings"].extend(content_issues[:3])
        
        logger.info(f"  - Content coherence issues: {len(content_issues)}")
        
        return results
    
    # ==================== INJURY DATA CHECKS ====================
    
    def check_injury_data(self) -> Dict:
        """Quality checks for injury data"""
        logger.info("\n" + "="*60)
        logger.info("CHECKING INJURY DATA QUALITY")
        logger.info("="*60)
        
        results = {
            "source": "injuries",
            "file_paths": [],
            "total_documents": 0,
            "checks": {},
            "issues": [],
            "warnings": []
        }
        
        # Load injury data
        injury_file = os.path.join(self.data_dir, 'injuries/injury_history_2024_25.json')
        
        if not os.path.exists(injury_file):
            results["issues"].append("Injury data file not found")
            return results
        
        with open(injury_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            injuries = data.get('injuries', [])
        
        results["file_paths"].append('injuries/injury_history_2024_25.json')
        results["total_documents"] = len(injuries)
        
        # CHECK 1: Injury Severity and Games Missed Consistency
        logger.info("\n[Check 1] Severity and Games Missed Consistency")
        consistency_issues = []
        
        severity_ranges = {
            'minor': (0, 10),
            'moderate': (5, 30),
            'major': (15, 82)
        }
        
        for i, injury in enumerate(injuries):
            severity = injury.get('severity', '')
            games_missed = injury.get('games_missed', 0)
            
            if severity in severity_ranges:
                min_games, max_games = severity_ranges[severity]
                if games_missed < min_games or games_missed > max_games:
                    consistency_issues.append(
                        f"Injury {i}: {severity} severity but {games_missed} games missed (expected {min_games}-{max_games})"
                    )
        
        results["checks"]["severity_consistency"] = {
            "passed": len(consistency_issues) == 0,
            "issues_found": len(consistency_issues),
            "details": consistency_issues[:5]
        }
        
        if consistency_issues:
            results["warnings"].extend(consistency_issues[:3])
        
        logger.info(f"  - Consistency issues: {len(consistency_issues)}")
        
        # CHECK 2: Player Name Validation
        logger.info("\n[Check 2] Player Name Validation")
        name_issues = []
        player_injury_counts = {}
        
        for i, injury in enumerate(injuries):
            player_name = injury.get('player_name', '')
            
            if not player_name:
                name_issues.append(f"Injury {i}: Missing player name")
            elif len(player_name) < 3:
                name_issues.append(f"Injury {i}: Invalid player name: {player_name}")
            
            # Track injury frequency
            player_injury_counts[player_name] = player_injury_counts.get(player_name, 0) + 1
        
        # Check for unrealistic injury counts
        for player, count in player_injury_counts.items():
            if count > 10:  # More than 10 injuries is suspicious
                name_issues.append(f"Player {player} has {count} injuries (seems excessive)")
        
        results["checks"]["player_validation"] = {
            "passed": len(name_issues) == 0,
            "issues_found": len(name_issues),
            "unique_players": len(player_injury_counts),
            "max_injuries_per_player": max(player_injury_counts.values()) if player_injury_counts else 0
        }
        
        if name_issues:
            results["warnings"].extend(name_issues[:3])
        
        logger.info(f"  - Player validation issues: {len(name_issues)}")
        logger.info(f"  - Unique players with injuries: {len(player_injury_counts)}")
        
        return results
    
    # ==================== VECTOR EMBEDDING CHECKS ====================
    
    def check_vector_quality(self) -> Dict:
        """Quality checks for vector embeddings in Milvus"""
        logger.info("\n" + "="*60)
        logger.info("CHECKING VECTOR EMBEDDING QUALITY")
        logger.info("="*60)
        
        results = {
            "source": "embeddings",
            "checks": {},
            "issues": [],
            "warnings": []
        }
        
        try:
            from pymilvus import connections, Collection
            from dotenv import load_dotenv
            
            # Load environment
            env_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                '.env'
            )
            load_dotenv(env_path)
            
            # Connect to Milvus
            milvus_uri = os.getenv("MILVUS_HOST")
            milvus_token = os.getenv("MILVUS_TOKEN")
            
            connections.connect(
                alias="default",
                uri=milvus_uri,
                token=milvus_token,
                timeout=30
            )
            
            # CHECK 1: Embedding Dimensions
            logger.info("\n[Check 1] Embedding Dimensions")
            collections = ['sportsbrain_players', 'sportsbrain_strategies', 'sportsbrain_trades']
            dim_issues = []
            
            for coll_name in collections:
                try:
                    collection = Collection(coll_name)
                    # Sample some vectors
                    sample = collection.query(
                        expr="primary_key > 0",
                        output_fields=["vector"],
                        limit=10
                    )
                    
                    for item in sample:
                        vector = item.get('vector', [])
                        if len(vector) != 768:
                            dim_issues.append(f"{coll_name}: Vector dimension {len(vector)} != 768")
                    
                    logger.info(f"  - {coll_name}: Checked {len(sample)} vectors")
                    
                except Exception as e:
                    dim_issues.append(f"{coll_name}: Error checking vectors - {e}")
            
            results["checks"]["embedding_dimensions"] = {
                "passed": len(dim_issues) == 0,
                "issues_found": len(dim_issues),
                "details": dim_issues
            }
            
            # CHECK 2: Embedding Normalization
            logger.info("\n[Check 2] Embedding Normalization")
            norm_issues = []
            
            for coll_name in collections[:1]:  # Check first collection as sample
                try:
                    collection = Collection(coll_name)
                    sample = collection.query(
                        expr="primary_key > 0",
                        output_fields=["vector"],
                        limit=5
                    )
                    
                    for i, item in enumerate(sample):
                        vector = np.array(item.get('vector', []))
                        norm = np.linalg.norm(vector)
                        
                        # Check if normalized (norm should be close to 1)
                        if abs(norm - 1.0) > 0.01:
                            norm_issues.append(f"{coll_name} item {i}: Norm = {norm:.3f} (not normalized)")
                    
                except Exception as e:
                    norm_issues.append(f"{coll_name}: Error checking normalization - {e}")
            
            results["checks"]["embedding_normalization"] = {
                "passed": len(norm_issues) == 0,
                "issues_found": len(norm_issues),
                "details": norm_issues
            }
            
            logger.info(f"  - Normalization issues: {len(norm_issues)}")
            
        except Exception as e:
            results["issues"].append(f"Could not connect to Milvus: {e}")
            logger.error(f"Milvus connection error: {e}")
        
        return results
    
    # ==================== MAIN QUALITY CHECK RUNNER ====================
    
    def run_all_checks(self) -> Dict:
        """Run all data quality checks and generate report"""
        logger.info("\n" + "="*60)
        logger.info("SPORTSBRAIN DATA QUALITY VALIDATION")
        logger.info("="*60)
        
        all_results = []
        
        # Check each data source
        all_results.append(self.check_strategy_data())
        all_results.append(self.check_trade_data())
        all_results.append(self.check_injury_data())
        all_results.append(self.check_vector_quality())
        
        # Compile summary
        total_checks = 0
        passed_checks = 0
        total_issues = 0
        total_warnings = 0
        
        for result in all_results:
            self.quality_report["sources_checked"].append(result["source"])
            
            for check_name, check_result in result.get("checks", {}).items():
                total_checks += 1
                if check_result.get("passed", False):
                    passed_checks += 1
                
            total_issues += len(result.get("issues", []))
            total_warnings += len(result.get("warnings", []))
        
        self.quality_report["total_checks"] = total_checks
        self.quality_report["passed_checks"] = passed_checks
        self.quality_report["total_issues"] = total_issues
        self.quality_report["warnings"] = total_warnings
        self.quality_report["check_results"] = all_results
        
        # Generate summary
        logger.info("\n" + "="*60)
        logger.info("QUALITY CHECK SUMMARY")
        logger.info("="*60)
        logger.info(f"Total Checks Run: {total_checks}")
        logger.info(f"Checks Passed: {passed_checks}/{total_checks}")
        logger.info(f"Critical Issues: {total_issues}")
        logger.info(f"Warnings: {total_warnings}")
        logger.info(f"Overall Quality Score: {(passed_checks/total_checks*100):.1f}%")
        
        # Save report
        report_file = os.path.join(self.data_dir, 'quality_report.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.quality_report, f, indent=2)
        
        logger.info(f"\nDetailed report saved to: {report_file}")
        
        return self.quality_report


def main():
    """Run data quality checks"""
    checker = DataQualityChecker()
    report = checker.run_all_checks()
    
    # Print pass/fail
    print("\n" + "="*60)
    if report["total_issues"] == 0 and report["passed_checks"] == report["total_checks"]:
        print("[PASS] ALL DATA QUALITY CHECKS PASSED!")
    elif report["total_issues"] == 0:
        print("[WARNING] DATA QUALITY CHECKS PASSED WITH WARNINGS")
    else:
        print("[FAIL] DATA QUALITY ISSUES DETECTED")
    print("="*60)


if __name__ == "__main__":
    main()