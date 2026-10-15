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
BACKUP_SUFFIX = "bak-s2-chp9-p267-p268-endpoints-20261015"
EXPECTED_HASHES = {
    "entity-candidates.csv": "887966f4c85920ae5ee41a93587047d2947eecad7b7608965c2719015245900a",
    "mentions.csv": "14eaeff5e74d9e2cfede55994ff6f99efe392bb75c236fec42bf29e1283e8030",
    "book-statements.jsonl": "70fe07f04f4a13a3369de0db276933ffabccd94906d983855d71e482079df655",
}
SEGMENT_HASHES = {
    "chp-9:09_CHP-9_intro:l313-321": "3b6bb69ba75dac969f2059036fd7dd45a1a67b771e41ba507f85bd982dc70080",
    "chp-9:09_CHP-9_sec_ii:l6-16": "011ed62e984b1e67c23bc2e36b88e9957fae9c3f97458a06918a4b75254853f8",
}
NEW_CANDIDATES = [
    {
        "candidate_id": "cand-12388",
        "canonical_name": "Unidentified pictures from Mantua reported on the Venetian market (Haskell, p.267)",
        "suggested_type": "work",
        "detail": "A source-defined group described as a great number of pictures from Mantua appearing on the Venetian market. The source does not identify individual pictures or establish that all came from the Gonzaga ducal collection; do not infer authorship or equate this group with the specifically named purchases in the following sentences.",
        "candidate_source_ref": "chp-9:09_CHP-9_intro:l313-321#L319",
    },
    {
        "candidate_id": "cand-12389",
        "canonical_name": "Venetian art market in Haskell's p.267-268 account",
        "suggested_type": "term",
        "detail": "The local art-market context in Haskell's account of Mantuan pictures and Church demand for modern painting. This is a market concept, not a separately named institution or venue; keep it distinct from Venice as a place.",
        "candidate_source_ref": "chp-9:09_CHP-9_intro:l313-321#L319",
    },
    {
        "candidate_id": "cand-12390",
        "canonical_name": "Posthumous reception of Castiglione's prints and drawings in Haskell's p.267 account",
        "suggested_type": "event",
        "detail": "The source-described reception pattern in which admiration for Castiglione's prints and drawings became fervent and widespread after Zaccaria Sagredo's death. Haskell gives no complete audience, individual works or precise start date; preserve this as the author's broad chronological generalization.",
        "candidate_source_ref": "chp-9:09_CHP-9_intro:l313-321#L316",
    },
    {
        "candidate_id": "cand-12391",
        "canonical_name": "Unidentified traveller quoted on Venetian noble younger sons (Haskell, p.268)",
        "suggested_type": "person",
        "detail": "An unnamed traveller whose observation Haskell reports about the Venetian nobility and younger sons. The source gives no identity; retain the nested attribution and do not treat the report as an independently verified social rule.",
        "candidate_source_ref": "chp-9:09_CHP-9_sec_ii:l6-16#L11",
    },
]
NEW_MENTIONS = [
    {
        "mention_id": "m-chp9-p267-mantuan-market-picture-group",
        "segment_id": "chp-9:09_CHP-9_intro:l313-321",
        "candidate_id": "cand-12388",
        "surface_form": "a great number of pictures from Mantua",
        "note": "Source-defined group; the source does not enumerate its members or establish that all belonged to the Gonzaga ducal collection.",
    },
    {
        "mention_id": "m-chp9-p267-art-market",
        "segment_id": "chp-9:09_CHP-9_intro:l313-321",
        "candidate_id": "cand-12389",
        "surface_form": "market",
        "note": "Nested within the existing 'Venetian market' place mention; records the market concept separately from Venice as a place.",
    },
    {
        "mention_id": "m-chp9-p267-admiration-event",
        "segment_id": "chp-9:09_CHP-9_intro:l313-321",
        "candidate_id": "cand-12390",
        "surface_form": "This admiration for Castiglione’s prints and drawings",
        "note": "Source-defined reception pattern; retain Haskell's broad wording and chronology.",
    },
    {
        "mention_id": "m-chp9-p268-modern-painting-market",
        "segment_id": "chp-9:09_CHP-9_sec_ii:l6-16",
        "candidate_id": "cand-12389",
        "surface_form": "a market for modern painting",
        "note": "The local Venetian art-market concept in Haskell's account; 'elsewhere' remains unspecified.",
    },
]
TARGETS = {
    "st-chp9-p267-mantua-pictures-entered-venetian-market",
    "st-chp9-p267-posthumous-castiglione-reception",
    "st-chp9-p268-church-altarpiece-market",
    "st-chp9-p268-traveller-younger-sons",
}


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
        ("entity-candidates.csv", candidate_raw),
        ("mentions.csv", mention_raw),
        ("book-statements.jsonl", statement_raw),
    ):
        if digest(data) != EXPECTED_HASHES[name]:
            raise ValueError(f"Input changed since this batch was reviewed: {name}")

    segments = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    segment_index = {row["segment_id"]: row for row in segments}
    segment_texts: dict[str, str] = {}
    for segment_id, expected_hash in SEGMENT_HASHES.items():
        segment = segment_index.get(segment_id)
        if segment is None or segment.get("sha256") != expected_hash:
            raise ValueError(f"Reviewed source segment changed: {segment_id}")
        source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8").splitlines()
        segment_texts[segment_id] = "\n".join(
            source_lines[int(segment["line_start"]) - 1 : int(segment["line_end"])]
        )

    candidates_by_id = {row["candidate_id"]: row for row in candidates}
    existing_natural_keys = {
        (row.get("canonical_name", "").strip().casefold(), row.get("suggested_type", "").strip())
        for row in candidates
    }
    for candidate in NEW_CANDIDATES:
        if candidate["candidate_id"] in candidates_by_id:
            raise ValueError(f"Candidate ID already exists: {candidate['candidate_id']}")
        natural_key = (candidate["canonical_name"].strip().casefold(), candidate["suggested_type"])
        if natural_key in existing_natural_keys:
            raise ValueError(f"Candidate natural key already exists: {candidate['canonical_name']}")
        existing_natural_keys.add(natural_key)

    mention_by_id = {row["mention_id"]: row for row in mentions}
    traveller_mention = mention_by_id.get("m-chp9-p268-traveller")
    if (
        traveller_mention is None
        or traveller_mention.get("segment_id") != "chp-9:09_CHP-9_sec_ii:l6-16"
        or traveller_mention.get("candidate_id") != "cand-8677"
        or traveller_mention.get("surface_form") != "a traveller"
        or traveller_mention.get("start_char") != "1394"
        or traveller_mention.get("end_char") != "1405"
    ):
        raise ValueError("Expected existing traveller mention is absent or changed")
    existing_spans = {
        (row["segment_id"], row["start_char"], row["end_char"])
        for row in mentions
    }
    for mention in NEW_MENTIONS:
        if mention["mention_id"] in mention_by_id:
            raise ValueError(f"Mention ID already exists: {mention['mention_id']}")
        segment_id = mention["segment_id"]
        surface = mention["surface_form"]
        start = segment_texts[segment_id].find(surface)
        if start < 0 or segment_texts[segment_id].find(surface, start + 1) >= 0:
            raise ValueError(f"Mention surface must occur exactly once in reviewed segment: {surface}")
        end = start + len(surface)
        if (segment_id, str(start), str(end)) in existing_spans:
            raise ValueError(f"A mention already occupies the exact span: {surface}")
        mention["start_char"] = str(start)
        mention["end_char"] = str(end)

    rows = [json.loads(line) for line in statement_raw.decode("utf-8").splitlines() if line.strip()]
    before_counts = endpoint_counts(rows)
    if before_counts != (415, 258, 53, 104):
        raise ValueError(f"Unexpected pre-update endpoint counts: {before_counts}")
    statement_index = {row["statement_id"]: row for row in rows}
    if not TARGETS.issubset(statement_index):
        raise ValueError("One or more reviewed p.267-268 statements are missing")
    targets = [statement_index[statement_id] for statement_id in TARGETS]
    if any(not is_open(row) for row in targets):
        raise ValueError("One or more reviewed statements no longer have open endpoints")
    expected_originals = {
        "st-chp9-p267-mantua-pictures-entered-venetian-market": (None, None),
        "st-chp9-p267-posthumous-castiglione-reception": ("cand-0602", None),
        "st-chp9-p268-church-altarpiece-market": ("cand-8672", None),
        "st-chp9-p268-traveller-younger-sons": (None, "cand-8677"),
    }
    for statement_id, endpoints in expected_originals.items():
        row = statement_index[statement_id]
        if (row.get("subject_candidate_id"), row.get("object_candidate_id")) != endpoints:
            raise ValueError(f"Reviewed endpoints changed: {statement_id}")

    candidate_rows = []
    for candidate in NEW_CANDIDATES:
        candidate_rows.append({
            "candidate_id": candidate["candidate_id"], "index_entry_id": "",
            "canonical_name": candidate["canonical_name"], "index_page_range": "",
            "suggested_type": candidate["suggested_type"], "status": "open", "index_source_file": "",
            "sub_entry": "", "detail": candidate["detail"], "exclude_reason": "",
            "candidate_origin": "body-mention", "candidate_source_ref": candidate["candidate_source_ref"],
        })
    candidate_after = append_rows(candidate_raw, candidate_fields, candidate_rows)
    mention_rows = []
    for mention in NEW_MENTIONS:
        mention_rows.append({
            "mention_id": mention["mention_id"], "segment_id": mention["segment_id"],
            "candidate_id": mention["candidate_id"], "surface_form": mention["surface_form"],
            "start_char": mention["start_char"], "end_char": mention["end_char"], "note": mention["note"],
        })
    updated_mentions = [dict(row) for row in mentions]
    for row in updated_mentions:
        if row["mention_id"] == "m-chp9-p268-traveller":
            row["candidate_id"] = "cand-12391"
            row["note"] = "Unnamed speaker of the reported observation; identity remains unknown."
            break
    mention_after = rewrite_csv(mention_raw, mention_fields, updated_mentions + mention_rows)

    statement_index["st-chp9-p267-mantua-pictures-entered-venetian-market"].update({
        "subject_candidate_id": "cand-12388", "object_candidate_id": "cand-12389",
    })
    q = statement_index["st-chp9-p267-mantua-pictures-entered-venetian-market"]["qualifiers"]
    q["claim"] = "Haskell says a great number of pictures from Mantua appeared on the Venetian art market despite the inheritance claim."
    q["mentioned_candidate_ids"] = list(dict.fromkeys((q.get("mentioned_candidate_ids") or []) + ["cand-12388", "cand-12389"]))
    q["relation_candidate_note"] = "The source defines an unidentified group of pictures from Mantua and reports that they appeared on the Venetian market. It does not identify individual pictures or establish that all came from the Gonzaga ducal collection; the market term is distinct from Venice as a place."
    q.pop("open_endpoint_reason", None)

    statement_index["st-chp9-p267-posthumous-castiglione-reception"]["object_candidate_id"] = "cand-12390"
    q = statement_index["st-chp9-p267-posthumous-castiglione-reception"]["qualifiers"]
    q["mentioned_candidate_ids"] = list(dict.fromkeys((q.get("mentioned_candidate_ids") or []) + ["cand-12390"]))
    q["relation_candidate_note"] = "The object is a source-defined reception pattern, not an individually identified audience or complete list of works. Preserve Haskell's broad chronology and do not claim that no earlier individual admired Castiglione."
    q.pop("open_endpoint_reason", None)

    statement_index["st-chp9-p268-church-altarpiece-market"]["object_candidate_id"] = "cand-12389"
    q = statement_index["st-chp9-p268-church-altarpiece-market"]["qualifiers"]
    q["mentioned_candidate_ids"] = list(dict.fromkeys((q.get("mentioned_candidate_ids") or []) + ["cand-12389"]))
    q["relation_candidate_note"] = "Haskell explicitly links the Church's demand for altarpieces to a market for modern painting. The source does not name a venue; the local market concept is kept distinct from Venice as a place and from any individual commission."
    q.pop("open_endpoint_reason", None)

    statement_index["st-chp9-p268-traveller-younger-sons"]["subject_candidate_id"] = "cand-12391"
    q = statement_index["st-chp9-p268-traveller-younger-sons"]["qualifiers"]
    q["mentioned_candidate_ids"] = list(dict.fromkeys((q.get("mentioned_candidate_ids") or []) + ["cand-12391"]))
    q["relation_candidate_note"] = "The subject is a source-defined, unnamed traveller, with no identity inferred. Keep the reported observation nested under Haskell and retain its generalization about Venetian noble younger sons."
    q.pop("open_endpoint_reason", None)

    after_counts = endpoint_counts(rows)
    if after_counts != (411, 256, 52, 103):
        raise ValueError(f"Unexpected post-update endpoint counts: {after_counts}")
    statement_after = ("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)).encode("utf-8")
    print("reviewed=p.267 Mantua-picture group, Venetian art market and Castiglione reception; p.268 Church market and unnamed traveller attribution")
    print("resolved=4 open relation candidates; added 4 source-defined candidates and 4 exact mentions; corrected the existing traveller mention mapping")
    print(f"candidates={len(candidates)}->{len(candidates)+len(candidate_rows)}; mentions={len(mentions)}->{len(updated_mentions)+len(mention_rows)}; statements={len(rows)}")
    print(f"open_endpoints={before_counts}->{after_counts}")
    for name, before, after in (
        ("entity-candidates.csv", candidate_raw, candidate_after),
        ("mentions.csv", mention_raw, mention_after),
        ("book-statements.jsonl", statement_raw, statement_after),
    ):
        print(f"{name} sha256 {digest(before)}->{digest(after)}")
    if args.preview:
        return 0

    outputs = (
        (CANDIDATES, candidate_after),
        (MENTIONS, mention_after),
        (STATEMENTS, statement_after),
    )
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
