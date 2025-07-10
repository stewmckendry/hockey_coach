"""Utility to normalize and infer LTAD skill metadata without using an LLM."""

from __future__ import annotations
import re
from models.ltad import LTADSkill

LTAD_STAGE_LOOKUP = {
    "U7": "Fundamentals 1",
    "U9": "Fundamentals 2",
    "U11": "Learn to Train",
    "U13": "Train to Train",
}

def infer_age_group_from_filename(filename: str) -> str | None:
    match = re.search(r"u\d{1,2}", filename.lower())
    if match:
        return match.group(0).upper()
    return None


def infer_age_group_from_text(text: str) -> str | None:
    match = re.search(r"U\d{1,2}", text.upper())
    if match:
        return match.group(0)
    return None


def normalize_ltad_skill(skill: dict) -> dict:
    """Rule-based normalization for LTAD skill metadata."""
    result = skill.copy()

    # Infer age group from source filename if missing
    if not result.get("age_group") and result.get("source"):
        ag = infer_age_group_from_filename(result["source"])
        if ag:
            result["age_group"] = ag

    # Map ltad_stage from age group if missing
    ag = result.get("age_group")
    if ag and not result.get("ltad_stage"):
        result["ltad_stage"] = LTAD_STAGE_LOOKUP.get(ag)

    # Ensure position list and title case
    pos = result.get("position") or ["Any"]
    cleaned_pos = []
    for p in pos:
        p_low = p.lower()
        if p_low.startswith("forw"):
            cleaned_pos.append("Forward")
        elif p_low.startswith("defenc") or p_low.startswith("defens"):
            cleaned_pos.append("Defence")
        elif p_low.startswith("goal"):
            cleaned_pos.append("Goalie")
        else:
            cleaned_pos.append("Any")
    result["position"] = sorted(set(cleaned_pos))

    # Basic cleanup for variant formatting
    if result.get("variant"):
        v = result["variant"].lower()
        v = v.replace("forward and backward", "fwd+bwd")
        v = v.replace("forward & backward", "fwd+bwd")
        v = v.replace("forward/backward", "fwd+bwd")
        v = v.replace("around circle", "circle")
        v = v.replace("-", ",")
        v = v.replace("  ", " ")
        result["variant"] = v.strip(" ,;")

    return LTADSkill(**result).model_dump()
