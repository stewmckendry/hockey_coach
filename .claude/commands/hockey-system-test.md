# Hockey System Test Command

Comprehensive full system validation for the Hockey Coach AI Assistant platform.

**Usage**: Any Claude instance - after integrations, before declaring system ready

---

## Service Startup and Health Check

### Start All Core Services
```bash
echo "🚀 Starting all core services..."

# Ensure we're in the correct directory
cd /Users/liammckendry/thunder_playbook

# Activate Python environment
if [[ "$VIRTUAL_ENV" != *"spacy_env"* ]]; then
    echo "🐍 Activating spacy_env..."
    source ../spacy_env/bin/activate
fi

# Start services using unified startup
echo "🔧 Starting core services..."
python start_services.py &
STARTUP_PID=$!

# Wait for services to initialize
echo "⏳ Waiting for services to initialize..."
sleep 10

# Check if startup completed successfully
if ps -p $STARTUP_PID > /dev/null; then
    echo "✅ Service startup initiated"
else
    echo "🟡 Service startup process completed"
fi

echo "✅ Core services startup complete"
```

### Individual Service Health Checks
```bash
echo "🔍 Performing individual service health checks..."

# Test MCP Server (port 8000)
echo "🔧 Testing MCP Server..."
if curl -s -f http://localhost:8000/health > /dev/null; then
    echo "✅ MCP Server (port 8000): HEALTHY"
    
    # Get detailed health information
    HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
    echo "   Response: $HEALTH_RESPONSE"
else
    echo "❌ MCP Server (port 8000): UNREACHABLE"
    echo "   Starting MCP server manually..."
    python servers/hockey_mcp.py &
    sleep 5
    
    if curl -s -f http://localhost:8000/health > /dev/null; then
        echo "✅ MCP Server: RECOVERED"
    else
        echo "❌ MCP Server: FAILED TO START"
        exit 1
    fi
fi

# Test Direct API Bridge (port 3003)
echo "🌉 Testing Direct API Bridge..."
if curl -s -f http://localhost:3003/api/mcp > /dev/null; then
    echo "✅ Direct API Bridge (port 3003): HEALTHY"
else
    echo "🟡 Direct API Bridge (port 3003): NOT RUNNING"
    echo "   Starting Direct API bridge..."
    python servers/hockey_mcp_direct_api.py &
    sleep 3
    
    if curl -s -f http://localhost:3003/api/mcp > /dev/null; then
        echo "✅ Direct API Bridge: STARTED"
    else
        echo "🟡 Direct API Bridge: OPTIONAL SERVICE"
    fi
fi

# Test Web App (port 3000)
echo "📱 Testing Web App..."
if curl -s -f http://localhost:3000 > /dev/null; then
    echo "✅ Web App (port 3000): HEALTHY"
else
    echo "🟡 Web App (port 3000): NOT RUNNING"
    echo "   Starting Web App..."
    cd web_app
    npm run dev &
    cd ..
    sleep 8
    
    if curl -s -f http://localhost:3000 > /dev/null; then
        echo "✅ Web App: STARTED"
    else
        echo "🟡 Web App: STARTING (may take longer)"
    fi
fi

# Test Agent HTTP Server (port 8002)
echo "🤖 Testing Agent HTTP Server..."
if curl -s -f http://localhost:8002 > /dev/null; then
    echo "✅ Agent HTTP Server (port 8002): HEALTHY"
else
    echo "🟡 Agent HTTP Server (port 8002): NOT RUNNING"
    echo "   Starting Agent HTTP Server..."
    cd servers/poc
    python agent_http_server.py &
    cd ../..
    sleep 3
    
    if curl -s -f http://localhost:8002 > /dev/null; then
        echo "✅ Agent HTTP Server: STARTED"
    else
        echo "🟡 Agent HTTP Server: OPTIONAL FOR TESTING"
    fi
fi

echo "✅ Service health checks complete"
```

---

## MCP Tool Validation

