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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "06_CHP-6_sec_v.md"
SEGMENT = "chp-6:06_CHP-6_sec_v:l42-45"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp6-secv-p166-l42-45-relation-classification-20261013"

EXPECTED = {
    STATEMENTS: "1e13a1a48af430fc6cc7f600a48d2cd6722fe69963b7695cfb6b7e6fc057e0d8",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "724f421d1c98612a8820404c82dda956dadaf6006483fcdf394cc53af4e72d15",
}

TRUE_NOTES = {
    "st-chp6-p166-v1-01": "This records Crespi's reported sending of The Confession from Bologna to Ottoboni; the source's aesthetic praise remains attributed.",
    "st-chp6-p166-v1-02": "This records the work's use of a subject reportedly not painted since Poussin; preserve the distinction between subject matter and the scene's treatment.",
    "st-chp6-p166-v1-03": "This preserves Haskell's explicit comparison between Ottoboni and Cassiano dal Pozzo; the temperamental descriptions remain evaluative.",
    "st-chp6-p166-v1-04": "This records Ottoboni's reported response to The Confession.",
    "st-chp6-p166-v1-05": "This records Ottoboni's commission of Crespi's remaining six Sacraments after The Confession.",
    "st-chp6-p166-v1-07": "This records Crespi's continued residence in Bologna in comparison with Solimena's residence in Naples.",
    "st-chp6-p166-v1-08": "This records Solimena's continued residence in Naples in comparison with Crespi's residence in Bologna.",
    "st-chp6-p166-v1-09": "This records Solimena's reported sending of pictures to Ottoboni.",
    "st-chp6-p166-v1-10": "This records the reported difficulty faced by patrons in attracting their preferred artists to Rome; preserve 'increasingly' and 'if not impossible'.",
    "st-chp6-p166-v1-13": "This records Haskell's identification of European powers as a growing rival to Rome; it remains his historical interpretation.",
    "st-chp6-p166-v1-14": "This records Haskell's identification of other Italian towns as a growing rival to Rome; the towns are not named individually.",
}

FALSE_NOTES = {
    "st-chp6-p166-v1-06": "This is Haskell's evaluative judgment about the success of the six paintings, without a specific entity relation.",
    "st-chp6-p166-v1-11": "This is a broad causal interpretation of financial uncertainty's effects on patronage and artist availability, not a specific entity relation.",
    "st-chp6-p166-v1-12": "This is a broad causal interpretation of classical taste's effects on patronage, not a specific entity relation.",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.166 S2 statement relation candidates")
    parser.add_argument("--apply", action="store_true", help="write the guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    if "[Page 166]" not in source_lines[41] or "From Bologna" not in source_lines[42] or "European powers" not in source_lines[44]:
        raise SystemExit("p.166 source-line guard failed")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row["statement_id"]
        for row in rows
        if row.get("segment_id") == SEGMENT and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    expected_targets = set(TRUE_NOTES) | set(FALSE_NOTES)
    if unset != expected_targets or len(unset) != 14:
        raise SystemExit(f"p.166 target set changed: {sorted(unset ^ expected_targets)}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 42 or end > 45 or start > end:
            raise SystemExit(f"invalid p.166 source anchor: {sid} {start}-{end}")
        ids = [row.get("subject_candidate_id"), row.get("object_candidate_id")] + q.get("mentioned_candidate_ids", [])
        missing = sorted({cid for cid in ids if cid and cid not in candidate_ids})
        if missing:
            raise SystemExit(f"candidate endpoint missing for {sid}: {missing}")

    for sid, note in TRUE_NOTES.items():
        q = by_id[sid].setdefault("qualifiers", {})
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note
    for sid, note in FALSE_NOTES.items():
        q = by_id[sid].setdefault("qualifiers", {})
        q["relation_candidate"] = False
        q["relation_candidate_note"] = note

    output = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n"
    result = output.encode("utf-8")
    print(json.dumps({"mode": "apply" if args.apply else "dry_run", "segment": SEGMENT, "classified": len(unset), "relation_candidate_true": len(TRUE_NOTES), "relation_candidate_false": len(FALSE_NOTES), "unset_in_segment": 0, "before_sha256": digest(raw[STATEMENTS]), "after_sha256": digest(result)}, ensure_ascii=False))
    if not args.apply:
        return
    if BACKUP.exists():
        raise SystemExit(f"backup already exists; refusing to overwrite: {BACKUP.name}")
    shutil.copy2(STATEMENTS, BACKUP)
    atomic_write(STATEMENTS, result)
    print(f"backup={BACKUP.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
