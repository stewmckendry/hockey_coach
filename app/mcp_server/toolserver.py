from __future__ import annotations

"""Minimal FastMCP server exposing the ElicitationTool."""

from fastapi import Request
from fastmcp.server.fastmcp import FastMCP
from fastmcp.server.http import create_sse_app
import uvicorn

from .elicitation_tool import mcp as elicitation_mcp, responses

# Compose tool server with elicitation tool registered
server = FastMCP("ToolServer", tools=[elicitation_mcp])

app = create_sse_app(server, message_path="/messages", sse_path="/sse")


@app.post("/submit")
async def submit(req: Request) -> dict[str, str]:
    data = await req.json()
    session_id = data.get("session_id")
    answer = data.get("response")
    if session_id and answer:
        responses[session_id] = answer
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
