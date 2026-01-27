# test_workflows.py - Integration tests for complete workflows
"""
Integration tests that test complete workflows combining multiple operations.
These tests verify that operations work together correctly.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, call
import json
import sys
import os

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'MCP_Server'))


def create_test_client():
    """Create a fresh test client with mocked Ableton connection."""
    with patch.dict(os.environ, {
        "RATE_LIMIT_ENABLED": "false",
        "REST_API_KEY": ""
    }):
        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {}

        with patch('rest_api_server.AbletonConnection') as MockClass:
            MockClass.return_value = mock_conn

            import importlib
            import rest_api_server
            importlib.reload(rest_api_server)
            rest_api_server.ableton = mock_conn

            return TestClient(rest_api_server.app), mock_conn


# =============================================================================
# Basic Workflow Tests
# =============================================================================

class TestBasicWorkflow:
    """Test basic music production workflows."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_create_track_add_clip_add_notes(self):
        """Test creating a track, adding a clip, and adding notes."""
        # Step 1: Create MIDI track
        self.mock_ableton.send_command.return_value = {"name": "MIDI 1", "index": 0}
        response = self.client.post("/api/tracks/midi", json={"index": -1})
        assert response.status_code == 200

        # Step 2: Create clip
        self.mock_ableton.send_command.return_value = {"name": "Clip 1", "length": 4.0}
        response = self.client.post("/api/tracks/0/clips/0", json={
            "track_index": 0,
            "clip_index": 0,
            "length": 4.0,
            "name": "My Clip"
        })
        assert response.status_code == 200

        # Step 3: Add notes
        self.mock_ableton.send_command.return_value = {"notes_added": 3}
        response = self.client.post("/api/tracks/0/clips/0/notes", json={
            "track_index": 0,
            "clip_index": 0,
            "notes": [
                {"pitch": 60, "start_time": 0.0, "duration": 0.5, "velocity": 100},
                {"pitch": 64, "start_time": 0.5, "duration": 0.5, "velocity": 100},
                {"pitch": 67, "start_time": 1.0, "duration": 0.5, "velocity": 100}
            ]
        })
        assert response.status_code == 200

        # Step 4: Fire clip
        self.mock_ableton.send_command.return_value = {"fired": True}
        response = self.client.post("/api/tracks/0/clips/0/fire")
        assert response.status_code == 200

        # Verify all commands were called
        calls = self.mock_ableton.send_command.call_args_list
        assert len(calls) >= 4

    def test_create_drum_track_with_pattern(self):
        """Test creating a drum track with generated pattern."""
        # Create MIDI track for drums
        self.mock_ableton.send_command.return_value = {"name": "Drums", "index": 0}
        response = self.client.post("/api/tracks/midi", json={"index": -1, "name": "Drums"})
        assert response.status_code == 200

        # Generate drum pattern
        self.mock_ableton.send_command.return_value = {"pattern_created": True}
        response = self.client.post("/api/music/drums", json={
            "track_index": 0,
            "clip_index": 0,
            "style": "house",
            "length": 4.0
        })
        assert response.status_code == 200

    def test_create_bassline_track(self):
        """Test creating a bass track with generated bassline."""
        # Create MIDI track for bass
        self.mock_ableton.send_command.return_value = {"name": "Bass", "index": 1}
        response = self.client.post("/api/tracks/midi", json={"index": -1, "name": "Bass"})
        assert response.status_code == 200

        # Generate bassline
        self.mock_ableton.send_command.return_value = {"bassline_created": True}
        response = self.client.post("/api/music/bassline", json={
            "track_index": 1,
            "clip_index": 0,
            "root": 36,
            "scale_type": "minor",
            "length": 4.0
        })
        assert response.status_code == 200


# =============================================================================
# Transport Control Workflow Tests
# =============================================================================

