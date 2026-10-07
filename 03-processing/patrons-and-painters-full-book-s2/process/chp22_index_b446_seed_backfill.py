#!/usr/bin/env python3
"""Append four printed p.446 index rows omitted from B.csv without renumbering seeds."""

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
B_CSV = ROOT / "02-sources/03-Index/03-2-Index-CSV/B.csv"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
BACKUP_SUFFIX = ".bak-s2-chp22-p446-index-seed-backfill-20261007"

EXPECTED_HASHES = {
    "02-sources/01-book/CHP-22Index.pdf": "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    "02-sources/02-Markdown/22_CHP-22Index.md": "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081",
    "02-sources/03-Index/03-2-Index-CSV/B.csv": "cb75290976d362c68297faf41e30ff1f6fb019219968d14dc083d1117b216120",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "04-knowledge/tables/entity-candidates.csv": "2dc3ed0ddeee634c6484357e40141395b4c88890880291a63b41d421740e3593",
}

SUPPLEMENT = [
    {
        "candidate_id": "cand-11459",
        "index_entry_id": "B.csv#324",
        "canonical_name": "Bentveugels",
        "index_page_range": "20, 130",
        "suggested_type": "institution",
        "status": "open",
        "index_source_file": "B.csv",
        "sub_entry": "",
        "detail": (
            "Printed p.446 index headword for the colony of Dutch and Flemish artists in Rome. "
            "Chapter 1 uses Bentveughels and also names the Schildersbent; retain the index and body "
            "candidates separately for S3 identity review."
        ),
        "exclude_reason": "",
        "candidate_origin": "",
        "candidate_source_ref": "",
    },
    {
        "candidate_id": "cand-11460",
        "index_entry_id": "B.csv#325",
        "canonical_name": "Bergamo",
        "index_page_range": "215-21",
        "suggested_type": "place",
        "status": "open",
        "index_source_file": "B.csv",
        "sub_entry": "",
        "detail": (
            "Printed p.446 main heading names the city of Bergamo. Keep distinct from existing body-origin "
            "Bergamo candidates cand-6208, cand-7743, and cand-8574 until S3."
        ),
        "exclude_reason": "",
        "candidate_origin": "",
        "candidate_source_ref": "",
    },
    {
        "candidate_id": "cand-11461",
        "index_entry_id": "B.csv#326",
        "canonical_name": "Santa Maria Maggiore, Bergamo",
        "index_page_range": "215-23",
        "suggested_type": "place",
        "status": "open",
        "index_source_file": "B.csv",
        "sub_entry": "Santa Maria Maggiore",
        "detail": (
            "Printed p.446 Bergamo subentry names the basilica as a distinct architectural place, not the city. "
            "Keep separate from body-origin place candidate cand-7627 until S3."
        ),
        "exclude_reason": "",
        "candidate_origin": "",
        "candidate_source_ref": "",
    },
    {
        "candidate_id": "cand-11462",
        "index_entry_id": "B.csv#327",
        "canonical_name": "S. Paolo d'Argan, Bergamo",
        "index_page_range": "221n",
        "suggested_type": "place",
        "status": "open",
        "index_source_file": "B.csv",
        "sub_entry": "S. Paolo d'Argan",
        "detail": (
            "Printed p.446 Bergamo subentry names a distinct church/place. Preserve the printed index form; "
            "the exact building identity is not otherwise established here."
        ),
        "exclude_reason": "",
        "candidate_origin": "",
        "candidate_source_ref": "",
    },
]

CSV_ROWS = [
    {
        "Main Entry": "Bentveugels",
        "Location": "",
        "Sub-entry": "",
        "Detail": "",
        "Page Numbers": "20, 130",
    },
    {
        "Main Entry": "Bergamo",
        "Location": "",
        "Sub-entry": "",
        "Detail": "",
        "Page Numbers": "215-21",
    },
    {
        "Main Entry": "Bergamo",
        "Location": "",
        "Sub-entry": "Santa Maria Maggiore",
        "Detail": "",
        "Page Numbers": "215-23",
    },
    {
        "Main Entry": "Bergamo",
        "Location": "",
        "Sub-entry": "S. Paolo d'Argan",
        "Detail": "",
        "Page Numbers": "221n",
    },
]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_candidate_csv(path):
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    return raw.startswith(b"\xef\xbb\xbf"), "\r\n" if "\r\n" in text else "\n", list(
        csv.DictReader(io.StringIO(text, newline=""))
    )


