#!/usr/bin/env python3
"""Reconcile Chapter 19 candidate-surface prompts against the reviewed text.

The locator is a heuristic prompt source. This migration records source-local
work groups and collection classes, repairs several existing mappings, and
leaves the generic use of "subject" unmapped. Default execution is read-only;
pass --apply to write after exact preflight checks.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_s2_candidate_surfaces as surface_audit  # noqa: E402

TABLES = ROOT / "04-knowledge" / "tables"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "19_CHP-19Appendix.md"

EXPECTED_HASHES = {
    "04-knowledge/tables/entity-candidates.csv": "a3f70aab1d1afe5200bc27f9d1a430299d12f8555f399e7fb2f5a251a9e4a598",
    "04-knowledge/tables/mentions.csv": "c2ee7821af5388282374054d1486e2e7bd0ed3e6c69572f0c378a687ffb1028e",
    "04-knowledge/tables/book-statements.jsonl": "c82eb9b0968c0b2607f10ac357cc8dda9087ef886ce218589780cdc37066ae65",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/s2-coverage.csv": "84f8497a7ce0100f4785acd8bf8ed88bb4c69fe5254cd89d172577b0400eb6c1",
    "02-sources/02-Markdown/19_CHP-19Appendix.md": "725dc16a2983bec379ce2a8b608542ab3defe348d2b2f2a336632ac4905388f1",
    "scripts/audit_s2_candidate_surfaces.py": "130b53da86d940daad454079960415ac5e7043e0b71239370b66226158cd1ee2",
    "scripts/audit_tables.py": "066bbdcd5fc397713af266c0d1fe2bd23f2a66e7affa3ed797f2c104a8d3d5de",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
}

PROMPT_SIGNATURES = {
    ("chp-19:19_CHP-19Appendix:l109-124", 1349, 1356, "subject"),
    ("chp-19:19_CHP-19Appendix:l109-124", 1628, 1638, "collection"),
    ("chp-19:19_CHP-19Appendix:l109-124", 1956, 1966, "Collection"),
    ("chp-19:19_CHP-19Appendix:l109-124", 2143, 2149, "palace"),
    ("chp-19:19_CHP-19Appendix:l109-124", 2354, 2364, "collection"),
    ("chp-19:19_CHP-19Appendix:l109-124", 2528, 2538, "collection"),
    ("chp-19:19_CHP-19Appendix:l109-124", 2911, 2919, "drawings"),
    ("chp-19:19_CHP-19Appendix:l109-124", 3204, 3214, "Collection"),
    ("chp-19:19_CHP-19Appendix:l126-138", 558, 568, "collection"),
    ("chp-19:19_CHP-19Appendix:l126-138", 631, 641, "Collection"),
    ("chp-19:19_CHP-19Appendix:l140-155", 1186, 1196, "collection"),
    ("chp-19:19_CHP-19Appendix:l140-155", 2065, 2071, "palace"),
    ("chp-19:19_CHP-19Appendix:l140-155", 2295, 2303, "drawings"),
    ("chp-19:19_CHP-19Appendix:l140-155", 2736, 2746, "collection"),
    ("chp-19:19_CHP-19Appendix:l140-155", 3042, 3052, "collection"),
    ("chp-19:19_CHP-19Appendix:l3-20", 46, 57, "altarpieces"),
    ("chp-19:19_CHP-19Appendix:l65-84", 791, 798, "modello"),
}

NO_WRITE = {
    ("chp-19:19_CHP-19Appendix:l109-124", 1349, 1356): (
        "The phrase says the Uccelli list gives the subject but not the artist; "
        "it is a generic description, not the Contracts index subentry."
    )
}

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-11509",
        "index_entry_id": "",
        "canonical_name": "Altarpieces in S. Andrea al Quirinale named in the Appendix 1 heading",
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "The heading describes documents concerning altarpieces at S. Andrea al Quirinale "
            "by Giacinto Brandi and Carlo Maratta. It gives no count or individual work titles. "
            "Do not equate this group with the specifically described Brandi Novitiate painting "
            "cand-10749 or infer that every planned work was completed."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-19:19_CHP-19Appendix:l3-20#L5",
    },
    {
        "candidate_id": "cand-11510",
        "index_entry_id": "",
        "canonical_name": "Several hundred pictures recorded in Joseph Smith's palace in 1770",
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Haskell reports that Uccelli recorded several hundred pictures in Smith's palace "
            "at his death in 1770. Individual works and the palace identity are not supplied. "
            "Keep this recorded group distinct from the archival list cand-10806 and from the "
            "1762 sale group cand-10807; possible overlap is unresolved."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-19:19_CHP-19Appendix:l109-124#L118",
    },
    {
        "candidate_id": "cand-11511",
        "index_entry_id": "",
        "canonical_name": "Joseph Smith's mixed collection discussed in Appendix 5",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Haskell discusses Smith's collection as a mixed body of books, gems, pictures, and "
            "drawings in connection with the 1761 will and later disposal hypotheses. The type "
            "and precise boundaries are unresolved. Do not equate this aggregate with the 1762 "
            "sale group cand-10807, the 1770 picture group cand-11510, or the 1776 remainder "
            "cand-11516; overlap and continuity remain questions for S3."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-19:19_CHP-19Appendix:l109-124#L122",
    },
    {
        "candidate_id": "cand-11512",
        "index_entry_id": "",
        "canonical_name": "Drawings named as a collection class in Joseph Smith's 1761 will",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Haskell reports that Smith hoped the drawings class of his collection might remain "
            "united. Individual sheets and extent are not identified. Keep source-local and "
            "distinct from other Smith drawing groups, including cand-9224, pending S3 alignment."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-19:19_CHP-19Appendix:l109-124#L122",
    },
    {
        "candidate_id": "cand-11513",
        "index_entry_id": "",
        "canonical_name": "Pictures named as a collection class in Joseph Smith's 1761 will",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Haskell reports that Smith hoped the pictures class of his collection might remain "
            "united. Individual works are not identified. Keep distinct from the 1762 sale group "
            "cand-10807, the 1770 recorded group cand-11510, and other Smith picture holdings "
            "pending S3 alignment."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-19:19_CHP-19Appendix:l109-124#L122",
    },
    {
        "candidate_id": "cand-11514",
        "index_entry_id": "",
        "canonical_name": "Gems named as a collection class in Joseph Smith's 1761 will",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "The source spells the class 'Gemms' in the OCR. Haskell says Smith hoped the class "
            "might remain united; individual stones and the exact collection boundary are not "
            "given. Keep distinct from cand-9228 pending S3 alignment."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-19:19_CHP-19Appendix:l109-124#L122",
    },
    {
        "candidate_id": "cand-11515",
        "index_entry_id": "",
        "canonical_name": "Drawings said to be included in Joseph Smith's library negotiations",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Haskell says the library under negotiation by about 1755 included drawings. The "
            "individual drawings are not identified. Keep this library-related set distinct from "
            "the separate Drawings class cand-11512 until S3 can resolve their overlap."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-19:19_CHP-19Appendix:l109-124#L122",
    },
    {
        "candidate_id": "cand-11516",
        "index_entry_id": "",
        "canonical_name": "Remaining pictures and drawings from Joseph Smith's collection sold in 1776",
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Haskell says the remaining pictures and drawings were sold in London in 1776 at two "
            "Christie's sales. Individual works and assignment to either date are not supplied. "
            "Keep distinct from the sale events cand-10816 and cand-10817, the drawings and "
            "etchings group cand-10826, and the 1770 picture group cand-11510."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-19:19_CHP-19Appendix:l140-155#L150",
    },
]

NEW_MENTIONS = [
    ("m-chp19-surface-001", "chp-19:19_CHP-19Appendix:l3-20", "cand-11509", "altarpieces", 46, 57,
     "Collective work reference in the Appendix 1 heading; individual altarpieces are not named."),
    ("m-chp19-surface-002", "chp-19:19_CHP-19Appendix:l109-124", "cand-11511", "collection", 1628, 1638,
     "The collection Smith might have continued adding to; its relation to the sale and later holdings remains unresolved."),
    ("m-chp19-surface-003", "chp-19:19_CHP-19Appendix:l109-124", "cand-9171", "his palace", 2139, 2149,
     "Smith's unnamed palace in the unresolved 1762–1770 picture-history discussion."),
    ("m-chp19-surface-004", "chp-19:19_CHP-19Appendix:l109-124", "cand-11511", "collection", 2354, 2364,
     "The mixed collection described in Haskell's summary of Smith's 1761 will."),
    ("m-chp19-surface-005", "chp-19:19_CHP-19Appendix:l109-124", "cand-11511", "collection", 2528, 2538,
     "The mixed collection whose classes Smith hoped might remain united."),
    ("m-chp19-surface-006", "chp-19:19_CHP-19Appendix:l109-124", "cand-11514", "Gemms", 2589, 2594,
     "OCR spelling of the gems class named in the 1761 will; individual stones are unspecified."),
    ("m-chp19-surface-007", "chp-19:19_CHP-19Appendix:l109-124", "cand-9177", "books", 2885, 2890,
     "Books listed among the holdings Smith had built up; related to the library candidate without resolving its full contents."),
    ("m-chp19-surface-008", "chp-19:19_CHP-19Appendix:l109-124", "cand-11514", "gems", 2892, 2896,
     "Gems listed as one component of Smith's mixed collection; no individual stones are identified."),
    ("m-chp19-surface-009", "chp-19:19_CHP-19Appendix:l109-124", "cand-11513", "pictures", 2898, 2906,
     "Pictures listed as one class within Smith's mixed collection; individual works are unspecified."),
    ("m-chp19-surface-010", "chp-19:19_CHP-19Appendix:l109-124", "cand-11512", "drawings", 2911, 2919,
     "Drawings listed as one class within Smith's mixed collection; individual sheets are unspecified."),
    ("m-chp19-surface-011", "chp-19:19_CHP-19Appendix:l109-124", "cand-2292", "Royal\nCollection", 3198, 3214,
     "Royal Collection across the line break at the end of the 1762 sale sentence."),
    ("m-chp19-surface-012", "chp-19:19_CHP-19Appendix:l126-138", "cand-11511", "collection", 558, 568,
     "The mixed collection Haskell says Smith may have wished to dispose of."),
    ("m-chp19-surface-013", "chp-19:19_CHP-19Appendix:l126-138", "cand-11511", "Collection", 631, 641,
     "Smith's quoted phrase 'this whole Collection, the work of my life'."),
    ("m-chp19-surface-014", "chp-19:19_CHP-19Appendix:l140-155", "cand-11511", "collection", 1186, 1196,
     "Haskell's reference to the collection Smith had built up; the sentence is quoted as Smith's statement."),
    ("m-chp19-surface-015", "chp-19:19_CHP-19Appendix:l140-155", "cand-11510", "pictures", 2043, 2051,
     "Pictures in Smith's palace in 1770, discussed by Haskell as the recorded group."),
    ("m-chp19-surface-016", "chp-19:19_CHP-19Appendix:l140-155", "cand-9171", "his palace", 2061, 2071,
     "Second occurrence of Smith's unnamed palace in Haskell's provisional synthesis."),
    ("m-chp19-surface-017", "chp-19:19_CHP-19Appendix:l140-155", "cand-11516", "remaining pictures and drawings", 2272, 2303,
     "Group Haskell says was sold in London in 1776; the two sale dates are not assigned individual works."),
    ("m-chp19-surface-018", "chp-19:19_CHP-19Appendix:l140-155", "cand-11511", "collection", 2736, 2746,
     "Collection named in Haskell's qualified provenance phrase 'said to have come from Smith's collection'."),
    ("m-chp19-surface-019", "chp-19:19_CHP-19Appendix:l140-155", "cand-11511", "collection", 3042, 3052,
     "Smith's collection from which Haskell says no further pictures had been traced."),
    ("m-chp19-surface-020", "chp-19:19_CHP-19Appendix:l65-84", "cand-5555", "modello", 791, 798,
     "Second reference to Tacca's horse model in the same sentence; distinct from the preliminary oil-sketch term cand-3451."),
]

MENTION_UPDATES = {
    "m-chp19-p391-015": {"candidate_id": ("cand-10806", "cand-11510"),
                         "note": "The several hundred pictures recorded in 1770; cand-10806 is the archival list, not the pictures."},
    "m-chp19-p391-028": {"candidate_id": ("cand-10807", "cand-11512"),
                         "note": "Drawings named as a collection class in Smith's 1761 will; not the separate 1762 sale group."},
    "m-chp19-p391-029": {"candidate_id": ("cand-10807", "cand-11513"),
                         "note": "Pictures named as a collection class in Smith's 1761 will; not the separate 1762 sale group."},
    "m-chp19-p391-032": {"candidate_id": ("cand-10807", "cand-11515"),
                         "note": "Drawings said to be included in the library under negotiation; keep distinct from the will's separate class pending S3."},
    "m-chp19-p391-037": {"candidate_id": ("cand-2447", "cand-11511"),
                         "note": "The mixed collection Smith expected might be sold after his death; not Joseph Smith as a person."},
    "m-chp19-p393-053": {"candidate_id": ("cand-2447", "cand-11511"),
                         "note": "Smith's collection in 1762, the source basis Haskell discusses; distinct from the person candidate."},
    "m-chp19-p391-039": {"end_char": ("1955", "1966"),
                         "surface_form": ("the Royal", "the Royal Collection"),
                         "note": "Complete Royal Collection mention; the existing span stopped before Collection."},
}

STATEMENT_EDITS = {
    "st-chp19-p386-appendix-archive-locator": {
        "subject": "cand-5338", "object": "cand-0695", "add": ["cand-11509"], "remove": []},
    "st-chp19-p391-smith-1770-picture-list": {
        "subject": "cand-2665", "object": "cand-10806", "new_object": "cand-11510",
        "add": ["cand-11510"] , "remove": []},
    "st-chp19-p391-smith-sale-hypotheses-unresolved": {
        "subject": "cand-2447", "object": "cand-10806",
        "add": ["cand-9171", "cand-11510", "cand-11511"], "remove": []},
    "st-chp19-p391-smith-1761-will-and-collection-classes": {
        "subject": "cand-2476", "object": "cand-8651",
        "add": ["cand-11511", "cand-11512", "cand-11513", "cand-11514", "cand-11515"],
        "remove": ["cand-10807"]},
    "st-chp19-p391-smith-1761-expectation-and-1762-sale": {
        "subject": "cand-2476", "object": "cand-9278",
        "add": ["cand-11511", "cand-11512", "cand-11513", "cand-11514"], "remove": []},
    "st-chp19-p392-smith-1761-relocation-and-reports": {
        "subject": "cand-2447", "object": "cand-9171", "add": ["cand-11511"], "remove": []},
    "st-chp19-p392-smith-disposal-and-purchase-inferences": {
        "subject": "cand-2447", "object": None, "add": ["cand-11511"], "remove": []},
    "st-chp19-p393-smith-own-collection-remark": {
        "subject": "cand-2447", "object": "cand-10807", "new_object": "cand-11511",
        "add": ["cand-11511"], "remove": []},
    "st-chp19-p393-haskell-smith-sale-synthesis": {
        "subject": "cand-2447", "object": "cand-1141", "add": ["cand-11510", "cand-11511"], "remove": []},
    "st-chp19-p393-1789-anonymous-sale-and-attributed-groups": {
        "subject": "cand-2447", "object": "cand-10818", "add": ["cand-11511"], "remove": []},
    "st-chp19-p393-haskell-future-picture-find-inference": {
        "subject": "cand-2447", "object": None, "add": ["cand-11511"], "remove": []},
    "st-chp19-p393-haskell-basis-for-smith-taste-discussion": {
        "subject": "cand-2447", "object": "cand-10807", "new_object": "cand-11511",
        "add": ["cand-11511"], "remove": []},
    "st-chp19-p393-christies-1776-sales-and-listed-pictures": {
        "subject": "cand-2447", "object": None, "add": ["cand-11516"], "remove": []},
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_hashes() -> None:
    mismatches = []
    for relative, expected in EXPECTED_HASHES.items():
        actual = sha256(ROOT / relative)
        if actual != expected:
            mismatches.append(f"{relative}: expected {expected}, got {actual}")
    if mismatches:
        raise RuntimeError("preflight hash mismatch:\n" + "\n".join(mismatches))


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line]


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> Path:
    target = path.with_name(path.name + ".next")
    with target.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)
    return target


def write_jsonl(path: Path, rows: list[dict[str, object]], changed_ids: set[str]) -> Path:
    target = path.with_name(path.name + ".next")
    original_bytes = path.read_bytes()
    has_bom = original_bytes.startswith(b"\xef\xbb\xbf")
    original_text = original_bytes.decode("utf-8-sig")
    updated = {str(row["statement_id"]): row for row in rows if str(row["statement_id"]) in changed_ids}
    output: list[str] = []
    for raw_line in original_text.splitlines(keepends=True):
        line = raw_line.rstrip("\r\n")
        ending = raw_line[len(line):]
        if not ending:
            ending = "\n"
        current = json.loads(line)
        statement_id = str(current["statement_id"])
        if statement_id not in changed_ids:
            output.append(raw_line)
            continue
        separators = (", ", ": ") if ', "' in line else (",", ":")
        output.append(json.dumps(updated[statement_id], ensure_ascii=False, separators=separators) + ending)
    with target.open("wb") as handle:
        if has_bom:
            handle.write(b"\xef\xbb\xbf")
        handle.write("".join(output).encode("utf-8"))
    return target


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def check_prompt_signature() -> list[dict[str, object]]:
    summary, hits = surface_audit.audit("chp-19", 6)
    found = {
        (str(hit["segment_id"]), int(hit["start_char"]), int(hit["end_char"]), str(hit["surface_form"]))
        for hit in hits
    }
    require(found == PROMPT_SIGNATURES,
            f"candidate-surface prompt set changed: expected {len(PROMPT_SIGNATURES)}, got {len(found)}")
    return hits


def check_source_spans(segments: list[dict[str, object]]) -> None:
    by_id = {str(row["segment_id"]): row for row in segments}
    cache: dict[str, list[str]] = {}
    for mention in NEW_MENTIONS:
        _, segment_id, _, surface, start, end, _ = mention
        row = by_id[segment_id]
        source_file = str(row["source_file"])
        if source_file not in cache:
            cache[source_file] = (ROOT / source_file).read_text(encoding="utf-8-sig").splitlines()
        lines = cache[source_file]
        text = "\n".join(lines[int(row["line_start"]) - 1:int(row["line_end"])])
        require(text[start:end] == surface,
                f"source span mismatch for {mention[0]}: {text[start:end]!r} != {surface!r}")


def prepare() -> tuple[list[str], list[dict[str, str]], list[dict[str, str]], list[dict[str, object]], list[dict[str, object]]]:
    check_hashes()
    hits = check_prompt_signature()
    c_fields, candidates = read_csv(CANDIDATES)
    m_fields, mentions = read_csv(MENTIONS)
    statements = read_jsonl(STATEMENTS)
    segments = read_jsonl(SEGMENTS)
    require(len(candidates) == 11487, f"candidate count changed: {len(candidates)}")
    require(max(int(row["candidate_id"].split("-")[1]) for row in candidates) == 11508,
            "candidate ID ceiling changed")
    require(len(mentions) == 27371, f"mention count changed: {len(mentions)}")
    require(len(statements) == 12263, f"statement count changed: {len(statements)}")
    candidate_ids = {row["candidate_id"] for row in candidates}
    require(not (candidate_ids & {row["candidate_id"] for row in NEW_CANDIDATES}),
            "a planned candidate ID already exists")
    mention_ids = {row["mention_id"] for row in mentions}
    new_ids = {row[0] for row in NEW_MENTIONS}
    require(len(new_ids) == len(NEW_MENTIONS) and not (mention_ids & new_ids),
            "a planned mention ID already exists or is duplicated")
    check_source_spans(segments)

    mention_by_id = {row["mention_id"]: row for row in mentions}
    for mention_id, edits in MENTION_UPDATES.items():
        require(mention_id in mention_by_id, f"missing expected mention {mention_id}")
        row = mention_by_id[mention_id]
        for key, change in edits.items():
            if key == "note":
                continue
            old_value, _new_value = change
            require(row.get(key) == old_value,
                    f"{mention_id}.{key} changed: expected {old_value!r}, got {row.get(key)!r}")
    statement_by_id = {str(row["statement_id"]): row for row in statements}
    require(len(statement_by_id) == len(statements), "duplicate statement IDs")
    for statement_id, edits in STATEMENT_EDITS.items():
        require(statement_id in statement_by_id, f"missing expected statement {statement_id}")
        row = statement_by_id[statement_id]
        require(row.get("subject_candidate_id") == edits["subject"], f"{statement_id} subject changed")
        require(row.get("object_candidate_id") == edits["object"], f"{statement_id} object changed")
        require("mentioned_candidate_ids" in row["qualifiers"], f"{statement_id} lacks candidate list")
        old_ids = row["qualifiers"]["mentioned_candidate_ids"]
        require(len(old_ids) == len(set(old_ids)), f"{statement_id} has duplicate candidate IDs")
        require(not (set(edits["add"]) & set(old_ids)), f"{statement_id} already contains planned additions")
        require(set(edits["remove"]) <= set(old_ids), f"{statement_id} lacks planned removals")
    return c_fields, candidates, mentions, statements, hits


def apply_changes(c_fields: list[str], candidates: list[dict[str, str]], mentions: list[dict[str, str]],
                  statements: list[dict[str, object]]) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, object]]]:
    candidates.extend(NEW_CANDIDATES)
    mention_by_id = {row["mention_id"]: row for row in mentions}
    for mention_id, edits in MENTION_UPDATES.items():
        row = mention_by_id[mention_id]
        for key, change in edits.items():
            row[key] = change[1] if isinstance(change, tuple) else change
    for mention_id, segment_id, candidate_id, surface, start, end, note in NEW_MENTIONS:
        mentions.append({
            "mention_id": mention_id,
            "segment_id": segment_id,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(end),
            "note": note,
        })
    statement_by_id = {str(row["statement_id"]): row for row in statements}
    for statement_id, edits in STATEMENT_EDITS.items():
        row = statement_by_id[statement_id]
        if "new_object" in edits:
            row["object_candidate_id"] = edits["new_object"]
        ids = row["qualifiers"]["mentioned_candidate_ids"]
        row["qualifiers"]["mentioned_candidate_ids"] = [
            candidate_id for candidate_id in ids if candidate_id not in edits["remove"]
        ] + edits["add"]
    return candidates, mentions, statements


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write after exact source/table preflight")
    args = parser.parse_args()
    c_fields, candidates, mentions, statements, hits = prepare()
    print(json.dumps({
        "mode": "apply" if args.apply else "dry-run",
        "verified_prompt_count": len(hits),
        "no_write": [{"segment_id": seg, "start_char": start, "end_char": end, "reason": reason}
                     for (seg, start, end), reason in NO_WRITE.items()],
        "planned_new_candidates": len(NEW_CANDIDATES),
        "planned_new_mentions": len(NEW_MENTIONS),
        "planned_mention_repairs": len(MENTION_UPDATES),
        "planned_statement_repairs": len(STATEMENT_EDITS),
        "before_counts": {"candidates": len(candidates), "mentions": len(mentions), "statements": len(statements)},
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        return 0

    candidates, mentions, statements = apply_changes(c_fields, candidates, mentions, statements)
    require(len(candidates) == 11495, "unexpected candidate count after apply")
    require(len(mentions) == 27391, "unexpected mention count after apply")
    require(len(statements) == 12263, "unexpected statement count after apply")
    backups = Path(tempfile.mkdtemp(prefix="pnp-s2-chp19-surface-"))
    staged: list[tuple[Path, Path]] = []
    try:
        for path in (CANDIDATES, MENTIONS, STATEMENTS):
            shutil.copy2(path, backups / path.name)
        staged = [
            (write_csv(CANDIDATES, c_fields, candidates), CANDIDATES),
            (write_csv(MENTIONS, read_csv(MENTIONS)[0], mentions), MENTIONS),
            (write_jsonl(STATEMENTS, statements, set(STATEMENT_EDITS)), STATEMENTS),
        ]
        for temporary, destination in staged:
            os.replace(temporary, destination)
    except Exception:
        for path in (CANDIDATES, MENTIONS, STATEMENTS):
            backup = backups / path.name
            if backup.exists():
                shutil.copy2(backup, path)
        raise

    after_summary, after_hits = surface_audit.audit("chp-19", 6)
    print(json.dumps({
        "backup_dir": str(backups),
        "after_counts": {"candidates": len(candidates), "mentions": len(mentions), "statements": len(statements)},
        "after_surface_summary": after_summary,
        "remaining_prompts": after_hits,
        "after_hashes": {path.name: sha256(path) for path in (CANDIDATES, MENTIONS, STATEMENTS)},
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
