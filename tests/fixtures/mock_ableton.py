# mock_ableton.py - Mock Ableton Live objects for testing
"""
Mock objects that simulate Ableton Live's object model for unit testing.
These mocks allow testing the Remote Script without requiring Ableton Live.
"""


class MockMixerDevice:
    """Mock for Ableton's MixerDevice."""

    def __init__(self):
        self._volume = MockDeviceParameter("Volume", 0.85, 0.0, 1.0)
        self._panning = MockDeviceParameter("Pan", 0.0, -1.0, 1.0)
        self._sends = []

    @property
    def volume(self):
        return self._volume

    @property
    def panning(self):
        return self._panning

    @property
    def sends(self):
        return self._sends


class MockDeviceParameter:
    """Mock for Ableton's DeviceParameter."""

    def __init__(self, name, value, min_val, max_val):
        self.name = name
        self._value = value
        self.min = min_val
        self.max = max_val

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = max(self.min, min(self.max, v))


class MockDevice:
    """Mock for Ableton's Device."""

    def __init__(self, name="Test Device", class_name="PluginDevice"):
        self.name = name
        self.class_name = class_name
        self._is_active = True
        self.parameters = [
            MockDeviceParameter("Device On", 1.0, 0.0, 1.0),
            MockDeviceParameter("Dry/Wet", 1.0, 0.0, 1.0),
        ]

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, v):
        self._is_active = v


class MockClipSlot:
    """Mock for Ableton's ClipSlot."""

    def __init__(self, has_clip=False):
        self._has_clip = has_clip
        self._clip = MockClip() if has_clip else None

    @property
    def has_clip(self):
        return self._has_clip

    @property
    def clip(self):
        return self._clip

    def create_clip(self, length):
        self._clip = MockClip(length=length)
        self._has_clip = True
        return self._clip

    def delete_clip(self):
        self._clip = None
        self._has_clip = False


class MockClip:
    """Mock for Ableton's Clip."""

    def __init__(self, name="Test Clip", length=4.0, is_midi=True):
        self.name = name
        self.length = length
        self._is_playing = False
        self._is_recording = False
        self.looping = True
        self.loop_start = 0.0
        self.loop_end = length
        self.color_index = 0
        self.is_midi_clip = is_midi
        self.is_audio_clip = not is_midi
        self._notes = []

        # Audio clip properties
        if not is_midi:
            self.gain = 1.0
            self.pitch_coarse = 0
            self.pitch_fine = 0
            self.warping = True
            self.warp_mode = 0
            self.warp_markers = []

    @property
    def is_playing(self):
        return self._is_playing

    @property
    def is_recording(self):
        return self._is_recording

    def fire(self):
        self._is_playing = True

    def stop(self):
        self._is_playing = False

    def get_notes(self, start_time, start_pitch, time_span, pitch_span):
        return self._notes

    def set_notes(self, notes):
        self._notes = notes

    def remove_notes(self, start_time, start_pitch, time_span, pitch_span):
        self._notes = []


class MockTrack:
    """Mock for Ableton's Track."""

    def __init__(self, name="Test Track", is_midi=True):
        self.name = name
        self.has_midi_input = is_midi
        self.has_audio_input = not is_midi
        self._mute = False
        self._solo = False
        self._arm = False
        self.color_index = 0
        self.mixer_device = MockMixerDevice()
        self.devices = []
        self.clip_slots = [MockClipSlot() for _ in range(8)]
        self.is_frozen = False

    @property
    def mute(self):
        return self._mute

    @mute.setter
    def mute(self, v):
        self._mute = v

    @property
    def solo(self):
        return self._solo

    @solo.setter
    def solo(self, v):
        self._solo = v

    @property
    def arm(self):
        return self._arm

    @arm.setter
    def arm(self, v):
        self._arm = v

    def freeze(self):
        self.is_frozen = True

    def flatten(self):
        if self.is_frozen:
            self.is_frozen = False


class MockScene:
    """Mock for Ableton's Scene."""

    def __init__(self, name="Scene 1"):
        self.name = name
        self.color_index = 0

    def fire(self):
        pass


class MockSong:
    """Mock for Ableton's Song."""

    def __init__(self):
        self._tempo = 120.0
        self._is_playing = False
        self.signature_numerator = 4
        self.signature_denominator = 4
        self.tracks = [MockTrack(f"Track {i}") for i in range(8)]
        self.scenes = [MockScene(f"Scene {i}") for i in range(8)]
        self.return_tracks = []
        self.master_track = MockTrack("Master")

    @property
    def tempo(self):
        return self._tempo

    @tempo.setter
    def tempo(self, v):
        self._tempo = max(20.0, min(300.0, v))

    @property
    def is_playing(self):
        return self._is_playing

    def start_playing(self):
        self._is_playing = True

    def stop_playing(self):
        self._is_playing = False

    def create_midi_track(self, index=-1):
        track = MockTrack(f"MIDI Track {len(self.tracks)}")
        if index == -1:
            self.tracks.append(track)
        else:
            self.tracks.insert(index, track)
        return track

    def create_audio_track(self, index=-1):
        track = MockTrack(f"Audio Track {len(self.tracks)}", is_midi=False)
        if index == -1:
            self.tracks.append(track)
        else:
            self.tracks.insert(index, track)
        return track

    def delete_track(self, index):
        if 0 <= index < len(self.tracks):
            del self.tracks[index]

    def duplicate_track(self, index):
        if 0 <= index < len(self.tracks):
            original = self.tracks[index]
            new_track = MockTrack(f"{original.name} Copy")
            self.tracks.insert(index + 1, new_track)
            return new_track

    def create_scene(self, index=-1):
        scene = MockScene(f"Scene {len(self.scenes)}")
        if index == -1:
            self.scenes.append(scene)
        else:
            self.scenes.insert(index, scene)
        return scene

    def delete_scene(self, index):
        if 0 <= index < len(self.scenes):
            del self.scenes[index]

    def undo(self):
        pass

    def redo(self):
        pass
