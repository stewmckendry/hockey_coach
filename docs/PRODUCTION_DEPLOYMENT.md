# Production Deployment Guide

This guide explains how to deploy the Hockey Coach Playbook from development (in-memory FastMCP) to production (HTTP transport) environments.

## Architecture Changes: Development vs Production

### Development Architecture
```
Next.js App → Bridge API → In-Memory FastMCP Client → hockey_mcp.py (same process) → ChromaDB Cloud
```

### Production Architecture  
```
Next.js App → Bridge API → HTTP FastMCP Client → Remote MCP Server → ChromaDB Cloud
    │              │              │                      │              │
Container 1    Container 2    Container 3          Container 4      External Service
```

**Note**: ChromaDB is deployed as a cloud service (e.g., Railway) and shared between development and production environments.

## Key Differences

| Aspect | Development | Production |
|--------|-------------|------------|
| **FastMCP Transport** | In-memory (`Client(mcp)`) | HTTP (`Client("http://server:8000/mcp")`) |
| **Process Model** | Single process, direct import | Microservices, network communication |
| **ChromaDB** | Cloud service (shared) | Cloud service (shared) |
| **Scalability** | Limited to single machine | Independent scaling per service |
| **Fault Isolation** | Shared failure domain | Isolated failure domains |
| **Resource Usage** | Shared memory/CPU | Dedicated resources per service |

## Files Modified for Production

### 1. MCP Server (`servers/hockey_mcp.py`)
**Changes**: Added environment-based transport selection

```python
# Before (development only)
if __name__ == "__main__":
    mcp.run()  # Always STDIO

# After (environment-aware)
transport = os.getenv('MCP_TRANSPORT', 'sse')
if transport == 'http':
    mcp.run(transport="http", host=host, port=port, path="/mcp")
elif transport == 'stdio':
    mcp.run(transport="stdio")
else:
    uvicorn.run(mcp.sse_app, host=host, port=port)
```

### 2. Bridge API (`servers/hockey_mcp_production_api.py`)
**New file**: Environment-aware client factory

```python
def get_mcp_client():
    if ENVIRONMENT == 'production':
        # Remote HTTP client
        return Client(os.getenv('MCP_SERVER_URL'))
    else:
        # In-memory client (development)
        from hockey_mcp import mcp
        return Client(mcp)
```

## Deployment Methods

### Method 1: Docker Compose (Recommended)

1. **Create production environment file**:
```bash
cp .env.production.example .env.production
# Edit .env.production with your values
```

2. **Deploy**:
```bash
./scripts/deploy-production.sh
```

3. **Verify deployment**:
```bash
# Check all services are running
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Method 2: Manual Deployment

1. **Start ChromaDB**:
```bash
docker run -d --name chromadb -p 8001:8000 \
  -v chroma_data:/chroma/chroma \
  chromadb/chroma:latest
```

2. **Start MCP Server**:
```bash
cd servers
export MCP_TRANSPORT=http
export MCP_PORT=8000
export ENVIRONMENT=production
python hockey_mcp.py
```

3. **Start Bridge API**:
```bash
cd servers  
export ENVIRONMENT=production
export MCP_SERVER_URL=http://localhost:8000/mcp
python hockey_mcp_production_api.py
```

4. **Start Web App**:
```bash
cd web_app
export NODE_ENV=production
export HOCKEY_MCP_DIRECT_URL=http://localhost:3003
npm run build && npm start
```

## Environment Variables

### Required for Production

| Variable | Description | Example |
|----------|-------------|---------|
| `ENVIRONMENT` | Deployment environment | `production` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `MCP_SERVER_URL` | Remote MCP server URL | `http://hockey-mcp:8000/mcp` |
| `WEB_APP_URL` | Production web app URL | `https://hockey-coach.com` |
| `CHROMA_SERVER_HOST` | ChromaDB cloud host | `https://your-chroma.railway.app` |
| `CHROMA_SERVER_HTTP_PORT` | ChromaDB cloud port | `443` |
| `CHROMA_TOKEN` | ChromaDB authentication token | `your-token` |

