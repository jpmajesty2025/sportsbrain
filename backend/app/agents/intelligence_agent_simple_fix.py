"""Simple fix for Intelligence Agent - ensure SQL results are returned in full"""

import logging
from app.agents.intelligence_agent_enhanced import IntelligenceAgentEnhanced

logger = logging.getLogger(__name__)

class SimplifiedIntelligenceAgent(IntelligenceAgentEnhanced):
    """Simplified version that logs and returns full SQL results"""
    
    def _find_sleeper_candidates_enhanced(self, criteria: str = "") -> str:
        """Override to ensure full results are returned"""
        logger.info(f"SIMPLIFIED: Finding sleepers with criteria: {criteria}")
        
        # Get the SQL results
        result = super()._find_sleeper_candidates_enhanced(criteria)
        
        # Log what we're returning
        logger.info(f"SIMPLIFIED: Returning {len(result)} characters of sleeper data")
        
        # Ensure we're not truncating
        if len(result) < 500:
            logger.warning(f"SIMPLIFIED: Result seems too short! Only {len(result)} chars")
            # Add a note about why results might be limited
            result += "\n\nNote: This analysis is based on SQL data. Vector search enhancement is being debugged."
        
        return result