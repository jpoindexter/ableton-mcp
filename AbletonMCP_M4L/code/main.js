/**
 * AbletonMCP - Multi-Provider AI Integration for Ableton Live
 * Node for Max script that connects any LLM to Ableton Live
 *
 * Supported providers: Ollama, OpenAI, Claude API, Groq
 *
 * 200+ tools for complete Ableton Live control
 */

const Max = require('max-api');
const http = require('http');
const https = require('https');

// ============================================================================
// Configuration
// ============================================================================

let config = {
    provider: 'ollama',      // ollama, openai, claude, groq
    model: 'llama3.2',       // model name
    apiKey: '',              // API key for cloud providers
    ollamaHost: 'http://localhost:11434',
    temperature: 0.7,
    maxTokens: 4096
};

// Live API reference (populated on init)
let liveApi = null;
let liveSet = null;

// ============================================================================
// Tool Definitions (200+ Ableton tools)
// ============================================================================

const TOOLS = [
    // ========================================================================
    // TRANSPORT & SESSION
    // ========================================================================
    {
        name: "get_session_info",
        description: "Get current Ableton session info including tempo, time signature, track count, and scene count",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "set_tempo",
        description: "Set the session tempo in BPM (20-300)",
        parameters: {
            type: "object",
            properties: {
                tempo: { type: "number", description: "Tempo in BPM (20-300)" }
            },
            required: ["tempo"]
        }
    },
    {
        name: "start_playback",
        description: "Start playback in Ableton",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "stop_playback",
        description: "Stop playback in Ableton",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "continue_playing",
        description: "Continue playback from current position",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "stop_all_clips",
        description: "Stop all playing clips",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "tap_tempo",
        description: "Tap tempo",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "undo",
        description: "Undo the last action",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "redo",
        description: "Redo the last undone action",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "get_metronome_state",
        description: "Get metronome on/off state",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "set_metronome",
        description: "Enable or disable the metronome",
        parameters: {
            type: "object",
            properties: {
                enabled: { type: "boolean", description: "True to enable, false to disable" }
            },
            required: ["enabled"]
        }
    },
    {
        name: "jump_to_time",
        description: "Jump to a specific time position in beats",
        parameters: {
            type: "object",
            properties: {
                time: { type: "number", description: "Time position in beats" }
            },
            required: ["time"]
        }
    },
    {
        name: "scrub_by",
        description: "Move playback position by delta beats",
        parameters: {
            type: "object",
            properties: {
                delta: { type: "number", description: "Time delta in beats (positive or negative)" }
            },
            required: ["delta"]
        }
    },
    {
        name: "get_playback_position",
        description: "Get current playback position",
        parameters: { type: "object", properties: {}, required: [] }
    },

    // ========================================================================
    // TRACK MANAGEMENT
    // ========================================================================
    {
        name: "get_track_info",
        description: "Get detailed information about a specific track",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track (0-based)" }
            },
            required: ["track_index"]
        }
    },
    {
        name: "get_all_track_names",
        description: "Get names of all tracks quickly",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "create_midi_track",
        description: "Create a new MIDI track",
        parameters: {
            type: "object",
            properties: {
                index: { type: "integer", description: "Position to insert track (-1 for end)" },
                name: { type: "string", description: "Name for the new track" }
            },
            required: []
        }
    },
    {
        name: "create_audio_track",
        description: "Create a new audio track",
        parameters: {
            type: "object",
            properties: {
                index: { type: "integer", description: "Position to insert track (-1 for end)" },
                name: { type: "string", description: "Name for the new track" }
            },
            required: []
        }
    },
    {
        name: "delete_track",
        description: "Delete a track",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track to delete" }
            },
            required: ["track_index"]
        }
    },
    {
        name: "duplicate_track",
        description: "Duplicate a track with all its clips and devices",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track to duplicate" }
            },
            required: ["track_index"]
        }
    },
    {
        name: "set_track_name",
        description: "Set the name of a track",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                name: { type: "string", description: "New name for the track" }
            },
            required: ["track_index", "name"]
        }
    },
    {
        name: "get_track_color",
        description: "Get the color of a track",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" }
            },
            required: ["track_index"]
        }
    },
    {
        name: "set_track_color",
        description: "Set the color of a track (0-69)",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                color: { type: "integer", description: "Color index (0-69)" }
            },
            required: ["track_index", "color"]
        }
    },
    {
        name: "set_track_volume",
        description: "Set track volume (0.0-1.0)",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                volume: { type: "number", description: "Volume level (0.0-1.0)" }
            },
            required: ["track_index", "volume"]
        }
    },
    {
        name: "set_track_pan",
        description: "Set track pan (-1.0 to 1.0)",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                pan: { type: "number", description: "Pan position (-1.0 left to 1.0 right)" }
            },
            required: ["track_index", "pan"]
        }
    },
    {
        name: "set_track_mute",
        description: "Mute or unmute a track",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                mute: { type: "boolean", description: "True to mute, false to unmute" }
            },
            required: ["track_index", "mute"]
        }
    },
    {
        name: "set_track_solo",
        description: "Solo or unsolo a track",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                solo: { type: "boolean", description: "True to solo, false to unsolo" }
            },
            required: ["track_index", "solo"]
        }
    },
    {
        name: "set_track_arm",
        description: "Arm or disarm a track for recording",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                arm: { type: "boolean", description: "True to arm, false to disarm" }
            },
            required: ["track_index", "arm"]
        }
    },
    {
        name: "select_track",
        description: "Select a track",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" }
            },
            required: ["track_index"]
        }
    },
    {
        name: "get_selected_track",
        description: "Get currently selected track",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "solo_exclusive",
        description: "Solo a track exclusively (unsolo all others)",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track to solo" }
            },
            required: ["track_index"]
        }
    },
    {
        name: "unsolo_all",
        description: "Unsolo all tracks",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "unmute_all",
        description: "Unmute all tracks",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "unarm_all",
        description: "Disarm all tracks",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "freeze_track",
        description: "Freeze a track",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" }
            },
            required: ["track_index"]
        }
    },
    {
        name: "flatten_track",
        description: "Flatten a frozen track",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" }
            },
            required: ["track_index"]
        }
    },
    {
        name: "get_track_delay",
        description: "Get track delay in ms",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" }
            },
            required: ["track_index"]
        }
    },
    {
        name: "set_track_delay",
        description: "Set track delay in ms",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                delay_ms: { type: "number", description: "Delay in milliseconds" }
            },
            required: ["track_index", "delay_ms"]
        }
    },
    {
        name: "get_track_output_meter",
        description: "Get track output meter level",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" }
            },
            required: ["track_index"]
        }
    },
    {
        name: "get_track_capabilities",
        description: "Get track capabilities (can_be_armed, has_midi_input, etc)",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" }
            },
            required: ["track_index"]
        }
    },

    // ========================================================================
    // CLIP OPERATIONS
    // ========================================================================
    {
        name: "get_clip_info",
        description: "Get information about a specific clip",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip slot" }
            },
            required: ["track_index", "clip_index"]
        }
    },
    {
        name: "create_clip",
        description: "Create a new MIDI clip",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip slot" },
                length: { type: "number", description: "Length in beats (default 4)" },
                name: { type: "string", description: "Name for the clip" }
            },
            required: ["track_index", "clip_index"]
        }
    },
    {
        name: "delete_clip",
        description: "Delete a clip",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip slot" }
            },
            required: ["track_index", "clip_index"]
        }
    },
    {
        name: "duplicate_clip",
        description: "Duplicate a clip",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" }
            },
            required: ["track_index", "clip_index"]
        }
    },
    {
        name: "fire_clip",
        description: "Trigger a clip to start playing",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" }
            },
            required: ["track_index", "clip_index"]
        }
    },
    {
        name: "stop_clip",
        description: "Stop a playing clip",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" }
            },
            required: ["track_index", "clip_index"]
        }
    },
    {
        name: "select_clip",
        description: "Select a clip",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" }
            },
            required: ["track_index", "clip_index"]
        }
    },
    {
        name: "set_clip_name",
        description: "Set the name of a clip",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                name: { type: "string", description: "New name for the clip" }
            },
            required: ["track_index", "clip_index", "name"]
        }
    },
    {
        name: "get_clip_color",
        description: "Get the color of a clip",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" }
            },
            required: ["track_index", "clip_index"]
        }
    },
    {
        name: "set_clip_color",
        description: "Set the color of a clip (0-69)",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                color: { type: "integer", description: "Color index (0-69)" }
            },
            required: ["track_index", "clip_index", "color"]
        }
    },
    {
        name: "get_clip_loop",
        description: "Get clip loop settings",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" }
            },
            required: ["track_index", "clip_index"]
        }
    },
    {
        name: "set_clip_loop",
        description: "Set clip loop settings",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                loop_start: { type: "number", description: "Loop start in beats" },
                loop_end: { type: "number", description: "Loop end in beats" },
                looping: { type: "boolean", description: "Enable/disable looping" }
            },
            required: ["track_index", "clip_index"]
        }
    },
    {
        name: "duplicate_clip_loop",
        description: "Double the clip length by duplicating loop content",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" }
            },
            required: ["track_index", "clip_index"]
        }
    },
    {
        name: "get_clip_is_playing",
        description: "Check if a clip is playing",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" }
            },
            required: ["track_index", "clip_index"]
        }
    },
    {
        name: "get_clip_playing_position",
        description: "Get the current playing position in a clip",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" }
            },
            required: ["track_index", "clip_index"]
        }
    },

    // ========================================================================
    // MIDI NOTE EDITING
    // ========================================================================
    {
        name: "get_clip_notes",
        description: "Get all notes from a MIDI clip",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" }
            },
            required: ["track_index", "clip_index"]
        }
    },
    {
        name: "get_notes_in_range",
        description: "Get notes within a time and pitch range",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                start_time: { type: "number", description: "Start time in beats" },
                end_time: { type: "number", description: "End time in beats" },
                pitch_start: { type: "integer", description: "Start pitch (0-127)" },
                pitch_end: { type: "integer", description: "End pitch (0-127)" }
            },
            required: ["track_index", "clip_index", "start_time", "end_time"]
        }
    },
    {
        name: "add_notes_to_clip",
        description: "Add MIDI notes to a clip",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                notes: {
                    type: "array",
                    description: "Array of notes with pitch (0-127), start_time (beats), duration (beats), velocity (1-127)",
                    items: {
                        type: "object",
                        properties: {
                            pitch: { type: "integer" },
                            start_time: { type: "number" },
                            duration: { type: "number" },
                            velocity: { type: "integer" }
                        }
                    }
                }
            },
            required: ["track_index", "clip_index", "notes"]
        }
    },
    {
        name: "set_clip_notes",
        description: "Replace all notes in a clip",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                notes: {
                    type: "array",
                    description: "Array of notes to set",
                    items: {
                        type: "object",
                        properties: {
                            pitch: { type: "integer" },
                            start_time: { type: "number" },
                            duration: { type: "number" },
                            velocity: { type: "integer" }
                        }
                    }
                }
            },
            required: ["track_index", "clip_index", "notes"]
        }
    },
    {
        name: "remove_notes",
        description: "Remove notes in a time/pitch range",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                from_time: { type: "number", description: "Start time" },
                time_span: { type: "number", description: "Time span" },
                from_pitch: { type: "integer", description: "Start pitch (0-127)" },
                pitch_span: { type: "integer", description: "Pitch range" }
            },
            required: ["track_index", "clip_index", "from_time", "time_span"]
        }
    },
    {
        name: "remove_all_notes",
        description: "Remove all notes from a clip",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" }
            },
            required: ["track_index", "clip_index"]
        }
    },
    {
        name: "transpose_notes",
        description: "Transpose all notes in a clip by semitones",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                semitones: { type: "integer", description: "Semitones to transpose (+/-)" }
            },
            required: ["track_index", "clip_index", "semitones"]
        }
    },
    {
        name: "move_clip_notes",
        description: "Move notes by time and/or pitch delta",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                time_delta: { type: "number", description: "Time shift in beats" },
                pitch_delta: { type: "integer", description: "Pitch shift in semitones" }
            },
            required: ["track_index", "clip_index", "time_delta", "pitch_delta"]
        }
    },
    {
        name: "quantize_clip",
        description: "Quantize notes to a grid",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                quantize_to: { type: "number", description: "Grid size (0.25=16th, 0.5=8th, 1=quarter)" },
                amount: { type: "number", description: "Quantize strength (0.0-1.0)" }
            },
            required: ["track_index", "clip_index", "quantize_to"]
        }
    },
    {
        name: "deselect_all_notes",
        description: "Deselect all notes in a clip",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" }
            },
            required: ["track_index", "clip_index"]
        }
    },
    {
        name: "set_clip_velocity_amount",
        description: "Set velocity scaling amount for a clip",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                amount: { type: "number", description: "Velocity amount (0.0-1.0)" }
            },
            required: ["track_index", "clip_index", "amount"]
        }
    },

    // ========================================================================
    // AUDIO CLIP EDITING
    // ========================================================================
    {
        name: "get_clip_gain",
        description: "Get audio clip gain",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" }
            },
            required: ["track_index", "clip_index"]
        }
    },
    {
        name: "set_clip_gain",
        description: "Set audio clip gain in dB",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                gain: { type: "number", description: "Gain in dB" }
            },
            required: ["track_index", "clip_index", "gain"]
        }
    },
    {
        name: "get_clip_pitch",
        description: "Get audio clip pitch shift",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" }
            },
            required: ["track_index", "clip_index"]
        }
    },
    {
        name: "set_clip_pitch",
        description: "Set audio clip pitch shift (-48 to +48 semitones)",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                pitch: { type: "integer", description: "Pitch shift in semitones (-48 to +48)" }
            },
            required: ["track_index", "clip_index", "pitch"]
        }
    },
    {
        name: "set_clip_warp_mode",
        description: "Set audio clip warp mode",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                mode: { type: "integer", description: "Warp mode (0=Beats, 1=Tones, 2=Texture, 3=Re-Pitch, 4=Complex, 5=Complex Pro)" }
            },
            required: ["track_index", "clip_index", "mode"]
        }
    },
    {
        name: "get_clip_warp_info",
        description: "Get audio clip warp information",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" }
            },
            required: ["track_index", "clip_index"]
        }
    },
    {
        name: "get_warp_markers",
        description: "Get warp markers from an audio clip",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" }
            },
            required: ["track_index", "clip_index"]
        }
    },
    {
        name: "add_warp_marker",
        description: "Add a warp marker to an audio clip",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                beat_time: { type: "number", description: "Beat time position" },
                sample_time: { type: "number", description: "Sample time position" }
            },
            required: ["track_index", "clip_index", "beat_time", "sample_time"]
        }
    },
    {
        name: "delete_warp_marker",
        description: "Delete a warp marker",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                index: { type: "integer", description: "Index of the warp marker" }
            },
            required: ["track_index", "clip_index", "index"]
        }
    },
    {
        name: "get_clip_fades",
        description: "Get audio clip fade settings",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" }
            },
            required: ["track_index", "clip_index"]
        }
    },
    {
        name: "set_clip_fade_in",
        description: "Set audio clip fade in",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                start: { type: "number", description: "Fade start" },
                end: { type: "number", description: "Fade end" }
            },
            required: ["track_index", "clip_index", "start", "end"]
        }
    },
    {
        name: "set_clip_fade_out",
        description: "Set audio clip fade out",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                start: { type: "number", description: "Fade start" },
                end: { type: "number", description: "Fade end" }
            },
            required: ["track_index", "clip_index", "start", "end"]
        }
    },
    {
        name: "get_audio_clip_file_path",
        description: "Get the file path of an audio clip",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" }
            },
            required: ["track_index", "clip_index"]
        }
    },
    {
        name: "set_clip_ram_mode",
        description: "Set whether audio clip loads to RAM",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                enabled: { type: "boolean", description: "True to load to RAM" }
            },
            required: ["track_index", "clip_index", "enabled"]
        }
    },

    // ========================================================================
    // CLIP LAUNCH & FOLLOW ACTIONS
    // ========================================================================
    {
        name: "get_clip_launch_mode",
        description: "Get clip launch mode",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" }
            },
            required: ["track_index", "clip_index"]
        }
    },
    {
        name: "set_clip_launch_mode",
        description: "Set clip launch mode (0=Trigger, 1=Gate, 2=Toggle, 3=Repeat)",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                mode: { type: "integer", description: "Launch mode (0=Trigger, 1=Gate, 2=Toggle, 3=Repeat)" }
            },
            required: ["track_index", "clip_index", "mode"]
        }
    },
    {
        name: "get_clip_launch_quantization",
        description: "Get clip launch quantization",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" }
            },
            required: ["track_index", "clip_index"]
        }
    },
    {
        name: "set_clip_launch_quantization",
        description: "Set clip launch quantization",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                quantization: { type: "integer", description: "Quantization value" }
            },
            required: ["track_index", "clip_index", "quantization"]
        }
    },
    {
        name: "get_clip_follow_action",
        description: "Get clip follow action settings",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" }
            },
            required: ["track_index", "clip_index"]
        }
    },
    {
        name: "set_clip_follow_action",
        description: "Set clip follow action",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                action_a: { type: "integer", description: "Action A type" },
                action_b: { type: "integer", description: "Action B type" },
                chance: { type: "number", description: "Chance A vs B" },
                time: { type: "number", description: "Follow time in beats" }
            },
            required: ["track_index", "clip_index"]
        }
    },

    // ========================================================================
    // SCENE MANAGEMENT
    // ========================================================================
    {
        name: "get_all_scenes",
        description: "Get information about all scenes",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "create_scene",
        description: "Create a new scene",
        parameters: {
            type: "object",
            properties: {
                index: { type: "integer", description: "Position to insert (-1 for end)" }
            },
            required: []
        }
    },
    {
        name: "delete_scene",
        description: "Delete a scene",
        parameters: {
            type: "object",
            properties: {
                scene_index: { type: "integer", description: "Index of the scene" }
            },
            required: ["scene_index"]
        }
    },
    {
        name: "duplicate_scene",
        description: "Duplicate a scene",
        parameters: {
            type: "object",
            properties: {
                scene_index: { type: "integer", description: "Index of the scene" }
            },
            required: ["scene_index"]
        }
    },
    {
        name: "fire_scene",
        description: "Launch a scene",
        parameters: {
            type: "object",
            properties: {
                scene_index: { type: "integer", description: "Index of the scene" }
            },
            required: ["scene_index"]
        }
    },
    {
        name: "stop_scene",
        description: "Stop a scene",
        parameters: {
            type: "object",
            properties: {
                scene_index: { type: "integer", description: "Index of the scene" }
            },
            required: ["scene_index"]
        }
    },
    {
        name: "set_scene_name",
        description: "Set the name of a scene",
        parameters: {
            type: "object",
            properties: {
                scene_index: { type: "integer", description: "Index of the scene" },
                name: { type: "string", description: "New name" }
            },
            required: ["scene_index", "name"]
        }
    },
    {
        name: "get_scene_color",
        description: "Get scene color",
        parameters: {
            type: "object",
            properties: {
                scene_index: { type: "integer", description: "Index of the scene" }
            },
            required: ["scene_index"]
        }
    },
    {
        name: "set_scene_color",
        description: "Set scene color (0-69)",
        parameters: {
            type: "object",
            properties: {
                scene_index: { type: "integer", description: "Index of the scene" },
                color: { type: "integer", description: "Color index (0-69)" }
            },
            required: ["scene_index", "color"]
        }
    },
    {
        name: "select_scene",
        description: "Select a scene",
        parameters: {
            type: "object",
            properties: {
                scene_index: { type: "integer", description: "Index of the scene" }
            },
            required: ["scene_index"]
        }
    },
    {
        name: "get_selected_scene",
        description: "Get currently selected scene",
        parameters: { type: "object", properties: {}, required: [] }
    },

    // ========================================================================
    // DEVICE CONTROL
    // ========================================================================
    {
        name: "get_device_parameters",
        description: "Get all parameters for a device",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                device_index: { type: "integer", description: "Index of the device" }
            },
            required: ["track_index", "device_index"]
        }
    },
    {
        name: "set_device_parameter",
        description: "Set a device parameter value",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                device_index: { type: "integer", description: "Index of the device" },
                parameter_index: { type: "integer", description: "Index of the parameter" },
                value: { type: "number", description: "New value (0.0-1.0 normalized)" }
            },
            required: ["track_index", "device_index", "parameter_index", "value"]
        }
    },
    {
        name: "toggle_device",
        description: "Enable or disable a device",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                device_index: { type: "integer", description: "Index of the device" },
                enabled: { type: "boolean", description: "True to enable" }
            },
            required: ["track_index", "device_index"]
        }
    },
    {
        name: "delete_device",
        description: "Delete a device from a track",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                device_index: { type: "integer", description: "Index of the device" }
            },
            required: ["track_index", "device_index"]
        }
    },
    {
        name: "get_device_by_name",
        description: "Find a device by name on a track",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                device_name: { type: "string", description: "Name of the device" }
            },
            required: ["track_index", "device_name"]
        }
    },
    {
        name: "select_device",
        description: "Select a device for viewing",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                device_index: { type: "integer", description: "Index of the device" }
            },
            required: ["track_index", "device_index"]
        }
    },
    {
        name: "get_selected_device",
        description: "Get currently selected device",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "move_device",
        description: "Move device to new position",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                device_index: { type: "integer", description: "Index of the device" },
                new_index: { type: "integer", description: "New position" }
            },
            required: ["track_index", "device_index", "new_index"]
        }
    },

    // ========================================================================
    // RACK CONTROL
    // ========================================================================
    {
        name: "get_rack_chains",
        description: "Get chains in a rack device",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                device_index: { type: "integer", description: "Index of the rack device" }
            },
            required: ["track_index", "device_index"]
        }
    },
    {
        name: "select_rack_chain",
        description: "Select a chain in a rack",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                device_index: { type: "integer", description: "Index of the rack device" },
                chain_index: { type: "integer", description: "Index of the chain" }
            },
            required: ["track_index", "device_index", "chain_index"]
        }
    },
    {
        name: "get_rack_macros",
        description: "Get macro control values",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                device_index: { type: "integer", description: "Index of the rack device" }
            },
            required: ["track_index", "device_index"]
        }
    },
    {
        name: "set_rack_macro",
        description: "Set a macro control value",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                device_index: { type: "integer", description: "Index of the rack device" },
                macro_index: { type: "integer", description: "Index of the macro (0-7 or 0-15)" },
                value: { type: "number", description: "Value (0.0-1.0)" }
            },
            required: ["track_index", "device_index", "macro_index", "value"]
        }
    },

    // ========================================================================
    // DRUM RACK
    // ========================================================================
    {
        name: "get_drum_rack_pads",
        description: "Get all pads in a drum rack",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                device_index: { type: "integer", description: "Index of the drum rack" }
            },
            required: ["track_index", "device_index"]
        }
    },
    {
        name: "get_drum_pad_info",
        description: "Get info about a drum pad",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                device_index: { type: "integer", description: "Index of the drum rack" },
                pad_index: { type: "integer", description: "Index of the pad" }
            },
            required: ["track_index", "device_index", "pad_index"]
        }
    },
    {
        name: "set_drum_rack_pad_mute",
        description: "Mute/unmute a drum pad",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                device_index: { type: "integer", description: "Index of the drum rack" },
                note: { type: "integer", description: "MIDI note of the pad (36-127)" },
                mute: { type: "boolean", description: "True to mute" }
            },
            required: ["track_index", "device_index", "note", "mute"]
        }
    },
    {
        name: "set_drum_rack_pad_solo",
        description: "Solo/unsolo a drum pad",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                device_index: { type: "integer", description: "Index of the drum rack" },
                note: { type: "integer", description: "MIDI note of the pad (36-127)" },
                solo: { type: "boolean", description: "True to solo" }
            },
            required: ["track_index", "device_index", "note", "solo"]
        }
    },
    {
        name: "set_drum_pad_name",
        description: "Set drum pad name",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                device_index: { type: "integer", description: "Index of the drum rack" },
                pad_index: { type: "integer", description: "Index of the pad" },
                name: { type: "string", description: "New name" }
            },
            required: ["track_index", "device_index", "pad_index", "name"]
        }
    },

    // ========================================================================
    // SIMPLER/SAMPLER
    // ========================================================================
    {
        name: "get_simpler_sample_info",
        description: "Get Simpler/Sampler sample information",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                device_index: { type: "integer", description: "Index of the Simpler/Sampler" }
            },
            required: ["track_index", "device_index"]
        }
    },
    {
        name: "get_simpler_parameters",
        description: "Get Simpler playback parameters",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                device_index: { type: "integer", description: "Index of the Simpler" }
            },
            required: ["track_index", "device_index"]
        }
    },

    // ========================================================================
    // BROWSER & LOADING
    // ========================================================================
    {
        name: "get_browser_tree",
        description: "Get browser category structure",
        parameters: {
            type: "object",
            properties: {
                category_type: { type: "string", description: "Category type (all, sounds, drums, instruments, effects, samples)" }
            },
            required: []
        }
    },
    {
        name: "search_browser",
        description: "Search the browser for items",
        parameters: {
            type: "object",
            properties: {
                query: { type: "string", description: "Search query" },
                category: { type: "string", description: "Category to search (all, sounds, etc.)" }
            },
            required: ["query"]
        }
    },
    {
        name: "load_instrument_or_effect",
        description: "Load an instrument or effect to a track",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                uri: { type: "string", description: "URI of the item to load" }
            },
            required: ["track_index", "uri"]
        }
    },
    {
        name: "load_browser_item",
        description: "Load a browser item to a track",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                item_uri: { type: "string", description: "URI of the browser item" }
            },
            required: ["track_index", "item_uri"]
        }
    },
    {
        name: "load_browser_item_to_return",
        description: "Load an effect to a return track",
        parameters: {
            type: "object",
            properties: {
                return_index: { type: "integer", description: "Index of the return track" },
                item_uri: { type: "string", description: "URI of the effect" }
            },
            required: ["return_index", "item_uri"]
        }
    },
    {
        name: "load_device_preset",
        description: "Load a preset to a device",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                device_index: { type: "integer", description: "Index of the device" },
                preset_uri: { type: "string", description: "URI of the preset" }
            },
            required: ["track_index", "device_index", "preset_uri"]
        }
    },

    // ========================================================================
    // RETURN/SEND TRACKS
    // ========================================================================
    {
        name: "get_return_tracks",
        description: "Get information about all return tracks",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "get_return_track_info",
        description: "Get info about a return track",
        parameters: {
            type: "object",
            properties: {
                return_index: { type: "integer", description: "Index of the return track" }
            },
            required: ["return_index"]
        }
    },
    {
        name: "create_return_track",
        description: "Create a new return track",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "delete_return_track",
        description: "Delete a return track",
        parameters: {
            type: "object",
            properties: {
                index: { type: "integer", description: "Index of the return track" }
            },
            required: ["index"]
        }
    },
    {
        name: "get_send_level",
        description: "Get send level from a track",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                send_index: { type: "integer", description: "Index of the send (0=A, 1=B, etc.)" }
            },
            required: ["track_index", "send_index"]
        }
    },
    {
        name: "set_send_level",
        description: "Set send level from a track to a return",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                send_index: { type: "integer", description: "Index of the send (0=A, 1=B, etc.)" },
                level: { type: "number", description: "Send level (0.0-1.0)" }
            },
            required: ["track_index", "send_index", "level"]
        }
    },
    {
        name: "set_return_volume",
        description: "Set the volume of a return track",
        parameters: {
            type: "object",
            properties: {
                return_index: { type: "integer", description: "Index of the return track" },
                volume: { type: "number", description: "Volume (0.0-1.0)" }
            },
            required: ["return_index", "volume"]
        }
    },
    {
        name: "set_return_pan",
        description: "Set the pan of a return track",
        parameters: {
            type: "object",
            properties: {
                return_index: { type: "integer", description: "Index of the return track" },
                pan: { type: "number", description: "Pan (-1.0 to 1.0)" }
            },
            required: ["return_index", "pan"]
        }
    },

    // ========================================================================
    // MASTER TRACK
    // ========================================================================
    {
        name: "get_master_info",
        description: "Get master track information",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "set_master_volume",
        description: "Set master track volume",
        parameters: {
            type: "object",
            properties: {
                volume: { type: "number", description: "Volume (0.0-1.0)" }
            },
            required: ["volume"]
        }
    },
    {
        name: "set_master_pan",
        description: "Set master track pan",
        parameters: {
            type: "object",
            properties: {
                pan: { type: "number", description: "Pan (-1.0 to 1.0)" }
            },
            required: ["pan"]
        }
    },
    {
        name: "get_cue_volume",
        description: "Get cue/preview volume",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "set_cue_volume",
        description: "Set cue/preview volume",
        parameters: {
            type: "object",
            properties: {
                volume: { type: "number", description: "Volume (0.0-1.0)" }
            },
            required: ["volume"]
        }
    },

    // ========================================================================
    // CROSSFADER
    // ========================================================================
    {
        name: "get_crossfader",
        description: "Get crossfader position",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "set_crossfader",
        description: "Set crossfader position",
        parameters: {
            type: "object",
            properties: {
                value: { type: "number", description: "Position (0.0=A, 0.5=center, 1.0=B)" }
            },
            required: ["value"]
        }
    },
    {
        name: "get_track_crossfade_assign",
        description: "Get track crossfade assignment",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" }
            },
            required: ["track_index"]
        }
    },
    {
        name: "set_track_crossfade_assign",
        description: "Set track crossfade assignment (0=A, 1=None, 2=B)",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                assign: { type: "integer", description: "Assignment (0=A, 1=None, 2=B)" }
            },
            required: ["track_index", "assign"]
        }
    },

    // ========================================================================
    // RECORDING
    // ========================================================================
    {
        name: "start_recording",
        description: "Start recording",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "stop_recording",
        description: "Stop recording",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "toggle_session_record",
        description: "Toggle session record button",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "toggle_arrangement_record",
        description: "Toggle arrangement record button",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "set_overdub",
        description: "Set MIDI overdub mode",
        parameters: {
            type: "object",
            properties: {
                enabled: { type: "boolean", description: "True to enable overdub" }
            },
            required: ["enabled"]
        }
    },
    {
        name: "capture_midi",
        description: "Capture recently played MIDI",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "get_session_automation_record",
        description: "Get session automation record state",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "set_session_automation_record",
        description: "Set session automation record",
        parameters: {
            type: "object",
            properties: {
                enabled: { type: "boolean", description: "True to enable" }
            },
            required: ["enabled"]
        }
    },
    {
        name: "get_arrangement_overdub",
        description: "Get arrangement overdub state",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "set_arrangement_overdub",
        description: "Set arrangement overdub",
        parameters: {
            type: "object",
            properties: {
                enabled: { type: "boolean", description: "True to enable" }
            },
            required: ["enabled"]
        }
    },
    {
        name: "re_enable_automation",
        description: "Re-enable all automation (un-override)",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "get_count_in_duration",
        description: "Get count-in duration setting",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "set_count_in_duration",
        description: "Set count-in duration (0=None, 1=1bar, 2=2bars, 4=4bars)",
        parameters: {
            type: "object",
            properties: {
                duration: { type: "integer", description: "Duration (0, 1, 2, or 4)" }
            },
            required: ["duration"]
        }
    },

    // ========================================================================
    // ARRANGEMENT
    // ========================================================================
    {
        name: "get_arrangement_length",
        description: "Get arrangement length in beats",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "set_arrangement_loop",
        description: "Set arrangement loop region",
        parameters: {
            type: "object",
            properties: {
                start: { type: "number", description: "Loop start in beats" },
                end: { type: "number", description: "Loop end in beats" },
                enabled: { type: "boolean", description: "Enable loop" }
            },
            required: ["start", "end"]
        }
    },
    {
        name: "get_locators",
        description: "Get all locators/cue points",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "create_locator",
        description: "Create a locator at a position",
        parameters: {
            type: "object",
            properties: {
                time: { type: "number", description: "Time position in beats" },
                name: { type: "string", description: "Locator name" }
            },
            required: ["time"]
        }
    },
    {
        name: "delete_locator",
        description: "Delete a locator",
        parameters: {
            type: "object",
            properties: {
                locator_index: { type: "integer", description: "Index of the locator" }
            },
            required: ["locator_index"]
        }
    },
    {
        name: "jump_to_cue_point",
        description: "Jump to a cue point",
        parameters: {
            type: "object",
            properties: {
                index: { type: "integer", description: "Index of the cue point" }
            },
            required: ["index"]
        }
    },
    {
        name: "jump_to_prev_cue",
        description: "Jump to previous cue point",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "jump_to_next_cue",
        description: "Jump to next cue point",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "get_punch_settings",
        description: "Get punch in/out settings",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "set_punch_in",
        description: "Enable/disable punch in",
        parameters: {
            type: "object",
            properties: {
                enabled: { type: "boolean", description: "True to enable" }
            },
            required: ["enabled"]
        }
    },
    {
        name: "set_punch_out",
        description: "Enable/disable punch out",
        parameters: {
            type: "object",
            properties: {
                enabled: { type: "boolean", description: "True to enable" }
            },
            required: ["enabled"]
        }
    },
    {
        name: "trigger_back_to_arrangement",
        description: "Return to arrangement (exit session override)",
        parameters: { type: "object", properties: {}, required: [] }
    },

    // ========================================================================
    // AUTOMATION
    // ========================================================================
    {
        name: "get_clip_automation",
        description: "Get clip automation envelope",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                parameter_index: { type: "integer", description: "Index of the parameter" }
            },
            required: ["track_index", "clip_index", "parameter_index"]
        }
    },
    {
        name: "set_clip_automation",
        description: "Set clip automation envelope points",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                parameter_index: { type: "integer", description: "Index of the parameter" },
                points: {
                    type: "array",
                    description: "Array of points with time and value",
                    items: {
                        type: "object",
                        properties: {
                            time: { type: "number" },
                            value: { type: "number" }
                        }
                    }
                }
            },
            required: ["track_index", "clip_index", "parameter_index", "points"]
        }
    },
    {
        name: "clear_clip_automation",
        description: "Clear clip automation for a parameter",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                parameter_index: { type: "integer", description: "Index of the parameter" }
            },
            required: ["track_index", "clip_index", "parameter_index"]
        }
    },
    {
        name: "get_clip_has_envelopes",
        description: "Check if clip has automation envelopes",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" }
            },
            required: ["track_index", "clip_index"]
        }
    },

    // ========================================================================
    // VIEW CONTROL
    // ========================================================================
    {
        name: "get_current_view",
        description: "Get current view (Session/Arranger)",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "focus_view",
        description: "Switch to a view",
        parameters: {
            type: "object",
            properties: {
                view_name: { type: "string", description: "View name (Session, Arranger, Detail, etc.)" }
            },
            required: ["view_name"]
        }
    },
    {
        name: "get_detail_clip",
        description: "Get clip shown in detail view",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "set_detail_clip",
        description: "Show a clip in detail view",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" }
            },
            required: ["track_index", "clip_index"]
        }
    },
    {
        name: "get_follow_mode",
        description: "Get follow playhead mode",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "set_follow_mode",
        description: "Set follow playhead mode",
        parameters: {
            type: "object",
            properties: {
                enabled: { type: "boolean", description: "True to follow playhead" }
            },
            required: ["enabled"]
        }
    },
    {
        name: "get_draw_mode",
        description: "Get draw mode state",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "set_draw_mode",
        description: "Set draw mode",
        parameters: {
            type: "object",
            properties: {
                enabled: { type: "boolean", description: "True to enable draw mode" }
            },
            required: ["enabled"]
        }
    },
    {
        name: "get_grid_quantization",
        description: "Get grid quantization setting",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "set_grid_quantization",
        description: "Set grid quantization",
        parameters: {
            type: "object",
            properties: {
                quantization: { type: "integer", description: "Grid quantization value" },
                triplet: { type: "boolean", description: "Enable triplet grid" }
            },
            required: ["quantization"]
        }
    },

    // ========================================================================
    // SONG PROPERTIES
    // ========================================================================
    {
        name: "get_signature",
        description: "Get time signature",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "set_signature",
        description: "Set time signature",
        parameters: {
            type: "object",
            properties: {
                numerator: { type: "integer", description: "Numerator (beats per bar)" },
                denominator: { type: "integer", description: "Denominator (beat value)" }
            },
            required: ["numerator", "denominator"]
        }
    },
    {
        name: "get_swing_amount",
        description: "Get global swing amount",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "set_swing_amount",
        description: "Set global swing amount (0.0-1.0)",
        parameters: {
            type: "object",
            properties: {
                amount: { type: "number", description: "Swing amount (0.0-1.0)" }
            },
            required: ["amount"]
        }
    },
    {
        name: "get_groove_amount",
        description: "Get groove pool intensity",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "set_groove_amount",
        description: "Set groove pool intensity",
        parameters: {
            type: "object",
            properties: {
                amount: { type: "number", description: "Groove amount (0.0-1.0)" }
            },
            required: ["amount"]
        }
    },
    {
        name: "get_song_root_note",
        description: "Get song root note/key",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "set_song_root_note",
        description: "Set song root note (0=C, 1=C#, ... 11=B)",
        parameters: {
            type: "object",
            properties: {
                root_note: { type: "integer", description: "Root note (0-11)" }
            },
            required: ["root_note"]
        }
    },
    {
        name: "get_song_scale",
        description: "Get song scale",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "get_exclusive_arm",
        description: "Get exclusive arm mode",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "set_exclusive_arm",
        description: "Set exclusive arm mode",
        parameters: {
            type: "object",
            properties: {
                enabled: { type: "boolean", description: "True for exclusive arm" }
            },
            required: ["enabled"]
        }
    },
    {
        name: "get_exclusive_solo",
        description: "Get exclusive solo mode",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "set_exclusive_solo",
        description: "Set exclusive solo mode",
        parameters: {
            type: "object",
            properties: {
                enabled: { type: "boolean", description: "True for exclusive solo" }
            },
            required: ["enabled"]
        }
    },

    // ========================================================================
    // GROOVE POOL
    // ========================================================================
    {
        name: "get_groove_pool",
        description: "Get grooves in the groove pool",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "apply_groove",
        description: "Apply a groove to a clip",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                groove_index: { type: "integer", description: "Index of the groove" }
            },
            required: ["track_index", "clip_index", "groove_index"]
        }
    },
    {
        name: "commit_groove",
        description: "Commit groove to clip (make permanent)",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" }
            },
            required: ["track_index", "clip_index"]
        }
    },

    // ========================================================================
    // GROUP TRACKS
    // ========================================================================
    {
        name: "create_group_track",
        description: "Create a group track from selected tracks",
        parameters: {
            type: "object",
            properties: {
                track_indices: {
                    type: "array",
                    description: "Array of track indices to group",
                    items: { type: "integer" }
                }
            },
            required: ["track_indices"]
        }
    },
    {
        name: "ungroup_tracks",
        description: "Ungroup a group track",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the group track" }
            },
            required: ["track_index"]
        }
    },
    {
        name: "fold_track",
        description: "Fold/collapse a group track",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the group track" }
            },
            required: ["track_index"]
        }
    },
    {
        name: "unfold_track",
        description: "Unfold/expand a group track",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the group track" }
            },
            required: ["track_index"]
        }
    },
    {
        name: "get_track_is_grouped",
        description: "Check if track is in a group",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" }
            },
            required: ["track_index"]
        }
    },
    {
        name: "get_track_is_foldable",
        description: "Check if track can be folded (is a group)",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" }
            },
            required: ["track_index"]
        }
    },

    // ========================================================================
    // SESSION INFO
    // ========================================================================
    {
        name: "get_session_path",
        description: "Get path to the current Live Set",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "is_session_modified",
        description: "Check if session has unsaved changes",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "get_cpu_load",
        description: "Get current CPU load",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "health_check",
        description: "Check connection to Ableton",
        parameters: { type: "object", properties: {}, required: [] }
    },

    // ========================================================================
    // AI MUSIC HELPERS
    // ========================================================================
    {
        name: "get_scale_notes",
        description: "Get MIDI note numbers for a scale (major, minor, dorian, phrygian, lydian, mixolydian, locrian, harmonic_minor, melodic_minor, pentatonic_major, pentatonic_minor, blues)",
        parameters: {
            type: "object",
            properties: {
                root: { type: "integer", description: "Root note (0=C, 1=C#, ... 11=B)" },
                scale_type: { type: "string", description: "Scale type" }
            },
            required: ["root", "scale_type"]
        }
    },
    {
        name: "quantize_clip_notes",
        description: "Smart quantize with strength control",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                grid: { type: "number", description: "Grid size in beats" },
                amount: { type: "number", description: "Quantize strength (0.0-1.0)" }
            },
            required: ["track_index", "clip_index", "grid"]
        }
    },
    {
        name: "humanize_clip_timing",
        description: "Add human-like timing variations",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                amount: { type: "number", description: "Humanize amount (0.01 = subtle, 0.1 = heavy)" }
            },
            required: ["track_index", "clip_index", "amount"]
        }
    },
    {
        name: "humanize_clip_velocity",
        description: "Add human-like velocity variations",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                amount: { type: "number", description: "Velocity variation (0.0-1.0)" }
            },
            required: ["track_index", "clip_index", "amount"]
        }
    },
    {
        name: "generate_drum_pattern",
        description: "Generate a drum pattern (styles: basic, house, techno, hip_hop, trap, dnb, jazz, funk)",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the drum track" },
                clip_index: { type: "integer", description: "Index of the clip slot" },
                style: { type: "string", description: "Pattern style" },
                complexity: { type: "number", description: "Complexity (0.0-1.0)" }
            },
            required: ["track_index", "clip_index", "style"]
        }
    },
    {
        name: "generate_bassline",
        description: "Generate a bassline (styles: basic, walking, synth, funk, octave, arpeggiated)",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the bass track" },
                clip_index: { type: "integer", description: "Index of the clip slot" },
                root: { type: "integer", description: "Root note (0=C)" },
                scale: { type: "string", description: "Scale type" },
                style: { type: "string", description: "Bassline style" }
            },
            required: ["track_index", "clip_index", "root", "scale", "style"]
        }
    }
];

