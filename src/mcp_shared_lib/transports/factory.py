from .config import TransportConfig
from .http import HttpTransport
from .sse import SSETransport
from .stdio import StdioTransport
from .websocket import WebSocketTransport


def get_transport(config: TransportConfig):
    ttype = config.type.lower()
    if ttype == "stdio":
        return StdioTransport(config)
    elif ttype == "http":
        return HttpTransport(config)
    elif ttype == "websocket":
        return WebSocketTransport(config)
    elif ttype == "sse":
        return SSETransport(config)
    else:
        raise ValueError(f"Unknown transport type: {ttype}")
