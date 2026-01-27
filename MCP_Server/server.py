# ableton_mcp_server.py
from mcp.server.fastmcp import FastMCP, Context
import socket
import json
import logging
from dataclasses import dataclass
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any, List, Union

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AbletonMCPServer")

@dataclass
class AbletonConnection:
    host: str
    port: int
    sock: socket.socket = None
    
    def connect(self) -> bool:
        """Connect to the Ableton Remote Script socket server"""
        if self.sock:
            return True
            
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            logger.info(f"Connected to Ableton at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Ableton: {str(e)}")
            self.sock = None
            return False
    
    def disconnect(self):
        """Disconnect from the Ableton Remote Script"""
        if self.sock:
            try:
                self.sock.close()
            except Exception as e:
                logger.error(f"Error disconnecting from Ableton: {str(e)}")
            finally:
                self.sock = None

    def receive_full_response(self, sock, buffer_size=8192):
        """Receive the complete response, potentially in multiple chunks"""
        chunks = []
        sock.settimeout(15.0)  # Increased timeout for operations that might take longer
        
        try:
            while True:
                try:
                    chunk = sock.recv(buffer_size)
                    if not chunk:
                        if not chunks:
                            raise Exception("Connection closed before receiving any data")
                        break
                    
                    chunks.append(chunk)
                    
                    # Check if we've received a complete JSON object
                    try:
                        data = b''.join(chunks)
                        json.loads(data.decode('utf-8'))
                        logger.info(f"Received complete response ({len(data)} bytes)")
                        return data
                    except json.JSONDecodeError:
                        # Incomplete JSON, continue receiving
                        continue
                except socket.timeout:
                    logger.warning("Socket timeout during chunked receive")
                    break
                except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
                    logger.error(f"Socket connection error during receive: {str(e)}")
                    raise
        except Exception as e:
            logger.error(f"Error during receive: {str(e)}")
            raise
            
        # If we get here, we either timed out or broke out of the loop
        if chunks:
            data = b''.join(chunks)
            logger.info(f"Returning data after receive completion ({len(data)} bytes)")
            try:
                json.loads(data.decode('utf-8'))
                return data
            except json.JSONDecodeError:
                raise Exception("Incomplete JSON response received")
        else:
            raise Exception("No data received")

    def send_command(self, command_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a command to Ableton and return the response"""
        if not self.sock and not self.connect():
            raise ConnectionError("Not connected to Ableton")
        
        command = {
            "type": command_type,
            "params": params or {}
        }
        
        # Check if this is a state-modifying command
        is_modifying_command = command_type in [
            "create_midi_track", "create_audio_track", "set_track_name",
            "set_track_mute", "set_track_solo", "set_track_arm",
            "delete_track", "duplicate_track", "set_track_color",
            "create_clip", "delete_clip", "add_notes_to_clip", "set_clip_name",
            "duplicate_clip", "set_clip_color", "set_clip_loop",
            "remove_notes", "remove_all_notes", "transpose_notes",
            "set_tempo", "fire_clip", "stop_clip", "set_device_parameter",
            "toggle_device", "delete_device",
            "start_playback", "stop_playback", "load_instrument_or_effect",
            "load_browser_item",
            "create_scene", "delete_scene", "fire_scene", "stop_scene",
            "set_scene_name", "set_scene_color", "duplicate_scene",
            "undo", "redo",
            "set_send_level", "set_return_volume", "set_return_pan",
            "focus_view", "select_track", "select_scene", "select_clip",
            "start_recording", "stop_recording", "toggle_session_record",
            "toggle_arrangement_record", "set_overdub", "capture_midi",
            # Tier 3 & 4 commands
            "set_arrangement_loop", "jump_to_time", "create_locator", "delete_locator",
            "set_track_input_routing", "set_track_output_routing", "set_metronome",
            "quantize_clip_notes", "humanize_clip_timing", "humanize_clip_velocity",
            "generate_drum_pattern", "generate_bassline"
        ]
        
        try:
            logger.info(f"Sending command: {command_type} with params: {params}")
            
            # Send the command
            self.sock.sendall(json.dumps(command).encode('utf-8'))
            logger.info(f"Command sent, waiting for response...")
            
            # For state-modifying commands, add a small delay to give Ableton time to process
            if is_modifying_command:
                import time
                time.sleep(0.1)  # 100ms delay
            
            # Set timeout based on command type
            timeout = 15.0 if is_modifying_command else 10.0
            self.sock.settimeout(timeout)
            
            # Receive the response
            response_data = self.receive_full_response(self.sock)
            logger.info(f"Received {len(response_data)} bytes of data")
            
            # Parse the response
            response = json.loads(response_data.decode('utf-8'))
            logger.info(f"Response parsed, status: {response.get('status', 'unknown')}")
            
            if response.get("status") == "error":
                logger.error(f"Ableton error: {response.get('message')}")
                raise Exception(response.get("message", "Unknown error from Ableton"))
            
            # For state-modifying commands, add another small delay after receiving response
            if is_modifying_command:
                import time
                time.sleep(0.1)  # 100ms delay
            
            return response.get("result", {})
        except socket.timeout:
            logger.error("Socket timeout while waiting for response from Ableton")
            self.sock = None
            raise Exception("Timeout waiting for Ableton response")
        except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
            logger.error(f"Socket connection error: {str(e)}")
            self.sock = None
            raise Exception(f"Connection to Ableton lost: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Ableton: {str(e)}")
            if 'response_data' in locals() and response_data:
                logger.error(f"Raw response (first 200 bytes): {response_data[:200]}")
            self.sock = None
            raise Exception(f"Invalid response from Ableton: {str(e)}")
        except Exception as e:
            logger.error(f"Error communicating with Ableton: {str(e)}")
            self.sock = None
            raise Exception(f"Communication error with Ableton: {str(e)}")

@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Manage server startup and shutdown lifecycle"""
    try:
        logger.info("AbletonMCP server starting up")
        
        try:
            ableton = get_ableton_connection()
            logger.info("Successfully connected to Ableton on startup")
        except Exception as e:
            logger.warning(f"Could not connect to Ableton on startup: {str(e)}")
            logger.warning("Make sure the Ableton Remote Script is running")
        
        yield {}
    finally:
        global _ableton_connection
        if _ableton_connection:
            logger.info("Disconnecting from Ableton on shutdown")
            _ableton_connection.disconnect()
            _ableton_connection = None
        logger.info("AbletonMCP server shut down")

# Create the MCP server with lifespan support
mcp = FastMCP(
    "AbletonMCP",
    description="Ableton Live integration through the Model Context Protocol",
    lifespan=server_lifespan
)

# Global connection for resources
_ableton_connection = None

def get_ableton_connection():
    """Get or create a persistent Ableton connection"""
    global _ableton_connection
    
    if _ableton_connection is not None:
        try:
            # Test the connection with a simple ping
            # We'll try to send an empty message, which should fail if the connection is dead
            # but won't affect Ableton if it's alive
            _ableton_connection.sock.settimeout(1.0)
            _ableton_connection.sock.sendall(b'')
            return _ableton_connection
        except Exception as e:
            logger.warning(f"Existing connection is no longer valid: {str(e)}")
            try:
                _ableton_connection.disconnect()
            except:
                pass
            _ableton_connection = None
    
    # Connection doesn't exist or is invalid, create a new one
    if _ableton_connection is None:
        # Try to connect up to 3 times with a short delay between attempts
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"Connecting to Ableton (attempt {attempt}/{max_attempts})...")
                _ableton_connection = AbletonConnection(host="localhost", port=9877)
                if _ableton_connection.connect():
                    logger.info("Created new persistent connection to Ableton")
                    
                    # Validate connection with a simple command
                    try:
                        # Get session info as a test
                        _ableton_connection.send_command("get_session_info")
                        logger.info("Connection validated successfully")
                        return _ableton_connection
                    except Exception as e:
                        logger.error(f"Connection validation failed: {str(e)}")
                        _ableton_connection.disconnect()
                        _ableton_connection = None
                        # Continue to next attempt
                else:
                    _ableton_connection = None
            except Exception as e:
                logger.error(f"Connection attempt {attempt} failed: {str(e)}")
                if _ableton_connection:
                    _ableton_connection.disconnect()
                    _ableton_connection = None
            
            # Wait before trying again, but only if we have more attempts left
            if attempt < max_attempts:
                import time
                time.sleep(1.0)
        
        # If we get here, all connection attempts failed
        if _ableton_connection is None:
            logger.error("Failed to connect to Ableton after multiple attempts")
            raise Exception("Could not connect to Ableton. Make sure the Remote Script is running.")
    
    return _ableton_connection


