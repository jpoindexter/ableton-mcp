# rest_api_server.py
"""
AbletonMCP REST API Server

This server exposes Ableton Live control as a REST API that can be used with:
- Ollama (via function calling)
- OpenAI API (via function calling)
- Claude API (via tool use)
- Any HTTP client

Run with: python rest_api_server.py
Or: uvicorn rest_api_server:app --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any
import socket
import json
import logging
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AbletonRESTAPI")

# ============================================================================
# Ableton Connection
# ============================================================================

class AbletonConnection:
    def __init__(self, host: str = "localhost", port: int = 9877):
        self.host = host
        self.port = port
        self.sock = None
        self._max_retries = 2

    def connect(self) -> bool:
        if self.sock:
            return True
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5.0)
            self.sock.connect((self.host, self.port))
            logger.info(f"Connected to Ableton at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Ableton: {str(e)}")
            self.sock = None
            return False

    def disconnect(self):
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None

    def _reconnect(self) -> bool:
        """Force a reconnection"""
        self.disconnect()
        return self.connect()

    def send_command(self, command_type: str, params: dict = None) -> dict:
        last_error = None

        for attempt in range(self._max_retries + 1):
            if not self.connect():
                if attempt < self._max_retries:
                    logger.warning(f"Connection failed, retrying ({attempt + 1}/{self._max_retries})")
                    continue
                raise HTTPException(
                    status_code=503,
                    detail="Could not connect to Ableton. Make sure Live is running with the AbletonMCP control surface enabled."
                )

            command = {"type": command_type, "params": params or {}}

            try:
                self.sock.sendall(json.dumps(command).encode('utf-8'))
                self.sock.settimeout(15.0)

                chunks = []
                while True:
                    try:
                        chunk = self.sock.recv(8192)
                        if not chunk:
                            break
                        chunks.append(chunk)
                        try:
                            json.loads(b''.join(chunks).decode('utf-8'))
                            break
                        except json.JSONDecodeError:
                            continue
                    except socket.timeout:
                        break

                if not chunks:
                    raise Exception("No response from Ableton")

                response_data = b''.join(chunks)
                response = json.loads(response_data.decode('utf-8'))

                if response.get("status") == "error":
                    error_msg = response.get("message", "Unknown error from Ableton")
                    raise HTTPException(status_code=400, detail=error_msg)

                return response.get("result", {})

            except HTTPException:
                raise
            except json.JSONDecodeError as e:
                last_error = f"Invalid response from Ableton: {str(e)}"
                self._reconnect()
            except Exception as e:
                last_error = str(e)
                self._reconnect()
                if attempt < self._max_retries:
                    logger.warning(f"Command failed, retrying ({attempt + 1}/{self._max_retries}): {last_error}")

        raise HTTPException(status_code=500, detail=f"Command failed after retries: {last_error}")


# Global connection
ableton = AbletonConnection()

# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="AbletonMCP REST API",
    description="REST API for controlling Ableton Live - works with Ollama, OpenAI, and other LLMs",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler for cleaner error responses
from fastapi.responses import JSONResponse
from fastapi import Request

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "detail": "An unexpected error occurred"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

# ============================================================================
# Request Models
# ============================================================================

class TempoRequest(BaseModel):
    tempo: float

    @field_validator('tempo')
    @classmethod
    def validate_tempo(cls, v):
        if not 20 <= v <= 300:
            raise ValueError('Tempo must be between 20 and 300 BPM')
        return v

class TrackRequest(BaseModel):
    track_index: int

class TrackCreateRequest(BaseModel):
    index: Optional[int] = -1
    name: Optional[str] = None

class TrackNameRequest(BaseModel):
    track_index: int
    name: str

class TrackBoolRequest(BaseModel):
    track_index: int
    value: bool

class TrackVolumeRequest(BaseModel):
    volume: float  # 0.0 to 1.0

    @field_validator('volume')
    @classmethod
    def validate_volume(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Volume must be between 0.0 and 1.0')
        return v

class TrackPanRequest(BaseModel):
    pan: float  # -1.0 to 1.0

    @field_validator('pan')
    @classmethod
    def validate_pan(cls, v):
        if not -1 <= v <= 1:
            raise ValueError('Pan must be between -1.0 and 1.0')
        return v

class TrackColorRequest(BaseModel):
    track_index: int
    color: int

class ClipRequest(BaseModel):
    track_index: int
    clip_index: int

class ClipCreateRequest(BaseModel):
    track_index: int
    clip_index: int
    length: Optional[float] = 4.0
    name: Optional[str] = None

class ClipNameRequest(BaseModel):
    track_index: int
    clip_index: int
    name: str

class ClipColorRequest(BaseModel):
    track_index: int
    clip_index: int
    color: int

class ClipLoopRequest(BaseModel):
    track_index: int
    clip_index: int
    loop_start: Optional[float] = None
    loop_end: Optional[float] = None
    looping: Optional[bool] = None

class ClipDuplicateRequest(BaseModel):
    track_index: int
    clip_index: int
    target_index: int

class Note(BaseModel):
    pitch: int
    start_time: float
    duration: float
    velocity: Optional[int] = 100

    @field_validator('pitch')
    @classmethod
    def validate_pitch(cls, v):
        if not 0 <= v <= 127:
            raise ValueError('Pitch must be between 0 and 127')
        return v

    @field_validator('velocity')
    @classmethod
    def validate_velocity(cls, v):
        if v is not None and not 0 <= v <= 127:
            raise ValueError('Velocity must be between 0 and 127')
        return v

    @field_validator('duration')
    @classmethod
    def validate_duration(cls, v):
        if v <= 0:
            raise ValueError('Duration must be positive')
        return v

class AddNotesRequest(BaseModel):
    track_index: int
    clip_index: int
    notes: List[Note]

class RemoveNotesRequest(BaseModel):
    track_index: int
    clip_index: int
    pitch: Optional[int] = -1
    start_time: float
    end_time: float

class TransposeRequest(BaseModel):
    track_index: int
    clip_index: int
    semitones: int

class SceneRequest(BaseModel):
    scene_index: int

class SceneCreateRequest(BaseModel):
    index: Optional[int] = -1
    name: Optional[str] = None

class SceneNameRequest(BaseModel):
    scene_index: int
    name: str

class DeviceRequest(BaseModel):
    track_index: int
    device_index: int

class DeviceToggleRequest(BaseModel):
    track_index: int
    device_index: int
    enabled: Optional[bool] = None

class DeviceParamRequest(BaseModel):
    track_index: int
    device_index: int
    parameter_index: int
    value: float

class SendLevelRequest(BaseModel):
    track_index: int
    send_index: int
    level: float

class ReturnVolumeRequest(BaseModel):
    return_index: int
    volume: float

class ReturnPanRequest(BaseModel):
    return_index: int
    pan: float

class MetronomeRequest(BaseModel):
    enabled: bool

class OverdubRequest(BaseModel):
    enabled: bool

class ArrangementLoopRequest(BaseModel):
    start: float
    end: float
    enabled: Optional[bool] = True

class JumpRequest(BaseModel):
    time: float

class LocatorRequest(BaseModel):
    time: float
    name: Optional[str] = None

class DeleteLocatorRequest(BaseModel):
    index: int

class ScaleRequest(BaseModel):
    root: str
    scale_type: str
    octave: Optional[int] = 4

class QuantizeRequest(BaseModel):
    grid: float = 0.25  # Grid size in beats (0.25 = 16th notes, 0.5 = 8th, 1.0 = quarter)
    strength: Optional[float] = 1.0

class HumanizeTimingRequest(BaseModel):
    amount: float

class HumanizeVelocityRequest(BaseModel):
    amount: float

class DrumPatternRequest(BaseModel):
    track_index: int  # Target track index
    clip_index: int   # Target clip slot index
    style: str = "basic"  # Pattern style: basic, house, techno, breakbeat
    length: float = 4.0   # Length in beats

class BasslineRequest(BaseModel):
    track_index: int  # Target track index
    clip_index: int   # Target clip slot index
    root: int = 36    # Root note as MIDI number (36 = C1)
    scale_type: str = "minor"  # Scale type: major, minor, dorian, etc.
    length: float = 4.0  # Length in beats

class BrowserRequest(BaseModel):
    path: Optional[str] = None

class LoadItemRequest(BaseModel):
    track_index: int
    uri: str

class RoutingRequest(BaseModel):
    track_index: int
    routing_type: str
    channel: str

# ============================================================================
# API Endpoints
# ============================================================================

# Health & Info
@app.get("/")
def root():
    return {"status": "ok", "service": "AbletonMCP REST API"}

@app.get("/health")
def health():
    try:
        result = ableton.send_command("get_session_info")
        return {"status": "connected", "ableton": result}
    except Exception as e:
        return {"status": "disconnected", "error": str(e)}

@app.get("/tools")
def get_tools():
    """Return OpenAI/Ollama compatible tool definitions"""
    return {"tools": TOOL_DEFINITIONS}

# Transport & Session
@app.get("/api/session")
def get_session_info():
    return ableton.send_command("get_session_info")

@app.post("/api/tempo")
def set_tempo(req: TempoRequest):
    return ableton.send_command("set_tempo", {"tempo": req.tempo})

@app.post("/api/transport/play")
def start_playback():
    return ableton.send_command("start_playback")

@app.post("/api/transport/stop")
def stop_playback():
    return ableton.send_command("stop_playback")

@app.post("/api/undo")
def undo():
    return ableton.send_command("undo")

@app.post("/api/redo")
def redo():
    return ableton.send_command("redo")

@app.get("/api/metronome")
def get_metronome():
    return ableton.send_command("get_metronome_state")

@app.post("/api/metronome")
def set_metronome(req: MetronomeRequest):
    return ableton.send_command("set_metronome", {"enabled": req.enabled})

# Tracks
@app.get("/api/tracks/{track_index}")
def get_track_info(track_index: int):
    return ableton.send_command("get_track_info", {"track_index": track_index})

@app.post("/api/tracks/midi")
def create_midi_track(req: TrackCreateRequest):
    return ableton.send_command("create_midi_track", {"index": req.index, "name": req.name})

@app.post("/api/tracks/audio")
def create_audio_track(req: TrackCreateRequest):
    return ableton.send_command("create_audio_track", {"index": req.index, "name": req.name})

@app.delete("/api/tracks/{track_index}")
def delete_track(track_index: int):
    return ableton.send_command("delete_track", {"track_index": track_index})

@app.post("/api/tracks/{track_index}/duplicate")
def duplicate_track(track_index: int):
    return ableton.send_command("duplicate_track", {"track_index": track_index})

@app.put("/api/tracks/{track_index}/name")
def set_track_name(track_index: int, req: TrackNameRequest):
    return ableton.send_command("set_track_name", {"track_index": track_index, "name": req.name})

@app.put("/api/tracks/{track_index}/color")
def set_track_color(track_index: int, req: TrackColorRequest):
    return ableton.send_command("set_track_color", {"track_index": track_index, "color": req.color})

@app.put("/api/tracks/{track_index}/mute")
def set_track_mute(track_index: int, req: TrackBoolRequest):
    return ableton.send_command("set_track_mute", {"track_index": track_index, "mute": req.value})

@app.put("/api/tracks/{track_index}/solo")
def set_track_solo(track_index: int, req: TrackBoolRequest):
    return ableton.send_command("set_track_solo", {"track_index": track_index, "solo": req.value})

@app.put("/api/tracks/{track_index}/arm")
def set_track_arm(track_index: int, req: TrackBoolRequest):
    return ableton.send_command("set_track_arm", {"track_index": track_index, "arm": req.value})

@app.put("/api/tracks/{track_index}/volume")
def set_track_volume(track_index: int, req: TrackVolumeRequest):
    return ableton.send_command("set_track_volume", {"track_index": track_index, "volume": req.volume})

@app.put("/api/tracks/{track_index}/pan")
def set_track_pan(track_index: int, req: TrackPanRequest):
    return ableton.send_command("set_track_pan", {"track_index": track_index, "pan": req.pan})

# Clips
@app.get("/api/tracks/{track_index}/clips/{clip_index}")
def get_clip_info(track_index: int, clip_index: int):
    return ableton.send_command("get_clip_info", {"track_index": track_index, "clip_index": clip_index})

@app.post("/api/tracks/{track_index}/clips/{clip_index}")
def create_clip(track_index: int, clip_index: int, req: ClipCreateRequest):
    return ableton.send_command("create_clip", {
        "track_index": track_index,
        "clip_index": clip_index,
        "length": req.length,
        "name": req.name
    })

@app.delete("/api/tracks/{track_index}/clips/{clip_index}")
def delete_clip(track_index: int, clip_index: int):
    return ableton.send_command("delete_clip", {"track_index": track_index, "clip_index": clip_index})

@app.post("/api/tracks/{track_index}/clips/{clip_index}/fire")
def fire_clip(track_index: int, clip_index: int):
    return ableton.send_command("fire_clip", {"track_index": track_index, "clip_index": clip_index})

@app.post("/api/tracks/{track_index}/clips/{clip_index}/stop")
def stop_clip(track_index: int, clip_index: int):
    return ableton.send_command("stop_clip", {"track_index": track_index, "clip_index": clip_index})

@app.post("/api/tracks/{track_index}/clips/{clip_index}/duplicate")
def duplicate_clip(track_index: int, clip_index: int, req: ClipDuplicateRequest):
    return ableton.send_command("duplicate_clip", {
        "track_index": track_index,
        "clip_index": clip_index,
        "target_index": req.target_index
    })

# Notes
@app.get("/api/tracks/{track_index}/clips/{clip_index}/notes")
def get_clip_notes(track_index: int, clip_index: int):
    return ableton.send_command("get_clip_notes", {"track_index": track_index, "clip_index": clip_index})

@app.post("/api/tracks/{track_index}/clips/{clip_index}/notes")
def add_notes(track_index: int, clip_index: int, req: AddNotesRequest):
    notes = [{"pitch": n.pitch, "start_time": n.start_time, "duration": n.duration, "velocity": n.velocity} for n in req.notes]
    return ableton.send_command("add_notes_to_clip", {
        "track_index": track_index,
        "clip_index": clip_index,
        "notes": notes
    })

@app.delete("/api/tracks/{track_index}/clips/{clip_index}/notes")
def remove_all_notes(track_index: int, clip_index: int):
    return ableton.send_command("remove_all_notes", {"track_index": track_index, "clip_index": clip_index})

@app.post("/api/tracks/{track_index}/clips/{clip_index}/transpose")
def transpose_notes(track_index: int, clip_index: int, req: TransposeRequest):
    return ableton.send_command("transpose_notes", {
        "track_index": track_index,
        "clip_index": clip_index,
        "semitones": req.semitones
    })

# Scenes
@app.get("/api/scenes")
def get_all_scenes():
    return ableton.send_command("get_all_scenes")

@app.post("/api/scenes")
def create_scene(req: SceneCreateRequest):
    return ableton.send_command("create_scene", {"index": req.index, "name": req.name})

@app.delete("/api/scenes/{scene_index}")
def delete_scene(scene_index: int):
    return ableton.send_command("delete_scene", {"scene_index": scene_index})

@app.post("/api/scenes/{scene_index}/fire")
def fire_scene(scene_index: int):
    return ableton.send_command("fire_scene", {"scene_index": scene_index})

@app.post("/api/scenes/{scene_index}/stop")
def stop_scene(scene_index: int):
    return ableton.send_command("stop_scene", {"scene_index": scene_index})

@app.post("/api/scenes/{scene_index}/duplicate")
def duplicate_scene(scene_index: int):
    return ableton.send_command("duplicate_scene", {"scene_index": scene_index})

# Devices
@app.get("/api/tracks/{track_index}/devices/{device_index}")
def get_device_parameters(track_index: int, device_index: int):
    return ableton.send_command("get_device_parameters", {"track_index": track_index, "device_index": device_index})

@app.put("/api/tracks/{track_index}/devices/{device_index}/parameter")
def set_device_parameter(track_index: int, device_index: int, req: DeviceParamRequest):
    return ableton.send_command("set_device_parameter", {
        "track_index": track_index,
        "device_index": device_index,
        "parameter_index": req.parameter_index,
        "value": req.value
    })

@app.put("/api/tracks/{track_index}/devices/{device_index}/toggle")
def toggle_device(track_index: int, device_index: int, req: DeviceToggleRequest):
    return ableton.send_command("toggle_device", {
        "track_index": track_index,
        "device_index": device_index,
        "enabled": req.enabled
    })

@app.delete("/api/tracks/{track_index}/devices/{device_index}")
def delete_device(track_index: int, device_index: int):
    return ableton.send_command("delete_device", {"track_index": track_index, "device_index": device_index})

# Return Tracks
@app.get("/api/returns")
def get_return_tracks():
    return ableton.send_command("get_return_tracks")

@app.post("/api/tracks/{track_index}/sends/{send_index}")
def set_send_level(track_index: int, send_index: int, req: SendLevelRequest):
    return ableton.send_command("set_send_level", {
        "track_index": track_index,
        "send_index": send_index,
        "level": req.level
    })

@app.put("/api/returns/{return_index}/volume")
def set_return_volume(return_index: int, req: ReturnVolumeRequest):
    return ableton.send_command("set_return_volume", {"return_index": return_index, "volume": req.volume})

# Recording
@app.post("/api/recording/start")
def start_recording():
    return ableton.send_command("start_recording")

@app.post("/api/recording/stop")
def stop_recording():
    return ableton.send_command("stop_recording")

@app.post("/api/recording/capture")
def capture_midi():
    return ableton.send_command("capture_midi")

@app.post("/api/recording/overdub")
def set_overdub(req: OverdubRequest):
    return ableton.send_command("set_overdub", {"enabled": req.enabled})

# AI Music Helpers
NOTE_TO_MIDI = {"C": 0, "C#": 1, "DB": 1, "D": 2, "D#": 3, "EB": 3, "E": 4, "F": 5,
                "F#": 6, "GB": 6, "G": 7, "G#": 8, "AB": 8, "A": 9, "A#": 10, "BB": 10, "B": 11}

@app.get("/api/music/scale")
def get_scale_notes(root: str, scale_type: str, octave: int = 4):
    # Convert string root to MIDI note number
    root_upper = root.upper().replace("♯", "#").replace("♭", "B")
    root_midi = NOTE_TO_MIDI.get(root_upper, 0) + (octave * 12)
    return ableton.send_command("get_scale_notes", {"root": root_midi, "scale_type": scale_type})

@app.post("/api/tracks/{track_index}/clips/{clip_index}/quantize")
def quantize_clip(track_index: int, clip_index: int, req: QuantizeRequest):
    return ableton.send_command("quantize_clip_notes", {
        "track_index": track_index,
        "clip_index": clip_index,
        "grid": req.grid,
        "strength": req.strength
    })

@app.post("/api/tracks/{track_index}/clips/{clip_index}/humanize/timing")
def humanize_timing(track_index: int, clip_index: int, req: HumanizeTimingRequest):
    return ableton.send_command("humanize_clip_timing", {
        "track_index": track_index,
        "clip_index": clip_index,
        "amount": req.amount
    })

@app.post("/api/tracks/{track_index}/clips/{clip_index}/humanize/velocity")
def humanize_velocity(track_index: int, clip_index: int, req: HumanizeVelocityRequest):
    return ableton.send_command("humanize_clip_velocity", {
        "track_index": track_index,
        "clip_index": clip_index,
        "amount": req.amount
    })

@app.post("/api/music/drums")
def generate_drum_pattern(req: DrumPatternRequest):
    return ableton.send_command("generate_drum_pattern", {
        "track_index": req.track_index,
        "clip_index": req.clip_index,
        "style": req.style,
        "length": req.length
    })

@app.post("/api/music/bassline")
def generate_bassline(req: BasslineRequest):
    return ableton.send_command("generate_bassline", {
        "track_index": req.track_index,
        "clip_index": req.clip_index,
        "root": req.root,
        "scale_type": req.scale_type,
        "length": req.length
    })

# ============================================================================
# Master Track Control
# ============================================================================

class MasterVolumeRequest(BaseModel):
    volume: float

    @field_validator('volume')
    @classmethod
    def validate_volume(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Volume must be between 0.0 and 1.0')
        return v

class MasterPanRequest(BaseModel):
    pan: float

    @field_validator('pan')
    @classmethod
    def validate_pan(cls, v):
        if not -1 <= v <= 1:
            raise ValueError('Pan must be between -1.0 and 1.0')
        return v

@app.get("/api/master")
def get_master_info():
    """Get master track information including volume, pan, and devices"""
    return ableton.send_command("get_master_info")

@app.post("/api/master/volume")
def set_master_volume(req: MasterVolumeRequest):
    """Set master track volume (0.0 to 1.0)"""
    return ableton.send_command("set_master_volume", {"volume": req.volume})

@app.post("/api/master/pan")
def set_master_pan(req: MasterPanRequest):
    """Set master track pan (-1.0 to 1.0)"""
    return ableton.send_command("set_master_pan", {"pan": req.pan})

# ============================================================================
# Browser
# ============================================================================

class BrowsePathRequest(BaseModel):
    path: List[str]  # e.g. ["Audio Effects", "EQ Eight"]

class BrowserSearchRequest(BaseModel):
    query: str
    category: str = "all"  # all, instruments, sounds, drums, audio_effects, midi_effects

class BrowserChildrenRequest(BaseModel):
    uri: str

class LoadItemToTrackRequest(BaseModel):
    track_index: int
    uri: str

class LoadItemToReturnRequest(BaseModel):
    return_index: int
    uri: str

@app.post("/api/browser/browse")
def browse_path(req: BrowsePathRequest):
    """Navigate browser by path list"""
    return ableton.send_command("browse_path", {"path": req.path})

@app.post("/api/browser/search")
def search_browser(req: BrowserSearchRequest):
    """Search browser for items matching query"""
    return ableton.send_command("search_browser", {
        "query": req.query,
        "category": req.category
    })

@app.post("/api/browser/children")
def get_browser_children(req: BrowserChildrenRequest):
    """Get children of a browser item by URI"""
    return ableton.send_command("get_browser_children", {"uri": req.uri})

@app.post("/api/browser/load")
def load_item_to_track(req: LoadItemToTrackRequest):
    """Load a browser item onto a track"""
    return ableton.send_command("load_instrument_or_effect", {
        "track_index": req.track_index,
        "uri": req.uri
    })

@app.post("/api/browser/load-to-return")
def load_item_to_return(req: LoadItemToReturnRequest):
    """Load a browser item onto a return track"""
    return ableton.send_command("load_browser_item_to_return", {
        "return_index": req.return_index,
        "item_uri": req.uri
    })

# ============================================================================
# Generic Command Endpoint (for Ollama function calling)
# ============================================================================

class GenericCommand(BaseModel):
    command: str
    params: Optional[Dict[str, Any]] = None

@app.post("/api/command")
def execute_command(cmd: GenericCommand):
    """
    Generic command endpoint for LLM function calling.
    Allows executing any Ableton command by name.
    """
    return ableton.send_command(cmd.command, cmd.params)

# ============================================================================
# Tool Definitions for LLMs
# ============================================================================

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "ableton_command",
            "description": "Execute a command in Ableton Live. Available commands: get_session_info, set_tempo, start_playback, stop_playback, undo, redo, create_midi_track, create_audio_track, delete_track, duplicate_track, set_track_name, set_track_mute, set_track_solo, set_track_arm, create_clip, delete_clip, fire_clip, stop_clip, add_notes_to_clip, remove_all_notes, transpose_notes, get_all_scenes, create_scene, delete_scene, fire_scene, duplicate_scene, get_device_parameters, set_device_parameter, toggle_device, delete_device, get_return_tracks, set_send_level, start_recording, stop_recording, capture_midi, get_scale_notes, quantize_clip_notes, humanize_clip_timing, humanize_clip_velocity, generate_drum_pattern, generate_bassline",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command to execute"
                    },
                    "params": {
                        "type": "object",
                        "description": "Parameters for the command"
                    }
                },
                "required": ["command"]
            }
        }
    }
]

# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("AbletonMCP REST API Server")
    print("=" * 60)
    print("Endpoints:")
    print("  - Health:     GET  http://localhost:8000/health")
    print("  - Tools:      GET  http://localhost:8000/tools")
    print("  - Command:    POST http://localhost:8000/api/command")
    print("  - API Docs:   GET  http://localhost:8000/docs")
    print("")
    print("For Ollama integration, use the /api/command endpoint")
    print("with function calling.")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
