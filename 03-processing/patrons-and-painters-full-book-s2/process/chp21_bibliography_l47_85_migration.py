#!/usr/bin/env python3
"""Controlled S2 migration for bibliography entries on printed p. 412."""
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
SEGMENT = "chp-21:21_CHP-21Bibliography:l47-85"
HEADER = "chp-21:21_CHP-21Bibliography:l1-1"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
SEGMENT_SHA = "396dc079d1c3a85664b946bc191af6ef9f45d7421d9bb18e7c9aa03b966fc370"
BACKUP = ".bak-s2-chp21-bibliography-l47-85-20261004"

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
segment_text = "\n".join(source_lines[46:85])
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
if (len(candidates), len(mentions), len(statements), len(coverage)) != (11203, 25953, 11230, 832):
    raise SystemExit("unexpected bibliography S2 pre-state")

candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}
if SEGMENT not in coverage_by_id or (coverage_by_id[SEGMENT]["disposition"], coverage_by_id[SEGMENT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("bibliography segment is not queued")
if HEADER not in coverage_by_id or (coverage_by_id[HEADER]["disposition"], coverage_by_id[HEADER]["migration_status"]) != ("excluded", "complete"):
    raise SystemExit("generated bibliography heading was not excluded")

# Exact publication candidates already used for corresponding short citations
# are reused. New records are created only where the book does not provide an
# existing publication candidate or where the edition/date remains distinct.
new_candidate_specs = [
    ("cand-11225", "Giuseppe Agnello, ‘Un caravaggesco: Mario Minniti’ (Archivi, 1941)", "archive", 55,
     "Bibliography entry gives the article title, periodical, year, and pages; cited contents were not independently consulted."),
    ("cand-11226", "Amelot de la Houssaye, Histoire du gouvernement de Venise (Paris, 1677)", "archive", 65,
     "Bibliography entry identifies a 1677 Paris publication; no edition or text was independently checked."),
    ("cand-11227", "A. J. Dézallier d’Argenville, Abrégé de la vie des plus fameux peintres (Paris, 1762)", "archive", 68,
     "Bibliography entry identifies a four-volume Paris publication; cited contents were not independently consulted."),
    ("cand-11228", "Vincenzo Armanni, Delle lettere del Signor V. A. nobile d’ugubbio (Rome, 1663 and 1674)", "archive", 69,
     "The bibliography lists a three-volume work with publication years 1663 and 1674; volume-level assignment is not supplied."),
    ("cand-11229", "Orazio Arrighi-Landini, Il-Tempio della Filosofia (Venice, 1755)", "archive", 74,
     "Bibliography entry lists the Venice 1755 edition. Keep separate from p.301 note 6 candidate cand-9514 (cited as 1757) until edition identity is resolved."),
    ("cand-11230", "W. Arslan, ‘Quattro lettere di Pietro Visconti a Gian Pietro Ligari’ (1952)", "archive", 78,
     "Bibliography entry identifies the article and fascicle; the article was not independently consulted."),
    ("cand-11231", "Duc d’Aumale, Inventaire de tous les meubles du Cardinal Mazarin (London, 1861)", "archive", 82,
     "Bibliography entry identifies an 1861 publication of the 1653 inventory; the inventory itself was not consulted."),
    ("cand-11232", "Giovanni Baglione, Le Vite de’ Pittori Scultori et Architetti (Rome, 1935 facsimile)", "archive", 83,
     "Bibliography describes a 1935 facsimile of the 1642 Rome edition; keep the facsimile edition distinct from the original printing."),
]

entries = [
    {"candidate_id":"cand-4563", "start":49,"end":50,"author":"Ackerman, G.","title":"Gian Battista Marino’s contribution to Seicento Art Theory","details":"Art Bulletin, 1961, pp. 326–336","kind":"journal article","corrections":[{"line":50,"ocr":"3 26-3 3 6","print":"326–336"}]},
    {"candidate_id":"cand-7837", "start":51,"end":51,"author":"Acton, Harold","title":"The last Medici","details":"London, 1958","kind":"book"},
    {"candidate_id":"cand-4860", "start":52,"end":52,"author":"Ademollo, A.","title":"I teatri di Roma nel secolo decimosettimo","details":"Rome, 1888","kind":"book"},
    {"candidate_id":"cand-9335", "start":53,"end":53,"author":"Adhémar, Hélène","title":"Watteau—sa vie—son œuvre","details":"Paris, 1950","kind":"book"},
    {"candidate_id":"cand-7261", "start":54,"end":54,"author":"Agnelli, J.","title":"Galleria di pitture del Card. Tomm. Ruffo vescovo di Ferrara","details":"Ferrara, 1734","kind":"book"},
    {"candidate_id":"cand-11225", "start":55,"end":55,"author":"Agnello, Giuseppe","title":"Un caravaggesco: Mario Minniti","details":"Archivi, 1941, pp. 60–80","kind":"journal article"},
    {"candidate_id":"cand-11200", "start":56,"end":57,"author":"Aikema, Bernard","title":"Patronage in late baroque Venice: the Zenobio","details":"Overdruk uit de Mededelingen van het Nederlands Instituut te Rome, Deel XLI—Nova Series 6, 1979, pp. 209–218","kind":"journal article","corrections":[{"line":56,"ocr":"Mede­ / . delingen","print":"Mededelingen (line-break hyphenation)"},{"line":57,"ocr":"Institut","print":"Instituut"}]},
    {"candidate_id":"cand-7099", "start":58,"end":59,"author":"Alazard, Jean","title":"L’Abbé Luigi Strozzi correspondant artistique de Mazarin, de Colbert, de Louvois et de La Teulière","details":"Paris, 1924","kind":"book"},
    {"candidate_id":"cand-7055", "start":60,"end":60,"author":"Albion, G. H. J.","title":"Charles I and the Court of Rome","details":"Louvain, 1935","kind":"book"},
    {"candidate_id":"cand-10158", "start":61,"end":61,"author":"[Albrizzi, G. B.]","title":"Memorie intorno alla Vita di G. B. Piazzetta","details":"Venice, 1760","kind":"book","qualification":"The author name is bracketed; the bibliography’s scope note says brackets indicate anonymous publications. The bracketed form is not independent proof of authorship."},
    {"candidate_id":"cand-10229", "start":62,"end":62,"author":"Algarotti, Francesco","title":"Opere","details":"17 vols., Venice, 1791–4","kind":"collected works"},
    {"candidate_id":"cand-11126", "start":63,"end":63,"author":"Algarotti, Francesco","title":"Saggi","details":"Edited by Giovanni da Pozzo, Bari, 1963","kind":"edited book"},
    {"candidate_id":"cand-9801", "start":64,"end":64,"author":"Ambri, Paola Berselli","title":"L’opera di Montesquieu nel settecento italiano","details":"Florence, 1960","kind":"book","corrections":[{"line":64,"ocr":"i960","print":"1960"}]},
    {"candidate_id":"cand-11226", "start":65,"end":65,"author":"Amelot de la Houssaye, A. N.","title":"Histoire du gouvernement de Venise","details":"Paris, 1677","kind":"book"},
    {"candidate_id":"cand-11202", "start":67,"end":67,"author":"D’Arcais, Francesca","title":"L’attività viennese di Antonio Bellucci","details":"Arte Veneta, 1964, pp. 99–109","kind":"journal article","corrections":[{"line":67,"ocr":"L’attiviti","print":"L’attività"},{"line":67,"ocr":"Beliucci","print":"Bellucci"}]},
    {"candidate_id":"cand-11227", "start":68,"end":68,"author":"D’Argenville, A. J. Dézallier","title":"Abrégé de la vie des plus fameux peintres","details":"4 vols., Paris, 1762","kind":"book"},
    {"candidate_id":"cand-11228", "start":69,"end":70,"author":"Armanni, Vincenzo","title":"Delle lettere del Signor V. A. nobile d’ugubbio","details":"3 vols., Rome, 1663 and 1674","kind":"collected letters"},
    {"candidate_id":"cand-5139", "start":71,"end":71,"author":"Armellini, M.","title":"Le chiese di Roma","details":"Rome, 1942","kind":"book"},
    {"candidate_id":"cand-8504", "start":72,"end":73,"author":"Arnaldi, Lodovico","title":"Orazione in lode di Marco Foscarini Doge di Venezia","details":"In G. A. Molin, Orazioni, elogj e vite scritte da letterati patrizj, Venice, 1795","kind":"essay in collected volume"},
    {"candidate_id":"cand-11229", "start":74,"end":74,"author":"Arrighi-Landini, Orazio","title":"Il-Tempio della Filosofia","details":"Venice, 1755","kind":"book","qualification":"The bibliography lists 1755; p.301 note 6 cites 1757. This record is kept separate from cand-9514 pending edition reconciliation."},
    {"candidate_id":"cand-8796", "start":75,"end":75,"author":"Arslan, W.","title":"G. B. Tiepolo e G. M. Morlaiter ai Gesuati","details":"Rivista di Venezia, 1932, pp. 19–25","kind":"journal article","corrections":[{"line":75,"ocr":"Arsian","print":"Arslan"}]},
    {"candidate_id":"cand-9361", "start":76,"end":76,"author":"Arslan, W.","title":"Alcuni dipinti per il MacSwiney","details":"Rivista d’Arte, 1932, pp. 128–140","kind":"journal article","corrections":[{"line":76,"ocr":"Arsian","print":"Arslan"}]},
    {"candidate_id":"cand-9362", "start":77,"end":77,"author":"Arslan, W.","title":"Altri due quadri per il MacSwiney","details":"Rivista d’Arte, 1933, pp. 244–248","kind":"journal article"},
    {"candidate_id":"cand-11230", "start":78,"end":78,"author":"Arslan, W.","title":"Quattro lettere di Pietro Visconti a Gian Pietro Ligari","details":"Rivista Archeologica dell’antica provincia di Como, fasc. 133, 1952, pp. 63–72","kind":"journal article","corrections":[{"line":78,"ocr":"fase. 13 3","print":"fasc. 133"}]},
    {"candidate_id":"cand-9370", "start":79,"end":79,"author":"Arslan, W.","title":"Altri due dipinti per il McSwiny","details":"Commentari, 1955, pp. 189–192","kind":"journal article"},
    {"candidate_id":"cand-11150", "start":80,"end":81,"author":None,"title":"Art and its images—an exhibition of printed books containing engraved illustrations after Italian paintings","details":"Oxford (Bodleian Library), 1975","kind":"exhibition catalogue"},
    {"candidate_id":"cand-11231", "start":82,"end":82,"author":"d’Aumale, duc","title":"Inventaire de tous les meubles du Cardinal Mazarin dressé en 1653 d’après l’original, conservé dans les archives de Condé","details":"London, 1861","kind":"inventory publication","corrections":[{"line":82,"ocr":"tneubles","print":"meubles"}]},
    {"candidate_id":"cand-11232", "start":83,"end":84,"author":"Baglione, Gio.","title":"Le Vite de’ Pittori Scultori et Architetti dal pontificato di Gregorio XIII del 1572 in fino a’ tempi di Papa Urbano Ottavo nel 1642","details":"Facsimile of the 1642 Rome edition, Rome, 1935","kind":"facsimile edition"},
    {"candidate_id":"cand-7110", "start":85,"end":85,"author":"Bailly, N.","title":"Inventaire des tableaux du Roy rédigé en 1709 et 1710","details":"Paris, 1899","kind":"inventory publication","corrections":[{"line":85,"ocr":"Ni","print":"N."}]},
]
if len(entries) != 29 or len({entry["candidate_id"] for entry in entries}) != 29:
    raise SystemExit("bibliography entry specification is incomplete or duplicated")

natural_keys = {
    (row["canonical_name"].strip().casefold(), row["suggested_type"].strip().casefold())
    for row in candidates
}
new_candidates = []
for candidate_id, name, kind, line_number, detail in new_candidate_specs:
    if candidate_id in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    key = (name.casefold(), kind.casefold())
    if key in natural_keys:
        raise SystemExit(f"candidate natural-key collision: {candidate_id} {name}")
    row = {field: "" for field in candidate_fields}
    row.update(
        candidate_id=candidate_id,
        canonical_name=name,
        suggested_type=kind,
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

crossref_candidate_ids = ["cand-1292", "cand-11167"]
for candidate_id in crossref_candidate_ids:
    if candidate_id not in candidate_by_id:
        raise SystemExit(f"missing cross-reference candidate: {candidate_id}")
if "cand-11166" not in candidate_by_id or "cand-11165" not in candidate_by_id:
    raise SystemExit("missing postscript short-author/citation candidates for cross-reference audit")

mentions = list(mentions)
mention_keys = {
    (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"]))
    for row in mentions
}
line_offsets = {}
offset = 0
for line_number in range(47, 86):
    line_offsets[line_number] = offset
    offset += len(source_lines[line_number - 1]) + 1

new_mentions = []

def add_mention(start_line, end_line, surface, candidate_id, note=""):
    expected = "\n".join(source_lines[start_line - 1:end_line])
    if surface == expected:
        local_offset = 0
    elif start_line == end_line:
        found = source_lines[start_line - 1].find(surface)
        if found < 0 or source_lines[start_line - 1].find(surface, found + 1) >= 0:
            raise SystemExit(f"mention span text is absent or ambiguous at L{start_line}: {surface!r}")
        local_offset = found
    else:
        raise SystemExit(f"mention span text mismatch at L{start_line}-{end_line}: {surface!r} != {expected!r}")
    start = line_offsets[start_line] + local_offset
    end = start + len(surface)
    key = (SEGMENT, candidate_id, str(start), str(end))
    if key in mention_keys:
        raise SystemExit(f"duplicate mention natural key: {candidate_id} L{start_line}-{end_line}")
    row = {field: "" for field in mention_fields}
    row.update(
        mention_id=f"m-chp21-bib-l47-85-{len(new_mentions)+1:03d}",
        segment_id=SEGMENT,
        candidate_id=candidate_id,
        surface_form=surface,
        start_char=start,
        end_char=end,
        note=note,
    )
    new_mentions.append(row)
    mention_keys.add(key)

for entry in entries:
    raw = "\n".join(source_lines[entry["start"] - 1:entry["end"]])
    add_mention(entry["start"], entry["end"], raw, entry["candidate_id"], "Complete bibliography entry; page-image readings and OCR differences are recorded on its linked statement.")

# Line 66 is an author cross-reference, not a separate publication. Keep the
# index heading spelling and the target author forms as individual mentions.
add_mention(66, 66, "Andres, Gregorio de", "cand-11167", "Cross-reference heading form; S0 omits the accent found in the print image.")
add_mention(66, 66, "Harris, Enriqueta", "cand-1292", "Named author in the cross-reference target; same-identity mapping to short-form candidates is deferred to S3.")
add_mention(66, 66, "Andrés, Gregorio de", "cand-11167", "Named author in the cross-reference target; external/global identity alignment is deferred to S3.")

new_statements = []
for index, entry in enumerate(entries, start=1):
    raw = "\n".join(source_lines[entry["start"] - 1:entry["end"]])
    qualifier = {
        "source_line_start": entry["start"],
        "source_line_end": entry["end"],
        "claim": f"Haskell lists {entry['title']} in the book bibliography.",
        "speaker": "Haskell’s bibliography",
        "text_layer": "bibliographic entry",
        "qualification": entry.get("qualification", "This statement records the book’s bibliographic entry; it does not mean the cited publication was independently consulted in this S2 pass."),
        "relation_candidate": False,
        "mentioned_candidate_ids": [entry["candidate_id"]],
        "bibliographic_record": {
            "author_as_printed": entry["author"],
            "title_as_printed": entry["title"],
            "publication_details_as_printed": entry["details"],
            "record_kind": entry["kind"],
            "printed_page": 412,
        },
    }
    if entry.get("corrections"):
        qualifier["page_image_ocr_corrections"] = entry["corrections"]
    if entry["candidate_id"] == "cand-11200":
        qualifier["bibliography_resolves_short_citation_candidate"] = "p.405 note 4 cites Aikema; the source’s unique Aikema entry concerns the Zenobio. The publication text itself remains unread."
    if entry["candidate_id"] == "cand-11202":
        qualifier["bibliography_resolves_short_citation_candidate"] = "p.406 note 5 cites D’Arcais for a Bellucci-in-Vienna article; this entry uniquely matches that subject in the bibliography. The publication text itself remains unread."
    if entry["candidate_id"] == "cand-11229":
        qualifier["edition_conflict"] = {"bibliography": "1755", "p301_note6_candidate": "cand-9514, 1757", "decision": "keep separate pending S3/edition reconciliation"}
    new_statements.append({
        "statement_id": f"st-chp21-bib-l47-85-entry-{index:02d}",
        "segment_id": SEGMENT,
        "subject_candidate_id": None,
        "object_candidate_id": entry["candidate_id"],
        "predicate": "bibliography_lists_publication",
        "qualifiers": qualifier,
        "original_quote": raw,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
    })

heading_quote = source_lines[47]
new_statements.append({
    "statement_id": "st-chp21-bib-l47-85-published-materials-heading",
    "segment_id": SEGMENT,
    "subject_candidate_id": None,
    "object_candidate_id": None,
    "predicate": "bibliography_section_heading",
    "qualifiers": {
        "source_line_start": 48,
        "source_line_end": 48,
        "claim": "The bibliography labels this section ‘Published Materials.’",
        "speaker": "Haskell’s bibliography",
        "text_layer": "section heading",
        "qualification": "The print image reads ‘PUBLISHED MATERIALS’; S0 OCR mangles the ornamental subsection marker.",
        "page_image_reading": "—b— PUBLISHED MATERIALS",
        "page_number_line": 47,
        "relation_candidate": False,
        "mentioned_candidate_ids": [],
    },
    "original_quote": heading_quote,
    "origin": "book",
    "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
})

crossref_quote = source_lines[65]
new_statements.append({
    "statement_id": "st-chp21-bib-l47-85-andres-harris-cross-reference",
    "segment_id": SEGMENT,
    "subject_candidate_id": "cand-11167",
    "object_candidate_id": "cand-1292",
    "predicate": "bibliography_author_cross_reference",
    "qualifiers": {
        "source_line_start": 66,
        "source_line_end": 66,
        "claim": "The bibliography redirects Gregorio de Andrés’s entry to the joint Harris, Enriqueta and Andrés, Gregorio de entry at source line 578.",
        "speaker": "Haskell’s bibliography",
        "text_layer": "author cross-reference",
        "qualification": "The target line is queued for later S2 processing. The cross-reference supplies full author forms for surname-only note candidates, but consolidation of candidates and external identity alignment remain for S3.",
        "target_source_line": 578,
        "target_source_line_status": "queued",
        "related_candidate_ids_for_s3": ["cand-11166", "cand-11167", "cand-1292"],
        "relation_candidate": False,
        "mentioned_candidate_ids": ["cand-1292", "cand-11167"],
        "page_image_ocr_corrections": [{"line": 66, "ocr": "Andres", "print": "Andrés"}],
    },
    "original_quote": crossref_quote,
    "origin": "book",
    "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
})

if len(new_mentions) != 32 or len(new_statements) != 31 or len(new_candidates) != 8:
    raise SystemExit("unexpected migration row counts")
for statement in new_statements:
    if statement["statement_id"] in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement['statement_id']}")
    if statement["segment_id"] != SEGMENT:
        raise SystemExit("statement points to wrong segment")
    if statement.get("object_candidate_id") and statement["object_candidate_id"] not in candidate_by_id:
        raise SystemExit(f"statement candidate FK missing: {statement['statement_id']}")

# Add same-book cross-reference evidence to the existing surname-only author
# candidates without changing their IDs or resolving external identities.
candidate_detail_updates = {
    "cand-11166": "Bibliography line 66 cross-references the p.401 note’s Harris form to the full printed author name Enriqueta Harris and the joint entry at line 578. This is within-book citation evidence; alignment with other Harris candidates remains for S3.",
    "cand-11167": "Bibliography line 66 cross-references the p.401 note’s de Andrés form to the full printed author name Gregorio de Andrés and the joint entry at line 578. This is within-book citation evidence; external identity alignment remains for S3.",
    "cand-11200": "Bibliography lines 56–57 identify the p.405 note 4 Aikema short citation with the title ‘Patronage in late baroque Venice: the Zenobio’ (1979). The article itself was not independently consulted.",
    "cand-11201": "Bibliography line 67 gives the full author form Francesca D’Arcais for the Bellucci-in-Vienna article cited at p.406 note 5. External identity alignment remains for S3.",
    "cand-11202": "Bibliography line 67 identifies the p.406 note 5 D’Arcais short citation with ‘L’attività viennese di Antonio Bellucci’ (Arte Veneta, 1964, pp. 99–109). The article itself was not independently consulted.",
}
for candidate_id, added_detail in candidate_detail_updates.items():
    candidate = candidate_by_id.get(candidate_id)
    if not candidate:
        raise SystemExit(f"missing candidate for same-book bibliography reconciliation: {candidate_id}")
    if added_detail in candidate.get("detail", ""):
        raise SystemExit(f"candidate detail already updated: {candidate_id}")

new_candidates = sorted(new_candidates, key=lambda row: int(row["candidate_id"].split("-")[1]))
all_candidates = candidates + new_candidates
all_mentions = mentions + new_mentions
all_statements = statements + new_statements
for row in all_mentions:
    if row["segment_id"] == SEGMENT:
        segment_start, segment_end = row["start_char"], row["end_char"]
        if segment_text[segment_start:segment_end] != row["surface_form"]:
            raise SystemExit(f"mention offset validation failed: {row['mention_id']}")

coverage_by_id[SEGMENT]["disposition"] = "reviewed"
coverage_by_id[SEGMENT]["migration_status"] = "complete"
coverage_by_id[SEGMENT]["source_line_ranges"] = "L47-85"
coverage_by_id[SEGMENT]["note"] = "Printed p.412: section heading, 29 publication entries, and one author cross-reference. Page-image OCR corrections are recorded in statements; cited works were not independently read."
all_coverage = [coverage_by_id[row["segment_id"]] for row in coverage]

print(json.dumps({
    "mode": "apply" if ARGS.apply else "dry-run",
    "segment": SEGMENT,
    "new_publication_candidates": [row["candidate_id"] for row in new_candidates],
    "reused_publication_candidates": 29 - len(new_candidates),
    "mentions_added": len(new_mentions),
    "statements_added": len(new_statements),
    "candidate_detail_updates": sorted(candidate_detail_updates),
    "coverage": {"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L47-85"},
}, ensure_ascii=False, indent=2))

if ARGS.apply:
    for path in (candidate_path, mention_path, statement_path, coverage_path):
        backup = path.with_name(path.name + BACKUP)
        if backup.exists():
            raise SystemExit(f"recovery copy already exists: {backup.name}")
        shutil.copy2(path, backup)
    for candidate_id, added_detail in candidate_detail_updates.items():
        candidate_by_id[candidate_id]["detail"] = (candidate_by_id[candidate_id].get("detail", "").rstrip() + " " + added_detail).strip()
    write_csv(candidate_path, candidate_fields, all_candidates)
    write_csv(mention_path, mention_fields, all_mentions)
    write_jsonl(statement_path, all_statements)
    write_csv(coverage_path, coverage_fields, all_coverage)
