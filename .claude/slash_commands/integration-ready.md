# Integration Ready Command

Comprehensive pre-integration quality gates and submission preparation for Worker Claude instances.

**Usage**: Worker Claude instances only - after Build phase, before requesting integration

---

## Pre-Integration Quality Checks

### Code Quality Validation
```bash
echo "🔍 Running code quality checks..."

# Determine if this is a web app change
WEB_CHANGES=false
if git diff --name-only HEAD | grep -q "web_app/"; then
    WEB_CHANGES=true
fi

if [ "$WEB_CHANGES" = true ]; then
    echo "📱 Web app changes detected, running frontend quality checks..."
    
    cd web_app
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ] || [ "package.json" -nt "node_modules" ]; then
        echo "📦 Installing npm dependencies..."
        npm install
    fi
    
    # ESLint - Check for code quality issues
    echo "🔍 Running ESLint..."
    if npm run lint; then
        echo "✅ ESLint: No issues found"
    else
        echo "❌ ESLint: Issues found - fix before integration"
        exit 1
    fi
    
    # TypeScript - Check for type errors
    echo "🔍 Running TypeScript checks..."
    if npm run type-check; then
        echo "✅ TypeScript: No type errors"
    else
        echo "❌ TypeScript: Type errors found - fix before integration"
        exit 1
    fi
    
    # Production build test
    echo "🔍 Testing production build..."
    if npm run build; then
        echo "✅ Build: Production build successful"
    else
        echo "❌ Build: Production build failed - fix before integration"
        exit 1
    fi
    
    cd ..
    echo "✅ Web app quality checks: All passed"
else
    echo "📝 No web app changes detected, skipping frontend checks"
fi
```

### Python Quality Validation
```bash
echo "🔍 Running Python quality checks..."

# Check if Python files were modified
PYTHON_CHANGES=false
if git diff --name-only HEAD | grep -q "\.py$"; then
    PYTHON_CHANGES=true
fi

if [ "$PYTHON_CHANGES" = true ]; then
    echo "🐍 Python changes detected, running Python quality checks..."
    
    # Ensure spacy_env is activated
    if [[ "$VIRTUAL_ENV" != *"spacy_env"* ]]; then
        source /Users/liammckendry/spacy_env/bin/activate
    fi
    
    # Run Python tests if they exist
    if [ -d "tests" ]; then
        echo "🧪 Running Python tests..."
        if python -m pytest tests/ -v; then
            echo "✅ Python tests: All passed"
        else
            echo "❌ Python tests: Some tests failed - fix before integration"
            exit 1
        fi
    fi
    
    # Test new MCP tools if server files modified
    if git diff --name-only HEAD | grep -q "servers/hockey_mcp.py"; then
        echo "🔧 MCP server changes detected, testing tools..."
        if python -c "
import requests
try:
    response = requests.get('http://localhost:8000/mcp/list_tools', timeout=10)
    if response.status_code == 200:
        print('✅ MCP Tools: Server responding correctly')
    else:
        print('❌ MCP Tools: Server error - check implementation')
        exit(1)
except Exception as e:
    print(f'❌ MCP Tools: Connection error - {e}')
    exit(1)
"; then
            echo "✅ MCP tools: Server integration working"
        else
            echo "❌ MCP tools: Integration issues found"
            exit 1
        fi
    fi
    
    echo "✅ Python quality checks: All passed"
else
    echo "📝 No Python changes detected, skipping Python checks"
fi
```

### Service Integration Testing
```bash
echo "🔍 Testing service integration..."

# Test MCP Server health
if curl -s -f http://localhost:8000/health > /dev/null; then
    echo "✅ MCP Server: Healthy and responding"
else
    echo "❌ MCP Server: Unreachable - check server status"
    exit 1
fi

# Test agent integration if POC changes made
if git diff --name-only HEAD | grep -q "servers/poc/"; then
    echo "🤖 POC agent changes detected, testing integration..."
    
    # Test agent CLI functionality  
    if [ -f "servers/poc/test_agent_cli.py" ]; then
        cd servers/poc
        if python test_agent_cli.py; then
            echo "✅ Agent CLI: Integration working"
        else
            echo "❌ Agent CLI: Integration issues found"
            exit 1
        fi
        cd ../..
    fi
    
    # Test MCP connection
    if [ -f "servers/poc/test_mcp_connection.py" ]; then
        cd servers/poc  
        if python test_mcp_connection.py; then
            echo "✅ MCP Connection: Agent-to-MCP integration working"
        else
            echo "❌ MCP Connection: Agent-to-MCP issues found"
            exit 1
        fi
        cd ../..
    fi
fi

echo "✅ Service integration: All tests passed"
```

---

## Git Operations & Branch Management

