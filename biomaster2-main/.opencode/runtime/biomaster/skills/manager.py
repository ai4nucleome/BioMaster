from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import re
from typing import Any, Iterable

import yaml

from biomaster.knowledge import DEFAULT_INTERNAL_SKILL_ROOT, DEFAULT_KNOWLEDGE_ROOT, DEFAULT_SKILL_ROOT, OPENCODE_ROOT, PROJECT_ROOT


BIOMASTER_SKILL_ROOT = PROJECT_ROOT
DEFAULT_ACCESS_POLICY = OPENCODE_ROOT / "agent_skill_access.yaml"
PLAN_REFERENCE_RE = re.compile(r"\b(?:exec|verify|debug|plan)-[a-z0-9]+(?:-[a-z0-9]+)*\b")


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    layer: str
    path: Path
    metadata: dict[str, str]
    body: str

    @property
    def canonical_name(self) -> str:
        return self.metadata.get("canonical", self.name)

    @property
    def status(self) -> str:
        return self.metadata.get("status", "active")

    @property
    def aliases(self) -> list[str]:
        raw = self.metadata.get("aliases", "")
        return [item.strip() for item in raw.split(",") if item.strip()]

    @property
    def relative_path(self) -> str:
        return self.path.relative_to(BIOMASTER_SKILL_ROOT).as_posix()

    def summary(self) -> dict[str, Any]:
        item: dict[str, Any] = {
            "name": self.name,
            "layer": self.layer,
            "path": self.relative_path,
            "description": self.description,
        }
        for key in (
            "domain",
            "analysis",
            "tool",
            "output",
            "failure",
            "source",
            "status",
            "canonical",
            "aliases",
            "origin_source",
            "origin_page",
        ):
            if key in self.metadata:
                item[key] = self.metadata[key]
        return item


@dataclass(frozen=True)
class KnowledgeRecord:
    record_id: str
    title: str
    summary: str
    keywords: list[str]
    path: Path
    metadata: dict[str, str]

    @property
    def relative_path(self) -> str:
        return self.path.relative_to(BIOMASTER_SKILL_ROOT).as_posix()

    def haystack(self) -> str:
        return " ".join(
            [
                self.record_id,
                self.title,
                self.summary,
                " ".join(self.keywords),
                " ".join(self.metadata.values()),
            ]
        ).lower()

    def summary_row(self) -> str:
        skill = self.metadata.get("canonical_plan_skill") or self.metadata.get("canonical_exec_skill", "")
        return f"{self.record_id}\t{skill}\t{self.title}"


def parse_skill_file(path: Path) -> Skill:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path} missing YAML frontmatter")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{path} invalid YAML frontmatter")

    frontmatter = yaml.safe_load(parts[1])
    if not isinstance(frontmatter, dict):
        raise ValueError(f"{path} frontmatter must be a mapping")

    metadata = frontmatter.get("metadata") or {}
    if not isinstance(metadata, dict):
        raise ValueError(f"{path} metadata must be a mapping")

    normalized_metadata = {str(key): str(value) for key, value in metadata.items()}
    name = frontmatter.get("name")
    description = frontmatter.get("description")
    if not isinstance(name, str) or not isinstance(description, str):
        raise ValueError(f"{path} missing string name or description")

    return Skill(
        name=name,
        description=description.strip(),
        layer=normalized_metadata.get("layer", ""),
        path=path,
        metadata=normalized_metadata,
        body=parts[2].lstrip(),
    )


def parse_knowledge_record(item: dict[str, Any], root: Path) -> KnowledgeRecord:
    if not isinstance(item, dict):
        raise ValueError("knowledge registry entries must be mappings")
    record_id = str(item.get("id", ""))
    path_value = item.get("path")
    if not record_id or not path_value:
        raise ValueError("knowledge registry entry missing id or path")
    path = BIOMASTER_SKILL_ROOT / str(path_value)
    keywords = item.get("keywords") or []
    if not isinstance(keywords, list):
        keywords = [str(keywords)]
    metadata = {
        str(key): str(value)
        for key, value in item.items()
        if key not in {"id", "title", "summary", "keywords", "path"}
    }
    return KnowledgeRecord(
        record_id=record_id,
        title=str(item.get("title", record_id)),
        summary=str(item.get("summary", "")),
        keywords=[str(keyword) for keyword in keywords],
        path=path,
        metadata=metadata,
    )


