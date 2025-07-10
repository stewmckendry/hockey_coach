#!/usr/bin/env python3
"""Extract off-ice training drills and guidance from Hockey Canada PDF."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

from pydantic import ValidationError

import fitz  # PyMuPDF
import yaml
from openai import OpenAI

sys.path.append(str(Path(__file__).resolve().parent.parent))

from models.off_ice import OffIceEntry

client = OpenAI()

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"
PROMPT_STAGE0 = PROMPT_DIR / "office_stage0_extract.yaml"


def load_prompt(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return str(data.get("prompt", ""))


PROMPT = load_prompt(PROMPT_STAGE0)


def _parse_json(content: str) -> list[dict] | dict | None:
    """Safely parse JSON content from an LLM response."""
    try:
        if content.startswith("```json"):
            content = content.split("```json", 1)[1].split("```", 1)[0]
        return json.loads(content)
    except Exception as e:
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


def stage0_extract_items(text: str, page_no: int) -> List[OffIceEntry]:
    user = f"Page {page_no}:\n{text}\n\nReturn JSON list."
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        temperature=0,
        messages=[{"role": "system", "content": PROMPT}, {"role": "user", "content": user}],
    )
    data = _parse_json(resp.choices[0].message.content)
    if not data:
        return []
    if isinstance(data, dict):
        data = [data]
    items: List[OffIceEntry] = []
    for d in data:
        d.setdefault("source_page", page_no)
        d.setdefault("source", "off_ice_manual_hockey_canada_level1")
        try:
            if isinstance(d.get("goals"), str):
                d["goals"] = [d["goals"]]
            items.append(OffIceEntry(**d))
        except ValidationError as e:
            print(f"❌ Validation error: {e}")
            continue
    return items


def dedupe(items: List[OffIceEntry]) -> List[OffIceEntry]:
    seen = set()
    result: List[OffIceEntry] = []
    for it in items:
        key = (it.title, it.category, it.source_page)
        if key in seen:
            continue
        seen.add(key)
        result.append(it)
    return result


def extract_pdf(pdf_path: Path) -> List[OffIceEntry]:
    doc = fitz.open(pdf_path)
    rows: List[OffIceEntry] = []
    for page_no, page in enumerate(doc, start=1):
        print(f"📄 Processing page {page_no}...")
        text = page.get_text().strip()
        if not text:
            continue
        items = stage0_extract_items(text, page_no)
        print(f"🔍 Found {len(items)} items on page {page_no}")
        rows.extend([i for i in items if i.is_valid()])
    doc.close()
    return dedupe(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract off-ice manual content")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/raw/off_ice_manual_level1.pdf"),
        help="Input PDF file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/raw/off_ice_raw.json"),
        help="Output JSON file",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print results only")
    args = parser.parse_args()

    entries = extract_pdf(args.input)

    if args.dry_run:
        print(json.dumps([e.dict() for e in entries], indent=2))
        return

    existing_raw = _load_json_if_exists(args.output)
    existing: List[OffIceEntry] = []
    for d in existing_raw:
        try:
            existing.append(OffIceEntry(**d))
        except ValidationError as e:
            print(f"❌ Validation error for existing entry: {e}")

    existing.extend(entries)
    existing = dedupe(existing)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump([e.dict() for e in existing], f, indent=2)
    print(f"✅ Wrote {len(existing)} entries to {args.output}")


if __name__ == "__main__":
    main()
