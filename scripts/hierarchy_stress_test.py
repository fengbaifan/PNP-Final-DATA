#!/usr/bin/env python3
"""五级知识层级压力测试。

检查 Domain -> Dimension -> Theme -> Topic -> KU 的机械完整性与分布信号。
Cluster 是跨层发现候选，不在这里计作结构节点或自动生成层级归属。
"""

from __future__ import annotations

try:
    from scripts._relation_tables import load_relations
except ModuleNotFoundError:
    from _relation_tables import load_relations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
UNITS = ROOT / "04-knowledge" / "units"
HIERARCHY = ROOT / "04-knowledge" / "structure" / "hierarchy"
THEMES = ROOT / "04-knowledge" / "structure" / "themes"
TOPICS = ROOT / "04-knowledge" / "structure" / "topics"
RELATION_INDEX = ROOT / "04-knowledge" / "tables" / "relations.csv"
HIERARCHY_FIELDS = ("primary_domain", "primary_dimension", "primary_theme", "topic_memberships")
FRONTMATTER_RE = re.compile(r"\A(?:\ufeff)?---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9'-]{2,}|[\u4e00-\u9fff]{2,}")
UNIT_LINK_RE = re.compile(r"\.\./\.\./units/([A-Za-z0-9_./-]+\.md)")
UNIT_DIRS = ("persons", "families", "institutions", "places", "works", "archives", "terms", "procedures", "events")
ALLOWED_ROLES = {
    "term_anchor",
    "representative_work",
    "key_person",
    "key_institution",
    "geographical_context",
    "source_archive",
    "procedure",
    "evidence_event",
    "historical_context",
    "counterexample",
    "boundary_case",
    "supporting_source",
    "contested_claim",
}
DEFAULT_ROLE_BY_TYPE = {
    "person": "key_person",
    "institution": "key_institution",
    "place": "geographical_context",
    "work": "representative_work",
    "archive": "source_archive",
    "term": "term_anchor",
    "procedure": "procedure",
    "event": "evidence_event",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def frontmatter_data(path: Path) -> dict:
    match = FRONTMATTER_RE.match(read_text(path))
    if not match:
        return {}
    try:
        data = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def repo_path(path: Path, root: Path = ROOT) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def aggregate_path_state(paths: list[Path], root: Path = ROOT) -> dict:
    """Return a compact, deterministic digest for a complete scanned path set."""
    digest = hashlib.sha256()
    total_bytes = 0
    for path in sorted(paths, key=lambda item: repo_path(item, root)):
        relative = repo_path(path, root)
        file_hash = sha256_path(path)
        total_bytes += path.stat().st_size
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("ascii"))
        digest.update(b"\n")
    return {
        "algorithm": "sha256(relative_path\\0sha256(file)\\n)",
        "file_count": len(paths),
        "total_bytes": total_bytes,
        "sha256": digest.hexdigest().upper(),
    }


def unit_key(path: Path, units: Path = UNITS) -> str:
    return path.relative_to(units).as_posix()


def _evidence_refs(data: dict, doc_id: str | None = None) -> list[dict]:
    """Return direct KU source references, never relation-evidence provenance."""
    refs: list[dict] = []
    sources = data.get("sources") or []
    if not isinstance(sources, list):
        return refs
    for item in sources:
        if not isinstance(item, dict):
            continue
        evidence_ref = item.get("evidence_ref") or {}
        if not isinstance(evidence_ref, dict):
            continue
        current_doc_id = str(evidence_ref.get("doc_id") or "").strip()
        source_file = str(evidence_ref.get("source_file") or "").strip()
        if (
            not current_doc_id
            or not source_file
            or (doc_id is not None and current_doc_id != doc_id)
        ):
            continue
        ref = {
            "doc_id": current_doc_id,
            "chapter_id": str(evidence_ref.get("chapter_id") or "").strip() or None,
            "source_file": source_file,
        }
        if ref not in refs:
            refs.append(ref)
    return refs


def _membership_topics(data: dict) -> set[str]:
    results: set[str] = set()
    for membership in data.get("topic_memberships") or []:
        if not isinstance(membership, dict):
            continue
        topic = str(membership.get("topic") or "").strip()
        role = str(membership.get("role") or "").strip()
        if topic and role:
            results.add(topic if topic.startswith("topics/") else f"topics/{Path(topic).name}")
    return results


def _tokens(data: dict, text: str) -> set[str]:
    values = [str(data.get("title") or ""), str(data.get("name_en") or "")]
    values.extend(str(tag) for tag in data.get("tags") or [])
    values.append(text)
    return {token.casefold() for token in TOKEN_RE.findall(" ".join(values))}


