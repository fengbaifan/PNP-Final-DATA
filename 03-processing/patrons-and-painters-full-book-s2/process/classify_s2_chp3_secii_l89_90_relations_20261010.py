from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
COVERAGE = ROOT / "04-knowledge/tables/s2-coverage.csv"
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/03_CHP-3_sec_ii.md"
PDF = ROOT / "02-sources/01-book/CHP-3.pdf"
SEGMENT = "chp-3:03_CHP-3_sec_ii:l89-90"
SOURCE_FILE = "02-sources/02-Markdown/03_CHP-3_sec_ii.md"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp3-sec-ii-l89-90-relations-20261010")

HASHES = {
    TABLE: "e6813143f3a55a28f5fbddb93433ada0b3394e337daa8fb5d9737c261f25ed9d",
    COVERAGE: "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    SOURCE: "cb17a400fc5a79d895e31fe4a112c83e010f5e5b859883852b3985b7010eb1e6",
    PDF: "362e08518334ae5cda65cc1758f92ef4de6874b5982bfb6600187d889dc6785d",
}

DECISIONS = {
    "st-chp3-secii-l89-90-p15-church-city": (
        "cand-3967", "cand-3126",
        "The Plate 15 caption explicitly identifies S. Ignazio as being in Rome; this is a place-to-city relation."
    ),
    "st-chp3-secii-l89-90-p15-fresco-location": (
        "cand-5074", "cand-3967",
        "The caption places the intended fresco on the vault of S. Ignazio; it does not say that the modello itself was located there."
    ),
    "st-chp3-secii-l89-90-p15-model-for": (
        "cand-4002", "cand-5074",
        "The caption explicitly identifies the modello as a model for a distinct fresco; keep the two works separate."
    ),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="apply the reviewed S2 relation classifications")
    args = parser.parse_args()
    for path, expected in HASHES.items():
        actual = digest(path)
        require(actual == expected, f"preflight hash changed for {path.relative_to(ROOT)}: {actual}")
    require(not BACKUP.exists(), "recovery backup already exists; refusing to overwrite it")

    raw = TABLE.read_bytes()
    rows = read_jsonl(TABLE)
    require(len(rows) == 12748, "unexpected statement table row count")
    require(len({row["statement_id"] for row in rows}) == len(rows), "duplicate statement_id before write")
    by_id = {row["statement_id"]: row for row in rows}
    target = [row for row in rows if row.get("segment_id") == SEGMENT]
    require(len(target) == 4, f"expected four Plate 15 statements, found {len(target)}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_manifest = {row["segment_id"]: row for row in read_jsonl(SEGMENTS)}.get(SEGMENT)
    require(segment_manifest is not None, "target segment missing from S0 manifest")
    require((segment_manifest.get("source_file"), segment_manifest.get("line_start"), segment_manifest.get("line_end")) == (SOURCE_FILE, 89, 90), "S0 segment range changed")
    segment_text = "\n".join(source_lines[88:90])
    normalized = lambda value: re.sub(r"\s+", " ", value).strip()
    require(normalized(segment_text).endswith("Andrea Pozzo: Modello for fresco on vault o£ S. Ignazio, Rome"), "source caption changed")
    with COVERAGE.open(encoding="utf-8-sig", newline="") as handle:
        import csv
        coverage = list(csv.DictReader(handle))
    coverage_row = next((row for row in coverage if row["segment_id"] == SEGMENT), None)
    require(coverage_row is not None and (coverage_row["disposition"], coverage_row["migration_status"]) == ("reviewed", "complete"), "target coverage is not complete")
    coverage_note = coverage_row.get("note", "")
    require(
        "PDF physical p.13 confirms Plate 15" in coverage_note
        and "o£" in coverage_note
        and "print reads “of”" in coverage_note,
        "existing page-image comparison is not recorded in the S2 coverage note",
    )

    for statement_id, (subject, obj, _) in DECISIONS.items():
        row = by_id.get(statement_id)
        require(row is not None and row.get("segment_id") == SEGMENT, f"target statement missing: {statement_id}")
        require((row.get("subject_candidate_id"), row.get("object_candidate_id")) == (subject, obj), f"endpoint changed: {statement_id}")
        q = row.get("qualifiers") or {}
        require(q.get("relation_candidate") is None, f"statement already classified: {statement_id}")
        require(normalized(row.get("original_quote", "")) in normalized(segment_text), f"quote no longer matches page-15 caption: {statement_id}")
    credit = by_id["st-chp3-secii-l89-90-p15-credit"]
    require((credit.get("qualifiers") or {}).get("relation_candidate") is True, "existing caption-credit classification changed")

    for statement_id, (_, _, note) in DECISIONS.items():
        row = by_id[statement_id]
        q = dict(row.get("qualifiers") or {})
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note
        if statement_id in {
            "st-chp3-secii-l89-90-p15-fresco-location",
            "st-chp3-secii-l89-90-p15-model-for",
        }:
            q["ocr_corrections"] = [{
                "source_file": SOURCE_FILE,
                "source_line": 90,
                "ocr": "o£",
                "print": "of",
                "basis": "CHP-3.pdf physical page 13 (Plate 15).",
            }]
        row["qualifiers"] = q

    true_bilateral = sum(bool(row.get("subject_candidate_id") and row.get("object_candidate_id")) and (row.get("qualifiers") or {}).get("relation_candidate") is True for row in rows)
    false_bilateral = sum(bool(row.get("subject_candidate_id") and row.get("object_candidate_id")) and (row.get("qualifiers") or {}).get("relation_candidate") is False for row in rows)
    pending_bilateral = sum(bool(row.get("subject_candidate_id") and row.get("object_candidate_id")) and (row.get("qualifiers") or {}).get("relation_candidate") is None for row in rows)
    total_relation = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in rows)
    open_relation = sum((row.get("qualifiers") or {}).get("relation_candidate") is True and not (row.get("subject_candidate_id") and row.get("object_candidate_id")) for row in rows)
    require((true_bilateral, false_bilateral, pending_bilateral, total_relation, open_relation) == (4703, 473, 3360, 4752, 49), "unexpected projected relation totals")

    bom = raw.startswith(b"\xef\xbb\xbf")
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    payload_lines = []
    for index, row in enumerate(rows):
        encoded = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if index == 0 and bom:
            encoded = b"\xef\xbb\xbf" + encoded
        payload_lines.append(encoded + newline)
    payload = b"".join(payload_lines)

    result = {
        "action": "apply" if args.apply else "dry-run",
        "segment_id": SEGMENT,
        "printed_page": 15,
        "pdf_physical_page": 13,
        "classified_statement_ids": list(DECISIONS),
        "bilateral_after": {"relation_true": true_bilateral, "relation_false": false_bilateral, "unclassified": pending_bilateral},
        "relation_candidates_total": total_relation,
        "relation_candidates_open": open_relation,
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not args.apply:
        print("Dry run only. Pass --apply to write.")
        return

    shutil.copy2(TABLE, BACKUP)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(dir=TABLE.parent, prefix=TABLE.name + ".s2tmp-", delete=False) as handle:
            handle.write(payload)
            temp_path = Path(handle.name)
        os.replace(temp_path, TABLE)
        written = read_jsonl(TABLE)
        written_by_id = {row["statement_id"]: row for row in written}
        require(len(written) == 12748 and all((written_by_id[sid].get("qualifiers") or {}).get("relation_candidate") is True for sid in DECISIONS), "post-write readback failed")
        require(digest(TABLE) == hashlib.sha256(payload).hexdigest(), "post-write SHA mismatch")
    except Exception:
        if temp_path and temp_path.exists():
            temp_path.unlink()
        shutil.copy2(BACKUP, TABLE)
        raise
    result["result"] = "applied"
    result["backup"] = str(BACKUP.relative_to(ROOT))
    result["sha256_after"] = digest(TABLE)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
