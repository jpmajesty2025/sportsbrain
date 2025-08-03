from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import api_router
from app.db.database import engine
from app.models import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="SportsBrain API - AI-powered sports analytics platform",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to SportsBrain API!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "sportsbrain-backend"}

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with database and Redis connectivity"""
    from app.db.database import get_db
    import datetime
    
    health_status = {
        "status": "healthy",
        "service": "sportsbrain-backend",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Database check
    try:
        from sqlalchemy import text
        db = next(get_db())
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Redis check
    try:
        from app.db.redis_client import redis_client
        redis_client.ping()  # Synchronous ping for simplicity
        health_status["checks"]["redis"] = "healthy"
    except ImportError:
        health_status["checks"]["redis"] = "not_configured"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    return health_status