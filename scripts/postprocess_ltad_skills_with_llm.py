#!/usr/bin/env python3
"""Post-process LTAD skills using an LLM and perform deduplication."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Any

import yaml
from openai import OpenAI

sys.path.append(str(Path(__file__).resolve().parent.parent))

from models.ltad import LTADSkill  # noqa: E402

client = OpenAI()

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"

with open(PROMPT_DIR / "ltad_postprocess_prompt.yaml", "r", encoding="utf-8") as f:
    POSTPROCESS_PROMPT = yaml.safe_load(f).get("prompt", "")
with open(PROMPT_DIR / "ltad_compare_prompt.yaml", "r", encoding="utf-8") as f:
    COMPARE_PROMPT = yaml.safe_load(f).get("prompt", "")
with open(PROMPT_DIR / "ltad_merge_prompt.yaml", "r", encoding="utf-8") as f:
    MERGE_PROMPT = yaml.safe_load(f).get("prompt", "")


# ---------------------------------------------------------------------------
# Utils
# ---------------------------------------------------------------------------

def _parse_json(content: str) -> Any:
    """Safely parse JSON content from an LLM response."""
    try:
        if content.startswith("```json"):
            content = content.split("```json", 1)[1].split("```", 1)[0]
        return json.loads(content)
    except Exception as e:  # pragma: no cover - simple helper
        print(f"❌ JSON parse failed: {e}")
        print("🔍 Raw content was:\n", content)
        return None


def _load_json_if_exists(path: Path) -> list[dict]:
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


# ---------------------------------------------------------------------------
# LLM helpers
# ---------------------------------------------------------------------------

def postprocess_skill_llm(skill: dict) -> dict:
    """Normalize a single skill record using the LLM."""
    user = json.dumps(skill, indent=2)
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        temperature=0,
        messages=[{"role": "system", "content": POSTPROCESS_PROMPT}, {"role": "user", "content": user}],
    )
    data = _parse_json(resp.choices[0].message.content)
    if isinstance(data, dict):
        try:
            return LTADSkill(**data).model_dump()
        except Exception as e:  # pragma: no cover - validation helper
            print(f"❌ Invalid LTADSkill from LLM: {e}")
    return skill


def compare_skills_llm(skills: List[dict]) -> List[List[dict]]:
    """Ask the LLM which skills in the list are duplicates."""
    user = json.dumps(skills, indent=2)
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        temperature=0,
        messages=[{"role": "system", "content": COMPARE_PROMPT}, {"role": "user", "content": user}],
    )
    data = _parse_json(resp.choices[0].message.content)
    if isinstance(data, list):
        groups: List[List[dict]] = []
        for g in data:
            if isinstance(g, list):
                groups.append([skills[i] for i in g if 0 <= i < len(skills)])
        if groups:
            return groups
    return [skills]


def merge_skills_llm(skills: List[dict]) -> dict:
    """Merge multiple skill records via LLM."""
    user = json.dumps(skills, indent=2)
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        temperature=0,
        messages=[{"role": "system", "content": MERGE_PROMPT}, {"role": "user", "content": user}],
    )
    data = _parse_json(resp.choices[0].message.content)
    if isinstance(data, dict):
        return data
    return skills[0]


# ---------------------------------------------------------------------------
# Deduplication logic
# ---------------------------------------------------------------------------

def _canonical_key(skill: dict) -> tuple[str, str, str, str]:
    name = (skill.get("skill_name") or "").lower().strip()
    cat = (skill.get("skill_category") or "").lower().strip()
    pos_list = skill.get("position") or ["Any"]
    pos = ";".join(sorted(p.lower().strip() for p in pos_list))
    variant = (skill.get("variant") or "").lower().strip()
    return name, cat, pos, variant


def deduplicate_skills(skills: List[dict]) -> tuple[List[dict], dict]:
    groups: Dict[tuple[str, str, str], List[dict]] = defaultdict(list)
    for s in skills:
        key = _canonical_key(s)[:3]
        groups[key].append(s)

    merged: List[dict] = []
    report_clusters: List[dict] = []

    for grp in groups.values():
        if len(grp) == 1:
            merged.append(grp[0])
            continue
        subgroups = [grp]
        if 2 <= len(grp) <= 10:
            subgroups = compare_skills_llm(grp)
        for sub in subgroups:
            if len(sub) == 1:
                merged.append(sub[0])
                continue
            merged_skill = merge_skills_llm(sub)
            merged.append(merged_skill)
            report_clusters.append({"original": sub, "merged": merged_skill})

    report = {
        "total_before": len(skills),
        "total_after": len(merged),
        "deduplicated": len(skills) - len(merged),
        "merged_clusters": len(report_clusters),
        "sample_clusters": report_clusters[:5],
    }
    return merged, report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Post-process LTAD skills with LLM and deduplicate")
    parser.add_argument("--input", type=Path, default=Path("data/processed/ltad_skills_processed.json"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/ltad_skills_postprocessed.json"))
    parser.add_argument("--enriched", type=Path, default=Path("data/processed/ltad_skills_enriched.json"))
    parser.add_argument("--report", type=Path, default=Path("data/processed/ltad_dedup_report.json"))
    args = parser.parse_args()

    skills = _load_json_if_exists(args.input)
    if not skills:
        print(f"❌ No skills found at {args.input}")
        return
    print(f"✅ Loaded {len(skills)} skills from {args.input}")

    enriched = [postprocess_skill_llm(s) for s in skills]
    args.enriched.parent.mkdir(parents=True, exist_ok=True)
    with open(args.enriched, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2)
    print(f"✅ Wrote enriched skills to {args.enriched}")

    deduped, report = deduplicate_skills(enriched)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(deduped, f, indent=2)
    print(f"✅ Wrote {len(deduped)} deduplicated skills to {args.output}")

    with open(args.report, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"✅ Wrote deduplication report to {args.report}")


if __name__ == "__main__":
    main()
