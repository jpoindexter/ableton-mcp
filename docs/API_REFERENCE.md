# AbletonMCP REST API Reference

Complete reference for the AbletonMCP REST API.

## Base URL

```
http://localhost:8000/api
```

## Authentication

Authentication is optional. Set the `REST_API_KEY` environment variable to enable API key authentication.

```bash
export REST_API_KEY="your-secret-key"
```

When enabled, include the key in requests:
```
X-API-Key: your-secret-key
```

## Rate Limiting

Default: 100 requests per minute per IP address.

Configure via environment variables:
- `RATE_LIMIT_ENABLED`: "true" or "false" (default: "true")
- `RATE_LIMIT_REQUESTS`: Number of requests (default: 100)
- `RATE_LIMIT_WINDOW`: Time window in seconds (default: 60)

---

## Parameter Constraints

All parameters are validated against the following bounds:

| Constraint | Value | Description |
|------------|-------|-------------|
| `MAX_TRACK_INDEX` | 999 | Maximum track index (Ableton supports up to 1000 tracks) |
| `MAX_CLIP_INDEX` | 999 | Maximum clip slot index per track |
| `MAX_SCENE_INDEX` | 999 | Maximum scene index |
| `MAX_DEVICE_INDEX` | 127 | Maximum device index per track |
| `MAX_PARAMETER_INDEX` | 255 | Maximum parameter index per device |
| `MAX_SEND_INDEX` | 11 | Maximum send index (return tracks A-L) |
| Tempo | 20-300 BPM | Valid tempo range |
| Volume | 0.0-1.0 | Track/return volume (0.85 is Ableton's default) |
| Pan | -1.0 to 1.0 | Pan position (-1.0 = left, 0.0 = center, 1.0 = right) |
| Pitch shift | -48 to +48 | Audio clip pitch shift in semitones |
| MIDI pitch | 0-127 | MIDI note number (60 = middle C) |
| Velocity | 0-127 | MIDI velocity |
| Color | 0-69 | Ableton color palette index |

---

## Error Codes

All errors return JSON with this format:

```json
{"error": "Error message here"}
```

### HTTP Status Codes

| Status | Description | Example Scenarios |
|--------|-------------|-------------------|
| `200` | Success | Request completed successfully |
| `400` | Bad Request | Invalid command name, command too large (>1MB), invalid Ableton operation |
| `401` | Unauthorized | API key required but not provided in `X-API-Key` header |
| `403` | Forbidden | Invalid API key provided |
| `422` | Validation Error | Parameter out of bounds, invalid data type, missing required field |
| `429` | Too Many Requests | Rate limit exceeded (default: 100 requests/minute) |
| `500` | Internal Server Error | Unexpected server error, invalid JSON response from Ableton, command failed after retries |
| `503` | Service Unavailable | Ableton Live not connected, Remote Script not running |

### Error Examples

**400 - Invalid Command:**
```json
{"error": "Unknown command: invalid_command. Use /api/commands to see available commands."}
```

**401 - Missing API Key:**
```json
{"error": "API key required. Set X-API-Key header."}
```

**403 - Invalid API Key:**
```json
{"error": "Invalid API key"}
```

**422 - Validation Error (tempo out of range):**
```json
{"error": [{"loc": ["body", "tempo"], "msg": "Tempo must be between 20 and 300 BPM", "type": "value_error"}]}
```

**422 - Validation Error (track index out of bounds):**
```json
{"error": [{"loc": ["path", "track_index"], "msg": "ensure this value is less than or equal to 999", "type": "value_error.number.not_le"}]}
```

**429 - Rate Limit Exceeded:**
```json
{"error": "Rate limit exceeded", "detail": "Maximum 100 requests per 60 seconds"}
```

**503 - Ableton Not Connected:**
```json
{"error": "Could not connect to Ableton at localhost:9877. Make sure Live is running with the AbletonMCP control surface enabled."}
```

---

## Transport

### GET /health
Health check endpoint.

**Response:**
```json
{"status": "ok", "connected": true}
```

### GET /session
Get current session information.

**Response:**
```json
{
  "tempo": 120.0,
  "signature_numerator": 4,
  "signature_denominator": 4,
  "is_playing": false,
  "track_count": 8,
  "scene_count": 8
}
```

### PUT /tempo
Set the session tempo.

**Request:**
```json
{"tempo": 128.0}
```

**Validation:** Tempo must be between 20 and 300 BPM.

### POST /transport/play
Start playback.

### POST /transport/stop
Stop playback.

### GET /transport/position
Get current playback position.

**Response:**
```json
{
  "current_time": 16.5,
  "current_bar": 5,
  "current_beat": 1,
  "is_playing": true
}
```

### POST /undo
Undo last action.

### POST /redo
Redo last undone action.

### GET /metronome
Get metronome state.

**Response:**
```json
{"enabled": true}
```

### POST /metronome
Set metronome state.

**Request:**
```json
{"enabled": true}
```

---

## Tracks

### GET /tracks/{track_index}
Get detailed track information.

**Response:**
```json
{
  "index": 0,
  "name": "Track 1",
  "is_midi_track": true,
  "mute": false,
  "solo": false,
  "arm": false,
  "volume": 0.85,
  "panning": 0.0,
  "clip_slots": [...],
  "devices": [...]
}
```

### POST /tracks/midi
Create a new MIDI track.

**Request:**
```json
{"index": -1, "name": "My Track"}
```

`index`: Position to insert (-1 = end of list)

### POST /tracks/audio
Create a new audio track.

**Request:**
```json
{"index": -1, "name": "My Audio Track"}
```

### DELETE /tracks/{track_index}
Delete a track.

### POST /tracks/{track_index}/duplicate
Duplicate a track.

### POST /tracks/{track_index}/freeze
Freeze track (render devices to audio for CPU optimization).

**Note:** Freezing renders all devices on a track to audio, reducing CPU load. The track cannot be edited while frozen.

### POST /tracks/{track_index}/flatten
Flatten frozen track to permanent audio.

**Note:** The track must be frozen first. Flattening converts the freeze to a permanent audio file and removes the original devices.

### PUT /tracks/{track_index}/name
Set track name.

**Request:**
```json
{"name": "New Name"}
```

### GET /tracks/{track_index}/color
Get track color index.

**Response:**
```json
{"color_index": 15}
```

### PUT /tracks/{track_index}/color
Set track color.

**Request:**
```json
{"color": 15}
```

Color indices range from 0-69 (Ableton color palette).

### PUT /tracks/{track_index}/mute
Set track mute state.

**Request:**
```json
{"value": true}
```

### PUT /tracks/{track_index}/solo
Set track solo state.

**Request:**
```json
{"value": true}
```

### PUT /tracks/{track_index}/arm
Set track arm state.

**Request:**
```json
{"value": true}
```

### PUT /tracks/{track_index}/volume
Set track volume.

**Request:**
```json
{"volume": 0.85}
```

**Validation:** Volume must be between 0.0 and 1.0.

### PUT /tracks/{track_index}/pan
Set track panning.

**Request:**
```json
{"pan": 0.0}
```

**Validation:** Pan must be between -1.0 (left) and 1.0 (right).

### POST /tracks/{track_index}/select
Select track for editing.

### GET /tracks/{track_index}/monitoring
Get track monitoring state.

**Response:**
```json
{"monitoring": "in"}
```

Monitoring values: `"in"` (always monitor input), `"auto"` (monitor when armed), `"off"` (never monitor input)

### PUT /tracks/{track_index}/monitoring
Set track monitoring state.

**Request:**
```json
{"state": "auto"}
```

**Valid values:** `"in"`, `"auto"`, `"off"`

### POST /tracks/group
Group selected tracks.

**Request:**
```json
{"track_indices": [0, 1, 2]}
```

Creates a group track containing the specified tracks.

### POST /tracks/{track_index}/fold
Fold a group track (collapse its children).

### POST /tracks/{track_index}/unfold
Unfold a group track (expand its children).

---

## Clips

### GET /tracks/{track_index}/clips/{clip_index}
Get clip information.

**Response:**
```json
{
  "name": "Clip 1",
  "length": 4.0,
  "is_midi_clip": true,
  "looping": true,
  "loop_start": 0.0,
  "loop_end": 4.0
}
```

### POST /tracks/{track_index}/clips/{clip_index}
Create a new clip.

**Request:**
```json
{"length": 4.0, "name": "New Clip"}
```

### DELETE /tracks/{track_index}/clips/{clip_index}
Delete a clip.

### POST /tracks/{track_index}/clips/{clip_index}/fire
Launch/fire a clip.

### POST /tracks/{track_index}/clips/{clip_index}/stop
Stop a clip.

### POST /tracks/{track_index}/clips/{clip_index}/duplicate
Duplicate a clip.

**Request:**
```json
{"target_index": 1}
```

### PUT /tracks/{track_index}/clips/{clip_index}/name
Set clip name.

**Request:**
```json
{"name": "New Clip Name"}
```

### GET /tracks/{track_index}/clips/{clip_index}/color
Get clip color.

**Response:**
```json
{"color_index": 10}
```

### PUT /tracks/{track_index}/clips/{clip_index}/color
Set clip color.

**Request:**
```json
{"color": 10}
```

### GET /tracks/{track_index}/clips/{clip_index}/loop
Get clip loop settings.

**Response:**
```json
{
  "loop_start": 0.0,
  "loop_end": 4.0,
  "looping": true
}
```

### PUT /tracks/{track_index}/clips/{clip_index}/loop
Set clip loop settings.

**Request:**
```json
{
  "loop_start": 0.0,
  "loop_end": 4.0,
  "looping": true
}
```

### POST /tracks/{track_index}/clips/{clip_index}/select
Select clip for editing.

---

## Notes (MIDI)

### GET /tracks/{track_index}/clips/{clip_index}/notes
Get all notes in a MIDI clip.

**Response:**
```json
{
  "notes": [
    {"pitch": 60, "start_time": 0.0, "duration": 0.5, "velocity": 100, "mute": false},
    {"pitch": 64, "start_time": 0.5, "duration": 0.5, "velocity": 100, "mute": false}
  ],
  "count": 2
}
```

### POST /tracks/{track_index}/clips/{clip_index}/notes
Add notes to a MIDI clip.

**Request:**
```json
{
  "notes": [
    {"pitch": 60, "start_time": 0.0, "duration": 0.5, "velocity": 100},
    {"pitch": 64, "start_time": 0.5, "duration": 0.5, "velocity": 100}
  ]
}
```

**Validation:**
- pitch: 0-127
- velocity: 0-127
- start_time: >= 0
- duration: > 0

### DELETE /tracks/{track_index}/clips/{clip_index}/notes
Remove all notes from a clip.

### POST /tracks/{track_index}/clips/{clip_index}/transpose
Transpose notes in a clip.

**Request:**
```json
{"semitones": 12}
```

---

## Audio Clip Properties

### GET /tracks/{track_index}/clips/{clip_index}/gain
Get audio clip gain.

**Response:**
```json
{"gain_db": 0.0, "gain_linear": 1.0}
```

### PUT /tracks/{track_index}/clips/{clip_index}/gain
Set audio clip gain.

**Request:**
```json
{"gain": -6.0}
```

**Note:** Gain is specified in decibels (dB). Negative values reduce volume, positive values boost.

### GET /tracks/{track_index}/clips/{clip_index}/pitch
Get audio clip pitch.

**Response:**
```json
{"pitch_coarse": 0, "pitch_fine": 0}
```

### PUT /tracks/{track_index}/clips/{clip_index}/pitch
Set audio clip pitch.

**Request:**
```json
{"pitch": 12}
```

**Validation:** Pitch must be between -48 and +48 semitones.

---

## Warp Settings (Audio Clips)

### GET /tracks/{track_index}/clips/{clip_index}/warp
Get audio clip warp settings.

**Response:**
```json
{
  "warping": true,
  "warp_mode": "beats",
  "start_marker": 0.0,
  "end_marker": 176400.0,
  "loop_start": 0.0,
  "loop_end": 4.0
}
```

### PUT /tracks/{track_index}/clips/{clip_index}/warp
Set audio clip warp settings.

**Request:**
```json
{
  "warping": true,
  "warp_mode": "complex_pro"
}
```

**Valid warp modes:** `"beats"`, `"tones"`, `"texture"`, `"repitch"`, `"complex"`, `"complex_pro"`

---

## Warp Markers (Audio Clips)

### GET /tracks/{track_index}/clips/{clip_index}/warp-markers
Get all warp markers.

**Response:**
```json
{
  "warp_markers": [
    {"index": 0, "beat_time": 0.0, "sample_time": 0.0},
    {"index": 1, "beat_time": 1.0, "sample_time": 44100.0}
  ],
  "count": 2
}
```

### POST /tracks/{track_index}/clips/{clip_index}/warp-markers
Add a warp marker.

**Request:**
```json
{"beat_time": 2.0, "sample_time": 88200.0}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `beat_time` | float | Yes | Position in beats where the marker should be placed |
| `sample_time` | float | No | Sample position the marker should map to (if omitted, calculated automatically) |

### DELETE /tracks/{track_index}/clips/{clip_index}/warp-markers
Delete a warp marker.

**Request:**
```json
{"beat_time": 2.0}
```

---

## Clip Automation

### GET /tracks/{track_index}/clips/{clip_index}/automation/{parameter_name}
Get automation envelope data for a parameter.

**Response:**
```json
{
  "parameter": "Volume",
  "automation_enabled": true,
  "points": [
    {"time": 0.0, "value": 0.85},
    {"time": 2.0, "value": 0.5},
    {"time": 4.0, "value": 0.85}
  ]
}
```

### PUT /tracks/{track_index}/clips/{clip_index}/automation/{parameter_name}
Set automation envelope for a parameter.

**Request:**
```json
{
  "points": [
    {"time": 0.0, "value": 0.85},
    {"time": 2.0, "value": 0.5},
    {"time": 4.0, "value": 0.85}
  ]
}
```

### DELETE /tracks/{track_index}/clips/{clip_index}/automation/{parameter_name}
Clear automation for a parameter.

---

## Scenes

### GET /scenes
Get all scenes.

**Response:**
```json
{
  "scenes": [
    {"index": 0, "name": "Scene 1", "tempo": null, "color_index": 0},
    {"index": 1, "name": "Scene 2", "tempo": 128.0, "color_index": 5}
  ],
  "count": 2
}
```

### POST /scenes
Create a new scene.

**Request:**
```json
{"index": -1, "name": "New Scene"}
```

### DELETE /scenes/{scene_index}
Delete a scene.

### POST /scenes/{scene_index}/fire
Launch a scene.

### POST /scenes/{scene_index}/stop
Stop a scene.

### POST /scenes/{scene_index}/duplicate
Duplicate a scene.

### PUT /scenes/{scene_index}/name
Set scene name.

**Request:**
```json
{"name": "Verse"}
```

### GET /scenes/{scene_index}/color
Get scene color.

**Response:**
```json
{"color_index": 5}
```

### PUT /scenes/{scene_index}/color
Set scene color.

**Request:**
```json
{"color": 5}
```

### POST /scenes/{scene_index}/select
Select scene.

---

## Devices

### GET /tracks/{track_index}/devices/{device_index}
Get device parameters.

**Response:**
```json
{
  "name": "EQ Eight",
  "class_name": "PluginDevice",
  "is_active": true,
  "parameters": [
    {"index": 0, "name": "Device On", "value": 1.0, "min": 0.0, "max": 1.0},
    {"index": 1, "name": "Band 1 Gain", "value": 0.0, "min": -15.0, "max": 15.0}
  ]
}
```

### PUT /tracks/{track_index}/devices/{device_index}/parameter
Set a device parameter.

**Request:**
```json
{"parameter_index": 0, "value": 0.5}
```

### PUT /tracks/{track_index}/devices/{device_index}/toggle
Toggle device on/off.

**Request:**
```json
{"enabled": true}
```

If `enabled` is omitted, the device state will be toggled.

### DELETE /tracks/{track_index}/devices/{device_index}
Delete a device.

### GET /tracks/{track_index}/devices/by-name/{device_name}
Get device by name.

**Response:**
```json
{
  "index": 2,
  "name": "EQ Eight",
  "class_name": "PluginDevice",
  "is_active": true,
  "parameters": [...]
}
```

Returns 404 if device not found on track.

### GET /tracks/{track_index}/devices/{device_index}/chains
Get chains for a rack device (Drum Rack, Instrument Rack, etc.).

**Response:**
```json
{
  "chains": [
    {"index": 0, "name": "Chain 1", "mute": false, "solo": false},
    {"index": 1, "name": "Chain 2", "mute": false, "solo": false}
  ],
  "count": 2
}
```

### POST /tracks/{track_index}/devices/{device_index}/chains/{chain_index}/select
Select a chain within a rack device.

---

## Return Tracks

### GET /returns
Get all return tracks.

**Response:**
```json
{
  "returns": [
    {"index": 0, "name": "A-Reverb", "volume": 0.85, "panning": 0.0, "mute": false, "solo": false},
    {"index": 1, "name": "B-Delay", "volume": 0.85, "panning": 0.0, "mute": false, "solo": false}
  ],
  "count": 2
}
```

### GET /tracks/{track_index}/sends/{send_index}
Get send level.

**Response:**
```json
{"level": 0.5}
```

### POST /tracks/{track_index}/sends/{send_index}
Set send level.

**Request:**
```json
{"level": 0.5}
```

**Validation:** Level must be between 0.0 and 1.0.

### PUT /returns/{return_index}/volume
Set return track volume.

**Request:**
```json
{"volume": 0.85}
```

### PUT /returns/{return_index}/pan
Set return track pan.

**Request:**
```json
{"pan": 0.0}
```

### GET /returns/{return_index}
Get detailed return track information.

**Response:**
```json
{
  "index": 0,
  "name": "A-Reverb",
  "volume": 0.85,
  "panning": 0.0,
  "mute": false,
  "solo": false,
  "devices": [...]
}
```

---

## Grooves

### GET /grooves
Get available grooves from the groove pool.

**Response:**
```json
{
  "grooves": [
    {"index": 0, "name": "Swing 8", "base": 8, "amount": 0.5},
    {"index": 1, "name": "MPC 60 16ths", "base": 16, "amount": 0.4}
  ],
  "count": 2
}
```

### POST /tracks/{track_index}/clips/{clip_index}/groove
Apply a groove to a clip.

**Request:**
```json
{"groove_index": 0}
```

Applies the groove from the groove pool to the clip's timing.

### POST /tracks/{track_index}/clips/{clip_index}/groove/commit
Commit applied groove to clip notes.

Makes the groove permanent by modifying the actual note positions.

---

## Master Track

### GET /master
Get master track information.

**Response:**
```json
{
  "volume": 0.85,
  "panning": 0.0,
  "devices": [...]
}
```

### POST /master/volume
Set master track volume.

**Request:**
```json
{"volume": 0.85}
```

### POST /master/pan
Set master track pan.

**Request:**
```json
{"pan": 0.0}
```

---

## Browser

### POST /browser/browse
Navigate browser by path list.

**Request:**
```json
{"path": ["Audio Effects", "EQ Eight"]}
```

**Response:**
```json
{
  "items": [
    {"name": "EQ Eight", "is_folder": false, "is_loadable": true, "uri": "query:..."}
  ]
}
```

### POST /browser/search
Search browser for items matching query.

**Request:**
```json
{
  "query": "reverb",
  "category": "audio_effects"
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search query string |
| `category` | string | No | Filter category: `all`, `instruments`, `sounds`, `drums`, `audio_effects`, `midi_effects` (default: `all`) |

**Response:**
```json
{
  "results": [
    {"name": "Reverb", "is_loadable": true, "uri": "query:..."},
    {"name": "Convolution Reverb", "is_loadable": true, "uri": "query:..."}
  ],
  "count": 2
}
```

### POST /browser/children
Get children of a browser item by URI.

**Request:**
```json
{"uri": "query:AudioEffects#"}
```

**Response:**
```json
{
  "children": [
    {"name": "EQ Eight", "is_folder": false, "is_loadable": true, "uri": "query:..."},
    {"name": "Reverb", "is_folder": false, "is_loadable": true, "uri": "query:..."}
  ]
}
```

### POST /browser/load
Load a browser item onto a track.

**Request:**
```json
{
  "track_index": 0,
  "uri": "query:AudioEffects#EQ%20Eight"
}
```

**Response:**
```json
{
  "loaded": true,
  "new_devices": ["EQ Eight"],
  "devices_after": ["EQ Eight", "Reverb"]
}
```

### POST /browser/load-to-return
Load a browser item onto a return track.

**Request:**
```json
{
  "return_index": 0,
  "uri": "query:AudioEffects#Reverb"
}
```

### GET /browser/tree
Get the full browser tree structure.

**Response:**
```json
{
  "tree": {
    "name": "Browser",
    "children": [
      {
        "name": "Sounds",
        "is_folder": true,
        "children": [...]
      },
      {
        "name": "Drums",
        "is_folder": true,
        "children": [...]
      }
    ]
  }
}
```

### GET /browser/items
Get browser items at a specific path.

**Query Parameters:**
- `path` (string, optional): Path to browse (e.g., "Sounds/Bass")

**Response:**
```json
{
  "items": [
    {"name": "Analog Bass", "is_folder": false, "is_loadable": true, "uri": "query:..."},
    {"name": "Electric Bass", "is_folder": false, "is_loadable": true, "uri": "query:..."}
  ],
  "count": 2
}
```

---

## View Control

### GET /view
Get current view state.

**Response:**
```json
{
  "focused_document_view": "Session",
  "selected_track_index": 0,
  "selected_scene_index": 0,
  "detail_clip_track_index": 0,
  "detail_clip_index": 0
}
```

### POST /view/focus
Focus a specific view.

**Query Parameter:** `view_name` - The view to focus

**Valid view names:**
- `Session` - Session view
- `Arranger` - Arrangement view
- `Detail` - Detail view (clip/device)
- `Detail/Clip` - Clip detail view
- `Detail/DeviceChain` - Device chain view

**Example:**
```
POST /api/view/focus?view_name=Session
```

---

## Quantization & Humanization

### POST /tracks/{track_index}/clips/{clip_index}/quantize
Quantize notes in a MIDI clip to a grid.

**Request:**
```json
{
  "grid": 0.25,
  "strength": 1.0
}
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `grid` | float | 0.25 | Grid size in beats (0.25 = 16th notes, 0.5 = 8th notes, 1.0 = quarter notes) |
| `strength` | float | 1.0 | Quantize strength (0.0 = no change, 1.0 = full quantize) |

### POST /tracks/{track_index}/clips/{clip_index}/humanize/timing
Add random timing variation to notes.

**Request:**
```json
{"amount": 0.05}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `amount` | float | Timing variation in beats (0.05 = subtle, 0.1 = moderate, 0.2 = heavy) |

### POST /tracks/{track_index}/clips/{clip_index}/humanize/velocity
Add random velocity variation to notes.

**Request:**
```json
{"amount": 0.1}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `amount` | float | Velocity variation as percentage (0.1 = +/-10%, 0.2 = +/-20%) |

---

## Recording

### POST /recording/start
Start recording.

### POST /recording/stop
Stop recording.

### POST /recording/capture
Capture recently played MIDI (like Ableton's Capture feature).

### POST /recording/overdub
Set overdub mode.

**Request:**
```json
{"enabled": true}
```

### POST /recording/toggle-session
Toggle session record mode.

**Response:**
```json
{"session_record": true}
```

### POST /recording/toggle-arrangement
Toggle arrangement record mode.

**Response:**
```json
{"arrangement_record": true}
```

---

## I/O Routing

### GET /tracks/{track_index}/routing/input
Get track input routing.

**Response:**
```json
{
  "input_routing_type": "Ext. In",
  "input_routing_channel": "1/2"
}
```

### GET /tracks/{track_index}/routing/output
Get track output routing.

**Response:**
```json
{
  "output_routing_type": "Master",
  "output_routing_channel": ""
}
```

### PUT /tracks/{track_index}/routing/input
Set track input routing.

**Query Parameters:**
- `routing_type` (required): Input source type
- `routing_channel` (optional): Specific channel

**Valid `routing_type` values:**
- `Ext. In` - External audio input
- `No Input` - No input
- `Resampling` - Resample from master output
- `[Track Name]` - Input from another track (e.g., "1-Audio", "2-MIDI")
- MIDI tracks: `Computer Keyboard`, `All MIDI Inputs`, specific MIDI device names

**Example:**
```
PUT /api/tracks/0/routing/input?routing_type=Ext.%20In&routing_channel=1/2
```

### PUT /tracks/{track_index}/routing/output
Set track output routing.

**Query Parameters:**
- `routing_type` (required): Output destination type
- `routing_channel` (optional): Specific channel

**Valid `routing_type` values:**
- `Master` - Route to master track
- `Ext. Out` - External audio output
- `Sends Only` - Only send to return tracks
- `[Track Name]` - Route to another track
- `[Return Track Name]` - Route directly to a return track

**Example:**
```
PUT /api/tracks/0/routing/output?routing_type=Master
```

### GET /routing/inputs
Get available audio/MIDI inputs.

**Response:**
```json
{
  "input_types": ["Ext. In", "No Input", "Resampling", "1-Audio", "2-MIDI"],
  "input_channels": {"Ext. In": ["1/2", "3/4", "1", "2", "3", "4"]}
}
```

### GET /routing/outputs
Get available audio/MIDI outputs.

**Response:**
```json
{
  "output_types": ["Master", "Ext. Out", "Sends Only", "A-Reverb", "B-Delay"],
  "output_channels": {"Ext. Out": ["1/2", "3/4"]}
}
```

---

## Session Info

### GET /session/path
Get file path of current session.

**Response:**
```json
{
  "path": "/Users/username/Music/Ableton/Project/Project.als",
  "name": "Project"
}
```

### GET /session/modified
Check if session has unsaved changes.

**Response:**
```json
{"modified": true}
```

### GET /session/cpu
Get current CPU load.

**Response:**
```json
{"cpu_load": 45.2}
```

---

## Arrangement

### GET /arrangement/length
Get arrangement length and loop settings.

**Response:**
```json
{
  "song_length": 256.0,
  "loop_start": 0.0,
  "loop_length": 16.0,
  "loop_on": true
}
```

### POST /arrangement/loop
Set arrangement loop region.

**Query Parameters:**
- `loop_start` (float): Loop start position in beats
- `loop_length` (float): Loop length in beats
- `loop_on` (bool, default: true): Enable/disable looping

### POST /arrangement/jump
Jump to a specific time in the arrangement.

**Query Parameter:** `time` (float) - Position in beats

### GET /arrangement/locators
Get all locators/markers.

**Response:**
```json
{
  "locators": [
    {"index": 0, "name": "Intro", "time": 0.0},
    {"index": 1, "name": "Verse", "time": 16.0}
  ],
  "count": 2
}
```

### POST /arrangement/locators
Create a locator at specified time.

**Query Parameters:**
- `time` (float): Position in beats
- `name` (string, optional): Locator name

### DELETE /arrangement/locators/{index}
Delete a locator by index.

---

## Music Helpers (AI)

### GET /music/scale
Get notes in a musical scale.

**Query Parameters:**
- `root` (string): Root note (e.g., "C", "F#", "Bb")
- `scale_type` (string): Scale type
- `octave` (int, default: 4): Octave number

**Valid scale types:**
- `major`, `minor`, `dorian`, `phrygian`, `lydian`, `mixolydian`, `locrian`
- `harmonic_minor`, `melodic_minor`
- `pentatonic_major`, `pentatonic_minor`
- `blues`, `chromatic`

**Response:**
```json
{
  "root": 60,
  "scale_type": "minor",
  "notes": [60, 62, 63, 65, 67, 68, 70, 72],
  "note_names": ["C4", "D4", "Eb4", "F4", "G4", "Ab4", "Bb4", "C5"]
}
```

### POST /music/drums
Generate a drum pattern.

**Request:**
```json
{
  "track_index": 0,
  "clip_index": 0,
  "style": "house",
  "length": 4.0
}
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `track_index` | int | - | Target track (should have drum rack) |
| `clip_index` | int | - | Target clip slot |
| `style` | string | "basic" | Pattern style: `basic`, `house`, `hiphop`, `dnb`, `random` |
| `length` | float | 4.0 | Pattern length in beats |

### POST /music/bassline
Generate a bassline pattern.

**Request:**
```json
{
  "track_index": 1,
  "clip_index": 0,
  "root": 36,
  "scale_type": "minor",
  "length": 4.0
}
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `track_index` | int | - | Target track |
| `clip_index` | int | - | Target clip slot |
| `root` | int | 36 | Root note MIDI number (36 = C1) |
| `scale_type` | string | "minor" | Scale type: `major`, `minor`, `dorian`, `pentatonic_minor`, `blues` |
| `length` | float | 4.0 | Pattern length in beats |

---

## Generic Command Endpoint

### POST /command
Execute any Ableton command by name. Useful for LLM function calling.

**Request:**
```json
{
  "command": "get_session_info",
  "params": {}
}
```

**Request (with parameters):**
```json
{
  "command": "set_tempo",
  "params": {"tempo": 128.0}
}
```

**Available Commands:**

Use `GET /api/commands` to list all available commands.

```json
{
  "commands": [
    "add_notes_to_clip", "browse_path", "capture_midi", "create_clip",
    "create_locator", "create_midi_track", "create_audio_track", "create_scene",
    "delete_clip", "delete_device", "delete_locator", "delete_scene", "delete_track",
    "duplicate_clip", "duplicate_scene", "duplicate_track", "fire_clip", "fire_scene",
    "flatten_track", "focus_view", "freeze_track", "generate_bassline",
    "generate_drum_pattern", "get_all_scenes", "get_arrangement_length",
    "get_available_inputs", "get_available_outputs", "get_browser_children",
    "get_browser_tree", "get_clip_color", "get_clip_gain", "get_clip_info",
    "get_clip_loop", "get_clip_notes", "get_clip_pitch", "get_cpu_load",
    "get_current_view", "get_device_parameters", "get_locators", "get_master_info",
    "get_metronome_state", "get_playback_position", "get_return_tracks",
    "get_return_track_info", "get_scene_color", "get_send_level", "get_session_info",
    "get_session_path", "get_track_color", "get_track_info", "get_track_input_routing",
    "get_track_output_routing", "get_warp_markers", "health_check",
    "humanize_clip_timing", "humanize_clip_velocity", "is_session_modified",
    "jump_to_time", "load_browser_item", "load_instrument_or_effect",
    "quantize_clip_notes", "redo", "remove_all_notes", "remove_notes",
    "search_browser", "select_clip", "select_scene", "select_track",
    "set_arrangement_loop", "set_clip_color", "set_clip_gain", "set_clip_loop",
    "set_clip_name", "set_clip_pitch", "set_device_parameter", "set_master_pan",
    "set_master_volume", "set_metronome", "set_overdub", "set_return_pan",
    "set_return_volume", "set_scene_color", "set_scene_name", "set_send_level",
    "set_tempo", "set_track_arm", "set_track_color", "set_track_input_routing",
    "set_track_mute", "set_track_name", "set_track_output_routing", "set_track_pan",
    "set_track_solo", "set_track_volume", "start_playback", "start_recording",
    "stop_clip", "stop_playback", "stop_recording", "stop_scene",
    "toggle_arrangement_record", "toggle_device", "toggle_session_record",
    "transpose_notes", "undo"
  ],
  "count": 89
}
```
