#!/usr/bin/env python3
"""Normalize the three claims and citation in chapter 2, printed p.60 note 3.

The default mode is a guarded dry run. Use --apply only after the displayed
source, candidate, anchor, and table-hash checks pass.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge/tables/book-statements.jsonl"
MENTIONS = ROOT / "04-knowledge/tables/mentions.csv"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
SOURCE = ROOT / "02-sources/02-Markdown/02_CHP-2_sec_vii.md"
STATEMENTS_SHA = "86b1f406992ebc61fa2a427d4e2b49f50dd374466a20fcbbdeea4a3533cc4b70"
MENTIONS_SHA = "c95782736e9cfc5b4dad1cbae2afa04f0694548f29dd7f46a2d7beffdf1de897"
CANDIDATES_SHA = "b4ac5c42748249c553bf133ab9267acb9fbb85422d1198208b19b7e8b8c250de"
SOURCE_SHA = "5f2ec3c85927ed4aded258d7a6b1801ccb3b8e0416f0f3f9e57ad7b2fae8dd4c"
BACKUP_SUFFIX = ".bak-s2-handoff-chp2-p60-note3-20261010"

OLD_A = "st-chp2-secvii-l38-54-fn-p60-3a-described-portrait-location"
OLD_B = "st-chp2-secvii-l38-54-fn-p60-3b-other-antonio-portraits"
NEW_ATTRIBUTION = "st-chp2-secvii-l38-54-fn-p60-3c-two-portraits-attributed-to-nanteuil"
NEW_CITATION = "st-chp2-secvii-l38-54-fn-p60-3d-lombardo-citation"
BODY_IDS = [
    "st-chp2-secvii-l21-30-described-portrait-visual-and-symbolic-description",
    "st-chp2-secvii-l21-30-maratta-records-antonio-in-portraits",
]
BOOK_ID = "cand-2962"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"preflight failed: {message}")


def load_statements() -> tuple[list[dict], list[bytes], bool]:
    raw = STATEMENTS.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    lines = raw.splitlines(keepends=True)
    rows = [json.loads(line.decode("utf-8-sig")) for line in lines if line.strip()]
    return rows, lines, bom


def load_csv(path: Path) -> tuple[list[dict[str, str]], list[bytes]]:
    raw_lines = path.read_bytes().splitlines(keepends=True)
    text = path.read_text(encoding="utf-8-sig")
    return list(csv.DictReader(text.splitlines())), raw_lines


def audit() -> tuple[list[dict], list[bytes], bool, list[dict[str, str]], list[bytes], list[dict[str, str]]]:
    for path, expected in (
        (STATEMENTS, STATEMENTS_SHA),
        (MENTIONS, MENTIONS_SHA),
        (CANDIDATES, CANDIDATES_SHA),
        (SOURCE, SOURCE_SHA),
    ):
        require(sha(path) == expected, f"unexpected SHA-256 for {path.relative_to(ROOT)}")

    statements, statement_lines, statement_bom = load_statements()
    mentions, mention_lines = load_csv(MENTIONS)
    candidates, _ = load_csv(CANDIDATES)
    by_id = {row["statement_id"]: row for row in statements}
    require(len(by_id) == len(statements), "duplicate statement_id")
    require(not ({NEW_ATTRIBUTION, NEW_CITATION} & set(by_id)), "new statement ID already exists")
    require(OLD_A in by_id and OLD_B in by_id, "target note statements missing")

    a, b = by_id[OLD_A], by_id[OLD_B]
    require(a["predicate"] == b["predicate"] == "footnote-claim", "target predicates changed")
    require(a["subject_candidate_id"] == "cand-4922" and a["object_candidate_id"] == "cand-4142", "location endpoints changed")
    require(b["subject_candidate_id"] == "cand-0187" and b["object_candidate_id"] == "cand-4950", "portrait-group endpoints changed")
    require("Edoardo Lombardo, 1959, p. 2" in a["original_quote"], "note text changed")

    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    expected_candidates = {
        "cand-2962": ("archive", "open"),
        "cand-4142": ("institution", "open"),
        "cand-4490": ("place", "open"),
        "cand-4922": ("work", "open"),
        "cand-4949": ("person", "open"),
        "cand-4950": ("work", "open"),
        "cand-4951": ("archive", "open"),
    }
    for candidate_id, (kind, status) in expected_candidates.items():
        row = candidate_by_id.get(candidate_id)
        require(row is not None, f"candidate {candidate_id} missing")
        require(row["suggested_type"] == kind and row["status"] == status, f"candidate {candidate_id} type/status changed")

    source = SOURCE.read_text(encoding="utf-8-sig")
    source_line = source.splitlines()[45]
    require(source_line.startswith("3 For the most recent discussion of the portrait, now in the Galleria Nazionale"), "source line 46 changed")
    require("others of the Cardinal (including two by Nanteuil)" in source_line and "Edoardo Lombardo, 1959, p. 2" in source_line, "note wording changed")

    mention_by_id = {row["mention_id"]: row for row in mentions}
    target_mention = mention_by_id.get("m-chp2-secvii-l38-54-0015")
    require(target_mention is not None, "the portrait mention missing")
    require(target_mention["candidate_id"] == "cand-4950", "the portrait mention mapping already changed")
    require(target_mention["segment_id"] == "chp-2:02_CHP-2_sec_vii:l38-54", "mention segment changed")
    require((target_mention["start_char"], target_mention["end_char"]) == ("443", "455"), "mention span changed")
    source_lines = source.splitlines()
    segment_text = "\n".join(source_lines[37:54])
    require(segment_text[443:455] == "the portrait", "mention span no longer resolves to the described portrait")

    for body_id in BODY_IDS:
        body = by_id.get(body_id)
        require(body is not None, f"body statement {body_id} missing")
        refs = body.get("qualifiers", {}).get("footnote_refs", [])
        note_ref = next((ref for ref in refs if ref.get("marker") == 3 and ref.get("segment_id") == a["segment_id"] and ref.get("source_line") == 46), None)
        require(note_ref is not None and set(note_ref.get("statement_ids", [])) == {OLD_A, OLD_B}, f"body links for {body_id} changed")

    return statements, statement_lines, statement_bom, mentions, mention_lines, candidates


def build_rows(rows: list[dict]) -> tuple[dict, dict, dict, dict, list[dict]]:
    by_id = {row["statement_id"]: row for row in rows}
    a, b = by_id[OLD_A], by_id[OLD_B]
    body_ids = list(BODY_IDS)
    quote = a["original_quote"]

    q_a = a["qualifiers"]
    q_a["claim"] = "Haskell's footnote reports that, at the time of publication, the portrait described in the body was in the Galleria Nazionale di Arte Antica in Rome."
    q_a["qualification"] = "The word 'now' is relative to Haskell's publication. The candidate's exact institutional identity and present custody are not resolved; the cited discussion was not independently consulted."
    q_a["relation_candidate"] = True
    q_a["relation_candidate_note"] = "Source-qualified S2 candidate for the reported location at publication; it is not a present-day custody assertion or a formal S6 relation."
    q_a["related_body_statement_ids"] = body_ids
    q_a["cited_material_not_independently_consulted"] = True
    a["predicate"] = "book_note_reports_work_location_at_publication"

    old_b = copy.deepcopy(b)
    q_b = b["qualifiers"]
    q_b["claim"] = "Haskell's footnote refers to other portraits of Cardinal Antonio, distinct from the portrait described in the preceding text."
    q_b["qualification"] = "The note does not identify the individual portraits or the total number in this group."
    q_b.pop("artist_candidate_id", None)
    q_b.pop("reference_candidate_id", None)
    q_b["relation_candidate"] = True
    q_b["relation_candidate_note"] = "S2 candidate records the note's statement that this work group depicts Cardinal Antonio; individual works and the group's membership remain unspecified. No formal S6 edge is created."
    q_b["related_body_statement_ids"] = body_ids
    b["subject_candidate_id"] = "cand-4950"
    b["object_candidate_id"] = "cand-0187"
    b["predicate"] = "other_portraits_group_depicts_cardinal_antonio"

    attribution = copy.deepcopy(old_b)
    attribution["statement_id"] = NEW_ATTRIBUTION
    attribution["subject_candidate_id"] = "cand-4950"
    attribution["object_candidate_id"] = "cand-4949"
    attribution["predicate"] = "two_portraits_in_group_attributed_to_nanteuil"
    attribution["qualifiers"] = copy.deepcopy(old_b["qualifiers"])
    attribution["qualifiers"].update({
        "claim": "Haskell says that two of the other portraits of Cardinal Antonio are by Nanteuil.",
        "qualification": "The count applies to two members of the unspecified portrait group, not to the whole group. Individual works and Nanteuil's identity remain unresolved; the statement records Haskell's report, not an independently verified attribution.",
        "count": 2,
        "scope": "Two portraits within the other-portraits group; remaining membership and total group size are unspecified.",
        "attribution_status": "reported",
        "relation_candidate": True,
        "relation_candidate_note": "Source-qualified S2 candidate for the two-member attribution only; it does not attribute every work in the group or create a formal S6 edge.",
    })
    attribution["qualifiers"].pop("reference_candidate_id", None)
    attribution["original_quote"] = quote

    citation = copy.deepcopy(old_b)
    citation["statement_id"] = NEW_CITATION
    citation["subject_candidate_id"] = BOOK_ID
    citation["object_candidate_id"] = "cand-4951"
    citation["predicate"] = "cites"
    citation["qualifiers"] = {
        "source_line_start": 46,
        "source_line_end": 46,
        "claim": "Haskell's footnote cites Edoardo Lombardo (1959, p. 2) for a recent discussion of the described portrait and other portraits of Cardinal Antonio.",
        "speaker": "Haskell, footnote",
        "text_layer": "bibliographic citation",
        "qualification": "The citation identifies no title in the note; the cited publication was not independently consulted and does not independently verify the reported location or attributions.",
        "footnote_marker": 3,
        "print_page": 60,
        "pdf_physical_page": 49,
        "page": 2,
        "linked_body_statement_ids": body_ids,
        "citation_context_candidate_ids": ["cand-4922", "cand-4950"],
        "cited_material_not_independently_consulted": True,
        "relation_candidate": True,
        "relation_candidate_note": "The note explicitly cites this archive from Haskell's book. This records a bibliographic link, not validation of the cited discussion, and creates no formal S6 edge.",
    }
    citation["original_quote"] = quote

    for body_id in BODY_IDS:
        body = by_id[body_id]
        for ref in body["qualifiers"]["footnote_refs"]:
            if ref.get("marker") == 3 and ref.get("segment_id") == a["segment_id"] and ref.get("source_line") == 46:
                ref["statement_ids"] = [OLD_A, OLD_B, NEW_ATTRIBUTION, NEW_CITATION]
    return a, b, attribution, citation, rows


def serialized_rows(rows: list[dict], original_lines: list[bytes], had_bom: bool) -> bytes:
    newline = b"\r\n" if any(line.endswith(b"\r\n") for line in original_lines) else b"\n"
    old_bom = b"\xef\xbb\xbf" if had_bom else b""
    out: list[bytes] = []
    by_id = {row["statement_id"]: row for row in rows}
    for row in rows:
        if row["statement_id"] in {NEW_ATTRIBUTION, NEW_CITATION}:
            continue
        encoded = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if not out and old_bom:
            encoded = old_bom + encoded
        out.append(encoded + newline)
        if row["statement_id"] == OLD_B:
            out.append(json.dumps(by_id[NEW_ATTRIBUTION], ensure_ascii=False, separators=(",", ":")).encode("utf-8") + newline)
            out.append(json.dumps(by_id[NEW_CITATION], ensure_ascii=False, separators=(",", ":")).encode("utf-8") + newline)
    return b"".join(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the audited change; default is dry-run")
    args = parser.parse_args()
    statements, statement_lines, statement_bom, mentions, mention_lines, candidates = audit()

    updated_statements = copy.deepcopy(statements)
    a, b, attribution, citation, updated_statements = build_rows(updated_statements)
    # New rows are inserted after the retained 3b row in serialized_rows.
    updated_statements.extend([attribution, citation])
    output_statements = serialized_rows(updated_statements, statement_lines, statement_bom)

    target_mention_id = "m-chp2-secvii-l38-54-0015"
    output_mentions: list[bytes] = []
    mention_changed = 0
    for raw in mention_lines:
        line = raw.decode("utf-8-sig")
        if line.startswith(target_mention_id + ","):
            require(",cand-4950,the portrait,443,455," in line, "target mention CSV row changed")
            line = line.replace(",cand-4950,the portrait,443,455,", ",cand-4922,the portrait,443,455,", 1)
            mention_changed += 1
        output_mentions.append(line.encode("utf-8"))
    require(mention_changed == 1, "target mention row not uniquely changed")
    # Keep the source table's original line ending and UTF-8 BOM state.
    mention_newline = b"\r\n" if any(line.endswith(b"\r\n") for line in mention_lines) else b"\n"
    output_mentions_bytes = b"".join(
        (b"\xef\xbb\xbf" if i == 0 and MENTIONS.read_bytes().startswith(b"\xef\xbb\xbf") else b"")
        + line.rstrip(b"\r\n") + mention_newline
        for i, line in enumerate(output_mentions)
    )

    before_true = sum(s.get("qualifiers", {}).get("relation_candidate") is True for s in statements)
    before_unclassified = sum(bool(s.get("subject_candidate_id") and s.get("object_candidate_id")) and "relation_candidate" not in s.get("qualifiers", {}) for s in statements)
    before_footnote_claims = sum(s.get("predicate") == "footnote-claim" for s in statements)
    after_true = sum(s.get("qualifiers", {}).get("relation_candidate") is True for s in updated_statements)
    after_unclassified = sum(bool(s.get("subject_candidate_id") and s.get("object_candidate_id")) and "relation_candidate" not in s.get("qualifiers", {}) for s in updated_statements)
    after_footnote_claims = sum(s.get("predicate") == "footnote-claim" for s in updated_statements)
    require(before_true == 3635 and after_true == 3639, f"relation candidate projection changed: {before_true} -> {after_true}")
    require(before_unclassified == 4438 and after_unclassified == 4436, f"unclassified projection changed: {before_unclassified} -> {after_unclassified}")
    require(before_footnote_claims == 14 and after_footnote_claims == 12, f"footnote claim projection changed: {before_footnote_claims} -> {after_footnote_claims}")
    preview = {
        "action": "apply" if args.apply else "dry-run",
        "statement_rows": f"{len(statements)} -> {len(updated_statements)}",
        "relation_candidates": f"{before_true} -> {after_true}",
        "dual_endpoint_unclassified": f"{before_unclassified} -> {after_unclassified}",
        "footnote_claims": f"{before_footnote_claims} -> {after_footnote_claims}",
        "candidate_rows": len(candidates),
        "mention_rows": len(mentions),
        "mention_mapping": "m-chp2-secvii-l38-54-0015: cand-4950 -> cand-4922",
        "new_statements": [NEW_ATTRIBUTION, NEW_CITATION],
        "reviewable_changes": [
            {
                "statement_id": OLD_A,
                "from": {"predicate": "footnote-claim", "subject": "cand-4922", "object": "cand-4142"},
                "to": {"predicate": a["predicate"], "subject": a["subject_candidate_id"], "object": a["object_candidate_id"], "relation_candidate": a["qualifiers"]["relation_candidate"], "claim": a["qualifiers"]["claim"]},
            },
            {
                "statement_id": OLD_B,
                "from": {"predicate": "footnote-claim", "subject": "cand-0187", "object": "cand-4950"},
                "to": {"predicate": b["predicate"], "subject": b["subject_candidate_id"], "object": b["object_candidate_id"], "relation_candidate": b["qualifiers"]["relation_candidate"], "claim": b["qualifiers"]["claim"]},
            },
            {"statement_id": NEW_ATTRIBUTION, "predicate": attribution["predicate"], "subject": attribution["subject_candidate_id"], "object": attribution["object_candidate_id"], "claim": attribution["qualifiers"]["claim"], "count": 2},
            {"statement_id": NEW_CITATION, "predicate": citation["predicate"], "subject": citation["subject_candidate_id"], "object": citation["object_candidate_id"], "claim": citation["qualifiers"]["claim"], "page": 2},
            {"body_statement_ids": BODY_IDS, "footnote_marker": 3, "linked_note_statement_ids": [OLD_A, OLD_B, NEW_ATTRIBUTION, NEW_CITATION]},
        ],
    }
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    statement_backup = STATEMENTS.with_name(STATEMENTS.name + BACKUP_SUFFIX)
    mention_backup = MENTIONS.with_name(MENTIONS.name + BACKUP_SUFFIX)
    require(not statement_backup.exists() and not mention_backup.exists(), "recovery backup already exists")
    shutil.copy2(STATEMENTS, statement_backup)
    shutil.copy2(MENTIONS, mention_backup)
    temp_paths: list[Path] = []
    try:
        for path, content in ((STATEMENTS, output_statements), (MENTIONS, output_mentions_bytes)):
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".tmp-", delete=False) as tmp:
                tmp.write(content)
                temp_paths.append(Path(tmp.name))
        os.replace(temp_paths[0], STATEMENTS)
        os.replace(temp_paths[1], MENTIONS)
        after_rows, _, _ = load_statements()
        require(len(after_rows) == 12667, "post-write statement count mismatch")
        require(sum(s.get("qualifiers", {}).get("relation_candidate") is True for s in after_rows) == 3639, "post-write relation candidate count mismatch")
        require(sum(bool(s.get("subject_candidate_id") and s.get("object_candidate_id")) and "relation_candidate" not in s.get("qualifiers", {}) for s in after_rows) == 4436, "post-write unclassified count mismatch")
        with MENTIONS.open(encoding="utf-8-sig", newline="") as f:
            after_mentions = list(csv.DictReader(f))
        require(len(after_mentions) == 27486, "post-write mention count mismatch")
        print(json.dumps({
            "result": "applied",
            "statements_sha256": sha(STATEMENTS),
            "mentions_sha256": sha(MENTIONS),
            "backups": [str(statement_backup.relative_to(ROOT)), str(mention_backup.relative_to(ROOT))],
        }, ensure_ascii=False, indent=2))
    except Exception:
        if statement_backup.exists():
            shutil.copy2(statement_backup, STATEMENTS)
        if mention_backup.exists():
            shutil.copy2(mention_backup, MENTIONS)
        raise
    finally:
        for path in temp_paths:
            if path.exists():
                path.unlink()


if __name__ == "__main__":
    main()
