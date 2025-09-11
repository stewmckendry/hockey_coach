#!/usr/bin/env python3
"""
Hockey Dryland Videos Indexing Script

This script loads dryland video clips data and indexes it into a dedicated 
Chroma vector database collection for semantic search and retrieval.
"""
import json
import argparse
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from more_itertools import chunked
import tiktoken
from typing import Dict, List, Any, Optional
import chromadb
from chromadb.config import Settings

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from utils.chroma_utils import get_client, clear_chroma_collection

def extract_video_id(url: str) -> str | None:
    """Extract YouTube video ID from a URL safely."""
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)

    # Case 1: Standard YouTube link with ?v=abc123
    if "v" in qs:
        return qs["v"][0]

    # Case 2: Shortened youtu.be links
    if "youtu.be" in parsed.netloc:
        return parsed.path.lstrip("/")

    # Case 3: If it’s a /watch path but v= is missing
    if parsed.path.startswith("/watch") and "v" in parsed.query:
        return parsed.query.split("&")[0].replace("v=", "")

    # Fallback: Warn and return None
    print(f"⚠️ Warning: Could not extract video ID from URL: {url}")
    return None



def clip_text(clip: dict) -> str:
    """Assemble a text block for embedding."""
    parts = [
        f"Video ID: {clip.get('video_id', '')}",
        f"Segment ID: {clip.get('segment_id', '')}",
        f"Query Term: {clip.get('query_term', '')}",
        f"Title: {clip.get('title', '')}",
        f"Summary: {clip.get('summary', '')}",
        clip.get("transcript", ""),
        "Teaching Points: " + ", ".join(clip.get("teaching_points", [])),
        "Training Focus: " + ", ".join(clip.get("training_focus", [])),
        "Positions: " + ", ".join(clip.get("position") or []),
        f"Complexity: {clip.get('complexity', '')}",
        f"Duration: {clip.get('duration', '')}",
        f"Clip Type: {clip.get('clip_type', '')}",
        f"Audience: {clip.get('intended_audience', '')}",
        f"Focus: {clip.get('play_or_skill_focus', '')}",
    ]
    text = "\n".join(part for part in parts if part)
    # Ensure we don't embed extremely long documents
    if len(text) > 16000:
        text = text[:16000]
    return text


def metadata_for(clip: dict) -> dict:
    """Flatten clip fields for easier filtering/search."""
    def s(val):
        return str(val or "")

    return {
        "segment_number": s(clip.get("segment_number")),
        "segment_id": s(clip.get("segment_id")),
        "video_id": s(clip.get("video_id")),
        "title": s(clip.get("title")),
        "summary": s(clip.get("summary")),
        "query_term": s(clip.get("query_term")),
        "teaching_points": "; ".join(clip.get("teaching_points", [])),
        "training_focus": "; ".join(clip.get("training_focus", [])),
        "position": "; ".join(clip.get("position") or []),
        "complexity": s(clip.get("complexity")),
        "source": s(clip.get("source")),
        "video_url": s(clip.get("video_url")),
        "start_time": s(clip.get("start_time")),
        "end_time": s(clip.get("end_time")),
        "duration": s(clip.get("duration")),
        "clip_type": "off_ice_video",
        "type": "off_ice_video",
        "intended_audience": s(clip.get("intended_audience")),
        "play_or_skill_focus": s(clip.get("play_or_skill_focus")),
        "published_at": s(clip.get("published_at")),
        "transcript": clip.get("transcript", "")[:500],
    }

def load_clips(files: list[Path]) -> tuple[list[dict], dict[str, int]]:
    clips: list[dict] = []
    counts: dict[str, int] = {}
    for fp in files:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                items = json.load(f)
                clips.extend(items)
                counts[fp.name] = len(items)
                print(f"📂 Loaded {len(items)} clips from {fp}")
        except Exception as e:
            print(f"❌ Failed to load {fp}: {e}")
    return clips, counts


