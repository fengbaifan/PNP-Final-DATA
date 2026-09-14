#!/usr/bin/env python3
"""Project accepted formal relations into the readable relation table of each KU.

Frontmatter remains authoritative. The script preserves prose after the first
standard relation table and makes inverse navigation point back to its source
card, so evidence labels cannot be mistaken for labels on the target card.
"""
from __future__ import annotations

import argparse
import os
import re
from collections import defaultdict
from pathlib import Path, PurePosixPath

import yaml

try:
    from scripts._accepted_knowledge import select_paths
    from scripts._relation_schema import INVERSE_MAP
except ModuleNotFoundError:
    from _accepted_knowledge import select_paths
    from _relation_schema import INVERSE_MAP


BASE = Path(__file__).resolve().parents[1]
UNITS = BASE / "04-knowledge" / "units"
FRONTMATTER_RE = re.compile(r"^\ufeff?---\n(.*?)\n---\n", re.DOTALL)
HEADING_RE = re.compile(r"^### (?:当前)?关系记录(?:（[^\n]+）)?\s*$", re.MULTILINE)
TABLE_RE = re.compile(
    r"^\| 方向与关系 \| 关联知识元 \| 语境与证据 \|\n"
    r"^\|---\|---\|---\|\n"
    r"(?:^\|.*\|\n)+",
    re.MULTILINE,
)

LABELS = {
    "acquired_by": "由其购入",
    "acquirer_of": "购入者",
    "addressed_to": "致函",
    "addressee_of": "为收信人",
    "advised": "向其建议",
    "advised_by": "获其建议",
    "appointer_of": "任命者",
    "appointed_by": "由其任命",
    "authored_by": "作者",
    "author_of": "所著文献",
    "borrowed_by": "由其借阅",
    "borrower_of": "借阅者",
    "collaborated_with": "合作",
    "commissioned_by": "由其委托",
    "commissioner_of": "委托者",
    "contributed_by": "由其贡献",
    "contributor_to": "贡献者",
    "corresponded_with": "通信",
    "created_by": "创作者",
    "creator_of": "所创作对象",
    "derived_from": "源自",
    "source_of": "来源",
    "disputed_with": "争执",
    "employed_by": "受雇于",
    "employer_of": "雇主",
    "granted_privilege_to": "向其授予权利",
    "privilege_granted_by": "由其授予权利",
    "exemplified_by": "以此为实例",
    "instantiates": "为其具体实例",
    "friend_of": "朋友",
    "handled_by": "由其经手",
    "handler_of": "经手者",
    "held_by": "由其保管",
    "holder_of": "保管对象",
    "has_participant": "参与者",
    "participated_in": "参与事件",
    "has_subject": "所涉对象",
    "subject_of": "为其所涉对象",
    "honourer_of": "荣衔授予者",
    "honoured_by": "获其授予荣衔",
    "intended_site_of": "预定地点",
    "intended_for": "拟用于",
    "installed_at": "安置于",
    "installation_site_of": "安置地点",
    "issued_by": "由其发布",
    "issuer_of": "发布者",
    "kin_of": "亲缘",
    "located_at": "位于",
    "location_of": "所在地",
    "member_of": "隶属／任职于",
    "contains": "包含成员",
    "occurred_at": "发生于",
    "scene_of": "事件地点",
    "spouse_of": "配偶",
    "owned_by": "由其收藏／拥有",
    "owner_of": "收藏者／所有者",
    "part_of": "组成部分",
    "patron_of": "赞助者／保护人",
    "patronized_by": "受其赞助／保护",
    "pendant_of": "配对作品",
    "supplied_by": "由其供应",
    "supplier_of": "供应者",
    "testified_about": "为其相关争议作证",
    "testimony_subject_of": "证词所涉对象",
    "trained_by": "师从／受训于",
    "teacher_of": "教师",
    "uses_procedure": "采用程序",
    "procedure_used_by": "程序使用者",
    "variant_of": "为其版本／复制",
    "has_variant": "有版本／复制",
}


def _frontmatter(text: str, path: Path) -> dict:
    match = FRONTMATTER_RE.search(text)
    if not match:
        raise ValueError(f"{path.relative_to(BASE).as_posix()}: missing frontmatter")
    value = yaml.safe_load(match.group(1)) or {}
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(BASE).as_posix()}: invalid frontmatter")
    return value


def _normalize_target(target: str) -> str:
    value = target.replace("\\", "/").strip()
    for prefix in ("04-knowledge/units/", "units/"):
        if value.startswith(prefix):
            value = value[len(prefix):]
    while value.startswith("../"):
        value = value[3:]
    while value.startswith("./"):
        value = value[2:]
    return value


def _relative_link(source_key: str, target: str) -> str:
    start = PurePosixPath(source_key).parent
    return os.path.relpath(target, start).replace("\\", "/")


def _repo_relative_link(source_key: str, target: str) -> str:
    start = PurePosixPath("04-knowledge/units") / PurePosixPath(source_key).parent
    return os.path.relpath(target, start).replace("\\", "/")


def _escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _evidence_text(source_key: str, relation: dict) -> str:
    evidence = relation.get("evidence_ref") or {}
    parts: list[str] = []
    source_file = str(evidence.get("source_file") or "")
    if source_file.startswith(("http://", "https://")):
        parts.append(f"[来源]({source_file})")
    elif source_file:
        parts.append(f"[来源]({_repo_relative_link(source_key, source_file)})")
    if evidence.get("doc_id"):
        parts.append(str(evidence["doc_id"]))
    if evidence.get("source_span"):
        parts.append(str(evidence["source_span"]))
    return "；".join(parts) if parts else "未登记可点击证据定位"