# Core Tool endpoints

@mcp.tool()
def health_check(ctx: Context) -> str:
    """Check if Ableton Live is connected and responsive."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("health_check")
        return json.dumps({
            "connected": True,
            "status": result.get("status", "ok"),
            "tempo": result.get("tempo"),
            "is_playing": result.get("is_playing"),
            "track_count": result.get("track_count")
        }, indent=2)
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return json.dumps({
            "connected": False,
            "error": str(e)
        }, indent=2)

@mcp.tool()
def get_playback_position(ctx: Context) -> str:
    """Get the current playback position and transport state."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_playback_position")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting playback position: {str(e)}")
        return f"Error getting playback position: {str(e)}"

@mcp.tool()
def get_session_info(ctx: Context) -> str:
    """Get detailed information about the current Ableton session"""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_session_info")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting session info from Ableton: {str(e)}")
        return f"Error getting session info: {str(e)}"

@mcp.tool()
def get_track_info(ctx: Context, track_index: int) -> str:
    """
    Get detailed information about a specific track in Ableton.
    
    Parameters:
    - track_index: The index of the track to get information about
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_track_info", {"track_index": track_index})
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting track info from Ableton: {str(e)}")
        return f"Error getting track info: {str(e)}"

@mcp.tool()
def create_midi_track(ctx: Context, index: int = -1) -> str:
    """
    Create a new MIDI track in the Ableton session.

    Parameters:
    - index: The index to insert the track at (-1 = end of list)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("create_midi_track", {"index": index})
        return f"Created new MIDI track: {result.get('name', 'unknown')}"
    except Exception as e:
        logger.error(f"Error creating MIDI track: {str(e)}")
        return f"Error creating MIDI track: {str(e)}"

@mcp.tool()
def create_audio_track(ctx: Context, index: int = -1) -> str:
    """
    Create a new audio track in the Ableton session.

    Parameters:
    - index: The index to insert the track at (-1 = end of list)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("create_audio_track", {"index": index})
        return f"Created new audio track: {result.get('name', 'unknown')} at index {result.get('index')}"
    except Exception as e:
        logger.error(f"Error creating audio track: {str(e)}")
        return f"Error creating audio track: {str(e)}"

@mcp.tool()
def set_track_name(ctx: Context, track_index: int, name: str) -> str:
    """
    Set the name of a track.

    Parameters:
    - track_index: The index of the track to rename
    - name: The new name for the track
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_track_name", {"track_index": track_index, "name": name})
        return f"Renamed track to: {result.get('name', name)}"
    except Exception as e:
        logger.error(f"Error setting track name: {str(e)}")
        return f"Error setting track name: {str(e)}"

@mcp.tool()
def set_track_mute(ctx: Context, track_index: int, mute: bool) -> str:
    """
    Set the mute state of a track.

    Parameters:
    - track_index: The index of the track
    - mute: True to mute, False to unmute
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_track_mute", {"track_index": track_index, "mute": mute})
        state = "muted" if result.get("mute") else "unmuted"
        return f"Track {track_index} is now {state}"
    except Exception as e:
        logger.error(f"Error setting track mute: {str(e)}")
        return f"Error setting track mute: {str(e)}"

@mcp.tool()
def set_track_solo(ctx: Context, track_index: int, solo: bool) -> str:
    """
    Set the solo state of a track.

    Parameters:
    - track_index: The index of the track
    - solo: True to solo, False to unsolo
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_track_solo", {"track_index": track_index, "solo": solo})
        state = "soloed" if result.get("solo") else "unsoloed"
        return f"Track {track_index} is now {state}"
    except Exception as e:
        logger.error(f"Error setting track solo: {str(e)}")
        return f"Error setting track solo: {str(e)}"

@mcp.tool()
def set_track_arm(ctx: Context, track_index: int, arm: bool) -> str:
    """
    Set the arm (record enable) state of a track.

    Parameters:
    - track_index: The index of the track
    - arm: True to arm for recording, False to disarm
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_track_arm", {"track_index": track_index, "arm": arm})
        if "error" in result:
            return f"Track {track_index}: {result.get('error')}"
        state = "armed" if result.get("arm") else "disarmed"
        return f"Track {track_index} is now {state}"
    except Exception as e:
        logger.error(f"Error setting track arm: {str(e)}")
        return f"Error setting track arm: {str(e)}"

@mcp.tool()
def set_track_volume(ctx: Context, track_index: int, volume: float) -> str:
    """
    Set the volume of a track.

    Parameters:
    - track_index: The index of the track
    - volume: Volume level from 0.0 (silent) to 1.0 (unity gain). 0.85 is Ableton's default.
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_track_volume", {"track_index": track_index, "volume": volume})
        return f"Track {track_index} volume set to {result.get('volume', volume):.2f}"
    except Exception as e:
        logger.error(f"Error setting track volume: {str(e)}")
        return f"Error setting track volume: {str(e)}"

@mcp.tool()
def set_track_pan(ctx: Context, track_index: int, pan: float) -> str:
    """
    Set the panning of a track.

    Parameters:
    - track_index: The index of the track
    - pan: Pan position from -1.0 (full left) to 1.0 (full right). 0.0 is center.
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_track_pan", {"track_index": track_index, "pan": pan})
        return f"Track {track_index} pan set to {result.get('panning', pan):.2f}"
    except Exception as e:
        logger.error(f"Error setting track pan: {str(e)}")
        return f"Error setting track pan: {str(e)}"

@mcp.tool()
def create_clip(ctx: Context, track_index: int, clip_index: int, length: float = 4.0) -> str:
    """
    Create a new MIDI clip in the specified track and clip slot.

    Parameters:
    - track_index: The index of the track to create the clip in
    - clip_index: The index of the clip slot to create the clip in
    - length: The length of the clip in beats (default: 4.0)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("create_clip", {
            "track_index": track_index,
            "clip_index": clip_index,
            "length": length
        })
        return f"Created new clip at track {track_index}, slot {clip_index} with length {length} beats"
    except Exception as e:
        logger.error(f"Error creating clip: {str(e)}")
        return f"Error creating clip: {str(e)}"

