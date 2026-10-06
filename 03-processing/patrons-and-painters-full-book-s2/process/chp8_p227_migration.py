"""Controlled S2 migration for Chapter 8 printed page 227 and notes 1-3."""
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_ii.md"
P226 = "chp-8:08_CHP-8_sec_ii:l179-188"
P227 = "chp-8:08_CHP-8_sec_ii:l190-204"
P228 = "chp-8:08_CHP-8_sec_ii:l206-214"
NOTES = "chp-8:08_CHP-8_sec_ii:l372-461"
TARGET_IDS = {P226, P227, P228, NOTES}
BACKUP_SUFFIX = ".bak-s2-chp8-p227-20261001"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent,
                                     delete=False, suffix=".tmp") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl_atomic(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent,
                                     delete=False, suffix=".tmp") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


segments = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {row["segment_id"]: row for row in segments}
if len(segment_by_id) != len(segments) or not TARGET_IDS <= set(segment_by_id):
    raise SystemExit("missing or duplicate target segment metadata")
for segment_id in TARGET_IDS:
    meta = segment_by_id[segment_id]
    asset = ROOT / meta["source_file"]
    if hashlib.sha256(asset.read_bytes()).hexdigest() != meta["asset_sha256"]:
        raise SystemExit(f"source asset hash changed: {meta['source_file']}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
line_offsets = {}
for segment_id in TARGET_IDS:
    meta = segment_by_id[segment_id]
    lines = source_lines[meta["line_start"] - 1:meta["line_end"]]
    if hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest() != meta["sha256"]:
        raise SystemExit(f"segment content hash changed: {segment_id}")
    offset = 0
    for line_no, line in zip(range(meta["line_start"], meta["line_end"] + 1), lines):
        line_offsets[(segment_id, line_no)] = offset
        offset += len(line) + 1

candidate_fields, candidate_rows = read_csv(TABLES / "entity-candidates.csv")
mention_fields, mention_rows = read_csv(TABLES / "mentions.csv")
statement_rows = read_jsonl(TABLES / "book-statements.jsonl")
coverage_fields, coverage_rows = read_csv(TABLES / "s2-coverage.csv")
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
if len(coverage_by_id) != len(coverage_rows):
    raise SystemExit("duplicate S2 coverage segment IDs")
expected = {
    P226: ("reviewed", "partial", "L179-188"),
    P227: ("queued", "pending", ""),
}
for segment_id, state in expected.items():
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != state:
        raise SystemExit(f"unexpected coverage for {segment_id}: {row}")
if coverage_by_id[NOTES]["source_line_ranges"] != "L373-399":
    raise SystemExit("footnote coverage changed; inspect before proceeding")
if any(row["segment_id"] == P227 for row in mention_rows + statement_rows):
    raise SystemExit("p.227 rows already exist; inspect before rerunning")

new_candidates = [
    ("cand-7797", "Franceschini's proposed fanciful pastoral for Stefano Conti", "work", 191,
     "A proposed and accepted subject; the source does not establish that the painting was completed."),
    ("cand-7798", "Torelli's proposed Trojan-history painting of Pyrrhus and Polyxena", "work", 192,
     "A proposed composition described in a letter; it later arrived, but Conti asked what it represented."),
    ("cand-7799", "Six religious pictures by Gregorio Lazzarini for Stefano Conti", "work", 193,
     "A group of six Old and New Testament subjects; titles are not supplied."),
    ("cand-7800", "Three portraits of Stefano Conti and his family by Sebastiano Bombelli", "work", 197,
     "Portrait group of Conti, his wife and son; individual titles are not supplied."),
    ("cand-7801", "Marcantonio Franceschini letter dated 17 February 1705, MS 3299", "archive", 400,
     "Cited in note 1 at Biblioteca Governativa, Lucca; full text is referred to Appendix 3 and was not independently read."),
    ("cand-7802", "Unidentified letter dated 24 February 1705, MS 3299", "archive", 401,
     "Cited in note 2 at Biblioteca Governativa, Lucca for the proposed Torelli composition; signer is not inferred."),
    ("cand-7803", "Biblioteca Governativa, Lucca", "institution", 400,
     "Repository named in notes 1 and 2; no manuscript was independently consulted."),
    ("cand-7804", "Seven fruit and animal pictures by Giovanni Agostino Cassana", "work", 198,
     "A commissioned group of seven pictures; individual titles are not supplied."),
    ("cand-7805", "Unspecified landscapes by other artists in Stefano Conti's gallery", "work", 199,
     "The source mentions a number of landscapes without naming their makers or titles."),
    ("cand-7806", "Three views of Venice by Luca Carlevarijs owned by Stefano Conti", "work", 199,
     "A group of three views; titles are not supplied."),
    ("cand-7807", "Busts of Diana and Endymion by Giuseppe Mazza", "work", 200,
     "A pair of busts said to complete Conti's gallery; no further object details are given."),
    ("cand-7808", "Angiolo Trevisani", "person", 196,
     "The page reads Angiolo Trevisani; do not merge with the index candidate for Francesco Trevisani."),
    ("cand-7809", "The Venetian tenebrosi", "term", 196,
     "Artistic group named in Haskell's contrast; no membership list is supplied."),
    ("cand-7810", "Stefano Conti's three unnamed daughters", "", 197,
     "Collective reference only; the daughters are not individually identified and no group type is forced."),
    ("cand-7811", "Endymion", "person", 200,
     "Mythological figure named as the subject of one of Mazza's busts."),
    ("cand-7812", "Adam", "person", 191,
     "Biblical figure named as one possible subject proposed by Franceschini."),
    ("cand-7813", "Eve", "person", 191,
     "Biblical figure named as one possible subject proposed by Franceschini."),
    ("cand-7814", "Bacchus", "person", 191,
     "Mythological figure named as one possible subject proposed by Franceschini."),
    ("cand-7815", "Ariadne", "person", 191,
     "Mythological figure named as one possible subject proposed by Franceschini."),
    ("cand-7816", "Pyrrhus", "person", 192,
     "Mythological figure named in Torelli's proposed Trojan-history composition."),
    ("cand-7817", "Polyxena", "person", 192,
     "Mythological figure named in Torelli's proposed Trojan-history composition."),
    ("cand-7818", "Chalchas (as printed)", "person", 192,
     "Name as printed in the source OCR/PDF transcription; identity and spelling remain unresolved."),
    ("cand-7820", "Antinorus (as printed)", "person", 192,
     "Name as printed in the source; do not silently normalize to another figure."),
    ("cand-7821", "Achilles", "person", 192,
     "Mythological figure identified from the page image; OCR in the source line reads Acliilles."),
    ("cand-7822", "Landscape by Francesco Bassi intended to complete a set of four", "work", 203,
     "An intended acquisition in 1725; the source says Conti was trying to obtain it, not that he did."),
    ("cand-7823", "Two further Venice views by Luca Carlevarijs sought by Stefano Conti in 1725", "work", 203,
     "Intended additional views, distinct from the three Carlevarijs views already owned; the source does not say Conti acquired them."),
]
candidate_ids = {row["candidate_id"] for row in candidate_rows}
existing_keys = {(row["canonical_name"], row["suggested_type"]) for row in candidate_rows if not row["index_entry_id"]}
new_keys = set()
for candidate_id, name, kind, source_line, detail in new_candidates:
    if candidate_id in candidate_ids:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    if (name, kind) in existing_keys or (name, kind) in new_keys:
        raise SystemExit(f"candidate natural-key collision: {(name, kind)}")
    new_keys.add((name, kind))
    anchor_segment = NOTES if source_line >= 400 else P227
    candidate_rows.append({
        "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{anchor_segment}#L{source_line}",
    })
    candidate_ids.add(candidate_id)

new_mentions = []
existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mention_rows}


