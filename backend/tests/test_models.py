"""
Model testing for SportsBrain data models
Tests database models, relationships, and validation
"""
import pytest
from datetime import datetime, date
from sqlalchemy.exc import IntegrityError
from app.models.models import User, Player, Game, GameStats, Team, AgentSession, AgentMessage
from app.db.database import get_db


def skip_if_no_db(func):
    """Decorator to ensure database session is available"""
    def wrapper(self, db_session, *args, **kwargs):
        print(f"skip_if_no_db: db_session type = {type(db_session)}")
        if db_session is None:
            pytest.fail("Database session is None - check database connection")
        return func(self, db_session, *args, **kwargs)
    return wrapper


class TestUserModel:
    """Test User model functionality"""
    
    @skip_if_no_db
    def test_user_creation(self, db_session):
        """Test creating a user with required fields"""
            
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password_here",
            full_name="Test User"
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.created_at is not None
    
    @skip_if_no_db
    def test_user_email_uniqueness(self, db_session):
        """Test that user emails must be unique"""
        user1 = User(
            email="duplicate@example.com",
            username="user1",
            hashed_password="password1"
        )
        user2 = User(
            email="duplicate@example.com",
            username="user2", 
            hashed_password="password2"
        )
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestPlayerModel:
    """Test Player model and Phase 1A enhancements"""
    
    @skip_if_no_db
    def test_player_creation(self, db_session):
        """Test creating a player with basic fields"""
        player = Player(
            name="LeBron James",
            position="SF",
            team="Lakers",
            jersey_number=6,
            height=6.9,
            weight=250,
            nationality="USA"
        )
        db_session.add(player)
        db_session.commit()
        
        assert player.id is not None
        assert player.name == "LeBron James"
        assert player.is_active is True
    
    @skip_if_no_db
    def test_player_phase1a_enhancements(self, db_session):
        """Test Phase 1A enhanced fields"""
        player = Player(
            name="Jayson Tatum",
            position="SF",
            team="Celtics",
            college="Duke",
            playing_style="Versatile Scorer",
            career_start=datetime(2017, 10, 1)
        )
        db_session.add(player)
        db_session.commit()
        
        assert player.college == "Duke"
        assert player.playing_style == "Versatile Scorer"
        assert player.career_start.year == 2017
        assert player.career_end is None  # Still active


class TestGameModel:
    """Test Game model functionality"""
    
    @skip_if_no_db
    def test_game_creation(self, db_session):
        """Test creating a game"""
        game = Game(
            home_team="Lakers",
            away_team="Celtics",
            date=datetime.now(),
            season_type="regular",
            season_year=2024,
            status="scheduled"
        )
        db_session.add(game)
        db_session.commit()
        
        assert game.id is not None
        assert game.home_team == "Lakers"
        assert game.away_team == "Celtics"


class TestGameStatsModel:
    """Test GameStats model and relationships"""
    
    @skip_if_no_db
    def test_game_stats_creation(self, db_session):
        """Test creating game stats with player relationship"""
        # Create player first
        player = Player(name="Stephen Curry", position="PG", team="Warriors")
        db_session.add(player)
        db_session.flush()  # Get ID without committing
        
        # Create game
        game = Game(
            home_team="Warriors",
            away_team="Lakers", 
            date=datetime.now(),
            season_type="regular",
            season_year=2024
        )
        db_session.add(game)
        db_session.flush()
        
        # Create stats
        stats = GameStats(
            player_id=player.id,
            game_id=game.id,
            points=30,
            rebounds=5,
            assists=8,
            steals=2,
            blocks=0,
            field_goals_made=10,
            field_goals_attempted=18,
            three_pointers_made=6,
            three_pointers_attempted=12,
            free_throws_made=4,
            free_throws_attempted=4,
            minutes_played=35
        )
        db_session.add(stats)
        db_session.commit()
        
        assert stats.player_id == player.id
        assert stats.points == 30
        assert stats.player.name == "Stephen Curry"


class TestAgentModels:
    """Test multi-agent system models"""
    
    @skip_if_no_db
    def test_agent_session_creation(self, db_session):
        """Test creating an agent session"""
        # Create user first
        user = User(
            email="agent_test@example.com",
            username="agentuser",
            hashed_password="password"
        )
        db_session.add(user)
        db_session.flush()
        
        session = AgentSession(
            user_id=user.id,
            session_id="test-session-123",
            agent_type="analytics",
            status="active"
        )
        db_session.add(session)
        db_session.commit()
        
        assert session.user_id == user.id
        assert session.status == "active"
    
    @skip_if_no_db
    def test_agent_message_creation(self, db_session):
        """Test creating agent messages"""
        # Create user and session
        user = User(
            email="msg_test@example.com",
            username="msguser", 
            hashed_password="password"
        )
        db_session.add(user)
        db_session.flush()
        
        session = AgentSession(
            user_id=user.id,
            session_id="test-chat-session-456",
            agent_type="chat",
            status="active"
        )
        db_session.add(session)
        db_session.flush()
        
        message = AgentMessage(
            session_id=session.session_id,
            role="user",
            content="Who should I start at point guard?",
            message_metadata={"context": "weekly_lineup"}
        )
        db_session.add(message)
        db_session.commit()
        
        assert message.session_id == session.id
        assert message.agent_type == "ChatAgent"
        assert "point guard" in message.content


class TestModelValidation:
    """Test data validation and constraints"""
    
    @skip_if_no_db
    def test_required_fields_validation(self, db_session):
        """Test that required fields are enforced"""
        # User without email should fail
        user = User(
            username="incomplete_user",
            hashed_password="password"
        )
        db_session.add(user)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    @skip_if_no_db
    def test_relationship_integrity(self, db_session):
        """Test foreign key relationships work correctly"""
        # GameStats without valid player_id should fail
        stats = GameStats(
            player_id=999999,  # Non-existent player
            game_id=1,
            points=20
        )
        db_session.add(stats)
        
        with pytest.raises(IntegrityError):
            db_session.commit()


# Fixtures for database testing
# Removed duplicate db_session fixture - using the one from conftest.py


@pytest.fixture 
def sample_player(db_session):
    """Create a sample player for testing"""
    player = Player(
        name="Test Player",
        position="PG",
        team="Test Team",
        jersey_number=1
    )
    db_session.add(player)
    db_session.commit()
    return player


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing"""
    user = User(
        email="test@sportsbrain.com",
        username="testuser",
        hashed_password="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    return user