from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_plan_steps_drive_visible_task_checklist():
    files = [
        ROOT / ".opencode" / "skills" / "biomaster" / "SKILL.md",
        ROOT / ".opencode" / "agents" / "biomaster-intake.md",
        ROOT / ".opencode" / "commands" / "biomaster-plan.md",
    ]
    for path in files:
        text = path.read_text(encoding="utf-8")
        assert "PLAN.yaml.steps" in text
        assert "task count" in text.lower() or "checklist count" in text.lower()

    intake = (ROOT / ".opencode" / "agents" / "biomaster-intake.md").read_text(encoding="utf-8")
    assert "one task per `PLAN.yaml.steps[]` entry" in intake
    assert "Mark a step task complete only after the corresponding Check result is `pass`" in intake

    run_command = (ROOT / ".opencode" / "commands" / "biomaster-run.md").read_text(encoding="utf-8")
    assert "Mark `Step <step_id>` complete only after `@biomaster-check` returns `pass`" in run_command
