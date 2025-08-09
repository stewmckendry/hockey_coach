---
description: "Debug MCP server issues with comprehensive diagnostics and fixes"
argument-hint: "[service-name|port] [--fix]"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "TodoWrite"]
---

# Debug MCP - Specialized MCP Troubleshooting

Comprehensive MCP debugging tool to diagnose and fix common MCP server issues that cause silent failures and wasted development time.

**Usage**: `$ARGUMENTS` - Service name or port number, optional --fix flag to attempt automatic fixes

---

## Phase 1: MCP Service Discovery

### Identify MCP Services
```bash
echo "🔍 MCP DEBUGGING TOOL"
echo "===================="
echo ""

# Parse arguments
SERVICE_ARG=$(echo "$ARGUMENTS" | awk '{print $1}')
FIX_MODE=false
if echo "$ARGUMENTS" | grep -q "\-\-fix"; then
    FIX_MODE=true
    echo "🔧 Fix mode enabled - will attempt automatic repairs"
fi

echo "📡 Discovering MCP services..."
echo ""

# Define known MCP services
declare -A MCP_SERVICES=(
    ["main"]="8000:servers/hockey_mcp.py:Main MCP Server"
    ["diagram"]="8001:servers/hockey_diagram_mcp/server.py:Hockey Diagram MCP"
    ["direct"]="3003:servers/hockey_mcp_direct_api.py:Direct API Wrapper"
    ["diagram-api"]="8002:servers/hockey_diagram_mcp/direct_api.py:Diagram Direct API"
)

# Function to check service
check_mcp_service() {
    local PORT=$1
    local SCRIPT=$2
    local NAME=$3
    
    echo "🔍 Checking $NAME (port $PORT)..."
    
    # Check if running
    if lsof -i :$PORT > /dev/null 2>&1; then
        echo "  ✅ Process running on port $PORT"
        
        # Get process details
        PID=$(lsof -ti :$PORT)
        echo "  📌 PID: $PID"
        
        # Check if it's responding
        if curl -s -f http://localhost:$PORT/health > /dev/null 2>&1; then
            echo "  ✅ Health check passing"
        else
            echo "  ⚠️  Process running but health check failing"
        fi
    else
        echo "  ❌ Not running"
        echo "  📝 Start command: python $SCRIPT"
    fi
    
    # Check for MCP endpoint
    echo "  🔌 Checking MCP endpoint..."
    check_mcp_endpoint_detailed $PORT
    echo ""
}

# Check specific service or all
if [ -n "$SERVICE_ARG" ]; then
    # Check if argument is a port number
    if [[ "$SERVICE_ARG" =~ ^[0-9]+$ ]]; then
        PORT=$SERVICE_ARG
        echo "Checking service on port $PORT..."
        
        # Find which service uses this port
        for key in "${!MCP_SERVICES[@]}"; do
            IFS=':' read -r service_port script name <<< "${MCP_SERVICES[$key]}"
            if [ "$service_port" = "$PORT" ]; then
                check_mcp_service $service_port "$script" "$name"
                break
            fi
        done
    else
        # Check by service name
        if [ -n "${MCP_SERVICES[$SERVICE_ARG]}" ]; then
            IFS=':' read -r port script name <<< "${MCP_SERVICES[$SERVICE_ARG]}"
            check_mcp_service $port "$script" "$name"
        else
            echo "❌ Unknown service: $SERVICE_ARG"
            echo "   Available: main, diagram, direct, diagram-api"
        fi
    fi
else
    # Check all services
    for key in "${!MCP_SERVICES[@]}"; do
        IFS=':' read -r port script name <<< "${MCP_SERVICES[$key]}"
        check_mcp_service $port "$script" "$name"
    done
fi
```

### Detailed MCP Endpoint Check
```bash
check_mcp_endpoint_detailed() {
    local PORT=$1
    
    # Determine endpoint path based on port
    case $PORT in
        8000|8001)
            ENDPOINT="/mcp"
            ;;
        3003|8002)
            ENDPOINT="/api/mcp"
            ;;
        *)
            ENDPOINT="/mcp"
            ;;
    esac
    
    # Test basic connectivity
    RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:${PORT}${ENDPOINT} 2>/dev/null)
    HTTP_CODE=$(echo "$RESPONSE" | tail -1)
    
    if [ "$HTTP_CODE" = "404" ]; then
        echo "    ❌ CRITICAL: MCP endpoint NOT FOUND at ${ENDPOINT}"
        echo "    🔥 This causes silent failures in MCP tool calls!"
        
        if [ "$FIX_MODE" = true ]; then
            echo "    🔧 Attempting to add MCP endpoint..."
            attempt_mcp_fix $PORT
        else
            echo "    💡 Run with --fix to attempt automatic repair"
            echo "    📝 Or manually add MCP handler to the service"
        fi
        return 1
    elif [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "405" ]; then
        echo "    ✅ MCP endpoint exists"
        
        # Test JSONRPC methods
        test_mcp_methods $PORT $ENDPOINT
    else
        echo "    ⚠️  Unexpected response: HTTP $HTTP_CODE"
    fi
}
```

