# Hockey Diagram Architecture Plan: Zone-Based Dynamic System

## Overview

This document outlines the implementation plan for enhancing the Hockey Diagram MCP Server with a zone-based architecture combined with dynamic coach control capabilities. The system will provide precise positioning through ice zones while allowing coaches to describe any formation, play, or drill using natural language.

## Architecture Components

### 1. Zone-Based Positioning System (Foundation Layer)

#### Ice Surface Zone Grid
The ice surface is divided into named zones providing 100% coverage:

**Defensive Zone (12 zones)**
```
| def-left-corner  | def-behind-net-left  | def-behind-net-right | def-right-corner |
| def-low-left     | def-crease-left      | def-crease-right     | def-low-right    |
| def-mid-left     | def-low-slot         | def-high-slot        | def-mid-right    |
| def-high-left    | def-high-slot-left   | def-high-slot-right  | def-high-right   |
```

**Neutral Zone (8 zones)**
```
| neu-left-boards  | neu-left-center  | neu-right-center | neu-right-boards |
| neu-left-mid     | neu-center-dot   | neu-center-ice   | neu-right-mid    |
```

**Offensive Zone (12 zones)**
```
| off-high-left    | off-high-slot-left   | off-high-slot-right  | off-high-right   |
| off-mid-left     | off-high-slot        | off-low-slot         | off-mid-right    |
| off-low-left     | off-crease-left      | off-crease-right     | off-low-right    |
| off-left-corner  | off-behind-net-left  | off-behind-net-right | off-right-corner |
```

#### Zone Properties
Each zone contains:
- `center`: (x, y) coordinates of zone center
- `bounds`: (x_min, y_min, x_max, y_max) zone boundaries
- `adjacent_zones`: List of neighboring zones
- `common_roles`: Typical positions that occupy this zone

### 2. Dynamic Interpretation Layer (Intelligence)

#### Multi-Stage Processing Pipeline
1. **Intent Extraction**: Parse coach request to identify diagram type and key concepts
2. **Research Integration**: Query knowledge sources when concepts are unknown
3. **Zone Mapping**: Convert researched positions to zone placements
4. **Feedback Learning**: Apply previous corrections and coach preferences

#### Knowledge Sources
- **Base Patterns**: Small library of common formations (not exhaustive)
- **MCP Tools**: `search_hockey_tactics`, `search_hockey_drills` for hockey-specific knowledge
- **Web Search**: Exa API for formations/plays not in local knowledge
- **Diagram History**: Previous diagrams and coach corrections

### 3. Coach Feedback System (Adaptation)

#### Feedback Processing
- Natural language position adjustments ("move D1 closer to net")
- Zone-based corrections ("put wingers on half-walls")
- Offset modifications ("shift center 5 feet left")
- Coverage area adjustments ("extend defensive coverage to neutral zone")

#### Learning Mechanism
- Pattern recognition from corrections
- Coach preference profiles
- Context-aware adjustments
- Iterative refinement within session

## Implementation Phases

### Phase 1: Zone Infrastructure (Week 1)
1. **Create Zone Grid System**
   - Define all 32 zones with coordinates and boundaries
   - Implement `ZoneGrid` class with zone lookup and offset calculations
   - Add zone relationship mappings (adjacency, passing lanes)

2. **Update Coordinate Mapper**
   - Replace position-based coordinates with zone-based system
   - Implement `get_zone_position(zone_name, offset_x, offset_y)` method
   - Maintain backward compatibility with existing formations

3. **Enhance Generator**
   - Update zone rendering to use new zone boundaries
   - Implement smooth coverage area rendering across multiple zones
   - Add zone-based movement path calculations

### Phase 2: Research Integration (Week 2)
1. **Research Module**
   ```python
   class HockeyResearcher:
       async def research_formation(self, name: str) -> FormationSpec
       async def research_drill(self, name: str) -> DrillSpec
       async def research_play(self, name: str) -> PlaySpec
   ```

2. **MCP Tool Integration**
   - Connect to `hockey-coaching` MCP server
   - Implement search result parsing
   - Extract positioning information from text

3. **Fallback to Web Search**
   - Exa API integration for unknown concepts
   - Parse web results for hockey positioning data

### Phase 3: Dynamic Parser Enhancement (Week 3)
1. **Enhanced Two-Stage Parser**
   - Stage 1: Concept extraction with research triggers
   - Stage 2: Zone-based position mapping
   - Context-aware role selection

2. **Unknown Concept Handling**
   ```python
   if formation not in known_formations:
       research_results = await researcher.research_formation(formation)
       zone_mapping = extract_zone_mapping(research_results)
   ```

