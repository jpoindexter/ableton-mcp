# test_rest_api_complete.py - Comprehensive REST API endpoint tests
"""
Comprehensive tests for ALL REST API endpoints in AbletonMCP.
Tests cover valid inputs, invalid inputs, and error conditions.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'MCP_Server'))


# =============================================================================
# Test Setup Helper
# =============================================================================

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
# Transport Endpoints
# =============================================================================

class TestTransportEndpoints:
    """Test all transport-related endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_get_session_info(self, sample_session_info):
        """Test GET /api/session returns session info."""
        self.mock_ableton.send_command.return_value = sample_session_info
        response = self.client.get("/api/session")
        assert response.status_code == 200
        assert response.json()["tempo"] == 120.0
        self.mock_ableton.send_command.assert_called_with("get_session_info")

    def test_set_tempo_valid(self):
        """Test valid tempo setting."""
        self.mock_ableton.send_command.return_value = {"tempo": 140.0}
        response = self.client.post("/api/tempo", json={"tempo": 140.0})
        assert response.status_code == 200
        self.mock_ableton.send_command.assert_called_with("set_tempo", {"tempo": 140.0})

    def test_set_tempo_valid_minimum(self):
        """Test minimum valid tempo (20 BPM)."""
        response = self.client.post("/api/tempo", json={"tempo": 20.0})
        assert response.status_code == 200

    def test_set_tempo_valid_maximum(self):
        """Test maximum valid tempo (300 BPM)."""
        response = self.client.post("/api/tempo", json={"tempo": 300.0})
        assert response.status_code == 200

    def test_set_tempo_invalid_too_low(self):
        """Test tempo below minimum returns 422."""
        response = self.client.post("/api/tempo", json={"tempo": 19.9})
        assert response.status_code == 422

    def test_set_tempo_invalid_too_high(self):
        """Test tempo above maximum returns 422."""
        response = self.client.post("/api/tempo", json={"tempo": 300.1})
        assert response.status_code == 422

    def test_set_tempo_invalid_negative(self):
        """Test negative tempo returns 422."""
        response = self.client.post("/api/tempo", json={"tempo": -100})
        assert response.status_code == 422

    def test_set_tempo_invalid_zero(self):
        """Test zero tempo returns 422."""
        response = self.client.post("/api/tempo", json={"tempo": 0})
        assert response.status_code == 422

    def test_set_tempo_missing_field(self):
        """Test missing tempo field returns 422."""
        response = self.client.post("/api/tempo", json={})
        assert response.status_code == 422

    def test_start_playback(self):
        """Test POST /api/transport/play."""
        response = self.client.post("/api/transport/play")
        assert response.status_code == 200
        self.mock_ableton.send_command.assert_called_with("start_playback")

    def test_stop_playback(self):
        """Test POST /api/transport/stop."""
        response = self.client.post("/api/transport/stop")
        assert response.status_code == 200
        self.mock_ableton.send_command.assert_called_with("stop_playback")

    def test_undo(self):
        """Test POST /api/undo."""
        response = self.client.post("/api/undo")
        assert response.status_code == 200
        self.mock_ableton.send_command.assert_called_with("undo")

    def test_redo(self):
        """Test POST /api/redo."""
        response = self.client.post("/api/redo")
        assert response.status_code == 200
        self.mock_ableton.send_command.assert_called_with("redo")

    def test_get_metronome(self):
        """Test GET /api/metronome."""
        self.mock_ableton.send_command.return_value = {"enabled": True}
        response = self.client.get("/api/metronome")
        assert response.status_code == 200
        self.mock_ableton.send_command.assert_called_with("get_metronome_state")

    def test_set_metronome_on(self):
        """Test enabling metronome."""
        response = self.client.post("/api/metronome", json={"enabled": True})
        assert response.status_code == 200
        self.mock_ableton.send_command.assert_called_with("set_metronome", {"enabled": True})

    def test_set_metronome_off(self):
        """Test disabling metronome."""
        response = self.client.post("/api/metronome", json={"enabled": False})
        assert response.status_code == 200
        self.mock_ableton.send_command.assert_called_with("set_metronome", {"enabled": False})

    def test_get_playback_position(self):
        """Test GET /api/transport/position."""
        self.mock_ableton.send_command.return_value = {"current_time": 4.5, "is_playing": True}
        response = self.client.get("/api/transport/position")
        assert response.status_code == 200
        self.mock_ableton.send_command.assert_called_with("get_playback_position")


# =============================================================================
# Track Endpoints
# =============================================================================

