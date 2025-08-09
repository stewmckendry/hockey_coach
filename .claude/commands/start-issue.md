---
description: "One-command setup for starting work on a GitHub issue with all safety checks"
argument-hint: "<github-issue-url> [--skip-checks]"
allowed-tools: ["Read", "Write", "Bash", "Grep", "WebFetch", "TodoWrite"]
---

# Start Issue - Complete Setup in One Command

Streamlined command that combines worktree setup, preflight checks, and feature onboarding into a single workflow.

**Usage**: `$ARGUMENTS` - GitHub issue URL, optional --skip-checks to bypass preflight

---

## Phase 1: Setup Worktree

### Create and Navigate to Worktree
```bash
echo "🚀 STARTING ISSUE WORKFLOW"
echo "========================="
echo ""

# Parse arguments
ISSUE_URL=$(echo "$ARGUMENTS" | awk '{print $1}')
SKIP_CHECKS=false
if echo "$ARGUMENTS" | grep -q "\-\-skip-checks"; then
    SKIP_CHECKS=true
fi

# Extract issue number and repo info
ISSUE_NUMBER=$(echo "$ISSUE_URL" | grep -oE '[0-9]+$')
REPO_PATH=$(echo "$ISSUE_URL" | sed 's|https://github.com/||' | sed 's|/issues/.*||')

echo "📋 Issue: #$ISSUE_NUMBER"
echo "📦 Repository: $REPO_PATH"
echo ""

# Step 1: Create worktree
echo "1️⃣ CREATING WORKTREE"
echo "-------------------"

# Fetch issue title for branch name
echo "📥 Fetching issue details..."
ISSUE_TITLE=$(curl -s "https://api.github.com/repos/$REPO_PATH/issues/$ISSUE_NUMBER" | \
    python -c "import json, sys; print(json.load(sys.stdin).get('title', 'issue'))" 2>/dev/null)

# Sanitize branch name
BRANCH_NAME="issue-${ISSUE_NUMBER}-$(echo "$ISSUE_TITLE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | cut -c1-50)"
WORKTREE_PATH="../thunder_playbook_worktrees/issue-${ISSUE_NUMBER}"

# Check if worktree already exists
if [ -d "$WORKTREE_PATH" ]; then
    echo "✅ Worktree already exists: $WORKTREE_PATH"
    echo "📂 Navigating to existing worktree..."
else
    echo "🌿 Creating new worktree..."
    git worktree add "$WORKTREE_PATH" -b "$BRANCH_NAME"
    echo "✅ Worktree created: $WORKTREE_PATH"
fi

echo ""
echo "📍 Location: $WORKTREE_PATH"
echo "🌿 Branch: $BRANCH_NAME"
```

---

## Phase 2: Navigate and Activate Environment

### Switch to Worktree and Setup Environment
```bash
echo ""
echo "2️⃣ ENVIRONMENT SETUP"
echo "-------------------"

# Navigate to worktree
cd "$WORKTREE_PATH"
echo "📂 Changed to worktree directory"

# Activate virtual environment
cd .. && source spacy_env/bin/activate && cd "$(basename "$WORKTREE_PATH")"
echo "✅ Virtual environment activated"

# Verify Python
echo "🐍 Python: $(which python)"
echo "📦 Version: $(python --version)"
```

---

## Phase 3: Run Preflight Checks

### Execute Safety Checks
```bash
if [ "$SKIP_CHECKS" = false ]; then
    echo ""
    echo "3️⃣ PREFLIGHT CHECKS"
    echo "------------------"
    
    # Critical checks only for speed
    CHECKS_PASSED=true
    
    # Check MCP endpoints
    echo "🔍 Checking MCP endpoints..."
    for port in 8000 8001 3003; do
        if lsof -i :$port > /dev/null 2>&1; then
            ENDPOINT=$([[ $port == 3003 ]] && echo "/api/mcp" || echo "/mcp")
            CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port$ENDPOINT 2>/dev/null)
            
            if [ "$CODE" = "404" ]; then
                echo "  ❌ Port $port: MCP endpoint MISSING!"
                echo "     Run: /debug-mcp $port --fix"
                CHECKS_PASSED=false
            elif [ "$CODE" = "200" ] || [ "$CODE" = "405" ]; then
                echo "  ✅ Port $port: MCP working"
            fi
        fi
    done
    
    # Check ChromaDB
    echo "🔍 Checking ChromaDB..."
    python -c "
import sys
sys.path.append('.')
try:
    from utils.chroma_utils import get_chroma_collection
    collection = get_chroma_collection('drill-source1')
    print('  ✅ ChromaDB connected')
except:
    print('  ⚠️  ChromaDB not accessible (may not be needed)')
" 2>/dev/null
    
    if [ "$CHECKS_PASSED" = false ]; then
        echo ""
        echo "⚠️  Some checks failed. Run /debug-mcp for fixes."
    else
        echo ""
        echo "✅ All critical checks passed!"
    fi
else
    echo ""
    echo "⏭️  Skipping preflight checks (--skip-checks)"
fi
```

---

## Phase 4: Check for Existing Documentation

