from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_plan_prompt_requires_project_discovery_and_semantic_ids():
    text = (ROOT / ".opencode" / "agents" / "biomaster-plan.md").read_text(encoding="utf-8")
    assert "always inspect `projects/`" in text
    assert "PLAN.yaml`, `PROJECT_LOG.yaml`, and `CHECK_REPORT.yaml`" in text
    assert "dataset, analysis type, and scientific goal" in text
    assert "Do not use ambiguous numeric slugs" in text


def test_plan_prompt_limits_step_confirmation_noise():
    text = (ROOT / ".opencode" / "agents" / "biomaster-plan.md").read_text(encoding="utf-8")
    assert "Ask for user confirmation once before starting or resuming the step loop" in text
    assert "Do not ask for a clickable option before every normal step" in text
    assert "Continue from step N to step N+1 automatically after Check passes" in text


def test_plan_prompt_defaults_to_concise_user_display():
    text = (ROOT / ".opencode" / "agents" / "biomaster-plan.md").read_text(encoding="utf-8")
    assert "Default to concise mode" in text
    assert "Do not expose long internal deliberation" in text
    assert "Offer `Show details` / `Continue concise`" in text


def test_check_prompt_requires_detailed_project_log():
    text = (ROOT / ".opencode" / "agents" / "biomaster-check.md").read_text(encoding="utf-8")
    for snippet in [
        "`PROJECT_LOG.yaml` is the durable project memory",
        "`plan_context`",
        "`skill_evidence`",
        "`artifacts`",
        "`next_action`",
    ]:
        assert snippet in text


def test_sqlite_readiness_is_a_hard_gate():
    skill = (ROOT / ".opencode" / "skills" / "biomaster" / "SKILL.md").read_text(encoding="utf-8")
    plan = (ROOT / ".opencode" / "agents" / "biomaster-plan.md").read_text(encoding="utf-8")
    execute = (ROOT / ".opencode" / "agents" / "biomaster-execute.md").read_text(encoding="utf-8")

    assert "On skill load, ensure the SQLite control plane is ready" in skill
    assert "Plan must include SQLite route search evidence" in skill
    assert "Execute must query SQLite `skills`" in skill
    assert "sqlite_readiness" in plan
    assert "Do not proceed from prompt memory alone" in execute