@mcp.tool()
def delete_clip(ctx: Context, track_index: int, clip_index: int) -> str:
    """
    Delete a clip from a clip slot.

    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("delete_clip", {
            "track_index": track_index,
            "clip_index": clip_index
        })
        return f"Deleted clip '{result.get('clip_name')}' from track {track_index}, slot {clip_index}"
    except Exception as e:
        logger.error(f"Error deleting clip: {str(e)}")
        return f"Error deleting clip: {str(e)}"

@mcp.tool()
def get_clip_notes(ctx: Context, track_index: int, clip_index: int) -> str:
    """
    Get all MIDI notes from a clip.

    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_clip_notes", {
            "track_index": track_index,
            "clip_index": clip_index
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting clip notes: {str(e)}")
        return f"Error getting clip notes: {str(e)}"

@mcp.tool()
def add_notes_to_clip(
    ctx: Context, 
    track_index: int, 
    clip_index: int, 
    notes: List[Dict[str, Union[int, float, bool]]]
) -> str:
    """
    Add MIDI notes to a clip.
    
    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    - notes: List of note dictionaries, each with pitch, start_time, duration, velocity, and mute
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("add_notes_to_clip", {
            "track_index": track_index,
            "clip_index": clip_index,
            "notes": notes
        })
        return f"Added {len(notes)} notes to clip at track {track_index}, slot {clip_index}"
    except Exception as e:
        logger.error(f"Error adding notes to clip: {str(e)}")
        return f"Error adding notes to clip: {str(e)}"

@mcp.tool()
def set_clip_name(ctx: Context, track_index: int, clip_index: int, name: str) -> str:
    """
    Set the name of a clip.
    
    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    - name: The new name for the clip
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_clip_name", {
            "track_index": track_index,
            "clip_index": clip_index,
            "name": name
        })
        return f"Renamed clip at track {track_index}, slot {clip_index} to '{name}'"
    except Exception as e:
        logger.error(f"Error setting clip name: {str(e)}")
        return f"Error setting clip name: {str(e)}"

@mcp.tool()
def set_tempo(ctx: Context, tempo: float) -> str:
    """
    Set the tempo of the Ableton session.
    
    Parameters:
    - tempo: The new tempo in BPM
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_tempo", {"tempo": tempo})
        return f"Set tempo to {tempo} BPM"
    except Exception as e:
        logger.error(f"Error setting tempo: {str(e)}")
        return f"Error setting tempo: {str(e)}"


@mcp.tool()
def load_instrument_or_effect(ctx: Context, track_index: int, uri: str) -> str:
    """
    Load an instrument or effect onto a track using its URI.
    
    Parameters:
    - track_index: The index of the track to load the instrument on
    - uri: The URI of the instrument or effect to load (e.g., 'query:Synths#Instrument%20Rack:Bass:FileId_5116')
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("load_browser_item", {
            "track_index": track_index,
            "item_uri": uri
        })
        
        # Check if the instrument was loaded successfully
        if result.get("loaded", False):
            new_devices = result.get("new_devices", [])
            if new_devices:
                return f"Loaded instrument with URI '{uri}' on track {track_index}. New devices: {', '.join(new_devices)}"
            else:
                devices = result.get("devices_after", [])
                return f"Loaded instrument with URI '{uri}' on track {track_index}. Devices on track: {', '.join(devices)}"
        else:
            return f"Failed to load instrument with URI '{uri}'"
    except Exception as e:
        logger.error(f"Error loading instrument by URI: {str(e)}")
        return f"Error loading instrument by URI: {str(e)}"

@mcp.tool()
def fire_clip(ctx: Context, track_index: int, clip_index: int) -> str:
    """
    Start playing a clip.
    
    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("fire_clip", {
            "track_index": track_index,
            "clip_index": clip_index
        })
        return f"Started playing clip at track {track_index}, slot {clip_index}"
    except Exception as e:
        logger.error(f"Error firing clip: {str(e)}")
        return f"Error firing clip: {str(e)}"

@mcp.tool()
def stop_clip(ctx: Context, track_index: int, clip_index: int) -> str:
    """
    Stop playing a clip.
    
    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("stop_clip", {
            "track_index": track_index,
            "clip_index": clip_index
        })
        return f"Stopped clip at track {track_index}, slot {clip_index}"
    except Exception as e:
        logger.error(f"Error stopping clip: {str(e)}")
        return f"Error stopping clip: {str(e)}"

@mcp.tool()
def start_playback(ctx: Context) -> str:
    """Start playing the Ableton session."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("start_playback")
        return "Started playback"
    except Exception as e:
        logger.error(f"Error starting playback: {str(e)}")
        return f"Error starting playback: {str(e)}"

@mcp.tool()
def stop_playback(ctx: Context) -> str:
    """Stop playing the Ableton session."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("stop_playback")
        return "Stopped playback"
    except Exception as e:
        logger.error(f"Error stopping playback: {str(e)}")
        return f"Error stopping playback: {str(e)}"

@mcp.tool()
def get_device_parameters(ctx: Context, track_index: int, device_index: int) -> str:
    """
    Get all parameters from a device on a track.

    Parameters:
    - track_index: The index of the track containing the device
    - device_index: The index of the device on the track
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_device_parameters", {
            "track_index": track_index,
            "device_index": device_index
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting device parameters: {str(e)}")
        return f"Error getting device parameters: {str(e)}"

@mcp.tool()
def set_device_parameter(ctx: Context, track_index: int, device_index: int, parameter_index: int, value: float) -> str:
    """
    Set a device parameter value.

    Parameters:
    - track_index: The index of the track containing the device
    - device_index: The index of the device on the track
    - parameter_index: The index of the parameter to set
    - value: The new value for the parameter (will be clamped to valid range)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_device_parameter", {
            "track_index": track_index,
            "device_index": device_index,
            "parameter_index": parameter_index,
            "value": value
        })
        return f"Set {result.get('parameter_name')} to {result.get('value')} (range: {result.get('min')} - {result.get('max')})"
    except Exception as e:
        logger.error(f"Error setting device parameter: {str(e)}")
        return f"Error setting device parameter: {str(e)}"

# ==================== SCENE MANAGEMENT ====================

@mcp.tool()
def get_all_scenes(ctx: Context) -> str:
    """Get information about all scenes in the session."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_all_scenes")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting scenes: {str(e)}")
        return f"Error getting scenes: {str(e)}"

@mcp.tool()
def create_scene(ctx: Context, index: int = -1) -> str:
    """
    Create a new scene.

    Parameters:
    - index: The index to insert the scene at (-1 = end of list)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("create_scene", {"index": index})
        return f"Created new scene '{result.get('name')}' at index {result.get('index')}"
    except Exception as e:
        logger.error(f"Error creating scene: {str(e)}")
        return f"Error creating scene: {str(e)}"

@mcp.tool()
def delete_scene(ctx: Context, scene_index: int) -> str:
    """
    Delete a scene.

    Parameters:
    - scene_index: The index of the scene to delete
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("delete_scene", {"scene_index": scene_index})
        return f"Deleted scene '{result.get('scene_name')}' at index {scene_index}"
    except Exception as e:
        logger.error(f"Error deleting scene: {str(e)}")
        return f"Error deleting scene: {str(e)}"

@mcp.tool()
def fire_scene(ctx: Context, scene_index: int) -> str:
    """
    Fire (trigger) a scene to play all clips in that row.

    Parameters:
    - scene_index: The index of the scene to fire
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("fire_scene", {"scene_index": scene_index})
        return f"Fired scene '{result.get('scene_name')}' at index {scene_index}"
    except Exception as e:
        logger.error(f"Error firing scene: {str(e)}")
        return f"Error firing scene: {str(e)}"

