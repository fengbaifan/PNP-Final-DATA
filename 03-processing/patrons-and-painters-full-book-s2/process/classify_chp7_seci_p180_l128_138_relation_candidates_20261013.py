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
SEGMENT = "chp-7:07_CHP-7_sec_i:l128-138"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp7-seci-p180-l128-138-relation-classification-20261013"
EXPECTED = {
    STATEMENTS: "37db7e5937b4da972f53dbd59413affb891776242c37ecde3ecc74dd8aeaa6b8",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
}

TRUE_NOTES = {
    "st-chp7-p180-i01": "This records Haskell's link between postwar recovery and increased demand for Italian art, alongside the reported decline of English interest under the Puritans.",
    "st-chp7-p180-i02": "This preserves Haskell's interpretive connection between the comparative decline in artistic talent and Italian efforts to gain a place in the European balance of power.",
    "st-chp7-p180-i03": "This records Mazarin taking over the government of France after Richelieu's death in 1642; the political entity remains distinct from geographic France.",
    "st-chp7-p180-i04": "This records the source's approximate birth period and Abruzzi location for Mazarin; the village is unnamed and the date remains approximate.",
    "st-chp7-p180-i05": "This records Mazarin's Jesuit education in Rome; the city is retained as contextual location rather than the sole endpoint.",
    "st-chp7-p180-i06": "This records Mazarin entering the Colonna family's service and preserves the separate claim about his father's intendant role without conflating the two people.",
    "st-chp7-p180-i07": "This records Mazarin accompanying Girolamo Colonna to Spain; the travel destination is retained in the statement mentions.",
    "st-chp7-p180-i08": "This records Mazarin's captaincy in the Colonna regiment raised for the Valtellina campaign; the regiment and campaign remain source-bounded.",
    "st-chp7-p180-i09": "This records Mazarin's diplomatic ability attracting Giovanni Francesco Sacchetti's attention in Valtellina, as Haskell reports.",
    "st-chp7-p180-i10": "This records the stated brother relationship between Giovanni Francesco and Giulio Sacchetti.",
    "st-chp7-p180-i11": "This records the stated brother relationship between Giovanni Francesco and Marcello Sacchetti.",
    "st-chp7-p180-i12": "This records Mazarin becoming a protégé of the Sacchetti family; the source's description of the family as powerful remains attributed to Haskell.",
    "st-chp7-p180-i13": "This records Haskell's claim that Bentivoglio support strengthened Mazarin's position.",
    "st-chp7-p180-i14": "This preserves the source's claim that the Bentivoglio remained alert to new talent; no specific artists or recruitment acts are inferred.",
    "st-chp7-p180-i15": "This records Mazarin acting under Cardinal Antonio Barberini in the diplomatic context described on this page.",
    "st-chp7-p180-i16": "This records Cardinal Antonio Barberini's attempt to end the France-Spain war over the Mantua succession; the states and succession event retain their distinct political scopes.",
    "st-chp7-p180-i17": "This records Haskell's interpretation that Mazarin's diplomatic coup nearly fulfilled Urban VIII's hopes; it does not claim a direct appointment or an independently verified papal expectation.",
    "st-chp7-p180-i18": "This records Mazarin's return to Rome in 1632.",
    "st-chp7-p180-i19": "This records Haskell's characterization of Mazarin's social position in unnamed European circles; personality descriptions remain attributed, and Europe is not treated as the social group endpoint.",
    "st-chp7-p180-i20": "This records Haskell's claim that Mazarin was befriended by leading families; their identities are not supplied in this statement.",
    "st-chp7-p180-i21": "This records Mazarin choosing Leonora Baroni as his mistress; Haskell's characterization of Baroni's fame remains attributed.",
    "st-chp7-p180-i22": "This preserves Haskell's claim that Baroni's success inaugurated a tradition of operatic stardom; the tradition is recorded as a concept, not as a named institution.",
    "st-chp7-p180-i23": "This records Mazarin's association with the Barberini, Sacchetti and Bentivoglio families and Haskell's characterization of them as exceptional art patrons.",
    "st-chp7-p180-i24": "This records Haskell's claim that Mazarin acquired a lasting passion for collecting; no specific collection or acquired work is asserted.",
    "st-chp7-p180-i27": "This preserves Haskell's qualified report that the Bentivoglio apparently lent money to Mazarin; the loan remains unverified here.",
    "st-chp7-p180-i28": "This records Mazarin's appointment to a canonry associated with S. Giovanni in Laterano and the income Haskell says it provided; the church is contextual, not the canonry itself.",
    "st-chp7-p180-i29": "This preserves Haskell's report about Mazarin's use of his own and other people's money; the unnamed reports and owners remain unspecified.",
    "st-chp7-p180-i30": "This records Haskell's qualified claim that Poussin was the first artist from whom Mazarin seems to have commissioned paintings.",
    "st-chp7-p180-i31": "This preserves Haskell's interpretation that Poussin's nationality suited Mazarin's emerging political sympathies.",
    "st-chp7-p180-i32": "This records Haskell's qualified causal judgment that Poussin's then-limited fame made the price reasonable; no amount is supplied.",
    "st-chp7-p180-i33": "This records Poussin's access to the Barberini circle and the absence of official commissions described in this passage; no specific commission is inferred.",
    "st-chp7-p180-i34": "This records Haskell's possibility that Poussin painted two named works for Mazarin; 'may have' and the attribution remain uncertain.",
    "st-chp7-p180-i35": "This records Haskell's comparison of the two Poussin pictures with Giorgione's and young Titian's poesie and his claim that they owe much to both; the artistic-source works are not specifically identified.",
}

