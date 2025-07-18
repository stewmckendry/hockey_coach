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
from ltad_normalizer import normalize_ltad_skill, infer_age_group_from_text
from difflib import SequenceMatcher


PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"

def load_prompt(name: str) -> str:
    path = PROMPT_DIR / name
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return str(data.get("prompt", ""))

PROMPT_STAGE0 = load_prompt("ltad_stage0_extract.yaml")
PROMPT_STAGE1 = load_prompt("ltad_stage1_parse_skills.yaml")
PROMPT_STAGE2 = load_prompt("ltad_stage2_enrich_skills.yaml")
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
    "Body Contact": "Checking",
    "Checking": "Checking",
    "Body Contact and Checking": "Checking",
    "Angling": "Defensive Tactics",
    "Face-offs": "Faceoffs",
    "Faceoff": "Faceoffs",
    "Shooting and Scoring": "Shooting",
    "Skating Agility": "Skating",
    "Goaltender Movement": "Goaltending",
    "Offensive Skills": "Offensive Tactics",
    "Individual Skills": "General Development",
    "Compete Level": "Compete",
    "Small Area Games": "Team Play",
    "Power Play": "Team Play",
    "Penalty Kill": "Team Play",
    "Specialty Teams": "Team Play",
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
    return "General"


def clean_variant(text: str | None) -> str:
    if not text:
        return ""
    v = text.lower()
    v = v.replace("forward and backward", "fwd+bwd")
    v = v.replace("forward & backward", "fwd+bwd")
    v = v.replace("forward/backward", "fwd+bwd")
    v = v.replace("around circle", "circle")
    v = v.replace("-", ",")
    v = v.replace("  ", " ")
    return v.strip(" ,;")


def normalize_variant(text: str | None) -> str:
    """Normalize verbose variant strings for consistency."""
    return clean_variant(text)


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
        skill = LTADSkill(**data).model_dump()
        skill["section_title"] = row.get("section_title")
        return skill
    except Exception:
        return None


def stage3_normalize(skill: dict) -> dict:
    norm = normalize_ltad_skill(skill)

    # Infer age group from section title if still missing
    if not norm.get("age_group") and skill.get("section_title"):
        ag = infer_age_group_from_text(skill["section_title"])
        if ag:
            norm["age_group"] = ag

    cat = normalize_category(norm.get("skill_category"))
    if cat:
        norm["skill_category"] = cat

    age = _safe_age_group(norm.get("age_group"))
    if age:
        norm["age_group"] = age
        norm["ltad_stage"] = norm.get("ltad_stage") or AGE_STAGE_MAP.get(age)
    else:
        norm["age_group"] = "Unknown"

    norm["variant"] = normalize_variant(norm.get("variant"))

    ag = norm.get("age_group")
    if ag:
        norm["age_groups"] = [ag]
    else:
        norm["age_groups"] = []

    norm.pop("age_group", None)

    norm.pop("section_title", None)
    return norm




def _canonical_key(skill: dict) -> Tuple[str, str, str, str]:
    name = (skill.get("skill_name") or "").lower().strip()
    cat = (skill.get("skill_category") or "").lower().strip()
    variant = normalize_variant(skill.get("variant"))
    pos_list = skill.get("position") or ["Any"]
    pos = ";".join(sorted(p.lower().strip() for p in pos_list))
    return name, cat, variant, pos


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
        key_parts = _canonical_key(s)
        key = key_parts[:3]  # name, category, variant
        groups[key].append(s)

    merged: List[dict] = []
    report_clusters: List[dict] = []

    for grp in groups.values():
        if len(grp) == 1:
            merged.append(grp[0])
            continue
        notes = [g.get("teaching_notes") or "" for g in grp]
        first_note = notes[0]
        similar = all(SequenceMatcher(None, first_note, n).ratio() > 0.9 for n in notes[1:])
        subgroups = [grp]
        if not similar and 2 <= len(grp) <= 10:
            subgroups = compare_skills_llm(grp)
        for sub in subgroups:
            if len(sub) == 1:
                merged.append(sub[0])
                continue
            if similar:
                merged_skill = sub[0].copy()
            else:
                merged_skill = merge_skills_llm(sub)
            ags = set()
            for it in sub:
                if it.get("age_groups"):
                    ags.update(it["age_groups"])
            if merged_skill.get("age_groups"):
                ags.update(merged_skill["age_groups"])
            if ags:
                merged_skill["age_groups"] = sorted(ags)
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
        required = [
            "age_groups",
            "ltad_stage",
            "position",
            "skill_category",
            "skill_name",
            "source",
        ]
        missing = [f for f in required if not skill.get(f)]
        audits.append({
            "skill_name": skill.get("skill_name"),
            "found_in_source": found,
            "source_excerpt": excerpt,
            "missing_fields": missing,
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

    print(f"\n✅ Parsing PDF: {pdf_path.name}")

    for page_no, page in enumerate(doc, start=1):
        text = page.get_text()
        secs = stage0_sections(text, pdf_path.name, page_no)
        sections.extend(secs)
        print(f"  - Stage 0 sections on page {page_no}: {len(secs)}")
        for sec in secs:
            rows = stage1_parse(sec)
            raw_rows.extend(rows)
            print(f"    • Stage 1 rows from section '{sec.get('section_title', '')}': {len(rows)}")
            for row in rows:
                skill = stage2_enrich(row)
                if skill:
                    skills.append(skill)
    doc.close()
    print(f"  -> Stage 2 enriched skills: {len(skills)}")
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

    print("\n✅ Starting Stage 1: Parse Raw Skill Rows")
    for pdf in sorted(args.input_folder.glob("*.pdf")):
        print(f"📖 Processing {pdf.name}")
        try:
            secs, rows, skills = process_pdf(pdf)
            all_sections.extend(secs)
            all_rows.extend(rows)
            all_skills.extend(skills)
        except Exception as e:
            print(f"❌ Failed to process {pdf.name}: {e}")
    print(f"-> Parsed sections: {len(all_sections)} | rows: {len(all_rows)} | skills: {len(all_skills)}")

    print("\n✅ Starting Stage 3: Normalize Skills")

    # Stage 3 normalize
    normalized = [stage3_normalize(s) for s in all_skills]
    print(f"-> Normalized skills: {len(normalized)}")

    # Age group default for position pathways
    for skill in normalized:
        cat = skill.get("skill_category") or ""
        if not skill.get("age_groups") and cat in {"Goaltending", "Defensive Tactics"}:
            skill["age_groups"] = DEFAULT_POSITION_AGES.copy()
            skill["source_type"] = "position_pathway"

    print("\n✅ Starting Stage 5: Merge & Deduplicate")
    deduped, report = deduplicate(normalized)
    print(f"-> Deduplicated {report['deduplicated']} items (final count {len(deduped)})")

    print("\n✅ Starting Stage 6: Audit")
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
