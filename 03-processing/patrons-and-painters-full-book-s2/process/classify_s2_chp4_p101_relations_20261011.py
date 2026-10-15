#!/usr/bin/env python3
"""Classify p.101 body and footnote claims with guarded statement-table writes."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SEGMENT_BODY = "chp-4:04_CHP-4_sec_ii:l24-31"
SEGMENT_NOTES = "chp-4:04_CHP-4_sec_ii:l232-308"
SEGMENT_NEXT = "chp-4:04_CHP-4_sec_ii:l33-44"
SOURCE_REL = Path("02-sources/02-Markdown/04_CHP-4_sec_ii.md")
PDF_REL = Path("02-sources/01-book/CHP-4.pdf")
STATEMENTS_REL = Path("04-knowledge/tables/book-statements.jsonl")
CANDIDATES_REL = Path("04-knowledge/tables/entity-candidates.csv")
BACKUP_TAG = "s2-chp4-p101-relations-20261011"

EXPECTED_SHA256 = {
    SOURCE_REL: "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575",
    PDF_REL: "2a737df590be91a661dbb2dd5c75b7d9df3d882487183f58430e51fb43b26303",
    STATEMENTS_REL: "118499f35a322f7140ca46d5ae92c3f7e8a29c57310b7330a63c7aab78364620",
    CANDIDATES_REL: "008176568d37d51db72fcc7393bb72711d8c0c7e9dcd1b4cccd1c018ac29a85d",
}
SEGMENT_SHA256 = {
    SEGMENT_BODY: "bb7074a81019378f57e08bb514671a9f4869443a7d5a5d9e20f4c953442b36aa",
    SEGMENT_NOTES: "792d95e61aab35b3bfb639af2364220365d26076eeafb93e545526ccf302ca7e",
    SEGMENT_NEXT: "b58e75c02a220218d26467325369277c99d76b05ff11d3ce57af8b100d0038bf",
}

TARGET_IDS = {
    "st-chp4-sec-ii-l24-31-antiques-and-guarded-feelings",
    "st-chp4-sec-ii-l24-31-archaeology-and-means",
    "st-chp4-sec-ii-l24-31-only-modern-treatment",
    "st-chp4-sec-ii-l24-31-veneration-fragment",
    "st-chp4-sec-ii-p101-footnote1-citations",
    "st-chp4-sec-ii-p101-footnote2-lumbroso",
    "st-chp4-sec-ii-p101-museum-chartaceum",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> tuple[list[dict], str]:
    raw = path.read_bytes()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    return rows, newline


def jsonl_bytes(rows: list[dict], newline: str) -> bytes:
    return (newline.join(json.dumps(row, ensure_ascii=False) for row in rows) + newline).encode("utf-8")


def unique_add(values: list[str], value: str) -> list[str]:
    result = list(values)
    if value not in result:
        result.append(value)
    return result


def set_classification(row: dict, is_relation: bool, note: str) -> None:
    q = row.setdefault("qualifiers", {})
    q["relation_candidate"] = is_relation
    q["relation_candidate_note"] = note


def cite_row(
    statement_id: str,
    object_id: str,
    quote: str,
    locator: str,
    line_start: int,
    line_end: int,
    marker: int | None,
    text_layer: str,
) -> dict:
    q = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "claim": f"Haskell's book cites {locator}.",
        "speaker": "Haskell footnote" if marker is not None else "Haskell",
        "text_layer": text_layer,
        "pdf_physical_page": 8,
        "printed_page_locator": "p.101",
        "citation_locator": locator,
        "cited_material_not_independently_consulted": True,
        "qualification": "This records a bibliographic link only; the cited material was not independently consulted and the citation does not verify adjacent claims.",
        "mentioned_candidate_ids": ["cand-2962", object_id],
        "relation_candidate": True,
        "relation_candidate_note": "The book explicitly cites this source; preserve the locator and do not infer independent consultation.",
    }
    if marker is not None:
        q["footnote_marker"] = marker
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_BODY if line_start < 232 else SEGMENT_NOTES,
        "subject_candidate_id": "cand-2962",
        "object_candidate_id": object_id,
        "predicate": "cites",
        "qualifiers": q,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_REL.as_posix(),
    }


def scalar_row(
    statement_id: str,
    segment_id: str,
    subject_id: str | None,
    predicate: str,
    quote: str,
    claim: str,
    speaker: str,
    text_layer: str,
    line_start: int,
    line_end: int,
    mentions: list[str],
    qualification: str,
    page: int = 101,
) -> dict:
    return {
        "statement_id": statement_id,
        "segment_id": segment_id,
        "subject_candidate_id": subject_id,
        "object_candidate_id": None,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": line_start,
            "source_line_end": line_end,
            "claim": claim,
            "speaker": speaker,
            "text_layer": text_layer,
            "pdf_physical_page": 8 if page == 101 else 9,
            "printed_page_locator": f"p.{page}",
            "mentioned_candidate_ids": mentions,
            "qualification": qualification,
            "relation_candidate": False,
            "relation_candidate_note": "This is a source-bounded scalar, bibliographic, or authorial claim rather than a relation between two entities.",
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_REL.as_posix(),
    }


def relation_row(
    statement_id: str,
    subject_id: str,
    object_id: str,
    predicate: str,
    quote: str,
    claim: str,
    line_start: int,
    line_end: int,
    note: str,
    speaker: str = "Haskell citing Carlo Dati, 1664",
) -> dict:
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_NOTES,
        "subject_candidate_id": subject_id,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": line_start,
            "source_line_end": line_end,
            "claim": claim,
            "speaker": speaker,
            "text_layer": "bibliographic report",
            "pdf_physical_page": 8,
            "printed_page_locator": "p.101",
            "mentioned_candidate_ids": [subject_id, object_id],
            "qualification": note,
            "relation_candidate": True,
            "relation_candidate_note": "This records Haskell's source-bounded report of a publication's contents; it does not independently verify the cited publication.",
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_REL.as_posix(),
    }


def atomic_write(path: Path, data: bytes) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".tmp-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the prevalidated S2 edits; default is dry-run")
    args = parser.parse_args()
    if not (ROOT / ".agents" / "pipeline.md").exists():
        raise SystemExit(f"Run from the repository checkout; resolved root={ROOT}")

    paths = {rel: ROOT / rel for rel in EXPECTED_SHA256}
    for rel, expected in EXPECTED_SHA256.items():
        actual = sha256(paths[rel].read_bytes())
        if actual != expected:
            raise SystemExit(f"Precondition hash mismatch for {rel}: expected {expected}, found {actual}")
    segment_rows = [json.loads(line) for line in (ROOT / "04-knowledge/tables/segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment_map = {row["segment_id"]: row for row in segment_rows}
    for segment_id, expected in SEGMENT_SHA256.items():
        actual = segment_map.get(segment_id, {}).get("sha256")
        if actual != expected:
            raise SystemExit(f"S0 segment hash changed for {segment_id}: expected {expected}, found {actual}")

    source_text = paths[SOURCE_REL].read_text(encoding="utf-8-sig")
    statements, newline = read_jsonl(paths[STATEMENTS_REL])
    rows = {row["statement_id"]: row for row in statements}
    target_set = {
        row["statement_id"]
        for row in statements
        if row.get("qualifiers", {}).get("printed_page_locator") == "p.101"
        and row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if target_set != TARGET_IDS:
        raise SystemExit(f"The p.101 target set changed: expected {sorted(TARGET_IDS)}, found {sorted(target_set)}")

    with paths[CANDIDATES_REL].open(encoding="utf-8-sig", newline="") as stream:
        candidate_ids = {row["candidate_id"] for row in csv.DictReader(stream)}
    required_ids = {"cand-2962", "cand-2036", "cand-5683", "cand-4830", "cand-5662", "cand-5684", "cand-5685", "cand-5687", "cand-5686", "cand-5689", "cand-5690", "cand-5666", "cand-5688", "cand-2035"}
    if not required_ids.issubset(candidate_ids):
        raise SystemExit(f"Required candidate endpoint missing: {sorted(required_ids - candidate_ids)}")

    required_quotes = [
        "For him antiques were certainly objects of great beauty",
        "though he is nearly always guarded in the expression of his feelings.",
        "In fact, nothing shows Cassiano’s deep seriousness more clearly than his attitude to archaeology.",
        "He was a man of only moderate means and could not therefore collect ancient marbles on the scale of a Cardinal Ludovisi or a Vincenzo Giustiniani",
        "Vermeule, 1956, pp. 32-46.",
        "Lumbroso, pp. 176, 179, 197, 251, 299",
        "Bottari, I, p. 369",
        "Peiresc, IV, p. 525",
        "Naudé (p. 99, note 5)",
        "Evelyn, II, p. 277",
        "Skippon, p. 679",
        "2 Lumbroso, p. 211.",
        "For Cassiano’s Museum Chartacewn see Carlo Dati, 1664",
        "who gives a list of its contents",
        "mentions\n23 volumes.",
        "Cassiano’s brother Carlo Antonio says that there were more than this",
        "Lumbroso, p. 167",
    ]
    for quote in required_quotes:
        if quote not in source_text:
            raise SystemExit(f"Expected exact p.101 source substring not found: {quote!r}")

    veneration = rows["st-chp4-sec-ii-l24-31-veneration-fragment"]
    next_rows, _ = read_jsonl(STATEMENTS_REL)
    closure = next(row for row in next_rows if row["statement_id"] == "st-chp4-sec-ii-l33-44-veneration-closure")
    continuation = closure.get("qualifiers", {}).get("continuation_from", {})
    if continuation.get("statement_id") != veneration["statement_id"] or continuation.get("status") != "closes_statement":
        raise SystemExit("The p.101/p.102 veneration continuation changed; review the page boundary before classifying")

    # Keep the continuation fragment open until the p.102 sentence is classified with it.
    new_rows: list[dict] = []

    antiques = rows["st-chp4-sec-ii-l24-31-antiques-and-guarded-feelings"]
    antiques["predicate"] = "regarded_antiquities_as_beautiful"
    antiques["original_quote"] = "For him antiques were certainly objects of great beauty"
    antiques["qualifiers"]["claim"] = "Haskell says Cassiano regarded antiques as objects of great beauty."
    antiques["qualifiers"]["mentioned_candidate_ids"] = ["cand-2036"]
    set_classification(antiques, False, "This is Haskell's scalar characterization of Cassiano's aesthetic response, not a relation with a separately identified object.")
    new_rows.append(scalar_row(
        "st-chp4-sec-ii-l24-31-guarded-feelings",
        SEGMENT_BODY,
        "cand-2036",
        "guarded_in_expression_of_feelings",
        "though he is nearly always guarded in the expression of his feelings.",
        "Haskell says Cassiano was nearly always guarded in expressing his feelings.",
        "Haskell",
        "authorial characterization",
        29,
        29,
        ["cand-2036"],
        "Retain Haskell's qualification 'nearly always'.",
    ))

    archaeology = rows["st-chp4-sec-ii-l24-31-archaeology-and-means"]
    archaeology["predicate"] = "serious_about_archaeology"
    archaeology["original_quote"] = "In fact, nothing shows Cassiano’s deep seriousness more clearly than his attitude to archaeology."
    archaeology["qualifiers"]["claim"] = "Haskell characterizes Cassiano as deeply serious about archaeology."
    archaeology["qualifiers"]["mentioned_candidate_ids"] = ["cand-2036"]
    set_classification(archaeology, False, "This is Haskell's scalar characterization of Cassiano's intellectual seriousness; no separate archaeology object is identified in this sentence.")
    new_rows.append(scalar_row(
        "st-chp4-sec-ii-l24-31-moderate-means-limited-marble-collection",
        SEGMENT_BODY,
        "cand-2036",
        "moderate_means_limited_marble_collection",
        "He was a man of only moderate means and could not therefore collect ancient marbles on the scale of a Cardinal Ludovisi or a Vincenzo Giustiniani",
        "Haskell says Cassiano's moderate means prevented him from collecting ancient marbles on the scale of Cardinal Ludovisi or Vincenzo Giustiniani.",
        "Haskell",
        "authorial comparison",
        29,
        29,
        ["cand-2036", "cand-1456", "cand-3077"],
        "This is a comparison of means and collection scale, not a claim that Cassiano interacted with or acquired works from either comparator. Ludovisi's identity remains for S3 alignment.",
    ))

    only_modern = rows["st-chp4-sec-ii-l24-31-only-modern-treatment"]
    set_classification(only_modern, False, "The phrase 'only modern treatment' is Haskell's bibliographic scope assessment; the citation link is recorded separately.")
    new_rows.append(cite_row(
        "st-chp4-sec-ii-l24-31-vermeule-citation",
        "cand-5690",
        "Vermeule, 1956, pp. 32-46.",
        "C. Vermeule, Art Bulletin (1956), pp. 32–46",
        30,
        30,
        None,
        "bibliographic reference",
    ))

    note1 = rows["st-chp4-sec-ii-p101-footnote1-citations"]
    citations_note1 = [
        ("cand-4830", "Bottari, I, p. 369", "Bottari, volume I, p. 369"),
        ("cand-5662", "Peiresc, IV, p. 525", "Peiresc, volume IV, p. 525"),
        ("cand-5684", "Naudé (p. 99, note 5)", "Naudé account cited at p. 99, note 5"),
        ("cand-5685", "Evelyn, II, p. 277", "Evelyn, volume II, p. 277"),
        ("cand-5687", "Skippon, p. 679", "Skippon, p. 679"),
    ]
    note1["subject_candidate_id"] = "cand-2962"
    note1["object_candidate_id"] = "cand-5683"
    note1["predicate"] = "cites"
    note1["original_quote"] = "Lumbroso, pp. 176, 179, 197, 251, 299"
    note1q = note1["qualifiers"]
    note1q.update({
        "claim": "Haskell's book cites Lumbroso's Notizie sulla vita di Cassiano dal Pozzo at the listed pages.",
        "speaker": "Haskell footnote",
        "text_layer": "bibliographic citation",
        "citation_locator": "Lumbroso, pp. 176, 179, 197, 251, 299",
        "footnote_marker": 1,
        "cited_material_not_independently_consulted": True,
        "qualification": "The references locate cited discussions; they do not show that the cited pages were consulted or independently verified here.",
        "mentioned_candidate_ids": ["cand-2962", "cand-5683", "cand-5626"],
    })
    set_classification(note1, True, "This records one bibliographic source with several page locators; it does not verify the cited material.")
    for object_id, quote, locator in citations_note1:
        new_rows.append(cite_row(
            f"st-chp4-sec-ii-p101-footnote1-cite-{object_id}",
            object_id,
            quote,
            locator,
            242,
            242,
            1,
            "bibliographic citation",
        ))

    note2 = rows["st-chp4-sec-ii-p101-footnote2-lumbroso"]
    note2["subject_candidate_id"] = "cand-2962"
    note2["object_candidate_id"] = "cand-5683"
    note2["predicate"] = "cites"
    note2q = note2["qualifiers"]
    note2q.update({
        "claim": "Haskell's book cites Lumbroso's Notizie sulla vita di Cassiano dal Pozzo, page 211.",
        "speaker": "Haskell footnote",
        "text_layer": "bibliographic citation",
        "citation_locator": "Lumbroso, p. 211",
        "footnote_marker": 2,
        "cited_material_not_independently_consulted": True,
        "qualification": "Keep the page-specific citation; the cited page was not independently consulted.",
        "mentioned_candidate_ids": ["cand-2962", "cand-5683"],
    })
    set_classification(note2, True, "This is a page-specific citation from Haskell's book; it does not verify the cited content.")

    museum = rows["st-chp4-sec-ii-p101-museum-chartaceum"]
    museum["subject_candidate_id"] = "cand-5666"
    museum["object_candidate_id"] = None
    museum["predicate"] = "volume_count_reported"
    museum["original_quote"] = "mentions\n23 volumes."
    museumq = museum["qualifiers"]
    museumq.update({
        "claim": "Haskell reports that Carlo Dati's 1664 publication mentions 23 volumes of Cassiano's paper museum.",
        "speaker": "Haskell citing Carlo Dati, 1664",
        "text_layer": "attributed scalar report",
        "mentioned_candidate_ids": ["cand-5666", "cand-5688"],
        "qualification": "This is Dati's cited count as reported by Haskell; Carlo Antonio's distinct higher count follows and neither figure is independently verified.",
    })
    set_classification(museum, False, "A reported volume count is a scalar attribute, not a relation between two entities.")
    new_rows.extend([
        cite_row(
            "st-chp4-sec-ii-p101-footnote3-dati-citation",
            "cand-5688",
            "For Cassiano’s Museum Chartacewn see Carlo Dati, 1664",
            "Carlo Dati, 1664 (title unspecified)",
            244,
            244,
            3,
            "bibliographic citation",
        ),
        relation_row(
            "st-chp4-sec-ii-p101-dati-lists-museum-contents",
            "cand-5688",
            "cand-5666",
            "lists_contents_of",
            "who gives a list of its contents",
            "Haskell says Carlo Dati's 1664 publication gives a list of the contents of Cassiano's Museum Chartaceum.",
            244,
            244,
            "This is Haskell's report of the cited publication's contents; the publication was not independently consulted.",
        ),
        scalar_row(
            "st-chp4-sec-ii-p101-carlo-antonio-higher-count",
            SEGMENT_NOTES,
            "cand-5666",
            "higher_volume_count_reported",
            "Cassiano’s brother Carlo Antonio says that there were more than this",
            "Haskell reports, through Lumbroso, that Carlo Antonio said the paper museum contained more volumes than Dati's 23.",
            "Haskell reporting Carlo Antonio through Lumbroso",
            "attributed scalar report",
            245,
            245,
            ["cand-5666", "cand-2035", "cand-5683"],
            "This is a second-hand report of a higher count, not an independently verified total; retain the contrast with Dati's 23 volumes.",
        ),
        cite_row(
            "st-chp4-sec-ii-p101-footnote3-lumbroso-citation",
            "cand-5683",
            "Lumbroso, p. 167",
            "Lumbroso, p. 167",
            245,
            245,
            3,
            "bibliographic citation",
        ),
    ])

    # Each source fragment and each citation slice must remain verbatim traceable.
    for row in new_rows:
        if row["statement_id"] in rows:
            raise SystemExit(f"New statement ID already exists: {row['statement_id']}")
        if row["original_quote"] not in source_text:
            raise SystemExit(f"New quote is not an exact source substring: {row['statement_id']}")

    additions_after = {
        "st-chp4-sec-ii-l24-31-antiques-and-guarded-feelings": [new_rows[0]],
        "st-chp4-sec-ii-l24-31-archaeology-and-means": [new_rows[1]],
        "st-chp4-sec-ii-l24-31-only-modern-treatment": [new_rows[2]],
        "st-chp4-sec-ii-p101-footnote1-citations": new_rows[3:8],
        "st-chp4-sec-ii-p101-museum-chartaceum": new_rows[8:12],
    }
    out: list[dict] = []
    for row in statements:
        out.append(row)
        out.extend(additions_after.get(row["statement_id"], []))

    target_output = [row for row in out if row["statement_id"] in TARGET_IDS or row["statement_id"] in {x["statement_id"] for x in new_rows}]
    if len(target_output) != 19:
        raise SystemExit(f"Expected 19 p.101 target rows after atomization, found {len(target_output)}")
    statuses = [row.get("qualifiers", {}).get("relation_candidate") for row in target_output]
    if statuses.count(True) != 11 or statuses.count(False) != 7 or statuses.count(None) != 1:
        raise SystemExit(f"Unexpected p.101 classification counts: {statuses.count(True)} true, {statuses.count(False)} false, {statuses.count(None)} unclassified")
    if not any(row["statement_id"] == "st-chp4-sec-ii-l24-31-veneration-fragment" and row.get("qualifiers", {}).get("relation_candidate") is None for row in target_output):
        raise SystemExit("Keep the cross-page veneration statement pending until its p.102 continuation is handled")
    for row in target_output:
        q = row.get("qualifiers", {})
        if q.get("relation_candidate") is True:
            endpoints = [row.get("subject_candidate_id"), row.get("object_candidate_id")]
            if not all(endpoints) or not set(endpoints).issubset(candidate_ids):
                raise SystemExit(f"p.101 relation has an invalid endpoint: {row['statement_id']} {endpoints}")
            if not set(endpoints).issubset(set(q.get("mentioned_candidate_ids", []))):
                raise SystemExit(f"p.101 relation endpoint missing from mentioned_candidate_ids: {row['statement_id']}")

    proposed = jsonl_bytes(out, newline)
    print("PREVIEW: 19 p.101 output rows; 11 relation candidates, 7 scalar/non-relation claims, 1 cross-page continuation held for p.102")
    print("PREVIEW: 12 atomic statements added; candidates and mentions unchanged; no S6 formal relations")
    for row in target_output:
        q = row.get("qualifiers", {})
        print(f"REVIEW: {row['statement_id']} | {q.get('relation_candidate')} | {row.get('predicate')} | {row.get('subject_candidate_id')} -> {row.get('object_candidate_id')} | {row.get('original_quote', '')[:90]}")
    print(f"PREVIEW: {STATEMENTS_REL.as_posix()} {sha256(paths[STATEMENTS_REL].read_bytes())} -> {sha256(proposed)} bytes={len(proposed)}")
    if not args.apply:
        print("DRY RUN ONLY. Re-run with --apply to write the prevalidated changes.")
        return 0

    path = paths[STATEMENTS_REL]
    backup = path.with_name(path.name + ".bak-" + BACKUP_TAG)
    if backup.exists():
        raise SystemExit(f"Backup already exists; refusing to overwrite: {backup}")
    with backup.open("xb") as stream:
        stream.write(path.read_bytes())
        stream.flush()
        os.fsync(stream.fileno())
    atomic_write(path, proposed)
    print(f"BACKUP: {backup.relative_to(ROOT).as_posix()} sha256={sha256(backup.read_bytes())}")
    print(f"WRITTEN: {STATEMENTS_REL.as_posix()} sha256={sha256(path.read_bytes())}")
    print("APPLY COMPLETE. Source, candidate and mention tables and formal S6 relations were not modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
