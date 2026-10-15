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
PDF = ROOT / "02-sources/01-book/CHP-15.pdf"
PDF_SHA256 = "357e830cc4e880909edd62975bfcd06ade1c2b432d8866229831025fe86f2885"
SEGMENTS_TO_CHECK = {
    "chp-15:15_CHP-15_sec_i:l27-36": "71e4bbafdb118c58add17b0f68b00575cf85e0efce419d2d81bb56807fea5609",
    "chp-15:15_CHP-15_sec_i:l38-41": "dbe5bb511b921cb9d05498aa53bbe0bf0710279331791671727a9ba64ad1d340",
}
ASSET_SHA256 = "798e2903ab45c8a90ac5be9746c43964007426d3b2e2723baa20332665d11624"
PATRONAGE_ID = "st-chp15-p363-daniele-continued-patronage-partial"
OUTCOME_ID = "st-chp15-p364-denunciation-to-no-avail"
GROUP_CANDIDATE_ID = "cand-12422"
GROUP_MENTION_ID = "m-s2-chp15-p363-contemporary-artists-patronage"
GROUP_PHRASE = "contemporary artists"
EXPECTED_HASHES = {
    "statements": "8a7b026e7ed57ff9f8435049d59b3be67264f1ed3c2fca3a50154a28c99aea38",
    "mentions": "9ed666c4eafce131efd41c489b29d8a0214ba6669fc2a21c202a6db28133d3c7",
    "candidates": "0f990b0e9fba758ccfeeed84ef0e7336e21716d18cce35eec70bbb1fcf63dbc4",
}
BACKUP_SUFFIX = ".bak-s2-chp15-p363-p364-group-outcome-20261015"
TEMP_SUFFIX = ".tmp-s2-chp15-p363-p364-group-outcome-20261015"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_jsonl(raw: bytes) -> list[dict]:
    return [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]


def parse_csv(raw: bytes) -> tuple[bool, list[str], list[dict[str, str]]]:
    bom = raw.startswith(b"\xef\xbb\xbf")
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    return bom, list(reader.fieldnames or []), list(reader)


