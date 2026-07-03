from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / ".opencode" / "agents"


def test_agents_define_readable_progress_cards():
    expectations = {
        "biomaster-plan.md": ["## Readable Progress Display", "## BioMaster Status", "| Stage | Status | Key Evidence |"],
        "biomaster-execute.md": ["## Readable Progress Display", "## Execute Result", "| Item | Path |"],
        "biomaster-debug.md": ["## Readable Progress Display", "## Debug Review", "| Evidence | Path / Summary |"],
        "biomaster-check.md": ["## Readable Progress Display", "## Check Review", "| Expected Output | Status | Evidence |"],
    }
    for filename, snippets in expectations.items():
        text = (AGENTS / filename).read_text(encoding="utf-8")
        for snippet in snippets:
            assert snippet in text
