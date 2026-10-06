#!/usr/bin/env python3
"""Controlled S2 migration for bibliography printed p. 428."""

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
SEGMENT = "chp-21:21_CHP-21Bibliography:l701-754"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
SEGMENT_SHA = "83bf278786ec87a2850b51344f9bd9e729021cc58077a5d0d5c8c52709e3998a"
BACKUP = ".bak-s2-chp21-bibliography-l701-754-20261007"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write changes; default is dry-run")
ARGS = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(handle.name)
    temporary.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("bibliography Markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("bibliography PDF changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[700:754])
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

if (len(candidates), len(mentions), len(statements), len(coverage)) != (
    11355,
    26424,
    11699,
    832,
):
    raise SystemExit("unexpected bibliography S2 pre-state")

candidate_by_id = {row["candidate_id"]: row for row in candidates}
coverage_by_id = {row["segment_id"]: row for row in coverage}
coverage_row = coverage_by_id.get(SEGMENT)
if not coverage_row or (
    coverage_row["disposition"],
    coverage_row["migration_status"],
) != ("queued", "pending"):
    raise SystemExit("bibliography segment is not queued")

# Enrich an existing local citation candidate only when the bibliography and
# its citation locator provide a usable local match. Ambiguous locators remain
# separate and are linked for S3 below.
candidate_updates = [
    {
        "id": "cand-7144",
        "expected": "Il Goya romano e la “cultura di Via Condotti” (Roberto Longhi; Paragone 53, 1954, pp. 28–39)",
        "name": "Il Goya romano e la “cultura di Via Condotti” (Roberto Longhi; Paragone 53, 1954, pp. 28–39)",
        "detail": "The bibliography at printed p.428 confirms the title, journal, year and pages for the existing citation. The article was not independently consulted; person-level identity remains for S3.",
    },
    {
        "id": "cand-7604",
        "expected": "Un collezionista di pittura napoletana nella Firenze del ’600 (R. Longhi, Paragone 75, 1956, pp.61-64)",
        "name": "Un collezionista di pittura napoletana nella Firenze del ’600 (R. Longhi, Paragone 75, 1956, pp. 61–64)",
        "detail": "The bibliography at printed p.428 confirms the title, journal, year and pages for the existing citation. The article was not independently consulted; author identity remains for S3.",
    },
    {
        "id": "cand-10856",
        "expected": "Roberto Longhi, 1963 publication cited for an alternative Maffeo portrait (title unspecified)",
        "name": "Roberto Longhi, ‘Il vero “Maffeo Barberini” del Caravaggio’ (Paragone, 1963, no. 165, pp. 3–11)",
        "detail": "The bibliography at printed p.428 supplies the title and publication details for the existing 1963 locator in the postscript. The article was not independently consulted; the other Longhi 1963 locator remains distinct for S3.",
    },
    {
        "id": "cand-10602",
        "expected": "Lorenzetti, 1914 (short-form biography citation; title unspecified)",
        "name": "G. Lorenzetti, ‘Il mercato artistico a Venezia nel Settecento’ (Fanfulla della Domenica, 1 Febbraio 1914)",
        "detail": "The bibliography at printed p.428 lists the only Lorenzetti 1914 item and supplies its title and periodical for the existing short-form citation about Sasso. The cited pages and article were not independently consulted; author identity remains for S3.",
    },
    {
        "id": "cand-6583",
        "expected": "Loret, I pittori napoletani a Roma nel Settecento (1934), p.545",
        "name": "M. Loret, ‘I pittori napoletani a Roma nel Settecento’ (Capitolium, 1934, pp. 541–555)",
        "detail": "Printed p.428 confirms Capitolium, 1934 and pp.541–555 for the existing p.545 citation. The cited page was not independently consulted; the page image corrects the OCR periodical spelling ‘Capitoliam’.",
    },
    {
        "id": "cand-6184",
        "expected": "Carandini family history (G. A. Lotti, 1784)",
        "name": "Giuseppe Antonio Lotti, Cenni storici della famiglia Carandini di Modena (Modena, 1784)",
        "detail": "Printed p.428 supplies the full title and place for the source-derived 1784 Carandini family history citation. The publication was not independently consulted; the author form is retained as printed.",
    },
    {
        "id": "cand-5683",
        "expected": "G. Lumbroso, Notizie sulla vita di Cassiano dal Pozzo (Turin, 1874)",
        "name": "G. Lumbroso, Notizie sulla vita di Cassiano dal Pozzo (Torino, 1874)",
        "detail": "Printed p.428 confirms the Italian place form Torino for the existing title/year match. Cited pages were not independently consulted; keep separate from the distinct p.137 Lumbroso citation pending S3.",
    },
    {
        "id": "cand-7052",
        "expected": "Alessandro Luzio, La galleria dei Gonzaga venduta all’Inghilterra nel 1627–38 (Milan, 1913)",
        "name": "Alessandro Luzio, La galleria dei Gonzaga venduta all’Inghilterra nel 1627–38 (Milano, 1913)",
        "detail": "Printed p.428 confirms the Italian place form Milano for the existing bibliographic title/year match. The cited contents were not independently consulted.",
    },
    {
        "id": "cand-7124",
        "expected": "The Spanish School (National Gallery Catalogue) (N. Maclaren, 1952)",
        "name": "N. Maclaren, The Spanish School (National Gallery Catalogue) (London, 1952)",
        "detail": "Printed p.428 confirms London 1952 for the existing publication candidate; Haskell's cited p.76 was not independently read. Person-level identity remains for S3.",
    },
    {
        "id": "cand-8269",
        "expected": "Madrisio's 1711 oration thanking Dionigi Delfino for the public library at Udine",
        "name": "Niccolò Madrisio, Orazione all’Illustriss. e Reverindiss. Monsignor Dionigi Delfino Patriarca d’Aquileja in rendimento di grazie per la sontuosa Libreria da lui aperta in Udine à pubblico, e perpetuo commodo della sua Diocesi (Venezia, 1711)",
        "detail": "Printed p.428 supplies the full title and publication details for this 1711 oration. The text was not consulted independently; the abbreviated spellings and accents in the title are retained from the source.",
    },
    {
        "id": "cand-4371",
        "expected": "Mahon (1947), cited study, pp. 111–154; title unspecified",
        "name": "D. Mahon, Studies in Seicento art and theory (London, 1947)",
        "detail": "Printed p.428 supplies the title and London publication details for the existing 1947, pp.111–154 citation. The cited pages were not independently consulted; author identity remains for S3.",
    },
    {
        "id": "cand-7057",
        "expected": "Denis Mahon, “Guercino’s paintings of Semiramis” (Burlington Magazine, 1949)",
        "name": "Denis Mahon, ‘Guercino’s paintings of Semiramis’ (Art Bulletin, 1949, pp. 217–223)",
        "detail": "Printed p.428 confirms Art Bulletin and pp.217–223 for the existing 1949 article candidate. The article was not independently consulted.",
    },
    {
        "id": "cand-5526",
        "expected": "Denis Mahon, publication from 1960 cited at pp. 288–304 (title unresolved in this note)",
        "name": "D. Mahon, ‘Poussin’s early development: an alternative hypothesis’ (Burlington Magazine, 1960, pp. 288–304)",
        "detail": "Printed p.428 confirms the title and Burlington Magazine record for the exact 1960 page locator. The article was not independently consulted; keep the separate 1960 Mahon citation candidates for S3.",
    },
    {
        "id": "cand-7070",
        "expected": "Denis Mahon, “Mazarin and Poussin” (Burlington Magazine, 1960)",
        "name": "Denis Mahon, ‘Mazarin and Poussin’ (Burlington Magazine, 1960, pp. 352–354)",
        "detail": "Printed p.428 confirms the page range for the existing title/year match. The article was not independently consulted.",
    },
    {
        "id": "cand-5905",
        "expected": "Denis Mahon, 1961 publication cited at p. 120 (title unspecified)",
        "name": "D. Mahon, ‘Reflexions sur les paysages de Poussin’ (Art de France, 1961, pp. 119–132)",
        "detail": "Printed p.428 confirms the title, periodical and page range containing the existing p.120 citation. Preserve the title spelling shown in the print; the article was not independently consulted.",
    },
    {
        "id": "cand-10454",
        "expected": "Malamani, Canova, p.6, cited in p.363 note 4",
        "name": "V. Malamani, Canova (Milano, n.d.)",
        "detail": "Printed p.428 confirms the title and place for the existing p.6 locator. The work was not independently consulted; a short trailing dash after ‘n.d.’ appears in print and is not treated as publication data.",
    },
    {
        "id": "cand-9461",
        "expected": "Malamani, ‘Rosalba Carriera’ (1899), p.77 (citation locator)",
        "name": "V. Malamani, ‘Rosalba Carriera’ (Le Gallerie Nazionali Italiane, 1899, pp. 27–149)",
        "detail": "Printed p.428 confirms the periodical and page range for the existing p.77 locator. Other Malamani 1899 locators remain separate and linked for S3; the article was not independently consulted.",
    },
    {
        "id": "cand-9299",
        "expected": "Duke of Manchester, vol. II (citation locator; work and edition unresolved)",
        "name": "Duke of Manchester, Court and Society from Elizabeth to Anne (2 vols., London, 1864)",
        "detail": "Printed p.428 supplies the title, two-volume extent and London 1864 for the existing volume-II citation. The cited contents were not independently consulted; identity of the author relative to person candidates remains for S3.",
    },
    {
        "id": "cand-6089",
        "expected": "Critical edition of Giulio Mancini's works (1956; title unspecified)",
        "name": "Giulio Mancini, Considerazioni sulla Pittura, ed. Adriana Marucchi, commentary by Luigi Salerno (2 vols., Roma, 1956)",
        "detail": "Printed p.428 supplies the title, editor, commentator and two-volume extent for the existing 1956 critical-edition candidate. The edition was not independently consulted; volume/page locators remain separately linked for S3.",
    },
    {
        "id": "cand-9936",
        "expected": "Manuel, pages 86 and 94 (citation locator)",
        "name": "F. E. Manuel, The Eighteenth Century confronts the Gods (Oxford, 1958)",
        "detail": "Printed p.428 supplies the title and Oxford 1958 for the existing pages 86 and 94 locator. The cited pages were not independently consulted; person-level identity remains for S3.",
    },
    {
        "id": "cand-8146",
        "expected": "Marcellino reference for Paolo Renier, p. 30, note 78",
        "name": "T. M. Marcellino, Una forte personalità nel patriziato veneziano del Settecento: Paolo Renier (Trieste, 1959)",
        "detail": "Printed p.428 supplies the title and publication details for the existing p.30 note 78 locator. The cited page was not independently consulted; the separate p.18 note 32 Marcellino locator remains for S3.",
    },
]

