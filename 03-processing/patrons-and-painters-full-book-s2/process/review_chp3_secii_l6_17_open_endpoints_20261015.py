from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
MENTIONS = ROOT / "04-knowledge/tables/mentions.csv"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-chp3-secii-l6-17-open-endpoints-20261015")

APSE = "st-chp3-secii-l6-17-apse-mosaic-plan"
PAINTER = "st-chp3-secii-l6-17-external-painter-exposed-jesuit-financial-weakness"
SCHEMES = "st-chp3-secii-l6-17-schemes-grandiose-while-alive"
BAGLIONE_EXAMPLE = "st-chp3-secii-l6-17-baglione-complained-to-pope-about-unpaid-fee"
SEGMENT = "chp-3:03_CHP-3_sec_ii:l6-17"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def transform(raw: bytes) -> tuple[bytes, dict[str, dict]]:
    lines = raw.decode("utf-8").splitlines(keepends=True)
    found: dict[str, dict] = {}
    all_ids: set[str] = set()
    for i, line in enumerate(lines):
        item = json.loads(line)
        sid = item.get("statement_id")
        if sid:
            all_ids.add(sid)
        if sid not in {APSE, PAINTER, SCHEMES}:
            continue
        if item.get("segment_id") != SEGMENT:
            raise ValueError(f"Unexpected segment for {sid}: {item.get('segment_id')}")
        found[sid] = item
        q = item.setdefault("qualifiers", {})
        if sid == APSE:
            if item.get("subject_candidate_id"):
                raise ValueError(f"Expected unresolved passive subject for {sid}")
            q["open_endpoint_reason"] = (
                "The passive clause 'plans were made' does not identify who formulated the apse mosaic plan. "
                "The surrounding passage frames several projects as Farnese's schemes, but does not explicitly "
                "assign the plan-maker; do not infer Farnese, the Jesuits, or the artists."
            )
        elif sid == PAINTER:
            if item.get("object_candidate_id"):
                raise ValueError(f"Expected open painter endpoint for {sid}")
            item["object_candidate_id"] = "cand-0158"
            q["claim"] = (
                "Haskell says commissioning an established painter from outside the Jesuits' ranks made their "
                "financial weakness evident; the immediately following account of Giovanni Baglione's unpaid "
                "Resurrection picture supplies a concrete instance."
            )
            q["qualification"] = (
                "Baglione is linked as one contextual example: Haskell says he complained to the Pope that the "
                "Jesuit fathers had not fully paid him five years after his Resurrection picture. The broader "
                "generalization does not make him the only outside painter."
            )
            q["relation_candidate_note"] = (
                "The next sentence names Giovanni Baglione and reports his unpaid Resurrection picture as a "
                "concrete example of the financial weakness exposed by work outside the Jesuits' own ranks. "
                "Link Baglione as one instance, not as the exhaustive set of external painters."
            )
            q.pop("open_endpoint_reason", None)
            q["related_statement_ids"] = [BAGLIONE_EXAMPLE]
        elif sid == SCHEMES:
            q["relation_candidate"] = False
            q["relation_candidate_note"] = (
                "This is Haskell's evaluative characterization of Farnese's schemes as 'grandiose,' like other "
                "one-ended aesthetic judgments in the same section. It does not assert a relation between two "
                "bounded entities; preserve the attribution and continuation without inventing an object."
            )
            q.pop("open_endpoint_reason", None)
        lines[i] = json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n"

    if set(found) != {APSE, PAINTER, SCHEMES}:
        raise ValueError(f"Missing target statements: {sorted({APSE, PAINTER, SCHEMES} - found.keys())}")
    if BAGLIONE_EXAMPLE not in all_ids:
        raise ValueError(f"Missing contextual statement: {BAGLIONE_EXAMPLE}")

    with MENTIONS.open(encoding="utf-8-sig", newline="") as f:
        mention_rows = list(csv.DictReader(f))
    if not any(r.get("segment_id") == SEGMENT and r.get("candidate_id") == "cand-0158" for r in mention_rows):
        raise ValueError("Baglione candidate has no mention in the target segment")
    with CANDIDATES.open(encoding="utf-8-sig", newline="") as f:
        candidate_ids = {r["candidate_id"] for r in csv.DictReader(f)}
    if "cand-0158" not in candidate_ids:
        raise ValueError("Missing Baglione candidate cand-0158")
    return "".join(lines).encode("utf-8"), found


def count_open(data: bytes) -> int:
    return sum(
        1
        for line in data.decode("utf-8").splitlines()
        if (lambda x: (x.get("qualifiers") or {}).get("relation_candidate") is True
        and (not x.get("subject_candidate_id") or not x.get("object_candidate_id")))(json.loads(line))
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    before = TABLE.read_bytes()
    after, _ = transform(before)
    print(f"table={TABLE.relative_to(ROOT)}")
    print(f"before_sha256={digest(before)}")
    print(f"after_sha256={digest(after)}")
    print(f"open_endpoints={count_open(before)}->{count_open(after)}")
    print("changes:")
    print(f"  {APSE}: retain open subject; add explicit reason for passive agent")
    print(f"  {PAINTER}: object (open)->cand-0158; link Baglione's unpaid-fee example")
    print(f"  {SCHEMES}: relation_candidate true->false; retain Haskell's attributed evaluation")

    if args.preview:
        return 0
    if BACKUP.exists():
        raise FileExistsError(f"Refusing to overwrite recovery copy: {BACKUP}")
    shutil.copy2(TABLE, BACKUP)
    temp = TABLE.with_suffix(TABLE.suffix + ".tmp")
    temp.write_bytes(after)
    temp.replace(TABLE)
    print(f"backup={BACKUP.relative_to(ROOT)}")
    print(f"applied_sha256={digest(TABLE.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
