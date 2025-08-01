#!/usr/bin/env python3
"""Index LTAD skills into a Chroma collection."""

from __future__ import annotations
import argparse
import json
from pathlib import Path
from collections import Counter
from datetime import datetime
import sys

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from utils.chroma_utils import get_client, clear_chroma_collection


def doc_text(skill: dict) -> str:
    """Create document text for enriched LTAD skill."""
    parts = [
        f"Skill: {skill.get('skill_name') or ''}",
        f"Category: {skill.get('skill_category') or ''}",
        f"Age Group: {skill.get('age_group') or ''}",
        f"Complexity: {skill.get('complexity', '')}",
        f"Summary: {skill.get('summary') or ''}",
        f"Instructions: {skill.get('instructions') or ''}",
        f"Teaching Points: {'; '.join(skill.get('teaching_points') or [])}",
        f"Equipment: {'; '.join(skill.get('equipment') or [])}",
        f"Positions: {'; '.join(skill.get('positions') or [])}",
        f"Source: {skill.get('source') or ''}",
    ]
    text = "\n".join([p for p in parts if p and not p.endswith(': ')])
    return text[:16000]


def metadata_for(skill: dict) -> dict:
    """Create metadata for enriched LTAD skill."""
    def safe_str(val) -> str:
        return val if isinstance(val, str) else ""
    
    def safe_list_str(val) -> str:
        if isinstance(val, list):
            return "; ".join(str(item) for item in val)
        return safe_str(val)
    
    base = {
        "skill_name": safe_str(skill.get("skill_name")),
        "skill_category": safe_str(skill.get("skill_category")),
        "age_group": safe_str(skill.get("age_group")),
        "summary": safe_str(skill.get("summary")),
        "teaching_points": safe_list_str(skill.get("teaching_points")),
        "equipment": safe_list_str(skill.get("equipment")),
        "positions": safe_list_str(skill.get("positions")),
        "complexity": str(skill.get("complexity") or ""),
        "source": safe_str(skill.get("source")),
    }

    return {k: v for k, v in base.items() if v}