def load_relation_adjacency(path: Path = RELATION_INDEX) -> dict[str, set[str]]:
    """Load formal unit-neighbor edges; weak associations are absent from this index."""
    adjacency: defaultdict[str, set[str]] = defaultdict(set)
    if not path.exists():
        return adjacency
    data = load_relations(path)
    if isinstance(data, dict):
        data = data.get("relations") or []
    prefixes = tuple(f"{name}/" for name in UNIT_DIRS)
    for row in data:
        if not isinstance(row, dict):
            continue
        source = str(row.get("source") or "").strip()
        target = str(row.get("target") or "").strip()
        source_is_unit = source.startswith(prefixes)
        target_is_unit = target.startswith(prefixes)
        source_is_topic = source.startswith("structure/topics/")
        target_is_topic = target.startswith("structure/topics/")
        if source_is_unit and (target_is_unit or target_is_topic):
            adjacency[source].add(target)
        if target_is_unit and (source_is_unit or source_is_topic):
            adjacency[target].add(source)
    return adjacency


def build_topic_recall_index(
    units: Path = UNITS,
    topics: Path = TOPICS,
    relation_index: Path = RELATION_INDEX,
) -> dict:
    """Build mechanical recall signals without approving any Topic membership."""
    member_topics: defaultdict[str, set[str]] = defaultdict(set)
    chapter_topics: defaultdict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    unit_paths = sorted(units.glob("*/*.md")) if units.exists() else []
    for path in unit_paths:
        key = unit_key(path, units)
        data = frontmatter_data(path)
        memberships = _membership_topics(data)
        member_topics[key].update(memberships)
        for ref in _evidence_refs(data):
            chapter = ref.get("chapter_id")
            if chapter:
                for topic in memberships:
                    chapter_topics[(ref["doc_id"], chapter)][topic] += 1

    topic_data: dict[str, dict] = {}
    topic_tokens: dict[str, set[str]] = {}
    topic_tags: dict[str, set[str]] = {}
    if topics.exists():
        for path in sorted(topics.glob("*.md")):
            if path.name.lower() == "readme.md":
                continue
            ref = f"topics/{path.name}"
            data = frontmatter_data(path)
            text = read_text(path)
            topic_data[ref] = data
            topic_tokens[ref] = _tokens(data, text)
            topic_tags[ref] = {str(tag).casefold() for tag in data.get("tags") or []}

    return {
        "member_topics": member_topics,
        "chapter_topics": chapter_topics,
        "topic_data": topic_data,
        "topic_tokens": topic_tokens,
        "topic_tags": topic_tags,
        "adjacency": load_relation_adjacency(relation_index),
    }


def recall_topics_for_unit(
    *,
    key: str,
    data: dict,
    text: str,
    source_doc_id: str,
    index: dict,
    limit: int,
) -> list[dict]:
    """Rank recall signals only; scores are not semantic decisions."""
    signals: defaultdict[str, dict] = defaultdict(
        lambda: {
            "direct_topic_relation": False,
            "relation_neighbors": set(),
            "shared_source_chapters": Counter(),
            "shared_tags": set(),
            "shared_tokens": set(),
        }
    )
    for neighbor in sorted(index["adjacency"].get(key, set())):
        if neighbor.startswith("structure/topics/"):
            signals[f"topics/{Path(neighbor).name}"]["direct_topic_relation"] = True
        for topic in index["member_topics"].get(neighbor, set()):
            signals[topic]["relation_neighbors"].add(neighbor)

    for ref in _evidence_refs(data, source_doc_id):
        chapter = ref.get("chapter_id")
        if not chapter:
            continue
        for topic, count in index["chapter_topics"].get((source_doc_id, chapter), {}).items():
            signals[topic]["shared_source_chapters"][chapter] += count

    unit_tags = {str(tag).casefold() for tag in data.get("tags") or []}
    unit_tokens = _tokens(data, text)
    for topic in index["topic_data"]:
        shared_tags = unit_tags & index["topic_tags"][topic]
        shared_tokens = unit_tokens & index["topic_tokens"][topic]
        if shared_tags:
            signals[topic]["shared_tags"].update(shared_tags)
        if shared_tokens:
            signals[topic]["shared_tokens"].update(shared_tokens)

    ranked: list[dict] = []
    for topic, basis in signals.items():
        if topic not in index["topic_data"]:
            continue
        neighbor_count = len(basis["relation_neighbors"])
        chapter_count = sum(basis["shared_source_chapters"].values())
        score = (
            (80 if basis["direct_topic_relation"] else 0)
            + min(neighbor_count * 20, 60)
            + min(chapter_count * 6, 36)
            + min(len(basis["shared_tags"]) * 8, 24)
            + min(len(basis["shared_tokens"]), 12)
        )
        if score <= 0:
            continue
        ranked.append(
            {
                "topic": topic,
                "score": score,
                "basis": {
                    "direct_topic_relation": basis["direct_topic_relation"],
                    "relation_neighbors": sorted(basis["relation_neighbors"]),
                    "shared_source_chapters": dict(sorted(basis["shared_source_chapters"].items())),
                    "shared_tags": sorted(basis["shared_tags"]),
                    "shared_tokens": sorted(basis["shared_tokens"])[:12],
                },
            }
        )
    return sorted(ranked, key=lambda row: (-row["score"], row["topic"]))[:limit]