def _context(source_key: str, relation: dict, source_title: str | None = None) -> str:
    parts = [str(relation.get("note") or "").strip().rstrip("。；;")]
    for key, label in (("time", "时间"), ("role", "角色"), ("scope", "范围")):
        if relation.get(key) not in (None, "", [], {}):
            parts.append(f"{label}：{relation[key]}")
    evidence = _evidence_text(source_key, relation)
    if source_title:
        parts.append(f"原断言与证据见发出端卡片“{source_title}”：{evidence}")
    else:
        parts.append(f"证据：{evidence}")
    return "；".join(part for part in parts if part)


def _row(direction: str, relation_type: str, target_title: str, link: str, context: str) -> str:
    label = LABELS.get(relation_type, relation_type)
    if direction == "outgoing":
        relation_cell = f"→ {label}（`{relation_type}`）"
    else:
        relation_cell = f"← {label}（`{relation_type}`，反向投影）"
    return f"| {_escape(relation_cell)} | [{_escape(target_title)}]({link}) | {_escape(context)} |"


def render_table(rows: list[str]) -> str:
    return "\n".join(
        [
            "| 方向与关系 | 关联知识元 | 语境与证据 |",
            "|---|---|---|",
            *rows,
        ]
    ) + "\n"


def replace_relation_view(text: str, rows: list[str]) -> str:
    headings = list(HEADING_RE.finditer(text))
    if len(headings) != 1:
        raise ValueError(f"expected one relation heading, found {len(headings)}")
    text = HEADING_RE.sub("### 关系记录", text, count=1)
    table = TABLE_RE.search(text)
    if rows:
        if table is None:
            heading = HEADING_RE.search(text)
            assert heading is not None
            return text[:heading.end()] + "\n\n" + render_table(rows) + text[heading.end():].lstrip("\n")
        return text[:table.start()] + render_table(rows) + text[table.end():]
    if table is not None:
        return text[:table.start()] + "当前没有正式关系。正文中的导航与线索不自动形成关系边。\n" + text[table.end():]
    return text


def _atomic_write(planned: dict[Path, str]) -> None:
    originals = {path: path.read_bytes() for path in planned}
    temporary: list[tuple[Path, Path]] = []
    replaced: list[Path] = []
    try:
        for index, (path, text) in enumerate(planned.items()):
            tmp = path.with_name(f".{path.name}.relation-view-{os.getpid()}-{index}.tmp")
            tmp.write_text(text, encoding="utf-8", newline="\n")
            temporary.append((tmp, path))
        for tmp, path in temporary:
            tmp.replace(path)
            replaced.append(path)
    except OSError:
        for path in reversed(replaced):
            rollback = path.with_name(f".{path.name}.rollback-{os.getpid()}.tmp")
            rollback.write_bytes(originals[path])
            rollback.replace(path)
        raise
    finally:
        for tmp, _ in temporary:
            tmp.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write after full validation; default is dry-run")
    args = parser.parse_args()

    paths = select_paths(BASE, "units", list(UNITS.rglob("*.md")))
    units: dict[str, tuple[Path, str, str, list[dict]]] = {}
    for path in paths:
        text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        data = _frontmatter(text, path)
        key = path.relative_to(UNITS).as_posix()
        relations = data.get("relations") or []
        if not isinstance(relations, list) or not all(isinstance(item, dict) for item in relations):
            raise ValueError(f"{key}: relations must be a list of objects")
        units[key] = (path, text, str(data.get("title") or path.stem), relations)

    explicit_pairs = {
        (source, _normalize_target(str(relation.get("target") or "")))
        for source, (_, _, _, relations) in units.items()
        for relation in relations
    }
    rows_by_unit: dict[str, list[str]] = defaultdict(list)
    for source, (_, _, source_title, relations) in units.items():
        for relation in relations:
            target = _normalize_target(str(relation.get("target") or ""))
            if target not in units:
                raise ValueError(f"{source}: target is not an accepted KU: {target!r}")
            relation_type = str(relation.get("relation_type") or "")
            target_title = units[target][2]
            rows_by_unit[source].append(
                _row(
                    "outgoing",
                    relation_type,
                    target_title,
                    _relative_link(source, target),
                    _context(source, relation),
                )
            )
            inverse = INVERSE_MAP.get(relation_type)
            if inverse and (target, source) not in explicit_pairs:
                rows_by_unit[target].append(
                    _row(
                        "incoming",
                        inverse,
                        source_title,
                        _relative_link(target, source),
                        _context(source, relation, source_title=source_title),
                    )
                )

    planned: dict[Path, str] = {}
    for key, (path, text, _, _) in units.items():
        candidate = replace_relation_view(text, rows_by_unit.get(key, []))
        if candidate != text:
            planned[path] = candidate

    mode = "APPLY" if args.apply else "DRY RUN"
    print(
        f"[{mode}] accepted_units={len(units)} explicit_relations={sum(len(item[3]) for item in units.values())} "
        f"projected_rows={sum(len(rows) for rows in rows_by_unit.values())} changed_files={len(planned)}"
    )
    for path in sorted(planned):
        print(f"  {path.relative_to(BASE).as_posix()}")
    if args.apply:
        _atomic_write(planned)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
