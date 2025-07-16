from __future__ import annotations

import argparse
import asyncio
import shutil
import subprocess
import time
from datetime import date
from pathlib import Path
from typing import Any, Optional

from agents import gen_trace_id, trace
from agents.mcp import MCPServerSse

from models.dryland_models import DrylandContext
from .dryland_planner_agent import run_agent as run_plan_agent
from .dryland_session_agent import run_agent as run_session_agent


async def run_pipeline(session_date: Optional[date] = None) -> None:
    async with MCPServerSse(
        name="Off-Ice KB MCP Server",
        params={"url": "http://localhost:8000/sse", "timeout": 30},
    ) as mcp_server:
        ctx = DrylandContext()
        trace_id = gen_trace_id()
        with trace("dryland_plan", trace_id=trace_id):
            plan = await run_plan_agent(ctx)
            ctx.plan = plan
        if session_date:
            with trace("dryland_session", trace_id=trace_id):
                session = await run_session_agent(session_date, ctx)
                out_dir = Path("data/generated")
                out_dir.mkdir(parents=True, exist_ok=True)
                (out_dir / f"session_{session_date}.json").write_text(
                    session.model_dump_json(indent=2), encoding="utf-8"
                )
                print(f"✅ Session for {session_date} saved")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, help="Generate session for this date (YYYY-MM-DD)")
    args = parser.parse_args()

    if not shutil.which("uv"):
        raise RuntimeError("Missing `uv`. Install it from https://docs.astral.sh/uv/")

    print("🚀 Launching Thunder MCP SSE server at http://localhost:8000/sse ...")

    server_path = Path(__file__).resolve().parents[1] / "mcp_server" / "off_ice" / "off_ice_mcp_server.py"
    process: subprocess.Popen[Any] | None = subprocess.Popen(["uv", "run", str(server_path)])
    time.sleep(3)

    print("✅ Server started. Connecting agent...\n")

    try:
        ses_date = date.fromisoformat(args.date) if args.date else None
        asyncio.run(run_pipeline(ses_date))
    finally:
        if process:
            print("\n🛑 Shutting down server...")
            process.terminate()


if __name__ == "__main__":
    main()

