# AbletonMCP Configuration Guide

This document describes all configuration options for AbletonMCP.

## Environment Variables

### REST API Server

| Variable | Default | Description |
|----------|---------|-------------|
| `REST_API_HOST` | `127.0.0.1` | Host to bind the REST API server. Use `0.0.0.0` for external access (not recommended for security). |
| `REST_API_PORT` | `8000` | Port for the REST API server |
| `REST_API_KEY` | (none) | API key for authentication. When set, all requests must include `X-API-Key` header. |
| `CORS_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | Comma-separated list of allowed CORS origins |
| `RATE_LIMIT_ENABLED` | `true` | Enable/disable rate limiting |
| `RATE_LIMIT_REQUESTS` | `100` | Maximum requests per time window |
| `RATE_LIMIT_WINDOW` | `60` | Time window in seconds |
| `TRUST_PROXY_HEADERS` | `false` | Trust X-Forwarded-For headers for client IP. **Only enable when behind a trusted reverse proxy!** |
| `MAX_RATE_LIMIT_CLIENTS` | `10000` | Maximum number of unique client IPs to track for rate limiting (LRU eviction) |

### MCP Server (Claude Desktop)

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_RECV_TIMEOUT` | `15.0` | Socket receive timeout in seconds |
| `MCP_MODIFYING_CMD_TIMEOUT` | `15.0` | Timeout for state-modifying commands (create, delete, set) |
| `MCP_READ_CMD_TIMEOUT` | `10.0` | Timeout for read-only commands (get) |
| `MCP_HEALTH_CHECK_TIMEOUT` | `2.0` | Timeout for connection health checks |
| `MCP_COMMAND_DELAY` | `0.05` | Delay before/after modifying commands (seconds) |
| `MCP_RETRY_DELAY` | `1.0` | Delay between connection retry attempts |
| `MCP_MAX_CONNECT_ATTEMPTS` | `3` | Maximum connection attempts before failing |
| `ABLETON_HOST` | `localhost` | Hostname of the Ableton Remote Script |
| `ABLETON_PORT` | `9877` | Port for socket communication |

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

---

## Parameter Validation Limits

The REST API server enforces the following bounds on all parameters:

| Constant | Value | Description |
|----------|-------|-------------|
| `MAX_TRACK_INDEX` | 999 | Maximum valid track index |
| `MAX_CLIP_INDEX` | 999 | Maximum valid clip slot index |
| `MAX_SCENE_INDEX` | 999 | Maximum valid scene index |
| `MAX_DEVICE_INDEX` | 127 | Maximum valid device index per track |
| `MAX_PARAMETER_INDEX` | 255 | Maximum valid parameter index per device |
| `MAX_SEND_INDEX` | 11 | Maximum valid send index (return tracks A-L) |

### Value Ranges

| Parameter | Range | Description |
|-----------|-------|-------------|
| Tempo | 20-300 BPM | Session tempo |
| Volume | 0.0-1.0 | Track/return/master volume |
| Pan | -1.0 to 1.0 | Panning position |
| Pitch | -48 to +48 | Audio clip pitch shift (semitones) |
| MIDI Pitch | 0-127 | Note pitch |
| Velocity | 0-127 | Note velocity |
| Color | 0-69 | Ableton color palette index |

---

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

5. **Never expose the Remote Script to untrusted networks:**
   - Keep `ABLETON_MCP_HOST` set to `localhost` unless absolutely necessary
   - Use a VPN or SSH tunnel for remote access

### Development

For local development, you can use more permissive settings:

```bash
export REST_API_HOST="127.0.0.1"
export REST_API_KEY=""  # Disable auth for dev
export RATE_LIMIT_ENABLED="false"
```

### Reverse Proxy Configuration

If running behind a reverse proxy (nginx, Traefik, etc.):

1. Enable proxy header trust:
   ```bash
   export TRUST_PROXY_HEADERS="true"
   ```

2. Configure your proxy to set `X-Forwarded-For` header

3. Ensure the proxy strips any client-provided `X-Forwarded-For` headers

**Warning:** Only enable `TRUST_PROXY_HEADERS` when behind a trusted reverse proxy. Enabling this without a proxy allows clients to spoof their IP address, bypassing rate limiting.

---

## Example Configurations

### Minimal (Development)

```bash
# .env.development
REST_API_HOST=127.0.0.1
REST_API_PORT=8000
ABLETON_HOST=localhost
ABLETON_PORT=9877
```

### Production (Single Machine)

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

### Production (Behind Reverse Proxy)

