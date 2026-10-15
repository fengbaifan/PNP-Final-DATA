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
PAGE_IMAGE = ROOT / "scripts/.tmp_active_s2_chp15_p365_20261004.png"
SEGMENT_ID = "chp-15:15_CHP-15_sec_ii:l6-12"

EXPECTED_HASHES = {
    "source": "eea847f75c7876dc5b8ea38ef4b64ad30cdd6c629df6a064125ac5f63917d31f",
    "pdf": "357e830cc4e880909edd62975bfcd06ade1c2b432d8866229831025fe86f2885",
    "page_image": "64273b49e1c16192c9a912880f7f0dde5ca38690e81a14684fcaf85c9a67a2c8",
    "statements": "88a61de7327f3323b98a6a90e2f6f64efb4f934f35407c19846aef143e383810",
    "candidates": "7b60fb5af28ecf4ccc08c5c597a1f07255628ab430541da29b76d587d42ef495",
    "mentions": "23b11d0fc4b2fe606d7bb32b9e31cceff11d689faec831d81ec61fafa34ed0ba",
}

# relation_candidate=True preserves a source-supported, potentially meaningful
# relationship for later S6 review; False keeps the claim without proposing a graph edge.
DECISIONS: dict[str, tuple[bool, str, str | None]] = {
    "st-chp15-p365-memmo-career-and-doge": (
        True,
        "Haskell reports that Memmo declined an opportunity to become Doge; the office is an explicit endpoint, and the source does not say he held it.",
        None,
    ),
    "st-chp15-p365-memmo-appointed-provveditore": (
        True,
        "This is a source-reported appointment to the Provveditore office at Padua in 1775; the passage does not define the office's legal remit.",
        None,
    ),
    "st-chp15-p365-memmo-patronage-main-concern": (
        False,
        "This is a biographical characterization of Memmo's principal concern, not a proposed relation to a distinct identified entity. Retain Haskell's wording as a claim.",
        None,
    ),
    "st-chp15-p365-memmo-ideas-new-attitude-to-art": (
        False,
        "This is Haskell's broad intellectual characterization of Memmo's ideas, not a distinct person-to-person, institution, or work relation. The attribution remains in the claim.",
        None,
    ),
    "st-chp15-p365-fair-inaugurated-two-or-three-years-earlier": (
        False,
        "The approximate interval is a chronology attribute of the fair; the source gives no exact founding year or named founder.",
        None,
    ),
    "st-chp15-p365-first-suggestions-realistic-little-permanent-value": (
        False,
        "This is Haskell's evaluation of the initial suggestions, not an entity relationship.",
        None,
    ),
    "st-chp15-p365-entertainment-proposed-for-venetian-nobility": (
        True,
        "Haskell reports Memmo's stated attendance rationale and explicitly identifies the Venetian nobility as the group to be entertained.",
        None,
    ),
    "st-chp15-p365-dealers-needed-suitable-stall-site": (
        True,
        "The fair's proposed arrangements require stall space for the source-defined dealer group. This records a planning requirement, not proof that stalls were installed or the fair held at a particular site.",
        "The passage does not explicitly identify the final stall area or name individual dealers.",
    ),
    "st-chp15-p365-pra-location-before-s-giustina": (
        True,
        "This is an explicit spatial relation between the Prà della Valle marshland and S. Giustina.",
        None,
    ),
    "st-chp15-p365-memmo-oval-plan-colosseum": (
        True,
        "Haskell explicitly says the oval plan was based on the Colosseum; this records design reference, not a claim that the plan copied every feature.",
        None,
    ),
    "st-chp15-p365-pra-great-town-planning-evaluation": (
        False,
        "This is Haskell's qualified comparative evaluation of the project's importance, not a graph relation. The probability and historical comparison remain in the claim.",
        None,
    ),
    "st-chp15-p365-commercial-not-religious-or-family-glory-motive": (
        True,
        "Haskell explicitly attributes a commercial motive to the plan and contrasts it with religious or family glory. Preserve this as the author's interpretation, not an independently verified motive.",
        "The commercial motive is not represented by a distinct concept candidate in this passage; do not infer a named funder or transaction.",
    ),
    "st-chp15-p365-memmo-resource-constraints-and-negotiation": (
        False,
        "The sentence characterizes Memmo's authority and resources; the related project actions are recorded in separate statements. It does not identify an entity relationship here.",
        None,
    ),
    "st-chp15-p365-lodoli-plan-functional-commercial": (
        True,
        "Haskell links the plan's functional and commercial conception to attracting international funds and support. This is a source-described aim, not evidence that funds were actually attracted.",
        "The source does not identify the potential funders or institutions individually.",
    ),
    "st-chp15-p365-statue-foundations-strengthen-canal-banks": (
        True,
        "The statement connects the planned statue foundations with strengthening the canal banks as part of the design.",
        "The passage does not identify a standalone canal entity or individual statues, and it describes a plan rather than verified construction.",
    ),
    "st-chp15-p365-statues-as-civic-virtue-gallery": (
        True,
        "Haskell describes the planned statues as a public gallery intended to teach civic virtue and ties that function to Enlightenment opinion; this is a source-reported design purpose.",
        "The intended audience and individual statues are not identified.",
    ),
    "st-chp15-p365-pra-plan-inspired-by-bologna-vicenza": (
        True,
        "Haskell explicitly identifies Bologna as one example that inspired the plan; the claim is now separated from the parallel Vicenza example so each place has its own endpoint.",
        None,
    ),
    "st-chp15-p365-eighty-eight-statues-and-conditions": (
        False,
        "The stated number is a scalar planning estimate, not an entity relationship; it does not establish how many statues were completed.",
        None,
    ),
    "st-chp15-p365-memmo-representation-eligibility-partial": (
        True,
        "This records the plan's stated eligibility rule for nobles and men credited with particular glory to the city; the groups are not enumerated.",
        "The passage does not specify that every eligible noble was Venetian, and the second eligible class has no separate candidate endpoint.",
    ),
    "st-chp15-p365-memmo-career-impressive": (
        False,
        "This is Haskell's evaluative description of Memmo's political career, not an entity relationship.",
        None,
    ),
    "st-chp15-p365-memmo-patronage-historical-contribution": (
        False,
        "This is Haskell's retrospective evaluation of the historical significance of Memmo's patronage, not a graph relation.",
        None,
    ),
    "st-chp15-p365-memmo-arrival-padua-1775": (
        True,
        "This records Haskell's explicit person-to-place arrival claim with its stated year.",
        None,
    ),
    "st-chp15-p365-fair-entertainment-arrangements": (
        True,
        "The fair's proposed program explicitly includes theatres, operas, and masked balls; the source presents arrangements, not confirmed performances.",
        "No individual performance or theatre is identified as a separate endpoint.",
    ),
    "st-chp15-p365-memmo-central-island-for-traders": (
        True,
        "The plan assigns the central island a proposed use by traders; the statement now links the plan to the source-defined trader group.",
        None,
    ),
    "st-chp15-p365-pra-opposition-negotiation": (
        True,
        "Haskell reports that opposition to the project was to be overcome through negotiation and persuasion.",
        "The opposing parties and the outcome are not identified.",
    ),
    "st-chp15-p365-pra-fundraising-required": (
        True,
        "Haskell explicitly states that money had to be raised for the project; this does not identify subscribers, a sum, or a successful outcome.",
        "No funder or amount is named.",
    ),
    "st-chp15-p365-scheme-rationale-for-inclusion": (
        False,
        "This explains Haskell's editorial reason for discussing the site in an arts book; it is a text-level rationale, not a historical entity relation.",
        None,
    ),
    "st-chp15-p365-statue-donor-choice": (
        True,
        "Haskell states that the plan allowed a donor to choose a statue's subject and artist within limits; the statement now links the plan to an unnamed donor-role candidate.",
        None,
    ),
    "st-chp15-p365-bologna-vicenza-porticoes": (
        True,
        "Haskell reports civic cooperation in building the porticoes and shrines used as examples for the plan; this remains a source-bounded group claim.",
        "The citizens, individual structures, and pilgrimage churches are not named; the two city mentions do not establish a single joint civic body.",
    ),
    "st-chp15-p365-proposal-more-ambitious": (
        False,
        "This is Haskell's comparative evaluation of the proposal, not a graph relation.",
        None,
    ),
    "st-chp15-p365-conditions-limit-venetian-enlightenment": (
        False,
        "This is Haskell's interpretation of what the conditions imply about the Venetian Enlightenment. Preserve it as an attributed claim rather than an independently established relation.",
        None,
    ),
}