class TestTransportWorkflow:
    """Test transport control workflows."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_play_stop_workflow(self):
        """Test play/stop transport workflow."""
        # Set tempo
        self.mock_ableton.send_command.return_value = {"tempo": 128.0}
        response = self.client.post("/api/tempo", json={"tempo": 128.0})
        assert response.status_code == 200

        # Start playback
        self.mock_ableton.send_command.return_value = {"is_playing": True}
        response = self.client.post("/api/transport/play")
        assert response.status_code == 200

        # Get position
        self.mock_ableton.send_command.return_value = {"current_time": 4.5}
        response = self.client.get("/api/transport/position")
        assert response.status_code == 200

        # Stop playback
        self.mock_ableton.send_command.return_value = {"is_playing": False}
        response = self.client.post("/api/transport/stop")
        assert response.status_code == 200

    def test_recording_workflow(self):
        """Test recording workflow."""
        # Arm track
        self.mock_ableton.send_command.return_value = {"arm": True}
        response = self.client.put("/api/tracks/0/arm", json={"track_index": 0, "value": True})
        assert response.status_code == 200

        # Enable metronome
        self.mock_ableton.send_command.return_value = {"enabled": True}
        response = self.client.post("/api/metronome", json={"enabled": True})
        assert response.status_code == 200

        # Start recording
        self.mock_ableton.send_command.return_value = {"recording": True}
        response = self.client.post("/api/recording/start")
        assert response.status_code == 200

        # Stop recording
        self.mock_ableton.send_command.return_value = {"recording": False}
        response = self.client.post("/api/recording/stop")
        assert response.status_code == 200


# =============================================================================
# Mixing Workflow Tests
# =============================================================================

class TestMixingWorkflow:
    """Test mixing workflow scenarios."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_basic_mix_setup(self):
        """Test basic mix setup workflow."""
        # Set track volumes
        for i in range(4):
            self.mock_ableton.send_command.return_value = {"volume": 0.75}
            response = self.client.put(f"/api/tracks/{i}/volume", json={"volume": 0.75})
            assert response.status_code == 200

        # Pan tracks
        pans = [-0.5, -0.25, 0.25, 0.5]
        for i, pan in enumerate(pans):
            self.mock_ableton.send_command.return_value = {"pan": pan}
            response = self.client.put(f"/api/tracks/{i}/pan", json={"pan": pan})
            assert response.status_code == 200

        # Solo a track
        self.mock_ableton.send_command.return_value = {"solo": True}
        response = self.client.put("/api/tracks/0/solo", json={"track_index": 0, "value": True})
        assert response.status_code == 200

        # Mute a track
        self.mock_ableton.send_command.return_value = {"mute": True}
        response = self.client.put("/api/tracks/1/mute", json={"track_index": 1, "value": True})
        assert response.status_code == 200

    def test_send_effects_workflow(self):
        """Test setting up send effects."""
        # Get return tracks
        self.mock_ableton.send_command.return_value = {
            "return_tracks": [
                {"index": 0, "name": "Return A"},
                {"index": 1, "name": "Return B"}
            ]
        }
        response = self.client.get("/api/returns")
        assert response.status_code == 200

        # Set send levels
        self.mock_ableton.send_command.return_value = {"level": 0.5}
        response = self.client.post("/api/tracks/0/sends/0", json={
            "track_index": 0,
            "send_index": 0,
            "level": 0.5
        })
        assert response.status_code == 200

        # Set return volume
        self.mock_ableton.send_command.return_value = {"volume": 0.8}
        response = self.client.put("/api/returns/0/volume", json={
            "return_index": 0,
            "volume": 0.8
        })
        assert response.status_code == 200


# =============================================================================
# Scene Workflow Tests
# =============================================================================

