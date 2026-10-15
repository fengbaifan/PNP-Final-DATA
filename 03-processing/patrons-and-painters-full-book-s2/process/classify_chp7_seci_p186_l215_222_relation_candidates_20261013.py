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
SEGMENT = "chp-7:07_CHP-7_sec_i:l215-222"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp7-seci-p186-l215-222-relation-classification-20261013"
EXPECTED = {
    STATEMENTS: "5b0ada7d50eddba1a5d557ee6f5f138eeb1456aa691dd15249aba039abdaea02",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
}

TRUE_NOTES = {
    "st-chp7-p186-i01": "This records Brienne's account that the Scipio tapestry hung in Mazarin's small gallery and preserves its reported prior ownership; the full identity and physical version remain unresolved.",
    "st-chp7-p186-i02": "This records Brienne's attribution of the tapestry's design to Jules Romain, retained as Giulio Romano only as an index candidate and not as independent verification.",
    "st-chp7-p186-i03": "This records Mazarin's repeated words about leaving his pictures and his reported regret, preserving Brienne's quoted memoir layer.",
    "st-chp7-p186-i04": "This records Brienne's account of Mazarin pointing to and praising three pictures; the collection is an umbrella endpoint while individual works remain in mentions.",
    "st-chp7-p186-i05": "This preserves Haskell's rhetorical interpretation that Mazarin continued to promote Italian art after death through his will and church arrangements; it does not attribute posthumous agency to Mazarin himself.",
    "st-chp7-p186-i06": "This records Mazarin summoning a branch of the Theatine order to Paris in 1644 and its settlement by the Seine; the branch is not expanded into a specific house.",
    "st-chp7-p186-i07": "This records Haskell's account that Mazarin's will left a large but unspecified sum to the Theatines for rebuilding St Anne-la-Royale.",
    "st-chp7-p186-i08": "This records the will's direction that Mazarin's heart be buried at St Anne-la-Royale; the heart's object type remains unresolved.",
    "st-chp7-p186-i09": "This records the Theatines summoning Guarini, who arrived in 1662, for the church project; the stated date is his arrival.",
    "st-chp7-p186-i10": "This records Guarini beginning the church work, its interruption in 1669, and completion about fifty years later without converting the approximate duration into a date.",
    "st-chp7-p186-i11": "This records Haskell's account that the church facade derived from Borromini's S. Carlo alle Quattro Fontane; the OCR reading is corrected only in the claim.",
    "st-chp7-p186-i13": "This records Haskell's comparison that the architectural plan made no concession to current French practice; it is an attributed judgment, not a universal claim about French architects.",
    "st-chp7-p186-i14": "This records Haskell's description of the plan as an isolated example of Italian Baroque architecture in Paris during the Grand Siècle.",
    "st-chp7-p186-i15": "This preserves Haskell's tentative interpretation that the example may have deterred rather than encouraged similar experiments.",
    "st-chp7-p186-i16": "This records Haskell's statement that a reaction was underway but not yet visible; its scope remains limited to the architectural context of the preceding passage.",
    "st-chp7-p186-i17": "This records Haskell's account that Fouquet was arrested when Louis XIV took power; the sentence continues across the page boundary.",
    "st-chp7-p186-i18": "This records Colbert replacing Fouquet; it is a separate succession claim within a sentence that continues across the page boundary.",
    "st-chp7-p186-i19": "This records Haskell's claim that Fouquet had been employed by Mazarin; the source sentence continues at p.187.",
    "st-chp7-p186-i20": "This records Haskell's claim that Colbert had been employed by Mazarin; the source sentence continues at p.187.",
    "st-chp7-p186-q01": "This preserves the continuation and closure of Brienne's account of Mazarin's last visit, including their exchange and the pictures Mazarin named; it remains a quoted memoir, not independent verification.",
}

FALSE_NOTES = {
    "st-chp7-p186-i12": "This is Haskell's evaluative description of the vault's character, without a separate relation between represented entities.",
}

