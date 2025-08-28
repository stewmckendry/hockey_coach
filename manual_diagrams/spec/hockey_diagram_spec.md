# Hockey Diagram Specification v1.0

## Overview
This specification defines the structure and elements used to create hockey tactical diagrams programmatically. The spec evolves with each iteration based on real coaching needs.

## Diagram Structure

### 1. Rink Configuration
```json
{
  "view": "full | offensive | defensive | neutral | half",
  "orientation": "horizontal | vertical",
  "show_zones": true | false,
  "show_faceoff_dots": true | false,
  "show_grid": false | true
}
```

### 2. Player Elements (Based on Hockey Canada Template)

#### Player Types
- **Coach**: `©` - Circle with C
- **Forwards**: `○` - Open circle (can add F1, F2, F3 labels)
- **Defenders**: `△` - Triangle (can add D1, D2 labels)
- **Goaltenders**: `◐` - Half-filled circle with G
- **X Players**: `X` - Opposition players (X1-X5)
- **Pucks**: `●` - Solid black circle

#### Player Object
```json
{
  "type": "forward | defense | goalie | coach | opponent",
  "position": "C | LW | RW | LD | RD | G | X1-X5",
  "coordinates": {"x": 0, "y": 0},
  "team": "home | away",
  "has_puck": false,
  "label": "optional custom label",
  "number": null
}
```

### 3. Movement Elements

#### Movement Types (Hockey Canada Legend)
- **Puck Carrying**: `———>` - Solid arrow line
- **Shooting**: `---->` - Dashed arrow line
- **Pass**: `• • • >` - Dotted arrow line
- **Drop Pass**: `◐—>` - Solid with hook
- **Backward Skate**: `〜〜〜` - Wavy line
- **Lateral Movement**: `←→` - Double arrow
- **Defensive Pressure**: `====` - Thick solid line

#### Movement Object
```json
{
  "type": "carry | pass | shot | drop_pass | skate | backward | lateral | pressure",
  "from": {"x": 0, "y": 0} | "player_id",
  "to": {"x": 0, "y": 0} | "player_id",
  "style": "solid | dashed | dotted | wavy",
  "with_puck": false,
  "label": "optional label"
}
```

### 4. Zone Elements

#### Zone Types
- **Coverage zones**: Semi-transparent overlays showing defensive responsibility
- **Pressure zones**: Areas of forechecking pressure
- **Passing lanes**: Corridors for puck movement

#### Zone Object
```json
{
  "type": "coverage | pressure | lane",
  "shape": "rectangle | circle | polygon",
  "bounds": {"x": 0, "y": 0, "width": 0, "height": 0},
  "team": "home | away",
  "opacity": 0.2,
  "color": "blue | red | yellow",
  "label": "Zone A"
}
```

### 5. Annotations

#### Text Annotations
```json
{
  "text": "Power Play Setup",
  "position": {"x": 0, "y": -50},
  "size": "small | medium | large",
  "style": "normal | bold"
}
```

#### Drill Markers
- **Cones**: `▲` - Orange triangles
- **Pylons**: `|` - Vertical lines
- **Stop signs**: `⬢` - Hexagon

### 6. Complete Diagram Schema
```json
{
  "title": "2-1-2 Forecheck",
  "rink": { /* Rink configuration */ },
  "players": [ /* Array of player objects */ ],
  "movements": [ /* Array of movement objects */ ],
  "zones": [ /* Array of zone objects */ ],
  "annotations": [ /* Array of text/markers */ ],
  "metadata": {
    "created": "2025-01-27",
    "category": "forecheck | breakout | powerplay | penalty_kill | drill",
    "age_group": "U11 | U13 | U15 | U18",
    "skill_level": "beginner | intermediate | advanced"
  }
}
```

## Coordinate System
- Origin (0, 0) at center ice
- X-axis: -100 (left) to +100 (right) 
- Y-axis: -42.5 (bottom) to +42.5 (top)
- Standard NHL rink dimensions (200' x 85')

## Evolution Notes
This specification will evolve with each diagram iteration:
- New movement types will be added as needed
- Zone definitions will expand based on coaching patterns
- Player positioning presets will grow from common formations

### Key Implementation Learnings (Drill 1 - 16 iterations)

#### 1. Z-Order Layering
All elements need explicit z-order values to appear above the sportypy rink surface:
- Rink surface: z-order 0-5 (provided by sportypy)
- Coverage zones: z-order 6 (background areas with low opacity)
- Movement lines: z-order 8-9
- Player markers: z-order 10
- Equipment (cones/pylons): z-order 11 (should be visible above players)
- Pucks: z-order 10 (rendered as simple black dots)
- Labels/text: z-order 11 (regular players), z-order 13 (goalie)
- Goalie: z-order 12 (higher than regular players to ensure visibility on crease)