FALSE_NOTES = {
    "st-chp7-p180-i25": "This is Haskell's statement about uncertainty over how Mazarin expressed his collecting interest, not a distinct relation between entities.",
    "st-chp7-p180-i26": "This is a point-in-time biographical status claim about Mazarin's wealth, without a second entity endpoint.",
}

OPEN_ENDPOINTS = {
    "st-chp7-p180-i01": "The postwar recovery and English loss of interest are not represented as event or group candidates; the statement preserves the source's comparative relation to Italian art demand.",
    "st-chp7-p180-i02": "The source does not identify the people or works behind the comparative decline in talent, nor the particular Italian political actors seeking influence.",
    "st-chp7-p180-i06": "The father-intendant clause concerns a separate person and role; only Mazarin's service relationship is represented by the statement's scalar endpoints.",
    "st-chp7-p180-i14": "The source names no specific artists or recruitment actions covered by the Bentivoglio's general attention to new talent.",
    "st-chp7-p180-i19": "The social circles are unnamed; Europe marks the geographic scope, not a discrete membership group.",
    "st-chp7-p180-i20": "The families who befriended Mazarin are not identified in this sentence.",
    "st-chp7-p180-i23": "Three families are named in the claim, so no single scalar object endpoint captures all associations; the family mentions remain linked.",
    "st-chp7-p180-i24": "The source identifies an interest in collecting but no specific collection, work, or collecting activity as an endpoint.",
    "st-chp7-p180-i28": "The canonry is not separately identified as an entity candidate; S. Giovanni in Laterano is kept only as the named church context.",
    "st-chp7-p180-i29": "The reports and the people whose money Mazarin spent are unnamed; the source's broad characterization remains attributed and qualified.",
    "st-chp7-p180-i32": "The price, commission transaction, and amount are not specified; 'doubtless' marks Haskell's inference about affordability.",
    "st-chp7-p180-i33": "The Barberini circle has no resolved type or member list, and no particular official commission is identified.",
    "st-chp7-p180-i34": "The two named paintings are linked in mentions, while the source presents their commission for Mazarin as possible rather than certain.",
    "st-chp7-p180-i35": "The two Poussin works are named, but the particular Giorgione and young Titian poesie are not; the original person-to-person endpoints would misstate this stylistic comparison.",
}

ENDPOINT_FIXES = {
    "st-chp7-p180-i19": {"object": ("cand-3462", None)},
    "st-chp7-p180-i28": {"object": ("cand-6775", None)},
    "st-chp7-p180-i35": {
        "subject": ("cand-1984", None),
        "object": ("cand-1188", None),
    },
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.180 body S2 relation candidates")
    parser.add_argument("--apply", action="store_true", help="write guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    required_source = (
        (127, "[Page 180]"),
        (128, "thereafter recovery from the devastation of the Thirty Years War"),
        (128, "Whereas the period so far chronicled"),
        (129, "Cardinal Mazarin, who took over the government of France"),
        (131, "He accompanied Girolamo Colonna to Spain"),
        (133, "Giovanni Francesco Sacchetti, brother of Giulio and Marcello"),
        (135, "He was handsome, cunning and ambitious"),
        (135, "The families with whom he was especially associated"),
        (135, "not yet rich, though the Bentivoglio apparently lent him money"),
        (136, "Poussin may have painted for Mazarin two of his most beautiful pictures"),
    )
    if any(text not in source_lines[index] for index, text in required_source):
        raise SystemExit("p.180 source-line guards failed")

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
    if unset != expected_targets or len(unset) != 35:
        raise SystemExit(f"p.180 target set changed: {sorted(unset ^ expected_targets)}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 129 or end > 138 or start > end:
            raise SystemExit(f"invalid p.180 source anchor: {sid} {start}-{end}")
        refs = [row.get("subject_candidate_id"), row.get("object_candidate_id")] + q.get("mentioned_candidate_ids", [])
        missing_refs = sorted({cid for cid in refs if cid and cid not in candidate_ids})
        if missing_refs:
            raise SystemExit(f"candidate reference missing for {sid}: {missing_refs}")
    for sid, changes in ENDPOINT_FIXES.items():
        row = by_id[sid]
        for field, (old, new) in changes.items():
            if row.get(f"{field}_candidate_id") != old:
                raise SystemExit(f"unexpected {field} endpoint for {sid}; review before applying")
            if new and new not in candidate_ids:
                raise SystemExit(f"replacement candidate missing for {sid}: {new}")

    for sid, changes in ENDPOINT_FIXES.items():
        row = by_id[sid]
        for field, (_, new) in changes.items():
            row[f"{field}_candidate_id"] = new
    for mapping in (TRUE_NOTES, FALSE_NOTES):
        for sid, note in mapping.items():
            q = by_id[sid].setdefault("qualifiers", {})
            q["relation_candidate"] = sid in TRUE_NOTES
            q["relation_candidate_note"] = note
            if sid in OPEN_ENDPOINTS:
                q["open_endpoint_reason"] = OPEN_ENDPOINTS[sid]

    output = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n"
    result = output.encode("utf-8")
    print(json.dumps({
        "mode": "apply" if args.apply else "dry_run",
        "segment": SEGMENT,
        "classified": len(unset),
        "relation_candidate_true": len(TRUE_NOTES),
        "relation_candidate_false": len(FALSE_NOTES),
        "unset_in_segment": 0,
        "endpoint_corrections": [
            f"{sid} {field}_candidate_id {old!r} -> {new!r}"
            for sid, changes in ENDPOINT_FIXES.items()
            for field, (old, new) in changes.items()
            if old != new
        ],
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
