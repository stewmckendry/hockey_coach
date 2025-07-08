# Codex Agent Task: Fix JSON Parsing in LTAD LLM Pipeline

## 🏋️ Overview

The 3-stage LLM pipeline for extracting LTAD skills is failing in Stage 1 and 2 due to JSON parsing errors. This task fixes those issues and improves LLM reliability and robustness.

Error log:

```
❌ JSON parse failed: Expecting value: line 1 column 1 (char 0)
```

This happens because the OpenAI model returns nothing or non-JSON content. We must sanitize, anchor, and parse the output correctly.

---

## 🔧 What to Fix

### 1. Update `_parse_json()` Function in `extract_ltad_skills.py`

* Add handling for markdown-wrapped JSON responses (`json ... `)
* Add fallback logging to inspect raw content

**Replace current `_parse_json()` with:**

````python
def _parse_json(content: str) -> list[dict] | dict | None:
    try:
        if content.startswith("```json"):
            content = content.strip().split("```json")[1].split("```", 1)[0].strip()
        return json.loads(content)
    except Exception as e:
        print(f"❌ JSON parse failed: {e}")
        print("🔍 Raw content was:\n", content)
        return None
````

---

### 2. Fix Prompts in `prompts/*.yaml`

#### `ltad_stage1_parse_skills.yaml`

Update to:

````yaml
prompt: |
  You are an expert hockey development coach. Given a raw skill section, parse it into structured skill items.

  Return each skill as an object with:
  - skill_name (e.g., "Backward C-cuts")
  - skill_category (e.g., "Skating", "Passing")
  - raw_description (short explanation if needed)

  Use this JSON format:
  ```json
  [
    {
      "skill_name": "Backward C-cuts",
      "skill_category": "Skating",
      "raw_description": "Focus on wide stance and edge control"
    }
  ]
````

Return only the JSON block.

````

#### `ltad_stage2_enrich_skills.yaml`
Make sure it ends with:
```yaml
Return a single JSON object like:
```json
{
  "age_group": "U9",
  "ltad_stage": "Fundamentals 2",
  "position": ["Any"],
  "skill_category": "Skating",
  "skill_name": "T-push",
  "teaching_notes": "Used for lateral movement. Emphasize quick recovery and balance.",
  "season_month": null,
  "source": "u9-core-skills-e.pdf"
}
````

Return only the JSON block.

````

---

## 🔹 Optional Enhancements
- Add retry logic on empty LLM response
- Log intermediate JSON responses to file (`debug/llm_outputs_stage1.json`, etc.)
- Add CLI flag `--debug` to enable full LLM output logging

---

## 🚀 Test Case
```bash
uv run scripts/extract_ltad_skills.py --input-folder data/raw/ltad --output data/processed/ltad_skills_raw.json
````

Check that:

* No parse errors appear
* Outputs written to `ltad_raw_skill_rows.json` and `ltad_skills_raw.json`
* First file has structured rows, second file has valid LTADSkill entries
