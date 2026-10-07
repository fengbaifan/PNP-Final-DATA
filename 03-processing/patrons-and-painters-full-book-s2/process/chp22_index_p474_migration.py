#!/usr/bin/env python3
"""Classify p.474 index entries and repair their existing S2 body references."""

import argparse
import csv
import hashlib
import io
import json
import os
import re
import shutil
import tempfile
from collections import Counter
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
MARKER_SEGMENT = "chp-22:22_CHP-22Index:l3517-3517"
LEFT_SEGMENT = "chp-22:22_CHP-22Index:l3519-3542"
RIGHT_SEGMENT = "chp-22:22_CHP-22Index:l3567-3588"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p474-20261007"

EXPECTED_HASHES = {
    "02-sources/02-Markdown/22_CHP-22Index.md": "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081",
    "02-sources/01-book/CHP-22Index.pdf": "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    "02-sources/03-Index/03-2-Index-CSV/UVWXYZ.csv": "19a9e5db94a3da83c673a7fa03b003ed501317de161e4664ca572b0f0d6d5e21",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "02-sources/02-Markdown/10_CHP-10_intro.md": "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f",
    "02-sources/02-Markdown/10_CHP-10_sec_ii.md": "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9",
    "02-sources/02-Markdown/13_CHP-13_intro.md": "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8",
    "04-knowledge/tables/entity-candidates.csv": "bd7fc3881580e7e41995d64ebb5884890f1758c3ec758a508bc1c02da6fc047a",
    "04-knowledge/tables/mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    "04-knowledge/tables/book-statements.jsonl": "9167379d3236687266b5aafd93b7c110f56ce26a5575e2114134aa2483be2444",
    "04-knowledge/tables/s2-coverage.csv": "69e243e62df96b3d6b8d8766e54460a4845fcfab8d0dfa534492b5eb8e29bae6",
}

EXPECTED_SEGMENT_HASHES = {
    MARKER_SEGMENT: "b41e1c5d45ff46cccff5d4683d7bc4a6550e1a23a869a9cd45152e50b4f1f3ee",
    LEFT_SEGMENT: "3856c20bc4b4cd6c2992f70ee190d138a8c4c0061e683dd6a21904d8ba6be9ae",
    RIGHT_SEGMENT: "8fe160f28e33d2728d5ef14e257d78a3ce93035ea86c95c1246da65dda4babcc",
}

TYPE_BY_ENTRY = {
    191: "person",
    192: "archive",
    193: "person",
    194: "person",
    195: "archive",
    196: "work",
    197: "person",
    198: "person",
    199: "archive",
    200: "person",
    201: "person",
    202: "person",
    203: "archive",
    204: "person",
    205: "person",
    206: "person",
    207: "family",
    208: "place",
    209: "person",
    210: "work",
    211: "person",
    212: "work",
    213: "work",
    214: "person",
    215: "person",
    216: "person",
    217: "person",
    218: "work",
    219: "work",
    220: "work",
    221: "person",
    222: "person",
    223: "person",
    224: "person",
    225: "person",
}
PREEXISTING_TYPES = {"UVWXYZ.csv#197": ("cand-2860", "person")}

