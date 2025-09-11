#!/usr/bin/env python3
"""
Direct FastMCP Integration - Simple HTTP API that works with the existing hockey MCP
"""

import sys
import os
import asyncio
import json
from pathlib import Path

# Add the project root to path
sys.path.append(str(Path(__file__).resolve().parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional

# Import the hockey MCP server directly
sys.path.append(str(Path(__file__).resolve().parent))
from hockey_mcp import mcp

app = FastAPI(title="Hockey MCP Direct API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ToolRequest(BaseModel):
    tool: str
    parameters: Optional[Dict[str, Any]] = {}

@app.post("/api/mcp")
async def call_mcp_tool(request: ToolRequest):
    """Call a tool directly on the imported hockey MCP server"""
    try:
        # Check if this is an external MCP tool call
        if request.tool.startswith('mcp__'):
            # For external MCP tools like Exa, return a fallback response
            # The frontend should handle these separately or we need a different architecture
            return {
                "success": False,
                "error": f"External MCP tool '{request.tool}' not supported via Direct API. Use fallback to local knowledge.",
                "fallback": True,
                "timestamp": "2025-07-23T20:30:00Z"
            }
        else:
            # Use the FastMCP Client with in-memory transport for local hockey MCP
            from fastmcp import Client
            
            client = Client(mcp)  # Direct in-memory connection!
            
            async with client:
                result = await client.call_tool(request.tool, request.parameters)
                
                return {
                    "success": True,
                    "data": result,
                    "timestamp": "2025-07-23T20:30:00Z"
                }
            
    except Exception as e:
        print(f"Error calling tool '{request.tool}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mcp")
async def health_check():
    """Health check using direct MCP connection"""
    try:
        from fastmcp import Client
        
        client = Client(mcp)
        
        async with client:
            await client.ping()
            tools = await client.list_tools()
            
            return {
                "status": "healthy",
                "mcpServer": {
                    "type": "in-memory",
                    "protocol": "FastMCP Direct",
                    "connected": True,
                    "tools_available": len(tools.tools) if hasattr(tools, 'tools') else 0
                },
                "timestamp": "2025-07-23T20:30:00Z"
            }
            
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2025-07-23T20:30:00Z"
        }

@app.get("/tools")
async def list_tools():
    """List available tools"""
    try:
        from fastmcp import Client
        
        client = Client(mcp)
        
        async with client:
            tools = await client.list_tools()
            return {
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

if __name__ == "__main__":
    import uvicorn
    print("🏒 Starting Hockey MCP Direct API on port 3003...")
    uvicorn.run(app, host="0.0.0.0", port=3003)