### Prepare Changes for Integration
```bash
echo "🔍 Preparing changes for integration..."

# Check git status
echo "📊 Git status:"
git status

# Add all changes
echo "📝 Adding changes to git..."
git add .

# Verify what will be committed
echo "📋 Changes to be committed:"
git diff --staged --name-only

# Check for sensitive information
echo "🔒 Scanning for sensitive information..."
if git diff --staged | grep -i -E "(api_key|password|secret|token|sk-)" | grep -v "OPENAI_API_KEY"; then
    echo "❌ Security: Sensitive information detected in staged changes"
    echo "Remove sensitive data before integration"
    exit 1
else
    echo "✅ Security: No sensitive information detected"
fi
```

### Create Integration Commit
```bash
echo "🔍 Creating integration commit..."

# Determine task info for commit message
TASK_NUMBER=""
TASK_DESCRIPTION=""
case "$(pwd)" in
    *"task_1_4") 
        TASK_NUMBER="1.4"
        TASK_DESCRIPTION="Season Planning Specialist Agent"
        ;;
    *"task_1_5") 
        TASK_NUMBER="1.5"
        TASK_DESCRIPTION="Team Assessment Tool"
        ;;
    *"task_1_6") 
        TASK_NUMBER="1.6"
        TASK_DESCRIPTION="Artifact Generation"
        ;;
esac

# Create structured commit message
git commit -m "$(cat <<EOF
Complete Task ${TASK_NUMBER}: ${TASK_DESCRIPTION}

Implementation includes:
$(git diff --staged --name-only | sed 's/^/- /')

All quality gates passed:
- Code quality checks: ✅
- Service integration tests: ✅  
- Security scan: ✅

Ready for integration into main branch.

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

if [ $? -eq 0 ]; then
    echo "✅ Integration commit: Created successfully"
else
    echo "❌ Integration commit: Failed to create"
    exit 1
fi
```

### Rebase with Main Branch
```bash
echo "🔍 Syncing with main branch..."

# Fetch latest changes from origin
git fetch origin main

# Check if rebase is needed
BEHIND_COUNT=$(git rev-list --count HEAD..origin/main)
if [ "$BEHIND_COUNT" -gt 0 ]; then
    echo "📥 Main branch has $BEHIND_COUNT new commits, rebasing..."
    
    # Perform rebase
    if git rebase origin/main; then
        echo "✅ Rebase: Successfully synced with main"
    else
        echo "❌ Rebase: Conflicts detected"
        echo "📋 Resolve conflicts manually:"
        echo "1. Fix conflicts in affected files"
        echo "2. git add <resolved-files>"
        echo "3. git rebase --continue"
        echo "4. Re-run /integration-ready when resolved"
        exit 1
    fi
else
    echo "✅ Sync: Already up to date with main branch"
fi
```

### Push Integration Branch
```bash
echo "🔍 Pushing integration branch..."

# Push branch to origin
CURRENT_BRANCH=$(git branch --show-current)
if git push origin "$CURRENT_BRANCH"; then
    echo "✅ Branch push: Successfully pushed $CURRENT_BRANCH"
else
    echo "❌ Branch push: Failed to push $CURRENT_BRANCH"
    exit 1
fi
```

---

## Integration Queue Submission

### Update Integration Queue
```bash
echo "🔍 Submitting to integration queue..."

# Generate integration submission
cat >> coordination/integration_queue.md << EOF

## Task ${TASK_NUMBER}: ${TASK_DESCRIPTION}
**Submitted By**: Worker Claude ${TASK_NUMBER}
**Completion Date**: $(date -u +%Y-%m-%dT%H:%M:%SZ)
**Branch**: $CURRENT_BRANCH
**Commit**: $(git rev-parse HEAD)

### Files Modified:
$(git diff origin/main --name-only | sed 's/^/- /')

### Pre-Integration Checklist:
- [x] All tests passing (code quality, service integration)
- [x] Code quality checks complete (lint, type-check, build)
- [x] Security scan completed (no sensitive data)
- [x] Git operations successful (commit, rebase, push)
- [x] Branch synced with latest main
- [x] Integration submission prepared

### Quality Gate Results:
$(if [ "$WEB_CHANGES" = true ]; then echo "- [x] Web app: ESLint, TypeScript, build tests passed"; fi)
$(if [ "$PYTHON_CHANGES" = true ]; then echo "- [x] Python: Tests and MCP integration validated"; fi)
- [x] Service health: All core services operational
- [x] Security: No sensitive information in changes

### Integration Notes:
$(git log --oneline origin/main..HEAD | sed 's/^/- /')

### Post-Integration Tasks:
- [ ] Validate integrated system functionality
- [ ] Archive task scratchpad files
- [ ] Clean up worktree after successful integration

**STATUS**: READY_FOR_INTEGRATION

---

EOF

echo "✅ Integration queue: Submission added"
```