def extract_plan_references(text: str) -> set[str]:
    return set(PLAN_REFERENCE_RE.findall(text))


def query_tokens(query: str) -> list[str]:
    tokens: list[str] = []
    for token in re.findall(r"[a-z0-9][a-z0-9-]*", query.lower()):
        if len(token) < 2:
            continue
        tokens.append(token)
        normalized = token.replace("-", "")
        if normalized != token and len(normalized) >= 2:
            tokens.append(normalized)
    return list(dict.fromkeys(tokens))


def search_score(query: str, tokens: list[str], haystack: str) -> int:
    score = 0
    normalized_query = query.lower().strip()
    if normalized_query and normalized_query in haystack:
        score += 10
    if normalized_query:
        compact_query = normalized_query.replace("-", "")
        compact_haystack = haystack.replace("-", "")
        if compact_query != normalized_query and compact_query in compact_haystack:
            score += 8
    for token in tokens:
        if token in haystack:
            score += 1
        elif "-" in token and token.replace("-", "") in haystack.replace("-", ""):
            score += 1
    return score


def skill_search_score(query: str, tokens: list[str], skill: "Skill") -> int:
    haystack = " ".join(
        [
            skill.name,
            skill.canonical_name,
            skill.description,
            " ".join(skill.metadata.values()),
            " ".join(skill.aliases),
            skill.body[:4000],
        ]
    ).lower()
    score = search_score(query, tokens, haystack)
    if not score:
        return 0

    if skill.name == skill.canonical_name:
        score += 8
    if skill.status == "active":
        score += 4
    elif skill.status == "variant":
        score -= 3
    elif skill.status == "deprecated":
        score -= 8
    if skill.metadata.get("source", "manual") == "manual":
        score += 4
    if skill.layer == "registry":
        score -= 4
    return max(score, 1)