def write_candidate_csv(path, rows, bom, line_ending):
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Write the guarded backfill; default is dry-run.")
    args = parser.parse_args()

    for relative, expected in EXPECTED_HASHES.items():
        path = ROOT / relative
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"preflight hash mismatch: {relative}")

    source_raw = B_CSV.read_bytes()
    if source_raw.startswith(b"\xef\xbb\xbf") or source_raw.count(b"\n") != 325:
        raise SystemExit("B.csv encoding or row boundary changed")
    source_text = source_raw.decode("cp1252")
    source_eol = "\r\n" if "\r\n" in source_text else "\n"
    with B_CSV.open("r", encoding="cp1252", newline="") as handle:
        source_rows = list(csv.DictReader(handle))
        fieldnames = list(csv.DictReader(B_CSV.open("r", encoding="cp1252", newline="")).fieldnames or [])
    if len(source_rows) != 324 or fieldnames != [
        "Main Entry", "Location", "Sub-entry", "Detail", "Page Numbers"
    ]:
        raise SystemExit("B.csv row count or header changed")
    text_folded = source_text.casefold()
    if any(token in text_folded for token in ("bentveugels", "bergamo", "santa maria maggiore", "s. paolo d")):
        raise SystemExit("one or more p.446 seed backfill rows already occur in B.csv")
    if not source_raw.endswith(source_eol.encode("ascii")):
        raise SystemExit("B.csv does not end at a complete row")

    bom, candidate_eol, candidates = read_candidate_csv(CANDIDATES)
    if len(candidates) != 11437:
        raise SystemExit("candidate count changed")
    if max(int(row["candidate_id"].split("-")[1]) for row in candidates) != 11458:
        raise SystemExit("candidate ID boundary changed")
    existing_ids = {row["candidate_id"] for row in candidates}
    existing_index_ids = {row["index_entry_id"] for row in candidates if row["index_entry_id"]}
    if existing_ids & {row["candidate_id"] for row in SUPPLEMENT}:
        raise SystemExit("one or more planned candidate IDs already exist")
    if existing_index_ids & {row["index_entry_id"] for row in SUPPLEMENT}:
        raise SystemExit("one or more planned B.csv row IDs already exist")
    if any(row["index_entry_id"] != f"B.csv#{324 + i}" for i, row in enumerate(SUPPLEMENT)):
        raise SystemExit("supplement row IDs are not aligned to the append boundary")

    candidate_rows_after = candidates + SUPPLEMENT
    planned_csv = io.StringIO(newline="")
    writer = csv.DictWriter(
        planned_csv, fieldnames=fieldnames, lineterminator=source_eol
    )
    writer.writerows(CSV_ROWS)
    supplement_bytes = planned_csv.getvalue().encode("cp1252")
    candidate_count_after = len(candidate_rows_after)
    source_row_count_after = len(source_rows) + len(CSV_ROWS)

    summary = {
        "source_physical_page": "CHP-22Index.pdf physical p.4 / printed p.446",
        "omitted_printed_rows": [
            "Bentveugels",
            "Bergamo",
            "Bergamo — Santa Maria Maggiore",
            "Bergamo — S. Paolo d'Argan",
        ],
        "B_csv_rows_before": len(source_rows),
        "B_csv_rows_appended": len(CSV_ROWS),
        "B_csv_rows_after": source_row_count_after,
        "candidate_rows_added": [
            {
                "candidate_id": row["candidate_id"],
                "index_entry_id": row["index_entry_id"],
                "canonical_name": row["canonical_name"],
                "type": row["suggested_type"],
                "sub_entry": row["sub_entry"],
            }
            for row in SUPPLEMENT
        ],
        "candidate_count_before": len(candidates),
        "candidate_count_after": candidate_count_after,
        "existing_index_ids_renumbered": False,
        "mentions_changed": False,
        "statements_changed": False,
        "apply": args.apply,
    }

    if args.apply:
        source_backup = B_CSV.with_name(B_CSV.name + BACKUP_SUFFIX)
        candidate_backup = CANDIDATES.with_name(CANDIDATES.name + BACKUP_SUFFIX)
        if source_backup.exists() or candidate_backup.exists():
            raise SystemExit("a p.446 recovery backup already exists")
        shutil.copy2(B_CSV, source_backup)
        shutil.copy2(CANDIDATES, candidate_backup)
        B_CSV.write_bytes(source_raw + supplement_bytes)
        write_candidate_csv(CANDIDATES, candidate_rows_after, bom, candidate_eol)
        summary["backups"] = [
            str(source_backup.relative_to(ROOT)),
            str(candidate_backup.relative_to(ROOT)),
        ]

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
