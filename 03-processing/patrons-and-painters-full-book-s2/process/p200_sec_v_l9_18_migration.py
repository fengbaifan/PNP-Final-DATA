"""Controlled S2 migration for the p.200 section V segment.

Default invocation is a read-only dry run. Apply only after reviewing the
semantic payload, scan corrections, and generated source spans.
"""
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
SOURCE_REL = "02-sources/02-Markdown/07_CHP-7_sec_v.md"
SOURCE_PATH = ROOT / SOURCE_REL
SEGMENT_ID = "chp-7:07_CHP-7_sec_v:l9-18"
PREVIOUS_SEGMENT_ID = "chp-7:07_CHP-7_sec_v:l3-7"
BODY_CONTINUATION_SEGMENT_ID = "chp-7:07_CHP-7_sec_v:l42-55"
LINE_START = 9
LINE_END = 18
PRINTED_PAGE = 200
PDF_PHYSICAL_PAGE = 38

CANDIDATE_PATH = TABLES / "entity-candidates.csv"
MENTION_PATH = TABLES / "mentions.csv"
STATEMENT_PATH = TABLES / "book-statements.jsonl"
COVERAGE_PATH = TABLES / "s2-coverage.csv"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


source_lines = SOURCE_PATH.read_text(encoding="utf-8-sig").splitlines()
segment_records = [
    json.loads(line)
    for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8").splitlines()
    if line
]
segment_record = next(row for row in segment_records if row.get("segment_id") == SEGMENT_ID)
if segment_record["source_file"] != SOURCE_REL:
    raise SystemExit("segment source_file differs from the current S0 record")
if segment_record["line_start"] != LINE_START or segment_record["line_end"] != LINE_END:
    raise SystemExit("segment bounds differ from the current S0 record")
if hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest() != segment_record["asset_sha256"]:
    raise SystemExit("source asset fingerprint changed; stop and review the affected source")
segment_text = "\n".join(source_lines[LINE_START - 1 : LINE_END])

candidate_fields, candidate_rows = read_csv(CANDIDATE_PATH)
mention_fields, mention_rows = read_csv(MENTION_PATH)
coverage_fields, coverage_rows = read_csv(COVERAGE_PATH)
statement_rows = [
    json.loads(line)
    for line in STATEMENT_PATH.read_text(encoding="utf-8").splitlines()
    if line
]

coverage = next((row for row in coverage_rows if row["segment_id"] == SEGMENT_ID), None)
if coverage is None or coverage["disposition"] != "queued":
    raise SystemExit(f"expected a queued coverage row for {SEGMENT_ID}")
if any(row["segment_id"] == SEGMENT_ID for row in mention_rows):
    raise SystemExit(f"mentions already exist for {SEGMENT_ID}; inspect before rerunning")
if any(row["segment_id"] == SEGMENT_ID for row in statement_rows):
    raise SystemExit(f"statements already exist for {SEGMENT_ID}; inspect before rerunning")


def candidate(candidate_id, name, entity_type, detail, line):
    return {
        "candidate_id": candidate_id,
        "index_entry_id": "",
        "canonical_name": name,
        "index_page_range": "",
        "suggested_type": entity_type,
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": detail,
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L{line}",
    }