for update in candidate_updates:
    row = candidate_by_id.get(update["id"])
    if not row or row.get("suggested_type") != "archive":
        raise SystemExit(f"missing/wrong-type candidate update: {update['id']}")
    if row["canonical_name"] != update["expected"]:
        raise SystemExit(f"candidate pre-state changed: {update['id']}")
    row["canonical_name"] = update["name"]
    row["detail"] = update["detail"]

new_candidate_specs = [
    ("cand-11377", "R. Longhi, ‘Velazquez 1630: “La rissa all’ambasciata di Spagna”’ (Paragone, I, 1950, pp. 28–34)", "Bibliography entry at printed p.428. The article was not independently consulted; the cited bibliographic text and author form are preserved.", 702),
    ("cand-11378", "Antonio Longo, Memorie della vita—edizione seconda (4 vols., Venezia, 1820)", "Bibliography entry at printed p.428. The memoirs were not independently consulted; the existing volume-I page locator remains separate for S3.", 712),
    ("cand-11379", "G. Lorenzetti, Un dilettante incisore veneziano del XVIII secolo—Anton Maria Zanetti di Gerolamo (Venezia, 1917)", "Bibliography entry at printed p.428. Keep the two Lorenzetti 1917 citation locators distinct for S3; the work was not independently consulted.", 716),
    ("cand-11380", "G. Lorenzetti, Venezia e il suo estuario (Roma, 1956)", "Bibliography entry at printed p.428. The existing Lorenzetti 1956 citation locator remains distinct pending S3; the work was not independently consulted.", 718),
    ("cand-11381", "D. Mahon, ‘Addenda to Caravaggio’ (Burlington Magazine, 1952, pp. 3–23)", "Bibliography entry at printed p.428. The article was not independently consulted; author identity remains for S3.", 728),
    ("cand-11382", "D. Mahon, Poussiniana (published by Gazette des Beaux-Arts, Paris and New York, 1962)", "Bibliography entry at printed p.428. Preserve its distinction from the unspecified Mahon 1962 locator pending S3; the book was not independently consulted.", 736),
    ("cand-11383", "E. Male, L’art religieux de la fin du XVIème siècle, du XVIIème siècle et du XVIIIème siècle (Paris, 1951)", "Bibliography entry at printed p.428. The printed surname form is ‘Male’; do not add an accent absent from this source. The book was not independently consulted.", 741),
    ("cand-11384", "Carlo Cesare Malvasia, Felsina Pittrice (2 vols., Bologna, 1841 edition)", "Bibliography entry at printed p.428. This 1841 edition is kept distinct from the 1678-work citation candidate; edition alignment is for S3.", 743),
    ("cand-11385", "Giuseppe Manini, Serie de’ Senatori Fiorentini (Firenze, 1722)", "Bibliography entry at printed p.428. The book was not independently consulted; possible alignment with the existing Giuseppe Manini person candidate remains for S3.", 748),
    ("cand-11386", "A. Marabottini, ‘Novità sul Lucchesino’ (Commentari, 1954, pp. 116–135)", "One of two separately titled 1954 articles in the combined bibliography entry at printed p.428. The citation locator cand-5898 remains distinct pending S3; the article was not independently consulted.", 750),
    ("cand-11387", "A. Marabottini, ‘Il “Trattato di Pittura” e i disegni del Lucchesino’ (Commentari, 1954, pp. 217–244)", "One of two separately titled 1954 articles in the combined bibliography entry at printed p.428. The citation locator cand-5898 remains distinct pending S3; the article was not independently consulted.", 750),
    ("cand-11388", "A. Marabottini, ‘Il naturalismo di Pietro Paolini’ (Scritti di storia dell’Arte in onore di Mario Salmi, vol. III, 1963, pp. 306–324)", "Bibliography entry at printed p.428. Keep separate from the title-unspecified 1963 citation about The Death of Wallenstein pending S3; the chapter was not independently consulted.", 751),
]

