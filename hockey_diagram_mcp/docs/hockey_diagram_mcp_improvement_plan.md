# Hockey Diagram MCP Tools Improvement Plan & Specification

## Executive Summary

The current hockey diagram MCP tools struggle with accurately translating natural language hockey queries into correct positions and movements. This document outlines a comprehensive plan to create reliable, predictable diagram generation tools.

## Current State Analysis

### Core Issues Identified

1. **Position Mapping Inconsistencies**
   - Coordinate system confusion (offensive zone returns negative X values)
   - Hardcoded positions without contextual understanding
   - No relative positioning intelligence

2. **Natural Language Processing Gaps**
   - Cannot parse hockey notation (e.g., "2v1", "3v2")
   - Doesn't understand drill patterns (e.g., "give and go", "cycle")
   - No contextual awareness of hockey terminology

3. **Lack of Hockey Intelligence**
   - No understanding of common plays and formations
   - Missing drill pattern recognition
   - Cannot infer logical player positions from context

4. **Validation Weaknesses**
   - Over-reliance on LLM validation without structured checks
   - No pre-flight validation of hockey logic
   - Missing feedback loop for corrections

## Proposed Solution Architecture

### 1. Hockey Intelligence Layer

#### 1.1 Drill Pattern Recognition Engine
```python
class DrillPatternEngine:
    """Recognizes and decomposes hockey drill patterns"""
    
    patterns = {
        "2v1": {
            "players": {"offensive": 2, "defensive": 1},
            "typical_positions": {
                "offensive": ["left wing", "center"],
                "defensive": ["defense"]
            }
        },
        "give_and_go": {
            "movements": [
                {"type": "pass", "from": "puck_carrier", "to": "support"},
                {"type": "skate", "from": "puck_carrier", "to": "open_space"},
                {"type": "pass", "from": "support", "to": "puck_carrier"}
            ]
        },
        "cycle": {
            "zone": "offensive",
            "movements": "along_boards",
            "players_involved": 2
        }
    }
```

#### 1.2 Hockey Terminology Parser
```python
class HockeyTermParser:
    """Parses natural language hockey terms into structured data"""
    
    def parse_drill_notation(text: str) -> Dict:
        # "2v1 rush from neutral zone"
        # Returns: {
        #   "offensive_count": 2,
        #   "defensive_count": 1,
        #   "drill_type": "rush",
        #   "starting_zone": "neutral"
        # }
    
    def extract_positions(text: str) -> List[Dict]:
        # "F1 at the left dot, D1 at the point"
        # Returns structured position data
    
    def identify_movements(text: str) -> List[Dict]:
        # "pass to the slot then drive the net"
        # Returns movement sequence
```

### 2. Improved Position Mapping System

#### 2.1 Contextual Position Resolver
```python
class ContextualPositionResolver:
    """Resolves positions based on context and relative references"""
    
    def resolve_position(
        description: str,
        context: Dict,
        existing_positions: Dict[str, Tuple[float, float]]
    ) -> Tuple[float, float]:
        """
        Smart position resolution with:
        - Relative positioning ("left of F1", "between D1 and D2")
        - Zone awareness (offensive/defensive/neutral)
        - Contextual defaults (e.g., "wing" defaults based on drill)
        - Fuzzy matching with confidence scores
        """
```

#### 2.2 Coordinate System Standardization
```python
# Standardized coordinate system
COORDINATE_SYSTEM = {
    "x_range": (-100, 100),  # Left to right
    "y_range": (-42.5, 42.5),  # Bottom to top
    "zones": {
        "defensive": {"x": (-100, -25)},  # Left third
        "neutral": {"x": (-25, 25)},      # Middle third
        "offensive": {"x": (25, 100)}     # Right third
    },
    "orientation": "offensive_right"  # Offensive zone on right
}
```

### 3. Drill Decomposition Pipeline

#### 3.1 Multi-Stage Processing
```python
class DrillDecomposer:
    """Decomposes drill descriptions into diagram elements"""
    
    def process(self, drill_request: str) -> Dict:
        # Stage 1: Extract drill type and player counts
        drill_info = self.extract_drill_info(drill_request)
        
        # Stage 2: Identify zones and starting positions
        positions = self.determine_positions(drill_request, drill_info)
        
        # Stage 3: Extract movement patterns
        movements = self.extract_movements(drill_request, positions)
        
        # Stage 4: Add hockey-specific enhancements
        enhanced = self.apply_hockey_logic(positions, movements)
        
        return enhanced
```

#### 3.2 Hockey Logic Rules Engine
```python
class HockeyLogicEngine:
    """Applies hockey-specific rules and validations"""
    
    rules = [
        # Spatial rules
        "players_cannot_overlap",
        "maintain_realistic_spacing",
        
        # Movement rules
        "passes_require_clear_lanes",
        "shots_target_net",
        
        # Formation rules
        "defensive_players_protect_net",
        "offensive_players_create_space"
    ]
    
    def validate_and_fix(self, spec: Dict) -> Dict:
        """Validates and auto-corrects based on hockey logic"""
```