OPEN_ENDPOINTS = {
    "st-chp7-p186-i01": "The tapestry's physical version and the Marshal of Saint-André's full identity are not resolved by this passage.",
    "st-chp7-p186-i04": "The three named paintings are retained in mentions; their versions and the identity of Cortège remain unresolved.",
    "st-chp7-p186-i05": "The phrase 'from the grave' is Haskell's rhetorical attribution; the underlying will and rebuilding arrangement are the actual source-grounded actors.",
    "st-chp7-p186-i07": "The sum is not quantified; the Theatines are the recipients while the church is the stated purpose of the bequest.",
    "st-chp7-p186-i08": "The heart is recorded as a material remains object, but the current taxonomy has no settled type for it.",
    "st-chp7-p186-i12": "The vault's architectural terminology is not further specified; the statement is excluded from relational candidates as an attribute/evaluation.",
    "st-chp7-p186-i15": "The deterrent effect is Haskell's tentative interpretation and no specific later experiment is named.",
    "st-chp7-p186-i16": "The reaction's actors and exact target are not specified; the preceding architecture and French-practice contrast supply only its immediate context.",
    "st-chp7-p186-i17": "The arrest is temporally linked to Louis XIV taking power; no legal process or further causal explanation is supplied.",
    "st-chp7-p186-i19": "The employment statement continues to the next segment, where the sentence supplies additional context.",
    "st-chp7-p186-i20": "The employment statement continues to the next segment, where the sentence supplies additional context.",
    "st-chp7-p186-q01": "The excerpt includes several unnamed objects of Mazarin's farewell and remains attributed through Brienne as quoted by Haskell.",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.186 body S2 relation candidates")
    parser.add_argument("--apply", action="store_true", help="write guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    required_source = (
        (214, "[Page 186]"),
        (215, "à quelques jours de là dans les appartements neufs de son palais"),
        (217, "Voyez-vous, mon ami, ce beau tableau du Cortège"),
        (218, "yet even from the grave Mazarin was able to promote"),
        (220, "Both Fouquet, the unfortunate finance minister"),
        (221, "XIV took over power, and Colbert, who replaced him, had been employed by Mazarin"),
    )
    if any(text not in source_lines[index] for index, text in required_source):
        raise SystemExit("p.186 source-line guards failed")

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
    preclassified = expected_targets - unset
    allowed_preclassified = {"st-chp7-p186-i06", "st-chp7-p186-i07", "st-chp7-p186-i09"}
    if preclassified != allowed_preclassified or len(unset) != 18:
        raise SystemExit(f"p.186 target set changed: unset={sorted(unset)} preclassified={sorted(preclassified)}")
    if any((by_id[sid].get("qualifiers") or {}).get("relation_candidate") is not True for sid in preclassified):
        raise SystemExit("preclassified p.186 decisions changed; review before applying")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 216 or end > 222 or start > end:
            raise SystemExit(f"invalid p.186 source anchor: {sid} {start}-{end}")
        refs = [row.get("subject_candidate_id"), row.get("object_candidate_id")] + q.get("mentioned_candidate_ids", [])
        missing_refs = sorted({cid for cid in refs if cid and cid not in candidate_ids})
        if missing_refs:
            raise SystemExit(f"candidate reference missing for {sid}: {missing_refs}")

    quote_start = by_id["st-chp7-p185-i30"].get("qualifiers") or {}
    if quote_start.get("continuation_to_statement_id") != "st-chp7-p186-q01" or quote_start.get("continuation_status") != "closed":
        raise SystemExit("p.185 quote continuation link changed; review before applying")
    if by_id["st-chp7-p186-q01"].get("segment_id") != SEGMENT:
        raise SystemExit("p.186 quote target moved; review before applying")

    for sid, note in {**TRUE_NOTES, **FALSE_NOTES}.items():
        q = by_id[sid].setdefault("qualifiers", {})
        q["relation_candidate"] = sid in TRUE_NOTES
        q["relation_candidate_note"] = note
        if sid in OPEN_ENDPOINTS:
            q["open_endpoint_reason"] = OPEN_ENDPOINTS[sid]
    quote_start = by_id["st-chp7-p185-i30"].setdefault("qualifiers", {})
    quote_end = by_id["st-chp7-p186-q01"].setdefault("qualifiers", {})
    quote_end["continuation_of_statement_id"] = "st-chp7-p185-i30"
    quote_end["continuation_from_segment_id"] = "chp-7:07_CHP-7_sec_i:l205-213"
    quote_end["continuation_status"] = "closed"

    output = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n"
    result = output.encode("utf-8")
    print(json.dumps({
        "mode": "apply" if args.apply else "dry_run",
        "segment": SEGMENT,
        "classified": len(unset),
        "relation_candidate_true": len(TRUE_NOTES),
        "relation_candidate_false": len(FALSE_NOTES),
        "preclassified_preserved_and_documented": len(preclassified),
        "unset_in_segment": 0,
        "continuation_link": "st-chp7-p185-i30 -> st-chp7-p186-q01",
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
