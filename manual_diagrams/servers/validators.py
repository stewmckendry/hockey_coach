"""
Validation utilities for hockey diagrams.
"""

from typing import Dict, Any, List, Optional
import jsonschema
from diagram_schemas import NODE_SCHEMAS, DIAGRAM_SPEC_SCHEMA

def validate_node(node_type: str, node_data: Any) -> Dict[str, Any]:
    """Validate a single node against its schema."""
    if node_type not in NODE_SCHEMAS:
        return {
            "valid": False,
            "errors": [f"Unknown node type: {node_type}"]
        }
    
    schema = NODE_SCHEMAS[node_type]
    
    try:
        jsonschema.validate(instance=node_data, schema=schema)
        return {"valid": True, "errors": []}
    except jsonschema.ValidationError as e:
        return {
            "valid": False,
            "errors": [str(e.message)],
            "path": list(e.absolute_path)
        }

def validate_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Validate complete diagram specification."""
    try:
        jsonschema.validate(instance=spec, schema=DIAGRAM_SPEC_SCHEMA)
        
        # Additional hockey-specific validations
        issues = []
        
        # Check player count
        if "players" in spec:
            home_count = sum(1 for p in spec["players"] if p.get("team") == "home")
            visitor_count = sum(1 for p in spec["players"] if p.get("team") == "visitor")
            
            if home_count > 6:
                issues.append(f"Home team has {home_count} players (max 6)")
            if visitor_count > 6:
                issues.append(f"Visitor team has {visitor_count} players (max 6)")
        
        # Check puck possession
        if "players" in spec:
            puck_holders = [p for p in spec["players"] if p.get("has_puck")]
            if len(puck_holders) > 1:
                issues.append(f"Multiple players have puck: {[p.get('position', 'unknown') for p in puck_holders]}")
        
        return {
            "valid": len(issues) == 0,
            "errors": issues,
            "warnings": []
        }
        
    except jsonschema.ValidationError as e:
        return {
            "valid": False,
            "errors": [str(e.message)],
            "path": list(e.absolute_path)
        }

def check_spatial_conflicts(spec: Dict[str, Any]) -> List[str]:
    """Check for spatial conflicts in positioning."""
    conflicts = []
    
    if "players" not in spec:
        return conflicts
    
    players = spec["players"]
    
    # Rink boundaries and restricted zones
    RINK_WIDTH = 85.0  # Half-width (full width is 200, so +/-100 but leave buffer)
    RINK_HEIGHT = 40.0  # Half-height (full height is 85, so +/-42.5 but leave buffer)
    
    # Goal net dimensions and positions
    NET_WIDTH = 6.0  # Goal net is 6 feet wide
    NET_DEPTH = 4.0  # Goal net extends 4 feet from goal line
    GOAL_LINE_X = 89.0  # Goal line position
    
    # Goal net restricted areas (players shouldn't be inside nets)
    LEFT_NET_AREA = {
        "min_x": -GOAL_LINE_X - NET_DEPTH, "max_x": -GOAL_LINE_X,
        "min_y": -NET_WIDTH/2, "max_y": NET_WIDTH/2
    }
    RIGHT_NET_AREA = {
        "min_x": GOAL_LINE_X, "max_x": GOAL_LINE_X + NET_DEPTH,
        "min_y": -NET_WIDTH/2, "max_y": NET_WIDTH/2
    }
    
    # Check each player and equipment item
    all_entities = list(players)
    if "equipment" in spec:
        all_entities.extend(spec["equipment"])
    
    for i, entity in enumerate(all_entities):
        coords = entity.get("coordinates", {})
        if not coords:
            continue
            
        x, y = coords.get("x", 0), coords.get("y", 0)
        entity_name = entity.get("position", entity.get("id", f"entity_{i}"))
        
        # 1. Check rink boundaries
        if abs(x) > RINK_WIDTH:
            conflicts.append(f"{entity_name} out of rink bounds (x={x:.1f}, limit=±{RINK_WIDTH})")
        if abs(y) > RINK_HEIGHT:
            conflicts.append(f"{entity_name} out of rink bounds (y={y:.1f}, limit=±{RINK_HEIGHT})")
        
        # 2. Check goal net overlap (unless it's a goalie)
        entity_type = entity.get("type", "")
        if entity_type != "goalie":  # Goalies are allowed in net area
            # Check left net
            if (LEFT_NET_AREA["min_x"] <= x <= LEFT_NET_AREA["max_x"] and 
                LEFT_NET_AREA["min_y"] <= y <= LEFT_NET_AREA["max_y"]):
                conflicts.append(f"{entity_name} overlapping with left goal net (x={x:.1f}, y={y:.1f})")
            
            # Check right net
            if (RIGHT_NET_AREA["min_x"] <= x <= RIGHT_NET_AREA["max_x"] and 
                RIGHT_NET_AREA["min_y"] <= y <= RIGHT_NET_AREA["max_y"]):
                conflicts.append(f"{entity_name} overlapping with right goal net (x={x:.1f}, y={y:.1f})")
        
        # 3. Check board proximity (too close to boards can look unrealistic)
        BOARD_BUFFER = 3.0  # Minimum distance from boards
        if abs(y) > RINK_HEIGHT - BOARD_BUFFER:
            conflicts.append(f"{entity_name} too close to side boards (y={y:.1f}, min distance={BOARD_BUFFER})")
        if abs(x) > RINK_WIDTH - BOARD_BUFFER:
            conflicts.append(f"{entity_name} too close to end boards (x={x:.1f}, min distance={BOARD_BUFFER})")
    
    # 4. Check for overlapping players (original logic)
    for i, p1 in enumerate(players):
        for p2 in players[i+1:]:
            coords1 = p1.get("coordinates", {})
            coords2 = p2.get("coordinates", {})
            
            if not coords1 or not coords2:
                continue
                
            dist = ((coords1.get("x", 0) - coords2.get("x", 0))**2 + 
                   (coords1.get("y", 0) - coords2.get("y", 0))**2)**0.5
            
            if dist < 5:  # Minimum spacing between players
                conflicts.append(
                    f"Players {p1.get('position', f'player_{i}')} and {p2.get('position', f'player_{i+1}')} too close ({dist:.1f} units)"
                )
    
    # 5. Check equipment placement conflicts
    if "equipment" in spec:
        equipment = spec["equipment"]
        for i, eq1 in enumerate(equipment):
            for eq2 in equipment[i+1:]:
                coords1 = eq1.get("coordinates", {})
                coords2 = eq2.get("coordinates", {})
                
                if not coords1 or not coords2:
                    continue
                    
                dist = ((coords1.get("x", 0) - coords2.get("x", 0))**2 + 
                       (coords1.get("y", 0) - coords2.get("y", 0))**2)**0.5
                
                if dist < 3:  # Minimum spacing between equipment
                    conflicts.append(
                        f"Equipment {eq1.get('id', f'eq_{i}')} and {eq2.get('id', f'eq_{i+1}')} too close ({dist:.1f} units)"
                    )
    
    return conflicts