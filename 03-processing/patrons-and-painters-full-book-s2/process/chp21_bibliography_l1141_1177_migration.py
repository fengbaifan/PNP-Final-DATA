#!/usr/bin/env python3
"""Controlled S2 migration for bibliography printed p. 438."""

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
SOURCE_FILE = "02-sources/02-Markdown/21_CHP-21Bibliography.md"
SEGMENT = "chp-21:21_CHP-21Bibliography:l1141-1177"
SEGMENT_SHA = "002ac07d49d47f3731c111b94ff873c42aa88d5a2be640ee17c18efddda3dced"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
PREVIOUS_SEGMENT = "chp-21:21_CHP-21Bibliography:l1102-1139"
BACKUP_SUFFIX = ".bak-s2-chp21-bibliography-l1141-1177-20261007"

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


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if sha256(SOURCE) != SOURCE_SHA or sha256(PDF) != PDF_SHA:
    raise SystemExit("bibliography Markdown or PDF changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[1140:1177])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 segment text/hash changed")

segment_rows = {row["segment_id"]: row for row in read_jsonl(TABLES / "segments.jsonl")}
segment_row = segment_rows.get(SEGMENT)
if not segment_row or (
    segment_row.get("source_file"),
    segment_row.get("line_start"),
    segment_row.get("line_end"),
    segment_row.get("sha256"),
    segment_row.get("asset_sha256"),
) != (SOURCE_FILE, 1141, 1177, SEGMENT_SHA, SOURCE_SHA):
    raise SystemExit("source segment manifest changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage = read_csv(coverage_path)
statements = read_jsonl(statement_path)

if (len(candidates), len(mentions), len(statements), len(coverage)) != (
    11415,
    26712,
    11985,
    832,
):
    raise SystemExit("unexpected bibliography S2 pre-state")

candidate_by_id = {row["candidate_id"]: row for row in candidates}
coverage_by_id = {row["segment_id"]: row for row in coverage}
coverage_row = coverage_by_id.get(SEGMENT)
if not coverage_row or (coverage_row["disposition"], coverage_row["migration_status"]) != (
    "queued",
    "pending",
):
    raise SystemExit("bibliography segment is not queued")
previous_coverage = coverage_by_id.get(PREVIOUS_SEGMENT)
if not previous_coverage or (
    previous_coverage["disposition"],
    previous_coverage["migration_status"],
) != ("reviewed", "complete"):
    raise SystemExit("previous bibliography segment is not complete")

candidate_updates = [
    {
        "id": "cand-5467", "type": "archive",
        "expected": "Tacchi-Venturi (1935), cited publication, pp.147-156",
        "name": "P. Tacchi-Venturi, ‘Le convenzioni tra Giov. Battista Gaulli e il Generale dei Gesuiti’ (Roma, 1935, pp. 147–156)",
        "detail": "Printed p.438 supplies the title and full locator for the p.80 note 3/note 6 Tacchi-Venturi citation. It appears to match the prior p.147–156 and p.154–155 references; neither the article nor cited pages was independently consulted.",
    },
    {
        "id": "cand-5492", "type": "archive",
        "expected": "Tacchi-Venturi, La casa di S. Ignazio in Roma (undated)",
        "name": "P. Tacchi-Venturi, La casa di S. Ignazio di Loiola in Roma (Roma, n.d.)",
        "detail": "Printed p.438 confirms the full printed title and Roma n.d. details for the p.89 note 1 citation. The work and cited material were not independently consulted; preserve the printed Loiola spelling.",
    },
    {
        "id": "cand-5834", "type": "archive",
        "expected": "1886 publication of Jean-Jacques Bouchard’s will by Tamizey de Laroque (title unresolved)",
        "name": "P. Tamizey de Larroque, ‘Deux testaments inédits’ (Bulletin Critique, 15 Mai 1886)",
        "detail": "Printed p.438 supplies an 1886 Tamizey de Larroque article citation that is a possible match for the p.265 report about Bouchard’s will. The title suggests but does not prove that mapping; compare in S3. The article and testaments were not consulted.",
    },
    {
        "id": "cand-6590", "type": "archive",
        "expected": "Tassi, Vite de’ Pittori... vol. II p.60",
        "name": "F. M. Tassi, Vite de’ Pittori, Scultori e Architetti Bergamaschi (Bergamo, 1793)",
        "detail": "Printed p.438 supplies the full title, place, and year for the existing volume-II p.60/p.64 citation candidate. The separate volume-I p.265 locator cand-7690 is retained for S3 comparison; cited pages were not consulted.",
    },
    {
        "id": "cand-8428", "type": "archive",
        "expected": "Tassini, 1915, page 335 (citation locator)",
        "name": "G. Tassini, Curiosità Veneziane (5a edizione, Venezia, 1915)",
        "detail": "Printed p.438 identifies the fifth edition corresponding to the p.257 note 2, p.335 locator. Keep distinct from the separately cited fourth edition of 1887 (cand-10687); neither edition nor cited page was independently consulted.",
    },
    {
        "id": "cand-9957", "type": "archive",
        "expected": "Temanza, page 87 (citation locator)",
        "name": "T. Temanza, Vite dei più celebri architetti, e scultori veneziani (Venezia, 1778)",
        "detail": "Printed p.438 supplies the title and publication details for the p.320–323 page-87 Temanza locator. The cited page and book were not independently consulted.",
    },
    {
        "id": "cand-8799", "type": "archive",
        "expected": "Tentori, volume X, p.288 (citation locator; title pending)",
        "name": "Abbate D. Cristoforo Tentori, Saggio sulla storia civile, politica, ecclesiastica e sulla corografia e topografia degli stati della repubblica di Venezia (12 vols., Venezia, 1785–90)",
        "detail": "Printed p.438 supplies the twelve-volume title set and dates for the p.271 note 4, vol. X, p.288 locator. Neither the set nor cited page was independently consulted.",
    },
    {
        "id": "cand-4569", "type": "archive",
        "expected": "Alfred de Terrebasse, cited publication, p. 40; title unspecified",
        "name": "Alfred de Terrebasse, Relation des principaux événements de la vie de Salvaing de Boissieu (Lyon, 1850)",
        "detail": "Printed p.438 supplies the title and Lyon 1850 details for the earlier p.2 p.40 citation. The work and cited page were not independently consulted.",
    },
    {
        "id": "cand-10392", "type": "archive",
        "expected": "Introduction to Raccolta di disegni originali di Mauro Tesi (citation in p.358 n.3)",
        "name": "Mauro Tesi, Raccolta di disegni originali estratti da diverse collezioni pubblicata da Lodovico Inig calcografo in Bologna—aggiuntavi la vita dell’autore (Bologna, [1787])",
        "detail": "Printed p.438 gives the full title and bracketed date for the p.358 note 3 introduction reference. The page image appears to read Inig; retain that printed form without conjectural correction. The collection and introduction were not independently consulted; compare the precise object boundary in S3.",
    },
    {
        "id": "cand-4837", "type": "archive",
        "expected": "J. Thuillier (1958), cited publication; title unspecified",
        "name": "J. Thuillier, ‘Un peintre passionné’ (L’Œil, no. 47, November 1958, pp. 26–33)",
        "detail": "Printed p.438 supplies the article title, journal, issue, month, and pages for the p.219 note 2 reference to the picture’s 1958 publication. The article and cited page were not independently consulted.",
    },
    {
        "id": "cand-5805", "type": "archive",
        "expected": "Thuillier 1960 source in Actes du Colloque Poussin, volume II, page 210",
        "name": "J. Thuillier, ‘Pour un “Corpus Poussinianum”’ in Actes du Colloque Poussin (1960, vol. II, pp. 49–238)",
        "detail": "Printed p.438 supplies the article title and full proceedings page range for the p.257 citation at vol. II, p.210. The cited page and proceedings were not independently consulted; this identifies the publication record, not the reported quotation’s accuracy.",
    },
    {
        "id": "cand-8792", "type": "archive",
        "expected": "Mostra del Tiepolo, 1951, p.8 (citation locator)",
        "name": "Tiepolo—catalogo della mostra a cura di Giulio Lorenzetti (Venezia, 1951)",
        "detail": "Printed p.438 supplies the catalogue title and curator for the p.270 note 3 p.8 citation. The exhibition publication and cited page were not independently consulted.",
    },
    {
        "id": "cand-7350", "type": "archive",
        "expected": "H. Tietze, article on Prince Eugene, pp. 891-907 (1933; title as transcribed in bibliography)",
        "name": "H. Tietze, ‘Eugenio di Savoia amico dell’arte’ (Le Vie d’Italia e del Mondo, 1933, pp. 891–907)",
        "detail": "Printed p.438 confirms the title, periodical, year, and pp.891–907 locator for the p.201 note 2 Tietze citation. The article and cited pages were not independently consulted.",
    },
    {
        "id": "cand-10451", "type": "archive",
        "expected": "De Tipaldo (1833), cited in p.363 note 1",
        "name": "Emilio de Tipaldo, Descrizione della deliziosa villa di Sala di proprietà del signor Demetrio Mircovich (Venezia, 1833)",
        "detail": "Printed p.438 supplies the title and place/year for the p.363 note 1 De Tipaldo citation. Keep distinct from the separately listed multi-volume Biografia entry on this page; neither publication was independently consulted.",
    },
    {
        "id": "cand-9346", "type": "archive",
        "expected": "Ilaria Toesca, 1952, p.208 (citation locator in p.286 note 1; work unresolved)",
        "name": "L. Toesca, ‘Alessandro Galilei in Inghilterra’ (English Miscellany, Roma, 1952, pp. 189–220)",
        "detail": "Printed p.438 supplies the title and page range containing the p.286 note 1 p.208 locator. The bibliography prints L. Toesca, while the earlier footnote names Ilaria Toesca; the article match is likely but author identity remains for S3 with cand-4332 and cand-9345. The cited page was not consulted.",
    },
    {
        "id": "cand-4333", "type": "archive",
        "expected": "Note sulla storia del Palazzo Giustiniani a San Luigi dei Francesi (Toesca, 1957)",
        "name": "L. Toesca, ‘Note sulla storia del Palazzo Giustiniani a San Luigi dei Francesi’ (Bollettino d’Arte, 1957, pp. 296–308)",
        "detail": "Printed p.438 confirms the title, journal, year, and page range for the p.96 chapter-2 Toesca citation. The article was not independently consulted; the author initial remains as printed and is not expanded.",
    },
    {
        "id": "cand-10476", "type": "archive",
        "expected": "Torcellan, 1963, biographical source on Andrea Memmo (p.364 note 4 citation locator)",
        "name": "Gianfranco Torcellan, Una figura della Venezia settecentesca: Andrea Memmo (Venezia–Roma, 1963)",
        "detail": "Printed p.438 supplies the title and publication places for the p.364/p.367 Torcellan 1963 biography citation. The book and cited material were not independently consulted.",
    },
    {
        "id": "cand-11110", "type": "archive",
        "expected": "Gianfranco Torcellan's 1969 publication cited on the Venetian Enlightenment",
        "name": "Gianfranco Torcellan, Settecento veneto e altri scritti storici (Torino, 1969)",
        "detail": "Printed p.438 supplies the title and Torino 1969 details for the p.408 Torcellan reference. This identifies the bibliography record only; the book and any cited passages were not independently consulted.",
    },
    {
        "id": "cand-5801", "type": "archive",
        "expected": "Kate Trauman-Steinitz 1953 publication on Poussin and Leonardo",
        "name": "K. Trauman-Steinitz, ‘Poussin illustiator of Leonardo da Vinci’ (Art Quarterly, Spring 1953, pp. 40–55)",
        "detail": "Printed p.438 supplies the complete article locator for the p.259 citation. The printed title spells illustiator; preserve this apparent print error rather than silently correcting it. The article and cited pages were not independently consulted.",
    },
    {
        "id": "cand-9303", "type": "archive",
        "expected": "Turberville, vol. II, p.14 (citation locator; work and edition unresolved)",
        "name": "A. S. Turberville, A history of Welbeck Abbey and its owners (London, 1939)",
        "detail": "Printed p.438 supplies the title, author initials, place, and year for the p.280 note 2 vol. II, p.14 locator. The cited volume and page were not independently consulted.",
    },
    {
        "id": "cand-5833", "type": "person",
        "expected": "Tamizey de Laroque",
        "detail": "The p.438 bibliography prints the author form P. Tamizey de Larroque for the 1886 article that may match the p.265 Bouchard-will citation. This supplies a source form only; retain identity and exact citation mapping for S3.",
    },
]

for update in candidate_updates:
    row = candidate_by_id.get(update["id"])
    if not row or row.get("suggested_type") != update["type"]:
        raise SystemExit(f"missing/wrong-type candidate update: {update['id']}")
    if row.get("canonical_name") != update["expected"]:
        raise SystemExit(f"candidate pre-state changed: {update['id']}")
    if "name" in update:
        row["canonical_name"] = update["name"]
    row["detail"] = update["detail"]

new_candidate_specs = [
    {
        "id": "cand-11437",
        "name": "G. de Tervarent, Attributs et symboles dans l’art profane 1450–1600 (Genève, 1959)",
        "detail": "Bibliography entry at printed p.438. This work was not independently consulted; author identity is not expanded beyond the printed initial.",
        "source_line": 1155,
    },
    {
        "id": "cand-11438",
        "name": "Girolamo Teti, Aedes Barberinae ad Quirinalem a comite Hieronymo Tetio Persino descriptae (Romae, MDCXLII)",
        "detail": "Bibliography entry at printed p.438. The title, author form, and date are transcribed from the page; the work was not independently consulted. Compare with index person candidate cand-2561 at S3.",
        "source_line": 1158,
    },
    {
        "id": "cand-11439",
        "name": "Emilio de Tipaldo, Biografia degli Italiani illustri nelle scienze, lettere ed arti del secolo XVIII, e de’ contemporanei (10 vols., Venezia, 1834–45)",
        "detail": "Bibliography entry at printed p.438. This is a separate ten-volume work from de Tipaldo’s 1833 villa publication; neither work was independently consulted.",
        "source_line": 1167,
    },
    {
        "id": "cand-11440",
        "name": "L. Treat, Un cosmopolite italien du XVIIIème siècle—Francesco Algarotti (Trévoux, 1913)",
        "detail": "Bibliography entry at printed p.438. The book was not independently consulted; author identity is retained as the printed initial and surname.",
        "source_line": 1174,
    },
    {
        "id": "cand-11441",
        "name": "Nicholas Turner, ‘Ferrante Carlo’s Descrittione della Cupola di S. Andrea della Valle depinta dal Cavalier Gio: Lanfranchi; a source for Bellori’s descriptive method’ (Storia dell’Arte, 1971, pp. 297–325)",
        "detail": "Bibliography entry at printed p.438. The article was not independently consulted; its title is preserved as printed, including the historical Descrittione spelling.",
        "source_line": 1176,
    },
]

natural_keys = {}
for row in candidates:
    key = (row["canonical_name"].strip().casefold(), row["suggested_type"])
    natural_keys.setdefault(key, set()).add(row["candidate_id"])
new_candidates = []
for spec in new_candidate_specs:
    if spec["id"] in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {spec['id']}")
    key = (spec["name"].strip().casefold(), "archive")
    if natural_keys.get(key):
        raise SystemExit(f"candidate natural-key collision: {spec['id']}")
    row = {field: "" for field in candidate_fields}
    row.update(
        candidate_id=spec["id"],
        canonical_name=spec["name"],
        suggested_type="archive",
        status="open",
        detail=spec["detail"],
        candidate_origin="body-mention",
        candidate_source_ref=f"{SEGMENT}#L{spec['source_line']}",
    )
    new_candidates.append(row)
    candidate_by_id[spec["id"]] = row
    natural_keys.setdefault(key, set()).add(spec["id"])


def record(candidate_id, start, end, author, title, details, kind, *, corrections=None, notes=None, related=None, quote=None, shared_line=False):
    return {
        "candidate_id": candidate_id,
        "start": start,
        "end": end,
        "author": author,
        "title": title,
        "details": details,
        "kind": kind,
        "corrections": corrections or [],
        "page_image_notes": notes or [],
        "related": related or [],
        "quote": quote,
        "shared_line": shared_line,
    }


line_1158 = source_lines[1157]
tessier_quote, separator, teti_tail = line_1158.partition("Teti, Girolamo:")
if not separator or not tessier_quote.endswith("289315") or not teti_tail:
    raise SystemExit("the merged OCR line 1158 has changed")
teti_quote = "Teti, Girolamo:" + teti_tail

entries = [
    record("cand-5467", 1142, 1143, "P. Tacchi-Venturi", "‘Le convenzioni tra Giov. Battista Gaulli e il Generale dei Gesuiti’", "Roma, 1935, pp. 147–156", "journal article", related=["cand-3513"]),
    record("cand-5492", 1144, 1144, "P. Tacchi-Venturi", "La casa di S. Ignazio di Loiola in Roma", "Roma n.d.", "book", related=["cand-3513"]),
    record("cand-5834", 1145, 1145, "P. Tamizey de Larroque", "‘Deux testaments inédits’", "Bulletin Critique, 15 Mai 1886", "journal article", notes=["Possible match to the p.265 report about Bouchard’s will; exact mapping remains for S3."], related=["cand-5833"]),
    record("cand-7023", 1146, 1146, "V. L. Tapié", "La France de Louis XIII et de Richelieu", "Paris 1952", "book"),
    record("cand-6590", 1147, 1147, "F. M. Tassi", "Vite de’ Pittori, Scultori e Architetti Bergamaschi", "Bergamo 1793", "book", notes=["Existing volume-II locators are cited separately from the volume-I p.265 candidate; compare their identity in S3."], related=["cand-7690"]),
    record("cand-8428", 1148, 1148, "G. Tassini", "Curiosità Veneziane", "5a edizione, Venezia 1915", "book/guide", notes=["This is the fifth edition and remains distinct from the fourth edition cand-10687 (1887)."], related=["cand-10687"]),
    record("cand-7089", 1149, 1150, "F. H. Taylor", "The taste of angels—a history of art collecting from Rameses to Napoleon", "Boston 1948", "book"),
    record("cand-9957", 1151, 1151, "T. Temanza", "Vite dei più celebri architetti, e scultori veneziani", "Venezia 1778", "book"),
    record("cand-8799", 1152, 1152, "Abbate D. Cristoforo Tentori", "Saggio sulla storia civile, politica, ecclesiastica e sulla corografia e topografia degli stati della repubblica di Venezia", "12 vols., Venezia 1785–90", "book set"),
    record("cand-4569", 1153, 1154, "Alfred de Terrebasse", "Relation des principaux événements de la vie de Salvaing de Boissieu", "Lyon 1850", "book"),
    record("cand-11437", 1155, 1155, "G. de Tervarent", "Attributs et symboles dans l’art profane 1450–1600", "Genève 1959", "book"),
    record("cand-10392", 1156, 1157, "Mauro Tesi", "Raccolta di disegni originali estratti da diverse collezioni pubblicata da Lodovico Inig calcografo in Bologna—aggiuntavi la vita dell’autore", "[Bologna 1787]", "book/catalogue", notes=["The page image reads Inig; retain the printed spelling. The candidate represents the collection; the precise status of the introduction cited in p.358 note 3 remains to be clarified."], related=["cand-2551"]),
    record("cand-9779", 1158, 1158, "A. Tessier", "‘Di Francesco Maggiotto—pittore veneziano’", "Archivio Veneto, 1882, pp. 289–315", "journal article", quote=tessier_quote, shared_line=True, corrections=[{"line": 1158, "ocr": "pp. 289315Teti, Girolamo:", "print": "pp. 289–315. / Teti, Girolamo:", "note": "The page image shows the page range ending 315, then a separate Teti record; OCR merged both entries and omitted punctuation."}]),
    record("cand-11438", 1158, 1158, "Teti, Girolamo", "Aedes Barberinae ad Quirinalem a comite Hieronymo Tetio Persino descriptae", "Romae MDCXLII", "book", quote=teti_quote, shared_line=True, related=["cand-2561"], notes=["The OCR places this separate entry immediately after the Tessier range on the same line; the page image confirms separate entries." ]),
    record("cand-4837", 1159, 1159, "J. Thuillier", "‘Un peintre passionné’", "L’Œil, no. 47, Nov. 1958, pp. 26–33", "journal article", corrections=[{"line": 1159, "ocr": "L’CEil", "print": "L’Œil", "note": "The page image reads the journal title with the œ ligature."}]),
    record("cand-5805", 1160, 1160, "J. Thuillier", "‘Pour un “Corpus Poussinianum” ’", "Actes du Colloque Poussin, 1960, vol. II, pp. 49–238", "conference paper", corrections=[{"line": 1160, "ocr": "i960", "print": "1960", "note": "The page image reads 1960; the volume is II."}]),
    record("cand-8792", 1161, 1161, "Giulio Lorenzetti, curator", "Tiepolo—catalogo della mostra a cura di Giulio Lorenzetti", "Venezia 1951", "exhibition catalogue", notes=["Likely identifies the p.270 note 3 Mostra del Tiepolo p.8 locator; the page itself was not consulted."]),
    record("cand-5493", 1162, 1163, "H. Tietze", "‘Andrea Pozzo und die Fürsten Liechtenstein’", "Jahrbuch für Landeskunde von Niederösterreich, 1914–15, pp. 432–446", "journal article"),
    record("cand-7350", 1164, 1164, "H. Tietze", "‘Eugenio di Savoia amico dell’arte’", "Le Vie d’Italia e del Mondo, 1933, pp. 891–907", "journal article"),
    record("cand-10451", 1165, 1166, "Emilio de Tipaldo", "Descrizione della deliziosa villa di Sala di proprietà del signor Demetrio Mircovich", "Venezia 1833", "book", notes=["The stray marks after Venezia 1833 in the OCR are not part of the printed entry."]),
    record("cand-11439", 1167, 1167, "Emilio de Tipaldo", "Biografia degli Italiani illustri nelle scienze, lettere ed arti del secolo XVIII, e de’ contemporanei", "10 vols., Venezia 1834–45", "book set", corrections=[{"line": 1167, "ocr": "io vols.", "print": "10 vols.", "note": "The page image reads 10 vols.; OCR confuses the numeral 1 with i."}], related=["cand-10451"]),
    record("cand-9346", 1168, 1168, "L. Toesca", "‘Alessandro Galilei in Inghilterra’", "English Miscellany, Roma 1952, pp. 189–220", "journal article", related=["cand-4332", "cand-9345"], notes=["The p.286 note 1 p.208 locator falls within the printed range; author form differs (L. Toesca versus Ilaria Toesca) and remains for S3."]),
    record("cand-4333", 1169, 1169, "L. Toesca", "‘Note sulla storia del Palazzo Giustiniani a San Luigi dei Francesi’", "Bollettino d’Arte, 1957, pp. 296–308", "journal article", related=["cand-4332"]),
    record("cand-10476", 1170, 1170, "Gianfranco Torcellan", "Una figura della Venezia settecentesca: Andrea Memmo", "Venezia–Roma 1963", "book", corrections=[{"line": 1170, "ocr": "VeneziaRoma", "print": "Venezia-Roma", "note": "The page image has a line-end hyphen after Venezia continued by Roma on the next line."}], related=["cand-2644"]),
    record("cand-11110", 1171, 1171, "Gianfranco Torcellan", "Settecento veneto e altri scritti storici", "Torino 1969", "book", related=["cand-2644"]),
    record("cand-7002", 1172, 1172, "E. du Gué Trapier", "Ribera", "New York 1952", "book"),
    record("cand-5801", 1173, 1173, "K. Trauman-Steinitz", "‘Poussin illustiator of Leonardo da Vinci’", "Art Quarterly, Spring 1953, pp. 40–55", "journal article", related=["cand-5800"], notes=["The printed title spells illustiator; preserve the apparent print error rather than normalize it."]),
    record("cand-11440", 1174, 1174, "L. Treat", "Un cosmopolite italien du XVIIIème siècle—Francesco Algarotti", "Trévoux 1913", "book"),
    record("cand-9303", 1175, 1175, "A. S. Turberville", "A history of Welbeck Abbey and its owners", "London 1939", "book", notes=["Likely matches the p.280 note 2 vol.II p.14 locator; cited volume and page were not consulted."]),
    record("cand-11441", 1176, 1177, "Nicholas Turner", "‘Ferrante Carlo’s Descrittione della Cupola di S. Andrea della Valle depinta dal Cavalier Gio: Lanfranchi; a source for Bellori’s descriptive method’", "Storia dell’Arte, 1971, pp. 297–325", "journal article"),
]

if len(candidate_updates) != 21 or len(new_candidates) != 5 or len(entries) != 30:
    raise SystemExit("unexpected candidate or publication counts")

mention_ids = {row["mention_id"] for row in mentions}
mention_keys = {
    (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"]))
    for row in mentions
}
statement_ids = {row["statement_id"] for row in statements}
existing_claim_keys = {
    (
        row.get("segment_id", ""),
        " ".join(str((row.get("qualifiers") or {}).get("claim", "")).split()).casefold(),
    )
    for row in statements
    if isinstance(row.get("qualifiers"), dict)
}
new_mentions = []
new_statements = []
covered_lines = set()
line_owners = {}
new_spans = []


def source_quote(item):
    if item["quote"] is not None:
        return item["quote"]
    return "\n".join(source_lines[item["start"] - 1 : item["end"]])


for index, item in enumerate(entries, start=1):
    candidate_id = item["candidate_id"]
    candidate = candidate_by_id.get(candidate_id)
    if not candidate or candidate.get("suggested_type") != "archive":
        raise SystemExit(f"missing/wrong-type publication candidate: {candidate_id}")
    for related_id in item["related"]:
        if related_id not in candidate_by_id:
            raise SystemExit(f"related candidate FK missing: {candidate_id}: {related_id}")
    line_span = set(range(item["start"], item["end"] + 1))
    for line in line_span:
        owners = line_owners.setdefault(line, [])
        if owners and not (line == 1158 and item["shared_line"] and all(owner["shared_line"] for owner in owners)):
            raise SystemExit(f"overlapping publication line range at L{line}: {candidate_id}")
        owners.append(item)
    covered_lines |= line_span

    quote = source_quote(item)
    positions = [i for i in range(len(segment_text)) if segment_text.startswith(quote, i)]
    if len(positions) != 1:
        raise SystemExit(f"source quote must occur once: {candidate_id} L{item['start']}")
    start_char = positions[0]
    end_char = start_char + len(quote)
    mention_id = f"m-chp21-bib-l1141-1177-{index:03d}"
    if mention_id in mention_ids:
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    mention_key = (SEGMENT, candidate_id, str(start_char), str(end_char))
    if mention_key in mention_keys:
        raise SystemExit(f"duplicate mention natural key: {mention_id}")
    mention_row = {field: "" for field in mention_fields}
    mention_row.update(
        mention_id=mention_id,
        segment_id=SEGMENT,
        candidate_id=candidate_id,
        surface_form=quote,
        start_char=start_char,
        end_char=end_char,
        note="S0 bibliography entry; page-image readings and S3 comparisons are recorded on its statement.",
    )
    new_mentions.append(mention_row)
    mention_ids.add(mention_id)
    mention_keys.add(mention_key)
    new_spans.append((start_char, end_char))

    statement_id = f"st-chp21-bib-l1141-1177-entry-{index:02d}"
    if statement_id in statement_ids:
        raise SystemExit(f"duplicate statement ID: {statement_id}")
    claim = f"Haskell lists {item['title']} in the bibliography."
    claim_key = (SEGMENT, " ".join(claim.split()).casefold())
    if claim_key in existing_claim_keys:
        raise SystemExit(f"duplicate statement claim: {claim}")
    statement_ids.add(statement_id)
    existing_claim_keys.add(claim_key)
    qualifiers = {
        "source_line_start": item["start"],
        "source_line_end": item["end"],
        "claim": claim,
        "speaker": "Haskell’s bibliography",
        "relation_candidate": False,
        "mentioned_candidate_ids": [candidate_id],
        "text_layer": "bibliographic entry",
        "qualification": "This records the bibliography entry only; the cited publication was not independently consulted in this S2 pass.",
        "bibliographic_record": {
            "author_as_printed": item["author"],
            "title_as_printed": item["title"],
            "publication_details_as_printed": item["details"],
            "record_kind": item["kind"],
            "printed_page": 438,
            "pdf_physical_page": 28,
        },
    }
    if item["corrections"]:
        qualifiers["page_image_ocr_corrections"] = item["corrections"]
    if item["page_image_notes"]:
        qualifiers["page_image_notes"] = item["page_image_notes"]
    if item["related"]:
        qualifiers["related_candidate_ids_for_s3"] = item["related"]
    new_statements.append(
        {
            "statement_id": statement_id,
            "segment_id": SEGMENT,
            "subject_candidate_id": None,
            "object_candidate_id": candidate_id,
            "predicate": "bibliography_lists_publication",
            "qualifiers": qualifiers,
            "original_quote": quote,
            "origin": "book",
            "source_file": SOURCE_FILE,
        }
    )

if covered_lines != set(range(1142, 1178)):
    raise SystemExit(f"bibliography lines not covered exactly: {sorted(set(range(1142, 1178)) - covered_lines)}")
if not all(line_owners[1158][i]["shared_line"] for i in range(2)) or len(line_owners[1158]) != 2:
    raise SystemExit("the two records split from OCR line 1158 were not isolated")
if len(new_mentions) != 30 or len(new_statements) != 30:
    raise SystemExit("unexpected mention/statement counts")
if any(new_spans[i][1] > new_spans[i + 1][0] for i in range(len(new_spans) - 1)):
    raise SystemExit("mention character spans overlap")

for statement in new_statements:
    for field in ("subject_candidate_id", "object_candidate_id"):
        candidate_id = statement.get(field)
        if candidate_id is not None and candidate_id not in candidate_by_id:
            raise SystemExit(f"statement FK missing: {statement['statement_id']} {field}={candidate_id}")
    for field in ("mentioned_candidate_ids", "related_candidate_ids_for_s3"):
        for candidate_id in statement["qualifiers"].get(field, []):
            if candidate_id not in candidate_by_id:
                raise SystemExit(f"{field} FK missing: {statement['statement_id']}: {candidate_id}")
    if statement["original_quote"] not in segment_text:
        raise SystemExit(f"statement quote outside source segment: {statement['statement_id']}")

coverage_row.update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L1142-1177",
    note="Printed p.438: 30 publication records reviewed; OCR line L1158 split into two page-image-confirmed entries; see process/stages.md.",
)

all_candidates = candidates + new_candidates
all_mentions = mentions + new_mentions
all_statements = statements + new_statements
after = {
    "candidate_count": len(all_candidates),
    "mention_count": len(all_mentions),
    "statement_count": len(all_statements),
    "coverage_complete": sum(row["disposition"] == "reviewed" for row in coverage),
    "coverage_queued": sum(row["disposition"] == "queued" for row in coverage),
    "coverage_excluded": sum(row["disposition"] == "excluded" for row in coverage),
}
expected_after = {
    "candidate_count": 11420,
    "mention_count": 26742,
    "statement_count": 12015,
    "coverage_complete": 613,
    "coverage_queued": 98,
    "coverage_excluded": 121,
}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "segment_id": SEGMENT,
    "candidate_updates": len(candidate_updates),
    "new_archive_candidates": len(new_candidates),
    "publication_entries": len(entries),
    "new_mentions": len(new_mentions),
    "publication_statements": len(new_statements),
    **after,
}

if ARGS.apply:
    table_paths = (candidate_path, mention_path, statement_path, coverage_path)
    backup_paths = [path.with_name(path.name + BACKUP_SUFFIX) for path in table_paths]
    if any(path.exists() for path in backup_paths):
        raise SystemExit("a migration backup already exists; refusing to overwrite it")
    for path, backup_path in zip(table_paths, backup_paths):
        shutil.copy2(path, backup_path)
    write_csv(candidate_path, candidate_fields, all_candidates)
    write_csv(mention_path, mention_fields, all_mentions)
    write_jsonl(statement_path, all_statements)
    write_csv(coverage_path, coverage_fields, coverage)
    result["backups"] = [str(path.relative_to(ROOT)) for path in backup_paths]

print(json.dumps(result, ensure_ascii=False, indent=2))
