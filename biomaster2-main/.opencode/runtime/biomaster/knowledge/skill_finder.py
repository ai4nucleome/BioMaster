from __future__ import annotations

from pathlib import Path
import argparse
import json
from datetime import datetime, timezone

from biomaster.knowledge import (
    DEFAULT_DB_PATH,
    connect,
    ensure_schema,
    json_dumps,
    normalize_agent_name,
)
from biomaster.knowledge.query_skills import (
    agent_allowed,
    get_skill_by_id,
    route_skill_ids,
    search_knowledge_records,
    search_routes,
    search_skills,
)
from biomaster.knowledge.phases import PHASE_ALLOWED_LAYERS, default_skills_for_phase, filter_core_skills
from biomaster.knowledge.state_manager import get_disabled_skill_ids, update_run


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


PLAN_AGENTS = {"biomaster-intake", "biomaster-plan"}
EXECUTE_AGENTS = {"biomaster-execute", "biomaster-debug", "biomaster-check"}
CHECK_AGENTS = {"biomaster-check"}

PHASE_SEARCH_LAYERS: dict[str, set[str]] = {
    "planning": {"plan", "report"},
    "preflight": {"execute", "env", "verify"},
    "execution": {"execute", "env", "verify"},
    "checking": {"verify"},
    "debugging": {"debug", "env", "execute", "verify", "report"},
    "reporting": {"report", "verify"},
}


def choose_best_route(scored_routes: list[tuple[int, dict]], user_request: str) -> dict | None:
    if not scored_routes:
        return None
    return scored_routes[0][1]


def knowledge_record_type_for_agent(agent_name: str) -> str | None:
    agent = normalize_agent_name(agent_name)
    if agent in PLAN_AGENTS:
        return "workflow"
    if agent in EXECUTE_AGENTS:
        return "task"
    return None


def filter_skill_ids(
    connection,
    skill_ids: list[str],
    *,
    agent_name: str,
    disabled_skill_ids: set[str],
    phase: str | None = None,
) -> tuple[list[str], list[str]]:
    selected: list[str] = []
    rejected: list[str] = []
    agent = normalize_agent_name(agent_name)
    allowed_layers = PHASE_ALLOWED_LAYERS.get(phase or "", set())

    for skill_id in skill_ids:
        if skill_id in disabled_skill_ids:
            rejected.append(skill_id)
            continue
        skill = get_skill_by_id(connection, skill_id)
        if skill is None:
            rejected.append(skill_id)
            continue
        if not skill.get("enabled"):
            rejected.append(skill_id)
            continue
        if not agent_allowed(skill, agent):
            rejected.append(skill_id)
            continue
        layer = str(skill.get("layer") or "")
        if allowed_layers and layer and layer not in allowed_layers:
            rejected.append(skill_id)
            continue
        selected.append(skill_id)

    return selected, rejected


def merge_skill_candidates(*groups: list[str]) -> list[str]:
    merged: list[str] = []
    for group in groups:
        for skill_id in group:
            if skill_id not in merged:
                merged.append(skill_id)
    return merged


def build_reason(
    route: dict | None,
    selected: list[str],
    rejected: list[str],
    user_request: str,
    workflow_records: list[str],
    task_records: list[str],
) -> str:
    if route and selected:
        return (
            f"Selected route '{route['route_id']}' with {len(workflow_records)} workflow records "
            f"and {len(task_records)} task records for: {user_request.strip()}"
        )
    if workflow_records or task_records:
        return (
            f"Matched {len(workflow_records)} workflow records and {len(task_records)} task records "
            f"from numbered knowledge for: {user_request.strip()}"
        )
    if route is None:
        return f"No pipeline route or numbered knowledge record matched the request: {user_request.strip()}"
    return f"Route '{route['route_id']}' matched, but no required skills passed agent and enabled filters."


