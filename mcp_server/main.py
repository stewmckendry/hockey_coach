# main.py (updated)

import asyncio
import os
import shutil
import subprocess
import time
import argparse
from typing import Any
from agents import gen_trace_id, trace
from agents.mcp import MCPServerSse

from drill_planner import DrillPlannerManager


async def main(input_text: str):
    async with MCPServerSse(
        name="Thunder MCP Server",
        params={"url": "http://localhost:8000/sse"},
    ) as mcp_server:
        trace_id = gen_trace_id()
        with trace(workflow_name="Thunder Drill Planner", trace_id=trace_id):
            print(f"📍 View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            mgr = DrillPlannerManager(mcp_server)
            result = await mgr.run(input_text, trace_id=trace_id)

            print("\n--- Drill Planner Output ---\n")
            print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Query text to search drills")
    args = parser.parse_args()

    if not shutil.which("uv"):
        raise RuntimeError("Missing `uv`. Install it from https://docs.astral.sh/uv/")

    print("🚀 Launching Thunder MCP SSE server at http://localhost:8000/sse ...")

    this_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(this_dir, "server.py")

    process: subprocess.Popen[Any] | None = subprocess.Popen(["uv", "run", server_path])
    time.sleep(3)

    print("✅ Server started. Connecting agent...\n")

    try:
        asyncio.run(main(args.input))
    finally:
        if process:
            print("\n🛑 Shutting down server...")
            process.terminate()
