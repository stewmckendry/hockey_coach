# Hockey Position Schemas v2.0

Complete reference of all position mappings used by the MCP tools.

## Offensive Zone Positions (x > 25)

### Faceoff Formations

#### Offensive Left Dot (69, 22.5)
**Home Team (attacking)**
- `offensive left faceoff home center`: (67, 22.5) - Left of dot
- `offensive left faceoff home left wing`: (67, 37) - Outside circle  
- `offensive left faceoff home right wing`: (67, 7.5) - Hashmark on circle
- `offensive left faceoff home left defense`: (40, 38) - Point position
- `offensive left faceoff home right defense`: (40, 0) - High slot

**Away Team (defending)**
- `offensive left faceoff away center`: (71, 22.5) - Right of dot
- `offensive left faceoff away left wing`: (71, 7.5) - Hashmark (opposite side)
- `offensive left faceoff away right wing`: (71, 37) - Outside (opposite side)
- `offensive left faceoff away left defense`: (85, 7.5) - Back position
- `offensive left faceoff away right defense`: (85, 37) - Back wide

#### Offensive Right Dot (69, -22.5)
**Home Team (attacking)**
- `offensive right faceoff home center`: (67, -22.5)
- `offensive right faceoff home left wing`: (67, -7.5)
- `offensive right faceoff home right wing`: (67, -37)
- `offensive right faceoff home left defense`: (40, 0)
- `offensive right faceoff home right defense`: (40, -38)

**Away Team (defending)**
- `offensive right faceoff away center`: (71, -22.5)
- `offensive right faceoff away left wing`: (71, -37)
- `offensive right faceoff away right wing`: (71, -7.5)
- `offensive right faceoff away left defense`: (85, -37)
- `offensive right faceoff away right defense`: (85, -7.5)

### Slot Positions

#### High Slot (x=47)
- `high slot`: (47, 0)
- `high slot middle`: (47, 0)
- `high slot left`: (47, 20)
- `high slot right`: (47, -20)

#### Mid Slot (x=69)
- `slot` / `mid slot`: (69, 0)
- `mid slot middle`: (69, 0)
- `mid slot left`: (69, 20)
- `mid slot right`: (69, -20)

#### Low Slot (x=79)
- `low slot`: (79, 0)
- `low slot middle`: (79, 0)
- `low slot left`: (79, 20)
- `low slot right`: (79, -20)

### Point Positions (x=30)
- `point` / `point middle`: (30, 0)
- `point left`: (30, 20)
- `point right`: (30, -20)
- `point left boards`: (30, 38)
- `point right boards`: (30, -38)

### Net Area
- `goalie` / `offensive goalie`: (89, 0)
- `net front` / `crease`: (83, 0)
- `crease left`: (83, 4)
- `crease right`: (83, -4)
- `left post`: (89, 3)
- `right post`: (89, -3)
- `behind net`: (92, 0)

### Corners & Walls
- `left corner` / `offensive left corner`: (89, 36)
- `right corner` / `offensive right corner`: (89, -36)
- `left half wall` / `offensive left half wall`: (69, 36)
- `right half wall` / `offensive right half wall`: (69, -36)
- `offensive left boards`: (50, 40)
- `offensive right boards`: (50, -40)

### Blue Line
- `offensive blue line center`: (25, 0)
- `offensive blue line left`: (25, 20)
- `offensive blue line right`: (25, -20)

## Defensive Zone Positions (x < -25)

### Faceoff Formations

#### Defensive Left Dot (-69, 22.5)
**Home Team (defending)**
- `defensive left faceoff home center`: (-67, 22.5)
- `defensive left faceoff home left wing`: (-67, 7.5)
- `defensive left faceoff home right wing`: (-67, 37)
- `defensive left faceoff home left defense`: (-85, 7.5)
- `defensive left faceoff home right defense`: (-85, 37)

**Away Team (attacking)**
- `defensive left faceoff away center`: (-71, 22.5)
- `defensive left faceoff away left wing`: (-71, 37)
- `defensive left faceoff away right wing`: (-71, 7.5)
- `defensive left faceoff away left defense`: (-40, 38)
- `defensive left faceoff away right defense`: (-40, 0)