@mcp.tool()
def stop_scene(ctx: Context, scene_index: int) -> str:
    """
    Stop all clips in a scene.

    Parameters:
    - scene_index: The index of the scene to stop
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("stop_scene", {"scene_index": scene_index})
        return f"Stopped scene at index {scene_index}"
    except Exception as e:
        logger.error(f"Error stopping scene: {str(e)}")
        return f"Error stopping scene: {str(e)}"

@mcp.tool()
def set_scene_name(ctx: Context, scene_index: int, name: str) -> str:
    """
    Set the name of a scene.

    Parameters:
    - scene_index: The index of the scene to rename
    - name: The new name for the scene
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_scene_name", {"scene_index": scene_index, "name": name})
        return f"Renamed scene {scene_index} to '{result.get('name')}'"
    except Exception as e:
        logger.error(f"Error setting scene name: {str(e)}")
        return f"Error setting scene name: {str(e)}"

@mcp.tool()
def set_scene_color(ctx: Context, scene_index: int, color: int) -> str:
    """
    Set the color of a scene.

    Parameters:
    - scene_index: The index of the scene
    - color: The color index (0-69 in Ableton's color palette)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_scene_color", {"scene_index": scene_index, "color": color})
        return f"Set scene {scene_index} color to {result.get('color_index')}"
    except Exception as e:
        logger.error(f"Error setting scene color: {str(e)}")
        return f"Error setting scene color: {str(e)}"

@mcp.tool()
def duplicate_scene(ctx: Context, scene_index: int) -> str:
    """
    Duplicate a scene.

    Parameters:
    - scene_index: The index of the scene to duplicate
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("duplicate_scene", {"scene_index": scene_index})
        return f"Duplicated scene {scene_index}, new scene at index {result.get('new_index')}"
    except Exception as e:
        logger.error(f"Error duplicating scene: {str(e)}")
        return f"Error duplicating scene: {str(e)}"

# ==================== TRACK MANAGEMENT ====================

@mcp.tool()
def delete_track(ctx: Context, track_index: int) -> str:
    """
    Delete a track.

    Parameters:
    - track_index: The index of the track to delete
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("delete_track", {"track_index": track_index})
        return f"Deleted track '{result.get('track_name')}' at index {track_index}"
    except Exception as e:
        logger.error(f"Error deleting track: {str(e)}")
        return f"Error deleting track: {str(e)}"

@mcp.tool()
def duplicate_track(ctx: Context, track_index: int) -> str:
    """
    Duplicate a track with all its clips and devices.

    Parameters:
    - track_index: The index of the track to duplicate
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("duplicate_track", {"track_index": track_index})
        return f"Duplicated track {track_index}, new track '{result.get('new_name')}' at index {result.get('new_index')}"
    except Exception as e:
        logger.error(f"Error duplicating track: {str(e)}")
        return f"Error duplicating track: {str(e)}"

@mcp.tool()
def set_track_color(ctx: Context, track_index: int, color: int) -> str:
    """
    Set the color of a track.

    Parameters:
    - track_index: The index of the track
    - color: The color index (0-69 in Ableton's color palette)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_track_color", {"track_index": track_index, "color": color})
        return f"Set track {track_index} color to {result.get('color_index')}"
    except Exception as e:
        logger.error(f"Error setting track color: {str(e)}")
        return f"Error setting track color: {str(e)}"

# ==================== DEVICE MANAGEMENT ====================

@mcp.tool()
def toggle_device(ctx: Context, track_index: int, device_index: int) -> str:
    """
    Toggle a device on or off.

    Parameters:
    - track_index: The index of the track containing the device
    - device_index: The index of the device on the track
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("toggle_device", {
            "track_index": track_index,
            "device_index": device_index
        })
        state = "on" if result.get("is_active") else "off"
        return f"Toggled device '{result.get('device_name')}' {state}"
    except Exception as e:
        logger.error(f"Error toggling device: {str(e)}")
        return f"Error toggling device: {str(e)}"

@mcp.tool()
def delete_device(ctx: Context, track_index: int, device_index: int) -> str:
    """
    Delete a device from a track.

    Parameters:
    - track_index: The index of the track containing the device
    - device_index: The index of the device to delete
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("delete_device", {
            "track_index": track_index,
            "device_index": device_index
        })
        return f"Deleted device '{result.get('device_name')}' from track {track_index}"
    except Exception as e:
        logger.error(f"Error deleting device: {str(e)}")
        return f"Error deleting device: {str(e)}"

# ==================== CLIP MANAGEMENT ====================

@mcp.tool()
def duplicate_clip(ctx: Context, track_index: int, clip_index: int) -> str:
    """
    Duplicate a clip to the next empty slot.

    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("duplicate_clip", {
            "track_index": track_index,
            "clip_index": clip_index
        })
        return f"Duplicated clip to slot {result.get('new_index')}"
    except Exception as e:
        logger.error(f"Error duplicating clip: {str(e)}")
        return f"Error duplicating clip: {str(e)}"

@mcp.tool()
def set_clip_color(ctx: Context, track_index: int, clip_index: int, color: int) -> str:
    """
    Set the color of a clip.

    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    - color: The color index (0-69 in Ableton's color palette)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_clip_color", {
            "track_index": track_index,
            "clip_index": clip_index,
            "color": color
        })
        return f"Set clip color to {result.get('color_index')}"
    except Exception as e:
        logger.error(f"Error setting clip color: {str(e)}")
        return f"Error setting clip color: {str(e)}"

@mcp.tool()
def set_clip_loop(ctx: Context, track_index: int, clip_index: int, loop_start: float = 0.0, loop_end: float = 4.0, looping: bool = True) -> str:
    """
    Set the loop settings of a clip.

    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    - loop_start: The start point of the loop in beats
    - loop_end: The end point of the loop in beats
    - looping: Whether looping is enabled
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_clip_loop", {
            "track_index": track_index,
            "clip_index": clip_index,
            "loop_start": loop_start,
            "loop_end": loop_end,
            "looping": looping
        })
        return f"Set clip loop: {result.get('loop_start')} - {result.get('loop_end')}, looping: {result.get('looping')}"
    except Exception as e:
        logger.error(f"Error setting clip loop: {str(e)}")
        return f"Error setting clip loop: {str(e)}"

# ==================== NOTE EDITING ====================

@mcp.tool()
def remove_notes(ctx: Context, track_index: int, clip_index: int, from_time: float = 0.0, time_span: float = 4.0, from_pitch: int = 0, pitch_span: int = 128) -> str:
    """
    Remove notes from a clip within a specified range.

    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    - from_time: Start time in beats
    - time_span: Duration in beats
    - from_pitch: Starting MIDI pitch (0-127)
    - pitch_span: Number of pitches to include
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("remove_notes", {
            "track_index": track_index,
            "clip_index": clip_index,
            "from_time": from_time,
            "time_span": time_span,
            "from_pitch": from_pitch,
            "pitch_span": pitch_span
        })
        return f"Removed notes from clip (time: {from_time}-{from_time + time_span}, pitch: {from_pitch}-{from_pitch + pitch_span})"
    except Exception as e:
        logger.error(f"Error removing notes: {str(e)}")
        return f"Error removing notes: {str(e)}"

@mcp.tool()
def remove_all_notes(ctx: Context, track_index: int, clip_index: int) -> str:
    """
    Remove all notes from a clip.

    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("remove_all_notes", {
            "track_index": track_index,
            "clip_index": clip_index
        })
        return f"Removed all notes from clip at track {track_index}, slot {clip_index}"
    except Exception as e:
        logger.error(f"Error removing all notes: {str(e)}")
        return f"Error removing all notes: {str(e)}"

