# Enhanced Data Ingestion Strategy & Quality Framework

## Phase 1 MVP Ingestion Architecture with Community Intelligence

### Core Data Sources & Integration Patterns

#### Primary Data Sources
**NBA Stats API (stats.nba.com)**
- **Endpoints**: Player stats, game logs, team information, historical data, defensive ratings
- **Rate Limits**: 600 requests/hour, burst allowance of 200
- **Data Format**: JSON with nested player/team objects
- **Update Frequency**: Real-time during games, daily for historical data
- **Reliability**: High (official NBA source)
- **Mobile Optimization**: Compressed payloads for mobile endpoints

**ESPN API**
- **Endpoints**: News articles, injury reports, game schedules, expert analysis
- **Rate Limits**: 1000 requests/hour
- **Data Format**: JSON with rich metadata
- **Update Frequency**: Real-time for breaking news, hourly for routine updates
- **Reliability**: High with occasional maintenance windows

**Basketball Reference (Web Scraping)**
- **Endpoints**: Advanced metrics, historical player comparisons, opponent-specific data
- **Rate Limits**: Self-imposed 10 requests/minute to avoid blocking
- **Data Format**: HTML tables requiring parsing
- **Update Frequency**: Daily batch processing
- **Reliability**: Medium (subject to website changes)

#### **NEW: Community Intelligence Data Sources**

**Reddit API (r/fantasybball)**
- **Endpoints**: Subreddit posts, comments, upvote patterns, user sentiment
- **Rate Limits**: 60 requests/minute with OAuth
- **Data Format**: JSON with comment trees and metadata
- **Update Frequency**: Real-time for trending posts, hourly for sentiment analysis
- **Reliability**: High with rate limiting considerations
- **Content Types**: Player discussions, start/sit advice, community consensus

**Twitter API (X API)**
- **Endpoints**: Tweets, trending hashtags, expert opinions, breaking news
- **Rate Limits**: 300 requests per 15-minute window (Essential tier)
- **Data Format**: JSON with engagement metrics
- **Update Frequency**: Real-time for breaking news, every 15 minutes for sentiment
- **Reliability**: High but requires robust error handling
- **Focus Areas**: NBA experts, fantasy analysts, injury reporters

**Expert Consensus APIs**
- **FantasyPros API**: Start/sit recommendations, ownership percentages, expert rankings
- **Rate Limits**: 1000 requests/day (paid tier)
- **Data Format**: JSON with confidence scores
- **Update Frequency**: Daily updates, real-time during active periods
- **Reliability**: Very high (paid service)

### Enhanced Ingestion Patterns by Data Type

#### Real-time Streaming Data (Enhanced for Community)
```python
# Enhanced real-time for game updates + community buzz
async def enhanced_stream_processor():
    """Process game updates, injuries, and community reactions"""
    while game_active:
        try:
            # Traditional game data
            game_data = await nba_api.get_live_game_data(game_id)
            
            # NEW: Community sentiment during games
            community_buzz = await community_processor.get_live_sentiment(game_id)
            
            # NEW: Expert real-time opinions
            expert_updates = await expert_consensus.get_live_updates(game_id)
            
            # Process all streams together
            await process_enhanced_live_update(game_data, community_buzz, expert_updates)
            await asyncio.sleep(30)
            
        except RateLimitException:
            await asyncio.sleep(60)  # Backoff strategy
```

#### Enhanced Batch Processing (Primary Pattern for Phase 1)
```python
# Enhanced daily batch ingestion workflow
class EnhancedDailyIngestionPipeline:
    async def run_enhanced_daily_pipeline(self):
        """Execute enhanced daily data ingestion with community intelligence"""
        
        # 1. Traditional data (enhanced)
        await self.ingest_team_rosters()
        await self.ingest_player_profiles()
        await self.ingest_defensive_profiles()  # NEW: Team defensive breakdowns
        
        # 2. Game data (yesterday's completed games)
        game_ids = await self.get_completed_games(date.yesterday())
        for game_id in game_ids:
            await self.ingest_game_data(game_id)
            await self.ingest_player_stats(game_id)
            await self.ingest_team_stats(game_id)
            await self.ingest_opponent_matchup_data(game_id)  # NEW
        
        # 3. NEW: Community intelligence data
        await self.ingest_reddit_sentiment()
        await self.ingest_twitter_trends()
        await self.ingest_expert_consensus()
        
        # 4. Enhanced contextual data
        await self.ingest_injury_reports()
        await self.ingest_news_articles()
        await self.process_sentiment_analysis()  # NEW
        
        # 5. NEW: User behavior data (privacy-compliant)
        await self.process_user_interaction_patterns()
        await self.update_personalization_models()
        
        # 6. Enhanced data quality validation
        await self.run_enhanced_quality_checks()
        
        # 7. NEW: Mobile optimization
        await self.prepare_mobile_optimized_payloads()
```

