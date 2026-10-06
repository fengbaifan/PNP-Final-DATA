"""Controlled S2 migration for chapter 8 printed p.209 body text.

Default invocation is a read-only dry run. Printed-page readings are recorded
in S2; immutable S0 source transcriptions are never edited by this script.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_i.md"
SOURCE_PATH = ROOT / SOURCE_REL
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l62-70"
NEXT_SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l72-82"
BACKUP_SUFFIX = ".bak-s2-chp8-p209-body-20260930"
EXPECTED_MAX_CANDIDATE = 7464


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl_atomic(path: Path, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
segment_path = TABLES / "segments.jsonl"
candidate_fields, candidate_rows = read_csv(candidate_path)
mention_fields, mention_rows = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statement_rows = read_jsonl(statement_path)
segment_rows = read_jsonl(segment_path)
segments = {row["segment_id"]: row for row in segment_rows}
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}

meta = segments.get(SEGMENT_ID)
if not meta or meta["source_file"] != SOURCE_REL or (int(meta["line_start"]), int(meta["line_end"])) != (62, 70):
    raise SystemExit("p.209 segment metadata changed; review before migration")
raw_source = SOURCE_PATH.read_bytes()
if hashlib.sha256(raw_source).hexdigest() != meta["asset_sha256"]:
    raise SystemExit("source file fingerprint changed; rebuild segments and review")
source_lines = SOURCE_PATH.read_text(encoding="utf-8-sig").splitlines()
segment_lines = source_lines[61:70]
segment_text = "\n".join(segment_lines)
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != meta["sha256"]:
    raise SystemExit("p.209 segment text hash changed; review before migration")
if coverage_by_id.get(SEGMENT_ID, {}).get("disposition") != "queued":
    raise SystemExit("expected queued p.209 coverage; inspect before rerunning")
if any(row["segment_id"] == SEGMENT_ID for row in mention_rows):
    raise SystemExit("mentions already exist for p.209; inspect before rerunning")
if any(row["segment_id"] == SEGMENT_ID for row in statement_rows):
    raise SystemExit("statements already exist for p.209; inspect before rerunning")

candidate_ids = {row["candidate_id"] for row in candidate_rows}
existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_statement_ids = {row["statement_id"] for row in statement_rows}
current_max = max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows)
if current_max != EXPECTED_MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: expected {EXPECTED_MAX_CANDIDATE}, found {current_max}")


def candidate(cid, name, typ, detail, line):
    return {
        "candidate_id": cid,
        "index_entry_id": "",
        "canonical_name": name,
        "index_page_range": "",
        "suggested_type": typ,
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": detail,
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L{line}",
    }


new_candidates = [
    candidate("cand-7465", "Unnamed Viceroy whose authority over Messina Antonio Ruffo opposed", "person",
              "The source identifies the office but not the office-holder; do not align to a Neapolitan or Sicilian viceroy without evidence.", 65),
    candidate("cand-7466", "Strada Emmanuela in Messina", "place",
              "The street name is corrected from S0 OCR only in S2 by comparison with CHP-8.pdf physical page 7; exact modern location is not established here.", 67),
    candidate("cand-7467", "Unidentified palace in Messina built for Antonio Ruffo by his mother", "place",
              "The passage gives a street location and builder but no palace name or surviving-site identification.", 65),
    candidate("cand-7468", "Antonio Ruffo's unidentified picture collection", "",
              "Collection is a meaningful object here, but the current entity taxonomy has no collection type; retain the type unresolved.", 65),
    candidate("cand-7469", "Calabria region", "place",
              "Named as the apparent limit of Ruffo's travel; Haskell qualifies the claim with 'seems'.", 68),
    candidate("cand-7470", "Antonio Ruffo's unnamed information and ordering intermediaries", "term",
              "The passage includes family, friends, employed artists and picture dealers pressed into agent-like work; no individual agent is named.", 68),
    candidate("cand-7471", "Unidentified Guercino picture required to match Rembrandt's Aristotle", "work",
              "Haskell says Guercino's own picture was required to match Rembrandt's work; no title, subject beyond the comparison, or location is supplied.", 69),
    candidate("cand-7472", "Metropolitan Museum in New York (institution as named in Haskell)", "institution",
              "The book gives this as the reported location of Rembrandt's Aristotle; no current catalogue record is independently checked here.", 69),
    candidate("cand-7473", "New York (place in the reported Metropolitan Museum location)", "place",
              "Recorded only as the city attached to the work's location in the book.", 69),
    candidate("cand-7474", "Symmetrical arrangement and picture-pairing practice in Ruffo's collection", "term",
              "Haskell describes a collection arrangement pattern and pairing preference that affected composition; no installation plan is supplied.", 68),
    candidate("cand-7475", "South Italy region", "place",
              "Regional setting given for Ruffo's residence; no narrower boundary is defined in this passage.", 63),
]
new_candidate_ids = {row["candidate_id"] for row in new_candidates}
if len(new_candidate_ids) != len(new_candidates) or new_candidate_ids & candidate_ids:
    raise SystemExit("planned candidate IDs collide")

mention_specs = []


def add(line_number, surface, cid, note, occurrence=1):
    mention_specs.append((line_number, surface, cid, note, occurrence))


add(63, "South Italy", "cand-7475", "Regional location given for Ruffo's activity; scope follows the source wording.")
add(63, "Don Antonio Ruffo", "cand-2297", "Patron introduced at the start of this section.")
add(63, "Messina", "cand-1655", "Ruffo's reported birthplace.")
add(63, "one of the great aristocratic families", "cand-2297", "Unspecified family background reported for Ruffo; the family is not identified.")
add(65, "Spanish rule", "cand-4591", "Political context; mapped to the polity candidate, not to a geographic place.")
add(65, "his native city", "cand-1655", "Anaphoric reference to Messina.")
add(65, "the Viceroy", "cand-7465", "Unnamed authority opposed by Ruffo in support of Messina's privileges.")
add(65, "his palace", "cand-7467", "Unidentified Ruffo residence in Messina.")
add(65, "Messina", "cand-1655", "City where Ruffo's palace is said to have become a cultural centre.", 1)
add(65, "more than 350 pictures", "cand-7468", "Size of the collection reported at Ruffo's death.")
add(65, "Italy", "cand-3461", "Origin of many artists whose pictures were in Ruffo's collection.")
add(66, "Ruffo", "cand-2297", "Antonio Ruffo, subject of the collecting chronology.")
add(66, "the palace", "cand-7467", "Anaphoric reference to Ruffo's palace in Messina.")
add(67, "Strada Emnianuela", "cand-7466", "S0 OCR form; the print reads Strada Emmanuela.")
add(67, "his mother", "cand-0160", "The passage identifies Ruffo's mother by her title, Duchess of Bagnara.")
add(67, "the Duchess of Bagnara", "cand-0160", "Ruffo's mother, said to have built the palace.")
add(68, "Calabria", "cand-7469", "Apparent travel boundary; the source says Ruffo seems never to have travelled beyond it.")
add(68, "Italy", "cand-3461", "Location of leading painters known to Ruffo through agents.")
add(68, "agents", "cand-7470", "Unspecified information intermediaries.")
add(68, "his family", "cand-7470", "Group pressed into acting as intermediaries for Ruffo.")
add(68, "his friends", "cand-7470", "Group pressed into acting as intermediaries for Ruffo.")
add(68, "the artists he employed", "cand-7470", "Group pressed into acting as intermediaries for Ruffo.")
add(68, "picture dealers", "cand-7470", "Group pressed into acting as intermediaries for Ruffo.")
add(68, "his agents", "cand-7470", "Unspecified intermediaries through whom Ruffo ordered some pictures.", 1)
add(68, "his contemporaries", "cand-2301", "Index subentry for Ruffo's interest in contemporary artists.")
add(68, "size and expense", "cand-2302", "Index subentry matching the two considerations that guided Ruffo.")
add(68, "a symmetrical pattern", "cand-7474", "Collection arrangement practice described by Haskell.")
add(68, "pairs", "cand-7474", "Pairing preference that Haskell says affected picture composition.")
add(68, "Guercino", "cand-1258", "Painter who asked for a drawing to match his own picture.")
add(68, "Rembrandt’s Aristotle contemplating the Bust of Homer", "cand-2119", "Work by Rembrandt used as the comparator for Guercino's picture.")
add(68, "Rembrandt’s", "cand-2117", "Artist named in the title and comparison; this mention is nested within the work title.")
add(69, "Metropolitan Museum", "cand-7472", "Institution named as the location of Rembrandt's picture.")
add(69, "New York", "cand-7473", "City attached to the Metropolitan Museum location.")
add(69, "his own picture", "cand-7471", "Unidentified Guercino painting required to match Rembrandt's Aristotle.")
add(69, "Ruffo", "cand-2297", "Antonio Ruffo, whose picture prices and offers are discussed.", 1)
add(69, "Guercino", "cand-1258", "Painter whose fixed figure rate and negotiations are described.", 1)
add(69, "Ruffo", "cand-2297", "Antonio Ruffo's offer of one hundred scudi.", 2)
add(69, "Ruffo", "cand-2297", "Antonio Ruffo later raised the sum to 100 ducats.", 3)
add(69, "Guercino", "cand-1258", "Painter who answered Ruffo's later offer.", 2)
add(70, "Ruffo", "cand-2297", "Antonio Ruffo, receiving an artist's first picture.")
add(70, "Messina", "cand-1655", "City where the first picture arrived.")
add(70, "his gallery", "cand-7468", "Anaphoric reference to Ruffo's picture collection.")
add(70, "a representative collection", "cand-7468", "Ruffo's stated collecting aim; the sentence continues onto p.210.")

new_mentions = []
line_offsets = {}
offset = 0
for line_number, line in zip(range(62, 71), segment_lines):
    line_offsets[line_number] = offset
    offset += len(line) + 1
for index, (line_number, surface, cid, note, occurrence) in enumerate(mention_specs, 1):
    if cid not in candidate_ids | new_candidate_ids:
        raise SystemExit(f"mention references missing candidate: {cid}")
    source_line = source_lines[line_number - 1]
    starts = []
    cursor = 0
    while True:
        found = source_line.find(surface, cursor)
        if found < 0:
            break
        starts.append(found)
        cursor = found + 1
    if occurrence > len(starts):
        raise SystemExit(f"line {line_number}: occurrence {occurrence} missing for {surface!r}; found {len(starts)}")
    start = line_offsets[line_number] + starts[occurrence - 1]
    end = start + len(surface)
    if segment_text[start:end] != surface:
        raise SystemExit(f"mention offset mismatch for {surface!r}")
    new_mentions.append({
        "mention_id": f"m-chp8-p209-{index:03d}",
        "segment_id": SEGMENT_ID,
        "candidate_id": cid,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    })

new_mentions.sort(key=lambda row: (int(row["start_char"]), int(row["end_char"])))
for i, first in enumerate(new_mentions):
    if first["mention_id"] in existing_mention_ids:
        raise SystemExit(f"mention ID collision: {first['mention_id']}")
    for second in new_mentions[i + 1:]:
        a, b = int(first["start_char"]), int(first["end_char"])
        c, d = int(second["start_char"]), int(second["end_char"])
        if a < d and c < b:
            nested = (a <= c and d <= b and (a, b) != (c, d)) or (c <= a and b <= d and (a, b) != (c, d))
            if not nested:
                raise SystemExit(f"overlapping non-nested mentions: {first!r} / {second!r}")


def make_statement(sid, line_start, line_end, predicate, claim, qualification,
                   *, subject=None, obj=None, mentioned=(), quote=None, extra=None, speaker="Haskell"):
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 209,
        "pdf_physical_page": 7,
        "claim": claim,
        "speaker": speaker,
        "text_layer": "body",
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    if extra:
        qualifiers.update(extra)
    return {
        "statement_id": sid,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_REL,
    }


ocr_corrections = [
    {"source_line": 65, "ocr": "Use", "print": "life", "basis": "CHP-8.pdf physical page 7."},
    {"source_line": 67, "ocr": "Strada Emnianuela", "print": "Strada Emmanuela", "basis": "CHP-8.pdf physical page 7."},
    {"source_line": 69, "ocr": "halfa figure", "print": "half a figure", "basis": "CHP-8.pdf physical page 7."},
]

body_statements = [
    make_statement("st-chp8-p209-ruffo-born-messina-aristocratic-family", 63, 63,
                   "patron_born_messina_in_1610_into_aristocratic_family",
                   "Haskell says Don Antonio Ruffo was born in Messina in 1610 and belonged to one of the great aristocratic families.",
                   "The family is not named; the statement is Haskell's report, not independently verified here.",
                   subject="cand-2297", obj="cand-1655", mentioned=["cand-2297", "cand-1655"],
                   quote="Don Antonio Ruffo was born in Messina in 1610 of one of the great aristocratic families.",
                   extra={"date": 1610, "footnote_marker": 1}),
    make_statement("st-chp8-p209-ruffo-trade-and-tax-revenue", 63, 63,
                   "patron_engaged_in_trade_and_received_tax_revenues",
                   "Haskell says Ruffo engaged in trade and further increased his income through revenues from taxes on grain, silk and other vital goods.",
                   "No revenue amounts, tax jurisdictions, or trading partners are specified.",
                   subject="cand-2297",
                   quote="This did not prevent him engaging in trade, and his income was still further increased by the vast revenues he drew from taxes on grain, silk and other vital goods."),
    make_statement("st-chp8-p209-ruffo-outlawed-for-supporting-messina-privileges", 64, 65,
                   "patron_briefly_outlawed_after_supporting_native_city_privileges",
                   "Haskell says Ruffo played a limited part in political activity under Spanish rule and was briefly outlawed in 1661 for supporting Messina's privileges against the Viceroy's authority.",
                   "The source does not name the Viceroy or specify the legal process; the event remains Haskell's report.",
                   subject="cand-2297", obj="cand-7465", mentioned=["cand-2297", "cand-1655", "cand-4591", "cand-7465"],
                   quote="He played a limited part in what little political activity was permitted the nobility under\nSpanish rule, and in 1661 he was outlawed for a short time for supporting the privileges of his native city against the authority of the Viceroy.",
                   extra={"date": 1661, "relation_candidate": True}),
    make_statement("st-chp8-p209-ruffo-patronage-palace-cultural-centre-until-death", 65, 65,
                   "patron_devoted_life_to_arts_and_palace_was_cultural_centre",
                   "Haskell says most of Ruffo's life was devoted to patronage of the arts and his palace in Messina became the centre of cultural life until his death in 1678.",
                   "This is Haskell's characterization; the palace is unnamed.",
                   subject="cand-2297", obj="cand-7467", mentioned=["cand-2297", "cand-7467", "cand-1655"],
                   quote="But most of his Use was devoted to patronage of the arts and his palace in Messina became the centre of cultural life there until his death in 1678.",
                   extra={"date": 1678, "ocr_corrections": [ocr_corrections[0]], "relation_candidate": True}),
    make_statement("st-chp8-p209-ruffo-collection-over-350-at-death", 65, 65,
                   "picture_collection_reported_over_350_at_patron_death",
                   "Haskell says Ruffo's palace contained more than 350 pictures at his death, painted by artists throughout Italy and elsewhere.",
                   "The total and geographic range are Haskell's report; no inventory is cited in this passage.",
                   subject="cand-2297", obj="cand-7468", mentioned=["cand-2297", "cand-7468", "cand-3461"],
                   quote="At that time it contained more than 350 pictures painted by artists all over Italy and even elsewhere.",
                   extra={"relation_candidate": True}),
    make_statement("st-chp8-p209-ruffo-began-collecting-about-1646-palace-built-by-mother", 66, 67,
                   "collector_started_about_1646_and_mother_built_messina_palace",
                   "Haskell says Ruffo began collecting about 1646 after moving into a palace on Strada Emmanuela that his mother, the Duchess of Bagnara, had built for him.",
                   "The collecting date is approximate; the palace has no supplied proper name. S0's street spelling is corrected only in S2.",
                   subject="cand-2297", obj="cand-7467",
                   mentioned=["cand-2297", "cand-7467", "cand-7466", "cand-0160"],
                   quote="Ruffo began collecting in about 1646 shortly after moving into the palace in the\nStrada Emnianuela which his mother, the Duchess of Bagnara, had built for him.",
                   extra={"date_text": "about 1646", "relation_candidate": True, "ocr_corrections": [ocr_corrections[1]]}),
    make_statement("st-chp8-p209-ruffo-collected-almost-uninterrupted-for-thirty-years", 67, 67,
                   "collector_collected_almost_without_interruption_for_thirty_years",
                   "Haskell says Ruffo continued collecting almost without interruption for the next thirty years.",
                   "The duration is relative to the approximate start date; do not calculate a precise end year.",
                   subject="cand-2297", quote="He continued almost without interruption for the next thirty years.",
                   extra={"period_text": "the next thirty years", "modality": "almost"}),
    make_statement("st-chp8-p209-ruffo-personal-interest-and-limited-acquaintance", 67, 67,
                   "patron_took_interest_in_commissions_but_likely_knew_few_other_paintings",
                   "Haskell says evidence shows Ruffo took great personal interest in ordered works, while his acquaintance with paintings other than his own must have been negligible.",
                   "The contrast is Haskell's assessment; 'must have been' marks an inference, not a direct measurement of Ruffo's knowledge.",
                   subject="cand-2297",
                   quote="A good deal of evidence makes it clear beyond doubt that he took a great personal interest in the works that he ordered, and yet it is an astonishing fact that his acquaintance with any paintings other than his own must have been negligible.",
                   extra={"modality": "must have been", "relation_candidate": True}),
    make_statement("st-chp8-p209-ruffo-travelled-seemingly-only-within-calabria", 67, 68,
                   "patron_seems_never_to_have_travelled_beyond_calabria",
                   "Haskell says Ruffo seems never to have travelled beyond Calabria and heard about leading painters elsewhere entirely through agents.",
                   "The travel claim is explicitly qualified with 'seems'; no travel itinerary is supplied.",
                   subject="cand-2297", obj="cand-7469", mentioned=["cand-2297", "cand-7469", "cand-3461", "cand-7470"],
                   quote="He seems never to have travelled beyond\nCalabria, and he heard about the leading painters in Italy and elsewhere entirely through agents.",
                   extra={"modality": "seems", "relation_candidate": True}),
    make_statement("st-chp8-p209-ruffo-pressed-network-into-agency", 68, 68,
                   "patron_used_family_friends_artists_and_dealers_as_intermediaries",
                   "Haskell says Ruffo pressed family, friends, employed artists and picture dealers into acting for him as intermediaries.",
                   "No individual intermediary or specific information transaction is named.",
                   subject="cand-2297", obj="cand-7470", mentioned=["cand-2297", "cand-7470"],
                   quote="Everyone was pressed into acting for him in this capacity: his family, his friends, the artists he employed and picture dealers.",
                   extra={"relation_candidate": True}),
    make_statement("st-chp8-p209-ruffo-agents-reported-market-and-contemporary-artists", 68, 68,
                   "intermediaries_reported_artist_talent_and_market_state",
                   "Haskell says Ruffo's intermediaries informed him about more talented working artists, especially contemporaries, and the state of the market.",
                   "The passage names no informant or artist in this general description.",
                   subject="cand-2297", obj="cand-7470", mentioned=["cand-2297", "cand-7470", "cand-2301"],
                   quote="From them he was informed who were the more talented artists at work—for he was primarily interested in his contemporaries— and what was the state of the market."),
    make_statement("st-chp8-p209-ruffo-ordered-directly-or-through-agents-with-varying-briefs", 68, 68,
                   "patron_ordered_pictures_directly_or_through_agents_with_variable_instructions",
                   "Haskell says Ruffo wrote to artists directly or through agents, sometimes specifying the subject and sometimes leaving the painter free choice.",
                   "No individual order or letter is identified in this sentence.",
                   subject="cand-2297", obj="cand-7470", mentioned=["cand-2297", "cand-7470"],
                   quote="He then wrote to the artists directly or through his agents to order the pictures he required, sometimes with instructions as to the subject, at others leaving the painter a free hand.",
                   extra={"relation_candidate": True}),
    make_statement("st-chp8-p209-ruffo-guided-by-size-and-expense", 68, 68,
                   "collector_used_size_and_expense_as_two_criteria",
                   "Haskell says Ruffo was guided by size and expense.",
                   "The source gives no threshold or ranking between the two considerations.",
                   subject="cand-2297", obj="cand-2302", mentioned=["cand-2297", "cand-2302"],
                   quote="He was guided by two considerations: size and expense."),
    make_statement("st-chp8-p209-ruffo-symmetry-and-pairs-shaped-composition", 68, 68,
                   "collection_arrangement_and_pairing_preference_affected_composition",
                   "Haskell says Ruffo arranged pictures symmetrically, often sought pairs from one or two artists, and let this concern shape composition.",
                   "The passage gives no installation plan or named pair.",
                   subject="cand-2297", obj="cand-7474", mentioned=["cand-2297", "cand-7474"],
                   quote="His pictures were arranged according to a symmetrical pattern, and he was often anxious to make up pairs—either from the same artist or two different ones, and this concern naturally involved the actual composition."),
    make_statement("st-chp8-p209-guercino-picture-required-to-match-rembrandt-aristotle", 68, 69,
                   "guercino_picture_required_to_match_rembrandt_work",
                   "Haskell says Guercino asked for a rough drawing of Rembrandt's Aristotle contemplating the Bust of Homer, which his own picture was required to match.",
                   "The Guercino picture is unidentified; the source does not give its title or assert that it was the same picture as any other Ruffo commission.",
                   subject="cand-1258", obj="cand-2119", mentioned=["cand-1258", "cand-2117", "cand-2119", "cand-7471", "cand-7472", "cand-7473"],
                   quote="Thus Guercino asked for a rough drawing of Rembrandt’s Aristotle contemplating the Bust of Homer (now in the\nMetropolitan Museum, New York) which his own picture was required to match.",
                   extra={"relation_candidate": True}),
    make_statement("st-chp8-p209-ruffo-seems-to-set-picture-price-in-advance", 69, 69,
                   "collector_seems_to_set_price_in_advance_affecting_picture_structure",
                   "Haskell says Ruffo seems to have decided in advance what price he wished to pay for each work, affecting the structure of pictures painted for him.",
                   "The author marks the claim with 'seems'; the following Guercino negotiation is an example.",
                   subject="cand-2297",
                   quote="In general, Ruffo seems to have decided in advance the price he wished to pay for each work, and this too affected the structure of the pictures painted for him.",
                   extra={"modality": "seems", "relation_candidate": True}),
    make_statement("st-chp8-p209-guercino-rate-and-ruffo-offer-in-scudi", 69, 69,
                   "artist_rate_per_figure_and_patron_offer_prompted_partial_figure_reply",
                   "Haskell reports that Guercino charged 125 ducats per figure; when Ruffo offered 100 scudi for a picture, Guercino said he would paint a little more than half a figure.",
                   "These are different currency units as printed and are not converted. The quoted reply is Guercino's as reported by Haskell; printed 'half a' is corrected from S0 OCR 'halfa'.",
                   subject="cand-1258", obj="cand-7471", mentioned=["cand-1258", "cand-2297", "cand-7471"],
                   quote="As Guercino, for instance, had a fixed rate of 125 ducats for each figure, when Ruffo offered him a hundred scudi for a picture, the artist wrote that he would be prepared to paint ‘a little more than halfa figure’.",
                   extra={"quoted_speaker": "Guercino as reported by Haskell", "relation_candidate": True,
                          "amounts_as_printed": ["125 ducats per figure", "100 scudi"], "ocr_corrections": [ocr_corrections[2]]}),
    make_statement("st-chp8-p209-ruffo-raised-price-guercino-promised-proportionate-picture", 69, 69,
                   "patron_raised_offer_and_artist_promised_proportionate_picture",
                   "Haskell says Ruffo later raised the sum to 100 ducats, and Guercino answered that he would paint something satisfactory in proportion to the amount offered.",
                   "The quoted reply is reported by Haskell; the S0 hyphen in 'offering-me' is retained because it is present in the print.",
                   subject="cand-2297", obj="cand-7471", mentioned=["cand-2297", "cand-1258", "cand-7471"],
                   quote="Later Ruffo raised the sum to 100 ducats, and Guercino answered that he would ‘paint something to your satisfaction proportionate to the amount of money that you are offering-me’.",
                   extra={"quoted_speaker": "Guercino as reported by Haskell", "relation_candidate": True,
                          "amounts_as_printed": ["100 ducats"]}),
    make_statement("st-chp8-p209-first-picture-guided-further-orders-open", 70, 70,
                   "first_picture_from_artist_allowed_patron_to_decide_on_more",
                   "Haskell says that when an artist's first picture reached Ruffo in Messina, Ruffo could decide whether he wanted more from the same artist.",
                   "This sentence is complete; it describes an option and does not say Ruffo always ordered additional works.",
                   subject="cand-2297", obj="cand-1655", mentioned=["cand-2297", "cand-1655"],
                   quote="When the first picture by an artist reached Ruffo in Messina he could decide whether he wanted more by the same man;",
                   extra={"relation_candidate": True}),
    make_statement("st-chp8-p209-gallery-works-as-clues-to-taste", 70, 70,
                   "collection_artist_counts_help_infer_taste_without_letters",
                   "Haskell says that without Ruffo's letters and instructions, the number of works by each painter in his gallery helps provide clues to his taste.",
                   "This is an inference from collection counts, not a direct statement by Ruffo; the sentence precedes his continuing claim about a representative collection.",
                   subject="cand-2297", obj="cand-7468", mentioned=["cand-2297", "cand-7468"],
                   quote="and in the absence of his own letters and instructions, the number of works by each painter in his gallery helps to give us some clues as to his taste.",
                   extra={"relation_candidate": True}),
    make_statement("st-chp8-p209-ruffo-aimed-for-representative-collection-open", 70, 70,
                   "author_said_patron_obviously_aimed_for_representative_collection",
                   "Haskell says Ruffo was obviously trying to amass a representative collection; the sentence continues on p.210.",
                   "The sentence is open at the segment boundary and its continuation must be read before resolving the full claim.",
                   subject="cand-2297", obj="cand-7468", mentioned=["cand-2297", "cand-7468"],
                   quote="Above all he was obviously trying to amass a representative collection",
                   extra={"continuation_status": "open", "continuation_expected_segment_id": NEXT_SEGMENT_ID,
                          "continuation_note": "p.210 segment chp-8:08_CHP-8_sec_i:l72-82 continues the sentence."}),
]

if len({row["statement_id"] for row in body_statements}) != len(body_statements):
    raise SystemExit("duplicate planned statement IDs")
new_statement_ids = {row["statement_id"] for row in body_statements}
if new_statement_ids & existing_statement_ids:
    raise SystemExit("planned statement ID collision")
for row in body_statements:
    q = row["qualifiers"]
    excerpt = "\n".join(source_lines[q["source_line_start"] - 1:q["source_line_end"]])
    if not isinstance(row.get("original_quote"), str) or row["original_quote"] not in excerpt:
        raise SystemExit(f"quote is not reproducible in S0 source: {row['statement_id']}")
    if not (62 <= q["source_line_start"] <= q["source_line_end"] <= 70):
        raise SystemExit(f"statement line range outside segment: {row['statement_id']}")
    mentioned = set(q.get("mentioned_candidate_ids", []))
    if row.get("subject_candidate_id"):
        mentioned.add(row["subject_candidate_id"])
    if row.get("object_candidate_id"):
        mentioned.add(row["object_candidate_id"])
    if not mentioned <= candidate_ids | new_candidate_ids:
        raise SystemExit(f"statement references missing candidate: {row['statement_id']}")

updated_coverage = []
for row in coverage_rows:
    row = dict(row)
    if row["segment_id"] == SEGMENT_ID:
        row.update({
            "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L63-70",
            "note": "P.209 body read against CHP-8.pdf physical p.7. S2 print readings: life, Strada Emmanuela, half a figure; S0 remains unchanged. The representative-collection sentence continues to p.210 L72. Footnote 1 remains pending in 08_CHP-8.md L135.",
        })
    updated_coverage.append(row)

preview = {
    "mode": "dry-run",
    "segment": SEGMENT_ID,
    "new_candidates": len(new_candidates),
    "candidate_ids": [row["candidate_id"] for row in new_candidates],
    "new_mentions": len(new_mentions),
    "new_statements": len(body_statements),
    "coverage": {SEGMENT_ID: "reviewed/partial"},
    "continuation_pending": {"statement_id": "st-chp8-p209-ruffo-aimed-for-representative-collection-open", "next_segment_id": NEXT_SEGMENT_ID},
    "footnotes_pending": ["p.209 note 1 in 08_CHP-8.md L135"],
    "ocr_corrections": ocr_corrections,
    "statement_ids": [row["statement_id"] for row in body_statements],
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write validated tables and create recovery backups")
if not parser.parse_args().apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)

for path in (candidate_path, mention_path, statement_path, coverage_path):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(path, backup)

candidate_rows.extend(new_candidates)
mention_rows.extend(new_mentions)
statement_rows.extend(body_statements)
write_csv_atomic(candidate_path, candidate_fields, candidate_rows)
write_csv_atomic(mention_path, mention_fields, mention_rows)
write_jsonl_atomic(statement_path, statement_rows)
write_csv_atomic(coverage_path, coverage_fields, updated_coverage)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
