# Hockey Diagram v2 MCP Tools - Impact Assessment
## Atomic Pipeline Impact Analysis

## Current v2 Tools (11 tools)

1. `initialize_diagram` - Session initialization
2. `search_diagram_node` - Get node schemas
3. `search_diagram_template` - Find templates
4. `fetch_diagram_template` - Get template details
5. `validate_diagram_node_minimal` - Validate single node
6. `validate_diagram_spec_full` - Full spec validation with LLM
7. `preview_diagram` - ASCII/coordinate preview
8. `generate_diagram` - Final diagram generation
9. `map_position_to_coordinates` - Position to coordinate mapping
10. `map_movement_to_coordinates` - Movement path generation
11. `tools_health_check` - Server health check

## Impact Assessment by Tool

### 🔴 Tools to Replace/Remove

#### 1. `initialize_diagram`
- **Current**: Creates session and provides workflow instructions
- **Issue**: Too high-level, doesn't fit atomic pipeline
- **Replace with**: `analyze_query_gaps` + `generate_assumptions`
- **Impact**: HIGH - Core workflow change

#### 2. `search_diagram_node`
- **Current**: Returns schema for node types
- **Issue**: Too generic, not action-oriented
- **Replace with**: Built into specific extraction tools
- **Impact**: MEDIUM - Functionality absorbed elsewhere

#### 3. `validate_diagram_spec_full`
- **Current**: Monolithic validation with LLM
- **Issue**: Does too much in one step, expensive LLM call
- **Replace with**: Multiple atomic validators
  - `validate_position_spec`
  - `validate_movement_spec`
  - `validate_full_spec` (no LLM)
- **Impact**: HIGH - Major validation redesign

### 🟡 Tools to Modify

#### 4. `map_position_to_coordinates`
- **Current**: Maps single position to coordinates
- **Modify to**: `map_positions_to_coordinates` (batch processing)
- **Changes**:
  - Accept array of positions
  - Return confidence scores
  - Better error handling for unknown positions
- **Impact**: MEDIUM - API change but core logic retained

#### 5. `map_movement_to_coordinates`
- **Current**: Generates movement with waypoints
- **Modify to**: `map_movements_to_coordinates` (batch processing)
- **Changes**:
  - Process multiple movements
  - Separate path generation from validation
  - Return structured movement specs
- **Impact**: MEDIUM - Enhanced functionality

#### 6. `preview_diagram`
- **Current**: Preview full spec
- **Modify to**: Multiple preview tools
  - `preview_positions` - Just players
  - `preview_movements` - Movement overlay
  - `preview_full_diagram` - Complete preview
- **Impact**: MEDIUM - Split into atomic previews

#### 7. `validate_diagram_node_minimal`
- **Current**: Validates individual nodes
- **Modify to**: Specific validators
  - `validate_position_spec`
  - `validate_movement_spec`
  - `validate_additional_spec`
- **Impact**: LOW - More specific validation

### 🟢 Tools to Keep

#### 8. `generate_diagram`
- **Current**: Final diagram generation
- **Keep**: Core functionality unchanged
- **Minor updates**: Better error messages
- **Impact**: LOW - Minimal changes

#### 9. `search_diagram_template`
- **Current**: Template search
- **Keep**: Still useful for finding examples
- **Enhancement**: Tag templates by atomic components
- **Impact**: LOW - Optional enhancement

#### 10. `fetch_diagram_template`
- **Current**: Get template details
- **Keep**: Useful for learning patterns
- **Impact**: NONE - No changes needed

#### 11. `tools_health_check`
- **Current**: Health check
- **Keep**: Always useful
- **Impact**: NONE - No changes needed

## New Tools Required (18 total)

### Gap Analysis & Assumptions (2 tools)
1. ✅ `analyze_query_gaps` - Identify missing information
2. ✅ `generate_assumptions` - Create smart defaults

### Extraction Tools (3 tools - LLM)
3. ✅ `extract_player_positions` - Get player positions
4. ✅ `extract_movements` - Get movement patterns
5. ✅ `extract_additional_elements` - Get rink view, equipment

### Mapping Tools (3 tools)
6. 🔄 `map_positions_to_coordinates` - Batch position mapping (modified from v2)
7. 🔄 `map_movements_to_coordinates` - Batch movement mapping (modified from v2)
8. ✅ `map_additional_to_spec` - Map additional elements

