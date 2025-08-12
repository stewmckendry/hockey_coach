#!/usr/bin/env python3
"""Check metadata fields in each collection to understand categories."""

import sys
from pathlib import Path
from collections import Counter

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent))

from utils.chroma_utils import get_client

def check_collection_metadata(collection_name: str, category_field: str):
    """Check metadata in a collection."""
    try:
        client = get_client()
        collection = client.get_collection(name=collection_name)
        
        # Get sample of documents
        results = collection.get(
            limit=1000,
            include=["metadatas"]
        )
        
        if not results['metadatas']:
            print(f"  ❌ No documents in {collection_name}")
            return []
        
        # Count categories
        categories = []
        for metadata in results['metadatas']:
            if metadata and category_field in metadata:
                categories.append(metadata[category_field])
        
        category_counts = Counter(categories)
        print(f"\n📊 {collection_name} - {category_field}:")
        for category, count in category_counts.most_common():
            print(f"  - {category}: {count} items")
        
        return list(category_counts.keys())
        
    except Exception as e:
        print(f"  ❌ Error accessing {collection_name}: {e}")
        return []

if __name__ == "__main__":
    print("🏒 Checking Hockey Collection Categories\n")
    
    # Check drills
    check_collection_metadata("hockey_drills", "drill_type")
    check_collection_metadata("hockey_drills", "drill_category")
    
    # Check tactics
    check_collection_metadata("hockey_tactics", "tactic_type")
    check_collection_metadata("hockey_tactics", "category")
    
    # Check videos
    check_collection_metadata("hockey_videos", "skill_category")
    check_collection_metadata("hockey_videos", "clip_category")
    
    # Check dryland
    check_collection_metadata("hockey_dryland", "exercise_category")
    check_collection_metadata("hockey_dryland", "category")
    check_collection_metadata("hockey_dryland_videos", "exercise_category")