#!/usr/bin/env python3
"""Test if manual continuation is still needed with structured outputs."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

client = OpenAI()

def test_with_structured_output():
    """Test if structured output alone gives us the final answer after MCP."""
    
    print("Testing Structured Output with MCP")
    print("=" * 60)
    
    # Query that should trigger MCP
    query = "What is the Michigan move in hockey?"
    
    # Define the JSON schema (simplified version)
    json_schema = {
        "type": "json_schema",
        "name": "hockey_analysis",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "term": {"type": "string"},
                "definition": {"type": "string"},
                "key_elements": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["term", "definition", "key_elements"],
            "additionalProperties": False
        }
    }
    
    response = client.responses.create(
        model="gpt-4o-mini",
        instructions="You are a hockey expert. Search for information about unfamiliar terms before answering. Provide a structured analysis.",
        input=[{
            "type": "message",
            "role": "user",
            "content": f"Analyze this hockey term: {query}"
        }],
        tools=[{
            "type": "mcp",
            "server_label": "exa",
            "server_url": f"https://mcp.exa.ai/mcp?exaApiKey={os.getenv('EXA_API_KEY')}",
            "require_approval": "never",
            "allowed_tools": ["web_search_exa"]
        }],
        text={"format": json_schema},
        max_output_tokens=2000
    )
    
    print(f"Response ID: {response.id}")
    print(f"Has output_text: {hasattr(response, 'output_text')}")
    print(f"output_text is populated: {bool(response.output_text) if hasattr(response, 'output_text') else False}")
    
    if response.output_text:
        print("\n✅ Structured output ALONE provided the final answer!")
        print(f"Output length: {len(response.output_text)} chars")
        try:
            parsed = json.loads(response.output_text)
            print(f"Valid JSON: {list(parsed.keys())}")
        except:
            print("Not valid JSON - might be markdown wrapped")
    else:
        print("\n⚠️ Structured output did NOT provide final answer after MCP")
        print("Output items:")
        if hasattr(response, 'output'):
            for i, item in enumerate(response.output[:5]):
                print(f"  {i}: {item.type}")
        print("\n➡️ Manual continuation is STILL NEEDED")

if __name__ == "__main__":
    test_with_structured_output()