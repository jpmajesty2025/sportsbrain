# SportsBrain Data Model Enhancement Plan
## Phase 1 Implementation Strategy

### Overview
This plan details the systematic enhancement of the current basic data models to implement the Phase 1 enhanced data model as specified in `enhanced_phase1_data_model.mermaid`. The approach prioritizes community intelligence, personalization, and mobile optimization features.

## Current State Analysis

### ✅ Already Implemented (Basic Models)
- **User**: Basic auth fields (id, email, username, password, etc.)
- **Player**: Basic info (id, name, position, team, height, weight, etc.)
- **Game**: Basic game info (id, date, teams, scores, status, etc.) 
- **GameStats**: Player performance stats (points, rebounds, assists, shooting, etc.)
- **Team**: Basic team info (id, name, city, abbreviation, conference, etc.)
- **AgentSession**: Multi-agent session tracking
- **AgentMessage**: Conversation history

### 🚫 Missing Phase 1 Enhanced Models
- Community Intelligence: `COMMUNITY_SENTIMENT`, `EXPERT_CONSENSUS`
- User Personalization: `USER_PREFERENCES`, `USER_DECISIONS`, `USER_QUERIES`
- Matchup Analysis: `OPPONENT_MATCHUP`, `DEFENSIVE_PROFILE`
- Enhanced Analytics: `GAME_LINEUP`, enhanced `TEAM_STATS`, `PLAYER_TEAM_HISTORY`
- Content Intelligence: `NEWS_ARTICLE`, `INJURY_REPORT`, `SEASON`

## Enhancement Implementation Plan

### Phase 1A: Enhance Existing Models (Foundation)

#### 1. **PLAYER Model Enhancements**
```python
# ADD to existing Player model:
- college: String  # Education background
- playing_style: String  # Analytical style classification
- career_start: Date  # Professional career beginning
- career_end: Date (nullable)  # Career conclusion if retired
```

#### 1b. **PLAYER_RISK_ASSESSMENT Model** (NEW - Replaces injury_risk_score)
```python
class PlayerRiskAssessment(Base):
    __tablename__ = "player_risk_assessment"
    
    assessment_id: Integer (PK)
    player_id: Integer (FK to Player)
    assessment_date: Date
    
    # Availability Risk (high confidence)
    games_missed_last_30: Integer
    load_management_frequency: Float  # % of games rested when healthy
    injury_recurrence_risk: String  # Based on injury type patterns
    
    # Performance Risk (moderate confidence) 
    fantasy_point_variance: Float  # Game-to-game volatility
    consistency_score: Float  # % games within 1 std dev
    rest_vs_b2b_differential: Float  # Performance drop on back-to-backs
    
    # Role Risk (contextual)
    usage_volatility: Float  # Target share consistency
    bench_risk_flag: Boolean  # Coach/depth chart concerns
    
    # Composite
    overall_risk_category: String  # 'low', 'moderate', 'high'
    confidence_level: Float  # How much data supports this assessment
    created_at: DateTime
    updated_at: DateTime
```

#### 2. **TEAM Model Enhancements**  
```python
# ADD to existing Team model:
- head_coach: String  # Current coaching staff
- pace_factor: Float  # Team pace rating for matchup analysis
- offensive_style_rating: Float  # Offensive approach classification
- defensive_style_rating: Float  # Defensive approach classification
```

#### 3. **GAME Model Enhancements**
```python  
# ADD to existing Game model:
- overtime: Boolean  # Overtime indicator
- pace: Float  # Game pace metric
- game_importance: String  # Context importance (regular, playoff, etc.)
- season: String -> season_type: String  # Rename for clarity
- season_year: Integer  # Extract year separately
```

#### 4. **Enhanced GAME_STATS → PLAYER_STATS**
```python
# ADD to existing GameStats model (rename to PlayerStats):
- usage_rate: Float  # Player usage percentage in game
- game_score: Float  # Advanced efficiency metric
- fantasy_points: Float  # Platform-specific fantasy scoring
```

### Phase 1B: New Community Intelligence Models

