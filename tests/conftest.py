# conftest.py - pytest configuration and fixtures
import pytest
import sys
import os

# Add project paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MCP_Server'))


@pytest.fixture
def mock_socket(mocker):
    """Mock socket for testing without real Ableton connection."""
    mock = mocker.patch('socket.socket')
    mock_instance = mock.return_value
    mock_instance.connect.return_value = None
    mock_instance.sendall.return_value = None
    mock_instance.recv.return_value = b'{"status": "success", "result": {}}'
    return mock_instance


@pytest.fixture
def mock_ableton_response():
    """Factory for creating mock Ableton responses."""
    def _create_response(status="success", result=None, error=None):
        response = {"status": status}
        if result is not None:
            response["result"] = result
        if error is not None:
            response["error"] = error
        return response
    return _create_response


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
        "is_playing": False,
        "is_recording": False,
        "looping": True,
        "loop_start": 0.0,
        "loop_end": 4.0
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
        "return_track_count": 2
    }


@pytest.fixture
def sample_notes():
    """Sample MIDI notes."""
    return [
        {"pitch": 60, "start_time": 0.0, "duration": 0.5, "velocity": 100},
        {"pitch": 64, "start_time": 0.5, "duration": 0.5, "velocity": 100},
        {"pitch": 67, "start_time": 1.0, "duration": 0.5, "velocity": 100}
    ]
