#!/usr/bin/env python3
"""Controlled S2 migration for bibliography printed p. 426."""
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
SEGMENT = "chp-21:21_CHP-21Bibliography:l616-656"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
SEGMENT_SHA = "3e4902cb1cf3d1e384faf0b46780179511a5a86b7b6bccf0acdf3dac4c2b761d"
BACKUP = ".bak-s2-chp21-bibliography-l616-656-20261007"

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
segment_text = "\n".join(source_lines[615:656])
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
    11334,
    26359,
    11634,
    832,
):
    raise SystemExit("unexpected bibliography S2 pre-state")

candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}
if SEGMENT not in coverage_by_id or (
    coverage_by_id[SEGMENT]["disposition"],
    coverage_by_id[SEGMENT]["migration_status"],
) != ("queued", "pending"):
    raise SystemExit("bibliography segment is not queued")

# Page-image review of PDF physical p.16 / printed p.426 found 31 bibliography
# records and two author cross-reference entries. Line 631 fuses two records in S0.
#
# Existing citation candidates are refined only where author/year/page evidence
# identifies the same publication. Other short locators stay distinct for S3.
candidate_updates = [
    {
        "id": "cand-10154", "type": "archive",
        "expected": "Hofer, p. 37 (p.336 note 1 citation locator)",
        "name": "P. Hofer, Fragonard’s drawings for Ariosto (London, 1945)",
        "detail": "Printed p.426 identifies the p.336 note 1 locator ‘Hofer, p. 37’ with this 1945 London book. Its contents were not independently consulted; the author’s identity alignment remains for S3.",
    },
    {
        "id": "cand-6199", "type": "archive",
        "expected": "Hoogewerff (1913), cited publication, p. 50",
        "name": "G. J. Hoogewerff, Bescheiden en Italie omtrent Nederlandsche Kunstenaars en Geleerden (’s-Gravenhage, 1913)",
        "detail": "Printed p.426 supplies the title and edition details for the p.156 note citation to Hoogewerff (1913), p. 50. The cited page was not independently consulted; person-level alignment remains for S3.",
    },
    {
        "id": "cand-5142", "type": "archive",
        "expected": "Huetter e Golzio, cited publication; title unspecified",
        "name": "L. Huetter and V. Golzio, S. Vitale (Roma, n.d.)",
        "detail": "Printed p.426 identifies the S. Vitale publication cited in the p.67 note. The work was not independently consulted; author forms are transcribed from the bibliography and identity alignment remains for S3.",
    },
    {
        "id": "cand-9352", "type": "archive",
        "expected": "Hussey, 1955, p.43 (citation locator; work unresolved)",
        "name": "C. Hussey, English country houses—Early Georgian (London, 1955)",
        "detail": "Printed p.426 identifies the p.287 note 1 citation to Hussey (1955), p.43. The cited page was not independently consulted; author identity alignment remains for S3.",
    },
    {
        "id": "cand-7349", "type": "archive",
        "expected": "Ilg, work on Prince Eugene (Wien, 1889; title as transcribed in bibliography)",
        "name": "A. Ilg, Prinz Eugen von Savoyen als Kunstfreunde (Wien, 1889)",
        "detail": "Printed p.426 supplies the title for Ilg’s work cited at p.201 note 2. The cited work was not independently consulted; author identity alignment remains for S3.",
    },
    {
        "id": "cand-4564", "type": "archive",
        "expected": "Incisa della Rocchetta (1924), cited publication, pp. 60-76; title unspecified",
        "name": "G. Incisa della Rocchetta, ‘Notizie inedite su Andrea Sacchi’ (L’Arte, 1924, pp. 60–76)",
        "detail": "Printed p.426 identifies the 1924, pp.60–76 citation as this L’Arte article. The article was not independently consulted; global author alignment remains for S3.",
    },
    {
        "id": "cand-6379", "type": "archive",
        "expected": "Incisa della Rocchetta (1925), cited publication, pp.539–544; title unspecified",
        "name": "G. Incisa della Rocchetta, ‘Il museo di curiosità del Cardinale Flavio Chigi Seniore’ (Roma, 1925, III, pp. 539–544)",
        "detail": "Printed p.426 identifies the p.154 note citation, 1925, III, pp.539–544, as this article in Roma. The article was not independently consulted; global author alignment remains for S3.",
    },
    {
        "id": "cand-4850", "type": "archive",
        "expected": "Incisa della Rocchetta (1959), cited publication; title unspecified",
        "name": "G. Incisa della Rocchetta, ‘Tre quadri Barberini acquistati dal Museo di Roma’ (Bollettino dei Musei Comunali di Roma, 1959, pp. 20–37)",
        "detail": "Printed p.426 identifies the p.235 note citation to Incisa della Rocchetta (1959), pp.20 ff., as this article. The article was not independently consulted; global author alignment remains for S3.",
    },
    {
        "id": "cand-4581", "type": "archive",
        "expected": "Well-documented study by P. Domenico da Isnello; title unspecified",
        "name": "P. Domenico da Isnello, Il convento della Santissima Concezione de’ Padri Cappuccini in Piazza Barberini di Roma (Viterbo, 1923)",
        "detail": "Printed p.426 identifies the p.191 note’s ‘well-documented study’ by P. Domenico da Isnello. The book was not independently consulted.",
    },
    {
        "id": "cand-7256", "type": "archive",
        "expected": "Italian Art and Britain (publication cited at pp. 19–20; full details unspecified)",
        "name": "Italian Art and Britain (Royal Academy of Arts exhibition catalogue, London, 1960)",
        "detail": "Printed p.426 identifies the exhibition and venue details for the Italian Art and Britain item cited at pp.19–20; p.197 note 2 separately cites p.170. The catalogue contents were not independently consulted. The p.170 locator remains a separate S3 comparison candidate.",
    },
    {
        "id": "cand-11204", "type": "archive",
        "expected": "Konopleva publication cited at p.406 note 7 (title and year unspecified)",
        "name": "M. S. Konopleva, Teatralni Zhivopicets Giuseppe Valeriani (Leningrad, 1948)",
        "detail": "Printed p.426 identifies the p.406 note 7 citation to Konopleva. The work was not independently consulted; the author identity remains for S3.",
    },
    {
        "id": "cand-10212", "type": "archive",
        "expected": "Kurz, 1955, pp. 282–287 (short-form cited publication; title unresolved)",
        "name": "O. Kurz, ‘Engravings on Silver by Annibale Carracci’ (Burlington Magazine, 1955, pp. 282–287)",
        "detail": "Printed p.426 identifies the p.342 note 7 citation, 1955, pp.282–287, as this Burlington Magazine article. The article was not independently consulted; author identity alignment remains for S3.",
    },
]