class TestSceneWorkflow:
    """Test scene-based workflow scenarios."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_scene_arrangement_workflow(self):
        """Test creating and arranging scenes."""
        # Create scenes
        scene_names = ["Intro", "Verse", "Chorus", "Bridge", "Outro"]
        for i, name in enumerate(scene_names):
            self.mock_ableton.send_command.return_value = {"index": i, "name": name}
            response = self.client.post("/api/scenes", json={"index": -1, "name": name})
            assert response.status_code == 200

        # Fire first scene
        self.mock_ableton.send_command.return_value = {"fired": True}
        response = self.client.post("/api/scenes/0/fire")
        assert response.status_code == 200

        # Get all scenes
        self.mock_ableton.send_command.return_value = {
            "scenes": [{"index": i, "name": name} for i, name in enumerate(scene_names)]
        }
        response = self.client.get("/api/scenes")
        assert response.status_code == 200

    def test_duplicate_scene_workflow(self):
        """Test duplicating and modifying scenes."""
        # Duplicate scene
        self.mock_ableton.send_command.return_value = {"index": 1, "name": "Scene 1 Copy"}
        response = self.client.post("/api/scenes/0/duplicate")
        assert response.status_code == 200

        # Rename duplicated scene
        self.mock_ableton.send_command.return_value = {"name": "Chorus 2"}
        response = self.client.put("/api/scenes/1/name", json={
            "scene_index": 1,
            "name": "Chorus 2"
        })
        assert response.status_code == 200


# =============================================================================
# Clip Editing Workflow Tests
# =============================================================================

class TestClipEditingWorkflow:
    """Test clip editing workflows."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_quantize_and_humanize_workflow(self):
        """Test quantizing then humanizing notes."""
        # Get existing notes
        self.mock_ableton.send_command.return_value = {
            "notes": [
                {"pitch": 60, "start_time": 0.1, "duration": 0.5, "velocity": 100}
            ]
        }
        response = self.client.get("/api/tracks/0/clips/0/notes")
        assert response.status_code == 200

        # Quantize notes
        self.mock_ableton.send_command.return_value = {"quantized": True}
        response = self.client.post("/api/tracks/0/clips/0/quantize", json={
            "grid": 0.25,
            "strength": 1.0
        })
        assert response.status_code == 200

        # Humanize timing
        self.mock_ableton.send_command.return_value = {"humanized": True}
        response = self.client.post("/api/tracks/0/clips/0/humanize/timing", json={
            "amount": 0.05
        })
        assert response.status_code == 200

        # Humanize velocity
        self.mock_ableton.send_command.return_value = {"humanized": True}
        response = self.client.post("/api/tracks/0/clips/0/humanize/velocity", json={
            "amount": 0.1
        })
        assert response.status_code == 200

    def test_transpose_workflow(self):
        """Test transposing clip notes."""
        # Add notes
        self.mock_ableton.send_command.return_value = {"notes_added": 4}
        response = self.client.post("/api/tracks/0/clips/0/notes", json={
            "track_index": 0,
            "clip_index": 0,
            "notes": [
                {"pitch": 60, "start_time": 0.0, "duration": 0.5, "velocity": 100},
                {"pitch": 62, "start_time": 0.5, "duration": 0.5, "velocity": 100},
                {"pitch": 64, "start_time": 1.0, "duration": 0.5, "velocity": 100},
                {"pitch": 65, "start_time": 1.5, "duration": 0.5, "velocity": 100}
            ]
        })
        assert response.status_code == 200

        # Transpose up an octave
        self.mock_ableton.send_command.return_value = {"transposed": True}
        response = self.client.post("/api/tracks/0/clips/0/transpose", json={
            "track_index": 0,
            "clip_index": 0,
            "semitones": 12
        })
        assert response.status_code == 200

    def test_loop_editing_workflow(self):
        """Test editing clip loop settings."""
        # Get current loop
        self.mock_ableton.send_command.return_value = {
            "looping": True,
            "loop_start": 0.0,
            "loop_end": 4.0
        }
        response = self.client.get("/api/tracks/0/clips/0/loop")
        assert response.status_code == 200

        # Modify loop
        self.mock_ableton.send_command.return_value = {
            "looping": True,
            "loop_start": 0.0,
            "loop_end": 8.0
        }
        response = self.client.put("/api/tracks/0/clips/0/loop", json={
            "track_index": 0,
            "clip_index": 0,
            "loop_start": 0.0,
            "loop_end": 8.0,
            "looping": True
        })
        assert response.status_code == 200


# =============================================================================
# Device Manipulation Workflow Tests
# =============================================================================

class TestDeviceWorkflow:
    """Test device manipulation workflows."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_device_parameter_automation(self):
        """Test automating device parameters."""
        # Get device parameters
        self.mock_ableton.send_command.return_value = {
            "name": "Auto Filter",
            "parameters": [
                {"name": "Device On", "value": 1.0, "min": 0.0, "max": 1.0},
                {"name": "Frequency", "value": 1000.0, "min": 20.0, "max": 20000.0}
            ]
        }
        response = self.client.get("/api/tracks/0/devices/0")
        assert response.status_code == 200

        # Modify parameter - DeviceParamRequest requires all fields
        # value must be normalized (0-1)
        self.mock_ableton.send_command.return_value = {"value": 0.5}
        response = self.client.put("/api/tracks/0/devices/0/parameter", json={
            "track_index": 0,
            "device_index": 0,
            "parameter_index": 1,
            "value": 0.5
        })
        assert response.status_code == 200

    def test_device_bypass_workflow(self):
        """Test bypassing devices."""
        # Toggle device off - DeviceToggleRequest requires track/device index
        self.mock_ableton.send_command.return_value = {"enabled": False}
        response = self.client.put("/api/tracks/0/devices/0/toggle", json={
            "track_index": 0,
            "device_index": 0,
            "enabled": False
        })
        assert response.status_code == 200

        # Toggle device back on
        self.mock_ableton.send_command.return_value = {"enabled": True}
        response = self.client.put("/api/tracks/0/devices/0/toggle", json={
            "track_index": 0,
            "device_index": 0,
            "enabled": True
        })
        assert response.status_code == 200


# =============================================================================
# Browser Workflow Tests
# =============================================================================

class TestBrowserWorkflow:
    """Test browser and loading workflows."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_search_and_load_instrument(self):
        """Test searching for and loading an instrument."""
        # Search for instrument
        self.mock_ableton.send_command.return_value = {
            "results": [
                {"name": "Analog", "uri": "browser://instrument/analog"},
                {"name": "Wavetable", "uri": "browser://instrument/wavetable"}
            ]
        }
        response = self.client.post("/api/browser/search", json={
            "query": "synth",
            "category": "instruments"
        })
        assert response.status_code == 200

        # Load instrument to track
        self.mock_ableton.send_command.return_value = {"loaded": True}
        response = self.client.post("/api/browser/load", json={
            "track_index": 0,
            "uri": "browser://instrument/analog"
        })
        assert response.status_code == 200

    def test_load_effect_to_return(self):
        """Test loading effect to return track."""
        # Search for effect
        self.mock_ableton.send_command.return_value = {
            "results": [
                {"name": "Reverb", "uri": "browser://effect/reverb"}
            ]
        }
        response = self.client.post("/api/browser/search", json={
            "query": "reverb",
            "category": "audio_effects"
        })
        assert response.status_code == 200

        # Load to return track
        self.mock_ableton.send_command.return_value = {"loaded": True}
        response = self.client.post("/api/browser/load-to-return", json={
            "return_index": 0,
            "uri": "browser://effect/reverb"
        })
        assert response.status_code == 200


