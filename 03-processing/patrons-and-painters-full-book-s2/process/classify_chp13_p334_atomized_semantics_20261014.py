from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import shutil
from io import StringIO
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge" / "tables" / "entity-candidates.csv"
MENTIONS = ROOT / "04-knowledge" / "tables" / "mentions.csv"
SEGMENTS = ROOT / "04-knowledge" / "tables" / "segments.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-13.pdf"
IMAGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "p334_page_review_20261014.png"
BODY = "chp-13:13_CHP-13_intro:l21-30"
PREVIOUS = "chp-13:13_CHP-13_intro:l14-19"
NOTES = "chp-13:13_CHP-13_intro:l179-251"
BACKUP_SUFFIX = ".bak-s2-ch13-p334-atomized-semantics-20261014"
EXPECTED = {
    TABLE.name: "dfa833740fcd700530a24052ef68de03adb29399a9661e2eb5c219d03af61bf9",
    CANDIDATES.name: "c85332107e01ce06772e197ebf8f0c1d8aa18e8fc4bfe628b73df9bae57013d8",
    MENTIONS.name: "8e935e54b14afb24f5a0f020196fccd787b8cd39477b6d70facd70b38b8c11cb",
    SEGMENTS.name: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE.name: "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8",
    PDF.name: "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc",
    IMAGE.name: "9987c1e894ea7f0737480b39259223f845974b509f7cf380168a9c6653175efc",
}

TARGET_IDS = {
    "st-chp13-p334-albrizzi-birth-and-inherited-business",
    "st-chp13-p334-albrizzi-catholic-and-aristocratic-connections-inference",
    "st-chp13-p334-albrizzi-collector-and-publisher",
    "st-chp13-p334-albrizzi-prominent-in-venetian-intellectual-life",
    "st-chp13-p334-albrizzi-travel-and-vienna-education",
    "st-chp13-p334-albrizzi-international-audience-goal",
    "st-chp13-p334-albrizzi-guidebook-1737",
    "st-chp13-p334-albrizzi-edited-weekly-bulletin",
    "st-chp13-p334-albrizzi-member-and-guardiano-at-san-rocco",
    "st-chp13-p334-albrizzi-plan-revive-venetian-prints-open",
    "st-chp13-p334-almoro-organized-academy",
    "st-chp13-p334-bossuet-french-edition-started-1736",
    "st-chp13-p334-bossuet-interest-and-heresy-context",
    "st-chp13-p334-bettinelli-criticized-opulent-poem-collection",
    "st-chp13-p334-fine-edition-category-produced-striking-designs",
    "st-chp13-p334-named-publisher-triad",
    "st-chp13-p334-noble-reported-thousand-ducats",
    "st-chp13-p334-publications-reflected-connections",
}

# Exact rows in the current table; this set is checked independently of any prose label.
TARGET_IDS.add("st-chp13-p334-piazzetta-first-bossuet-illustrator")

UNSET_CLASSIFICATIONS = {
    "st-chp13-p334-albrizzi-birth-and-inherited-business": False,
    "st-chp13-p334-albrizzi-collector-and-publisher": True,
    "st-chp13-p334-albrizzi-prominent-in-venetian-intellectual-life": True,
    "st-chp13-p334-albrizzi-travel-and-vienna-education": True,
    "st-chp13-p334-albrizzi-international-audience-goal": True,
    "st-chp13-p334-bettinelli-criticized-opulent-poem-collection": True,
    "st-chp13-p334-bossuet-interest-and-heresy-context": True,
    "st-chp13-p334-fine-edition-category-produced-striking-designs": True,
    "st-chp13-p334-named-publisher-triad": False,
    "st-chp13-p334-noble-reported-thousand-ducats": True,
    "st-chp13-p334-publications-reflected-connections": True,
}