DETAIL_UPDATES = {
    "cand-2854": (
        "Main index entry for Antonio Maria Zanetti the Younger. Its publication, topic, and print-suite "
        "subentries are separate candidates; do not duplicate the person."
    ),
    "cand-2855": "Della Pittura Veneziana is a textual art-historical publication and is classified as archive.",
    "cand-2858": "The index refers to the younger Zanetti's 1733 revision of Boschini's textual publication; archive.",
    "cand-2859": (
        "The p.345 context identifies Varie Pitture a Fresco as a 1760 visual album of copies after classic artists; "
        "classify the album as work, not as the bibliographic citation. Compare body candidate cand-10117 at S3."
    ),
    "cand-2862": "Elogio di Rosalba Carriera is a textual encomium/biographical publication; archive.",
    "cand-2866": (
        "The index groups editions of six Italian authors; treat the textual editions as archive material while "
        "retaining the grouped identity and individual title alignment for S3."
    ),
    "cand-2867": "Support of the Jesuits is person-context for Antonio Zatta; the body statement carries the claim.",
    "cand-2870": "The index explicitly identifies the Zenobio family in Venice; family.",
    "cand-2871": "The Zenobio palace is a named architectural space in Venice; place.",
    "cand-2873": "A double portrait is a visual artwork; sitter identities and surviving-work identity remain open.",
    "cand-2875": (
        "Index candidate for Zompini's print series after Castiglione drawings. Keep distinct from the source "
        "drawings (cand-11458) and body-origin print-series candidate cand-10110 until S3."
    ),
    "cand-2876": (
        "Le Arti che vanno per via nella Città di Venezia is the named visual print work; keep the body-origin "
        "candidate cand-10111 separate until S3."
    ),
    "cand-2877": "Work-for subentry is person-context for Gaetano Zompini, not a separate work or relation.",
    "cand-2880": (
        "Rousseau-followers' admiration is a Zuccarelli person-context; the p.328 body statements carry the "
        "specific praise evidence."
    ),
    "cand-2881": (
        "The p.351 text presents this as a proposed subject for a picture, not proof that a painting was completed. "
        "Keep distinct from body candidate cand-10271 until S3."
    ),
    "cand-2882": (
        "The index names a group of six Rebecca, Jacob, and Esau landscapes. Keep separate from body candidate "
        "cand-9252 until S3."
    ),
    "cand-2883": (
        "The Palladian overdoors are decorative works. Keep this Zuccarelli-context candidate distinct from "
        "cand-2785 until S3; the index does not identify the building."
    ),
    "cand-2884": "Work-in-England subentry is person-context for Zuccarelli, not a separate person.",
    "cand-10110": (
        "This is the output series of prints made by Gaetano Zompini after Castiglione drawings in Zanetti's "
        "collection. Keep it distinct from the source drawings cand-11458, from the index work candidate "
        "cand-2875, and from Zanetti's separate twelve Castiglione drawings engraved in 1759."
    ),
    "cand-10117": (
        "The 1760 Varie Pitture a Fresco is a visual album/print suite of Zanetti's reproductive copies, so it is "
        "classified as work under the art-album rule. Keep separate from index candidate cand-2859 until S3."
    ),
}

MENTION_UPDATES = {
    "m-chp10-p308-zuccarelli": ("cand-2883", "cand-2879"),
    "m-chp10-p308-zuccarelli-enterprise": ("cand-2883", "cand-2879"),
    "m-chp10-p309-zuccarelli-england": ("cand-2883", "cand-2884"),
    "m-s2-ch10-p309n5-zuccarelli": ("cand-2883", "cand-2879"),
    "m-s2-ch13-p344-018": ("cand-2875", "cand-2874"),
    "m-s2-ch13-p344-019": ("cand-10110", "cand-11458"),
    "m-s2-ch13-p344-022": ("cand-2876", "cand-2874"),
}

STATEMENT_MENTION_REPLACEMENTS = {
    "st-chp10-p308-smith-continued-overdoor-series": ("cand-2883", "cand-2879"),
    "st-chp10-p308-visentini-long-employment": ("cand-2883", "cand-2879"),
    "st-chp10-p308-zuccarelli-employment-and-landscape-series": ("cand-2883", "cand-2879"),
    "st-chp10-p308-zuccarelli-role-in-overdoors": ("cand-2883", "cand-2879"),
    "st-chp10-p309-algarotti-diverted-tiepolo-work": ("cand-2883", "cand-2884"),
    "st-chp10-p309-facade-palace-referent": ("cand-2883", "cand-2884"),
    "st-chp10-p309-possible-smith-employment-of-zais": ("cand-2883", "cand-2884"),
    "st-chp10-p309-smith-contemporary-patronage-diminished": ("cand-2883", "cand-2884"),
    "st-chp10-p309-smith-shift-to-sober-landscapes-and-architecture": ("cand-2883", "cand-2884"),
    "st-chp10-p309-tiepolo-commission-came-to-nothing": ("cand-2883", "cand-2884"),
    "st-chp10-p309-visentini-built-marble-facade": ("cand-2883", "cand-2884"),
    "st-chp10-p309-zais-landscapes-excluded-from-george-iii-sale": ("cand-2883", "cand-2884"),
    "st-chp10-p309-note5-smith-patron-of-zuccarelli": ("cand-2883", "cand-2879"),
}

