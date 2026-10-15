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
SEGMENT = "chp-6:06_CHP-6_sec_v:l21-26"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp6-secv-p163-l21-26-relation-classification-20261013"

EXPECTED = {
    STATEMENTS: "bcf566e9ef31d391f2ccb023ce5625500c6b12820625135e51908af2752196f8",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "724f421d1c98612a8820404c82dda956dadaf6006483fcdf394cc53af4e72d15",
}

TRUE_NOTES = {
    "st-chp6-p163-v1-03": "This records Innocent XI's refusal of the chapter's proposal for a third colonnade around St Peter's Square.",
    "st-chp6-p163-v1-04": "This records the King of Spain's reported funding of the Jesuits' proposed Gesu tribune decoration; the hoped-for project is not treated as completed.",
    "st-chp6-p163-v1-05": "This records the Jesuits' request to use the papal foundries for the proposed Gesu tribune project.",
    "st-chp6-p163-v1-06": "This records Innocent XI's reported refusal of the Jesuits' spending request; preserve the quoted wording and source attribution.",
    "st-chp6-p163-v1-07": "This records the unnamed chronicler's counterfactual estimate of the labour the proposed work could have supported; it is not an observed employment count.",
    "st-chp6-p163-v1-08": "This records Haskell's claim that Maratta's official commissions nearly disappeared during two successive papacies; the commissions are an unnamed group.",
    "st-chp6-p163-v1-09": "This records Haskell's causal account linking unemployment and critical dogmatism to painters' decision not to settle in Rome.",
    "st-chp6-p163-v1-10": "This records the reported effect of declining patronage on surviving patrons who wished to continue Barberini traditions; the patrons remain an unnamed group.",
    "st-chp6-p163-v1-16": "This records Clement XI's commissions from leading artists across Italy; individual works are not identified.",
    "st-chp6-p163-v1-17": "This preserves the attributed counterfactual that Clement XI would have commissioned more absent Charles II's death and European wars; it is not independently verified.",
    "st-chp6-p163-v1-18": "This records Haskell's account that other potentates, including the Schonborn family, paid most of the Lateran statues and paintings; payment is not attributed exclusively to that family.",
}

FALSE_NOTES = {
    "st-chp6-p163-v1-01": "This is Haskell's characterization of Innocent XI's personal interest in building, without a specific entity relation.",
    "st-chp6-p163-v1-02": "This is Haskell's characterization of Innocent XI's ambition for a memorial, not a relation between identified entities.",
    "st-chp6-p163-v1-11": "This is a broad corrective statement that building and decoration continued despite decline, without a specific work or actor relation.",
    "st-chp6-p163-v1-12": "This is Haskell's explanation of his own narrative emphasis, not a historical entity relation.",
    "st-chp6-p163-v1-13": "This is a broad historiographic description of the timing and growth of decline, without a specific entity-to-entity relation.",
    "st-chp6-p163-v1-14": "This is Haskell's broad comparative evaluation of outcomes despite decline, without a specific identified work relation.",
    "st-chp6-p163-v1-15": "This is a general claim about unnamed important figures and Roman art life; no specific contributor or relation is identified.",
    "st-chp6-p163-v1-19": "This is Haskell's interpretive framing of Ottoboni's career as characteristic of the period, not a specific entity relation.",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.163 S2 statement relation candidates")
    parser.add_argument("--apply", action="store_true", help="write the guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    if "[Page 163]" not in source_lines[20] or "important figures" not in source_lines[23] or "Clement XI" not in source_lines[23]:
        raise SystemExit("p.163 source-line guard failed")

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
    if unset != expected_targets or len(unset) != 19:
        raise SystemExit(f"p.163 target set changed: {sorted(unset ^ expected_targets)}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 21 or end > 26 or start > end:
            raise SystemExit(f"invalid p.163 source anchor: {sid} {start}-{end}")
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
    by_id["st-chp6-p163-v1-08"]["qualifiers"]["open_endpoint_reason"] = (
        "Haskell refers to Maratta's official commissions as an unnamed group; no individual commission is specified here."
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
