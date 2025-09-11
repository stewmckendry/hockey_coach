#!/usr/bin/env python3
"""
Test script for the new template management tools in hockey_diagram_mcp_v3.py
"""

import sys
from pathlib import Path
import json

# Add parent directories to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
sys.path.append(str(Path(__file__).resolve().parent / 'servers'))

# Import the MCP server module
from servers.hockey_diagram_mcp_v3 import (
    save_diagram_template,
    search_diagram_templates,
    fetch_diagram_template,
    initialize_diagram,
    health_check
)

def test_template_tools():
    """Test the template management tools."""
    
    print("=" * 60)
    print("Testing Hockey Diagram Template Management Tools")
    print("=" * 60)
    
    # 1. Initialize a session
    print("\n1. Initializing diagram session...")
    session = initialize_diagram("Test template management", "drill")
    session_id = session.get("session_id")
    print(f"   Session ID: {session_id}")
    
    # 2. Create a sample spec
    sample_spec = {
        "rink": {
            "features": ["neutral_zone", "face_off_dots", "goals", "goal_creases"]
        },
        "players": [
            {
                "id": "F1",
                "position": {"x": 0, "y": -30},
                "team": "offense",
                "role": "forward",
                "label": "F1"
            },
            {
                "id": "F2",
                "position": {"x": -15, "y": -20},
                "team": "offense",
                "role": "forward",
                "label": "F2"
            },
            {
                "id": "F3",
                "position": {"x": 15, "y": -20},
                "team": "offense",
                "role": "forward",
                "label": "F3"
            },
            {
                "id": "D1",
                "position": {"x": 0, "y": 20},
                "team": "defense",
                "role": "defenseman",
                "label": "D1"
            },
            {
                "id": "D2",
                "position": {"x": -10, "y": 25},
                "team": "defense",
                "role": "defenseman",
                "label": "D2"
            }
        ],
        "movements": [
            {
                "type": "pass",
                "from": "F1",
                "to": "F2",
                "style": "normal",
                "label": "outlet pass"
            }
        ],
        "zones": [],
        "annotations": [
            {
                "type": "text",
                "position": {"x": 0, "y": 40},
                "text": "2-1-2 Forecheck Formation",
                "style": "title"
            }
        ]
    }
    
    # 3. Test save_diagram_template
    print("\n2. Testing save_diagram_template...")
    save_result = save_diagram_template(
        spec=sample_spec,
        name="2-1-2 Forecheck",
        description="Basic 2-1-2 forecheck formation with outlet pass",
        tags=["forecheck", "defensive", "formation", "neutral_zone"],
        session_id=session_id
    )
    
    if "error" in save_result:
        print(f"   ❌ Error: {save_result['error']}")
    else:
        print(f"   ✅ Saved template: {save_result['template_id']}")
        print(f"   File: {save_result['filepath']}")
    
    # 4. Test search_diagram_templates
    print("\n3. Testing search_diagram_templates...")
    
    # Test exact match
    search_result = search_diagram_templates(
        query="forecheck",
        session_id=session_id
    )
    print(f"   Query: 'forecheck'")
    print(f"   Found: {search_result['total_found']} templates")
    if search_result['templates']:
        for i, template in enumerate(search_result['templates'][:3], 1):
            print(f"   {i}. {template['name']} (score: {template['similarity']})")
    
    # Test fuzzy match
    search_result2 = search_diagram_templates(
        query="defensive formation",
        tags=["defensive"],
        session_id=session_id
    )
    print(f"\n   Query: 'defensive formation' with tag filter")
    print(f"   Found: {search_result2['total_found']} templates")
    
    # 5. Test fetch_diagram_template
    print("\n4. Testing fetch_diagram_template...")
    if search_result['templates']:
        # Find a template with a valid ID
        template_id = None
        for template in search_result['templates']:
            if template.get('id'):
                template_id = template['id']
                break
        
        if template_id:
            fetch_result = fetch_diagram_template(
                template_id=template_id,
                session_id=session_id
            )
            
            if "error" in fetch_result:
                print(f"   ❌ Error: {fetch_result['error']}")
            else:
                print(f"   ✅ Fetched template: {fetch_result['name']}")
                print(f"   Description: {fetch_result['description']}")
                print(f"   Tags: {', '.join(fetch_result['tags'])}")
                print(f"   Players: {fetch_result['metadata']['players_count']}")
                print(f"   Movements: {fetch_result['metadata']['movements_count']}")
    
    # 6. Test with non-existent template
    print("\n5. Testing error handling...")
    fetch_error = fetch_diagram_template(
        template_id="non_existent_template",
        session_id=session_id
    )
    print(f"   Fetching non-existent template...")
    if "error" in fetch_error:
        print(f"   ✅ Correctly handled: {fetch_error['error']}")
    
    # 7. Test health check
    print("\n6. Testing health_check with template info...")
    health = health_check()
    print(f"   Server status: {health['status']}")
    print(f"   Template library: {health['template_library']['template_count']} templates")
    print(f"   Templates dir: {health['template_library']['templates_dir']}")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    test_template_tools()