class TestTrackEndpoints:
    """Test all track-related endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_get_track_info(self, sample_track_info):
        """Test GET /api/tracks/{track_index}."""
        self.mock_ableton.send_command.return_value = sample_track_info
        response = self.client.get("/api/tracks/0")
        assert response.status_code == 200
        assert response.json()["name"] == "Test Track"

    def test_get_track_info_various_indices(self, sample_track_info):
        """Test track info for various valid indices."""
        self.mock_ableton.send_command.return_value = sample_track_info
        for idx in [0, 1, 10, 100, 999]:
            response = self.client.get(f"/api/tracks/{idx}")
            assert response.status_code == 200

    def test_get_track_info_invalid_negative(self):
        """Test negative track index returns 422."""
        response = self.client.get("/api/tracks/-1")
        assert response.status_code == 422

    def test_get_track_info_invalid_too_high(self):
        """Test track index over max returns 422."""
        response = self.client.get("/api/tracks/1000")
        assert response.status_code == 422

    def test_create_midi_track(self):
        """Test POST /api/tracks/midi."""
        self.mock_ableton.send_command.return_value = {"name": "MIDI 1", "index": 0}
        response = self.client.post("/api/tracks/midi", json={"index": -1})
        assert response.status_code == 200

    def test_create_midi_track_at_specific_index(self):
        """Test creating MIDI track at specific index."""
        response = self.client.post("/api/tracks/midi", json={"index": 5})
        assert response.status_code == 200

    def test_create_midi_track_with_name(self):
        """Test creating MIDI track with name."""
        response = self.client.post("/api/tracks/midi", json={"index": -1, "name": "My MIDI"})
        assert response.status_code == 200

    def test_create_audio_track(self):
        """Test POST /api/tracks/audio."""
        response = self.client.post("/api/tracks/audio", json={"index": -1})
        assert response.status_code == 200

    def test_create_audio_track_with_name(self):
        """Test creating audio track with name."""
        response = self.client.post("/api/tracks/audio", json={"index": -1, "name": "Audio In"})
        assert response.status_code == 200

    def test_delete_track(self):
        """Test DELETE /api/tracks/{track_index}."""
        response = self.client.delete("/api/tracks/0")
        assert response.status_code == 200
        self.mock_ableton.send_command.assert_called_with("delete_track", {"track_index": 0})

    def test_delete_track_invalid_index(self):
        """Test delete with invalid index."""
        response = self.client.delete("/api/tracks/-1")
        assert response.status_code == 422

    def test_duplicate_track(self):
        """Test POST /api/tracks/{track_index}/duplicate."""
        response = self.client.post("/api/tracks/0/duplicate")
        assert response.status_code == 200
        self.mock_ableton.send_command.assert_called_with("duplicate_track", {"track_index": 0})

    def test_freeze_track(self):
        """Test POST /api/tracks/{track_index}/freeze."""
        response = self.client.post("/api/tracks/0/freeze")
        assert response.status_code == 200
        self.mock_ableton.send_command.assert_called_with("freeze_track", {"track_index": 0})

    def test_flatten_track(self):
        """Test POST /api/tracks/{track_index}/flatten."""
        response = self.client.post("/api/tracks/0/flatten")
        assert response.status_code == 200
        self.mock_ableton.send_command.assert_called_with("flatten_track", {"track_index": 0})

    def test_set_track_name(self):
        """Test PUT /api/tracks/{track_index}/name."""
        response = self.client.put("/api/tracks/0/name", json={"track_index": 0, "name": "New Name"})
        assert response.status_code == 200

    def test_get_track_color(self):
        """Test GET /api/tracks/{track_index}/color."""
        self.mock_ableton.send_command.return_value = {"color": 16725558}
        response = self.client.get("/api/tracks/0/color")
        assert response.status_code == 200

    def test_set_track_color(self):
        """Test PUT /api/tracks/{track_index}/color."""
        # TrackColorRequest requires track_index and color (0-69)
        response = self.client.put("/api/tracks/0/color", json={"track_index": 0, "color": 10})
        assert response.status_code == 200

    def test_set_track_mute_on(self):
        """Test muting a track."""
        response = self.client.put("/api/tracks/0/mute", json={"track_index": 0, "value": True})
        assert response.status_code == 200

    def test_set_track_mute_off(self):
        """Test unmuting a track."""
        response = self.client.put("/api/tracks/0/mute", json={"track_index": 0, "value": False})
        assert response.status_code == 200

    def test_set_track_solo_on(self):
        """Test soloing a track."""
        response = self.client.put("/api/tracks/0/solo", json={"track_index": 0, "value": True})
        assert response.status_code == 200

    def test_set_track_solo_off(self):
        """Test unsoloing a track."""
        response = self.client.put("/api/tracks/0/solo", json={"track_index": 0, "value": False})
        assert response.status_code == 200

    def test_set_track_arm_on(self):
        """Test arming a track."""
        response = self.client.put("/api/tracks/0/arm", json={"track_index": 0, "value": True})
        assert response.status_code == 200

    def test_set_track_arm_off(self):
        """Test disarming a track."""
        response = self.client.put("/api/tracks/0/arm", json={"track_index": 0, "value": False})
        assert response.status_code == 200

    def test_set_track_volume_valid(self):
        """Test setting valid track volume."""
        response = self.client.put("/api/tracks/0/volume", json={"volume": 0.5})
        assert response.status_code == 200

    def test_set_track_volume_min(self):
        """Test setting minimum track volume."""
        response = self.client.put("/api/tracks/0/volume", json={"volume": 0.0})
        assert response.status_code == 200

    def test_set_track_volume_max(self):
        """Test setting maximum track volume."""
        response = self.client.put("/api/tracks/0/volume", json={"volume": 1.0})
        assert response.status_code == 200

    def test_set_track_volume_invalid_negative(self):
        """Test negative volume returns 422."""
        response = self.client.put("/api/tracks/0/volume", json={"volume": -0.1})
        assert response.status_code == 422

    def test_set_track_volume_invalid_over_max(self):
        """Test volume over 1.0 returns 422."""
        response = self.client.put("/api/tracks/0/volume", json={"volume": 1.1})
        assert response.status_code == 422

    def test_set_track_pan_valid_left(self):
        """Test setting pan to full left."""
        response = self.client.put("/api/tracks/0/pan", json={"pan": -1.0})
        assert response.status_code == 200

    def test_set_track_pan_valid_right(self):
        """Test setting pan to full right."""
        response = self.client.put("/api/tracks/0/pan", json={"pan": 1.0})
        assert response.status_code == 200

    def test_set_track_pan_valid_center(self):
        """Test setting pan to center."""
        response = self.client.put("/api/tracks/0/pan", json={"pan": 0.0})
        assert response.status_code == 200

    def test_set_track_pan_invalid_too_left(self):
        """Test pan below -1.0 returns 422."""
        response = self.client.put("/api/tracks/0/pan", json={"pan": -1.1})
        assert response.status_code == 422

    def test_set_track_pan_invalid_too_right(self):
        """Test pan above 1.0 returns 422."""
        response = self.client.put("/api/tracks/0/pan", json={"pan": 1.1})
        assert response.status_code == 422

    def test_select_track(self):
        """Test POST /api/tracks/{track_index}/select."""
        response = self.client.post("/api/tracks/0/select")
        assert response.status_code == 200
        self.mock_ableton.send_command.assert_called_with("select_track", {"track_index": 0})


# =============================================================================
# Clip Endpoints
# =============================================================================

class TestClipEndpoints:
    """Test all clip-related endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_get_clip_info(self, sample_clip_info):
        """Test GET /api/tracks/{track_index}/clips/{clip_index}."""
        self.mock_ableton.send_command.return_value = sample_clip_info
        response = self.client.get("/api/tracks/0/clips/0")
        assert response.status_code == 200
        assert response.json()["name"] == "Test Clip"

    def test_get_clip_info_invalid_track_index(self):
        """Test invalid track index returns 422."""
        response = self.client.get("/api/tracks/-1/clips/0")
        assert response.status_code == 422

    def test_get_clip_info_invalid_clip_index(self):
        """Test invalid clip index returns 422."""
        response = self.client.get("/api/tracks/0/clips/-1")
        assert response.status_code == 422

    def test_create_clip(self):
        """Test POST /api/tracks/{track_index}/clips/{clip_index}."""
        response = self.client.post("/api/tracks/0/clips/0", json={
            "track_index": 0,
            "clip_index": 0,
            "length": 4.0
        })
        assert response.status_code == 200

    def test_create_clip_with_name(self):
        """Test creating clip with custom name."""
        response = self.client.post("/api/tracks/0/clips/0", json={
            "track_index": 0,
            "clip_index": 0,
            "length": 8.0,
            "name": "My Clip"
        })
        assert response.status_code == 200

    def test_create_clip_default_length(self):
        """Test creating clip with default length."""
        response = self.client.post("/api/tracks/0/clips/0", json={
            "track_index": 0,
            "clip_index": 0
        })
        assert response.status_code == 200

    def test_delete_clip(self):
        """Test DELETE /api/tracks/{track_index}/clips/{clip_index}."""
        response = self.client.delete("/api/tracks/0/clips/0")
        assert response.status_code == 200
        self.mock_ableton.send_command.assert_called_with("delete_clip", {
            "track_index": 0, "clip_index": 0
        })

    def test_fire_clip(self):
        """Test POST /api/tracks/{track_index}/clips/{clip_index}/fire."""
        response = self.client.post("/api/tracks/0/clips/0/fire")
        assert response.status_code == 200
        self.mock_ableton.send_command.assert_called_with("fire_clip", {
            "track_index": 0, "clip_index": 0
        })

    def test_stop_clip(self):
        """Test POST /api/tracks/{track_index}/clips/{clip_index}/stop."""
        response = self.client.post("/api/tracks/0/clips/0/stop")
        assert response.status_code == 200
        self.mock_ableton.send_command.assert_called_with("stop_clip", {
            "track_index": 0, "clip_index": 0
        })

    def test_duplicate_clip(self):
        """Test POST /api/tracks/{track_index}/clips/{clip_index}/duplicate."""
        response = self.client.post("/api/tracks/0/clips/0/duplicate", json={
            "track_index": 0,
            "clip_index": 0,
            "target_index": 1
        })
        assert response.status_code == 200

    def test_set_clip_name(self):
        """Test PUT /api/tracks/{track_index}/clips/{clip_index}/name."""
        response = self.client.put("/api/tracks/0/clips/0/name", json={
            "track_index": 0,
            "clip_index": 0,
            "name": "New Clip Name"
        })
        assert response.status_code == 200

    def test_get_clip_color(self):
        """Test GET /api/tracks/{track_index}/clips/{clip_index}/color."""
        self.mock_ableton.send_command.return_value = {"color": 16725558}
        response = self.client.get("/api/tracks/0/clips/0/color")
        assert response.status_code == 200

    def test_set_clip_color(self):
        """Test PUT /api/tracks/{track_index}/clips/{clip_index}/color."""
        # ClipColorRequest requires track_index, clip_index, and color (0-69)
        response = self.client.put("/api/tracks/0/clips/0/color", json={
            "track_index": 0,
            "clip_index": 0,
            "color": 10
        })
        assert response.status_code == 200

    def test_get_clip_loop(self):
        """Test GET /api/tracks/{track_index}/clips/{clip_index}/loop."""
        self.mock_ableton.send_command.return_value = {
            "looping": True, "loop_start": 0.0, "loop_end": 4.0
        }
        response = self.client.get("/api/tracks/0/clips/0/loop")
        assert response.status_code == 200

    def test_set_clip_loop(self):
        """Test PUT /api/tracks/{track_index}/clips/{clip_index}/loop."""
        response = self.client.put("/api/tracks/0/clips/0/loop", json={
            "track_index": 0,
            "clip_index": 0,
            "loop_start": 0.0,
            "loop_end": 8.0,
            "looping": True
        })
        assert response.status_code == 200

    def test_select_clip(self):
        """Test POST /api/tracks/{track_index}/clips/{clip_index}/select."""
        response = self.client.post("/api/tracks/0/clips/0/select")
        assert response.status_code == 200


