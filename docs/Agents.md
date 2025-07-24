## Codex Agent Guide: Thunder Hockey Assistant Dev Standards

Welcome to the **Codex Agent workspace** for the Thunder Hockey AI Assistant. This guide sets repo-wide standards for agent development, integration, and testing.

---

## 📂 Repo Structure

| Folder              | Purpose                                                          |
| ------------------- | ---------------------------------------------------------------- |
| `app/client/agent/` | All Codex Agent definitions (e.g., summarizer, planner)          |
| `app/client/`       | Agent runners and interface logic                                |
| `app/mcp_server/`   | MCP Server + tool integration                                    |
| `prompts/`          | Prompt templates (YAML) for agent behaviors                      |
| `scripts/`          | CLI runners, test harnesses, indexers                            |
| `data/processed/`   | Structured, clean data (e.g., `drills.json`, `video_clips.json`) |
| `data/raw/`         | Unstructured/raw input scraped from the web                      |

---

## ✅ Dev Standards

### 🔧 Use SDKs & Libraries

* Always prefer well-supported SDKs over reinventing (e.g., `yt-dlp`, `whisper`, `openai`, `chromadb`, `pydantic`)
* Avoid hardcoding API logic if supported through a maintained library

### ⚖️ Prompt + Agent Design

* Follow patterns in `summarizer_agent.py`
* Prompt files must be in `prompts/` and referenced dynamically
* Use `Agent(...)` constructor with clear `name`, `instructions`, and `output_type`
* Keep prompt YAML simple and declarative

### ✍️ Input/Output Schema

* Use `pydantic.BaseModel` for all input/output models
* Output JSON should be aligned with user-facing entities: drills, clips, summaries, etc.

### ⚡ CLI Compatibility

* All scripts should include `argparse` CLI entry points
* Include minimal console prints to visualize progress
* Validate `.env` or config dependencies at start

### ✅ Testing

* Test agents with real or mock inputs
* Include sample outputs in CLI script logs
* Use `print("✅ [Step Description]")` for debug checkpoints

### ⚠️ Integration Expectations

* Any output data must:

  * Match the `drills.json` or `video_clips.json` schema
  * Be embeddable in Chroma using `chroma_utils.py`
* Embed metadata fields as flat strings (e.g., `;`-joined lists)
* Always clean and validate before writing to disk

---

## 📄 Example Main File Requirements

```python
# main.py header for agent or script
# Requirements:
# - yt-dlp installed
# - whisper + ffmpeg
# - video URL via --url flag
# Usage:
#   python scripts/process_video_transcripts.py --url https://youtube.com/watch?v=xyz123
```

---

## 🔗 Integration Goals

* Video knowledge must be searchable just like drills
* Visual generation prompts should be attached to transcript chunks
* System must scale from one clip to hundreds (add batching if needed)

---

## 🔄 Feedback & Review

* Codex Agents should leave inline comments when unsure
* All PRs reviewed before indexing or deployment
* Use tracing if working across multiple agents

---

## 🔗 Reference SDKs

* Agents SDK: [https://github.com/openai/openai-agents-python](https://github.com/openai/openai-agents-python)
* Whisper: [https://github.com/openai/whisper](https://github.com/openai/whisper)
* yt-dlp: [https://github.com/yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp)
* ChromaDB: [https://docs.trychroma.com/](https://docs.trychroma.com/)

Let's build the best AI-powered hockey assistant for coaches and kids — together.
