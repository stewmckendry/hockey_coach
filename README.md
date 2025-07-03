# 🏒 Hockey Coach Playbook: AI-Powered Drill Search Assistant

The Hockey Coach Playbook is an intelligent assistant that helps coaches and players discover hockey drills using natural language. It leverages AI agents, a semantic vector database (Chroma), and structured metadata to provide high-quality, context-aware recommendations.

---

## 🔍 What It Does

- 💬 **Understands Coaching Goals**: Accepts natural language queries like "I want drills that teach backchecking and speed."
- 🧠 **Expands the Query**: Uses an LLM to broaden searches with synonyms, hockey-specific terms, and coaching language.
- 🔎 **Searches Semantically**: Matches expanded queries against a Chroma vector DB of 1000+ drills.
- 🏅 **Reranks Results with LLM**: A second agent reranks and filters results for coaching relevance.
- 📋 **Summarizes and Explains**: Presents a friendly summary and a curated list of drills with rationale.

---

## 🗂 Project Structure

```bash
hockey_coach_playbook/
├── data/                # Drill datasets (raw, interim, processed)
│   ├── raw/             # Source JSON/CSV
│   ├── interim/         # Sampled or revised versions
│   └── processed/       # Final merged/classified datasets
├── mcp_server/          # AI agents, server tools, prompts
│   ├── server.py        # FastMCP server
│   ├── drill_planner.py # Orchestrator agent
│   ├── main.py          # CLI entrypoint
│   ├── chroma_utils.py  # Chroma helpers
│   └── prompts/         # Agent prompt YAMLs
├── scripts/             # ETL scripts (indexing, cleaning, analysis)
├── outputs/             # Chroma-ready/exportable files
└── README.md
```

---

## 🚀 How to Run It

1. **Set up environment**
    ```bash
    uv venv
    uv pip install -r mcp_server/requirements.txt
    ```

2. **Start Chroma (local)**
    ```bash
    chroma run --host 0.0.0.0 --port 8000 --no-auth
    ```

3. **Index drills into Chroma**
    ```bash
    uv run scripts/index_drills_chroma.py
    ```

4. **Run the AI assistant**
    ```bash
    uv run mcp_server/main.py --input "transition drills for forwards"
    ```

---

## 🧠 Agents Overview

| Agent Name    | Purpose                                 |
|---------------|-----------------------------------------|
| query_agent   | Expands user input with synonyms        |
| search_agent  | Searches Chroma DB with embeddings      |
| reranker      | Reorders results based on LLM review    |
| summarizer    | Summarizes results in coach language    |
| drill_planner | Orchestrates the full pipeline          |

---

## 🛠 Tech Stack

- **OpenAI GPT-4** – LLM agent reasoning
- **MCP SDK** – Agent framework and orchestration
- **Chroma** – Local vector DB for semantic search
- **Python + uv** – Fast dependency and script management

---

## ✅ Status

- ✅ Query expansion
- ✅ Chroma search
- ✅ LLM reranking
- ✅ Final summary output

*🧪 Optional: feedback loop, UI frontend, tagging enhancements*

---

## 🧼 Cleanup Tips

- Keep only `drills_classified_full.json` (final merged dataset)
- Remove/archive `*_sample.json`, `*_page1.csv`, `*_revised.*`
- Use `.gitignore` to skip outputs and cache

---

## 📬 Feedback

Open an issue or connect if you'd like to collaborate on expanding the Hockey Coach Playbook for other sports or training domains!
