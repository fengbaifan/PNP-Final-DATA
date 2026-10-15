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
SEGMENT = "chp-7:07_CHP-7_sec_i:l45-59"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp7-seci-p174-l45-59-relation-classification-20261013"
EXPECTED = {
    STATEMENTS: "41aceee30301b4142eb3cb8529702097f9bf04064bf374152ea5fc2f42434dfa",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
}

TRUE_NOTES = {
    "st-chp7-p174-i01": "This records the source-stated niece relationship between Marie de Medici and Grand Duke Ferdinand; the duke's identity remains unresolved.",
    "st-chp7-p174-i02": "This records Marie de Medici's unnamed sister marrying Duke Vincenzo of Mantua; neither person's individual identity is supplied.",
    "st-chp7-p174-i03": "This preserves Haskell's claim that Marie used her family connections; the preceding sentence identifies separate Medici and Gonzaga connections, but no particular act is specified here.",
    "st-chp7-p174-i04": "This records Marie's arrival in Paris and her reported reaction to the Louvre; the wording is Haskell's narrative characterization, not securely a verbatim quotation from Marie.",
    "st-chp7-p174-i05": "This records Marie's temporary stay at the Gondi palace without inferring an exact duration.",
    "st-chp7-p174-i06": "This records the Gondi family's settlement in Paris about fifty years before the narrative; the interval remains approximate.",
    "st-chp7-p174-i08": "This records Haskell's causal account that Henri IV, struck by the fountain, summoned Pietro Francavilla to Paris; the summons does not itself establish a commission.",
    "st-chp7-p174-i09": "This records Pietro Francavilla as maker of the Fountain of Orpheus in the Gondi garden, as stated by Haskell.",
    "st-chp7-p174-i10": "This records Francesco Bordoni's arrival with Pietro Francavilla and his stated roles as assistant and future son-in-law.",
    "st-chp7-p174-i11": "This records Haskell's characterization of Marie's first important service to the arts in 1604; the particular commission is stated in the following row.",
    "st-chp7-p174-i12": "This records Marie persuading her uncle to commission a Henri IV equestrian statue from Giambologna; it preserves the source's attribution and does not claim immediate completion.",
    "st-chp7-p174-i13": "This records the intended placement of the Henri IV equestrian statue on the newly built Pont Neuf; the OCR spelling is corrected only in this S2 interpretation.",
    "st-chp7-p174-i14": "This records Marie's reported request to Ferdinand for the horse and effigy from his own monument; the request is distinct from the Henri IV statue and was not carried out.",
    "st-chp7-p174-i15": "This records that the specific request to Ferdinand was not granted; the source does not name a separate decision-maker.",
    "st-chp7-p174-i16": "This records Pietro Tacca as one of the two makers who completed the Henri IV equestrian monument.",
    "st-chp7-p174-i17": "This records Pietro Francavilla as the other named maker who completed the Henri IV equestrian monument with Pietro Tacca.",
    "st-chp7-p174-i18": "This records the source's relative delay before the Henri IV monument arrived; it gives neither an exact arrival year nor a confirmed recipient or destination.",
    "st-chp7-p174-i19": "This records Marie summoning Franz Pourbus the Younger to Paris after turning her attention toward Mantua; it does not claim Pourbus came from Mantua.",
    "st-chp7-p174-i20": "This records Pourbus's arrival in Paris in 1609, with the destination carried forward from the preceding summons.",
    "st-chp7-p174-i21": "This records Pourbus painting many portraits of Marie and her court; the individual portraits and court members remain unidentified.",
    "st-chp7-p174-i22": "This records Haskell's account of Marie's artistic interests while Henri IV lived, preserving the qualification that they were largely confined to the named crafts.",
    "st-chp7-p174-i23": "This preserves Haskell's causal and evaluative account linking Henri IV's assassination, Marie's increased ambition, and the worsening regency without turning it into an independently verified causal finding.",
    "st-chp7-p174-i24": "This records Marie's order to Salomon de Brosse to build the new palace on the site of the earlier palace she had bought; the seller's identity and the earlier building remain unresolved.",
    "st-chp7-p174-i25": "This records Marie's request to her unnamed aunt for Palazzo Pitti plans and her stated hope to use that palace as a model; receipt and adoption are not asserted.",
    "st-chp7-p174-i26": "This records Haskell's comparison between the realized Luxembourg Palace design and the Palazzo Pitti model Marie had hoped to follow.",
    "st-chp7-p174-i27": "This records the reported delay to the new palace project caused by unspecified internal problems in which Marie became involved; the problems are not identified.",
    "st-chp7-p174-i28": "This records Haskell's account that Marie was back in power by 1620 and intended to impress the world; the source does not name a formal office or a specific audience.",
    "st-chp7-p174-i29": "This records Haskell's claim that the spectacular commission was the means by which Marie impressed the world; the evaluation and exact cycle identity remain attributed and open.",
    "st-chp7-p174-i30": "This preserves Haskell's probable explanation that Rubens was selected because of his connections with the Mantuan court; the nature of those connections is unspecified.",
    "st-chp7-p174-i31": "This records Rubens being approached and asked to paint scenes in the two galleries; it does not claim he accepted or completed the commission.",
    "st-chp7-p174-i32": "This row includes Haskell's editorial transition and the discrete claim that Gentileschi entered Marie's service; the relation endpoint is Marie, not the Rubens cycle mentioned in the framing clause.",
    "st-chp7-p174-i33": "This records Gentileschi sending an unidentified picture ahead from Genoa and arriving in 1623; the sentence continues on p.175, which supplies the Paris stay context.",
}

FALSE_NOTES = {
    "st-chp7-p174-i07": "This is Haskell's evaluative statement that the Gondi palace garden was especially famous; it does not assert a discrete relation between represented entities.",
}

OPEN_ENDPOINTS = {
    "st-chp7-p174-i03": "The source refers to Marie using plural family connections, including distinct Medici and Gonzaga ties, but identifies no specific act or single endpoint in this sentence.",
    "st-chp7-p174-i11": "The source names service to the arts broadly; the specific 1604 commission is described in the following statement, so this row has no single object endpoint.",
    "st-chp7-p174-i18": "The source gives the monument's relative delay but does not specify its eventual recipient or destination in this sentence.",
    "st-chp7-p174-i27": "The palace delay is attributed to internal problems, but those problems are not identified as an entity or event.",
    "st-chp7-p174-i28": "The source names no formal office in which Marie returned to power and uses the generic audience 'the world'; neither can be mapped to a single endpoint.",
}

ENDPOINT_FIXES = {
    "st-chp7-p174-i15": (None, "cand-6668"),
    "st-chp7-p174-i32": ("cand-4733", "cand-1631"),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.174 body S2 relation candidates")
    parser.add_argument("--apply", action="store_true", help="write guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    required_source = (
        (44, "[Page 174]"),
        (45, "Gonzaga in Mantua"),
        (48, "The garden especially was famous"),
        (50, "She persuaded her uncle"),
        (54, "From Florence Marie then turned her attention to Mantua"),
        (56, "she grew more ambitious"),
        (58, "He arrived in 1623"),
    )
    if any(text not in source_lines[index] for index, text in required_source):
        raise SystemExit("p.174 source-line guards failed")

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
    if unset != expected_targets or len(unset) != 33:
        raise SystemExit(f"p.174 target set changed: {sorted(unset ^ expected_targets)}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 45 or end > 59 or start > end:
            raise SystemExit(f"invalid p.174 source anchor: {sid} {start}-{end}")
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