### Update Task Scratchpad
```bash
echo "🔍 Updating task scratchpad with completion..."

# Determine scratchpad file
SCRATCHPAD_FILE=""
case "$(pwd)" in
    *"task_1_4") SCRATCHPAD_FILE="coordination/task_1_4_scratchpad.md" ;;
    *"task_1_5") SCRATCHPAD_FILE="coordination/task_1_5_scratchpad.md" ;;
    *"task_1_6") SCRATCHPAD_FILE="coordination/task_1_6_scratchpad.md" ;;
esac

# Add completion status to scratchpad
cat >> "$SCRATCHPAD_FILE" << EOF

---

## TASK COMPLETION - $(date -u +%Y-%m-%dT%H:%M:%SZ)

**Status**: ✅ INTEGRATION_READY
**Completion**: 100%
**Phase**: SUBMIT_WORK_COMPLETE

### Implementation Summary:
- Files created/modified: $(git diff origin/main --name-only | wc -l | tr -d ' ')
- Commits made: $(git rev-list --count origin/main..HEAD)
- Quality gates passed: All
- Integration submission: Complete

### Quality Validation Results:
$(if [ "$WEB_CHANGES" = true ]; then echo "- ✅ Web app quality checks: ESLint, TypeScript, build"; fi)
$(if [ "$PYTHON_CHANGES" = true ]; then echo "- ✅ Python quality checks: Tests, MCP integration"; fi)
- ✅ Service integration: MCP server and tools functional
- ✅ Security scan: No sensitive data detected
- ✅ Git operations: Commit, rebase, push successful

### Integration Details:
- **Branch**: $CURRENT_BRANCH
- **Commit**: $(git rev-parse --short HEAD)
- **Status**: Ready for Planning Claude integration
- **Queue**: Added to coordination/integration_queue.md

### Next Steps:
- Planning Claude will review and integrate
- Post-integration validation will be performed
- Task will be marked complete upon successful integration

**Worker Claude Task Execution**: ✅ COMPLETE

---

EOF

echo "✅ Task scratchpad: Updated with completion status"
```

### Update Shared Status Dashboard
```bash
echo "🔍 Updating shared status dashboard..."

# Update shared status with completion
python -c "
import re

# Read current shared status
with open('coordination/shared_status.md', 'r') as f:
    content = f.read()

# Update task status to INTEGRATION_READY
task_pattern = r'(\| ${TASK_NUMBER}.*?\| Worker-\d+ \|) [^|]+ (\| \d+% \|)'
replacement = r'\1 INTEGRATION_READY \2 100% |'

updated_content = re.sub(task_pattern.replace('${TASK_NUMBER}', '${TASK_NUMBER}'), replacement, content)

# Write updated content
with open('coordination/shared_status.md', 'w') as f:
    f.write(updated_content)

print('✅ Shared status updated: Task ${TASK_NUMBER} marked as INTEGRATION_READY')
"

echo "✅ Shared status: Updated with integration ready status"
```

---

## Final Integration Summary

### Generate Submission Report
```bash
echo ""
echo "🎉 INTEGRATION SUBMISSION COMPLETE!"
echo ""
echo "Task Summary:"
echo "  📋 Task: ${TASK_NUMBER} - ${TASK_DESCRIPTION}"
echo "  🌿 Branch: $CURRENT_BRANCH"
echo "  📝 Commit: $(git rev-parse --short HEAD)"
echo "  📁 Files Modified: $(git diff origin/main --name-only | wc -l | tr -d ' ')"
echo "  🧪 Quality Gates: All Passed"
echo ""
echo "Integration Details:"
echo "  📊 Queue: Added to coordination/integration_queue.md"
echo "  📝 Scratchpad: Updated with completion status"
echo "  🔄 Shared Status: Updated to INTEGRATION_READY"
echo "  ☁️  Remote: Branch pushed to origin"
echo ""
echo "Next Steps:"
echo "  1. Planning Claude will review submission"
echo "  2. Integration will be performed in dependency order"
echo "  3. Post-integration validation will be executed"
echo "  4. Task will be marked complete"
echo ""
echo "Worker Claude autonomous execution: ✅ COMPLETE"
echo ""
```

---

## Success Criteria

- ✅ All quality checks passed (web, Python, services)
- ✅ Security scan completed (no sensitive data)
- ✅ Git operations successful (commit, rebase, push)
- ✅ Integration queue submission added
- ✅ Task scratchpad updated with completion
- ✅ Shared status dashboard updated
- ✅ Branch ready for Planning Claude integration

## Troubleshooting

### Quality Check Failures
```bash
# Fix ESLint issues
cd web_app && npm run lint -- --fix

# Fix TypeScript issues  
cd web_app && npm run type-check

# Fix Python test failures
python -m pytest tests/ -v --tb=short
```

### Git Rebase Conflicts
```bash
# View conflicted files
git status

# Resolve conflicts manually, then:
git add <resolved-files>
git rebase --continue

# Re-run integration-ready after resolution
```

### Service Integration Issues
```bash
# Restart MCP server
python servers/hockey_mcp.py &

# Test connectivity
curl http://localhost:8000/health

# Re-run integration tests
```

### Push Failures
```bash
# Check remote status
git remote -v

# Force push if needed (use carefully)
git push origin $CURRENT_BRANCH --force-with-lease
```

Task is now ready for Planning Claude integration into main branch!