new_candidates = []
natural_keys = {}
for row in candidates:
    key = (row["canonical_name"].strip().casefold(), row["suggested_type"].casefold())
    natural_keys.setdefault(key, set()).add(row["candidate_id"])
for candidate_id, canonical_name, detail, source_line in new_candidate_specs:
    if candidate_id in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    key = (canonical_name.strip().casefold(), "archive")
    if natural_keys.get(key):
        raise SystemExit(f"candidate natural-key collision: {candidate_id} {canonical_name}")
    row = {field: "" for field in candidate_fields}
    row.update(
        candidate_id=candidate_id,
        canonical_name=canonical_name,
        suggested_type="archive",
        status="open",
        detail=detail,
        candidate_origin="body-mention",
        candidate_source_ref=f"{SEGMENT}#L{source_line}",
    )
    new_candidates.append(row)
    candidate_by_id[candidate_id] = row
    natural_keys.setdefault(key, set()).add(candidate_id)

entries = [
    {"candidate_id":"cand-11377","start":702,"end":704,"author":"Longhi, R.","title":"‘Velazquez 1630: “La rissa all’ambasciata di Spagna”’","details":"Paragone, I, 1950, pp. 28–34","kind":"journal article","related":["cand-5505","cand-7603"],"corrections":[{"line":702,"ocr":"Paragone,","print":"in Paragone,","note":"Periodical heading displaced above this record in OCR."},{"line":703,"ocr":"in I, 1950, pp.","print":"in Paragone, I, 1950, pp."}]},
    {"candidate_id":"cand-7144","start":705,"end":706,"author":"Longhi, R.","title":"‘Il Goya romano e la “cultura di Via Condotti”’","details":"Paragone, 53, 1954, pp. 28–39","kind":"journal article","related":["cand-5505","cand-7603"],"corrections":[{"line":705,"ocr":"Paragone,","print":"in Paragone,","note":"Periodical heading displaced above this record in OCR."}]},
    {"candidate_id":"cand-7604","start":707,"end":709,"author":"Longhi, R.","title":"‘Un collezionista di pittura napoletana nella Firenze del ’600’","details":"Paragone, 75, 1956, pp. 61–64","kind":"journal article","related":["cand-5505","cand-7603"],"corrections":[{"line":707,"ocr":"Paragone,","print":"in Paragone,","note":"Periodical heading displaced above this record in OCR."}]},
    {"candidate_id":"cand-10856","start":710,"end":711,"author":"Longhi, R.","title":"‘Il vero “Maffeo Barberini” del Caravaggio’","details":"Paragone, 1963, no. 165, pp. 3–11","kind":"journal article","related":["cand-5505","cand-7603","cand-4350"],"corrections":[{"line":710,"ocr":"Paragone,","print":"in Paragone,","note":"Periodical heading displaced above this record in OCR."}]},
    {"candidate_id":"cand-11378","start":712,"end":712,"author":"Longo, Antonio","title":"Memorie della vita—edizione seconda","details":"4 vols., Venezia 1820","kind":"multi-volume book","related":["cand-1435","cand-8426"],"corrections":[{"line":712,"ocr":"1820.\"","print":"1820.","note":"The trailing quotation mark is absent from the printed page."}]},
    {"candidate_id":"cand-10602","start":713,"end":715,"author":"Lorenzetti, G.","title":"‘Il mercato artistico a Venezia nel Settecento’","details":"Fanfulla della Domenica, 1 Febbraio 1914","kind":"journal article","related":["cand-9947"],"corrections":[{"line":713,"ocr":"Fanfulla della Domenica,","print":"in Fanfulla della Domenica,","note":"Periodical heading displaced above this record in OCR."},{"line":715,"ocr":"I Febbraio 1914","print":"1 Febbraio 1914","note":"The printed date begins with the numeral 1."}]},
    {"candidate_id":"cand-11379","start":716,"end":717,"author":"Lorenzetti, G.","title":"Un dilettante incisore veneziano del XVIII secolo—Anton Maria Zanetti di Gerolamo","details":"Venezia 1917","kind":"book","related":["cand-9947","cand-9948","cand-10192"]},
    {"candidate_id":"cand-11380","start":718,"end":718,"author":"Lorenzetti, G.","title":"Venezia e il suo estuario","details":"Roma 1956","kind":"book","related":["cand-9947","cand-8791"]},
    {"candidate_id":"cand-6583","start":719,"end":720,"author":"Loret, M.","title":"‘I pittori napoletani a Roma nel Settecento’","details":"Capitolium, 1934, pp. 541—555","kind":"journal article","surface":"Capitoliam,\nLoret, M.: ‘I pittori napoletani a Roma nel Settecento’ in 1934, pp. 541—555","quote":"Capitoliam,\nLoret, M.: ‘I pittori napoletani a Roma nel Settecento’ in 1934, pp. 541—555","related":["cand-7625"],"corrections":[{"line":719,"ocr":"Capitoliam,","print":"Capitolium,","note":"The page image reads Capitolium."},{"line":720,"ocr":"555Lotti,","print":"555.\nLotti,","note":"Two printed entries were fused without punctuation or spacing in the OCR."}]},
    {"candidate_id":"cand-6184","start":720,"end":720,"author":"Lotti, Giuseppe Antonio","title":"Cenni storici della famiglia Carandini di Modena","details":"Modena 1784","kind":"book","surface":"Lotti, Giuseppe Antonio: Cenni storici della famiglia Carandini di Modena, Modena 1784.","quote":"Lotti, Giuseppe Antonio: Cenni storici della famiglia Carandini di Modena, Modena 1784.","related":["cand-6185"]},
    {"candidate_id":"cand-5683","start":721,"end":721,"author":"Lumbroso, G.","title":"Notizie sulla vita di Cassiano dal Pozzo","details":"Torino 1874","kind":"book","related":["cand-5626"]},
    {"candidate_id":"cand-7052","start":722,"end":722,"author":"Luzio, Alessandro","title":"La galleria dei Gonzaga venduta all’Inghilterra nel 1627-38","details":"Milano 1913","kind":"book"},
    {"candidate_id":"cand-7124","start":723,"end":723,"author":"Maclaren, N.","title":"The Spanish School (National Gallery Catalogue)","details":"London 1952","kind":"book","related":["cand-7123"]},
    {"candidate_id":"cand-8269","start":724,"end":724,"author":"Madrisio, Niccolò","title":"Orazione all’Illustriss. e Reverindiss. Monsignor Dionigi Delfino Patriarca d’Aquileja in rendimento di grazie per la sontuosa Libreria da lui aperta in Udine à pubblico, e perpetuo commodo della sua Diocesi","details":"Venezia 1711","kind":"oration","related":["cand-8268"]},
    {"candidate_id":"cand-4371","start":725,"end":725,"author":"Mahon, D.","title":"Studies in Seicento art and theory","details":"London 1947","kind":"book","related":["cand-1494"]},
    {"candidate_id":"cand-7057","start":726,"end":727,"author":"Mahon, D.","title":"‘Guercino’s paintings of Semiramis’","details":"Art Bulletin, 1949, pp. 217-223","kind":"journal article","related":["cand-1494"],"corrections":[{"line":726,"ocr":"Art Bulletin,","print":"in Art Bulletin,","note":"Periodical heading displaced above this record in OCR."}]},
    {"candidate_id":"cand-11381","start":728,"end":729,"author":"Mahon, D.","title":"‘Addenda to Caravaggio’","details":"Burlington Magazine, 1952, pp. 3-23","kind":"journal article","related":["cand-1494"],"corrections":[{"line":728,"ocr":"Burlington Magazine,","print":"in Burlington Magazine,","note":"Periodical heading displaced above this record in OCR."}]},
    {"candidate_id":"cand-5526","start":730,"end":731,"author":"Mahon, D.","title":"‘Poussin’s early development: an alternative hypothesis’","details":"Burlington Magazine, 1960, pp. 288-304","kind":"journal article","related":["cand-1494"],"corrections":[{"line":730,"ocr":"Burlington Magazine,","print":"in Burlington Magazine,","note":"Periodical heading displaced above this record in OCR."},{"line":731,"ocr":"i960","print":"1960"}]},
    {"candidate_id":"cand-7070","start":732,"end":733,"author":"Mahon, D.","title":"‘Mazarin and Poussin’","details":"Burlington Magazine, 1960, pp. 352-354","kind":"journal article","related":["cand-1494"],"corrections":[{"line":732,"ocr":"Burlington Magazine,","print":"in Burlington Magazine,","note":"Periodical heading displaced above this record in OCR."},{"line":733,"ocr":"i960","print":"1960"}]},
    {"candidate_id":"cand-5905","start":734,"end":735,"author":"Mahon, D.","title":"‘Reflexions sur les paysages de Poussin’","details":"Art de France, 1961, pp. 119-132","kind":"journal article","related":["cand-1494"],"corrections":[{"line":734,"ocr":"Art de France,","print":"in Art de France,","note":"Periodical heading displaced above this record in OCR."}]},
    {"candidate_id":"cand-11382","start":736,"end":737,"author":"Mahon, D.","title":"Poussiniana","details":"published by Gazette des Beaux-Arts, Paris and New York 1962","kind":"book","related":["cand-1494","cand-4867"],"corrections":[{"line":736,"ocr":"Gazette des Beaux-Arts,","print":"published by Gazette des Beaux-Arts,","note":"Publisher heading displaced above this record in OCR."}]},
    {"candidate_id":"cand-10454","start":738,"end":738,"author":"Malamani, V.","title":"Canova","details":"Milano n.d. -","kind":"book","related":["cand-8664","cand-9433"],"page_image_notes":["A short dash follows ‘n.d.’ in print; it is retained as printed punctuation and not interpreted as publication data."]},
    {"candidate_id":"cand-9461","start":739,"end":740,"author":"Malamani, V.","title":"‘Rosalba Carriera’","details":"Le Gallerie Nazionali Italiane, 1899, pp. 27-149","kind":"journal article","related":["cand-8664","cand-9433","cand-8656","cand-9282","cand-9288","cand-9434","cand-9529","cand-9532"],"corrections":[{"line":739,"ocr":"Le Gallerie Nazionali Italiane,","print":"in Le Gallerie Nazionali Italiane,","note":"Periodical heading displaced above this record in OCR."}]},
    {"candidate_id":"cand-11383","start":741,"end":742,"author":"Male, E.","title":"L’art religieux de la fin du XVIème siècle, du XVIIème siècle et du XVIIIème siècle","details":"Paris 1951","kind":"book","corrections":[{"line":741,"ocr":"XVIlème","print":"XVIIème","note":"The page image has Roman numeral XVII; the OCR confuses the final capital I with lowercase l."}]},
    {"candidate_id":"cand-11384","start":743,"end":743,"author":"Malvasia, Carlo Cesare","title":"Felsina Pittrice","details":"2 vols., Bologna 1841","kind":"multi-volume book","related":["cand-6933","cand-1501","cand-1502"],"page_image_notes":["This bibliography entry identifies the 1841 two-volume edition; keep it distinct from the separately represented 1678 work pending S3."]},
    {"candidate_id":"cand-9299","start":744,"end":744,"author":"Manchester, Duke of","title":"Court and Society from Elizabeth to Anne","details":"2 vols., London 1864","kind":"multi-volume book","related":["cand-1504","cand-1505"]},
    {"candidate_id":"cand-6089","start":745,"end":746,"author":"Mancini, Giulio","title":"Considerazioni sulla Pittura","details":"published for the first time by Adriana Marucchi, commentary by Luigi Salerno, 2 vols., Roma 1956","kind":"critical edition","related":["cand-1507","cand-1508","cand-5726","cand-11158","cand-6066"]},
    {"candidate_id":"cand-5600","start":747,"end":747,"author":"Mandosio, Prospero","title":"Bibliotheca Romana","details":"Romae 1682","kind":"book","related":["cand-5599"]},
    {"candidate_id":"cand-11385","start":748,"end":748,"author":"Manini, Giuseppe","title":"Serie de’ Senatori Fiorentini","details":"Firenze 1722","kind":"book","related":["cand-7505","cand-8780"]},
    {"candidate_id":"cand-9936","start":749,"end":749,"author":"Manuel, F. E.","title":"The Eighteenth Century confronts the Gods","details":"Oxford 1958","kind":"book","related":["cand-9935"]},
    {"candidate_id":"cand-11386","start":750,"end":750,"author":"Marabottini, A.","title":"‘Novità sul Lucchesino’","details":"Commentari, 1954, pp. 116-135","kind":"journal article","mentions":["‘Novità sul Lucchesino’"],"related":["cand-5897","cand-5898"],"corrections":[{"line":750,"ocr":"LucCommentari, chesino","print":"Luc- / chesino’ in Commentari","note":"The page image shows two titled studies; a line break and journal label were interleaved by OCR."}],"page_image_notes":["The printed bibliographic line names two distinct articles and gives a separate page range for each; this statement records the first title and pp.116–135."]},
    {"candidate_id":"cand-11387","start":750,"end":750,"author":"Marabottini, A.","title":"‘Il “Trattato di Pittura” e i disegni del Lucchesino’","details":"Commentari, 1954, pp. 217-244","kind":"journal article","mentions":["‘Il “Trattato di Pittura” e i disegni del Luc",{"surface":"chesino’","occurrence":1}],"related":["cand-5897","cand-5898"],"corrections":[{"line":750,"ocr":"LucCommentari, chesino","print":"Luc- / chesino’ in Commentari","note":"The page image shows two titled studies; a line break and journal label were interleaved by OCR."}],"page_image_notes":["The printed bibliographic line names two distinct articles and gives a separate page range for each; this statement records the second title and pp.217–244."]},
    {"candidate_id":"cand-11388","start":751,"end":752,"author":"Marabottini, A.","title":"‘Il naturalismo di Pietro Paolini’","details":"Scritti di storia dell’Arte in onore di Mario Salmi, 1963, III, pp. 306-324","kind":"contributed chapter","related":["cand-5897","cand-6191"]},
    {"candidate_id":"cand-8146","start":753,"end":754,"author":"Marcellino, T. M.","title":"Una forte personalità nel patriziato veneziano del Settecento: Paolo Renier","details":"Trieste 1959","kind":"book","related":["cand-8430","cand-8431"]},
]

