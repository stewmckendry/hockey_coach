#!/usr/bin/env python3
"""Dump the raw OpenAI response object to understand MCP structure."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

def dump_response_structure():
    """Make an MCP call and dump the full response structure at each turn."""
    
    print("=" * 80)
    print("Testing Raw Response Structure with MCP")
    print("=" * 80)
    
    # Query that should trigger MCP
    query = "Explain the Kucherov no-look saucer pass technique"
    
    # First call - should trigger MCP
    print("\n1. FIRST API CALL (should trigger MCP):")
    print("-" * 60)
    
    response1 = client.responses.create(
        model="gpt-4o-mini",
        instructions="You are a hockey expert. Search for information about unfamiliar terms before answering. Always provide a complete JSON analysis after any searches.",
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
        max_output_tokens=4000
    )
    
    # Dump first response
    print(f"Response ID: {response1.id}")
    print(f"Response type: {type(response1)}")
    print(f"Has output_text: {hasattr(response1, 'output_text')}")
    print(f"output_text value: {response1.output_text[:100] if response1.output_text else 'None/Empty'}")
    print(f"Has output: {hasattr(response1, 'output')}")
    
    if hasattr(response1, 'output') and response1.output:
        print(f"\nOutput items ({len(response1.output)}):")
        for i, item in enumerate(response1.output):
            print(f"  Item {i}: type={item.type}")
            
            # Dump full item structure
            item_dict = {}
            for attr in dir(item):
                if not attr.startswith('_'):
                    try:
                        value = getattr(item, attr)
                        if not callable(value):
                            if attr == 'output' and len(str(value)) > 200:
                                item_dict[attr] = str(value)[:200] + "..."
                            else:
                                item_dict[attr] = value
                    except:
                        pass
            
            print(f"    Full structure: {json.dumps(item_dict, indent=6, default=str)[:500]}")
    
    # Save first response
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / "raw_response_1.json", 'w') as f:
        # Convert response to dict
        resp1_dict = {
            "id": response1.id,
            "output_text": response1.output_text,
            "output_items": []
        }
        if hasattr(response1, 'output'):
            for item in response1.output:
                item_info = {
                    "type": item.type,
                }
                if hasattr(item, 'output'):
                    item_info["output_preview"] = str(item.output)[:500]
                if hasattr(item, 'name'):
                    item_info["name"] = item.name
                if hasattr(item, 'arguments'):
                    item_info["arguments"] = str(item.arguments)[:200]
                resp1_dict["output_items"].append(item_info)
        
        json.dump(resp1_dict, f, indent=2)
    
    # Check if we need continuation
    needs_continuation = False
    if hasattr(response1, 'output') and response1.output:
        for item in response1.output:
            if item.type in ['mcp_list_tools', 'mcp_call']:
                needs_continuation = True
                break
    
    if needs_continuation:
        print("\n" + "=" * 80)
        print("2. SECOND API CALL (continuation after MCP):")
        print("-" * 60)
        
        # Continue conversation
        response2 = client.responses.create(
            model="gpt-4o-mini",
            instructions="Based on the search results, provide the final JSON analysis.",
            input=[{
                "type": "message",
                "role": "user",
                "content": f"Continue analyzing: {query}"
            }],
            previous_response_id=response1.id,
            max_output_tokens=4000
        )
        
        print(f"Response ID: {response2.id}")
        print(f"Has output_text: {hasattr(response2, 'output_text')}")
        print(f"output_text value: {response2.output_text[:100] if response2.output_text else 'None/Empty'}")
        
        if hasattr(response2, 'output') and response2.output:
            print(f"\nOutput items ({len(response2.output)}):")
            for i, item in enumerate(response2.output):
                print(f"  Item {i}: type={item.type}")
                if item.type == 'message' and hasattr(item, 'content'):
                    print(f"    Has content: {len(item.content) if item.content else 0} items")
        
        # Save second response
        with open(output_dir / "raw_response_2.json", 'w') as f:
            resp2_dict = {
                "id": response2.id,
                "previous_response_id": response1.id,
                "output_text": response2.output_text,
                "output_items": []
            }
            if hasattr(response2, 'output'):
                for item in response2.output:
                    item_info = {"type": item.type}
                    if hasattr(item, 'content') and item.content:
                        item_info["content_length"] = len(item.content)
                    resp2_dict["output_items"].append(item_info)
            
            json.dump(resp2_dict, f, indent=2)
    
    print("\n" + "=" * 80)
    print("ANALYSIS:")
    print("-" * 60)
    print(f"MCP was {'triggered' if needs_continuation else 'NOT triggered'}")
    print(f"Manual continuation was {'required' if needs_continuation and not response1.output_text else 'NOT required'}")
    print("\nHYPOTHESIS CHECK:")
    print("If the SDK says it should automatically return the final answer after MCP,")
    print("but we're not getting output_text in response1, then either:")
    print("1. We're missing a configuration parameter")
    print("2. The response structure is different than expected")
    print("3. The MCP tool needs different setup")
    
    print(f"\nSaved raw responses to: {output_dir}")

if __name__ == "__main__":
    dump_response_structure()