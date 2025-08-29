# Gap Fix Plan - Hockey Diagram MCP v2

## Fix Categories
- **INSTRUCTION**: Update hockey-diagram-expert.md agent instructions
- **TOOL**: Modify MCP tools or schemas
- **BOTH**: Changes to both instructions and tools

## Gap Fixes by Priority

### 🔴 CRITICAL GAPS

#### Gap 1: Missing Drill Analysis Framework
**Type:** INSTRUCTION  
**Fix:** Add new Step 1.5 after "Analyze & Understand" with structured analysis:
- Zone usage analysis table
- Player journey tracking table  
- Movement validation checklist

#### Gap 2: Waypoint Format Inconsistency  
**Type:** TOOL
**Fix:** Modify `calculate_waypoints()` in position_mapper.py to return array format:
```python
# Change from: [{"x": -55, "y": 22.5}]
# To: [[-55, 22.5]]
```

#### Gap 3: Missing Trace/Logging Integration
**Type:** INSTRUCTION
**Fix:** Add trace initialization example in Step 2:
```python
from auto_trace_logger import start_session
session_id = start_session(drill_request)
```

### 🟡 MODERATE GAPS

#### Gap 4: Limited Player Type Support
**Type:** TOOL
**Fix:** Update diagram_schemas.py:
- Add 'puck' to PLAYER_TYPES enum
- Update PLAYER_SCHEMA to make has_puck optional for puck type

#### Gap 5: Missing Zone Type Examples  
**Type:** INSTRUCTION
**Fix:** Add polygon zone examples for pylons:
```json
{
  "type": "cone",
  "shape": "polygon", 
  "vertices": [[-15, -12], [-17, -17], [-13, -17]]
}
```

#### Gap 6: No Metadata Structure
**Type:** INSTRUCTION  
**Fix:** Add metadata template to Step 4:
```json
"metadata": {
  "created": "ISO timestamp",
  "category": "drill type",
  "age_group": "U11",
  "skill_focus": "skating"
}
```

### 🟢 MINOR GAPS

#### Gap 7: Missing Queue Position References
**Type:** TOOL
**Fix:** Add to position_mapper.py OFFENSIVE_POSITIONS:
```python
"left queue": (-20, -38),
"right queue": (20, 38),
"neutral queue left": (10, 38),
"neutral queue right": (10, -38)
```

#### Gap 8: No Multi-Phase Drill Support
**Type:** INSTRUCTION
**Fix:** Add section on multi-phase drills:
- Use movement labels: "Phase 1: Setup", "Phase 2: Execute"
- Group movements by phase in spec

#### Gap 9: Limited Annotation Positioning  
**Type:** INSTRUCTION
**Fix:** Add annotation positioning guide:
```json
{
  "text": "Key point",
  "position": {"x": 0, "y": -40},  // Specific y-coords
  "anchor": "middle"  // left|middle|right
}
```

## Implementation Order

1. **TOOL fixes first** (Gaps 2, 4, 7) - Update schemas and mappers
2. **INSTRUCTION fixes second** (Gaps 1, 3, 5, 6, 8, 9) - Update agent instructions
3. **Test integration** - Verify all changes work together

## Files to Modify

### Tool Files:
- `position_mapper.py` - Gaps 2, 7
- `diagram_schemas.py` - Gap 4
- `hockey_diagram_mcp_v2.py` - Gap 2 (if needed)

### Instruction Files:
- `hockey-diagram-expert.md` - Gaps 1, 3, 5, 6, 8, 9
- Copy to `.claude/agents/` after updates

## Validation Tests

After fixes, test with:
1. Simple give-and-go drill (basic validation)
2. Multi-phase breakout drill (complex validation)
3. 3v3 battle with pylons (zone shapes)
4. Drill with pucks and queues (new types)