#!/usr/bin/env python3
"""对已审查 evidence JSONL 执行预检、dry-run 或原子写回。

collect 与 apply 严格分离。正式 apply 会先在内存中完成整批预检，只有全部记录
可写时才同时提交 KU 和 verification log；任何失败都会回滚已替换的文件。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from _runtime_state import RuntimeState, check_resumable

try:
    from scripts._evidence_policy import validate_evidence_schema, validate_recommended_changes
except ModuleNotFoundError:
    from _evidence_policy import validate_evidence_schema, validate_recommended_changes


BASE = Path(__file__).resolve().parents[1]
VERIFICATION_LOG = BASE / "04-knowledge" / "quality" / "verification-log.md"
EVIDENCE_FIELDS = ("evidence_status", "verification_level", "confidence", "consensus")
SAFE_CONFIDENCE = {"medium", "low"}
FRONTMATTER_RE = re.compile(r"^\ufeff?---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
VERIFY_SECTION_RE = re.compile(r"^## 验证状态[ \t]*\n.*?(?=^##[ \t]+|^---[ \t]*$|\Z)", re.MULTILINE | re.DOTALL)
EVIDENCE_SECTION_RE = re.compile(r"^## 关系与证据[ \t]*$", re.MULTILINE)
NESTED_VERIFY_RE = re.compile(r"^### 验证状态[ \t]*\n.*?(?=^#{1,3}[ \t]+|\Z)", re.MULTILINE | re.DOTALL)


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(errors="replace")


class NullRunState:
    """未显式提供批次状态文件时使用的无写入适配器。"""

    def __getattr__(self, _name):
        return lambda *args, **kwargs: None

    def get_processed_items(self) -> set[str]:
        return set()

    def get_progress_index(self) -> int:
        return -1


@dataclass(frozen=True)
class PlannedEntry:
    entry: dict
    ku_path: Path
    relative_path: str
    new_text: str
    outcome: str
    detail: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_frontmatter(text: str) -> str:
    match = FRONTMATTER_RE.search(text)
    return match.group(1).strip("\n") if match else ""


def scalar_fm(fm: str, field: str) -> str:
    match = re.search(rf"^{re.escape(field)}\s*:\s*(.+?)\s*$", fm, re.MULTILINE)
    return match.group(1).strip().strip('"').strip("'") if match else ""


def validate_changes(changes: dict, entry: dict) -> list[str]:
    return validate_recommended_changes(changes, entry)


def _set_frontmatter_scalar(frontmatter: str, field: str, value: object) -> str:
    rendered = str(value)
    if re.search(rf"^{re.escape(field)}\s*:", frontmatter, re.MULTILINE):
        return re.sub(
            rf"^{re.escape(field)}\s*:\s*.*?$",
            f"{field}: {rendered}",
            frontmatter,
            flags=re.MULTILINE,
        )
    return frontmatter.rstrip() + f"\n{field}: {rendered}"


def _upsert_verification_section(body: str, section: str) -> str:
    """Keep machine verification under the third part; preserve unrelated content."""
    if len(VERIFY_SECTION_RE.findall(body)) > 1 or len(EVIDENCE_SECTION_RE.findall(body)) > 1:
        raise ValueError("ambiguous duplicate verification/evidence sections")
    body = VERIFY_SECTION_RE.sub("", body)
    evidence = EVIDENCE_SECTION_RE.search(body)
    if evidence is None:
        return body.rstrip("\n") + "\n\n## 关系与证据\n\n" + section + "\n"
    following = re.search(r"^#{1,2}[ \t]+", body[evidence.end():], re.MULTILINE)
    end = evidence.end() + following.start() if following else len(body)
    contents = body[evidence.end():end]
    if len(NESTED_VERIFY_RE.findall(contents)) > 1:
        raise ValueError("ambiguous duplicate nested verification sections")
    if NESTED_VERIFY_RE.search(contents):
        contents = NESTED_VERIFY_RE.sub(lambda _: section + "\n", contents)
    else:
        contents = contents.rstrip("\n") + "\n\n" + section + "\n"
    return body[:evidence.end()] + contents + body[end:]


def _render_entry(entry: dict, current_text: str) -> tuple[str | None, str, str]:
    issues = validate_evidence_schema(entry)
    if issues:
        return None, "blocked", "; ".join(issues)
    frontmatter = extract_frontmatter(current_text)
    if not frontmatter:
        return None, "blocked", "no frontmatter"
    changes = entry.get("recommended_changes") or {}
    if not changes:
        return None, "blocked", "no recommended changes"
    warnings = validate_changes(changes, entry)
    if warnings:
        return None, "blocked", "; ".join(warnings)

    new_frontmatter = frontmatter
    details: list[str] = []
    for field in EVIDENCE_FIELDS:
        value = changes.get(field)
        if value is None:
            continue
        if field == "confidence" and value not in SAFE_CONFIDENCE:
            value = "medium"
        existing = scalar_fm(new_frontmatter, field)
        if field == "confidence" and existing == "high" and value != "high":
            details.append(f"protected {field}=high")
            continue
        if field == "consensus" and existing == "confirmed" and value != "confirmed":
            details.append(f"protected {field}=confirmed")
            continue
        new_frontmatter = _set_frontmatter_scalar(new_frontmatter, field, value)
        details.append(f"{field}:{existing or '<missing>'}->{value}")

    today = datetime.now(timezone.utc).date().isoformat()
    new_frontmatter = _set_frontmatter_scalar(new_frontmatter, "last_verified", today)
    new_frontmatter = _set_frontmatter_scalar(new_frontmatter, "updated", today)
    version_match = re.search(r"^version:\s*(\d+)", new_frontmatter, re.MULTILINE)
    if version_match:
        new_frontmatter = _set_frontmatter_scalar(new_frontmatter, "version", int(version_match.group(1)) + 1)

    match = FRONTMATTER_RE.search(current_text.replace("\r\n", "\n"))
    if match is None:
        return None, "blocked", "no frontmatter"
    body = current_text.replace("\r\n", "\n")[match.end():]
    section = (
        "### 验证状态\n\n"
        f"- **证据状态**: {changes.get('evidence_status', scalar_fm(new_frontmatter, 'evidence_status'))}\n"
        f"- **验证层级**: {changes.get('verification_level', scalar_fm(new_frontmatter, 'verification_level'))}\n"
        f"- **验证平台**: {entry.get('platform', 'N/A')}\n"
        f"- **匹配质量**: {entry.get('match_quality', 'N/A')}\n"
        f"- **验证日期**: {today}\n"
        f"- **证据范围**: {entry.get('claim_scope', 'N/A')}\n"
    )
    if entry.get("url"):
        section += f"- **来源URL**: {entry['url']}\n"
    if entry.get("notes"):
        section += f"- **说明**: {entry['notes']}\n"
    try:
        body = _upsert_verification_section(body, section)
    except ValueError as exc:
        return None, "blocked", str(exc)
    new_text = f"---\n{new_frontmatter}\n---\n{body}"
    outcome = "no_delta" if new_text == current_text else "applied"
    return new_text, outcome, ", ".join(details) or "metadata refreshed"


def apply_one(entry: dict, dry_run: bool = True) -> list[str]:
    """兼容单条调用；正式批次写回由 main 的原子事务负责。"""
    relative = str(entry.get("ku_path") or "")
    path = BASE / relative
    if not path.is_file():
        return [f"BLOCKED: missing: {relative}"]
    new_text, outcome, detail = _render_entry(entry, read_text(path))
    if new_text is None:
        return [f"BLOCKED: {relative}: {detail}"]
    if not dry_run:
        _atomic_commit({path: new_text})
    return [f"{outcome.upper()}: {relative}: {detail}"]


def _read_evidence(path: Path) -> list[dict]:
    entries: list[dict] = []
    with path.open(encoding="utf-8-sig") as handle:
        for number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            item = json.loads(line)
            if not isinstance(item, dict):
                raise ValueError(f"evidence line {number} must be an object")
            entries.append(item)
    return entries


def _input_fingerprint(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    return f"sha256:{digest}"


def _apply_independence_flags(entries: list[dict]) -> int:
    """仅显式 independence group 可支持第二独立来源判定。"""
    groups: dict[str, list[dict]] = {}
    for entry in entries:
        key = f"{entry.get('ku_path', '?')}|{entry.get('claim_target', '?')}"
        groups.setdefault(key, []).append(entry)
    changed = 0
    for group in groups.values():
        eligible = [
            entry
            for entry in group
            if entry.get("match_quality") in {"strong", "medium"}
            and not entry.get("blocking_reason")
            and not entry.get("conflicting_fields")
            and entry.get("source_independence_group")
        ]
        independence_groups = {entry["source_independence_group"] for entry in eligible}
        if len(independence_groups) < 2:
            continue
        for entry in eligible:
            entry["second_source_confirmed"] = True
            changed += 1
    return changed


def _evidence_id(entry: dict, evidence_file: str) -> str:
    if entry.get("evidence_id"):
        return str(entry["evidence_id"])
    seed = json.dumps(
        {
            "file": evidence_file,
            "ku_path": entry.get("ku_path"),
            "claim_target": entry.get("claim_target"),
            "url": entry.get("url"),
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return "ev-" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]


def _verification_log_text(plans: list[PlannedEntry], evidence_file: str) -> str:
    if VERIFICATION_LOG.is_file():
        current = read_text(VERIFICATION_LOG).rstrip() + "\n"
    else:
        current = (
            "---\n"
            "title: 验证日志\n"
            "type: meta\n"
            "sub_type: verification-log\n"
            "---\n\n"
            "# 验证日志\n\n"
            "> 只记录成功提交的 evidence 写回；阻断和失败留在工作包状态与 summary。\n\n"
            "| timestamp | evidence_id | target | claim_scope | verification_level | outcome | reviewer | evidence_file |\n"
            "|---|---|---|---|---|---|---|---|\n"
        )
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = []
    for plan in plans:
        entry = plan.entry
        level = (entry.get("recommended_changes") or {}).get("verification_level", "")
        rows.append(
            "| "
            + " | ".join(
                str(value).replace("|", "\\|")
                for value in (
                    timestamp,
                    _evidence_id(entry, evidence_file),
                    plan.relative_path,
                    entry.get("claim_scope", ""),
                    level,
                    plan.outcome,
                    entry.get("reviewer") or "agent-approved-evidence",
                    evidence_file,
                )
            )
            + " |"
        )
    return current + "\n".join(rows) + ("\n" if rows else "")


def _atomic_commit(planned_texts: dict[Path, str]) -> None:
    originals = {path: path.read_bytes() if path.exists() else None for path in planned_texts}
    temporary_paths: list[Path] = []
    replaced: list[Path] = []
    try:
        for index, (path, text) in enumerate(planned_texts.items()):
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_name(f".{path.name}.verify-{os.getpid()}-{index}.tmp")
            temporary.write_text(text, encoding="utf-8")
            temporary_paths.append(temporary)
        for temporary, path in zip(temporary_paths, planned_texts):
            temporary.replace(path)
            replaced.append(path)
    except OSError:
        for path in reversed(replaced):
            original = originals[path]
            if original is None:
                path.unlink(missing_ok=True)
            else:
                rollback = path.with_name(f".{path.name}.rollback-{os.getpid()}.tmp")
                rollback.write_bytes(original)
                rollback.replace(path)
        raise
    finally:
        for temporary in temporary_paths:
            temporary.unlink(missing_ok=True)


def _plan(entries: list[dict], processed: set[str]) -> tuple[list[PlannedEntry], list[str]]:
    planned_texts: dict[Path, str] = {}
    plans: list[PlannedEntry] = []
    blocked: list[str] = []
    for index, entry in enumerate(entries):
        relative = str(entry.get("ku_path") or "")
        item_id = str(entry.get("evidence_id") or relative or index)
        if item_id in processed:
            continue
        path = BASE / relative
        if not relative or not path.is_file():
            blocked.append(f"{item_id}: missing KU {relative!r}")
            continue
        current = planned_texts.get(path, read_text(path))
        new_text, outcome, detail = _render_entry(entry, current)
        if new_text is None:
            blocked.append(f"{item_id}: {detail}")
            continue
        planned_texts[path] = new_text
        plans.append(PlannedEntry(entry, path, relative, new_text, outcome, detail))
    return plans, blocked


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="整批预检，不写文件")
    mode.add_argument("--apply", action="store_true", help="预检通过后原子写回")
    mode.add_argument("--resume", action="store_true", help="核对输入指纹后恢复正式写回")
    parser.add_argument("--state-file", help="批次内 runner-state.json；--resume 时必填")
    parser.add_argument("--batch-id", help="新建状态文件时使用的 work package ID")
    parser.add_argument("evidence_file", help="evidence JSONL 文件")
    args = parser.parse_args()

    if args.resume and not args.state_file:
        parser.error("--resume requires --state-file")
    if args.dry_run and args.state_file:
        parser.error("--dry-run does not write runtime state")

    evidence_path = Path(args.evidence_file)
    if not evidence_path.is_absolute():
        evidence_path = BASE / evidence_path
    if not evidence_path.is_file():
        print(f"文件不存在: {evidence_path}", file=sys.stderr)
        return 1
    try:
        entries = _read_evidence(evidence_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"证据文件无效: {exc}", file=sys.stderr)
        return 1
    fingerprint = _input_fingerprint(evidence_path)
    _apply_independence_flags(entries)

    run_state: RuntimeState | NullRunState
    if args.state_file:
        state_path = Path(args.state_file)
        if not state_path.is_absolute():
            state_path = BASE / state_path
        if args.resume:
            try:
                resumable = check_resumable(
                    state_path,
                    expected_input_fingerprint=fingerprint,
                )
                if resumable is None:
                    print("无可恢复的批次状态", file=sys.stderr)
                    return 1
                run_state = RuntimeState(state_path=state_path)
                run_state.resume(fingerprint, "verify_apply")
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                print(f"恢复被拒绝: {exc}", file=sys.stderr)
                return 1
        else:
            batch_id = args.batch_id or state_path.parent.name
            try:
                run_state = RuntimeState(
                    state_path=state_path,
                    batch_id=batch_id,
                    input_fingerprint=fingerprint,
                )
                run_state.start("verify_apply")
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                print(f"状态初始化失败: {exc}", file=sys.stderr)
                return 1
    else:
        run_state = NullRunState()

    plans, blocked = _plan(entries, run_state.get_processed_items())
    print(f"[{'DRY RUN' if args.dry_run else 'APPLY'}] evidence={len(entries)} planned={len(plans)} blocked={len(blocked)}")
    for plan in plans:
        print(f"  {plan.outcome.upper()}: {plan.relative_path}: {plan.detail}")
    for issue in blocked:
        print(f"  BLOCKED: {issue}", file=sys.stderr)
    if blocked:
        run_state.fail("verify_apply", "; ".join(blocked), blocked=True)
        return 1
    if args.dry_run:
        return 0

    planned_texts: dict[Path, str] = {}
    for plan in plans:
        planned_texts[plan.ku_path] = plan.new_text
    if plans:
        planned_texts[VERIFICATION_LOG] = _verification_log_text(plans, args.evidence_file)
    try:
        _atomic_commit(planned_texts)
    except OSError as exc:
        run_state.fail("verify_apply", str(exc))
        print(f"写回失败且已回滚: {exc}", file=sys.stderr)
        return 1
    for index, plan in enumerate(plans):
        item_id = str(plan.entry.get("evidence_id") or plan.relative_path)
        run_state.track_progress(index, item_id, True)
    run_state.checkpoint("apply_committed")
    run_state.complete("verify_apply")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
