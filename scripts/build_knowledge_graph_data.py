#!/usr/bin/env python3
"""Build visualization data from current KUs and the authoritative relation index."""

from __future__ import annotations

import json
import re
from datetime import date, datetime
from pathlib import Path

import yaml

try:
    from scripts._accepted_knowledge import select_paths, load_catalog
except ModuleNotFoundError:
    from _accepted_knowledge import select_paths, load_catalog


BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "05-outputs" / "knowledge-graph-data.json"
OUT_JS = BASE / "05-outputs" / "knowledge-graph-data.js"

TYPE_COLORS = {
    "person": "#3B82F6",
    "family": "#A16207",
    "institution": "#8B5CF6",
    "place": "#06B6D4",
    "work": "#F59E0B",
    "archive": "#6366F1",
    "term": "#10B981",
    "procedure": "#EC4899",
    "event": "#EF4444",
}
TYPE_ZH = {
    "person": "人物",
    "family": "家族",
    "institution": "机构",
    "place": "地点",
    "work": "作品",
    "archive": "文献与档案",
    "term": "术语",
    "procedure": "程序",
    "event": "事件",
}


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    try:
        frontmatter = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        frontmatter = {}
    return frontmatter if isinstance(frontmatter, dict) else {}, parts[2]


def safe_str(value, max_length: int = 200) -> str:
    if value is None:
        return ""
    return str(value).strip().strip("\"'")[:max_length]


def safe_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if item is not None]
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return []


def safe_topic_memberships(value) -> list[str | dict]:
    """Keep topic memberships compact while preserving an optional membership role."""
    if not isinstance(value, list):
        return []
    memberships: list[str | dict] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            memberships.append(item.strip())
        elif isinstance(item, dict):
            topic = safe_str(item.get("topic") or item.get("topic_id") or item.get("id"))
            if not topic:
                continue
            compact = {"topic": topic}
            role = safe_str(item.get("role"))
            if role:
                compact["role"] = role
            theme = safe_str(item.get("theme") or item.get("theme_id") or item.get("parent_theme"))
            if theme:
                compact["theme"] = theme
            memberships.append(compact)
    return memberships


def json_compatible(value):
    """Normalize YAML-native values before they cross the JSON boundary."""
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): json_compatible(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_compatible(item) for item in value]
    return value


def endpoint_node_id(value: str) -> str:
    normalized = value.replace("\\", "/").strip().strip("\"'")
    if "04-knowledge/units/" in normalized:
        normalized = normalized.split("04-knowledge/units/", 1)[1]
    normalized = normalized.lstrip("./")
    return normalized.removesuffix(".md").replace("/", ":")


def build_structure(base: Path) -> dict[str, list[dict]]:
    """Read actual structure nodes; missing parent levels are valid."""
    root = base / "04-knowledge" / "structure"
    folders = {
        "domains": "domain",
        "dimensions": "dimension",
        "themes": "theme",
        "topics": "topic",
    }
    structure: dict[str, list[dict]] = {key: [] for key in folders}
    for key, expected_type in folders.items():
        for path in select_paths(base, "structure", sorted((root / key).glob("*.md"))):
            if path.name.lower() == "readme.md":
                continue
            frontmatter, body = parse_frontmatter(path.read_text(encoding="utf-8"))
            if not frontmatter or safe_str(frontmatter.get("node_type")) != expected_type:
                continue
            code = safe_str(
                frontmatter.get(f"{expected_type}_code")
                or frontmatter.get("code")
                or path.stem
            )
            boundary_match = re.search(
                r"## (?:研究边界|核心主张)\r?\n(.*?)(?=\r?\n##|\Z)", body, re.DOTALL
            )
            structure[key].append(
                {
                    "id": path.stem,
                    "code": code,
                    "title": safe_str(frontmatter.get("title")),
                    "name_en": safe_str(frontmatter.get("name_en")),
                    "core_question": safe_str(frontmatter.get("core_question"), max_length=320),
                    "members": frontmatter.get("members") if isinstance(frontmatter.get("members"), list) else [],
                    "basis": safe_str(frontmatter.get("basis"), max_length=800),
                    "primary_domain": safe_str(frontmatter.get("primary_domain") or frontmatter.get("parent_domain")),
                    "primary_dimension": safe_str(frontmatter.get("primary_dimension") or frontmatter.get("dimension_code")),
                    "parent_theme": safe_str(frontmatter.get("parent_theme")),
                    "secondary_themes": safe_list(frontmatter.get("secondary_themes")),
                    "summary": boundary_match.group(1).strip()[:360] if boundary_match else "",
                    "path": path.relative_to(root).as_posix(),
                }
            )
    return structure


