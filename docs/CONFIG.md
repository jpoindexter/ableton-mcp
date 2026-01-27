# AbletonMCP Configuration Guide

This document describes all configuration options for AbletonMCP.

## Environment Variables

### REST API Server

| Variable | Default | Description |
|----------|---------|-------------|
| `REST_API_HOST` | `127.0.0.1` | Host to bind the REST API server. Use `0.0.0.0` for external access (not recommended). |
| `REST_API_PORT` | `8000` | Port for the REST API server |
| `REST_API_KEY` | (none) | API key for authentication. When set, all requests must include `X-API-Key` header. |
| `CORS_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | Comma-separated list of allowed CORS origins |
| `RATE_LIMIT_ENABLED` | `true` | Enable/disable rate limiting |
| `RATE_LIMIT_REQUESTS` | `100` | Maximum requests per time window |
| `RATE_LIMIT_WINDOW` | `60` | Time window in seconds |

### Ableton Connection

| Variable | Default | Description |
|----------|---------|-------------|
| `ABLETON_HOST` | `localhost` | Hostname of the Ableton Remote Script |
| `ABLETON_PORT` | `9877` | Port for socket communication |
| `ABLETON_MAX_RETRIES` | `2` | Number of connection retry attempts |
| `ABLETON_CONNECT_TIMEOUT` | `5.0` | Connection timeout in seconds |
| `ABLETON_RECV_TIMEOUT` | `15.0` | Receive timeout in seconds |
| `ABLETON_MAX_BUFFER` | `1048576` | Maximum buffer size (1MB) |

### Remote Script (Ableton Side)

| Variable | Default | Description |
|----------|---------|-------------|
| `ABLETON_MCP_PORT` | `9877` | Port for socket server |
| `ABLETON_MCP_HOST` | `localhost` | Host to bind socket server |
| `ABLETON_MCP_CLIENT_TIMEOUT` | `300.0` | Client connection timeout (5 min) |
| `ABLETON_MCP_MAX_CLIENTS` | `10` | Maximum concurrent clients |
| `ABLETON_MCP_MAX_BUFFER` | `1048576` | Maximum receive buffer size |
| `ABLETON_MCP_COMMAND_TIMEOUT` | `30.0` | Command execution timeout |
| `ABLETON_MCP_MAX_QUEUE_SIZE` | `100` | Maximum response queue size |

## Security Best Practices

### Production Deployment

1. **Always use API key authentication:**
   ```bash
   export REST_API_KEY="$(openssl rand -hex 32)"
   ```

2. **Bind to localhost only:**
   ```bash
   export REST_API_HOST="127.0.0.1"
   ```

3. **Enable rate limiting:**
   ```bash
   export RATE_LIMIT_ENABLED="true"
   export RATE_LIMIT_REQUESTS="60"
   ```

4. **Restrict CORS origins:**
   ```bash
   export CORS_ORIGINS="https://your-app.com"
   ```

### Development

For local development, you can use more permissive settings:

```bash
export REST_API_HOST="127.0.0.1"
export REST_API_KEY=""  # Disable auth for dev
export RATE_LIMIT_ENABLED="false"
```

## Example Configurations

### Minimal (Development)

```bash
# .env.development
REST_API_HOST=127.0.0.1
REST_API_PORT=8000
ABLETON_HOST=localhost
ABLETON_PORT=9877
```

### Production

```bash
# .env.production
REST_API_HOST=127.0.0.1
REST_API_PORT=8000
REST_API_KEY=your-secret-key-here
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW=60
CORS_ORIGINS=https://your-app.com
ABLETON_HOST=localhost
ABLETON_PORT=9877
ABLETON_MAX_RETRIES=3
ABLETON_CONNECT_TIMEOUT=10.0
```

### Remote Ableton

For connecting to Ableton on a different machine:

```bash
# REST API Server (Client Machine)
ABLETON_HOST=192.168.1.100
ABLETON_PORT=9877

# Remote Script (Ableton Machine)
ABLETON_MCP_HOST=0.0.0.0  # Accept external connections
ABLETON_MCP_PORT=9877
```

**Warning:** Only expose the Remote Script to trusted networks.

## Loading Configuration

### Using dotenv

```python
from dotenv import load_dotenv
load_dotenv('.env')
```

### Using shell exports

```bash
source .env
python -m uvicorn rest_api_server:app
```

### Docker

```dockerfile
ENV REST_API_HOST=0.0.0.0
ENV REST_API_PORT=8000
ENV REST_API_KEY=your-key
```