def build_source_hierarchy_review_records(
    *,
    source_doc_id: str,
    review_date: str,
    unit_type_filter: str | None = None,
    checkpoint_size: int = 45,
    recall_limit: int = 5,
    units: Path = UNITS,
    topics: Path = TOPICS,
    relation_index: Path = RELATION_INDEX,
    root: Path = ROOT,
) -> list[dict]:
    if checkpoint_size < 1:
        raise ValueError("checkpoint_size must be positive")
    if recall_limit < 1:
        raise ValueError("recall_limit must be positive")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", review_date):
        raise ValueError("review_date must use YYYY-MM-DD")
    if unit_type_filter is not None:
        unit_type_filter = unit_type_filter.strip().lower()
        if unit_type_filter not in DEFAULT_ROLE_BY_TYPE:
            raise ValueError(f"unsupported unit_type_filter: {unit_type_filter}")

    incomplete_by_path = {
        record["unit"]: record
        for record in find_missing_hierarchy_fields(units, root=root)
    }
    selected: list[tuple[tuple, Path, dict, list[dict]]] = []
    for path in sorted(units.glob("*/*.md")):
        relative = repo_path(path, root)
        if relative not in incomplete_by_path:
            continue
        data = frontmatter_data(path)
        refs = _evidence_refs(data, source_doc_id)
        if not refs:
            continue
        chapters = sorted({ref["chapter_id"] for ref in refs if ref.get("chapter_id")})
        unit_type = str(data.get("type") or ("family" if path.parent.name == "families" else path.parent.name.rstrip("s"))).strip()
        if unit_type_filter is not None and unit_type != unit_type_filter:
            continue
        sub_type = str(data.get("sub_type") or "<none>").strip()
        cluster_key = (unit_type, sub_type, "+".join(chapters) or "<no-chapter>", path.name)
        selected.append((cluster_key, path, data, refs))

    recall_index = build_topic_recall_index(units, topics, relation_index)
    records: list[dict] = []
    for position, (_, path, data, refs) in enumerate(sorted(selected, key=lambda row: row[0]), 1):
        relative = repo_path(path, root)
        key = unit_key(path, units)
        chapters = sorted({ref["chapter_id"] for ref in refs if ref.get("chapter_id")})
        unit_type = str(data.get("type") or ("family" if path.parent.name == "families" else path.parent.name.rstrip("s"))).strip()
        sub_type = str(data.get("sub_type") or "<none>").strip()
        candidates = recall_topics_for_unit(
            key=key,
            data=data,
            text=read_text(path),
            source_doc_id=source_doc_id,
            index=recall_index,
            limit=recall_limit,
        )
        records.append(
            {
                "candidate_id": f"hierarchy:{source_doc_id}:{key}",
                "origin_type": "source",
                "origin_ref": source_doc_id,
                "candidate_type": "hierarchy_change",
                "target_ref": relative,
                "payload": {
                    "title": data.get("title"),
                    "unit_type": unit_type,
                    "sub_type": sub_type,
                    "missing_fields": incomplete_by_path[relative]["missing_fields"],
                    "cluster": {
                        "source_doc_id": source_doc_id,
                        "unit_type": unit_type,
                        "sub_type": sub_type,
                        "chapter_ids": chapters,
                    },
                    "checkpoint": f"checkpoint-{((position - 1) // checkpoint_size) + 1:02d}",
                    "candidate_topics": candidates,
                    "recall_status": "candidates_recalled" if candidates else "no_recall_signal",
                    "unit_sha256": sha256_path(path),
                },
                "evidence_refs": refs,
                "state": "ready_for_review",
                "decision": {
                    "status": "pending",
                    "reason": None,
                    "decided_by": None,
                    "decided_at": None,
                },
                "apply_permitted": False,
                "created_at": review_date,
                "updated_at": review_date,
            }
        )
    return records