```bash
# .env.production-proxy
REST_API_HOST=127.0.0.1
REST_API_PORT=8000
REST_API_KEY=your-secret-key-here
TRUST_PROXY_HEADERS=true
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW=60
CORS_ORIGINS=https://your-app.com
ABLETON_HOST=localhost
ABLETON_PORT=9877
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

**Warning:** Only expose the Remote Script to trusted networks. Consider using SSH tunneling instead.

### High-Throughput Configuration

For applications making many API calls:

```bash
# .env.high-throughput
REST_API_HOST=127.0.0.1
REST_API_PORT=8000
REST_API_KEY=your-secret-key-here
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=300
RATE_LIMIT_WINDOW=60
ABLETON_HOST=localhost
ABLETON_PORT=9877
ABLETON_MAX_RETRIES=1
ABLETON_CONNECT_TIMEOUT=3.0
ABLETON_RECV_TIMEOUT=10.0
```

---

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

Or export individually:

```bash
export REST_API_HOST="127.0.0.1"
export REST_API_PORT="8000"
export REST_API_KEY="your-secret-key"
python -m uvicorn MCP_Server.rest_api_server:app
```

### Docker

```dockerfile
ENV REST_API_HOST=0.0.0.0
ENV REST_API_PORT=8000
ENV REST_API_KEY=your-key
ENV ABLETON_HOST=host.docker.internal
ENV ABLETON_PORT=9877
```

Docker Compose example:

```yaml
version: '3.8'
services:
  ableton-mcp:
    build: .
    environment:
      - REST_API_HOST=0.0.0.0
      - REST_API_PORT=8000
      - REST_API_KEY=${REST_API_KEY}
      - ABLETON_HOST=host.docker.internal
      - ABLETON_PORT=9877
    ports:
      - "8000:8000"
```

---

## Timeout Tuning

### When to Adjust Timeouts

| Scenario | Recommended Settings |
|----------|---------------------|
| Fast local network | `ABLETON_CONNECT_TIMEOUT=3.0`, `ABLETON_RECV_TIMEOUT=10.0` |
| Slow network/remote | `ABLETON_CONNECT_TIMEOUT=10.0`, `ABLETON_RECV_TIMEOUT=30.0` |
| Complex operations (freeze, browser) | `ABLETON_RECV_TIMEOUT=30.0` |
| Simple queries only | `ABLETON_RECV_TIMEOUT=5.0` |

### Operations That May Require Longer Timeouts

Some operations take longer to complete in Ableton:

- `freeze_track` - Renders all audio, can take 5-30+ seconds
- `flatten_track` - Converts frozen audio, similar to freeze
- `load_instrument_or_effect` - Loading large plugins can take several seconds
- `get_browser_tree` - Scanning the browser hierarchy
- `generate_drum_pattern` / `generate_bassline` - Creating and adding notes

For these operations, ensure `ABLETON_RECV_TIMEOUT` is set to at least 15 seconds (the default).

---

## Rate Limiting Details

### How Rate Limiting Works

- Tracks requests per IP address
- Uses a sliding window approach
- Counts reset after the window period expires
- Returns `429 Too Many Requests` when limit exceeded

### Rate Limit Headers

When rate limiting is enabled, responses include:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1704067200
```

### Exemptions

The following endpoints are exempt from rate limiting:
- `/api/health` - Health check endpoint

---

## Command Whitelist

The REST API server maintains a whitelist of allowed commands for security. Only commands in this list can be executed via the `/api/command` endpoint.

To see the current list of allowed commands:

```bash
curl http://localhost:8000/api/commands
```

The command whitelist cannot be modified via environment variables. To add custom commands, you must modify the `ALLOWED_COMMANDS` set in `rest_api_server.py`.

---

## Troubleshooting

### Connection Issues

**Error: "Could not connect to Ableton"**
- Ensure Ableton Live is running
- Verify the AbletonMCP control surface is enabled in Live's preferences
- Check that `ABLETON_HOST` and `ABLETON_PORT` match the Remote Script settings
- Try increasing `ABLETON_CONNECT_TIMEOUT`

**Error: "Timeout waiting for response"**
- Increase `ABLETON_RECV_TIMEOUT`
- Check if Ableton is responding (CPU overload, dialog boxes, etc.)
- Verify no firewall is blocking the connection

### Authentication Issues

**Error: "API key required"**
- Add `X-API-Key` header to your request
- Ensure `REST_API_KEY` is set on the server

**Error: "Invalid API key"**
- Verify the API key matches exactly (case-sensitive)
- Check for whitespace in the key

### Rate Limiting Issues

**Error: "Rate limit exceeded"**
- Wait for the rate limit window to reset
- Consider increasing `RATE_LIMIT_REQUESTS`
- Implement request throttling in your client

### CORS Issues

**Error: "CORS policy blocked"**
- Add your origin to `CORS_ORIGINS`
- Ensure the origin includes the protocol (http:// or https://)
- Check for trailing slashes in the origin
