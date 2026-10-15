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
BACKLOG = TABLES / "candidate-backlog.csv"
BACKUP_SUFFIX = "bak-s2-chp9-p269-p271-endpoints-20261015"
EXPECTED_HASHES = {
    "entity-candidates.csv": "466b235045a59c6bf4fc6705c3050ab0b35ea7d72ee110f315447ff98924809f",
    "mentions.csv": "99be5088117ad5cb3bae6d753e2d8d221ce33e98c09a3bd46000ba1e73c6d33a",
    "book-statements.jsonl": "00025aec9fc06803da97d22b733bf4a95cf073adbdf14b80e2ed6eb7969c8188",
}
SEGMENT_HASHES = {
    "chp-9:09_CHP-9_sec_ii:l18-25": "908c9e9ac8a5a25f91200eec9d2680beb6b8345dceb66b88392c96b51bd7530d",
    "chp-9:09_CHP-9_sec_ii:l27-36": "93efb8db0766c4e0f568e4c49f04cfa8f41c4ae584666445c0682d070e260026",
    "chp-9:09_CHP-9_sec_ii:l85-127": "d00ced6fff3f96f5cf574f47f45eea80ef1b6867c581d7d017f217ee2a8a5a99",
}
EVENT_CANDIDATE = {
    "candidate_id": "cand-12392",
    "canonical_name": "Rapid rebuilding or rich decoration of Venetian parish churches described on p.269",
    "suggested_type": "event",
    "detail": "Haskell says parish churches such as S. Toma and S. Vitale were either rebuilt or richly decorated with remarkable speed. The source does not assign one action to each church; preserve the disjunction and the author's qualification of an observer's complaint.",
    "candidate_source_ref": "chp-9:09_CHP-9_sec_ii:l18-25#L19",
}
EVENT_MENTION = {
    "mention_id": "m-chp9-p269-parish-church-work-event",
    "segment_id": "chp-9:09_CHP-9_sec_ii:l18-25",
    "candidate_id": "cand-12392",
    "surface_form": "were either rebuilt or richly decorated with remarkable speed",
    "note": "Preserves Haskell's disjunctive description; no action is assigned to an individual named church.",
}
BACKLOG_FIELDS = [
    "backlog_id", "canonical_name", "suggested_type", "status", "source_id", "source_ref",
    "statement_id", "endpoint_role", "candidate_id", "ku_id", "decision_note", "process_ref",
]
BACKLOG_ROW = {
    "backlog_id": "bl-0001",
    "canonical_name": "Luigi Pavini",
    "suggested_type": "person",
    "status": "pending",
    "source_id": "haskell-1980-rev-ed",
    "source_ref": "chp-9:09_CHP-9_sec_ii:l85-127#L95",
    "statement_id": "st-chp9-p269-n05",
    "endpoint_role": "publisher of cand-8789",
    "candidate_id": "",
    "ku_id": "",
    "decision_note": "Haskell names Luigi Pavini as publisher of the 1734 pamphlet; no candidate or independent identity record is present. Resolve through S1-S3-S4 without inferring more than the source provides.",
    "process_ref": "03-processing/patrons-and-painters-full-book-s2/process/stages.md",
}
TARGETS = {
    "st-chp9-p269-n05": (None, "cand-8789"),
    "st-chp9-p269-parish-rebuilds-rebuttal": ("cand-8682", None),
    "st-chp9-p270-carmelite-patronage-comparison": ("cand-0563", None),
    "st-chp9-p270-n06": (None, "cand-8640"),
    "st-chp9-p271-n01": (None, "cand-8795"),
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
    if BACKLOG.exists():
        raise FileExistsError("candidate-backlog.csv appeared after this batch was prepared")

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

    candidate_ids = {row["candidate_id"] for row in candidates}
    if EVENT_CANDIDATE["candidate_id"] in candidate_ids:
        raise ValueError("p.269 event candidate ID already exists")
    natural_key = (EVENT_CANDIDATE["canonical_name"].strip().casefold(), EVENT_CANDIDATE["suggested_type"])
    if any((row["canonical_name"].strip().casefold(), row["suggested_type"].strip()) == natural_key for row in candidates):
        raise ValueError("p.269 event candidate natural key already exists")
    mention_ids = {row["mention_id"] for row in mentions}
    if EVENT_MENTION["mention_id"] in mention_ids:
        raise ValueError("p.269 event mention ID already exists")
    text = segment_texts[EVENT_MENTION["segment_id"]]
    start = text.find(EVENT_MENTION["surface_form"])
    if start < 0 or text.find(EVENT_MENTION["surface_form"], start + 1) >= 0:
        raise ValueError("Reviewed p.269 event phrase is absent or repeated")
    EVENT_MENTION["start_char"] = str(start)
    EVENT_MENTION["end_char"] = str(start + len(EVENT_MENTION["surface_form"]))
    if any(
        row["segment_id"] == EVENT_MENTION["segment_id"]
        and row["start_char"] == EVENT_MENTION["start_char"]
        and row["end_char"] == EVENT_MENTION["end_char"]
        for row in mentions
    ):
        raise ValueError("Another mention already occupies the reviewed event phrase span")

    rows = [json.loads(line) for line in statement_raw.decode("utf-8").splitlines() if line.strip()]
    before_counts = endpoint_counts(rows)
    if before_counts != (411, 256, 52, 103):
        raise ValueError(f"Unexpected pre-update endpoint counts: {before_counts}")
    statement_index = {row["statement_id"]: row for row in rows}
    if not set(TARGETS).issubset(statement_index):
        raise ValueError("One or more p.269-271 reviewed statements are missing")
    for statement_id, endpoints in TARGETS.items():
        row = statement_index[statement_id]
        if not is_open(row) or (row.get("subject_candidate_id"), row.get("object_candidate_id")) != endpoints:
            raise ValueError(f"Reviewed statement changed: {statement_id}")

    p269_note = statement_index["st-chp9-p269-n05"]
    p269_note["qualifiers"]["open_endpoint_reason"] = (
        "The note explicitly names Luigi Pavini as publisher, but no candidate record exists. "
        "Track this named endpoint in candidate-backlog.csv for S1-S3-S4; do not substitute Haskell or Ferrari as publisher. "
        "Keep the citation relation open until Pavini receives a supported candidate or the endpoint is explicitly left undecided."
    )
    p269_note["qualifiers"]["relation_candidate_note"] = (
        "The object is the identified 1734 pamphlet. The missing subject is its source-named publisher Luigi Pavini, "
        "whose identity candidate is pending S1-S3-S4; the separately cited Ferrari locator is not the publisher."
    )

    parish = statement_index["st-chp9-p269-parish-rebuilds-rebuttal"]
    parish["object_candidate_id"] = EVENT_CANDIDATE["candidate_id"]
    parish["qualifiers"]["mentioned_candidate_ids"] = list(dict.fromkeys(
        (parish["qualifiers"].get("mentioned_candidate_ids") or []) + [EVENT_CANDIDATE["candidate_id"]]
    ))
    parish["qualifiers"]["relation_candidate_note"] = (
        "The object is the source-described rebuilding-or-rich-decoration event group. Haskell gives S. Toma and S. Vitale as examples "
        "but does not assign one alternative action to each church; retain the disjunction and do not generalize to every parish."
    )
    parish["qualifiers"].pop("open_endpoint_reason", None)

    comparison = statement_index["st-chp9-p270-carmelite-patronage-comparison"]
    comparison["object_candidate_id"] = "cand-2389"
    comparison["qualifiers"]["relation_candidate_note"] = (
        "The object is the Scalzi, named in the preceding sentence and referred to by 'their mother Order'; "
        "this records Haskell's comparison of patronage, not an identity or membership relation."
    )
    comparison["qualifiers"].pop("open_endpoint_reason", None)

    march = statement_index["st-chp9-p270-n06"]
    march["subject_candidate_id"] = "cand-1539"
    march["qualifiers"]["relation_candidate_note"] = (
        "The subject is the named sender Alessandro Marchesini and the object the source-defined letter locator. "
        "This records Haskell's note and does not claim independent consultation of the letter or repository witness."
    )
    march["qualifiers"].pop("open_endpoint_reason", None)

    gherardi = statement_index["st-chp9-p271-n01"]
    gherardi["subject_candidate_id"] = "cand-1155"
    gherardi["qualifiers"]["relation_candidate_note"] = (
        "The subject is the named sender P. E. Gherardi and the object the source-defined letter locator. "
        "This records Haskell's citation used to identify the visitor; it does not independently establish that the sender and visitor are the same person."
    )
    gherardi["qualifiers"].pop("open_endpoint_reason", None)

    after_counts = endpoint_counts(rows)
    if after_counts != (407, 254, 50, 103):
        raise ValueError(f"Unexpected post-update endpoint counts: {after_counts}")
    statement_after = ("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)).encode("utf-8")
    candidate_row = {
        "candidate_id": EVENT_CANDIDATE["candidate_id"], "index_entry_id": "",
        "canonical_name": EVENT_CANDIDATE["canonical_name"], "index_page_range": "",
        "suggested_type": EVENT_CANDIDATE["suggested_type"], "status": "open", "index_source_file": "",
        "sub_entry": "", "detail": EVENT_CANDIDATE["detail"], "exclude_reason": "",
        "candidate_origin": "body-mention", "candidate_source_ref": EVENT_CANDIDATE["candidate_source_ref"],
    }
    mention_row = {
        "mention_id": EVENT_MENTION["mention_id"], "segment_id": EVENT_MENTION["segment_id"],
        "candidate_id": EVENT_MENTION["candidate_id"], "surface_form": EVENT_MENTION["surface_form"],
        "start_char": EVENT_MENTION["start_char"], "end_char": EVENT_MENTION["end_char"], "note": EVENT_MENTION["note"],
    }
    candidate_after = append_rows(candidate_raw, candidate_fields, [candidate_row])
    mention_after = append_rows(mention_raw, mention_fields, [mention_row])
    backlog_stream = io.StringIO(newline="")
    backlog_writer = csv.DictWriter(backlog_stream, fieldnames=BACKLOG_FIELDS, lineterminator="\r\n")
    backlog_writer.writeheader()
    backlog_writer.writerow(BACKLOG_ROW)
    backlog_after = backlog_stream.getvalue().encode("utf-8")

    segment = segment_index["chp-9:09_CHP-9_sec_ii:l85-127"]
    if segment.get("source_id") != BACKLOG_ROW["source_id"]:
        raise ValueError("Unexpected source ID for the p.269 footnote segment")

    print("reviewed=p.269 parish-church work claim; p.270 Carmelite comparison and Marchesini letter; p.271 Gherardi letter locator")
    print("resolved=4 open relation candidates; retained p.269 note 5 open and queued named publisher Luigi Pavini")
    print("added=1 event candidate, 1 exact mention, 1 candidate-backlog row")
    print(f"candidates={len(candidates)}->{len(candidates)+1}; mentions={len(mentions)}->{len(mentions)+1}; statements={len(rows)}")
    print(f"open_endpoints={before_counts}->{after_counts}")
    for name, before, after in (
        ("entity-candidates.csv", candidate_raw, candidate_after),
        ("mentions.csv", mention_raw, mention_after),
        ("book-statements.jsonl", statement_raw, statement_after),
        ("candidate-backlog.csv", b"", backlog_after),
    ):
        print(f"{name} sha256 {digest(before)}->{digest(after)}")
    if args.preview:
        return 0

    outputs = (
        (CANDIDATES, candidate_after),
        (MENTIONS, mention_after),
        (STATEMENTS, statement_after),
        (BACKLOG, backlog_after),
    )
    pairs: list[tuple[Path, Path, Path, bytes]] = []
    for path, data in outputs:
        backup = path.with_name(f"{path.name}.{BACKUP_SUFFIX}")
        temporary = path.with_name(f"{path.name}.tmp-{BACKUP_SUFFIX}")
        if temporary.exists() or (path != BACKLOG and backup.exists()):
            raise FileExistsError(f"Recovery or temporary file already exists: {path.name}")
        pairs.append((path, backup, temporary, data))
    for path, backup, _, _ in pairs:
        if path != BACKLOG:
            shutil.copy2(path, backup)
    replaced: list[tuple[Path, Path, bool]] = []
    try:
        for _, _, temporary, data in pairs:
            temporary.write_bytes(data)
        for path, backup, temporary, _ in pairs:
            existed = path.exists()
            temporary.replace(path)
            replaced.append((path, backup, existed))
    except Exception:
        for _, _, temporary, _ in pairs:
            if temporary.exists():
                temporary.unlink()
        for path, backup, existed in replaced:
            if existed and backup.exists():
                shutil.copy2(backup, path)
            elif not existed and path.exists():
                path.unlink()
        raise
    for path, backup, _, _ in pairs:
        print(f"backup={backup.relative_to(ROOT)}" if backup.exists() else f"created={path.relative_to(ROOT)}")
        print(f"applied_sha256={path.relative_to(ROOT)}:{digest(path.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
