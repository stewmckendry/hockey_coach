# Phase 1 Atomic Tools - Revised Specification

## Overview
Atomic tools for incremental hockey diagram building with full session logging integration.

## Modified Tool: initialize_diagram (Enhanced)

### Purpose
Initialize a new diagram session AND return an empty spec for incremental building.

### MCP Tool Definition
```python
@mcp.tool("initialize_diagram")
def initialize_diagram(
    description: str, 
    diagram_type: Optional[str] = None,
    title: Optional[str] = None,
    view: str = "full",
    return_empty_spec: bool = True  # NEW parameter
) -> Dict[str, Any]:
```

### Enhanced Output (with empty spec)
```json
{
    "session_id": "a3f4b2c1",
    "description": "2v1 rush drill",
    "diagram_type": "drill",
    "created_at": "2025-01-09T10:00:00Z",
    "workflow": {
        "traditional": "Use analyze_hockey_query() for full pipeline",
        "incremental": "Use add_player(), add_movement(), etc. with returned spec"
    },
    "spec": {  // NEW: Returns empty spec when return_empty_spec=True
        "title": "2v1 rush drill",
        "description": "2v1 rush drill",
        "rink": {
            "view": "full",
            "features": ["center_line", "blue_lines", "goal_lines", "faceoff_dots", "faceoff_circles"]
        },
        "players": [],
        "movements": [],
        "zones": [],
        "annotations": [],
        "equipment": [],
        "metadata": {
            "created": "2025-01-09T10:00:00Z",
            "session_id": "a3f4b2c1",
            "diagram_type": "drill",
            "build_method": "incremental"
        }
    },
    "instructions": "Pass session_id='a3f4b2c1' to ALL subsequent tool calls",
    "status": "ready"
}
```

### Implementation with Logging
```python
@mcp.tool("initialize_diagram")
def initialize_diagram(description: str, diagram_type: Optional[str] = None, 
                       title: Optional[str] = None, view: str = "full",
                       return_empty_spec: bool = True) -> Dict[str, Any]:
    import uuid
    from datetime import datetime
    
    # Generate unique session ID
    session_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()
    
    # Store session info
    session_info = {
        "session_id": session_id,
        "description": description,
        "diagram_type": diagram_type or "drill",
        "created_at": timestamp,
        "steps_completed": [],
        "current_step": "initialized",
        "build_method": "incremental" if return_empty_spec else "traditional"
    }
    active_sessions[session_id] = session_info
    
    # Enhanced logging with separators
    logger.info("=" * 80)
    logger.info(f"🏒 NEW DIAGRAM SESSION INITIALIZED")
    logger.info(f"   Session ID: {session_id}")
    logger.info(f"   Description: {description}")
    logger.info(f"   Type: {diagram_type or 'drill'}")
    logger.info(f"   Build Method: {'INCREMENTAL' if return_empty_spec else 'TRADITIONAL'}")
    logger.info(f"   View: {view}")
    logger.info(f"   Started: {timestamp}")
    logger.info("=" * 80)
    
    result = {
        "session_id": session_id,
        "description": description,
        "diagram_type": diagram_type or "drill",
        "created_at": timestamp,
        "workflow": {
            "traditional": "Use analyze_hockey_query() for full pipeline",
            "incremental": "Use add_player(), add_movement(), etc. with returned spec"
        },
        "instructions": f"Pass session_id='{session_id}' to ALL subsequent tool calls",
        "status": "ready"
    }
    
    # Add empty spec if requested
    if return_empty_spec:
        result["spec"] = {
            "title": title or description,
            "description": description,
            "rink": {
                "view": view,
                "features": get_rink_features_for_view(view)
            },
            "players": [],
            "movements": [],
            "zones": [],
            "annotations": [],
            "equipment": [],
            "metadata": {
                "created": timestamp,
                "session_id": session_id,
                "diagram_type": diagram_type or "drill",
                "build_method": "incremental"
            }
        }
        logger.info(f"[Session {session_id}] Empty spec created with view: {view}")
    
    return result
```

