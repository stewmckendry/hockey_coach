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
    
    # Check for overlapping players
    for i, p1 in enumerate(players):
        for p2 in players[i+1:]:
            coords1 = p1.get("coordinates", {})
            coords2 = p2.get("coordinates", {})
            
            if not coords1 or not coords2:
                continue
                
            dist = ((coords1.get("x", 0) - coords2.get("x", 0))**2 + 
                   (coords1.get("y", 0) - coords2.get("y", 0))**2)**0.5
            
            if dist < 5:  # Minimum spacing
                conflicts.append(
                    f"Players {p1.get('position', f'player_{i}')} and {p2.get('position', f'player_{i+1}')} too close ({dist:.1f} units)"
                )
    
    return conflicts