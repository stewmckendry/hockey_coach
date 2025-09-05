#!/usr/bin/env python3
"""
Hockey Diagram MCP Server v3 - Clean Implementation
Uses OpenAI Responses API with Exa MCP for hockey term searches.
"""

from __future__ import annotations

import json
import logging
import sys
import os
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import asyncio
import uuid
from pydantic import BaseModel, Field

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
sys.path.append(str(Path(__file__).resolve().parent.parent / 'src'))
sys.path.append(str(Path(__file__).resolve().parent))  # Add servers directory for validators

from mcp.server.fastmcp import FastMCP

# Import validation and generation utilities from correct locations
from validators import validate_node, validate_spec, check_spatial_conflicts
from spec_converter import dict_to_diagram_spec, validate_spec_dict
from hockey_diagram_builder import DiagramBuilder, DiagramSpec

# Setup logging with both file and console output
from pathlib import Path
from datetime import datetime

log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"hockey_diagram_mcp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"=== MCP Server Started - Logging to {log_file} ===")

# Initialize MCP server
mcp = FastMCP(
    name="hockey-diagram-v3",
    version="3.0.2",
    description="Hockey Diagram MCP Server v3 - OpenAI Responses API with Exa MCP"
)

# OpenAI client
try:
    from openai import OpenAI
    from dotenv import load_dotenv
    
    # Load .env file
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        # Try parent directory
        load_dotenv(Path(__file__).parent.parent.parent / ".env")
    
    client = OpenAI() if os.getenv("OPENAI_API_KEY") else None
    if client:
        logger.info("✅ OpenAI client initialized successfully")
    else:
        logger.warning("⚠️ OpenAI API key not found")
except ImportError:
    client = None
    logger.warning("⚠️ OpenAI package not installed")

# ============================================================================
# CONFIGURATION LOADING
# ============================================================================

def load_prompt_config(prompt_name: str = "analyze_hockey_query") -> Dict[str, Any]:
    """Load prompt configuration from JSON file."""
    config_path = Path(__file__).parent.parent / "config" / "prompts" / f"{prompt_name}.json"
    
    if not config_path.exists():
        logger.warning(f"Prompt config not found at {config_path}, using defaults")
        return None
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            logger.info(f"✅ Loaded prompt config from {config_path}")
            return config
    except Exception as e:
        logger.error(f"Failed to load prompt config: {e}")
        return None

# Load prompt configuration on startup
PROMPT_CONFIG = load_prompt_config()

# ============================================================================
# MAIN MCP TOOL: QUERY ANALYSIS WITH EXA
# ============================================================================