#### 5. **COMMUNITY_SENTIMENT Model** (NEW)
```python
class CommunitySentiment(Base):
    __tablename__ = "community_sentiment"
    
    sentiment_id: Integer (PK)
    player_id: Integer (FK to Player)
    sentiment_date: Date
    source_platform: String  # 'reddit', 'twitter', 'expert'
    sentiment_score: Float  # -1 to +1 sentiment rating
    mention_count: Integer  # Volume of mentions
    confidence_level: Float  # Model confidence in sentiment
    trending_direction: String  # 'up', 'down', 'stable'
    created_at: DateTime
    updated_at: DateTime
```

#### 6. **EXPERT_CONSENSUS Model** (NEW)
```python
class ExpertConsensus(Base):
    __tablename__ = "expert_consensus"
    
    consensus_id: Integer (PK)
    player_id: Integer (FK to Player)
    game_id: Integer (FK to Game, nullable)
    analysis_date: Date
    start_percentage: Float  # % of experts recommending start
    ownership_percentage: Float  # DFS ownership projection
    consensus_rating: String  # 'strong_start', 'weak_start', etc.
    expert_source: String  # 'fantasypros', 'rotogrinders', etc.
    created_at: DateTime
    updated_at: DateTime
```

### Phase 1C: User Personalization Models

#### 7. **Enhanced USER Model** 
```python
# Keep User model clean - identity only:
# No changes needed to existing User model
# (Remove planned additions: subscription_tier, risk_tolerance, preferred_analysis_depth, mobile_user)
```

#### 7b. **USER_SUBSCRIPTION Model** (NEW - Separate subscription management)
```python
class UserSubscription(Base):
    __tablename__ = "user_subscription"
    
    subscription_id: Integer (PK)
    user_id: Integer (FK to User)
    tier: String  # 'free', 'premium', 'pro'
    start_date: Date
    end_date: Date (nullable)  # Null for active subscriptions
    billing_cycle: String  # 'monthly', 'yearly'
    status: String  # 'active', 'cancelled', 'expired', 'trial'
    created_at: DateTime
    updated_at: DateTime
```

#### 8. **USER_PREFERENCES Model** (NEW - Now includes moved User fields)
```python
class UserPreferences(Base):
    __tablename__ = "user_preferences"
    
    preference_id: Integer (PK)
    user_id: Integer (FK to User)
    preference_type: String  # Examples:
        # 'risk_tolerance' -> 'conservative'/'moderate'/'aggressive'
        # 'analysis_depth' -> 'quick'/'detailed'/'expert'
        # 'device_preference' -> 'mobile'/'desktop'/'tablet'
        # 'player_type' -> 'safe'/'boom_bust'/'contrarian'
        # 'notification' -> 'injury_alerts'/'lineup_suggestions'
    preference_value: String  # Specific preference value
    weight: Float  # Preference strength (0-1)
    last_updated: DateTime
    created_at: DateTime
```

#### 9. **USER_DECISIONS Model** (NEW)
```python
class UserDecisions(Base):
    __tablename__ = "user_decisions"
    
    decision_id: Integer (PK)
    user_id: Integer (FK to User)
    player_id: Integer (FK to Player)
    decision_type: String  # 'start', 'sit', 'trade', 'draft'
    decision_value: String  # Specific decision made
    decision_date: DateTime
    outcome: String  # 'correct', 'incorrect', 'partial' (nullable)
    accuracy_score: Float  # Decision accuracy (0-1, nullable)
    created_at: DateTime
```

#### 10. **USER_QUERIES Model** (NEW)
```python
class UserQueries(Base):
    __tablename__ = "user_queries"
    
    query_id: Integer (PK)
    user_id: Integer (FK to User)
    query_text: Text  # Full user query
    query_category: String  # 'player_analysis', 'matchup', 'general'
    query_time: DateTime
    response_time: Float  # Milliseconds to response
    satisfaction_score: Float  # User feedback (1-5, nullable)
    device_type: String  # 'mobile', 'desktop', 'tablet'
    created_at: DateTime
```

### Phase 1D: Enhanced Matchup Analysis Models

