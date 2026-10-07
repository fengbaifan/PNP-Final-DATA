"""Controlled Chapter 19 S2 relation-endpoint and composite-statement audit.

Defaults to dry-run. Applying the reviewed plan requires exact source, PDF,
segment, candidate, statement, and open-endpoint preconditions.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE_NAME = "02-sources/02-Markdown/19_CHP-19Appendix.md"
SOURCE_PATH = ROOT / SOURCE_NAME
PDF_PATH = ROOT / "02-sources" / "01-book" / "CHP-19Appendix.pdf"
EXPECTED_SOURCE_SHA256 = "725dc16a2983bec379ce2a8b608542ab3defe348d2b2f2a336632ac4905388f1"
EXPECTED_PDF_SHA256 = "2a1c29e6c2864527482d231a85c4252e55524b436ae4dff5b0d55d9d5a67a9eb"
EXPECTED_SEGMENT_HASHES = {
    "chp-19:19_CHP-19Appendix:l140-155": "17875bbcb383b85ecb7e69438a5c01dcfe1276437ed0ed4f19e7aea2f8f48110",
    "chp-19:19_CHP-19Appendix:l157-183": "efb8708a6b775c8c5cadd9363c5b45b0c646c0ec688228228459b9d8192f6dd9",
    "chp-19:19_CHP-19Appendix:l185-208": "a5cd45b0170686ae85bb3860f458c495375188f1e32d08a8ec4af4b8ccc4f60a",
}
EXPECTED_MAX_CANDIDATE = 11473
EXPECTED_STATEMENT_COUNT = 12234
EXPECTED_MENTION_COUNT = 26837
EXPECTED_RELATION_COUNTS = (2311, 2299, 12)
EXPECTED_OPEN_ENDPOINTS = {
    "st-chp19-p393-smith-1768-letter-continuation": ("cand-2447", None),
    "st-chp19-p393-christies-1776-sales-and-listed-pictures": ("cand-2447", None),
    "st-chp19-p394-memmo-professional-tax-comparisons": ("cand-1642", None),
    "st-chp19-p394-memmo-academies-and-associates": ("cand-1642", None),
    "st-chp19-p395-memmo-patron-saint-and-vasari-reading": ("cand-1642", None),
    "st-chp19-p395-memmo-guild-statutes-and-academy-access": ("cand-1642", None),
}
EXPECTED_AFTER_STATEMENT_COUNT = 12251
EXPECTED_AFTER_MENTION_COUNT = 26845
EXPECTED_AFTER_RELATION_COUNTS = (2323, 2317, 6)
EXPECTED_AFTER_OPEN_BY_CHAPTER = {
    "chp7": 1,
    "chp8": 3,
    "chp14": 1,
    "chp20": 1,
}

CANDIDATE_TYPES = {
    "cand-10807": "work",
    "cand-10812": "archive",
    "cand-2447": "person",
    "cand-10815": "person",
    "cand-10816": "event",
    "cand-10817": "event",
    "cand-10818": "event",
    "cand-10819": "archive",
    "cand-9543": "archive",
    "cand-10820": "work",
    "cand-10821": "work",
    "cand-10822": "work",
    "cand-10823": "work",
    "cand-10824": "work",
    "cand-10825": "work",
    "cand-10827": "person",
    "cand-10828": "person",
    "cand-0498": "person",
    "cand-1430": "person",
    "cand-0094": "person",
    "cand-2154": "person",
    "cand-2149": "person",
    "cand-2879": "person",
    "cand-0575": "person",
    "cand-1577": "person",
    "cand-1401": "person",
    "cand-2527": "person",
    "cand-1033": "person",
    "cand-1368": "person",
    "cand-1422": "place",
    "cand-9400": "institution",
    "cand-2516": "person",
    "cand-1642": "person",
    "cand-9857": "archive",
    "cand-9864": "archive",
    "cand-0005": "institution",
    "cand-10844": "person",
    "cand-10839": "term",
    "cand-10838": "term",
    "cand-9853": "term",
    "cand-9854": "term",
    "cand-9852": "term",
    "cand-10835": "institution",
    "cand-1838": "institution",
    "cand-10840": "term",
    "cand-0581": "person",
    "cand-10842": "term",
    "cand-2702": "person",
    "cand-1699": "person",
    "cand-10847": "term",
    "cand-10848": "term",
}

QUOTE_1776_SALE = (
    "We know that, in accordance with Smith’s desires, these remaining pictures and drawings "
    "were sold in London in 1776 (Christie’s, 22 April and 16 May)."
)
QUOTE_1776_LIST_QUALIFICATION = (
    "The fists are not very satisfactory, and the attributions cannot be treated as definitive."
)
QUOTE_1776_LISTED_PICTURES = (
    "The only eighteenth-century pictures recorded are fourteen views of Venice by Canaletto, "
    "‘two conversations, Mr Murray and family’ by Pietro Longhi, and Amigoni: "
    "‘The portrait of Farinelli and two others’."
)
QUOTE_1789 = (
    "To these we can add a number of pictures said to have come from Smith’s collection in an "
    "anonymous sale (in fact, John Strange) of 10 December 1789. These include a self portrait "
    "by Sebastiano Ricci, landscapes by Marco Ricci and Zuccarelli, and a number of pictures "
    "by Giulio\nCarpioni, Mastelletta, Pietro Liberi, Strozzi, Fetti and Lazzarini."
)
QUOTE_MONTORSOLI_READING = "Leggi la vita del Montorsoli in Vasari—Letta."
P393_SEGMENT_ID = "chp-19:19_CHP-19Appendix:l140-155"

P393_MENTION_ADDITIONS = [
    ("cand-10807", "his collections to the King", "Unspecified group of pictures and drawings Haskell says Smith sold to George III in 1762; no individual works or exact count are supplied here."),
    ("cand-10812", "nota della raccolta Gennari", "The note/list of the Gennari collection that Smith says he returned for clearer copying; the note itself is not reproduced or independently consulted."),
    ("cand-10815", "Le", "Second-person pronoun in Smith's offer to show his purchases; linked to the still-unidentified correspondent described on p.392. This is a coreference, not a named identity."),
    ("cand-10820", "fourteen views of Venice", "Unspecified group of fourteen Venice views in the 1776 lists; individual titles and sale date are not supplied, and the attribution is expressly uncertain."),
    ("cand-10821", "two conversations, Mr Murray and family", "Unspecified group of two conversation pictures as described in the 1776 lists; no titles are given and Mr Murray's identity remains unresolved."),
    ("cand-10822", "The portrait of Farinelli and two others", "Portrait entry as described in the 1776 lists; no full title or identities for the other sitters are supplied."),
    ("cand-10824", "landscapes by Marco Ricci and Zuccarelli", "Unspecified landscape group reported among pictures said to have come from Smith's collection in the 1789 sale; individual works are not identified."),
    ("cand-10825", "a number of pictures by Giulio\nCarpioni, Mastelletta, Pietro Liberi, Strozzi, Fetti and Lazzarini", "Unspecified picture group reported among works said to have come from Smith's collection in the 1789 sale; individual works and surname identities remain unresolved."),
]


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def encode_jsonl(rows):
    return "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)


def encode_csv(rows, fieldnames):
    from io import StringIO

    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def atomic_write(path: Path, text: str):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        f.write(text)
        temporary = Path(f.name)
    temporary.replace(path)


def relation_counts(rows):
    relations = [r for r in rows if r.get("qualifiers", {}).get("relation_candidate") is True]
    complete = sum(bool(r.get("subject_candidate_id") and r.get("object_candidate_id")) for r in relations)
    return len(relations), complete, len(relations) - complete


def require_literal(source_lines, line_start, line_end, quote, label):
    excerpt = "\n".join(source_lines[line_start - 1 : line_end])
    if quote not in excerpt:
        raise SystemExit(f"reviewed quote is not present in source lines for {label}")


def find_unique_span(text, surface, label):
    start = text.find(surface)
    if start < 0 or text.find(surface, start + 1) >= 0:
        raise SystemExit(f"mention span is missing or ambiguous for {label}: {surface!r}")
    return start, start + len(surface)


def remove_mentioned_ids(row, candidate_ids):
    current = row.get("qualifiers", {}).get("mentioned_candidate_ids", [])
    missing = set(candidate_ids) - set(current)
    if missing:
        raise SystemExit(f"expected contextual mention IDs missing for {row['statement_id']}: {sorted(missing)}")
    row["qualifiers"]["mentioned_candidate_ids"] = [value for value in current if value not in set(candidate_ids)]


def set_nonrelation(row, claim, qualification, quote=None, line_start=None, line_end=None, mentions=None):
    q = row["qualifiers"]
    q["relation_candidate"] = False
    q.pop("relation_candidate_note", None)
    q["claim"] = claim
    q["qualification"] = qualification
    if quote is not None:
        row["original_quote"] = quote
    if line_start is not None:
        q["source_line_start"] = line_start
    if line_end is not None:
        q["source_line_end"] = line_end
    if mentions is not None:
        q["mentioned_candidate_ids"] = mentions


def make_relation(
    template,
    statement_id,
    subject_id,
    object_id,
    predicate,
    quote,
    line_start,
    line_end,
    claim,
    qualification,
    mentions,
    speaker,
    text_layer,
    relation_note,
):
    row = copy.deepcopy(template)
    row["statement_id"] = statement_id
    row["subject_candidate_id"] = subject_id
    row["object_candidate_id"] = object_id
    row["predicate"] = predicate
    row["original_quote"] = quote
    row["origin"] = "book"
    row["source_file"] = SOURCE_NAME
    q = row["qualifiers"]
    for key in list(q):
        if key.startswith("footnote_") or key == "ocr_corrections":
            q.pop(key, None)
    q["source_line_start"] = line_start
    q["source_line_end"] = line_end
    q["claim"] = claim
    q["speaker"] = speaker
    q["text_layer"] = text_layer
    q["qualification"] = qualification
    q["mentioned_candidate_ids"] = mentions
    q["relation_candidate"] = True
    q["relation_candidate_note"] = relation_note
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the reviewed changes; default is dry-run")
    parser.add_argument("--show-diff", action="store_true", help="show concise before/after statement fields")
    args = parser.parse_args()

    candidate_path = TABLES / "entity-candidates.csv"
    mention_path = TABLES / "mentions.csv"
    statement_path = TABLES / "book-statements.jsonl"
    segment_path = TABLES / "segments.jsonl"
    if hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest() != EXPECTED_SOURCE_SHA256:
        raise SystemExit("Chapter 19 Appendix source asset changed")
    if hashlib.sha256(PDF_PATH.read_bytes()).hexdigest() != EXPECTED_PDF_SHA256:
        raise SystemExit("Chapter 19 Appendix PDF changed")
    source_lines = SOURCE_PATH.read_text(encoding="utf-8-sig").splitlines()
    segment_by_id = {r["segment_id"]: r for r in read_jsonl(segment_path)}
    for segment_id, expected_hash in EXPECTED_SEGMENT_HASHES.items():
        meta = segment_by_id.get(segment_id)
        if (
            not meta
            or meta.get("source_file") != SOURCE_NAME
            or meta.get("sha256") != expected_hash
            or meta.get("asset_sha256") != EXPECTED_SOURCE_SHA256
        ):
            raise SystemExit(f"source segment manifest changed: {segment_id}")
        excerpt = "\n".join(source_lines[int(meta["line_start"]) - 1 : int(meta["line_end"])])
        if hashlib.sha256(excerpt.encode("utf-8")).hexdigest() != expected_hash:
            raise SystemExit(f"source segment hash mismatch: {segment_id}")
    require_literal(source_lines, 150, 150, QUOTE_1776_SALE, "1776 Christie’s sales")
    require_literal(source_lines, 150, 150, QUOTE_1776_LISTED_PICTURES, "1776 list entries")
    require_literal(source_lines, 150, 151, QUOTE_1789, "1789 anonymous sale entries")
    require_literal(source_lines, 188, 188, QUOTE_MONTORSOLI_READING, "Montorsoli reading mark")

    with candidate_path.open(encoding="utf-8-sig", newline="") as f:
        candidates = list(csv.DictReader(f))
    mention_file_bytes = mention_path.read_bytes()
    mention_has_bom = mention_file_bytes.startswith(b"\xef\xbb\xbf")
    with mention_path.open(encoding="utf-8-sig", newline="") as f:
        mention_reader = csv.DictReader(f)
        mention_fieldnames = mention_reader.fieldnames
        mentions = list(mention_reader)
    statements = read_jsonl(statement_path)
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    statement_by_id = {r["statement_id"]: r for r in statements}
    if len(candidate_by_id) != len(candidates) or len(statement_by_id) != len(statements):
        raise SystemExit("duplicate identifiers in candidate or statement table")
    mention_by_id = {r["mention_id"]: r for r in mentions}
    if len(mention_by_id) != len(mentions):
        raise SystemExit("duplicate identifiers in mention table")
    if max(int(r["candidate_id"].split("-")[-1]) for r in candidates) != EXPECTED_MAX_CANDIDATE:
        raise SystemExit("candidate sequence changed")
    if len(statements) != EXPECTED_STATEMENT_COUNT or relation_counts(statements) != EXPECTED_RELATION_COUNTS:
        raise SystemExit(f"table counts changed: statements={len(statements)}, relations={relation_counts(statements)}")
    if len(mentions) != EXPECTED_MENTION_COUNT or "m-chp19-p393-054" not in mention_by_id:
        raise SystemExit(f"mention table precondition changed: mentions={len(mentions)}")

    open_ids = {
        r["statement_id"]: (r.get("subject_candidate_id"), r.get("object_candidate_id"))
        for r in statements
        if r["statement_id"].startswith("st-chp19-")
        and r.get("qualifiers", {}).get("relation_candidate") is True
        and (not r.get("subject_candidate_id") or not r.get("object_candidate_id"))
    }
    if open_ids != EXPECTED_OPEN_ENDPOINTS:
        raise SystemExit(f"Chapter 19 open endpoint set changed: {open_ids}")

    for candidate_id, expected_type in CANDIDATE_TYPES.items():
        if candidate_by_id.get(candidate_id, {}).get("suggested_type") != expected_type:
            raise SystemExit(f"candidate type precondition changed: {candidate_id}")
    smith_row = statement_by_id["st-chp19-p393-smith-1768-letter-continuation"]
    christies_row = statement_by_id["st-chp19-p393-christies-1776-sales-and-listed-pictures"]
    anonymous_row = statement_by_id["st-chp19-p393-1789-anonymous-sale-and-attributed-groups"]
    reading_row = statement_by_id["st-chp19-p395-memmo-patron-saint-and-vasari-reading"]
    if "farò vedere" not in smith_row["original_quote"] or "Le" not in smith_row["original_quote"]:
        raise SystemExit("Smith letter continuation no longer contains the addressee offer")
    if QUOTE_1776_SALE not in christies_row["original_quote"] or QUOTE_1776_LISTED_PICTURES not in christies_row["original_quote"]:
        raise SystemExit("1776 sales/list statement changed")
    if QUOTE_1789 not in anonymous_row["original_quote"] or anonymous_row.get("object_candidate_id") != "cand-10818":
        raise SystemExit("1789 anonymous-sale statement changed")
    if QUOTE_MONTORSOLI_READING not in reading_row["original_quote"]:
        raise SystemExit("Memmo reading-status statement changed")

    segment_mentions = {}
    for row in mentions:
        segment_mentions.setdefault(row.get("segment_id"), set()).add(row.get("candidate_id"))

    p393_excerpt = "\n".join(source_lines[139:155])
    for row in mentions:
        if row.get("segment_id") != P393_SEGMENT_ID:
            continue
        start, end = int(row["start_char"]), int(row["end_char"])
        if p393_excerpt[start:end] != row["surface_form"]:
            raise SystemExit(f"existing Chapter 19 p.393 mention span changed: {row['mention_id']}")
    mention_additions = []
    for index, (candidate_id, surface, note) in enumerate(P393_MENTION_ADDITIONS, start=55):
        mention_id = f"m-chp19-p393-{index:03d}"
        if mention_id in mention_by_id:
            raise SystemExit(f"planned mention ID already exists: {mention_id}")
        if candidate_id not in candidate_by_id:
            raise SystemExit(f"missing candidate for planned mention: {mention_id} -> {candidate_id}")
        if candidate_id == "cand-10815":
            phrase_start, _ = find_unique_span(p393_excerpt, "siccome Le farò vedere", mention_id)
            start = phrase_start + len("siccome ")
            end = start + len("Le")
        else:
            start, end = find_unique_span(p393_excerpt, surface, mention_id)
        if p393_excerpt[start:end] != surface:
            raise SystemExit(f"planned mention span does not match source: {mention_id}")
        mention_additions.append({
            "mention_id": mention_id,
            "segment_id": P393_SEGMENT_ID,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(end),
            "note": note,
        })
    mentions_after = mentions + mention_additions
    for row in mention_additions:
        segment_mentions.setdefault(row["segment_id"], set()).add(row["candidate_id"])
    if len(mentions_after) != EXPECTED_AFTER_MENTION_COUNT:
        raise SystemExit(f"planned mention count differs: {len(mentions_after)}")

    before = copy.deepcopy(statement_by_id)
    for statement_id in EXPECTED_OPEN_ENDPOINTS:
        if not statement_by_id.get(statement_id):
            raise SystemExit(f"open statement missing: {statement_id}")

    # Smith's purchases remain an assertion about unnamed objects; the offer to show
    # them is a separate, explicitly addressed relation to the unidentified recipient.
    smith_row = statement_by_id["st-chp19-p393-smith-1768-letter-continuation"]
    remove_mentioned_ids(smith_row, ["cand-10811"])
    smith_row["object_candidate_id"] = "cand-10815"
    smith_row["predicate"] = "smith_reported_purchases_and_offered_to_show_pictures_and_prints_to_correspondent"
    smith_row["qualifiers"]["claim"] = (
        "Smith says buyers were fewer, pictures and prints were often offered, he had bought several of each, "
        "and he might show them to the correspondent if they met again."
    )
    smith_row["qualifiers"]["qualification"] = (
        "The second-person Le addresses the unidentified correspondent cand-10815, known only from Haskell's "
        "description of the letter as addressed to an unknown person in Bologna. The purchase does not establish "
        "that the pictures and prints were acquired for Smith's own collection; the proposed showing is future and conditional."
    )
    smith_row["qualifiers"]["relation_candidate_note"] = (
        "The relation endpoint is the explicitly addressed correspondent; the pictures and prints remain an unnamed group, not endpoints."
    )

    # The sales sentence, list caveat, and list entries have different semantic roles.
    christies_row = statement_by_id["st-chp19-p393-christies-1776-sales-and-listed-pictures"]
    quote_1776_summary = f"{QUOTE_1776_SALE} {QUOTE_1776_LIST_QUALIFICATION}"
    set_nonrelation(
        christies_row,
        "Haskell says Smith's remaining pictures and drawings were sold in London at Christie's on 22 April and 16 May 1776, and warns that the lists are unsatisfactory and their attributions are not definitive.",
        "The source does not allocate any named picture group to either date. The catalogues were not independently consulted, and the fourteen Canaletto views are not identified with the fourteen further pictures in the 16 May catalogue cited at p.304 note 7.",
        quote=quote_1776_summary,
        mentions=["cand-2447", "cand-1422", "cand-9400", "cand-10816", "cand-10817"],
    )

    # The following references are contextual carryovers from adjacent pages or
    # chapters, not local p.393–395 mentions. Preserve their identity questions
    # for S3 rather than presenting them as directly mentioned on these pages.
    remove_mentioned_ids(
        statement_by_id["st-chp19-p393-smith-gennari-note-and-letter-signature"],
        ["cand-10811", "cand-10814"],
    )
    remove_mentioned_ids(
        statement_by_id["st-chp19-p394-memmo-c-veneziano-exemption-query"],
        ["cand-0498"],
    )
    for statement_id in [
        "st-chp19-p395-manfrin-edwards-letter-source",
        "st-chp19-p395-manfrin-selection-criteria-and-experts",
        "st-chp19-p395-manfrin-confidential-judgment-condition",
        "st-chp19-p395-manfrin-letter-closure-and-signature",
    ]:
        remove_mentioned_ids(statement_by_id[statement_id], ["cand-1515"])

    # Queries and proposed research actions in Memmo's notes are not completed
    # institutional or personal relations.
    set_nonrelation(
        statement_by_id["st-chp19-p394-memmo-professional-tax-comparisons"],
        "Memmo's note records one unverified statement that music teachers and engravers were not taxed, then asks about architects' and painters' taxation in several cities.",
        "The transcribed note is the source for the reported status; its questions about architects and painters have no answers here and do not establish city tax rules.",
    )
    set_nonrelation(
        statement_by_id["st-chp19-p394-memmo-academies-and-associates"],
        "Memmo's note asks about a Naples painting academy, the new Academy of Parma, women painters' tax status, and possible selection of foreign associated academicians.",
        "These are research queries and a proposed selection topic, not findings or appointments. The Parma reference is retained as written; the existence and identity of the Naples academy and the status of the unnamed foreign professors are not established by these queries.",
    )
    reading_row = statement_by_id["st-chp19-p395-memmo-patron-saint-and-vasari-reading"]
    quote_patron_queries = "\n".join(source_lines[185:187])
    set_nonrelation(
        reading_row,
        "Memmo's note asks which saint protects the abbreviated n.A. and directs research into privileges granted by Duke Cosimo to painters; it also marks an unspecified Vasari text as read.",
        "The queries do not identify the Academy behind n.A. or establish any privilege. ‘Vasari lett.’ does not name a work or identify who read it; only the separate line about the Life of Montorsoli names a specific text.",
        quote=quote_patron_queries,
        line_start=186,
        line_end=187,
        mentions=["cand-1642", "cand-9857", "cand-0005", "cand-10844", "cand-10839", "cand-2702"],
    )
    set_nonrelation(
        statement_by_id["st-chp19-p395-memmo-guild-statutes-and-academy-access"],
        "Memmo's note proposes researching trade statutes and asks how Academy youths might be granted access to schools or communities.",
        "No particular guild, school, or community is identified, and the proposal does not say that privileges were enacted or access granted.",
    )

    # Narrow the existing 1789 event statement to its own source passage. Keep
    # reported provenance explicitly qualified and split listed artist relations below.
    anonymous_row = statement_by_id["st-chp19-p393-1789-anonymous-sale-and-attributed-groups"]
    anonymous_row["predicate"] = "haskell_reported_pictures_said_to_come_from_smiths_collection_in_1789_sale"
    anonymous_row["original_quote"] = QUOTE_1789
    aq = anonymous_row["qualifiers"]
    aq["source_line_start"] = 150
    aq["source_line_end"] = 151
    aq["claim"] = (
        "Haskell reports pictures said to have come from Smith's collection in an anonymous sale of 10 December 1789, "
        "which he identifies parenthetically with John Strange; he lists a Sebastiano Ricci self-portrait, landscapes "
        "by Marco Ricci and Zuccarelli, and pictures by six further artists."
    )
    aq["qualification"] = (
        "‘Said to have come from Smith's collection’ is reported provenance, not verified ownership. The sale catalogue "
        "and attributions were not independently checked. Haskell's parenthetical identification with John Strange is retained as his report."
    )
    aq["mentioned_candidate_ids"] = [
        "cand-2447", "cand-10818", "cand-2516", "cand-10823", "cand-2154", "cand-10824",
        "cand-2149", "cand-2879", "cand-10825", "cand-0575", "cand-1577", "cand-1401",
        "cand-2527", "cand-1033", "cand-1368",
    ]

    new_relations = []

    def add(*args, template_id, **kwargs):
        new_relations.append(make_relation(before[template_id], *args, **kwargs))

    # The two sale dates are separate event candidates; neither receives an
    # individual lot assignment from Haskell's passage.
    sale_qualification = (
        "Haskell names this as one of two 1776 sales of Smith's remaining pictures and drawings, conducted in accordance "
        "with Smith's wishes. No lot or named picture group is allocated to this date, and this does not claim that Smith "
        "personally acted as the seller; the catalogue was not consulted."
    )
    for statement_id, event_id, date in [
        ("st-chp19-p393-remaining-pictures-sale-1776-04-22", "cand-10816", "22 April 1776"),
        ("st-chp19-p393-remaining-pictures-sale-1776-05-16", "cand-10817", "16 May 1776"),
    ]:
        add(
            statement_id, event_id, "cand-2447", "was_one_of_two_sales_of_smiths_remaining_pictures_and_drawings",
            QUOTE_1776_SALE, 150, 150,
            f"Haskell identifies the {date} Christie's event as one of the two 1776 sales of Smith's remaining pictures and drawings.",
            sale_qualification, [event_id, "cand-2447"], "Haskell", "authorial report of sale events",
            "Event-to-person collection provenance candidate; not a claim that Smith personally sold the works.",
            template_id="st-chp19-p393-christies-1776-sales-and-listed-pictures",
        )

    attribution_specs = [
        (
            "st-chp19-p393-1776-canaletto-fourteen-views-attribution", "cand-10820", "cand-0498",
            "sale_list_attributed_fourteen_venice_views_to_canaletto", "fourteen views of Venice by Canaletto",
            "Haskell reports fourteen Venice views in the 1776 sale lists as by Canaletto.",
            ["cand-10820", "cand-0498"],
        ),
        (
            "st-chp19-p393-1776-longhi-two-conversations-attribution", "cand-10821", "cand-1430",
            "sale_list_attributed_two_conversations_to_pietro_longhi", "‘two conversations, Mr Murray and family’ by Pietro Longhi",
            "Haskell reports two conversations described as ‘Mr Murray and family’ in the 1776 sale lists as by Pietro Longhi.",
            ["cand-10821", "cand-1430"],
        ),
        (
            "st-chp19-p393-1776-amigoni-farinelli-portrait-attribution", "cand-10822", "cand-0094",
            "sale_list_attributed_farinelli_portrait_entry_to_amigoni", "Amigoni: ‘The portrait of Farinelli and two others’",
            "Haskell reports a sale-list portrait entry for Farinelli and two others as by Amigoni.",
            ["cand-10822", "cand-0094"],
        ),
    ]
    for statement_id, work_id, artist_id, predicate, quote, claim, mentions_for_row in attribution_specs:
        add(
            statement_id, work_id, artist_id, predicate, quote, 150, 150, claim,
            "Haskell says the 1776 lists and their attributions are unsatisfactory and not definitive; the catalogues were not consulted, and this passage does not assign the entry to either sale date.",
            mentions_for_row, "Haskell", "reported auction-list attribution",
            "Uncertain sale-list creator attribution; retain as an S2 candidate, not a formal authorship edge.",
            template_id="st-chp19-p393-christies-1776-sales-and-listed-pictures",
        )

    sitter_specs = [
        (
            "st-chp19-p393-1776-longhi-conversations-murray-sitter", "cand-10821", "cand-10827",
            "sale_list_described_longhi_conversations_as_murray_and_family", "‘two conversations, Mr Murray and family’",
            "Haskell reports that the sale-list description for two Pietro Longhi conversations names Mr Murray and family.",
            ["cand-10821", "cand-10827"],
            "The list gives only ‘Mr Murray’; his identity is unresolved and is not merged with the indexed John Murray candidate. Family members are unnamed, and the catalogue was not consulted.",
        ),
        (
            "st-chp19-p393-1776-amigoni-portrait-farinelli-sitter", "cand-10822", "cand-10828",
            "sale_list_named_farinelli_as_one_of_portrait_sitters", "‘The portrait of Farinelli and two others’",
            "Haskell reports that the Amigoni sale-list portrait entry names Farinelli and two other sitters.",
            ["cand-10822", "cand-10828"],
            "The entry identifies Farinelli only by the name printed in Haskell's account; the other sitters are unnamed and the catalogue was not consulted.",
        ),
    ]
    for statement_id, work_id, sitter_id, predicate, quote, claim, mentions_for_row, qualification in sitter_specs:
        add(
            statement_id, work_id, sitter_id, predicate, quote, 150, 150, claim, qualification,
            mentions_for_row, "Haskell", "reported auction-list subject description",
            "Sale-list sitter description; not an independently verified identity or portrait attribution.",
            template_id="st-chp19-p393-christies-1776-sales-and-listed-pictures",
        )

    # Memmo's source sheet marks one named text as read. The endpoints are the
    # note sheet and the text, avoiding an unsupported assumption about reader/date.
    add(
        "st-chp19-p395-memmo-note-marks-life-of-montorsoli-read", "cand-9857", "cand-9864",
        "memmos_note_marked_vasaris_life_of_montorsoli_as_read", QUOTE_MONTORSOLI_READING, 188, 188,
        "The preparatory sheet attributed to Memmo directs the reader to the Life of Montorsoli in Vasari and marks it ‘Letta’ (read).",
        "The sheet is identified by Haskell as Memmo's but was not independently consulted. This records the sheet's reading mark, not independent proof of who read the work or when; the specific edition is unidentified.",
        ["cand-1699", "cand-2702", "cand-9864"], "Andrea Memmo's note as transcribed by Haskell", "transcribed research instruction and reading mark",
        "The archive sheet marks the text as read; the relation records the note's content, not an independently verified reader or date.",
        template_id="st-chp19-p395-memmo-patron-saint-and-vasari-reading",
    )

    # The 1789 sale paragraph contains explicit group-to-artist attributions.
    # Preserve the catalog's reported provenance and unresolved surname mapping.
    group_1789 = [
        ("st-chp19-p393-1789-ricci-self-portrait-attribution", "cand-10823", "cand-2154", "sale_list_attributed_self_portrait_to_sebastiano_ricci", "a self portrait by Sebastiano Ricci", "Haskell lists a self-portrait by Sebastiano Ricci among the pictures said to come from Smith's collection in the 1789 sale."),
        ("st-chp19-p393-1789-marco-ricci-landscapes-attribution", "cand-10824", "cand-2149", "sale_list_attributed_landscapes_to_marco_ricci", "landscapes by Marco Ricci", "Haskell lists landscapes by Marco Ricci among the pictures said to come from Smith's collection in the 1789 sale."),
        ("st-chp19-p393-1789-zuccarelli-landscapes-attribution", "cand-10824", "cand-2879", "sale_list_attributed_landscapes_to_zuccarelli", "landscapes by Marco Ricci and Zuccarelli", "Haskell lists landscapes by Zuccarelli among the pictures said to come from Smith's collection in the 1789 sale."),
        ("st-chp19-p393-1789-carpioni-pictures-attribution", "cand-10825", "cand-0575", "sale_list_attributed_pictures_to_giulio_carpioni", "pictures by Giulio\nCarpioni", "Haskell lists pictures by Giulio Carpioni among the pictures said to come from Smith's collection in the 1789 sale."),
        ("st-chp19-p393-1789-mastelletta-pictures-attribution", "cand-10825", "cand-1577", "sale_list_attributed_pictures_to_mastelletta", "Mastelletta", "Haskell lists pictures by Mastelletta among the pictures said to come from Smith's collection in the 1789 sale."),
        ("st-chp19-p393-1789-liberi-pictures-attribution", "cand-10825", "cand-1401", "sale_list_attributed_pictures_to_pietro_liberi", "Pietro Liberi", "Haskell lists pictures by Pietro Liberi among the pictures said to come from Smith's collection in the 1789 sale."),
        ("st-chp19-p393-1789-strozzi-pictures-attribution", "cand-10825", "cand-2527", "sale_list_attributed_pictures_to_strozzi", "Strozzi", "Haskell lists pictures by Strozzi among the pictures said to come from Smith's collection in the 1789 sale."),
        ("st-chp19-p393-1789-fetti-pictures-attribution", "cand-10825", "cand-1033", "sale_list_attributed_pictures_to_fetti_candidate", "Fetti", "Haskell lists pictures by an artist named Fetti among the pictures said to come from Smith's collection in the 1789 sale."),
        ("st-chp19-p393-1789-lazzarini-pictures-attribution", "cand-10825", "cand-1368", "sale_list_attributed_pictures_to_lazzarini", "Lazzarini", "Haskell lists pictures by Lazzarini among the pictures said to come from Smith's collection in the 1789 sale."),
    ]
    for statement_id, work_id, artist_id, predicate, quote, claim in group_1789:
        identity_note = (
            "The source spells the surname Fetti while the index candidate is Feti, Domenico; this local candidate mapping is provisional for S3. "
            if artist_id == "cand-1033" else ""
        )
        add(
            statement_id, work_id, artist_id, predicate, quote, 150, 151, claim,
            "Haskell reports these works as entries said to have come from Smith's collection in the anonymous 10 December 1789 sale, which he identifies with John Strange. The catalogue was not consulted; individual works, attributions, and same-name identities remain unverified. " + identity_note,
            [work_id, artist_id], "Haskell", "reported 1789 sale-list attribution",
            "Reported, unverified sale-list attribution; retain as an S2 candidate, not a formal creator relation.",
            template_id="st-chp19-p393-1789-anonymous-sale-and-attributed-groups",
        )

    planned_ids = [row["statement_id"] for row in new_relations]
    if len(planned_ids) != len(set(planned_ids)):
        raise SystemExit("duplicate statement IDs in the planned additions")
    for statement_id in planned_ids:
        if statement_id in statement_by_id:
            raise SystemExit(f"planned statement ID already exists: {statement_id}")

    for row in new_relations:
        quote = row["original_quote"]
        q = row["qualifiers"]
        require_literal(source_lines, q["source_line_start"], q["source_line_end"], quote, row["statement_id"])
        for candidate_id in q.get("mentioned_candidate_ids", []):
            if candidate_id not in candidate_by_id:
                raise SystemExit(f"missing mentioned candidate: {row['statement_id']} -> {candidate_id}")
            if candidate_id not in segment_mentions.get(row["segment_id"], set()):
                raise SystemExit(f"candidate is not mentioned in source segment: {row['statement_id']} -> {candidate_id}")
        for candidate_id in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if not candidate_id or candidate_id not in candidate_by_id:
                raise SystemExit(f"missing relation endpoint: {row['statement_id']} -> {candidate_id}")

    statements.extend(new_relations)
    statement_by_id.update({row["statement_id"]: row for row in new_relations})
    remaining_open = {
        row["statement_id"]
        for row in statements
        if row["statement_id"].startswith("st-chp19-")
        and row.get("qualifiers", {}).get("relation_candidate") is True
        and (not row.get("subject_candidate_id") or not row.get("object_candidate_id"))
    }
    if remaining_open:
        raise SystemExit(f"Chapter 19 still has unresolved relation endpoints: {sorted(remaining_open)}")
    open_by_chapter = {}
    all_relations = [r for r in statements if r.get("qualifiers", {}).get("relation_candidate") is True]
    for row in all_relations:
        if not row.get("subject_candidate_id") or not row.get("object_candidate_id"):
            chapter = row["statement_id"].split("-")[1]
            open_by_chapter[chapter] = open_by_chapter.get(chapter, 0) + 1
    if len(statements) != EXPECTED_AFTER_STATEMENT_COUNT or relation_counts(statements) != EXPECTED_AFTER_RELATION_COUNTS:
        raise SystemExit(f"planned aggregate counts differ: statements={len(statements)}, relations={relation_counts(statements)}")
    if open_by_chapter != EXPECTED_AFTER_OPEN_BY_CHAPTER:
        raise SystemExit(f"planned open-endpoint distribution differs: {open_by_chapter}")
    for row in statements:
        for candidate_id in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if candidate_id and candidate_id not in candidate_by_id:
                raise SystemExit(f"missing statement endpoint candidate: {row['statement_id']} -> {candidate_id}")
        for candidate_id in row.get("qualifiers", {}).get("mentioned_candidate_ids", []):
            if candidate_id not in candidate_by_id:
                raise SystemExit(f"missing mentioned candidate: {row['statement_id']} -> {candidate_id}")
    stale_notes = [
        row["statement_id"] for row in statements
        if row.get("qualifiers", {}).get("relation_candidate") is False
        and row.get("qualifiers", {}).get("relation_candidate_note")
    ]
    if stale_notes:
        raise SystemExit(f"nonrelation rows retain relation-candidate notes: {stale_notes[:10]}")

    changed_ids = sorted(set(EXPECTED_OPEN_ENDPOINTS) | {
        "st-chp19-p393-smith-gennari-note-and-letter-signature",
        "st-chp19-p393-1789-anonymous-sale-and-attributed-groups",
        "st-chp19-p394-memmo-c-veneziano-exemption-query",
        "st-chp19-p395-manfrin-edwards-letter-source",
        "st-chp19-p395-manfrin-selection-criteria-and-experts",
        "st-chp19-p395-manfrin-confidential-judgment-condition",
        "st-chp19-p395-manfrin-letter-closure-and-signature",
    })
    print("Chapter 19 S2 relation-endpoint and composite-statement audit plan")
    print("six initial open items: Smith-to-correspondent relation completed; four query/status composites retained as assertions; 1776 list summary separated")
    print("1776: two dated sale-event candidates, three uncertain artist attributions, and two catalogued sitter descriptions")
    print("1789: nine reported work-to-artist candidates split from the sale-provenance statement; Fetti/Feti identity remains for S3")
    print("Memmo's specific Montorsoli reading mark is linked from the archival note sheet to Vasari's Life; reader and date are not independently verified")
    print(f"new statements: {len(new_relations)}; candidate table unchanged; p.393 mention links added: {len(mention_additions)}")
    print(f"statements: {EXPECTED_STATEMENT_COUNT} -> {len(statements)}")
    print(f"mentions: {EXPECTED_MENTION_COUNT} -> {len(mentions_after)}")
    print(f"relation candidates (total/complete/open): {EXPECTED_RELATION_COUNTS} -> {relation_counts(statements)}")
    print(f"open endpoint distribution: {open_by_chapter}")
    if args.show_diff:
        for statement_id in changed_ids:
            old = before[statement_id]
            new = statement_by_id[statement_id]
            for label, row in (("BEFORE", old), ("AFTER", new)):
                q = row.get("qualifiers", {})
                print(f"{label} {statement_id}: {row.get('subject_candidate_id') or '∅'} → {row.get('object_candidate_id') or '∅'}; relation={q.get('relation_candidate')}; predicate={row.get('predicate')}; mentions={q.get('mentioned_candidate_ids', [])}; quote={row.get('original_quote','')[:180]!r}")
        for row in new_relations:
            print(f"ADD {row['statement_id']}: {row['subject_candidate_id']} → {row['object_candidate_id']}; {row['predicate']}")
        for row in mention_additions:
            print(f"MENTION {row['mention_id']}: {row['candidate_id']} {row['surface_form']!r} [{row['start_char']}:{row['end_char']}]")
    if not args.apply:
        print("DRY-RUN only; inspect this plan, then pass --apply to write.")
        return

    backup_dir = Path(tempfile.mkdtemp(prefix="pnp-chp19-s2-relation-audit-"))
    statement_backup = backup_dir / statement_path.name
    mention_backup = backup_dir / mention_path.name
    shutil.copy2(statement_path, statement_backup)
    shutil.copy2(mention_path, mention_backup)
    try:
        atomic_write(statement_path, encode_jsonl(statements))
        mention_text = encode_csv(mentions_after, mention_fieldnames)
        if mention_has_bom:
            mention_text = "\ufeff" + mention_text
        atomic_write(mention_path, mention_text)

        written = read_jsonl(statement_path)
        with mention_path.open(encoding="utf-8-sig", newline="") as f:
            written_mentions = list(csv.DictReader(f))
        if len(written) != EXPECTED_AFTER_STATEMENT_COUNT or relation_counts(written) != EXPECTED_AFTER_RELATION_COUNTS:
            raise RuntimeError("post-write statement counts differ")
        if len(written_mentions) != EXPECTED_AFTER_MENTION_COUNT:
            raise RuntimeError("post-write mention count differs")
        written_by_id = {row["statement_id"]: row for row in written}
        written_mention_by_id = {row["mention_id"]: row for row in written_mentions}
        if len(written_mention_by_id) != len(written_mentions):
            raise RuntimeError("post-write duplicate mention IDs")
        chapter19_open = [
            row["statement_id"] for row in written
            if row["statement_id"].startswith("st-chp19-")
            and row.get("qualifiers", {}).get("relation_candidate") is True
            and (not row.get("subject_candidate_id") or not row.get("object_candidate_id"))
        ]
        if chapter19_open or any(statement_id not in written_by_id for statement_id in planned_ids):
            raise RuntimeError("post-write Chapter 19 endpoint verification failed")
        for row in mention_additions:
            written_mention = written_mention_by_id.get(row["mention_id"])
            if written_mention != row:
                raise RuntimeError(f"post-write mention row differs: {row['mention_id']}")
            start, end = int(written_mention["start_char"]), int(written_mention["end_char"])
            if p393_excerpt[start:end] != written_mention["surface_form"]:
                raise RuntimeError(f"post-write mention span does not match source: {row['mention_id']}")
        for row in written:
            for candidate_id in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
                if candidate_id and candidate_id not in candidate_by_id:
                    raise RuntimeError(f"post-write dangling endpoint: {row['statement_id']} -> {candidate_id}")
            for candidate_id in row.get("qualifiers", {}).get("mentioned_candidate_ids", []):
                if candidate_id not in candidate_by_id:
                    raise RuntimeError(f"post-write dangling mention candidate: {row['statement_id']} -> {candidate_id}")
    except Exception as error:
        shutil.copy2(statement_backup, statement_path)
        shutil.copy2(mention_backup, mention_path)
        raise SystemExit(f"write verification failed; original tables restored; recovery copies: {backup_dir}; error: {error}")
    print(f"APPLIED; recovery copies: {backup_dir}")


if __name__ == "__main__":
    main()
