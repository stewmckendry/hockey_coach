#!/usr/bin/env python3
"""Extract LTAD skill guidance from Hockey Canada PDFs."""

from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import List

import fitz  # PyMuPDF
import openai
import yaml
from pydantic import BaseModel


class LTADSkill(BaseModel):
    age_group: str | None = None
    ltad_stage: str | None = None
    position: List[str] | None = None
    skill_category: str | None = None
    skill_name: str | None = None
    teaching_notes: str | None = None
    season_month: str | None = None
    source: str


def chunk_pages(pages: List[str], size: int = 2) -> List[str]:
    for i in range(0, len(pages), size):
        yield "\n".join(pages[i : i + size])


DEFAULT_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "ltad_extract_prompt.yaml"


def load_prompt(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return str(data.get("prompt", ""))


PROMPT = load_prompt(DEFAULT_PROMPT_PATH)


def parse_with_llm(text: str, source: str) -> List[dict]:
    """Use OpenAI to convert text into LTADSkill dicts."""
    system = PROMPT
    user = f"Source: {source}\n\n{text}\n\nReturn JSON list."
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0125",
        temperature=0,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
    )
    content = resp.choices[0].message.content
    try:
        data = json.loads(content)
        if isinstance(data, dict):
            data = [data]
        return data
    except Exception as e:
        print(f"❌ JSON parse failed: {e}")
        return []


def extract_pdf(pdf_path: Path) -> List[dict]:
    """Extract skills from a single PDF file."""
    doc = fitz.open(pdf_path)
    pages = [page.get_text() for page in doc]
    doc.close()

    results: List[dict] = []
    for chunk in chunk_pages(pages):
        items = parse_with_llm(chunk, pdf_path.name)
        for it in items:
            it["source"] = pdf_path.name
            try:
                results.append(LTADSkill(**it).model_dump())
            except Exception as e:
                print(f"❌ Invalid item in {pdf_path.name}: {e}")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract LTAD skills from PDFs")
    parser.add_argument("--input-folder", type=Path, default=Path("data/raw/ltad"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/ltad_skills_raw.json"),
        help="Output JSON file",
    )
    parser.add_argument(
        "--prompt-file",
        type=Path,
        default=DEFAULT_PROMPT_PATH,
        help="YAML file with LLM prompt",
    )
    args = parser.parse_args()

    global PROMPT
    PROMPT = load_prompt(args.prompt_file)

    skills: List[dict] = []
    for pdf in sorted(args.input_folder.glob("*.pdf")):
        print(f"📖 Processing {pdf.name}")
        try:
            skills.extend(extract_pdf(pdf))
        except Exception as e:
            print(f"❌ Failed to process {pdf.name}: {e}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(skills, f, indent=2)
    print(f"✅ Wrote {len(skills)} skills to {args.output}")


if __name__ == "__main__":
    main()