NEW_CANDIDATES = [
    {"candidate_id":"cand-12126","index_entry_id":"","canonical_name":"Contemporary pictures collected by Giambattista Albrizzi (unnamed group)","index_page_range":"","suggested_type":"work","status":"open","index_source_file":"","sub_entry":"","detail":"Haskell calls Albrizzi a notable collector of contemporary pictures but names no individual picture or inventory. Keep this as a source-bounded group.","exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":f"{BODY}#L26"},
    {"candidate_id":"cand-12127","index_entry_id":"","canonical_name":"Finely produced books published by Giambattista Albrizzi (unnamed group)","index_page_range":"","suggested_type":"archive","status":"open","index_source_file":"","sub_entry":"","detail":"Haskell says Albrizzi published some of the century's most finely produced books; no titles are specified in this clause.","exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":f"{BODY}#L26"},
    {"candidate_id":"cand-12128","index_entry_id":"","canonical_name":"Unnamed father of Giambattista Albrizzi","index_page_range":"","suggested_type":"person","status":"open","index_source_file":"","sub_entry":"","detail":"The source identifies Albrizzi's father only through the inheritance statement; it supplies no personal name or other biography.","exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":f"{BODY}#L26"},
    {"candidate_id":"cand-12129","index_entry_id":"","canonical_name":"Flourishing publishing concern inherited by Giambattista Albrizzi","index_page_range":"","suggested_type":"institution","status":"open","index_source_file":"","sub_entry":"","detail":"The source says Albrizzi inherited a flourishing concern from his father; its name, imprint, and business history are not supplied.","exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":f"{BODY}#L26"},
    {"candidate_id":"cand-12130","index_entry_id":"","canonical_name":"Wide international public intended for Albrizzi's French editions","index_page_range":"","suggested_type":"term","status":"open","index_source_file":"","sub_entry":"","detail":"Haskell describes an intended wide international public for the French-language edition; no audience membership or reception evidence is given.","exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":f"{BODY}#L29"},
    {"candidate_id":"cand-12131","index_entry_id":"","canonical_name":"Unnamed son of Giambattista Albrizzi","index_page_range":"","suggested_type":"person","status":"open","index_source_file":"","sub_entry":"","detail":"The source says Albrizzi sent his son to be educated in Vienna but gives no name, age, or school.","exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":f"{BODY}#L26"},
    {"candidate_id":"cand-12132","index_entry_id":"","canonical_name":"Spread of heretical opinions across Europe in Haskell's account","index_page_range":"","suggested_type":"term","status":"open","index_source_file":"","sub_entry":"","detail":"Haskell links the renewed interest in Bossuet to the spread of heretical opinions; this is his historical interpretation, not an independently verified event series.","exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":f"{BODY}#L29"},
    {"candidate_id":"cand-12133","index_entry_id":"","canonical_name":"Striking designs produced for fine illustrated editions (unnamed group)","index_page_range":"","suggested_type":"work","status":"open","index_source_file":"","sub_entry":"","detail":"Haskell refers to many striking designs for the fine-edition category without naming or enumerating them.","exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":f"{BODY}#L24"},
    {"candidate_id":"cand-12134","index_entry_id":"","canonical_name":"Unnamed noble who reported spending on a commemorative collection","index_page_range":"","suggested_type":"person","status":"open","index_source_file":"","sub_entry":"","detail":"Haskell reports that one unnamed noble said he had spent a thousand ducats on a collection; no name or further identity is supplied.","exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":f"{BODY}#L22"},
    {"candidate_id":"cand-12135","index_entry_id":"","canonical_name":"Unnamed commemorative collection reportedly costing one thousand ducats","index_page_range":"","suggested_type":"archive","status":"open","index_source_file":"","sub_entry":"","detail":"The specific collection referred to as 'such a collection' is not titled or otherwise identified; keep it distinct from the genre candidate cand-9985.","exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":f"{BODY}#L22"},
    {"candidate_id":"cand-12136","index_entry_id":"","canonical_name":"Giambattista Albrizzi's publications discussed on p.334 (unnamed group)","index_page_range":"","suggested_type":"archive","status":"open","index_source_file":"","sub_entry":"","detail":"Source-defined group of Albrizzi's publications whose choice and style are said to stress his connections; individual titles are not enumerated by this sentence.","exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":f"{BODY}#L28"},
    {"candidate_id":"cand-12137","index_entry_id":"","canonical_name":"Intellectual life of Venice in Haskell's account","index_page_range":"","suggested_type":"term","status":"open","index_source_file":"","sub_entry":"","detail":"Haskell characterizes Albrizzi as prominent in Venice's intellectual life; this is a social-cultural sphere, not an institution or membership list.","exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":f"{BODY}#L26"},
    {"candidate_id":"cand-12138","index_entry_id":"","canonical_name":"Il Forestiere Illuminato (Venice guidebook, first issued 1737)","index_page_range":"","suggested_type":"archive","status":"open","index_source_file":"","sub_entry":"","detail":"Haskell says Albrizzi first issued this guide to Venice in 1737 with a dedication to the Elector of Saxony. The page image reads 'Il Forestiere Illuminato'; no external edition was consulted.","exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":f"{BODY}#L26"},
]

