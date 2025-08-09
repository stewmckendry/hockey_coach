---
description: "Run comprehensive preflight checks before starting development to catch common issues early"
argument-hint: "[feature-name] [--verbose]"
allowed-tools: ["Read", "Bash", "Grep", "TodoWrite"]
---

# Preflight Check - Prevent Development Issues

Run comprehensive checks to verify services, endpoints, and dependencies are properly configured before starting development. This prevents the most common issues that cause rework and debugging delays.

**Usage**: `$ARGUMENTS` - Optional feature name for feature-specific checks, --verbose for detailed output

---

## Phase 1: Environment Verification

### Check Virtual Environment
```bash
echo "🔍 PREFLIGHT CHECK INITIATED"
echo "============================="
echo ""
echo "1️⃣ ENVIRONMENT VERIFICATION"
echo "----------------------------"

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == *"spacy_env"* ]]; then
    echo "✅ Virtual environment activated: $VIRTUAL_ENV"
    PYTHON_PATH=$(which python)
    echo "   Python: $PYTHON_PATH"
    echo "   Version: $(python --version)"
else
    echo "❌ CRITICAL: Virtual environment NOT activated!"
    echo "   Fix: cd .. && source spacy_env/bin/activate && cd thunder_playbook"
    echo ""
    echo "⚠️  STOPPING: Cannot proceed without virtual environment"
    exit 1
fi

# Check critical Python packages
echo ""
echo "📦 Checking Python dependencies..."
python -c "
import sys
critical_packages = {
    'fastmcp': 'MCP server functionality',
    'openai': 'AI operations', 
    'chromadb': 'Vector database',
    'pydantic': 'Data validation'
}

missing = []
for package, purpose in critical_packages.items():
    try:
        __import__(package)
        print(f'  ✅ {package}: Available ({purpose})')
    except ImportError:
        print(f'  ❌ {package}: MISSING ({purpose})')
        missing.append(package)

if missing:
    print('')
    print('  ⚠️  Install missing packages: pip install ' + ' '.join(missing))
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "⚠️  Fix dependency issues before proceeding"
    exit 1
fi
```

---

## Phase 2: Service Health Checks

### Check Core Services
```bash
echo ""
echo "2️⃣ SERVICE HEALTH CHECKS"
echo "------------------------"

SERVICES_OK=true

# MCP Server on port 8000
echo ""
echo "🔧 MCP Server (port 8000):"
if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "  ✅ Running and healthy"
    
    # Check MCP tools availability
    echo "  📋 Checking MCP tools..."
    TOOLS_RESPONSE=$(curl -s http://localhost:8000/mcp/list_tools 2>/dev/null)
    
    if [ -n "$TOOLS_RESPONSE" ]; then
        TOOL_COUNT=$(echo "$TOOLS_RESPONSE" | python -c "import json, sys; d=json.load(sys.stdin); print(len(d.get('tools', [])))" 2>/dev/null || echo "0")
        echo "  ✅ $TOOL_COUNT tools available"
    else
        echo "  ⚠️  Could not verify tools - check /mcp/list_tools endpoint"
    fi
else
    echo "  ❌ NOT RUNNING"
    echo "  Fix: python servers/hockey_mcp.py &"
    SERVICES_OK=false
fi

# Direct API on port 3003
echo ""
echo "🔌 Direct API (port 3003):"
if curl -s -f http://localhost:3003/api/mcp > /dev/null 2>&1; then
    echo "  ✅ Running and responding"
else
    echo "  ⚠️  Not running (optional)"
    echo "  Start if needed: python servers/hockey_mcp_direct_api.py &"
fi

# Web App on port 3000
echo ""
echo "🌐 Web App (port 3000):"
if curl -s -f http://localhost:3000 > /dev/null 2>&1; then
    echo "  ✅ Running and accessible"
else
    echo "  ⚠️  Not running (optional)"
    echo "  Start if needed: cd web_app && npm run dev"
fi

# Hockey Diagram MCP on port 8001
echo ""
echo "🏒 Hockey Diagram MCP (port 8001):"
if curl -s -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "  ✅ Running and healthy"
else
    echo "  ⚠️  Not running (optional for hockey diagram features)"
    echo "  Start if needed: cd servers/hockey_diagram_mcp && python server.py"
fi

# ChromaDB
echo ""
echo "💾 ChromaDB:"
python -c "
import sys
sys.path.append('/Users/liammckendry/thunder_playbook')
try:
    from utils.chroma_utils import get_chroma_collection
    collection = get_chroma_collection('drill-source1')
    count = collection.count()
    print(f'  ✅ Connected - {count} items in test collection')
except Exception as e:
    print(f'  ❌ Connection failed: {e}')
    print('  Fix: chroma run --host localhost --port 8000 --no-auth &')
    sys.exit(1)
" || SERVICES_OK=false

if [ "$SERVICES_OK" = false ]; then
    echo ""
    echo "⚠️  Some required services are not running. Fix issues above before proceeding."
fi
```