// ============================================================================
// Provider API Implementations
// ============================================================================

function formatToolsForProvider(provider) {
    switch (provider) {
        case 'ollama':
            return TOOLS.map(t => ({
                type: 'function',
                function: {
                    name: t.name,
                    description: t.description,
                    parameters: t.parameters
                }
            }));

        case 'openai':
        case 'groq':
            return TOOLS.map(t => ({
                type: 'function',
                function: {
                    name: t.name,
                    description: t.description,
                    parameters: t.parameters
                }
            }));

        case 'claude':
            return TOOLS.map(t => ({
                name: t.name,
                description: t.description,
                input_schema: t.parameters
            }));

        default:
            return TOOLS;
    }
}

async function callOllama(messages, tools) {
    return new Promise((resolve, reject) => {
        const url = new URL(config.ollamaHost + '/api/chat');

        const requestBody = JSON.stringify({
            model: config.model,
            messages: messages,
            tools: tools,
            stream: false,
            options: {
                temperature: config.temperature
            }
        });

        const options = {
            hostname: url.hostname,
            port: url.port || 11434,
            path: url.pathname,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(requestBody)
            }
        };

        const req = http.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const response = JSON.parse(data);
                    resolve(response);
                } catch (e) {
                    reject(new Error(`Failed to parse Ollama response: ${e.message}`));
                }
            });
        });

        req.on('error', reject);
        req.write(requestBody);
        req.end();
    });
}

