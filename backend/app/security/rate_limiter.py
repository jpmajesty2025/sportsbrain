"""Rate limiting and threat monitoring for users"""

from datetime import datetime, timedelta
from collections import defaultdict
import asyncio
from typing import Dict, List, Optional, Tuple
import logging
import json
from enum import Enum

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """Threat level classifications"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RateLimiter:
    """Per-user rate limiting with threat detection"""
    
    # Rate limit configurations
    DEFAULT_LIMITS = {
        "requests_per_minute": 20,
        "requests_per_hour": 200,
        "requests_per_day": 1000,
    }
    
    # Threat scoring weights
    THREAT_WEIGHTS = {
        "prompt_injection": 5,
        "info_extraction": 3,
        "rate_exceeded": 1,
        "repeated_violation": 2,
        "suspicious_pattern": 2,
    }
    
    def __init__(self, redis_client=None):
        """Initialize rate limiter
        
        Args:
            redis_client: Optional Redis client for distributed rate limiting
        """
        self.redis_client = redis_client
        
        # In-memory storage (fallback if Redis not available)
        self.user_requests: Dict[str, List[datetime]] = defaultdict(list)
        self.blocked_users: Dict[str, datetime] = {}
        self.threat_scores: Dict[str, int] = defaultdict(int)
        self.violation_history: Dict[str, List[dict]] = defaultdict(list)
        
        # Lock for thread safety
        self.lock = asyncio.Lock()
    
    async def check_rate_limit(
        self, 
        user_id: str, 
        max_requests: Optional[int] = None,
        window_minutes: int = 1
    ) -> Tuple[bool, Optional[str]]:
        """Check if user exceeds rate limit
        
        Args:
            user_id: User identifier
            max_requests: Maximum requests allowed (uses default if None)
            window_minutes: Time window in minutes
            
        Returns:
            (is_allowed, error_message)
        """
        async with self.lock:
            # Check if user is blocked
            if user_id in self.blocked_users:
                if datetime.now() < self.blocked_users[user_id]:
                    remaining = (self.blocked_users[user_id] - datetime.now()).seconds
                    return False, f"Account temporarily blocked for {remaining} seconds due to suspicious activity"
                else:
                    # Unblock expired blocks
                    del self.blocked_users[user_id]
                    self.threat_scores[user_id] = max(0, self.threat_scores[user_id] - 5)
            
            # Use default limit if not specified
            if max_requests is None:
                if window_minutes == 1:
                    max_requests = self.DEFAULT_LIMITS["requests_per_minute"]
                elif window_minutes == 60:
                    max_requests = self.DEFAULT_LIMITS["requests_per_hour"]
                else:
                    max_requests = self.DEFAULT_LIMITS["requests_per_minute"] * window_minutes
            
            # Clean old requests
            cutoff = datetime.now() - timedelta(minutes=window_minutes)
            self.user_requests[user_id] = [
                req for req in self.user_requests[user_id] 
                if req > cutoff
            ]
            
            # Check rate
            current_requests = len(self.user_requests[user_id])
            if current_requests >= max_requests:
                # Report rate limit violation
                await self.report_threat(user_id, "rate_exceeded", {
                    "requests": current_requests,
                    "limit": max_requests,
                    "window": window_minutes
                })
                return False, f"Rate limit exceeded: {max_requests} requests per {window_minutes} minute(s)"
            
            # Add current request
            self.user_requests[user_id].append(datetime.now())
            
            # Check multiple time windows
            await self._check_multi_window_limits(user_id)
            
            return True, None
    
    async def _check_multi_window_limits(self, user_id: str):
        """Check rate limits across multiple time windows
        
        Args:
            user_id: User identifier
        """
        now = datetime.now()
        
        # Check hourly limit
        hour_cutoff = now - timedelta(hours=1)
        hour_requests = sum(1 for req in self.user_requests[user_id] if req > hour_cutoff)
        if hour_requests > self.DEFAULT_LIMITS["requests_per_hour"]:
            await self.report_threat(user_id, "rate_exceeded", {"window": "hourly"})
        
        # Check daily limit
        day_cutoff = now - timedelta(days=1)
        day_requests = sum(1 for req in self.user_requests[user_id] if req > day_cutoff)
        if day_requests > self.DEFAULT_LIMITS["requests_per_day"]:
            await self.report_threat(user_id, "rate_exceeded", {"window": "daily"})
    
    async def report_threat(self, user_id: str, threat_type: str, details: dict = None):
        """Track security threats per user
        
        Args:
            user_id: User identifier
            threat_type: Type of threat detected
            details: Additional threat details
        """
        async with self.lock:
            # Calculate threat weight
            weight = self.THREAT_WEIGHTS.get(threat_type, 1)
            
            # Check for repeated violations
            recent_violations = [
                v for v in self.violation_history[user_id]
                if datetime.fromisoformat(v["timestamp"]) > datetime.now() - timedelta(hours=1)
            ]
            if len(recent_violations) > 3:
                weight *= self.THREAT_WEIGHTS["repeated_violation"]
            
            # Update threat score
            self.threat_scores[user_id] += weight
            
            # Log violation
            violation = {
                "timestamp": datetime.now().isoformat(),
                "type": threat_type,
                "details": details or {},
                "score": weight
            }
            self.violation_history[user_id].append(violation)
            
            # Keep only recent history (last 24 hours)
            day_ago = datetime.now() - timedelta(days=1)
            self.violation_history[user_id] = [
                v for v in self.violation_history[user_id]
                if datetime.fromisoformat(v["timestamp"]) > day_ago
            ]
            
            logger.warning(f"Threat reported for user {user_id}: {threat_type} (score: {self.threat_scores[user_id]})")
            
            # Auto-block based on threat score
            threat_level = self._calculate_threat_level(self.threat_scores[user_id])
            
            if threat_level == ThreatLevel.HIGH:
                # Block for 1 hour
                self.blocked_users[user_id] = datetime.now() + timedelta(hours=1)
                logger.warning(f"User {user_id} blocked for 1 hour due to high threat score")
            elif threat_level == ThreatLevel.CRITICAL:
                # Block for 24 hours
                self.blocked_users[user_id] = datetime.now() + timedelta(hours=24)
                logger.critical(f"User {user_id} blocked for 24 hours due to critical threat score")
                # Could trigger additional alerts here
    
    def _calculate_threat_level(self, score: int) -> ThreatLevel:
        """Calculate threat level from score
        
        Args:
            score: Threat score
            
        Returns:
            Threat level classification
        """
        if score == 0:
            return ThreatLevel.NONE
        elif score < 5:
            return ThreatLevel.LOW
        elif score < 10:
            return ThreatLevel.MEDIUM
        elif score < 20:
            return ThreatLevel.HIGH
        else:
            return ThreatLevel.CRITICAL
    
    async def get_user_status(self, user_id: str) -> dict:
        """Get current status for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with user status information
        """
        async with self.lock:
            is_blocked = user_id in self.blocked_users and datetime.now() < self.blocked_users[user_id]
            
            return {
                "user_id": user_id,
                "is_blocked": is_blocked,
                "block_expires": self.blocked_users.get(user_id).isoformat() if is_blocked else None,
                "threat_score": self.threat_scores.get(user_id, 0),
                "threat_level": self._calculate_threat_level(self.threat_scores.get(user_id, 0)).value,
                "recent_requests": len([
                    req for req in self.user_requests.get(user_id, [])
                    if req > datetime.now() - timedelta(minutes=1)
                ]),
                "violations": len(self.violation_history.get(user_id, []))
            }
    
    async def reset_user(self, user_id: str):
        """Reset user's rate limit and threat status
        
        Args:
            user_id: User identifier
        """
        async with self.lock:
            self.user_requests.pop(user_id, None)
            self.blocked_users.pop(user_id, None)
            self.threat_scores.pop(user_id, None)
            self.violation_history.pop(user_id, None)
            logger.info(f"Reset rate limit and threat status for user {user_id}")
    
    async def cleanup_old_data(self):
        """Clean up old data to prevent memory bloat"""
        async with self.lock:
            cutoff = datetime.now() - timedelta(hours=24)
            
            # Clean old requests
            for user_id in list(self.user_requests.keys()):
                self.user_requests[user_id] = [
                    req for req in self.user_requests[user_id]
                    if req > cutoff
                ]
                if not self.user_requests[user_id]:
                    del self.user_requests[user_id]
            
            # Clean expired blocks
            for user_id in list(self.blocked_users.keys()):
                if self.blocked_users[user_id] < datetime.now():
                    del self.blocked_users[user_id]
            
            logger.debug("Cleaned up old rate limit data")