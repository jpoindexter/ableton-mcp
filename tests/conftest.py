# conftest.py - pytest configuration and fixtures
"""
Comprehensive test fixtures for AbletonMCP testing.
Provides mocks for socket connections, Ableton responses, and API clients.
"""
import pytest
import sys
import os
import json
import time
from unittest.mock import patch, MagicMock, PropertyMock

# Add project paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MCP_Server'))


# =============================================================================
# Socket and Connection Mocks
# =============================================================================

@pytest.fixture
def mock_socket(mocker):
    """Mock socket for testing without real Ableton connection."""
    mock = mocker.patch('socket.socket')
    mock_instance = mock.return_value
    mock_instance.connect.return_value = None
    mock_instance.sendall.return_value = None
    mock_instance.recv.return_value = b'{"status": "success", "result": {}}'
    mock_instance.settimeout.return_value = None
    mock_instance.close.return_value = None
    return mock_instance


@pytest.fixture
def mock_socket_timeout(mocker):
    """Mock socket that raises timeout."""
    import socket
    mock = mocker.patch('socket.socket')
    mock_instance = mock.return_value
    mock_instance.connect.return_value = None
    mock_instance.sendall.return_value = None
    mock_instance.recv.side_effect = socket.timeout("Connection timed out")
    return mock_instance


@pytest.fixture
def mock_socket_connection_error(mocker):
    """Mock socket that raises connection error."""
    mock = mocker.patch('socket.socket')
    mock_instance = mock.return_value
    mock_instance.connect.side_effect = ConnectionRefusedError("Connection refused")
    return mock_instance


@pytest.fixture
def mock_socket_invalid_json(mocker):
    """Mock socket that returns invalid JSON."""
    mock = mocker.patch('socket.socket')
    mock_instance = mock.return_value
    mock_instance.connect.return_value = None
    mock_instance.sendall.return_value = None
    mock_instance.recv.return_value = b'not valid json {'
    return mock_instance


# =============================================================================
# Ableton Response Factories
# =============================================================================

@pytest.fixture
def mock_ableton_response():
    """Factory for creating mock Ableton responses."""
    def _create_response(status="success", result=None, error=None):
        response = {"status": status}
        if result is not None:
            response["result"] = result
        if error is not None:
            response["error"] = error
            response["message"] = error
        return response
    return _create_response


@pytest.fixture
def mock_ableton_success_response():
    """Creates a successful Ableton response bytes object."""
    def _create(result=None):
        response = {"status": "success", "result": result or {}}
        return json.dumps(response).encode('utf-8')
    return _create


@pytest.fixture
def mock_ableton_error_response():
    """Creates an error Ableton response bytes object."""
    def _create(message="Unknown error"):
        response = {"status": "error", "message": message}
        return json.dumps(response).encode('utf-8')
    return _create


# =============================================================================
# Sample Data Fixtures
# =============================================================================

@pytest.fixture
def sample_track_info():
    """Sample track info response."""
    return {
        "index": 0,
        "name": "Test Track",
        "is_audio_track": False,
        "is_midi_track": True,
        "mute": False,
        "solo": False,
        "arm": False,
        "volume": 0.85,
        "panning": 0.0,
        "color": 16725558,
        "clip_slots": [],
        "devices": []
    }


@pytest.fixture
def sample_clip_info():
    """Sample clip info response."""
    return {
        "track_index": 0,
        "clip_index": 0,
        "name": "Test Clip",
        "length": 4.0,
        "is_midi_clip": True,
        "is_audio_clip": False,
        "is_playing": False,
        "is_recording": False,
        "looping": True,
        "loop_start": 0.0,
        "loop_end": 4.0,
        "color": 16725558
    }


@pytest.fixture
def sample_session_info():
    """Sample session info response."""
    return {
        "tempo": 120.0,
        "signature_numerator": 4,
        "signature_denominator": 4,
        "is_playing": False,
        "track_count": 8,
        "scene_count": 8,
        "return_track_count": 2,
        "master_track": {"name": "Master", "volume": 1.0}
    }


@pytest.fixture
def sample_notes():
    """Sample MIDI notes."""
    return [
        {"pitch": 60, "start_time": 0.0, "duration": 0.5, "velocity": 100},
        {"pitch": 64, "start_time": 0.5, "duration": 0.5, "velocity": 100},
        {"pitch": 67, "start_time": 1.0, "duration": 0.5, "velocity": 100}
    ]