NEW_MENTIONS = [
    {"mention_id":"m-s2-ch13-p334-027","candidate_id":"cand-12134","surface_form":"One noble","start_char":168,"end_char":177,"note":"The person is unnamed; the statement is reported speech."},
    {"mention_id":"m-s2-ch13-p334-028","candidate_id":"cand-12135","surface_form":"such a collection","start_char":222,"end_char":239,"note":"Anaphoric reference to an unidentified individual commemorative collection, not just the genre."},
    {"mention_id":"m-s2-ch13-p334-029","candidate_id":"cand-12133","surface_form":"many of the most striking designs","start_char":823,"end_char":856,"note":"Unenumerated design group produced for the fine-edition category."},
    {"mention_id":"m-s2-ch13-p334-030","candidate_id":"cand-2068","surface_form":"Three publishers","start_char":872,"end_char":888,"note":"Collective framing for the three names listed in this sentence."},
    {"mention_id":"m-s2-ch13-p334-034","candidate_id":"cand-12126","surface_form":"contemporary pictures","start_char":1070,"end_char":1091,"note":"Source-defined group collected by Albrizzi; individual works are not named."},
    {"mention_id":"m-s2-ch13-p334-035","candidate_id":"cand-12127","surface_form":"some of the most finely produced books","start_char":1120,"end_char":1158,"note":"Unnamed publication group; no title is supplied here."},
    {"mention_id":"m-s2-ch13-p334-036","candidate_id":"cand-12129","surface_form":"a flourishing concern","start_char":1209,"end_char":1230,"note":"Unidentified publishing business inherited by Albrizzi."},
    {"mention_id":"m-s2-ch13-p334-037","candidate_id":"cand-12128","surface_form":"his father","start_char":1236,"end_char":1246,"note":"Unnamed person; no identity inferred."},
    {"mention_id":"m-s2-ch13-p334-038","candidate_id":"cand-12131","surface_form":"his son","start_char":1371,"end_char":1378,"note":"Unnamed person sent to Vienna for education."},
    {"mention_id":"m-s2-ch13-p334-039","candidate_id":"cand-12137","surface_form":"intellectual life of Venice","start_char":1672,"end_char":1699,"note":"Conceptual social-cultural sphere named in Haskell's assessment."},
    {"mention_id":"m-s2-ch13-p334-040","candidate_id":"cand-2719","surface_form":"Venice","start_char":1693,"end_char":1699,"note":"Place nested within the intellectual-life phrase."},
    {"mention_id":"m-s2-ch13-p334-041","candidate_id":"cand-12136","surface_form":"his publications","start_char":2418,"end_char":2434,"note":"Unspecified group of Albrizzi's publications."},
    {"mention_id":"m-s2-ch13-p334-042","candidate_id":"cand-12132","surface_form":"the increasing spread of heretical opinions throughout Europe","start_char":2670,"end_char":2731,"note":"Haskell's interpretive historical context; no named movement or adherents are supplied."},
    {"mention_id":"m-s2-ch13-p334-043","candidate_id":"cand-12130","surface_form":"wide international public","start_char":2823,"end_char":2848,"note":"Intended audience in Haskell's account; no specific readership is identified."},
]

