"""Controlled S2 migration for the consolidated p.268-275 notes; dry-run by default."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_sec_ii.md"
NOTES = "chp-9:09_CHP-9_sec_ii:l85-127"
P270 = "chp-9:09_CHP-9_sec_ii:l27-36"
P271 = "chp-9:09_CHP-9_sec_ii:l38-51"
P272 = "chp-9:09_CHP-9_sec_ii:l53-60"
P273 = "chp-9:09_CHP-9_sec_ii:l62-68"
P275 = "chp-9:09_CHP-9_sec_ii:l80-83"
ASSET_SHA = "67d60205c246f2f126433bab8a22ddb29ed73e2af2fed5fff5978c319b3ee923"
NOTES_SHA = "d00ced6fff3f96f5cf574f47f45eea80ef1b6867c581d7d017f217ee2a8a5a99"
MAX_CANDIDATE = 8772
BACKUP_SUFFIX = ".bak-s2-chp9-notes-p268-p275-20261002"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(handle.name)
    temporary.replace(path)


candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
segment_path = TABLES / "segments.jsonl"

source_bytes = SOURCE.read_bytes()
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if hashlib.sha256(source_bytes).hexdigest() != ASSET_SHA:
    raise SystemExit("chapter 9 source asset has changed")
segments = {row["segment_id"]: row for row in read_jsonl(segment_path)}
if segments.get(NOTES, {}).get("sha256") != NOTES_SHA or segments[NOTES].get("asset_sha256") != ASSET_SHA:
    raise SystemExit("consolidated p.268-275 note segment is missing or changed")
if not source_lines[84].startswith("**Footnotes:**") or not source_lines[126].startswith("2 Other people too protested"):
    raise SystemExit("expected note boundaries have changed")

candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)
candidate_ids = {row["candidate_id"] for row in candidates}
mention_ids = {row["mention_id"] for row in mentions}
statement_ids = {row["statement_id"] for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}
max_candidate = max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates)
if max_candidate != MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: expected {MAX_CANDIDATE}, found {max_candidate}")
if (coverage_by_id[NOTES]["disposition"], coverage_by_id[NOTES]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("consolidated note segment is not queued/pending")
if (coverage_by_id[P270]["disposition"], coverage_by_id[P270]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.270 body is not reviewed/partial")
if (coverage_by_id[P272]["disposition"], coverage_by_id[P272]["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("p.272 body is not reviewed/complete")


EXISTING = {
    "zanetti": "cand-2861", "gherardi": "cand-1155", "muratori": "cand-1717",
    "mocenigo": "cand-1673", "stazio": "cand-2508", "piazzetta": "cand-1901",
    "ricci": "cand-2154", "tiepolo": "cand-2569", "trevisani": "cand-2650",
    "pittoni": "cand-1950", "dominicans": "cand-0941", "jesuits": "cand-1322",
    "zattere": "cand-8707", "scuola_carmine": "cand-8706", "rubens": "cand-2293",
    "luigi": "cand-5453", "foscarini_will": "cand-8469", "foscarini": "cand-1056",
    "correr": "cand-8262", "pieta": "cand-8551", "clerici": "cand-0790",
    "carmanite": "cand-0563", "letterini": "cand-1400", "corner": "cand-0844", "benedictines": "cand-0287",
    "sanciano": "cand-0731", "british_museum": "cand-5986", "biblioteca_estense": "cand-8539",
    "biblioteca_lucca": "cand-7803", "archivio_venezia": "cand-8592", "virgin": "cand-3427",
    "bevilacqua": "cand-8549", "marchesini_letter": "cand-8640", "marchesini": "cand-1539",
    "conti": "cand-0833", "cignaroli": "cand-1026", "venice": "cand-2719",
    "angelic_group": "cand-0734", "carmelite_order": "cand-0563", "memmo": "cand-1642",
    "wilde_prior": "cand-8662", "maria_assunta": "cand-1322", "tiepolo_index": "cand-2596",
    "scalzi": "cand-2389", "gazzetta": "cand-8729", "pieta_governors": "cand-8730",
    "manin_family": "cand-1519", "giuseppe_manini": "cand-7505",
}
for key, candidate_id in EXISTING.items():
    if candidate_id not in candidate_ids:
        raise SystemExit(f"required existing candidate is missing: {key}={candidate_id}")


# Each citation/archive locator is a provisional S1 candidate. Full bibliographic identity is deferred to the book bibliography pass.
CANDIDATE_SPECS = [
    ("silhouette156", "Etienne de Silhouette, volume I, p.156 (citation locator; title pending)", "archive", "Short citation in p.268 note 1; cited page not independently consulted.", 86, "Etienne de Silhouette"),
    ("tabacco123", "Tabacco, p.123 (citation locator; title pending)", "archive", "Short citation in p.268 note 2; do not merge with the separate Tabacco p.38 locator.", 87, "Tabacco, p. 123"),
    ("burney140", "Burney, volume I, p.140 (citation locator; title pending)", "archive", "Short citation in p.268 note 4; cited page not independently consulted.", 88, "Burney, I, p. 140"),
    ("coggiola304", "Coggiola-Pittoni, 1935, p.304 (citation locator; title pending)", "archive", "Short citation in p.268 note 5; title and argument deferred to bibliography review.", 89, "Coggiola-Pittoni, 193 5, p. 304"),
    ("ferrari1882", "L. Ferrari, 1882 (citation locator; cited p.22 and p.269 note 2)", "archive", "Short reference appears in p.268 notes 5 and p.269 note 2; do not infer that it verifies the cited archival statement independently.", 89, "L. Ferrari, 1882, p. 22"),
    ("benigna_memoir", "Libri di Memorie of Antonio Benigna (Biblioteca Marciana, MS. Ital. Cl. VII, 1620)", "archive", "A manuscript cited by Haskell through Zanetti/other notes. It is not independently consulted; the p.268 note inserts '[of the Jesuit Church]' editorially.", 89, "Biblioteca Marciana, MS. Itai. Cl. VII, 1620"),
    ("benigna_person", "Antonio Benigna (compiler named in the cited Libri di Memorie)", "person", "Keep the source's abbreviated names for the Manini brothers unresolved; do not merge them with the indexed Manin family at S2.", 89, "Antonio Benigna"),
    ("manini_brothers", "Manini brothers named in Antonio Benigna's 1729 account (personal identities unresolved)", "family", "The source reads 'S. Ant.o e S. Nicolò Fratelli Co:Co:Manini'; preserve the abbreviated source form and defer identity matching to S3.", 89, "Fratelli Co:Co:Manini"),
    ("zanetti_may1743", "Girolamo Zanetti observation of 22 May 1743 (published 1885, p.129)", "archive", "Haskell identifies the p.268-269 observer through this source locator; publication page not independently consulted.", 90, "22 Maggio 1743"),
    ("corner163", "Corner, p.163 (citation locator; title pending)", "archive", "Short reference in p.269 note 1; source title and cited page deferred to bibliography review.", 91, "Corner, p. 163"),
    ("stae_church", "S. Stae parish church in Venice (p.269 note 1)", "place", "The note treats the parish church as distinct from the 1709 façade and choir-picture group.", 91, "S. Stae"),
    ("stae_facade", "S. Stae façade funded from a legacy in 1709", "work", "An architectural component of S. Stae; Alvise Mocenigo's legacy is the reported funding source.", 91, "a façade in 1709"),
    ("stae_choir_pictures", "Unidentified choir pictures at S. Stae by Piazzetta, Sebastiano Ricci and Tiepolo", "work", "The note gives no titles and Stazio's will does not identify the commissioning artists; do not assign individual works to a painter.", 91, "pictures in the choir"),
    ("stazio_will", "Will of Andrea Stazio (Archivio di Stato di Venezia, Sezione Notarile, Atti Giovanni Zon 1283:27)", "archive", "Specific archival locator cited by Haskell; the note says it does not identify who commissioned the choir pictures.", 91, "Stazio’s will"),
    ("bianchini1894", "Bianchini, 1894, p.II (citation locator; title pending)", "archive", "Short citation in p.269 note 3; title and cited page deferred to bibliography review.", 93, "Bianchini, 1894, p. II"),
    ("pollnitz", "Pöllnitz, volume II (citation locator; cited pp.149 and 152)", "archive", "The p.269 and p.272 notes cite pp.149 and 152 of the same volume; cited pages not independently consulted.", 94, "Pôllnitz, II, p. 149"),
    ("scalzi_pamphlet", "Risposta ad un amico sopra certi riflessi falsamente concepiti contra la Chiesa dei Carmelitani Scalzi a Venezia (1734 pamphlet)", "archive", "A 32-page pamphlet by M.A., published by Luigi Pavini in 1734 and held at Biblioteca Marciana, Misc.1135, no.3; Haskell cites it through Ferrari 1882.", 95, "Risposta ad un amico"),
    ("fogolari1931", "Fogolari, 1931, pp.18-32 (citation locator; title pending)", "archive", "Short citation in p.270 note 1; cited pages not independently consulted.", 96, "Fogolari, 1931"),
    ("lorenzetti1956", "Lorenzetti, 1956 (citation locator; cited pp.30, 551 and 553)", "archive", "One provisional publication locator used across p.270-271 notes; p.269 OCR 'Lorenzetri' is read as printed 'Lorenzetti'.", 97, "Lorenzetri, 1956"),
    ("mostra_tiepolo1951", "Mostra del Tiepolo, 1951, p.8 (citation locator)", "archive", "Short citation in p.270 note 3; the note also reports a present location in the Brera.", 98, "Mostra del Tiepolo, 1951, p. 8"),
    ("urbani1879", "Urbani de Ghelthof, 1879 (citation locator; cited pp.100-117, 123-126)", "archive", "The p.270, p.273 and p.274 notes use this same 1879 publication; cited pages not independently consulted.", 99, "Urbani de Ghelthof, 1879"),
    ("zarzabini19", "Zarzabini, p.19 (citation locator; title pending)", "archive", "Short citation accompanying the specific Marchesini letter locator in p.270 note 6.", 101, "Zarzabini, p. 19"),
    ("gherardi1742", "Letter from P. E. Gherardi to Muratori, 26 October 1742 (Biblioteca Estense, Modena)", "archive", "Haskell cites this letter to identify the 1742 Gesuati visitor; neither the letter nor its manuscript witness is independently consulted.", 103, "Letter from P. E. Gherardi to Muratori"),
    ("arslan1932", "Arslan, Rivista di Venezia, 1932, p.19 (citation locator)", "archive", "Short citation in p.271 note 2; publication and page not independently consulted.", 104, "Arslan, in Rivista di Venezia, 1932, p. 19"),
    ("vecchi_person", "Alberto Vecchi (named in p.271 note 3)", "person", "The note's later pronoun 'him' may refer to Concina or Vecchi; preserve that ambiguity.", 105, "Alberto Vecchi"),
    ("vecchi1960", "Alberto Vecchi, 1960 (citation locator; title pending bibliography review)", "archive", "Short source reference in p.271 note 3; the British Museum sentence has an unresolved pronoun antecedent.", 105, "Alberto Vecchi, i960"),
    ("tentori288", "Tentori, volume X, p.288 (citation locator; title pending)", "archive", "Short citation in p.271 note 4; cited page not independently consulted.", 106, "Tentori, X, p. 288"),
    ("benedictine_nuns", "Benedictine nuns of SS. Cosma e Damiano alla Giudecca", "institution", "The community named by Haskell is distinct from the Benedictine order as a whole; individual commissions are unspecified.", 107, "nuns of SS. Cosma e Damiano alia Giudecca"),
    ("bernis_person", "Cardinal de Bernis (named in p.271 note 6)", "person", "Attribution of the quoted assessment is reported by Haskell; identity alignment remains for S3.", 108, "Cardinal de Bernis"),
    ("bernis421", "Cardinal de Bernis, volume I, p.421 (citation locator)", "archive", "Short publication locator in p.271 note 6; title and cited page not independently checked.", 108, "I, p. 421"),
    ("appendice1762", "Appendice alla prima parte dei Monumenti Veneti in risposta alla lettera di un'uomo onesto (1762)", "archive", "Pamphlet cited in p.272 note 1; keep it distinct from the 1734 Scalzi pamphlet in p.269 note 5.", 109, "Appendice alla prima parte"),
    ("seilern1959", "Count Seilern, 1959, catalogue no.170 (citation/source locator)", "archive", "Haskell cites the catalogue entry for a modello of the Glory of S. Luigi Gonzaga; catalog itself not independently consulted.", 111, "1959, No. 170"),
    ("seilern_person", "Count Seilern (as cited in p.272 note 3)", "person", "Retain the source's abbreviated attribution; defer identity alignment to S3.", 111, "Count Seilern"),
    ("luigi_modello", "Modello for the Glory of S. Luigi Gonzaga", "work", "The modello is the proposed sketch for an unrealized altarpiece in Wilde's reported interpretation; do not conflate it with the separate Pietà dome painting.", 111, "a modello for the Glory of S. Luigi Gonzaga"),
    ("wilde1960", "Professor Wilde, Italian Art and Britain, 1960, p.170 (citation locator)", "archive", "The cited page is reported by Haskell; the book and page are not independently consulted.", 59, "Italian Art and Britain"),
    ("wilde_person", "Professor Wilde (cited for an interpretation of the Seilern modello)", "person", "Do not merge automatically with the surname-only Wilde candidate from another citation; resolve in S3.", 59, "Professor Wilde"),
    ("male448", "Mâle, p.448 (citation locator; title pending)", "archive", "Short citation in p.272 note 4; the antecedent of 'It' is left unresolved.", 112, "Mâle, p. 448"),
    ("rubens_antwerp_series", "Rubens's Old Testament series for the Jesuit Church at Antwerp", "work", "A series of Old Testament scenes described as prefiguring the Life of Christ; do not infer that the note's 'It' refers to this series.", 112, "a whole series of Old Testament scenes"),
    ("bosisio", "Bosisio (citation locator; title and page unspecified)", "archive", "Short citation in p.272 note 5; full identity deferred to bibliography review.", 113, "Bosisio"),
    ("memmo1786", "Andrea Memmo, 1786, pp.4 ff. (citation locator; title pending)", "archive", "Short citation in p.272 note 6; the cited text is not independently consulted.", 114, "Andrea Memmo"),
    ("penn_model", "Modello for St Philip Neri and the Virgin (location reported as Pennsylvania Museum)", "work", "Distinct from the full-size painting or subject mention in p.273 body; object identity remains unresolved.", 117, "modello"),
    ("penn_museum", "Pennsylvania Museum (institution named as the modello's location)", "institution", "Preserve the institution's historical name; do not identify a successor institution at S2.", 117, "Pennsylvania Museum"),
    ("battistella1930", "Battistella, 1930, pp.38 ff. (citation locator; title pending)", "archive", "Short citation in p.273 note 5; cited pages not independently consulted.", 119, "Battistella, 1930, pp. 38 ff."),
    ("zanetti_mar1743", "Girolamo Zanetti report of 25 March 1743 (published 1885, p.110)", "archive", "Separate dated locator from Zanetti's 22 May 1743 report on p.268; do not merge the source texts.", 120, "25 Marzo 1743"),
    ("costadoni_person", "Don Anselmo Costadoni (source named for the following account)", "person", "Haskell cites Costadoni for the subsequent p.274 account; no title or independent consultation is supplied here.", 122, "Don Anselmo Costadoni"),
    ("casanova246", "Casanova, volume IV, p.246 (citation locator; title pending)", "archive", "Short citation in p.274 note 4; cited page not independently consulted.", 123, "Casanova, IV, p. 246"),
    ("gradenigo185_corner", "Flaminio Corner relic entry, Biblioteca Correr, Cod. Gradenigo 185 (folios unspecified)", "archive", "Separate from cand-8581, which is another Gradenigo manuscript with different folios and content; this note gives no folio range.", 124, "Cod. Gradenigo 185"),
    ("pallucchini1931", "Pallucchini, 1931, pp.421-432 (citation locator; title pending)", "archive", "Short citation in p.274 note 6; cited pages not independently consulted.", 125, "Pallucchini, 1931, pp. 421-32"),
    ("brustoloni1779", "Don Giovanni Domenico Brustoloni, 1779 (citation locator; publication title unspecified)", "archive", "Short citation in p.275 note 1; Haskell's following Letterini attribution remains explicitly probable.", 126, "Don Giovanni Domenico Brustoloni, 1779"),
    ("letterini_paintings", "Sentimental altar paintings by Bartolommeo Letterini (possible Corner commission)", "work", "Haskell says it is probable that Corner also commissioned these paintings; titles, dates and locations are not supplied.", 126, "altar paintings by Bartolommeo Letterini"),
    ("gherardi1746", "Letter from P. E. Gherardi to Muratori, 20 February 1746 (Biblioteca Estense, Modena)", "archive", "Keep this letter distinct from the separate 1742 and 1745 Gherardi letters; Haskell's closing evaluation is separately recorded.", 127, "20 February 1746"),
    ("brera", "Brera (museum/institution named as the picture's present location)", "institution", "The note says 'the Brera'; do not infer a current institutional title beyond the printed wording.", 98, "the Brera"),
    ("madonna_carmelo", "Tiepolo's Madonna del Carmelo, painted about 1720 for a Carmelite chapel at S. Aponal", "work", "A named painting, distinct from the index-derived Tiepolo painter candidate; retain the approximate date and unnamed chapel.", 98, "The picture"),
    ("unexecuted_luigi_altarpiece", "Unexecuted altarpiece possibly planned from the S. Luigi Gonzaga modello", "work", "Wilde's reported interpretation is tentative; the note explicitly says there is no evidence it was planned for the Venetian Jesuit church.", 59, "altarpiece which was never carried out"),
    ("venetian_jesuit_church", "Jesuit church in Venice (building referenced in the p.268 and p.272 notes)", "place", "Keep the church building distinct from the Jesuit institution; identity is not asserted from the bracketed p.268 editorial insertion.", 60, "Jesuit church in Venice"),
    ("dominican_zattere_church", "Unidentified Dominican Observant church on the Zattere", "place", "The p.270 note reports a new church built on part of the convent site; no formal title is supplied.", 36, "la nuova Chiesa"),
    ("redentore_church", "Church of the Redentore in Venice (named as the model for the Dominican church)", "place", "The note states a design/model comparison; do not infer authorship or a direct architectural lineage.", 36, "quella del Redentore"),
    ("antwerp_jesuit_church", "Jesuit Church at Antwerp (building named in the Rubens series note)", "place", "Keep this Antwerp building distinct from the Jesuit church in Venice and from the Jesuit order.", 112, "Jesuit Church at Antwerp"),
]

candidate_by_key = {}
new_candidates = []
for offset, (key, name, kind, detail, line_no, surface) in enumerate(CANDIDATE_SPECS, 1):
    candidate_id = f"cand-{MAX_CANDIDATE + offset:04d}"
    if candidate_id in candidate_ids:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    if any(row["canonical_name"] == name and row["suggested_type"] == kind for row in candidates):
        raise SystemExit(f"candidate natural key already exists: {name}")
    candidate_by_key[key] = candidate_id
    new_candidates.append({
        "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{NOTES if line_no >= 85 else P270 if line_no <= 36 else P271 if line_no <= 51 else P272 if line_no <= 60 else P275}#L{line_no}",
    })
candidate_ids |= {row["candidate_id"] for row in new_candidates}


def candidate(key):
    return candidate_by_key[key] if key in candidate_by_key else EXISTING[key]


segment_texts = {}
line_offsets = {}
for segment_id, meta in segments.items():
    if segment_id not in {NOTES, P270, P271, P272, P273, P275}:
        continue
    start_line, end_line = meta["line_start"], meta["line_end"]
    offset = 0
    for line_no in range(start_line, end_line + 1):
        line_offsets[(segment_id, line_no)] = offset
        offset += len(source_lines[line_no - 1]) + 1
    segment_texts[segment_id] = "\n".join(source_lines[start_line - 1:end_line])


new_mentions = []


def add_mention(mention_id, segment_id, line_no, candidate_id, surface, note, occurrence=0):
    if mention_id in mention_ids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in candidate_ids:
        raise SystemExit(f"unknown mention candidate: {candidate_id}")
    line = source_lines[line_no - 1]
    positions, cursor = [], 0
    while True:
        position = line.find(surface, cursor)
        if position < 0:
            break
        positions.append(position)
        cursor = position + 1
    if occurrence >= len(positions):
        raise SystemExit(f"surface missing on L{line_no}: {surface!r}")
    start = line_offsets[(segment_id, line_no)] + positions[occurrence]
    end = start + len(surface)
    if segment_texts[segment_id][start:end] != surface:
        raise SystemExit(f"invalid exact mention span: {mention_id}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


for key, _name, _kind, detail, line_no, surface in CANDIDATE_SPECS:
    segment_id = NOTES if line_no >= 85 else P270 if line_no <= 36 else P271 if line_no <= 51 else P272 if line_no <= 60 else P275
    add_mention(f"m-chp9-notes-{key}", segment_id, line_no, candidate(key), surface, detail)


EXTRA_MENTIONS = [
    (NOTES, 89, "benigna_memoir", "Libri di Memorie", "The quoted 1729 passage is attributed to this manuscript, not independently consulted."),
    (NOTES, 89, "venetian_jesuit_church", "[of the Jesuit Chuch]", "Bracketed building identification inserted editorially by Haskell; the S0 reading preserves the OCR spelling."),
    (NOTES, 102, "benigna_memoir", "Benigna reported", "Cross-page source attribution in Zanetti's note; same manuscript as p.268 note 5."),
    (NOTES, 102, "benigna_person", "Benigna", "Compiler/source attribution only; identity remains for S3."),
    (NOTES, 91, "stazio_will", "Archivio di Stato", "Repository cited for Stazio's will; reuse the existing repository candidate."),
    (NOTES, 91, "stazio_will", "Atti Giovanni Zon 1283:27", "Exact archival series and item locator as printed."),
    (NOTES, 91, "stae_choir_pictures", "Piazzetta", "One of the artists included in Haskell's unnamed choir-picture group."),
    (NOTES, 91, "stae_choir_pictures", "Sebastiano Ricci", "One of the artists included in Haskell's unnamed choir-picture group."),
    (NOTES, 91, "stae_choir_pictures", "Tiepolo", "One of the artists included in Haskell's unnamed choir-picture group."),
    (NOTES, 105, "vecchi_person", "Concina", "The note's pronoun 'him' may refer to Concina or Vecchi; no resolution at S2."),
    (NOTES, 105, "british_museum", "British Museum", "Repository in the note's ambiguous statement about works by 'him'."),
    (NOTES, 107, "benedictines", "Benedictines", "Order named in Haskell's general sentence; keep distinct from the specific Giudecca community of nuns."),
    (NOTES, 107, "benedictine_nuns", "Tiepolo", "Artist employed by the nuns; no individual work is named."),
    (NOTES, 107, "benedictine_nuns", "Pittoni", "Artist employed by the nuns; no individual work is named."),
    (NOTES, 107, "benedictine_nuns", "Ricci", "Artist employed by the nuns; no individual work is named."),
    (NOTES, 107, "benedictine_nuns", "Trevisani", "Artist employed by the nuns; no individual work is named."),
    (NOTES, 111, "luigi_modello", "S. Luigi Gonzaga", "Saint named as the modello's subject; reuse the existing candidate."),
    (NOTES, 112, "rubens_antwerp_series", "Rubens", "Painter named in the source account."),
    (P272, 59, "luigi_modello", "this", "Wilde's pronoun refers to the S. Luigi Gonzaga modello discussed in p.272 note 3."),
    (P273, 65, "penn_model", "the preliminary version", "The model object is distinct from the full-size subject painting; location supplied by note 3."),
    (NOTES, 118, "scuola_carmine", "questa Scola", "The note's Italian refers to the Scuola del Carmine."),
    (NOTES, 118, "tiepolo", "Tiepolo", "Artist named in the note's chronology."),
    (NOTES, 118, "clerici", "Palazzo Clerici", "First Milan destination as reported by Haskell; chronology does not establish abandonment of a contract."),
    (NOTES, 124, "corner", "Flaminio Corner", "Person identified as collector in the Correr manuscript quotation."),
    (NOTES, 124, "correr", "Biblioteca Correr", "Repository; reuse existing institution candidate."),
    (NOTES, 116, "pieta", "the church", "Anaphoric location of the proposed marble altar; context identifies the church as the Pietà."),
    (NOTES, 127, "gherardi", "P. E. Gherardi", "Author of the dated 1746 letter; source letter candidate is separate from the 1742 and 1745 letters."),
    (NOTES, 127, "muratori", "Muratori", "Letter addressee; retain the short form used in the note."),
    (NOTES, 126, "letterini", "Bartolommeo Letterini", "Painter named as the probable author of the altar paintings; reuse the existing person candidate."),
]
for index, (segment_id, line_no, key, surface, note) in enumerate(EXTRA_MENTIONS, 1):
    occurrence = 0
    if segment_id == NOTES and line_no == 91 and surface == "S. Stae":
        occurrence = 1
    add_mention(f"m-chp9-note-extra-{index:03d}", segment_id, line_no, candidate(key), surface, note, occurrence)


NOTE_SPECS = [
    # page, marker, source line, slice start, slice end, citation candidate keys, predicate, claim, qualification, text layer
    (268, 1, 86, "1 Thus", None, ["silhouette156"], "citation_locator", "P.268 note 1 cites Etienne de Silhouette, volume I, p.156, for the preceding account.", "Bibliographic locator only; the publication and page were not independently consulted.", "footnote source locator"),
    (268, 2, 87, "2 Tabacco", "3 Bevilacqua", ["tabacco123"], "citation_locator", "P.268 note 2 cites Tabacco, p.123.", "Short citation; title and cited page deferred to bibliography review.", "footnote source locator"),
    (268, 3, 87, "3 Bevilacqua", None, ["bevilacqua"], "citation_locator", "P.268 note 3 cites Bevilacqua, p.32.", "Reuse the existing Bevilacqua citation candidate; no independent consultation is claimed.", "footnote source locator"),
    (268, 4, 88, "4 Burney", None, ["burney140"], "citation_locator", "P.268 note 4 cites Burney, volume I, p.140.", "Short citation; title and cited page deferred to bibliography review.", "footnote source locator"),
    (268, 5, 89, "5 Coggiola", "‘NN.HH.", ["coggiola304", "ferrari1882", "benigna_memoir"], "benigna_primary_source_citation_chain", "P.268 note 5 cites Coggiola-Pittoni, Ferrari and the Biblioteca Marciana Libri di Memorie manuscript attributed to Antonio Benigna.", "These are Haskell's citation pointers. The archival manuscript and cited publications were not independently consulted; the quote that follows is handled as a separate source claim.", "footnote source locator"),
    (268, 6, 90, "8 [Girolamo Zanetti]", None, ["zanetti_may1743", "zanetti"], "zanetti_1743_observer_identification", "The note identifies the p.268-269 observer as Girolamo Zanetti and cites his 22 May 1743 report, published in 1885, p.129.", "The OCR note marker is 8; the scan shows printed note 6. This source-level attribution does not settle wider identity matching beyond this cited report.", "footnote source locator"),
    (269, 1, 91, "1 Corner", "Another parish church", ["corner163"], "corner_citation_locator", "P.269 note 1 cites Corner, p.163.", "Citation locator only; the following S. Stae supplement is recorded in separate source-level statements.", "footnote source locator"),
    (269, 2, 92, "2 L. Ferrari", None, ["ferrari1882"], "citation_locator", "P.269 note 2 cites L. Ferrari, 1882.", "Same provisional publication candidate as p.268 note 5; full identity remains for bibliography review.", "footnote source locator"),
    (269, 3, 93, "3 Bianchini", None, ["bianchini1894"], "citation_locator", "P.269 note 3 cites Bianchini, 1894, p.II.", "Short citation; title and cited page deferred to bibliography review.", "footnote source locator"),
    (269, 4, 94, "4 Pôllnitz", None, ["pollnitz"], "citation_locator", "P.269 note 4 cites Pöllnitz, volume II, p.149.", "The same volume is cited again at p.272 note 2; no independent source consultation is claimed.", "footnote source locator"),
    (269, 5, 95, "5 Risposta", None, ["scalzi_pamphlet", "ferrari1882"], "scalzi_1734_pamphlet_locator", "P.269 note 5 identifies a 32-page 1734 pamphlet by M.A., published by Luigi Pavini and held at Biblioteca Marciana, Misc.1135, no.3, cited through Ferrari 1882.", "Keep distinct from the 1762 pamphlet cited at p.272 note 1; neither pamphlet was independently consulted.", "footnote source locator"),
    (270, 1, 96, "1 Fogolari", None, ["fogolari1931"], "citation_locator", "P.270 note 1 cites Fogolari, 1931, pp.18-32.", "Citation locator only; cited pages not independently consulted.", "footnote source locator"),
    (270, 2, 97, "2 Lorenzetri", None, ["lorenzetti1956"], "citation_locator", "P.270 note 2 cites Lorenzetti, 1956, p.551.", "The source OCR reads 'Lorenzetri'; the p.270 scan reads 'Lorenzetti'. The cited page was not independently consulted.", "footnote source locator"),
    (270, 3, 98, "8 Mostra", "The picture", ["mostra_tiepolo1951"], "citation_locator", "P.270 note 3 cites Mostra del Tiepolo, 1951, p.8.", "The OCR note marker is 8; the scan shows printed note 3. The cited publication page was not independently consulted.", "footnote source locator"),
    (270, 4, 99, "4 Documents", None, ["urbani1879"], "commission_documents_published", "P.270 note 4 says documents for the commission are published by Urbani de Ghelthof, 1879, pp.100-117.", "Publication locator only; no independent reading of the cited documents is claimed.", "footnote source locator"),
    (270, 5, 100, "6 Lorenzetti", None, ["lorenzetti1956"], "citation_locator", "P.270 note 5 cites Lorenzetti, 1956, p.553.", "The OCR note marker is 6; the scan shows printed note 5. Citation locator only.", "footnote source locator"),
    (270, 6, 101, "8 Letter", None, ["marchesini_letter", "marchesini", "conti", "biblioteca_lucca", "zarzabini19"], "marchesini_letter_locator", "P.270 note 6 cites Alessandro Marchesini's letter to Stefano Conti dated 11 August 1725 in Biblioteca Governativa, Lucca, and also cites Zarzabini, p.19.", "The OCR marker 8 is printed note 6. The letter and publication pages were not independently consulted; reuse the exact existing letter candidate.", "footnote source locator"),
    (270, 7, 102, "7 [Girolamo Zanetti]", "the Dominicans", ["zanetti"], "zanetti_attribution_in_misaligned_note", "P.270 note 7 attributes the following report to Girolamo Zanetti and dates it to 1743.", "The printed marker follows a Gesuati funding sentence, while the note concerns the Dominicans. Preserve that placement/content mismatch and do not use the note as evidence for Gesuati funding.", "footnote source locator"),
    (271, 1, 103, "1 Letter", None, ["gherardi1742", "gherardi", "muratori", "biblioteca_estense"], "gherardi_1742_letter_locator", "P.271 note 1 identifies the 1742 Gesuati visitor through P. E. Gherardi's letter to Muratori dated 26 October 1742 at Biblioteca Estense, Modena.", "This is Haskell's source attribution; the letter and archive witness were not independently consulted.", "footnote source locator"),
    (271, 2, 104, "2 Arslan", None, ["arslan1932", "lorenzetti1956"], "citation_locators", "P.271 note 2 cites Arslan in Rivista di Venezia, 1932, p.19, and Lorenzetti, 1956, p.30.", "Short citation locators only; cited sources not independently consulted.", "footnote source locator"),
    (271, 3, 105, "3 For a general", "There are", ["vecchi1960", "vecchi_person"], "vecchi_citation_locator", "P.271 note 3 directs readers to Alberto Vecchi, 1960, for a general discussion of Concina's thought.", "The cited work is not independently consulted. The note's following British Museum sentence has an unresolved pronoun and is recorded separately.", "footnote source locator"),
    (271, 4, 106, "4 Tentori", None, ["tentori288"], "citation_locator", "P.271 note 4 cites Tentori, volume X, p.288.", "Short citation only; full bibliographic identity is deferred.", "footnote source locator"),
    (271, 5, 107, "5 Among patrons", "Tiepolo", ["benedictines"], "benedictines_active_patrons", "P.271 note 5 says the Benedictines were especially active patrons among the older established religious orders.", "Haskell's general characterization; the following sentence's four named artist-employment facts are recorded separately.", "substantive footnote"),
    (271, 6, 108, "6 Though", None, ["bernis_person", "bernis421", "jesuits"], "de_bernis_jesuit_credit_quote", "P.271 note 6 reports Cardinal de Bernis saying that in the 1740s the Jesuits were 'dans le plus grand crédit'.", "Nested quotation cited through volume I, p.421; retain Haskell's reporting layer and do not treat it as an independently verified assessment.", "substantive footnote"),
    (272, 1, 109, "1 Appendice", None, ["appendice1762"], "citation_locator", "P.272 note 1 cites the 1762 Appendice alla prima parte dei Monumenti Veneti in risposta alla lettera di un'uomo onesto.", "Keep this 1762 source distinct from the 1734 Scalzi pamphlet; the pamphlet was not independently consulted.", "footnote source locator"),
    (272, 2, 110, "2 See", None, ["pollnitz"], "citation_locator", "P.272 note 2 cites Pöllnitz, volume II, p.152.", "Reuses the p.269 note 4 publication candidate; the cited page was not independently consulted.", "footnote source locator"),
    (272, 3, 111, "3 [Count Seilern]", None, ["seilern1959", "seilern_person", "luigi_modello"], "seilern_catalogue_modello_ownership", "P.272 note 3 says Count Seilern's 1959 catalogue no.170 listed him as owning a modello for the Glory of S. Luigi Gonzaga.", "Catalogue attribution as reported by Haskell; the cited entry was not independently consulted. The Wilde interpretation continues at p.272 L59-60 and is recorded separately.", "substantive footnote"),
    (272, 4, 112, "4 Mâle", "It had", ["male448"], "male_citation_locator", "P.272 note 4 cites Mâle, p.448.", "Citation locator only. The following sentence describes a Rubens series, but its pronoun antecedent is unresolved and is not used to identify the preceding referent.", "footnote source locator"),
    (272, 5, 113, "5 Bosisio", None, ["bosisio"], "citation_locator", "P.272 note 5 cites Bosisio.", "The note supplies no page or title; full identity deferred to bibliography review.", "footnote source locator"),
    (272, 6, 114, "8 [Andrea Memmo]", None, ["memmo1786", "memmo"], "citation_locator", "P.272 note 6 cites Andrea Memmo, 1786, pp.4 ff.", "The OCR marker 8 is printed note 6 on the scan; citation locator only.", "footnote source locator"),
    (273, 1, 115, "1 Urbani", None, ["urbani1879"], "citation_locator", "P.273 note 1 cites Urbani de Ghelthof, pp.124-126.", "Reuses the same 1879 source cited on p.270; cited pages not independently consulted.", "footnote source locator"),
    (273, 2, 116, "—Biblioteca Correr", None, ["foscarini_will", "correr"], "foscarini_1745_will_locator", "P.273 note 2 identifies the source for the preceding bequest as Pietro Foscarini's 1745 will in Biblioteca Correr, Cod. Cicogna MMDCCCCXLV-2686.", "Reuse the exact will candidate; the will itself has not been independently consulted.", "footnote source locator"),
    (273, 3, 117, "3 The modello", None, ["penn_model", "penn_museum"], "pennsylvania_modello_location", "P.273 note 3 reports that the modello for St Philip Neri and the Virgin is in the Pennsylvania Museum.", "The preceding body refers to a preliminary version; do not identify the model with the full-size painting or with another same-subject work.", "substantive footnote"),
    (273, 4, 118, "4 See p. 270", "‘gli amorosi", [], "internal_footnote_cross_reference", "P.273 note 4 cross-references p.270 note 4 for the quoted account that follows.", "Internal source-note pointer; the pressure claim itself is recorded separately from the quoted appeal.", "footnote source locator"),
    (273, 5, 119, "5 Battistella", None, ["battistella1930"], "citation_locator", "P.273 note 5 cites Battistella, 1930, pp.38 ff.", "Short citation locator only; cited pages not independently consulted.", "footnote source locator"),
    (274, 1, 120, "1 [Girolamo Zanetti]", None, ["zanetti_mar1743", "zanetti"], "zanetti_march1743_locator", "P.274 note 1 cites Girolamo Zanetti's report of 25 March 1743, published in 1885, p.110.", "Keep this dated report distinct from the 22 May 1743 report cited at p.268 note 6.", "footnote source locator"),
    (274, 2, 121, "2 Urbani", None, ["urbani1879"], "citation_locator", "P.274 note 2 cites Urbani de Ghelthof, p.123.", "Reuses the 1879 source candidate; cited page not independently consulted.", "footnote source locator"),
    (274, 3, 122, "3 For all", None, ["costadoni_person"], "costadoni_source_scope", "P.274 note 3 identifies Don Anselmo Costadoni as the source for all that follows.", "Scope note for the ensuing p.274 account; title and independent consultation are not supplied.", "footnote source locator"),
    (274, 4, 123, "4 Casanova", None, ["casanova246"], "citation_locator", "P.274 note 4 cites Casanova, volume IV, p.246.", "Short citation only; cited page not independently consulted.", "footnote source locator"),
    (274, 5, 124, "5 Biblioteca Correr", None, ["gradenigo185_corner", "corner"], "corner_relic_collection_report", "The Correr Cod. Gradenigo 185 quotation says Flaminio Corner collected many authentic relics and could display each day's saint for veneration according to church rite.", "The note gives no folio locator. Do not conflate this source with cand-8581, a different Gradenigo manuscript with specified folios.", "substantive footnote"),
    (274, 6, 125, "6 Pallucchini", None, ["pallucchini1931"], "citation_locator", "P.274 note 6 cites Pallucchini, 1931, pp.421-432.", "Short citation locator only; cited pages not independently consulted.", "footnote source locator"),
    (275, 1, 126, "1 Don Giovanni", "It is probable", ["brustoloni1779"], "brustoloni_citation_locator", "P.275 note 1 cites Don Giovanni Domenico Brustoloni, 1779.", "The following Corner/Letterini attribution is explicitly probable and is recorded separately; Brustoloni's publication was not independently consulted.", "footnote source locator"),
    (275, 2, 127, "On 20 February 1746", ": ‘E cosa", ["gherardi1746", "gherardi", "muratori"], "gherardi_1746_letter_locator", "P.275 note 2 identifies a letter from P. E. Gherardi to Muratori dated 20 February 1746 in Biblioteca Estense, Modena.", "The letter is cited by Haskell but was not independently consulted; its complaint is recorded separately and continues at p.275 L83.", "footnote source locator"),
]


def note_id(page, marker):
    return f"st-chp9-p{page}-n{marker:02d}"


def extract_quote(line_no, start_token, end_token=None):
    line = source_lines[line_no - 1]
    start = line.find(start_token)
    if start < 0:
        raise SystemExit(f"quote start missing on L{line_no}: {start_token!r}")
    end = len(line) if end_token is None else line.find(end_token, start + len(start_token))
    if end < 0:
        raise SystemExit(f"quote end missing on L{line_no}: {end_token!r}")
    quote = line[start:end].strip()
    if not quote or quote not in line:
        raise SystemExit(f"invalid quote on L{line_no}")
    return quote


def statement_source_meta(segment_id, line_no):
    meta = segments[segment_id]
    if not meta["line_start"] <= line_no <= meta["line_end"]:
        raise SystemExit(f"L{line_no} falls outside {segment_id}")
    return meta


NOTE_CORRECTIONS = {
    (268, 5): [
        {"source_file": str(SOURCE.relative_to(ROOT)).replace("\\", "/"), "source_line": 89, "ocr": "Itai.", "print": "Ital.", "basis": "CHP-9.pdf physical page 34."},
        {"source_file": str(SOURCE.relative_to(ROOT)).replace("\\", "/"), "source_line": 89, "ocr": "[of the Jesuit Chuch]", "print": "[of the Jesuit Church]", "basis": "CHP-9.pdf physical page 34; bracketed wording is Haskell's editorial insertion."},
        {"source_file": str(SOURCE.relative_to(ROOT)).replace("\\", "/"), "source_line": 89, "ocr": "193 5", "print": "1935", "basis": "CHP-9.pdf physical page 34."},
    ],
    (268, 6): [{"source_file": str(SOURCE.relative_to(ROOT)).replace("\\", "/"), "source_line": 90, "ocr": "8", "print": "6", "basis": "CHP-9.pdf physical page 34."}],
    (270, 2): [{"source_file": str(SOURCE.relative_to(ROOT)).replace("\\", "/"), "source_line": 97, "ocr": "Lorenzetri", "print": "Lorenzetti", "basis": "CHP-9.pdf physical page 36."}],
    (270, 3): [{"source_file": str(SOURCE.relative_to(ROOT)).replace("\\", "/"), "source_line": 98, "ocr": "8", "print": "3", "basis": "CHP-9.pdf physical page 36."}],
    (270, 5): [{"source_file": str(SOURCE.relative_to(ROOT)).replace("\\", "/"), "source_line": 100, "ocr": "6", "print": "5", "basis": "CHP-9.pdf physical page 36."}],
    (270, 6): [{"source_file": str(SOURCE.relative_to(ROOT)).replace("\\", "/"), "source_line": 101, "ocr": "8", "print": "6", "basis": "CHP-9.pdf physical page 36."}],
    (271, 3): [{"source_file": str(SOURCE.relative_to(ROOT)).replace("\\", "/"), "source_line": 105, "ocr": "i960", "print": "1960", "basis": "CHP-9.pdf physical page 37."}],
    (271, 5): [{"source_file": str(SOURCE.relative_to(ROOT)).replace("\\", "/"), "source_line": 107, "ocr": "alia Giudecca", "print": "alla Giudecca", "basis": "CHP-9.pdf physical page 37."}],
    (272, 6): [{"source_file": str(SOURCE.relative_to(ROOT)).replace("\\", "/"), "source_line": 114, "ocr": "8", "print": "6", "basis": "CHP-9.pdf physical page 38."}],
}


SUPPLEMENTAL_SPECS = [
    # suffix, source segment, page, marker, line, quote start/end, subject key, object key,
    # predicate, claim, qualification, mentioned keys, speaker, text layer, relation candidate
    ("silhouette-piety-rhetoric", NOTES, 268, 1, 86, "‘Si le grand nombre", None, None, "silhouette156", "quoted_characterization", "Silhouette's quoted French remark says the number and magnificence of churches do not prove piety but at least show a wish to appear pious.", "Nested quotation reproduced by Haskell; the cited publication page has not been consulted, and this is the quoted author's characterization.", ["silhouette156"], "Etienne de Silhouette as quoted by Haskell", "nested quotation in footnote", False),
    ("benigna-manini-high-altar", NOTES, 268, 5, 89, "‘NN.HH.", "tutta la Incrostradura", "manini_brothers", "venetian_jesuit_church", "manini_group_paid_for_jesuit_church_high_altar", "The 1729 Benigna entry says the abbreviated Manini brothers had the Jesuit church's high altar erected at their own expense.", "Haskell's bracketed church name is editorial; preserve the abbreviated brothers' names and do not identify them with the Manin family. The manuscript was not independently inspected.", ["benigna_memoir", "benigna_person", "manini_brothers", "venetian_jesuit_church"], "Antonio Benigna's Libri di Memorie as quoted by Haskell", "nested manuscript quotation", True),
    ("benigna-church-decoration-list", NOTES, 268, 5, 89, "tutta la Incrostradura", None, "manini_brothers", "venetian_jesuit_church", "benigna_lists_church_marble_organs_oratories_pavement_ceiling_and_facade", "The Benigna entry lists antique-green marble cladding, organs, oratories, pavement, a gilded stucco ceiling and the exterior façade among works paid for in connection with the church.", "Retain the source's abbreviated Italian list and the uncertainty in its OCR; the manuscript was not independently consulted.", ["benigna_memoir", "manini_brothers", "venetian_jesuit_church"], "Antonio Benigna's Libri di Memorie as quoted by Haskell", "nested manuscript quotation", True),
    ("stae-facade-mocenigo-legacy", NOTES, 269, 1, 91, "Another parish church", "while a bourgeois", "mocenigo", "stae_facade", "alvise_mocenigo_legacy_funded_stae_facade_1709", "Haskell's note says S. Stae received a façade in 1709 from the proceeds of Doge Alvise Mocenigo's legacy.", "A report in Haskell's note; the cited Corner page and underlying records were not independently consulted.", ["stae_church", "stae_facade", "mocenigo"], "Haskell's footnote", "substantive footnote claim", True),
    ("stazio-bequest", NOTES, 269, 1, 91, "while a bourgeois", "Some of this", "stazio", "stae_church", "stazio_left_nearly_200_ducats_for_stae_building_and_decoration", "Andrea Stazio reportedly left nearly 200 ducats for further building and decoration at S. Stae.", "Haskell gives an approximate amount and does not specify the later distribution of the bequest.", ["stae_church", "stazio"], "Haskell's footnote", "substantive footnote claim", True),
    ("stae-choir-pictures", NOTES, 269, 1, 91, "Some of this", "Unfortunately", "stae_church", "stae_choir_pictures", "stazio_bequest_partly_spent_on_choir_pictures_by_three_named_artists", "Haskell says some of Stazio's bequest was spent on unidentified choir pictures by a group including Piazzetta, Sebastiano Ricci and Tiepolo.", "No individual picture titles or separate artist-to-work assignments are given.", ["stae_church", "stae_choir_pictures", "piazzetta", "ricci", "tiepolo", "stazio"], "Haskell's footnote", "substantive footnote claim", True),
    ("stazio-will-no-commissioner", NOTES, 269, 1, 91, "Unfortunately, Stazio’s will", None, "stazio_will", "stae_choir_pictures", "stazio_will_does_not_name_the_choir_picture_commissioners", "Haskell says the cited will gives no information about who commissioned the choir pictures.", "A statement about what the cited will does not specify; do not infer that Stazio commissioned the works. The manuscript was not independently consulted.", ["stazio_will", "stae_choir_pictures", "archivio_venezia"], "Haskell's footnote", "substantive footnote claim", False),
    ("zanetti-dominican-alms", NOTES, 270, 7, 102, "the Dominicans", "It had been begun", "dominicans", "dominican_zattere_church", "zanetti_reported_dominicans_still_collecting_alms_for_their_church", "Zanetti reportedly wrote in 1743 that the Dominicans were still collecting alms throughout the day for their church.", "The note is physically attached to the preceding Gesuati public-funding sentence but its content concerns the Dominicans; do not treat it as evidence for Gesuati funding.", ["zanetti", "dominicans", "dominican_zattere_church", "benigna_memoir"], "Girolamo Zanetti as cited by Haskell", "substantive footnote claim", True),
    ("benigna-dominican-church-model", P270, 270, 7, 36, "Cl. VII", None, "dominicans", "dominican_zattere_church", "benigna_1725_dominican_church_demolition_and_redentore_model_report", "The quoted Benigna entry reports that Observant Dominicans on the Zattere began demolishing part of their convent and building a new church on the model of the Redentore.", "This is the continuation of the misaligned printed note 7, not evidence for the Gesuati church. The source reports the building activity as begun in 1725; authorship or a direct architectural lineage is not inferred.", ["benigna_memoir", "benigna_person", "dominicans", "dominican_zattere_church", "redentore_church"], "Antonio Benigna as quoted in the Zanetti source cited by Haskell", "footnote continuation", True),
    ("vecchi-ambiguous-british-museum-works", NOTES, 271, 3, 105, "There are", None, None, "british_museum", "works_by_ambiguous_him_reported_in_british_museum", "The note reports a large number of works by 'him' in the British Museum, but the pronoun's antecedent is unresolved between Concina and Alberto Vecchi.", "Do not assign the works to either person; the statement is not independently verified against a museum catalogue.", ["vecchi_person", "vecchi1960", "british_museum"], "Haskell's footnote", "substantive footnote claim", False),
    ("madonna-brera-location", NOTES, 270, 3, 98, "The picture", None, "madonna_carmelo", "brera", "madonna_del_carmelo_reported_now_in_brera", "P.270 note 3 says the Madonna del Carmelo is now in the Brera.", "The anaphoric 'The picture' refers to the work named in p.270 L31. This is Haskell's report, not independent verification of the present location.", ["madonna_carmelo", "brera", "mostra_tiepolo1951"], "Haskell's footnote", "substantive footnote claim", True),
    ("foscarini-will-marble-altar-bequest", NOTES, 273, 2, 116, "For instance, Pietro Foscarini", "—Biblioteca Correr", "foscarini", "pieta", "foscarini_1745_will_left_funds_for_fine_marble_altar", "Pietro Foscarini's 1745 will reportedly left money for a fine marble altar to be erected in the church.", "The will supplies no amount in this passage; preserve 'left money' and do not infer a completed altar. Reuse the exact cited will candidate.", ["foscarini", "foscarini_will", "pieta", "correr"], "Haskell's footnote", "substantive footnote claim", True),
    ("carmine-confratelli-pressure-quote", NOTES, 273, 4, 118, "‘gli amorosi", "None the less", "scuola_carmine", "tiepolo", "carmine_confratelli_urged_tiepolo_to_leave_milan_engagement_and_accept_scuola_work", "The quoted Carmine confratelli urged Tiepolo to leave his Milan engagement and accept the Scuola work.", "Reported pressure only; the passage does not establish an abandoned contract or that Tiepolo accepted at this point.", ["scuola_carmine", "tiepolo"], "Carmine confratelli as quoted by Haskell", "nested Italian quotation in footnote", True),
    ("probable-letterini-corner-commission", NOTES, 275, 1, 126, "It is probable", None, "corner", "letterini_paintings", "probable_corner_commission_of_letterini_altar_paintings", "Haskell says it is probable that Flaminio Corner also commissioned sentimental altar paintings by Bartolommeo Letterini.", "Preserve 'probable'; no titles, dates or locations are supplied. Keep these works distinct from Angeli's altar works on p.274.", ["corner", "letterini", "letterini_paintings"], "Haskell's footnote", "substantive footnote claim", True),
    ("wilde-modello-canonization-hypothesis", P272, 272, 3, 59, "Professor Wilde", "There is certainly no evidence", "luigi_modello", "unexecuted_luigi_altarpiece", "wilde_tentatively_interprets_modello_as_canonization_altarpiece_sketch", "Wilde suggests very plausibly that the modello was made for the saint's 1726 canonization and probably intended as a sketch for an altarpiece that was never carried out.", "Preserve Haskell's reported 'very plausibly' and 'probably'; this is an attributed hypothesis, not an established purpose or commission.", ["wilde_person", "wilde1960", "luigi_modello", "unexecuted_luigi_altarpiece"], "Professor Wilde as cited by Haskell", "footnote continuation", True),
    ("wilde-no-venice-evidence", P272, 272, 3, 59, "There is certainly no evidence", None, "unexecuted_luigi_altarpiece", "venetian_jesuit_church", "no_evidence_planned_altarpiece_was_for_venetian_jesuit_church", "The note says there is no evidence that the proposed altarpiece, if actually planned, was for the Jesuit church in Venice.", "Preserve the source's evidential limit; absence of evidence here does not establish that another venue was intended.", ["luigi_modello", "unexecuted_luigi_altarpiece", "venetian_jesuit_church"], "Haskell's footnote continuation", "footnote continuation", False),
    ("rubens-antwerp-series", NOTES, 272, 4, 112, "It had", None, "rubens", "rubens_antwerp_series", "rubens_painted_old_testament_series_for_antwerp_jesuit_church", "The note says Rubens painted a series of Old Testament scenes for the Jesuit Church at Antwerp and characterizes the scenes as prefiguring the Life of Christ.", "The antecedent of 'It' remains unresolved; this statement does not identify the preceding note's referent with the Rubens series.", ["male448", "rubens", "rubens_antwerp_series", "antwerp_jesuit_church"], "Haskell's footnote", "substantive footnote claim", True),
    ("carmine-chronology-palazzo-clerici", NOTES, 273, 4, 118, "None the less", None, "tiepolo", "clerici", "tiepolo_went_to_milan_first_to_decorate_palazzo_clerici", "Haskell says that despite the confratelli's appeal, Tiepolo went to Milan first to decorate Palazzo Clerici.", "Preserve sequence without inferring that Tiepolo abandoned a contract or declined the Scuola commission.", ["tiepolo", "clerici", "scuola_carmine"], "Haskell's footnote", "substantive footnote claim", True),
    ("gherardi-church-decoration-complaint", NOTES, 275, 2, 127, "‘E cosa", None, "gherardi1746", "virgin", "gherardi_1746_complained_of_excessive_church_decoration", "In the letter quoted by Haskell, Gherardi calls it ridiculous to see altars with painted saints surrounded by small saint statuettes, as in a child's altar.", "This is Gherardi's reported complaint, not an independent assessment of Venetian churches; the quote continues at p.275 L83.", ["gherardi1746", "gherardi", "muratori", "virgin"], "P. E. Gherardi as quoted by Haskell", "nested letter quotation", False),
]


note_page_by_key = {(page, marker): line_no for page, marker, line_no, *_ in NOTE_SPECS}
if len(note_page_by_key) != len(NOTE_SPECS):
    raise SystemExit("duplicate printed page/footnote number in NOTE_SPECS")
note_id_by_key = {key: note_id(*key) for key in note_page_by_key}
body_links = {key: [] for key in note_page_by_key}
body_target_override = {
    "st-chp9-p270-1742-visitor-description-partial": (271, 1),
    "st-chp9-p269-1743-observer-complaint-continuation": (268, 6),
}


def marker_list(qualifiers):
    values = qualifiers.get("footnote_markers")
    if values is None:
        marker = qualifiers.get("footnote_marker")
        values = [] if marker is None else [marker]
    elif not isinstance(values, list):
        values = [values]
    return [int(value) for value in values if str(value).isdigit()]


for row in statements:
    if not row.get("segment_id", "").startswith("chp-9:09_CHP-9_sec_ii:") or row.get("segment_id") == NOTES:
        continue
    q = row.get("qualifiers", {})
    if str(q.get("text_layer", "")).startswith("footnote"):
        continue
    page = q.get("printed_page", q.get("print_page"))
    if page is None or not marker_list(q):
        continue
    page = int(page)
    if page < 268 or page > 275:
        continue
    for marker in marker_list(q):
        key = body_target_override.get(row["statement_id"], (page, marker))
        if key not in body_links:
            raise SystemExit(f"body footnote has no source note: {row['statement_id']} -> {key}")
        if row["statement_id"] not in body_links[key]:
            body_links[key].append(row["statement_id"])


new_statements = []
statement_ids_by_note = {key: [note_id_by_key[key]] for key in note_page_by_key}


def make_note_statement(statement_id, segment_id, page, marker, line_start, line_end, quote,
                        subject_key, object_key, predicate, claim, qualification,
                        mentioned_keys, speaker="Haskell's footnote", text_layer="substantive footnote",
                        relation_candidate=False, extra=None, note_key=None, link_body=True):
    statement_source_meta(segment_id, line_start)
    statement_source_meta(segment_id, line_end)
    relevant = source_lines[line_start - 1:line_end]
    if quote not in "\n".join(relevant):
        raise SystemExit(f"quote is not reproduced in source range: {statement_id}")
    key = note_key or (page, marker)
    q = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": page,
        "pdf_physical_page": page - 234,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": [candidate(k) for k in mentioned_keys],
        "footnote_marker": marker,
        "footnote_segment": NOTES,
        "footnote_body_link_status": "mismatched" if key == (270, 7) else ("linked" if body_links.get(key) else "unlinked"),
        "related_segment": NOTES if segment_id != NOTES else None,
    }
    if q["related_segment"] is None:
        q.pop("related_segment")
    if link_body and body_links.get(key):
        q["linked_body_statement_ids"] = list(body_links[key])
    if relation_candidate:
        q["relation_candidate"] = True
    if extra:
        q.update(extra)
    row = {
        "statement_id": statement_id,
        "segment_id": segment_id,
        "subject_candidate_id": None if subject_key is None else candidate(subject_key),
        "object_candidate_id": None if object_key is None else candidate(object_key),
        "predicate": predicate,
        "qualifiers": q,
        "original_quote": quote,
        "source_file": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "origin": "book",
    }
    new_statements.append(row)
    if key in statement_ids_by_note and statement_id != note_id_by_key[key]:
        statement_ids_by_note[key].append(statement_id)
    return row


NOTE_ENDPOINTS = {
    (272, 3): ("seilern_person", "luigi_modello"),
    (273, 3): ("penn_model", "penn_museum"),
    (274, 5): ("corner", None),
}


for page, marker, line_no, start_token, end_token, citation_keys, predicate, claim, qualification, text_layer in NOTE_SPECS:
    key = (page, marker)
    quote = extract_quote(line_no, start_token, end_token)
    main_candidate = citation_keys[0] if citation_keys else None
    actual_layer = "footnote source locator" if "locator" in text_layer or "citation" in text_layer else text_layer
    extra = {"ocr_corrections": NOTE_CORRECTIONS[key]} if key in NOTE_CORRECTIONS else {}
    if key == (270, 7):
        extra.update({"marker_content_mismatch": True, "mismatch_note": "Printed marker follows the Gesuati public-funding sentence; the note's text concerns Dominican church building."})
    if key == (275, 2):
        extra.update({"cross_reference_segments": [{"segment_id": P275, "source_line_start": 83, "source_line_end": 83}], "continued_by_statement_ids": ["st-chp9-p275-gerardi-madonna-complaint-tail", "st-chp9-p275-n02-haskell-commentary-tail"]})
    if key == (272, 3):
        extra.update({"cross_reference_segments": [{"segment_id": P272, "source_line_start": 59, "source_line_end": 60}], "continued_by_statement_ids": ["st-chp9-p272-n03-wilde-modello-canonization-hypothesis", "st-chp9-p272-n03-wilde-no-venice-evidence"]})
    subject_key, object_key = NOTE_ENDPOINTS.get(key, (None, main_candidate))
    make_note_statement(
        note_id(page, marker), NOTES, page, marker, line_no, line_no, quote,
        subject_key, object_key, predicate, claim, qualification, citation_keys,
        speaker="Haskell's footnote", text_layer=actual_layer,
        extra=extra, note_key=key,
    )


for (suffix, segment_id, page, marker, line_no, start_token, end_token, subject_key, object_key,
     predicate, claim, qualification, mentioned_keys, speaker, text_layer, relation_candidate) in SUPPLEMENTAL_SPECS:
    key = (page, marker)
    quote = extract_quote(line_no, start_token, end_token)
    line_end = line_no
    if suffix == "wilde-no-venice-evidence":
        quote = quote.rstrip() + "\n" + source_lines[59]
        line_end = 60
    extra = {}
    if key == (270, 7):
        extra["marker_content_mismatch"] = True
        extra["related_statement_ids"] = [note_id(270, 7)]
    if segment_id != NOTES:
        extra["cross_reference_segments"] = [{"segment_id": NOTES, "source_line_start": note_page_by_key[key], "source_line_end": note_page_by_key[key]}]
        extra["continuation_of_statement_id"] = note_id(*key)
    if suffix == "gherardi-church-decoration-complaint":
        extra["cross_reference_segments"] = [{"segment_id": P275, "source_line_start": 83, "source_line_end": 83}]
        extra["continued_by_statement_ids"] = ["st-chp9-p275-gerardi-madonna-complaint-tail"]
    make_note_statement(
        f"st-chp9-p{page}-n{marker:02d}-{suffix}", segment_id, page, marker,
        line_no, line_end, quote, subject_key, object_key, predicate, claim,
        qualification, mentioned_keys, speaker=speaker, text_layer=text_layer,
        relation_candidate=relation_candidate, extra=extra, note_key=key,
        link_body=key != (270, 7),
    )


# The four named nuns' employment relations remain separate claims.
artist_employment_quote = extract_quote(107, "Tiepolo", None)
for artist_key, artist_name in [("tiepolo", "Tiepolo"), ("pittoni", "Pittoni"), ("ricci", "Ricci"), ("trevisani", "Trevisani")]:
    make_note_statement(
        f"st-chp9-p271-n05-nuns-employed-{artist_key}", NOTES, 271, 5, 107, 107,
        artist_employment_quote, "benedictine_nuns", artist_key,
        "employed_painter_for_nuns_of_ss_cosma_and_damiano",
        f"Haskell says the nuns of SS. Cosma e Damiano alla Giudecca employed {artist_name}.",
        "No individual work, date or commission is named; the specific painter-to-institution employment is retained without inferring a particular commission.",
        ["benedictine_nuns", artist_key], relation_candidate=True,
        extra={"time": "unspecified", "work_candidate_id": None}, note_key=(271, 5),
    )


# Source statement split at p.275 L83: Gherardi's quoted complaint and Haskell's evaluation are separate layers.
tail_original = next(row for row in statements if row["statement_id"] == "st-chp9-p275-gerardi-madonna-complaint-tail")
tail_q = tail_original["qualifiers"]
tail_quote = tail_original["original_quote"]
commentary = "The complaint is still more valid today than it was two hundred years ago."
if commentary not in tail_quote or tail_original["segment_id"] != P275:
    raise SystemExit("expected p.275 footnote continuation statement has changed")
gherardi_tail_quote = tail_quote[:tail_quote.index(" The complaint is still more valid today")].rstrip()
tail_q.update({
    "claim": "The continuation of Gherardi's quoted letter says Venetian churches displayed multiple Madonna images on an altar and a smaller image on a bench.",
    "speaker": "P. E. Gherardi as quoted by Haskell",
    "text_layer": "footnote continuation",
    "qualification": "This is the continuation of the 20 February 1746 letter quoted in p.275 note 2; it is not body prose. The Italian source is represented as transcribed by Haskell.",
    "footnote_marker": 2,
    "footnote_text_pending": False,
    "footnote_segment": NOTES,
    "footnote_body_link_status": "linked",
    "footnote_statement_ids": [note_id(275, 2), "st-chp9-p275-n02-gherardi-church-decoration-complaint"],
    "continuation_of_statement_id": "st-chp9-p275-n02-gherardi-church-decoration-complaint",
})
tail_original["original_quote"] = gherardi_tail_quote
statement_ids_by_note[(275, 2)].append("st-chp9-p275-gerardi-madonna-complaint-tail")

comment_start = source_lines[82].find(commentary)
if comment_start < 0:
    raise SystemExit("Haskell's p.275 commentary tail not found in source line 83")
make_note_statement(
    "st-chp9-p275-n02-haskell-commentary-tail", P275, 275, 2, 83, 83,
    commentary, None, None, "haskell_says_gherardi_complaint_remains_valid",
    "Haskell comments that Gherardi's complaint was even more valid in his own day than it had been two centuries earlier.",
    "Keep this authorial evaluation separate from the quoted 1746 letter; it is Haskell's commentary, not Gherardi's statement.",
    ["gherardi1746"], speaker="Haskell", text_layer="footnote commentary continuation",
    extra={"cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 127, "source_line_end": 127}], "continuation_of_statement_id": "st-chp9-p275-n02"},
    note_key=(275, 2),
)


planned_statement_ids = {row["statement_id"] for row in new_statements}
if len(planned_statement_ids) != len(new_statements) or statement_ids & planned_statement_ids:
    raise SystemExit("planned statement IDs collide")
for row in new_statements:
    q = row["qualifiers"]
    candidate_refs = [row.get("subject_candidate_id"), row.get("object_candidate_id"), *q.get("mentioned_candidate_ids", [])]
    if not set(candidate_refs) - {None} <= candidate_ids:
        raise SystemExit(f"statement has unknown candidate FK: {row['statement_id']}")
    if not row.get("predicate") or not row.get("original_quote"):
        raise SystemExit(f"statement is missing predicate or quote: {row['statement_id']}")


# Repoint only the two already indexed Madonna del Carmelo mentions to the new work candidate.
mention_reassignments = {
    "m-chp9-p270-madonna-del-carmelo": ("cand-2596", candidate("madonna_carmelo")),
    "m-chp9-p273-madonna": ("cand-2596", candidate("madonna_carmelo")),
}
mentions_by_id = {row["mention_id"]: row for row in mentions}
for mention_id, (old_id, new_id) in mention_reassignments.items():
    row = mentions_by_id.get(mention_id)
    if row is None or row["candidate_id"] != old_id:
        raise SystemExit(f"expected Madonna mention mapping changed: {mention_id}")


def replace_candidate(values, old_id, new_id):
    return list(dict.fromkeys(new_id if value == old_id else value for value in values))


body_updates = {}
body_update_ids = {
    row["statement_id"] for row in statements
    if row.get("segment_id", "").startswith("chp-9:09_CHP-9_sec_ii:")
    and row.get("segment_id") != NOTES
    and not str(row.get("qualifiers", {}).get("text_layer", "")).startswith("footnote")
    and int(row.get("qualifiers", {}).get("printed_page", row.get("qualifiers", {}).get("print_page", 0)) or 0) in range(268, 276)
    and marker_list(row.get("qualifiers", {}))
} | {
    "st-chp9-p270-tiepolo-madonna-del-carmelo",
    "st-chp9-p273-tiepolo-madonna-omits-purgatorial-fires",
    "st-chp9-p270-1742-visitor-description-partial",
    "st-chp9-p271-visitor-church-description-continuation",
    "st-chp9-p271-visitor-alms-funding",
    "st-chp9-p268-observer-complaint-partial",
    "st-chp9-p269-1743-observer-complaint-continuation",
    "st-chp9-p275-gerardi-madonna-complaint-tail",
}
body_rows = {row["statement_id"]: row for row in statements}
if not body_update_ids <= set(body_rows):
    raise SystemExit(f"expected body statements missing: {sorted(body_update_ids - set(body_rows))}")
for statement_id in body_update_ids:
    body_updates[statement_id] = json.loads(json.dumps(body_rows[statement_id], ensure_ascii=False))

work_id = candidate("madonna_carmelo")
for statement_id in ["st-chp9-p270-tiepolo-madonna-del-carmelo", "st-chp9-p273-tiepolo-madonna-omits-purgatorial-fires"]:
    row = body_updates[statement_id]
    q = row["qualifiers"]
    q["mentioned_candidate_ids"] = replace_candidate(q.get("mentioned_candidate_ids", []), "cand-2596", work_id)
    if statement_id == "st-chp9-p270-tiepolo-madonna-del-carmelo":
        if row["object_candidate_id"] != "cand-2596":
            raise SystemExit("p.270 Madonna statement no longer has the expected wrong work candidate")
        row["object_candidate_id"] = work_id
        q["qualification"] = "Retain 'about 1720'; the exact chapel is unnamed. The named work is now separate from the Tiepolo index candidate; note 3 reports a Brera location but is not independent verification."
    else:
        if row["subject_candidate_id"] != "cand-2596":
            raise SystemExit("p.273 Madonna statement no longer has the expected wrong subject candidate")
        row["subject_candidate_id"] = work_id


visitor_claims = {
    "st-chp9-p270-1742-visitor-description-partial": "Haskell's p.270 quotation begins P. E. Gherardi's 1742 description of the Gesuati church; note 1 identifies his 26 October letter to Muratori as the source.",
    "st-chp9-p271-visitor-church-description-continuation": "The description attributed by Haskell to P. E. Gherardi continues with the Gesuati church's decoration, proportions and marble altars.",
    "st-chp9-p271-visitor-alms-funding": "In the 1742 description identified with his letter, Gherardi reports that the church's 120,000 ducats had come entirely from alms.",
}
for statement_id, claim in visitor_claims.items():
    row = body_updates[statement_id]
    q = row["qualifiers"]
    q["speaker"] = "P. E. Gherardi as identified in Haskell's note 1"
    q["claim"] = claim
    q["mentioned_candidate_ids"] = list(dict.fromkeys([*q.get("mentioned_candidate_ids", []), candidate("gherardi")]))
    q["qualification"] = "Haskell identifies the quoted account through Gherardi's 26 October 1742 letter to Muratori; the letter itself has not been independently consulted."


zanetti_claims = {
    "st-chp9-p268-observer-complaint-partial": "Haskell's p.268 quotation begins Girolamo Zanetti's reported complaint about the sums religious communities could raise for church building.",
    "st-chp9-p269-1743-observer-complaint-continuation": "The account attributed by Haskell to Girolamo Zanetti continues by contrasting monastic church funds with parish support and long waits.",
}
for statement_id, claim in zanetti_claims.items():
    row = body_updates[statement_id]
    q = row["qualifiers"]
    q["speaker"] = "Girolamo Zanetti as identified in Haskell's note 6"
    q["claim"] = claim
    q["mentioned_candidate_ids"] = list(dict.fromkeys([*q.get("mentioned_candidate_ids", []), candidate("zanetti")]))
    q["qualification"] = "Haskell's note identifies the observer as Girolamo Zanetti and cites the 22 May 1743 report; that cited source has not been independently consulted."


# Preserve the p.270 note 7 marker but explicitly record that its footnote text is misattached.
for statement_id in ["st-chp9-p270-gesuati-new-church-public-funding", "st-chp9-p270-gesuati-emphasized-public-support"]:
    row = body_rows[statement_id]
    if row.get("qualifiers", {}).get("footnote_marker") != 7:
        raise SystemExit(f"expected p.270 printed marker 7 changed: {statement_id}")
    row = json.loads(json.dumps(row, ensure_ascii=False))
    q = row["qualifiers"]
    q["footnote_text_pending"] = False
    q["footnote_segment"] = NOTES
    q["footnote_refs"] = [{"marker": 7, "segment_id": NOTES, "source_line": 102}]
    q["footnote_statement_ids"] = []
    q["footnote_body_link_status"] = "mismatched"
    q["footnote_body_link_note"] = "Printed note 7 concerns the Dominicans and does not support this Gesuati funding claim."
    body_updates[statement_id] = row


# Correct the OCR's note number after Canaletto in the p.270 body quote.
pedozzi_id = "st-chp9-p270-pedozzi-reputation-and-canaletto-patron"
pedozzi = body_rows[pedozzi_id]
pedozzi_updated = json.loads(json.dumps(pedozzi, ensure_ascii=False))
pedozzi_q = pedozzi_updated["qualifiers"]
pedozzi_q.setdefault("ocr_corrections", []).append({
    "source_file": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
    "source_line": 34, "ocr": "Canaletto.8", "print": "Canaletto.6",
    "basis": "CHP-9.pdf physical page 36; the note identifies the Marchesini letter.",
})
body_updates[pedozzi_id] = pedozzi_updated


# Attach each numbered note statement to its body marker and resolve pending footnote state.
note_statement_ids_by_key = {key: statement_ids_by_note[key] for key in statement_ids_by_note}
for row in body_updates.values():
    q = row.get("qualifiers", {})
    if row["statement_id"] in {"st-chp9-p270-gesuati-new-church-public-funding", "st-chp9-p270-gesuati-emphasized-public-support"}:
        continue
    page = int(q.get("printed_page", q.get("print_page", 0)) or 0)
    marker_values = marker_list(q)
    if row["statement_id"] in body_target_override:
        page, marker = body_target_override[row["statement_id"]]
        marker_values = [marker]
    if not marker_values:
        continue
    q["footnote_segment"] = NOTES
    refs = q.setdefault("footnote_refs", [])
    for marker in marker_values:
        key = (page, marker)
        note_source_line = note_page_by_key[key]
        ref = {"marker": marker, "segment_id": NOTES, "source_line": note_source_line}
        if ref not in refs:
            refs.append(ref)
    q["footnote_statement_ids"] = list(dict.fromkeys(
        statement_id for marker in marker_values for statement_id in note_statement_ids_by_key[(page, marker)]
    ))
    q["footnote_text_pending"] = False
    if "footnote_pending" in q:
        q["footnote_pending"] = False
    q["footnote_body_link_status"] = "linked"


# Keep the split p.275 continuation linked to its source note after separating the commentary.
tail_row = body_updates["st-chp9-p275-gerardi-madonna-complaint-tail"]
tail_row["qualifiers"]["footnote_refs"] = [{"marker": 2, "segment_id": NOTES, "source_line": 127}]
tail_row["qualifiers"]["related_statement_ids"] = [note_id(275, 2), "st-chp9-p275-n02-gherardi-church-decoration-complaint"]


planned_mention_ids = {row["mention_id"] for row in new_mentions}
if len(planned_mention_ids) != len(new_mentions) or mention_ids & planned_mention_ids:
    raise SystemExit("planned mention IDs collide")
for row in new_mentions:
    if row["candidate_id"] not in candidate_ids:
        raise SystemExit(f"mention has unknown candidate: {row['mention_id']} -> {row['candidate_id']}")


updated_notes = []
for row in coverage:
    if row["segment_id"] == NOTES:
        row = dict(row)
        row.update({
            "disposition": "reviewed",
            "migration_status": "complete",
            "source_line_ranges": "L86-127",
            "note": "Consolidated p.268-275 notes read against scans and migrated. Includes the p.270 L36 note 7 continuation, p.272 L59-60 note 3 continuation and p.275 L83 note 2 continuation; p.270 printed note 7 is preserved as a marker/content mismatch and is not used as Gesuati evidence. Bibliographic locators remain distinct from independent verification.",
        })
        updated_notes.append(row)
    elif row["segment_id"] == P270:
        row = dict(row)
        row.update({
            "disposition": "reviewed",
            "migration_status": "complete",
            "source_line_ranges": "L28-36",
            "note": "Printed p.270 body L28-35 and its footnote 7 continuation at L36 are semantically processed. The visitor quotation is identified through p.271 note 1; printed p.270 note 7 remains physically attached to the Gesuati funding sentence but textually concerns the Dominicans, so it is not used as Gesuati evidence.",
        })
        updated_notes.append(row)
    elif row["segment_id"] == P272:
        row = dict(row)
        row["source_line_ranges"] = "L54-60"
        row["note"] = "Printed p.272 body L54-58 and the p.272 L59-60 continuation of printed note 3 are both processed. Note 3 preserves Seilern's reported modello ownership, Wilde's tentative canonization/altarpiece interpretation and the explicit absence of evidence for a Venetian Jesuit destination; p.272 L58 continues into p.273 L63."
        updated_notes.append(row)
    else:
        updated_notes.append(row)
coverage = updated_notes


def verify_plan():
    expected_updated = {NOTES, P270, P272}
    if not expected_updated <= {row["segment_id"] for row in coverage}:
        raise SystemExit("coverage update is incomplete")
    for mention_id, (old_id, new_id) in mention_reassignments.items():
        if mentions_by_id[mention_id]["candidate_id"] != old_id or new_id not in candidate_ids:
            raise SystemExit(f"invalid mention reassignment plan: {mention_id}")
    for row in new_statements:
        start, end = int(row["qualifiers"]["source_line_start"]), int(row["qualifiers"]["source_line_end"])
        if row["original_quote"] not in "\n".join(source_lines[start - 1:end]):
            raise SystemExit(f"quote verification failed: {row['statement_id']}")
    for statement_id, row in body_updates.items():
        start, end = int(row["qualifiers"]["source_line_start"]), int(row["qualifiers"]["source_line_end"])
        if row["original_quote"] not in "\n".join(source_lines[start - 1:end]):
            raise SystemExit(f"updated body quote verification failed: {statement_id}")
    if len(new_candidates) != len(CANDIDATE_SPECS):
        raise SystemExit("candidate count does not match specifications")
    if len(statement_ids_by_note) != len(NOTE_SPECS):
        raise SystemExit("one or more footnote numbers lack a note record")


verify_plan()


def preview():
    print(f"source sha256: {hashlib.sha256(source_bytes).hexdigest()}")
    print(f"consolidated note segment sha256: {NOTES_SHA}")
    print(f"new candidates: {len(new_candidates)} ({new_candidates[0]['candidate_id']}–{new_candidates[-1]['candidate_id']})")
    print(f"new exact mentions: {len(new_mentions)}")
    print(f"reassigned existing mentions: {len(mention_reassignments)}")
    print(f"new note statements: {len(new_statements)}")
    print(f"updated existing body statements: {len(body_updates)}")
    print("coverage: p.270 complete; p.272 ranges L54-60; p.268-275 notes complete")
    print(f"target source segment: {NOTES}")
    print("following segment: select the next queued segment in source order after application")
    print("mode: dry-run (no table writes)")
    missing_body_links = [key for key, ids in body_links.items() if not ids]
    if missing_body_links:
        print("notes without a marked body statement: " + ", ".join(f"p{p} n{n}" for p, n in missing_body_links))
    print("special review: p.270 note 7 marker/content mismatch retained; not evidence for Gesuati funding")


def apply_plan():
    planned_candidates = candidates + new_candidates
    planned_mentions = mentions + new_mentions
    for mention_id, (old_id, new_id) in mention_reassignments.items():
        mentions_by_id[mention_id]["candidate_id"] = new_id
        mentions_by_id[mention_id]["note"] = "Named Madonna del Carmelo work; reassigned from a Tiepolo index candidate to the dedicated work candidate during S2."
    planned_statements = []
    for row in statements:
        planned_statements.append(body_updates.get(row["statement_id"], row))
    planned_statements.extend(new_statements)
    candidate_backup = candidate_path.with_name(candidate_path.name + BACKUP_SUFFIX)
    mention_backup = mention_path.with_name(mention_path.name + BACKUP_SUFFIX)
    statement_backup = statement_path.with_name(statement_path.name + BACKUP_SUFFIX)
    coverage_backup = coverage_path.with_name(coverage_path.name + BACKUP_SUFFIX)
    backups = [(candidate_path, candidate_backup), (mention_path, mention_backup), (statement_path, statement_backup), (coverage_path, coverage_backup)]
    if any(backup.exists() for _, backup in backups):
        raise SystemExit("backup path already exists; refusing to overwrite recovery data")
    for original, backup in backups:
        shutil.copy2(original, backup)
    try:
        write_csv(candidate_path, candidate_fields, planned_candidates)
        write_csv(mention_path, mention_fields, planned_mentions)
        write_jsonl(statement_path, planned_statements)
        write_csv(coverage_path, coverage_fields, coverage)
    except Exception:
        for original, backup in backups:
            if backup.exists():
                shutil.copy2(backup, original)
        raise
    print("applied; four table backups saved:")
    for _, backup in backups:
        print(f"  {backup.relative_to(ROOT)}")
    print(f"rows: candidates={len(planned_candidates)}, mentions={len(planned_mentions)}, statements={len(planned_statements)}, coverage={len(coverage)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the verified migration")
    args = parser.parse_args()
    preview()
    if args.apply:
        apply_plan()
