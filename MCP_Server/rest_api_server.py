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
from pydantic import BaseModel, field_validator, Field
from typing import Optional, List, Dict, Any
import socket
import json
import logging
import uvicorn
import threading
import os

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AbletonRESTAPI")

# ============================================================================
# Configuration (can be overridden via environment variables)
# ============================================================================

ABLETON_HOST = os.environ.get("ABLETON_HOST", "localhost")
ABLETON_PORT = int(os.environ.get("ABLETON_PORT", "9877"))
MAX_RETRIES = int(os.environ.get("ABLETON_MAX_RETRIES", "2"))
CONNECT_TIMEOUT = float(os.environ.get("ABLETON_CONNECT_TIMEOUT", "5.0"))
RECV_TIMEOUT = float(os.environ.get("ABLETON_RECV_TIMEOUT", "15.0"))
MAX_BUFFER_SIZE = int(os.environ.get("ABLETON_MAX_BUFFER", "1048576"))  # 1MB max

# Command whitelist for security
ALLOWED_COMMANDS = {
    # Transport
    "health_check", "start_playback", "stop_playback", "get_playback_position",
    "get_session_info", "set_tempo", "undo", "redo",
    # Tracks
    "create_midi_track", "create_audio_track", "delete_track", "duplicate_track",
    "get_track_info", "set_track_name", "set_track_mute", "set_track_solo",
    "set_track_arm", "set_track_volume", "set_track_pan", "set_track_color",
    "select_track", "get_track_input_routing", "get_track_output_routing",
    "set_track_input_routing", "set_track_output_routing",
    "get_available_inputs", "get_available_outputs",
    "set_track_monitoring", "get_track_monitoring",
    # Clips
    "create_clip", "delete_clip", "fire_clip", "stop_clip", "duplicate_clip",
    "get_clip_info", "get_clip_notes", "set_clip_name", "set_clip_color",
    "set_clip_loop", "add_notes_to_clip", "remove_notes", "remove_all_notes",
    "transpose_notes", "select_clip",
    # Audio clip editing
    "set_clip_gain", "set_clip_pitch", "set_clip_warp_mode", "get_clip_warp_info",
    # Scenes
    "get_all_scenes", "create_scene", "delete_scene", "fire_scene", "stop_scene",
    "duplicate_scene", "set_scene_name", "set_scene_color", "select_scene",
    # Devices
    "get_device_parameters", "set_device_parameter", "toggle_device", "delete_device",
    "get_device_by_name", "load_device_preset",
    # Rack chains
    "get_rack_chains", "select_rack_chain", "create_rack_chain", "delete_rack_chain",
    # Browser
    "browse_path", "get_browser_children", "search_browser", "get_browser_tree",
    "get_browser_items_at_path", "load_browser_item", "load_instrument_or_effect",
    "load_browser_item_to_return",
    # Return tracks
    "get_return_tracks", "get_return_track_info", "set_send_level",
    "set_return_volume", "set_return_pan",
    # Master track
    "get_master_info", "set_master_volume", "set_master_pan",
    # Recording
    "start_recording", "stop_recording", "toggle_session_record",
    "toggle_arrangement_record", "set_overdub", "capture_midi",
    # Arrangement
    "get_arrangement_length", "set_arrangement_loop", "jump_to_time",
    "get_locators", "create_locator", "delete_locator",
    # View
    "get_current_view", "focus_view",
    # Session info
    "get_session_path", "is_session_modified", "get_cpu_load",
    "get_metronome_state", "set_metronome",
    # AI helpers
    "get_scale_notes", "quantize_clip_notes", "humanize_clip_timing",
    "humanize_clip_velocity", "generate_drum_pattern", "generate_bassline",
    # Automation
    "get_clip_automation", "set_clip_automation", "clear_clip_automation",
    # Group tracks
    "create_group_track", "ungroup_tracks", "fold_track", "unfold_track",
    # Groove
    "get_groove_pool", "apply_groove", "commit_groove",
}

# ============================================================================
# Ableton Connection (Thread-Safe)
# ============================================================================

