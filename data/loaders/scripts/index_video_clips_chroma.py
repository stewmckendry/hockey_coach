#!/usr/bin/env python3
"""
Hockey Video Clips Indexing Script

This script loads hockey video clips data and indexes it into Chroma vector database
for semantic search and retrieval.
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
from utils.chroma_utils import get_client

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
        "Skills: " + ", ".join(clip.get("hockey_skills", [])),
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
        "hockey_skills": "; ".join(clip.get("hockey_skills", [])),
        "position": "; ".join(clip.get("position") or []),
        "complexity": s(clip.get("complexity")),
        "source": s(clip.get("source")),
        "video_url": s(clip.get("video_url")),
        "start_time": s(clip.get("start_time")),
        "end_time": s(clip.get("end_time")),
        "duration": s(clip.get("duration")),
        "clip_type": s(clip.get("clip_type")),
        "intended_audience": s(clip.get("intended_audience")),
        "play_or_skill_focus": s(clip.get("play_or_skill_focus")),
        "published_at": s(clip.get("published_at")),
        "transcript": clip.get("transcript", "")[:500],
    }

class VideoClipsIndexer:
    def __init__(self, dry_run: bool = False, collection_name: str = "hockey_videos"):
        """Initialize the video clips indexer."""
        self.dry_run = dry_run
        self.collection_name = collection_name

    def load_clips(self, files: List[Path]) -> tuple[List[dict], Dict[str, int]]:
        """Load video clips from JSON files."""
        clips: List[dict] = []
        counts: Dict[str, int] = {}
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

    def find_video_clips_file(self, input_file: Optional[Path] = None) -> Path:
        """Find the video clips file to index."""
        if input_file is not None:
            if input_file.exists():
                return input_file
            else:
                # Try relative to processed directory
                processed_dir = Path(__file__).parent.parent / "processed"
                full_path = processed_dir / input_file
                if full_path.exists():
                    return full_path
                else:
                    raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Default to video_clips.json in processed/video directory
        default_file = Path(__file__).parent.parent / "processed" / "video" / "video_clips.json"
        if default_file.exists():
            return default_file
        else:
            raise FileNotFoundError(f"Default video clips file not found: {default_file}")

    def index_videos(self, clips: List[Dict[str, Any]], clear_existing: bool = True, chunk_size: int = 100) -> Dict[str, Any]:
        """Index all video clips into Chroma database."""
        
        print(f"\n🚀 Indexing {len(clips)} video clips...")
        
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
                print(f"   Video ID: {clip.get('video_id', 'Unknown')}")
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
            # Get or create dedicated video clips collection
            client = get_client()
            
            if clear_existing:
                try:
                    print(f"🗑️  Clearing existing video clips collection '{self.collection_name}'...")
                    client.delete_collection(name=self.collection_name)
                except Exception as e:
                    print(f"   (Collection may not exist yet: {e})")
            
            print(f"📚 Creating/accessing video clips collection: '{self.collection_name}'")
            collection = client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Hockey video clips and instructional content"}
            )
            
            # Prepare documents for indexing
            print(f"📝 Preparing {len(clips)} documents for indexing...")
            
            docs, metadatas, ids = [], [], []
            video_ids = set()
            query_terms: Dict[str, int] = {}
            manifest: Dict[str, Dict] = {}
            max_tokens = 0
            enc = tiktoken.get_encoding("cl100k_base")

            for clip in clips:
                text = clip_text(clip)
                docs.append(text)
                meta = metadata_for(clip)
                metadatas.append(meta)
                tokens = len(enc.encode(text))
                if tokens > max_tokens:
                    max_tokens = tokens
                vid_id = clip.get("video_id") or extract_video_id(clip.get("video_url", ""))
                seg_id = clip.get("segment_id") or f"{vid_id}_{clip.get('segment_number', '')}"
                ids.append(f"video-{seg_id}")
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

            if docs:
                print(f"📏 Largest document has {max_tokens} tokens")
                for i, (doc_chunk, meta_chunk, id_chunk) in enumerate(
                    zip(
                        chunked(docs, chunk_size),
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
                print(f"✅ Successfully indexed {collection_count} video clips")
                
                return {
                    "success": True,
                    "indexed_count": collection_count,
                    "video_ids": video_ids,
                    "query_terms": query_terms,
                    "manifest": manifest
                }
            else:
                print("No clips to index")
                return {
                    "success": False,
                    "error": "No clips found to index",
                    "indexed_count": 0
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
            # Get video clips collection and check count
            client = get_client()
            collection = client.get_collection(name=self.collection_name)
            collection_count = collection.count()
            print(f"📊 Collection contains {collection_count} documents")
            
            # Test sample queries
            test_queries = [
                "goalie training drills",
                "skating techniques", 
                "passing skills",
                "shooting practice",
                "defensive positioning"
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


def main():
    parser = argparse.ArgumentParser(description="Index hockey video clips into Chroma database")
    parser.add_argument(
        "--input",
        type=Path,
        help="Input video clips file (default: processed/video/video_clips.json)"
    )
    parser.add_argument(
        "--input-folder", 
        type=Path, 
        help="Folder containing clip JSON files"
    )
    parser.add_argument(
        "--input-files", 
        nargs="*", 
        type=Path, 
        help="Specific clip JSON files"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=100,
        help="Number of clips per indexing chunk",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Analyze indexing structure without actual indexing"
    )
    parser.add_argument(
        "--clear-videos",
        action="store_true",
        help="Clear existing video clips collection before indexing"
    )
    parser.add_argument(
        "--collection-name",
        type=str,
        default="hockey_videos",
        help="Name for the video clips collection (default: hockey_videos)"
    )
    
    args = parser.parse_args()
    
    print("🏒 Hockey Video Clips Indexing Script")
    print("=" * 50)
    print(f"Mode: {'DRY RUN' if args.dry_run else 'FULL INDEXING'}")
    print(f"Collection: {args.collection_name}")
    print(f"Clear existing: {'YES' if args.clear_videos else 'NO'}")
    
    indexer = VideoClipsIndexer(dry_run=args.dry_run, collection_name=args.collection_name)
    
    try:
        # Determine input files
        files: List[Path] = []
        if args.input_folder:
            files.extend(sorted(Path(args.input_folder).glob("*.json")))
        if args.input_files:
            files.extend(args.input_files)
        if args.input:
            files.append(args.input)
        if not files:
            # Use default file
            default_file = indexer.find_video_clips_file()
            files.append(default_file)
        
        print(f"📂 Input files: {[str(f) for f in files]}")
        
        # Load video clips
        clips, file_counts = indexer.load_clips(files)
        
        if not clips:
            print("❌ No video clips found!")
            return 1
        
        # Index video clips
        indexing_results = indexer.index_videos(clips, clear_existing=args.clear_videos, chunk_size=args.chunk_size)
        
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
            
            for fname, cnt in file_counts.items():
                print(f"✅ Indexed {cnt} clips from {fname}")
            
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
            
            # Show video distribution if available
            video_ids = indexing_results.get("video_ids", set())
            query_terms = indexing_results.get("query_terms", {})
            if video_ids:
                print(f"Unique video IDs: {len(video_ids)}")
            if query_terms:
                print("Query term distribution:")
                for term, cnt in query_terms.items():
                    print(f"  {term}: {cnt}")
        
        if args.dry_run:
            print(f"\n🔍 DRY RUN COMPLETE - Run without --dry-run to index all video clips")
        else:
            print(f"\n✅ INDEXING COMPLETE")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
