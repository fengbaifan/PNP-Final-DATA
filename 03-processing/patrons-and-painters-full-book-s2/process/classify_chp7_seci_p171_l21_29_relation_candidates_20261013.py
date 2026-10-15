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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "07_CHP-7_sec_i.md"
SEGMENT = "chp-7:07_CHP-7_sec_i:l21-29"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp7-seci-p171-l21-29-relation-classification-20261013"
EXPECTED = {
    STATEMENTS: "16d49ae4e72fce3707fb0488498611f07aec427ad489094a8be9d433356b2a07",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
}

TARGETS = {
    "st-chp7-p171-i01": "This completes the p.170 statement: Haskell identifies the power as Spanish and says it commissioned works from painters in the four cities. The city sequence remains source-bounded.",
    "st-chp7-p171-i02": "This records the stated concentration of Spanish commissioning activity in Naples; no individual official or commission is inferred.",
    "st-chp7-p171-i03": "This records the Spanish viceroys' governmental role in Naples and Haskell's characterization of its ceremonial and exploitative features; no individual viceroy is named.",
    "st-chp7-p171-i04": "This records Haskell's claim that the visual arts flourished in Naples under the described viceregal conditions; it remains the author's historical assessment.",
    "st-chp7-p171-i05": "This records Haskell's explicit attribution of a distinctive imprint on Neapolitan painting to Spanish cultural tendencies, with the quoted philosopher pictures as examples.",
    "st-chp7-p171-i06": "This records the reported employment of Ribera and his followers by the viceroys to decorate churches, palaces, and galleries; the specific commissions remain unnamed.",
    "st-chp7-p171-i07": "This records the viceroys' return to Spain with collections; neither individual viceroys nor collection contents are enumerated.",
    "st-chp7-p171-i08": "This records Haskell's stated practice of appointing former Rome ambassadors as viceroys; it does not identify the appointing authority or individuals.",
    "st-chp7-p171-i09": "This preserves Haskell's qualified causal claim that Rome ambassadorial service sometimes shaped a viceroy's later taste relative to his subjects.",
    "st-chp7-p171-i10": "This records Haskell's characterization of the Count of Monterey as a conspicuous Spanish patron in Italy during the first half of the century.",
    "st-chp7-p171-i11": "This records Haskell's attribution of Monterey's position to the influence of his brother-in-law, Count-Duke Olivarez; the author's personal description remains evaluative.",
    "st-chp7-p171-i12": "This records Monterey's welcome to Velasquez in Rome in 1630; the encounter is not expanded beyond the source.",
    "st-chp7-p171-i13": "This records Monterey's reported purchase of paintings attributed to Raphael, Titian, and other painters; the individual works and full group remain unidentified.",
    "st-chp7-p171-i14": "This records the claim that two important pictures among the purchased works were acquired for the unnamed King of Spain; the passive wording leaves the acquiring agent unspecified.",
    "st-chp7-p171-i15": "This records the reception of the two Titian paintings by Roman artists while the works were in Cardinal Aldobrandini's collection; the paintings remain separate work candidates.",
    "st-chp7-p171-i16": "This records the two Titian paintings passing into the possession of the Ludovisi family; the family's identity and the paintings' candidate records remain for S3 alignment.",
    "st-chp7-p171-i17": "This records Monterey's purchase of the Titian masterpieces from the Ludovisi family; the reaction attributed to all Italians remains Haskell's characterization.",
    "st-chp7-p171-i18": "This records Monterey's contact with contemporary painters and sculptors and his wish to continue employing them after transfer to Naples; contact is not treated as completed employment for every artist.",
    "st-chp7-p171-i19": "This records Haskell's collective account of Neapolitan artists defending a local commission monopoly through threats; no individual or incident is inferred.",
    "st-chp7-p171-i20": "This records Domenichino's reported arrival to paint cathedral frescoes and his appeal to the Viceroy for protection; the source does not name who compelled him.",
    "st-chp7-p171-i21": "This records Monterey's reported condition that Domenichino break his ecclesiastical contract and work for him in exchange for protection; it does not assert that the contract was broken.",
    "st-chp7-p171-i22": "This records Lanfranco's employment by Monterey alongside his work in the Naples Jesuit church; the specific church and frescoes remain unidentified.",
    "st-chp7-p171-i23": "This records Monterey's commissions from Lanfranco for palace pictures and distinct altarpieces for Augustinian buildings in Salamanca; the works and buildings remain unnamed.",
    "st-chp7-p171-i24": "This records Finelli's movement from Rome to work at Naples Cathedral; p.172 L301 closes the source sentence, without adding a claim about the later decoration dispute.",
}

OPEN_ENDPOINTS = {
    "st-chp7-p171-i13": "Monterey is named, but the purchased paintings form an unspecified group; artist mentions do not identify each acquired work.",
    "st-chp7-p171-i14": "The two pictures are identified by the continuation as the Titian pair, but the passive sentence does not name who acquired them for the unnamed King.",
    "st-chp7-p171-i15": "The two paintings are represented by separate work candidates; the source-defined Roman-artist group is the reception endpoint, and the collection remains contextual rather than being collapsed into Cardinal Aldobrandini.",
    "st-chp7-p171-i16": "The two Titian paintings remain separate work candidates; this statement preserves their collective transfer to the Ludovisi family without merging the works.",
}

ENDPOINT_FIXES = {
    # The source explicitly names the group of painters commissioned in all four cities.
    "st-chp7-p171-i01": (None, "cand-6623"),
    # The claim's recipient is the Roman-artist group, not Cardinal Aldobrandini; his collection remains a contextual mention.
    "st-chp7-p171-i15": ("cand-0033", "cand-6632"),
    # The composite source segment closes Finelli's sentence with "Cathedral", represented by the existing Naples Cathedral candidate.
    "st-chp7-p171-i24": (None, "cand-3117"),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.171 body S2 relation candidates")
    parser.add_argument("--apply", action="store_true", help="write guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    if not (
        "[Page 171]" in source_lines[20]
        and "the Spaniards commissioned important works" in source_lines[21]
        and "Bacchanal and Worship of Venus" in source_lines[24]
        and "came from Rome to work in the" in source_lines[28]
        and "Cathedral he too was at once taken up by the Viceroy" in source_lines[300]
    ):
        raise SystemExit("p.171 source and p.172 continuation guards failed")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row["statement_id"]
        for row in rows
        if row.get("segment_id") == SEGMENT and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    if unset != set(TARGETS) or len(unset) != 24:
        raise SystemExit(f"p.171 target set changed: {sorted(unset ^ set(TARGETS))}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 21 or end > 29 or start > end:
            raise SystemExit(f"invalid p.171 source anchor: {sid} {start}-{end}")
        refs = [row.get("subject_candidate_id"), row.get("object_candidate_id")] + q.get("mentioned_candidate_ids", [])
        missing_refs = sorted({cid for cid in refs if cid and cid not in candidate_ids})
        if missing_refs:
            raise SystemExit(f"candidate reference missing for {sid}: {missing_refs}")
    for sid, (old_object, new_object) in ENDPOINT_FIXES.items():
        if by_id[sid].get("object_candidate_id") != old_object:
            raise SystemExit(f"unexpected object endpoint for {sid}; review before applying")
        if new_object not in candidate_ids:
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
