#!/usr/bin/env python3
"""Check all metadata fields in each collection."""

import sys
from pathlib import Path
from collections import Counter

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent))

from utils.chroma_utils import get_client

def check_collection_fields(collection_name: str):
    """Check all metadata fields in a collection."""
    try:
        client = get_client()
        collection = client.get_collection(name=collection_name)
        
        # Get sample of documents
        results = collection.get(
            limit=5,  # Just a few samples
            include=["metadatas", "documents"]
        )
        
        if not results['metadatas']:
            print(f"  ❌ No documents in {collection_name}")
            return
        
        print(f"\n📊 {collection_name}:")
        
        # Show sample metadata keys
        for i, metadata in enumerate(results['metadatas'][:2]):
            if metadata:
                print(f"  Sample {i+1} fields: {list(metadata.keys())}")
                # Show values for key fields
                for key in ['drill_type', 'drill_category', 'drill_name', 'tactic_type', 
                           'category', 'skill_category', 'clip_category', 'exercise_category',
                           'exercise_name', 'clip_title', 'title']:
                    if key in metadata:
                        print(f"    {key}: {metadata[key]}")
        
        # Count all unique fields
        all_fields = set()
        for metadata in results['metadatas']:
            if metadata:
                all_fields.update(metadata.keys())
        
        print(f"  All fields: {sorted(all_fields)}")
        
    except Exception as e:
        print(f"  ❌ Error accessing {collection_name}: {e}")

if __name__ == "__main__":
    print("🏒 Checking Hockey Collection Metadata Fields\n")
    
    collections = [
        "hockey_drills",
        "hockey_tactics", 
        "hockey_videos",
        "hockey_dryland",
        "hockey_dryland_videos"
    ]
    
    for collection in collections:
        check_collection_fields(collection)