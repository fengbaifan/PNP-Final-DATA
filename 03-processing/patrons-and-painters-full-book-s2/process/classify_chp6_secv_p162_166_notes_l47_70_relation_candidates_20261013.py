from __future__ import annotations

import argparse
import copy
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
SEGMENT = "chp-6:06_CHP-6_sec_v:l47-70"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp6-secv-notes-l47-70-relation-classification-20261013"
SPLIT_ID = "st-chp6-p162-n1-loc-sacrifice-to-apollo"

EXPECTED = {
    STATEMENTS: "18768e44f5d6138944e7a6751dd29e56f019e7ca838e30f053e4aafc9af66e61",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "724f421d1c98612a8820404c82dda956dadaf6006483fcdf394cc53af4e72d15",
}

TRUE_NOTES = {
    "st-chp6-p162-n1-cite": "This records the footnote's citation to Rothlisberger for both Claude paintings; it is a bibliographic locator, not independent verification.",
    "st-chp6-p162-n1-loc": "This records the footnote's location claim for The Landing of Aeneas in Latium at Anglesey Abbey; the plural reference is split across the two named works.",
    "st-chp6-p162-n2-cite": "This records the footnote's citation to Barozzi e Berchet; locator only, not independent verification.",
    "st-chp6-p162-n3-cite": "This records the footnote's citation to Pastor; locator only, not independent verification.",
    "st-chp6-p162-n4-attack": "This records Haskell's claim that Bernini faced constant attack; the attacking group is not identified.",
    "st-chp6-p162-n4-cite": "This records the footnote's citations to the avviso and further Roma notices; locators only, not independent verification.",
    "st-chp6-p162-n5-cite": "This records the footnote's citation to Bellori 1942, p.107; locator only, not independent verification.",
    "st-chp6-p162-n6-cite": "This records the footnote's citation to Bellori 1942, p.108; locator only, not independent verification.",
    "st-chp6-p162-n7-cite": "This records the footnote's citation to Michaud and its nested reference to Servient; locator only, not independent verification.",
    "st-chp6-p162-n7-tomb": "This records Basadonna's tomb and bust at S. Marco in Palazzo Venezia; the location claim is attributed to Haskell.",
    "st-chp6-p163-n1-cite": "This records the footnote's citation to Michaud for the linked French report; locator only, not independent verification.",
    "st-chp6-p163-n2-cite": "This records the footnote's citation to Pascoli I; locator only, not independent verification.",
    "st-chp6-p163-n3-cite": "This records the footnote's citation to the 28 January 1679 avviso; locator only, not independent verification.",
    "st-chp6-p163-n4-cite": "This records the footnote's citation to the 18 February 1679 avviso; locator only, not independent verification.",
    "st-chp6-p163-n5-cite": "This records the footnote's citation to Pascoli II; locator only, not independent verification.",
    "st-chp6-p163-n6-cite": "This records the footnote's citation to Hantsch and Scherff; locator only, not independent verification.",
    "st-chp6-p164-n2-authors": "This records Haskell's claim that authors of the period wrote about Ottoboni's passion for art; the author group remains unnamed.",
    "st-chp6-p164-n2-cite": "This records the footnote's citation to the Ottoboni picture inventory; locator only, not independent verification.",
    "st-chp6-p164-n3-cite": "This records the footnote's citation to Rava on the Cancelleria theatre; locator only, not independent verification.",
    "st-chp6-p164-n4-cite": "This records the footnote's citation to Pascoli's unpublished Trevisani life; locator only, not independent verification.",
    "st-chp6-p164-n5-cite": "This records the footnote's citation to Waterhouse for the Trevisani portrait; locator only, not independent verification.",
    "st-chp6-p164-n5-portrait": "This records the reported location of Trevisani's portrait of Ottoboni at the Bowes Museum.",
    "st-chp6-p165-n1-cite": "This records the footnote's citation to Loret; locator only, not independent verification.",
    "st-chp6-p165-n2-cite": "This records the footnote's reference to V&A item DT.33.b; locator only, not independent verification.",
    "st-chp6-p165-n2-sketches": "This records the reported location of Juvarra's stage-design sketches at the Victoria and Albert Museum; the cited object reference is preserved.",
    "st-chp6-p165-n3-cite": "This records the footnote's citation to Cametti; locator only, not independent verification.",
    "st-chp6-p165-n3-europa": "This records the reported ownership by Corelli of a Europa painting attributed to Ricci; the work's identity remains unresolved.",
    "st-chp6-p165-n4-cite": "This records the footnote's citation to Mariette; locator only, not independent verification.",
    "st-chp6-p165-n5-cite": "This records the footnote's citation to Temanza's unpublished Zibaldone; locator only, not independent verification.",
    "st-chp6-p165-n6-cite": "This records the footnote's citation to Tassi; locator only, not independent verification.",
    "st-chp6-p166-n1-cite": "This records the footnote's citation to Crespi for the pictures' location; locator only, not independent verification.",
    "st-chp6-p166-n2-canal": "This records the footnote's citation to da Canal for Lazzarini's refusal; locator only, not independent verification.",
    "st-chp6-p166-n2-guidalotti": "This records the footnote's citation to Guidalotti Franchini for the Viani recruitment account; locator only, not independent verification.",
    "st-chp6-p166-n2-lazzarini": "This records the claim that Lazzarini refused to come to Rome despite pressure; the historical identity remains as indexed and is not independently verified.",
    "st-chp6-p166-n2-pallavicini": "This records Haskell's comparison of Pallavicini's munificence with Ottoboni's in the early eighteenth century.",
    "st-chp6-p166-n2-piola": "This records the reported failure of Pallavicini to retain Piola as his private painter.",
    "st-chp6-p166-n2-soprani": "This records the footnote's citation to Soprani II, p.186; locator only, not independent verification.",
    "st-chp6-p166-n2-viani": "This records the reported unsuccessful effort by d'Adda, supported by Gozzadini and Albani, to bring Viani to Rome.",
}

