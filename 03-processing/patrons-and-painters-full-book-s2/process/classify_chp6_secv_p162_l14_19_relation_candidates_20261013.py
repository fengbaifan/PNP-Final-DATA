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
SEGMENT = "chp-6:06_CHP-6_sec_v:l14-19"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp6-secv-p162-l14-19-relation-classification-20261013"

EXPECTED = {
    STATEMENTS: "84ac1182dccd35d187241d5a3e0cabfcf5a9fe1327f975425a1b4b05d468eb39",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "724f421d1c98612a8820404c82dda956dadaf6006483fcdf394cc53af4e72d15",
}

TRUE_NOTES = {
    "st-chp6-p162-v1-01": "This completes the p.161 comparison: Haskell compares Don Gasparo's luxury with the Barberini and Chigi families; no amount is inferred.",
    "st-chp6-p162-v1-02": "This records Don Gasparo's patronage relation to Claude's Landing of Aeneas and the reported placement beside the same artist's Sacrifice to Apollo.",
    "st-chp6-p162-v1-03": "This records the work's reported commission for the person called 'his father'; the father's identity remains unresolved.",
    "st-chp6-p162-v1-06": "This preserves the nested report from treasurers about their officials' debt collection; each speaker layer remains distinct.",
    "st-chp6-p162-v1-07": "This records the quoted causal account linking low prices, farmers' losses, and abandoned cultivation around Rome.",
    "st-chp6-p162-v1-08": "This records the quoted report linking Genoese grain sourcing from the Adriatic with unsold crops from the Roman shores; the three-year interval is relative.",
    "st-chp6-p162-v1-12": "This records Clement IX's proposed remodelling and burial scheme at S. Maria Maggiore, preserving the comparison with earlier papal tombs.",
    "st-chp6-p162-v1-13": "This records that Clement IX's plan was dropped after his death; no cause beyond the source's wording is added.",
    "st-chp6-p162-v1-14": "This records the family's reported fear that it would have to bear the expense of the plan.",
    "st-chp6-p162-v1-15": "This records the clergy's opposition to the threat that the plan posed to the church's mosaics.",
    "st-chp6-p162-v1-16": "This records the reported preparation by Roman municipal authorities of a resolution directed against Bernini; the allegation remains nested and attributed.",
    "st-chp6-p162-v1-17": "This records the proposed resolution's accusation that Bernini instigated papal spending; it remains an attributed allegation, not an established fact.",
    "st-chp6-p162-v1-18": "This records Innocent XI's succession to Clement X and the reported length of his reign.",
    "st-chp6-p162-v1-19": "This records the attributed account of Innocent XI's attention to the Ottoman advance toward Vienna and Hungary.",
    "st-chp6-p162-v1-20": "This records the reported absence of an opportunity for Maratta to be introduced to Innocent XI; the stated explanation remains attributed to Haskell.",
    "st-chp6-p162-v1-21": "This records Maratta's employment to retouch the identified Guido Reni painting of the Virgin at the Quirinal; the subject painting remains otherwise unidentified.",
    "st-chp6-p162-v1-23": "This records the reported discouragement of theatre and carnival and efforts to suppress indecency in art under Innocent XI.",
    "st-chp6-p162-v1-24": "This records the French envoy's conditional report about nude pictures in Cardinal Basadonna's bedroom; preserve 'if we are to believe' and the source attribution.",
    "st-chp6-p162-v1-25": "This records a distinct witness's quoted report about misery and hostility to the Roman government; the witness remains unnamed and the quotation continues on p.163.",
}

FALSE_NOTES = {
    "st-chp6-p162-v1-04": "This is Haskell's general assessment that Clement X had reason to economise, without a specific entity relation.",
    "st-chp6-p162-v1-05": "This is an attributed quotation about the general economic condition of the Papal States, not a relation between the ambassador and the polity; the speaker remains in the source attribution.",
    "st-chp6-p162-v1-09": "This is a broad reported description of regional liquidity and navigation, without a mapped relation between specific entity endpoints.",
    "st-chp6-p162-v1-10": "This is a general reported assessment of luxury's disadvantages in the regions, without a specific entity relation.",
    "st-chp6-p162-v1-11": "This is a broad historical account of opposition becoming vocal again, without a specific identified group-to-patronage relation.",
    "st-chp6-p162-v1-22": "This is Haskell's general characterization of the period as austere; the specific policy claims are recorded separately.",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.162 S2 statement relation candidates")
    parser.add_argument("--apply", action="store_true", help="write the guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    if "[Page 162]" not in source_lines[13] or "or a Chigi" not in source_lines[14] or "Cardinal" not in source_lines[17]:
        raise SystemExit("p.162 source-line guard failed")

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
    if unset != expected_targets or len(unset) != 25:
        raise SystemExit(f"p.162 target set changed: {sorted(unset ^ expected_targets)}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 14 or end > 19 or start > end:
            raise SystemExit(f"invalid p.162 source anchor: {sid} {start}-{end}")
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