new_candidates = [
    candidate("cand-7282", "Victor Amadeus of Savoy (named in the p.200 political transition account)", "person",
              "New source-derived person candidate. Haskell says he broke from Louis XIV's tutelage and emerged as the leading independent ruler in Italy; identity/title normalization is for S3.", 10),
    candidate("cand-7283", "Lombardy (territory named in the Austrian conquest account)", "place",
              "Geographic territory named as conquered by the Austrians; the source does not specify its boundaries or administrative status here.", 10),
    candidate("cand-7284", "Austria as political-military actor in the p.200 account", "institution",
              "Source-derived polity/force candidate for 'the Austrians' and Austrian authority. Keep separate from the existing geographic Austria candidate pending S3.", 10),
    candidate("cand-7285", "Admiral ‘Pekemburgh’ (Haskell's spelling; identity unresolved)", "person",
              "Haskell names an English admiral who entered Genoa before 1703 and commissioned a bust from Domenico Parodi. Footnote 1 is in a later composite source segment and remains to be migrated; do not merge in S2.", 11),
    candidate("cand-7286", "Philip V (French candidate for the Spanish throne in Haskell's account)", "person",
              "The source identifies him by regnal name and role only. Keep distinct pending S3 identity alignment.", 12),
    candidate("cand-7287", "Versailles (site associated with the ‘official’ style in Haskell's account)", "place",
              "Place named as the setting associated with the official style that younger art lovers were tiring of; the style itself is a separate concept.", 13),
    candidate("cand-7288", "Military commanders of the warring nations (unnamed collective)", "term",
              "Haskell's collective category for commanders who commissioned local artists between campaigns; the passage then gives examples.", 11),
    candidate("cand-7289", "Local artists serving commanders in many cities (unnamed collective)", "term",
              "Generalized group in Haskell's account of commissions during campaign pauses; no complete membership or city-to-artist mapping is supplied.", 11),
    candidate("cand-7290", "Younger generation of art lovers associated with interest in contemporary Italian painting (unnamed group)", "term",
              "Unnamed audience group said by Haskell to have become interested in contemporary Italian painting and tired of the official style at Versailles.", 13),
    candidate("cand-7291", "Influential nobles and bankers in Paris introduced to Paolo de Matteis (unnamed group)", "term",
              "The source does not name the individuals or assign them separate patronage acts.", 12),
    candidate("cand-7292", "Opposing forces that captured Naples (unnamed collective)", "term",
              "Haskell refers to the captors only as opposing forces; their full composition is not specified in this segment.", 13),
    candidate("cand-7293", "Capture of Naples in the p.200 account (date and forces not fully specified here)", "event",
              "The source says Naples was conquered by opposing forces and attributes responsibility for its capture to Count Daun; do not add a date or coalition beyond the wording in this segment.", 13),
    candidate("cand-7294", "Austrian regime in Naples established after the capture (unnamed)", "institution",
              "Haskell calls Daun the first viceroy of the new regime in 1707 but does not give the regime a formal name.", 13),
    candidate("cand-7295", "Spanish predecessors as viceroys of Naples (unnamed group)", "term",
              "Haskell compares Daun's patronage with his Spanish predecessors without naming the individual officeholders.", 13),
    candidate("cand-7296", "Giacomo del Po (person named in Haskell's p.200 account)", "person",
              "New source-derived person candidate; identity and cross-chapter alignment remain for S3.", 14),
    candidate("cand-7297", "Bust commissioned by Admiral ‘Pekemburgh’ from Domenico Parodi (unidentified work)", "work",
              "A portrait bust is described as a commissioned work, but no sitter inscription, title, date, or present location is supplied.", 11),
    candidate("cand-7298", "Pictures Gregorio de Ferrari painted for Maréchal de Noailles at Marseilles (unidentified group)", "work",
              "The source refers to some pictures collectively and does not identify individual works.", 11),
    candidate("cand-7299", "Count Daun's palace in Vienna (unnamed building)", "place",
              "The source calls it his palace; no formal name or exact address is given.", 14),
    candidate("cand-7300", "Canvases by Solimena, Giacomo del Po, and Paolo de Matteis for Count Daun's Viennese palace (unidentified group)", "work",
              "Haskell describes canvases collectively as palace decoration without identifying titles or one-to-one artist assignments.", 14),
    candidate("cand-7301", "Admiral ‘Binchs’ (Haskell's source form; identity claim deferred)", "person",
              "Kept as Haskell's source form. Footnote 5 is in a later composite source segment and will be migrated before any identity decision.", 13),
    candidate("cand-7302", "Portrait of Count Daun by Vittore Ghislandi (unidentified work)", "work",
              "Footnote 6 says Daun commissioned his portrait in Bergamo; no title, date, or present location is given.", 18),
    candidate("cand-7303", "High commanders of Italian origin serving in the Imperial army (unnamed group)", "term",
              "The p.200 sentence begins a distinct collective account and remains open at 'furnishing'; it continues after intervening plates on p.201.", 17),
    candidate("cand-7304", "Imperial army in Haskell's p.200–201 account", "institution",
              "Military organization named as the service of the Italian-origin commanders. Formal historical identity is not resolved here.", 17),
    candidate("cand-7305", "‘Official’ style associated with Versailles in Haskell's p.200 account", "term",
              "A quoted stylistic characterization attributed to Haskell; the passage does not define a formal school or style name.", 13),
]

new_candidate_ids = {row["candidate_id"] for row in new_candidates}
existing_candidate_ids = {row["candidate_id"] for row in candidate_rows}
if new_candidate_ids & existing_candidate_ids:
    raise SystemExit("one or more planned candidate IDs already exist")
if max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows) != 7281:
    raise SystemExit("candidate table advanced from the expected ID boundary; reassign new IDs")

