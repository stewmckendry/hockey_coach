# Codex Agent Task: Improve Chroma Indexing and Cleanup Logic for Video Clips

## 🏋️ Overview

You're improving the `index_video_clips_chroma.py`, `process_video_transcripts.py`, and `chroma_utils.py` files to ensure video knowledge is accurately and cleanly indexed without disrupting other data (like drills).

---

## 📄 Task Scope

### ✅ 1. **Extend Metadata Fields for Video Clips**

Update `index_video_clips_chroma.py` to include all new fields from `video_clips.json`:

* `segment_number`
* `start_time`
* `end_time`
* `duration`
* `clip_type`
* `intended_audience`
* `play_or_skill_focus`

Ensure these fields are added to both:

* the `metadata_for()` function
* (optional) the `clip_text()` summary string for search quality

---

### ♻️ 2. **Improve Wipe Logic in `chroma_utils.py`**

Extend the `clear_chroma_collection()` function to support the following modes:

#### Mode A: Wipe everything

```python
clear_chroma_collection(mode="all")
```

* Default behavior
* Same as current logic

#### Mode B: Wipe by prefix/type (e.g., all `video-` docs)

```python
clear_chroma_collection(mode="type", prefix="video-")
```

* Deletes all documents with ID that starts with a prefix

#### Mode C: Wipe by explicit ID(s)

```python
clear_chroma_collection(mode="ids", ids=["video-3", "drill-10"])
```

* Deletes only specified documents

---

### 🔍 3. **Add Transcript Text to Indexing**

Update `index_video_clips_chroma.py` to include the full transcript segment text in the Chroma index. Specifically:

* If the `transcript` field exists in the JSON clip, append it to the `clip_text()` for embedding.
* Also consider adding it to the metadata payload (truncated to \~500 chars) to support downstream UI or grounding.

Update `scripts/process_video_transcripts.py` to ensure that each summarized clip includes:

```python
"transcript": chunks[i]  # the raw transcript segment passed into the summarizer
```

Benefits:

* Enables better recall from semantic phrasing in original video
* Supports showing source quote during answer generation
* Useful for context injection in RAG or agent flows

---

## 🎓 Guidelines & Standards

* Use logging to indicate what was deleted and how many entries matched
* Avoid deleting anything if `mode="ids"` and no list is passed
* Maintain backwards compatibility by defaulting to full wipe if `mode` is not provided
* For transcript: ensure no more than 4000 tokens embedded; truncate if needed

---

## 📄 Files to Update

* `scripts/process_video_transcripts.py`
* `scripts/index_video_clips_chroma.py`
* `app/mcp_server/chroma_utils.py`

---

## ✏️ Test CLI

```bash
# Index
python scripts/index_video_clips_chroma.py

# Clear video clips only
from app.mcp_server.chroma_utils import clear_chroma_collection
clear_chroma_collection(mode="type", prefix="video-")
```

---

## 📃 Deliverables

* Updated script that adds rich metadata for video segments
* Safer `clear_chroma_collection()` with mode support
* Full transcript embedded into search index
* Debug prints showing what was indexed and/or wiped

---

## 🌟 Bonus

* Consider updating drill indexing script to support similar `clear_by_type()` behavior
* Use segment title + timestamp as unique ID if you want to support versioning later
