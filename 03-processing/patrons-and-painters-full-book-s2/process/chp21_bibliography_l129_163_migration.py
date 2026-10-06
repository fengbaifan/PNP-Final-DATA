#!/usr/bin/env python3
"""Controlled S2 migration for bibliography entries on printed p. 414."""
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
SEGMENT = "chp-21:21_CHP-21Bibliography:l129-163"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
SEGMENT_SHA = "1f55cc7604b48d357dfcd4b68419d3e76ae1872c5a6cd7a0355dd65732f593bb"
BACKUP = ".bak-s2-chp21-bibliography-l129-163-20261004"

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
        temp = Path(handle.name)
    temp.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp = Path(handle.name)
    temp.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("bibliography Markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("bibliography PDF changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[128:163])
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
if (len(candidates), len(mentions), len(statements), len(coverage)) != (11220, 26012, 11288, 832):
    raise SystemExit("unexpected bibliography S2 pre-state")

candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}
if SEGMENT not in coverage_by_id or (coverage_by_id[SEGMENT]["disposition"], coverage_by_id[SEGMENT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("bibliography segment is not queued")

new_candidate_specs = [
    ("cand-11242", "A. Bandi di Vesme, ‘L’Arte negli Stati Sabaudi’ (Atti della Società Piemontese di Archeologia e Belle Arti, 1932)", 130, "The bibliography gives the article title, venue, and year; volume, pages, and cited contents were not independently consulted."),
    ("cand-11243", "A. Bazzoni, Un nunzio straordinario alla corte di Francia nel secolo XVII (Florence, 1882)", 133, "The bibliography identifies this Florence 1882 publication. Keep separate from the earlier Bazzoni citation candidate cand-4573 until S3 can establish whether it is the same work."),
    ("cand-11244", "G. Beani, Clemente IX—Giulio Rospigliosi Pistoiese (Prato, 1893)", 134, "The bibliography identifies this Prato 1893 publication. Keep separate from the earlier Beani and Canevazzi citation candidate cand-4862 until S3 resolves the relation."),
    ("cand-11245", "Cardinal François-Joachim de Pierre de Bernis, Mémoires et lettres 1715–1758 (2 vols., Paris, 1878)", 153, "The bibliography identifies the two-volume 1878 publication edited by Frédéric Masson. Earlier volume-I citation locators cand-8802 and cand-10536 remain separate for S3 identity review."),
    ("cand-11246", "J. J. Berthier, L’église de Sainte Sabine à Rome (Rome, 1910)", 155, "The bibliography identifies the Rome 1910 publication; its contents were not independently consulted."),
    ("cand-11247", "A. Bertolotti, Artisti subalpini in Roma nei secoli XV, XVI e XVII (Mantua, 1884)", 158, "The bibliography identifies the Mantua 1884 publication; its contents were not independently consulted."),
    ("cand-11248", "A. Bertolotti, ‘Le ultime volontà di Michelangelo delle Battaglie’ (Arte e Storia, 1886, p. 22)", 160, "The bibliography identifies a journal article. Keep distinct from the journal-volume candidate cand-6183; the cited article was not independently consulted."),
]

entries = [
    {"candidate_id":"cand-11242","start":130,"end":130,"author":"Bandi di Vesme, A.","title":"L’Arte negli Stati Sabaudi","details":"Atti della Società Piemontese di Archeologia e Belle Arti, 1932; volume and pages not stated","kind":"journal article"},
    {"candidate_id":"cand-7039","start":131,"end":131,"author":"Baudson, E.","title":"Apollon et les Neuf Muses du Palais du Luxembourg","details":"Bulletin de la Société de l’Histoire de l’Art Français, 1941–1944, pp. 28–33","kind":"journal article"},
    {"candidate_id":"cand-5494","start":132,"end":132,"author":"Baumgarten, S.","title":"Pierre Legros artiste romain","details":"Paris, 1923","kind":"book"},
    {"candidate_id":"cand-11243","start":133,"end":133,"author":"Bazzoni, A.","title":"Un nunzio straordinario alla corte di Francia nel secolo XVII","details":"Florence, 1882","kind":"book","related":["cand-4573"]},
    {"candidate_id":"cand-11244","start":134,"end":134,"author":"Beani, G.","title":"Clemente IX—Giulio Rospigliosi Pistoiese","details":"Prato, 1893","kind":"book","related":["cand-4862"]},
    {"candidate_id":"cand-9439","start":135,"end":135,"author":"[Beckford, William]","title":"Italy, with sketches of Spain and Portugal","details":"2 vols., London, 1834","kind":"book","corrections":[{"line":135,"ocr":"thè author os Vathek","print":"the author of Vathek"}],"print_only_text":"2 vols., London 1834."},
    {"candidate_id":"cand-4832","start":136,"end":137,"author":"Bellori, G. P.","title":"Le Vite de’ Pittori, Scultori et Architetti moderni","details":"Facsimile of the Rome 1672 edition; Rome, 1931","kind":"facsimile edition"},
    {"candidate_id":"cand-4831","start":138,"end":138,"author":"Bellori, G. P.","title":"Le Vite inedite (Guido Reni, Andrea Sacchi, Carlo Maratta)","details":"Edited by M. Piacentini; Rome, 1942","kind":"edited book"},
    {"candidate_id":"cand-4377","start":139,"end":139,"author":"Bellori, G. P.","title":"Le Vite de’ Pittori, Scultori e Architetti Moderni","details":"Edited by Evelina Borea; introduction by Giovanni Previtali; Turin, 1976","kind":"edited book"},
    {"candidate_id":"cand-9462","start":140,"end":140,"author":None,"title":"Mostra di Bernardo Bellotto—opere provenienti dalla Polonia","details":"Venice, 1955","kind":"exhibition catalogue"},
    {"candidate_id":"cand-8541","start":141,"end":142,"author":"Beltrami, D.","title":"Storia della popolazione di Venezia dalla fine del secolo XVI alla caduta della Repubblica","details":"Padua, 1954","kind":"book"},
    {"candidate_id":"cand-7869","start":143,"end":143,"author":"[Bencivenni, già Pelli]","title":"Saggio istorico della Real Galleria di Firenze","details":"2 vols., Florence, 1779","kind":"book"},
    {"candidate_id":"cand-7081","start":144,"end":144,"author":"Benedetti, Elpidio","title":"Pompa funebre nell’esequie celebrate in Roma al Cardinal Mazarini nella Chiesa di S.S. Vincenzo Anastasio","details":"Rome, 1661","kind":"book"},
    {"candidate_id":"cand-4843","start":145,"end":145,"author":"Bentivoglio, Cardinal","title":"Memorie","details":"Milan, 1807","kind":"book"},
    {"candidate_id":"cand-4858","start":146,"end":148,"author":"Bentivoglio, Cardinal Guido","title":"Relazione della famosa festa fatta in Roma alli xxv di Febbraio mdcxxxiv sotto gli auspici dell’Eminentissimo Sig. Cardinale Antonio Barberini","details":"Included in Raccolta di lettere scritte dal Cardinal Bentivoglio (Rome, 1654); reprinted by Ludovico Passarmi in 1882","kind":"reprinted text"},
    {"candidate_id":"cand-8292","start":149,"end":149,"author":"Berengo, Marino","title":"La società Veneta alla fine del ’700","details":"Florence, 1955","kind":"book"},
    {"candidate_id":"cand-10134","start":150,"end":151,"author":"Berengo, Marino","title":"La crisi dell’Arte della Stampa Veneziana alla fine del XVIII secolo","details":"In Studi in onore di Armando Sapori, 2 vols., Milan, 1957, pp. 1321–1338","kind":"essay in collected volume","related":["cand-10136"]},
    {"candidate_id":"cand-7130","start":152,"end":152,"author":"Bernino, Domenico","title":"Vita del Cavalier Gio. Lorenzo Bernino","details":"Rome, 1713","kind":"book"},
    {"candidate_id":"cand-11245","start":153,"end":154,"author":"De Bernis, Cardinal François-Joachim de Pierre","title":"Mémoires et lettres 1715–1758","details":"Published by Frédéric Masson; 2 vols., Paris, 1878","kind":"edited book","related":["cand-8802","cand-10536"]},
    {"candidate_id":"cand-11246","start":155,"end":155,"author":"Berthier, J. J.","title":"L’église de Sainte Sabine à Rome","details":"Rome, 1910","kind":"book"},
    {"candidate_id":"cand-4574","start":156,"end":156,"author":"Bertolotti, A.","title":"Giornalisti, Astrologi e Negromanti in Roma nel secolo XVII","details":"Florence, 1878","kind":"book"},
    {"candidate_id":"cand-6182","start":157,"end":157,"author":"Bertolotti, A.","title":"Artisti belgi ed olandesi a Roma nei secoli XVI e XVII","details":"Florence, 1880","kind":"book"},
    {"candidate_id":"cand-11247","start":158,"end":158,"author":"Bertolotti, A.","title":"Artisti subalpini in Roma nei secoli XV, XVI e XVII","details":"Mantua, 1884","kind":"book"},
    {"candidate_id":"cand-5501","start":159,"end":159,"author":"Bertolotti, A.","title":"Un professore alla Sapienza di Roma nel secolo XVII","details":"Rome, 1886","kind":"book"},
    {"candidate_id":"cand-11248","start":160,"end":160,"author":"Bertolotti, A.","title":"Le ultime volontà di Michelangelo delle Battaglie","details":"Arte e Storia, 1886, p. 22","kind":"journal article","container_candidate_id":"cand-6183"},
    {"candidate_id":"cand-3505","start":161,"end":161,"author":"Bertolotti, A.","title":"Artisti bolognesi, ferraresi ed alcuni altri del già stato pontificio in Roma nei secoli XV, XVI, XVII","details":"Publication date not stated","kind":"book"},
    {"candidate_id":"cand-7050","start":162,"end":163,"author":"Betcherman, L. R.","title":"Balthazar Gerbier in seventeenth century Italy","details":"History Today, 1961, pp. 325–331","kind":"journal article","corrections":[{"line":163,"ocr":"PP-325-33I-","print":"pp. 325–331"}]},
]
if len(entries) != 27 or len({entry["candidate_id"] for entry in entries}) != 27:
    raise SystemExit("bibliography entry specification is incomplete or duplicated")

natural_keys = {
    (row["canonical_name"].strip().casefold(), row["suggested_type"].strip().casefold())
    for row in candidates
}
new_candidates = []
for candidate_id, name, line_number, detail in new_candidate_specs:
    if candidate_id in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    key = (name.casefold(), "archive")
    if key in natural_keys:
        raise SystemExit(f"candidate natural-key collision: {candidate_id} {name}")
    row = {field: "" for field in candidate_fields}
    row.update(
        candidate_id=candidate_id,
        canonical_name=name,
        suggested_type="archive",
        status="open",
        detail=detail,
        candidate_origin="body-mention",
        candidate_source_ref=f"{SEGMENT}#L{line_number}",
    )
    new_candidates.append(row)
    candidate_by_id[candidate_id] = row
    natural_keys.add(key)

for entry in entries:
    candidate = candidate_by_id.get(entry["candidate_id"])
    if not candidate or candidate.get("suggested_type") != "archive":
        raise SystemExit(f"missing/wrong-type publication candidate: {entry['candidate_id']}")

candidate_detail_updates = {
    "cand-9439": "Bibliography line 135 identifies the work as Italy, with sketches of Spain and Portugal, 2 vols., London 1834. The print page supplies the continuation and corrects two OCR errors; cited contents were not independently consulted.",
    "cand-4805": "Bibliography p.414 image supplies the full title Nota delli Musei, Librerie, Gallerie e Ornamenti di statue e pitture ne’ palazzi, nelle case e ne’ giardini di Roma, appended to Lunadoro’s Relatione della corte di Roma (Rome and Venice, 1664). The entry is absent from S0 OCR; exact edition identity remains for S3 review.",
    "cand-4832": "Bibliography line 136–137 identifies the 1931 Rome facsimile of Bellori’s Le Vite de’ Pittori, Scultori et Architetti moderni, based on the 1672 Rome edition; contents were not independently consulted.",
    "cand-4377": "Bibliography line 139 identifies the 1976 Turin edition of Le Vite de’ Pittori, Scultori e Architetti Moderni, edited by Evelina Borea with an introduction by Giovanni Previtali; contents were not independently consulted.",
    "cand-8541": "Bibliography lines 141–142 identify the 1954 Beltrami publication as Storia della popolazione di Venezia dalla fine del secolo XVI alla caduta della Repubblica (Padua); contents were not independently consulted.",
    "cand-4843": "Bibliography line 145 identifies Bentivoglio’s 1807 publication as Memorie (Milan); contents were not independently consulted.",
    "cand-4858": "Bibliography lines 146–148 identify the text as Relazione della famosa festa fatta in Roma alli xxv di Febbraio mdcxxxiv, included in the 1654 Raccolta di lettere scritte dal Cardinal Bentivoglio and reprinted by Ludovico Passarmi in 1882. Preserve the source spelling and edition distinctions; contents were not independently consulted.",
    "cand-10134": "Bibliography lines 150–151 identify the 1957 Berengo article as La crisi dell’Arte della Stampa Veneziana alla fine del XVIII secolo, in Studi in onore di Armando Sapori, pp. 1321–1338. Candidate cand-10136 is a separate short citation that may refer to this article; identity consolidation is deferred to S3.",
    "cand-7130": "Bibliography line 152 identifies the publication as Domenico Bernino, Vita del Cavalier Gio. Lorenzo Bernino (Rome, 1713); contents were not independently consulted.",
    "cand-4574": "Bibliography line 156 identifies Bertolotti’s 1878 publication as Giornalisti, Astrologi e Negromanti in Roma nel secolo XVII (Florence); contents were not independently consulted.",
    "cand-6182": "Bibliography line 157 identifies the full title as Artisti belgi ed olandesi a Roma nei secoli XVI e XVII (Florence, 1880); contents were not independently consulted.",
    "cand-5501": "Bibliography line 159 identifies Bertolotti’s 1886 publication as Un professore alla Sapienza di Roma nel secolo XVII (Rome); contents were not independently consulted.",
    "cand-6183": "This candidate is the journal-volume container Arte e Storia, volume V (1886), distinct from Bertolotti’s article ‘Le ultime volontà di Michelangelo delle Battaglie’ (p. 22), which is registered separately as cand-11248.",
    "cand-3505": "Bibliography line 161 supplies the full title: Artisti bolognesi, ferraresi ed alcuni altri del già stato pontificio in Roma nei secoli XV, XVI, XVII; no publication date is stated. The cited contents were not independently consulted.",
    "cand-7050": "Bibliography lines 162–163 identify the article as ‘Balthazar Gerbier in seventeenth century Italy’ (History Today, 1961, pp. 325–331); the page image corrects the OCR locator. Article not independently consulted.",
}
for candidate_id, detail in candidate_detail_updates.items():
    candidate = candidate_by_id.get(candidate_id)
    if not candidate or candidate.get("suggested_type") != "archive":
        raise SystemExit(f"missing/wrong-type short-citation candidate: {candidate_id}")
    if detail in candidate.get("detail", ""):
        raise SystemExit(f"candidate detail already updated: {candidate_id}")

mentions = list(mentions)
mention_keys = {
    (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"]))
    for row in mentions
}
new_mentions = []


def source_quote(entry):
    return entry.get("quote") or "\n".join(source_lines[entry["start"] - 1:entry["end"]])


def add_mention(entry):
    surface = source_quote(entry)
    position = segment_text.find(surface)
    if position < 0 or segment_text.find(surface, position + 1) >= 0:
        raise SystemExit(f"mention span text absent or ambiguous for {entry['candidate_id']}: {surface!r}")
    end = position + len(surface)
    key = (SEGMENT, entry["candidate_id"], str(position), str(end))
    if key in mention_keys:
        raise SystemExit(f"duplicate mention natural key: {entry['candidate_id']} L{entry['start']}-{entry['end']}")
    row = {field: "" for field in mention_fields}
    row.update(
        mention_id=f"m-chp21-bib-l129-163-{len(new_mentions)+1:03d}",
        segment_id=SEGMENT,
        candidate_id=entry["candidate_id"],
        surface_form=surface,
        start_char=position,
        end_char=end,
        note="Complete S0 bibliography entry. OCR omissions and corrections visible in the physical page are recorded in statement qualifiers.",
    )
    new_mentions.append(row)
    mention_keys.add(key)


for entry in entries:
    add_mention(entry)

new_statements = []
existing_claim_keys = {
    (row.get("segment_id", ""), " ".join(str((row.get("qualifiers") or {}).get("claim", "")).split()).casefold())
    for row in statements
    if isinstance(row.get("qualifiers"), dict)
}


def add_statement(statement_id, candidate_id, quote, line_start, line_end, claim, predicate="bibliography_lists_publication", record=None, extra_qualifiers=None):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    qualifier = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "claim": claim,
        "speaker": "Haskell’s bibliography",
        "text_layer": "bibliographic entry",
        "qualification": "This statement records the bibliography entry; the cited publication was not independently consulted in this S2 pass.",
        "relation_candidate": False,
        "mentioned_candidate_ids": [candidate_id],
    }
    if record:
        qualifier["bibliographic_record"] = record
    if extra_qualifiers:
        qualifier.update(extra_qualifiers)
    claim_key = (SEGMENT, " ".join(claim.split()).casefold())
    if claim_key in existing_claim_keys:
        raise SystemExit(f"duplicate statement claim: {claim}")
    existing_claim_keys.add(claim_key)
    statement = {
        "statement_id": statement_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": None,
        "object_candidate_id": candidate_id,
        "predicate": predicate,
        "qualifiers": qualifier,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
    }
    new_statements.append(statement)
    statement_by_id[statement_id] = statement


for index, entry in enumerate(entries, start=1):
    raw = source_quote(entry)
    extras = {}
    if entry.get("corrections"):
        extras["page_image_ocr_corrections"] = entry["corrections"]
    if entry.get("print_only_text"):
        extras["page_image_text_missing_from_s0"] = {
            "text": entry["print_only_text"],
            "location": "CHP-21Bibliography.pdf physical page 4, continuation of the Beckford entry",
            "handling": "preserved as a page-image addendum; S0 source text is not rewritten",
        }
    if entry.get("related"):
        extras["related_candidate_ids_for_s3"] = entry["related"]
    if entry.get("container_candidate_id"):
        extras["container_candidate_id"] = entry["container_candidate_id"]
    add_statement(
        f"st-chp21-bib-l129-163-entry-{index:02d}",
        entry["candidate_id"],
        raw,
        entry["start"],
        entry["end"],
        f"Haskell lists {entry['title']} in the book bibliography.",
        record={
            "author_as_printed": entry["author"],
            "title_as_printed": entry["title"],
            "publication_details_as_printed": entry["details"],
            "record_kind": entry["kind"],
            "printed_page": 414,
        },
        extra_qualifiers=extras,
    )

page_image_entry = "Bellori, G. P.: Nota delli Musei, Librerie, Gallerie e Ornamenti di statue e pitture ne’ palazzi, nelle case e ne’ giardini di Roma—appendice a Lunadoro: Relatione della corte di Roma, Roma e Venezia 1664."
page_image_anchor = "\n".join(source_lines[134:137])
add_statement(
    "st-chp21-bib-l129-163-page-image-omission-01",
    "cand-4805",
    page_image_anchor,
    135,
    137,
    "The printed bibliography page includes a Bellori Nota delli Musei entry omitted from the S0 OCR transcription.",
    predicate="bibliography_page_image_addendum",
    record={
        "author_as_printed": "Bellori, G. P.",
        "title_as_printed": "Nota delli Musei, Librerie, Gallerie e Ornamenti di statue e pitture ne’ palazzi, nelle case e ne’ giardini di Roma",
        "publication_details_as_printed": "Appendix to Lunadoro, Relatione della corte di Roma; Rome and Venice, 1664",
        "record_kind": "page-image-only bibliography entry omitted from S0",
        "printed_page": 414,
        "page_image_transcription": page_image_entry,
    },
    extra_qualifiers={
        "page_image_source": "02-sources/01-book/CHP-21Bibliography.pdf, physical page 4",
        "anchor_explanation": "original_quote reproduces the adjacent S0 OCR lines bracketing this omitted printed entry; it is not the transcription of the missing entry. The complete print transcription is page_image_transcription.",
        "s0_text_unchanged": True,
    },
)

if len(new_mentions) != 27 or len(new_statements) != 28 or len(new_candidates) != 7:
    raise SystemExit("unexpected migration row counts")
for statement in new_statements:
    if statement["object_candidate_id"] not in candidate_by_id:
        raise SystemExit(f"statement candidate FK missing: {statement['statement_id']}")
    if statement["original_quote"] not in "\n".join(source_lines[statement["qualifiers"]["source_line_start"] - 1:statement["qualifiers"]["source_line_end"]]):
        raise SystemExit(f"statement quote/line validation failed: {statement['statement_id']}")
for row in new_mentions:
    if segment_text[row["start_char"]:row["end_char"]] != row["surface_form"]:
        raise SystemExit(f"mention offset validation failed: {row['mention_id']}")

coverage_by_id[SEGMENT]["disposition"] = "reviewed"
coverage_by_id[SEGMENT]["migration_status"] = "complete"
coverage_by_id[SEGMENT]["source_line_ranges"] = "L129-163"
coverage_by_id[SEGMENT]["note"] = "Printed p.414 contains 27 S0-visible bibliography entries; the page image supplies the Beckford continuation and a separate Bellori 1664 entry omitted from S0, and confirms OCR corrections. Bibliography entries record cited works, not that their contents were read."
all_candidates = candidates + sorted(new_candidates, key=lambda row: int(row["candidate_id"].split("-")[1]))
all_mentions = mentions + new_mentions
all_statements = statements + new_statements
all_coverage = [coverage_by_id[row["segment_id"]] for row in coverage]

print(json.dumps({
    "mode": "apply" if ARGS.apply else "dry-run",
    "segment": SEGMENT,
    "new_publication_candidates": [row["candidate_id"] for row in new_candidates],
    "reused_candidates_for_27_s0_entries": 27 - len(new_candidates),
    "page_image_only_bellori_candidate": "cand-4805",
    "mentions_added": len(new_mentions),
    "statements_added": len(new_statements),
    "candidate_detail_updates": sorted(candidate_detail_updates),
    "page_image_omissions": ["Beckford continuation: 2 vols., London 1834.", page_image_entry],
    "coverage": {"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L129-163"},
}, ensure_ascii=False, indent=2))

if ARGS.apply:
    for path in (candidate_path, mention_path, statement_path, coverage_path):
        backup = path.with_name(path.name + BACKUP)
        if backup.exists():
            raise SystemExit(f"recovery copy already exists: {backup.name}")
        shutil.copy2(path, backup)
    for candidate_id, detail in candidate_detail_updates.items():
        old = candidate_by_id[candidate_id].get("detail", "").rstrip()
        candidate_by_id[candidate_id]["detail"] = f"{old} {detail}".strip()
    write_csv(candidate_path, candidate_fields, all_candidates)
    write_csv(mention_path, mention_fields, all_mentions)
    write_jsonl(statement_path, all_statements)
    write_csv(coverage_path, coverage_fields, all_coverage)
