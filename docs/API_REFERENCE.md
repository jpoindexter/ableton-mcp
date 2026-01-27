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

### POST /undo
Undo last action.

### POST /redo
Redo last undone action.

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
Freeze track (render devices to audio).

### POST /tracks/{track_index}/flatten
Flatten frozen track to permanent audio.

### PUT /tracks/{track_index}/name
Set track name.

**Request:**
```json
{"name": "New Name"}
```

### GET /tracks/{track_index}/color
Get track color index.

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

### PUT /tracks/{track_index}/arm
Set track arm state.

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

### GET /tracks/{track_index}/clips/{clip_index}/color
Get clip color.

### PUT /tracks/{track_index}/clips/{clip_index}/color
Set clip color.

### GET /tracks/{track_index}/clips/{clip_index}/loop
Get clip loop settings.

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

---

## Notes (MIDI)

### GET /tracks/{track_index}/clips/{clip_index}/notes
Get all notes in a MIDI clip.

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

### DELETE /tracks/{track_index}/clips/{clip_index}/warp-markers
Delete a warp marker.

**Request:**
```json
{"beat_time": 2.0}
```

---

## Audio Clip Properties

### GET /tracks/{track_index}/clips/{clip_index}/gain
Get audio clip gain.

**Response:**
```json
{"gain_db": 0.0, "gain_linear": 1.0}
```

### GET /tracks/{track_index}/clips/{clip_index}/pitch
Get audio clip pitch.

**Response:**
```json
{"pitch_coarse": 0, "pitch_fine": 0}
```

---

## Scenes

### GET /scenes
Get all scenes.

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

### GET /scenes/{scene_index}/color
Get scene color.

### PUT /scenes/{scene_index}/color
Set scene color.

---

## Devices

### GET /tracks/{track_index}/devices/{device_index}
Get device parameters.

### PUT /tracks/{track_index}/devices/{device_index}/parameter
Set a device parameter.

**Request:**
```json
{"parameter_index": 0, "value": 0.5}
```

### POST /tracks/{track_index}/devices/{device_index}/toggle
Toggle device on/off.

### DELETE /tracks/{track_index}/devices/{device_index}
Delete a device.

---

## Return Tracks

### GET /returns
Get all return tracks.

### GET /tracks/{track_index}/sends/{send_index}
Get send level.

### POST /tracks/{track_index}/sends/{send_index}
Set send level.

**Request:**
```json
{"level": 0.5}
```

### PUT /returns/{return_index}/volume
Set return track volume.

---

## Error Responses

All errors return JSON with this format:

```json
{"error": "Error message here"}
```

### Status Codes

- `200`: Success
- `400`: Bad request (invalid command)
- `401`: Unauthorized (API key required)
- `403`: Forbidden (invalid API key)
- `422`: Validation error (invalid parameters)
- `429`: Too many requests (rate limited)
- `500`: Internal server error
- `503`: Service unavailable (Ableton not connected)