# surface, candidate ID, note, source line numbers
mention_specs = [
    ("war of the Spanish succession", "cand-2502", "Closes the open chronological phrase from p.199; the existing event candidate is reused.", [10]),
    ("Victor Amadeus", "cand-7282", "Source-derived ruler candidate; title and historical identity alignment remain for S3.", [10]),
    ("Savoy", "cand-2379", "Territory/title named in the person reference; the state and geographical referents remain for S3.", [10]),
    ("Louis XIV", "cand-1447", "Existing index candidate; Haskell describes Victor Amadeus as breaking from his tutelage.", [10]),
    ("The Austrians", "cand-7284", "Political-military actor in the conquest statement, not the geographic Austria candidate.", [10]),
    ("Lombardy", "cand-7283", "Geographic territory named in the conquest claim.", [10]),
    ("Naples", "cand-3534", "Existing place candidate; in L10 it is the object of seizure, and later mentions refer to the city.", [10, 11, 13, 15]),
    ("Spaniards", "cand-4591", "Political-military group associated with Spain; this is not the geographic place candidate.", [10]),
    ("Treaties of Utrecht", "cand-2672", "Existing treaty candidate; Haskell says the treaties confirmed political changes.", [10]),
    ("Rastatt", "cand-2109", "Existing Treaty of Rastatt candidate.", [10]),
    ("Italy", "cand-3461", "Existing geographic candidate; Haskell calls Victor Amadeus a leading ruler in Italy.", [10]),
    ("Italian art", "cand-4131", "Existing concept candidate; the passage links political change with changes in patronage, and the footnote later characterizes Orléans's patronage.", [10, 13, 18]),
    ("Military commanders of all the warring nations", "cand-7288", "Collective category in Haskell's generalization.", [11]),
    ("campaigns", "cand-2502", "The pauses are within the account of the War of the Spanish Succession; no separate campaign event is named.", [11]),
    ("local talent", "cand-7289", "Unnamed local artists collectively serving commanders.", [11]),
    ("artists in many cities", "cand-7289", "Anaphoric expansion of the unnamed local artists group.", [11]),
    ("Admiral ‘Pekemburgh’", "cand-7285", "Keep Haskell's printed spelling separate from the possible Peterborough identification in note 1.", [11]),
    ("Genoa", "cand-1131", "Index candidate with p.200 coverage.", [11]),
    ("English ships", "cand-7200", "England is the national affiliation of the ships in Haskell's wording.", [11]),
    ("Domenico Parodi", "cand-1841", "Existing index candidate for the sculptor.", [11]),
    ("his bust", "cand-7297", "The commissioned portrait bust is an unidentified work; his refers to Admiral Pekemburgh.", [11]),
    ("England", "cand-7200", "Existing geographic candidate; destination in the unsuccessful attempt to take Parodi back.", [11]),
    ("Maréchal de Noailles", "cand-1742", "Existing index candidate; Haskell says he arrived soon after Pekemburgh.", [11]),
    ("Gregorio de Ferrari", "cand-1021", "Existing index candidate for the painter.", [11]),
    ("Marseilles", "cand-7093", "Existing place candidate.", [11]),
    ("some pictures for him", "cand-7298", "Unidentified group of pictures; him refers to Noailles.", [11]),
    ("Duc d’Estrées", "cand-0983", "Existing index candidate; exact person-to-title identity remains for S3.", [11]),
    ("Philip V", "cand-7286", "Source-derived person candidate; described as the French candidate for the Spanish throne.", [12]),
    ("Spanish throne", "cand-4591", "Polity/monarchy context, not a separate physical throne object.", [12]),
    ("Paolo de Matteis", "cand-1581", "Existing index person candidate; repeated mentions are anchored separately.", [12, 13, 14]),
    ("Paris", "cand-4653", "Existing place candidate.", [13]),
    ("influential nobles and bankers", "cand-7291", "Unnamed group introduced to de Matteis; no individual patrons are named.", [13]),
    ("contemporary Italian painting", "cand-4131", "Haskell's subject in the interest-shift statement.", [13]),
    ("younger generation of art lovers", "cand-7290", "Unnamed audience group in Haskell's interpretation.", [13]),
    ("‘official’ style", "cand-7305", "Quoted stylistic characterization; source associates it with Versailles.", [13]),
    ("Versailles", "cand-7287", "Place associated with the source's phrase ‘official’ style.", [13]),
    ("the city", "cand-3534", "Anaphora to Naples.", [13]),
    ("opposing forces", "cand-7292", "Unnamed forces said to have conquered Naples.", [13]),
    ("English Admiral ‘Binchs’", "cand-7301", "Keep the source-form admiral separate from Admiral Byng until S3.", [13]),
    ("Austrian", "cand-7284", "Nationality/political affiliation attached to Count Daun and the new regime.", [13, 15]),
    ("Count Daun", "cand-0906", "Existing index candidate; the passage attributes capture, viceroyalty, and patronage to him.", [13, 14, 15]),
    ("its capture", "cand-7293", "Anaphora to the conquest of Naples described in this passage.", [13]),
    ("the new regime", "cand-7294", "Unnamed Austrian regime in Naples; no formal title supplied.", [13]),
    ("Spanish predecessors", "cand-7295", "Unnamed prior viceroys; Haskell makes a comparative patronage claim.", [13]),
    ("Solimena", "cand-2484", "Existing index candidate for Francesco Solimena.", [14]),
    ("Giacomo del Po", "cand-7296", "New source-derived person candidate.", [14]),
    ("canvases", "cand-7300", "Unidentified canvases collectively described as palace decoration.", [14]),
    ("his palace", "cand-7299", "Unspecified palace belonging to Count Daun in the source account.", [14]),
    ("Vienna", "cand-2772", "Existing index candidate; place of Daun's palace.", [14]),
    ("Marc’antonio Chiarini", "cand-0662", "Existing index candidate; S0's form is retained, with capitalization normalization deferred.", [14]),
    ("his first appointment", "cand-0906", "Anaphora to Count Daun's appointment in Naples.", [15]),
    ("Neapolitan painting", "cand-1729", "Existing index candidate; Haskell describes its introduction into Central Europe.", [15]),
    ("Central Europe", "cand-6762", "Existing place candidate.", [15]),
    ("Austrian viceroys", "cand-7284", "Collective officeholders of the Austrian regime; Count Harrach is named as the later example.", [16]),
    ("Count Harrach", "cand-1291", "Existing index candidate.", [16]),
    ("these men", "cand-7288", "Anaphoric reference to the commanders just discussed; the next sentence introduces additional commanders.", [17]),
    ("high commanders of Italian origin", "cand-7303", "New unnamed collective; sentence remains open at the end of this segment.", [17]),
    ("Imperial army", "cand-7304", "Military organization named as the service of the Italian-origin commanders.", [17]),
    ("they", "cand-7303", "Anaphora to the high commanders of Italian origin.", [17]),
    ("he", "cand-0906", "Footnote 6's pronoun refers to Count Daun, the subject of the immediately preceding body passage.", [18]),
    ("ibid.", "cand-4835", "Note 6 continues the de Dominici reference from note 5.", [18]),
    ("Pascoli, H", "cand-4552", "S0 OCR reads H; the page image reads II. The mention span preserves the source text, and the correction is recorded in S2.", [18]),
    ("Zanotti, I", "cand-7115", "Bibliographic pointer to volume I, p.277; cited page not independently read.", [18]),
    ("Bergamo", "cand-6208", "Place named as the portrait commission location.", [18]),
    ("Vittore Gliislandi", "cand-1101", "OCR surface form; the scan reads Vittore Ghislandi. Correction is recorded only in S2.", [18]),
    ("Tassi, II", "cand-6590", "Bibliographic pointer to volume II, p.64; cited page not independently read.", [18]),
]


