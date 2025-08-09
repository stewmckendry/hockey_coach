---
description: "Read feature documentation and get up to speed on a specific feature implementation"
argument-hint: "<feature-name> [documentation-file]"
allowed-tools: ["Read", "Glob", "Grep", "Bash", "TodoWrite", "Task"]
---

# Onboard to Feature

Read comprehensive feature documentation and get up to speed quickly on a specific feature's implementation, setup requirements, and current status.

**Usage**: `$ARGUMENTS` - Feature name or path to documentation file

---

## Phase 1: Locate Documentation

### Find Feature Documentation
```bash
# Parse arguments
FEATURE_INPUT="$ARGUMENTS"

# Check if argument is a file path or feature name
if [[ -f "$FEATURE_INPUT" ]]; then
    FEATURE_DOC="$FEATURE_INPUT"
    FEATURE_NAME=$(basename "$FEATURE_INPUT" | sed 's/_handoff.*//' | sed 's/.md//')
    echo "📄 Using specified documentation: $FEATURE_DOC"
else
    FEATURE_NAME="$FEATURE_INPUT"
    echo "🔍 Searching for documentation for feature: $FEATURE_NAME"
    
    # Search for documentation files
    DOCS_DIR="coordination/feature_docs"
    
    # Find most recent documentation for this feature
    FEATURE_DOC=$(ls -t "$DOCS_DIR"/${FEATURE_NAME}_handoff_*.md 2>/dev/null | head -1)
    
    if [ -z "$FEATURE_DOC" ]; then
        # Try broader search
        FEATURE_DOC=$(find . -name "*${FEATURE_NAME}*handoff*.md" -type f 2>/dev/null | head -1)
    fi
    
    if [ -z "$FEATURE_DOC" ]; then
        echo "❌ No documentation found for feature: $FEATURE_NAME"
        echo ""
        echo "Available feature documentation:"
        ls -la "$DOCS_DIR"/*.md 2>/dev/null || echo "No documentation files found in $DOCS_DIR"
        echo ""
        echo "To generate documentation for a feature, use:"
        echo "/document-feature $FEATURE_NAME"
        exit 1
    fi
fi

echo "✅ Found documentation: $FEATURE_DOC"
echo ""
```

---

## Phase 2: Run Automatic Preflight Checks

### Execute Preflight Validation
```bash
echo "🚦 RUNNING PREFLIGHT CHECKS"
echo "=========================="
echo ""
echo "Running automated checks to prevent common issues..."
echo ""

# Quick preflight check for critical issues
PREFLIGHT_PASSED=true

# Check virtual environment
if [[ "$VIRTUAL_ENV" == *"spacy_env"* ]]; then
    echo "✅ Virtual environment activated"
else
    echo "❌ CRITICAL: Virtual environment NOT activated!"
    echo "   Fix: cd .. && source spacy_env/bin/activate && cd thunder_playbook"
    PREFLIGHT_PASSED=false
fi

# Check MCP endpoints for the most critical issue
echo ""
echo "🔍 Checking MCP endpoints (most common issue)..."
for port in 8000 8001 8002 3003; do
    if lsof -i :$port > /dev/null 2>&1; then
        ENDPOINT=$([[ $port == 3003 || $port == 8002 ]] && echo "/api/mcp" || echo "/mcp")
        CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port$ENDPOINT 2>/dev/null)
        
        if [ "$CODE" = "404" ]; then
            echo "  ❌ Port $port: MCP endpoint MISSING - causes silent failures!"
            echo "     This issue alone can waste 30-40% of development time"
            echo "     Run: /debug-mcp $port --fix"
            PREFLIGHT_PASSED=false
        elif [ "$CODE" = "200" ] || [ "$CODE" = "405" ]; then
            echo "  ✅ Port $port: MCP endpoint working"
        fi
    fi
done

# Quick ChromaDB check
echo ""
echo "🔍 Checking ChromaDB connection..."
python -c "
import sys
sys.path.append('/Users/liammckendry/thunder_playbook')
try:
    from utils.chroma_utils import get_chroma_collection
    collection = get_chroma_collection('drill-source1')
    print('  ✅ ChromaDB connected')
except:
    print('  ❌ ChromaDB not accessible')
    print('     Fix: chroma run --host localhost --port 8000 --no-auth &')
    sys.exit(1)
" || PREFLIGHT_PASSED=false

echo ""
if [ "$PREFLIGHT_PASSED" = false ]; then
    echo "⚠️  PREFLIGHT CHECKS FAILED"
    echo "Fix critical issues above before proceeding!"
    echo ""
    echo "For comprehensive check, run: /preflight-check"
    echo "For MCP debugging, run: /debug-mcp"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Onboarding cancelled. Fix issues and try again."
        exit 1
    fi
else
    echo "✅ All critical preflight checks passed!"
fi
echo ""
```

