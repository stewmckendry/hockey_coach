import argparse
import asyncio
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from agents import gen_trace_id, trace
from agents.mcp import MCPServerSse
from app.client.agent.off_ice_planner import OffIcePlannerManager, OffIceSearchResults


async def run_pipeline(input_text: str) -> OffIceSearchResults:
    async with MCPServerSse(
        name="Off-Ice KB MCP Server",
        params={"url": "http://localhost:8000/sse", "timeout": 30},
    ) as mcp_server:
        trace_id = gen_trace_id()
        with trace("off_ice_search", trace_id=trace_id):
            mgr = OffIcePlannerManager(mcp_server)
            result = await mgr.run(input_text, trace_id=trace_id)
            for item in result.items:
                print(f"- {item.title} ({item.category}) -> pages {item.source_pages}")
            return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Query text for off-ice search")
    args = parser.parse_args()

    if not shutil.which("uv"):
        raise RuntimeError("Missing `uv`. Install it from https://docs.astral.sh/uv/")

    print("🚀 Launching Thunder MCP SSE server at http://localhost:8000/sse ...")

    server_path = Path(__file__).resolve().parent.parent / "mcp_server" / "off_ice_mcp_server.py"
    process: subprocess.Popen[Any] | None = subprocess.Popen(["uv", "run", str(server_path)])
    time.sleep(3)

    print("✅ Server started. Connecting agent...\n")

    try:
        asyncio.run(run_pipeline(args.input))
    finally:
        if process:
            print("\n🛑 Shutting down server...")
            process.terminate()


if __name__ == "__main__":
    main()

