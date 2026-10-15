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
SEGMENT_ID = "chp-3:03_CHP-3_sec_i:l16-24"
SOURCE_SHA256 = "a18f48c7b8bf5b161fa13a7ce26ed2935e72d9a14d555f82dfc1d85f84314255"
SEGMENT_SHA256 = "5f883b3074bd9851a0bd8f3140da874b28a896640666cfeebcdc735c0487a8dd"
EXPECTED_HASHES = {
    STATEMENTS: "4e9d989f732973228085231d6063f69e890d178f5c7c9ad9d35768374e6f9749",
    CANDIDATES: "1de94b3bfca749dee7026c6c7a724d23766ca3edafbed287476292eea98adde9",
    MENTIONS: "b0743ff4efef8d312c8b7c04dc228f293a51f75db51de0a13d6cebc49d76230e",
}
CANDIDATE_IDS = ["cand-11898", "cand-11899", "cand-11900"]
NEW_MENTION_IDS = ["m-chp3-seci-l16-24-0069", "m-chp3-seci-l16-24-0070"]
CLASSIFICATIONS = {
    "st-chp3-seci-l16-24-century-change": (
        False,
        "Haskell's broad transition that the earlier situation changed as the century advanced does not specify a relation between distinct entities.",
    ),
    "st-chp3-seci-l16-24-families-determined-patronage": (
        True,
        "Haskell says the whole mechanism of patronage was determined by the unnamed powerful families ruling Rome. The mechanism is retained as an open concept candidate; the statement's following clause continues in the next segment.",
    ),
    "st-chp3-seci-l16-24-haskell-imago-assessment": (
        False,
        "The description of Imago primi saeculi as magnificently produced and as stunning the world is Haskell's evaluative rhetoric; no bounded audience endpoint is identified.",
    ),
    "st-chp3-seci-l16-24-orders-artistic-influence-ambiguous": (
        False,
        "The deliberate alternative 'everywhere—or nowhere' is Haskell's broad assessment of artistic influence, not a definite relation to an identified endpoint.",
    ),
    "st-chp3-seci-l16-24-orders-financial-shortage": (
        True,
        "Haskell explicitly says the religious Orders' success was accompanied for a long time by an extreme shortage of money. The reported financial condition is represented as an open source-defined endpoint, without inferred amounts or institutional allocation.",
    ),
    "st-chp3-seci-l16-24-orders-followers-devotion": (
        True,
        "The sentence says the early religious groups encouraged devotion among their followers. The followers are an unnamed collective; the possessive refers to the groups described in the previous segment, not only to the Oratorians named later.",
    ),
}
BACKUPS = {
    STATEMENTS: STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp3-seci-l16-24-residuals-20261013"),
    CANDIDATES: CANDIDATES.with_name("entity-candidates.csv.bak-s2-chp3-seci-l16-24-open-endpoints-20261013"),
    MENTIONS: MENTIONS.with_name("mentions.csv.bak-s2-chp3-seci-l16-24-open-endpoints-20261013"),
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
    parser = argparse.ArgumentParser(description="Resolve remaining section I claims and retain three explicit open endpoints.")
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
    expected_spans = {
        "The whole mechanism of patronage": 2590,
        "an extreme shortage of money": 2451,
    }
    for phrase, expected_start in expected_spans.items():
        start = segment_text.find(phrase)
        if start != expected_start:
            raise SystemExit(f"protected mention span changed for {phrase!r}: {start}")

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
    existing_candidates = {row.get("candidate_id") for row in candidate_rows}
    if existing_candidates.intersection(CANDIDATE_IDS):
        raise SystemExit("one or more new candidate IDs already exist")
    new_mentions = {row.get("mention_id") for row in mention_rows}
    if new_mentions.intersection(NEW_MENTION_IDS):
        raise SystemExit("one or more new mention IDs already exist")

    new_candidates = [
        {
            "candidate_id": "cand-11898",
            "index_entry_id": "",
            "canonical_name": "Whole mechanism of patronage in Rome (determined by powerful families)",
            "index_page_range": "",
            "suggested_type": "term",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell says the whole mechanism of patronage was determined by the powerful families ruling Rome. This term records the source's structural referent; its exact institutional boundaries are unspecified.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": "chp-3:03_CHP-3_sec_i:l16-24#L22",
        },
        {
            "candidate_id": "cand-11899",
            "index_entry_id": "",
            "canonical_name": "Extreme shortage of money accompanying religious Orders' success (reported condition)",
            "index_page_range": "",
            "suggested_type": "term",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell reports a long-term extreme shortage of money accompanying the success of the religious Orders. The passage provides no amount, accounting unit, or allocation by Order.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": "chp-3:03_CHP-3_sec_i:l16-24#L22",
        },
        {
            "candidate_id": "cand-11900",
            "index_entry_id": "",
            "canonical_name": "Followers of the early religious Orders (unnamed collective)",
            "index_page_range": "",
            "suggested_type": "term",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "The source refers to followers of the early religious groups and says they were encouraged toward intense devotion. Individual followers and group membership are not identified.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": "chp-3:03_CHP-3_sec_i:l16-24#L17",
        },
    ]
    if any(set(row) != set(candidate_fields) for row in new_candidates):
        raise SystemExit("candidate schema changed; refusing to append")
    candidate_rows.extend(new_candidates)

    new_mentions_rows = [
        {
            "mention_id": NEW_MENTION_IDS[0],
            "segment_id": SEGMENT_ID,
            "candidate_id": "cand-11899",
            "surface_form": "an extreme shortage of money",
            "start_char": "2451",
            "end_char": "2479",
            "note": "The source's stated financial condition accompanying the religious Orders' success; duration is retained from the statement qualifier.",
        },
        {
            "mention_id": NEW_MENTION_IDS[1],
            "segment_id": SEGMENT_ID,
            "candidate_id": "cand-11898",
            "surface_form": "The whole mechanism of patronage",
            "start_char": "2590",
            "end_char": "2622",
            "note": "Structural referent which Haskell says was determined by the powerful families ruling Rome.",
        },
    ]
    if any(set(row) != set(mention_fields) for row in new_mentions_rows):
        raise SystemExit("mention schema changed; refusing to append")
    mention_rows.extend(new_mentions_rows)

    follower_mention = next((row for row in mention_rows if row.get("mention_id") == "m-chp3-seci-l16-24-0001"), None)
    if not follower_mention or follower_mention.get("surface_form") != "their followers" or follower_mention.get("candidate_id") != "cand-2114":
        raise SystemExit("expected existing 'their followers' mention mapping changed")
    follower_mention["candidate_id"] = "cand-11900"
    follower_mention["note"] = "The noun phrase denotes the followers as an unnamed collective; 'their' refers to the early religious groups described in the preceding segment."

    for statement_id, (is_relation, note) in CLASSIFICATIONS.items():
        row = statement_map[statement_id]
        q = row["qualifiers"]
        q["relation_candidate"] = is_relation
        q["relation_candidate_note"] = note
    statement_map["st-chp3-seci-l16-24-families-determined-patronage"]["object_candidate_id"] = "cand-11898"
    statement_map["st-chp3-seci-l16-24-orders-financial-shortage"]["object_candidate_id"] = "cand-11899"
    statement_map["st-chp3-seci-l16-24-orders-followers-devotion"]["object_candidate_id"] = "cand-11900"
    for statement_id, candidate_ids in {
        "st-chp3-seci-l16-24-families-determined-patronage": ["cand-4984", "cand-11898"],
        "st-chp3-seci-l16-24-orders-financial-shortage": ["cand-2114", "cand-11899"],
        "st-chp3-seci-l16-24-orders-followers-devotion": ["cand-2114", "cand-11900"],
    }.items():
        mentioned = statement_map[statement_id]["qualifiers"].setdefault("mentioned_candidate_ids", [])
        for candidate_id in candidate_ids:
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

    print("Chapter 3 section I L16–24 residual classification preview")
    for statement_id, (is_relation, note) in CLASSIFICATIONS.items():
        row = statement_map[statement_id]
        endpoint = f" endpoints={row.get('subject_candidate_id')},{row.get('object_candidate_id')}" if is_relation else ""
        print(f"{statement_id}: {'true' if is_relation else 'false'}{endpoint} — {note}")
    for row in new_candidates:
        print(f"candidate: {row['candidate_id']} — {row['canonical_name']} (status=open)")
    print("mention remap: m-chp3-seci-l16-24-0001 'their followers' -> cand-11900")
    for row in new_mentions_rows:
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
        tmp = path.with_name(path.name + ".tmp-s2-chp3-seci-l16-24")
        tmp.write_bytes(output)
        tmp.replace(path)
    print("mode=apply; backups=" + ", ".join(path.name for path in BACKUPS.values()))


if __name__ == "__main__":
    main()
