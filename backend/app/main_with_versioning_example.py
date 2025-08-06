"""
Example of how to structure SportsBrain API with proper versioning
This shows best practices for when you need to support multiple API versions
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import api_router  # This would become v1_router
# from app.api.v2 import api_router as v2_router  # Future v2

# Root application
app = FastAPI(
    title="SportsBrain API",
    description="AI-powered sports analytics platform - All API versions",
    version="2.0.0",  # Overall API version
    docs_url="/docs",  # Root docs showing all mounted apps
    redoc_url="/redoc"
)

# API v1 sub-application
app_v1 = FastAPI(
    title="SportsBrain API v1",
    description="SportsBrain API v1 - Current stable version",
    version="1.0.0",
    openapi_url="/openapi.json",  # Relative to mount point
    docs_url="/docs",  # Will be /api/v1/docs after mounting
    redoc_url="/redoc"  # Will be /api/v1/redoc after mounting
)

# Future: API v2 sub-application
# app_v2 = FastAPI(
#     title="SportsBrain API v2",
#     description="SportsBrain API v2 - Beta version with new features",
#     version="2.0.0",
#     openapi_url="/openapi.json",
#     docs_url="/docs",  # Will be /api/v2/docs after mounting
#     redoc_url="/redoc"
# )

# Add CORS to sub-apps
app_v1.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers in versioned apps
app_v1.include_router(api_router)
# app_v2.include_router(v2_router)

# Mount versioned apps
app.mount("/api/v1", app_v1)
# app.mount("/api/v2", app_v2)

# Root-level endpoints (not versioned)
@app.get("/")
async def root():
    return {
        "message": "Welcome to SportsBrain API!",
        "versions": {
            "v1": {
                "status": "stable",
                "docs": "/api/v1/docs",
                "base_url": "/api/v1"
            },
            # "v2": {
            #     "status": "beta",
            #     "docs": "/api/v2/docs",
            #     "base_url": "/api/v2"
            # }
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "sportsbrain-backend"}

# v1 specific health check
@app_v1.get("/health")
async def v1_health_check():
    return {"status": "healthy", "service": "sportsbrain-backend", "version": "v1"}

# Mount health endpoint at root level too for backwards compatibility
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
        redis_client.ping()
        health_status["checks"]["redis"] = "healthy"
    except ImportError:
        health_status["checks"]["redis"] = "not_configured"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    return health_status