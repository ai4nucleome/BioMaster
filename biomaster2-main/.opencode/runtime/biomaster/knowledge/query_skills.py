from __future__ import annotations

from pathlib import Path
import argparse
import re

from biomaster.knowledge import (
    DEFAULT_DB_PATH,
    PROJECT_ROOT,
    connect,
    ensure_schema,
    json_loads,
    normalize_agent_name,
    row_to_dict,
)


def get_skill_by_id(connection, skill_id: str) -> dict | None:
    row = connection.execute(
        "SELECT * FROM skills WHERE skill_id = ?",
        (skill_id,),
    ).fetchone()
    return row_to_dict(row) if row else None


def list_skills(
    connection,
    *,
    layer: str | None = None,
    enabled_only: bool = True,
) -> list[dict]:
    query = "SELECT * FROM skills"
    clauses: list[str] = []
    params: list[object] = []
    if layer:
        clauses.append("layer = ?")
        params.append(layer)
    if enabled_only:
        clauses.append("enabled = 1")
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY priority DESC, skill_id ASC"
    return [row_to_dict(row) for row in connection.execute(query, params).fetchall()]


def list_skills_for_agent(
    connection,
    agent_name: str,
    *,
    layer: str | None = None,
    enabled_only: bool = True,
) -> list[dict]:
    agent = normalize_agent_name(agent_name)
    skills = list_skills(connection, layer=layer, enabled_only=enabled_only)
    return [skill for skill in skills if agent_allowed(skill, agent)]


def skill_haystack(skill: dict) -> str:
    return " ".join(
        [
            skill.get("skill_id") or "",
            skill.get("layer") or "",
            skill.get("domain") or "",
            skill.get("discipline") or "",
            skill.get("pipeline") or "",
            skill.get("tool") or "",
            skill.get("description") or "",
            skill.get("tags") or "",
            skill.get("body") or "",
        ]
    ).lower()


def search_skills(
    connection,
    query: str,
    *,
    layers: set[str] | None = None,
    agent_name: str | None = None,
    limit: int = 10,
) -> list[tuple[int, dict]]:
    tokens = [token for token in re.findall(r"[a-z0-9][a-z0-9-]*", query.lower()) if len(token) >= 2]
    normalized_query = query.lower().strip()
    scored: list[tuple[int, dict]] = []
    skills = list_skills(connection, enabled_only=True)
    if agent_name:
        agent = normalize_agent_name(agent_name)
        skills = [skill for skill in skills if agent_allowed(skill, agent)]

    for skill in skills:
        if layers and str(skill.get("layer") or "") not in layers:
            continue
        haystack = skill_haystack(skill)
        score = 0
        if normalized_query and normalized_query in haystack:
            score += 10
        for token in tokens:
            if token in haystack:
                score += 1
        if score:
            scored.append((score, skill))

    scored.sort(key=lambda item: (-item[0], item[1]["skill_id"]))
    return scored[:limit]


def agent_allowed(skill: dict, agent_name: str) -> bool:
    allowed = [item.strip() for item in str(skill.get("allowed_agents") or "").split(",") if item.strip()]
    return not allowed or agent_name in allowed


def record_agent_allowed(record: dict, agent_name: str) -> bool:
    return agent_allowed(record, agent_name)


def get_route(connection, route_id: str) -> dict | None:
    row = connection.execute(
        "SELECT * FROM pipeline_routes WHERE route_id = ?",
        (route_id,),
    ).fetchone()
    return row_to_dict(row) if row else None


def list_routes(connection, *, enabled_only: bool = True) -> list[dict]:
    query = "SELECT * FROM pipeline_routes"
    if enabled_only:
        query += " WHERE enabled = 1"
    query += " ORDER BY route_id ASC"
    return [row_to_dict(row) for row in connection.execute(query).fetchall()]


