"""Phase and skill-loading policy for the fixed BioMaster workflow."""

from __future__ import annotations

PHASE_ALLOWED_LAYERS: dict[str, set[str]] = {
    "init": {"registry"},
    "mode_selection": {"registry", "domain-guide"},
    "domain_anchoring": {"registry", "domain-guide"},
    "pipeline_routing": {"registry", "domain-guide", "discipline", "pipeline"},
    "planning": {"registry", "domain-guide", "discipline", "pipeline", "plan", "report", "bioskill"},
    "preflight": {"execute", "env", "verify", "bioskill"},
    "execution": {"execute", "env", "verify", "bioskill"},
    "checking": {"execute", "verify", "bioskill"},
    "debugging": {"debug", "env", "execute", "verify", "bioskill"},
    "reporting": {"report", "verify", "bioskill"},
    "done": set(),
}

FIXED_PHASE_ORDER: tuple[str, ...] = (
    "init",
    "mode_selection",
    "domain_anchoring",
    "pipeline_routing",
    "planning",
    "preflight",
    "execution",
    "debugging",
    "checking",
    "reporting",
    "done",
)

VALID_PHASE_TRANSITIONS: dict[str, set[str]] = {
    "init": {"mode_selection"},
    "mode_selection": {"domain_anchoring"},
    "domain_anchoring": {"pipeline_routing"},
    "pipeline_routing": {"planning"},
    "planning": {"preflight"},
    "preflight": {"execution"},
    "execution": {"debugging"},
    "debugging": {"execution", "checking"},
    "checking": {"debugging", "execution", "reporting"},
    "reporting": {"done"},
    "done": set(),
}

PRIMARY_USER_AGENT = "biomaster-plan"
SUBAGENT_BY_PHASE: dict[str, str] = {
    "planning": "biomaster-plan",
    "preflight": "biomaster-execute",
    "execution": "biomaster-execute",
    "checking": "biomaster-check",
    "debugging": "biomaster-debug",
    "reporting": "biomaster-plan",
}

# Early phases load only these skill ID patterns from route candidates.
# Prefix patterns end with "-" (e.g. "domain-guide-"). Exact IDs match literally.
PHASE_CORE_SKILL_PATTERNS: dict[str, tuple[str, ...]] = {
    "init": ("biomaster",),
    "mode_selection": ("biomaster",),
    "domain_anchoring": ("biomaster", "registry", "domain-guide-"),
    "pipeline_routing": (
        "registry",
        "domain-guide-",
        "discipline-",
        "pipeline-",
    ),
    "planning": (
        "registry",
        "domain-guide-",
        "discipline-",
        "biomaster",
        "pipeline-",
        "plan-",
    ),
}


def matches_core_skill(skill_id: str, patterns: tuple[str, ...]) -> bool:
    for pattern in patterns:
        if pattern.endswith("-"):
            if skill_id.startswith(pattern):
                return True
        elif skill_id == pattern:
            return True
    return False


def filter_core_skills(phase: str, skill_ids: list[str]) -> list[str]:
    patterns = PHASE_CORE_SKILL_PATTERNS.get(phase)
    if not patterns:
        return skill_ids
    return [skill_id for skill_id in skill_ids if matches_core_skill(skill_id, patterns)]


def default_skills_for_phase(phase: str) -> list[str]:
    if phase in {"init", "mode_selection", "domain_anchoring"}:
        return ["biomaster"]
    return []


def validate_phase(phase: str) -> list[str]:
    if phase not in PHASE_ALLOWED_LAYERS:
        return [f"unknown phase: {phase}"]
    return []


def validate_phase_transition(previous_phase: str | None, next_phase: str) -> list[str]:
    errors = validate_phase(next_phase)
    if errors:
        return errors
    if previous_phase is None:
        if next_phase != "init":
            return [f"workflow must start at init, not {next_phase}"]
        return []
    if next_phase not in VALID_PHASE_TRANSITIONS.get(previous_phase, set()):
        return [f"invalid phase transition: {previous_phase} -> {next_phase}"]
    return []
