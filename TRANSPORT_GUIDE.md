# MCP Transport System Guide

The MCP shared library provides a comprehensive transport system that allows your MCP servers to communicate using multiple protocols.

## Available Transports

### 1. Stdio Transport (Default)
- **Use Case**: Development, CLI tools, process-to-process communication
- **Protocol**: Standard input/output streams
- **Configuration**: No additional config required

```bash
# Default - no environment variables needed
poetry run local-git-analyzer

# Or explicitly
export MCP_TRANSPORT=stdio
poetry run local-git-analyzer
```

### 2. HTTP Transport
- **Use Case**: Web applications, REST APIs, production deployments
- **Protocol**: HTTP with streamable requests
- **Configuration**: Host and port settings

```bash
# Environment variables
export MCP_TRANSPORT=http
export MCP_HTTP_HOST=0.0.0.0
export MCP_HTTP_PORT=9040
poetry run local-git-analyzer

# Or CLI arguments
poetry run local-git-analyzer --transport http --port 9040
```

### 3. WebSocket Transport
- **Use Case**: Real-time bidirectional communication, web clients
- **Protocol**: WebSocket with heartbeat support
- **Configuration**: Host, port, and heartbeat interval

```bash
# Environment variables
export MCP_TRANSPORT=websocket
export MCP_WS_HOST=0.0.0.0
export MCP_WS_PORT=9041
export MCP_WS_HEARTBEAT_INTERVAL=30
poetry run local-git-analyzer

# Or CLI arguments
poetry run local-git-analyzer --transport websocket --port 9041
```

### 4. Server-Sent Events (SSE) Transport
- **Use Case**: Streaming responses, real-time updates to web clients
- **Protocol**: HTTP with Server-Sent Events
- **Configuration**: Uses HTTP config or defaults

```bash
# Environment variables
export MCP_TRANSPORT=sse
export MCP_HTTP_PORT=9042  # Optional, defaults to 8003
poetry run local-git-analyzer

# Or CLI arguments
poetry run local-git-analyzer --transport sse --port 9042
```

## Configuration Methods

### 1. Environment Variables
```bash
# Transport type
export MCP_TRANSPORT=http

# HTTP settings
export MCP_HTTP_HOST=0.0.0.0
export MCP_HTTP_PORT=9040
export MCP_HTTP_CORS_ORIGINS="*"

# WebSocket settings
export MCP_WS_HOST=0.0.0.0
export MCP_WS_PORT=9041
export MCP_WS_HEARTBEAT_INTERVAL=30

# Logging settings
export MCP_LOG_LEVEL=INFO
export MCP_LOG_TRANSPORT_DETAILS=true
```

### 2. YAML Configuration File
```yaml
# config.yaml
transport:
  type: http
  http:
    host: 0.0.0.0
    port: 9040
    cors_origins: ["*"]
  websocket:
    host: 0.0.0.0
    port: 9041
    heartbeat_interval: 30
  logging:
    level: INFO
    transport_details: true
    request_logging: true
    error_details: true
```

```bash
poetry run local-git-analyzer --config config.yaml
```

### 3. CLI Arguments
```bash
# Basic usage
poetry run local-git-analyzer --transport http --port 9040

# With additional options
poetry run local-git-analyzer \
  --transport http \
  --host 127.0.0.1 \
  --port 9040 \
  --log-level DEBUG
```

## Connection Information

Each transport provides connection information:

### Stdio
```json
{"transport": "stdio"}
```

### HTTP
```json
{
  "url": "http://0.0.0.0:9040",
  "cors_enabled": true,
  "cors_origins": ["*"]
}
```

### WebSocket
```json
{
  "url": "ws://0.0.0.0:9041",
  "heartbeat_interval": 30,
  "protocol": "websocket"
}
```

### SSE
```json
{
  "protocol": "sse",
  "url": "http://0.0.0.0:8003/sse",
  "health_url": "http://0.0.0.0:8003/healthz",
  "note": "SSE endpoint available at /sse"
}
```

## Health Checks

HTTP-based transports (HTTP, WebSocket, SSE) support health check endpoints:

```bash
# Check server health
curl http://localhost:9040/health

# For SSE transport
curl http://localhost:8003/healthz
```

## Error Handling

The transport system includes comprehensive error handling:

- **Graceful shutdown** on Ctrl+C
- **Connection reset handling** for network transports
- **Detailed error logging** (configurable)
- **Transport-specific error recovery**

## Usage Examples

### Development (Stdio)
```bash
# Simple development setup
poetry run local-git-analyzer
```

### Production HTTP Server
```bash
# Production HTTP server
export MCP_TRANSPORT=http
export MCP_HTTP_HOST=0.0.0.0
export MCP_HTTP_PORT=8080
export MCP_LOG_LEVEL=INFO
poetry run local-git-analyzer
```

### Real-time WebSocket
```bash
# WebSocket for real-time communication
export MCP_TRANSPORT=websocket
export MCP_WS_PORT=9041
export MCP_WS_HEARTBEAT_INTERVAL=30
poetry run local-git-analyzer
```

### Streaming SSE
```bash
# Server-Sent Events for streaming
export MCP_TRANSPORT=sse
export MCP_HTTP_PORT=9042
poetry run local-git-analyzer
```

## Integration with FastMCP

The transport system is fully integrated with FastMCP and supports all FastMCP features:

- **Tool registration**
- **Resource handling**
- **Lifecycle management**
- **Error handling**
- **Logging integration**

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using the port
   lsof -i :9040

   # Use a different port
   export MCP_HTTP_PORT=9041
   ```

2. **Permission denied**
   ```bash
   # Use a port > 1024 for non-root users
   export MCP_HTTP_PORT=8080
   ```

3. **Transport not found**
   ```bash
   # Check available transports
   poetry run local-git-analyzer --help
   ```

### Debug Mode
```bash
# Enable debug logging
export MCP_LOG_LEVEL=DEBUG
export MCP_LOG_TRANSPORT_DETAILS=true
poetry run local-git-analyzer --transport http --port 9040
```

## Extending the Transport System

To add a new transport:

1. Create a new transport class inheriting from `BaseTransport`
2. Implement required methods: `run()`, `stop()`, `is_running()`, `get_connection_info()`
3. Add configuration support in `TransportConfig`
4. Register in the transport factory

See existing transport implementations for examples.
