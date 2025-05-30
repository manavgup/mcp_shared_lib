"""
Shared Error Handler - Provides centralized error handling and retry mechanisms
"""
import logging
import asyncio
from functools import wraps
from typing import Callable, Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class MCPError(Exception):
    """Base exception for MCP operations"""
    pass

class ToolExecutionError(MCPError):
    """Error during tool execution"""
    pass

class ConnectionError(MCPError):
    """MCP connection error"""
    pass

class A2AError(MCPError):
    """Error during A2A communication"""
    pass

class ErrorHandler:
    """Provides centralized error handling and retry mechanisms"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Error Handler with configuration"""
        self.config = config or {}
        self.retry_config = self.config.get("retry", {
            "max_attempts": 3,
            "backoff_factor": 2,
            "max_delay": 30
        })
        logger.info(f"Error handler initialized with retry config: {self.retry_config}")
    
    def with_retry(self, exceptions=(Exception,)):
        """Decorator for automatic retry with exponential backoff"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                last_exception = None
                delay = 1
                
                for attempt in range(self.retry_config["max_attempts"]):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        if attempt < self.retry_config["max_attempts"] - 1:
                            self.logger.warning(
                                f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s"
                            )
                            await asyncio.sleep(delay)
                            delay = min(
                                delay * self.retry_config["backoff_factor"],
                                self.retry_config["max_delay"]
                            )
                        else:
                            self.logger.error(f"All attempts failed: {e}")
                
                raise last_exception
            return wrapper
        return decorator
    
    async def handle_tool_error(self, tool_name: str, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Centralized tool error handling"""
        error_context = {
            "tool": tool_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        }
        
        self.logger.error(f"Tool error: {error_context}")
        
        # TODO: Send to monitoring system
        # await self.send_to_monitoring(error_context)
        
        # Determine if error is recoverable
        if isinstance(error, ConnectionError):
            raise MCPError("Connection lost. Please retry.")
        elif isinstance(error, A2AError):
            raise MCPError(f"A2A communication error: {error}")
        else:
            raise ToolExecutionError(f"Tool {tool_name} failed: {error}")
    
    async def handle_workflow_error(self, workflow_id: str, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Centralized workflow error handling"""
        error_context = {
            "workflow_id": workflow_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        }
        
        self.logger.error(f"Workflow error: {error_context}")
        
        # TODO: Send to monitoring system
        # await self.send_to_monitoring(error_context)
        
        # Depending on the error type, you might update workflow state,
        # notify users, or trigger compensating actions.
        raise MCPError(f"Workflow {workflow_id} failed: {error}")
