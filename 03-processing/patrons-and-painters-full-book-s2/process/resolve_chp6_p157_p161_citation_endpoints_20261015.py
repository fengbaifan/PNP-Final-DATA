from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE_DIR = ROOT / "04-knowledge/tables"
STATEMENTS = TABLE_DIR / "book-statements.jsonl"
CANDIDATES = TABLE_DIR / "entity-candidates.csv"
MENTIONS = TABLE_DIR / "mentions.csv"
SEGMENTS = TABLE_DIR / "segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/06_CHP-6_sec_iv.md"
SEGMENT_ID = "chp-6:06_CHP-6_sec_iv:l55-72"
SOURCE_SHA256 = "65de7b08cd2bad4cbf783d807160ef15e80cb031a47e1f28a6cb6c0f2b29e775"
SEGMENT_SHA256 = "7c0d7c8e22fe0cbf4dde57a5eeada3874d54f83267412c7a8cc75d793e350aa6"
EXPECTED_STATEMENTS_SHA256 = "8daf5eb2cf51b7aa4a91bad73f560122d9c195b69632516cdb052516214265db"
BACKUP = STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp6-p157-p161-citation-endpoints-20261015")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_open(row: dict) -> bool:
    q = row.get("qualifiers") or {}
    return q.get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = STATEMENTS.read_bytes()
    if digest(raw) != EXPECTED_STATEMENTS_SHA256:
        raise ValueError(f"protected statement table changed: {digest(raw)}")
    if digest(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise ValueError("chapter 6 source asset changed")
    segment_map = {
        row["segment_id"]: row
        for row in (
            json.loads(line)
            for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines()
            if line.strip()
        )
    }
    segment = segment_map.get(SEGMENT_ID)
    if not segment or segment.get("sha256") != SEGMENT_SHA256 or segment.get("asset_sha256") != SOURCE_SHA256:
        raise ValueError("reviewed chapter 6 p.157–161 note segment changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[54:72])
    if digest(segment_text.encode("utf-8")) != SEGMENT_SHA256:
        raise ValueError("chapter 6 p.157–161 source text changed")
    quotes = ["1 Spon and Wilder, I, p. 232.", "1 Pascoli, I, p. 124, and II, pp. 119 and 290."]
    if any(q not in segment_text for q in quotes):
        raise ValueError("the reviewed note text changed")

    statements = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in statements}
    spon = by_id.get("st-chp6-p157-note1-source")
    pascoli = by_id.get("st-chp6-p161-note1-pascoli-canini")
    if not spon or not pascoli:
        raise ValueError("expected p.157 / p.161 footnote statements are missing")
    if spon.get("subject_candidate_id") or spon.get("object_candidate_id") != "cand-6395":
        raise ValueError("p.157 Spon/Wheler citation row changed")
    if pascoli.get("subject_candidate_id") != "cand-0530" or pascoli.get("object_candidate_id"):
        raise ValueError("p.161 Pascoli citation row changed")
    if (pascoli.get("qualifiers") or {}).get("relation_candidate") is not True:
        raise ValueError("p.161 footnote is no longer classified as a relation candidate")

    candidate_ids = {row["candidate_id"] for row in __import__("csv").DictReader(CANDIDATES.open(encoding="utf-8-sig", newline=""))}
    for candidate_id in ("cand-2962", "cand-6395", "cand-4834", "cand-4552"):
        if candidate_id not in candidate_ids:
            raise ValueError(f"required archive candidate is missing: {candidate_id}")
    new_id = "st-chp6-p161-note1-pascoli-canini-vol-ii"
    if new_id in by_id:
        raise ValueError(f"statement ID already exists: {new_id}")

    open_before = sum(is_open(row) for row in statements)
    no_reason_before = sum(
        is_open(row) and not (row.get("qualifiers") or {}).get("open_endpoint_reason") for row in statements
    )
    true_before = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in statements)
    false_before = sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in statements)
    if (open_before, no_reason_before, true_before, false_before, len(statements)) != (377, 56, 10397, 4753, 15150):
        raise ValueError("unexpected pre-edit S2 statement counts")

    spon["subject_candidate_id"] = "cand-2962"
    spon_q = spon["qualifiers"]
    spon_q["mentioned_candidate_ids"] = list(dict.fromkeys(
        spon_q.get("mentioned_candidate_ids", []) + ["cand-2962"]
    ))
    spon_q["relation_candidate_note"] = "The citing entity is the accepted Haskell book candidate (cand-2962); this preserves the source's bibliographic pointer without claiming the cited p.232 was read."
    spon_q.pop("open_endpoint_reason", None)

    pascoli["subject_candidate_id"] = "cand-2962"
    pascoli["object_candidate_id"] = "cand-4834"
    pascoli["predicate"] = "cites"
    pascoli["original_quote"] = "1 Pascoli, I, p. 124"
    pascoli_q = pascoli["qualifiers"]
    pascoli_q["claim"] = "Haskell's p.161 note 1 cites Pascoli, volume I, page 124, in the adjacent Canini discussion."
    pascoli_q["mentioned_candidate_ids"] = list(dict.fromkeys(
        pascoli_q.get("mentioned_candidate_ids", []) + ["cand-2962"]
    ))
    pascoli_q["relation_candidate_note"] = "This is a bibliographic citation link from Haskell's book to Pascoli's volume I; the cited page was not independently consulted."
    pascoli_q.pop("open_endpoint_reason", None)

    pascoli_vol_ii = copy.deepcopy(pascoli)
    pascoli_vol_ii["statement_id"] = new_id
    pascoli_vol_ii["object_candidate_id"] = "cand-4552"
    pascoli_vol_ii["original_quote"] = "II, pp. 119 and 290"
    pascoli_vol_ii["qualifiers"] = copy.deepcopy(pascoli_q)
    pascoli_vol_ii["qualifiers"]["claim"] = "Haskell's p.161 note 1 also cites Pascoli, volume II, pages 119 and 290, in the adjacent Canini discussion."
    pascoli_vol_ii["qualifiers"]["mentioned_candidate_ids"] = list(dict.fromkeys(
        pascoli_vol_ii["qualifiers"].get("mentioned_candidate_ids", []) + ["cand-4552"]
    ))
    pascoli_vol_ii["qualifiers"]["relation_candidate_note"] = "This is a separate bibliographic citation link to Pascoli's volume II; the cited pages were not independently consulted."
    statements.append(pascoli_vol_ii)

    open_after = sum(is_open(row) for row in statements)
    no_reason_after = sum(
        is_open(row) and not (row.get("qualifiers") or {}).get("open_endpoint_reason") for row in statements
    )
    true_after = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in statements)
    if (open_after, no_reason_after, true_after, len(statements)) != (375, 54, 10398, 15151):
        raise ValueError(f"unexpected resulting S2 statement state: {(open_after, no_reason_after, true_after, len(statements))}")

    output = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in statements).encode("utf-8")
    print("reviewed=chapter 6 p.157 note 1 and p.161 note 1; resolved citation source and split Pascoli volume locators")
    print("changes=2 existing source-book endpoints completed, 1 composite two-volume citation split into an atomic second statement")
    print(f"open_endpoints={open_before}->{open_after}; open_without_reason={no_reason_before}->{no_reason_after}; relation_true={true_after}")
    print(f"book-statements.jsonl sha256 {digest(raw)}->{digest(output)}")
    if args.preview:
        return 0

    if BACKUP.exists():
        raise FileExistsError(f"recovery copy already exists: {BACKUP.name}")
    temp = STATEMENTS.with_name(STATEMENTS.name + ".tmp-s2-chp6-p157-p161-citation-endpoints-20261015")
    if temp.exists():
        raise FileExistsError(f"protected temporary output already exists: {temp.name}")
    shutil.copy2(STATEMENTS, BACKUP)
    try:
        temp.write_bytes(output)
        temp.replace(STATEMENTS)
    except Exception:
        if temp.exists():
            temp.unlink()
        shutil.copy2(BACKUP, STATEMENTS)
        raise
    print(f"backup={BACKUP.name}")
    print(f"applied_hash={digest(STATEMENTS.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
