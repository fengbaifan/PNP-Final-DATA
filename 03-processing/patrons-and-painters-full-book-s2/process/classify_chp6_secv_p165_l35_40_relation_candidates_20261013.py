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
SEGMENT = "chp-6:06_CHP-6_sec_v:l35-40"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp6-secv-p165-l35-40-relation-classification-20261013"

EXPECTED = {
    STATEMENTS: "146905bd19c1468a3db686cb74a0a48252c4e58eb7b4dfd0422efbe344df3881",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "724f421d1c98612a8820404c82dda956dadaf6006483fcdf394cc53af4e72d15",
}

TRUE_NOTES = {
    "st-chp6-p165-v1-02": "This records Conca's reported move to Rome around 1706; the date remains approximate.",
    "st-chp6-p165-v1-04": "This records Conca being taken up by Ottoboni and his friends; no specific commission is inferred.",
    "st-chp6-p165-v1-05": "This records Gaulli's reported position as another of Ottoboni's favourites.",
    "st-chp6-p165-v1-07": "This records the reported influence of Fontana's academic Baroque on Juvarra's architectural style, with the 1704-1714 interval preserved.",
    "st-chp6-p165-v1-08": "This records Juvarra's exceptional work while working for Ottoboni; the source attributes the work's quality to Haskell's assessment.",
    "st-chp6-p165-v1-09": "This records the scope of Juvarra's work for Ottoboni as stage sets for the Cancelleria theatre.",
    "st-chp6-p165-v1-10": "This records Haskell's interpretation of Ottoboni's influence on the arts through a source-defined style; the aesthetic characterization remains attributed.",
    "st-chp6-p165-v1-11": "This records the reported transmission and reception of the style across masters, pupils, courts, princes, and the public; no individual members are inferred.",
    "st-chp6-p165-v1-12": "This records Haskell's comparison of the style with Baroque, French rococo, and later eighteenth-century painting; the evaluative language remains attributed.",
    "st-chp6-p165-v1-13": "This records the style's reported condemnation with the arrival of neo-classicism and its limited later reception.",
    "st-chp6-p165-v1-14": "This records Haskell's account of Ottoboni's effect on artists in close contact with him and his circle.",
    "st-chp6-p165-v1-15": "This records Ottoboni's failure to attract painters who worked for him to settle in Rome.",
    "st-chp6-p165-v1-16": "This records the relation between the painters Ottoboni could not attract and the emerging Italian painting revival; the broader group remains source-defined.",
    "st-chp6-p165-v1-17": "This records Haskell's characterization of the revival as opposed to values fostered by Rome; preserve the author's interpretive framing.",
    "st-chp6-p165-v1-18": "This records Haskell's placement of Ricci's case within the source-defined group of painters not attracted to Rome.",
    "st-chp6-p165-v1-19": "This records the approximate temporal relation between Ricci's arrival in Rome and Ottoboni's rise to power; no exact year is inferred.",
    "st-chp6-p165-v1-20": "This records Ricci's reported work for Ottoboni and his friends; 'naturally' remains Haskell's wording.",
    "st-chp6-p165-v1-21": "This preserves Mariette's explicitly hearsay account of Ricci's response to Raphael's frescoes and desire to return to Venice.",
    "st-chp6-p165-v1-23": "This records Diziani's arrival in Rome and Ottoboni's immediate patronage more than thirty years after Ricci's arrival.",
    "st-chp6-p165-v1-24": "This records Diziani's stage set for the Forty Hours ceremony in Ottoboni's titular church; the work is not generalized beyond the source.",
    "st-chp6-p165-v1-25": "This records Haskell's contrast between Fra Galgario's association with Venice and residence in Bergamo.",
    "st-chp6-p165-v1-26": "This records Fra Galgario's refusal of Ottoboni's call to Rome.",
}

FALSE_NOTES = {
    "st-chp6-p165-v1-03": "This is Haskell's evaluative account of Conca's changing artistic quality, without a specific entity relation.",
    "st-chp6-p165-v1-06": "This is Haskell's evaluative characterization of Gaulli's later style, without a specific entity relation.",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.165 S2 statement relation candidates")
    parser.add_argument("--apply", action="store_true", help="write the guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    if "[Page 165]" not in source_lines[34] or "Conca" not in source_lines[35] or "Fra Galgario" not in source_lines[39]:
        raise SystemExit("p.165 source-line guard failed")

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
    if unset != expected_targets or len(unset) != 24:
        raise SystemExit(f"p.165 target set changed: {sorted(unset ^ expected_targets)}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 35 or end > 40 or start > end:
            raise SystemExit(f"invalid p.165 source anchor: {sid} {start}-{end}")
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
    by_id["st-chp6-p165-v1-11"]["qualifiers"]["open_endpoint_reason"] = (
        "The passage describes transmission among masters, pupils, courts, princes, and the public as broad groups without naming individual members."
    )
    by_id["st-chp6-p165-v1-12"]["qualifiers"]["open_endpoint_reason"] = (
        "The comparison names artistic movements and periods but does not identify individual works as the compared objects."
    )

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
