from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_iv.md"
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l79-89"
SEGMENT_SHA = "7f8e4442443bc927ff276280e0d182a1e751cb542f9d0ad3e652f2cf523fb53b"
SOURCE_SHA = "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf"
BACKUP_SUFFIX = ".bak-s2-chp2-seciv-l79-89-scalar-semantics-20261013"
EXPECTED = {
    "book-statements.jsonl": "8ceb677453df644fba978c43aecd0acfeaa2c5a2f3ec5284c7fdee303df47fb5",
    "entity-candidates.csv": "e14cc4658e4f0a56963f2ccc2504d14048bc3ca9f74b3cb7a034e7f040010f17",
    "mentions.csv": "156a624f33d31521bd41fb640cf63952feaac2a2039b890afbdb31acc2cafdde",
    "s2-coverage.csv": "3c7fb7b43d9a5402235abde22fa2e8d703c49405d32abd33522f58df7be024d4",
}
UNSET_IDS = {
    "st-chp2-seciv-l79-89-camassei-career-seems-assured",
    "st-chp2-seciv-l79-89-cupid-psyche-decoration-instant-success",
    "st-chp2-seciv-l79-89-divine-wisdom-claimed-as-new-artistic-subject",
    "st-chp2-seciv-l79-89-god-creating-angels-iconographic-hierarchy",
    "st-chp2-seciv-l79-89-great-hopes-held-out-to-camassei",
    "st-chp2-seciv-l79-89-two-camassei-frescoes-foreshadow-larger-scheme",
}
NEW_CANDIDATES = {
    "cand-11888": {
        "canonical_name": "Divine sanction for worldly sovereignty (iconographic concept)",
        "suggested_type": "term",
        "detail": "Haskell interprets crown-bearing angels protecting provinces and kingdoms and sceptre-bearing angels assisting rulers as symbolising divine sanction to worldly sovereigns. This is the author's iconographic reading, not independently verified political theology.",
    },
    "cand-11889": {
        "canonical_name": "Unidentified larger decorative scheme foreshadowed by Camassei's ceiling frescoes",
        "suggested_type": "work",
        "detail": "Haskell says themes in Camassei's paired ceiling frescoes foreshadow a much larger decorative scheme to follow. The scheme has no title or identified scope here; keep distinct from the two small-room frescoes and the separate Divine Wisdom fresco.",
    },
}
NEW_MENTIONS = [
    ("m-chp2-seciv-l79-89-0054", "cand-11888", "the divine sanction given to the sovereigns of this world", 1221, 1278,
     "The concept symbolised by the angelic hierarchy in Haskell's interpretation of God creating the Angels."),
    ("m-chp2-seciv-l79-89-0055", "cand-11889", "the much larger scheme of decoration that was to follow", 940, 995,
     "The unnamed decorative programme whose themes Haskell says the paired ceiling frescoes foreshadowed."),
    ("m-chp2-seciv-l79-89-0056", "cand-0484", "Camassei", 1736, 1744,
     "Andrea Camassei is the stated recipient of the great hopes; the source does not identify who held them."),
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bytes]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader), raw


def serialize_jsonl(rows: list[dict], original: bytes) -> bytes:
    payload = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode("utf-8")
    return (b"\xef\xbb\xbf" + payload) if original.startswith(b"\xef\xbb\xbf") else payload


def serialize_csv(fieldnames: list[str], rows: list[dict[str, str]], original: bytes) -> bytes:
    buffer = io.StringIO(newline="")
    line_ending = "\r\n" if b"\r\n" in original else "\n"
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator=line_ending, extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    payload = buffer.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" + payload) if original.startswith(b"\xef\xbb\xbf") else payload