def write_source_hierarchy_review_queue(
    *,
    output: Path,
    manifest_output: Path,
    source_doc_id: str,
    review_date: str,
    unit_type_filter: str | None = None,
    checkpoint_size: int = 45,
    recall_limit: int = 5,
    units: Path = UNITS,
    topics: Path = TOPICS,
    relation_index: Path = RELATION_INDEX,
    root: Path = ROOT,
    generator_path: Path | None = None,
) -> int:
    """Write a reproducible, candidate-only review queue and provenance manifest."""
    for path in (output, manifest_output):
        if path.exists():
            raise FileExistsError(f"queue output already exists: {path}")
    records = build_source_hierarchy_review_records(
        source_doc_id=source_doc_id,
        review_date=review_date,
        unit_type_filter=unit_type_filter,
        checkpoint_size=checkpoint_size,
        recall_limit=recall_limit,
        units=units,
        topics=topics,
        relation_index=relation_index,
        root=root,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
        newline="\n",
    )
    generator_path = Path(__file__) if generator_path is None else generator_path
    all_unit_paths = sorted(units.glob("*/*.md"))
    all_topic_paths = sorted(path for path in topics.glob("*.md") if path.name.lower() != "readme.md")
    manifest = {
        "schema_version": 1,
        "artifact_role": "hierarchy_review_queue_reproducibility_manifest",
        "generator": {
            "path": repo_path(generator_path, root),
            "sha256": sha256_path(generator_path),
        },
        "invocation": {
            "source_doc_id": source_doc_id,
            "review_date": review_date,
            "unit_type_filter": unit_type_filter,
            "checkpoint_size": checkpoint_size,
            "recall_limit": recall_limit,
            "rebuild_command": [
                "python",
                repo_path(generator_path, root),
                "--queue-output",
                "{queue_output}",
                "--generation-manifest",
                "{manifest_output}",
                "--source-doc-id",
                source_doc_id,
                "--review-date",
                review_date,
                *(["--unit-type", unit_type_filter] if unit_type_filter else []),
                "--checkpoint-size",
                str(checkpoint_size),
                "--recall-limit",
                str(recall_limit),
            ],
        },
        "inputs": {
            "relation_index": {
                "path": repo_path(relation_index, root),
                "sha256": sha256_path(relation_index),
            },
            "ku_state": aggregate_path_state(all_unit_paths, root),
            "topic_state": aggregate_path_state(all_topic_paths, root),
        },
        "selection": {
            "source_doc_id": source_doc_id,
            "unit_type_filter": unit_type_filter,
            "selected_units": len(records),
            "checkpoints": dict(Counter(record["payload"]["checkpoint"] for record in records)),
            "by_unit_type": dict(Counter(record["payload"]["unit_type"] for record in records)),
        },
        "outputs": [
            {
                "path": repo_path(output, root),
                "bytes": output.stat().st_size,
                "sha256": sha256_path(output),
            }
        ],
        "semantic_boundary": "candidate recall only; no Topic membership is approved or applied",
    }
    manifest_output.parent.mkdir(parents=True, exist_ok=True)
    manifest_output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return len(records)


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSONL at {path}:{line_number}: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"JSONL row must be an object at {path}:{line_number}")
        rows.append(row)
    return rows


