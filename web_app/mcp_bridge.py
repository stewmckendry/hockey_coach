#!/usr/bin/env python3
"""
FastMCP Bridge Server for Hockey Coach Web App

This service acts as a bridge between the Next.js web application and the FastMCP hockey server.
It uses the FastMCP Python client to connect to the hockey MCP server and exposes a simple
HTTP API that the web app can call.
"""

import asyncio
import json
import logging
from typing import Any, Dict, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastmcp import Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models
class MCPRequest(BaseModel):
    tool: str
    parameters: Dict[str, Any] = {}

class MCPResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: str

# Create FastAPI application
app = FastAPI(
    title="Hockey Coach MCP Bridge",
    description="Bridge service between web app and FastMCP hockey server",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Hockey Coach MCP Bridge",
        "status": "running",
        "description": "Bridge service between web app and FastMCP hockey server"
    }

@app.post("/api/mcp", response_model=MCPResponse)
async def call_mcp_tool(request: MCPRequest):
    """
    Call an MCP tool through the FastMCP client
    
    This endpoint receives tool calls from the web app and forwards them
    to the hockey MCP server using the FastMCP client.
    """
    try:
        logger.info(f"🔧 Calling tool: {request.tool} with parameters: {request.parameters}")
        
        # Create client for each request (following FastMCP patterns)
        client = Client("http://localhost:8000")
        
        # Use async context manager as recommended by FastMCP docs
        async with client:
            # Ping to verify connection
            await client.ping()
            
            # Call the requested tool
            result = await client.call_tool(request.tool, request.parameters)
            
            logger.info(f"✅ Tool {request.tool} executed successfully")
            
            return MCPResponse(
                success=True,
                data=result.content if hasattr(result, 'content') else result,
                timestamp=datetime.now().isoformat()
            )
            
    except Exception as e:
        error_msg = f"Error calling tool {request.tool}: {str(e)}"
        logger.error(f"❌ {error_msg}")
        
        return MCPResponse(
            success=False,
            error=error_msg,
            timestamp=datetime.now().isoformat()
        )

@app.get("/health")
async def health_check():
    """Detailed health check with MCP server connectivity"""
    try:
        # Test connection to MCP server
        client = Client("http://localhost:8000")
        async with client:
            await client.ping()
            tools = await client.list_tools()
            
        return {
            "status": "healthy",
            "mcp_server": "connected",
            "available_tools": len(tools.tools) if hasattr(tools, 'tools') else 0,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "mcp_server": "disconnected",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🏒 Starting Hockey Coach MCP Bridge Server")
    uvicorn.run(
        app,
        host="0.0.0.0", 
        port=3002,
        reload=False,
        log_level="info"
    )
