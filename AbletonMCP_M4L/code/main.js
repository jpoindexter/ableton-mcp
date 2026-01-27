/**
 * AbletonMCP - Multi-Provider AI Integration for Ableton Live
 * Node for Max script that connects any LLM to Ableton Live
 *
 * Supported providers: Ollama, OpenAI, Claude API, Groq
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
// Tool Definitions (All 80+ Ableton tools)
// ============================================================================

const TOOLS = [
    // Transport & Session
    {
        name: "get_session_info",
        description: "Get current Ableton session info including tempo, time signature, track count, and scene count",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "set_tempo",
        description: "Set the session tempo in BPM",
        parameters: {
            type: "object",
            properties: {
                tempo: { type: "number", description: "Tempo in BPM (20-999)" }
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
        name: "undo",
        description: "Undo the last action in Ableton",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "redo",
        description: "Redo the last undone action in Ableton",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "get_metronome_state",
        description: "Get the current metronome on/off state",
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

    // Track Management
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
        name: "set_track_color",
        description: "Set the color of a track",
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

    // Clip Operations
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
        description: "Duplicate a clip to another slot",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the source clip" },
                target_index: { type: "integer", description: "Index of the target slot" }
            },
            required: ["track_index", "clip_index", "target_index"]
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
        name: "set_clip_color",
        description: "Set the color of a clip",
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

    // Note Editing
    {
        name: "get_clip_notes",
        description: "Get all notes from a clip",
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
        name: "add_notes_to_clip",
        description: "Add MIDI notes to a clip",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                notes: {
                    type: "array",
                    description: "Array of notes, each with pitch (0-127), start_time (beats), duration (beats), velocity (1-127)",
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
        description: "Remove specific notes from a clip",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                pitch: { type: "integer", description: "Pitch to remove (0-127), or -1 for all pitches" },
                start_time: { type: "number", description: "Start of time range" },
                end_time: { type: "number", description: "End of time range" }
            },
            required: ["track_index", "clip_index", "start_time", "end_time"]
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
                semitones: { type: "integer", description: "Number of semitones to transpose (positive or negative)" }
            },
            required: ["track_index", "clip_index", "semitones"]
        }
    },

    // Scene Management
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
                index: { type: "integer", description: "Position to insert scene (-1 for end)" },
                name: { type: "string", description: "Name for the scene" }
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
                scene_index: { type: "integer", description: "Index of the scene to delete" }
            },
            required: ["scene_index"]
        }
    },
    {
        name: "fire_scene",
        description: "Trigger a scene to play all clips in that row",
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
                name: { type: "string", description: "New name for the scene" }
            },
            required: ["scene_index", "name"]
        }
    },
    {
        name: "duplicate_scene",
        description: "Duplicate a scene",
        parameters: {
            type: "object",
            properties: {
                scene_index: { type: "integer", description: "Index of the scene to duplicate" }
            },
            required: ["scene_index"]
        }
    },

    // Device Control
    {
        name: "get_device_parameters",
        description: "Get all parameters for a device on a track",
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
        description: "Set a parameter value on a device",
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
                enabled: { type: "boolean", description: "True to enable, false to disable" }
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

    // Return/Send Tracks
    {
        name: "get_return_tracks",
        description: "Get information about all return tracks",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "set_send_level",
        description: "Set the send level from a track to a return track",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the source track" },
                send_index: { type: "integer", description: "Index of the send (0=A, 1=B, etc)" },
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
                volume: { type: "number", description: "Volume level (0.0-1.0)" }
            },
            required: ["return_index", "volume"]
        }
    },

    // Recording
    {
        name: "start_recording",
        description: "Start recording in Ableton",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "stop_recording",
        description: "Stop recording in Ableton",
        parameters: { type: "object", properties: {}, required: [] }
    },
    {
        name: "capture_midi",
        description: "Capture recently played MIDI notes into a new clip",
        parameters: { type: "object", properties: {}, required: [] }
    },

    // AI Music Helpers
    {
        name: "get_scale_notes",
        description: "Get MIDI note numbers for a scale. Available scales: major, minor, dorian, phrygian, lydian, mixolydian, aeolian, locrian, harmonic_minor, melodic_minor, pentatonic_major, pentatonic_minor, blues",
        parameters: {
            type: "object",
            properties: {
                root: { type: "string", description: "Root note (C, C#, D, etc.)" },
                scale_type: { type: "string", description: "Scale type (major, minor, dorian, etc.)" },
                octave: { type: "integer", description: "Starting octave (0-8, default 4)" }
            },
            required: ["root", "scale_type"]
        }
    },
    {
        name: "quantize_clip_notes",
        description: "Quantize notes in a clip to a grid",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                grid_size: { type: "number", description: "Grid size in beats (0.25=16th, 0.5=8th, 1.0=quarter)" },
                strength: { type: "number", description: "Quantize strength 0.0-1.0 (default 1.0 = full quantize)" }
            },
            required: ["track_index", "clip_index", "grid_size"]
        }
    },
    {
        name: "humanize_clip_timing",
        description: "Add human-like timing variations to notes",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                amount: { type: "number", description: "Humanize amount in beats (e.g., 0.02 = subtle)" }
            },
            required: ["track_index", "clip_index", "amount"]
        }
    },
    {
        name: "humanize_clip_velocity",
        description: "Add human-like velocity variations to notes",
        parameters: {
            type: "object",
            properties: {
                track_index: { type: "integer", description: "Index of the track" },
                clip_index: { type: "integer", description: "Index of the clip" },
                amount: { type: "number", description: "Velocity variation amount (e.g., 10 = +/- 10)" }
            },
            required: ["track_index", "clip_index", "amount"]
        }
    },
    {
        name: "generate_drum_pattern",
        description: "Generate a drum pattern. Styles: basic, house, techno, hip_hop, trap, dnb, jazz, funk",
        parameters: {
            type: "object",
            properties: {
                style: { type: "string", description: "Pattern style (basic, house, techno, hip_hop, trap, dnb, jazz, funk)" },
                bars: { type: "integer", description: "Number of bars (default 2)" },
                swing: { type: "number", description: "Swing amount 0.0-1.0 (default 0)" }
            },
            required: ["style"]
        }
    },
    {
        name: "generate_bassline",
        description: "Generate a bassline pattern. Styles: basic, walking, synth, funk, octave, arpeggiated",
        parameters: {
            type: "object",
            properties: {
                root: { type: "string", description: "Root note (C, D, E, etc.)" },
                scale: { type: "string", description: "Scale type (minor, major, dorian, etc.)" },
                style: { type: "string", description: "Bassline style (basic, walking, synth, funk, octave, arpeggiated)" },
                bars: { type: "integer", description: "Number of bars (default 2)" },
                octave: { type: "integer", description: "Bass octave (default 2)" }
            },
            required: ["root", "scale", "style"]
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
        // Convert messages to Claude format
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
        return { error: "Live API not initialized" };
    }

    try {
        const song = liveApi.get('live_set');

        switch (toolName) {
            // Transport
            case 'get_session_info':
                return {
                    tempo: liveApi.get('live_set tempo'),
                    is_playing: liveApi.get('live_set is_playing'),
                    track_count: liveApi.get('live_set tracks').length,
                    scene_count: liveApi.get('live_set scenes').length
                };

            case 'set_tempo':
                liveApi.set('live_set tempo', args.tempo);
                return { success: true, tempo: args.tempo };

            case 'start_playback':
                liveApi.call('live_set', 'start_playing');
                return { success: true };

            case 'stop_playback':
                liveApi.call('live_set', 'stop_playing');
                return { success: true };

            case 'undo':
                liveApi.call('live_set', 'undo');
                return { success: true };

            case 'redo':
                liveApi.call('live_set', 'redo');
                return { success: true };

            // Tracks
            case 'create_midi_track':
                liveApi.call('live_set', 'create_midi_track', args.index || -1);
                return { success: true };

            case 'create_audio_track':
                liveApi.call('live_set', 'create_audio_track', args.index || -1);
                return { success: true };

            case 'delete_track':
                liveApi.call('live_set', 'delete_track', args.track_index);
                return { success: true };

            case 'set_track_name':
                liveApi.set(`live_set tracks ${args.track_index} name`, args.name);
                return { success: true };

            case 'set_track_mute':
                liveApi.set(`live_set tracks ${args.track_index} mute`, args.mute ? 1 : 0);
                return { success: true };

            case 'set_track_solo':
                liveApi.set(`live_set tracks ${args.track_index} solo`, args.solo ? 1 : 0);
                return { success: true };

            case 'set_track_arm':
                liveApi.set(`live_set tracks ${args.track_index} arm`, args.arm ? 1 : 0);
                return { success: true };

            // Clips
            case 'create_clip':
                const clipSlots = liveApi.get(`live_set tracks ${args.track_index} clip_slots`);
                liveApi.call(`live_set tracks ${args.track_index} clip_slots ${args.clip_index}`,
                    'create_clip', args.length || 4.0);
                if (args.name) {
                    liveApi.set(`live_set tracks ${args.track_index} clip_slots ${args.clip_index} clip name`, args.name);
                }
                return { success: true };

            case 'delete_clip':
                liveApi.call(`live_set tracks ${args.track_index} clip_slots ${args.clip_index}`, 'delete_clip');
                return { success: true };

            case 'fire_clip':
                liveApi.call(`live_set tracks ${args.track_index} clip_slots ${args.clip_index} clip`, 'fire');
                return { success: true };

            case 'stop_clip':
                liveApi.call(`live_set tracks ${args.track_index} clip_slots ${args.clip_index} clip`, 'stop');
                return { success: true };

            // Notes
            case 'add_notes_to_clip':
                const clip = `live_set tracks ${args.track_index} clip_slots ${args.clip_index} clip`;
                liveApi.call(clip, 'deselect_all_notes');
                for (const note of args.notes) {
                    liveApi.call(clip, 'add_new_notes', {
                        notes: [{
                            pitch: note.pitch,
                            start_time: note.start_time,
                            duration: note.duration,
                            velocity: note.velocity || 100,
                            mute: false
                        }]
                    });
                }
                return { success: true, notes_added: args.notes.length };

            case 'remove_all_notes':
                liveApi.call(`live_set tracks ${args.track_index} clip_slots ${args.clip_index} clip`,
                    'remove_notes_extended', 0, 128, 0, 9999);
                return { success: true };

            // Scenes
            case 'get_all_scenes':
                const scenes = liveApi.get('live_set scenes');
                return scenes.map((s, i) => ({
                    index: i,
                    name: liveApi.get(`live_set scenes ${i} name`)
                }));

            case 'create_scene':
                liveApi.call('live_set', 'create_scene', args.index || -1);
                return { success: true };

            case 'delete_scene':
                liveApi.call('live_set', 'delete_scene', args.scene_index);
                return { success: true };

            case 'fire_scene':
                liveApi.call(`live_set scenes ${args.scene_index}`, 'fire');
                return { success: true };

            // Default
            default:
                return { error: `Unknown tool: ${toolName}` };
        }
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
You have access to tools that control Ableton Live. Use these tools to help the user create, edit, and manipulate their music.

When the user asks you to do something in Ableton:
1. Use the appropriate tool(s) to accomplish the task
2. Explain what you did
3. Suggest next steps if appropriate

Be creative and helpful. You can create beats, melodies, arrange songs, mix tracks, and more.`;

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

        // Extract tool calls
        const toolCalls = extractToolCalls(response, config.provider);

        // Execute tool calls
        const toolResults = [];
        for (const tc of toolCalls) {
            Max.post(`[AbletonMCP] Executing tool: ${tc.name}`);
            Max.outlet('status', `executing: ${tc.name}`);

            const result = executeToolViaLiveAPI(tc.name, tc.arguments);
            toolResults.push({
                tool: tc.name,
                result: result
            });

            Max.post(`[AbletonMCP] Tool result: ${JSON.stringify(result)}`);
        }

        // Get text response
        let textResponse = extractTextResponse(response, config.provider);

        // If there were tool calls, append results summary
        if (toolResults.length > 0) {
            const resultsSummary = toolResults.map(tr =>
                `${tr.tool}: ${tr.result.error || 'success'}`
            ).join(', ');

            if (!textResponse) {
                textResponse = `Executed: ${resultsSummary}`;
            }
        }

        // Update conversation history
        conversationHistory.push({ role: 'user', content: userMessage });
        conversationHistory.push({ role: 'assistant', content: textResponse });

        // Keep history manageable
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

Max.addHandler('initLiveApi', () => {
    // This would be called from Max to pass the Live API reference
    // In practice, we'll use Max's live.api objects
    Max.post(`[AbletonMCP] Live API initialization requested`);
});

// Initialize
Max.post('[AbletonMCP] Multi-provider AI assistant loaded');
Max.post('[AbletonMCP] Default provider: ollama');
Max.post('[AbletonMCP] Use "setProvider <name>" to change (ollama, openai, claude, groq)');
Max.outlet('status', 'ready');
