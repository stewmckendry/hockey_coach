from __future__ import annotations

from pathlib import Path

from models.dryland_models import DrylandContext
from client.shared.agent_templates import create_intake_agent
from client.off_ice.dryland_context_tools import set_dryland_context_param

PROMPTS_DIR = Path(__file__).resolve().parents[3] / "prompts" / "off_ice"


def _load_prompt() -> str:
    path = PROMPTS_DIR / "dryland_plan_prompt.yaml"
    with open(path, "r", encoding="utf-8") as f:
        return "".join(f.readlines()[1:]).lstrip()


def get_dryland_intake_agent():
    """Instantiate the dryland planning intake agent."""
    prompt = _load_prompt()
    return create_intake_agent(
        DrylandContext,
        prompt,
        [set_dryland_context_param],
        name="DrylandPlanIntakeAgent",
    )