class SkillCatalog:
    def __init__(self, skills: Iterable[Skill]) -> None:
        self._skills = sorted(skills, key=lambda skill: skill.name)
        self._by_name = {skill.name: skill for skill in self._skills}
        if len(self._by_name) != len(self._skills):
            raise ValueError("duplicate skill names found")

    @classmethod
    def from_root(cls, skill_root: Path = DEFAULT_SKILL_ROOT) -> "SkillCatalog":
        if not skill_root.exists():
            raise ValueError(f"skill root does not exist: {skill_root}")

        skills = [
            parse_skill_file(skill_dir / "SKILL.md")
            for skill_dir in sorted(path for path in skill_root.iterdir() if path.is_dir())
            if (skill_dir / "SKILL.md").exists()
        ]
        return cls(skills)

    @classmethod
    def from_roots(cls, skill_roots: Iterable[Path]) -> "SkillCatalog":
        skills: list[Skill] = []
        for skill_root in skill_roots:
            if not skill_root.exists():
                continue
            skills.extend(
                parse_skill_file(skill_dir / "SKILL.md")
                for skill_dir in sorted(path for path in skill_root.iterdir() if path.is_dir())
                if (skill_dir / "SKILL.md").exists()
            )
        return cls(skills)

    def list(
        self,
        layer: str | None = None,
        **metadata_filters: str,
    ) -> list[Skill]:
        results = self._skills
        if layer is not None:
            results = [skill for skill in results if skill.layer == layer]
        for key, value in metadata_filters.items():
            results = [skill for skill in results if skill.metadata.get(key) == value]
        return results

    def get(self, name: str) -> Skill:
        try:
            return self._by_name[name]
        except KeyError as exc:
            raise KeyError(f"unknown skill: {name}") from exc

    def get_canonical(self, name: str) -> Skill:
        skill = self.get(name)
        canonical_name = skill.canonical_name
        return self._by_name.get(canonical_name, skill)

    def list_variants(self, canonical_name: str) -> list[Skill]:
        return [skill for skill in self._skills if skill.canonical_name == canonical_name and skill.name != canonical_name]

    def search(
        self,
        query: str,
        layer: str | None = None,
        limit: int = 10,
        canonical_only: bool = True,
    ) -> list[Skill]:
        tokens = query_tokens(query)
        candidates = self.list(layer=layer) if layer else self._skills
        scored: list[tuple[int, Skill]] = []

        for skill in candidates:
            score = skill_search_score(query, tokens, skill)
            if score:
                scored.append((score, skill))

        return self._rank_scored(scored, limit=limit, canonical_only=canonical_only)

    def resolve_for_plan_step(self, step: dict[str, Any]) -> dict[str, list[Skill]]:
        execute_names = _as_list(step.get("required_execute_skills"))
        verify_names = _as_list(step.get("required_verify_skills"))
        return {
            "execute": [self.get(name) for name in execute_names],
            "verify": [self.get(name) for name in verify_names],
        }

    def validate_references(self) -> list[str]:
        errors: list[str] = []
        for skill in self.list(layer="plan"):
            for ref in sorted(extract_plan_references(skill.body)):
                if ref not in self._by_name:
                    errors.append(f"{skill.name} references missing skill: {ref}")
        return errors

    def agent_summary(self, layer: str | None = None) -> list[dict[str, Any]]:
        return [skill.summary() for skill in self.list(layer=layer)]

    def layer_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for skill in self._skills:
            counts[skill.layer] = counts.get(skill.layer, 0) + 1
        return dict(sorted(counts.items()))

    def allowed_for_agent(self, agent_name: str, policy: "AgentSkillAccessPolicy") -> list[Skill]:
        allowed_layers = policy.allowed_layers(agent_name)
        return [skill for skill in self._skills if skill.layer in allowed_layers]

    def list_for_agent(
        self,
        agent_name: str,
        policy: "AgentSkillAccessPolicy",
        layer: str | None = None,
    ) -> list[Skill]:
        allowed_layers = policy.allowed_layers(agent_name)
        if layer is not None:
            if layer not in allowed_layers:
                return []
            allowed_layers = {layer}
        return [skill for skill in self._skills if skill.layer in allowed_layers]

    def search_for_agent(
        self,
        agent_name: str,
        policy: "AgentSkillAccessPolicy",
        query: str,
        layer: str | None = None,
        limit: int = 10,
        canonical_only: bool = True,
    ) -> list[Skill]:
        allowed_layers = policy.allowed_layers(agent_name)
        if layer is not None:
            if layer not in allowed_layers:
                return []
            allowed_layers = {layer}

        tokens = query_tokens(query)
        scored: list[tuple[int, Skill]] = []
        for skill in self._skills:
            if skill.layer not in allowed_layers:
                continue
            score = skill_search_score(query, tokens, skill)
            if score:
                scored.append((score, skill))

        return self._rank_scored(scored, limit=limit, canonical_only=canonical_only)

    def _rank_scored(
        self,
        scored: list[tuple[int, Skill]],
        limit: int,
        canonical_only: bool,
    ) -> list[Skill]:
        if not canonical_only:
            scored.sort(key=lambda item: (-item[0], item[1].name))
            return [skill for _, skill in scored[:limit]]

        by_canonical: dict[str, tuple[int, Skill]] = {}
        for score, skill in scored:
            canonical = self._by_name.get(skill.canonical_name, skill)
            existing = by_canonical.get(canonical.name)
            if existing is None or score > existing[0]:
                by_canonical[canonical.name] = (score, canonical)

        folded = list(by_canonical.values())
        folded.sort(key=lambda item: (-item[0], item[1].name))
        return [skill for _, skill in folded[:limit]]


