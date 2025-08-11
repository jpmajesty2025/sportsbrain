"""Output filtering to prevent sensitive information leakage"""

import re
from typing import Tuple, List
import logging

logger = logging.getLogger(__name__)

class OutputFilter:
    """Filter agent outputs for sensitive information"""
    
    # Patterns that should never appear in output
    FORBIDDEN_PATTERNS = [
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'email'),  # Email
        (r'\b\d{3}-\d{2}-\d{4}\b', 'ssn'),  # SSN
        (r'\b\d{16}\b', 'credit_card'),  # Credit card
        (r'\b\d{13,19}\b', 'credit_card'),  # Credit card variations
        (r'api[_-]?key.*?["\']([^"\']+)["\']', 'api_key'),  # API keys
        (r'password.*?["\']([^"\']+)["\']', 'password'),  # Passwords  
        (r'token.*?["\']([^"\']+)["\']', 'token'),  # Tokens
        (r'secret.*?["\']([^"\']+)["\']', 'secret'),  # Secrets
        (r'bearer\s+[A-Za-z0-9\-._~+/]+=*', 'bearer_token'),  # Bearer tokens
        (r'[A-Za-z0-9]{32,}', 'potential_key'),  # Long random strings (potential keys)
        (r'\b(?:\d{1,3}\.){3}\d{1,3}\b', 'ip_address'),  # IP addresses
        (r'postgresql://[^\\s]+', 'database_url'),  # Database URLs
        (r'mongodb://[^\\s]+', 'database_url'),
        (r'redis://[^\\s]+', 'database_url'),
        (r'mysql://[^\\s]+', 'database_url'),
    ]
    
    # Phrases that indicate prompt leakage
    PROMPT_LEAKAGE_PHRASES = [
        "my instructions",
        "i was told",
        "my prompt", 
        "system message",
        "my rules",
        "i am programmed",
        "my configuration",
        "here are my instructions",
        "i should",
        "i must",
        "never violate",
        "critical security rules",
        "system boundary",
        "agent specific instructions",
    ]
    
    # Technical terms that shouldn't be exposed
    TECHNICAL_TERMS = [
        "sqlalchemy",
        "fastapi",
        "postgresql", 
        "redis",
        "milvus",
        "neo4j",
        "jwt",
        "bcrypt",
        "langchain",
        "openai",
        "embedding",
        "vector database",
        "backend/",
        "frontend/",
        "localhost:",
        "127.0.0.1",
        "0.0.0.0",
        ".env",
        "docker",
        "kubernetes",
    ]
    
    @classmethod
    def filter_output(cls, response: str) -> Tuple[str, bool, List[str]]:
        """
        Filter response for sensitive information
        
        Args:
            response: Raw agent response
            
        Returns:
            (filtered_response, is_safe, detected_leaks)
        """
        if not response:
            return "", True, []
            
        detected_leaks = []
        filtered = response
        
        # Check for forbidden patterns
        for pattern, leak_type in cls.FORBIDDEN_PATTERNS:
            matches = re.findall(pattern, filtered, re.IGNORECASE)
            if matches:
                detected_leaks.append(f"{leak_type}: {len(matches)} instance(s)")
                filtered = re.sub(pattern, f"[REDACTED_{leak_type.upper()}]", filtered, flags=re.IGNORECASE)
                logger.warning(f"Filtered {leak_type} from output: {matches[:3]}...")
        
        # Check for prompt leakage
        response_lower = filtered.lower()
        for phrase in cls.PROMPT_LEAKAGE_PHRASES:
            if phrase in response_lower:
                detected_leaks.append(f"Prompt leakage: '{phrase}'")
                logger.critical(f"Detected prompt leakage attempt: '{phrase}'")
                # Replace entire response if prompt leakage detected
                return "I can only provide fantasy basketball analysis and recommendations.", False, detected_leaks
        
        # Check for technical terms
        for term in cls.TECHNICAL_TERMS:
            if term.lower() in response_lower:
                detected_leaks.append(f"Technical term: '{term}'")
                # Replace the technical term with generic description
                filtered = re.sub(
                    re.escape(term),
                    "[TECHNICAL_DETAIL]",
                    filtered,
                    flags=re.IGNORECASE
                )
        
        # Additional safety checks
        filtered = cls._apply_additional_filters(filtered)
        
        is_safe = len(detected_leaks) == 0
        
        if not is_safe:
            logger.warning(f"Output filtering detected {len(detected_leaks)} potential leaks")
        
        return filtered, is_safe, detected_leaks
    
    @staticmethod
    def _apply_additional_filters(text: str) -> str:
        """Apply additional safety filters
        
        Args:
            text: Text to filter
            
        Returns:
            Filtered text
        """
        # Remove file paths
        text = re.sub(r'[/\\](?:home|usr|var|etc|mnt|opt)[/\\][^\s]+', '[PATH]', text)
        text = re.sub(r'C:\\[^\\s]+', '[PATH]', text)
        
        # Remove potential environment variables
        text = re.sub(r'\$[A-Z_]+', '[ENV_VAR]', text)
        text = re.sub(r'%[A-Z_]+%', '[ENV_VAR]', text)
        
        # Remove potential URLs with credentials
        text = re.sub(r'https?://[^:]+:[^@]+@[^\s]+', '[REDACTED_URL]', text)
        
        # Remove potential docker/k8s references
        text = re.sub(r'[a-z0-9]+\.dkr\.ecr\.[^\\s]+', '[REGISTRY]', text)
        text = re.sub(r'[a-z0-9]+\.azurecr\.io', '[REGISTRY]', text)
        
        return text
    
    @staticmethod
    def validate_json_response(response_dict: dict) -> dict:
        """Validate and filter JSON responses
        
        Args:
            response_dict: Dictionary response from agent
            
        Returns:
            Filtered dictionary
        """
        # Remove sensitive keys
        sensitive_keys = [
            'password', 'token', 'secret', 'key', 'credential',
            'api_key', 'auth', 'authorization', 'cookie', 'session'
        ]
        
        filtered_dict = {}
        for key, value in response_dict.items():
            # Check if key contains sensitive terms
            if any(term in key.lower() for term in sensitive_keys):
                filtered_dict[key] = "[REDACTED]"
            elif isinstance(value, str):
                # Filter string values
                filtered_value, _, _ = OutputFilter.filter_output(value)
                filtered_dict[key] = filtered_value
            elif isinstance(value, dict):
                # Recursively filter nested dictionaries
                filtered_dict[key] = OutputFilter.validate_json_response(value)
            elif isinstance(value, list):
                # Filter list items
                filtered_dict[key] = [
                    OutputFilter.validate_json_response(item) if isinstance(item, dict)
                    else OutputFilter.filter_output(item)[0] if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                filtered_dict[key] = value
                
        return filtered_dict