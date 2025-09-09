# Hockey Diagram MCP v3 Technical Design

## Overview

Hockey Diagram MCP v3 is an enhanced version that provides both traditional full-pipeline diagram generation and new atomic tools for incremental building. It uses OpenAI's Responses API with Exa MCP integration for intelligent hockey term searches and position mapping.

## Architecture

### Core Components

1. **MCP Server Framework** (`FastMCP`)
   - Handles tool registration and execution
   - Manages stdio/SSE transport
   - Session tracking and logging

2. **OpenAI Integration**
   - Responses API for multi-turn conversations
   - Function calling for position mapping
   - Exa MCP integration for web searches

3. **Diagram Generation Pipeline**
   - Query analysis with web search enrichment
   - Specification translation with LLM assistance
   - Validation and preview
   - SVG/PNG generation

4. **Template Management System**
   - Save/search/fetch diagram templates
   - Fuzzy matching for template discovery
   - JSON-based storage with metadata

5. **Atomic Building Tools** (NEW)
   - Incremental diagram construction
   - Granular control over elements
   - Real-time validation

## Available MCP Tools

### Full Pipeline Tools
1. `initialize_diagram` - Start diagram session with optional empty spec
2. `analyze_hockey_query` - Analyze natural language query with web search enrichment
3. ~~`translate_analysis_to_spec`~~ - **DEPRECATED** - Use atomic building tools instead

### Atomic Building Tools (NEW)
4. `add_player` - Add individual player with intelligent positioning
5. `add_coach` - Add coach with zone-aware placement
6. `add_equipment` - Add equipment items with spreading for multiples
7. `add_movement` - Add movements with realistic curved paths and waypoints

### Validation & Preview Tools
8. `validate_diagram_node_minimal` - Quick validation of individual nodes
9. `validate_diagram_spec_full` - Comprehensive spec validation
10. `preview_diagram` - ASCII art or coordinate preview

### Generation & Template Tools
11. `generate_diagram` - Generate final SVG/PNG diagram
12. `save_diagram_template` - Save spec as reusable template
13. `search_diagram_templates` - Search saved templates with fuzzy matching
14. `fetch_diagram_template` - Retrieve saved template by ID

### Utility Tools
15. `health_check` - Server health and configuration status

## MCP Tools Reference

### 1. initialize_diagram (Enhanced)

**Purpose**: Start a diagram session with optional empty spec for incremental building

**Inputs**:
```python
{
    "description": str,           # Required: Brief description of diagram/drill
    "diagram_type": str,          # Optional: "drill", "play", "formation", "practice_plan"
    "title": str,                 # Optional: Title (defaults to description)
    "view": str,                  # Optional: "full", "offensive", "defensive", "neutral" (default: "full")
    "return_empty_spec": bool     # Optional: Return empty spec for incremental building (default: True)
}
```

**Outputs**:
```python
{
    "session_id": str,            # Unique 8-char session identifier
    "description": str,           # Echo of input description
    "diagram_type": str,          # Type of diagram
    "created_at": str,            # ISO timestamp
    "workflow": {
        "recommended": str,       # "INCREMENTAL (atomic building tools)"
        "steps": [str],           # 7-step procedure list
        "movement_patterns": {    # Guidance for complex movements
            "simple": str,
            "complex": str,
            "curve_control": str
        },
        "note": str               # Deprecation notice for translate_to_spec
    },
    "instructions": str,          # How to use session_id
    "status": str,                # "ready"
    "spec": {                     # Only if return_empty_spec=True
        "title": str,
        "description": str,
        "rink": {...},
        "players": [],
        "movements": [],
        "zones": [],
        "annotations": [],
        "equipment": [],
        "metadata": {...}
    },
    "spec_hints": {...}           # Coordinate system and position hints
}
```

**Algorithm Summary**:
1. Generate unique session ID (UUID first 8 chars)
2. Store session info in `active_sessions` dict
3. Log with visual separators and build method
4. If `return_empty_spec=True`:
   - Create empty spec structure
   - Set rink features based on view
   - Add coordinate hints and common positions
5. Return session info with dual workflow paths

---

### 2. analyze_hockey_query

**Purpose**: Analyze natural language drill descriptions with optional web search enrichment

**Inputs**:
```python
{
    "query": str,                      # Required: Natural language drill/play description
    "clarifications": dict,            # Optional: User answers to previous questions
    "use_exa_mcp": bool,              # Optional: Enable web search (default: True)
    "exa_api_key": str,               # Optional: Exa API key (uses env var if not provided)
    "session_id": str                 # Optional: Session ID for tracking
}
```