RELATION_CANDIDATE_IDS = {
    "st-chp10-p328-baretti-wrote-enthusiastically-of-zuccarelli",
    "st-chp10-p328-biffi-praised-zuccarelli-in-letter",
    "st-chp10-p328-smith-employed-zuccarelli",
    "st-chp10-p328-zanetti-praised-zuccarelli",
    "st-chp13-p339-zatta-dante-support",
    "st-chp13-p342-zanetti_admired_canaletto_and_zuccarelli_early",
    "st-chp13-p345-varie-pitture-1760",
    "st-chp13-p345-ricche-miniere-edited-1733",
    "st-chp13-p345-della-pittura-veneziana-1771",
}

NEW_STATEMENT_ID = "st-chp13-p342-zanetti_admired_zuccarelli_early"

COVERAGE_SPECS = {
    MARKER_SEGMENT: (
        "excluded",
        "L3517",
        "no_semantic_content: S0 L3517 is the generated [Page 474] marker, confirmed on "
        "CHP-22Index.pdf physical p.32; it is navigation text, not an indexed object or factual claim.",
    ),
    LEFT_SEGMENT: (
        "reviewed",
        "L3519-3542",
        "no_semantic_content: index-navigation-only; index-seed classification. CHP-22Index.pdf physical p.32 "
        "prints p.474. The column maps UVWXYZ.csv#191-210 (20 rows): 19 newly typed and pre-existing "
        "cand-2860/#197 person type retained. Types: 12 person, 4 archive, 2 work, 1 family, 1 place. "
        "Index person-contexts do not independently establish relations; related claims remain in body statements.",
    ),
    RIGHT_SEGMENT: (
        "reviewed",
        "L3567-3588",
        "no_semantic_content: index-navigation-only; index-seed classification. CHP-22Index.pdf physical p.32 "
        "prints p.474. The column maps UVWXYZ.csv#211-225 (15 rows): 10 person and 5 work. The six landscapes, "
        "Palladian overdoors, and proposed Hunt subject remain distinct candidate records for S3 identity review; "
        "the index itself adds no mentions, statements, or formal relations.",
    ),
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    return raw.startswith(b"\xef\xbb\xbf"), "\r\n" if "\r\n" in text else "\n", list(
        csv.DictReader(io.StringIO(text, newline=""))
    )


def write_csv(path, rows, bom, line_ending):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator=line_ending)
    writer.writeheader()
    writer.writerows(rows)
    payload = output.getvalue().encode("utf-8")
    if bom:
        payload = b"\xef\xbb\xbf" + payload
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(payload)
    os.replace(temporary, path)


def read_jsonl(path):
    raw = path.read_bytes()
    return raw.startswith(b"\xef\xbb\xbf"), raw.decode("utf-8-sig").splitlines(keepends=True)


def write_jsonl(path, lines, bom):
    payload = "".join(lines).encode("utf-8")
    if bom:
        payload = b"\xef\xbb\xbf" + payload
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(payload)
    os.replace(temporary, path)


def serialize_jsonl(row, newline):
    return json.dumps(row, ensure_ascii=False, separators=(",", ":")) + newline


