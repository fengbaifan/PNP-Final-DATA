from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
SOURCE = ROOT / "02-sources/02-Markdown/06_CHP-6_sec_i.md"
EXPECTED_SHA256 = "cdb1614f56310ef6f222e6524b0922aa2c77c1573d7eea5d5ebeb1265feb2edb"
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-chp6-p155-body-relations-20261010")

RELATIONS = {
    "st-chp6-p155-bernin-reconstruction-delayed": {
        "predicate": "reconstruction-begins-late-in-papacy",
        "subject": "cand-0312", "object": "cand-0816", "line": 103,
        "anchor": "Bernini did not begin to reconstruct the palace until",
        "note": "The source directly connects Bernini with reconstruction of the palace and dates its start relative to Alexander VII's papacy. The palace endpoint is kept as the existing candidate; it is not merged with the similarly named Colonna palace candidate elsewhere in this passage.",
    },
    "st-chp6-p155-colonna-palace-decorated-by-girolamo": {
        "predicate": "rebuilt-and-decorated-by",
        "subject": "cand-0815", "object": "cand-0809", "line": 105,
        "anchor": "rebuilt and decorated by Filippo and his son, Cardinal Girolamo",
        "note": "The source explicitly names Girolamo as one of the two actors who rebuilt and decorated the Colonna palace. This row isolates his role; the palace identity remains at the current candidate level.",
    },
    "st-chp6-p155-colonna-palace-rebuilt": {
        "predicate": "rebuilt-and-decorated-by",
        "subject": "cand-0815", "object": "cand-0806", "line": 105,
        "anchor": "rebuilt and decorated by Filippo and his son, Cardinal Girolamo",
        "note": "The source explicitly names Filippo as one of the two actors who rebuilt and decorated the Colonna palace. This row isolates his role; the palace identity remains at the current candidate level.",
    },
    "st-chp6-p155-lorenzo-maria-marriage": {
        "predicate": "married-in-1661",
        "subject": "cand-0811", "object": "cand-1509", "line": 106,
        "anchor": "he married Maria Mancini",
        "note": "The source explicitly states Lorenzo Onofrio's marriage to Maria Mancini in 1661; the date remains a source-qualified assertion.",
    },
    "st-chp6-p155-palestrina-sale": {
        "predicate": "sold-to-under-financial-pressure",
        "subject": "cand-4215", "object": "cand-0198", "line": 105,
        "anchor": "sell their principality of Palestrina to the Barberini",
        "note": "The source explicitly reports the sale of the principality of Palestrina to the Barberini under financial pressure. The existing property-to-buyer endpoints are retained; the individual seller is not inferred.",
    },
    "st-chp6-p155-lorenzo-onofrio-family-patron": {
        "predicate": "influential-patron-of-family",
        "subject": "cand-0811", "object": "cand-4638", "line": 105,
        "anchor": "the most interesting and influential patron of the family was Lorenzo Onofrio",
        "note": "The source explicitly identifies Lorenzo Onofrio as an influential patron of the Colonna family; the author's evaluative wording remains in the claim.",
    },
    "st-chp6-p155-lorenzo-collection-additions": {
        "predicate": "adds-to-family-picture-collection",
        "subject": "cand-0811", "object": "cand-6334", "line": 107,
        "anchor": "continued to make a series of impressive additions to the family picture collection",
        "note": "The source explicitly states that Lorenzo continued adding pictures to the family collection. The collection candidate remains formally unidentified.",
    },
    "st-chp6-p155-grimaldi-landscape-decoration": {
        "predicate": "engaged-to-paint-landscapes-in-palace",
        "subject": "cand-1232", "object": "cand-0815", "line": 107,
        "anchor": "Gianfrancesco Grimaldi and many other artists were engaged to paint landscapes in his palace",
        "note": "The source explicitly connects Grimaldi with landscape painting in Lorenzo's palace. The passive wording does not identify the commissioning agent, so none is added.",
    },
    "st-chp6-p155-lorenzo-eclectic-patronage": {
        "predicate": "employs-range-of-roman-artists",
        "subject": "cand-0811", "object": "cand-3540", "line": 107,
        "anchor": "most of the principal Roman artists worked for him",
        "note": "The source explicitly states that principal Roman artists worked for Lorenzo. The range from bamboccianti to history painters is retained as the author's broad characterization.",
    },
    "st-chp6-p155-lorenzo-genre-preferences": {
        "predicate": "prefers-mythological-and-landscape-subjects",
        "subject": "cand-0811", "object": "cand-6335", "line": 107,
        "anchor": "his greatest passion seems to have been for mythological fables and landscapes",
        "note": "The source attributes a qualified preference to Lorenzo; 'seems' and the combined subject categories remain in the claim and qualifier.",
    },
    "st-chp6-p155-landscape-decoration-fashion": {
        "predicate": "helps-launch-or-confirm-fashion",
        "subject": "cand-0811", "object": "cand-6336", "line": 107, "anchor_line": 108,
        "anchor": "helped to launch, or at least to confirm, a fashion",
        "note": "The source presents Lorenzo's preference as possibly helping launch or confirm a landscape-decoration fashion. The alternative and limited causal strength are preserved; this is a source-qualified candidate, not an established causal fact.",
    },
    "st-chp6-p155-resta-landscape-criticism": {
        "predicate": "criticizes-landscape-artists-and-bamboccianti",
        "subject": "cand-2134", "object": "cand-6337", "line": 108,
        "anchor": "not derive much pleasure from these landscape artists and bamboc-",
        "note": "Haskell reports Resta's explicit criticism of landscape artists and bamboccianti. The statement remains attributed and does not identify individual artists.",
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = TABLE.read_bytes()
    actual_sha = sha256(raw)
    if actual_sha != EXPECTED_SHA256:
        raise SystemExit(f"input SHA mismatch: expected {EXPECTED_SHA256}, got {actual_sha}")

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as f:
        candidate_ids = {row["candidate_id"] for row in csv.DictReader(f)}
    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for sid, spec in RELATIONS.items():
        anchor_line = spec.get("anchor_line", spec["line"])
        if not (1 <= anchor_line <= len(source_lines)) or spec["anchor"] not in source_lines[anchor_line - 1]:
            raise SystemExit(f"source anchor mismatch: {sid} L{anchor_line}")
        for endpoint in (spec["subject"], spec["object"]):
            if endpoint not in candidate_ids:
                raise SystemExit(f"missing candidate endpoint {endpoint}: {sid}")

    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    by_id = {row.get("statement_id"): row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")
    if not set(RELATIONS).issubset(by_id):
        raise SystemExit(f"missing statements: {sorted(set(RELATIONS) - set(by_id))}")

    changed = {}
    for sid, spec in RELATIONS.items():
        row = deepcopy(by_id[sid])
        q = row.get("qualifiers") or {}
        if row.get("predicate") != spec["predicate"]:
            raise SystemExit(f"predicate mismatch: {sid}")
        if row.get("subject_candidate_id") != spec["subject"] or row.get("object_candidate_id") != spec["object"]:
            raise SystemExit(f"endpoint mismatch: {sid}")
        if q.get("source_line_start") != spec["line"] or q.get("source_line_end") not in (spec["line"], spec["line"] + 1):
            raise SystemExit(f"source span mismatch: {sid}")
        if q.get("relation_candidate") is not None:
            raise SystemExit(f"relation already classified: {sid}")
        q["relation_candidate"] = True
        q["relation_candidate_note"] = spec["note"]
        row["qualifiers"] = q
        changed[sid] = row

    output = []
    seen = set()
    for line in raw.decode("utf-8").splitlines():
        if not line.strip():
            output.append(line)
            continue
        row = json.loads(line)
        sid = row["statement_id"]
        if sid in changed:
            output.append(json.dumps(changed[sid], ensure_ascii=False, separators=(",", ":")))
            seen.add(sid)
        else:
            output.append(line)
    if seen != set(RELATIONS):
        raise SystemExit("write coverage mismatch")
    result = ("\n".join(output) + "\n").encode("utf-8")

    print(f"preflight passed: {len(changed)}/{len(RELATIONS)} statements, exact endpoints and source anchors; input_sha256={actual_sha}")
    print("classification only: no candidates, mentions, endpoints, or formal relations added")
    if not args.apply:
        print("dry-run only; table unchanged")
        return

    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")
    shutil.copy2(TABLE, BACKUP)
    fd, temp_name = tempfile.mkstemp(prefix=TABLE.name + ".", suffix=".tmp", dir=TABLE.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(result)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_name, TABLE)
    except Exception:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
        raise
    print(f"applied: backup={BACKUP.relative_to(ROOT)} output_sha256={sha256(result)}")


if __name__ == "__main__":
    main()
