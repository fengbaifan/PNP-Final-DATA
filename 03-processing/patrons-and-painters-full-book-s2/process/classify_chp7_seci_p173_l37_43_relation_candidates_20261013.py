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
SEGMENT = "chp-7:07_CHP-7_sec_i:l37-43"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp7-seci-p173-l37-43-relation-classification-20261013"
EXPECTED = {
    STATEMENTS: "6ffdd9e82191e11bb0d1bf0a49e7257fe562460849c4f7e632b3705fe4800a72",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
}

TRUE_NOTES = {
    "st-chp7-p173-i01": "This records Haskell's report of Röthlisberger's identification of Crescenzi as meeting the commission's qualifications; it does not establish that Crescenzi actually placed the commission.",
    "st-chp7-p173-i02": "This records Crescenzi's stated membership in a noble Roman family alongside his birth year; the family relationship remains source-bounded.",
    "st-chp7-p173-i04": "This records Haskell's collective claim that Giovanni Battista Crescenzi was among the early patrons employing Claude; no exact date is supplied.",
    "st-chp7-p173-i05": "This records Haskell's collective claim that Pietro Paolo Crescenzi was among the early patrons employing Claude; it is kept separate from his brother's statement.",
    "st-chp7-p173-i06": "This records Claude's fresco work in the brothers' unidentified palace; the palace is the location endpoint and the frescoes remain a separate open work candidate.",
    "st-chp7-p173-i07": "This records Giovanni Battista Crescenzi's stated devotion to the Spanish cause; it does not convert the phrase into a formal institution.",
    "st-chp7-p173-i08": "This records Pietro Paolo Crescenzi's stated devotion to the Spanish cause; it remains separate from the statement about his brother.",
    "st-chp7-p173-i09": "This preserves the Venetian ambassador's nested, unverified suspicion concerning Crescenzi's Spanish service and his brother's papal ambition; it is an attributed allegation, not an established motive.",
    "st-chp7-p173-i10": "This records Haskell's response that Crescenzi practised architecture and contributed to building Buen Retiro; no specific work is identified.",
    "st-chp7-p173-i11": "This preserves Haskell's 'more than likely' either/or attribution of the landscape order to one Crescenzi brother; the responsible brother remains unresolved.",
    "st-chp7-p173-i12": "This records the landscape commission's placement in Italy; 'most important' remains Haskell's evaluative ranking, not independently verified comparison.",
    "st-chp7-p173-i13": "This records Haskell's assessment that the Buen Retiro commission was decisive for Claude; it does not imply a single work or independently measured career effect.",
    "st-chp7-p173-i14": "This records Claude's additional landscape paintings for the King of Spain, distinct from the hermit series; no titles or count are supplied.",
    "st-chp7-p173-i15": "This records Haskell's claim that the additional landscapes secured Claude's reputation as a leading practitioner; 'leading' remains the author's evaluation.",
    "st-chp7-p173-i16": "This records Poussin's one-or-possibly-two early landscape works; the count and titles remain unresolved as stated.",
    "st-chp7-p173-i18": "This records Haskell's comparative claim that France could rival Spain in seeking Italian artists' services; it does not identify a specific commission.",
    "st-chp7-p173-i19": "This records the French elite group's stated interest in Italian patronage and its variation with international politics; the group and time span remain broad as in the source.",
    "st-chp7-p173-i21": "This records Haskell's claim that Henry IV's architectural assertion of royal supremacy had decisive importance for Paris; the historical evaluation remains attributed.",
    "st-chp7-p173-i22": "This records the reported implementation of Henry IV's Paris programme by French architects and craftsmen, retaining 'almost entirely' and the author's scope.",
    "st-chp7-p173-i23": "This records Haskell's assessment of the architectural policy's success and its contrasting effect on painting; the stated provincial result remains the author's characterization.",
    "st-chp7-p173-i24": "This records Marie de Medici's guidance in the beginning of Italian influence in Paris; 'largely' does not make her the sole cause.",
    "st-chp7-p173-i27": "This records Marie de Medici's stated connections to the Medici and Gonzaga families and the kinship paths completed in the p.174 continuation; the family endpoints remain separate.",
}

FALSE_NOTES = {
    "st-chp7-p173-i03": "This states Pietro Paolo Crescenzi's cardinal rank, a biographical status without a separate entity relation or identified appointing institution in this passage.",
    "st-chp7-p173-i17": "This is Haskell's broad historical assessment of landscape painting's development; the source names no specific impulse-giving actor or event for a discrete relation.",
    "st-chp7-p173-i20": "This is Henry IV's rhetorical self-description in a quotation, not a claim about a specific represented work or entity relation; the following architectural programme is recorded separately.",
    "st-chp7-p173-i25": "This is an evaluative characterization attributed by Haskell to historians, not a relation between represented entities.",
    "st-chp7-p173-i26": "This is Haskell's evaluative judgment of Marie de Medici's taste, without a specific relation endpoint.",
}

OPEN_ENDPOINTS = {
    "st-chp7-p173-i11": "Either Giovanni Battista or Pietro Paolo Crescenzi may have ordered the series; both remain candidates and the source does not select one.",
    "st-chp7-p173-i18": "The source names a rival nation and a group of Italian artists; the current France candidate is geographic, so its political-entity alignment remains for S3.",
    "st-chp7-p173-i27": "The claim names two distinct families and several kinship paths; no single scalar object endpoint can represent both the Medici and Gonzaga connections.",
}

ENDPOINT_FIXES = {
    # The statement says Claude painted frescoes in the palace; the fresco work is a separate contextual mention.
    "st-chp7-p173-i06": ("cand-6659", "cand-6658"),
    # Henry IV's general boast does not identify the later Paris architectural programme.
    "st-chp7-p173-i20": ("cand-6661", None),
    # The claim has two family endpoints; do not leave only Medici as the object.
    "st-chp7-p173-i27": ("cand-5179", None),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.173 body S2 relation candidates")
    parser.add_argument("--apply", action="store_true", help="write guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    if not (
        "[Page 173]" in source_lines[36]
        and "Rothlisberger" in source_lines[37]
        and "Only one other nation" in source_lines[38]
        and "Historians are agreed" in source_lines[42]
    ):
        raise SystemExit("p.173 source-line guards failed")

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
    if unset != expected_targets or len(unset) != 27:
        raise SystemExit(f"p.173 target set changed: {sorted(unset ^ expected_targets)}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 37 or end > 43 or start > end:
            raise SystemExit(f"invalid p.173 source anchor: {sid} {start}-{end}")
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
