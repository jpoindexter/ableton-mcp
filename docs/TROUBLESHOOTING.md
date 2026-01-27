# AbletonMCP Troubleshooting Guide

Common issues and solutions for AbletonMCP.

## Connection Issues

### "Could not connect to Ableton"

**Symptoms:**
- REST API returns 503 error
- MCP tools return connection error

**Solutions:**

1. **Verify Ableton is running** with the Remote Script enabled:
   - Open Ableton Live
   - Go to Preferences > Link, Tempo & MIDI
   - Under Control Surface, select "AbletonMCP"

2. **Check the port is not in use:**
   ```bash
   lsof -i :9877
   ```
   If another process is using the port, either stop it or change `ABLETON_MCP_PORT`.

3. **Verify firewall settings:**
   - macOS: System Preferences > Security & Privacy > Firewall
   - Allow incoming connections for Ableton Live

4. **Check Remote Script logs:**
   - In Ableton, open Window > Show Log
   - Look for "AbletonMCP" messages

### Connection drops frequently

**Solutions:**

1. **Increase timeouts:**
   ```bash
   export ABLETON_MCP_CLIENT_TIMEOUT=600.0
   export ABLETON_CONNECT_TIMEOUT=10.0
   ```

2. **Check for resource conflicts:**
   - Close other applications using MIDI/audio
   - Reduce CPU load in Ableton

## Authentication Issues

### "API key required"

**Solution:** Set the X-API-Key header:
```bash
curl -H "X-API-Key: your-key" http://localhost:8000/api/session
```

Or disable authentication:
```bash
export REST_API_KEY=""
```

### "Invalid API key"

**Solution:** Verify the key matches:
```bash
echo $REST_API_KEY  # Check what's set
```

## Rate Limiting

### "Rate limit exceeded"

**Symptoms:**
- HTTP 429 error
- "Maximum 100 requests per 60 seconds"

**Solutions:**

1. **Wait for rate limit window to reset**

2. **Increase rate limit:**
   ```bash
   export RATE_LIMIT_REQUESTS=200
   ```

3. **Disable rate limiting (development only):**
   ```bash
   export RATE_LIMIT_ENABLED=false
   ```

## Validation Errors

### "Tempo must be between 20 and 300 BPM"

**Solution:** Use valid tempo values (20-300).

### "Volume must be between 0.0 and 1.0"

**Solution:** Volume is normalized (0=silent, 1=max).

### "Pitch must be between 0 and 127"

**Solution:** Use MIDI note numbers (0-127). Middle C = 60.

### "Track index out of range"

**Solutions:**
1. Get session info first to find valid track indices
2. Indices are 0-based

## Remote Script Issues

### Script not loading

**Symptoms:**
- "AbletonMCP" not appearing in Control Surface list

**Solutions:**

1. **Verify installation path:**
   - macOS: `/Applications/Ableton Live.app/Contents/App-Resources/MIDI Remote Scripts/AbletonMCP`
   - Windows: `C:\ProgramData\Ableton\Live x.x\Resources\MIDI Remote Scripts\AbletonMCP`

2. **Check file structure:**
   ```
   AbletonMCP/
   ├── __init__.py
   └── (other files)
   ```

3. **Restart Ableton** after installation

### "Buffer overflow" error

**Symptoms:**
- Commands fail with buffer error
- Large responses truncated

**Solutions:**

1. **Increase buffer size:**
   ```bash
   export ABLETON_MCP_MAX_BUFFER=5242880  # 5MB
   ```

2. **Request less data at once:**
   - Get individual tracks instead of all tracks
   - Limit note queries to specific time ranges

### Commands timing out

**Symptoms:**
- "Timeout waiting for operation to complete"

**Solutions:**

1. **Increase command timeout:**
   ```bash
   export ABLETON_MCP_COMMAND_TIMEOUT=60.0
   ```

2. **Check Ableton CPU:**
   - High CPU can delay command processing
   - Freeze tracks to reduce CPU load

## Common Workflow Issues

### Clip won't fire

**Possible causes:**
1. Track not armed for recording
2. Clip slot empty
3. Another clip playing in exclusive slot

### Notes not appearing

**Possible causes:**
1. Clip is audio, not MIDI
2. Note data invalid (pitch out of range)
3. Time position outside clip loop

### Warp markers not working

**Possible causes:**
1. Clip is MIDI, not audio
2. Warping disabled on clip
3. Invalid beat_time position

## Performance Issues

### Slow response times

**Solutions:**

1. **Check Ableton CPU usage:**
   - View > CPU Meter
   - Freeze heavy tracks

2. **Reduce concurrent connections:**
   ```bash
   export ABLETON_MCP_MAX_CLIENTS=5
   ```

3. **Enable connection pooling** (use persistent connections)

### Memory issues

**Solutions:**

1. **Limit buffer sizes:**
   ```bash
   export ABLETON_MCP_MAX_BUFFER=1048576  # 1MB
   export ABLETON_MCP_MAX_QUEUE_SIZE=50
   ```

2. **Close unused client connections**

## Getting Help

### Collect debug information

```bash
# Check versions
python --version
pip show mcp fastapi

# Check configuration
env | grep -E "(ABLETON|REST_API|RATE_LIMIT)"

# Test connection
curl http://localhost:8000/api/health
```

### Report issues

1. Include debug information above
2. Include error messages (full stack trace if available)
3. Describe steps to reproduce
4. Open issue at: https://github.com/jpoindexter/ableton-mcp/issues
