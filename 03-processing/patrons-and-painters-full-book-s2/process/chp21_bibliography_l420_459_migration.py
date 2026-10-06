#!/usr/bin/env python3
"""Controlled S2 migration for bibliography entries on printed p. 421."""
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
SEGMENT = "chp-21:21_CHP-21Bibliography:l420-459"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
SEGMENT_SHA = "0ba7f8abc0f5a326a50f9154012c97f3727f6c93e6ae57de4d882df5cdc2190d"
BACKUP = ".bak-s2-chp21-bibliography-l420-459-20261007"

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
segment_text = "\n".join(source_lines[419:459])
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
    11293,
    26215,
    11489,
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

# Entry boundaries and OCR corrections were checked against PDF physical page 11.
entries = [
    {"candidate_id": "cand-9910", "start": 421, "end": 421,
     "author": "Denina, Carlo", "title": "Considérations d’un italien sur l’Italie",
     "details": "Berlin, 1796", "kind": "book"},
    {"candidate_id": "cand-11315", "new_name": "J. von Derschau, Irrige Zuschreibungen an Sebastiano Ricci (Monatshefte für Kunstwissenschaft, 1916)",
     "new_detail": "The bibliography identifies the article; it was not independently consulted.",
     "start": 422, "end": 422, "author": "Derschau, J. von",
     "title": "Irrige Zuschreibungen an Sebastiano Ricci",
     "details": "Monatshefte für Kunstwissenschaft, 1916, pp. 161–169", "kind": "journal article"},
    {"candidate_id": "cand-11316", "new_name": "J. von Derschau, Sebastiano Ricci (Heidelberg, 1922)",
     "new_detail": "The bibliography identifies the book; it was not independently consulted.",
     "start": 423, "end": 423, "author": "Derschau, J. von", "title": "Sebastiano Ricci",
     "details": "Heidelberg, 1922", "kind": "book",
     "corrections": [{"line": 423, "ocr": "Ricci,.Heidelberg", "print": "Ricci, Heidelberg"}]},
    {"candidate_id": "cand-7028", "start": 424, "end": 424,
     "author": "Desjardins, Abel", "title": "L’œuvre de Jean Bologne",
     "details": "Paris, 1883", "kind": "book"},
    {"candidate_id": "cand-9444", "start": 425, "end": 426,
     "author": "", "title": "Le Dessin Français dans les Collections du XVIII siècle",
     "details": "Catalogue of exhibition organised by Gazette des Beaux-Arts, Paris, 1935",
     "kind": "exhibition catalogue; organiser stated",
     "corrections": [{"line": 426, "ocr": "1935. \u0022", "print": "1935."}]},
    {"candidate_id": "cand-7029", "start": 427, "end": 427,
     "author": "Dhanens, Elizabeth", "title": "Jean Boulogne",
     "details": "Brussel, 1956", "kind": "book"},
    {"candidate_id": "cand-8261", "start": 428, "end": 429,
     "author": "Dolfin, Bortolo Giovanni",
     "title": "I Dolfin, patrizii veneziani nella storia di Venezia",
     "details": "2a edizione, Milano, 1924", "kind": "book"},
    {"candidate_id": "cand-11317",
     "new_name": "Bernardo de Dominici, Vite dei pittori scultori ed architetti napoletani (4 vols., Napoli, 1843)",
     "new_detail": "Set-level bibliography record. Keep distinct from volume-specific citation locator cand-4835 pending S3 identity review; cited contents were not independently consulted.",
     "start": 430, "end": 430, "author": "Dominici, Bernardo de",
     "title": "Vite dei pittori scultori ed architetti napoletani",
     "details": "4 vols., Napoli, 1843", "kind": "book set",
     "related": ["cand-4835"]},
    {"candidate_id": "cand-6422", "start": 431, "end": 431,
     "author": "Donahue, Kenneth", "title": "The ingenious Bellori—a biographical study",
     "details": "Marsyas, 1946", "kind": "journal article"},
    {"candidate_id": "cand-11318",
     "new_name": "G. B. Doni, De’ Trattati di Musica . . . raccolti e pubblicati per opera di A. F. Gori (2 vols., Firenze, 1763)",
     "new_detail": "The bibliography identifies a two-volume publication; its contents were not independently consulted.",
     "start": 432, "end": 433, "author": "Doni, G. B.",
     "title": "De’ Trattati di Musica . . . raccolti e pubblicati per opera di A. F. Gori",
     "details": "2 vols., Firenze, 1763", "kind": "book set",
     "corrections": [
         {"line": 432, "ocr": "De’ Trattati di Musica    raccolti",
          "print": "De’ Trattati di Musica . . . raccolti"},
         {"line": 433, "ocr": "Firenze 1763. -",
          "print": "Firenze 1763. (the trailing dash is a scan mark, not text)"},
     ]},
    {"candidate_id": "cand-9297", "start": 434, "end": 434,
     "author": "Donzelli, Carlo", "title": "I pittori Veneti del Settecento",
     "details": "Firenze, 1957", "kind": "book"},
    {"candidate_id": "cand-10866", "start": 435, "end": 435,
     "author": "Dubon, David",
     "title": "Tapestries from the Samuel H. Kress Collection at the Philadelphia Museum of Art",
     "details": "London, 1964", "kind": "book"},
    {"candidate_id": "cand-5470", "start": 436, "end": 436,
     "author": "Dudon, Paul", "title": "Le quiétiste espagnol Michel Molinos",
     "details": "Paris, 1921", "kind": "book"},
    {"candidate_id": "cand-11319", "new_name": "J. Dumesnil, Histoire des plus célèbres amateurs italiens (Paris, 1853)",
     "new_detail": "The bibliography identifies the cited work; the author's full identity is not supplied here.",
     "start": 437, "end": 437, "author": "Dumesnil, J.",
     "title": "Histoire des plus célèbres amateurs italiens",
     "details": "Paris, 1853", "kind": "book"},
    {"candidate_id": "cand-5611", "start": 438, "end": 438,
     "author": "Dworschak, Fritz", "title": "Der Medailleur Gianlorenzo Bernini",
     "details": "Jahrbuch der Preussischen Kunstsammlungen, 1934, pp. 27–41",
     "kind": "journal article"},
    {"candidate_id": "cand-5167", "start": 439, "end": 440,
     "author": "Ehrle, Franz", "title": "Dalle carte e dai disegni di Virgilio Spada",
     "details": "Atti della Pontificia Accademia Romana di Archeologia, 1927",
     "kind": "journal article"},
    {"candidate_id": "cand-5243", "start": 441, "end": 441,
     "author": "Enggass, Robert", "title": "Bernini, Gaulli and the frescoes of the Gesù",
     "details": "Art Bulletin, 1957, pp. 303–5", "kind": "journal article",
     "corrections": [{"line": 441,
                      "ocr": "frescoes of the Gesù in Art Bulletin",
                      "print": "frescoes of the Gesù’ in Art Bulletin"}]},
    {"candidate_id": "cand-10929", "start": 442, "end": 442,
     "author": "Enggass, Robert", "title": "The Painting of Baciccio",
     "details": "Philadelphia, 1964", "kind": "book"},
    {"candidate_id": "cand-10934", "start": 443, "end": 444,
     "author": "Enggass, Robert",
     "title": "The Altar-rail for St. Ignatius’ Chapel in the Gesù di Roma",
     "details": "Burlington Magazine, 1974, pp. 176–189", "kind": "journal article"},
    {"candidate_id": "cand-10935", "start": 445, "end": 445,
     "author": "Enggass, Robert",
     "title": "Early Eighteenth-Century Sculpture in Rome—an illustrated catalogue raisonné",
     "details": "2 vols., Philadelphia, 1976", "kind": "book set"},
    {"candidate_id": "cand-9350", "start": 446, "end": 447,
     "author": "", "title": "English Taste in the Eighteenth Century",
     "details": "Catalogue of exhibition at Royal Academy of Arts, London, 1955–6",
     "kind": "exhibition catalogue; author not stated"},
    {"candidate_id": "cand-11320",
     "new_name": "Janus Nicius Erithraeus [G. V. Rossi], Pinacotheca imaginum illustrium (3 vols., Coloniae, 1645–8)",
     "new_detail": "The bibliography identifies a three-volume publication; its contents and the author's identity were not independently verified.",
     "start": 448, "end": 449, "author": "Erithraeus, Janus Nicius [G. V. Rossi]",
     "title": "Pinacotheca imaginum illustrium",
     "details": "3 vols., Coloniae, 1645–8", "kind": "book set"},
    {"candidate_id": "cand-11206", "start": 450, "end": 450,
     "author": "Ernst, Serge", "title": "Stefano Torelli in Russia",
     "details": "Arte Veneta, 1970, pp. 173–184", "kind": "journal article"},
    {"candidate_id": "cand-11183", "start": 451, "end": 451,
     "author": "", "title": "Eugen, Prinz, und sein Belvedere",
     "details": "Wien, 1963", "kind": "bibliographic item; format unspecified"},
    {"candidate_id": "cand-11321",
     "new_name": "John Evelyn, Diary (edited by E. S. de Beer; 6 vols., Oxford, 1955)",
     "new_detail": "Set-level edited edition. Keep distinct from volume-II page-277 citation locator cand-5685 pending S3 identity review; the cited contents were not independently consulted.",
     "start": 452, "end": 452, "author": "Evelyn, John",
     "title": "Diary", "details": "Edited by E. S. de Beer; 6 vols., Oxford, 1955",
     "kind": "edited book set", "related": ["cand-5685"]},
    {"candidate_id": "cand-7935", "start": 453, "end": 453,
     "author": "Ewald, Gerhard", "title": "Johann Carl Loth 1632–1698",
     "details": "Amsterdam, 1965", "kind": "book"},
    {"candidate_id": "cand-11052", "start": 454, "end": 455,
     "author": "Ewald, Gerhard",
     "title": "Appunti sulla Galleria Gerini e sugli affreschi di Anton Domenico Gabbiani",
     "details": "In Kunst des Barock in der Toskana, München, 1976, pp. 333–343",
     "kind": "essay in collected volume",
     "corrections": [
         {"line": 455, "ocr": ". in Kunst", "print": "in Kunst"},
         {"line": 455, "ocr": "pp. 3 3 3^3 43", "print": "pp. 333–343"},
     ]},
    {"candidate_id": "cand-7845", "start": 456, "end": 456,
     "author": "Fabbri, Mario",
     "title": "Alessandro Scarlatti e il Principe Ferdinando de’ Medici",
     "details": "Firenze, 1961", "kind": "book"},
    {"candidate_id": "cand-5456", "start": 457, "end": 457,
     "author": "Fabrini, P. Natale", "title": "La chiesa di S. Ignazio in Roma",
     "details": "Roma, 1952", "kind": "book"},
    {"candidate_id": "cand-10852", "start": 458, "end": 458,
     "author": "Fagiolo dell’Arca, Maurizio; Carandini, Silvia",
     "title": "L’Effimero Barocco—Strutture della festa nella Roma del ’600",
     "details": "2 vols., Roma, 1977–8", "kind": "book set",
     "corrections": [
         {"line": 458, "ocr": "L’Effìmero", "print": "L’Effimero"},
         {"line": 458, "ocr": "’óoo", "print": "’600"},
     ]},
    {"candidate_id": "cand-5612", "start": 459, "end": 459,
     "author": "Faldi, Italo",
     "title": "I busti berniniani di Paolo Giordano e Isabella Orsini",
     "details": "Paragone, 57, 1954, pp. 13–15", "kind": "journal article",
    "corrections": [{"line": 459, "ocr": "T busti", "print": "‘I busti"}]},
]

