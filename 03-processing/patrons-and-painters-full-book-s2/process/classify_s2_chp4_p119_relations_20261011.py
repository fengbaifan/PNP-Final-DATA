from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "02-sources/02-Markdown/04_CHP-4_sec_ii.md"
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp4-p119-relations-20261011")
EXPECTED_SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
EXPECTED_TABLE_SHA256 = "85a9ac11e3fef23c087b6f488ef0a71523131cdeb7ba354d21236ca23b9df76b"
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l229-230"

DECISIONS = {
    "st-chp4-sec-ii-p119-antiquity-and-contemporary-painting": (
        False,
        "Authorial compatibility argument about classical antiquity and contemporary painting; it does not assert a relation between two identified entity endpoints.",
        None,
    ),
    "st-chp4-sec-ii-p119-carried-principles-forward": (
        True,
        "Records Massimi as carrying the principles of Giustiniani and Cassiano into Baroque art. The source does not identify the principles more narrowly; the Baroque art term is the explicit destination.",
        "cand-4132",
    ),
    "st-chp4-sec-ii-p119-friend-cassiano": (
        True,
        "Explicit person-to-person friendship as stated by Haskell; remains an S2 candidate, not an S6 edge.",
        None,
    ),
    "st-chp4-sec-ii-p119-learning-and-inspiration": (
        False,
        "Concluding authorial argument that learning and creative inspiration are compatible; no inter-entity relation is asserted.",
        None,
    ),
    "st-chp4-sec-ii-p119-masterpieces-by-three-artists": (
        False,
        "The works are used as evidence for Haskell's aesthetic argument; no specific work group or entity-to-entity relation is identified in this sentence.",
        None,
    ),
    "st-chp4-sec-ii-p119-opulence-pedantry": (
        False,
        "Scalar authorial evaluation of opulence and pedantry as traits of the period, not a relation between identified entities.",
        None,
    ),
    "st-chp4-sec-ii-p119-relation-vincenzo-giustiniani": (
        True,
        "Explicit but unspecified kin relationship between Massimi and Vincenzo Giustiniani; no particular degree of kinship is inferred.",
        None,
    ),
    "st-chp4-sec-ii-p119-tradition-survival": (
        False,
        "Broad authorial periodization of a patronage tradition and its renewal; the sentence does not identify a binary relation between the recorded person and period endpoints.",
        None,
    ),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Classify the eight p.119 S2 statements after source and endpoint review.")
    parser.add_argument("--apply", action="store_true", help="write the guarded statement update and preserve a recovery copy")
    args = parser.parse_args()

    if digest(SOURCE) != EXPECTED_SOURCE_SHA256:
        raise SystemExit("source SHA-256 changed; stop and review the affected source")
    if digest(TABLE) != EXPECTED_TABLE_SHA256:
        raise SystemExit("statement table SHA-256 changed; stop and rebuild the review from current data")
    if args.apply and BACKUP.exists():
        raise SystemExit(f"recovery copy already exists: {BACKUP}")

    original = TABLE.read_bytes()
    has_bom = original.startswith(b"\xef\xbb\xbf")
    text = original.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    output_lines: list[str] = []
    found: dict[str, dict] = {}

    for raw_line in text.splitlines(keepends=True):
        line = raw_line.rstrip("\r\n")
        ending = raw_line[len(line):]
        if not line.strip():
            output_lines.append(raw_line)
            continue
        row = json.loads(line)
        statement_id = row.get("statement_id")
        if statement_id in DECISIONS:
            if row.get("segment_id") != SEGMENT_ID:
                raise SystemExit(f"unexpected segment for {statement_id}: {row.get('segment_id')}")
            qualifiers = row.get("qualifiers") or {}
            if "relation_candidate" in qualifiers:
                raise SystemExit(f"statement already classified: {statement_id}")
            is_relation, note, target_id = DECISIONS[statement_id]
            if target_id:
                if row.get("object_candidate_id") is not None:
                    raise SystemExit(f"expected open object endpoint for {statement_id}")
                if target_id not in qualifiers.get("mentioned_candidate_ids", []):
                    raise SystemExit(f"target is not mentioned in the statement: {statement_id}")
                row["object_candidate_id"] = target_id
            qualifiers["relation_candidate"] = is_relation
            qualifiers["relation_candidate_note"] = note
            row["qualifiers"] = qualifiers
            found[statement_id] = row
            line = json.dumps(row, ensure_ascii=False)
            ending = ending or newline
        output_lines.append(line + ending)

    if set(found) != set(DECISIONS):
        missing = sorted(set(DECISIONS) - set(found))
        raise SystemExit(f"target statement set mismatch; missing: {missing}")

    updated = (b"\xef\xbb\xbf" if has_bom else b"") + "".join(output_lines).encode("utf-8")
    print(f"target statements: {len(found)}")
    print("classification: 3 relation candidates, 5 non-relational claims")
    print("new endpoint: carried-principles-forward -> Baroque art in Italy (cand-4132)")
    for statement_id, row in found.items():
        q = row.get("qualifiers") or {}
        print(f"{statement_id}: relation_candidate={q['relation_candidate']}; endpoints={row.get('subject_candidate_id')} -> {row.get('object_candidate_id')}")
    if not args.apply:
        print("dry-run only; no files written")
        return 0

    shutil.copy2(TABLE, BACKUP)
    temp = TABLE.with_suffix(TABLE.suffix + ".tmp-p119-review")
    temp.write_bytes(updated)
    temp.replace(TABLE)
    print(f"applied; recovery copy: {BACKUP.name}")
    print(f"new statement SHA-256: {digest(TABLE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
