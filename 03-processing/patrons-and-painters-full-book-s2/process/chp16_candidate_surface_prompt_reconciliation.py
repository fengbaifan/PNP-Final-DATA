#!/usr/bin/env python3
"""Reconcile Chapter 16 candidate-surface prompts against S2 evidence.

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
RESULT = TASK / "results" / "chp-16.md"

EXPECTED_HASHES = {
    "04-knowledge/tables/entity-candidates.csv": "78266078cf48f1ade43e79bcdb4378334328a3a7c29fad61680803e7a4e3653f",
    "04-knowledge/tables/mentions.csv": "87aaea0cffe74f7b3057595911a11e954484b8ee292d6d330348a7d823c40a7e",
    "04-knowledge/tables/book-statements.jsonl": "6f4769d0af0d52a375af1d0ee979a9c23d5accf147db2252ba57580b33b1b203",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/s2-coverage.csv": "84f8497a7ce0100f4785acd8bf8ed88bb4c69fe5254cd89d172577b0400eb6c1",
    "02-sources/02-Markdown/16_CHP-16_intro.md": "ee8516e7868b0036a753da731e10a7e201faafa45314615b45ae024c6c7507ff",
    "scripts/audit_s2_candidate_surfaces.py": "130b53da86d940daad454079960415ac5e7043e0b71239370b66226158cd1ee2",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "01-domain/stage-artifact-schema.md": "929b8a55f92103de962e8bd509d02d883683b0eea3a9ffe307e5de8229a86abe",
}


def accepted(index: int, candidate_id: str, statement_id: str, note: str, mention_form: str | None = None) -> dict[str, object]:
    return {
        "prompt_index": index,
        "candidate_id": candidate_id,
        "statement_id": statement_id,
        "note": note,
        "mention_form": mention_form,
    }


ACCEPTED = [
    accepted(
        1,
        "cand-10611",
        "st-chp16-p374-strange-drawing-instructions-via-sasso",
        "The request concerns the specifically described unidentified Guardi drawings Strange wanted clear, finished, paired, and accurately coloured; it is not Carracci's index subentry.",
    ),
    accepted(
        2,
        "cand-11500",
        "st-chp16-p374-sasso-posthumous-collection-partial",
        "The exact count identifies a bounded group in Sasso's collection auctioned in 1803. No makers, titles, or present locations are supplied.",
        "100 drawings",
    ),
    accepted(
        3,
        "cand-1674",
        "st-chp16-p374-sasso-posthumous-collection-partial",
        "Here modelli names the art-object category in Sasso's collection; reuse the indexed Modelli term, not the Andrea Sacchi index subentry.",
    ),
    accepted(
        4,
        "cand-11501",
        "st-chp16-p375-sasso-collection-list-completion",
        "The catalogue-list context identifies a distinct group of drawings and sketches by two named makers in Sasso's auctioned collection. Its count and individual works remain unspecified.",
        "drawings and sketches",
    ),
    accepted(
        5,
        "cand-10628",
        "st-chp16-p375-sasso-collection-list-completion",
        "The source's full phrase identifies the already registered combined group of one Guardi painting and seven Guardi drawings.",
        "seven drawings",
    ),
    accepted(
        8,
        "cand-11502",
        "st-chp16-p376-toninotto-collection-similar-taste",
        "His collection refers to Toninotto's art collection described in the following inventory; it is not Cardinal Borghese's collection index subentry.",
    ),
]

NO_WRITE_REASONS = {
    6: "Many drawings and paintings by four artists is an uncounted, unbounded plural description; the named artists and Haskell's collection statement are already represented.",
    7: "Capricious bust portraits describes a popular genre, not Schulenburg's indexed portrait group or a separately identified set.",
    9: "Similar collection and patronage is a group-level comparison, not an independently identified collection.",
    10: "Own collection is a possessive reference within the existing claim about the Tiepolo letter; it does not identify a separately bounded collection. The letter's reported provenance is already recorded.",
    11: "Prints and drawings is an unenumerated group in the note. The two 1805 Richardson auctions and Haskell's statement are already represented; no separate work group is identified.",
}

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-11500",
        "index_entry_id": "",
        "canonical_name": "One hundred unidentified drawings in Giammaria Sasso's posthumous collection",
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell lists 100 drawings among the contents of Sasso's personal collection, which was auctioned after his death in 1803. Individual makers, titles, and present locations are not supplied; keep this count-defined group distinct from the other listed objects.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-16:16_CHP-16_intro:l16-22#L22",
    },
    {
        "candidate_id": "cand-11501",
        "index_entry_id": "",
        "canonical_name": "Drawings and sketches by Canaletto and Carlevarijs in Giammaria Sasso's auctioned collection",
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell's continuation of the Sasso auction-collection list names drawings and sketches by Canaletto and Carlevarijs. No count, titles, or present locations are supplied. Keep this maker-defined group distinct from the 100 drawings cand-11500 and the one-painting-plus-seven-Guardi-drawings group cand-10628.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-16:16_CHP-16_intro:l24-36#L25",
    },
    {
        "candidate_id": "cand-11502",
        "index_entry_id": "",
        "canonical_name": "Giuseppe Toninotto's art collection",
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell explicitly refers to Toninotto's collection and describes its taste and contents, including old masters, modelli, works by Pietro della Vecchia, Flemish paintings, Venetian views, and separately counted Zais and Guardi groups. The passage does not provide a complete inventory; retain the individually described work groups as distinct candidates.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-16:16_CHP-16_intro:l38-46#L44",
    },
]

CANDIDATE_DETAIL_PATCHES = {
    "cand-10598": {
        "expected_detail": "Haskell describes Sasso setting aside a small private collection alongside his dealing; its contents and later fate are not yet processed here.",
        "detail": "Haskell describes Sasso setting aside a small private collection alongside his dealing. On pp.374–375 he also reports that the collection Sasso made for himself was auctioned after his death in 1803 and lists some contents. The full inventory is not supplied, and the sale catalogue was not independently consulted.",
    },
}

STATEMENT_REFERENCE_ADDITIONS = {
    "st-chp16-p374-sasso-posthumous-collection-partial": ["cand-11500", "cand-1674"],
    "st-chp16-p375-sasso-collection-list-completion": ["cand-11501"],
    "st-chp16-p376-toninotto-attributed-old-masters": ["cand-11502"],
    "st-chp16-p376-toninotto-mixed-collection": ["cand-11502"],
}

STATEMENT_TOP_LEVEL_PATCHES = {
    "st-chp16-p376-toninotto-attributed-old-masters": {"subject_candidate_id": "cand-11502"},
    "st-chp16-p376-toninotto-mixed-collection": {"subject_candidate_id": "cand-11502"},
}

NEW_STATEMENTS = [
    {
        "statement_id": "st-chp16-p376-toninotto-collection-similar-taste",
        "segment_id": "chp-16:16_CHP-16_intro:l38-46",
        "subject_candidate_id": "cand-11502",
        "object_candidate_id": None,
        "predicate": "collection_showed_similar_taste_to_preceding_collectors",
        "qualifiers": {
            "source_line_start": 44,
            "source_line_end": 44,
            "printed_page": 376,
            "pdf_physical_page": 4,
            "claim": "Haskell says Toninotto's collection showed a similar taste to those previously discussed.",
            "speaker": "Haskell",
            "text_layer": "authorial report",
            "qualification": "This is Haskell's broad comparison; this sentence does not identify a complete inventory or particular works.",
            "mentioned_candidate_ids": ["cand-11502", "cand-2643"],
            "ocr_corrections": [],
        },
        "original_quote": "And his collection shows a similar taste to those that have already been investigated.",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md",
    },
]

INSERT_NEW_STATEMENTS_AFTER = "st-chp16-p376-toninotto-del-pian-prints-after-carpaccio"


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
    eol = b"\r\n" if b"\r\n" in raw else b"\n"
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=columns, extrasaction="raise", lineterminator=eol.decode("ascii"))
    for row in rows:
        writer.writerow(row)
    prefix = b"" if raw.endswith((b"\n", b"\r")) else eol
    return raw + prefix + buffer.getvalue().encode("utf-8")


def patch_csv_row(
    raw: bytes,
    columns: list[str],
    rows: list[dict[str, str]],
    key: str,
    identifier: str,
    patch: dict[str, str],
) -> tuple[bytes, dict[str, str]]:
    text = raw.decode("utf-8-sig")
    lines = text.splitlines(keepends=True)
    if len(lines) != len(rows) + 1:
        raise ValueError("CSV records span physical lines; refusing a lossy row patch")
    matches = [index for index, row in enumerate(rows, start=1) if row.get(key) == identifier]
    if len(matches) != 1:
        raise ValueError(f"Expected one {key}={identifier}, found {len(matches)}")
    index = matches[0]
    updated = dict(rows[index - 1])
    updated.update(patch)
    buffer = io.StringIO(newline="")
    csv.DictWriter(buffer, fieldnames=columns, extrasaction="raise", lineterminator="\n").writerow(updated)
    old_line = lines[index]
    eol = "\r\n" if old_line.endswith("\r\n") else "\n" if old_line.endswith("\n") else "\r" if old_line.endswith("\r") else ""
    lines[index] = buffer.getvalue().rstrip("\r\n") + eol
    output = "".join(lines)
    if raw.startswith(b"\xef\xbb\xbf"):
        output = "\ufeff" + output
    return output.encode("utf-8"), updated


def json_bytes(row: dict[str, object]) -> str:
    return json.dumps(row, ensure_ascii=False, separators=(",", ":"))


def statement_output(raw: bytes, updates: dict[str, dict[str, object]]) -> bytes:
    text = raw.decode("utf-8-sig")
    eol = "\r\n" if "\r\n" in text else "\n"
    output = []
    found: set[str] = set()
    inserted = False
    for line in text.splitlines():
        row = json.loads(line)
        statement_id = str(row["statement_id"])
        if statement_id in updates:
            output.append(json_bytes(updates[statement_id]))
            found.add(statement_id)
        else:
            output.append(line)
        if statement_id == INSERT_NEW_STATEMENTS_AFTER:
            output.extend(json_bytes(row) for row in NEW_STATEMENTS)
            inserted = True
    if found != set(updates):
        raise ValueError(f"Could not update every statement: {sorted(set(updates)-found)}")
    if not inserted:
        raise ValueError(f"New statement insertion anchor is missing: {INSERT_NEW_STATEMENTS_AFTER}")
    if raw.startswith(b"\xef\xbb\xbf"):
        return ("\ufeff" + eol.join(output) + eol).encode("utf-8")
    return (eol.join(output) + eol).encode("utf-8")


def candidate_display(row: dict[str, str]) -> str:
    name = str(row.get("canonical_name", ""))
    sub_entry = str(row.get("sub_entry", "")).strip()
    return f"{name} — {sub_entry}" if sub_entry else name


def build_plan() -> dict[str, object]:
    summary, prompts = surface_audit.audit("chp-16", 6)
    if summary["reviewed_segments_scanned"] != 7 or len(prompts) != 11:
        raise ValueError(f"Chapter 16 prompt surface changed: {summary}")
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
    new_candidate_ids = {str(row["candidate_id"]) for row in NEW_CANDIDATES}
    if new_candidate_ids & set(candidate_by_id):
        raise ValueError(f"New candidate ID already exists: {sorted(new_candidate_ids & set(candidate_by_id))}")
    if any(row["statement_id"] in statement_by_id for row in NEW_STATEMENTS):
        raise ValueError("A new statement ID already exists")

    expected_old_detail = CANDIDATE_DETAIL_PATCHES["cand-10598"]["expected_detail"]
    if candidate_by_id.get("cand-10598", {}).get("detail") != expected_old_detail:
        raise ValueError("Sasso collection candidate detail changed; re-review before patching")
    candidate_raw, patched_candidate = patch_csv_row(
        candidate_raw,
        candidate_columns,
        candidates,
        "candidate_id",
        "cand-10598",
        {"detail": CANDIDATE_DETAIL_PATCHES["cand-10598"]["detail"]},
    )
    candidate_raw = append_csv_rows(candidate_raw, candidate_columns, NEW_CANDIDATES)
    candidate_by_id["cand-10598"] = patched_candidate
    candidate_by_id.update({str(row["candidate_id"]): row for row in NEW_CANDIDATES})

    segment_by_id = {
        row["segment_id"]: row
        for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line and (row := json.loads(line))
    }
    segment_text = {}
    for segment_id in {str(row["segment_id"]) for row in prompts} | {
        str(row["segment_id"]) for row in NEW_STATEMENTS
    }:
        segment = segment_by_id[segment_id]
        source_lines = (ROOT / str(segment["source_file"])).read_text(encoding="utf-8-sig").splitlines()
        segment_text[segment_id] = "\n".join(source_lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])

    existing_spans: dict[str, list[tuple[int, int]]] = {}
    mention_ids = set()
    for row in existing_mentions:
        existing_spans.setdefault(row["segment_id"], []).append((int(row["start_char"]), int(row["end_char"])))
        mention_ids.add(row["mention_id"])
    if len(mention_ids) != len(existing_mentions):
        raise ValueError("Duplicate mention IDs in locked inputs")

    prompt_by_index = {i: row for i, row in enumerate(prompts, 1)}
    known_statement_ids = set(statement_by_id) | {str(row["statement_id"]) for row in NEW_STATEMENTS}
    known_candidate_ids = set(candidate_by_id)
    planned_mentions = []
    planned_spans = []
    for index, decision in accepted_by_index.items():
        prompt = prompt_by_index[index]
        segment_id = str(prompt["segment_id"])
        text = segment_text[segment_id]
        prompt_start, prompt_end = int(prompt["start_char"]), int(prompt["end_char"])
        prompt_surface = str(prompt["surface_form"])
        if text[prompt_start:prompt_end] != prompt_surface:
            raise ValueError(f"Prompt span drift at {index}: {prompt}")
        surface = str(decision.get("mention_form") or prompt_surface)
        positions = [m.start() for m in __import__("re").finditer(__import__("re").escape(surface), text)]
        positions = [start for start in positions if start <= prompt_start and prompt_end <= start + len(surface)]
        if len(positions) != 1:
            raise ValueError(f"Expected one accepted span containing prompt {index}, found {positions}")
        start = positions[0]
        end = start + len(surface)
        candidate_id = str(decision["candidate_id"])
        statement_id = str(decision["statement_id"])
        if candidate_id not in known_candidate_ids or statement_id not in known_statement_ids:
            raise ValueError(f"Unknown candidate or statement in decision {index}: {decision}")
        if any(start < old_end and end > old_start for old_start, old_end in existing_spans.get(segment_id, [])):
            raise ValueError(f"Accepted span overlaps an existing mention: {index} {surface}")
        if any(segment_id == old_segment and start < old_end and end > old_start for old_segment, old_start, old_end in planned_spans):
            raise ValueError(f"Accepted spans overlap each other: {index} {surface}")
        mention_id = "m-s2-chp16-surface-" + sha256(f"{segment_id}|{start}|{end}|{candidate_id}".encode("utf-8"))[:16]
        if mention_id in mention_ids:
            raise ValueError(f"Planned mention ID already exists: {mention_id}")
        planned_mentions.append(
            {
                "mention_id": mention_id,
                "segment_id": segment_id,
                "candidate_id": candidate_id,
                "surface_form": surface,
                "start_char": start,
                "end_char": end,
                "note": str(decision["note"]),
            }
        )
        planned_spans.append((segment_id, start, end))

    updates: dict[str, dict[str, object]] = {}
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
    for statement_id, patch in STATEMENT_TOP_LEVEL_PATCHES.items():
        if statement_id not in statement_by_id:
            raise ValueError(f"Statement to patch is missing: {statement_id}")
        row = updates.setdefault(statement_id, json.loads(json.dumps(statement_by_id[statement_id])))
        row.update(patch)

    final_statements = dict(statement_by_id)
    final_statements.update(updates)
    final_statements.update({str(row["statement_id"]): row for row in NEW_STATEMENTS})
    for decision in ACCEPTED:
        row = final_statements[str(decision["statement_id"])]
        refs = row.get("qualifiers", {}).get("mentioned_candidate_ids", [])
        if decision["candidate_id"] not in refs:
            raise ValueError(f"Mapped candidate is absent from its linked statement: {decision}")
    for statement_id, row in updates.items():
        subject = row.get("subject_candidate_id")
        if subject and subject not in row.get("qualifiers", {}).get("mentioned_candidate_ids", []):
            raise ValueError(f"Updated statement subject is not in its candidate references: {statement_id}")

    outputs = {
        CANDIDATES: candidate_raw,
        MENTIONS: append_csv_rows(mention_raw, mention_columns, planned_mentions),
        STATEMENTS: statement_output(statement_raw, updates),
    }
    plan_content = {
        "scanner_summary": summary,
        "accepted": ACCEPTED,
        "no_write": NO_WRITE_REASONS,
        "new_candidates": NEW_CANDIDATES,
        "candidate_detail_patches": CANDIDATE_DETAIL_PATCHES,
        "new_statements": NEW_STATEMENTS,
        "statement_updates": updates,
        "mentions": planned_mentions,
    }
    plan_hash = sha256(json.dumps(plan_content, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    return {
        "scanner_summary": summary,
        "prompts": prompts,
        "segment_by_id": segment_by_id,
        "segment_text": segment_text,
        "candidates": candidate_by_id,
        "planned_mentions": planned_mentions,
        "planned_spans": planned_spans,
        "updates": updates,
        "new_statement_reference_count": new_statement_reference_count,
        "plan_hash": plan_hash,
        "before_hashes": {
            "entity-candidates.csv": sha256(CANDIDATES.read_bytes()),
            "mentions.csv": sha256(mention_raw),
            "book-statements.jsonl": sha256(statement_raw),
        },
        "outputs": outputs,
    }


def render_report(plan: dict[str, object], after_hashes: dict[str, str], recovery: Path, audit: dict[str, object]) -> bytes:
    accepted_by_index = {int(row["prompt_index"]): row for row in ACCEPTED}
    lines = [
        "# 第十六章候选表面提示裁决（2026-10-08）",
        "",
        "定位器在7个reviewed/complete段中给出11条提示。逐项核对S0来源、前后文、现有statement与候选边界后，6条写入提及、5条不写。扫描仅定位已有候选标签，不代表实体召回率或语义验收。",
        "",
        "本批补入Sasso目录中“100 drawings”及Canaletto/Carlevarijs素描组，分别保留为工作组候选；复用Guardi一幅绘画加七幅素描组及Modelli术语。新增Toninotto收藏候选和其相似性断言，将“collection includes...”两条statement的subject改为该收藏候选。Sasso原有小型私人收藏说明更新为反映p.374–375后续记录，但未把目录未核实的完整清单写成事实。",
        "",
        "| 序号 | 来源定位 | 提示跨度 | 提示原文 | 写入提及/裁决 | 判断依据 |",
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
        surface = str(prompt["surface_form"]).replace("|", "\\|").replace("\n", " ")
        if decision:
            mention = next(row for row in plan["planned_mentions"] if row["segment_id"] == segment_id and row["candidate_id"] == decision["candidate_id"] and row["start_char"] <= start and row["end_char"] >= end)
            candidate_id = str(decision["candidate_id"])
            candidate_name = candidate_display(plan["candidates"][candidate_id])
            outcome = f"{mention['surface_form']} → {candidate_id} ({candidate_name})"
            reason = str(decision["note"])
        else:
            outcome = "不写入"
            reason = NO_WRITE_REASONS[index]
        outcome = outcome.replace("|", "\\|").replace("\n", " ")
        reason = reason.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {index} | {source_name}#L{source_line} | {start}:{end} | {surface} | {outcome} | {reason} |")
    lines.extend(
        [
            "",
            "## 写回与核验",
            "",
            f"- 表格新增：{len(NEW_CANDIDATES)}个候选、{len(plan['planned_mentions'])}条mentions和{len(NEW_STATEMENTS)}条statement；核对4条既有statement的候选引用，实际新增{plan['new_statement_reference_count']}个引用；另更新1条候选detail、修正2条collection内容statement的subject候选。",
            f"- 写后定位器剩余{audit['uncovered_candidate_surface_spans']}条，与5条no-write提示逐跨度一致。定位器不证明召回完整。",
            f"- 严格S2审计：errors={audit.get('errors')}; s2_missing={audit.get('s2_missing')}; candidates={audit.get('candidates')}; mentions={audit.get('mentions')}; statements={audit.get('book_statements')}。",
            f"- 关系候选：{audit.get('relation_candidate_count')}条；本批没有新增关系候选或写入S6正式关系。",
            f"- 决策计划SHA-256：{plan['plan_hash']}；脚本SHA-256：{sha256((ROOT / '03-processing/patrons-and-painters-full-book-s2/process/chp16_candidate_surface_prompt_reconciliation.py').read_bytes())}。",
            f"- 写前表SHA-256：candidates {plan['before_hashes']['entity-candidates.csv']}；mentions {plan['before_hashes']['mentions.csv']}；statements {plan['before_hashes']['book-statements.jsonl']}。",
            f"- 写后表SHA-256：candidates {after_hashes['entity-candidates.csv']}；mentions {after_hashes['mentions.csv']}；statements {after_hashes['book-statements.jsonl']}。",
            f"- 恢复副本：{recovery}。",
            "",
            "候选提示裁决不取代全书S2交接审计中的未登记实体、重复副本、跨页注释、指代、限定语、候选外键与全部关系候选复核。",
            "",
        ]
    )
    return "\n".join(lines).encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    import os

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
    recovery = Path(tempfile.gettempdir()) / f"pnp-s2-chp16-surface-prompts-{datetime.now():%Y%m%d-%H%M%S}"
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
            signature
            for signature in expected_after
            if not any(signature[0] == segment_id and signature[1] < end and signature[2] > start for segment_id, start, end in plan["planned_spans"])
        }
        after_summary, remaining = surface_audit.audit("chp-16", 6)
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
            1
            for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines()
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
    print(
        json.dumps(
            {
                "mode": "apply" if args.apply else "dry-run",
                "scanner": plan["scanner_summary"],
                "accepted_mentions": len(plan["planned_mentions"]),
                "no_write_prompts": len(NO_WRITE_REASONS),
                "new_candidates": [row["candidate_id"] for row in NEW_CANDIDATES],
                "new_statements": [row["statement_id"] for row in NEW_STATEMENTS],
                "new_statement_reference_count": plan["new_statement_reference_count"],
                "updated_statements": sorted(plan["updates"]),
                "planned_mention_ids": [row["mention_id"] for row in plan["planned_mentions"]],
                "plan_sha256": plan["plan_hash"],
                "before_hashes": plan["before_hashes"],
            },
            ensure_ascii=False,
        )
    )
    if not args.apply:
        return 0
    print(json.dumps(apply_plan(plan), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
