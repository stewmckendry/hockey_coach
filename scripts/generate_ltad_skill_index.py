#!/usr/bin/env python3
"""Consolidated LTAD skill extraction and post-processing pipeline."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

import fitz
import yaml
from openai import OpenAI

sys.path.append(str(Path(__file__).resolve().parent.parent))

from models.ltad import LTADSkill
from ltad_normalizer import normalize_ltad_skill


PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"

def load_prompt(name: str) -> str:
    path = PROMPT_DIR / name
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return str(data.get("prompt", ""))

PROMPT_STAGE0 = load_prompt("ltad_stage0_extract.yaml")
PROMPT_STAGE1 = load_prompt("ltad_stage1_parse_skills.yaml")
PROMPT_STAGE2 = load_prompt("ltad_stage2_enrich_skills.yaml")
PROMPT_POST = load_prompt("ltad_postprocess_prompt.yaml")
PROMPT_COMPARE = load_prompt("ltad_compare_prompt.yaml")
PROMPT_MERGE = load_prompt("ltad_merge_prompt.yaml")

client = OpenAI()


CATEGORY_MAP = {
    "Skating": "Skating",
    "Starting and Stopping": "Skating",
    "Balance and Agility": "Skating",
    "Quick Feet": "Skating",
    "Power Skating": "Skating",
    "Stride": "Skating",
    "Edge Control": "Skating",
    "Puck Control": "Puck Control",
    "Puck Handling": "Puck Control",
    "Stickhandling": "Puck Control",
    "Basic Puck Control": "Puck Control",
    "Advanced Puckhandling": "Puck Control",
    "Control": "Puck Control",
    "Passing": "Passing",
    "Passing and Receiving": "Passing",
    "Moving Passing and Receiving": "Passing",
    "Stationary Passing and Receiving": "Passing",
    "Breakout Passes": "Passing",
    "Shooting": "Shooting",
    "Wrist Shot": "Shooting",
    "Slap Shot": "Shooting",
    "Backhand Shot": "Shooting",
    "Shot Mentality": "Shooting",
    "Scoring Situations": "Shooting",
    "Defensive Play": "Defensive Tactics",
    "Defensive Skills": "Defensive Tactics",
    "Defence": "Defensive Tactics",
    "Defense": "Defensive Tactics",
    "Defensive Zone Coverage": "Defensive Tactics",
    "Gap Control": "Defensive Tactics",
    "D Zone Coverage": "Defensive Tactics",
    "Offensive Play": "Offensive Tactics",
    "Offensive Tactics": "Offensive Tactics",
    "Offensive Zone Play": "Offensive Tactics",
    "Attack Triangle": "Offensive Tactics",
    "Entries": "Offensive Tactics",
    "Transition Play": "Team Play",
    "Breakouts": "Team Play",
    "Regroups": "Team Play",
    "Neutral Zone Play": "Team Play",
    "Team Play": "Team Play",
    "Game Situations": "Hockey IQ",
    "Game Awareness": "Hockey IQ",
    "Game Understanding": "Hockey IQ",
    "Game Strategy": "Hockey IQ",
    "Decision Making": "Hockey IQ",
    "Tactics": "Hockey IQ",
    "Position Versatility": "Hockey IQ",
    "Hockey Sense": "Hockey IQ",
    "Goaltending": "Goaltending",
    "Goalie Movement": "Goaltending",
    "Goaltending Skill Development": "Goaltending",
    "Development Pyramid": "Goaltending",
    "Positioning": "Goaltending",
    "Save Selection": "Goaltending",
    "Physical Play": "Compete",
    "Competitive Play": "Compete",
    "Intangibles": "Compete",
    "Work Ethic": "Compete",
    "Mental Toughness": "Compete",
    "Confidence": "Compete",
    "Resiliency": "Compete",
    "General": "General",
    "Developmental": "General",
    "Other": "General",
    "Technical Skills": "General Development",
    "General Development": "General Development",
}

AGE_STAGE_MAP = {
    "U7": "Fundamentals 1",
    "U9": "Fundamentals 2",
    "U11": "Learn to Train",
    "U13": "Train to Train",
    "U15": "Train to Train",
    "U18": "Train to Compete",
}

DEFAULT_POSITION_AGES = ["U9", "U11", "U13", "U15"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_json(content: str) -> Any:
    try:
        if content.startswith("```json"):
            content = content.split("```json", 1)[1].split("```", 1)[0]
        return json.loads(content)
    except Exception:
        return None


def _safe_age_group(val: str | None) -> str | None:
    if not val:
        return None
    v = val.upper().strip()
    if not v:
        return None
    if v.startswith("U") and len(v) <= 3:
        return v
    if "U" in v:
        parts = v.split("U")
        for p in parts:
            if p.isdigit():
                return f"U{p}"
    return None


def normalize_category(cat: str | None) -> str | None:
    if not cat:
        return None
    base = cat.strip()
    canonical = CATEGORY_MAP.get(base, CATEGORY_MAP.get(base.title(), None))
    if canonical:
        return canonical
    return base.title()


def stage0_sections(text: str, source: str, page_num: int) -> List[dict]:
    user = f"Source: {source}\nPage: {page_num}\n\n{text}\n\nReturn JSON list."
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        temperature=0,
        messages=[{"role": "system", "content": PROMPT_STAGE0}, {"role": "user", "content": user}],
    )
    data = _parse_json(resp.choices[0].message.content)
    if not data:
        return []
    if isinstance(data, dict):
        data = [data]
    for d in data:
        d.setdefault("source", source)
        d.setdefault("page_number", page_num)
    return data  # type: ignore[return-value]


def stage1_parse(section: dict) -> List[dict]:
    text = section.get("raw_text", "")
    title = section.get("section_title", "")
    user = f"Section: {title}\n\n{text}\n\nReturn JSON list."
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        temperature=0,
        messages=[{"role": "system", "content": PROMPT_STAGE1}, {"role": "user", "content": user}],
    )
    data = _parse_json(resp.choices[0].message.content)
    if not data:
        return []
    if isinstance(data, dict):
        data = [data]
    for d in data:
        d.update({
            "source": section.get("source"),
            "page_number": section.get("page_number"),
            "section_title": title,
        })
    return data  # type: ignore[return-value]


def stage2_enrich(row: dict) -> dict | None:
    user = f"Raw Skill Row:\n{json.dumps(row, indent=2)}\n\nReturn a JSON object."
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        temperature=0,
        messages=[{"role": "system", "content": PROMPT_STAGE2}, {"role": "user", "content": user}],
    )
    data = _parse_json(resp.choices[0].message.content)
    if not isinstance(data, dict):
        return None
    data.setdefault("source", row.get("source"))
    try:
        return LTADSkill(**data).model_dump()
    except Exception:
        return None


def stage3_normalize(skill: dict) -> dict:
    norm = normalize_ltad_skill(skill)
    cat = normalize_category(norm.get("skill_category"))
    if cat:
        norm["skill_category"] = cat

    age = _safe_age_group(norm.get("age_group"))
    if age:
        norm["age_group"] = age
        norm["ltad_stage"] = norm.get("ltad_stage") or AGE_STAGE_MAP.get(age)
    else:
        norm["age_group"] = None

    return norm


def stage4_postprocess(skill: dict) -> dict:
    user = json.dumps(skill, indent=2)
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        temperature=0,
        messages=[{"role": "system", "content": PROMPT_POST}, {"role": "user", "content": user}],
    )
    data = _parse_json(resp.choices[0].message.content)
    if isinstance(data, dict):
        try:
            return LTADSkill(**data).model_dump()
        except Exception:
            pass
    return skill


def _canonical_key(skill: dict) -> Tuple[str, str, str, str]:
    name = (skill.get("skill_name") or "").lower().strip()
    cat = (skill.get("skill_category") or "").lower().strip()
    pos_list = skill.get("position") or ["Any"]
    pos = ";".join(sorted(p.lower().strip() for p in pos_list))
    variant = (skill.get("variant") or "").lower().strip()
    return name, cat, pos, variant


def compare_skills_llm(skills: List[dict]) -> List[List[dict]]:
    user = json.dumps(skills, indent=2)
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        temperature=0,
        messages=[{"role": "system", "content": PROMPT_COMPARE}, {"role": "user", "content": user}],
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
    user = json.dumps(skills, indent=2)
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        temperature=0,
        messages=[{"role": "system", "content": PROMPT_MERGE}, {"role": "user", "content": user}],
    )
    data = _parse_json(resp.choices[0].message.content)
    if isinstance(data, dict):
        return data
    return skills[0]


def deduplicate(skills: List[dict]) -> Tuple[List[dict], dict]:
    groups: Dict[Tuple[str, str, str], List[dict]] = defaultdict(list)
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


def audit_skills(skills: List[dict], sections: List[dict]) -> dict:
    audits = []
    for skill in skills:
        name = (skill.get("variant") or skill.get("skill_name") or "").lower()
        cat = (skill.get("skill_category") or "").lower()
        found = False
        excerpt = ""
        for sec in sections:
            text = sec.get("raw_text", "").lower()
            if name and name in text:
                found = True
                excerpt = text[:200]
                break
            title = sec.get("section_title", "").lower()
            if cat and cat in title:
                found = True
                excerpt = text[:200]
                break
        audits.append({
            "skill_name": skill.get("skill_name"),
            "found_in_source": found,
            "source_excerpt": excerpt,
        })
    coverage = sum(1 for a in audits if a["found_in_source"]) / len(audits) if audits else 0
    return {"coverage": coverage, "audits": audits}


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def process_pdf(pdf_path: Path) -> Tuple[List[dict], List[dict], List[dict]]:
    doc = fitz.open(pdf_path)
    sections: List[dict] = []
    raw_rows: List[dict] = []
    skills: List[dict] = []

    for page_no, page in enumerate(doc, start=1):
        text = page.get_text()
        secs = stage0_sections(text, pdf_path.name, page_no)
        sections.extend(secs)
        for sec in secs:
            rows = stage1_parse(sec)
            raw_rows.extend(rows)
            for row in rows:
                skill = stage2_enrich(row)
                if skill:
                    skills.append(skill)
    doc.close()
    return sections, raw_rows, skills


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate LTAD skill index")
    parser.add_argument("--input-folder", type=Path, default=Path("data/raw/ltad"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/ltad_skills_final.json"))
    args = parser.parse_args()

    all_sections: List[dict] = []
    all_rows: List[dict] = []
    all_skills: List[dict] = []

    for pdf in sorted(args.input_folder.glob("*.pdf")):
        print(f"📖 Processing {pdf.name}")
        try:
            secs, rows, skills = process_pdf(pdf)
            all_sections.extend(secs)
            all_rows.extend(rows)
            all_skills.extend(skills)
        except Exception as e:
            print(f"❌ Failed to process {pdf.name}: {e}")

    # Stage 3 normalize
    normalized = [stage3_normalize(s) for s in all_skills]

    # Age group default for position pathways
    for skill in normalized:
        cat = skill.get("skill_category") or ""
        if not skill.get("age_group") and cat in {"Goaltending", "Defensive Tactics"}:
            skill["age_groups"] = DEFAULT_POSITION_AGES.copy()
            skill["source_type"] = "position_pathway"
        else:
            ag = skill.get("age_group")
            if ag:
                skill["age_groups"] = [ag]

    # Stage 4 postprocess with LLM
    post = [stage4_postprocess(s) for s in normalized]

    # Stage 5 deduplicate
    deduped, report = deduplicate(post)

    # Stage 6 audit
    audit = audit_skills(deduped, all_sections)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(deduped, f, indent=2)

    report_path = args.output.with_name("ltad_skills_dedup_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    audit_path = args.output.with_name("ltad_skills_audit.json")
    with open(audit_path, "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2)

    # Debug artifacts
    (args.output.with_name("ltad_sections.json")).write_text(json.dumps(all_sections, indent=2), encoding="utf-8")
    (args.output.with_name("ltad_raw_skill_rows.json")).write_text(json.dumps(all_rows, indent=2), encoding="utf-8")
    (args.output.with_name("ltad_skills_enriched.json")).write_text(json.dumps(all_skills, indent=2), encoding="utf-8")
    (args.output.with_name("ltad_skills_normalized.json")).write_text(json.dumps(normalized, indent=2), encoding="utf-8")

    print(f"✅ Final skills: {len(deduped)} (deduped from {len(all_skills)})")
    print(f"✅ Dedup report: {report_path}")
    print(f"✅ Audit report: {audit_path}")


if __name__ == "__main__":
    main()
