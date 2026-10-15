from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_i.md"
SEGMENTS = TABLES / "segments.jsonl"
SEGMENT_ID = "chp-3:03_CHP-3_sec_i:l3-14"
SOURCE_SHA256 = "a18f48c7b8bf5b161fa13a7ce26ed2935e72d9a14d555f82dfc1d85f84314255"
SEGMENT_SHA256 = "65731270d187f6441994d332868a81dc1e4dbc41b53168a2e173e46798316f26"
EXPECTED_HASHES = {
    STATEMENTS: "37bafce1c3cd895b6a9029ee7c4daaac438d29ad9599b0319d2349d16a6743cd",
    CANDIDATES: "bd8a821e545833c29e8e308e5ccba6b8c77e6d79452e0060adceeefc7bff5516",
    MENTIONS: "8215bf9cfdbde6a0d1f29998cdeeb0ea57cf907cee1c1453f3b9991180a1039e",
}
CLAIM_CANDIDATE_ID = "cand-11896"
EVENTS_CANDIDATE_ID = "cand-11897"
CLAIM_MENTION_ID = "m-chp3-seci-l3-14-0021"
EVENTS_MENTION_ID = "m-chp3-seci-l3-14-0022"
CLAIM_SPAN = "they deliberately fostered as an instrument of propaganda"
EVENTS_SPAN = "a large number of complex events"
CLASSIFICATIONS = {
    "st-chp3-seci-l3-14-charge-attributed-to-grey": (
        True,
        "Haskell says this charge was first made by an English traveller in 1620 and identifies Grey in the adjacent sentence. The claim is represented as a reported allegation; this candidate does not affirm its truth.",
    ),
    "st-chp3-seci-l3-14-haskell-evaluates-grey": (
        False,
        "This is Haskell's evaluation of Grey's Protestant convictions and understanding, not a relation between distinct entities.",
    ),
    "st-chp3-seci-l3-14-order-patronage-circumscribed": (
        True,
        "Haskell explicitly says that a large number of complex events circumscribed religious-order patronage. The source-defined group is left open; the following discussion is not treated as an exhaustive membership list.",
    ),
}
BACKUPS = {
    STATEMENTS: STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp3-seci-l3-14-residuals-20261013"),
    CANDIDATES: CANDIDATES.with_name("entity-candidates.csv.bak-s2-chp3-seci-l3-14-open-endpoints-20261013"),
    MENTIONS: MENTIONS.with_name("mentions.csv.bak-s2-chp3-seci-l3-14-open-endpoints-20261013"),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_csv(raw: bytes) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader)


