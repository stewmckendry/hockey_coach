"""Utility to normalize and infer LTAD skill metadata using an LLM."""

from __future__ import annotations
import json
import re
from pathlib import Path

import yaml
from openai import OpenAI
from models.ltad import LTADSkill

client = OpenAI()

PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "ltad_stage3_normalize.yaml"
with open(PROMPT_PATH, "r", encoding="utf-8") as f:
    PROMPT = yaml.safe_load(f).get("prompt", "")

LTAD_STAGE_LOOKUP = {
    "U7": "Fundamentals 1",
    "U9": "Fundamentals 2",
    "U11": "Learn to Train",
    "U13": "Train to Train",
}

def infer_age_group_from_filename(filename: str) -> str | None:
    match = re.search(r"u\d{1,2}", filename.lower())
    if match:
        return match.group(0).upper()
    return None


def _parse_json(content: str) -> dict | None:
    try:
        if content.startswith("```json"):
            content = content.split("```json", 1)[1].split("```", 1)[0]
        return json.loads(content)
    except Exception:
        return None

def normalize_ltad_skill(skill: dict) -> dict:
    """Use the LLM to canonicalize skill name/variant and infer metadata."""
    # Pre-fill missing fields using heuristics
    if not skill.get("age_group") and skill.get("source"):
        inferred = infer_age_group_from_filename(skill["source"])
        if inferred:
            skill["age_group"] = inferred

    if not skill.get("ltad_stage") and skill.get("age_group"):
        skill["ltad_stage"] = LTAD_STAGE_LOOKUP.get(skill["age_group"], "Not provided")

    user = json.dumps(skill, indent=2)
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        temperature=0,
        messages=[{"role": "system", "content": PROMPT}, {"role": "user", "content": user}],
    )
    data = _parse_json(resp.choices[0].message.content)
    if isinstance(data, dict):
        try:
            return LTADSkill(**data).model_dump()
        except Exception:
            pass
    return skill
