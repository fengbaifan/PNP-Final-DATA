#!/usr/bin/env python3
"""Route evidence records by risk and optionally invoke the typed apply path.

The runner is intentionally narrow: it parses evidence, classifies records,
writes only non-empty queues, optionally dry-runs/applies L1 records, and can
call the change-aware repository closure once. It does not create knowledge
units, decide claims or relations, generate governance prose, or run Git.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Iterable

import yaml

try:
    from scripts._evidence_policy import classify_evidence, recommended_changes
except ModuleNotFoundError:
    from _evidence_policy import classify_evidence, recommended_changes


BASE = Path(__file__).resolve().parents[1]
DEFAULT_OUT = BASE / "06-runtime" / "automation"
RETIRED_MANIFEST_FIELDS = {
    "candidate_snapshots",
    "source_snapshots",
    "relation_prescreen",
    "governance_draft",
    "gates",
    "write_current_health",
    "git_closeout",
    "resume",
    "state_file",
}


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def resolve_repo_path(raw: str | Path) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else BASE / path


def display_path(path: Path) -> str:
    return path.relative_to(BASE).as_posix() if path.is_relative_to(BASE) else path.as_posix()


def read_batch_manifest(path: Path) -> dict:
    text = path.read_text(encoding="utf-8-sig")
    data = yaml.safe_load(text) if path.suffix.lower() in {".yml", ".yaml"} else json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("batch manifest must be a JSON/YAML object")
    return data


def read_jsonl(path: Path) -> list[dict]:
    entries: list[dict] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            item = json.loads(line)
            if not isinstance(item, dict):
                raise ValueError(f"{display_path(path)}:{line_number} must be a JSON object")
            item["_source_file"] = display_path(path)
            item["_source_line"] = line_number
            entries.append(item)
    return entries


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, entries: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for entry in entries:
            handle.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")


def write_nonempty_queue(out_dir: Path, name: str, entries: list[dict]) -> str | None:
    if not entries:
        return None
    path = out_dir / name
    write_jsonl(path, entries)
    return display_path(path)


def read_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8-sig")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    data = yaml.safe_load(parts[1]) or {}
    return data if isinstance(data, dict) else {}


def is_no_delta_existing_ku(entry: dict) -> bool:
    changes = recommended_changes(entry)
    ku_path = resolve_repo_path(str(entry.get("ku_path") or ""))
    if not changes or not ku_path.is_file():
        return False
    current = read_frontmatter(ku_path)
    return all(current.get(field) == value for field, value in changes.items())


def classify(entry: dict) -> tuple[str, str, list[str]]:
    return classify_evidence(entry, lambda path: resolve_repo_path(path).is_file())


def decorate(entry: dict, risk: str, action: str, reasons: list[str]) -> dict:
    item = dict(entry)
    item.update({"risk_level": risk, "automation_action": action, "automation_reasons": reasons})
    return item


def summarize_automation_reasons(classified: list[dict]) -> dict:
    by_action: Counter[str] = Counter()
    by_risk: Counter[str] = Counter()
    by_reason: Counter[str] = Counter()
    for item in classified:
        by_action[str(item.get("automation_action") or "missing")] += 1
        by_risk[str(item.get("risk_level") or "missing")] += 1
        for reason in item.get("automation_reasons") or []:
            by_reason[str(reason)] += 1
    return {
        "by_action": dict(sorted(by_action.items())),
        "by_risk": dict(sorted(by_risk.items())),
        "by_reason": dict(sorted(by_reason.items())),
    }


def run_verify_apply(mode: str, evidence_path: Path, report_path: Path) -> int:
    command = [sys.executable, str(BASE / "scripts" / "verify_apply_evidence.py"), mode, str(evidence_path)]
    process = subprocess.run(command, cwd=BASE, text=True, capture_output=True)
    report_path.write_text(process.stdout + process.stderr, encoding="utf-8")
    return process.returncode


def run_change_aware_closure() -> dict:
    command = [sys.executable, "scripts/run_sync_closure.py"]
    process = subprocess.run(command, cwd=BASE, text=True, capture_output=True)
    return {
        "command": " ".join(command),
        "returncode": process.returncode,
        "stdout_tail": process.stdout[-4000:],
        "stderr_tail": process.stderr[-4000:],
    }


def merged_config(args: argparse.Namespace) -> dict:
    manifest_path = resolve_repo_path(args.batch_manifest) if args.batch_manifest else None
    manifest = read_batch_manifest(manifest_path) if manifest_path else {}
    evidence = args.evidence or manifest.get("evidence") or []
    if isinstance(evidence, str):
        evidence = [evidence]
    if not evidence:
        raise ValueError("evidence paths are required")
    out_dir_raw = args.out_dir or manifest.get("out_dir")
    out_dir = resolve_repo_path(out_dir_raw) if out_dir_raw else DEFAULT_OUT / now_stamp()
    return {
        "manifest": manifest,
        "manifest_path": manifest_path,
        "evidence": list(evidence),
        "out_dir": out_dir,
        "dry_run_apply": bool(args.dry_run_apply or manifest.get("dry_run_apply")),
        "apply_low_risk": bool(args.apply_low_risk or manifest.get("apply_low_risk")),
        "run_gates": bool(args.run_gates or manifest.get("run_gates")),
        "retired_fields": sorted(RETIRED_MANIFEST_FIELDS.intersection(manifest)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Route evidence and invoke the typed apply path when explicit.")
    parser.add_argument("--batch-manifest", help="JSON/YAML manifest path")
    parser.add_argument("--evidence", nargs="+", help="evidence JSONL path(s)")
    parser.add_argument("--out-dir", help="batch-local output directory")
    parser.add_argument("--dry-run-apply", action="store_true")
    parser.add_argument("--apply-low-risk", action="store_true")
    parser.add_argument("--run-gates", action="store_true", help="run change-aware closure once")
    args = parser.parse_args()

    try:
        config = merged_config(args)
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    if config["apply_low_risk"] and not config["dry_run_apply"]:
        parser.error("--apply-low-risk requires --dry-run-apply")
    if config["apply_low_risk"]:
        parser.error("--apply-low-risk is paused while evidence status moves from card frontmatter to enrichment tables")

    out_dir: Path = config["out_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        entries = [item for raw in config["evidence"] for item in read_jsonl(resolve_repo_path(raw))]
    except Exception as exc:
        write_json(out_dir / "parse-error.json", {"error": str(exc)})
        return 1

    classified: list[dict] = []
    queues: dict[str, list[dict]] = {"apply": [], "no_delta": [], "review": [], "defer": []}
    for entry in entries:
        risk, action, reasons = classify(entry)
        if risk == "L1" and is_no_delta_existing_ku(entry):
            action = "no_delta_existing_ku"
            reasons.append("current_frontmatter_already_matches_recommended_changes")
        item = decorate(entry, risk, action, reasons)
        classified.append(item)
        if risk == "L1" and action == "no_delta_existing_ku":
            queues["no_delta"].append(item)
        elif risk == "L1":
            queues["apply"].append(entry)
        elif risk == "L2":
            queues["review"].append(item)
        else:
            queues["defer"].append(item)

    output_names = {
        "apply": "apply_candidates.jsonl",
        "no_delta": "no_delta_candidates.jsonl",
        "review": "review_queue.jsonl",
        "defer": "defer_queue.jsonl",
    }
    outputs = {
        key: path
        for key, name in output_names.items()
        if (path := write_nonempty_queue(out_dir, name, queues[key])) is not None
    }
    command_results: list[dict] = []
    apply_failed = False
    apply_path = out_dir / output_names["apply"]
    if config["dry_run_apply"] and queues["apply"]:
        report = out_dir / "verify_apply_dry_run.txt"
        returncode = run_verify_apply("--dry-run", apply_path, report)
        command_results.append({"step": "verify_apply_dry_run", "returncode": returncode, "report": display_path(report)})
        apply_failed = returncode != 0
    if config["apply_low_risk"] and queues["apply"] and not apply_failed:
        report = out_dir / "verify_apply_apply.txt"
        returncode = run_verify_apply("--apply", apply_path, report)
        command_results.append({"step": "verify_apply_apply", "returncode": returncode, "report": display_path(report)})
        apply_failed = returncode != 0

    closure_result = run_change_aware_closure() if config["run_gates"] and not apply_failed else None
    counts = {"total": len(entries), **{key: len(value) for key, value in queues.items()}}
    plan = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "policy": ".agents/guards/automation-risk-policy.md",
        "batch_manifest": display_path(config["manifest_path"]) if config["manifest_path"] else None,
        "batch_id": config["manifest"].get("batch_id"),
        "inputs": [display_path(resolve_repo_path(path)) for path in config["evidence"]],
        "retired_manifest_fields_ignored": config["retired_fields"],
        "outputs": outputs,
        "counts": counts,
        "reason_summary": summarize_automation_reasons(classified),
        "items": classified,
        "command_results": command_results,
        "closure_result": closure_result,
    }
    write_json(out_dir / "plan.json", plan)
    failed = apply_failed or bool(closure_result and closure_result["returncode"] != 0)
    print(json.dumps({"out_dir": display_path(out_dir), "counts": counts}, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
