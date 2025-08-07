# Reconnect Command

Restart all servers for hockey applications in both worktree and main environments.

## Quick Reconnect (Current Worktree)

1. **Kill existing processes**
```bash
# Kill all hockey-related processes
pkill -f "hockey_diagram_direct_api"
pkill -f "hockey_diagram_mcp/server.py"
pkill -f "next dev"
pkill -f "hockey_mcp.py"
pkill -f "hockey_mcp_direct_api.py"
```

2. **Restart Hockey Diagram Services (Issue-97 Worktree)**
```bash
# Start MCP server
cd /Users/liammckendry/thunder_playbook_worktrees/issue-97/servers/hockey_diagram_mcp
nohup /Users/liammckendry/spacy_env/bin/python server.py > server.log 2>&1 &

# Start Agent API server
nohup /Users/liammckendry/spacy_env/bin/python hockey_diagram_direct_api.py > api_server.log 2>&1 &

# Start Web App
cd /Users/liammckendry/thunder_playbook_worktrees/issue-97/web_app
nohup npm run dev > web_server.log 2>&1 &
```

3. **Verify Services**
```bash
sleep 3
curl -s http://localhost:8001/health | jq '.' || echo "Agent server not responding"
curl -s http://localhost:3000/hockey-diagram-test -o /dev/null -w "%{http_code}\n" || echo "Web app not responding"
```

## Full Environment Reconnect (Main + Worktree)

1. **Kill ALL hockey processes**
```bash
pkill -f "hockey"
pkill -f "next dev"
```

2. **Start Main Thunder Playbook Services**
```bash
cd /Users/liammckendry/thunder_playbook
source ../spacy_env/bin/activate

# Start core MCP services
nohup python servers/hockey_mcp.py > logs/hockey_mcp.log 2>&1 &
nohup python servers/hockey_mcp_direct_api.py > logs/hockey_api.log 2>&1 &

# Start main web app (HockeyIQ)
cd web_app
nohup npm run dev > ../logs/web_app.log 2>&1 &
cd ..
```

3. **Start Worktree Services**
Follow steps 2-3 from Quick Reconnect above.

4. **Verify All Services**
```bash
echo "=== Service Status ==="
echo "Main MCP: $(curl -s http://localhost:8000/health | jq -r '.status' || echo 'DOWN')"
echo "Main API: $(curl -s http://localhost:3003/api/mcp | jq -r '.status' || echo 'DOWN')"
echo "Main Web: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 || echo 'DOWN')"
echo "Diagram Agent: $(curl -s http://localhost:8001/health | jq -r '.status' || echo 'DOWN')"
echo "Diagram Web: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/hockey-diagram-test || echo 'DOWN')"
```

## Service Ports Reference
- **Main Thunder Playbook:**
  - MCP Server: 8000
  - Direct API: 3003
  - Web App: 3000 (HockeyIQ)
  
- **Hockey Diagram Worktree:**
  - MCP Server: stdio (no port)
  - Agent API: 8001
  - Web App: 3000 (shared with main)

## Troubleshooting

If services fail to start:
1. Check if ports are already in use: `lsof -i :8000,8001,3000,3003`
2. Check Python environment: `which python` (should show spacy_env)
3. Check logs in respective directories
4. Ensure npm dependencies are installed: `cd web_app && npm install`

## Quick Status Check
```bash
ps aux | grep -E "hockey|next" | grep -v grep
```