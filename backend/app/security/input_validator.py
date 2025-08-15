"""Input validation and sanitization for user queries"""

import re
from typing import Tuple, List
import hashlib
import logging

logger = logging.getLogger(__name__)

class InputValidator:
    """Validates and sanitizes user input to prevent attacks"""
    
    # Patterns that indicate potential attacks
    INJECTION_PATTERNS = [
        r"ignore.*previous.*instructions",
        r"ignore.*all.*rules",
        r"disregard.*instructions",
        r"forget.*you.*told",
        r"system.*prompt",
        r"reveal.*prompt",
        r"show.*instructions",
        r"print.*prompt",
        r"what.*were.*you.*told",
        r"bypass.*safety",
        r"jailbreak",
        r"DAN mode",  # "Do Anything Now" jailbreak
        r"role.*play",
        r"pretend.*you",
        r"act.*as.*if",
        r"you.*are.*now",
        r"switch.*mode",
        r"developer.*mode",
        r"sudo",
        r"admin.*access",
    ]
    
    # Patterns for information extraction attempts
    INFO_EXTRACTION_PATTERNS = [
        r"list.*all.*users",
        r"show.*database",
        r"password",
        r"api.*key",
        r"secret",
        r"token",
        r"credentials",
        r"private.*key",
        r"email.*addresses",
        r"phone.*numbers",
        r"social.*security",
        r"credit.*card",
        r"bank.*account",
        r"personal.*information",
        r"dump.*data",
        r"export.*users",
        r"select.*from",  # SQL injection attempts (lowercase for matching)
        r"drop.*table",
        r"delete.*from",
        r"update.*set",
    ]
    
    # Allowed query patterns (whitelist approach)
    ALLOWED_PATTERNS = [
        r"keeper.*round",
        r"should.*i.*draft",
        r"worth.*draft",  # Added for "Is X worth drafting?"
        r"trade.*for",
        r"punt.*strategy",
        r"sleeper.*picks",
        r"injury.*status",
        r"player.*comparison",
        r"team.*analysis",
        r"sophomore.*breakout",
        r"usage.*rate",
        r"fantasy.*points",
        r"ADP",
        r"average.*draft.*position",
        r"waiver.*wire",
        r"drop.*candidate",
        r"pick.*up",
        r"start.*sit",
        r"matchup",
        r"schedule",
        r"playoff.*outlook",
        r"rest.*of.*season",
        r"dynasty.*value",
        r"rookie",
        r"veteran",
        r"breakout",
        r"breakout.*candidate",  # Added for "Is X a breakout candidate?"
        r"bust",
        r"value.*pick",
    ]
    
    @classmethod
    def validate_input(cls, query: str) -> Tuple[bool, str, List[str]]:
        """
        Validate user input for security threats
        
        Args:
            query: Raw user input
            
        Returns:
            (is_safe, sanitized_query, detected_threats)
        """
        if not query:
            return False, "", ["Empty query"]
            
        query_lower = query.lower()
        detected_threats = []
        
        # Check for injection attempts
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, query_lower):
                threat = f"Prompt injection: {pattern.replace('.*', ' ')}"
                detected_threats.append(threat)
                logger.warning(f"Detected {threat} in query: {query[:50]}...")
        
        # Check for information extraction
        for pattern in cls.INFO_EXTRACTION_PATTERNS:
            if re.search(pattern, query_lower):
                threat = f"Info extraction: {pattern.replace('.*', ' ')}"
                detected_threats.append(threat)
                logger.warning(f"Detected {threat} in query: {query[:50]}...")
        
        # Check if query matches allowed patterns
        is_allowed = any(
            re.search(pattern, query_lower) 
            for pattern in cls.ALLOWED_PATTERNS
        )
        
        # Sanitize query
        sanitized = cls._sanitize_query(query)
        
        # Determine if safe
        # Query is safe if no threats detected OR if it matches allowed patterns
        is_safe = len(detected_threats) == 0 or (is_allowed and len(detected_threats) <= 1)
        
        # Log suspicious activity
        if detected_threats and not is_safe:
            logger.warning(f"Blocked query with threats: {detected_threats}")
        
        return is_safe, sanitized, detected_threats
    
    @staticmethod
    def _sanitize_query(query: str) -> str:
        """Remove potentially dangerous content"""
        # Remove special characters that could be used for injection
        sanitized = re.sub(r'[<>{}\\`]', '', query)
        
        # Remove SQL-like syntax
        sanitized = re.sub(r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|EXEC|UNION)\b', '', sanitized, flags=re.IGNORECASE)
        
        # Remove script tags and similar
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        # Limit query length
        max_length = 500
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized.strip()
    
    @staticmethod
    def hash_query(query: str) -> str:
        """Generate hash of query for caching/tracking"""
        return hashlib.sha256(query.encode()).hexdigest()[:16]