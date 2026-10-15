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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_intro.md"
SEGMENTS = TABLES / "segments.jsonl"
SEGMENT_ID = "chp-4:04_CHP-4_intro:l3-8"
EXPECTED_HASHES = {
    STATEMENTS: "ab287040204ce095cd3fd4f243f9c3dc5effad3d44912564990309dfb50be8c6",
    CANDIDATES: "322503451a2b1761cfb5d70d175b46dd28f4272ab395468e4b698e841a0d8340",
    MENTIONS: "a997ab1c3bd6309bd0613ac82831a2c86a35ed0fc6551b0529bd877df1018529",
}
SEGMENT_METADATA_SHA256 = "3bf389f549c498902ecc1b876c57a93141d7872f7aa372b873daf8718ea14ee8"
SEGMENT_TEXT_SHA256 = "3bf389f549c498902ecc1b876c57a93141d7872f7aa372b873daf8718ea14ee8"
SELECTED_CANDIDATE_ID = "cand-11903"
PAINTERS_CANDIDATE_ID = "cand-11904"
NEW_STATEMENT_IDS = {
    "st-chp4-intro-l3-8-selected-patrons-wealth-painters",
    "st-chp4-intro-l3-8-selected-patrons-taste-artists",
}
NEW_CANDIDATES = [
    {
        "candidate_id": SELECTED_CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "A few prominent private patrons in seventeenth-century Rome (unnamed source-defined group)",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell narrows the broad category of Roman private collectors to a few men whom he considers especially important in the city's artistic life; no individual members are named in this passage.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L7-8",
    },
    {
        "candidate_id": PAINTERS_CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "Painters who swarmed into Rome from across Europe (unnamed source-defined group)",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell's source-defined group of painters arriving in Rome from across Europe; the phrase 'these artists' refers back to this group, whose members are not identified here.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L8",
    },
]
NEW_MENTIONS = [
    {
        "mention_id": "m-chp4-intro-0028",
        "segment_id": SEGMENT_ID,
        "candidate_id": SELECTED_CANDIDATE_ID,
        "surface_form": "A few men",
        "start_char": "869",
        "end_char": "878",
        "note": "Haskell introduces a subset of the previously described private collectors; no individual members are named.",
    },
    {
        "mention_id": "m-chp4-intro-0029",
        "segment_id": SEGMENT_ID,
        "candidate_id": PAINTERS_CANDIDATE_ID,
        "surface_form": "the painters who swarmed into Rome from all over\nEurope",
        "start_char": "1024",
        "end_char": "1079",
        "note": "Unnamed source-defined group arriving from across Europe; membership is unspecified.",
    },
    {
        "mention_id": "m-chp4-intro-0030",
        "segment_id": SEGMENT_ID,
        "candidate_id": PAINTERS_CANDIDATE_ID,
        "surface_form": "these artists",
        "start_char": "1139",
        "end_char": "1152",
        "note": "Anaphoric reference to m-chp4-intro-0029.",
    },
]
BACKUPS = {
    STATEMENTS: STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp4-intro-l3-8-relations-20261013"),
    CANDIDATES: CANDIDATES.with_name("entity-candidates.csv.bak-s2-chp4-intro-l3-8-open-groups-20261013"),
    MENTIONS: MENTIONS.with_name("mentions.csv.bak-s2-chp4-intro-l3-8-open-groups-20261013"),
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
    rendered = output.getvalue().encode("utf-8")
    return b"\xef\xbb\xbf" + rendered if raw.startswith(b"\xef\xbb\xbf") else rendered


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve chapter 4 opening residual claims and preserve their source-defined groups.")
    parser.add_argument("--apply", action="store_true", help="write after protected preview checks")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        if sha256(raw[path]) != expected:
            raise SystemExit(f"protected table changed: {path.name}")
    segment_rows = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segment_rows if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_METADATA_SHA256:
        raise SystemExit("protected S0 segment metadata changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
    actual_segment_text_sha = sha256(segment_text.encode("utf-8"))
    if actual_segment_text_sha != SEGMENT_TEXT_SHA256:
        raise SystemExit(f"protected S0 segment text changed: {actual_segment_text_sha}")
    exact_spans = {
        "A few men": (869, 878),
        "the painters who swarmed into Rome from all over\nEurope": (1024, 1079),
        "these artists": (1139, 1152),
    }
    for text, (start, end) in exact_spans.items():
        if segment_text[start:end] != text:
            raise SystemExit(f"protected mention span changed: {text!r}")

    statement_rows = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    statement_map = {row.get("statement_id"): row for row in statement_rows}
    if len(statement_map) != len(statement_rows):
        raise SystemExit("duplicate statement IDs")
    expected_unset = {
        "st-chp4-intro-l3-8-collectors-accumulate-art",
        "st-chp4-intro-l3-8-ghibbesio-profile",
        "st-chp4-intro-l3-8-selected-patrons",
    }
    segment_unset = {
        row.get("statement_id") for row in statement_rows
        if row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if segment_unset != expected_unset or NEW_STATEMENT_IDS.intersection(statement_map):
        raise SystemExit(f"protected statement set changed: {sorted(segment_unset)}")

    collecting = statement_map["st-chp4-intro-l3-8-collectors-accumulate-art"]
    collecting["qualifiers"]["relation_candidate"] = True
    collecting["qualifiers"]["relation_candidate_note"] = (
        "S2 candidate: Haskell explicitly reports accumulation of works of art as activity of the source-defined private-collector group. "
        "The artworks remain a generic, unbounded object category here; no discrete work group or formal S6 edge is asserted."
    )
    collecting["qualifiers"]["open_endpoint_reason"] = (
        "The source says only 'works of art' generically and does not identify individual works or a bounded collection for the object endpoint."
    )

    ghibbesio = statement_map["st-chp4-intro-l3-8-ghibbesio-profile"]
    ghibbesio["qualifiers"]["relation_candidate"] = False
    ghibbesio["qualifiers"]["relation_candidate_note"] = (
        "Nonrelation: this statement combines biographical details and Haskell's characterization of Ghibbesio. "
        "His ownership of the source-defined paintings-and-drawings group and Pietro da Cortona's authorship are recorded separately."
    )

    parent = statement_map["st-chp4-intro-l3-8-selected-patrons"]
    parent["subject_candidate_id"] = SELECTED_CANDIDATE_ID
    parent["qualifiers"]["relation_candidate"] = False
    parent["qualifiers"]["relation_candidate_note"] = (
        "This statement is Haskell's evaluative summary that a few men were especially important in Rome's artistic life. "
        "Its two causal interactions are represented separately as source-grounded S2 relation candidates below."
    )
    parent["qualifiers"]["mentioned_candidate_ids"] = [
        SELECTED_CANDIDATE_ID, "cand-4490", PAINTERS_CANDIDATE_ID, "cand-3462"
    ]

    new_statements = [
        {
            "statement_id": "st-chp4-intro-l3-8-selected-patrons-wealth-painters",
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": SELECTED_CANDIDATE_ID,
            "object_candidate_id": PAINTERS_CANDIDATE_ID,
            "predicate": "wealth_made_indispensable_to_painters",
            "qualifiers": {
                "source_line_start": 7,
                "source_line_end": 8,
                "claim": "Haskell says the selected patrons' towering wealth made them indispensable to painters arriving in Rome from across Europe.",
                "speaker": "Haskell",
                "text_layer": "authorial assessment",
                "qualification": "This is Haskell's generalized causal characterization; the patrons and painters are unnamed groups, and no individual membership or specific commission is identified.",
                "mentioned_candidate_ids": [SELECTED_CANDIDATE_ID, PAINTERS_CANDIDATE_ID, "cand-3462"],
                "relation_candidate": True,
                "relation_candidate_note": "S2 candidate: the source explicitly links the selected patrons' wealth to their indispensability to the painter group; no formal S6 edge is created.",
            },
            "original_quote": "their towering wealth made them indispensable to the painters who swarmed into Rome from all over\nEurope",
            "origin": "book",
            "source_file": SOURCE.relative_to(ROOT).as_posix(),
        },
        {
            "statement_id": "st-chp4-intro-l3-8-selected-patrons-taste-artists",
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": SELECTED_CANDIDATE_ID,
            "object_candidate_id": PAINTERS_CANDIDATE_ID,
            "predicate": "patrons_taste_led_artists_into_unexpected_channels",
            "qualifiers": {
                "source_line_start": 8,
                "source_line_end": 8,
                "claim": "Haskell says the selected patrons' firmly held and sometimes eccentric taste led the painter group into unexpected channels.",
                "speaker": "Haskell",
                "text_layer": "authorial assessment",
                "qualification": "Preserve Haskell's evaluative wording and the limitation sometimes; 'these artists' refers to the painters arriving in Rome from across Europe.",
                "mentioned_candidate_ids": [SELECTED_CANDIDATE_ID, PAINTERS_CANDIDATE_ID],
                "anaphora": {"these artists": "painters who swarmed into Rome from all over Europe"},
                "relation_candidate": True,
                "relation_candidate_note": "S2 candidate: the source explicitly reports an influence from the selected patrons' taste to the painter group; no formal S6 edge is created.",
            },
            "original_quote": "a firmly held and sometimes eccentric taste led these artists into unexpected channels",
            "origin": "book",
            "source_file": SOURCE.relative_to(ROOT).as_posix(),
        },
    ]
    parent_index = statement_rows.index(parent)
    statement_rows[parent_index + 1:parent_index + 1] = new_statements
    statements_rendered = ("\n".join(json.dumps(row, ensure_ascii=False) for row in statement_rows) + "\n").encode("utf-8")
    if raw[STATEMENTS].startswith(b"\xef\xbb\xbf"):
        statements_rendered = b"\xef\xbb\xbf" + statements_rendered

    candidate_fields, candidate_rows = load_csv(raw[CANDIDATES])
    mention_fields, mention_rows = load_csv(raw[MENTIONS])
    if any(row.get("candidate_id") in {SELECTED_CANDIDATE_ID, PAINTERS_CANDIDATE_ID} for row in candidate_rows):
        raise SystemExit("candidate IDs already exist")
    if any(row.get("mention_id") in {mention["mention_id"] for mention in NEW_MENTIONS} for row in mention_rows):
        raise SystemExit("mention IDs already exist")
    max_candidate = max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows)
    if max_candidate != 11902:
        raise SystemExit(f"candidate sequence changed: maximum is {max_candidate}")
    candidate_rows.extend(NEW_CANDIDATES)
    mention_rows.extend(NEW_MENTIONS)
    candidates_rendered = render_csv(raw[CANDIDATES], candidate_fields, candidate_rows)
    mentions_rendered = render_csv(raw[MENTIONS], mention_fields, mention_rows)

    rendered = {
        STATEMENTS: statements_rendered,
        CANDIDATES: candidates_rendered,
        MENTIONS: mentions_rendered,
    }
    print("Chapter 4 opening segment L3-8 preview:")
    print("collectors-accumulate-art: true; generic artwork object endpoint remains open")
    print("ghibbesio-profile: false; ownership and authorship are represented in separate atomic statements")
    print("selected-patrons assessment: false; split into two true source-grounded relation candidates")
    for row in NEW_CANDIDATES:
        print(f"candidate: {row['candidate_id']} {row['canonical_name']} (open)")
    for row in NEW_MENTIONS:
        print(f"mention: {row['mention_id']} {row['surface_form']!r} [{row['start_char']},{row['end_char']})")
    for row in new_statements:
        print(f"statement: {row['statement_id']} {row['subject_candidate_id']} -> {row['object_candidate_id']}")
    for path, output in rendered.items():
        print(f"{path.relative_to(ROOT)}: {sha256(raw[path])} -> {sha256(output)}")
    if not args.apply:
        print("mode=preview; no files changed")
        return
    if any(path.exists() for path in BACKUPS.values()):
        raise SystemExit("one or more protected backups already exist")
    for path, output in rendered.items():
        shutil.copy2(path, BACKUPS[path])
        temporary = path.with_name(path.name + ".tmp-s2-chp4-intro-l3-8")
        temporary.write_bytes(output)
        temporary.replace(path)
    print("mode=apply; backups=" + ", ".join(path.name for path in BACKUPS.values()))


if __name__ == "__main__":
    main()
