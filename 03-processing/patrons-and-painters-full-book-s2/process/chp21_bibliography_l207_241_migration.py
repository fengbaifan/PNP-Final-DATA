#!/usr/bin/env python3
"""Controlled S2 migration for bibliography entries and cross-reference on p. 416."""
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
SEGMENT = "chp-21:21_CHP-21Bibliography:l207-241"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
SEGMENT_SHA = "c1f7139fc74ef6c3195974ce3e4be2dfefe41c87bb6e94f2e22512dc3a75e7a6"
BACKUP = ".bak-s2-chp21-bibliography-l207-241-20261004"

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
segment_text = "\n".join(source_lines[206:241])
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
if (len(candidates), len(mentions), len(statements), len(coverage)) != (11231, 26064, 11341, 832):
    raise SystemExit("unexpected bibliography S2 pre-state")

candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}
if SEGMENT not in coverage_by_id or (coverage_by_id[SEGMENT]["disposition"], coverage_by_id[SEGMENT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("bibliography segment is not queued")

new_candidate_specs = [
    ("cand-11253", "Anthony Blunt and Hereward Lester Cooke, Roman drawings at Windsor Castle (London, 1961)", 208, "The bibliography identifies the joint book; contents were not independently consulted."),
    ("cand-11254", "Anthony Blunt, Nicolas Poussin—the A. W. Mellon Lectures in the Fine Arts (lectures 1958; New York, 1967)", 211, "The bibliography gives the lecture series title and the 1967 New York publication; contents were not independently consulted."),
    ("cand-11255", "Anthony Blunt, Supplements to the catalogues of Italian and French Drawings, published with Edmund Schilling’s The German Drawings in the Collection of Her Majesty the Queen at Windsor Castle (London and New York, 1971)", 213, "The composite bibliography entry is preserved as printed; no independent contents or component-edition distinction is inferred."),
    ("cand-11256", "Anthony Blunt, Borromini (London, 1979)", 215, "The bibliography identifies the book; contents were not independently consulted."),
    ("cand-11257", "Mme de Boccage, Letters concerning England, Holland and Italy (2 vols., London, 1770)", 216, "The bibliography identifies a two-volume set. Keep distinct from volume-I citation candidate cand-9521 pending S3 identity review."),
    ("cand-11258", "Fabia Borroni Salvadori, ‘Le Esposizioni d’Arte a Firenze dal 1674 al 1767’ (Mitteilungen des Kunsthistorischen Institutes in Florenz, vol. XVIII, 1974, Heft I, pp. 1–166)", 225, "The bibliography identifies the article; cited contents were not independently consulted."),
    ("cand-11259", "Angelo Borzelli, L’Assunta del Lanfranco in S. Andrea della Valle giudicata da Ferrante Carli (Naples, 1910)", 229, "The bibliography identifies the book; contents were not independently consulted."),
    ("cand-11260", "Boscovich, Lettere pubblicate per le nozze Olivieri-Balbi (Venice, 1811)", 232, "The bibliography identifies the publication set. Keep distinct from specific letter candidate cand-10450 pending S3 identity review."),
    ("cand-11261", "Giovanni Bottari and Stefano Ticozzi, Raccolta di lettere sulla Pittura, Scultura ed Architettura (Milan, 1822)", 235, "The bibliography identifies the collection; volume-level citations remain distinct for S3 alignment, including cand-4830, cand-5461, cand-5503, cand-6200, cand-7516, and cand-8584."),
    ("cand-11262", "Ferdinand Boyer, ‘Documents d’Archives Romaines et Florentines sur le Valentin, le Poussin et le Lorrain’ (Bulletin de la Société de l’Histoire de l’Art Français, 1931, pp. 233–238)", 236, "The bibliography identifies the article; page-image correction of the OCR page range is recorded in its statement."),
    ("cand-11263", "A. Bozzòla, Casanova illuminista (Venice, 1956)", 240, "The bibliography identifies the book; contents were not independently consulted."),
]

entries = [
    {"candidate_id":"cand-11253","start":208,"end":209,"author":"Blunt, Anthony and Cooke, Hereward Lester","title":"Roman drawings at Windsor Castle","details":"London, 1961","kind":"book"},
    {"candidate_id":"cand-9340","start":210,"end":210,"author":"Blunt, Anthony and Croft-Murray, Edward","title":"Venetian drawings of the XVII and XVIII centuries in the collection of Her Majesty the Queen at Windsor Castle","details":"London, 1957","kind":"catalogue"},
    {"candidate_id":"cand-11254","start":211,"end":212,"author":"Blunt, Anthony","title":"Nicolas Poussin—the A. W. Mellon Lectures in the Fine Arts","details":"Lectures 1958; New York, 1967","kind":"published lecture"},
    {"candidate_id":"cand-11255","start":213,"end":214,"author":"Blunt, Anthony","title":"Supplements to the catalogues of Italian and French Drawings—published with Edmund Schilling: The German Drawings in the Collection of Her Majesty the Queen at Windsor Castle","details":"London and New York, 1971","kind":"catalogue supplement / accompanying publication"},
    {"candidate_id":"cand-11256","start":215,"end":215,"author":"Blunt, Anthony","title":"Borromini","details":"London, 1979","kind":"book"},
    {"candidate_id":"cand-11257","start":216,"end":216,"author":"Boccage, Mme de","title":"Letters concerning England, Holland and Italy","details":"2 vols., London, 1770","kind":"book","related":["cand-9521"]},
    {"candidate_id":"cand-7348","start":217,"end":217,"author":"Bologna, Ferdinando","title":"Francesco Solimena","details":"Naples, 1958","kind":"book"},
    {"candidate_id":"cand-11163","start":218,"end":219,"author":"Bonadonna Russo, Maria Teresa","title":"I Cesi e la Congregazione dell’Oratorio","details":"Archivio della Società Romana di Storia Patria, vol. 90 (1967), pp. 101–163 and vol. 91 (1968), pp. 101–155","kind":"journal article, two installments","corrections":[{"line":219,"ocr":"Voi. 90; Vol. 9s","print":"Vol. 90; Vol. 91"}]},
    {"candidate_id":"cand-7042","start":220,"end":220,"author":"Bonnaffé, Edmond","title":"Dictionnaire des amateurs français au XVII siècle","details":"Paris, 1884","kind":"reference book"},
    {"candidate_id":"cand-4568","start":221,"end":221,"author":"Bonomelli, Emilio","title":"I Papi in campagna","details":"Rome, 1953","kind":"book"},
    {"candidate_id":"cand-11014","start":222,"end":222,"author":"Borea, Evelina","title":"La Quadreria di Don Lorenzo de’ Medici","details":"Florence, 1977","kind":"exhibition catalogue"},
    {"candidate_id":"cand-9366","start":223,"end":223,"author":"Borenius, Tancred","title":"A Venetian apotheosis of William III","details":"Burlington Magazine, 1936, pp. 245–246","kind":"journal article"},
    {"candidate_id":"cand-10193","start":224,"end":224,"author":"Borroni, Fabia","title":"I due Anton Maria Zanetti","details":"Florence, 1956","kind":"book","corrections":[{"line":224,"ocr":"Bortoni","print":"Borroni"}]},
    {"candidate_id":"cand-11258","start":225,"end":225,"author":"Borroni Salvadori, Fabia","title":"Le Esposizioni d’Arte a Firenze dal 1674 al 1767","details":"Mitteilungen des Kunsthistorischen Institutes in Florenz, vol. XVIII, 1974, Heft I, pp. 1–166","kind":"journal article","corrections":[{"line":225,"ocr":"Bortoni Salvadori","print":"Borroni Salvadori"}]},
    {"candidate_id":"cand-5588","start":226,"end":226,"author":"Borsari, L.","title":"Il castello di Bracciano","details":"Rome, 1895","kind":"book"},
    {"candidate_id":"cand-4562","start":227,"end":227,"author":"Borzelli, Angelo","title":"Il Cavalier Marino con gli artisti e la ‘galeria’","details":"Naples, 1891","kind":"book"},
    {"candidate_id":"cand-4561","start":228,"end":228,"author":"Borzelli, Angelo","title":"Il Cavalier Giovan Battista Marino","details":"Naples, 1898","kind":"book"},
    {"candidate_id":"cand-11259","start":229,"end":230,"author":"Borzelli, Angelo","title":"L’Assunta del Lanfranco in S. Andrea della Valle giudicata da Ferrante Carli","details":"Naples, 1910","kind":"book"},
    {"candidate_id":"cand-7166","start":231,"end":231,"author":"Boschini, Marco","title":"La carta del navegar pittoresco","details":"Venice, 1660","kind":"book"},
    {"candidate_id":"cand-11260","start":232,"end":232,"author":"Boscovich","title":"Lettere pubblicate per le nozze Olivieri-Balbi","details":"Venice, 1811","kind":"published letters collection","related":["cand-10450"]},
    {"candidate_id":"cand-10239","start":233,"end":233,"author":"Bosdari, Filippo","title":"Francesco Maria Zanotti nella vita bolognese del Settecento","details":"Atti e Memorie della R. Deputazione di Storia Patria per le provincie di Romagna, 1928, pp. 157–222","kind":"journal article"},
    {"candidate_id":"cand-8811","start":234,"end":234,"author":"Bosisio, Achille","title":"La chiesa di S. Maria della Visitazione o della Pietà","details":"Venice, 1951","kind":"book"},
    {"candidate_id":"cand-11261","start":235,"end":235,"author":"Bottari, Giovanni; continued by Stefano Ticozzi","title":"Raccolta di lettere sulla Pittura, Scultura ed Architettura scritta da’ più celebri personaggi dei secoli XV, XVI e XVII","details":"Published by M. Gio Bottari and continued through the present by Stefano Ticozzi; Milan, 1822","kind":"edited collection","related":["cand-4830","cand-5461","cand-5503","cand-6200","cand-7516","cand-8584"]},
    {"candidate_id":"cand-11262","start":236,"end":236,"author":"Boyer, Ferdinand","title":"Documents d’Archives Romaines et Florentines sur le Valentin, le Poussin et le Lorrain","details":"Bulletin de la Société de l’Histoire de l’Art Français, 1931, pp. 233–238","kind":"journal article","corrections":[{"line":236,"ocr":"23 3-23 8","print":"233–238"}]},
    {"candidate_id":"cand-5589","start":237,"end":237,"author":"Boyer, Ferdinand","title":"Les Orsini et les musiciens d’Italie au début du XVII siècle","details":"Mélanges de philologie, d’histoire et de littérature offerts à Henri Hauvette, Paris, 1934, pp. 301–310","kind":"essay in collected volume"},
    {"candidate_id":"cand-5590","start":238,"end":239,"author":"Boyer, Ferdinand","title":"Le mécénat des Orsini au début du XVII siècle","details":"Dante, vol. III, December 1934","kind":"journal article","quote":"Boyer, Ferdinand: ‘Le mécénat des Orsini au début du XVII siècle’ in Dante, III, Décembre\n1934","corrections":[{"line":239,"ocr":"1934Bozzòla","print":"1934. [new entry] Bozzòla"}]},
    {"candidate_id":"cand-10516","start":239,"end":239,"author":"Bozzòla, A.","title":"Inquietudini e velleità di riforma a Venezia nel 1761-2","details":"Bollettino Storico-Bibliografico Subalpino, 1948, pp. 93–116","kind":"journal article","quote":"Bozzòla, A.: ‘Inquietudini e velleità di riforma a Venezia nel 1761-2’ in Bollettino StoricoBibliografico Subalpino, 1948, pp. 93-116."},
    {"candidate_id":"cand-11263","start":240,"end":240,"author":"Bozzòla, A.","title":"Casanova illuminista","details":"Venice, 1956","kind":"book"},
]
if len(entries) != 28 or len({entry["candidate_id"] for entry in entries}) != 28:
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
    row.update(candidate_id=candidate_id, canonical_name=name, suggested_type="archive", status="open",
               detail=detail, candidate_origin="body-mention", candidate_source_ref=f"{SEGMENT}#L{line_number}")
    new_candidates.append(row)
    candidate_by_id[candidate_id] = row
    natural_keys.add(key)

for entry in entries:
    candidate = candidate_by_id.get(entry["candidate_id"])
    if not candidate or candidate.get("suggested_type") != "archive":
        raise SystemExit(f"missing/wrong-type publication candidate: {entry['candidate_id']}")

candidate_detail_updates = {
    "cand-11163": "Bibliography lines 218–219 identify the two-part Bonadonna Russo article as ‘I Cesi e la Congregazione dell’Oratorio’ in Archivio della Società Romana di Storia Patria, vol. 90 (1967), pp. 101–163, and vol. 91 (1968), pp. 101–155; the PDF corrects two OCR errors. The articles were not independently consulted.",
    "cand-4568": "Bibliography line 221 identifies Bonomelli’s publication as I Papi in campagna (Rome, 1953); contents were not independently consulted.",
    "cand-11014": "Bibliography line 222 identifies Evelina Borea’s 1977 Florence catalogue as La Quadreria di Don Lorenzo de’ Medici; catalogue contents were not independently consulted.",
    "cand-9366": "Bibliography line 223 identifies Borenius’s article as ‘A Venetian apotheosis of William III’ (Burlington Magazine, 1936, pp. 245–246); article not independently consulted.",
    "cand-10193": "Bibliography line 224 identifies Fabia Borroni’s book as I due Anton Maria Zanetti (Florence, 1956); the page image corrects the author surname from the S0 OCR. Contents were not independently consulted.",
    "cand-8811": "Bibliography line 234 identifies Bosisio’s publication as La chiesa di S. Maria della Visitazione o della Pietà (Venice, 1951); contents were not independently consulted.",
    "cand-4562": "Bibliography line 227 identifies Borzelli’s 1891 publication as Il Cavalier Marino con gli artisti e la ‘galeria’ (Naples); contents were not independently consulted.",
    "cand-4561": "Bibliography line 228 identifies Borzelli’s 1898 publication as Il Cavalier Giovan Battista Marino (Naples); contents were not independently consulted.",
    "cand-10516": "Bibliography line 239 identifies Bozzòla’s article as ‘Inquietudini e velleità di riforma a Venezia nel 1761-2’ (Bollettino Storico-Bibliografico Subalpino, 1948, pp. 93–116); the citation was merged with Boyer’s preceding article in S0 and is split by precise spans. Article not independently consulted.",
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
new_statements = []
existing_claim_keys = {
    (row.get("segment_id", ""), " ".join(str((row.get("qualifiers") or {}).get("claim", "")).split()).casefold())
    for row in statements if isinstance(row.get("qualifiers"), dict)
}


def source_quote(entry):
    return entry.get("quote") or "\n".join(source_lines[entry["start"] - 1:entry["end"]])


def add_mention(candidate_id, surface, note):
    position = segment_text.find(surface)
    if position < 0 or segment_text.find(surface, position + 1) >= 0:
        raise SystemExit(f"mention span text absent or ambiguous for {candidate_id}: {surface!r}")
    end = position + len(surface)
    key = (SEGMENT, candidate_id, str(position), str(end))
    if key in mention_keys:
        raise SystemExit(f"duplicate mention natural key: {candidate_id} {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update(mention_id=f"m-chp21-bib-l207-241-{len(new_mentions)+1:03d}", segment_id=SEGMENT,
               candidate_id=candidate_id, surface_form=surface, start_char=position, end_char=end, note=note)
    new_mentions.append(row)
    mention_keys.add(key)


def add_statement(statement_id, subject_id, object_id, predicate, quote, line_start, line_end, claim,
                  speaker="Haskell’s bibliography", text_layer="bibliographic entry", qualification=None,
                  mentioned_ids=None, record=None, extra=None):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    claim_key = (SEGMENT, " ".join(claim.split()).casefold())
    if claim_key in existing_claim_keys:
        raise SystemExit(f"duplicate statement claim: {claim}")
    existing_claim_keys.add(claim_key)
    qualifier = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification or "This statement records the bibliography entry; the cited publication was not independently consulted in this S2 pass.",
        "relation_candidate": False,
        "mentioned_candidate_ids": mentioned_ids or [object_id],
    }
    if record:
        qualifier["bibliographic_record"] = record
    if extra:
        qualifier.update(extra)
    statement = {
        "statement_id": statement_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": subject_id,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": qualifier,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
    }
    if not quote or quote not in "\n".join(source_lines[line_start - 1:line_end]):
        raise SystemExit(f"statement quote/line validation failed: {statement_id}")
    new_statements.append(statement)
    statement_by_id[statement_id] = statement


for entry in entries:
    quote = source_quote(entry)
    add_mention(entry["candidate_id"], quote,
                "S0 bibliography entry; any page-image OCR correction is recorded in its statement qualifiers.")
    extras = {}
    if entry.get("corrections"):
        extras["page_image_ocr_corrections"] = entry["corrections"]
    if entry.get("related"):
        extras["related_candidate_ids_for_s3"] = entry["related"]
    add_statement(
        f"st-chp21-bib-l207-241-entry-{len(new_statements)+1:02d}", None, entry["candidate_id"],
        "bibliography_lists_publication", quote, entry["start"], entry["end"],
        f"Haskell lists {entry['title']} in the book bibliography.",
        record={"author_as_printed": entry["author"], "title_as_printed": entry["title"],
                "publication_details_as_printed": entry["details"], "record_kind": entry["kind"], "printed_page": 416},
        extra=extras,
    )

crossref_quote = source_lines[240]
add_mention("cand-3479", "Bracciano, Duca di", "Bibliographic heading redirected by a printed ‘See’ cross-reference.")
add_mention("cand-0434", "Paolo Giordano", "Target heading in a printed bibliography cross-reference; identity remains subject to S3.")
add_statement(
    "st-chp21-bib-l207-241-crossref-01", "cand-3479", "cand-0434", "bibliography_cross_reference",
    crossref_quote, 241, 241,
    "Haskell’s bibliography redirects the heading ‘Bracciano, Duca di’ to ‘Paolo Giordano’.",
    text_layer="bibliographic cross-reference",
    qualification="Records the book’s printed ‘See’ direction only; it does not independently resolve the historical identity or authorize candidate merging.",
    mentioned_ids=["cand-3479", "cand-0434"],
    extra={"cross_reference_type": "see", "identity_resolution_deferred_to": "S3"},
)

if len(new_mentions) != 30 or len(new_statements) != 29 or len(new_candidates) != 11:
    raise SystemExit("unexpected migration row counts")
for statement in new_statements:
    for endpoint in (statement["subject_candidate_id"], statement["object_candidate_id"]):
        if endpoint and endpoint not in candidate_by_id:
            raise SystemExit(f"statement candidate FK missing: {statement['statement_id']}")
for row in new_mentions:
    if segment_text[row["start_char"]:row["end_char"]] != row["surface_form"]:
        raise SystemExit(f"mention offset validation failed: {row['mention_id']}")

coverage_by_id[SEGMENT]["disposition"] = "reviewed"
coverage_by_id[SEGMENT]["migration_status"] = "complete"
coverage_by_id[SEGMENT]["source_line_ranges"] = "L207-241"
coverage_by_id[SEGMENT]["note"] = "Printed p.416 contains 28 publication entries and one bibliographic cross-reference. S0 merges Boyer’s 1934 article ending with Bozzòla’s 1948 entry; separate exact spans are recorded. PDF comparison corrects Bonadonna Russo volume number, two Borroni surnames, and Boyer page range. The final ‘See’ cross-reference is recorded as a catalog pointer, not a formal historical relation."
all_candidates = candidates + sorted(new_candidates, key=lambda row: int(row["candidate_id"].split("-")[1]))
all_mentions = mentions + new_mentions
all_statements = statements + new_statements
all_coverage = [coverage_by_id[row["segment_id"]] for row in coverage]

print(json.dumps({
    "mode": "apply" if ARGS.apply else "dry-run",
    "segment": SEGMENT,
    "new_publication_candidates": [row["candidate_id"] for row in new_candidates],
    "reused_publication_candidates": 28 - len(new_candidates),
    "publication_entries": len(entries),
    "cross_reference": {"subject": "cand-3479", "target": "cand-0434", "predicate": "bibliography_cross_reference"},
    "mentions_added": len(new_mentions),
    "statements_added": len(new_statements),
    "candidate_detail_updates": sorted(candidate_detail_updates),
    "page_image_corrections": ["L219 Vol. 9s → Vol. 91", "L224 Bortoni → Borroni", "L225 Bortoni Salvadori → Borroni Salvadori", "L236 pp. 23 3-23 8 → pp. 233–238", "L239 split merged Boyer and Bozzòla entries"],
    "coverage": {"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L207-241"},
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
