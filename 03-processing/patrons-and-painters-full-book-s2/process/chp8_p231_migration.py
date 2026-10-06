"""Controlled S2 migration for Chapter 8 printed page 231 and notes 1–6."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_ii.md"
P230 = "chp-8:08_CHP-8_sec_ii:l227-236"
P231 = "chp-8:08_CHP-8_sec_ii:l238-249"
P232 = "chp-8:08_CHP-8_sec_ii:l251-257"
NOTES = "chp-8:08_CHP-8_sec_ii:l372-461"
TARGET_IDS = {P230, P231, P232, NOTES}
BACKUP_SUFFIX = ".bak-s2-chp8-p231-20261001"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


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
expected_coverage = {
    P230: ("reviewed", "partial", "L227-236"),
    P231: ("queued", "pending", ""),
    P232: ("queued", "pending", ""),
}
for segment_id, state in expected_coverage.items():
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != state:
        raise SystemExit(f"unexpected coverage for {segment_id}: {row}")
if coverage_by_id[NOTES]["source_line_ranges"] != "L373-408":
    raise SystemExit("footnote coverage changed; inspect before proceeding")
if any(row["segment_id"] == P231 for row in mention_rows + statement_rows):
    raise SystemExit("p.231 rows already exist; inspect before rerunning")

new_candidates = [
    ("cand-7856", "Fra Bartolommeo's S. Marco (painting purchased by Ferdinand from an unnamed church)", "work", 247,
     "Specific painting indexed under Fra Bartolommeo; keep it distinct from the later copy mentioned in the same sentence."),
    ("cand-7857", "Unidentified copy after Fra Bartolommeo's S. Marco by Antonio Franchi (Pitti no.125)", "work", 247,
     "Haskell says Ferdinand had the original replaced by a copy in 1692; the copy is now cited as Pitti no.125. Do not assume its present identity beyond the source."),
    ("cand-7858", "Unidentified church dedicated to Saint Mark from which Fra Bartolommeo's S. Marco was removed", "place", 247,
     "The church is described but not named. The wording links its dedication to the saint represented by the title; exact building and geographic identity remain unresolved."),
    ("cand-7859", "Saint Mark (referred to as the saint in the S. Marco church passage)", "person", 247,
     "The source calls the church dedicated to 'that saint' immediately after naming the painting S. Marco; record the referent without aligning a specific church."),
    ("cand-7860", "La Burla del Pievano Arlotto (painting by Baldassare Franceschini)", "work", 243,
     "The specific painting Ferdinand bought before 1693; indexed under its maker, but preserved as a separate work object."),
    ("cand-7861", "Madonna del Baldacchino (Raphael painting acquired by Ferdinand)", "work", 247,
     "Specific painting named in the 1690s church-purchase passage; acquisition and present identity remain as reported by Haskell."),
    ("cand-7862", "Madonna delle Arpie (Andrea del Sarto painting acquired by Ferdinand)", "work", 247,
     "Specific painting named in the 1690s church-purchase passage; acquisition and present identity remain as reported by Haskell."),
    ("cand-7863", "Deposition (Cigoli painting acquired by Ferdinand; exact identity unresolved)", "work", 248,
     "Painting title and maker are stated, but no precise version or source church is identified."),
    ("cand-7864", "Martyrdom of St Cecilia (Orazio Riminaldi painting acquired by Ferdinand)", "work", 248,
     "Specific painting named in the 1690s church-purchase passage; acquisition and present identity remain as reported by Haskell."),
    ("cand-7865", "Cardinal Leopoldo de' Medici's collection of Renaissance works", "", 249,
     "A large collection amassed by Cardinal Leopold and later amplified by Ferdinand. Collection is not a current KU type; leave suggested_type unresolved."),
    ("cand-7866", "Giglioli, O. H., 1908 publication cited for the picture's history (identity unresolved)", "archive", 410,
     "Footnote 2 cites Giglioli 1908. The bibliography lists a 1908 article but the correspondence of that entry to this particular citation is not established."),
    ("cand-7867", "K. Steinbart, Die Gemalten Schwänke des Pfarrers Arlotto (1936)", "archive", 410,
     "Bibliography identifies the cited 1936 article in Pantheon; it was not independently consulted."),
    ("cand-7868", "Sebastiano Benedetto Bartolozzi, Vita di Antonio Franchi Lucchese, pittor fiorentino (Firenze 1754)", "archive", 411,
     "Identified from the book bibliography as the source cited for Antonio Franchi; the cited work was not independently consulted."),
    ("cand-7869", "[Bencivenni, già Pelli], Saggio istorico della Real Galleria di Firenze (2 vols., Firenze 1779)", "archive", 412,
     "Bibliography identifies the cited work; Haskell also cites its volumes I and II in note 6. Not independently consulted."),
    ("cand-7870", "A. Jahn-Rusconi, La R. Galleria Pitti in Firenze (Roma 1937)", "archive", 412,
     "Bibliography identifies the cited work; it was not independently consulted."),
    ("cand-7871", "Ignazio Enrico Hugford, Vita di Anton Domenico Gabbiani pittor fiorentino (Firenze 1762)", "archive", 413,
     "Bibliography identifies the cited work; it was not independently consulted."),
    ("cand-7872", "Aldo Bartarelli, Anton Domenico Gabbiani (Rivista d'Arte, 1951)", "archive", 413,
     "Bibliography identifies the cited article; it was not independently consulted."),
    ("cand-7873", "Classical and Marattesque canons of art in Haskell's account of Gabbiani", "term", 248,
     "A style description applied to Gabbiani by Haskell; do not convert it into a formal school or institution."),
    ("cand-7874", "Unspecified other painters of the Venetian sixteenth century mentioned by Haskell", "", 249,
     "A collective reference to additional painters whose names are not given in this passage; no individuals are inferred."),
    ("cand-7875", "Venetian sixteenth-century painting tradition in Haskell's account of Ferdinand", "term", 241,
     "The tradition exemplified by Titian, Veronese and Bassano, which Haskell contrasts with the Florentine Renaissance; retain as the author's art-historical framing."),
    ("cand-7876", "Saint Cecilia (named as the subject of Riminaldi's Martyrdom)", "person", 248,
     "The source names her only within the painting title; no independent biographical claim is made here."),
]
candidate_ids = {row["candidate_id"] for row in candidate_rows}
existing_keys = {(row["canonical_name"], row["suggested_type"])
                 for row in candidate_rows if not row["index_entry_id"]}
new_keys = set()
for candidate_id, name, kind, source_line, detail in new_candidates:
    if candidate_id in candidate_ids:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    if (name, kind) in existing_keys or (name, kind) in new_keys:
        raise SystemExit(f"candidate natural-key collision: {(name, kind)}")
    new_keys.add((name, kind))
    anchor_segment = NOTES if source_line >= 405 else P231
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
    mention_id = f"m-chp8-p231-{suffix}"
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
    if span in existing_spans or any((row["segment_id"], row["start_char"], row["end_char"]) == span for row in new_mentions):
        raise SystemExit(f"duplicate mention span: {span}")
    new_mentions.append({"mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
                         "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


mentions = [
    (P231,239,"venetian-1","cand-3401","Venetian","Adjectival reference to Venice in the continuing sentence."),
    (P231,240,"europe","cand-3462","Europe","Geographic extent of the comparison."),
    (P231,240,"ferdinand-coref-1","cand-1609","he","Coreference to Ferdinand."),
    (P231,241,"titian-1","cand-2630","Titian","Artist named among the Venetian masters."),
    (P231,241,"veronese-1","cand-2755","Veronese","Artist named among the Venetian masters."),
    (P231,241,"bassano-1","cand-0257","Bassano","Surname-level painter reference; retain indexed candidate pending alignment."),
    (P231,242,"florentine","cand-3397","Florentine","Adjectival reference to Florence."),
    (P231,242,"renaissance-1","cand-3578","Renaissance","Art-historical period/category in the comparison."),
    (P231,242,"ferdinand-1","cand-1609","Ferdinand","Named subject of the passage."),
    (P231,242,"tradition-1","cand-7875","this tradition","Coreference to the sixteenth-century Venetian painting tradition."),
    (P231,243,"florentine-art","cand-3397","Florentine","Adjectival reference to Florence."),
    (P231,243,"franceschini-1","cand-1066","Baldassare Franceschini","Painter named by Haskell."),
    (P231,243,"cortona","cand-0342","Pietro da Cortona","Artist named as Franceschini's stylistic predecessor."),
    (P231,243,"franceschini-artist-coref","cand-1066","this artist","Coreference to Franceschini."),
    (P231,243,"burla-coref","cand-7860","one picture","The specific painting is named in the continuation at L244."),
    (P231,244,"franceschini-2","cand-1066","Franceschini","Painter named as the maker of the work."),
    (P231,243,"la-burla","cand-7860","La Burla del Pievano Arlotto","Specific work object; its maker is separately mapped to Franceschini."),
    (P231,243,"arlotto","cand-4167","Pievano Arlotto","Person named within the work title."),
    (P231,245,"tuscan","cand-6232","Tuscan","Adjectival reference to Tuscany."),
    (P231,245,"italy","cand-3461","Italy","Geographic contrast in Haskell's account."),
    (P231,245,"naturalism","cand-5739","naturalism","Art-historical tendency in Haskell's comparison."),
    (P231,246,"ferdinand-2","cand-1609","Ferdinand","Named subject of the statement."),
    (P231,246,"crespi","cand-0871","Crespi","Surname-level reference to Giuseppe Maria Crespi."),
    (P231,247,"bartolommeo","cand-0253","Fra Bartolommeo","Artist linked to the S. Marco painting."),
    (P231,247,"s-marco","cand-7856","S. Marco","Specific work, kept distinct from Fra Bartolommeo as its maker."),
    (P231,247,"mark-church","cand-7858","the church dedicated to that saint","Unidentified church described as the source of the painting."),
    (P231,247,"saint-mark","cand-7859","that saint","Coreference to Saint Mark in the dedication phrase."),
    (P231,247,"copy","cand-7857","a copy","Copy of the S. Marco painting, identity not otherwise specified."),
    (P231,247,"ferdinand-name","cand-1609","Ferdinand","Named patron and collector."),
    (P231,247,"florence","cand-3397","Florence","City from whose churches Haskell says pictures were acquired."),
    (P231,247,"raphael","cand-2102","Raphael","Artist named for the Madonna del Baldacchino."),
    (P231,247,"baldacchino","cand-7861","Madonna del Baldacchino","Specific work by Raphael."),
    (P231,247,"virgin-mary-1","cand-3427","Madonna","Religious figure named within the Raphael painting title."),
    (P231,247,"sarto","cand-2362","Andrea del Sarto","Artist named in Ferdinand's purchases."),
    (P231,247,"arpie","cand-7862","Madonna delle Arpie","Specific work by Andrea del Sarto."),
    (P231,247,"virgin-mary-2","cand-3427","Madonna","Religious figure named within the Andrea del Sarto painting title.",1),
    (P231,248,"cigoli","cand-0757","Cigoli","Artist named for the Deposition."),
    (P231,248,"deposition","cand-7863","Deposition","Specific work by Cigoli; exact version unresolved."),
    (P231,248,"riminaldi","cand-2201","Orazio Riminaldi","Artist named for the Martyrdom."),
    (P231,248,"martyrdom","cand-7864","Martyrdom of St Cecilia","Specific work by Orazio Riminaldi."),
    (P231,248,"cecilia","cand-7876","St Cecilia","Saint named within the work title."),
    (P231,248,"gabbiani","cand-1093","Anton Domenico Gabbiani","Contemporary painter in whom Ferdinand showed interest."),
    (P231,248,"marattesque","cand-7873","Marattesque canons of art","Haskell's characterization of Gabbiani's artistic principles."),
    (P231,248,"ferdinand-loyal","cand-1609","Ferdinand","Named subject of the statement."),
    (P231,249,"ferdinand-visits","cand-1609","his visits","Coreference to Ferdinand."),
    (P231,249,"venice","cand-3401","Venice","City whose art influenced Ferdinand."),
    (P231,249,"venetian-art","cand-7875","Venetian art","Adjectival reference to the sixteenth-century Venetian painting tradition."),
    (P231,249,"medici-court","cand-5520","Medici court","Institutional/patronage context."),
    (P231,249,"cardinal-leopold","cand-1629","Cardinal Leopold","Ferdinand's great uncle and collector."),
    (P231,249,"collection-1","cand-7865","a very large collection of works by masters of the Renaissance","The collection amassed by Cardinal Leopold."),
    (P231,249,"renaissance-2","cand-3578","Renaissance","Art-historical category in the collection description."),
    (P231,249,"ferdinand-amplify","cand-1609","Ferdinand","Named subject who set out to expand the collection."),
    (P231,249,"collection-2","cand-7865","this collection","Coreference to Cardinal Leopold's collection."),
    (P231,249,"titian-2","cand-2630","Titian","Artist named as recurring in Ferdinand's letters."),
    (P231,249,"veronese-2","cand-2755","Veronese","Artist named as recurring in Ferdinand's letters."),
    (P231,249,"bassano-2","cand-0257","Bassano","Surname-level painter reference; retain indexed candidate pending alignment."),
    (P231,249,"palma","cand-1811","Palma Giovane","Painter named among the Venetian sixteenth-century artists."),
    (P231,249,"other-painters","cand-7874","many other painters of the Venetian sixteenth century","Unspecified artist group; individuals are not named here."),
    (P231,249,"venetian-century","cand-3401","Venetian","Adjectival reference to Venice."),
    (P231,249,"ferdinand-letter-coref","cand-1609","he","Coreference to Ferdinand as letter writer."),
    (NOTES,409,"baldinucci","cand-4846","Baldinucci, VI, 1728","Citation supporting the reported Franceschini death date."),
    (NOTES,410,"pitti-582","cand-1949","Pitri","OCR surface for Pitti; exact institutional identity follows the index label."),
    (NOTES,410,"giglioli","cand-7866","Giglioli, 1908","Bibliography identifies one possible item; exact citation identity remains unresolved."),
    (NOTES,410,"steinbart","cand-7867","Steinhart, 1936","Cited article identified from the bibliography."),
    (NOTES,411,"pitti-125","cand-1949","Pitri","OCR surface for Pitti."),
    (NOTES,411,"copy-franchi","cand-7857","The copy","Coreference to the copy after Fra Bartolommeo's S. Marco."),
    (NOTES,411,"franchi","cand-1074","Antonio Franchi","Painter of the copy as reported in the footnote."),
    (NOTES,411,"bartolozzi","cand-7868","Bartolozzi","Cited work identified from the bibliography."),
    (NOTES,412,"florentine-churches","cand-3397","Florentine","Adjectival reference to Florence."),
    (NOTES,412,"bencivenni-1","cand-7869","Bencivenni","Cited publication identified from the bibliography."),
    (NOTES,412,"jahn-rusconi","cand-7870","Jahn-Rusconi","Cited publication identified from the bibliography."),
    (NOTES,413,"hugford","cand-7871","Hugford","Cited publication identified from the bibliography."),
    (NOTES,413,"bartarelli","cand-7872","Bartarelli","Cited article identified from the bibliography."),
    (NOTES,414,"cardinal-leopold-note","cand-1629","Cardinal Leopold","Person whose collecting is discussed."),
    (NOTES,414,"bencivenni-2","cand-7869","Bencivenni", "Second citation to the same bibliography-identified work."),
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
    if any(candidate_id not in candidate_ids for candidate_id in [subject, obj, *mentioned] if candidate_id):
        raise SystemExit(f"statement has missing candidate: {statement_id}")
    qualifiers = {"source_line_start": first, "source_line_end": last, "printed_page": 231,
                  "pdf_physical_page": 33, "claim": claim, "speaker": "Haskell",
                  "text_layer": text_layer, "qualification": qualification,
                  "mentioned_candidate_ids": list(dict.fromkeys(mentioned))}
    if extras:
        qualifiers.update(extras)
    return {"statement_id": statement_id, "segment_id": segment_id,
            "subject_candidate_id": subject, "object_candidate_id": obj, "predicate": predicate,
            "qualifiers": qualifiers, "original_quote": quote(segment_id, first, last),
            "origin": "book", "source_file": meta["source_file"]}


new_statements = [
    make_statement("st-chp8-p231-venetian-pictures-recalled", P231,239,240,"cand-1609",None,
                   "remembered_venetian_pictures_and_hoped_to_acquire_some",
                   "Continuing the p.230 account, Haskell says Ferdinand studied great pictures in Venetian collections and churches, which he describes as Europe's richest, and years later recalled some that he hoped to acquire.",
                   "The unnamed pictures are not individually identified; the comparative judgment about Venetian collections and churches is Haskell's.",
                   ["cand-1609","cand-3401","cand-3462"], extras={"continued_from_segment_id":P230,"continued_from_statement_id":"st-chp8-p230-venice-memory-observation-open","continuation_status":"closed","relation_candidate":True}),
    make_statement("st-chp8-p231-hosts-titian-veronese-bassano", P231,241,242,"cand-1609","cand-7875",
                   "saw_venetian_painting_tradition_in_hosts_palaces",
                   "Haskell says Ferdinand saw a painting tradition in masterpieces by Titian, Veronese and Bassano in his hosts' palaces, a tradition long considered the antithesis of the Florentine Renaissance.",
                   "The tradition and historical comparison are Haskell's account; the passage does not identify the palaces or particular paintings.",
                   ["cand-1609","cand-2630","cand-2755","cand-0257","cand-3578","cand-7875"], extras={"speaker_judgment":True}),
    make_statement("st-chp8-p231-ferdinand-seduced-by-venetian-tradition", P231,242,242,"cand-1609","cand-7875",
                   "was_seduced_by_venetian_tradition_and_wanted_to_revive_it",
                   "Haskell says Ferdinand was seduced by the Venetian tradition and longed to make it live again.",
                   "This describes Haskell's interpretation of Ferdinand's taste, not a specific completed commission.",
                   ["cand-1609","cand-7875"], extras={"speaker_judgment":True}),
    make_statement("st-chp8-p231-early-picture-collection", P231,243,243,"cand-1609",None,
                   "early_pictures_resembled_average_noble_collection_and_included_franceschini_works",
                   "Haskell says Ferdinand's early acquired pictures differed little from an average noble collection and included religious works painted for him by Baldassare Franceschini.",
                   "The source gives no titles for the other religious works in this group.",
                   ["cand-1609","cand-1066"], extras={"relation_candidate":True}),
    make_statement("st-chp8-p231-franceschini-biography", P231,243,243,"cand-1066","cand-0342",
                   "described_as_late_follower_of_cortona_and_died_1689",
                   "Haskell describes Franceschini as a late follower of Pietro da Cortona and reports that he died in 1689.",
                   "The death date is supported in Haskell's note by Baldinucci, VI (1728), p.411; neither the cited page nor the claim has been independently checked.",
                   ["cand-1066","cand-0342","cand-4846"], extras={"date":"1689","relation_candidate":True,"ocr_corrections":[{"source_line":243,"ocr":"1689?","print":"1689.¹","basis":"CHP-8.pdf physical page 33"}]}),
    make_statement("st-chp8-p231-la-burla-purchase-and-making", P231,243,244,"cand-1609","cand-7860",
                   "bought_la_burla_before_1693_after_franceschini_painted_it_for_private_citizen",
                   "Some time before 1693 Ferdinand bought La Burla del Pievano Arlotto, which Franceschini had painted in tempera many years earlier for a private citizen.",
                   "The buyer and date are Haskell's report; the earlier private citizen is unnamed and the cited art-historical sources were not independently read.",
                   ["cand-1609","cand-7860","cand-1066","cand-4167"], extras={"date_before":"1693","relation_candidate":True}),
    make_statement("st-chp8-p231-la-burla-style-and-subject", P231,245,245,"cand-7860",None,
                   "style_and_subject_owe_more_to_tuscan_narrative_than_naturalism",
                   "Haskell says the painting's homely, archaic simplicity owes more in style and subject inspiration to fifteenth-century Tuscan narrative than to contemporary naturalism elsewhere in Italy.",
                   "This is Haskell's stylistic judgment; the cited sources do not independently verify the comparison here.",
                   ["cand-7860","cand-6232","cand-3461","cand-5739"], extras={"speaker_judgment":True,"ocr_corrections":[{"source_line":245,"ocr":"than.to","print":"than to","basis":"CHP-8.pdf physical page 33"}]}),
    make_statement("st-chp8-p231-encouraged-crespi", P231,246,246,"cand-1609","cand-0871",
                   "encouraged_comparable_intimacy_in_crespi_works",
                   "Haskell says Ferdinand soon had an opportunity to encourage a comparable intimacy in Giuseppe Maria Crespi's works.",
                   "The passage does not identify the work or establish that any specific commission was completed.",
                   ["cand-1609","cand-0871"], extras={"relation_candidate":True}),
    make_statement("st-chp8-p231-s-marco-purchase-and-copy", P231,247,247,"cand-1609","cand-7856",
                   "bought_s_marco_from_church_and_had_copy_replace_it_in_1692",
                   "Haskell says Ferdinand bought Fra Bartolommeo's S. Marco from a church dedicated to Saint Mark and had it replaced with a copy in 1692.",
                   "The church is unnamed; note 3 locates the copy at the Pitti as no.125 and names Antonio Franchi as its painter. The painting and copy are separate objects.",
                   ["cand-1609","cand-0253","cand-7856","cand-7857","cand-7858","cand-7859"], extras={"date":"1692","relation_candidate":True,"ocr_corrections":[{"source_line":247,"ocr":"1692.3","print":"1692.³","basis":"CHP-8.pdf physical page 33"}]}),
    make_statement("st-chp8-p231-church-dedicated-to-mark", P231,247,247,"cand-7858","cand-7859",
                   "church_dedicated_to_saint_mark",
                   "The church from which Fra Bartolommeo's S. Marco was bought is described as dedicated to Saint Mark.",
                   "The source does not name or otherwise identify the church.",
                   ["cand-7858","cand-7859"], extras={"relation_candidate":True}),
    make_statement("st-chp8-p231-1690s-church-purchases", P231,247,248,"cand-1609",None,
                   "bought_named_pictures_from_florentine_and_other_churches_in_1690s",
                   "Haskell says Ferdinand bought pictures from various churches in Florence and elsewhere during the 1690s, including works by Raphael, Andrea del Sarto, Cigoli and Orazio Riminaldi.",
                   "The text does not give acquisition dates for each painting or identify all source churches; p.231 note 4 acknowledges discrepancies among accounts.",
                   ["cand-1609","cand-3397","cand-2102","cand-7861","cand-3427","cand-2362","cand-7862","cand-0757","cand-7863","cand-2201","cand-7864","cand-7876"], extras={"date_range":"1690s","relation_candidate":True}),
    make_statement("st-chp8-p231-interest-in-gabbiani", P231,248,248,"cand-1609","cand-1093",
                   "chiefly_interested_in_gabbiani_and_remained_loyal_to_him",
                   "Haskell says Ferdinand showed particular interest in Anton Domenico Gabbiani and remained loyal to him long after Ferdinand's horizons widened.",
                   "Haskell characterizes Gabbiani as faithful, within the limits of his talents, to classical and Marattesque canons; this is an evaluative description, not evidence of formal institutional membership.",
                   ["cand-1609","cand-1093","cand-7873"], extras={"speaker_judgment":True,"relation_candidate":True,"ocr_corrections":[{"source_line":248,"ocr":"chiefly hi","print":"chiefly in","basis":"CHP-8.pdf physical page 33"},{"source_line":248,"ocr":"CeciliaA","print":"Cecilia.⁴","basis":"CHP-8.pdf physical page 33"},{"source_line":248,"ocr":"art5","print":"art⁵","basis":"CHP-8.pdf physical page 33"}]}),
    make_statement("st-chp8-p231-cardinal-leopold-collection", P231,249,249,"cand-1629","cand-7865",
                   "amassed_large_renaissance_collection_and_influenced_medici_court",
                   "Haskell says a taste for Venetian art had appeared at the Medici court through Cardinal Leopold's activities; Leopold had amassed a very large collection of Renaissance works, which Ferdinand set out to amplify.",
                   "The collection is not a separately typed entity under the current taxonomy. The source does not inventory its works in this passage.",
                   ["cand-1629","cand-7865","cand-5520","cand-1609","cand-3401","cand-3578","cand-7875"], extras={"relation_candidate":True,"ocr_corrections":[{"source_line":249,"ocr":"ofTitian","print":"of Titian","basis":"CHP-8.pdf physical page 33"}]}),
    make_statement("st-chp8-p231-artists-recur-in-ferdinand-letters-open", P231,249,249,"cand-1609",None,
                   "sixteenth_century_venetian_artists_recurred_in_ferdinand_letters",
                   "Haskell says the names of Titian, Veronese, Bassano, Palma Giovane and other Venetian sixteenth-century painters recur in letters Ferdinand wrote over the next few years.",
                   "The sentence continues at p.232 L252; recipient and specific letters are not added until that source segment is processed.",
                   ["cand-1609","cand-2630","cand-2755","cand-0257","cand-1811","cand-7874","cand-3401","cand-7875"], extras={"continuation_status":"open","continuation_expected_segment_id":P232,"continuation_expected_source_line":252,"relation_candidate":True,"ocr_corrections":[{"source_line":249,"ocr":"Renaissance.6","print":"Renaissance.⁶","basis":"CHP-8.pdf physical page 33"}]}),
    make_statement("st-chp8-p231-note1-baldinucci", NOTES,409,409,None,None,
                   "footnote_cites_baldinucci_for_franceschini_biographical_detail",
                   "Footnote 1 cites Baldinucci, volume VI, 1728, p.411, following the report of Franceschini's 1689 death.",
                   "The cited page was not independently consulted.",
                   ["cand-4846","cand-1066"], text_layer="footnote citation", extras={"relation_candidate":False,"linked_body_statement_ids":["st-chp8-p231-franceschini-biography"]}),
    make_statement("st-chp8-p231-note2-la-burla-location-history", NOTES,410,410,"cand-7860","cand-1949",
                   "footnote_reports_la_burla_at_pitti_no_582_and_cites_history_sources",
                   "Footnote 2 says La Burla is now at the Pitti as no.582 and cites Giglioli (1908) and Steinhart (1936) for its history.",
                   "The cited publication identities are not fully verified and the works were not independently consulted; the bibliography's Giglioli 1908 entry may not unambiguously match this citation.",
                   ["cand-7860","cand-1949","cand-7866","cand-7867"], text_layer="footnote citation", extras={"relation_candidate":False,"linked_body_statement_ids":["st-chp8-p231-la-burla-purchase-and-making"],"ocr_corrections":[{"source_line":410,"ocr":"Pitri","print":"Pitti","basis":"CHP-8.pdf physical page 33"},{"source_line":410,"ocr":"Steinhart","print":"Steinbart","basis":"CHP-8.pdf physical page 33 and bibliography"}]}),
    make_statement("st-chp8-p231-note3-copy-location-and-franchi", NOTES,411,411,"cand-7857","cand-1949",
                   "footnote_locates_copy_at_pitti_no_125_and_names_franchi",
                   "Footnote 3 says the copy is now at the Pitti as no.125, identifies Antonio Franchi as its painter, and cites Bartolozzi.",
                   "The cited book and the present identity of the copy were not independently checked.",
                   ["cand-7857","cand-1949","cand-1074","cand-7868"], text_layer="footnote citation", extras={"relation_candidate":False,"linked_body_statement_ids":["st-chp8-p231-s-marco-purchase-and-copy"],"ocr_corrections":[{"source_line":411,"ocr":"Pitri","print":"Pitti","basis":"CHP-8.pdf physical page 33"}]}),
    make_statement("st-chp8-p231-note4-church-picture-records", NOTES,412,412,None,None,
                   "footnote_qualifies_accounts_of_pictures_from_churches",
                   "Footnote 4 says there is some confusion about the paintings from Florentine and other churches, citing Bencivenni and Jahn-Rusconi, while judging the general outline clear despite slight discrepancies.",
                   "The discrepancies are Haskell's qualification; the cited works were not independently compared here.",
                   ["cand-3397","cand-7869","cand-7870","cand-1609"], text_layer="footnote citation", extras={"relation_candidate":False,"linked_body_statement_ids":["st-chp8-p231-1690s-church-purchases"]}),
    make_statement("st-chp8-p231-note5-gabbiani-sources", NOTES,413,413,"cand-1093",None,
                   "footnote_cites_hugford_and_bartarelli_on_gabbiani",
                   "Footnote 5 directs the reader especially to Hugford and Bartarelli for Gabbiani.",
                   "The cited book and article were identified from the bibliography but not independently consulted.",
                   ["cand-1093","cand-7871","cand-7872"], text_layer="footnote citation", extras={"relation_candidate":False,"linked_body_statement_ids":["st-chp8-p231-interest-in-gabbiani"]}),
    make_statement("st-chp8-p231-note6-leopold-source", NOTES,414,414,"cand-1629","cand-7869",
                   "footnote_cites_bencivenni_for_cardinal_leopolds_collecting",
                   "Footnote 6 cites Bencivenni, volume I, pp.248–261, and volume II, pp.181–187, for general information on Cardinal Leopold's collecting.",
                   "The cited pages and work were not independently consulted.",
                   ["cand-1629","cand-7869"], text_layer="footnote citation", extras={"relation_candidate":False,"linked_body_statement_ids":["st-chp8-p231-cardinal-leopold-collection"]}),
]

statement_ids = {row["statement_id"] for row in statement_rows}
if len(statement_ids) != len(statement_rows) or any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("duplicate statement ID")
prior_id = "st-chp8-p230-venice-memory-observation-open"
prior = next((row for row in statement_rows if row["statement_id"] == prior_id), None)
if not prior or prior["qualifiers"].get("continuation_status") != "open":
    raise SystemExit("expected open p.230 Venice statement not found")
patched_prior = json.loads(json.dumps(prior))
patched_prior["qualifiers"].update({"continuation_status":"closed","continuation_to_segment_id":P231,
                                   "continuation_to_source_line":239,"continued_to_segment_id":P231,
                                   "continued_to_source_line":239,"continuation_closed_by_statement_id":"st-chp8-p231-venetian-pictures-recalled"})

for row in coverage_rows:
    if row["segment_id"] == P230:
        row.update({"disposition":"reviewed","migration_status":"complete","source_line_ranges":"L227-236",
                    "note":"p.230 final Venice-observation clause closed by p.231 L239; body and embedded notes are migrated."})
    elif row["segment_id"] == P231:
        row.update({"disposition":"reviewed","migration_status":"partial","source_line_ranges":"L238-249",
                    "note":"p.231 body and notes 1–6 at L409–414 reviewed against CHP-8.pdf physical page 33; final sentence continues at p.232 L252."})
    elif row["segment_id"] == NOTES:
        row.update({"disposition":"reviewed","migration_status":"partial","source_line_ranges":"L373-414",
                    "note":"p.228–231 post-text notes through p.231 n.6 migrated; later consolidated notes remain queued."})

preview = {"mode":"dry-run","candidate_additions":len(new_candidates),"mention_additions":len(new_mentions),
           "statement_additions":len(new_statements),"closed_continuation":{"statement_id":prior_id,"segment_id":P231,"line":239},
           "open_continuation":{"statement_id":"st-chp8-p231-artists-recur-in-ferdinand-letters-open","segment_id":P232,"line":252},
           "coverage":{P230:"complete",P231:"partial",NOTES:"L373-414 partial"},
           "ocr_corrections":["L243 1689? -> 1689.¹","L245 than.to -> than to","L247 note marker 3 normalized","L248 chiefly hi -> chiefly in, CeciliaA -> Cecilia.⁴, art5 -> art⁵","L249 ofTitian -> of Titian and note marker 6 normalized","L410-411 Pitri -> Pitti; L410 Steinhart -> Steinbart"]}

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