@mcp.tool("analyze_hockey_query")
def analyze_hockey_query(
    query: str, 
    clarifications: Optional[Dict[str, Any]] = None, 
    use_exa_mcp: bool = True,
    exa_api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyzes a hockey drill query and extracts/enriches components needed for diagram spec.
    Uses OpenAI Responses API with Exa MCP for hockey term searches.
    
    Args:
        query: Natural language drill/play description
        clarifications: Optional user answers to questions
        use_exa_mcp: Whether to include Exa MCP server for web search (default: True)
        exa_api_key: Exa API key (uses EXA_API_KEY env var if not provided)
        
    Returns:
        Analysis with explicit info, assumptions, and components aligned to spec sections
    """
    
    if not client:
        return {
            "error": "OpenAI client not configured",
            "original_query": query,
            "suggestion": "Configure OPENAI_API_KEY to enable LLM analysis"
        }
    
    # Determine mode: initial analysis or refinement
    is_refinement = bool(clarifications and clarifications.get("previous_response_id"))
    mode = "refinement" if is_refinement else "initial"
    logger.info(f"🎯 Running in {mode} mode")
    
    # Build prompt from config
    if PROMPT_CONFIG:
        clarifications_text = ""
        if clarifications:
            # Filter out previous_response_id from clarifications list
            clarification_items = {k: v for k, v in clarifications.items() if k != "previous_response_id"}
            if clarification_items:
                clarifications_list = "\n".join([f"- {k}: {v}" for k, v in clarification_items.items()])
                clarifications_text = PROMPT_CONFIG["clarifications_template"].format(
                    clarifications_list=clarifications_list
                )
                logger.info(f"📝 Processing {len(clarification_items)} clarifications")
        
        # Add search instructions if Exa MCP is enabled
        search_instructions = ""
        if use_exa_mcp:
            search_instructions = PROMPT_CONFIG.get("search_instructions", "")
        
        prompt = PROMPT_CONFIG["main_prompt_template"].format(
            query=query,
            clarifications=clarifications_text,
            instructions=PROMPT_CONFIG["instructions"] + search_instructions,
            output_format=PROMPT_CONFIG["output_format"],
            hockey_knowledge=PROMPT_CONFIG["hockey_knowledge"]
        )
        
        system_prompt = PROMPT_CONFIG["system_prompt"]
        model_config = PROMPT_CONFIG.get("model_config", {})
    else:
        # Fallback prompts
        system_prompt = "You are a hockey coach and diagram expert."
        prompt = f"Analyze this hockey query: {query}"
        model_config = {
            "model": "gpt-4o-mini",
            "temperature": 0.3,
            "max_tokens": 2000,
            "response_format": {"type": "json_object"}
        }
    
    try:
        # Get Exa API key
        if not exa_api_key:
            exa_api_key = os.getenv("EXA_API_KEY")
        
        # Check if we should use Responses API
        use_responses_api = use_exa_mcp and exa_api_key and hasattr(client, 'responses')
        
        if use_responses_api:
            # Use OpenAI Responses API with Exa MCP
            logger.info("✨ Using OpenAI Responses API with Exa MCP")
            
            # Build tools array with Exa MCP
            tools = []
            if use_exa_mcp and exa_api_key:
                tools.append({
                    "type": "mcp",
                    "server_label": "exa",
                    "server_description": "Exa web search for hockey terminology and tactics",
                    "server_url": f"https://mcp.exa.ai/mcp?exaApiKey={exa_api_key}",
                    "require_approval": "never",  # Skip approval for automatic execution
                    "allowed_tools": ["web_search_exa"]  # Only use the web search tool
                })
            
            # Prepare the Responses API request with proper attributes
            api_request = {
                "model": model_config.get("model", "gpt-4o-mini"),
                "tools": tools,
                "input": prompt,  # User message/prompt
                "instructions": system_prompt + "\n\nCRITICAL: After any MCP tool calls complete, you MUST provide the final JSON analysis incorporating the search results. Do not stop after tool calls - always conclude with the complete JSON response.",  # Enhanced instructions
                "max_output_tokens": model_config.get("max_tokens", 4000),  # Increased for search-enriched responses
                "max_tool_calls": 3,  # Limit tool calls to avoid excessive API usage
                "parallel_tool_calls": False,  # Disable for structured outputs compatibility
            }
            
            # Add structured output format if JSON is requested
            if model_config.get("response_format", {}).get("type") == "json_object":
                api_request["text"] = {
                    "format": {
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
                                        "rink": {
                                            "type": "object",
                                            "properties": {
                                                "view": {"type": "string"},
                                                "assumption": {"type": "string"},
                                                "confidence": {"type": "number"}
                                            },
                                            "required": ["view", "assumption", "confidence"],
                                            "additionalProperties": False
                                        },
                                        "players": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {"type": "string"},
                                                    "type": {"type": "string"},
                                                    "team": {"type": "string"},
                                                    "position_desc": {"type": "string"},
                                                    "assumption": {"type": "string"},
                                                    "confidence": {"type": "number"}
                                                },
                                                "required": ["id", "type", "team", "position_desc", "assumption", "confidence"],
                                                "additionalProperties": False
                                            }
                                        },
                                        "movements": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {"type": "string"},
                                                    "type": {"type": "string"},
                                                    "desc": {"type": "string"},
                                                    "from_player": {"type": "string"},
                                                    "to_area": {"type": "string"},
                                                    "assumption": {"type": "string"},
                                                    "confidence": {"type": "number"}
                                                },
                                                "required": ["id", "type", "desc", "from_player", "to_area", "assumption", "confidence"],
                                                "additionalProperties": False
                                            }
                                        },
                                        "zones": {"type": "array", "items": {"type": "object", "properties": {}, "additionalProperties": False}},
                                        "annotations": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "text": {"type": "string"},
                                                    "position_desc": {"type": "string"},
                                                    "assumption": {"type": "string"},
                                                    "confidence": {"type": "number"}
                                                },
                                                "required": ["text", "position_desc", "assumption", "confidence"],
                                                "additionalProperties": False
                                            }
                                        },
                                        "equipment": {"type": "array", "items": {"type": "object", "properties": {}, "additionalProperties": False}}
                                    },
                                    "required": ["rink", "players", "movements", "zones", "annotations", "equipment"],
                                    "additionalProperties": False
                                },
                                "questions_for_user": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "question": {"type": "string"},
                                            "key": {"type": "string"},
                                            "options": {"type": "array", "items": {"type": "string"}},
                                            "critical": {"type": "boolean"},
                                            "confidence": {"type": "number"}
                                        },
                                        "required": ["question", "key", "options", "critical", "confidence"],
                                        "additionalProperties": False
                                    }
                                },
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
                }
            
            # Add previous_response_id for multi-turn conversations if clarifications were provided
            if clarifications and clarifications.get("previous_response_id"):
                api_request["previous_response_id"] = clarifications["previous_response_id"]
            
            # Make the Responses API call
            response = client.responses.create(**api_request)
            
            # Log the response type and structure for debugging
            logger.info(f"Response type: {type(response)}")
            
            # Store response_id for multi-turn conversations
            response_id = response.id if hasattr(response, 'id') else None
            logger.info(f"Response ID for multi-turn: {response_id}")
            
            # Extract the output from Responses API structure
            output_text = ""
            
            # The SDK provides an output_text helper that extracts the text
            # After MCP tool calls complete, this should contain the final answer
            if hasattr(response, 'output_text'):
                output_text = response.output_text
                if output_text:
                    logger.info(f"✅ SDK provided output_text: {len(output_text)} chars")
                    logger.info(f"First 200 chars: {output_text[:200]}")
                else:
                    logger.info("⚠️ SDK has output_text attribute but it's empty/None")
            else:
                logger.info("⚠️ Response has no output_text attribute")
            
            # If no output_text, manually extract from output array
            if not output_text:
                logger.info("Manually extracting from output array")
                if hasattr(response, 'output') and isinstance(response.output, list):
                    # Log all items for debugging
                    logger.info(f"Output has {len(response.output)} items")
                    for idx, item in enumerate(response.output):
                        item_type = getattr(item, 'type', type(item).__name__)
                        logger.info(f"Item {idx}: {item_type}")
                        
                        # Look for message type items (should be last after tool calls)
                        if hasattr(item, 'type') and item.type == 'message':
                            logger.info(f"Found message item at index {idx}")
                            if hasattr(item, 'content') and isinstance(item.content, list):
                                for content in item.content:
                                    if hasattr(content, 'type') and content.type == 'output_text':
                                        if hasattr(content, 'text'):
                                            output_text = content.text
                                            logger.info("✅ Found text in message content")
                                            break
                            if output_text:
                                break
                    
                    # If still no text, check the last item (but NOT if it's an mcp_call)
                    if not output_text and response.output:
                        last_item = response.output[-1]
                        item_type = getattr(last_item, 'type', type(last_item).__name__)
                        logger.info(f"Checking last item: {item_type}")
                        
                        # Don't extract from mcp_call items - that's tool output, not the final answer
                        if item_type != 'mcp_call':
                            if hasattr(last_item, 'output'):
                                output_text = str(last_item.output)
                                logger.info(f"Found output in last item: {output_text[:100]}")
                            elif hasattr(last_item, 'result'):
                                output_text = str(last_item.result)
                                logger.info(f"Found result in last item: {output_text[:100]}")
                        else:
                            logger.info("Last item is mcp_call - need to continue conversation for final answer")
            
            # Check if MCP tools were called - if so, we need to continue the conversation
            if not output_text and hasattr(response, 'output') and response.output:
                # Check for MCP tool calls and track them
                has_mcp_tools = False
                mcp_tool_calls = []
                for item in response.output:
                    if hasattr(item, 'type'):
                        if item.type == 'mcp_list_tools':
                            has_mcp_tools = True
                            logger.info("🔧 MCP tools were listed, need to continue conversation")
                        elif item.type == 'mcp_call':
                            # Track the actual MCP calls
                            tool_info = {
                                "type": "mcp_call",
                                "name": getattr(item, 'name', 'unknown'),
                                "arguments": str(getattr(item, 'arguments', ''))[:200]
                            }
                            mcp_tool_calls.append(tool_info)
                            logger.info(f"📞 MCP tool called: {tool_info['name']}")
                
                if has_mcp_tools:
                    # Continue conversation to get final answer after MCP tool execution
                    logger.info("📞 Continuing conversation after MCP tool calls...")
                    try:
                        # Make a follow-up call with previous_response_id to get the final answer
                        # We need to pass a message to continue the conversation
                        followup_response = client.responses.create(
                            model=model_config.get("model", "gpt-4o-mini"),
                            instructions="Based on the search results, provide the final JSON analysis as requested.",
                            input=[{
                                "type": "message",
                                "role": "user", 
                                "content": f"Continue analyzing the hockey query and provide the JSON analysis: {query}"
                            }],
                            previous_response_id=response_id,
                            max_output_tokens=model_config.get("max_tokens", 4000),
                            temperature=model_config.get("temperature", 0.2)
                        )
                        
                        # Extract text from follow-up response
                        if hasattr(followup_response, 'output_text'):
                            output_text = followup_response.output_text
                            logger.info(f"✅ Got final answer after MCP: {len(output_text) if output_text else 0} chars")
                            # Update response_id for any further continuations
                            if hasattr(followup_response, 'id'):
                                response_id = followup_response.id
                        else:
                            logger.error("Failed to get text even after follow-up")
                    except Exception as e:
                        logger.error(f"Failed to continue after MCP: {e}")
            
            if not output_text:
                logger.error(f"Could not extract text. Response type: {type(response)}")
                logger.error(f"Response has output_text: {hasattr(response, 'output_text')}")
                if hasattr(response, 'output_text'):
                    logger.error(f"output_text value: {response.output_text}")
                if hasattr(response, 'output'):
                    logger.error(f"Output length: {len(response.output) if isinstance(response.output, list) else 'not a list'}")
                    if isinstance(response.output, list) and response.output:
                        for idx, item in enumerate(response.output[:2]):  # Just first 2 items
                            logger.error(f"Item {idx} type: {getattr(item, 'type', type(item).__name__)}")
                # Return empty response with debug info
                return {
                    "error": "Could not extract response text",
                    "debug": {
                        "has_output_text": hasattr(response, 'output_text'),
                        "output_text_value": str(response.output_text)[:100] if hasattr(response, 'output_text') else "N/A",
                        "output_items": len(response.output) if hasattr(response, 'output') and isinstance(response.output, list) else 0,
                        "item_types": [getattr(item, 'type', type(item).__name__) for item in response.output[:4]] if hasattr(response, 'output') and isinstance(response.output, list) else []
                    },
                    "original_query": query
                }
            
            # Initialize MCP calls tracking (may have been populated from continuation logic above)
            if 'mcp_tool_calls' not in locals():
                mcp_tool_calls = []
            
            # Also check in the final response output for any additional tool calls
            if hasattr(response, 'output') and response.output:
                for item in response.output:
                    if hasattr(item, 'type') and item.type == 'mcp_call':
                        # Only add if not already tracked
                        tool_name = getattr(item, 'name', 'unknown')
                        if not any(tc.get('name') == tool_name for tc in mcp_tool_calls):
                            mcp_tool_calls.append({
                                "type": "mcp_call",
                                "name": tool_name,
                                "arguments": str(getattr(item, 'arguments', ''))[:200]
                            })
                            logger.info(f"🔍 Additional tool call detected: {tool_name}")
            
            if mcp_tool_calls:
                logger.info(f"✅ Made {len(mcp_tool_calls)} MCP tool calls")
            else:
                logger.info("ℹ️ No MCP tools were called")
            
            # Parse JSON from the output
            # The output may be markdown with embedded JSON or pure JSON
            import re
            
            # Log the raw output for debugging
            logger.info(f"Raw output length: {len(output_text)}")
            if len(output_text) < 500:
                logger.info(f"Raw output: {output_text}")
            
            # Try to extract JSON from markdown code block first
            json_block_match = re.search(r'```json\s*(.*?)\s*```', output_text, re.DOTALL)
            if json_block_match:
                json_text = json_block_match.group(1).strip()
                logger.info("Found JSON in markdown code block")
            else:
                # Fallback to finding raw JSON
                json_match = re.search(r'\{.*\}', output_text, re.DOTALL)
                json_text = json_match.group() if json_match else None
                if json_text:
                    logger.info("Found raw JSON in output")
            
            if json_text:
                try:
                    result = json.loads(json_text)
                    logger.info("Successfully parsed JSON from output")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON: {e}")
                    result = {
                        "raw_output": output_text[:1000], 
                        "parse_error": f"JSON decode error: {str(e)}",
                        "json_attempt": json_text[:500]
                    }
            else:
                logger.warning("Could not find JSON in response")
                result = {
                    "raw_output": output_text[:1000], 
                    "parse_error": "Could not extract JSON from response"
                }
            
            result["api_used"] = "responses"
            result["exa_available"] = True
            result["mcp_calls"] = mcp_tool_calls
            result["mcp_tools_configured"] = ["web_search_exa"] if use_exa_mcp and exa_api_key else []
            result["api_mode"] = "responses"
            result["response_id"] = response_id  # For multi-turn conversations
            
            # Add conversation tracking
            if is_refinement:
                result["conversation"] = {
                    "turn": "refinement",
                    "previous_response_id": clarifications.get("previous_response_id"),
                    "current_response_id": response_id,
                    "note": "Use current_response_id for next refinement"
                }
            else:
                result["conversation"] = {
                    "turn": "initial",
                    "current_response_id": response_id,
                    "note": "Use this response_id for refinements"
                }
            
        else:
            # Fallback to standard chat completions
            if not use_responses_api:
                if not hasattr(client, 'responses'):
                    logger.info("ℹ️ Responses API not available in SDK, using chat completions")
                elif not exa_api_key:
                    logger.warning("⚠️ EXA_API_KEY not configured, using standard completion")
            
            # Standard chat completion request
            response = client.chat.completions.create(
                model=model_config.get("model", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                response_format=model_config.get("response_format", {"type": "json_object"}),
                temperature=model_config.get("temperature", 0.3),
                max_tokens=model_config.get("max_tokens", 2000)
            )
            
            result = json.loads(response.choices[0].message.content)
            result["api_used"] = "chat_completions"
            result["exa_available"] = False
        
        # Add metadata
        if clarifications:
            result["user_clarifications"] = clarifications
        result["mcp_tools_configured"] = ["web_search_exa"] if use_exa_mcp else []
        result["api_mode"] = "responses" if use_exa_mcp else "standard"
        
        # Log summary
        player_count = len(result.get("components_with_assumptions", {}).get("players", []))
        movement_count = len(result.get("components_with_assumptions", {}).get("movements", []))
        logger.info(f"🔍 Analysis complete: {player_count} players, {movement_count} movements")
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        return {
            "error": "Failed to parse analysis response",
            "original_query": query
        }
    except Exception as e:
        logger.error(f"Query analysis failed: {e}")
        return {
            "error": f"Analysis failed: {str(e)}",
            "original_query": query
        }


# ============================================================================
# TOOL 2: TRANSLATE ANALYSIS TO SPEC
# ============================================================================

@mcp.tool("translate_analysis_to_spec")
def translate_analysis_to_spec(
    analysis: Dict[str, Any],
    title: Optional[str] = None,
    description: Optional[str] = None,
    existing_spec: Optional[Dict[str, Any]] = None,
    clarifications: Optional[Dict[str, Any]] = None,
    previous_response_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Translate analyzed hockey query to complete diagram specification.
    Enhanced to handle both initial translation and clarification updates in a single call.
    
    This unified approach ensures cross-component cohesion and natural ripple effects.
    When updating with clarifications, the LLM can holistically optimize the entire spec.
    
    Args:
        analysis: The full output from analyze_hockey_query tool
        title: Optional title for the diagram (defaults to query)
        description: Optional description for the diagram
        existing_spec: Previous spec to update (for clarification workflows)
        clarifications: User clarifications to apply to existing spec
        previous_response_id: For conversation continuity with OpenAI Responses API
        
    Returns:
        Complete diagram specification with conversation metadata for updates
    """
    # Determine operation mode
    if existing_spec and clarifications:
        logger.info(f"🔄 Updating existing spec with {len(clarifications)} clarifications")
        logger.info(f"📍 Previous Response ID provided: {previous_response_id}")
        if not previous_response_id:
            logger.warning("⚠️  WARNING: No previous_response_id provided for update mode!")
            logger.warning("   This may cause LLM to lose conversation context")
        mode = "update"
    else:
        logger.info("📐 Translating analysis to diagram spec (initial)")
        if previous_response_id:
            logger.warning(f"⚠️  Unexpected previous_response_id in initial mode: {previous_response_id}")
        mode = "initial"
    
    # Initialize variables that may not be set in all code paths
    movement_mapping_result = None
    
    # Extract components from analysis
    components = analysis.get("components_with_assumptions", {})
    rink_info = components.get("rink", {})
    players_info = components.get("players", [])
    movements_info = components.get("movements", [])
    zones_info = components.get("zones", [])
    annotations_info = components.get("annotations", [])
    equipment_info = components.get("equipment", [])
    coaches_info = components.get("coaches", [])
    metadata = analysis.get("metadata", {})
    
    # Initialize spec structure
    spec = {
        "title": title or analysis.get("original_query", "Hockey Drill"),
        "description": description or f"{metadata.get('type', 'drill')} - {metadata.get('phase', 'practice')}",
        "rink": {
            "view": rink_info.get("view", "offensive"),
            "showDots": True,
            "showNets": True,
            "showCreases": True,
            "showCircles": True,
            "showLines": True
        },
        "players": [],
        "movements": []
    }
    
    # Add zones if present
    if zones_info:
        spec["zones"] = zones_info
    
    # Process annotations with smart positioning
    spec["annotations"] = []
    
    # Map position descriptions to actual coordinates and styles
    def map_annotation_position_and_style(position_desc: str):
        """Map semantic position to coordinates and style."""
        position_desc_lower = position_desc.lower() if position_desc else ""
        
        # Position mapping based on rink view
        if spec["rink"]["view"] == "full":
            title_y = -48
            subtitle_y = -43
        else:
            title_y = -40
            subtitle_y = -35
            
        # Map common position descriptions
        # Check subtitle first since it contains "title"
        if "subtitle" in position_desc_lower or "sub-title" in position_desc_lower or "sub title" in position_desc_lower:
            return {
                "position": {"x": 0, "y": subtitle_y},
                "size": "medium",
                "style": "normal"
            }
        elif "title" in position_desc_lower:
            return {
                "position": {"x": 0, "y": title_y},
                "size": "large",
                "style": "bold"
            }
        elif "note" in position_desc_lower:
            return {
                "position": {"x": 30, "y": 35},  # Upper right corner
                "size": "small",
                "style": "normal"
            }
        elif "bottom" in position_desc_lower:
            return {
                "position": {"x": 0, "y": 40},
                "size": "medium",
                "style": "normal"
            }
        elif "top" in position_desc_lower:
            return {
                "position": {"x": 0, "y": title_y + 5},
                "size": "medium",
                "style": "normal"
            }
        else:
            # Default position
            return {
                "position": {"x": 0, "y": 35},
                "size": "medium",
                "style": "normal"
            }
    
    # Auto-generate title if not present
    has_title = False
    title_count = 0  # Track multiple titles
    
    # Process existing annotations
    if annotations_info:
        for ann in annotations_info:
            position_desc = ann.get("position_desc", "")
            text = ann.get("text", "")
            
            # Check if we have a title
            if "title" in position_desc.lower() and "sub" not in position_desc.lower():
                has_title = True
                title_count += 1
            
            # Get position and style based on description
            position_style = map_annotation_position_and_style(position_desc)
            
            # Adjust position if we have multiple items of same type
            if "title" in position_desc.lower() and "sub" not in position_desc.lower() and title_count > 1:
                # Move additional titles down slightly
                position_style["position"]["y"] += (title_count - 1) * 5
            
            # Create annotation with smart positioning
            annotation_spec = {
                "text": text,
                "position": position_style["position"],
                "size": position_style["size"],
                "style": position_style["style"]
            }
            
            # Add confidence metadata if low
            confidence = ann.get("confidence", 1.0)
            if confidence < 0.7:
                annotation_spec["_confidence"] = confidence
                annotation_spec["_assumption"] = ann.get("assumption", "")
            
            spec["annotations"].append(annotation_spec)
    
    # Auto-generate title from query if missing
    if not has_title and title:
        title_position = map_annotation_position_and_style("title")
        spec["annotations"].insert(0, {
            "text": title,
            "position": title_position["position"],
            "size": title_position["size"],
            "style": title_position["style"],
            "_auto_generated": True
        })
    
    # Initialize metadata aggregation
    aggregated_metadata = {
        "confidence_by_category": {},
        "questions_by_category": {},
        "issues_by_category": {},
        "overall_confidence": 1.0,
        "critical_questions": [],
        "questions": [],
        "warnings": []
    }
    
    # Initialize tracking lists
    player_confidences = []
    player_questions = []
    movement_confidences = []
    movement_questions = []
    # Get players from components_with_assumptions (where analyze tool puts them)
    players_info = components.get("players", [])
    
    # Process players - map natural language positions to coordinates using LLM
    player_coords = {}  # Store for movement references
    zone = rink_info.get("view", "offensive")
    mapping_result = {}  # Initialize for later reference
    
    # Use LLM to map all player positions at once
    if players_info:
        # Prepare players for LLM mapping
        players_for_mapping = []
        for player in players_info:
            players_for_mapping.append({
                "id": player.get("id"),
                "position_desc": player.get("position_desc", ""),
                "type": player.get("type", "forward"),
                "team": player.get("team", "home"),
                "confidence": player.get("confidence", 0.5)
            })
        
        # Get mapped positions from LLM - with hybrid cascading support
        if mode == "update" and existing_spec:
            # Update mode with cascading context
            logger.info(f"🔗 Calling map_positions_with_llm in UPDATE mode")
            logger.info(f"   - Clarifications: {list(clarifications.keys()) if clarifications else 'None'}")
            logger.info(f"   - Previous Response ID: {previous_response_id}")
            logger.info(f"   - Has existing spec: {existing_spec is not None}")
            
            # Get conversation history from existing_spec if available
            conversation_history = existing_spec.get("_conversation_history")
            if conversation_history:
                logger.info(f"   - Using stored conversation history with {len(conversation_history)} items")
            
            mapping_result = map_positions_with_llm(
                players_for_mapping, 
                zone,
                clarifications=clarifications,
                previous_response_id=previous_response_id,
                existing_spec_context=existing_spec,
                conversation_history=conversation_history
            )
            
            logger.info(f"✅ Position mapping complete in update mode")
            if mapping_result.get("response_id"):
                logger.info(f"   New response ID from mapping: {mapping_result['response_id']}")
        else:
            # Initial mode
            logger.info(f"🔗 Calling map_positions_with_llm in INITIAL mode")
            mapping_result = map_positions_with_llm(players_for_mapping, zone)
            if mapping_result.get("response_id"):
                logger.info(f"   Response ID from initial mapping: {mapping_result['response_id']}")
        
        # Process mapped players
        if "players_mapped" in mapping_result:
            for mapped_player in mapping_result["players_mapped"]:
                player_id = mapped_player["id"]
                coords = mapped_player["coordinates"]
                
                # Find original player info
                original = next((p for p in players_info if p["id"] == player_id), None)
                if not original:
                    continue
                
                # Generate a valid ID for validation while keeping position as label
                # The ID needs to match regex: ^[FDG][0-9]?$|^COACH$|^P[0-9]+$
                player_type = get_player_type(original.get("type", "forward"))
                
                # Generate unique ID based on type and index
                if player_type == "forward":
                    # Count existing forwards to generate unique ID
                    forward_count = sum(1 for p in spec.get("players", []) if p.get("type") == "forward")
                    valid_id = f"F{forward_count + 1}"
                elif player_type == "defense":
                    # Count existing defense to generate unique ID
                    defense_count = sum(1 for p in spec.get("players", []) if p.get("type") == "defense")
                    valid_id = f"D{defense_count + 1}"
                elif player_type == "goalie":
                    # Count existing goalies
                    goalie_count = sum(1 for p in spec.get("players", []) if p.get("type") == "goalie")
                    valid_id = "G" if goalie_count == 0 else f"G{goalie_count + 1}"
                else:
                    valid_id = f"P{len(spec.get('players', [])) + 1}"
                
                player_spec = {
                    "id": valid_id,  # Use generated valid ID for validation
                    "type": player_type,
                    "position": valid_id,  # Position field also needs to be valid for schema
                    "team": original.get("team", "home"),
                    "coordinates": coords,
                    "label": player_id,  # Keep original position as label (LW, RW, C, LD, RD)
                    "_mapping_confidence": mapped_player.get("confidence", 0.5),
                    "_mapping_reasoning": mapped_player.get("reasoning", "")
                }
                
                spec["players"].append(player_spec)
                player_coords[valid_id] = coords  # Store with valid ID for movement mapping
                player_coords[player_id] = coords  # Also store original position for compatibility
        
        # Add any questions from mapping
        if "questions_for_user" in mapping_result:
            if "mapping_questions" not in spec:
                spec["mapping_questions"] = []
            spec["mapping_questions"].extend(mapping_result["questions_for_user"])
    else:
        # No players to map
        pass
    
    # Process coaches - Add coach entities to players array with coach type
    if coaches_info:
        logger.info(f"👨‍🏫 Processing {len(coaches_info)} coaches...")
        for idx, coach in enumerate(coaches_info):
            # Use simple position mapping for coaches (they're typically at standard locations)
            coach_coords = map_coach_position(
                coach.get("position_desc", ""), 
                rink_info.get("view", "offensive")
            )
            
            # Generate coach ID - schema only supports "COACH" for single coach
            # For multiple coaches, we'll need to use P1, P2 pattern or update schema
            if len(coaches_info) == 1:
                coach_id = "COACH"  # Single coach uses "COACH" 
            else:
                # Multiple coaches: use P pattern since COACH1, COACH2 not supported by schema
                coach_id = f"P{idx + 10}"  # Start at P10 to avoid conflicts with regular players
            
            coach_spec = {
                "id": coach_id,
                "type": "coach",
                "position": coach_id,
                "team": "neutral",  # Coaches are neutral
                "coordinates": coach_coords,
                "label": "C",  # Standard coach label
                "_role": coach.get("role", "observer"),
                "_confidence": coach.get("confidence", 0.9)
            }
            
            spec["players"].append(coach_spec)
            logger.info(f"   Added coach at {coach_coords} (role: {coach.get('role', 'observer')})")
    
    # Process movements - Use LLM for intelligent mapping with spatial awareness
    if movements_info:
        logger.info(f"🏃 Processing {len(movements_info)} movements with LLM mapping...")
        
        # Prepare movements for LLM mapping
        movements_for_mapping = []
        for idx, movement in enumerate(movements_info):
            movement_data = {
                "id": f"movement_{idx}",
                "type": movement.get("type", "skate"),
                "player_id": movement.get("from_player"),
                "description": movement.get("to_area", ""),
                "original": movement
            }
            
            # Add target player for passes
            if movement.get("type") == "pass":
                if movement.get("to_player"):
                    movement_data["target_player_id"] = movement["to_player"]
                else:
                    # Try to infer target from description
                    to_area = movement.get("to_area", "").lower()
                    
                    # Common patterns to player mappings
                    if "left winger" in to_area or "left wing" in to_area or "lw" in to_area:
                        movement_data["target_player_id"] = "LW"
                    elif "right winger" in to_area or "right wing" in to_area or "rw" in to_area:
                        movement_data["target_player_id"] = "RW"
                    elif "center" in to_area and "center ice" not in to_area:
                        movement_data["target_player_id"] = "C"
                    elif "left defense" in to_area or "left d" in to_area or "ld" in to_area:
                        movement_data["target_player_id"] = "LD"
                    elif "right defense" in to_area or "right d" in to_area or "rd" in to_area:
                        movement_data["target_player_id"] = "RD"
                    elif "goalie" in to_area:
                        movement_data["target_player_id"] = "G"
                    
                    # If we found a target, log it
                    if "target_player_id" in movement_data:
                        logger.info(f"  Inferred target player {movement_data['target_player_id']} from '{to_area}'")
            
            movements_for_mapping.append(movement_data)
        
        # Map movements using LLM with spatial awareness - with hybrid cascading support
        if mode == "update" and existing_spec:
            # Update mode with cascading context (chained response ID from player mapping)
            player_response_id = mapping_result.get("response_id")
            # Get conversation history from player mapping result
            player_conversation_history = mapping_result.get("conversation_history")
            movement_mapping_result = map_movements_with_llm(
                movements_for_mapping,
                spec["players"],  # Pass updated players for position context
                spec["rink"]["view"],
                clarifications=clarifications,
                previous_response_id=player_response_id,  # Chain from player mapping
                existing_spec_context=existing_spec,
                conversation_history=player_conversation_history  # Pass conversation history
            )
        else:
            # Initial mode
            movement_mapping_result = map_movements_with_llm(
                movements_for_mapping,
                spec["players"],  # Pass mapped players for position context
                spec["rink"]["view"]
            )
        
        # Process mapped movements
        if movement_mapping_result and "movements_mapped" in movement_mapping_result:
            for mapped_movement in movement_mapping_result["movements_mapped"]:
                movement_id = mapped_movement["id"]
                idx = int(movement_id.split("_")[1]) if "_" in movement_id else 0
                
                # Build movement spec - use v2 compatible format
                # Get player's starting position from spec
                player_id = mapped_movement.get("player_id")
                from_pos = {"x": 0, "y": 0}  # Default
                
                # Find player position in spec
                for player in spec["players"]:
                    if player.get("id") == player_id:
                        coords = player.get("coordinates", {})
                        from_pos = {"x": coords.get("x", 0), "y": coords.get("y", 0)}
                        break
                
                # If we have start position from mapping, use that instead
                if mapped_movement.get("start"):
                    from_pos = {
                        "x": mapped_movement["start"].get("x", 0),
                        "y": mapped_movement["start"].get("y", 0)
                    }
                
                # Determine style based on movement type
                movement_type = mapped_movement.get("type", "skate")
                if movement_type == "pass":
                    style = "dotted"
                elif movement_type == "shot":
                    style = "dashed"
                else:  # skate, carry
                    style = "solid"
                
                movement_spec = {
                    "type": movement_type,
                    "from_pos": from_pos,  # V2 uses from_pos, not from
                    "to_pos": {  # V2 uses to_pos, not to
                        "x": mapped_movement.get("end", {}).get("x", 0),
                        "y": mapped_movement.get("end", {}).get("y", 0)
                    },
                    "style": style,  # V2 requires style property
                    "label": str(idx + 1)
                }
                
                # Add waypoints if present - convert to object format for v2
                if mapped_movement.get("waypoints"):
                    waypoints = [
                        {"x": wp["x"], "y": wp["y"]} 
                        for wp in mapped_movement["waypoints"]
                    ]
                    if waypoints:
                        movement_spec["waypoints"] = waypoints
                
                spec["movements"].append(movement_spec)
                
                # Store movement confidence in metadata
                confidence = mapped_movement.get("confidence", 0.5)
                movement_confidences.append(confidence)
                
                # Store any questions about this movement
                if confidence < 0.7 and mapped_movement.get("reasoning"):
                    movement_questions.append({
                        "movement": f"Movement {idx + 1}",
                        "description": mapped_movement.get("original_description", ""),
                        "confidence": confidence,
                        "reasoning": mapped_movement["reasoning"],
                        "alternatives": mapped_movement.get("alternatives", [])
                    })
        
        # Store movement metadata
        aggregated_metadata["confidence_by_category"]["movements"] = {
            "average": sum(movement_confidences) / len(movement_confidences) if movement_confidences else 0.6,
            "min": min(movement_confidences) if movement_confidences else 0.6,
            "count": len(movement_confidences)
        }
        
        aggregated_metadata["questions_by_category"]["movements"] = movement_questions
        
        # Check for path validation issues
        if movement_mapping_result and "path_validation" in movement_mapping_result:
            path_val = movement_mapping_result["path_validation"]
            if path_val.get("through_net_issues"):
                aggregated_metadata["warnings"].append({
                    "category": "movements",
                    "issue": "Movement paths going through net",
                    "movements": path_val["through_net_issues"]
                })
            if path_val.get("out_of_bounds"):
                aggregated_metadata["warnings"].append({
                    "category": "movements",
                    "issue": "Movement paths going out of bounds", 
                    "movements": path_val["out_of_bounds"]
                })
        
        # Add any movement-specific questions for user
        if movement_mapping_result and "questions_for_user" in movement_mapping_result:
            for question in movement_mapping_result["questions_for_user"]:
                if question.get("impact", "").lower().find("critical") >= 0:
                    aggregated_metadata["critical_questions"].append(question)
                else:
                    aggregated_metadata["questions"].append(question)
    else:
        # No movements to process
        spec["movements"] = []
    
    # Final aggregation of player mapping metadata (if not already done)
    if players_info and "players_mapped" in mapping_result and "players" not in aggregated_metadata["confidence_by_category"]:
        player_confidences = []
        player_questions = []
        
        for mapped_player in mapping_result.get("players_mapped", []):
            confidence = mapped_player.get("confidence", 0.5)
            player_confidences.append(confidence)
            
            # Track low confidence items
            if confidence < 0.7:
                aggregated_metadata["warnings"].append({
                    "category": "players",
                    "id": mapped_player["id"],
                    "issue": f"Low confidence ({confidence:.1f}) for {mapped_player.get('original_position', 'position')}",
                    "reasoning": mapped_player.get("reasoning", "")
                })
        
        # Add questions from player mapping
        for question in mapping_result.get("questions_for_user", []):
            player_questions.append(question)
            if question.get("critical", False):
                aggregated_metadata["critical_questions"].append({
                    "category": "players",
                    **question
                })
        
        aggregated_metadata["confidence_by_category"]["players"] = {
            "average": sum(player_confidences) / len(player_confidences) if player_confidences else 1.0,
            "min": min(player_confidences) if player_confidences else 1.0,
            "count": len(player_confidences)
        }
        
        aggregated_metadata["questions_by_category"]["players"] = player_questions
    
    # Check for spatial issues
    if "spatial_checks" in mapping_result:
        spatial = mapping_result["spatial_checks"]
        if spatial.get("overlaps_detected"):
            aggregated_metadata["warnings"].append({
                "category": "spatial",
                "issue": "Player positions overlap",
                "details": spatial.get("spacing_issues", [])
            })
        if spatial.get("out_of_bounds"):
            aggregated_metadata["warnings"].append({
                "category": "spatial", 
                "issue": "Players positioned out of bounds",
                "players": spatial["out_of_bounds"]
            })
    
    # Set default movement confidence if not already set by LLM mapping
    if "movements" not in aggregated_metadata["confidence_by_category"]:
        movement_confidence = 0.6  # Default medium confidence
        aggregated_metadata["confidence_by_category"]["movements"] = {
            "average": movement_confidence,
            "min": movement_confidence,
            "count": len(spec.get("movements", []))
        }
    
    # Process equipment if present
    if equipment_info:
        logger.info(f"🔧 Processing {len(equipment_info)} equipment items")
        
        # Known simple positions that map_hockey_position handles well
        simple_positions = [
            "faceoff dot", "circle", "slot", "high slot", "point",
            "net front", "behind net", "corner", "half wall", "center ice"
        ]
        
        # Check if ALL equipment uses simple positions
        use_simple_mapping = True
        for eq in equipment_info:
            position_desc = eq.get("position_desc", "").lower()
            
            # If no position description, use LLM
            if not position_desc:
                use_simple_mapping = False
                break
                
            # Check if this is a simple known position
            is_simple = any(pos in position_desc for pos in simple_positions)
            # But if it has modifiers like "near", "between", etc., use LLM
            has_modifier = any(term in position_desc for term in [
                "between", "halfway", "feet from", "meters from", 
                "diagonal", "near", "around", "triangle", "zigzag", 
                "arc", "circle", "beside", "away from", "across from"
            ])
            
            # Also check for "blue line" or "goal line" without modifiers
            is_line = ("blue line" in position_desc or "goal line" in position_desc) and not has_modifier
            
            if has_modifier or not (is_simple or is_line):
                use_simple_mapping = False
                break
        
        if not use_simple_mapping:
            # Use LLM mapping for complex positions
            logger.info("🤖 Using LLM for complex equipment positioning")
            
            # Get the final layout context from previous mappings
            final_layout_context = {
                "players": spec.get("players", []),
                "movements": spec.get("movements", [])
            }
            
            if mode == "update" and existing_spec:
                # Update mode with cascading context (chained response ID from movement mapping)
                movement_response_id = movement_mapping_result.get("response_id") if movement_mapping_result else None
                mapping_result = map_equipment_with_llm(
                    equipment_info, 
                    spec["rink"]["view"],
                    clarifications=clarifications,
                    previous_response_id=movement_response_id,  # Chain from movement mapping
                    existing_spec_context=existing_spec
                )
            else:
                # Initial mode
                mapping_result = map_equipment_with_llm(equipment_info, spec["rink"]["view"])
            
            if "equipment_mapped" in mapping_result:
                spec["equipment"] = []
                for mapped_eq in mapping_result["equipment_mapped"]:
                    # Check if we have spread items (multiple positions)
                    if "spread_items" in mapped_eq and mapped_eq["spread_items"]:
                        # Create individual equipment for each spread position
                        for i, coords in enumerate(mapped_eq["spread_items"]):
                            equipment_spec = {
                                "id": f"{mapped_eq['id']}_{i}",
                                "type": equipment_info[0].get("type", "cone"),  # Get type from original
                                "coordinates": coords,
                                "count": 1,
                                "color": equipment_info[0].get("color", "orange"),
                                "size": "medium",
                                "label": equipment_info[0].get("purpose", "") if i == 0 else ""
                            }
                            spec["equipment"].append(equipment_spec)
                    else:
                        # Single equipment item
                        equipment_spec = {
                            "id": mapped_eq["id"],
                            "type": equipment_info[0].get("type", "cone"),
                            "coordinates": mapped_eq["coordinates"],
                            "count": equipment_info[0].get("count", 1),
                            "color": equipment_info[0].get("color", "orange"),
                            "size": "medium",
                            "label": equipment_info[0].get("purpose", "")
                        }
                        spec["equipment"].append(equipment_spec)
                
                # Add mapping confidence to metadata
                for mapped_eq in mapping_result["equipment_mapped"]:
                    if mapped_eq.get("confidence", 0) < 0.7:
                        aggregated_metadata["warnings"].append({
                            "category": "equipment",
                            "issue": f"Low confidence equipment placement: {mapped_eq.get('reasoning', 'Unknown position')}"
                        })
            else:
                logger.warning("LLM equipment mapping failed, falling back to simple mapping")
                use_simple_mapping = True
        
        if use_simple_mapping:
            # Use simple mapping for standard positions
            spec["equipment"] = []
            for eq in equipment_info:
                position_desc = eq.get("position_desc", "")
                
                # Use the existing map_hockey_position function
                if position_desc:
                    # First try direct position mapping
                    eq_coords = map_hockey_position(position_desc, spec["rink"]["view"])
                    
                    # If no direct match, try to extract key position terms
                    if eq_coords["x"] == 0 and eq_coords["y"] == 0 and position_desc != "center ice":
                        # Additional equipment-specific position handling
                        if "blue line" in position_desc.lower():
                            if spec["rink"]["view"] == "offensive":
                                eq_coords = {"x": 25, "y": 0}  # Offensive blue line
                            else:
                                eq_coords = {"x": -25, "y": 0}  # Defensive blue line
                        elif "goal line" in position_desc.lower():
                            eq_coords = {"x": 89, "y": 0} if spec["rink"]["view"] == "offensive" else {"x": -89, "y": 0}
                        elif "neutral zone" in position_desc.lower():
                            eq_coords = {"x": 0, "y": 0}
                else:
                    eq_coords = {"x": 0, "y": 0}  # Default to center
                
                # Handle multiple equipment items
                count = eq.get("count", 1)
                if count > 1 and "along" in position_desc.lower():
                    # Spread equipment items along a line
                    for i in range(int(count)):
                        offset = (i - count/2 + 0.5) * 10  # Spread by 10 units
                        item_coords = {
                            "x": eq_coords["x"],
                            "y": eq_coords["y"] + offset
                        }
                        
                        equipment_spec = {
                            "id": f"{eq.get('id', 'eq')}_{i}",
                            "type": eq.get("type", "cone"),
                            "coordinates": item_coords,
                            "count": 1,
                            "color": eq.get("color", "orange"),
                            "size": "medium",
                            "label": eq.get("purpose", "") if i == 0 else ""
                        }
                        spec["equipment"].append(equipment_spec)
                else:
                    # Single item or grouped items at one location
                    equipment_spec = {
                        "id": eq.get("id", f"equipment_{len(spec['equipment'])}"),
                        "type": eq.get("type", "cone"),
                        "coordinates": eq_coords,
                        "count": count,
                        "color": eq.get("color", "orange"),
                        "size": "medium",
                        "label": eq.get("purpose", "")
                    }
                    spec["equipment"].append(equipment_spec)
    
    # Calculate overall confidence
    category_confidences = [
        cat["average"] for cat in aggregated_metadata["confidence_by_category"].values()
    ]
    if category_confidences:
        aggregated_metadata["overall_confidence"] = sum(category_confidences) / len(category_confidences)
    
    # Generate validation summary
    validation_summary = []
    if aggregated_metadata["overall_confidence"] >= 0.8:
        validation_summary.append("✅ High confidence mapping - ready for validation")
    elif aggregated_metadata["overall_confidence"] >= 0.6:
        validation_summary.append("⚠️ Medium confidence - review warnings before proceeding")
    else:
        validation_summary.append("❌ Low confidence - address critical questions first")
    
    if aggregated_metadata["critical_questions"]:
        validation_summary.append(f"🔴 {len(aggregated_metadata['critical_questions'])} critical questions need answers")
    
    if aggregated_metadata["warnings"]:
        validation_summary.append(f"⚠️ {len(aggregated_metadata['warnings'])} warnings to review")
    
    # Collect response IDs from mapping calls for conversation continuity
    conversation_metadata = {
        "response_ids": {},
        "original_analysis": analysis,  # Store for reconstruction in updates
        "mapping_results": {}  # Store intermediate results if needed
    }
    
    # Collect response IDs from all mapping stages that were executed
    response_ids = {}
    
    # Player mapping response ID
    if 'mapping_result' in locals() and isinstance(mapping_result, dict):
        if "response_id" in mapping_result:
            response_ids["player_mapping"] = mapping_result["response_id"]
    
    # Movement mapping response ID  
    if movement_mapping_result and isinstance(movement_mapping_result, dict):
        if "response_id" in movement_mapping_result:
            response_ids["movement_mapping"] = movement_mapping_result["response_id"]
    
    # Equipment mapping response ID (note: uses chat completions, so response_id will be None)
    # We scan the local variables for equipment mapping results from the equipment processing section
    for var_name in locals():
        if 'equipment' in var_name and 'mapping' in var_name and isinstance(locals()[var_name], dict):
            result_dict = locals()[var_name]
            if "response_id" in result_dict:
                response_ids["equipment_mapping"] = result_dict["response_id"]
                break
    
    conversation_metadata["response_ids"] = response_ids
    
    # Determine the final response ID for chaining (last mapping call made)
    final_response_id = None
    
    # Get response ID from the last mapping operation (for both initial and update modes)
    if movement_mapping_result and movement_mapping_result.get("response_id"):
        final_response_id = movement_mapping_result["response_id"]
    elif 'mapping_result' in locals() and mapping_result and mapping_result.get("response_id"):
        final_response_id = mapping_result["response_id"]
    
    # Log response ID for debugging
    if final_response_id:
        logger.info(f"📍 Final response ID for chaining: {final_response_id}")
    else:
        logger.warning("⚠️  No response ID available for conversation continuity")
    
    # Store conversation history in spec for future updates
    if 'mapping_result' in locals() and mapping_result and mapping_result.get("conversation_history"):
        spec["_conversation_history"] = mapping_result["conversation_history"]
        logger.info(f"📚 Stored conversation history with {len(mapping_result['conversation_history'])} items in spec")
    
    return {
        "success": True,
        "spec": spec,
        "translation_summary": {
            "players_mapped": len(spec["players"]),
            "movements_mapped": len(spec["movements"]),
            "equipment_placed": len(spec.get("equipment", [])),
            "rink_view": spec["rink"]["view"],
            "has_zones": len(spec.get("zones", [])) > 0,
            "has_annotations": len(spec.get("annotations", [])) > 0
        },
        "metadata": aggregated_metadata,
        "validation_summary": validation_summary,
        "conversation": conversation_metadata,  # NEW: For clarification updates
        "response_id": final_response_id,  # NEW: For hybrid approach chaining
        "notes": [
            "Spec generated from analysis - ready for validation",
            "Review metadata for confidence scores and questions", 
            "Use validate_diagram_spec_full to check for issues",
            "Use generate_diagram to create the visual",
            "Use conversation.response_ids for clarification updates"
        ]
    }


def validate_player_positions(positions: List[Dict], situation: str = "") -> Dict[str, Any]:
    """
    Validate player positions for spatial issues and hockey sense.
    
    Args:
        positions: List of player positions with x, y coordinates
        situation: Hockey situation context
        
    Returns:
        Validation results with issues and suggestions
    """
    issues = []
    warnings = []
    suggestions = []
    
    # Check for overlapping players
    for i, p1 in enumerate(positions):
        for j, p2 in enumerate(positions[i+1:], i+1):
            dist = ((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)**0.5
            if dist < 2.0:
                issues.append(f"Players {p1.get('id', i)} and {p2.get('id', j)} too close ({dist:.1f} units apart)")
                if p1.get('team') != p2.get('team'):
                    suggestions.append(f"Opposing players need at least 3 units spacing")
    
    # Check for out of bounds
    for p in positions:
        if abs(p['x']) > 100:
            issues.append(f"Player {p.get('id')} x-coordinate out of bounds: {p['x']}")
        if abs(p['y']) > 42.5:
            issues.append(f"Player {p.get('id')} y-coordinate out of bounds: {p['y']}")
    
    # Situation-specific checks
    if "center ice" in situation.lower() and "faceoff" in situation.lower():
        # Check that players are around center ice
        for p in positions:
            if abs(p['x']) > 25:
                warnings.append(f"Player {p.get('id')} at x={p['x']} seems far from center ice (should be |x| < 25)")
                suggestions.append(f"For center ice faceoffs, all players should be within x=[-25, 25]")
        
        # Check centers are at faceoff position
        centers = [p for p in positions if 'center' in p.get('description', '').lower() or p.get('id', '').startswith('C')]
        if centers:
            for c in centers:
                if abs(c['x']) > 2 and abs(c['y']) > 2:
                    warnings.append(f"Center {c.get('id')} at ({c['x']}, {c['y']}) not at faceoff dot")
    
    # Return validation results
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings, 
        "suggestions": list(set(suggestions)),  # Remove duplicates
        "summary": "All positions valid" if not issues else f"{len(issues)} positioning issues found"
    }

def build_clarification_text(clarifications: Dict[str, Any]) -> str:
    """Build formatted clarification text for LLM prompts."""
    if not clarifications:
        return ""
    
    clarification_lines = []
    for key, value in clarifications.items():
        if isinstance(value, dict) and 'answer' in value:
            clarification_lines.append(f"- {key}: {value['answer']}")
        else:
            clarification_lines.append(f"- {key}: {value}")
    
    return "\n".join(clarification_lines)

def map_positions_with_llm(
    players: List[Dict[str, Any]], 
    rink_view: str = "offensive",
    clarifications: Optional[Dict[str, Any]] = None,
    previous_response_id: Optional[str] = None,
    existing_spec_context: Optional[Dict[str, Any]] = None,
    conversation_history: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Map multiple player positions using LLM with spatial awareness.
    Uses OpenAI Responses API for native function calling.
    Enhanced for conversational updates with clarifications.
    
    Args:
        players: List of player dictionaries with position descriptions
        rink_view: The rink view context
        clarifications: Optional clarifications from user to update positions
        previous_response_id: Previous response ID for conversation continuity
        existing_spec_context: Existing spec for context in update mode
        conversation_history: Previous conversation history including function outputs
    
    Returns:
        Mapped positions with coordinates and confidence
    """
    # Load position mapping prompt
    prompt_config_path = Path(__file__).parent.parent / "config" / "prompts" / "map_positions.json"
    try:
        with open(prompt_config_path, 'r') as f:
            position_prompt_config = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load position mapping prompt: {e}")
        return {"error": "Failed to load position mapping configuration"}
    
    # Import zone boundaries functions
    sys.path.append(str(Path(__file__).parent.parent / "src"))
    from zone_boundaries import get_zone_boundaries, list_available_zones
    
    # Build the main prompt
    prompt = position_prompt_config["main_prompt_template"].format(
        rink_view=rink_view,
        zone_context=f"Focusing on {rink_view} zone view",
        players_json=json.dumps(players, indent=2),
        instructions=position_prompt_config["instructions"],
        rink_reference=position_prompt_config["rink_reference"],
        zone_positions=position_prompt_config["zone_positions"],
        output_format=position_prompt_config["output_format"]
    )
    
    # Add clarifications if provided
    if clarifications:
        clarification_text = build_clarification_text(clarifications)
        prompt += f"\n\nUser Clarifications:\n{clarification_text}"
        prompt += "\n\nUpdate the player positions based on these clarifications. "
        prompt += "Focus only on changes needed due to clarifications."
    
    # Add existing spec context for updates (hybrid approach)
    if existing_spec_context:
        prompt += "\n\nSPEC UPDATE MODE - PLAYER MAPPING\n\n"
        prompt += "EXISTING SPEC CONTEXT:\n"
        prompt += json.dumps(existing_spec_context, indent=2)
        prompt += "\n\nINSTRUCTIONS:\n"
        prompt += "1. START with the existing players as your foundation\n"
        prompt += "2. Apply clarifications while maintaining overall cohesion\n"
        prompt += "3. Keep unchanged player elements stable unless clarifications require changes\n"
        prompt += "4. Ensure your updates work with the overall spec context\n"
        prompt += "5. Be conservative - only change what the clarifications specifically request\n"
    
    # Add tool instructions
    prompt += "\n\n" + position_prompt_config["tool_instructions"]
    
    # Define the zone tools
    tools = [
        {
            "type": "function",
            "name": "validate_player_positions",
            "description": "REQUIRED: Validate your proposed player positions before finalizing. Returns warnings about overlaps, out of bounds, or incorrect positioning.",
            "parameters": {
                "type": "object",
                "properties": {
                    "positions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "x": {"type": "number"},
                                "y": {"type": "number"},
                                "team": {"type": "string"},
                                "description": {"type": "string"}
                            },
                            "required": ["id", "x", "y"]
                        },
                        "description": "Array of player positions to validate"
                    },
                    "situation": {
                        "type": "string",
                        "description": "The hockey situation (e.g., 'center ice faceoff', 'offensive zone faceoff')"
                    }
                },
                "required": ["positions"]
            }
        },
        {
            "type": "function",
            "name": "list_available_zones",
            "description": "List all available zones that can be queried for boundaries",
            "parameters": {
                "type": "object",
                "properties": {
                    "view": {
                        "type": "string",
                        "enum": ["offensive", "defensive", "neutral", "full", "all"],
                        "description": "Optional view filter to list zones for specific view only. Use 'all' or omit to see all zones."
                    }
                },
                "required": []
            }
        },
        {
            "type": "function",
            "name": "get_zone_boundaries",
            "description": "Get boundary coordinates for a specific zone/area on the rink",
            "parameters": {
                "type": "object",
                "properties": {
                    "view": {
                        "type": "string",
                        "enum": ["offensive", "defensive", "neutral", "full"],
                        "description": "Rink view context"
                    },
                    "zone": {
                        "type": "string", 
                        "description": "Specific area name (e.g., 'slot', 'left_circle', 'right_point')"
                    }
                },
                "required": ["view", "zone"]
            }
        }
    ]
    
    model_config = position_prompt_config.get("model_config", {})
    
    try:
        # Create input list for Responses API
        if conversation_history and previous_response_id:
            # Continue from previous conversation with function outputs
            # Clean the conversation history to remove duplicate IDs
            seen_ids = set()
            cleaned_history = []
            for item in conversation_history:
                # Check for function calls - they're objects with .type attribute
                if hasattr(item, 'type') and item.type == "function_call":
                    # Function call objects have a call_id attribute
                    if hasattr(item, 'call_id') and item.call_id:
                        if item.call_id in seen_ids:
                            logger.warning(f"Skipping duplicate function call ID: {item.call_id}")
                            continue
                        seen_ids.add(item.call_id)
                # Check for function call outputs (dicts)
                elif isinstance(item, dict) and item.get("type") == "function_call_output":
                    # Function call outputs have call_id field
                    call_id = item.get("call_id")
                    if call_id and call_id in seen_ids:
                        logger.warning(f"Skipping duplicate function output ID: {call_id}")
                        continue
                    if call_id:
                        seen_ids.add(call_id)
                cleaned_history.append(item)
            
            input_list = cleaned_history + [
                {"role": "user", "content": prompt}
            ]
            logger.info(f"📚 Using conversation history with {len(cleaned_history)} items (cleaned from {len(conversation_history)})")
        else:
            # Start fresh conversation
            input_list = [
                {"role": "system", "content": position_prompt_config["system_prompt"]},
                {"role": "user", "content": prompt}
            ]
        
        # Build API request parameters
        api_request = {
            "model": model_config.get("model", "gpt-4o-mini"),
            "instructions": position_prompt_config["system_prompt"],
            "tools": tools,
            "tool_choice": "auto",  # Let model decide if tools are needed
            "input": input_list,
            "max_output_tokens": model_config.get("max_tokens", 2000),
            "temperature": model_config.get("temperature", 0.2)
        }
        
        # Include previous_response_id for conversation continuity if provided
        if previous_response_id:
            api_request["previous_response_id"] = previous_response_id
            logger.info(f"🔄 Continuing conversation from response: {previous_response_id}")
            logger.info("   ✅ Response ID added to API request for conversation continuity")
        else:
            logger.info("   ℹ️  No previous_response_id - starting fresh conversation")
        
        # DEBUG: Log full API request
        logger.info("🔍 DEBUG: Full API request:")
        logger.info(f"  Model: {api_request['model']}")
        logger.info(f"  Temperature: {api_request['temperature']}")
        logger.info(f"  Max tokens: {api_request['max_output_tokens']}")
        logger.info(f"  Tools available: {len(api_request['tools'])}")
        logger.info(f"  Has previous_response_id: {'previous_response_id' in api_request}")
        if 'previous_response_id' in api_request:
            logger.info(f"  📍 Previous Response ID in request: {api_request['previous_response_id']}")
        logger.info(f"  System prompt length: {len(api_request['instructions'])}")
        logger.info(f"  User prompt length: {len(prompt)}")
        logger.info(f"  User prompt preview: {prompt[:500]}...")
        
        # Log the player descriptions being mapped
        logger.info("📝 PLAYERS TO MAP:")
        for p in players[:10]:  # Log up to 10 players
            logger.info(f"  - {p.get('id')}: {p.get('position_desc')} (team: {p.get('team')})")
        if clarifications:
            logger.info(f"  Clarifications received: {clarifications}")
        
        # Use Responses API with native function calling
        response = client.responses.create(**api_request)
        
        # Capture response ID for conversation continuity
        response_id = response.id if hasattr(response, 'id') else None
        
        # Check if there were function calls
        function_calls_made = False
        result_text = None
        
        # DEBUG: Log initial response details
        logger.info(f"🔍 DEBUG: Initial response details:")
        logger.info(f"  Response ID: {response_id}")
        logger.info(f"  Output items count: {len(response.output)}")
        if hasattr(response, 'reasoning') and response.reasoning:
            logger.info(f"  🧠 REASONING Round 1 available")
            
            # Extract detailed reasoning components
            if hasattr(response.reasoning, 'summary') and response.reasoning.summary:
                logger.info(f"  🧠 REASONING Summary: {response.reasoning.summary}")
            
            if hasattr(response.reasoning, 'effort') and response.reasoning.effort:
                logger.info(f"  🧠 REASONING Effort: {response.reasoning.effort}")
                
            if hasattr(response.reasoning, 'generate_summary') and response.reasoning.generate_summary:
                logger.info(f"  🧠 REASONING Generate Summary: {response.reasoning.generate_summary}")
                
            # Log the full reasoning object structure for debugging
            logger.info(f"  🧠 REASONING Full Object: {response.reasoning}")
        else:
            logger.info("  No reasoning available in Round 1")
        
        # Check the output
        for i, item in enumerate(response.output):
            logger.info(f"  Output item {i}: type={item.type}")
            if item.type == "function_call":
                function_calls_made = True
                logger.info(f"    Function: {item.name}")
                logger.info(f"    Arguments: {item.arguments}")
                # We need to execute the function and make another call
            elif item.type == "text":
                logger.info(f"    Text content length: {len(item.text) if item.text else 0}")
                logger.info(f"    Text preview: {item.text[:200] if item.text else 'None'}...")
        
        if function_calls_made:
            logger.info(f"🔧 Found {sum(1 for item in response.output if item.type == 'function_call')} function calls to execute")
        
        if not function_calls_made:
            # No function calls, should have the answer directly
            result_text = response.output_text
            logger.info(f"Got direct response: {result_text[:100] if result_text else 'None'}")
        else:
            # Has function calls - need to execute them and call again
            logger.info("Response contains function calls, executing them...")
            
            # Add the response output to input list, checking for duplicates
            # Track IDs we've already seen
            existing_ids = set()
            for hist_item in input_list:
                if hasattr(hist_item, 'call_id'):
                    existing_ids.add(hist_item.call_id)
                elif isinstance(hist_item, dict) and hist_item.get('call_id'):
                    existing_ids.add(hist_item['call_id'])
            
            # Add new response items, skipping duplicates
            for item in response.output:
                if hasattr(item, 'call_id') and item.call_id in existing_ids:
                    logger.warning(f"Skipping duplicate position response item with call_id: {item.call_id}")
                    continue
                input_list.append(item)
            
            # Execute each function call
            for item in response.output:
                if item.type == "function_call":
                    if item.name == "list_available_zones":
                        args = json.loads(item.arguments) if item.arguments else {}
                        view_filter = args.get("view", None)
                        zones_list = list_available_zones(view_filter)
                        
                        input_list.append({
                            "type": "function_call_output",
                            "call_id": item.call_id,
                            "output": json.dumps(zones_list)
                        })
                        logger.info(f"📋 Executed list_available_zones({view_filter})")
                        logger.info(f"    Result: {zones_list}")
                        
                    elif item.name == "get_zone_boundaries":
                        args = json.loads(item.arguments)
                        boundaries = get_zone_boundaries(args["view"], args["zone"])
                        
                        input_list.append({
                            "type": "function_call_output",
                            "call_id": item.call_id,
                            "output": json.dumps(boundaries)
                        })
                        logger.info(f"🔧 Executed get_zone_boundaries({args['view']}, {args['zone']})")
                        logger.info(f"    Result: {boundaries}")
                        
                    elif item.name == "validate_player_positions":
                        args = json.loads(item.arguments) if item.arguments else {}
                        validation = validate_player_positions(args.get("positions", []), args.get("situation", ""))
                        input_list.append({
                            "type": "function_call_output",
                            "call_id": item.call_id,
                            "output": json.dumps(validation)
                        })
                        logger.info(f"✅ Executed validate_player_positions in round 1")
                        logger.info(f"    Validation: {validation['summary']}")
                        if validation['issues']:
                            logger.warning(f"    Issues: {validation['issues']}")
                        if validation['warnings']:
                            logger.info(f"    Warnings: {validation['warnings']}")
            
            # Keep making calls until we get text output (not more function calls)
            max_rounds = 5  # Prevent infinite loops
            round_num = 2
            
            while round_num <= max_rounds:
                logger.info(f"🔄 Making call {round_num} with function results...")
                logger.info(f"🔍 DEBUG Round {round_num}: Current input list has {len(input_list)} items")
                
                # Adjust instructions based on round number
                if round_num == 2:
                    follow_up_instructions = "You now have the zone information. Map each player to exact coordinates and return ONLY valid JSON."
                elif round_num >= 3:
                    follow_up_instructions = f"This is round {round_num}. You should have enough information now. Please provide the final JSON mapping immediately without requesting more zone boundaries."
                else:
                    follow_up_instructions = "Use the zone boundary information to map each player to exact coordinates. Return ONLY valid JSON."
                
                logger.info(f"🔍 DEBUG Round {round_num}: Instructions: {follow_up_instructions}")
                
                final_response = client.responses.create(
                    model=model_config.get("model", "gpt-4o-mini"),
                    instructions=follow_up_instructions,
                    tools=tools,
                    tool_choice="auto" if round_num < 4 else "none",  # Disable tools after round 3
                    input=input_list,
                    max_output_tokens=model_config.get("max_tokens", 2000),
                    temperature=model_config.get("temperature", 0.2)
                )
                
                # Update response ID from the latest call
                if hasattr(final_response, 'id'):
                    response_id = final_response.id
                
                # Check if we got text or more function calls
                has_function_calls = False
                result_text = final_response.output_text
                
                # DEBUG: Log round response details
                logger.info(f"🔍 DEBUG Round {round_num} response:")
                logger.info(f"  Response ID: {final_response.id if hasattr(final_response, 'id') else 'None'}")
                logger.info(f"  Output text length: {len(result_text) if result_text else 0}")
                logger.info(f"  Has output items: {hasattr(final_response, 'output')}")
                if hasattr(final_response, 'output'):
                    logger.info(f"  Output items count: {len(final_response.output)}")
                
                if not result_text and hasattr(final_response, 'output'):
                    # Log any reasoning from the model
                    if hasattr(final_response, 'reasoning') and final_response.reasoning:
                        logger.info(f"  🧠 Round {round_num} reasoning available")
                        if hasattr(final_response.reasoning, 'summary') and final_response.reasoning.summary:
                            logger.info(f"  🧠 Round {round_num} reasoning summary: {final_response.reasoning.summary}")
                        logger.info(f"  🧠 Round {round_num} full reasoning: {final_response.reasoning}")
                    else:
                        logger.info(f"  No reasoning available in Round {round_num}")
                    
                    function_call_count = 0
                    text_count = 0
                    for i, item in enumerate(final_response.output):
                        logger.info(f"  Round {round_num} item {i}: type={item.type}")
                        if item.type == "function_call":
                            function_call_count += 1
                            logger.info(f"    Function: {item.name}({item.arguments})")
                        elif item.type == "text":
                            text_count += 1
                            logger.info(f"    Text length: {len(item.text) if item.text else 0}")
                            logger.info(f"    Text preview: {item.text[:200] if item.text else 'None'}...")
                    
                    logger.info(f"  Round {round_num} summary: {function_call_count} functions, {text_count} text items")
                    
                    for item in final_response.output:
                        if item.type == "function_call":
                            # Skip if this call_id is already in our input_list
                            if hasattr(item, 'call_id') and item.call_id in existing_ids:
                                logger.info(f"  Round {round_num}: Skipping execution of duplicate function {item.call_id}")
                                continue
                                
                            has_function_calls = True
                            function_call_count += 1
                            # Execute this function call too
                            if item.name == "get_zone_boundaries":
                                args = json.loads(item.arguments)
                                boundaries = get_zone_boundaries(args["view"], args["zone"])
                                input_list.append({
                                    "type": "function_call_output",
                                    "call_id": item.call_id,
                                    "output": json.dumps(boundaries)
                                })
                                logger.info(f"  Round {round_num}: Executed get_zone_boundaries({args['view']}, {args['zone']})")
                                logger.info(f"     Result: center=({boundaries.get('center', {}).get('x')}, {boundaries.get('center', {}).get('y')}), bounds=[{boundaries.get('min_x')},{boundaries.get('max_x')}] x [{boundaries.get('min_y')},{boundaries.get('max_y')}]")
                            elif item.name == "list_available_zones":
                                args = json.loads(item.arguments) if item.arguments else {}
                                zones = list_available_zones(args.get("view"))
                                input_list.append({
                                    "type": "function_call_output",
                                    "call_id": item.call_id,
                                    "output": json.dumps(zones)
                                })
                                logger.info(f"  Round {round_num}: Executed list_available_zones({args.get('view', 'all')})")
                            elif item.name == "validate_player_positions":
                                args = json.loads(item.arguments) if item.arguments else {}
                                validation = validate_player_positions(args.get("positions", []), args.get("situation", ""))
                                input_list.append({
                                    "type": "function_call_output",
                                    "call_id": item.call_id,
                                    "output": json.dumps(validation)
                                })
                                logger.info(f"  Round {round_num}: Executed validate_player_positions")
                                logger.info(f"     Validation: {validation['summary']}")
                                if validation['issues']:
                                    logger.warning(f"     Issues: {validation['issues']}")
                                if validation['warnings']:
                                    logger.info(f"     Warnings: {validation['warnings']}")
                    
                    if has_function_calls:
                        logger.info(f"  Round {round_num}: Model made {function_call_count} more function calls")
                
                # Add the response to input for next round if needed
                if has_function_calls:
                    # Already handled duplicates when executing functions
                    # Just add all non-duplicate items
                    for item in final_response.output:
                        # Skip items we already skipped during execution
                        if hasattr(item, 'call_id') and item.call_id in existing_ids:
                            logger.warning(f"  Round {round_num}: Skipping duplicate call_id: {item.call_id}")
                            continue
                        input_list.append(item)
                    round_num += 1
                else:
                    # We got the final answer
                    logger.info(f"Got final answer in round {round_num}")
                    break
            
            if not result_text:
                logger.error(f"Failed to get text response after {max_rounds} rounds")
        
        # DEBUG: Log final result processing
        logger.info("🔍 DEBUG: Final result processing:")
        logger.info(f"  Raw result text length: {len(result_text) if result_text else 0}")
        logger.info(f"  Raw result preview: {result_text[:300] if result_text else 'None'}...")
        
        # Parse the JSON response (handle markdown code blocks)
        try:
            original_text = result_text
            
            # Extract JSON from markdown if present
            if result_text and "```json" in result_text:
                # Extract content between ```json and ```
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
                if json_match:
                    result_text = json_match.group(1)
                    logger.info("🔧 Extracted JSON from markdown code block")
            elif result_text and "```" in result_text:
                # Extract content between ``` and ```
                import re
                json_match = re.search(r'```\s*(.*?)\s*```', result_text, re.DOTALL)
                if json_match:
                    result_text = json_match.group(1)
                    logger.info("🔧 Extracted JSON from code block")
            
            logger.info(f"🔍 DEBUG: Processing JSON (length: {len(result_text) if result_text else 0})")
            
            result = json.loads(result_text)
            
            # DEBUG: Log parsed result details
            logger.info("🔍 DEBUG: Parsed JSON result:")
            logger.info(f"  Keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            if isinstance(result, dict) and 'players_mapped' in result:
                players_mapped = result.get('players_mapped', [])
                logger.info(f"  Players mapped: {len(players_mapped)}")
                
                # Log detailed reasoning for ALL players
                logger.info("📊 DETAILED PLAYER REASONING:")
                for i, player in enumerate(players_mapped):
                    coords = player.get('coordinates', {})
                    player_id = player.get('id', 'No ID')
                    x_coord = coords.get('x', 'No X')
                    y_coord = coords.get('y', 'No Y')
                    zone = player.get('zone', 'No zone')
                    area = player.get('area', 'No area')
                    confidence = player.get('confidence', 0)
                    reasoning = player.get('reasoning', 'No reasoning provided')
                    
                    logger.info(f"  🏒 Player {player_id}:")
                    logger.info(f"     Position: ({x_coord}, {y_coord})")
                    logger.info(f"     Zone: {zone}, Area: {area}")
                    logger.info(f"     Confidence: {confidence}")
                    logger.info(f"     Reasoning: {reasoning}")
                    
                    # Check for potential issues
                    if isinstance(x_coord, (int, float)):
                        if abs(x_coord) > 25 and "center ice" in player.get('original_position', '').lower():
                            logger.warning(f"     ⚠️  WARNING: Player {player_id} described as 'center ice' but x={x_coord} (should be near 0)")
                
                # Log overall reasoning if present
                if 'overall_reasoning' in result:
                    logger.info("📋 OVERALL POSITIONING STRATEGY:")
                    logger.info(f"  {result['overall_reasoning']}")
                
                # Log spatial checks
                if 'spatial_checks' in result:
                    spatial = result['spatial_checks']
                    logger.info("🔍 SPATIAL VALIDATION:")
                    logger.info(f"  Overlaps detected: {spatial.get('overlaps_detected', False)}")
                    if spatial.get('out_of_bounds'):
                        logger.warning(f"  ⚠️  Out of bounds: {spatial.get('out_of_bounds')}")
                    if spatial.get('spacing_issues'):
                        logger.warning(f"  ⚠️  Spacing issues: {spatial.get('spacing_issues')}")
                
                # Log questions for user
                if 'questions_for_user' in result and result['questions_for_user']:
                    logger.info("❓ CLARIFICATION QUESTIONS:")
                    for q in result['questions_for_user']:
                        logger.info(f"  - {q.get('player_id')}: {q.get('question')}")
                        if q.get('options'):
                            logger.info(f"    Options: {q.get('options')}")
            
            logger.info(f"✅ Mapped {len(result.get('players_mapped', []))} player positions")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {result_text[:500] if result_text else 'None'}")
            # Return a default structure
            result = {"players_mapped": [], "error": "Failed to parse LLM response"}
        
        # Add response_id and clarifications info for conversation continuity
        if isinstance(result, dict):
            result["response_id"] = response_id
            result["clarifications_applied"] = clarifications or {}
            # Include the conversation history for subsequent calls
            result["conversation_history"] = input_list
            logger.info(f"📚 Returning conversation history with {len(input_list)} items for continuity")
        
        return result
        
    except Exception as e:
        logger.error(f"Position mapping failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"error": str(e), "players_mapped": [], "response_id": None}

def map_movements_with_llm(
    movements: List[Dict[str, Any]], 
    players: List[Dict[str, Any]],
    rink_view: str = "offensive",
    clarifications: Optional[Dict[str, Any]] = None,
    previous_response_id: Optional[str] = None,
    existing_spec_context: Optional[Dict[str, Any]] = None,
    conversation_history: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Map movement descriptions to coordinate paths using LLM with spatial awareness.
    Uses OpenAI Responses API for native function calling.
    Enhanced for conversational updates with clarifications.
    
    Args:
        movements: List of movement dictionaries with descriptions
        players: List of player dictionaries with positions (for start points)
        rink_view: The rink view context
        clarifications: Optional clarifications from user to update movements
        previous_response_id: Previous response ID for conversation continuity
        existing_spec_context: Previous spec to use as foundation for updates
        conversation_history: Previous conversation history including function outputs
    
    Returns:
        Mapped movements with paths, waypoints and confidence
    """
    # Load movement mapping prompt
    prompt_config_path = Path(__file__).parent.parent / "config" / "prompts" / "map_movements.json"
    try:
        with open(prompt_config_path, 'r') as f:
            movement_prompt_config = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load movement mapping prompt: {e}")
        return {"error": "Failed to load movement mapping configuration"}
    
    # Import zone boundaries and curve generation functions
    import sys
    zone_path = Path(__file__).parent.parent / "src"
    if str(zone_path) not in sys.path:
        sys.path.append(str(zone_path))
    from zone_boundaries import get_zone_boundaries, list_available_zones
    from curve_generator import generate_curve_waypoints, suggest_curve_type, validate_path
    
    # Define tools for spatial awareness and curve generation
    tools = [
        {
            "type": "function",
            "name": "list_available_zones",
            "description": "List all available zones that can be queried for boundaries",
            "parameters": {
                "type": "object",
                "properties": {
                    "view": {
                        "type": "string",
                        "enum": ["offensive", "defensive", "neutral"],
                        "description": "Optional view filter"
                    }
                }
            }
        },
        {
            "type": "function",
            "name": "get_zone_boundaries",
            "description": "Get boundary coordinates for a specific zone/area on the rink",
            "parameters": {
                "type": "object",
                "properties": {
                    "view": {
                        "type": "string",
                        "enum": ["offensive", "defensive", "neutral", "full"],
                        "description": "Rink view context"
                    },
                    "zone": {
                        "type": "string",
                        "description": "Specific area name (e.g., 'slot', 'left_circle')"
                    }
                },
                "required": ["view", "zone"]
            }
        },
        {
            "type": "function",
            "name": "generate_curve_waypoints",
            "description": "Generate smooth curve waypoints for realistic hockey movements between two points",
            "parameters": {
                "type": "object",
                "properties": {
                        "start": {
                            "type": "object",
                            "properties": {
                                "x": {"type": "number"},
                                "y": {"type": "number"}
                            },
                            "required": ["x", "y"],
                            "description": "Starting position"
                        },
                        "end": {
                            "type": "object",
                            "properties": {
                                "x": {"type": "number"},
                                "y": {"type": "number"}
                            },
                            "required": ["x", "y"],
                            "description": "Ending position"
                        },
                        "curve_type": {
                            "type": "string",
                            "enum": ["standard", "behind_net", "rush", "bank", "button_hook", "cycle", "circle", "turn_tight", "turn_gradual"],
                            "description": "Type of curve: standard (gentle arc), behind_net (around net), rush (slight weave), bank (off boards), button_hook (curl back), cycle (along boards), circle (around faceoff circle), turn_tight (sharp U-turn), turn_gradual (wide sweeping turn)"
                        },
                        "curve_intensity": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "How much curve to apply (0=straight, 1=maximum curve)"
                        },
                        "num_waypoints": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 5,
                            "description": "Number of waypoints to generate"
                        },
                        "circle_center": {
                            "type": "object",
                            "properties": {
                                "x": {"type": "number"},
                                "y": {"type": "number"}
                            },
                            "description": "Optional center point for circle skating (auto-detected if not provided)"
                        }
                },
                "required": ["start", "end"]
            }
        },
        {
            "type": "function",
            "name": "suggest_curve_type",
            "description": "Get suggested curve parameters based on movement context",
            "parameters": {
                "type": "object",
                "properties": {
                        "movement_type": {
                            "type": "string",
                            "enum": ["pass", "skate", "carry"],
                            "description": "Type of movement"
                        },
                        "start": {
                            "type": "object",
                            "properties": {
                                "x": {"type": "number"},
                                "y": {"type": "number"}
                            },
                            "required": ["x", "y"],
                            "description": "Starting position"
                        },
                        "end": {
                            "type": "object",
                            "properties": {
                                "x": {"type": "number"},
                                "y": {"type": "number"}
                            },
                            "required": ["x", "y"],
                            "description": "Ending position"
                        },
                        "description": {
                            "type": "string",
                            "description": "Natural language description of the movement"
                        }
                },
                "required": ["movement_type", "start", "end"]
            }
        },
        {
            "type": "function",
            "name": "validate_path",
            "description": "Validate that a path is legal and realistic for hockey movements",
            "parameters": {
                "type": "object",
                "properties": {
                        "start": {
                            "type": "object",
                            "properties": {
                                "x": {"type": "number"},
                                "y": {"type": "number"}
                            },
                            "required": ["x", "y"],
                            "description": "Starting position"
                        },
                        "end": {
                            "type": "object",
                            "properties": {
                                "x": {"type": "number"},
                                "y": {"type": "number"}
                            },
                            "required": ["x", "y"],
                            "description": "Ending position"
                        },
                        "waypoints": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "x": {"type": "number"},
                                    "y": {"type": "number"}
                                },
                                "required": ["x", "y"]
                            },
                            "description": "List of intermediate waypoints"
                        }
                },
                "required": ["start", "end", "waypoints"]
            }
        }
    ]
    
    # Build context for prompt
    model_config = movement_prompt_config.get("model_config", {})
    
    # Debug: log tools to check structure
    logger.debug(f"Tools array has {len(tools)} tools")
    for i, tool in enumerate(tools):
        if 'name' in tool:
            logger.debug(f"Tool {i}: {tool['name']}")
        else:
            logger.error(f"Tool {i} missing name field")
    
    # Create player position lookup for start points
    player_positions = {p["id"]: p.get("coordinates", p.get("position", {})) for p in players}
    
    # Format movements for LLM with explicit player positions
    movements_with_context = []
    for movement in movements:
        player_id = movement.get("player_id")
        player_pos = player_positions.get(player_id, {})
        
        movement_data = {
            "id": movement.get("id", f"movement_{len(movements_with_context)}"),
            "type": movement.get("type", "unknown"),
            "player_id": player_id,
            "description": movement.get("description", ""),
            "player_position": player_pos,
            "start_x": player_pos.get("x", 0),
            "start_y": player_pos.get("y", 0)
        }
        
        # Add destination for movements
        if movement.get("type") == "pass" and movement.get("target_player_id"):
            # Find target player position - check both by ID and label
            target_id = movement["target_player_id"]
            target_pos = player_positions.get(target_id, {})
            
            # If not found by ID, try to find by label
            if not target_pos:
                for p in players:
                    if p.get("label") == target_id:
                        target_pos = p.get("coordinates", {})
                        break
            
            if target_pos:
                movement_data["target_position"] = target_pos
                movement_data["target_player_id"] = target_id
                movement_data["end_x"] = target_pos.get("x", 85)
                movement_data["end_y"] = target_pos.get("y", 0)
                movement_data["instruction"] = f"Pass must end at {target_id} position"
            else:
                # Fallback to area description
                movement_data["instruction"] = f"Pass to {movement.get('description', 'target area')}"
        elif movement.get("type") == "shot":
            # Shots always target the net
            movement_data["end_x"] = 89
            movement_data["end_y"] = 0
            movement_data["instruction"] = "Shot must target the net at (89, 0)"
            
        movements_with_context.append(movement_data)
    
    # Prepare prompt with player positions
    prompt_template = movement_prompt_config["main_prompt_template"]
    
    # Add player positions to context
    players_context = "PLAYER POSITIONS:\n"
    for p in players:
        coords = p.get("coordinates", {})
        players_context += f"- {p['id']} ({p.get('label', p['id'])}): x={coords.get('x', 0):.1f}, y={coords.get('y', 0):.1f}\n"
    
    # Update instructions to use player positions
    enhanced_instructions = movement_prompt_config["instructions"] + "\n\n" + players_context
    
    prompt = prompt_template.format(
        rink_view=rink_view,
        zone_context=f"Mapping movements in {rink_view} view",
        movements_json=json.dumps(movements_with_context, indent=2),
        instructions=enhanced_instructions,
        rink_reference=movement_prompt_config["rink_reference"],
        movement_patterns=movement_prompt_config["movement_patterns"],
        output_format=movement_prompt_config["output_format"]
    )
    
    # Add clarifications if provided
    if clarifications:
        clarification_text = build_clarification_text(clarifications)
        prompt += f"\n\nUser Clarifications:\n{clarification_text}"
        prompt += "\n\nUpdate the movement paths based on these clarifications. "
        prompt += "Focus only on changes needed due to clarifications."
    
    # Add existing spec context for updates (hybrid approach)
    if existing_spec_context:
        prompt += "\n\nSPEC UPDATE MODE - MOVEMENT MAPPING\n\n"
        prompt += "EXISTING SPEC CONTEXT:\n"
        prompt += json.dumps(existing_spec_context, indent=2)
        prompt += "\n\nINSTRUCTIONS:\n"
        prompt += "1. START with the existing movements as your foundation\n"
        prompt += "2. Apply clarifications while maintaining overall cohesion\n"
        prompt += "3. Keep unchanged movement elements stable unless clarifications require changes\n"
        prompt += "4. Ensure your updates work with the overall spec context\n"
        prompt += "5. Be conservative - only change what the clarifications specifically request\n"
    
    # Create input list for Responses API
    if conversation_history and previous_response_id:
        # Continue from previous conversation with function outputs
        # Clean the conversation history to remove duplicate IDs
        seen_ids = set()
        cleaned_history = []
        for item in conversation_history:
            # Check for function calls - they're objects with .type attribute
            if hasattr(item, 'type') and item.type == "function_call":
                # Function call objects have a call_id attribute
                if hasattr(item, 'call_id') and item.call_id:
                    if item.call_id in seen_ids:
                        logger.warning(f"Skipping duplicate movement function call ID: {item.call_id}")
                        continue
                    seen_ids.add(item.call_id)
            # Check for function call outputs (dicts)
            elif isinstance(item, dict) and item.get("type") == "function_call_output":
                # Function call outputs have call_id field
                call_id = item.get("call_id")
                if call_id and call_id in seen_ids:
                    logger.warning(f"Skipping duplicate movement function output ID: {call_id}")
                    continue
                if call_id:
                    seen_ids.add(call_id)
            cleaned_history.append(item)
        
        input_list = cleaned_history + [
            {"role": "user", "content": prompt},
            {"role": "user", "content": movement_prompt_config["tool_instructions"]}
        ]
        logger.info(f"📚 Using conversation history with {len(cleaned_history)} items for movements (cleaned from {len(conversation_history)})")
    else:
        # Start fresh conversation
        input_list = [
            {"role": "system", "content": movement_prompt_config["system_prompt"]},
            {"role": "user", "content": prompt},
            {"role": "user", "content": movement_prompt_config["tool_instructions"]}
        ]
    
    try:
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        client = OpenAI(api_key=api_key)
        
        # Build API request parameters
        api_request = {
            "model": model_config.get("model", "gpt-4o-mini"),
            "instructions": movement_prompt_config["system_prompt"],
            "tools": tools,
            "input": input_list,
            "max_output_tokens": model_config.get("max_tokens", 2500),
            "temperature": model_config.get("temperature", 0.2)
        }
        
        # Include previous_response_id for conversation continuity if provided
        if previous_response_id:
            api_request["previous_response_id"] = previous_response_id
            logger.info(f"🔄 Continuing movement conversation from response: {previous_response_id}")
        
        # Call Responses API with native function calling
        logger.info("🏃 Mapping movements with LLM using spatial awareness...")
        response = client.responses.create(**api_request)
        
        # Capture response ID for conversation continuity
        response_id = response.id if hasattr(response, 'id') else None
        
        # Process response and handle function calls
        function_calls_made = 0
        final_output = None
        
        # Add the response output to input list, checking for duplicates
        # Track IDs we've already seen (from cleaned history)
        existing_ids = set()
        for hist_item in input_list:
            if hasattr(hist_item, 'call_id'):
                existing_ids.add(hist_item.call_id)
            elif isinstance(hist_item, dict) and hist_item.get('call_id'):
                existing_ids.add(hist_item['call_id'])
        
        # Add new response items, skipping duplicates
        for item in response.output:
            if hasattr(item, 'call_id') and item.call_id in existing_ids:
                logger.warning(f"Skipping duplicate response item with call_id: {item.call_id}")
                continue
            input_list.append(item)
        
        for item in response.output:
            if item.type == "function_call":
                function_calls_made += 1
                # Map function names to actual functions
                if item.name == "list_available_zones":
                    args = json.loads(item.arguments) if isinstance(item.arguments, str) else item.arguments
                    result = list_available_zones(args.get("view"))
                    input_list.append({
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps(result)
                    })
                    logger.info(f"🔧 Listed zones for view: {args.get('view', 'all')}")
                elif item.name == "get_zone_boundaries":
                    args = json.loads(item.arguments) if isinstance(item.arguments, str) else item.arguments
                    result = get_zone_boundaries(args["view"], args["zone"])
                    input_list.append({
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps(result)
                    })
                    logger.info(f"🔧 Got boundaries for: {args['view']} - {args['zone']}")
                elif item.name == "generate_curve_waypoints":
                    args = json.loads(item.arguments) if isinstance(item.arguments, str) else item.arguments
                    result = generate_curve_waypoints(
                        args["start"],
                        args["end"],
                        args.get("curve_type", "standard"),
                        args.get("curve_intensity", 0.5),
                        args.get("num_waypoints", 3),
                        args.get("circle_center")
                    )
                    input_list.append({
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps(result)
                    })
                    logger.info(f"🎯 Generated {len(result)} waypoints for {args.get('curve_type', 'standard')} curve")
                elif item.name == "suggest_curve_type":
                    args = json.loads(item.arguments) if isinstance(item.arguments, str) else item.arguments
                    result = suggest_curve_type(
                        args["movement_type"],
                        args["start"],
                        args["end"],
                        args.get("description", "")
                    )
                    input_list.append({
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps(result)
                    })
                    logger.info(f"💡 Suggested curve: {result['curve_type']} for {args['movement_type']}")
                elif item.name == "validate_path":
                    args = json.loads(item.arguments) if isinstance(item.arguments, str) else item.arguments
                    result = validate_path(
                        args["start"],
                        args["end"],
                        args["waypoints"]
                    )
                    input_list.append({
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps(result)
                    })
                    issues_count = len(result.get('issues', []))
                    status = 'Valid' if result.get('valid', False) else f'Invalid - {issues_count} issues'
                    logger.info(f"✅ Validated path: {status}")
            elif item.type == "message":
                final_output = item.content if hasattr(item, 'content') else None
        
        # If function calls were made, get final response
        if function_calls_made > 0:
            logger.info(f"🏃 Made {function_calls_made} function calls for movement paths")
            
            # Keep making calls until we get text output
            max_rounds = 3
            round_num = 2
            
            while round_num <= max_rounds:
                final_response = client.responses.create(
                    model=model_config.get("model", "gpt-4o-mini"),
                    instructions=f"Complete the movement mapping using the function results. Return ONLY valid JSON. This is round {round_num}.",
                    tools=tools,
                    tool_choice="none" if round_num >= 3 else "auto",  # Disable tools after round 2
                    input=input_list,
                    max_output_tokens=model_config.get("max_tokens", 2500),
                    temperature=model_config.get("temperature", 0.2)
                )
                
                # Update response ID from the latest call
                if hasattr(final_response, 'id'):
                    response_id = final_response.id
                
                # Check if we got text or more function calls
                has_more_calls = False
                result_text = final_response.output_text if hasattr(final_response, 'output_text') else None
                
                # Log what we received
                logger.debug(f"Round {round_num} - output_text: {result_text[:50] if result_text else 'None'}")
                
                if not result_text and hasattr(final_response, 'output'):
                    logger.debug(f"Round {round_num} - output items: {len(final_response.output)}")
                    
                    # First check for duplicate IDs before processing
                    existing_ids = set()
                    skipped_call_ids = set()
                    for hist_item in input_list:
                        if hasattr(hist_item, 'call_id'):
                            existing_ids.add(hist_item.call_id)
                        elif isinstance(hist_item, dict) and hist_item.get('call_id'):
                            existing_ids.add(hist_item['call_id'])
                    
                    # Identify which calls to skip
                    for item in final_response.output:
                        if hasattr(item, 'type') and item.type == "function_call":
                            if hasattr(item, 'call_id') and item.call_id in existing_ids:
                                logger.warning(f"  Round {round_num}: Marking duplicate call_id to skip: {item.call_id}")
                                skipped_call_ids.add(item.call_id)
                    
                    for i, item in enumerate(final_response.output):
                        logger.debug(f"  Item {i}: type={item.type}")
                        
                        if item.type == "function_call":
                            # Skip if duplicate
                            if hasattr(item, 'call_id') and item.call_id in skipped_call_ids:
                                logger.warning(f"  Round {round_num}: Skipping duplicate function call: {item.call_id}")
                                continue
                                
                            has_more_calls = True
                            # Process any additional function calls
                            logger.info(f"Round {round_num}: Additional function call to {item.name}")
                            
                            # Execute the function call
                            if item.name == "generate_curve_waypoints":
                                args = json.loads(item.arguments) if isinstance(item.arguments, str) else item.arguments
                                waypoints = generate_curve_waypoints(
                                    args["start"],
                                    args["end"],
                                    args.get("curve_type", "standard"),
                                    args.get("curve_intensity", 0.5),
                                    args.get("num_waypoints", 3),
                                    args.get("circle_center")
                                )
                                input_list.append({
                                    "type": "function_call_output",
                                    "call_id": item.call_id,
                                    "output": json.dumps(waypoints)
                                })
                                logger.info(f"  Generated {len(waypoints)} waypoints")
                                
                        elif item.type == "message":
                            # Extract text content from the message
                            if hasattr(item, 'content'):
                                # Check if content is a list of content items
                                if isinstance(item.content, list):
                                    # Extract text from content items
                                    text_parts = []
                                    for content_item in item.content:
                                        if hasattr(content_item, 'text'):
                                            text_parts.append(content_item.text)
                                        elif isinstance(content_item, str):
                                            text_parts.append(content_item)
                                    content = ' '.join(text_parts)
                                elif isinstance(item.content, str):
                                    content = item.content
                                else:
                                    content = str(item.content)
                            else:
                                content = str(item)
                            
                            logger.debug(f"  Message content: {content[:100] if content else 'None'}")
                            result_text = content
                            break
                    
                    # Add response to input list, using the skipped_call_ids we already identified
                    for item in final_response.output:
                        # Skip duplicate function calls
                        if hasattr(item, 'type') and item.type == "function_call":
                            if hasattr(item, 'call_id') and item.call_id in skipped_call_ids:
                                # Already logged above, just skip
                                continue
                        # Skip outputs for skipped function calls 
                        elif hasattr(item, 'type') and item.type == "function_call_output":
                            if hasattr(item, 'call_id') and item.call_id in skipped_call_ids:
                                logger.warning(f"  Round {round_num}: Skipping output for duplicate call_id: {item.call_id}")
                                continue
                        input_list.append(item)
                
                if result_text:
                    logger.info(f"Got final result in round {round_num} - length: {len(result_text)}")
                    logger.debug(f"Result text preview: {result_text[:100] if result_text else 'None'}")
                    break
                elif not has_more_calls:
                    # No text and no function calls, try to extract from output
                    logger.warning(f"Round {round_num}: No text or function calls in response")
                    result_text = "{}"
                    break
                    
                round_num += 1
            else:
                # Max rounds reached
                logger.warning(f"Max rounds ({max_rounds}) reached without result")
                result_text = final_output or "{}"
        else:
            logger.info("🏃 Direct movement mapping without function calls")
            result_text = response.output_text if hasattr(response, 'output_text') else final_output or "{}"
        
        # Parse the JSON response
        logger.info(f"Result text first 100 chars: {result_text[:100] if result_text else 'Empty'}")
        logger.debug(f"Result text to parse: {result_text[:200] if result_text else 'None'}")
        
        if not result_text or result_text.strip() == "":
            logger.warning("Empty result text, returning empty mapping")
            return {"movements_mapped": [], "error": "No output from LLM", "response_id": response_id}
        
        # Check if result_text is actually the ResponseFunctionToolCall object
        if not isinstance(result_text, str):
            logger.error(f"Result text is not a string, it's: {type(result_text)}")
            result_text = str(result_text)
        
        # Extract JSON from markdown if present (same as position mapping)
        if result_text and "```json" in result_text:
            # Extract content between ```json and ```
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group(1)
                logger.info("Extracted JSON from markdown code block")
        elif result_text and "```" in result_text:
            # Extract content between ``` and ```
            import re
            json_match = re.search(r'```\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group(1)
                logger.info("Extracted JSON from code block")
        
        result = json.loads(result_text)
        logger.info(f"✅ Mapped {len(result.get('movements_mapped', []))} movements")
        
        # Add response_id and clarifications info for conversation continuity
        if isinstance(result, dict):
            result["response_id"] = response_id
            result["clarifications_applied"] = clarifications or {}
            # Include the conversation history for subsequent calls
            result["conversation_history"] = input_list
            logger.info(f"📚 Returning conversation history with {len(input_list)} items for continuity")
        
        return result
        
    except Exception as e:
        logger.error(f"Movement mapping failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"error": str(e), "movements_mapped": [], "response_id": None}

def map_equipment_with_llm(
    equipment_items: List[Dict[str, Any]],
    rink_view: str = "offensive",
    clarifications: Optional[Dict[str, Any]] = None,
    previous_response_id: Optional[str] = None,
    existing_spec_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Map equipment position descriptions to precise coordinates using LLM.
    Handles custom locations like "10 feet from blue line" or "between the circles".
    Uses OpenAI Responses API with zone boundary tools for accurate positioning.
    Enhanced for conversational updates with clarifications.
    
    Args:
        equipment_items: List of equipment dictionaries with position descriptions
        rink_view: The rink view context
        clarifications: Optional clarifications from user to update equipment positions
        previous_response_id: Previous response ID for conversation continuity
        existing_spec_context: Previous spec to use as foundation for updates
    
    Returns:
        Mapped equipment with coordinates and confidence
    """
    if not equipment_items:
        return {"equipment_mapped": []}
    
    # Load equipment mapping prompt configuration
    prompt_config_path = Path(__file__).parent.parent / "config" / "prompts" / "map_equipment.json"
    try:
        with open(prompt_config_path, 'r') as f:
            equipment_prompt_config = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load equipment mapping prompt: {e}")
        return {"error": "Failed to load equipment mapping configuration"}
    
    # Import zone boundaries functions
    sys.path.append(str(Path(__file__).parent.parent / "src"))
    from zone_boundaries import get_zone_boundaries, list_available_zones
    
    # Build the main prompt
    prompt = equipment_prompt_config["main_prompt_template"].format(
        rink_view=rink_view,
        equipment_context=equipment_prompt_config["equipment_context"],
        equipment_json=json.dumps(equipment_items, indent=2),
        instructions=equipment_prompt_config["instructions"],
        coordinate_reference=equipment_prompt_config["coordinate_reference"],
        output_format=equipment_prompt_config["output_format"]
    )
    
    # Add clarifications if provided
    if clarifications:
        clarification_text = build_clarification_text(clarifications)
        prompt += f"\n\nUser Clarifications:\n{clarification_text}"
        prompt += "\n\nUpdate the equipment positions based on these clarifications. "
        prompt += "Focus only on changes needed due to clarifications."
    
    # Add existing spec context for updates (hybrid approach)
    if existing_spec_context:
        prompt += "\n\nSPEC UPDATE MODE - EQUIPMENT MAPPING\n\n"
        prompt += "EXISTING SPEC CONTEXT:\n"
        prompt += json.dumps(existing_spec_context, indent=2)
        prompt += "\n\nINSTRUCTIONS:\n"
        prompt += "1. START with the existing equipment as your foundation\n"
        prompt += "2. Apply clarifications while maintaining overall cohesion\n"
        prompt += "3. Keep unchanged equipment elements stable unless clarifications require changes\n"
        prompt += "4. Ensure your updates work with the overall spec context\n"
        prompt += "5. Be conservative - only change what the clarifications specifically request\n"
    
    # Add tool usage instructions
    prompt += "\n\nIMPORTANT: Use the zone boundary tools to get precise coordinates for named areas like 'slot', 'circles', 'blue line', etc."
    
    # Define the zone boundary tools (same as position mapping)
    tools = [
        {
            "type": "function",
            "function": {
                "name": "list_available_zones",
                "description": "List all available zones that can be queried for boundaries",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "view": {
                            "type": "string",
                            "enum": ["offensive", "defensive", "neutral", "full", "all"],
                            "description": "View filter (use 'all' to see everything)"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_zone_boundaries",
                "description": "Get boundary coordinates for a specific zone/area on the rink",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "view": {
                            "type": "string",
                            "enum": ["offensive", "defensive", "neutral", "full"],
                            "description": "Rink view context"
                        },
                        "zone": {
                            "type": "string",
                            "description": "Specific area name (e.g., 'slot', 'left_circle', 'blue_line')"
                        }
                    },
                    "required": ["view", "zone"]
                }
            }
        }
    ]
    
    # Tool implementations
    def list_available_zones_impl(view=None):
        result = list_available_zones(view)
        logger.info(f"📋 Listed zones for view: {view}")
        return result
    
    def get_zone_boundaries_impl(view, zone):
        result = get_zone_boundaries(view, zone)
        logger.info(f"📍 Got boundaries for {view}/{zone}")
        return result
    
    tool_map = {
        "list_available_zones": list_available_zones_impl,
        "get_zone_boundaries": get_zone_boundaries_impl
    }
    
    try:
        model_config = equipment_prompt_config.get("model_config", {})
        
        # Use Responses API for function calling
        messages = [
            {"role": "system", "content": equipment_prompt_config["system_prompt"]},
            {"role": "user", "content": prompt}
        ]
        
        # Make initial call with tools
        response = client.chat.completions.create(
            model=model_config.get("model", "gpt-4o-mini"),
            messages=messages,
            tools=tools,
            temperature=model_config.get("temperature", 0.3),
            max_tokens=model_config.get("max_tokens", 1500)
        )
        
        # Handle function calls (similar to position mapping)
        max_rounds = 5
        for round_num in range(max_rounds):
            message = response.choices[0].message
            
            if message.tool_calls:
                # Execute tool calls
                messages.append(message.model_dump())
                
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    if function_name in tool_map:
                        result = tool_map[function_name](**function_args)
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result)
                        })
                        logger.info(f"  Round {round_num + 1}: Executed {function_name}")
                
                # Make next call
                response = client.chat.completions.create(
                    model=model_config.get("model", "gpt-4o-mini"),
                    messages=messages,
                    tools=tools,
                    temperature=model_config.get("temperature", 0.3)
                )
            else:
                # Got final answer
                result_text = message.content
                
                # Extract JSON from response
                if "```json" in result_text:
                    json_str = result_text.split("```json")[1].split("```")[0].strip()
                elif "```" in result_text:
                    json_str = result_text.split("```")[1].split("```")[0].strip()
                else:
                    json_str = result_text
                
                result = json.loads(json_str)
                logger.info(f"🎯 LLM mapped {len(result.get('equipment_mapped', []))} equipment items with zone awareness")
                
                # Add placeholder response_id and clarifications info for equipment mapping (uses chat completions, not responses API)
                if isinstance(result, dict):
                    result["response_id"] = None  # Equipment mapping uses chat completions API
                    result["clarifications_applied"] = clarifications or {}
                
                return result
        
        # If we hit max rounds, return error
        logger.error("Equipment mapping hit max rounds without completion")
        return {"error": "Mapping exceeded maximum rounds", "equipment_mapped": [], "response_id": None}
        
    except Exception as e:
        logger.error(f"Equipment mapping failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        # Fallback to simple mapping
        return {
            "equipment_mapped": [
                {
                    "id": eq.get("id", f"eq_{i}"),
                    "coordinates": {"x": 0, "y": 0},
                    "confidence": 0.3,
                    "reasoning": "Failed to map, using default position"
                }
                for i, eq in enumerate(equipment_items)
            ],
            "response_id": None  # Equipment mapping uses chat completions API
        }

def map_hockey_position(position_desc: str, zone: str = "offensive") -> Dict[str, float]:
    """
    Map natural language hockey position to coordinates.
    
    This is a simplified version - in production would use the full
    map_position_to_coordinates tool from v2.
    """
    # Common hockey positions with zone-aware coordinates
    position_map = {
        "offensive": {
            "right faceoff dot": {"x": 69, "y": -22.5},
            "left faceoff dot": {"x": 69, "y": 22.5},
            "right circle": {"x": 69, "y": -22.5},
            "left circle": {"x": 69, "y": 22.5},
            "slot": {"x": 75, "y": 0},
            "high slot": {"x": 65, "y": 0},
            "right point": {"x": 54, "y": -38},
            "left point": {"x": 54, "y": 38},
            "net front": {"x": 85, "y": 0},
            "behind net": {"x": 92, "y": 0},
            "right corner": {"x": 89, "y": -36},
            "left corner": {"x": 89, "y": 36},
            "right half wall": {"x": 75, "y": -38},
            "left half wall": {"x": 75, "y": 38}
        },
        "defensive": {
            "right faceoff dot": {"x": -69, "y": -22.5},
            "left faceoff dot": {"x": -69, "y": 22.5},
            "slot": {"x": -75, "y": 0},
            "right point": {"x": -54, "y": -38},
            "left point": {"x": -54, "y": 38},
            "net front": {"x": -85, "y": 0},
            "behind net": {"x": -92, "y": 0},
            "right corner": {"x": -89, "y": -36},
            "left corner": {"x": -89, "y": 36}
        },
        "neutral": {
            "center ice": {"x": 0, "y": 0},
            "right neutral dot": {"x": 20, "y": -22.5},
            "left neutral dot": {"x": 20, "y": 22.5},
            "center ice faceoff": {"x": 0, "y": 0}
        }
    }
    
    # Try to find exact match first
    zone_positions = position_map.get(zone, position_map["offensive"])
    
    # Check for exact match
    position_lower = position_desc.lower()
    for key, coords in zone_positions.items():
        if key in position_lower:
            return coords
    
    # Fallback to pattern matching
    if "dot" in position_lower or "faceoff" in position_lower:
        if "right" in position_lower:
            return zone_positions.get("right faceoff dot", {"x": 69, "y": -22.5})
        elif "left" in position_lower:
            return zone_positions.get("left faceoff dot", {"x": 69, "y": 22.5})
    
    if "point" in position_lower:
        if "right" in position_lower or "strong" in position_lower:
            return zone_positions.get("right point", {"x": 54, "y": -38})
        elif "left" in position_lower or "weak" in position_lower:
            return zone_positions.get("left point", {"x": 54, "y": 38})
    
    if "corner" in position_lower:
        if "right" in position_lower:
            return zone_positions.get("right corner", {"x": 89, "y": -36})
        elif "left" in position_lower:
            return zone_positions.get("left corner", {"x": 89, "y": 36})
    
    # Default fallback based on zone
    defaults = {
        "offensive": {"x": 69, "y": 0},
        "defensive": {"x": -69, "y": 0},
        "neutral": {"x": 0, "y": 0}
    }
    
    return defaults.get(zone, {"x": 0, "y": 0})

def map_coach_position(position_desc: str, zone: str = "offensive") -> Dict[str, float]:
    """
    Map natural language coach position to coordinates.
    Coaches are positioned for observation and instruction, not gameplay.
    """
    if not position_desc:
        # Default coach position based on zone
        defaults = {
            "offensive": {"x": 50, "y": 0},    # Behind play for observation
            "defensive": {"x": -50, "y": 0},   # Behind play for observation
            "neutral": {"x": 0, "y": 40},      # Center ice, boards
            "full": {"x": 0, "y": 40}          # Center ice, boards for full rink
        }
        return defaults.get(zone, {"x": 0, "y": 40})
    
    position_lower = position_desc.lower()
    
    # Common coach positions based on existing spec examples
    coach_positions = {
        # Specific locations
        "center ice": {"x": 0, "y": 0},
        "centre ice": {"x": 0, "y": 0},
        "blue line": {"x": 25, "y": 0},
        "goal line": {"x": 89, "y": 0},
        "behind goal": {"x": 94, "y": 0},
        "behind net": {"x": 94, "y": 0},
        
        # Bench and board positions
        "bench": {"x": 0, "y": -42},
        "on bench": {"x": 0, "y": -42},
        "boards": {"x": 0, "y": 40},
        "at boards": {"x": 0, "y": 40},
        
        # Corner positions for observation
        "corner": {"x": 89, "y": 35},
        "offensive corner": {"x": 89, "y": 35},
        "defensive corner": {"x": -89, "y": 35},
        
        # Zone-specific positions
        "offensive zone": {"x": 75, "y": 40},
        "defensive zone": {"x": -75, "y": 40},
        "neutral zone": {"x": 0, "y": 40},
    }
    
    # Check for exact matches first
    for key, coords in coach_positions.items():
        if key in position_lower:
            return coords
    
    # Pattern matching for directional positions
    if "right" in position_lower:
        if "corner" in position_lower:
            return {"x": 89, "y": -35}
        elif "boards" in position_lower:
            return {"x": 0, "y": -40}
        else:
            return {"x": 50, "y": -30}
    
    if "left" in position_lower:
        if "corner" in position_lower:
            return {"x": 89, "y": 35}
        elif "boards" in position_lower:
            return {"x": 0, "y": 40}
        else:
            return {"x": 50, "y": 30}
    
    # Fallback based on zone
    if zone == "offensive":
        return {"x": 50, "y": 0}
    elif zone == "defensive":
        return {"x": -50, "y": 0}
    else:
        return {"x": 0, "y": 40}

def get_player_type(type_desc: str) -> str:
    """Convert player type description to valid spec type."""
    type_lower = type_desc.lower()
    
    if "center" in type_lower:
        return "forward"
    elif "wing" in type_lower:
        return "forward"
    elif "forward" in type_lower:
        return "forward"
    elif "defense" in type_lower or "defence" in type_lower:
        return "defense"
    elif "goalie" in type_lower or "goal" in type_lower:
        return "goalie"
    else:
        return "forward"  # Default

def calculate_movement_waypoints(
    from_coords: Dict[str, float],
    to_coords: Dict[str, float],
    movement_type: str,
    zone: str
) -> List[List[float]]:
    """
    Calculate waypoints for smooth movement paths.
    
    This creates curved or multi-point paths for realistic hockey movements.
    """
    waypoints = []
    
    # Calculate distance
    dx = to_coords["x"] - from_coords["x"]
    dy = to_coords["y"] - from_coords["y"]
    distance = (dx**2 + dy**2) ** 0.5
    
    # Only add waypoints for longer movements
    if distance < 20:
        return []
    
    # For skating movements, add curve points
    if movement_type in ["skate", "carry"]:
        # Add 1-2 waypoints for natural skating curve
        if abs(dy) > 20:  # Significant lateral movement
            # Add curve point
            mid_x = from_coords["x"] + dx * 0.5
            mid_y = from_coords["y"] + dy * 0.7  # Curve more in y direction
            waypoints.append([mid_x, mid_y])
        elif abs(dx) > 40:  # Long forward/backward movement
            # Add slight curve
            mid_x = from_coords["x"] + dx * 0.6
            mid_y = from_coords["y"] + dy * 0.5 + (5 if dy >= 0 else -5)
            waypoints.append([mid_x, mid_y])
    
    return waypoints

# ============================================================================
# TOOL: VALIDATE DIAGRAM NODE MINIMAL
# ============================================================================

@mcp.tool("validate_diagram_node_minimal")
def validate_diagram_node_minimal(node_type: str, node_data: Any) -> Dict[str, Any]:
    """Validate a single node of the diagram spec.
    
    Args:
        node_type: Type of node (players|movements|rink|zones|annotations)
        node_data: The node data to validate
        
    Returns:
        Validation results with issues and fixes
    """
    logger.info(f"✅ [VALIDATE NODE] {node_type}")
    
    # Use modular validator for basic schema validation
    result = validate_node(node_type, node_data)
    
    # Add additional hockey-specific warnings
    warnings = []
    fixes = {}
    
    if node_type == "players" and result["valid"]:
        has_puck_count = sum(1 for p in node_data if p.get("has_puck", False))
        if has_puck_count == 0:
            warnings.append("No player has puck - is this intentional?")
            
    elif node_type == "movements" and result["valid"]:
        for i, movement in enumerate(node_data):
            # Check cross-ice movements
            if movement.get("type") == "skate":
                from_pos = movement.get("from_pos", {})
                to_pos = movement.get("to_pos", {})
                from_y = from_pos.get("y", 0)
                to_y = to_pos.get("y", 0)
                if abs(to_y - from_y) > 40:
                    if "waypoints" not in movement:
                        warnings.append(f"Movement {i}: Cross-ice movement should have waypoints for smooth curve")
                        
    elif node_type == "rink" and result["valid"]:
        if "view" not in node_data:
            warnings.append("No view specified, will use 'offensive' by default")
            fixes["rink"] = {"view": "offensive"}
    
    return {
        "valid": result["valid"],
        "issues": result.get("errors", []),
        "warnings": warnings,
        "fixes": fixes if fixes else None,
        "path": result.get("path")
    }

# ============================================================================
# TOOL: VALIDATE DIAGRAM SPEC FULL
# ============================================================================

@mcp.tool("validate_diagram_spec_full")
def validate_diagram_spec_full(spec: Dict[str, Any], original_request: Optional[str] = None, use_llm: bool = True) -> Dict[str, Any]:
    """Complete validation of entire diagram specification.
    
    Args:
        spec: Complete diagram specification
        original_request: Original drill description for context
        use_llm: Whether to use LLM for semantic validation (default: True)
        
    Returns:
        Comprehensive validation with structure, spatial, and hockey sense checks
    """
    logger.info(f"🔍 [VALIDATE FULL] Spec with {len(spec.get('players', []))} players")
    
    # Use modular validators
    validation_result = validate_spec(spec)
    structure_valid = validation_result["valid"]
    structure_issues = validation_result.get("errors", [])
    
    # Spatial validation using modular function
    spatial_issues = check_spatial_conflicts(spec)
    spatial_valid = len(spatial_issues) == 0
    
    # Hockey sense validation (LLM if available and enabled)
    hockey_sense_valid = True
    llm_feedback = None
    llm_warnings = []
    llm_issues = []
    
    if original_request and client and use_llm:
        try:
            # Build detailed spec summary for LLM
            players = spec.get('players', [])
            movements = spec.get('movements', [])
            
            # Count offensive and defensive players
            home_players = [p for p in players if p.get('team') == 'home']
            away_players = [p for p in players if p.get('team') == 'away']
            
            # Summarize player positions
            player_summary = []
            for p in players:
                pos = p.get('position', 'Unknown')
                coords = p.get('coordinates', {})
                team = p.get('team', 'unknown')
                player_summary.append(f"{pos} at ({coords.get('x', 0)}, {coords.get('y', 0)}) [{team}]")
            
            # Summarize movements
            movement_summary = []
            for m in movements:
                m_type = m.get('type', 'unknown')
                from_pos = m.get('from_pos', {})
                to_pos = m.get('to_pos', {})
                movement_summary.append(f"{m_type}: ({from_pos.get('x', 0)}, {from_pos.get('y', 0)}) → ({to_pos.get('x', 0)}, {to_pos.get('y', 0)})")
            
            prompt = f"""
            Analyze if this hockey diagram matches the drill request.
            
            DRILL REQUEST: "{original_request}"
            
            GENERATED DIAGRAM:
            Players ({len(players)} total - {len(home_players)} home/offensive, {len(away_players)} away/defensive):
            {chr(10).join(player_summary[:10]) if player_summary else "None"}
            
            Movements ({len(movements)}):
            {chr(10).join(movement_summary[:10]) if movement_summary else "None"}
            
            Zones: {len(spec.get('zones', []))} zones
            Rink view: {spec.get('rink', {}).get('view', 'full')}
            
            HOCKEY DRILL NOTATION:
            - "2v1" means 2 offensive players vs 1 defensive player (3 total)
            - "3v2" means 3 offensive players vs 2 defensive players (5 total)
            - Home team is typically offensive, away team is defensive
            
            OUTPUT FORMAT (use | as separator):
            MATCH: YES or NO
            ISSUES: List only CRITICAL mismatches (semicolon separated) or "none"
            WARNINGS: List minor concerns (semicolon separated) or "none"
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            llm_response = response.choices[0].message.content.strip()
            logger.info(f"LLM validation response: {llm_response}")
            
            # Parse LLM response
            lines = llm_response.split('\n')
            for line in lines:
                if '|' in line or ':' in line:
                    sep = '|' if '|' in line else ':'
                    parts = line.split(sep, 1)
                    if len(parts) == 2:
                        key = parts[0].strip().upper()
                        value = parts[1].strip()
                        
                        if key == "MATCH" and value.upper() == "NO":
                            hockey_sense_valid = False
                        elif key == "ISSUES" and value.lower() != "none":
                            issues = [i.strip() for i in value.split(';') if i.strip()]
                            llm_issues.extend(issues)
                        elif key == "WARNINGS" and value.lower() != "none":
                            warnings = [w.strip() for w in value.split(';') if w.strip()]
                            llm_warnings.extend(warnings)
            
            # Create consolidated feedback
            if llm_issues or llm_warnings:
                llm_feedback = "LLM Analysis: " + "; ".join(llm_issues[:2]) if llm_issues else None
                
        except Exception as e:
            logger.warning(f"LLM validation failed: {e}")
            pass
    
    # Compile results
    all_issues = structure_issues + spatial_issues + llm_issues
    all_warnings = llm_warnings
    
    suggestions = []
    if "players" in spec and len(spec["players"]) == 1 and "give" in str(original_request).lower():
        suggestions.append("Give-and-go requires 2+ players")
    
    # Add any LLM suggestions to suggestions list
    for warning in llm_warnings:
        if warning not in suggestions:
            suggestions.append(warning)
    
    return {
        "valid": structure_valid and spatial_valid and hockey_sense_valid,
        "structure_valid": structure_valid,
        "spatial_valid": spatial_valid, 
        "hockey_sense_valid": hockey_sense_valid,
        "issues": all_issues,
        "warnings": all_warnings,
        "suggestions": suggestions,
        "llm_analysis": {
            "performed": original_request is not None and client is not None and use_llm,
            "match": hockey_sense_valid,
            "feedback": llm_feedback,
            "issues": llm_issues,
            "warnings": llm_warnings
        }
    }

# ============================================================================
# TOOL: PREVIEW DIAGRAM
# ============================================================================

@mcp.tool("preview_diagram")
def preview_diagram(spec: Dict[str, Any], format: str = "ascii") -> Dict[str, Any]:
    """Preview the diagram as ASCII art or coordinate list.
    
    Args:
        spec: Diagram specification to preview
        format: "ascii" for ASCII art, "coordinates" for coordinate list
        
    Returns:
        Preview representation of the diagram
    """
    logger.info(f"👁️ [PREVIEW] Generating {format} preview")
    
    if format == "ascii":
        # Create simple ASCII representation
        ascii_width = 40
        ascii_height = 17
        
        # Initialize ASCII grid
        grid = [[' ' for _ in range(ascii_width)] for _ in range(ascii_height)]
        
        # Draw basic rink outline
        for x in range(ascii_width):
            grid[0][x] = '-'
            grid[ascii_height-1][x] = '-'
        for y in range(ascii_height):
            grid[y][0] = '|'
            grid[y][ascii_width-1] = '|'
            
        # Add center line
        center_x = ascii_width // 2
        for y in range(1, ascii_height-1):
            grid[y][center_x] = '|'
            
        # Add goals
        grid[ascii_height//2][1] = 'G'
        grid[ascii_height//2][ascii_width-2] = 'G'
        
        # Plot players
        players = spec.get("players", [])
        for player in players:
            coords = player.get("coordinates", {})
            x = coords.get("x", 0)
            y = coords.get("y", 0)
            
            # Convert rink coords to ASCII coords
            ascii_x = int((x + 100) * ascii_width / 200)
            ascii_y = int((y + 42.5) * ascii_height / 85)
            
            # Clamp to grid bounds
            ascii_x = max(1, min(ascii_width-2, ascii_x))
            ascii_y = max(1, min(ascii_height-2, ascii_y))
            
            # Get player symbol
            pos = player.get("position", "")
            if pos.startswith("F"):
                symbol = 'F'
            elif pos.startswith("D"):
                symbol = 'D'
            elif pos.startswith("G"):
                symbol = 'G'
            else:
                symbol = 'P'
                
            grid[ascii_y][ascii_x] = symbol
            
        # Plot equipment
        equipment = spec.get("equipment", [])
        for item in equipment:
            coords = item.get("coordinates", {})
            x = coords.get("x", 0)
            y = coords.get("y", 0)
            
            # Convert rink coords to ASCII coords
            ascii_x = int((x + 100) * ascii_width / 200)
            ascii_y = int((y + 42.5) * ascii_height / 85)
            
            # Clamp to grid bounds
            ascii_x = max(1, min(ascii_width-2, ascii_x))
            ascii_y = max(1, min(ascii_height-2, ascii_y))
            
            # Get equipment symbol based on type
            eq_type = item.get("type", "").lower()
            if "cone" in eq_type:
                symbol = 'C'
            elif "pylon" in eq_type:
                symbol = 'Y'
            elif "puck" in eq_type:
                symbol = 'o'
            elif "net" in eq_type and "goal" not in eq_type:  # Avoid conflict with goal nets
                symbol = 'N'
            else:
                symbol = 'E'  # Generic equipment
                
            # Only place if cell is empty (don't overwrite players/goals)
            if grid[ascii_y][ascii_x] == ' ':
                grid[ascii_y][ascii_x] = symbol
            
        # Convert grid to string
        ascii_art = '\n'.join([''.join(row) for row in grid])
        
        return {
            "format": "ascii",
            "preview": ascii_art,
            "legend": {
                "F": "Forward",
                "D": "Defense", 
                "G": "Goalie",
                "P": "Player",
                "C": "Cone",
                "Y": "Pylon", 
                "o": "Puck",
                "N": "Net",
                "E": "Equipment",
                "|": "Lines",
                "-": "Boards"
            }
        }
        
    elif format == "coordinates":
        # Generate coordinate list
        coord_list = []
        
        # List players
        players = spec.get("players", [])
        for player in players:
            coords = player.get("coordinates", {})
            coord_list.append({
                "type": "player",
                "position": player.get("position"),
                "team": player.get("team"),
                "x": coords.get("x"),
                "y": coords.get("y")
            })
            
        # List movements
        movements = spec.get("movements", [])
        for i, movement in enumerate(movements):
            from_pos = movement.get("from_pos", {})
            to_pos = movement.get("to_pos", {})
            coord_list.append({
                "type": "movement",
                "movement_type": movement.get("type"),
                "from": f"({from_pos.get('x')}, {from_pos.get('y')})",
                "to": f"({to_pos.get('x')}, {to_pos.get('y')})",
                "waypoints": movement.get("waypoints", [])
            })
            
        # List equipment
        equipment = spec.get("equipment", [])
        for item in equipment:
            coords = item.get("coordinates", {})
            coord_list.append({
                "type": "equipment",
                "equipment_type": item.get("type", "unknown"),
                "description": item.get("description", ""),
                "x": coords.get("x"),
                "y": coords.get("y")
            })
            
        return {
            "format": "coordinates",
            "total_elements": {
                "players": len(players),
                "movements": len(movements),
                "zones": len(spec.get("zones", [])),
                "annotations": len(spec.get("annotations", [])),
                "equipment": len(equipment)
            },
            "coordinates": coord_list,
            "rink_view": spec.get("rink", {}).get("view", "full")
        }
        
    else:
        return {
            "error": f"Unknown format: {format}",
            "available_formats": ["ascii", "coordinates"]
        }

# ============================================================================
# TOOL: GENERATE DIAGRAM
# ============================================================================

@mcp.tool("generate_diagram")
def generate_diagram(spec: Dict[str, Any], output_name: Optional[str] = None) -> Dict[str, Any]:
    """Generate the hockey diagram and save files.
    
    Args:
        spec: Complete validated diagram specification
        output_name: Optional name for output files
        
    Returns:
        Paths to generated files and success status
    """
    logger.info(f"🎨 [GENERATE] Creating diagram: {output_name or 'diagram'}")
    
    try:
        # Convert spec
        diagram_spec = dict_to_diagram_spec(spec)
        if not diagram_spec:
            return {
                "success": False,
                "error": "Failed to convert spec to diagram"
            }
        
        # Generate output paths
        if not output_name:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"diagram_{timestamp}"
        
        output_dir = Path(__file__).parent.parent / "outputs"
        output_dir.mkdir(exist_ok=True)
        png_path = output_dir / f"{output_name}.png"
        
        # Generate diagram
        builder = DiagramBuilder()
        result_path = builder.build(diagram_spec, str(png_path))
        
        # Save spec JSON (remove non-serializable conversation history)
        spec_path = output_dir / f"{output_name}.json"
        # Create a clean copy for saving
        clean_spec = {k: v for k, v in spec.items() if not k.startswith('_')}
        with open(spec_path, 'w') as f:
            json.dump(clean_spec, f, indent=2)
        
        return {
            "success": True,
            "image_path": str(png_path),
            "spec_path": str(spec_path),
            "element_count": {
                "players": len(spec.get("players", [])),
                "movements": len(spec.get("movements", [])),
                "zones": len(spec.get("zones", [])),
                "annotations": len(spec.get("annotations", []))
            }
        }
        
    except Exception as e:
        logger.error(f"Diagram generation error: {e}")
        import traceback
        tb = traceback.format_exc()
        return {
            "success": False,
            "error": f"Failed to generate diagram: {e}",
            "error_detail": tb
        }

# ============================================================================
# HEALTH CHECK
# ============================================================================

@mcp.tool("health_check")
def health_check() -> Dict[str, Any]:
    """
    Check health and status of the MCP server.
    
    Returns:
        Server health status and configuration
    """
    return {
        "status": "healthy",
        "server": "hockey-diagram-v3",
        "version": "3.0.2",
        "openai_configured": client is not None,
        "tools_available": [
            "analyze_hockey_query",
            "translate_analysis_to_spec",
            "health_check"
        ],
        "responses_api_info": {
            "status": "Ready for Responses API",
            "mcp_integration": "Exa MCP configured",
            "note": "When client.responses.create() is available, Exa searches will be automatic"
        }
    }

# ============================================================================
# SERVER INITIALIZATION
# ============================================================================

def main():
    """Main entry point for the Hockey Diagram MCP server v3."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Hockey Diagram MCP Server v3")
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio",
                       help="Transport mechanism (stdio or sse)")
    parser.add_argument("--host", default="localhost", help="Host for SSE transport")
    parser.add_argument("--port", type=int, default=8001, help="Port for SSE transport")
    
    args = parser.parse_args()
    
    if args.transport == "stdio":
        # Stdio mode for Claude Desktop
        async def run_stdio():
            from mcp.server.stdio import stdio_server
            async with stdio_server() as streams:
                await mcp.run(
                    streams[0], streams[1],
                    mcp.create_initialization_options()
                )
            
        logger.info("🏒 Starting Hockey Diagram MCP Server v3 (stdio mode)")
        logger.info("📊 Ready for OpenAI Responses API with Exa MCP")
        try:
            asyncio.run(run_stdio())
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
    else:
        # SSE/HTTP mode
        logger.info(f"🏒 Starting Hockey Diagram MCP Server v3 at http://{args.host}:{args.port}")
        logger.info("📊 Ready for OpenAI Responses API with Exa MCP")
        mcp.run(transport="sse", host=args.host, port=args.port)

if __name__ == "__main__":
    main()