if len(entries) != 31 or len({row["candidate_id"] for row in entries}) != 31:
    raise SystemExit("bibliography publication specification is incomplete or duplicated")
covered_lines = {line for entry in entries for line in range(entry["start"], entry["end"] + 1)}
if covered_lines != set(range(421, 460)):
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
    row.update(
        candidate_id=candidate_id,
        canonical_name=entry["new_name"],
        suggested_type="archive",
        status="open",
        detail=entry["new_detail"],
        candidate_origin="body-mention",
        candidate_source_ref=f"{SEGMENT}#L{entry['start']}",
    )
    new_candidates.append(row)
    candidate_by_id[candidate_id] = row
    natural_keys.add(key)

expected_name_updates = {
    "cand-9910": (
        "Denina, page 196 (citation locator)",
        "Carlo Denina, Considérations d’un italien sur l’Italie (Berlin, 1796)",
        "Printed bibliography p.421 identifies the cited work; page 196 was not independently consulted.",
    ),
    "cand-6422": (
        "Donahue, 1946 (publication on Bellori's life; title unspecified)",
        "Kenneth Donahue, The ingenious Bellori—a biographical study (Marsyas, 1946)",
        "Printed bibliography p.421 supplies the article title; the article was not independently consulted.",
    ),
    "cand-10866": (
        "David Dubon’s publication describing the French tapestries given to Cardinal Francesco Barberini (title unspecified)",
        "David Dubon, Tapestries from the Samuel H. Kress Collection at the Philadelphia Museum of Art (London, 1964)",
        "Printed bibliography p.421 supplies the title and publication details; the cited work was not independently consulted.",
    ),
    "cand-5470": (
        "Paul Dudon, cited study of Molinos; title and edition unresolved",
        "Paul Dudon, Le quiétiste espagnol Michel Molinos (Paris, 1921)",
        "Printed bibliography p.421 identifies the cited study; its contents were not independently consulted.",
    ),
    "cand-5167": (
        "Ehrle, cited publication on Virgilio Spada; title and date unspecified",
        "Franz Ehrle, Dalle carte e dai disegni di Virgilio Spada (Atti della Pontificia Accademia Romana di Archeologia, 1927)",
        "Printed bibliography p.421 identifies the cited article; it was not independently consulted.",
    ),
    "cand-5243": (
        "Enggass (1957) study of the Gesù dome",
        "Robert Enggass, Bernini, Gaulli and the frescoes of the Gesù (Art Bulletin, 1957)",
        "Printed bibliography p.421 identifies the cited article; it was not independently consulted.",
    ),
    "cand-10929": (
        "Robert Enggass’s monograph on Giovanni Battista Gaulli (1964; title unspecified)",
        "Robert Enggass, The Painting of Baciccio (Philadelphia, 1964)",
        "Printed bibliography p.421 supplies the title and publication details; the book was not independently consulted.",
    ),
    "cand-10934": (
        "Enggass’s article on the Gesù altar of St Ignatius (1974; title unspecified)",
        "Robert Enggass, The Altar-rail for St. Ignatius’ Chapel in the Gesù di Roma (Burlington Magazine, 1974)",
        "Printed bibliography p.421 supplies the title and publication details; the article was not independently consulted.",
    ),
    "cand-10935": (
        "Enggass’s book on eighteenth-century sculpture in Rome (1976; title unspecified)",
        "Robert Enggass, Early Eighteenth-Century Sculpture in Rome (2 vols., Philadelphia, 1976)",
        "Printed bibliography p.421 supplies the full title and two-volume extent; the book was not independently consulted.",
    ),
    "cand-9350": (
        "English Taste in the Eighteenth Century, 1955-6, pp. 26 and 54 (citation locators; author unresolved)",
        "English Taste in the Eighteenth Century (Royal Academy of Arts exhibition catalogue, London, 1955–6; author not stated)",
        "Printed bibliography p.421 identifies the Royal Academy of Arts exhibition catalogue; no author is named in the entry.",
    ),
    "cand-11206": (
        "Ernst publication cited at p.406 note 8 (title and year unspecified)",
        "Serge Ernst, Stefano Torelli in Russia (Arte Veneta, 1970)",
        "Printed bibliography p.421 identifies the article and year; it was not independently consulted.",
    ),
    "cand-11183": (
        "Eugen, Prinz, publication cited at p.403 note 3, pp. 115-41 (bibliographic role unresolved)",
        "Eugen, Prinz, und sein Belvedere (Wien, 1963; author not stated)",
        "The bibliography prints the complete item title in italics and supplies Wien, 1963; it does not state an author.",
    ),
    "cand-7935": (
        "Ewald (1965), catalogue entries on Karl Loth",
        "Gerhard Ewald, Johann Carl Loth 1632–1698 (Amsterdam, 1965)",
        "Printed bibliography p.421 identifies the title of the cited work; its contents were not independently consulted.",
    ),
    "cand-11052": (
        "Ewald's 1976 articles on Antonio Domenico Gabbiani",
        "Gerhard Ewald, Appunti sulla Galleria Gerini e sugli affreschi di Anton Domenico Gabbiani (Kunst des Barock in der Toskana, 1976)",
        "Printed bibliography p.421 identifies the single 1976 essay cited in note 17; the essay was not independently consulted.",
    ),
    "cand-5456": (
        "Unidentified Fabrini publication cited for the Annunciation relief",
        "P. Natale Fabrini, La chiesa di S. Ignazio in Roma (Roma, 1952)",
        "Printed bibliography p.421 identifies the cited publication; it was not independently consulted.",
    ),
    "cand-10852": (
        "Study of seventeenth-century Roman festivals by Fagiolo dell’Arca and Carandini (title unspecified)",
        "Maurizio Fagiolo dell’Arca and Silvia Carandini, L’Effimero Barocco—Strutture della festa nella Roma del ’600 (2 vols., Roma, 1977–8)",
        "Printed bibliography p.421 identifies the cited two-volume study; its contents were not independently consulted.",
    ),
}