---

## Phase 3: MCP Endpoint Verification

### Verify Critical MCP Endpoints
```bash
echo ""
echo "3️⃣ MCP ENDPOINT VERIFICATION"
echo "----------------------------"
echo "Checking for common MCP endpoint issues..."

# Function to check MCP endpoint
check_mcp_endpoint() {
    local PORT=$1
    local SERVICE=$2
    local ENDPOINT=$3
    
    echo ""
    echo "🔍 Checking $SERVICE MCP endpoint..."
    
    # First check if service is running
    if ! curl -s -f http://localhost:${PORT}/health > /dev/null 2>&1; then
        echo "  ⏭️  Skipping - service not running"
        return
    fi
    
    # Check for /mcp endpoint
    RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:${PORT}${ENDPOINT} 2>/dev/null)
    HTTP_CODE=$(echo "$RESPONSE" | tail -1)
    BODY=$(echo "$RESPONSE" | head -n -1)
    
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "405" ]; then
        echo "  ✅ MCP endpoint exists at port $PORT$ENDPOINT"
        
        # Try to list tools
        if [[ "$ENDPOINT" == "/mcp" ]]; then
            TOOLS=$(curl -s -X POST http://localhost:${PORT}/mcp \
                -H "Content-Type: application/json" \
                -d '{"jsonrpc":"2.0","method":"tools/list","id":1}' 2>/dev/null)
            
            if echo "$TOOLS" | grep -q "result"; then
                TOOL_COUNT=$(echo "$TOOLS" | python -c "import json, sys; d=json.load(sys.stdin); print(len(d.get('result', {}).get('tools', [])))" 2>/dev/null || echo "0")
                echo "  ✅ MCP tools accessible: $TOOL_COUNT tools found"
            else
                echo "  ⚠️  MCP endpoint exists but tools/list failed"
                echo "  Debug: $TOOLS"
            fi
        fi
    elif [ "$HTTP_CODE" = "404" ]; then
        echo "  ❌ CRITICAL: MCP endpoint NOT FOUND at port $PORT$ENDPOINT"
        echo "  This is a common issue that causes silent failures!"
        echo "  Fix: Add MCP handler to the service's API server"
        return 1
    else
        echo "  ⚠️  Unexpected response: HTTP $HTTP_CODE"
    fi
}

# Check main MCP server
check_mcp_endpoint 8000 "Main MCP Server" "/mcp"

# Check hockey diagram MCP
check_mcp_endpoint 8001 "Hockey Diagram MCP" "/mcp"

# Check direct API MCP endpoint
check_mcp_endpoint 3003 "Direct API" "/api/mcp"

# Check if hockey diagram direct API has MCP
if curl -s -f http://localhost:8002/health > /dev/null 2>&1; then
    check_mcp_endpoint 8002 "Hockey Diagram Direct API" "/api/mcp"
fi
```

---

## Phase 4: Data Schema Validation