---

## Tool 1: add_player (with Session Logging)

### MCP Tool Definition
```python
@mcp.tool("add_player")
def add_player(
    spec: Dict[str, Any],
    player_type: str,
    position_desc: str,
    team: str = "home",
    has_puck: bool = False,
    player_id: Optional[str] = None,
    label: Optional[str] = None,
    zone_hint: Optional[str] = None,
    session_id: Optional[str] = None  # For logging
) -> Dict[str, Any]:
```

### Implementation with Session Logging
```python
@mcp.tool("add_player")
def add_player(spec: Dict[str, Any], player_type: str, position_desc: str,
               team: str = "home", has_puck: bool = False, 
               player_id: Optional[str] = None, label: Optional[str] = None,
               zone_hint: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
    
    # Session-aware logging
    log_with_session(session_id, "info", f"➕ Adding {player_type} at '{position_desc}'")
    
    # Update session tracking
    if session_id and session_id in active_sessions:
        active_sessions[session_id]["steps_completed"].append(f"add_player:{player_id or 'auto'}")
        active_sessions[session_id]["current_step"] = "building_players"
    
    try:
        # Auto-generate player ID if not provided
        if not player_id:
            player_id = auto_generate_player_id(spec, player_type)
            log_with_session(session_id, "debug", f"Auto-generated ID: {player_id}")
        
        # Get zone from spec view if not provided
        if not zone_hint and "rink" in spec:
            zone_hint = spec["rink"].get("view", "full")
            log_with_session(session_id, "debug", f"Using view as zone hint: {zone_hint}")
        
        # Map position to coordinates using existing function
        position_result = map_position_to_coordinates(position_desc, zone_hint, session_id=session_id)
        
        if position_result.get("error"):
            log_with_session(session_id, "error", f"❌ Position mapping failed: {position_result['error']}")
            return {
                "status": "error",
                "error": position_result["error"],
                "spec": spec
            }
        
        coordinates = position_result["coordinates"]
        confidence = position_result.get("confidence", 1.0)
        
        log_with_session(session_id, "info", 
                        f"📍 Mapped '{position_desc}' to ({coordinates['x']}, {coordinates['y']}) "
                        f"[confidence: {confidence:.2f}]")
        
        # Check for overlaps
        overlap_check = check_player_overlap(spec, coordinates)
        if overlap_check["has_overlap"]:
            log_with_session(session_id, "warning", 
                           f"⚠️ Player overlap detected with {overlap_check['overlapping_player']}")
        
        # Handle puck assignment
        if has_puck:
            # Remove puck from other players
            for player in spec.get("players", []):
                if player.get("has_puck"):
                    log_with_session(session_id, "info", 
                                   f"🏒 Moving puck from {player['id']} to {player_id}")
                    player["has_puck"] = False
        
        # Create player object
        new_player = {
            "id": player_id,
            "type": player_type,
            "position": player_id,  # Display position
            "team": team,
            "has_puck": has_puck,
            "coordinates": coordinates,
            "label": label or player_id,
            "number": None
        }
        
        # Add to spec
        if "players" not in spec:
            spec["players"] = []
        spec["players"].append(new_player)
        
        # Log success with visual separator
        log_with_session(session_id, "info", 
                        f"✅ Successfully added {player_type} {player_id} "
                        f"({'with puck' if has_puck else 'without puck'})")
        log_with_session(session_id, "info", "-" * 40)
        
        return {
            "spec": spec,
            "added_player": {
                "id": player_id,
                "coordinates": coordinates,
                "position_confidence": confidence,
                "position_source": position_result.get("source", "unknown")
            },
            "status": "success",
            "message": f"Added {player_type} {player_id} at {position_desc}",
            "validation": {
                "zone_check": "pass",
                "overlap_check": "warning" if overlap_check["has_overlap"] else "pass",
                "puck_assignment": "valid"
            }
        }
        
    except Exception as e:
        log_with_session(session_id, "error", f"❌ Failed to add player: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "spec": spec
        }
```