@mcp.tool()
def transpose_notes(ctx: Context, track_index: int, clip_index: int, semitones: int) -> str:
    """
    Transpose all notes in a clip.

    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    - semitones: Number of semitones to transpose (positive = up, negative = down)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("transpose_notes", {
            "track_index": track_index,
            "clip_index": clip_index,
            "semitones": semitones
        })
        direction = "up" if semitones > 0 else "down"
        return f"Transposed {result.get('note_count')} notes {direction} by {abs(semitones)} semitones"
    except Exception as e:
        logger.error(f"Error transposing notes: {str(e)}")
        return f"Error transposing notes: {str(e)}"

# ==================== UNDO/REDO ====================

@mcp.tool()
def undo(ctx: Context) -> str:
    """Undo the last operation in Ableton."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("undo")
        if result.get("undone"):
            return "Undid last operation"
        else:
            return result.get("error", "Nothing to undo")
    except Exception as e:
        logger.error(f"Error undoing: {str(e)}")
        return f"Error undoing: {str(e)}"

@mcp.tool()
def redo(ctx: Context) -> str:
    """Redo the last undone operation in Ableton."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("redo")
        if result.get("redone"):
            return "Redid last operation"
        else:
            return result.get("error", "Nothing to redo")
    except Exception as e:
        logger.error(f"Error redoing: {str(e)}")
        return f"Error redoing: {str(e)}"

# ==================== RETURN/SEND TRACK CONTROL ====================

@mcp.tool()
def get_return_tracks(ctx: Context) -> str:
    """Get information about all return (aux) tracks."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_return_tracks")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting return tracks: {str(e)}")
        return f"Error getting return tracks: {str(e)}"

@mcp.tool()
def get_return_track_info(ctx: Context, return_index: int) -> str:
    """
    Get detailed information about a return track.

    Parameters:
    - return_index: The index of the return track
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_return_track_info", {"return_index": return_index})
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting return track info: {str(e)}")
        return f"Error getting return track info: {str(e)}"

@mcp.tool()
def set_send_level(ctx: Context, track_index: int, send_index: int, level: float) -> str:
    """
    Set the send level from a track to a return track.

    Parameters:
    - track_index: The index of the source track
    - send_index: The index of the send (corresponds to return track index)
    - level: The send level (0.0 to 1.0)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_send_level", {
            "track_index": track_index,
            "send_index": send_index,
            "level": level
        })
        return f"Set track {track_index} send {send_index} to {result.get('level')}"
    except Exception as e:
        logger.error(f"Error setting send level: {str(e)}")
        return f"Error setting send level: {str(e)}"

@mcp.tool()
def set_return_volume(ctx: Context, return_index: int, volume: float) -> str:
    """
    Set the volume of a return track.

    Parameters:
    - return_index: The index of the return track
    - volume: The volume level (0.0 to 1.0)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_return_volume", {
            "return_index": return_index,
            "volume": volume
        })
        return f"Set return track {return_index} volume to {result.get('volume')}"
    except Exception as e:
        logger.error(f"Error setting return volume: {str(e)}")
        return f"Error setting return volume: {str(e)}"

@mcp.tool()
def set_return_pan(ctx: Context, return_index: int, pan: float) -> str:
    """
    Set the panning of a return track.

    Parameters:
    - return_index: The index of the return track
    - pan: The pan position (-1.0 = left, 0.0 = center, 1.0 = right)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_return_pan", {
            "return_index": return_index,
            "pan": pan
        })
        return f"Set return track {return_index} pan to {result.get('panning')}"
    except Exception as e:
        logger.error(f"Error setting return pan: {str(e)}")
        return f"Error setting return pan: {str(e)}"

# ==================== VIEW CONTROL ====================

@mcp.tool()
def get_current_view(ctx: Context) -> str:
    """Get information about the current view state (selected track, scene, etc.)."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_current_view")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting current view: {str(e)}")
        return f"Error getting current view: {str(e)}"

@mcp.tool()
def focus_view(ctx: Context, view_name: str) -> str:
    """
    Focus a specific view in Ableton.

    Parameters:
    - view_name: The name of the view (Session, Arranger, Detail, etc.)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("focus_view", {"view_name": view_name})
        return f"Focused view: {view_name}"
    except Exception as e:
        logger.error(f"Error focusing view: {str(e)}")
        return f"Error focusing view: {str(e)}"

@mcp.tool()
def select_track(ctx: Context, track_index: int) -> str:
    """
    Select a track.

    Parameters:
    - track_index: The index of the track to select
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("select_track", {"track_index": track_index})
        return f"Selected track '{result.get('track_name')}' at index {track_index}"
    except Exception as e:
        logger.error(f"Error selecting track: {str(e)}")
        return f"Error selecting track: {str(e)}"

@mcp.tool()
def select_scene(ctx: Context, scene_index: int) -> str:
    """
    Select a scene.

    Parameters:
    - scene_index: The index of the scene to select
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("select_scene", {"scene_index": scene_index})
        return f"Selected scene '{result.get('scene_name')}' at index {scene_index}"
    except Exception as e:
        logger.error(f"Error selecting scene: {str(e)}")
        return f"Error selecting scene: {str(e)}"

@mcp.tool()
def select_clip(ctx: Context, track_index: int, clip_index: int) -> str:
    """
    Select a clip slot.

    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("select_clip", {
            "track_index": track_index,
            "clip_index": clip_index
        })
        has_clip = "with clip" if result.get("has_clip") else "empty"
        return f"Selected clip slot at track {track_index}, slot {clip_index} ({has_clip})"
    except Exception as e:
        logger.error(f"Error selecting clip: {str(e)}")
        return f"Error selecting clip: {str(e)}"

# ==================== RECORDING CONTROL ====================

@mcp.tool()
def start_recording(ctx: Context) -> str:
    """Start recording in Ableton."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("start_recording")
        return "Started recording" if result.get("recording") else "Failed to start recording"
    except Exception as e:
        logger.error(f"Error starting recording: {str(e)}")
        return f"Error starting recording: {str(e)}"

@mcp.tool()
def stop_recording(ctx: Context) -> str:
    """Stop recording in Ableton."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("stop_recording")
        return "Stopped recording"
    except Exception as e:
        logger.error(f"Error stopping recording: {str(e)}")
        return f"Error stopping recording: {str(e)}"

@mcp.tool()
def toggle_session_record(ctx: Context) -> str:
    """Toggle session record mode."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("toggle_session_record")
        if "error" in result:
            return result.get("error")
        state = "on" if result.get("session_record") else "off"
        return f"Session record is now {state}"
    except Exception as e:
        logger.error(f"Error toggling session record: {str(e)}")
        return f"Error toggling session record: {str(e)}"