for candidate_id, (expected, updated, detail) in expected_name_updates.items():
    candidate = candidate_by_id.get(candidate_id)
    if not candidate or candidate.get("suggested_type") != "archive":
        raise SystemExit(f"missing/wrong-type bibliography candidate: {candidate_id}")
    if candidate["canonical_name"] != expected:
        raise SystemExit(f"candidate identity label changed: {candidate_id}")
    if detail in candidate.get("detail", ""):
        raise SystemExit(f"candidate detail already updated: {candidate_id}")
    candidate["canonical_name"] = updated
    candidate["detail"] = f'{candidate.get("detail", "").rstrip()} {detail}'.strip()

candidate_detail_updates = {
    "cand-4835": (
        "Printed p.421 lists the complete four-volume 1843 set as separate candidate cand-11317; "
        "this candidate retains its volume-specific citation scope pending S3."
    ),
    "cand-5685": (
        "Printed p.421 lists the complete six-volume 1955 edited Diary set as separate candidate "
        "cand-11321; this candidate retains its volume-II, p.277 citation-locator scope pending S3."
    ),
}
for candidate_id, detail in candidate_detail_updates.items():
    candidate = candidate_by_id.get(candidate_id)
    if not candidate or candidate.get("suggested_type") != "archive":
        raise SystemExit(f"missing/wrong-type locator candidate: {candidate_id}")
    if detail in candidate.get("detail", ""):
        raise SystemExit(f"locator candidate detail already updated: {candidate_id}")
    candidate["detail"] = f'{candidate.get("detail", "").rstrip()} {detail}'.strip()

