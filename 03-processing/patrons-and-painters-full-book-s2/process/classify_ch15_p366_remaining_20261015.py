from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge/tables/book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
MENTIONS = ROOT / "04-knowledge/tables/mentions.csv"
SOURCE = ROOT / "02-sources/02-Markdown/15_CHP-15_sec_ii.md"
PDF = ROOT / "02-sources/01-book/CHP-15.pdf"
PAGE_IMAGE = ROOT / "scripts/.tmp_active_s2_chp15_p366_20261004.png"
SEGMENT_ID = "chp-15:15_CHP-15_sec_ii:l14-28"
P365_SEGMENT_ID = "chp-15:15_CHP-15_sec_ii:l6-12"

EXPECTED_HASHES = {
    "source": "eea847f75c7876dc5b8ea38ef4b64ad30cdd6c629df6a064125ac5f63917d31f",
    "pdf": "357e830cc4e880909edd62975bfcd06ade1c2b432d8866229831025fe86f2885",
    "page_image": "1809b0340f0cf935fecf9bd2d2e1388aff3fd6efef1e91cc39f3b110feb482e0",
    "statements": "1e485b6659a99e518c0cea6116e0efc25fa3e80db377c026a5acffb9003cf9f5",
    "candidates": "58e9461e5936d29fa7102ce2ac432ff192259c9a22970b19bc53ff8ce507f372",
    "mentions": "25e85d154952defd6cd6e3d94e7de1124488f4b8a1f3e12beff0ed0734ab0522",
}