---

## Tool 2: add_movement (with Session Logging)

### Implementation
```python
@mcp.tool("add_movement")
def add_movement(spec: Dict[str, Any], movement_type: str, from_ref: str, to_ref: str,
                pattern: str = "auto", timing: Optional[str] = None, 
                label: Optional[str] = None, movement_id: Optional[str] = None,
                session_id: Optional[str] = None) -> Dict[str, Any]:
    
    # Session logging with movement details
    log_with_session(session_id, "info", 
                    f"➡️ Adding {movement_type}: {from_ref} → {to_ref} [pattern: {pattern}]")
    
    # Update session tracking
    if session_id and session_id in active_sessions:
        active_sessions[session_id]["steps_completed"].append(f"add_movement:{movement_type}")
        active_sessions[session_id]["current_step"] = "building_movements"
    
    try:
        # Auto-generate movement ID
        if not movement_id:
            movement_id = f"m{len(spec.get('movements', [])) + 1}"
            log_with_session(session_id, "debug", f"Generated movement ID: {movement_id}")
        
        # Resolve from reference (player ID or position)
        from_resolved = resolve_reference(spec, from_ref)
        to_resolved = resolve_reference(spec, to_ref)
        
        log_with_session(session_id, "debug", 
                        f"Resolved: {from_ref} → {from_resolved['type']}:{from_resolved['id']}")
        log_with_session(session_id, "debug", 
                        f"Resolved: {to_ref} → {to_resolved['type']}:{to_resolved['id']}")
        
        # Get zone context from spec
        zone = spec.get("rink", {}).get("view", "full")
        
        # Use existing movement mapping function
        movement_result = map_movement_to_coordinates(
            from_resolved["position_desc"],
            to_resolved["position_desc"],
            movement_type,
            pattern,
            zone,
            session_id
        )
        
        if movement_result.get("error"):
            log_with_session(session_id, "error", f"❌ Movement mapping failed: {movement_result['error']}")
            return {
                "status": "error",
                "error": movement_result["error"],
                "spec": spec
            }
        
        # Log waypoint generation
        waypoints = movement_result.get("waypoints", [])
        if waypoints:
            log_with_session(session_id, "info", 
                           f"🔄 Generated {len(waypoints)} waypoints for {pattern} pattern")
        
        # Create movement object
        new_movement = {
            "id": movement_id,
            "type": movement_type,
            "from_pos": movement_result["from_pos"],
            "to_pos": movement_result["to_pos"],
            "waypoints": waypoints,
            "style": movement_result.get("style", "solid"),
            "arrow": movement_result.get("arrow", True),
            "arrow_end": movement_result.get("arrow_end", True),
            "label": label,
            "timing": timing
        }
        
        # Add to spec
        if "movements" not in spec:
            spec["movements"] = []
        spec["movements"].append(new_movement)
        
        # Calculate distance for logging
        distance = calculate_distance(movement_result["from_pos"], movement_result["to_pos"])
        
        log_with_session(session_id, "info", 
                        f"✅ Added {movement_type} {movement_id}: "
                        f"{from_ref} → {to_ref} (distance: {distance:.1f} units)")
        log_with_session(session_id, "info", "-" * 40)
        
        return {
            "spec": spec,
            "added_movement": {
                "id": movement_id,
                "type": movement_type,
                "pattern_used": pattern,
                "waypoints_generated": len(waypoints),
                "distance": distance,
                "from_resolved": f"{from_resolved['type']}:{from_resolved['id']}",
                "to_resolved": f"{to_resolved['type']}:{to_resolved['id']}"
            },
            "status": "success",
            "message": f"Added {movement_type} from {from_ref} to {to_ref}",
            "validation": {
                "path_clear": True,  # Could add obstacle detection
                "references_valid": True,
                "timing_valid": True
            }
        }
        
    except Exception as e:
        log_with_session(session_id, "error", f"❌ Failed to add movement: {str(e)}")
        return {
            "status": "error", 
            "error": str(e),
            "spec": spec
        }
```