**Outputs**:
```python
{
    "original_query": str,
    "explicit_info": {
        "situation": str,              # What was clearly stated
        "zone": str,                   # Identified zone
        "key_actions": [str],          # Main actions/movements
        "faceoff_location": str        # If faceoff play
    },
    "components_with_assumptions": {
        "rink": {
            "view": str,               # Recommended view
            "assumption": str,         # Why this view
            "confidence": float        # 0.0-1.0
        },
        "players": [{
            "id": str,                # F1, D1, etc.
            "type": str,              # forward/defense/goalie
            "team": str,              # home/away/neutral
            "position_desc": str,     # Natural language position
            "assumption": str,        # What was assumed
            "confidence": float
        }],
        "movements": [{
            "id": str,                # m1, m2, etc.
            "type": str,              # pass/skate/shot
            "desc": str,              # Movement description
            "from_player": str,       # Source player ID
            "to_area": str,           # Target area/player
            "assumption": str,
            "confidence": float
        }],
        "zones": [...],
        "annotations": [...],
        "equipment": [...]
    },
    "questions_for_user": [{
        "question": str,              # Clarification needed
        "key": str,                  # Reference key
        "options": [str],            # Suggested answers
        "critical": bool,            # If critical for accuracy
        "confidence": float
    }],
    "metadata": {
        "type": str,                 # Drill classification
        "phase": str,                # Game phase
        "key_players": [str]         # Primary actors
    },
    "response_id": str,              # For conversation continuity
    "conversation": {...}            # Multi-turn tracking
}
```

**Algorithm Summary**:
1. Load prompt configuration
2. If Exa MCP enabled and available:
   - Configure MCP tools for web search
   - Set up Responses API with Exa integration
3. Make OpenAI Responses API call:
   - System prompt with hockey expertise
   - User query with clarifications
   - Structured JSON output format
4. If Exa used, extract search results from tool calls
5. Parse final JSON response
6. Return analysis with assumptions and questions

---

### 3. translate_analysis_to_spec (DEPRECATED)

**Status**: ⚠️ **DEPRECATED - NOT EXPOSED VIA MCP**

**Deprecation Reason**: 
- This all-in-one translation tool was overly ambitious with too many assumptions
- Lower confidence due to trying to map everything at once
- Atomic building tools provide higher confidence and precise control
- Code kept for reference but `@mcp.tool` decorator commented out

**Replacement Approach**:
Use atomic building tools in sequence:
1. `add_player()` - Add players one by one
2. `add_coach()` - Add coaches as needed
3. `add_equipment()` - Place equipment items
4. `add_movement()` - Create movements with curve control

**Original Purpose**: Convert analyzed query to complete diagram specification

**Inputs**:
```python
{
    "analysis": dict,                 # Required: Output from analyze_hockey_query
    "title": str,                     # Optional: Diagram title
    "description": str,               # Optional: Diagram description
    "existing_spec": dict,            # Optional: Previous spec to update
    "clarifications": dict,           # Optional: User clarifications
    "previous_response_id": str,      # Optional: For conversation continuity
    "session_id": str                 # Optional: Session ID for tracking
}
```

**Outputs**:
```python
{
    "spec": {
        "title": str,
        "description": str,
        "rink": {
            "view": str,              # full/offensive/defensive/neutral
            "features": [str]         # Rink elements to display
        },
        "players": [{
            "id": str,
            "type": str,              # forward/defense/goalie
            "position": str,          # Display position
            "team": str,              # home/away/neutral
            "has_puck": bool,
            "coordinates": {"x": float, "y": float},
            "label": str,
            "number": int
        }],
        "movements": [{
            "id": str,
            "type": str,              # pass/skate/shot/carry
            "from_pos": {"x": float, "y": float},
            "to_pos": {"x": float, "y": float},
            "waypoints": [{"x": float, "y": float}],
            "style": str,             # solid/dashed
            "arrow": bool,
            "arrow_end": bool,
            "label": str,
            "timing": str
        }],
        "zones": [...],
        "annotations": [...],
        "equipment": [...],
        "metadata": {...}
    },
    "conversation": {
        "response_id": str,           # For updates
        "mode": str                   # "initial" or "update"
    },
    "status": str,                    # "success" or "error"
    "message": str                    # Status message
}
```

**Algorithm Summary**:
1. Determine mode (initial vs update with clarifications)
2. Extract components from analysis
3. **Position Mapping** (Two-tier approach):
   - Try `map_hockey_position()` for direct lookup
   - Fallback to `map_positions_with_llm()` for complex positions
4. **Movement Generation**:
   - Map movement types to styles (pass=dashed, skate=solid)
   - Generate waypoints for curves if needed
   - Use LLM for complex patterns
5. **Equipment Placement**:
   - Position relative to players or landmarks
   - Generate patterns (line, arc, circle)
6. Apply clarifications if in update mode
7. Validate and return complete spec

---

### 4. add_player (NEW - Updated)

**Purpose**: Add individual player to diagram with intelligent positioning and mandatory zone specification

**Inputs**:
```python
{
    "spec": dict,                    # Required: Current diagram specification
    "player_type": str,              # Required: "forward", "defense", "goalie"
    "position_desc": str,            # Required: Natural language position
    "zone": str,                     # Required: "offensive", "defensive", "neutral" - MANDATORY
    "team": str,                     # Optional: "home", "away", "neutral" (default: "home")
    "has_puck": bool,               # Optional: Has puck (default: False)
    "player_id": str,               # Optional: Custom ID (auto-generates F1, D1, G1)
    "label": str,                   # Optional: Display label (defaults to player_id)
    "session_id": str               # Optional: Session ID for tracking
}
```