# =============================================================================
# Note Endpoints
# =============================================================================

class TestNoteEndpoints:
    """Test all note-related endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_get_clip_notes(self, sample_notes):
        """Test GET /api/tracks/{track_index}/clips/{clip_index}/notes."""
        self.mock_ableton.send_command.return_value = {"notes": sample_notes}
        response = self.client.get("/api/tracks/0/clips/0/notes")
        assert response.status_code == 200

    def test_add_notes_valid(self, valid_note):
        """Test adding valid notes."""
        response = self.client.post("/api/tracks/0/clips/0/notes", json={
            "track_index": 0,
            "clip_index": 0,
            "notes": [valid_note]
        })
        assert response.status_code == 200

    def test_add_notes_multiple(self, sample_notes):
        """Test adding multiple notes."""
        response = self.client.post("/api/tracks/0/clips/0/notes", json={
            "track_index": 0,
            "clip_index": 0,
            "notes": sample_notes
        })
        assert response.status_code == 200

    def test_add_notes_invalid_pitch_too_high(self):
        """Test note with pitch > 127 returns 422."""
        response = self.client.post("/api/tracks/0/clips/0/notes", json={
            "track_index": 0,
            "clip_index": 0,
            "notes": [{"pitch": 128, "start_time": 0.0, "duration": 0.5, "velocity": 100}]
        })
        assert response.status_code == 422

    def test_add_notes_invalid_pitch_negative(self):
        """Test note with negative pitch returns 422."""
        response = self.client.post("/api/tracks/0/clips/0/notes", json={
            "track_index": 0,
            "clip_index": 0,
            "notes": [{"pitch": -1, "start_time": 0.0, "duration": 0.5, "velocity": 100}]
        })
        assert response.status_code == 422

    def test_add_notes_invalid_velocity_too_high(self):
        """Test note with velocity > 127 returns 422."""
        response = self.client.post("/api/tracks/0/clips/0/notes", json={
            "track_index": 0,
            "clip_index": 0,
            "notes": [{"pitch": 60, "start_time": 0.0, "duration": 0.5, "velocity": 128}]
        })
        assert response.status_code == 422

    def test_add_notes_invalid_duration_zero(self):
        """Test note with zero duration returns 422."""
        response = self.client.post("/api/tracks/0/clips/0/notes", json={
            "track_index": 0,
            "clip_index": 0,
            "notes": [{"pitch": 60, "start_time": 0.0, "duration": 0.0, "velocity": 100}]
        })
        assert response.status_code == 422

    def test_add_notes_invalid_duration_negative(self):
        """Test note with negative duration returns 422."""
        response = self.client.post("/api/tracks/0/clips/0/notes", json={
            "track_index": 0,
            "clip_index": 0,
            "notes": [{"pitch": 60, "start_time": 0.0, "duration": -0.5, "velocity": 100}]
        })
        assert response.status_code == 422

    def test_add_notes_invalid_start_time_negative(self):
        """Test note with negative start_time returns 422."""
        response = self.client.post("/api/tracks/0/clips/0/notes", json={
            "track_index": 0,
            "clip_index": 0,
            "notes": [{"pitch": 60, "start_time": -1.0, "duration": 0.5, "velocity": 100}]
        })
        assert response.status_code == 422

    def test_add_notes_default_velocity(self):
        """Test note without velocity uses default."""
        response = self.client.post("/api/tracks/0/clips/0/notes", json={
            "track_index": 0,
            "clip_index": 0,
            "notes": [{"pitch": 60, "start_time": 0.0, "duration": 0.5}]
        })
        assert response.status_code == 200

    def test_remove_all_notes(self):
        """Test DELETE /api/tracks/{track_index}/clips/{clip_index}/notes."""
        response = self.client.delete("/api/tracks/0/clips/0/notes")
        assert response.status_code == 200
        self.mock_ableton.send_command.assert_called_with("remove_all_notes", {
            "track_index": 0, "clip_index": 0
        })

    def test_transpose_notes(self):
        """Test POST /api/tracks/{track_index}/clips/{clip_index}/transpose."""
        response = self.client.post("/api/tracks/0/clips/0/transpose", json={
            "track_index": 0,
            "clip_index": 0,
            "semitones": 12
        })
        assert response.status_code == 200

    def test_transpose_notes_negative(self):
        """Test transposing notes down."""
        response = self.client.post("/api/tracks/0/clips/0/transpose", json={
            "track_index": 0,
            "clip_index": 0,
            "semitones": -12
        })
        assert response.status_code == 200


# =============================================================================
# Warp Marker Endpoints
# =============================================================================

class TestWarpMarkerEndpoints:
    """Test warp marker endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_get_warp_markers(self):
        """Test GET /api/tracks/{track_index}/clips/{clip_index}/warp-markers."""
        self.mock_ableton.send_command.return_value = {"markers": []}
        response = self.client.get("/api/tracks/0/clips/0/warp-markers")
        assert response.status_code == 200

    def test_add_warp_marker(self):
        """Test POST /api/tracks/{track_index}/clips/{clip_index}/warp-markers."""
        response = self.client.post("/api/tracks/0/clips/0/warp-markers", json={
            "beat_time": 1.0
        })
        assert response.status_code == 200

    def test_add_warp_marker_with_sample_time(self):
        """Test adding warp marker with sample time."""
        response = self.client.post("/api/tracks/0/clips/0/warp-markers", json={
            "beat_time": 1.0,
            "sample_time": 44100.0
        })
        assert response.status_code == 200

    def test_delete_warp_marker(self):
        """Test DELETE /api/tracks/{track_index}/clips/{clip_index}/warp-markers."""
        # FastAPI TestClient doesn't support json in delete, need to use request body workaround
        from starlette.testclient import TestClient as StarletteClient
        response = self.client.request(
            "DELETE",
            "/api/tracks/0/clips/0/warp-markers",
            json={"beat_time": 1.0}
        )
        assert response.status_code == 200


