# test_validation.py - Unit tests for parameter validation
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'MCP_Server'))

from pydantic import ValidationError


class TestTempoValidation:
    """Test tempo validation."""

    def test_valid_tempo_min(self):
        """Test minimum valid tempo."""
        from rest_api_server import TempoRequest
        req = TempoRequest(tempo=20.0)
        assert req.tempo == 20.0

    def test_valid_tempo_max(self):
        """Test maximum valid tempo."""
        from rest_api_server import TempoRequest
        req = TempoRequest(tempo=300.0)
        assert req.tempo == 300.0

    def test_valid_tempo_normal(self):
        """Test normal tempo value."""
        from rest_api_server import TempoRequest
        req = TempoRequest(tempo=120.0)
        assert req.tempo == 120.0

    def test_invalid_tempo_too_low(self):
        """Test tempo below minimum."""
        from rest_api_server import TempoRequest
        with pytest.raises(ValidationError):
            TempoRequest(tempo=19.9)

    def test_invalid_tempo_too_high(self):
        """Test tempo above maximum."""
        from rest_api_server import TempoRequest
        with pytest.raises(ValidationError):
            TempoRequest(tempo=300.1)


class TestVolumeValidation:
    """Test volume validation."""

    def test_valid_volume_min(self):
        """Test minimum valid volume."""
        from rest_api_server import TrackVolumeRequest
        req = TrackVolumeRequest(volume=0.0)
        assert req.volume == 0.0

    def test_valid_volume_max(self):
        """Test maximum valid volume."""
        from rest_api_server import TrackVolumeRequest
        req = TrackVolumeRequest(volume=1.0)
        assert req.volume == 1.0

    def test_invalid_volume_negative(self):
        """Test negative volume."""
        from rest_api_server import TrackVolumeRequest
        with pytest.raises(ValidationError):
            TrackVolumeRequest(volume=-0.1)

    def test_invalid_volume_too_high(self):
        """Test volume above 1."""
        from rest_api_server import TrackVolumeRequest
        with pytest.raises(ValidationError):
            TrackVolumeRequest(volume=1.1)


class TestPanValidation:
    """Test pan validation."""

    def test_valid_pan_left(self):
        """Test full left pan."""
        from rest_api_server import TrackPanRequest
        req = TrackPanRequest(pan=-1.0)
        assert req.pan == -1.0

    def test_valid_pan_right(self):
        """Test full right pan."""
        from rest_api_server import TrackPanRequest
        req = TrackPanRequest(pan=1.0)
        assert req.pan == 1.0

    def test_valid_pan_center(self):
        """Test center pan."""
        from rest_api_server import TrackPanRequest
        req = TrackPanRequest(pan=0.0)
        assert req.pan == 0.0

    def test_invalid_pan_too_left(self):
        """Test pan too far left."""
        from rest_api_server import TrackPanRequest
        with pytest.raises(ValidationError):
            TrackPanRequest(pan=-1.1)

    def test_invalid_pan_too_right(self):
        """Test pan too far right."""
        from rest_api_server import TrackPanRequest
        with pytest.raises(ValidationError):
            TrackPanRequest(pan=1.1)


class TestNoteValidation:
    """Test MIDI note validation."""

    def test_valid_note(self):
        """Test valid MIDI note."""
        from rest_api_server import Note
        note = Note(pitch=60, start_time=0.0, duration=0.5, velocity=100)
        assert note.pitch == 60
        assert note.start_time == 0.0
        assert note.duration == 0.5
        assert note.velocity == 100

    def test_valid_note_min_pitch(self):
        """Test minimum MIDI pitch."""
        from rest_api_server import Note
        note = Note(pitch=0, start_time=0.0, duration=0.5)
        assert note.pitch == 0

    def test_valid_note_max_pitch(self):
        """Test maximum MIDI pitch."""
        from rest_api_server import Note
        note = Note(pitch=127, start_time=0.0, duration=0.5)
        assert note.pitch == 127

    def test_invalid_pitch_too_high(self):
        """Test pitch above 127."""
        from rest_api_server import Note
        with pytest.raises(ValidationError):
            Note(pitch=128, start_time=0.0, duration=0.5)

    def test_invalid_pitch_negative(self):
        """Test negative pitch."""
        from rest_api_server import Note
        with pytest.raises(ValidationError):
            Note(pitch=-1, start_time=0.0, duration=0.5)

    def test_invalid_velocity_too_high(self):
        """Test velocity above 127."""
        from rest_api_server import Note
        with pytest.raises(ValidationError):
            Note(pitch=60, start_time=0.0, duration=0.5, velocity=128)

    def test_invalid_duration_zero(self):
        """Test zero duration."""
        from rest_api_server import Note
        with pytest.raises(ValidationError):
            Note(pitch=60, start_time=0.0, duration=0.0)

    def test_invalid_duration_negative(self):
        """Test negative duration."""
        from rest_api_server import Note
        with pytest.raises(ValidationError):
            Note(pitch=60, start_time=0.0, duration=-0.5)

    def test_invalid_start_time_negative(self):
        """Test negative start time."""
        from rest_api_server import Note
        with pytest.raises(ValidationError):
            Note(pitch=60, start_time=-1.0, duration=0.5)

    def test_default_velocity(self):
        """Test default velocity value."""
        from rest_api_server import Note
        note = Note(pitch=60, start_time=0.0, duration=0.5)
        assert note.velocity == 100


class TestIndexValidation:
    """Test index validation functions."""

    def test_valid_track_index(self):
        """Test valid track index."""
        from rest_api_server import validate_track_index
        assert validate_track_index(0) == 0
        assert validate_track_index(100) == 100

    def test_invalid_track_index_negative(self):
        """Test negative track index."""
        from rest_api_server import validate_track_index
        with pytest.raises(ValueError):
            validate_track_index(-1)

    def test_invalid_track_index_too_high(self):
        """Test track index above max."""
        from rest_api_server import validate_track_index, MAX_TRACK_INDEX
        with pytest.raises(ValueError):
            validate_track_index(MAX_TRACK_INDEX + 1)

    def test_valid_clip_index(self):
        """Test valid clip index."""
        from rest_api_server import validate_clip_index
        assert validate_clip_index(0) == 0
        assert validate_clip_index(50) == 50

    def test_valid_scene_index(self):
        """Test valid scene index."""
        from rest_api_server import validate_scene_index
        assert validate_scene_index(0) == 0
        assert validate_scene_index(100) == 100

    def test_valid_device_index(self):
        """Test valid device index."""
        from rest_api_server import validate_device_index
        assert validate_device_index(0) == 0
        assert validate_device_index(50) == 50
