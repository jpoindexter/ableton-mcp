# AbletonMCP Complete Manual

**Control Ableton Live with AI assistants like Claude, GPT, or any LLM.**

AbletonMCP provides 200+ commands covering virtually every controllable aspect of Ableton Live through:
- **MCP Server** - For Claude Desktop integration
- **REST API** - For any LLM with function calling (Ollama, GPT, etc.)

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Transport Control](#transport-control)
3. [Track Operations](#track-operations)
4. [Clip Operations](#clip-operations)
5. [MIDI Editing](#midi-editing)
6. [Audio Clip Editing](#audio-clip-editing)
7. [Device Control](#device-control)
8. [Scene Control](#scene-control)
9. [Browser & Loading](#browser--loading)
10. [Mixing & Routing](#mixing--routing)
11. [Recording](#recording)
12. [Arrangement](#arrangement)
13. [Automation](#automation)
14. [View Control](#view-control)
15. [AI Music Helpers](#ai-music-helpers)
16. [Advanced Features](#advanced-features)

---

## Quick Start

### Installation

1. Copy `AbletonMCP_Remote_Script` folder to Ableton's MIDI Remote Scripts:
   - **macOS**: `/Applications/Ableton Live.app/Contents/App-Resources/MIDI Remote Scripts/AbletonMCP`
   - **Windows**: `C:\ProgramData\Ableton\Live x.x\Resources\MIDI Remote Scripts\AbletonMCP`

2. In Ableton: Preferences > Link, Tempo & MIDI > Control Surface > Select "AbletonMCP"

3. Run the server:
   ```bash
   # For Claude Desktop (MCP)
   python -m MCP_Server.server

   # For REST API (Ollama, GPT, etc.)
   python -m MCP_Server.rest_api_server
   ```

### Basic Example (REST API)

```bash
# Get session info
curl http://localhost:8000/api/session

# Set tempo to 128 BPM
curl -X POST http://localhost:8000/api/tempo -H "Content-Type: application/json" -d '{"tempo": 128}'

# Start playback
curl -X POST http://localhost:8000/api/transport/play
```

---

## Transport Control

Control playback, tempo, and navigation.

| Command | Description | Parameters |
|---------|-------------|------------|
| `start_playback` | Start playing | - |
| `stop_playback` | Stop playing | - |
| `continue_playing` | Continue from current position | - |
| `set_tempo` | Set BPM (20-300) | `tempo` |
| `tap_tempo` | Tap tempo | - |
| `stop_all_clips` | Stop all clips | - |
| `jump_to_time` | Jump to beat position | `time` |
| `scrub_by` | Move position by delta | `delta` |

### Examples

```bash
# Set tempo to 140 BPM
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "set_tempo", "params": {"tempo": 140}}'

# Jump to bar 5 (beat 16 in 4/4)
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "jump_to_time", "params": {"time": 16}}'
```

---

## Track Operations

Create, modify, and control tracks.

| Command | Description | Parameters |
|---------|-------------|------------|
| `create_midi_track` | Create MIDI track | `index`, `name` |
| `create_audio_track` | Create audio track | `index`, `name` |
| `delete_track` | Delete track | `track_index` |
| `duplicate_track` | Duplicate track | `track_index` |
| `set_track_name` | Rename track | `track_index`, `name` |
| `set_track_color` | Set track color (0-69) | `track_index`, `color` |
| `set_track_volume` | Set volume (0.0-1.0) | `track_index`, `volume` |
| `set_track_pan` | Set pan (-1.0 to 1.0) | `track_index`, `pan` |
| `set_track_mute` | Mute/unmute | `track_index`, `mute` |
| `set_track_solo` | Solo/unsolo | `track_index`, `solo` |
| `set_track_arm` | Arm for recording | `track_index`, `arm` |
| `freeze_track` | Freeze track | `track_index` |
| `flatten_track` | Flatten frozen track | `track_index` |
| `get_track_info` | Get track details | `track_index` |
| `get_all_track_names` | Quick list of all tracks | - |

### Examples

```bash
# Create a MIDI track named "Synth Lead"
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "create_midi_track", "params": {"index": 0, "name": "Synth Lead"}}'

# Set track 0 volume to 80%
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "set_track_volume", "params": {"track_index": 0, "volume": 0.8}}'

# Solo track 2 exclusively (unsolo all others)
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "solo_exclusive", "params": {"track_index": 2}}'

# Unsolo all tracks
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "unsolo_all"}'
```

---

## Clip Operations

Create, fire, and manage clips.

| Command | Description | Parameters |
|---------|-------------|------------|
| `create_clip` | Create empty MIDI clip | `track_index`, `clip_index`, `length` |
| `delete_clip` | Delete clip | `track_index`, `clip_index` |
| `duplicate_clip` | Duplicate clip | `track_index`, `clip_index` |
| `fire_clip` | Launch clip | `track_index`, `clip_index` |
| `stop_clip` | Stop clip | `track_index`, `clip_index` |
| `set_clip_name` | Rename clip | `track_index`, `clip_index`, `name` |
| `set_clip_color` | Set clip color | `track_index`, `clip_index`, `color` |
| `set_clip_loop` | Set loop points | `track_index`, `clip_index`, `loop_start`, `loop_end`, `looping` |
| `duplicate_clip_loop` | Double clip length | `track_index`, `clip_index` |
| `get_clip_info` | Get clip details | `track_index`, `clip_index` |
| `get_clip_is_playing` | Check if playing | `track_index`, `clip_index` |
| `get_clip_playing_position` | Get playhead position | `track_index`, `clip_index` |

### Clip Launch Settings

| Command | Description | Parameters |
|---------|-------------|------------|
| `set_clip_launch_mode` | Set launch mode | `track_index`, `clip_index`, `mode` |
| `set_clip_launch_quantization` | Set launch quantize | `track_index`, `clip_index`, `quantization` |
| `set_clip_follow_action` | Set follow action | `track_index`, `clip_index`, `action_a`, `action_b`, `chance`, `time` |

### Examples

```bash
# Create a 4-bar MIDI clip
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "create_clip", "params": {"track_index": 0, "clip_index": 0, "length": 16}}'

# Fire clip at track 0, slot 0
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "fire_clip", "params": {"track_index": 0, "clip_index": 0}}'

# Set loop to bars 1-2 (beats 0-8)
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "set_clip_loop", "params": {"track_index": 0, "clip_index": 0, "loop_start": 0, "loop_end": 8, "looping": true}}'
```

---

## MIDI Editing

Add, remove, and manipulate MIDI notes.

| Command | Description | Parameters |
|---------|-------------|------------|
| `add_notes_to_clip` | Add MIDI notes | `track_index`, `clip_index`, `notes` |
| `remove_notes` | Remove notes in range | `track_index`, `clip_index`, `from_time`, `time_span`, `from_pitch`, `pitch_span` |
| `remove_all_notes` | Clear all notes | `track_index`, `clip_index` |
| `transpose_notes` | Transpose by semitones | `track_index`, `clip_index`, `semitones` |
| `get_clip_notes` | Get all notes | `track_index`, `clip_index` |
| `get_notes_in_range` | Get notes in time/pitch range | `track_index`, `clip_index`, `start_time`, `end_time`, `pitch_start`, `pitch_end` |
| `set_clip_notes` | Replace all notes | `track_index`, `clip_index`, `notes` |
| `move_clip_notes` | Shift notes by time/pitch | `track_index`, `clip_index`, `time_delta`, `pitch_delta` |
| `quantize_clip` | Quantize notes to grid | `track_index`, `clip_index`, `quantize_to`, `amount` |
| `set_clip_velocity_amount` | Scale velocities | `track_index`, `clip_index`, `amount` |

### Note Format

Notes are specified as objects with:
- `pitch`: MIDI note (0-127, middle C = 60)
- `start_time`: Position in beats
- `duration`: Length in beats
- `velocity`: Velocity (1-127)
- `mute`: Optional, default false

### Examples

```bash
# Add a C major chord (C4, E4, G4)
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{
    "command": "add_notes_to_clip",
    "params": {
      "track_index": 0,
      "clip_index": 0,
      "notes": [
        {"pitch": 60, "start_time": 0, "duration": 1, "velocity": 100},
        {"pitch": 64, "start_time": 0, "duration": 1, "velocity": 100},
        {"pitch": 67, "start_time": 0, "duration": 1, "velocity": 100}
      ]
    }
  }'

# Transpose up an octave
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "transpose_notes", "params": {"track_index": 0, "clip_index": 0, "semitones": 12}}'

# Quantize to 1/16 notes (0.25 beats)
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "quantize_clip", "params": {"track_index": 0, "clip_index": 0, "quantize_to": 0.25, "amount": 1.0}}'

# Move all notes forward by 1 beat
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "move_clip_notes", "params": {"track_index": 0, "clip_index": 0, "time_delta": 1, "pitch_delta": 0}}'
```

---

## Audio Clip Editing

Modify audio clips - pitch, gain, warp, fades.

| Command | Description | Parameters |
|---------|-------------|------------|
| `set_clip_gain` | Set clip gain (dB) | `track_index`, `clip_index`, `gain` |
| `set_clip_pitch` | Transpose audio (-48 to +48) | `track_index`, `clip_index`, `pitch` |
| `set_clip_warp_mode` | Set warp algorithm | `track_index`, `clip_index`, `mode` |
| `get_clip_warp_info` | Get warp settings | `track_index`, `clip_index` |
| `set_clip_ram_mode` | Load to RAM | `track_index`, `clip_index`, `enabled` |
| `get_audio_clip_file_path` | Get source file path | `track_index`, `clip_index` |

### Warp Markers

| Command | Description | Parameters |
|---------|-------------|------------|
| `get_warp_markers` | Get all warp markers | `track_index`, `clip_index` |
| `add_warp_marker` | Add warp marker | `track_index`, `clip_index`, `beat_time`, `sample_time` |
| `delete_warp_marker` | Remove warp marker | `track_index`, `clip_index`, `index` |

### Fades

| Command | Description | Parameters |
|---------|-------------|------------|
| `get_clip_fades` | Get fade settings | `track_index`, `clip_index` |
| `set_clip_fade_in` | Set fade in | `track_index`, `clip_index`, `start`, `end` |
| `set_clip_fade_out` | Set fade out | `track_index`, `clip_index`, `start`, `end` |

### Examples

```bash
# Pitch shift up 5 semitones
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "set_clip_pitch", "params": {"track_index": 1, "clip_index": 0, "pitch": 5}}'

# Set gain to -3dB
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "set_clip_gain", "params": {"track_index": 1, "clip_index": 0, "gain": -3}}'
```

---

## Device Control

Control instruments and effects.

| Command | Description | Parameters |
|---------|-------------|------------|
| `get_device_parameters` | List all parameters | `track_index`, `device_index` |
| `set_device_parameter` | Set parameter value | `track_index`, `device_index`, `parameter_index`, `value` |
| `toggle_device` | Enable/disable device | `track_index`, `device_index` |
| `delete_device` | Remove device | `track_index`, `device_index` |
| `get_device_by_name` | Find device by name | `track_index`, `device_name` |
| `select_device` | Select for viewing | `track_index`, `device_index` |
| `get_selected_device` | Get selected device | - |

### Rack Control

| Command | Description | Parameters |
|---------|-------------|------------|
| `get_rack_chains` | List rack chains | `track_index`, `device_index` |
| `select_rack_chain` | Select chain | `track_index`, `device_index`, `chain_index` |
| `get_rack_macros` | Get macro values | `track_index`, `device_index` |
| `set_rack_macro` | Set macro value | `track_index`, `device_index`, `macro_index`, `value` |

### Drum Rack

| Command | Description | Parameters |
|---------|-------------|------------|
| `get_drum_rack_pads` | List all pads | `track_index`, `device_index` |
| `get_drum_pad_info` | Get pad details | `track_index`, `device_index`, `pad_index` |
| `set_drum_rack_pad_mute` | Mute pad | `track_index`, `device_index`, `note`, `mute` |
| `set_drum_rack_pad_solo` | Solo pad | `track_index`, `device_index`, `note`, `solo` |
| `set_drum_pad_name` | Rename pad | `track_index`, `device_index`, `pad_index`, `name` |

### Simpler/Sampler

| Command | Description | Parameters |
|---------|-------------|------------|
| `get_simpler_sample_info` | Get sample info | `track_index`, `device_index` |
| `get_simpler_parameters` | Get all params | `track_index`, `device_index` |

### Examples

```bash
# Get all parameters of first device on track 0
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "get_device_parameters", "params": {"track_index": 0, "device_index": 0}}'

# Set parameter 5 to 0.75
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "set_device_parameter", "params": {"track_index": 0, "device_index": 0, "parameter_index": 5, "value": 0.75}}'

# Set macro 1 to 100%
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "set_rack_macro", "params": {"track_index": 0, "device_index": 0, "macro_index": 0, "value": 1.0}}'
```

---

## Scene Control

Launch and manage scenes.

| Command | Description | Parameters |
|---------|-------------|------------|
| `get_all_scenes` | List all scenes | - |
| `create_scene` | Create scene | `index` |
| `delete_scene` | Delete scene | `scene_index` |
| `duplicate_scene` | Duplicate scene | `scene_index` |
| `fire_scene` | Launch scene | `scene_index` |
| `stop_scene` | Stop scene | `scene_index` |
| `set_scene_name` | Rename scene | `scene_index`, `name` |
| `set_scene_color` | Set color | `scene_index`, `color` |
| `select_scene` | Select scene | `scene_index` |
| `get_selected_scene` | Get selected | - |

### Examples

```bash
# Fire scene 0 (first scene)
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "fire_scene", "params": {"scene_index": 0}}'

# Rename scene
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "set_scene_name", "params": {"scene_index": 0, "name": "Intro"}}'
```

---

## Browser & Loading

Browse and load instruments, effects, samples.

| Command | Description | Parameters |
|---------|-------------|------------|
| `get_browser_tree` | Get browser structure | `category_type` |
| `search_browser` | Search for items | `query`, `category` |
| `load_instrument_or_effect` | Load by URI | `track_index`, `uri` |
| `load_browser_item` | Load item to track | `track_index`, `item_uri` |
| `load_browser_item_to_return` | Load to return track | `return_index`, `item_uri` |
| `load_device_preset` | Load device preset | `track_index`, `device_index`, `preset_uri` |

### Examples

```bash
# Search for "EQ Eight"
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "search_browser", "params": {"query": "EQ Eight", "category": "all"}}'

# Load Wavetable to track 0
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "load_instrument_or_effect", "params": {"track_index": 0, "uri": "query:Wavetable"}}'
```

---

## Mixing & Routing

Control sends, returns, routing, and crossfader.

### Sends & Returns

| Command | Description | Parameters |
|---------|-------------|------------|
| `get_return_tracks` | List return tracks | - |
| `get_send_level` | Get send level | `track_index`, `send_index` |
| `set_send_level` | Set send level (0-1) | `track_index`, `send_index`, `level` |
| `set_return_volume` | Set return volume | `return_index`, `volume` |
| `set_return_pan` | Set return pan | `return_index`, `pan` |
| `create_return_track` | Add return track | - |
| `delete_return_track` | Remove return | `index` |

### Routing

| Command | Description | Parameters |
|---------|-------------|------------|
| `get_track_input_routing` | Get input routing | `track_index` |
| `set_track_input_routing` | Set input routing | `track_index`, `routing_type`, `routing_channel` |
| `get_track_output_routing` | Get output routing | `track_index` |
| `set_track_output_routing` | Set output routing | `track_index`, `routing_type`, `routing_channel` |
| `get_available_inputs` | List input options | `track_index` |
| `get_available_outputs` | List output options | `track_index` |
| `set_track_monitoring` | Set monitoring mode | `track_index`, `monitoring` |

### Crossfader

| Command | Description | Parameters |
|---------|-------------|------------|
| `get_crossfader` | Get position | - |
| `set_crossfader` | Set position (0-1) | `value` |
| `get_track_crossfade_assign` | Get A/B assignment | `track_index` |
| `set_track_crossfade_assign` | Set A/B (0/1/2) | `track_index`, `assign` |

### Master

| Command | Description | Parameters |
|---------|-------------|------------|
| `get_master_info` | Get master track info | - |
| `set_master_volume` | Set master volume | `volume` |
| `set_master_pan` | Set master pan | `pan` |
| `get_cue_volume` | Get preview volume | - |
| `set_cue_volume` | Set preview volume | `volume` |

### Examples

```bash
# Set send A on track 0 to 50%
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "set_send_level", "params": {"track_index": 0, "send_index": 0, "level": 0.5}}'

# Assign track 0 to crossfader A
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "set_track_crossfade_assign", "params": {"track_index": 0, "assign": 0}}'
```

---

## Recording

Control recording modes.

| Command | Description | Parameters |
|---------|-------------|------------|
| `start_recording` | Start recording | - |
| `stop_recording` | Stop recording | - |
| `toggle_session_record` | Toggle session record | - |
| `toggle_arrangement_record` | Toggle arrangement record | - |
| `set_overdub` | Set MIDI overdub | `enabled` |
| `capture_midi` | Capture last played MIDI | - |
| `get_session_automation_record` | Get automation record state | - |
| `set_session_automation_record` | Enable/disable auto record | `enabled` |
| `get_arrangement_overdub` | Get arrangement overdub | - |
| `set_arrangement_overdub` | Set arrangement overdub | `enabled` |
| `re_enable_automation` | Re-enable all automation | - |
| `get_count_in_duration` | Get count-in setting | - |
| `set_count_in_duration` | Set count-in (0/1/2/4 bars) | `duration` |

### Examples

```bash
# Enable session automation recording
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "set_session_automation_record", "params": {"enabled": true}}'

# Set 2-bar count-in
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "set_count_in_duration", "params": {"duration": 2}}'
```

---

## Arrangement

Control arrangement view and locators.

| Command | Description | Parameters |
|---------|-------------|------------|
| `get_arrangement_length` | Get song length | - |
| `set_arrangement_loop` | Set loop region | `start`, `end`, `enabled` |
| `get_locators` | List all locators | - |
| `create_locator` | Add locator | `time`, `name` |
| `delete_locator` | Remove locator | `locator_index` |
| `jump_to_cue_point` | Jump to cue point | `index` |
| `jump_to_prev_cue` | Jump to previous cue | - |
| `jump_to_next_cue` | Jump to next cue | - |

### Punch Recording

| Command | Description | Parameters |
|---------|-------------|------------|
| `get_punch_settings` | Get punch in/out | - |
| `set_punch_in` | Enable punch in | `enabled` |
| `set_punch_out` | Enable punch out | `enabled` |
| `trigger_back_to_arrangement` | Back to arrangement | - |

### Examples

```bash
# Set loop from bar 1 to bar 5
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "set_arrangement_loop", "params": {"start": 0, "end": 16, "enabled": true}}'

# Create locator at bar 9
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "create_locator", "params": {"time": 32, "name": "Chorus"}}'
```

---

## Automation

Control clip automation envelopes.

| Command | Description | Parameters |
|---------|-------------|------------|
| `get_clip_automation` | Get envelope points | `track_index`, `clip_index`, `parameter_index` |
| `set_clip_automation` | Set envelope points | `track_index`, `clip_index`, `parameter_index`, `points` |
| `clear_clip_automation` | Clear envelope | `track_index`, `clip_index`, `parameter_index` |
| `get_clip_has_envelopes` | Check for envelopes | `track_index`, `clip_index` |

### Examples

```bash
# Set automation envelope (fade in volume)
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{
    "command": "set_clip_automation",
    "params": {
      "track_index": 0,
      "clip_index": 0,
      "parameter_index": 0,
      "points": [
        {"time": 0, "value": 0},
        {"time": 4, "value": 1}
      ]
    }
  }'
```

---

## View Control

Control Ableton's interface.

| Command | Description | Parameters |
|---------|-------------|------------|
| `get_current_view` | Get active view | - |
| `focus_view` | Switch view | `view_name` |
| `get_detail_clip` | Get clip in detail view | - |
| `set_detail_clip` | Show clip in detail | `track_index`, `clip_index` |
| `get_selected_track` | Get selected track | - |
| `select_track` | Select track | `track_index` |
| `get_follow_mode` | Get follow playhead | - |
| `set_follow_mode` | Set follow playhead | `enabled` |
| `get_draw_mode` | Get draw mode state | - |
| `set_draw_mode` | Enable/disable draw mode | `enabled` |
| `get_grid_quantization` | Get grid setting | - |
| `set_grid_quantization` | Set grid | `quantization`, `triplet` |

### View Names

- `Session` - Session view
- `Arranger` - Arrangement view
- `Detail` - Detail view
- `Detail/Clip` - Clip view
- `Detail/DeviceChain` - Device view
- `Browser` - Browser

### Examples

```bash
# Switch to arrangement view
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "focus_view", "params": {"view_name": "Arranger"}}'

# Enable follow playhead
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "set_follow_mode", "params": {"enabled": true}}'
```

---

## AI Music Helpers

Built-in AI-powered music generation helpers.

| Command | Description | Parameters |
|---------|-------------|------------|
| `get_scale_notes` | Get notes in scale | `root`, `scale_type` |
| `generate_drum_pattern` | Generate drum beat | `track_index`, `clip_index`, `style`, `complexity` |
| `generate_bassline` | Generate bass line | `track_index`, `clip_index`, `root`, `scale`, `style` |
| `humanize_clip_timing` | Randomize timing | `track_index`, `clip_index`, `amount` |
| `humanize_clip_velocity` | Randomize velocities | `track_index`, `clip_index`, `amount` |
| `quantize_clip_notes` | Smart quantize | `track_index`, `clip_index`, `grid`, `amount` |

### Scale Types

`major`, `minor`, `dorian`, `phrygian`, `lydian`, `mixolydian`, `locrian`, `harmonic_minor`, `melodic_minor`, `pentatonic_major`, `pentatonic_minor`, `blues`

### Examples

```bash
# Get C minor scale notes
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "get_scale_notes", "params": {"root": 0, "scale_type": "minor"}}'

# Generate a house drum pattern
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "generate_drum_pattern", "params": {"track_index": 0, "clip_index": 0, "style": "house", "complexity": 0.5}}'

# Humanize timing by 10%
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "humanize_clip_timing", "params": {"track_index": 0, "clip_index": 0, "amount": 0.1}}'
```

---

## Advanced Features

### Song Properties

| Command | Description | Parameters |
|---------|-------------|------------|
| `get_signature` | Get time signature | - |
| `set_signature` | Set time signature | `numerator`, `denominator` |
| `get_swing_amount` | Get global swing | - |
| `set_swing_amount` | Set global swing | `amount` |
| `get_groove_amount` | Get groove intensity | - |
| `set_groove_amount` | Set groove intensity | `amount` |
| `get_song_root_note` | Get song key | - |
| `set_song_root_note` | Set song key | `root_note` |
| `get_song_scale` | Get song scale | - |

### Groove Pool

| Command | Description | Parameters |
|---------|-------------|------------|
| `get_groove_pool` | List grooves | - |
| `apply_groove` | Apply groove to clip | `track_index`, `clip_index`, `groove_index` |
| `commit_groove` | Commit groove to clip | `track_index`, `clip_index` |

### Group Tracks

| Command | Description | Parameters |
|---------|-------------|------------|
| `create_group_track` | Create group | `track_indices` |
| `ungroup_tracks` | Ungroup | `track_index` |
| `fold_track` | Collapse group | `track_index` |
| `unfold_track` | Expand group | `track_index` |

### Track Capabilities

| Command | Description | Parameters |
|---------|-------------|------------|
| `get_track_capabilities` | Get track features | `track_index` |
| `get_track_delay` | Get track delay (ms) | `track_index` |
| `set_track_delay` | Set track delay | `track_index`, `delay_ms` |
| `get_track_output_meter` | Get meter level | `track_index` |

### Session Info

| Command | Description | Parameters |
|---------|-------------|------------|
| `get_session_info` | Full session overview | - |
| `get_session_path` | Get .als file path | - |
| `is_session_modified` | Check unsaved changes | - |
| `get_cpu_load` | Get CPU usage | - |
| `health_check` | Connection test | - |

---

## Color Reference

Ableton uses color indices 0-69:

| Range | Colors |
|-------|--------|
| 0-13 | Reds to Oranges |
| 14-27 | Yellows to Greens |
| 28-41 | Teals to Blues |
| 42-55 | Purples to Pinks |
| 56-69 | Grays and Whites |

---

## Error Handling

All commands return JSON with:

```json
// Success
{
  "status": "success",
  "result": { ... }
}

// Error
{
  "status": "error",
  "message": "Error description"
}
```

Common errors:
- `Track index out of range` - Invalid track_index
- `No clip in slot` - Empty clip slot
- `Not a MIDI clip` - Audio clip for MIDI operation
- `Not an audio clip` - MIDI clip for audio operation
- `Device index out of range` - Invalid device_index

---

## Tips for AI Assistants

1. **Always get session info first** to understand the project structure
2. **Check track types** before operations (MIDI vs audio)
3. **Use get_ commands** before set_ to understand current state
4. **Batch notes** in single add_notes_to_clip for efficiency
5. **Use humanize** for more natural-sounding results
6. **Check clip_is_playing** before modifying playing clips

---

---

## Complete Tutorial: Raw Hypnotic Techno Track (135 BPM)

This tutorial walks through creating a complete techno track from scratch using AbletonMCP commands. We'll cover drums, bass, melody, arrangement, mixing, and mastering.

### Step 1: Project Setup

```bash
# Get current session info
curl http://localhost:8000/api/session

# Set tempo to 135 BPM
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "set_tempo", "params": {"tempo": 135}}'

# Set time signature to 4/4
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "set_signature", "params": {"numerator": 4, "denominator": 4}}'

# Set key to A minor (root note 9 = A)
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "set_song_root_note", "params": {"root_note": 9}}'
```

### Step 2: Create Tracks

```bash
# Create drum track
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "create_midi_track", "params": {"index": 0, "name": "Drums"}}'

# Create bass track
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "create_midi_track", "params": {"index": 1, "name": "Bass"}}'

# Create synth lead track
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "create_midi_track", "params": {"index": 2, "name": "Synth Lead"}}'

# Create pad track
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "create_midi_track", "params": {"index": 3, "name": "Pad"}}'

# Create FX track
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "create_audio_track", "params": {"index": 4, "name": "FX Riser"}}'

# Set track colors (techno vibes - dark colors)
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "set_track_color", "params": {"track_index": 0, "color": 69}}'  # Gray for drums
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "set_track_color", "params": {"track_index": 1, "color": 3}}'   # Red for bass
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "set_track_color", "params": {"track_index": 2, "color": 45}}'  # Purple for lead
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "set_track_color", "params": {"track_index": 3, "color": 35}}'  # Blue for pad
```

### Step 3: Load Instruments

```bash
# Load Drum Rack on drums track
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "load_instrument_or_effect", "params": {"track_index": 0, "uri": "query:Drum Rack"}}'

# Load bass synth (Wavetable or Analog)
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "load_instrument_or_effect", "params": {"track_index": 1, "uri": "query:Wavetable"}}'

# Load lead synth
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "load_instrument_or_effect", "params": {"track_index": 2, "uri": "query:Wavetable"}}'

# Load pad synth
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "load_instrument_or_effect", "params": {"track_index": 3, "uri": "query:Wavetable"}}'
```

### Step 4: Create Drum Pattern (Raw Techno Kick + Hats)

```bash
# Create 4-bar drum clip
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "create_clip", "params": {"track_index": 0, "clip_index": 0, "length": 16}}'

# Name the clip
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "set_clip_name", "params": {"track_index": 0, "clip_index": 0, "name": "Main Beat"}}'

# Add techno kick pattern (4-on-the-floor with variations)
# Kick on C1 (36), Hi-hat on F#1 (42), Open hat on A#1 (46), Clap on D1 (38)
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{
    "command": "add_notes_to_clip",
    "params": {
      "track_index": 0,
      "clip_index": 0,
      "notes": [
        {"pitch": 36, "start_time": 0, "duration": 0.5, "velocity": 127},
        {"pitch": 36, "start_time": 1, "duration": 0.5, "velocity": 120},
        {"pitch": 36, "start_time": 2, "duration": 0.5, "velocity": 127},
        {"pitch": 36, "start_time": 3, "duration": 0.5, "velocity": 115},
        {"pitch": 36, "start_time": 4, "duration": 0.5, "velocity": 127},
        {"pitch": 36, "start_time": 5, "duration": 0.5, "velocity": 120},
        {"pitch": 36, "start_time": 6, "duration": 0.5, "velocity": 127},
        {"pitch": 36, "start_time": 7, "duration": 0.5, "velocity": 115},
        {"pitch": 36, "start_time": 8, "duration": 0.5, "velocity": 127},
        {"pitch": 36, "start_time": 9, "duration": 0.5, "velocity": 120},
        {"pitch": 36, "start_time": 10, "duration": 0.5, "velocity": 127},
        {"pitch": 36, "start_time": 11, "duration": 0.5, "velocity": 115},
        {"pitch": 36, "start_time": 12, "duration": 0.5, "velocity": 127},
        {"pitch": 36, "start_time": 13, "duration": 0.5, "velocity": 120},
        {"pitch": 36, "start_time": 14, "duration": 0.5, "velocity": 127},
        {"pitch": 36, "start_time": 15, "duration": 0.5, "velocity": 115},

        {"pitch": 42, "start_time": 0.5, "duration": 0.25, "velocity": 80},
        {"pitch": 42, "start_time": 1.0, "duration": 0.25, "velocity": 70},
        {"pitch": 42, "start_time": 1.5, "duration": 0.25, "velocity": 85},
        {"pitch": 42, "start_time": 2.0, "duration": 0.25, "velocity": 70},
        {"pitch": 42, "start_time": 2.5, "duration": 0.25, "velocity": 80},
        {"pitch": 42, "start_time": 3.0, "duration": 0.25, "velocity": 70},
        {"pitch": 42, "start_time": 3.5, "duration": 0.25, "velocity": 85},
        {"pitch": 42, "start_time": 4.5, "duration": 0.25, "velocity": 80},
        {"pitch": 42, "start_time": 5.0, "duration": 0.25, "velocity": 70},
        {"pitch": 42, "start_time": 5.5, "duration": 0.25, "velocity": 85},
        {"pitch": 42, "start_time": 6.0, "duration": 0.25, "velocity": 70},
        {"pitch": 42, "start_time": 6.5, "duration": 0.25, "velocity": 80},
        {"pitch": 42, "start_time": 7.0, "duration": 0.25, "velocity": 70},
        {"pitch": 42, "start_time": 7.5, "duration": 0.25, "velocity": 90},
        {"pitch": 42, "start_time": 8.5, "duration": 0.25, "velocity": 80},
        {"pitch": 42, "start_time": 9.0, "duration": 0.25, "velocity": 70},
        {"pitch": 42, "start_time": 9.5, "duration": 0.25, "velocity": 85},
        {"pitch": 42, "start_time": 10.0, "duration": 0.25, "velocity": 70},
        {"pitch": 42, "start_time": 10.5, "duration": 0.25, "velocity": 80},
        {"pitch": 42, "start_time": 11.0, "duration": 0.25, "velocity": 70},
        {"pitch": 42, "start_time": 11.5, "duration": 0.25, "velocity": 85},
        {"pitch": 42, "start_time": 12.5, "duration": 0.25, "velocity": 80},
        {"pitch": 42, "start_time": 13.0, "duration": 0.25, "velocity": 70},
        {"pitch": 42, "start_time": 13.5, "duration": 0.25, "velocity": 85},
        {"pitch": 42, "start_time": 14.0, "duration": 0.25, "velocity": 70},
        {"pitch": 42, "start_time": 14.5, "duration": 0.25, "velocity": 80},
        {"pitch": 42, "start_time": 15.0, "duration": 0.25, "velocity": 70},
        {"pitch": 42, "start_time": 15.5, "duration": 0.25, "velocity": 95},

        {"pitch": 46, "start_time": 2, "duration": 0.5, "velocity": 90},
        {"pitch": 46, "start_time": 6, "duration": 0.5, "velocity": 90},
        {"pitch": 46, "start_time": 10, "duration": 0.5, "velocity": 90},
        {"pitch": 46, "start_time": 14, "duration": 0.5, "velocity": 90},

        {"pitch": 38, "start_time": 1, "duration": 0.25, "velocity": 100},
        {"pitch": 38, "start_time": 3, "duration": 0.25, "velocity": 95},
        {"pitch": 38, "start_time": 5, "duration": 0.25, "velocity": 100},
        {"pitch": 38, "start_time": 7, "duration": 0.25, "velocity": 95},
        {"pitch": 38, "start_time": 9, "duration": 0.25, "velocity": 100},
        {"pitch": 38, "start_time": 11, "duration": 0.25, "velocity": 95},
        {"pitch": 38, "start_time": 13, "duration": 0.25, "velocity": 100},
        {"pitch": 38, "start_time": 15, "duration": 0.25, "velocity": 110}
      ]
    }
  }'

# Humanize timing slightly for groove
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "humanize_clip_timing", "params": {"track_index": 0, "clip_index": 0, "amount": 0.02}}'
```

### Step 5: Create Hypnotic Bass Line

```bash
# Create 4-bar bass clip
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "create_clip", "params": {"track_index": 1, "clip_index": 0, "length": 16}}'

curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "set_clip_name", "params": {"track_index": 1, "clip_index": 0, "name": "Hypnotic Bass"}}'

# Hypnotic A minor bass pattern (A1 = 33, E1 = 28, G1 = 31)
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{
    "command": "add_notes_to_clip",
    "params": {
      "track_index": 1,
      "clip_index": 0,
      "notes": [
        {"pitch": 33, "start_time": 0, "duration": 0.75, "velocity": 110},
        {"pitch": 33, "start_time": 1, "duration": 0.25, "velocity": 90},
        {"pitch": 33, "start_time": 1.5, "duration": 0.25, "velocity": 100},
        {"pitch": 33, "start_time": 2, "duration": 0.75, "velocity": 110},
        {"pitch": 33, "start_time": 3, "duration": 0.25, "velocity": 85},
        {"pitch": 33, "start_time": 3.5, "duration": 0.5, "velocity": 95},

        {"pitch": 33, "start_time": 4, "duration": 0.75, "velocity": 110},
        {"pitch": 33, "start_time": 5, "duration": 0.25, "velocity": 90},
        {"pitch": 33, "start_time": 5.5, "duration": 0.25, "velocity": 100},
        {"pitch": 31, "start_time": 6, "duration": 0.75, "velocity": 105},
        {"pitch": 31, "start_time": 7, "duration": 0.25, "velocity": 85},
        {"pitch": 28, "start_time": 7.5, "duration": 0.5, "velocity": 100},

        {"pitch": 33, "start_time": 8, "duration": 0.75, "velocity": 110},
        {"pitch": 33, "start_time": 9, "duration": 0.25, "velocity": 90},
        {"pitch": 33, "start_time": 9.5, "duration": 0.25, "velocity": 100},
        {"pitch": 33, "start_time": 10, "duration": 0.75, "velocity": 110},
        {"pitch": 33, "start_time": 11, "duration": 0.25, "velocity": 85},
        {"pitch": 33, "start_time": 11.5, "duration": 0.5, "velocity": 95},

        {"pitch": 33, "start_time": 12, "duration": 0.75, "velocity": 110},
        {"pitch": 33, "start_time": 13, "duration": 0.25, "velocity": 90},
        {"pitch": 33, "start_time": 13.5, "duration": 0.25, "velocity": 100},
        {"pitch": 28, "start_time": 14, "duration": 0.5, "velocity": 105},
        {"pitch": 31, "start_time": 14.5, "duration": 0.25, "velocity": 95},
        {"pitch": 33, "start_time": 15, "duration": 0.25, "velocity": 90},
        {"pitch": 36, "start_time": 15.5, "duration": 0.5, "velocity": 100}
      ]
    }
  }'
```

### Step 6: Create Synth Arp/Lead

```bash
# Create synth clip
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "create_clip", "params": {"track_index": 2, "clip_index": 0, "length": 16}}'

curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "set_clip_name", "params": {"track_index": 2, "clip_index": 0, "name": "Acid Lead"}}'

# Hypnotic arp pattern in A minor (A3=57, C4=60, D4=62, E4=64, G4=67)
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{
    "command": "add_notes_to_clip",
    "params": {
      "track_index": 2,
      "clip_index": 0,
      "notes": [
        {"pitch": 57, "start_time": 0, "duration": 0.25, "velocity": 100},
        {"pitch": 60, "start_time": 0.25, "duration": 0.25, "velocity": 80},
        {"pitch": 64, "start_time": 0.5, "duration": 0.25, "velocity": 90},
        {"pitch": 67, "start_time": 0.75, "duration": 0.25, "velocity": 85},
        {"pitch": 64, "start_time": 1, "duration": 0.25, "velocity": 95},
        {"pitch": 60, "start_time": 1.25, "duration": 0.25, "velocity": 80},
        {"pitch": 57, "start_time": 1.5, "duration": 0.25, "velocity": 100},
        {"pitch": 60, "start_time": 1.75, "duration": 0.25, "velocity": 85},

        {"pitch": 57, "start_time": 2, "duration": 0.25, "velocity": 100},
        {"pitch": 62, "start_time": 2.25, "duration": 0.25, "velocity": 80},
        {"pitch": 64, "start_time": 2.5, "duration": 0.25, "velocity": 90},
        {"pitch": 67, "start_time": 2.75, "duration": 0.25, "velocity": 85},
        {"pitch": 69, "start_time": 3, "duration": 0.25, "velocity": 95},
        {"pitch": 67, "start_time": 3.25, "duration": 0.25, "velocity": 80},
        {"pitch": 64, "start_time": 3.5, "duration": 0.25, "velocity": 90},
        {"pitch": 60, "start_time": 3.75, "duration": 0.25, "velocity": 85},

        {"pitch": 57, "start_time": 4, "duration": 0.25, "velocity": 100},
        {"pitch": 60, "start_time": 4.25, "duration": 0.25, "velocity": 80},
        {"pitch": 64, "start_time": 4.5, "duration": 0.25, "velocity": 90},
        {"pitch": 67, "start_time": 4.75, "duration": 0.25, "velocity": 85},
        {"pitch": 64, "start_time": 5, "duration": 0.25, "velocity": 95},
        {"pitch": 60, "start_time": 5.25, "duration": 0.25, "velocity": 80},
        {"pitch": 57, "start_time": 5.5, "duration": 0.25, "velocity": 100},
        {"pitch": 55, "start_time": 5.75, "duration": 0.25, "velocity": 85},

        {"pitch": 52, "start_time": 6, "duration": 0.5, "velocity": 105},
        {"pitch": 55, "start_time": 6.5, "duration": 0.25, "velocity": 90},
        {"pitch": 57, "start_time": 6.75, "duration": 0.25, "velocity": 85},
        {"pitch": 60, "start_time": 7, "duration": 0.5, "velocity": 100},
        {"pitch": 57, "start_time": 7.5, "duration": 0.5, "velocity": 90},

        {"pitch": 57, "start_time": 8, "duration": 0.25, "velocity": 100},
        {"pitch": 60, "start_time": 8.25, "duration": 0.25, "velocity": 80},
        {"pitch": 64, "start_time": 8.5, "duration": 0.25, "velocity": 90},
        {"pitch": 67, "start_time": 8.75, "duration": 0.25, "velocity": 85},
        {"pitch": 64, "start_time": 9, "duration": 0.25, "velocity": 95},
        {"pitch": 60, "start_time": 9.25, "duration": 0.25, "velocity": 80},
        {"pitch": 57, "start_time": 9.5, "duration": 0.25, "velocity": 100},
        {"pitch": 60, "start_time": 9.75, "duration": 0.25, "velocity": 85},

        {"pitch": 57, "start_time": 10, "duration": 0.25, "velocity": 100},
        {"pitch": 62, "start_time": 10.25, "duration": 0.25, "velocity": 80},
        {"pitch": 64, "start_time": 10.5, "duration": 0.25, "velocity": 90},
        {"pitch": 67, "start_time": 10.75, "duration": 0.25, "velocity": 85},
        {"pitch": 69, "start_time": 11, "duration": 0.25, "velocity": 95},
        {"pitch": 67, "start_time": 11.25, "duration": 0.25, "velocity": 80},
        {"pitch": 64, "start_time": 11.5, "duration": 0.25, "velocity": 90},
        {"pitch": 60, "start_time": 11.75, "duration": 0.25, "velocity": 85},

        {"pitch": 57, "start_time": 12, "duration": 0.25, "velocity": 100},
        {"pitch": 60, "start_time": 12.25, "duration": 0.25, "velocity": 80},
        {"pitch": 64, "start_time": 12.5, "duration": 0.25, "velocity": 90},
        {"pitch": 67, "start_time": 12.75, "duration": 0.25, "velocity": 85},
        {"pitch": 72, "start_time": 13, "duration": 0.5, "velocity": 105},
        {"pitch": 69, "start_time": 13.5, "duration": 0.5, "velocity": 95},

        {"pitch": 67, "start_time": 14, "duration": 0.25, "velocity": 100},
        {"pitch": 64, "start_time": 14.25, "duration": 0.25, "velocity": 90},
        {"pitch": 60, "start_time": 14.5, "duration": 0.25, "velocity": 85},
        {"pitch": 57, "start_time": 14.75, "duration": 0.25, "velocity": 80},
        {"pitch": 55, "start_time": 15, "duration": 0.5, "velocity": 95},
        {"pitch": 57, "start_time": 15.5, "duration": 0.5, "velocity": 100}
      ]
    }
  }'

# Slight humanization for organic feel
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "humanize_clip_timing", "params": {"track_index": 2, "clip_index": 0, "amount": 0.015}}'

curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "humanize_clip_velocity", "params": {"track_index": 2, "clip_index": 0, "amount": 0.1}}'
```

### Step 7: Create Atmospheric Pad

```bash
# Create pad clip
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "create_clip", "params": {"track_index": 3, "clip_index": 0, "length": 16}}'

curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "set_clip_name", "params": {"track_index": 3, "clip_index": 0, "name": "Dark Pad"}}'

# Ambient pad chords (Am - G - F - Em progression, each 4 beats)
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{
    "command": "add_notes_to_clip",
    "params": {
      "track_index": 3,
      "clip_index": 0,
      "notes": [
        {"pitch": 57, "start_time": 0, "duration": 4, "velocity": 70},
        {"pitch": 60, "start_time": 0, "duration": 4, "velocity": 65},
        {"pitch": 64, "start_time": 0, "duration": 4, "velocity": 60},

        {"pitch": 55, "start_time": 4, "duration": 4, "velocity": 70},
        {"pitch": 59, "start_time": 4, "duration": 4, "velocity": 65},
        {"pitch": 62, "start_time": 4, "duration": 4, "velocity": 60},

        {"pitch": 53, "start_time": 8, "duration": 4, "velocity": 70},
        {"pitch": 57, "start_time": 8, "duration": 4, "velocity": 65},
        {"pitch": 60, "start_time": 8, "duration": 4, "velocity": 60},

        {"pitch": 52, "start_time": 12, "duration": 4, "velocity": 70},
        {"pitch": 55, "start_time": 12, "duration": 4, "velocity": 65},
        {"pitch": 59, "start_time": 12, "duration": 4, "velocity": 60}
      ]
    }
  }'
```

### Step 8: Create Scenes for Arrangement

```bash
# Create scenes for different song sections
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "set_scene_name", "params": {"scene_index": 0, "name": "Intro - Drums Only"}}'
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "create_scene", "params": {"index": 1}}'
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "set_scene_name", "params": {"scene_index": 1, "name": "Build - Add Bass"}}'
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "create_scene", "params": {"index": 2}}'
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "set_scene_name", "params": {"scene_index": 2, "name": "Main - Full"}}'
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "create_scene", "params": {"index": 3}}'
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "set_scene_name", "params": {"scene_index": 3, "name": "Break - Pad Only"}}'
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "create_scene", "params": {"index": 4}}'
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "set_scene_name", "params": {"scene_index": 4, "name": "Drop - Full Power"}}'
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "create_scene", "params": {"index": 5}}'
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "set_scene_name", "params": {"scene_index": 5, "name": "Outro - Drums Fade"}}'

# Duplicate clips to other scenes
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "duplicate_clip", "params": {"track_index": 0, "clip_index": 0}}'
# (Repeat for other tracks/scenes as needed)
```

### Step 9: Setup Return Tracks (Reverb & Delay)

```bash
# Create return tracks
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "create_return_track"}'
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "create_return_track"}'

# Load reverb on return A
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "load_browser_item_to_return", "params": {"return_index": 0, "item_uri": "query:Reverb"}}'

# Load delay on return B
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "load_browser_item_to_return", "params": {"return_index": 1, "item_uri": "query:Delay"}}'
```

### Step 10: Mixing - Set Levels & Sends

```bash
# Set track volumes (rough mix)
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "set_track_volume", "params": {"track_index": 0, "volume": 0.85}}'  # Drums
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "set_track_volume", "params": {"track_index": 1, "volume": 0.75}}'  # Bass
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "set_track_volume", "params": {"track_index": 2, "volume": 0.65}}'  # Lead
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "set_track_volume", "params": {"track_index": 3, "volume": 0.50}}'  # Pad

# Set panning (slight stereo spread)
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "set_track_pan", "params": {"track_index": 0, "pan": 0}}'      # Drums center
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "set_track_pan", "params": {"track_index": 1, "pan": 0}}'      # Bass center
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "set_track_pan", "params": {"track_index": 2, "pan": -0.15}}'  # Lead slight left
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "set_track_pan", "params": {"track_index": 3, "pan": 0.1}}'    # Pad slight right

# Send levels to reverb (return A)
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "set_send_level", "params": {"track_index": 0, "send_index": 0, "level": 0.15}}'  # Drums - little reverb
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "set_send_level", "params": {"track_index": 1, "send_index": 0, "level": 0.10}}'  # Bass - minimal
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "set_send_level", "params": {"track_index": 2, "send_index": 0, "level": 0.35}}'  # Lead - more
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "set_send_level", "params": {"track_index": 3, "send_index": 0, "level": 0.50}}'  # Pad - lots

# Send levels to delay (return B)
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "set_send_level", "params": {"track_index": 0, "send_index": 1, "level": 0.10}}'  # Drums
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "set_send_level", "params": {"track_index": 2, "send_index": 1, "level": 0.25}}'  # Lead
```

### Step 11: Add Effects to Tracks

```bash
# Add EQ Eight to drums for low-end punch
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "load_instrument_or_effect", "params": {"track_index": 0, "uri": "query:EQ Eight"}}'

# Add Saturator to bass for warmth
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "load_instrument_or_effect", "params": {"track_index": 1, "uri": "query:Saturator"}}'

# Add Auto Filter to lead for movement
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "load_instrument_or_effect", "params": {"track_index": 2, "uri": "query:Auto Filter"}}'

# Add Compressor to pad
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "load_instrument_or_effect", "params": {"track_index": 3, "uri": "query:Compressor"}}'
```

### Step 12: Master Chain

```bash
# Add mastering chain to master (track index -1 or use master commands)
# First, let's add effects to a dedicated master bus or use master track

# Get master info
curl http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "get_master_info"}'

# Set master volume slightly below 0dB
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "set_master_volume", "params": {"volume": 0.9}}'
```

### Step 13: Arrangement Tips

Use these commands to build your arrangement:

```bash
# Set up arrangement loop for working on a section
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "set_arrangement_loop", "params": {"start": 0, "end": 64, "enabled": true}}'

# Create locators for song sections
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "create_locator", "params": {"time": 0, "name": "Intro"}}'
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "create_locator", "params": {"time": 32, "name": "Build"}}'
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "create_locator", "params": {"time": 64, "name": "Drop 1"}}'
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "create_locator", "params": {"time": 128, "name": "Break"}}'
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "create_locator", "params": {"time": 160, "name": "Drop 2"}}'
curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d '{"command": "create_locator", "params": {"time": 224, "name": "Outro"}}'
```

### Step 14: Final Polish

```bash
# Set global swing for groove
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "set_swing_amount", "params": {"amount": 0.1}}'

# Fire scene to preview
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "fire_scene", "params": {"scene_index": 2}}'

# Start playback
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "start_playback"}'
```

### Typical Techno Arrangement Structure

| Section | Bars | What's Playing |
|---------|------|----------------|
| Intro | 1-16 | Kick only, hi-hats fade in |
| Build 1 | 17-32 | Add bass, filter opening |
| Main 1 | 33-64 | Full beat + bass + lead |
| Break | 65-80 | Drop kick, pad + FX |
| Build 2 | 81-96 | Kick returns, filter riser |
| Drop | 97-160 | Full power, all elements |
| Breakdown | 161-176 | Strip back, tension |
| Main 2 | 177-224 | Full arrangement |
| Outro | 225-256 | Elements drop out |

### Pro Tips for Hypnotic Techno

1. **Keep it minimal** - Less is more. One good synth line > 5 weak ones
2. **Repetition is key** - Hypnotic = repetitive. Let patterns loop
3. **Subtle variations** - Small filter movements, velocity changes
4. **Strong kick** - The kick is the foundation. EQ it properly
5. **Leave headroom** - Mix at -6dB, leave room for mastering
6. **Sidechain the bass** - Duck bass on kick hits
7. **Automate everything** - Filter sweeps, reverb sends, etc.

---

## Full Command List

Total: **200+ commands**

Run this to see all available commands:
```bash
curl http://localhost:8000/api/commands
```