# relation_candidate=True records a source-supported candidate relation, not an S6 formal edge.
DECISIONS: dict[str, tuple[bool, str, str | None]] = {
    "st-chp15-p366-eligible-presenters": (
        True,
        "Haskell identifies nobles as one class allowed to present statues in their own names. This is distinct from the adjacent rule about who could be represented as a statue subject.",
        None,
    ),
    "st-chp15-p366-memmo-not-only-rich": (
        True,
        "Haskell reports Memmo's aim that the opportunity to raise a statue should not be restricted to wealthy contributors.",
        None,
    ),
    "st-chp15-p366-price-and-appearance": (
        False,
        "This combines price estimates and cost-control specifications for the proposed statues; these are scalar/design properties, not entity relationships. The separate appearance claim remains separately recorded.",
        None,
    ),
    "st-chp15-p366-quality-committee-and-stone": (
        False,
        "This records a required quality standard for the proposed statues. The appointment of the committee and the uniform-stone rule are separately represented; the standard itself is a design requirement.",
        None,
    ),
    "st-chp15-p366-latin-inscriptions-pedestals": (
        False,
        "Latin and brevity are requirements for the inscriptions, not a relation between separately identified entities.",
        None,
    ),
    "st-chp15-p366-poets-new-athens": (
        True,
        "Haskell reports an anonymous group of poets reacting to progress on the scheme through the 'new Athens' comparison; the comparison remains rhetorical, not a literal identity.",
        None,
    ),
    "st-chp15-p366-1777-progress-and-ambassadorship": (
        False,
        "The nineteen statues in place are a dated progress count, not a separate entity relation. Memmo's departure and ambassadorship are recorded in their own statement.",
        None,
    ),
    "st-chp15-p366-difficulties-at-pra-while-memmo-away": (
        False,
        "This is a summary statement about the project's condition during Memmo's absence; the concrete debt, councillor objection, and work-delay claims are separately recorded.",
        None,
    ),
    "st-chp15-p366-statues-promised-and-in-situ-1786": (
        False,
        "This gives aggregate promise and installation counts by 1786. It is a quantitative progress claim and does not identify individual statues or subscribers.",
        None,
    ),
    "st-chp15-p366-memmo-expert-patron-reputation-partial": (
        False,
        "This is Haskell's evaluative statement about Memmo's reputation, not a graph relation.",
        None,
    ),
    "st-chp15-p366-note1-duke-visits": (
        True,
        "The note explicitly locates the Duke of Gloucester in Padua during two visits and reports illness on both occasions; preserve the two dates and Haskell's note attribution.",
        None,
    ),
    "st-chp15-p366-note1-egerton-ms-1969-no80": (
        True,
        "Haskell's note identifies a specific Egerton manuscript letter from Memmo in Padua to John Strange and reports its date and subject. The manuscript was not independently consulted.",
        None,
    ),
    "st-chp15-p366-general-appearance-mattered": (
        False,
        "This is a source-reported design preference about general appearance, not a relation to a separately identified work or artist.",
        None,
    ),
    "st-chp15-p366-committee-appointed-for-quality": (
        True,
        "Haskell says an unnamed committee was appointed to ensure that the scheme's quality standard was followed; the committee is a distinct source-defined body.",
        None,
    ),
    "st-chp15-p366-uniform-stone-required": (
        False,
        "Use of the same kind of stone is a material specification for the statue series, not a relation to a separately identified material source or work.",
        None,
    ),
    "st-chp15-p366-pedestal-space-limited-inscriptions": (
        False,
        "This is a design-feature explanation for keeping inscriptions brief; the pedestals and inscriptions are not individually identified entities.",
        None,
    ),
    "st-chp15-p366-memmo-declined-self-representation": (
        True,
        "The pronoun 'their' refers to the city of Padua, which offered the third statue immediately before this clause; Haskell says Memmo declined its proposal to represent him.",
        None,
    ),
    "st-chp15-p366-debts-piled-up": (
        False,
        "This reports the project's accumulated debt as a financial condition; no creditor, lender, or individual debt is identified.",
        None,
    ),
    "st-chp15-p366-work-slowed-while-memmo-away": (
        False,
        "This is a temporal progress condition of the project; no separate work event or agent is identified.",
        None,
    ),
    "st-chp15-p366-memmo-remained-enthusiastic-in-rome": (
        True,
        "The paragraph locates Memmo in Rome while he remained engaged with the Prà scheme; the contextual connection is source-bounded and does not measure his enthusiasm independently.",
        None,
    ),
    "st-chp15-p366-memmo-spread-ideas": (
        True,
        "Haskell explicitly reports that Memmo spread his ideas for the Prà scheme while pressing friends to contribute statues.",
        None,
    ),
    "st-chp15-p366-note1-azzo-statue-erected-by-1777": (
        True,
        "The note reports that the Duke of Gloucester's Azzo statue had been erected by October 1777 and locates it at the Prà della Valle.",
        None,
    ),
}

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-12230",
        "canonical_name": "Nobility in the eligibility rules for Memmo's Prà statue scheme (p.365-366)",
        "suggested_type": "term",
        "status": "open",
        "detail": "Haskell says nobles could be represented and could present statues in their own names. The passage does not identify members or specify a regional boundary; do not equate this class with the separately mentioned Venetian nobility without alignment evidence.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L15",
    },
    {
        "candidate_id": "cand-12231",
        "canonical_name": "A few old and distinguished professions eligible to present statues (p.366)",
        "suggested_type": "term",
        "status": "open",
        "detail": "Haskell gives university teachers as an example of eligible professions; no complete list or individual presenter is named.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L15",
    },
    {
        "candidate_id": "cand-12232",
        "canonical_name": "Wealthy prospective contributors considered for statue raising (p.366)",
        "suggested_type": "term",
        "status": "open",
        "detail": "Source-defined social class in Memmo's reported concern that access to statue raising not be restricted to the rich; no individual contributor is named.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L15",
    },
    {
        "candidate_id": "cand-12233",
        "canonical_name": "Unnamed poets reacting to progress on the Prà scheme (p.366)",
        "suggested_type": "term",
        "status": "open",
        "detail": "Haskell refers collectively to poets who asked whether they had found themselves in a new Athens as the scheme progressed; no poet is named.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L20",
    },
    {
        "candidate_id": "cand-12234",
        "canonical_name": "Unnamed quality-control committee for Memmo's Prà scheme (p.366)",
        "suggested_type": "institution",
        "status": "open",
        "detail": "Haskell says a committee was appointed to ensure the required statue-quality standard was followed; its name, members, and institutional affiliation are not supplied.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L16",
    },
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_hash(key: str, path: Path) -> None:
    actual = sha(path)
    expected = EXPECTED_HASHES[key]
    if actual != expected:
        raise SystemExit(f"{key} SHA mismatch: expected {expected}, got {actual}")


def read_jsonl(path: Path) -> tuple[list[dict], bool]:
    raw = path.read_bytes()
    final_newline = raw.endswith(b"\n")
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    return rows, final_newline


def encode_jsonl(rows: list[dict], final_newline: bool) -> bytes:
    text = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows)
    if final_newline:
        text += "\n"
    return text.encode("utf-8")


def read_csv(path: Path) -> tuple[list[str], list[dict], bool]:
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig" if has_bom else "utf-8")
    with io.StringIO(text, newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader), has_bom


