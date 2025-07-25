# Test-First Development Template

Use this template for implementing new features with test-driven development.

## Phase 1: Explore & Plan

### 1. Read Relevant Files
```bash
# Use Read, Glob, Grep tools to understand:
# - Existing code patterns
# - Related components
# - Integration points
# - Dependencies
```

**Questions to Answer:**
- What files need to be modified?
- What existing patterns should be followed?
- What are the integration requirements?
- What could go wrong?

### 2. Define Success Criteria
- [ ] Functional requirements clear
- [ ] Performance expectations defined
- [ ] Error handling requirements specified
- [ ] Integration points identified

### 3. Create Implementation Plan
**Course Correction Checkpoint**: *"Does the scope and approach look right?"*

## Phase 2: Write Tests First

### 1. Create Test Cases
```python
# Example: Python component test
def test_new_feature():
    """Test description of what should happen"""
    # Arrange
    input_data = "test input"
    expected_output = "expected result"
    
    # Act
    result = new_feature_function(input_data)
    
    # Assert
    assert result == expected_output
    assert isinstance(result, str)
    assert len(result) > 0
```

```typescript
// Example: TypeScript component test
describe('NewFeature', () => {
  it('should handle valid input correctly', () => {
    const input = 'test input';
    const expected = 'expected result';
    
    const result = newFeature(input);
    
    expect(result).toBe(expected);
    expect(typeof result).toBe('string');
    expect(result.length).toBeGreaterThan(0);
  });
});
```

### 2. Run Tests (Should Fail)
```bash
# Python tests
python -m pytest tests/test_new_feature.py -v

# JavaScript/TypeScript tests  
npm test -- new-feature.test.ts
```

**Expected Result**: Tests should fail because feature not implemented yet.

## Phase 3: Implement Feature

### 1. Minimal Implementation
Create the simplest possible implementation that makes tests pass.

**Course Correction Checkpoint**: *"Are we on the right track technically?"*

### 2. Iterative Development
- Implement core functionality
- Run tests after each change
- Add error handling
- Add edge case handling

### 3. Integration Testing
```bash
# Test integration points
curl -X POST -H "Content-Type: application/json" \
  -d '{"test": "integration"}' \
  http://localhost:3000/api/new-feature
```

## Phase 4: Refine & Validate

### 1. Run All Tests
```bash
# Python
python -m pytest tests/ -v

# Web app
cd web_app
npm run test
npm run type-check
npm run lint
```

### 2. Manual Testing
- [ ] Happy path works
- [ ] Error cases handled gracefully
- [ ] Performance acceptable
- [ ] UI responsive (if applicable)

**Course Correction Checkpoint**: *"Does this meet the requirements?"*

### 3. Visual Validation (if UI component)
- Take screenshots before/after
- Test responsive behavior
- Verify accessibility

## Phase 5: Documentation & Commit

### 1. Update Documentation
- [ ] CLAUDE.md updated if needed
- [ ] Code comments added
- [ ] README updated if applicable

### 2. Pre-Commit Checks
```bash
# Use /commit-prep slash command
```

### 3. Commit with Clear Message
```
feat: add new feature with comprehensive testing

- Implement core functionality with test coverage
- Add error handling for edge cases
- Update documentation and examples
- Verify integration with existing components

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Template Checklist

- [ ] **Explore**: Read relevant files and understand scope
- [ ] **Plan**: Define success criteria and implementation approach
- [ ] **Test First**: Write failing tests before implementation
- [ ] **Implement**: Build feature to pass tests
- [ ] **Integrate**: Verify integration points work
- [ ] **Validate**: Manual testing and visual validation
- [ ] **Document**: Update relevant documentation
- [ ] **Commit**: Clean commit with descriptive message

## Common Patterns

### Hockey AI Features
- MCP tool integration
- Agent response formatting
- Web API endpoints
- Trace logging integration

### Testing Patterns
- Mock MCP server responses
- Test tool selection logic
- Validate response formats
- Test error scenarios

### Integration Points
- MCP server connection
- OpenAI API calls
- Web app communication
- Database queries (ChromaDB)

Use this template as a starting point and adapt based on the specific feature being implemented.