def render_csv(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = "\r\n" if b"\r\n" in raw else "\n"
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator=newline, extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    result = output.getvalue().encode("utf-8")
    return b"\xef\xbb\xbf" + result if raw.startswith(b"\xef\xbb\xbf") else result


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve the three remaining section I statements with source-defined endpoints.")
    parser.add_argument("--apply", action="store_true", help="write changes after protected preview checks")
    args = parser.parse_args()

    raw_by_path = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        actual = sha256(raw_by_path[path])
        if actual != expected:
            raise SystemExit(f"protected table changed: {path.name}; expected {expected}, found {actual}")
    if sha256(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise SystemExit("protected S0 source changed")
    segment_rows = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segment_rows if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA256:
        raise SystemExit("protected segment metadata changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
    if sha256(segment_text.encode("utf-8")) != SEGMENT_SHA256:
        raise SystemExit("protected segment source lines changed")
    claim_start = segment_text.find(CLAIM_SPAN)
    events_start = segment_text.find(EVENTS_SPAN)
    if claim_start != 604 or events_start != 1792:
        raise SystemExit(f"protected mention offsets changed: claim={claim_start}, events={events_start}")

    statement_rows = [json.loads(line) for line in raw_by_path[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    statement_map = {row.get("statement_id"): row for row in statement_rows}
    if len(statement_map) != len(statement_rows) or not set(CLASSIFICATIONS).issubset(statement_map):
        raise SystemExit("target statement set changed")
    for statement_id in CLASSIFICATIONS:
        row = statement_map[statement_id]
        if row.get("segment_id") != SEGMENT_ID or row.get("qualifiers", {}).get("relation_candidate") is not None:
            raise SystemExit(f"target is no longer an unset statement: {statement_id}")
        q = row["qualifiers"]
        cited = " ".join(" ".join(source_lines[int(q["source_line_start"]) - 1:int(q["source_line_end"])]).split())
        quote = " ".join(row.get("original_quote", "").split())
        if quote not in cited:
            raise SystemExit(f"quote does not match cited source lines: {statement_id}")

    candidate_fields, candidate_rows = load_csv(raw_by_path[CANDIDATES])
    mention_fields, mention_rows = load_csv(raw_by_path[MENTIONS])
    candidate_ids = {row.get("candidate_id") for row in candidate_rows}
    mention_ids = {row.get("mention_id") for row in mention_rows}
    if candidate_ids.intersection({CLAIM_CANDIDATE_ID, EVENTS_CANDIDATE_ID}):
        raise SystemExit("candidate ID already exists")
    if mention_ids.intersection({CLAIM_MENTION_ID, EVENTS_MENTION_ID}):
        raise SystemExit("mention ID already exists")

    new_candidates = [
        {
            "candidate_id": CLAIM_CANDIDATE_ID,
            "index_entry_id": "",
            "canonical_name": "Claim that religious Orders deliberately fostered Baroque taste as propaganda (reported allegation)",
            "index_page_range": "",
            "suggested_type": "term",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell discusses the allegation that religious Orders deliberately cultivated Baroque taste as propaganda and reports that Grey Brydges first made it in 1620. This candidate represents the attributed claim, not an independently verified historical fact.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": "chp-3:03_CHP-3_sec_i:l3-14#L6",
        },
        {
            "candidate_id": EVENTS_CANDIDATE_ID,
            "index_entry_id": "",
            "canonical_name": "Complex circumstances limiting religious Orders' patronage (unspecified group)",
            "index_page_range": "",
            "suggested_type": "term",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell says a large number of complex events circumscribed religious-order patronage but does not enumerate the group here. Later examples are not assumed to exhaust its membership.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": "chp-3:03_CHP-3_sec_i:l3-14#L12",
        },
    ]
    expected_candidate_fields = set(candidate_fields)
    if any(set(row) != expected_candidate_fields for row in new_candidates):
        raise SystemExit("candidate schema changed; refusing to append")
    candidate_rows.extend(new_candidates)

    new_mentions = [
        {
            "mention_id": CLAIM_MENTION_ID,
            "segment_id": SEGMENT_ID,
            "candidate_id": CLAIM_CANDIDATE_ID,
            "surface_form": CLAIM_SPAN,
            "start_char": str(claim_start),
            "end_char": str(claim_start + len(CLAIM_SPAN)),
            "note": "Exact wording of the propagandistic Baroque-cultivation allegation that Haskell next calls 'the charge'; retained as an attributed claim.",
        },
        {
            "mention_id": EVENTS_MENTION_ID,
            "segment_id": SEGMENT_ID,
            "candidate_id": EVENTS_CANDIDATE_ID,
            "surface_form": EVENTS_SPAN,
            "start_char": str(events_start),
            "end_char": str(events_start + len(EVENTS_SPAN)),
            "note": "Source-defined but unspecified group of circumstances said to circumscribe religious-order patronage.",
        },
    ]
    if any(set(row) != set(mention_fields) for row in new_mentions):
        raise SystemExit("mention schema changed; refusing to append")
    mention_rows.extend(new_mentions)

    claim_row = statement_map["st-chp3-seci-l3-14-charge-attributed-to-grey"]
    claim_row["subject_candidate_id"] = CLAIM_CANDIDATE_ID
    claim_row["predicate"] = "introduced_by"
    q = claim_row["qualifiers"]
    q["relation_candidate"] = True
    q["relation_candidate_note"] = CLASSIFICATIONS[claim_row["statement_id"]][1]
    mentioned = q.setdefault("mentioned_candidate_ids", [])
    for candidate_id in [CLAIM_CANDIDATE_ID, "cand-0644"]:
        if candidate_id not in mentioned:
            mentioned.append(candidate_id)

    evaluation_row = statement_map["st-chp3-seci-l3-14-haskell-evaluates-grey"]
    evaluation_row["qualifiers"]["relation_candidate"] = False
    evaluation_row["qualifiers"]["relation_candidate_note"] = CLASSIFICATIONS[evaluation_row["statement_id"]][1]

    patronage_row = statement_map["st-chp3-seci-l3-14-order-patronage-circumscribed"]
    patronage_row["object_candidate_id"] = EVENTS_CANDIDATE_ID
    q = patronage_row["qualifiers"]
    q["relation_candidate"] = True
    q["relation_candidate_note"] = CLASSIFICATIONS[patronage_row["statement_id"]][1]
    mentioned = q.setdefault("mentioned_candidate_ids", [])
    for candidate_id in ["cand-2114", EVENTS_CANDIDATE_ID]:
        if candidate_id not in mentioned:
            mentioned.append(candidate_id)

    statements_rendered = ("\n".join(json.dumps(row, ensure_ascii=False) for row in statement_rows) + "\n").encode("utf-8")
    if raw_by_path[STATEMENTS].startswith(b"\xef\xbb\xbf"):
        statements_rendered = b"\xef\xbb\xbf" + statements_rendered
    rendered = {
        STATEMENTS: statements_rendered,
        CANDIDATES: render_csv(raw_by_path[CANDIDATES], candidate_fields, candidate_rows),
        MENTIONS: render_csv(raw_by_path[MENTIONS], mention_fields, mention_rows),
    }

    print("Chapter 3 section I L3–14 residual classification preview")
    for statement_id, (is_relation, note) in CLASSIFICATIONS.items():
        endpoint = " endpoints=" + str(statement_map[statement_id].get("subject_candidate_id")) + "," + str(statement_map[statement_id].get("object_candidate_id")) if is_relation else ""
        print(f"{statement_id}: {'true' if is_relation else 'false'}{endpoint} — {note}")
    for row in new_candidates:
        print(f"candidate: {row['candidate_id']} — {row['canonical_name']} (status=open)")
    for row in new_mentions:
        print(f"mention: {row['mention_id']} — {row['surface_form']} [{row['start_char']},{row['end_char']})")
    for path, output in rendered.items():
        print(f"{path.relative_to(ROOT)}: {sha256(raw_by_path[path])} -> {sha256(output)}")
    if not args.apply:
        print("mode=preview; no files changed")
        return
    if any(path.exists() for path in BACKUPS.values()):
        raise SystemExit("one or more protected backups already exist")
    for path, output in rendered.items():
        shutil.copy2(path, BACKUPS[path])
        tmp = path.with_name(path.name + ".tmp-s2-chp3-seci-l3-14")
        tmp.write_bytes(output)
        tmp.replace(path)
    print("mode=apply; backups=" + ", ".join(path.name for path in BACKUPS.values()))


if __name__ == "__main__":
    main()