#### **NEW: User Interaction Stream Processing**
```python
class UserInteractionProcessor:
    """Process user queries and decisions for personalization"""
    
    async def process_user_stream(self):
        """Real-time user interaction processing"""
        async for user_event in self.user_event_stream:
            # Extract user preferences
            await self.extract_preferences(user_event)
            
            # Update user risk profile
            await self.update_risk_tolerance(user_event)
            
            # Track decision accuracy
            if user_event.type == "decision_outcome":
                await self.track_decision_accuracy(user_event)
            
            # Update mobile behavior patterns
            if user_event.device_type == "mobile":
                await self.update_mobile_preferences(user_event)
```

### Enhanced Data Quality Framework

#### Enhanced Schema Validation Layer
```python
from pydantic import BaseModel, validator
from typing import Optional
from datetime import date

class EnhancedPlayerStatsSchema(BaseModel):
    """Enhanced data quality with community context"""
    game_id: int
    player_id: int
    minutes_played: int
    points: int
    rebounds: int
    assists: int
    fantasy_points: float  # NEW: Pre-calculated fantasy points
    community_sentiment: Optional[float] = None  # NEW: -1 to 1 sentiment score
    expert_consensus: Optional[str] = None  # NEW: start/sit consensus
    
    @validator('minutes_played')
    def validate_minutes(cls, v):
        if v < 0 or v > 58:  # Account for overtime
            raise ValueError('Minutes must be between 0 and 58')
        return v
    
    @validator('community_sentiment')
    def validate_sentiment(cls, v):
        if v is not None and (v < -1 or v > 1):
            raise ValueError('Sentiment must be between -1 and 1')
        return v

class CommunityDataSchema(BaseModel):
    """Validation for community intelligence data"""
    player_id: int
    sentiment_score: float
    mention_count: int
    source_platform: str
    confidence_level: float
    trending_direction: str
    
    @validator('sentiment_score')
    def validate_sentiment_range(cls, v):
        if v < -1 or v > 1:
            raise ValueError('Sentiment score must be between -1 and 1')
        return v
    
    @validator('source_platform')
    def validate_platform(cls, v):
        allowed_platforms = ['reddit', 'twitter', 'expert_consensus']
        if v not in allowed_platforms:
            raise ValueError(f'Platform must be one of {allowed_platforms}')
        return v

class UserInteractionSchema(BaseModel):
    """Privacy-compliant user interaction validation"""
    user_id: str  # Hashed/anonymized
    query_type: str
    device_type: str
    response_time: float
    satisfaction_score: Optional[float] = None
    
    @validator('device_type')
    def validate_device(cls, v):
        allowed_devices = ['mobile', 'desktop', 'tablet']
        if v not in allowed_devices:
            raise ValueError(f'Device type must be one of {allowed_devices}')
        return v
```

#### Enhanced Data Quality Checker
```python
class EnhancedDataQualityChecker:
    """Comprehensive quality validation with community intelligence"""
    
    def check_completeness(self, data: dict) -> QualityScore:
        """Enhanced completeness checking"""
        required_fields = ['player_id', 'game_id', 'points', 'rebounds', 'assists']
        optional_enhanced_fields = ['community_sentiment', 'expert_consensus', 'fantasy_points']
        
        missing_required = [f for f in required_fields if f not in data or data[f] is None]
        missing_enhanced = [f for f in optional_enhanced_fields if f not in data or data[f] is None]
        
        # Calculate completeness score including enhanced fields
        total_fields = len(required_fields) + len(optional_enhanced_fields)
        missing_total = len(missing_required) + len(missing_enhanced)
        completeness_score = (total_fields - missing_total) / total_fields
        
        return QualityScore(
            metric='enhanced_completeness', 
            score=completeness_score, 
            required_issues=missing_required,
            enhanced_issues=missing_enhanced
        )
    
    def check_community_data_quality(self, community_data: List[CommunityData]) -> QualityScore:
        """Validate community intelligence data quality"""
        issues = []
        
        # Check sentiment distribution (should be somewhat balanced)
        sentiments = [data.sentiment_score for data in community_data]
        avg_sentiment = sum(sentiments) / len(sentiments)
        
        if abs(avg_sentiment) > 0.8:  # Extremely skewed sentiment
            issues.append(f"Sentiment heavily skewed: {avg_sentiment:.2f}")
        
        # Check mention volume (detect spam/bot activity)
        total_mentions = sum(data.mention_count for data in community_data)
        if total_mentions < 10:  # Too few mentions for reliable sentiment
            issues.append(f"Insufficient mention volume: {total_mentions}")
        
        # Check confidence levels
        low_confidence_count = sum(1 for data in community_data if data.confidence_level < 0.5)
        if low_confidence_count > len(community_data) * 0.7:  # More than 70% low confidence
            issues.append("High proportion of low-confidence sentiment data")
        
        quality_score = 1.0 - (len(issues) * 0.2)  # Deduct 0.2 per issue
        return QualityScore(
            metric='community_data_quality',
            score=max(quality_score, 0.0),
            issues=issues
        )
    
    def check_mobile_optimization(self, response_data: dict) -> QualityScore:
        """Validate mobile-optimized payload quality"""
        issues = []
        
        # Check payload size (should be < 50KB for mobile)
        payload_size = len(str(response_data).encode('utf-8'))
        if payload_size > 50000:  # 50KB limit
            issues.append(f"Payload too large for mobile: {payload_size} bytes")
        
        # Check required mobile fields
        mobile_fields = ['quick_actions', 'essential_info', 'progressive_data']
        missing_mobile = [f for f in mobile_fields if f not in response_data]
        
        if missing_mobile:
            issues.append(f"Missing mobile optimization fields: {missing_mobile}")
        
        mobile_score = 1.0 if not issues else 0.7
        return QualityScore(
            metric='mobile_optimization',
            score=mobile_score,
            issues=issues
        )
```

