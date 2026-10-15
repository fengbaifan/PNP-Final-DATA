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
SEGMENT = "chp-7:07_CHP-7_sec_i:l232-241"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp7-seci-p188-l232-241-relation-classification-20261013"
EXPECTED = {
    STATEMENTS: "7429b62323c12aa79b6ca58e20eccd96e73d5b50645cf0ce2dc4104e7a76b37c",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
}

TRUE_NOTES = {
    "st-chp7-p188-i01": "This preserves Bernini's quoted demand for grander French royal projects; the quotation begins on p.187 and closes here.",
    "st-chp7-p188-i02": "This records Colbert's inability to view the Louvre proposals from Bernini's perspective; the person whose view is contrasted is explicit.",
    "st-chp7-p188-i03": "This records Colbert's practical attention to expense and the detailed arrangement of rooms.",
    "st-chp7-p188-i04": "This preserves Haskell's claim that Bernini failed to appreciate the institutional difference between the French monarchy and the papacy.",
    "st-chp7-p188-i05": "This records Haskell's account of each new pope seeking to outshine the predecessor and begin afresh.",
    "st-chp7-p188-i06": "This records the contrast between hereditary French kingship and the preservation of revered predecessors' memory.",
    "st-chp7-p188-i07": "This records Louis XIV's attempt to explain his wish to preserve what his predecessors had made.",
    "st-chp7-p188-i08": "This records that Louis XIV's explanation did not affect Bernini, whose proposals remained uncompromisingly new.",
    "st-chp7-p188-i09": "This preserves Haskell's causal account linking Bernini's contempt for French things to the opposition it aroused.",
    "st-chp7-p188-i10": "This records the existence of factions at court without inventing their members.",
    "st-chp7-p188-i11": "This records the King's continued interest in Bernini's plans; the passage does not name a particular proposal.",
    "st-chp7-p188-i12": "This records Bernini's return journey from Paris to Rome by October.",
    "st-chp7-p188-i13": "This records the contemporary belief that Bernini's further plans would not be executed; the believers are unnamed.",
    "st-chp7-p188-i15": "This records Bernini's commission to make a marble bust of Louis XIV within weeks of arriving in Paris.",
    "st-chp7-p188-i16": "This records the bust as Bernini's first opportunity to portray a secular prince from life.",
    "st-chp7-p188-i17": "This preserves Haskell's interpretation of the bust as an idealized image of personal monarchy.",
    "st-chp7-p188-i18": "This records the bust's attributed role as a record of absolutism in visual art while retaining Haskell's superlative assessment.",
    "st-chp7-p188-i19": "This records Louis XIV ordering an equestrian statue after seeing Bernini's bust.",
    "st-chp7-p188-i20": "This records Bernini beginning the equestrian statue four years after returning to Rome.",
    "st-chp7-p188-i21": "This records the statue's arrival in Paris in 1684, after Bernini's death.",
    "st-chp7-p188-i23": "This preserves Haskell's comparative claim about France's military, literary, and other standing; the rival countries are not enumerated.",
    "st-chp7-p188-i24": "This records Haskell's explanation of Gallican principles as Louis XIV's wish for a state religion independent of papal influence.",
    "st-chp7-p188-i25": "This records the judgment that Bernini's monument was uncongenial; the judging audience is implicit and remains open.",
    "st-chp7-p188-i26": "This records the request that the equestrian statue follow Bernini's Constantine statue; the requester is not named.",
    "st-chp7-p188-i27": "This preserves Haskell's modal interpretation that the statue echoed ultramontane claims and seemed jarring and tactless.",
    "st-chp7-p188-i28": "This records Haskell's claim that native French taste rejected Italian floridity.",
    "st-chp7-p188-i29": "This records Louis XIV's wish to break up the equestrian statue.",
    "st-chp7-p188-i30": "This records Louis XIV relenting and banishing the statue to a remote part of the Versailles grounds.",
    "st-chp7-p188-i31": "This records Girardon's alterations to the statue and its later name, Marcus Curtius; the name is not treated as a separate person.",
    "st-chp7-p188-i32": "This preserves the reported interpretation that Bernini's Paris failure marked the collapse of Italian artistic prestige in France.",
    "st-chp7-p188-i33": "This records Haskell's claim that criticism and hostility toward Italian art strengthened as French self-assurance grew.",
}

FALSE_NOTES = {
    "st-chp7-p188-i14": "This is Haskell's evaluative praise of Bernini's genius, without a separate relation between represented entities.",
    "st-chp7-p188-i22": "This is a characterization of French national mood, not a relation between distinct entities in the passage.",
    "st-chp7-p188-i34": "This is an incomplete sentence fragment; its continuation is linked to p.189, where the claim can be read in full.",
}

OPEN_ENDPOINTS = {
    "st-chp7-p188-i09": "The opposition is attributed to hostility Bernini aroused, but the French actors or institution are not identified.",
    "st-chp7-p188-i10": "The court factions are not named or enumerated.",
    "st-chp7-p188-i13": "The plans are identified, but the source of the widespread belief that they would not be executed is unnamed.",
    "st-chp7-p188-i15": "The commission and bust are explicit, but the commissioning patron is not named in this sentence.",
    "st-chp7-p188-i23": "France's unnamed rival countries or combination of countries are not enumerated.",
    "st-chp7-p188-i25": "The audience that found the monument uncongenial is implied by context but not named.",
    "st-chp7-p188-i26": "The requester is not named; the source only says that Bernini had been asked.",
    "st-chp7-p188-i27": "The claims and the statue's echo are identified, but the audience for whom they seemed jarring is not named; this remains Haskell's inference.",
    "st-chp7-p188-i32": "The source says the interpretation is always reported but does not identify its proponents.",
}

