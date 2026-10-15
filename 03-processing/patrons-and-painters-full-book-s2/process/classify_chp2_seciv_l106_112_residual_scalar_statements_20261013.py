from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-chp2-seciv-l106-112-residual-scalars-20261013")
REASONS = {
    "st-chp2-seciv-l106-112-haskell-accepts-domenichino-reading": (
        "This is Haskell's qualified assessment of Domenichino's reported interpretation. The sentence identifies no additional entity or independently expressible relation endpoint."
    ),
    "st-chp2-seciv-l106-112-romanelli-painting-assessed": (
        "This is Haskell's critical assessment of Romanelli's changing style, not a relation between distinct entities."
    ),
    "st-chp2-seciv-l106-112-romanelli-reliable-rewarded": (
        "This combines an authorial reliability judgment with a general report of pensions and honours. No particular award, grantor, or other relation endpoint is identified, so the source claim remains narrative rather than a formal relation candidate."
    ),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--expected-sha256")
    args = parser.parse_args()

    before = digest(TABLE)
    if args.expected_sha256 and before != args.expected_sha256:
        raise SystemExit(f"stale table hash: expected {args.expected_sha256}, got {before}")

    lines = TABLE.read_text(encoding="utf-8-sig").splitlines()
    rows = [json.loads(line) for line in lines]
    target_rows = {row.get("statement_id"): i for i, row in enumerate(rows) if row.get("statement_id") in REASONS}
    if set(target_rows) != set(REASONS):
        raise SystemExit(f"target mismatch: expected {sorted(REASONS)}, got {sorted(target_rows)}")

    for statement_id, reason in REASONS.items():
        index = target_rows[statement_id]
        row = rows[index]
        qualifiers = row.get("qualifiers")
        if not isinstance(qualifiers, dict) or qualifiers.get("relation_candidate") is not None:
            raise SystemExit(f"expected unset relation_candidate: {statement_id}")
        qualifiers["relation_candidate"] = False
        qualifiers["relation_candidate_note"] = reason
        lines[index] = json.dumps(row, ensure_ascii=False)
        print(f"{statement_id}: false — {reason}")

    rendered = "\n".join(lines) + "\n"
    print(f"table_sha256={before}")
    if not args.apply:
        print("mode=preview; no files changed")
        return
    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")
    shutil.copy2(TABLE, BACKUP)
    tmp = TABLE.with_suffix(TABLE.suffix + ".tmp-s2-chp2-l106-112")
    tmp.write_text(rendered, encoding="utf-8")
    tmp.replace(TABLE)
    print(f"mode=apply; backup={BACKUP.name}; new_sha256={digest(TABLE)}")


if __name__ == "__main__":
    main()