class AbletonConnection:
    def __init__(self, host: str = ABLETON_HOST, port: int = ABLETON_PORT):
        self.host = host
        self.port = port
        self.sock = None
        self._max_retries = MAX_RETRIES
        self._lock = threading.Lock()  # Thread safety

    def connect(self) -> bool:
        """Connect to Ableton (must be called within lock)"""
        if self.sock:
            return True
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(CONNECT_TIMEOUT)
            self.sock.connect((self.host, self.port))
            logger.info(f"Connected to Ableton at {self.host}:{self.port}")
            return True
        except socket.error as e:
            logger.error(f"Socket error connecting to Ableton: {str(e)}")
            if self.sock:
                try:
                    self.sock.close()
                except socket.error:
                    pass
            self.sock = None
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to Ableton: {str(e)}")
            if self.sock:
                try:
                    self.sock.close()
                except socket.error:
                    pass
            self.sock = None
            return False

    def disconnect(self):
        """Disconnect from Ableton (must be called within lock)"""
        if self.sock:
            try:
                self.sock.close()
            except socket.error as e:
                logger.warning(f"Error closing socket: {str(e)}")
            finally:
                self.sock = None

    def _reconnect(self) -> bool:
        """Force a reconnection (must be called within lock)"""
        self.disconnect()
        return self.connect()

    def send_command(self, command_type: str, params: dict = None) -> dict:
        """Send command to Ableton (thread-safe with validation)"""

        # Validate command is allowed
        if command_type not in ALLOWED_COMMANDS:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown command: {command_type}. Use /api/commands to see available commands."
            )

        last_error = None

        with self._lock:  # Thread-safe socket access
            for attempt in range(self._max_retries + 1):
                if not self.connect():
                    if attempt < self._max_retries:
                        logger.warning(f"Connection failed, retrying ({attempt + 1}/{self._max_retries})")
                        continue
                    raise HTTPException(
                        status_code=503,
                        detail=f"Could not connect to Ableton at {self.host}:{self.port}. Make sure Live is running with the AbletonMCP control surface enabled."
                    )

                command = {"type": command_type, "params": params or {}}

                try:
                    # Serialize and send
                    command_json = json.dumps(command)
                    if len(command_json) > MAX_BUFFER_SIZE:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Command too large: {len(command_json)} bytes (max {MAX_BUFFER_SIZE})"
                        )

                    self.sock.sendall(command_json.encode('utf-8'))
                    self.sock.settimeout(RECV_TIMEOUT)

                    # Receive with size limit
                    chunks = []
                    total_size = 0

                    while True:
                        try:
                            chunk = self.sock.recv(8192)
                            if not chunk:
                                break

                            total_size += len(chunk)
                            if total_size > MAX_BUFFER_SIZE:
                                raise HTTPException(
                                    status_code=500,
                                    detail=f"Response too large (>{MAX_BUFFER_SIZE} bytes)"
                                )

                            chunks.append(chunk)

                            # Try to parse - if valid JSON, we're done
                            try:
                                json.loads(b''.join(chunks).decode('utf-8'))
                                break
                            except json.JSONDecodeError:
                                continue

                        except socket.timeout:
                            if chunks:
                                break  # Got partial data, try to use it
                            raise Exception("Timeout waiting for response from Ableton")

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
                    last_error = f"Invalid JSON response from Ableton: {str(e)}"
                    self._reconnect()
                except socket.error as e:
                    last_error = f"Socket error: {str(e)}"
                    self._reconnect()
                    if attempt < self._max_retries:
                        logger.warning(f"Command failed, retrying ({attempt + 1}/{self._max_retries}): {last_error}")
                except Exception as e:
                    last_error = str(e)
                    self._reconnect()
                    if attempt < self._max_retries:
                        logger.warning(f"Command failed, retrying ({attempt + 1}/{self._max_retries}): {last_error}")

        raise HTTPException(status_code=500, detail=f"Command failed after {self._max_retries} retries: {last_error}")


# Global connection (thread-safe)
ableton = AbletonConnection()

# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="AbletonMCP REST API",
    description="REST API for controlling Ableton Live - works with Ollama, OpenAI, and other LLMs",
    version="1.0.0"
)

# CORS configuration - restrict to local development by default
# Set CORS_ORIGINS environment variable to allow additional origins
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,  # Disable credentials for security
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
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

@app.get("/api/commands")
def list_commands():
    """List all available commands"""
    return {"commands": sorted(list(ALLOWED_COMMANDS)), "count": len(ALLOWED_COMMANDS)}

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

@app.put("/api/tracks/{track_index}/clips/{clip_index}/name")
def set_clip_name(track_index: int, clip_index: int, req: ClipNameRequest):
    return ableton.send_command("set_clip_name", {
        "track_index": track_index,
        "clip_index": clip_index,
        "name": req.name
    })

@app.put("/api/tracks/{track_index}/clips/{clip_index}/color")
def set_clip_color(track_index: int, clip_index: int, req: ClipColorRequest):
    return ableton.send_command("set_clip_color", {
        "track_index": track_index,
        "clip_index": clip_index,
        "color": req.color
    })

@app.put("/api/tracks/{track_index}/clips/{clip_index}/loop")
def set_clip_loop(track_index: int, clip_index: int, req: ClipLoopRequest):
    return ableton.send_command("set_clip_loop", {
        "track_index": track_index,
        "clip_index": clip_index,
        "loop_start": req.loop_start,
        "loop_end": req.loop_end,
        "looping": req.looping
    })