# =============================================================================
# Audio Clip Property Endpoints
# =============================================================================

class TestAudioClipEndpoints:
    """Test audio clip property endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_get_clip_gain(self):
        """Test GET /api/tracks/{track_index}/clips/{clip_index}/gain."""
        self.mock_ableton.send_command.return_value = {"gain": 0.0}
        response = self.client.get("/api/tracks/0/clips/0/gain")
        assert response.status_code == 200

    def test_set_clip_gain(self):
        """Test PUT /api/tracks/{track_index}/clips/{clip_index}/gain."""
        response = self.client.put("/api/tracks/0/clips/0/gain", json={
            "gain": 3.0
        })
        assert response.status_code == 200

    def test_get_clip_pitch(self):
        """Test GET /api/tracks/{track_index}/clips/{clip_index}/pitch."""
        self.mock_ableton.send_command.return_value = {"pitch": 0}
        response = self.client.get("/api/tracks/0/clips/0/pitch")
        assert response.status_code == 200

    def test_set_clip_pitch(self):
        """Test PUT /api/tracks/{track_index}/clips/{clip_index}/pitch."""
        response = self.client.put("/api/tracks/0/clips/0/pitch", json={
            "pitch": 12
        })
        assert response.status_code == 200

    def test_set_clip_pitch_min(self):
        """Test minimum pitch (-48)."""
        response = self.client.put("/api/tracks/0/clips/0/pitch", json={
            "pitch": -48
        })
        assert response.status_code == 200

    def test_set_clip_pitch_max(self):
        """Test maximum pitch (48)."""
        response = self.client.put("/api/tracks/0/clips/0/pitch", json={
            "pitch": 48
        })
        assert response.status_code == 200

    def test_set_clip_pitch_invalid_too_low(self):
        """Test pitch below -48 returns 422."""
        response = self.client.put("/api/tracks/0/clips/0/pitch", json={
            "pitch": -49
        })
        assert response.status_code == 422

    def test_set_clip_pitch_invalid_too_high(self):
        """Test pitch above 48 returns 422."""
        response = self.client.put("/api/tracks/0/clips/0/pitch", json={
            "pitch": 49
        })
        assert response.status_code == 422


# =============================================================================
# Scene Endpoints
# =============================================================================

class TestSceneEndpoints:
    """Test all scene-related endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_get_all_scenes(self):
        """Test GET /api/scenes."""
        self.mock_ableton.send_command.return_value = {
            "scenes": [{"index": 0, "name": "Scene 1"}]
        }
        response = self.client.get("/api/scenes")
        assert response.status_code == 200

    def test_create_scene(self):
        """Test POST /api/scenes."""
        response = self.client.post("/api/scenes", json={"index": -1})
        assert response.status_code == 200

    def test_create_scene_with_name(self):
        """Test creating scene with name."""
        response = self.client.post("/api/scenes", json={"index": -1, "name": "Intro"})
        assert response.status_code == 200

    def test_delete_scene(self):
        """Test DELETE /api/scenes/{scene_index}."""
        response = self.client.delete("/api/scenes/0")
        assert response.status_code == 200
        self.mock_ableton.send_command.assert_called_with("delete_scene", {"scene_index": 0})

    def test_delete_scene_invalid_index(self):
        """Test delete scene with invalid index."""
        response = self.client.delete("/api/scenes/-1")
        assert response.status_code == 422

    def test_fire_scene(self):
        """Test POST /api/scenes/{scene_index}/fire."""
        response = self.client.post("/api/scenes/0/fire")
        assert response.status_code == 200
        self.mock_ableton.send_command.assert_called_with("fire_scene", {"scene_index": 0})

    def test_stop_scene(self):
        """Test POST /api/scenes/{scene_index}/stop."""
        response = self.client.post("/api/scenes/0/stop")
        assert response.status_code == 200
        self.mock_ableton.send_command.assert_called_with("stop_scene", {"scene_index": 0})

    def test_duplicate_scene(self):
        """Test POST /api/scenes/{scene_index}/duplicate."""
        response = self.client.post("/api/scenes/0/duplicate")
        assert response.status_code == 200
        self.mock_ableton.send_command.assert_called_with("duplicate_scene", {"scene_index": 0})

    def test_set_scene_name(self):
        """Test PUT /api/scenes/{scene_index}/name."""
        response = self.client.put("/api/scenes/0/name", json={
            "scene_index": 0,
            "name": "Chorus"
        })
        assert response.status_code == 200

    def test_get_scene_color(self):
        """Test GET /api/scenes/{scene_index}/color."""
        self.mock_ableton.send_command.return_value = {"color": 16725558}
        response = self.client.get("/api/scenes/0/color")
        assert response.status_code == 200

    def test_set_scene_color(self):
        """Test PUT /api/scenes/{scene_index}/color."""
        # SceneColorRequest only has 'color' field (0-69)
        response = self.client.put("/api/scenes/0/color", json={"color": 10})
        assert response.status_code == 200

    def test_select_scene(self):
        """Test POST /api/scenes/{scene_index}/select."""
        response = self.client.post("/api/scenes/0/select")
        assert response.status_code == 200


# =============================================================================
# Device Endpoints
# =============================================================================

