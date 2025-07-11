#!/usr/bin/env python3
"""Extract and enrich hockey code of conduct entries."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import List, Dict, Any

import fitz
from bs4 import BeautifulSoup
import yaml
from openai import OpenAI

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

from models.conduct import ConductEntry

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"


def load_prompt(name: str) -> str:
    path = PROMPT_DIR / name
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return str(data.get("prompt", ""))


PROMPT_STAGE0 = (
    "You analyze hockey policy text and extract individual rules, code of conduct statements, or definitions."
    " Return a JSON list where each item has: title, content. Keep content concise but clear."
)
PROMPT_STAGE1 = load_prompt("conduct_stage1_enrich.yaml")

client = OpenAI()


def _parse_json(content: str) -> Any:
    try:
        if content.startswith("```json"):
            content = content.split("```json", 1)[1].split("```", 1)[0]
        return json.loads(content)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------

def extract_batch(pages: List[tuple[int, str]], source: str) -> List[dict]:
    user_blocks = [f"Page {p}:\n{text}" for p, text in pages]
    user = "\n\n".join(user_blocks) + "\n\nReturn JSON list."
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
        d.setdefault("page", pages[0][0])
        d.setdefault("source", source)
    return data  # type: ignore[return-value]


def extract_pdf(path: Path, batch_size: int = 3) -> List[dict]:
    doc = fitz.open(path)
    entries: List[dict] = []
    batch: List[tuple[int, str]] = []
    for page_no, page in enumerate(doc, start=1):
        text = page.get_text().strip()
        if not text:
            continue
        batch.append((page_no, text))
        if len(batch) >= batch_size:
            print(f"✨ Extracting policy entries from pages {batch[0][0]}–{batch[-1][0]}...")
            entries.extend(extract_batch(batch, path.name))
            batch = []
    if batch:
        print(f"✨ Extracting policy entries from pages {batch[0][0]}–{batch[-1][0]}...")
        entries.extend(extract_batch(batch, path.name))
    doc.close()
    return entries


def extract_html(path: Path, chunk_words: int = 150) -> List[dict]:
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator="\n")
    words = []
    entries: List[dict] = []
    start_idx = 0
    for word in text.split():
        words.append(word)
        if len(words) >= chunk_words:
            chunk = " ".join(words)
            pages = [(start_idx // chunk_words + 1, chunk)]
            entries.extend(extract_batch(pages, path.name))
            words = []
            start_idx += chunk_words
    if words:
        chunk = " ".join(words)
        pages = [(start_idx // chunk_words + 1, chunk)]
        entries.extend(extract_batch(pages, path.name))
    return entries


# ---------------------------------------------------------------------------
# Enrichment
# ---------------------------------------------------------------------------

def enrich_batch(rows: List[dict]) -> List[dict]:
    user = json.dumps(rows, indent=2)
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
    return data  # type: ignore[return-value]


def normalize(entry: dict) -> dict:
    defaults = {
        "title": "",
        "content": "",
        "role": None,
        "topic": None,
        "document_type": None,
        "source": entry.get("source"),
        "page": entry.get("page"),
    }
    norm = {**defaults, **entry}
    return ConductEntry(**norm).model_dump()


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def process_file(path: Path, batch_size: int) -> List[dict]:
    print(f"📖 Reading file: {path.name}")
    if path.suffix.lower() == ".pdf":
        raw_entries = extract_pdf(path, batch_size)
    else:
        raw_entries = extract_html(path)
    print(f"🔹 Extracted {len(raw_entries)} raw entries")

    enriched: List[dict] = []
    for i in range(0, len(raw_entries), 8):
        batch = raw_entries[i : i + 8]
        print(f"🔍 Enriching entry batch {i//8 + 1}/{(len(raw_entries)-1)//8 + 1}...")
        enriched.extend(enrich_batch(batch))
    normalized = [normalize(e) for e in enriched if e]
    return normalized


def audit(entries: List[dict]) -> Dict[str, Any]:
    audits = []
    required = ["title", "content", "role", "topic", "document_type", "source"]
    for e in entries:
        missing = [f for f in required if not e.get(f)]
        audits.append({"title": e.get("title"), "missing": missing})
    coverage = sum(1 for a in audits if not a["missing"]) / len(audits) if audits else 0
    return {"coverage": coverage, "audits": audits}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate conduct index")
    parser.add_argument("--input-folder", type=Path, default=Path("data/raw/rules"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/conduct_enriched.json"))
    parser.add_argument("--batch-pages", type=int, default=3)
    args = parser.parse_args()

    start = time.perf_counter()
    all_entries: List[dict] = []
    for f in sorted(args.input_folder.iterdir()):
        if not f.is_file():
            continue
        entries = process_file(f, args.batch_pages)
        all_entries.extend(entries)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(all_entries, f, indent=2)

    audit_report = audit(all_entries)
    audit_path = args.output.with_name("conduct_audit.json")
    with open(audit_path, "w", encoding="utf-8") as f:
        json.dump(audit_report, f, indent=2)

    duration = time.perf_counter() - start
    print(f"✅ Final enriched entries: {len(all_entries)}")
    print(f"⏱️ Took {duration:.1f}s")


if __name__ == "__main__":
    main()
