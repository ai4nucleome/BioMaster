from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_opencode_native_choice_policy_is_documented():
    paths = [
        ROOT / ".opencode" / "skills" / "biomaster" / "SKILL.md",
        ROOT / ".opencode" / "agents" / "biomaster-plan.md",
        ROOT / ".opencode" / "commands" / "biomaster-start.md",
        ROOT / ".opencode" / "commands" / "biomaster-plan.md",
        ROOT / ".opencode" / "commands" / "biomaster-resume.md",
    ]
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "OpenCode" in text
        assert "native option selector" in text
        assert "QuestionTool" in text


def test_project_choice_options_are_explicit():
    text = (ROOT / ".opencode" / "agents" / "biomaster-plan.md").read_text(encoding="utf-8")
    for option in [
        "Continue existing project",
        "Create new suffixed project",
        "Review existing results",
        "Review completed results",
        "Create new project from scratch",
    ]:
        assert option in text
