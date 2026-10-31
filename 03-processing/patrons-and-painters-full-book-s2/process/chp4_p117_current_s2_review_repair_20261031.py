"""Apply the verified p.117 S2 wording and quote repairs from the independent review.

Default mode is a preconditioned dry run. Use --apply only after inspecting the diff.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
BACKUP = TABLE.with_name(
    "book-statements.jsonl.bak-s2-chp4-p117-current-review-20261031"
)

UPDATES = {
    "st-chp4-sec-ii-p117-mood-and-moral-reading": {
        "qualifiers.claim": (
            "Haskell says the paintings’ melancholy mood suited Massimi’s career and quotes one as warning against greed for riches, the other against transient pleasure.",
            "Haskell says the pair’s melancholy mood, if not actually moral, was particularly appropriate to the circumstances of Massimi’s own chequered career; he interprets King Midas as warning against a mad desire for riches and the first Arcadian Shepherds as warning against thoughtless enjoyment of pleasures soon to be ended.",
        ),
    },
    "st-chp4-sec-ii-p117-poussin-library-visits": {
        "qualifiers.claim": (
            "Haskell says Poussin must have visited Massimi’s library while working on his late paintings.",
            "Haskell infers that Poussin must have made many visits to Massimi’s library while working on the increasingly abstruse pictures of his final years.",
        ),
    },
    "st-chp4-sec-ii-p117-bellori-anecdote": {
        "original_quote": (
            "Poussin showing Massimi downstairs late one night",
            "Bellori gives us a charming picture of Poussin showing Massimi downstairs late one night",
        ),
    },
    "st-chp4-sec-ii-p117-studio-conversation": {
        "original_quote": (
            "after they had been talking together in his studio",
            "Bellori gives us a charming picture of Poussin showing Massimi downstairs late one night after they had been talking together in his studio",
        ),
    },
    "st-chp4-sec-ii-p117-cassiano-visits": {
        "original_quote": (
            "whom he had known",
            "Cassiano dal Pozzo whom he had known",
        ),
    },
    "st-chp4-sec-ii-p117-cassiano-accompanied-on-visits": {
        "original_quote": (
            "and accompanied on his visits to connoisseurs",
            "Cassiano dal Pozzo whom he had known and accompanied on his visits to connoisseurs",
        ),
    },
}


def get_path(record: dict, dotted: str) -> tuple[dict, str]:
    bits = dotted.split(".")
    parent = record
    for bit in bits[:-1]:
        parent = parent[bit]
    return parent, bits[-1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    original = TABLE.read_bytes()
    lines = original.splitlines(keepends=True)
    found: set[str] = set()
    patched: list[bytes] = []
    changes: list[tuple[str, str, str, str]] = []

    for raw_line in lines:
        ending = b"\r\n" if raw_line.endswith(b"\r\n") else b"\n" if raw_line.endswith(b"\n") else b""
        payload = raw_line[: -len(ending)] if ending else raw_line
        record = json.loads(payload.decode("utf-8"))
        statement_id = record.get("statement_id")
        updates = UPDATES.get(statement_id)
        if not updates:
            patched.append(raw_line)
            continue
        if statement_id in found:
            raise SystemExit(f"duplicate statement_id: {statement_id}")
        found.add(statement_id)
        for dotted, (expected, replacement) in updates.items():
            parent, key = get_path(record, dotted)
            actual = parent[key]
            if actual != expected:
                raise SystemExit(
                    f"precondition failed for {statement_id} {dotted}: {actual!r}"
                )
            parent[key] = replacement
            changes.append((statement_id, dotted, expected, replacement))
        patched.append(
            json.dumps(record, ensure_ascii=False).encode("utf-8") + ending
        )

    missing = sorted(set(UPDATES) - found)
    if missing:
        raise SystemExit(f"missing statement IDs: {missing}")
    result = b"".join(patched)

    print(f"statements={len(found)} field_changes={len(changes)}")
    for statement_id, field, before, after in changes:
        print(f"{statement_id} | {field}\n  before: {before}\n  after:  {after}")
    if not args.apply:
        print("DRY RUN: no files written")
        return 0
    if BACKUP.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {BACKUP}")
    shutil.copy2(TABLE, BACKUP)
    temp = TABLE.with_suffix(TABLE.suffix + ".tmp")
    temp.write_bytes(result)
    temp.replace(TABLE)
    print(f"backup={BACKUP}")
    print(f"table={TABLE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