class TestDeviceEndpoints:
    """Test all device-related endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_get_device_parameters(self, sample_device_info):
        """Test GET /api/tracks/{track_index}/devices/{device_index}."""
        self.mock_ableton.send_command.return_value = sample_device_info
        response = self.client.get("/api/tracks/0/devices/0")
        assert response.status_code == 200

    def test_get_device_invalid_track_index(self):
        """Test invalid track index returns 422."""
        response = self.client.get("/api/tracks/-1/devices/0")
        assert response.status_code == 422

    def test_get_device_invalid_device_index(self):
        """Test invalid device index returns 422."""
        response = self.client.get("/api/tracks/0/devices/-1")
        assert response.status_code == 422

    def test_get_device_index_too_high(self):
        """Test device index over max returns 422."""
        response = self.client.get("/api/tracks/0/devices/128")
        assert response.status_code == 422

    def test_set_device_parameter(self):
        """Test PUT /api/tracks/{track_index}/devices/{device_index}/parameter."""
        response = self.client.put("/api/tracks/0/devices/0/parameter", json={
            "track_index": 0,
            "device_index": 0,
            "parameter_index": 0,
            "value": 0.5
        })
        assert response.status_code == 200

    def test_toggle_device_on(self):
        """Test enabling a device."""
        response = self.client.put("/api/tracks/0/devices/0/toggle", json={
            "track_index": 0,
            "device_index": 0,
            "enabled": True
        })
        assert response.status_code == 200

    def test_toggle_device_off(self):
        """Test disabling a device."""
        response = self.client.put("/api/tracks/0/devices/0/toggle", json={
            "track_index": 0,
            "device_index": 0,
            "enabled": False
        })
        assert response.status_code == 200

    def test_delete_device(self):
        """Test DELETE /api/tracks/{track_index}/devices/{device_index}."""
        response = self.client.delete("/api/tracks/0/devices/0")
        assert response.status_code == 200
        self.mock_ableton.send_command.assert_called_with("delete_device", {
            "track_index": 0, "device_index": 0
        })


# =============================================================================
# Return Track & Send Endpoints
# =============================================================================

class TestReturnTrackEndpoints:
    """Test return track and send endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_get_return_tracks(self):
        """Test GET /api/returns."""
        self.mock_ableton.send_command.return_value = {
            "return_tracks": [{"index": 0, "name": "Return A"}]
        }
        response = self.client.get("/api/returns")
        assert response.status_code == 200

    def test_get_send_level(self):
        """Test GET /api/tracks/{track_index}/sends/{send_index}."""
        self.mock_ableton.send_command.return_value = {"level": 0.0}
        response = self.client.get("/api/tracks/0/sends/0")
        assert response.status_code == 200

    def test_get_send_level_invalid_send_index(self):
        """Test invalid send index returns 422."""
        response = self.client.get("/api/tracks/0/sends/12")
        assert response.status_code == 422

    def test_set_send_level(self):
        """Test POST /api/tracks/{track_index}/sends/{send_index}."""
        response = self.client.post("/api/tracks/0/sends/0", json={
            "track_index": 0,
            "send_index": 0,
            "level": 0.5
        })
        assert response.status_code == 200

    def test_set_return_volume(self):
        """Test PUT /api/returns/{return_index}/volume."""
        response = self.client.put("/api/returns/0/volume", json={
            "return_index": 0,
            "volume": 0.8
        })
        assert response.status_code == 200


# =============================================================================
# Recording Endpoints
# =============================================================================

class TestRecordingEndpoints:
    """Test recording-related endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_start_recording(self):
        """Test POST /api/recording/start."""
        response = self.client.post("/api/recording/start")
        assert response.status_code == 200
        self.mock_ableton.send_command.assert_called_with("start_recording")

    def test_stop_recording(self):
        """Test POST /api/recording/stop."""
        response = self.client.post("/api/recording/stop")
        assert response.status_code == 200
        self.mock_ableton.send_command.assert_called_with("stop_recording")

    def test_capture_midi(self):
        """Test POST /api/recording/capture."""
        response = self.client.post("/api/recording/capture")
        assert response.status_code == 200
        self.mock_ableton.send_command.assert_called_with("capture_midi")

    def test_set_overdub_on(self):
        """Test enabling overdub."""
        response = self.client.post("/api/recording/overdub", json={"enabled": True})
        assert response.status_code == 200

    def test_set_overdub_off(self):
        """Test disabling overdub."""
        response = self.client.post("/api/recording/overdub", json={"enabled": False})
        assert response.status_code == 200

    def test_toggle_session_record(self):
        """Test POST /api/recording/toggle-session."""
        response = self.client.post("/api/recording/toggle-session")
        assert response.status_code == 200

    def test_toggle_arrangement_record(self):
        """Test POST /api/recording/toggle-arrangement."""
        response = self.client.post("/api/recording/toggle-arrangement")
        assert response.status_code == 200


# =============================================================================
# Master Track Endpoints
# =============================================================================

class TestMasterTrackEndpoints:
    """Test master track endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_get_master_info(self):
        """Test GET /api/master."""
        self.mock_ableton.send_command.return_value = {
            "name": "Master", "volume": 1.0, "pan": 0.0
        }
        response = self.client.get("/api/master")
        assert response.status_code == 200

    def test_set_master_volume_valid(self):
        """Test setting valid master volume."""
        response = self.client.put("/api/master/volume", json={"volume": 0.8})
        assert response.status_code == 200

    def test_set_master_volume_min(self):
        """Test minimum master volume."""
        response = self.client.put("/api/master/volume", json={"volume": 0.0})
        assert response.status_code == 200

    def test_set_master_volume_max(self):
        """Test maximum master volume."""
        response = self.client.put("/api/master/volume", json={"volume": 1.0})
        assert response.status_code == 200

    def test_set_master_volume_invalid_negative(self):
        """Test negative master volume returns 422."""
        response = self.client.put("/api/master/volume", json={"volume": -0.1})
        assert response.status_code == 422

    def test_set_master_volume_invalid_over_max(self):
        """Test master volume over 1.0 returns 422."""
        response = self.client.put("/api/master/volume", json={"volume": 1.1})
        assert response.status_code == 422

    def test_set_master_pan_valid(self):
        """Test setting valid master pan."""
        response = self.client.put("/api/master/pan", json={"pan": 0.0})
        assert response.status_code == 200

    def test_set_master_pan_left(self):
        """Test setting master pan left."""
        response = self.client.put("/api/master/pan", json={"pan": -1.0})
        assert response.status_code == 200

    def test_set_master_pan_right(self):
        """Test setting master pan right."""
        response = self.client.put("/api/master/pan", json={"pan": 1.0})
        assert response.status_code == 200

    def test_set_master_pan_invalid(self):
        """Test invalid master pan returns 422."""
        response = self.client.put("/api/master/pan", json={"pan": 1.5})
        assert response.status_code == 422


# =============================================================================
# Browser Endpoints
# =============================================================================