covered_lines = {line for entry in entries for line in range(entry["start"], entry["end"] + 1)}
if covered_lines != set(range(702, 755)):
    raise SystemExit(f"bibliography line coverage incomplete: missing={sorted(set(range(702,755))-covered_lines)}")
if len(entries) != 34:
    raise SystemExit(f"unexpected publication count: {len(entries)}")
if [row["candidate_id"] for row in new_candidates] != [f"cand-{i}" for i in range(11377, 11389)]:
    raise SystemExit("new candidate IDs are not the expected next sequence")

mention_keys = {
    (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"]))
    for row in mentions
}
mention_ids = {row["mention_id"] for row in mentions}
new_mentions = []
new_statements = []
statement_ids = {row["statement_id"] for row in statements}
existing_claim_keys = {
    (
        row.get("segment_id", ""),
        " ".join(str((row.get("qualifiers") or {}).get("claim", "")).split()).casefold(),
    )
    for row in statements
    if isinstance(row.get("qualifiers"), dict)
}


def source_quote(entry):
    return entry.get("quote") or "\n".join(source_lines[entry["start"] - 1:entry["end"]])


def add_mention(candidate_id, surface, note, occurrence=0):
    positions = [index for index in range(len(segment_text)) if segment_text.startswith(surface, index)]
    if len(positions) <= occurrence:
        raise SystemExit(f"mention span text absent for {candidate_id}: {surface!r}")
    position = positions[occurrence]
    end = position + len(surface)
    key = (SEGMENT, candidate_id, str(position), str(end))
    if key in mention_keys:
        raise SystemExit(f"duplicate mention natural key: {candidate_id} {surface!r}")
    mention_id = f"m-chp21-bib-l701-754-{len(new_mentions) + 1:03d}"
    if mention_id in mention_ids:
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    row = {field: "" for field in mention_fields}
    row.update(
        mention_id=mention_id,
        segment_id=SEGMENT,
        candidate_id=candidate_id,
        surface_form=surface,
        start_char=position,
        end_char=end,
        note=note,
    )
    new_mentions.append(row)
    mention_keys.add(key)
    mention_ids.add(mention_id)


def add_statement(statement_id, claim, entry, candidate_id):
    if statement_id in statement_ids:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    claim_key = (SEGMENT, " ".join(claim.split()).casefold())
    if claim_key in existing_claim_keys:
        raise SystemExit(f"duplicate statement claim: {claim}")
    statement_ids.add(statement_id)
    existing_claim_keys.add(claim_key)
    related = entry.get("related", [])
    qualifiers = {
        "source_line_start": entry["start"],
        "source_line_end": entry["end"],
        "claim": claim,
        "speaker": "Haskell’s bibliography",
        "relation_candidate": False,
        "mentioned_candidate_ids": [candidate_id],
        "text_layer": "bibliographic entry",
        "qualification": "This records the bibliography entry only; the cited publication was not independently consulted in this S2 pass.",
        "bibliographic_record": {
            "author_as_printed": entry["author"],
            "title_as_printed": entry["title"],
            "publication_details_as_printed": entry["details"],
            "record_kind": entry["kind"],
            "printed_page": 428,
        },
    }
    if entry.get("corrections"):
        qualifiers["page_image_ocr_corrections"] = entry["corrections"]
    if entry.get("page_image_notes"):
        qualifiers["page_image_notes"] = entry["page_image_notes"]
    if related:
        qualifiers["related_candidate_ids_for_s3"] = related
    quote = source_quote(entry)
    if not quote or quote not in "\n".join(source_lines[entry["start"] - 1:entry["end"]]):
        raise SystemExit(f"statement quote/line validation failed: {statement_id}")
    new_statements.append({
        "statement_id": statement_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": None,
        "object_candidate_id": candidate_id,
        "predicate": "bibliography_lists_publication",
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
    })


for index, entry in enumerate(entries, start=1):
    candidate_id = entry["candidate_id"]
    candidate = candidate_by_id.get(candidate_id)
    if not candidate or candidate.get("suggested_type") != "archive":
        raise SystemExit(f"missing/wrong-type bibliographic candidate: {candidate_id}")
    for related_id in entry.get("related", []):
        if related_id not in candidate_by_id:
            raise SystemExit(f"related candidate FK missing: {candidate_id}: {related_id}")
    quote = source_quote(entry)
    for mention in entry.get("mentions", [entry.get("surface", quote)]):
        if isinstance(mention, dict):
            surface = mention["surface"]
            occurrence = mention.get("occurrence", 0)
        else:
            surface = mention
            occurrence = 0
        add_mention(
            candidate_id,
            surface,
            "S0 bibliography entry; page-image layout readings and S3 comparisons are recorded on its statement.",
            occurrence,
        )
    title = entry["title"].strip("‘’\" ")
    claim = f"Haskell lists {title} in the bibliography."
    add_statement(
        f"st-chp21-bib-l701-754-entry-{index:02d}",
        claim,
        entry,
        candidate_id,
    )

if len(new_candidates) != 12 or len(new_mentions) != 35 or len(new_statements) != 34:
    raise SystemExit(
        f"unexpected migration row counts: candidates={len(new_candidates)}, "
        f"mentions={len(new_mentions)}, statements={len(new_statements)}"
    )

for statement in new_statements:
    if statement["object_candidate_id"] not in candidate_by_id:
        raise SystemExit(f"statement candidate FK missing: {statement['statement_id']}")
    qualifiers = statement["qualifiers"]
    for field in ("mentioned_candidate_ids", "related_candidate_ids_for_s3"):
        for candidate_id in qualifiers.get(field, []):
            if candidate_id not in candidate_by_id:
                raise SystemExit(f"{field} FK missing: {statement['statement_id']}: {candidate_id}")

for row in new_mentions:
    if segment_text[row["start_char"]:row["end_char"]] != row["surface_form"]:
        raise SystemExit(f"mention offset validation failed: {row['mention_id']}")
ordered_mentions = sorted(new_mentions, key=lambda row: (int(row["start_char"]), int(row["end_char"])))
for left, right in zip(ordered_mentions, ordered_mentions[1:]):
    if int(left["end_char"]) > int(right["start_char"]):
        raise SystemExit(f"overlapping mention spans: {left['mention_id']} and {right['mention_id']}")

coverage_row["disposition"] = "reviewed"
coverage_row["migration_status"] = "complete"
coverage_row["source_line_ranges"] = "L702-754"
coverage_row["note"] = (
    "Printed p.428 contains 33 bibliographic entries naming 34 publications; [Page 428] at L701 is only a page marker. "
    "Reused 22 archive candidates and added 12 publication candidates. Page-image review restores displaced periodical names, "
    "splits the L720 Loret/Lotti OCR collision, and records two separately titled Marabottini 1954 articles from one printed entry. "
    "Uncertain citation locators and edition relationships remain linked for S3; cited contents were not independently consulted."
)

all_candidates = candidates + new_candidates
all_mentions = mentions + new_mentions
all_statements = statements + new_statements
all_coverage = [coverage_by_id[row["segment_id"]] for row in coverage]

print(json.dumps({
    "mode": "apply" if ARGS.apply else "dry-run",
    "segment_id": SEGMENT,
    "candidate_updates": len(candidate_updates),
    "new_candidates": len(new_candidates),
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "candidate_count_after": len(all_candidates),
    "mention_count_after": len(all_mentions),
    "statement_count_after": len(all_statements),
    "coverage_rows": len(all_coverage),
    "publication_statements": len(new_statements),
}, ensure_ascii=False, indent=2))

if ARGS.apply:
    for path in (candidate_path, mention_path, statement_path, coverage_path):
        backup_path = path.with_name(path.name + BACKUP)
        if backup_path.exists():
            raise SystemExit(f"backup already exists: {backup_path}")
        shutil.copy2(path, backup_path)
    write_csv(candidate_path, candidate_fields, all_candidates)
    write_csv(mention_path, mention_fields, all_mentions)
    write_jsonl(statement_path, all_statements)
    write_csv(coverage_path, coverage_fields, all_coverage)