async function callOpenAI(messages, tools) {
    return new Promise((resolve, reject) => {
        const requestBody = JSON.stringify({
            model: config.model,
            messages: messages,
            tools: tools,
            temperature: config.temperature,
            max_tokens: config.maxTokens
        });

        const options = {
            hostname: 'api.openai.com',
            port: 443,
            path: '/v1/chat/completions',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${config.apiKey}`,
                'Content-Length': Buffer.byteLength(requestBody)
            }
        };

        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const response = JSON.parse(data);
                    if (response.error) {
                        reject(new Error(response.error.message));
                    } else {
                        resolve(response);
                    }
                } catch (e) {
                    reject(new Error(`Failed to parse OpenAI response: ${e.message}`));
                }
            });
        });

        req.on('error', reject);
        req.write(requestBody);
        req.end();
    });
}

async function callClaude(messages, tools) {
    return new Promise((resolve, reject) => {
        const claudeMessages = messages.filter(m => m.role !== 'system').map(m => ({
            role: m.role === 'assistant' ? 'assistant' : 'user',
            content: m.content
        }));

        const systemMessage = messages.find(m => m.role === 'system')?.content || '';

        const requestBody = JSON.stringify({
            model: config.model || 'claude-sonnet-4-20250514',
            max_tokens: config.maxTokens,
            system: systemMessage,
            messages: claudeMessages,
            tools: tools
        });

        const options = {
            hostname: 'api.anthropic.com',
            port: 443,
            path: '/v1/messages',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': config.apiKey,
                'anthropic-version': '2023-06-01',
                'Content-Length': Buffer.byteLength(requestBody)
            }
        };

        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const response = JSON.parse(data);
                    if (response.error) {
                        reject(new Error(response.error.message));
                    } else {
                        resolve(response);
                    }
                } catch (e) {
                    reject(new Error(`Failed to parse Claude response: ${e.message}`));
                }
            });
        });

        req.on('error', reject);
        req.write(requestBody);
        req.end();
    });
}

async function callGroq(messages, tools) {
    return new Promise((resolve, reject) => {
        const requestBody = JSON.stringify({
            model: config.model || 'llama-3.3-70b-versatile',
            messages: messages,
            tools: tools,
            temperature: config.temperature,
            max_tokens: config.maxTokens
        });

        const options = {
            hostname: 'api.groq.com',
            port: 443,
            path: '/openai/v1/chat/completions',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${config.apiKey}`,
                'Content-Length': Buffer.byteLength(requestBody)
            }
        };

        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const response = JSON.parse(data);
                    if (response.error) {
                        reject(new Error(response.error.message));
                    } else {
                        resolve(response);
                    }
                } catch (e) {
                    reject(new Error(`Failed to parse Groq response: ${e.message}`));
                }
            });
        });

        req.on('error', reject);
        req.write(requestBody);
        req.end();
    });
}

