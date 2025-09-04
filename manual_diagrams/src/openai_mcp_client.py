#!/usr/bin/env python3
"""
OpenAI client that uses MCP servers directly for hockey diagram analysis.
This demonstrates using the Responses API with MCP tools for enhanced capabilities.
"""

import os
import json
from typing import Dict, Any, Optional, List
from openai import OpenAI
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_hockey_with_mcp(
    query: str, 
    mcp_servers: Optional[List[Dict[str, Any]]] = None,
    use_exa: bool = True
) -> Dict[str, Any]:
    """
    Analyze hockey query using OpenAI with direct MCP integration.
    
    Args:
        query: Hockey drill/play description
        mcp_servers: Optional list of MCP server configurations
        use_exa: Whether to include Exa MCP for web search
        
    Returns:
        Analysis result from OpenAI with MCP tool results
    """
    
    # Default MCP servers if not provided
    if mcp_servers is None:
        mcp_servers = []
        
        # Add our hockey diagram MCP server
        mcp_servers.append({
            "type": "mcp",
            "server_label": "hockey_diagram",
            "server_url": "http://localhost:8001",  # Our v3 server
            "allowed_tools": ["analyze_hockey_query", "test_analyze_query"],
            "require_approval": "never"
        })
        
        # Optionally add Exa for web search
        if use_exa:
            mcp_servers.append({
                "type": "mcp", 
                "server_label": "exa_search",
                "server_url": "http://localhost:8002",  # Exa MCP server
                "allowed_tools": ["web_search_exa", "company_research_exa"],
                "require_approval": "never"
            })
    
    # Build the prompt
    system_prompt = """You are a hockey coach analyzing drills and plays. 
    Use the available MCP tools to:
    1. Analyze the hockey query for components needed
    2. Search for any unclear hockey terms if needed
    3. Provide a complete diagram specification"""
    
    user_prompt = f"""Analyze this hockey drill/play and create a diagram specification:

{query}

Instructions:
1. First use the hockey_diagram MCP server's analyze_hockey_query tool
2. If any terms are unclear, use the exa_search MCP to look them up
3. Return a complete analysis with all players and movements identified"""

    try:
        # Make the API call with MCP tools
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            tools=mcp_servers,
            tool_choice="auto",
            max_tokens=3000,
            temperature=0.3
        )
        
        # Extract the response
        message = response.choices[0].message
        
        # Parse any tool calls that were made
        tool_results = []
        if hasattr(message, 'tool_calls') and message.tool_calls:
            for tool_call in message.tool_calls:
                tool_results.append({
                    "tool": tool_call.function.name,
                    "server": tool_call.function.server_label if hasattr(tool_call.function, 'server_label') else "unknown",
                    "result": tool_call.function.arguments if hasattr(tool_call.function, 'arguments') else None
                })
        
        return {
            "success": True,
            "analysis": message.content,
            "tool_calls": tool_results,
            "original_query": query
        }
        
    except Exception as e:
        logger.error(f"Analysis with MCP failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "original_query": query
        }


def test_mcp_client():
    """Test the MCP client with the faceoff example."""
    
    # Test query
    query = """build a hockey diagram of an offensive zone faceoff. 
    The play is to bump the puck back and the weak side winger swings over 
    to grab puck and take a shot. Faceoff is at right dot."""
    
    print("🏒 Testing OpenAI with Direct MCP Integration")
    print("=" * 60)
    print(f"Query: {query}")
    print("-" * 60)
    
    # Run analysis
    result = analyze_hockey_with_mcp(query, use_exa=False)  # Start without Exa
    
    if result["success"]:
        print("\n✅ Analysis successful!")
        print("\n📊 Analysis Result:")
        print(result["analysis"])
        
        if result["tool_calls"]:
            print("\n🛠️ MCP Tools Used:")
            for tool in result["tool_calls"]:
                print(f"  - {tool['tool']} from {tool['server']}")
    else:
        print(f"\n❌ Analysis failed: {result['error']}")
    
    # Now test with Exa for term lookup
    print("\n" + "=" * 60)
    print("🔍 Testing with Exa MCP for term lookup...")
    
    query_with_term = """Create a hockey diagram showing a 'Michigan move' 
    in the offensive zone."""
    
    result = analyze_hockey_with_mcp(query_with_term, use_exa=True)
    
    if result["success"]:
        print("\n✅ Analysis with web search successful!")
        if result["tool_calls"]:
            print("\n🛠️ MCP Tools Used:")
            for tool in result["tool_calls"]:
                print(f"  - {tool['tool']} from {tool['server']}")


def create_mcp_config_example():
    """Create an example configuration for using multiple MCP servers."""
    
    config = {
        "mcp_servers": [
            {
                "type": "mcp",
                "server_label": "hockey_diagram",
                "server_url": "http://localhost:8001",
                "description": "Hockey diagram analysis and generation",
                "allowed_tools": [
                    "analyze_hockey_query",
                    "map_position_to_coordinates", 
                    "map_movement_to_coordinates",
                    "validate_diagram_spec_full",
                    "generate_diagram"
                ],
                "require_approval": "never"
            },
            {
                "type": "mcp",
                "server_label": "exa_search",
                "server_url": "http://localhost:8002", 
                "description": "Web search for hockey terms and tactics",
                "allowed_tools": [
                    "web_search_exa",
                    "company_research_exa"
                ],
                "require_approval": "auto"
            },
            {
                "type": "mcp",
                "server_label": "hockey_kb",
                "server_url": "http://localhost:8003",
                "description": "Hockey knowledge base search",
                "allowed_tools": [
                    "search_hockey_tactics",
                    "search_hockey_drills",
                    "search_hockey_skills"
                ],
                "require_approval": "never"
            }
        ],
        "model_config": {
            "model": "gpt-4o-mini",
            "temperature": 0.3,
            "max_tokens": 3000
        }
    }
    
    # Save config example
    config_path = "/Users/liammckendry/hockey_coach_issue-111/manual_diagrams/config/mcp_client_config.json"
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ MCP configuration saved to {config_path}")
    return config


if __name__ == "__main__":
    # Create configuration example
    print("📝 Creating MCP configuration example...")
    create_mcp_config_example()
    print()
    
    # Note about direct MCP in OpenAI
    print("ℹ️ Note: Direct MCP integration in OpenAI Responses API requires:")
    print("  - OpenAI API with Responses endpoint access")
    print("  - MCP servers running and accessible")
    print("  - Proper server URLs in configuration")
    print()
    
    # For now, demonstrate the pattern
    print("🎯 This example demonstrates the pattern for direct MCP usage.")
    print("   When OpenAI Responses API is available, this will work directly.")
    print("   For now, we can simulate with function calling.\n")
    
    # Test the client (will use function calling simulation for now)
    # test_mcp_client()