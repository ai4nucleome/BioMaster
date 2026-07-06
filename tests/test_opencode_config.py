from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]


def test_plan_is_only_registered_primary_agent():
    config = json.loads((ROOT / ".opencode" / "opencode.json").read_text(encoding="utf-8"))
    agents = config["agent"]

    assert "biomaster-intake" not in agents
    runtime_agents = {
        "biomaster-plan",
        "biomaster-execute",
        "biomaster-debug",
        "biomaster-check",
    }
    management_agents = {
        "biomaster-skiller",
        "biomaster-skill-author",
        "biomaster-skill-creator",
    }
    assert runtime_agents.issubset(agents)
    assert management_agents.issubset(agents)
    assert agents["biomaster-plan"]["mode"] == "primary"

    primary_agents = [name for name, spec in agents.items() if spec.get("mode") == "primary"]
    assert primary_agents == ["biomaster-plan"]
    assert all(agents[name]["mode"] == "subagent" for name in runtime_agents - {"biomaster-plan"})
    assert all(agents[name]["mode"] == "subagent" for name in management_agents)


def test_runtime_prompt_files_keep_v02_skeleton_with_optional_skill_management_agents():
    agent_files = {path.name for path in (ROOT / ".opencode" / "agents").glob("*.md")}
    runtime_files = {
        "biomaster-plan.md",
        "biomaster-execute.md",
        "biomaster-debug.md",
        "biomaster-check.md",
    }
    management_files = {
        "biomaster-skiller.md",
        "biomaster-skill-author.md",
        "biomaster-skill-creator.md",
    }
    assert runtime_files.issubset(agent_files)
    assert management_files.issubset(agent_files)
