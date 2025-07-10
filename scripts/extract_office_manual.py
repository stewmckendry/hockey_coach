#!/usr/bin/env python3
"""Extract off-ice training drills and guidance from Hockey Canada PDF."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict

import re
from difflib import SequenceMatcher

from pydantic import ValidationError

import fitz  # PyMuPDF
import yaml
from openai import OpenAI

sys.path.append(str(Path(__file__).resolve().parent.parent))

from models.off_ice import OffIceEntry
from models.enriched_off_ice import EnrichedOffIceEntry

client = OpenAI()

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"
PROMPT_STAGE0 = PROMPT_DIR / "office_stage0_extract.yaml"
PROMPT_STAGE1 = PROMPT_DIR / "office_stage1_merge_enrich.yaml"


def load_prompt(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return str(data.get("prompt", ""))


PROMPT = load_prompt(PROMPT_STAGE0)
PROMPT_MERGE = load_prompt(PROMPT_STAGE1)


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


def _norm(text: str) -> str:
    text = re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
    return text


def group_similar(items: List[OffIceEntry]) -> List[List[OffIceEntry]]:
    """Group entries with fuzzy-matched titles for merging."""
    groups: List[List[OffIceEntry]] = []
    used: set[int] = set()
    titles = [_norm(it.title) for it in items]
    for i, it in enumerate(items):
        if i in used:
            continue
        grp = [it]
        used.add(i)
        for j in range(i + 1, len(items)):
            if j in used:
                continue
            if SequenceMatcher(None, titles[i], titles[j]).ratio() >= 0.85:
                grp.append(items[j])
                used.add(j)
        groups.append(grp)
    return groups


def merge_and_enrich(group: List[OffIceEntry]) -> EnrichedOffIceEntry | None:
    """Use the LLM to merge similar entries and enrich metadata."""
    user = json.dumps([e.model_dump() for e in group], indent=2)
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        temperature=0,
        messages=[{"role": "system", "content": PROMPT_MERGE}, {"role": "user", "content": user}],
    )
    data = _parse_json(resp.choices[0].message.content)
    if isinstance(data, dict):
        data.setdefault("source_pages", sorted({e.source_page for e in group}))
        data.setdefault("source", group[0].source)
        try:
            return EnrichedOffIceEntry(**data)
        except ValidationError as e:
            print(f"❌ Validation error: {e}")
    return None


def extract_pdf(pdf_path: Path) -> List[OffIceEntry]:
    doc = fitz.open(pdf_path)
    rows: List[OffIceEntry] = []
    for page_no, page in enumerate(doc, start=1):
        text = page.get_text().strip()
        if not text:
            continue
        items = stage0_extract_items(text, page_no)
        rows.extend([i for i in items if i.is_valid()])
    doc.close()
    return dedupe(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Process off-ice manual entries with optional PDF extraction"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/raw/off_ice_raw.json"),
        help="Input JSON file from stage 0",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/off_ice_enriched.json"),
        help="Output enriched JSON file",
    )
    parser.add_argument(
        "--pdf",
        type=Path,
        help="Optional PDF path to re-run stage 0 extraction",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print results only")
    args = parser.parse_args()

    raw_entries: List[OffIceEntry] = []
    if args.pdf:
        print(f"📖 Extracting from {args.pdf}")
        raw_entries = extract_pdf(args.pdf)
        args.input.parent.mkdir(parents=True, exist_ok=True)
        with open(args.input, "w", encoding="utf-8") as f:
            json.dump([e.model_dump() for e in raw_entries], f, indent=2)
        print(f"✅ Wrote {len(raw_entries)} raw entries to {args.input}")
    else:
        for d in _load_json_if_exists(args.input):
            try:
                raw_entries.append(OffIceEntry(**d))
            except ValidationError as e:
                print(f"❌ Invalid raw entry: {e}")

    if not raw_entries:
        print("❌ No entries to process")
        return

    groups = group_similar(raw_entries)
    enriched: List[EnrichedOffIceEntry] = []
    for grp in groups:
        item = merge_and_enrich(grp)
        if item:
            enriched.append(item)

    if args.dry_run:
        print(json.dumps([e.model_dump() for e in enriched], indent=2))
        return

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump([e.model_dump() for e in enriched], f, indent=2)
    print(f"✅ Wrote {len(enriched)} enriched entries to {args.output}")


if __name__ == "__main__":
    main()