def append_csv_record(raw: bytes, key: str, addition: dict[str, str]) -> bytes:
    bom, fields, parsed = parse_csv(raw)
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve the p.363 patronage group and classify p.364's event outcome.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--expected-statements-sha256")
    parser.add_argument("--expected-mentions-sha256")
    parser.add_argument("--expected-candidates-sha256")
    args = parser.parse_args()

    if sha(PDF.read_bytes()) != PDF_SHA256:
        raise ValueError("Reviewed CHP-15.pdf changed.")
    segment_rows = read_jsonl(SEGMENTS.read_bytes())
    segments = {r["segment_id"]: r for r in segment_rows if r.get("segment_id") in SEGMENTS_TO_CHECK}
    if set(segments) != set(SEGMENTS_TO_CHECK):
        raise ValueError("A reviewed p.363/p.364 segment is missing or duplicated.")
    texts = {}
    for segment_id, expected_hash in SEGMENTS_TO_CHECK.items():
        segment = segments[segment_id]
        if segment.get("sha256") != expected_hash or segment.get("asset_sha256") != ASSET_SHA256:
            raise ValueError(f"Reviewed segment metadata changed: {segment_id}")
        lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8").splitlines()
        texts[segment_id] = "\n".join(lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
        if sha(texts[segment_id].encode("utf-8")) != expected_hash:
            raise ValueError(f"Reviewed source text changed: {segment_id}")
    group_segment_id = "chp-15:15_CHP-15_sec_i:l38-41"
    if texts[group_segment_id].count(GROUP_PHRASE) != 1:
        raise ValueError("The p.364 recipient group phrase is missing or not unique.")

    raw = {
        "statements": STATEMENTS.read_bytes(),
        "mentions": MENTIONS.read_bytes(),
        "candidates": CANDIDATES.read_bytes(),
    }
    actual = {name: sha(data) for name, data in raw.items()}
    if actual != EXPECTED_HASHES:
        raise ValueError(f"Protected table snapshot changed: {actual}")
    statements = read_jsonl(raw["statements"])
    if len(statements) != 15158:
        raise ValueError("Unexpected statement inventory.")
    by_id = {r["statement_id"]: r for r in statements}
    if len(by_id) != len(statements):
        raise ValueError("Duplicate statement IDs.")
    _, candidate_fields, candidates = parse_csv(raw["candidates"])
    _, mention_fields, mentions = parse_csv(raw["mentions"])
    candidate_ids = {r["candidate_id"] for r in candidates}
    mention_ids = {r["mention_id"] for r in mentions}
    if GROUP_CANDIDATE_ID in candidate_ids or GROUP_MENTION_ID in mention_ids:
        raise ValueError("Planned p.363 group candidate or mention ID already exists.")

    patronage = by_id.get(PATRONAGE_ID)
    outcome = by_id.get(OUTCOME_ID)
    if not patronage or not outcome:
        raise ValueError("A p.363/p.364 target statement is missing.")
    patronage = json.loads(json.dumps(patronage, ensure_ascii=False))
    pq = patronage.get("qualifiers") or {}
    if (
        patronage.get("segment_id") != "chp-15:15_CHP-15_sec_i:l27-36"
        or patronage.get("subject_candidate_id") != "cand-1001"
        or patronage.get("object_candidate_id")
        or pq.get("relation_candidate") is not True
        or pq.get("open_endpoint_reason")
        or "chp-15:15_CHP-15_sec_i:l38-41" not in pq.get("cross_reference_segments", [])
    ):
        raise ValueError("The p.363 patronage statement no longer matches the reviewed open state.")
    patronage["object_candidate_id"] = GROUP_CANDIDATE_ID
    pq["mentioned_candidate_ids"] = list(dict.fromkeys(pq.get("mentioned_candidate_ids", []) + [GROUP_CANDIDATE_ID]))
    pq["qualification"] = (
        "P.364 L39 completes the sentence with 'patronage of contemporary artists'. The broad recipient group is represented without naming individual artists or commissions."
    )
    pq["relation_candidate_note"] = (
        "Haskell explicitly states that Daniele continued the family's patronage of contemporary artists; the endpoint records only this source-defined group, not individual recipients."
    )
    patronage["qualifiers"] = pq

    outcome = json.loads(json.dumps(outcome, ensure_ascii=False))
    oq = outcome.get("qualifiers") or {}
    if (
        outcome.get("segment_id") != "chp-15:15_CHP-15_sec_i:l38-41"
        or outcome.get("subject_candidate_id") != "cand-11525"
        or outcome.get("object_candidate_id")
        or oq.get("relation_candidate") is not True
        or oq.get("open_endpoint_reason")
    ):
        raise ValueError("The p.364 outcome statement no longer matches the reviewed state.")
    oq["relation_candidate"] = False
    oq["relation_candidate_note"] = (
        "This records the reported outcome of the denunciation event. 'To no avail' is an event-state claim and supplies no independent entity endpoint or stated response by the Inquisitors."
    )
    outcome["qualifiers"] = oq

    replacements = {PATRONAGE_ID: patronage, OUTCOME_ID: outcome}
    bom = raw["statements"].startswith(b"\xef\xbb\xbf")
    output: list[str] = []
    seen: set[str] = set()
    for line in raw["statements"].decode("utf-8-sig").splitlines(keepends=True):
        body = line.rstrip("\r\n")
        ending = line[len(body):]
        row = json.loads(body)
        sid = row.get("statement_id")
        if sid in replacements:
            output.append(json.dumps(replacements[sid], ensure_ascii=False, separators=(",", ":")) + ending)
            seen.add(sid)
        else:
            output.append(line)
    if seen != set(replacements):
        raise ValueError("The p.363/p.364 statements were not rewritten exactly once.")
    statement_out = (("\ufeff" if bom else "") + "".join(output)).encode("utf-8")

    start = texts[group_segment_id].index(GROUP_PHRASE)
    candidate = {
        "candidate_id": GROUP_CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "Contemporary artists whose patronage the Farsetti family continued through Daniele (p.363)",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell says Daniele continued the Farsetti family's patronage of contemporary artists. This source-defined group records only that broad recipient class; no members, individual commissions, or roster are identified.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{group_segment_id}#L39",
    }
    mention = {
        "mention_id": GROUP_MENTION_ID,
        "segment_id": group_segment_id,
        "candidate_id": GROUP_CANDIDATE_ID,
        "surface_form": GROUP_PHRASE,
        "start_char": str(start),
        "end_char": str(start + len(GROUP_PHRASE)),
        "note": "Unspecified recipients of the Farsetti family's continued patronage; individuals and commissions are not named.",
    }
    candidate_out = append_csv_record(raw["candidates"], "candidate_id", candidate)
    mention_out = append_csv_record(raw["mentions"], "mention_id", mention)
    after = read_jsonl(statement_out)
    open_rows = [
        r for r in after
        if (r.get("qualifiers") or {}).get("relation_candidate") is True
        and (not r.get("subject_candidate_id") or not r.get("object_candidate_id"))
    ]
    no_reason = sum(not (r.get("qualifiers") or {}).get("open_endpoint_reason") for r in open_rows)
    flag_counts = {True: 0, False: 0}
    for row in after:
        flag = (row.get("qualifiers") or {}).get("relation_candidate")
        if flag in flag_counts:
            flag_counts[flag] += 1
    if (len(open_rows), no_reason, flag_counts[True], flag_counts[False]) != (336, 8, 10399, 4759):
        raise ValueError(f"Unexpected post-edit counts: open={len(open_rows)}, no_reason={no_reason}, flags={flag_counts}")
    if (len(parse_csv(candidate_out)[2]), len(parse_csv(mention_out)[2])) != (12400, 26614):
        raise ValueError("Unexpected post-edit candidate or mention inventory.")
    if texts[group_segment_id][start:start + len(GROUP_PHRASE)] != GROUP_PHRASE:
        raise ValueError("The p.363 recipient group mention span is not exact.")

    outputs = {STATEMENTS: statement_out, MENTIONS: mention_out, CANDIDATES: candidate_out}
    print("reviewed=CHP-15 p.363 physical page 3 and p.364 physical page 4 continuation")
    print("decision=map Daniele's continued patronage to the source-defined unnamed contemporary-artist group; classify 'to no avail' as an event outcome claim")
    print(f"open_true=338->{len(open_rows)}; no_reason=10->{no_reason}; relation_flags=true {10400}->{flag_counts[True]}, false {4758}->{flag_counts[False]}; candidates=12399->{len(parse_csv(candidate_out)[2])}; mentions=26613->{len(parse_csv(mention_out)[2])}")
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
