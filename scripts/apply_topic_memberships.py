#!/usr/bin/env python3
"""按已审计划原子写回 KU 的五级层级与 Topic membership。

本执行器不发现、不推荐也不裁决 membership。计划必须显式列出已审 Topic、
输入哈希、排除项和语义覆盖；脚本只展开 Topic 文件中已有的 KU 显式链接，
完成整批预检、dry-run、原子写回和结果记录。
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import subprocess
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
FRONTMATTER_RE = re.compile(r"\A(?:\ufeff)?---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
UNIT_LINK_RE = re.compile(r"\.\./\.\./units/([A-Za-z0-9_./-]+\.md)")
HIERARCHY_KEYS = {
    "primary_domain",
    "secondary_domains",
    "primary_dimension",
    "secondary_dimensions",
    "primary_theme",
    "secondary_themes",
    "role_in_theme",
    "topic_memberships",
    "hierarchy_scope_note",
}
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


class PlanError(ValueError):
    """计划或目标状态不满足原子写回条件。"""


@dataclass(frozen=True)
class TopicSpec:
    path: str
    sha256: str
    domain: str
    dimension: str
    parent_theme: str
    unit_paths: tuple[str, ...]
    excluded: dict[str, str]
    role_overrides: dict[str, str]
    scope_note_overrides: dict[str, str]


@dataclass(frozen=True)
class PlannedChange:
    path: Path
    relative_path: str
    before: str
    after: str


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_yaml_mapping(path: Path) -> dict:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise PlanError(f"无法读取 YAML：{path}: {exc}") from exc
    if not isinstance(data, dict):
        raise PlanError(f"YAML 顶层必须是 mapping：{path}")
    return data


def parse_frontmatter(path: Path) -> tuple[dict, re.Match[str], str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise PlanError(f"缺少可解析 frontmatter：{path}")
    try:
        data = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        raise PlanError(f"frontmatter YAML 无效：{path}: {exc}") from exc
    if not isinstance(data, dict):
        raise PlanError(f"frontmatter 顶层必须是 mapping：{path}")
    return data, match, text


def normalize_unit_path(value: str) -> str:
    path = str(value or "").replace("\\", "/").strip()
    if path.startswith("04-knowledge/units/"):
        return path
    if path.startswith("units/"):
        return f"04-knowledge/{path}"
    if re.fullmatch(r"[A-Za-z0-9_-]+/[A-Za-z0-9_./-]+\.md", path):
        return f"04-knowledge/units/{path}"
    raise PlanError(f"无效 KU 路径：{value!r}")


def normalize_topic_path(value: str) -> str:
    path = str(value or "").replace("\\", "/").strip()
    if path.startswith("04-knowledge/structure/topics/"):
        return path
    if path.startswith("topics/"):
        return f"04-knowledge/structure/{path}"
    if re.fullmatch(r"[A-Za-z0-9_.-]+\.md", path):
        return f"04-knowledge/structure/topics/{path}"
    raise PlanError(f"无效 Topic 路径：{value!r}")


def topic_membership_ref(topic_path: str) -> str:
    return "topics/" + Path(topic_path).name


def current_head(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def dirty_targets(root: Path, relative_paths: list[str]) -> list[str]:
    if not relative_paths:
        return []
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--", *relative_paths],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def load_topic_specs(plan: dict, root: Path) -> tuple[list[TopicSpec], list[dict]]:
    specs: list[TopicSpec] = []
    rejected: list[dict] = []
    raw_topics = plan.get("topics")
    if not isinstance(raw_topics, list) or not raw_topics:
        raise PlanError("计划必须包含非空 topics 列表")

    seen_topics: set[str] = set()
    for raw in raw_topics:
        if not isinstance(raw, dict):
            raise PlanError("topics[] 必须是 mapping")
        topic_path = normalize_topic_path(raw.get("topic"))
        if topic_path in seen_topics:
            raise PlanError(f"重复 Topic：{topic_path}")
        seen_topics.add(topic_path)
        path = root / topic_path
        if not path.is_file():
            raise PlanError(f"Topic 不存在：{topic_path}")
        expected_hash = str(raw.get("sha256") or "").upper()
        if not re.fullmatch(r"[0-9A-F]{64}", expected_hash):
            raise PlanError(f"Topic 缺少有效 sha256：{topic_path}")
        actual_hash = sha256_path(path)
        if actual_hash != expected_hash:
            raise PlanError(f"Topic 哈希漂移：{topic_path}: {actual_hash} != {expected_hash}")
        if raw.get("approve_explicit_links") is not True:
            raise PlanError(f"Topic 未显式授权展开链接：{topic_path}")

        topic_data, _, topic_text = parse_frontmatter(path)
        domain = str(topic_data.get("primary_domain") or "").strip()
        dimension = str(topic_data.get("primary_dimension") or "").strip()
        parent_theme = str(topic_data.get("parent_theme") or "").strip()
        if not domain or not dimension or not re.fullmatch(r"[A-Z]\.\d+", parent_theme):
            raise PlanError(f"Topic 层级字段不完整：{topic_path}")
        if parent_theme.split(".", 1)[0] != dimension:
            raise PlanError(f"Topic dimension 与 parent_theme 不一致：{topic_path}")

        unit_paths = tuple(
            normalize_unit_path(value)
            for value in sorted(set(UNIT_LINK_RE.findall(topic_text)))
        )
        if not unit_paths:
            raise PlanError(f"Topic 没有显式 KU 链接：{topic_path}")

        excluded: dict[str, str] = {}
        for unit_value, reason in (raw.get("exclude") or {}).items():
            unit_path = normalize_unit_path(unit_value)
            if unit_path not in unit_paths:
                raise PlanError(f"排除项不是 Topic 显式链接：{topic_path}: {unit_path}")
            reason_text = str(reason or "").strip()
            if not reason_text:
                raise PlanError(f"排除项缺少语义理由：{topic_path}: {unit_path}")
            excluded[unit_path] = reason_text
            rejected.append({"topic": topic_membership_ref(topic_path), "unit": unit_path, "reason": reason_text})

        role_overrides = {
            normalize_unit_path(unit_value): str(role or "").strip()
            for unit_value, role in (raw.get("role_overrides") or {}).items()
        }
        scope_note_overrides = {
            normalize_unit_path(unit_value): str(note or "").strip()
            for unit_value, note in (raw.get("scope_note_overrides") or {}).items()
        }
        for override_path in {*role_overrides, *scope_note_overrides}:
            if override_path not in unit_paths or override_path in excluded:
                raise PlanError(f"覆盖项不是获批链接：{topic_path}: {override_path}")
        for role in role_overrides.values():
            if role not in ALLOWED_ROLES:
                raise PlanError(f"无效 role：{topic_path}: {role}")

        specs.append(
            TopicSpec(
                path=topic_path,
                sha256=expected_hash,
                domain=domain,
                dimension=dimension,
                parent_theme=parent_theme,
                unit_paths=unit_paths,
                excluded=excluded,
                role_overrides=role_overrides,
                scope_note_overrides=scope_note_overrides,
            )
        )
    return specs, rejected


def yaml_inline_list(values: list[str]) -> str:
    return "[" + ", ".join(values) + "]"


def quoted(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_hierarchy_block(
    *,
    domain: str,
    secondary_domains: list[str],
    primary_theme: str,
    secondary_themes: list[str],
    role_in_theme: str,
    memberships: list[dict],
    scope_note: str,
) -> str:
    primary_dimension = primary_theme.split(".", 1)[0]
    secondary_dimensions = sorted({theme.split(".", 1)[0] for theme in secondary_themes} - {primary_dimension})
    lines = [
        f"primary_domain: {domain}",
        f"secondary_domains: {yaml_inline_list(secondary_domains)}",
        f"primary_dimension: {primary_dimension}",
        f"secondary_dimensions: {yaml_inline_list(secondary_dimensions)}",
        f"primary_theme: {primary_theme}",
        f"secondary_themes: {yaml_inline_list(secondary_themes)}",
        f"role_in_theme: {role_in_theme}",
        "topic_memberships:",
    ]
    for membership in memberships:
        lines.extend(
            [
                f"  - topic: {membership['topic']}",
                f"    role: {membership['role']}",
                f"    primary: {'true' if membership['primary'] else 'false'}",
            ]
        )
        if membership.get("scope_note"):
            lines.append(f"    scope_note: {quoted(membership['scope_note'])}")
    lines.append(f"hierarchy_scope_note: {quoted(scope_note)}")
    return "\n".join(lines) + "\n"


def canonical_hierarchy(data: dict) -> dict:
    """Return a formatting-independent view of the governed hierarchy fields."""
    normalized = {key: data.get(key) for key in HIERARCHY_KEYS if key in data}
    for key in ("secondary_domains", "secondary_dimensions", "secondary_themes"):
        normalized[key] = sorted(str(value) for value in (normalized.get(key) or []))
    memberships: list[dict] = []
    for raw in normalized.get("topic_memberships") or []:
        if isinstance(raw, dict):
            item = {
                "topic": str(raw.get("topic") or "").strip(),
                "role": str(raw.get("role") or "").strip(),
                "primary": raw.get("primary") is True,
            }
            if raw.get("scope_note"):
                item["scope_note"] = str(raw["scope_note"]).strip()
            memberships.append(item)
    normalized["topic_memberships"] = sorted(memberships, key=lambda item: item["topic"])
    return normalized


def validate_existing_memberships(data: dict, path: Path) -> list[dict]:
    raw_memberships = data.get("topic_memberships") or []
    if not isinstance(raw_memberships, list):
        raise PlanError(f"现有 topic_memberships 必须是 list：{path}")
    memberships: list[dict] = []
    seen: set[str] = set()
    for raw in raw_memberships:
        if not isinstance(raw, dict):
            raise PlanError(f"现有 topic_memberships[] 必须是 mapping：{path}")
        topic = str(raw.get("topic") or "").strip()
        role = str(raw.get("role") or "").strip()
        primary = raw.get("primary")
        if not re.fullmatch(r"topics/[A-Za-z0-9_.-]+\.md", topic):
            raise PlanError(f"现有 membership Topic 无效：{path}: {topic!r}")
        if topic in seen:
            raise PlanError(f"现有 membership Topic 重复：{path}: {topic}")
        if role not in ALLOWED_ROLES or not isinstance(primary, bool):
            raise PlanError(f"现有 membership role/primary 无效：{path}: {topic}")
        seen.add(topic)
        item = {"topic": topic, "role": role, "primary": primary}
        if raw.get("scope_note"):
            item["scope_note"] = str(raw["scope_note"]).strip()
        memberships.append(item)
    if memberships and sum(item["primary"] for item in memberships) != 1:
        raise PlanError(f"现有 memberships 必须且只能有一个 primary：{path}")
    return memberships


def strip_hierarchy_fields(lines: list[str]) -> list[str]:
    """Remove governed top-level keys while leaving unrelated YAML formatting intact."""
    kept: list[str] = []
    index = 0
    while index < len(lines):
        match = re.match(r"^([A-Za-z0-9_-]+):(.*)$", lines[index])
        if not match or match.group(1) not in HIERARCHY_KEYS:
            kept.append(lines[index])
            index += 1
            continue
        value = match.group(2).strip()
        index += 1
        if value == "" or re.fullmatch(r"[>|][+-]?", value):
            while index < len(lines) and (not lines[index].strip() or lines[index][0].isspace()):
                index += 1
    return kept


def mutate_frontmatter(
    path: Path,
    hierarchy_block: str,
    updated: str,
    *,
    allow_existing: bool = False,
) -> tuple[str, str]:
    data, match, before = parse_frontmatter(path)
    present = sorted(HIERARCHY_KEYS.intersection(data))
    if present and not allow_existing:
        raise PlanError(f"目标已有层级字段，拒绝覆盖：{path}: {present}")
    unit_type = str(data.get("type") or data.get("node_type") or "").strip()
    if unit_type not in DEFAULT_ROLE_BY_TYPE:
        raise PlanError(f"目标 KU type 无效：{path}: {unit_type!r}")

    frontmatter = match.group(1)
    lines = frontmatter.splitlines()
    if present:
        lines = strip_hierarchy_fields(lines)
    insert_at = next((index + 1 for index, line in enumerate(lines) if re.match(r"^(?:type|node_type):", line)), None)
    if insert_at is None:
        raise PlanError(f"目标缺少 type 字段：{path}")
    block_lines = hierarchy_block.rstrip("\n").splitlines()
    lines[insert_at:insert_at] = block_lines

    updated_seen = False
    version_seen = False
    for index, line in enumerate(lines):
        if re.match(r"^updated:", line):
            lines[index] = f"updated: {updated}"
            updated_seen = True
        elif re.match(r"^version:", line):
            match_version = re.fullmatch(r"version:\s*(\d+)\s*", line)
            if not match_version:
                raise PlanError(f"version 不是整数：{path}: {line}")
            lines[index] = f"version: {int(match_version.group(1)) + 1}"
            version_seen = True
    if not updated_seen:
        lines.append(f"updated: {updated}")
    if not version_seen:
        lines.append("version: 1")

    replacement = "---\n" + "\n".join(lines) + "\n---\n"
    after = replacement + before[match.end():]
    return before, after


def build_changes(plan_path: Path, root: Path = ROOT) -> tuple[list[PlannedChange], dict]:
    plan = load_yaml_mapping(plan_path)
    if plan.get("schema_version") != "topic-membership-plan-v1":
        raise PlanError("不支持的 schema_version")
    existing_hierarchy_policy = str(plan.get("existing_hierarchy_policy") or "reject").strip()
    if existing_hierarchy_policy not in {"reject", "merge"}:
        raise PlanError("existing_hierarchy_policy 只允许 reject 或 merge")
    base_commit = str(plan.get("base_commit") or "").strip()
    if not re.fullmatch(r"[0-9a-f]{40}", base_commit):
        raise PlanError("base_commit 必须是完整 40 位 Git SHA")
    actual_head = current_head(root)
    if actual_head != base_commit:
        raise PlanError(f"HEAD 漂移：{actual_head} != {base_commit}")
    reviewed_by = str(plan.get("reviewed_by") or "").strip()
    reviewed_at = str(plan.get("reviewed_at") or "").strip()
    if not reviewed_by or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", reviewed_at):
        raise PlanError("计划必须声明 reviewed_by 与 YYYY-MM-DD reviewed_at")

    specs, rejected = load_topic_specs(plan, root)
    memberships_by_unit: dict[str, list[dict]] = defaultdict(list)
    topic_by_ref = {topic_membership_ref(spec.path): spec for spec in specs}
    domains_by_unit: dict[str, set[str]] = defaultdict(set)
    for spec in specs:
        topic_ref = topic_membership_ref(spec.path)
        for unit_path in spec.unit_paths:
            if unit_path in spec.excluded:
                continue
            target = root / unit_path
            if not target.is_file():
                raise PlanError(f"Topic 链接的 KU 不存在：{spec.path}: {unit_path}")
            data, _, _ = parse_frontmatter(target)
            unit_type = str(data.get("type") or data.get("node_type") or "").strip()
            role = spec.role_overrides.get(unit_path, DEFAULT_ROLE_BY_TYPE.get(unit_type, ""))
            if role not in ALLOWED_ROLES:
                raise PlanError(f"无法确定有效 role：{unit_path}: {role!r}")
            memberships_by_unit[unit_path].append(
                {
                    "topic": topic_ref,
                    "role": role,
                    "theme": spec.parent_theme,
                    "scope_note": spec.scope_note_overrides.get(unit_path),
                }
            )
            domains_by_unit[unit_path].add(spec.domain)

    primary_topic_overrides = {
        normalize_unit_path(unit): str(topic).strip()
        for unit, topic in (plan.get("primary_topic_overrides") or {}).items()
    }
    hierarchy_overrides = {
        normalize_unit_path(unit): value
        for unit, value in (plan.get("hierarchy_overrides") or {}).items()
    }
    unknown_override_units = (set(primary_topic_overrides) | set(hierarchy_overrides)) - set(memberships_by_unit)
    if unknown_override_units:
        raise PlanError(f"覆盖项不在获批 membership 中：{sorted(unknown_override_units)}")

    target_paths = sorted(memberships_by_unit)
    dirty = dirty_targets(root, target_paths)
    if dirty:
        raise PlanError("目标 KU 已有未提交改动：" + "; ".join(dirty))

    changes: list[PlannedChange] = []
    membership_count = 0
    memberships_added = 0
    memberships_updated = 0
    units_no_delta = 0
    for unit_path in target_paths:
        planned_memberships = sorted(memberships_by_unit[unit_path], key=lambda item: item["topic"])
        membership_count += len(planned_memberships)
        target = root / unit_path
        data, _, _ = parse_frontmatter(target)
        present = HIERARCHY_KEYS.intersection(data)
        if present and existing_hierarchy_policy == "reject":
            raise PlanError(f"目标已有层级字段，拒绝覆盖：{target}: {sorted(present)}")

        existing_memberships: list[dict] = []
        if present:
            required = {"primary_domain", "primary_dimension", "primary_theme", "role_in_theme"}
            missing = sorted(required - set(data))
            if missing:
                raise PlanError(f"现有层级字段不完整，拒绝增量合并：{target}: {missing}")
            expected_dimension = str(data.get("primary_theme") or "").split(".", 1)[0]
            if str(data.get("primary_dimension") or "") != expected_dimension:
                raise PlanError(f"现有 primary_dimension 与 primary_theme 不一致：{target}")
            existing_memberships = validate_existing_memberships(data, target)

        merged_by_topic = {item["topic"]: dict(item) for item in existing_memberships}
        for planned in planned_memberships:
            topic = planned["topic"]
            merged = dict(merged_by_topic.get(topic) or {})
            merged.update({"topic": topic, "role": planned["role"]})
            if planned.get("scope_note"):
                merged["scope_note"] = planned["scope_note"]
            merged_by_topic[topic] = merged
        memberships = sorted(merged_by_topic.values(), key=lambda item: item["topic"])

        domains = domains_by_unit[unit_path]
        if not present and len(domains) != 1:
            raise PlanError(f"新层级写入不支持跨 Domain membership：{unit_path}: {sorted(domains)}")
        available_topics = {item["topic"] for item in memberships}
        primary_topic = primary_topic_overrides.get(unit_path)
        if primary_topic is None:
            existing_primary = [item["topic"] for item in existing_memberships if item["primary"]]
            if len(existing_primary) == 1:
                primary_topic = existing_primary[0]
            elif len(memberships) != 1:
                raise PlanError(f"多 Topic KU 必须显式选择 primary_topic：{unit_path}")
            else:
                primary_topic = memberships[0]["topic"]
        if primary_topic not in available_topics:
            raise PlanError(f"primary_topic 不是获批 membership：{unit_path}: {primary_topic}")
        if unit_path in primary_topic_overrides and primary_topic not in topic_by_ref:
            raise PlanError(f"primary_topic override 不是本计划获批 membership：{unit_path}: {primary_topic}")

        override = hierarchy_overrides.get(unit_path) or {}
        if not isinstance(override, dict):
            raise PlanError(f"hierarchy_overrides 必须是 mapping：{unit_path}")
        default_primary_theme = str(data.get("primary_theme") or "").strip()
        if not default_primary_theme:
            if primary_topic not in topic_by_ref:
                raise PlanError(f"无法从计划解析 primary_topic 的 Theme：{unit_path}: {primary_topic}")
            default_primary_theme = topic_by_ref[primary_topic].parent_theme
        primary_theme = str(override.get("primary_theme") or default_primary_theme).strip()
        if not re.fullmatch(r"[A-Z]\.\d+", primary_theme):
            raise PlanError(f"primary_theme 无效：{unit_path}: {primary_theme}")
        extra_secondary = override.get("extra_secondary_themes") or []
        if not isinstance(extra_secondary, list):
            raise PlanError(f"extra_secondary_themes 必须是 list：{unit_path}")
        existing_secondary_themes = data.get("secondary_themes") or []
        if not isinstance(existing_secondary_themes, list):
            raise PlanError(f"现有 secondary_themes 必须是 list：{unit_path}")
        secondary_themes = sorted(
            (
                {item["theme"] for item in planned_memberships}
                | {str(value).strip() for value in existing_secondary_themes}
                | {str(value).strip() for value in extra_secondary}
            )
            - {primary_theme, ""}
        )
        if any(not re.fullmatch(r"[A-Z]\.\d+", value) for value in secondary_themes):
            raise PlanError(f"secondary_themes 无效：{unit_path}: {secondary_themes}")

        unit_type = str(data.get("type") or data.get("node_type") or "").strip()
        role_in_theme = str(
            override.get("role_in_theme") or data.get("role_in_theme") or DEFAULT_ROLE_BY_TYPE.get(unit_type) or ""
        ).strip()
        if role_in_theme not in ALLOWED_ROLES:
            raise PlanError(f"role_in_theme 无效：{unit_path}: {role_in_theme}")
        for membership in memberships:
            membership["primary"] = membership["topic"] == primary_topic
            membership.pop("theme", None)

        scope_note = str(
            override.get("hierarchy_scope_note")
            or data.get("hierarchy_scope_note")
            or "Topic 文件显式材料链接经本批逐对象语义复读确认；层级挂载不改变置信度、共识或验证状态。"
        ).strip()
        primary_domain = str(data.get("primary_domain") or "").strip()
        if not primary_domain:
            primary_domain = next(iter(domains))
        existing_secondary_domains = data.get("secondary_domains") or []
        if not isinstance(existing_secondary_domains, list):
            raise PlanError(f"现有 secondary_domains 必须是 list：{unit_path}")
        secondary_domains = sorted(
            ({str(value).strip() for value in existing_secondary_domains} | domains) - {primary_domain, ""}
        )
        block = render_hierarchy_block(
            domain=primary_domain,
            secondary_domains=secondary_domains,
            primary_theme=primary_theme,
            secondary_themes=secondary_themes,
            role_in_theme=role_in_theme,
            memberships=memberships,
            scope_note=scope_note,
        )
        desired = yaml.safe_load(block) or {}
        if present and canonical_hierarchy(data) == canonical_hierarchy(desired):
            units_no_delta += 1
            continue

        before_by_topic = {item["topic"]: item for item in existing_memberships}
        after_by_topic = {item["topic"]: item for item in memberships}
        memberships_added += len(set(after_by_topic) - set(before_by_topic))
        memberships_updated += sum(
            canonical_hierarchy({"topic_memberships": [before_by_topic[topic]]})
            != canonical_hierarchy({"topic_memberships": [after_by_topic[topic]]})
            for topic in set(after_by_topic).intersection(before_by_topic)
        )
        before, after = mutate_frontmatter(
            target,
            block,
            reviewed_at,
            allow_existing=existing_hierarchy_policy == "merge",
        )
        relative = target.relative_to(root).as_posix()
        changes.append(PlannedChange(target, relative, before, after))

    result = {
        "schema_version": "topic-membership-result-v1",
        "plan": plan_path.relative_to(root).as_posix() if plan_path.is_relative_to(root) else plan_path.as_posix(),
        "plan_sha256": sha256_path(plan_path),
        "base_commit": base_commit,
        "reviewed_by": reviewed_by,
        "reviewed_at": reviewed_at,
        "existing_hierarchy_policy": existing_hierarchy_policy,
        "topics_reviewed": len(specs),
        "explicit_link_candidates": membership_count + len(rejected),
        "memberships_approved": membership_count,
        "memberships_rejected": len(rejected),
        "memberships_added": memberships_added,
        "memberships_updated": memberships_updated,
        "units_planned": len(changes),
        "units_no_delta": units_no_delta,
        "rejected": rejected,
        "targets": [
            {
                "unit": change.relative_path,
                "before_sha256": sha256_bytes(change.before.encode("utf-8")),
                "after_sha256": sha256_bytes(change.after.encode("utf-8")),
            }
            for change in changes
        ],
    }
    return changes, result


def write_diff(changes: list[PlannedChange], output: Path) -> None:
    chunks: list[str] = []
    for change in changes:
        chunks.extend(
            difflib.unified_diff(
                change.before.splitlines(keepends=True),
                change.after.splitlines(keepends=True),
                fromfile=change.relative_path,
                tofile=change.relative_path,
            )
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("".join(chunks), encoding="utf-8")


def atomic_apply(changes: list[PlannedChange]) -> None:
    staged: dict[Path, Path] = {}
    originals = {change.path: change.before.encode("utf-8") for change in changes}
    replaced: list[Path] = []
    try:
        for change in changes:
            handle = tempfile.NamedTemporaryFile(
                mode="wb",
                prefix=f".{change.path.name}.",
                suffix=".tmp",
                dir=change.path.parent,
                delete=False,
            )
            with handle:
                handle.write(change.after.encode("utf-8"))
                handle.flush()
                os.fsync(handle.fileno())
            staged[change.path] = Path(handle.name)
        for target, staged_path in staged.items():
            os.replace(staged_path, target)
            replaced.append(target)
    except Exception:
        for target in reversed(replaced):
            handle = tempfile.NamedTemporaryFile(
                mode="wb",
                prefix=f".{target.name}.rollback.",
                suffix=".tmp",
                dir=target.parent,
                delete=False,
            )
            with handle:
                handle.write(originals[target])
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(handle.name, target)
        raise
    finally:
        for staged_path in staged.values():
            if staged_path.exists():
                staged_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path, help="已审 topic-membership-plan-v1 YAML")
    parser.add_argument("--apply", action="store_true", help="通过整批预检后执行原子写回；默认 dry-run")
    parser.add_argument("--diff-output", type=Path, help="写出整批 unified diff")
    parser.add_argument("--result", type=Path, help="写出机器可读结果 JSON")
    args = parser.parse_args()

    plan_path = args.plan if args.plan.is_absolute() else ROOT / args.plan
    changes, result = build_changes(plan_path)
    result["outcome"] = "applied" if args.apply else "dry_run"
    if args.diff_output:
        diff_output = args.diff_output if args.diff_output.is_absolute() else ROOT / args.diff_output
        write_diff(changes, diff_output)
        result["diff"] = diff_output.relative_to(ROOT).as_posix() if diff_output.is_relative_to(ROOT) else diff_output.as_posix()
        result["diff_sha256"] = sha256_path(diff_output)
    if args.apply:
        atomic_apply(changes)
    if args.result:
        result_path = args.result if args.result.is_absolute() else ROOT / args.result
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "targets"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