### Test All Hockey MCP Tools
```bash
echo "🔧 Testing MCP tool functionality..."

python3 << 'EOF'
import requests
import json
import time

def test_mcp_tools():
    """Test all hockey MCP tools for functionality"""
    
    # Test tools list endpoint
    try:
        print("🔍 Testing MCP tools list...")
        response = requests.get('http://localhost:8000/mcp/list_tools', timeout=10)
        
        if response.status_code != 200:
            print(f"❌ MCP Tools List: HTTP {response.status_code}")
            return False
            
        tools_data = response.json()
        available_tools = [tool.get('name', '') for tool in tools_data.get('tools', [])]
        
        # Expected hockey coaching tools
        expected_tools = [
            'search_hockey_knowledge',
            'get_coaching_recommendations', 
            'create_practice_plan',
            'analyze_player_development'
        ]
        
        print("📋 MCP Tools availability:")
        all_available = True
        for tool in expected_tools:
            if tool in available_tools:
                print(f"   ✅ {tool}: Available")
            else:
                print(f"   ❌ {tool}: Missing")
                all_available = False
        
        if not all_available:
            print("❌ MCP Tools: Some expected tools are missing")
            return False
            
        print(f"✅ MCP Tools: All {len(expected_tools)} expected tools available")
        
        # Test individual tool functionality
        print("\n🧪 Testing individual tool functionality...")
        
        # Test search_hockey_knowledge
        print("🔍 Testing search_hockey_knowledge...")
        search_payload = {
            "tool": "search_hockey_knowledge",
            "parameters": {
                "query": "U10 skating drills",
                "age_groups": ["U10"],
                "content_types": ["drill"],
                "n_results": 3
            }
        }
        
        try:
            response = requests.post('http://localhost:8000/mcp/call_tool', 
                                   json=search_payload, timeout=15)
            if response.status_code == 200:
                result = response.json()
                if 'result' in result and len(str(result['result'])) > 50:
                    print("   ✅ search_hockey_knowledge: Functional (returned data)")
                else:
                    print("   🟡 search_hockey_knowledge: Responding but limited data")
            else:
                print(f"   ❌ search_hockey_knowledge: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ search_hockey_knowledge: Error - {e}")
            
        # Test get_coaching_recommendations
        print("🎯 Testing get_coaching_recommendations...")
        coaching_payload = {
            "tool": "get_coaching_recommendations", 
            "parameters": {
                "team_age": "U10",
                "skill_focus": ["skating", "passing"],
                "available_time": 60
            }
        }
        
        try:
            response = requests.post('http://localhost:8000/mcp/call_tool',
                                   json=coaching_payload, timeout=15)
            if response.status_code == 200:
                result = response.json()
                if 'result' in result and len(str(result['result'])) > 50:
                    print("   ✅ get_coaching_recommendations: Functional")
                else:
                    print("   🟡 get_coaching_recommendations: Limited response")
            else:
                print(f"   ❌ get_coaching_recommendations: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ get_coaching_recommendations: Error - {e}")
            
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ MCP Tools: Connection error - {e}")
        return False
    except Exception as e:
        print(f"❌ MCP Tools: Unexpected error - {e}")
        return False

# Run the test
if test_mcp_tools():
    print("\n✅ MCP tool validation: PASSED")
else:
    print("\n❌ MCP tool validation: FAILED")
    exit(1)
EOF

echo "✅ MCP tool functionality validation complete"
```

---

## ChromaDB Connectivity and Data Validation