class KnowledgeRegistry:
    def __init__(self, records: Iterable[KnowledgeRecord], kind: str) -> None:
        self.kind = kind
        self._records = sorted(records, key=lambda record: record.record_id)
        self._by_id = {record.record_id: record for record in self._records}
        if len(self._by_id) != len(self._records):
            raise ValueError(f"duplicate {kind} knowledge record ids found")

    @classmethod
    def from_file(cls, path: Path, key: str, kind: str) -> "KnowledgeRegistry":
        if not path.exists():
            return cls([], kind=kind)
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get(key), list):
            raise ValueError(f"{path} must contain a {key} list")
        return cls([parse_knowledge_record(item, path.parent) for item in data[key]], kind=kind)

    @classmethod
    def workflows(cls, root: Path = DEFAULT_KNOWLEDGE_ROOT) -> "KnowledgeRegistry":
        return cls.from_file(root / "workflows" / "registry.yaml", key="workflows", kind="workflow")

    @classmethod
    def tasks(cls, root: Path = DEFAULT_KNOWLEDGE_ROOT) -> "KnowledgeRegistry":
        return cls.from_file(root / "tasks" / "registry.yaml", key="tasks", kind="task")

    def list(self) -> list[KnowledgeRecord]:
        return list(self._records)

    def get(self, record_id: str) -> KnowledgeRecord:
        try:
            return self._by_id[record_id]
        except KeyError as exc:
            raise KeyError(f"unknown {self.kind} record: {record_id}") from exc