def route_skill_ids(route: dict, include_optional: bool = False) -> list[str]:
    required = json_loads(route.get("required_skill_ids"), [])
    optional = json_loads(route.get("optional_skill_ids"), []) if include_optional else []
    return list(dict.fromkeys([*required, *optional]))


def skills_for_route(
    connection,
    route_id: str,
    *,
    agent_name: str | None = None,
    include_optional: bool = False,
    enabled_only: bool = True,
) -> list[dict]:
    route = get_route(connection, route_id)
    if route is None:
        raise KeyError(f"unknown route: {route_id}")

    skills: list[dict] = []
    for skill_id in route_skill_ids(route, include_optional=include_optional):
        skill = get_skill_by_id(connection, skill_id)
        if skill is None:
            continue
        if enabled_only and not skill.get("enabled"):
            continue
        if agent_name and not agent_allowed(skill, normalize_agent_name(agent_name)):
            continue
        skills.append(skill)
    return skills


def search_routes(connection, query: str, *, limit: int = 5) -> list[tuple[int, dict]]:
    tokens = [token for token in re.findall(r"[a-z0-9][a-z0-9-]*", query.lower()) if len(token) >= 2]
    scored: list[tuple[int, dict]] = []
    normalized_query = query.lower().strip()

    for route in list_routes(connection):
        haystack = " ".join(
            [
                route["route_id"],
                route["domain"],
                route["discipline"],
                route["pipeline"],
                route["title"],
                route.get("description") or "",
                route.get("trigger_keywords") or "",
                route.get("preview_steps") or "",
            ]
        ).lower()
        score = 0
        if normalized_query and normalized_query in haystack:
            score += 10
        for token in tokens:
            if token in haystack:
                score += 1
        if score:
            scored.append((score, route))

    scored.sort(key=lambda item: (-item[0], item[1]["route_id"]))
    return scored[:limit]


def get_knowledge_record(connection, record_id: str) -> dict | None:
    row = connection.execute(
        "SELECT * FROM knowledge_records WHERE record_id = ?",
        (record_id,),
    ).fetchone()
    return row_to_dict(row) if row else None


def list_knowledge_records(
    connection,
    *,
    record_type: str | None = None,
    enabled_only: bool = True,
) -> list[dict]:
    query = "SELECT * FROM knowledge_records"
    clauses: list[str] = []
    params: list[object] = []
    if record_type:
        clauses.append("record_type = ?")
        params.append(record_type)
    if enabled_only:
        clauses.append("enabled = 1")
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY record_id ASC"
    return [row_to_dict(row) for row in connection.execute(query, params).fetchall()]


def list_knowledge_for_agent(
    connection,
    agent_name: str,
    *,
    record_type: str | None = None,
    enabled_only: bool = True,
) -> list[dict]:
    agent = normalize_agent_name(agent_name)
    records = list_knowledge_records(connection, record_type=record_type, enabled_only=enabled_only)
    return [record for record in records if record_agent_allowed(record, agent)]


def knowledge_haystack(record: dict) -> str:
    keywords = json_loads(record.get("keywords"), [])
    return " ".join(
        [
            record.get("record_id") or "",
            record.get("record_type") or "",
            record.get("title") or "",
            record.get("summary") or "",
            record.get("analysis_type") or "",
            record.get("tool") or "",
            record.get("canonical_skill_id") or "",
            " ".join(keywords) if isinstance(keywords, list) else str(keywords),
        ]
    ).lower()


def search_knowledge_records(
    connection,
    query: str,
    *,
    record_type: str | None = None,
    agent_name: str | None = None,
    limit: int = 10,
) -> list[tuple[int, dict]]:
    tokens = [token for token in re.findall(r"[a-z0-9][a-z0-9-]*", query.lower()) if len(token) >= 2]
    normalized_query = query.lower().strip()
    scored: list[tuple[int, dict]] = []

    records = list_knowledge_records(connection, record_type=record_type, enabled_only=True)
    if agent_name:
        agent = normalize_agent_name(agent_name)
        records = [record for record in records if record_agent_allowed(record, agent)]

    for record in records:
        haystack = knowledge_haystack(record)
        score = 0
        if normalized_query and normalized_query in haystack:
            score += 10
        for token in tokens:
            if token in haystack:
                score += 1
        if record.get("analysis_type") and str(record["analysis_type"]).lower() in normalized_query:
            score += 8
        if record.get("tool") and str(record["tool"]).lower() in normalized_query:
            score += 8
        if score:
            scored.append((score, record))

    scored.sort(key=lambda item: (-item[0], item[1]["record_id"]))
    return scored[:limit]


