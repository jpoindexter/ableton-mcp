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

from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator, Field
from typing import Optional, List, Dict, Any
import socket
import json
import logging
import uvicorn
import threading
import os
import secrets

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

# API Key Authentication (optional - set REST_API_KEY env var to enable)
# When enabled, all requests must include X-API-Key header
REST_API_KEY = os.environ.get("REST_API_KEY", None)
API_KEY_ENABLED = REST_API_KEY is not None and len(REST_API_KEY) > 0

# Rate Limiting Configuration (requests per minute per IP)
RATE_LIMIT_ENABLED = os.environ.get("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_REQUESTS = int(os.environ.get("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW = int(os.environ.get("RATE_LIMIT_WINDOW", "60"))  # seconds

# Trust proxy headers only when explicitly enabled (for reverse proxy deployments)
# WARNING: Only enable this if running behind a trusted reverse proxy!
TRUST_PROXY_HEADERS = os.environ.get("TRUST_PROXY_HEADERS", "false").lower() == "true"

# Command whitelist for security
ALLOWED_COMMANDS = {
    # Transport
    "health_check", "start_playback", "stop_playback", "get_playback_position",
    "get_session_info", "set_tempo", "undo", "redo",
    # Tracks
    "create_midi_track", "create_audio_track", "delete_track", "duplicate_track",
    "freeze_track", "flatten_track",
    "get_track_info", "get_track_color", "set_track_name", "set_track_mute", "set_track_solo",
    "set_track_arm", "set_track_volume", "set_track_pan", "set_track_color",
    "select_track", "get_track_input_routing", "get_track_output_routing",
    "set_track_input_routing", "set_track_output_routing",
    "get_available_inputs", "get_available_outputs",
    "set_track_monitoring", "get_track_monitoring",
    # Clips
    "create_clip", "delete_clip", "fire_clip", "stop_clip", "duplicate_clip",
    "get_clip_info", "get_clip_notes", "get_clip_color", "get_clip_loop",
    "set_clip_name", "set_clip_color", "set_clip_loop", "add_notes_to_clip",
    "remove_notes", "remove_all_notes", "transpose_notes", "select_clip",
    # Audio clip editing
    "get_clip_gain", "get_clip_pitch", "set_clip_gain", "set_clip_pitch",
    "set_clip_warp_mode", "get_clip_warp_info",
    # Warp markers
    "get_warp_markers", "add_warp_marker", "delete_warp_marker",
    # Scenes
    "get_all_scenes", "create_scene", "delete_scene", "fire_scene", "stop_scene",
    "duplicate_scene", "set_scene_name", "get_scene_color", "set_scene_color", "select_scene",
    # Devices
    "get_device_parameters", "set_device_parameter", "toggle_device", "delete_device",
    "get_device_by_name", "load_device_preset",
    # Rack chains
    "get_rack_chains", "select_rack_chain",
    # Browser
    "browse_path", "get_browser_children", "search_browser", "get_browser_tree",
    "get_browser_items_at_path", "load_browser_item", "load_instrument_or_effect",
    "load_browser_item_to_return",
    # Return tracks
    "get_return_tracks", "get_return_track_info", "get_send_level", "set_send_level",
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
                        detail="Could not connect to Ableton. Make sure Live is running with the AbletonMCP control surface enabled."
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
CORS_ORIGINS = [o.strip() for o in os.environ.get("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")]

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
    # Sanitize error message to avoid leaking internal details
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "An unexpected error occurred"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

# ============================================================================
# API Key Authentication Middleware
# ============================================================================

from starlette.middleware.base import BaseHTTPMiddleware

class APIKeyMiddleware(BaseHTTPMiddleware):
    """Middleware to validate API key on all requests (if enabled)."""

    async def dispatch(self, request: Request, call_next):
        # Skip auth for OpenAPI docs and health endpoints
        if request.url.path in ["/docs", "/openapi.json", "/redoc", "/api/health"]:
            return await call_next(request)

        if API_KEY_ENABLED:
            api_key = request.headers.get("X-API-Key")
            if api_key is None:
                return JSONResponse(
                    status_code=401,
                    content={"error": "API key required. Set X-API-Key header."}
                )
            # Use timing-safe comparison to prevent timing attacks
            if not secrets.compare_digest(api_key, REST_API_KEY):
                return JSONResponse(
                    status_code=403,
                    content={"error": "Invalid API key"}
                )

        return await call_next(request)

# Add API key middleware if enabled
if API_KEY_ENABLED:
    app.add_middleware(APIKeyMiddleware)
    logger.info("API Key authentication enabled")

# ============================================================================
# Rate Limiting Middleware
# ============================================================================

import time as time_module
from collections import OrderedDict

# Maximum number of unique client IPs to track for rate limiting (LRU eviction)
MAX_RATE_LIMIT_CLIENTS = int(os.environ.get("MAX_RATE_LIMIT_CLIENTS", "10000"))

class RateLimitMiddleware(BaseHTTPMiddleware):
    """LRU-based in-memory rate limiter by client IP with bounded memory."""

    def __init__(self, app, requests_limit: int, window_seconds: int, max_clients: int = MAX_RATE_LIMIT_CLIENTS):
        super().__init__(app)
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.max_clients = max_clients
        self.request_counts = OrderedDict()  # LRU-style with bounded size
        self._lock = threading.Lock()

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP. Only trusts proxy headers when TRUST_PROXY_HEADERS is enabled."""
        # Only trust X-Forwarded-For when explicitly configured
        # This prevents IP spoofing attacks when not behind a trusted proxy
        if TRUST_PROXY_HEADERS:
            forwarded = request.headers.get("X-Forwarded-For")
            if forwarded:
                return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _cleanup_old_requests(self, client_ip: str, current_time: float):
        """Remove requests outside the time window and evict stale clients."""
        cutoff = current_time - self.window_seconds

        # Clean up old timestamps for this client
        if client_ip in self.request_counts:
            self.request_counts[client_ip] = [
                t for t in self.request_counts[client_ip] if t > cutoff
            ]
            # Remove entry entirely if no requests remain (prevents memory leak)
            if not self.request_counts[client_ip]:
                del self.request_counts[client_ip]

        # LRU eviction: remove oldest clients if over max_clients limit
        while len(self.request_counts) > self.max_clients:
            self.request_counts.popitem(last=False)  # Remove oldest (FIFO order)

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks and docs
        if request.url.path in ["/api/health", "/health", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        current_time = time_module.time()

        with self._lock:
            self._cleanup_old_requests(client_ip, current_time)

            # Initialize if new client
            if client_ip not in self.request_counts:
                self.request_counts[client_ip] = []

            if len(self.request_counts[client_ip]) >= self.requests_limit:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "detail": f"Maximum {self.requests_limit} requests per {self.window_seconds} seconds"
                    }
                )

            self.request_counts[client_ip].append(current_time)
            # Move to end for LRU ordering (most recently used)
            self.request_counts.move_to_end(client_ip)

        return await call_next(request)

# Add rate limiting middleware if enabled
if RATE_LIMIT_ENABLED:
    app.add_middleware(RateLimitMiddleware, requests_limit=RATE_LIMIT_REQUESTS, window_seconds=RATE_LIMIT_WINDOW)
    logger.info(f"Rate limiting enabled: {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW}s")

# ============================================================================
# Index Validation Constants
# ============================================================================

# Maximum valid indices (Ableton has limits)
MAX_TRACK_INDEX = 999  # Ableton allows up to 1000 tracks
MAX_CLIP_INDEX = 999   # Clips per track
MAX_SCENE_INDEX = 999  # Scenes
MAX_DEVICE_INDEX = 127 # Devices per track
MAX_PARAMETER_INDEX = 255  # Parameters per device
MAX_SEND_INDEX = 11    # Return tracks (A-L)

def validate_track_index(v: int) -> int:
    """Validate track index is within bounds."""
    if v < 0 or v > MAX_TRACK_INDEX:
        raise ValueError(f'Track index must be between 0 and {MAX_TRACK_INDEX}')
    return v

def validate_clip_index(v: int) -> int:
    """Validate clip/scene index is within bounds."""
    if v < 0 or v > MAX_CLIP_INDEX:
        raise ValueError(f'Clip index must be between 0 and {MAX_CLIP_INDEX}')
    return v

def validate_scene_index(v: int) -> int:
    """Validate scene index is within bounds."""
    if v < 0 or v > MAX_SCENE_INDEX:
        raise ValueError(f'Scene index must be between 0 and {MAX_SCENE_INDEX}')
    return v

def validate_device_index(v: int) -> int:
    """Validate device index is within bounds."""
    if v < 0 or v > MAX_DEVICE_INDEX:
        raise ValueError(f'Device index must be between 0 and {MAX_DEVICE_INDEX}')
    return v

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
    track_index: int = Field(..., ge=0, le=MAX_TRACK_INDEX)

class TrackCreateRequest(BaseModel):
    index: Optional[int] = Field(-1, ge=-1, le=MAX_TRACK_INDEX)
    name: Optional[str] = Field(None, max_length=256)

class TrackNameRequest(BaseModel):
    track_index: int = Field(..., ge=0, le=MAX_TRACK_INDEX)
    name: str = Field(..., max_length=256)

class TrackBoolRequest(BaseModel):
    track_index: int = Field(..., ge=0, le=MAX_TRACK_INDEX)
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
    track_index: int = Field(..., ge=0, le=MAX_TRACK_INDEX)
    color: int = Field(..., ge=0, le=69)  # Ableton has 70 color indices (0-69)

class ClipRequest(BaseModel):
    track_index: int = Field(..., ge=0, le=MAX_TRACK_INDEX)
    clip_index: int = Field(..., ge=0, le=MAX_CLIP_INDEX)

class ClipCreateRequest(BaseModel):
    track_index: int = Field(..., ge=0, le=MAX_TRACK_INDEX)
    clip_index: int = Field(..., ge=0, le=MAX_CLIP_INDEX)
    length: Optional[float] = Field(4.0, gt=0, le=1024)  # Max 1024 beats
    name: Optional[str] = Field(None, max_length=256)

class ClipNameRequest(BaseModel):
    track_index: int = Field(..., ge=0, le=MAX_TRACK_INDEX)
    clip_index: int = Field(..., ge=0, le=MAX_CLIP_INDEX)
    name: str = Field(..., max_length=256)

class ClipColorRequest(BaseModel):
    track_index: int = Field(..., ge=0, le=MAX_TRACK_INDEX)
    clip_index: int = Field(..., ge=0, le=MAX_CLIP_INDEX)
    color: int = Field(..., ge=0, le=69)  # Ableton has 70 color indices (0-69)

class ClipLoopRequest(BaseModel):
    track_index: int = Field(..., ge=0, le=MAX_TRACK_INDEX)
    clip_index: int = Field(..., ge=0, le=MAX_CLIP_INDEX)
    loop_start: Optional[float] = Field(None, ge=0, le=100000)
    loop_end: Optional[float] = Field(None, ge=0, le=100000)
    looping: Optional[bool] = None

class ClipDuplicateRequest(BaseModel):
    track_index: int = Field(..., ge=0, le=MAX_TRACK_INDEX)
    clip_index: int = Field(..., ge=0, le=MAX_CLIP_INDEX)
    target_index: int = Field(..., ge=0, le=MAX_CLIP_INDEX)

class Note(BaseModel):
    pitch: int = Field(..., ge=0, le=127)
    start_time: float = Field(..., ge=0, le=100000)
    duration: float = Field(..., gt=0, le=1024)
    velocity: Optional[int] = Field(100, ge=0, le=127)

class AddNotesRequest(BaseModel):
    track_index: int = Field(..., ge=0, le=MAX_TRACK_INDEX)
    clip_index: int = Field(..., ge=0, le=MAX_CLIP_INDEX)
    notes: List[Note] = Field(..., max_length=10000)  # Limit notes per request

class RemoveNotesRequest(BaseModel):
    track_index: int = Field(..., ge=0, le=MAX_TRACK_INDEX)
    clip_index: int = Field(..., ge=0, le=MAX_CLIP_INDEX)
    pitch: Optional[int] = Field(-1, ge=-1, le=127)
    start_time: float = Field(..., ge=0, le=100000)
    end_time: float = Field(..., ge=0, le=100000)

class TransposeRequest(BaseModel):
    track_index: int = Field(..., ge=0, le=MAX_TRACK_INDEX)
    clip_index: int = Field(..., ge=0, le=MAX_CLIP_INDEX)
    semitones: int = Field(..., ge=-127, le=127)

class SceneRequest(BaseModel):
    scene_index: int = Field(..., ge=0, le=MAX_SCENE_INDEX)

class SceneCreateRequest(BaseModel):
    index: Optional[int] = Field(-1, ge=-1, le=MAX_SCENE_INDEX)
    name: Optional[str] = Field(None, max_length=256)

class SceneNameRequest(BaseModel):
    scene_index: int = Field(..., ge=0, le=MAX_SCENE_INDEX)
    name: str = Field(..., max_length=256)

class DeviceRequest(BaseModel):
    track_index: int = Field(..., ge=0, le=MAX_TRACK_INDEX)
    device_index: int = Field(..., ge=0, le=MAX_DEVICE_INDEX)

class DeviceToggleRequest(BaseModel):
    track_index: int = Field(..., ge=0, le=MAX_TRACK_INDEX)
    device_index: int = Field(..., ge=0, le=MAX_DEVICE_INDEX)
    enabled: Optional[bool] = None

class DeviceParamRequest(BaseModel):
    track_index: int = Field(..., ge=0, le=MAX_TRACK_INDEX)
    device_index: int = Field(..., ge=0, le=MAX_DEVICE_INDEX)
    parameter_index: int = Field(..., ge=0, le=MAX_PARAMETER_INDEX)
    value: float = Field(..., ge=0, le=1)  # Normalized parameter value

class SendLevelRequest(BaseModel):
    track_index: int = Field(..., ge=0, le=MAX_TRACK_INDEX)
    send_index: int = Field(..., ge=0, le=MAX_SEND_INDEX)
    level: float = Field(..., ge=0, le=1)  # Normalized level

class ReturnVolumeRequest(BaseModel):
    return_index: int = Field(..., ge=0, le=MAX_SEND_INDEX)
    volume: float = Field(..., ge=0, le=1)  # Normalized volume

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
def get_track_info(track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX, description="Track index")):
    return ableton.send_command("get_track_info", {"track_index": track_index})

@app.post("/api/tracks/midi")
def create_midi_track(req: TrackCreateRequest):
    return ableton.send_command("create_midi_track", {"index": req.index, "name": req.name})

@app.post("/api/tracks/audio")
def create_audio_track(req: TrackCreateRequest):
    return ableton.send_command("create_audio_track", {"index": req.index, "name": req.name})

@app.delete("/api/tracks/{track_index}")
def delete_track(track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX)):
    return ableton.send_command("delete_track", {"track_index": track_index})

@app.post("/api/tracks/{track_index}/duplicate")
def duplicate_track(track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX)):
    return ableton.send_command("duplicate_track", {"track_index": track_index})

@app.post("/api/tracks/{track_index}/freeze")
def freeze_track(track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX)):
    return ableton.send_command("freeze_track", {"track_index": track_index})

@app.post("/api/tracks/{track_index}/flatten")
def flatten_track(track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX)):
    return ableton.send_command("flatten_track", {"track_index": track_index})

@app.put("/api/tracks/{track_index}/name")
def set_track_name(track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX), req: TrackNameRequest = None):
    return ableton.send_command("set_track_name", {"track_index": track_index, "name": req.name})

@app.get("/api/tracks/{track_index}/color")
def get_track_color(track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX)):
    return ableton.send_command("get_track_color", {"track_index": track_index})

@app.put("/api/tracks/{track_index}/color")
def set_track_color(track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX), req: TrackColorRequest = None):
    return ableton.send_command("set_track_color", {"track_index": track_index, "color": req.color})

@app.put("/api/tracks/{track_index}/mute")
def set_track_mute(track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX), req: TrackBoolRequest = None):
    return ableton.send_command("set_track_mute", {"track_index": track_index, "mute": req.value})

@app.put("/api/tracks/{track_index}/solo")
def set_track_solo(track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX), req: TrackBoolRequest = None):
    return ableton.send_command("set_track_solo", {"track_index": track_index, "solo": req.value})

@app.put("/api/tracks/{track_index}/arm")
def set_track_arm(track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX), req: TrackBoolRequest = None):
    return ableton.send_command("set_track_arm", {"track_index": track_index, "arm": req.value})

@app.put("/api/tracks/{track_index}/volume")
def set_track_volume(track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX), req: TrackVolumeRequest = None):
    return ableton.send_command("set_track_volume", {"track_index": track_index, "volume": req.volume})

@app.put("/api/tracks/{track_index}/pan")
def set_track_pan(track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX), req: TrackPanRequest = None):
    return ableton.send_command("set_track_pan", {"track_index": track_index, "pan": req.pan})

# Track Monitoring
class MonitoringRequest(BaseModel):
    monitoring: int = Field(..., ge=0, le=2, description="Monitoring state (0=In, 1=Auto, 2=Off)")

@app.get("/api/tracks/{track_index}/monitoring")
def get_track_monitoring(track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX)):
    """Get track monitoring state"""
    return ableton.send_command("get_track_monitoring", {"track_index": track_index})

@app.put("/api/tracks/{track_index}/monitoring")
def set_track_monitoring(track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX), req: MonitoringRequest = None):
    """Set track monitoring state (0=In, 1=Auto, 2=Off)"""
    return ableton.send_command("set_track_monitoring", {"track_index": track_index, "monitoring": req.monitoring})

# Group Tracks
class GroupTrackRequest(BaseModel):
    track_indices: List[int] = Field(..., min_length=1, description="List of track indices to group")

@app.post("/api/tracks/group")
def create_group_track(req: GroupTrackRequest):
    """Create a group track containing the specified tracks"""
    return ableton.send_command("create_group_track", {"track_indices": req.track_indices})

@app.post("/api/tracks/{track_index}/fold")
def fold_track(track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX)):
    """Fold/collapse a group track"""
    return ableton.send_command("fold_track", {"track_index": track_index})

@app.post("/api/tracks/{track_index}/unfold")
def unfold_track(track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX)):
    """Unfold/expand a group track"""
    return ableton.send_command("unfold_track", {"track_index": track_index})

# Clips
@app.get("/api/tracks/{track_index}/clips/{clip_index}")
def get_clip_info(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX)
):
    return ableton.send_command("get_clip_info", {"track_index": track_index, "clip_index": clip_index})

@app.post("/api/tracks/{track_index}/clips/{clip_index}")
def create_clip(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX),
    req: ClipCreateRequest = None
):
    return ableton.send_command("create_clip", {
        "track_index": track_index,
        "clip_index": clip_index,
        "length": req.length,
        "name": req.name
    })

@app.delete("/api/tracks/{track_index}/clips/{clip_index}")
def delete_clip(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX)
):
    return ableton.send_command("delete_clip", {"track_index": track_index, "clip_index": clip_index})

@app.post("/api/tracks/{track_index}/clips/{clip_index}/fire")
def fire_clip(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX)
):
    return ableton.send_command("fire_clip", {"track_index": track_index, "clip_index": clip_index})

@app.post("/api/tracks/{track_index}/clips/{clip_index}/stop")
def stop_clip(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX)
):
    return ableton.send_command("stop_clip", {"track_index": track_index, "clip_index": clip_index})

@app.post("/api/tracks/{track_index}/clips/{clip_index}/duplicate")
def duplicate_clip(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX),
    req: ClipDuplicateRequest = None
):
    return ableton.send_command("duplicate_clip", {
        "track_index": track_index,
        "clip_index": clip_index,
        "target_index": req.target_index
    })

@app.put("/api/tracks/{track_index}/clips/{clip_index}/name")
def set_clip_name(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX),
    req: ClipNameRequest = None
):
    return ableton.send_command("set_clip_name", {
        "track_index": track_index,
        "clip_index": clip_index,
        "name": req.name
    })

@app.get("/api/tracks/{track_index}/clips/{clip_index}/color")
def get_clip_color(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX)
):
    return ableton.send_command("get_clip_color", {
        "track_index": track_index,
        "clip_index": clip_index
    })

@app.put("/api/tracks/{track_index}/clips/{clip_index}/color")
def set_clip_color(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX),
    req: ClipColorRequest = None
):
    return ableton.send_command("set_clip_color", {
        "track_index": track_index,
        "clip_index": clip_index,
        "color": req.color
    })

@app.get("/api/tracks/{track_index}/clips/{clip_index}/loop")
def get_clip_loop(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX)
):
    return ableton.send_command("get_clip_loop", {
        "track_index": track_index,
        "clip_index": clip_index
    })

@app.put("/api/tracks/{track_index}/clips/{clip_index}/loop")
def set_clip_loop(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX),
    req: ClipLoopRequest = None
):
    return ableton.send_command("set_clip_loop", {
        "track_index": track_index,
        "clip_index": clip_index,
        "loop_start": req.loop_start,
        "loop_end": req.loop_end,
        "looping": req.looping
    })

@app.post("/api/tracks/{track_index}/clips/{clip_index}/select")
def select_clip(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX)
):
    return ableton.send_command("select_clip", {
        "track_index": track_index,
        "clip_index": clip_index
    })

# Notes
@app.get("/api/tracks/{track_index}/clips/{clip_index}/notes")
def get_clip_notes(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX)
):
    return ableton.send_command("get_clip_notes", {"track_index": track_index, "clip_index": clip_index})

@app.post("/api/tracks/{track_index}/clips/{clip_index}/notes")
def add_notes(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX),
    req: AddNotesRequest = None
):
    notes = [{"pitch": n.pitch, "start_time": n.start_time, "duration": n.duration, "velocity": n.velocity} for n in req.notes]
    return ableton.send_command("add_notes_to_clip", {
        "track_index": track_index,
        "clip_index": clip_index,
        "notes": notes
    })

@app.delete("/api/tracks/{track_index}/clips/{clip_index}/notes")
def remove_all_notes(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX)
):
    return ableton.send_command("remove_all_notes", {"track_index": track_index, "clip_index": clip_index})

@app.post("/api/tracks/{track_index}/clips/{clip_index}/transpose")
def transpose_notes(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX),
    req: TransposeRequest = None
):
    return ableton.send_command("transpose_notes", {
        "track_index": track_index,
        "clip_index": clip_index,
        "semitones": req.semitones
    })

# Warp Markers
@app.get("/api/tracks/{track_index}/clips/{clip_index}/warp-markers")
def get_warp_markers(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX)
):
    return ableton.send_command("get_warp_markers", {
        "track_index": track_index,
        "clip_index": clip_index
    })

class WarpMarkerRequest(BaseModel):
    beat_time: float = Field(..., ge=0, le=100000)
    sample_time: Optional[float] = Field(None, ge=0, le=1000000000)

@app.post("/api/tracks/{track_index}/clips/{clip_index}/warp-markers")
def add_warp_marker(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX),
    req: WarpMarkerRequest = None
):
    params = {
        "track_index": track_index,
        "clip_index": clip_index,
        "beat_time": req.beat_time
    }
    if req.sample_time is not None:
        params["sample_time"] = req.sample_time
    return ableton.send_command("add_warp_marker", params)

class DeleteWarpMarkerRequest(BaseModel):
    beat_time: float = Field(..., ge=0, le=100000)

@app.delete("/api/tracks/{track_index}/clips/{clip_index}/warp-markers")
def delete_warp_marker(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX),
    req: DeleteWarpMarkerRequest = None
):
    return ableton.send_command("delete_warp_marker", {
        "track_index": track_index,
        "clip_index": clip_index,
        "beat_time": req.beat_time
    })

# Audio Clip Properties
@app.get("/api/tracks/{track_index}/clips/{clip_index}/gain")
def get_clip_gain(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX)
):
    return ableton.send_command("get_clip_gain", {
        "track_index": track_index,
        "clip_index": clip_index
    })

class ClipGainRequest(BaseModel):
    gain: float = Field(..., ge=-70, le=24, description="Gain in dB")

@app.put("/api/tracks/{track_index}/clips/{clip_index}/gain")
def set_clip_gain(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX),
    req: ClipGainRequest = None
):
    return ableton.send_command("set_clip_gain", {
        "track_index": track_index,
        "clip_index": clip_index,
        "gain": req.gain
    })

@app.get("/api/tracks/{track_index}/clips/{clip_index}/pitch")
def get_clip_pitch(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX)
):
    return ableton.send_command("get_clip_pitch", {
        "track_index": track_index,
        "clip_index": clip_index
    })

class ClipPitchRequest(BaseModel):
    pitch: int = Field(..., ge=-48, le=48, description="Pitch shift in semitones")

@app.put("/api/tracks/{track_index}/clips/{clip_index}/pitch")
def set_clip_pitch(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX),
    req: ClipPitchRequest = None
):
    return ableton.send_command("set_clip_pitch", {
        "track_index": track_index,
        "clip_index": clip_index,
        "pitch": req.pitch
    })

# Clip Automation
class AutomationRequest(BaseModel):
    points: List[Dict[str, float]] = Field(..., max_length=10000, description="List of automation points with 'time' and 'value' keys")

@app.get("/api/tracks/{track_index}/clips/{clip_index}/automation/{parameter_name}")
def get_clip_automation(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX),
    parameter_name: str = Path(...)
):
    """Get automation envelope for a parameter in a clip"""
    return ableton.send_command("get_clip_automation", {
        "track_index": track_index,
        "clip_index": clip_index,
        "parameter_name": parameter_name
    })

@app.put("/api/tracks/{track_index}/clips/{clip_index}/automation/{parameter_name}")
def set_clip_automation(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX),
    parameter_name: str = Path(...),
    req: AutomationRequest = None
):
    """Set automation envelope for a parameter in a clip"""
    return ableton.send_command("set_clip_automation", {
        "track_index": track_index,
        "clip_index": clip_index,
        "parameter_name": parameter_name,
        "points": req.points
    })

@app.delete("/api/tracks/{track_index}/clips/{clip_index}/automation/{parameter_name}")
def clear_clip_automation(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX),
    parameter_name: str = Path(...)
):
    """Clear automation envelope for a parameter in a clip"""
    return ableton.send_command("clear_clip_automation", {
        "track_index": track_index,
        "clip_index": clip_index,
        "parameter_name": parameter_name
    })

# Warp Mode
class WarpModeRequest(BaseModel):
    warp_mode: int = Field(..., ge=0, le=6, description="Warp mode (0=Beats, 1=Tones, 2=Texture, 3=Re-Pitch, 4=Complex, 5=Rex, 6=Complex Pro)")

@app.get("/api/tracks/{track_index}/clips/{clip_index}/warp")
def get_clip_warp_info(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX)
):
    """Get warp information for an audio clip"""
    return ableton.send_command("get_clip_warp_info", {
        "track_index": track_index,
        "clip_index": clip_index
    })

@app.put("/api/tracks/{track_index}/clips/{clip_index}/warp")
def set_clip_warp_mode(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX),
    req: WarpModeRequest = None
):
    """Set warp mode for an audio clip"""
    return ableton.send_command("set_clip_warp_mode", {
        "track_index": track_index,
        "clip_index": clip_index,
        "warp_mode": req.warp_mode
    })

# Scenes
@app.get("/api/scenes")
def get_all_scenes():
    return ableton.send_command("get_all_scenes")

@app.post("/api/scenes")
def create_scene(req: SceneCreateRequest):
    return ableton.send_command("create_scene", {"index": req.index, "name": req.name})

@app.delete("/api/scenes/{scene_index}")
def delete_scene(scene_index: int = Path(..., ge=0, le=MAX_SCENE_INDEX)):
    return ableton.send_command("delete_scene", {"scene_index": scene_index})

@app.post("/api/scenes/{scene_index}/fire")
def fire_scene(scene_index: int = Path(..., ge=0, le=MAX_SCENE_INDEX)):
    return ableton.send_command("fire_scene", {"scene_index": scene_index})

@app.post("/api/scenes/{scene_index}/stop")
def stop_scene(scene_index: int = Path(..., ge=0, le=MAX_SCENE_INDEX)):
    return ableton.send_command("stop_scene", {"scene_index": scene_index})

@app.post("/api/scenes/{scene_index}/duplicate")
def duplicate_scene(scene_index: int = Path(..., ge=0, le=MAX_SCENE_INDEX)):
    return ableton.send_command("duplicate_scene", {"scene_index": scene_index})

@app.put("/api/scenes/{scene_index}/name")
def set_scene_name(scene_index: int = Path(..., ge=0, le=MAX_SCENE_INDEX), req: SceneNameRequest = None):
    return ableton.send_command("set_scene_name", {"scene_index": scene_index, "name": req.name})

class SceneColorRequest(BaseModel):
    color: int = Field(..., ge=0, le=69)  # Ableton has 70 color indices (0-69)

@app.get("/api/scenes/{scene_index}/color")
def get_scene_color(scene_index: int = Path(..., ge=0, le=MAX_SCENE_INDEX)):
    return ableton.send_command("get_scene_color", {"scene_index": scene_index})

@app.put("/api/scenes/{scene_index}/color")
def set_scene_color(scene_index: int = Path(..., ge=0, le=MAX_SCENE_INDEX), req: SceneColorRequest = None):
    return ableton.send_command("set_scene_color", {"scene_index": scene_index, "color": req.color})

@app.post("/api/scenes/{scene_index}/select")
def select_scene(scene_index: int = Path(..., ge=0, le=MAX_SCENE_INDEX)):
    return ableton.send_command("select_scene", {"scene_index": scene_index})

# Devices
@app.get("/api/tracks/{track_index}/devices/{device_index}")
def get_device_parameters(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    device_index: int = Path(..., ge=0, le=MAX_DEVICE_INDEX)
):
    return ableton.send_command("get_device_parameters", {"track_index": track_index, "device_index": device_index})

@app.put("/api/tracks/{track_index}/devices/{device_index}/parameter")
def set_device_parameter(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    device_index: int = Path(..., ge=0, le=MAX_DEVICE_INDEX),
    req: DeviceParamRequest = None
):
    return ableton.send_command("set_device_parameter", {
        "track_index": track_index,
        "device_index": device_index,
        "parameter_index": req.parameter_index,
        "value": req.value
    })

@app.put("/api/tracks/{track_index}/devices/{device_index}/toggle")
def toggle_device(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    device_index: int = Path(..., ge=0, le=MAX_DEVICE_INDEX),
    req: DeviceToggleRequest = None
):
    return ableton.send_command("toggle_device", {
        "track_index": track_index,
        "device_index": device_index,
        "enabled": req.enabled
    })

@app.delete("/api/tracks/{track_index}/devices/{device_index}")
def delete_device(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    device_index: int = Path(..., ge=0, le=MAX_DEVICE_INDEX)
):
    return ableton.send_command("delete_device", {"track_index": track_index, "device_index": device_index})

@app.get("/api/tracks/{track_index}/devices/by-name/{device_name}")
def get_device_by_name(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    device_name: str = Path(...)
):
    """Get a device by its name on a track"""
    return ableton.send_command("get_device_by_name", {"track_index": track_index, "device_name": device_name})

# Rack Chains
@app.get("/api/tracks/{track_index}/devices/{device_index}/chains")
def get_rack_chains(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    device_index: int = Path(..., ge=0, le=MAX_DEVICE_INDEX)
):
    """Get chains in a rack device"""
    return ableton.send_command("get_rack_chains", {"track_index": track_index, "device_index": device_index})

@app.post("/api/tracks/{track_index}/devices/{device_index}/chains/{chain_index}/select")
def select_rack_chain(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    device_index: int = Path(..., ge=0, le=MAX_DEVICE_INDEX),
    chain_index: int = Path(..., ge=0)
):
    """Select a chain in a rack device"""
    return ableton.send_command("select_rack_chain", {
        "track_index": track_index,
        "device_index": device_index,
        "chain_index": chain_index
    })

# Return Tracks
@app.get("/api/returns")
def get_return_tracks():
    return ableton.send_command("get_return_tracks")

@app.get("/api/tracks/{track_index}/sends/{send_index}")
def get_send_level(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    send_index: int = Path(..., ge=0, le=MAX_SEND_INDEX)
):
    return ableton.send_command("get_send_level", {
        "track_index": track_index,
        "send_index": send_index
    })

@app.post("/api/tracks/{track_index}/sends/{send_index}")
def set_send_level(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    send_index: int = Path(..., ge=0, le=MAX_SEND_INDEX),
    req: SendLevelRequest = None
):
    return ableton.send_command("set_send_level", {
        "track_index": track_index,
        "send_index": send_index,
        "level": req.level
    })

@app.put("/api/returns/{return_index}/volume")
def set_return_volume(return_index: int = Path(..., ge=0, le=MAX_SEND_INDEX), req: ReturnVolumeRequest = None):
    return ableton.send_command("set_return_volume", {"return_index": return_index, "volume": req.volume})

@app.put("/api/returns/{return_index}/pan")
def set_return_pan(return_index: int = Path(..., ge=0, le=MAX_SEND_INDEX), req: ReturnPanRequest = None):
    """Set return track pan (-1.0 to 1.0)"""
    return ableton.send_command("set_return_pan", {"return_index": return_index, "pan": req.pan})

@app.get("/api/returns/{return_index}")
def get_return_track_info(return_index: int = Path(..., ge=0, le=MAX_SEND_INDEX)):
    """Get detailed information about a specific return track"""
    return ableton.send_command("get_return_track_info", {"return_index": return_index})

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
def quantize_clip(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX),
    req: QuantizeRequest = None
):
    return ableton.send_command("quantize_clip_notes", {
        "track_index": track_index,
        "clip_index": clip_index,
        "grid": req.grid,
        "strength": req.strength
    })

@app.post("/api/tracks/{track_index}/clips/{clip_index}/humanize/timing")
def humanize_timing(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX),
    req: HumanizeTimingRequest = None
):
    return ableton.send_command("humanize_clip_timing", {
        "track_index": track_index,
        "clip_index": clip_index,
        "amount": req.amount
    })

@app.post("/api/tracks/{track_index}/clips/{clip_index}/humanize/velocity")
def humanize_velocity(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX),
    req: HumanizeVelocityRequest = None
):
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
# Groove Pool
# ============================================================================

class ApplyGrooveRequest(BaseModel):
    groove_index: int = Field(..., ge=0, description="Index of the groove in the pool")

@app.get("/api/grooves")
def get_groove_pool():
    """Get all grooves in the groove pool"""
    return ableton.send_command("get_groove_pool")

@app.post("/api/tracks/{track_index}/clips/{clip_index}/groove")
def apply_groove(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX),
    req: ApplyGrooveRequest = None
):
    """Apply a groove from the groove pool to a clip"""
    return ableton.send_command("apply_groove", {
        "track_index": track_index,
        "clip_index": clip_index,
        "groove_index": req.groove_index
    })

@app.post("/api/tracks/{track_index}/clips/{clip_index}/groove/commit")
def commit_groove(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    clip_index: int = Path(..., ge=0, le=MAX_CLIP_INDEX)
):
    """Commit/bake the groove into the clip"""
    return ableton.send_command("commit_groove", {
        "track_index": track_index,
        "clip_index": clip_index
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

@app.put("/api/master/volume")
def set_master_volume(req: MasterVolumeRequest):
    """Set master track volume (0.0 to 1.0)"""
    return ableton.send_command("set_master_volume", {"volume": req.volume})

@app.put("/api/master/pan")
def set_master_pan(req: MasterPanRequest):
    """Set master track pan (-1.0 to 1.0)"""
    return ableton.send_command("set_master_pan", {"pan": req.pan})

# ============================================================================
# Browser
# ============================================================================

class BrowsePathRequest(BaseModel):
    path: List[str] = Field(..., max_length=20)  # e.g. ["Audio Effects", "EQ Eight"]

class BrowserSearchRequest(BaseModel):
    query: str = Field(..., max_length=256)
    category: str = Field("all", max_length=32)  # all, instruments, sounds, drums, audio_effects, midi_effects

class BrowserChildrenRequest(BaseModel):
    uri: str = Field(..., max_length=2048)

class LoadItemToTrackRequest(BaseModel):
    track_index: int = Field(..., ge=0, le=MAX_TRACK_INDEX)
    uri: str = Field(..., max_length=2048)

class LoadItemToReturnRequest(BaseModel):
    return_index: int = Field(..., ge=0, le=MAX_SEND_INDEX)
    uri: str = Field(..., max_length=2048)

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

@app.get("/api/browser/tree")
def get_browser_tree():
    """Get the root-level browser tree structure"""
    return ableton.send_command("get_browser_tree")

class BrowserPathRequest(BaseModel):
    path: str = Field(..., max_length=1024, description="Browser path like 'Sounds/Drums' or 'Audio Effects/EQ'")

@app.get("/api/browser/items")
def get_browser_items_at_path(path: str = Query(..., max_length=1024, description="Browser path like 'Sounds/Drums' or 'Audio Effects/EQ'")):
    """Get browser items at a specific path"""
    return ableton.send_command("get_browser_items_at_path", {"path": path})

# ============================================================================
# View & Selection
# ============================================================================

# Valid view names for focus_view
VALID_VIEW_NAMES = {"Session", "Arranger", "Detail", "Detail/Clip", "Detail/DeviceChain", "Browser"}

@app.get("/api/view")
def get_current_view():
    """Get current view state (selected track, scene, etc.)"""
    return ableton.send_command("get_current_view")

@app.post("/api/view/focus")
def focus_view(view_name: str = Query(...)):
    """Focus a specific view (Session, Arranger, Detail, etc.)"""
    if view_name not in VALID_VIEW_NAMES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid view_name. Must be one of: {sorted(VALID_VIEW_NAMES)}"
        )
    return ableton.send_command("focus_view", {"view_name": view_name})

@app.post("/api/tracks/{track_index}/select")
def select_track(track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX)):
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
def get_track_input_routing(track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX)):
    """Get track input routing"""
    return ableton.send_command("get_track_input_routing", {"track_index": track_index})

@app.get("/api/tracks/{track_index}/routing/output")
def get_track_output_routing(track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX)):
    """Get track output routing"""
    return ableton.send_command("get_track_output_routing", {"track_index": track_index})

@app.put("/api/tracks/{track_index}/routing/input")
def set_track_input_routing(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    routing_type: str = Query(...),
    routing_channel: str = Query("")
):
    """Set track input routing"""
    return ableton.send_command("set_track_input_routing", {
        "track_index": track_index,
        "routing_type": routing_type,
        "routing_channel": routing_channel
    })

@app.put("/api/tracks/{track_index}/routing/output")
def set_track_output_routing(
    track_index: int = Path(..., ge=0, le=MAX_TRACK_INDEX),
    routing_type: str = Query(...),
    routing_channel: str = Query("")
):
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

# Parameter validation schemas for generic command endpoint
COMMAND_PARAM_SCHEMAS = {
    # Transport commands (no params or simple params)
    "health_check": {},
    "start_playback": {},
    "stop_playback": {},
    "get_playback_position": {},
    "get_session_info": {},
    "undo": {},
    "redo": {},
    "set_tempo": {"tempo": {"type": float, "min": 20, "max": 300}},
    # Track commands
    "create_midi_track": {"index": {"type": int, "min": -1, "max": MAX_TRACK_INDEX, "optional": True}, "name": {"type": str, "max_length": 256, "optional": True}},
    "create_audio_track": {"index": {"type": int, "min": -1, "max": MAX_TRACK_INDEX, "optional": True}, "name": {"type": str, "max_length": 256, "optional": True}},
    "delete_track": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}},
    "duplicate_track": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}},
    "freeze_track": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}},
    "flatten_track": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}},
    "get_track_info": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}},
    "get_track_color": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}},
    "set_track_name": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "name": {"type": str, "max_length": 256}},
    "set_track_mute": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "mute": {"type": bool}},
    "set_track_solo": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "solo": {"type": bool}},
    "set_track_arm": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "arm": {"type": bool}},
    "set_track_volume": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "volume": {"type": float, "min": 0, "max": 1}},
    "set_track_pan": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "pan": {"type": float, "min": -1, "max": 1}},
    "set_track_color": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "color": {"type": int, "min": 0, "max": 69}},
    "select_track": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}},
    # Clip commands
    "create_clip": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}, "length": {"type": float, "min": 0.01, "max": 1024, "optional": True}, "name": {"type": str, "max_length": 256, "optional": True}},
    "delete_clip": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}},
    "fire_clip": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}},
    "stop_clip": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}},
    "duplicate_clip": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}, "target_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}},
    "get_clip_info": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}},
    "get_clip_notes": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}},
    "get_clip_color": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}},
    "get_clip_loop": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}},
    "set_clip_name": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}, "name": {"type": str, "max_length": 256}},
    "set_clip_color": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}, "color": {"type": int, "min": 0, "max": 69}},
    "set_clip_loop": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}, "loop_start": {"type": float, "min": 0, "max": 100000, "optional": True}, "loop_end": {"type": float, "min": 0, "max": 100000, "optional": True}, "looping": {"type": bool, "optional": True}},
    "select_clip": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}},
    # Note commands
    "add_notes_to_clip": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}, "notes": {"type": list, "max_length": 10000}},
    "remove_notes": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}, "pitch": {"type": int, "min": -1, "max": 127, "optional": True}, "start_time": {"type": float, "min": 0, "max": 100000}, "end_time": {"type": float, "min": 0, "max": 100000}},
    "remove_all_notes": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}},
    "transpose_notes": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}, "semitones": {"type": int, "min": -127, "max": 127}},
    # Scene commands
    "get_all_scenes": {},
    "create_scene": {"index": {"type": int, "min": -1, "max": MAX_SCENE_INDEX, "optional": True}, "name": {"type": str, "max_length": 256, "optional": True}},
    "delete_scene": {"scene_index": {"type": int, "min": 0, "max": MAX_SCENE_INDEX}},
    "fire_scene": {"scene_index": {"type": int, "min": 0, "max": MAX_SCENE_INDEX}},
    "stop_scene": {"scene_index": {"type": int, "min": 0, "max": MAX_SCENE_INDEX}},
    "duplicate_scene": {"scene_index": {"type": int, "min": 0, "max": MAX_SCENE_INDEX}},
    "set_scene_name": {"scene_index": {"type": int, "min": 0, "max": MAX_SCENE_INDEX}, "name": {"type": str, "max_length": 256}},
    "get_scene_color": {"scene_index": {"type": int, "min": 0, "max": MAX_SCENE_INDEX}},
    "set_scene_color": {"scene_index": {"type": int, "min": 0, "max": MAX_SCENE_INDEX}, "color": {"type": int, "min": 0, "max": 69}},
    "select_scene": {"scene_index": {"type": int, "min": 0, "max": MAX_SCENE_INDEX}},
    # Device commands
    "get_device_parameters": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "device_index": {"type": int, "min": 0, "max": MAX_DEVICE_INDEX}},
    "set_device_parameter": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "device_index": {"type": int, "min": 0, "max": MAX_DEVICE_INDEX}, "parameter_index": {"type": int, "min": 0, "max": MAX_PARAMETER_INDEX}, "value": {"type": float, "min": 0, "max": 1}},
    "toggle_device": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "device_index": {"type": int, "min": 0, "max": MAX_DEVICE_INDEX}, "enabled": {"type": bool, "optional": True}},
    "delete_device": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "device_index": {"type": int, "min": 0, "max": MAX_DEVICE_INDEX}},
    # View commands
    "get_current_view": {},
    "focus_view": {"view_name": {"type": str, "allowed_values": VALID_VIEW_NAMES}},
    # Additional commands with minimal validation
    "get_track_input_routing": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}},
    "get_track_output_routing": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}},
    "set_track_input_routing": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "routing_type": {"type": str, "max_length": 64}, "routing_channel": {"type": str, "max_length": 64, "optional": True}},
    "set_track_output_routing": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "routing_type": {"type": str, "max_length": 64}, "routing_channel": {"type": str, "max_length": 64, "optional": True}},
    "get_available_inputs": {},
    "get_available_outputs": {},
    "set_track_monitoring": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "monitoring": {"type": int, "min": 0, "max": 2}},
    "get_track_monitoring": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}},
    # Return tracks
    "get_return_tracks": {},
    "get_return_track_info": {"return_index": {"type": int, "min": 0, "max": MAX_SEND_INDEX}},
    "get_send_level": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "send_index": {"type": int, "min": 0, "max": MAX_SEND_INDEX}},
    "set_send_level": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "send_index": {"type": int, "min": 0, "max": MAX_SEND_INDEX}, "level": {"type": float, "min": 0, "max": 1}},
    "set_return_volume": {"return_index": {"type": int, "min": 0, "max": MAX_SEND_INDEX}, "volume": {"type": float, "min": 0, "max": 1}},
    "set_return_pan": {"return_index": {"type": int, "min": 0, "max": MAX_SEND_INDEX}, "pan": {"type": float, "min": -1, "max": 1}},
    # Master track
    "get_master_info": {},
    "set_master_volume": {"volume": {"type": float, "min": 0, "max": 1}},
    "set_master_pan": {"pan": {"type": float, "min": -1, "max": 1}},
    # Recording
    "start_recording": {},
    "stop_recording": {},
    "toggle_session_record": {},
    "toggle_arrangement_record": {},
    "set_overdub": {"enabled": {"type": bool}},
    "capture_midi": {},
    # Arrangement
    "get_arrangement_length": {},
    "set_arrangement_loop": {"loop_start": {"type": float, "min": 0, "max": 100000}, "loop_length": {"type": float, "min": 0.01, "max": 100000}, "loop_on": {"type": bool, "optional": True}},
    "jump_to_time": {"time": {"type": float, "min": 0, "max": 100000}},
    "get_locators": {},
    "create_locator": {"time": {"type": float, "min": 0, "max": 100000}, "name": {"type": str, "max_length": 256, "optional": True}},
    "delete_locator": {"index": {"type": int, "min": 0, "max": 999}},
    # Session info
    "get_session_path": {},
    "is_session_modified": {},
    "get_cpu_load": {},
    "get_metronome_state": {},
    "set_metronome": {"enabled": {"type": bool}},
    # AI helpers
    "get_scale_notes": {"root": {"type": int, "min": 0, "max": 127}, "scale_type": {"type": str, "max_length": 32}},
    "quantize_clip_notes": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}, "grid": {"type": float, "min": 0.01, "max": 16, "optional": True}, "strength": {"type": float, "min": 0, "max": 1, "optional": True}},
    "humanize_clip_timing": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}, "amount": {"type": float, "min": 0, "max": 1}},
    "humanize_clip_velocity": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}, "amount": {"type": float, "min": 0, "max": 1}},
    "generate_drum_pattern": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}, "style": {"type": str, "max_length": 32, "optional": True}, "length": {"type": float, "min": 0.5, "max": 64, "optional": True}},
    "generate_bassline": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}, "root": {"type": int, "min": 0, "max": 127, "optional": True}, "scale_type": {"type": str, "max_length": 32, "optional": True}, "length": {"type": float, "min": 0.5, "max": 64, "optional": True}},
    # Audio clip editing
    "get_clip_gain": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}},
    "get_clip_pitch": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}},
    "set_clip_gain": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}, "gain": {"type": float, "min": -70, "max": 24}},
    "set_clip_pitch": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}, "pitch": {"type": int, "min": -48, "max": 48}},
    "set_clip_warp_mode": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}, "warp_mode": {"type": int, "min": 0, "max": 6}},
    "get_clip_warp_info": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}},
    # Warp markers
    "get_warp_markers": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}},
    "add_warp_marker": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}, "beat_time": {"type": float, "min": 0, "max": 100000}, "sample_time": {"type": float, "min": 0, "max": 1000000000, "optional": True}},
    "delete_warp_marker": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}, "beat_time": {"type": float, "min": 0, "max": 100000}},
    # Automation
    "get_clip_automation": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}, "parameter_index": {"type": int, "min": 0, "max": MAX_PARAMETER_INDEX, "optional": True}},
    "set_clip_automation": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}, "parameter_index": {"type": int, "min": 0, "max": MAX_PARAMETER_INDEX}, "points": {"type": list, "max_length": 10000}},
    "clear_clip_automation": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}, "parameter_index": {"type": int, "min": 0, "max": MAX_PARAMETER_INDEX, "optional": True}},
    # Group tracks
    "create_group_track": {"track_indices": {"type": list, "max_length": 100}, "name": {"type": str, "max_length": 256, "optional": True}},
    "ungroup_tracks": {"group_track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}},
    "fold_track": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}},
    "unfold_track": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}},
    # Groove
    "get_groove_pool": {},
    "apply_groove": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}, "groove_index": {"type": int, "min": 0, "max": 127}},
    "commit_groove": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "clip_index": {"type": int, "min": 0, "max": MAX_CLIP_INDEX}},
    # Browser
    "browse_path": {"path": {"type": list, "max_length": 20}},
    "get_browser_children": {"uri": {"type": str, "max_length": 2048}},
    "search_browser": {"query": {"type": str, "max_length": 256}, "category": {"type": str, "max_length": 32, "optional": True}},
    "get_browser_tree": {},
    "get_browser_items_at_path": {"path": {"type": list, "max_length": 20}},
    "load_browser_item": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "uri": {"type": str, "max_length": 2048}},
    "load_instrument_or_effect": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "uri": {"type": str, "max_length": 2048}},
    "load_browser_item_to_return": {"return_index": {"type": int, "min": 0, "max": MAX_SEND_INDEX}, "item_uri": {"type": str, "max_length": 2048}},
    # Rack chains
    "get_rack_chains": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "device_index": {"type": int, "min": 0, "max": MAX_DEVICE_INDEX}},
    "select_rack_chain": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "device_index": {"type": int, "min": 0, "max": MAX_DEVICE_INDEX}, "chain_index": {"type": int, "min": 0, "max": 127}},
    "get_device_by_name": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "device_name": {"type": str, "max_length": 256}},
    "load_device_preset": {"track_index": {"type": int, "min": 0, "max": MAX_TRACK_INDEX}, "device_index": {"type": int, "min": 0, "max": MAX_DEVICE_INDEX}, "preset_uri": {"type": str, "max_length": 2048}},
}


def validate_command_params(command: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize command parameters based on schema."""
    if command not in COMMAND_PARAM_SCHEMAS:
        # Command exists in ALLOWED_COMMANDS but has no schema - allow with basic sanitization
        return params

    schema = COMMAND_PARAM_SCHEMAS[command]
    validated = {}

    for param_name, rules in schema.items():
        is_optional = rules.get("optional", False)

        if param_name not in params:
            if not is_optional:
                raise HTTPException(
                    status_code=422,
                    detail=f"Missing required parameter: {param_name}"
                )
            continue

        value = params[param_name]
        expected_type = rules.get("type")

        # Type validation
        if expected_type == int:
            if not isinstance(value, int) or isinstance(value, bool):
                raise HTTPException(status_code=422, detail=f"Parameter {param_name} must be an integer")
            if "min" in rules and value < rules["min"]:
                raise HTTPException(status_code=422, detail=f"Parameter {param_name} must be >= {rules['min']}")
            if "max" in rules and value > rules["max"]:
                raise HTTPException(status_code=422, detail=f"Parameter {param_name} must be <= {rules['max']}")
        elif expected_type == float:
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise HTTPException(status_code=422, detail=f"Parameter {param_name} must be a number")
            value = float(value)
            if "min" in rules and value < rules["min"]:
                raise HTTPException(status_code=422, detail=f"Parameter {param_name} must be >= {rules['min']}")
            if "max" in rules and value > rules["max"]:
                raise HTTPException(status_code=422, detail=f"Parameter {param_name} must be <= {rules['max']}")
        elif expected_type == bool:
            if not isinstance(value, bool):
                raise HTTPException(status_code=422, detail=f"Parameter {param_name} must be a boolean")
        elif expected_type == str:
            if not isinstance(value, str):
                raise HTTPException(status_code=422, detail=f"Parameter {param_name} must be a string")
            if "max_length" in rules and len(value) > rules["max_length"]:
                raise HTTPException(status_code=422, detail=f"Parameter {param_name} exceeds max length of {rules['max_length']}")
            if "allowed_values" in rules and value not in rules["allowed_values"]:
                raise HTTPException(status_code=422, detail=f"Parameter {param_name} must be one of: {sorted(rules['allowed_values'])}")
        elif expected_type == list:
            if not isinstance(value, list):
                raise HTTPException(status_code=422, detail=f"Parameter {param_name} must be a list")
            if "max_length" in rules and len(value) > rules["max_length"]:
                raise HTTPException(status_code=422, detail=f"Parameter {param_name} exceeds max length of {rules['max_length']}")

        validated[param_name] = value

    # Include any extra params that weren't in schema (for flexibility)
    for key, value in params.items():
        if key not in validated:
            validated[key] = value

    return validated


class GenericCommand(BaseModel):
    command: str = Field(..., max_length=64)
    params: Optional[Dict[str, Any]] = None

    @field_validator('command')
    @classmethod
    def validate_command(cls, v):
        if v not in ALLOWED_COMMANDS:
            raise ValueError(f'Unknown command: {v}. Use /api/commands to see available commands.')
        return v


@app.post("/api/command")
def execute_command(cmd: GenericCommand):
    """
    Generic command endpoint for LLM function calling.
    Allows executing any Ableton command by name.
    """
    # Validate params based on command type
    validated_params = validate_command_params(cmd.command, cmd.params or {})
    return ableton.send_command(cmd.command, validated_params)

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

# Server host configuration - default to localhost for security
# Set REST_API_HOST environment variable to override (e.g., "0.0.0.0" for network access)
REST_API_HOST = os.environ.get("REST_API_HOST", "127.0.0.1")
REST_API_PORT = int(os.environ.get("REST_API_PORT", "8000"))

if __name__ == "__main__":
    print("=" * 60)
    print("AbletonMCP REST API Server")
    print("=" * 60)
    print("Endpoints:")
    print(f"  - Health:     GET  http://{REST_API_HOST}:{REST_API_PORT}/health")
    print(f"  - Tools:      GET  http://{REST_API_HOST}:{REST_API_PORT}/tools")
    print(f"  - Command:    POST http://{REST_API_HOST}:{REST_API_PORT}/api/command")
    print(f"  - API Docs:   GET  http://{REST_API_HOST}:{REST_API_PORT}/docs")
    print("")
    print("For Ollama integration, use the /api/command endpoint")
    print("with function calling.")
    if REST_API_HOST == "127.0.0.1":
        print("")
        print("NOTE: Server bound to localhost only for security.")
        print("Set REST_API_HOST=0.0.0.0 to allow network access.")
    print("=" * 60)
    uvicorn.run(app, host=REST_API_HOST, port=REST_API_PORT)