def find_skills(
    user_request: str,
    agent_name: str,
    phase: str,
    *,
    run_id: str | None = None,
    db_path: Path = DEFAULT_DB_PATH,
    include_optional: bool = False,
    include_knowledge_records: bool = False,
    log_selection: bool = True,
    knowledge_limit: int = 5,
    save_run_state: bool = False,
) -> dict[str, object]:
    connection = connect(db_path)
    try:
        ensure_schema(connection)
        disabled = get_disabled_skill_ids(connection, run_id) if run_id else set()
        agent = normalize_agent_name(agent_name)

        scored_routes = search_routes(connection, user_request, limit=5)
        selected_route = choose_best_route(scored_routes, user_request)
        if phase == "planning" and selected_route is None:
            raise ValueError(
                "planning requires a SQLite pipeline_routes match before PLAN.yaml can be generated"
            )

        route_skill_candidates: list[str] = []
        if selected_route:
            route_skill_candidates = route_skill_ids(selected_route, include_optional=include_optional)

        record_type = knowledge_record_type_for_agent(agent) if include_knowledge_records else None
        knowledge_hits = (
            search_knowledge_records(
                connection,
                user_request,
                record_type=record_type,
                agent_name=agent,
                limit=knowledge_limit,
            )
            if record_type
            else []
        )
        selected_workflow_record_ids = [
            record["record_id"]
            for _, record in knowledge_hits
            if record.get("record_type") == "workflow"
        ]
        selected_task_record_ids = [
            record["record_id"]
            for _, record in knowledge_hits
            if record.get("record_type") == "task"
        ]

        knowledge_skill_candidates = [
            record["canonical_skill_id"]
            for _, record in knowledge_hits
            if record.get("canonical_skill_id")
        ]
        searched_skill_candidates = [
            skill["skill_id"]
            for _, skill in search_skills(
                connection,
                user_request,
                layers=PHASE_SEARCH_LAYERS.get(phase),
                agent_name=agent,
                limit=8,
            )
        ]
        candidate_skill_ids = merge_skill_candidates(
            route_skill_candidates,
            knowledge_skill_candidates,
            searched_skill_candidates,
        )
        if not candidate_skill_ids:
            candidate_skill_ids = default_skills_for_phase(phase)
        candidate_skill_ids = filter_core_skills(phase, candidate_skill_ids)
        if not candidate_skill_ids:
            candidate_skill_ids = default_skills_for_phase(phase)

        selected_skill_ids, rejected_skill_ids = filter_skill_ids(
            connection,
            candidate_skill_ids,
            agent_name=agent_name,
            disabled_skill_ids=disabled,
            phase=phase,
        )

        result = {
            "selected_route_id": selected_route["route_id"] if selected_route else None,
            "sqlite_route_search": True,
            "route_candidates": [
                {"score": score, "route_id": route["route_id"], "title": route["title"]}
                for score, route in scored_routes
            ],
            "selected_skill_ids": selected_skill_ids,
            "rejected_skill_ids": rejected_skill_ids,
            "candidate_skill_ids": candidate_skill_ids,
            "searched_skill_ids": searched_skill_candidates,
            "selected_workflow_record_ids": selected_workflow_record_ids,
            "selected_task_record_ids": selected_task_record_ids,
            "reason": build_reason(
                selected_route,
                selected_skill_ids,
                rejected_skill_ids,
                user_request,
                selected_workflow_record_ids,
                selected_task_record_ids,
            ),
            "agent_name": agent,
            "phase": phase,
            "run_id": run_id,
        }

        if save_run_state:
            if not run_id:
                raise ValueError("--save-run-state requires --run-id")
            if not selected_route:
                raise ValueError("cannot save run state without a SQLite selected_route_id")
            update_run(
                connection,
                run_id,
                selected_route_id=selected_route["route_id"],
                selected_skill_ids=selected_skill_ids,
                state_json={
                    "sqlite_route_search": True,
                    "route_candidates": result["route_candidates"],
                    "skill_finder_phase": phase,
                },
            )

        if log_selection:
            connection.execute(
                """
                INSERT INTO skill_selection_logs (
                  run_id, agent_name, phase, user_request,
                  candidate_skill_ids, selected_skill_ids, rejected_skill_ids, reason, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    agent,
                    phase,
                    user_request,
                    json_dumps(
                        {
                            "skills": candidate_skill_ids,
                            "workflow_records": selected_workflow_record_ids,
                            "task_records": selected_task_record_ids,
                        }
                    ),
                    json_dumps(selected_skill_ids),
                    json_dumps(rejected_skill_ids),
                    result["reason"],
                    utc_now(),
                ),
            )
            connection.commit()

        return result
    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Agentic skill finder with SQLite hard filters.")
    parser.add_argument("user_request")
    parser.add_argument("--agent", required=True)
    parser.add_argument("--phase", default="planning")
    parser.add_argument("--run-id")
    parser.add_argument("--include-optional", action="store_true")
    parser.add_argument("--save-run-state", action="store_true")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    args = parser.parse_args()

    result = find_skills(
        args.user_request,
        args.agent,
        args.phase,
        run_id=args.run_id,
        db_path=args.db,
        include_optional=args.include_optional,
        save_run_state=args.save_run_state,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