def statement(statement_id, start, end, predicate, claim, qualification,
              subject=None, obj=None, mentioned=(), quote=None, speaker="Haskell",
              text_layer="body", extra=None):
    qualifiers = {
        "source_line_start": start,
        "source_line_end": end,
        "printed_page": PRINTED_PAGE,
        "pdf_physical_page": PDF_PHYSICAL_PAGE,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": list(mentioned),
    }
    if extra:
        qualifiers.update(extra)
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote or "\n".join(source_lines[start - 1 : end]),
        "origin": "book",
        "source_file": SOURCE_REL,
    }


def cite(statement_id, quote, object_candidate_id, marker, linked_body_ids, qualification):
    return statement(
        statement_id, 18, 18, "footnote_citation",
        f"The note cites {quote}.",
        qualification,
        obj=object_candidate_id,
        mentioned=[object_candidate_id],
        quote=quote,
        speaker="Haskell footnote",
        text_layer="bibliographic pointer",
        extra={
            "footnote_marker": marker,
            "footnote_segment": SEGMENT_ID,
            "related_segment": SEGMENT_ID,
            "related_source_lines": [13],
            "linked_body_statement_ids": linked_body_ids,
        },
    )


statements = [
    statement("st-chp7-p200-v-victor-amadeus-breaks-from-louis-xiv", 10, 10,
              "political_independence_emerges",
              "Haskell says Victor Amadeus of Savoy broke loose from Louis XIV's tutelage and, after tortuous manoeuvres, emerged as Italy's leading independent ruler.",
              "This is Haskell's political characterization; keep the transition and superlative attributed to the author.",
              subject="cand-7282", obj="cand-3461", mentioned=["cand-7282", "cand-2379", "cand-1447", "cand-3461"],
              quote="Victor Amadeus of Savoy broke loose from the tutelage of Louis XIV and after a series of tortuous' manoeuvres finally emerged as the leading independent ruler in Italy."),
    statement("st-chp7-p200-v-austrians-conquer-lombardy", 10, 10,
              "conquered", "Haskell states that the Austrians conquered Lombardy.",
              "The claim is recorded as the book reports it; no independent historical verification is implied.",
              subject="cand-7284", obj="cand-7283", mentioned=["cand-7284", "cand-7283"],
              quote="The Austrians conquered Lombardy"),
    statement("st-chp7-p200-v-austrians-seize-naples-from-spaniards", 10, 10,
              "seized", "Haskell states that the Austrians seized Naples from the Spaniards.",
              "Keep the political-military actors distinct from the geographic places and preserve the source's wording.",
              subject="cand-7284", obj="cand-3534", mentioned=["cand-7284", "cand-3534", "cand-4591"],
              quote="and seized Naples from the Spaniards."),
    statement("st-chp7-p200-v-treaties-confirm-changes-and-patronage-counterpart", 10, 10,
              "treaties_confirmed_political_changes_with_patronage_counterpart",
              "Haskell says the changes were confirmed by the Treaties of Utrecht and Rastatt in 1713 and 1714 and had counterparts in the patronage of Italian art.",
              "Preserve the correspondence as Haskell's interpretation; do not imply that the treaties themselves caused a particular commission.",
              subject="cand-2672", obj="cand-4131", mentioned=["cand-2672", "cand-2109", "cand-4131", "cand-2502"],
              quote="These changes, which were confirmed by the Treaties of Utrecht and Rastatt in 1713 and 1714, had their counterparts in the patronage of Italian art."),
    statement("st-chp7-p200-v-commanders-commission-local-artists", 11, 11,
              "commanders_commission_local_art_between_campaigns",
              "Haskell generalizes that commanders of the warring nations used pauses between campaigns to commission local artists, who served them with fine impartiality in many cities.",
              "This is an authorial generalization. It does not assign a specific artist to each commander or city.",
              subject="cand-7288", obj="cand-7289", mentioned=["cand-7288", "cand-7289", "cand-2502"],
              quote="Military commanders of all the warring nations took advantage of the fleeting opportunities between campaigns to commission local talent and were served with fine impartiality by artists in many cities."),
    statement("st-chp7-p200-v-pekemburgh-arrives-genoa", 11, 11,
              "arrived_with_english_squadron", "Haskell says Admiral ‘Pekemburgh’ sailed into Genoa with a squadron of English ships sometime before 1703.",
              "The date is before 1703, not a precise year; preserve the printed name form pending the qualified identification in note 1.",
              subject="cand-7285", obj="cand-1131", mentioned=["cand-7285", "cand-1131", "cand-7200", "cand-2502"],
              quote="There was Admiral ‘Pekemburgh’, for instance, who sailed into Genoa with a squadron of English ships sometime before 1703"),
    statement("st-chp7-p200-v-pekemburgh-commissions-parodi-bust", 11, 11,
              "commissioned_portrait_bust_from", "Haskell says Admiral ‘Pekemburgh’ ordered his bust from the sculptor Domenico Parodi.",
              "The bust is not identified by title, date, or location; it remains an unidentified work candidate.",
              subject="cand-7285", obj="cand-7297", mentioned=["cand-7285", "cand-1841", "cand-7297"],
              quote="ordered his bust from the sculptor Domenico Parodi", extra={"footnote_marker": 1}),
    statement("st-chp7-p200-v-parodi-trip-to-england-failed", 11, 11,
              "attempted_to_take_artist_to_england_unsuccessfully",
              "Haskell says Pekemburgh tried in vain to take Parodi back with him to England.",
              "This is an unsuccessful attempt, not a completed move or employment.",
              subject="cand-7285", obj="cand-1841", mentioned=["cand-7285", "cand-1841", "cand-7200"],
              quote="whom he then tried in vain to take back with him to England"),
    statement("st-chp7-p200-v-noailles-secures-de-ferrari-at-marseilles", 11, 11,
              "persuaded_artist_to_paint_for_him",
              "Haskell says Maréchal de Noailles arrived soon after Pekemburgh and persuaded Gregorio de Ferrari to come to Marseilles and paint pictures for him there.",
              "The pictures are not individually identified; preserve the sequence ‘soon after’ without assigning a year.",
              subject="cand-1742", obj="cand-7298", mentioned=["cand-1742", "cand-1021", "cand-7093", "cand-7298", "cand-7288"],
              quote="the French Maréchal de Noailles who arrived soon after and was more successful in persuading Gregorio de Ferrari to come to Marseilles and paint some pictures for him there"),
    statement("st-chp7-p200-v-destrees-visits-naples-with-philip-v", 11, 12,
              "visited_with_claimant", "Haskell says the Duc d’Estrées visited Naples with Philip V, whom he describes as the French candidate for the Spanish throne.",
              "This records the source's political description and does not independently resolve the succession claim.",
              subject="cand-0983", obj="cand-3534", mentioned=["cand-0983", "cand-3534", "cand-7286", "cand-4591"],
              quote="or the Duc d’Estrées who visited Naples with\nPhilip V, French candidate for the Spanish throne"),
    statement("st-chp7-p200-v-destrees-takes-paolo-to-paris", 12, 13,
              "took_painter_to_paris", "Haskell says d’Estrées was struck by Paolo de Matteis and took him to Paris.",
              "The source describes a journey and patronal interest; it does not state that de Matteis settled in Paris.",
              subject="cand-0983", obj="cand-1581", mentioned=["cand-0983", "cand-1581", "cand-4653"],
              quote="and was so struck by Paolo de\nMatteis that he took him back to Paris"),
    statement("st-chp7-p200-v-destrees-introduces-paolo-to-nobles-bankers", 13, 13,
              "introduced_painter_to_potential_patrons", "Haskell says d’Estrées introduced de Matteis to influential nobles and bankers in Paris.",
              "No individual noble or banker is named and no commission by them is asserted.",
              subject="cand-0983", obj="cand-7291", mentioned=["cand-0983", "cand-1581", "cand-7291", "cand-4653"],
              quote="introduced him to a number of influential nobles and bankers"),
    statement("st-chp7-p200-v-contemporary-painting-interest-at-versailles", 12, 13,
              "stimulated_interest_in_contemporary_italian_painting",
              "Haskell says the occasion stimulated interest in contemporary Italian painting among some younger art lovers who were tiring of the official style at Versailles.",
              "This is an attributed qualitative account; preserve ‘some’ and the author's quoted ‘official’ characterization.",
              subject="cand-7290", obj="cand-4131", mentioned=["cand-7290", "cand-4131", "cand-7305", "cand-7287"],
              quote="This was an important occasion for it stimulated interest in contemporary Italian painting among some of the younger generation of art lovers who were growing tired of the ‘official’ style at Versailles.",
              extra={"footnote_marker": 4}),
    statement("st-chp7-p200-v-naples-captured-after-paolos-return", 13, 13,
              "conquered_by_opposing_forces", "Haskell says that after Paolo de Matteis returned to Naples, the city was conquered by opposing forces.",
              "The opposing forces and exact date are not supplied in this clause; do not infer the coalition from later context.",
              subject="cand-7292", obj="cand-7293", mentioned=["cand-1581", "cand-3534", "cand-7292", "cand-7293"],
              quote="But hardly had Paolo got back to Naples when the city was conquered by the opposing forces"),
    statement("st-chp7-p200-v-paolo-works-for-binchs-and-daun", 13, 13,
              "worked_for_after_conquest", "Haskell says Paolo de Matteis found himself working for the English Admiral ‘Binchs’ and Count Daun after the capture.",
              "The wording gives employment/patronage after the capture; do not infer whether each work was a formal commission.",
              subject="cand-1581", obj="cand-7301", mentioned=["cand-1581", "cand-7301", "cand-0906", "cand-7293"],
              quote="and he found himself working for the English Admiral ‘Binchs’ and the Austrian commander Count Daun"),
    statement("st-chp7-p200-v-daun-responsible-for-naples-capture", 13, 13,
              "held_responsible_for_capture", "Haskell identifies Count Daun as responsible for the capture of Naples.",
              "Keep this source-attributed responsibility claim distinct from a general claim about the full military operation.",
              subject="cand-0906", obj="cand-7293", mentioned=["cand-0906", "cand-7293"],
              quote="who had been responsible for its capture", extra={"footnote_marker": 5}),
    statement("st-chp7-p200-v-daun-first-viceroy-and-patronage", 13, 13,
              "appointed_viceroy_and_rivalled_predecessors_in_patronage",
              "Haskell says Daun became the first viceroy of the new regime in 1707 and rivalled his Spanish predecessors in patronage of Italian art.",
              "The regime and prior viceroys are unnamed; ‘rivalled’ is Haskell's comparative characterization, not a measured ranking.",
              subject="cand-0906", obj="cand-7294", mentioned=["cand-0906", "cand-7294", "cand-7295", "cand-4131", "cand-7284"],
              quote="Daun, who in 1707 was made the first viceroy of the new regime, rivalled his Spanish predecessors in the patronage of Italian art",
              extra={"footnote_marker": 6}),
    statement("st-chp7-p200-v-painters-make-canvases-for-daun-palace", 14, 14,
              "produced_canvases_for_palace", "Haskell says Solimena, Giacomo del Po, and Paolo de Matteis produced canvases to decorate Daun's palace in Vienna.",
              "Works are described collectively; no titles or individual artist-to-canvas assignments are supplied.",
              subject="cand-2484", obj="cand-7300", mentioned=["cand-2484", "cand-7296", "cand-1581", "cand-7300", "cand-0906", "cand-7299", "cand-2772"],
              quote="Solimena, Giacomo del Po and Paolo de Matteis all produced canvases to decorate his palace in Vienna"),
    statement("st-chp7-p200-v-chiarini-frescoes-daun-palace", 14, 14,
              "frescoed_palace", "Haskell says Marc’antonio Chiarini frescoed Daun's palace in Vienna.",
              "The source supplies no dates, room names, or specific fresco subjects.",
              subject="cand-0662", obj="cand-7299", mentioned=["cand-0662", "cand-7299", "cand-2772"],
              quote="which was frescoed by the Bolognese Marc’antonio Chiarini"),
    statement("st-chp7-p200-v-daun-appointment-and-return", 15, 15,
              "returned_to_naples_after_short_first_appointment",
              "Haskell says Daun's first appointment in Naples lasted only a few months and that he returned in 1713 for a further six years.",
              "The source's duration and return year are retained as written; no exact start/end dates are inferred.",
              subject="cand-0906", obj="cand-3534", mentioned=["cand-0906", "cand-3534"],
              quote="Although his first appointment in Naples only lasted for a few months, he came back for a further six years in 1713"),
    statement("st-chp7-p200-v-daun-neapolitan-painting-central-europe", 15, 15,
              "principal_agent_in_diffusion_of_neapolitan_painting",
              "Haskell calls Daun one of the principal agents through whom Neapolitan painting was introduced into Central Europe.",
              "This is Haskell's account of cultural transmission; it does not specify a complete route or every work involved.",
              subject="cand-0906", obj="cand-1729", mentioned=["cand-0906", "cand-1729", "cand-6762"],
              quote="and was one of the principal agents through whom Neapolitan painting was introduced into Central Europe"),
    statement("st-chp7-p200-v-harrach-continues-process-after-1728", 15, 16,
              "continued_process_after_1728",
              "Haskell says the process was carried further after 1728 by Count Harrach, whom he calls the most cultivated of the Austrian viceroys.",
              "The OCR reads ‘Anther’; the page image reads ‘further’. The correction is recorded here only, and the author's evaluative phrase remains attributed.",
              subject="cand-1291", obj="cand-1729", mentioned=["cand-1291", "cand-1729", "cand-7284"],
              quote="a process which was carried much\nAnther after 1728 by the most cultivated of all the Austrian viceroys, Count Harrach.",
              extra={"ocr_corrections": [{"source_line": 16, "ocr": "Anther", "print": "further"}], "footnote_marker": 7}),
    statement("st-chp7-p200-v-italian-commanders-open-continuation", 17, 17,
              "open_description_continuation",
              "Haskell begins a further account of high commanders of Italian origin serving in the Imperial army and says they were keen to furnish something; the sentence is unfinished at the segment boundary.",
              "Keep the statement partial. It continues on p.201 after the intervening plate segments; do not complete the object of furnishing before that segment is read.",
              subject="cand-7303", obj="cand-7304", mentioned=["cand-7288", "cand-7303", "cand-7304"],
              quote="Besides these men there were a number of high commanders of Italian origin serving in the Imperial army and they were especially keen to take the opportunity of furnishing",
              extra={"continuation_status": "open", "continuation_expected_segment_id": BODY_CONTINUATION_SEGMENT_ID}),
    statement("st-chp7-p200-v-note6-daun-commissioned-ghislandi-portrait", 18, 18,
              "commissioned_portrait_from",
              "Haskell's note says Count Daun commissioned his portrait from Vittore Ghislandi in Bergamo.",
              "The portrait is unidentified and the claim is reported through the note's citations; cited pages were not independently consulted.",
              subject="cand-0906", obj="cand-7302", mentioned=["cand-0906", "cand-1101", "cand-7302", "cand-6208"],
              quote="In Bergamo he commissioned his portrait from Vittore Gliislandi",
              speaker="Haskell footnote", text_layer="footnote",
              extra={"footnote_marker": 6, "related_segment": SEGMENT_ID,
                     "ocr_corrections": [{"source_line": 18, "ocr": "Gliislandi", "print": "Ghislandi"}]}),
    cite("st-chp7-p200-v-note6-cite-de-dominici", "ibid., pp. 295, 332, 435-7, 444", "cand-4835", 6,
         ["st-chp7-p200-v-daun-first-viceroy-and-patronage", "st-chp7-p200-v-note6-daun-commissioned-ghislandi-portrait"], "Ibid. continues the de Dominici volume IV citation; the cited pages were not independently read."),
    cite("st-chp7-p200-v-note6-cite-pascoli", "Pascoli, H, p. 102", "cand-4552", 6,
         ["st-chp7-p200-v-note6-daun-commissioned-ghislandi-portrait"], "Volume II, p.102 is a bibliographic locator only."),
    cite("st-chp7-p200-v-note6-cite-zanotti", "Zanotti, I, p. 277", "cand-7115", 6,
         ["st-chp7-p200-v-note6-daun-commissioned-ghislandi-portrait"], "Volume I, p.277 is a bibliographic locator only."),
    cite("st-chp7-p200-v-note6-cite-tassi", "Tassi, II, p. 64", "cand-6590", 6,
         ["st-chp7-p200-v-note6-daun-commissioned-ghislandi-portrait"], "Volume II, p.64 is a bibliographic locator only."),

]

