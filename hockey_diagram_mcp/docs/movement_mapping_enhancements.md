# Movement Mapping Enhancement Recommendations

## Current Limitations

1. **No LLM Fallback**: Unlike `map_position_to_coordinates`, this tool lacks LLM-based interpretation for complex movement descriptions
2. **Fixed Pattern Detection**: Auto-detection uses rigid rules without context awareness
3. **Limited Movement Vocabulary**: Doesn't understand hockey-specific terms like "rim", "chip", "sauce", "dump", "stretch pass"
4. **No Zone Awareness**: Doesn't adjust patterns based on offensive/defensive/neutral zone context
5. **Missing Reference Movements**: Can't handle relative movements like "same path as F1" or "mirror of previous movement"

## Proposed Enhancements

### 1. Add LLM-Based Movement Interpretation
```python
def map_movement_to_coordinates(...):
    # After basic position mapping, add LLM interpretation for complex patterns
    if pattern == "auto" and client:
        prompt = f"""
        Hockey movement: {movement_type} from "{from_position}" to "{to_position}"
        Zone: {zone}
        
        Common patterns:
        - Rim: Along boards behind net
        - Dump: High glass/boards from neutral zone
        - Stretch pass: Long outlet pass through neutral zone
        - Sauce: Over stick/player (add arc waypoint)
        - Chip: Quick advance past defender
        - Wrap around: Behind net to opposite side
        
        Suggest pattern and waypoints.
        Format: pattern|waypoint1_x,waypoint1_y|waypoint2_x,waypoint2_y
        """
        # Use LLM to interpret movement pattern
```

### 2. Zone-Aware Pattern Selection
```python
# Adjust patterns based on zone context
if zone == "defensive":
    pattern_map = {
        "breakout": ["along_boards", "up_middle", "reverse"],
        "clear": ["hard_around", "soft_chip", "up_ice"],
        "outlet": ["stretch", "bank", "direct"]
    }
elif zone == "neutral":
    pattern_map = {
        "entry": ["carry_wide", "drop_pass", "chip_and_chase"],
        "regroup": ["button_hook", "swing", "reverse"]
    }
elif zone == "offensive":
    pattern_map = {
        "cycle": ["low_to_high", "corner_work", "behind_net"],
        "setup": ["half_wall", "point", "backdoor"]
    }
```

### 3. Movement Pattern Library
```python
MOVEMENT_PATTERNS = {
    "rim": {
        "description": "Puck along boards behind net",
        "waypoint_formula": lambda from_pos, to_pos: [
            [89 * sign(from_pos[0]), from_pos[1]],  # To end boards
            [89 * sign(from_pos[0]), 0],  # Behind net
            [89 * sign(to_pos[0]), to_pos[1]]  # Out other side
        ]
    },
    "button_hook": {
        "description": "Curl back to maintain possession",
        "waypoint_formula": lambda from_pos, to_pos: [
            [from_pos[0] + 10, from_pos[1]],  # Forward
            [from_pos[0] + 8, from_pos[1] - 8],  # Start curl
            [from_pos[0], from_pos[1] - 10],  # Complete curl
            [to_pos[0], to_pos[1]]  # Continue
        ]
    },
    "bank_pass": {
        "description": "Off boards to teammate",
        "waypoint_formula": lambda from_pos, to_pos: [
            [from_pos[0], 40 * sign(from_pos[1])],  # To boards
            [to_pos[0], to_pos[1]]  # To target
        ]
    }
}
```

### 4. Relative Movement Support
```python
def map_movement_to_coordinates(
    from_position: str,
    to_position: str,
    movement_type: str = "skate",
    pattern: Optional[str] = "auto",
    zone: Optional[str] = "offensive",
    reference_movements: Optional[Dict] = None,  # NEW
    session_id: Optional[str] = None
):
    # Handle relative movements
    if "same as" in pattern or "mirror" in pattern:
        # Extract reference movement and apply transformation
        ref_name = extract_reference(pattern)
        if ref_name in reference_movements:
            base_movement = reference_movements[ref_name]
            # Apply transformation (mirror, offset, etc.)
```

### 5. Movement Validation
```python
def validate_movement_physics(movement_spec: Dict) -> Dict:
    """Validate movement is physically possible"""
    
    # Check speed/distance ratio
    distance = calculate_distance(movement_spec)
    movement_type = movement_spec["type"]
    
    if movement_type == "skate" and distance > 100:
        return {"warning": "Very long skating path - consider breaking into segments"}
    
    if movement_type == "pass" and len(movement_spec.get("waypoints", [])) > 2:
        return {"warning": "Passes typically don't have complex paths"}
    
    # Check for impossible angles
    if movement_type == "shot":
        angle = calculate_shot_angle(movement_spec)
        if angle > 120:
            return {"warning": "Shot angle very wide - consider adjusting"}
```

### 6. Context-Aware Waypoint Generation
```python
def calculate_waypoints_enhanced(
    from_pos: Tuple, 
    to_pos: Tuple,
    pattern: str,
    zone: str,
    obstacles: Optional[List[Tuple]] = None
) -> List[List[float]]:
    """Generate waypoints considering zone and obstacles"""
    
    # Avoid collisions with other players
    if obstacles:
        waypoints = avoid_obstacles(from_pos, to_pos, obstacles)
    
    # Adjust for zone boundaries
    if crosses_blue_line(from_pos, to_pos):
        # Add waypoint at blue line for zone entry
        waypoints.append([25 * sign(to_pos[0]), interpolate_y()])
    
    # Smooth paths near boards
    if near_boards(from_pos) or near_boards(to_pos):
        # Add buffer waypoints to show proper angles
```

## Implementation Priority

1. **High Priority**: LLM fallback for complex movement descriptions (similar to position mapping)
2. **High Priority**: Expand movement pattern library with hockey-specific patterns
3. **Medium Priority**: Zone-aware pattern selection
4. **Medium Priority**: Movement validation for physics/rules
5. **Low Priority**: Relative movement support
6. **Low Priority**: Obstacle avoidance in waypoint generation

## Testing Requirements

- Test all new patterns with actual diagram generation
- Verify waypoints create smooth, realistic paths
- Ensure LLM integration doesn't slow down simple movements
- Validate zone transitions and boundary handling
- Test with complex drill sequences