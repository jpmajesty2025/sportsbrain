"""
Professional error messages for agent failures
"""
from typing import Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def get_friendly_error_message(agent_type: str, query: str = "", error_type: str = "timeout") -> str:
    """
    Generate a professional error message and log the failure for analysis
    
    Args:
        agent_type: Type of agent (intelligence, draft_prep, trade_impact)
        query: The original user query (optional)
        error_type: Type of error (timeout, iteration_limit, general)
    
    Returns:
        A professional, apologetic error message
    """
    
    # Log the error for later analysis
    timestamp = datetime.now().isoformat()
    logger.error(f"Agent Failure - Time: {timestamp}, Agent: {agent_type}, Error: {error_type}, Query: {query}")
    
    # TODO: In production, this should write to a database or external logging service
    # For now, it just logs to console/file depending on Railway's logging setup
    
    # Return a simple, professional message
    return ("I apologize for the inconvenience. I am unable to complete your request at this time. "
            "At SportsBrain, we're always working hard to improve user experience. "
            "This interaction has been logged for later analysis.")


def get_partial_success_message(agent_type: str, partial_data: Optional[str] = None) -> str:
    """
    Generate a message when we have partial results but couldn't complete the full analysis
    
    Args:
        agent_type: Type of agent
        partial_data: Any partial results we managed to get
    
    Returns:
        A professional error message (ignoring partial data)
    """
    
    # Log that we had partial data but couldn't complete
    timestamp = datetime.now().isoformat()
    logger.warning(f"Partial Success - Time: {timestamp}, Agent: {agent_type}, Had partial data: {bool(partial_data)}")
    
    # Return the same professional message - don't expose partial/broken results
    return ("I apologize for the inconvenience. I am unable to complete your request at this time. "
            "At SportsBrain, we're always working hard to improve user experience. "
            "This interaction has been logged for later analysis.")