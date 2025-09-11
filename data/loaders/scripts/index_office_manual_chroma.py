#!/usr/bin/env python3
"""Index enriched off-ice manual entries into a Chroma collection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

import sys

# Add repo root to PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from utils.chroma_utils import get_client, clear_chroma_collection


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def doc_text(entry: dict) -> str:
    """Create document text for enriched off-ice workout."""
    parts = [
        f"Title: {entry.get('title', '')}",
        f"Category: {entry.get('category', '')}",
        f"Summary: {entry.get('summary', '')}",
        f"Instructions: {entry.get('instructions', '')}",
        f"Teaching Points: {'; '.join(entry.get('teaching_points', []))}",
        f"Equipment: {entry.get('equipment', '')}",
        f"Complexity: {entry.get('complexity', '')}",
        f"Source: {entry.get('source', '')}",
    ]
    text = "\n".join([p for p in parts if p and not p.endswith(': ') and not p.endswith(': N/A')])
    return text[:16000]

def metadata_for(entry: dict) -> dict:
    """Create metadata for enriched off-ice workout."""
    def safe_str(value) -> str:
        if value is None:
            return ""
        if isinstance(value, list):
            return "; ".join(str(v) for v in value)
        return str(value)

    return {
        "title": safe_str(entry.get("title")),
        "category": safe_str(entry.get("category")),
        "summary": safe_str(entry.get("summary")),
        "instructions": safe_str(entry.get("instructions")),
        "teaching_points": safe_str(entry.get("teaching_points")),
        "equipment": safe_str(entry.get("equipment")),
        "complexity": safe_str(entry.get("complexity")),
        "source": safe_str(entry.get("source", "off_ice_manual_hockey_canada_level1")),
        "age_recommendation": safe_str(entry.get("age_recommendation")),
        "source_page": safe_str(entry.get("source_page")),
        "document_type": "off_ice_workout"
    }


# ---------------------------------------------------------------------------
# Indexer Class
# ---------------------------------------------------------------------------

class DrylandIndexer:
    def __init__(self, dry_run: bool = False, collection_name: str = "hockey_dryland"):
        """Initialize the dryland indexer."""
        self.dry_run = dry_run
        self.collection_name = collection_name
    
    def index_workouts(self, workouts: List[dict], clear_existing: bool = True) -> dict:
        """Index all workouts into Chroma database."""
        
        print(f"\n🚀 Indexing {len(workouts)} dryland workouts...")
        
        if self.dry_run:
            print("🔍 DRY RUN MODE: Analyzing indexing structure")
            
            # Show sample documents
            sample_count = min(3, len(workouts))
            for i in range(sample_count):
                workout = workouts[i]
                doc_content = doc_text(workout)
                metadata = metadata_for(workout)
                print(f"\n📄 Sample Document {i+1}:")
                print(f"   Workout: {workout.get('title', 'Unknown')}")
                print(f"   Content length: {len(doc_content)} chars")
                print(f"   Content preview: {doc_content[:200]}...")
                print(f"   Metadata keys: {list(metadata.keys())}")
            
            return {
                "success": True,
                "dry_run": True,
                "total_workouts": len(workouts),
                "sample_count": sample_count
            }
        
        try:
            # Get or create dedicated dryland collection
            client = get_client()
            
            if clear_existing:
                try:
                    print(f"🗑️  Clearing existing dryland collection '{self.collection_name}'...")
                    client.delete_collection(name=self.collection_name)
                except Exception as e:
                    print(f"   (Collection may not exist yet: {e})")
            
            print(f"📚 Creating/accessing dryland collection: '{self.collection_name}'")
            collection = client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Hockey dryland and off-ice training exercises"}
            )
            
            # Prepare documents for indexing
            print(f"📝 Preparing {len(workouts)} documents for indexing...")
            
            documents = []
            metadatas = []
            ids = []
            
            for i, workout in enumerate(workouts):
                # Create document content
                doc_content = doc_text(workout)
                documents.append(doc_content)
                
                # Create metadata
                metadata = metadata_for(workout)
                metadatas.append(metadata)
                
                # Create unique ID
                workout_title = workout.get('title', f'workout_{i}')
                safe_title = workout_title.lower().replace(' ', '_').replace('-', '_')
                doc_id = f"dryland_{i}_{safe_title}"
                ids.append(doc_id)
            
            # Add to collection
            print(f"📊 Adding documents to Chroma collection...")
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            # Verify insertion
            collection_count = collection.count()
            print(f"✅ Successfully indexed {collection_count} dryland workouts")
            
            return {
                "success": True,
                "indexed_count": collection_count
            }
            
        except Exception as e:
            print(f"❌ Error during indexing: {e}")
            return {
                "success": False,
                "error": str(e),
                "indexed_count": 0
            }
    
    def verify_indexing(self, original_count: int) -> dict:
        """Verify the indexing results with sample queries."""
        if self.dry_run:
            return {"dry_run": True, "verification_skipped": True}
        
        print(f"\n🔍 Verifying indexing results...")
        
        try:
            # Get dryland collection and check count
            client = get_client()
            collection = client.get_collection(name=self.collection_name)
            collection_count = collection.count()
            print(f"📊 Collection contains {collection_count} documents")
            
            # Test sample queries
            test_queries = [
                "plyometric exercises",
                "core strength training", 
                "agility drills",
                "balance exercises",
                "conditioning workouts"
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


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Index enriched off-ice workouts into Chroma")
    parser.add_argument(
        "--input",
        type=Path,
        help="Path to enriched off-ice JSON file (default: find latest in processed/dryland/)"
    )
    parser.add_argument(
        "--clear-dryland",
        action="store_true", 
        help="Clear existing dryland collection before indexing"
    )
    parser.add_argument(
        "--collection-name",
        type=str,
        default="hockey_dryland",
        help="Name for the dryland collection (default: hockey_dryland)"
    )
    parser.add_argument("--dry-run", action="store_true", help="Print summary without indexing")
    parser.add_argument("--limit", type=int, help="Only index first N entries")
    args = parser.parse_args()

    # Determine input file
    if args.input:
        input_file = args.input
    else:
        # Find latest enriched off-ice file
        processed_dir = Path(__file__).parent.parent / "processed" / "dryland"
        enriched_files = list(processed_dir.glob("off_ice_enriched_*.json"))
        
        if enriched_files:
            # Use the most recent enriched file
            input_file = max(enriched_files, key=lambda p: p.stat().st_mtime)
            print(f"📂 Using most recent enriched off-ice file: {input_file}")
        else:
            # Fall back to legacy location
            input_file = Path("data/processed/off_ice_enriched.json")
            print(f"📂 Using legacy off-ice file: {input_file}")

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data: List[dict] = json.load(f)
    except FileNotFoundError:
        print(f"❌ Input file not found: {input_file}")
        print("   Run the off-ice enrichment script first or specify --input")
        return

    if args.limit:
        data = data[: args.limit]
    print(f"📂 Loaded {len(data)} enriched off-ice workouts from {input_file}")

    print(f"🏒 Hockey Dryland Indexing Script")
    print("=" * 50)
    print(f"Mode: {'DRY RUN' if args.dry_run else 'FULL INDEXING'}")
    print(f"Collection: {args.collection_name}")
    print(f"Clear existing: {'YES' if args.clear_dryland else 'NO'}")
    
    # Initialize indexer
    indexer = DrylandIndexer(dry_run=args.dry_run, collection_name=args.collection_name)
    
    if not data:
        print("❌ No dryland workouts found!")
        return
    
    # Index workouts
    indexing_results = indexer.index_workouts(data, clear_existing=args.clear_dryland)
    
    if not indexing_results.get("success", False):
        print(f"❌ Indexing failed: {indexing_results.get('error', 'Unknown error')}")
        return
    
    # Verify indexing
    verification_results = indexer.verify_indexing(len(data))
    
    # Print final summary
    print(f"\n📋 INDEXING SUMMARY")
    print("=" * 50)
    
    if args.dry_run:
        print(f"Documents analyzed: {indexing_results.get('total_workouts', 0)}")
        print(f"Sample documents: {indexing_results.get('sample_count', 0)}")
    else:
        print(f"Documents indexed: {indexing_results.get('indexed_count', 0)}")
        
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
    
    print(f"Input file: {input_file}")
    
    if args.dry_run:
        print(f"\n🔍 DRY RUN COMPLETE - Run without --dry-run to index all dryland workouts")
    else:
        print(f"\n✅ INDEXING COMPLETE")


if __name__ == "__main__":
    main()