planned_statement_ids = {row["statement_id"] for row in statements}
existing_statement_ids = {row["statement_id"] for row in statement_rows}
if len(planned_statement_ids) != len(statements) or planned_statement_ids & existing_statement_ids:
    raise SystemExit("statement IDs are duplicated")

line_offsets = {}
offset = 0
for number in range(LINE_START, LINE_END + 1):
    line_offsets[number] = offset
    offset += len(source_lines[number - 1]) + 1

new_mentions = []
available_candidate_ids = existing_candidate_ids | new_candidate_ids
for _, (surface, candidate_id, note, lines) in enumerate(mention_specs, 1):
    if candidate_id not in available_candidate_ids:
        raise SystemExit(f"mention references missing candidate: {surface!r} -> {candidate_id}")
    # OCR sometimes attaches a superscript footnote digit directly to a name
    # (for example England1). Treat letters as lexical boundaries while
    # allowing trailing digits to remain outside the mention span.
    pattern = re.compile(r"(?<![^\W\d_])" + re.escape(surface) + r"(?![^\W\d_])", re.IGNORECASE)
    spans = []
    for line_number in lines:
        if line_number not in line_offsets:
            raise SystemExit(f"mention line outside segment: {surface!r}, L{line_number}")
        spans.extend(
            (line_offsets[line_number] + match.start(), line_offsets[line_number] + match.end())
            for match in pattern.finditer(source_lines[line_number - 1])
        )
    if not spans:
        raise SystemExit(f"mention text not found: {surface!r} on lines {lines}")
    for start, end in spans:
        if segment_text[start:end].casefold() != surface.casefold():
            raise SystemExit(f"mention offsets do not recover source text: {surface!r}")
        new_mentions.append({
            "mention_id": "",
            "segment_id": SEGMENT_ID,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(end),
            "note": note,
        })

