"""Shared target-list and JSONL helpers for verification collectors."""

from __future__ import annotations

import json
from pathlib import Path


def resolve(path: Path, root: Path) -> Path:
    return path if path.is_absolute() else root / path


def load_result_targets(path: Path, root: Path, units: Path, checkpoint: int = 0) -> list[Path]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    targets = data.get("targets") if isinstance(data, dict) else None
    if not isinstance(targets, list) or not targets:
        raise ValueError(f"结果文件没有非空 targets：{path}")
    result: list[Path] = []
    for item in targets:
        if not isinstance(item, dict):
            raise ValueError(f"结果文件包含无效 target：{item!r}")
        if checkpoint and item.get("checkpoint") != checkpoint:
            continue
        relative = item.get("unit")
        if not isinstance(relative, str) or not relative.startswith("04-knowledge/units/"):
            raise ValueError(f"结果文件包含无效 KU 路径：{relative!r}")
        target = root / relative
        if not target.is_file() or not target.resolve().is_relative_to(units.resolve()):
            raise ValueError(f"目标 KU 不存在或越界：{relative}")
        result.append(target)
    if not result:
        raise ValueError(f"结果文件在 checkpoint={checkpoint} 下没有目标：{path}")
    return result


def load_evidence_targets(
    paths: list[Path],
    root: Path,
    units: Path,
    blocking_reasons: set[str] | None = None,
) -> list[Path]:
    """Load and de-duplicate KU paths from prior evidence JSONL files.

    This is intentionally a target selector only: historical evidence remains
    immutable, while a new collector run emits a separate retry ledger.
    """
    selected_reasons = blocking_reasons or set()
    result: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        if not path.is_file():
            raise ValueError(f"evidence 文件不存在：{path}")
        for line_number, raw_line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
            if not raw_line.strip():
                continue
            try:
                row = json.loads(raw_line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"evidence JSONL 无效：{path}:{line_number}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"evidence 行不是对象：{path}:{line_number}")
            if selected_reasons and row.get("blocking_reason") not in selected_reasons:
                continue
            relative = row.get("ku_path")
            if not isinstance(relative, str) or not relative.startswith("04-knowledge/units/"):
                raise ValueError(f"evidence 包含无效 KU 路径：{path}:{line_number}: {relative!r}")
            target = root / relative
            if not target.is_file() or not target.resolve().is_relative_to(units.resolve()):
                raise ValueError(f"evidence 目标 KU 不存在或越界：{relative}")
            if relative not in seen:
                seen.add(relative)
                result.append(target)
    if not result:
        reason_text = ", ".join(sorted(selected_reasons)) if selected_reasons else "任意状态"
        raise ValueError(f"evidence 文件中没有符合条件的目标（{reason_text}）")
    return result


def resolve_single_target(name: str, units: Path) -> Path | None:
    target = name if name.endswith(".md") else f"{name}.md"
    for type_dir in sorted(units.iterdir()):
        if not type_dir.is_dir():
            continue
        candidate = type_dir / target
        if candidate.is_file():
            return candidate
    return None


def write_jsonl(rows: list[dict], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )
    temporary.replace(output)