## Phase 3: Read and Parse Documentation

### Display Feature Overview
```bash
echo "📚 FEATURE DOCUMENTATION OVERVIEW"
echo "=================================="
echo ""

# Extract key sections from documentation
if [ -f "$FEATURE_DOC" ]; then
    # Show executive summary if available
    sed -n '/## Executive Summary/,/^##[^#]/p' "$FEATURE_DOC" | head -20
    
    echo ""
    echo "📋 TABLE OF CONTENTS"
    echo "===================="
    # Extract all section headers
    grep "^##" "$FEATURE_DOC" | sed 's/## /  - /'
    echo ""
fi
```

### Extract Quick Start Information
```bash
echo "🚀 QUICK START GUIDE"
echo "==================="
echo ""

# Extract and display quick start section
sed -n '/## Quick Start/,/^##[^#]/p' "$FEATURE_DOC" | head -50

# If no quick start section, show virtual environment and services
if ! grep -q "## Quick Start" "$FEATURE_DOC"; then
    echo "### Essential Setup Steps:"
    echo ""
    echo "1. **Activate Virtual Environment** (CRITICAL!):"
    echo '```bash'
    echo "cd .. && source spacy_env/bin/activate && cd thunder_playbook"
    echo '```'
    echo ""
    echo "2. **Start Required Services**:"
    echo '```bash'
    echo "python start_services.py  # Starts all services"
    echo '```'
fi
echo ""
```

---

## Phase 3: Understand Current State

### Check Git Status and Branch
```bash
echo "📊 CURRENT STATE ANALYSIS"
echo "========================"
echo ""

# Determine current location
CURRENT_DIR=$(pwd)
echo "📍 Current directory: $CURRENT_DIR"

if [[ "$CURRENT_DIR" == *"worktree"* ]]; then
    echo "🌳 Working in worktree"
    WORKTREE_MODE=true
else
    echo "📦 Working in main repository"
    WORKTREE_MODE=false
fi

echo ""
echo "🌿 Git Information:"
echo "  Branch: $(git branch --show-current)"
echo "  Status: $(git status --porcelain | wc -l) uncommitted changes"
echo "  Latest commit: $(git log -1 --oneline)"
echo ""

# Check if we're on the expected branch from documentation
if grep -q "Branch:" "$FEATURE_DOC"; then
    EXPECTED_BRANCH=$(grep "Branch:" "$FEATURE_DOC" | head -1 | sed 's/.*Branch: *//' | sed 's/[*`]//g' | awk '{print $1}')
    CURRENT_BRANCH=$(git branch --show-current)
    
    if [ "$EXPECTED_BRANCH" != "$CURRENT_BRANCH" ]; then
        echo "⚠️  WARNING: Documentation is for branch '$EXPECTED_BRANCH' but you're on '$CURRENT_BRANCH'"
        echo ""
    fi
fi
```

### Verify Service Dependencies
```bash
echo "🔧 SERVICE DEPENDENCIES CHECK"
echo "============================"
echo ""

# Extract service requirements from documentation
echo "Required Services:"

# Check MCP Server
if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "  ✅ MCP Server (port 8000) - Running"
else
    echo "  ❌ MCP Server (port 8000) - Not running"
    echo "     Start with: python servers/hockey_mcp.py &"
fi

# Check Web App
if curl -s -f http://localhost:3000 > /dev/null 2>&1; then
    echo "  ✅ Web App (port 3000) - Running"
else
    echo "  ⚠️  Web App (port 3000) - Not running"
    echo "     Start with: cd web_app && npm run dev"
fi

# Check Direct API
if curl -s -f http://localhost:3003/api/mcp > /dev/null 2>&1; then
    echo "  ✅ Direct API (port 3003) - Running"
else
    echo "  ⚠️  Direct API (port 3003) - Not running"
    echo "     Start with: python servers/hockey_mcp_direct_api.py &"
fi

echo ""
```

---

## Phase 4: Key Files and Implementation

### List Modified Files
```bash
echo "📁 KEY FILES TO REVIEW"
echo "===================="
echo ""

# Extract file structure from documentation
if grep -q "## File Structure" "$FEATURE_DOC"; then
    sed -n '/## File Structure/,/^##[^#]/p' "$FEATURE_DOC" | head -100
