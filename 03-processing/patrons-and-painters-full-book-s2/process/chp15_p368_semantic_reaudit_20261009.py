"""Controlled, source-locked semantic re-audit of printed p.368 and notes 1-7."""
import argparse
import csv
import copy
import hashlib
import json
import shutil
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-15.pdf"
SOURCE_FILE = "02-sources/02-Markdown/15_CHP-15_sec_ii.md"
BODY = "chp-15:15_CHP-15_sec_ii:l38-47"
NOTES = "chp-15:15_CHP-15_sec_ii:l90-113"
INPUT_SHA = {
    "entity-candidates.csv": "6b3dd053ba fa927526b7b6c93ccc1a4258423be0b9addd7daad c5252ca11b40c".replace(" ", ""),
    "mentions.csv": "3a12c238ee a49646efd80e4b6112e1492eb68501c9238cc3069cdd00ec213af2".replace(" ", ""),
    "book-statements.jsonl": "d723d02f4c 6b6b782f73f680351f4522dc23ae9fb186a430810f6217662c20c8".replace(" ", ""),
}
SOURCE_SHA = "eea847f75c7876dc5b8ea38ef4b64ad30cdd6c629df6a064125ac5f63917d31f"
PDF_SHA = "357e830cc4e880909edd62975bfcd06ade1c2b432d8866229831025fe86f2885"
BACKUP_SUFFIX = ".bak-s2-chp15-p368-semantic-reaudit-20261009"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed p.368 S2 changes")
args = parser.parse_args()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp = Path(handle.name)
    temp.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp = Path(handle.name)
    temp.replace(path)


if sha256(SOURCE) != SOURCE_SHA or sha256(PDF) != PDF_SHA:
    raise SystemExit("p.368 S0 source or registered PDF changed")
paths = {name: TABLES / name for name in INPUT_SHA}
for name, expected in INPUT_SHA.items():
    if sha256(paths[name]) != expected:
        raise SystemExit(f"table changed since this re-audit was prepared: {name}")
