#!/usr/bin/env python3
from pathlib import Path
import json
import sys
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.audit_repo import build_results
from scripts.audit_content_quality import get_content_quality_summary


def write_health_snapshot(
    path: Path,
    results: dict,
    *,
    now: str | None = None,
) -> dict:
    """Write a health snapshot while preserving its timestamp when data is unchanged."""
    previous: dict = {}
    if path.exists():
        try:
            previous = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            previous = {}

    current_payload = {key: value for key, value in results.items() if key != "timestamp"}
    previous_payload = {key: value for key, value in previous.items() if key != "timestamp"}
    if previous and previous_payload == current_payload:
        timestamp = previous.get("timestamp")
    else:
        timestamp = now or datetime.now().isoformat(timespec="seconds")

    snapshot = {"timestamp": timestamp, **current_payload}
    rendered = json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n"
    if not path.exists() or path.read_text(encoding="utf-8") != rendered:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
    return snapshot


def main():
    results = build_results(ROOT)
    try:
        content_quality = get_content_quality_summary()
        results["content_quality"] = content_quality
        cq_findings = content_quality.get("total_findings", 0)
        print(f"content_quality_findings={cq_findings}")
    except Exception as e:
        print(f"content_quality_audit_skipped: {e}", file=sys.stderr)
        results["content_quality"] = {"error": str(e)}
    out = ROOT / "06-runtime" / "state" / "current-health.json"
    results = write_health_snapshot(out, results)
    print(f"wrote={out}")
    structural_health = results.get('structural_health', {}).get('total', '?')
    drift_count = results.get('rule_drift', {}).get('findings', 0)
    print(f"structural_health={structural_health}")
    if drift_count > 0:
        print(f"rule_drift_findings={drift_count} (规则文档与磁盘事实不一致)")

    # ── 自动同步 governance backlog ──
    # health 刷新后必须同步 backlog，防止两份状态产物发散
    try:
        from scripts.generate_governance_backlog import main as generate_backlog
        generate_backlog()
    except Exception as e:
        print(f"governance_backlog_sync_skipped: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
