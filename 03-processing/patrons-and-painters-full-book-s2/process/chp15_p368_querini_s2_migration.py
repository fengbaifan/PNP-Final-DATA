"""Controlled S2 migration for printed p.368 and its notes 1–7."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-15.pdf"
SOURCE_SHA = "eea847f75c7876dc5b8ea38ef4b64ad30cdd6c629df6a064125ac5f63917d31f"
PDF_SHA = "357e830cc4e880909edd62975bfcd06ade1c2b432d8866229831025fe86f2885"
SOURCE_FILE = "02-sources/02-Markdown/15_CHP-15_sec_ii.md"
BODY_PREV = "chp-15:15_CHP-15_sec_ii:l30-36"
BODY = "chp-15:15_CHP-15_sec_ii:l38-47"
BODY_NEXT = "chp-15:15_CHP-15_sec_ii:l49-59"
NOTES = "chp-15:15_CHP-15_sec_ii:l90-113"
P367_PARTIAL = "st-chp15-p367-climate-and-prato-impression-partial"
BACKUP_SUFFIX = ".bak-s2-chp15-p368-querini-apply-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.368 S2 migration")
args = parser.parse_args()


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


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("chapter 15 sec_ii source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-15 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
required_source = [
    (39, "wilderness. The inscriptions are worn"),
    (40, "Pra della Valle represented one of the most noble attempts"),
    (41, "Pietro Zaguri, over the merits of Lodoli"),
    (41, "owned only forty-eight, mostly copies"),
    (41, "until his death in 1792"),
    (43, "ANGELO QUERINI"),
    (44, "Angelo Querini, carried his"),
    (45, "scholar-gentleman of cultivated tastes"),
    (46, "a possible association with a foreign ambassador"),
    (46, "constitutional crisis of 1761"),
    (47, "State Inquisition"),
    (97, "Molmenti: Un nobil huomo"),
    (98, "Fontana, p. 142"),
    (99, "Petizion 488"),
    (100, "drawing of the holy family by Mengs"),
    (102, "flooding of the Brenta"),
    (103, "[Andrea Memmo], 1786, p. 29, note 1"),
    (104, "1948, pp. 93-116"),
]
for line_number, required in required_source:
    if required.casefold() not in source_lines[line_number - 1].casefold():
        raise SystemExit(f"required source text changed at L{line_number}: {required}")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)
candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}

for segment_id in (BODY_PREV, BODY, BODY_NEXT, NOTES):
    if segment_id not in coverage_by_id:
        raise SystemExit(f"missing S2 coverage row: {segment_id}")
if (
    coverage_by_id[BODY_PREV]["migration_status"] != "partial"
    or coverage_by_id[BODY]["migration_status"] != "pending"
    or coverage_by_id[BODY_NEXT]["migration_status"] != "pending"
    or coverage_by_id[NOTES]["migration_status"] != "partial"
    or coverage_by_id[NOTES]["source_line_ranges"] != "L91-96"
):
    raise SystemExit("S2 coverage preconditions changed")
if P367_PARTIAL not in statement_by_id or statement_by_id[P367_PARTIAL]["qualifiers"].get("predicate_status") != "partial":
    raise SystemExit("expected p.367 cross-page statement is not partial")
if any(row["segment_id"] == BODY for row in mentions) or any(row["segment_id"] == BODY for row in statements):
    raise SystemExit("p.368 body rows already exist")
if any(row.get("statement_id", "").startswith("st-chp15-p368-") for row in statements):
    raise SystemExit("p.368 statements already exist")

new_candidates = [
    ("cand-10512", "Fontana, p.142 (citation locator in Haskell p.368 note 2)", "archive", 98,
     "Haskell gives only a surname and page reference; work and author's identity remain unresolved."),
    ("cand-10513", "Lorenzo da Ponte, p.52 (citation locator in Haskell p.368 note 4)", "archive", 101,
     "The note supplies a name and page only; cited work and exact bibliographic role have not been checked."),
    ("cand-10514", "Andrea Memmo effects inventory, Archivio di Stato di Venezia, Petizion 488 (1792)", "archive", 99,
     "Haskell cites entries dated 30 January 1792 and 24 February 1792/3 M.V.; the archival record has not been consulted."),
    ("cand-10515", "Brunelli Bonetti, 1951, pp.185-200 (citation locator in Haskell p.368 note 5)", "archive", 102,
     "Citation locator for discussion of Querini and Brenta flood-control proposals; title and source text not independently checked."),
    ("cand-10516", "Bozzola, 1948, pp.93-116 (citation locator in Haskell p.368 note 7)", "archive", 104,
     "Citation locator for the 1761 constitutional crisis; title and source text not independently checked."),
    ("cand-10517", "Andrea Memmo family palace, location unspecified in Haskell p.368", "place", 41,
     "The source names a family palace but does not identify its address or distinguish it from other Memmo residences."),
    ("cand-10518", "Frescoed gallery of classical orators, poets and philosophers in the Memmo family palace", "work", 41,
     "Haskell describes a named-figure decorative program; note 2 says ‘These’ were destroyed about 1960, with referent left cautious."),
    ("cand-10519", "Drawing of the Holy Family by Anton Rafael Mengs listed in the Memmo inventory", "work", 100,
     "The drawing is reported in Haskell's account of the 1792 inventory; no present location or independent attribution is supplied."),
    ("cand-10520", "Brenta River, named in the p.368 note 5 flood-control account", "place", 102,
     "Source refers to flooding of the Brenta; geographic normalization is deferred to S3."),
    ("cand-10521", "Unidentified foreign ambassador possibly associated with Angelo Querini", "person", 46,
     "Haskell reports only a possible association; the ambassador's identity and the allegation remain unresolved."),
    ("cand-10522", "Unidentified woman said possibly to be involved in Angelo Querini's reported association", "person", 46,
     "Haskell's ‘perhaps’ qualification is retained; the woman is unnamed and no relationship is inferred."),
    ("cand-10523", "Venetian constitutional crisis of 1761", "event", 46,
     "Haskell says Querini played a leading part; event scope and chronology remain as described in the source."),
    ("cand-10524", "State Inquisition named in Haskell's account of Querini's dispute", "institution", 47,
     "Source names the State Inquisition but the sentence continues onto p.369; institutional identity is not normalized here."),
    ("cand-10525", "Sasso, surname-only co-compiler of the Memmo effects inventory", "person", 99,
     "Haskell gives only the surname in this note; do not assume identity with another Sasso candidate until S3."),
    ("cand-10526", "Scholar-gentleman ideal of cultivated taste and detached estate life", "term", 45,
     "Haskell calls this a recurrent ideal; retain it as an interpretive concept, not as a concrete social organization."),
]
for cid, name, suggested_type, source_line, detail in new_candidates:
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {cid}")
    row = {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": suggested_type, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY}#L{source_line}" if source_line < 90 else f"{NOTES}#L{source_line}",
    }
    candidates.append(row)
    candidate_by_id[cid] = row

segment_lines = {
    BODY: {number: source_lines[number - 1] for number in range(38, 48)},
    NOTES: {number: source_lines[number - 1] for number in range(90, 114)},
}
segment_offsets = {}
for segment_id, lines in segment_lines.items():
    offset = 0
    segment_offsets[segment_id] = {}
    for number, line in lines.items():
        segment_offsets[segment_id][number] = offset
        offset += len(line) + 1

planned_mentions = []
mention_counter = 1


def add_mention(candidate_id, surface, segment_id, source_line, note=""):
    global mention_counter
    if candidate_id not in candidate_by_id:
        raise SystemExit(f"mention candidate missing: {candidate_id}")
    line = segment_lines[segment_id][source_line]
    line_offset = segment_offsets[segment_id][source_line]
    occupied = [
        (int(row["start_char"]), int(row["end_char"]))
        for row in mentions + planned_mentions
        if row["segment_id"] == segment_id
        and line_offset <= int(row["start_char"]) < line_offset + len(line)
    ]
    search_from = 0
    while True:
        pos = line.find(surface, search_from)
        if pos < 0:
            raise SystemExit(f"surface not found on {segment_id} L{source_line}: {surface!r}")
        start = line_offset + pos
        end = start + len(surface)
        if not any(start < old_end and old_start < end for old_start, old_end in occupied):
            break
        search_from = pos + 1
    mention_id = f"m-chp15-p368-querini-{mention_counter:04d}"
    if any(row["mention_id"] == mention_id for row in mentions + planned_mentions):
        raise SystemExit(f"mention ID already exists: {mention_id}")
    planned_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })
    mention_counter += 1


def quote(segment_id, line_start, line_end):
    if line_start > line_end or line_start not in segment_lines[segment_id] or line_end not in segment_lines[segment_id]:
        raise SystemExit(f"quote span outside {segment_id}: L{line_start}-{line_end}")
    return "\n".join(segment_lines[segment_id][n] for n in range(line_start, line_end + 1))


def add_statement(statement_id, subject, obj, predicate, segment_id, line_start, line_end, claim,
                  speaker="Haskell", text_layer="authorial report", qualification="",
                  mentioned=(), **extra):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    qualifiers = {
        "source_line_start": line_start, "source_line_end": line_end,
        "printed_page": 368, "pdf_physical_page": 8,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    qualifiers.update(extra)
    row = {
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote(segment_id, line_start, line_end),
        "origin": "book", "source_file": SOURCE_FILE,
    }
    statements.append(row)
    statement_by_id[statement_id] = row


def footnote(marker, note_line_start, note_line_end, body_line, statement_ids, note=""):
    return {
        "footnote_marker": str(marker), "footnote_segment": NOTES,
        "footnote_line_range": f"L{note_line_start}-L{note_line_end}", "footnote_text_pending": False,
        "footnote_body_link_status": "linked", "footnote_body_line_range": f"L{body_line}",
        "footnote_note_statement_ids": list(statement_ids), "footnote_link_note": note,
    }


# P.367's final climate-and-Prà sentence closes at p.368 L39.
previous = statement_by_id[P367_PARTIAL]
previous["predicate"] = "time_climate_and_summer_conditions_modify_prato_impression"
previous["qualifiers"]["predicate_status"] = "complete"
previous["qualifiers"]["claim"] = (
    "Haskell says time and the Italian climate modified the original impression of the Prà della Valle; "
    "summer vegetation withers and dust removes the effect it originally made as an oasis amid confusion and wilderness."
)
previous["qualifiers"]["qualification"] = (
    "P.367 L36 ends ‘dust robs the Prà della’; p.368 L39 completes the place-name and sentence. "
    "This is Haskell's evaluative description, not an independently verified condition report."
)
previous["qualifiers"]["cross_reference_text"] = "P.367 L36 ‘Prà della’ continues at p.368 L39 ‘Valle of the effect…’."
previous["qualifiers"]["cross_reference_text_pending"] = False


# Body mentions follow OCR offsets; print corrections are recorded below, not written into S0.
add_mention("cand-1804", "Valle", BODY, 39, "Continuation of the p.367 L36 Prà della Valle place-name.")
add_mention("cand-1804", "Pra della Valle", BODY, 40, "The print reads Prà della Valle; the OCR omits the accent.")
add_mention("cand-1642", "Venetian patron", BODY, 40, "The immediate context identifies the patron as Andrea Memmo.")
add_mention("cand-8107", "Enlightenment", BODY, 40)
add_mention("cand-1642", "Memmo", BODY, 41)
add_mention("cand-2829", "Pietro Zaguri", BODY, 41)
add_mention("cand-1411", "Lodoli", BODY, 41)
add_mention("cand-2719", "Venice", BODY, 41)
add_mention("cand-10517", "family palace", BODY, 41)
add_mention("cand-10518", "frescoed gallery", BODY, 41)
add_mention("cand-1646", "paintings", BODY, 41, "Index candidate for Memmo's collection of paintings.")
add_mention("cand-1642", "his brothers", BODY, 41, "The brothers are unnamed; no individual identities are inferred.")
add_mention("cand-1002", "Farsetti", BODY, 44)
add_mention("cand-1642", "Memmo", BODY, 44)
add_mention("cand-2719", "Venice", BODY, 44)
add_mention("cand-1803", "Padua", BODY, 44)
add_mention("cand-2075", "ANGELO QUERINI", BODY, 43, "Section heading in print; OCR layout marks this as the opening of section III.")
add_mention("cand-2075", "Angelo Querini", BODY, 44)
add_mention("cand-8107", "enlightened", BODY, 44, "A stylistic description linked to the existing Enlightenment term candidate.")
add_mention("cand-2075", "his", BODY, 45, "Querini remains the subject from the preceding sentence.")
add_mention("cand-10526", "scholar-gentleman", BODY, 45)
add_mention("cand-1411", "Carlo Lodoli", BODY, 46)
add_mention("cand-1642", "Memmo", BODY, 46)
add_mention("cand-10521", "a foreign ambassador", BODY, 46)
add_mention("cand-10522", "a woman", BODY, 46)
add_mention("cand-10523", "constitutional crisis of 1761", BODY, 46)
add_mention("cand-10524", "State Inquisition", BODY, 47)

# Notes 1–7 for p.368; the notes remain in their consolidated source segment.
add_mention("cand-10474", "Molmenti", NOTES, 97)
add_mention("cand-10475", "Un nobil huomo", NOTES, 97)
add_mention("cand-10512", "Fontana", NOTES, 98)
add_mention("cand-10518", "These", NOTES, 98, "The note's plural referent is not fully explicit; linked cautiously to the preceding gallery passage.")
add_mention("cand-10514", "inventory", NOTES, 99)
add_mention("cand-10525", "Sasso", NOTES, 99, "Only the surname is printed in this note.")
add_mention("cand-2773", "Viero", NOTES, 99)
add_mention("cand-8592", "Archivio di Stato, Venice", NOTES, 99)
add_mention("cand-10514", "Petizion 488", NOTES, 99)
add_mention("cand-10514", "30 Gennaio 1792", NOTES, 100)
add_mention("cand-10514", "24 Febbraio 1792/3 M.V.", NOTES, 100)
add_mention("cand-8533", "Levi, II, p. 254", NOTES, 100, "Citation to the published portion of the inventory; the cited volume is not independently consulted.")
add_mention("cand-1646", "Memmo’s collection", NOTES, 100)
add_mention("cand-1652", "Mengs", NOTES, 100)
add_mention("cand-10519", "drawing of the holy family", NOTES, 100)
add_mention("cand-10513", "Lorenzo da Ponte", NOTES, 101)
add_mention("cand-10520", "Brenta", NOTES, 102)
add_mention("cand-2081", "his garden", NOTES, 102, "Index candidate for Querini's garden; the note does not state the garden's proper name.")
add_mention("cand-10515", "BruneUi Bonetti", NOTES, 102, "OCR form; p.368 print reads Brunelli Bonetti.")
add_mention("cand-1642", "Andrea Memmo", NOTES, 103)
add_mention("cand-1647", "1786", NOTES, 103, "Bibliographic citation to Memmo's 1786 publication; the note itself does not restate the title.")
add_mention("cand-10516", "BozzMa", NOTES, 104, "OCR form; the print reads Bozzola.")

N1 = "st-chp15-p368-note1-memmo-zaguri-reference"
N2 = "st-chp15-p368-note2-gallery-destruction"
N3A = "st-chp15-p368-note3-inventory-record"
N3B = "st-chp15-p368-note3-mengs-drawing-and-prints"
N4 = "st-chp15-p368-note4-open-house-reference"
N5 = "st-chp15-p368-note5-brenta-obstruction-reference"
N6 = "st-chp15-p368-note6-elementi-reference"
N7 = "st-chp15-p368-note7-1761-crisis-reference"
N1_LINK = footnote(1, 97, 97, 41, [N1])
N2_LINK = footnote(2, 98, 98, 41, [N2], "The note's ‘These’ is left with an uncertain plural referent.")
N3_LINK = footnote(3, 99, 100, 41, [N3A, N3B])
N4_LINK = footnote(4, 101, 101, 41, [N4])
N5_LINK = footnote(5, 102, 102, 45, [N5])
N6_LINK = footnote(6, 103, 103, 46, [N6])
N7_LINK = footnote(7, 104, 104, 46, [N7])

add_statement(
    "st-chp15-p368-prato-effect-of-decay", "cand-1804", None,
    "decay_changed_prato_valle_inscriptions_figures_and_weaker_sculpture", BODY, 39, 40,
    "Haskell says the inscriptions were worn, figures had retreated into anonymity, and weaker sculptures had gained from general decay; he contrasts this with the site's original oasis-like effect.",
    qualification="The description is Haskell's retrospective evaluation; no independent site survey is used.",
    mentioned=["cand-1804"], cross_reference_segments=[BODY_PREV],
    cross_reference_text="Completes the p.367 sentence that dust robs the Prà della Valle of its original effect.",
    cross_reference_text_pending=False)
add_statement(
    "st-chp15-p368-prato-beauty-utility-and-enlightenment", "cand-1804", "cand-8107",
    "pra_del_valle_as_attempt_to_combine_beauty_and_utility", BODY, 40, 40,
    "Haskell calls the Prà della Valle one of the most noble attempts by a Venetian patron to combine beauty with utility and solve a problem that occupied Enlightenment thinkers.",
    qualification="This is Haskell's evaluation of the project, not a claim that the problem was objectively solved.",
    mentioned=["cand-1804", "cand-1642", "cand-8107"])
add_statement(
    "st-chp15-p368-memmo-zaguri-lodoli-controversy", "cand-1642", "cand-2829",
    "friendly_controversy_over_lodoli_merits", BODY, 41, 41,
    "Haskell says Andrea Memmo had a friendly controversy with Pietro Zaguri over Carlo Lodoli's merits and remained passionately faithful to Lodoli's memory.",
    mentioned=["cand-1642", "cand-2829", "cand-1411"], **N1_LINK)
add_statement(
    "st-chp15-p368-memmo-political-ambition-declines", "cand-1642", "cand-2719",
    "political_ambitions_declined_with_venice_fortunes", BODY, 41, 41,
    "Haskell says Memmo's political ambitions declined as Venice's fortunes declined.",
    mentioned=["cand-1642", "cand-2719"])
add_statement(
    "st-chp15-p368-memmo-palace-frescoed-gallery", "cand-1642", "cand-10518",
    "family_palace_decorated_with_frescoed_gallery", BODY, 41, 41,
    "Haskell says Memmo had the family palace decorated with a frescoed gallery of classical orators, poets and philosophers, each named on a pedestal.",
    qualification="The palace's location and the artists who executed the decoration are not identified.",
    mentioned=["cand-1642", "cand-10517", "cand-10518"], **N2_LINK)
add_statement(
    "st-chp15-p368-memmo-forty-eight-paintings", "cand-1642", "cand-1646",
    "owned_about_48_paintings_mostly_copies", BODY, 41, 41,
    "Haskell says Memmo seems to have had little interest in paintings and owned only forty-eight, mostly copies.",
    qualification="Haskell's ‘seems’ is retained; the inventory was not independently consulted.",
    mentioned=["cand-1642", "cand-1646"], **N3_LINK)
add_statement(
    "st-chp15-p368-memmo-open-house-until-death", "cand-1642", None,
    "held_open_house_for_advanced_spirits_until_1792", BODY, 41, 41,
    "Haskell says Memmo held open house in the palace with his brothers for more advanced spirits of the day until his death in 1792.",
    qualification="The brothers and visitors are unnamed; no membership list or individual identity is inferred.",
    mentioned=["cand-1642"], **N4_LINK)
add_statement(
    "st-chp15-p368-farsetti-memmo-public-service-patronage", "cand-1002", "cand-1642",
    "patronage_bound_to_public_service_in_venice_and_padua", BODY, 44, 44,
    "Haskell characterizes Farsetti and Memmo as patrons whose arts patronage was inseparable from service to the public life of Venice and Padua.",
    mentioned=["cand-1002", "cand-1642", "cand-2719", "cand-1803"])
add_statement(
    "st-chp15-p368-querini-emerges-as-major-venetian-patron", "cand-2075", None,
    "last_important_patron_to_emerge_in_venice", BODY, 44, 45,
    "Haskell calls Angelo Querini the last important patron to emerge in Venice and says his enlightened views went further than those of Farsetti and Memmo.",
    qualification="‘Last important’ and the comparison are Haskell's historical evaluation.",
    mentioned=["cand-2075", "cand-1002", "cand-1642", "cand-2719", "cand-8107"])
add_statement(
    "st-chp15-p368-querini-private-art-public-interest", "cand-2075", None,
    "confined_art_interest_to_private_use_and_accused_of_self_interest", BODY, 44, 45,
    "Haskell says Querini confined his love of art to private use and was accused of advancing his own interests at public expense.",
    qualification="The accusation is reported by Haskell; its basis and the accusers are not identified on this page.",
    mentioned=["cand-2075"], **N5_LINK)
add_statement(
    "st-chp15-p368-querini-scholar-gentleman-ideal", "cand-2075", "cand-10526",
    "later_life_as_example_of_scholar_gentleman_ideal", BODY, 45, 45,
    "Haskell presents Querini's later life as an example of a recurring scholar-gentleman ideal: cultivated taste, quiet estate life and detachment from the world.",
    qualification="This is Haskell's interpretive characterization, not an institutional or occupational classification.",
    mentioned=["cand-2075", "cand-10526"])
add_statement(
    "st-chp15-p368-querini-born-and-admired-lodoli", "cand-2075", "cand-1411",
    "born_1721_and_early_admirer_of_lodoli", BODY, 46, 46,
    "Haskell says Querini was born in 1721 and had been a keen admirer of Carlo Lodoli.",
    mentioned=["cand-2075", "cand-1411"], **N6_LINK)
add_statement(
    "st-chp15-p368-querini-informed-memmo-about-lodoli", "cand-2075", "cand-1642",
    "gave_memmo_information_about_lodoli_early_years", BODY, 46, 46,
    "Haskell says Querini gave Memmo much information about Lodoli's earlier years.",
    mentioned=["cand-2075", "cand-1642", "cand-1411"], **N6_LINK)
add_statement(
    "st-chp15-p368-querini-possible-ambassador-association", "cand-2075", "cand-10521",
    "political_difficulty_after_possible_association_with_foreign_ambassador", BODY, 46, 46,
    "Haskell says Querini encountered difficulties with the authorities because of a possible association with a foreign ambassador, while suggesting the association concerned a woman rather than politics.",
    qualification="Both the association and the explanation retain Haskell's uncertainty (‘possible’ and ‘perhaps’); the ambassador and woman remain unidentified.",
    mentioned=["cand-2075", "cand-10521", "cand-10522"])
add_statement(
    "st-chp15-p368-querini-leading-role-1761-crisis", "cand-2075", "cand-10523",
    "leading_part_in_1761_constitutional_crisis", BODY, 46, 46,
    "Haskell says Querini first achieved notoriety during the constitutional crisis of 1761, in which he played the leading part.",
    mentioned=["cand-2075", "cand-10523"], **N7_LINK)
add_statement(
    "st-chp15-p368-querini-state-inquisition-dispute-partial", "cand-2075", "cand-10524",
    "dispute_over_state_inquisition_powers_continues_partial", BODY, 47, 47,
    "Haskell begins to describe a dispute over the powers of the State Inquisition that Querini wished to...",
    qualification="The sentence breaks at the page end after ‘wished to’; the requested change and outcome are pending p.369.",
    mentioned=["cand-2075", "cand-10524"], predicate_status="partial",
    cross_reference_segments=[BODY_NEXT], cross_reference_text="P.368 L47 ends ‘which Querini wished to’; continue with p.369.",
    cross_reference_text_pending=True)

# The following note statements preserve Haskell's citation trail, not independent source verification.
add_statement(
    N1, None, "cand-10475", "note_cites_molmenti_un_nobil_huomo", NOTES, 97, 97,
    "Haskell cites Molmenti, Un nobil huomo, pages 137 onward, for the p.368 discussion.",
    speaker="Haskell's note", text_layer="bibliographic citation", qualification="The cited work was not independently consulted.",
    mentioned=["cand-10474", "cand-10475"], cited_source_independently_consulted=False, **N1_LINK)
add_statement(
    N2, "cand-10518", None, "gallery_or_decoration_destroyed_about_1960", NOTES, 98, 98,
    "Haskell's note cites Fontana, page 142, and says ‘These’ were destroyed about 1960.",
    speaker="Haskell's note", text_layer="bibliographic citation", qualification="The plural referent of ‘These’ is not explicit; do not assert that the entire palace or gallery was destroyed.",
    mentioned=["cand-10512", "cand-10518"], cited_source_independently_consulted=False, **N2_LINK)
add_statement(
    N3A, None, "cand-10514", "1792_memmo_effects_inventory_in_venice_state_archive", NOTES, 99, 100,
    "Haskell identifies an inventory of Memmo's effects drawn up by Sasso and Viero in the Archivio di Stato in Venice, Petizion 488, with entries dated 30 January 1792 and 24 February 1792/3 M.V.; part was published by Levi, volume II, page 254.",
    speaker="Haskell's note", text_layer="bibliographic citation", qualification="The archive, inventory and publication were not independently consulted; Sasso is identified by surname only.",
    mentioned=["cand-10514", "cand-10525", "cand-2773", "cand-8592", "cand-8532", "cand-8533"],
    cited_source_independently_consulted=False, **N3_LINK)
add_statement(
    N3B, "cand-10514", "cand-10519", "inventory_lists_mengs_holy_family_drawing_and_many_prints", NOTES, 100, 100,
    "Haskell says the inventory includes a drawing of the Holy Family by Mengs and that Memmo also owned several hundred prints, rarely with the artist indicated.",
    speaker="Haskell's note", text_layer="authorial report of an inventory", qualification="The inventory was not independently examined; the drawing's present location is not given.",
    mentioned=["cand-10514", "cand-1646", "cand-1652", "cand-10519"], **N3_LINK)
add_statement(
    N4, None, "cand-10513", "note_cites_lorenzo_da_ponte_page_52", NOTES, 101, 101,
    "Haskell cites Lorenzo da Ponte, page 52, for the p.368 account of Memmo's open house.",
    speaker="Haskell's note", text_layer="bibliographic citation", qualification="The cited work and bibliographic role were not independently checked.",
    mentioned=["cand-10513"], cited_source_independently_consulted=False, **N4_LINK)
add_statement(
    N5, "cand-2075", "cand-10520", "accused_of_obstructing_brenta_flood_control_due_to_garden", NOTES, 102, 102,
    "Haskell says Querini was accused of obstructing plans to stop flooding of the Brenta because the plans threatened his garden.",
    speaker="Haskell's note", text_layer="authorial report of a cited account", qualification="The accusation is attributed to Haskell's citation chain and was not independently checked.",
    mentioned=["cand-2075", "cand-10520", "cand-2081", "cand-10515"], cited_source_independently_consulted=False, **N5_LINK)
add_statement(
    N6, None, "cand-1647", "note_cites_memmo_elementi_1786_page_29", NOTES, 103, 103,
    "Haskell cites [Andrea Memmo], 1786, page 29, note 1, for the p.368 information about Lodoli's earlier years.",
    speaker="Haskell's note", text_layer="bibliographic citation", qualification="The edition was not independently consulted.",
    mentioned=["cand-1642", "cand-1647"], cited_source_independently_consulted=False, **N6_LINK)
add_statement(
    N7, None, "cand-10516", "note_cites_bozzola_1948_pages_93_116", NOTES, 104, 104,
    "Haskell cites Bozzola, 1948, pages 93–116, for the p.368 account of Querini's role in the 1761 crisis.",
    speaker="Haskell's note", text_layer="bibliographic citation", qualification="The cited work was not independently consulted; the print reads Bozzola where OCR reads BozzMa.",
    mentioned=["cand-10516"], cited_source_independently_consulted=False, **N7_LINK)

# Print review confirms OCR-only errors; S0 source transcription remains untouched.
previous["qualifiers"]["print_checked"] = True
previous["qualifiers"]["printed_page"] = 367

coverage_by_id[BODY_PREV].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L31-36",
    "note": "P.368 L39 closes the p.367 climate-and-Prà della Valle sentence; print corrections are recorded in S2 only.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L39-47",
    "note": "Printed p.368 checked against CHP-15.pdf physical p.8. Processes the close of the Prà della Valle account, Memmo's later life and collection, and Angelo Querini's opening account. L47 breaks mid-sentence at ‘wished to’ and continues at p.369. Notes 1–7 at consolidated L97–104 are migrated. Print corrections are recorded in S2 only; S0 unchanged.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L91-104",
    "note": "P.365 notes 1–2 at L91–92, p.367 notes 1–4 at L93–96, and p.368 notes 1–7 at L97–104 are migrated. Remaining notes L105–113 belong to later pages and remain pending.",
})

expected_statement_count = 24
new_statement_ids = [sid for sid in statement_by_id if sid.startswith("st-chp15-p368-")]
if len(new_candidates) != 15 or len(planned_mentions) != 49 or len(new_statement_ids) != expected_statement_count:
    raise SystemExit(f"count guard failed: candidates={len(new_candidates)}, mentions={len(planned_mentions)}, statements={len(new_statement_ids)}")

result = {
    "mode": "apply" if args.apply else "dry-run",
    "source_sha256": SOURCE_SHA, "pdf_sha256": PDF_SHA,
    "new_candidates": len(new_candidates), "new_mentions": len(planned_mentions),
    "new_statements": len(new_statement_ids), "updated_statements": [P367_PARTIAL],
    "coverage_updates": {sid: coverage_by_id[sid] for sid in (BODY_PREV, BODY, NOTES)},
    "printed_page": 368, "pdf_physical_page": 8,
    "open_cross_page_statement": "st-chp15-p368-querini-state-inquisition-dispute-partial",
}
if args.apply:
    touched = [candidate_path, mention_path, statement_path, coverage_path]
    backups = [(path, path.with_name(path.name + BACKUP_SUFFIX)) for path in touched]
    collision = next((backup for _, backup in backups if backup.exists()), None)
    if collision:
        raise SystemExit(f"backup already exists: {collision.name}")
    for path, backup in backups:
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions + planned_mentions)
    write_jsonl(statement_path, statements)
    write_csv(coverage_path, coverage_fields, coverage)
print(json.dumps(result, ensure_ascii=False, indent=2))
