#!/usr/bin/env python3
"""Index conduct entries into a Chroma collection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Dict, List, Any, Optional

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from utils.chroma_utils import get_client


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
        "type": "conduct_policy",
    }


class ConductIndexer:
    def __init__(self, dry_run: bool = False, collection_name: str = "hockey_rules"):
        """Initialize the conduct indexer."""
        self.dry_run = dry_run
        self.collection_name = collection_name

    def load_conduct_entries(self, input_file: Path) -> List[Dict[str, Any]]:
        """Load conduct entries from JSON file."""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                entries = json.load(f)
            print(f"📂 Loaded {len(entries)} conduct entries from {input_file}")
            return entries
        except Exception as e:
            raise Exception(f"Error loading conduct entries from {input_file}: {e}")

    def index_conduct_entries(self, entries: List[Dict[str, Any]], clear_existing: bool = True) -> Dict[str, Any]:
        """Index all conduct entries into Chroma database."""
        
        print(f"\n🚀 Indexing {len(entries)} conduct entries...")
        
        if self.dry_run:
            print("🔍 DRY RUN MODE: Analyzing indexing structure")
            
            # Show sample documents
            sample_count = min(3, len(entries))
            for i in range(sample_count):
                entry = entries[i]
                doc_content = doc_text(entry)
                metadata = metadata_for(entry)
                print(f"\n📄 Sample Document {i+1}:")
                print(f"   Title: {entry.get('title', 'Unknown')}")
                print(f"   Content length: {len(doc_content)} chars")
                print(f"   Content preview: {doc_content[:200]}...")
                print(f"   Metadata keys: {list(metadata.keys())}")
            
            return {
                "success": True,
                "dry_run": True,
                "total_entries": len(entries),
                "sample_count": sample_count
            }
        
        try:
            # Get or create dedicated hockey rules collection
            client = get_client()
            
            if clear_existing:
                try:
                    print(f"🗑️  Clearing existing hockey rules collection '{self.collection_name}'...")
                    client.delete_collection(name=self.collection_name)
                except Exception as e:
                    print(f"   (Collection may not exist yet: {e})")
            
            print(f"📚 Creating/accessing hockey rules collection: '{self.collection_name}'")
            collection = client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Hockey rules, conduct policies, and regulations"}
            )
            
            # Prepare documents for indexing
            print(f"📝 Preparing {len(entries)} documents for indexing...")
            
            documents = []
            metadatas = []
            ids = []
            
            for i, entry in enumerate(entries):
                # Create document content
                doc_content = doc_text(entry)
                documents.append(doc_content)
                
                # Create metadata
                metadata = metadata_for(entry)
                metadatas.append(metadata)
                
                # Create unique ID
                doc_id = f"conduct-{i}"
                ids.append(doc_id)
            
            # Add to collection
            print(f"📚 Adding documents to Chroma collection...")
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            # Verify insertion
            collection_count = collection.count()
            print(f"✅ Successfully indexed {collection_count} conduct entries")
            
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

    def verify_indexing(self, original_count: int) -> Dict[str, Any]:
        """Verify the indexing results with sample queries."""
        if self.dry_run:
            return {"dry_run": True, "verification_skipped": True}
        
        print(f"\n🔍 Verifying indexing results...")
        
        try:
            # Get hockey rules collection and check count
            client = get_client()
            collection = client.get_collection(name=self.collection_name)
            collection_count = collection.count()
            print(f"📊 Collection contains {collection_count} documents")
            
            # Test sample queries
            test_queries = [
                "hockey rules and regulations",
                "conduct policies", 
                "player behavior",
                "game regulations",
                "officiating guidelines"
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
    parser = argparse.ArgumentParser(description="Index conduct entries into Chroma database")
    parser.add_argument(
        "--input", 
        type=Path, 
        default=Path("chroma_load/processed/rules/conduct_enriched.json"), 
        help="Path to conduct_enriched.json"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Analyze indexing structure without actual indexing"
    )
    parser.add_argument(
        "--limit", 
        type=int, 
        help="Only index first N entries"
    )
    parser.add_argument(
        "--clear-existing",
        action="store_true",
        help="Clear existing hockey rules collection before indexing"
    )
    parser.add_argument(
        "--collection-name",
        type=str,
        default="hockey_rules",
        help="Name for the hockey rules collection (default: hockey_rules)"
    )
    
    args = parser.parse_args()
    
    print("🏒 Hockey Rules/Conduct Indexing Script")
    print("=" * 50)
    print(f"Mode: {'DRY RUN' if args.dry_run else 'FULL INDEXING'}")
    print(f"Collection: {args.collection_name}")
    print(f"Clear existing: {'YES' if args.clear_existing else 'NO'}")
    
    indexer = ConductIndexer(dry_run=args.dry_run, collection_name=args.collection_name)
    
    try:
        # Load input file
        print(f"📂 Input file: {args.input}")
        
        entries = indexer.load_conduct_entries(args.input)
        
        if args.limit:
            entries = entries[:args.limit]
            print(f"📋 Limited to first {args.limit} entries")
        
        if not entries:
            print("❌ No conduct entries found!")
            return
        
        # Index conduct entries
        indexing_results = indexer.index_conduct_entries(entries, clear_existing=args.clear_existing)
        
        if not indexing_results.get("success", False):
            print(f"❌ Indexing failed: {indexing_results.get('error', 'Unknown error')}")
            return
        
        # Verify indexing
        verification_results = indexer.verify_indexing(len(entries))
        
        # Print final summary
        print(f"\n📋 INDEXING SUMMARY")
        print("=" * 50)
        
        if args.dry_run:
            print(f"Documents analyzed: {indexing_results.get('total_entries', 0)}")
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
        
        print(f"Input file: {args.input}")
        
        if args.dry_run:
            print(f"\n🔍 DRY RUN COMPLETE - Run without --dry-run to index all conduct entries")
        else:
            print(f"\n✅ INDEXING COMPLETE")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return


if __name__ == "__main__":
    main()
