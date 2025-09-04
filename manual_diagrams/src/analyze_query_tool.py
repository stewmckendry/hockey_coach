"""
Standalone version of the analyze_hockey_query MCP tool for testing.
This can be integrated into the MCP server once tested.
"""

import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_hockey_query(query: str, clarifications: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyzes a hockey drill query and extracts/enriches components needed for diagram spec.
    Uses LLM with hockey intelligence to fill gaps with educated assumptions.
    
    Args:
        query: Natural language drill/play description
        clarifications: Optional user answers to questions (e.g., {"faceoff_location": "right dot"})
        
    Returns:
        Analysis with explicit info, assumptions, and components aligned to spec sections
    """
    
    # Prepare clarifications text
    clarifications_text = ""
    if clarifications:
        clarifications_text = "\nUser clarifications provided:\n"
        for key, value in clarifications.items():
            clarifications_text += f"- {key}: {value}\n"
    
    # Create the analysis prompt
    prompt = f"""Analyze this hockey drill/play query and extract components needed for a diagram.
    
QUERY: "{query}"
{clarifications_text}

Your task is to analyze this query with hockey expertise and provide a structured JSON response.

For ANY hockey situation, you MUST:
1. Identify what's explicitly stated vs what needs to be assumed
2. Apply hockey knowledge to fill gaps (e.g., faceoffs need 11 players total)
3. Make educated assumptions with confidence levels
4. Generate questions for critical unknowns

Output a JSON object with this EXACT structure:
{{
    "original_query": "the original query",
    "explicit_info": {{
        "situation": "faceoff/drill/play/etc",
        "zone": "offensive/defensive/neutral if mentioned",
        "key_actions": ["list of mentioned actions"],
        "faceoff_location": "right dot/left dot if specified"
    }},
    "components_with_assumptions": {{
        "rink": {{
            "view": "offensive/defensive/full",
            "assumption": "reasoning for this choice",
            "confidence": 0.0-1.0
        }},
        "players": [
            {{
                "id": "C/LW/RW/LD/RD/OC/etc",
                "type": "center/winger/defense/goalie",
                "team": "home/away",
                "position_desc": "natural language position description",
                "assumption": "why this player is needed",
                "confidence": 0.0-1.0
            }}
            // Include ALL players needed for the situation
        ],
        "movements": [
            {{
                "id": "m1/m2/etc",
                "type": "pass/shot/skate/carry",
                "desc": "movement description",
                "from_player": "player ID",
                "to_area": "target area description",
                "assumption": "reasoning for this movement",
                "confidence": 0.0-1.0
            }}
        ],
        "zones": [],
        "annotations": [
            {{
                "text": "title or label text",
                "position_desc": "where to place it",
                "assumption": "why this annotation",
                "confidence": 0.0-1.0
            }}
        ],
        "equipment": []
    }},
    "questions_for_user": [
        {{
            "question": "question text",
            "key": "parameter_key",
            "options": ["option1", "option2"],
            "critical": true/false,
            "confidence": 0.0-1.0
        }}
    ],
    "metadata": {{
        "type": "drill/play",
        "phase": "offensive/defensive/neutral/transition",
        "key_players": ["list of key player IDs"]
    }}
}}

IMPORTANT HOCKEY KNOWLEDGE:
- Faceoffs require both teams: 5v5 plus goalie (11 total) for zone faceoffs
- "Weak side" for right dot = left wing, for left dot = right wing
- "Bump back" = faceoff win technique sending puck backward
- Offensive zone faceoffs: attacking team at points, defending team protecting net
- Always include goalie if there's a shot
- Standard positions: C, LW, RW, LD, RD for home; OC, OW1, OW2, OD1, OD2, G for away

Apply your hockey expertise to provide a complete, realistic analysis."""
    
    # Use LLM to analyze
    if not client:
        logger.warning("OpenAI client not available, returning basic analysis")
        return {
            "error": "OpenAI client not configured",
            "original_query": query,
            "suggestion": "Configure OPENAI_API_KEY to enable LLM analysis"
        }
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use gpt-4o-mini for better hockey understanding
            messages=[
                {"role": "system", "content": "You are a hockey coach and diagram expert. Analyze drills and plays with deep hockey knowledge."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.3,  # Lower temperature for consistent analysis
            response_format={"type": "json_object"}  # Ensure JSON response
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Apply any clarifications that weren't processed by LLM
        if clarifications:
            result["user_clarifications"] = clarifications
        
        # Log summary
        player_count = len(result.get("components_with_assumptions", {}).get("players", []))
        movement_count = len(result.get("components_with_assumptions", {}).get("movements", []))
        logger.info(f"🔍 Query analysis complete: {player_count} players, {movement_count} movements")
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        return {
            "error": "Failed to parse analysis response",
            "original_query": query,
            "raw_response": response.choices[0].message.content if response else None
        }
    except Exception as e:
        logger.error(f"Query analysis failed: {e}")
        return {
            "error": f"Analysis failed: {str(e)}",
            "original_query": query
        }


def test_tool():
    """Test the analyze_hockey_query tool with your specific query."""
    
    # Your test query
    query = "build a hockey diagram of an offensive zone faceoff. The play is to bump the puck back and the weak side winger swings over to grab puck and take a shot."
    
    # Your clarifications
    clarifications = {
        "faceoff_location": "right dot",
        "show_opposing": "all players",
        "shot_location": "from slot"
    }
    
    print("Testing analyze_hockey_query tool...")
    print(f"Query: {query}")
    print(f"Clarifications: {clarifications}")
    print("-" * 80)
    
    result = analyze_hockey_query(query, clarifications)
    
    print(json.dumps(result, indent=2))
    
    # Summary
    if "error" not in result:
        players = result.get("components_with_assumptions", {}).get("players", [])
        movements = result.get("components_with_assumptions", {}).get("movements", [])
        print(f"\nSummary:")
        print(f"- Players: {len(players)}")
        print(f"- Movements: {len(movements)}")
        print(f"- Rink view: {result.get('components_with_assumptions', {}).get('rink', {}).get('view')}")
        
        if players:
            print("\nPlayers identified:")
            for p in players:
                print(f"  - {p['id']} ({p['team']}): {p['position_desc']}")
        
        if movements:
            print("\nMovements identified:")
            for m in movements:
                print(f"  - {m['id']}: {m['desc']}")


if __name__ == "__main__":
    test_tool()