natural_keys = {}
for row in candidates:
    if not row.get("index_entry_id") and row.get("suggested_type", "").strip():
        key = (row["canonical_name"].strip().casefold(), row["suggested_type"].strip().casefold())
        natural_keys.setdefault(key, set()).add(row["candidate_id"])

for update in candidate_updates:
    candidate = candidate_by_id.get(update["id"])
    if not candidate or candidate.get("suggested_type") != update["type"]:
        raise SystemExit(f"missing/wrong-type candidate: {update['id']}")
    if candidate["canonical_name"] != update["expected"]:
        raise SystemExit(f"candidate identity label changed: {update['id']}")
    old_key = (
        candidate["canonical_name"].strip().casefold(),
        candidate["suggested_type"].strip().casefold(),
    )
    new_key = (update["name"].strip().casefold(), candidate["suggested_type"].strip().casefold())
    collisions = natural_keys.get(new_key, set()) - {update["id"]}
    if collisions:
        raise SystemExit(f"candidate name collision {update['id']}: {sorted(collisions)}")
    natural_keys.get(old_key, set()).discard(update["id"])
    natural_keys.setdefault(new_key, set()).add(update["id"])
    candidate["canonical_name"] = update["name"]
    candidate["detail"] = update["detail"]

new_candidate_specs = [
    ("cand-11356", "G. J. Hoogewerff, ‘Il conflitto fra la insigne Accademia di S. Luca e la banda dei pittori neerlandesi’ (Archivio della Società Romana di Storia Patria, 1935, pp. 189–203)", "Printed p.426 lists this article; the bibliography citation does not establish that its contents were consulted.", 623),
    ("cand-11357", "G. J. Hoogewerff, Die Bentveughels (’s-Gravenhage, 1952)", "Printed p.426 lists this book; it was not independently consulted.", 624),
    ("cand-11358", "Isham, Sir Thomas—an English Collector in Rome (Northampton, 1969)", "Printed p.426 italicizes the full heading as the title and gives Northampton 1969. The author/title boundary is not explicit in the entry; no authorship is inferred.", 632),
    ("cand-11359", "Cristoforo Ivanovich, Minerva al Tavolino (Venezia, 1688)", "Printed p.426 lists this publication; its contents were not independently consulted.", 637),
    ("cand-11360", "M. Jaffé, ‘Peter Paul Rubens and the Oratorian fathers’ (Proporzioni, IV, 1961)", "Printed p.426 lists this article; its contents were not independently consulted. Keep distinct from the Irma Jaffé author heading and p.398 citation pending S3.", 639),
    ("cand-11361", "Richard Krautheimer and Roger Jones, ‘The Diary of Alexander VII: Notes on Art, Artists and Buildings’ (Römisches Jahrbuch für Kunstgeschischte, Band 15, 1975, pp. 199–233)", "Printed p.426 identifies the target of the Roger Jones ‘See’ pointer. The journal title is transcribed as printed in the page image; the article was not independently consulted.", 653),
    ("cand-11362", "E. Kauffmann, ‘At an eighteenth-century crossroads: Algarotti vs. Lodoli’ (Journal of American Society of Architectural Historians, 1944, pp. 23–29)", "Printed p.426 lists this article; the text was not independently consulted. The p.322 citation and author alignment remain for S3.", 642),
    ("cand-11363", "E. Kauffmann, ‘Piranesi, Algarotti and Lodoli (a controversy in XVIII century Venice)’ (Gazette des Beaux-Arts, 1955, II, pp. 21–28)", "Printed p.426 lists this article; the text was not independently consulted. Keep separate from the 1944 article and from the combined p.322 citation locator for S3.", 644),
    ("cand-11364", "J. G. Keysler, Travels through Germany, Bohemia, Hungary, Switzerland, Italy and Lorrain (2nd edition, 4 vols., London, 1757)", "Printed p.426 lists this four-volume second edition. Existing volume/page citation locators remain separate for S3.", 646),
    ("cand-11365", "W. Chandler Kirwin, ‘Addendum to Cardinal Francesco Maria del Monte’s Inventory: the Date of the Sale of Various Notable Paintings’ (Storia dell’Arte, 1971, pp. 53–56)", "Printed p.426 lists this article; its contents were not independently consulted. The generic p.397 Kirwin publication candidate remains separate for S3.", 649),
    ("cand-11366", "G. Knox, Tiepolo drawings in the Victoria and Albert Museum (London, 1960)", "Printed p.426 lists this book; its contents were not independently consulted. The p.354 note locator remains separate for S3.", 651),
    ("cand-11367", "Joseph Jérôme le Français de Lalande, Voyage en Italie (seconde édition, 7 vols., Yverdon, 1787)", "Printed p.426 lists this seven-volume second edition; its contents were not independently consulted.", 655),
    ("cand-11368", "R. Wittkower and Irma Jaffe (eds.), Baroque Art: The Jesuit Contribution (New York, 1972)", "Created as the target for the Jaffé, Irma author cross-reference on printed p.426. The cited S0 line L1276 spells Jaffe without an accent; full page-image review and the bibliography-list statement remain queued for segment L1261–1299.", 1276),
]