#### 11. **OPPONENT_MATCHUP Model** (NEW)
```python
class OpponentMatchup(Base):
    __tablename__ = "opponent_matchup"
    
    matchup_id: Integer (PK)
    player_id: Integer (FK to Player)
    opponent_team_id: Integer (FK to Team)
    opponent_position: String  # Position player matches up against
    historical_performance: Float  # Avg performance vs this opponent
    defensive_rating_vs_position: Float  # Opponent's defense vs position
    key_advantages: Text  # Textual analysis of advantages
    key_concerns: Text  # Textual analysis of concerns
    created_at: DateTime
    updated_at: DateTime
```

#### 12. **DEFENSIVE_PROFILE Model** (NEW)
```python
class DefensiveProfile(Base):
    __tablename__ = "defensive_profile"
    
    profile_id: Integer (PK)
    team_id: Integer (FK to Team)
    position_defended: String  # 'PG', 'SG', 'SF', 'PF', 'C'
    points_allowed_per_game: Float  # Avg points allowed to position
    field_goal_pct_allowed: Float  # FG% allowed to position
    three_pt_pct_allowed: Float  # 3P% allowed to position
    defensive_style: String  # 'aggressive', 'conservative', 'switching'
    key_weaknesses: Text  # Textual analysis of weaknesses
    created_at: DateTime
    updated_at: DateTime
```

### Phase 1E: Enhanced Analytics Models

#### 13. **GAME_LINEUP Model** (NEW)
```python
class GameLineup(Base):
    __tablename__ = "game_lineup"
    
    lineup_id: Integer (PK)
    game_id: Integer (FK to Game)
    player_id: Integer (FK to Player)
    is_starter: Boolean
    lineup_position: Integer  # 1-5 for starting lineup
    position_played: String  # Actual position in game
    minutes_played: Integer
    usage_rate: Float  # Usage rate in this game
    created_at: DateTime
```

#### 14. **Enhanced TEAM_STATS Model**
```python
# ADD to existing TeamStats model:
- three_pt_allowed_pct: Float  # 3P% allowed by team
- paint_points_allowed: Float  # Points in paint allowed
```

#### 15. **PLAYER_TEAM_HISTORY Model** (NEW)
```python
class PlayerTeamHistory(Base):
    __tablename__ = "player_team_history"
    
    history_id: Integer (PK)
    player_id: Integer (FK to Player)
    team_id: Integer (FK to Team)
    start_date: Date
    end_date: Date (nullable)
    primary_position: String
    was_starter: Boolean
    avg_minutes: Float  # Average minutes per game
    role_description: String  # Role on team
    created_at: DateTime
```

### Phase 1F: Content Intelligence Models

#### 16. **NEWS_ARTICLE Model** (NEW)
```python
class NewsArticle(Base):
    __tablename__ = "news_article"
    
    article_id: Integer (PK)
    title: String
    content: Text
    source: String  # 'ESPN', 'The Athletic', etc.
    publish_date: DateTime
    url: String
    sentiment: String  # 'positive', 'negative', 'neutral'
    relevance_score: Float  # Relevance to fantasy (0-1)
    player_id: Integer (FK to Player, nullable)
    team_id: Integer (FK to Team, nullable)
    created_at: DateTime
```

#### 17. **INJURY_REPORT Model** (NEW)
```python
class InjuryReport(Base):
    __tablename__ = "injury_report"
    
    injury_id: Integer (PK)
    player_id: Integer (FK to Player)
    injury_type: String  # 'ankle', 'knee', 'back', etc.
    injury_date: Date
    severity: String  # 'minor', 'moderate', 'major'
    status: String  # 'day-to-day', 'out', 'probable', etc.
    expected_return: Date (nullable)
    impact_rating: Float  # Expected impact on performance (0-1)
    affected_stats: String  # Which stats likely affected
    created_at: DateTime
    updated_at: DateTime
```

#### 18. **SEASON Model** (NEW)
```python
class Season(Base):
    __tablename__ = "season"
    
    season_id: Integer (PK)
    year: Integer  # 2024, 2025, etc.
    type: String  # 'regular', 'playoff', 'preseason'
    start_date: Date
    end_date: Date
    created_at: DateTime
```

