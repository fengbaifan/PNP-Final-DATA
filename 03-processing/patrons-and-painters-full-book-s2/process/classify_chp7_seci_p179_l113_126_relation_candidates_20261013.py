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
SEGMENT = "chp-7:07_CHP-7_sec_i:l113-126"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp7-seci-p179-l113-126-relation-classification-20261013"
EXPECTED = {
    STATEMENTS: "aa4545f7c92a77b060db760eca7299e60aea28e81f37cf7c73394bf58ee07ccf",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
}

TRUE_NOTES = {
    "st-chp7-p179-i01": "This records Arundel's intention to employ Fanelli on the tomb; it does not establish that either the tomb or employment was carried out.",
    "st-chp7-p179-i03": "This records Charles I securing Barberini authorization for Bernini's bust; the Pope's hopes and fears concerning English Catholics remain the means described by Haskell.",
    "st-chp7-p179-i04": "This records the bust's arrival in England and its basis in Van Dyck's triple portrait; both destination and source portrait are retained in the statement mentions.",
    "st-chp7-p179-i05": "This records Haskell's comparison of Bernini's bust with Van Dyck's portrait and the sitter's response; the aesthetic characterization remains attributed to Haskell.",
    "st-chp7-p179-i06": "This records Charles I's delight in the bust and his gifts to Bernini; the presents are not individually identified.",
    "st-chp7-p179-i07": "This records plans for a Queen's bust; the immediately following account identifies it as Bernini's and later says it was cancelled.",
    "st-chp7-p179-i08": "This records Thomas Baker carrying Van Dyck's triple portrait to Rome for Bernini; it is distinct from Bernini's later bust of Baker.",
    "st-chp7-p179-i09": "This records Bernini making a bust of Baker before Pope Urban VIII; the work remains distinct from Van Dyck's portrait.",
    "st-chp7-p179-i10": "This records Urban VIII halting further English commissions to preserve the exceptional concession for Charles I's bust; the affected commissioners and works are not specified.",
    "st-chp7-p179-i11": "This records Arundel's quoted statement that he sent a picture of himself with 'little Tom' through Francesco to William Petty; the carrier and 'little Tom' remain unidentified.",
    "st-chp7-p179-i12": "This records Arundel's request for a Florentine marble relief based on the picture, to be attempted by a young sculptor named Francesco; execution is not established.",
    "st-chp7-p179-i13": "This records Arundel's wish for Bernini or Duquesnoy to make a second relief of the same subject; it remains an alternative proposal, not a completed work.",
    "st-chp7-p179-i14": "This records Haskell's statement that Arundel's relief wishes were unfulfilled; the passage does not identify which alternative failed or why.",
    "st-chp7-p179-i15": "This records the source's broad claim that contemporary Italian works reached England before 1642; no individual work or transfer is identified.",
    "st-chp7-p179-i16": "This records Haskell's report that Charles I commissioned a group of paintings from Angelo Caroselli; no titles, number, or completion status are given.",
    "st-chp7-p179-i17": "This records the unidentified Cardinal Barberini sending pictures to Henrietta Maria and their display in her private chapel at Somerset House; the individual pictures remain unnamed.",
    "st-chp7-p179-i18": "This preserves Haskell's evaluation of the display as tactless and the reported complaints that gifts from Rome were deceiving the King; it does not assert that deception occurred.",
    "st-chp7-p179-i19": "This records the Reni painting's arrival as civil war neared and its subsequent passage into French hands; the recipient and transfer mechanism are unspecified.",
    "st-chp7-p179-i20": "This records the cancellation of Bernini's planned bust of Henrietta Maria; the work was not completed according to this account.",
    "st-chp7-p179-i21": "This records Fanelli's hurried departure to Paris in the period described by Haskell.",
    "st-chp7-p179-i25": "This records Urban VIII's unnamed nephews fleeing Rome and Haskell's claim that their departure removed Italy's leading source of patronage; the group remains untyped and unidentified.",
    "st-chp7-p179-i26": "This records the p.180-confirmed identification of the unnamed 'Italian amateur' as Mazarin and Haskell's claim that he controlled French affairs by 1644.",
    "st-chp7-p179-n1-cite-wittkower": "This records the book's citation of Wittkower's 1955 work as a locator for the Queen's bust account; the cited source was not independently consulted here.",
}