@app.post("/api/tracks/{track_index}/clips/{clip_index}/select")
def select_clip(track_index: int, clip_index: int):
    return ableton.send_command("select_clip", {
        "track_index": track_index,
        "clip_index": clip_index
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

@app.put("/api/scenes/{scene_index}/name")
def set_scene_name(scene_index: int, req: SceneNameRequest):
    return ableton.send_command("set_scene_name", {"scene_index": scene_index, "name": req.name})

@app.put("/api/scenes/{scene_index}/color")
def set_scene_color(scene_index: int, color: int):
    return ableton.send_command("set_scene_color", {"scene_index": scene_index, "color": color})

@app.post("/api/scenes/{scene_index}/select")
def select_scene(scene_index: int):
    return ableton.send_command("select_scene", {"scene_index": scene_index})

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
    # Fix: ♭ should map to "b" for flat (e.g., Bb, Eb), not uppercase "B"
    root_normalized = root.upper().replace("♯", "#").replace("♭", "b")
    # Handle flat notes: Bb -> A#, Eb -> D#, etc. (enharmonic equivalents)
    flat_to_sharp = {"Bb": "A#", "Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#"}
    if root_normalized in flat_to_sharp:
        root_normalized = flat_to_sharp[root_normalized]
    root_midi = NOTE_TO_MIDI.get(root_normalized, 0) + (octave * 12)
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
# View & Selection
# ============================================================================

@app.get("/api/view")
def get_current_view():
    """Get current view state (selected track, scene, etc.)"""
    return ableton.send_command("get_current_view")

@app.post("/api/view/focus")
def focus_view(view_name: str):
    """Focus a specific view (Session, Arranger, Detail, etc.)"""
    return ableton.send_command("focus_view", {"view_name": view_name})

@app.post("/api/tracks/{track_index}/select")
def select_track(track_index: int):
    """Select a track"""
    return ableton.send_command("select_track", {"track_index": track_index})

# ============================================================================
# Arrangement
# ============================================================================

@app.get("/api/arrangement/length")
def get_arrangement_length():
    """Get arrangement length and loop settings"""
    return ableton.send_command("get_arrangement_length")

@app.post("/api/arrangement/loop")
def set_arrangement_loop(loop_start: float, loop_length: float, loop_on: bool = True):
    """Set arrangement loop region"""
    return ableton.send_command("set_arrangement_loop", {
        "loop_start": loop_start,
        "loop_length": loop_length,
        "loop_on": loop_on
    })

@app.post("/api/arrangement/jump")
def jump_to_time(time: float):
    """Jump to a specific time in the arrangement"""
    return ableton.send_command("jump_to_time", {"time": time})

@app.get("/api/arrangement/locators")
def get_locators():
    """Get all locators/markers"""
    return ableton.send_command("get_locators")

@app.post("/api/arrangement/locators")
def create_locator(time: float, name: str = ""):
    """Create a locator at specified time"""
    return ableton.send_command("create_locator", {"time": time, "name": name})

@app.delete("/api/arrangement/locators/{index}")
def delete_locator(index: int):
    """Delete a locator by index"""
    return ableton.send_command("delete_locator", {"index": index})

# ============================================================================
# I/O Routing
# ============================================================================

@app.get("/api/tracks/{track_index}/routing/input")
def get_track_input_routing(track_index: int):
    """Get track input routing"""
    return ableton.send_command("get_track_input_routing", {"track_index": track_index})

@app.get("/api/tracks/{track_index}/routing/output")
def get_track_output_routing(track_index: int):
    """Get track output routing"""
    return ableton.send_command("get_track_output_routing", {"track_index": track_index})

@app.put("/api/tracks/{track_index}/routing/input")
def set_track_input_routing(track_index: int, routing_type: str, routing_channel: str = ""):
    """Set track input routing"""
    return ableton.send_command("set_track_input_routing", {
        "track_index": track_index,
        "routing_type": routing_type,
        "routing_channel": routing_channel
    })

@app.put("/api/tracks/{track_index}/routing/output")
def set_track_output_routing(track_index: int, routing_type: str, routing_channel: str = ""):
    """Set track output routing"""
    return ableton.send_command("set_track_output_routing", {
        "track_index": track_index,
        "routing_type": routing_type,
        "routing_channel": routing_channel
    })

@app.get("/api/routing/inputs")
def get_available_inputs():
    """Get available audio/MIDI inputs"""
    return ableton.send_command("get_available_inputs")

@app.get("/api/routing/outputs")
def get_available_outputs():
    """Get available audio/MIDI outputs"""
    return ableton.send_command("get_available_outputs")

# ============================================================================
# Recording
# ============================================================================

@app.post("/api/recording/toggle-session")
def toggle_session_record():
    """Toggle session record mode"""
    return ableton.send_command("toggle_session_record")

@app.post("/api/recording/toggle-arrangement")
def toggle_arrangement_record():
    """Toggle arrangement record mode"""
    return ableton.send_command("toggle_arrangement_record")

# ============================================================================
# Session Info
# ============================================================================

@app.get("/api/session/path")
def get_session_path():
    """Get file path of current session"""
    return ableton.send_command("get_session_path")

@app.get("/api/session/modified")
def is_session_modified():
    """Check if session has unsaved changes"""
    return ableton.send_command("is_session_modified")

@app.get("/api/session/cpu")
def get_cpu_load():
    """Get current CPU load"""
    return ableton.send_command("get_cpu_load")

@app.get("/api/transport/position")
def get_playback_position():
    """Get current playback position"""
    return ableton.send_command("get_playback_position")

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