## Database Migration Strategy

### Migration Order (Minimize Dependencies)
1. **Phase 1A**: Enhance existing models (add columns)
2. **Phase 1F**: Add independent models (Season, NewsArticle, InjuryReport)
3. **Phase 1C**: Add user personalization models  
4. **Phase 1B**: Add community intelligence models
5. **Phase 1D**: Add matchup analysis models
6. **Phase 1E**: Add enhanced analytics models

### Indexing Strategy for Performance
```python
# Critical indexes for mobile performance (<1.5s targets)
- player_risk_assessment(player_id, assessment_date)  # NEW: Risk data access
- user_subscription(user_id, status, end_date)  # NEW: Subscription management
- community_sentiment(player_id, sentiment_date)
- expert_consensus(player_id, analysis_date)  
- user_preferences(user_id, preference_type)
- user_decisions(user_id, decision_date)
- user_queries(user_id, query_time)
- opponent_matchup(player_id, opponent_team_id)
- defensive_profile(team_id, position_defended)
- news_article(player_id, publish_date)
- injury_report(player_id, status, injury_date)

# Composite indexes for complex queries
- player_stats(player_id, game_id)  # Already exists
- game_lineup(game_id, player_id)
- community_sentiment(player_id, source_platform, sentiment_date)
- player_risk_assessment(player_id, overall_risk_category, assessment_date)  # NEW
- user_subscription(user_id, tier, status)  # NEW: Quick subscription lookups
```

## Mobile Optimization Considerations

### Database Design for <1.5s Response Times
1. **Denormalization**: Add calculated fields to reduce joins
2. **Caching Strategy**: Redis integration for hot data
3. **Pagination**: Limit result sets for mobile queries
4. **Selective Loading**: Only fetch required fields for mobile

### Mobile-First Columns to Add
```python
# Add to relevant models:
- mobile_optimized: Boolean  # Flag for mobile-ready data
- quick_summary: String  # Pre-calculated mobile summary
- priority_score: Float  # For mobile result ranking
```

## Implementation Timeline

### Week 1-2: Foundation Enhancement
- [ ] Enhance existing models (Phase 1A)
- [ ] Create database migration scripts
- [ ] Add basic indexes

### Week 3-4: Core Intelligence Models  
- [ ] Implement community intelligence models (Phase 1B)
- [ ] Implement user personalization models (Phase 1C)
- [ ] Add relationship configurations

### Week 5-6: Advanced Features
- [ ] Implement matchup analysis models (Phase 1D)  
- [ ] Implement enhanced analytics models (Phase 1E)
- [ ] Implement content intelligence models (Phase 1F)

### Week 7-8: Optimization & Testing
- [ ] Performance optimization and indexing
- [ ] Mobile response time testing
- [ ] Data migration validation
- [ ] Integration testing with existing agents

## Testing Strategy

### Model Testing Requirements
1. **Unit Tests**: Each model's CRUD operations
2. **Relationship Tests**: FK constraints and joins
3. **Performance Tests**: Query response times
4. **Migration Tests**: Safe schema changes
5. **Mobile Tests**: Response payload size validation

### Success Criteria
- [ ] All models pass unit tests
- [ ] Mobile queries respond in <1.5s
- [ ] Zero data loss during migration
- [ ] All relationships function correctly
- [ ] Indexing improves query performance by >50%

## Risk Mitigation

### Potential Issues & Solutions
1. **Large Migration**: Use staged rollout with feature flags
2. **Performance Impact**: Implement indexes before data load
3. **Data Integrity**: Extensive validation during migration
4. **Mobile Performance**: Pre-aggregate common queries
5. **Storage Growth**: Implement data retention policies

## Next Steps After This Plan
1. **Review & Approval**: Validate plan with stakeholders
2. **Implementation**: Begin Phase 1A model enhancements
3. **Agent Integration**: Update agents to use new models
4. **API Enhancement**: Extend endpoints for new data
5. **Frontend Integration**: Update UI for new features

---

*This plan provides the foundation for SportsBrain's Phase 1 enhanced data model, enabling community intelligence, personalization, and mobile-first features as specified in the design documents.*