3. **Flexible Interpretation**
   - Handle partial specifications ("2-1-2 but with aggressive F1")
   - Support modifications ("standard box +1 in slot")

### Phase 4: Feedback System (Week 4)
1. **Feedback Parser**
   ```python
   class FeedbackProcessor:
       def parse_position_adjustment(feedback: str) -> PositionDelta
       def parse_zone_change(feedback: str) -> ZoneChange
       def parse_coverage_adjustment(feedback: str) -> CoverageChange
   ```

2. **Session Management**
   - Track diagram iterations
   - Store feedback history
   - Apply cumulative adjustments

3. **Learning Database**
   - Store successful patterns
   - Track coach preferences
   - Build correction library

### Phase 5: Integration & Testing (Week 5)
1. **End-to-End Testing**
   - Test unknown formation research
   - Verify feedback processing
   - Validate zone positioning accuracy

2. **Performance Optimization**
   - Cache research results
   - Optimize zone calculations
   - Minimize API calls

## Technical Architecture

### Core Classes

```python
# Zone System
class ZoneGrid:
    def get_zone(self, zone_name: str) -> Zone
    def get_position(self, zone_name: str, offset: Tuple[float, float]) -> Tuple[float, float]
    def get_zones_between(self, start: str, end: str) -> List[str]
    def get_coverage_zones(self, position: str, formation: str) -> List[str]

# Research System  
class DiagramInterpreter:
    def __init__(self, researcher: HockeyResearcher, zone_grid: ZoneGrid)
    async def interpret_request(self, prompt: str, context: dict) -> DiagramSpec
    def apply_feedback(self, current_spec: DiagramSpec, feedback: str) -> DiagramSpec

# Feedback System
class DiagramSession:
    def __init__(self, interpreter: DiagramInterpreter)
    async def generate(self, prompt: str) -> Diagram
    async def refine(self, feedback: str) -> Diagram
    def get_history(self) -> List[DiagramIteration]
```

### API Flow Example

```python
# Coach request: "Show me a neutral zone trap that I saw in the NHL"
session = DiagramSession()

# Initial generation
diagram = await session.generate("neutral zone trap NHL style")
# -> Researches "neutral zone trap NHL"
# -> Finds 1-3-1 or 1-2-2 formations
# -> Places players in appropriate zones
# -> Returns diagram

# Coach feedback
diagram = await session.refine("Move the forwards closer together")
# -> Adjusts F1, F2, F3 positions toward center zones
# -> Maintains formation structure
# -> Returns updated diagram

# Further refinement
diagram = await session.refine("Add forechecking pressure arrows")
# -> Adds movement indicators
# -> Returns final diagram
```

## Success Metrics

1. **Accuracy**: 90% of generated diagrams require ≤2 refinements
2. **Coverage**: Can handle any formation/drill/play described in natural language
3. **Learning**: Repeated requests improve without explicit feedback
4. **Performance**: Diagram generation <5 seconds including research

## Migration Strategy

1. **Backward Compatibility**: Existing presets continue working
2. **Gradual Enhancement**: Add zone system alongside current system
3. **Feature Flags**: Enable research/feedback features progressively
4. **Data Migration**: Convert existing formations to zone-based specs

## Example Use Cases

### Use Case 1: Unknown Formation
**Coach**: "Show me a Swedish torpedo forecheck"
**System**: 
1. Searches MCP/web for "Swedish torpedo forecheck"
2. Learns it's an aggressive 2-1-2 with both D pinching
3. Places players in appropriate offensive zones
4. Generates diagram

### Use Case 2: Custom Drill
**Coach**: "Create a 3-station passing drill using all three zones"
**System**:
1. Identifies "3-station", "passing drill", "three zones"
2. Places stations in def-high-slot, neu-center, off-high-slot
3. Adds passing movement indicators
4. Generates diagram

### Use Case 3: Iterative Refinement
**Coach**: "Show defensive zone coverage"
**System**: Generates standard box coverage
**Coach**: "Move wingers higher to cover points"
**System**: 
1. Identifies wingers (F1, F2)
2. Moves from def-mid zones to def-high zones
3. Adjusts coverage areas
4. Regenerates diagram

## Next Steps

1. **Immediate**: Fix current test case issues (zone rendering, D positioning)
2. **Week 1**: Implement zone grid system
3. **Week 2**: Add research capabilities
4. **Week 3**: Enhance parser with dynamic interpretation
5. **Week 4**: Build feedback system
6. **Week 5**: Integration and testing

## Conclusion

This architecture combines the precision of a zone-based positioning system with the flexibility of dynamic interpretation and coach feedback. It transforms the hockey diagram generator from a static tool into an intelligent assistant that learns and adapts to each coach's needs while maintaining accurate hockey positioning and tactics.