else
    echo "Modified files in this feature:"
    git diff --name-only origin/main...HEAD 2>/dev/null | head -20 || echo "Unable to determine modified files"
fi
echo ""
```

### Show API Endpoints
```bash
echo "🔌 API ENDPOINTS"
echo "==============="
echo ""

# Extract API endpoints from documentation
if grep -q "### API Endpoints" "$FEATURE_DOC"; then
    sed -n '/### API Endpoints/,/^###[^#]/p' "$FEATURE_DOC" | head -30
else
    echo "No API endpoints documented for this feature."
fi
echo ""
```

### Display MCP Tools Used
```bash
echo "🛠️ MCP TOOLS USED"
echo "================"
echo ""

# Extract MCP tools from documentation
if grep -q "### MCP Tools Used" "$FEATURE_DOC"; then
    sed -n '/### MCP Tools Used/,/^###[^#]/p' "$FEATURE_DOC" | head -20
else
    echo "No MCP tools documented for this feature."
fi
echo ""
```

---

## Phase 5: Testing Information

### Show Test Commands
```bash
echo "🧪 TESTING PROCEDURES"
echo "===================="
echo ""

# Extract testing section
if grep -q "## Testing" "$FEATURE_DOC"; then
    sed -n '/## Testing/,/^##[^#]/p' "$FEATURE_DOC" | head -50
else
    echo "Standard test commands:"
    echo '```bash'
    echo "# Python tests"
    echo "cd .. && source spacy_env/bin/activate && cd thunder_playbook"
    echo "python -m pytest tests/ -v"
    echo ""
    echo "# Web app tests"
    echo "cd web_app"
    echo "npm test"
    echo "npm run lint"
    echo "npm run type-check"
    echo '```'
fi
echo ""
```

---

## Phase 6: Create Working Todo List

### Generate Todo List for Feature Work
```python
import re
import os

# Read the documentation file
doc_path = os.environ.get('FEATURE_DOC', '')
feature_name = os.environ.get('FEATURE_NAME', 'Feature')

todos = []

# Standard onboarding todos
todos.append({
    'id': '1',
    'content': 'Activate virtual environment and verify Python setup',
    'status': 'pending'
})

todos.append({
    'id': '2', 
    'content': 'Start required services (MCP, Web App, etc.)',
    'status': 'pending'
})

todos.append({
    'id': '3',
    'content': f'Review key files for {feature_name} feature',
    'status': 'pending'
})

# Check for uncommitted changes
import subprocess
try:
    result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
    if result.stdout.strip():
        todos.append({
            'id': str(len(todos) + 1),
            'content': 'Review uncommitted changes in repository',
            'status': 'pending'
        })
except:
    pass

# Add feature-specific todos based on documentation
if os.path.exists(doc_path):
    with open(doc_path, 'r') as f:
        content = f.read()
        
    # Check for incomplete items
    if 'TODO' in content or '[ ]' in content:
        todos.append({
            'id': str(len(todos) + 1),
            'content': 'Complete pending TODO items from documentation',
            'status': 'pending'
        })
    
    # Check for test requirements
    if '### Manual Testing Checklist' in content:
        todos.append({
            'id': str(len(todos) + 1),
            'content': 'Run manual testing checklist',
            'status': 'pending'
        })

todos.append({
    'id': str(len(todos) + 1),
    'content': 'Run automated tests to verify feature functionality',
    'status': 'pending'
})

# Display the todo list
print("\n📝 SUGGESTED TODO LIST")
print("====================")
print("\nUse TodoWrite tool to create this working list:\n")
print("```python")
print("todos = [")
for todo in todos:
    print(f"    {todo},")
print("]")
print("```")
```

---

## Phase 7: Review Documented Pitfalls

### Display Known Issues from Documentation
```bash
echo ""
echo "⚠️  KNOWN PITFALLS FOR THIS FEATURE"
echo "==================================="
echo ""

# Extract pitfalls section from documentation if it exists
if grep -q "## Common Pitfalls and Solutions" "$FEATURE_DOC"; then
    echo "Found documented issues from previous development:"
    echo ""
    
    # Show the pitfalls section
    sed -n '/## Common Pitfalls and Solutions/,/^## [^#]/p' "$FEATURE_DOC" | head -80
    
    echo ""
    echo "📊 Time Impact Summary:"
    sed -n '/### Time Impact of Common Issues/,/^###/p' "$FEATURE_DOC" | grep "%" | head -10
    
    echo ""
    echo "🛡️ Preventive Measures:"
    sed -n '/### Preventive Measures/,/^###/p' "$FEATURE_DOC" | grep "^[0-9]" | head -10
