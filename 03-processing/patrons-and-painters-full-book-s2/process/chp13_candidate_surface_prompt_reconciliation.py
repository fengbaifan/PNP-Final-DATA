#!/usr/bin/env python3
"""Reconcile Chapter 13 candidate-surface prompts against S2 evidence.

The scanner is a locator, not a semantic gate. This one-off writer applies only
the reviewed Chapter 13 decisions below and refuses any change to its locked
inputs. Default execution is a read-only preflight; pass --apply to write.
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
RESULT = TASK / "results" / "chp-13.md"

EXPECTED_HASHES = {
    "04-knowledge/tables/entity-candidates.csv": "da4d8ff5b7e2ddaad15fa47fb83d48ab73071607d84b13e41885bb844e68ccda",
    "04-knowledge/tables/mentions.csv": "69a9e8efad682814c6d6a18f4e4ed439cef7c9453a16875214cd2497206ee566",
    "04-knowledge/tables/book-statements.jsonl": "c1b5a0eea7d2d44c38c9b3965129ef9e9efd0019fe8bc3098177e18af3754445",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/s2-coverage.csv": "84f8497a7ce0100f4785acd8bf8ed88bb4c69fe5254cd89d172577b0400eb6c1",
    "02-sources/02-Markdown/13_CHP-13_intro.md": "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8",
    "02-sources/02-Markdown/13_CHP-13_intro_plates_visual-transcription.md": "73d5fad85a4b84f11508ef0cad9590bded516b69ed2ce203dc3afaf3079906bd",
    "scripts/audit_s2_candidate_surfaces.py": "130b53da86d940daad454079960415ac5e7043e0b71239370b66226158cd1ee2",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "01-domain/stage-artifact-schema.md": "929b8a55f92103de962e8bd509d02d883683b0eea3a9ffe307e5de8229a86abe",
}


def accepted(index: int, candidate_id: str, statement_id: str, note: str) -> dict[str, object]:
    return {"prompt_index": index, "candidate_id": candidate_id, "statement_id": statement_id, "note": note}


ACCEPTED = [
    accepted(1, "cand-2719", "st-chp13-p344-delle_antiche_statue-neoclassical_taste", "Venice is the city where the plates mark the arrival of neo-classical taste; use the place candidate, not the topical Venice index subentries."),
    accepted(2, "cand-3570", "st-chp13-p344-clement-description_of_zanetti", "Clement's quoted amateur describes Zanetti as a social/collecting category; use the existing term candidate and preserve the attributed wording."),
    accepted(5, "cand-1310", "st-chp13-p333-publishers-sales-employment-and-commissions", "Illustrated books are the eighteenth-century publication category discussed in the publisher account; the existing index term matches this context."),
    accepted(7, "cand-1310", "st-chp13-p333-two-categories-of-illustrated-books", "The phrase names the two broad categories of eighteenth-century Venetian illustrated books already distinguished in this statement."),
    accepted(9, "cand-7618", "st-chp13-p345-monaco-collection-advertised-dealer", "Such a collection refers to Monaco's 112-plate print publication discussed immediately before; keep its edition mapping unresolved against the separate 1779 candidate."),
    accepted(10, "cand-2719", "st-chp13-p332-n4-marin-counterview", "Venice is the geographic context of the footnote's account of eighteenth-century engraving; this is not a topical subentry."),
    accepted(11, "cand-11495", "st-chp13-p344-notes-note2-northall-reported-zanetti-collection", "Northall's quoted report identifies a multi-medium collection at the dealer contextually identified as A. M. Zanetti; preserve the printed Lanetti spelling and unresolved inventory boundary."),
    accepted(14, "cand-2719", "st-chp13-p334-albrizzi-guidebook-1737", "Venice is the city named in the title and description of Albrizzi's guide; the statement already links the city candidate."),
    accepted(15, "cand-2719", "st-chp13-p334-albrizzi-prominent-in-venetian-intellectual-life", "Venice is the setting for Haskell's separate assessment of Albrizzi's role in its intellectual life."),
    accepted(16, "cand-1310", "st-chp13-p332-publishers-export-illustrated-books", "Lavishly illustrated books are the publication category in Haskell's account of export-oriented publishers."),
    accepted(22, "cand-10007", "st-chp13-p336-albrizzi-owned-piazzetta-private-collection", "Private collection identifies the bounded, type-unresolved Albrizzi holdings of Piazzetta drawings and paintings, not Albrizzi the person."),
    accepted(24, "cand-10007", "st-chp13-p336-albrizzi-owned-piazzetta-private-collection", "The several hundred drawings are part of the same source-described Albrizzi collection; no individual sheets are inferred."),
    accepted(25, "cand-1310", "st-chp13-p337-pasquali-books-recorded-smith-collection", "The fine illustrated books are the eighteenth-century publication category in the Smith/Pasquali passage."),
    accepted(28, "cand-10013", "st-chp13-p338-haskell-praised-drawings-quality", "The drawings are the specific Novelli illustration program for Pasquali's Goldoni edition, already represented by cand-10013."),
    accepted(29, "cand-1321", "st-chp13-p338-zatta-combatively-supported-jesuits", "Jesuits names the Society Zatta supported; reuse the institution candidate used by the existing statement."),
    accepted(30, "cand-1321", "st-chp13-p339-zatta-parodied-symbolic-readings", "The quoted phrase about finding Jesuits everywhere names the same institution; retain the satirical framing."),
    accepted(31, "cand-10045", "st-chp13-p340-print-sellers-often-important-art-patrons", "In this sentence the phrase describes print sellers' role as art patrons; use the source-local concept candidate, not the broad library subject heading."),
    accepted(32, "cand-2123", "st-chp13-p340-remondini-established-at-bassano", "Remondini refers to the publishing firm in the p.340 account; use the index candidate scoped to this chapter passage."),
]


NO_WRITE_REASONS = {
    3: "Subject-matter is a generic description of content, not the Contracts > subject index concept.",
    4: "Drawings is a generic medium among works that might be commissioned for reproduction; no bounded drawing group is identified.",
    6: "Drawings is a generic category of material commissioned for illustrated books, not the Carracci person or a named work group.",
    8: "The younger Zanetti's drawings and prints are described as a practice and linked to Varie Pitture; no separate, bounded set is identified here.",
    12: "Drawings is one medium in the dealer's reported collection, not an independently identified drawing set.",
    13: "The noble's collection is an unnamed instance of the commemorative-publication category; its owner and contents are not identified as a separate object.",
    17: "Drawings describes illustrations within the named Teatro delle Pitture publication; no independent drawing group is identified.",
    18: "Out of character is an idiom about style, not the unrelated character index entry.",
    19: "Altarpieces is a generic category of Piazzetta's religious work, not the Poussin index subentry.",
    20: "Hieratic portraits is a generic image category in the Bossuet illustration discussion, not Schulenburg's portrait subentry or a bounded group.",
    21: "The occasional drawings supplied by several artists for Albrizzi's firm are not a bounded or titled set.",
    23: "This nested collection hit lies within the accepted private collection span at prompt 22; a second mention would overlap the same words.",
    26: "Presentation describes the comparative design of a book, not Solimena's Presentation work.",
    27: "School is a generic educational setting in Perugia, not Padre Lodoli's school candidate.",
    33: "School is a generic setting in the Goldoni caption, not Padre Lodoli's institution.",
}


NEW_CANDIDATES = [
    {
        "candidate_id": "cand-11495",
        "index_entry_id": "",
        "canonical_name": "Collection reported at Signor Lanetti's [sic] (contextually identified as A. M. Zanetti; scope unresolved)",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Northall's 1767 report quoted in Haskell describes pictures, drawings, some of his own from wooden plates, cameos, and intaglios at the dealer printed as Signor Lanetti's [sic]. The p.344 note context identifies the dealer with A. M. Zanetti while preserving the quotation's spelling. No inventory or boundary is supplied; do not equate this group with cand-10113 (the gem and medal collection) or infer complete contents.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-13:13_CHP-13_intro:l179-251#L240",
    }
]


NEW_STATEMENTS = [
    {
        "statement_id": "st-chp13-p334-albrizzi-prominent-in-venetian-intellectual-life",
        "segment_id": "chp-13:13_CHP-13_intro:l21-30",
        "subject_candidate_id": "cand-0025",
        "object_candidate_id": None,
        "predicate": "described_as_playing_prominent_part_in_venetian_intellectual_life",
        "qualifiers": {
            "source_line_start": 26,
            "source_line_end": 26,
            "printed_page": 334,
            "pdf_physical_page": 3,
            "claim": "Haskell says Albrizzi played a fairly prominent part in the intellectual life of Venice.",
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "qualification": "This is Haskell's qualitative assessment; the sentence does not itself specify particular activities or institutional membership.",
            "mentioned_candidate_ids": ["cand-0025", "cand-2719"],
        },
        "original_quote": "Albrizzi also played a fairly prominent part in the intellectual life of Venice.",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
    },
    {
        "statement_id": "st-chp13-p344-notes-note2-northall-reported-zanetti-collection",
        "segment_id": "chp-13:13_CHP-13_intro:l179-251",
        "subject_candidate_id": "cand-2838",
        "object_candidate_id": "cand-11495",
        "predicate": "northall_reported_dealer_had_multimedium_collection",
        "qualifiers": {
            "source_line_start": 240,
            "source_line_end": 240,
            "printed_page": 344,
            "pdf_physical_page": 13,
            "claim": "Haskell's note quotes John Northall in 1767 reporting that the dealer printed as Signor Lanetti's [sic] had a fine collection of pictures and drawings, some of his own from wooden plates, cameos, and intaglios.",
            "speaker": "John Northall, quoted in Haskell's footnote",
            "text_layer": "reported quotation in a secondary-source footnote",
            "qualification": "The process record identifies the dealer with A. M. Zanetti from Haskell's context but preserves the printed Lanetti's [sic] form. Northall's cited page was not consulted. The holdings have no supplied inventory or boundary and are not equated with the separate gem and medal collection.",
            "mentioned_candidate_ids": ["cand-10215", "cand-2838", "cand-11495"],
            "footnote_marker": "2",
            "footnote_printed_page": 344,
            "footnote_text_pending": False,
            "footnote_segment": "chp-13:13_CHP-13_intro:l179-251",
            "footnote_body_link_status": "linked",
            "linked_body_statement_ids": ["st-chp13-p344-clement-description_of_zanetti"],
            "relation_candidate": True,
        },
        "original_quote": "a dealer, who has a fine collection of pictures and drawings; some of his own from wooden plates; cameos, and intaglios",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
    },
]


STATEMENT_REFERENCE_ADDITIONS = {
    "st-chp13-p344-delle_antiche_statue-neoclassical_taste": ["cand-2719"],
    "st-chp13-p344-clement-description_of_zanetti": ["cand-3570"],
    "st-chp13-p333-publishers-sales-employment-and-commissions": ["cand-1310"],
    "st-chp13-p333-two-categories-of-illustrated-books": ["cand-1310"],
    "st-chp13-p332-n4-marin-counterview": ["cand-2719"],
    "st-chp13-p332-publishers-export-illustrated-books": ["cand-1310"],
    "st-chp13-p337-pasquali-books-recorded-smith-collection": ["cand-1310"],
    "st-chp13-p339-zatta-parodied-symbolic-readings": ["cand-1321"],
}


INSERT_AFTER = {
    "st-chp13-p334-albrizzi-collector-and-publisher": [NEW_STATEMENTS[0]],
    "st-chp13-p344-notes-note2-northall-quote": [NEW_STATEMENTS[1]],
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
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
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
    lines = text.splitlines()
    output: list[str] = []
    inserted: set[str] = set()
    for line in lines:
        row = json.loads(line)
        statement_id = str(row["statement_id"])
        output.append(json_bytes(updates[statement_id]) if statement_id in updates else line)
        for extra in INSERT_AFTER.get(statement_id, []):
            output.append(json_bytes(extra))
            inserted.add(str(extra["statement_id"]))
    expected = {str(row["statement_id"]) for rows in INSERT_AFTER.values() for row in rows}
    if inserted != expected:
        raise ValueError(f"Could not place every new statement: inserted={sorted(inserted)}")
    result = eol.join(output) + eol
    if raw.startswith(b"\xef\xbb\xbf"):
        result = "\ufeff" + result
    return result.encode("utf-8")


def build_plan() -> dict[str, object]:
    summary, prompts = surface_audit.audit("chp-13", 6)
    if summary["reviewed_segments_scanned"] != 24 or len(prompts) != 33:
        raise ValueError(f"Chapter 13 prompt surface changed: {summary}")
    prompt_indices = set(range(1, len(prompts) + 1))
    accepted_by_index = {int(row["prompt_index"]): row for row in ACCEPTED}
    if set(accepted_by_index) & set(NO_WRITE_REASONS) or set(accepted_by_index) | set(NO_WRITE_REASONS) != prompt_indices:
        raise ValueError("Accepted and no-write decisions do not form an exact prompt partition")

    candidate_raw, candidate_columns, candidates = read_csv(CANDIDATES)
    mention_raw, mention_columns, existing_mentions = read_csv(MENTIONS)
    statement_raw = STATEMENTS.read_bytes()
    statement_lines = statement_raw.decode("utf-8-sig").splitlines()
    statements = [json.loads(line) for line in statement_lines if line.strip()]
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    statement_by_id = {str(row["statement_id"]): row for row in statements}
    if len(candidate_by_id) != len(candidates) or len(statement_by_id) != len(statements):
        raise ValueError("Duplicate candidate or statement IDs in locked inputs")
    if any(row["candidate_id"] in candidate_by_id for row in NEW_CANDIDATES):
        raise ValueError("A new candidate ID already exists")
    if any(str(row["statement_id"]) in statement_by_id for row in NEW_STATEMENTS):
        raise ValueError("A new statement ID already exists")

    segment_by_id = {
        row["segment_id"]: row
        for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line and (row := json.loads(line))
    }
    segment_text: dict[str, str] = {}
    for segment_id in {str(row["segment_id"]) for row in prompts}:
        segment = segment_by_id[segment_id]
        source_lines = (ROOT / str(segment["source_file"])).read_text(encoding="utf-8-sig").splitlines()
        segment_text[segment_id] = "\n".join(source_lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])

    existing_spans: dict[str, list[tuple[int, int]]] = {}
    for row in existing_mentions:
        existing_spans.setdefault(row["segment_id"], []).append((int(row["start_char"]), int(row["end_char"])))
    planned_mentions: list[dict[str, object]] = []
    planned_spans: list[tuple[str, int, int]] = []
    prompt_by_index = {i: row for i, row in enumerate(prompts, 1)}
    known_candidate_ids = set(candidate_by_id) | {str(row["candidate_id"]) for row in NEW_CANDIDATES}
    known_statement_ids = set(statement_by_id) | {str(row["statement_id"]) for row in NEW_STATEMENTS}

    for index, decision in accepted_by_index.items():
        prompt = prompt_by_index[index]
        segment_id = str(prompt["segment_id"])
        start, end = int(prompt["start_char"]), int(prompt["end_char"])
        surface = str(prompt["surface_form"])
        if segment_text[segment_id][start:end] != surface:
            raise ValueError(f"Prompt span drift at {index}: {prompt}")
        candidate_id = str(decision["candidate_id"])
        statement_id = str(decision["statement_id"])
        if candidate_id not in known_candidate_ids or statement_id not in known_statement_ids:
            raise ValueError(f"Unknown candidate or statement in decision {index}: {decision}")
        if any(start < old_end and end > old_start for old_start, old_end in existing_spans.get(segment_id, [])):
            raise ValueError(f"Accepted span overlaps an existing mention: {index} {prompt}")
        if any(segment_id == old_segment and start < old_end and end > old_start for old_segment, old_start, old_end in planned_spans):
            raise ValueError(f"Accepted spans overlap each other: {index} {prompt}")
        mention_id = "m-s2-chp13-surface-" + sha256(f"{segment_id}|{start}|{end}|{candidate_id}".encode("utf-8"))[:16]
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

    updates: dict[str, dict[str, object]] = {}
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
    final_statements.update({str(row["statement_id"]): row for row in NEW_STATEMENTS})
    for decision in ACCEPTED:
        row = final_statements[str(decision["statement_id"])]
        refs = row.get("qualifiers", {}).get("mentioned_candidate_ids", [])
        if decision["candidate_id"] not in refs:
            raise ValueError(f"Mapped candidate is absent from its linked statement: {decision}")
    for row in NEW_STATEMENTS:
        for candidate_id in row.get("qualifiers", {}).get("mentioned_candidate_ids", []):
            if candidate_id not in known_candidate_ids:
                raise ValueError(f"New statement has unknown candidate reference: {candidate_id}")

    mention_ids = {row["mention_id"] for row in existing_mentions}
    if len(mention_ids) != len(existing_mentions):
        raise ValueError("Duplicate mention IDs in locked inputs")
    if any(row["mention_id"] in mention_ids for row in planned_mentions):
        raise ValueError("A planned mention ID already exists")

    candidate_output = append_csv_rows(candidate_raw, candidate_columns, NEW_CANDIDATES)
    mention_output = append_csv_rows(mention_raw, mention_columns, planned_mentions)
    updated_ids = set(updates)
    statement_updates = {str(row["statement_id"]): row for row in statements if str(row["statement_id"]) in updated_ids}
    statements_output = statement_output(statement_raw, statement_updates)

    plan_content = {
        "scanner_summary": summary,
        "accepted": ACCEPTED,
        "no_write": NO_WRITE_REASONS,
        "new_candidates": NEW_CANDIDATES,
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
        "outputs": {
            CANDIDATES: candidate_output,
            MENTIONS: mention_output,
            STATEMENTS: statements_output,
        },
    }


def render_report(plan: dict[str, object], after_hashes: dict[str, str], recovery: Path, audit: dict[str, object]) -> bytes:
    accepted_by_index = {int(row["prompt_index"]): row for row in ACCEPTED}
    lines = [
        "# 第十三章候选表面提示裁决（2026-10-08）",
        "",
        "定位器在24个reviewed/complete段中给出33条提示。逐条回到规范S0来源、现有statement和候选边界裁决后，18条映射、15条不写；其中第23条是第22条已接纳“private collection”跨度内的嵌套命中。扫描只覆盖当前有类型候选词形，不代表实体召回率或语义验收。",
        "",
        "新增cand-11495记录Northall转引中“Signor Lanetti’s [sic]”所指dealer的多媒介收藏，类型、库存和边界均未确定；新增来源断言和一个待S6审查的关系候选。另补记Albrizzi参与威尼斯思想生活的独立评价。未新增KU或正式S6关系。",
        "",
        "字符跨度是拼接段文本的零起点、右开区间；行号回到规范来源。索引误撞、普通泛称、未界定集合及与已接受跨度重叠的子词不另写mentions。",
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
        f"- 表格新增：1个类型待定候选、{len(plan['planned_mentions'])}条mentions、2条statement；另更新{len(plan['updates'])}条statement的候选引用。新增statement中1条记录Albrizzi评价，1条把Northall引文中的收藏主张与原有dealer识别拆开。",
        f"- 写后定位器剩余{audit['uncovered_candidate_surface_spans']}条，等于未被已接纳跨度遮盖的no-write残余；另1条嵌套提示随父跨度消失。定位器不证明召回完整。",
        f"- 严格S2审计：errors={audit.get('errors')}; s2_missing={audit.get('s2_missing')}; candidates={audit.get('candidates')}; mentions={audit.get('mentions')}; statements={audit.get('book_statements')}。",
        f"- 关系候选：{audit.get('relation_candidate_count')}条；此批新增1条开放端点完整的来源关系候选，没有写入正式关系表。",
        f"- 决策计划SHA-256：{plan['plan_hash']}；脚本SHA-256：{sha256((ROOT / '03-processing/patrons-and-painters-full-book-s2/process/chp13_candidate_surface_prompt_reconciliation.py').read_bytes())}。",
        f"- 写前表SHA-256：candidates {plan['before_hashes']['entity-candidates.csv']}；mentions {plan['before_hashes']['mentions.csv']}；statements {plan['before_hashes']['book-statements.jsonl']}。",
        f"- 写后表SHA-256：candidates {after_hashes['entity-candidates.csv']}；mentions {after_hashes['mentions.csv']}；statements {after_hashes['book-statements.jsonl']}。",
        f"- 恢复副本：{recovery}。",
        "",
        "候选提示裁决不取代全书S2交接审计中的未登记实体、重复副本、跨页注释、指代、限定语、外键与全部关系候选复核。",
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
    recovery = Path(tempfile.gettempdir()) / f"pnp-s2-chp13-surface-prompts-{datetime.now():%Y%m%d-%H%M%S}"
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
        after_summary, remaining = surface_audit.audit("chp-13", 6)
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
        "new_statements": [row["statement_id"] for row in NEW_STATEMENTS],
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
