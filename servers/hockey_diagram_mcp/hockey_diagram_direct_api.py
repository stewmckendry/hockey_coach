#!/usr/bin/env python3
"""
Direct FastMCP Integration for Hockey Diagram MCP Server
Provides HTTP API that works with the existing hockey diagram MCP
"""

import sys
import os
import asyncio
import json
from pathlib import Path
from datetime import datetime

# Add the project root to path
sys.path.append(str(Path(__file__).resolve().parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional

# Import the hockey diagram MCP server directly
from server import mcp

app = FastAPI(title="Hockey Diagram MCP Direct API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:8002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ToolRequest(BaseModel):
    tool: str
    parameters: Optional[Dict[str, Any]] = {}

@app.post("/api/mcp")
async def call_mcp_tool(request: ToolRequest):
    """Call a tool directly on the imported hockey diagram MCP server"""
    try:
        # Use the FastMCP Client with in-memory transport
        from fastmcp import Client
        
        client = Client(mcp)  # Direct in-memory connection!
        
        async with client:
            result = await client.call_tool(request.tool, request.parameters)
            
            return {
                "success": True,
                "data": result.data if hasattr(result, 'data') else result,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        print(f"Error calling MCP tool '{request.tool}': {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to call MCP tool: {str(e)}"
        )

@app.post("/generate")
async def generate_diagram(request: dict):
    """Generate a hockey diagram using the agent"""
    try:
        prompt = request.get("prompt", "")
        conversation_id = request.get("conversationId")
        
        # Import the agent module
        from hockey_diagram_agent import generate_hockey_diagram_with_agent
        import os
        import base64
        
        # Generate the diagram using the agent
        context = {"conversation_id": conversation_id} if conversation_id else None
        result = await generate_hockey_diagram_with_agent(prompt, context=context)
        
        # Parse the result to extract the diagram data
        if isinstance(result, dict) and result.get("success"):
            # Read the diagram file and convert to base64
            diagram_path = result.get("diagram_path")
            if diagram_path:
                try:
                    full_path = os.path.join(os.path.dirname(__file__), diagram_path)
                    with open(full_path, 'rb') as f:
                        image_data = f.read()
                        base64_data = base64.b64encode(image_data).decode('utf-8')
                    
                    # Return in the format expected by the web app
                    return {
                        "success": True,
                        "diagram_base64": f"data:image/png;base64,{base64_data}",
                        "metadata": {
                            "tools_used": result.get("tools_used", []),
                            "processing_time_ms": result.get("processing_time", 0) * 1000,  # Convert to ms
                            "parser_type": "agent",
                            "traces": result.get("tool_calls_detail", [])
                        },
                        "explanation": result.get("response", ""),
                        "parser_traces": result.get("parser_traces", {}),
                        "conversation_id": result.get("conversation_id")
                    }
                except Exception as e:
                    print(f"Error reading diagram file: {e}")
                    return {
                        "success": False,
                        "error": f"Failed to read diagram file: {str(e)}"
                    }
            else:
                return {
                    "success": False,
                    "error": "No diagram path in result"
                }
        else:
            return {
                "success": False,
                "error": result.get("error", "Agent returned failure"),
                "details": str(result)
            }
            
    except Exception as e:
        print(f"Error generating diagram: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate diagram: {str(e)}"
        )

@app.get("/api/mcp")
async def health_check():
    """Health check endpoint"""
    try:
        from fastmcp import Client
        
        client = Client(mcp)
        
        async with client:
            # List available tools
            tools = await client.list_tools()
            
            return {
                "status": "healthy",
                "mcpServer": {
                    "protocol": "FastMCP",
                    "transport": "in-memory",
                    "connected": True,
                    "tools_available": len(tools.tools) if hasattr(tools, 'tools') else 0
                },
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        print(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "mcpServer": {
                "protocol": "FastMCP",
                "transport": "in-memory",
                "connected": False,
                "error": str(e)
            },
            "timestamp": datetime.now().isoformat()
        }

@app.get("/tools")
async def list_tools():
    """List available tools from the MCP server"""
    try:
        from fastmcp import Client
        
        client = Client(mcp)
        
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

@app.get("/health")
async def simple_health():
    """Simple health check"""
    return {"status": "healthy", "service": "hockey-diagram-mcp-api"}

if __name__ == "__main__":
    import uvicorn
    import logging
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    port = int(os.environ.get("HOCKEY_DIAGRAM_API_PORT", "8001"))
    
    logger.info(f"Starting Hockey Diagram MCP Direct API on port {port}")
    logger.info("This provides HTTP access to the hockey diagram MCP tools")
    
    uvicorn.run(app, host="0.0.0.0", port=port)