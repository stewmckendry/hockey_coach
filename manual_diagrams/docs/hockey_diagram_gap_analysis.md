# Hockey Diagram MCP v2 Gap Analysis

## Executive Summary
Comparison between current hockey-diagram-expert.md agent instructions/MCP tools vs previous versions and successful drill implementations reveals several gaps categorized by criticality.

## Analysis Sources
1. **Previous Agent Instructions**: backup/hockey-diagram-expert-20250828-141631.md
2. **Successful Drill Scripts**: drill4_3v3_battle.py, drill2_backcheck_angling.py
3. **Recent JSON Specs**: drill_u11_skating_warmup_spec.json, drill1_crossovers_pass_final_spec.json
4. **Current Implementation**: hockey-diagram-expert.md, hockey_diagram_mcp_v2.py

## Gap Analysis by Criticality

### 🔴 CRITICAL GAPS (High Impact on Diagram Quality)

#### 1. Missing Drill Analysis Framework
**Previous Version Had:**
```markdown
### 1.5 Drill Analysis Framework (MANDATORY BEFORE COORDINATES)
A. Zone Usage Analysis
B. Player Journey Table
C. Movement Validation
```
**Current Version:** No structured analysis framework before building spec
**Impact:** Leads to misunderstanding drill requirements and incorrect positioning
**Fix Required:** Add mandatory drill analysis step before Step 4 in current instructions

#### 2. Waypoint Format Inconsistency
**Successful Specs Use:**
```json
"waypoints": [[-55, 22.5], [-25, 20], [0, 15]]  // Array of arrays
```
**Current MCP Returns:**
```json
"waypoints": [{"x": -55, "y": 22.5}]  // Array of objects
```
**Impact:** Generated specs may fail validation or rendering
**Fix Required:** Update movement schema and waypoint generation to match expected format

#### 3. Missing Trace/Logging Integration
**Previous Version Had:**
```python
from agent_trace_logger import start_trace, log_agent_thought
logger = start_trace(description)
```
**Current Version:** References trace in Step 7 but no initialization
**Impact:** No retrospective analysis capability
**Fix Required:** Add trace initialization in Step 2

### 🟡 MODERATE GAPS (Affects Efficiency)

#### 4. Limited Player Type Support
**Successful Specs Have:**
- `type: 'puck'` for puck markers
- `type: 'coach'` for coaches
**Current Schema:** Only forward/defense/goalie/coach
**Impact:** Cannot represent pucks as visual elements on ice
**Fix Required:** Extend PLAYER_TYPES enum

#### 5. Missing Zone Type Examples
**Successful Specs Use:**
```python
Zone(type='cone', shape='polygon', 
     bounds={'vertices': [(-15, -12), (-17, -17), (-13, -17)]})
```
**Current Instructions:** No polygon/vertices examples
**Impact:** Agent may not know how to create triangular pylons
**Fix Required:** Add zone shape examples to instructions

#### 6. No Metadata Structure
**Successful Specs Include:**
```json
"metadata": {
  "created": "2025-08-28T09:43:17",
  "category": "skating_warm_up",
  "age_group": "U11",
  "player_count": "6-8"
}
```
**Current Instructions:** No metadata guidance
**Impact:** Missing contextual information
**Fix Required:** Add metadata template

### 🟢 MINOR GAPS (Nice to Have)

#### 7. Missing Queue Position References
**Previous Version Had:**
```python
'left_queue': {'x': -20, 'y': -38}
'neutral_queue_left': {'x': 10, 'y': 38}
```
**Current Version:** No queue positions in mapping tools
**Impact:** Manual calculation needed for player queues

#### 8. No Multi-Phase Drill Support
**Successful Drills:** Often have Phase 1, Phase 2 movements
**Current Instructions:** Single-phase assumption
**Impact:** Complex drills harder to represent

#### 9. Limited Annotation Positioning
**Successful Specs:** Place annotations at specific y-coordinates
**Current Instructions:** Basic annotation array
**Impact:** Less control over text placement

## Recommended Priority Actions

### Immediate (Critical)
1. **Add Drill Analysis Framework** to Step 1 of agent instructions
2. **Fix waypoint format** in map_movement_to_coordinates tool
3. **Add trace initialization** example in Step 2

### Short-term (Moderate)
4. **Extend player types** in diagram_schemas.py
5. **Add zone shape examples** to instructions
6. **Include metadata template** in build spec section

### Long-term (Minor)
7. Add queue positions to position_mapper.py
8. Document multi-phase drill patterns
9. Enhance annotation positioning guidance

## Validation Checklist

To ensure complete coverage, generated diagrams should:
- [ ] Use consistent waypoint format (array of arrays)
- [ ] Include drill analysis before coordinates
- [ ] Support all player types including pucks
- [ ] Handle polygon zones for pylons
- [ ] Include complete metadata
- [ ] Initialize trace logging
- [ ] Map queue positions correctly
- [ ] Support multi-phase drills
- [ ] Position annotations precisely

## Code Examples Needed

### 1. Drill Analysis Template
```markdown
**Zone Analysis:**
- Primary zone: offensive
- Crosses blue line: yes/no
- View required: full/half/offensive

**Player Journey:**
| Player | Start | Actions | End | Type |
|--------|-------|---------|-----|------|
| F1 | left dot | pass, skate | slot | MOVING |
```

### 2. Waypoint Conversion
```python
# Convert object waypoints to array format
waypoints_array = [[wp["x"], wp["y"]] for wp in waypoints_dict]
```

### 3. Puck Representation
```json
{
  "type": "puck",
  "position": "P1",
  "coordinates": {"x": -70, "y": -38},
  "team": "neutral"
}
```

## Success Metrics

A successful implementation should:
1. Generate correct diagrams on first attempt 80% of the time
2. Support all drill types from examples
3. Produce valid JSON matching the rendering schema
4. Include all visual elements (players, pucks, pylons, zones)
5. Maintain spatial accuracy and hockey sense