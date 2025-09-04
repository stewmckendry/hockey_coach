#!/usr/bin/env python3
"""
Test script to debug OpenAI Responses API with MCP tools
"""
import os
import json
import logging
from openai import OpenAI
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment
env_file = Path("/Users/liammckendry/thunder_playbook/.env")
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key.strip()] = value.strip().strip('"')

# Initialize client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def test_responses_api():
    """Test the Responses API with MCP tools"""
    
    # Get Exa API key
    exa_api_key = os.getenv("EXA_API_KEY")
    if not exa_api_key:
        logger.error("EXA_API_KEY not found")
        return
    
    # Check if Responses API is available
    if not hasattr(client, 'responses'):
        logger.error("Responses API not available in SDK")
        return
    
    logger.info("Testing Responses API with Exa MCP")
    
    # Build the request
    system_prompt = "You are a professional hockey coach and diagram expert."
    user_prompt = "Analyze this hockey query: offensive zone faceoff weak side winger swings over and shoots. Return a JSON object with the analysis."
    
    # Configure MCP tools
    tools = [{
        "type": "mcp",
        "server_label": "exa",
        "server_description": "Exa web search for hockey terminology",
        "server_url": f"https://mcp.exa.ai/mcp?exaApiKey={exa_api_key}",
        "require_approval": "never"
    }]
    
    # Try different API configurations
    configs = [
        {
            "name": "Config 1: Basic with tools",
            "params": {
                "model": "gpt-4o-mini",
                "tools": tools,
                "input": user_prompt,
                "instructions": system_prompt,
                "max_output_tokens": 2000,
                "max_tool_calls": 3,
                "parallel_tool_calls": False
            }
        },
        {
            "name": "Config 2: Without instructions",
            "params": {
                "model": "gpt-4o-mini",
                "tools": tools,
                "input": f"{system_prompt}\n\n{user_prompt}",
                "max_output_tokens": 2000,
                "max_tool_calls": 3,
                "parallel_tool_calls": False
            }
        },
        {
            "name": "Config 3: Messages format",
            "params": {
                "model": "gpt-4o-mini",
                "tools": tools,
                "input": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_output_tokens": 2000,
                "max_tool_calls": 3,
                "parallel_tool_calls": False
            }
        }
    ]
    
    for config in configs:
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing {config['name']}")
        logger.info(f"{'='*60}")
        
        try:
            # Make the API call
            response = client.responses.create(**config['params'])
            
            # Log response structure
            logger.info(f"Response type: {type(response)}")
            logger.info(f"Response attributes: {dir(response)}")
            
            # Try SDK helper
            if hasattr(response, 'output_text'):
                logger.info(f"✅ SDK output_text helper available")
                logger.info(f"Output text: {response.output_text[:200]}...")
            else:
                logger.info("❌ No output_text helper")
            
            # Check output structure
            if hasattr(response, 'output'):
                logger.info(f"Output type: {type(response.output)}")
                
                if isinstance(response.output, list):
                    logger.info(f"Output has {len(response.output)} items")
                    
                    for idx, item in enumerate(response.output):
                        item_type = getattr(item, 'type', type(item).__name__)
                        logger.info(f"  Item {idx}: type={item_type}")
                        
                        # Log item attributes
                        if hasattr(item, '__dict__'):
                            logger.info(f"    Attributes: {list(item.__dict__.keys())[:5]}")
                        
                        # Check for message type
                        if hasattr(item, 'type') and item.type == 'message':
                            logger.info(f"    Found message item!")
                            if hasattr(item, 'content'):
                                logger.info(f"    Content type: {type(item.content)}")
                                if isinstance(item.content, list) and item.content:
                                    for cidx, content in enumerate(item.content):
                                        content_type = getattr(content, 'type', 'unknown')
                                        logger.info(f"      Content {cidx}: type={content_type}")
                                        if content_type == 'output_text' and hasattr(content, 'text'):
                                            logger.info(f"      ✅ Found text: {content.text[:100]}...")
                        
                        # Check for McpListTools
                        elif type(item).__name__ == 'McpListTools':
                            logger.info(f"    Found McpListTools with {len(item.tools) if hasattr(item, 'tools') else 0} tools")
                            if hasattr(item, 'tools') and item.tools:
                                logger.info(f"    Available tools: {[t.name for t in item.tools[:3]]}")
                
                elif isinstance(response.output, str):
                    logger.info(f"Output is string: {response.output[:200]}...")
            
            # Try to extract text
            output_text = ""
            if hasattr(response, 'output_text'):
                output_text = response.output_text
            elif hasattr(response, 'output') and isinstance(response.output, list):
                for item in response.output:
                    if hasattr(item, 'type') and item.type == 'message':
                        if hasattr(item, 'content') and isinstance(item.content, list):
                            for content in item.content:
                                if hasattr(content, 'type') and content.type == 'output_text':
                                    if hasattr(content, 'text'):
                                        output_text = content.text
                                        break
                    if output_text:
                        break
            
            if output_text:
                logger.info(f"\n✅ Successfully extracted output text")
                logger.info(f"Output: {output_text[:500]}...")
            else:
                logger.warning("❌ Could not extract output text")
            
        except Exception as e:
            logger.error(f"Error with {config['name']}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

if __name__ == "__main__":
    test_responses_api()