class TestBrowserEndpoints:
    """Test browser-related endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_browse_path(self):
        """Test POST /api/browser/browse."""
        self.mock_ableton.send_command.return_value = {"items": []}
        response = self.client.post("/api/browser/browse", json={
            "path": ["Audio Effects", "EQ Eight"]
        })
        assert response.status_code == 200

    def test_search_browser(self):
        """Test POST /api/browser/search."""
        self.mock_ableton.send_command.return_value = {"results": []}
        response = self.client.post("/api/browser/search", json={
            "query": "reverb",
            "category": "audio_effects"
        })
        assert response.status_code == 200

    def test_search_browser_all_categories(self):
        """Test browser search with all categories."""
        response = self.client.post("/api/browser/search", json={
            "query": "synth",
            "category": "all"
        })
        assert response.status_code == 200

    def test_get_browser_children(self):
        """Test POST /api/browser/children."""
        response = self.client.post("/api/browser/children", json={
            "uri": "browser://some-uri"
        })
        assert response.status_code == 200

    def test_load_item_to_track(self):
        """Test POST /api/browser/load."""
        response = self.client.post("/api/browser/load", json={
            "track_index": 0,
            "uri": "browser://instrument-uri"
        })
        assert response.status_code == 200

    def test_load_item_to_return(self):
        """Test POST /api/browser/load-to-return."""
        response = self.client.post("/api/browser/load-to-return", json={
            "return_index": 0,
            "uri": "browser://effect-uri"
        })
        assert response.status_code == 200


# =============================================================================
# View & Selection Endpoints
# =============================================================================

class TestViewEndpoints:
    """Test view and selection endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_get_current_view(self):
        """Test GET /api/view."""
        self.mock_ableton.send_command.return_value = {
            "view": "Session",
            "selected_track": 0,
            "selected_scene": 0
        }
        response = self.client.get("/api/view")
        assert response.status_code == 200

    def test_focus_view(self):
        """Test POST /api/view/focus."""
        response = self.client.post("/api/view/focus", params={"view_name": "Arranger"})
        assert response.status_code == 200


# =============================================================================
# Arrangement Endpoints
# =============================================================================

class TestArrangementEndpoints:
    """Test arrangement-related endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_get_arrangement_length(self):
        """Test GET /api/arrangement/length."""
        self.mock_ableton.send_command.return_value = {
            "length": 64.0,
            "loop_start": 0.0,
            "loop_end": 16.0
        }
        response = self.client.get("/api/arrangement/length")
        assert response.status_code == 200

    def test_set_arrangement_loop(self):
        """Test POST /api/arrangement/loop."""
        response = self.client.post("/api/arrangement/loop", params={
            "loop_start": 0.0,
            "loop_length": 16.0,
            "loop_on": True
        })
        assert response.status_code == 200

    def test_jump_to_time(self):
        """Test POST /api/arrangement/jump."""
        response = self.client.post("/api/arrangement/jump", params={"time": 8.0})
        assert response.status_code == 200

    def test_get_locators(self):
        """Test GET /api/arrangement/locators."""
        self.mock_ableton.send_command.return_value = {"locators": []}
        response = self.client.get("/api/arrangement/locators")
        assert response.status_code == 200

    def test_create_locator(self):
        """Test POST /api/arrangement/locators."""
        response = self.client.post("/api/arrangement/locators", params={
            "time": 16.0,
            "name": "Chorus"
        })
        assert response.status_code == 200

    def test_delete_locator(self):
        """Test DELETE /api/arrangement/locators/{index}."""
        response = self.client.delete("/api/arrangement/locators/0")
        assert response.status_code == 200


# =============================================================================
# Routing Endpoints
# =============================================================================

class TestRoutingEndpoints:
    """Test I/O routing endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_get_track_input_routing(self):
        """Test GET /api/tracks/{track_index}/routing/input."""
        self.mock_ableton.send_command.return_value = {
            "routing_type": "Ext. In",
            "routing_channel": "1/2"
        }
        response = self.client.get("/api/tracks/0/routing/input")
        assert response.status_code == 200

    def test_get_track_output_routing(self):
        """Test GET /api/tracks/{track_index}/routing/output."""
        self.mock_ableton.send_command.return_value = {
            "routing_type": "Master",
            "routing_channel": ""
        }
        response = self.client.get("/api/tracks/0/routing/output")
        assert response.status_code == 200

    def test_set_track_input_routing(self):
        """Test PUT /api/tracks/{track_index}/routing/input."""
        response = self.client.put("/api/tracks/0/routing/input", params={
            "routing_type": "Ext. In",
            "routing_channel": "1/2"
        })
        assert response.status_code == 200

    def test_set_track_output_routing(self):
        """Test PUT /api/tracks/{track_index}/routing/output."""
        response = self.client.put("/api/tracks/0/routing/output", params={
            "routing_type": "Master"
        })
        assert response.status_code == 200

    def test_get_available_inputs(self):
        """Test GET /api/routing/inputs."""
        self.mock_ableton.send_command.return_value = {"inputs": []}
        response = self.client.get("/api/routing/inputs")
        assert response.status_code == 200

    def test_get_available_outputs(self):
        """Test GET /api/routing/outputs."""
        self.mock_ableton.send_command.return_value = {"outputs": []}
        response = self.client.get("/api/routing/outputs")
        assert response.status_code == 200


# =============================================================================
# Session Info Endpoints
# =============================================================================