def encode_csv(fields: list[str], rows: list[dict], has_bom: bool) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="raise", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return ("\ufeff" if has_bom else "").__add__(stream.getvalue()).encode("utf-8")


def require(row: dict | None, description: str) -> dict:
    if row is None:
        raise SystemExit(f"Missing {description}")
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the reviewed changes after all checks")
    args = parser.parse_args()

    for key, path in (("source", SOURCE), ("pdf", PDF), ("page_image", PAGE_IMAGE),
                      ("statements", STATEMENTS), ("candidates", CANDIDATES), ("mentions", MENTIONS)):
        verify_hash(key, path)

    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    if lines[13] != "[Page 66]":
        raise SystemExit("Expected p.366 source page marker changed")
    segment_text = "[Page 66]\n" + "\n".join(lines[14:28])
    for term in ("old and distinguished professions", "the poets", "a committee", "the rich"):
        if term not in segment_text:
            raise SystemExit(f"Expected p.366 source text missing: {term!r}")
    for start, end, phrase in ((158, 191, "old and distinguished professions"),
                               (1471, 1480, "the poets"),
                               (612, 623, "a committee"),
                               (339, 347, "the rich"),
                               (119, 125, "nobles")):
        if segment_text[start:end] != phrase:
            raise SystemExit(f"Source mention span changed: {phrase!r} at [{start},{end})")

    statement_rows, statement_final_newline = read_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statement_rows}
    if len(by_id) != len(statement_rows):
        raise SystemExit("Duplicate statement_id in table")
    segment_rows = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
    if len(segment_rows) != 54:
        raise SystemExit(f"Expected 54 statements in p.366 segment; got {len(segment_rows)}")
    unset_ids = {row["statement_id"] for row in segment_rows if row.get("qualifiers", {}).get("relation_candidate") is None}
    if unset_ids != set(DECISIONS):
        raise SystemExit(f"Unset statement set changed: missing={sorted(set(DECISIONS)-unset_ids)}, extra={sorted(unset_ids-set(DECISIONS))}")
    classified = [row for row in segment_rows if row.get("qualifiers", {}).get("relation_candidate") is not None]
    if len(classified) != 32 or any(row["qualifiers"].get("relation_candidate") is not True for row in classified):
        raise SystemExit("Expected the 32 existing p.366 classifications to be true")

    candidate_fields, candidate_rows, candidate_bom = read_csv(CANDIDATES)
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    if len(candidate_by_id) != len(candidate_rows):
        raise SystemExit("Duplicate candidate_id in table")
    suffixes = [int(cid.split("-")[1]) for cid in candidate_by_id if cid.startswith("cand-") and cid.split("-")[1].isdigit()]
    if max(suffixes) != 12229 or any(row["candidate_id"] in candidate_by_id for row in NEW_CANDIDATES):
        raise SystemExit("Candidate sequence or target candidate IDs changed")

    mention_fields, mention_rows, mention_bom = read_csv(MENTIONS)
    mention_by_id = {row["mention_id"]: row for row in mention_rows}
    if len(mention_by_id) != len(mention_rows):
        raise SystemExit("Duplicate mention_id in table")
    checks = {
        "m-chp15-p366-memmo-0004": ("nobles", "cand-8108", "119", "125"),
        "m-chp15-p366-memmo-0006": ("the rich", "cand-1650", "339", "347"),
        "m-chp15-p366-memmo-0012": ("a committee", "cand-1650", "612", "623"),
        "m-chp15-p365-memmo-0045": ("Only nobles", "cand-8108", "3199", "3210"),
    }
    for mention_id, expected in checks.items():
        m = require(mention_by_id.get(mention_id), mention_id)
        actual = (m["surface_form"], m["candidate_id"], m["start_char"] or None, m["end_char"] or None)
        if actual != expected:
            raise SystemExit(f"Mention precondition changed for {mention_id}: {actual}")
    new_mentions = {
        "m-chp15-p366-memmo-0088": ("cand-12231", "old and distinguished professions", "158", "191", "Source-defined profession class; university teachers are given as one example."),
        "m-chp15-p366-memmo-0089": ("cand-12233", "the poets", "1471", "1480", "Unnamed collective whose rhetorical response to the scheme is reported by Haskell."),
    }
    if any(mention_id in mention_by_id for mention_id in new_mentions):
        raise SystemExit("A new p.366 mention ID already exists")

    # Add source-bounded group and committee candidates; do not equate generic nobles with Venetian nobility.
    for row in NEW_CANDIDATES:
        candidate_rows.append({field: row.get(field, "") for field in candidate_fields})

    mention_by_id["m-chp15-p366-memmo-0004"]["candidate_id"] = "cand-12230"
    mention_by_id["m-chp15-p366-memmo-0004"]["note"] = "Generic noble class in the statue eligibility rules; the passage does not specify a Venetian or Paduan boundary."
    mention_by_id["m-chp15-p366-memmo-0006"]["candidate_id"] = "cand-12232"
    mention_by_id["m-chp15-p366-memmo-0006"]["note"] = "Source-defined wealthy contributor class that Memmo reportedly did not want to be the only group with access."
    mention_by_id["m-chp15-p366-memmo-0012"]["candidate_id"] = "cand-12234"
    mention_by_id["m-chp15-p366-memmo-0012"]["note"] = "Unnamed committee appointed to enforce the scheme's statue-quality standard."
    for mention_id, (candidate_id, surface, start, end, note) in new_mentions.items():
        mention_rows.append({
            "mention_id": mention_id,
            "segment_id": SEGMENT_ID,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": start,
            "end_char": end,
            "note": note,
        })

    for statement_id, (is_relation, note, open_reason) in DECISIONS.items():
        row = by_id[statement_id]
        q = row["qualifiers"]
        q["relation_candidate"] = is_relation
        q["relation_candidate_note"] = note
        if is_relation and open_reason:
            q["open_endpoint_reason"] = open_reason
        else:
            q.pop("open_endpoint_reason", None)

    # Resolve the p.365 eligibility reference with the general-noble-class candidate now available.
    p365_eligibility = by_id["st-chp15-p365-memmo-representation-eligibility-partial"]
    if p365_eligibility.get("object_candidate_id") != "cand-8108":
        raise SystemExit("p.365 eligibility endpoint changed")
    p365_eligibility["object_candidate_id"] = "cand-12230"
    p365_eligibility["qualifiers"]["mentioned_candidate_ids"] = ["cand-1650", "cand-12230", "cand-3944"]
    p365_mention = mention_by_id["m-chp15-p365-memmo-0045"]
    p365_mention["candidate_id"] = "cand-12230"
    p365_mention["note"] = "Generic noble class in the p.365-366 statue eligibility rules; not identified as exclusively Venetian."

    # Split the three distinct presenter classes into one-endpoint statements.
    eligible = by_id["st-chp15-p366-eligible-presenters"]
    eligible["object_candidate_id"] = "cand-12230"
    eligible["predicate"] = "nobles_could_present_statues_in_own_names"
    eligible["original_quote"] = "nobles"
    eligible["qualifiers"]["claim"] = "Haskell says nobles could present statues in their own names."
    eligible["qualifiers"]["qualification"] = "The source does not specify a regional boundary for these nobles."
    eligible["qualifiers"]["mentioned_candidate_ids"] = ["cand-1650", "cand-12230"]
    eligible["qualifiers"]["relation_candidate"] = True
    eligible["qualifiers"]["relation_candidate_note"] = DECISIONS[eligible["statement_id"]][1]

    extra_statements = [
        {
            "statement_id": "st-chp15-p366-eligible-churchmen",
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": "cand-1650",
            "object_candidate_id": "cand-10489",
            "predicate": "important_churchmen_could_present_statues_in_own_names",
            "qualifiers": {
                "source_line_start": 15, "source_line_end": 15, "printed_page": 366, "pdf_physical_page": 6,
                "claim": "Haskell says important churchmen could present statues in their own names.",
                "speaker": "Haskell", "text_layer": "authorial report",
                "qualification": "No individual churchman or institution is named.",
                "mentioned_candidate_ids": ["cand-1650", "cand-10489"],
                "relation_candidate": True,
                "relation_candidate_note": "Haskell identifies important churchmen as a distinct eligible presenter class; no individual or institution is named.",
            },
            "original_quote": "important churchmen",
            "origin": "book", "source_file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
        },
        {
            "statement_id": "st-chp15-p366-eligible-old-professions",
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": "cand-1650",
            "object_candidate_id": "cand-12231",
            "predicate": "old_distinguished_professions_including_university_teachers_could_present_statues",
            "qualifiers": {
                "source_line_start": 15, "source_line_end": 15, "printed_page": 366, "pdf_physical_page": 6,
                "claim": "Haskell says a few old and distinguished professions, including university teachers, could present statues in their own names.",
                "speaker": "Haskell", "text_layer": "authorial report",
                "qualification": "University teachers are an example, not a complete list of the eligible professions.",
                "mentioned_candidate_ids": ["cand-1650", "cand-12231", "cand-10490"],
                "relation_candidate": True,
                "relation_candidate_note": "Haskell identifies a source-bounded profession class and gives university teachers as an example; the list remains incomplete.",
            },
            "original_quote": "a few old and distinguished professions such as university teachers",
            "origin": "book", "source_file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
        },
    ]
    for row in extra_statements:
        if row["statement_id"] in by_id:
            raise SystemExit(f"New statement ID already exists: {row['statement_id']}")

    rich = by_id["st-chp15-p366-memmo-not-only-rich"]
    rich["object_candidate_id"] = "cand-12232"
    rich["qualifiers"]["mentioned_candidate_ids"] = ["cand-1642", "cand-1650", "cand-12232"]

    poets = by_id["st-chp15-p366-poets-new-athens"]
    poets["subject_candidate_id"] = "cand-12233"
    poets["qualifiers"]["mentioned_candidate_ids"] = ["cand-12233", "cand-1650", "cand-10502"]

    committee = by_id["st-chp15-p366-committee-appointed-for-quality"]
    committee["subject_candidate_id"] = "cand-12234"
    committee["object_candidate_id"] = "cand-1650"
    committee["qualifiers"]["mentioned_candidate_ids"] = ["cand-12234", "cand-1650"]

    memmo_declined = by_id["st-chp15-p366-memmo-declined-self-representation"]
    memmo_declined["object_candidate_id"] = "cand-8406"
    memmo_declined["qualifiers"]["mentioned_candidate_ids"] = ["cand-1642", "cand-8406"]

    memmo_enthusiastic = by_id["st-chp15-p366-memmo-remained-enthusiastic-in-rome"]
    memmo_enthusiastic["object_candidate_id"] = "cand-1650"
    memmo_enthusiastic["qualifiers"]["mentioned_candidate_ids"] = ["cand-1642", "cand-4490", "cand-1650"]

    duke_visits = by_id["st-chp15-p366-note1-duke-visits"]
    duke_visits["subject_candidate_id"] = "cand-1204"
    duke_visits["object_candidate_id"] = "cand-3944"
    duke_visits["qualifiers"]["mentioned_candidate_ids"] = ["cand-1204", "cand-3944"]

    azzo_date = by_id["st-chp15-p366-note1-azzo-statue-erected-by-1777"]
    azzo_date["object_candidate_id"] = "cand-3960"
    azzo_date["qualifiers"]["mentioned_candidate_ids"] = ["cand-10486", "cand-1204", "cand-3960"]

    insert_at = statement_rows.index(eligible) + 1
    statement_rows[insert_at:insert_at] = extra_statements
    if not args.apply:
        t = sum(value[0] for value in DECISIONS.values())
        f = len(DECISIONS) - t
        print(f"DRY-RUN OK: classify {t} true + {f} false; split presenter eligibility into 3 endpoint statements (+2); add {len(NEW_CANDIDATES)} candidates and {len(new_mentions)} mentions.")
        print(f"source={EXPECTED_HASHES['source']} pdf={EXPECTED_HASHES['pdf']} page_image={EXPECTED_HASHES['page_image']}")
        print(f"pre-write tables: statements={EXPECTED_HASHES['statements']} candidates={EXPECTED_HASHES['candidates']} mentions={EXPECTED_HASHES['mentions']}")
        return

    suffix = ".bak-s2-ch15-p366-classification-20261015"
    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        backup = path.with_name(path.name + suffix)
        if backup.exists():
            raise SystemExit(f"Backup already exists: {backup}")
        shutil.copy2(path, backup)

    STATEMENTS.write_bytes(encode_jsonl(statement_rows, statement_final_newline))
    CANDIDATES.write_bytes(encode_csv(candidate_fields, candidate_rows, candidate_bom))
    MENTIONS.write_bytes(encode_csv(mention_fields, mention_rows, mention_bom))
    print("APPLIED")
    print(f"statements={sha(STATEMENTS)} candidates={sha(CANDIDATES)} mentions={sha(MENTIONS)}")
    print(f"counts: statements={len(statement_rows)} candidates={len(candidate_rows)} mentions={len(mention_rows)}")
    print("backups=" + ", ".join(str(path.with_name(path.name + suffix)) for path in (STATEMENTS, CANDIDATES, MENTIONS)))


if __name__ == "__main__":
    main()
