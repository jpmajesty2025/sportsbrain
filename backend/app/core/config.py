from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "SportsBrain"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql://sportsbrain:password@localhost:5432/sportsbrain"
    TEST_DATABASE_URL: Optional[str] = None
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Milvus (Zilliz Cloud)
    MILVUS_HOST: Optional[str] = None  # URI for Zilliz Cloud
    MILVUS_TOKEN: Optional[str] = None  # API token for Zilliz Cloud
    
    # Milvus Collections
    MILVUS_PLAYERS_COLLECTION: str = "sportsbrain_players"  # Player profiles & stats (dense)
    MILVUS_DRAFT_STRATEGIES_COLLECTION: str = "sportsbrain_strategies"  # Draft strategies & analysis (dense)
    MILVUS_TRADE_NEWS_COLLECTION: str = "sportsbrain_trades"  # Trade news & Reddit posts (hybrid)
    
    # Neo4j (Aura)
    NEO4J_URI: Optional[str] = None
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: Optional[str] = None
    NEO4J_DATABASE: str = "neo4j"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Environment
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # External APIs
    OPENAI_API_KEY: Optional[str] = None
    LANGCHAIN_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()