**Outputs**:
```python
{
    "spec": dict,                    # Updated spec with new player
    "added_player": {
        "id": str,                   # Player ID used
        "coordinates": {"x": float, "y": float, "note": str},  # Note included for special positions
        "position_confidence": float, # 0.0-1.0
        "position_source": str       # "direct_mapping" or "llm_mapping"
    },
    "status": str,                   # "success" or "error"
    "message": str,                  # Human-readable message
    "validation": {
        "zone_check": str,           # "pass" or "fail"
        "overlap_check": str,        # "pass" or "warning"
        "overlapping_with": [str],   # Entity IDs with overlaps (format: "type:id")
        "puck_assignment": str       # "valid" or "invalid"
    }
}
```

**Key Changes in v3**:
- **Mandatory Zone Parameter**: Zone is now required to eliminate ambiguity in position descriptions
- **Centralized Coordinates**: All position coordinates loaded from centralized `rink_positions.json` file
- **Enhanced Faceoff Dots**: Support for all 9 official faceoff dots (2 offensive, 2 defensive, 5 neutral)
- **Top of Circle**: Added "top of circle" coordinates (x=79 offensive, x=-79 defensive) extending past blue lines
- **Improved LLM Mapping**: Enhanced position mapping prompts with better coordinate examples

**Algorithm Summary**:
1. **Zone Validation**: Validate mandatory zone parameter ("offensive", "defensive", "neutral")
2. **Coordinate Loading**: Load centralized coordinate reference from `rink_positions.json`
3. **ID Generation**: If not provided, generate based on type (F1, D1, G1)
4. **Position Mapping** (Two-tier):
   - **Direct Mapping**: Check zone-specific position dictionary from centralized coordinates
   - **LLM Mapping**: Use enhanced prompts with correct coordinate examples for complex descriptions
5. **Spatial Collision Detection**: Check 5.0-unit proximity overlaps with players, coaches, and equipment
6. **Puck Management**: Ensure single possession if has_puck=True
7. **Spec Update**: Add player object to spec.players array with coordinates from centralized system
8. **Validation**: Return status with any warnings

---

### 5. add_coach (NEW)

**Purpose**: Add individual coach to diagram with intelligent positioning and zone-aware placement

**Inputs**:
```python
{
    "spec": dict,                    # Required: Current diagram specification
    "position_desc": str,            # Required: Natural language position like "behind bench", "top of circle", "near boards"
    "zone": str,                     # Required: "offensive", "defensive", "neutral", "bench" - MANDATORY
    "role": str,                     # Optional: "head", "assistant", "guest" (default: "head")
    "coach_id": str,                # Optional: Custom ID (auto-generates C1, C2, C3)
    "label": str,                   # Optional: Display label (defaults to coach_id)
    "session_id": str               # Optional: Session ID for tracking
}
```

**Outputs**:
```python
{
    "spec": dict,                    # Updated spec with new coach
    "added_coach": {
        "id": str,                   # Coach ID used
        "coordinates": {"x": float, "y": float},
        "position_confidence": float, # 0.0-1.0
        "position_source": str       # "direct_mapping" or "llm_mapping"
    },
    "status": str,                   # "success" or "error"
    "message": str,                  # Human-readable message
    "validation": {
        "position_check": str,       # "pass" or "fail"
        "overlap_check": str,        # "pass" or "warning"
        "overlapping_with": [str],   # Entity IDs with overlaps (format: "type:id")
        "in_play_area": bool         # Whether position is in valid coaching area
    }
}
```

**Key Features**:
- **Zone-Specific Positioning**: Supports "offensive", "defensive", "neutral", and "bench" zones
- **Coaching Positions**: Includes bench areas, penalty box, teaching positions like "top of circle"
- **Centralized Coordinates**: Uses same coordinate system as add_player
- **Role Management**: Supports different coaching roles with appropriate positioning

**Supported Positions by Zone**:
- **Offensive**: top of circle, blue line center, corners, behind net, goal line, slot positions
- **Defensive**: same as offensive with mirrored coordinates
- **Neutral**: center ice, red line, near blue lines
- **Bench**: home/away bench, behind bench, penalty box

**Algorithm Summary**:
1. **Zone Validation**: Validate mandatory zone parameter including "bench" zone
2. **Coordinate Loading**: Load centralized coordinate reference from `rink_positions.json`
3. **ID Generation**: If not provided, generate sequential coach ID (C1, C2, C3)
4. **Position Mapping** (Two-tier):
   - **Direct Mapping**: Check zone-specific coaching positions from centralized coordinates
   - **LLM Mapping**: Use enhanced prompts for complex coaching position descriptions
5. **Spatial Collision Detection**: Check 5.0-unit proximity overlaps with players, coaches, and equipment
6. **Position Validation**: Ensure coach position is appropriate for coaching context
7. **Spec Update**: Add coach object to spec.coaches array
8. **Validation**: Return status with overlap warnings and coaching position confirmation

---

### 6. add_equipment (NEW)

**Purpose**: Add equipment to diagram with intelligent positioning and zone-aware placement

