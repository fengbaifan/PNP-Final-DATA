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
SEGMENTS = TABLES / "segments.jsonl"
STATEMENTS = TABLES / "book-statements.jsonl"
MENTIONS = TABLES / "mentions.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
PDF = ROOT / "02-sources/01-book/CHP-13.pdf"
PDF_SHA256 = "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc"
ASSET_SHA256 = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"
SEGMENT_HASHES = {
    "chp-13:13_CHP-13_intro:l179-251": "f592d5913122cf2c4c2e7db9a39b8016c82dbc232a869018793ef11096faacb9",
    "chp-13:13_CHP-13_intro:l161-171": "3b428ba03ee1060eafa7b250f5ad4831613f35cc4ab909b49703bf20a35bd37c",
}
MARIN_STATEMENT_ID = "st-chp13-p332-n4-marin-counterview"
MARIN_TERM_ID = "cand-12421"
MARIN_MENTION_ID = "m-s2-ch13-p332-marin-optimistic-view"
P344_STATEMENT_ID = "st-chp13-p344-zanetti-1752-incomplete_letter_fragment"
QUOTE_CONTINUATION_ID = "st-chp13-p345-zanetti-1752-quote-continuation"
P345_ENDPOINTS = {
    "st-chp13-p345-zanetti-1752-quote-continuation": ("cand-2838", "cand-3461"),
    "st-chp13-p345-younger-zanetti-cousin": ("cand-2854", "cand-2838"),
    "st-chp13-p345-zanettis-collaborated-on-two-books": ("cand-2854", "cand-2838"),
    "st-chp13-p345-varie-pitture-1760": ("cand-10117", "cand-2854"),
    "st-chp13-p345-ricche-miniere-edited-1733": ("cand-10118", "cand-2854"),
    "st-chp13-p345-della-pittura-veneziana-1771": ("cand-9837", "cand-2854"),
    "st-chp13-p345-monaco-1743-collection": ("cand-10115", "cand-1682"),
    "st-chp13-p345-monaco-1763-1779-editions": ("cand-10116", "cand-2773"),
    "st-chp13-p345-monaco-collection-advertised-dealer": ("cand-1682", "cand-7618"),
    "st-chp13-p345-toni-born-near-modena": ("cand-2640", "cand-3416"),
    "st-chp13-p345-toni-settled-in-venice": ("cand-2640", "cand-2719"),
    "st-chp13-p345-toni-gambled-on-ricci-behalf": ("cand-2640", "cand-2154"),
    "st-chp13-p345-toni-contact-with-pittoni": ("cand-2640", "cand-1950"),
    "st-chp13-p345-toni-collections-left-to-novelli-1748": ("cand-2640", "cand-1760"),
    "st-chp13-p345-toni-discussions-may-have-shaped-novelli": ("cand-2640", "cand-1760"),
}
EXPECTED_HASHES = {
    "statements": "15e0d2fc7438e3d7f935ebf6218285c9da129512c2da5a3f0ffeeb73a5ca6d77",
    "mentions": "239f261993951f3c43edad685f822659f42575275bf9ce397ae2644e2d53aaa6",
    "candidates": "1e1715ea789a67678fc11199d723bc1837abfc48be9d642b0ef848ada0dcb752",
}
BACKUP_SUFFIX = ".bak-s2-chp13-p332-p345-open-endpoints-20261015"
TEMP_SUFFIX = ".tmp-s2-chp13-p332-p345-open-endpoints-20261015"
VIEW_PHRASE = "the optimistic view generally given of eighteenth-century engraving in Venice"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def jsonl(raw: bytes) -> list[dict]:
    return [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]


def csv_rows(raw: bytes) -> tuple[bool, list[str], list[dict[str, str]]]:
    bom = raw.startswith(b"\xef\xbb\xbf")
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    return bom, list(reader.fieldnames or []), list(reader)