@mcp.tool()
def toggle_arrangement_record(ctx: Context) -> str:
    """Toggle arrangement record mode."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("toggle_arrangement_record")
        state = "on" if result.get("arrangement_record") else "off"
        return f"Arrangement record is now {state}"
    except Exception as e:
        logger.error(f"Error toggling arrangement record: {str(e)}")
        return f"Error toggling arrangement record: {str(e)}"

@mcp.tool()
def set_overdub(ctx: Context, enabled: bool) -> str:
    """
    Set overdub mode.

    Parameters:
    - enabled: True to enable overdub, False to disable
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_overdub", {"enabled": enabled})
        if "error" in result:
            return result.get("error")
        state = "enabled" if result.get("overdub") else "disabled"
        return f"Overdub is now {state}"
    except Exception as e:
        logger.error(f"Error setting overdub: {str(e)}")
        return f"Error setting overdub: {str(e)}"

@mcp.tool()
def capture_midi(ctx: Context) -> str:
    """Capture MIDI that was played recently (like Ableton's Capture feature)."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("capture_midi")
        if result.get("captured"):
            return "Captured MIDI"
        else:
            return result.get("error", "Failed to capture MIDI")
    except Exception as e:
        logger.error(f"Error capturing MIDI: {str(e)}")
        return f"Error capturing MIDI: {str(e)}"

# ==================== ARRANGEMENT VIEW ====================

@mcp.tool()
def get_arrangement_length(ctx: Context) -> str:
    """Get the length and loop settings of the arrangement."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_arrangement_length")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting arrangement length: {str(e)}")
        return f"Error getting arrangement length: {str(e)}"

@mcp.tool()
def set_arrangement_loop(ctx: Context, start: float, end: float, enabled: bool = True) -> str:
    """
    Set the arrangement loop region.

    Parameters:
    - start: Loop start position in beats
    - end: Loop end position in beats
    - enabled: Whether to enable looping
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_arrangement_loop", {
            "start": start,
            "end": end,
            "enabled": enabled
        })
        return f"Set loop from {result.get('loop_start')} to {result.get('loop_start') + result.get('loop_length')}"
    except Exception as e:
        logger.error(f"Error setting arrangement loop: {str(e)}")
        return f"Error setting arrangement loop: {str(e)}"

@mcp.tool()
def jump_to_time(ctx: Context, time: float) -> str:
    """
    Jump to a specific time in the arrangement.

    Parameters:
    - time: Position in beats to jump to
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("jump_to_time", {"time": time})
        return f"Jumped to position {result.get('current_time')}"
    except Exception as e:
        logger.error(f"Error jumping to time: {str(e)}")
        return f"Error jumping to time: {str(e)}"

@mcp.tool()
def get_locators(ctx: Context) -> str:
    """Get all locators/cue points in the arrangement."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_locators")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting locators: {str(e)}")
        return f"Error getting locators: {str(e)}"

@mcp.tool()
def create_locator(ctx: Context, time: float, name: str = "") -> str:
    """
    Create a new locator/cue point.

    Parameters:
    - time: Position in beats for the locator
    - name: Name for the locator
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("create_locator", {"time": time, "name": name})
        if result.get("created"):
            return f"Created locator '{name}' at {time}"
        else:
            return result.get("error", "Failed to create locator")
    except Exception as e:
        logger.error(f"Error creating locator: {str(e)}")
        return f"Error creating locator: {str(e)}"

@mcp.tool()
def delete_locator(ctx: Context, locator_index: int) -> str:
    """
    Delete a locator.

    Parameters:
    - locator_index: Index of the locator to delete
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("delete_locator", {"locator_index": locator_index})
        if result.get("deleted"):
            return f"Deleted locator '{result.get('name')}'"
        else:
            return result.get("error", "Failed to delete locator")
    except Exception as e:
        logger.error(f"Error deleting locator: {str(e)}")
        return f"Error deleting locator: {str(e)}"

# ==================== INPUT/OUTPUT ROUTING ====================

@mcp.tool()
def get_track_input_routing(ctx: Context, track_index: int) -> str:
    """
    Get the input routing of a track.

    Parameters:
    - track_index: The index of the track
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_track_input_routing", {"track_index": track_index})
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting track input routing: {str(e)}")
        return f"Error getting track input routing: {str(e)}"

@mcp.tool()
def get_track_output_routing(ctx: Context, track_index: int) -> str:
    """
    Get the output routing of a track.

    Parameters:
    - track_index: The index of the track
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_track_output_routing", {"track_index": track_index})
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting track output routing: {str(e)}")
        return f"Error getting track output routing: {str(e)}"

@mcp.tool()
def get_available_inputs(ctx: Context, track_index: int) -> str:
    """
    Get available input routing options for a track.

    Parameters:
    - track_index: The index of the track
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_available_inputs", {"track_index": track_index})
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting available inputs: {str(e)}")
        return f"Error getting available inputs: {str(e)}"

@mcp.tool()
def get_available_outputs(ctx: Context, track_index: int) -> str:
    """
    Get available output routing options for a track.

    Parameters:
    - track_index: The index of the track
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_available_outputs", {"track_index": track_index})
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting available outputs: {str(e)}")
        return f"Error getting available outputs: {str(e)}"

@mcp.tool()
def set_track_input_routing(ctx: Context, track_index: int, routing_type: str, routing_channel: str = "") -> str:
    """
    Set the input routing of a track.

    Parameters:
    - track_index: The index of the track
    - routing_type: The input routing type (use get_available_inputs to see options)
    - routing_channel: The input channel (optional)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_track_input_routing", {
            "track_index": track_index,
            "routing_type": routing_type,
            "routing_channel": routing_channel
        })
        return f"Set track {track_index} input to {result.get('input_routing_type')}"
    except Exception as e:
        logger.error(f"Error setting track input routing: {str(e)}")
        return f"Error setting track input routing: {str(e)}"

@mcp.tool()
def set_track_output_routing(ctx: Context, track_index: int, routing_type: str, routing_channel: str = "") -> str:
    """
    Set the output routing of a track.

    Parameters:
    - track_index: The index of the track
    - routing_type: The output routing type (use get_available_outputs to see options)
    - routing_channel: The output channel (optional)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_track_output_routing", {
            "track_index": track_index,
            "routing_type": routing_type,
            "routing_channel": routing_channel
        })
        return f"Set track {track_index} output to {result.get('output_routing_type')}"
    except Exception as e:
        logger.error(f"Error setting track output routing: {str(e)}")
        return f"Error setting track output routing: {str(e)}"

# ==================== PERFORMANCE & SESSION ====================

@mcp.tool()
def get_cpu_load(ctx: Context) -> str:
    """Get the current CPU load of Ableton."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_cpu_load")
        if result.get("cpu_load") is not None:
            return f"CPU Load: {result.get('cpu_load')}%"
        else:
            return "CPU load information not available"
    except Exception as e:
        logger.error(f"Error getting CPU load: {str(e)}")
        return f"Error getting CPU load: {str(e)}"

@mcp.tool()
def get_session_path(ctx: Context) -> str:
    """Get the file path of the current session."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_session_path")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting session path: {str(e)}")
        return f"Error getting session path: {str(e)}"

@mcp.tool()
def is_session_modified(ctx: Context) -> str:
    """Check if the session has unsaved changes."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("is_session_modified")
        if result.get("modified") is not None:
            status = "has unsaved changes" if result.get("modified") else "is saved"
            return f"Session {status}"
        else:
            return "Session modification status not available"
    except Exception as e:
        logger.error(f"Error checking session modified: {str(e)}")
        return f"Error checking session modified: {str(e)}"

