#!/usr/bin/env python3
"""Separate the reported 1654 comments from Haskell's Hanotaux citation.

Default mode performs a guarded dry run. Pass --apply to write after all checks.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import io
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
STATEMENTS_SHA = "97638a76da75dee567f8ec0306de06c5eab4ef2f800193cdff5b70ab46703cb5"
MENTIONS_SHA = "223072dfc14c44d6f1098c71653a2ea90230479e4af21d569eb14d4c25f84be4"
CANDIDATES_SHA = "b4ac5c42748249c553bf133ab9267acb9fbb85422d1198208b19b7e8b8c250de"
SOURCE_SHA = "5f2ec3c85927ed4aded258d7a6b1801ccb3b8e0416f0f3f9e57ad7b2fae8dd4c"
BACKUP_SUFFIX = ".bak-s2-handoff-chp2-p60-note4-20261010"

OLD_ID = "st-chp2-secvii-l38-54-fn-p60-4-french-ministers-comments"
NEW_ID = "st-chp2-secvii-l38-54-fn-p60-4-hanotaux-citation"
BODY_ID = "st-chp2-secvii-l21-30-francesco-political-sympathies-after-exile"
GROUP_CANDIDATE = "cand-4952"
FRANCESCO_CANDIDATE = "cand-0199"
HANOTAUX_CANDIDATE = "cand-4953"
FRANCE_POLITY_CANDIDATE = "cand-4221"
FRANCE_PLACE_CANDIDATE = "cand-4266"
BOOK_CANDIDATE = "cand-2962"

MINISTERS_MENTION = "m-chp2-secvii-l38-54-0022"
QUOTE_FRANCE_MENTION = "m-chp2-secvii-l38-54-0023"
HANOTAUX_MENTION = "m-chp2-secvii-l38-54-0024"
BODY_FRANCE_MENTION = "m-chp2-secvii-l21-30-0051"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"preflight failed: {message}")


def read_statements() -> tuple[list[dict], list[bytes], bool]:
    raw = STATEMENTS.read_bytes()
    lines = raw.splitlines(keepends=True)
    rows = [json.loads(line.decode("utf-8-sig")) for line in lines if line.strip()]
    return rows, lines, raw.startswith(b"\xef\xbb\xbf")


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[bytes], list[str], bool]:
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    decoded = raw.decode("utf-8-sig")
    physical_lines = decoded.splitlines(keepends=True)
    require(bool(physical_lines), f"empty CSV: {path.name}")
    reader = csv.reader(io.StringIO(decoded, newline=""))
    fieldnames = next(reader, None)
    require(fieldnames is not None, f"missing CSV header: {path.name}")
    header_end = reader.line_num
    records: list[bytes] = []
    rows: list[dict[str, str]] = []
    line_cursor = header_end
    for row in reader:
        line_end = reader.line_num
        require(len(row) == len(fieldnames), f"CSV column count mismatch in {path.name}")
        records.append("".join(physical_lines[line_cursor:line_end]).encode("utf-8"))
        line_cursor = line_end
        rows.append(dict(zip(fieldnames, row)))
    require(line_cursor == len(physical_lines), f"unparsed trailing CSV data in {path.name}")
    header_bytes = "".join(physical_lines[:header_end]).encode("utf-8")
    return rows, [header_bytes, *records], fieldnames, bom


def counts(rows: list[dict]) -> dict[str, int]:
    relations = [s for s in rows if s.get("qualifiers", {}).get("relation_candidate") is True]
    return {
        "statements": len(rows),
        "relations": len(relations),
        "complete_relations": sum(bool(s.get("subject_candidate_id") and s.get("object_candidate_id")) for s in relations),
        "open_relations": sum(not (s.get("subject_candidate_id") and s.get("object_candidate_id")) for s in relations),
        "dual_unclassified": sum(
            bool(s.get("subject_candidate_id") and s.get("object_candidate_id"))
            and "relation_candidate" not in s.get("qualifiers", {})
            for s in rows
        ),
        "footnote_claims": sum(s.get("predicate") == "footnote-claim" for s in rows),
        "cites": sum(s.get("predicate") == "cites" and s.get("qualifiers", {}).get("relation_candidate") is True for s in rows),
    }


def preflight():
    for path, expected in (
        (STATEMENTS, STATEMENTS_SHA),
        (MENTIONS, MENTIONS_SHA),
        (CANDIDATES, CANDIDATES_SHA),
        (SOURCE, SOURCE_SHA),
    ):
        require(sha(path) == expected, f"unexpected SHA-256 for {path.relative_to(ROOT)}")

    statements, statement_lines, statement_bom = read_statements()
    mentions, mention_lines, mention_fields, mention_bom = read_csv(MENTIONS)
    candidates, _, _, _ = read_csv(CANDIDATES)
    by_id = {s["statement_id"]: s for s in statements}
    require(len(by_id) == len(statements), "duplicate statement_id")
    require(OLD_ID in by_id and NEW_ID not in by_id, "statement target or new ID changed")
    old = by_id[OLD_ID]
    q = old.get("qualifiers", {})
    require(old["predicate"] == "footnote-claim", "target predicate changed")
    require(old["subject_candidate_id"] == FRANCESCO_CANDIDATE and old["object_candidate_id"] == GROUP_CANDIDATE,
            "target endpoints changed")
    require(q.get("print_page") == 60 and q.get("footnote_marker") == 4 and q.get("source_line_start") == 47,
            "print locator changed")
    require(old["original_quote"] == "4 See the biting comments made about him by the French ministers in 1654: ‘... tout à fait suspect à la France . ..jalousie, envie, vengeance, ingratitude... . .’ in Hanotaux, p. 8 and pp. 12-13.",
            "OCR quote changed")

    candidate_by_id = {c["candidate_id"]: c for c in candidates}
    required_candidates = {
        FRANCESCO_CANDIDATE: "person",
        HANOTAUX_CANDIDATE: "archive",
        FRANCE_POLITY_CANDIDATE: "institution",
        FRANCE_PLACE_CANDIDATE: "place",
        BOOK_CANDIDATE: "archive",
    }
    for candidate_id, kind in required_candidates.items():
        c = candidate_by_id.get(candidate_id)
        require(c is not None and c["suggested_type"] == kind and c["status"] == "open",
                f"candidate {candidate_id} changed")
    group = candidate_by_id.get(GROUP_CANDIDATE)
    require(group is not None and group["status"] == "open" and not group["suggested_type"],
            "unnamed ministers group candidate changed")
    require("political power in Haskell" in candidate_by_id[FRANCE_POLITY_CANDIDATE]["canonical_name"],
            "France polity candidate identity changed")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    require(source_lines[46] == old["original_quote"], "source line 47 changed")
    footnote_segment = "\n".join(source_lines[37:54])
    require(footnote_segment[641:644] == "him", "Francesco pronoun span changed")
    require(footnote_segment[648:668] == "the French ministers", "ministers mention span changed")
    require(footnote_segment[708:714] == "France", "quoted France span changed")
    require(footnote_segment[770:778] == "Hanotaux", "Hanotaux mention span changed")
    body_segment = "\n".join(source_lines[20:30])
    require(body_segment[1668:1674] == "France", "body France mention span changed")

    mention_by_id = {m["mention_id"]: m for m in mentions}
    expected_mentions = {
        MINISTERS_MENTION: (GROUP_CANDIDATE, "the French ministers", "648", "668"),
        QUOTE_FRANCE_MENTION: (FRANCE_PLACE_CANDIDATE, "France", "708", "714"),
        HANOTAUX_MENTION: (HANOTAUX_CANDIDATE, "Hanotaux", "770", "778"),
        BODY_FRANCE_MENTION: (FRANCE_PLACE_CANDIDATE, "France", "1668", "1674"),
    }
    for mention_id, (candidate_id, surface, start, end) in expected_mentions.items():
        m = mention_by_id.get(mention_id)
        require(m is not None and (m["candidate_id"], m["surface_form"], m["start_char"], m["end_char"])
                == (candidate_id, surface, start, end), f"mention {mention_id} changed")

    body = by_id.get(BODY_ID)
    require(body is not None and body.get("object_candidate_id") == FRANCE_PLACE_CANDIDATE,
            "body sympathy statement endpoint changed")
    refs = body.get("qualifiers", {}).get("footnote_refs", [])
    ref = next((r for r in refs if isinstance(r, dict) and r.get("marker") == 4
                and r.get("segment_id") == old["segment_id"] and r.get("source_line") == 47), None)
    require(ref is not None and ref.get("statement_ids") == [OLD_ID], "body-to-footnote link changed")

    before = counts(statements)
    expected_before = {
        "statements": 12668, "relations": 3640, "complete_relations": 3626,
        "open_relations": 14, "dual_unclassified": 4435, "footnote_claims": 11, "cites": 108,
    }
    require(before == expected_before, f"current ledger counts differ: {before}")
    return statements, statement_lines, statement_bom, mentions, mention_lines, mention_fields, mention_bom, candidates


def make_changes(statements: list[dict], mentions: list[dict[str, str]]):
    rows = copy.deepcopy(statements)
    updated_mentions = copy.deepcopy(mentions)
    by_id = {s["statement_id"]: s for s in rows}
    old = by_id[OLD_ID]
    old["subject_candidate_id"] = GROUP_CANDIDATE
    old["object_candidate_id"] = FRANCESCO_CANDIDATE
    old["predicate"] = "reported_critical_comments_about"
    q = old["qualifiers"]
    q["claim"] = "Haskell reports that unnamed French ministers made biting comments about Francesco in 1654, calling him suspect to France and alleging jealousy, envy, vengeance, and ingratitude."
    q["speaker"] = "Haskell"
    q["text_layer"] = "authorial footnote reporting comments"
    q["qualification"] = "The French wording is relayed through Hanotaux, pages 8 and 12-13; those pages and the underlying ministerial document were not independently consulted. The actor remains an unnamed group, and the statement is only an S2 relation candidate."
    q.pop("place_candidate_id", None)
    q.pop("cited_publication_candidate_id", None)
    q["reported_via_publication_candidate_id"] = HANOTAUX_CANDIDATE
    q["political_entity_candidate_id"] = FRANCE_POLITY_CANDIDATE
    q["date"] = "1654"
    q["relation_candidate"] = True
    q["relation_candidate_note"] = "The footnote explicitly attributes a directed critical-comment act to an unnamed French ministerial group about Francesco. This is an S2 candidate only; the group identity remains open and no formal S6 relation is created."
    q["related_body_statement_ids"] = [BODY_ID]

    citation = {
        "statement_id": NEW_ID,
        "segment_id": old["segment_id"],
        "subject_candidate_id": BOOK_CANDIDATE,
        "object_candidate_id": HANOTAUX_CANDIDATE,
        "predicate": "cites",
        "qualifiers": {
            "source_line_start": 47,
            "source_line_end": 47,
            "claim": "Haskell's footnote cites Hanotaux, p. 8 and pp. 12-13, for its report of the French ministers' 1654 comments about Francesco.",
            "speaker": "Haskell, footnote",
            "text_layer": "bibliographic citation",
            "qualification": "This records the citation route in Haskell. The cited pages and the underlying ministerial document were not independently consulted, so the citation does not independently verify the reported comments.",
            "footnote_marker": 4,
            "print_page": 60,
            "pdf_physical_page": 49,
            "citation_publication_candidate_id": HANOTAUX_CANDIDATE,
            "citation_context_candidate_ids": [FRANCESCO_CANDIDATE, GROUP_CANDIDATE],
            "linked_body_statement_ids": [BODY_ID],
            "citations": [{
                "source_candidate_id": HANOTAUX_CANDIDATE,
                "publication_candidate_id": HANOTAUX_CANDIDATE,
                "locator": "p. 8 and pp. 12-13",
                "reference_as_printed": "Hanotaux, p. 8 and pp. 12-13",
            }],
            "cited_material_not_independently_consulted": True,
            "relation_candidate": True,
            "relation_candidate_note": "This records Haskell's bibliographic link to the cited archive only; it does not validate the report or create a formal S6 edge.",
        },
        "original_quote": old["original_quote"],
        "origin": old["origin"],
        "source_file": old["source_file"],
    }
    updated_rows: list[dict] = []
    for row in rows:
        updated_rows.append(row)
        if row["statement_id"] == OLD_ID:
            updated_rows.append(citation)

    mention_by_id = {m["mention_id"]: m for m in updated_mentions}
    quote_france = mention_by_id[QUOTE_FRANCE_MENTION]
    quote_france["candidate_id"] = FRANCE_POLITY_CANDIDATE
    quote_france["note"] = "France as the political polity named in the quoted comment; mapped to the chapter 2 polity candidate, not the geographic-location candidate."
    body_france = mention_by_id[BODY_FRANCE_MENTION]
    body_france["candidate_id"] = FRANCE_POLITY_CANDIDATE
    body_france["note"] = "Polity away from which Francesco's reported political sympathies shifted; not a geographic travel location."

    body = by_id[BODY_ID]
    body["object_candidate_id"] = FRANCE_POLITY_CANDIDATE
    for ref in body["qualifiers"]["footnote_refs"]:
        if isinstance(ref, dict) and ref.get("marker") == 4 and ref.get("source_line") == 47:
            ref["statement_ids"] = [OLD_ID, NEW_ID]
    return updated_rows, updated_mentions


def serialize_statements(rows: list[dict], original_lines: list[bytes], bom: bool) -> bytes:
    newline = b"\r\n" if any(line.endswith(b"\r\n") for line in original_lines) else b"\n"
    output = []
    for index, row in enumerate(rows):
        line = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if index == 0 and bom:
            line = b"\xef\xbb\xbf" + line
        output.append(line + newline)
    return b"".join(output)


def serialize_mentions(rows, original_records: list[bytes], fieldnames: list[str], bom: bool, original_rows):
    newline = "\r\n" if any(record.endswith(b"\r\n") for record in original_records) else "\n"
    output = [original_records[0]]
    for original, row, old_row in zip(original_records[1:], rows, original_rows):
        if row == old_row:
            output.append(original)
            continue
        buffer = io.StringIO(newline="")
        csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator=newline, extrasaction="ignore").writerow(row)
        output.append(buffer.getvalue().encode("utf-8"))
    return (b"\xef\xbb\xbf" if bom else b"") + b"".join(output)


def write_atomic(path: Path, content: bytes) -> Path:
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".tmp-", delete=False) as tmp:
        tmp.write(content)
        return Path(tmp.name)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the audited statement and mention changes")
    args = parser.parse_args()
    statements, statement_lines, statement_bom, mentions, mention_lines, mention_fields, mention_bom, candidates = preflight()
    updated_statements, updated_mentions = make_changes(statements, mentions)
    after = counts(updated_statements)
    expected_after = {
        "statements": 12669, "relations": 3642, "complete_relations": 3628,
        "open_relations": 14, "dual_unclassified": 4434, "footnote_claims": 10, "cites": 109,
    }
    require(after == expected_after, f"projected counts differ: {after}")
    before_mentions = {m["mention_id"]: m for m in mentions}
    after_mentions = {m["mention_id"]: m for m in updated_mentions}
    preview = {
        "action": "apply" if args.apply else "dry-run",
        "before": counts(statements),
        "after": after,
        "candidate_rows": len(candidates),
        "mention_rows": f"{len(mentions)} -> {len(updated_mentions)}",
        "mention_reassignments": [
            {"id": mid, "from": before_mentions[mid]["candidate_id"], "to": after_mentions[mid]["candidate_id"], "span": [before_mentions[mid]["start_char"], before_mentions[mid]["end_char"]]}
            for mid in (QUOTE_FRANCE_MENTION, BODY_FRANCE_MENTION)
        ],
        "body_endpoint": {"statement": BODY_ID, "from": FRANCE_PLACE_CANDIDATE, "to": FRANCE_POLITY_CANDIDATE},
        "statement_change": {"id": OLD_ID, "from": {"predicate": "footnote-claim", "subject": FRANCESCO_CANDIDATE, "object": GROUP_CANDIDATE}, "to": {"predicate": "reported_critical_comments_about", "subject": GROUP_CANDIDATE, "object": FRANCESCO_CANDIDATE, "relation_candidate": True}},
        "new_citation": {"id": NEW_ID, "predicate": "cites", "subject": BOOK_CANDIDATE, "object": HANOTAUX_CANDIDATE, "locators": ["p. 8", "pp. 12-13"]},
        "body_footnote_links": [OLD_ID, NEW_ID],
    }
    print(json.dumps(preview, ensure_ascii=True, indent=2))
    if not args.apply:
        return

    statement_backup = STATEMENTS.with_name(STATEMENTS.name + BACKUP_SUFFIX)
    mention_backup = MENTIONS.with_name(MENTIONS.name + BACKUP_SUFFIX)
    require(not statement_backup.exists() and not mention_backup.exists(), "recovery backup already exists")
    shutil.copy2(STATEMENTS, statement_backup)
    shutil.copy2(MENTIONS, mention_backup)
    temps: list[Path] = []
    try:
        temps = [
            write_atomic(STATEMENTS, serialize_statements(updated_statements, statement_lines, statement_bom)),
            write_atomic(MENTIONS, serialize_mentions(updated_mentions, mention_lines, mention_fields, mention_bom, mentions)),
        ]
        os.replace(temps[0], STATEMENTS)
        os.replace(temps[1], MENTIONS)
        result, _, _ = read_statements()
        require(counts(result) == expected_after, "post-write statement counts mismatch")
        with MENTIONS.open(encoding="utf-8-sig", newline="") as f:
            result_mentions = list(csv.DictReader(f))
        result_by_id = {m["mention_id"]: m for m in result_mentions}
        require(len(result_mentions) == len(mentions), "post-write mention row count changed")
        require(result_by_id[QUOTE_FRANCE_MENTION]["candidate_id"] == FRANCE_POLITY_CANDIDATE
                and result_by_id[BODY_FRANCE_MENTION]["candidate_id"] == FRANCE_POLITY_CANDIDATE,
                "post-write France mention mapping failed")
        result_by_statement = {s["statement_id"]: s for s in result}
        require(result_by_statement[BODY_ID]["object_candidate_id"] == FRANCE_POLITY_CANDIDATE,
                "post-write body endpoint failed")
        refs = result_by_statement[BODY_ID]["qualifiers"]["footnote_refs"]
        ref = next(r for r in refs if isinstance(r, dict) and r.get("marker") == 4 and r.get("source_line") == 47)
        require(ref["statement_ids"] == [OLD_ID, NEW_ID], "post-write reciprocal footnote links failed")
        print(json.dumps({
            "result": "applied",
            "statements_sha256": sha(STATEMENTS),
            "mentions_sha256": sha(MENTIONS),
            "backups": [str(statement_backup.relative_to(ROOT)), str(mention_backup.relative_to(ROOT))],
        }, indent=2))
    except Exception:
        shutil.copy2(statement_backup, STATEMENTS)
        shutil.copy2(mention_backup, MENTIONS)
        raise
    finally:
        for temp in temps:
            if temp.exists():
                temp.unlink()


if __name__ == "__main__":
    main()