ENDPOINT_FIXES = {
    "st-chp7-p188-i02": {"object": (None, "cand-0295")},
    "st-chp7-p188-i09": {"object": (None, "cand-1082")},
    "st-chp7-p188-i11": {"object": (None, "cand-6906")},
    "st-chp7-p188-i13": {"object": (None, "cand-6906")},
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.188 body S2 relation candidates")
    parser.add_argument("--apply", action="store_true", help="write guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    required_source = (
        (232, "[Page 188]"),
        (233, "But Colbert couldhardly see the matter in the same light"),
        (234, "the French monarchy and the papacy"),
        (235, "There were factions at court"),
        (236, "one unchallengeable proof of his genius"),
        (237, "The bust he made in 1665 remains the most compelling record"),
        (238, "no country—or combination of countries—could rival her"),
        (239, "No wonder that Bernini’s monument was found uncongenial"),
        (240, "Soon Girardon made the necessary alterations"),
        (241, "It is also true that, with the full support"),
        (243, "[Page 189]"),
        (244, "Louis established in 1666 the French Academy in Rome"),
    )
    if any(text not in source_lines[index - 1] for index, text in required_source):
        raise SystemExit("p.188/p.189 source-line guards failed")

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
    if unset != expected_targets or len(unset) != 34:
        raise SystemExit(f"p.188 target set changed: {sorted(unset ^ expected_targets)}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 233 or end > 241 or start > end:
            raise SystemExit(f"invalid p.188 source anchor: {sid} {start}-{end}")
        refs = [row.get("subject_candidate_id"), row.get("object_candidate_id")] + q.get("mentioned_candidate_ids", [])
        missing_refs = sorted({cid for cid in refs if cid and cid not in candidate_ids})
        if missing_refs:
            raise SystemExit(f"candidate reference missing for {sid}: {missing_refs}")

    opening = by_id["st-chp7-p188-i01"]
    opening_q = opening.get("qualifiers") or {}
    if opening_q.get("continuation_of_statement_id") != "st-chp7-p187-i29":
        raise SystemExit("p.188 opening quotation continuation changed")
    previous_q = by_id["st-chp7-p187-i29"].get("qualifiers") or {}
    if previous_q.get("continuation_to_segment_id") != SEGMENT or previous_q.get("continuation_source_line_start") != 233:
        raise SystemExit("p.187 to p.188 quotation link changed")
    closing = by_id["st-chp7-p188-i34"]
    closing_q = closing.get("qualifiers") or {}
    successor = by_id["st-chp7-p189-i01"]
    successor_q = successor.get("qualifiers") or {}
    if closing_q.get("continuation_statement_id") != successor["statement_id"]:
        raise SystemExit("p.188 closing fragment target changed")
    if successor.get("segment_id") != "chp-7:07_CHP-7_sec_i:l243-257" or successor_q.get("source_line_start") != 244:
        raise SystemExit("p.189 continuation anchor changed")
    if successor_q.get("continuation_of_statement_id") != closing["statement_id"]:
        raise SystemExit("p.189 reciprocal continuation link changed")

    for sid, endpoints in ENDPOINT_FIXES.items():
        row = by_id[sid]
        for endpoint, (expected_old, new_value) in endpoints.items():
            field = f"{endpoint}_candidate_id"
            if row.get(field) != expected_old:
                raise SystemExit(f"{sid} {field} changed: expected {expected_old!r}, got {row.get(field)!r}")
            if new_value not in candidate_ids:
                raise SystemExit(f"{sid} references missing {new_value}")
            mentioned = (row.get("qualifiers") or {}).get("mentioned_candidate_ids", [])
            if new_value not in mentioned:
                raise SystemExit(f"{sid} endpoint {new_value} is not grounded in its mention set")

    for sid, note in {**TRUE_NOTES, **FALSE_NOTES}.items():
        q = by_id[sid].setdefault("qualifiers", {})
        q["relation_candidate"] = sid in TRUE_NOTES
        q["relation_candidate_note"] = note
        if sid in OPEN_ENDPOINTS:
            q["open_endpoint_reason"] = OPEN_ENDPOINTS[sid]
    for sid, endpoints in ENDPOINT_FIXES.items():
        row = by_id[sid]
        for endpoint, (_, new_value) in endpoints.items():
            row[f"{endpoint}_candidate_id"] = new_value

    closing_q = closing.setdefault("qualifiers", {})
    closing_q["continuation_to_segment_id"] = successor["segment_id"]
    closing_q["continuation_status"] = "closed"
    closing_q["continuation_source_line_start"] = successor_q["source_line_start"]
    closing_q["continuation_source_line_end"] = successor_q["source_line_end"]

    output = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n"
    result = output.encode("utf-8")
    print(json.dumps({
        "mode": "apply" if args.apply else "dry_run",
        "segment": SEGMENT,
        "classified": len(unset),
        "relation_candidate_true": len(TRUE_NOTES),
        "relation_candidate_false": len(FALSE_NOTES),
        "unset_in_segment": 0,
        "endpoint_fixes": {sid: edits for sid, edits in ENDPOINT_FIXES.items()},
        "continuation_links": [
            "st-chp7-p187-i29 -> st-chp7-p188-i01",
            "st-chp7-p188-i34 -> st-chp7-p189-i01",
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
