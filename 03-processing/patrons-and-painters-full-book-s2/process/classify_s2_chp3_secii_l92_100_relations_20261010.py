from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
COVERAGE = ROOT / "04-knowledge/tables/s2-coverage.csv"
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/03_CHP-3_sec_ii.md"
PDF = ROOT / "02-sources/01-book/CHP-3.pdf"
SEGMENT = "chp-3:03_CHP-3_sec_ii:l92-100"
STATEMENT_ID = "st-chp3-secii-l92-100-p16-part-of"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp3-sec-ii-l92-100-relations-20261010")
HASHES = {
    TABLE: "6908b19b0df128907cbcc3b7fa7b89e2f1729fb23a158cb493ff0aee4c0d6f14",
    COVERAGE: "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "cb17a400fc5a79d895e31fe4a112c83e010f5e5b859883852b3985b7010eb1e6",
    PDF: "362e08518334ae5cda65cc1758f92ef4de6874b5982bfb6600187d889dc6785d",
}
NOTE = (
    "Plate 16 explicitly names the interior of S. Andrea al Quirinale. "
    "The interior space and church building are distinct place candidates; "
    "the caption supports the interior-to-building part_of relation."
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="apply the reviewed S2 classification")
    args = parser.parse_args()
    for path, expected in HASHES.items():
        require(digest(path) == expected, f"preflight hash changed for {path.relative_to(ROOT)}")
    require(not BACKUP.exists(), "recovery backup already exists; refusing to overwrite it")

    raw = TABLE.read_bytes()
    rows = read_jsonl(TABLE)
    require(len(rows) == 12748, "unexpected statement table row count")
    require(len({row["statement_id"] for row in rows}) == len(rows), "duplicate statement_id")
    by_id = {row["statement_id"]: row for row in rows}
    row = by_id.get(STATEMENT_ID)
    require(row is not None and row.get("segment_id") == SEGMENT, "target statement missing or moved")
    require((row.get("subject_candidate_id"), row.get("object_candidate_id"), row.get("predicate")) == ("cand-3928", "cand-3966", "part_of"), "target endpoints or predicate changed")
    require((row.get("qualifiers") or {}).get("relation_candidate") is None, "target statement already classified")

    segments = {x["segment_id"]: x for x in read_jsonl(SEGMENTS)}
    manifest = segments.get(SEGMENT)
    require(manifest is not None and (manifest.get("line_start"), manifest.get("line_end")) == (92, 100), "S0 segment range changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[91:100])
    require(source_text.endswith("lanirinO\n1n\naerdnA.SFo\nroiretni\n:\nïNIN\nïte\nB"), "S0 Plate 16 caption changed")

    with COVERAGE.open(encoding="utf-8-sig", newline="") as handle:
        coverage = list(csv.DictReader(handle))
    coverage_row = next((x for x in coverage if x["segment_id"] == SEGMENT), None)
    require(coverage_row is not None and (coverage_row["disposition"], coverage_row["migration_status"]) == ("reviewed", "complete"), "coverage is not complete")
    note = coverage_row.get("note", "")
    require(
        "physical p.14" in note
        and "Plate 16" in note
        and "printed text reads “Bernini: Interior of S. Andrea al Quirinale”" in note,
        "page-image comparison is not recorded in coverage",
    )

    candidates = {x["candidate_id"]: x for x in csv.DictReader(CANDIDATES.open(encoding="utf-8-sig", newline=""))}
    require(candidates.get("cand-3928", {}).get("suggested_type") == "place", "interior candidate type changed")
    require(candidates.get("cand-3966", {}).get("suggested_type") == "place", "church candidate type changed")

    q = dict(row.get("qualifiers") or {})
    q["relation_candidate"] = True
    q["relation_candidate_note"] = NOTE
    row["qualifiers"] = q
    true_after = sum(bool(x.get("subject_candidate_id") and x.get("object_candidate_id")) and (x.get("qualifiers") or {}).get("relation_candidate") is True for x in rows)
    false_after = sum(bool(x.get("subject_candidate_id") and x.get("object_candidate_id")) and (x.get("qualifiers") or {}).get("relation_candidate") is False for x in rows)
    pending_after = sum(bool(x.get("subject_candidate_id") and x.get("object_candidate_id")) and (x.get("qualifiers") or {}).get("relation_candidate") is None for x in rows)
    total_after = sum((x.get("qualifiers") or {}).get("relation_candidate") is True for x in rows)
    open_after = sum((x.get("qualifiers") or {}).get("relation_candidate") is True and not (x.get("subject_candidate_id") and x.get("object_candidate_id")) for x in rows)
    require((true_after, false_after, pending_after, total_after, open_after) == (4704, 473, 3359, 4753, 49), "unexpected projected relation totals")

    bom = raw.startswith(b"\xef\xbb\xbf")
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    encoded_rows = []
    for i, item in enumerate(rows):
        encoded = json.dumps(item, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if i == 0 and bom:
            encoded = b"\xef\xbb\xbf" + encoded
        encoded_rows.append(encoded + newline)
    payload = b"".join(encoded_rows)
    result = {
        "action": "apply" if args.apply else "dry-run",
        "segment_id": SEGMENT,
        "statement_id": STATEMENT_ID,
        "decision": "relation_candidate=true",
        "bilateral_after": {"relation_true": true_after, "relation_false": false_after, "unclassified": pending_after},
        "relation_candidates_total": total_after,
        "relation_candidates_open": open_after,
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
        written_by_id = {x["statement_id"]: x for x in written}
        require(len(written) == 12748 and (written_by_id[STATEMENT_ID].get("qualifiers") or {}).get("relation_candidate") is True, "post-write readback failed")
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
