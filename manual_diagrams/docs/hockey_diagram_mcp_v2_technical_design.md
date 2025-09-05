# Hockey Diagram MCP v2 Technical Design

## Overview
Version 2.0 represents a major evolution of the hockey diagram MCP server, with comprehensive position mapping, enhanced movement patterns, and smooth curve rendering.

## Architecture

### Core Components

#### 1. MCP Server (`hockey_diagram_mcp_v2.py`)
- FastMCP-based server with 10 specialized tools
- Session management for trace logging
- Integration with OpenAI for LLM-based interpretation
- Google Sheets integration for trace upload

#### 2. Position Mapper (`position_mapper.py`)
- 80+ positions per zone (offensive, defensive, neutral)
- Faceoff formations with proper team orientations
- Slot positioning (high/mid/low with left/middle/right)
- Point positions (5 variations inside blue line)
- Relative positioning support
- LLM fallback for complex descriptions

#### 3. Movement Pattern System
- 15 distinct movement patterns
- Automatic waypoint generation
- Pattern aliases (e.g., "wrap around" → "wrap")
- LLM-based pattern detection
- Zone-aware adjustments

#### 4. Diagram Builder (`hockey_diagram_builder.py`)
- CubicSpline interpolation for smooth curves
- Proper z-ordering for visual hierarchy
- Support for equipment (cones, pylons)
- Net element with realistic 3D appearance

## MCP Tool Workflow

### Typical Tool Flow
```
1. initialize_diagram → Start session, get instructions
2. search_diagram_template → Find similar drills
3. map_position_to_coordinates → Convert positions to coords
4. map_movement_to_coordinates → Generate movement paths
5. validate_diagram_node_minimal → Quick validation
6. validate_diagram_spec_full → Complete validation
7. preview_diagram → ASCII/coordinate preview
8. generate_diagram → Create final PNG/SVG
```

## Tool Implementations

### 1. `initialize_diagram`
**Purpose**: Start a new diagram session and provide workflow guidance  
**Input**: `drill_request` - Natural language drill description  
**Output**: Session ID, workflow instructions, available tools

```python
def initialize_diagram(drill_request: str) -> Dict[str, Any]:
    # Creates unique session ID for trace logging
    # Returns step-by-step workflow instructions
    # Lists available tools and their sequence
    # Example: "2v1 rush drill" → session_123, instructions
```

### 2. `search_diagram_node`
**Purpose**: Get schema and instructions for diagram spec nodes  
**Input**: `node_type` - Type of node (players|movements|rink|zones|annotations)  
**Output**: Schema, enums, examples, and constraints

```python
def search_diagram_node(node_type: str) -> Dict[str, Any]:
    # Returns JSON schema for the node type
    # Includes valid enums (e.g., player types)
    # Provides examples and validation rules
    # Example: "players" → player schema with types, positions
```

### 3. `search_diagram_template`
**Purpose**: Find existing drill templates matching query  
**Input**: `query` - Search terms, `template_type` - Filter, `limit` - Max results  
**Output**: List of matching templates with previews

```python
def search_diagram_template(query: str, template_type: str = None) -> List:
    # Searches template library (40+ drills)
    # Returns matches with confidence scores
    # Includes preview of each template
    # Example: "2v1" → rush template, give_and_go template
```

### 4. `fetch_diagram_template`
**Purpose**: Get complete template specification  
**Input**: `template_name` - Name of template  
**Output**: Full JSON specification ready to use

```python
def fetch_diagram_template(template_name: str) -> Dict:
    # Loads complete template from library
    # Returns ready-to-use diagram spec
    # Can be modified or used as-is
    # Example: "rush" → full 2v1 rush drill spec
```

### 5. `map_position_to_coordinates`
**Purpose**: Convert natural language positions to exact coordinates  
**Input**: `position` - Natural language, `zone` - Context zone, `reference_positions` - For relative  
**Output**: Exact [x, y] coordinates with confidence

Enhanced with:
- **Direct Matching**: 250+ predefined positions
- **LLM Interpretation**: GPT-3.5 for complex descriptions
- **Relative Positioning**: "5 units left of F1"
- **Fuzzy Matching**: Partial string matches
- **Confidence Scoring**: 0.7-1.0 scale

```python
# Processing hierarchy:
1. Check direct position match (confidence=1.0)
2. Try LLM interpretation (confidence=0.8-0.95)
3. Parse relative positions (confidence=0.9)
4. Fuzzy substring matching (confidence=0.7-0.85)

# Example: "high slot left" → {"x": 47, "y": 20, "confidence": 1.0}
```