### Enhanced Error Handling & Recovery Strategies

#### **NEW: Community Data Resilience**
```python
class CommunityDataResilientIngestion:
    """Handle community API failures with graceful degradation"""
    
    async def ingest_community_data_with_fallback(self, player_id: str):
        """Multi-tier community data fallback strategy"""
        
        # Primary: Real-time Reddit + Twitter
        try:
            reddit_sentiment = await self.reddit_api.get_player_sentiment(player_id)
            twitter_sentiment = await self.twitter_api.get_player_sentiment(player_id)
            
            if self.validate_community_data(reddit_sentiment, twitter_sentiment):
                return self.combine_sentiment_sources(reddit_sentiment, twitter_sentiment)
                
        except (APIException, ValidationException) as e:
            self.log_error(f"Real-time community data failed: {e}")
        
        # Secondary: Expert consensus only
        try:
            expert_data = await self.expert_consensus_api.get_player_consensus(player_id)
            if self.validate_expert_data(expert_data):
                self.log_warning(f"Using expert consensus only for {player_id}")
                return self.format_expert_as_community_data(expert_data)
                
        except Exception as e:
            self.log_error(f"Expert consensus failed: {e}")
        
        # Tertiary: Cached community data
        cached_community = await self.get_cached_community_data(player_id)
        if cached_community and self.is_cache_fresh(cached_community, max_age_hours=6):
            self.log_warning(f"Using cached community data for {player_id}")
            return cached_community
        
        # Fallback: No community data (graceful degradation)
        return self.get_minimal_community_fallback(player_id)
```

### **NEW: Mobile-First Data Pipeline**

#### Mobile Optimization Layer
```python
class MobileDataOptimizer:
    """Optimize data payloads for mobile consumption"""
    
    def optimize_for_mobile(self, full_data: dict, user_context: dict) -> dict:
        """Create mobile-optimized data payload"""
        
        mobile_payload = {
            # Essential info first
            "essential": {
                "recommendation": full_data.get("recommendation"),
                "confidence": full_data.get("confidence_score"),
                "key_reason": full_data.get("primary_reasoning")
            },
            
            # Quick actions
            "quick_actions": [
                {"label": "Start Player", "action": "start", "confidence": 0.85},
                {"label": "Get Alerts", "action": "notify", "player_id": full_data.get("player_id")}
            ],
            
            # Community proof (social validation)
            "social_proof": {
                "expert_consensus": full_data.get("expert_start_percentage", "N/A"),
                "community_sentiment": full_data.get("community_sentiment_summary", "Neutral")
            },
            
            # Progressive data (load on demand)
            "progressive_data_available": True,
            "detailed_analysis_url": f"/api/detailed/{full_data.get('player_id')}"
        }
        
        # Personalization for mobile
        if user_context.get("risk_tolerance") == "conservative":
            mobile_payload["essential"]["risk_note"] = "Matches your conservative approach"
        
        return mobile_payload

    def prepare_progressive_data(self, full_data: dict) -> dict:
        """Prepare detailed data for progressive loading"""
        return {
            "detailed_stats": full_data.get("statistical_analysis"),
            "matchup_breakdown": full_data.get("opponent_analysis"),
            "historical_context": full_data.get("historical_comparisons"),
            "injury_impact": full_data.get("injury_analysis")
        }
```

### Enhanced Monitoring & Alerting

