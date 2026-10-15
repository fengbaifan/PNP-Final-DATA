from __future__ import annotations

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
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "07_CHP-7_intro.md"
SEGMENT = "chp-7:07_CHP-7_intro:l11-15"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp7-intro-p169-l11-15-relation-classification-20261013"
EXPECTED = {
    STATEMENTS: "ff2f8ad569f2103a8880d27f7a60009605273e8587dc4f9ab666d477fdb925b1",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "ac151af9ecb9904bb6e984d6f3c4ddb66cf2ab4f613f591246202086e177e30c",
}
TARGETS = {
    "st-chp7-p169-n1-cite": "This records the footnote's citation to De Rinaldis for Rosa's letter; locator only, not independent verification.",
    "st-chp7-p169-n3-cite": "This records the footnote's citation to Ruffo, p.289; locator only, not independent verification.",
    "st-chp7-p169-n4-albani": "This records the report that Albani could not serve Don Cesare promptly because he had to finish other paintings for patrons; the report's author and document remain unidentified.",
    "st-chp7-p169-n4-cite": "This records the footnote's citation to Gualandi for the Albani example; locator only, not independent verification.",
    "st-chp7-p169-n5-cite": "This records the footnote's citation to Miller for the Crespi letter; locator only, not independent verification.",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.169 intro-note S2 relation candidates")
    parser.add_argument("--apply", action="store_true", help="write the guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    if "Footnotes:" not in source_lines[10] or "case of Albani" not in source_lines[13] or "Miller" not in source_lines[14]:
        raise SystemExit("p.169 note source guard failed")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row["statement_id"]
        for row in rows
        if row.get("segment_id") == SEGMENT and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    if unset != set(TARGETS):
        raise SystemExit(f"p.169 target set changed: {sorted(unset ^ set(TARGETS))}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    if "cand-2962" not in candidate_ids:
        raise SystemExit("missing Haskell book candidate cand-2962")
    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 12 or end > 15 or start > end:
            raise SystemExit(f"invalid p.169 source anchor: {sid} {start}-{end}")
        ids = [row.get("subject_candidate_id"), row.get("object_candidate_id")] + q.get("mentioned_candidate_ids", [])
        missing = sorted({cid for cid in ids if cid and cid not in candidate_ids})
        if missing:
            raise SystemExit(f"candidate endpoint missing for {sid}: {missing}")

    for sid, note in TARGETS.items():
        row = by_id[sid]
        q = row.setdefault("qualifiers", {})
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note
        if row.get("predicate") == "footnote_citation":
            row["subject_candidate_id"] = "cand-2962"

    output = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n"
    result = output.encode("utf-8")
    print(json.dumps({"mode": "apply" if args.apply else "dry_run", "segment": SEGMENT, "classified": len(unset), "relation_candidate_true": len(TARGETS), "relation_candidate_false": 0, "unset_in_segment": 0, "before_sha256": digest(raw[STATEMENTS]), "after_sha256": digest(result)}, ensure_ascii=False))
    if not args.apply:
        return
    if BACKUP.exists():
        raise SystemExit(f"backup already exists; refusing to overwrite: {BACKUP.name}")
    shutil.copy2(STATEMENTS, BACKUP)
    atomic_write(STATEMENTS, result)
    print(f"backup={BACKUP.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
