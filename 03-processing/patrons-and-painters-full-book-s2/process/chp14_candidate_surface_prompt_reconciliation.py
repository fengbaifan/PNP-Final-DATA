#!/usr/bin/env python3
"""Reconcile Chapter 14 candidate-surface prompts against S2 evidence.

The scanner is only a locator. This script applies the reviewed decisions
below after checking that every input still matches the reviewed snapshot.
Default execution is a read-only preflight; pass --apply to write.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_s2_candidate_surfaces as surface_audit  # noqa: E402

TASK = ROOT / "03-processing" / "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
RESULT = TASK / "results" / "chp-14.md"

EXPECTED_HASHES = {
    "04-knowledge/tables/entity-candidates.csv": "14d110c7438e00699a4e9dbeb31c4987ab3475ed8cf756022cb9348bf70af134",
    "04-knowledge/tables/mentions.csv": "c75f88628b6450bcbc54566eb8a21c578fd65e7af2e7fd2e310c0038d55a78ae",
    "04-knowledge/tables/book-statements.jsonl": "435bc84c80d9f49335084155e4231d36e8de62a769e6404d06a94edc951c32ef",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/s2-coverage.csv": "84f8497a7ce0100f4785acd8bf8ed88bb4c69fe5254cd89d172577b0400eb6c1",
    "02-sources/02-Markdown/14_CHP-14_intro.md": "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7",
    "scripts/audit_s2_candidate_surfaces.py": "130b53da86d940daad454079960415ac5e7043e0b71239370b66226158cd1ee2",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "01-domain/stage-artifact-schema.md": "929b8a55f92103de962e8bd509d02d883683b0eea3a9ffe307e5de8229a86abe",
}


def accepted(index: int, candidate_id: str, statement_id: str, note: str) -> dict[str, object]:
    return {"prompt_index": index, "candidate_id": candidate_id, "statement_id": statement_id, "note": note}


ACCEPTED = [
    accepted(1, "cand-11496", "st-chp14-p357-pannini-colour-and-interior-strength", "The phrase refers to Dr Richard Mead's identifiable London art collection; preserve its unspecified holdings and keep its type unresolved."),
    accepted(2, "cand-4490", "st-chp14-p358-piranesi-parallel-and-admiration", "Rome is the geographic location of Piranesi's parallel creations; use the existing Rome place candidate, not the unrelated index phrases 'in Rome'."),
    accepted(5, "cand-11497", "st-chp14-p349-note1-bonomo-paris-letters", "The note identifies a larger Treviso-held correspondence group, within which the separately recorded Paris letters are a subset; keep fonds and boundary unresolved."),
    accepted(7, "cand-2719", "st-chp14-p355-note2-two-works-and-locations", "Venice is the city containing the two named picture locations; use the place candidate, not the topical Venice index entries."),
    accepted(8, "cand-0499", "st-chp14-p357-note7-pesci-letter-and-parma-version", "Canaletto is named as the painter in the possessive phrase; the referenced view is separately identified in the main-text statement."),
    accepted(9, "cand-2719", "st-chp14-p360-note2-biffi-cecilia", "Venice is where Biffi arrived in 1773; use the geographic city candidate."),
    accepted(11, "cand-4129", "st-chp14-p347-leading-position", "'Art patrons' is the social category in Haskell's description of Algarotti; the existing term candidate has the same category meaning."),
    accepted(17, "cand-4288", "st-chp14-p351-old-master-preference-and-modern-art-success", "'Old masters' names the broad art-historical category in the contrast with Algarotti's promotion of modern artists."),
    accepted(20, "cand-11498", "st-chp14-p353-king-prefers-old-masters", "The source identifies Augustus III's collection of old masters as an object he sought to enlarge; its identity in relation to the Dresden royal gallery remains unresolved."),
    accepted(23, "cand-2719", "st-chp14-p355-no-evidence-of-algarotti-canaletto-contact", "Venice is the city of the visit discussed in this statement; use the place candidate."),
]

NO_WRITE_REASONS = {
    3: "'Battle' is a metaphor for conflict between styles, not Salvator Rosa or a titled work.",
    4: "'Winter' describes the season of Constable's evenings and does not identify Rosalba Carriera.",
    6: "'The subject' means the topic of Algarotti's ideas, not the Contracts index concept.",
    10: "'Temperament' is a general personal quality in Haskell's interpretation, not a separately identified person or work.",
    12: "'Artistic tastes' describes Algarotti's critical quality; it is not Joseph Smith or an independently bounded entity.",
    13: "'Temperament' is a general quality attributed to Algarotti, not either person candidate returned by the index matcher.",
    14: "'Receptive character' is a description of Algarotti, not Maffeo Barberini.",
    15: "The scholarly approach is an attributed interpretive quality, not the person candidate's index subentry or a separate work.",
    16: "'Subject' means the generic topic assigned to a history painting, not the Contracts term.",
    18: "The Italian garden is a generic pictorial setting in the sketch, not an independently identified place.",
    19: "This is the same generic garden setting described as absent from the large version; no bounded garden is identified.",
    21: "The 'tradition of Italian painting' is a broad historical characterization; cand-11017 refers to Italian painting as the subject of a specific catalogue, not this tradition.",
    22: "The large number of drawings is an unbounded medium group within the collection; no separate drawing set or individual sheets are identified here.",
    24: "The pronoun 'their' is explicitly unresolved among the p.347 personal/joint collections, the p.355 family collection, or another group; preserve the existing identity question without forcing a mapping.",
}

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-11496",
        "index_entry_id": "",
        "canonical_name": "Dr Richard Mead's collection of paintings seen by Algarotti in London (p.357)",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell says Algarotti had seen paintings by Pannini in Dr Richard Mead's collection in London. No inventory, number, or individual Pannini painting is identified; the collection's scope and relation to any separately described collection remain open.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-14:14_CHP-14_intro:l107-116#L111",
    },
    {
        "candidate_id": "cand-11497",
        "index_entry_id": "",
        "canonical_name": "Large Treviso collection of letters from Francesco Algarotti to Bonomo (p.349 n.1)",
        "index_page_range": "",
        "suggested_type": "archive",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell reports a large collection of letters from Algarotti to his brother Bonomo in the Archivio Comunale in Treviso and says some letters from Paris, November 1734-January 1736, belong to it. Keep this larger correspondence distinct from the Paris-letter subset cand-10259 and repository citation cand-10251; no fonds identifier or full boundary is supplied.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-14:14_CHP-14_intro:l168-220#L174",
    },
    {
        "candidate_id": "cand-11498",
        "index_entry_id": "",
        "canonical_name": "Augustus III's collection of old masters (p.353)",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell says Augustus III was more anxious to increase his collection of old masters than to commission contemporary artists. No inventory or individual holdings are identified; whether this is the collection associated with the Dresden royal gallery candidate cand-10222 or a separately bounded group is unresolved. Keep distinct from the broad term cand-4288 (Old masters).",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-14:14_CHP-14_intro:l63-71#L68",
    },
]

STATEMENT_REFERENCE_ADDITIONS = {
    "st-chp14-p357-pannini-colour-and-interior-strength": ["cand-11496"],
    "st-chp14-p358-piranesi-parallel-and-admiration": ["cand-4490"],
    "st-chp14-p349-note1-bonomo-paris-letters": ["cand-11497"],
    "st-chp14-p355-note2-two-works-and-locations": ["cand-2719"],
    "st-chp14-p357-note7-pesci-letter-and-parma-version": ["cand-0499"],
    "st-chp14-p360-note2-biffi-cecilia": ["cand-2719"],
    "st-chp14-p347-leading-position": ["cand-4129"],
    "st-chp14-p351-old-master-preference-and-modern-art-success": ["cand-4288"],
    "st-chp14-p353-king-prefers-old-masters": ["cand-11498"],
    "st-chp14-p355-no-evidence-of-algarotti-canaletto-contact": ["cand-2719"],
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_hashes() -> None:
    changed = {}
    for relative, expected in EXPECTED_HASHES.items():
        actual = sha256((ROOT / relative).read_bytes())
        if actual != expected:
            changed[relative] = {"expected": expected, "actual": actual}
    if changed:
        raise RuntimeError(f"Locked inputs changed; re-review before writing: {json.dumps(changed, ensure_ascii=False)}")


def read_csv(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    return raw, list(reader.fieldnames or []), list(reader)


def append_csv_rows(raw: bytes, columns: list[str], rows: list[dict[str, object]]) -> bytes:
    if not rows:
        return raw
    eol = "\r\n" if b"\r\n" in raw else "\n"
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=columns, extrasaction="raise", lineterminator=eol)
    for row in rows:
        writer.writerow(row)
    prefix = b"" if raw.endswith((b"\n", b"\r")) else eol.encode("ascii")
    return raw + prefix + buffer.getvalue().encode("utf-8")


def json_bytes(row: dict[str, object]) -> str:
    return json.dumps(row, ensure_ascii=False, separators=(",", ":"))


def statement_output(raw: bytes, updates: dict[str, dict[str, object]]) -> bytes:
    text = raw.decode("utf-8-sig")
    eol = "\r\n" if "\r\n" in text else "\n"
    output = []
    found: set[str] = set()
    for line in text.splitlines():
        row = json.loads(line)
        statement_id = str(row["statement_id"])
        if statement_id in updates:
            output.append(json_bytes(updates[statement_id]))
            found.add(statement_id)
        else:
            output.append(line)
    if found != set(updates):
        raise ValueError(f"Could not update every statement: {sorted(set(updates)-found)}")
    result = eol.join(output) + eol
    if raw.startswith(b"\xef\xbb\xbf"):
        result = "\ufeff" + result
    return result.encode("utf-8")


def build_plan() -> dict[str, object]:
    summary, prompts = surface_audit.audit("chp-14", 6)
    if summary["reviewed_segments_scanned"] != 18 or len(prompts) != 24:
        raise ValueError(f"Chapter 14 prompt surface changed: {summary}")
    prompt_indices = set(range(1, len(prompts) + 1))
    accepted_by_index = {int(row["prompt_index"]): row for row in ACCEPTED}
    if set(accepted_by_index) & set(NO_WRITE_REASONS) or set(accepted_by_index) | set(NO_WRITE_REASONS) != prompt_indices:
        raise ValueError("Accepted and no-write decisions do not form an exact prompt partition")

    candidate_raw, candidate_columns, candidates = read_csv(CANDIDATES)
    mention_raw, mention_columns, existing_mentions = read_csv(MENTIONS)
    statement_raw = STATEMENTS.read_bytes()
    statements = [json.loads(line) for line in statement_raw.decode("utf-8-sig").splitlines() if line.strip()]
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    statement_by_id = {str(row["statement_id"]): row for row in statements}
    if len(candidate_by_id) != len(candidates) or len(statement_by_id) != len(statements):
        raise ValueError("Duplicate candidate or statement IDs in locked inputs")
    if any(row["candidate_id"] in candidate_by_id for row in NEW_CANDIDATES):
        raise ValueError("A new candidate ID already exists")

    segment_by_id = {
        row["segment_id"]: row
        for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line and (row := json.loads(line))
    }
    segment_text = {}
    for segment_id in {str(row["segment_id"]) for row in prompts}:
        segment = segment_by_id[segment_id]
        source_lines = (ROOT / str(segment["source_file"])).read_text(encoding="utf-8-sig").splitlines()
        segment_text[segment_id] = "\n".join(source_lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])

    existing_spans: dict[str, list[tuple[int, int]]] = {}
    for row in existing_mentions:
        existing_spans.setdefault(row["segment_id"], []).append((int(row["start_char"]), int(row["end_char"])))
    prompt_by_index = {i: row for i, row in enumerate(prompts, 1)}
    known_candidate_ids = set(candidate_by_id) | {str(row["candidate_id"]) for row in NEW_CANDIDATES}
    planned_mentions = []
    planned_spans = []
    for index, decision in accepted_by_index.items():
        prompt = prompt_by_index[index]
        segment_id = str(prompt["segment_id"])
        start, end = int(prompt["start_char"]), int(prompt["end_char"])
        surface = str(prompt["surface_form"])
        if segment_text[segment_id][start:end] != surface:
            raise ValueError(f"Prompt span drift at {index}: {prompt}")
        candidate_id = str(decision["candidate_id"])
        statement_id = str(decision["statement_id"])
        if candidate_id not in known_candidate_ids or statement_id not in statement_by_id:
            raise ValueError(f"Unknown candidate or statement in decision {index}: {decision}")
        if any(start < old_end and end > old_start for old_start, old_end in existing_spans.get(segment_id, [])):
            raise ValueError(f"Accepted span overlaps an existing mention: {index} {prompt}")
        if any(segment_id == old_segment and start < old_end and end > old_start for old_segment, old_start, old_end in planned_spans):
            raise ValueError(f"Accepted spans overlap each other: {index} {prompt}")
        mention_id = "m-s2-chp14-surface-" + sha256(f"{segment_id}|{start}|{end}|{candidate_id}".encode("utf-8"))[:16]
        planned_mentions.append({
            "mention_id": mention_id,
            "segment_id": segment_id,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": start,
            "end_char": end,
            "note": str(decision["note"]),
        })
        planned_spans.append((segment_id, start, end))

    updates = {}
    for statement_id, candidate_ids in STATEMENT_REFERENCE_ADDITIONS.items():
        if statement_id not in statement_by_id:
            raise ValueError(f"Statement to update is missing: {statement_id}")
        row = json.loads(json.dumps(statement_by_id[statement_id]))
        mentioned = row.setdefault("qualifiers", {}).setdefault("mentioned_candidate_ids", [])
        for candidate_id in candidate_ids:
            if candidate_id not in known_candidate_ids:
                raise ValueError(f"Unknown candidate reference: {candidate_id}")
            if candidate_id not in mentioned:
                mentioned.append(candidate_id)
        updates[statement_id] = row

    final_statements = dict(statement_by_id)
    final_statements.update(updates)
    for decision in ACCEPTED:
        row = final_statements[str(decision["statement_id"])]
        refs = row.get("qualifiers", {}).get("mentioned_candidate_ids", [])
        if decision["candidate_id"] not in refs:
            raise ValueError(f"Mapped candidate is absent from its linked statement: {decision}")

    mention_ids = {row["mention_id"] for row in existing_mentions}
    if len(mention_ids) != len(existing_mentions):
        raise ValueError("Duplicate mention IDs in locked inputs")
    if any(row["mention_id"] in mention_ids for row in planned_mentions):
        raise ValueError("A planned mention ID already exists")

    outputs = {
        CANDIDATES: append_csv_rows(candidate_raw, candidate_columns, NEW_CANDIDATES),
        MENTIONS: append_csv_rows(mention_raw, mention_columns, planned_mentions),
        STATEMENTS: statement_output(statement_raw, updates),
    }
    plan_content = {
        "scanner_summary": summary,
        "accepted": ACCEPTED,
        "no_write": NO_WRITE_REASONS,
        "new_candidates": NEW_CANDIDATES,
        "statement_updates": updates,
        "mentions": planned_mentions,
    }
    plan_hash = sha256(json.dumps(plan_content, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    return {
        "scanner_summary": summary,
        "prompts": prompts,
        "segment_by_id": segment_by_id,
        "segment_text": segment_text,
        "candidates": candidate_by_id | {str(row["candidate_id"]): row for row in NEW_CANDIDATES},
        "planned_mentions": planned_mentions,
        "planned_spans": planned_spans,
        "updates": updates,
        "plan_hash": plan_hash,
        "before_hashes": {
            "entity-candidates.csv": sha256(candidate_raw),
            "mentions.csv": sha256(mention_raw),
            "book-statements.jsonl": sha256(statement_raw),
        },
        "outputs": outputs,
    }


def render_report(plan: dict[str, object], after_hashes: dict[str, str], recovery: Path, audit: dict[str, object]) -> bytes:
    accepted_by_index = {int(row["prompt_index"]): row for row in ACCEPTED}
    lines = [
        "# 第十四章候选表面提示裁决（2026-10-08）",
        "",
        "定位器在18个reviewed/complete段中给出24条提示。逐项核对规范来源、上下文断言和候选边界后，10条映射、14条不写；定位器只覆盖现有候选词形，不代表实体召回率或语义验收。",
        "",
        "新增3个来源候选：Mead在伦敦的绘画收藏（类型未定）、Treviso保存的Algarotti—Bonomo书信群（archive）及Augustus III扩充的古代大师收藏（类型未定）。前两组的具体边界分别缺少藏品清单和档案fonds信息；第三组与Dresden royal gallery的关系未定。未新增KU、statement或S6正式关系。",
        "",
        "字符跨度为拼接段文本的零起点、右开区间；行号回到规范来源。索引误撞、泛称、未界定媒介组及身份未决的代词不强行写入。",
        "",
        "| 序号 | 来源定位 | 字符跨度 | 提示原文 | 裁决/候选 | 判断依据 |",
        "|---:|---|---:|---|---|---|",
    ]
    for index, prompt in enumerate(plan["prompts"], 1):
        segment_id = str(prompt["segment_id"])
        segment = plan["segment_by_id"][segment_id]
        text = plan["segment_text"][segment_id]
        start, end = int(prompt["start_char"]), int(prompt["end_char"])
        source_line = int(segment["line_start"]) + text[:start].count("\n")
        source_name = Path(str(segment["source_file"])).name
        decision = accepted_by_index.get(index)
        if decision:
            candidate_id = str(decision["candidate_id"])
            candidate_name = str(plan["candidates"][candidate_id]["canonical_name"])
            outcome = f"映射 {candidate_id} ({candidate_name})"
            reason = str(decision["note"])
        else:
            outcome = "不写入"
            reason = NO_WRITE_REASONS[index]
        surface = str(prompt["surface_form"]).replace("|", "\\|").replace("\n", " ")
        reason = reason.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {index} | {source_name}#L{source_line} | {start}:{end} | {surface} | {outcome} | {reason} |")
    lines.extend([
        "",
        "## 写回与核验",
        "",
        f"- 表格新增：{len(NEW_CANDIDATES)}个候选、{len(plan['planned_mentions'])}条mentions；未新增statement，补齐{len(plan['updates'])}条既有statement的候选引用。",
        f"- 写后定位器剩余{audit['uncovered_candidate_surface_spans']}条，与14条no-write裁决逐跨度一致。定位器不证明召回完整。",
        f"- 严格S2审计：errors={audit.get('errors')}; s2_missing={audit.get('s2_missing')}; candidates={audit.get('candidates')}; mentions={audit.get('mentions')}; statements={audit.get('book_statements')}。",
        f"- 关系候选：{audit.get('relation_candidate_count')}条；本批没有写入S6正式关系。",
        f"- 决策计划SHA-256：{plan['plan_hash']}；脚本SHA-256：{sha256((ROOT / '03-processing/patrons-and-painters-full-book-s2/process/chp14_candidate_surface_prompt_reconciliation.py').read_bytes())}。",
        f"- 写前表SHA-256：candidates {plan['before_hashes']['entity-candidates.csv']}；mentions {plan['before_hashes']['mentions.csv']}；statements {plan['before_hashes']['book-statements.jsonl']}。",
        f"- 写后表SHA-256：candidates {after_hashes['entity-candidates.csv']}；mentions {after_hashes['mentions.csv']}；statements {after_hashes['book-statements.jsonl']}。",
        f"- 恢复副本：{recovery}。",
        "",
        "候选提示裁决不取代全书S2交接审计中的未登记实体、重复副本、跨页注释、指代、限定语、候选外键与全部关系候选复核。",
        "",
    ])
    return "\n".join(lines).encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def apply_plan(plan: dict[str, object]) -> dict[str, object]:
    recovery = Path(tempfile.gettempdir()) / f"pnp-s2-chp14-surface-prompts-{datetime.now():%Y%m%d-%H%M%S}"
    recovery.mkdir(parents=True, exist_ok=False)
    for path in plan["outputs"]:
        shutil.copy2(path, recovery / path.name)
    old_result = RESULT.read_bytes() if RESULT.exists() else None
    try:
        for path, data in plan["outputs"].items():
            atomic_write(path, data)
        expected_after = {
            (str(plan["prompts"][index - 1]["segment_id"]), int(plan["prompts"][index - 1]["start_char"]), int(plan["prompts"][index - 1]["end_char"]), str(plan["prompts"][index - 1]["surface_form"]))
            for index in NO_WRITE_REASONS
        }
        after_summary, remaining = surface_audit.audit("chp-14", 6)
        actual_after = {
            (str(hit["segment_id"]), int(hit["start_char"]), int(hit["end_char"]), str(hit["surface_form"]))
            for hit in remaining
        }
        if actual_after != expected_after:
            raise RuntimeError(f"Post-write prompts differ from no-write residue: missing={sorted(expected_after-actual_after)}; extra={sorted(actual_after-expected_after)}; scanner={after_summary}")

        audit_run = subprocess.run(
            [sys.executable, "-X", "utf8", "scripts/audit_tables.py", "--strict-stage"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        strict_audit = json.loads(audit_run.stdout)
        if strict_audit.get("errors") or strict_audit.get("s2_missing"):
            raise RuntimeError(f"Strict S2 audit failed: {strict_audit}")
        strict_audit["relation_candidate_count"] = sum(
            1 for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines()
            if line and json.loads(line).get("qualifiers", {}).get("relation_candidate") is True
        )
        after_hashes = {path.name: sha256(data) for path, data in plan["outputs"].items()}
        report_audit = {**after_summary, **strict_audit}
        atomic_write(RESULT, render_report(plan, after_hashes, recovery, report_audit))
        return {
            "post_write_scanner": after_summary,
            "remaining_prompts_match_no_write_residue": True,
            "strict_audit": strict_audit,
            "after_hashes": after_hashes,
            "recovery_directory": str(recovery),
            "chapter_result": str(RESULT),
        }
    except Exception:
        for path in plan["outputs"]:
            shutil.copy2(recovery / path.name, path)
        if old_result is None:
            RESULT.unlink(missing_ok=True)
        else:
            atomic_write(RESULT, old_result)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the locked, preflighted S2 decisions")
    args = parser.parse_args()
    verify_hashes()
    plan = build_plan()
    print(json.dumps({
        "mode": "apply" if args.apply else "dry-run",
        "scanner": plan["scanner_summary"],
        "accepted_mentions": len(plan["planned_mentions"]),
        "no_write_prompts": len(NO_WRITE_REASONS),
        "new_candidates": [row["candidate_id"] for row in NEW_CANDIDATES],
        "updated_statements": sorted(plan["updates"]),
        "planned_mention_ids": [row["mention_id"] for row in plan["planned_mentions"]],
        "plan_sha256": plan["plan_hash"],
        "before_hashes": plan["before_hashes"],
    }, ensure_ascii=False))
    if not args.apply:
        return 0
    print(json.dumps(apply_plan(plan), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
