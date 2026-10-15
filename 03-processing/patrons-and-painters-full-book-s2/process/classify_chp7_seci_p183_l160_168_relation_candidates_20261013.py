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
SEGMENT = "chp-7:07_CHP-7_sec_i:l160-168"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp7-seci-p183-l160-168-relation-classification-20261013"
EXPECTED = {
    STATEMENTS: "b713446b983ec547e6eab34ac3cace2dc1eb15c6154ad0415f6a70ff9202cb0d",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
}

TRUE_NOTES = {
    "st-chp7-p183-i01": "This records Haskell's claim that Mazarin's accession in France strengthened his position in Rome despite the Pope's hostility; the Pope remains unnamed.",
    "st-chp7-p183-i02": "This records Mazarin's acquisition of the Bentivoglio palace soon after 1644; the transfer chain and uncertain exact date remain as stated in the note.",
    "st-chp7-p183-i03": "This records Mazarin's plan to use the palace for distinguished French visitors; it does not assert that the visitors actually stayed there.",
    "st-chp7-p183-i04": "This records Mazarin's earlier reception in the palace as a young diplomat and his later non-return; no date is inferred.",
    "st-chp7-p183-i05": "This records the casino's containment of Reni's Aurora fresco; the casino and fresco remain unidentified at the more specific level.",
    "st-chp7-p183-i06": "This records Haskell's wording that Guido Reni painted the Aurora fresco for Scipione Borghese; no further commission terms are inferred.",
    "st-chp7-p183-i07": "This preserves Haskell's inference that owning the palace gave Mazarin satisfaction; it is not treated as Mazarin's reported statement.",
    "st-chp7-p183-i08": "This records Mazarin's commission to Longhi through Maccarani for a facade at SS. Vincenzo ed Anastasio; the intermediary and architect remain distinct roles.",
    "st-chp7-p183-i09": "This records Haskell's description of Mazarin's limited control over the facade's architecture, not a legal measure of authority.",
    "st-chp7-p183-i10": "This records the slow facade work alongside Mazarin's increasing economic difficulties; it does not assert that either caused the other.",
    "st-chp7-p183-i11": "This records Haskell's quotation of Mazarin writing to Maccarani shortly before his death in 1661; the cited letter is not independently verified here.",
    "st-chp7-p183-i12": "This records Haskell's interpretation of the facade as proclaiming Mazarin's authority; it is not independent evidence of audience reception.",
    "st-chp7-p183-i13": "This records the First Fronde as a temporary setback to Mazarin's patronage of Italian artists in 1649; Haskell's evaluative wording is preserved.",
    "st-chp7-p183-i14": "This records Haskell's claim that Mazarin's enemies targeted his employment of Italian artists; it does not expand on the political implications he brackets.",
    "st-chp7-p183-i15": "This records the lampoon's description of Italian artists in the quoted terms; its author, title, and publication remain unidentified.",
    "st-chp7-p183-i16": "This records Haskell's statement that Torelli was financially ruined and imprisoned for months; the cited secondary account has not been independently read.",
    "st-chp7-p183-i17": "This records Stefano della Bella's return to Italy after a narrow escape from lynching; the source does not identify the attackers.",
    "st-chp7-p183-i18": "This records Grimaldi's hiding in a Jesuit seminary before returning home; the seminary and destination home remain unidentified.",
    "st-chp7-p183-i19": "This preserves Haskell's summary of reversals in Mazarin's position, library sale, and threatened dispersal of his collections; no single event or collection is substituted for the composite passage.",
    "st-chp7-p183-i20": "This records the footnote's qualified dating of the palace transaction as before 1647 while its exact date remains uncertain; the cited pages have not been independently read.",
    "st-chp7-p183-q01": "This closes the quoted account begun on p.182: offers and flattery led Algardi to change his mind and cancel his French contracts; attribution remains tied to Haskell's cited source.",
}

FALSE_NOTES = {
    "st-chp7-p183-n2-cite-callari": "This is a bibliographic locator for the palace transaction, not an independent relation claim.",
    "st-chp7-p183-n2-cite-daumale": "This is a bibliographic locator for the palace transaction, not an independent relation claim.",
}

