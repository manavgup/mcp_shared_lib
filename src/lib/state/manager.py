import json
import logging
from typing import Dict, Any, Optional
import redis

class StateManager:
    """Manages workflow execution state using Redis"""

    def __init__(self, redis_url: str = "redis://localhost:6379", key_prefix: str = "workflow"):
        """Initialize the State Manager with Redis connection and key prefix"""
        self.redis = redis.from_url(redis_url)
        self.ttl = 3600  # 1 hour default TTL
        self.key_prefix = key_prefix
        self.logger = logging.getLogger(__name__)

    async def save_workflow_state(self, workflow_id: str, state: Dict[str, Any]):
        """Save workflow execution state"""
        key = f"{self.key_prefix}:{workflow_id}"
        try:
            self.redis.setex(key, self.ttl, json.dumps(state))
            self.logger.debug(f"Saved state for workflow: {workflow_id}")
        except Exception as e:
            self.logger.error(f"Error saving state for workflow {workflow_id}: {e}")

    async def get_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve workflow execution state"""
        key = f"{self.key_prefix}:{workflow_id}"
        try:
            data = self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            self.logger.error(f"Error getting state for workflow {workflow_id}: {e}")
            return None
