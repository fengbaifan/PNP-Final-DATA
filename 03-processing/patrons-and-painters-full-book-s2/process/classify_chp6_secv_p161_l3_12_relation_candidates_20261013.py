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
SEGMENT = "chp-6:06_CHP-6_sec_v:l3-12"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp6-secv-p161-l3-12-relation-classification-20261013"

EXPECTED = {
    STATEMENTS: "7a67d35f302684bf606ca6e5f4d55f3ee1d07002ea27f7baa359b50b9561de18",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "724f421d1c98612a8820404c82dda956dadaf6006483fcdf394cc53af4e72d15",
}

TRUE_NOTES = {
    "st-chp6-p161-note2-avviso": "This records Haskell's bibliographic pointer to the 9 April 1672 avviso; the cited item is a locator, not independently checked evidence.",
    "st-chp6-p161-v1-01": "This records the temporal sequence between Alexander VII's death and the reported decline in official artistic patronage; it does not assert that the death caused the decline.",
    "st-chp6-p161-v1-02": "This records Giulio Rospigliosi's accession as Clement IX in 1667 and the reported two-year reign.",
    "st-chp6-p161-v1-03": "This records Clement IX's reported commission of a portrait from Carlo Maratta; the portrait remains unidentified.",
    "st-chp6-p161-v1-04": "This records Clement IX's reported commission of Bernini's sculptural figures for Ponte S. Angelo; the commission remains attributed to Haskell.",
    "st-chp6-p161-v1-06": "This records the Altieri family's concern that the palace might not be completed before Clement X's death.",
    "st-chp6-p161-v1-07": "This records the palace's location beside the Gesu and the Jesuits' reported indignation; these are distinct relations in one source-anchored statement.",
    "st-chp6-p161-v1-09": "This records the principal hall ceiling's readiness for the planned decorative programme by 1673.",
    "st-chp6-p161-v1-10": "This records Massimi's advice in Maratta's selection and Maratta's consultation with Bellori on iconography.",
    "st-chp6-p161-v1-11": "This records Haskell's explicit comparison of the Altieri fresco with Cortona's Barberini ceiling, preserving the evaluative attribution.",
    "st-chp6-p161-v1-12": "This records the fresco's depiction of Clemency and its visual reference to Clement X; the pun and golden-light description remain Haskell's account.",
    "st-chp6-p161-v1-13": "This records the fresco's reported enclosure within a carved stucco frame; the frame is not separately identified in the passage.",
    "st-chp6-p161-v1-14": "This records the allegorical relationship between Public Happiness, the standard, and Don Gasparo Altieri; the group of virtues remains unnamed.",
    "st-chp6-p161-v1-15": "This records Don Gasparo's reported adopted-nephew relationship to Clement X and his office as Gonfaloniere.",
    "st-chp6-p161-v1-17": "This preserves the explicit relation of the fresco's formal language to the Baroque while retaining Haskell's subjective assessment of its vitality.",
    "st-chp6-p161-v1-19": "This records the uncompleted palace decoration planned by Maratta and his pupils and Haskell's attribution of the failure to unspecified differences with Don Gasparo.",
    "st-chp6-p161-v1-21": "This records Clement X's effort to reduce nepotism and Haskell's qualified assessment of its success.",
    "st-chp6-p161-v1-22": "This preserves Haskell's comparison of Don Gasparo's luxury with the Barberini and Chigi families without turning the comparison into a quantified fact.",
}

FALSE_NOTES = {
    "st-chp6-p161-v1-05": "This is a biographical age-at-accession statement about Clement X, not a relation between identified entities.",
    "st-chp6-p161-v1-08": "This describes the construction activity's working conditions without a specific independent entity endpoint.",
    "st-chp6-p161-v1-16": "This is Haskell's broad evaluative judgment about the fresco's propagandistic effect, without a specific entity relation.",
    "st-chp6-p161-v1-18": "The referent of 'the work' is unresolved among the building, decoration, and fresco; this duration claim is not assigned as a specific entity relation.",
    "st-chp6-p161-v1-20": "This is Haskell's qualified inference that the unspecified differences were economic, not a specific entity relation.",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.161 section V relation candidates")
    parser.add_argument("--apply", action="store_true", help="write the guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    if "After the death of Pope Alexander VII" not in source_lines[2] or "9 April 1672" not in source_lines[11]:
        raise SystemExit("p.161 section V source guard failed")

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
    if unset != expected_targets or len(unset) != 23:
        raise SystemExit(f"p.161 section V target set changed: {sorted(unset ^ expected_targets)}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 3 or end > 12 or start > end:
            raise SystemExit(f"invalid p.161 section V source anchor: {sid} {start}-{end}")
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

    by_id["st-chp6-p161-v1-09"]["object_candidate_id"] = "cand-6467"
    by_id["st-chp6-p161-v1-13"]["qualifiers"]["open_endpoint_reason"] = (
        "The source identifies only a carved stucco frame, not a separately named or bounded frame entity."
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
