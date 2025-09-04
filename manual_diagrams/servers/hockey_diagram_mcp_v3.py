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
                    "require_approval": "never"
                })
            
            # Prepare the Responses API request with proper attributes
            api_request = {
                "model": model_config.get("model", "gpt-4o-mini"),
                "tools": tools,
                "input": prompt,  # User message/prompt
                "instructions": system_prompt,  # System-level instructions (separate from user prompt)
                "max_output_tokens": model_config.get("max_tokens", 2000),
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
                                        "situation": {"type": "string"},
                                        "zone": {"type": "string"},
                                        "key_actions": {"type": "array", "items": {"type": "string"}},
                                        "faceoff_location": {"type": "string"}
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
            if hasattr(response, 'output_text'):
                output_text = response.output_text
                logger.info(f"SDK output_text: {output_text[:200] if output_text else 'None/Empty'}")
            else:
                # Fallback: manually extract from output array
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
                    
                    # If still no text, check the last item
                    if not output_text and response.output:
                        last_item = response.output[-1]
                        logger.info(f"Checking last item: {getattr(last_item, 'type', type(last_item).__name__)}")
                        if hasattr(last_item, 'output'):
                            output_text = str(last_item.output)
                            logger.info(f"Found output in last item: {output_text[:100]}")
                        elif hasattr(last_item, 'result'):
                            output_text = str(last_item.result)
                            logger.info(f"Found result in last item: {output_text[:100]}")
            
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
            
            # Log MCP tool calls if any were made
            mcp_calls = []
            # Check in the output message content for tool calls
            if hasattr(response, 'output') and response.output:
                for message in response.output:
                    if hasattr(message, 'content') and message.content:
                        for content_item in message.content:
                            if hasattr(content_item, 'type') and 'tool' in content_item.type.lower():
                                mcp_call_info = {
                                    "type": content_item.type,
                                    "details": str(content_item)[:200]  # First 200 chars
                                }
                                mcp_calls.append(mcp_call_info)
                                logger.info(f"🔍 Tool call detected: {content_item.type}")
            
            if mcp_calls:
                logger.info(f"✅ Made {len(mcp_calls)} MCP tool calls")
            else:
                logger.info("ℹ️ No MCP tools were called")
            
            # Parse JSON from the output
            # The output should be JSON based on our prompt instructions
            import re
            
            # Log the raw output for debugging
            logger.info(f"Raw output length: {len(output_text)}")
            if len(output_text) < 500:
                logger.info(f"Raw output: {output_text}")
            
            json_match = re.search(r'\{.*\}', output_text, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                except json.JSONDecodeError as e:
                    result = {
                        "raw_output": output_text[:1000], 
                        "parse_error": f"JSON decode error: {str(e)}",
                        "json_attempt": json_match.group()[:500]
                    }
            else:
                result = {
                    "raw_output": output_text[:1000], 
                    "parse_error": "Could not extract JSON from response"
                }
            
            result["api_used"] = "responses"
            result["exa_available"] = True
            result["mcp_calls"] = mcp_calls
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
# TEST TOOL
# ============================================================================

@mcp.tool("test_analyze_query")
def test_analyze_query() -> Dict[str, Any]:
    """
    Test the analyze_hockey_query tool with the standard faceoff example.
    
    Returns:
        Test results showing the analysis output
    """
    
    query = "build a hockey diagram of an offensive zone faceoff. The play is to bump the puck back and the weak side winger swings over to grab puck and take a shot."
    
    clarifications = {
        "faceoff_location": "right dot",
        "show_opposing": "all players",
        "shot_location": "from slot"
    }
    
    logger.info(f"Testing with query: {query}")
    logger.info(f"Clarifications: {clarifications}")
    
    result = analyze_hockey_query(query, clarifications)
    
    if "error" not in result:
        return {
            "success": True,
            "query": query,
            "clarifications": clarifications,
            "player_count": len(result.get("components_with_assumptions", {}).get("players", [])),
            "movement_count": len(result.get("components_with_assumptions", {}).get("movements", [])),
            "mcp_tools": result.get("mcp_tools_configured", []),
            "full_result": result
        }
    else:
        return {
            "success": False,
            "error": result.get("error"),
            "query": query
        }

# ============================================================================
# TOOL 2: TRANSLATE ANALYSIS TO SPEC
# ============================================================================

@mcp.tool("translate_analysis_to_spec")
def translate_analysis_to_spec(
    analysis: Dict[str, Any],
    title: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Translate analyzed hockey query output to complete diagram specification.
    
    This tool systematically converts the natural language positions and movements
    from the analysis into precise coordinates and a valid diagram spec structure.
    
    Args:
        analysis: The full output from analyze_hockey_query tool
        title: Optional title for the diagram (defaults to query)
        description: Optional description for the diagram
        
    Returns:
        Complete diagram specification ready for validation and generation
    """
    logger.info("📐 Translating analysis to diagram spec")
    
    # Extract components from analysis
    components = analysis.get("components_with_assumptions", {})
    rink_info = components.get("rink", {})
    players_info = components.get("players", [])
    movements_info = components.get("movements", [])
    zones_info = components.get("zones", [])
    annotations_info = components.get("annotations", [])
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
    
    # Add annotations if present
    if annotations_info:
        spec["annotations"] = []
        for ann in annotations_info:
            spec["annotations"].append({
                "text": ann.get("text", ""),
                "position": {"x": 0, "y": 50},  # Default position, can be refined
                "anchor": "middle"
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
        
        # Get mapped positions from LLM
        mapping_result = map_positions_with_llm(players_for_mapping, zone)
        
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
            if movement.get("type") == "pass" and movement.get("to_player"):
                movement_data["target_player_id"] = movement["to_player"]
            
            movements_for_mapping.append(movement_data)
        
        # Map movements using LLM with spatial awareness
        movement_mapping_result = map_movements_with_llm(
            movements_for_mapping,
            spec["players"],  # Pass mapped players for position context
            spec["rink"]["view"]
        )
        
        # Process mapped movements
        if "movements_mapped" in movement_mapping_result:
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
        if "path_validation" in movement_mapping_result:
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
        if "questions_for_user" in movement_mapping_result:
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
    
    return {
        "success": True,
        "spec": spec,
        "translation_summary": {
            "players_mapped": len(spec["players"]),
            "movements_mapped": len(spec["movements"]),
            "rink_view": spec["rink"]["view"],
            "has_zones": len(spec.get("zones", [])) > 0,
            "has_annotations": len(spec.get("annotations", [])) > 0
        },
        "metadata": aggregated_metadata,
        "validation_summary": validation_summary,
        "notes": [
            "Spec generated from analysis - ready for validation",
            "Review metadata for confidence scores and questions",
            "Use validate_diagram_spec_full to check for issues",
            "Use generate_diagram to create the visual"
        ]
    }

def map_positions_with_llm(
    players: List[Dict[str, Any]], 
    rink_view: str = "offensive"
) -> Dict[str, Any]:
    """
    Map multiple player positions using LLM with spatial awareness.
    Uses OpenAI Responses API for native function calling.
    
    Args:
        players: List of player dictionaries with position descriptions
        rink_view: The rink view context
    
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
    
    # Add tool instructions
    prompt += "\n\n" + position_prompt_config["tool_instructions"]
    
    # Define the zone tools
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
        input_list = [
            {"role": "system", "content": position_prompt_config["system_prompt"]},
            {"role": "user", "content": prompt}
        ]
        
        # Use Responses API with native function calling
        response = client.responses.create(
            model=model_config.get("model", "gpt-4o-mini"),
            instructions=position_prompt_config["system_prompt"],
            tools=tools,
            tool_choice="auto",  # Let model decide if tools are needed
            input=input_list,
            max_output_tokens=model_config.get("max_tokens", 2000),
            temperature=model_config.get("temperature", 0.2)
        )
        
        # Check if there were function calls
        function_calls_made = False
        result_text = None
        
        # Check the output
        for item in response.output:
            if item.type == "function_call":
                function_calls_made = True
                # We need to execute the function and make another call
                break
        
        if not function_calls_made:
            # No function calls, should have the answer directly
            result_text = response.output_text
            logger.info(f"Got direct response: {result_text[:100] if result_text else 'None'}")
        else:
            # Has function calls - need to execute them and call again
            logger.info("Response contains function calls, executing them...")
            
            # Add the response output to input list
            input_list += response.output
            
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
                        
                    elif item.name == "get_zone_boundaries":
                        args = json.loads(item.arguments)
                        boundaries = get_zone_boundaries(args["view"], args["zone"])
                        
                        input_list.append({
                            "type": "function_call_output",
                            "call_id": item.call_id,
                            "output": json.dumps(boundaries)
                        })
                        logger.info(f"🔧 Executed get_zone_boundaries({args['view']}, {args['zone']})")
            
            # Keep making calls until we get text output (not more function calls)
            max_rounds = 5  # Prevent infinite loops
            round_num = 2
            
            while round_num <= max_rounds:
                logger.info(f"Making call {round_num} with function results...")
                
                # Adjust instructions based on round number
                if round_num == 2:
                    follow_up_instructions = "You now have the zone information. Map each player to exact coordinates and return ONLY valid JSON."
                elif round_num >= 3:
                    follow_up_instructions = f"This is round {round_num}. You should have enough information now. Please provide the final JSON mapping immediately without requesting more zone boundaries."
                else:
                    follow_up_instructions = "Use the zone boundary information to map each player to exact coordinates. Return ONLY valid JSON."
                
                final_response = client.responses.create(
                    model=model_config.get("model", "gpt-4o-mini"),
                    instructions=follow_up_instructions,
                    tools=tools,
                    tool_choice="auto" if round_num < 4 else "none",  # Disable tools after round 3
                    input=input_list,
                    max_output_tokens=model_config.get("max_tokens", 2000),
                    temperature=model_config.get("temperature", 0.2)
                )
                
                # Check if we got text or more function calls
                has_function_calls = False
                result_text = final_response.output_text
                
                if not result_text and hasattr(final_response, 'output'):
                    # Log any reasoning from the model
                    if hasattr(final_response, 'reasoning') and final_response.reasoning:
                        logger.info(f"  Round {round_num} reasoning: {final_response.reasoning}")
                    
                    function_call_count = 0
                    for item in final_response.output:
                        if item.type == "function_call":
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
                            elif item.name == "list_available_zones":
                                args = json.loads(item.arguments) if item.arguments else {}
                                zones = list_available_zones(args.get("view"))
                                input_list.append({
                                    "type": "function_call_output",
                                    "call_id": item.call_id,
                                    "output": json.dumps(zones)
                                })
                                logger.info(f"  Round {round_num}: Executed list_available_zones({args.get('view', 'all')})")
                    
                    if has_function_calls:
                        logger.info(f"  Round {round_num}: Model made {function_call_count} more function calls")
                
                # Add the response to input for next round if needed
                if has_function_calls:
                    input_list += final_response.output
                    round_num += 1
                else:
                    # We got the final answer
                    logger.info(f"Got final answer in round {round_num}")
                    break
            
            if not result_text:
                logger.error(f"Failed to get text response after {max_rounds} rounds")
        
        # Debug: log what we got
        logger.debug(f"Raw result text: {result_text[:500] if result_text else 'None'}")
        
        # Parse the JSON response (handle markdown code blocks)
        try:
            # Extract JSON from markdown if present
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
            logger.info(f"✅ Mapped {len(result.get('players_mapped', []))} player positions")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {result_text[:500] if result_text else 'None'}")
            # Return a default structure
            result = {"players_mapped": [], "error": "Failed to parse LLM response"}
        
        return result
        
    except Exception as e:
        logger.error(f"Position mapping failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"error": str(e), "players_mapped": []}

def map_movements_with_llm(
    movements: List[Dict[str, Any]], 
    players: List[Dict[str, Any]],
    rink_view: str = "offensive"
) -> Dict[str, Any]:
    """
    Map movement descriptions to coordinate paths using LLM with spatial awareness.
    Uses OpenAI Responses API for native function calling.
    
    Args:
        movements: List of movement dictionaries with descriptions
        players: List of player dictionaries with positions (for start points)
        rink_view: The rink view context
    
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
        
        # Add destination player for passes
        if movement.get("type") == "pass" and movement.get("target_player_id"):
            target_pos = player_positions.get(movement["target_player_id"], {})
            movement_data["target_position"] = target_pos
            movement_data["target_player_id"] = movement["target_player_id"]
            movement_data["end_x"] = target_pos.get("x", 85)
            movement_data["end_y"] = target_pos.get("y", 0)
        elif movement.get("type") == "shot":
            # Shots always target the net
            movement_data["end_x"] = 89
            movement_data["end_y"] = 0
            
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
    
    # Create input list for Responses API
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
        
        # Call Responses API with native function calling
        logger.info("🏃 Mapping movements with LLM using spatial awareness...")
        response = client.responses.create(
            model=model_config.get("model", "gpt-4o-mini"),
            instructions=movement_prompt_config["system_prompt"],
            tools=tools,
            input=input_list,
            max_output_tokens=model_config.get("max_tokens", 2500),
            temperature=model_config.get("temperature", 0.2)
        )
        
        # Process response and handle function calls
        function_calls_made = 0
        final_output = None
        
        # Add the response output to input list
        input_list += response.output
        
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
                
                # Check if we got text or more function calls
                has_more_calls = False
                result_text = final_response.output_text if hasattr(final_response, 'output_text') else None
                
                # Log what we received
                logger.debug(f"Round {round_num} - output_text: {result_text[:50] if result_text else 'None'}")
                
                if not result_text and hasattr(final_response, 'output'):
                    logger.debug(f"Round {round_num} - output items: {len(final_response.output)}")
                    
                    for i, item in enumerate(final_response.output):
                        logger.debug(f"  Item {i}: type={item.type}")
                        
                        if item.type == "function_call":
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
                    
                    # Add response to input list
                    input_list += final_response.output
                
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
            return {"movements_mapped": [], "error": "No output from LLM"}
        
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
        
        return result
        
    except Exception as e:
        logger.error(f"Movement mapping failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"error": str(e), "movements_mapped": []}

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
            
        return {
            "format": "coordinates",
            "total_elements": {
                "players": len(players),
                "movements": len(movements),
                "zones": len(spec.get("zones", [])),
                "annotations": len(spec.get("annotations", []))
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
        
        # Save spec JSON
        spec_path = output_dir / f"{output_name}.json"
        with open(spec_path, 'w') as f:
            json.dump(spec, f, indent=2)
        
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
            "test_analyze_query",
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