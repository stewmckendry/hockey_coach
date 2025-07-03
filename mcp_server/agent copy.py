import asyncio
import os
import shutil
import subprocess
import time
from typing import Any

from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServerSse
from agents.model_settings import ModelSettings


async def run(agent_mcp_server: MCPServerSse):
    agent = Agent(
        name="Thunder Drill Agent",
        instructions="You are a helpful assistant that knows how to search and explore a hockey drill knowledge base. Use the tools provided by the Thunder Drill MCP server.",
        mcp_servers=[agent_mcp_server],
        model_settings=ModelSettings(tool_choice="required"),
        model="gpt-3.5-turbo"
    )

    message = "Find drills that involve backchecking and skating."
    print(f"🔍 User: {message}\n")

    result = await Runner.run(starting_agent=agent, input=message)
    print("🧠 Assistant:", result.final_output)


async def main():
    async with MCPServerSse(
        name="Thunder MCP Server",
        params={"url": "http://localhost:8000/sse"},
    ) as mcp_server:
        trace_id = gen_trace_id()
        with trace(workflow_name="Thunder Agent Session", trace_id=trace_id):
            print(f"📍 View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await run(mcp_server)


if __name__ == "__main__":
    # Ensure `uv` is installed (or replace with subprocess.run(["python", "server.py"]))
    if not shutil.which("uv"):
        raise RuntimeError("Missing `uv`. Install it from https://docs.astral.sh/uv/")

    print("🚀 Launching Thunder MCP SSE server at http://localhost:8000/sse ...")

    this_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(this_dir, "server.py")

    # Run server in subprocess (or adjust path as needed)
    process: subprocess.Popen[Any] | None = subprocess.Popen(["uv", "run", server_path])
    time.sleep(3)

    print("✅ Server started. Connecting agent...\n")

    try:
        asyncio.run(main())
    finally:
        if process:
            print("\n🛑 Shutting down server...")
            process.terminate()
