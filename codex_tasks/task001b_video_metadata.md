# Codex Agent Task: Enhance Video Clip Structuring for Downstream Learning

**STATUS:** 🟢 Completed

## 🏋️ Overview

You're improving the pipeline that processes YouTube hockey instruction videos into structured segments with summaries and tags. The goal is to make these outputs more useful and actionable for downstream users — hockey coaches, parents, and players.

---

## 📝 Task Scope

Update the video transcript processing pipeline to:

### ✅ 1. **Add Timestamp Metadata**

* For each segment, include:

  * `start_time`: start of the segment in seconds (float)
  * `end_time`: end of the segment in seconds (float)
  * `video_url`: direct jump link to segment (e.g., `https://youtu.be/l9cN8j6au2U?t=95`)

### 📃 2. **Add Segment Indexing Info**

* Add a `segment_number` (1-based index) so the AI assistant or UI can reference them like: "This is segment 3 of 9."

### 🧠 3. **Add Contextual Metadata (Optional Enhancements)**

* Add optional `clip_type` field: e.g., "Drill Explanation", "Demonstration", "Warm-Up"
* Add `intended_audience` field: e.g., "Beginner Coach", "U9 Player", "Parent Helper"
* Add `play_or_skill_focus`: e.g., "Breakout Support", "Backward Crossover"

### ⚡ 4. **Format Update**

Each item in `video_clips.json` should now look like:

```json
{
  "segment_number": 3,
  "title": "FLA Panthers SKILLS Coach Drills 🔥",
  "video_url": "https://youtu.be/l9cN8j6au2U?t=95",
  "source": "Hockey Training",
  "start_time": 95.3,
  "end_time": 112.6,
  "summary": "...",
  "teaching_points": ["..."],
  "visual_prompt": "...",
  "hockey_skills": ["..."],
  "position": ["..."],
  "complexity": "Intermediate",
  "clip_type": "Drill Explanation",
  "intended_audience": "U11 Coach",
  "play_or_skill_focus": "Puck Protection"
}
```

---

## 🎓 Guidelines & Standards

* Use Whisper timestamps (`start`, `end`) from the transcript segments
* Compute and inject YouTube `?t=` links based on `start_time`
* Maintain all existing logic for summarization and grouping
* Extend the clip JSON schema as shown
* Default optional fields to `null` or infer simple values from LLM if available

---

## 📄 Code to Update

* `scripts/process_video_transcripts.py` (both `group_segments` and output generation)
* `video_summarizer_agent.py` output model (optional: include extra fields)

---

## ✏️ Suggested CLI Test

```bash
python scripts/process_video_transcripts.py \
  --url https://youtu.be/l9cN8j6au2U \
  --output data/processed/video_clips.json
```

Expected result: each segment includes full metadata, video jump link, and is clearly labeled for use in teaching workflows.

---

## 🌟 Bonus (Optional)

* Add `duration` (in seconds)
* Add top keyword tags from the transcript text (e.g. via TF-IDF or OpenAI embeddings)
* Export to `.csv` for coaches who prefer spreadsheets
