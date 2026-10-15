from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
SEGMENT_ID = "chp-9:09_CHP-9_intro:l303-311"
BACKUP_SUFFIX = "bak-s2-chp9-p266-collection-endpoints-20261015"
EXPECTED_HASHES = {
    "entity-candidates.csv": "44615b46c74f374e098a05d1b8f01b3c04c2377e9a18122768f09515bc7b496b",
    "mentions.csv": "14eaeff5e74d9e2cfede55994ff6f99efe392bb75c236fec42bf29e1283e8030",
    "book-statements.jsonl": "8021bd9d6dc67aeb8cde1c525e5af0b67d26494c43a0f2acee2d453add515af7",
}
EXPECTED_SEGMENT_HASH = "6153ee105244f9e9bf25cd7cfbffef26cd195c6648061760e56bd83c9de98270"
REPUTATION_ID = "st-chp9-p266-reputation-and-collection"
PURCHASE_ID = "st-chp9-p266-original-pieces-and-attention"
COLLECTOR_ID = "st-chp9-p266-sagredo-collected-prints-and-drawings"
COLLECTOR_SURFACE = "prints and drawings"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return raw, list(reader.fieldnames or []), list(reader)


def append_rows(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=newline.decode("ascii"))
    writer.writerows(rows)
    if raw and not raw.endswith((b"\n", b"\r")):
        raw += newline
    return raw + stream.getvalue().encode("utf-8")


def rewrite_csv(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=newline.decode("ascii"))
    writer.writeheader()
    writer.writerows(rows)
    prefix = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    return prefix + stream.getvalue().encode("utf-8")