def materialize_hierarchy_decision_log(
    *,
    queue_input: Path,
    decision_map: Path,
    output: Path,
) -> int:
    """Expand an Agent-authored exact decision map; never infer a decision."""
    if output.exists():
        raise FileExistsError(f"decision output already exists: {output}")
    queue = load_jsonl(queue_input)
    queue_by_target: dict[str, dict] = {}
    for row in queue:
        target = str(row.get("target_ref") or "").strip()
        if not target:
            raise ValueError("review queue row lacks target_ref")
        if target in queue_by_target:
            raise ValueError(f"duplicate review queue target: {target}")
        queue_by_target[target] = row

    mapping = yaml.safe_load(decision_map.read_text(encoding="utf-8")) or {}
    if not isinstance(mapping, dict):
        raise ValueError("decision map must be a mapping")
    reviewer = str(mapping.get("reviewed_by") or "").strip()
    reviewed_at = str(mapping.get("reviewed_at") or "").strip()
    if not reviewer or not reviewed_at:
        raise ValueError("decision map requires reviewed_by and reviewed_at")

    approved: dict[str, dict] = {}
    for group in mapping.get("topics") or []:
        if not isinstance(group, dict):
            raise ValueError("topics[] must be a mapping")
        topic = str(group.get("topic") or "").strip()
        reason = str(group.get("reason") or "").strip()
        members = group.get("members") or {}
        if not topic.startswith("topics/") or not reason or not isinstance(members, dict):
            raise ValueError(f"invalid topic decision group: {topic or '<missing>'}")
        for target, raw_role in members.items():
            target = str(target).strip()
            role = str(raw_role or "").strip()
            if target in approved:
                raise ValueError(f"duplicate approved target: {target}")
            if role not in ALLOWED_ROLES:
                raise ValueError(f"invalid role for {target}: {role}")
            approved[target] = {"topic": topic, "role": role, "reason": reason}

    deferred = mapping.get("deferred") or {}
    if not isinstance(deferred, dict):
        raise ValueError("deferred must be a mapping")
    deferred = {str(target).strip(): str(reason or "").strip() for target, reason in deferred.items()}
    overlap = set(approved) & set(deferred)
    if overlap:
        raise ValueError(f"targets cannot be both approved and deferred: {sorted(overlap)}")
    if any(not reason for reason in deferred.values()):
        raise ValueError("every deferred target requires a reason")
    decisions = set(approved) | set(deferred)
    queue_targets = set(queue_by_target)
    if decisions != queue_targets:
        missing = sorted(queue_targets - decisions)
        extra = sorted(decisions - queue_targets)
        raise ValueError(f"decision coverage mismatch: missing={missing}; extra={extra}")

    rows: list[dict] = []
    for source in queue:
        target = source["target_ref"]
        if target in approved:
            choice = approved[target]
            state = "approved"
            memberships = [
                {
                    "topic": choice["topic"],
                    "role": choice["role"],
                    "primary": True,
                }
            ]
            reason = choice["reason"]
        else:
            state = "deferred"
            memberships = []
            reason = deferred[target]
        rows.append(
            {
                "candidate_id": source.get("candidate_id"),
                "origin_type": source.get("origin_type"),
                "origin_ref": source.get("origin_ref"),
                "candidate_type": source.get("candidate_type"),
                "target_ref": target,
                "checkpoint": (source.get("payload") or {}).get("checkpoint"),
                "unit_sha256": (source.get("payload") or {}).get("unit_sha256"),
                "automatic_recall": [
                    item.get("topic")
                    for item in (source.get("payload") or {}).get("candidate_topics") or []
                    if isinstance(item, dict) and item.get("topic")
                ],
                "state": state,
                "decision": {
                    "status": state,
                    "reason": reason,
                    "decided_by": reviewer,
                    "decided_at": reviewed_at,
                    "memberships": memberships,
                },
                "apply_permitted": False,
                "created_at": source.get("created_at"),
                "updated_at": reviewed_at,
            }
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )
    return len(rows)


