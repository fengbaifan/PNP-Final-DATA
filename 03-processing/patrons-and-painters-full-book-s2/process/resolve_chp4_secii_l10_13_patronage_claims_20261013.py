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
SEGMENTS = TABLES / "segments.jsonl"
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l10-13"
EXPECTED_HASHES = {
    STATEMENTS: "da049878dbeb540e8c4977bb922869065da3aaabdbd77176cd09220f1a794bba",
    CANDIDATES: "00c7ebc8ed902d545128e996f2bdcdd3dd9327cdd443c847d0401dbf39bcce82",
    MENTIONS: "0644450cf12abbb2bc56f06996101c4e443b2ece528fc7349788b99b1b7f04cf",
}
SEGMENT_SHA256 = "913ddaef5ecfe883e714386f3e702db25f9e70c9bc59e4acbee14c59972e6d31"
CONTEMPORARY_PAINTING_ID = "cand-11905"
ARTS_AND_SCIENCES_ID = "cand-11906"
NEW_STATEMENT_IDS = {
    "st-chp4-sec-ii-l10-13-patronage-archaeological-studies",
    "st-chp4-sec-ii-l10-13-patronage-contemporary-painting",
    "st-chp4-sec-ii-l10-13-income-promoted-arts-and-sciences",
}
FALSE_NOTES = {
    "st-chp4-sec-ii-l10-13-admired-scholars-fragment": "Nonrelation/continuation parent: the sentence closes on p.100, where the admiration and loyal collaboration claims are recorded as separate relation candidates.",
    "st-chp4-sec-ii-l10-13-cassiano-estimated-income-and-use": "Nonrelation/parent summary: the estimated annual amount is a scalar financial statement; Cassiano's use of that income to promote the arts and sciences is recorded separately below.",
    "st-chp4-sec-ii-l10-13-cassiano-favoured-after-offices": "Nonrelation/parent summary: 'among the very first to be favoured' is Haskell's broad account of access after the offices changed; the concrete household posts and revenue sources are recorded separately.",
    "st-chp4-sec-ii-l10-13-cassiano-not-rich_or_ambitious": "Nonrelation: this is Haskell's relative assessment of Cassiano's wealth and ambition by contemporary standards.",
    "st-chp4-sec-ii-l10-13-cassiano-took-opportunities-not-office": "Nonrelation: this characterizes Cassiano's choices and appetite for office; it does not identify a second entity endpoint.",
    "st-chp4-sec-ii-l10-13-patronage-archaeology-and-painting": "Nonrelation/parent assessment: the explicit patronage targets, archaeological studies and contemporary painting, are represented in separate relation candidates below; seriousness and consistency remain Haskell's evaluation.",
    "st-chp4-sec-ii-l10-13-religious-opinions-qualified": "Nonrelation: this is a qualified characterization of Cassiano's religious views, with the promised later discussion outside this segment.",
}
PREDICATES = {
    "st-chp4-sec-ii-l10-13-admired-scholars-fragment": "sentence_fragment",
    "st-chp4-sec-ii-l10-13-cassiano-estimated-income-and-use": "estimated_income_used_for_arts_and_sciences",
    "st-chp4-sec-ii-l10-13-cassiano-favoured-after-offices": "among_first_favoured_after_maffeo_and_francesco_raised",
    "st-chp4-sec-ii-l10-13-cassiano-not-rich_or_ambitious": "wealth_and_ambition_assessed_by_contemporary_standards",
    "st-chp4-sec-ii-l10-13-cassiano-took-opportunities-not-office": "took_opportunities_but_showed_little_desire_for_office",
    "st-chp4-sec-ii-l10-13-patronage-archaeology-and-painting": "patronage_assessed_as_serious_and_consistent",
    "st-chp4-sec-ii-l10-13-religious-opinions-qualified": "religious_opinions_seem_independent_and_not_wholly_orthodox",
}
NEW_CANDIDATES = [
    {
        "candidate_id": CONTEMPORARY_PAINTING_ID,
        "index_entry_id": "",
        "canonical_name": "Contemporary painting as a field of Cassiano dal Pozzo's patronage",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell names contemporary painting as one of the fields of Cassiano's uniquely serious and consistent patronage; no individual artist, work, institution, or commission is identified by this phrase.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L11",
    },
    {
        "candidate_id": ARTS_AND_SCIENCES_ID,
        "index_entry_id": "",
        "canonical_name": "The arts and sciences as fields promoted through Cassiano dal Pozzo's income",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell says Cassiano used his estimated annual income entirely to promote the arts and sciences; individual works, institutions, and scientific projects are not named here.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L13",
    },
]
NEW_MENTIONS = [
    {
        "mention_id": "m-chp4-sec-ii-l10-13-0026",
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-5751",
        "surface_form": "archaeological studies",
        "start_char": "239",
        "end_char": "261",
        "note": "Same broad archaeology field candidate used for the later Cassiano-Poussin passage; this passage makes the distinct claim about Cassiano's patronage of the field.",
    },
    {
        "mention_id": "m-chp4-sec-ii-l10-13-0027",
        "segment_id": SEGMENT_ID,
        "candidate_id": CONTEMPORARY_PAINTING_ID,
        "surface_form": "contemporary painting",
        "start_char": "266",
        "end_char": "287",
        "note": "Generic field of Cassiano's patronage; no particular painting or commission is identified here.",
    },
    {
        "mention_id": "m-chp4-sec-ii-l10-13-0028",
        "segment_id": SEGMENT_ID,
        "candidate_id": ARTS_AND_SCIENCES_ID,
        "surface_form": "the arts and sciences",
        "start_char": "1243",
        "end_char": "1264",
        "note": "Source's combined broad domains promoted through Cassiano's income; no individual object or project is named.",
    },
]
BACKUPS = {
    STATEMENTS: STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp4-secii-l10-13-patronage-20261013"),
    CANDIDATES: CANDIDATES.with_name("entity-candidates.csv.bak-s2-chp4-secii-l10-13-domains-20261013"),
    MENTIONS: MENTIONS.with_name("mentions.csv.bak-s2-chp4-secii-l10-13-domains-20261013"),
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
    parser = argparse.ArgumentParser(description="Resolve chapter 4 section II residual claims about Cassiano's patronage, income, and continued admiration sentence.")
    parser.add_argument("--apply", action="store_true", help="write after protected preview checks")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        if sha256(raw[path]) != expected:
            raise SystemExit(f"protected table changed: {path.name}")
    segments = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA256:
        raise SystemExit("protected S0 segment metadata changed")
    source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
    if sha256(source_text.encode("utf-8")) != SEGMENT_SHA256:
        raise SystemExit("protected S0 source segment changed")
    spans = {
        "archaeological studies": (239, 261),
        "contemporary painting": (266, 287),
        "the arts and sciences": (1243, 1264),
    }
    for text, (start, end) in spans.items():
        if source_text[start:end] != text:
            raise SystemExit(f"protected source mention changed: {text}")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row.get("statement_id"): row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row.get("statement_id") for row in rows
        if row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if unset != set(FALSE_NOTES) or NEW_STATEMENT_IDS.intersection(by_id):
        raise SystemExit(f"protected segment unset set changed: {sorted(unset)}")
    for statement_id, note in FALSE_NOTES.items():
        row = by_id[statement_id]
        if row.get("predicate") != PREDICATES[statement_id]:
            raise SystemExit(f"protected predicate changed: {statement_id}")
        row["qualifiers"]["relation_candidate"] = False
        row["qualifiers"]["relation_candidate_note"] = note

    by_id["st-chp4-sec-ii-l10-13-admired-scholars-fragment"]["qualifiers"]["related_statement_ids"] = [
        "st-chp4-sec-ii-l15-22-admired-scholars-closure",
        "st-chp4-sec-ii-l15-22-collaborated-with-scholars",
    ]
    by_id["st-chp4-sec-ii-l10-13-cassiano-favoured-after-offices"]["qualifiers"]["related_statement_ids"] = [
        "st-chp4-sec-ii-l10-13-cassiano-posts-in-barberini-household",
        "st-chp4-sec-ii-l10-13-cassiano-received-new-revenue",
    ]
    patronage_parent = by_id["st-chp4-sec-ii-l10-13-patronage-archaeology-and-painting"]
    patronage_ids = [
        "st-chp4-sec-ii-l10-13-patronage-archaeological-studies",
        "st-chp4-sec-ii-l10-13-patronage-contemporary-painting",
    ]
    patronage_parent["qualifiers"]["related_statement_ids"] = patronage_ids
    income_parent = by_id["st-chp4-sec-ii-l10-13-cassiano-estimated-income-and-use"]
    income_id = "st-chp4-sec-ii-l10-13-income-promoted-arts-and-sciences"
    income_parent["qualifiers"]["related_statement_ids"] = [income_id]

    new_statements = [
        {
            "statement_id": patronage_ids[0],
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": "cand-2036",
            "object_candidate_id": "cand-5751",
            "predicate": "patronage_of",
            "qualifiers": {
                "source_line_start": 11,
                "source_line_end": 11,
                "claim": "Haskell identifies archaeological studies as a field of Cassiano's patronage.",
                "speaker": "Haskell",
                "text_layer": "authorial narrative",
                "qualification": "This uses the same broad archaeology field candidate named later in connection with Cassiano and Poussin, while preserving this passage's distinct patronage claim.",
                "mentioned_candidate_ids": ["cand-2036", "cand-5751"],
                "pdf_physical_page": 6,
                "printed_page_locator": "p.99",
                "relation_candidate": True,
                "relation_candidate_note": "S2 candidate: the source explicitly names archaeological studies as a patronage domain; no specific project or formal S6 edge is asserted.",
            },
            "original_quote": "His patronage of archaeological studies",
            "origin": "book",
            "source_file": segment["source_file"],
        },
        {
            "statement_id": patronage_ids[1],
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": "cand-2036",
            "object_candidate_id": CONTEMPORARY_PAINTING_ID,
            "predicate": "patronage_of",
            "qualifiers": {
                "source_line_start": 11,
                "source_line_end": 11,
                "claim": "Haskell identifies contemporary painting as a field of Cassiano's patronage.",
                "speaker": "Haskell",
                "text_layer": "authorial narrative",
                "qualification": "No particular painting, artist, institution, or commission is specified in this phrase.",
                "mentioned_candidate_ids": ["cand-2036", CONTEMPORARY_PAINTING_ID],
                "pdf_physical_page": 6,
                "printed_page_locator": "p.99",
                "relation_candidate": True,
                "relation_candidate_note": "S2 candidate: the source explicitly names contemporary painting as a patronage domain; no formal S6 edge is asserted.",
            },
            "original_quote": "and contemporary painting",
            "origin": "book",
            "source_file": segment["source_file"],
        },
        {
            "statement_id": income_id,
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": "cand-2036",
            "object_candidate_id": ARTS_AND_SCIENCES_ID,
            "predicate": "used_income_to_promote",
            "qualifiers": {
                "source_line_start": 13,
                "source_line_end": 13,
                "claim": "Haskell says Cassiano used his income entirely to promote the arts and sciences.",
                "speaker": "Haskell",
                "text_layer": "authorial narrative",
                "qualification": "The amount is estimated at six thousand livres annually at the height of Cassiano's career; the linked work retains that amount and its source qualification.",
                "mentioned_candidate_ids": ["cand-2036", ARTS_AND_SCIENCES_ID],
                "amount": "six thousand livres annually",
                "pdf_physical_page": 6,
                "printed_page_locator": "p.99",
                "relation_candidate": True,
                "relation_candidate_note": "S2 candidate: the source explicitly says Cassiano used his income to promote these two domains; individual works, institutions, and projects remain unspecified, and no formal S6 edge is created.",
            },
            "original_quote": "he used these entirely to promote the arts and sciences",
            "origin": "book",
            "source_file": segment["source_file"],
        },
    ]
    rows.extend(new_statements)
    statements_rendered = ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")
    if raw[STATEMENTS].startswith(b"\xef\xbb\xbf"):
        statements_rendered = b"\xef\xbb\xbf" + statements_rendered

    candidate_fields, candidate_rows = load_csv(raw[CANDIDATES])
    mention_fields, mention_rows = load_csv(raw[MENTIONS])
    if any(row.get("candidate_id") in {CONTEMPORARY_PAINTING_ID, ARTS_AND_SCIENCES_ID} for row in candidate_rows):
        raise SystemExit("new candidate IDs already exist")
    if any(row.get("mention_id") in {mention["mention_id"] for mention in NEW_MENTIONS} for row in mention_rows):
        raise SystemExit("new mention IDs already exist")
    if max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows) != 11904:
        raise SystemExit("candidate ID sequence changed")
    candidate_rows.extend(NEW_CANDIDATES)
    mention_rows.extend(NEW_MENTIONS)
    candidates_rendered = render_csv(raw[CANDIDATES], candidate_fields, candidate_rows)
    mentions_rendered = render_csv(raw[MENTIONS], mention_fields, mention_rows)

    rendered = {STATEMENTS: statements_rendered, CANDIDATES: candidates_rendered, MENTIONS: mentions_rendered}
    print("Chapter 4 section II L10-13 preview:")
    print("7 residual parent/scalar statements -> false; admiration continuation is linked to the p.100 relation records")
    for candidate in NEW_CANDIDATES:
        print(f"candidate: {candidate['candidate_id']} {candidate['canonical_name']} (open)")
    for mention in NEW_MENTIONS:
        print(f"mention: {mention['mention_id']} {mention['surface_form']!r} [{mention['start_char']},{mention['end_char']})")
    for statement in new_statements:
        print(f"statement: {statement['statement_id']} {statement['subject_candidate_id']} -> {statement['object_candidate_id']}")
    for path, output in rendered.items():
        print(f"{path.relative_to(ROOT)}: {sha256(raw[path])} -> {sha256(output)}")
    if not args.apply:
        print("mode=preview; no files changed")
        return
    if any(path.exists() for path in BACKUPS.values()):
        raise SystemExit("one or more protected backups already exist")
    for path, output in rendered.items():
        shutil.copy2(path, BACKUPS[path])
        temporary = path.with_name(path.name + ".tmp-s2-chp4-secii-l10-13")
        temporary.write_bytes(output)
        temporary.replace(path)
    print("mode=apply; backups=" + ", ".join(path.name for path in BACKUPS.values()))


if __name__ == "__main__":
    main()