**Inputs**:
```python
{
    "spec": dict,                    # Required: Current diagram specification
    "equipment_type": str,           # Required: "cone", "pylon", "tire", "net", "stick", "puck", "obstacle"
    "position_desc": str,            # Required: Natural language position like "blue line", "center ice", "corner"
    "zone": str,                     # Required: "offensive", "defensive", "neutral" - MANDATORY
    "count": int,                    # Optional: Number of equipment items (default: 1)
    "color": str,                    # Optional: Equipment color - "orange", "red", "blue", "yellow", "white", "black" (default: "orange")
    "size": str,                     # Optional: Equipment size - "small", "medium", "large" (default: "medium")
    "equipment_id": str,             # Optional: Custom ID (auto-generates E1, E2, E3)
    "label": str,                    # Optional: Display label (defaults to equipment_id)
    "session_id": str                # Optional: Session ID for tracking
}
```

**Outputs**:
```python
{
    "spec": dict,                    # Updated spec with new equipment
    "added_equipment": {
        "id": str,                   # Equipment ID used
        "type": str,                 # Equipment type
        "coordinates": {"x": float, "y": float},
        "count": int,                # Number of items requested
        "items_created": int,        # Actual items created (may be multiple for spreading)
        "position_confidence": float, # 0.0-1.0
        "position_source": str       # "direct_mapping" or "llm_mapping"
    },
    "status": str,                   # "success" or "error"
    "message": str,                  # Human-readable message
    "validation": {
        "position_check": str,       # "pass" or "fail"
        "overlap_check": str,        # "pass" or "warning"
        "overlapping_with": [str],   # Entity IDs with overlaps (format: "type:id")
        "count_check": str,          # "pass" or "fail"
        "equipment_type_valid": bool # Whether equipment type is recognized
    }
}
```

**Key Features**:
- **Zone-Specific Positioning**: Supports "offensive", "defensive", "neutral" zones using centralized coordinates
- **Multiple Equipment Support**: Can place 1-50 items with automatic spreading (8 units apart on y-axis)
- **Equipment Types**: Supports cone, pylon, tire, net, stick, puck, obstacle, goal, barrier
- **Visual Customization**: Color (orange, red, blue, yellow, white, black) and size options
- **Centralized Coordinates**: Uses same coordinate system as add_player and add_coach

**Equipment Specification Structure**:
```python
equipment_spec = {
    "id": str,                       # E1, E1_1, E1_2 (for multiple items)
    "type": str,                     # Equipment type
    "coordinates": {"x": float, "y": float},
    "count": 1,                      # Always 1 per individual item
    "color": str,                    # Visual color
    "size": str,                     # Physical size
    "label": str                     # Display label (only on first item if multiple)
}
```

**Algorithm Summary**:
1. **Zone Validation**: Validate mandatory zone parameter ("offensive", "defensive", "neutral")
2. **Equipment Validation**: Validate type, count (1-50), color, and size parameters
3. **Coordinate Loading**: Load centralized coordinate reference from `rink_positions.json`
4. **ID Generation**: If not provided, generate sequential equipment ID (E1, E2, E3)
5. **Position Mapping** (Two-tier):
   - **Direct Mapping**: Check zone-specific positions from centralized coordinates
   - **LLM Mapping**: Use enhanced prompts for complex equipment position descriptions
6. **Spatial Collision Detection**: Check 5.0-unit proximity overlaps with players, coaches, and equipment
7. **Multiple Item Handling**: 
   - Single item: Create one equipment object
   - Multiple items: Create individual objects spread 8 units apart on y-axis
8. **Spec Update**: Add equipment object(s) to spec.equipment array
9. **Validation**: Return status with overlap warnings and equipment placement confirmation

---

### 7. add_movement (ENHANCED v3)

**Purpose**: Add hockey movements with precise curve control using mathematical algorithms or intelligent LLM path generation

**Inputs**:
```python
{
    "spec": dict,                    # Required: Current diagram specification
    "movement_type": str,            # Required: "pass", "shot", "skate", "carry", "drop_pass", "backward", "lateral", "pressure"
    "from_desc": str,                # Required: Start position - player ID or position like "center ice"
    "to_desc": str,                  # Required: End position - player ID or position like "net", "slot"
    "curve_point": str,              # Optional: Control point for curve - where direction changes (NEW)
    "style": str,                    # Optional: "solid", "dashed", "dotted", "wavy" (default: "solid")
    "with_puck": bool,              # Optional: Whether movement involves puck (default: False)
    "label": str,                   # Optional: Label for the movement
    "movement_id": str,             # Optional: Custom ID (auto-generates M1, M2, M3)
    "session_id": str               # Optional: Session ID for tracking
}
```

**Outputs**:
```python
{
    "spec": dict,                    # Updated spec with new movement
    "added_movement": {
        "id": str,                   # Movement ID used
        "type": str,                 # Movement type
        "from_pos": {"x": float, "y": float},
        "to_pos": {"x": float, "y": float},
        "waypoints": [{"x": float, "y": float}],  # Generated curve waypoints
        "from_confidence": float,    # 0.0-1.0 confidence for start position
        "to_confidence": float,      # 0.0-1.0 confidence for end position
        "style": str,                # Line style
        "with_puck": bool,           # Puck involvement
        "has_waypoints": bool        # Whether waypoints were generated
    },
    "status": str,                   # "success" or "error"
    "message": str,                  # Human-readable message
    "validation": {
        "movement_type_valid": bool, # Valid movement type
        "style_valid": bool,         # Valid line style
        "from_resolved": bool,       # Start position successfully resolved
        "to_resolved": bool,         # End position successfully resolved
        "position_confidence": float,# Combined position confidence
        "path_check": str,           # "pass" or "warning"
        "path_intersections": [str], # Entity IDs that path crosses (format: "type:id")
        "boundary_violations": [str],# Boundary violations with coordinates
        "validation_warnings": [str],# All validation warnings
        "total_path_distance": float # Total path distance in units
    }
}
```

