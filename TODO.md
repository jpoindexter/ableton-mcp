# AbletonMCP TODO

## High Priority

### M4L Device Update Required
The Max for Live device (`AbletonMCP_M4L/code/main.js`) has **55 tools** but the Remote Script now supports **200+ commands**.

**Commands to add to M4L:**

#### Detail View (NEW)
- `get_detail_clip` - Get clip in detail view
- `set_detail_clip` - Show clip in detail
- `get_highlighted_clip_slot` - Get highlighted slot
- `select_device` - Select device for viewing
- `get_selected_device` - Get selected device

#### Audio Clip Fades (NEW)
- `get_clip_fades` - Get fade settings
- `set_clip_fade_in` - Set fade in
- `set_clip_fade_out` - Set fade out

#### Clip Time (NEW)
- `get_clip_start_time` / `set_clip_start_time`
- `get_clip_end_time` / `set_clip_end_time`

#### Automation (NEW)
- `get_session_automation_record` / `set_session_automation_record`
- `get_arrangement_overdub` / `set_arrangement_overdub`
- `re_enable_automation`

#### Drum Rack Advanced (NEW)
- `get_drum_pad_info`
- `set_drum_pad_name`

#### Simpler/Sampler (NEW)
- `get_simpler_sample_info`
- `get_simpler_parameters`

#### MIDI Editing (NEW)
- `get_notes_in_range` - Filter notes by time/pitch
- `move_clip_notes` - Shift notes
- `set_clip_notes` - Replace all notes
- `quantize_clip` - Quantize notes
- `deselect_all_notes`
- `duplicate_clip_loop`

#### Track Capabilities (NEW)
- `get_track_capabilities`
- `get_track_available_input_types`
- `get_track_available_output_types`
- `get_track_implicit_arm` / `set_track_implicit_arm`

#### Count In (NEW)
- `get_count_in_duration` / `set_count_in_duration`

#### Clip State (NEW)
- `get_clip_playing_position`
- `get_clip_has_envelopes`

#### Quick Queries (NEW)
- `get_all_track_names`
- `scrub_by`

#### Cue Control (NEW)
- `get_cue_volume` / `set_cue_volume`
- `jump_to_prev_cue`
- `jump_to_next_cue`

#### Song Properties (NEW)
- `get_groove_amount` / `set_groove_amount`
- `get_signature` / `set_signature`
- `get_exclusive_arm` / `set_exclusive_arm`
- `get_exclusive_solo` / `set_exclusive_solo`

#### Transport (NEW)
- `continue_playing`
- `tap_tempo`
- `stop_all_clips`

#### Return Track Management (NEW)
- `create_return_track`
- `delete_return_track`

#### Multi-Track Operations (NEW)
- `solo_exclusive`
- `unsolo_all`
- `unmute_all`
- `unarm_all`

#### Track State (NEW)
- `get_track_delay` / `set_track_delay`
- `get_track_is_grouped`
- `get_track_is_foldable`

#### Clip Markers (NEW)
- `get_clip_start_end_markers`
- `set_clip_start_marker`
- `set_clip_end_marker`
- `get_clip_velocity_amount` / `set_clip_velocity_amount`

#### Quantization Settings (NEW)
- `get_clip_trigger_quantization` / `set_clip_trigger_quantization`
- `get_midi_recording_quantization` / `set_midi_recording_quantization`

---

## Medium Priority

### Documentation Updates
- [ ] Update API_REFERENCE.md with all new commands
- [ ] Update TOOLS.md with MCP tool definitions

### Testing
- [ ] Add unit tests for new commands
- [ ] Test all new LOM features

---

## Low Priority

### Performance
- [ ] Connection pooling
- [ ] Request caching for GET commands

### Security
- [ ] Rate limiting on individual commands
- [ ] Command logging

---

## Completed

- [x] Add 200+ LOM commands to Remote Script
- [x] Update REST API whitelist
- [x] Create comprehensive MANUAL.md with techno tutorial
- [x] Push all changes to git