class TestSessionInfoEndpoints:
    """Test session info endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_get_session_path(self):
        """Test GET /api/session/path."""
        self.mock_ableton.send_command.return_value = {
            "path": "/Users/test/Music/project.als"
        }
        response = self.client.get("/api/session/path")
        assert response.status_code == 200

    def test_is_session_modified(self):
        """Test GET /api/session/modified."""
        self.mock_ableton.send_command.return_value = {"modified": False}
        response = self.client.get("/api/session/modified")
        assert response.status_code == 200

    def test_get_cpu_load(self):
        """Test GET /api/session/cpu."""
        self.mock_ableton.send_command.return_value = {"cpu_load": 25.5}
        response = self.client.get("/api/session/cpu")
        assert response.status_code == 200


# =============================================================================
# AI Music Helper Endpoints
# =============================================================================

class TestAIMusicHelperEndpoints:
    """Test AI music helper endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_get_scale_notes(self):
        """Test GET /api/music/scale."""
        self.mock_ableton.send_command.return_value = {"notes": [60, 62, 64, 65, 67, 69, 71]}
        response = self.client.get("/api/music/scale", params={
            "root": "C",
            "scale_type": "major",
            "octave": 4
        })
        assert response.status_code == 200

    def test_get_scale_notes_minor(self):
        """Test getting minor scale notes."""
        response = self.client.get("/api/music/scale", params={
            "root": "A",
            "scale_type": "minor"
        })
        assert response.status_code == 200

    def test_get_scale_notes_with_sharps(self):
        """Test getting scale with sharp root."""
        response = self.client.get("/api/music/scale", params={
            "root": "F#",
            "scale_type": "minor"
        })
        assert response.status_code == 200

    def test_get_scale_notes_with_flats(self):
        """Test getting scale with flat root."""
        response = self.client.get("/api/music/scale", params={
            "root": "Bb",
            "scale_type": "major"
        })
        assert response.status_code == 200

    def test_quantize_clip(self):
        """Test POST /api/tracks/{track_index}/clips/{clip_index}/quantize."""
        response = self.client.post("/api/tracks/0/clips/0/quantize", json={
            "grid": 0.25,
            "strength": 1.0
        })
        assert response.status_code == 200

    def test_quantize_clip_default_strength(self):
        """Test quantize with default strength."""
        response = self.client.post("/api/tracks/0/clips/0/quantize", json={
            "grid": 0.5
        })
        assert response.status_code == 200

    def test_humanize_timing(self):
        """Test POST /api/tracks/{track_index}/clips/{clip_index}/humanize/timing."""
        response = self.client.post("/api/tracks/0/clips/0/humanize/timing", json={
            "amount": 0.1
        })
        assert response.status_code == 200

    def test_humanize_velocity(self):
        """Test POST /api/tracks/{track_index}/clips/{clip_index}/humanize/velocity."""
        response = self.client.post("/api/tracks/0/clips/0/humanize/velocity", json={
            "amount": 0.2
        })
        assert response.status_code == 200

    def test_generate_drum_pattern(self):
        """Test POST /api/music/drums."""
        response = self.client.post("/api/music/drums", json={
            "track_index": 0,
            "clip_index": 0,
            "style": "house",
            "length": 4.0
        })
        assert response.status_code == 200

    def test_generate_drum_pattern_styles(self):
        """Test various drum pattern styles."""
        for style in ["basic", "house", "techno", "breakbeat"]:
            response = self.client.post("/api/music/drums", json={
                "track_index": 0,
                "clip_index": 0,
                "style": style,
                "length": 4.0
            })
            assert response.status_code == 200

    def test_generate_bassline(self):
        """Test POST /api/music/bassline."""
        response = self.client.post("/api/music/bassline", json={
            "track_index": 0,
            "clip_index": 0,
            "root": 36,
            "scale_type": "minor",
            "length": 4.0
        })
        assert response.status_code == 200


# =============================================================================
# Generic Command Endpoint
# =============================================================================

class TestGenericCommandEndpoint:
    """Test the generic command endpoint."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_execute_command(self):
        """Test POST /api/command with valid command."""
        response = self.client.post("/api/command", json={
            "command": "get_session_info"
        })
        assert response.status_code == 200

    def test_execute_command_with_params(self):
        """Test command with parameters."""
        response = self.client.post("/api/command", json={
            "command": "set_tempo",
            "params": {"tempo": 140.0}
        })
        assert response.status_code == 200

    def test_execute_unknown_command(self):
        """Test unknown command returns error."""
        from fastapi import HTTPException
        self.mock_ableton.send_command.side_effect = HTTPException(
            status_code=400,
            detail="Unknown command: invalid_command"
        )
        response = self.client.post("/api/command", json={
            "command": "invalid_command"
        })
        # Can be 400 or 422 depending on how validation is handled
        assert response.status_code in [400, 422]


# =============================================================================
# Utility Endpoints
# =============================================================================

class TestUtilityEndpoints:
    """Test utility endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_root_endpoint(self):
        """Test GET /."""
        response = self.client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_health_endpoint(self):
        """Test GET /health."""
        self.mock_ableton.send_command.return_value = {"tempo": 120.0}
        response = self.client.get("/health")
        assert response.status_code == 200

    def test_tools_endpoint(self):
        """Test GET /tools."""
        response = self.client.get("/tools")
        assert response.status_code == 200
        assert "tools" in response.json()

    def test_commands_endpoint(self):
        """Test GET /api/commands."""
        response = self.client.get("/api/commands")
        assert response.status_code == 200
        assert "commands" in response.json()
        assert "count" in response.json()


# =============================================================================
# Generic Command Parameter Validation Tests
# =============================================================================