**Key Features**:
- **Position Resolution**: Three-tier resolution for FROM and TO positions:
  1. Player ID reference (existing players in spec)
  2. Direct coordinate mapping from centralized positions
  3. LLM fallback for complex descriptions
- **Realistic Path Generation**: LLM generates 2-4 waypoints for curved movements
- **Movement Physics**: Considers hockey-specific movement patterns (skating curves, obstacle avoidance)
- **Path Validation**: Comprehensive validation including:
  - Collision detection with players/equipment (5-unit radius)
  - Boundary checking (rink limits)
  - Distance validation by movement type

**Movement Types & Characteristics**:
- **pass**: Straight or slightly curved puck movement
- **shot**: Usually straight, can curve for deflections
- **skate**: Curved skating paths avoiding obstacles
- **carry**: Puck-carrying with realistic skating curves
- **drop_pass**: Backward pass with continuation
- **backward**: Skating backward with wider curves
- **lateral**: Side-to-side movement
- **pressure**: Aggressive forechecking path

**Algorithm Summary (ENHANCED v3)**:
1. **Type & Style Validation**: Validate movement type and line style parameters
2. **FROM Position Resolution** (3-tier):
   - Check if player ID reference → use player coordinates (confidence: 0.95)
   - Search centralized coordinates → use position (confidence: 0.9)
   - LLM position mapping → resolve complex description (confidence: 0.7)
3. **TO Position Resolution** (same 3-tier approach)
4. **CURVE_POINT Resolution** (NEW - optional):
   - If provided, resolve using same 3-tier approach as FROM/TO
   - Used as control point for mathematical curve generation
5. **Waypoint Generation Strategy** (NEW):
   - **With curve_point**: Use mathematical Bezier curve algorithm
     - Quadratic Bezier: B(t) = (1-t)²P0 + 2(1-t)tP1 + t²P2
     - Generates 2-4 smooth waypoints based on movement type
   - **Without curve_point**:
     - Shots/passes: Default to straight line (no waypoints)
     - Skating movements: Use LLM for intelligent path generation
     - LLM considers obstacles, hockey physics, realistic curves
6. **Path Validation**:
   - **Collision Detection**: Check if path intersects players/equipment (5-unit radius)
   - **Boundary Check**: Ensure path stays within rink limits (x: -100 to 100, y: -42.5 to 42.5)
   - **Distance Validation**: Check appropriate distance for movement type
7. **Spec Update**: Add movement with waypoints to spec.movements array
8. **Return Results**: Include comprehensive validation warnings and path metrics

**Mathematical Curve Generation (NEW)**:
When `curve_point` is provided, the tool uses a deterministic Bezier curve algorithm:
- **Quadratic Bezier Formula**: Generates smooth, predictable curves
- **Waypoint Count**: Adapts based on movement type and distance
  - Short passes/shots: 2 waypoints
  - Skating movements: 4 waypoints  
  - Default: 3 waypoints
- **Benefits**: Precise control, consistent results, no LLM API calls needed

**LLM Movement Context** (Fallback):
When no `curve_point` provided for complex movements, the LLM receives:
- Movement type and characteristics
- Start/end positions with descriptions and coordinates
- Current player positions for obstacle awareness
- Hockey coordinate system reference
- Instructions for realistic path generation

---

### 8. validate_diagram_node_minimal

**Purpose**: Quick validation of individual diagram nodes

**Inputs**:
```python
{
    "node_type": str,                # Required: "players", "movements", "zones", "annotations", "coaches"
    "node_data": dict,               # Required: Node data to validate
    "session_id": str                # Optional: Session ID for tracking
}
```

**Outputs**:
```python
{
    "valid": bool,                   # Overall validity
    "errors": [str],                 # Critical errors
    "warnings": [str],               # Non-critical issues
    "fixes": [str],                  # Suggested fixes
    "validated_data": dict           # Cleaned/fixed data if possible
}
```

**Algorithm Summary**:
1. Load schema for node_type (including new "coaches" node type)
2. Check required fields
3. Validate data types
4. Check value ranges (coordinates, etc.)
5. Suggest fixes for common issues
6. Return validation results

---

### 9. validate_diagram_spec_full

**Purpose**: Comprehensive validation of entire diagram specification

**Inputs**:
```python
{
    "spec": dict,                    # Required: Complete diagram specification
    "original_request": str,         # Optional: Original drill description for context
    "use_llm": bool,                # Optional: Use LLM for semantic validation (default: True)
    "session_id": str                # Optional: Session ID for tracking
}
```

