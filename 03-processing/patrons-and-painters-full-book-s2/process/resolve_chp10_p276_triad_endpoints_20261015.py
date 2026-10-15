from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE_DIR = ROOT / "04-knowledge/tables"
STATEMENTS = TABLE_DIR / "book-statements.jsonl"
CANDIDATES = TABLE_DIR / "entity-candidates.csv"
MENTIONS = TABLE_DIR / "mentions.csv"
SOURCE = ROOT / "02-sources/02-Markdown/10_CHP-10_intro.md"
SEGMENT_ID = "chp-10:10_CHP-10_intro:l3-13"
SEGMENT_SHA256 = "2b86f1b920d1aa7de55b2ba8f511e3c8ec71b8c546387f71da2113d40e197e92"
SOURCE_SHA256 = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_HASHES = {
    STATEMENTS: "f00b14a885227f0b394315d3b4c8347feefd2e135a8925d9fd2412f366c7327b",
    CANDIDATES: "29123c116e225707201042712915b5b634513b70a82739a974ee1625a6ebf1fa",
    MENTIONS: "5068be683d6dd012d36ac27117675545007f7afe9f1700af26f7d538e99e6af0",
}
BACKUPS = {
    STATEMENTS: STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp10-p276-triad-endpoints-20261015"),
    CANDIDATES: CANDIDATES.with_name("entity-candidates.csv.bak-s2-chp10-p276-triad-endpoints-20261015"),
    MENTIONS: MENTIONS.with_name("mentions.csv.bak-s2-chp10-p276-triad-endpoints-20261015"),
}

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-12404",
        "index_entry_id": "",
        "canonical_name": "State, nobles, and Church as the three traditional patronage source categories (p.276)",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell's source-defined collective antecedent for 'All three'. Its members are the State (cand-8831), nobles (cand-8677), and Church (cand-8672), treated as three patronage categories rather than a unified institution; no individual members are specified.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L7",
    },
    {
        "candidate_id": "cand-12405",
        "index_entry_id": "",
        "canonical_name": "Traditional artistic patronage in Venice in the first part of the eighteenth century (p.276)",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "The time-bounded patronage context in Haskell's account, where the State, nobles, and Church are called traditional sources. 'First part' is retained without converting it to a narrower date range.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L6",
    },
]