#### **NEW: Community Data Health Metrics**
```python
class EnhancedIngestionMonitoring:
    """Track enhanced pipeline health including community intelligence"""
    
    async def track_enhanced_pipeline_metrics(self):
        """Collect enhanced metrics including community data"""
        
        traditional_metrics = {
            'records_processed_last_hour': await self.count_recent_records(),
            'data_quality_score': await self.calculate_quality_score(),
            'api_success_rate': await self.calculate_api_success_rate(),
            'average_processing_latency': await self.get_avg_latency(),
        }
        
        # NEW: Community intelligence metrics
        community_metrics = {
            'community_sentiment_accuracy': await self.validate_sentiment_predictions(),
            'expert_consensus_availability': await self.check_expert_consensus_coverage(),
            'reddit_api_health': await self.check_reddit_api_status(),
            'twitter_api_health': await self.check_twitter_api_status(),
            'community_data_freshness': await self.get_community_data_age()
        }
        
        # NEW: Mobile optimization metrics
        mobile_metrics = {
            'mobile_payload_avg_size': await self.get_avg_mobile_payload_size(),
            'mobile_response_time': await self.get_mobile_response_times(),
            'progressive_loading_success_rate': await self.get_progressive_loading_success(),
            'mobile_user_satisfaction': await self.get_mobile_satisfaction_scores()
        }
        
        # NEW: User personalization metrics
        personalization_metrics = {
            'user_preference_learning_rate': await self.get_preference_learning_metrics(),
            'recommendation_accuracy_improvement': await self.get_recommendation_improvements(),
            'user_decision_tracking_health': await self.get_decision_tracking_health(),
            'privacy_compliance_score': await self.validate_privacy_compliance()
        }
        
        all_metrics = {
            **traditional_metrics,
            **community_metrics,
            **mobile_metrics,
            **personalization_metrics
        }
        
        # Enhanced alerting
        await self.check_enhanced_alerts(all_metrics)
        
        return all_metrics
    
    async def check_enhanced_alerts(self, metrics: dict):
        """Enhanced alerting for community and mobile features"""
        
        # Traditional alerts (enhanced thresholds)
        if metrics['data_quality_score'] < 0.90:  # Raised from 0.85
            await self.send_alert(
                severity='high',
                message=f"Data quality degraded: {metrics['data_quality_score']:.2f}"
            )
        
        # NEW: Community intelligence alerts
        if metrics['community_sentiment_accuracy'] < 0.70:
            await self.send_alert(
                severity='medium',
                message=f"Community sentiment accuracy low: {metrics['community_sentiment_accuracy']:.2f}"
            )
        
        if metrics['community_data_freshness'] > 3600:  # More than 1 hour old
            await self.send_alert(
                severity='medium',
                message="Community data becoming stale"
            )
        
        # NEW: Mobile performance alerts
        if metrics['mobile_response_time'] > 1.5:  # Mobile SLA
            await self.send_alert(
                severity='high',
                message=f"Mobile response time SLA breach: {metrics['mobile_response_time']:.2f}s"
            )
        
        # NEW: Personalization health alerts
        if metrics['user_decision_tracking_health'] < 0.95:
            await self.send_alert(
                severity='low',
                message="User decision tracking experiencing issues"
            )
```

### Success Metrics & KPIs (Enhanced)

#### Technical Metrics (Enhanced)
- **Ingestion Completeness**: 99.5% of available data successfully ingested
- **Enhanced Data Quality Score**: Composite score >95% across all quality dimensions including community data
- **Processing Latency**: <5 minutes for batch data, <30 seconds for streaming, <15 seconds for community sentiment
- **API Reliability**: 99% uptime across all external data sources including community APIs
- **Error Recovery**: 100% of transient failures automatically recovered
- **NEW: Community Data Accuracy**: >70% sentiment prediction accuracy validated against outcomes
- **NEW: Mobile Performance**: <1.5s response time for mobile-optimized endpoints
- **NEW: Personalization Learning**: >15% improvement in user recommendation accuracy over baseline

#### Business Metrics (Enhanced)
- **Data Coverage**: Complete player/game coverage for target analysis scenarios
- **Historical Depth**: 20+ years of historical data for cross-era comparisons
- **Update Frequency**: Daily updates for historical data, real-time during games, real-time community sentiment
- **Analysis Readiness**: Data available for agent consumption within SLA
- **NEW: Community Engagement**: >60% of users actively engaging with community features
- **NEW: Mobile Adoption**: >70% of queries coming from mobile-optimized endpoints
- **NEW: User Satisfaction**: >4.0/5.0 rating with enhanced features including community intelligence

This enhanced ingestion strategy demonstrates enterprise-grade thinking while remaining implementable for Phase 1 MVP, with clear evolution paths for future phases and full integration of market-validated community intelligence and mobile-first optimization features.