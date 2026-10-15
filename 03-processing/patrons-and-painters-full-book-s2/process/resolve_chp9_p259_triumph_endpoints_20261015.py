from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge/tables/book-statements.jsonl"
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
BACKUP_SUFFIX = "bak-s2-chp9-p259-triumph-endpoints-20261015"
EXPECTED_HASH = "6578677eb73bda55f07272904d1c6a298e903cdfcf8956f68f6d6f43752d1a82"
SEGMENT_ID = "chp-9:09_CHP-9_intro:l188-200"
SEGMENT_HASH = "717631e0c86fc16769da90d83e6363ce28a3576fbe24c8be41eb46d2d6958d2b"
TARGETS = {
    "st-chp9-p259-triumph-depicts-arts-republic-history-fame": ("cand-4085", None),
    "st-chp9-p259-triumph-depicts-sages-and-warrior": ("cand-4085", None),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_open(row: dict[str, object]) -> bool:
    q = row.get("qualifiers") or {}
    return q.get("relation_candidate") is True and (not row.get("subject_candidate_id") or not row.get("object_candidate_id"))


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

    raw = STATEMENTS.read_bytes()
    if digest(raw) != EXPECTED_HASH:
        raise ValueError("Statement table changed since the p.259 review")
    segment = next((json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8").splitlines() if line.strip() and json.loads(line)["segment_id"] == SEGMENT_ID), None)
    if segment is None or segment.get("sha256") != SEGMENT_HASH:
        raise ValueError("The reviewed p.259 source segment changed")
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    before = endpoint_counts(rows)
    if before != (404, 251, 50, 103):
        raise ValueError(f"Unexpected pre-update endpoint counts: {before}")
    index = {row["statement_id"]: row for row in rows}
    if not set(TARGETS).issubset(index):
        raise ValueError("One or more p.259 Triumph statements are missing")
    for statement_id, endpoints in TARGETS.items():
        row = index[statement_id]
        if not is_open(row) or (row.get("subject_candidate_id"), row.get("object_candidate_id")) != endpoints:
            raise ValueError(f"Reviewed p.259 statement changed: {statement_id}")
        mentioned = (row.get("qualifiers") or {}).get("mentioned_candidate_ids") or []
        if "cand-8105" not in mentioned:
            raise ValueError(f"Expected Venetian State subject is not linked: {statement_id}")

    first = index["st-chp9-p259-triumph-depicts-arts-republic-history-fame"]
    first["object_candidate_id"] = "cand-8105"
    first["predicate"] = "triumph_of_venice_depicts_the_republic_with_allegorical_figures"
    first["qualifiers"]["claim"] = "Haskell describes the arts at Minerva's feet and the Republic's chariot with Doge Loredano surveyed by History and Fame in Batoni's Triumph of Venice."
    first["qualifiers"]["relation_candidate_note"] = (
        "The work-to-subject endpoint is the Venetian State represented by the Republic's chariot. "
        "The existing mentions preserve Minerva, the arts, Doge Loredano, History and Fame as iconographic details; do not infer relations among those figures."
    )
    first["qualifiers"].pop("open_endpoint_reason", None)

    second = index["st-chp9-p259-triumph-depicts-sages-and-warrior"]
    second["object_candidate_id"] = "cand-8105"
    second["predicate"] = "triumph_of_venice_exalts_the_venetian_state_through_mythological_figures"
    second["qualifiers"]["claim"] = "Haskell says the painting presents Venice's recorded achievements and present grandeur to Greek sages and a Roman warrior through Mercury and Neptune."
    second["qualifiers"]["relation_candidate_note"] = (
        "The work-to-subject endpoint is the Venetian State. The existing Greek sages, Mercury, Roman warrior and Neptune candidates record the iconographic arrangement; "
        "the unnamed figures remain generic and no edges between depicted figures are inferred."
    )
    second["qualifiers"].pop("open_endpoint_reason", None)

    after = endpoint_counts(rows)
    if after != (402, 249, 50, 103):
        raise ValueError(f"Unexpected post-update endpoint counts: {after}")
    changed = ("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)).encode("utf-8")
    print("reviewed=p.259 iconographic descriptions in Batoni's Triumph of Venice")
    print("resolved=2 work-to-subject relations -> Venetian State cand-8105; retained depicted figures as details, without figure-to-figure edges")
    print(f"statements={len(rows)}; open_endpoints={before}->{after}")
    print(f"book-statements.jsonl sha256 {digest(raw)}->{digest(changed)}")
    if args.preview:
        return 0

    backup = STATEMENTS.with_name(f"{STATEMENTS.name}.{BACKUP_SUFFIX}")
    temporary = STATEMENTS.with_name(f"{STATEMENTS.name}.tmp-{BACKUP_SUFFIX}")
    if backup.exists() or temporary.exists():
        raise FileExistsError("p.259 recovery or temporary file already exists")
    shutil.copy2(STATEMENTS, backup)
    try:
        temporary.write_bytes(changed)
        temporary.replace(STATEMENTS)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        shutil.copy2(backup, STATEMENTS)
        raise
    print(f"backup={backup.relative_to(ROOT)}")
    print(f"applied_sha256={STATEMENTS.relative_to(ROOT)}:{digest(STATEMENTS.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
