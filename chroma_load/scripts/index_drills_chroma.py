# scripts/index_drills_chroma.py
import os
import json
import argparse
from pathlib import Path
from typing import List
from more_itertools import chunked
import tiktoken

import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from dotenv import load_dotenv

load_dotenv()

# Setup Chroma client
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))  # Go up to project root
from utils.chroma_utils import get_chroma_collection, clear_chroma_collection

# === Helper functions ===
def drill_text(drill: dict) -> str:
    def join_list(label, items):
        if isinstance(items, list):
            return f"{label}: {', '.join(str(item) for item in items)}" if items else ""
        elif isinstance(items, str) and items:
            return f"{label}: {items}"
        return ""

    parts = [
        f"Title: {drill.get('title', '')}",
        f"Summary: {drill.get('summary', '')}",
        f"Instructions: {drill.get('instructions', '')}",
        join_list("Teaching Points", drill.get("teaching_points", [])),
        join_list("Equipment", drill.get("equipment", [])),
        join_list("Skills", drill.get("skills", [])),
        join_list("Sub-Skills", drill.get("sub_skills", [])),
        join_list("Positions", drill.get("positions", [])),
        f"Complexity: {drill.get('complexity', '')}",
        f"Source: {drill.get('source', '')}",
        f"URL: {drill.get('url', '')}",
    ]
    return "\n".join(part for part in parts if part)

def safe_str(value) -> str:
    return value if isinstance(value, str) else ""

def safe_list_to_str(value) -> str:
    """Convert list to semicolon-separated string, or return string as-is."""
    if isinstance(value, list):
        return "; ".join(str(item) for item in value)
    elif isinstance(value, str):
        return value
    return ""

def metadata_for(drill: dict) -> dict:
    return {
        "title": safe_str(drill.get("title")),
        "summary": safe_str(drill.get("summary")),
        "instructions": safe_str(drill.get("instructions")),
        "teaching_points": safe_list_to_str(drill.get("teaching_points", [])),
        "equipment": safe_list_to_str(drill.get("equipment", [])),
        "skills": safe_list_to_str(drill.get("skills", [])),
        "sub_skills": safe_list_to_str(drill.get("sub_skills", [])),
        "positions": safe_list_to_str(drill.get("positions", [])),
        "complexity": safe_str(drill.get("complexity")),
        "source": safe_str(drill.get("source")),
        "url": safe_str(drill.get("url")),
    }

def main():
    parser = argparse.ArgumentParser(description="Index hockey drills into Chroma vector database")
    parser.add_argument(
        "--clear-drills",
        action="store_true",
        help="Clear existing drill documents (with 'drill-' prefix) before indexing"
    )
    parser.add_argument(
        "--input-file",
        help="Path to specific drill JSON file to index (default: use processed/drills.json)"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=100,
        help="Number of drills per indexing chunk (default: 100)"
    )
    
    args = parser.parse_args()
    chunk_size = args.chunk_size
    enc = tiktoken.get_encoding("cl100k_base")
    
    # Clear existing drill documents if requested
    if args.clear_drills:
        print("🧹 Clearing existing drill documents...")
        clear_chroma_collection(mode="type", prefix="drill-")
    
    collection = get_chroma_collection()
    
    # Determine input file
    if args.input_file:
        data_path = Path(args.input_file)
    else:
        # Look for the most recent enriched drills file
        processed_dir = Path(__file__).parent.parent / "processed"
        enriched_files = list(processed_dir.glob("enriched_drills_*.json"))
        
        if enriched_files:
            # Use the most recent enriched file
            data_path = max(enriched_files, key=lambda p: p.stat().st_mtime)
            print(f"📂 Using most recent enriched drills file: {data_path}")
        else:
            # Fall back to legacy drills.json
            data_path = processed_dir / "drills.json"
            print(f"📂 Using legacy drills file: {data_path}")
    
    if not data_path.exists():
        print(f"❌ Data file not found: {data_path}")
        print("   Run the drill enrichment script first or specify --input-file")
        return 1
        
    # Load drill data
    with open(data_path, "r") as f:
        data = json.load(f)
    
    print(f"📚 Loaded {len(data)} drills from {data_path}")
    
    # === Build text chunks to embed ===
    docs = [drill_text(d) for d in data]
    metadatas = [metadata_for(d) for d in data]
    ids = [f"drill-{i}" for i in range(len(data))]
    
    # Check token counts
    max_tokens = 0
    for doc in docs:
        tokens = len(enc.encode(doc))
        if tokens > max_tokens:
            max_tokens = tokens
    
    print(f"📏 Largest document has {max_tokens} tokens")
    
    # Index drills in chunks
    if docs:
        for i, (doc_chunk, meta_chunk, id_chunk) in enumerate(
            zip(
                chunked(docs, chunk_size),
                chunked(metadatas, chunk_size),
                chunked(ids, chunk_size),
            )
        ):
            print(f"📦 Indexing chunk {i+1} with {len(doc_chunk)} drills...")
            try:
                collection.add(documents=doc_chunk, metadatas=meta_chunk, ids=id_chunk)
            except Exception as e:
                print(f"❌ Failed to index chunk {i+1}: {e}")
                continue
    
    print("Count:", collection.count())
    
    # Show sample results
    results = collection.get(include=["documents", "metadatas"], limit=5)
    for i, doc in enumerate(results["documents"]):
        print(f"Doc {i+1}:")
        print("  ID:", results["ids"][i])  # this is always included even if not in `include`
        print("  Title:", results["metadatas"][i].get("title"))
        print("  Text:", doc[:100], "...")
        
    print(f"✅ Indexed {len(docs)} drills into Chroma")

if __name__ == "__main__":
    import sys
    sys.exit(main())
