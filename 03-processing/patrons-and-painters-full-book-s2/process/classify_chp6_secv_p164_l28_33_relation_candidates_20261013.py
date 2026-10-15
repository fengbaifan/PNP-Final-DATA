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
SEGMENT = "chp-6:06_CHP-6_sec_v:l28-33"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp6-secv-p164-l28-33-relation-classification-20261013"

EXPECTED = {
    STATEMENTS: "a6e89658aa78701731fc2f3f956b33630b952f6ca39805cdbc2ef9398b984fed",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "724f421d1c98612a8820404c82dda956dadaf6006483fcdf394cc53af4e72d15",
}

TRUE_NOTES = {
    "st-chp6-p164-note1-cicogna": "This records Haskell's bibliographic pointer to Cicogna for Ottoboni's political career; it is a locator, not independent verification.",
    "st-chp6-p164-v1-01": "This records Pietro Ottoboni's reported kinship with Pope Alexander VIII.",
    "st-chp6-p164-v1-02": "This records Ottoboni's reported appointment to the cardinalate in 1689; age 22 remains Haskell's statement.",
    "st-chp6-p164-v1-03": "This records Ottoboni's connection to Venetian nobility as stated by Haskell.",
    "st-chp6-p164-v1-04": "This records Ottoboni's temporary removal from the Libro d'Oro for accepting foreign-government stipends; the alleged motive remains attributed.",
    "st-chp6-p164-v1-04b": "This records the same reported Libro d'Oro sanction for Ottoboni's unnamed father; do not identify him from context.",
    "st-chp6-p164-v1-06": "This records Ottoboni's cardinal-nephew role and the source's description of its two-year duration and associated tastes.",
    "st-chp6-p164-v1-07": "This records Ottoboni's continued office as papal Vice-Chancellor under successive regimes until 1740.",
    "st-chp6-p164-v1-08": "This records Ottoboni's residence at the Cancelleria palace.",
    "st-chp6-p164-v1-09": "This records Haskell's characterization of the Cancelleria as a centre of Roman patronage; the praise remains evaluative.",
    "st-chp6-p164-v1-11": "This preserves Haskell's qualified comparison of Ottoboni with Francesco Barberini in cultivation and possible influence; 'perhaps' remains explicit.",
    "st-chp6-p164-v1-12": "This records Ottoboni's musical activity and authorship of operatic librettos; individual works are unnamed.",
    "st-chp6-p164-v1-13": "This records Ottoboni's fostering of a theatre; the theatre remains unidentified.",
    "st-chp6-p164-v1-14": "This records Filippo Juvarra's management of the scenery for Ottoboni's theatre.",
    "st-chp6-p164-v1-15": "This records Ottoboni's acquisition of pictures by leading Italian artists; no complete artist list is inferred.",
    "st-chp6-p164-v1-17": "This records Haskell's interpretation that Ottoboni revived an echo of Barberini glamour, while preserving the approximate half-century and the separate evaluation of permanence.",
    "st-chp6-p164-v1-20": "This records Ottoboni's patronage of Trevisani as Haskell's most enthusiastic example.",
    "st-chp6-p164-v1-21": "This records Trevisani's reported move from Venice to Rome around 1682.",
    "st-chp6-p164-v1-24": "This records the reported influence of Rome's classical ambience and Maratta on Trevisani; Haskell's characterization is retained.",
    "st-chp6-p164-v1-24b": "This records Trevisani's reported succession to Maratta as the leading Roman painter.",
    "st-chp6-p164-v1-25": "This records Haskell's claim that Ottoboni's circle affected most painters who worked for him; 'most' is preserved.",
}

FALSE_NOTES = {
    "st-chp6-p164-v1-01b": "This is a reign-duration attribute of Alexander VIII, not a specific entity relation.",
    "st-chp6-p164-v1-05": "This is a broad biographical characterization of Ottoboni's lifelong effort to raise money, without a specific identified source or transaction.",
    "st-chp6-p164-v1-10": "This is Haskell's account of his own narrative reluctance, not a historical entity relation.",
    "st-chp6-p164-v1-16": "This is a broad temporal characterization of Rome's creative climate during Ottoboni's life, without a specific entity relation.",
    "st-chp6-p164-v1-18": "This is Haskell's contrast between contemporary and modern assessments of Ottoboni, not a specific entity relation.",
    "st-chp6-p164-v1-19": "This is Haskell's editorial judgment about the scope of his study, not a historical entity relation.",
    "st-chp6-p164-v1-23": "This is Haskell's general aesthetic evaluation of an unnamed group of works, not a specific entity relation.",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.164 S2 statement relation candidates")
    parser.add_argument("--apply", action="store_true", help="write the guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    if "most adventurous" not in source_lines[25] or "Ottoboni was a Venetian" not in source_lines[30]:
        raise SystemExit("p.164 source-line guard failed")

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
    if unset != expected_targets or len(unset) != 28:
        raise SystemExit(f"p.164 target set changed: {sorted(unset ^ expected_targets)}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 29 or end > 33 or start > end:
            raise SystemExit(f"invalid p.164 source anchor: {sid} {start}-{end}")
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
    by_id["st-chp6-p164-v1-12"]["qualifiers"]["open_endpoint_reason"] = (
        "Ottoboni's operatic librettos are mentioned as an unnamed body of work; no individual titles are given."
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
