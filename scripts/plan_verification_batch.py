#!/usr/bin/env python3
"""Plan one deterministic high-value verification batch without changing knowledge.

The planner consumes the read-only confidence queue and current projections. It
selects only existing KUs that are both single-source and tentative, ranks them
by explicit risk signals and relation degree, assigns internal checkpoints, and
reports Topic coverage for later Agent selection.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
UNIT_PREFIX = "04-knowledge/units/"
UNIT_DIRS = {"persons", "families", "institutions", "places", "works", "archives", "terms", "procedures", "events"}


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"JSONL 第 {line_number} 行不是对象：{path}")
        rows.append(row)
    return rows


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def full_unit_path(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.replace("\\", "/").lstrip("./")
    if normalized.startswith(UNIT_PREFIX):
        relative = normalized.removeprefix(UNIT_PREFIX)
    else:
        relative = normalized
    first = relative.split("/", 1)[0]
    if first not in UNIT_DIRS or not relative.endswith(".md"):
        return None
    return f"{UNIT_PREFIX}{relative}"


def relation_degrees(path: Path) -> Counter[str]:
    rows = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    if not isinstance(rows, list):
        raise ValueError(f"relation index 不是列表：{path}")
    degrees: Counter[str] = Counter()
    for row in rows:
        if not isinstance(row, dict):
            continue
        for key in ("source", "target"):
            unit = full_unit_path(row.get(key))
            if unit:
                degrees[unit] += 1
    return degrees


def nested_unit_paths(value: object) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for nested in value.values():
            found.update(nested_unit_paths(nested))
    elif isinstance(value, list):
        for nested in value:
            found.update(nested_unit_paths(nested))
    else:
        unit = full_unit_path(value)
        if unit:
            found.add(unit)
    return found


def active_candidate_targets(path: Path) -> set[str]:
    targets: set[str] = set()
    for row in read_jsonl(path):
        if row.get("lifecycle_class") != "active":
            continue
        targets.update(nested_unit_paths(row.get("target_ref")))
        targets.update(nested_unit_paths(row.get("payload")))
    return targets


def eligible(row: dict) -> bool:
    reasons = set(row.get("reasons") or [])
    return {
        "single_source",
        "tentative_or_missing_consensus",
    }.issubset(reasons)


def rank_key(row: dict) -> tuple:
    return (
        0 if row.get("low_confidence") else 1,
        0 if row.get("active_candidate_linked") else 1,
        -int(row.get("relation_degree") or 0),
        0 if row.get("evidence_status") == "source_backed" else 1,
        str(row.get("unit") or ""),
    )


def select_targets(
    queue_rows: list[dict],
    degrees: Counter[str],
    active_targets: set[str],
    target_count: int,
    checkpoint_size: int,
    unit_types: set[str] | None = None,
) -> list[dict]:
    candidates: list[dict] = []
    for row in queue_rows:
        if not eligible(row):
            continue
        if unit_types and row.get("type") not in unit_types:
            continue
        unit = str(row.get("unit") or "")
        if not unit.startswith(UNIT_PREFIX):
            continue
        enriched = dict(row)
        enriched["relation_degree"] = degrees.get(unit, 0)
        enriched["active_candidate_linked"] = unit in active_targets
        enriched["low_confidence"] = row.get("confidence") in {None, "", "low"}
        selection_reasons = ["single_source", "tentative"]
        if enriched["low_confidence"]:
            selection_reasons.append("low_confidence")
        if enriched["active_candidate_linked"]:
            selection_reasons.append("active_candidate_linked")
        selection_reasons.append("relation_degree")
        enriched["selection_reasons"] = selection_reasons
        candidates.append(enriched)
    candidates.sort(key=rank_key)
    if len(candidates) < target_count:
        scope = f"且类型属于 {sorted(unit_types)}" if unit_types else ""
        raise ValueError(
            f"满足 single-source + tentative {scope} 的 KU 只有 {len(candidates)}，不足 {target_count}"
        )
    selected = candidates[:target_count]
    for index, row in enumerate(selected, start=1):
        row["rank"] = index
        row["checkpoint"] = ((index - 1) // checkpoint_size) + 1
    return selected


def topic_metadata(topic: str) -> dict:
    relative = topic.removeprefix("topics/")
    path = ROOT / "04-knowledge" / "structure" / "topics" / relative
    if not path.is_file():
        return {"title": Path(relative).stem, "primary_dimension": None, "parent_theme": None}
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    data = yaml.safe_load(match.group(1)) if match else {}
    if not isinstance(data, dict):
        data = {}
    return {
        "title": data.get("title") or path.stem,
        "primary_dimension": data.get("primary_dimension"),
        "parent_theme": data.get("parent_theme"),
    }


def topic_shortlist(graph_path: Path, selected: list[dict], limit: int = 12) -> list[dict]:
    graph = json.loads(graph_path.read_text(encoding="utf-8-sig"))
    nodes = graph.get("nodes") if isinstance(graph, dict) else None
    if not isinstance(nodes, list):
        raise ValueError(f"knowledge graph 缺少 nodes：{graph_path}")
    selected_units = {row["unit"] for row in selected}
    total: Counter[str] = Counter()
    selected_count: Counter[str] = Counter()
    for node in nodes:
        if not isinstance(node, dict):
            continue
        unit = full_unit_path(node.get("path"))
        memberships = node.get("topic_memberships") or []
        for membership in memberships:
            topic = membership.get("topic") if isinstance(membership, dict) else None
            if not isinstance(topic, str) or not topic.startswith("topics/"):
                continue
            total[topic] += 1
            if unit in selected_units:
                selected_count[topic] += 1
    rows = []
    for topic, count in selected_count.items():
        metadata = topic_metadata(topic)
        rows.append(
            {
                "topic": topic,
                **metadata,
                "selected_target_count": count,
                "total_member_count": total[topic],
            }
        )
    rows.sort(key=lambda row: (-row["selected_target_count"], -row["total_member_count"], row["topic"]))
    return rows[:limit]


def checkpoint_summary(selected: list[dict]) -> list[dict]:
    grouped: defaultdict[int, list[dict]] = defaultdict(list)
    for row in selected:
        grouped[int(row["checkpoint"])].append(row)
    return [
        {
            "checkpoint": checkpoint,
            "start_rank": rows[0]["rank"],
            "end_rank": rows[-1]["rank"],
            "target_count": len(rows),
        }
        for checkpoint, rows in sorted(grouped.items())
    ]


def build_plan(
    queue_path: Path,
    relation_index: Path,
    candidate_index: Path,
    graph_path: Path,
    target_count: int,
    checkpoint_size: int,
    unit_types: set[str] | None = None,
) -> dict:
    queue_rows = read_jsonl(queue_path)
    selected = select_targets(
        queue_rows,
        relation_degrees(relation_index),
        active_candidate_targets(candidate_index),
        target_count,
        checkpoint_size,
        unit_types,
    )
    return {
        "schema_version": "1.0",
        "plan_kind": "high_value_verification_batch",
        "criteria": {
            "required": ["single_source", "tentative"],
            "unit_types": sorted(unit_types) if unit_types else [],
            "ranking": ["low_confidence", "active_candidate_linked", "relation_degree", "source_backed_first"],
            "semantic_decision": "agent_required",
        },
        "target_count": len(selected),
        "checkpoint_size": checkpoint_size,
        "input_fingerprints": {
            queue_path.relative_to(ROOT).as_posix(): f"sha256:{sha256(queue_path)}",
            relation_index.relative_to(ROOT).as_posix(): f"sha256:{sha256(relation_index)}",
            candidate_index.relative_to(ROOT).as_posix(): f"sha256:{sha256(candidate_index)}",
            graph_path.relative_to(ROOT).as_posix(): f"sha256:{sha256(graph_path)}",
        },
        "checkpoints": checkpoint_summary(selected),
        "type_distribution": dict(sorted(Counter(row["type"] for row in selected).items())),
        "source_family_distribution": dict(sorted(Counter(row["source_family"] for row in selected).items())),
        "topic_shortlist": topic_shortlist(graph_path, selected),
        "targets": selected,
    }


def write_summary(plan: dict, output: Path) -> None:
    lines = [
        "# 高价值验证批次规划",
        "",
        f"- 目标：{plan['target_count']} 个 KU",
        f"- Checkpoint：{len(plan['checkpoints'])} 个，每个 {plan['checkpoint_size']} 个",
        "- 必须条件：同时为 `single_source` 与 `tentative`。",
        f"- 类型范围：{', '.join(plan['criteria']['unit_types']) or '全部 KU 类型'}。",
        "- 排序信号：低置信、活跃候选关联、关系度、source-backed 优先。",
        "- 语义边界：本规划器不收集证据、不裁决事实、不改变 KU 状态。",
        "",
        "## 类型分布",
        "",
        "| 类型 | 数量 |",
        "|---|---:|",
    ]
    for key, value in plan["type_distribution"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(["", "## Topic 候选", "", "| Topic | 维度 | 批次目标 | 全部成员 |", "|---|---|---:|---:|"])
    for row in plan["topic_shortlist"]:
        lines.append(
            f"| `{row['topic']}` | {row.get('primary_dimension') or '-'} | "
            f"{row['selected_target_count']} | {row['total_member_count']} |"
        )
    lines.extend(["", "## Checkpoint", "", "| Checkpoint | 排名范围 | 数量 |", "|---:|---:|---:|"])
    for row in plan["checkpoints"]:
        lines.append(f"| {row['checkpoint']} | {row['start_rank']}–{row['end_rank']} | {row['target_count']} |")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary-output", type=Path)
    parser.add_argument("--target-count", type=int, default=150)
    parser.add_argument("--checkpoint-size", type=int, default=50)
    parser.add_argument(
        "--unit-type",
        action="append",
        choices=sorted(UNIT_DIRS),
        dest="unit_types",
        help="只选择指定 KU 类型；可重复传入。",
    )
    parser.add_argument("--relation-index", type=Path, default=Path("04-knowledge/quality/relation-index.yml"))
    parser.add_argument("--candidate-index", type=Path, default=Path("06-runtime/state/candidate-index.jsonl"))
    parser.add_argument("--graph", type=Path, default=Path("05-outputs/knowledge-graph-data.json"))
    args = parser.parse_args()
    if not 120 <= args.target_count <= 180:
        parser.error("--target-count 必须在 120–180 之间")
    if not 40 <= args.checkpoint_size <= 50:
        parser.error("--checkpoint-size 必须在 40–50 之间")

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else ROOT / path

    queue = resolve(args.queue)
    output = resolve(args.output)
    summary_output = resolve(args.summary_output) if args.summary_output else None
    plan = build_plan(
        queue,
        resolve(args.relation_index),
        resolve(args.candidate_index),
        resolve(args.graph),
        args.target_count,
        args.checkpoint_size,
        set(args.unit_types) if args.unit_types else None,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if summary_output:
        write_summary(plan, summary_output)
    print(f"plan={output.relative_to(ROOT) if output.is_relative_to(ROOT) else output}")
    print(f"targets={plan['target_count']}")
    print(f"checkpoints={len(plan['checkpoints'])}")
    print(f"topic_shortlist={len(plan['topic_shortlist'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
