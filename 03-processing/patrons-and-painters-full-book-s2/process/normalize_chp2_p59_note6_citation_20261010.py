#!/usr/bin/env python3
"""Separate the reported disappearance of the Xenophon painting from its citation.

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
STATEMENTS_SHA = "a6b45f0f86494891e81ae74746ee6b85df71443ffcb91d11cce2152b134dc250"
MENTIONS_SHA = "1dabacecf00af014d87d42e6cad24d1e24d59880725f25634eb005d420d694ca"
CANDIDATES_SHA = "b4ac5c42748249c553bf133ab9267acb9fbb85422d1198208b19b7e8b8c250de"
SOURCE_SHA = "5f2ec3c85927ed4aded258d7a6b1801ccb3b8e0416f0f3f9e57ad7b2fae8dd4c"
BACKUP_SUFFIX = ".bak-s2-handoff-chp2-p59-note6-20261010"

OLD_ID = "st-chp2-secvii-l38-54-fn-p59-6-briganti-picture-disappeared"
NEW_ID = "st-chp2-secvii-l38-54-fn-p59-6-briganti-citation"
BODY_ID = "st-chp2-secvii-l5-19-antonio-returns-and-xenophon-picture"
MENTION_ID = "m-chp2-secvii-l38-54-0053"
PICTURE_CANDIDATE = "cand-4913"
PUBLICATION_CANDIDATE = "cand-4473"
BOOK_CANDIDATE = "cand-2962"


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


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[bytes]]:
    raw_lines = path.read_bytes().splitlines(keepends=True)
    rows = list(csv.DictReader(path.read_text(encoding="utf-8-sig").splitlines()))
    return rows, raw_lines


def counts(rows: list[dict]) -> dict[str, int]:
    relations = [s for s in rows if s.get("qualifiers", {}).get("relation_candidate") is True]
    return {
        "statements": len(rows),
        "relations": len(relations),
        "complete_relations": sum(bool(s.get("subject_candidate_id") and s.get("object_candidate_id")) for s in relations),
        "open_relations": sum(not (s.get("subject_candidate_id") and s.get("object_candidate_id")) for s in relations),
        "dual_unclassified": sum(bool(s.get("subject_candidate_id") and s.get("object_candidate_id")) and "relation_candidate" not in s.get("qualifiers", {}) for s in rows),
        "footnote_claims": sum(s.get("predicate") == "footnote-claim" for s in rows),
        "cites": sum(s.get("predicate") == "cites" and s.get("qualifiers", {}).get("relation_candidate") is True for s in rows),
    }


def preflight() -> tuple[list[dict], list[bytes], bool, list[dict[str, str]], list[bytes], list[dict[str, str]]]:
    for path, expected in (
        (STATEMENTS, STATEMENTS_SHA),
        (MENTIONS, MENTIONS_SHA),
        (CANDIDATES, CANDIDATES_SHA),
        (SOURCE, SOURCE_SHA),
    ):
        require(sha(path) == expected, f"unexpected SHA-256 for {path.relative_to(ROOT)}")

    statements, statement_lines, statement_bom = read_statements()
    mentions, mention_lines = read_csv(MENTIONS)
    candidates, _ = read_csv(CANDIDATES)
    by_id = {s["statement_id"]: s for s in statements}
    require(len(by_id) == len(statements), "duplicate statement_id")
    require(OLD_ID in by_id and NEW_ID not in by_id, "statement target or new ID changed")
    old = by_id[OLD_ID]
    require(old["predicate"] == "footnote-claim", "target predicate changed")
    require(old["subject_candidate_id"] == PICTURE_CANDIDATE and old["object_candidate_id"] == PUBLICATION_CANDIDATE, "target endpoints changed")
    require(old.get("qualifiers", {}).get("print_page") == 59 and old["qualifiers"].get("footnote_marker") == 6, "print locator changed")
    require(old["original_quote"] == "8 Briganti, 1962, p. 254. The picture has disappeared.", "OCR quote changed")

    candidate_by_id = {c["candidate_id"]: c for c in candidates}
    for candidate_id, kind in ((PICTURE_CANDIDATE, "work"), (PUBLICATION_CANDIDATE, "archive"), (BOOK_CANDIDATE, "archive")):
        c = candidate_by_id.get(candidate_id)
        require(c is not None and c["suggested_type"] == kind and c["status"] == "open", f"candidate {candidate_id} changed")

    source_text = SOURCE.read_text(encoding="utf-8-sig")
    source_lines = source_text.splitlines()
    require(source_lines[43] == "8 Briganti, 1962, p. 254. The picture has disappeared.", "source line 44 changed")
    segment_text = "\n".join(source_lines[37:54])
    require(segment_text[287:298] == "The picture", "anaphoric mention span changed")

    mention_by_id = {m["mention_id"]: m for m in mentions}
    require(MENTION_ID not in mention_by_id, "new mention ID already exists")
    briganti = mention_by_id.get("m-chp2-secvii-l38-54-0011")
    require(briganti is not None and briganti["candidate_id"] == PUBLICATION_CANDIDATE and briganti["start_char"] == "263" and briganti["end_char"] == "277", "Briganti mention changed")

    body = by_id.get(BODY_ID)
    require(body is not None, "body statement missing")
    refs = body.get("qualifiers", {}).get("footnote_refs", [])
    ref = next((r for r in refs if isinstance(r, dict) and r.get("marker") == 6 and r.get("segment_id") == old["segment_id"] and r.get("source_line") == 44), None)
    require(ref is not None and ref.get("statement_ids") == [OLD_ID], "body-to-footnote link changed")
    before = counts(statements)
    expected_before = {"statements": 12667, "relations": 3639, "complete_relations": 3625, "open_relations": 14, "dual_unclassified": 4436, "footnote_claims": 12, "cites": 107}
    require(before == expected_before, f"current ledger counts differ: {before}")
    return statements, statement_lines, statement_bom, mentions, mention_lines, candidates


def make_changes(statements: list[dict], mentions: list[dict[str, str]]) -> tuple[list[dict], list[dict[str, str]]]:
    rows = copy.deepcopy(statements)
    by_id = {s["statement_id"]: s for s in rows}
    old = by_id[OLD_ID]
    old["object_candidate_id"] = None
    old["predicate"] = "reported_missing_by_book_publication"
    q = old["qualifiers"]
    q["claim"] = "Haskell says that the Xenophon painting discussed in the preceding text had disappeared."
    q["speaker"] = "Haskell, footnote"
    q["text_layer"] = "authorial note"
    q["qualification"] = "Book-reported status; Briganti p. 254 is cited but was not independently consulted. This is not a present-day location check."
    q["relation_candidate"] = False
    q["related_body_statement_ids"] = [BODY_ID]

    citation = {
        "statement_id": NEW_ID,
        "segment_id": old["segment_id"],
        "subject_candidate_id": BOOK_CANDIDATE,
        "object_candidate_id": PUBLICATION_CANDIDATE,
        "predicate": "cites",
        "qualifiers": {
            "source_line_start": 44,
            "source_line_end": 44,
            "claim": "Haskell's footnote cites Briganti (1962, p. 254) in connection with its report that the Xenophon painting had disappeared.",
            "speaker": "Haskell, footnote",
            "text_layer": "bibliographic citation",
            "qualification": "This records Haskell's citation. Briganti p. 254 was not independently consulted and does not independently verify the reported disappearance.",
            "footnote_marker": 6,
            "print_page": 59,
            "pdf_physical_page": 48,
            "page": 254,
            "linked_body_statement_ids": [BODY_ID],
            "citation_context_candidate_ids": [PICTURE_CANDIDATE],
            "cited_material_not_independently_consulted": True,
            "relation_candidate": True,
            "relation_candidate_note": "The footnote explicitly cites this archive from Haskell's book; this records the bibliographic link only and creates no formal S6 edge.",
        },
        "original_quote": old["original_quote"],
        "origin": old["origin"],
        "source_file": old["source_file"],
    }
    updated: list[dict] = []
    for row in rows:
        updated.append(row)
        if row["statement_id"] == OLD_ID:
            updated.append(citation)

    new_mention = {
        "mention_id": MENTION_ID,
        "segment_id": "chp-2:02_CHP-2_sec_vii:l38-54",
        "candidate_id": PICTURE_CANDIDATE,
        "surface_form": "The picture",
        "start_char": "287",
        "end_char": "298",
        "note": "Anaphoric mention of the Xenophon painting described in the preceding body passage.",
    }
    updated_mentions = [*mentions, new_mention]

    body = next(s for s in updated if s["statement_id"] == BODY_ID)
    for ref in body["qualifiers"]["footnote_refs"]:
        if isinstance(ref, dict) and ref.get("marker") == 6 and ref.get("source_line") == 44:
            ref["statement_ids"] = [OLD_ID, NEW_ID]
    return updated, updated_mentions


def serialize_statements(rows: list[dict], original_lines: list[bytes], bom: bool) -> bytes:
    newline = b"\r\n" if any(x.endswith(b"\r\n") for x in original_lines) else b"\n"
    out = []
    for i, row in enumerate(rows):
        line = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if i == 0 and bom:
            line = b"\xef\xbb\xbf" + line
        out.append(line + newline)
    return b"".join(out)


def serialize_mentions(rows: list[dict[str, str]], original_lines: list[bytes]) -> bytes:
    newline = "\r\n" if any(x.endswith(b"\r\n") for x in original_lines) else "\n"
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=["mention_id", "segment_id", "candidate_id", "surface_form", "start_char", "end_char", "note"], lineterminator=newline)
    writer.writerow(rows[-1])
    raw = MENTIONS.read_bytes()
    if raw and not raw.endswith((b"\n", b"\r")):
        raw += newline.encode("ascii")
    return raw + buffer.getvalue().encode("utf-8")


def write_atomic(path: Path, content: bytes) -> Path:
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".tmp-", delete=False) as tmp:
        tmp.write(content)
        return Path(tmp.name)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the audited statement and mention changes")
    args = parser.parse_args()
    statements, statement_lines, statement_bom, mentions, mention_lines, candidates = preflight()
    updated_statements, updated_mentions = make_changes(statements, mentions)
    after = counts(updated_statements)
    expected_after = {"statements": 12668, "relations": 3640, "complete_relations": 3626, "open_relations": 14, "dual_unclassified": 4435, "footnote_claims": 11, "cites": 108}
    require(after == expected_after, f"projected counts differ: {after}")
    preview = {
        "action": "apply" if args.apply else "dry-run",
        "before": counts(statements),
        "after": after,
        "candidate_rows": len(candidates),
        "mention_rows": f"{len(mentions)} -> {len(updated_mentions)}",
        "mention_change": {"id": MENTION_ID, "candidate": PICTURE_CANDIDATE, "surface": "The picture", "span": [287, 298]},
        "statement_change": {"id": OLD_ID, "from": {"predicate": "footnote-claim", "subject": PICTURE_CANDIDATE, "object": PUBLICATION_CANDIDATE}, "to": {"predicate": "reported_missing_by_book_publication", "subject": PICTURE_CANDIDATE, "object": None, "relation_candidate": False}},
        "new_citation": {"id": NEW_ID, "predicate": "cites", "subject": BOOK_CANDIDATE, "object": PUBLICATION_CANDIDATE, "page": 254, "relation_candidate": True},
        "body_links": [OLD_ID, NEW_ID],
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
        temps = [write_atomic(STATEMENTS, serialize_statements(updated_statements, statement_lines, statement_bom)), write_atomic(MENTIONS, serialize_mentions(updated_mentions, mention_lines))]
        os.replace(temps[0], STATEMENTS)
        os.replace(temps[1], MENTIONS)
        result, _, _ = read_statements()
        require(counts(result) == expected_after, "post-write statement counts mismatch")
        with MENTIONS.open(encoding="utf-8-sig", newline="") as f:
            result_mentions = list(csv.DictReader(f))
        require(len(result_mentions) == 27487 and any(m["mention_id"] == MENTION_ID and m["candidate_id"] == PICTURE_CANDIDATE and m["start_char"] == "287" and m["end_char"] == "298" for m in result_mentions), "post-write mention verification failed")
        print(json.dumps({"result": "applied", "statements_sha256": sha(STATEMENTS), "mentions_sha256": sha(MENTIONS), "backups": [str(statement_backup.relative_to(ROOT)), str(mention_backup.relative_to(ROOT))]}, indent=2))
    except Exception:
        shutil.copy2(statement_backup, STATEMENTS)
        shutil.copy2(mention_backup, MENTIONS)
        raise
    finally:
        for path in temps:
            if path.exists():
                path.unlink()


if __name__ == "__main__":
    main()
