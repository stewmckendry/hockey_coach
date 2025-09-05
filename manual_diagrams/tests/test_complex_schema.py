#!/usr/bin/env python3
"""Test if complex schema still gets output_text with MCP."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

client = OpenAI()

# Load the prompt config to get the exact instructions
config_path = "config/prompts/analyze_hockey_query.json"
with open(config_path, 'r') as f:
    prompt_config = json.load(f)

def test_with_complex_schema():
    """Test with the actual complex schema from our implementation."""
    
    print("Testing Complex Schema with MCP")
    print("=" * 60)
    
    query = "Michigan move hockey technique"
    
    # Use the exact schema from our implementation
    json_schema = {
        "type": "json_schema",
        "name": "hockey_analysis",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "original_query": {"type": "string"},
                "explicit_info": {
                    "type": "object",
                    "properties": {
                        "situation": {"type": ["string", "null"]},
                        "zone": {"type": ["string", "null"]},
                        "key_actions": {"type": "array", "items": {"type": "string"}},
                        "faceoff_location": {"type": ["string", "null"]}
                    },
                    "required": ["situation", "zone", "key_actions", "faceoff_location"],
                    "additionalProperties": False
                },
                "components_with_assumptions": {
                    "type": "object",
                    "properties": {
                        "rink": {"type": "object", "additionalProperties": False},
                        "players": {"type": "array", "items": {"type": "object", "additionalProperties": False}},
                        "movements": {"type": "array", "items": {"type": "object", "additionalProperties": False}},
                        "zones": {"type": "array", "items": {"type": "object", "additionalProperties": False}},
                        "annotations": {"type": "array", "items": {"type": "object", "additionalProperties": False}},
                        "equipment": {"type": "array", "items": {"type": "object", "additionalProperties": False}},
                        "coaches": {"type": "array", "items": {"type": "object", "additionalProperties": False}}
                    },
                    "required": ["rink", "players", "movements", "zones", "annotations", "equipment", "coaches"],
                    "additionalProperties": False
                },
                "questions_for_user": {"type": "array", "items": {"type": "object", "additionalProperties": False}},
                "metadata": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "phase": {"type": "string"},
                        "key_players": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["type", "phase", "key_players"],
                    "additionalProperties": False
                }
            },
            "required": ["original_query", "explicit_info", "components_with_assumptions", "questions_for_user", "metadata"],
            "additionalProperties": False
        }
    }
    
    # Use the instructions from config
    system_prompt = prompt_config["system_prompt"]
    
    response = client.responses.create(
        model="gpt-4o-mini",
        instructions=system_prompt + "\n\nProvide the complete JSON analysis.",
        input=[{
            "type": "message",
            "role": "user",
            "content": f"Analyze this hockey technique: {query}"
        }],
        tools=[{
            "type": "mcp",
            "server_label": "exa",
            "server_url": f"https://mcp.exa.ai/mcp?exaApiKey={os.getenv('EXA_API_KEY')}",
            "require_approval": "never",
            "allowed_tools": ["web_search_exa"]
        }],
        text={"format": json_schema},
        max_output_tokens=4000
    )
    
    print(f"Response ID: {response.id}")
    print(f"Has output_text: {hasattr(response, 'output_text')}")
    print(f"output_text populated: {bool(response.output_text) if hasattr(response, 'output_text') else False}")
    
    if response.output_text:
        print("\n✅ Complex schema WITH MCP returned output_text!")
        print(f"Output length: {len(response.output_text)} chars")
        print("Manual continuation NOT needed!")
        
        # Try to parse
        try:
            # Check if it's markdown wrapped
            if "```json" in response.output_text:
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', response.output_text, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(1))
                    print(f"Extracted from markdown. Keys: {list(parsed.keys())[:5]}")
            else:
                parsed = json.loads(response.output_text)
                print(f"Direct JSON. Keys: {list(parsed.keys())[:5]}")
        except Exception as e:
            print(f"Parse error: {e}")
    else:
        print("\n⚠️ Complex schema did NOT return output_text")
        print("Manual continuation IS needed")
        if hasattr(response, 'output'):
            print(f"Output items: {[item.type for item in response.output[:5]]}")

if __name__ == "__main__":
    test_with_complex_schema()