### Optional Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_TRANSPORT` | `sse` | MCP transport type (`http`, `sse`, `stdio`) |
| `MCP_PORT` | `8000` | MCP server port |
| `BRIDGE_PORT` | `3003` | Bridge API port |
| `LOG_LEVEL` | `INFO` | Logging level |

## Health Checks

All services provide health check endpoints:

- **MCP Server**: `GET http://localhost:8000/health`
- **Bridge API**: `GET http://localhost:3003/health`  
- **Web App**: `GET http://localhost:3000` (Next.js built-in)
- **ChromaDB**: `GET http://localhost:8001/api/v1/heartbeat`

## Monitoring

### Docker Compose Monitoring
```bash
# View service status
docker-compose -f docker-compose.prod.yml ps

# View logs from all services
docker-compose -f docker-compose.prod.yml logs -f

# View logs from specific service
docker-compose -f docker-compose.prod.yml logs -f hockey-mcp

# Resource usage
docker stats
```

### Application Logs
Each service logs important events:

- **Connection status** (in-memory vs HTTP)
- **Tool execution results**
- **Health check status**
- **Error conditions**

## Scaling Considerations

### Horizontal Scaling
```yaml
# docker-compose.prod.yml - Scale specific services
services:
  hockey-bridge:
    deploy:
      replicas: 3  # Scale bridge API
  
  hockey-mcp:
    deploy:
      replicas: 2  # Scale MCP server
```

### Load Balancing
Add nginx or similar load balancer:

```nginx
upstream hockey_bridge {
    server hockey-bridge-1:3003;
    server hockey-bridge-2:3003;
    server hockey-bridge-3:3003;
}

upstream hockey_mcp {
    server hockey-mcp-1:8000;
    server hockey-mcp-2:8000;
}
```

## Troubleshooting

### Common Issues

1. **MCP Connection Failed**
   - Check `MCP_SERVER_URL` is correct
   - Verify MCP server is running and reachable
   - Check network connectivity between containers

2. **ChromaDB Connection Failed**
   - Ensure ChromaDB is running before MCP server
   - Check `CHROMA_HOST` and `CHROMA_PORT` settings
   - Verify ChromaDB data persistence

3. **CORS Errors**
   - Update `allowed_origins` in bridge API
   - Set correct `WEB_APP_URL` environment variable

### Debug Commands

```bash
# Test MCP server directly
curl http://localhost:8000/health

# Test bridge API
curl http://localhost:3003/health

# Test tool execution
curl -X POST http://localhost:3003/api/mcp \
  -H "Content-Type: application/json" \
  -d '{"tool": "search_hockey_knowledge", "parameters": {"query": "test"}}'

# Check container logs
docker logs hockey-mcp
docker logs hockey-bridge
```

## Security Considerations

### Production Security
- Use environment variables for secrets
- Implement proper CORS policies
- Use HTTPS in production
- Regular security updates for base images
- Network segmentation between services

### API Key Management
- Never commit API keys to version control
- Use secrets management (Docker secrets, K8s secrets)
- Rotate keys regularly
- Monitor API usage

## Rollback Procedure

To rollback to previous version:

```bash
# Stop current deployment
docker-compose -f docker-compose.prod.yml down

# Restore previous images
docker tag hockey-mcp:previous hockey-mcp:latest
docker tag hockey-bridge:previous hockey-bridge:latest

# Restart with previous version
docker-compose -f docker-compose.prod.yml up -d
```

## Next Steps

1. **CI/CD Pipeline**: Automate deployment with GitHub Actions
2. **Monitoring**: Add Prometheus/Grafana for metrics
3. **Logging**: Centralized logging with ELK stack
4. **Secrets Management**: Use proper secrets management
5. **Load Balancing**: Add load balancer for high availability