new_candidates = []
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
        # Keep the candidate's primary source anchor inside reviewed coverage.
        # The target line is retained in its detail and cross-reference statement
        # until segment L1261-1299 receives its full page-image review.
        candidate_source_ref=f"{SEGMENT}#L{source_line if source_line <= 656 else 638}",
    )
    new_candidates.append(row)
    candidate_by_id[candidate_id] = row
    natural_keys.setdefault(key, set()).add(candidate_id)

entries = [
    {"candidate_id":"cand-10154","start":617,"end":617,"author":"Hofer, P.","title":"Fragonard’s drawings for Ariosto","details":"London 1945","kind":"book","related":["cand-10153"]},
    {"candidate_id":"cand-7250","start":618,"end":618,"author":"Holst, Niels von","title":"La pittura veneziana tra il Reno e la Neva","details":"Arte Veneta, 1951, pp. 131–140","kind":"journal article"},
    {"candidate_id":"cand-7260","start":619,"end":619,"author":"Honour, H.","title":"English patrons and Italian sculptors in the first half of the eighteenth century","details":"Connoisseur, 1958, vol. 141, pp. 220–226","kind":"journal article","corrections":[{"line":619,"ocr":"195 8","print":"1958"}]},
    {"candidate_id":"cand-7095","start":620,"end":620,"author":"Hoog, M.","title":"Attributions anciennes à Valentin","details":"Revue des Arts, 1960, pp. 267–278","kind":"journal article","related":["cand-7094"],"corrections":[{"line":620,"ocr":"i960","print":"1960"}]},
    {"candidate_id":"cand-6199","start":621,"end":622,"author":"Hoogewerff, G. J.","title":"Bescheiden en Italie omtrent Nederlandsche Kunstenaars en Geleerden","details":"’s-Gravenhage 1913","kind":"book","related":["cand-3522"],"corrections":[{"line":621,"ocr":"omirent","print":"omtrent"}]},
    {"candidate_id":"cand-11356","start":623,"end":623,"author":"Hoogewerff, G. J.","title":"Il conflitto fra la insigne Accademia di S. Luca e la banda dei pittori neerlandesi","details":"Archivio della Società Romana di Storia Patria, 1935, pp. 189–203","kind":"journal article","related":["cand-3522"],"corrections":[{"line":623,"ocr":"193 5","print":"1935"},{"line":623,"ocr":"ppr","print":"pp."}]},
    {"candidate_id":"cand-11357","start":624,"end":624,"author":"Hoogewerff, G. J.","title":"Die Bentveughels","details":"’s-Gravenhage 1952","kind":"book","related":["cand-3522"]},
    {"candidate_id":"cand-5142","start":625,"end":625,"author":"Huetter, L. e Golzio, V.","title":"S. Vitale","details":"Roma n.d.","kind":"book"},
    {"candidate_id":"cand-7871","start":626,"end":626,"author":"Hugford, Ignazio Enrico","title":"Vita di Anton Domenico Gabbiani pittor fiorentino","details":"Firenze 1762","kind":"book"},
    {"candidate_id":"cand-9352","start":627,"end":627,"author":"Hussey, C.","title":"English country houses—Early Georgian","details":"London 1955","kind":"book","related":["cand-9351"]},
    {"candidate_id":"cand-7349","start":628,"end":628,"author":"Ilg, A.","title":"Prinz Eugen von Savoyen als Kunstfreunde","details":"Wien 1889","kind":"book"},
    {"candidate_id":"cand-4564","start":629,"end":629,"author":"Incisa della Rocchetta, G.","title":"Notizie inedite su Andrea Sacchi","details":"L’Arte, 1924, pp. 60–76","kind":"journal article","related":["cand-3498"]},
    {"candidate_id":"cand-6379","start":630,"end":631,"author":"Incisa della Rocchetta, G.","title":"Il museo di curiosità del Cardinale Flavio Chigi Seniore","details":"Roma, 1925, III, pp. 539–544","kind":"journal article","related":["cand-3498"],"corrections":[{"line":631,"ocr":"539'544","print":"539–544."},{"line":631,"ocr":"544Incisa della Rocchetta","print":"544. [entry break] Incisa della Rocchetta"}]},
    {"candidate_id":"cand-4850","start":631,"end":631,"author":"Incisa della Rocchetta, G.","title":"Tre quadri Barberini acquistati dal Museo di Roma","details":"Bollettino dei Musei Comunali di Roma, 1959, pp. 20–37","kind":"journal article","related":["cand-3498"]},
    {"candidate_id":"cand-11358","start":632,"end":632,"author":"","title":"Isham, Sir Thomas—an English Collector in Rome","details":"Northampton 1969","kind":"exhibition catalogue or monograph; author/title boundary unclear","related":["cand-1315"],"page_image_notes":["The entire heading is italicized. The entry does not distinguish an author from a subject heading; authorship is left unassigned."]},
    {"candidate_id":"cand-4581","start":633,"end":634,"author":"Isnello, P. Domenico da","title":"Il convento della Santissima Concezione de’ Padri Cappuccini in Piazza Barberini di Roma","details":"Viterbo 1923","kind":"book","related":["cand-4536"]},
    {"candidate_id":"cand-7256","start":635,"end":635,"author":"","title":"Italian Art and Britain","details":"Exhibition at Royal Academy of Arts, London 1960","kind":"exhibition catalogue","related":["cand-8807"],"corrections":[{"line":635,"ocr":"i960","print":"1960"}]},
    {"candidate_id":"cand-8265","start":636,"end":636,"author":"Ivanov, N.","title":"Una postilla tiepolesca","details":"Ateneo Veneto, 1951, pp. 1–3","kind":"journal article","related":["cand-8264"]},
    {"candidate_id":"cand-11359","start":637,"end":637,"author":"Ivanovich, Cristoforo","title":"Minerva al Tavolino","details":"Venezia 1688","kind":"book"},
    {"candidate_id":"cand-11360","start":639,"end":639,"author":"Jaffé, M.","title":"Peter Paul Rubens and the Oratorian fathers","details":"Proporzioni, IV, 1961","kind":"journal article"},
    {"candidate_id":"cand-7870","start":640,"end":640,"author":"Jahn-Rusconi, A.","title":"La R. Galleria Pitti in Firenze","details":"Roma 1937","kind":"book"},
    {"candidate_id":"cand-11362","start":642,"end":643,"author":"Kauffmann, E.","title":"At an eighteenth-century crossroads: Algarotti vs. Lodoli","details":"Journal of American Society of Architectural Historians, 1944, pp. 23–29","kind":"journal article","related":["cand-9960","cand-9961"]},
    {"candidate_id":"cand-11363","start":644,"end":645,"author":"Kauffmann, E.","title":"Piranesi, Algarotti and Lodoli (a controversy in XVIII century Venice)","details":"Gazette des Beaux-Arts, 1955, II, pp. 21–28","kind":"journal article","related":["cand-9960","cand-9961"]},
    {"candidate_id":"cand-11364","start":646,"end":647,"author":"Keysler, J. G.","title":"Travels through Germany, Bohemia, Hungary, Switzerland, Italy and Lorrain","details":"2nd edition, 4 vols., London 1757","kind":"four-volume book set","related":["cand-8578","cand-8579","cand-9883"]},
    {"candidate_id":"cand-9567","start":648,"end":648,"author":"","title":"King’s Pictures","details":"Exhibition at Royal Academy of Arts, London 1946–7","kind":"exhibition record","predicate":"bibliography_lists_event","related":["cand-9566"]},
    {"candidate_id":"cand-11365","start":649,"end":650,"author":"Kirwin, W. Chandler","title":"Addendum to Cardinal Francesco Maria del Monte’s Inventory: the Date of the Sale of Various Notable Paintings","details":"Storia dell’Arte, 1971, pp. 53–56","kind":"journal article","related":["cand-10879","cand-10880"]},
    {"candidate_id":"cand-11366","start":651,"end":651,"author":"Knox, G.","title":"Tiepolo drawings in the Victoria and Albert Museum","details":"London 1960","kind":"book","related":["cand-10301"]},
    {"candidate_id":"cand-11204","start":652,"end":652,"author":"Konopleva, M. S.","title":"Teatralni Zhivopicets Giuseppe Valeriani","details":"Leningrad 1948","kind":"book","related":["cand-11203"]},
    {"candidate_id":"cand-11361","start":653,"end":653,"author":"Krautheimer, Richard and Jones, Roger","title":"The Diary of Alexander VII: Notes on Art, Artists and Buildings","details":"Römisches Jahrbuch für Kunstgeschischte, Band 15, 1975, pp. 199–233","kind":"journal article","related":["cand-11176","cand-11177"],"corrections":[{"line":653,"ocr":"23 3","print":"233"}]},
    {"candidate_id":"cand-10212","start":654,"end":654,"author":"Kurz, O.","title":"Engravings on Silver by Annibale Carracci","details":"Burlington Magazine, 1955, pp. 282–287","kind":"journal article","related":["cand-10211"]},
    {"candidate_id":"cand-11367","start":655,"end":656,"author":"Lalande, Joseph Jérôme le Français de","title":"Voyage en Italie","details":"seconde édition, 7 vols., Yverdon 1787","kind":"seven-volume book set"},
]

