import argparse
import asyncio
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from agents import gen_trace_id, trace
from agents.mcp import MCPServerSse
from .off_ice_workout_planner import OffIceWorkoutPlannerManager, WorkoutPlanOutput


async def run_pipeline(input_text: str, generate_images: bool = False, include_video: bool = False) -> WorkoutPlanOutput:
    async with MCPServerSse(
        name="Off-Ice KB MCP Server",
        params={"url": "http://localhost:8000/sse", "timeout": 30},
    ) as mcp_server:
        trace_id = gen_trace_id()
        with trace("off_ice_workout", trace_id=trace_id):
            mgr = OffIceWorkoutPlannerManager(mcp_server, generate_images=generate_images)
            result = await mgr.run(input_text, include_video=include_video, trace_id=trace_id)
            return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Workout plan request")
    parser.add_argument("--generate-images", action="store_true", help="Include generated visuals")
    parser.add_argument("--include-video", action="store_true", help="Include video summary")
    args = parser.parse_args()

    if not shutil.which("uv"):
        raise RuntimeError("Missing `uv`. Install it from https://docs.astral.sh/uv/")

    print("🚀 Launching Thunder MCP SSE server at http://localhost:8000/sse ...")

    server_path = Path(__file__).resolve().parents[1] / "mcp_server" / "off_ice" / "off_ice_mcp_server.py"
    process: subprocess.Popen[Any] | None = subprocess.Popen(["uv", "run", str(server_path)])
    time.sleep(3)

    print("✅ Server started. Connecting agent...\n")

    try:
        result = asyncio.run(run_pipeline(args.input, generate_images=args.generate_images, include_video=args.include_video))
        print(f"Plan saved to {result.file_path}")
    finally:
        if process:
            print("\n🛑 Shutting down server...")
            process.terminate()


if __name__ == "__main__":
    main()
