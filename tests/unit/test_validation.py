# test_validation.py - Comprehensive parameter validation tests
"""
Complete validation testing for all Pydantic models and validation functions.
Tests boundary conditions, edge cases, and type validation.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'MCP_Server'))

from pydantic import ValidationError


# =============================================================================
# Tempo Validation
# =============================================================================

class TestTempoValidation:
    """Test tempo validation."""

    def test_valid_tempo_min(self):
        """Test minimum valid tempo (20 BPM)."""
        from rest_api_server import TempoRequest
        req = TempoRequest(tempo=20.0)
        assert req.tempo == 20.0

    def test_valid_tempo_max(self):
        """Test maximum valid tempo (300 BPM)."""
        from rest_api_server import TempoRequest
        req = TempoRequest(tempo=300.0)
        assert req.tempo == 300.0

    def test_valid_tempo_normal(self):
        """Test normal tempo value (120 BPM)."""
        from rest_api_server import TempoRequest
        req = TempoRequest(tempo=120.0)
        assert req.tempo == 120.0

    def test_valid_tempo_integer(self):
        """Test tempo with integer value."""
        from rest_api_server import TempoRequest
        req = TempoRequest(tempo=128)
        assert req.tempo == 128.0

    def test_valid_tempo_decimal(self):
        """Test tempo with decimal precision."""
        from rest_api_server import TempoRequest
        req = TempoRequest(tempo=120.5)
        assert req.tempo == 120.5

    def test_invalid_tempo_too_low(self):
        """Test tempo below minimum (19.9 BPM)."""
        from rest_api_server import TempoRequest
        with pytest.raises(ValidationError) as exc_info:
            TempoRequest(tempo=19.9)
        assert "Tempo must be between 20 and 300 BPM" in str(exc_info.value)

    def test_invalid_tempo_too_high(self):
        """Test tempo above maximum (300.1 BPM)."""
        from rest_api_server import TempoRequest
        with pytest.raises(ValidationError) as exc_info:
            TempoRequest(tempo=300.1)
        assert "Tempo must be between 20 and 300 BPM" in str(exc_info.value)

    def test_invalid_tempo_zero(self):
        """Test zero tempo."""
        from rest_api_server import TempoRequest
        with pytest.raises(ValidationError):
            TempoRequest(tempo=0)

    def test_invalid_tempo_negative(self):
        """Test negative tempo."""
        from rest_api_server import TempoRequest
        with pytest.raises(ValidationError):
            TempoRequest(tempo=-100)

    def test_invalid_tempo_none(self):
        """Test None tempo."""
        from rest_api_server import TempoRequest
        with pytest.raises(ValidationError):
            TempoRequest(tempo=None)


# =============================================================================
# Volume Validation
# =============================================================================

class TestVolumeValidation:
    """Test volume validation."""

    def test_valid_volume_min(self):
        """Test minimum valid volume (0.0)."""
        from rest_api_server import TrackVolumeRequest
        req = TrackVolumeRequest(volume=0.0)
        assert req.volume == 0.0

    def test_valid_volume_max(self):
        """Test maximum valid volume (1.0)."""
        from rest_api_server import TrackVolumeRequest
        req = TrackVolumeRequest(volume=1.0)
        assert req.volume == 1.0

    def test_valid_volume_middle(self):
        """Test middle volume (0.5)."""
        from rest_api_server import TrackVolumeRequest
        req = TrackVolumeRequest(volume=0.5)
        assert req.volume == 0.5

    def test_valid_volume_near_min(self):
        """Test volume near minimum."""
        from rest_api_server import TrackVolumeRequest
        req = TrackVolumeRequest(volume=0.001)
        assert req.volume == 0.001

    def test_valid_volume_near_max(self):
        """Test volume near maximum."""
        from rest_api_server import TrackVolumeRequest
        req = TrackVolumeRequest(volume=0.999)
        assert req.volume == 0.999

    def test_invalid_volume_negative(self):
        """Test negative volume."""
        from rest_api_server import TrackVolumeRequest
        with pytest.raises(ValidationError) as exc_info:
            TrackVolumeRequest(volume=-0.1)
        assert "Volume must be between 0.0 and 1.0" in str(exc_info.value)

    def test_invalid_volume_too_high(self):
        """Test volume above 1.0."""
        from rest_api_server import TrackVolumeRequest
        with pytest.raises(ValidationError):
            TrackVolumeRequest(volume=1.1)

    def test_invalid_volume_much_too_high(self):
        """Test volume way above maximum."""
        from rest_api_server import TrackVolumeRequest
        with pytest.raises(ValidationError):
            TrackVolumeRequest(volume=100.0)


# =============================================================================
# Pan Validation
# =============================================================================

class TestPanValidation:
    """Test pan validation."""

    def test_valid_pan_left(self):
        """Test full left pan (-1.0)."""
        from rest_api_server import TrackPanRequest
        req = TrackPanRequest(pan=-1.0)
        assert req.pan == -1.0

    def test_valid_pan_right(self):
        """Test full right pan (1.0)."""
        from rest_api_server import TrackPanRequest
        req = TrackPanRequest(pan=1.0)
        assert req.pan == 1.0

    def test_valid_pan_center(self):
        """Test center pan (0.0)."""
        from rest_api_server import TrackPanRequest
        req = TrackPanRequest(pan=0.0)
        assert req.pan == 0.0

    def test_valid_pan_partial_left(self):
        """Test partial left pan."""
        from rest_api_server import TrackPanRequest
        req = TrackPanRequest(pan=-0.5)
        assert req.pan == -0.5

    def test_valid_pan_partial_right(self):
        """Test partial right pan."""
        from rest_api_server import TrackPanRequest
        req = TrackPanRequest(pan=0.5)
        assert req.pan == 0.5

    def test_invalid_pan_too_left(self):
        """Test pan too far left."""
        from rest_api_server import TrackPanRequest
        with pytest.raises(ValidationError) as exc_info:
            TrackPanRequest(pan=-1.1)
        assert "Pan must be between -1.0 and 1.0" in str(exc_info.value)

    def test_invalid_pan_too_right(self):
        """Test pan too far right."""
        from rest_api_server import TrackPanRequest
        with pytest.raises(ValidationError):
            TrackPanRequest(pan=1.1)

    def test_invalid_pan_extreme_left(self):
        """Test extreme left pan."""
        from rest_api_server import TrackPanRequest
        with pytest.raises(ValidationError):
            TrackPanRequest(pan=-100.0)

    def test_invalid_pan_extreme_right(self):
        """Test extreme right pan."""
        from rest_api_server import TrackPanRequest
        with pytest.raises(ValidationError):
            TrackPanRequest(pan=100.0)


# =============================================================================
# Master Track Volume/Pan Validation
# =============================================================================

class TestMasterVolumeValidation:
    """Test master volume validation."""

    def test_valid_master_volume_min(self):
        """Test minimum master volume."""
        from rest_api_server import MasterVolumeRequest
        req = MasterVolumeRequest(volume=0.0)
        assert req.volume == 0.0

    def test_valid_master_volume_max(self):
        """Test maximum master volume."""
        from rest_api_server import MasterVolumeRequest
        req = MasterVolumeRequest(volume=1.0)
        assert req.volume == 1.0

    def test_invalid_master_volume_negative(self):
        """Test negative master volume."""
        from rest_api_server import MasterVolumeRequest
        with pytest.raises(ValidationError):
            MasterVolumeRequest(volume=-0.1)

    def test_invalid_master_volume_over_max(self):
        """Test master volume over maximum."""
        from rest_api_server import MasterVolumeRequest
        with pytest.raises(ValidationError):
            MasterVolumeRequest(volume=1.1)


class TestMasterPanValidation:
    """Test master pan validation."""

    def test_valid_master_pan_center(self):
        """Test center master pan."""
        from rest_api_server import MasterPanRequest
        req = MasterPanRequest(pan=0.0)
        assert req.pan == 0.0

    def test_valid_master_pan_left(self):
        """Test left master pan."""
        from rest_api_server import MasterPanRequest
        req = MasterPanRequest(pan=-1.0)
        assert req.pan == -1.0

    def test_valid_master_pan_right(self):
        """Test right master pan."""
        from rest_api_server import MasterPanRequest
        req = MasterPanRequest(pan=1.0)
        assert req.pan == 1.0

    def test_invalid_master_pan(self):
        """Test invalid master pan."""
        from rest_api_server import MasterPanRequest
        with pytest.raises(ValidationError):
            MasterPanRequest(pan=1.5)


# =============================================================================
# Note Validation
# =============================================================================

class TestNoteValidation:
    """Test MIDI note validation."""

    def test_valid_note_all_fields(self):
        """Test valid MIDI note with all fields."""
        from rest_api_server import Note
        note = Note(pitch=60, start_time=0.0, duration=0.5, velocity=100)
        assert note.pitch == 60
        assert note.start_time == 0.0
        assert note.duration == 0.5
        assert note.velocity == 100

    def test_valid_note_min_pitch(self):
        """Test minimum MIDI pitch (0)."""
        from rest_api_server import Note
        note = Note(pitch=0, start_time=0.0, duration=0.5)
        assert note.pitch == 0

    def test_valid_note_max_pitch(self):
        """Test maximum MIDI pitch (127)."""
        from rest_api_server import Note
        note = Note(pitch=127, start_time=0.0, duration=0.5)
        assert note.pitch == 127

    def test_valid_note_min_velocity(self):
        """Test minimum velocity (0)."""
        from rest_api_server import Note
        note = Note(pitch=60, start_time=0.0, duration=0.5, velocity=0)
        assert note.velocity == 0

    def test_valid_note_max_velocity(self):
        """Test maximum velocity (127)."""
        from rest_api_server import Note
        note = Note(pitch=60, start_time=0.0, duration=0.5, velocity=127)
        assert note.velocity == 127

    def test_valid_note_small_duration(self):
        """Test small but valid duration."""
        from rest_api_server import Note
        note = Note(pitch=60, start_time=0.0, duration=0.001)
        assert note.duration == 0.001

    def test_valid_note_large_duration(self):
        """Test large duration."""
        from rest_api_server import Note
        note = Note(pitch=60, start_time=0.0, duration=100.0)
        assert note.duration == 100.0

    def test_valid_note_large_start_time(self):
        """Test large start time."""
        from rest_api_server import Note
        note = Note(pitch=60, start_time=1000.0, duration=0.5)
        assert note.start_time == 1000.0

    def test_invalid_pitch_too_high(self):
        """Test pitch above 127."""
        from rest_api_server import Note
        with pytest.raises(ValidationError) as exc_info:
            Note(pitch=128, start_time=0.0, duration=0.5)
        # Pydantic may use custom or default error messages
        error_str = str(exc_info.value).lower()
        assert "pitch" in error_str and ("127" in error_str or "less than" in error_str)

    def test_invalid_pitch_negative(self):
        """Test negative pitch."""
        from rest_api_server import Note
        with pytest.raises(ValidationError):
            Note(pitch=-1, start_time=0.0, duration=0.5)

    def test_invalid_velocity_too_high(self):
        """Test velocity above 127."""
        from rest_api_server import Note
        with pytest.raises(ValidationError) as exc_info:
            Note(pitch=60, start_time=0.0, duration=0.5, velocity=128)
        # Pydantic may use custom or default error messages
        error_str = str(exc_info.value).lower()
        assert "velocity" in error_str and ("127" in error_str or "less than" in error_str)

    def test_invalid_velocity_negative(self):
        """Test negative velocity."""
        from rest_api_server import Note
        with pytest.raises(ValidationError):
            Note(pitch=60, start_time=0.0, duration=0.5, velocity=-1)

    def test_invalid_duration_zero(self):
        """Test zero duration."""
        from rest_api_server import Note
        with pytest.raises(ValidationError) as exc_info:
            Note(pitch=60, start_time=0.0, duration=0.0)
        # Pydantic may use custom or default error messages
        error_str = str(exc_info.value).lower()
        assert "duration" in error_str and ("positive" in error_str or "greater than" in error_str)

    def test_invalid_duration_negative(self):
        """Test negative duration."""
        from rest_api_server import Note
        with pytest.raises(ValidationError):
            Note(pitch=60, start_time=0.0, duration=-0.5)

    def test_invalid_start_time_negative(self):
        """Test negative start time."""
        from rest_api_server import Note
        with pytest.raises(ValidationError) as exc_info:
            Note(pitch=60, start_time=-1.0, duration=0.5)
        # Pydantic may use custom or default error messages
        error_str = str(exc_info.value).lower()
        assert "start_time" in error_str and ("non-negative" in error_str or "greater than" in error_str)

    def test_default_velocity(self):
        """Test default velocity value (100)."""
        from rest_api_server import Note
        note = Note(pitch=60, start_time=0.0, duration=0.5)
        assert note.velocity == 100


# =============================================================================
# Index Validation Functions
# =============================================================================

class TestIndexValidation:
    """Test index validation functions."""

    def test_valid_track_index_zero(self):
        """Test track index 0."""
        from rest_api_server import validate_track_index
        assert validate_track_index(0) == 0

    def test_valid_track_index_middle(self):
        """Test track index in middle range."""
        from rest_api_server import validate_track_index
        assert validate_track_index(100) == 100

    def test_valid_track_index_max(self):
        """Test maximum track index."""
        from rest_api_server import validate_track_index, MAX_TRACK_INDEX
        assert validate_track_index(MAX_TRACK_INDEX) == MAX_TRACK_INDEX

    def test_invalid_track_index_negative(self):
        """Test negative track index."""
        from rest_api_server import validate_track_index
        with pytest.raises(ValueError) as exc_info:
            validate_track_index(-1)
        assert "Track index must be between" in str(exc_info.value)

    def test_invalid_track_index_too_high(self):
        """Test track index above maximum."""
        from rest_api_server import validate_track_index, MAX_TRACK_INDEX
        with pytest.raises(ValueError):
            validate_track_index(MAX_TRACK_INDEX + 1)

    def test_valid_clip_index_zero(self):
        """Test clip index 0."""
        from rest_api_server import validate_clip_index
        assert validate_clip_index(0) == 0

    def test_valid_clip_index_middle(self):
        """Test clip index in middle range."""
        from rest_api_server import validate_clip_index
        assert validate_clip_index(50) == 50

    def test_invalid_clip_index_negative(self):
        """Test negative clip index."""
        from rest_api_server import validate_clip_index
        with pytest.raises(ValueError):
            validate_clip_index(-1)

    def test_valid_scene_index_zero(self):
        """Test scene index 0."""
        from rest_api_server import validate_scene_index
        assert validate_scene_index(0) == 0

    def test_valid_scene_index_middle(self):
        """Test scene index in middle range."""
        from rest_api_server import validate_scene_index
        assert validate_scene_index(100) == 100

    def test_invalid_scene_index_negative(self):
        """Test negative scene index."""
        from rest_api_server import validate_scene_index
        with pytest.raises(ValueError):
            validate_scene_index(-1)

    def test_valid_device_index_zero(self):
        """Test device index 0."""
        from rest_api_server import validate_device_index
        assert validate_device_index(0) == 0

    def test_valid_device_index_middle(self):
        """Test device index in middle range."""
        from rest_api_server import validate_device_index
        assert validate_device_index(50) == 50

    def test_invalid_device_index_negative(self):
        """Test negative device index."""
        from rest_api_server import validate_device_index
        with pytest.raises(ValueError):
            validate_device_index(-1)


# =============================================================================
# Index Constants
# =============================================================================

class TestIndexConstants:
    """Test index constant values."""

    def test_max_track_index(self):
        """Test MAX_TRACK_INDEX constant."""
        from rest_api_server import MAX_TRACK_INDEX
        assert MAX_TRACK_INDEX == 999

    def test_max_clip_index(self):
        """Test MAX_CLIP_INDEX constant."""
        from rest_api_server import MAX_CLIP_INDEX
        assert MAX_CLIP_INDEX == 999

    def test_max_scene_index(self):
        """Test MAX_SCENE_INDEX constant."""
        from rest_api_server import MAX_SCENE_INDEX
        assert MAX_SCENE_INDEX == 999

    def test_max_device_index(self):
        """Test MAX_DEVICE_INDEX constant."""
        from rest_api_server import MAX_DEVICE_INDEX
        assert MAX_DEVICE_INDEX == 127

    def test_max_parameter_index(self):
        """Test MAX_PARAMETER_INDEX constant."""
        from rest_api_server import MAX_PARAMETER_INDEX
        assert MAX_PARAMETER_INDEX == 255

    def test_max_send_index(self):
        """Test MAX_SEND_INDEX constant."""
        from rest_api_server import MAX_SEND_INDEX
        assert MAX_SEND_INDEX == 11


# =============================================================================
# Request Model Validation
# =============================================================================

class TestRequestModels:
    """Test request model validation."""

    def test_track_create_request_default(self):
        """Test TrackCreateRequest with defaults."""
        from rest_api_server import TrackCreateRequest
        req = TrackCreateRequest()
        assert req.index == -1
        assert req.name is None

    def test_track_create_request_with_values(self):
        """Test TrackCreateRequest with values."""
        from rest_api_server import TrackCreateRequest
        req = TrackCreateRequest(index=5, name="My Track")
        assert req.index == 5
        assert req.name == "My Track"

    def test_clip_create_request_default_length(self):
        """Test ClipCreateRequest default length."""
        from rest_api_server import ClipCreateRequest
        req = ClipCreateRequest(track_index=0, clip_index=0)
        assert req.length == 4.0

    def test_clip_create_request_custom_length(self):
        """Test ClipCreateRequest custom length."""
        from rest_api_server import ClipCreateRequest
        req = ClipCreateRequest(track_index=0, clip_index=0, length=8.0)
        assert req.length == 8.0

    def test_scene_create_request_defaults(self):
        """Test SceneCreateRequest defaults."""
        from rest_api_server import SceneCreateRequest
        req = SceneCreateRequest()
        assert req.index == -1
        assert req.name is None

    def test_quantize_request_defaults(self):
        """Test QuantizeRequest defaults."""
        from rest_api_server import QuantizeRequest
        req = QuantizeRequest()
        assert req.grid == 0.25
        assert req.strength == 1.0

    def test_quantize_request_custom(self):
        """Test QuantizeRequest custom values."""
        from rest_api_server import QuantizeRequest
        req = QuantizeRequest(grid=0.5, strength=0.75)
        assert req.grid == 0.5
        assert req.strength == 0.75

    def test_drum_pattern_request_defaults(self):
        """Test DrumPatternRequest defaults."""
        from rest_api_server import DrumPatternRequest
        req = DrumPatternRequest(track_index=0, clip_index=0)
        assert req.style == "basic"
        assert req.length == 4.0

    def test_bassline_request_defaults(self):
        """Test BasslineRequest defaults."""
        from rest_api_server import BasslineRequest
        req = BasslineRequest(track_index=0, clip_index=0)
        assert req.root == 36
        assert req.scale_type == "minor"
        assert req.length == 4.0


# =============================================================================
# Clip Pitch Validation
# =============================================================================

class TestClipPitchValidation:
    """Test audio clip pitch validation."""

    def test_valid_pitch_min(self):
        """Test minimum pitch (-48)."""
        from rest_api_server import ClipPitchRequest
        req = ClipPitchRequest(pitch=-48)
        assert req.pitch == -48

    def test_valid_pitch_max(self):
        """Test maximum pitch (48)."""
        from rest_api_server import ClipPitchRequest
        req = ClipPitchRequest(pitch=48)
        assert req.pitch == 48

    def test_valid_pitch_zero(self):
        """Test zero pitch."""
        from rest_api_server import ClipPitchRequest
        req = ClipPitchRequest(pitch=0)
        assert req.pitch == 0

    def test_invalid_pitch_too_low(self):
        """Test pitch below minimum."""
        from rest_api_server import ClipPitchRequest
        with pytest.raises(ValidationError):
            ClipPitchRequest(pitch=-49)

    def test_invalid_pitch_too_high(self):
        """Test pitch above maximum."""
        from rest_api_server import ClipPitchRequest
        with pytest.raises(ValidationError):
            ClipPitchRequest(pitch=49)


# =============================================================================
# Add Notes Request Validation
# =============================================================================

class TestAddNotesRequestValidation:
    """Test AddNotesRequest validation."""

    def test_valid_single_note(self):
        """Test valid single note."""
        from rest_api_server import AddNotesRequest, Note
        req = AddNotesRequest(
            track_index=0,
            clip_index=0,
            notes=[Note(pitch=60, start_time=0.0, duration=0.5)]
        )
        assert len(req.notes) == 1

    def test_valid_multiple_notes(self):
        """Test valid multiple notes."""
        from rest_api_server import AddNotesRequest, Note
        req = AddNotesRequest(
            track_index=0,
            clip_index=0,
            notes=[
                Note(pitch=60, start_time=0.0, duration=0.5),
                Note(pitch=64, start_time=0.5, duration=0.5),
                Note(pitch=67, start_time=1.0, duration=0.5)
            ]
        )
        assert len(req.notes) == 3

    def test_empty_notes_list(self):
        """Test empty notes list."""
        from rest_api_server import AddNotesRequest
        req = AddNotesRequest(track_index=0, clip_index=0, notes=[])
        assert len(req.notes) == 0


# =============================================================================
# Clip Loop Request Validation
# =============================================================================

class TestClipLoopRequestValidation:
    """Test ClipLoopRequest validation."""

    def test_clip_loop_all_optional(self):
        """Test that all loop parameters are optional."""
        from rest_api_server import ClipLoopRequest
        req = ClipLoopRequest(track_index=0, clip_index=0)
        assert req.loop_start is None
        assert req.loop_end is None
        assert req.looping is None

    def test_clip_loop_with_values(self):
        """Test with all values set."""
        from rest_api_server import ClipLoopRequest
        req = ClipLoopRequest(
            track_index=0,
            clip_index=0,
            loop_start=0.0,
            loop_end=4.0,
            looping=True
        )
        assert req.loop_start == 0.0
        assert req.loop_end == 4.0
        assert req.looping == True