### 6. `map_movement_to_coordinates`
**Purpose**: Generate complete movement with waypoints  
**Input**: `from_position`, `to_position` - Start/end positions, `movement_type`, `pattern`  
**Output**: Movement spec with coordinates and waypoints

Enhanced with:
- **Pattern Detection**: LLM determines best pattern when auto
- **15 Movement Patterns**: rim, dump, sauce, wrap, etc.
- **Custom Waypoints**: LLM can suggest specific waypoints
- **Pattern Aliases**: Natural language support

```python
# Pattern selection:
if pattern == "auto" and client:
    # LLM analyzes movement context
    # Suggests pattern and waypoints
else:
    # Use specified pattern
    # Calculate waypoints via calculate_waypoints()

# Example: "slot to corner", pattern="dump" → waypoints for dump-in
```

### 7. `validate_diagram_node_minimal`
**Purpose**: Quick validation of single node  
**Input**: `node_type`, `node_data` - Node to validate  
**Output**: Validation results with issues and fixes

```python
def validate_diagram_node_minimal(node_type: str, node_data: dict):
    # Checks required fields present
    # Validates data types
    # Returns specific issues and fixes
    # Example: missing "team" field → add "team": "home"
```

### 8. `validate_diagram_spec_full`
**Purpose**: Comprehensive validation of complete diagram  
**Input**: `spec` - Complete diagram, `original_request` - For context  
**Output**: Valid flag, issues, suggestions, warnings

Comprehensive validation:
- **Structure Check**: Required fields present
- **Spatial Validation**: No overlapping players
- **Hockey Rules**: Max 6 players per team
- **Movement Logic**: Cross-ice needs waypoints
- **Zone Validation**: Players in correct zones

```python
# Example validation output:
{
    "valid": False,
    "issues": ["Player F1 outside rink bounds"],
    "suggestions": ["Move F1 to slot position"],
    "warnings": ["Cross-ice pass may need waypoints"]
}
```

### 9. `preview_diagram`
**Purpose**: Preview diagram before generation  
**Input**: `spec` - Diagram spec, `format` - "ascii" or "coordinates"  
**Output**: Text-based preview of diagram

```python
def preview_diagram(spec: dict, format: str = "ascii"):
    # ASCII art shows rough player positions
    # Coordinate list shows exact positions
    # Helps verify before final generation
    # Example: ASCII art with F1, F2, D1 positions
```

### 10. `generate_diagram`
**Purpose**: Create final diagram files  
**Input**: `spec` - Validated diagram spec, `output_name` - Optional filename  
**Output**: File paths to PNG/SVG, trace data

- Creates PNG/SVG output files
- Returns trace data for Google Sheets
- Handles session logging
- Provides file paths

```python
# Example output:
{
    "png_path": "outputs/rush_drill_2025-09-01.png",
    "svg_path": "outputs/rush_drill_2025-09-01.svg",
    "trace_data": {...},
    "session_id": "session_123"
}
```

### 11. `tools_health_check`
**Purpose**: Verify MCP server status  
**Output**: Server health, available resources, debug info

```python
def tools_health_check():
    # Checks server status
    # Lists available tools
    # Shows resource counts
    # Returns debug information
```

## Key Enhancements in v2.0

### Position System Overhaul
```python
OFFENSIVE_POSITIONS = {
    # Faceoff formations (22 positions)
    "offensive left faceoff home center": (67, 22.5),
    # ... proper team orientations
    
    # Slot positions (13 variations)
    "high slot": (47, 0),  # x=47, not 69!
    "mid slot": (69, 0),   # At hashmarks
    "low slot": (79, 0),   # Near crease
    
    # Point positions (5 variations)
    "point": (30, 0),  # Inside blue line, not on it
    # ... with boards variations
}
```

### Movement Pattern Library
```python
def calculate_waypoints(from_pos, to_pos, pattern):
    if pattern == "rim":
        # Along boards behind net
        waypoints = [
            [from_x, 38],      # To boards
            [89, 38],          # Along to corner
            [89, 0],           # Behind net
            [89, -38],         # Other corner
            [to_x, to_y]       # Final
        ]
    elif pattern == "dump":
        # High and deep
        waypoints = [
            [from_x + dx * 0.3, from_y + dy * 0.2],
            [85, 35]  # High into corner
        ]
    # ... 13 more patterns
```

### Rendering Improvements
```python
def _draw_curved_movement(self, movement):
    # Build complete path
    path_points = [start] + waypoints + [end]
    
    # CubicSpline interpolation
    cs_x = CubicSpline(t, points[:, 0])
    cs_y = CubicSpline(t, points[:, 1])
    
    # 100 smooth points
    t_smooth = np.linspace(0, len(points)-1, 100)
```

## LLM Integration