class DrylandVideosIndexer:
    def __init__(self, dry_run: bool = False, collection_name: str = "hockey_dryland_videos"):
        """Initialize the dryland videos indexer."""
        self.dry_run = dry_run
        self.collection_name = collection_name
    
    def index_videos(self, clips: List[Dict[str, Any]], clear_existing: bool = True) -> Dict[str, Any]:
        """Index all video clips into Chroma database."""
        
        print(f"\n🚀 Indexing {len(clips)} dryland video clips...")
        
        if self.dry_run:
            print("🔍 DRY RUN MODE: Analyzing indexing structure")
            
            # Show sample documents
            sample_count = min(3, len(clips))
            for i in range(sample_count):
                clip = clips[i]
                doc_content = clip_text(clip)
                metadata = metadata_for(clip)
                print(f"\n📄 Sample Document {i+1}:")
                print(f"   Title: {clip.get('title', 'Unknown')}")
                print(f"   Content length: {len(doc_content)} chars")
                print(f"   Content preview: {doc_content[:200]}...")
                print(f"   Metadata keys: {list(metadata.keys())}")
            
            return {
                "success": True,
                "dry_run": True,
                "total_clips": len(clips),
                "sample_count": sample_count
            }
        
        try:
            # Get or create dedicated dryland videos collection
            client = get_client()
            
            if clear_existing:
                try:
                    print(f"🗑️  Clearing existing dryland videos collection '{self.collection_name}'...")
                    client.delete_collection(name=self.collection_name)
                except Exception as e:
                    print(f"   (Collection may not exist yet: {e})")
            
            print(f"📚 Creating/accessing dryland videos collection: '{self.collection_name}'")
            collection = client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Hockey dryland training video clips and demonstrations"}
            )
            
            # Prepare documents for indexing
            print(f"📝 Preparing {len(clips)} documents for indexing...")
            
            documents = []
            metadatas = []
            ids = []
            video_ids = set()
            query_terms: dict[str, int] = {}
            manifest: dict[str, dict] = {}
            
            # Initialize tiktoken encoder with fallback
            enc = None
            try:
                enc = tiktoken.get_encoding("cl100k_base")
            except Exception as e:
                print(f"⚠️  Could not load tiktoken encoder (network issue): {e}")
                print("   Token counting will be skipped, but indexing will proceed")
            
            max_tokens = 0
            
            for clip in clips:
                text = clip_text(clip)
                documents.append(text)
                meta = metadata_for(clip)
                metadatas.append(meta)
                
                # Count tokens if encoder is available
                if enc:
                    try:
                        tokens = len(enc.encode(text))
                        if tokens > max_tokens:
                            max_tokens = tokens
                    except Exception:
                        pass  # Skip token counting if it fails
                vid_id = clip.get("video_id") or extract_video_id(clip.get("video_url", ""))
                seg_id = clip.get("segment_id") or f"{vid_id}_{clip.get('segment_number', '')}"
                ids.append(f"dryland-{seg_id}")
                if vid_id:
                    video_ids.add(str(vid_id))
                    m = manifest.setdefault(str(vid_id), {
                        "video_id": str(vid_id),
                        "query_term": clip.get("query_term", ""),
                        "clip_count": 0,
                        "publish_time": clip.get("published_at", "")
                    })
                    m["clip_count"] += 1
                term = clip.get("query_term")
                if term:
                    query_terms[term] = query_terms.get(term, 0) + 1
            
            if max_tokens > 0:
                print(f"📏 Largest document has {max_tokens} tokens")
            else:
                print(f"📏 Token counting skipped (encoder unavailable)")
            
            # Add to collection in chunks
            chunk_size = 100
            for i, (doc_chunk, meta_chunk, id_chunk) in enumerate(
                zip(
                    chunked(documents, chunk_size),
                    chunked(metadatas, chunk_size),
                    chunked(ids, chunk_size),
                )
            ):
                print(f"📦 Indexing chunk {i+1} with {len(doc_chunk)} clips...")
                try:
                    collection.add(documents=doc_chunk, metadatas=meta_chunk, ids=id_chunk)
                except Exception as e:
                    print(f"❌ Failed to index chunk {i+1}: {e}")
                    continue
            
            # Verify insertion
            collection_count = collection.count()
            print(f"✅ Successfully indexed {collection_count} dryland video clips")
            
            # Save manifests
            manifest_path = Path("index_manifest_dryland.csv")
            import csv
            with open(manifest_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["video_id", "query_term", "clip_count", "publish_time"])
                writer.writeheader()
                writer.writerows(manifest.values())
            
            summary = {
                "total_clips": len(clips),
                "unique_videos": len(video_ids),
                "query_terms": query_terms,
                "max_tokens": max_tokens
            }
            with open("index_summary_dryland.json", "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)
            print("✅ Wrote index summary to index_summary_dryland.json")
            
            return {
                "success": True,
                "indexed_count": collection_count,
                "unique_videos": len(video_ids),
                "query_terms": query_terms
            }
            
        except Exception as e:
            print(f"❌ Error during indexing: {e}")
            return {
                "success": False,
                "error": str(e),
                "indexed_count": 0
            }
    
    def verify_indexing(self, original_count: int) -> Dict[str, Any]:
        """Verify the indexing results with sample queries."""
        if self.dry_run:
            return {"dry_run": True, "verification_skipped": True}
        
        print(f"\n🔍 Verifying indexing results...")
        
        try:
            # Get dryland videos collection and check count
            client = get_client()
            collection = client.get_collection(name=self.collection_name)
            collection_count = collection.count()
            print(f"📊 Collection contains {collection_count} documents")
            
            # Test sample queries
            test_queries = [
                "agility drills",
                "plyometric training", 
                "stickhandling off ice",
                "balance exercises",
                "core strength hockey"
            ]
            
            verification_results = {
                "collection_count": collection_count,
                "original_count": original_count,
                "count_match": collection_count == original_count,
                "sample_queries": {}
            }
            
            for query in test_queries:
                try:
                    results = collection.query(
                        query_texts=[query],
                        n_results=3
                    )
                    
                    result_count = len(results['documents'][0]) if results['documents'] else 0
                    verification_results["sample_queries"][query] = {
                        "result_count": result_count,
                        "success": True
                    }
                    
                    if result_count > 0:
                        # Show first result preview
                        first_result = results['documents'][0][0]
                        print(f"  🔎 '{query}': {result_count} results")
                        print(f"     Top result: {first_result[:100]}...")
                    else:
                        print(f"  🔎 '{query}': No results found")
                        
                except Exception as e:
                    verification_results["sample_queries"][query] = {
                        "result_count": 0,
                        "success": False,
                        "error": str(e)
                    }
                    print(f"  ❌ '{query}': Query failed - {e}")
            
            return verification_results
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }


def main() -> None:
    parser = argparse.ArgumentParser(description="Index dryland video clips into dedicated Chroma collection")
    parser.add_argument("--input-folder", type=Path, help="Folder containing clip JSON files")
    parser.add_argument("--input-files", nargs="*", type=Path, help="Specific clip JSON files")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Analyze indexing structure without actual indexing"
    )
    parser.add_argument(
        "--clear-existing",
        action="store_true",
        help="Clear existing dryland videos collection before indexing"
    )
    parser.add_argument(
        "--collection-name",
        type=str,
        default="hockey_dryland_videos",
        help="Name for the dryland videos collection (default: hockey_dryland_videos)"
    )
    args = parser.parse_args()

    print("🏒 Hockey Dryland Videos Indexing Script")
    print("=" * 50)
    print(f"Mode: {'DRY RUN' if args.dry_run else 'FULL INDEXING'}")
    print(f"Collection: {args.collection_name}")
    print(f"Clear existing: {'YES' if args.clear_existing else 'NO'}")

    indexer = DrylandVideosIndexer(dry_run=args.dry_run, collection_name=args.collection_name)

    try:
        # Determine input files
        files: list[Path] = []
        if args.input_folder:
            files.extend(sorted(Path(args.input_folder).glob("*.json")))
        if args.input_files:
            files.extend(args.input_files)
        if not files:
            # Default to both dryland video files
            processed_dir = Path(__file__).parent.parent / "processed" / "video"
            default_files = [
                processed_dir / "video_clips_dryland.json",
                processed_dir / "video_clips_dryland_jj_sam.json"
            ]
            files = [f for f in default_files if f.exists()]
            
        if not files:
            print("❌ No input files found!")
            return 1

        print(f"📂 Input files: {[str(f) for f in files]}")

        # Load clips from all files
        clips, file_counts = load_clips(files)
        
        if not clips:
            print("❌ No clips found!")
            return 1

        # Index clips
        indexing_results = indexer.index_videos(clips, clear_existing=args.clear_existing)
        
        if not indexing_results.get("success", False):
            print(f"❌ Indexing failed: {indexing_results.get('error', 'Unknown error')}")
            return 1

        # Verify indexing
        verification_results = indexer.verify_indexing(len(clips))

        # Print final summary
        print(f"\n📋 INDEXING SUMMARY")
        print("=" * 50)

        if args.dry_run:
            print(f"Documents analyzed: {indexing_results.get('total_clips', 0)}")
            print(f"Sample documents: {indexing_results.get('sample_count', 0)}")
        else:
            print(f"Documents indexed: {indexing_results.get('indexed_count', 0)}")
            print(f"Unique videos: {indexing_results.get('unique_videos', 0)}")
            
            if verification_results.get("count_match", False):
                print("✅ Document count verification: PASSED")
            else:
                print("❌ Document count verification: FAILED")
                print(f"   Expected: {verification_results.get('original_count', 0)}")
                print(f"   Actual: {verification_results.get('collection_count', 0)}")
            
            # Show query test results
            successful_queries = sum(1 for q in verification_results.get("sample_queries", {}).values() if q.get("success", False))
            total_queries = len(verification_results.get("sample_queries", {}))
            print(f"Sample queries: {successful_queries}/{total_queries} successful")

            # Show file counts
            for fname, cnt in file_counts.items():
                print(f"✅ Indexed {cnt} clips from {fname}")
            
            # Show query term distribution
            if indexing_results.get("query_terms"):
                print("\nQuery term distribution:")
                for term, cnt in indexing_results["query_terms"].items():
                    print(f"  {term}: {cnt}")

        if args.dry_run:
            print(f"\n🔍 DRY RUN COMPLETE - Run without --dry-run to index all clips")
        else:
            print(f"\n✅ INDEXING COMPLETE")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