for name in INPUT_SHA:
    if paths[name].with_name(paths[name].name + BACKUP_SUFFIX).exists():
        raise SystemExit(f"recovery copy already exists: {name}{BACKUP_SUFFIX}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
required = {
    39: ["The inscriptions are worn", "figures have retreated into anonymity", "weaker sculptures have gained"],
    40: ["Pra della Valle represented one of the most noble attempts", "combine beauty with utility"],
    41: ["friendly controversy with another patrician", "his brothers", "more advanced spirits", "forty-eight, mostly copies"],
    44: ["Farsetti and Memmo were both men", "The last important patron", "confmed his love of art"],
    45: ["Use", "fives quietly", "earlier life had been very much more stormy"],
    46: ["Born in 1721", "a possible association with a foreign ambassador", "constitutional crisis of 1761"],
    47: ["powers of-the State Inquisition", "Querini wished to"],
}
for number, fragments in required.items():
    for fragment in fragments:
        if fragment.casefold() not in source_lines[number - 1].casefold():
            raise SystemExit(f"required source text changed at L{number}: {fragment}")

candidate_path = paths["entity-candidates.csv"]
mention_path = paths["mentions.csv"]
statement_path = paths["book-statements.jsonl"]
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
candidate_by_id = {row["candidate_id"]: row for row in candidates}
mention_by_id = {row["mention_id"]: row for row in mentions}
statement_by_id = {row["statement_id"]: row for row in statements}

required_existing = {
    "st-chp15-p368-prato-effect-of-decay",
    "st-chp15-p368-prato-beauty-utility-and-enlightenment",
    "st-chp15-p368-memmo-zaguri-lodoli-controversy",
    "st-chp15-p368-memmo-political-ambition-declines",
    "st-chp15-p368-memmo-palace-frescoed-gallery",
    "st-chp15-p368-memmo-forty-eight-paintings",
    "st-chp15-p368-memmo-open-house-until-death",
    "st-chp15-p368-farsetti-memmo-public-service-patronage",
    "st-chp15-p368-querini-emerges-as-major-venetian-patron",
    "st-chp15-p368-querini-private-art-public-interest",
    "st-chp15-p368-querini-scholar-gentleman-ideal",
    "st-chp15-p368-querini-born-and-admired-lodoli",
    "st-chp15-p368-querini-informed-memmo-about-lodoli",
    "st-chp15-p368-querini-possible-ambassador-association",
    "st-chp15-p368-querini-leading-role-1761-crisis",
    "st-chp15-p368-querini-state-inquisition-dispute-partial",
    "st-chp15-p368-note1-memmo-zaguri-reference",
    "st-chp15-p368-note4-open-house-reference",
    "st-chp15-p368-note5-brenta-obstruction-reference",
    "st-chp15-p368-note6-elementi-reference",
    "st-chp15-p368-note7-1761-crisis-reference",
}
if not required_existing.issubset(statement_by_id):
    raise SystemExit("one or more expected p.368 statements are missing")
if sum(row["segment_id"] == BODY for row in statements) != 16:
    raise SystemExit("p.368 body statement count changed")
if sum(row["segment_id"] == BODY for row in mentions) != 29:
    raise SystemExit("p.368 body mention count changed")
if any(f"st-chp15-p368-{suffix}" in statement_by_id for suffix in (
    "memmo-lodoli-memory-loyalty", "memmo-paintings-interest", "memmo-family-paintings-owned",
    "memmo-open-house-hosted-by", "memmo-open-house-at-family-palace", "memmo-open-house-with-brothers",
    "memmo-open-house-for-advanced-spirits", "memmo-public-service-patronage",
    "querini-enlightened-views-comparison", "querini-public-interest-accusation",
    "querini-earlier-life-stormy", "querini-admired-lodoli", "querini-successful-political-career",
    "querini-authorities-difficulties", "querini-woman-possible-association", "querini-first-notoriety-1761",
)):
    raise SystemExit("one or more planned p.368 statement IDs already exist")
for cid in ("cand-11532", "cand-11533", "cand-11534"):
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID collision: {cid}")
for mid in ("m-chp15-p368-querini-0050", "m-chp15-p368-querini-0051"):
    if mid in mention_by_id:
        raise SystemExit(f"mention ID collision: {mid}")


def span_quote(line_number, start, end):
    text = source_lines[line_number - 1]
    left = text.index(start)
    right = text.index(end, left) + len(end)
    return text[left:right]


def line_range_quote(start_line, start_marker, end_line, end_marker):
    first = source_lines[start_line - 1]
    last = source_lines[end_line - 1]
    left = first.index(start_marker)
    right = last.index(end_marker) + len(end_marker)
    if start_line == end_line:
        return first[left:right]
    return "\n".join([first[left:], *source_lines[start_line:end_line - 1], last[:right]])


def make_qualifiers(start, end, claim, mentioned, *, relation=None, relation_note=None,
                    qualification="", footnote=None, predicate_status=None, cross_refs=None,
                    ocr=None, role=None):
    q = {
        "source_line_start": start,
        "source_line_end": end,
        "printed_page": 368,
        "pdf_physical_page": 8,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "authorial report",
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    if relation:
        q["relation_candidate"] = True
        q["relation_candidate_note"] = relation_note or "Source-bound S2 relation candidate; no S6 formal edge is created here."
    if footnote:
        marker, note_id, body_line = footnote
        q.update({
            "footnote_marker": marker,
            "footnote_segment": NOTES,
            "footnote_line_range": f"L{97 + int(marker) - 1}-L{97 + int(marker) - 1}" if False else {
                "1": "L97-L97", "2": "L98-L98", "3": "L99-L100", "4": "L101-L101",
                "5": "L102-L102", "6": "L103-L103", "7": "L104-L104",
            }[marker],
            "footnote_text_pending": False,
            "footnote_body_link_status": "linked",
            "footnote_body_line_range": f"L{body_line}",
            "footnote_note_statement_ids": [note_id],
            "footnote_link_note": "",
        })
    if predicate_status:
        q["predicate_status"] = predicate_status
    if cross_refs:
        q.update(cross_refs)
    if ocr:
        q["ocr_corrections"] = ocr
    if role:
        q["role"] = role
    return q


def set_statement(statement_id, *, subject, predicate, object_id, quote, start, end, claim, mentioned,
                  relation=None, relation_note=None, qualification="", footnote=None,
                  predicate_status=None, cross_refs=None, ocr=None, role=None):
    row = statement_by_id[statement_id]
    row["subject_candidate_id"] = subject
    row["predicate"] = predicate
    row["object_candidate_id"] = object_id
    row["original_quote"] = quote
    row["qualifiers"] = make_qualifiers(start, end, claim, mentioned, relation=relation,
        relation_note=relation_note, qualification=qualification, footnote=footnote,
        predicate_status=predicate_status, cross_refs=cross_refs, ocr=ocr, role=role)
    return row


def add_statement(statement_id, *, subject, predicate, object_id, quote, start, end, claim, mentioned,
                  relation=None, relation_note=None, qualification="", footnote=None,
                  predicate_status=None, cross_refs=None, ocr=None, role=None):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID collision: {statement_id}")
    row = {
        "statement_id": statement_id,
        "segment_id": BODY,
        "subject_candidate_id": subject,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": make_qualifiers(start, end, claim, mentioned, relation=relation,
            relation_note=relation_note, qualification=qualification, footnote=footnote,
            predicate_status=predicate_status, cross_refs=cross_refs, ocr=ocr, role=role),
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_FILE,
    }
    statement_by_id[statement_id] = row
    statements.append(row)
    return row


def ocr(line, original, printed):
    return [{"source_file": SOURCE_FILE, "source_line": line, "ocr": original,
             "print": printed, "basis": "CHP-15.pdf physical page 8."}]


def note(marker, note_id):
    return (marker, note_id, 41 if marker in {"1", "2", "3", "4"} else (45 if marker == "5" else 46))


q = span_quote(39, "The inscriptions are worn", "general decay.")
set_statement("st-chp15-p368-prato-effect-of-decay", subject="cand-3960", predicate="decay_changed_prato_valle_inscriptions_figures_and_weaker_sculpture", object_id=None,
    quote=q, start=39, end=39,
    claim="Haskell says the inscriptions were worn, figures had retreated into anonymity, and weaker sculptures had gained from general decay.",
    mentioned=["cand-3960"], qualification="This is Haskell's retrospective report; no independent site survey is used.",
    cross_refs={"cross_reference_segments": ["chp-15:15_CHP-15_sec_ii:l30-36"],
                "cross_reference_text": "The preceding p.367 sentence describes the original oasis-like impression and its loss through time, climate and summer dust.",
                "cross_reference_text_pending": False})

set_statement("st-chp15-p368-prato-beauty-utility-and-enlightenment", subject="cand-3960", predicate="pra_del_valle_as_attempt_to_combine_beauty_and_utility", object_id="cand-8107",
    quote=span_quote(40, "Pra della Valle", "Enlightenment."), start=40, end=40,
    claim="Haskell calls the Prà della Valle one of the most noble attempts by a Venetian patron to combine beauty with utility and solve a problem that occupied Enlightenment thinkers.",
    mentioned=["cand-3960", "cand-1642", "cand-8107"],
    qualification="This is Haskell's evaluative characterization. The surrounding p.367 passage identifies Memmo as the patron, but no formal relation to the concept of utility is inferred.",
    ocr=ocr(40, "Pra", "Prà"))

set_statement("st-chp15-p368-memmo-zaguri-lodoli-controversy", subject="cand-1642", predicate="disputed_with", object_id="cand-2829",
    quote=span_quote(41, "During his last years Memmo became involved", "over the merits of Lodoli"), start=41, end=41,
    claim="Haskell says Andrea Memmo became involved in a friendly controversy with Pietro Zaguri over Carlo Lodoli's merits.",
    mentioned=["cand-1642", "cand-2829", "cand-1411"], relation=True,
    relation_note="The source explicitly reports a friendly controversy. It does not establish collaboration or a lasting personal conflict.",
    footnote=note("1", "st-chp15-p368-note1-memmo-zaguri-reference"))

add_statement("st-chp15-p368-memmo-lodoli-memory-loyalty", subject="cand-1642", predicate="remained_faithful_to_memory_of", object_id="cand-1411",
    quote=span_quote(41, "to whose memory he remained", "faithful."), start=41, end=41,
    claim="Haskell says Memmo remained passionately faithful to Lodoli's memory.",
    mentioned=["cand-1642", "cand-1411"], relation=True,
    relation_note="This is a source-bound statement of commemorative loyalty; do not convert it into a teacher-student or influence relation.",
    footnote=note("1", "st-chp15-p368-note1-memmo-zaguri-reference"))

set_statement("st-chp15-p368-memmo-political-ambition-declines", subject="cand-1642", predicate="political_ambitions_declined_with_venice_fortunes", object_id="cand-2719",
    quote=span_quote(41, "But his political ambitions", "fortunes of Venice."), start=41, end=41,
    claim="Haskell says Memmo's political ambitions declined as Venice's fortunes declined.",
    mentioned=["cand-1642", "cand-2719"], qualification="The source presents a parallel decline; no more specific causal mechanism is asserted.")

set_statement("st-chp15-p368-memmo-palace-frescoed-gallery", subject="cand-10518", predicate="commissioned_by", object_id="cand-1642",
    quote=span_quote(41, "He had had the family palace decorated", "pedestal,2"), start=41, end=41,
    claim="Haskell says Memmo had the family palace decorated with a frescoed gallery of classical orators, poets and philosophers, each named on a pedestal.",
    mentioned=["cand-1642", "cand-10517", "cand-10518"], relation=True,
    relation_note="The causative wording says Memmo had the decoration made; it supports a commissioning candidate but names no painter or formal contract.",
    footnote=note("2", "st-chp15-p368-note2-gallery-destruction"))

set_statement("st-chp15-p368-memmo-forty-eight-paintings", subject="cand-1642", predicate="had_little_interest_in_paintings", object_id="cand-1646",
    quote=span_quote(41, "but he seems to have had almost no interest", "paintings"), start=41, end=41,
    claim="Haskell says Memmo seems to have had almost no interest in paintings.", mentioned=["cand-1642", "cand-1646"],
    qualification="Haskell explicitly qualifies this as an appearance ('seems').")

add_statement("st-chp15-p368-memmo-family-paintings-owned", subject="cand-1646", predicate="owned_by", object_id="cand-1642",
    quote=span_quote(41, "of which he owned only forty-eight", "mostly copies.3"), start=41, end=41,
    claim="Haskell says Memmo owned only forty-eight paintings, mostly copies.", mentioned=["cand-1642", "cand-1646"], relation=True,
    relation_note="The source reports an inventory-based ownership count; the collection and inventory have not been independently examined.",
    footnote=note("3", "st-chp15-p368-note3-inventory-record"))

set_statement("st-chp15-p368-memmo-open-house-until-death", subject="cand-11534", predicate="recurring_open_house_gatherings_until_1792", object_id=None,
    quote=span_quote(41, "In this palace, in the company of his brothers", "until his death in 1792.4"), start=41, end=41,
    claim="Haskell says recurring open-house gatherings took place in Memmo's family palace with his brothers and more advanced spirits of the day until his death in 1792.",
    mentioned=["cand-11534", "cand-1642", "cand-10517", "cand-11532", "cand-11533"],
    qualification="The text gives no names or count for the brothers or guests; the event candidate represents a recurring practice, not a single dated gathering.",
    footnote=note("4", "st-chp15-p368-note4-open-house-reference"))

for sid, subject, pred, obj, claim, ids, relnote in [
    ("st-chp15-p368-memmo-open-house-hosted-by", "cand-11534", "hosted_by", "cand-1642", "The recurring open-house gatherings were hosted by Andrea Memmo.", ["cand-11534", "cand-1642"], "The source directly assigns the open house to Memmo; the claim remains tied to Haskell's account."),
    ("st-chp15-p368-memmo-open-house-at-family-palace", "cand-11534", "occurred_at", "cand-10517", "The recurring open-house gatherings took place in the Memmo family palace.", ["cand-11534", "cand-10517"], "The source names the palace but does not identify its address."),
    ("st-chp15-p368-memmo-open-house-with-brothers", "cand-11534", "has_participant", "cand-11532", "Memmo's unnamed brothers were present at the recurring open-house gatherings.", ["cand-11534", "cand-11532"], "The source says 'in the company of his brothers'; their names and number remain unknown."),
    ("st-chp15-p368-memmo-open-house-for-advanced-spirits", "cand-11534", "has_participant", "cand-11533", "The recurring open-house gatherings were held for the more advanced spirits of the day.", ["cand-11534", "cand-11533"], "This is Haskell's unnamed social group; no institution or individual membership is inferred."),
]:
    add_statement(sid, subject=subject, predicate=pred, object_id=obj,
        quote=span_quote(41, "In this palace, in the company of his brothers", "to the more advanced spirits of the day"), start=41, end=41,
        claim=claim, mentioned=ids, relation=True, relation_note=relnote,
        qualification="Source-bound relationship candidate; no S6 formal relation is created.")

set_statement("st-chp15-p368-farsetti-memmo-public-service-patronage", subject="cand-1002", predicate="patronage_bound_to_public_service_in_venice_and_padua", object_id=None,
    quote=span_quote(44, "Farsetti and Memmo were both men", "Venice and Padua."), start=44, end=44,
    claim="Haskell characterizes Farsetti as a patron whose arts patronage was closely bound to service to the public life of Venice and Padua.",
    mentioned=["cand-1002", "cand-2719", "cand-1803"], qualification="The source makes the same generalization about both men; this statement isolates Farsetti without asserting a relationship between him and Memmo.")

add_statement("st-chp15-p368-memmo-public-service-patronage", subject="cand-1642", predicate="patronage_bound_to_public_service_in_venice_and_padua", object_id=None,
    quote=span_quote(44, "Farsetti and Memmo were both men", "Venice and Padua."), start=44, end=44,
    claim="Haskell characterizes Memmo as a patron whose arts patronage was closely bound to service to the public life of Venice and Padua.",
    mentioned=["cand-1642", "cand-2719", "cand-1803"], qualification="The source makes the same generalization about both men; this statement isolates Memmo without asserting a relationship between him and Farsetti.")

set_statement("st-chp15-p368-querini-emerges-as-major-venetian-patron", subject="cand-2075", predicate="last_important_patron_to_emerge_in_venice", object_id=None,
    quote=span_quote(44, "The last important patron", "Angelo Querini,"), start=44, end=44,
    claim="Haskell calls Angelo Querini the last important patron to emerge in Venice.", mentioned=["cand-2075", "cand-2719"],
    qualification="This is Haskell's historical evaluation, not a count-based conclusion.")

add_statement("st-chp15-p368-querini-enlightened-views-comparison", subject="cand-2075", predicate="enlightened_views_compared_with_farsetti_and_memmo", object_id=None,
    quote=span_quote(44, "carried his", "either of these men"), start=44, end=44,
    claim="Haskell says Querini carried his enlightened views further than those of Farsetti and Memmo.",
    mentioned=["cand-2075", "cand-8107", "cand-1002", "cand-1642"],
    qualification="This comparison is Haskell's evaluation; it does not create a social or institutional relation among the three patrons.")

set_statement("st-chp15-p368-querini-private-art-public-interest", subject="cand-2075", predicate="confined_art_interest_to_private_use", object_id=None,
    quote=line_range_quote(44, "but he confmed his love of art", 45, "Use"), start=44, end=45,
    claim="Haskell says Querini confined his love of art strictly to private use.", mentioned=["cand-2075"],
    qualification="The print reads 'life'; S0 OCR breaks the word across the page line as 'private Use'.",
    ocr=[*ocr(44, "confmed", "confined"), *ocr(45, "Use", "life")])

add_statement("st-chp15-p368-querini-public-interest-accusation", subject="cand-2075", predicate="accused_of_advancing_private_interests_at_public_expense", object_id=None,
    quote=span_quote(45, "indeed he was accused of furthering", "those of the public.5"), start=45, end=45,
    claim="Haskell reports that Querini was accused of furthering his own interests in art at the expense of the public.",
    mentioned=["cand-2075"], qualification="This is an accusation reported by Haskell; its accusers and basis are not identified in the sentence.",
    footnote=note("5", "st-chp15-p368-note5-brenta-obstruction-reference"))

set_statement("st-chp15-p368-querini-scholar-gentleman-ideal", subject="cand-2075", predicate="later_life_as_example_of_scholar_gentleman_ideal", object_id="cand-10526",
    quote=span_quote(45, "In his later years he provides", "world with a certain detachment."), start=45, end=45,
    claim="Haskell presents Querini's later life as an example of a recurring scholar-gentleman ideal: cultivated taste, quiet estate life and detachment from the world.",
    mentioned=["cand-2075", "cand-10526"], qualification="This is Haskell's interpretive characterization, not an occupational classification.",
    ocr=ocr(45, "fives", "lives"))

add_statement("st-chp15-p368-querini-earlier-life-stormy", subject="cand-2075", predicate="earlier_life_described_as_more_stormy", object_id=None,
    quote=span_quote(45, "But his earlier life", "stormy."), start=45, end=45,
    claim="Haskell contrasts Querini's later quiet life with a much more stormy earlier life.", mentioned=["cand-2075"],
    qualification="This is a comparative characterization by Haskell.")

set_statement("st-chp15-p368-querini-born-and-admired-lodoli", subject="cand-2075", predicate="born_in_1721", object_id=None,
    quote=span_quote(46, "Born in 1721", "Born in 1721"), start=46, end=46,
    claim="Haskell gives Angelo Querini's birth year as 1721.", mentioned=["cand-2075"], qualification="The date is reported by Haskell and not independently verified here.")

add_statement("st-chp15-p368-querini-admired-lodoli", subject="cand-2075", predicate="expressed_admiration_for", object_id="cand-1411",
    quote=span_quote(46, "he too had been a keen admirer", "Carlo Lodoli"), start=46, end=46,
    claim="Haskell says Querini had been a keen admirer of Carlo Lodoli.", mentioned=["cand-2075", "cand-1411"], relation=True,
    relation_note="Admiration is explicit. Do not infer that Lodoli taught Querini or directly influenced every later position.")

informed_row = set_statement("st-chp15-p368-querini-informed-memmo-about-lodoli", subject="cand-2075", predicate="provided_information_to", object_id="cand-1642",
    quote=span_quote(46, "and it was he who gave Memmo much information", "that influential figure."), start=46, end=46,
    claim="Haskell says Querini gave Memmo much information about Lodoli's earlier years.", mentioned=["cand-2075", "cand-1642", "cand-1411"], relation=True,
    relation_note="The source explicitly identifies Querini as an information source for Memmo about Lodoli; the cited Memmo text was not independently consulted.",
    footnote=note("6", "st-chp15-p368-note6-elementi-reference"))
informed_row["qualifiers"]["footnote_link_note"] = "CHP-15.pdf physical page 8 shows superscript 6 after 'influential figure'; the S0 OCR omits that marker."
informed_row["qualifiers"]["print_checked"] = True

add_statement("st-chp15-p368-querini-successful-political-career", subject="cand-2075", predicate="began_successful_political_career", object_id=None,
    quote=span_quote(46, "After beginning a successful career in politics", "in politics,"), start=46, end=46,
    claim="Haskell describes Querini as beginning a successful political career.", mentioned=["cand-2075"])

set_statement("st-chp15-p368-querini-possible-ambassador-association", subject="cand-2075", predicate="possibly_associated_with", object_id="cand-10521",
    quote=span_quote(46, "because of a possible association", "foreign ambassador"), start=46, end=46,
    claim="Haskell says Querini's difficulties with the authorities followed a possible association with a foreign ambassador.",
    mentioned=["cand-2075", "cand-10521"], relation=True,
    relation_note="The source says 'possible'; the ambassador and the alleged association remain unidentified and unverified.",
    qualification="The text reports political difficulties separately from the uncertain explanation; it does not establish the association as fact.")

add_statement("st-chp15-p368-querini-authorities-difficulties", subject="cand-2075", predicate="encountered_difficulties_with_authorities", object_id=None,
    quote=span_quote(46, "he was soon in difficulties with the authorities", "the authorities"), start=46, end=46,
    claim="Haskell says Querini soon encountered difficulties with the authorities after beginning his political career.", mentioned=["cand-2075"],
    qualification="The source does not name the authorities here.")

add_statement("st-chp15-p368-querini-woman-possible-association", subject="cand-2075", predicate="possible_association_involved_unnamed_woman", object_id="cand-10522",
    quote=span_quote(46, "though", "rather than politics."), start=46, end=46,
    claim="Haskell suggests, with 'perhaps', that the possible association concerned a woman rather than politics.",
    mentioned=["cand-2075", "cand-10521", "cand-10522"], relation=True,
    relation_note="The explanation is explicitly tentative; neither the woman nor the nature of any association is identified.",
    qualification="Retain Haskell's 'perhaps'; this is not an established romantic, diplomatic or political relationship.")

set_statement("st-chp15-p368-querini-leading-role-1761-crisis", subject="cand-2075", predicate="played_leading_role_in", object_id="cand-10523",
    quote=span_quote(46, "in which he played the leading part", "leading part.7"), start=46, end=46,
    claim="Haskell says Querini played the leading part in the constitutional crisis of 1761.",
    mentioned=["cand-2075", "cand-10523"], relation=True,
    relation_note="The role is explicitly attributed by Haskell; the cited Bozzola study was not independently consulted.",
    footnote=note("7", "st-chp15-p368-note7-1761-crisis-reference"))

add_statement("st-chp15-p368-querini-first-notoriety-1761", subject="cand-2075", predicate="first_achieved_notoriety_during", object_id="cand-10523",
    quote=span_quote(46, "He first achieved notoriety", "crisis of 1761"), start=46, end=46,
    claim="Haskell says Querini first achieved notoriety during the constitutional crisis of 1761.",
    mentioned=["cand-2075", "cand-10523"], footnote=note("7", "st-chp15-p368-note7-1761-crisis-reference"))

state_row = statement_by_id["st-chp15-p368-querini-state-inquisition-dispute-partial"]
state_q = state_row["qualifiers"]
state_q["relation_candidate"] = True
state_q["relation_candidate_note"] = "The source reports Querini's intention to reduce State Inquisition powers; the sentence continues at p.369, and the specific legal mechanism is not stated."
state_q["ocr_corrections"] = ocr(47, "of-the", "of the")
state_q["mentioned_candidate_ids"] = ["cand-2075", "cand-10524"]


def add_candidate(cid, label, suggested_type, detail):
    candidates.append({
        "candidate_id": cid,
        "index_entry_id": "",
        "canonical_name": label,
        "index_page_range": "",
        "suggested_type": suggested_type,
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": detail,
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY}#L41",
    })