**Outputs**:
```python
{
    "valid": bool,                   # Overall validity
    "validation_results": {
        "structure": {
            "valid": bool,
            "errors": [str],
            "warnings": [str]
        },
        "spatial": {
            "valid": bool,
            "conflicts": [str],       # Overlapping elements
            "out_of_bounds": [str]    # Elements outside rink
        },
        "hockey_sense": {
            "valid": bool,
            "issues": [str],          # Unrealistic positions/movements
            "suggestions": [str]      # Improvements
        }
    },
    "fixes_applied": [str],          # Auto-fixes applied
    "manual_fixes_needed": [str],    # Issues requiring user input
    "cleaned_spec": dict             # Spec with fixes applied
}
```

**Algorithm Summary**:
1. **Structure Validation**:
   - Check all required fields
   - Validate data types and formats
   - Ensure IDs are unique
2. **Spatial Validation**:
   - Check coordinate bounds (-100 to 100, -42.5 to 42.5)
   - Detect overlapping players
   - Verify movement paths are valid
3. **Hockey Sense** (if use_llm=True):
   - Check positions make hockey sense
   - Validate movement patterns
   - Ensure drill flow is logical
4. Apply automatic fixes where possible
5. Return comprehensive validation report

---

### 10. preview_diagram

**Purpose**: Preview diagram as ASCII art or coordinate list

**Inputs**:
```python
{
    "spec": dict,                    # Required: Diagram specification
    "format": str,                   # Optional: "ascii" or "coordinates" (default: "ascii")
    "session_id": str                # Optional: Session ID for tracking
}
```

**Outputs**:
```python
# If format="ascii":
{
    "preview": str,                  # ASCII art representation
    "legend": str,                   # Symbol explanations
    "dimensions": {"width": int, "height": int}
}

# If format="coordinates":
{
    "players": [{
        "id": str,
        "position": {"x": float, "y": float},
        "symbol": str
    }],
    "movements": [{
        "id": str,
        "from": {"x": float, "y": float},
        "to": {"x": float, "y": float},
        "type": str
    }],
    "equipment": [...],
    "rink_bounds": {"x": [-100, 100], "y": [-42.5, 42.5]}
}
```

**Algorithm Summary**:
1. If format="ascii":
   - Create 80x40 character grid
   - Map coordinates to grid positions
   - Place symbols for players (F, D, G)
   - Draw movement lines with ASCII characters
   - Add legend
2. If format="coordinates":
   - Extract all positioned elements
   - Format as structured data
   - Include bounds for reference
3. Return preview in requested format

---

### 11. generate_diagram

**Purpose**: Generate final SVG and PNG diagram files

**Inputs**:
```python
{
    "spec": dict,                    # Required: Complete validated diagram specification
    "output_name": str,              # Optional: Base name for output files
    "session_id": str                # Optional: Session ID for tracking
}
```

**Outputs**:
```python
{
    "status": str,                   # "success" or "error"
    "svg_path": str,                 # Path to generated SVG file
    "png_path": str,                 # Path to generated PNG file
    "output_dir": str,               # Directory containing files
    "filename_base": str,            # Base filename used
    "generation_time": float,        # Time taken in seconds
    "trace_data": {                  # If session_id provided
        "rows": [[...]],             # Data for Google Sheets upload
        "summary": str               # Generation summary
    }
}
```

**Algorithm Summary**:
1. Convert spec dict to DiagramSpec object
2. Initialize DiagramBuilder with spec
3. **Rendering Pipeline**:
   - Draw rink with specified features
   - Place players at coordinates
   - Draw movements with waypoints
   - Add equipment and zones
   - Render annotations
4. Export as SVG using svgwrite
5. Convert SVG to PNG using cairosvg
6. Save files with timestamp/name
7. If session tracked, compile trace data
8. Return file paths and metadata

---

### 12. save_diagram_template

**Purpose**: Save validated diagram spec as reusable template

**Inputs**:
```python
{
    "spec": dict,                    # Required: Validated diagram specification
    "name": str,                     # Required: Unique template name
    "description": str,              # Required: Human-readable description
    "tags": [str],                   # Optional: Tags for searchability
    "session_id": str                # Optional: Session ID for tracking
}
```

**Outputs**:
```python
{
    "template_id": str,              # Unique template identifier
    "filepath": str,                 # Where template was saved
    "name": str,                     # Template name
    "description": str,              # Template description
    "status": str,                   # Success message
    "metadata": {
        "created_at": str,           # ISO timestamp
        "spec_version": str,         # Spec format version
        "player_count": int,
        "movement_count": int
    }
}
```

**Algorithm Summary**:
1. Generate template ID (hash of name + timestamp)
2. Create template metadata
3. Bundle spec with metadata
4. Save to templates directory as JSON
5. Update template index
6. Return template info

---

### 13. search_diagram_templates

**Purpose**: Fuzzy search for existing diagram templates

**Inputs**:
```python
{
    "query": str,                    # Required: Search query
    "tags": [str],                   # Optional: Filter by tags
    "top_k": int,                    # Optional: Number of results (default: 5)
    "session_id": str                # Optional: Session ID for tracking
}
```