def materialize_topic_membership_plan(
    *,
    decision_log: Path,
    output: Path,
    base_commit: str,
    batch_label: str,
    topics: Path = TOPICS,
    root: Path = ROOT,
) -> dict:
    """Convert exact Agent decisions to apply boilerplate without inferring membership."""
    if output.exists():
        raise FileExistsError(f"topic membership plan already exists: {output}")
    if not re.fullmatch(r"[0-9a-f]{40}", base_commit):
        raise ValueError("base_commit must be a full lowercase Git SHA")
    batch_label = str(batch_label or "").strip()
    if not batch_label:
        raise ValueError("batch_label is required")

    rows = load_jsonl(decision_log)
    if not rows:
        raise ValueError("decision log is empty")
    reviewers = {str((row.get("decision") or {}).get("decided_by") or "").strip() for row in rows}
    review_dates = {str((row.get("decision") or {}).get("decided_at") or "").strip() for row in rows}
    if len(reviewers) != 1 or "" in reviewers or len(review_dates) != 1 or "" in review_dates:
        raise ValueError("decision log must have one non-empty reviewer and review date")
    reviewed_by = next(iter(reviewers))
    reviewed_at = next(iter(review_dates))
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", reviewed_at):
        raise ValueError("decision date must use YYYY-MM-DD")

    approved_by_topic: defaultdict[str, dict[str, dict]] = defaultdict(dict)
    approved_targets: set[str] = set()
    for row in rows:
        state = str(row.get("state") or "").strip()
        decision = row.get("decision") or {}
        if row.get("apply_permitted") is not False:
            raise ValueError("decision log must remain apply_permitted=false")
        if state == "deferred":
            continue
        if state != "approved" or decision.get("status") != "approved":
            raise ValueError(f"unsupported decision state: {state or '<missing>'}")
        target = str(row.get("target_ref") or "").strip()
        memberships = decision.get("memberships") or []
        if not target or len(memberships) != 1 or not isinstance(memberships[0], dict):
            raise ValueError(f"approved decision requires exactly one explicit membership: {target}")
        membership = memberships[0]
        topic = str(membership.get("topic") or "").strip()
        role = str(membership.get("role") or "").strip()
        reason = str(decision.get("reason") or "").strip()
        if not topic.startswith("topics/") or role not in ALLOWED_ROLES or not reason:
            raise ValueError(f"invalid approved decision: {target}")
        if target in approved_targets:
            raise ValueError(f"duplicate approved target: {target}")
        approved_targets.add(target)
        approved_by_topic[topic][target] = {"role": role, "reason": reason}

    topic_specs: list[dict] = []
    for topic_ref in sorted(approved_by_topic):
        topic_path = topics / Path(topic_ref).name
        if not topic_path.is_file():
            raise ValueError(f"approved Topic does not exist: {topic_ref}")
        explicit_units = {
            f"04-knowledge/units/{value}"
            for value in UNIT_LINK_RE.findall(read_text(topic_path))
        }
        approved = approved_by_topic[topic_ref]
        missing_links = sorted(set(approved) - explicit_units)
        if missing_links:
            raise ValueError(f"approved targets are not explicit Topic links: {topic_ref}: {missing_links}")
        spec: dict = {
            "topic": repo_path(topic_path, root),
            "sha256": sha256_path(topic_path),
            "approve_explicit_links": True,
            "exclude": {
                unit: f"既有或非本批显式材料链接；保留当前状态，不在 {batch_label} 中重写。"
                for unit in sorted(explicit_units - set(approved))
            },
            "role_overrides": {
                unit: approved[unit]["role"]
                for unit in sorted(approved)
            },
            "scope_note_overrides": {
                unit: f"{batch_label} 逐对象语义复读：{approved[unit]['reason']}"
                for unit in sorted(approved)
            },
        }
        topic_specs.append(spec)

    hierarchy_overrides = {
        unit: {
            "role_in_theme": details["role"],
            "hierarchy_scope_note": (
                f"{batch_label} 已依据 KU 正文、来源定位、Topic 研究问题与替代 Topic 逐对象复核；"
                "自动召回只作候选，层级挂载不改变事实关系、置信度、共识或验证状态。"
            ),
        }
        for topic_ref in sorted(approved_by_topic)
        for unit, details in sorted(approved_by_topic[topic_ref].items())
    }
    plan = {
        "schema_version": "topic-membership-plan-v1",
        "base_commit": base_commit,
        "reviewed_by": reviewed_by,
        "reviewed_at": reviewed_at,
        "existing_hierarchy_policy": "merge",
        "topics": topic_specs,
        "hierarchy_overrides": hierarchy_overrides,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        yaml.safe_dump(plan, allow_unicode=True, sort_keys=False, width=1000),
        encoding="utf-8",
        newline="\n",
    )
    return {
        "decisions": len(rows),
        "approved_units": len(approved_targets),
        "deferred_units": len(rows) - len(approved_targets),
        "topics": len(topic_specs),
        "output": repo_path(output, root),
        "sha256": sha256_path(output),
    }


def hierarchy_version() -> str:
    index = HIERARCHY / "index.md"
    if not index.exists():
        return "unknown"
    match = re.search(r"层级知识体系\s+(v\d+(?:\.\d+)*)", read_text(index))
    return match.group(1) if match else "unknown"


def count_units_by_type() -> dict[str, int]:
    if not UNITS.exists():
        return {}
    return {
        directory.name: len(list(directory.glob("*.md")))
        for directory in sorted(UNITS.iterdir())
        if directory.is_dir() and not directory.name.startswith(".")
    }


def count_dimension_anchors() -> dict[str, int]:
    anchors = {}
    for dim_file in sorted(HIERARCHY.glob("dimension-*.md")):
        text = read_text(dim_file)
        anchors[dim_file.stem] = len(re.findall(r"\[([^\]]+)\]\(\.\./\.\./units/", text))
    return anchors


def count_theme_coverage(themes: Path | None = None, topics: Path | None = None) -> dict[str, dict]:
    """Return formal Theme-to-Topic coverage; source diversity is not inferred here."""
    themes = THEMES if themes is None else themes
    topics = TOPICS if topics is None else topics
    topic_counts: Counter[str] = Counter()
    topic_names: dict[str, list[str]] = {}
    if topics.exists():
        for topic_file in sorted(topics.glob("*.md")):
            if topic_file.name.lower() == "readme.md":
                continue
            data = frontmatter_data(topic_file)
            parent = str(data.get("parent_theme") or "").strip()
            if parent:
                topic_counts[parent] += 1
                topic_names.setdefault(parent, []).append(topic_file.stem)

    coverage = {}
    if not themes.exists():
        return coverage
    for theme_file in sorted(themes.glob("*.md")):
        if theme_file.name.lower() == "readme.md":
            continue
        data = frontmatter_data(theme_file)
        code = str(data.get("theme_code") or "").strip()
        coverage[theme_file.stem] = {
            "theme_code": code,
            "primary_dimension": str(data.get("primary_dimension") or "").strip(),
            "topic_count": topic_counts[code],
            "topics": topic_names.get(code, []),
        }
    return coverage