add_candidate("cand-11532", "Unidentified brothers of Andrea Memmo present at his open-house gatherings", "",
    "Haskell says Memmo held open house in the company of his brothers. Their names and number are not supplied; keep the group separate from Memmo and do not infer a family identity beyond the stated sibling relation.")
add_candidate("cand-11533", "Unidentified more advanced spirits of the day who attended Memmo's open house", "",
    "Haskell names the guests only as 'the more advanced spirits of the day'. No individuals, stable organization or exact membership are identified.")
add_candidate("cand-11534", "Recurring open-house gatherings at Andrea Memmo's family palace", "event",
    "Haskell reports recurring open-house gatherings in the family palace, with Memmo's brothers and more advanced spirits of the day, until his death in 1792. This candidate represents a recurring social activity, not one separately dated event.")

mention_by_id["m-chp15-p368-querini-0012"]["candidate_id"] = "cand-11532"
mention_by_id["m-chp15-p368-querini-0012"]["note"] = "The phrase identifies Memmo's unnamed brothers, not Memmo himself; their names and number are unknown."


def add_mention(mid, surface, cid, note_text):
    line = source_lines[40]
    segment_text = "\n".join(source_lines[37:47])
    start = segment_text.index(surface)
    mentions.append({
        "mention_id": mid,
        "segment_id": BODY,
        "candidate_id": cid,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": note_text,
    })


