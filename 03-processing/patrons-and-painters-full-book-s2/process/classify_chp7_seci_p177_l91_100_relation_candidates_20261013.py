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
SEGMENT = "chp-7:07_CHP-7_sec_i:l91-100"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp7-seci-p177-l91-100-relation-classification-20261013"
EXPECTED = {
    STATEMENTS: "79067e87421d161d3683b6d7fa2ec1583bcef9890321aa1c64f72c2ec6d2ea9b",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
}

TRUE_NOTES = {
    "st-chp7-p177-i01": "This preserves Haskell's report of Urban VIII's statement to Bernini and his account that it helped detain the artist in Rome.",
    "st-chp7-p177-i02": "This records Haskell's claim that Urban VIII retained authority over Bernini even while near death; it completes the p.176 continuation.",
    "st-chp7-p177-i03": "This records Haskell's account linking Bernini's continued presence to Urban VIII's patronage and the later difficulties after the patron's death.",
    "st-chp7-p177-i04": "This records Haskell's comparison between the efforts of unnamed European nations and the attractions of the Barberini regime; the nations are not inferred from the preceding French example.",
    "st-chp7-p177-i05": "This records English patronage efforts to dislodge leading Italian artists and Haskell's comparison of their results with the preceding European efforts.",
    "st-chp7-p177-i06": "This records Haskell's characterization of Arundel, Charles I and unnamed courtiers as sharing a strong interest in art; the collective subject remains broader than the Arundel endpoint.",
    "st-chp7-p177-i07": "This records Charles I's purchase of the Duke of Mantua's picture collection; the Duke's identity and the individual works remain unresolved.",
    "st-chp7-p177-i08": "This records Haskell's claim that the purchase had repercussions for unnamed European rulers; neither the rulers nor the effects are specified.",
    "st-chp7-p177-i09": "This preserves Naudé's reported expectation that some pictures might go to Arundel and his quoted characterization of Arundel's pursuit of Italian works; it does not establish transfer.",
    "st-chp7-p177-i10": "This records Haskell's account of Charles I and his agents repeatedly failing to secure Italian artists' patronage and travel to England; failure does not mean no Italian artist ever worked for Charles.",
    "st-chp7-p177-i11": "This records Charles I employing Rubens; Haskell's satisfaction with the employment remains an attributed evaluation.",
    "st-chp7-p177-i12": "This records Charles I employing Van Dyck; Haskell's satisfaction with the employment remains an attributed evaluation.",
    "st-chp7-p177-i14": "This records Charles I and his ministers consciously trying to reduce the isolation between England and Rome; no particular diplomatic act is named.",
    "st-chp7-p177-i15": "This records the religious affiliation of Charles I's unnamed wife and many unnamed courtiers; Charles is retained only as their contextual relation, not as the subject of the status claim.",
    "st-chp7-p177-i18": "This records English travelers' ability to visit Rome without fear of the Inquisition and their reported welcome by an unidentified Cardinal Barberini; the two identities remain open.",
    "st-chp7-p177-i19": "This records diplomatic exchanges encouraged between England and Rome in the context of reciprocal gestures; the participants and exchanges are unspecified.",
    "st-chp7-p177-i20": "This records Haskell's association between political relaxation and growing English respect for contemporary Italian culture; the sentence does not identify a single cause.",
    "st-chp7-p177-i21": "This records Haskell's claim that Catholic humanism appealed to people repelled by the preceding half-century's intransigence; the audience is unnamed.",
    "st-chp7-p177-i22": "This records Haskell's account that connoisseurship promoted distinction between aesthetic merit and representational content; it does not say representation became irrelevant.",
    "st-chp7-p177-i23": "This records Haskell's claim that the described sophistication characterized a small privileged elite; the people are not identified.",
    "st-chp7-p177-i24": "This records the relationship Haskell draws between growing Puritan objection to the court and the increasing difficulty of maintaining the described sophistication.",
    "st-chp7-p177-i25": "This records the dated breakdown of the England-Rome political and religious balance in 1642, as described by Haskell.",
    "st-chp7-p177-i26": "This preserves Haskell's interpretive claim that the continuing tensions should inform an assessment of Charles I's artistic policy; the tensions' specific components remain contextual.",
    "st-chp7-p177-i27": "This records Charles I's offer of favorable terms to Guercino after seeing the Semiramis picture; the offer's condition continues on p.178 and Haskell's causal link remains qualified by the cited contrary interpretation.",
}

FALSE_NOTES = {
    "st-chp7-p177-i13": "This is an unspecified inference about Charles I's perspective on the preceding matter, without stating the alternative view or a discrete relationship endpoint.",
    "st-chp7-p177-i16": "This is a broad frequency statement about unnamed conversions with no identified entities or specific relation endpoint.",
    "st-chp7-p177-i17": "This is a broad status statement about unnamed penal laws and their enforcement, without a named law, enforcing body or discrete candidate relation in this passage.",
}

OPEN_ENDPOINTS = {
    "st-chp7-p177-i04": "The source refers to unnamed European nations as the competing party; it does not identify which nations.",
    "st-chp7-p177-i06": "The source groups Arundel, Charles I and unnamed courtiers together; no single scalar person endpoint represents the full subject group or the general object of their love.",
    "st-chp7-p177-i08": "The source does not name the European rulers or specify the repercussions of the collection purchase.",
    "st-chp7-p177-i10": "The claim includes Charles I and unnamed agents; Charles is not treated as the sole actor in the repeated efforts.",
    "st-chp7-p177-i14": "The source names Charles I and his ministers as collective actors and treats Rome as a political counterpart without naming a specific institution or diplomatic action.",
    "st-chp7-p177-i15": "The source names an unnamed wife and an unspecified number of courtiers; it does not identify individual subjects or a candidate for the religious affiliation.",
    "st-chp7-p177-i18": "The Cardinal's identity and the Inquisition tribunal are unspecified; the traveler group is also unnamed.",
    "st-chp7-p177-i19": "The source does not identify the diplomatic exchanges, participants or their dates.",
    "st-chp7-p177-i21": "The source says 'many' but does not identify or count the people to whom Catholic humanism appealed.",
    "st-chp7-p177-i23": "The source does not identify or enumerate the small privileged elite.",
    "st-chp7-p177-i24": "The source names no Puritan individuals or organization; the relation is retained at the level of the source-defined group candidate.",
    "st-chp7-p177-i26": "The source refers to tensions present from the start but does not enumerate them as a single candidate endpoint.",
}

ENDPOINT_FIXES = {
    "st-chp7-p177-i15": {"subject": ("cand-0650", None)},
    "st-chp7-p177-i17": {"subject": ("cand-0650", None)},
    "st-chp7-p177-i24": {"object": (None, "cand-6735")},
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.177 body S2 relation candidates")
    parser.add_argument("--apply", action="store_true", help="write guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    required_source = (
        (90, "[Page 177]"),
        (93, "English efforts to dislodge the principal Italian artists"),
        (94, "The passionate love of art felt by Lord Arundel"),
        (95, "Charles I and his ministers were making a conscious effort"),
        (97, "The whole precarious balance broke down in 1642"),
        (98, "After seeing a picture of Semiramis by Guercino"),
    )
    if any(text not in source_lines[index] for index, text in required_source):
        raise SystemExit("p.177 source-line guards failed")

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
        raise SystemExit(f"p.177 target set changed: {sorted(unset ^ expected_targets)}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 91 or end > 100 or start > end:
            raise SystemExit(f"invalid p.177 source anchor: {sid} {start}-{end}")
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
