#!/usr/bin/env python3
"""Build and validate the derived Skill registry snapshot."""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

import yaml


BASE = Path(__file__).resolve().parents[1]
SKILLS_DIR = BASE / ".agents" / "skills"
REGISTRY_PATH = BASE / "06-runtime" / "state" / "skill-registry.json"
SCRIPT_REF = re.compile(r"scripts/[A-Za-z0-9_-]+\.py")
REFERENCE_REF = re.compile(
    r"`([^`\r\n]+\.md)`|\[[^\]]+\]\(([^)\r\n]+\.md)\)"
)
SKIP_WALK_DIRS = {".git", ".tmp", ".venv", "node_modules", "__pycache__", ".specstory"}


class UniqueKeyLoader(yaml.SafeLoader):
    """Fail closed instead of silently overwriting duplicate frontmatter keys."""


def _construct_unique_mapping(loader: UniqueKeyLoader, node: yaml.nodes.MappingNode, deep: bool = False) -> dict:
    loader.flatten_mapping(node)
    mapping: dict = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ValueError(f"duplicate YAML key: {key}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def _frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"missing YAML frontmatter: {path}")
    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration as exc:
        raise ValueError(f"unclosed YAML frontmatter: {path}") from exc
    try:
        data = yaml.load("\n".join(lines[1:end]), Loader=UniqueKeyLoader) or {}
    except (ValueError, yaml.YAMLError) as exc:
        raise ValueError(f"invalid YAML frontmatter in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"frontmatter must be a mapping: {path}")
    return data


def discover_skill_files(skills_dir: Path = SKILLS_DIR) -> list[Path]:
    """Return every active leaf and router contract; role comes from frontmatter."""
    return sorted(skills_dir.rglob("SKILL.md"))


def discover_skill_dirs(skills_dir: Path = SKILLS_DIR) -> dict[str, Path]:
    mapping: dict[str, Path] = {}
    for skill_file in discover_skill_files(skills_dir):
        name = str(_frontmatter(skill_file).get("name") or "").strip()
        if name and name not in mapping:
            mapping[name] = skill_file
    return mapping


def _normalized_reference(raw: str, source: Path, base: Path) -> Path | None:
    raw = raw.strip().replace("\\", "/")
    if not raw or "://" in raw or "*" in raw:
        return None
    candidate = base / raw if raw.startswith(".agents/") else source.parent / raw
    candidate = Path(os.path.normpath(candidate))
    explicit_path = raw.startswith((".agents/", "../", "./", "references/"))
    if not explicit_path and not candidate.is_file():
        return None
    try:
        relative = candidate.relative_to(base)
    except ValueError:
        return None
    parts = relative.parts
    if (
        len(parts) >= 5
        and parts[:2] == (".agents", "skills")
        and "references" in parts
        and relative.suffix.lower() == ".md"
    ):
        return relative
    return None


def _direct_references(source: Path, base: Path) -> set[Path]:
    text = source.read_text(encoding="utf-8-sig")
    references: set[Path] = set()
    for match in REFERENCE_REF.finditer(text):
        raw = match.group(1) or match.group(2) or ""
        normalized = _normalized_reference(raw, source, base)
        if normalized is not None:
            references.add(normalized)
    return references


def _reference_closure(skill_file: Path, base: Path) -> list[str]:
    pending = list(_direct_references(skill_file, base))
    seen: set[Path] = set()
    while pending:
        relative = pending.pop()
        if relative in seen:
            continue
        seen.add(relative)
        target = base / relative
        if target.is_file():
            pending.extend(_direct_references(target, base) - seen)
    return sorted(path.as_posix() for path in seen)


def _metadata_list(metadata: dict, field: str) -> list[str]:
    value = metadata.get(field, [])
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _skill_entry(skill_file: Path, base: Path, skills_dir: Path) -> dict:
    metadata = _frontmatter(skill_file)
    description = " ".join(str(metadata.get("description") or "").split())
    references = sorted(path.as_posix() for path in _direct_references(skill_file, base))
    contract_paths = [skill_file, *(base / ref for ref in references if (base / ref).is_file())]
    scripts = sorted({
        match
        for path in contract_paths
        for match in SCRIPT_REF.findall(path.read_text(encoding="utf-8-sig"))
    })
    entry = {
        "path": skill_file.relative_to(base).as_posix(),
        "kind": str(metadata.get("kind") or "").strip(),
        "phase": str(metadata.get("phase") or "support").strip(),
        "description": description,
        "triggers": _metadata_list(metadata, "triggers"),
        "references": references,
        "scripts": scripts,
    }
    routes_to = _metadata_list(metadata, "routes_to")
    if routes_to:
        entry["routes_to"] = routes_to
    return entry


def build_registry(base: Path = BASE) -> dict[str, dict]:
    skills_dir = base / ".agents" / "skills"
    entries: dict[str, dict] = {}
    for skill_file in discover_skill_files(skills_dir):
        metadata = _frontmatter(skill_file)
        name = str(metadata.get("name") or "").strip()
        if name and name not in entries:
            entries[name] = _skill_entry(skill_file, base, skills_dir)
    return dict(sorted(entries.items()))


def duplicate_declared_names(skills_dir: Path = SKILLS_DIR) -> dict[str, list[Path]]:
    declared: dict[str, list[Path]] = {}
    for path in discover_skill_files(skills_dir):
        name = str(_frontmatter(path).get("name") or "").strip()
        if name:
            declared.setdefault(name, []).append(path)
    return {name: paths for name, paths in declared.items() if len(paths) > 1}


def external_skill_files(base: Path = BASE) -> list[Path]:
    active_root = base / ".agents" / "skills"
    found: list[Path] = []
    for root, dirs, files in os.walk(base):
        dirs[:] = [name for name in dirs if name not in SKIP_WALK_DIRS]
        root_path = Path(root)
        if "SKILL.md" not in files:
            continue
        candidate = root_path / "SKILL.md"
        try:
            candidate.relative_to(active_root)
        except ValueError:
            found.append(candidate)
    return sorted(found)


def validate(registry: dict[str, dict], base: Path = BASE) -> list[str]:
    issues: list[str] = []
    skills_dir = base / ".agents" / "skills"
    actual = build_registry(base)

    for path in discover_skill_files(skills_dir):
        name = str(_frontmatter(path).get("name") or "").strip()
        if path.relative_to(skills_dir).parts != (name, "SKILL.md"):
            issues.append(f"Skill 必须使用扁平规范路径: {path.relative_to(base).as_posix()}")

    for path in external_skill_files(base):
        issues.append(f"唯一 Skill 根之外存在 SKILL.md: {path.relative_to(base).as_posix()}")

    for name, paths in sorted(duplicate_declared_names(skills_dir).items()):
        rendered = ", ".join(path.relative_to(base).as_posix() for path in paths)
        issues.append(f"重复 Skill name '{name}': {rendered}")

    trigger_owners: dict[str, list[str]] = {}
    referenced: set[str] = set()
    for name, entry in actual.items():
        if entry.get("phase") not in {"current", "later", "support"}:
            issues.append(f"[{name}] invalid phase")
        kind = entry.get("kind")
        if kind not in {"leaf", "router"}:
            issues.append(f"[{name}] kind 必须为 leaf 或 router")
        triggers = entry.get("triggers", [])
        if not triggers:
            issues.append(f"[{name}] 缺少显式 triggers")
        for trigger in triggers:
            trigger_owners.setdefault(trigger.casefold(), []).append(name)
        routes_to = entry.get("routes_to", [])
        if kind == "router" and not routes_to:
            issues.append(f"[{name}] router 缺少 routes_to")
        if kind == "leaf" and routes_to:
            issues.append(f"[{name}] leaf 不得声明 routes_to")
        for target in routes_to:
            if target not in actual:
                issues.append(f"[{name}] routes_to 指向不存在 Skill: {target}")
        skill_file = base / entry["path"]
        direct = set(entry.get("references", []))
        hidden = sorted(set(_reference_closure(skill_file, base)) - direct)
        for reference in hidden:
            issues.append(f"[{name}] reference 隐藏第二层必读规则，必须在 Skill 直接登记: {reference}")
        referenced.update(entry.get("references", []))

    for trigger, owners in sorted(trigger_owners.items()):
        if len(owners) > 1:
            issues.append(f"重复 trigger '{trigger}': {', '.join(sorted(owners))}")

    for name in sorted(set(actual) - set(registry)):
        issues.append(f"SKILL.md 存在于磁盘但快照缺失: {name}")
    for name in sorted(set(registry) - set(actual)):
        issues.append(f"注册快照中有但磁盘无 SKILL.md: {name}")
    for name in sorted(set(actual) & set(registry)):
        if registry[name] != actual[name]:
            issues.append(f"[{name}] 注册快照与 SKILL.md 磁盘事实不一致")
        for script in actual[name].get("scripts", []):
            if not (base / script).is_file():
                issues.append(f"[{name}] 活跃契约引用不存在脚本: {script}")
        for reference in actual[name].get("references", []):
            if not (base / reference).is_file():
                issues.append(f"[{name}] 活跃契约引用不存在 reference: {reference}")

    all_references = {
        path.relative_to(base).as_posix()
        for path in skills_dir.rglob("references/*.md")
    }
    for reference in sorted(all_references - referenced):
        issues.append(f"未被任何 Skill 显式引用的 reference: {reference}")
    return issues


def registry_document(base: Path = BASE) -> dict:
    return {
        "version": "4.0",
        "generated_by": "scripts/skill_registry.py",
        "source": ".agents/skills/**/SKILL.md",
        "skills": build_registry(base),
    }


def export_registry(path: Path = REGISTRY_PATH, base: Path = BASE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(registry_document(base), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Exported registry to {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export", action="store_true", help="重新生成派生注册快照")
    parser.add_argument("--registry", type=Path, default=REGISTRY_PATH)
    args = parser.parse_args()
    if args.export:
        try:
            export_registry(args.registry)
        except ValueError as exc:
            print(f"Issues found: 1\n  - {exc}")
            return 1
        return 0
    if not args.registry.is_file():
        print("Issues found: 1\n  - skill-registry.json 不存在；先运行 --export")
        return 1
    data = json.loads(args.registry.read_text(encoding="utf-8"))
    try:
        issues = validate(data.get("skills", {}))
    except ValueError as exc:
        print(f"Issues found: 1\n  - {exc}")
        return 1
    if issues:
        print(f"Issues found: {len(issues)}")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    entries = data.get("skills", {})
    leaves = sum(entry.get("kind") == "leaf" for entry in entries.values())
    routers = sum(entry.get("kind") == "router" for entry in entries.values())
    print(f"OK: {len(entries)} 个 Skill（{leaves} leaf, {routers} router）均由磁盘契约确定")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
