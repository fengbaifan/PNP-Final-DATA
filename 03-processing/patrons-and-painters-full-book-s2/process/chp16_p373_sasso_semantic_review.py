"""Controlled semantic refinement for printed p.373 and notes 1-2."""
import argparse
import csv
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENT_TABLE = TABLES / "book-statements.jsonl"
MENTION_TABLE = TABLES / "mentions.csv"
CANDIDATE_TABLE = TABLES / "entity-candidates.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "16_CHP-16_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-16.pdf"
BODY = "chp-16:16_CHP-16_intro:l3-14"
NOTES = "chp-16:16_CHP-16_intro:l69-89"
STATEMENT_SHA = "20d1fd6bffe112300f5da41b843b208053ad411812d221ae18a347cb20f60c77"
MENTION_SHA = "25af9000c98f4ab8d55b2aaa33901f6d8257ad4cca64184be4aaae1b584392ca"
CANDIDATE_SHA = "524924330cd382dfe3be976b07e87edfe313a34051c7dbdf8ec6aac07d5716e3"
SOURCE_SHA = "ee8516e7868b0036a753da731e10a7e201faafa45314615b45ae024c6c7507ff"
PDF_SHA = "6bfb3e331f0ac2421d31279f97b08b17486f0e2c32451a10a6798cf31424af5f"
BACKUP_SUFFIX = ".bak-s2-chp16-p373-semantic-review-20261009"
NO_CHANGE = object()