OPEN_ENDPOINTS = {
    "st-chp7-p183-i01": "The hostile Pope is mentioned but remains unnamed and is not assigned as the scalar endpoint of this claim.",
    "st-chp7-p183-i03": "The planned visitors are an unnamed collective; the statement does not identify individual guests.",
    "st-chp7-p183-i10": "The sentence links slow construction with Mazarin's economic difficulties but supplies no separate event or entity for the abstract difficulty and does not state causation.",
    "st-chp7-p183-i12": "The authority being proclaimed is an interpretation of Mazarin's status rather than a separately identified entity.",
    "st-chp7-p183-i16": "Financial ruin and imprisonment are reported conditions, with no separate event or responsible actor identified.",
    "st-chp7-p183-i17": "The people threatening Bella are not identified in the source.",
    "st-chp7-p183-i18": "The seminary and the destination described as home are not identified more specifically.",
    "st-chp7-p183-i19": "The passage compresses several political reversals and refers to a library sale and threatened dispersal of collections without naming a single common object.",
    "st-chp7-p183-i20": "The date is a qualified bound on the palace transaction rather than a separately identified entity; the exact date remains unknown.",
    "st-chp7-p183-q01": "The quoted offerors include an unnamed nephew alongside Innocent X; the passage does not identify that nephew.",
}

ENDPOINT_FIXES = {
    "st-chp7-p183-i05": {
        "subject": ("cand-1588", "cand-4291"),
        "object": ("cand-4291", "cand-4290"),
    },
    "st-chp7-p183-i15": {
        "subject": ("cand-6784", "cand-6802"),
        "object": ("cand-6802", "cand-6784"),
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
    parser = argparse.ArgumentParser(description="Classify p.183 body S2 relation candidates")
    parser.add_argument("--apply", action="store_true", help="write guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    required_source = (
        (159, "[Page 183]"),
        (161, "assumption of power in France strengthened his position in Rome"),
        (161, "world-famous fresco of Aurora"),
        (162, "commissioned, through Paolo Maccarani"),
        (163, "Maccarani shortly before his death in 1661"),
        (164, "In 1649 Mazarin"),
        (165, "Giacomo Torelli was financially ruined"),
        (166, "The next four years saw a series of fantastic reversals"),
        (167, "exact-date of the transaction is not certain"),
    )
    if any(text not in source_lines[index] for index, text in required_source):
        raise SystemExit("p.183 source-line guards failed")

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
    if unset != expected_targets or len(unset) != 23:
        raise SystemExit(f"p.183 target set changed: {sorted(unset ^ expected_targets)}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 160 or end > 168 or start > end:
            raise SystemExit(f"invalid p.183 source anchor: {sid} {start}-{end}")
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

    quote_start = by_id["st-chp7-p182-i24"].get("qualifiers") or {}
    if quote_start.get("continuation_resolved_by_segment_id") != SEGMENT or quote_start.get("continuation_resolved_source_line") != 161:
        raise SystemExit("p.182 quote continuation link changed; review before applying")

    for sid, changes in ENDPOINT_FIXES.items():
        row = by_id[sid]
        for field, (_, new) in changes.items():
            row[f"{field}_candidate_id"] = new
    for sid, note in {**TRUE_NOTES, **FALSE_NOTES}.items():
        q = by_id[sid].setdefault("qualifiers", {})
        q["relation_candidate"] = sid in TRUE_NOTES
        q["relation_candidate_note"] = note
        if sid in OPEN_ENDPOINTS:
            q["open_endpoint_reason"] = OPEN_ENDPOINTS[sid]
    continuation = by_id["st-chp7-p183-q01"].setdefault("qualifiers", {})
    continuation["continuation_of_statement_id"] = "st-chp7-p182-i24"
    continuation["continuation_from_segment_id"] = "chp-7:07_CHP-7_sec_i:l150-158"
    continuation["continuation_status"] = "closed"

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
        "continuation_link": "st-chp7-p182-i24 -> st-chp7-p183-q01",
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
