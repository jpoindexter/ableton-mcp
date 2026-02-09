# Contributing to AbletonMCP

Thank you for your interest in contributing to AbletonMCP! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites

- Python 3.10+
- Ableton Live 10+ (Suite or with Max for Live for M4L development)
- [uv](https://astral.sh/uv) package manager
- Git

### Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ableton-mcp.git
   cd ableton-mcp
   ```

3. Install dependencies:
   ```bash
   # For MCP server development
   pip install -e ".[all]"

   # Or with uv
   uv pip install -e ".[all]"
   ```

4. Install the Remote Script in Ableton (see README.md)

## Project Structure

```
ableton-mcp/
├── AbletonMCP_Remote_Script/    # Ableton Remote Script (runs inside Ableton)
│   └── __init__.py              # Main script with all command handlers
├── MCP_Server/                  # Server components
│   ├── server.py                # MCP server for Claude
│   └── rest_api_server.py       # REST API for Ollama/OpenAI
├── AbletonMCP_M4L/              # Max for Live device
│   ├── AbletonMCP.amxd.maxpat   # Max patch
│   └── code/main.js             # Node for Max script
├── examples/                    # Usage examples
└── docs/                        # Documentation
```

## How to Contribute

### Reporting Bugs

1. Check existing issues first
2. Create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Ableton version, OS, Python version
   - Relevant logs (Ableton Log.txt, server output)

### Suggesting Features

1. Open an issue with `[Feature Request]` prefix
2. Describe the feature and use case
3. Explain why it would be useful
4. If possible, suggest implementation approach

### Submitting Code

1. Create a branch for your feature/fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the coding standards below

3. Test your changes:
   - Test with Ableton Live
   - Test MCP tools via Claude
   - Test REST API if applicable

4. Commit with clear messages:
   ```bash
   git commit -m "Add feature: description of what it does"
   ```

5. Push and create a Pull Request

### Pull Request Guidelines

- Clear title and description
- Reference related issues
- Include test results
- Update documentation if needed
- Keep changes focused (one feature/fix per PR)

## Coding Standards

### Python (Server & Remote Script)

- Follow PEP 8 style guide
- Use type hints where practical
- Document functions with docstrings
- Handle errors gracefully

```python
def my_function(param: str) -> dict:
    """
    Brief description of what the function does.

    Args:
        param: Description of parameter

    Returns:
        Description of return value
    """
    try:
        # Implementation
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

### JavaScript (Max for Live)

- Use ES6+ features
- Document with JSDoc comments
- Handle async operations properly

```javascript
/**
 * Description of function
 * @param {string} param - Description
 * @returns {Promise<Object>} Description
 */
async function myFunction(param) {
    try {
        // Implementation
    } catch (error) {
        Max.post(`Error: ${error.message}`);
    }
}
```

### Adding New Commands

1. **Remote Script** (`AbletonMCP_Remote_Script/__init__.py`):
   - Add a `_your_command_name()` handler method
   - Add routing in `_process_command()`:
     - Read only commands go in the first `if/elif` section
     - State changing commands go in the `schedule_message` section for main thread safety
   - Copy updated file to Ableton's MIDI Remote Scripts folder to test

2. **REST API** (`MCP_Server/rest_api_server.py`):
   - Add to `ALLOWED_COMMANDS` set
   - Add a REST endpoint with proper HTTP method
   - Create Pydantic model for request body if needed
   - Add parameter validation to `COMMAND_PARAMS`

3. **MCP Server** (`MCP_Server/server.py`):
   - Add `@mcp.tool()` decorated function
   - Document parameters and return value

4. **M4L Device** (`AbletonMCP_M4L/code/main.js`):
   - Add tool definition to the `TOOLS` array

### Tool Naming Conventions

- Use snake_case: `get_track_info`, `set_clip_name`
- Start with verb: `get_`, `set_`, `create_`, `delete_`, `fire_`, `toggle_`
- Be specific: `get_clip_notes` not `get_notes`

## Testing

### Manual Testing

1. Start Ableton with Remote Script loaded
2. Test via Claude Desktop or REST API
3. Verify tool executes correctly
4. Check for edge cases (invalid indices, etc.)

### Test Checklist

- [ ] Tool executes without errors
- [ ] Return value is correct
- [ ] Error cases handled gracefully
- [ ] Works with various Ableton setups
- [ ] Documentation is accurate

## Questions?

- Open an issue for questions
- Check existing issues and discussions
- Review the README and documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
