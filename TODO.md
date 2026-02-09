# AbletonMCP TODO

## Completed

- [x] Add 200+ LOM commands to Remote Script
- [x] Update REST API whitelist with all commands
- [x] Create comprehensive MANUAL.md with techno tutorial
- [x] Update M4L device with 200+ tools
- [x] Fix M4L device binary format (AMPF container)
- [x] Fix M4L dropdown and compact layout
- [x] Add freeze_track, flatten_track, unarm_all, move_device_left/right
- [x] Add pagination to list endpoints (scenes, tracks, device params)
- [x] Add MCP tools for missing commands
- [x] Fix unbounded Queue (maxsize=10)
- [x] Push all changes to git

## Medium Priority

### Testing
- [ ] Test M4L device with Ollama end-to-end
- [ ] Test M4L device with OpenAI/Claude/Groq
- [ ] Add unit tests for new commands

### Documentation
- [ ] Update README with latest feature count
- [ ] Add screenshots of M4L device

## Low Priority

### Performance
- [ ] Connection pooling
- [ ] Request caching for GET commands

### Future Ideas
- [ ] MIDI Effect version of M4L device (no audio passthrough needed)
- [ ] WebSocket support for real-time updates
- [ ] Preset browser integration