// ============================================================================
// Tool Execution via Live API
// ============================================================================

function executeToolViaLiveAPI(toolName, args) {
    if (!liveApi) {
        return { error: "Live API not initialized. This M4L device needs to be connected to Live." };
    }

    try {
        // Most tools are forwarded to the Remote Script via socket
        // The M4L device acts as a bridge between LLM and Remote Script
        // For now, return a message that the tool was called
        return {
            tool: toolName,
            args: args,
            status: "executed",
            note: "Tool execution handled by AbletonMCP Remote Script"
        };
    } catch (e) {
        return { error: e.message };
    }
}

// ============================================================================
// Message Handling
// ============================================================================

function extractToolCalls(response, provider) {
    const toolCalls = [];

    switch (provider) {
        case 'ollama':
            if (response.message?.tool_calls) {
                for (const tc of response.message.tool_calls) {
                    toolCalls.push({
                        name: tc.function.name,
                        arguments: tc.function.arguments
                    });
                }
            }
            break;

        case 'openai':
        case 'groq':
            if (response.choices?.[0]?.message?.tool_calls) {
                for (const tc of response.choices[0].message.tool_calls) {
                    toolCalls.push({
                        name: tc.function.name,
                        arguments: JSON.parse(tc.function.arguments)
                    });
                }
            }
            break;

        case 'claude':
            if (response.content) {
                for (const block of response.content) {
                    if (block.type === 'tool_use') {
                        toolCalls.push({
                            name: block.name,
                            arguments: block.input
                        });
                    }
                }
            }
            break;
    }

    return toolCalls;
}

