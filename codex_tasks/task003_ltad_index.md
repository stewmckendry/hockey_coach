# Codex Agent Task: Index Hockey Canada LTAD Skill Pathways

## 🏋️ Overview

You are building a data ingestion and indexing pipeline to process Hockey Canada PDF resources containing long-term athlete development (LTAD) guidance by age group and position. The resulting index will support age- and role-appropriate season planning and practice generation by other agents.

This task focuses specifically on structured, seasonally grounded skill pathways for:

* Core hockey skills (e.g. skating, puck control, shooting)
* Positional development (e.g. goaltending, defence)
* Monthly skill progression recommendations

> 🚨 This task excludes general drill content (handled separately), off-ice drills (new task), and small-area games.

---

## 🔧 What to Build

### 1. `scripts/extract_ltad_skills.py`

* Load source PDFs from `data/raw/ltad/`
* Use `PyMuPDF` or `pdfplumber` to extract structured content from text + layout
* Use LLM (via OpenAI API) to:

  * Parse blocks of text into JSON records
  * Classify by age group, skill category, position, and month if available
  * Summarize long skill descriptions into coaching tips

### 2. `scripts/normalize_ltad_schema.py`

* Standardize fields across PDFs and age levels
* Normalize synonyms (e.g. "crossunders" = "crossovers", "goalie" = "goaltending")
* Deduplicate overlapping entries

### 3. `scripts/index_ltad_chroma.py`

* Embed entries using OpenAIEmbeddings
* Store in ChromaDB collection: `ltad_index`
* Metadata fields:

  ```json
  {
    "age_group": "U9",
    "ltad_stage": "Fundamentals 2",
    "position": ["Goalie", "Defence", "Any"],
    "skill_category": "Skating",
    "skill_name": "Backward C-cuts",
    "teaching_notes": "Maintain balance and use alternating edge pushes",
    "season_month": "October",
    "source": "2022-23-goaltending-pathway-e.pdf"
  }
  ```

### 4. `data/processed/ltad_index.json`

* Save structured data prior to embedding
* Reusable by future QA or UI display agents

---

## 🔍 Input Files (Expected in `data/raw/ltad/`)

| File Name                                         | Content                                     | Notes                                                                 |
| ------------------------------------------------- | ------------------------------------------- | --------------------------------------------------------------------- |
| `u7-core-skills.pdf` ... `u18-core-skills.pdf`    | Age-based skill ladders                     | ✅ Main source                                                         |
| `goaltending-pathway.pdf`                         | Positional monthly progression              | ✅ Extract seasonal structure + skills 【76†source】                     |
| `developing-defence.pdf`                          | Defence skill pyramid + month-by-month plan | ✅ Include 【78†source】                                                 |
| `off-ice-training.pdf`                            | Dryland drills                              | ❌ Skip for now (separate task)                                        |
| `skating.pdf`, `puck-control.pdf`, `shooting.pdf` | TBD                                         | May be better treated as drill entries. Clarify coverage vs. age docs |
| `small-area-games.pdf`                            | SAG design                                  | ❌ Skip                                                                |

---

## 🚀 MCP Tool Integration (Post Indexing)

Add tools to `ltad_tools.py` or `ltad_server.py`:

```python
@mcp.tool("get_skills_by_age")
def get_skills_by_age(age_group: str) -> list[LTADSkill]: ...

@mcp.tool("get_skills_by_position")
def get_skills_by_position(position: str) -> list[LTADSkill]: ...

@mcp.tool("search_ltad_knowledge")
def search_ltad_knowledge(query: str) -> list[LTADSkill]: ...
```

---

## 🚀 Codex-Specific Guidance

* Use `prompt_tool.py` LLM wrapper if available to chunk and convert skill blocks into JSON
* Match prompt pattern to `video_summarizer_agent.py`
* Validate output: no missing fields, consistent age/stage labels
* Store outputs in `data/processed/ltad_index.json` and Chroma
* Reuse `chroma_utils.py` for collection and embedding logic

---

## ✨ Stretch Goals

* Include off-ice skills and map them to on-ice equivalents in a separate pipeline
* Create LTAD-aligned tags in `drills.json` and `video_clips.json`
* Annotate skills with developmental priorities (e.g. intro vs refine)

---

## 🔎 Additional Notes

* Goaltending and defence have clear pathways. Forward development may be embedded in general skills or missing entirely.
* Future work: extract or synthesize forward skill ladders from video/coach sources.
