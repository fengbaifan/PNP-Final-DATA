"""生成只读的置信度与证据状态审计队列。

脚本只报告事实与下一跳，不修改 KU，也不自动改变 confidence、consensus、
evidence_status、verification_level 或 source_count。
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
UNITS = ROOT / "04-knowledge" / "units"
RELATION_INDEX = ROOT / "04-knowledge" / "quality" / "relation-index.yml"

LLM_FIRST_TYPES = {"terms", "procedures"}
DIRECT_TYPES = {"persons", "families", "institutions", "places", "works", "archives", "events"}


@dataclass(frozen=True)
class Unit:
    path: Path
    type_name: str
    title: str
    confidence: str
    consensus: str
    source_count: int | None
    evidence_status: str
    verification_level: str
    last_verified: str
    review_due: str
    conflicts: tuple[object, ...]
    source_family: str
    unverified_notes: tuple[str, ...]
    isolated_from_structure_and_relation_graph: bool


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def frontmatter(text: str) -> dict:
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}
    data = yaml.safe_load(match.group(1)) or {}
    return data if isinstance(data, dict) else {}


def status_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if "UNVERIFIED" in line]


def reason_from_lines(lines: list[str]) -> str:
    joined = " ".join(lines).lower()
    if "external" in joined or "api" in joined or "受限" in joined:
        return "external_api_limited"
    if "direct verification" in joined or "直接验证" in joined or "needs direct" in joined:
        return "needs_direct_verification"
    if "no wiki" in joined or "无独立词条" in joined or "wikipedia无" in joined:
        return "no_wiki_page"
    if "internal" in joined or "llm" in joined:
        return "llm_internal_pending"
    return "generic_unverified"


def source_family(text: str) -> str:
    text_lc = text.lower()
    if "patrons and painters" in text_lc or "haskell" in text_lc:
        return "Haskell 1980"
    if "wikipedia" in text_lc:
        return "Wikipedia-derived"
    return "other/unknown"


def recommended_action(type_name: str, reason: str) -> str:
    if reason == "external_api_limited":
        return "retry_verify_when_network_available"
    if type_name in LLM_FIRST_TYPES and reason in {
        "no_wiki_page",
        "generic_unverified",
        "llm_internal_pending",
    }:
        return "llm_internal_semantic_review"
    if type_name in {"persons", "places", "families", "institutions"}:
        return "identity_evidence_collect"
    if type_name in {"works", "archives"}:
        return "bibliographic_direct_verification"
    if type_name == "events":
        return "event_secondary_source_check"
    return "manual_review"


def normalize_date(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, date):
        return value.isoformat()
    return str(value).strip().strip("'\"")


def normalize_source_count(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def collect(paths: list[Path] | None = None) -> list[Unit]:
    units: list[Unit] = []
    candidates = paths if paths is not None else sorted(UNITS.rglob("*.md"))
    connected: set[str] = set()
    if RELATION_INDEX.is_file():
        relation_rows = yaml.safe_load(RELATION_INDEX.read_text(encoding="utf-8")) or []
        if isinstance(relation_rows, list):
            for row in relation_rows:
                if not isinstance(row, dict):
                    continue
                for key in ("source", "target"):
                    value = row.get(key)
                    if isinstance(value, str):
                        normalized_value = value.replace("\\", "/")
                        connected.add(f"04-knowledge/units/{normalized_value}")
    for path in sorted(set(candidates)):
        if not path.is_file() or path.suffix.lower() != ".md":
            raise ValueError(f"KU 路径不存在或不是 Markdown：{path}")
        if not path.resolve().is_relative_to(UNITS.resolve()):
            raise ValueError(f"审计范围越出 04-knowledge/units：{path}")
        text = read_text(path)
        fm = frontmatter(text)
        if not fm:
            raise ValueError(f"缺少可解析 frontmatter：{path}")
        conflicts = fm.get("conflicts")
        if not isinstance(conflicts, list):
            conflicts = [] if conflicts is None or conflicts == "" else [conflicts]
        units.append(
            Unit(
                path=path,
                type_name=path.parent.name,
                title=str(fm.get("title") or path.stem),
                confidence=str(fm.get("confidence") or "").strip(),
                consensus=str(fm.get("consensus") or "").strip(),
                source_count=normalize_source_count(fm.get("source_count")),
                evidence_status=str(fm.get("evidence_status") or "").strip(),
                verification_level=str(fm.get("verification_level") or "").strip(),
                last_verified=normalize_date(fm.get("last_verified")),
                review_due=normalize_date(fm.get("review_due")),
                conflicts=tuple(conflicts),
                source_family=source_family(text),
                unverified_notes=tuple(status_lines(text)),
                isolated_from_structure_and_relation_graph=(
                    path.relative_to(ROOT).as_posix() not in connected
                    and not fm.get("primary_theme")
                    and not fm.get("topic_memberships")
                ),
            )
        )
    return units


def load_result_targets(path: Path) -> list[Path]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    targets = data.get("targets") if isinstance(data, dict) else None
    if not isinstance(targets, list) or not targets:
        raise ValueError(f"结果文件没有非空 targets：{path}")
    result: list[Path] = []
    for item in targets:
        rel = item.get("unit") if isinstance(item, dict) else None
        if not isinstance(rel, str) or not rel.startswith("04-knowledge/units/"):
            raise ValueError(f"结果文件包含无效 KU 路径：{rel!r}")
        result.append(ROOT / rel)
    return result


def assess(unit: Unit, today: date) -> dict:
    reasons: list[str] = []
    conflicts: list[str] = []

    if unit.conflicts:
        conflicts.append("unresolved_conflicts")
    if unit.confidence == "high" and (
        unit.evidence_status == "unverified" or unit.unverified_notes
    ):
        conflicts.append("high_confidence_but_unverified")
    if unit.evidence_status == "externally_verified" and (unit.source_count or 0) < 1:
        conflicts.append("external_status_without_counted_source")

    if unit.source_count is None or unit.source_count == 0:
        reasons.append("zero_or_missing_source_count")
    elif unit.source_count == 1:
        reasons.append("single_source")
    if unit.confidence in {"", "low"}:
        reasons.append("low_or_missing_confidence")
    if unit.consensus in {"", "tentative"}:
        reasons.append("tentative_or_missing_consensus")
    if unit.evidence_status in {"", "unverified"} or unit.unverified_notes:
        reasons.append("unverified_evidence")
    if not unit.verification_level:
        reasons.append("missing_verification_level")
    if unit.review_due:
        try:
            if date.fromisoformat(unit.review_due) < today:
                reasons.append("review_overdue")
        except ValueError:
            conflicts.append("invalid_review_due")
    if not unit.last_verified:
        reasons.append("missing_last_verified")
    if unit.isolated_from_structure_and_relation_graph:
        reasons.append("isolated_from_structure_and_relation_graph")

    if conflicts:
        priority = "P0"
        next_step = "verify"  # identity, evidence and conflict review share one Skill
    elif any(reason in reasons for reason in {"zero_or_missing_source_count", "unverified_evidence", "review_overdue"}):
        priority = "P1"
        next_step = "verify"
    elif reasons:
        priority = "P2"
        next_step = "verify"
    else:
        priority = "P3"
        next_step = "no_action"

    if unit.unverified_notes:
        reason_detail = reason_from_lines(list(unit.unverified_notes))
        next_step = recommended_action(unit.type_name, reason_detail)
    else:
        reason_detail = ""

    return {
        "unit": unit.path.relative_to(ROOT).as_posix(),
        "title": unit.title,
        "type": unit.type_name,
        "priority": priority,
        "reasons": reasons,
        "status_conflicts": conflicts,
        "next_step": next_step,
        "unverified_reason_detail": reason_detail,
        "source_family": unit.source_family,
        "source_count": unit.source_count,
        "confidence": unit.confidence or None,
        "consensus": unit.consensus or None,
        "evidence_status": unit.evidence_status or None,
        "verification_level": unit.verification_level or None,
        "last_verified": unit.last_verified or None,
        "review_due": unit.review_due or None,
    }


def write_jsonl(rows: list[dict], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def write_summary(rows: list[dict], output: Path, scope: str) -> None:
    priorities = Counter(row["priority"] for row in rows)
    reasons = Counter(reason for row in rows for reason in row["reasons"])
    conflicts = Counter(reason for row in rows for reason in row["status_conflicts"])
    lines = [
        "# 置信度与证据状态审计",
        "",
        f"- 审查范围：{scope}",
        f"- 审查对象：{len(rows)}",
        f"- 优先级：P0={priorities['P0']}，P1={priorities['P1']}，P2={priorities['P2']}，P3={priorities['P3']}",
        "- 状态边界：本审计未修改任何 KU 或状态字段。",
        "",
        "## 原因分布",
        "",
        "| 原因 | 数量 |",
        "|---|---:|",
    ]
    for key, count in sorted(reasons.items()):
        lines.append(f"| `{key}` | {count} |")
    if conflicts:
        lines.extend(["", "## 状态冲突", "", "| 冲突 | 数量 |", "|---|---:|"])
        for key, count in sorted(conflicts.items()):
            lines.append(f"| `{key}` | {count} |")
    lines.extend(
        [
            "",
            "## 边界",
            "",
            "- 单来源、到期或字段缺失只产生复核信号，不自动降级或晋升。",
            "- Topic membership 是组织关系，不是新的独立证据。",
        ]
    )
    isolated_count = reasons["isolated_from_structure_and_relation_graph"]
    if isolated_count:
        lines.append(
            f"- 关系图孤立性只表示对象同时缺少 relation、primary_theme 与 topic_memberships；"
            f"本次识别 {isolated_count} 个，不等同于知识错误。"
        )
    else:
        lines.append("- 本次范围未发现同时缺少 relation、primary_theme 与 topic_memberships 的对象。")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-result", type=Path, help="仅审计结果 JSON 的 targets")
    parser.add_argument("--output", type=Path, required=True, help="JSONL 队列输出路径")
    parser.add_argument("--summary-output", type=Path, help="可选 Markdown 摘要输出路径")
    args = parser.parse_args()

    input_result = None
    if args.input_result:
        input_result = args.input_result if args.input_result.is_absolute() else ROOT / args.input_result
    output = args.output if args.output.is_absolute() else ROOT / args.output
    summary_output = None
    if args.summary_output:
        summary_output = args.summary_output if args.summary_output.is_absolute() else ROOT / args.summary_output

    paths = load_result_targets(input_result) if input_result else None
    units = collect(paths)
    rows = [assess(unit, date.today()) for unit in units]
    rank = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    rows.sort(key=lambda row: (rank[row["priority"]], row["unit"]))
    write_jsonl(rows, output)
    scope = input_result.relative_to(ROOT).as_posix() if input_result else "04-knowledge/units/**/*.md"
    if summary_output:
        write_summary(rows, summary_output, scope)

    priorities = Counter(row["priority"] for row in rows)
    print(f"queue={output.relative_to(ROOT) if output.is_relative_to(ROOT) else output}")
    print(f"total={len(rows)}")
    for key in ("P0", "P1", "P2", "P3"):
        print(f"{key}={priorities[key]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
