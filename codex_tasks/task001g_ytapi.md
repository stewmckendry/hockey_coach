# Codex Agent Task: Use YouTube Data API via MCP Tool for Video Search Agent

## 🏋️ Overview

You're improving the `video_search_agent` by replacing LLM-generated video links with real, verified YouTube links returned from the official YouTube Data API. You'll build a new MCP Tool that wraps the `youtube.search.list` and `videos.list` endpoints.

The new tool will be used in the agent instead of (or alongside) `WebSearchTool` for reliable results.

---

## 📄 Task Scope

### ✅ Build `YouTubeSearchTool`

* Create a tool that calls YouTube Data API `search.list`

* Accepts parameters:

  * `query`: search string (e.g., "backchecking drills")
  * `max_results`: number of videos to return
  * (optional) `channel_id`, `videoCategoryId`, `order` (e.g., "viewCount", "date")

* For each result, call `videos.list` to fetch full metadata:

  * `title`, `videoId`, `channelTitle`, `viewCount`, `publishTime`, etc.

* Return a list of structured `VideoResult` objects:

```json
{
  "url": "https://www.youtube.com/watch?v=IN7YbVpfHrM",
  "title": "Edge Work Drills",
  "author": "BK Hockey",
  "channel": "World Class Skating",
  "view_count": 120304,
  "published_at": "2023-02-14T00:00:00Z"
}
```

### ✅ Integrate Tool into `video_search_agent.py`

* Replace or supplement `WebSearchTool()` with `YouTubeSearchTool`
* Update prompt to clarify that all results must come from the YouTube API (not hallucinated)

---

## 🧠 Prompt Suggestions

Update `video_search_prompt.yaml` to clarify:

```yaml
Only return video links retrieved from the YouTube Data API, with real video IDs.
Do not guess or fabricate video URLs.
```

---

## 🧰 Setup: How to Enable YouTube Data API Access

1. Go to [https://console.cloud.google.com/](https://console.cloud.google.com/)
2. Create or select a project
3. In "APIs & Services > Library", enable:

   * YouTube Data API v3
4. Go to "Credentials" and:

   * Create an API key
   * Restrict usage to YouTube Data API (optional, recommended)
5. Add this to your environment:

```bash
export YOUTUBE_API_KEY="your-key-here"
```

Or store in `.env` and load using `os.getenv("YOUTUBE_API_KEY")`

---

## 📄 Files to Create/Update

* `tools/youtube_search_tool.py` (or `agents/tool/youtube_search_tool.py`)
* `app/client/agent/video_search_agent.py`
* `prompts/video_search_prompt.yaml`

---

## ✏️ Test Queries

```bash
python app/client/agent/video_search_agent.py \
  --query "top hockey shooting drills" \
  --num 10 \
  --output data/input/video_index.json
```

---

## 📃 Deliverables

* Verified YouTube video metadata fetched from YouTube API
* Agent uses real video IDs only
* URLs saved to `.json` for use with transcript pipeline
* No LLM-generated video IDs

---

## 🌟 Bonus

* Add filtering by skill or role using query pattern matching
* Add `--channel` override to restrict search
* Support fuzzy filters (e.g., "goalie" vs "goaltending")
