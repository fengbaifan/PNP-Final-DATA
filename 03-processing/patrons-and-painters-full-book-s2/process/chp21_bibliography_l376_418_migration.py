#!/usr/bin/env python3
"""Controlled S2 migration for bibliography entries on printed p. 420."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "21_CHP-21Bibliography.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-21Bibliography.pdf"
SEGMENT = "chp-21:21_CHP-21Bibliography:l376-418"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
SEGMENT_SHA = "5e44cafeed9ff68b1686c9dbe1f2edc6de160ac1a8611133d48d0092e10e175b"
BACKUP = ".bak-s2-chp21-bibliography-l376-418-20261007"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write changes; default is dry-run")
ARGS = parser.parse_args()


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
        temporary = Path(handle.name)
    temporary.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(handle.name)
    temporary.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("bibliography Markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("bibliography PDF changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[375:418])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 segment text/hash changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage = read_csv(coverage_path)
statements = read_jsonl(statement_path)
if (len(candidates), len(mentions), len(statements), len(coverage)) != (11275, 26183, 11458, 832):
    raise SystemExit("unexpected bibliography S2 pre-state")

candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}
if SEGMENT not in coverage_by_id or (
    coverage_by_id[SEGMENT]["disposition"], coverage_by_id[SEGMENT]["migration_status"]
) != ("queued", "pending"):
    raise SystemExit("bibliography segment is not queued")

# The source line boundaries and all OCR corrections were checked against PDF physical page 10.
entries = [
    {"candidate_id":"cand-7836","start":377,"end":377,"author":"Conti, Giuseppe","title":"Firenze dai Medici ai Lorena","details":"Florence, 1909","kind":"book"},
    {"candidate_id":"cand-11297","new_name":"Flaminio Corner, Notizie storiche delle chiese e monasteri di Venezia e di Torcello (Padua, 1758)","new_detail":"The bibliography identifies Flaminio Corner’s publication; its contents were not independently consulted.","start":378,"end":378,"author":"Corner, Flaminio","title":"Notizie storiche delle chiese e monasteri di Venezia e di Torcello tratte dalle chiese veneziane, e torcellane illustrate da F. C.","details":"Padua, 1758","kind":"book","corrections":[{"line":378,"ocr":"delle‘chiese","print":"delle chiese"}]},
    {"candidate_id":"cand-11298","new_name":"G. Corti, Galleria Colonna (Rome, 1937)","new_detail":"The bibliography identifies this publication; its contents were not independently consulted.","start":379,"end":379,"author":"Corti, G.","title":"Galleria Colonna","details":"Rome, 1937","kind":"book"},
    {"candidate_id":"cand-7087","start":380,"end":380,"author":"Cosnac, Comte Gabriel-Jules de","title":"Les richesses du Palais Mazarin","details":"Paris, 1885","kind":"book"},
    {"candidate_id":"cand-11299","new_name":"Don Anselmo Costadoni, Memorie della vita di Flaminio Cornaro (Venice, 1780)","new_detail":"The bibliography identifies the book and edition; its contents were not independently consulted.","start":381,"end":381,"author":"Costadoni, Don Anselmo","title":"Memorie della vita di Flaminio Cornaro","details":"Venice, 1780","kind":"book"},
    {"candidate_id":"cand-7017","start":382,"end":383,"author":"Costello, Jane","title":"The twelve pictures ‘ordered by Velasquez’ and the trial of Valguarnera","details":"Journal of the Warburg and Courtauld Institutes, 1950, pp. 237–284","kind":"journal article"},
    {"candidate_id":"cand-11300","new_name":"Abbé Coyer, Voyages d’Italie et de Hollande (2 vols., Paris, 1775)","new_detail":"The bibliography identifies a two-volume publication; its contents were not independently consulted.","start":384,"end":384,"author":"Coyer, Abbé","title":"Voyages d’Italie et de Hollande","details":"2 vols., Paris, 1775","kind":"book set","corrections":[{"line":384,"ocr":"isolated trailing dash after ‘Paris 1775.’","print":"no dash belongs to the bibliographic entry"}]},
    {"candidate_id":"cand-11301","new_name":"Gaetano Cozzi, ‘Intorno al Cardinale Ottaviano Paravicino, a Monsignor Paolo Gualdo e a Michelangelo da Caravaggio’ (Rivista Storica Italiana, 1961)","new_detail":"The bibliography identifies the article; its contents were not independently consulted.","start":385,"end":386,"author":"Cozzi, Gaetano","title":"Intorno al Cardinale Ottaviano Paravicino, a Monsignor Paolo Gualdo e a Michelangelo da Caravaggio","details":"Rivista Storica Italiana, 1961, pp. 36–68","kind":"journal article"},
    {"candidate_id":"cand-5594","start":387,"end":387,"author":"Crescimbeni, G. M.","title":"Dell’Istoria della Volgar Poesia","details":"Venice, 1730","kind":"book"},
    {"candidate_id":"cand-8022","start":388,"end":388,"author":"","entry_heading":"Crespi","title":"Mostra celebrativa di Giuseppe M. Crespi","details":"Bologna, 1948","kind":"exhibition catalogue; authorship not stated"},
    {"candidate_id":"cand-6591","start":389,"end":389,"author":"Crespi, Luigi","title":"Vite de’ Pittori bolognesi non descritte nella ‘Felsina Pittrice’","details":"Rome, 1769","kind":"book"},
    {"candidate_id":"cand-7060","start":390,"end":391,"author":"Crinò, Anna Maria","title":"Due lettere autografe inedite di Orazio e di Artemisia Gentileschi","details":"Rivista d’Arte, 1954, pp. 203–206","kind":"journal article"},
    {"candidate_id":"cand-5602","start":392,"end":392,"author":"Croce, Benedetto","title":"Lirici marinisti","details":"Bari, 1910","kind":"book"},
    {"candidate_id":"cand-7265","start":393,"end":394,"author":"Croce, Benedetto","title":"Shaftesbury in Italia","details":"Reprinted in Uomini e cose della vecchia Italia, Bari, 1927, pp. 272–309","kind":"reprinted essay"},
    {"candidate_id":"cand-11302","new_name":"E. Croft-Murray, Decorative Painting in England 1537–1837, vol. I (London, 1962)","new_detail":"The bibliography identifies volume I of the two-volume work; volume contents were not independently consulted.","start":395,"end":396,"author":"Croft-Murray, E.","title":"Decorative Painting in England 1537–1837: Volume I—Early Tudor to Sir James Thornhill","details":"Volume I, London, 1962","kind":"book volume"},
    {"candidate_id":"cand-11070","start":397,"end":397,"author":"Croft-Murray, E.","title":"Decorative Painting in England 1537–1837: Volume 2—The 18th and early 19th centuries","details":"Volume 2, London, 1970","kind":"book volume"},
    {"candidate_id":"cand-7019","start":399,"end":400,"author":"Crozet, René","title":"La vie artistique en France au XVII siècle, 1598–1661: les artistes et la société","details":"Paris, 1954","kind":"book"},
    {"candidate_id":"cand-11303","new_name":"G. Cugnoni, ‘Agostino Chigi il Magnifico’ (Archivio della Società Romana di Storia Patria, 1879–1881)","new_detail":"The bibliography identifies a journal article with installments listed for 1879–1881; the cited article was not independently consulted.","start":401,"end":402,"author":"Cugnoni, G.","title":"Agostino Chigi il Magnifico","details":"Archivio della Società Romana di Storia Patria, 1879, pp. 37–83, 209–226; 1880, pp. 213–232, 291–305, 422–448; 1881, pp. 56–75, 195–216","kind":"journal article"},
    {"candidate_id":"cand-11304","new_name":"L. Cust, ‘Notes on pictures in the Royal Collections’ (Burlington Magazine, vol. XXIII, 1913)","new_detail":"The bibliography identifies the article and year; the article was not independently consulted.","start":403,"end":404,"author":"Cust, L.","title":"Notes on pictures in the Royal Collections","details":"Burlington Magazine, vol. XXIII, 1913, pp. 150–162 and 267–275","kind":"journal article","corrections":[{"line":404,"ocr":"191z","print":"1913"}]},
    {"candidate_id":"cand-11305","new_name":"Gino Damerini, Morosini (Milan, 1929)","new_detail":"The bibliography identifies the book and edition; its contents were not independently consulted.","start":405,"end":405,"author":"Damerini, Gino","title":"Morosini","details":"Milan, 1929","kind":"book"},
    {"candidate_id":"cand-11306","new_name":"Gino Damerini, Caterina Dolfin Tron (Milan, 1929)","new_detail":"The bibliography identifies the book and edition; its contents were not independently consulted.","start":406,"end":406,"author":"Damerini, Gino","title":"Caterina Dolfin Tron","details":"Milan, 1929","kind":"book"},
    {"candidate_id":"cand-11307","new_name":"Girolamo Dandolo, La caduta della Repubblica di Venezia ed i suoi ultimi cinquant’anni (Venice, 1855)","new_detail":"The bibliography identifies the book and edition; its contents were not independently consulted.","start":407,"end":408,"author":"Dandolo, Girolamo","title":"La caduta della Repubblica di Venezia ed i suoi ultimi cinquant’anni","details":"Venice, 1855","kind":"book","corrections":[{"line":407,"ocr":"cinquantanni","print":"cinquant’anni"}]},
    {"candidate_id":"cand-11075","start":409,"end":409,"author":"Daniels, Jeffery","title":"Sebastiano Ricci","details":"Hove, 1976","kind":"book"},
    {"candidate_id":"cand-11308","new_name":"Domenico Darmanno, ‘Inediti documenti sulle vicende di Alvise Zenobio’ (Archivio Veneto, 1872)","new_detail":"The bibliography identifies the article; its contents were not independently consulted.","start":410,"end":411,"author":"Darmanno, Domenico","title":"Inediti documenti sulle vicende di Alvise Zenobio","details":"Archivio Veneto, vol. III, 1872, pp. 278–300","kind":"journal article"},
    {"candidate_id":"cand-11309","new_name":"Carlo Dati, Delle lodi di Cassiano dal Pozzo (Florence, 1664)","new_detail":"The bibliography identifies the book and edition; its contents were not independently consulted.","start":412,"end":412,"author":"Dati, Carlo","title":"Delle lodi di Cassiano dal Pozzo","details":"Florence, 1664","kind":"book","corrections":[{"line":412,"ocr":"isolated trailing dash after ‘Firenze 1664.’","print":"no dash belongs to the bibliographic entry"}]},
    {"candidate_id":"cand-11310","new_name":"James C. Davis, The decline of the Venetian Nobility as a ruling class (Baltimore, 1962)","new_detail":"The bibliography identifies the book and edition; its contents were not independently consulted.","start":413,"end":413,"author":"Davis, James C.","title":"The decline of the Venetian Nobility as a ruling class","details":"Baltimore, 1962","kind":"book"},
    {"candidate_id":"cand-11311","new_name":"Manlio Dazzi, Carlo Goldoni e la sua poetica sociale (Turin, 1957)","new_detail":"The bibliography identifies the book and edition; its contents were not independently consulted.","start":414,"end":414,"author":"Dazzi, Manlio","title":"Carlo Goldoni e la sua poetica sociale","details":"Turin, 1957","kind":"book"},
    {"candidate_id":"cand-11312","new_name":"Giuseppe Delogu, G. B. Castiglione detto Il Grechetto (Bologna, 1928)","new_detail":"The bibliography identifies the book and edition; its contents were not independently consulted.","start":415,"end":415,"author":"Delogu, Giuseppe","title":"G. B. Castiglione detto Il Grechetto","details":"Bologna, 1928","kind":"book","corrections":[{"line":415,"ocr":"II Grechetto","print":"Il Grechetto"}]},
    {"candidate_id":"cand-11313","new_name":"J. Delumeau, La vie économique et sociale de Rome dans la seconde moitié du 16ème siècle (Paris, 1957)","new_detail":"The bibliography identifies the book and edition; its contents were not independently consulted.","start":416,"end":417,"author":"Delumeau, J.","title":"La vie économique et sociale de Rome dans la seconde moitié du 16ème siècle","details":"Paris, 1957","kind":"book","corrections":[{"line":416,"ocr":"l6ème siècle","print":"16ème siècle"}]},
    {"candidate_id":"cand-11314","new_name":"Louis Demonts, ‘Essai sur la formation de Simon Vouet en Italie’ (Bulletin de la Société de l’Histoire de l’Art Français, 1913)","new_detail":"The bibliography identifies the article; its contents were not independently consulted.","start":418,"end":418,"author":"Demonts, Louis","title":"Essai sur la formation de Simon Vouet en Italie","details":"Bulletin de la Société de l’Histoire de l’Art Français, 1913, pp. 309–348","kind":"journal article"},
]

if len(entries) != 30 or len({row["candidate_id"] for row in entries}) != 30:
    raise SystemExit("bibliography publication specification is incomplete or duplicated")

covered_lines = {line for entry in entries for line in range(entry["start"], entry["end"] + 1)}
covered_lines.add(398)  # Printed cross-reference, not a publication record.
if covered_lines != set(range(377, 419)):
    raise SystemExit("bibliography entry line coverage is incomplete or overlaps the page marker")

natural_keys = {
    (row["canonical_name"].strip().casefold(), row["suggested_type"].strip().casefold())
    for row in candidates
}
new_candidates = []
for entry in entries:
    if not entry.get("new_name"):
        continue
    candidate_id = entry["candidate_id"]
    if candidate_id in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    key = (entry["new_name"].strip().casefold(), "archive")
    if key in natural_keys:
        raise SystemExit(f"candidate natural-key collision: {candidate_id} {entry['new_name']}")
    row = {field: "" for field in candidate_fields}
    row.update(candidate_id=candidate_id, canonical_name=entry["new_name"], suggested_type="archive", status="open",
               detail=entry["new_detail"], candidate_origin="body-mention",
               candidate_source_ref=f"{SEGMENT}#L{entry['start']}")
    new_candidates.append(row)
    candidate_by_id[candidate_id] = row
    natural_keys.add(key)

candidate_detail_updates = {
    "cand-7836": "Printed bibliography p. 420 lists Firenze dai Medici ai Lorena (Florence, 1909); the publication was not independently consulted in this S2 pass.",
    "cand-7087": "Printed bibliography p. 420 gives the full Cosnac entry Les richesses du Palais Mazarin (Paris, 1885); the book was not independently consulted in this S2 pass.",
    "cand-7017": "Printed bibliography p. 420 identifies Jane Costello’s article in Journal of the Warburg and Courtauld Institutes (1950), pp. 237–284; the article was not independently consulted in this S2 pass.",
    "cand-5594": "Printed bibliography p. 420 lists Dell’Istoria della Volgar Poesia (Venice, 1730); the work was not independently consulted in this S2 pass.",
    "cand-8022": "Printed bibliography p. 420 lists the exhibition catalogue Mostra celebrativa di Giuseppe M. Crespi (Bologna, 1948); the catalogue entry does not state an author and the catalogue was not independently consulted.",
    "cand-6591": "Printed bibliography p. 420 identifies Luigi Crespi’s Vite de’ Pittori bolognesi non descritte nella ‘Felsina Pittrice’ (Rome, 1769); the book was not independently consulted in this S2 pass.",
    "cand-7060": "Printed bibliography p. 420 identifies the Crinò article in Rivista d’Arte (1954), pp. 203–206; the article was not independently consulted in this S2 pass.",
    "cand-5602": "Printed bibliography p. 420 lists Lirici marinisti (Bari, 1910); the book was not independently consulted in this S2 pass.",
    "cand-7265": "Printed bibliography p. 420 identifies the 1927 reprint and pages 272–309 in Uomini e cose della vecchia Italia; the cited essay was not independently consulted in this S2 pass.",
    "cand-11070": "Printed bibliography p. 420 identifies volume 2 as Decorative Painting in England 1537–1837: The 18th and early 19th centuries (London, 1970); the volume was not independently consulted.",
    "cand-7019": "Printed bibliography p. 420 confirms the title, Paris 1954 publication details, and 1598–1661 range; the book was not independently consulted in this S2 pass.",
    "cand-11075": "Printed bibliography p. 420 identifies the monograph Sebastiano Ricci (Hove, 1976); the book was not independently consulted in this S2 pass.",
}
for candidate_id, detail in candidate_detail_updates.items():
    candidate = candidate_by_id.get(candidate_id)
    if not candidate or candidate.get("suggested_type") != "archive":
        raise SystemExit(f"missing/wrong-type bibliography candidate: {candidate_id}")
    if detail in candidate.get("detail", ""):
        raise SystemExit(f"candidate detail already updated: {candidate_id}")

mention_keys = {
    (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"]))
    for row in mentions
}
new_mentions = []
new_statements = []
existing_claim_keys = {
    (row.get("segment_id", ""), " ".join(str((row.get("qualifiers") or {}).get("claim", "")).split()).casefold())
    for row in statements if isinstance(row.get("qualifiers"), dict)
}


def source_quote(entry):
    return "\n".join(source_lines[entry["start"] - 1:entry["end"]])


def add_mention(candidate_id, surface, note, scope=None):
    if scope is None:
        position = segment_text.find(surface)
        ambiguous = position >= 0 and segment_text.find(surface, position + 1) >= 0
    else:
        scope_position = segment_text.find(scope)
        if scope_position < 0 or segment_text.find(scope, scope_position + 1) >= 0:
            raise SystemExit(f"mention scope absent or ambiguous: {scope!r}")
        relative_position = scope.find(surface)
        ambiguous = relative_position >= 0 and scope.find(surface, relative_position + 1) >= 0
        position = scope_position + relative_position if relative_position >= 0 else -1
    if position < 0 or ambiguous:
        raise SystemExit(f"mention span text absent or ambiguous for {candidate_id}: {surface!r}")
    end = position + len(surface)
    key = (SEGMENT, candidate_id, str(position), str(end))
    if key in mention_keys:
        raise SystemExit(f"duplicate mention natural key: {candidate_id} {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update(mention_id=f"m-chp21-bib-l376-418-{len(new_mentions)+1:03d}", segment_id=SEGMENT,
               candidate_id=candidate_id, surface_form=surface, start_char=position, end_char=end, note=note)
    new_mentions.append(row)
    mention_keys.add(key)


def add_statement(statement_id, subject_id, object_id, predicate, quote, line_start, line_end, claim, qualifiers):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    claim_key = (SEGMENT, " ".join(claim.split()).casefold())
    if claim_key in existing_claim_keys:
        raise SystemExit(f"duplicate statement claim: {claim}")
    existing_claim_keys.add(claim_key)
    row = {
        "statement_id": statement_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": subject_id,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": line_start,
            "source_line_end": line_end,
            "claim": claim,
            "speaker": "Haskell’s bibliography",
            "relation_candidate": False,
            "mentioned_candidate_ids": [value for value in (subject_id, object_id) if value],
            **qualifiers,
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
    }
    if not quote or quote not in "\n".join(source_lines[line_start - 1:line_end]):
        raise SystemExit(f"statement quote/line validation failed: {statement_id}")
    new_statements.append(row)
    statement_by_id[statement_id] = row


for index, entry in enumerate(entries, start=1):
    candidate_id = entry["candidate_id"]
    candidate = candidate_by_id.get(candidate_id)
    if not candidate or candidate.get("suggested_type") != "archive":
        raise SystemExit(f"missing/wrong-type publication candidate: {candidate_id}")
    quote = source_quote(entry)
    add_mention(candidate_id, quote,
                "S0 bibliography entry; page-image corrections are recorded in statement qualifiers.")
    record = {
        "author_as_printed": entry["author"],
        "title_as_printed": entry["title"],
        "publication_details_as_printed": entry["details"],
        "record_kind": entry["kind"],
        "printed_page": 420,
    }
    if entry.get("entry_heading"):
        record["entry_heading_as_printed"] = entry["entry_heading"]
    qualifiers = {
        "text_layer": "bibliographic entry",
        "qualification": "This records the book bibliography entry only; the cited publication was not independently consulted in this S2 pass.",
        "bibliographic_record": record,
    }
    if entry.get("corrections"):
        qualifiers["page_image_ocr_corrections"] = entry["corrections"]
    add_statement(
        f"st-chp21-bib-l376-418-entry-{index:02d}", None, candidate_id, "bibliography_lists_publication",
        quote, entry["start"], entry["end"], f"Haskell lists {entry['title']} in the book bibliography.", qualifiers,
    )

crossref_quote = source_lines[397]
crossref_subject = "cand-11001"  # The Croft-Murray candidate remains unresolved for S3.
crossref_object = "cand-9340"    # Existing local bibliography entry at L210.
target_statement_id = "st-chp21-bib-l207-241-entry-02"
target_statement = statement_by_id.get(target_statement_id)
if not target_statement or target_statement.get("object_candidate_id") != crossref_object:
    raise SystemExit("the printed cross-reference target does not resolve to the expected local bibliography record")
add_mention(crossref_subject, "Croft-Murray, E.", "Source heading in a printed bibliography ‘See also’ cross-reference; identity remains for S3.", scope=crossref_quote)
add_mention(crossref_object, "Blunt and Croft-Murray", "Target author heading in a printed bibliography cross-reference to the L210 joint publication.", scope=crossref_quote)
add_statement(
    "st-chp21-bib-l376-418-crossref-01", crossref_subject, crossref_object, "bibliography_cross_reference",
    crossref_quote, 398, 398,
    "Haskell’s bibliography redirects the heading ‘Croft-Murray, E.’ to ‘Blunt and Croft-Murray’.",
    {
        "text_layer": "bibliographic cross-reference",
        "qualification": "Records the printed ‘See also’ direction to the local L210 joint publication only; it does not assert an author relation or resolve Croft-Murray candidate identity.",
        "cross_reference_type": "see_also",
        "target_segment_id": "chp-21:21_CHP-21Bibliography:l207-241",
        "target_statement_id": target_statement_id,
        "identity_resolution_deferred_to": "S3",
    },
)

if len(new_candidates) != 18 or len(new_mentions) != 32 or len(new_statements) != 31:
    raise SystemExit("unexpected migration row counts")
for statement in new_statements:
    for endpoint in (statement["subject_candidate_id"], statement["object_candidate_id"]):
        if endpoint and endpoint not in candidate_by_id:
            raise SystemExit(f"statement candidate FK missing: {statement['statement_id']}")
for row in new_mentions:
    if segment_text[row["start_char"]:row["end_char"]] != row["surface_form"]:
        raise SystemExit(f"mention offset validation failed: {row['mention_id']}")
ordered_mentions = sorted(new_mentions, key=lambda row: (int(row["start_char"]), int(row["end_char"])))
for left, right in zip(ordered_mentions, ordered_mentions[1:]):
    if int(left["end_char"]) > int(right["start_char"]):
        raise SystemExit(f"overlapping mention spans: {left['mention_id']} and {right['mention_id']}")

coverage_by_id[SEGMENT]["disposition"] = "reviewed"
coverage_by_id[SEGMENT]["migration_status"] = "complete"
coverage_by_id[SEGMENT]["source_line_ranges"] = "L376-418"
coverage_by_id[SEGMENT]["note"] = "Printed p.420 contains 30 publication records and one ‘See also’ bibliographic pointer; L376 is a page marker. Reused 12 archive candidates, added 18, and recorded the cross-reference to the previously recorded L210 joint publication. PDF physical page 10 corrections are in statement qualifiers; source OCR remains unchanged. Cited works were not independently consulted."
all_candidates = candidates + sorted(new_candidates, key=lambda row: int(row["candidate_id"].split("-")[1]))
all_mentions = mentions + new_mentions
all_statements = statements + new_statements
all_coverage = [coverage_by_id[row["segment_id"]] for row in coverage]

print(json.dumps({
    "mode": "apply" if ARGS.apply else "dry-run",
    "segment": SEGMENT,
    "printed_page": 420,
    "publication_records": len(entries),
    "reused_archive_candidates": len(entries) - len(new_candidates),
    "new_archive_candidates": [row["candidate_id"] for row in new_candidates],
    "cross_reference": {"subject": crossref_subject, "target": crossref_object, "target_statement_id": target_statement_id},
    "mentions_added": len(new_mentions),
    "statements_added": len(new_statements),
    "coverage_after": {"disposition": coverage_by_id[SEGMENT]["disposition"], "migration_status": coverage_by_id[SEGMENT]["migration_status"]},
    "table_counts_after": {"candidates": len(all_candidates), "mentions": len(all_mentions), "statements": len(all_statements), "coverage": len(all_coverage)},
}, ensure_ascii=False, indent=2))

if ARGS.apply:
    for path in (candidate_path, mention_path, statement_path, coverage_path):
        backup = path.with_name(path.name + BACKUP)
        if backup.exists():
            if hashlib.sha256(backup.read_bytes()).hexdigest() != hashlib.sha256(path.read_bytes()).hexdigest():
                raise SystemExit(f"existing recovery copy differs from pre-state: {backup.name}")
        else:
            shutil.copy2(path, backup)
    for candidate_id, detail in candidate_detail_updates.items():
        old = candidate_by_id[candidate_id].get("detail", "").rstrip()
        candidate_by_id[candidate_id]["detail"] = f"{old} {detail}".strip()
    write_csv(candidate_path, candidate_fields, all_candidates)
    write_csv(mention_path, mention_fields, all_mentions)
    write_jsonl(statement_path, all_statements)
    write_csv(coverage_path, coverage_fields, all_coverage)