class SkillsIndexer:
    def __init__(self, dry_run: bool = False, collection_name: str = "hockey_skills"):
        """Initialize the skills indexer."""
        self.dry_run = dry_run
        self.collection_name = collection_name
    
    def find_latest_enriched_file(self, input_dir: Path, input_file: str = None) -> Path:
        """Find the latest enriched LTAD skills file."""
        if input_file:
            # Try direct path first
            file_path = Path(input_file)
            if file_path.exists():
                return file_path
            
            # Try relative to input directory
            candidate = input_dir / input_file
            if candidate.exists():
                return candidate
            
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Find the most recent enriched LTAD skills file
        pattern = "enriched_ltad_skills_*.json"
        files = list(input_dir.glob(pattern))
        if not files:
            raise FileNotFoundError(f"No enriched LTAD skills files found in {input_dir}")
        
        return max(files, key=lambda f: f.stat().st_mtime)
    
    def load_enriched_skills(self, input_file: Path) -> list:
        """Load enriched skills from JSON file."""
        try:
            with open(input_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"📂 Loaded {len(data)} enriched skills from {input_file}")
            return data
        except Exception as e:
            raise Exception(f"Error loading skills from {input_file}: {e}")
    
    def index_skills(self, skills: list, clear_existing: bool = True) -> dict:
        """Index all skills into Chroma database."""
        print(f"\n🚀 Indexing {len(skills)} skills...")
        
        if self.dry_run:
            print("🔍 DRY RUN MODE: Analyzing indexing structure")
            
            # Show sample documents
            sample_count = min(3, len(skills))
            for i in range(sample_count):
                skill = skills[i]
                doc_content = doc_text(skill)
                metadata = metadata_for(skill)
                print(f"\n📄 Sample Document {i+1}:")
                print(f"   Skill: {skill.get('skill_name', 'Unknown')}")
                print(f"   Content length: {len(doc_content)} chars")
                print(f"   Content preview: {doc_content[:200]}...")
                print(f"   Metadata keys: {list(metadata.keys())}")
            
            return {
                "success": True,
                "dry_run": True,
                "total_skills": len(skills),
                "sample_count": sample_count
            }
        
        try:
            # Get or create dedicated skills collection
            client = get_client()
            
            if clear_existing:
                try:
                    print(f"🗑️  Clearing existing skills collection '{self.collection_name}'...")
                    client.delete_collection(name=self.collection_name)
                except Exception as e:
                    print(f"   (Collection may not exist yet: {e})")
            
            print(f"📚 Creating/accessing skills collection: '{self.collection_name}'")
            collection = client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Hockey skills development and LTAD guidelines"}
            )
            
            # Prepare documents for indexing
            print(f"📝 Preparing {len(skills)} documents for indexing...")
            
            documents = []
            metadatas = []
            ids = []
            
            for idx, skill in enumerate(skills):
                # Create document content
                doc_content = doc_text(skill)
                documents.append(doc_content)
                
                # Create metadata
                metadata = metadata_for(skill)
                if not metadata:
                    print(f"⚠️ Skipping skill {idx}: empty metadata")
                    continue
                metadatas.append(metadata)
                
                # Create unique ID
                skill_name = skill.get('skill_name', f'skill_{idx}')
                safe_name = skill_name.lower().replace(' ', '-').replace('_', '-')
                doc_id = f"ltad-{idx}-{safe_name}"
                ids.append(doc_id)
            
            # Add to collection
            print(f"💾 Adding documents to Chroma collection...")
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            # Verify insertion
            collection_count = collection.count()
            print(f"✅ Successfully indexed {collection_count} skills")
            
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
            # Get skills collection and check count
            client = get_client()
            collection = client.get_collection(name=self.collection_name)
            collection_count = collection.count()
            print(f"📊 Collection contains {collection_count} documents")
            
            # Test sample queries
            test_queries = [
                "skating skills",
                "passing techniques",
                "shooting drills",
                "stickhandling practice",
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Index enriched LTAD skills into hockey_skills collection")
    parser.add_argument(
        "--input", 
        type=Path, 
        default=Path("chroma_load/processed/ltad"), 
        help="Directory with enriched LTAD skills JSON files"
    )
    parser.add_argument(
        "--file", 
        type=str, 
        help="Specific enriched skills file to index (e.g., enriched_ltad_skills_20250722_195101.json)"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing hockey_skills collection before indexing",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Analyze indexing structure without actual indexing",
    )
    parser.add_argument(
        "--collection-name",
        type=str,
        default="hockey_skills",
        help="Name for the skills collection (default: hockey_skills)"
    )
    
    args = parser.parse_args()
    
    print("🏒 Hockey Skills Indexing Script")
    print("=" * 50)
    print(f"Mode: {'DRY RUN' if args.dry_run else 'FULL INDEXING'}")
    print(f"Collection: {args.collection_name}")
    print(f"Clear existing: {'YES' if args.clear else 'NO'}")
    
    indexer = SkillsIndexer(dry_run=args.dry_run, collection_name=args.collection_name)
    
    try:
        # Find and load input file
        input_file = indexer.find_latest_enriched_file(args.input, args.file)
        print(f"📂 Input file: {input_file}")
        
        skills = indexer.load_enriched_skills(input_file)
        
        if not skills:
            print("❌ No skills found!")
            return
        
        # Show data summary
        print(f"📊 Loaded {len(skills)} enriched skills")
        print(
            "Top categories:",
            Counter(s.get("skill_category") for s in skills).most_common(5),
        )
        print(
            "Age group coverage:",
            Counter(s.get("age_group") for s in skills).most_common(),
        )
        print(
            "Complexity distribution:",
            Counter(s.get("complexity") for s in skills).most_common(),
        )
        print(
            "Position distribution:",
            Counter(pos for s in skills for pos in (s.get("positions") or [])).most_common(),
        )
        
        # Index skills
        indexing_results = indexer.index_skills(skills, clear_existing=args.clear)
        
        if not indexing_results.get("success", False):
            print(f"❌ Indexing failed: {indexing_results.get('error', 'Unknown error')}")
            return
        
        # Verify indexing
        verification_results = indexer.verify_indexing(len(skills))
        
        # Create snapshot for verification (similar to original)
        if not args.dry_run:
            snapshot = []
            for idx, skill in enumerate(skills):
                skill_name = skill.get('skill_name', f'skill_{idx}')
                safe_name = skill_name.lower().replace(' ', '-').replace('_', '-')
                doc_id = f"ltad-{idx}-{safe_name}"
                snapshot.append({
                    "id": doc_id,
                    "document": doc_text(skill),
                    "metadata": metadata_for(skill)
                })
            
            snapshot_file = f"ltad_skills_indexed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(snapshot_file, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, indent=2)
            print(f"📄 Created indexing snapshot: {snapshot_file}")
        
        # Print final summary
        print(f"\n📋 INDEXING SUMMARY")
        print("=" * 50)
        
        if args.dry_run:
            print(f"Documents analyzed: {indexing_results.get('total_skills', 0)}")
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
            print(f"\n🔍 DRY RUN COMPLETE - Run without --dry-run to index all skills")
        else:
            print(f"\n✅ INDEXING COMPLETE")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return


if __name__ == "__main__":
    main()
