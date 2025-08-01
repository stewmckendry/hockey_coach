#!/usr/bin/env python3
"""Index Maple Leafs Hot Stove NHL insights into a Chroma collection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Dict, Any

from more_itertools import chunked
import sys

# Add repo root to PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils.chroma_utils import get_client


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


class NHLInsightsIndexer:
    def __init__(self, collection_name: str = "hockey_nhl_insights"):
        """Initialize the NHL insights indexer."""
        self.collection_name = collection_name
    
    def index_insights(self, insights: List[dict], chunk_size: int = 100) -> dict:
        """Index NHL insights into dedicated Chroma collection."""
        try:
            # Get or create dedicated NHL insights collection
            client = get_client()
            
            print(f"📚 Creating/accessing NHL insights collection: '{self.collection_name}'")
            collection = client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "NHL player insights and interview quotes for hockey coaching"}
            )
            
            # Get existing IDs to avoid duplicates
            existing_data = collection.get()
            existing_ids = set(existing_data["ids"]) if existing_data["ids"] else set()
            
            docs: List[str] = []
            metas: List[dict] = []
            ids: List[str] = []
            
            for ins in insights:
                doc_id = f"insight-{ins.get('id')}"
                if doc_id in existing_ids:
                    continue
                docs.append(insight_text(ins))
                metas.append(metadata_for(ins))
                ids.append(doc_id)
            
            if not docs:
                print("No new insights to index")
                return {"success": True, "indexed_count": 0, "message": "No new insights"}
            
            # Index in chunks
            indexed_count = 0
            for i, (d_chunk, m_chunk, id_chunk) in enumerate(
                zip(chunked(docs, chunk_size), chunked(metas, chunk_size), chunked(ids, chunk_size))
            ):
                print(f"📦 Indexing chunk {i+1} with {len(d_chunk)} insights...")
                try:
                    collection.add(documents=d_chunk, metadatas=m_chunk, ids=id_chunk)
                    indexed_count += len(d_chunk)
                except Exception as e:
                    print(f"❌ Failed to index chunk {i+1}: {e}")
                    return {"success": False, "error": str(e), "indexed_count": indexed_count}
            
            # Verify final count
            final_count = collection.count()
            print(f"✅ Successfully indexed {indexed_count} new insights")
            print(f"📊 Total collection count: {final_count}")
            
            return {
                "success": True,
                "indexed_count": indexed_count,
                "total_count": final_count
            }
            
        except Exception as e:
            print(f"❌ Error during indexing: {e}")
            return {"success": False, "error": str(e), "indexed_count": 0}
    
    def verify_indexing(self) -> dict:
        """Verify the indexing results with sample queries."""
        print(f"\n🔍 Verifying indexing results...")
        
        try:
            # Get NHL insights collection and check count
            client = get_client()
            collection = client.get_collection(name=self.collection_name)
            collection_count = collection.count()
            print(f"📊 Collection contains {collection_count} documents")
            
            # Test sample queries
            test_queries = [
                "defensive game strategies",
                "player mindset and motivation", 
                "professional development advice",
                "team chemistry insights",
                "NHL career experiences"
            ]
            
            verification_results = {
                "collection_count": collection_count,
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
            return {"success": False, "error": str(e)}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Index NHL insights into Chroma")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("chroma_load/processed/nhl_interviews/mlhs_insights.json"),
        help="Path to mlhs_insights.json",
    )
    parser.add_argument(
        "--chunk-size", type=int, default=100, help="Number of insights per batch"
    )
    parser.add_argument(
        "--collection-name",
        type=str,
        default="hockey_nhl_insights",
        help="Name for the NHL insights collection (default: hockey_nhl_insights)"
    )
    args = parser.parse_args()

    print("🏒 NHL Insights Indexing Script")
    print("=" * 50)
    print(f"Collection: {args.collection_name}")
    print(f"Input file: {args.input}")
    print(f"Chunk size: {args.chunk_size}")
    
    # Load data
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"📂 Loaded {len(data)} insights from {args.input}")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return 1
    
    # Initialize indexer and index insights
    indexer = NHLInsightsIndexer(collection_name=args.collection_name)
    indexing_results = indexer.index_insights(data, chunk_size=args.chunk_size)
    
    if not indexing_results.get("success", False):
        print(f"❌ Indexing failed: {indexing_results.get('error', 'Unknown error')}")
        return 1
    
    # Verify indexing
    verification_results = indexer.verify_indexing()
    
    # Print final summary
    print(f"\n📋 INDEXING SUMMARY")
    print("=" * 50)
    print(f"Documents indexed: {indexing_results.get('indexed_count', 0)}")
    print(f"Total collection count: {indexing_results.get('total_count', 0)}")
    
    # Show query test results
    if "sample_queries" in verification_results:
        successful_queries = sum(1 for q in verification_results["sample_queries"].values() if q.get("success", False))
        total_queries = len(verification_results["sample_queries"])
        print(f"Sample queries: {successful_queries}/{total_queries} successful")
    
    print(f"✅ INDEXING COMPLETE")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