# =============================================================================
# Undo/Redo Workflow Tests
# =============================================================================

class TestUndoRedoWorkflow:
    """Test undo/redo workflows."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_undo_after_change(self):
        """Test undoing after making a change."""
        # Make a change (set tempo)
        self.mock_ableton.send_command.return_value = {"tempo": 140.0}
        response = self.client.post("/api/tempo", json={"tempo": 140.0})
        assert response.status_code == 200

        # Undo the change
        self.mock_ableton.send_command.return_value = {"undone": True}
        response = self.client.post("/api/undo")
        assert response.status_code == 200

        # Redo the change
        self.mock_ableton.send_command.return_value = {"redone": True}
        response = self.client.post("/api/redo")
        assert response.status_code == 200


# =============================================================================
# Complete Song Creation Workflow
# =============================================================================

class TestCompleteSongWorkflow:
    """Test complete song creation workflow."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_create_simple_song(self):
        """Test creating a simple song with drums, bass, and lead."""
        # Set tempo
        self.mock_ableton.send_command.return_value = {"tempo": 120.0}
        response = self.client.post("/api/tempo", json={"tempo": 120.0})
        assert response.status_code == 200

        # Create drum track
        self.mock_ableton.send_command.return_value = {"name": "Drums", "index": 0}
        response = self.client.post("/api/tracks/midi", json={"index": -1, "name": "Drums"})
        assert response.status_code == 200

        # Create bass track
        self.mock_ableton.send_command.return_value = {"name": "Bass", "index": 1}
        response = self.client.post("/api/tracks/midi", json={"index": -1, "name": "Bass"})
        assert response.status_code == 200

        # Create lead track
        self.mock_ableton.send_command.return_value = {"name": "Lead", "index": 2}
        response = self.client.post("/api/tracks/midi", json={"index": -1, "name": "Lead"})
        assert response.status_code == 200

        # Generate drum pattern
        self.mock_ableton.send_command.return_value = {"pattern_created": True}
        response = self.client.post("/api/music/drums", json={
            "track_index": 0,
            "clip_index": 0,
            "style": "house",
            "length": 4.0
        })
        assert response.status_code == 200

        # Generate bassline
        self.mock_ableton.send_command.return_value = {"bassline_created": True}
        response = self.client.post("/api/music/bassline", json={
            "track_index": 1,
            "clip_index": 0,
            "root": 36,
            "scale_type": "minor",
            "length": 4.0
        })
        assert response.status_code == 200

        # Create lead clip with notes
        self.mock_ableton.send_command.return_value = {"created": True}
        response = self.client.post("/api/tracks/2/clips/0", json={
            "track_index": 2,
            "clip_index": 0,
            "length": 4.0,
            "name": "Lead"
        })
        assert response.status_code == 200

        # Add lead notes
        self.mock_ableton.send_command.return_value = {"notes_added": 4}
        response = self.client.post("/api/tracks/2/clips/0/notes", json={
            "track_index": 2,
            "clip_index": 0,
            "notes": [
                {"pitch": 72, "start_time": 0.0, "duration": 1.0, "velocity": 100},
                {"pitch": 74, "start_time": 1.0, "duration": 0.5, "velocity": 90},
                {"pitch": 76, "start_time": 1.5, "duration": 0.5, "velocity": 95},
                {"pitch": 79, "start_time": 2.0, "duration": 2.0, "velocity": 100}
            ]
        })
        assert response.status_code == 200

        # Create scene and name it
        self.mock_ableton.send_command.return_value = {"index": 0, "name": "Main Loop"}
        response = self.client.put("/api/scenes/0/name", json={
            "scene_index": 0,
            "name": "Main Loop"
        })
        assert response.status_code == 200

        # Fire scene to play all clips
        self.mock_ableton.send_command.return_value = {"fired": True}
        response = self.client.post("/api/scenes/0/fire")
        assert response.status_code == 200
