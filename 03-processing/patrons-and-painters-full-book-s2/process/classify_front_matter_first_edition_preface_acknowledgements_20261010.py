from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
MENTIONS = ROOT / "04-knowledge/tables/mentions.csv"
COVERAGE = ROOT / "04-knowledge/tables/s2-coverage.csv"
SOURCE = ROOT / "02-sources/02-Markdown/00_03_Preface_1st_Ed.md"
PDF = ROOT / "02-sources/01-book/CHP-0Cover.pdf"
EXPECTED_TABLE_SHA256 = "bbb4c5b8a300f151aad6e209c6f5e57ae7ba33e950b2b332f5c4ff92017bf23c"
EXPECTED_SOURCE_SHA256 = "e793793f71fc5e9b9ba97a1c12fa50d497ec4de89f3c19f247c4a93228618c4a"
EXPECTED_PDF_SHA256 = "502a6dcf66b5c01b09209ad92abbf6b1a172488de1058750ca9db9b906b2d266"
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-front-matter-first-ed-preface-acknowledgements-20261010")
SEGMENT = "front-matter:00_03_Preface_1st_Ed:l19-29"

ROWS = {
    "st-fm-c-preface-warburg-library-support": {
        "predicate": "research_support_at", "subject": "cand-3770", "object": "cand-3701",
        "line_start": 21, "line_end": 22,
        "anchors": [(21, "All the libraries and archives which are referred to on a later page"), (22, "Warburg Institute in London")],
        "note": "Haskell reports receiving encouragement and advice at the Warburg Institute library from people associated with the organization. Keep the named institution as the research-support context; the individual advisers are not identified.",
    },
    "st-fm-c-preface-constable-printing": {
        "predicate": "printed_and_checked_text_of", "subject": "cand-3689", "object": "cand-2962",
        "line_start": 22, "line_end": 22,
        "anchors": [(22, "T. and A. Constable Ltd., the printers of the book"), (22, "setting and checking my text")],
        "note": "The preface directly identifies T. and A. Constable Ltd. as the book's printers and says they set and checked Haskell's text.",
    },
    "st-fm-c-preface-kings-college-support": {
        "predicate": "institutional_support_from", "subject": "cand-3770", "object": "cand-3653",
        "line_start": 22, "line_end": 22,
        "anchors": [(22, "Provost and Fellows of my own College"), (22, "undertake and continue this book")],
        "note": "Haskell says King's College made it possible for him to undertake and continue the book. The recipient-to-provider direction is retained by the predicate 'support_from'; the institutional identity is supported by the signature immediately following the preface.",
    },
    "st-fm-c-preface-munby-assistance": {
        "predicate": "research_assistance_from", "subject": "cand-3770", "object": "cand-3708",
        "line_start": 22, "line_end": 22,
        "anchors": [(22, "A. N. L. Munby, the librarian"), (22, "solved countless problems for me")],
        "note": "Haskell says librarian A. N. L. Munby solved many research problems for him. Preserve the recipient-to-provider direction expressed by 'assistance_from'.",
    },
    "st-fm-c-preface-orna-index": {
        "predicate": "compiled_index_for", "subject": "cand-3756", "object": "cand-2962",
        "line_start": 22, "line_end": 22,
        "anchors": [(22, "Elizabeth Oma"), (22, "compiling a full and necessarily rather complicated Index")],
        "note": "Haskell says Elizabeth Orna compiled the book's index. The S0 transcription reads 'Oma', but the facsimile on CHP-0Cover.pdf physical page 7 (printed page ix) visibly reads 'Orna'; preserve S0 and retain the existing candidate mapping based on the facsimile.",
    },
    "st-fm-c-preface-rylands-proofreading": {
        "predicate": "proofreading_and_correction", "subject": "cand-3775", "object": "cand-2962",
        "line_start": 22, "line_end": 22,
        "anchors": [(22, "G. H. W. Rylands"), (22, "whole book in proof and made many suggestions and corrections")],
        "note": "The preface directly reports that G. H. W. Rylands read the typescript and book proofs and made suggestions and corrections.",
    },
    "st-fm-c-preface-pignatti-correr-facilities": {
        "predicate": "provided_research_facilities_at", "subject": "cand-3888", "object": "cand-3635",
        "line_start": 23, "line_end": 23,
        "anchors": [(23, "Dr Terisio Pignatti"), (23, "facilities for working in the Correr Library in Venice")],
        "note": "Haskell says Pignatti provided facilities for Haskell's work at the Correr Library. The library is the stated setting; do not infer that Pignatti was its employee or owner.",
    },
    "st-fm-c-preface-blunt-discussion": {
        "predicate": "intellectual_discussion_with", "subject": "cand-3770", "object": "cand-3722",
        "line_start": 24, "line_end": 24,
        "anchors": [(24, "Sir Anthony Blunt"), (24, "with whom I have had so many stimulating discussions")],
        "note": "Haskell directly reports repeated stimulating discussions with Anthony Blunt. The relation is conversational, not an inferred friendship or collaboration.",
    },
    "st-fm-c-preface-levey-discussion": {
        "predicate": "intellectual_discussion_with", "subject": "cand-3770", "object": "cand-3843",
        "line_start": 24, "line_end": 24,
        "anchors": [(24, "Mr Michael Levey"), (24, "with whom I have had so many stimulating discussions")],
        "note": "Haskell directly reports repeated stimulating discussions with Michael Levey. The relation is conversational, not an inferred friendship or collaboration.",
    },
    "st-fm-c-preface-marabottini-hospitality": {
        "predicate": "hospitality_to", "subject": "cand-3714", "object": "cand-3770",
        "line_start": 24, "line_end": 24,
        "anchors": [(24, "whose repeated hospitality has made the writing of this book such a pleasure")],
        "note": "Haskell directly attributes repeated hospitality to Alessandro Marabottini Marabotti and says it made writing the book a pleasure. Preserve the source's OCR spelling separately from the verified printed wording.",
    },
    "st-fm-c-preface-marabottini-viewing": {
        "predicate": "viewed_works_with", "subject": "cand-3770", "object": "cand-3714",
        "line_start": 24, "line_end": 24,
        "anchors": [(24, "in whose company I have seen so many of the works discussed")],
        "note": "Haskell says he saw many works discussed in the book in Marabottini Marabotti's company; do not infer authorship, ownership, or a specific visit date.",
    },
    "st-fm-c-preface-nicolson-textual-help": {
        "predicate": "textual_assistance_to", "subject": "cand-3732", "object": "cand-3770",
        "line_start": 25, "line_end": 25,
        "anchors": [(25, "Benedict Nicolson who has taken endless trouble with my text at every stage"), (25, "attitude has helped me more than I can express")],
        "note": "Haskell reports Nicolson's sustained textual assistance and the effect of his attitude. The S2 candidate records assistance to Haskell, not authorship of the book.",
    },
    "st-fm-c-preface-pevsner-introduction": {
        "predicate": "introduced_subject_of_interest", "subject": "cand-3770", "object": "cand-3848",
        "line_start": 24, "line_end": 24,
        "anchors": [(24, "Nikolaus Pevsner, who first interested me in the subject of art patronage")],
        "note": "Haskell says Pevsner first interested him in art patronage. Preserve the source's recipient-to-influencer endpoint order encoded by the current predicate; this is a reported intellectual influence, not a formal mentorship claim.",
    },
    "st-fm-c-preface-signature-date": {
        "predicate": "preface_signature", "subject": "cand-3770", "object": "cand-2962",
        "line_start": 26, "line_end": 29,
        "anchors": [(26, "FRANCIS HASKELL"), (27, "King’s College"), (29, "July 1962")],
        "note": "The first-edition preface is signed by Haskell at King's College, Cambridge, in July 1962. This is an explicit author-to-book-preface attribution and date/place context, not an independent claim about the entire book's publication date.",
    },
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify first-edition preface acknowledgement statements at lines 19-29.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = TABLE.read_bytes()
    if digest(raw) != EXPECTED_TABLE_SHA256:
        raise SystemExit(f"statement SHA mismatch: expected {EXPECTED_TABLE_SHA256}, got {digest(raw)}")
    if digest(SOURCE.read_bytes()) != EXPECTED_SOURCE_SHA256:
        raise SystemExit("S0 source SHA mismatch")
    if digest(PDF.read_bytes()) != EXPECTED_PDF_SHA256:
        raise SystemExit("source PDF SHA mismatch")
    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    candidate_rows = {row["candidate_id"]: row for row in read_csv(CANDIDATES)}
    mentions = read_csv(MENTIONS)
    coverage = read_csv(COVERAGE)
    coverage_row = next((row for row in coverage if row["segment_id"] == SEGMENT), None)
    if not coverage_row or (coverage_row["disposition"], coverage_row["migration_status"]) != ("reviewed", "complete"):
        raise SystemExit("segment coverage is not reviewed/complete")
    mentioned_ids = {row["candidate_id"] for row in mentions if row["segment_id"] == SEGMENT}
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    by_id = {row.get("statement_id"): row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")

    for statement_id, spec in ROWS.items():
        row = by_id.get(statement_id)
        if row is None:
            raise SystemExit(f"missing statement: {statement_id}")
        q = row.get("qualifiers") or {}
        if (
            row.get("segment_id") != SEGMENT
            or row.get("source_file") != "02-sources/02-Markdown/00_03_Preface_1st_Ed.md"
            or row.get("origin") != "book"
            or row.get("predicate") != spec["predicate"]
            or row.get("subject_candidate_id") != spec["subject"]
            or row.get("object_candidate_id") != spec["object"]
            or q.get("source_line_start") != spec["line_start"]
            or q.get("source_line_end") != spec["line_end"]
            or q.get("speaker") not in {"Haskell", "Francis Haskell"}
            or "relation_candidate" in q
        ):
            raise SystemExit(f"statement preflight mismatch: {statement_id}")
        for line_number, anchor in spec["anchors"]:
            if line_number > len(source_lines) or anchor not in source_lines[line_number - 1]:
                raise SystemExit(f"source anchor mismatch: {statement_id} line {line_number}")
        for endpoint in (spec["subject"], spec["object"]):
            if endpoint not in candidate_rows:
                raise SystemExit(f"missing candidate endpoint {endpoint}: {statement_id}")
            if endpoint != "cand-3770" and endpoint not in mentioned_ids:
                raise SystemExit(f"endpoint mention missing for {endpoint}: {statement_id}")

    updated = {}
    for statement_id, spec in ROWS.items():
        row = deepcopy(by_id[statement_id])
        row["qualifiers"]["relation_candidate"] = True
        row["qualifiers"]["relation_candidate_note"] = spec["note"]
        updated[statement_id] = row

    output = []
    seen = set()
    for line in raw.decode("utf-8").splitlines():
        if not line.strip():
            output.append(line)
            continue
        row = json.loads(line)
        statement_id = row["statement_id"]
        if statement_id in updated:
            output.append(json.dumps(updated[statement_id], ensure_ascii=False, separators=(",", ":")))
            seen.add(statement_id)
        else:
            output.append(line)
    if seen != set(ROWS):
        raise SystemExit("write coverage mismatch")
    result = ("\n".join(output) + "\n").encode("utf-8")
    print(f"preflight passed: {len(seen)}/{len(ROWS)} statements; table/S0/PDF hashes, candidate mentions, speaker, coverage and anchors verified")
    print("facsimile review: Elizabeth Orna is visibly spelled 'Orna' on physical PDF page 7 (printed page ix); S0 remains unchanged")
    print("classification: 14 direct acknowledgement, support, production, discussion, hospitality, research and signature candidates; no endpoint or row changes")
    for statement_id, spec in ROWS.items():
        print(f"review {statement_id}: relation_candidate absent -> true; endpoints {spec['subject']} -> {spec['object']}")
        print(f"  rationale: {spec['note']}")
    if not args.apply:
        print(f"dry-run only; table unchanged; input_sha256={digest(raw)}")
        return
    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")
    shutil.copy2(TABLE, BACKUP)
    fd, temp_name = tempfile.mkstemp(prefix=TABLE.name + ".", suffix=".tmp", dir=TABLE.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(result)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, TABLE)
    except Exception:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
        raise
    print(f"applied: backup={BACKUP.relative_to(ROOT)} output_sha256={digest(result)}")


if __name__ == "__main__":
    main()
