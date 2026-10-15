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
SEGMENT = "chp-7:07_CHP-7_sec_i:l11-19"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp7-seci-p170-l11-19-relation-classification-20261013"
EXPECTED = {
    STATEMENTS: "19155d52423bf195ff69c7d49f2a2dc4436c981d7e4efdee6563fdc3e6c4cdc9",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
}

TRUE_NOTES = {
    "st-chp7-p170-i01": "This records Crespi's reported travel, lodging, and per-space payment terms for the Prince of Liechtenstein's proposed palace decoration; the terms are not treated as accepted or fulfilled.",
    "st-chp7-p170-i04": "This records Haskell's claim that some foreign princes tried unsuccessfully to attract painters; the painter group and individual courts remain unnamed.",
    "st-chp7-p170-i05": "This records the stated relation between an unnamed group of painters and European court interest; it does not identify the painters or courts.",
    "st-chp7-p170-i06": "This preserves Haskell's time-bounded comparison of Rome's work opportunities with foreign rulers' competition against papal patronage; it does not identify particular rulers or painters.",
    "st-chp7-p170-i07": "This records Haskell's causal account linking declining papal patronage to painters' awareness of opportunities abroad; no destination or individual artist is inferred.",
    "st-chp7-p170-i09": "This records named rulers' spending on painting collections and their acquisition of works through agents or directly from artists; the collections and works are not individually identified.",
    "st-chp7-p170-i11": "This records the reception of works by Titian and Michelangelo in comparison with the earlier demand for Raphael's work; no individual works or buyers are named.",
    "st-chp7-p170-i13": "This records the source-described relation between artists from across Europe and Italy, where living masters' reputations and recently deceased masters' memory drew them.",
    "st-chp7-p170-i15": "This records Haskell's attribution of the embedded writing to Van Mander and the stated location, Amsterdam; the underlying text and date are not supplied here.",
    "st-chp7-p170-i16": "This records Van Mander's quoted report that Annibale Carracci was lodged by Cardinal Farnese; the Cardinal's forename and identity remain unresolved.",
    "st-chp7-p170-i17": "This records Van Mander's quoted attribution of works by Carracci to Cardinal Farnese; the works are not individually identified and the report is not independently checked.",
    "st-chp7-p170-i18": "This records the gallery's attribution to Carracci and the quoted report of unnamed observers' praise; neither the gallery's title nor building is identified.",
    "st-chp7-p170-i19": "This records Van Mander's quoted statement that Caravaggio was working in Rome; the accompanying praise is not tied to a named work.",
    "st-chp7-p170-i20": "This records Haskell's account that news from the North redirected patrons' attention toward Rome and Italy; the report and patrons remain unnamed.",
    "st-chp7-p170-i21": "This preserves Haskell's time-bounded account of occasional foreign commissions and the limited impact of foreign princes in Rome; no specific commission is inferred.",
    "st-chp7-p170-i22": "The continuation on p.171 identifies the previously unnamed power as the Spaniards and says their rulers competed with the popes for Italian artists' services; no individual ruler or commission is inferred.",
}

FALSE_NOTES = {
    "st-chp7-p170-i02": "This is Haskell's evaluative comparison of Crespi's success and other artists' ability to adopt an independent stance, without a specific relation between represented entities.",
    "st-chp7-p170-i03": "This is Haskell's general characterization of supply and demand, not a claim connecting specific artists, patrons, works, or institutions.",
    "st-chp7-p170-i08": "This is a broad historiographic claim about Italian art's predominance and European acceptance, not a discrete relation among identified actors or works.",
    "st-chp7-p170-i10": "This is Haskell's broad periodization and reception claim; the asserted general recognition is not assigned to a specific group or event.",
    "st-chp7-p170-i12": "This is an evaluative status claim about an unnamed group of modern painters, without a specific work, evaluator, or relation endpoint.",
    "st-chp7-p170-i14": "This is a figurative transition to the next discussion, not a claim about an identifiable entity or relation.",
}

OPEN_ENDPOINTS = {
    "st-chp7-p170-i01": "The surrounding passage identifies the recipient as the Prince of Liechtenstein, but the underlying personal identity is unresolved; the palace is not a separately identified commission or work.",
    "st-chp7-p170-i04": "The foreign-prince group is represented, but no painter or individual court targeted by the attempts is identified.",
    "st-chp7-p170-i05": "The painter group is represented; the European courts are not identified as a distinct candidate and no specific court or commission is named.",
    "st-chp7-p170-i06": "The sentence compares Rome, papal patronage, and foreign rulers' competition for artists, but names no individual ruler or painter and does not reduce the comparison to a single paired relation.",
    "st-chp7-p170-i07": "The painter group is represented, but the destinations and commissions abroad are unspecified.",
    "st-chp7-p170-i09": "François I, Charles V, and Philip II are examples; no collection or acquired painting is individually identified, and agents are not named.",
    "st-chp7-p170-i11": "Works by Titian and Michelangelo are the subject, but no individual works or seeking audience is identified; Raphael is only the comparison for prior reception.",
    "st-chp7-p170-i20": "The report, its route, and the patrons whose attention shifted are not identified; Rome and Italy remain the stated destinations of attention.",
    "st-chp7-p170-i21": "No specific foreign court, artist, or commission is identified; preserve only Haskell's stated period and contrast with Rome.",
    "st-chp7-p170-i22": "The p.171 continuation resolves the power as Spanish, but no individual ruler or member of the leading-artist group is named; the source quote for this row remains anchored at p.170 L19.",
}

ENDPOINT_FIXES = {
    # The terms continue the Prince of Liechtenstein proposal described on p.169.
    "st-chp7-p170-i01": (None, "cand-1405"),
    # Europe is the geographic location, not the court group whose interest painters failed to attract.
    "st-chp7-p170-i05": ("cand-3462", None),
    # The statement explicitly contrasts Spanish rulers with the popes for artists' services.
    "st-chp7-p170-i22": (None, "cand-4223"),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.170 body S2 relation candidates")
    parser.add_argument("--apply", action="store_true", help="write guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    if not (
        "[Page 170]" in source_lines[10]
        and "law of supply and demand" in source_lines[11]
        and "van Mander" in source_lines[15]
        and "the Spaniards commissioned important works" in source_lines[21]
    ):
        raise SystemExit("p.170 source and p.171 continuation guards failed")

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
    if unset != expected_targets or len(unset) != 22:
        raise SystemExit(f"p.170 target set changed: {sorted(unset ^ expected_targets)}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 11 or end > 19 or start > end:
            raise SystemExit(f"invalid p.170 source anchor: {sid} {start}-{end}")
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
