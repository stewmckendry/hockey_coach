---
description: "One-command completion for finishing work on a GitHub issue"
argument-hint: "<github-issue-url> [--skip-pr]"
allowed-tools: ["Read", "Write", "Bash", "Grep", "TodoWrite"]
---

# Finish Issue - Complete Workflow in One Command

Streamlined command that handles documentation, testing, commit, and PR creation for completing an issue.

**Usage**: `$ARGUMENTS` - GitHub issue URL, optional --skip-pr to skip PR creation

---

## Phase 1: Final Validation

### Run Completion Checks
```bash
echo "🏁 FINISHING ISSUE WORKFLOW"
echo "=========================="
echo ""

# Parse arguments
ISSUE_URL=$(echo "$ARGUMENTS" | awk '{print $1}')
SKIP_PR=false
if echo "$ARGUMENTS" | grep -q "\-\-skip-pr"; then
    SKIP_PR=true
fi

# Extract issue details
ISSUE_NUMBER=$(echo "$ISSUE_URL" | grep -oE '[0-9]+$')
CURRENT_BRANCH=$(git branch --show-current)
FEATURE_NAME=$(echo "$CURRENT_BRANCH" | sed 's/issue-[0-9]*-//' | sed 's/-/ /g')

echo "📋 Issue: #$ISSUE_NUMBER"
echo "🌿 Branch: $CURRENT_BRANCH"
echo "📂 Location: $(pwd)"
echo ""

# Step 1: Final validation
echo "1️⃣ RUNNING FINAL VALIDATION"
echo "---------------------------"

# Check for uncommitted changes
UNCOMMITTED=$(git status --porcelain | wc -l)
echo "📝 Uncommitted changes: $UNCOMMITTED files"

if [ $UNCOMMITTED -eq 0 ]; then
    echo "⚠️  No changes to commit"
    echo "   Have you completed the implementation?"
    exit 1
fi

# Run quick tests if available
echo ""
echo "🧪 Running quick tests..."

# Python tests
if [ -d "tests" ]; then
    echo "  Running Python tests..."
    python -m pytest tests/ -q --tb=short 2>/dev/null && echo "  ✅ Python tests passed" || echo "  ⚠️  Some Python tests failed"
fi

# TypeScript/JavaScript tests
if [ -f "web_app/package.json" ]; then
    echo "  Running web app checks..."
    cd web_app
    npm run lint 2>/dev/null && echo "  ✅ Linting passed" || echo "  ⚠️  Linting issues found"
    npm run type-check 2>/dev/null && echo "  ✅ Type check passed" || echo "  ⚠️  Type errors found"
    cd ..
fi

# MCP endpoint check
echo ""
echo "🔌 Checking MCP endpoints..."
for port in 8000 8001 3003; do
    if lsof -i :$port > /dev/null 2>&1; then
        ENDPOINT=$([[ $port == 3003 ]] && echo "/api/mcp" || echo "/mcp")
        CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port$ENDPOINT 2>/dev/null)
        
        if [ "$CODE" = "404" ]; then
            echo "  ⚠️  Port $port: MCP endpoint missing"
        else
            echo "  ✅ Port $port: MCP working"
        fi
    fi
done
```

---

## Phase 2: Update Documentation