new_mentions.sort(key=lambda row: (int(row["start_char"]), int(row["end_char"]), row["candidate_id"]))
for number, row in enumerate(new_mentions, 1):
    row["mention_id"] = f"m-chp7-p200-v-{number:03d}"
    if any(existing["mention_id"] == row["mention_id"] for existing in mention_rows):
        raise SystemExit(f"mention ID already exists: {row['mention_id']}")

claimed_spans = {}
for row in new_mentions:
    span = (row["start_char"], row["end_char"])
    prior = claimed_spans.get(span)
    if prior and prior != row["candidate_id"]:
        raise SystemExit(f"one exact span maps to two candidates: {span}, {prior}, {row['candidate_id']}")
    claimed_spans[span] = row["candidate_id"]

for row in statements:
    q = row["qualifiers"]
    excerpt = "\n".join(source_lines[q["source_line_start"] - 1 : q["source_line_end"]])
    if row["original_quote"] not in excerpt:
        raise SystemExit(f"statement quote does not occur in source excerpt: {row['statement_id']}")
    for candidate_id in q.get("mentioned_candidate_ids", []):
        if candidate_id not in available_candidate_ids:
            raise SystemExit(f"statement references missing candidate: {row['statement_id']} -> {candidate_id}")
    for linked_id in q.get("linked_body_statement_ids", []):
        if linked_id not in planned_statement_ids and linked_id not in existing_statement_ids:
            raise SystemExit(f"citation references missing statement: {row['statement_id']} -> {linked_id}")

