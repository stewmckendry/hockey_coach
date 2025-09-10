"""
Hockey diagram generation tools for OpenAI Agents SDK.
These are properly decorated function tools that can be used by agents.
"""
import json
from typing import Dict, Any
from agents import function_tool
from agents.tracing import custom_span, function_span

# Import core functionality
from core_tools import (
    parse_hockey_formation_core,
    generate_diagram_from_spec_core,
    list_formations_core
)

@function_tool
async def parse_hockey_formation(prompt: str, parser_type: str = "agent") -> str:
    """Parse a hockey formation description into structured data.
    
    Args:
        prompt: Natural language description of the hockey formation/play
        parser_type: Parser to use - 'agent' (default), 'two_stage', or 'simple'
        
    Returns:
        JSON string with parsed formation data or error information
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"🎯 parse_hockey_formation called with: {prompt}")
    
    # Use SDK function_span for tracing
    with function_span(
        name="parse_hockey_formation",
        input=json.dumps({"prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt, "parser_type": parser_type})
    ) as span:
        try:
            if parser_type == "agent":
                # Use the parser agent (recommended approach)
                from parser_agent import parse_with_agent
                result_json = await parse_with_agent(prompt)
                result = json.loads(result_json)
                
                # Log tool traces if present
                if result.get("tool_traces"):
                    logger.info(f"🔍 Parser agent tool traces: {len(result.get('tool_traces', []))} tools used")
                    for trace in result.get("tool_traces", []):
                        logger.info(f"  - {trace.get('name')}")
                        
            elif parser_type == "simple":
                # Use simple pattern matching
                from parser_agent import parse_simple
                result_json = await parse_simple(prompt)
                result = json.loads(result_json)
            else:
                # Fall back to original two-stage parser
                result = await parse_hockey_formation_core(prompt, parser_type)
            
            logger.info(f"✅ Parser returned: success={result.get('success')}")
            json_result = json.dumps(result)
            logger.info(f"📦 Returning JSON of length: {len(json_result)}")
            
            # Update span with output
            if span:
                span.span_data.output = json.dumps({
                    "success": result.get("success"),
                    "parser_used": result.get("parser", parser_type),
                    "tool_count": len(result.get("tool_traces", []))
                })
            
            return json_result
        except Exception as e:
            logger.error(f"❌ Error in parse_hockey_formation: {e}")
            return json.dumps({"success": False, "error": str(e)})

@function_tool
async def generate_diagram_from_spec(diagram_spec: str, output_format: str = "png") -> str:
    """Generate a hockey diagram from parsed specification.
    
    Args:
        diagram_spec: JSON string of parsed diagram specification (from parse_hockey_formation)
        output_format: Output format - 'png' or 'svg' (default: png)
        
    Returns:
        JSON string containing diagram path and generation details
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"🎨 generate_diagram_from_spec called")
    
    try:
        spec_dict = json.loads(diagram_spec) if isinstance(diagram_spec, str) else diagram_spec
        logger.info(f"📊 Parsed spec with {len(spec_dict.get('players', []))} players")
        result = await generate_diagram_from_spec_core(spec_dict, output_format)
        logger.info(f"✅ generate_diagram_from_spec_core returned: success={result.get('success')}")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"❌ Error in generate_diagram_from_spec: {e}")
        return json.dumps({"success": False, "error": str(e)})

@function_tool
def list_hockey_formations() -> str:
    """List all available preset hockey formations.
    
    Returns:
        JSON string containing available formations by category
    """
    return json.dumps(list_formations_core())