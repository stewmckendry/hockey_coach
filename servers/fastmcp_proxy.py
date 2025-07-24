#!/usr/bin/env python3
"""
FastMCP API Proxy Server
Provides HTTP API endpoints that use FastMCP Client to communicate with the hockey MCP server
"""

import asyncio
import json
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
from fastmcp import Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Hockey MCP API Proxy", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
MCP_SERVER_URL = "http://localhost:8000"

class ToolRequest(BaseModel):
    tool: str
    parameters: Optional[Dict[str, Any]] = {}

class ToolResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: str

@app.post("/api/mcp", response_model=ToolResponse)
async def call_mcp_tool(request: ToolRequest):
    """Call a tool on the FastMCP hockey server using FastMCP client"""
    try:
        # Create FastMCP client pointing to our hockey server
        client = Client(MCP_SERVER_URL)
        
        async with client:
            # Test connection first
            await client.ping()
            
            # Call the requested tool
            result = await client.call_tool(request.tool, request.parameters)
            
            return ToolResponse(
                success=True,
                data=result.data if hasattr(result, 'data') else result,
                timestamp=datetime.now().isoformat()
            )
            
    except Exception as e:
        logger.error(f"Error calling MCP tool '{request.tool}': {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to call MCP tool: {str(e)}"
        )

@app.get("/api/mcp")
async def health_check():
    """Health check endpoint"""
    try:
        client = Client(MCP_SERVER_URL)
        
        async with client:
            await client.ping()
            
            # List available tools
            tools = await client.list_tools()
            
            return {
                "status": "healthy",
                "mcpServer": {
                    "url": MCP_SERVER_URL,
                    "protocol": "FastMCP",
                    "connected": True,
                    "tools_available": len(tools.tools) if hasattr(tools, 'tools') else 0
                },
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "mcpServer": {
                "url": MCP_SERVER_URL,
                "protocol": "FastMCP",
                "connected": False,
                "error": str(e)
            },
            "timestamp": datetime.now().isoformat()
        }

@app.get("/tools")
async def list_tools():
    """List available tools from the MCP server"""
    try:
        client = Client(MCP_SERVER_URL)
        
        async with client:
            tools = await client.list_tools()
            return {
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.inputSchema
                    }
                    for tool in (tools.tools if hasattr(tools, 'tools') else [])
                ]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    from datetime import datetime
    
    logger.info("Starting FastMCP API Proxy server...")
    uvicorn.run(app, host="0.0.0.0", port=3002)