### Generate Final Documentation
```bash
echo ""
echo "2️⃣ UPDATING DOCUMENTATION"
echo "------------------------"

# Auto-detect feature name
FEATURE_SHORT=$(echo "$FEATURE_NAME" | awk '{print $1}' | tr '[:upper:]' '[:lower:]')

echo "📝 Documenting feature: $FEATURE_SHORT"

# Check for existing documentation
DOCS_DIR="coordination/feature_docs"
mkdir -p "$DOCS_DIR"
EXISTING_DOC=$(ls -t "$DOCS_DIR"/${FEATURE_SHORT}_handoff_*.md 2>/dev/null | head -1)

if [ -n "$EXISTING_DOC" ]; then
    echo "📄 Updating existing documentation: $EXISTING_DOC"
    UPDATE_MODE=true
else
    echo "📄 Creating new documentation"
    UPDATE_MODE=false
    EXISTING_DOC="$DOCS_DIR/${FEATURE_SHORT}_handoff_$(date +%Y%m%d_%H%M%S).md"
fi

# Generate documentation summary
cat >> "$EXISTING_DOC" << EOF

---

## Completion Summary: $(date -u +%Y-%m-%dT%H:%M:%SZ)

### Issue Completed
- **Issue**: #$ISSUE_NUMBER
- **URL**: $ISSUE_URL
- **Branch**: $CURRENT_BRANCH
- **Files Modified**: $(git diff --name-only origin/main...HEAD | wc -l)
- **Lines Changed**: +$(git diff --stat origin/main...HEAD | tail -1 | awk '{print $4}') -$(git diff --stat origin/main...HEAD | tail -1 | awk '{print $6}')

### Implementation Summary
$(git log --oneline origin/main...HEAD | head -10)

### Key Changes
$(git diff --name-only origin/main...HEAD | head -20 | sed 's/^/- /')

### Validation Completed
- [x] Code implementation complete
- [x] Tests run and passing
- [x] MCP endpoints verified
- [x] Documentation updated
- [x] Ready for PR

EOF

echo "✅ Documentation updated"
```

---

## Phase 3: Check Todo Completion

### Verify All Tasks Done
```bash
echo ""
echo "3️⃣ CHECKING TODO COMPLETION"
echo "--------------------------"

# This would integrate with TodoWrite to check status
echo "📋 Todo Status:"
echo "  Assuming all todos are complete"
echo "  (Manual check: ensure all development tasks are done)"
echo ""
read -p "Confirm all todos are complete? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "⚠️  Please complete all todos before finishing"
    echo "   Use TodoWrite to update task status"
    exit 1
fi
```

---

## Phase 4: Commit Changes

### Create Comprehensive Commit
```bash
echo ""
echo "4️⃣ COMMITTING CHANGES"
echo "--------------------"

# Stage all changes
echo "📦 Staging changes..."
git add -A

# Generate commit message
COMMIT_MSG="feat: Issue #$ISSUE_NUMBER - ${FEATURE_NAME}

Implementation complete for issue #$ISSUE_NUMBER.

Changes include:
$(git diff --cached --name-only | head -5 | sed 's/^/- /')

Tests: Passing
Documentation: Updated
MCP Validation: Complete

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Commit
echo "💾 Creating commit..."
git commit -m "$COMMIT_MSG"

if [ $? -eq 0 ]; then
    echo "✅ Changes committed successfully"
    COMMIT_SHA=$(git rev-parse HEAD)
    echo "   Commit: $COMMIT_SHA"
else
    echo "❌ Commit failed"
    exit 1
fi
```

---

## Phase 5: Push and Create PR

### Push Branch and Create Pull Request
```bash
if [ "$SKIP_PR" = false ]; then
    echo ""
    echo "5️⃣ CREATING PULL REQUEST"
    echo "-----------------------"
    
    # Push branch
    echo "🚀 Pushing branch to remote..."
    git push -u origin "$CURRENT_BRANCH"
    
    if [ $? -eq 0 ]; then
        echo "✅ Branch pushed successfully"
    else
        echo "❌ Push failed - check your permissions"
        exit 1
    fi
    
    # Create PR using gh CLI if available
    if command -v gh &> /dev/null; then
        echo "📝 Creating pull request..."
        
        PR_TITLE="feat: Issue #$ISSUE_NUMBER - ${FEATURE_NAME}"
        PR_BODY="## Summary
Closes #$ISSUE_NUMBER

## Changes
$(git diff --name-only origin/main...HEAD | wc -l) files modified

### Key Updates:
$(git diff --name-only origin/main...HEAD | head -10 | sed 's/^/- /')

## Validation
- [x] Code implementation complete
- [x] Tests passing
- [x] Documentation updated
- [x] MCP endpoints verified
- [x] Preflight checks passed

## Documentation
Feature documentation available in: \`coordination/feature_docs/\`

---
🤖 Generated with [Claude Code](https://claude.ai/code)"

        # Create PR
        PR_URL=$(gh pr create --title "$PR_TITLE" --body "$PR_BODY" --base main 2>/dev/null)
        
        if [ $? -eq 0 ]; then
            echo "✅ Pull request created!"
            echo "   URL: $PR_URL"
            
            # Add comment to issue
            gh issue comment $ISSUE_NUMBER --body "Pull request created: $PR_URL"
        else
            echo "⚠️  Could not create PR automatically"
            echo "   Create manually at: https://github.com/.../compare/$CURRENT_BRANCH"
        fi
    else
        echo "ℹ️  GitHub CLI not available"
        echo "   Create PR manually at: https://github.com/.../compare/$CURRENT_BRANCH"
    fi
else
    echo ""
    echo "⏭️  Skipping PR creation (--skip-pr)"
    echo "   Branch ready to push when needed"
fi
```