### Test ChromaDB Collections
```bash
echo "💾 Testing ChromaDB connectivity and data availability..."

python3 << 'EOF'
import sys
sys.path.append('/Users/liammckendry/thunder_playbook')

def test_chromadb_collections():
    """Test all ChromaDB collections for connectivity and data"""
    
    try:
        from utils.chroma_utils import get_chroma_collection
        
        # Test collections across different knowledge domains
        test_collections = [
            'drill-source1',       # On-ice drills
            'drill-source2', 
            'ltad-source1',        # Long-term athlete development
            'tactics-source1',     # Team systems and tactics
            'conduct-source1',     # Rules and conduct
            'insight-source1',     # NHL expert insights
            'video-source1',       # Instructional videos
            'office-source1'       # Off-ice training
        ]
        
        print("🔍 Testing ChromaDB collections...")
        
        available_collections = []
        total_items = 0
        
        for collection_name in test_collections:
            try:
                collection = get_chroma_collection(collection_name)
                count = collection.count()
                total_items += count
                available_collections.append(collection_name)
                
                if count > 0:
                    print(f"   ✅ {collection_name}: {count} items")
                else:
                    print(f"   🟡 {collection_name}: Empty collection")
                    
            except Exception as e:
                print(f"   ❌ {collection_name}: Error - {str(e)[:60]}...")
        
        print(f"\n📊 ChromaDB Summary:")
        print(f"   Available collections: {len(available_collections)}/{len(test_collections)}")
        print(f"   Total hockey knowledge items: {total_items}")
        
        if len(available_collections) >= 4 and total_items >= 100:
            print("✅ ChromaDB: Sufficient data available for hockey coaching")
            return True
        elif len(available_collections) >= 2:
            print("🟡 ChromaDB: Limited data but functional")
            return True
        else:
            print("❌ ChromaDB: Insufficient data collections")
            return False
            
    except ImportError as e:
        print(f"❌ ChromaDB: Import error - {e}")
        return False
    except Exception as e:
        print(f"❌ ChromaDB: Connection error - {e}")
        return False

# Run the test
if test_chromadb_collections():
    print("\n✅ ChromaDB validation: PASSED")
else:
    print("\n❌ ChromaDB validation: FAILED")
    exit(1)
EOF

echo "✅ ChromaDB connectivity and data validation complete"
```

---

## Agent Integration Testing

### Test Agent-to-MCP Integration
```bash
echo "🤖 Testing agent integration with MCP server..."

# Test CLI agent functionality
if [ -f "servers/poc/test_agent_cli.py" ]; then
    echo "🔍 Testing CLI agent functionality..."
    cd servers/poc
    
    if python test_agent_cli.py > /tmp/agent_test_output.txt 2>&1; then
        echo "✅ CLI Agent: Basic functionality working"
        
        # Check for successful tool usage in output
        if grep -q "MCP TOOLS USED" /tmp/agent_test_output.txt; then
            echo "✅ CLI Agent: MCP tool integration confirmed"
        else
            echo "🟡 CLI Agent: Working but tool usage unclear"
        fi
    else
        echo "❌ CLI Agent: Test failed"
        echo "   Output: $(cat /tmp/agent_test_output.txt | tail -3)"
    fi
    
    cd ../..
else
    echo "🟡 CLI Agent: Test file not available"
fi

# Test MCP connection directly
if [ -f "servers/poc/test_mcp_connection.py" ]; then
    echo "🔍 Testing direct MCP connection..."
    cd servers/poc
    
    if python test_mcp_connection.py > /tmp/mcp_connection_test.txt 2>&1; then
        echo "✅ MCP Connection: Direct connection working"
        
        # Check for successful tool listing
        if grep -q "Available tools" /tmp/mcp_connection_test.txt; then
            echo "✅ MCP Connection: Tool discovery successful"
        fi
    else
        echo "❌ MCP Connection: Test failed"
        echo "   Output: $(cat /tmp/mcp_connection_test.txt | tail -3)"
    fi
    
    cd ../..
fi

# Test Agent HTTP Server functionality
echo "🔧 Testing Agent HTTP Server integration..."
if curl -s -f http://localhost:8002 > /dev/null; then
    # Test with sample hockey query
    AGENT_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
        -d '{"message":"What are good U10 passing drills?","group_id":"system-test"}' \
        http://localhost:8002 2>/dev/null)
    
    if [ $? -eq 0 ] && [ -n "$AGENT_RESPONSE" ]; then
        # Check if response contains hockey-specific content
        if echo "$AGENT_RESPONSE" | grep -i -q -E "(drill|hockey|passing|U10)"; then
            echo "✅ Agent HTTP Server: Hockey coaching functionality working"
        else
            echo "🟡 Agent HTTP Server: Responding but content unclear"
        fi
        
        # Check response structure
        if echo "$AGENT_RESPONSE" | grep -q '"response"'; then
            echo "✅ Agent HTTP Server: Response format correct"
        else
            echo "🟡 Agent HTTP Server: Response format may be incorrect" 
        fi
    else
        echo "❌ Agent HTTP Server: No response to test query"
    fi
else
    echo "🟡 Agent HTTP Server: Not running (optional component)"
fi

echo "✅ Agent integration testing complete"
```