@mcp.tool()
def get_metronome_state(ctx: Context) -> str:
    """Get the current metronome state."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_metronome_state")
        if result.get("enabled") is not None:
            state = "on" if result.get("enabled") else "off"
            return f"Metronome is {state}"
        else:
            return "Metronome state not available"
    except Exception as e:
        logger.error(f"Error getting metronome state: {str(e)}")
        return f"Error getting metronome state: {str(e)}"

@mcp.tool()
def set_metronome(ctx: Context, enabled: bool) -> str:
    """
    Turn the metronome on or off.

    Parameters:
    - enabled: True to enable, False to disable
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_metronome", {"enabled": enabled})
        state = "on" if result.get("enabled") else "off"
        return f"Metronome is now {state}"
    except Exception as e:
        logger.error(f"Error setting metronome: {str(e)}")
        return f"Error setting metronome: {str(e)}"

# ==================== AI MUSIC HELPERS ====================

@mcp.tool()
def get_scale_notes(ctx: Context, root: int, scale_type: str = "major") -> str:
    """
    Get the notes in a musical scale.

    Parameters:
    - root: MIDI note number for the root (0-127, where 60 = middle C)
    - scale_type: Type of scale (major, minor, dorian, phrygian, lydian, mixolydian, locrian, harmonic_minor, melodic_minor, pentatonic_major, pentatonic_minor, blues, chromatic)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_scale_notes", {
            "root": root,
            "scale_type": scale_type
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting scale notes: {str(e)}")
        return f"Error getting scale notes: {str(e)}"

@mcp.tool()
def quantize_clip_notes(ctx: Context, track_index: int, clip_index: int, grid: float = 0.25) -> str:
    """
    Quantize notes in a clip to a grid.

    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    - grid: Grid size in beats (0.25 = 16th notes, 0.5 = 8th notes, 1.0 = quarter notes)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("quantize_clip_notes", {
            "track_index": track_index,
            "clip_index": clip_index,
            "grid": grid
        })
        return f"Quantized {result.get('note_count')} notes to {grid} beat grid"
    except Exception as e:
        logger.error(f"Error quantizing clip notes: {str(e)}")
        return f"Error quantizing clip notes: {str(e)}"

@mcp.tool()
def humanize_clip_timing(ctx: Context, track_index: int, clip_index: int, amount: float = 0.05) -> str:
    """
    Add random timing variation to notes in a clip for a more human feel.

    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    - amount: Amount of timing variation in beats (0.05 = subtle, 0.1 = moderate, 0.2 = heavy)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("humanize_clip_timing", {
            "track_index": track_index,
            "clip_index": clip_index,
            "amount": amount
        })
        return f"Humanized timing of {result.get('note_count')} notes with amount {amount}"
    except Exception as e:
        logger.error(f"Error humanizing clip timing: {str(e)}")
        return f"Error humanizing clip timing: {str(e)}"

@mcp.tool()
def humanize_clip_velocity(ctx: Context, track_index: int, clip_index: int, amount: float = 0.1) -> str:
    """
    Add random velocity variation to notes in a clip for a more human feel.

    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    - amount: Amount of velocity variation (0.1 = +/-10%, 0.2 = +/-20%)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("humanize_clip_velocity", {
            "track_index": track_index,
            "clip_index": clip_index,
            "amount": amount
        })
        return f"Humanized velocity of {result.get('note_count')} notes with amount {amount}"
    except Exception as e:
        logger.error(f"Error humanizing clip velocity: {str(e)}")
        return f"Error humanizing clip velocity: {str(e)}"

@mcp.tool()
def generate_drum_pattern(ctx: Context, track_index: int, clip_index: int, style: str = "basic", length: float = 4.0) -> str:
    """
    Generate a drum pattern and add it to a clip.

    Parameters:
    - track_index: The index of the track (should be a drum track)
    - clip_index: The index of the clip slot
    - style: Pattern style (basic, house, hiphop, dnb, random)
    - length: Pattern length in beats
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("generate_drum_pattern", {
            "track_index": track_index,
            "clip_index": clip_index,
            "style": style,
            "length": length
        })
        return f"Generated {style} drum pattern with {result.get('note_count')} notes"
    except Exception as e:
        logger.error(f"Error generating drum pattern: {str(e)}")
        return f"Error generating drum pattern: {str(e)}"

@mcp.tool()
def generate_bassline(ctx: Context, track_index: int, clip_index: int, root: int = 36, scale_type: str = "minor", length: float = 4.0) -> str:
    """
    Generate a bassline pattern and add it to a clip.

    Parameters:
    - track_index: The index of the track (should be a bass track)
    - clip_index: The index of the clip slot
    - root: Root note MIDI number (36 = C1, common bass range)
    - scale_type: Scale to use (minor, major, dorian, pentatonic_minor, blues)
    - length: Pattern length in beats
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("generate_bassline", {
            "track_index": track_index,
            "clip_index": clip_index,
            "root": root,
            "scale_type": scale_type,
            "length": length
        })
        return f"Generated {scale_type} bassline with {result.get('note_count')} notes"
    except Exception as e:
        logger.error(f"Error generating bassline: {str(e)}")
        return f"Error generating bassline: {str(e)}"

@mcp.tool()
def get_browser_tree(ctx: Context, category_type: str = "all") -> str:
    """
    Get a hierarchical tree of browser categories from Ableton.
    
    Parameters:
    - category_type: Type of categories to get ('all', 'instruments', 'sounds', 'drums', 'audio_effects', 'midi_effects')
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_browser_tree", {
            "category_type": category_type
        })
        
        # Check if we got any categories
        if "available_categories" in result and len(result.get("categories", [])) == 0:
            available_cats = result.get("available_categories", [])
            return (f"No categories found for '{category_type}'. "
                   f"Available browser categories: {', '.join(available_cats)}")
        
        # Format the tree in a more readable way
        total_folders = result.get("total_folders", 0)
        formatted_output = f"Browser tree for '{category_type}' (showing {total_folders} folders):\n\n"
        
        def format_tree(item, indent=0):
            output = ""
            if item:
                prefix = "  " * indent
                name = item.get("name", "Unknown")
                path = item.get("path", "")
                has_more = item.get("has_more", False)
                
                # Add this item
                output += f"{prefix}• {name}"
                if path:
                    output += f" (path: {path})"
                if has_more:
                    output += " [...]"
                output += "\n"
                
                # Add children
                for child in item.get("children", []):
                    output += format_tree(child, indent + 1)
            return output
        
        # Format each category
        for category in result.get("categories", []):
            formatted_output += format_tree(category)
            formatted_output += "\n"
        
        return formatted_output
    except Exception as e:
        error_msg = str(e)
        if "Browser is not available" in error_msg:
            logger.error(f"Browser is not available in Ableton: {error_msg}")
            return f"Error: The Ableton browser is not available. Make sure Ableton Live is fully loaded and try again."
        elif "Could not access Live application" in error_msg:
            logger.error(f"Could not access Live application: {error_msg}")
            return f"Error: Could not access the Ableton Live application. Make sure Ableton Live is running and the Remote Script is loaded."
        else:
            logger.error(f"Error getting browser tree: {error_msg}")
            return f"Error getting browser tree: {error_msg}"

@mcp.tool()
def get_browser_items_at_path(ctx: Context, path: str) -> str:
    """
    Get browser items at a specific path in Ableton's browser.
    
    Parameters:
    - path: Path in the format "category/folder/subfolder"
            where category is one of the available browser categories in Ableton
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_browser_items_at_path", {
            "path": path
        })
        
        # Check if there was an error with available categories
        if "error" in result and "available_categories" in result:
            error = result.get("error", "")
            available_cats = result.get("available_categories", [])
            return (f"Error: {error}\n"
                   f"Available browser categories: {', '.join(available_cats)}")
        
        return json.dumps(result, indent=2)
    except Exception as e:
        error_msg = str(e)
        if "Browser is not available" in error_msg:
            logger.error(f"Browser is not available in Ableton: {error_msg}")
            return f"Error: The Ableton browser is not available. Make sure Ableton Live is fully loaded and try again."
        elif "Could not access Live application" in error_msg:
            logger.error(f"Could not access Live application: {error_msg}")
            return f"Error: Could not access the Ableton Live application. Make sure Ableton Live is running and the Remote Script is loaded."
        elif "Unknown or unavailable category" in error_msg:
            logger.error(f"Invalid browser category: {error_msg}")
            return f"Error: {error_msg}. Please check the available categories using get_browser_tree."
        elif "Path part" in error_msg and "not found" in error_msg:
            logger.error(f"Path not found: {error_msg}")
            return f"Error: {error_msg}. Please check the path and try again."
        else:
            logger.error(f"Error getting browser items at path: {error_msg}")
            return f"Error getting browser items at path: {error_msg}"