def dedupe(values):
    return list(dict.fromkeys(values))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Write the guarded migration; default is dry-run.")
    args = parser.parse_args()

    for relative, expected in EXPECTED_HASHES.items():
        path = ROOT / relative
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"preflight hash mismatch: {relative}")

    segment_records = [
        json.loads(line)
        for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
    ]
    segments = {row["segment_id"]: row for row in segment_records}
    for segment_id, expected in EXPECTED_SEGMENT_HASHES.items():
        row = segments.get(segment_id)
        if not row or row.get("sha256") != expected:
            raise SystemExit(f"p.474 segment changed or missing: {segment_id}")

    candidate_path = TABLES / "entity-candidates.csv"
    mention_path = TABLES / "mentions.csv"
    statement_path = TABLES / "book-statements.jsonl"
    coverage_path = TABLES / "s2-coverage.csv"
    candidate_bom, candidate_eol, candidates = read_csv(candidate_path)
    mention_bom, mention_eol, mentions = read_csv(mention_path)
    coverage_bom, coverage_eol, coverage = read_csv(coverage_path)
    statement_bom, statement_lines = read_jsonl(statement_path)

    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    candidate_by_entry = {}
    for row in candidates:
        entry_id = row["index_entry_id"]
        if entry_id:
            if entry_id in candidate_by_entry:
                raise SystemExit(f"duplicate index seed candidate: {entry_id}")
            candidate_by_entry[entry_id] = row

    expected_entries = {f"UVWXYZ.csv#{number}" for number in TYPE_BY_ENTRY}
    if expected_entries - set(candidate_by_entry):
        raise SystemExit("one or more p.474 index seed candidates are missing")
    if len(expected_entries) != 35:
        raise SystemExit("p.474 seed mapping must contain exactly 35 rows")
    if len(candidates) != 11436 or max(int(row["candidate_id"].split("-")[1]) for row in candidates) != 11457:
        raise SystemExit("candidate count or next-ID boundary changed")
    for entry_id, (candidate_id, entity_type) in PREEXISTING_TYPES.items():
        row = candidate_by_entry.get(entry_id)
        if not row or row["candidate_id"] != candidate_id or row["suggested_type"] != entity_type:
            raise SystemExit(f"pre-existing p.474 type changed: {entry_id}")
    for number in TYPE_BY_ENTRY:
        entry_id = f"UVWXYZ.csv#{number}"
        row = candidate_by_entry[entry_id]
        if entry_id not in PREEXISTING_TYPES and (row["suggested_type"] or row["status"] != "open"):
            raise SystemExit(f"p.474 candidate is no longer open/untyped: {entry_id}")

    for candidate_id in DETAIL_UPDATES:
        if candidate_id not in candidate_by_id:
            raise SystemExit(f"candidate detail target missing: {candidate_id}")
    if candidate_by_id["cand-10117"]["suggested_type"] != "archive":
        raise SystemExit("cand-10117 prestate changed; review its work/archive classification")
    if candidate_by_id["cand-10110"]["suggested_type"] != "work":
        raise SystemExit("cand-10110 is not the expected body-origin work candidate")
    if "cand-11458" in candidate_by_id:
        raise SystemExit("planned source-drawing candidate cand-11458 already exists")

    mentions_by_id = {row["mention_id"]: row for row in mentions}
    if len(mentions_by_id) != len(mentions):
        raise SystemExit("duplicate mention ID before migration")
    for mention_id, (before, _after) in MENTION_UPDATES.items():
        row = mentions_by_id.get(mention_id)
        if not row or row["candidate_id"] != before:
            raise SystemExit(f"mention mapping changed or missing: {mention_id}")

    parsed = {}
    statement_locations = {}
    for index, line in enumerate(statement_lines):
        if not line.strip():
            continue
        row = json.loads(line)
        statement_id = row.get("statement_id")
        if statement_id in parsed:
            raise SystemExit(f"duplicate statement ID before migration: {statement_id}")
        parsed[statement_id] = row
        statement_locations[statement_id] = index
    if len(parsed) != 12107:
        raise SystemExit("statement count changed")
    if NEW_STATEMENT_ID in parsed:
        raise SystemExit(f"planned endpoint-specific statement already exists: {NEW_STATEMENT_ID}")
    for statement_id, (before, _after) in STATEMENT_MENTION_REPLACEMENTS.items():
        row = parsed.get(statement_id)
        if not row or before not in row.get("qualifiers", {}).get("mentioned_candidate_ids", []):
            raise SystemExit(f"statement mention reference changed or missing: {statement_id}")
    for statement_id in RELATION_CANDIDATE_IDS:
        row = parsed.get(statement_id)
        if not row or "relation_candidate" in row.get("qualifiers", {}):
            raise SystemExit(f"relation-candidate prestate changed or missing: {statement_id}")
    castiglione = parsed.get("st-chp13-p344-zompini-engraved_castiglione_series")
    owns_drawings = parsed.get("st-chp13-p344-zanetti-owned_castiglione_drawings")
    le_arti = parsed.get("st-chp13-p344-zompini-drew_for_le_arti_1753")
    if not castiglione or (
        castiglione.get("subject_candidate_id"), castiglione.get("object_candidate_id"),
        castiglione.get("predicate")
    ) != ("cand-2875", "cand-10110", "engraved_a_series_of"):
        raise SystemExit("Zompini print-series statement changed")
    if not owns_drawings or (
        owns_drawings.get("subject_candidate_id"), owns_drawings.get("object_candidate_id")
    ) != ("cand-10110", "cand-2838"):
        raise SystemExit("Castiglione drawing ownership statement changed")
    if not le_arti or (
        le_arti.get("subject_candidate_id"), le_arti.get("object_candidate_id")
    ) != ("cand-2876", "cand-10111"):
        raise SystemExit("Le Arti statement changed")
    admiration = parsed.get("st-chp13-p342-zanetti_admired_canaletto_and_zuccarelli_early")
    if not admiration or (
        admiration.get("subject_candidate_id"), admiration.get("object_candidate_id"),
        admiration.get("qualifiers", {}).get("source_line_start")
    ) != ("cand-2838", None, 104):
        raise SystemExit("p.342 compound admiration statement changed")

    coverage_by_id = {row["segment_id"]: row for row in coverage}
    if len(coverage_by_id) != len(coverage):
        raise SystemExit("duplicate coverage segment ID")
    for segment_id in COVERAGE_SPECS:
        row = coverage_by_id.get(segment_id)
        if not row or (
            row["disposition"], row["migration_status"], row["source_line_ranges"], row["note"]
        ) != ("queued", "pending", "", ""):
            raise SystemExit(f"p.474 coverage is not queued/pending: {segment_id}")

    # Apply only after every source, seed, FK, and coverage precondition passes.
    for number, entity_type in TYPE_BY_ENTRY.items():
        candidate_by_entry[f"UVWXYZ.csv#{number}"]["suggested_type"] = entity_type
    for candidate_id, detail in DETAIL_UPDATES.items():
        candidate_by_id[candidate_id]["detail"] = detail
    candidate_by_id["cand-10117"]["suggested_type"] = "work"
    candidate_by_id["cand-11458"] = {
        field: {
            "candidate_id": "cand-11458",
            "index_entry_id": "",
            "canonical_name": (
                "Unidentified Castiglione drawings owned by A. M. Zanetti the Elder and used by Gaetano Zompini"
            ),
            "index_page_range": "",
            "suggested_type": "work",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": (
                "The p.344 text distinguishes Castiglione's source drawings in Zanetti's collection from "
                "Zompini's resulting print series. Individual titles and count are not supplied; keep distinct "
                "from print candidates cand-2875 and cand-10110."
            ),
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": "chp-13:13_CHP-13_intro:l116-122#L119",
        }[field]
        for field in candidates[0]
    }
    candidates.append(candidate_by_id["cand-11458"])

    for mention_id, (before, after) in MENTION_UPDATES.items():
        mentions_by_id[mention_id]["candidate_id"] = after

    for segment_id, (disposition, line_range, note) in COVERAGE_SPECS.items():
        coverage_by_id[segment_id].update({
            "disposition": disposition,
            "migration_status": "complete",
            "source_line_ranges": line_range,
            "note": note,
        })

    rewritten_lines = []
    statement_updates = set()
    statement_additions = []
    for line in statement_lines:
        newline = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
        body = line.rstrip("\r\n")
        if not body.strip():
            rewritten_lines.append(line)
            continue
        row = json.loads(body)
        statement_id = row["statement_id"]
        changed = False
        qualifiers = row.setdefault("qualifiers", {})
        if statement_id in STATEMENT_MENTION_REPLACEMENTS:
            before, after = STATEMENT_MENTION_REPLACEMENTS[statement_id]
            values = qualifiers.get("mentioned_candidate_ids", [])
            if before not in values:
                raise SystemExit(f"expected FK is absent during rewrite: {statement_id}")
            qualifiers["mentioned_candidate_ids"] = dedupe(
                [after if value == before else value for value in values]
            )
            changed = True
        if statement_id == "st-chp10-p308-zuccarelli-employment-and-landscape-series":
            row["subject_candidate_id"] = "cand-2879"
            changed = True
        if statement_id == "st-chp10-p308-zuccarelli-role-in-overdoors":
            row["subject_candidate_id"] = "cand-2879"
            changed = True
        if statement_id == "st-chp10-p309-note5-smith-patron-of-zuccarelli":
            row["object_candidate_id"] = "cand-2879"
            changed = True
        if statement_id == "st-chp13-p344-zompini-engraved_castiglione_series":
            row["subject_candidate_id"] = "cand-2874"
            qualifiers["mentioned_candidate_ids"] = [
                "cand-2874", "cand-11458", "cand-2875", "cand-10110"
            ]
            changed = True
        if statement_id == "st-chp13-p344-zanetti-owned_castiglione_drawings":
            row["subject_candidate_id"] = "cand-11458"
            qualifiers["mentioned_candidate_ids"] = ["cand-11458", "cand-2838"]
            changed = True
        if statement_id == "st-chp13-p344-zompini-drew_for_le_arti_1753":
            row["subject_candidate_id"] = "cand-2874"
            qualifiers["mentioned_candidate_ids"] = ["cand-2874", "cand-2876", "cand-10111"]
            changed = True
        if statement_id in RELATION_CANDIDATE_IDS:
            qualifiers["relation_candidate"] = True
            changed = True
        if statement_id == "st-chp13-p342-zanetti_admired_canaletto_and_zuccarelli_early":
            row["object_candidate_id"] = "cand-0498"
            row["predicate"] = "zanetti_admired_canaletto_at_career_start"
            qualifiers["claim"] = (
                "Haskell says the elder A. M. Zanetti was a keen admirer of Canaletto at the very beginning "
                "of Canaletto's career."
            )
            qualifiers["qualification"] = (
                "Retain Haskell's timing and characterization; this does not establish a specific purchase, "
                "commission, or meeting."
            )
            qualifiers["mentioned_candidate_ids"] = ["cand-2838", "cand-0498"]
            qualifiers["relation_candidate"] = True
            copy = deepcopy(row)
            copy["statement_id"] = NEW_STATEMENT_ID
            copy["object_candidate_id"] = "cand-2879"
            copy["predicate"] = "zanetti_admired_zuccarelli_at_career_start"
            copy["qualifiers"]["claim"] = (
                "Haskell says the elder A. M. Zanetti was a keen admirer of Zuccarelli at the very beginning "
                "of Zuccarelli's career."
            )
            copy["qualifiers"]["mentioned_candidate_ids"] = ["cand-2838", "cand-2879"]
            copy["original_quote"] = row["original_quote"]
            statement_additions.append(serialize_jsonl(copy, newline))
            statement_updates.add(statement_id)
            rewritten_lines.append(serialize_jsonl(row, newline))
            rewritten_lines.extend(statement_additions[-1:])
            continue
        if changed:
            statement_updates.add(statement_id)
            rewritten_lines.append(serialize_jsonl(row, newline))
        else:
            rewritten_lines.append(line)

    expected_updates = set(STATEMENT_MENTION_REPLACEMENTS) | {
        "st-chp10-p308-zuccarelli-employment-and-landscape-series",
        "st-chp10-p308-zuccarelli-role-in-overdoors",
        "st-chp10-p309-note5-smith-patron-of-zuccarelli",
        "st-chp13-p344-zompini-engraved_castiglione_series",
        "st-chp13-p344-zanetti-owned_castiglione_drawings",
        "st-chp13-p344-zompini-drew_for_le_arti_1753",
    } | RELATION_CANDIDATE_IDS
    if statement_updates != expected_updates or len(statement_additions) != 1:
        raise SystemExit("statement rewrite set differs from the guarded migration plan")

    left_rows = [candidate_by_entry[f"UVWXYZ.csv#{number}"] for number in range(191, 211)]
    right_rows = [candidate_by_entry[f"UVWXYZ.csv#{number}"] for number in range(211, 226)]
    type_counts = dict(sorted(Counter(TYPE_BY_ENTRY.values()).items()))
    segment_type_counts = {
        LEFT_SEGMENT: dict(sorted(Counter(row["suggested_type"] for row in left_rows).items())),
        RIGHT_SEGMENT: dict(sorted(Counter(row["suggested_type"] for row in right_rows).items())),
    }
    index_untyped_before = sum(
        bool(row["index_entry_id"]) and row["status"] == "open" and not row["suggested_type"]
        for row in read_csv(candidate_path)[2]
    )
    index_untyped_after = sum(
        bool(row["index_entry_id"]) and row["status"] == "open" and not row["suggested_type"]
        for row in candidates
    )
    statement_count_before = len(parsed)
    statement_count_after = statement_count_before + len(statement_additions)
    summary = {
        "segments": {
            MARKER_SEGMENT: "excluded/complete",
            LEFT_SEGMENT: "reviewed/complete",
            RIGHT_SEGMENT: "reviewed/complete",
        },
        "p474_index_rows": 35,
        "newly_typed": 34,
        "candidate_type_updates": {
            candidate_by_entry[f"UVWXYZ.csv#{number}"]["candidate_id"]: entity_type
            for number, entity_type in TYPE_BY_ENTRY.items()
            if f"UVWXYZ.csv#{number}" not in PREEXISTING_TYPES
        },
        "candidate_detail_updates": sorted(DETAIL_UPDATES),
        "preexisting_type_preserved": PREEXISTING_TYPES,
        "classified_types": type_counts,
        "segment_type_counts": segment_type_counts,
        "new_source_drawing_candidate": "cand-11458",
        "body_candidate_type_correction": {"candidate_id": "cand-10117", "before": "archive", "after": "work"},
        "mentions_changed": len(MENTION_UPDATES),
        "mention_fk_updates": {
            mention_id: {"before": before, "after": after}
            for mention_id, (before, after) in MENTION_UPDATES.items()
        },
        "existing_statements_updated": len(statement_updates),
        "statement_fk_updates": sorted(
            set(STATEMENT_MENTION_REPLACEMENTS)
            | {
                "st-chp10-p308-zuccarelli-employment-and-landscape-series",
                "st-chp10-p308-zuccarelli-role-in-overdoors",
                "st-chp10-p309-note5-smith-patron-of-zuccarelli",
                "st-chp13-p344-zompini-engraved_castiglione_series",
                "st-chp13-p344-zanetti-owned_castiglione_drawings",
                "st-chp13-p344-zompini-drew_for_le_arti_1753",
            }
        ),
        "new_endpoint_specific_statements": [NEW_STATEMENT_ID],
        "relation_candidate_flags_added": sorted(RELATION_CANDIDATE_IDS),
        "formal_relations_changed": False,
        "candidate_count_before": len(candidates) - 1,
        "candidate_count_after": len(candidates),
        "mention_count": len(mentions),
        "statement_count_before": statement_count_before,
        "statement_count_after": statement_count_after,
        "index_open_untyped_before": index_untyped_before,
        "index_open_untyped_after": index_untyped_after,
        "apply": args.apply,
    }

    if args.apply:
        backup_paths = [
            candidate_path.with_name(candidate_path.name + BACKUP_SUFFIX),
            mention_path.with_name(mention_path.name + BACKUP_SUFFIX),
            coverage_path.with_name(coverage_path.name + BACKUP_SUFFIX),
            statement_path.with_name(statement_path.name + BACKUP_SUFFIX),
        ]
        if any(path.exists() for path in backup_paths):
            raise SystemExit("a p.474 recovery backup already exists")
        for original, backup in zip(
            (candidate_path, mention_path, coverage_path, statement_path), backup_paths
        ):
            shutil.copy2(original, backup)
        write_csv(candidate_path, candidates, candidate_bom, candidate_eol)
        write_csv(mention_path, mentions, mention_bom, mention_eol)
        write_csv(coverage_path, coverage, coverage_bom, coverage_eol)
        write_jsonl(statement_path, rewritten_lines, statement_bom)
        summary["backups"] = [str(path.relative_to(ROOT)) for path in backup_paths]

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