add_mention("m-chp15-p368-querini-0050", "the more advanced spirits", "cand-11533",
    "Unnamed collective described by Haskell; no individual members or institution inferred.")
add_mention("m-chp15-p368-querini-0051", "open house", "cand-11534",
    "Recurring social activity treated as an event candidate; not a named or single dated gathering.")

all_candidate_ids = {row["candidate_id"] for row in candidates}
all_statement_ids = {row["statement_id"] for row in statements}
all_mention_ids = {row["mention_id"] for row in mentions}
if len(all_candidate_ids) != len(candidates) or len(all_statement_ids) != len(statements) or len(all_mention_ids) != len(mentions):
    raise SystemExit("duplicate IDs found after planned transformations")
for row in statements:
    if row.get("segment_id") not in (BODY, NOTES):
        continue
    for cid in [row.get("subject_candidate_id"), row.get("object_candidate_id"), *(row.get("qualifiers", {}).get("mentioned_candidate_ids", []))]:
        if cid and cid not in all_candidate_ids:
            raise SystemExit(f"dangling candidate reference in {row['statement_id']}: {cid}")

quote_errors = []
for row in statements:
    if row.get("segment_id") not in (BODY, NOTES):
        continue
    q = row.get("qualifiers") or {}
    start = q.get("source_line_start")
    end = q.get("source_line_end")
    if not start or not end:
        quote_errors.append(f"{row['statement_id']}: no source line anchor")
        continue
    cited = "\n".join(source_lines[int(start) - 1:int(end)])
    if " ".join(row.get("original_quote", "").split()) not in " ".join(cited.split()):
        quote_errors.append(f"{row['statement_id']}: quote does not match cited source lines")
