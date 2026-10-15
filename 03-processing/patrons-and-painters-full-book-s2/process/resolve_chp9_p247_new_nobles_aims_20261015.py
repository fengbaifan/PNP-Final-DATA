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
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
SEGMENT_ID = "chp-9:09_CHP-9_intro:l27-36"
STATEMENT_ID = "st-chp9-p247-new-nobles-integration"
NEW_STATEMENT_ID = "st-chp9-p247-new-nobles-disguise-mercantile-origins"
EXISTING_MENTION_ID = "m-chp9-p247-mercantile-origins"
NEW_CANDIDATES = (
    ("cand-12374", "Mercantile origins attributed to newer Venetian nobles in Haskell's p.247 account"),
    ("cand-12375", "Existing order of things in Haskell's p.247 account of newer Venetian nobles"),
)
BACKUP_SUFFIX = "bak-s2-chp9-p247-new-nobles-aims-20261015"
EXPECTED_HASHES = {
    "entity-candidates.csv": "d1f80e052029f1dba5444d827a4f2423a4f5f03e77b63dcf71a407d90e2899ee",
    "mentions.csv": "f992499c8883f42cdca68d76addf56527bc0afaf78c50c1844340fa47d565850",
    "book-statements.jsonl": "688547235e8b3010a709737e22d3702f4e2c9cfee562c620dc03f1c0208efed7",
}
EXPECTED_SEGMENT_HASH = "7b7c85bfda0e96fa9e2d3d69aee031457433796ae97125cba42ae80f5f3db2ee"
EXPECTED_AFTER = (429, 271, 54, 104)


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


def serialize_csv(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=newline.decode("ascii"))
    writer.writeheader()
    writer.writerows(rows)
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    return bom + stream.getvalue().encode("utf-8")


