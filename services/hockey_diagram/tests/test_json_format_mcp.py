#!/usr/bin/env python3
"""Test SDK behavior with MCP when requesting JSON format."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

def test_with_json_format():
    """Test Responses API with MCP and JSON format request."""
    
    print("Testing with JSON Format Request")
    print("=" * 60)
    
    # Query that should trigger MCP
    query = "What is the Gretzky office in hockey?"
    
    response = client.responses.create(
        model="gpt-4o-mini",
        instructions="""You are a hockey expert. Search for unfamiliar terms before answering.
        
        IMPORTANT: After searching, provide your final answer ONLY as JSON with this structure:
        {
            "term": "the term explained",
            "definition": "detailed definition",
            "origin": "how it got this name"
        }
        
        Output ONLY the JSON, no other text.""",
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
        print("\n✅ SDK populated output_text with JSON format!")
        print(f"Content: {response.output_text[:500]}...")
    else:
        print("\n⚠️ SDK did not populate output_text with JSON format")
        print("Output items:")
        if hasattr(response, 'output'):
            for i, item in enumerate(response.output[:5]):
                print(f"  {i}: {item.type}")

if __name__ == "__main__":
    test_with_json_format()