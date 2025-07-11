#!/usr/bin/env python3
"""Index conduct entries into a Chroma collection."""

from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.mcp_server.chroma_utils import get_client, _embed

COLLECTION_NAME = "conduct_index"


def doc_text(entry: dict) -> str:
    return f"{entry.get('title','')}\n{entry.get('content','')}"[:16000]


def metadata_for(entry: dict) -> dict:
    def s(val) -> str:
        return val if isinstance(val, str) else ""
    return {
        "role": s(entry.get("role")),
        "topic": s(entry.get("topic")),
        "document_type": s(entry.get("document_type")),
        "source": s(entry.get("source")),
        "page": str(entry.get("page") or ""),
    }


def clear_collection(coll) -> None:
    ids = coll.get().get("ids", [])
    if ids:
        coll.delete(ids=ids)
        print(f"🧹 Cleared {len(ids)} documents")


def main() -> None:
    parser = argparse.ArgumentParser(description="Index conduct entries")
    parser.add_argument("--input", type=Path, default=Path("data/processed/conduct_enriched.json"))
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    client = get_client()
    collection = client.get_or_create_collection(COLLECTION_NAME, embedding_function=_embed)
    clear_collection(collection)

    docs = [doc_text(e) for e in data]
    metas = [metadata_for(e) for e in data]
    ids = [f"conduct-{i}" for i in range(len(data))]

    if docs:
        collection.add(documents=docs, metadatas=metas, ids=ids)
        print("Count:", collection.count())
        print(f"✅ Indexed {len(docs)} conduct entries into Chroma")
    else:
        print("No entries to index")


if __name__ == "__main__":
    main()