OLD_IDS = {
    "st-chp16-p373-patronage-tastes-and-venetian-tradition",
    "st-chp16-p373-dealers-perceived-as-agents-and-collectors",
    "st-chp16-p373-sasso-dealing-collection-and-writing",
    "st-chp16-p373-sasso-survived-republic-and-died-1803",
    "st-chp16-p373-sasso-born-to-poor-parents-and-studied-painting",
    "st-chp16-p373-sasso-contacted-british-residency-in-1774",
    "st-chp16-p373-strange-new-occupant-of-residency",
    "st-chp16-p373-strange-and-sasso-corresponded-nearly-twenty-years",
    "st-chp16-p373-strange-and-sasso-shared-complaints-and-business",
    "st-chp16-p373-strange-employed-sasso-to-buy-pictures-partial",
    "st-chp16-p373-note1-sasso-biography-citations",
    "st-chp16-p373-note1-longhi-portrait-reference",
    "st-chp16-p373-note2-strange-sasso-letters-in-epistolario",
    "st-chp16-p373-note2-mauroner-quotes-letters",
    "st-chp16-p373-note2-sasso-replies-mostly-missing",
    "st-chp16-p373-note2-four-sasso-letters-british-museum",
}
RENAMES = {
    "st-chp16-p373-patronage-tastes-and-venetian-tradition":
        "st-chp16-p373-prominent-patrons-influenced-by-lodoli-algarotti",
    "st-chp16-p373-sasso-dealing-collection-and-writing":
        "st-chp16-p373-sasso-kept-small-private-collection",
    "st-chp16-p373-sasso-survived-republic-and-died-1803":
        "st-chp16-p373-sasso-survived-the-republic",
    "st-chp16-p373-sasso-born-to-poor-parents-and-studied-painting":
        "st-chp16-p373-sasso-born-to-poor-parents",
    "st-chp16-p373-strange-and-sasso-corresponded-nearly-twenty-years":
        "st-chp16-p373-sasso-strange-corresponded-nearly-twenty-years",
    "st-chp16-p373-strange-and-sasso-shared-complaints-and-business":
        "st-chp16-p373-sasso-strange-shared-social-complaints",
    "st-chp16-p373-strange-employed-sasso-to-buy-pictures-partial":
        "st-chp16-p373-strange-employed-sasso-to-buy-pictures",
    "st-chp16-p373-note1-longhi-portrait-reference":
        "st-chp16-p373-note1-longhi-painted-sasso-portrait",
}
NEW_CANDIDATES = {"cand-11543", "cand-11544", "cand-11545"}
NEW_MENTIONS = {
    "m-chp16-p373-sasso-review-0001",
    "m-chp16-p373-sasso-review-0002",
    "m-chp16-p373-sasso-review-0003",
    "m-chp16-p373-sasso-review-0004",
}
NEW_STATEMENTS = {
    "st-chp16-p373-patrons-promoted-functional-or-classical-taste",
    "st-chp16-p373-patron-taste-distinct-from-venetian-tradition",
    "st-chp16-p373-venetian-tradition-last-great-master-guardi",
    "st-chp16-p373-venetian-tradition-carried-by-lower-status-men",
    "st-chp16-p373-lower-status-men-and-their-painting-attracted-little-attention",
    "st-chp16-p373-dealers-built-small-collections",
    "st-chp16-p373-collections-reflect-distinctive-taste-and-appeal",
    "st-chp16-p373-sasso-bought-and-sold-pictures",
    "st-chp16-p373-sasso-dealt-with-british-agents",
    "st-chp16-p373-sasso-corresponded-with-friends-and-dealers",
    "st-chp16-p373-sasso-produced-occasional-pamphlets",
    "st-chp16-p373-sasso-amassed-facts",
    "st-chp16-p373-sasso-planned-unfinished-book-on-venetian-painting",
    "st-chp16-p373-sasso-life-typical-of-contemporary-figures",
    "st-chp16-p373-sasso-died-in-1803",
    "st-chp16-p373-sasso-studied-painting-briefly",
    "st-chp16-p373-sasso-strange-on-excellent-terms",
    "st-chp16-p373-sasso-strange-saw-each-other",
    "st-chp16-p373-sasso-strange-condoled-losses-and-illnesses",
    "st-chp16-p373-sasso-strange-exchanged-gossip",
    "st-chp16-p373-sasso-strange-did-lucrative-business",
    "st-chp16-p373-note1-portrait-depicts-sasso",
    "st-chp16-p373-note1-bollettino-portrait-citation",
    "st-chp16-p373-note2-epistolario-at-correr",
    "st-chp16-p373-note2-correr-in-venice",
    "st-chp16-p373-note2-sasso-wrote-four-letters-to-strange",
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed p.373 data")
args = parser.parse_args()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


for path, expected, label in (
    (STATEMENT_TABLE, STATEMENT_SHA, "statement table"),
    (MENTION_TABLE, MENTION_SHA, "mention table"),
    (CANDIDATE_TABLE, CANDIDATE_SHA, "candidate table"),
    (SOURCE, SOURCE_SHA, "chapter 16 source"),
    (PDF, PDF_SHA, "registered CHP-16 PDF"),
):
    if sha(path) != expected:
        raise SystemExit(f"{label} changed since this review's dry-run baseline")


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(handle.name)
    temporary.replace(path)


source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
body_text = "\n".join(source_lines[2:14])
note_text = "\n".join(source_lines[68:89])


def quote(start_line, end_line, first, last):
    text = "\n".join(source_lines[start_line - 1:end_line])
    start = text.find(first)
    end = text.rfind(last)
    if start < 0 or end < start:
        raise SystemExit(f"source quote changed at L{start_line}-L{end_line}: {first!r} ... {last!r}")
    end += len(last)
    return text[start:end]


candidate_fields, candidates = read_csv(CANDIDATE_TABLE)
mention_fields, mentions = read_csv(MENTION_TABLE)
statements = [json.loads(line) for line in STATEMENT_TABLE.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
candidate_by_id = {row["candidate_id"]: row for row in candidates}
mention_by_id = {row["mention_id"]: row for row in mentions}
statement_by_id = {row["statement_id"]: row for row in statements}
actual_old = {row["statement_id"] for row in statements if row.get("statement_id", "").startswith("st-chp16-p373-")}
if actual_old != OLD_IDS:
    raise SystemExit(f"p.373 statement set changed: {sorted(actual_old ^ OLD_IDS)}")
if len(statements) != 12566 or len(mentions) != 27446 or len(candidates) != 11520:
    raise SystemExit("unexpected table counts; review baseline must be refreshed")
if NEW_CANDIDATES & candidate_by_id.keys() or NEW_MENTIONS & mention_by_id.keys() or NEW_STATEMENTS & statement_by_id.keys():
    raise SystemExit("one or more planned IDs already exist")

p374 = statement_by_id.get("st-chp16-p374-strange-pictures-list-and-custody")
employment_id = "st-chp16-p373-strange-employed-sasso-to-buy-pictures-partial"
if (p374 is None or p374.get("qualifiers", {}).get("cross_reference_statement_ids") != [employment_id]
        or statement_by_id[employment_id].get("qualifiers", {}).get("cross_reference_statement_ids")
        != ["st-chp16-p374-strange-pictures-list-and-custody"]):
    raise SystemExit("p.373/p.374 purchase-list cross-reference changed")

new_candidates = [
    {
        "candidate_id": "cand-11543", "index_entry_id": "", "canonical_name": "Venetian art tradition described by Haskell",
        "index_page_range": "", "suggested_type": "term", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Haskell describes a Venetian art tradition whose last great master he identifies as Francesco Guardi and which he says was carried on by lower-status men. This source-specific term does not predefine a research theme or hierarchy node.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{BODY}#L8",
    },
    {
        "candidate_id": "cand-11544", "index_entry_id": "", "canonical_name": "Unfinished planned book by Sasso on Venetian painting history",
        "index_page_range": "", "suggested_type": "work", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Haskell says Sasso planned a book on the history of Venetian painting but never completed it; no title or surviving manuscript is identified in this passage.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{BODY}#L9",
    },
    {
        "candidate_id": "cand-11545", "index_entry_id": "", "canonical_name": "Alessandro Longhi (person named as painter of Sasso's portrait)",
        "index_page_range": "", "suggested_type": "person", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Haskell's note names Longhi as the painter of Sasso's portrait. The note supplies no dates or further identity evidence. Keep this person separate from index work candidate cand-1426, whose sub-entry is the portrait of G. M. Sasso; compare the portrait candidates at S3.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{NOTES}#L70",
    },
]
for row in new_candidates:
    if row["candidate_id"] in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {row['candidate_id']}")
    candidates.append(row)
    candidate_by_id[row["candidate_id"]] = row

candidate_by_id["cand-2367"]["detail"] = (
    "Index sub-entry for the purchase undertaking described on p.373: Strange employed Sasso to buy Venetian pictures, "
    "with the painter list continuing on p.374. This candidate denotes the purchasing activity, not the person Sasso."
)
candidate_by_id["cand-1426"]["detail"] = (
    "Index sub-entry points to the portrait of G. M. Sasso; retain as an index-derived work candidate. "
    "Do not map the person-name mention 'Alessandro Longhi' to this work candidate; compare with cand-10599 at S3."
)
candidate_by_id["cand-10599"]["detail"] = (
    "Haskell's note reports a portrait of Sasso by Alessandro Longhi. The note does not supply the title, date, "
    "medium, or present location, and the attribution was not independently verified. Compare with index work candidate cand-1426 at S3."
)

def make_mention(mention_id, segment_id, candidate_id, surface, note=""):
    text = body_text if segment_id == BODY else note_text
    start = text.find(surface)
    if start < 0 or text.find(surface, start + 1) >= 0:
        raise SystemExit(f"new mention surface must occur exactly once: {surface!r}")
    end = start + len(surface)
    for existing in mentions:
        if existing["segment_id"] != segment_id:
            continue
        a, b = int(existing["start_char"]), int(existing["end_char"])
        if start < b and a < end:
            raise SystemExit(f"new mention overlaps {existing['mention_id']}: {surface!r}")
    return {"mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
            "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note}


new_mentions = [
    make_mention("m-chp16-p373-sasso-review-0001", BODY, "cand-11543", "the most fruitful tradition of Venetian art"),
    make_mention("m-chp16-p373-sasso-review-0002", BODY, "cand-2719", "the seemingly inexhaustible city",
                 "Anaphoric description of Venice in Haskell's account of embassy agents."),
    make_mention("m-chp16-p373-sasso-review-0003", BODY, "cand-11544", "a great book",
                 "The planned but unfinished book on Venetian painting history; no title is supplied."),
    make_mention("m-chp16-p373-sasso-review-0004", BODY, "cand-2367",
                 "to buy him\nVenetian pictures of all kinds—Giorgiones and Titians, Veroneses and Tintorettos, and",
                 "The purchase undertaking indexed as an event; the painter list continues on p.374."),
]
for row in new_mentions:
    if row["mention_id"] in mention_by_id:
        raise SystemExit(f"mention ID already exists: {row['mention_id']}")
    mentions.append(row)
    mention_by_id[row["mention_id"]] = row

# The index sub-entry is a purchase event; the grammatical mention in this sentence is Sasso the person.
mention_by_id["m-chp16-p373-sasso-0015"]["candidate_id"] = "cand-2364"
mention_by_id["m-chp16-p373-sasso-0015"]["note"] = (
    "Sasso is the person employed; the purchase undertaking is separately represented by cand-2367."
)
# The source's repository locator names the city, so use the existing indexed place candidate.
mention_by_id["m-chp16-p373-sasso-surfacefix-0002"]["candidate_id"] = "cand-2719"
mention_by_id["m-chp16-p373-sasso-surfacefix-0002"]["note"] = (
    "Geographic Venice in the Biblioteca Correr repository locator; mapped to the indexed city candidate cand-2719."
)
mention_by_id["m-chp16-p373-sasso-0021"]["candidate_id"] = "cand-11545"
mention_by_id["m-chp16-p373-sasso-0021"]["note"] = (
    "Person named as the portrait painter; cand-1426 is the index-derived work candidate for a portrait of G. M. Sasso."
)

def edit(statement_id, *, new_id=None, predicate=None, claim=None, qualification=None,
         quote_text=None, start_line=None, end_line=None, subject=NO_CHANGE, object_id=NO_CHANGE,
         relation_candidate=NO_CHANGE, mention_ids=None, speaker=None, text_layer=None,
         ocr_corrections=None, extra=None):
    row = statement_by_id[statement_id]
    if quote_text is not None:
        if row["segment_id"] == BODY:
            source = "\n".join(source_lines[start_line - 1:end_line])
        else:
            source = "\n".join(source_lines[start_line - 1:end_line])
        normalize = lambda value: " ".join(value.split())
        if normalize(quote_text) not in normalize(source):
            raise SystemExit(f"quote does not match cited source lines: {statement_id}")
        row["original_quote"] = quote_text
    if new_id:
        if new_id in statement_by_id:
            raise SystemExit(f"replacement statement ID already exists: {new_id}")
        del statement_by_id[statement_id]
        row["statement_id"] = new_id
        statement_by_id[new_id] = row
    if predicate is not None:
        row["predicate"] = predicate
    if subject is not NO_CHANGE:
        row["subject_candidate_id"] = subject
    if object_id is not NO_CHANGE:
        row["object_candidate_id"] = object_id
    qf = row["qualifiers"]
    if claim is not None:
        qf["claim"] = claim
    if qualification is not None:
        qf["qualification"] = qualification
    if start_line is not None:
        qf["source_line_start"] = start_line
    if end_line is not None:
        qf["source_line_end"] = end_line
    if mention_ids is not None:
        qf["mentioned_candidate_ids"] = mention_ids
    if speaker is not None:
        qf["speaker"] = speaker
    if text_layer is not None:
        qf["text_layer"] = text_layer
    if relation_candidate is not NO_CHANGE:
        if relation_candidate:
            qf["relation_candidate"] = True
        else:
            qf.pop("relation_candidate", None)
    if ocr_corrections is not None:
        if ocr_corrections:
            qf["ocr_corrections"] = ocr_corrections
        else:
            qf.pop("ocr_corrections", None)
    if extra:
        qf.update(extra)
    return row


def correction(line, raw, print_text):
    return {"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": line,
            "ocr": raw, "print": print_text, "basis": "CHP-16.pdf physical page 1."}


body_edits = {
    "st-chp16-p373-patronage-tastes-and-venetian-tradition": dict(
        new_id=RENAMES["st-chp16-p373-patronage-tastes-and-venetian-tradition"],
        predicate="significant_second_half_eighteenth_century_patrons_affected_by_lodoli_algarotti_ideas",
        claim="Haskell says the most significant art patrons emerging in the second half of the eighteenth century were affected by new ideas entering Venice through Carlo Lodoli and Francesco Algarotti.",
        qualification="The passage does not enumerate these patrons; 'most significant' and the intellectual framing are Haskell's assessment. The chapter-opening page has no visible printed folio; p.373 follows the continuous pagination.",
        quote_text=quote(6, 8, "E have seen", "Francesco Algarotti."), start_line=6, end_line=8,
        mention_ids=["cand-4129", "cand-1416", "cand-0041", "cand-2719"],
        ocr_corrections=[
            correction(6, "E have seen", "We have seen"),
            correction(7, "Wof the eighteenth", "of the eighteenth"),
            correction(7, "die new ideas", "the new ideas"),
        ],
    ),
    "st-chp16-p373-dealers-perceived-as-agents-and-collectors": dict(
        predicate="lower_status_dealers_seen_as_agents_for_foreign_embassy_art_acquisitions",
        claim="Haskell says the lower-status men were viewed, when noticed at all, as dealers or agents helping foreign embassies plunder Venice's riches.",
        qualification="This records Haskell's description of how the men were perceived, not an independently verified account of each dealer's conduct.",
        quote_text=quote(8, 8, "In so far as they were known", "city in which they lived."), start_line=8, end_line=8,
        mention_ids=["cand-2719"], relation_candidate=False,
    ),
    "st-chp16-p373-sasso-dealing-collection-and-writing": dict(
        new_id=RENAMES["st-chp16-p373-sasso-dealing-collection-and-writing"],
        predicate="kept_a_small_private_picture_collection",
        claim="Haskell says Sasso set aside a small collection of pictures for himself while dealing.",
        qualification="The passage gives no inventory or title for the collection; the separate candidate is a source-level collection object, not a verified catalogue.",
        quote_text=quote(9, 9, "putting a small collection", "for himself"), start_line=9, end_line=9,
        subject="cand-2364", object_id="cand-10598", mention_ids=["cand-2364", "cand-10598"],
        relation_candidate=True, ocr_corrections=[],
    ),
    "st-chp16-p373-sasso-survived-republic-and-died-1803": dict(
        new_id=RENAMES["st-chp16-p373-sasso-survived-republic-and-died-1803"],
        predicate="survived_the_venetian_republic",
        claim="Haskell says Sasso only just survived the Republic.",
        qualification="The passage does not specify the Republic's end date; no date is inferred here.",
        quote_text=quote(10, 10, "Sasso only just survived", "the Republic"), start_line=10, end_line=10,
        subject="cand-2364", object_id="cand-8838", mention_ids=["cand-2364", "cand-8838"],
        relation_candidate=False,
    ),
    "st-chp16-p373-sasso-born-to-poor-parents-and-studied-painting": dict(
        new_id=RENAMES["st-chp16-p373-sasso-born-to-poor-parents-and-studied-painting"],
        predicate="born_to_poor_parents_around_sixty_years_before_the_account",
        claim="Haskell says Sasso was born some sixty years earlier to poor parents.",
        qualification="The approximate wording is retained; no birth year is calculated.",
        quote_text=quote(12, 12, "He had been born", "poor parents"), start_line=12, end_line=12,
        subject="cand-2364", object_id=None, mention_ids=["cand-2364"], relation_candidate=False,
    ),
    "st-chp16-p373-sasso-contacted-british-residency-in-1774": dict(
        predicate="first_contacted_british_residency_in_1774",
        claim="Haskell identifies Sasso's first contact with the British Residency in 1774 as the moment his career began to matter.",
        qualification="'His real moment' is Haskell's evaluation; the passage does not specify the nature of the contact.",
        quote_text=quote(12, 12, "his real moment", "British Residency."), start_line=12, end_line=12,
        subject="cand-2364", object_id="cand-9174", mention_ids=["cand-2364", "cand-9174"],
        relation_candidate=True,
    ),
    "st-chp16-p373-strange-new-occupant-of-residency": dict(
        predicate="john_strange_was_the_new_occupant_of_the_british_residency_post",
        claim="Haskell identifies John Strange as the new occupant of the British Residency post.",
        qualification="The paragraph places this in the 1774 episode; no independent appointment date is asserted.",
        quote_text=quote(12, 12, "new occupant of the post", "John Strange"), start_line=12, end_line=12,
        subject="cand-2517", object_id="cand-9174", mention_ids=["cand-2364", "cand-2517", "cand-9174"],
        relation_candidate=True,
        ocr_corrections=[correction(12, "termswith", "terms with")],
    ),
    "st-chp16-p373-strange-and-sasso-corresponded-nearly-twenty-years": dict(
        new_id=RENAMES["st-chp16-p373-strange-and-sasso-corresponded-nearly-twenty-years"],
        predicate="corresponded_for_nearly_twenty_years",
        claim="Haskell says Sasso and Strange corresponded for nearly twenty years.",
        qualification="The duration is approximate as stated; the note supplies locators but the letters were not independently consulted.",
        quote_text=quote(12, 13, "and corresponded", "twenty years.2"), start_line=12, end_line=13,
        subject="cand-2364", object_id="cand-2517", mention_ids=["cand-2364", "cand-2517"],
        relation_candidate=True,
        ocr_corrections=[correction(13, "' for nearly twenty years.2", "for nearly twenty years.^2")],
    ),
    "st-chp16-p373-strange-and-sasso-shared-complaints-and-business": dict(
        new_id=RENAMES["st-chp16-p373-strange-and-sasso-shared-complaints-and-business"],
        predicate="shared_complaints_about_contemporary_social_changes",
        claim="Haskell reports that Sasso and Strange grumbled about contemporary social changes, including the end of domestic life and women going out at all hours.",
        qualification="These are Haskell's summaries of the men's complaints; no individual letter or speaker is identified.",
        quote_text=quote(13, 13, "They grumbled about the times", "at all hours of the day and night."), start_line=13, end_line=13,
        subject="cand-2364", object_id="cand-2517", mention_ids=["cand-2364", "cand-2517"], relation_candidate=True,
    ),
    "st-chp16-p373-strange-employed-sasso-to-buy-pictures-partial": dict(
        new_id=RENAMES["st-chp16-p373-strange-employed-sasso-to-buy-pictures-partial"],
        predicate="employed_sasso_to_buy_venetian_pictures_for_strange",
        claim="Haskell says Strange employed Sasso to buy Venetian pictures for him; p.374 continues the painter list.",
        qualification="The p.373 list is incomplete at the page break; p.374 supplies the less-frequent modern painters.",
        quote_text=quote(13, 14, "Strange employed Sasso", "and"), start_line=13, end_line=14,
        subject="cand-2517", object_id="cand-2364", mention_ids=["cand-2517", "cand-2364", "cand-2367"],
        relation_candidate=True,
        extra={"cross_reference_statement_ids": ["st-chp16-p374-strange-pictures-list-and-custody"]},
    ),
}
for statement_id, values in body_edits.items():
    edit(statement_id, **values)

# Existing note rows are narrowed to one claim each; preserve their source-status qualifiers.
edit(
    "st-chp16-p373-note1-sasso-biography-citations",
    predicate="note_cites_cicogna_1856_edition_and_lorenzetti_1914_for_sasso_biography",
    claim="Haskell's note directs readers to Cicogna's footnote in the 1856 edition of Sasso's Osservazioni and to Lorenzetti (1914) for a short biography.",
    qualification="The edition and short-form Lorenzetti reference were not independently consulted; the title's printed reading is corrected in S2 only.",
    quote_text=quote(70, 70, "1 For a short biography", "also Lorenzetti, 1914."), start_line=70, end_line=70,
    mention_ids=["cand-2364", "cand-10600", "cand-10601", "cand-10602"], speaker="Haskell's note",
    text_layer="bibliographic citation", relation_candidate=False,
    ocr_corrections=[correction(70, "A niello", "a niello")],
)
edit(
    "st-chp16-p373-note1-longhi-portrait-reference",
    new_id=RENAMES["st-chp16-p373-note1-longhi-portrait-reference"],
    predicate="longhi_painted_sassos_portrait",
    claim="Haskell's note attributes Sasso's portrait to Alessandro Longhi.",
    qualification="This is the printed attribution as reported by Haskell; the portrait and artist identity were not independently verified.",
    quote_text=quote(70, 70, "For bis portrait by Alessandro Longhi", "Longhi"), start_line=70, end_line=70,
    subject="cand-11545", object_id="cand-10599", mention_ids=["cand-11545", "cand-10599", "cand-2364"],
    speaker="Haskell's note", text_layer="artwork attribution", relation_candidate=True,
    ocr_corrections=[correction(70, "bis portrait", "his portrait")],
)
edit(
    "st-chp16-p373-note2-strange-sasso-letters-in-epistolario",
    predicate="letters_from_strange_to_sasso_located_in_epistolario_moschini",
    claim="Haskell says letters from Strange to Sasso are in the Epistolario Moschini.",
    qualification="The collection and letters were not independently consulted; the note gives no dates or individual shelfmark.",
    quote_text=quote(71, 71, "The letters from Strange to Sasso", "Epistolario Moschini"), start_line=71, end_line=71,
    mention_ids=["cand-2517", "cand-2364", "cand-10604", "cand-10605"],
    speaker="Haskell's note", text_layer="archival locator", relation_candidate=True,
    ocr_corrections=[correction(71, "Biblioteca Cotter", "Biblioteca Correr")],
)
edit(
    "st-chp16-p373-note2-mauroner-quotes-letters",
    quote_text=quote(71, 71, "There are quotations from them", "pp. 48-50."), start_line=71, end_line=71,
    mention_ids=["cand-10606", "cand-10604", "cand-2517", "cand-2364"], relation_candidate=True,
)
edit(
    "st-chp16-p373-note2-sasso-replies-mostly-missing",
    quote_text=quote(71, 71, "Sasso’s replies", "mostly missing"), start_line=71, end_line=71,
    mention_ids=["cand-2364", "cand-2517"], relation_candidate=False,
)
edit(
    "st-chp16-p373-note2-four-sasso-letters-british-museum",
    quote_text=quote(71, 71, "but there are four letters", "ff. 359-63."), start_line=71, end_line=71,
    mention_ids=["cand-2364", "cand-2517", "cand-10607", "cand-5986"], relation_candidate=True,
)

def make_statement(statement_id, segment_id, subject_id, object_id, predicate, start_line, end_line,
                   claim, speaker, text_layer, qualification, mentioned_ids, quote_text,
                   relation_candidate=False, footnote=None, ocr_corrections=None):
    source = "\n".join(source_lines[start_line - 1:end_line])
    normalize = lambda value: " ".join(value.split())
    if normalize(quote_text) not in normalize(source):
        raise SystemExit(f"new statement quote does not match source: {statement_id}")
    qualifiers = {
        "source_line_start": start_line, "source_line_end": end_line,
        "printed_page": 373, "pdf_physical_page": 1,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification, "mentioned_candidate_ids": mentioned_ids,
    }
    if relation_candidate:
        qualifiers["relation_candidate"] = True
    if ocr_corrections:
        qualifiers["ocr_corrections"] = ocr_corrections
    row = {"statement_id": statement_id, "segment_id": segment_id,
           "subject_candidate_id": subject_id, "object_candidate_id": object_id,
           "predicate": predicate, "qualifiers": qualifiers, "original_quote": quote_text,
           "origin": "book", "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md"}
    if footnote:
        row["qualifiers"].update(footnote)
    return row


new_body = [
    make_statement(
        "st-chp16-p373-patrons-promoted-functional-or-classical-taste", BODY, None, None,
        "patrons_promoted_functional_or_classical_tastes", 8, 8,
        "Haskell says the new patrons promoted tastes that were severely functional or returned to the classical.",
        "Haskell", "authorial interpretation", "The passage does not assign either taste to a named individual patron.",
        ["cand-4129", "cand-1416", "cand-0041"], quote(8, 8, "tbe taste that they promoted", "return to the classical—"),
    ),
    make_statement(
        "st-chp16-p373-patron-taste-distinct-from-venetian-tradition", BODY, "cand-11543", None,
        "new_patron_taste_bore_little_relation_to_earlier_venetian_art_tradition", 8, 8,
        "Haskell says the promoted taste bore little relation to the earlier Venetian art tradition.",
        "Haskell", "authorial interpretation", "This is Haskell's comparison; no individual patron's taste is assigned here.",
        ["cand-11543", "cand-1416", "cand-0041"], quote(8, 8, "bore little relation", "Venetian art."),
    ),
    make_statement(
        "st-chp16-p373-venetian-tradition-last-great-master-guardi", BODY, "cand-11543", "cand-1239",
        "guardi_identified_as_last_great_master_of_venetian_art_tradition", 8, 8,
        "Haskell identifies Francesco Guardi as the last great master of this Venetian art tradition.",
        "Haskell", "authorial interpretation", "'Last great master' is Haskell's evaluative periodization.",
        ["cand-11543", "cand-1239"], quote(8, 8, "This tradition", "Guardi,'was"),
        relation_candidate=True,
        ocr_corrections=[correction(8, 'Francesco "Guardi,\'was', "Francesco Guardi, was")],
    ),
    make_statement(
        "st-chp16-p373-venetian-tradition-carried-by-lower-status-men", BODY, "cand-11543", None,
        "venetian_art_tradition_carried_on_by_lower_status_men", 8, 8,
        "Haskell says the Venetian art tradition was carried on by men of less exalted social position.",
        "Haskell", "authorial interpretation", "The men are not named in this passage.",
        ["cand-11543"], quote(8, 8, "was carried on rather by men", "position,"),
    ),
    make_statement(
        "st-chp16-p373-lower-status-men-and-their-painting-attracted-little-attention", BODY, "cand-11543", None,
        "lower_status_men_and_their_painting_attracted_little_attention", 8, 8,
        "Haskell says these men and the kind of painting they encouraged attracted little attention in their own day.",
        "Haskell", "authorial interpretation", "This summarizes the comparison in Haskell's sentence without naming an individual painter beyond Guardi.",
        ["cand-11543"], quote(8, 8, "who in their own day attracted little attention", "they enjoyed and encouraged."),
    ),
    make_statement(
        "st-chp16-p373-dealers-built-small-collections", BODY, None, None,
        "lower_status_dealers_built_small_private_collections", 8, 8,
        "Haskell says these dealers often found time to build small collections of their own while carrying out their activities.",
        "Haskell", "authorial report", "The collecting group is not enumerated and no individual collection is assigned here.",
        [], quote(8, 8, "Yet, while fulfilling these activities", "small collections of their own"),
    ),
    make_statement(
        "st-chp16-p373-collections-reflect-distinctive-taste-and-appeal", BODY, None, None,
        "private_collections_reflected_distinctive_taste_compared_with_major_patronage", 8, 8,
        "Haskell says these small collections reflected a definite taste that might appeal today more than the spectacular patronage of Farsetti, Memmo, or Querini.",
        "Haskell", "authorial interpretation", "The possible modern appeal is explicitly Haskell's judgment, not a measured audience response.",
        ["cand-1002", "cand-1642", "cand-2075"], quote(8, 8, "which reflect a definite taste", "Querini."),
    ),
    make_statement(
        "st-chp16-p373-sasso-bought-and-sold-pictures", BODY, "cand-2364", None,
        "bought_and_sold_pictures", 9, 9,
        "Haskell describes Sasso as buying and selling pictures rapidly.",
        "Haskell", "authorial report", "The passage names no specific pictures in this clause.",
        ["cand-2364"], quote(9, 9, "buying and selling", "he could"),
    ),
    make_statement(
        "st-chp16-p373-sasso-dealt-with-british-agents", BODY, "cand-2364", None,
        "dealt_with_british_agents_who_flattered_and_bullied_him", 9, 10,
        "Haskell says Sasso dealt with British agents who alternately flattered and bullied him.",
        "Haskell", "authorial report", "The agents are not named and their conduct is reported only through Haskell.",
        ["cand-2364"], quote(9, 10, "dealing with\nBritish agents", "bullied him"),
    ),
    make_statement(
        "st-chp16-p373-sasso-corresponded-with-friends-and-dealers", BODY, "cand-2364", None,
        "exchanged_long_letters_with_friends_and_other_dealers", 10, 10,
        "Haskell says Sasso found time for long exchanges of letters with friends and other dealers.",
        "Haskell", "authorial report", "The correspondents are not individually named in this sentence.",
        ["cand-2364"], quote(10, 10, "finding the time somehow", "friends and other dealers"),
    ),
    make_statement(
        "st-chp16-p373-sasso-produced-occasional-pamphlets", BODY, "cand-2364", None,
        "produced_occasional_pamphlets", 10, 10,
        "Haskell says Sasso produced the occasional pamphlet.",
        "Haskell", "authorial report", "No pamphlet title is supplied here.", ["cand-2364"],
        quote(10, 10, "turning out the odd pamphlet", "pamphlet"),
    ),
    make_statement(
        "st-chp16-p373-sasso-amassed-facts", BODY, "cand-2364", None,
        "amassed_facts_of_all_kinds", 10, 10,
        "Haskell says Sasso amassed facts of all kinds.",
        "Haskell", "authorial report", "The passage does not specify a subject or surviving record for these facts.",
        ["cand-2364"], quote(10, 10, "amassing facts", "all kinds"),
    ),
    make_statement(
        "st-chp16-p373-sasso-planned-unfinished-book-on-venetian-painting", BODY, "cand-2364", "cand-11544",
        "planned_but_never_completed_book_on_venetian_painting_history", 10, 10,
        "Haskell says Sasso planned a book on the history of Venetian painting but never completed it.",
        "Haskell", "authorial report", "No title or surviving manuscript is identified; the work remains a source-level candidate.",
        ["cand-2364", "cand-11544"], quote(10, 10, "planning a great book", "painting.1"),
    ),
    make_statement(
        "st-chp16-p373-sasso-life-typical-of-contemporary-figures", BODY, "cand-2364", None,
        "life_described_as_typical_of_figures_of_the_time", 10, 10,
        "Haskell describes Sasso's life as typical of a number of figures at the time.",
        "Haskell", "authorial interpretation", "This is Haskell's generalization, not a measured sample of contemporaries.",
        ["cand-2364"], quote(10, 10, "It was a life typical", "at the time"),
    ),
    make_statement(
        "st-chp16-p373-sasso-died-in-1803", BODY, "cand-2364", None,
        "died_in_1803", 10, 11,
        "Haskell says Sasso died in 1803.",
        "Haskell", "authorial report", "The text says he only just survived the Republic; it does not date the Republic's end.",
        ["cand-2364"], quote(10, 11, "died in", "1803."),
    ),
    make_statement(
        "st-chp16-p373-sasso-studied-painting-briefly", BODY, "cand-2364", None,
        "studied_painting_for_a_short_time", 12, 12,
        "Haskell says Sasso studied painting for a short time.",
        "Haskell", "authorial report", "No school, teacher, or date is supplied.", ["cand-2364"],
        quote(12, 12, "and had himself studied painting", "a short time"),
    ),
    make_statement(
        "st-chp16-p373-sasso-strange-on-excellent-terms", BODY, "cand-2364", "cand-2517",
        "soon_on_excellent_terms_with_john_strange", 12, 12,
        "Haskell says Sasso was soon on excellent terms with John Strange.",
        "Haskell", "authorial report", "'Excellent terms' is Haskell's characterization.",
        ["cand-2364", "cand-2517"], quote(12, 12, "He was soon on excellent termswith", "John Strange"),
        relation_candidate=True,
    ),
    make_statement(
        "st-chp16-p373-sasso-strange-saw-each-other", BODY, "cand-2364", "cand-2517",
        "saw_each_other", 12, 12,
        "Haskell says Sasso and Strange saw each other.",
        "Haskell", "authorial report", "The passage gives no dates or frequency for their meetings.",
        ["cand-2364", "cand-2517"], quote(12, 12, "and the two men saw each other", "each other"),
        relation_candidate=True,
    ),
    make_statement(
        "st-chp16-p373-sasso-strange-condoled-losses-and-illnesses", BODY, "cand-2364", "cand-2517",
        "condoled_with_each_other_in_losses_and_illnesses", 13, 13,
        "Haskell says Sasso and Strange condoled with each other in their losses and illnesses.",
        "Haskell", "authorial report", "The specific losses and illnesses are not identified.",
        ["cand-2364", "cand-2517"], quote(13, 13, "They condoled with each other", "illnesses"),
        relation_candidate=True,
    ),
    make_statement(
        "st-chp16-p373-sasso-strange-exchanged-gossip", BODY, "cand-2364", "cand-2517",
        "exchanged_gossip", 13, 13,
        "Haskell says Sasso and Strange exchanged gossip.",
        "Haskell", "authorial report", "No specific gossip or letter is identified.",
        ["cand-2364", "cand-2517"], quote(13, 13, "exchanged gossip", "gossip"),
        relation_candidate=True,
    ),
    make_statement(
        "st-chp16-p373-sasso-strange-did-lucrative-business", BODY, "cand-2364", "cand-2517",
        "conducted_involved_lucrative_business_together", 13, 13,
        "Haskell says Sasso and Strange did involved, lucrative business together.",
        "Haskell", "authorial report", "The following sentence gives picture purchases as a specific example; no other transactions are inferred.",
        ["cand-2364", "cand-2517"], quote(13, 13, "And above all they did involved, lucrative business together", "together."),
        relation_candidate=True,
    ),
]

note1_ids = [
    "st-chp16-p373-note1-sasso-biography-citations",
    "st-chp16-p373-note1-longhi-painted-sasso-portrait",
    "st-chp16-p373-note1-portrait-depicts-sasso",
    "st-chp16-p373-note1-bollettino-portrait-citation",
]
note2_ids = [
    "st-chp16-p373-note2-strange-sasso-letters-in-epistolario",
    "st-chp16-p373-note2-epistolario-at-correr",
    "st-chp16-p373-note2-correr-in-venice",
    "st-chp16-p373-note2-mauroner-quotes-letters",
    "st-chp16-p373-note2-sasso-replies-mostly-missing",
    "st-chp16-p373-note2-four-sasso-letters-british-museum",
    "st-chp16-p373-note2-sasso-wrote-four-letters-to-strange",
]

def footnote_shared(number, body_lines, note_ids, link_note):
    return {
        "footnote_marker": str(number), "footnote_segment": NOTES,
        "footnote_line_range": "L70-L70" if number == 1 else "L71-L71",
        "footnote_text_pending": False, "footnote_body_link_status": "linked",
        "footnote_body_line_range": body_lines,
        "footnote_note_statement_ids": note_ids,
        "footnote_link_note": link_note,
    }


new_notes = [
    make_statement(
        "st-chp16-p373-note1-portrait-depicts-sasso", NOTES, "cand-10599", "cand-2364",
        "portrait_depicts_sasso", 70, 70,
        "Haskell's note identifies the cited portrait as a portrait of Sasso.",
        "Haskell's note", "artwork attribution", "The pronoun 'his' refers to Sasso in the note; the portrait was not independently viewed.",
        ["cand-10599", "cand-2364"], quote(70, 70, "For bis portrait", "portrait"),
        relation_candidate=True,
    ),
    make_statement(
        "st-chp16-p373-note1-bollettino-portrait-citation", NOTES, "cand-10599", "cand-10603",
        "note_directs_reader_to_bollettino_portrait_reference", 70, 70,
        "Haskell directs readers to Bollettino dei Musei Civici Veneziani (1959, no. 2) for the portrait reference.",
        "Haskell's note", "bibliographic citation", "The cited issue was not independently consulted and the note gives no page or article title.",
        ["cand-10599", "cand-10603"], quote(70, 70, "For bis portrait", "No. 2."),
    ),
    make_statement(
        "st-chp16-p373-note2-epistolario-at-correr", NOTES, "cand-10605", "cand-8262",
        "epistolario_moschini_located_at_biblioteca_correr", 71, 71,
        "Haskell's note locates the Epistolario Moschini at Biblioteca Correr.",
        "Haskell's note", "archival locator", "The repository was not independently consulted; the OCR reading Cotter is corrected to Correr in S2.",
        ["cand-10605", "cand-8262"], quote(71, 71, "Epistolario Moschini", "Biblioteca Cotter"),
        relation_candidate=True,
    ),
    make_statement(
        "st-chp16-p373-note2-correr-in-venice", NOTES, "cand-8262", "cand-2719",
        "biblioteca_correr_located_in_venice", 71, 71,
        "Haskell's note identifies Venice as the location of Biblioteca Correr.",
        "Haskell's note", "repository locator", "The place is mapped to the existing Venice city candidate; the locator has not been externally verified.",
        ["cand-8262", "cand-2719"], quote(71, 71, "Biblioteca Cotter", "Venice."),
        relation_candidate=True,
    ),
    make_statement(
        "st-chp16-p373-note2-sasso-wrote-four-letters-to-strange", NOTES, "cand-2364", "cand-2517",
        "sasso_wrote_four_letters_to_strange", 71, 71,
        "Haskell reports four letters from Sasso to Strange.",
        "Haskell's note", "correspondence report", "The letters and their direction are reported by Haskell; manuscripts were not independently consulted.",
        ["cand-2364", "cand-2517", "cand-10607"], quote(71, 71, "four letters from him to Strange", "Strange"),
        relation_candidate=True,
    ),
]

if {row["statement_id"] for row in new_body + new_notes} != NEW_STATEMENTS:
    raise SystemExit("planned statement set does not match the reviewed inventory")

# Set the note cross-reference lists on all note statements and on the two body statements carrying markers.
for note_id in note1_ids:
    row = next((r for r in statements + new_body + new_notes if r["statement_id"] == note_id), None)
    if row is not None:
        row["qualifiers"].update(footnote_shared(1, "L9-L10", note1_ids,
                                                 "Note 1 supplies Sasso biographical and portrait references."))
for note_id in note2_ids:
    row = next((r for r in statements + new_body + new_notes if r["statement_id"] == note_id), None)
    if row is not None:
        row["qualifiers"].update(footnote_shared(2, "L12-L13", note2_ids,
                                                 "Note 2 identifies the documentary sources behind the Sasso-Strange correspondence."))

book_statement = next(r for r in new_body if r["statement_id"] == "st-chp16-p373-sasso-planned-unfinished-book-on-venetian-painting")
book_statement["qualifiers"].update(footnote_shared(1, "L9-L10", note1_ids,
                                                   "Note 1 supplies Sasso biographical and portrait references."))
correspondence_statement = statement_by_id[RENAMES["st-chp16-p373-strange-and-sasso-corresponded-nearly-twenty-years"]]
correspondence_statement["qualifiers"].update(footnote_shared(2, "L12-L13", note2_ids,
                                                              "Note 2 identifies the documentary sources behind the Sasso-Strange correspondence."))

# Add one S2-only print correction to the surviving citation statement; never rewrite the S0 transcript.
bio = statement_by_id["st-chp16-p373-note1-sasso-biography-citations"]
bio["qualifiers"]["ocr_corrections"] = [correction(70, "A niello", "a niello")]

# Record the p.373 purchase-list continuation from p.374 after the statement ID is normalized.
old_employment = "st-chp16-p373-strange-employed-sasso-to-buy-pictures-partial"
new_employment = RENAMES[old_employment]
p374["qualifiers"]["cross_reference_statement_ids"] = [new_employment]

# Append reviewed body rows immediately after the original body block and notes at the end of p.373's note block.
body_anchor = next(i for i, r in enumerate(statements) if r["statement_id"] == new_employment) + 1
statements[body_anchor:body_anchor] = new_body
note_anchor = next(i for i, r in enumerate(statements) if r["statement_id"] == "st-chp16-p373-note2-four-sasso-letters-british-museum") + 1
statements[note_anchor:note_anchor] = new_notes

all_candidate_ids = {row["candidate_id"] for row in candidates}
for row in statements:
    if row.get("segment_id") not in {BODY, NOTES}:
        continue
    qf = row["qualifiers"]
    start, end = int(qf["source_line_start"]), int(qf["source_line_end"])
    if row["segment_id"] == BODY:
        source = "\n".join(source_lines[start - 1:end])
    else:
        source = "\n".join(source_lines[start - 1:end])
    normalize = lambda value: " ".join(value.split())
    if normalize(row["original_quote"]) not in normalize(source):
        raise SystemExit(f"p.373 quote mismatch after review: {row['statement_id']}")
    if qf.get("relation_candidate") and not (row.get("subject_candidate_id") and row.get("object_candidate_id")):
        raise SystemExit(f"p.373 relation candidate has an open endpoint: {row['statement_id']}")
    for cid in qf.get("mentioned_candidate_ids", []):
        if cid not in all_candidate_ids:
            raise SystemExit(f"candidate reference missing for {row['statement_id']}: {cid}")

planned_ids = set(statement_by_id) | NEW_STATEMENTS
if len(statements) != 12592 or len(mentions) != 27450 or len(candidates) != 11523:
    raise SystemExit("planned table counts do not match the reviewed inventory")

if not args.apply:
    print(json.dumps({
        "mode": "dry-run",
        "p373_statements_before": 16,
        "p373_statements_after": 42,
        "statements_added": len(NEW_STATEMENTS),
        "candidates_added": len(NEW_CANDIDATES),
        "mentions_added": len(NEW_MENTIONS),
        "p373_relation_candidates_after": 20,
        "p373_relation_candidates_with_endpoints": 20,
        "p373_quotes_checked": 42,
        "p374_reverse_cross_reference_updated": p374["qualifiers"]["cross_reference_statement_ids"],
        "backup_suffix": BACKUP_SUFFIX,
    }, ensure_ascii=False, indent=2))
    raise SystemExit(0)

backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in (STATEMENT_TABLE, MENTION_TABLE, CANDIDATE_TABLE)]
for path, backup, expected in zip((STATEMENT_TABLE, MENTION_TABLE, CANDIDATE_TABLE), backups,
                                  (STATEMENT_SHA, MENTION_SHA, CANDIDATE_SHA), strict=True):
    if backup.exists():
        if sha(backup) != expected:
            raise SystemExit(f"recovery copy already exists with unexpected content: {backup.name}")
    else:
        shutil.copy2(path, backup)
write_csv(CANDIDATE_TABLE, candidate_fields, candidates)
write_csv(MENTION_TABLE, mention_fields, mentions)
write_jsonl(STATEMENT_TABLE, statements)
print(json.dumps({
    "mode": "applied",
    "candidates": len(candidates),
    "mentions": len(mentions),
    "statements": len(statements),
    "recovery_copies": [p.name for p in backups],
    "sha256_after": {p.name: sha(p) for p in (STATEMENT_TABLE, MENTION_TABLE, CANDIDATE_TABLE)},
}, ensure_ascii=False, indent=2))