### Spec Creation Tools (3 tools)
9. ✅ `create_position_spec` - Build player specification
10. ✅ `create_movement_spec` - Build movement specification
11. ✅ `create_additional_spec` - Build additional elements spec

### Validation Tools (3 tools)
12. ✅ `validate_position_spec` - Check player positions
13. ✅ `validate_movement_spec` - Check movements
14. ✅ `validate_full_spec` - Check complete diagram

### Preview Tools (3 tools)
15. ✅ `preview_positions` - Show player positions
16. ✅ `preview_movements` - Show movement overlay
17. 🔄 `preview_full_diagram` - Complete preview (modified from v2)

### Assembly & Generation (1 tool)
18. ✅ `assemble_full_spec` - Combine all specs

## Migration Strategy

### Phase 1: Parallel Implementation (Week 1)
- Keep v2 tools running
- Build new atomic tools alongside
- Test atomic pipeline with simple drills

### Phase 2: Gradual Migration (Week 2)
- Route simple drills to atomic pipeline
- Complex drills still use v2
- A/B test for accuracy comparison

### Phase 3: Full Cutover (Week 3)
- All drills use atomic pipeline
- v2 tools deprecated but available
- Monitor for issues

### Phase 4: Cleanup (Week 4)
- Remove deprecated v2 tools
- Optimize atomic pipeline
- Document final API

## Compatibility Considerations

### Breaking Changes
1. **Session Management**: No more `initialize_diagram` sessions
2. **Validation API**: Split validation into multiple tools
3. **Preview API**: Multiple preview tools instead of one
4. **Batch Processing**: Position/movement mapping now batch-oriented

### Backward Compatibility Options
1. **Wrapper Functions**: Create v2-compatible wrappers around atomic tools
2. **Legacy Mode**: Flag to use old pipeline
3. **Migration Helper**: Tool to convert v2 specs to atomic format

## Code Reuse Opportunities

### Can Reuse from v2
- Position coordinate database (`OFFENSIVE_POSITIONS`, etc.)
- Waypoint calculation logic
- SVG generation code
- Template database
- Spatial validation logic

### Need to Rewrite
- LLM prompts (more focused)
- Validation logic (split into stages)
- Preview generation (stage-specific)
- Error handling (atomic-specific)

## Performance Impact

### Improvements
- ✅ Fewer LLM calls (3 vs potentially many)
- ✅ Faster validation (no LLM in validation)
- ✅ Better caching opportunities (atomic results)
- ✅ Parallel processing potential

### Potential Issues
- ⚠️ More tool calls overall (but simpler)
- ⚠️ More network overhead (if remote)
- ⚠️ More complex orchestration

## Risk Assessment

### High Risk
1. **User Adoption**: Significant workflow change
2. **Agent Compatibility**: Agents need retraining
3. **Edge Cases**: May not handle all v2 scenarios initially

### Medium Risk
1. **Performance**: More tool calls could be slower
2. **Complexity**: More moving parts to maintain
3. **Testing**: Need comprehensive test coverage

### Low Risk
1. **Technical Feasibility**: All components proven
2. **Rollback**: Can keep v2 as fallback
3. **Data Loss**: No data migration needed

## Recommendation

### Proceed with Atomic Pipeline Because:

1. **Better Reliability**: Each atomic step is predictable
2. **Easier Debugging**: Clear failure points
3. **Higher Confidence**: Validation at each stage
4. **Better Maintainability**: Simple, focused tools
5. **Improved Accuracy**: Less reliance on LLM interpretation

### Implementation Priority:

1. **Week 1**: Build core atomic tools (gaps, positions, movements)
2. **Week 2**: Add validation and preview layers
3. **Week 3**: Integrate and test with real drills
4. **Week 4**: Migration and optimization

### Success Metrics:

- **Accuracy**: >95% correct drill interpretation
- **Reliability**: <5% failure rate
- **Performance**: <2s for simple drills, <5s for complex
- **User Satisfaction**: Positive feedback on predictability

## Conclusion

The atomic pipeline represents a fundamental shift from monolithic to modular design. While it requires significant changes to v2 tools, the benefits in reliability, debuggability, and accuracy justify the effort. The migration can be done gradually with minimal risk.