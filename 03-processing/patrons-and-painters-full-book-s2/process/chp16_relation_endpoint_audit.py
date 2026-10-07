"""Controlled Chapter 16 S2 relation-candidate audit.

Defaults to dry-run. The write path requires the reviewed source, segment,
candidate, statement-count, and open-endpoint preconditions to remain exact.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE_NAME = "02-sources/02-Markdown/16_CHP-16_intro.md"
SOURCE_PATH = ROOT / SOURCE_NAME
EXPECTED_SOURCE_SHA256 = "ee8516e7868b0036a753da731e10a7e201faafa45314615b45ae024c6c7507ff"
EXPECTED_SEGMENT_HASHES = {
    "chp-16:16_CHP-16_intro:l16-22": "87d6a971885fc5f2fda989b529c765ba2d1acd1ca9435f3705c3ba41c4e7dbc6",
    "chp-16:16_CHP-16_intro:l24-36": "8f91497e15e495d2f9ed395c3ecd4b66ff04bdd965293a6e543921f74ecbfdec",
    "chp-16:16_CHP-16_intro:l38-46": "4e792398d6861ac903aa6d71876765346f3b28f74d117e1b80cf5974b8ef9797",
    "chp-16:16_CHP-16_intro:l69-89": "3f2a01cb6c359faaa9158cbbca552a89228fac73308541ef3d18e3fb2304c283",
}
EXPECTED_MAX_CANDIDATE = 11473
EXPECTED_STATEMENT_COUNT = 12225
EXPECTED_RELATION_COUNTS = (2310, 2286, 24)
EXPECTED_OPEN_ENDPOINTS = {
    "st-chp16-p374-strange-modern-art-commissions": ("cand-2517", None),
    "st-chp16-p375-sasso-reputation-and-removal-of-masterpieces": ("cand-2364", None),
    "st-chp16-p376-vianello-circle-membership": ("cand-2764", None),
}
NOTE_STATEMENT_ID = "st-chp16-p375-note3-sasso-correspondents"
NOTE_QUOTE = (
    "3 Among those in touch with Sasso were A. Hume—see Lorenzetti, 1914, "
    "who publishes three letters of 1790-2; John Skippe (1778-9) and "
    "Hamilton, Marquis of Douglas (1800-2)—see letters in the Epistolario "
    "Moschini, Biblioteca Correr, Venice."
)
NEW_ROWS = [
    (
        "st-chp16-p375-hume-in-touch-with-sasso",
        "cand-1308",
        "Haskell's note names A. Hume among those in touch with Sasso.",
        "Haskell's note associates Hume with Sasso and cites three Hume letters published by Lorenzetti for 1790–1792. The note and cited letters were not independently consulted.",
        ["cand-1308", "cand-2364"],
    ),
    (
        "st-chp16-p375-skippe-in-touch-with-sasso",
        "cand-2437",
        "Haskell's note names John Skippe among those in touch with Sasso.",
        "Haskell's note places Skippe among Sasso's contacts and gives the years 1778–1779; it does not identify a particular letter for this claim, and the cited papers were not independently consulted.",
        ["cand-2437", "cand-2364"],
    ),
    (
        "st-chp16-p375-douglas-in-touch-with-sasso",
        "cand-0946",
        "Haskell's note names Hamilton, Marquis of Douglas, among those in touch with Sasso.",
        "Haskell's note places Douglas among Sasso's contacts and gives the years 1800–1802; it does not identify a particular letter for this claim, and the cited papers were not independently consulted.",
        ["cand-0946", "cand-2364"],
    ),
]
NEW_STATEMENT_IDS = {row[0] for row in NEW_ROWS}


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def encode_jsonl(rows):
    return "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)


def atomic_write(path: Path, text: str):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        f.write(text)
        temporary = Path(f.name)
    temporary.replace(path)


def relation_counts(rows):
    relations = [r for r in rows if r.get("qualifiers", {}).get("relation_candidate") is True]
    complete = sum(bool(r.get("subject_candidate_id") and r.get("object_candidate_id")) for r in relations)
    return len(relations), complete, len(relations) - complete


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the reviewed changes; default is dry-run")
    parser.add_argument("--show-diff", action="store_true", help="print before/after rows in dry-run")
    args = parser.parse_args()

    candidate_path = TABLES / "entity-candidates.csv"
    statement_path = TABLES / "book-statements.jsonl"
    segment_path = TABLES / "segments.jsonl"
    if hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest() != EXPECTED_SOURCE_SHA256:
        raise SystemExit("Chapter 16 source asset changed")
    source_lines = SOURCE_PATH.read_text(encoding="utf-8-sig").splitlines()
    segment_by_id = {r["segment_id"]: r for r in read_jsonl(segment_path)}
    for segment_id, expected_hash in EXPECTED_SEGMENT_HASHES.items():
        meta = segment_by_id.get(segment_id)
        if (
            not meta
            or meta.get("source_file") != SOURCE_NAME
            or meta.get("sha256") != expected_hash
            or meta.get("asset_sha256") != EXPECTED_SOURCE_SHA256
        ):
            raise SystemExit(f"source segment manifest changed: {segment_id}")
        excerpt = "\n".join(source_lines[int(meta["line_start"]) - 1 : int(meta["line_end"])])
        if hashlib.sha256(excerpt.encode("utf-8")).hexdigest() != expected_hash:
            raise SystemExit(f"source segment hash mismatch: {segment_id}")

    with candidate_path.open(encoding="utf-8-sig", newline="") as f:
        candidates = list(csv.DictReader(f))
    statements = read_jsonl(statement_path)
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    statement_by_id = {r["statement_id"]: r for r in statements}
    if len(candidate_by_id) != len(candidates) or len(statement_by_id) != len(statements):
        raise SystemExit("duplicate identifiers in candidate or statement table")
    if max(int(r["candidate_id"].split("-")[-1]) for r in candidates) != EXPECTED_MAX_CANDIDATE:
        raise SystemExit("candidate sequence changed")
    if len(statements) != EXPECTED_STATEMENT_COUNT or relation_counts(statements) != EXPECTED_RELATION_COUNTS:
        raise SystemExit(f"table counts changed: statements={len(statements)}, relations={relation_counts(statements)}")

    open_ids = {
        r["statement_id"]: (r.get("subject_candidate_id"), r.get("object_candidate_id"))
        for r in statements
        if r["statement_id"].startswith("st-chp16-")
        and r.get("qualifiers", {}).get("relation_candidate") is True
        and (not r.get("subject_candidate_id") or not r.get("object_candidate_id"))
    }
    if open_ids != EXPECTED_OPEN_ENDPOINTS:
        raise SystemExit(f"Chapter 16 open endpoint set changed: {open_ids}")
    if not NEW_STATEMENT_IDS.isdisjoint(statement_by_id):
        raise SystemExit("one or more planned statement IDs already exist")

    note = statement_by_id.get(NOTE_STATEMENT_ID)
    if not note or note.get("original_quote") != NOTE_QUOTE:
        raise SystemExit("the p.375 note 3 source statement changed")
    note_qualifiers = note.get("qualifiers", {})
    required_note_candidates = {"cand-2364", "cand-1308", "cand-2437", "cand-0946"}
    if not required_note_candidates <= set(note_qualifiers.get("mentioned_candidate_ids", [])):
        raise SystemExit("the named Sasso contacts are no longer attached to note 3")
    if note_qualifiers.get("footnote_body_link_status") != "linked" or note_qualifiers.get("footnote_body_line_range") != "L28-L29":
        raise SystemExit("the note 3 to p.375 body link changed")
    for candidate_id in required_note_candidates:
        if candidate_id not in candidate_by_id:
            raise SystemExit(f"missing note 3 candidate: {candidate_id}")
    for candidate_id in {"cand-1308", "cand-2437", "cand-0946", "cand-2364"}:
        if candidate_by_id[candidate_id].get("suggested_type") != "person":
            raise SystemExit(f"candidate type precondition changed: {candidate_id}")

    before = copy.deepcopy(statement_by_id)
    nonrelations = {
        "st-chp16-p374-strange-modern-art-commissions": (
            "The source describes occasional commissions for Strange himself or an unnamed client but identifies neither a particular commissioned work nor which recipient applies; keep the aggregate report as an assertion."
        ),
        "st-chp16-p375-sasso-reputation-and-removal-of-masterpieces": (
            "Haskell's evaluative account concerns unnamed English dealers and an unspecified body of works and transactions. Note 3's named contacts are split into separate person-to-Sasso candidates; this broad causal and collective account remains an assertion."
        ),
        "st-chp16-p376-vianello-circle-membership": (
            "Haskell says Vianello may have belonged to an undefined circle associated with Sasso and della Lena. The hedge and group boundary are unresolved; this does not assert separate membership relations with either person."
        ),
    }
    for statement_id, qualification in nonrelations.items():
        statement_by_id[statement_id]["qualifiers"]["relation_candidate"] = False
        statement_by_id[statement_id]["qualifiers"]["qualification"] = qualification

    note["qualifiers"]["relation_candidate"] = False
    note["qualifiers"]["qualification"] = (
        "This aggregate note summary is retained as source context; separate candidate statements record each named person-to-Sasso contact. "
        "The cited letters and Lorenzetti's publication were not independently consulted, and the note does not map every person to a particular preserved letter."
    )

    added = []
    for new_id, person_id, claim, qualification, mentioned in NEW_ROWS:
        row = copy.deepcopy(note)
        row["statement_id"] = new_id
        row["subject_candidate_id"] = person_id
        row["object_candidate_id"] = "cand-2364"
        row["predicate"] = "was_in_touch_with"
        row["original_quote"] = NOTE_QUOTE
        q = row["qualifiers"]
        q["source_line_start"] = 78
        q["source_line_end"] = 78
        q["claim"] = claim
        q["speaker"] = "Haskell's note"
        q["text_layer"] = "archival and secondary-source locator"
        q["qualification"] = qualification
        q["mentioned_candidate_ids"] = mentioned
        q["relation_candidate"] = True
        q["cited_source_independently_consulted"] = False
        q["footnote_link_note"] = "Candidate contact statement sourced from note 3; the cited letters remain unverified."
        added.append(row)

    statements.extend(added)
    statement_by_id.update({row["statement_id"]: row for row in added})
    candidate_ids = set(candidate_by_id)
    for row in statements:
        for candidate_id in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if candidate_id and candidate_id not in candidate_ids:
                raise SystemExit(f"missing statement endpoint candidate: {row['statement_id']} -> {candidate_id}")
        for candidate_id in row.get("qualifiers", {}).get("mentioned_candidate_ids", []):
            if candidate_id not in candidate_ids:
                raise SystemExit(f"missing mentioned candidate: {row['statement_id']} -> {candidate_id}")

    remaining = {
        row["statement_id"]
        for row in statements
        if row["statement_id"].startswith("st-chp16-")
        and row.get("qualifiers", {}).get("relation_candidate") is True
        and (not row.get("subject_candidate_id") or not row.get("object_candidate_id"))
    }
    if remaining:
        raise SystemExit(f"unexpected Chapter 16 unresolved endpoint set: {sorted(remaining)}")
    expected_after = (2310, 2289, 21)
    if len(statements) != 12228 or relation_counts(statements) != expected_after:
        raise SystemExit(f"planned aggregate counts differ: statements={len(statements)}, relations={relation_counts(statements)}")

    print("Chapter 16 S2 relation-candidate audit plan")
    print("open endpoint candidates: 3 -> 0; 3 specific contacts from note 3 split into person-to-Sasso rows")
    print("the generic commission claim, broad Sasso assessment, Vianello circle-membership hedge, and aggregate note remain assertions")
    print(f"statements: {EXPECTED_STATEMENT_COUNT} -> {len(statements)}")
    print(f"relation candidates (total/complete/open): {EXPECTED_RELATION_COUNTS} -> {relation_counts(statements)}")
    for statement_id in sorted(set(nonrelations) | {NOTE_STATEMENT_ID} | NEW_STATEMENT_IDS):
        row = statement_by_id[statement_id]
        q = row.get("qualifiers", {})
        print(f"{statement_id}: {row.get('subject_candidate_id') or '∅'} → {row.get('object_candidate_id') or '∅'}; relation={q.get('relation_candidate')}; {q.get('claim')}")
        if args.show_diff:
            if statement_id in before:
                print("  BEFORE", json.dumps(before[statement_id], ensure_ascii=False))
            print("  AFTER ", json.dumps(row, ensure_ascii=False))
    if not args.apply:
        print("DRY-RUN only; inspect this plan, then pass --apply to write.")
        return

    backup_dir = Path(tempfile.mkdtemp(prefix="pnp-chp16-s2-relation-audit-"))
    shutil.copy2(statement_path, backup_dir / statement_path.name)
    atomic_write(statement_path, encode_jsonl(statements))
    written = read_jsonl(statement_path)
    if len(written) != 12228 or relation_counts(written) != expected_after:
        raise SystemExit("post-write verification failed; restore copy is available")
    written_ids = {row["statement_id"] for row in written}
    if not NEW_STATEMENT_IDS <= written_ids:
        raise SystemExit("one or more planned statements are missing after write")
    print(f"APPLIED; recovery copy: {backup_dir}")


if __name__ == "__main__":
    main()
