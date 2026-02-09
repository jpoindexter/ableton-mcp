# Title: I forked AbletonMCP and expanded it from 80 to 200+ AI tools for full Ableton Live control

I forked [Siddharth Ahuja's AbletonMCP](https://github.com/ahujasid/ableton-mcp) and expanded it from about 80 tools to 200+ tools covering near complete Ableton Live Object Model control. Full credit to Siddharth for the original project and architecture. I just kept going until basically every LOM feature was mapped.

**What I added on top of the original:**

Went from about 80 to 200+ commands including automation, clip fades, drum rack control, simpler/sampler, freeze/flatten, warp markers, full MIDI editing, metering, and a lot more.

Added a REST API server with authentication, rate limiting, pagination, and OpenAI compatible tool definitions for use with any LLM.

Added a Max for Live device so you can chat with AI directly inside Ableton's device view.

Added AI music helpers including drum pattern generation (8 styles), bassline generation (6 styles), and scale reference.

Wrote a comprehensive manual with a start to finish techno track tutorial.

**Three ways to use it:**

1. Claude Desktop or Cursor via MCP where Claude directly controls Ableton
2. REST API that works with Ollama (free and local), OpenAI, Groq, or any LLM with tool calling
3. Max for Live device with a chat UI inside Ableton, no external apps needed

**Fair warning, there are bugs.** This has been a rapid build and I have not had time to thoroughly test every one of the 200+ commands. The M4L device in particular still has issues and needs work. Some commands might not work as expected depending on your Ableton version or session state. The core stuff like transport, tracks, clips, notes, devices, and scenes is solid but some of the newer additions like automation envelopes, simpler parameters, and some edge cases might need work.

**Contributions welcome.** If you are into Ableton and Python and want to help fix bugs, add tests, or expand coverage, PRs are very welcome. The Remote Script is straightforward Python using Ableton's LOM API. Even just reporting issues when you find commands that don't work right would be super helpful.

**Example prompts:**

"Create a raw hypnotic techno track at 135 BPM with kick, hats, bass, and acid lead"

"Quantize the bass clip to 16th notes and humanize the velocity"

"Create intro, verse, chorus, and outro scenes"

"Freeze track 3 and flatten it"

GitHub: https://github.com/jpoindexter/ableton-mcp

Original project: https://github.com/ahujasid/ableton-mcp

Would love feedback and help making this more solid.
