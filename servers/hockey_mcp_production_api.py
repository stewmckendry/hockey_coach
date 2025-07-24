#!/usr/bin/env python3
"""
Production-Ready FastMCP Integration
Supports both development (in-memory) and production (HTTP/SSE) transports
"""

import sys
import os
import asyncio
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Add the project root to path
sys.path.append(str(Path(__file__).resolve().parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Hockey MCP Production API", version="2.0.0")

# Environment-based CORS configuration
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
if ENVIRONMENT == 'production':
    allowed_origins = [
        os.getenv('WEB_APP_URL', 'https://your-app.com'),
        os.getenv('ADMIN_URL', 'https://admin.your-app.com')
    ]
else:
    allowed_origins = [
        "http://localhost:3000", 
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ToolRequest(BaseModel):
    tool: str
    parameters: Optional[Dict[str, Any]] = {}

def get_mcp_client():
    """
    Factory function to create appropriate MCP client based on environment
    """
    from fastmcp import Client
    
    if ENVIRONMENT == 'production':
        # Production: Connect to remote MCP server via HTTP/SSE
        mcp_server_url = os.getenv('MCP_SERVER_URL')
        if not mcp_server_url:
            raise ValueError("MCP_SERVER_URL environment variable required in production")
        
        print(f"🌐 Connecting to remote MCP server: {mcp_server_url}")
        return Client(mcp_server_url)
    else:
        # Development: Use in-memory transport
        print("🔧 Using in-memory MCP client for development")
        from hockey_mcp import mcp
        return Client(mcp)

@app.post("/api/mcp")
async def call_mcp_tool(request: ToolRequest):
    """Call a tool on the MCP server (environment-aware)"""
    try:
        client = get_mcp_client()
        
        async with client:
            result = await client.call_tool(request.tool, request.parameters)
            
            return {
                "success": True,
                "data": result,
                "environment": ENVIRONMENT,
                "timestamp": "2025-07-23T20:30:00Z"
            }
            
    except Exception as e:
        print(f"Error calling tool '{request.tool}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mcp")
async def health_check():
    """Health check with environment awareness"""
    try:
        client = get_mcp_client()
        
        async with client:
            await client.ping()
            tools = await client.list_tools()
            
            return {
                "status": "healthy",
                "environment": ENVIRONMENT,
                "mcpServer": {
                    "type": "remote" if ENVIRONMENT == 'production' else "in-memory",
                    "protocol": "FastMCP",
                    "connected": True,
                    "tools_available": len(tools.tools) if hasattr(tools, 'tools') else 0,
                    "server_url": os.getenv('MCP_SERVER_URL') if ENVIRONMENT == 'production' else "in-memory"
                },
                "timestamp": "2025-07-23T20:30:00Z"
            }
            
    except Exception as e:
        return {
            "status": "unhealthy",
            "environment": ENVIRONMENT,
            "error": str(e),
            "timestamp": "2025-07-23T20:30:00Z"
        }

@app.get("/tools")
async def list_tools():
    """List available tools"""
    try:
        client = get_mcp_client()
        
        async with client:
            tools = await client.list_tools()
            return {
                "environment": ENVIRONMENT,
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description
                    }
                    for tool in (tools.tools if hasattr(tools, 'tools') else [])
                ]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def simple_health():
    """Simple health endpoint for load balancers"""
    return {
        "status": "ok",
        "environment": ENVIRONMENT,
        "service": "hockey-mcp-bridge"
    }

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv('BRIDGE_PORT', '3003'))
    host = os.getenv('BRIDGE_HOST', '0.0.0.0')
    
    print(f"🏒 Starting Hockey MCP Bridge API on {host}:{port}")
    print(f"   Environment: {ENVIRONMENT}")
    
    if ENVIRONMENT == 'production':
        print(f"   MCP Server: {os.getenv('MCP_SERVER_URL', 'Not configured')}")
        print(f"   Allowed Origins: {allowed_origins}")
    
    uvicorn.run(app, host=host, port=port)