### Check for Schema Mismatches
```bash
echo ""
echo "4️⃣ DATA SCHEMA VALIDATION"
echo "-------------------------"

# Check ChromaDB schema consistency
echo "🔍 Checking ChromaDB schema consistency..."

python -c "
import sys
import json
sys.path.append('/Users/liammckendry/thunder_playbook')

try:
    from utils.chroma_utils import get_chroma_collection
    
    # Check cached diagrams collection if it exists
    try:
        collection = get_chroma_collection('cached_diagrams')
        
        # Sample a few entries to check schema
        results = collection.get(limit=3)
        
        if results and results['metadatas']:
            schemas_found = set()
            for metadata in results['metadatas']:
                # Check for old vs new schema
                if 'spec' in metadata:
                    spec = json.loads(metadata.get('spec', '{}'))
                    if 'zone' in spec:
                        schemas_found.add('old_zone_based')
                    if 'players' in spec and any('x' in p for p in spec.get('players', [])):
                        schemas_found.add('new_coordinate_based')
            
            if len(schemas_found) > 1:
                print('  ⚠️  WARNING: Mixed schemas detected in cached_diagrams!')
                print('     Found:', ', '.join(schemas_found))
                print('     This can cause validation errors when retrieving entries')
                print('     Consider migration or backward compatibility handling')
            else:
                print('  ✅ Schema consistency check passed')
        else:
            print('  ℹ️  No cached diagrams found to check')
            
    except Exception as e:
        print(f'  ℹ️  Cached diagrams collection not found (normal if not using diagram caching)')
        
except Exception as e:
    print(f'  ❌ Error checking schemas: {e}')
"
```

---

## Phase 5: Common Pitfall Detection

### Check for Known Issues
```bash
echo ""
echo "5️⃣ COMMON PITFALL DETECTION"
echo "---------------------------"

ISSUES_FOUND=false

# Check for empty query handling in search functions
echo "🔍 Checking for empty query handling..."
if [ -f "web_app/app/api/hockey-diagram/library/route.ts" ]; then
    if grep -q "search_cached_diagrams" web_app/app/api/hockey-diagram/library/route.ts; then
        if ! grep -q "list_all_cached_diagrams\|query.*||.*'hockey'" web_app/app/api/hockey-diagram/library/route.ts; then
            echo "  ⚠️  WARNING: search_cached_diagrams may fail with empty queries"
            echo "     OpenAI embeddings require non-empty input"
            echo "     Consider using list_all_cached_diagrams for browsing"
            ISSUES_FOUND=true
        else
            echo "  ✅ Empty query handling appears to be implemented"
        fi
    fi
else
    echo "  ℹ️  Library route not found (skip if not using diagram library)"
fi

# Check for CSS truncation issues
echo ""
echo "🔍 Checking for CSS truncation issues..."
if find web_app -name "*.css" -o -name "*.tsx" -o -name "*.jsx" | xargs grep -l "truncate\|text-ellipsis\|overflow-hidden" > /dev/null 2>&1; then
    echo "  ℹ️  Found truncation CSS classes - verify long content displays properly"
    echo "     Common issue: Technical details get cut off with ellipsis"
    echo "     Check: line-clamp, truncate, max-w settings on detail views"
fi

# Check for state management complexity
echo ""
echo "🔍 Checking state management patterns..."
if [ -f "web_app/components/hockey-diagram/DiagramLibrary.tsx" ]; then
    STATE_COUNT=$(grep -c "useState\|useReducer" web_app/components/hockey-diagram/DiagramLibrary.tsx 2>/dev/null || echo "0")
    if [ "$STATE_COUNT" -gt 10 ]; then
        echo "  ⚠️  High state complexity detected: $STATE_COUNT state declarations"
        echo "     Consider consolidating related states into objects or using useReducer"
        ISSUES_FOUND=true
    else
        echo "  ✅ State management appears manageable: $STATE_COUNT state declarations"
    fi
fi

# Check for proper error handling
echo ""
echo "🔍 Checking error handling..."
ERROR_PATTERNS=$(grep -r "catch.*{.*}" --include="*.ts" --include="*.tsx" --include="*.py" . 2>/dev/null | grep -c "console.log\|pass\|continue" || echo "0")
if [ "$ERROR_PATTERNS" -gt 5 ]; then
    echo "  ⚠️  Found $ERROR_PATTERNS instances of silent error handling"
    echo "     Silent failures make debugging difficult"
    echo "     Consider proper error logging and user feedback"
    ISSUES_FOUND=true
else
    echo "  ✅ Error handling appears adequate"
fi

if [ "$ISSUES_FOUND" = true ]; then
    echo ""
    echo "⚠️  Some potential issues detected. Review warnings above."
fi
```

---

## Phase 6: Feature-Specific Checks