updated_archive_names = {
    (row["canonical_name"].strip().casefold(), row["suggested_type"].strip().casefold()): row["candidate_id"]
    for row in candidates
    if row["suggested_type"].strip().casefold() == "archive"
}
for candidate_id, (_, updated, _) in expected_name_updates.items():
    key = (updated.strip().casefold(), "archive")
    collision = updated_archive_names.get(key)
    if collision and collision != candidate_id:
        raise SystemExit(f"candidate rename collides with archive candidate {collision}: {candidate_id}")
    updated_archive_names[key] = candidate_id
for row in new_candidates:
    key = (row["canonical_name"].strip().casefold(), "archive")
    if key in updated_archive_names:
        raise SystemExit(f"new candidate collides with archive candidate {updated_archive_names[key]}")
    updated_archive_names[key] = row["candidate_id"]

mention_keys = {
    (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"]))
    for row in mentions
}
new_mentions = []
new_statements = []
existing_claim_keys = {
    (
        row.get("segment_id", ""),
        " ".join(str((row.get("qualifiers") or {}).get("claim", "")).split()).casefold(),
    )
    for row in statements
    if isinstance(row.get("qualifiers"), dict)
}


def source_quote(entry):
    return "\n".join(source_lines[entry["start"] - 1:entry["end"]])


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
        mention_id=f"m-chp21-bib-l420-459-{len(new_mentions) + 1:03d}",
        segment_id=SEGMENT,
        candidate_id=candidate_id,
        surface_form=surface,
        start_char=position,
        end_char=end,
        note=note,
    )
    new_mentions.append(row)
    mention_keys.add(key)