line_631 = source_lines[630]
second_incisa = line_631.find("Incisa della Rocchetta, G.: ‘Tre quadri Barberini")
if second_incisa <= 0:
    raise SystemExit("could not locate fused Incisa entry boundary in S0 L631")
entries[12]["quote_override"] = source_lines[629] + "\n" + line_631[:second_incisa]
entries[13]["quote_override"] = line_631[second_incisa:]
entries[13]["page_image_notes"] = [
    "S0 joins this entry to the preceding 1925 Roma article on the same line; the page image confirms a distinct record boundary and independent page range."
]
entries[28]["page_image_notes"] = [
    "The journal title is retained in the page-image spelling; the 1975 page range reads 199–233."
]

cross_references = [
    {
        "statement_id": "st-chp21-bib-l616-656-xref-jaffe-irma",
        "line": 638,
        "subject_id": "cand-11159",
        "object_id": "cand-11368",
        "target_line": 1276,
        "target_segment": "chp-21:21_CHP-21Bibliography:l1261-1299",
        "target_status": "queued; bibliography-list statement pending",
        "claim": "Haskell’s bibliography redirects the heading ‘Jaffé, Irma’ to ‘Wittkower and Jaffé’.",
        "note": "The target title and publication data are taken from S0 L1276–1277 solely to resolve this printed See pointer. Full page-image review and its bibliography-list statement remain for the later queued segment; no external identity alignment is asserted.",
        "corrections": [{"line": 638, "ocr": ".See", "print": "See"}],
    },
    {
        "statement_id": "st-chp21-bib-l616-656-xref-jones-roger",
        "line": 641,
        "subject_id": "cand-11177",
        "object_id": "cand-11361",
        "target_line": 653,
        "target_segment": SEGMENT,
        "target_status": "reviewed in this segment",
        "claim": "Haskell’s bibliography redirects the heading ‘Jones, Roger’ to the joint Krautheimer and Jones publication on the same page.",
        "note": "This records the printed bibliography pointer and target only; external identity alignment and any formal relationship remain for S3/S6.",
        "page_image_notes": ["The page image confirms that the trailing OCR apostrophe and dash are detached scan marks, not part of the See pointer."],
    },
]

