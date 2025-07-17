from __future__ import annotations

from pathlib import Path
import yaml


def load_prompt_yaml(path: str | Path) -> str:
    """Load a YAML prompt file and return the prompt text."""
    path = Path(path)
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if isinstance(data, dict):
        return str(data.get("prompt", ""))
    return str(data)
