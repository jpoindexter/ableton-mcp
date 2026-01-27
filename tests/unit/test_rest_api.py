# test_rest_api.py - Unit tests for REST API server
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'MCP_Server'))


class TestRestAPIValidation:
    """Test request validation."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client with mocked Ableton connection."""
        with patch('rest_api_server.AbletonConnection') as mock_conn:
            mock_instance = MagicMock()
            mock_instance.send_command.return_value = {"status": "success", "result": {}}
            mock_conn.return_value = mock_instance

            from rest_api_server import app
            self.client = TestClient(app)
            self.mock_ableton = mock_instance

    def test_tempo_validation_valid(self):
        """Test valid tempo values."""
        response = self.client.put("/api/tempo", json={"tempo": 120.0})
        assert response.status_code == 200

    def test_tempo_validation_too_low(self):
        """Test tempo below minimum."""
        response = self.client.put("/api/tempo", json={"tempo": 10.0})
        assert response.status_code == 422  # Validation error

    def test_tempo_validation_too_high(self):
        """Test tempo above maximum."""
        response = self.client.put("/api/tempo", json={"tempo": 400.0})
        assert response.status_code == 422

    def test_volume_validation_valid(self):
        """Test valid volume values."""
        response = self.client.put("/api/tracks/0/volume", json={"volume": 0.5})
        assert response.status_code == 200

    def test_volume_validation_out_of_range(self):
        """Test volume outside 0-1 range."""
        response = self.client.put("/api/tracks/0/volume", json={"volume": 1.5})
        assert response.status_code == 422

    def test_pan_validation_valid(self):
        """Test valid pan values."""
        response = self.client.put("/api/tracks/0/pan", json={"pan": -0.5})
        assert response.status_code == 200

    def test_pan_validation_out_of_range(self):
        """Test pan outside -1 to 1 range."""
        response = self.client.put("/api/tracks/0/pan", json={"pan": 2.0})
        assert response.status_code == 422

    def test_note_pitch_validation(self):
        """Test MIDI note pitch validation."""
        # Valid pitch
        response = self.client.post("/api/tracks/0/clips/0/notes", json={
            "notes": [{"pitch": 60, "start_time": 0, "duration": 0.5, "velocity": 100}]
        })
        assert response.status_code == 200

    def test_note_pitch_invalid(self):
        """Test invalid MIDI pitch."""
        response = self.client.post("/api/tracks/0/clips/0/notes", json={
            "notes": [{"pitch": 200, "start_time": 0, "duration": 0.5, "velocity": 100}]
        })
        assert response.status_code == 422

    def test_note_velocity_validation(self):
        """Test MIDI velocity validation."""
        response = self.client.post("/api/tracks/0/clips/0/notes", json={
            "notes": [{"pitch": 60, "start_time": 0, "duration": 0.5, "velocity": 150}]
        })
        assert response.status_code == 422

    def test_note_start_time_validation(self):
        """Test note start time must be non-negative."""
        response = self.client.post("/api/tracks/0/clips/0/notes", json={
            "notes": [{"pitch": 60, "start_time": -1.0, "duration": 0.5, "velocity": 100}]
        })
        assert response.status_code == 422

    def test_note_duration_validation(self):
        """Test note duration must be positive."""
        response = self.client.post("/api/tracks/0/clips/0/notes", json={
            "notes": [{"pitch": 60, "start_time": 0, "duration": 0, "velocity": 100}]
        })
        assert response.status_code == 422