covered_lines = {line for entry in entries for line in range(entry["start"], entry["end"] + 1)}
covered_lines.update(ref["line"] for ref in cross_references)
if covered_lines != set(range(617, 657)):
    raise SystemExit(f"bibliography line coverage incomplete: missing={sorted(set(range(617,657))-covered_lines)}")
if len(entries) != 31 or len(cross_references) != 2:
    raise SystemExit("unexpected page bibliography record count")

mention_keys = {
    (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"]))
    for row in mentions
}
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
    return entry.get("quote_override") or "\n".join(
        source_lines[entry["start"] - 1:entry["end"]]
    )


def add_mention(candidate_id, surface, note):
    positions = [index for index in range(len(segment_text)) if segment_text.startswith(surface, index)]
    if len(positions) != 1:
        raise SystemExit(f"mention span text absent or ambiguous for {candidate_id}: {surface!r}")
    position = positions[0]
    end = position + len(surface)
    key = (SEGMENT, candidate_id, str(position), str(end))
    if key in mention_keys:
        raise SystemExit(f"duplicate mention natural key: {candidate_id} {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update(
        mention_id=f"m-chp21-bib-l616-656-{len(new_mentions) + 1:03d}",
        segment_id=SEGMENT,
        candidate_id=candidate_id,
        surface_form=surface,
        start_char=position,
        end_char=end,
        note=note,
    )
    new_mentions.append(row)
    mention_keys.add(key)


def add_statement(statement_id, claim, quote, start, end, object_id, predicate, qualifiers):
    if statement_id in statement_ids:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    claim_key = (SEGMENT, " ".join(claim.split()).casefold())
    if claim_key in existing_claim_keys:
        raise SystemExit(f"duplicate statement claim: {claim}")
    statement_ids.add(statement_id)
    existing_claim_keys.add(claim_key)
    row = {
        "statement_id": statement_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": qualifiers.pop("_subject_candidate_id", None),
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": start,
            "source_line_end": end,
            "claim": claim,
            "speaker": "Haskell’s bibliography",
            "relation_candidate": False,
            "mentioned_candidate_ids": qualifiers.pop("_mentioned_candidate_ids", [object_id]),
            **qualifiers,
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
    }
    if not quote or quote not in "\n".join(source_lines[start - 1:end]):
        raise SystemExit(f"statement quote/line validation failed: {statement_id}")
    new_statements.append(row)


for index, entry in enumerate(entries, start=1):
    candidate_id = entry["candidate_id"]
    candidate = candidate_by_id.get(candidate_id)
    expected_type = "event" if entry.get("predicate") == "bibliography_lists_event" else "archive"
    if not candidate or candidate.get("suggested_type") != expected_type:
        raise SystemExit(f"missing/wrong-type bibliographic candidate: {candidate_id}")
    quote = source_quote(entry)
    related = entry.get("related", [])
    for related_id in related:
        if related_id not in candidate_by_id:
            raise SystemExit(f"related candidate FK missing: {candidate_id}: {related_id}")
    add_mention(
        candidate_id,
        quote,
        "S0 bibliography entry; page-image OCR corrections, scan notes, and S3 candidate comparisons are recorded on its statement.",
    )
    qualifiers = {
        "text_layer": "bibliographic entry" if expected_type == "archive" else "exhibition entry",
        "qualification": "This records the bibliography entry only; the cited publication or event was not independently consulted in this S2 pass.",
        "bibliographic_record": {
            "author_as_printed": entry["author"],
            "title_as_printed": entry["title"],
            "publication_details_as_printed": entry["details"],
            "record_kind": entry["kind"],
            "printed_page": 426,
        },
    }
    if entry.get("corrections"):
        qualifiers["page_image_ocr_corrections"] = entry["corrections"]
    if entry.get("page_image_notes"):
        qualifiers["page_image_notes"] = entry["page_image_notes"]
    if related:
        qualifiers["related_candidate_ids_for_s3"] = related
    if entry.get("predicate") == "bibliography_lists_event":
        qualifiers["qualification"] = "The page lists the exhibition event; this statement does not claim a separately identified catalogue publication."
    claim = f"Haskell lists {entry['title']} in the bibliography."
    add_statement(
        f"st-chp21-bib-l616-656-entry-{index:02d}",
        claim,
        quote,
        entry["start"],
        entry["end"],
        candidate_id,
        entry.get("predicate", "bibliography_lists_publication"),
        qualifiers,
    )

for ref in cross_references:
    subject_id = ref["subject_id"]
    object_id = ref["object_id"]
    if subject_id not in candidate_by_id or object_id not in candidate_by_id:
        raise SystemExit(f"cross-reference candidate FK missing: {subject_id} -> {object_id}")
    quote = source_lines[ref["line"] - 1]
    add_mention(
        subject_id,
        quote,
        "Printed bibliography author cross-reference; target and deferred identity status are recorded on the statement.",
    )
    qualifiers = {
        "text_layer": "author cross-reference",
        "qualification": ref["note"],
        "cross_reference_type": "see",
        "target_source_line": ref["target_line"],
        "target_segment_id": ref["target_segment"],
        "target_source_line_status": ref["target_status"],
        "related_candidate_ids_for_s3": [subject_id, object_id],
        "_subject_candidate_id": subject_id,
        "_mentioned_candidate_ids": [subject_id],
    }
    if ref.get("corrections"):
        qualifiers["page_image_ocr_corrections"] = ref["corrections"]
    if ref.get("page_image_notes"):
        qualifiers["page_image_notes"] = ref["page_image_notes"]
    add_statement(
        ref["statement_id"],
        ref["claim"],
        quote,
        ref["line"],
        ref["line"],
        object_id,
        "bibliography_author_cross_reference",
        qualifiers,
    )

if len(new_candidates) != 13 or len(new_mentions) != 33 or len(new_statements) != 33:
    raise SystemExit("unexpected migration row counts")
if [row["candidate_id"] for row in new_candidates] != [f"cand-{i}" for i in range(11356, 11369)]:
    raise SystemExit("new candidate IDs are not the expected next sequence")

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

coverage_by_id[SEGMENT]["disposition"] = "reviewed"
coverage_by_id[SEGMENT]["migration_status"] = "complete"
coverage_by_id[SEGMENT]["source_line_ranges"] = "L617-656"
coverage_by_id[SEGMENT]["note"] = (
    "Printed p.426 contains 31 bibliography entries (30 publication/catalogue records and one exhibition listing) plus two author See pointers; the [Page 426] marker is not a record. Reused 19 existing candidates and added 12 for this page. A thirteenth archive candidate was created as the target of the Jaffé, Irma pointer using S0 L1276; its full segment review remains queued. The fused Incisa entries at L631 have disjoint mention spans. Page-image OCR readings are recorded in statements; cited contents were not independently consulted. Short-form cross-chapter candidates remain separate for S3."
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
    "xref_targets": {ref["statement_id"]: ref["object_id"] for ref in cross_references},
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