def is_open(row: dict[str, object]) -> bool:
    q = row.get("qualifiers") or {}
    return q.get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def endpoint_counts(rows: list[dict[str, object]]) -> tuple[int, int, int, int]:
    opens = [r for r in rows if is_open(r)]
    object_only = sum(bool(r.get("subject_candidate_id")) and not r.get("object_candidate_id") for r in opens)
    subject_only = sum(not r.get("subject_candidate_id") and bool(r.get("object_candidate_id")) for r in opens)
    both = sum(not r.get("subject_candidate_id") and not r.get("object_candidate_id") for r in opens)
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
    raw_by_name = {
        "entity-candidates.csv": candidate_raw,
        "mentions.csv": mention_raw,
        "book-statements.jsonl": statement_raw,
    }
    for name, expected in EXPECTED_HASHES.items():
        if digest(raw_by_name[name]) != expected:
            raise ValueError(f"Input table changed since review: {name}")

    for cid, name in NEW_CANDIDATES:
        if any(r["candidate_id"] == cid or r["canonical_name"] == name for r in candidates):
            raise ValueError(f"Candidate ID or name already exists: {cid}")
    segment = next(
        json.loads(line)
        for line in SEGMENTS.read_text(encoding="utf-8").splitlines()
        if json.loads(line).get("segment_id") == SEGMENT_ID
    )
    if segment.get("sha256") != EXPECTED_SEGMENT_HASH:
        raise ValueError("Page 247 segment changed")
    source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8").splitlines()
    line_no = 28
    line = source_lines[line_no - 1]
    phrases = {
        "subject": "more recent nobles",
        "disguise": "mercantile origins",
        "integration": "existing order of things",
    }
    if any(line.count(surface) != 1 for surface in phrases.values()):
        raise ValueError("Expected unique source phrases are missing or repeated")
    line_base = sum(len(text) + 1 for text in source_lines[int(segment["line_start"]) - 1 : line_no - 1])

    existing_mention = next((m for m in mentions if m["mention_id"] == EXISTING_MENTION_ID), None)
    if existing_mention is None or existing_mention["candidate_id"] != "cand-8134" or existing_mention["surface_form"] != phrases["disguise"]:
        raise ValueError("Expected existing mercantile-origins mention is not present")
    existing_mention["candidate_id"] = "cand-12374"
    existing_mention["note"] = "The source phrase denotes the mercantile background the newer nobles sought to disguise; it is not another mention of the nobles themselves."

    mention_specs = [
        ("m-chp9-p247-existing-order", "cand-12375", phrases["integration"], "The source's broad phrase for the order the newer nobles sought to enter."),
    ]
    new_mentions = []
    existing_mention_ids = {m["mention_id"] for m in mentions}
    for mid, cid, surface, note in mention_specs:
        if mid in existing_mention_ids:
            raise ValueError(f"Mention ID already exists: {mid}")
        start = line.find(surface)
        end = start + len(surface)
        if line[start:end] != surface:
            raise ValueError(f"Source span mismatch: {mid}")
        new_mentions.append({
            "mention_id": mid,
            "segment_id": SEGMENT_ID,
            "candidate_id": cid,
            "surface_form": surface,
            "start_char": str(line_base + start),
            "end_char": str(line_base + end),
            "note": note,
        })

    rows = [json.loads(text) for text in statement_raw.decode("utf-8").splitlines() if text.strip()]
    if endpoint_counts(rows) != (430, 272, 54, 104):
        raise ValueError(f"Unexpected pre-update endpoint counts: {endpoint_counts(rows)}")
    target = next((r for r in rows if r.get("statement_id") == STATEMENT_ID), None)
    if target is None or not is_open(target) or target.get("subject_candidate_id") != "cand-8134" or target.get("object_candidate_id") is not None:
        raise ValueError("Expected p.247 open integration statement not found")
    if any(r.get("statement_id") == NEW_STATEMENT_ID for r in rows):
        raise ValueError("New statement ID already exists")

    candidate_rows = []
    details = (
        "A source-bounded term for the mercantile background Haskell attributes to recently admitted Venetian nobles. The passage identifies no individual family or specific trade.",
        "A source-bounded term for Haskell's broad phrase 'existing order of things'; it does not identify a particular office, institution, or constitutional body.",
    )
    for (cid, name), detail in zip(NEW_CANDIDATES, details):
        candidate_rows.append({
            "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
            "index_page_range": "", "suggested_type": "term", "status": "open",
            "index_source_file": "", "sub_entry": "", "detail": detail,
            "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L{line_no}",
        })

    # Retain the existing stable statement ID for the integration claim and split the distinct concealment aim.
    target["object_candidate_id"] = "cand-12375"
    tq = target["qualifiers"]
    tq["claim"] = "Haskell says the newer nobles aimed to integrate themselves into the existing order of things."
    tq["mentioned_candidate_ids"] = ["cand-8134", "cand-12375"]
    tq["relation_candidate_note"] = "A source-reported collective aim; retain 'existing order of things' as a broad term and do not infer a particular institution."
    tq["cross_reference_statement_ids"] = [NEW_STATEMENT_ID]
    tq.pop("footnote_marker", None)
    tq.pop("open_endpoint_reason", None)
    target["predicate"] = "aimed_to_integrate_into_existing_venetian_social_order"
    target["original_quote"] = "and to integrate themselves into the existing order of things."

    source_sentence = "These more recent nobles, who were often treated with contempt by the older aristocracy and who were excluded from the more important spheres of the administration, had one aim: to disguise their mercantile origins"
    new_statement = {
        "statement_id": NEW_STATEMENT_ID,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-8134",
        "object_candidate_id": "cand-12374",
        "predicate": "aimed_to_disguise_mercantile_origins",
        "qualifiers": {
            "source_line_start": line_no, "source_line_end": line_no,
            "printed_page": 247, "pdf_physical_page": 5,
            "claim": "Haskell says the newer nobles aimed to disguise their mercantile origins.",
            "speaker": "Haskell", "text_layer": "body",
            "qualification": "This is a collective aim attributed by Haskell; no individual family or specific source of mercantile income is identified.",
            "mentioned_candidate_ids": ["cand-8134", "cand-12374"],
            "relation_candidate": True,
            "relation_candidate_note": "A source-reported collective aim; do not infer individual family identities or specific commercial activities.",
            "cross_reference_statement_ids": [STATEMENT_ID],
        },
        "original_quote": source_sentence,
        "origin": "book",
        "source_file": segment["source_file"],
    }
    rows.append(new_statement)
    if endpoint_counts(rows) != EXPECTED_AFTER:
        raise ValueError(f"Unexpected post-update endpoint counts: {endpoint_counts(rows)}")

    candidate_after = append_rows(candidate_raw, candidate_fields, candidate_rows)
    mention_after = serialize_csv(mention_raw, mention_fields, mentions + new_mentions)
    statement_after = ("".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in rows)).encode("utf-8")
    print(f"candidates={len(candidates)}->{len(candidates) + len(candidate_rows)}")
    print(f"mentions={len(mentions)}->{len(mentions) + len(new_mentions)}; remapped={EXISTING_MENTION_ID}:cand-8134->cand-12374")
    print(f"statements={len([1 for x in statement_raw.decode('utf-8').splitlines() if x.strip()])}->{len(rows)}")
    print(f"split_statement={STATEMENT_ID}|integrate->cand-12375; disguise->cand-12374")
    print(f"open_endpoints={endpoint_counts([json.loads(x) for x in statement_raw.decode('utf-8').splitlines() if x.strip()])}->{endpoint_counts(rows)}")
    for name, before, after in (
        ("entity-candidates.csv", candidate_raw, candidate_after),
        ("mentions.csv", mention_raw, mention_after),
        ("book-statements.jsonl", statement_raw, statement_after),
    ):
        print(f"{name} sha256 {digest(before)}->{digest(after)}")
    if args.preview:
        return 0

    outputs = ((CANDIDATES, candidate_after), (MENTIONS, mention_after), (STATEMENTS, statement_after))
    pairs: list[tuple[Path, Path, Path, bytes]] = []
    for path, data in outputs:
        backup = path.with_name(f"{path.name}.{BACKUP_SUFFIX}")
        temp = path.with_name(f"{path.name}.tmp-{BACKUP_SUFFIX}")
        if backup.exists() or temp.exists():
            raise FileExistsError(f"Recovery or temporary file already exists: {path.name}")
        pairs.append((path, backup, temp, data))
    for path, backup, _, _ in pairs:
        shutil.copy2(path, backup)
    replaced: list[tuple[Path, Path]] = []
    try:
        for _, _, temp, data in pairs:
            temp.write_bytes(data)
        for path, backup, temp, _ in pairs:
            temp.replace(path)
            replaced.append((path, backup))
    except Exception:
        for _, _, temp, _ in pairs:
            if temp.exists():
                temp.unlink()
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
