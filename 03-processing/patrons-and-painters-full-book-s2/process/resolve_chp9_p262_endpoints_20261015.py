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
TABLES = ROOT / "04-knowledge/tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
SEGMENTS = TABLES / "segments.jsonl"
STATEMENT_BACKUP = STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp9-p262-20261015")
CANDIDATE_BACKUP = CANDIDATES.with_name("entity-candidates.csv.bak-s2-chp9-p262-20261015")
EXPECTED_HASHES = {
    "book-statements.jsonl": "19eddb57ce63b2e9700aee0dec99f51a8451cef1b606d5b573052bdcd2503efa",
    "entity-candidates.csv": "6bf9f1452de4f8aefb3e48726613a03850a846855be4a0ff7ad555da5c6c649d",
}
SEGMENT_HASHES = {
    "chp-9:09_CHP-9_intro:l218-229": "19071349bda95267fa463da2c9c65c3af827a9e978d3585bdbb715e08831f9dc",
    "chp-9:09_CHP-9_intro:l323-445": "51cc706d49319744d5efe4ed0c2528e68a2a3e1d82d75b14961092f0c36eebfc",
}
REVIEWED_IDS = {
    "st-chp9-p262-foreign-competition-price-context",
    "st-chp9-p262-foscarini-income",
    "st-chp9-p262-gallery-as-corollary-of-nobility",
    "st-chp9-p262-small-fashionable-works-price-comparison",
    "st-chp9-p262-tiepolo-martyrdom-payment",
    "st-chp9-p262-tiepolo-pieta-dome-payment",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return raw, list(reader.fieldnames or []), list(reader)


def rewrite_csv(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=newline.decode("ascii"))
    writer.writeheader()
    writer.writerows(rows)
    prefix = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    return prefix + stream.getvalue().encode("utf-8")


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

    statement_raw = STATEMENTS.read_bytes()
    candidate_raw, candidate_fields, candidate_rows = read_csv(CANDIDATES)
    for name, raw in (("book-statements.jsonl", statement_raw), ("entity-candidates.csv", candidate_raw)):
        if digest(raw) != EXPECTED_HASHES[name]:
            raise ValueError(f"{name} changed since p.262 review was prepared")
    segments = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment_index = {row["segment_id"]: row for row in segments}
    for segment_id, expected_hash in SEGMENT_HASHES.items():
        segment = segment_index.get(segment_id)
        if segment is None or segment.get("sha256") != expected_hash:
            raise ValueError(f"Reviewed p.262 source segment changed: {segment_id}")

    statement_rows = [json.loads(line) for line in statement_raw.decode("utf-8-sig").splitlines() if line.strip()]
    statement_index = {row["statement_id"]: row for row in statement_rows}
    if not REVIEWED_IDS.issubset(statement_index):
        raise ValueError("One or more p.262 reviewed statements are missing")
    if endpoint_counts(statement_rows) != (397, 249, 48, 100):
        raise ValueError(f"Unexpected global open-endpoint counts: {endpoint_counts(statement_rows)}")
    for statement_id in ("st-chp9-p262-foreign-competition-price-context", "st-chp9-p262-foscarini-income", "st-chp9-p262-gallery-as-corollary-of-nobility", "st-chp9-p262-small-fashionable-works-price-comparison"):
        if not is_open(statement_index[statement_id]):
            raise ValueError(f"Reviewed p.262 statement is no longer open: {statement_id}")

    candidate_index = {row["candidate_id"]: row for row in candidate_rows}
    tiepolo_price_candidate = candidate_index.get("cand-2603")
    if (
        tiepolo_price_candidate is None
        or tiepolo_price_candidate.get("canonical_name") != "Tiepolo, Giambattista"
        or tiepolo_price_candidate.get("suggested_type") != "term"
        or tiepolo_price_candidate.get("sub_entry") != "prices"
    ):
        raise ValueError("Expected p.262 Tiepolo price-subentry candidate changed")
    if candidate_index.get("cand-2569", {}).get("suggested_type") != "person":
        raise ValueError("Canonical Tiepolo person candidate cand-2569 is absent or changed")

    foreign = statement_index["st-chp9-p262-foreign-competition-price-context"]
    foreign["subject_candidate_id"] = "cand-8568"
    foreign["object_candidate_id"] = "cand-2062"
    foreign["qualifiers"]["relation_candidate_note"] = "The source-defined factor term and artist-price term provide the two endpoints for Haskell's causal explanation. Preserve that this is an authorial market account without comparative data or a quantified causal measure."
    foreign["qualifiers"].pop("open_endpoint_reason", None)

    income = statement_index["st-chp9-p262-foscarini-income"]
    income["qualifiers"]["relation_candidate"] = False
    income["qualifiers"]["relation_candidate_note"] = "This is a reported numeric family attribute derived from Visconti's 1749 letter, not a relation to a separate entity. Preserve the estimate, unit, date context, and Haskell's currency caveat without fabricating an object endpoint."
    income["qualifiers"].pop("open_endpoint_reason", None)

    gallery = statement_index["st-chp9-p262-gallery-as-corollary-of-nobility"]
    gallery["qualifiers"]["relation_candidate"] = False
    gallery["qualifiers"]["relation_candidate_note"] = "This is Haskell's broad social interpretation of gallery display as a feature of noble status; no particular gallery or family is asserted as the endpoint. Retain it as an attributed proposition, not a specific edge."
    gallery["qualifiers"].pop("open_endpoint_reason", None)

    comparison = statement_index["st-chp9-p262-small-fashionable-works-price-comparison"]
    comparison["qualifiers"]["relation_candidate"] = False
    comparison["qualifiers"]["relation_candidate_note"] = "This is a qualified comparison between broad classes of small fashionable works and large history pictures/decorations, not a pairing of identified works. The named price examples are recorded separately; retain this comparative claim without inventing work-group entities."
    comparison["qualifiers"].pop("open_endpoint_reason", None)

    pieta = statement_index["st-chp9-p262-tiepolo-pieta-dome-payment"]
    pieta["qualifiers"]["mentioned_candidate_ids"] = list(dict.fromkeys(
        (pieta["qualifiers"].get("mentioned_candidate_ids") or [])
    ))
    if "cand-2569" in pieta["qualifiers"]["mentioned_candidate_ids"]:
        pieta["qualifiers"]["mentioned_candidate_ids"] = [
            "cand-2603" if cid == "cand-2569" else cid for cid in pieta["qualifiers"]["mentioned_candidate_ids"]
        ]

    candidate_index["cand-2603"]["suggested_type"] = "person"
    candidate_index["cand-2603"]["detail"] = "Index subentry for prices; the referent in Haskell's p.262 passage is Giambattista Tiepolo the painter. Keep this index-derived candidate distinct from cand-2569 until S3 identity alignment."

    after = endpoint_counts(statement_rows)
    if after != (393, 247, 46, 100):
        raise ValueError(f"Unexpected post-review global open-endpoint counts: {after}")
    statement_after = ("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in statement_rows)).encode("utf-8")
    candidate_after = rewrite_csv(candidate_raw, candidate_fields, list(candidate_index.values()))

    print("reviewed=p.262 broad market claims, family income, nobility/gallery claim, and artist-price comparisons")
    print("resolved=linked foreign-competition and artist-price concepts; retained broad claims as propositions; corrected the Tiepolo price-subentry candidate to person")
    print(f"statements={len(statement_rows)}; candidates={len(candidate_rows)}; open_endpoints={endpoint_counts([json.loads(line) for line in statement_raw.decode('utf-8-sig').splitlines() if line.strip()])}->{after}")
    print(f"book-statements.jsonl sha256 {digest(statement_raw)}->{digest(statement_after)}")
    print(f"entity-candidates.csv sha256 {digest(candidate_raw)}->{digest(candidate_after)}")
    if args.preview:
        return 0
    if STATEMENT_BACKUP.exists() or CANDIDATE_BACKUP.exists():
        raise FileExistsError("One or more p.262 recovery copies already exist")
    statement_tmp = STATEMENTS.with_name("book-statements.jsonl.tmp-s2-chp9-p262-20261015")
    candidate_tmp = CANDIDATES.with_name("entity-candidates.csv.tmp-s2-chp9-p262-20261015")
    if statement_tmp.exists() or candidate_tmp.exists():
        raise FileExistsError("One or more p.262 temporary files already exist")
    shutil.copy2(STATEMENTS, STATEMENT_BACKUP)
    shutil.copy2(CANDIDATES, CANDIDATE_BACKUP)
    replaced: list[tuple[Path, Path]] = []
    try:
        statement_tmp.write_bytes(statement_after)
        candidate_tmp.write_bytes(candidate_after)
        statement_tmp.replace(STATEMENTS)
        replaced.append((STATEMENTS, STATEMENT_BACKUP))
        candidate_tmp.replace(CANDIDATES)
        replaced.append((CANDIDATES, CANDIDATE_BACKUP))
    except Exception:
        if statement_tmp.exists():
            statement_tmp.unlink()
        if candidate_tmp.exists():
            candidate_tmp.unlink()
        for path, backup in replaced:
            shutil.copy2(backup, path)
        raise
    print(f"backup={STATEMENT_BACKUP.relative_to(ROOT)}")
    print(f"backup={CANDIDATE_BACKUP.relative_to(ROOT)}")
    print(f"applied_sha256={digest(STATEMENTS.read_bytes())};{digest(CANDIDATES.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
