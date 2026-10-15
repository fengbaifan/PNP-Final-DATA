from __future__ import annotations

import argparse
import collections
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
BACKUP = TABLE.with_name(
    TABLE.name + ".bak-s2-handoff-caption-relations-20261010"
)
EXPECTED_TABLE_SHA256 = (
    "da2574e97f3d42e85978f041847263f5e52ea5af3091762267bf9e2e5e073fe2"
)
EXPECTED_BY_PREDICATE = {
    "caption_attribution": 156,
    "caption_location_or_collection": 151,
    "caption_iconographic_subject": 56,
    "caption_subject": 45,
    "caption_depiction": 14,
    "caption_title_subject": 10,
    "caption_depicts_person": 7,
    "caption_bibliographic_imprint": 6,
    "caption_subject_group": 5,
    "caption_title_setting": 5,
    "caption_design_attribution": 4,
    "caption_work_context": 4,
    "caption_title_context": 3,
    "caption_architectural_space": 2,
    "caption_location_history": 2,
    "caption_names_as_author": 2,
    "caption_painted_for": 2,
    "caption_spatial_context": 2,
    "caption_title_reference": 2,
    "caption_acquisition_credit": 1,
    "caption_depiction_as_pope_urban_viii": 1,
    "caption_depiction_as_young_prelate": 1,
    "caption_depicts_episode": 1,
    "caption_depicts_tomb_of": 1,
    "caption_detail_of": 1,
    "caption_engraver_attribution": 1,
    "caption_identifies_endpiece_of_edition": 1,
    "caption_identifies_frontispiece_of": 1,
    "caption_locates_tomb_at": 1,
    "caption_location_or_component": 1,
    "caption_proposed_location": 1,
    "caption_reproduction_permission": 1,
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def prepare() -> tuple[bytes, bytes, list[str]]:
    original = TABLE.read_bytes()
    actual_hash = sha256(original)
    if actual_hash != EXPECTED_TABLE_SHA256:
        raise SystemExit(
            f"table hash changed: expected {EXPECTED_TABLE_SHA256}, got {actual_hash}"
        )

    lines = original.decode("utf-8").splitlines(keepends=True)
    parsed = [json.loads(line) for line in lines if line.strip()]
    candidate_rows = [
        row
        for row in parsed
        if row.get("subject_candidate_id")
        and row.get("object_candidate_id")
        and row["predicate"].startswith("caption_")
        and "relation_candidate" not in (row.get("qualifiers") or {})
    ]
    by_predicate = collections.Counter(row["predicate"] for row in candidate_rows)
    if dict(by_predicate) != EXPECTED_BY_PREDICATE:
        raise SystemExit(
            "caption relation classification inventory changed: "
            f"{dict(sorted(by_predicate.items()))!r}"
        )
    candidate_ids = {
        row["statement_id"]: row for row in candidate_rows
    }
    if len(candidate_ids) != len(candidate_rows):
        raise SystemExit("selected statement IDs are not unique")
    for row in candidate_rows:
        q = row.get("qualifiers") or {}
        if row.get("origin") != "book":
            raise SystemExit(f"non-book statement selected: {row['statement_id']}")
        if not row.get("original_quote") or not row.get("source_file"):
            raise SystemExit(f"missing source anchor: {row['statement_id']}")
        if not q.get("source_line_start") or not q.get("source_line_end"):
            raise SystemExit(f"missing source line range: {row['statement_id']}")
        if not row.get("subject_candidate_id") or not row.get("object_candidate_id"):
            raise SystemExit(f"missing endpoint: {row['statement_id']}")

    replacements: dict[str, str] = {}
    updated_lines: list[str] = []
    for line in lines:
        if not line.strip():
            updated_lines.append(line)
            continue
        row = json.loads(line)
        if row.get("statement_id") in candidate_ids:
            row["qualifiers"]["relation_candidate"] = True
            replacements[row["statement_id"]] = row["predicate"]
            updated_lines.append(
                json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
            )
        else:
            updated_lines.append(line)

    if set(replacements) != set(candidate_ids):
        raise SystemExit("not all selected records were replaced exactly once")
    result = "".join(updated_lines).encode("utf-8")
    final_rows = [
        json.loads(line) for line in result.decode("utf-8").splitlines() if line.strip()
    ]
    flagged = [
        row
        for row in final_rows
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
    ]
    if len(flagged) != 3300:
        raise SystemExit(f"expected 3300 flagged relation candidates, got {len(flagged)}")
    complete = sum(
        bool(row.get("subject_candidate_id") and row.get("object_candidate_id"))
        for row in flagged
    )
    if complete != 3286:
        raise SystemExit(f"expected 3286 complete endpoints, got {complete}")
    return original, result, sorted(replacements)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    original, result, selected_ids = prepare()
    print(
        json.dumps(
            {
                "mode": "apply" if args.apply else "dry-run",
                "selected_statement_count": len(selected_ids),
                "predicate_count": len(EXPECTED_BY_PREDICATE),
                "expected_relation_candidate_total_after": 3300,
                "expected_complete_relation_candidates_after": 3286,
                "expected_open_relation_candidates_after": 14,
                "before_sha256": sha256(original),
                "after_sha256": sha256(result),
                "write": args.apply,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if not args.apply:
        return
    if BACKUP.exists():
        raise SystemExit(f"recovery copy already exists: {BACKUP}")
    shutil.copy2(TABLE, BACKUP)
    if sha256(BACKUP.read_bytes()) != sha256(original):
        raise SystemExit("recovery copy does not match the preimage")
    TABLE.write_bytes(result)
    if sha256(TABLE.read_bytes()) != sha256(result):
        TABLE.write_bytes(original)
        raise SystemExit("post-write hash mismatch; original bytes restored")
    print(f"backup={BACKUP}")
    print(f"applied_sha256={sha256(result)}")


if __name__ == "__main__":
    main()
