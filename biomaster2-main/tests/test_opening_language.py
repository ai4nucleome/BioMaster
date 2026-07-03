from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_biomaster_opening_is_english_only():
    paths = [
        ROOT / ".opencode" / "skills" / "biomaster" / "SKILL.md",
        ROOT / ".opencode" / "agents" / "biomaster-plan.md",
    ]
    forbidden = [
        "我是 BioMaster Intake Agent",
        "请选择运行模式",
        "测试模式",
        "正式分析",
        "自定义说明",
    ]
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "MUST be in English" in text
        for phrase in forbidden:
            assert phrase not in text


def test_biomaster_opening_uses_readable_start_card():
    paths = [
        ROOT / ".opencode" / "skills" / "biomaster" / "SKILL.md",
        ROOT / ".opencode" / "agents" / "biomaster-plan.md",
    ]
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "## BioMaster Ready" in text
        assert "| Mode | Use Case | Next Step |" in text
        assert "**Primary agent:** `biomaster-plan`" in text
        assert "**Workspace model:** `projects/<project_slug>/`" in text
