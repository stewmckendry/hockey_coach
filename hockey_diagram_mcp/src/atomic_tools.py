"""
Atomic tools for hockey diagram generation pipeline.
Each tool does ONE thing well and can be validated independently.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
import json

# ============================================================================
# TOOL 1: ANALYZE QUERY GAPS
# ============================================================================

def analyze_query_gaps(query: str) -> Dict[str, Any]:
    """
    Analyzes a hockey drill query to identify what information is provided 
    and what is missing but needed for diagram generation.
    
    Args:
        query: Natural language drill description
        
    Returns:
        Dictionary with explicit info, missing info, and questions
    """
    
    # Initialize result structure
    result = {
        "original_query": query,
        "explicit": {},
        "missing": {},
        "questions": [],
        "confidence": 1.0
    }
    
    # Parse drill notation (2v1, 3v2, etc.)
    drill_pattern = r'(\d+)v(\d+)'
    drill_match = re.search(drill_pattern, query.lower())
    if drill_match:
        result["explicit"]["offensive_count"] = int(drill_match.group(1))
        result["explicit"]["defensive_count"] = int(drill_match.group(2))
        result["explicit"]["drill_notation"] = drill_match.group(0)
    
    # Detect drill types
    drill_types = {
        "rush": ["rush", "attack", "counter"],
        "breakout": ["breakout", "break out", "exit"],
        "cycle": ["cycle", "cycling"],
        "give_and_go": ["give and go", "give-and-go", "give & go"],
        "power_play": ["power play", "pp", "powerplay", "man advantage"],
        "penalty_kill": ["penalty kill", "pk", "short handed"],
        "faceoff": ["faceoff", "face-off", "draw"],
        "transition": ["transition", "regroup", "neutral zone"]
    }
    
    for drill_type, keywords in drill_types.items():
        if any(keyword in query.lower() for keyword in keywords):
            result["explicit"]["drill_type"] = drill_type
            break
    
    # Detect zones mentioned
    zones_mentioned = []
    if any(z in query.lower() for z in ["offensive zone", "o-zone", "attacking zone"]):
        zones_mentioned.append("offensive")
    if any(z in query.lower() for z in ["defensive zone", "d-zone", "defending zone"]):
        zones_mentioned.append("defensive")
    if any(z in query.lower() for z in ["neutral zone", "center ice", "red line"]):
        zones_mentioned.append("neutral")
    
    if zones_mentioned:
        result["explicit"]["zones_mentioned"] = zones_mentioned
    
    # Detect specific positions mentioned
    position_patterns = {
        "left_dot": ["left dot", "left faceoff", "left circle"],
        "right_dot": ["right dot", "right faceoff", "right circle"],
        "slot": ["slot", "high slot", "low slot"],
        "point": ["point", "blue line", "at the point"],
        "corner": ["corner", "behind the net", "below goal line"],
        "net_front": ["net front", "in front", "crease", "front of net"]
    }
    
    positions_found = []
    for pos_name, patterns in position_patterns.items():
        if any(p in query.lower() for p in patterns):
            positions_found.append(pos_name)
    
    if positions_found:
        result["explicit"]["positions_mentioned"] = positions_found
    
    # Detect movements/actions
    movements = []
    movement_keywords = {
        "pass": ["pass", "passes", "passing", "dish", "feed"],
        "shot": ["shot", "shoot", "shoots", "shooting", "one-timer"],
        "skate": ["skate", "drive", "rush", "attack", "move"],
        "cycle": ["cycle", "cycling", "work the boards"],
        "screen": ["screen", "screening", "net front"],
        "forecheck": ["forecheck", "pressure", "force"],
        "backcheck": ["backcheck", "track back", "defensive coverage"]
    }
    
    for movement_type, keywords in movement_keywords.items():
        if any(k in query.lower() for k in keywords):
            movements.append(movement_type)
    
    if movements:
        result["explicit"]["movements"] = movements
    
    # Detect specific players mentioned (F1, F2, D1, etc.)
    player_pattern = r'[FDG]\d+'
    players_mentioned = re.findall(player_pattern, query.upper())
    if players_mentioned:
        result["explicit"]["players_mentioned"] = players_mentioned
    
    # Identify what's missing
    missing = {}
    questions = []
    
    # Check if we know how many players
    if "offensive_count" not in result["explicit"] and "players_mentioned" not in result["explicit"]:
        missing["player_count"] = None
        questions.append("How many players are involved in this drill?")
    
    # Check if we know starting zone
    if "zones_mentioned" not in result["explicit"]:
        missing["starting_zone"] = None
        if result["explicit"].get("drill_type") == "rush":
            questions.append("Where does the rush start? (typically neutral zone)")
        elif result["explicit"].get("drill_type") == "breakout":
            questions.append("Starting from defensive zone for the breakout?")
        else:
            questions.append("Which zone does the drill start in?")
    
    # Check if we know rink view preference
    missing["rink_view"] = None
    if len(result["explicit"].get("zones_mentioned", [])) > 1:
        questions.append("Should we show the full rink or focus on specific zones?")
    else:
        questions.append("What rink view would best show this drill? (full/half/zone)")
    
    # Check if goalie should be shown
    if "shot" in result["explicit"].get("movements", []):
        missing["show_goalie"] = None
        questions.append("Should the goalie be shown in the diagram?")
    
    # Check for equipment needs
    missing["equipment"] = None
    questions.append("Any special equipment needed? (cones, pucks, etc.)")
    
    # Check movement patterns
    if result["explicit"].get("drill_type") == "rush" and "movements" not in result["explicit"]:
        missing["movement_pattern"] = None
        questions.append("What's the rush pattern? (wide, middle, cross-ice)")
    
    # Calculate confidence based on how much is explicit
    explicit_count = len(result["explicit"])
    missing_count = len(missing)
    total = explicit_count + missing_count
    result["confidence"] = explicit_count / total if total > 0 else 0.5
    
    result["missing"] = missing
    result["questions"] = questions
    
    return result


# ============================================================================
# TOOL 2: GENERATE ASSUMPTIONS
# ============================================================================

def generate_assumptions(gaps_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates smart assumptions for missing information based on hockey knowledge.
    
    Args:
        gaps_analysis: Output from analyze_query_gaps
        
    Returns:
        Dictionary with assumptions and enriched query
    """
    
    result = {
        "original_query": gaps_analysis["original_query"],
        "assumptions": {},
        "enriched_query": "",
        "reasoning": {}
    }
    
    explicit = gaps_analysis["explicit"]
    missing = gaps_analysis["missing"]
    
    # Generate assumptions for each missing element
    
    # Player count assumptions
    if "player_count" in missing:
        if explicit.get("drill_type") == "give_and_go":
            result["assumptions"]["offensive_count"] = 2
            result["assumptions"]["defensive_count"] = 1
            result["reasoning"]["player_count"] = "Give and go typically involves 2 offensive players and 1 defender"
        elif explicit.get("drill_type") == "power_play":
            result["assumptions"]["offensive_count"] = 5
            result["assumptions"]["defensive_count"] = 4
            result["reasoning"]["player_count"] = "Power play is 5v4 situation"
        else:
            # Default to small group drill
            result["assumptions"]["offensive_count"] = 2
            result["assumptions"]["defensive_count"] = 1
            result["reasoning"]["player_count"] = "Defaulting to 2v1 for unspecified drill"
    
    # Starting zone assumptions
    if "starting_zone" in missing:
        drill_type = explicit.get("drill_type")
        if drill_type == "rush":
            result["assumptions"]["starting_zone"] = "neutral"
            result["reasoning"]["starting_zone"] = "Rushes typically start from neutral zone"
        elif drill_type == "breakout":
            result["assumptions"]["starting_zone"] = "defensive"
            result["reasoning"]["starting_zone"] = "Breakouts start from defensive zone"
        elif drill_type == "cycle":
            result["assumptions"]["starting_zone"] = "offensive"
            result["reasoning"]["starting_zone"] = "Cycling happens in offensive zone"
        elif drill_type == "power_play":
            result["assumptions"]["starting_zone"] = "offensive"
            result["reasoning"]["starting_zone"] = "Power play setup in offensive zone"
        else:
            zones = explicit.get("zones_mentioned", [])
            if zones:
                result["assumptions"]["starting_zone"] = zones[0]
                result["reasoning"]["starting_zone"] = f"Using first mentioned zone: {zones[0]}"
            else:
                result["assumptions"]["starting_zone"] = "neutral"
                result["reasoning"]["starting_zone"] = "Defaulting to neutral zone for flexibility"
    
    # Rink view assumptions
    if "rink_view" in missing:
        zones_mentioned = explicit.get("zones_mentioned", [])
        drill_type = explicit.get("drill_type")
        
        if len(zones_mentioned) > 1 or drill_type in ["rush", "transition", "breakout"]:
            result["assumptions"]["rink_view"] = "full"
            result["reasoning"]["rink_view"] = "Multiple zones or transition play needs full rink view"
        elif "offensive" in zones_mentioned or drill_type in ["cycle", "power_play"]:
            result["assumptions"]["rink_view"] = "offensive"
            result["reasoning"]["rink_view"] = "Focus on offensive zone action"
        elif "defensive" in zones_mentioned:
            result["assumptions"]["rink_view"] = "defensive"
            result["reasoning"]["rink_view"] = "Focus on defensive zone action"
        else:
            result["assumptions"]["rink_view"] = "full"
            result["reasoning"]["rink_view"] = "Full rink provides most flexibility"
    
    # Goalie assumptions
    if "show_goalie" in missing:
        if "shot" in explicit.get("movements", []):
            result["assumptions"]["show_goalie"] = True
            result["reasoning"]["show_goalie"] = "Including goalie since drill involves shooting"
        elif explicit.get("drill_type") in ["rush", "power_play"]:
            result["assumptions"]["show_goalie"] = True
            result["reasoning"]["show_goalie"] = f"{explicit.get('drill_type')} drills typically include goalie"
        else:
            result["assumptions"]["show_goalie"] = False
            result["reasoning"]["show_goalie"] = "No shooting mentioned, goalie not needed"
    
    # Equipment assumptions
    if "equipment" in missing:
        result["assumptions"]["equipment"] = ["pucks"]
        result["reasoning"]["equipment"] = "Standard drill uses pucks, no special equipment mentioned"
    
    # Movement pattern assumptions
    if "movement_pattern" in missing and explicit.get("drill_type") == "rush":
        offensive_count = explicit.get("offensive_count") or result["assumptions"].get("offensive_count", 2)
        if offensive_count == 2:
            result["assumptions"]["movement_pattern"] = "wide_lanes"
            result["reasoning"]["movement_pattern"] = "2-player rush typically uses wide lanes"
        elif offensive_count == 3:
            result["assumptions"]["movement_pattern"] = "triangle"
            result["reasoning"]["movement_pattern"] = "3-player rush uses triangle formation"
        else:
            result["assumptions"]["movement_pattern"] = "standard"
            result["reasoning"]["movement_pattern"] = "Standard rush pattern"
    
    # Add default movements if none specified
    if "movements" not in explicit:
        drill_type = explicit.get("drill_type")
        if drill_type == "rush":
            result["assumptions"]["movements"] = ["skate", "pass", "shot"]
            result["reasoning"]["movements"] = "Rush typically includes skating, passing, and shooting"
        elif drill_type == "cycle":
            result["assumptions"]["movements"] = ["skate", "pass", "cycle"]
            result["reasoning"]["movements"] = "Cycling drill includes skating and passing along boards"
        elif drill_type == "give_and_go":
            result["assumptions"]["movements"] = ["pass", "skate", "pass", "shot"]
            result["reasoning"]["movements"] = "Give and go: pass, skate to space, receive pass back, shoot"
        else:
            result["assumptions"]["movements"] = ["skate", "pass"]
            result["reasoning"]["movements"] = "Basic drill movements"
    
    # Build enriched query
    enriched_parts = [gaps_analysis["original_query"]]
    
    # Add assumed details
    assumptions_text = []
    if result["assumptions"].get("starting_zone"):
        assumptions_text.append(f"Starting in {result['assumptions']['starting_zone']} zone")
    if result["assumptions"].get("rink_view"):
        assumptions_text.append(f"Using {result['assumptions']['rink_view']} rink view")
    if result["assumptions"].get("show_goalie"):
        assumptions_text.append("Including goalie")
    if result["assumptions"].get("movement_pattern"):
        assumptions_text.append(f"Using {result['assumptions']['movement_pattern']} pattern")
    
    if assumptions_text:
        enriched_parts.append(f"[Assumed: {', '.join(assumptions_text)}]")
    
    result["enriched_query"] = " ".join(enriched_parts)
    
    return result


# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_gap_analysis():
    """Test the analyze_query_gaps function with our test queries."""
    from test_queries import TEST_QUERIES
    
    print("=" * 80)
    print("TESTING: analyze_query_gaps")
    print("=" * 80)
    
    for test_query in TEST_QUERIES:
        print(f"\nTest: {test_query['id']}")
        print(f"Query: {test_query['query']}")
        print("-" * 40)
        
        result = analyze_query_gaps(test_query['query'])
        
        print(f"Explicit info found:")
        for key, value in result['explicit'].items():
            print(f"  - {key}: {value}")
        
        print(f"Missing info:")
        for key in result['missing'].keys():
            print(f"  - {key}")
        
        print(f"Questions to clarify:")
        for q in result['questions']:
            print(f"  ? {q}")
        
        print(f"Confidence: {result['confidence']:.2f}")
        print()


def test_assumptions():
    """Test the generate_assumptions function with our test queries."""
    from test_queries import TEST_QUERIES
    
    print("=" * 80)
    print("TESTING: generate_assumptions")
    print("=" * 80)
    
    for test_query in TEST_QUERIES[:3]:  # Test first 3 queries
        print(f"\nTest: {test_query['id']}")
        print(f"Query: {test_query['query']}")
        print("-" * 40)
        
        # First analyze gaps
        gaps = analyze_query_gaps(test_query['query'])
        
        # Then generate assumptions
        result = generate_assumptions(gaps)
        
        print(f"Assumptions made:")
        for key, value in result['assumptions'].items():
            reason = result['reasoning'].get(key, "No reason provided")
            print(f"  - {key}: {value}")
            print(f"    Reason: {reason}")
        
        print(f"\nEnriched query:")
        print(f"  {result['enriched_query']}")
        print()


if __name__ == "__main__":
    # Run tests
    test_gap_analysis()
    print("\n" + "=" * 80 + "\n")
    test_assumptions()