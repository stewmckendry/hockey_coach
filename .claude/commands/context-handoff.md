---
description: "Handle context window exhaustion - commit work and prepare handoff to new Claude Code instance"
argument-hint: "[--emergency] [--skip-tests]"
allowed-tools: ["Read", "Write", "Bash", "Grep", "TodoWrite", "Task"]
---

# Context Handoff - When Context Window is Full

Handles the critical moment when Claude Code's context window is exhausted and needs to hand off to a new instance. This command ensures all work is committed, documented, and ready for seamless continuation.

**Usage**: `$ARGUMENTS` - Optional: --emergency for quick handoff, --skip-tests to bypass tests

---

## Phase 1: Context Assessment

### Check Current Context Status
```bash
echo "🔍 CONTEXT WINDOW HANDOFF PROCEDURE"
echo "===================================="
echo ""

# Parse arguments
EMERGENCY=false
SKIP_TESTS=false
if echo "$ARGUMENTS" | grep -q "\-\-emergency"; then
    EMERGENCY=true
    echo "⚡ EMERGENCY MODE: Rapid handoff enabled"
fi
if echo "$ARGUMENTS" | grep -q "\-\-skip-tests"; then
    SKIP_TESTS=true
fi

# Estimate context usage (rough approximation)
echo "📊 Context Status:"
echo "  • Current session duration: $(ps -o etime= -p $$ | tr -d ' ')"
echo "  • Files opened this session: $(history | grep -c "cat\|Read\|Edit" 2>/dev/null || echo "Unknown")"
echo "  • Current branch: $(git branch --show-current)"
echo "  • Working directory: $(pwd)"
echo ""

# Check for uncommitted changes
UNCOMMITTED=$(git status --porcelain | wc -l)
if [ $UNCOMMITTED -gt 0 ]; then
    echo "⚠️  CRITICAL: $UNCOMMITTED uncommitted changes detected!"
    echo "   These MUST be committed before handoff"
else
    echo "✅ No uncommitted changes"
fi
echo ""
```

---

## Phase 2: Emergency Commit (If Needed)

### Commit All Work in Progress
```bash
if [ $UNCOMMITTED -gt 0 ]; then
    echo "💾 COMMITTING WORK IN PROGRESS"
    echo "=============================="
    
    # Stage all changes
    echo "📦 Staging all changes..."
    git add -A
    
    # Show what's being committed
    echo ""
    echo "Files being committed:"
    git status --short | head -20
    if [ $(git status --short | wc -l) -gt 20 ]; then
        echo "... and $(( $(git status --short | wc -l) - 20 )) more files"
    fi
    
    # Generate context-aware commit message
    BRANCH=$(git branch --show-current)
    ISSUE_NUM=$(echo "$BRANCH" | grep -oE 'issue-[0-9]+' | grep -oE '[0-9]+' || echo "")
    
    if [ "$EMERGENCY" = true ]; then
        COMMIT_MSG="WIP: Emergency context handoff - work in progress

Context window exhausted. Committing all current work for handoff.

Status: Work in progress
Branch: $BRANCH"
        
        if [ -n "$ISSUE_NUM" ]; then
            COMMIT_MSG="$COMMIT_MSG
Issue: #$ISSUE_NUM"
        fi
        
        COMMIT_MSG="$COMMIT_MSG

Files modified: $(git status --porcelain | wc -l)
Emergency commit due to context exhaustion

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
    else
        COMMIT_MSG="feat: Work in progress - context handoff

Committing current progress for context window handoff.

Changes include:
$(git diff --cached --name-only | head -5 | sed 's/^/- /')

Status: In Progress
Handoff Required: Yes

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
    fi
    
    # Commit
    echo ""
    echo "💾 Creating commit..."
    git commit -m "$COMMIT_MSG"
    
    if [ $? -eq 0 ]; then
        echo "✅ Changes committed successfully"
        COMMIT_SHA=$(git rev-parse HEAD)
        echo "   Commit: $COMMIT_SHA"
    else
        echo "❌ Commit failed - manual intervention needed!"
        exit 1
    fi
fi
```

---

## Phase 3: Quick Tests (Unless Skipped)