previous_statement_id = "st-chp7-p199-v-open-then-came-the"
previous_statement = next((row for row in statement_rows if row["statement_id"] == previous_statement_id), None)
if previous_statement is None or previous_statement["qualifiers"].get("continuation_status") != "open":
    raise SystemExit("expected the p.199 open continuation statement to remain open")
previous_coverage = next((row for row in coverage_rows if row["segment_id"] == PREVIOUS_SEGMENT_ID), None)
if previous_coverage is None or previous_coverage["migration_status"] != "partial":
    raise SystemExit("expected p.199 coverage to be reviewed/partial before closing its sentence")

updated_coverage = []
for row in coverage_rows:
    row = dict(row)
    if row["segment_id"] == PREVIOUS_SEGMENT_ID:
        row.update({
            "disposition": "reviewed",
            "migration_status": "complete",
            "source_line_ranges": "L3-7",
            "note": "p.199 L7 'Then came the' is closed by p.200 L10 'war of the Spanish succession'; the cross-segment continuation is linked in book-statements.jsonl.",
        })
    elif row["segment_id"] == SEGMENT_ID:
        row.update({
            "disposition": "reviewed",
            "migration_status": "partial",
            "source_line_ranges": "L10-18",
            "note": "p.200 body and footnote 6 (the text present at L18) read against CHP-7.pdf physical p.38 and migrated. Footnotes 1-5 and 7 occur in the later composite note block L62-76 and remain queued there. The L17 sentence ending 'furnishing' continues on p.201 L42-55 after plate segments. S2 corrections: printed 'further' for OCR 'Anther'; printed 'Pascoli, II' for OCR 'H'; printed 'Ghislandi' for OCR 'Gliislandi'. Source text unchanged.",
        })
    updated_coverage.append(row)