@mcp.tool()
def load_drum_kit(ctx: Context, track_index: int, rack_uri: str, kit_path: str) -> str:
    """
    Load a drum rack and then load a specific drum kit into it.
    
    Parameters:
    - track_index: The index of the track to load on
    - rack_uri: The URI of the drum rack to load (e.g., 'Drums/Drum Rack')
    - kit_path: Path to the drum kit inside the browser (e.g., 'drums/acoustic/kit1')
    """
    try:
        ableton = get_ableton_connection()
        
        # Step 1: Load the drum rack
        result = ableton.send_command("load_browser_item", {
            "track_index": track_index,
            "item_uri": rack_uri
        })
        
        if not result.get("loaded", False):
            return f"Failed to load drum rack with URI '{rack_uri}'"
        
        # Step 2: Get the drum kit items at the specified path
        kit_result = ableton.send_command("get_browser_items_at_path", {
            "path": kit_path
        })
        
        if "error" in kit_result:
            return f"Loaded drum rack but failed to find drum kit: {kit_result.get('error')}"
        
        # Step 3: Find a loadable drum kit
        kit_items = kit_result.get("items", [])
        loadable_kits = [item for item in kit_items if item.get("is_loadable", False)]
        
        if not loadable_kits:
            return f"Loaded drum rack but no loadable drum kits found at '{kit_path}'"
        
        # Step 4: Load the first loadable kit
        kit_uri = loadable_kits[0].get("uri")
        load_result = ableton.send_command("load_browser_item", {
            "track_index": track_index,
            "item_uri": kit_uri
        })
        
        return f"Loaded drum rack and kit '{loadable_kits[0].get('name')}' on track {track_index}"
    except Exception as e:
        logger.error(f"Error loading drum kit: {str(e)}")
        return f"Error loading drum kit: {str(e)}"

# ==================== MASTER TRACK CONTROL ====================

@mcp.tool()
def get_master_info(ctx: Context) -> str:
    """Get information about the master track including volume, pan, and devices."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_master_info")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting master info: {str(e)}")
        return f"Error getting master info: {str(e)}"

@mcp.tool()
def set_master_volume(ctx: Context, volume: float) -> str:
    """
    Set the master track volume.

    Parameters:
    - volume: Volume level from 0.0 (silent) to 1.0 (unity gain). 0.85 is Ableton's default.
    """
    try:
        if not 0 <= volume <= 1:
            return "Error: Volume must be between 0.0 and 1.0"
        ableton = get_ableton_connection()
        result = ableton.send_command("set_master_volume", {"volume": volume})
        return f"Master volume set to {result.get('volume', volume):.2f}"
    except Exception as e:
        logger.error(f"Error setting master volume: {str(e)}")
        return f"Error setting master volume: {str(e)}"

@mcp.tool()
def set_master_pan(ctx: Context, pan: float) -> str:
    """
    Set the master track panning.

    Parameters:
    - pan: Pan position from -1.0 (full left) to 1.0 (full right). 0.0 is center.
    """
    try:
        if not -1 <= pan <= 1:
            return "Error: Pan must be between -1.0 and 1.0"
        ableton = get_ableton_connection()
        result = ableton.send_command("set_master_pan", {"pan": pan})
        return f"Master pan set to {result.get('panning', pan):.2f}"
    except Exception as e:
        logger.error(f"Error setting master pan: {str(e)}")
        return f"Error setting master pan: {str(e)}"

# ==================== BROWSER SEARCH & NAVIGATION ====================

@mcp.tool()
def browse_path(ctx: Context, path: list) -> str:
    """
    Navigate browser by path list to get items at that location.

    Parameters:
    - path: List of path components, e.g. ["Audio Effects", "EQ Eight"] or ["Sounds", "Bass"]
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("browse_path", {"path": path})
        if "error" in result:
            return f"Error: {result.get('error')}. Available categories: {result.get('available_categories', [])}"
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error browsing path: {str(e)}")
        return f"Error browsing path: {str(e)}"

@mcp.tool()
def search_browser(ctx: Context, query: str, category: str = "all") -> str:
    """
    Search the browser for items matching a query.

    Parameters:
    - query: Search term to find in item names
    - category: Category to search in (all, instruments, sounds, drums, audio_effects, midi_effects)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("search_browser", {
            "query": query,
            "category": category
        })
        if "error" in result:
            return f"Error: {result.get('error')}"

        count = result.get('result_count', 0)
        if count == 0:
            return f"No results found for '{query}' in category '{category}'"

        return f"Found {count} results for '{query}':\n" + json.dumps(result.get('results', []), indent=2)
    except Exception as e:
        logger.error(f"Error searching browser: {str(e)}")
        return f"Error searching browser: {str(e)}"

@mcp.tool()
def load_item_to_track(ctx: Context, track_index: int, uri: str) -> str:
    """
    Load a browser item (instrument or effect) onto a track by URI.

    Parameters:
    - track_index: The index of the track to load the item onto
    - uri: The URI of the browser item (obtained from browse_path or search_browser)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("load_instrument_or_effect", {
            "track_index": track_index,
            "uri": uri
        })
        if "error" in result:
            return f"Error: {result.get('error')}"
        return f"Loaded '{result.get('item_name')}' on track '{result.get('track_name')}'"
    except Exception as e:
        logger.error(f"Error loading item to track: {str(e)}")
        return f"Error loading item to track: {str(e)}"

@mcp.tool()
def load_item_to_return(ctx: Context, return_index: int, uri: str) -> str:
    """
    Load a browser item (effect) onto a return track by URI.

    Parameters:
    - return_index: The index of the return track to load the item onto
    - uri: The URI of the browser item (obtained from browse_path or search_browser)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("load_browser_item_to_return", {
            "return_index": return_index,
            "item_uri": uri
        })
        if "error" in result:
            return f"Error: {result.get('error')}"
        return f"Loaded '{result.get('item_name')}' on return track '{result.get('return_track_name')}'"
    except Exception as e:
        logger.error(f"Error loading item to return track: {str(e)}")
        return f"Error loading item to return track: {str(e)}"

# Main execution
def main():
    """Run the MCP server"""
    mcp.run()

if __name__ == "__main__":
    main()