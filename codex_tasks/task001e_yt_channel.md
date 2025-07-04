# Codex Agent Task: Automate YouTube Channel Discovery and Video Selection

## 🏋️ Overview

You're building a utility that pulls video metadata from a public YouTube channel and prepares a structured list of URLs to be passed into the video processing pipeline.

---

## 📄 Task Scope

### ✅ Build YouTube Channel Scraper Utility

Create a new script, e.g. `scripts/fetch_channel_videos.py`, that:

* Accepts a YouTube channel URL (e.g. `https://www.youtube.com/@itrainhockey`)
* Extracts a list of videos from the channel

  * For each video: `title`, `url`, `view_count`, `published_date`
* Optionally supports:

  * Limit by most recent `k` videos
  * Limit by most viewed `k` videos
  * Filter by keyword in title (e.g., "defense" or "power skating")
* Saves results to a JSON or `.txt` file (e.g. `data/input/channel_videos.txt` or `.json`)

You may use the `yt-dlp` Python module or YouTube Data API (if API key is available) for fetching video metadata.

---

### ✉️ Output Format

Example output:

```json
[
  {"title": "Power Turns for Beginners", "url": "https://youtu.be/abc123"},
  {"title": "Defense Gap Control", "url": "https://youtu.be/xyz456"}
]
```

Or simple `.txt` list:

```txt
https://youtu.be/abc123
https://youtu.be/xyz456
```

---

### ♻️ Optional Follow-up Integration

* After generating the URL list, allow user to **review/edit** file before passing it to the `process_video_transcripts.py` script
* Add support to `process_video_transcripts.py` to accept:

```bash
--url-list data/input/channel_videos.txt
```

Which loads and expands to `--url` args (need to extract the URLs from the file).

---

## 🎓 Guidelines & Standards

* Use `yt-dlp` or `youtube_dl` for scraping if no API key is configured
* Handle pagination and lazy loading for large channels
* Provide logging per video retrieved
* Keep CLI flexible to add filtering logic later

---

## 📄 Files to Create/Update

* `scripts/fetch_channel_videos.py`
* (Optionally) `scripts/process_video_transcripts.py` to support `--url-list`

---

## ✏️ Example CLI Usage

```bash
# Fetch recent or popular videos
python scripts/fetch_channel_videos.py \
  --channel https://www.youtube.com/@itrainhockey \
  --sort recent --limit 15 \
  --output data/input/itrainhockey_urls.txt

# Run video pipeline using saved file
python scripts/process_video_transcripts.py \
  --url-list data/input/itrainhockey_urls.txt \
  --output-folder data/processed/clips/
```

---

## 📃 Deliverables

* New script to fetch and save video URLs from any hockey YouTube account
* Optional support for sorted/filtered lists
* Smooth handoff to existing multi-video processing pipeline

---

## 🌟 Bonus

* Show total channel video count
* Add support for export as CSV with `title`, `views`, `url`, `published`
* Visualize top videos for selection UI later
