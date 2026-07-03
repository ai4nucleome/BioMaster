from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_intake_requires_visible_worker_subagents():
    paths = [
        ROOT / ".opencode" / "skills" / "biomaster" / "SKILL.md",
        ROOT / ".opencode" / "agents" / "biomaster-intake.md",
        ROOT / ".opencode" / "commands" / "biomaster-run.md",
    ]
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "@biomaster-execute" in text
        assert "@biomaster-debug" in text
        assert "@biomaster-check" in text

    intake = (ROOT / ".opencode" / "agents" / "biomaster-intake.md").read_text(encoding="utf-8")
    assert "Do not satisfy worker phases by running Python runtime helpers" in intake
    assert "run_step_cycle()" in intake
