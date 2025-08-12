import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.config import settings
from app.db.database import get_db, Base
from app.models.models import User, Player, Team, Game, GameStats, AgentSession, AgentMessage
from app.core.security import get_password_hash

# Use SQLite for testing if PostgreSQL is not available
import os


# In CI, use DATABASE_PUBLIC_URL from GitHub secrets
if os.getenv("CI"):
    database_url = os.getenv("DATABASE_PUBLIC_URL")
    if database_url:
        # Use the Railway PostgreSQL database for tests
        # Railway PostgreSQL requires SSL
        SQLALCHEMY_DATABASE_URL = database_url
        # Add SSL requirement if not already in URL
        if "sslmode" not in database_url:
            if "?" in database_url:
                SQLALCHEMY_DATABASE_URL = f"{database_url}&sslmode=require"
            else:
                SQLALCHEMY_DATABASE_URL = f"{database_url}?sslmode=require"
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
    else:
        # Fallback to SQLite if no database URL provided
        SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
        from sqlalchemy.pool import StaticPool
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
else:
    # Local development - use configured test database or SQLite
    SQLALCHEMY_DATABASE_URL = settings.TEST_DATABASE_URL or "sqlite:///./test.db"
    if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
        from sqlalchemy.pool import StaticPool
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db():
    try:
        # Test the connection first
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
        
        if "sqlite" in SQLALCHEMY_DATABASE_URL:
            # For SQLite, we can safely drop and recreate
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)
            yield engine
            Base.metadata.drop_all(bind=engine)
        else:
            # For PostgreSQL, only create tables if they don't exist
            # This is safer for shared databases
            Base.metadata.create_all(bind=engine)
            yield engine
            # Don't drop tables in PostgreSQL - just clean data
    except Exception as e:
        import traceback
        traceback.print_exc()
        pytest.fail(f"Database connection failed: {str(e)}")

@pytest.fixture(scope="function")
def db_session(db):
    """Create a new database session for a test."""
    if db is None:
        pytest.fail("Database fixture returned None - connection failed")
        return None
    
    # db is now the engine from the db fixture    
    if "sqlite" in SQLALCHEMY_DATABASE_URL:
        # SQLite doesn't support nested transactions well
        session = TestingSessionLocal()
        yield session
        session.query(User).delete()
        session.query(Player).delete()
        session.query(Team).delete()
        session.query(Game).delete()
        session.query(GameStats).delete()
        session.query(AgentSession).delete()
        session.query(AgentMessage).delete()
        session.commit()
        session.close()
    else:
        # PostgreSQL with proper transaction isolation
        connection = db.connect()  # Use the db parameter (which is the engine)
        transaction = connection.begin()
        session = TestingSessionLocal(bind=connection)
        yield session
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session):
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=get_password_hash("testpassword"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def authenticated_client(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "testpassword"}
    )
    tokens = response.json()
    client.headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    return client

@pytest.fixture
def auth_headers(client, test_user):
    """Return authorization headers for test user"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "testpassword"}
    )
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}