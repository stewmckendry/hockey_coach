# Reusability Lessons from Drill Development

## Key Improvements for Future Drills

### 1. Equipment Library
We added support for:
- **Pucks**: Simple black dots using `Player(type='puck')`
- **Pylons/Cones**: Orange triangles using `Zone(type='cone', shape='polygon')` with vertices
- **Proper Z-ordering**: Equipment at z-order 11 to be visible above players

### 2. Movement Pattern Functions
The `drill_utilities.py` module provides:
- `generate_arc_points()`: For curved skating paths with proper counterclockwise handling
- Standard positions dictionary for common locations
- Z-order constants for consistent layering

### 3. Coordinate Understanding
Instead of requiring exact coordinates from users:
- **Landmarks Reference**: 
  - Goal lines: x = ±89
  - Blue lines: x = ±25  
  - Faceoff circles: center at (±69, ±22.5)
  - Boards: y = ±42.5
  - Center ice: (0, 0)

- **Movement Descriptions to Coordinates**:
  - "Cross ice" = Big Y-axis change (e.g., +38 to -22.5)
  - "Around circle" = Arc with radius ~17 units
  - "To blue line" = Move to x = ±25
  - "Outside the house" = x > -60 (away from net area)

### 4. Visual Language Patterns
Common drill descriptions map to specific implementations:
- "Queue at boards" → Position at y = ±38, spaced 5 units apart
- "Go around pylon" → Create waypoints before, at, and after obstacle
- "Wide loop" → Series of arc segments with smooth transitions
- "Intercept" → Convergence point with pressure line at end

### 5. Iteration Efficiency Improvements
To reduce iteration count:
1. **Start with correct z-order values** (see spec.md)
2. **Use polygon zones for equipment** from the start
3. **Place pucks beside queues**, not on players
4. **Show paths around obstacles** with explicit waypoints
5. **Use descriptive labels** on key movements

### 6. Natural Language to Diagram Mapping

#### Position Descriptions
- "Top corner" → Near boards at goal line (±85, ±38)
- "Bottom of circle" → Faceoff circle edge (~±69, ~±15)
- "Neutral zone" → Between blue lines (-25 to 25)
- "Slot area" → Front of net (~±69, ±10)

#### Movement Descriptions  
- "Cross ice and back" → Diagonal path with Y-axis emphasis
- "Loop around cone" → Arc segments with labeled waypoint
- "Backcheck" → Return path with angling component
- "Breakout" → Movement from defensive zone past blue line

### 7. Reusable Components

#### From hockey_diagram_builder.py
- Player type handlers (forward, defense, goalie, coach, puck)
- Movement renderers (carry, pass, shot, skate, pressure)
- Zone/equipment support (rectangle, circle, polygon)

#### From drill_utilities.py
```python
# Arc generation for any curved path
generate_arc_points(center_x, center_y, radius, start_angle, end_angle)

# Standard positions
STANDARD_POSITIONS = {
    'left_corner_top': (-85, 38),
    'left_corner_bottom': (-85, -38),
    'left_circle_center': (-69, 22.5),
    # ... etc
}

# Consistent z-ordering
Z_ORDER = {
    'zone': 6,
    'movement': 8,
    'player': 10,
    'equipment': 11,
    'goalie': 12
}
```

### 8. Common Gotchas to Avoid
1. **Don't place equipment at player positions** - Offset them slightly
2. **Don't use straight lines for skating around objects** - Use waypoints
3. **Don't forget counterclockwise adjustment** in arc generation (add 360° if needed)
4. **Don't put text labels at same z-order as objects** - Labels need +1 or +2

### 9. User Communication Tips
Instead of asking for exact coordinates:
- Ask: "Where does the player go?" (e.g., "to far circle", "across ice")
- Ask: "What are they doing?" (e.g., "loop around cone", "intercept at blue line")
- Ask: "Where do they end up?" (e.g., "in front of net", "at boards")

Then map these descriptions to coordinates using the landmark reference system.

### 10. Testing Approach
For each new drill:
1. Place all equipment first and verify visibility
2. Add player starting positions
3. Create primary movement path
4. Add secondary movements
5. Verify intersections/interactions
6. Add annotations last

This order minimizes rework from z-order issues and ensures core elements work before adding details.