def append_csv_record(raw: bytes, key: str, addition: dict[str, str]) -> bytes:
    bom, fields, parsed = csv_rows(raw)
    ids = [row.get(key, "") for row in parsed]
    if not fields or len(ids) != len(set(ids)) or set(addition) != set(fields):
        raise ValueError(f"Invalid {key} table schema or duplicate IDs.")
    if addition[key] in set(ids):
        raise ValueError(f"Planned {key} ID already exists.")
    text = raw.decode("utf-8-sig")
    physical = text.splitlines(keepends=True)
    newline = "\r\n" if b"\r\n" in raw else "\n"
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if reader.fieldnames != fields or reader.line_num != 1:
        raise ValueError("CSV header could not be mapped to physical lines.")
    previous_line = reader.line_num
    output = [physical[0]]
    for _row in reader:
        end_line = reader.line_num
        chunk = "".join(physical[previous_line:end_line])
        if not chunk:
            raise ValueError("Could not map CSV record to physical lines.")
        output.append(chunk)
        previous_line = end_line
    stream = io.StringIO(newline="")
    csv.DictWriter(stream, fieldnames=fields, lineterminator=newline).writerow(addition)
    output.append(stream.getvalue())
    return (("\ufeff" if bom else "") + "".join(output)).encode("utf-8")


def rewrite_statements(raw: bytes, replacements: dict[str, dict]) -> bytes:
    bom = raw.startswith(b"\xef\xbb\xbf")
    out: list[str] = []
    found: set[str] = set()
    for line in raw.decode("utf-8-sig").splitlines(keepends=True):
        body = line.rstrip("\r\n")
        ending = line[len(body):]
        row = json.loads(body)
        sid = row.get("statement_id")
        if sid in replacements:
            if sid in found:
                raise ValueError(f"Duplicate statement ID: {sid}")
            out.append(json.dumps(replacements[sid], ensure_ascii=False, separators=(",", ":")) + ending)
            found.add(sid)
        else:
            out.append(line)
    if found != set(replacements):
        raise ValueError(f"Statement targets missing or duplicated: {set(replacements) - found}")
    return (("\ufeff" if bom else "") + "".join(out)).encode("utf-8")


