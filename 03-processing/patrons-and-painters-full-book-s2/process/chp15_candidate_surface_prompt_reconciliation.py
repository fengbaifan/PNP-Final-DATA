#!/usr/bin/env python3
"""Reconcile Chapter 15 candidate-surface prompts against S2 evidence.

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
RESULT = TASK / "results" / "chp-15.md"

EXPECTED_HASHES = {
    "04-knowledge/tables/entity-candidates.csv": "08661d2bd55ac80f82a314a013334e0203cc51d3ab6beda7a4d6a57ba7f73eab",
    "04-knowledge/tables/mentions.csv": "459ecd81f77e97bef006dca8003aba7c3731f66e4fd30a30d93c420c33a10e14",
    "04-knowledge/tables/book-statements.jsonl": "37ec0304b794b839157bfd00996330612a202ff84c96283c53dbb26921205949",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/s2-coverage.csv": "84f8497a7ce0100f4785acd8bf8ed88bb4c69fe5254cd89d172577b0400eb6c1",
    "02-sources/02-Markdown/15_CHP-15_sec_i.md": "798e2903ab45c8a90ac5be9746c43964007426d3b2e2723baa20332665d11624",
    "02-sources/02-Markdown/15_CHP-15_sec_ii.md": "eea847f75c7876dc5b8ea38ef4b64ad30cdd6c629df6a064125ac5f63917d31f",
    "scripts/audit_s2_candidate_surfaces.py": "130b53da86d940daad454079960415ac5e7043e0b71239370b66226158cd1ee2",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "01-domain/stage-artifact-schema.md": "929b8a55f92103de962e8bd509d02d883683b0eea3a9ffe307e5de8229a86abe",
}


def accepted(index: int, candidate_id: str, statement_id: str, note: str) -> dict[str, object]:
    return {"prompt_index": index, "candidate_id": candidate_id, "statement_id": statement_id, "note": note}


ACCEPTED = [
    accepted(1, "cand-11499", "st-chp15-p363-contemporary-praised-villa", "The contemporary quotation identifies a collection of rarities associated with Farsetti's villa; its inventory and relation to his other holdings remain unspecified."),
    accepted(4, "cand-4490", "st-chp15-p366-memmo-urges-friends-for-statues", "Rome is the geographic setting in which Memmo continued urging friends to contribute statues; use the existing Rome place candidate."),
    accepted(5, "cand-10517", "st-chp15-p368-memmo-open-house-until-death", "'This palace' refers back to the Memmo family palace named in the preceding sentence; use its existing place candidate."),
    accepted(6, "cand-2719", "st-chp15-p368-querini-emerges-as-major-venetian-patron", "Venice is the city from which Querini emerged as a major patron; use the geographic place candidate."),
    accepted(8, "cand-2079", "st-chp15-p369-foscarini-victory-querini-arrest", "This is Querini's specific arrest and detention event indexed at p.369; accept the full phrase so the nested generic 'arrest' prompt is not duplicated."),
    accepted(11, "cand-10547", "st-chp15-p370-alticchiero-library-contents", "The phrase names the subject-matter book collection in the Alticchiero library, already recorded as cand-10547."),
    accepted(12, "cand-2081", "st-chp15-p370-garden-allegory-philosophers-way-of-life", "This is the garden indexed under Querini at p.370 and described as part of the Alticchiero estate; retain the index-derived candidate pending S3 identity review."),
    accepted(14, "cand-4302", "st-chp15-p371-grand-duke-monument-sphinx-apollo-relief", "The 'reforming prince' is the unnamed Grand Duke of Tuscany identified immediately before; reuse the same person candidate without inferring his individual identity."),
    accepted(15, "cand-2081", "st-chp15-p371-querini-garden-allegories-straightforward", "The later possessive reference is to the same Querini garden described at p.370; use cand-2081."),
]

NO_WRITE_REASONS = {
    2: "'Portraits' describes a generic genre in which Alessandro Longhi worked, not Schulenburg's indexed portrait group.",
    3: "'Forming a collection there' is a general statement about collecting interest in Venice, not an identified collection or collector.",
    7: "This single-word 'arrest' span is nested within the accepted event phrase 'arrest and detention' at prompt 8; a second mention would overlap the same event wording.",
    9: "'Subject' means the topic of a statue chosen by a donor, not the Contracts index concept.",
    10: "'Churches' is a generic comparison class; no bounded group of pilgrimage churches is identified.",
    13: "'Temperament' is a general quality attributed to Querini, not either unrelated Algarotti index candidate.",
    16: "'Character' refers to the restraint and lack of excess treated as a quality of the sculpture, not Pope Urban VIII.",
}

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-11499",
        "index_entry_id": "",
        "canonical_name": "Collection of rarities associated with Farsetti's villa at S. Maria di Sala (p.363)",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "An unnamed contemporary quoted by Haskell praises a 'collection of rarities' in connection with Farsetti's villa. No inventory or precise boundary is supplied. Do not equate it with the separate indexed collections of casts cand-1005 or paintings cand-1006, with the villa gardens cand-10457, or with the broader collection Daniele later inherited without further evidence.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-15:15_CHP-15_sec_i:l27-36#L28",
    },
]

STATEMENT_REFERENCE_ADDITIONS = {
    "st-chp15-p363-contemporary-praised-villa": ["cand-11499"],
    "st-chp15-p366-memmo-urges-friends-for-statues": ["cand-4490"],
    "st-chp15-p368-memmo-open-house-until-death": ["cand-10517"],
    "st-chp15-p368-querini-emerges-as-major-venetian-patron": ["cand-2719"],
    "st-chp15-p369-foscarini-victory-querini-arrest": ["cand-2079"],
    "st-chp15-p370-alticchiero-library-contents": ["cand-10547"],
    "st-chp15-p370-garden-allegory-philosophers-way-of-life": ["cand-2081"],
    "st-chp15-p371-grand-duke-monument-sphinx-apollo-relief": ["cand-4302"],
    "st-chp15-p371-querini-garden-allegories-straightforward": ["cand-2081"],
}

STATEMENT_CONTENT_PATCHES = {
    "st-chp15-p363-contemporary-praised-villa": {
        "claim": "Haskell quotes an unnamed contemporary praising the villa's splendour, richness, fine taste, collection of rarities, arrangement and Farsetti's magnificence; Haskell says Farsetti was highly thought of in Paris.",
        "qualification": "The quoted speaker is not named in the body. Note 2 cites a Boscovich letter, but it was not independently consulted; the speaker attribution is not upgraded beyond Haskell's citation trail. The rarities collection has no inventory or specified boundary and is not equated with Farsetti's other indexed holdings.",
    },
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
    summary, prompts = surface_audit.audit("chp-15", 6)
    if summary["reviewed_segments_scanned"] != 17 or len(prompts) != 16:
        raise ValueError(f"Chapter 15 prompt surface changed: {summary}")
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
        mention_id = "m-s2-chp15-surface-" + sha256(f"{segment_id}|{start}|{end}|{candidate_id}".encode("utf-8"))[:16]
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
    new_statement_reference_count = 0
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
                new_statement_reference_count += 1
        updates[statement_id] = row

    for statement_id, patch in STATEMENT_CONTENT_PATCHES.items():
        row = updates[statement_id]
        qualifiers = row.setdefault("qualifiers", {})
        for key, value in patch.items():
            qualifiers[key] = value

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
        "new_statement_reference_count": new_statement_reference_count,
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
        "# 第十五章候选表面提示裁决（2026-10-08）",
        "",
        "定位器在17个reviewed/complete段中给出16条提示。逐项核对规范来源、前后文和候选边界后，9条映射、7条不写；扫描只匹配已有候选词形，不代表实体召回率或语义验收。",
        "",
        "新增cand-11499记录匿名当代引文所说的Farsetti别墅‘collection of rarities’，类型、清单和与Farsetti其他藏品的边界均未确定；同时将原有villa评价statement补全为含该引文内容。其余映射复用Rome、Venice、Memmo家族宫殿、Querini被捕事件、Alticchiero书籍集合及Querini花园候选；‘reforming prince’回连到本句前文所述但身份未名的Grand Duke。未新增statement或S6正式关系。",
        "",
        "字符跨度为拼接段文本的零起点、右开区间；行号回到规范来源。索引误撞、泛称、未界定对象和与已接纳跨度重叠的子词不另造mentions。",
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
            candidate = plan["candidates"][candidate_id]
            candidate_name = str(candidate["canonical_name"])
            sub_entry = str(candidate.get("sub_entry", "")).strip()
            if sub_entry:
                candidate_name = f"{candidate_name} — {sub_entry}"
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
        f"- 表格新增：{len(NEW_CANDIDATES)}个候选、{len(plan['planned_mentions'])}条mentions；未新增statement；核对{len(plan['updates'])}条既有statement的候选引用，实际新增{plan['new_statement_reference_count']}个引用，并修订1条claim及限定语。",
        f"- 写后定位器剩余{audit['uncovered_candidate_surface_spans']}条；prompt 7嵌套于已接纳的prompt 8，随完整事件跨度被覆盖。其余提示与no-write裁决逐跨度一致。定位器不证明召回完整。",
        f"- 严格S2审计：errors={audit.get('errors')}; s2_missing={audit.get('s2_missing')}; candidates={audit.get('candidates')}; mentions={audit.get('mentions')}; statements={audit.get('book_statements')}。",
        f"- 关系候选：{audit.get('relation_candidate_count')}条；本批没有新增关系候选或写入S6正式关系。",
        f"- 决策计划SHA-256：{plan['plan_hash']}；脚本SHA-256：{sha256((ROOT / '03-processing/patrons-and-painters-full-book-s2/process/chp15_candidate_surface_prompt_reconciliation.py').read_bytes())}。",
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
    recovery = Path(tempfile.gettempdir()) / f"pnp-s2-chp15-surface-prompts-{datetime.now():%Y%m%d-%H%M%S}"
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
        expected_after = {
            signature for signature in expected_after
            if not any(signature[0] == segment_id and signature[1] < end and signature[2] > start for segment_id, start, end in plan["planned_spans"])
        }
        after_summary, remaining = surface_audit.audit("chp-15", 6)
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
