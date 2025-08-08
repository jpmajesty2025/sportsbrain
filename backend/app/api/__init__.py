from fastapi import APIRouter
from .endpoints import auth, users, players, games, agents, milvus_test

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(players.router, prefix="/players", tags=["players"])
api_router.include_router(games.router, prefix="/games", tags=["games"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(milvus_test.router, prefix="/test/milvus", tags=["testing"])