@pytest.fixture
def sample_device_info():
    """Sample device info response."""
    return {
        "name": "Test Device",
        "class_name": "PluginDevice",
        "is_active": True,
        "parameters": [
            {"name": "Device On", "value": 1.0, "min": 0.0, "max": 1.0},
            {"name": "Dry/Wet", "value": 1.0, "min": 0.0, "max": 1.0}
        ]
    }


@pytest.fixture
def sample_scene_info():
    """Sample scene info response."""
    return {
        "index": 0,
        "name": "Scene 1",
        "color": 16725558,
        "is_triggered": False
    }


@pytest.fixture
def sample_return_track_info():
    """Sample return track info response."""
    return {
        "index": 0,
        "name": "Return A",
        "volume": 0.85,
        "panning": 0.0,
        "devices": []
    }


# =============================================================================
# FastAPI Test Client Fixtures
# =============================================================================

@pytest.fixture
def mock_ableton_connection():
    """Create a mock AbletonConnection that can be configured per test."""
    mock = MagicMock()
    mock.send_command.return_value = {}
    return mock


@pytest.fixture
def client(mock_ableton_connection):
    """Create a test client with mocked Ableton connection."""
    # We need to patch at module level before importing
    with patch.dict(os.environ, {
        "RATE_LIMIT_ENABLED": "false",
        "REST_API_KEY": ""
    }):
        with patch('rest_api_server.AbletonConnection') as MockClass:
            MockClass.return_value = mock_ableton_connection

            # Need to reload module to pick up new environment
            import importlib
            import rest_api_server
            importlib.reload(rest_api_server)

            # Re-patch the global ableton connection
            rest_api_server.ableton = mock_ableton_connection

            from fastapi.testclient import TestClient
            yield TestClient(rest_api_server.app), mock_ableton_connection


@pytest.fixture
def client_with_auth():
    """Create a test client with API key authentication enabled."""
    test_api_key = "test-secret-key-12345"

    with patch.dict(os.environ, {
        "REST_API_KEY": test_api_key,
        "RATE_LIMIT_ENABLED": "false"
    }):
        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {}

        with patch('rest_api_server.AbletonConnection') as MockClass:
            MockClass.return_value = mock_conn

            import importlib
            import rest_api_server
            importlib.reload(rest_api_server)
            rest_api_server.ableton = mock_conn

            from fastapi.testclient import TestClient
            yield TestClient(rest_api_server.app), mock_conn, test_api_key


@pytest.fixture
def client_with_rate_limit():
    """Create a test client with rate limiting enabled."""
    with patch.dict(os.environ, {
        "RATE_LIMIT_ENABLED": "true",
        "RATE_LIMIT_REQUESTS": "5",
        "RATE_LIMIT_WINDOW": "60",
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

            from fastapi.testclient import TestClient
            yield TestClient(rest_api_server.app), mock_conn


@pytest.fixture
def client_disconnected():
    """Create a test client where Ableton is disconnected."""
    from fastapi import HTTPException

    with patch.dict(os.environ, {
        "RATE_LIMIT_ENABLED": "false",
        "REST_API_KEY": ""
    }):
        mock_conn = MagicMock()
        mock_conn.send_command.side_effect = HTTPException(
            status_code=503,
            detail="Could not connect to Ableton"
        )

        with patch('rest_api_server.AbletonConnection') as MockClass:
            MockClass.return_value = mock_conn

            import importlib
            import rest_api_server
            importlib.reload(rest_api_server)
            rest_api_server.ableton = mock_conn

            from fastapi.testclient import TestClient
            yield TestClient(rest_api_server.app), mock_conn


# =============================================================================
# Utility Fixtures
# =============================================================================

@pytest.fixture
def valid_note():
    """A valid MIDI note for testing."""
    return {"pitch": 60, "start_time": 0.0, "duration": 0.5, "velocity": 100}


@pytest.fixture
def invalid_notes():
    """Collection of invalid notes for boundary testing."""
    return {
        "pitch_too_high": {"pitch": 128, "start_time": 0.0, "duration": 0.5, "velocity": 100},
        "pitch_negative": {"pitch": -1, "start_time": 0.0, "duration": 0.5, "velocity": 100},
        "velocity_too_high": {"pitch": 60, "start_time": 0.0, "duration": 0.5, "velocity": 128},
        "velocity_negative": {"pitch": 60, "start_time": 0.0, "duration": 0.5, "velocity": -1},
        "duration_zero": {"pitch": 60, "start_time": 0.0, "duration": 0.0, "velocity": 100},
        "duration_negative": {"pitch": 60, "start_time": 0.0, "duration": -0.5, "velocity": 100},
        "start_time_negative": {"pitch": 60, "start_time": -1.0, "duration": 0.5, "velocity": 100},
    }