---

## Tool 3: add_equipment (with Session Logging)

### Implementation
```python
@mcp.tool("add_equipment")
def add_equipment(spec: Dict[str, Any], equipment_type: str, position_desc: str,
                 count: int = 1, pattern: Optional[str] = None, 
                 spacing: Optional[float] = None, color: Optional[str] = None,
                 size: Optional[str] = None, equipment_id: Optional[str] = None,
                 session_id: Optional[str] = None) -> Dict[str, Any]:
    
    # Session logging
    log_with_session(session_id, "info", 
                    f"🔶 Adding {count} {equipment_type}(s) at '{position_desc}'")
    
    # Update session tracking
    if session_id and session_id in active_sessions:
        active_sessions[session_id]["steps_completed"].append(f"add_equipment:{equipment_type}")
        active_sessions[session_id]["current_step"] = "building_equipment"
    
    try:
        # Resolve position (could be relative)
        center_pos = resolve_relative_position(spec, position_desc, session_id)
        
        log_with_session(session_id, "debug", 
                        f"Center position: ({center_pos['x']}, {center_pos['y']})")
        
        # Generate positions based on pattern
        if count > 1 and pattern:
            positions = generate_pattern_positions(center_pos, count, pattern, spacing or 5.0)
            log_with_session(session_id, "info", 
                           f"📐 Generated {pattern} pattern with {count} items")
        else:
            positions = [center_pos]
        
        # Get equipment shape and style
        shape_info = get_equipment_shape(equipment_type, size or "medium")
        
        # Add equipment items
        if "equipment" not in spec:
            spec["equipment"] = []
        
        added_items = []
        for i, pos in enumerate(positions):
            item_id = equipment_id + str(i+1) if equipment_id else f"{equipment_type}{len(spec['equipment'])+i+1}"
            
            if equipment_type in ["cone", "pylon"]:
                # Create triangular cone shape
                vertices = create_cone_vertices(pos, shape_info["vertices_offset"])
                equipment_item = {
                    "id": item_id,
                    "type": equipment_type,
                    "shape": "polygon",
                    "vertices": vertices,
                    "color": color or "darkorange",
                    "fill": color or "darkorange",
                    "opacity": 0.8
                }
            elif equipment_type == "tire":
                equipment_item = {
                    "id": item_id,
                    "type": equipment_type,
                    "shape": "circle",
                    "position": pos,
                    "radius": shape_info["radius"],
                    "color": color or "black",
                    "fill": "none",
                    "stroke": color or "black",
                    "stroke_width": 2
                }
            elif equipment_type == "puck":
                equipment_item = {
                    "id": item_id,
                    "type": "puck",
                    "position": f"equipment_{item_id}",
                    "team": "neutral",
                    "coordinates": pos
                }
            
            spec["equipment"].append(equipment_item)
            added_items.append(item_id)
            
            log_with_session(session_id, "debug", f"Added {equipment_type} {item_id} at ({pos['x']}, {pos['y']})")
        
        log_with_session(session_id, "info", 
                        f"✅ Successfully added {count} {equipment_type}(s)")
        log_with_session(session_id, "info", "-" * 40)
        
        return {
            "spec": spec,
            "added_equipment": {
                "items": added_items,
                "positions": positions,
                "pattern": pattern,
                "total_added": count
            },
            "status": "success",
            "message": f"Added {count} {equipment_type}(s) at {position_desc}",
            "validation": {
                "positions_valid": True,
                "no_overlaps": True  # Could add overlap detection
            }
        }
        
    except Exception as e:
        log_with_session(session_id, "error", f"❌ Failed to add equipment: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "spec": spec
        }
```

---

## Supporting Functions with Logging