FALSE_NOTES = {
    "st-chp7-p179-i02": "This is Haskell's characterization of Charles I's artistic imagination, without a discrete relation between identified entities.",
    "st-chp7-p179-i22": "This compares the timing of Gentileschi's death with Fanelli's departure but does not assert a social or other entity relation; no event nodes are identified here.",
    "st-chp7-p179-i23": "This is Haskell's periodization of the dissemination of Italian art, not a discrete relation between identified entities.",
    "st-chp7-p179-i24": "This is a dated biographical event about Urban VIII, without a second entity endpoint.",
    "st-chp7-p179-i27": "This is a broad historical statement about the return of peace in two regions; no discrete relation between identified entities is asserted.",
}

OPEN_ENDPOINTS = {
    "st-chp7-p179-i10": "The source does not identify the further English commissioners or the works Urban VIII stopped; Bernini and Charles I describe the preceding exceptional concession.",
    "st-chp7-p179-i14": "The two proposed reliefs are separate candidate works, and Haskell does not specify whether both or only one were unrealized.",
    "st-chp7-p179-i15": "The source names Italy and England but no individual or bounded group of the many contemporary works that travelled between them.",
    "st-chp7-p179-i18": "The complainants and the particular gifts covered by their allegation are unnamed; the claim is retained as a reported criticism, not verified deception.",
    "st-chp7-p179-i25": "The nephews are unnamed and the source does not identify each patronage activity removed by their departure.",
    "st-chp7-p179-n1-cite-wittkower": "The cited work is identified, but the citing book is represented by this project's source_id rather than an entity candidate.",
}

ENDPOINT_FIXES = {
    "st-chp7-p179-i05": {
        "subject": ("cand-0295", "cand-0304"),
        "object": ("cand-0304", "cand-4437"),
    },
    "st-chp7-p179-i07": {"subject": (None, "cand-0295")},
    "st-chp7-p179-i20": {"subject": (None, "cand-0295")},
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.179 body S2 relation candidates")
    parser.add_argument("--apply", action="store_true", help="write guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    required_source = (
        (112, "[Page 179]"),
        (113, "Fanelli’s reputation in England"),
        (114, "He used all his influence"),
        (116, "Meanwhile his courtiers"),
        (117, "Arundel was less successful"),
        (120, "Many contemporary works of art reached England"),
        (121, "Caroselli"),
        (123, "The 1640s and 1650s mark a turning-point"),
        (124, "In 1644 Pope Urban VIII died"),
        (125, "Wittkower, 1955, p. 201"),
    )
    if any(text not in source_lines[index] for index, text in required_source):
        raise SystemExit("p.179 source-line guards failed")

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
    if unset != expected_targets or len(unset) != 28:
        raise SystemExit(f"p.179 target set changed: {sorted(unset ^ expected_targets)}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 113 or end > 126 or start > end:
            raise SystemExit(f"invalid p.179 source anchor: {sid} {start}-{end}")
        refs = [row.get("subject_candidate_id"), row.get("object_candidate_id")] + q.get("mentioned_candidate_ids", [])
        missing_refs = sorted({cid for cid in refs if cid and cid not in candidate_ids})
        if missing_refs:
            raise SystemExit(f"candidate reference missing for {sid}: {missing_refs}")
    for sid, changes in ENDPOINT_FIXES.items():
        row = by_id[sid]
        for field, (old, new) in changes.items():
            if row.get(f"{field}_candidate_id") != old:
                raise SystemExit(f"unexpected {field} endpoint for {sid}; review before applying")
            if new not in candidate_ids:
                raise SystemExit(f"replacement candidate missing for {sid}: {new}")

    for sid, changes in ENDPOINT_FIXES.items():
        row = by_id[sid]
        for field, (_, new) in changes.items():
            row[f"{field}_candidate_id"] = new
    for sid in ("st-chp7-p179-i05",):
        q = by_id[sid].setdefault("qualifiers", {})
        mentioned = q.setdefault("mentioned_candidate_ids", [])
        if "cand-4437" not in mentioned:
            mentioned.append("cand-4437")
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
        ],
        "added_statement_candidate_links": ["st-chp7-p179-i05 mentioned cand-4437"] ,
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