else
    echo "No documented pitfalls found for this feature."
    echo ""
    echo "Common issues to watch for:"
    echo "1. Missing MCP endpoints (causes 30-40% time loss)"
    echo "2. Empty query handling in search functions"
    echo "3. Complex data extraction from nested structures"
    echo "4. CSS truncation hiding important details"
    echo "5. Schema version mismatches in cached data"
fi
echo ""
```

## Phase 8: Troubleshooting Guide

### Display Common Issues
```bash
echo ""
echo "🔧 TROUBLESHOOTING GUIDE"
echo "======================="
echo ""

# Extract troubleshooting section from documentation
if grep -q "### Common Issues and Solutions" "$FEATURE_DOC"; then
    sed -n '/### Common Issues and Solutions/,/^###[^#]/p' "$FEATURE_DOC"
else
    echo "### Common Issues:"
    echo ""
    echo "**Virtual Environment Not Activated**"
    echo "Error: ModuleNotFoundError: No module named 'fastmcp'"
    echo "Solution: cd .. && source spacy_env/bin/activate && cd thunder_playbook"
    echo ""
    echo "**Port Already in Use**"
    echo "Error: Address already in use"
    echo "Solution: lsof -i :8000 && kill -9 <PID>"
    echo ""
    echo "**ChromaDB Connection Failed**"
    echo "Error: Connection refused"
    echo "Solution: chroma run --host localhost --port 8000 --no-auth &"
fi
echo ""
```

---

## Phase 8: Summary and Next Steps

### Provide Onboarding Summary
```bash
echo "✅ ONBOARDING COMPLETE"
echo "===================="
echo ""
echo "You are now ready to work on: $FEATURE_NAME"
echo ""
echo "📋 Quick Reference:"
echo "  • Documentation: $FEATURE_DOC"
echo "  • Branch: $(git branch --show-current)"
echo "  • Working directory: $(pwd)"
echo ""
echo "🎯 Next Steps:"
echo "  1. Review the generated todo list above"
echo "  2. Activate virtual environment if not done"
echo "  3. Start required services"
echo "  4. Review key files listed in documentation"
echo "  5. Run tests to verify current state"
echo "  6. Continue feature implementation or maintenance"
echo ""
echo "💡 Tips:"
echo "  • Keep documentation updated with /document-feature as you make changes"
echo "  • Use git commits frequently to track progress"
echo "  • Run tests after each significant change"
echo "  • Check service health if encountering errors"
echo ""

# Check for related issues
if grep -q "Related GitHub Issues:" "$FEATURE_DOC"; then
    echo "🔗 Related Issues:"
    grep -A 10 "Related GitHub Issues:" "$FEATURE_DOC" | grep "^- " | head -5
    echo ""
fi

echo "Ready to continue development! 🚀"
```

---

## Interactive Features

### Option to View Full Documentation
```bash
echo ""
echo "📖 View Options:"
echo "  • To view full documentation: cat $FEATURE_DOC"
echo "  • To search documentation: grep -i 'search_term' $FEATURE_DOC"
echo "  • To edit documentation: \$EDITOR $FEATURE_DOC"
echo ""
```

### Generate Status Report
```bash
# Create a brief status report for the feature
cat > /tmp/feature_status_${FEATURE_NAME}.md << EOF
# Feature Status Report: $FEATURE_NAME
**Generated**: $(date -u +%Y-%m-%dT%H:%M:%SZ)

## Current State
- **Branch**: $(git branch --show-current)
- **Uncommitted Changes**: $(git status --porcelain | wc -l)
- **Documentation**: $FEATURE_DOC
- **Services Running**: $(curl -s http://localhost:8000/health > /dev/null 2>&1 && echo "MCP ✅" || echo "MCP ❌")

## Onboarding Completed
- ✅ Documentation located and parsed
- ✅ Current state analyzed
- ✅ Service dependencies checked
- ✅ Key files identified
- ✅ Testing procedures reviewed
- ✅ Todo list generated
- ✅ Troubleshooting guide provided

## Ready for Development
The Claude Code instance is now ready to continue work on this feature.
EOF

echo "📊 Status report saved to: /tmp/feature_status_${FEATURE_NAME}.md"
```

---

## Success Confirmation

The onboarding process is complete! You now have:
- ✅ Located and parsed feature documentation
- ✅ Understood the current repository state
- ✅ Verified service dependencies
- ✅ Identified key files and APIs
- ✅ Reviewed testing procedures
- ✅ Generated a working todo list
- ✅ Accessed troubleshooting information
- ✅ Received clear next steps

You're ready to continue development on the $FEATURE_NAME feature!