NEW_MENTIONS = [
    {
        "mention_id": "m-chp10-p276-traditional-patron-triad",
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-12404",
        "surface_form": "All three",
        "start_char": "197",
        "end_char": "206",
        "note": "Anaphoric collective referring to the preceding State, nobles, and Church categories; no individual members are implied.",
    },
    {
        "mention_id": "m-chp10-p276-early-eighteenth-century-patronage",
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-12405",
        "surface_form": "patronage",
        "start_char": "102",
        "end_char": "111",
        "note": "The source's patronage concept; the place, period, and traditional-source role are bounded by the statement context.",
    },
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_open(row: dict) -> bool:
    q = row.get("qualifiers") or {}
    return q.get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def csv_bytes(rows: list[dict], fields: list[str], has_bom: bool) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8-sig" if has_bom else "utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        if digest(raw[path]) != expected:
            raise ValueError(f"protected table changed: {path.name} ({digest(raw[path])})")
    if digest(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise ValueError("chapter 10 source asset changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[2:13])
    if digest(segment_text.encode("utf-8")) != SEGMENT_SHA256:
        raise ValueError("reviewed p.276 source segment changed")
    for mention in NEW_MENTIONS:
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if segment_text[start:end] != mention["surface_form"]:
            raise ValueError(f"source span mismatch: {mention['mention_id']}")

    statements = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in statements}
    patronage = by_id.get("st-chp10-p276-traditional-patronage-sources")
    tendency = by_id.get("st-chp10-p276-counter-reformation-painting")
    if not patronage or not tendency:
        raise ValueError("expected p.276 triad statements are missing")
    for row in (patronage, tendency):
        q = row.get("qualifiers") or {}
        if row.get("subject_candidate_id") or row.get("object_candidate_id") or q.get("relation_candidate") is not True:
            raise ValueError(f"reviewed statement changed: {row['statement_id']}")
    if "All three" not in segment_text or "tended to promote" not in segment_text:
        raise ValueError("source does not support the reviewed anaphoric triad claims")

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        candidate_fields = reader.fieldnames
        candidates = list(reader)
    with MENTIONS.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        mention_fields = reader.fieldnames
        mentions = list(reader)
    candidate_ids = {row["candidate_id"] for row in candidates}
    mention_ids = {row["mention_id"] for row in mentions}
    for row in NEW_CANDIDATES:
        if row["candidate_id"] in candidate_ids:
            raise ValueError(f"candidate ID already exists: {row['candidate_id']}")
    for row in NEW_MENTIONS:
        if row["mention_id"] in mention_ids:
            raise ValueError(f"mention ID already exists: {row['mention_id']}")

    open_before = sum(is_open(row) for row in statements)
    no_reason_before = sum(
        is_open(row) and not (row.get("qualifiers") or {}).get("open_endpoint_reason") for row in statements
    )
    true_before = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in statements)
    false_before = sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in statements)
    if (open_before, no_reason_before, true_before, false_before, len(statements)) != (379, 59, 10394, 4753, 15147):
        raise ValueError("unexpected pre-edit S2 statement counts")

    patronage["subject_candidate_id"] = "cand-12404"
    patronage["object_candidate_id"] = "cand-12405"
    patronage_q = patronage["qualifiers"]
    patronage_q["mentioned_candidate_ids"] = list(dict.fromkeys(
        patronage_q.get("mentioned_candidate_ids", []) + ["cand-12404", "cand-12405"]
    ))
    patronage_q["claim"] = "Haskell names the State, nobles, and Church as traditional sources of patronage, noting their operation during the first part of the eighteenth century."
    patronage_q["relation_candidate_note"] = "The collective subject is the exact anaphoric referent of 'All three' in the next sentence; its three source categories stay distinct, and the period remains the author's broad wording."
    patronage_q.pop("open_endpoint_reason", None)

    tendency["subject_candidate_id"] = "cand-12404"
    tendency["object_candidate_id"] = "cand-8834"
    tendency_q = tendency["qualifiers"]
    tendency_q["mentioned_candidate_ids"] = list(dict.fromkeys(
        tendency_q.get("mentioned_candidate_ids", []) + ["cand-12404"]
    ))
    tendency_q["claim"] = "Haskell says the three traditional patron categories tended to promote conservative Counter-Reformation elements in Italian painting."
    tendency_q["relation_candidate_note"] = "The source explicitly links the same three-category collective to a tendency, not a universal rule or a claim about every commission."
    tendency_q.pop("open_endpoint_reason", None)

    candidates.extend(NEW_CANDIDATES)
    mentions.extend(NEW_MENTIONS)
    outputs = {
        STATEMENTS: "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in statements).encode("utf-8"),
        CANDIDATES: csv_bytes(candidates, candidate_fields, raw[CANDIDATES].startswith(b"\xef\xbb\xbf")),
        MENTIONS: csv_bytes(mentions, mention_fields, raw[MENTIONS].startswith(b"\xef\xbb\xbf")),
    }
    open_after = sum(is_open(row) for row in statements)
    no_reason_after = sum(
        is_open(row) and not (row.get("qualifiers") or {}).get("open_endpoint_reason") for row in statements
    )
    if (open_after, no_reason_after) != (377, 57):
        raise ValueError(f"unexpected resulting open state: {open_after}, {no_reason_after}")

    print("reviewed=chapter 10 p.276; resolved the explicit 'All three' antecedent and its two claims")
    print("changes=2 source-bounded candidates, 2 exact mentions, 2 relation-candidate endpoints completed")
    print(f"open_endpoints={open_before}->{open_after}; open_without_reason={no_reason_before}->{no_reason_after}")
    for path, output in outputs.items():
        print(f"{path.name} sha256 {digest(raw[path])}->{digest(output)}")
    if args.preview:
        return 0

    for backup in BACKUPS.values():
        if backup.exists():
            raise FileExistsError(f"recovery copy already exists: {backup.name}")
    temps = {path: path.with_name(path.name + ".tmp-s2-chp10-p276-triad-20261015") for path in outputs}
    if any(path.exists() for path in temps.values()):
        raise FileExistsError("protected temporary output already exists")
    for path, backup in BACKUPS.items():
        shutil.copy2(path, backup)
    try:
        for path, output in outputs.items():
            temps[path].write_bytes(output)
        for path in outputs:
            temps[path].replace(path)
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        for path, backup in BACKUPS.items():
            shutil.copy2(backup, path)
        raise
    print("backups=" + ", ".join(path.name for path in BACKUPS.values()))
    print("applied_hashes=" + ", ".join(f"{path.name}:{digest(path.read_bytes())}" for path in outputs))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
