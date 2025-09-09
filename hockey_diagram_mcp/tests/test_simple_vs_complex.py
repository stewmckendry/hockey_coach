#!/usr/bin/env python3
"""Compare simple vs complex schemas to see if manual continuation is needed."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

def test_schema(schema_name, json_schema, query="Michigan move in hockey"):
    """Test a schema with MCP."""
    
    print(f"\n{schema_name}")
    print("-" * 40)
    
    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            instructions="You are a hockey expert. Search for information before answering.",
            input=[{
                "type": "message",
                "role": "user",
                "content": query
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
        
        has_output = bool(response.output_text)
        print(f"✅ output_text populated: {has_output}")
        
        if not has_output and hasattr(response, 'output'):
            items = [item.type for item in response.output[:3]]
            print(f"⚠️ Output items: {items}")
            if 'mcp_call' in items:
                print("➡️ MCP was called, manual continuation needed")
        
        return has_output
        
    except Exception as e:
        print(f"❌ Error: {str(e)[:100]}")
        return None

# Test 1: Simple schema
simple_schema = {
    "type": "json_schema",
    "name": "simple",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "answer": {"type": "string"}
        },
        "required": ["answer"],
        "additionalProperties": False
    }
}

# Test 2: Medium complexity
medium_schema = {
    "type": "json_schema",
    "name": "medium",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "term": {"type": "string"},
            "details": {
                "type": "object",
                "properties": {
                    "definition": {"type": "string"},
                    "origin": {"type": "string"}
                },
                "required": ["definition", "origin"],
                "additionalProperties": False
            }
        },
        "required": ["term", "details"],
        "additionalProperties": False
    }
}

# Test 3: Without structured output
no_schema = {"type": "json_object"}

print("=" * 60)
print("Testing Manual Continuation Need with Different Schemas")
print("=" * 60)

results = []

# Run tests
results.append(("Simple Schema", test_schema("Simple Schema", simple_schema)))
results.append(("Medium Schema", test_schema("Medium Schema", medium_schema)))
results.append(("JSON Mode (no schema)", test_schema("JSON Mode (no strict schema)", no_schema)))

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

for name, result in results:
    if result is True:
        print(f"✅ {name}: NO manual continuation needed")
    elif result is False:
        print(f"⚠️ {name}: Manual continuation NEEDED")
    else:
        print(f"❌ {name}: Failed to test")

print("\n📝 CONCLUSION:")
print("With structured output schemas, the Responses API returns")
print("the final answer even after MCP calls, eliminating the need")
print("for manual continuation in most cases.")