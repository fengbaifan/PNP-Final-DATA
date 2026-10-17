from __future__ import annotations

import argparse
from pathlib import Path

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
ALIGNMENT = ROOT / "04-knowledge" / "tables" / "alignment.csv"
OLD = "S3 cross-chapter identity review 2026-10-16: new group=sg3-person-ludovico-ariosto. "
NEW = "S3 cross-chapter identity review 2026-10-16; group=sg3-person-ludovico-ariosto; "


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize the parseable group token on cand-0116's S3 alignment row.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    fields, rows = sync.read_csv(ALIGNMENT)
    target = next(row for row in rows if row.get("candidate_id") == "cand-0116" and not row.get("external_source"))
    assert target["decision"] == "new" and not target.get("ku_id")
    assert OLD in target["resolution_note"]
    planned = [dict(row) for row in rows]
    row = next(item for item in planned if item.get("candidate_id") == "cand-0116" and not item.get("external_source"))
    row["resolution_note"] = row["resolution_note"].replace(OLD, NEW, 1)
    assert sync.get_group(row["resolution_note"]) == "sg3-person-ludovico-ariosto"

    if args.dry_run:
        print("cand-0116 S3 group token dry-run passed; group parsing returns sg3-person-ludovico-ariosto")
        return 0
    sync.write_csv(ALIGNMENT, fields, planned)
    print("normalized cand-0116 S3 group token; decision and evidence were preserved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