---

## Phase 2: MCP Protocol Testing

### Test MCP JSONRPC Methods
```bash
test_mcp_methods() {
    local PORT=$1
    local ENDPOINT=$2
    
    echo "    🧪 Testing MCP methods..."
    
    # Test tools/list
    TOOLS_RESPONSE=$(curl -s -X POST http://localhost:${PORT}${ENDPOINT} \
        -H "Content-Type: application/json" \
        -d '{"jsonrpc":"2.0","method":"tools/list","id":1}' 2>/dev/null)
    
    if echo "$TOOLS_RESPONSE" | grep -q '"result"'; then
        TOOL_COUNT=$(echo "$TOOLS_RESPONSE" | python -c "
import json, sys
try:
    d = json.load(sys.stdin)
    tools = d.get('result', {}).get('tools', [])
    print(len(tools))
    if tools:
        print('    Tools available:')
        for t in tools[:5]:  # Show first 5 tools
            print(f'      - {t.get(\"name\", \"unknown\")}')
except:
    print('0')
" 2>/dev/null)
        echo "    ✅ tools/list: $TOOL_COUNT tools found"
    else
        echo "    ❌ tools/list failed"
        echo "    Response: $(echo "$TOOLS_RESPONSE" | head -c 200)"
    fi
    
    # Test specific tool call
    if echo "$TOOLS_RESPONSE" | grep -q "search_hockey_knowledge\|generate_hockey_diagram"; then
        echo "    🧪 Testing tool execution..."
        
        # Pick appropriate test based on available tools
        if echo "$TOOLS_RESPONSE" | grep -q "list_hockey_formations"; then
            TEST_TOOL="list_hockey_formations"
            TEST_ARGS="{}"
        elif echo "$TOOLS_RESPONSE" | grep -q "search_hockey_knowledge"; then
            TEST_TOOL="search_hockey_knowledge"
            TEST_ARGS='{"query":"test","collection":"drill-source1","n_results":1}'
        else
            TEST_TOOL=""
        fi
        
        if [ -n "$TEST_TOOL" ]; then
            TOOL_RESPONSE=$(curl -s -X POST http://localhost:${PORT}${ENDPOINT} \
                -H "Content-Type: application/json" \
                -d "{
                    \"jsonrpc\":\"2.0\",
                    \"method\":\"tools/call\",
                    \"params\":{
                        \"name\":\"$TEST_TOOL\",
                        \"arguments\":$TEST_ARGS
                    },
                    \"id\":2
                }" 2>/dev/null)
            
            if echo "$TOOL_RESPONSE" | grep -q '"result"'; then
                echo "    ✅ Tool execution working ($TEST_TOOL)"
            else
                echo "    ❌ Tool execution failed"
                echo "    Error: $(echo "$TOOL_RESPONSE" | python -c "import json, sys; d=json.load(sys.stdin); print(d.get('error', {}).get('message', 'unknown'))" 2>/dev/null)"
            fi
        fi
    fi
}
```

---

## Phase 3: Common MCP Issues Detection