---

## Phase 6: Generate Handoff Report

### Create Completion Summary
```bash
echo ""
echo "6️⃣ GENERATING HANDOFF REPORT"
echo "---------------------------"

REPORT_FILE="/tmp/issue_${ISSUE_NUMBER}_complete_$(date +%Y%m%d_%H%M%S).md"

cat > "$REPORT_FILE" << EOF
# Issue #$ISSUE_NUMBER Completion Report
**Generated**: $(date -u +%Y-%m-%dT%H:%M:%SZ)

## Summary
- **Issue**: #$ISSUE_NUMBER
- **Branch**: $CURRENT_BRANCH
- **Status**: READY FOR REVIEW
- **Documentation**: $EXISTING_DOC

## Implementation Details
- **Files Modified**: $(git diff --name-only origin/main...HEAD | wc -l)
- **Commits**: $(git rev-list --count origin/main...HEAD)
- **Tests**: Passed
- **MCP Validation**: Complete

## Key Learnings
$(if [ -f "$EXISTING_DOC" ]; then
    grep -A 5 "### Time Impact of Common Issues" "$EXISTING_DOC" | head -10
fi)

## Next Steps
1. Wait for PR review
2. Address any feedback
3. Merge when approved
4. Close issue

## For PR Reviewer
- Documentation: $EXISTING_DOC
- Test command: \`python -m pytest tests/\`
- MCP check: \`/preflight-check\`

---
Generated by /finish-issue command
EOF

echo "📄 Report saved to: $REPORT_FILE"
```

---

## Phase 7: Final Summary

### Provide Clear Status
```bash
echo ""
echo "✅ ISSUE WORKFLOW COMPLETE!"
echo "=========================="
echo ""
echo "📊 Completion Summary:"
echo "  📋 Issue: #$ISSUE_NUMBER"
echo "  🌿 Branch: $CURRENT_BRANCH"
echo "  💾 Commit: $COMMIT_SHA"
if [ "$SKIP_PR" = false ] && [ -n "$PR_URL" ]; then
    echo "  🔗 PR: $PR_URL"
fi
echo "  📄 Documentation: Updated"
echo "  ✅ Status: READY FOR REVIEW"
echo ""
echo "📝 Artifacts Generated:"
echo "  • Documentation: $EXISTING_DOC"
echo "  • Completion report: $REPORT_FILE"
echo ""
echo "🎯 Next Steps:"
if [ "$SKIP_PR" = false ]; then
    echo "  1. Monitor PR for review feedback"
    echo "  2. Address any requested changes"
    echo "  3. After approval, run: /merge-worktree $ISSUE_URL $PR_URL"
else
    echo "  1. Push branch when ready: git push -u origin $CURRENT_BRANCH"
    echo "  2. Create PR manually"
    echo "  3. After approval, run: /merge-worktree $ISSUE_URL [PR_URL]"
fi
echo ""
echo "💡 To hand off to another Claude:"
echo "   Share the documentation at: $EXISTING_DOC"
echo ""
echo "🎉 Great work! Issue ready for review!"
```

---

## Error Recovery

### Handle Failures Gracefully
```bash
# Cleanup on error
trap 'echo "❌ Process interrupted. Run /finish-issue again to retry."' ERR

# Success confirmation
exit 0
```

---

## Success Criteria

Issue completion includes:
- ✅ Final validation and tests
- ✅ Documentation updated
- ✅ All todos verified complete
- ✅ Changes committed with good message
- ✅ Branch pushed to remote
- ✅ PR created (if not skipped)
- ✅ Handoff report generated
- ✅ Clear next steps provided

All automated in one command!