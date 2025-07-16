from __future__ import annotations

"""Agent to draft the agenda for a dryland workout session."""

import argparse
import asyncio
from pathlib import Path
from typing import List

from pydantic import BaseModel
from agents import Agent, Runner
from agents.mcp import MCPServerSse

from .input_structurer import StructuredInput

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts" / "off_ice"


def _load_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    with open(path, "r", encoding="utf-8") as f:
        return "".join(f.readlines()[1:]).lstrip()


class DrylandOutline(BaseModel):
    agenda: str


dryland_structure_agent = Agent(
    name="DrylandStructureAgent",
    instructions=_load_prompt("outline_prompt.yaml"),
    output_type=DrylandOutline,
    mcp_servers=[MCPServerSse(name="Off-Ice KB MCP Server", params={"url": "http://localhost:8000/sse", "timeout": 30})],
    model="gpt-4o",
)


async def run_agent(
    data: StructuredInput, *, needs_approval: bool = False
) -> tuple[DrylandOutline, str]:
    """Run the structure agent and optionally require approval.

    If ``needs_approval`` is True the run will pause for user feedback via the
    Agents SDK approval flow. Any comment returned from the approval UI is
    extracted from the ``MCPApprovalResponseItem`` and returned alongside the
    parsed outline.
    """
    res = await Runner.run(
        dryland_structure_agent, data.model_dump_json(), needs_approval=needs_approval
    )
    outline = res.final_output_as(DrylandOutline)

    comment = ""
    from agents.items import MCPApprovalResponseItem

    for item in res.new_items:
        if isinstance(item, MCPApprovalResponseItem):
            try:
                comment = item.raw_item.comment  # type: ignore[attr-defined]
            except AttributeError:
                comment = getattr(item.raw_item, "input", "[Feedback not found in raw_item.input]")

    return outline, comment


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True, help="Structured input JSON")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dryland_structure.json"),
        help="Where to save outline JSON",
    )
    args = parser.parse_args()

    structured = StructuredInput.model_validate_json(args.input.read_text())
    outline = asyncio.run(run_agent(structured))
    args.output.write_text(outline.model_dump_json(indent=2), encoding="utf-8")
    print(f"✅ Dryland outline saved to {args.output}")


if __name__ == "__main__":
    main()