#### 2. Arc Generation for Circular Movements
Critical for counterclockwise movement around circles:
```python
def generate_arc_points(center_x, center_y, radius, start_angle, end_angle, num_points=15):
    # IMPORTANT: If end_angle <= start_angle, add 360° for counterclockwise
    if end_angle <= start_angle:
        end_angle += 360
    angles = np.linspace(np.radians(start_angle), np.radians(end_angle), num_points)
    x_points = center_x + radius * np.cos(angles)
    y_points = center_y + radius * np.sin(angles)
    return [(float(x), float(y)) for x, y in zip(x_points, y_points)]
```

#### 3. Angle Reference System
Standard mathematical coordinates used:
- 0° = Right side (positive x-axis)
- 90° = Top (positive y-axis)  
- 180° = Left side (negative x-axis)
- 270° = Bottom (negative y-axis)

#### 4. Player Positioning Guidelines
- Queue spacing: 5 units apart horizontally
- Off-board positioning: ~38 units from center (not 42 at boards)
- Coach positions: Near boards at ~y=35/-35 (not at face-off dots)
- Goalie positions: x=±83 (in crease, not behind net)

#### 5. Movement Path Best Practices
- Use tangential entry/exit for natural flow
- Calculate intermediate points along trajectories for pass/receive
- Offset entry angles to prevent path overlap (e.g., 315° vs 270°)
- Arc radius slightly outside face-off circle (17 units vs 15)

#### 6. New Player Type Addition
- **Drill Group**: Players marked with 'X' for drill queues (distinct from opponents)
  - Notation: X1, X2 for lead players, X for queue members

### Key Implementation Learnings (Drill 2 - 9 iterations)

#### 7. Equipment Representation
- **Pylons/Cones**: Use polygon zones with triangle vertices for realistic appearance
  - Fill with solid color (darkorange) at opacity 1.0
  - Z-order 11 ensures visibility above players
  - Example vertices for cone: `[(-15, -12), (-17, -17), (-13, -17)]`

#### 8. Cross-Ice Movement
- Cross-ice paths require significant Y-axis changes (e.g., from +38 to -22.5)
- The Y-axis shift creates the visual cross-ice movement pattern
- X-axis changes alone won't show proper cross-ice movement

#### 9. Puck Representation
- Use dedicated 'puck' player type rendered as simple black dots
- No additional circles or decorations needed
- Place beside player queues for clarity

#### 10. Path Around Obstacles
- When players go around pylons, create explicit waypoints
- Use dashed lines for the curved portion around obstacles
- Label key movements like "Around pylon" at appropriate segments

#### 11. Intercept Points
- Blue line intercepts occur around x=-45 (outside the "house")
- Defensive engagement should be clearly marked with pressure lines
- Final defensive position matters for drill clarity

### Key Implementation Learnings (Drill 3 - 2 iterations)

#### 12. Multi-Part Drills
- Separate diagrams for different phases (e.g., breakout vs break-in)
- Clear sequential numbering for step-by-step progressions
- Label movement options with A/B/C for alternative plays

#### 13. Defensive Reactions
- Show defensive movements with different line styles
- Use "pressure" movement type for defensive engagement
- Position defensive players to show coverage concepts

### Key Implementation Learnings (Drill 4 - 4 iterations)

#### 14. Custom View Support
- Added custom rink view with xlim/ylim parameters:
```json
{
  "view": "custom",
  "xlim": [0, 100],
  "ylim": [-42.5, 42.5]
}
```

#### 15. Multiple Nets Setup
- Second net can be represented using zone rectangles
- Layer multiple zones for realistic net appearance:
  - Dark red rectangle for frame (opacity 0.9)
  - White rectangle for opening (opacity 0.8)
  - Gray rectangle for mesh (opacity 0.3)

#### 16. Player Queues in Neutral Zone
- Position queues at x=10 (neutral zone)
- Separate home/away queues on opposite sides
- 4-unit vertical spacing between queue players

#### 17. Simplified Diagrams
- Remove movement lines for cleaner setup diagrams
- Show only positioning and equipment
- Let drill dynamics be explained verbally

#### 18. Zone-Based Drills
- Small area games benefit from zone boundaries
- Use multiple coaches as passing stations
- Both goalies face same direction (toward offensive end)

## Version History
- v1.0 (2025-01-27): Initial specification based on Hockey Canada template legend
- v1.1 (2025-01-27): Added implementation details from Drill 1 development
- v1.2 (2025-01-27): Added learnings from Drill 2 (equipment, cross-ice movement, pucks)
- v1.3 (2025-01-27): Added learnings from Drills 3-4 (multi-part drills, custom views, multiple nets)