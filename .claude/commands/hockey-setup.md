# Hockey Setup Command

Set up complete development environment for Hockey Coach AI Assistant.

## Environment Setup

1. **Activate Python Environment**
```bash
cd /Users/liammckendry/thunder_playbook
source ../spacy_env/bin/activate
```

2. **Verify Environment Variables**
Check that these are set:
- OPENAI_API_KEY
- CHROMA_HOST=localhost  
- CHROMA_PORT=8000

3. **Start Core Services**
```bash
# Option A: All services
python start_services.py

# Option B: Manual startup
python servers/hockey_mcp.py &           # MCP server (port 8000)
python servers/hockey_mcp_direct_api.py &  # API wrapper (port 3003)
cd web_app && npm run dev                # Next.js app (port 3000)
```

4. **Start POC Components**
```bash
cd servers/poc
/Users/liammckendry/spacy_env/bin/python agent_http_server.py &  # Port 8002
```

5. **Verify All Services**
```bash
curl http://localhost:8000/health      # MCP Server
curl http://localhost:8002             # Agent HTTP Server
curl http://localhost:3000             # Web App
curl http://localhost:3003/api/mcp     # Direct API
```

## Quick Test
```bash
# Test complete integration
curl -X POST -H "Content-Type: application/json" \
  -d '{"message":"What are good U10 skating drills?"}' \
  http://localhost:3000/api/agent-test
```

Environment is ready when all services respond successfully.