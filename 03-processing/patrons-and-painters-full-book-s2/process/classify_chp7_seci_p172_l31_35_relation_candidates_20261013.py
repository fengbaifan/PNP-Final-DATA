from __future__ import annotations

import csv
import argparse
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "07_CHP-7_sec_i.md"
SEGMENT = "chp-7:07_CHP-7_sec_i:l31-35"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp7-seci-p172-l31-35-relation-classification-20261013"
EXPECTED = {
    STATEMENTS: "fc1e7c5a7fc1723857ae1c40c0087b2c7d88c68dc639fedf7c40bf69e174854e",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
}

TARGETS = {
    "st-chp7-p172-i01": "This records Philip IV's stated continuing interest in Rome's art scene, retaining Haskell's relative time phrase and not converting it into a specific commission.",
    "st-chp7-p172-i02": "This records the unnamed ambassador's 1628 commission for Guido Reni's The Abduction of Helen; the ambassador remains unidentified.",
    "st-chp7-p172-i03": "This records the source's pendant relation between Guercino's The Death of Dido and The Abduction of Helen, with the three-year relative interval preserved.",
    "st-chp7-p172-i04": "This records the reported non-delivery of the two royal pictures to Madrid because of diplomatic confusion; the agent and actual destination are not supplied.",
    "st-chp7-p172-i05": "This records an unnamed royal agent's negotiation of an about-1636 commission for a series of more than a dozen landscapes with hermit or anchorite figures.",
    "st-chp7-p172-i06": "This records the landscape series' intended installation at Buen Retiro and preserves the distinction between the palace and the monastery site.",
    "st-chp7-p172-i07": "This records Haskell's explanation connecting the commission's subject choice to Philip IV's turn to Rome; it is the author's account of the King's reason.",
    "st-chp7-p172-i08": "This records Haskell's account of the landscape-and-figure type's creation in Venice, later neglect, and reappearance in Rome; the approximate chronology remains unchanged.",
    "st-chp7-p172-i09": "This records the claimed contributions to the picture type by Carracci and Domenichino and by Northern artists; the two directions of influence remain distinct.",
    "st-chp7-p172-i10": "This records Haskell's qualified claim that Northern artists held almost a monopoly of the landscape genre in the 1620s and 1630s.",
    "st-chp7-p172-i11": "This records the named and grouped artists' practice of the balanced landscape genre, preserving the uncertainty around Jan Both's prominence and Poussin's lesser role.",
    "st-chp7-p172-i12": "This records Philip IV's turn to the named and grouped landscape painters as they began to establish their reputations; the group is not collapsed into the genre itself.",
}

OPEN_ENDPOINTS = {
    "st-chp7-p172-i04": "The Abduction of Helen and The Death of Dido are separately represented works; no single work-group candidate or individual dispatch agent is identified.",
    "st-chp7-p172-i08": "The picture type is represented; Venice and Rome are separate location mentions for its origin and reappearance, not one scalar destination.",
    "st-chp7-p172-i09": "The statement includes two named artists as the initial influence and a separate Northern-artist group as contributors; these roles are not collapsed into one endpoint.",
    "st-chp7-p172-i11": "The genre is represented, but the source refers to several separate artists and an unnamed Flemish group rather than one unified artist endpoint.",
    "st-chp7-p172-i12": "Philip IV is represented, but the artists are several named people plus a source-defined group; no single collective candidate captures all of them.",
}

ENDPOINT_FIXES = {
    # The King turned to the artist group, not to the art-historical genre itself.
    "st-chp7-p172-i12": ("cand-6652", None),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.172 body S2 relation candidates")
    parser.add_argument("--apply", action="store_true", help="write guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    if not (
        "[Page 172]" in source_lines[30]
        and "In 1628 his ambassador commissioned" in source_lines[32]
        and "Abduction of Helen" in source_lines[32]
        and "Spainnow turned" in source_lines[34]
    ):
        raise SystemExit("p.172 source-line guards failed")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row["statement_id"]
        for row in rows
        if row.get("segment_id") == SEGMENT and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    if unset != set(TARGETS) or len(unset) != 12:
        raise SystemExit(f"p.172 target set changed: {sorted(unset ^ set(TARGETS))}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 31 or end > 35 or start > end:
            raise SystemExit(f"invalid p.172 source anchor: {sid} {start}-{end}")
        refs = [row.get("subject_candidate_id"), row.get("object_candidate_id")] + q.get("mentioned_candidate_ids", [])
        missing_refs = sorted({cid for cid in refs if cid and cid not in candidate_ids})
        if missing_refs:
            raise SystemExit(f"candidate reference missing for {sid}: {missing_refs}")
    for sid, (old_object, new_object) in ENDPOINT_FIXES.items():
        if by_id[sid].get("object_candidate_id") != old_object:
            raise SystemExit(f"unexpected object endpoint for {sid}; review before applying")
        if new_object and new_object not in candidate_ids:
            raise SystemExit(f"replacement candidate missing for {sid}: {new_object}")

    for sid, (_, new_object) in ENDPOINT_FIXES.items():
        by_id[sid]["object_candidate_id"] = new_object
    for sid, note in TARGETS.items():
        q = by_id[sid].setdefault("qualifiers", {})
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note
        if sid in OPEN_ENDPOINTS:
            q["open_endpoint_reason"] = OPEN_ENDPOINTS[sid]

    output = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n"
    result = output.encode("utf-8")
    print(json.dumps({
        "mode": "apply" if args.apply else "dry_run",
        "segment": SEGMENT,
        "classified": len(unset),
        "relation_candidate_true": len(TARGETS),
        "relation_candidate_false": 0,
        "unset_in_segment": 0,
        "endpoint_corrections": [f"{sid} object_candidate_id {old!r} -> {new!r}" for sid, (old, new) in ENDPOINT_FIXES.items()],
        "before_sha256": digest(raw[STATEMENTS]),
        "after_sha256": digest(result),
    }, ensure_ascii=True))
    if not args.apply:
        return
    if BACKUP.exists():
        raise SystemExit(f"backup already exists; refusing to overwrite: {BACKUP.name}")
    shutil.copy2(STATEMENTS, BACKUP)
    atomic_write(STATEMENTS, result)
    print(f"backup={BACKUP.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