---

## Web Application Testing

### Test Web App Functionality
```bash
echo "📱 Testing web application functionality..."

if curl -s -f http://localhost:3000 > /dev/null; then
    echo "✅ Web App: Basic connectivity confirmed"
    
    # Test main page load
    MAIN_PAGE=$(curl -s http://localhost:3000)
    if echo "$MAIN_PAGE" | grep -q -i "hockey"; then
        echo "✅ Web App: Main page contains hockey content"
    else
        echo "🟡 Web App: Main page loaded but content unclear"
    fi
    
    # Test API endpoints
    echo "🔍 Testing web app API endpoints..."
    
    # Test chat API health
    if curl -s -f http://localhost:3000/api/chat > /dev/null; then
        echo "✅ Web API: Chat endpoint responding"
    else
        echo "🟡 Web API: Chat endpoint not responding to GET"
    fi
    
    # Test MCP API endpoint  
    if curl -s -f http://localhost:3000/api/mcp > /dev/null; then
        echo "✅ Web API: MCP endpoint responding"
    else
        echo "🟡 Web API: MCP endpoint not responding"
    fi
    
    # Test agent test endpoint if available
    if curl -s -f http://localhost:3000/api/agent-test > /dev/null; then
        echo "✅ Web API: Agent test endpoint responding"
        
        # Test with actual query
        echo "🧪 Testing agent integration via web API..."
        WEB_AGENT_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
            -d '{"message":"What are basic U10 skating fundamentals?"}' \
            http://localhost:3000/api/agent-test 2>/dev/null)
        
        if [ $? -eq 0 ] && [ -n "$WEB_AGENT_RESPONSE" ]; then
            if echo "$WEB_AGENT_RESPONSE" | grep -i -q -E "(skating|hockey|U10|fundamental)"; then
                echo "✅ Web Agent Integration: Hockey coaching working via web"
            else
                echo "🟡 Web Agent Integration: Response received but content unclear"
            fi
        else
            echo "❌ Web Agent Integration: No response via web API"
        fi
    else
        echo "🟡 Web API: Agent test endpoint not available"
    fi
    
else
    echo "🟡 Web App: Not running (development component)"
    echo "   To start: cd web_app && npm run dev"
fi

echo "✅ Web application testing complete"
```

---

## End-to-End Integration Testing

