#!/usr/bin/env python3
"""Index Maple Leafs Hot Stove NHL insights into a Chroma collection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

from more_itertools import chunked
import sys

# Add repo root to PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.mcp_server.chroma_utils import get_chroma_collection


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def insight_text(insight: dict) -> str:
    """Build a single text block for embedding."""
    parts = [
        f"Speaker: {insight.get('speaker') or ''}",
        f"Quote: {insight.get('quote') or ''}",
        f"Question: {insight.get('question') or ''}",
        insight.get('context') or '',
        "Tags: " + ", ".join(insight.get('tags') or []),
        f"Takeaways (Coach): {insight.get('takeaways_for_coach') or ''}",
        f"Takeaways (Player): {insight.get('takeaways_for_player') or ''}",
    ]
    text = "\n".join([p for p in parts if p])
    return text[:16000]


def metadata_for(insight: dict) -> dict:
    """Flatten metadata for filtering/search."""

    def s(val) -> str:
        return str(val) if val is not None else ""

    return {
        "speaker": s(insight.get("speaker")),
        "tags": "; ".join(insight.get("tags") or []),
        "source_url": s(insight.get("source_url")),
        "source_article": s(insight.get("source_article")),
        "source_type": s(insight.get("source_type")),
        "published_date": s(insight.get("published_date")),
        "author": s(insight.get("author")),
        "question": s(insight.get("question")),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Index NHL insights into Chroma")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/processed/mlhs_insights.json"),
        help="Path to mlhs_insights.json",
    )
    parser.add_argument(
        "--chunk-size", type=int, default=100, help="Number of insights per batch"
    )
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    collection = get_chroma_collection()
    existing_ids = set(collection.get()["ids"])

    docs: List[str] = []
    metas: List[dict] = []
    ids: List[str] = []

    for ins in data:
        doc_id = f"insight-{ins.get('id')}"
        if doc_id in existing_ids:
            continue
        docs.append(insight_text(ins))
        metas.append(metadata_for(ins))
        ids.append(doc_id)

    if not docs:
        print("No new insights to index")
        return

    for i, (d_chunk, m_chunk, id_chunk) in enumerate(
        zip(chunked(docs, args.chunk_size), chunked(metas, args.chunk_size), chunked(ids, args.chunk_size))
    ):
        print(f"📦 Indexing chunk {i+1} with {len(d_chunk)} insights...")
        try:
            collection.add(documents=d_chunk, metadatas=m_chunk, ids=id_chunk)
        except Exception as e:
            print(f"❌ Failed to index chunk {i+1}: {e}")

    print("Count:", collection.count())
    print(f"✅ Indexed {len(docs)} insights into Chroma")


if __name__ == "__main__":
    main()
