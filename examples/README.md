# AbletonMCP Examples

Example scripts and usage patterns for AbletonMCP.

## Available Examples

### ollama_example.py

Interactive CLI chat that connects Ollama to Ableton Live.

**Requirements:**
- Ollama installed and running
- Model with tool support (llama3.2, mistral, etc.)
- REST API server running

**Usage:**
```bash
# Start the REST API server (in one terminal)
python MCP_Server/rest_api_server.py

# Run the chat (in another terminal)
python examples/ollama_example.py
```

**Example prompts:**
- "Create a house beat at 124 BPM"
- "Add a funky bassline in E minor"
- "Set the tempo to 90"
- "Create scenes for intro, verse, and chorus"
- "Add reverb to track 1"

## Quick Start Recipes

### Create a Basic Beat

```python
import requests

API = "http://localhost:8000/api"

# Set tempo
requests.post(f"{API}/tempo", json={"tempo": 120})

# Create a drum track
requests.post(f"{API}/tracks/midi", json={"name": "Drums"})

# Create a clip
requests.post(f"{API}/tracks/0/clips/0", json={"length": 4})

# Generate a drum pattern
pattern = requests.post(f"{API}/music/drums", json={"style": "house"}).json()

# Add notes to clip
requests.post(f"{API}/tracks/0/clips/0/notes", json={
    "track_index": 0,
    "clip_index": 0,
    "notes": pattern["notes"]
})

# Fire the clip
requests.post(f"{API}/tracks/0/clips/0/fire")
```

### Create a Full Song Structure

```python
import requests

API = "http://localhost:8000/api"

# Create scenes
for name in ["Intro", "Verse", "Chorus", "Outro"]:
    requests.post(f"{API}/scenes", json={"name": name})

# Create tracks
requests.post(f"{API}/tracks/midi", json={"name": "Drums"})
requests.post(f"{API}/tracks/midi", json={"name": "Bass"})
requests.post(f"{API}/tracks/midi", json={"name": "Lead"})

# Fire a scene
requests.post(f"{API}/scenes/0/fire")
```

### Using with Different LLMs

The REST API works with any LLM that supports function calling:

**Ollama:**
```python
import requests

response = requests.post("http://localhost:11434/api/chat", json={
    "model": "llama3.2",
    "messages": [{"role": "user", "content": "Create a drum beat"}],
    "tools": [...]  # Tool definitions from /tools endpoint
})
```

**OpenAI:**
```python
from openai import OpenAI

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Create a drum beat"}],
    tools=[...]  # Tool definitions
)
```

## Writing Your Own Integration

1. Get tool definitions: `GET http://localhost:8000/tools`
2. Send to your LLM with user prompt
3. Parse tool calls from LLM response
4. Execute via: `POST http://localhost:8000/api/command`
5. Return results to LLM for follow-up

See `ollama_example.py` for a complete implementation.
