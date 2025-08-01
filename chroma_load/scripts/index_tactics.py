#!/usr/bin/env python3
"""
Hockey Tactics Indexing Script

This script loads enriched tactics data and indexes it into Chroma vector database
for semantic search and retrieval.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import chromadb
from chromadb.config import Settings

# Setup paths
SCRIPT_DIR = Path(__file__).parent
PROCESSED_DIR = SCRIPT_DIR.parent / "processed"
INDEXED_DIR = SCRIPT_DIR.parent / "indexed"

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from utils.chroma_utils import get_client, clear_chroma_collection

def doc_text(tactic: dict) -> str:
    """Create document text for enriched tactic."""
    parts = [
        f"Tactic: {tactic.get('tactic_name') or ''}",
        f"Summary: {tactic.get('summary') or ''}",
        f"Instructions: {tactic.get('instructions') or ''}",
        f"Skills: {'; '.join(tactic.get('skills') or [])}",
        f"Centre: {tactic.get('centre_assignments') or ''}",
        f"Wingers: {tactic.get('winger_assignments') or ''}",
        f"Defense: {tactic.get('defense_assignments') or ''}",
        f"Goalie: {tactic.get('goalie_assignments') or ''}",
        f"Teaching Points: {'; '.join(tactic.get('teaching_points') or [])}",
        f"Source: {tactic.get('source') or ''}",
    ]
    text = "\n".join([p for p in parts if p and not p.endswith(': ') and not p.endswith(': N/A')])
    return text[:16000]


def metadata_for(tactic: dict) -> dict:
    """Create metadata for enriched tactic."""
    def safe_str(val) -> str:
        return val if isinstance(val, str) else ""
    
    def safe_list_str(val) -> str:
        if isinstance(val, list):
            return "; ".join(str(item) for item in val)
        return safe_str(val)
    
    return {
        "tactic_name": safe_str(tactic.get("tactic_name")),
        "summary": safe_str(tactic.get("summary")),
        "source": safe_str(tactic.get("source")),
        "skills": safe_list_str(tactic.get("skills")),
        "centre_assignments": safe_str(tactic.get("centre_assignments")),
        "winger_assignments": safe_str(tactic.get("winger_assignments")),
        "defense_assignments": safe_str(tactic.get("defense_assignments")),
        "goalie_assignments": safe_str(tactic.get("goalie_assignments")),
        "teaching_points": safe_list_str(tactic.get("teaching_points")),
        "document_type": "tactic"
    }


class TacticsIndexer:
    def __init__(self, dry_run: bool = False, collection_name: str = "hockey_tactics"):
        """Initialize the tactics indexer."""
        self.dry_run = dry_run
        self.collection_name = collection_name
    def find_latest_enriched_file(self, input_file: Optional[Path] = None) -> Path:
        """Find the latest enriched tactics file."""
        if input_file is not None:
            if input_file.exists():
                return input_file
            else:
                # Try relative to processed directory
                full_path = PROCESSED_DIR / input_file
                if full_path.exists():
                    return full_path
                else:
                    raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Find latest enriched file
        pattern = "tactics_enriched_*.json"
        enriched_files = list(PROCESSED_DIR.glob(pattern))
        
        if not enriched_files:
            raise FileNotFoundError(f"No enriched tactics files found in {PROCESSED_DIR}")
        
        # Sort by modification time to get latest
        latest_file = max(enriched_files, key=lambda f: f.stat().st_mtime)
        return latest_file
    
    def load_enriched_tactics(self, input_file: Path) -> List[Dict[str, Any]]:
        """Load enriched tactics from JSON file."""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                tactics = json.load(f)
            print(f"📂 Loaded {len(tactics)} enriched tactics from {input_file}")
            return tactics
        except Exception as e:
            raise Exception(f"Error loading tactics from {input_file}: {e}")
    
    def index_tactics(self, tactics: List[Dict[str, Any]], clear_existing: bool = True) -> Dict[str, Any]:
        """Index all tactics into Chroma database."""
        
        print(f"\n🚀 Indexing {len(tactics)} tactics...")
        
        if self.dry_run:
            print("🔍 DRY RUN MODE: Analyzing indexing structure")
            
            # Show sample documents
            sample_count = min(3, len(tactics))
            for i in range(sample_count):
                tactic = tactics[i]
                doc_content = doc_text(tactic)
                metadata = metadata_for(tactic)
                print(f"\n📄 Sample Document {i+1}:")
                print(f"   Tactic: {tactic.get('tactic_name', 'Unknown')}")
                print(f"   Content length: {len(doc_content)} chars")
                print(f"   Content preview: {doc_content[:200]}...")
                print(f"   Metadata keys: {list(metadata.keys())}")
            
            return {
                "success": True,
                "dry_run": True,
                "total_tactics": len(tactics),
                "sample_count": sample_count
            }
        
        try:
            # Get or create dedicated tactics collection
            client = get_client()
            
            if clear_existing:
                try:
                    print(f"🗑️  Clearing existing tactics collection '{self.collection_name}'...")
                    client.delete_collection(name=self.collection_name)
                except Exception as e:
                    print(f"   (Collection may not exist yet: {e})")
            
            print(f"📚 Creating/accessing tactics collection: '{self.collection_name}'")
            collection = client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Hockey tactics, systems, and strategic plays"}
            )
            
            # Prepare documents for indexing
            print(f"📝 Preparing {len(tactics)} documents for indexing...")
            
            documents = []
            metadatas = []
            ids = []
            
            for i, tactic in enumerate(tactics):
                # Create document content
                doc_content = doc_text(tactic)
                documents.append(doc_content)
                
                # Create metadata
                metadata = metadata_for(tactic)
                metadatas.append(metadata)
                
                # Create unique ID
                tactic_name = tactic.get('tactic_name', f'tactic_{i}')
                safe_name = tactic_name.lower().replace(' ', '_').replace('-', '_')
                doc_id = f"tactic_{i}_{safe_name}"
                ids.append(doc_id)
            
            # Add to collection
            print(f"� Adding documents to Chroma collection...")
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            # Verify insertion
            collection_count = collection.count()
            print(f"✅ Successfully indexed {collection_count} tactics")
            
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
            # Get tactics collection and check count
            client = get_client()
            collection = client.get_collection(name=self.collection_name)
            collection_count = collection.count()
            print(f"📊 Collection contains {collection_count} documents")
            
            # Test sample queries
            test_queries = [
                "forechecking tactics",
                "power play systems", 
                "defensive zone coverage",
                "neutral zone trap",
                "breakout strategies"
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
    
    def save_indexing_summary(self, 
                            input_file: Path, 
                            indexing_results: Dict[str, Any], 
                            verification_results: Dict[str, Any]) -> str:
        """Save indexing summary to JSON file."""
        
        if self.dry_run:
            print("🔍 DRY RUN: Would save indexing summary")
            return "dry-run-summary"
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        summary = {
            "timestamp": timestamp,
            "input_file": str(input_file),
            "indexing_results": indexing_results,
            "verification_results": verification_results
        }
        
        # Ensure indexed directory exists
        INDEXED_DIR.mkdir(parents=True, exist_ok=True)
        
        output_file = INDEXED_DIR / f"tactics_indexed_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved indexing summary to: {output_file}")
        return str(output_file)

def main():
    parser = argparse.ArgumentParser(description="Index enriched hockey tactics into Chroma database")
    parser.add_argument(
        "--input",
        type=Path,
        help="Input enriched tactics file (default: latest tactics_enriched_*.json)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Analyze indexing structure without actual indexing"
    )
    parser.add_argument(
        "--clear-tactics",
        action="store_true",
        help="Clear existing tactics collection before indexing"
    )
    parser.add_argument(
        "--collection-name",
        type=str,
        default="hockey_tactics",
        help="Name for the tactics collection (default: hockey_tactics)"
    )
    
    args = parser.parse_args()
    
    print("🏒 Hockey Tactics Indexing Script")
    print("=" * 50)
    print(f"Mode: {'DRY RUN' if args.dry_run else 'FULL INDEXING'}")
    print(f"Collection: {args.collection_name}")
    print(f"Clear existing: {'YES' if args.clear_tactics else 'NO'}")
    
    indexer = TacticsIndexer(dry_run=args.dry_run, collection_name=args.collection_name)
    
    try:
        # Find and load input file
        input_file = indexer.find_latest_enriched_file(args.input)
        print(f"📂 Input file: {input_file}")
        
        tactics = indexer.load_enriched_tactics(input_file)
        
        if not tactics:
            print("❌ No tactics found!")
            return 1
        
        # Index tactics
        indexing_results = indexer.index_tactics(tactics, clear_existing=args.clear_tactics)
        
        if not indexing_results.get("success", False):
            print(f"❌ Indexing failed: {indexing_results.get('error', 'Unknown error')}")
            return 1
        
        # Verify indexing
        verification_results = indexer.verify_indexing(len(tactics))
        
        # Save summary
        summary_file = indexer.save_indexing_summary(input_file, indexing_results, verification_results)
        
        # Print final summary
        print(f"\n📋 INDEXING SUMMARY")
        print("=" * 50)
        
        if args.dry_run:
            print(f"Documents analyzed: {indexing_results.get('total_tactics', 0)}")
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
        print(f"Summary file: {summary_file}")
        
        if args.dry_run:
            print(f"\n🔍 DRY RUN COMPLETE - Run without --dry-run to index all tactics")
        else:
            print(f"\n✅ INDEXING COMPLETE")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