def build_graph(base: Path = BASE) -> dict:
    units = base / "04-knowledge" / "units"
    nodes: list[dict] = []
    node_ids: set[str] = set()
    structure = build_structure(base)

    for path in select_paths(base, "units", sorted(units.rglob("*.md"))):
        text = path.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(text)
        if not frontmatter:
            continue
        relative = path.relative_to(units).as_posix()
        node_id = endpoint_node_id(relative)
        unit_type = safe_str(frontmatter.get("type"))
        description_match = re.search(r"## (?:描述|定义)\r?\n(.*?)(?=\r?\n##|\Z)", body, re.DOTALL)
        nodes.append(
            {
                "id": node_id,
                "title": safe_str(frontmatter.get("title")),
                "name_en": safe_str(frontmatter.get("name_en")) or safe_str(frontmatter.get("title")),
                "type": unit_type,
                "type_zh": TYPE_ZH.get(unit_type, unit_type),
                "color": TYPE_COLORS.get(unit_type, "#9CA3AF"),
                "tags": safe_list(frontmatter.get("tags"))[:5],
                "confidence": safe_str(frontmatter.get("confidence")),
                "consensus": safe_str(frontmatter.get("consensus")),
                "sub_type": safe_str(frontmatter.get("sub_type")),
                "source_count": safe_str(frontmatter.get("source_count")),
                "evidence_status": safe_str(frontmatter.get("evidence_status")),
                "description": description_match.group(1).strip()[:200] if description_match else "",
                "path": relative,
                "sources": frontmatter.get("sources") if isinstance(frontmatter.get("sources"), list) else [],
                "primary_domain": safe_str(frontmatter.get("primary_domain")),
                "secondary_domains": safe_list(frontmatter.get("secondary_domains")),
                "primary_dimension": safe_str(frontmatter.get("primary_dimension")),
                "primary_theme": safe_str(frontmatter.get("primary_theme")),
                "secondary_themes": safe_list(frontmatter.get("secondary_themes")),
                "role_in_theme": safe_str(frontmatter.get("role_in_theme")),
                "topic_memberships": safe_topic_memberships(frontmatter.get("topic_memberships")),
                "hierarchy_scope_note": safe_str(frontmatter.get("hierarchy_scope_note"), max_length=400),
            }
        )
        node_ids.add(node_id)

    try:
        from scripts._relation_tables import load_relations
    except ModuleNotFoundError:
        from _relation_tables import load_relations
    relations = load_relations(base / "04-knowledge" / "tables" / "relations.csv")
    links = []
    for relation in relations:
        source = endpoint_node_id(str(relation.get("source", "")))
        target = endpoint_node_id(str(relation.get("target", "")))
        if source not in node_ids or target not in node_ids:
            continue
        links.append(
            {
                "source": source,
                "target": target,
                "relation_type": safe_str(relation.get("relation_type")),
                "relation_source": safe_str(relation.get("relation_source")),
                "review_status": safe_str(relation.get("review_status")),
                "confidence": safe_str(relation.get("confidence")),
                "evidence_ref": relation.get("evidence_ref") or {},
            }
        )

    by_type = {unit_type: 0 for unit_type in TYPE_COLORS}
    for node in nodes:
        by_type[node["type"]] = by_type.get(node["type"], 0) + 1
    hierarchy = {
        "domain_assigned": sum(bool(node["primary_domain"]) for node in nodes),
        "dimension_assigned": sum(bool(node["primary_dimension"]) for node in nodes),
        "theme_assigned": sum(bool(node["primary_theme"] or node["secondary_themes"]) for node in nodes),
        "topic_assigned": sum(bool(node["topic_memberships"]) for node in nodes),
    }
    return json_compatible({
        "nodes": nodes,
        "links": links,
        "structure": structure,
        "stats": {
            "total_nodes": len(nodes),
            "total_links": len(links),
            "relation_index_total": len(links) if load_catalog(base) is not None else len(relations),
            "skipped_non_unit_relations": 0 if load_catalog(base) is not None else len(relations) - len(links),
            "by_type": by_type,
            "hierarchy": hierarchy,
            "structure_nodes": {key: len(values) for key, values in structure.items()},
        },
    })


def render_data_script(data: dict) -> str:
    """Render a file:// compatible data payload for direct HTML opening."""
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return f"window.KNOWLEDGE_GRAPH_DATA={payload};\n"


def main() -> None:
    data = build_graph()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_JS.write_text(render_data_script(data), encoding="utf-8")
    print(f"Generated {OUT} and {OUT_JS}: {len(data['nodes'])} nodes, {len(data['links'])} links")
    for unit_type, count in sorted(data["stats"]["by_type"].items()):
        print(f"  {unit_type}: {count}")


if __name__ == "__main__":
    main()
