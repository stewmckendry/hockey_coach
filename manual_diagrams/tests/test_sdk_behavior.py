#!/usr/bin/env python3
"""Test SDK behavior with MCP to understand when output_text is populated."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

def test_direct_api():
    """Test direct Responses API call with MCP."""
    
    print("Testing Direct API Call with MCP")
    print("=" * 60)
    
    # Simple query that should trigger MCP
    query = "What is the Gretzky office in hockey?"
    
    response = client.responses.create(
        model="gpt-4o-mini",
        instructions="You are a hockey expert. Search for information about unfamiliar terms before answering.",
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
        max_output_tokens=2000
    )
    
    print(f"Response ID: {response.id}")
    print(f"Has output_text: {hasattr(response, 'output_text')}")
    print(f"output_text is None: {response.output_text is None if hasattr(response, 'output_text') else 'N/A'}")
    print(f"output_text length: {len(response.output_text) if response.output_text else 0}")
    
    if response.output_text:
        print("\n✅ SDK populated output_text automatically!")
        print(f"First 300 chars: {response.output_text[:300]}...")
    else:
        print("\n⚠️ SDK did not populate output_text")
        print("Output items:")
        if hasattr(response, 'output'):
            for i, item in enumerate(response.output):
                print(f"  {i}: {item.type}")

if __name__ == "__main__":
    test_direct_api()