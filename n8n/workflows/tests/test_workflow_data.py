#!/usr/bin/env python3
"""
Test the data flow for n8n workflow.
Simulates what n8n nodes would see.
"""

import json
import requests

# Simulate Generate Spec output
generate_spec_output = {
    "message": {
        "content": json.dumps({
            "schema_version": "0.1",
            "type": "drill",
            "title": "Test Drill",
            "players": [
                {"id": "X1", "role": "X", "location": {"landmark": "center_dot"}}
            ],
            "drill": {
                "sequence": [
                    {
                        "step": 1,
                        "actions": [
                            {"actor": "X1", "action": "skate", "from_landmark": "center_dot", "to_landmark": "blue_line_right"}
                        ]
                    }
                ]
            }
        })
    }
}

# Parse spec like n8n would
spec = json.loads(generate_spec_output["message"]["content"])
print("1. Generated Spec:")
print(json.dumps(spec, indent=2))

# Call renderer like n8n would
response = requests.post("http://localhost:5002/render", json={"spec": spec})
render_output = response.json()
print("\n2. Render Output Keys:", list(render_output.keys()))
print("   Image URL type:", type(render_output.get("image_url")))
print("   Image URL prefix:", render_output.get("image_url", "")[:50] + "...")

# Format Output node would create:
format_output = {
    "status": "ok",
    "spec": spec,
    "diagram": render_output
}

print("\n3. Format Output structure:")
print("   Keys:", list(format_output.keys()))
print("   $json.diagram.image_url exists:", "image_url" in format_output["diagram"])
print("   $json.spec.title:", format_output["spec"]["title"])
print("   $json.status:", format_output["status"])

# What HTML node would access
print("\n4. HTML Node would access:")
print("   $json.diagram.image_url: data URI with", len(format_output["diagram"]["image_url"]), "characters")
print("   $json.spec.players count:", len(format_output["spec"]["players"]))
print("   $json.spec.drill.sequence.length:", len(format_output["spec"]["drill"]["sequence"]))