# Codex Agent Task: Multi-Video Processing Support for YouTube Pipeline

**STATUS:** 🟢 Completed

## 🏋️ Overview

You're updating the `scripts/process_video_transcripts.py` and `scripts/index_video_clips_chroma.py` scripts to enable batch processing and indexing of multiple YouTube videos.

---

## 📄 Task Scope

### ✅ Multi-Video Pipeline Support

Update `scripts/process_video_transcripts.py` to support:

* Accepting **multiple `--url` values**
* Looping through and processing each video one-by-one
* Optionally outputting to **one combined file** or **separate files** per video:

  * E.g., `data/processed/video_clips_<video_id>.json`
* Print clear success/failure status per video

Update `index_video_clips_chroma.py` to:

* Either index all `.json` files in a given folder
* Or accept a list of input files to index
* Prevent duplicates or collisions across files (e.g., use `video-<video_id>-<segment_number>` as unique IDs)

---

## 🎓 Guidelines & Standards

* Use logging to indicate which video is being processed and how many segments were added
* Continue to embed full transcript into Chroma search index
* Use `video_id` (from URL) for file naming and ID scoping
* Maintain existing single-video compatibility

---

## 📄 Files to Update

* `scripts/process_video_transcripts.py`
* `scripts/index_video_clips_chroma.py`

---

## ✏️ Test CLI

```bash
# Run pipeline on multiple videos
python scripts/process_video_transcripts.py \
  --url https://youtu.be/abc123 --url https://youtu.be/xyz456 \
  --output-folder data/processed/clips/

# Index all .jsons in folder
python scripts/index_video_clips_chroma.py --input-folder data/processed/clips/
```

---

## 📃 Deliverables

* Updated video processing script with multi-URL support
* Folder-based indexing in Chroma
* Unique document IDs for each segment
* Summary printout of processed videos and indexed entries

---

## 🌟 Bonus

* Use video ID + segment\_number as unique Chroma ID
* Export a manifest file listing all processed videos + segments
* Extend CLI to accept input `.txt` list of YouTube URLs
