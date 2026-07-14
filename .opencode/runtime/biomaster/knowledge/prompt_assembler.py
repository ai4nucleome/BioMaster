from __future__ import annotations

from pathlib import Path
import argparse
import json

from biomaster.knowledge import (
    DEFAULT_DB_PATH,
    PROJECT_ROOT,
    connect,
    ensure_knowledge_db,
    ensure_schema,
    json_loads,
    normalize_agent_name,
)
from biomaster.knowledge.query_skills import get_skill_by_id
from biomaster.knowledge.state_manager import get_disabled_skill_ids


from biomaster.knowledge.phases import PHASE_ALLOWED_LAYERS, SUBAGENT_BY_PHASE


def read_contract_file(relative_path: str) -> str:
    path = PROJECT_ROOT / relative_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def read_manifest_files(manifest_dir: Path) -> list[tuple[str, str]]:
    if not manifest_dir.exists():
        return []
    items: list[tuple[str, str]] = []
    for path in sorted(manifest_dir.glob("*.md")):
        items.append((path.name, path.read_text(encoding="utf-8")))
    return items


def assemble_prompt(
    *,
    agent_name: str,
    phase: str,
    selected_skill_ids: list[str],
    run_id: str | None = None,
    db_path: Path = DEFAULT_DB_PATH,
) -> dict[str, object]:
    ensure_knowledge_db(db_path)
    agent = normalize_agent_name(agent_name)
    expected_agent = SUBAGENT_BY_PHASE.get(phase)
    phase_agent_allowed = expected_agent is None or agent == expected_agent
    connection = connect(db_path)
    try:
        ensure_schema(connection)
        disabled = get_disabled_skill_ids(connection, run_id) if run_id else set()
        allowed_layers = PHASE_ALLOWED_LAYERS.get(phase, set())

        inserted_skills: list[str] = []
        inserted_manifests: list[str] = []
        skipped_skills: list[str] = []
        context_blocks: list[str] = []

        for skill_id in selected_skill_ids:
            if not phase_agent_allowed or skill_id in disabled:
                skipped_skills.append(skill_id)
                continue
            skill = get_skill_by_id(connection, skill_id, agent_name=agent)
            if skill is None:
                skipped_skills.append(skill_id)
                continue
            layer = str(skill.get("layer") or "")
            if allowed_layers and layer not in allowed_layers:
                skipped_skills.append(skill_id)
                continue
            body = skill.get("body") or ""
            if not body.strip():
                skipped_skills.append(skill_id)
                continue

            inserted_skills.append(skill_id)
            context_blocks.append(f"<!-- skill:{skill_id} -->\n{body.strip()}")

            if phase == "planning" and layer == "plan":
                io_contract = skill.get("io_contract")
                if io_contract:
                    contract_text = read_contract_file(str(io_contract))
                    if contract_text.strip():
                        inserted_manifests.append(str(io_contract))
                        context_blocks.append(f"<!-- io_contract:{io_contract} -->\n{contract_text.strip()}")

                extra = json_loads(skill.get("extra_json"), {})
                manifest_dir_rel = extra.get("manifest_dir")
                if manifest_dir_rel:
                    manifest_dir = PROJECT_ROOT / str(manifest_dir_rel)
                    for name, content in read_manifest_files(manifest_dir):
                        inserted_manifests.append(f"{manifest_dir_rel}/{name}")
                        context_blocks.append(f"<!-- manifest:{name} -->\n{content.strip()}")

        final_context = "\n\n---\n\n".join(context_blocks)
        return {
            "agent_name": agent_name,
            "phase": phase,
            "run_id": run_id,
            "inserted_skills": inserted_skills,
            "inserted_manifests": inserted_manifests,
            "skipped_skills": skipped_skills,
            "final_context": final_context,
        }
    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Assemble agent prompt context from selected skills.")
    parser.add_argument("--agent", required=True)
    parser.add_argument("--phase", required=True)
    parser.add_argument("--skills", required=True, help="Comma-separated skill IDs")
    parser.add_argument("--run-id")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    args = parser.parse_args()

    result = assemble_prompt(
        agent_name=args.agent,
        phase=args.phase,
        selected_skill_ids=[item.strip() for item in args.skills.split(",") if item.strip()],
        run_id=args.run_id,
        db_path=args.db,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