def read_knowledge_record(connection, record_id: str, project_root: Path | None = None) -> str:
    record = get_knowledge_record(connection, record_id)
    if record is None:
        raise KeyError(f"unknown knowledge record: {record_id}")
    content = record.get("content")
    if isinstance(content, str) and content.strip():
        return content
    path = Path(record["path"])
    if not path.is_absolute():
        root = project_root or PROJECT_ROOT
        path = root / path
    if not path.exists():
        raise FileNotFoundError(
            f"knowledge record content missing in SQLite and file not found: {record_id}"
        )
    return path.read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Query BioMaster SQLite skill control records.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--skill-id")
    parser.add_argument("--layer")
    parser.add_argument("--agent")
    parser.add_argument("--route-id")
    parser.add_argument("--search-routes")
    parser.add_argument("--list-skills", action="store_true")
    parser.add_argument("--list-routes", action="store_true")
    parser.add_argument("--list-workflows", action="store_true")
    parser.add_argument("--list-tasks", action="store_true")
    parser.add_argument("--record-id")
    parser.add_argument("--search-knowledge")
    parser.add_argument("--record-type")
    parser.add_argument("--show-record", action="store_true")
    args = parser.parse_args()

    connection = connect(args.db)
    try:
        ensure_schema(connection)

        if args.list_workflows:
            for record in list_knowledge_records(connection, record_type="workflow"):
                print(f"{record['record_id']}\t{record.get('analysis_type') or '-'}\t{record['title']}")
            return

        if args.list_tasks:
            for record in list_knowledge_records(connection, record_type="task"):
                print(f"{record['record_id']}\t{record.get('tool') or '-'}\t{record['title']}")
            return

        if args.search_knowledge:
            for score, record in search_knowledge_records(
                connection,
                args.search_knowledge,
                record_type=args.record_type,
                agent_name=args.agent,
            ):
                print(f"{score}\t{record['record_id']}\t{record['title']}")
            return

        if args.record_id:
            if args.show_record:
                print(read_knowledge_record(connection, args.record_id))
                return
            record = get_knowledge_record(connection, args.record_id)
            if record is None:
                raise SystemExit(f"unknown knowledge record: {args.record_id}")
            for key, value in record.items():
                print(f"{key}: {value}")
            return

        if args.list_routes:
            for route in list_routes(connection):
                print(f"{route['route_id']}\t{route['title']}")
            return

        if args.search_routes:
            for score, route in search_routes(connection, args.search_routes):
                print(f"{score}\t{route['route_id']}\t{route['title']}")
            return

        if args.route_id:
            for skill in skills_for_route(connection, args.route_id, agent_name=args.agent):
                print(f"{skill['skill_id']}\t{skill['layer']}\t{skill['description']}")
            return

        if args.skill_id:
            skill = get_skill_by_id(connection, args.skill_id)
            if skill is None:
                raise SystemExit(f"unknown skill: {args.skill_id}")
            for key, value in skill.items():
                print(f"{key}: {value}")
            return

        skills = (
            list_skills_for_agent(connection, args.agent, layer=args.layer)
            if args.agent
            else list_skills(connection, layer=args.layer)
        )
        if args.list_skills or args.layer or args.agent:
            for skill in skills:
                print(f"{skill['skill_id']}\t{skill['layer']}\t{skill['description']}")
            return

        parser.print_help()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