**Outputs**:
```python
{
    "templates": [{
        "id": str,                   # Template ID
        "name": str,                 # Template name
        "description": str,          # Template description
        "similarity": float,         # Match score (0.0-1.0)
        "tags": [str],              # Template tags
        "metadata": {...}           # Additional info
    }],
    "total_found": int,             # Total matches
    "query": str                    # Original query
}
```

**Algorithm Summary**:
1. Load all templates from directory
2. For each template:
   - Calculate similarity using difflib.SequenceMatcher
   - Match against name and description
   - Apply tag filters if provided
3. Sort by similarity score
4. Return top_k results
5. Include metadata for each match

---

### 14. fetch_diagram_template

**Purpose**: Retrieve a saved diagram template by ID

**Inputs**:
```python
{
    "template_id": str,              # Required: Template ID to fetch
    "session_id": str                # Optional: Session ID for tracking
}
```

**Outputs**:
```python
{
    "template_id": str,              # Template ID
    "name": str,                     # Template name
    "description": str,              # Template description
    "spec": dict,                    # Complete diagram specification
    "tags": [str],                   # Template tags
    "metadata": {
        "created_at": str,
        "spec_version": str,
        "player_count": int,
        "movement_count": int
    },
    "status": str                    # Success/error message
}
```

**Algorithm Summary**:
1. Construct template filepath from ID
2. Check if file exists
3. Load and parse JSON
4. Validate template structure
5. Extract spec and metadata
6. Return complete template data

---

### 15. health_check

**Purpose**: Check server health and configuration status

**Inputs**:
```python
{
    # No inputs required
}
```

**Outputs**:
```python
{
    "status": str,                   # "healthy" or "unhealthy"
    "server": str,                   # "hockey-diagram-v3"
    "version": str,                  # Server version
    "openai_configured": bool,       # If OpenAI API key present
    "tools_available": [str],        # List of all available tools
    "template_library": {
        "templates_dir": str,         # Template directory path
        "template_count": int,        # Number of templates
        "status": str                 # Library status
    },
    "responses_api_info": {
        "status": str,                # API readiness
        "mcp_integration": str,       # Exa MCP status
        "note": str                   # Additional info
    }
}
```

**Algorithm Summary**:
1. Check OpenAI client initialization
2. Count templates in directory
3. List all registered MCP tools
4. Check Responses API availability
5. Return comprehensive status report

---

## Position Mapping Details

### Two-Tier Position Mapping System (Enhanced v3)

#### Tier 1: Direct Mapping (Centralized Coordinates)
Position coordinates now loaded from centralized `config/coordinates/rink_positions.json`:

```python
# Loaded dynamically from rink_positions.json
zone_positions = {
    "offensive": {
        "right faceoff dot": {"x": 69, "y": -22.5},
        "left faceoff dot": {"x": 69, "y": 22.5},
        "top of circle": {"x": 79, "y": 0},     # NEW - Circle extends past blue line
        "slot": {"x": 75, "y": 0},
        "high slot": {"x": 65, "y": 0},
        "right point": {"x": 54, "y": -38},
        "left point": {"x": 54, "y": 38},
        "net front": {"x": 85, "y": 0},
        "behind net": {"x": 92, "y": 0},
        # ... complete reference in centralized file
    },
    "defensive": {
        # Mirror of offensive with negative x values
        "top of circle": {"x": -79, "y": 0},    # NEW - Consistent coordinate
        # ... complete reference in centralized file
    },
    "neutral": {
        "center faceoff dot": {"x": 0, "y": 0},
        "right offensive neutral dot": {"x": 20, "y": -22.5},  # NEW - All 9 faceoff dots
        "left offensive neutral dot": {"x": 20, "y": 22.5},
        "right defensive neutral dot": {"x": -20, "y": -22.5},
        "left defensive neutral dot": {"x": -20, "y": 22.5},
        # ... complete reference in centralized file
    },
    "bench": {
        "home bench": {"x": -50, "y": 42},      # NEW - Coaching positions
        "away bench": {"x": -50, "y": -42},
        "penalty box": {"x": 0, "y": -42}
        # ... complete reference in centralized file
    }
}
```

**Key Improvements**:
- **Single Source of Truth**: All coordinates in one JSON file
- **All 9 Faceoff Dots**: Complete official faceoff dot set
- **Top of Circle**: Accurate positioning extending past blue lines
- **Coaching Zones**: Dedicated bench and teaching positions

#### Tier 2: LLM Mapping (Enhanced Prompts)
Enhanced with accurate coordinate examples from centralized file:
- "halfway between blue line and top of circle" → x = (69 + 79) / 2 = 74
- "between the circles"
- "screening the goalie"  
- "just inside the offensive zone on the left"

Uses OpenAI function calling with corrected spatial reasoning prompts loaded from centralized coordinates.

## Coordinate System

### Ice Surface
- **X-axis**: -100 (left boards) to +100 (right boards)
- **Y-axis**: -42.5 (bottom boards) to +42.5 (top boards)
- **Origin**: (0, 0) at center ice

### Zone Boundaries
- **Offensive**: x > 25
- **Neutral**: -25 ≤ x ≤ 25
- **Defensive**: x < -25