def count_topic_memberships(units: Path | None = None) -> Counter[str]:
    units = UNITS if units is None else units
    counts: Counter[str] = Counter()
    if not units.exists():
        return counts
    for unit_path in sorted(units.glob("*/*.md")):
        memberships = frontmatter_data(unit_path).get("topic_memberships") or []
        if not isinstance(memberships, list):
            continue
        for item in memberships:
            if isinstance(item, dict) and item.get("topic") and item.get("role"):
                counts[str(item["topic"]).strip()] += 1
    return counts


def find_cross_dimension_topics(topics: Path | None = None) -> list[tuple[str, int]]:
    topics = TOPICS if topics is None else topics
    results = []
    if not topics.exists():
        return results
    for topic_file in sorted(topics.glob("*.md")):
        if topic_file.name.lower() == "readme.md":
            continue
        data = frontmatter_data(topic_file)
        dimensions = {str(data.get("primary_dimension") or "").strip()}
        for theme in data.get("secondary_themes", []) or []:
            code = str(theme).strip()
            if "." in code:
                dimensions.add(code.split(".", 1)[0])
        dimensions.discard("")
        if len(dimensions) >= 3:
            results.append((topic_file.stem, len(dimensions)))
    return results


def _valid_topic_membership(data: dict) -> bool:
    memberships = data.get("topic_memberships") or []
    return isinstance(memberships, list) and any(
        isinstance(item, dict)
        and str(item.get("topic") or "").strip()
        and str(item.get("role") or "").strip()
        for item in memberships
    )


def find_missing_hierarchy_fields(units: Path = UNITS, *, root: Path = ROOT) -> list[dict]:
    """List incomplete KU hierarchy fields without proposing semantic values."""
    records = []
    if not units.exists():
        return records
    for unit_path in sorted(units.glob("*/*.md")):
        data = frontmatter_data(unit_path)
        missing = [
            field
            for field in HIERARCHY_FIELDS[:-1]
            if not str(data.get(field) or "").strip()
        ]
        if not _valid_topic_membership(data):
            missing.append("topic_memberships")
        if missing:
            records.append({
                "unit": unit_path.relative_to(root).as_posix() if unit_path.is_relative_to(root) else unit_path.as_posix(),
                "missing_fields": missing,
                "status": "needs_semantic_hierarchy_assignment",
                "apply_permitted": False,
            })
    return records


def write_hierarchy_backfill_queue(output: Path, units: Path = UNITS) -> int:
    """Write an explicit queue; fail if the destination already exists."""
    if output.exists():
        raise FileExistsError(f"queue output already exists: {output}")
    records = find_missing_hierarchy_fields(units)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in records) + ("\n" if records else ""),
        encoding="utf-8",
    )
    return len(records)


