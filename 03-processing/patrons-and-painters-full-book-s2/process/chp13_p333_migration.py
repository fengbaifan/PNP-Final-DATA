"""Controlled S2 migration for printed p.333; dry-run by default."""

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-13.pdf"
BODY = "chp-13:13_CHP-13_intro:l14-19"
PREVIOUS = "chp-13:13_CHP-13_intro:l3-12"
CONTINUATION = "chp-13:13_CHP-13_intro:l21-30"
NOTES = "chp-13:13_CHP-13_intro:l179-251"
SOURCE_SHA = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"
PDF_SHA = "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc"
BACKUP_SUFFIX = ".bak-s2-chp13-p333-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply the reviewed p.333 S2 migration")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("canonical chapter 13 Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-13 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
expected_prefixes = {
    14: "[Page 333]",
    15: "To understand the part played by publishers",
    16: "Lovisa. This practice naturally continued",
    17: "It is evident that the expense and authority",
    18: "Two broad categories of illustrated books",
    19: "Caterina Barbarigo in 1765 through her agent Gaspara Gozzi,1",
}
for line_no, prefix in expected_prefixes.items():
    if not source_lines[line_no - 1].startswith(prefix):
        raise SystemExit(f"canonical source changed at L{line_no}")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_by_id = {row["candidate_id"]: row for row in candidates}
candidate_ids = set(candidate_by_id)
mention_ids = {row["mention_id"] for row in mentions}
statement_ids = {row["statement_id"] for row in statements}
coverage = {row["segment_id"]: row for row in coverage_rows}

state = (
    len(candidates),
    max(int(row["candidate_id"].split("-")[1]) for row in candidates),
    len(mentions),
    len(statements),
)
if state != (9965, 9978, 21180, 9411):
    raise SystemExit(f"unexpected table pre-state: {state}")
for segment in (BODY, PREVIOUS, CONTINUATION, NOTES):
    if segment not in coverage:
        raise SystemExit(f"required coverage row missing: {segment}")
if (coverage[BODY]["disposition"], coverage[BODY]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.333 body segment is not queued/pending")
if (coverage[PREVIOUS]["disposition"], coverage[PREVIOUS]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.332 is not reviewed/partial")
if (coverage[CONTINUATION]["disposition"], coverage[CONTINUATION]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.334 continuation segment is not queued/pending")
if any(row["segment_id"] == BODY for row in mentions) or any(row["segment_id"] == BODY for row in statements):
    raise SystemExit("p.333 body rows already exist")
planned_ids = {f"cand-{n}" for n in range(9979, 9986)}
if candidate_ids & planned_ids:
    raise SystemExit("one or more p.333 candidate IDs already exist")
if any(row["mention_id"].startswith("m-s2-ch13-p333-") for row in mentions):
    raise SystemExit("p.333 mention IDs already exist")
if any(row["statement_id"].startswith("st-chp13-p333-") for row in statements):
    raise SystemExit("p.333 statement IDs already exist")

required_candidates = {
    "cand-0182", "cand-0554", "cand-0555", "cand-1220", "cand-1452", "cand-1453",
    "cand-1901", "cand-2068", "cand-2569", "cand-2719", "cand-8108",
}
missing = required_candidates - candidate_ids
if missing:
    raise SystemExit(f"expected index/body candidates missing: {sorted(missing)}")
if candidate_by_id["cand-1220"]["canonical_name"] != "Gozzi, Gasparo":
    raise SystemExit("the Gozzi index candidate changed")
if "333" not in candidate_by_id["cand-1220"].get("index_page_range", ""):
    raise SystemExit("the Gozzi index candidate no longer points to p.333")
if candidate_by_id["cand-1453"].get("sub_entry") != "Il Gran Teatro delle Pitture e Prospettive di Venezia":
    raise SystemExit("Lovisa work candidate changed")

body_lines = {line_no: source_lines[line_no - 1] for line_no in range(14, 20)}
segment_text = "\n".join(body_lines[line_no] for line_no in range(14, 20))
new_candidates = []


def add_candidate(cid, name, kind, detail, line_no):
    if cid in candidate_ids or any(row["candidate_id"] == cid for row in new_candidates):
        raise SystemExit(f"candidate ID already exists: {cid}")
    row = {field: "" for field in candidate_fields}
    row.update({
        "candidate_id": cid,
        "canonical_name": name,
        "suggested_type": kind,
        "status": "open",
        "detail": detail,
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY}#L{line_no}",
    })
    new_candidates.append(row)


add_candidate(
    "cand-9979",
    "Gaspara Gozzi (spelling in Haskell’s p.333 text; identity unresolved)",
    "person",
    "Haskell names Gaspara Gozzi as Caterina Barbarigo's agent in 1765. The S1 index separately lists Gozzi, Gasparo at p.333; spelling and identity are not merged at S2 and must be adjudicated at S3.",
    19,
)
add_candidate(
    "cand-9980",
    "Zorzi family (branch unspecified in the p.333 arms instruction)",
    "family",
    "The source says a family pamphlet's arms should be intertwined with those of the Zorzi. No individual, branch, ceremony participant, or genealogical link is identified.",
    19,
)
add_candidate(
    "cand-9981",
    "Reproduction of established Venetian masterpieces in prints",
    "procedure",
    "First of four distinct production routes: draughtsmen and engravers, or engravers alone, reproduce established Venetian masterpieces. The passage says the practice continued but had little direct relevance to patronage history.",
    15,
)
add_candidate(
    "cand-9982",
    "Contemporary paintings made primarily for reproduction by engraving",
    "procedure",
    "Second production route: a contemporary painter produces a picture whose primary purpose is reproduction by an engraver. Do not infer that a named painting or commission is described here.",
    16,
)
add_candidate(
    "cand-9983",
    "Artist drawings designed for engraving as book illustrations",
    "procedure",
    "Third and more frequent production route: artists make drawings intended to be engraved as book illustrations.",
    16,
)
add_candidate(
    "cand-9984",
    "Artists producing their own engravings",
    "procedure",
    "Fourth production route in Haskell's typology: artists make their own engravings.",
    16,
)
add_candidate(
    "cand-9985",
    "Poem and eulogy collections commemorating noble ceremonies (publishing category)",
    "term",
    "First of two broad illustrated-book categories identified by Haskell: collections commemorating ceremonies involving the nobility. This is a genre/category, not a specific publication.",
    18,
)

all_candidate_ids = candidate_ids | {row["candidate_id"] for row in new_candidates}
new_mentions = []


def add_mention(line_no, surface, cid, note="", occurrence=0):
    if cid not in all_candidate_ids:
        raise SystemExit(f"unknown candidate for mention: {surface!r} {cid}")
    line = body_lines[line_no]
    starts = []
    cursor = 0
    while True:
        at = line.find(surface, cursor)
        if at < 0:
            break
        starts.append(at)
        cursor = at + 1
    if occurrence >= len(starts):
        raise SystemExit(f"mention text missing at L{line_no}: {surface!r} occurrence {occurrence}")
    start = sum(len(body_lines[n]) + 1 for n in range(14, line_no)) + starts[occurrence]
    end = start + len(surface)
    if segment_text[start:end] != surface:
        raise SystemExit(f"mention span mismatch at L{line_no}: {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch13-p333-{len(new_mentions) + 1:03d}",
        "segment_id": BODY,
        "candidate_id": cid,
        "surface_form": surface,
        "start_char": start,
        "end_char": end,
        "note": note,
    })
    new_mentions.append(row)


add_mention(15, "publishers", "cand-2068")
add_mention(15, "draughtsmen and engravers, or sometimes merely engravers, might reproduce wellestablished masterpieces of Venetian art", "cand-9981")
add_mention(15, "Venetian", "cand-2719", "Geographic adjective nested in the first production-route mention.")
add_mention(15, "Domenico", "cand-1452", "First half of a personal name split by the S0 line break; continued by Lovisa at L16.")
add_mention(16, "Lovisa", "cand-1452", "Second half of the split personal name Domenico Lovisa.")
add_mention(15, "the book", "cand-1453", "Anaphoric reference to Il Gran Teatro, named at p.332.")
add_mention(16, "leading contemporary painters sometimes produced pictures whose primary purpose was to be reproduced by some engraver", "cand-9982")
add_mention(16, "artists produced drawings designed to be engraved as bookillustrations", "cand-9983", "S0 OCR lacks a hyphen in bookillustrations; see page-image correction.")
add_mention(16, "a number of artists produced their own engravings", "cand-9984")
add_mention(17, "Tiepolo", "cand-2569")
add_mention(17, "Piazzetta", "cand-1901")
add_mention(17, "A well-established publisher", "cand-2068")
add_mention(17, "Such publishers", "cand-2068", "Continuation of the previously stated publisher group.")
add_mention(18, "Venice", "cand-2719")
add_mention(18, "the nobility", "cand-8108")
add_mention(18, "collections of poems and eulogies", "cand-9985")
add_mention(18, "the publisher", "cand-2068")
add_mention(19, "Caterina Barbarigo", "cand-0182")
add_mention(19, "Gaspara Gozzi", "cand-9979", "Haskell's text spelling; do not merge with index candidate cand-1220 (Gozzi, Gasparo) at S2.")
add_mention(19, "the Zorzi", "cand-9980", "Family name in the coat-of-arms instruction; branch and members unspecified.")
add_mention(19, "Venetian", "cand-2719", "Adjectival reference to the poets' city context.")
add_mention(19, "These collections", "cand-9985", "Anaphoric reference to the commemorative poem and eulogy category.")
add_mention(19, "Bundles of them", "cand-9985", "Anaphoric reference within an unattributed quotation; the quote continues on p.334.")

new_mentions.sort(key=lambda row: (int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
for i, left in enumerate(new_mentions):
    left_start, left_end = int(left["start_char"]), int(left["end_char"])
    for right in new_mentions[i + 1:]:
        right_start, right_end = int(right["start_char"]), int(right["end_char"])
        if right_start >= left_end:
            break
        strict_nested = (
            (left_start <= right_start and right_end <= left_end and (left_start, left_end) != (right_start, right_end))
            or (right_start <= left_start and left_end <= right_end and (left_start, left_end) != (right_start, right_end))
        )
        if not strict_nested:
            raise SystemExit(f"crossing or duplicate mention spans: {left['mention_id']} / {right['mention_id']}")
if any(row["mention_id"] in mention_ids for row in new_mentions):
    raise SystemExit("p.333 mention ID already exists")

new_statements = []
OCR_CORRECTIONS = [
    {"source_line": 15, "ocr": "wellestablished", "print": "well-established", "basis": "CHP-13.pdf physical page 2."},
    {"source_line": 16, "ocr": "bookillustrations", "print": "book-illustrations", "basis": "CHP-13.pdf physical page 2."},
    {"source_line": 19, "ocr": "500 copies'must", "print": "500 copies must", "basis": "CHP-13.pdf physical page 2."},
]


def excerpt(line_no, start_text, end_text):
    line = body_lines[line_no]
    start = line.find(start_text)
    end = line.find(end_text, start)
    if start < 0 or end < 0:
        raise SystemExit(f"quote boundary missing at L{line_no}: {start_text!r} / {end_text!r}")
    return line[start:end + len(end_text)]


def cross_line_excerpt(first_line, last_line, start_text, end_text):
    text = "\n".join(body_lines[n] for n in range(first_line, last_line + 1))
    start = text.find(start_text)
    end = text.find(end_text, start)
    if start < 0 or end < 0:
        raise SystemExit(f"cross-line quote boundary missing: {start_text!r} / {end_text!r}")
    return text[start:end + len(end_text)]


def add_statement(suffix, subject, obj, predicate, line_start, line_end, claim, quote, qualification, mentioned,
                  *, speaker="Haskell", layer="authorial narrative", extra=None):
    statement_id = f"st-chp13-p333-{suffix}"
    if statement_id in statement_ids or any(row["statement_id"] == statement_id for row in new_statements):
        raise SystemExit(f"statement ID already exists: {statement_id}")
    if quote not in segment_text:
        raise SystemExit(f"statement quote not anchored in S0: {statement_id}")
    if any(cid not in all_candidate_ids for cid in mentioned):
        raise SystemExit(f"mentioned-candidate FK missing: {statement_id}")
    for cid in (subject, obj):
        if cid and cid not in all_candidate_ids:
            raise SystemExit(f"statement endpoint FK missing: {statement_id}: {cid}")
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 333,
        "pdf_physical_page": 2,
        "claim": claim,
        "speaker": speaker,
        "text_layer": layer,
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "ocr_corrections": [correction for correction in OCR_CORRECTIONS if line_start <= correction["source_line"] <= line_end],
    }
    if extra:
        qualifiers.update(extra)
    new_statements.append({
        "statement_id": statement_id,
        "segment_id": BODY,
        "subject_candidate_id": subject or None,
        "object_candidate_id": obj or None,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
    })


def pending_note(marker):
    return {
        "footnote_marker": marker,
        "footnote_text_pending": True,
        "footnote_segment": NOTES,
        "footnote_body_link_status": "pending",
        "cross_reference_segments": [NOTES],
    }


typology_quote = cross_line_excerpt(15, 16, "four ventures, closely related", "their own engravings.")
lovisa_quote = cross_line_excerpt(15, 16, "Such was the book sponsored by Domenico", "Lovisa.")
continued_practice_quote = excerpt(16, "This practice naturally continued", "history of patronage.")
picture_route_quote = excerpt(16, "Secondly, leading contemporary painters", "some engraver.")
drawing_route_quote = excerpt(16, "Thirdly, and far more frequently", "bookillustrations.")
self_engraving_quote = excerpt(16, "And fourthly", "their own engravings.")
publisher_necessity_quote = excerpt(17, "It is evident that the expense", "publisher was essential.")
premises_quote = excerpt(17, "Such publishers always owned", "printing works.")
commercial_activity_quote = excerpt(17, "They dealt either in sets", "artists they found suitable.")
patronage_quote = excerpt(17, "In this way they were considerable patrons", "make it possible;")
dedications_quote = excerpt(17, "and the list of subscribers", "aimed at.")
categories_quote = excerpt(18, "Two broad categories", "eighteenth century.")
commemorative_quote = excerpt(18, "There were, first,", "same kind.")
pamphlet_quote = excerpt(18, "These might be little more", "instructions as to their make-up.")
popularity_quote = excerpt(19, "These collections, which were", "enormously popular with the public.")
caterina_quote = cross_line_excerpt(18, 19, "‘The paper must be of excellent quality,’ wrote", "500 copies'must be printed.’")
bundles_quote = excerpt(19, "‘Bundles of them are sent round", "trousseau of verses.")

add_statement(
    "four-illustration-production-routes", None, None, "distinguished_four_related_but_distinct_production_routes",
    15, 16,
    "Haskell distinguishes four related but non-identical routes for producing art for print: reproducing established works, making pictures for engraving, making drawings for illustrated books, and artists engraving their own work.",
    typology_quote,
    "This is Haskell's typology; the four routes should not be collapsed into a single patronage relationship.",
    ["cand-9981", "cand-9982", "cand-9983", "cand-9984"],
    layer="authorial classification",
)
add_statement(
    "lovisa-book-sponsored-example", "cand-1453", "cand-1452", "sponsored_by",
    15, 16,
    "Haskell identifies the Il Gran Teatro named on p.332 as the book sponsored by Domenico Lovisa in the first reproduction venture.",
    lovisa_quote,
    "This is a cross-page anaphoric link to the existing work candidate and p.332 publication statement; sponsorship is recorded separately from publication.",
    ["cand-1453", "cand-1452", "cand-9981"],
    extra={"relation_candidate": True, "cross_reference_segments": [PREVIOUS], "cross_reference_statement_ids": ["st-chp13-p332-lovisa-gran-teatro-publication-and-illustrations"]},
)
add_statement(
    "reproduction-practice-and-patronage-relevance", "cand-9981", None, "continued_but_had_little_direct_patronage_relevance",
    16, 16,
    "Haskell says reproduction of established works continued through the eighteenth century, as in the past, but had little direct relevance to patronage history.",
    continued_practice_quote,
    "This is Haskell's explicit assessment of the first route; it does not say the practice had no patrons or economic effects.",
    ["cand-9981", "cand-1453"],
    layer="authorial assessment",
)
add_statement(
    "contemporary-pictures-made-for-engraving", "cand-9982", None, "contemporary_painters_made_pictures_for_reproduction",
    16, 16,
    "The second route consists of contemporary painters making pictures whose primary purpose was reproduction by an engraver.",
    picture_route_quote,
    "A general production category; no individual picture or commission is identified in this sentence.",
    ["cand-9982"],
)
add_statement(
    "drawings-made-for-book-illustration", "cand-9983", None, "artists_made_drawings_to_be_engraved_as_book_illustrations",
    16, 16,
    "The third and more frequent route consists of artists making drawings designed to be engraved as book illustrations.",
    drawing_route_quote,
    "The comparative frequency is Haskell's account; this does not identify a particular drawing or book.",
    ["cand-9983"],
)
add_statement(
    "artists-made-own-engravings", "cand-9984", None, "artists_produced_their_own_engravings",
    16, 16,
    "The fourth route consists of artists producing their own engravings.",
    self_engraving_quote,
    "The passage names no individual artist or engraving in this category.",
    ["cand-9984"],
)
add_statement(
    "publishers-enabled-high-cost-artist-commissions", "cand-2068", None, "publisher_required_for_high_cost_reproduction_commissions",
    17, 17,
    "Haskell says an engraver could not bear the expense and authority needed to persuade artists of Tiepolo's or Piazzetta's stature to make work for reproduction; an established publisher was essential.",
    publisher_necessity_quote,
    "The claim concerns the capacity required for such ventures; it does not identify an actual commission by Tiepolo or Piazzetta on this page.",
    ["cand-2068", "cand-2569", "cand-1901"],
)
add_statement(
    "publishers-owned-commercial-premises", "cand-2068", None, "publishers_owned_shops_and_major_firms_owned_printing_works",
    17, 17,
    "Haskell says publishers always owned their own shops and the more important publishers also owned printing works.",
    premises_quote,
    "The source's generalization ‘always’ is preserved; it is not independently verified here.",
    ["cand-2068"],
)
add_statement(
    "publishers-sales-employment-and-commissions", "cand-2068", None, "sold_prints_or_books_employed_printmakers_and_commissioned_artists",
    17, 17,
    "Haskell says publishers dealt in loose prints or illustrated books, employed printmakers, and commissioned suitable artists to produce drawings or sometimes paintings.",
    commercial_activity_quote,
    "This describes publisher practices in general; no individual employment contract or commission is identified.",
    ["cand-2068"],
    extra={"relation_candidate": True},
)
add_statement(
    "publishers-as-patrons-and-reliance-on-patronage", "cand-2068", None, "acted_as_patrons_but_sometimes_depended_on_other_patronage",
    17, 17,
    "Haskell characterizes publishers as patrons in their own right while noting that expensive ventures often depended on patronage to become possible.",
    patronage_quote,
    "The patrons who financed expensive ventures are not named; the statement does not equate the publisher's own patronage with their financing role.",
    ["cand-2068"],
)
add_statement(
    "subscribers-and-dedications-reveal-target-market", "cand-2068", None, "subscriber_lists_and_dedications_indicate_intended_market",
    17, 17,
    "Haskell says subscriber lists and book dedications can reveal the market at which publishers aimed.",
    dedications_quote,
    "This is a claim about what those book paratexts can show, not evidence about any specific subscriber or dedication on this page.",
    ["cand-2068"],
)
add_statement(
    "two-categories-of-illustrated-books", None, None, "identified_two_broad_categories_of_illustrated_books_in_venice",
    18, 18,
    "Haskell divides eighteenth-century Venetian illustrated books into two broad categories, beginning with collections of poems and eulogies for ceremonies involving the nobility.",
    categories_quote,
    "The second category is not defined in this segment and is deferred to the next source segment; the two categories are not treated as exhaustive beyond Haskell's framing.",
    ["cand-2719", "cand-9985", "cand-8108"],
)
add_statement(
    "commemorative-poetry-for-noble-ceremonies", "cand-9985", "cand-8108", "commemorated_specific_noble_ceremonies",
    18, 18,
    "The first category consisted of poem and eulogy collections commemorating noble ceremonies such as taking office, marriage, or a young woman's entry into a convent.",
    commemorative_quote,
    "These are examples of ceremony types; no individual person, family, marriage, or convent is identified.",
    ["cand-9985", "cand-8108"],
)
add_statement(
    "pamphlet-format-and-commissioned-design", "cand-9985", "cand-2068", "pamphlets_commissioned_to_publisher_with_design_instructions",
    18, 18,
    "Haskell says such collections could be brief pamphlets with decorated title pages or fuller illustrations and were commissioned from publishers with instructions about their design.",
    pamphlet_quote,
    "The text gives a range of possible formats; not every collection had the same length or illustration scheme.",
    ["cand-9985", "cand-2068"],
    extra={"relation_candidate": True},
)
add_statement(
    "collections-popular-and-burdened-poets", "cand-9985", None, "collections_popular_but_required_poets_contributions_and_supported_artists",
    19, 19,
    "Haskell says the collections were extremely popular, while required verses burdened Venetian poets and the publications supported many artists.",
    popularity_quote,
    "This is Haskell's characterization; no poet, artist, collection count, or measure of popularity is supplied.",
    ["cand-9985", "cand-2719"],
)
add_statement(
    "barbarigo-1765-pamphlet-instructions-through-gozzi", "cand-0182", "cand-9979", "conveyed_pamphlet_specifications_through_agent",
    18, 19,
    "Haskell quotes Caterina Barbarigo's 1765 specifications, relayed through the agent he names as Gaspara Gozzi: high-quality paper and type, a restrained title page rather than an engraving frieze, selected page decorations, family arms intertwined with those of the Zorzi, 24 pages, and 500 copies.",
    caterina_quote,
    "Direct wording is quoted by Haskell and not independently checked. The text's Gaspara spelling conflicts with the S1 index form Gozzi, Gasparo at p.333; identities remain separate until S3. The instructions are one example, not a universal publisher contract.",
    ["cand-0182", "cand-9979", "cand-9980", "cand-9985", "cand-2068"],
    speaker="Caterina Barbarigo as quoted by Haskell; wording conveyed through Gaspara Gozzi",
    layer="reported correspondence/instruction quotation",
    extra={**pending_note(1), "relation_candidate": True, "source_spelling_conflict": {"book_text": "Gaspara Gozzi", "index_candidate_id": "cand-1220", "index_form": "Gozzi, Gasparo", "resolution": "unresolved"}},
)
add_statement(
    "anonymous-quotation-on-poem-collections", None, "cand-9985", "described_as_gifts_but_rarely_read_and_expected_at_weddings",
    19, 19,
    "An unattributed quoted voice describes these collections as gifts circulated to guests and relatives, quickly damaged, rarely read, yet expected as part of a bride's trousseau.",
    bundles_quote,
    "The quotation continues into p.334 and its speaker is unresolved. Do not assign it to Gaspara Gozzi from adjacency alone; complete the claim and inspect its note after processing the continuation.",
    ["cand-9985"],
    speaker="Unattributed source quoted by Haskell",
    layer="quotation with unresolved attribution",
    extra={"continuation_status": "open", "continuation_to_segment_id": CONTINUATION, "continuation_quote_pending": True, "speaker_identity_status": "undecided", "cross_reference_segments": [CONTINUATION]},
)

all_candidates = candidates + new_candidates
all_mentions = mentions + new_mentions
all_statements = statements + new_statements
if len({row["candidate_id"] for row in all_candidates}) != len(all_candidates):
    raise SystemExit("duplicate candidate IDs")
if len({row["mention_id"] for row in all_mentions}) != len(all_mentions):
    raise SystemExit("duplicate mention IDs")
if len({row["statement_id"] for row in all_statements}) != len(all_statements):
    raise SystemExit("duplicate statement IDs")

coverage[BODY].update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "source_line_ranges": "L14-19",
    "note": "Printed p.333 body reviewed against CHP-13.pdf physical page 2. The anonymous quotation beginning ‘Bundles of them’ continues into p.334 S0 L22–24 and its speaker is unresolved; Caterina Barbarigo's instructions have footnote marker 1 pending the consolidated notes L179–251. Keep partial until continuation and note are processed and linked.",
})

candidate_rows = sorted(all_candidates, key=lambda row: row["candidate_id"])
mention_rows = sorted(all_mentions, key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
all_statements.sort(key=lambda row: row["statement_id"])
coverage_rows = [coverage[row["segment_id"]] for row in coverage_rows]

print(f"p.333 dry-run: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements")
print("coverage: p.333 body -> reviewed/partial; quote continues to p.334 and citation remains pending")
print(f"totals: {len(candidate_rows)} candidates, {len(mention_rows)} mentions, {len(all_statements)} statements")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

paths = [candidate_path, mention_path, statement_path, coverage_path]
for path in paths:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"recovery copy already exists: {backup.name}")
for path in paths:
    shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
write_csv(candidate_path, candidate_fields, candidate_rows)
write_csv(mention_path, mention_fields, mention_rows)
write_jsonl(statement_path, all_statements)
write_csv(coverage_path, coverage_fields, coverage_rows)
print(f"applied; four recovery copies created with suffix {BACKUP_SUFFIX}")
