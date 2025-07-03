# Codex Agent Task: Build Season Plan Orchestrator for Hockey Coach AI Assistant

## 🏋️ Overview

You are building a multi-agent orchestrator called `SeasonPlannerAgent` to help youth hockey coaches create a full-season development plan. This includes:

* Team identity and development goals
* Player cards with skills, learning needs, positioning tips
* Month-by-month skill + drill progression
* Practice templates that match LTAD and positional development

The system is intended to be used by volunteer coaches, so it must generate high-quality outputs that are editable, understandable, and tailored to the team's age and level.

This agent must be implemented using the **OpenAI Agents SDK** and **Model Context Protocol (MCP)**, consistent with the existing architecture (e.g., `drill_planner_agent.py`, `main.py`).

---

## 🔧 What to Build

### 1. `season_planner_agent.py`

* A new orchestrator agent modeled after `drill_planner_agent`
* Gathers context from the coach (age group, goals, start/end dates)
* Invokes a panel of sub-agents (e.g., TeamIdentityAgent, SkillProgressionAgent, PlayerCardAgent)
* Outputs a structured season plan object

### 2. Sub-Agents

| Agent                   | Purpose                                                                          |
| ----------------------- | -------------------------------------------------------------------------------- |
| `TeamIdentityAgent`     | Generates team "mission" and core style (e.g. speed, structure, creativity)      |
| `SkillProgressionAgent` | Builds a month-by-month ladder of core and positional skills                     |
| `PlayerCardAgent`       | Generates editable player profiles: strengths, needs, role, goals, off-ice notes |
| `PracticeTemplateAgent` | Suggests sample templates with time blocks and drill categories                  |
| `EvaluatorAgent`        | Scores plan for coverage, clarity, and LTAD compliance                           |

### 3. Input Prompt YAML

* Create `prompts/season_planner_prompt.yaml`
* Should allow flexible coach input:

  * "We're a U11 team with good skating but need puck support work."
  * "I want us to be a hard-working, fast-transition team."

### 4. Output Schema (`SeasonPlan`)

```python
class SeasonPlan(BaseModel):
    team_identity: str
    goals: list[str]
    skill_progression: dict[str, list[str]]  # e.g. {"October": ["Backward Skating", "Passing"]}
    player_cards: list[PlayerCard]
    practice_templates: list[PracticeTemplate]

class PlayerCard(BaseModel):
    name: str
    strengths: list[str]
    focus_areas: list[str]
    position: str
    notes: str
    off_ice: Optional[str]

class PracticeTemplate(BaseModel):
    name: str
    blocks: list[dict[str, str]]  # e.g. [ {"Drill": "Tight Turns Relay", "Time": "10 min"} ]
```

---

## 🔹 Integration Tasks

### 5. `season_planner.py` + `SeasonPlannerManager`

* Implement manager class similar to `DrillPlannerManager`
* Should be run from `main.py` with flag or mode to switch between agents
* Ensure it sets `mcp_server` and `model` fields

### 6. Update `main.py`

* Add CLI support for `--mode season` to run `SeasonPlannerManager`
* Reuse trace + SSE launch logic from existing flow【58†source】

### 7. UI Hooks (Future)

* Add React UI wireframe to edit:

  * Team goals
  * Player card notes
  * Practice templates

---

## 🎧 Reference Files

* `drill_planner.py` — agent orchestration pattern【57†source】
* `main.py` — CLI + SSE bootstrap + MCP runner【58†source】
* `summarizer_agent.py` — prompt loading
* `Agents.md` — dev standards

---

## ✨ Stretch Goals

* Embed LTAD data into progression planning
* Suggest off-ice activities for each month
* Render monthly calendar output with practice themes