NEW_CANDIDATES = [
    {
        "candidate_id": "cand-12227",
        "canonical_name": "Unnamed dealers seeking stalls at the annual agricultural fair in Padua (p.365)",
        "suggested_type": "term",
        "status": "open",
        "detail": "Source-defined collective of dealers for whom stall space was to be arranged at the annual agricultural fair; no individuals or firms are named.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L8",
    },
    {
        "candidate_id": "cand-12228",
        "canonical_name": "Unnamed traders intended to use the central island in Memmo's Prà plan (p.365)",
        "suggested_type": "term",
        "status": "open",
        "detail": "Source-defined group for the proposed use of the central island; membership and whether the plan was implemented are not stated.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L8",
    },
    {
        "candidate_id": "cand-12229",
        "canonical_name": "Unidentified donor role in Memmo's proposed statue series (p.365)",
        "suggested_type": "term",
        "status": "open",
        "detail": "The source says a donor could choose a statue's subject and artist within limits; no donor or particular statue is identified.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L9",
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
    had_final_newline = raw.endswith(b"\n")
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    return rows, had_final_newline


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

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "[Page 365]\n" + "\n".join(source_lines[6:12])
    expected_quotes = (
        "the dealers", "the traders", "the donor",
        "Memmo’s plan was inspired by the examples of Bologna", "and Vicenza",
    )
    for quote in expected_quotes:
        if quote not in segment_text:
            raise SystemExit(f"Expected source text missing: {quote!r}")
    if segment_text[1045:1056] != "the dealers" or segment_text[1370:1381] != "the traders" or segment_text[2346:2355] != "the donor":
        raise SystemExit("Source mention spans changed")

    statement_rows, statement_final_newline = read_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statement_rows}
    if len(by_id) != len(statement_rows):
        raise SystemExit("Duplicate statement_id in table")
    segment_rows = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
    if len(segment_rows) != 36:
        raise SystemExit(f"Expected 36 existing statements in segment; got {len(segment_rows)}")
    unset_ids = {row["statement_id"] for row in segment_rows if "relation_candidate" not in row.get("qualifiers", {})}
    if unset_ids != set(DECISIONS):
        raise SystemExit(f"Unset statement ID set changed: missing={sorted(set(DECISIONS)-unset_ids)}, extra={sorted(unset_ids-set(DECISIONS))}")
    already_true = {row["statement_id"] for row in segment_rows if row.get("qualifiers", {}).get("relation_candidate") is True}
    expected_true = {
        "st-chp15-p365-padua-authorities-request-fair-assistance",
        "st-chp15-p365-memmo-reclamation-canal-island",
        "st-chp15-p365-memmo-summoned-cerato-to-implement-plan",
        "st-chp15-p365-subscriptions-for-statue-series",
        "st-chp15-p365-memmo-pupil-of-lodoli",
    }
    if already_true != expected_true:
        raise SystemExit(f"Preclassified true set changed: {sorted(already_true)}")

    candidate_fields, candidate_rows, candidate_bom = read_csv(CANDIDATES)
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    if len(candidate_by_id) != len(candidate_rows):
        raise SystemExit("Duplicate candidate_id in table")
    suffixes = [int(cid.split("-")[1]) for cid in candidate_by_id if cid.startswith("cand-") and cid.split("-")[1].isdigit()]
    if max(suffixes) != 12226 or any(row["candidate_id"] in candidate_by_id for row in NEW_CANDIDATES):
        raise SystemExit("Candidate ID sequence or target candidate IDs changed")

    mention_fields, mention_rows, mention_bom = read_csv(MENTIONS)
    mention_by_id = {row["mention_id"]: row for row in mention_rows}
    if len(mention_by_id) != len(mention_rows):
        raise SystemExit("Duplicate mention_id in table")
    dealers_mention = require(mention_by_id.get("m-chp15-p365-memmo-0015"), "dealers mention")
    traders_mention = require(mention_by_id.get("m-chp15-p365-memmo-0023"), "traders mention")
    if (dealers_mention["surface_form"], dealers_mention["candidate_id"], dealers_mention["start_char"], dealers_mention["end_char"]) != (
        "a suitable site must be found for the dealers", "cand-1650", "1011", "1056"
    ):
        raise SystemExit("Dealers mention precondition changed")
    if (traders_mention["surface_form"], traders_mention["candidate_id"], traders_mention["start_char"], traders_mention["end_char"]) != (
        "the traders", "cand-1650", "1370", "1381"
    ):
        raise SystemExit("Traders mention precondition changed")
    new_mention_id = "m-chp15-p365-memmo-0057"
    if new_mention_id in mention_by_id:
        raise SystemExit("New donor mention ID already exists")

    # Resolve each body mention to its source-defined role candidate, not to the plan as a whole.
    dealers_mention.update({
        "candidate_id": "cand-12227", "surface_form": "the dealers", "start_char": "1045", "end_char": "1056",
        "note": "Unnamed dealers who were to set up stalls at the annual fair; no individual or firm is identified.",
    })
    traders_mention.update({
        "candidate_id": "cand-12228",
        "note": "Unnamed trader group described as the intended users of the proposed central island.",
    })
    donor_mention = {
        "mention_id": new_mention_id,
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-12229",
        "surface_form": "the donor",
        "start_char": "2346",
        "end_char": "2355",
        "note": "Unidentified donor role in the proposed statue series; no donor or particular statue is named.",
    }
    mention_rows.append(donor_mention)

    for row in NEW_CANDIDATES:
        candidate_rows.append({field: row.get(field, "") for field in candidate_fields})

    for statement_id, (is_relation, note, open_reason) in DECISIONS.items():
        row = by_id[statement_id]
        q = row["qualifiers"]
        q["relation_candidate"] = is_relation
        q["relation_candidate_note"] = note
        if is_relation and open_reason:
            q["open_endpoint_reason"] = open_reason
        else:
            q.pop("open_endpoint_reason", None)

    inspiration = by_id["st-chp15-p365-pra-plan-inspired-by-bologna-vicenza"]
    inspiration["object_candidate_id"] = "cand-3398"
    inspiration["predicate"] = "plan_inspired_by_example_from_bologna"
    inspiration["original_quote"] = "Memmo’s plan was inspired by the examples of Bologna"
    inspiration["qualifiers"]["claim"] = "Haskell says Memmo’s plan was inspired by the example of Bologna."
    inspiration["qualifiers"]["qualification"] = "Bologna is one of two cited examples; no particular building or exact design element is identified."
    inspiration["qualifiers"]["mentioned_candidate_ids"] = ["cand-1650", "cand-3398"]
    inspiration["qualifiers"]["relation_candidate"] = True
    inspiration["qualifiers"]["relation_candidate_note"] = DECISIONS[inspiration["statement_id"]][1]

    vicenza_statement = {
        "statement_id": "st-chp15-p365-plan-inspired-by-vicenza",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-1650",
        "object_candidate_id": "cand-2769",
        "predicate": "plan_inspired_by_example_from_vicenza",
        "qualifiers": {
            "source_line_start": 10,
            "source_line_end": 10,
            "printed_page": 365,
            "pdf_physical_page": 5,
            "claim": "Haskell says Memmo’s plan was inspired by the example of Vicenza.",
            "speaker": "Haskell",
            "text_layer": "authorial report",
            "qualification": "Vicenza is the second cited example; no particular building or exact design element is identified.",
            "mentioned_candidate_ids": ["cand-1650", "cand-2769"],
            "relation_candidate": True,
            "relation_candidate_note": "Haskell explicitly identifies Vicenza as a second example that inspired the plan; this is split from the Bologna reference so each place has its own endpoint.",
        },
        "original_quote": "and Vicenza",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
    }
    if vicenza_statement["statement_id"] in by_id:
        raise SystemExit("New Vicenza statement ID already exists")
    insert_at = statement_rows.index(inspiration) + 1
    statement_rows.insert(insert_at, vicenza_statement)

    # Attach the previously broad plan mentions to the source-bounded actor roles.
    site_row = by_id["st-chp15-p365-dealers-needed-suitable-stall-site"]
    site_row["object_candidate_id"] = "cand-12227"
    site_row["qualifiers"]["mentioned_candidate_ids"] = ["cand-10480", "cand-12227"]
    site_row["qualifiers"]["relation_candidate_note"] = DECISIONS[site_row["statement_id"]][1]
    site_row["qualifiers"]["open_endpoint_reason"] = DECISIONS[site_row["statement_id"]][2]

    island_row = by_id["st-chp15-p365-memmo-central-island-for-traders"]
    island_row["object_candidate_id"] = "cand-12228"
    island_row["qualifiers"]["mentioned_candidate_ids"] = ["cand-1642", "cand-1650", "cand-3960", "cand-12228"]

    donor_row = by_id["st-chp15-p365-statue-donor-choice"]
    donor_row["object_candidate_id"] = "cand-12229"
    donor_row["qualifiers"]["mentioned_candidate_ids"] = ["cand-1650", "cand-12229"]

    # Link the design-purpose statement to the identified Enlightenment concept as its stated norm.
    gallery_row = by_id["st-chp15-p365-statues-as-civic-virtue-gallery"]
    gallery_row["object_candidate_id"] = "cand-8107"

    # Remove the stale open-endpoint qualifier from statements now mapped to explicit role candidates.
    for sid in ("st-chp15-p365-memmo-central-island-for-traders", "st-chp15-p365-statue-donor-choice"):
        by_id[sid]["qualifiers"].pop("open_endpoint_reason", None)

    new_statement_ids = {row["statement_id"] for row in statement_rows} - set(by_id)
    if new_statement_ids != {vicenza_statement["statement_id"]}:
        raise SystemExit(f"Unexpected new statement IDs: {sorted(new_statement_ids)}")

    if not args.apply:
        true_count = sum(value[0] for value in DECISIONS.values())
        false_count = len(DECISIONS) - true_count
        print(f"DRY-RUN OK: classify {true_count} true + {false_count} false; add one Vicenza statement; add {len(NEW_CANDIDATES)} term candidates and one donor mention; remap dealers/traders mentions.")
        print(f"source={EXPECTED_HASHES['source']} pdf={EXPECTED_HASHES['pdf']} page_image={EXPECTED_HASHES['page_image']}")
        print(f"pre-write tables: statements={EXPECTED_HASHES['statements']} candidates={EXPECTED_HASHES['candidates']} mentions={EXPECTED_HASHES['mentions']}")
        return

    suffix = ".bak-s2-ch15-p365-classification-20261015"
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
