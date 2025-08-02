from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    position = Column(String)
    team = Column(String, index=True)
    jersey_number = Column(Integer)
    height = Column(Float)
    weight = Column(Float)
    birth_date = Column(DateTime)
    nationality = Column(String)
    is_active = Column(Boolean, default=True)
    
    # Phase 1A Enhanced Fields
    college = Column(String)  # Education background
    playing_style = Column(String)  # Analytical style classification
    career_start = Column(DateTime)  # Professional career beginning
    career_end = Column(DateTime)  # Career conclusion if retired (nullable)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    game_stats = relationship("GameStats", back_populates="player")

class Game(Base):
    __tablename__ = "games"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, index=True)
    home_team = Column(String, nullable=False, index=True)
    away_team = Column(String, nullable=False, index=True)
    home_score = Column(Integer)
    away_score = Column(Integer)
    status = Column(String, default="scheduled")  # scheduled, live, completed, postponed
    venue = Column(String)
    week = Column(Integer)
    game_type = Column(String)  # regular, playoff, preseason
    weather_conditions = Column(JSON)
    
    # Phase 1A Enhanced Fields
    season_type = Column(String, index=True)  # Renamed from 'season' for clarity
    season_year = Column(Integer, index=True)  # Extract year separately
    overtime = Column(Boolean, default=False)  # Overtime indicator
    pace = Column(Float)  # Game pace metric
    game_importance = Column(String)  # Context importance (regular, playoff, etc.)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    game_stats = relationship("GameStats", back_populates="game")

class GameStats(Base):
    __tablename__ = "game_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    
    # Basic stats
    points = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    rebounds = Column(Integer, default=0)
    steals = Column(Integer, default=0)
    blocks = Column(Integer, default=0)
    turnovers = Column(Integer, default=0)
    
    # Shooting stats
    field_goals_made = Column(Integer, default=0)
    field_goals_attempted = Column(Integer, default=0)
    three_pointers_made = Column(Integer, default=0)
    three_pointers_attempted = Column(Integer, default=0)
    free_throws_made = Column(Integer, default=0)
    free_throws_attempted = Column(Integer, default=0)
    
    # Time
    minutes_played = Column(Float, default=0.0)
    
    # Advanced stats (can be calculated)
    plus_minus = Column(Integer, default=0)
    
    # Phase 1A Enhanced Fields
    usage_rate = Column(Float)  # Player usage percentage in game
    game_score = Column(Float)  # Advanced efficiency metric
    fantasy_points = Column(Float)  # Platform-specific fantasy scoring
    
    # Additional stats (JSON for flexibility)
    additional_stats = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    player = relationship("Player", back_populates="game_stats")
    game = relationship("Game", back_populates="game_stats")

class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    city = Column(String)
    abbreviation = Column(String, unique=True, index=True)
    conference = Column(String)
    division = Column(String)
    founded_year = Column(Integer)
    colors = Column(JSON)  # Team colors
    logo_url = Column(String)
    is_active = Column(Boolean, default=True)
    
    # Phase 1A Enhanced Fields
    head_coach = Column(String)  # Current coaching staff
    pace_factor = Column(Float)  # Team pace rating for matchup analysis
    offensive_style_rating = Column(Float)  # Offensive approach classification
    defensive_style_rating = Column(Float)  # Defensive approach classification
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class AgentSession(Base):
    __tablename__ = "agent_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String, unique=True, index=True, nullable=False)
    agent_type = Column(String, nullable=False)  # analytics, prediction, chat, etc.
    status = Column(String, default="active")  # active, completed, failed
    context = Column(JSON)  # Session context and state
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")

class AgentMessage(Base):
    __tablename__ = "agent_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("agent_sessions.session_id"), nullable=False)
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON)  # Additional message metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("AgentSession")

class PlayerRiskAssessment(Base):
    __tablename__ = "player_risk_assessment"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    assessment_date = Column(DateTime, nullable=False, index=True)
    
    # Availability Risk (high confidence)
    games_missed_last_30 = Column(Integer, default=0)
    load_management_frequency = Column(Float)  # % of games rested when healthy
    injury_recurrence_risk = Column(String)  # Based on injury type patterns
    
    # Performance Risk (moderate confidence) 
    fantasy_point_variance = Column(Float)  # Game-to-game volatility
    consistency_score = Column(Float)  # % games within 1 std dev
    rest_vs_b2b_differential = Column(Float)  # Performance drop on back-to-backs
    
    # Role Risk (contextual)
    usage_volatility = Column(Float)  # Target share consistency
    bench_risk_flag = Column(Boolean, default=False)  # Coach/depth chart concerns
    
    # Composite
    overall_risk_category = Column(String)  # 'low', 'moderate', 'high'
    confidence_level = Column(Float)  # How much data supports this assessment
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    player = relationship("Player")