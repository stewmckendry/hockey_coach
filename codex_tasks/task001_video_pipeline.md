# Codex Agent Task: Build YouTube Video Processing Pipeline for Hockey Assistant

**STATUS:** 🟢 Completed

## 🏋️ Overview

You are contributing to a multi-agent AI assistant for hockey coaches, players, and parents. The system already includes a curated database of 1125 structured drills and a full AI agent stack built using the OpenAI Agents SDK and Model Context Protocol (MCP).

Your task is to extend this system with a new pipeline that ingests YouTube videos from hockey instructors, extracts knowledge, and stores it in a structured, searchable format.

---

## ⚖️ What to Build

Create a new pipeline that:

1. **Ingests YouTube videos**

   * Uses `yt-dlp` to download videos or audio

2. **Transcribes audio**

   * Uses OpenAI Whisper to transcribe audio
   * Segment transcript into logical teaching points

3. **Summarizes each segment**

   * Use existing LLM summarizer patterns (see `summarizer_agent.py`)

4. **Extracts structured metadata (using GPT/LLM calls)**

   * Skill tags (e.g., Skating, Shooting, Angling)
   * Teaching points (e.g., "knees bent", "weight transfer")
   * Visual prompts (for diagram or image generation later)

5. **Outputs structured data** in a format similar to `drills.json`

   * Create `video_clips.json`

6. **Indexes into Chroma**

   * Use `chroma_utils.py` and match embedding/indexing strategy from `index_drills_chroma.py`

---

## 🔍 Reference Files

* `app/client/agent/summarizer_agent.py` — baseline for building `video_summarizer_agent.py`
* `prompts/summarizer_prompt.yaml` — adapt this for video-specific version
* `scripts/index_drills_chroma.py` — reuse format, structure, metadata logic
* `data/processed/drills.json` — match schema when creating `video_clips.json`

---

## 🎓 Guidelines & Standards

### ⚖️ General

* Always prefer standard libraries and SDKs (e.g., `yt-dlp`, `whisper`, `openai`, `pydantic`, `chromadb`)
* Modular, readable, testable code
* Include CLI entry point (e.g. via argparse)
* Use async if possible (to match drill planner architecture)

### ✅ Testing

* Include test input and console output
* Add printouts for intermediate steps (transcript chunking, tagging, summary)
* Do not require end-to-end system to be running (isolate new pipeline)

### 🔗 Integration

* Structure `video_clips.json` to match `drills.json`
* Use same `get_chroma_collection()` method
* Reuse LLM interface patterns from `agents/`

---

## 🚀 Deliverables

1. `scripts/process_video_transcripts.py` — end-to-end script to process 1+ YouTube videos
2. `app/client/agent/video_summarizer_agent.py`
3. `prompts/video_summarizer_prompt.yaml`
4. `scripts/index_video_clips_chroma.py`
5. `data/processed/video_clips.json` (initial placeholder or real sample)

---

## 🚀 Optional Next Steps (Leave Hooks For)

* Visual generation using OpenAI image APIs or Sora
* UI hook to render video + transcript + tags
* RAG-based retrieval from drills + videos combined

---

## ✏️ Example Input

```
python scripts/process_video_transcripts.py --url https://www.youtube.com/watch?v=abc123
```

## 📚 Example Output JSON

```json
{
  "title": "Backward Crossovers: Balance and Edges",
  "video_url": "https://www.youtube.com/watch?v=abc123&t=95s",
  "source": "HowToHockey",
  "summary": "Teaches how to use outside edge and stay low during backward crossovers",
  "teaching_points": [
    "Knees bent and weight forward",
    "Push from outside edge of lead foot"
  ],
  "visual_prompt": "Side view of hockey player doing backward crossover, bent knees, chest up",
  "hockey_skills": ["Skating", "Crossovers"],
  "position": ["Defence"],
  "complexity": "Intermediate"
}
```
