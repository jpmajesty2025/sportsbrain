"""Version endpoint to verify deployments"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/version", tags=["version"])

@router.get("/")
async def get_version():
    """Get current version info"""
    return {
        "version": "2024.08.18.diagnostic",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "milvus_fix": "Hit.get() issue fixed",
            "diagnostic_agent": "Active with extensive logging",
            "reranking": "Enabled if Milvus works"
        },
        "debug": {
            "agent_type": "DiagnosticIntelligenceAgent",
            "expected_logs": "Look for DIAGNOSTIC: prefixed messages"
        }
    }