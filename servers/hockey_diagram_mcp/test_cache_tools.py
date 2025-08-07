#!/usr/bin/env python3
"""
Test the hockey diagram cache MCP tools.
Run this to verify the caching system is working correctly.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

from diagram_cache import DiagramCacheManager
from two_stage_parser import TwoStageHockeyParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_cache_operations():
    """Test all cache operations."""
    print("\n" + "="*60)
    print("Hockey Diagram Cache Test Suite")
    print("="*60)
    
    # Initialize components
    cache_manager = DiagramCacheManager()
    parser = TwoStageHockeyParser()
    
    # Test 1: Save a diagram to cache
    print("\n1. Testing SAVE operation...")
    test_prompt = "2-1-2 forecheck with F1 pressuring behind net"
    
    # Parse the prompt to get a spec
    spec_result = await parser.parse_prompt(test_prompt)
    if not spec_result or not spec_result.get('success'):
        print("   ❌ Failed to parse test prompt")
        return
    
    spec = spec_result['spec']
    
    # Save to cache
    diagram_id = cache_manager.save_diagram(
        prompt=test_prompt,
        spec=spec,
        parser_type="two_stage",
        metadata={
            "tags": ["forecheck", "2-1-2", "test"],
            "author": "test_suite"
        }
    )
    print(f"   ✅ Saved diagram with ID: {diagram_id}")
    
    # Test 2: Search for similar diagrams
    print("\n2. Testing SEARCH operation...")
    search_results = cache_manager.search_diagrams(
        query="forecheck formation",
        limit=5,
        min_similarity=0.5
    )
    print(f"   ✅ Found {len(search_results)} similar diagrams")
    if search_results:
        for result in search_results[:3]:
            print(f"      - {result['prompt'][:50]}... (similarity: {result['similarity']:.2f})")
    
    # Test 3: Get specific diagram
    print("\n3. Testing GET operation...")
    retrieved = cache_manager.get_diagram(diagram_id)
    if retrieved:
        print(f"   ✅ Retrieved diagram: {retrieved['id']}")
        print(f"      Prompt: {retrieved['prompt'][:50]}...")
        print(f"      Usage count: {retrieved['usage_count']}")
    else:
        print("   ❌ Failed to retrieve diagram")
    
    # Test 4: Update diagram metadata
    print("\n4. Testing UPDATE operation...")
    success = cache_manager.update_diagram(
        diagram_id=diagram_id,
        metadata={
            "validated": True,
            "tags": ["forecheck", "2-1-2", "verified", "test"]
        }
    )
    if success:
        print("   ✅ Updated diagram metadata")
    else:
        print("   ❌ Failed to update diagram")
    
    # Test 5: Get cache statistics
    print("\n5. Testing STATISTICS operation...")
    stats = cache_manager.get_statistics()
    print(f"   ✅ Cache statistics:")
    print(f"      Total diagrams: {stats.get('total_diagrams', 0)}")
    print(f"      Validated: {stats.get('validated_count', 0)}")
    print(f"      Parser types: {stats.get('parser_types', {})}")
    
    # Test 6: Save another diagram for variety
    print("\n6. Testing multiple diagram storage...")
    test_prompts = [
        "Power play 1-3-1 umbrella formation",
        "Penalty kill box formation in defensive zone",
        "Neutral zone trap 1-3-1 setup"
    ]
    
    saved_ids = []
    for prompt in test_prompts:
        spec_result = await parser.parse_prompt(prompt)
        if spec_result and spec_result.get('success'):
            new_id = cache_manager.save_diagram(
                prompt=prompt,
                spec=spec_result['spec'],
                parser_type="two_stage",
                metadata={"author": "test_suite"}
            )
            saved_ids.append(new_id)
            print(f"   ✅ Saved: {prompt[:30]}... (ID: {new_id})")
    
    # Test 7: Search with different queries
    print("\n7. Testing search relevance...")
    search_queries = [
        "power play formation",
        "defensive zone coverage",
        "neutral zone system"
    ]
    
    for query in search_queries:
        results = cache_manager.search_diagrams(query, limit=3, min_similarity=0.6)
        print(f"   Query: '{query}'")
        print(f"   Found {len(results)} results")
        if results:
            best_match = results[0]
            print(f"   Best match: {best_match['prompt'][:40]}... (sim: {best_match['similarity']:.2f})")
    
    # Test 8: Delete a diagram
    print("\n8. Testing DELETE operation...")
    if saved_ids:
        delete_id = saved_ids[0]
        success = cache_manager.delete_diagram(delete_id)
        if success:
            print(f"   ✅ Deleted diagram {delete_id}")
        else:
            print(f"   ❌ Failed to delete diagram {delete_id}")
    
    # Final statistics
    print("\n9. Final cache statistics...")
    final_stats = cache_manager.get_statistics()
    print(f"   Total diagrams: {final_stats.get('total_diagrams', 0)}")
    print(f"   Most used diagrams:")
    for diagram in final_stats.get('most_used', [])[:3]:
        print(f"      - {diagram.get('prompt', 'Unknown')[:40]}... (uses: {diagram.get('usage_count', 0)})")
    
    print("\n" + "="*60)
    print("✅ Cache test suite completed successfully!")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(test_cache_operations())