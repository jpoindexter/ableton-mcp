#!/usr/bin/env python3
"""
AbletonMCP + Ollama Integration Example

This script shows how to use Ollama with AbletonMCP via the REST API.
It creates an interactive chat that can control Ableton Live.

Requirements:
1. Ollama installed and running (ollama serve)
2. A model with tool support: ollama pull llama3.2
3. AbletonMCP REST API running: python MCP_Server/rest_api_server.py
4. Ableton Live with Remote Script loaded

Usage:
    python examples/ollama_example.py
"""

import requests
import json

OLLAMA_URL = "http://localhost:11434/api/chat"
ABLETON_API_URL = "http://localhost:8000/api/command"

# Tool definition for Ollama
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "ableton_command",
            "description": """Execute a command in Ableton Live.

Available commands and their parameters:

TRANSPORT:
- get_session_info: Get session state (no params)
- set_tempo: Set BPM (params: tempo)
- start_playback: Start playing (no params)
- stop_playback: Stop playing (no params)
- undo: Undo last action (no params)
- redo: Redo action (no params)

TRACKS:
- create_midi_track: Create MIDI track (params: index, name)
- create_audio_track: Create audio track (params: index, name)
- delete_track: Delete track (params: track_index)
- duplicate_track: Duplicate track (params: track_index)
- set_track_name: Rename track (params: track_index, name)
- set_track_mute: Mute track (params: track_index, mute)
- set_track_solo: Solo track (params: track_index, solo)
- set_track_arm: Arm track (params: track_index, arm)

CLIPS:
- create_clip: Create MIDI clip (params: track_index, clip_index, length, name)
- delete_clip: Delete clip (params: track_index, clip_index)
- fire_clip: Play clip (params: track_index, clip_index)
- stop_clip: Stop clip (params: track_index, clip_index)

NOTES:
- add_notes_to_clip: Add notes (params: track_index, clip_index, notes[{pitch, start_time, duration, velocity}])
- remove_all_notes: Clear notes (params: track_index, clip_index)
- transpose_notes: Transpose (params: track_index, clip_index, semitones)

SCENES:
- get_all_scenes: List scenes (no params)
- create_scene: Create scene (params: index, name)
- delete_scene: Delete scene (params: scene_index)
- fire_scene: Play scene (params: scene_index)
- duplicate_scene: Duplicate scene (params: scene_index)

DEVICES:
- get_device_parameters: Get params (params: track_index, device_index)
- set_device_parameter: Set param (params: track_index, device_index, parameter_index, value)
- toggle_device: Enable/disable (params: track_index, device_index, enabled)
- delete_device: Remove device (params: track_index, device_index)

AI MUSIC:
- get_scale_notes: Get scale notes (params: root, scale_type, octave)
- generate_drum_pattern: Create drums (params: style[basic/house/techno/hip_hop/trap/dnb/jazz/funk], bars, swing)
- generate_bassline: Create bass (params: root, scale, style[basic/walking/synth/funk/octave/arpeggiated], bars, octave)
- quantize_clip_notes: Quantize (params: track_index, clip_index, grid_size, strength)
- humanize_clip_timing: Humanize timing (params: track_index, clip_index, amount)
- humanize_clip_velocity: Humanize velocity (params: track_index, clip_index, amount)
""",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The Ableton command to execute"
                    },
                    "params": {
                        "type": "object",
                        "description": "Parameters for the command (varies by command)"
                    }
                },
                "required": ["command"]
            }
        }
    }
]

SYSTEM_PROMPT = """You are an AI music production assistant with direct control of Ableton Live.

You can create beats, melodies, and full tracks using the ableton_command tool.
When the user asks you to do something musical:
1. Use the appropriate command(s)
2. Explain what you did
3. Suggest next steps

Be creative! You can:
- Create drum patterns (use generate_drum_pattern)
- Create basslines (use generate_bassline)
- Set up tracks and clips
- Control playback
- Mix and arrange

Always use the tool to actually make changes in Ableton."""


def call_ollama(messages: list, model: str = "llama3.2") -> dict:
    """Call Ollama API with tools"""
    response = requests.post(OLLAMA_URL, json={
        "model": model,
        "messages": messages,
        "tools": TOOLS,
        "stream": False
    })
    return response.json()


def execute_ableton_command(command: str, params: dict = None) -> dict:
    """Execute a command via the REST API"""
    try:
        response = requests.post(ABLETON_API_URL, json={
            "command": command,
            "params": params or {}
        })
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to Ableton REST API. Make sure rest_api_server.py is running."}


def process_tool_calls(response: dict) -> list:
    """Process tool calls from Ollama response"""
    results = []

    if "message" in response and "tool_calls" in response["message"]:
        for tool_call in response["message"]["tool_calls"]:
            if tool_call["function"]["name"] == "ableton_command":
                args = tool_call["function"]["arguments"]
                command = args.get("command")
                params = args.get("params", {})

                print(f"\n  [Executing: {command}]")
                result = execute_ableton_command(command, params)
                print(f"  [Result: {json.dumps(result, indent=2)[:200]}...]")

                results.append({
                    "command": command,
                    "result": result
                })

    return results


def chat(user_message: str, history: list, model: str = "llama3.2") -> tuple:
    """Send a message and get a response"""

    # Add user message to history
    history.append({"role": "user", "content": user_message})

    # Build messages with system prompt
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

    # Call Ollama
    response = call_ollama(messages, model)

    # Process any tool calls
    tool_results = process_tool_calls(response)

    # Get the text response
    assistant_message = response.get("message", {}).get("content", "")

    # If there were tool calls but no text, summarize the results
    if tool_results and not assistant_message:
        assistant_message = "Executed commands:\n" + "\n".join(
            f"- {r['command']}: {'success' if 'error' not in r['result'] else r['result']['error']}"
            for r in tool_results
        )

    # Add assistant response to history
    history.append({"role": "assistant", "content": assistant_message})

    return assistant_message, history


def main():
    print("=" * 60)
    print("AbletonMCP + Ollama Chat")
    print("=" * 60)
    print("Control Ableton Live with natural language!")
    print("Type 'quit' to exit, 'clear' to reset conversation")
    print("")
    print("Examples:")
    print('  - "Create a house beat at 124 BPM"')
    print('  - "Add a funky bassline in E minor"')
    print('  - "Set the tempo to 90"')
    print('  - "Fire scene 1"')
    print("=" * 60)

    # Check connections
    print("\nChecking connections...")

    try:
        health = requests.get("http://localhost:8000/health").json()
        if health.get("status") == "connected":
            print("  [OK] REST API connected to Ableton")
        else:
            print("  [!] REST API running but not connected to Ableton")
            print("      Make sure Ableton is open with the Remote Script loaded")
    except:
        print("  [X] REST API not running!")
        print("      Start it with: python MCP_Server/rest_api_server.py")
        return

    try:
        requests.post(OLLAMA_URL, json={"model": "llama3.2", "messages": [], "stream": False}, timeout=5)
        print("  [OK] Ollama is running")
    except:
        print("  [X] Ollama not running!")
        print("      Start it with: ollama serve")
        print("      Then pull a model: ollama pull llama3.2")
        return

    print("\nReady! Start chatting.\n")

    history = []

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() == 'quit':
                print("Goodbye!")
                break

            if user_input.lower() == 'clear':
                history = []
                print("Conversation cleared.\n")
                continue

            print("\nThinking...")
            response, history = chat(user_input, history)
            print(f"\nAssistant: {response}\n")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()
