# Codex Agent Task: Enrich and Normalize LTAD Skills (Stages 2 & 4)

## 🏋️ Overview

This task updates the existing LTAD skill enrichment and normalization pipeline:

* Enhances Stage 2 (LLM-based enrichment)
* Adds a new Stage 4 to normalize and infer missing metadata
* Updates the main script to append output to existing files instead of overwriting

The goal is to produce semantically rich, consistent, structured skill entries ready for search and planning agents.

---

## 🔧 Part 1 – Update Stage 2 (Enrichment)

### 1.1 Add new fields to `LTADSkill` model (in `models/ltad.py`):

```python
class LTADSkill(BaseModel):
    age_group: str | None = None
    ltad_stage: str | None = None
    position: list[str] | None = None
    skill_category: str | None = None
    skill_name: str | None = None
    teaching_notes: str | None = None
    season_month: str | None = None
    progression_stage: str | None = None  # e.g. Introductory, Developmental, Refinement
    teaching_complexity: int | None = None  # e.g. 1 = beginner, 2 = intermediate, 3 = advanced
    variant: str | None = None
    source: str
```

### 1.2 Update `ltad_stage2_enrich_skills.yaml` prompt:

Add to the end:

```yaml
Also include:
- progression_stage: one of ["Introductory", "Developmental", "Refinement"]
- teaching_complexity: 1 (easy) to 3 (complex), based on how hard this is for the average player
```

LLM should now return a complete enriched `LTADSkill` with added context.

---

## 🔧 Part 3 – Add Stage 3: Normalize & Canonicalize

Create `normalize_ltad_skill(skill: dict) -> dict` in a new `ltad_normalizer.py`

### 3.1 Normalize Skill Name + Variants

* Canonicalize common skill patterns:

  * "C-cuts - left foot / right foot", "C-cuts alternating" → `skill_name = "C-cuts"`, `variant = "alternating"`, etc.
  * "Stance", "Wide Stance", "Narrow Stance" remain separate, but tagged with `variant = "wide"`, etc.

### 3.2 Infer `age_group` from filename

```python
if not skill["age_group"]:
    skill["age_group"] = infer_age_group_from_filename(skill["source"])  # e.g. "U7"
```

### 3.3 Infer `ltad_stage` from lookup table

```python
LTAD_STAGE_LOOKUP = {
    "U7": "Fundamentals 1",
    "U9": "Fundamentals 2",
    "U11": "Learn to Train",
    "U13": "Train to Train"
    # etc.
}
if not skill["ltad_stage"]:
    skill["ltad_stage"] = LTAD_STAGE_LOOKUP.get(skill["age_group"], "Not provided")
```

### 3.4 Implement as Stage 3 in Pipeline

* Add new function: `stage4_normalize_skill(enriched_skill: dict) -> dict`
* Run this as a final pass after Stage 2 (and before indexing)
* Log both raw and normalized skill versions for traceability

---

## 🔧 Part 4 – Update `scripts/extract_ltad_skills.py`

### 3.1 Update Output File Logic

For each of the following output paths:

* `data/processed/ltad_skills_raw.json`
* `data/processed/ltad_raw_skill_rows.json`
* `data/processed/ltad_sections.json`

Update logic to:

* Load any existing data from disk
* Append new entries
* Deduplicate if needed (based on skill\_name + category + source)
* Save the extended output

---

## 🚀 Sample Normalized Output

```json
{
  "skill_name": "C-cuts",
  "variant": "alternating",
  "skill_category": "Skating",
  "age_group": "U7",
  "ltad_stage": "Fundamentals 1",
  "progression_stage": "Introductory",
  "teaching_complexity": 1,
  "teaching_notes": "Used to develop early edge control and rhythm.",
  "source": "u7-core-skills-e.pdf"
}
```

---

## 📂 Output

* `data/processed/ltad_skills_normalized.json`
* Final list of enriched, normalized skills for indexing

---

## 🔹 Bonus (optional)

* Add `--normalize` flag to CLI to enable/disable Stage 4
* Create a JSONL file with `[{raw}, {normalized}]` entries for QA

---

## 📊 Test Criteria

* Run on `u7-core-skills-e.pdf`
* Check that:

  * \~50 skills are returned
  * All have `progression_stage`, `teaching_complexity`, `age_group`, `ltad_stage`
  * Variants like "C-cuts alternating" are normalized
  * Output files are appended to, not overwritten
