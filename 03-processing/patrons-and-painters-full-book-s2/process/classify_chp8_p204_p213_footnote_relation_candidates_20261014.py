"""Classify existing p.204-p.213 footnote statements in the composite S2 segment."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_i.md"
SOURCE = ROOT / SOURCE_REL
PDF = ROOT / "02-sources" / "01-book" / "CHP-8.pdf"
PAGE_IMAGE = ROOT / "scripts" / ".tmp_chp8_p212_review.png"
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l126-157"
SEGMENT_SHA = "0ecf16986f97d6044129c91ccafde31ac1ebe6dadef71c79a6d4691c10d90b4c"
BACKUP = STATEMENTS.with_name(
    STATEMENTS.name + ".bak-s2-chp8-p204-p213-footnote-review-20261014"
)

EXPECTED_HASHES = {
    STATEMENTS: "c640a02e7dc085bad9d734a19d95704696661c644d3d6cfb5937916c873543a8",
    SOURCE: "8449a867c1b0459a35c8ebbf7d37c0f770cd71ef0be987b12b7a1281d41e12bf",
    PDF: "cb11451ac726f37ed5badf21a569af88f790f858f1c39eb63f2efb58a0fe4ac3",
    PAGE_IMAGE: "522bd1da6d59fb26e103f3f50185175c1c27661643f5da9e96fcd2ae4b7eeb43",
}

FALSE_IDS = {
    "st-chp8-p204-n1-citations",
    "st-chp8-p204-n2-citation",
    "st-chp8-p204-n3-codazzi-paintings-citation",
    "st-chp8-p204-n3-giordano-iconography-citation",
    "st-chp8-p204-n3-patronage-citations",
    "st-chp8-p205-n1-roomer-source-citations",
    "st-chp8-p205-n2-palomino-capaccio-trapier-citations",
    "st-chp8-p205-n3-capaccio-trapier-ville-citations",
    "st-chp8-p205-n4-trapier-citation",
    "st-chp8-p206-n1-cite-saxl",
    "st-chp8-p206-n2-cite-burchard",
    "st-chp8-p207-n1-cite-de-dominici",
    "st-chp8-p207-n1-cite-ferdinando-colonna",
    "st-chp8-p207-n2-cite-de-dominici",
    "st-chp8-p208-n1-cite-de-dominici",
    "st-chp8-p208-n2-cite-ruffo",
    "st-chp8-p208-n3-cite-bartsch",
    "st-chp8-p208-n4-cite-bologna",
    "st-chp8-p208-n5-cite-vaes",
    "st-chp8-p208-n6-cite-de-dominici",
    "st-chp8-p208-n7-cite-de-dominici-ibid",
    "st-chp8-p209-n1-cite-ruffo",
    "st-chp8-p209-n1-cite-slive",
    "st-chp8-p212-n1-cite-richa",
    "st-chp8-p212-n2-cite-cinelli-baldinucci",
    "st-chp8-p212-n3-cite-gualandi-mostra",
    "st-chp8-p212-n5-cite-baldinucci",
    "st-chp8-p212-n4-polgigrafo-archive-locator",
}

TRUE_NOTES = {
    "st-chp8-p205-drunk-silenus-capaccio-1634-list":
        "The note links the identified Ribera painting to a dated location and a specific 1634 picture-list report; preserve Haskell's negative-list qualification.",
    "st-chp8-p205-n1-articles-reference-firsthand-sources":
        "This is a substantive claim about the two articles quoting and citing named first-hand sources, not a bare citation locator.",
    "st-chp8-p205-san-martino-flaying-not-roomer-1634-picture":
        "The statement distinguishes the dated Museo di San Martino painting from the subject recorded in Roomer's 1634 picture list.",
    "st-chp8-p207-n1-limits-on-other-colonna-provenance":
        "This records Haskell's explicit evidentiary position about the provenance of other pictures; it does not negate his separate report about the two Codazzi works.",
    "st-chp8-p212-n2-longhi-publishes-vannini-scenes":
        "The note links two identified Vannini scenes with Longhi's 1956 article; the article is identified from the book bibliography but was not independently read.",
    "st-chp8-p212-n3-bilivert-picture-group":
        "The note reports a source-defined group of four religious Bilivert pictures in the Del Rosso collection; individual works are unnamed.",
    "st-chp8-p212-n3-cortona-madonna-four-saints":
        "The note connects the smaller Cortona painting, its earlier version, Luca Giordano's acquisition role, and the Del Rosso family; retain the reported rather than independently verified status.",
    "st-chp8-p212-n3-dolci-and-bilivert-pictures":
        "This records the Del Rosso family's reported three Dolci pictures and their religious subject matter; the separate Bilivert group remains in its own statement.",
    "st-chp8-p212-n3-ferri-altarpieces":
        "The note reports the family's ownership of otherwise unidentified Ciro Ferri altarpieces; no titles or locations are supplied.",
    "st-chp8-p212-n5-archivio-letter-content":
        "This captures the reported contents of a dated archival letter and its account of correspondence involving Panciatichi and Giordano; sender and Viceroy remain unidentified, so this is only a candidate and not a formal edge.",
    "st-chp8-p212-n5-panciatichi-nicola-kinship":
        "The note explicitly identifies Nicola del Rosso as Panciatichi's son-in-law and fourth brother in Haskell's account; preserve this as a source-level kinship claim pending identity review.",
    "st-chp8-p212-n5-panciatichi-office":
        "The note reports Panciatichi holding the named office from 1682; the office endpoint is not yet registered and must remain unresolved for later backlog review.",
    "st-chp8-p213-n1-longhi-publication":
        "The note links the Paceco de Rosa pictures to Longhi's 1956 article; this remains a source-level publication claim and does not establish individual work identities.",
    "st-chp8-p213-n1-more-del-rosso-pictures":
        "The note adds reported Ribera, Preti, and Paceco de Rosa picture holdings to the Del Rosso collection; titles and individual work identities are not supplied.",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def jsonl_bytes(rows: list[dict]) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False, suffix=".tmp") as handle:
        handle.write(data)
        temporary = Path(handle.name)
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after guarded dry-run checks pass")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    actual = {path: sha(data) for path, data in raw.items()}
    if actual != EXPECTED_HASHES:
        raise SystemExit("a reviewed table, source, PDF, or page image changed; re-review before applying")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[125:157])
    if sha(segment_text.encode("utf-8")) != SEGMENT_SHA:
        raise SystemExit("the p.204-p.213 footnote segment changed since review")
    segment_rows = {row["segment_id"]: row for row in read_jsonl(TABLES / "segments.jsonl")}
    segment = segment_rows.get(SEGMENT_ID)
    if not segment or (
        segment.get("source_file"), segment.get("line_start"), segment.get("line_end"),
        segment.get("sha256"), segment.get("asset_sha256"),
    ) != (SOURCE_REL, 126, 157, SEGMENT_SHA, EXPECTED_HASHES[SOURCE]):
        raise SystemExit("the S0 segment manifest does not match the reviewed source")

    statements = read_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("statement identifiers are not unique")
    page_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    unset = {
        row["statement_id"] for row in page_rows
        if "relation_candidate" not in (row.get("qualifiers") or {})
    }
    if len(page_rows) != 56 or unset != FALSE_IDS | set(TRUE_NOTES):
        raise SystemExit(f"unexpected footnote inventory: rows={len(page_rows)}, unset={len(unset)}")
    if FALSE_IDS & set(TRUE_NOTES) or len(FALSE_IDS) != 28 or len(TRUE_NOTES) != 14:
        raise SystemExit("classification plan is internally inconsistent")
    for statement_id in FALSE_IDS:
        row = by_id[statement_id]
        if row.get("predicate") not in {"footnote_citation", "archival_locator"}:
            raise SystemExit(f"citation-only classification target changed: {statement_id}")

    for statement_id in FALSE_IDS:
        q = dict(by_id[statement_id].get("qualifiers") or {})
        q["relation_candidate"] = False
        q["relation_candidate_note"] = (
            "This is a bibliographic or archival locator attached to a narrative claim; retain its source and page data, "
            "but it does not itself assert an independent historical relation."
            if statement_id != "st-chp8-p212-n4-polgigrafo-archive-locator"
            else "This identifies a manuscript collection as a locator for supporting material; it records source location, not an independent historical relation."
        )
        by_id[statement_id]["qualifiers"] = q

    for statement_id, note in TRUE_NOTES.items():
        q = dict(by_id[statement_id].get("qualifiers") or {})
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note
        by_id[statement_id]["qualifiers"] = q

    letter = by_id["st-chp8-p212-n5-archivio-letter-content"]
    q = dict(letter.get("qualifiers") or {})
    corrections = list(q.get("ocr_corrections") or [])
    correction = {
        "source_file": SOURCE_REL,
        "source_line": 153,
        "ocr": "à S.E.",
        "print": "à S.E.’",
        "basis": "CHP-8.pdf physical page 10; the quoted letter continues to its closing quotation mark after S.E.",
    }
    if correction not in corrections:
        corrections.append(correction)
    q["ocr_corrections"] = corrections
    letter["qualifiers"] = q

    updated = jsonl_bytes(statements)
    counts = Counter(
        row.get("qualifiers", {}).get("relation_candidate")
        for row in page_rows
    )
    print("DRY RUN p.204-p.213 footnote relation review")
    print(f"segment={SEGMENT_ID} statements={len(page_rows)} classified={len(unset)} false={len(FALSE_IDS)} true={len(TRUE_NOTES)}")
    print(f"final segment counts: true={counts[True]} false={counts[False]} unset={counts[None]}")
    print(f"file={STATEMENTS.relative_to(ROOT)} before_sha256={actual[STATEMENTS]} after_sha256={sha(updated)}")
    print(f"page image={PAGE_IMAGE.relative_to(ROOT)}; p.212 note 5 closing quote correction recorded in S2 qualifiers")
    if not args.apply:
        print("No files written. Use --apply to write after reviewing this summary.")
        return
    if BACKUP.exists():
        raise SystemExit(f"recovery backup already exists: {BACKUP.name}")
    shutil.copy2(STATEMENTS, BACKUP)
    atomic_write(STATEMENTS, updated)
    print(f"APPLIED; recovery copy: {BACKUP.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