class AgentSkillAccessPolicy:
    def __init__(self, agents: dict[str, dict[str, Any]]) -> None:
        self._agents = agents

    @classmethod
    def from_file(cls, path: Path = DEFAULT_ACCESS_POLICY) -> "AgentSkillAccessPolicy":
        if not path.exists():
            raise ValueError(f"agent skill access policy does not exist: {path}")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("agents"), dict):
            raise ValueError(f"{path} must contain an agents mapping")
        return cls(data["agents"])

    def agent_names(self) -> list[str]:
        return sorted(self._agents)

    def allowed_layers(self, agent_name: str) -> set[str]:
        config = self._agent_config(agent_name)
        layers = config.get("allowed_layers") or []
        return {str(layer) for layer in layers}

    def denied_layers(self, agent_name: str) -> set[str]:
        config = self._agent_config(agent_name)
        layers = config.get("denied_layers") or []
        return {str(layer) for layer in layers}

    def validate(self, valid_layers: set[str]) -> list[str]:
        errors: list[str] = []
        for agent_name in self.agent_names():
            allowed = self.allowed_layers(agent_name)
            denied = self.denied_layers(agent_name)
            unknown = (allowed | denied) - valid_layers
            if unknown:
                errors.append(f"{agent_name} references unknown layers: {', '.join(sorted(unknown))}")
            overlap = allowed & denied
            if overlap:
                errors.append(f"{agent_name} both allows and denies layers: {', '.join(sorted(overlap))}")
            if not allowed:
                errors.append(f"{agent_name} has no allowed_layers")
        return errors

    def summary(self) -> list[dict[str, Any]]:
        items = []
        for agent_name in self.agent_names():
            config = self._agent_config(agent_name)
            items.append(
                {
                    "agent": agent_name,
                    "purpose": config.get("purpose", ""),
                    "allowed_layers": sorted(self.allowed_layers(agent_name)),
                    "denied_layers": sorted(self.denied_layers(agent_name)),
                }
            )
        return items

    def _agent_config(self, agent_name: str) -> dict[str, Any]:
        try:
            config = self._agents[agent_name]
        except KeyError as exc:
            raise KeyError(f"unknown agent in access policy: {agent_name}") from exc
        if not isinstance(config, dict):
            raise ValueError(f"invalid access policy entry for agent: {agent_name}")
        return config


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect BioMaster OpenCode skills.")
    parser.add_argument("--summary", action="store_true", help="print layer counts and reference status")
    parser.add_argument("--knowledge-summary", action="store_true", help="print active skill and numbered knowledge counts")
    parser.add_argument("--layer", help="list skills in a layer")
    parser.add_argument("--search", help="search skills by keyword")
    parser.add_argument("--agent", help="restrict listing or search to skills accessible by this agent")
    parser.add_argument("--show-access", action="store_true", help="print the agent skill access policy")
    parser.add_argument("--list-workflow-records", action="store_true", help="list numbered workflow knowledge records")
    parser.add_argument("--search-workflows", help="search numbered workflow knowledge records")
    parser.add_argument("--show-workflow", help="print one numbered workflow knowledge record")
    parser.add_argument("--list-task-records", action="store_true", help="list numbered task knowledge records")
    parser.add_argument("--search-tasks", help="search numbered task knowledge records")
    parser.add_argument("--show-task", help="print one numbered task knowledge record")
    args = parser.parse_args()

    catalog = SkillCatalog.from_roots([DEFAULT_SKILL_ROOT, DEFAULT_INTERNAL_SKILL_ROOT])
    policy = AgentSkillAccessPolicy.from_file()

    from biomaster.knowledge.store import KnowledgeStore

    store = KnowledgeStore()
    try:
        if args.knowledge_summary:
            print("BioMaster active skills")
            for layer, count in catalog.layer_counts().items():
                print(f"- {layer}: {count}")
            sqlite_summary = store.summary()
            print("BioMaster SQLite knowledge store")
            print(f"- workflow records: {sqlite_summary['workflow_records']}")
            print(f"- task records: {sqlite_summary['task_records']}")
            print(f"- pipeline routes: {sqlite_summary['pipeline_routes']}")
            return

        if args.list_workflow_records:
            for record in store.list_records(record_type="workflow"):
                print(store.record_summary_row(record))
            return

        if args.search_workflows:
            for record in store.search_records(args.search_workflows, record_type="workflow"):
                print(store.record_summary_row(record))
            return

        if args.show_workflow:
            print(store.read_record_content(args.show_workflow))
            return

        if args.list_task_records:
            for record in store.list_records(record_type="task"):
                print(store.record_summary_row(record))
            return

        if args.search_tasks:
            for record in store.search_records(args.search_tasks, record_type="task"):
                print(store.record_summary_row(record))
            return

        if args.show_task:
            print(store.read_record_content(args.show_task))
            return
    finally:
        store.close()

    if args.show_access:
        for item in policy.summary():
            print(f"{item['agent']}\tallow={','.join(item['allowed_layers'])}\tdeny={','.join(item['denied_layers'])}")
        errors = policy.validate(set(catalog.layer_counts()))
        if errors:
            print("Access policy errors:")
            for error in errors:
                print(f"- {error}")
            raise SystemExit(1)
        return

    if args.search:
        skills = (
            catalog.search_for_agent(
                args.agent,
                policy,
                args.search,
                layer=args.layer,
                canonical_only=True,
            )
            if args.agent
            else catalog.search(args.search, layer=args.layer, canonical_only=True)
        )
        for skill in skills:
            print(f"{skill.name}\t{skill.layer}\t{skill.description}")
        return

    if args.layer:
        skills = (
            catalog.list_for_agent(args.agent, policy, layer=args.layer)
            if args.agent
            else catalog.list(layer=args.layer)
        )
        for skill in skills:
            print(f"{skill.name}\t{skill.description}")
        return

    if args.agent:
        for skill in catalog.list_for_agent(args.agent, policy):
            print(f"{skill.name}\t{skill.layer}\t{skill.description}")
        return

    if args.summary:
        print("BioMaster skill catalog")
        for layer, count in catalog.layer_counts().items():
            print(f"- {layer}: {count}")
        errors = catalog.validate_references()
        if errors:
            print("Reference errors:")
            for error in errors:
                print(f"- {error}")
            raise SystemExit(1)
        print("Reference check: passed")
        access_errors = policy.validate(set(catalog.layer_counts()))
        if access_errors:
            print("Access policy errors:")
            for error in access_errors:
                print(f"- {error}")
            raise SystemExit(1)
        print("Access policy check: passed")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