def source_text(segment: dict) -> str:
    lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8").splitlines()
    first = int(segment["line_start"]) - 1
    last = int(segment["line_end"])
    return "\n".join(lines[first:last])


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve source-supported open endpoints in CHP-13 p.332 and p.345.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--expected-statements-sha256")
    parser.add_argument("--expected-mentions-sha256")
    parser.add_argument("--expected-candidates-sha256")
    args = parser.parse_args()

    if sha(PDF.read_bytes()) != PDF_SHA256:
        raise ValueError("Reviewed CHP-13.pdf changed.")
    segment_rows = jsonl(SEGMENTS.read_bytes())
    segments = {r["segment_id"]: r for r in segment_rows if r.get("segment_id") in SEGMENT_HASHES}
    if set(segments) != set(SEGMENT_HASHES):
        raise ValueError("A reviewed CHP-13 segment is missing or duplicated.")
    texts: dict[str, str] = {}
    for sid, expected_hash in SEGMENT_HASHES.items():
        segment = segments[sid]
        if segment.get("sha256") != expected_hash or segment.get("asset_sha256") != ASSET_SHA256:
            raise ValueError(f"Reviewed segment metadata changed: {sid}")
        texts[sid] = source_text(segment)
        if sha(texts[sid].encode("utf-8")) != expected_hash:
            raise ValueError(f"Reviewed source text changed: {sid}")
    view_text = texts["chp-13:13_CHP-13_intro:l179-251"]
    if view_text.count(VIEW_PHRASE) != 1:
        raise ValueError("The p.332 source phrase is missing or not unique.")

    raw = {
        "statements": STATEMENTS.read_bytes(),
        "mentions": MENTIONS.read_bytes(),
        "candidates": CANDIDATES.read_bytes(),
    }
    actual = {name: sha(data) for name, data in raw.items()}
    if actual != EXPECTED_HASHES:
        raise ValueError(f"Protected table snapshot changed: {actual}")
    statements = jsonl(raw["statements"])
    _, _, mention_rows = csv_rows(raw["mentions"])
    _, _, candidate_rows = csv_rows(raw["candidates"])
    if (len(statements), len(mention_rows), len(candidate_rows)) != (15158, 26612, 12398):
        raise ValueError("Unexpected table inventory.")
    statement_by_id = {r["statement_id"]: r for r in statements}
    if len(statement_by_id) != len(statements):
        raise ValueError("Duplicate statement IDs in source table.")
    candidate_ids = {r["candidate_id"] for r in candidate_rows}
    mention_ids = {r["mention_id"] for r in mention_rows}
    if MARIN_TERM_ID in candidate_ids or MARIN_MENTION_ID in mention_ids:
        raise ValueError("Planned p.332 term or mention ID already exists.")
    if len(P345_ENDPOINTS) != 15 or not set(P345_ENDPOINTS).issubset(statement_by_id):
        raise ValueError("The p.345 statement set is incomplete.")

    replacements: dict[str, dict] = {}
    for sid, endpoints in P345_ENDPOINTS.items():
        row = json.loads(json.dumps(statement_by_id[sid], ensure_ascii=False))
        q = row.get("qualifiers") or {}
        if row.get("segment_id") != "chp-13:13_CHP-13_intro:l161-171" or q.get("relation_candidate") is not True:
            raise ValueError(f"Unexpected p.345 target: {sid}")
        if row.get("subject_candidate_id") or row.get("object_candidate_id") or q.get("open_endpoint_reason"):
            raise ValueError(f"p.345 target is no longer in the reviewed open state: {sid}")
        if not set(q.get("mentioned_candidate_ids", [])) >= set(endpoints):
            raise ValueError(f"A resolved endpoint lacks a source mention: {sid}")
        row["subject_candidate_id"], row["object_candidate_id"] = endpoints
        if sid == QUOTE_CONTINUATION_ID:
            p344 = statement_by_id.get(P344_STATEMENT_ID)
            if not p344 or p344.get("qualifiers", {}).get("quote_continuation_statement_id") != sid:
                raise ValueError("p.344 does not link to the expected p.345 quote continuation.")
            if row.get("original_quote") != "or three times before being ready to spend it on that sort of thing...":
                raise ValueError("The p.345 quote continuation text changed.")
            q["speaker"] = "A. M. Zanetti, quoted by Haskell"
            q["text_layer"] = "quoted first-person statement"
            q["continued_from_segment_id"] = "chp-13:13_CHP-13_intro:l116-122"
            q["continued_from_source_line"] = 121
            q["continued_from_statement_id"] = P344_STATEMENT_ID
            q["continuation_status"] = "closed"
        row["qualifiers"] = q
        replacements[sid] = row

    marin = statement_by_id.get(MARIN_STATEMENT_ID)
    if not marin:
        raise ValueError("The p.332 Marin statement is missing.")
    marin = json.loads(json.dumps(marin, ensure_ascii=False))
    marin_q = marin.get("qualifiers") or {}
    if (
        marin.get("segment_id") != "chp-13:13_CHP-13_intro:l179-251"
        or marin.get("subject_candidate_id") != "cand-10139"
        or marin.get("object_candidate_id")
        or marin_q.get("relation_candidate") is not True
        or marin_q.get("open_endpoint_reason")
    ):
        raise ValueError("The p.332 Marin statement no longer matches its reviewed open state.")
    marin["object_candidate_id"] = MARIN_TERM_ID
    marin_q["mentioned_candidate_ids"] = list(dict.fromkeys(marin_q.get("mentioned_candidate_ids", []) + [MARIN_TERM_ID]))
    marin_q["qualification"] = (
        "The term represents the view Haskell says Marin challenges; this note does not name its author or state Marin's alternative argument."
    )
    marin_q["relation_candidate_note"] = (
        "The cited Marin volume is the source endpoint, and the general optimistic view of eighteenth-century Venetian engraving is the challenged object."
    )
    marin["qualifiers"] = marin_q
    replacements[MARIN_STATEMENT_ID] = marin

    candidate = {
        "candidate_id": MARIN_TERM_ID,
        "index_entry_id": "",
        "canonical_name": "Optimistic view of eighteenth-century Venetian engraving described in Haskell's p.332 note 4",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell's note says Marin challenges the optimistic view generally given of eighteenth-century engraving in Venice. This source-defined term represents that view as the object of the report; the note does not identify its author or specify the alternative argument.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-13:13_CHP-13_intro:l179-251#L183",
    }
    start = view_text.index(VIEW_PHRASE)
    mention = {
        "mention_id": MARIN_MENTION_ID,
        "segment_id": "chp-13:13_CHP-13_intro:l179-251",
        "candidate_id": MARIN_TERM_ID,
        "surface_form": VIEW_PHRASE,
        "start_char": str(start),
        "end_char": str(start + len(VIEW_PHRASE)),
        "note": "The view Haskell reports Marin challenging; its author and precise argument are not named in this note.",
    }

    statement_out = rewrite_statements(raw["statements"], replacements)
    mention_out = append_csv_record(raw["mentions"], "mention_id", mention)
    candidate_out = append_csv_record(raw["candidates"], "candidate_id", candidate)
    after = jsonl(statement_out)
    open_rows = [
        r for r in after
        if (r.get("qualifiers") or {}).get("relation_candidate") is True
        and (not r.get("subject_candidate_id") or not r.get("object_candidate_id"))
    ]
    no_reason = sum(not (r.get("qualifiers") or {}).get("open_endpoint_reason") for r in open_rows)
    if len(open_rows) != 341 or no_reason != 17:
        raise ValueError(f"Unexpected post-edit open endpoint inventory: open={len(open_rows)}, no_reason={no_reason}")
    if (len(csv_rows(mention_out)[2]), len(csv_rows(candidate_out)[2])) != (26613, 12399):
        raise ValueError("Unexpected post-edit candidate or mention inventory.")
    if view_text[start:start + len(VIEW_PHRASE)] != VIEW_PHRASE:
        raise ValueError("The p.332 mention span does not match its exact source text.")

    outputs = {STATEMENTS: statement_out, MENTIONS: mention_out, CANDIDATES: candidate_out}
    print("reviewed=CHP-13 printed p.332 note 4 / PDF physical page 1; p.345 / PDF physical page 18")
    print("decision=p.332 maps the challenged general view to a source-defined term; p.345 resolves 15 endpoints using existing mentions")
    print("quote=p.344-to-p.345 Zanetti quotation linked and attributed to Zanetti as quoted by Haskell")
    print(f"open_true={357}->{len(open_rows)}; no_reason={33}->{no_reason}; candidates={12398}->{len(csv_rows(candidate_out)[2])}; mentions={26612}->{len(csv_rows(mention_out)[2])}; statements={len(statements)}")
    for path, data in outputs.items():
        print(f"{path.name} sha256 {sha(path.read_bytes())}->{sha(data)}")
    if args.preview:
        return 0
    if {
        "statements": args.expected_statements_sha256,
        "mentions": args.expected_mentions_sha256,
        "candidates": args.expected_candidates_sha256,
    } != actual:
        raise ValueError("Apply requires the three input hashes printed by this preview.")
    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in outputs}
    temps = {path: path.with_name(path.name + TEMP_SUFFIX) for path in outputs}
    if any(path.exists() for path in backups.values()) or any(path.exists() for path in temps.values()):
        raise FileExistsError("A recovery copy or temporary table already exists.")
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    try:
        for path, data in outputs.items():
            temps[path].write_bytes(data)
        for path in outputs:
            temps[path].replace(path)
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        for path, backup in backups.items():
            shutil.copy2(backup, path)
        raise
    print("applied=yes")
    for path, backup in backups.items():
        print(f"backup={backup.relative_to(ROOT)}")
        print(f"applied_sha256={path.name}:{sha(path.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