#### Defensive Right Dot (-69, -22.5)
Similar pattern with y-values negated

### Defensive Slot Positions
- `defensive high slot`: (-47, 0) with left/right variations
- `defensive mid slot`: (-69, 0) with left/right variations
- `defensive low slot`: (-79, 0) with left/right variations

### Defensive Point Positions
- `defensive point`: (-30, 0) with 5 variations

### Defensive Net Area
- `defensive goalie`: (-89, 0)
- `defensive crease`: (-83, 0)
- `defensive behind net`: (-92, 0)

### Defensive Corners & Walls
- `defensive left corner`: (-89, 36)
- `defensive right corner`: (-89, -36)
- `defensive left half wall`: (-69, 36)
- `defensive right half wall`: (-69, -36)

## Neutral Zone Positions

### Center Ice
- `center ice` / `center ice faceoff`: (0, 0)
- `center ice home center`: (-2, 0)
- `center ice away center`: (2, 0)
- `center ice home left wing`: (-2, 22.5)
- `center ice home right wing`: (-2, -22.5)
- `center ice away left wing`: (2, -22.5)
- `center ice away right wing`: (2, 22.5)
- `center ice home left defense`: (-20, 15)
- `center ice home right defense`: (-20, -15)
- `center ice away left defense`: (20, -15)
- `center ice away right defense`: (20, 15)

### Neutral Zone Dots
- `neutral left dot` / `offside left dot`: (20, 22.5)
- `neutral right dot` / `offside right dot`: (20, -22.5)
- `neutral left dot home`: (18, 22.5)
- `neutral left dot away`: (22, 22.5)

### Blue Lines
- `neutral zone offensive blue line`: (25, 0)
- `neutral zone defensive blue line`: (-25, 0)
- `red line` / `center line`: (0, 0)

### Bench Areas
- `home bench`: (0, -42.5)
- `away bench`: (0, 42.5)
- `penalty box home`: (-15, -42.5)
- `penalty box away`: (-15, 42.5)

## Special Positions

### Relative Positioning
Supports patterns like:
- "5 units left of F1"
- "between F1 and F2"
- "halfway between F1 and D1"
- "2/3 of the way from F1 to F2"
- "near F1" or "close to D1"

### Zone-Agnostic Aliases
- `left wing` → maps to appropriate zone
- `right defense` → maps to appropriate zone
- `center` → maps to appropriate zone
- `slot` → maps to mid slot in appropriate zone
- `point` → maps to center point in appropriate zone

## Coordinate System Reference

```
        -100                0                 100
         |------------------|------------------|
    42.5 +==================+===================+
         |    DEFENSIVE     |     OFFENSIVE     |
         |      ZONE        |       ZONE        |
         |                  |                   |
       0 +------------------+-------------------+
         |     x < -25      |      x > 25       |
         |                  |                   |
         |   Blue: x=-25    |    Blue: x=25     |
   -42.5 +==================+===================+
```

## Position Confidence Levels
- **1.0**: Exact match found in position dictionary
- **0.95**: LLM high-confidence interpretation
- **0.85**: Fuzzy match or partial string match
- **0.80**: LLM medium-confidence interpretation
- **0.75**: Best guess based on context

## Usage in MCP Tools

### Direct Access
```python
from position_mapper import OFFENSIVE_POSITIONS, DEFENSIVE_POSITIONS, NEUTRAL_POSITIONS

pos = OFFENSIVE_POSITIONS["slot"]  # Returns (69, 0)
```

### Via MCP Tool
```json
mcp__hockey_diagram__map_position_to_coordinates(
  position="high slot left",
  zone="offensive"
)
// Returns: {"coordinates": {"x": 47, "y": 20}, "confidence": 1.0}
```

### LLM Fallback
When position not found directly, LLM interprets using:
- Context clues from description
- Zone information
- Reference positions if provided
- Hockey domain knowledge