def add_statement(statement_id, object_id, quote, line_start, line_end, claim, qualifiers):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    claim_key = (SEGMENT, " ".join(claim.split()).casefold())
    if claim_key in existing_claim_keys:
        raise SystemExit(f"duplicate statement claim: {claim}")
    existing_claim_keys.add(claim_key)
    row = {
        "statement_id": statement_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": None,
        "object_candidate_id": object_id,
        "predicate": "bibliography_lists_publication",
        "qualifiers": {
            "source_line_start": line_start,
            "source_line_end": line_end,
            "claim": claim,
            "speaker": "Haskell’s bibliography",
            "relation_candidate": False,
            "mentioned_candidate_ids": [object_id],
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
    add_mention(
        candidate_id,
        quote,
        "S0 bibliography entry; page-image OCR corrections are recorded on its statement.",
    )
    record = {
        "author_as_printed": entry["author"],
        "title_as_printed": entry["title"],
        "publication_details_as_printed": entry["details"],
        "record_kind": entry["kind"],
        "printed_page": 421,
    }
    qualifiers = {
        "text_layer": "bibliographic entry",
        "qualification": (
            "This records the book bibliography entry only; the cited publication was not "
            "independently consulted in this S2 pass."
        ),
        "bibliographic_record": record,
    }
    if entry.get("corrections"):
        qualifiers["page_image_ocr_corrections"] = entry["corrections"]
    if entry.get("related"):
        qualifiers["related_candidate_ids_for_s3"] = entry["related"]
    add_statement(
        f"st-chp21-bib-l420-459-entry-{index:02d}",
        candidate_id,
        quote,
        entry["start"],
        entry["end"],
        f'Haskell lists {entry["title"]} in the book bibliography.',
        qualifiers,
    )

if len(new_candidates) != 7 or len(new_mentions) != 31 or len(new_statements) != 31:
    raise SystemExit("unexpected migration row counts")
if [row["candidate_id"] for row in new_candidates] != [
    f"cand-{number}" for number in range(11315, 11322)
]:
    raise SystemExit("new candidate IDs are not the expected next sequence")
for statement in new_statements:
    object_id = statement["object_candidate_id"]
    if object_id not in candidate_by_id:
        raise SystemExit(f"statement candidate FK missing: {statement['statement_id']}")
    for related_id in statement["qualifiers"].get("related_candidate_ids_for_s3", []):
        if related_id not in candidate_by_id:
            raise SystemExit(f"related candidate FK missing: {statement['statement_id']}: {related_id}")
for row in new_mentions:
    if segment_text[row["start_char"]:row["end_char"]] != row["surface_form"]:
        raise SystemExit(f"mention offset validation failed: {row['mention_id']}")
ordered_mentions = sorted(new_mentions, key=lambda row: (int(row["start_char"]), int(row["end_char"])))
for left, right in zip(ordered_mentions, ordered_mentions[1:]):
    if int(left["end_char"]) > int(right["start_char"]):
        raise SystemExit(f"overlapping mention spans: {left['mention_id']} and {right['mention_id']}")

coverage_by_id[SEGMENT]["disposition"] = "reviewed"
coverage_by_id[SEGMENT]["migration_status"] = "complete"
coverage_by_id[SEGMENT]["source_line_ranges"] = "L420-459"
coverage_by_id[SEGMENT]["note"] = (
    "Printed p.421 contains 31 publication records; the [Page 421] marker is not a record. "
    "Reused 24 archive candidates and added 7; two set-level entries are linked to existing "
    "volume-specific citation locators for S3 comparison. PDF physical page 11 corrections "
    "are in statement qualifiers; source OCR remains unchanged. Cited works were not "
    "independently consulted."
)

all_candidates = candidates + new_candidates
all_mentions = mentions + new_mentions
all_statements = statements + new_statements
all_coverage = [coverage_by_id[row["segment_id"]] for row in coverage]

print(json.dumps({
    "mode": "apply" if ARGS.apply else "dry-run",
    "segment_id": SEGMENT,
    "printed_page": 421,
    "publication_records": len(entries),
    "reused_archive_candidates": len(entries) - len(new_candidates),
    "new_archive_candidates": [row["candidate_id"] for row in new_candidates],
    "candidate_labels_refined": len(expected_name_updates),
    "volume_locators_kept_for_s3": ["cand-4835", "cand-5685"],
    "mentions_added": len(new_mentions),
    "statements_added": len(new_statements),
    "coverage_after": {
        "disposition": coverage_by_id[SEGMENT]["disposition"],
        "migration_status": coverage_by_id[SEGMENT]["migration_status"],
    },
    "table_counts_after": {
        "candidates": len(all_candidates),
        "mentions": len(all_mentions),
        "statements": len(all_statements),
        "coverage": len(all_coverage),
    },
}, ensure_ascii=False, indent=2))

if ARGS.apply:
    for path in (candidate_path, mention_path, statement_path, coverage_path):
        backup = path.with_name(path.name + BACKUP)
        if backup.exists():
            if hashlib.sha256(backup.read_bytes()).hexdigest() != hashlib.sha256(path.read_bytes()).hexdigest():
                raise SystemExit(f"refusing to overwrite a distinct backup: {backup}")
        else:
            shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, all_candidates)
    write_csv(mention_path, mention_fields, all_mentions)
    write_jsonl(statement_path, all_statements)
    write_csv(coverage_path, coverage_fields, all_coverage)
