"""
Shared State Manager - Provides a common state management interface
"""
import logging
import json
from typing import Optional, Dict, Any
import redis

logger = logging.getLogger(__name__)

class StateManager:
    """Provides a common state management interface using Redis"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """Initialize the Shared State Manager with Redis connection"""
        try:
            self.redis = redis.from_url(redis_url)
            # Test connection
            self.redis.ping()
            logger.info(f"Connected to Redis at {redis_url}")
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Failed to connect to Redis at {redis_url}: {e}")
            self.redis = None # Set to None if connection fails
        
        self.ttl = 3600  # 1 hour default TTL
    
    async def save_state(self, key: str, state: Dict[str, Any], namespace: Optional[str] = None):
        """Save state with optional namespace"""
        if not self.redis:
            logger.error("Redis connection not available. Cannot save state.")
            return
            
        full_key = f"{namespace}:{key}" if namespace else key
        try:
            self.redis.setex(full_key, self.ttl, json.dumps(state))
            logger.debug(f"Saved state for key: {full_key}")
        except Exception as e:
            logger.error(f"Error saving state for key {full_key}: {e}")
    
    async def get_state(self, key: str, namespace: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieve state with optional namespace"""
        if not self.redis:
            logger.error("Redis connection not available. Cannot get state.")
            return None
            
        full_key = f"{namespace}:{key}" if namespace else key
        try:
            data = self.redis.get(full_key)
            if data:
                logger.debug(f"Retrieved state for key: {full_key}")
                return json.loads(data)
            else:
                logger.debug(f"No state found for key: {full_key}")
                return None
        except Exception as e:
            logger.error(f"Error getting state for key {full_key}: {e}")
            return None
    
    async def delete_state(self, key: str, namespace: Optional[str] = None):
        """Delete state with optional namespace"""
        if not self.redis:
            logger.error("Redis connection not available. Cannot delete state.")
            return
            
        full_key = f"{namespace}:{key}" if namespace else key
        try:
            self.redis.delete(full_key)
            logger.debug(f"Deleted state for key: {full_key}")
        except Exception as e:
            logger.error(f"Error deleting state for key {full_key}: {e}")