preview = {
    "mode": "dry-run",
    "segment": SEGMENT_ID,
    "closed_previous_segment": PREVIOUS_SEGMENT_ID,
    "body_continuation_segment": BODY_CONTINUATION_SEGMENT_ID,
    "new_candidates": len(new_candidates),
    "new_mentions": len(new_mentions),
    "new_statements": len(statements),
    "previous_coverage": "reviewed/complete",
    "coverage": "reviewed/partial",
    "scan_corrections": ["Anther -> further", "Pascoli, H -> Pascoli, II", "Gliislandi -> Ghislandi"],
    "deferred_footnotes": [1, 2, 3, 4, 5, 7],
    "statement_ids": [row["statement_id"] for row in statements],
    "mention_preview": [
        {"surface": row["surface_form"], "candidate_id": row["candidate_id"], "start_char": row["start_char"], "end_char": row["end_char"]}
        for row in new_mentions
    ],
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
if not parser.parse_args().apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)

# Close the p.199 continuation with the exact p.200 evidence while preserving
# the original fragment as its source quote.
previous_statement["predicate"] = "chronological_continuation"
previous_statement["qualifiers"].update({
    "claim": "The open phrase 'Then came the' continues on p.200 as 'war of the Spanish succession.'",
    "qualification": "Closed by the next body segment in source order; the two fragments form one chronological clause.",
    "continuation_status": "completed",
    "continuation_completed_in_segment_id": SEGMENT_ID,
    "continuation_source_lines": [10],
    "mentioned_candidate_ids": ["cand-2502"],
    "continuation_note": "Closed by p.200 L10; the phrase now reads 'Then came the war of the Spanish succession.'",
})
previous_statement["qualifiers"].pop("continuation_expected_segment_id", None)

backup_suffix = ".bak-s2-chp7-p200-sec-v-l9-18-20260930"
for path in (CANDIDATE_PATH, MENTION_PATH, STATEMENT_PATH, COVERAGE_PATH):
    backup = path.with_name(path.name + backup_suffix)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(path, backup)


def write_csv_atomic(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


candidate_rows.extend(new_candidates)
mention_rows.extend(new_mentions)
statement_rows.extend(statements)
write_csv_atomic(CANDIDATE_PATH, candidate_fields, candidate_rows)
write_csv_atomic(MENTION_PATH, mention_fields, mention_rows)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=STATEMENT_PATH.parent, delete=False, suffix=".tmp") as stream:
    for row in statement_rows:
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    temporary = Path(stream.name)
temporary.replace(STATEMENT_PATH)
write_csv_atomic(COVERAGE_PATH, coverage_fields, updated_coverage)

preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