### Detect Known Problems
```bash
echo ""
echo "🔍 COMMON MCP ISSUES SCAN"
echo "------------------------"

ISSUES_FOUND=0

# Issue 1: Missing MCP endpoint handler
echo ""
echo "1. Missing MCP Endpoint Handler"
for port in 8000 8001 8002 3003; do
    if lsof -i :$port > /dev/null 2>&1; then
        RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/mcp 2>/dev/null)
        if [ "$RESPONSE" = "404" ]; then
            echo "  ❌ Port $port: MCP endpoint missing (404)"
            echo "     This causes all MCP tool calls to fail silently!"
            ((ISSUES_FOUND++))
        fi
    fi
done

if [ $ISSUES_FOUND -eq 0 ]; then
    echo "  ✅ All running services have MCP endpoints"
fi

# Issue 2: Spec extraction complexity
echo ""
echo "2. Complex Spec Extraction Patterns"
if [ -f "web_app/lib/server/diagramSpecExtractor.ts" ]; then
    COMPLEXITY=$(grep -c "agentTraces\|parserSpec\|RunResult" web_app/lib/server/diagramSpecExtractor.ts 2>/dev/null || echo "0")
    if [ $COMPLEXITY -gt 5 ]; then
        echo "  ⚠️  High complexity in spec extraction ($COMPLEXITY patterns)"
        echo "     Multiple data formats can cause extraction failures"
        ((ISSUES_FOUND++))
    else
        echo "  ✅ Spec extraction appears manageable"
    fi
else
    echo "  ℹ️  Spec extractor not found (skip if not using diagrams)"
fi

# Issue 3: Empty query handling
echo ""
echo "3. Empty Query Error Handling"
SEARCH_FILES=$(find . -name "*.ts" -o -name "*.py" | xargs grep -l "search_cached_diagrams\|embeddings" 2>/dev/null | head -5)
if [ -n "$SEARCH_FILES" ]; then
    EMPTY_HANDLING=$(echo "$SEARCH_FILES" | xargs grep -c "query.*||.*default\|if.*not.*query\|query.*or.*''" 2>/dev/null | grep -v ":0" | wc -l)
    if [ $EMPTY_HANDLING -eq 0 ]; then
        echo "  ⚠️  No empty query handling found"
        echo "     OpenAI embeddings fail with: 'input is invalid'"
        ((ISSUES_FOUND++))
    else
        echo "  ✅ Empty query handling found in $EMPTY_HANDLING files"
    fi
else
    echo "  ℹ️  No search functions found"
fi

# Issue 4: Schema version conflicts
echo ""
echo "4. Schema Version Conflicts"
python -c "
import sys, json
sys.path.append('/Users/liammckendry/thunder_playbook')

issues = 0
try:
    from utils.chroma_utils import get_chroma_collection
    
    # Check for mixed schemas
    try:
        collection = get_chroma_collection('cached_diagrams')
        results = collection.get(limit=10)
        
        if results and results['metadatas']:
            old_count = 0
            new_count = 0
            
            for metadata in results['metadatas']:
                if 'spec' in metadata:
                    spec = json.loads(metadata.get('spec', '{}'))
                    if 'zone' in spec:
                        old_count += 1
                    if 'players' in spec and any('x' in p for p in spec.get('players', [])):
                        new_count += 1
            
            if old_count > 0 and new_count > 0:
                print(f'  ⚠️  Mixed schemas: {old_count} old, {new_count} new')
                print('     This causes validation errors on retrieval')
                issues = 1
            else:
                print('  ✅ Schema consistency maintained')
        else:
            print('  ℹ️  No cached data to check')
    except:
        print('  ℹ️  Cached diagrams not in use')
        
except Exception as e:
    print(f'  ❌ Error checking schemas: {e}')
    issues = 1

sys.exit(issues)
" && ((ISSUES_FOUND+=$?))

echo ""
if [ $ISSUES_FOUND -gt 0 ]; then
    echo "🔥 Found $ISSUES_FOUND critical MCP issues!"
    if [ "$FIX_MODE" = true ]; then
        echo "🔧 Attempting fixes..."
    else
        echo "💡 Run with --fix flag to attempt automatic fixes"
    fi
else
    echo "✅ No critical MCP issues detected"
fi
```

---

## Phase 4: Automatic Fix Attempts

### Attempt to Fix MCP Issues
```bash
attempt_mcp_fix() {
    local PORT=$1
    
    echo "    🔧 Attempting automatic fix for port $PORT..."
    
    # Determine which service and file to fix
    case $PORT in
        8002)
            FILE="servers/hockey_diagram_mcp/direct_api.py"
            if [ -f "$FILE" ]; then
                echo "    📝 Adding MCP handler to $FILE..."
                
                # Check if file already has partial MCP support
                if grep -q "async def handle_mcp" "$FILE"; then
                    echo "    ℹ️  MCP handler function exists but may not be wired up"
                    echo "    📝 Check that /api/mcp route calls handle_mcp()"
                else
                    echo "    📝 Would add MCP handler code here"
                    echo "    💡 Manual fix required: Add MCP endpoint handler"
                    echo ""
                    echo "    Example code to add:"
                    echo '    ```python'
                    echo '    @app.post("/api/mcp")'
                    echo '    async def handle_mcp(request: dict):'
                    echo '        """Handle MCP protocol requests"""'
                    echo '        # Forward to MCP server on port 8001'
                    echo '        async with httpx.AsyncClient() as client:'
                    echo '            response = await client.post('
                    echo '                "http://localhost:8001/mcp",'
                    echo '                json=request,'
                    echo '                timeout=30.0'
                    echo '            )'
                    echo '        return response.json()'
                    echo '    ```'
                fi
            fi
            ;;
        *)
            echo "    ℹ️  Automatic fix not available for port $PORT"
            echo "    📝 Manual intervention required"
            ;;
    esac
}

