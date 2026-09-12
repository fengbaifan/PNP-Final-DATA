#!/usr/bin/env python3
"""Preview or atomically apply a reviewed relation migration plan.

The plan is JSONL. Each record identifies one existing explicit relation by
source file, relation type and target, then supplies one or more replacements.
Semantic decisions belong in the plan; this script only validates and writes.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

import yaml

try:
    from scripts._accepted_knowledge import select_paths
    from scripts._relation_schema import VALID_RELATION_TYPES
except ModuleNotFoundError:
    from _accepted_knowledge import select_paths
    from _relation_schema import VALID_RELATION_TYPES


BASE = Path(__file__).resolve().parents[1]
FRONTMATTER_RE = re.compile(r"^(\ufeff?---\n)(.*?)(\n---\n)", re.DOTALL)
RELATION_LINE_RE = re.compile(r"^(?P<indent>\s*-\s+)(?P<json>\{.*\})\s*$")


def _read_plan(path: Path) -> list[dict]:
    decisions: list[dict] = []
    for number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not raw.strip():
            continue
        item = json.loads(raw)
        if not isinstance(item, dict):
            raise ValueError(f"plan line {number} must be an object")
        item["_line"] = number
        decisions.append(item)
    return decisions


def _validated_replacement(original: dict, replacement: dict, line: int) -> dict:
    if not isinstance(replacement, dict):
        raise ValueError(f"plan line {line}: replacement must be an object")
    relation_type = replacement.get("relation_type")
    if relation_type not in VALID_RELATION_TYPES:
        raise ValueError(f"plan line {line}: unknown relation type {relation_type!r}")
    updated = dict(original)
    for key in ("relation_type", "target", "note", "time", "role", "scope"):
        if key in replacement:
            value = replacement[key]
            if value in (None, ""):
                updated.pop(key, None)
            else:
                updated[key] = value
    target = updated.get("target")
    if not isinstance(target, str) or not target.endswith(".md"):
        raise ValueError(f"plan line {line}: invalid target {target!r}")
    if not (BASE / "04-knowledge" / "units" / target).is_file():
        raise ValueError(f"plan line {line}: missing target {target!r}")
    return updated


def _render_file(path: Path, decisions: list[dict]) -> tuple[str, list[str]]:
    current = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    match = FRONTMATTER_RE.search(current)
    if not match:
        raise ValueError(f"{path.relative_to(BASE).as_posix()}: missing frontmatter")
    lines = match.group(2).splitlines()
    parsed: list[tuple[int, dict, str]] = []
    for index, raw in enumerate(lines):
        relation = RELATION_LINE_RE.match(raw)
        if relation:
            parsed.append((index, json.loads(relation.group("json")), relation.group("indent")))

    changes: list[str] = []
    for decision in decisions:
        old_type = decision.get("relation_type")
        target = decision.get("target")
        replacements = decision.get("replacements")
        if not isinstance(replacements, list) or not replacements:
            raise ValueError(f"plan line {decision['_line']}: replacements must be a non-empty list")
        found = [item for item in parsed if item[1].get("relation_type") == old_type and item[1].get("target") == target]
        if not found:
            expected = [
                _validated_replacement(
                    {"relation_type": old_type, "target": target}, replacement, decision["_line"]
                )
                for replacement in replacements
            ]
            already_applied = all(
                sum(
                    all(relation.get(key) == value for key, value in expected_relation.items())
                    for _, relation, _ in parsed
                ) == 1
                for expected_relation in expected
            )
            if already_applied:
                new_types = ",".join(replacement["relation_type"] for replacement in replacements)
                changes.append(f"already-applied {old_type}->{new_types} {target}")
                continue
        if len(found) != 1:
            raise ValueError(
                f"plan line {decision['_line']}: expected one {old_type} -> {target} in "
                f"{path.relative_to(BASE).as_posix()}, found {len(found)}"
            )
        index, original, indent = found[0]
        rendered = [
            indent + json.dumps(
                _validated_replacement(original, replacement, decision["_line"]),
                ensure_ascii=False,
                separators=(",", ":"),
            )
            for replacement in replacements
        ]
        lines[index:index + 1] = rendered
        delta = len(rendered) - 1
        if delta:
            parsed = [
                (item_index + delta if item_index > index else item_index, relation, item_indent)
                for item_index, relation, item_indent in parsed
            ]
        parsed = [item for item in parsed if item[0] != index]
        for offset, replacement_line in enumerate(rendered):
            relation = RELATION_LINE_RE.match(replacement_line)
            assert relation is not None
            parsed.append((index + offset, json.loads(relation.group("json")), relation.group("indent")))
        new_types = ",".join(replacement["relation_type"] for replacement in replacements)
        changes.append(f"{old_type}->{new_types} {target}")

    frontmatter = "\n".join(lines)
    return match.group(1) + frontmatter + match.group(3) + current[match.end():], changes


def _atomic_write(planned: dict[Path, str]) -> None:
    originals = {path: path.read_bytes() for path in planned}
    temporary: list[tuple[Path, Path]] = []
    replaced: list[Path] = []
    try:
        for index, (path, text) in enumerate(planned.items()):
            tmp = path.with_name(f".{path.name}.relations-{os.getpid()}-{index}.tmp")
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
    parser.add_argument("plan")
    parser.add_argument("--apply", action="store_true", help="apply after full validation; default is dry-run")
    args = parser.parse_args()

    plan_path = Path(args.plan)
    if not plan_path.is_absolute():
        plan_path = BASE / plan_path
    decisions = _read_plan(plan_path)
    accepted = {
        path.resolve()
        for path in select_paths(BASE, "units", list((BASE / "04-knowledge" / "units").rglob("*.md")))
    }
    grouped: dict[Path, list[dict]] = {}
    seen: set[tuple[str, str, str]] = set()
    for decision in decisions:
        source = decision.get("source")
        key = (str(source), str(decision.get("relation_type")), str(decision.get("target")))
        if key in seen:
            raise ValueError(f"plan line {decision['_line']}: duplicate relation selector")
        seen.add(key)
        path = (BASE / str(source)).resolve()
        if path not in accepted:
            raise ValueError(f"plan line {decision['_line']}: source is not an accepted KU: {source!r}")
        grouped.setdefault(path, []).append(decision)

    planned: dict[Path, str] = {}
    changes: list[str] = []
    for path, file_decisions in grouped.items():
        planned[path], file_changes = _render_file(path, file_decisions)
        relative = path.relative_to(BASE).as_posix()
        changes.extend(f"{relative}: {change}" for change in file_changes)

    mode = "APPLY" if args.apply else "DRY RUN"
    print(f"[{mode}] decisions={len(decisions)} files={len(planned)} resulting_relations={sum(len(d['replacements']) for d in decisions)}")
    for change in changes:
        print(f"  {change}")
    if args.apply:
        _atomic_write(planned)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