### 4. Enhanced MCP Tool Interface

#### 4.1 New Tool: analyze_drill_request
```python
@mcp.tool("analyze_drill_request")
def analyze_drill_request(drill_request: str) -> Dict:
    """
    Analyzes a drill request and returns structured interpretation.
    
    Args:
        drill_request: Natural language drill description
        
    Returns:
        {
            "drill_type": "2v1_rush",
            "player_requirements": {
                "offensive": 2,
                "defensive": 1
            },
            "zones_involved": ["neutral", "offensive"],
            "key_movements": ["rush", "pass", "shot"],
            "suggested_positions": [...],
            "suggested_movements": [...],
            "confidence": 0.95
        }
    """
```

#### 4.2 New Tool: validate_hockey_logic
```python
@mcp.tool("validate_hockey_logic")
def validate_hockey_logic(spec: Dict, drill_type: str) -> Dict:
    """
    Validates diagram spec against hockey rules.
    
    Returns:
        {
            "valid": true/false,
            "issues": [...],
            "auto_fixes": [...],
            "suggestions": [...]
        }
    """
```

#### 4.3 Improved Tool: map_position_to_coordinates
```python
@mcp.tool("map_position_to_coordinates")
def map_position_to_coordinates(
    position: str,
    zone: str = "offensive",
    context: Dict = None,
    reference_positions: Dict = None
) -> Dict:
    """
    Enhanced position mapping with context awareness.
    
    Returns:
        {
            "coordinates": {"x": 69, "y": 22.5},
            "confidence": 0.95,
            "alternatives": [...],
            "reasoning": "Matched 'left dot' to offensive left faceoff circle"
        }
    """
```

### 5. Testing and Validation Framework

#### 5.1 Test Suite Structure
```python
class HockeyDiagramTestSuite:
    """Comprehensive testing for diagram generation"""
    
    test_cases = {
        "basic_drills": [
            {
                "input": "2v1 rush",
                "expected": {
                    "players": 3,
                    "offensive": 2,
                    "defensive": 1
                }
            }
        ],
        "complex_drills": [...],
        "edge_cases": [...]
    }
    
    def run_tests(self) -> TestResults:
        """Runs all test cases and reports accuracy"""
```

#### 5.2 Diagnostic Tools
```python
@mcp.tool("diagnose_diagram_generation")
def diagnose_diagram_generation(
    drill_request: str,
    verbose: bool = True
) -> Dict:
    """
    Step-by-step diagnostic of diagram generation.
    
    Returns each processing stage with:
    - Input/output at each stage
    - Decisions made
    - Confidence scores
    - Alternative interpretations
    """
```

### 6. Implementation Phases

#### Phase 1: Foundation (Week 1)
- [ ] Fix coordinate system inconsistencies
- [ ] Standardize position mappings
- [ ] Create basic hockey terminology parser

#### Phase 2: Intelligence Layer (Week 2)
- [ ] Implement drill pattern recognition
- [ ] Build contextual position resolver
- [ ] Create hockey logic rules engine

#### Phase 3: Enhanced Tools (Week 3)
- [ ] Develop new analysis tools
- [ ] Improve existing mapping tools
- [ ] Add diagnostic capabilities

#### Phase 4: Testing & Refinement (Week 4)
- [ ] Build comprehensive test suite
- [ ] Run accuracy benchmarks
- [ ] Refine based on test results

## Success Metrics

1. **Accuracy**: 95% correct interpretation of common drill types
2. **Reliability**: Consistent results for same input
3. **Coverage**: Handle 50+ standard drill patterns
4. **Performance**: < 500ms processing time per request
5. **Debuggability**: Clear diagnostic output for failures

## Example Transformations

### Before (Current System)
```
Input: "2v1 rush from neutral zone"
Output: Confused positioning, wrong player counts, unclear movements
```

### After (Improved System)
```
Input: "2v1 rush from neutral zone"
Output: {
  "players": [
    {"id": "F1", "team": "home", "position": {"x": 0, "y": 20}},
    {"id": "F2", "team": "home", "position": {"x": 0, "y": -20}},
    {"id": "D1", "team": "away", "position": {"x": 40, "y": 0}}
  ],
  "movements": [
    {"type": "skate", "from": "F1", "to": {"x": 70, "y": 15}, "style": "rush"},
    {"type": "pass", "from": "F1", "to": "F2", "at": {"x": 50, "y": 0}},
    {"type": "shot", "from": "F2", "to": "net"}
  ]
}
```

## Risk Mitigation

1. **Backward Compatibility**: Maintain existing tool interfaces
2. **Gradual Rollout**: Test with subset of drills first
3. **Fallback Mechanisms**: Keep current system as backup
4. **Performance Impact**: Profile and optimize critical paths

## Conclusion

This improvement plan addresses the root causes of diagram generation issues by:
1. Adding hockey intelligence and context understanding
2. Fixing coordinate system inconsistencies
3. Implementing structured drill decomposition
4. Providing comprehensive testing and diagnostics

The phased approach ensures manageable implementation while delivering incremental improvements.