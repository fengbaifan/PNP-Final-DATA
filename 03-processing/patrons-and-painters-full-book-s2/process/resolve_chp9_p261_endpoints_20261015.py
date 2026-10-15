from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-chp9-p261-20261015")
EXPECTED_TABLE_HASH = "ed4444c6f6b3c942f883e3841c29436f7b3470afa7de1108735682d05152708d"
SEGMENT_HASHES = {
    "chp-9:09_CHP-9_intro:l212-216": "e94cea1632b183f4153ca8a3fef9cba2f227692c01e4c904a018c000303fa97b",
    "chp-9:09_CHP-9_intro:l323-445": "51cc706d49319744d5efe4ed0c2528e68a2a3e1d82d75b14961092f0c36eebfc",
}
REVIEWED_IDS = {
    "st-chp9-p261-important-families-lost-wealth",
    "st-chp9-p261-traveller-wall-display-quotation",
    "st-chp9-p261-wealth-restricted-inner-group",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_open(row: dict[str, object]) -> bool:
    q = row.get("qualifiers") or {}
    return q.get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def endpoint_counts(rows: list[dict[str, object]]) -> tuple[int, int, int, int]:
    opens = [row for row in rows if is_open(row)]
    object_only = sum(bool(row.get("subject_candidate_id")) and not row.get("object_candidate_id") for row in opens)
    subject_only = sum(not row.get("subject_candidate_id") and bool(row.get("object_candidate_id")) for row in opens)
    both = sum(not row.get("subject_candidate_id") and not row.get("object_candidate_id") for row in opens)
    return len(opens), object_only, subject_only, both


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = TABLE.read_bytes()
    if digest(raw) != EXPECTED_TABLE_HASH:
        raise ValueError("book-statements.jsonl changed since the p.261 review was prepared")
    segments = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment_index = {row["segment_id"]: row for row in segments}
    for segment_id, expected_hash in SEGMENT_HASHES.items():
        segment = segment_index.get(segment_id)
        if segment is None or segment.get("sha256") != expected_hash:
            raise ValueError(f"Reviewed p.261 source segment changed: {segment_id}")

    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    index = {row["statement_id"]: row for row in rows}
    if not REVIEWED_IDS.issubset(index):
        raise ValueError("One or more p.261 reviewed statements are missing")
    if endpoint_counts(rows) != (400, 251, 49, 100):
        raise ValueError(f"Unexpected global open-endpoint counts: {endpoint_counts(rows)}")
    for statement_id in REVIEWED_IDS:
        if not is_open(index[statement_id]):
            raise ValueError(f"Reviewed p.261 statement is no longer open: {statement_id}")

    families = index["st-chp9-p261-important-families-lost-wealth"]
    families["qualifiers"]["relation_candidate"] = False
    families["qualifiers"]["relation_candidate_note"] = "This is an attributed historical claim about an unnamed group's economic condition. 'Wealth' is an attribute, not a separately identified entity endpoint; preserve Haskell's wording as a claim rather than inventing an object."
    families["qualifiers"].pop("open_endpoint_reason", None)

    traveller = index["st-chp9-p261-traveller-wall-display-quotation"]
    traveller["subject_candidate_id"] = "cand-8522"
    traveller["predicate"] = "travel_account_described_venetian_picture_display"
    traveller["qualifiers"]["speaker"] = "Unnamed English woman, quoted by Haskell from the travel account cited in note 1"
    traveller["qualifiers"]["mentioned_candidate_ids"] = list(dict.fromkeys(
        (traveller["qualifiers"].get("mentioned_candidate_ids") or []) + ["cand-8522"]
    ))
    traveller["qualifiers"]["cross_reference_segments"] = [
        {
            "segment_id": "chp-9:09_CHP-9_intro:l323-445",
            "source_line_start": 404,
            "source_line_end": 404,
        }
    ]
    traveller["qualifiers"]["relation_candidate_note"] = "Note 1 identifies the cited source as the travel account Letters from Italy, volume III, page 274, by an unnamed English woman. The publication is the source endpoint for Haskell's quotation; neither the account nor its broad generalization was independently consulted."
    traveller["qualifiers"].pop("open_endpoint_reason", None)

    wealth = index["st-chp9-p261-wealth-restricted-inner-group"]
    wealth["qualifiers"]["relation_candidate"] = False
    wealth["qualifiers"]["relation_candidate_note"] = "Haskell's sentence states an attributed distribution trend already represented by the source-defined term candidate. The 'small inner group' is not independently identified, so retain the proposition and its uncertainty without inventing a second group endpoint."
    wealth["qualifiers"].pop("open_endpoint_reason", None)

    after = endpoint_counts(rows)
    if after != (397, 249, 48, 100):
        raise ValueError(f"Unexpected post-review global open-endpoint counts: {after}")
    statement_after = ("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)).encode("utf-8")

    print("reviewed=p.261 traveller quotation and wealth-distribution claims")
    print("resolved=travel-account source attributed through note 1; two broad economic claims retained as non-edge propositions")
    print("open=p.261 none")
    print(f"statements={len(rows)}; open_endpoints={endpoint_counts([json.loads(line) for line in raw.decode('utf-8-sig').splitlines() if line.strip()])}->{after}")
    print(f"book-statements.jsonl sha256 {digest(raw)}->{digest(statement_after)}")
    if args.preview:
        return 0
    if BACKUP.exists():
        raise FileExistsError(f"Recovery copy already exists: {BACKUP.name}")
    temporary = TABLE.with_name("book-statements.jsonl.tmp-s2-chp9-p261-20261015")
    if temporary.exists():
        raise FileExistsError(f"Temporary file already exists: {temporary.name}")
    shutil.copy2(TABLE, BACKUP)
    try:
        temporary.write_bytes(statement_after)
        temporary.replace(TABLE)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        shutil.copy2(BACKUP, TABLE)
        raise
    print(f"backup={BACKUP.relative_to(ROOT)}")
    print(f"applied_sha256={digest(TABLE.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