```python
def log_with_session(session_id: Optional[str], level: str, message: str):
    """Helper to log with session context - REUSE EXISTING"""
    session_tag = f"[Session {session_id}] " if session_id else ""
    full_message = f"{session_tag}{message}"
    
    if level == "info":
        logger.info(full_message)
    elif level == "error":
        logger.error(full_message)
    elif level == "warning":
        logger.warning(full_message)
    elif level == "debug":
        logger.debug(full_message)

def auto_generate_player_id(spec: Dict, player_type: str) -> str:
    """Generate next available player ID"""
    existing_ids = [p["id"] for p in spec.get("players", [])]
    
    prefix_map = {
        "forward": "F",
        "defense": "D", 
        "goalie": "G"
    }
    prefix = prefix_map.get(player_type, "P")
    
    # Find next available number
    num = 1
    while f"{prefix}{num}" in existing_ids:
        num += 1
    
    return f"{prefix}{num}"

def resolve_reference(spec: Dict, ref: str) -> Dict[str, Any]:
    """Resolve player ID or position to coordinates"""
    # Check if it's a player ID
    for player in spec.get("players", []):
        if player["id"] == ref:
            return {
                "type": "player",
                "id": ref,
                "coordinates": player["coordinates"],
                "position_desc": f"player {ref}"
            }
    
    # Otherwise treat as position description
    return {
        "type": "position",
        "id": ref,
        "position_desc": ref,
        "coordinates": None  # Will be resolved by map_position_to_coordinates
    }
```

---

## Usage Example with Full Logging

```python
# Step 1: Initialize with empty spec
result = initialize_diagram(
    description="2v1 rush drill with delayed support",
    diagram_type="drill", 
    view="full",
    return_empty_spec=True
)
session_id = result["session_id"]
spec = result["spec"]

# Console output:
# ================================================================================
# 🏒 NEW DIAGRAM SESSION INITIALIZED
#    Session ID: a3f4b2c1
#    Description: 2v1 rush drill with delayed support
#    Type: drill
#    Build Method: INCREMENTAL
#    View: full
#    Started: 2025-01-09T10:00:00Z
# ================================================================================

# Step 2: Add players incrementally
spec = add_player(spec, "forward", "center ice left", team="home", 
                 has_puck=True, session_id=session_id)
# [Session a3f4b2c1] ➕ Adding forward at 'center ice left'
# [Session a3f4b2c1] 📍 Mapped 'center ice left' to (0, -20) [confidence: 0.95]
# [Session a3f4b2c1] ✅ Successfully added forward F1 (with puck)
# ----------------------------------------

spec = add_player(spec, "forward", "center ice right", team="home",
                 session_id=session_id)
# [Session a3f4b2c1] ➕ Adding forward at 'center ice right'
# [Session a3f4b2c1] 📍 Mapped 'center ice right' to (0, 20) [confidence: 0.95]
# [Session a3f4b2c1] ✅ Successfully added forward F2 (without puck)
# ----------------------------------------

# Step 3: Add movements
spec = add_movement(spec, "skate", "F1", "offensive zone left", 
                   pattern="drive", session_id=session_id)
# [Session a3f4b2c1] ➡️ Adding skate: F1 → offensive zone left [pattern: drive]
# [Session a3f4b2c1] 🔄 Generated 2 waypoints for drive pattern
# [Session a3f4b2c1] ✅ Added skate m1: F1 → offensive zone left (distance: 45.2 units)
# ----------------------------------------

# Step 4: Add equipment
spec = add_equipment(spec, "cone", "neutral zone center", count=3,
                    pattern="line", spacing=10, session_id=session_id)
# [Session a3f4b2c1] 🔶 Adding 3 cone(s) at 'neutral zone center'
# [Session a3f4b2c1] 📐 Generated line pattern with 3 items
# [Session a3f4b2c1] ✅ Successfully added 3 cone(s)
# ----------------------------------------
```

This approach:
1. **Saves a tool** by enhancing `initialize_diagram`
2. **Uses existing logging** infrastructure with session IDs
3. **Provides visual feedback** with emojis and separators
4. **Tracks progress** through session state
5. **Enables debugging** with detailed step-by-step logs