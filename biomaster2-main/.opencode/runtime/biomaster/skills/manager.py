from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

from biomaster.knowledge import DEFAULT_BIOSKILLS_ROOT, DEFAULT_DB_PATH, OPENCODE_ROOT, connect, ensure_knowledge_db
from biomaster.knowledge.query_skills import list_skills, list_skills_for_agent, search_skills


def bioskill_names(root: Path = DEFAULT_BIOSKILLS_ROOT) -> list[str]:
    if not root.exists():
        return []
    return sorted(path.name for path in root.iterdir() if path.is_dir() and (path / "SKILL.md").exists())


def access_policy() -> dict[str, Any]:
    path = OPENCODE_ROOT / "bioskills-access.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def print_access() -> None:
    print(yaml.safe_dump(access_policy(), sort_keys=False, allow_unicode=True).strip())


def print_summary() -> None:
    readiness = ensure_knowledge_db(DEFAULT_DB_PATH)
    connection = connect(DEFAULT_DB_PATH)
    try:
        rows = list_skills(connection)
        counts: dict[str, int] = {}
        for row in rows:
            layer = str(row.get("layer") or "unknown")
            counts[layer] = counts.get(layer, 0) + 1
        print("BioMaster BioSkills catalog")
        print(f"- file-backed bioskills: {len(bioskill_names())}")
        print(f"- SQLite skills: {len(rows)}")
        print(f"- SQLite refreshed: {readiness.get('created_or_synced')}")
        for layer in sorted(counts):
            print(f"- {layer}: {counts[layer]}")
    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect BioMaster BioSkills and SQLite cache.")
    parser.add_argument("--summary", action="store_true", help="print BioSkills and SQLite layer counts")
    parser.add_argument("--show-access", action="store_true", help="print BioSkills role/layer access policy")
    parser.add_argument("--layer", help="list SQLite skills in a layer")
    parser.add_argument("--agent", help="restrict listing to skills accessible by this agent")
    parser.add_argument("--search", help="search SQLite skills by keyword")
    args = parser.parse_args()

    if args.show_access:
        print_access()
        return
    if args.summary or not any((args.layer, args.agent, args.search)):
        print_summary()
        return

    ensure_knowledge_db(DEFAULT_DB_PATH)
    connection = connect(DEFAULT_DB_PATH)
    try:
        if args.search:
            rows = [skill for _, skill in search_skills(connection, args.search, layers={args.layer} if args.layer else None, agent_name=args.agent)]
        elif args.agent:
            rows = list_skills_for_agent(connection, args.agent, layer=args.layer)
        else:
            rows = list_skills(connection, layer=args.layer)
        for row in rows:
            print(f"{row['skill_id']}\t{row['layer']}\t{row.get('description') or ''}")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
