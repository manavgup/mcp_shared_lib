"""Transport configuration models and utilities."""

import os
import yaml
from pydantic import BaseModel, Field
from typing import Optional, List


class HTTPConfig(BaseModel):
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    cors_origins: Optional[List[str]] = Field(default_factory=lambda: ["*"])
    enable_health_check: bool = Field(default=True)
    health_check_path: str = Field(default="/health")


class WebSocketConfig(BaseModel):
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8001)
    heartbeat_interval: int = Field(default=30)


class SSEConfig(BaseModel):
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8003)
    cors_origins: Optional[List[str]] = Field(default_factory=lambda: ["*"])
    enable_health_check: bool = Field(default=True)
    health_check_path: str = Field(default="/healthz")


class LoggingConfig(BaseModel):
    level: str = Field(default="INFO")
    transport_details: bool = Field(default=True)
    request_logging: bool = Field(default=True)
    error_details: bool = Field(default=True)

class TransportConfig(BaseModel):
    type: str = Field(default="stdio")  # stdio, http, websocket, sse
    http: Optional[HTTPConfig] = None
    websocket: Optional[WebSocketConfig] = None
    sse: Optional[SSEConfig] = None
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    @classmethod
    def from_env(cls):
        ttype = os.environ.get("MCP_TRANSPORT", "stdio")
        http = None
        websocket = None
        sse = None

        if ttype == "http":
            http = HTTPConfig(
                host=os.environ.get("MCP_HTTP_HOST", "0.0.0.0"),
                port=int(os.environ.get("MCP_HTTP_PORT", 8000)),
                cors_origins=os.environ.get("MCP_HTTP_CORS_ORIGINS", "*").split(",")
            )
        if ttype == "websocket":
            websocket = WebSocketConfig(
                host=os.environ.get("MCP_WS_HOST", "0.0.0.0"),
                port=int(os.environ.get("MCP_WS_PORT", 8001)),
                heartbeat_interval=int(os.environ.get("MCP_WS_HEARTBEAT_INTERVAL", 30))
            )
        if ttype == "sse":
            sse = SSEConfig(
                host=os.environ.get("MCP_SSE_HOST", "0.0.0.0"),
                port=int(os.environ.get("MCP_SSE_PORT", 8003)),
                cors_origins=os.environ.get("MCP_SSE_CORS_ORIGINS", "*").split(",")
            )
        logging = LoggingConfig(
            level=os.environ.get("MCP_LOG_LEVEL", "INFO"),
            transport_details=os.environ.get("MCP_LOG_TRANSPORT_DETAILS", "true").lower() == "true"
        )
        return cls(type=ttype, http=http, websocket=websocket, sse=sse, logging=logging)

    @classmethod
    def from_file(cls, path):
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        ttype = data.get("transport", {}).get("type", "stdio")
        http = None
        websocket = None
        sse = None
        logging = None
        if "http" in data.get("transport", {}):
            http = HTTPConfig(**data["transport"]["http"])
        if "websocket" in data.get("transport", {}):
            websocket = WebSocketConfig(**data["transport"]["websocket"])
        if "sse" in data.get("transport", {}):
            sse = SSEConfig(**data["transport"]["sse"])
        if "logging" in data.get("transport", {}):
            logging = LoggingConfig(**data["transport"]["logging"])
        return cls(type=ttype, http=http, websocket=websocket, sse=sse, logging=logging or LoggingConfig())
