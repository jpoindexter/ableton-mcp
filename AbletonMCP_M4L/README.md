# AbletonMCP Max for Live Device

A Max for Live device that connects Ableton Live directly to AI language models (Ollama, OpenAI, Claude API, Groq) without needing the MCP server.

## Features

- **Multi-provider support**: Works with Ollama (local, free), OpenAI, Claude API, and Groq
- **Direct integration**: No separate MCP server needed
- **Visual UI**: Text input and response display inside Ableton
- **All 80+ tools**: Full access to track, clip, scene, device, and AI music tools

## Requirements

- Ableton Live Suite (includes Max for Live) or Max for Live add-on
- Max 8.5 or newer
- Node for Max (included with Max 8)
- For local AI: [Ollama](https://ollama.ai) installed

## Installation

1. Copy the `AbletonMCP_M4L` folder to your Max for Live devices folder:
   - macOS: `~/Music/Ableton/User Library/Presets/Audio Effects/Max Audio Effect/`
   - Windows: `\Users\[Username]\Documents\Ableton\User Library\Presets\Audio Effects\Max Audio Effect\`

2. Rename `AbletonMCP.amxd.maxpat` to `AbletonMCP.amxd`

3. In Ableton Live, drag the device onto any track

## Usage

### With Ollama (Free, Local)

1. Install Ollama: https://ollama.ai

2. Pull a model with tool support:
   ```bash
   ollama pull llama3.2
   ```

3. Make sure Ollama is running:
   ```bash
   ollama serve
   ```

4. In the M4L device:
   - Provider: `ollama`
   - Model: `llama3.2`
   - API Key: (leave blank)

5. Type your prompt and click Send!

### With OpenAI

1. Get an API key from https://platform.openai.com

2. In the M4L device:
   - Provider: `openai`
   - Model: `gpt-4` or `gpt-4o`
   - API Key: `sk-...`

### With Claude API

1. Get an API key from https://console.anthropic.com

2. In the M4L device:
   - Provider: `claude`
   - Model: `claude-sonnet-4-20250514`
   - API Key: `sk-ant-...`

### With Groq (Fast, Free Tier)

1. Get an API key from https://console.groq.com

2. In the M4L device:
   - Provider: `groq`
   - Model: `llama-3.3-70b-versatile`
   - API Key: `gsk_...`

## Example Prompts

- "Create a house beat at 124 BPM"
- "Add a funky bassline in E minor"
- "Create 4 scenes: intro, verse, chorus, outro"
- "Add reverb to track 1"
- "Humanize the drum clip on track 2"
- "Generate a trap drum pattern"
- "Quantize the notes in clip 1 to 16th notes"

## Available Tools

The device has access to all 80+ AbletonMCP tools including:

- **Transport**: play, stop, tempo, undo/redo
- **Tracks**: create, delete, duplicate, mute, solo, arm
- **Clips**: create, fire, stop, duplicate, loop settings
- **Notes**: add, remove, transpose
- **Scenes**: create, fire, duplicate
- **Devices**: load, toggle, delete, parameters
- **AI Music**: drum patterns, basslines, scales, quantize, humanize

## Troubleshooting

### "Could not connect to Ollama"
- Make sure Ollama is running: `ollama serve`
- Check it's on the default port: http://localhost:11434

### "Model not found"
- Pull the model first: `ollama pull llama3.2`

### "API key invalid"
- Check your API key is correct
- Make sure you have credits/quota remaining

### Device not responding
- Check Max Console for errors (Window > Max Console)
- Try reloading the device

## Development

The device consists of:
- `AbletonMCP.amxd.maxpat` - Max patch with UI
- `code/main.js` - Node for Max script with all logic

To modify, open the .maxpat file in Max and edit the patch or JavaScript.