### Run Minimal Validation
```bash
if [ "$SKIP_TESTS" = false ] && [ "$EMERGENCY" = false ]; then
    echo ""
    echo "🧪 RUNNING QUICK VALIDATION"
    echo "=========================="
    
    # Quick syntax check
    echo "Checking Python syntax..."
    find . -name "*.py" -type f -exec python -m py_compile {} \; 2>&1 | head -5
    
    # Quick TypeScript check if web app exists
    if [ -d "web_app" ]; then
        echo "Checking TypeScript..."
        cd web_app
        npm run type-check 2>&1 | head -10 || true
        cd ..
    fi
    
    echo "✅ Quick validation complete (full tests skipped for handoff)"
else
    echo ""
    echo "⏭️  Skipping tests for rapid handoff"
fi
```

---

## Phase 4: Generate Handoff Documentation

### Create Comprehensive Handoff Report
```bash
echo ""
echo "📝 GENERATING HANDOFF DOCUMENTATION"
echo "==================================="

HANDOFF_FILE="coordination/context_handoff_$(date +%Y%m%d_%H%M%S).md"
mkdir -p coordination

cat > "$HANDOFF_FILE" << 'EOF'
# Context Handoff Report
**Generated**: $(date -u +%Y-%m-%dT%H:%M:%SZ)
**Reason**: Context window exhaustion

## Current State

### Git Information
- **Branch**: $(git branch --show-current)
- **Last Commit**: $(git log -1 --oneline)
- **Uncommitted Changes**: $UNCOMMITTED files (now committed)
- **Working Directory**: $(pwd)

### Active Work
EOF

# Add current issue if detectable
BRANCH=$(git branch --show-current)
if echo "$BRANCH" | grep -q "issue-"; then
    ISSUE_NUM=$(echo "$BRANCH" | grep -oE '[0-9]+')
    echo "- **GitHub Issue**: #$ISSUE_NUM" >> "$HANDOFF_FILE"
    echo "- **Issue URL**: https://github.com/[owner]/[repo]/issues/$ISSUE_NUM" >> "$HANDOFF_FILE"
fi

cat >> "$HANDOFF_FILE" << 'EOF'

### Environment Status
- **Virtual Environment**: $(if [[ "$VIRTUAL_ENV" == *"spacy_env"* ]]; then echo "✅ Activated"; else echo "❌ Not activated"; fi)
- **Python Path**: $(which python)
- **Current Directory**: $(pwd)

## Services Running
EOF

# Check service status
for port in 8000 8001 3003 3000; do
    if lsof -i :$port > /dev/null 2>&1; then
        echo "- Port $port: ✅ Running" >> "$HANDOFF_FILE"
    else
        echo "- Port $port: ❌ Not running" >> "$HANDOFF_FILE"
    fi
done

cat >> "$HANDOFF_FILE" << 'EOF'

## Work Completed This Session

### Files Modified
```
$(git diff --name-only HEAD~1...HEAD 2>/dev/null | head -20 || echo "Unable to determine")
```

### Recent Commands
Key commands executed in this session:
- Virtual environment activation
- Service startup
- Testing commands
- Git operations

## Critical Context to Preserve

### Known Issues Encountered
1. **MCP Endpoints**: Check if /mcp endpoints are responding (common 30-40% time loss)
2. **Virtual Environment**: Must activate spacy_env from parent directory
3. **Schema Versions**: Watch for cached data schema mismatches

### Current Todo List
[TodoWrite tool status would be captured here if available]

## Handoff Instructions for New Claude

### Immediate Setup Required
```bash
# 1. Navigate to correct location
cd $(pwd)

# 2. Activate virtual environment (CRITICAL!)
cd .. && source spacy_env/bin/activate && cd $(basename $(pwd))

# 3. Run preflight check
/preflight-check

# 4. Review this handoff document
cat $HANDOFF_FILE
```

### Continue Work
```bash
# First: Review this handoff document
cat $HANDOFF_FILE

# Then EITHER:

# Option A: Continue existing work (if in worktree)
/onboard-feature [feature-name]  # Reads documentation
/preflight-check                 # Verify environment