class TestRestAPIEndpoints:
    """Test REST API endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client with mocked Ableton connection."""
        with patch('rest_api_server.AbletonConnection') as mock_conn:
            mock_instance = MagicMock()
            mock_instance.send_command.return_value = {"status": "success", "result": {}}
            mock_conn.return_value = mock_instance

            from rest_api_server import app
            self.client = TestClient(app)
            self.mock_ableton = mock_instance

    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get("/api/health")
        assert response.status_code == 200

    def test_get_session_info(self):
        """Test get session info endpoint."""
        self.mock_ableton.send_command.return_value = {
            "tempo": 120.0,
            "is_playing": False
        }
        response = self.client.get("/api/session")
        assert response.status_code == 200

    def test_get_track_info(self):
        """Test get track info endpoint."""
        response = self.client.get("/api/tracks/0")
        assert response.status_code == 200

    def test_create_midi_track(self):
        """Test create MIDI track endpoint."""
        response = self.client.post("/api/tracks/midi", json={"index": -1})
        assert response.status_code == 200

    def test_create_audio_track(self):
        """Test create audio track endpoint."""
        response = self.client.post("/api/tracks/audio", json={"index": -1})
        assert response.status_code == 200

    def test_set_track_mute(self):
        """Test set track mute endpoint."""
        response = self.client.put("/api/tracks/0/mute", json={"value": True})
        assert response.status_code == 200

    def test_set_track_solo(self):
        """Test set track solo endpoint."""
        response = self.client.put("/api/tracks/0/solo", json={"value": True})
        assert response.status_code == 200

    def test_get_all_scenes(self):
        """Test get all scenes endpoint."""
        response = self.client.get("/api/scenes")
        assert response.status_code == 200

    def test_fire_scene(self):
        """Test fire scene endpoint."""
        response = self.client.post("/api/scenes/0/fire")
        assert response.status_code == 200

    def test_get_track_color(self):
        """Test get track color endpoint."""
        response = self.client.get("/api/tracks/0/color")
        assert response.status_code == 200

    def test_get_clip_color(self):
        """Test get clip color endpoint."""
        response = self.client.get("/api/tracks/0/clips/0/color")
        assert response.status_code == 200

    def test_get_clip_loop(self):
        """Test get clip loop endpoint."""
        response = self.client.get("/api/tracks/0/clips/0/loop")
        assert response.status_code == 200

    def test_get_warp_markers(self):
        """Test get warp markers endpoint."""
        response = self.client.get("/api/tracks/0/clips/0/warp-markers")
        assert response.status_code == 200

    def test_add_warp_marker(self):
        """Test add warp marker endpoint."""
        response = self.client.post("/api/tracks/0/clips/0/warp-markers",
                                   json={"beat_time": 1.0})
        assert response.status_code == 200

    def test_freeze_track(self):
        """Test freeze track endpoint."""
        response = self.client.post("/api/tracks/0/freeze")
        assert response.status_code == 200

    def test_flatten_track(self):
        """Test flatten track endpoint."""
        response = self.client.post("/api/tracks/0/flatten")
        assert response.status_code == 200


class TestRateLimiting:
    """Test rate limiting middleware."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup with rate limiting enabled."""
        with patch.dict(os.environ, {"RATE_LIMIT_ENABLED": "true", "RATE_LIMIT_REQUESTS": "5"}):
            with patch('rest_api_server.AbletonConnection') as mock_conn:
                mock_instance = MagicMock()
                mock_instance.send_command.return_value = {"status": "success"}
                mock_conn.return_value = mock_instance

                # Need to reimport to pick up env vars
                import importlib
                import rest_api_server
                importlib.reload(rest_api_server)

                from rest_api_server import app
                self.client = TestClient(app)

    def test_rate_limit_not_exceeded(self):
        """Test requests within rate limit."""
        for _ in range(3):
            response = self.client.get("/api/session")
            assert response.status_code in [200, 503]  # 503 if not connected


class TestAPIKeySecurity:
    """Test API key authentication."""

    def test_no_api_key_when_disabled(self):
        """Test that requests work without API key when auth disabled."""
        with patch.dict(os.environ, {"REST_API_KEY": ""}):
            with patch('rest_api_server.AbletonConnection') as mock_conn:
                mock_instance = MagicMock()
                mock_instance.send_command.return_value = {"status": "success"}
                mock_conn.return_value = mock_instance

                from rest_api_server import app
                client = TestClient(app)
                response = client.get("/api/health")
                assert response.status_code == 200