if [ "$FIX_MODE" = true ] && [ $ISSUES_FOUND -gt 0 ]; then
    echo ""
    echo "🔧 FIX ATTEMPTS"
    echo "---------------"
    
    # Run specific fixes based on issues found
    echo "Fixes would be applied here based on detected issues"
fi
```

---

## Phase 5: MCP Performance Analysis

### Analyze MCP Performance
```bash
echo ""
echo "⚡ MCP PERFORMANCE ANALYSIS"
echo "--------------------------"

# Test response times
test_mcp_performance() {
    local PORT=$1
    local ENDPOINT=$2
    local NAME=$3
    
    echo "Testing $NAME performance..."
    
    # Measure tools/list response time
    START=$(date +%s%N)
    curl -s -X POST http://localhost:${PORT}${ENDPOINT} \
        -H "Content-Type: application/json" \
        -d '{"jsonrpc":"2.0","method":"tools/list","id":1}' > /dev/null 2>&1
    END=$(date +%s%N)
    
    DURATION=$((($END - $START) / 1000000))
    
    if [ $DURATION -lt 100 ]; then
        echo "  ✅ Response time: ${DURATION}ms (excellent)"
    elif [ $DURATION -lt 500 ]; then
        echo "  ✅ Response time: ${DURATION}ms (good)"
    elif [ $DURATION -lt 2000 ]; then
        echo "  ⚠️  Response time: ${DURATION}ms (slow)"
    else
        echo "  ❌ Response time: ${DURATION}ms (very slow)"
    fi
}

# Test each running service
for port in 8000 8001 8002 3003; do
    if curl -s -f http://localhost:$port/health > /dev/null 2>&1; then
        case $port in
            8000) test_mcp_performance $port "/mcp" "Main MCP" ;;
            8001) test_mcp_performance $port "/mcp" "Diagram MCP" ;;
            8002) test_mcp_performance $port "/api/mcp" "Diagram API" ;;
            3003) test_mcp_performance $port "/api/mcp" "Direct API" ;;
        esac
    fi
done
```

---

## Phase 6: Generate Debug Report

### Create Comprehensive Debug Report
```bash
echo ""
echo "📊 MCP DEBUG REPORT"
echo "=================="
echo ""

# Save debug report
REPORT_FILE="/tmp/mcp_debug_$(date +%Y%m%d_%H%M%S).md"

cat > "$REPORT_FILE" << EOF
# MCP Debug Report
**Generated**: $(date -u +%Y-%m-%dT%H:%M:%SZ)

## Services Status
$(for port in 8000 8001 8002 3003; do
    if lsof -i :$port > /dev/null 2>&1; then
        echo "- Port $port: ✅ Running (PID: $(lsof -ti :$port))"
    else
        echo "- Port $port: ❌ Not running"
    fi
done)

## MCP Endpoints
$(for port in 8000 8001 8002 3003; do
    if curl -s -f http://localhost:$port/health > /dev/null 2>&1; then
        endpoint=$([[ $port == 3003 || $port == 8002 ]] && echo "/api/mcp" || echo "/mcp")
        code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port$endpoint 2>/dev/null)
        echo "- Port $port$endpoint: HTTP $code"
    fi
done)

## Issues Found
- Critical Issues: $ISSUES_FOUND
- Fix Mode: $FIX_MODE

## Recommendations
1. Always verify MCP endpoints exist before assuming tools work
2. Test with empty queries to catch embedding errors early
3. Monitor response times for performance issues
4. Implement proper error logging for debugging
5. Consider schema versioning for data compatibility

EOF

echo "📄 Debug report saved to: $REPORT_FILE"
echo ""

# Generate actionable todos
echo "📝 RECOMMENDED ACTIONS"
echo "====================="

python -c "
todos = []

# Add todos based on issues found
if $ISSUES_FOUND > 0:
    todos.append({
        'id': '1',
        'content': 'Fix missing MCP endpoints on affected services',
        'status': 'pending'
    })
    
    todos.append({
        'id': '2',
        'content': 'Add empty query handling to search functions',
        'status': 'pending'
    })
    
    todos.append({
        'id': '3',
        'content': 'Implement schema migration for mixed data formats',
        'status': 'pending'
    })

if todos:
    print('Use TodoWrite to track fixes:')
    print('todos = [')
    for todo in todos:
        print(f'    {todo},')
    print(']')
else:
    print('✅ No critical actions required')
"

echo ""
echo "🔍 Debug session complete!"
```

---

## Success Criteria

MCP debugging is complete when:
- ✅ All MCP services identified and checked
- ✅ MCP endpoints verified and tested
- ✅ Common issues detected and reported
- ✅ Performance metrics captured
- ✅ Fix attempts made (if --fix enabled)
- ✅ Debug report generated with recommendations

This tool helps quickly identify and resolve MCP issues that commonly cause silent failures and development delays!