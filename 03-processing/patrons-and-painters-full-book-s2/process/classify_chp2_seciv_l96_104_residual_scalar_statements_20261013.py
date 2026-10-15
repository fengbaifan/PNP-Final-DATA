from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-chp2-seciv-l96-104-residual-scalars-20261013")
REASONS = {
    "st-chp2-seciv-l96-104-appeal-not-taken-seriously": (
        "This records Haskell's account of how the plea was received. The preceding letters to all Barberini do not explicitly identify the scope of 'no one' as a distinct relation endpoint; retain the reception statement without asserting a family-level relation."
    ),
    "st-chp2-seciv-l96-104-ceiling-single-fresco": (
        "This is a formal description of the ceiling's composition (one continuous fresco rather than compartments), not a relation between distinct entities."
    ),
    "st-chp2-seciv-l96-104-grandeur-awe-effect": (
        "This is Haskell's characterization of the fresco's effect on a generic visitor; no independently identified viewer or audience entity is asserted."
    ),
    "st-chp2-seciv-l96-104-montagu-interpretation-as-end": (
        "This preserves Montagu's reported scholarly interpretation about seventeenth-century writers; the generalized class and interpretive proposition are not a formal relation between identified entities."
    ),
    "st-chp2-seciv-l96-104-painted-frame-defied": (
        "This describes an internal compositional feature of the same fresco, not a relation between distinct entities."
    ),
    "st-chp2-seciv-l96-104-vitzthum-further-citation": (
        "This is a bibliographic pointer to Vitzthum's article. Citation records remain in the statement table but are not historical or domain-relation candidates."
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
    tmp = TABLE.with_suffix(TABLE.suffix + ".tmp-s2-residual-scalars")
    tmp.write_text(rendered, encoding="utf-8")
    tmp.replace(TABLE)
    print(f"mode=apply; backup={BACKUP.name}; new_sha256={digest(TABLE)}")


if __name__ == "__main__":
    main()