NEW_STATEMENTS = {
    "st-chp13-p334-albrizzi-inherited-fathers-concern",
    "st-chp13-p334-albrizzi-son-of-unnamed-father",
    "st-chp13-p334-albrizzi-published-finely-produced-books",
    "st-chp13-p334-albrizzi-travelled-in-austria",
    "st-chp13-p334-albrizzi-sent-son-to-vienna-for-education",
}
FOOTNOTE_KEYS = {
    "footnote_marker", "footnote_printed_page", "footnote_text_pending", "footnote_segment",
    "footnote_body_link_status", "cross_reference_segments", "footnote_refs", "footnote_segment_id",
    "footnote_source_line", "footnote_source_lines", "footnote_statement_ids", "footnote_link_status",
    "footnote_pending",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames or [], list(reader)


def csv_bytes(path: Path, rows: list[dict], extra: list[dict] = ()) -> bytes:
    fields, _ = read_csv(path)
    output = [dict(row) for row in rows]
    output.extend({key: str(row.get(key, "")) for key in fields} for row in extra)
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(output)
    return buffer.getvalue().encode("utf-8")


def strip_footnotes(qualifiers: dict) -> None:
    for key in FOOTNOTE_KEYS:
        qualifiers.pop(key, None)


def make_statement(template: dict, statement_id: str, subject: str | None, object_: str | None,
                   predicate: str, claim: str, quote: str, line: int, mentioned: list[str],
                   qualification: str, *, keep_footnote: bool = False) -> dict:
    qualifiers = copy.deepcopy(template["qualifiers"])
    if not keep_footnote:
        strip_footnotes(qualifiers)
    qualifiers.update({
        "source_line_start": line,
        "source_line_end": line,
        "printed_page": 334,
        "pdf_physical_page": 3,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "authorial narrative",
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": True,
    })
    qualifiers.pop("ocr_corrections", None)
    return {
        "statement_id": statement_id, "segment_id": BODY,
        "subject_candidate_id": subject, "object_candidate_id": object_, "predicate": predicate,
        "qualifiers": qualifiers, "original_quote": quote, "origin": "book",
        "source_file": SOURCE.relative_to(ROOT).as_posix(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Atomize and classify Chapter 13 p.334 S2 statements")
    parser.add_argument("--apply", action="store_true", help="write after source, row-set, citation, and span checks")
    args = parser.parse_args()

    paths = (TABLE, CANDIDATES, MENTIONS, SEGMENTS, SOURCE, PDF, IMAGE)
    actual = {path.name: sha(path) for path in paths}
    if actual != EXPECTED:
        raise SystemExit(f"preflight hash mismatch; no writes made: {actual}")

    rows = [json.loads(line) for line in TABLE.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement_id in table")
    target = [row for row in rows if row.get("segment_id") == BODY]
    if {row["statement_id"] for row in target} != TARGET_IDS:
        raise SystemExit("p.334 statement set changed")
    unset = {row["statement_id"] for row in target if "relation_candidate" not in row.get("qualifiers", {})}
    if unset != set(UNSET_CLASSIFICATIONS):
        raise SystemExit(f"p.334 unset statement set changed: {unset}")
    if NEW_STATEMENTS & set(by_id):
        raise SystemExit("one or more planned p.334 statement IDs already exist")

    candidate_fields, candidates = read_csv(CANDIDATES)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    new_candidate_ids = {row["candidate_id"] for row in NEW_CANDIDATES}
    if new_candidate_ids & set(candidate_by_id) or len(new_candidate_ids) != len(NEW_CANDIDATES):
        raise SystemExit("planned candidate IDs are not unused and unique")
    if candidate_by_id.get("cand-1907", {}).get("suggested_type") != "work":
        raise SystemExit("Piazzetta index candidate type changed; review before applying")
    if candidate_by_id.get("cand-0028", {}).get("canonical_name") != "Albrizzi, Giambattista":
        raise SystemExit("Albrizzi index subentry candidate changed")

    mention_fields, mentions = read_csv(MENTIONS)
    mention_by_id = {row["mention_id"]: row for row in mentions}
    new_mention_ids = {row["mention_id"] for row in NEW_MENTIONS}
    if new_mention_ids & set(mention_by_id) or len(new_mention_ids) != len(NEW_MENTIONS):
        raise SystemExit("planned mention IDs are not unused and unique")
    if mention_by_id.get("m-s2-ch13-p334-010", {}).get("candidate_id") != "cand-0028":
        raise SystemExit("guidebook mention mapping changed")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_meta = next(json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8").splitlines() if json.loads(line)["segment_id"] == BODY)
    segment_text = "\n".join(source_lines[segment_meta["line_start"] - 1:segment_meta["line_end"]])
    if not segment_text.startswith("[Page 334]\n"):
        raise SystemExit("canonical p.334 segment changed")
    if segment_text[1516:1540] != "II Forestiere Illuminate":
        raise SystemExit("p.334 guidebook OCR mention span changed")
    for row in target:
        q = row["qualifiers"]
        block = "\n".join(source_lines[q["source_line_start"] - 1:q["source_line_end"]])
        if not row.get("original_quote") or row["original_quote"] not in block:
            raise SystemExit(f"source quote mismatch: {row['statement_id']}")
    for mention in NEW_MENTIONS:
        if segment_text[mention["start_char"]:mention["end_char"]] != mention["surface_form"]:
            raise SystemExit(f"mention offset mismatch: {mention['mention_id']}")

    def quote(needle: str) -> str:
        start = segment_text.find(needle)
        if start < 0:
            raise SystemExit(f"source quote not found: {needle}")
        return segment_text[start:start + len(needle)]

    # Confirm the two footnote handoffs before splitting their body claims.
    note2 = by_id["st-chp13-p334-n2-morazzoni-citation"]
    note3 = by_id["st-chp13-p334-n3-bossuet-eighth-volume-1755"]
    birth = by_id["st-chp13-p334-albrizzi-birth-and-inherited-business"]
    birth_template = copy.deepcopy(birth)
    travel = by_id["st-chp13-p334-albrizzi-travel-and-vienna-education"]
    if note2["qualifiers"].get("linked_body_statement_ids") != [birth["statement_id"]]:
        raise SystemExit("p.334 footnote 2 body link changed")
    if note3["qualifiers"].get("linked_body_statement_ids") != [travel["statement_id"]]:
        raise SystemExit("p.334 footnote 3 body link changed")
    p333_quote = by_id["st-chp13-p333-anonymous-quotation-on-poem-collections"]
    if "cornplains" not in p333_quote["qualifiers"].get("continuation_quote", ""):
        raise SystemExit("cross-page p.333 quotation changed")

    for sid, decision in UNSET_CLASSIFICATIONS.items():
        by_id[sid]["qualifiers"]["relation_candidate"] = decision

    # Split the compound biography sentence; footnote 2 specifically cites the inheritance.
    birth["predicate"] = "born_in_1699"
    birth["qualifiers"]["claim"] = "Haskell states that Albrizzi was born in 1699."
    birth["qualifiers"]["qualification"] = "A birth-date claim, kept separate from the inheritance relation in the following clause."
    birth["qualifiers"]["mentioned_candidate_ids"] = ["cand-0025"]
    birth["qualifiers"].pop("ocr_corrections", None)
    strip_footnotes(birth["qualifiers"])
    birth["original_quote"] = quote("He was born in 1699")

    collector = by_id["st-chp13-p334-albrizzi-collector-and-publisher"]
    collector["object_candidate_id"] = "cand-12126"
    collector["predicate"] = "collected_contemporary_pictures"
    collector["qualifiers"]["claim"] = "Haskell describes Albrizzi as a notable collector of contemporary pictures."
    collector["qualifiers"]["qualification"] = "The pictures are an unnamed source-defined group; no title or inventory is supplied."
    collector["qualifiers"]["mentioned_candidate_ids"] = ["cand-0025", "cand-12126"]
    collector["qualifiers"]["ocr_corrections"] = [{"source_line":26,"ocr":"welT","print":"well","basis":"CHP-13.pdf physical page 3."}]
    collector["original_quote"] = quote("a notable collector of contemporary pictures")

    intellectual = by_id["st-chp13-p334-albrizzi-prominent-in-venetian-intellectual-life"]
    intellectual["object_candidate_id"] = "cand-12137"
    intellectual["predicate"] = "prominent_in"
    intellectual["qualifiers"]["qualification"] = "This is Haskell's qualitative assessment of a cultural sphere; no organization or specific activity is inferred."
    intellectual["qualifiers"]["mentioned_candidate_ids"] = ["cand-0025", "cand-12137", "cand-2719"]

    international = by_id["st-chp13-p334-albrizzi-international-audience-goal"]
    international["object_candidate_id"] = "cand-12130"
    international["predicate"] = "aimed_to_reach"
    international["qualifiers"]["qualification"] = "The audience is an intended public in Haskell's account; this does not establish sales or actual readership."
    international["qualifiers"]["mentioned_candidate_ids"] = ["cand-0025", "cand-9987", "cand-12130"]

    travel["object_candidate_id"] = "cand-5529"
    travel["predicate"] = "travelled_in"
    travel["qualifiers"]["claim"] = "Haskell says Albrizzi travelled widely, especially in Germany."
    travel["qualifiers"]["qualification"] = "The adjacent clause also names Austria and says he maintained close links with both places; the vague links are not separately normalized. Note 3's antecedent remains uncertain."
    travel["qualifiers"]["mentioned_candidate_ids"] = ["cand-0025", "cand-5529"]
    travel["qualifiers"]["ocr_corrections"] = []
    travel["original_quote"] = quote("especially in Germany")

    international_title = by_id["st-chp13-p334-albrizzi-guidebook-1737"]
    international_title["object_candidate_id"] = "cand-12138"
    international_title["predicate"] = "published_venice_guide_with_dedication_to_elector_of_saxony_in_1737"
    international_title["qualifiers"]["mentioned_candidate_ids"] = ["cand-0025", "cand-12138", "cand-2719", "cand-0028"]
    international_title["qualifiers"]["ocr_corrections"] = [{"source_line":26,"ocr":"II Forestiere Illuminate","print":"Il Forestiere Illuminato","basis":"CHP-13.pdf physical page 3."}]

    triad = by_id["st-chp13-p334-named-publisher-triad"]
    triad["subject_candidate_id"] = "cand-2068"
    triad["qualifiers"]["qualification"] = "Haskell singles out these three named publishers; this is a comparative assessment, not an exhaustive ranking or a specific patronage relation."
    triad["qualifiers"]["mentioned_candidate_ids"] = ["cand-2068", "cand-0025", "cand-1844", "cand-2865"]

    noble = by_id["st-chp13-p334-noble-reported-thousand-ducats"]
    noble["subject_candidate_id"] = "cand-12134"
    noble["object_candidate_id"] = "cand-12135"
    noble["predicate"] = "reported_spending_one_thousand_ducats_on"
    noble["qualifiers"]["qualification"] = "Haskell reports the noble's statement; neither the speaker nor the collection is identified, and the expenditure is not independently verified."
    noble["qualifiers"]["mentioned_candidate_ids"] = ["cand-12134", "cand-12135", "cand-9985"]
    noble["qualifiers"]["ocr_corrections"] = []

    connections = by_id["st-chp13-p334-publications-reflected-connections"]
    connections["object_candidate_id"] = "cand-12136"
    connections["predicate"] = "connections_reflected_in_publication_choices_and_style"
    connections["qualifiers"]["qualification"] = "This is Haskell's interpretive summary about an unspecified publication group; it does not establish the separate causal contribution of each connection."
    connections["qualifiers"]["mentioned_candidate_ids"] = ["cand-0025", "cand-12136"]

    heresy = by_id["st-chp13-p334-bossuet-interest-and-heresy-context"]
    heresy["object_candidate_id"] = "cand-12132"
    heresy["predicate"] = "renewed_interest_in_bossuet_linked_to_spread_of_heresy"
    heresy["qualifiers"]["qualification"] = "This is Haskell's historical interpretation; it is not independently verified here."
    heresy["qualifiers"]["mentioned_candidate_ids"] = ["cand-0415", "cand-12132", "cand-3462"]

    designs = by_id["st-chp13-p334-fine-edition-category-produced-striking-designs"]
    designs["subject_candidate_id"] = "cand-12133"
    designs["object_candidate_id"] = "cand-9986"
    designs["predicate"] = "produced_for_fine_edition_category"
    designs["qualifiers"]["qualification"] = "Haskell's comparative claim concerns an unnamed group of designs; it supplies no inventory or individual attribution here."
    designs["qualifiers"]["mentioned_candidate_ids"] = ["cand-12133", "cand-9986"]

    reflected_quote = by_id["st-chp13-p333-anonymous-quotation-on-poem-collections"]["qualifiers"]
    reflected_quote["continuation_quote"] = reflected_quote["continuation_quote"].replace("cornplains", "complains")
    reflected_quote.setdefault("ocr_corrections", []).append({"source_line":22,"ocr":"cornplains","print":"complains","basis":"CHP-13.pdf physical page 3."})
    catholic = by_id["st-chp13-p334-albrizzi-catholic-and-aristocratic-connections-inference"]
    catholic.setdefault("ocr_corrections", [])
    family_fix = {"source_line":27,"ocr":"famflies","print":"families","basis":"CHP-13.pdf physical page 3."}
    if family_fix not in catholic["ocr_corrections"]:
        catholic["ocr_corrections"].append(family_fix)

    # The source index entry c0028 is Albrizzi, not the guidebook; c1907 is a Piazzetta person entry.
    mention_by_id["m-s2-ch13-p334-010"]["candidate_id"] = "cand-12138"
    mention_by_id["m-s2-ch13-p334-010"]["note"] = "S0 OCR form; page image reads Il Forestiere Illuminato. The S1 subentry candidate cand-0028 denotes Albrizzi, not the book."
    piazzetta = candidate_by_id["cand-1907"]
    piazzetta["suggested_type"] = "person"
    piazzetta["detail"] = "The index subentry 'book illustration for Albrizzi' concerns Piazzetta's activity; the indexed entity is the artist, not a work. Keep this index candidate separate from cand-1901 until S3 identity alignment."
    by_id["st-chp13-p334-piazzetta-first-bossuet-illustrator"]["qualifiers"]["mentioned_candidate_ids"] = ["cand-0025", "cand-9987", "cand-1907"]

    new_statements = [
        make_statement(birth_template, "st-chp13-p334-albrizzi-inherited-fathers-concern", "cand-0025", "cand-12129",
            "inherited_flourishing_concern_from_father", "Haskell says Albrizzi inherited a flourishing concern from his father.",
            quote("inherited a flourishing concern from his father"), 26, ["cand-0025", "cand-12128", "cand-12129"],
            "The business and father are source-defined but unnamed; p.334 note 2 cites Morazzoni, p.131, which was not independently consulted.", keep_footnote=True),
        make_statement(birth, "st-chp13-p334-albrizzi-son-of-unnamed-father", "cand-0025", "cand-12128",
            "son_of", "The source identifies the unnamed man as Albrizzi's father.", quote("his father"), 26,
            ["cand-0025", "cand-12128"], "The father is not named; no further identity is inferred."),
        make_statement(collector, "st-chp13-p334-albrizzi-published-finely-produced-books", "cand-0025", "cand-12127",
            "published_finely_produced_books", "Haskell says Albrizzi published some of the century's most finely produced books.",
            quote("publisher of some of the most finely produced books of the century"), 26,
            ["cand-0025", "cand-12127"], "The source supplies no title in this clause; keep the publication group open."),
        make_statement(travel, "st-chp13-p334-albrizzi-travelled-in-austria", "cand-0025", "cand-7201",
            "travelled_in", "Haskell says Albrizzi travelled in Austria and maintained close links there.",
            quote("and Austria with which he maintained close links"), 26,
            ["cand-0025", "cand-7201"], "The source's phrase 'close links' is retained as Haskell's wording; no particular institution or activity is inferred.", keep_footnote=True),
        make_statement(travel, "st-chp13-p334-albrizzi-sent-son-to-vienna-for-education", "cand-0025", "cand-12131",
            "sent_son_to_vienna_for_education", "Haskell says Albrizzi sent his son to be educated in Vienna.",
            quote("he sent his son to be educated in Vienna"), 26,
            ["cand-0025", "cand-12131", "cand-2772"],
            "The son is unnamed and no school is identified. Printed note 3 is linked to the source sentence, but its 'This' antecedent remains unresolved and is not treated as separate corroboration.", keep_footnote=True),
    ]

    # Footnote 2 cites inheritance; note 3 stays attached to the complete travel/education sentence.
    note2["qualifiers"]["linked_body_statement_ids"] = ["st-chp13-p334-albrizzi-inherited-fathers-concern"]
    note3["qualifiers"]["linked_body_statement_ids"] = [
        "st-chp13-p334-albrizzi-travel-and-vienna-education",
        "st-chp13-p334-albrizzi-travelled-in-austria",
        "st-chp13-p334-albrizzi-sent-son-to-vienna-for-education",
    ]

    updated_rows = rows + new_statements
    updated_target = [row for row in updated_rows if row.get("segment_id") == BODY]
    totals = {
        "true": sum(row["qualifiers"].get("relation_candidate") is True for row in updated_target),
        "false": sum(row["qualifiers"].get("relation_candidate") is False for row in updated_target),
        "unset": sum("relation_candidate" not in row["qualifiers"] for row in updated_target),
    }
    if len(updated_target) != 24 or totals != {"true": 21, "false": 3, "unset": 0}:
        raise SystemExit(f"unexpected p.334 totals: rows={len(updated_target)}, counts={totals}")

    candidate_bytes = csv_bytes(CANDIDATES, candidates, NEW_CANDIDATES)
    mention_rows = [{"mention_id": row["mention_id"], "segment_id": BODY, **row} for row in NEW_MENTIONS]
    mention_bytes = csv_bytes(MENTIONS, mentions, mention_rows)
    statement_bytes = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in updated_rows) + "\n").encode("utf-8")
    print("p.334 physical page 3: 11 unset claims classified; 5 atomic relations added.")
    print("Registered 13 source-bounded endpoints; repaired guidebook and Piazzetta candidate mappings; moved OCR notes to the relevant claims.")
    print("Counts: 21 relation candidates / 3 non-relational claims / 0 unset across 24 statements.")
    print("Rows after apply: candidates", len(candidates) + 13, "mentions", len(mentions) + len(NEW_MENTIONS), "statements", len(updated_rows))
    print("planned sha256:", "statements", hashlib.sha256(statement_bytes).hexdigest(), "candidates", hashlib.sha256(candidate_bytes).hexdigest(), "mentions", hashlib.sha256(mention_bytes).hexdigest())
    if not args.apply:
        print("preview only; no files written")
        return 0

    backup_map = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in (TABLE, CANDIDATES, MENTIONS)}
    existing = [backup.name for backup in backup_map.values() if backup.exists()]
    if existing:
        raise SystemExit(f"backup already exists; refusing overwrite: {existing}")
    for path, backup in backup_map.items():
        shutil.copy2(path, backup)
    TABLE.write_bytes(statement_bytes)
    CANDIDATES.write_bytes(candidate_bytes)
    MENTIONS.write_bytes(mention_bytes)
    print("applied; backups:", ", ".join(backup.name for backup in backup_map.values()))
    for path in (TABLE, CANDIDATES, MENTIONS):
        print(path.name, sha(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