def generate(
    *,
    queue_output: Path | None = None,
    generation_manifest: Path | None = None,
    source_doc_id: str | None = None,
    review_date: str | None = None,
    unit_type_filter: str | None = None,
    checkpoint_size: int = 45,
    recall_limit: int = 5,
) -> None:
    counts = count_units_by_type()
    dim_anchors = count_dimension_anchors()
    theme_coverage = count_theme_coverage()
    topic_memberships = count_topic_memberships()
    cross_dimension = find_cross_dimension_topics()
    incomplete = find_missing_hierarchy_fields()
    total = sum(counts.values())

    zero_topic = sum(info["topic_count"] == 0 for info in theme_coverage.values())
    summary = {
        "hierarchy_version": hierarchy_version(),
        "knowledge_units": total,
        "unit_types": counts,
        "themes": len(theme_coverage),
        "themes_without_topics": zero_topic,
        "topics": sum(info["topic_count"] for info in theme_coverage.values()),
        "topic_memberships": sum(topic_memberships.values()),
        "complete_assignments": total - len(incomplete),
        "incomplete_assignments": len(incomplete),
        "dimension_anchor_counts": dim_anchors,
        "cross_dimension_topics": [
            {"topic": name, "dimension_count": dimension_count}
            for name, dimension_count in cross_dimension
        ],
        "apply_permitted": False,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if queue_output is not None:
        output = queue_output if queue_output.is_absolute() else ROOT / queue_output
        if source_doc_id is None:
            print(f"hierarchy_backfill_queue={write_hierarchy_backfill_queue(output)}")
        else:
            if generation_manifest is None or review_date is None:
                raise ValueError("source-scoped recall requires generation_manifest and review_date")
            manifest = generation_manifest if generation_manifest.is_absolute() else ROOT / generation_manifest
            count = write_source_hierarchy_review_queue(
                output=output,
                manifest_output=manifest,
                source_doc_id=source_doc_id,
                review_date=review_date,
                unit_type_filter=unit_type_filter,
                checkpoint_size=checkpoint_size,
                recall_limit=recall_limit,
            )
            print(f"hierarchy_source_review_queue={count}")
            print(f"hierarchy_source_review_manifest={manifest}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--queue-output",
        type=Path,
        help="显式生成当前 KU 层级语义待审队列；不执行层级写回",
    )
    parser.add_argument(
        "--generation-manifest",
        type=Path,
        help="同源召回队列的可重建 provenance manifest；仅与 --source-doc-id 配合使用",
    )
    parser.add_argument(
        "--source-doc-id",
        help="只召回仍缺层级且由指定 doc_id 支撑的 KU；不自动裁决 membership",
    )
    parser.add_argument(
        "--review-date",
        help="候选 envelope 的显式日期（YYYY-MM-DD），用于保持重建幂等",
    )
    parser.add_argument(
        "--unit-type",
        choices=sorted(DEFAULT_ROLE_BY_TYPE),
        help="在来源限定队列内进一步选择一种 KU type；只缩小召回范围，不裁决 membership",
    )
    parser.add_argument("--checkpoint-size", type=int, default=45)
    parser.add_argument("--recall-limit", type=int, default=5)
    parser.add_argument("--review-queue-input", type=Path)
    parser.add_argument("--decision-map", type=Path)
    parser.add_argument("--decision-output", type=Path)
    parser.add_argument("--decision-log-input", type=Path)
    parser.add_argument("--topic-plan-output", type=Path)
    parser.add_argument("--base-commit")
    parser.add_argument("--batch-label")
    args = parser.parse_args()
    decision_args = (args.review_queue_input, args.decision_map, args.decision_output)
    plan_args = (args.decision_log_input, args.topic_plan_output, args.base_commit, args.batch_label)
    if any(plan_args):
        if not all(plan_args):
            parser.error(
                "plan materialization requires --decision-log-input, --topic-plan-output, "
                "--base-commit, and --batch-label"
            )
        if any((args.queue_output, args.source_doc_id, args.generation_manifest, *decision_args)):
            parser.error("plan materialization cannot be combined with queue or decision generation")
        decision_log = args.decision_log_input if args.decision_log_input.is_absolute() else ROOT / args.decision_log_input
        plan_output = args.topic_plan_output if args.topic_plan_output.is_absolute() else ROOT / args.topic_plan_output
        print(
            "topic_membership_plan="
            + json.dumps(
                materialize_topic_membership_plan(
                    decision_log=decision_log,
                    output=plan_output,
                    base_commit=args.base_commit,
                    batch_label=args.batch_label,
                ),
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return
    if any(decision_args):
        if not all(decision_args):
            parser.error("decision materialization requires --review-queue-input, --decision-map, and --decision-output")
        if args.queue_output or args.source_doc_id or args.generation_manifest:
            parser.error("decision materialization cannot be combined with queue generation")
        queue_input = args.review_queue_input if args.review_queue_input.is_absolute() else ROOT / args.review_queue_input
        decision_map = args.decision_map if args.decision_map.is_absolute() else ROOT / args.decision_map
        decision_output = args.decision_output if args.decision_output.is_absolute() else ROOT / args.decision_output
        print(
            "hierarchy_decision_log="
            f"{materialize_hierarchy_decision_log(queue_input=queue_input, decision_map=decision_map, output=decision_output)}"
        )
        return
    if args.source_doc_id and not args.queue_output:
        parser.error("--source-doc-id requires --queue-output")
    if args.source_doc_id and (not args.generation_manifest or not args.review_date):
        parser.error("--source-doc-id requires --generation-manifest and --review-date")
    if args.generation_manifest and not args.source_doc_id:
        parser.error("--generation-manifest requires --source-doc-id")
    generate(
        queue_output=args.queue_output,
        generation_manifest=args.generation_manifest,
        source_doc_id=args.source_doc_id,
        review_date=args.review_date,
        unit_type_filter=args.unit_type,
        checkpoint_size=args.checkpoint_size,
        recall_limit=args.recall_limit,
    )


if __name__ == "__main__":
    main()