### Look for Previous Work
```bash
echo ""
echo "4️⃣ CHECKING FOR EXISTING DOCUMENTATION"
echo "--------------------------------------"

# Determine feature name from issue
FEATURE_NAME=$(echo "$ISSUE_TITLE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | cut -c1-30)

# Check for existing documentation
DOCS_DIR="coordination/feature_docs"
EXISTING_DOC=$(ls -t "$DOCS_DIR"/${FEATURE_NAME}_handoff_*.md 2>/dev/null | head -1)

if [ -n "$EXISTING_DOC" ]; then
    echo "📄 Found existing documentation!"
    echo "   File: $EXISTING_DOC"
    echo ""
    echo "📋 Previous work summary:"
    # Show executive summary or last update
    sed -n '/## Executive Summary/,/^##/p' "$EXISTING_DOC" | head -10
    sed -n '/### Update Summary/,/^###/p' "$EXISTING_DOC" | head -10
    
    echo ""
    echo "💡 To review full documentation:"
    echo "   /onboard-feature $FEATURE_NAME"
else
    echo "📄 No existing documentation found"
    echo "   Starting fresh on this feature"
fi
```

---

## Phase 5: Fetch and Analyze Issue

### Get Issue Context
```bash
echo ""
echo "5️⃣ ANALYZING ISSUE REQUIREMENTS"
echo "-------------------------------"

# Fetch full issue details
echo "📥 Fetching issue details and comments..."

python << EOF
import json
import urllib.request

try:
    # Fetch issue
    url = f"https://api.github.com/repos/$REPO_PATH/issues/$ISSUE_NUMBER"
    with urllib.request.urlopen(url) as response:
        issue = json.loads(response.read())
    
    print(f"📌 Title: {issue['title']}")
    print(f"👤 Author: {issue['user']['login']}")
    print(f"🏷️  Labels: {', '.join([l['name'] for l in issue['labels']])}")
    print(f"💬 Comments: {issue['comments']}")
    print("")
    print("📝 Description:")
    print("-" * 40)
    description = issue['body'] or 'No description provided'
    # Show first 500 chars
    print(description[:500])
    if len(description) > 500:
        print("... [truncated]")
    print("-" * 40)
    
    # Check for related issues mentioned
    related = []
    if '#' in description:
        import re
        related = re.findall(r'#(\d+)', description)
    if related:
        print(f"\n🔗 Related issues mentioned: {', '.join(['#' + r for r in related])}")
        
except Exception as e:
    print(f"⚠️  Could not fetch issue details: {e}")
    print("   Continue with manual review of requirements")
EOF
```

---

## Phase 6: Generate Initial Todo List

### Create Starting Tasks
```bash
echo ""
echo "6️⃣ GENERATING TODO LIST"
echo "----------------------"

python << EOF
import json

todos = [
    {
        'id': '1',
        'content': 'Review issue requirements and acceptance criteria',
        'status': 'pending'
    },
    {
        'id': '2',
        'content': 'Identify affected files and components',
        'status': 'pending'
    },
    {
        'id': '3',
        'content': 'Plan implementation approach',
        'status': 'pending'
    },
    {
        'id': '4',
        'content': 'Implement core functionality',
        'status': 'pending'
    },
    {
        'id': '5',
        'content': 'Write/update tests',
        'status': 'pending'
    },
    {
        'id': '6',
        'content': 'Document changes with /document-feature',
        'status': 'pending'
    },
    {
        'id': '7',
        'content': 'Run final preflight checks',
        'status': 'pending'
    }
]

print("📝 Suggested todo list:")
print("")
print("Use TodoWrite to create:")
print("```python")
print("todos = [")
for todo in todos:
    print(f"    {todo},")
print("]")
print("```")
EOF
```

---

## Phase 7: Final Setup Summary

### Provide Clear Next Steps
```bash
echo ""
echo "✅ SETUP COMPLETE!"
echo "================="
echo ""
echo "📊 Summary:"
echo "  📋 Issue: #$ISSUE_NUMBER - $ISSUE_TITLE"
echo "  🌿 Branch: $BRANCH_NAME"
echo "  📂 Location: $WORKTREE_PATH"
echo "  🐍 Environment: Activated"
if [ "$SKIP_CHECKS" = false ]; then
    echo "  ✅ Preflight: Checked"
fi
if [ -n "$EXISTING_DOC" ]; then
    echo "  📄 Documentation: Found previous work"
fi
echo ""
echo "🎯 Next Steps:"
echo "  1. Create the todo list shown above"
echo "  2. Review issue requirements thoroughly"
echo "  3. Run /implement-feature $ISSUE_URL if needed"
echo "  4. Document progress with /document-feature"
echo ""
echo "💡 Quick Commands:"
echo "  • See full issue: Open $ISSUE_URL"
echo "  • Check services: /preflight-check"
echo "  • Debug MCP: /debug-mcp"
echo "  • Review docs: /onboard-feature $FEATURE_NAME"
echo ""
echo "🚀 Ready to start development!"
```

---

## Error Handling

### Handle Common Setup Issues
```bash
# If any critical errors occurred
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Setup encountered issues"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Ensure you're in the main repo directory"
    echo "  2. Check git status for uncommitted changes"
    echo "  3. Verify GitHub issue URL is correct"
    echo "  4. Run /preflight-check for detailed diagnostics"
fi
```

---

## Success Confirmation

The streamlined setup includes:
- ✅ Worktree creation and navigation
- ✅ Virtual environment activation
- ✅ Preflight safety checks
- ✅ Documentation discovery
- ✅ Issue analysis and context
- ✅ Initial todo list generation
- ✅ Clear next steps

All in one command!