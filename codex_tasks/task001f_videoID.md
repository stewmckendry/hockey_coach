# Codex Agent Task: Add Video ID & Segment ID to Support Duplicate Detection

## 🏋️ Overview

You're updating the `process_video_transcripts.py` script to add more stable identifiers to each segment so that duplicate videos are correctly skipped during re-runs, and segments can be uniquely addressed later.

---

## 📄 Task Scope

### ✅ Add `video_id` to Each Clip

* Use `info['id']` returned from `yt_dlp.extract_info(...)`
* Add this as a new field in each `clip` dictionary:

```python
"video_id": info.get("id", "unknown")
```

### ✅ Add `segment_id` for Uniqueness

* Create a stable ID for each segment, combining video ID and segment number:

```python
"segment_id": f"{video_id}_{idx+1:03d}"
```

* This can later be used for:

  * Exact segment lookup
  * Re-indexing safety
  * UI deep links or sorting

### ✅ Use `video_id` for Processed Skipping

* When checking existing clips (in combined output mode):

  * Instead of calling `parse_video_id(clip['video_url'])`, use the new `clip['video_id']`
  * Update the logic to build `processed_ids` set from `clip['video_id']`

This avoids issues where `video_url` includes a timestamp (`?t=95`) that breaks ID parsing.

### 🧼 Normalize `position`

* Standardize `position` field across clips:

  * Convert `null` to empty list `[]`
  * If the clip applies broadly, use `"Any"` or `"All"`
  * This ensures predictable filtering in downstream agents or UIs

### 📏 Ensure `segment_number` Consistency

* Check that `segment_number` increments properly and matches the order of `start_time`
* This ensures playback or UI ordering matches transcript progression

---

## 🎓 Guidelines & Standards

* If `info.get("id")` is not available, fallback to parsing manually or tagging `"unknown"`
* Prefer storing `video_id` explicitly on disk rather than re-parsing from `video_url`
* Normalize fields like `position` to consistent list formats
* IDs should be stable across runs and consistent regardless of sort order

---

## 📄 Files to Update

* `scripts/process_video_transcripts.py`

---

## ✏️ Test CLI

```bash
python scripts/process_video_transcripts.py \
  --url-file data/input/channel_videos.txt \
  --output data/processed/video_clips.json
```

Re-running the above twice should skip already-processed videos, using `video_id` detection.

---

## 📃 Deliverables

* Each clip includes new `video_id` and `segment_id`
* Skipping logic uses `video_id` for deduplication
* No false negatives or duplicate videos processed in reruns
* Position field is consistently formatted across all clips
* Segment numbering matches the actual video order and time codes

---

## 🌟 Bonus

* Index `segment_id` in Chroma for traceable retrieval
* Add CLI flag `--force` to override skip logic and reprocess all