if quote_errors:
    raise SystemExit("quote anchor preflight failed:\n" + "\n".join(quote_errors))

for row in mentions:
    if row.get("segment_id") != BODY:
        continue
    segment = "\n".join(source_lines[37:47])
    start = int(row["start_char"])
    end = int(row["end_char"])
    if segment[start:end] != row["surface_form"]:
        raise SystemExit(f"mention span mismatch: {row['mention_id']}")

relation_rows = [row for row in statements if row.get("segment_id") in (BODY, NOTES) and (row.get("qualifiers") or {}).get("relation_candidate") is True]
open_relation_rows = [row for row in relation_rows if not row.get("subject_candidate_id") or not row.get("object_candidate_id")]
print(f"p368 body statements: {sum(row['segment_id'] == BODY for row in statements)}; body mentions: {sum(row['segment_id'] == BODY for row in mentions)}")
print(f"new candidates: cand-11532..cand-11534; new statements: {len(statements) - len(read_jsonl(statement_path))}; new mentions: 2; p368/note relation candidates now {len(relation_rows)} (open endpoints {len(open_relation_rows)})")
print("source quotes, mention spans and candidate references: preflight passed")
print("changes: separate composite claims; correct brothers mention; move note 6 to information claim; add source-bound relationship candidates; record page-8 OCR readings")

if args.apply:
    for name, path in paths.items():
        shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions)
    write_jsonl(statement_path, statements)
    for name, path in paths.items():
        print(f"{name} sha256={sha256(path)}")
    print("applied; recovery copies saved with", BACKUP_SUFFIX)
else:
    print("dry-run only; no table was written")
