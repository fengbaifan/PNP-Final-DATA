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
SEGMENT = "chp-7:07_CHP-7_sec_i:l3-9"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp7-seci-p169-l3-9-relation-classification-20261013"
EXPECTED = {
    STATEMENTS: "40b0792ffdb328b3c1a93bb80df0c40e9e64cbf38df5db2cdfe41ce2ad92bed8",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
}

TARGETS = {
    "st-chp7-p169-i01": "This records Rosa's 1669 letter to Ricciardi; it establishes this communication, not a separately documented long-term correspondence.",
    "st-chp7-p169-i02": "This preserves Rosa's quoted report of declining commissions from across Europe. The commissioners are unnamed; the separate Forabosco-prince group is not the endpoint here.",
    "st-chp7-p169-i03": "This records Haskell's causal account linking Rome's financial and political decline to the popes' difficulty maintaining patronage; no individual pope or measured decline is inferred.",
    "st-chp7-p169-i04": "This records Haskell's account of outside-Italy figures taking over patronage; the collective group remains as stated and is not expanded to named patrons.",
    "st-chp7-p169-i05": "This preserves Haskell's modal counterfactual linking recession to the threatened future of large-scale painting in Italy; it does not assert that the predicted outcome occurred.",
    "st-chp7-p169-i06": "This records Haskell's stated relation between unspecified foreign intervention and the halting and reversal of the recession; actors and dates remain unknown.",
    "st-chp7-p169-i07": "This records the source-defined Italian-painter group becoming more sought after and taking advantage of the changed patronage situation; no individual painter is inferred.",
    "st-chp7-p169-i08": "This records Ruffo's 1671 attempt to obtain a picture from Forabosco and the reported snub in Messina.",
    "st-chp7-p169-i09": "This records the reported prospective wait and price for the unidentified picture; 'two half-length figures' is not expanded into two separate works.",
    "st-chp7-p169-i10": "This preserves the report that European princes implored Forabosco for works and would pay his requested prices; it remains Haskell's reported account, not independent verification.",
    "st-chp7-p169-i11": "This records Haskell's broad but explicit claim that Italian artists relied on foreign clients for commissions; 'few' and 'significant proportion' remain qualitative.",
    "st-chp7-p169-i12": "This records the stated painter-to-patron relation for an unnamed subset of Italian artists and the princes and viceroys of Germany and Spain; no individuals are inferred.",
    "st-chp7-p169-i13": "This records the migration of the source-defined artist group from Italy to new countries. The destination countries and individual artists are not named.",
    "st-chp7-p169-i14": "This records the artists' stated tactic of playing Italian and foreign patrons against one another to obtain high terms; 'blackmail' remains Haskell's evaluation.",
    "st-chp7-p169-i16": "This records Crespi's letter to the Prince of Liechtenstein and the prince's wish for Crespi to come to Vienna for palace decoration; the palace is not identified.",
    "st-chp7-p169-i17": "This preserves Crespi's quoted conditional response to the proposed service arrangement; it does not claim that he travelled or completed the decoration.",
    "st-chp7-p169-i18": "This records Crespi's refusal to collaborate with an architectural painter; that painter is unnamed.",
    "st-chp7-p169-n2-cite": "This records the segment's citation to Haskell 1959 as a source locator, not independent verification.",
}
OPEN_ENDPOINTS = {
    "st-chp7-p169-i02": "Rosa reports commissions from across Europe, but no commissioning person or group is identified. The candidate for princes seeking pictures from Forabosco refers to a different passage and is removed from this statement.",
    "st-chp7-p169-i13": "The source-defined Italian-painter group is retained as subject; Italy is the stated place of departure, but no settlement destination or individual artist is named.",
    "st-chp7-p169-i18": "Crespi is named, but the architectural painter with whom he refused to collaborate is not identified.",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.169 body S2 relation candidates")
    parser.add_argument("--apply", action="store_true", help="write guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    if not ("N 1669" in source_lines[2] and "Ricciardi" in source_lines[4] and "Forabosco" in source_lines[5] and "Haskell, 1959" in source_lines[8]):
        raise SystemExit("p.169 source-line guard failed")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row["statement_id"]
        for row in rows
        if row.get("segment_id") == SEGMENT and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    if unset != set(TARGETS):
        raise SystemExit(f"p.169 target set changed: {sorted(unset ^ set(TARGETS))}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    required = {"cand-2962", "cand-2241", "cand-2187", "cand-6598", "cand-6606"}
    if missing := sorted(required - candidate_ids):
        raise SystemExit(f"required candidates missing: {missing}")

    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 3 or end > 9 or start > end:
            raise SystemExit(f"invalid p.169 source anchor: {sid} {start}-{end}")
        refs = [row.get("subject_candidate_id"), row.get("object_candidate_id")] + q.get("mentioned_candidate_ids", [])
        missing_refs = sorted({cid for cid in refs if cid and cid not in candidate_ids})
        if missing_refs:
            raise SystemExit(f"candidate reference missing for {sid}: {missing_refs}")

    # cand-6598 denotes princes seeking works from Forabosco at line 6, not Rosa's unnamed commissioners at line 5.
    if by_id["st-chp7-p169-i02"].get("object_candidate_id") != "cand-6598":
        raise SystemExit("unexpected p.169 i02 object endpoint; review before applying")
    by_id["st-chp7-p169-i02"]["object_candidate_id"] = None

    for sid, note in TARGETS.items():
        row = by_id[sid]
        q = row.setdefault("qualifiers", {})
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note
        if sid in OPEN_ENDPOINTS:
            q["open_endpoint_reason"] = OPEN_ENDPOINTS[sid]
        if row.get("predicate") == "footnote_citation":
            row["subject_candidate_id"] = "cand-2962"

    output = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n"
    result = output.encode("utf-8")
    print(json.dumps({"mode": "apply" if args.apply else "dry_run", "segment": SEGMENT, "classified": len(unset), "relation_candidate_true": len(TARGETS), "relation_candidate_false": 0, "unset_in_segment": 0, "endpoint_corrections": ["st-chp7-p169-i02 object_candidate_id cand-6598 -> null"], "citation_source_endpoint": "st-chp7-p169-n2-cite subject_candidate_id=cand-2962", "before_sha256": digest(raw[STATEMENTS]), "after_sha256": digest(result)}, ensure_ascii=True))
    if not args.apply:
        return
    if BACKUP.exists():
        raise SystemExit(f"backup already exists; refusing to overwrite: {BACKUP.name}")
    shutil.copy2(STATEMENTS, BACKUP)
    atomic_write(STATEMENTS, result)
    print(f"backup={BACKUP.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
