# AbletonMCP - Ableton Live Model Context Protocol Integration

[![smithery badge](https://smithery.ai/badge/@ahujasid/ableton-mcp)](https://smithery.ai/server/@ahujasid/ableton-mcp)

AbletonMCP connects Ableton Live to Claude AI through the Model Context Protocol (MCP), allowing Claude to directly interact with and control Ableton Live. This integration enables AI-assisted music production, track creation, and Live session manipulation.

**80+ tools** for comprehensive Ableton Live control including AI-powered music generation.

## Features

### Core Features
- **Two-way communication**: Connect Claude AI to Ableton Live through a socket-based server
- **Full session control**: Transport, tempo, metronome, undo/redo
- **Track manipulation**: Create, delete, duplicate, and modify MIDI and audio tracks
- **Clip operations**: Create, edit, duplicate, loop, and color clips
- **Note editing**: Add, remove, transpose notes with full velocity/timing control
- **Device control**: Load, toggle, delete instruments and effects
- **Scene management**: Create, fire, duplicate, and organize scenes
- **Browser access**: Navigate and load from Ableton's library
- **Return/Send tracks**: Full aux bus control
- **Recording**: Arm tracks, capture MIDI, session/arrangement recording
- **Arrangement view**: Locators, loop regions, timeline navigation
- **I/O routing**: Configure track inputs and outputs
- **Performance monitoring**: CPU load, session info

### AI Music Helpers
- **Scale reference**: Get notes for 12 scale types (major, minor, modes, blues, pentatonic)
- **Quantization**: Snap clip notes to any grid size
- **Humanization**: Add natural timing and velocity variations
- **Drum pattern generation**: 8 styles (basic, house, techno, hip-hop, trap, dnb, jazz, funk)
- **Bassline generation**: 6 styles (basic, walking, synth, funk, octave, arpeggiated)

## Tool Reference

### Transport & Session (8 tools)
| Tool | Description |
|------|-------------|
| `get_session_info` | Get current session state (tempo, time signature, tracks, scenes) |
| `set_tempo` | Set session tempo in BPM |
| `start_playback` | Start playback |
| `stop_playback` | Stop playback |
| `get_metronome_state` | Get metronome on/off status |
| `set_metronome` | Enable/disable metronome |
| `undo` | Undo last action |
| `redo` | Redo last undone action |

### Track Management (12 tools)
| Tool | Description |
|------|-------------|
| `get_track_info` | Get details for a specific track |
| `create_midi_track` | Create a new MIDI track |
| `create_audio_track` | Create a new audio track |
| `delete_track` | Delete a track |
| `duplicate_track` | Duplicate a track with all clips and devices |
| `set_track_name` | Rename a track |
| `set_track_color` | Set track color |
| `set_track_mute` | Mute/unmute a track |
| `set_track_solo` | Solo/unsolo a track |
| `set_track_arm` | Arm/disarm a track for recording |
| `set_track_volume` | Set track volume |
| `set_track_pan` | Set track panning |

### Clip Operations (9 tools)
| Tool | Description |
|------|-------------|
| `get_clip_info` | Get clip details and notes |
| `create_clip` | Create a new MIDI clip |
| `delete_clip` | Delete a clip |
| `duplicate_clip` | Duplicate a clip to another slot |
| `fire_clip` | Trigger a clip to play |
| `stop_clip` | Stop a playing clip |
| `set_clip_name` | Rename a clip |
| `set_clip_color` | Set clip color |
| `set_clip_loop` | Configure clip loop points |

### Note Editing (5 tools)
| Tool | Description |
|------|-------------|
| `get_clip_notes` | Get all notes in a clip |
| `add_notes_to_clip` | Add MIDI notes to a clip |
| `remove_notes` | Remove specific notes from a clip |
| `remove_all_notes` | Clear all notes from a clip |
| `transpose_notes` | Transpose all notes by semitones |

### Scene Management (8 tools)
| Tool | Description |
|------|-------------|
| `get_all_scenes` | List all scenes with info |
| `create_scene` | Create a new scene |
| `delete_scene` | Delete a scene |
| `fire_scene` | Trigger an entire scene row |
| `stop_scene` | Stop a scene |
| `set_scene_name` | Rename a scene |
| `set_scene_color` | Set scene color |
| `duplicate_scene` | Duplicate a scene |

### Device Control (6 tools)
| Tool | Description |
|------|-------------|
| `get_device_info` | Get device details and parameters |
| `get_device_parameters` | Get all parameters for a device |
| `set_device_parameter` | Set a device parameter value |
| `toggle_device` | Enable/disable a device |
| `delete_device` | Remove a device from a track |
| `load_instrument_or_effect` | Load an instrument or effect |

### Return/Send Tracks (5 tools)
| Tool | Description |
|------|-------------|
| `get_return_tracks` | List all return tracks |
| `get_return_track_info` | Get return track details |
| `set_send_level` | Set send amount from track to return |
| `set_return_volume` | Set return track volume |
| `set_return_pan` | Set return track panning |

### Browser Navigation (3 tools)
| Tool | Description |
|------|-------------|
| `get_browser_tree` | Navigate the browser hierarchy |
| `get_browser_items` | Get items in a browser category |
| `load_browser_item` | Load an item from the browser |

### View Control (5 tools)
| Tool | Description |
|------|-------------|
| `get_current_view` | Get active view (Session/Arrangement/Detail) |
| `focus_view` | Switch to a specific view |
| `select_track` | Select a track |
| `select_scene` | Select a scene |
| `select_clip` | Select a clip |

### Recording (6 tools)
| Tool | Description |
|------|-------------|
| `start_recording` | Begin recording |
| `stop_recording` | Stop recording |
| `toggle_session_record` | Toggle session record mode |
| `toggle_arrangement_record` | Toggle arrangement record mode |
| `set_overdub` | Enable/disable overdub |
| `capture_midi` | Capture recently played MIDI |

### Arrangement View (6 tools)
| Tool | Description |
|------|-------------|
| `get_arrangement_length` | Get total arrangement time |
| `set_arrangement_loop` | Set loop region |
| `jump_to_time` | Seek to a specific time |
| `get_locators` | Get arrangement markers |
| `create_locator` | Add a marker |
| `delete_locator` | Remove a marker |

### I/O Routing (6 tools)
| Tool | Description |
|------|-------------|
| `get_track_input_routing` | Get track input configuration |
| `get_track_output_routing` | Get track output configuration |
| `get_available_inputs` | List available input options |
| `get_available_outputs` | List available output options |
| `set_track_input_routing` | Set track input |
| `set_track_output_routing` | Set track output |

### Performance & Session (5 tools)
| Tool | Description |
|------|-------------|
| `get_cpu_load` | Get current CPU usage |
| `get_session_path` | Get current project file path |
| `is_session_modified` | Check for unsaved changes |
| `get_metronome_state` | Get metronome status |
| `set_metronome` | Toggle metronome |

### AI Music Helpers (6 tools)
| Tool | Description |
|------|-------------|
| `get_scale_notes` | Get MIDI notes for any scale |
| `quantize_clip_notes` | Quantize notes to a grid |
| `humanize_clip_timing` | Add timing variation |
| `humanize_clip_velocity` | Add velocity variation |
| `generate_drum_pattern` | Generate drum MIDI patterns |
| `generate_bassline` | Generate bassline patterns |

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
   - Right-click Ableton Live app → Show Package Contents → `Contents/App-Resources/MIDI Remote Scripts/`
   - Or: `/Users/[Username]/Library/Preferences/Ableton/Live XX/User Remote Scripts`

   **Windows:**
   - `C:\Users\[Username]\AppData\Roaming\Ableton\Live x.x.x\Preferences\User Remote Scripts`
   - Or: `C:\ProgramData\Ableton\Live XX\Resources\MIDI Remote Scripts\`

3. Create a folder called `AbletonMCP` in the Remote Scripts directory

4. Paste the `__init__.py` file into the `AbletonMCP` folder

5. Launch Ableton Live

6. Go to Settings → Link, Tempo & MIDI

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
Claude will:
1. Create a MIDI track
2. Load a drum rack
3. Generate a drum pattern using `generate_drum_pattern`
4. Add the notes to a clip

#### Build a Track
```
"Create a synthwave track with drums, bass, and synth lead"
```
Claude will:
1. Set tempo to 120 BPM
2. Create multiple tracks with appropriate instruments
3. Generate patterns for each element
4. Organize into scenes

#### Mix and Arrange
```
"Add reverb to the drums and create an intro scene"
```
Claude will:
1. Load a reverb effect on the drum track
2. Create a new scene
3. Duplicate and modify clips for variation

### AI Music Generation

#### Generate Drum Patterns
Available styles: `basic`, `house`, `techno`, `hip_hop`, `trap`, `dnb`, `jazz`, `funk`

```
"Generate a house drum pattern"
```

#### Generate Basslines
Available styles: `basic`, `walking`, `synth`, `funk`, `octave`, `arpeggiated`

```
"Create a funky bassline in E minor"
```

#### Get Scale Notes
Available scales: `major`, `minor`, `dorian`, `phrygian`, `lydian`, `mixolydian`, `aeolian`, `locrian`, `harmonic_minor`, `melodic_minor`, `pentatonic_major`, `pentatonic_minor`, `blues`

```
"What notes are in D dorian?"
```

#### Humanize Your Music
```
"Humanize the timing and velocity of the bass clip"
```

### Scene Workflow

Scenes let you trigger entire rows of clips horizontally:

```
"Create scenes for intro, verse, chorus, and outro"
"Fire the chorus scene"
```

### Recording

```
"Arm track 1 and start recording"
"Capture my last MIDI playing into a clip"
```

### Arrangement View

```
"Create a locator at bar 16 called 'Drop'"
"Set the arrangement loop from bar 8 to bar 24"
"Jump to bar 32"
```

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
- Verify Python is installed correctly

### Commands Not Working
- Make sure you're requesting actions on valid track/clip indices
- Check that clips exist before trying to edit notes
- Verify devices are loaded before adjusting parameters

## Technical Details

### Communication Protocol

JSON-based protocol over TCP sockets (port 9877):

**Request:**
```json
{
    "type": "command_name",
    "params": { ... }
}
```

**Response:**
```json
{
    "status": "success",
    "result": { ... }
}
```

### Architecture

```
Claude AI ←→ MCP Server (Python/FastMCP) ←→ Ableton Remote Script (Python)
                    ↓                              ↓
              Port 9877 TCP                   Ableton Live API
```

---

## Alternative: Ollama & Other LLMs

AbletonMCP also supports **Ollama** and other LLMs via a REST API. This lets you use free, local AI models.

### Quick Start with Ollama

1. Install Ollama: https://ollama.ai
   ```bash
   # macOS
   brew install ollama
   ```

2. Pull a model with tool support:
   ```bash
   ollama pull llama3.2
   ```

3. Install REST API dependencies:
   ```bash
   pip install fastapi uvicorn pydantic
   ```

4. Start the REST API server:
   ```bash
   python MCP_Server/rest_api_server.py
   ```

5. Run the interactive chat:
   ```bash
   python examples/ollama_example.py
   ```

### REST API Endpoints

The REST API runs on `http://localhost:8000`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Check Ableton connection |
| `/tools` | GET | Get tool definitions for LLMs |
| `/api/command` | POST | Execute any Ableton command |
| `/docs` | GET | Interactive API documentation |

Example using curl:
```bash
# Get session info
curl http://localhost:8000/api/session

# Set tempo
curl -X POST http://localhost:8000/api/tempo \
  -H "Content-Type: application/json" \
  -d '{"tempo": 120}'

# Create a drum pattern
curl -X POST http://localhost:8000/api/music/drums \
  -H "Content-Type: application/json" \
  -d '{"style": "house", "bars": 2}'
```

### Supported LLM Providers

| Provider | Cost | Setup |
|----------|------|-------|
| Ollama | Free (local) | `ollama pull llama3.2` |
| Groq | Free tier | API key from console.groq.com |
| OpenAI | Paid | API key from platform.openai.com |
| Claude API | Paid | API key from console.anthropic.com |

---

## Alternative: Max for Live Device

For a fully integrated experience without needing Claude Desktop, use the **Max for Live device**.

### Features
- Multi-provider support (Ollama, OpenAI, Claude API, Groq)
- Visual UI inside Ableton
- No external server needed
- Works with any LLM

### Installation

1. Copy `AbletonMCP_M4L` folder to:
   - macOS: `~/Music/Ableton/User Library/Presets/Audio Effects/Max Audio Effect/`
   - Windows: `Documents\Ableton\User Library\Presets\Audio Effects\Max Audio Effect\`

2. Rename `AbletonMCP.amxd.maxpat` to `AbletonMCP.amxd`

3. Drag onto any track in Ableton Live

4. Select your AI provider and start chatting!

See [AbletonMCP_M4L/README.md](AbletonMCP_M4L/README.md) for detailed setup.

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Credits

- Original AbletonMCP by [Siddharth](https://x.com/sidahuj)
- Extended version with 80+ tools and AI helpers

## Disclaimer

This is a third-party integration and not made by Ableton.

## License

MIT License - See LICENSE file for details.