FALSE_NOTES = {
    "st-chp6-p163-n1-bias": "This is Haskell's source-reliability caveat about French hostility toward the Pope, not a historical entity relation; the caution remains attached to the report.",
    "st-chp6-p164-n2-inventory": "This is Haskell's assessment of the inventory as evidence for Ottoboni's passion for art, not a historical entity relation; the citation itself is recorded separately.",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.162-166 note-segment S2 relation candidates")
    parser.add_argument("--apply", action="store_true", help="write the guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    if "Footnotes:" not in source_lines[46] or "these two Claudes" not in source_lines[47] or "Adda" not in source_lines[69]:
        raise SystemExit("p.162-166 composite-note source guard failed")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")
    targets = {
        row["statement_id"]
        for row in rows
        if row.get("segment_id") == SEGMENT and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    expected_targets = set(TRUE_NOTES) | set(FALSE_NOTES)
    if targets != expected_targets or len(targets) != 40:
        raise SystemExit(f"p.162-166 composite-note target set changed: {sorted(targets ^ expected_targets)}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    required_candidates = {"cand-2962", "cand-0779", "cand-0783", "cand-6594"}
    if not required_candidates <= candidate_ids:
        raise SystemExit(f"required endpoint candidates missing: {sorted(required_candidates - candidate_ids)}")
    for sid in sorted(targets):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 48 or end > 70 or start > end:
            raise SystemExit(f"invalid composite-note source anchor: {sid} {start}-{end}")
        ids = [row.get("subject_candidate_id"), row.get("object_candidate_id")] + q.get("mentioned_candidate_ids", [])
        missing = sorted({cid for cid in ids if cid and cid not in candidate_ids})
        if missing:
            raise SystemExit(f"candidate endpoint missing for {sid}: {missing}")

    for sid, note in TRUE_NOTES.items():
        row = by_id[sid]
        q = row.setdefault("qualifiers", {})
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note
        if row.get("predicate") == "footnote_citation":
            row["subject_candidate_id"] = "cand-2962"
    for sid, note in FALSE_NOTES.items():
        q = by_id[sid].setdefault("qualifiers", {})
        q["relation_candidate"] = False
        q["relation_candidate_note"] = note

    by_id["st-chp6-p162-n4-attack"]["qualifiers"]["open_endpoint_reason"] = (
        "Haskell reports that Bernini was under attack but does not identify the attacking people or groups."
    )
    by_id["st-chp6-p164-n2-authors"]["qualifiers"]["open_endpoint_reason"] = (
        "The passage refers collectively to authors of the period without naming them individually."
    )

    loc = by_id["st-chp6-p162-n1-loc"]
    loc_q = loc["qualifiers"]
    if SPLIT_ID in by_id:
        raise SystemExit(f"split statement already exists: {SPLIT_ID}")
    loc["subject_candidate_id"] = "cand-0779"
    loc_q["claim"] = "Haskell says Claude's The Landing of Aeneas in Latium is among the two paintings now at Anglesey Abbey."
    loc_q["mentioned_candidate_ids"] = ["cand-0779", "cand-6594"]
    loc_q["linked_body_statement_ids"] = ["st-chp6-p162-v1-02"]
    loc_q["citation_body_statement_ids"] = ["st-chp6-p162-v1-02"]
    loc_copy = copy.deepcopy(loc)
    loc_copy["statement_id"] = SPLIT_ID
    loc_copy["subject_candidate_id"] = "cand-0783"
    loc_copy["qualifiers"]["claim"] = "Haskell says Claude's Sacrifice to Apollo is among the two paintings now at Anglesey Abbey."
    loc_copy["qualifiers"]["mentioned_candidate_ids"] = ["cand-0783", "cand-6594"]
    loc_copy["qualifiers"]["linked_body_statement_ids"] = ["st-chp6-p162-v1-02", "st-chp6-p162-v1-03"]
    loc_copy["qualifiers"]["citation_body_statement_ids"] = ["st-chp6-p162-v1-02", "st-chp6-p162-v1-03"]
    rows.append(loc_copy)
    by_id[SPLIT_ID] = loc_copy
    for sid in ("st-chp6-p162-n1-cite", "st-chp6-p162-n1-loc"):
        q = by_id[sid]["qualifiers"]
        q["linked_body_statement_ids"] = ["st-chp6-p162-v1-02", "st-chp6-p162-v1-03"]
        q["citation_body_statement_ids"] = ["st-chp6-p162-v1-02", "st-chp6-p162-v1-03"]

    output = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n"
    result = output.encode("utf-8")
    print(json.dumps({"mode": "apply" if args.apply else "dry_run", "segment": SEGMENT, "classified_existing": len(targets), "new_atomic_location_statement": SPLIT_ID, "relation_candidate_true": len(TRUE_NOTES) + 1, "relation_candidate_false": len(FALSE_NOTES), "unset_in_segment": 0, "before_sha256": digest(raw[STATEMENTS]), "after_sha256": digest(result)}, ensure_ascii=False))
    if not args.apply:
        return
    if BACKUP.exists():
        raise SystemExit(f"backup already exists; refusing to overwrite: {BACKUP.name}")
    shutil.copy2(STATEMENTS, BACKUP)
    atomic_write(STATEMENTS, result)
    print(f"backup={BACKUP.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