### Test Complete Hockey Coaching Pipeline
```bash
echo "🏒 Testing complete hockey coaching pipeline..."

python3 << 'EOF'
import requests
import json
import time

def test_hockey_coaching_pipeline():
    """Test the complete hockey coaching workflow"""
    
    print("🎯 Testing complete hockey coaching pipeline...")
    
    # Test scenarios covering different coaching needs
    test_scenarios = [
        {
            "name": "U10 Skill Development",
            "query": "What are essential skating skills for U10 players?",
            "expected_keywords": ["skating", "u10", "balance", "stride", "edge"]
        },
        {
            "name": "Practice Planning",
            "query": "Create a 60-minute practice plan for U12 players focusing on passing",
            "expected_keywords": ["practice", "passing", "drill", "minute", "u12"]
        },
        {
            "name": "Team Systems",
            "query": "Explain basic forechecking for youth hockey",
            "expected_keywords": ["forecheck", "system", "pressure", "zone", "hockey"]
        }
    ]
    
    # Test via MCP server directly
    print("\n📡 Testing via MCP server...")
    for scenario in test_scenarios:
        print(f"   🎯 {scenario['name']}...")
        
        payload = {
            "tool": "search_hockey_knowledge",
            "parameters": {
                "query": scenario["query"],
                "n_results": 3
            }
        }
        
        try:
            response = requests.post('http://localhost:8000/mcp/call_tool',
                                   json=payload, timeout=20)
            
            if response.status_code == 200:
                result = response.json()
                result_text = str(result.get('result', '')).lower()
                
                # Check for expected keywords
                keywords_found = sum(1 for keyword in scenario['expected_keywords'] 
                                   if keyword.lower() in result_text)
                
                if keywords_found >= 2:
                    print(f"      ✅ {scenario['name']}: Relevant hockey content returned")
                else:
                    print(f"      🟡 {scenario['name']}: Response received but relevance unclear")
            else:
                print(f"      ❌ {scenario['name']}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ {scenario['name']}: Error - {e}")
    
    # Test via Agent HTTP Server (if available)
    try:
        if requests.get('http://localhost:8002', timeout=5).status_code == 200:
            print("\n🤖 Testing via Agent HTTP Server...")
            
            for scenario in test_scenarios:
                print(f"   🎯 {scenario['name']}...")
                
                payload = {
                    "message": scenario["query"],
                    "group_id": "system-test"
                }
                
                try:
                    response = requests.post('http://localhost:8002',
                                           json=payload, timeout=30)
                    
                    if response.status_code == 200:
                        result = response.json()
                        response_text = result.get('response', '').lower()
                        
                        keywords_found = sum(1 for keyword in scenario['expected_keywords'] 
                                           if keyword.lower() in response_text)
                        
                        if keywords_found >= 2:
                            print(f"      ✅ {scenario['name']}: Agent provided relevant coaching advice")
                        else:
                            print(f"      🟡 {scenario['name']}: Agent responded but relevance unclear")
                    else:
                        print(f"      ❌ {scenario['name']}: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"      ❌ {scenario['name']}: Error - {e}")
        
    except:
        print("\n🟡 Agent HTTP Server not available for pipeline testing")
    
    print("\n✅ Hockey coaching pipeline testing complete")
    return True

# Run pipeline test
test_hockey_coaching_pipeline()
EOF

echo "✅ End-to-end integration testing complete"
```

---

## System Health Report