class TestCommandParameterValidation:
    """Test validate_command_params function via /api/command endpoint."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_command_missing_required_param(self):
        """Test command with missing required parameter returns 422."""
        response = self.client.post("/api/command", json={
            "command": "create_clip",
            "params": {"track_index": 0}  # Missing clip_index
        })
        assert response.status_code == 422
        # Check error message in either 'detail' or 'error' field
        error_msg = response.json().get("detail", "") or response.json().get("error", "")
        assert "clip_index" in error_msg.lower()

    def test_command_int_param_not_integer(self):
        """Test integer parameter with non-integer value."""
        response = self.client.post("/api/command", json={
            "command": "create_clip",
            "params": {"track_index": "not_an_int", "clip_index": 0}
        })
        assert response.status_code == 422

    def test_command_int_param_below_min(self):
        """Test integer parameter below minimum."""
        response = self.client.post("/api/command", json={
            "command": "get_track_info",
            "params": {"track_index": -1}
        })
        assert response.status_code == 422

    def test_command_int_param_above_max(self):
        """Test integer parameter above maximum."""
        response = self.client.post("/api/command", json={
            "command": "get_track_info",
            "params": {"track_index": 1000}
        })
        assert response.status_code == 422

    def test_command_float_param_not_number(self):
        """Test float parameter with non-numeric value."""
        response = self.client.post("/api/command", json={
            "command": "set_tempo",
            "params": {"tempo": "not_a_number"}
        })
        assert response.status_code == 422

    def test_command_float_param_below_min(self):
        """Test float parameter below minimum."""
        response = self.client.post("/api/command", json={
            "command": "set_tempo",
            "params": {"tempo": 10.0}  # Min is 20
        })
        assert response.status_code == 422

    def test_command_float_param_above_max(self):
        """Test float parameter above maximum."""
        response = self.client.post("/api/command", json={
            "command": "set_tempo",
            "params": {"tempo": 400.0}  # Max is 300
        })
        assert response.status_code == 422

    def test_command_bool_param_not_bool(self):
        """Test boolean parameter with non-boolean value."""
        response = self.client.post("/api/command", json={
            "command": "set_track_mute",
            "params": {"track_index": 0, "mute": "yes"}  # Should be bool
        })
        assert response.status_code == 422

    def test_command_string_param_not_string(self):
        """Test string parameter with non-string value."""
        response = self.client.post("/api/command", json={
            "command": "set_track_name",
            "params": {"track_index": 0, "name": 12345}  # Should be string
        })
        assert response.status_code == 422

    def test_command_string_param_too_long(self):
        """Test string parameter exceeding max length."""
        response = self.client.post("/api/command", json={
            "command": "set_track_name",
            "params": {"track_index": 0, "name": "x" * 300}  # Max is 256
        })
        assert response.status_code == 422

    def test_command_list_param_not_list(self):
        """Test list parameter with non-list value."""
        response = self.client.post("/api/command", json={
            "command": "add_notes_to_clip",
            "params": {
                "track_index": 0,
                "clip_index": 0,
                "notes": "not_a_list"  # Should be list
            }
        })
        assert response.status_code == 422

    def test_command_list_param_valid(self):
        """Test list parameter with valid values."""
        notes = [{"pitch": 60, "start_time": i * 0.25, "duration": 0.25} for i in range(10)]
        response = self.client.post("/api/command", json={
            "command": "add_notes_to_clip",
            "params": {
                "track_index": 0,
                "clip_index": 0,
                "notes": notes
            }
        })
        assert response.status_code == 200

    def test_command_string_valid_value(self):
        """Test string parameter with valid value."""
        response = self.client.post("/api/command", json={
            "command": "generate_drum_pattern",
            "params": {
                "track_index": 0,
                "clip_index": 0,
                "style": "techno"  # Valid value
            }
        })
        assert response.status_code == 200

    def test_command_valid_string_allowed_value(self):
        """Test string parameter with valid allowed value."""
        response = self.client.post("/api/command", json={
            "command": "generate_drum_pattern",
            "params": {
                "track_index": 0,
                "clip_index": 0,
                "style": "house"  # Valid value
            }
        })
        assert response.status_code == 200

    def test_command_optional_param_not_provided(self):
        """Test command with optional param not provided succeeds."""
        response = self.client.post("/api/command", json={
            "command": "create_midi_track",
            "params": {}  # All params optional
        })
        assert response.status_code == 200

    def test_command_extra_params_allowed(self):
        """Test command with extra params not in schema still passes."""
        response = self.client.post("/api/command", json={
            "command": "get_session_info",
            "params": {"extra_param": "value"}  # Not in schema
        })
        assert response.status_code == 200

    def test_command_bool_param_false(self):
        """Test boolean parameter with False value (not truthy check)."""
        response = self.client.post("/api/command", json={
            "command": "set_track_mute",
            "params": {"track_index": 0, "mute": False}
        })
        assert response.status_code == 200

    def test_command_int_coercion_blocked(self):
        """Test that boolean is not accepted as int."""
        response = self.client.post("/api/command", json={
            "command": "get_track_info",
            "params": {"track_index": True}  # Boolean, not int
        })
        assert response.status_code == 422


# =============================================================================
# Additional Endpoint Coverage Tests
# =============================================================================

class TestAdditionalEndpointCoverage:
    """Additional tests for better endpoint coverage."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client, self.mock_ableton = create_test_client()

    def test_create_midi_track_at_negative_index(self):
        """Test creating MIDI track at negative index (should use -1 for end)."""
        response = self.client.post("/api/tracks/midi", json={
            "index": -1,
            "name": "Test Track"
        })
        assert response.status_code == 200

    def test_create_clip_with_both_indices(self):
        """Test creating clip with both indices in path and body."""
        response = self.client.post("/api/tracks/0/clips/0", json={
            "track_index": 0,
            "clip_index": 0,
            "length": 4.0,
            "name": "Test Clip"
        })
        assert response.status_code == 200

    def test_get_clip_notes_various_tracks(self):
        """Test getting notes from clips on different tracks."""
        for track_idx in [0, 1, 5]:
            response = self.client.get(f"/api/tracks/{track_idx}/clips/0/notes")
            assert response.status_code == 200

    def test_fire_scene_various_indices(self):
        """Test firing scenes at various indices."""
        for scene_idx in [0, 1, 10]:
            response = self.client.post(f"/api/scenes/{scene_idx}/fire")
            assert response.status_code == 200

    def test_set_clip_loop_all_params(self):
        """Test setting clip loop with all parameters."""
        response = self.client.put("/api/tracks/0/clips/0/loop", json={
            "track_index": 0,
            "clip_index": 0,
            "loop_start": 0.0,
            "loop_end": 4.0,
            "looping": True
        })
        assert response.status_code == 200

    def test_set_scene_color_valid(self):
        """Test setting scene color with valid color index."""
        response = self.client.put("/api/scenes/0/color", json={
            "scene_index": 0,
            "color": 5
        })
        assert response.status_code == 200

    def test_add_warp_marker_minimal(self):
        """Test adding warp marker with minimal params."""
        response = self.client.post("/api/tracks/0/clips/0/warp-markers", json={
            "beat_time": 1.0
        })
        assert response.status_code == 200

    def test_delete_warp_marker_at_time(self):
        """Test deleting warp marker at specific time."""
        response = self.client.request(
            "DELETE",
            "/api/tracks/0/clips/0/warp-markers",
            json={"beat_time": 1.0}
        )
        assert response.status_code == 200

    def test_set_clip_gain_boundary_values(self):
        """Test setting clip gain at boundary values."""
        for gain in [0.0, 0.5, 1.0]:
            response = self.client.put("/api/tracks/0/clips/0/gain", json={
                "gain": gain
            })
            assert response.status_code == 200

    def test_get_all_scenes_returns_list(self):
        """Test get all scenes returns proper structure."""
        self.mock_ableton.send_command.return_value = {
            "scenes": [
                {"index": 0, "name": "Scene 1"},
                {"index": 1, "name": "Scene 2"}
            ]
        }
        response = self.client.get("/api/scenes")
        assert response.status_code == 200
        data = response.json()
        assert "scenes" in data

    def test_browse_path_with_path(self):
        """Test browsing path with specific path list."""
        self.mock_ableton.send_command.return_value = {"items": []}
        response = self.client.post("/api/browser/browse", json={
            "path": ["Drums", "Acoustic"]
        })
        assert response.status_code == 200

    def test_load_item_to_track_with_uri(self):
        """Test loading browser item to track."""
        response = self.client.post("/api/browser/load", json={
            "uri": "userfolder:///path/to/preset.adg",
            "track_index": 0
        })
        assert response.status_code == 200

    def test_focus_view_session(self):
        """Test focusing session view."""
        response = self.client.post("/api/view/focus", params={
            "view_name": "Session"
        })
        assert response.status_code == 200

    def test_focus_view_arranger(self):
        """Test focusing arranger view."""
        response = self.client.post("/api/view/focus", params={
            "view_name": "Arranger"
        })
        assert response.status_code == 200

    def test_set_arrangement_loop_with_all_params(self):
        """Test setting arrangement loop with all parameters."""
        response = self.client.post("/api/arrangement/loop", params={
            "loop_start": 0.0,
            "loop_length": 16.0,
            "loop_on": True
        })
        assert response.status_code == 200

    def test_create_locator_with_name(self):
        """Test creating locator with name."""
        response = self.client.post("/api/arrangement/locators", params={
            "time": 8.0,
            "name": "Chorus"
        })
        assert response.status_code == 200

    def test_humanize_timing_various_amounts(self):
        """Test humanize with various timing amounts."""
        for amount in [0.01, 0.1, 0.5]:
            response = self.client.post("/api/tracks/0/clips/0/humanize/timing", json={
                "amount": amount
            })
            assert response.status_code == 200

    def test_generate_bassline_all_params(self):
        """Test bassline generation with all parameters."""
        response = self.client.post("/api/music/bassline", json={
            "track_index": 0,
            "clip_index": 0,
            "root": 36,
            "scale_type": "minor",
            "length": 8.0,
            "density": 0.5
        })
        assert response.status_code == 200