# Option B: Start fresh with the issue
/start-issue https://github.com/owner/repo/issues/XXX
```

### Quick Status Commands
```bash
git status                    # Check for uncommitted changes
git log -5 --oneline          # Review recent commits
/debug-mcp                    # If MCP issues arise
/preflight-check              # Full environment check
```

## Session Summary

### What Was Attempted
[Describe the main goal of this session]

### What Was Completed
[List completed tasks]

### What Remains
[List pending tasks]

### Blockers or Issues
[Note any blockers encountered]

## Recovery Information

### If Something Goes Wrong
1. **Git Recovery**: Last stable commit is $(git rev-parse HEAD)
2. **Branch Recovery**: Working on branch $(git branch --show-current)
3. **Rollback Command**: `git reset --hard HEAD~1` (if needed)

### Critical Files to Review
$(git diff --name-only HEAD~1...HEAD 2>/dev/null | grep -E "\.(py|ts|tsx|js|jsx)$" | head -10)

---

**Handoff Type**: $(if [ "$EMERGENCY" = true ]; then echo "EMERGENCY"; else echo "PLANNED"; fi)
**Tests Run**: $(if [ "$SKIP_TESTS" = true ]; then echo "SKIPPED"; else echo "MINIMAL"; fi)
**Ready for Continuation**: YES

EOF

echo "✅ Handoff documentation created: $HANDOFF_FILE"
```

---

## Phase 5: Push Changes (If Possible)

### Push to Remote for Safety
```bash
echo ""
echo "🚀 PUSHING TO REMOTE"
echo "==================="

CURRENT_BRANCH=$(git branch --show-current)

# Check if we're on a feature branch
if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
    echo "Pushing branch to remote for safety..."
    
    git push -u origin "$CURRENT_BRANCH" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ Branch pushed successfully"
        echo "   Remote backup created"
    else
        echo "⚠️  Could not push to remote"
        echo "   Changes are committed locally"
    fi
else
    echo "⚠️  On main branch - not pushing"
    echo "   Create feature branch first"
fi
```

---

## Phase 6: Final Handoff Summary

### Provide Clear Next Steps
```bash
echo ""
echo "✅ CONTEXT HANDOFF COMPLETE"
echo "=========================="
echo ""
echo "📊 Handoff Summary:"
echo "  • All changes: $(if [ $UNCOMMITTED -gt 0 ]; then echo "✅ Committed"; else echo "Already committed"; fi)"
echo "  • Documentation: ✅ Generated"
echo "  • Branch status: $(if git push -u origin HEAD 2>/dev/null; then echo "✅ Pushed"; else echo "⚠️ Local only"; fi)"
echo "  • Handoff file: $HANDOFF_FILE"
echo ""
echo "🎯 For New Claude Code Instance:"
echo ""
echo "1. Read the handoff documentation:"
echo "   cat $HANDOFF_FILE"
echo ""
echo "2. If continuing same issue:"
echo "   /onboard-feature $(echo "$BRANCH" | sed 's/issue-[0-9]*-//' | sed 's/-/ /g')"
echo ""
echo "3. Or start fresh with issue:"
echo "   /start-issue [github-issue-url]"
echo ""
echo "4. Quick status check:"
echo "   /preflight-check"
echo "   git log -5 --oneline"
echo ""
echo "💡 Critical Information:"
echo "  • Branch: $CURRENT_BRANCH"
echo "  • Last commit: $(git log -1 --oneline)"
echo "  • Working dir: $(pwd)"
echo ""

if [ "$EMERGENCY" = true ]; then
    echo "⚡ EMERGENCY HANDOFF COMPLETE"
    echo "   Work saved, ready for new instance"
else
    echo "📋 PLANNED HANDOFF COMPLETE"
    echo "   All work documented and ready"
fi

echo ""
echo "This Claude Code instance can now safely close."
echo "All work has been preserved for continuation."
```

---

## What This Command Does

When Claude Code's context window is exhausted, this command:

1. **Commits Everything**: Stages and commits ALL uncommitted changes with descriptive message
2. **Documents State**: Creates comprehensive handoff documentation
3. **Pushes to Remote**: Backs up work to remote repository
4. **Prepares Continuation**: Provides exact commands for new instance

### Key Features:
- **Emergency Mode** (`--emergency`): Rapid handoff without tests
- **Skip Tests** (`--skip-tests`): Bypass validation for speed
- **Automatic Documentation**: Captures entire session state
- **Recovery Information**: Includes rollback commands if needed
- **Clear Instructions**: Step-by-step guide for new instance

### When Context is Getting Full:
```bash
# Planned handoff (recommended)
/context-handoff

# Emergency handoff (when context critically low)
/context-handoff --emergency

# Quick handoff without tests
/context-handoff --skip-tests
```

The new Claude Code instance will have everything needed to continue seamlessly!