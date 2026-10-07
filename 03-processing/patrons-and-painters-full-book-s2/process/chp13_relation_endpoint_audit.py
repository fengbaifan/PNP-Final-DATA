"""Controlled Chapter 13 S2 relation-candidate audit.

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
SOURCE_NAME = "02-sources/02-Markdown/13_CHP-13_intro.md"
SOURCE_PATH = ROOT / SOURCE_NAME
EXPECTED_SOURCE_SHA256 = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"
EXPECTED_SEGMENT_HASHES = {
    "chp-13:13_CHP-13_intro:l14-19": "14b387b94bdd8ff02e1b97b42c2ab554839d8a2d55645f6a7d5d00b82a554bf6",
    "chp-13:13_CHP-13_intro:l21-30": "71051b50a7ec099c88196112b4d831e5d947992428833bc30c66e28907641d9d",
    "chp-13:13_CHP-13_intro:l32-39": "87b76d69cdd5618e7276f859c5ad8cf89a9ffb947d6e78c6032782e93414fe14",
    "chp-13:13_CHP-13_intro:l41-50": "575ec0ac309dcec132ec190a56e047e1d634a0407f4a40453f06764329833fde",
    "chp-13:13_CHP-13_intro:l52-59": "7ef0d455d825a64771a87aa0ebbd3e7b14cd82f3b0e88c56f8c7919de474e986",
    "chp-13:13_CHP-13_intro:l79-88": "661b04d02c9cbf2feda5e28e972bcb16c5375d173d775de71709151c87e2d073",
    "chp-13:13_CHP-13_intro:l179-251": "f592d5913122cf2c4c2e7db9a39b8016c82dbc232a869018793ef11096faacb9",
}
EXPECTED_MAX_CANDIDATE = 11473
EXPECTED_STATEMENT_COUNT = 12213
EXPECTED_RELATION_COUNTS = (2312, 2274, 38)
EXPECTED_OPEN_ENDPOINT_IDS = {
    "st-chp13-p333-publishers-sales-employment-and-commissions",
    "st-chp13-p334-albrizzi-plan-revive-venetian-prints-open",
    "st-chp13-p335-gerusalemme-subscriber-network",
    "st-chp13-p336-note2-reported-canvas-distribution",
    "st-chp13-p337-pasquali-revealed-book-clients-under-pressure",
    "st-chp13-p337-note1-lodoli-influenced-publishers-booksellers",
    "st-chp13-p340-viero-same-limited-original-commissioning-applies",
    "st-chp13-p340-wagner-seems-to-have-commissioned-little-original-work",
}
EXPECTED_ENDPOINTS = {
    "st-chp13-p333-publishers-sales-employment-and-commissions": ("cand-2068", None),
    "st-chp13-p334-albrizzi-plan-revive-venetian-prints-open": ("cand-0027", None),
    "st-chp13-p335-gerusalemme-subscriber-network": ("cand-9990", None),
    "st-chp13-p336-note2-reported-canvas-distribution": ("cand-9998", None),
    "st-chp13-p337-pasquali-revealed-book-clients-under-pressure": ("cand-1844", None),
    "st-chp13-p337-note1-lodoli-influenced-publishers-booksellers": ("cand-1411", None),
    "st-chp13-p340-viero-same-limited-original-commissioning-applies": ("cand-2773", None),
    "st-chp13-p340-wagner-seems-to-have-commissioned-little-original-work": ("cand-2796", None),
}
SUBSCRIBERS = [
    (
        "schulenburg",
        "cand-2401",
        "Marshal Schulenburg",
        "Haskell names Marshal Schulenburg among the subscribers to the 1745 Gerusalemme Liberata edition.",
        "The statement is keyed to the existing index candidate; final global identity alignment remains in S3.",
    ),
    (
        "smith",
        "cand-2440",
        "Consul Smith",
        "Haskell names Consul Smith among the subscribers to the 1745 Gerusalemme Liberata edition.",
        "The source gives only “Consul Smith”; its match to the existing Joseph Smith candidate remains for S3 identity alignment.",
    ),
    (
        "carriera",
        "cand-0581",
        "Rosalba Carriera",
        "Haskell names Rosalba Carriera among the subscribers to the 1745 Gerusalemme Liberata edition.",
        "The page image confirms the printed surname Carriera; S0 OCR “Camera” is corrected in this statement.",
    ),
    (
        "pellegrini",
        "cand-1862",
        "Pellegrini",
        "Haskell names Pellegrini among the subscribers to the 1745 Gerusalemme Liberata edition.",
        "The source gives only the surname Pellegrini; its match to the existing Giovanni Antonio Pellegrini candidate remains for S3 identity alignment.",
    ),
]
NEW_STATEMENT_IDS = {
    f"st-chp13-p335-{slug}-listed-as-subscriber-to-gerusalemme" for slug, *_ in SUBSCRIBERS
}


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

    source_bytes = SOURCE_PATH.read_bytes()
    actual_source_hash = hashlib.sha256(source_bytes).hexdigest()
    if actual_source_hash != EXPECTED_SOURCE_SHA256:
        raise SystemExit(f"Chapter 13 source changed: {actual_source_hash}")
    source_lines = SOURCE_PATH.read_text(encoding="utf-8-sig").splitlines()
    segment_by_id = {r["segment_id"]: r for r in read_jsonl(segment_path)}
    for segment_id, expected_hash in EXPECTED_SEGMENT_HASHES.items():
        meta = segment_by_id.get(segment_id)
        if not meta or meta.get("source_file") != SOURCE_NAME:
            raise SystemExit(f"required source segment missing or remapped: {segment_id}")
        if meta.get("sha256") != expected_hash or meta.get("asset_sha256") != EXPECTED_SOURCE_SHA256:
            raise SystemExit(f"source segment manifest changed: {segment_id}")
        excerpt = "\n".join(source_lines[int(meta["line_start"]) - 1 : int(meta["line_end"])])
        if hashlib.sha256(excerpt.encode("utf-8")).hexdigest() != expected_hash:
            raise SystemExit(f"source segment hash mismatch: {segment_id}")

    with candidate_path.open(encoding="utf-8-sig", newline="") as f:
        import io

        candidate_reader = csv.DictReader(f)
        candidate_fields = candidate_reader.fieldnames
        candidates = list(candidate_reader)
    statements = read_jsonl(statement_path)
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    statement_by_id = {r["statement_id"]: r for r in statements}
    if len(candidate_by_id) != len(candidates) or len(statement_by_id) != len(statements):
        raise SystemExit("duplicate identifiers in candidate or statement table")
    if max(int(r["candidate_id"].split("-")[-1]) for r in candidates) != EXPECTED_MAX_CANDIDATE:
        raise SystemExit("candidate sequence changed")
    if len(statements) != EXPECTED_STATEMENT_COUNT:
        raise SystemExit(f"statement count changed: expected {EXPECTED_STATEMENT_COUNT}, found {len(statements)}")
    if relation_counts(statements) != EXPECTED_RELATION_COUNTS:
        raise SystemExit(f"relation counts changed: {relation_counts(statements)}")

    open_ids = {
        r["statement_id"]
        for r in statements
        if r["statement_id"].startswith("st-chp13-")
        and r.get("qualifiers", {}).get("relation_candidate") is True
        and (not r.get("subject_candidate_id") or not r.get("object_candidate_id"))
    }
    if open_ids != EXPECTED_OPEN_ENDPOINT_IDS:
        raise SystemExit(f"Chapter 13 open endpoint set changed: {sorted(open_ids)}")
    for sid, endpoints in EXPECTED_ENDPOINTS.items():
        row = statement_by_id[sid]
        if (row.get("subject_candidate_id"), row.get("object_candidate_id")) != endpoints:
            raise SystemExit(f"statement endpoint precondition changed: {sid}")
    if not NEW_STATEMENT_IDS.isdisjoint(statement_by_id):
        raise SystemExit("one or more planned statement IDs already exist")
    for cid in {person_id for _, person_id, *_ in SUBSCRIBERS} | {"cand-9990"}:
        if cid not in candidate_by_id:
            raise SystemExit(f"subscriber endpoint candidate missing: {cid}")
    for _, person_id, *_ in SUBSCRIBERS:
        if candidate_by_id[person_id].get("suggested_type") != "person":
            raise SystemExit(f"subscriber candidate is not a person candidate: {person_id}")
    if candidate_by_id["cand-9990"].get("suggested_type") != "archive":
        raise SystemExit("the 1745 Gerusalemme edition must remain an archive candidate")

    required_linked_notes = {
        "st-chp13-p334-albrizzi-plan-revive-venetian-prints-open": "st-chp13-p335-note1-augustine-advertisement",
        "st-chp13-p337-pasquali-admired-lodoli": "st-chp13-p337-note1-lodoli-influenced-publishers-booksellers",
        "st-chp13-p340-wagner-seems-to-have-commissioned-little-original-work": "st-chp13-p340-note4-moschini-wagner-locator",
    }
    for body_id, note_id in required_linked_notes.items():
        if note_id not in statement_by_id:
            raise SystemExit(f"linked note statement missing: {note_id}")
        body_q = statement_by_id[body_id].get("qualifiers", {})
        if body_q.get("footnote_body_link_status") != "linked" or note_id not in body_q.get("footnote_note_statement_ids", []):
            raise SystemExit(f"expected body-note link changed: {body_id} -> {note_id}")
    if statement_by_id["st-chp13-p334-albrizzi-plan-revive-venetian-prints-open"]["qualifiers"].get("continuation_footnote_text_pending") is not True:
        raise SystemExit("expected stale p.334 footnote-pending flag changed")
    if "pending consolidated-note processing" not in statement_by_id["st-chp13-p334-albrizzi-plan-revive-venetian-prints-open"]["qualifiers"].get("qualification", ""):
        raise SystemExit("expected stale p.334 qualification changed")
    if "await linkage" not in statement_by_id["st-chp13-p337-pasquali-admired-lodoli"]["qualifiers"].get("qualification", ""):
        raise SystemExit("expected stale p.337 note-link wording changed")
    if "pending in the notes segment" not in statement_by_id["st-chp13-p340-wagner-seems-to-have-commissioned-little-original-work"]["qualifiers"].get("qualification", ""):
        raise SystemExit("expected stale p.340 note-link wording changed")

    original_by_id = copy.deepcopy(statement_by_id)

    def mark_nonrelation(statement_id: str, qualification: str | None = None):
        row = statement_by_id[statement_id]
        row.setdefault("qualifiers", {})["relation_candidate"] = False
        if qualification is not None:
            row["qualifiers"]["qualification"] = qualification

    nonrelations = {
        "st-chp13-p333-publishers-sales-employment-and-commissions": "This describes general publisher practices; no individual employer, artist, or commission is identified.",
        "st-chp13-p334-albrizzi-plan-revive-venetian-prints-open": "The printed note identifies a 19 March 1730 Novelle advertisement for a proposed edition of Saint Augustine’s works. It does not identify a proposed editor or establish that the edition was published; “reputation of Venetian prints” is an abstract aim, not a named relation endpoint.",
        "st-chp13-p335-gerusalemme-subscriber-network": "This preserves Haskell’s aggregate description of the subscriber list; the four named people and the 1745 edition are represented in separate candidate relation statements.",
        "st-chp13-p336-note2-reported-canvas-distribution": "The note reports a distribution among unnamed museums and private collections in four cities. It does not identify individual canvases, institutions, owners, or a work-to-city mapping; retain it as a source-reported assertion.",
        "st-chp13-p337-pasquali-revealed-book-clients-under-pressure": "The clients are unnamed. The book is the item Pasquali had sold, not the object of the disclosure; note 3 remains a linked archival locator.",
        "st-chp13-p337-note1-lodoli-influenced-publishers-booksellers": "Publishers and booksellers are unspecified groups. The Conti letter is cited as evidence, not as the target of Lodoli’s influence; preserve Haskell’s reported characterization and his separate qualified inference about Pasquali.",
        "st-chp13-p340-viero-same-limited-original-commissioning-applies": "This extends Haskell’s hedged assessment to Viero; it names no artist or work and does not assert a relation between Viero and Wagner.",
        "st-chp13-p340-wagner-seems-to-have-commissioned-little-original-work": "Haskell’s “seems” and “little” are retained. The statement concerns unspecified other artists and works; printed note 4 is linked, but its cited page has not been independently consulted.",
    }
    for sid, qualification in nonrelations.items():
        mark_nonrelation(sid, qualification)

    p334 = statement_by_id["st-chp13-p334-albrizzi-plan-revive-venetian-prints-open"]["qualifiers"]
    p334["continuation_footnote_text_pending"] = False
    p337_body = statement_by_id["st-chp13-p337-pasquali-admired-lodoli"]["qualifiers"]
    p337_body["qualification"] = "This is Haskell’s characterization of Pasquali’s admiration; printed note 1 and its consolidated L203 statements are linked. The cited Conti letter and publication have not been independently consulted."
    p340_wagner = statement_by_id["st-chp13-p340-wagner-seems-to-have-commissioned-little-original-work"]["qualifiers"]
    p340_wagner["qualification"] = "Haskell’s hedge “seems” is retained. Printed note 4 cites Moschini (1924), p. 132; the cited page and work title have not been independently consulted."

    parent_id = "st-chp13-p335-gerusalemme-subscriber-network"
    parent = statement_by_id[parent_id]
    parent_quote = parent["original_quote"]
    carriera_fix = [
        correction for correction in parent["qualifiers"].get("ocr_corrections", [])
        if correction.get("ocr") == "Rosalba Camera"
    ]
    if len(carriera_fix) != 1:
        raise SystemExit("the scanned Rosalba Carriera correction is missing or changed")
    added = []
    for slug, person_id, source_name, claim, qualification in SUBSCRIBERS:
        statement_id = f"st-chp13-p335-{slug}-listed-as-subscriber-to-gerusalemme"
        row = copy.deepcopy(parent)
        row["statement_id"] = statement_id
        row["subject_candidate_id"] = person_id
        row["object_candidate_id"] = "cand-9990"
        row["predicate"] = "listed_as_subscriber_to_edition"
        q = row["qualifiers"]
        q["source_line_start"] = 36
        q["source_line_end"] = 37
        q["claim"] = claim
        q["speaker"] = "Haskell"
        q["text_layer"] = "authorial narrative"
        q["qualification"] = qualification
        q["mentioned_candidate_ids"] = [person_id, "cand-9990"]
        q["ocr_corrections"] = copy.deepcopy(carriera_fix)
        q["relation_candidate"] = True
        row["original_quote"] = parent_quote
        added.append(row)

    statements.extend(added)
    statement_by_id.update({r["statement_id"]: r for r in added})

    final_ch13_open = {
        r["statement_id"] for r in statements
        if r["statement_id"].startswith("st-chp13-")
        and r.get("qualifiers", {}).get("relation_candidate") is True
        and (not r.get("subject_candidate_id") or not r.get("object_candidate_id"))
    }
    if final_ch13_open:
        raise SystemExit(f"planned Chapter 13 open endpoints remain: {sorted(final_ch13_open)}")
    candidate_ids = set(candidate_by_id)
    for row in statements:
        for cid in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if cid and cid not in candidate_ids:
                raise SystemExit(f"missing statement endpoint candidate: {row['statement_id']} -> {cid}")
        for cid in row.get("qualifiers", {}).get("mentioned_candidate_ids", []):
            if cid not in candidate_ids:
                raise SystemExit(f"missing mentioned candidate: {row['statement_id']} -> {cid}")

    expected_after = (12217, (2308, 2278, 30))
    actual_after = (len(statements), relation_counts(statements))
    if actual_after != expected_after:
        raise SystemExit(f"planned aggregate counts differ: expected {expected_after}, found {actual_after}")

    print("Chapter 13 S2 relation and linked-note audit plan")
    print("open endpoint candidates: 8 -> 0")
    print("subscriber list: split into 4 person-to-edition candidate statements")
    print("generalized claims retained as source assertions; no candidates or mentions added")
    print("three stale note-status descriptions corrected; no S6 formal relations added")
    print(f"statements: {EXPECTED_STATEMENT_COUNT} -> {len(statements)}")
    print(f"relation candidates (total/complete/open): {EXPECTED_RELATION_COUNTS} -> {relation_counts(statements)}")
    changed_ids = sorted(
        sid for sid, row in statement_by_id.items()
        if sid in original_by_id and row != original_by_id[sid]
    )
    for sid in changed_ids + sorted(NEW_STATEMENT_IDS):
        row = statement_by_id[sid]
        q = row.get("qualifiers", {})
        endpoints = f"{row.get('subject_candidate_id') or '∅'} → {row.get('object_candidate_id') or '∅'}"
        print(f"{sid}: {endpoints}; relation={q.get('relation_candidate')}; {q.get('claim')}")
        if args.show_diff:
            if sid in original_by_id:
                print("  BEFORE", json.dumps(original_by_id[sid], ensure_ascii=False))
            print("  AFTER ", json.dumps(row, ensure_ascii=False))

    if not args.apply:
        print("DRY-RUN only; inspect this plan, then pass --apply to write.")
        return

    backup_dir = Path(tempfile.mkdtemp(prefix="pnp-chp13-s2-relation-audit-"))
    shutil.copy2(statement_path, backup_dir / statement_path.name)
    atomic_write(statement_path, encode_jsonl(statements))
    written = read_jsonl(statement_path)
    if len(written) != 12217 or relation_counts(written) != (2308, 2278, 30):
        raise SystemExit("post-write verification failed; restore copy is available")
    if any(sid not in {r["statement_id"] for r in written} for sid in NEW_STATEMENT_IDS):
        raise SystemExit("one or more subscriber statements are missing after write")
    print(f"APPLIED; recovery copy: {backup_dir}")


if __name__ == "__main__":
    main()
