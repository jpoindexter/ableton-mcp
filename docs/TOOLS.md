# AbletonMCP Tool Reference

Complete reference for all 80+ tools available in AbletonMCP.

## Table of Contents

- [Transport & Session](#transport--session)
- [Track Management](#track-management)
- [Clip Operations](#clip-operations)
- [Note Editing](#note-editing)
- [Scene Management](#scene-management)
- [Device Control](#device-control)
- [Return/Send Tracks](#returnsend-tracks)
- [Browser Navigation](#browser-navigation)
- [View Control](#view-control)
- [Recording](#recording)
- [Arrangement View](#arrangement-view)
- [I/O Routing](#io-routing)
- [Performance & Session Info](#performance--session-info)
- [AI Music Helpers](#ai-music-helpers)

---

## Transport & Session

### get_session_info

Get current session state including tempo, time signature, tracks, and scenes.

**Parameters:** None

**Returns:**
```json
{
  "tempo": 120.0,
  "time_signature": [4, 4],
  "is_playing": false,
  "track_count": 8,
  "scene_count": 4,
  "tracks": [
    {"index": 0, "name": "Drums", "type": "midi"},
    {"index": 1, "name": "Bass", "type": "midi"}
  ]
}
```

---

### set_tempo

Set the session tempo in BPM.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| tempo | float | Yes | Tempo in BPM (20-999) |

**Example:**
```json
{"tempo": 128}
```

---

### start_playback

Start playback from the current position.

**Parameters:** None

---

### stop_playback

Stop playback.

**Parameters:** None

---

### undo

Undo the last action.

**Parameters:** None

---

### redo

Redo the last undone action.

**Parameters:** None

---

### get_metronome_state

Get the current metronome on/off state.

**Parameters:** None

**Returns:**
```json
{"enabled": true}
```

---

### set_metronome

Enable or disable the metronome.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| enabled | boolean | Yes | True to enable, false to disable |

---

## Track Management

### get_track_info

Get detailed information about a specific track.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track (0-based) |

**Returns:**
```json
{
  "index": 0,
  "name": "Drums",
  "type": "midi",
  "color": 15,
  "mute": false,
  "solo": false,
  "arm": false,
  "volume": 0.85,
  "pan": 0.0,
  "devices": [
    {"index": 0, "name": "Drum Rack", "type": "instrument"}
  ],
  "clip_slots": 8
}
```

---

### create_midi_track

Create a new MIDI track.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| index | integer | No | Position to insert (-1 for end, default) |
| name | string | No | Name for the new track |

**Example:**
```json
{"index": -1, "name": "Synth Lead"}
```

---

### create_audio_track

Create a new audio track.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| index | integer | No | Position to insert (-1 for end, default) |
| name | string | No | Name for the new track |

---

### delete_track

Delete a track.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track to delete |

---

### duplicate_track

Duplicate a track with all its clips and devices.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track to duplicate |

---

### set_track_name

Set the name of a track.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| name | string | Yes | New name for the track |

---

### set_track_color

Set the color of a track.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| color | integer | Yes | Color index (0-69) |

**Color Reference:** Ableton uses 70 colors indexed 0-69. Common colors:
- 0-13: Reds/Oranges
- 14-27: Yellows/Greens
- 28-41: Cyans/Blues
- 42-55: Purples/Pinks
- 56-69: Grays/Browns

---

### set_track_mute

Mute or unmute a track.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| mute | boolean | Yes | True to mute, false to unmute |

---

### set_track_solo

Solo or unsolo a track.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| solo | boolean | Yes | True to solo, false to unsolo |

---

### set_track_arm

Arm or disarm a track for recording.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| arm | boolean | Yes | True to arm, false to disarm |

---

## Clip Operations

### get_clip_info

Get information about a specific clip.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| clip_index | integer | Yes | Index of the clip slot |

**Returns:**
```json
{
  "name": "Beat 1",
  "color": 5,
  "length": 4.0,
  "is_playing": false,
  "is_recording": false,
  "loop_start": 0.0,
  "loop_end": 4.0,
  "looping": true,
  "note_count": 16
}
```

---

### create_clip

Create a new MIDI clip.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| clip_index | integer | Yes | Index of the clip slot |
| length | float | No | Length in beats (default 4.0) |
| name | string | No | Name for the clip |

**Example:**
```json
{"track_index": 0, "clip_index": 0, "length": 8.0, "name": "Verse"}
```

---

### delete_clip

Delete a clip.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| clip_index | integer | Yes | Index of the clip slot |

---

### duplicate_clip

Duplicate a clip to another slot.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| clip_index | integer | Yes | Index of the source clip |
| target_index | integer | Yes | Index of the target slot |

---

### fire_clip

Trigger a clip to start playing.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| clip_index | integer | Yes | Index of the clip |

---

### stop_clip

Stop a playing clip.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| clip_index | integer | Yes | Index of the clip |

---

### set_clip_name

Set the name of a clip.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| clip_index | integer | Yes | Index of the clip |
| name | string | Yes | New name for the clip |

---

### set_clip_color

Set the color of a clip.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| clip_index | integer | Yes | Index of the clip |
| color | integer | Yes | Color index (0-69) |

---

### set_clip_loop

Configure clip loop settings.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| clip_index | integer | Yes | Index of the clip |
| loop_start | float | No | Loop start in beats |
| loop_end | float | No | Loop end in beats |
| looping | boolean | No | Enable/disable looping |

---

## Note Editing

### get_clip_notes

Get all notes from a clip.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| clip_index | integer | Yes | Index of the clip |

**Returns:**
```json
{
  "notes": [
    {"pitch": 60, "start_time": 0.0, "duration": 0.5, "velocity": 100, "mute": false},
    {"pitch": 64, "start_time": 0.5, "duration": 0.5, "velocity": 90, "mute": false}
  ]
}
```

---

### add_notes_to_clip

Add MIDI notes to a clip.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| clip_index | integer | Yes | Index of the clip |
| notes | array | Yes | Array of note objects |

**Note Object:**
| Property | Type | Required | Description |
|----------|------|----------|-------------|
| pitch | integer | Yes | MIDI pitch (0-127, 60=C4) |
| start_time | float | Yes | Start time in beats |
| duration | float | Yes | Duration in beats |
| velocity | integer | No | Velocity (1-127, default 100) |

**Example:**
```json
{
  "track_index": 0,
  "clip_index": 0,
  "notes": [
    {"pitch": 60, "start_time": 0.0, "duration": 0.5, "velocity": 100},
    {"pitch": 64, "start_time": 0.5, "duration": 0.5, "velocity": 90},
    {"pitch": 67, "start_time": 1.0, "duration": 0.5, "velocity": 95}
  ]
}
```

**MIDI Note Reference:**
- C4 = 60 (Middle C)
- Each semitone = +1
- Each octave = +12

---

### remove_notes

Remove specific notes from a clip.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| clip_index | integer | Yes | Index of the clip |
| pitch | integer | No | Pitch to remove (-1 for all pitches) |
| start_time | float | Yes | Start of time range |
| end_time | float | Yes | End of time range |

---

### remove_all_notes

Remove all notes from a clip.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| clip_index | integer | Yes | Index of the clip |

---

### transpose_notes

Transpose all notes in a clip.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| clip_index | integer | Yes | Index of the clip |
| semitones | integer | Yes | Semitones to transpose (+/-) |

**Example:**
```json
{"track_index": 0, "clip_index": 0, "semitones": 5}
```

---

## Scene Management

### get_all_scenes

Get information about all scenes.

**Parameters:** None

**Returns:**
```json
{
  "scenes": [
    {"index": 0, "name": "Intro", "color": 10},
    {"index": 1, "name": "Verse", "color": 15},
    {"index": 2, "name": "Chorus", "color": 20}
  ]
}
```

---

### create_scene

Create a new scene.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| index | integer | No | Position to insert (-1 for end) |
| name | string | No | Name for the scene |

---

### delete_scene

Delete a scene.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| scene_index | integer | Yes | Index of the scene to delete |

---

### fire_scene

Trigger an entire scene (all clips in that row).

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| scene_index | integer | Yes | Index of the scene |

---

### stop_scene

Stop a scene.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| scene_index | integer | Yes | Index of the scene |

---

### set_scene_name

Set the name of a scene.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| scene_index | integer | Yes | Index of the scene |
| name | string | Yes | New name for the scene |

---

### set_scene_color

Set the color of a scene.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| scene_index | integer | Yes | Index of the scene |
| color | integer | Yes | Color index (0-69) |

---

### duplicate_scene

Duplicate a scene.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| scene_index | integer | Yes | Index of the scene to duplicate |

---

## Device Control

### get_device_parameters

Get all parameters for a device.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| device_index | integer | Yes | Index of the device |

**Returns:**
```json
{
  "name": "Reverb",
  "type": "audio_effect",
  "enabled": true,
  "parameters": [
    {"index": 0, "name": "Decay Time", "value": 0.5, "min": 0.0, "max": 1.0},
    {"index": 1, "name": "Room Size", "value": 0.7, "min": 0.0, "max": 1.0}
  ]
}
```

---

### set_device_parameter

Set a parameter value on a device.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| device_index | integer | Yes | Index of the device |
| parameter_index | integer | Yes | Index of the parameter |
| value | float | Yes | New value (0.0-1.0 normalized) |

---

### toggle_device

Enable or disable a device.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| device_index | integer | Yes | Index of the device |
| enabled | boolean | No | True to enable, false to disable (toggles if not specified) |

---

### delete_device

Remove a device from a track.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| device_index | integer | Yes | Index of the device |

---

### load_instrument_or_effect

Load an instrument or effect from the browser.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| uri | string | Yes | Browser item URI |

---

## Return/Send Tracks

### get_return_tracks

Get information about all return tracks.

**Parameters:** None

**Returns:**
```json
{
  "return_tracks": [
    {"index": 0, "name": "A-Reverb", "volume": 0.85, "pan": 0.0},
    {"index": 1, "name": "B-Delay", "volume": 0.75, "pan": 0.0}
  ]
}
```

---

### get_return_track_info

Get detailed information about a return track.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| return_index | integer | Yes | Index of the return track |

---

### set_send_level

Set the send level from a track to a return track.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the source track |
| send_index | integer | Yes | Index of the send (0=A, 1=B, etc.) |
| level | float | Yes | Send level (0.0-1.0) |

---

### set_return_volume

Set the volume of a return track.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| return_index | integer | Yes | Index of the return track |
| volume | float | Yes | Volume level (0.0-1.0) |

---

### set_return_pan

Set the panning of a return track.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| return_index | integer | Yes | Index of the return track |
| pan | float | Yes | Pan position (-1.0 to 1.0, 0=center) |

---

## Browser Navigation

### get_browser_tree

Navigate the browser hierarchy.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| path | string | No | Path to navigate (empty for root) |

---

### get_browser_items

Get items in a browser category.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| category | string | Yes | Category name (Drums, Instruments, etc.) |

---

### load_browser_item

Load an item from the browser.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Target track index |
| uri | string | Yes | Browser item URI |

---

## View Control

### get_current_view

Get the currently active view.

**Parameters:** None

**Returns:**
```json
{"view": "Session"}
```

Possible values: "Session", "Arrangement", "Detail"

---

### focus_view

Switch to a specific view.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| view | string | Yes | View name: "Session", "Arrangement", or "Detail" |

---

### select_track

Select a track.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track to select |

---

### select_scene

Select a scene.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| scene_index | integer | Yes | Index of the scene to select |

---

### select_clip

Select a clip.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| clip_index | integer | Yes | Index of the clip |

---

## Recording

### start_recording

Begin recording.

**Parameters:** None

---

### stop_recording

Stop recording.

**Parameters:** None

---

### toggle_session_record

Toggle session record mode.

**Parameters:** None

---

### toggle_arrangement_record

Toggle arrangement record mode.

**Parameters:** None

---

### set_overdub

Enable or disable MIDI overdub.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| enabled | boolean | Yes | True to enable, false to disable |

---

### capture_midi

Capture recently played MIDI notes into a new clip.

**Parameters:** None

---

## Arrangement View

### get_arrangement_length

Get the total arrangement time.

**Parameters:** None

**Returns:**
```json
{"length": 128.0, "length_bars": 32}
```

---

### set_arrangement_loop

Set the arrangement loop region.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| start | float | Yes | Loop start in beats |
| end | float | Yes | Loop end in beats |
| enabled | boolean | No | Enable looping (default true) |

---

### jump_to_time

Seek to a specific time in the arrangement.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| time | float | Yes | Time in beats |

---

### get_locators

Get all arrangement locators/markers.

**Parameters:** None

**Returns:**
```json
{
  "locators": [
    {"index": 0, "time": 0.0, "name": "Intro"},
    {"index": 1, "time": 32.0, "name": "Verse 1"},
    {"index": 2, "time": 64.0, "name": "Chorus"}
  ]
}
```

---

### create_locator

Create an arrangement locator/marker.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| time | float | Yes | Time position in beats |
| name | string | No | Name for the locator |

---

### delete_locator

Delete an arrangement locator.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| index | integer | Yes | Index of the locator to delete |

---

## I/O Routing

### get_track_input_routing

Get track input configuration.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |

---

### get_track_output_routing

Get track output configuration.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |

---

### get_available_inputs

List available input options for a track.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |

---

### get_available_outputs

List available output options for a track.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |

---

### set_track_input_routing

Set track input.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| routing_type | string | Yes | Input type |
| channel | string | Yes | Input channel |

---

### set_track_output_routing

Set track output.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| routing_type | string | Yes | Output type |
| channel | string | Yes | Output channel |

---

## Performance & Session Info

### get_cpu_load

Get current CPU usage.

**Parameters:** None

**Returns:**
```json
{"cpu_load": 25.5}
```

---

### get_session_path

Get current project file path.

**Parameters:** None

**Returns:**
```json
{"path": "/Users/me/Music/Projects/MySong.als"}
```

---

### is_session_modified

Check for unsaved changes.

**Parameters:** None

**Returns:**
```json
{"modified": true}
```

---

## AI Music Helpers

### get_scale_notes

Get MIDI note numbers for a scale.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| root | string | Yes | Root note (C, C#, D, Eb, etc.) |
| scale_type | string | Yes | Scale type (see below) |
| octave | integer | No | Starting octave (0-8, default 4) |

**Available Scales:**
- `major` - Major scale (Ionian)
- `minor` - Natural minor (Aeolian)
- `dorian` - Dorian mode
- `phrygian` - Phrygian mode
- `lydian` - Lydian mode
- `mixolydian` - Mixolydian mode
- `aeolian` - Aeolian mode (same as minor)
- `locrian` - Locrian mode
- `harmonic_minor` - Harmonic minor
- `melodic_minor` - Melodic minor
- `pentatonic_major` - Major pentatonic
- `pentatonic_minor` - Minor pentatonic
- `blues` - Blues scale

**Returns:**
```json
{
  "root": "C",
  "scale": "minor",
  "octave": 4,
  "notes": [60, 62, 63, 65, 67, 68, 70, 72],
  "note_names": ["C4", "D4", "Eb4", "F4", "G4", "Ab4", "Bb4", "C5"]
}
```

---

### quantize_clip_notes

Quantize notes in a clip to a grid.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| clip_index | integer | Yes | Index of the clip |
| grid_size | float | Yes | Grid size in beats |
| strength | float | No | Quantize strength 0.0-1.0 (default 1.0) |

**Grid Size Reference:**
- 0.125 = 32nd note
- 0.25 = 16th note
- 0.5 = 8th note
- 1.0 = Quarter note
- 2.0 = Half note

---

### humanize_clip_timing

Add human-like timing variations to notes.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| clip_index | integer | Yes | Index of the clip |
| amount | float | Yes | Variation amount in beats (e.g., 0.02) |

---

### humanize_clip_velocity

Add human-like velocity variations to notes.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| track_index | integer | Yes | Index of the track |
| clip_index | integer | Yes | Index of the clip |
| amount | float | Yes | Velocity variation (+/- range, e.g., 10) |

---

### generate_drum_pattern

Generate a drum pattern.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| style | string | Yes | Pattern style (see below) |
| bars | integer | No | Number of bars (default 2) |
| swing | float | No | Swing amount 0.0-1.0 (default 0) |

**Available Styles:**
- `basic` - Simple rock/pop beat
- `house` - Four-on-the-floor house
- `techno` - Driving techno pattern
- `hip_hop` - Boom-bap hip-hop
- `trap` - Modern trap with hi-hat rolls
- `dnb` - Drum & bass breakbeat
- `jazz` - Jazz swing pattern
- `funk` - Funky syncopated groove

**Returns:**
```json
{
  "style": "house",
  "bars": 2,
  "notes": [
    {"pitch": 36, "start_time": 0.0, "duration": 0.25, "velocity": 100},
    {"pitch": 38, "start_time": 1.0, "duration": 0.25, "velocity": 90}
  ]
}
```

**Drum Map (General MIDI):**
- 36 = Kick
- 38 = Snare
- 42 = Closed Hi-Hat
- 46 = Open Hi-Hat
- 49 = Crash

---

### generate_bassline

Generate a bassline pattern.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| root | string | Yes | Root note (C, D, E, etc.) |
| scale | string | Yes | Scale type (minor, major, dorian, etc.) |
| style | string | Yes | Bassline style (see below) |
| bars | integer | No | Number of bars (default 2) |
| octave | integer | No | Bass octave (default 2) |

**Available Styles:**
- `basic` - Simple root note pattern
- `walking` - Jazz walking bass
- `synth` - Synth bass with long notes
- `funk` - Funky syncopated bass
- `octave` - Octave jumping pattern
- `arpeggiated` - Arpeggiated pattern

**Returns:**
```json
{
  "root": "E",
  "scale": "minor",
  "style": "funk",
  "bars": 2,
  "notes": [
    {"pitch": 40, "start_time": 0.0, "duration": 0.25, "velocity": 100},
    {"pitch": 43, "start_time": 0.5, "duration": 0.25, "velocity": 90}
  ]
}
```

---

## Quick Reference

### Common Workflows

**Create a beat:**
```
1. create_midi_track (name: "Drums")
2. create_clip (track: 0, clip: 0, length: 4)
3. generate_drum_pattern (style: "house")
4. add_notes_to_clip (track: 0, clip: 0, notes: [pattern])
5. fire_clip (track: 0, clip: 0)
```

**Build a song structure:**
```
1. create_scene (name: "Intro")
2. create_scene (name: "Verse")
3. create_scene (name: "Chorus")
4. create_scene (name: "Outro")
5. Create clips in each scene
6. fire_scene to play sections
```

**Add effects:**
```
1. load_instrument_or_effect (track: 0, uri: "reverb")
2. get_device_parameters (track: 0, device: 0)
3. set_device_parameter (track: 0, device: 0, param: 1, value: 0.5)
```