### Position Mapping Prompt
```python
prompt = f"""
Position request: "{position}"
Zone: {zone} ZONE
Reference positions: {reference_positions}

{zone} ZONE positions (showing 60 of {total}):
[Categorized position list]

Handle:
1. Position aliases (RW→right wing)
2. Relative positions ("5 units left of F1")
3. Face-off positions
4. Contextual descriptions

Output: x|y|confidence|reasoning
"""
```

### Movement Pattern Prompt
```python
prompt = f"""
Movement: {movement_type} from {from_position} to {to_position}
Zone: {zone} ZONE
Distance: {distance} units

HOCKEY MOVEMENT PATTERNS:
[15 patterns with descriptions]

Determine:
1. Most appropriate pattern
2. Special waypoints needed

Output: pattern|waypoint1_x,waypoint1_y|waypoint2_x,waypoint2_y
"""
```

## Performance Optimizations

### Caching Strategy
- Position mappings cached in dictionaries
- Template patterns pre-loaded
- LLM responses not cached (context-dependent)

### Efficient Lookups
```python
# O(1) direct position lookup
if position_lower in zone_positions:
    return zone_positions[position_lower]

# Short-circuit on high confidence
if confidence >= 0.95:
    return early
```

## Error Handling

### Graceful Fallbacks
1. LLM fails → Fall back to fuzzy matching
2. No position match → Return closest landmark
3. Invalid pattern → Default to "curve"
4. Waypoint calculation fails → Use direct line

### Validation Feedback
```python
{
    "valid": False,
    "issues": ["High slot at wrong x-coordinate"],
    "suggestions": ["Change x from 69 to 47"],
    "warnings": ["Cross-ice movement needs waypoints"]
}
```

## Testing Coverage

### Position Testing
- `test_offensive_positions.py`: All offensive positions
- `test_defensive_positions.py`: All defensive positions  
- `test_neutral_positions.py`: Neutral zone positions
- Validates coordinates and orientations

### Movement Testing
- `test_movement_patterns.py`: All 15 patterns
- Verifies waypoint generation
- Checks curve rendering

## Integration Points

### Google Sheets
```python
# Trace data upload
trace_data = {
    "rows": [
        [timestamp, session_id, drill, step, phase, 
         action, thought, input, output, issues, 
         success, lessons]
    ]
}
```

### External Tools
- `mcp__hockey_kb__*`: Hockey knowledge base
- `mcp__exa__*`: Web search
- `mcp__google-sheets__*`: Data upload

## Configuration

### Environment Variables
```python
OPENAI_API_KEY  # For LLM interpretation
ANTHROPIC_API_KEY  # Optional
MCP_SERVER_NAME = "hockey-diagram"
```

### Default Settings
```python
# Confidence thresholds
MIN_CONFIDENCE = 0.7
LLM_CONFIDENCE = 0.85

# Rendering
INTERPOLATION_POINTS = 100
DEFAULT_Z_ORDER = {
    'rink': 0,
    'zones': 6,
    'movements': 8,
    'players': 10,
    'equipment': 11,
    'goalie': 12
}
```

## Future Enhancements

### Planned Features
1. **Multi-phase drill support**: Separate diagrams per phase
2. **Animation export**: Sequence of movements
3. **3D visualization**: Perspective view option
4. **Team system templates**: PP, PK, breakout systems

### Optimization Opportunities
1. **Batch LLM calls**: Multiple positions in one request
2. **Template caching**: Store generated specs
3. **Parallel rendering**: Multi-threaded diagram generation
4. **CDN for assets**: Host rink backgrounds

## Deployment

### Local Development
```bash
python servers/hockey_diagram_mcp_v2.py
```

### Production Considerations
- Use connection pooling for LLM clients
- Implement rate limiting for API calls
- Add monitoring for tool usage
- Set up error alerting

## Maintenance

### Adding New Positions
```python
# In position_mapper.py
OFFENSIVE_POSITIONS["new_position"] = (x, y)
```

### Adding New Patterns
```python
# In calculate_waypoints()
elif pattern == "new_pattern":
    waypoints = [
        # Define waypoint calculation
    ]
```

### Updating LLM Prompts
- Keep position list under 60 for token limits
- Prioritize commonly used positions
- Include clear examples in prompts

## Version History

### v2.0 (2025-09-01)
- Complete position system overhaul (250+ positions)
- 15 movement patterns with LLM detection
- Smooth curve rendering with CubicSpline
- Enhanced validation and error handling
- Agent instruction updates

### v1.1 (2025-08-27)
- Added waypoint support for movements
- Basic curve rendering
- Initial position mappings

### v1.0 (2025-08-26)
- Initial MCP server implementation
- 10 core tools
- Basic validation