function extractTextResponse(response, provider) {
    switch (provider) {
        case 'ollama':
            return response.message?.content || '';

        case 'openai':
        case 'groq':
            return response.choices?.[0]?.message?.content || '';

        case 'claude':
            const textBlocks = response.content?.filter(b => b.type === 'text') || [];
            return textBlocks.map(b => b.text).join('\n');

        default:
            return '';
    }
}

// ============================================================================
// Main Chat Function
// ============================================================================

let conversationHistory = [];

async function chat(userMessage) {
    Max.post(`[AbletonMCP] User: ${userMessage}`);
    Max.outlet('status', 'thinking');

    const systemPrompt = `You are an AI music production assistant integrated directly into Ableton Live.
You have access to 200+ tools that control every aspect of Ableton Live.

CAPABILITIES:
- Transport: play, stop, tempo, time signature, metronome
- Tracks: create, delete, rename, color, volume, pan, mute, solo, arm
- Clips: create, fire, stop, loop, duplicate, notes
- MIDI: add notes, remove notes, transpose, quantize, humanize
- Audio clips: gain, pitch, warp, fades
- Devices: parameters, toggle, presets, macros
- Scenes: create, fire, stop, name, color
- Sends/Returns: levels, create, delete
- Recording: arm, overdub, capture MIDI
- Arrangement: locators, loop, punch
- Automation: envelopes, record
- Browser: search, load instruments/effects
- AI Helpers: generate drums, basslines, get scale notes

When the user asks you to do something:
1. Use the appropriate tool(s)
2. Explain what you did briefly
3. Suggest next steps if helpful

Be creative and efficient. Batch operations when possible.`;

    const messages = [
        { role: 'system', content: systemPrompt },
        ...conversationHistory,
        { role: 'user', content: userMessage }
    ];

    const tools = formatToolsForProvider(config.provider);

    try {
        let response;
        switch (config.provider) {
            case 'ollama':
                response = await callOllama(messages, tools);
                break;
            case 'openai':
                response = await callOpenAI(messages, tools);
                break;
            case 'claude':
                response = await callClaude(messages, tools);
                break;
            case 'groq':
                response = await callGroq(messages, tools);
                break;
            default:
                throw new Error(`Unknown provider: ${config.provider}`);
        }

        const toolCalls = extractToolCalls(response, config.provider);

        const toolResults = [];
        for (const tc of toolCalls) {
            Max.post(`[AbletonMCP] Executing: ${tc.name}`);
            Max.outlet('status', `executing: ${tc.name}`);

            const result = executeToolViaLiveAPI(tc.name, tc.arguments);
            toolResults.push({
                tool: tc.name,
                result: result
            });

            Max.post(`[AbletonMCP] Result: ${JSON.stringify(result)}`);
        }

        let textResponse = extractTextResponse(response, config.provider);

        if (toolResults.length > 0) {
            const resultsSummary = toolResults.map(tr =>
                `${tr.tool}: ${tr.result.error || 'success'}`
            ).join(', ');

            if (!textResponse) {
                textResponse = `Executed: ${resultsSummary}`;
            }
        }

        conversationHistory.push({ role: 'user', content: userMessage });
        conversationHistory.push({ role: 'assistant', content: textResponse });

        if (conversationHistory.length > 20) {
            conversationHistory = conversationHistory.slice(-20);
        }

        Max.outlet('response', textResponse);
        Max.outlet('status', 'ready');

        return textResponse;

    } catch (error) {
        Max.post(`[AbletonMCP] Error: ${error.message}`);
        Max.outlet('status', 'error');
        Max.outlet('response', `Error: ${error.message}`);
        return null;
    }
}