### Key Landmarks (Updated v3)
| Position | Offensive | Defensive | Notes |
|----------|-----------|-----------|-------|
| Faceoff dots | (69, ±22.5) | (-69, ±22.5) | 2 per zone |
| Top of circle | (79, 0) | (-79, 0) | **NEW** - Extends past blue line |
| High slot | (65, 0) | (-65, 0) | Updated position |
| Slot | (75, 0) | (-75, 0) | Primary slot position |
| Net front | (85, 0) | (-85, 0) | Updated position |
| Behind net | (92, 0) | (-92, 0) | Behind goal line |
| Blue line | x = 69 | x = -69 | **Updated** - Actual blue line position |
| Goal line | x = 89 | x = -89 | Goal line position |

### Faceoff Dots (All 9 - NEW)
| Zone | Position | Coordinates |
|------|----------|-------------|
| Offensive | Right/Left | (69, ±22.5) |
| Defensive | Right/Left | (-69, ±22.5) |
| Neutral | Center | (0, 0) |
| Neutral | Offensive Right/Left | (20, ±22.5) |
| Neutral | Defensive Right/Left | (-20, ±22.5) |

### Coaching Positions (NEW)
| Zone | Position | Coordinates |
|------|----------|-------------|
| Bench | Home Bench | (-50, 42) |
| Bench | Away Bench | (-50, -42) |
| Bench | Penalty Box | (0, -42) |

## Session Management

### Session Structure
```python
active_sessions = {
    "session_id": {
        "description": str,
        "created_at": datetime,
        "steps_completed": [str],
        "current_step": str,
        "build_method": "traditional" | "incremental"
    }
}
```

### Logging Indicators
- 🏒 Session initialization
- ➕ Adding player
- ➡️ Adding movement
- 🔶 Adding equipment
- 📍 Position mapped
- ✅ Success
- ⚠️ Warning
- ❌ Error

## Movement Chaining Patterns

### Complex Movement Decomposition

For complex skating patterns, the LLM should decompose them into multiple chained `add_movement` calls:

#### Circle/Loop Pattern
**User Request**: "Player skates a circle around center ice"
**Decomposition**: 4 movements with curve points at compass positions
```python
# Quarter 1: South to East
add_movement(spec, "skate", "below center", "right of center", 
             curve_point="southeast of center")
# Quarter 2: East to North
add_movement(spec, "skate", "right of center", "above center",
             curve_point="northeast of center")
# Quarter 3: North to West
add_movement(spec, "skate", "above center", "left of center",
             curve_point="northwest of center")
# Quarter 4: West to South
add_movement(spec, "skate", "left of center", "below center",
             curve_point="southwest of center")
```

#### Figure-8 Pattern
**User Request**: "Figure-8 around the faceoff dots"
**Decomposition**: 4 movements forming two connected loops
```python
# First loop around left dot
add_movement(spec, "skate", "center", "center",
             curve_point="left faceoff dot")
# Second loop around right dot  
add_movement(spec, "skate", "center", "center",
             curve_point="right faceoff dot")
```

#### Zigzag/Crossovers Pattern
**User Request**: "Crossovers down the ice"
**Decomposition**: Alternating lateral movements
```python
# First crossover
add_movement(spec, "skate", "left boards defensive", "right boards neutral",
             curve_point="center defensive")
# Second crossover
add_movement(spec, "skate", "right boards neutral", "left boards offensive",
             curve_point="center neutral")
# Continue pattern...
```

#### Weave Through Cones
**User Request**: "Weave through cones in neutral zone"
**Decomposition**: Sequential curves around each obstacle
```python
# Around first cone
add_movement(spec, "skate", "start", "past E1",
             curve_point="left of E1")
# Around second cone
add_movement(spec, "skate", "past E1", "past E2",
             curve_point="right of E2")
# Continue for each cone...
```

### Movement Continuity Rules

1. **Continuous Path**: The TO position of movement N should match the FROM position of movement N+1
2. **Sequential IDs**: Use M1, M2, M3... for related movements in a pattern
3. **Consistent Style**: Maintain the same line style across pattern segments
4. **Shared Points**: Reuse positions for smooth connections (e.g., "center" in figure-8)

### Pattern Recognition Guidelines

LLMs should recognize these keywords as multi-movement patterns:
- **"circle"** → 4+ curved movements
- **"figure-8"** → 4 movements (2 per loop)
- **"weave"** → alternating lateral movements
- **"back and forth"** → paired opposite movements
- **"zigzag"** → alternating diagonal movements
- **"loop"** → closed path returning to start
- **"serpentine"** → S-curve patterns

## Error Handling

All tools follow consistent error handling:

```python
# Success response
{
    "status": "success",
    "data": {...},
    "message": str
}

# Error response
{
    "status": "error",
    "error": str,
    "suggestions": [str],
    "original_input": {...}
}
```

## Performance Metrics

- **Direct position mapping**: < 1ms
- **LLM position mapping**: 1-2s
- **Full pipeline**: 3-5s
- **Diagram generation**: 1-2s
- **Template search**: < 100ms

## Dependencies

- `mcp.server.fastmcp`: MCP framework
- `openai`: GPT-4 integration
- `hockey_diagram_builder`: SVG generation
- `validators`: Schema validation
- `difflib`: Fuzzy matching
- `cairosvg`: PNG conversion