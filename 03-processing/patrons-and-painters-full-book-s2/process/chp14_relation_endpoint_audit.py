"""Controlled Chapter 14 S2 relation-candidate audit.

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
SOURCE_NAME = "02-sources/02-Markdown/14_CHP-14_intro.md"
SOURCE_PATH = ROOT / SOURCE_NAME
EXPECTED_SOURCE_SHA256 = "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7"
EXPECTED_SEGMENT_HASHES = {
    "chp-14:14_CHP-14_intro:l3-12": "e40875f46c7c918079fc127c7bc9aa957e4a8d285b0dc03cb55f0435b240cf18",
    "chp-14:14_CHP-14_intro:l63-71": "def09441a0768efe65289db46f287add59632f45c8d99f53b3973b75696dc44d",
    "chp-14:14_CHP-14_intro:l85-95": "3b42bfa68085297951836e95914a95d9b4284382be03d5d890f4a469c2512055",
    "chp-14:14_CHP-14_intro:l97-105": "f25747acdfdcd2cd3d2ed19c6d1fcf5d04f351da9355ec83abffe2ac895e9e16",
    "chp-14:14_CHP-14_intro:l168-220": "72edc0571341795562aee96338a6bf5de6261bf0ee2f9948cd29ce23318edaa4",
}
EXPECTED_MAX_CANDIDATE = 11473
EXPECTED_STATEMENT_COUNT = 12217
EXPECTED_RELATION_COUNTS = (2308, 2278, 30)
EXPECTED_OPEN_ENDPOINT_IDS = {
    "st-chp14-p347-leading-position",
    "st-chp14-p347-education",
    "st-chp14-p347-bologna-contacts",
    "st-chp14-p353-bruhl-possessions-in-the-pictures",
    "st-chp14-p355-algarotti-collection-casual-disposals",
    "st-chp14-p356-encouraged-foreign-artists-study-in-italy",
    "st-chp14-p356-mixed-motives-in-dresden-purchases-and-frederick-proposals",
}
EXPECTED_ENDPOINTS = {
    "st-chp14-p347-leading-position": ("cand-0043", None),
    "st-chp14-p347-education": ("cand-0043", None),
    "st-chp14-p347-bologna-contacts": ("cand-0043", None),
    "st-chp14-p353-bruhl-possessions-in-the-pictures": ("cand-3781", None),
    "st-chp14-p355-algarotti-collection-casual-disposals": ("cand-10312", None),
    "st-chp14-p356-encouraged-foreign-artists-study-in-italy": ("cand-0063", None),
    "st-chp14-p356-mixed-motives-in-dresden-purchases-and-frederick-proposals": ("cand-0063", None),
}
NEW_ROWS = [
    ("st-chp14-p347-algarotti-close-contact-tiepolo", "st-chp14-p347-leading-position", "cand-0043", "cand-2572", "had_very_close_contact_with", "Haskell says Algarotti had very close contact with Tiepolo.", "This is Haskell’s qualitative description; it gives no dates or specific activity. The later p.349 correspondence claims are separately retained.", ["cand-0043", "cand-2572"], "; but chiefly for his clearly expressed artistic tastes and for his very close contacts with the leading painters of the day, especially the two greatest—Tiepolo and Canaletto.", 7, 7, []),
    ("st-chp14-p347-algarotti-close-contact-canaletto", "st-chp14-p347-leading-position", "cand-0043", "cand-0499", "had_very_close_contact_with", "Haskell says Algarotti had very close contact with Canaletto.", "This is Haskell’s qualitative description; it gives no dates or specific activity. The later p.349 correspondence claims are separately retained.", ["cand-0043", "cand-0499"], "; but chiefly for his clearly expressed artistic tastes and for his very close contacts with the leading painters of the day, especially the two greatest—Tiepolo and Canaletto.", 7, 7, []),
    ("st-chp14-p347-algarotti-educated-in-rome", "st-chp14-p347-education", "cand-0043", "cand-4490", "educated_in_city_for_one_year", "Haskell says Algarotti was educated in Rome for one year.", "Rome is the place named by the source; no school or teacher is identified.", ["cand-0043", "cand-4490"], "He was educated for a year in Rome, and in 1726, after the death of his father, in Bologna, where he studied principally the natural sciences and mathematics, in which he was always to be interested.", 9, 9, []),
    ("st-chp14-p347-algarotti-studied-in-bologna", "st-chp14-p347-education", "cand-0043", "cand-3398", "studied_in_city_after_1726", "Haskell says that in 1726, after his father’s death, Algarotti studied principally natural sciences and mathematics in Bologna.", "Bologna is the place named by the source; no school or teacher is identified, and the unnamed father remains unresolved.", ["cand-0043", "cand-3398", "cand-10225"], "He was educated for a year in Rome, and in 1726, after the death of his father, in Bologna, where he studied principally the natural sciences and mathematics, in which he was always to be interested.", 9, 9, []),
    ("st-chp14-p347-algarotti-corresponded-with-manfredi", "st-chp14-p347-bologna-contacts", "cand-0043", "cand-1511", "corresponded_with", "Haskell reports that Algarotti remained in constant correspondence with Eustachio Manfredi.", "Note 2 points to Bosdari’s study of Algarotti’s Bologna relationships; the cited work and correspondence were not independently consulted.", ["cand-0043", "cand-3398", "cand-1511"], "He kept up the contacts he made with the scholarly world of Bologna until the end of his Use, and remained in constant correspondence with Eustachio Manfredi, the Zanotti brothers and others whom he met during his student days.2", 9, 9, [{"source_line": 9, "ocr": "Use", "print": "life", "basis": "CHP-14.pdf physical page 1."}]),
    ("st-chp14-p347-algarotti-corresponded-with-zanotti-brothers", "st-chp14-p347-bologna-contacts", "cand-0043", "cand-10226", "corresponded_with", "Haskell reports that Algarotti remained in constant correspondence with the Zanotti brothers, collectively.", "The source names the brothers collectively. The candidate remains untyped; do not assign the relation to either brother until S3 identity review.", ["cand-0043", "cand-3398", "cand-10226"], "He kept up the contacts he made with the scholarly world of Bologna until the end of his Use, and remained in constant correspondence with Eustachio Manfredi, the Zanotti brothers and others whom he met during his student days.2", 9, 9, [{"source_line": 9, "ocr": "Use", "print": "life", "basis": "CHP-14.pdf physical page 1."}]),
    ("st-chp14-p356-algarotti-provided-introduction-for-bouchardon", "st-chp14-p356-encouraged-foreign-artists-study-in-italy", "cand-0063", "cand-0420", "provided_letter_of_introduction_for", "Haskell reports that Algarotti provided a letter of introduction for Bouchardon as an example of encouraging foreign artists to study in Italy.", "Note 3 cites letters dated 25 October 1750 and 23 April 1752 but does not map either date to Bouchardon; the cited letters were not independently consulted.", ["cand-0063", "cand-0420", "cand-10330", "cand-3461"], "He also did everything possible to encourage foreign artists to study in Italy, providing letters of introduction, for instance, for the French sculptor Bouchardon and the German painter Rode who was to be much influenced by Tiepolo.3", 102, 102, None),
    ("st-chp14-p356-algarotti-provided-introduction-for-rode", "st-chp14-p356-encouraged-foreign-artists-study-in-italy", "cand-0063", "cand-2207", "provided_letter_of_introduction_for", "Haskell reports that Algarotti provided a letter of introduction for Rode as an example of encouraging foreign artists to study in Italy.", "Note 3 cites letters dated 25 October 1750 and 23 April 1752 but does not map either date to Rode; the cited letters were not independently consulted. The adjacent claim that Tiepolo would influence Rode remains separate.", ["cand-0063", "cand-2207", "cand-10351", "cand-3461", "cand-3781"], "He also did everything possible to encourage foreign artists to study in Italy, providing letters of introduction, for instance, for the French sculptor Bouchardon and the German painter Rode who was to be much influenced by Tiepolo.3", 102, 102, None),
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
    raw = SOURCE_PATH.read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED_SOURCE_SHA256:
        raise SystemExit("Chapter 14 source asset changed")
    lines = SOURCE_PATH.read_text(encoding="utf-8-sig").splitlines()
    segment_by_id = {r["segment_id"]: r for r in read_jsonl(segment_path)}
    for segment_id, expected_hash in EXPECTED_SEGMENT_HASHES.items():
        meta = segment_by_id.get(segment_id)
        if not meta or meta.get("source_file") != SOURCE_NAME or meta.get("sha256") != expected_hash or meta.get("asset_sha256") != EXPECTED_SOURCE_SHA256:
            raise SystemExit(f"source segment manifest changed: {segment_id}")
        excerpt = "\n".join(lines[int(meta["line_start"]) - 1 : int(meta["line_end"])])
        if hashlib.sha256(excerpt.encode("utf-8")).hexdigest() != expected_hash:
            raise SystemExit(f"source segment hash mismatch: {segment_id}")

    with candidate_path.open(encoding="utf-8-sig", newline="") as f:
        candidate_reader = csv.DictReader(f)
        candidates = list(candidate_reader)
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
        r["statement_id"] for r in statements
        if r["statement_id"].startswith("st-chp14-")
        and r.get("qualifiers", {}).get("relation_candidate") is True
        and (not r.get("subject_candidate_id") or not r.get("object_candidate_id"))
    }
    if open_ids != EXPECTED_OPEN_ENDPOINT_IDS:
        raise SystemExit(f"Chapter 14 open endpoint set changed: {sorted(open_ids)}")
    for sid, endpoints in EXPECTED_ENDPOINTS.items():
        r = statement_by_id.get(sid)
        if not r or (r.get("subject_candidate_id"), r.get("object_candidate_id")) != endpoints:
            raise SystemExit(f"statement endpoint precondition changed: {sid}")
    if not NEW_STATEMENT_IDS.isdisjoint(statement_by_id):
        raise SystemExit("one or more planned statement IDs already exist")

    for body_id, note_id in {
        "st-chp14-p347-bologna-contacts": "st-chp14-p347-note2-bosdari",
        "st-chp14-p356-encouraged-foreign-artists-study-in-italy": "st-chp14-p356-note3-letters-1750-1752",
    }.items():
        q = statement_by_id[body_id].get("qualifiers", {})
        if note_id not in statement_by_id or q.get("footnote_body_link_status") != "linked" or note_id not in q.get("footnote_note_statement_ids", []):
            raise SystemExit(f"expected linked footnote changed: {body_id} -> {note_id}")
    bruhl_q = statement_by_id["st-chp14-p353-bruhl-possessions-in-the-pictures"].get("qualifiers", {})
    identity_questions = {r.get("candidate_id") for r in bruhl_q.get("candidate_identity_questions", [])}
    if identity_questions != {"cand-2590", "cand-2597"}:
        raise SystemExit("the p.353 ambiguity between Flora and Maecenas changed")
    for cid, expected_type in {
        "cand-0043": "person", "cand-0063": "person", "cand-2572": "person", "cand-0499": "person",
        "cand-4490": "place", "cand-3398": "place", "cand-1511": "person", "cand-0420": "person", "cand-2207": "person",
    }.items():
        if candidate_by_id.get(cid, {}).get("suggested_type") != expected_type:
            raise SystemExit(f"candidate type precondition changed: {cid}")
    if candidate_by_id.get("cand-10226", {}).get("suggested_type") != "":
        raise SystemExit("keep the Zanotti collective candidate untyped")

    original_by_id = copy.deepcopy(statement_by_id)
    nonrelations = {
        "st-chp14-p347-leading-position": "This is Haskell’s comparative evaluation of Algarotti’s standing, taste, collection, and commission count. The specific close-contact claims with Tiepolo and Canaletto are split into separate rows; this assessment itself is not a dyadic relation.",
        "st-chp14-p347-education": "The source gives two study locations but no school or teacher; the Rome and Bologna locations are represented in separate candidate statements. The father remains unnamed.",
        "st-chp14-p347-bologna-contacts": "This preserves the aggregate passage. Manfredi and the Zanotti brothers are split into candidate relations; the other student acquaintances remain unnamed, and the brothers remain a collective candidate for S3.",
        "st-chp14-p355-algarotti-collection-casual-disposals": "This describes acquisition and disposal patterns for an untyped collection, with no specific pictures or recipients named; retain it as a source assertion.",
        "st-chp14-p356-encouraged-foreign-artists-study-in-italy": "This preserves Haskell’s general statement about foreign artists; the two named examples are split into person-to-person candidate statements. Note 3 does not map its dates to either artist.",
        "st-chp14-p356-mixed-motives-in-dresden-purchases-and-frederick-proposals": "This is Haskell’s broad retrospective interpretation of varied purchases and proposals, not a claim with one specific relation endpoint; the individual transactions are represented elsewhere.",
    }
    for sid, qualification in nonrelations.items():
        statement_by_id[sid]["qualifiers"]["relation_candidate"] = False
        statement_by_id[sid]["qualifiers"]["qualification"] = qualification

    def clone(row_spec):
        (new_id, parent_id, subject, obj, predicate, claim, qualification, mentioned, quote, line_start, line_end, corrections) = row_spec
        row = copy.deepcopy(statement_by_id[parent_id])
        row["statement_id"] = new_id
        row["subject_candidate_id"] = subject
        row["object_candidate_id"] = obj
        row["predicate"] = predicate
        row["original_quote"] = quote
        q = row["qualifiers"]
        q["source_line_start"] = line_start
        q["source_line_end"] = line_end
        q["claim"] = claim
        q["qualification"] = qualification
        q["mentioned_candidate_ids"] = mentioned
        q["relation_candidate"] = True
        if corrections is not None:
            q["ocr_corrections"] = corrections
        return row

    added = [clone(spec) for spec in NEW_ROWS]
    statements.extend(added)
    statement_by_id.update({r["statement_id"]: r for r in added})
    candidate_ids = set(candidate_by_id)
    for row in statements:
        for cid in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if cid and cid not in candidate_ids:
                raise SystemExit(f"missing statement endpoint candidate: {row['statement_id']} -> {cid}")
        for cid in row.get("qualifiers", {}).get("mentioned_candidate_ids", []):
            if cid not in candidate_ids:
                raise SystemExit(f"missing mentioned candidate: {row['statement_id']} -> {cid}")
    remaining = {
        r["statement_id"] for r in statements
        if r["statement_id"].startswith("st-chp14-")
        and r.get("qualifiers", {}).get("relation_candidate") is True
        and (not r.get("subject_candidate_id") or not r.get("object_candidate_id"))
    }
    if remaining != {"st-chp14-p353-bruhl-possessions-in-the-pictures"}:
        raise SystemExit(f"unexpected Chapter 14 unresolved endpoint set: {sorted(remaining)}")
    if len(statements) != 12225 or relation_counts(statements) != (2310, 2286, 24):
        raise SystemExit(f"planned aggregate counts differ: statements={len(statements)}, relations={relation_counts(statements)}")

    print("Chapter 14 S2 relation-candidate audit plan")
    print("open endpoint candidates: 7 -> 1; p.353 work referent remains genuinely ambiguous between Flora and Maecenas")
    print("8 specific endpoint statements added for named contacts, study locations, and introduction-letter examples")
    print("general assessment, untyped collection profile, unnamed recipients, and broad motive synthesis retained as assertions")
    print(f"statements: {EXPECTED_STATEMENT_COUNT} -> {len(statements)}")
    print(f"relation candidates (total/complete/open): {EXPECTED_RELATION_COUNTS} -> {relation_counts(statements)}")
    changed_ids = sorted(sid for sid, row in statement_by_id.items() if sid in original_by_id and row != original_by_id[sid])
    for sid in changed_ids + sorted(NEW_STATEMENT_IDS):
        row = statement_by_id[sid]
        q = row.get("qualifiers", {})
        print(f"{sid}: {row.get('subject_candidate_id') or '∅'} → {row.get('object_candidate_id') or '∅'}; relation={q.get('relation_candidate')}; {q.get('claim')}")
        if args.show_diff:
            if sid in original_by_id:
                print("  BEFORE", json.dumps(original_by_id[sid], ensure_ascii=False))
            print("  AFTER ", json.dumps(row, ensure_ascii=False))
    if not args.apply:
        print("DRY-RUN only; inspect this plan, then pass --apply to write.")
        return

    backup_dir = Path(tempfile.mkdtemp(prefix="pnp-chp14-s2-relation-audit-"))
    shutil.copy2(statement_path, backup_dir / statement_path.name)
    atomic_write(statement_path, encode_jsonl(statements))
    written = read_jsonl(statement_path)
    if len(written) != 12225 or relation_counts(written) != (2310, 2286, 24):
        raise SystemExit("post-write verification failed; restore copy is available")
    written_ids = {r["statement_id"] for r in written}
    if not NEW_STATEMENT_IDS <= written_ids:
        raise SystemExit("one or more planned statements are missing after write")
    print(f"APPLIED; recovery copy: {backup_dir}")


if __name__ == "__main__":
    main()