def add_unique(values: list[str], additions: list[str]) -> list[str]:
    return list(dict.fromkeys([*values, *additions]))


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve the remaining semantic classifications in CHP-2 p.50.")
    parser.add_argument("--apply", action="store_true", help="write after protected preview; default is preview")
    args = parser.parse_args()
    paths = {name: TABLES / name for name in EXPECTED}
    raw_by_name = {name: path.read_bytes() for name, path in paths.items()}
    for name, expected in EXPECTED.items():
        actual = hashlib.sha256(raw_by_name[name]).hexdigest()
        if actual != expected:
            raise SystemExit(f"protected table changed: {name}: expected {expected}, found {actual}")
    if digest(SOURCE) != SOURCE_SHA:
        raise SystemExit("protected S0 source asset changed")

    segment = next((row for row in read_jsonl(TABLES / "segments.jsonl") if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA or segment.get("asset_sha256") != SOURCE_SHA:
        raise SystemExit("protected p.50 source segment fingerprint changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
    if hashlib.sha256(source_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
        raise SystemExit("p.50 source segment content changed")

    statements = read_jsonl(paths["book-statements.jsonl"])
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row["statement_id"] for row in statements
        if row.get("segment_id") == SEGMENT_ID and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    if unset != UNSET_IDS:
        raise SystemExit(f"unexpected p.50 unset set: {sorted(unset)}")

    candidate_fields, candidates, candidate_raw = read_csv(paths["entity-candidates.csv"])
    mention_fields, mentions, mention_raw = read_csv(paths["mentions.csv"])
    coverage_fields, coverage, coverage_raw = read_csv(paths["s2-coverage.csv"])
    candidate_ids = {row["candidate_id"] for row in candidates}
    if candidate_ids & NEW_CANDIDATES.keys():
        raise SystemExit(f"planned candidate IDs already exist: {sorted(candidate_ids & NEW_CANDIDATES.keys())}")
    mention_ids = {row["mention_id"] for row in mentions}
    if mention_ids & {item[0] for item in NEW_MENTIONS}:
        raise SystemExit("planned mention ID already exists")
    if "cand-0485" not in candidate_ids or "cand-0486" not in candidate_ids or "cand-0484" not in candidate_ids:
        raise SystemExit("required artwork or artist candidate missing")
    coverage_rows = [row for row in coverage if row.get("segment_id") == SEGMENT_ID]
    if len(coverage_rows) != 1 or "L80-89" not in coverage_rows[0].get("source_line_ranges", ""):
        raise SystemExit("p.50 coverage row is missing or has an unexpected source range")

    # Exact phrase and span protection: offsets are relative to the full S0 segment, including its page marker.
    for _, candidate_id, surface, start, end, _ in NEW_MENTIONS:
        if source_text[start:end] != surface:
            raise SystemExit(f"protected mention span mismatch: {candidate_id}: {start}:{end}")

    career = by_id["st-chp2-seciv-l79-89-camassei-career-seems-assured"]
    cq = career["qualifiers"]
    cq["relation_candidate"] = False
    cq["relation_candidate_note"] = "This is Haskell's forecast of Camassei's career prospects, not a claim connecting two entities."
    career["original_quote"] = "The process was by now a familiar one, and his career seemed assured."

    success = by_id["st-chp2-seciv-l79-89-cupid-psyche-decoration-instant-success"]
    sq = success["qualifiers"]
    sq["relation_candidate"] = False
    sq["relation_candidate_note"] = "The source attributes immediate success to the room decoration without identifying a distinct audience or other relation endpoint; retain this as a reception attribute."
    success["original_quote"] = "There he had decorated a room with scenes from the story of Cupid and Psyche which proved an instant success."

    novelty = by_id["st-chp2-seciv-l79-89-divine-wisdom-claimed-as-new-artistic-subject"]
    nq = novelty["qualifiers"]
    nq["relation_candidate"] = False
    nq["relation_candidate_note"] = "This is Haskell's historical novelty claim about the subject, not a relation to a separately identified entity."
    novelty["original_quote"] = "a subject not hitherto represented in art"

    concept_id = "cand-11888"
    concept = by_id["st-chp2-seciv-l79-89-god-creating-angels-iconographic-hierarchy"]
    concept["object_candidate_id"] = concept_id
    concept["predicate"] = "visualizes"
    iq = concept["qualifiers"]
    iq["claim"] = "Haskell interprets the crowned angels protecting provinces and kingdoms and the sceptre-bearing angels assisting rulers as symbolising divine sanction for worldly sovereigns."
    iq["relation_candidate"] = True
    iq["relation_candidate_note"] = "Haskell explicitly links the angelic imagery to the concept of divine sanction; preserve this as a work-to-concept iconographic relation."
    iq["mentioned_candidate_ids"] = add_unique(iq.get("mentioned_candidate_ids", []), ["cand-0485", concept_id])
    concept["original_quote"] = (
        "For among the hierarchy of angels brought into being by God two classes especially were singled out—those with crowns "
        "who protected provinces and kingdoms, and those with sceptres who assisted their rulers, thus symbolising the divine sanction "
        "given to the sovereigns of this world."
    )

    hopes = by_id["st-chp2-seciv-l79-89-great-hopes-held-out-to-camassei"]
    hopes["subject_candidate_id"] = None
    hopes["object_candidate_id"] = "cand-0484"
    hopes["predicate"] = "recipient_of_high_expectations_reported"
    hq = hopes["qualifiers"]
    hq["relation_candidate"] = True
    hq["relation_candidate_note"] = "The passive wording explicitly makes Camassei the recipient of high hopes; the source does not identify who held them."
    hq["open_endpoint_reason"] = "Haskell does not name the source or group holding these hopes; leave the subject endpoint open and do not infer patrons from adjacent sentences."
    hq["mentioned_candidate_ids"] = add_unique(hq.get("mentioned_candidate_ids", []), ["cand-0484"])
    hopes["original_quote"] = "great hopes were held out to Camassei"

    scheme_id = "cand-11889"
    scheme = by_id["st-chp2-seciv-l79-89-two-camassei-frescoes-foreshadow-larger-scheme"]
    scheme["object_candidate_id"] = scheme_id
    scheme["predicate"] = "foreshadows_themes_of_larger_decorative_scheme"
    fq = scheme["qualifiers"]
    fq["claim"] = "Haskell says themes in Camassei's two ceiling frescoes foreshadowed themes in a much larger decorative scheme to follow."
    fq["relation_candidate"] = True
    fq["relation_candidate_note"] = "The passage explicitly connects the paired ceiling frescoes with a later, larger decorative scheme; retain the latter as an unnamed work candidate."
    fq["mentioned_candidate_ids"] = add_unique(fq.get("mentioned_candidate_ids", []), ["cand-0485", "cand-0486", scheme_id])
    scheme["original_quote"] = "both of them foreshadowed some of the themes of the much larger scheme of decoration that was to follow."

    segment_ref = f"{SEGMENT_ID}#L84"
    candidate_rows = []
    for candidate_id, spec in NEW_CANDIDATES.items():
        candidate_rows.append({
            "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": spec["canonical_name"],
            "index_page_range": "", "suggested_type": spec["suggested_type"], "status": "open",
            "index_source_file": "", "sub_entry": "", "detail": spec["detail"],
            "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": segment_ref,
        })
    candidates.extend(candidate_rows)
    for mention_id, candidate_id, surface, start, end, note in NEW_MENTIONS:
        mentions.append({
            "mention_id": mention_id, "segment_id": SEGMENT_ID, "candidate_id": candidate_id,
            "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
        })

    coverage_row = coverage_rows[0]
    note = (
        " 本轮闭合6条旧unset：career prospects、instant success与subject novelty作为作者评价/属性标为非关系；"
        "God creating the Angels的图像释读连接到新term候选cand-11888（divine sanction）；“great hopes were held out to Camassei”保留明确受益人和未名施予方；"
        "两幅小室壁画对后续大型装饰方案的预示连接到开放work候选cand-11889。新增3条精确mention，S0及本段已分类关系候选端点不改。"
    )
    if note.strip() not in coverage_row.get("note", ""):
        coverage_row["note"] = coverage_row.get("note", "").rstrip() + note

    payloads = {
        "book-statements.jsonl": serialize_jsonl(statements, raw_by_name["book-statements.jsonl"]),
        "entity-candidates.csv": serialize_csv(candidate_fields, candidates, candidate_raw),
        "mentions.csv": serialize_csv(mention_fields, mentions, mention_raw),
        "s2-coverage.csv": serialize_csv(coverage_fields, coverage, coverage_raw),
    }
    result = {
        "mode": "apply" if args.apply else "preview",
        "segment": SEGMENT_ID,
        "closed_unset_ids": sorted(UNSET_IDS),
        "classification_counts_for_closed_rows": {"true": 3, "false": 3},
        "new_candidates": list(NEW_CANDIDATES),
        "new_mentions": [{"id": item[0], "candidate_id": item[1], "surface": item[2], "span": [item[3], item[4]]} for item in NEW_MENTIONS],
        "source_asset_unchanged": True,
        "remaining_unset_in_segment": [],
        "payload_sha256": {name: hashlib.sha256(payload).hexdigest() for name, payload in payloads.items()},
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups: dict[str, Path] = {}
    temps: dict[str, Path] = {}
    try:
        for name, payload in payloads.items():
            path = paths[name]
            backup = path.with_name(path.name + BACKUP_SUFFIX)
            if backup.exists():
                raise SystemExit(f"recovery copy already exists; refusing overwrite: {backup.name}")
            shutil.copy2(path, backup)
            backups[name] = backup
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as handle:
                temp = Path(handle.name)
                handle.write(payload)
            temps[name] = temp
        for name, temp in temps.items():
            os.replace(temp, paths[name])
        if digest(SOURCE) != SOURCE_SHA:
            raise SystemExit("S0 source asset changed during write")
        written = read_jsonl(paths["book-statements.jsonl"])
        written_by_id = {row["statement_id"]: row for row in written}
        if any((written_by_id[sid].get("qualifiers") or {}).get("relation_candidate") is None for sid in UNSET_IDS):
            raise SystemExit("a p.50 classification did not persist")
        if written_by_id[scheme["statement_id"]].get("object_candidate_id") != "cand-11889":
            raise SystemExit("the decorative-scheme relation did not persist")
        print(json.dumps({
            "result": "applied",
            "backups": {name: backup.name for name, backup in backups.items()},
            "written_hashes": {name: digest(path) for name, path in paths.items()},
        }, ensure_ascii=False, indent=2))
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        for name, backup in backups.items():
            shutil.copy2(backup, paths[name])
        raise


if __name__ == "__main__":
    main()