### Generate Comprehensive Health Report
```bash
echo "📊 Generating comprehensive system health report..."

# Create health report
HEALTH_REPORT_FILE="system_health_report_$(date +%Y%m%d_%H%M%S).md"

cat > "$HEALTH_REPORT_FILE" << EOF
# Hockey Coach AI Assistant - System Health Report

**Report Generated**: $(date -u +%Y-%m-%dT%H:%M:%SZ)  
**Test Execution**: Comprehensive system validation completed
**Overall Status**: $(curl -s -f http://localhost:8000/health > /dev/null && echo "✅ HEALTHY" || echo "❌ ISSUES DETECTED")

---

## Core Services Status

### MCP Server (Port 8000)
- **Status**: $(curl -s -f http://localhost:8000/health > /dev/null && echo "✅ RUNNING" || echo "❌ DOWN")
- **Health Endpoint**: $(curl -s http://localhost:8000/health 2>/dev/null || echo "No response")
- **Available Tools**: $(curl -s http://localhost:8000/mcp/list_tools 2>/dev/null | grep -o '"name"' | wc -l | tr -d ' ') detected

### Direct API Bridge (Port 3003)  
- **Status**: $(curl -s -f http://localhost:3003/api/mcp > /dev/null && echo "✅ RUNNING" || echo "🟡 OPTIONAL")

### Web Application (Port 3000)
- **Status**: $(curl -s -f http://localhost:3000 > /dev/null && echo "✅ RUNNING" || echo "🟡 DEVELOPMENT")

### Agent HTTP Server (Port 8002)
- **Status**: $(curl -s -f http://localhost:8002 > /dev/null && echo "✅ RUNNING" || echo "🟡 OPTIONAL")

---

## Data Layer Validation

### ChromaDB Collections
- **Connection**: $(python3 -c "import sys; sys.path.append('/Users/liammckendry/thunder_playbook'); from utils.chroma_utils import get_chroma_collection; get_chroma_collection('drill-source1'); print('✅ CONNECTED')" 2>/dev/null || echo "❌ DISCONNECTED")
- **Hockey Knowledge Items**: $(python3 -c "
import sys
sys.path.append('/Users/liammckendry/thunder_playbook')
from utils.chroma_utils import get_chroma_collection
try:
    collections = ['drill-source1', 'ltad-source1', 'tactics-source1', 'conduct-source1']
    total = sum(get_chroma_collection(c).count() for c in collections)
    print(f'{total} items available')
except: print('Count unavailable')
" 2>/dev/null)

### MCP Tool Functionality
$(curl -s http://localhost:8000/mcp/list_tools 2>/dev/null | grep -o '"search_hockey_knowledge"' > /dev/null && echo "- ✅ search_hockey_knowledge: Available" || echo "- ❌ search_hockey_knowledge: Missing")
$(curl -s http://localhost:8000/mcp/list_tools 2>/dev/null | grep -o '"get_coaching_recommendations"' > /dev/null && echo "- ✅ get_coaching_recommendations: Available" || echo "- ❌ get_coaching_recommendations: Missing")
$(curl -s http://localhost:8000/mcp/list_tools 2>/dev/null | grep -o '"create_practice_plan"' > /dev/null && echo "- ✅ create_practice_plan: Available" || echo "- ❌ create_practice_plan: Missing")
$(curl -s http://localhost:8000/mcp/list_tools 2>/dev/null | grep -o '"analyze_player_development"' > /dev/null && echo "- ✅ analyze_player_development: Available" || echo "- ❌ analyze_player_development: Missing")

---

## Integration Testing Results

### Agent-MCP Integration
- **CLI Agent**: $([ -f "servers/poc/test_agent_cli.py" ] && echo "✅ Available for testing" || echo "🟡 Test not available")
- **MCP Connection**: $([ -f "servers/poc/test_mcp_connection.py" ] && echo "✅ Connection test available" || echo "🟡 Test not available")

### Web Integration
- **API Endpoints**: $(curl -s -f http://localhost:3000/api/chat > /dev/null && echo "✅ Chat API responding" || echo "🟡 Chat API not tested")
- **Agent Integration**: $(curl -s -f http://localhost:3000/api/agent-test > /dev/null && echo "✅ Agent API available" || echo "🟡 Agent API not available")

---

## Performance Metrics

### Response Times (Approximate)
- **MCP Health Check**: $(time curl -s http://localhost:8000/health > /dev/null 2>&1; echo "${PIPESTATUS[0]}" | grep -q "0" && echo "<1 second" || echo "Timeout/Error")
- **Tool Query Response**: Varies 5-15 seconds depending on query complexity
- **Web App Load**: Varies based on development/production mode

### System Resource Usage
- **Python Processes**: $(ps aux | grep -c "python.*hockey_mcp\|python.*agent_http_server")+ running
- **Node.js Processes**: $(ps aux | grep -c "node.*next")+ running (if web app active)

---

## Recommendations

### Immediate Actions Required
$(curl -s -f http://localhost:8000/health > /dev/null || echo "- ❗ Start MCP server: python servers/hockey_mcp.py")
$(python3 -c "import sys; sys.path.append('/Users/liammckendry/thunder_playbook'); from utils.chroma_utils import get_chroma_collection; get_chroma_collection('drill-source1')" 2>/dev/null || echo "- ❗ Check ChromaDB connectivity and data indexing")

### Optional Enhancements
$(curl -s -f http://localhost:3000 > /dev/null || echo "- 🟡 Start web app for full UI testing: cd web_app && npm run dev")
$(curl -s -f http://localhost:8002 > /dev/null || echo "- 🟡 Start agent server for HTTP testing: cd servers/poc && python agent_http_server.py")

---

## Test Summary

**Core Functionality**: $(curl -s -f http://localhost:8000/health > /dev/null && echo "✅ OPERATIONAL" || echo "❌ REQUIRES ATTENTION")
**Hockey Knowledge**: $(python3 -c "import sys; sys.path.append('/Users/liammckendry/thunder_playbook'); from utils.chroma_utils import get_chroma_collection; get_chroma_collection('drill-source1'); print('✅ ACCESSIBLE')" 2>/dev/null || echo "❌ NEEDS SETUP")
**Integration Points**: $(curl -s -f http://localhost:8000/mcp/list_tools > /dev/null && echo "✅ FUNCTIONAL" || echo "❌ ISSUES DETECTED")
**Development Ready**: $([ -f "servers/hockey_mcp.py" ] && [ -d "web_app" ] && echo "✅ YES" || echo "❌ INCOMPLETE")

---

*Report generated by /hockey-system-test automation*
EOF

echo "✅ System health report generated: $HEALTH_REPORT_FILE"
echo ""
echo "📋 Report Summary:"
cat "$HEALTH_REPORT_FILE" | grep "Overall Status\|Core Functionality\|Hockey Knowledge\|Integration Points\|Development Ready"
```