def is_open(row: dict[str, object]) -> bool:
    qualifiers = row.get("qualifiers") or {}
    return qualifiers.get("relation_candidate") is True and (
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

    candidate_raw, candidate_fields, candidates = read_csv(CANDIDATES)
    mention_raw, mention_fields, mentions = read_csv(MENTIONS)
    statement_raw = STATEMENTS.read_bytes()
    for name, data in (
        ("entity-candidates.csv", candidate_raw), ("mentions.csv", mention_raw), ("book-statements.jsonl", statement_raw)
    ):
        if digest(data) != EXPECTED_HASHES[name]:
            raise ValueError(f"Input table changed since this batch was reviewed: {name}")

    segment = next(
        json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8").splitlines()
        if json.loads(line).get("segment_id") == SEGMENT_ID
    )
    if segment.get("sha256") != EXPECTED_SEGMENT_HASH:
        raise ValueError("p.266 source segment changed")
    source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8").splitlines()
    line = source_lines[303]
    if line.count(COLLECTOR_SURFACE) != 1:
        raise ValueError("Expected unique p.266 collector phrase not found")

    candidates_by_id = {row["candidate_id"]: row for row in candidates}
    collection = candidates_by_id.get("cand-2334")
    if collection is None or collection.get("sub_entry") != "collection of prints and drawings" or collection.get("suggested_type"):
        raise ValueError("The reviewed untyped Sagredo collection index sub-entry is absent or changed")
    if "cand-8590" not in candidates_by_id or "cand-8633" not in candidates_by_id:
        raise ValueError("Expected Bonfiglioli drawing group or Raphael sheets candidate is absent")

    mention_by_id = {row["mention_id"]: row for row in mentions}
    existing_collection_mention = mention_by_id.get("m-chp9-p266-print-collection")
    if existing_collection_mention is None or existing_collection_mention.get("candidate_id") != "cand-2334" or existing_collection_mention.get("surface_form") != COLLECTOR_SURFACE:
        raise ValueError("Expected exact print-and-drawing mention already present in the source segment")
    rows = [json.loads(item) for item in statement_raw.decode("utf-8").splitlines() if item.strip()]
    before_counts = endpoint_counts(rows)
    if before_counts != (417, 260, 53, 104):
        raise ValueError(f"Unexpected pre-update endpoint counts: {before_counts}")
    index = {row["statement_id"]: row for row in rows}
    reputation = index.get(REPUTATION_ID)
    purchase = index.get(PURCHASE_ID)
    if reputation is None or not is_open(reputation) or reputation.get("subject_candidate_id") != "cand-2329":
        raise ValueError("Expected open p.266 reputation statement is absent or changed")
    if purchase is None or not is_open(purchase) or purchase.get("subject_candidate_id") != "cand-2329":
        raise ValueError("Expected open p.266 purchase statement is absent or changed")
    if COLLECTOR_ID in index:
        raise ValueError("Atomic p.266 collector statement already exists")

    expected_start = sum(len(text) + 1 for text in source_lines[int(segment["line_start"]) - 1 : 303]) + line.index(COLLECTOR_SURFACE)
    if existing_collection_mention.get("segment_id") != SEGMENT_ID or existing_collection_mention.get("start_char") != str(expected_start) or existing_collection_mention.get("end_char") != str(expected_start + len(COLLECTOR_SURFACE)):
        raise ValueError("Existing print-and-drawing mention no longer matches the reviewed exact source span")

    collection["detail"] = (
        "Index sub-entry for Zaccaria Sagredo's print-and-drawing collection. Haskell describes Sagredo as a passionate collector of prints and drawings; "
        "the collection's exact boundary and its type under the current taxonomy remain unresolved. Keep it distinct from specifically identified drawing volumes and work groups."
    )

    reputation["predicate"] = "haskell_assessment_of_sagredo_patronage_reputation"
    rq = reputation["qualifiers"]
    rq["relation_candidate"] = False
    rq["claim"] = "Haskell says little is known of Sagredo and argues that contemporaries' enthusiasm explains attention to his patronage and the extent of his reputation."
    rq["mentioned_candidate_ids"] = ["cand-2329"]
    rq["qualification"] = "Authorial assessment of surviving knowledge and reputation, not a measured comparison across all patrons."
    rq["relation_candidate_note"] = "Nonrelational authorial assessment; the explicit collector-to-collection assertion is recorded separately."
    rq.pop("open_endpoint_reason", None)
    line_304 = source_lines[303]
    quote_start = line_304.index("our knowledge of Sagredo")
    quote_end = line_304.index(" He was a passionate collector", quote_start)
    reputation["original_quote"] = line_304[quote_start:quote_end]

    purchase["object_candidate_id"] = "cand-8590"
    purchase["predicate"] = "sagredo_bonfiglioli_purchase_included_original_works_and_attracted_connoisseurs"
    pq = purchase["qualifiers"]
    pq["claim"] = "Haskell says the Bonfiglioli purchase of three Carracci drawing volumes included fine Raphael sheets and other original works by great masters and attracted contemporary connoisseur attention."
    pq["mentioned_candidate_ids"] = ["cand-2329", "cand-8590", "cand-8633"]
    pq["relation_candidate_note"] = "The purchase refers to the three-volume Carracci drawing group described in the preceding sentence. The source says it included Raphael sheets and other unnamed originals; do not expand the candidate to identify those works or individual connoisseurs."
    pq.pop("open_endpoint_reason", None)

    collector = {
        "statement_id": COLLECTOR_ID, "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-2329", "object_candidate_id": "cand-2334",
        "predicate": "passionate_collector_of_prints_and_drawings",
        "qualifiers": {
            "source_line_start": 304, "source_line_end": 304, "printed_page": 266, "pdf_physical_page": 32,
            "claim": "Haskell describes Zaccaria Sagredo as a passionate collector of prints and drawings.",
            "speaker": "Haskell", "text_layer": "authorial narrative",
            "qualification": "This is Haskell's source-based characterization. The collection sub-entry's aggregate boundary and type remain unresolved.",
            "mentioned_candidate_ids": ["cand-2329", "cand-2334"],
            "relation_candidate": True,
            "relation_candidate_note": "The source directly describes Sagredo's collecting. The object reuses the matching index sub-entry for his print-and-drawing collection; no individual sheets or complete collection boundary are inferred.",
        },
        "original_quote": "He was a passionate collector of prints and drawings.",
        "origin": "book", "source_file": segment["source_file"],
    }
    rows.append(collector)
    after_counts = endpoint_counts(rows)
    if after_counts != (415, 258, 53, 104):
        raise ValueError(f"Unexpected post-update endpoint counts: {after_counts}")

    candidate_after = rewrite_csv(candidate_raw, candidate_fields, candidates)
    statement_after = ("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)).encode("utf-8")
    true_after = sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in rows)
    false_after = sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in rows)
    print("split=p.266 reputation/knowledge assessment (nonrelational) from Sagredo's collector-to-collection relation")
    print("resolved=p.266 Bonfiglioli purchase object -> existing Carracci drawing group cand-8590")
    print(f"candidates={len(candidates)}; mentions={len(mentions)} unchanged; statements={len(rows) - 1}->{len(rows)}")
    print(f"relation_true_false={true_after}/{false_after}; open_endpoints={before_counts}->{after_counts}")
    for name, before, after in (
        ("entity-candidates.csv", candidate_raw, candidate_after),
        ("book-statements.jsonl", statement_raw, statement_after),
    ):
        print(f"{name} sha256 {digest(before)}->{digest(after)}")
    if args.preview:
        return 0

    outputs = ((CANDIDATES, candidate_after), (STATEMENTS, statement_after))
    pairs: list[tuple[Path, Path, Path, bytes]] = []
    for path, data in outputs:
        backup = path.with_name(f"{path.name}.{BACKUP_SUFFIX}")
        temporary = path.with_name(f"{path.name}.tmp-{BACKUP_SUFFIX}")
        if backup.exists() or temporary.exists():
            raise FileExistsError(f"Recovery or temporary file already exists: {path.name}")
        pairs.append((path, backup, temporary, data))
    for path, backup, _, _ in pairs:
        shutil.copy2(path, backup)
    replaced: list[tuple[Path, Path]] = []
    try:
        for _, _, temporary, data in pairs:
            temporary.write_bytes(data)
        for path, backup, temporary, _ in pairs:
            temporary.replace(path)
            replaced.append((path, backup))
    except Exception:
        for _, _, temporary, _ in pairs:
            if temporary.exists():
                temporary.unlink()
        for path, backup in replaced:
            shutil.copy2(backup, path)
        raise
    for path, backup, _, _ in pairs:
        print(f"backup={backup.relative_to(ROOT)}")
        print(f"applied_sha256={path.relative_to(ROOT)}:{digest(path.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