def mention(segment_id, source_line, suffix, candidate_id, surface, note, occurrence=0):
    mention_id = f"m-chp8-p227-{suffix}"
    if mention_id in existing_mention_ids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in candidate_ids:
        raise SystemExit(f"missing mention candidate: {mention_id} -> {candidate_id}")
    line = source_lines[source_line - 1]
    search_at = 0
    found_at = -1
    for _ in range(occurrence + 1):
        found_at = line.find(surface, search_at)
        if found_at < 0:
            raise SystemExit(f"surface not found at L{source_line}: {surface!r} #{occurrence}")
        search_at = found_at + 1
    start = line_offsets[(segment_id, source_line)] + found_at
    end = start + len(surface)
    span = (segment_id, str(start), str(end))
    if span in existing_spans or any((r["segment_id"], r["start_char"], r["end_char"]) == span for r in new_mentions):
        raise SystemExit(f"duplicate mention span: {span}")
    new_mentions.append({"mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
                         "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


# The two line 191 spellings are preserved as transcribed; only Acliilles is corrected from the page image.
mentions = [
    (P227,191,"conti-practice","cand-7787","this sometimes led to problems","Coreference to the per-figure pricing practice begun on p.226."),
    (P227,191,"franceschini-1","cand-1069","Marcantonio Franceschini","Artist and letter writer reported by Haskell."),
    (P227,191,"bologna-1","cand-3398","Bologna","City from which Franceschini wrote."),
    (P227,191,"conti-gentleman","cand-0833","the gentleman","Franceschini's indirect reference to his patron, Stefano Conti."),
    (P227,191,"adam","cand-7812","Adam","Proposed subject named by Franceschini."),
    (P227,191,"eve","cand-7813","Eve","Proposed subject named by Franceschini."),
    (P227,191,"bacchus","cand-7814","Bacchus","Proposed subject named by Franceschini."),
    (P227,191,"ariadne","cand-7815","Ariadne","Proposed subject named by Franceschini."),
    (P227,191,"pastoral-work","cand-7797","a fanciful pastoral","Proposed composition accepted as a subject; completion is not stated."),
    (P227,192,"torelli","cand-2645","Felice Torelli","Reuse index candidate."),
    (P227,192,"trojan-work","cand-7798","a scene from Trojan history","Torelli's proposed painting subject."),
    (P227,192,"pyrrhus-1","cand-7816","Pyrrhus","Subject of the proposed painting."),
    (P227,192,"polyxena","cand-7817","Polyxena","Subject of the proposed painting."),
    (P227,192,"chalchas","cand-7818","Chalchas","Printed name retained as given; identity/spelling unresolved."),
    (P227,192,"aeneas","cand-4164","Aeneas","Reuse the existing mythological-person candidate from the front-matter plate list."),
    (P227,192,"antinorus","cand-7820","Antinorus","Printed name retained as given; do not normalize without evidence."),
    (P227,192,"achilles","cand-7821","Acliilles","OCR spelling corrected to Achilles against the page image."),
    (P227,192,"pyrrhus-2","cand-7816","Pyrrhus","Second occurrence in the phrase identifying Achilles as Pyrrhus's father.",1),
    (P227,192,"conti-arrival","cand-0833","Conti","Subject of the report that the painting arrived and he asked what it represented."),
    (P227,193,"venice","cand-3401","Venetian","Regional reference to the artists discussed on this page."),
    (P227,193,"lazzarini-1","cand-1368","Lazzarini","Reuse index candidate."),
    (P227,193,"religious-group","cand-7799","six subjects from the Old and New Testaments","Six paintings reported by Haskell; titles not supplied."),
    (P227,194,"conti-gallery","cand-7785","Conti’s gallery","The gallery whose appearance Haskell characterizes."),
    (P227,195,"marchesini","cand-1540","Marchesini","Artist and Conti's agent."),
    (P227,195,"lazzarini-2","cand-1368","Lazzarini","Artist included among Conti's selected painters."),
    (P227,196,"balestra","cand-0168","Balestra","Artist included among Conti's selected painters."),
    (P227,196,"fumiani","cand-1087","Fumiani","Artist included among Conti's selected painters."),
    (P227,196,"bellucci","cand-0282","Bellucci","Artist included among Conti's selected painters."),
    (P227,196,"trevisani","cand-7808","Angiolo Trevisani","Exact name on the page; not the indexed Francesco Trevisani."),
    (P227,196,"segala","cand-2417","Segala","Artist included among Conti's selected painters."),
    (P227,196,"dal-sole","cand-2480","Dal Sole","Reuse index candidate for Giovan Gioseffo dal Sole."),
    (P227,196,"franceschini-2","cand-1069","Franceschini","Reuse index candidate; second mention on p.227."),
    (P227,196,"tenebrosi","cand-7809","tenebrosi","Named artistic group in Haskell's contrast."),
    (P227,197,"conti-wife","cand-7792","his wife","Reuse unnamed wife candidate from p.226."),
    (P227,197,"conti-son","cand-7793","his son","Reuse unnamed only son candidate from p.226."),
    (P227,197,"conti-self","cand-0833","himself","Coreference to Stefano Conti."),
    (P227,197,"bombelli","cand-0383","Sebastiano Bombelli","Leading portraitist named by Haskell."),
    (P227,197,"franchi","cand-1074","Antonio Franchi","Local artist considered suitable for the daughters; execution is not asserted."),
    (P227,197,"daughters","cand-7810","his three daughters","Collective reference; none is individually identified."),
    (P227,197,"portrait-group","cand-7800","the portraits of his wife, his son and himself","Group of three portraits attributed in the text to Bombelli."),
    (P227,198,"cassana-given-name","cand-0592","Giovanni Agostino","Artist commissioned for seven fruit and animal pictures; surname continues on the next source line."),
    (P227,198,"fruit-animal-group","cand-7804","seven pictures of fruit and animals","Commissioned group; individual titles not supplied."),
    (P227,199,"landscapes","cand-7805","a number of landscapes","Unnamed works by other artists."),
    (P227,199,"carlevarijs-given-name","cand-0554","Luca","Artist of three Venice views; surname continues on the next source line."),
    (P227,200,"carlevarijs-surname","cand-0554","Carlevarijs","Completion of the name begun on the previous source line."),
    (P227,199,"venice-views","cand-7806","three views of Venice","Works owned by Conti."),
    (P227,200,"mazza","cand-1602","Giuseppe Mazza","Bolognese sculptor named by Haskell."),
    (P227,200,"diana","cand-4136","Diana","Subject of one bust."),
    (P227,200,"endymion","cand-7811","Endymion","Subject of one bust."),
    (P227,200,"bust-pair","cand-7807","Busts of Diana and Endymion","Pair of busts completing the gallery."),
    (P227,201,"correggio-work","cand-0853","a ‘Correggio’ Christ in the Garden of Olives","Work retained under the reported Correggio attribution; quotation marks preserved."),
    (P227,201,"guercino","cand-1258","a Guercino","Reuse the artist candidate; work title continues on the next source line."),
    (P227,202,"flight-egypt","cand-1264","Flight into Egypt","Reuse indexed work candidate; source line break follows the painter's name."),
    (P227,202,"brugiori","cand-0456","Domenico Brugiori","Local artist named as the painter of Cain and Abel."),
    (P227,202,"cain-abel","cand-0457","a Cain and Abel","Reuse indexed work candidate."),
    (P227,203,"date-1725","cand-0833","1725","Date attached to Conti's resumption of collecting."),
    (P227,203,"marchesini-2","cand-1540","Alessandro Marchesini","Conti again sought his advice."),
    (P227,203,"conti-collecting","cand-0833","Conti","Collector resuming activity in 1725."),
    (P227,203,"extra-views","cand-7823","two further views by Carlevarijs","Conti was trying to obtain two additional views, distinct from the three he already owned."),
    (P227,203,"bassi","cand-0259","Francesco Bassi","Reuse indexed candidate; the source says one landscape was sought."),
    (P227,204,"bassi-alias","cand-0259","Cremonese","Alias continues from 'il' at the end of the previous source line; do not create a separate person."),
    (P227,203,"bassi-landscape","cand-7822","one landscape by Francesco Bassi","Proposed acquisition intended to complete a set of four; completion is not asserted."),
    (P227,204,"venice-city-2","cand-3401","Venice","City whose artistic situation is said to have changed."),
    (P227,204,"carlevarijs-2","cand-0554","Carlevarijs","Marchesini's description begins and continues on p.228."),
    (NOTES,400,"letter-1","cand-7801","a letter of 17 February 1705","Archive source cited in note 1; full text only referred to Appendix 3."),
    (NOTES,400,"library","cand-7803","Biblioteca Governativa","Repository identified in the note."),
    (NOTES,400,"lucca","cand-1454","Lucca","City locating the repository."),
    (NOTES,401,"letter-2","cand-7802","a letter of 24 February 1705","Separate cited letter; signer not inferred."),
    (NOTES,401,"library-2","cand-7803","Biblioteca Governativa","Same repository as note 1."),
    (NOTES,401,"lucca-2","cand-1454","Lucca","City locating the repository."),
    (NOTES,402,"da-canal-citation","cand-6593","Da Canal, pp. 40, 58, 59","Reuse the already indexed 1809 Vita volume; cited pages differ from the earlier p.69 note."),
]
for row in mentions:
    mention(*row)


def quote(segment_id: str, first: int, last: int) -> str:
    return "\n".join(source_lines[first - 1:last])


def make_statement(statement_id, segment_id, first, last, subject, obj, predicate, claim,
                   qualification, mentioned, text_layer="body", extras=None):
    meta = segment_by_id[segment_id]
    if first < meta["line_start"] or last > meta["line_end"]:
        raise SystemExit(f"statement lines outside segment: {statement_id}")
    if any(cid not in candidate_ids for cid in [subject, obj, *mentioned] if cid):
        raise SystemExit(f"statement has missing candidate: {statement_id}")
    qualifiers = {"source_line_start": first, "source_line_end": last, "printed_page": 227,
                  "pdf_physical_page": 29, "claim": claim, "speaker": "Haskell",
                  "text_layer": text_layer, "qualification": qualification,
                  "mentioned_candidate_ids": list(dict.fromkeys(mentioned))}
    if extras:
        qualifiers.update(extras)
    return {"statement_id": statement_id, "segment_id": segment_id,
            "subject_candidate_id": subject, "object_candidate_id": obj, "predicate": predicate,
            "qualifiers": qualifiers, "original_quote": quote(segment_id, first, last),
            "origin": "book", "source_file": meta["source_file"]}


new_statements = [
    make_statement("st-chp8-p227-pricing-problems", P227, 191, 191, "cand-0833", "cand-7787",
                   "per_figure_payment_caused_problems_and_franceschini_objected",
                   "Haskell says Conti's per-figure payment practice sometimes caused problems; Franceschini wrote that it was difficult to find a history or fable with two figures and putti and would prefer Conti to choose.",
                   "The report is attributed to a letter from Franceschini; it closes the p.226 open statement but does not define a complete tariff.",
                   ["cand-0833", "cand-7787", "cand-1069", "cand-3398"], extras={"reported_speaker": "Marcantonio Franceschini", "continued_from_segment_id": P226, "continued_from_statement_id": "st-chp8-p226-conti-per-figure-payment-open", "continuation_status": "closed"}),
    make_statement("st-chp8-p227-franceschini-proposes-pastoral", P227, 191, 191, "cand-1069", "cand-7797",
                   "proposed_and_accepted_fanciful_pastoral_subject",
                   "Franceschini suggested sacred and profane subjects, including a fanciful pastoral with a shepherd, nymph and two or three putti; the suggestion was accepted.",
                   "Acceptance concerns the subject proposal; the text does not say the painting was completed.",
                   ["cand-1069", "cand-7797", "cand-0833", "cand-7812", "cand-7813", "cand-7814", "cand-7815"], extras={"reported_speaker": "Marcantonio Franceschini", "relation_candidate": True, "ocr_corrections": [{"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 191, "ocr": "curio so .", "print": "curioso.", "basis": "CHP-8.pdf physical page 29."}]}),
    make_statement("st-chp8-p227-torelli-proposed-scene", P227, 192, 192, "cand-2645", "cand-7798",
                   "proposed_trojan_history_painting_and_later_identification_question",
                   "Torelli proposed a Trojan-history scene of Pyrrhus killing Polyxena with additional named figures and the tomb of Achilles; Conti accepted a picture of this kind, but after it arrived asked what it represented.",
                   "The proposed composition and its later arrival are reported; the exact identity of the delivered picture remains uncertain in Haskell's account.",
                   ["cand-2645", "cand-7798", "cand-0833", "cand-7816", "cand-7817", "cand-7818", "cand-4164", "cand-7820", "cand-7821"], extras={"relation_candidate": True, "ocr_corrections": [{"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 192, "ocr": "Acliilles", "print": "Achilles", "basis": "CHP-8.pdf physical page 29."}]}),
    make_statement("st-chp8-p227-venetian-subjects", P227, 193, 193, "cand-1368", "cand-7799",
                   "lazzarini_painted_six_morally_impeccable_biblical_subjects",
                   "Haskell contrasts Venetian artists' usual stock biblical and mythological scenes with a preponderance of religious painting, and says Lazzarini painted six morally impeccable Old and New Testament subjects.",
                   "The comparison and 'impeccable morality' are Haskell's characterization, not independently assessed qualities.",
                   ["cand-1368", "cand-7799", "cand-3401"], extras={"speaker_judgment": True, "ocr_corrections": [{"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 193, "ocr": "evenLazzarini", "print": "even Lazzarini", "basis": "CHP-8.pdf physical page 29."}]}),
    make_statement("st-chp8-p227-gallery-academic-style", P227, 194, 196, "cand-0833", "cand-7785",
                   "gallery_had_academic_appearance_and_correct_drawing_style",
                   "Haskell says Conti's completed gallery had a notably academic appearance: his generation of selected painters mostly followed correct drawing and blond tonality, opposed to the successful Venetian tenebrosi.",
                   "'Academic', 'correct', and the opposition are Haskell's stylistic judgments; the source names Angiolo Trevisani, not the indexed Francesco Trevisani.",
                   ["cand-0833", "cand-7785", "cand-1540", "cand-1368", "cand-0168", "cand-1087", "cand-0282", "cand-7808", "cand-2417", "cand-2480", "cand-1069", "cand-7809"], extras={"speaker_judgment": True, "ocr_corrections": [{"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 195, "ocr": "’ ‘academic’", "print": "‘academic’", "basis": "CHP-8.pdf physical page 29."}]}),
    make_statement("st-chp8-p227-conti-portraits", P227, 197, 197, "cand-0833", "cand-7800",
                   "commissioned_family_portraits_from_bombelli_and_considered_franchi_for_daughters",
                   "Conti had portraits of himself, his wife and son painted by Sebastiano Bombelli; Haskell adds that local artist Antonio Franchi was considered good enough for Conti's three daughters.",
                   "The text explicitly reports Bombelli portraits; the Franchi sentence is not expanded into a completed commission or named portraits.",
                   ["cand-0833", "cand-7800", "cand-0383", "cand-7792", "cand-7793", "cand-1074", "cand-7810"], extras={"relation_candidate": True}),
    make_statement("st-chp8-p227-gallery-other-works", P227, 198, 200, "cand-0833", "cand-7804",
                   "commissioned_still_lifes_landscapes_venice_views_and_busts",
                   "Conti commissioned seven fruit and animal pictures from Cassana, acquired unnamed landscapes and three Venice views by Carlevarijs, and completed the gallery with Mazza's paired busts of Diana and Endymion.",
                   "Only counts and makers stated by the text are recorded; unnamed landscapes remain unidentified.",
                   ["cand-0833", "cand-0592", "cand-7804", "cand-7805", "cand-0554", "cand-7806", "cand-1602", "cand-7807", "cand-4136", "cand-7811"], extras={"relation_candidate": True}),
    make_statement("st-chp8-p227-three-purchases", P227, 201, 202, "cand-0833", "cand-0853",
                   "bought_only_three_pictures_for_nearly_twenty_years",
                   "For nearly twenty years Conti bought only three pictures: a Christ in the Garden of Olives attributed to 'Correggio', Guercino's Flight into Egypt, and Brugiori's Cain and Abel.",
                   "The Correggio attribution remains qualified by the source's quotation marks; the statement does not independently identify any work.",
                   ["cand-0833", "cand-0853", "cand-1264", "cand-0456", "cand-0457"], extras={"relation_candidate": True}),
    make_statement("st-chp8-p227-resumed-collecting-1725", P227, 203, 203, "cand-0833", "cand-1540",
                   "resumed_collecting_and_sought_advice_from_marchesini_in_1725",
                   "In 1725 Conti resumed collecting and again sought Marchesini's advice; he was trying to obtain two additional Carlevarijs views and one landscape by Francesco Bassi to complete a set of four.",
                   "The source says Conti was trying to obtain these works, not that the acquisitions or complete set were achieved.",
                   ["cand-0833", "cand-1540", "cand-0554", "cand-7806", "cand-7823", "cand-0259", "cand-7822"], extras={"relation_candidate": True, "date": "1725", "ocr_corrections": [{"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 203, "ocr": "- 1725", "print": "1725", "basis": "CHP-8.pdf physical page 29."}]}),
    make_statement("st-chp8-p227-carlevarijs-transformed-scene-open", P227, 204, 204, "cand-0554", "cand-1540",
                   "marchesini_begins_assessment_of_changed_venetian_art_scene_open",
                   "Haskell says the Venetian artistic situation had changed completely over the previous twenty years and begins to quote Marchesini's assessment of Carlevarijs.",
                   "The sentence ends before Marchesini's description is complete; continue at p.228 L206.",
                   ["cand-0554", "cand-1540", "cand-3401"], extras={"speaker_judgment": True, "relation_candidate": True, "continuation_status": "open", "continuation_to_segment_id": P228, "continuation_to_source_line": 206}),
    make_statement("st-chp8-p227-note1-letter-location", NOTES, 400, 400, "cand-7801", "cand-7803",
                   "footnote_locates_franceschini_letter_and_refers_to_appendix_text",
                   "Note 1 identifies a letter dated 17 February 1705 at Biblioteca Governativa, Lucca, MS 3299, and refers readers to Appendix 3 for the relevant section's full text.",
                   "This is Haskell's source locator; the manuscript and appendix were not independently checked in this migration.",
                   ["cand-7801", "cand-1069", "cand-7803", "cand-1454"], text_layer="footnote citation", extras={"relation_candidate": False}),
    make_statement("st-chp8-p227-note2-letter-location", NOTES, 401, 401, "cand-7802", "cand-7803",
                   "footnote_locates_unidentified_letter_for_torelli_proposal",
                   "Note 2 identifies a letter dated 24 February 1705 at Biblioteca Governativa, Lucca, MS 3299, and refers readers to Appendix 3.",
                   "The note does not name the writer; signer and manuscript wording remain unverified.",
                   ["cand-7802", "cand-7803", "cand-1454", "cand-2645", "cand-7798"], text_layer="footnote citation", extras={"relation_candidate": False}),
    make_statement("st-chp8-p227-note3-da-canal-reference", NOTES, 402, 402, "cand-7781", "cand-7799",
                   "footnote_cites_da_canal_pages_for_lazzarini_subjects",
                   "Note 3 cites Da Canal, pages 40, 58 and 59, in support of the preceding account of Lazzarini's subjects.",
                   "The citation is reused as a locator; the cited pages were not independently read here.",
                   ["cand-7781", "cand-6593", "cand-1368", "cand-7799"], text_layer="footnote citation", extras={"relation_candidate": False}),
]

statement_ids = {row["statement_id"] for row in statement_rows}
if len(statement_ids) != len(statement_rows) or any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("duplicate statement ID")
prior_id = "st-chp8-p226-conti-per-figure-payment-open"
prior = next((row for row in statement_rows if row["statement_id"] == prior_id), None)
if not prior or prior["qualifiers"].get("continuation_status") != "open":
    raise SystemExit("expected open p.226 payment statement not found")
patched_prior = json.loads(json.dumps(prior))
patched_prior["qualifiers"].update({"continuation_status": "closed", "continued_to_segment_id": P227,
                                    "continued_to_source_line": 191,
                                    "continuation_closed_by_statement_id": "st-chp8-p227-pricing-problems"})

for row in coverage_rows:
    if row["segment_id"] == P226:
        row.update({"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L179-188",
                    "note": "p.226 per-figure payment statement closes at p.227 L190-191."})
    elif row["segment_id"] == P227:
        row.update({"disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L190-204",
                    "note": "p.227 read against CHP-8.pdf physical page 29; Carlevarijs sentence continues at p.228 L206."})
    elif row["segment_id"] == NOTES:
        row.update({"source_line_ranges": "L373-402", "migration_status": "partial",
                    "note": "p.227 notes 1-3 at L400-402 migrated; later consolidated notes remain queued by printed page."})

preview = {"mode": "dry-run", "candidate_additions": len(new_candidates), "mention_additions": len(new_mentions),
           "statement_additions": len(new_statements),
           "closed_continuation": {"statement_id": prior_id, "to": P227, "line": 191},
           "open_continuation": {"statement_id": "st-chp8-p227-carlevarijs-transformed-scene-open", "to": P228, "line": 206},
           "coverage": {P226: "complete", P227: "partial", NOTES: "L373-402 partial"},
           "ocr_corrections": ["L191 curio so . -> curioso.", "L192 Acliilles -> Achilles", "L193 evenLazzarini -> even Lazzarini", "L195 remove stray leading quote before ‘academic’", "L203 remove OCR hyphen before 1725"]}

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="apply the preflighted S2 migration")
args = parser.parse_args()
if not args.apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)

for path in (TABLES / "entity-candidates.csv", TABLES / "mentions.csv", TABLES / "book-statements.jsonl", TABLES / "s2-coverage.csv"):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(path, backup)
patched_statements = [patched_prior if row["statement_id"] == prior_id else row for row in statement_rows]
patched_statements.extend(new_statements)
write_csv_atomic(TABLES / "entity-candidates.csv", candidate_fields, candidate_rows)
write_csv_atomic(TABLES / "mentions.csv", mention_fields, mention_rows + new_mentions)
write_jsonl_atomic(TABLES / "book-statements.jsonl", patched_statements)
write_csv_atomic(TABLES / "s2-coverage.csv", coverage_fields, coverage_rows)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
