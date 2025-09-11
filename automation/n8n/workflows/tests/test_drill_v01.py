#!/usr/bin/env python3
"""
Test script for Drill Renderer v0.1
Tests the example drill specification.
"""

import json
import requests

# Example drill spec v0.1
example_spec = {
    "schema_version": "0.1",
    "type": "drill",
    "title": "Two-Line NZ Half-Circle Give-and-Go, Shot",
    "players": [
        {"id": "X1", "role": "X", "location": {"landmark": "right_boards"}},
        {"id": "X2", "role": "X", "location": {"landmark": "left_boards"}},
        {"id": "C1", "role": "C", "location": {"landmark": "right_hashmarks"}},
        {"id": "C2", "role": "C", "location": {"landmark": "left_hashmarks"}},
        {"id": "G1", "role": "G", "location": {"landmark": "behind_net"}},
        {"id": "G2", "role": "G", "location": {"landmark": "behind_net", "offset": {"dx": -0.8, "dy": 0.0}}}
    ],
    "drill": {
        "sequence": [
            {
                "step": 1,
                "actions": [
                    {
                        "actor": "X1",
                        "action": "skate",
                        "from_landmark": "right_boards",
                        "to_landmark": "blue_line_right",
                        "path": {
                            "type": "arc",
                            "around_landmark": "center_dot",
                            "direction": "cw",
                            "sweep_degrees": 180
                        }
                    },
                    {
                        "actor": "X2",
                        "action": "skate",
                        "from_landmark": "left_boards",
                        "to_landmark": "blue_line_left",
                        "path": {
                            "type": "arc",
                            "around_landmark": "center_dot",
                            "direction": "ccw",
                            "sweep_degrees": 180
                        }
                    }
                ]
            },
            {
                "step": 2,
                "actions": [
                    {"actor": "X1", "action": "pass", "from_landmark": "blue_line_right", "to_landmark": "right_hashmarks"},
                    {"actor": "C1", "action": "pass", "from_landmark": "right_hashmarks", "to_landmark": "right_hashmarks"},
                    {"actor": "X2", "action": "pass", "from_landmark": "blue_line_left", "to_landmark": "left_hashmarks"},
                    {"actor": "C2", "action": "pass", "from_landmark": "left_hashmarks", "to_landmark": "left_hashmarks"}
                ]
            },
            {
                "step": 3,
                "actions": [
                    {"actor": "X1", "action": "skate", "from_landmark": "right_hashmarks", "to_landmark": "low_slot"},
                    {"actor": "X1", "action": "shoot", "from_landmark": "low_slot", "to_landmark": "low_slot"},
                    {"actor": "X2", "action": "skate", "from_landmark": "left_hashmarks", "to_landmark": "low_slot"},
                    {"actor": "X2", "action": "shoot", "from_landmark": "low_slot", "to_landmark": "low_slot"}
                ]
            }
        ]
    }
}

def test_renderer():
    """Test the drill renderer with example spec."""
    url = "http://localhost:5002/render"
    
    payload = {
        "spec": example_spec
    }
    
    print("Testing Drill Renderer v0.1...")
    print(f"Sending spec to {url}")
    print(f"Spec title: {example_spec['title']}")
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Rendering successful!")
            print(f"Image URL length: {len(data.get('image_url', ''))} characters")
            print(f"Warnings: {data.get('warnings', [])}")
            
            # Save image URL to file for inspection
            with open("drill_output.txt", "w") as f:
                f.write(data.get('image_url', ''))
            print("Image URL saved to drill_output.txt")
            
            # Extract base64 and save as image
            if data.get('image_url', '').startswith('data:image/png;base64,'):
                import base64
                from pathlib import Path
                
                base64_str = data['image_url'].replace('data:image/png;base64,', '')
                img_data = base64.b64decode(base64_str)
                
                output_path = Path("drill_diagram_test.png")
                output_path.write_bytes(img_data)
                print(f"✅ Image saved to {output_path}")
            
        else:
            print(f"❌ Error {response.status_code}")
            print(response.json())
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to renderer")
        print("Make sure the renderer is running: python drill_renderer_v01.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_renderer()