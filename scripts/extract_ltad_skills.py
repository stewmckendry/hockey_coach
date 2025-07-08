#!/usr/bin/env python3
"""3-stage pipeline to extract LTAD skills from Hockey Canada PDFs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

import fitz  # PyMuPDF
import yaml
from openai import OpenAI

sys.path.append(str(Path(__file__).resolve().parent.parent))

from models.ltad import LTADSkill

client = OpenAI()


# --- Prompt loading helpers -------------------------------------------------
PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"


def load_prompt(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return str(data.get("prompt", ""))


PROMPT_STAGE0 = load_prompt(PROMPT_DIR / "ltad_stage0_extract.yaml")
PROMPT_STAGE1 = load_prompt(PROMPT_DIR / "ltad_stage1_parse_skills.yaml")
PROMPT_STAGE2 = load_prompt(PROMPT_DIR / "ltad_stage2_enrich_skills.yaml")


# --- LLM utilities ----------------------------------------------------------

def _parse_json(content: str) -> list[dict] | dict | None:
    """Safely parse JSON content from an LLM response."""
    try:
        return json.loads(content)
    except Exception as e:
        print(f"❌ JSON parse failed: {e}")
        return None


def stage0_extract_relevant_sections(text_chunk: str, source: str, page_number: int) -> List[Dict[str, Any]]:
    """Return relevant skill sections from a PDF page."""
    user = f"Source: {source}\nPage: {page_number}\n\n{text_chunk}\n\nReturn JSON list."
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
        d.setdefault("page_number", page_number)
    return data  # type: ignore[return-value]


def stage1_parse_raw_skills(section: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse raw bullet lines from a section into skill rows."""
    text = section.get("raw_text", "")
    user = f"Section: {section.get('section_title','')}\n\n{text}\n\nReturn JSON list."
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
            "section_title": section.get("section_title"),
        })
    return data  # type: ignore[return-value]


def stage2_enrich_to_ltad_skill(raw_row: Dict[str, Any]) -> Dict[str, Any] | None:
    """Convert a raw skill row into a structured LTADSkill object."""
    user = f"Raw Skill Row:\n{json.dumps(raw_row, indent=2)}\n\nReturn a JSON object."
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        temperature=0,
        messages=[{"role": "system", "content": PROMPT_STAGE2}, {"role": "user", "content": user}],
    )
    data = _parse_json(resp.choices[0].message.content)
    if not isinstance(data, dict):
        return None
    data.setdefault("source", raw_row.get("source"))
    try:
        return LTADSkill(**data).model_dump()
    except Exception as e:
        print(f"❌ Invalid LTADSkill: {e}")
        return None


# --- PDF processing ---------------------------------------------------------

def extract_pdf(pdf_path: Path) -> tuple[list[dict], list[dict], list[dict]]:
    """Run all stages for a single PDF and return (sections, raw_rows, skills)."""
    doc = fitz.open(pdf_path)
    sections: list[dict] = []
    raw_rows: list[dict] = []
    skills: list[dict] = []

    for page_no, page in enumerate(doc, start=1):
        text = page.get_text()
        sec_blocks = stage0_extract_relevant_sections(text, pdf_path.name, page_no)
        sections.extend(sec_blocks)
        for sec in sec_blocks:
            rows = stage1_parse_raw_skills(sec)
            raw_rows.extend(rows)
            for row in rows:
                skill = stage2_enrich_to_ltad_skill(row)
                if skill:
                    skills.append(skill)
    doc.close()
    return sections, raw_rows, skills


# --- CLI -------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Extract LTAD skills from PDFs via 3-stage pipeline")
    parser.add_argument("--input-folder", type=Path, default=Path("data/raw/ltad"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/ltad_skills_raw.json"),
        help="Output JSON file",
    )
    args = parser.parse_args()

    all_sections: list[dict] = []
    all_rows: list[dict] = []
    all_skills: list[dict] = []

    for pdf in sorted(args.input_folder.glob("*.pdf")):
        print(f"📖 Processing {pdf.name}")
        try:
            secs, rows, skills = extract_pdf(pdf)
            all_sections.extend(secs)
            all_rows.extend(rows)
            all_skills.extend(skills)
        except Exception as e:
            print(f"❌ Failed to process {pdf.name}: {e}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(all_skills, f, indent=2)
    print(f"✅ Wrote {len(all_skills)} skills to {args.output}")

    rows_path = args.output.with_name("ltad_raw_skill_rows.json")
    with open(rows_path, "w", encoding="utf-8") as f:
        json.dump(all_rows, f, indent=2)
    sections_path = args.output.with_name("ltad_sections.json")
    with open(sections_path, "w", encoding="utf-8") as f:
        json.dump(all_sections, f, indent=2)
    print(f"✅ Wrote debug artifacts to {sections_path} and {rows_path}")


if __name__ == "__main__":
    main()
