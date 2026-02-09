# AbletonMCP - Ableton Live Model Context Protocol Integration

[![smithery badge](https://smithery.ai/badge/@ahujasid/ableton-mcp)](https://smithery.ai/server/@ahujasid/ableton-mcp)

AbletonMCP connects Ableton Live to Claude AI through the Model Context Protocol (MCP), allowing Claude to directly interact with and control Ableton Live. This integration enables AI-assisted music production, track creation, and Live session manipulation.

**200+ tools** for near-complete Ableton Live Object Model (LOM) coverage including AI-powered music generation.

## Three Ways to Use AbletonMCP

| Method | Best For | Requirements |
|--------|----------|-------------|
| **MCP Server** (Claude Desktop / Cursor) | Claude AI integration | Claude Desktop or Cursor |
| **REST API** (Ollama / OpenAI / Any LLM) | Any LLM, custom apps | Python, FastAPI |
| **Max for Live Device** | In-Ableton AI chat | Ableton Suite / M4L |

## Features

### Transport & Session
- Play, stop, record, overdub, capture MIDI, tap tempo, continue playing
- Tempo, time signature, metronome, count-in, swing, groove
- Arrangement loop, locators, jump to time, scrub

### Track Control
- Create/delete/duplicate MIDI, audio, group, and return tracks
- Volume, pan, mute, solo, arm, color, monitoring, delay
- Freeze/flatten, fold/unfold groups, implicit arm
- Input/output routing, crossfade assign
- Multi-track operations: solo exclusive, unsolo all, unmute all, unarm all

### Clip Operations
- Create/delete/duplicate/fire/stop clips
- Loop settings, start/end markers, gain, pitch, color
- Warp modes, warp markers, RAM mode
- Launch modes, launch quantization, follow actions
- Clip fades (in/out), trigger quantization
- Playing position, velocity amount

### MIDI Editing
- Add/remove/transpose notes, get notes in range
- Move notes (time + pitch shift), replace all notes
- Quantize, deselect all, duplicate loop
- Select all notes, set clip notes

### Devices & Effects
- Load instruments/effects from browser, toggle on/off, delete
- Get/set any device parameter, device presets
- Move devices (left/right/to position), collapse/expand
- Rack chains, rack macros, drum rack pads (mute/solo/name)
- Simpler/Sampler sample info and parameters

### Scene Management
- Create/delete/duplicate/fire/stop scenes, color, name

### Automation
- Clip automation envelopes (get/set/clear)
- Session automation record, arrangement overdub
- Re-enable automation

### Browser
- Navigate browser tree, search, load items
- Browse by path, get children, categories

### View & Selection
- Focus view (Session/Arrangement/Detail)
- Select track/scene/clip/device
- Detail clip, highlighted clip slot
- Draw mode, follow mode, grid quantization, zoom

### Recording
- Arm, record, overdub, capture MIDI
- Session/arrangement record modes
- MIDI recording quantization

### Mixing
- Track/master output metering (L/R)
- Send levels, pre/post send
- Return track volume/pan
- Master volume/pan, cue volume
- Crossfader position

### Song Properties
- Root note, scale, signature
- Groove amount, exclusive arm/solo
- Punch in/out, back to arrangement
- Record mode, can capture MIDI

### AI Music Helpers
- Scale reference (12+ scale types)
- Drum pattern generation (8 styles: house, techno, hip-hop, trap, dnb, jazz, funk, basic)
- Bassline generation (6 styles: basic, walking, synth, funk, octave, arpeggiated)
- Quantize/humanize timing and velocity

## Installation

### Prerequisites

- Ableton Live 10 or newer
- Python 3.8 or newer
- [uv package manager](https://astral.sh/uv)

**Install uv:**
```bash
# macOS
brew install uv

# Other platforms
# See https://docs.astral.sh/uv/getting-started/installation/
```

### Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

**Location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
    "mcpServers": {
        "AbletonMCP": {
            "command": "uvx",
            "args": ["ableton-mcp"]
        }
    }
}
```

### Installing via Smithery

```bash
npx -y @smithery/cli install @ahujasid/ableton-mcp --client claude
```

### Installing the Ableton Remote Script

1. Download `AbletonMCP_Remote_Script/__init__.py` from this repo

2. Copy to Ableton's MIDI Remote Scripts directory:

   **macOS:**
   - Right-click Ableton Live app > Show Package Contents > `Contents/App-Resources/MIDI Remote Scripts/`
   - Or: `/Users/[Username]/Library/Preferences/Ableton/Live XX/User Remote Scripts`

   **Windows:**
   - `C:\Users\[Username]\AppData\Roaming\Ableton\Live x.x.x\Preferences\User Remote Scripts`
   - Or: `C:\ProgramData\Ableton\Live XX\Resources\MIDI Remote Scripts\`

3. Create a folder called `AbletonMCP` in the Remote Scripts directory

4. Paste the `__init__.py` file into the `AbletonMCP` folder

5. Launch Ableton Live

6. Go to Settings > Link, Tempo & MIDI

7. In Control Surface dropdown, select "AbletonMCP"

8. Set Input and Output to "None"

### Cursor Integration

Go to Cursor Settings > MCP and add:
```
uvx ableton-mcp
```

## Usage Guide

### Getting Started

1. Ensure the Ableton Remote Script is loaded (look for "AbletonMCP" in Control Surface)
2. Configure Claude Desktop or Cursor with the MCP server
3. Start chatting with Claude about your music production needs

### Example Workflows

#### Create a Beat
```
"Create a hip-hop drum pattern at 90 BPM with a 808 kit"
```

#### Build a Full Track
```
"Create a raw hypnotic techno track at 135 BPM with kick, hats, clap, bass, and acid lead"
```

#### Mix and Arrange
```
"Add reverb to the drums, set up a sidechain send, and create intro/verse/chorus/outro scenes"
```

#### Sound Design
```
"Load a Simpler on track 3, show me the sample parameters, and adjust the filter"
```

### AI Music Generation

#### Generate Drum Patterns
Available styles: `basic`, `house`, `techno`, `hip_hop`, `trap`, `dnb`, `jazz`, `funk`

#### Generate Basslines
Available styles: `basic`, `walking`, `synth`, `funk`, `octave`, `arpeggiated`

#### Get Scale Notes
Available scales: `major`, `minor`, `dorian`, `phrygian`, `lydian`, `mixolydian`, `aeolian`, `locrian`, `harmonic_minor`, `melodic_minor`, `pentatonic_major`, `pentatonic_minor`, `blues`

## REST API (Ollama & Other LLMs)

AbletonMCP includes a REST API for use with any LLM provider.

### Quick Start with Ollama

1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull llama3.2`
3. Install dependencies: `pip install fastapi uvicorn pydantic`
4. Start the server: `python MCP_Server/rest_api_server.py`
5. Run interactive chat: `python examples/ollama_example.py`

### REST API Features

- **200+ commands** whitelisted and validated
- **API key authentication** (optional, via `REST_API_KEY` env var)
- **Rate limiting** (configurable per-IP)
- **CORS** configured for localhost by default
- **Pagination** on list endpoints (scenes, tracks, device parameters)
- **OpenAI-compatible tool definitions** at `/tools`

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Check Ableton connection |
| `/tools` | GET | Get LLM tool definitions |
| `/api/session` | GET | Session info |
| `/api/tracks` | GET | List all tracks (with pagination) |
| `/api/scenes` | GET | List all scenes (with pagination) |
| `/api/command` | POST | Execute any command |
| `/docs` | GET | Interactive Swagger docs |

### Supported LLM Providers

| Provider | Cost | Setup |
|----------|------|-------|
| Ollama | Free (local) | `ollama pull llama3.2` |
| Groq | Free tier | API key from console.groq.com |
| OpenAI | Paid | API key from platform.openai.com |
| Claude API | Paid | API key from console.anthropic.com |

## Max for Live Device

For a fully integrated experience inside Ableton, use the **Max for Live device**.

### Features
- Multi-provider support (Ollama, OpenAI, Claude API, Groq)
- Visual chat UI inside Ableton's device view
- 200+ tool definitions for complete LOM control
- No external server needed

### Installation

1. Copy `AbletonMCP_M4L` folder to:
   - macOS: `~/Music/Ableton/User Library/Presets/Audio Effects/Max Audio Effect/`
   - Windows: `Documents\Ableton\User Library\Presets\Audio Effects\Max Audio Effect\`

2. Build the `.amxd` binary (the repo includes a `.maxpat` source file):
   ```bash
   python3 scripts/build_amxd.py
   ```
   Or rename `AbletonMCP.amxd.maxpat` to `AbletonMCP.amxd`

3. Drag onto any track in Ableton Live

4. Select your AI provider and start chatting!

See [AbletonMCP_M4L/README.md](AbletonMCP_M4L/README.md) for detailed setup.

## Documentation

- [MANUAL.md](docs/MANUAL.md) - Complete command reference with examples and a step-by-step techno track tutorial
- [CONFIG.md](docs/CONFIG.md) - Configuration and environment variables

## Troubleshooting

### Connection Issues
- Verify AbletonMCP is selected in Ableton's Control Surface settings
- Check that no other application is using port 9877
- Restart both Claude and Ableton Live

### Timeout Errors
- Break complex requests into smaller steps
- Allow time for Ableton to process commands

### Script Not Loading
- Ensure the `__init__.py` file is in a folder named exactly `AbletonMCP`
- Check Ableton's Log.txt for errors

### Commands Not Working
- Make sure you're requesting actions on valid track/clip indices
- Check that clips exist before trying to edit notes
- Verify devices are loaded before adjusting parameters

## Technical Details

### Communication Protocol

JSON-based protocol over TCP sockets (port 9877):

```json
// Request
{"type": "command_name", "params": { ... }}

// Response
{"status": "success", "result": { ... }}
```

### Architecture

```
Claude AI <-> MCP Server (Python/FastMCP) <-> Ableton Remote Script (Python)
                    |                              |
              Port 9877 TCP                   Ableton Live API (LOM)

REST API (FastAPI) <-> Ableton Remote Script
       |
  Port 8000 HTTP

Max for Live Device <-> LLM Provider API (Ollama/OpenAI/Claude/Groq)
       |
  Node for Max (JavaScript)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Credits

- Original AbletonMCP by [Siddharth](https://x.com/sidahuj)
- Extended with 200+ tools, REST API, M4L device, and AI helpers

## Disclaimer

This is a third-party integration and not made by Ableton.

## License

MIT License - See LICENSE file for details.
