import argparse
import asyncio
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from agents import gen_trace_id, trace
from agents.mcp import MCPServerSse
from app.client.drill_planner import DrillPlannerManager


async def run_pipeline(input_text: str):
    async with MCPServerSse(
        name="Drills MCP Server",
        params={"url": "http://localhost:8000/sse"},
    ) as mcp_server:
        trace_id = gen_trace_id()
        with trace("drill_planner", trace_id=trace_id):
            mgr = DrillPlannerManager(mcp_server)
            result = await mgr.run(input_text, trace_id=trace_id)
            print("\n🧠 Summary:\n")
            print(result.summary.summary)
            return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Query text to search drills")
    args = parser.parse_args()

    if not shutil.which("uv"):
        raise RuntimeError("Missing `uv`. Install it from https://docs.astral.sh/uv/")

    print("🚀 Launching Drills MCP SSE server at http://localhost:8000/sse ...")

    server_path = Path(__file__).resolve().parent.parent / "mcp_server" / "drills_mcp_server.py"
    process: subprocess.Popen[Any] | None = subprocess.Popen(["uv", "run", str(server_path)])
    time.sleep(3)

    print("✅ Server started. Connecting agent...\n")

    try:
        asyncio.run(run_pipeline(args.input))
    finally:
        if process:
            print("\n🛑 Shutting down server...")
            process.terminate()
