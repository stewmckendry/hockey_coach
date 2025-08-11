#!/usr/bin/env python3
"""
Test script for interactive editing flow
Tests the power play scenario from design document
"""

import requests
import json
import time
import base64
from typing import Dict, Any

# Configuration
MCP_SERVER_URL = "http://localhost:8001"
API_BASE_URL = "http://localhost:3000/api/hockey-diagram"

# Import sys and add the server path to use the local server module directly
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'servers', 'hockey_diagram_mcp'))

def test_mcp_connection():
    """Test MCP server connection"""
    print("1. Testing MCP server connection...")
    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": 1
            }
        )
        if response.status_code == 200:
            tools = response.json()
            tool_names = [t['name'] for t in tools.get('result', {}).get('tools', [])]
            if 'process_diagram_feedback' in tool_names:
                print("✅ MCP server connected, feedback tool available")
                return True
            else:
                print("⚠️ MCP server connected but feedback tool not found")
                print(f"Available tools: {tool_names}")
        else:
            print(f"❌ MCP server error: {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to connect to MCP server: {e}")
    return False

def generate_initial_diagram() -> Dict[str, Any]:
    """Generate initial power play diagram"""
    print("\n2. Generating initial power play diagram...")
    
    prompt = "Show me a power play umbrella formation"
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/generate",
            json={"prompt": prompt}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Initial diagram generated successfully")
                print(f"   Parser type: {data.get('parserType', 'unknown')}")
                print(f"   Processing time: {data.get('processingTimeMs', 0)}ms")
                
                # Save image for visual inspection
                if data.get('imageBase64'):
                    with open('test_initial.png', 'wb') as f:
                        img_data = data['imageBase64']
                        if img_data.startswith('data:'):
                            img_data = img_data.split(',')[1]
                        f.write(base64.b64decode(img_data))
                    print("   Saved to: test_initial.png")
                
                return data
            else:
                print(f"❌ Generation failed: {data.get('error')}")
        else:
            print(f"❌ API error: {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to generate diagram: {e}")
    
    return None

def test_feedback_processing(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Test feedback processing"""
    print("\n3. Testing feedback processing...")
    
    feedback = "Move F2 down lower to the goal line for a low umbrella"
    print(f"   Feedback: {feedback}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/feedback-processor",
            json={
                "currentSpec": spec,
                "feedback": feedback
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Feedback processed successfully")
                print(f"   Explanation: {data.get('explanation')}")
                
                # Print changes
                changes = data.get('changes', [])
                if changes:
                    print(f"   Changes ({len(changes)}):")
                    for change in changes:
                        print(f"     - {change['type']}: {change['details']}")
                
                # Print suggestions
                suggestions = data.get('suggestions', [])
                if suggestions:
                    print(f"   Suggestions: {', '.join(suggestions)}")
                
                return data
            else:
                print(f"❌ Feedback processing failed: {data.get('error')}")
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Failed to process feedback: {e}")
    
    return None

def generate_from_updated_spec(spec: Dict[str, Any]) -> bool:
    """Generate diagram from updated spec"""
    print("\n4. Generating diagram from updated spec...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/generate-from-spec",
            json={"spec": spec}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Diagram regenerated successfully")
                print(f"   Processing time: {data.get('processingTime', 0)}ms")
                
                # Save updated image
                if data.get('imageBase64'):
                    with open('test_updated.png', 'wb') as f:
                        img_data = data['imageBase64']
                        if img_data.startswith('data:'):
                            img_data = img_data.split(',')[1]
                        f.write(base64.b64decode(img_data))
                    print("   Saved to: test_updated.png")
                
                return True
            else:
                print(f"❌ Generation failed: {data.get('error')}")
        else:
            print(f"❌ API error: {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to generate from spec: {e}")
    
    return False

def test_multiple_modifications(spec: Dict[str, Any]):
    """Test multiple sequential modifications"""
    print("\n5. Testing multiple modifications...")
    
    modifications = [
        "Add passing lanes between F1 and both wingers",
        "Show forechecking pressure with an opposing player",
        "Move the center forward into the slot area"
    ]
    
    current_spec = spec
    for i, feedback in enumerate(modifications, 1):
        print(f"\n   Modification {i}: {feedback}")
        
        response = requests.post(
            f"{API_BASE_URL}/feedback-processor",
            json={
                "currentSpec": current_spec,
                "feedback": feedback
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ Applied: {data.get('explanation')}")
                current_spec = data.get('updatedSpec')
            else:
                print(f"   ❌ Failed: {data.get('error')}")
                break
        else:
            print(f"   ❌ API error: {response.status_code}")
            break
    
    # Generate final diagram
    if current_spec != spec:
        print("\n   Generating final diagram with all modifications...")
        generate_from_updated_spec(current_spec)

def main():
    """Run interactive editing tests"""
    print("=" * 60)
    print("Hockey Diagram Interactive Editing Test")
    print("=" * 60)
    
    # Test MCP connection
    if not test_mcp_connection():
        print("\n⚠️ Cannot proceed without MCP server")
        return
    
    # Generate initial diagram
    initial_result = generate_initial_diagram()
    if not initial_result or not initial_result.get('parserSpec'):
        print("\n⚠️ Cannot proceed without initial diagram spec")
        return
    
    spec = initial_result['parserSpec']
    print(f"\n   Initial spec has {len(spec.get('players', []))} players")
    
    # Test single feedback
    feedback_result = test_feedback_processing(spec)
    if feedback_result and feedback_result.get('updatedSpec'):
        updated_spec = feedback_result['updatedSpec']
        
        # Generate from updated spec
        generate_from_updated_spec(updated_spec)
        
        # Test multiple modifications
        test_multiple_modifications(updated_spec)
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("Check test_initial.png and test_updated.png to compare results")
    print("=" * 60)

if __name__ == "__main__":
    main()