### Run Feature-Specific Validation
```bash
FEATURE_NAME=$(echo "$ARGUMENTS" | awk '{print $1}')

if [ -n "$FEATURE_NAME" ] && [ "$FEATURE_NAME" != "--verbose" ]; then
    echo ""
    echo "6️⃣ FEATURE-SPECIFIC CHECKS: $FEATURE_NAME"
    echo "----------------------------------------"
    
    # Hockey Diagram specific checks
    if [[ "$FEATURE_NAME" == *"diagram"* ]] || [[ "$FEATURE_NAME" == *"hockey"* ]]; then
        echo "🏒 Running hockey diagram specific checks..."
        
        # Check diagram server endpoints
        if curl -s -f http://localhost:8001/health > /dev/null 2>&1; then
            echo "  ✅ Hockey diagram MCP server running"
            
            # Test diagram generation
            echo "  🧪 Testing diagram generation..."
            TEST_RESULT=$(curl -s -X POST http://localhost:8001/mcp \
                -H "Content-Type: application/json" \
                -d '{
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "list_hockey_formations",
                        "arguments": {}
                    },
                    "id": 1
                }' 2>/dev/null)
            
            if echo "$TEST_RESULT" | grep -q "formations"; then
                echo "  ✅ Diagram tools responding correctly"
            else
                echo "  ⚠️  Diagram tools not responding as expected"
            fi
        fi
        
        # Check for agent dependencies
        if [ -f ".env" ] && grep -q "OPENAI_API_KEY" .env; then
            echo "  ✅ OpenAI API key configured"
        else
            echo "  ⚠️  OpenAI API key not found - agent features may not work"
        fi
    fi
    
    # Add more feature-specific checks as needed
fi
```

---

## Phase 7: Generate Preflight Report

### Create Summary Report
```bash
echo ""
echo "📊 PREFLIGHT CHECK SUMMARY"
echo "========================="
echo ""

# Generate pass/fail summary
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0

# Count results from output above (simplified for example)
if [[ "$VIRTUAL_ENV" == *"spacy_env"* ]]; then
    ((CHECKS_PASSED++))
else
    ((CHECKS_FAILED++))
fi

if [ "$SERVICES_OK" = true ]; then
    ((CHECKS_PASSED++))
else
    ((CHECKS_WARNING++))
fi

echo "Results:"
echo "  ✅ Passed: $CHECKS_PASSED critical checks"
echo "  ⚠️  Warnings: $CHECKS_WARNING non-critical issues"
echo "  ❌ Failed: $CHECKS_FAILED critical issues"
echo ""

if [ "$CHECKS_FAILED" -gt 0 ]; then
    echo "🛑 PREFLIGHT FAILED"
    echo "   Fix critical issues before starting development"
    echo "   This will save significant debugging time!"
else
    echo "✅ PREFLIGHT PASSED"
    echo "   System ready for development"
    
    if [ "$CHECKS_WARNING" -gt 0 ]; then
        echo "   ⚠️  Review warnings above for optimal development experience"
    fi
fi

echo ""
echo "💡 Tips:"
echo "  • Run this check before starting any feature work"
echo "  • Run again if you encounter unexpected errors"
echo "  • Add --verbose flag for more detailed output"
echo "  • Document any new issues with /document-feature"
```

---

## Phase 8: Generate Todo List for Issues

### Create Actionable Todo List
```python
import json

# Generate todo list for fixing issues
todos = []
todo_id = 1

# Check environment issues
import os
if 'VIRTUAL_ENV' not in os.environ or 'spacy_env' not in os.environ['VIRTUAL_ENV']:
    todos.append({
        'id': str(todo_id),
        'content': 'Activate virtual environment: cd .. && source spacy_env/bin/activate && cd thunder_playbook',
        'status': 'pending'
    })
    todo_id += 1

# Add todos for service issues (would be populated based on actual check results)
print("\n📝 SUGGESTED FIXES")
print("==================")

if todos:
    print("\nUse TodoWrite to create this fix list:")
    print("```python")
    print("todos = [")
    for todo in todos:
        print(f"    {todo},")
    print("]")
    print("```")
else:
    print("\n✅ No critical issues to fix!")

print("\n🚀 Ready to proceed with development once all checks pass!")
```

---

## Success Criteria

Preflight check is complete when:
- ✅ Virtual environment is properly activated
- ✅ All required services are running and healthy
- ✅ MCP endpoints are accessible and responding
- ✅ No schema mismatches detected
- ✅ Common pitfalls are checked and addressed
- ✅ Feature-specific validations pass

This preflight check helps prevent the most common issues that cause development delays and rework!