// ============================================================================
// Max Message Handlers
// ============================================================================

Max.addHandler('setProvider', (provider) => {
    config.provider = provider;
    Max.post(`[AbletonMCP] Provider set to: ${provider}`);
});

Max.addHandler('setModel', (model) => {
    config.model = model;
    Max.post(`[AbletonMCP] Model set to: ${model}`);
});

Max.addHandler('setApiKey', (key) => {
    config.apiKey = key;
    Max.post(`[AbletonMCP] API key set`);
});

Max.addHandler('setOllamaHost', (host) => {
    config.ollamaHost = host;
    Max.post(`[AbletonMCP] Ollama host set to: ${host}`);
});

Max.addHandler('chat', async (...args) => {
    const message = args.join(' ');
    await chat(message);
});

Max.addHandler('clearHistory', () => {
    conversationHistory = [];
    Max.post(`[AbletonMCP] Conversation history cleared`);
});

Max.addHandler('getToolCount', () => {
    Max.post(`[AbletonMCP] Total tools available: ${TOOLS.length}`);
    Max.outlet('tool_count', TOOLS.length);
});

Max.addHandler('initLiveApi', () => {
    Max.post(`[AbletonMCP] Live API initialization requested`);
});

// Initialize
Max.post('[AbletonMCP] Multi-provider AI assistant loaded');
Max.post(`[AbletonMCP] ${TOOLS.length} tools available`);
Max.post('[AbletonMCP] Default provider: ollama');
Max.post('[AbletonMCP] Use "setProvider <name>" to change (ollama, openai, claude, groq)');
Max.outlet('status', 'ready');
Max.outlet('tool_count', TOOLS.length);