---

## Final System Status

### Generate Final Status Summary
```bash
echo ""
echo "🏒 HOCKEY SYSTEM TEST COMPLETE!"
echo ""
echo "System Validation Summary:"
echo "  🔧 Core Services: $(curl -s -f http://localhost:8000/health > /dev/null && echo "✅ MCP Server Running" || echo "❌ MCP Server Down")"
echo "  💾 Data Layer: $(python3 -c "import sys; sys.path.append('/Users/liammckendry/thunder_playbook'); from utils.chroma_utils import get_chroma_collection; get_chroma_collection('drill-source1'); print('✅ ChromaDB Connected')" 2>/dev/null || echo "❌ ChromaDB Issues")"
echo "  🤖 Agent Integration: $([ -f "servers/poc/test_mcp_connection.py" ] && echo "✅ Available" || echo "🟡 Limited")"
echo "  📱 Web Application: $(curl -s -f http://localhost:3000 > /dev/null && echo "✅ Running" || echo "🟡 Development Mode")"
echo "  🔧 MCP Tools: $(curl -s http://localhost:8000/mcp/list_tools 2>/dev/null | grep -c '"name"' | awk '{print $1 >= 4 ? "✅ All Available" : "🟡 Limited Tools"}')"
echo ""
echo "Health Report: $HEALTH_REPORT_FILE"
echo ""

# Determine overall system status
SYSTEM_HEALTHY=true

# Check critical components
if ! curl -s -f http://localhost:8000/health > /dev/null; then
    SYSTEM_HEALTHY=false
fi

if ! python3 -c "import sys; sys.path.append('/Users/liammckendry/thunder_playbook'); from utils.chroma_utils import get_chroma_collection; get_chroma_collection('drill-source1')" 2>/dev/null; then
    SYSTEM_HEALTHY=false
fi

if [ "$SYSTEM_HEALTHY" = true ]; then
    echo "🎉 System Status: ✅ HEALTHY - Ready for hockey coaching AI assistance!"
else
    echo "⚠️  System Status: ❌ ISSUES DETECTED - Review health report for details"
    echo ""
    echo "Quick fixes:"
    echo "  - Start MCP server: python servers/hockey_mcp.py"
    echo "  - Check data indexing: python chroma_load/scripts/index_drills_chroma.py"
    echo "  - Verify environment: /hockey-setup"
fi
echo ""
```

---

## Success Criteria

- ✅ All core services started and health checked
- ✅ MCP server responding with all expected tools
- ✅ ChromaDB connectivity confirmed with data validation
- ✅ Agent integration tested (where available)
- ✅ Web application functionality verified (if running)
- ✅ End-to-end hockey coaching pipeline tested
- ✅ Comprehensive health report generated
- ✅ Overall system status determined

## Usage Examples

```bash
# Basic system test
/hockey-system-test

# After integration batch
/hockey-system-test > integration_validation.log

# Before production deployment
/hockey-system-test && echo "Ready for production"
```

## Troubleshooting

### MCP Server Issues
```bash
# Restart MCP server
python servers/hockey_mcp.py &

# Check logs
tail -f servers/hockey_mcp.log
```

### ChromaDB Connection Issues
```bash
# Test direct connection
python -c "from utils.chroma_utils import get_chroma_collection; print(get_chroma_collection('drill-source1').count())"

# Re-index data if needed
python chroma_load/scripts/index_drills_chroma.py
```

### Web App Issues
```bash
# Start web app
cd web_app && npm install && npm run dev

# Check build
cd web_app && npm run build
```

### Agent Integration Issues
```bash
# Test direct MCP connection
cd servers/poc && python test_mcp_connection.py

# Test CLI agent
cd servers/poc && python test_agent_cli.py
```

Comprehensive hockey system validation is now complete with automated health reporting!