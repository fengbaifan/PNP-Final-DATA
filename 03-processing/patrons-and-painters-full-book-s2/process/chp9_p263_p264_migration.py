"""Controlled S2 migration for printed pp.263-264; defaults to a read-only dry run."""
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
BODY_SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
P263 = "chp-9:09_CHP-9_intro:l231-238"
P264 = "chp-9:09_CHP-9_intro:l240-249"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
EXPECTED_HASHES = {
    P263: "403d813c6d986e4009cf2beb125153ce96b8b605547380e83dd806954d14dd56",
    P264: "355313d4c69e00f29306b9e6a740b06e817202f3d37621ce1724718501862751",
    NOTES: "51cc706d49319744d5efe4ed0c2528e68a2a3e1d82d75b14961092f0c36eebfc",
}
EXPECTED_ASSET = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
BACKUP_SUFFIX = ".bak-s2-chp9-p263-p264-20261001"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(f.name)
    tmp.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(path)


segments = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {r["segment_id"]: r for r in segments}
for sid, expected_hash in EXPECTED_HASHES.items():
    if sid not in segment_by_id or segment_by_id[sid]["sha256"] != expected_hash:
        raise SystemExit(f"missing or changed source segment: {sid}")
if hashlib.sha256(BODY_SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET:
    raise SystemExit("S0 source asset changed")
source_lines = BODY_SOURCE.read_text(encoding="utf-8-sig").splitlines()
source_lines_by_id = {P263: source_lines, P264: source_lines, NOTES: source_lines}


def quote(segment_id, first, last):
    lines = source_lines_by_id[segment_id]
    return "\n".join(lines[n - 1] for n in range(first, last + 1))


candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)
coverage_by_id = {r["segment_id"]: r for r in coverage}

expected_coverage = {
    P263: ("queued", "pending", ""),
    P264: ("queued", "pending", ""),
    NOTES: ("reviewed", "partial", "L349-413; p.255 L155 continuation"),
}
for sid, expected in expected_coverage.items():
    row = coverage_by_id.get(sid)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != expected:
        raise SystemExit(f"unexpected coverage for {sid}: {row}")

candidate_ids = {r["candidate_id"] for r in candidates}
if len(candidate_ids) != len(candidates) or max(int(x.split("-")[1]) for x in candidate_ids) != 8570:
    raise SystemExit("candidate inventory changed; inspect before allocating IDs")

C = {
    "sagredo_family": "cand-8571",
    "republic": "cand-8572",
    "venice": "cand-8573",
    "bergamo": "cand-8574",
    "sofia_palace": "cand-8575",
    "vienna_foscarini": "cand-8576",
    "barbaro_source": "cand-8577",
    "keysler": "cand-8578",
    "keysler_source": "cand-8579",
    "cochin_source": "cand-8580",
    "anonymous_ms": "cand-8581",
    "wright_source": "cand-8582",
    "meschini_source": "cand-8583",
    "bottari_source": "cand-8584",
    "zanotti_source": "cand-8585",
    "dargen": "cand-8586",
    "rocco_exhibition": "cand-8587",
    "rocco_place": "cand-8588",
    "bonfiglioli_family": "cand-8589",
    "carracci_drawings": "cand-8590",
    "crespi_pictures": "cand-8591",
    "archivio_venice": "cand-8592",
    "grigis": "cand-8593",
    "will": "cand-8594",
    "inventory_1738": "cand-8595",
    "walpole_source": "cand-8596",
    "posse_letter": "cand-8597",
    "blunt_document": "cand-8598",
    "udney_list": "cand-8599",
    "brunetti_source": "cand-8600",
    "baldinucci_source": "cand-8601",
    "borgognone_battles": "cand-8602",
    "plate48b_portrait": "cand-8603",
    "prestage_sale": "cand-8604",
    "bologna": "cand-8605",
}
candidate_specs = [
    (8571, "Sagredo family (collective family named in pp.263-264)", "family", P263, 234,
     "The family is distinguished from the individually named Sagredo candidates; internal genealogy and S3 identity reconciliation remain pending."),
    (8572, "Republic of Venice as political community in Haskell's p.263 account", "institution", P263, 234,
     "Political entity to which the Sagredo family gave Doge Niccolò; keep distinct from the city of Venice."),
    (8573, "Venice as a city in Haskell's p.263 account", "place", P263, 234,
     "Geographic city in the patronage statement; a local S2 candidate, not globally aligned."),
    (8574, "Bergamo as the governorship location named on p.263", "place", P263, 234,
     "City named for Zaccaria Sagredo's governorship; do not merge with other chapter candidates before S3."),
    (8575, "Unnamed Sagredo palace at S. Sofia, Venice", "place", P263, 236,
     "Residence named by Haskell without a fuller building identity; do not infer a modern palace address."),
    (8576, "Vienna Foscarini (named as Zaccaria Sagredo's mother)", "person", NOTES, 414,
     "Named only in Barbaro's genealogy as cited by Haskell; identity and external alignment are unresolved."),
    (8577, "Barbaro, Arbori de patritri veneti (Archivio di Stato, MSS. VI, c.507)", "archive", NOTES, 414,
     "Genealogical source cited by Haskell for Zaccaria Sagredo's birth, parentage, office and death; not independently consulted."),
    (8578, "Keysler (surname as cited in Haskell's Travels reference)", "person", P263, 237,
     "Surname-only author candidate; no identity beyond Haskell's citation is assumed."),
    (8579, "Keysler, Travels (1757), volume III, page 295 (citation locator)", "archive", P263, 237,
     "Citation locator for Haskell's report of a gallery description; the cited passage was not independently consulted."),
    (8580, "Cochin, volume III, pages 143-150 (1758 Sagredo-palace account locator)", "archive", P263, 237,
     "Haskell says Cochin discussed pictures in the collection; title and cited pages were not independently consulted."),
    (8581, "Anonymous manuscript, Serie delle Nobili Veneti... (Biblioteca Correr, Cod. Gradenigo 185, cc.379-386)", "archive", P263, 238,
     "Manuscript title and locator as transcribed by Haskell; the manuscript was not independently consulted."),
    (8582, "Edward Wright, volume I, page 77 (citation locator)", "archive", NOTES, 417,
     "Citation locator for the anecdote about Zaccaria avoiding foreigners; work title and cited page were not independently consulted."),
    (8583, "Meschini, 1806, volume III, page 93 (citation locator)", "archive", NOTES, 415,
     "Citation locator for the description of Zaccaria as a great friend of painting; cited page was not independently consulted."),
    (8584, "Bottari, volume II, page 186 (citation locator)", "archive", NOTES, 418,
     "Cited for Zaccaria's purchase of Carracci drawings from the Bonfiglioli family; title and cited page were not independently consulted."),
    (8585, "Zanotti, volume II, page 62 (citation locator)", "archive", NOTES, 418,
     "Cited for pictures commissioned from Giuseppe Maria Crespi; title and cited page were not independently consulted."),
    (8586, "d'Argenville, volume I, page 319 (citation locator)", "archive", NOTES, 418,
     "Cited for Zaccaria's purchase of Piazzetta's Angelo Custode at the S. Rocco exhibition; cited page was not independently consulted."),
    (8587, "Annual painting exhibition at S. Rocco (year of the Angelo Custode purchase unspecified)", "event", NOTES, 418,
     "Event series named in Haskell's note; do not assign a specific edition or date."),
    (8588, "S. Rocco (exhibition venue named by Haskell; exact venue identity unresolved)", "place", NOTES, 418,
     "Place as named in the citation; not normalized to a church or institution at S2."),
    (8589, "Bonfiglioli family in Bologna (named as prior owners of drawings)", "family", NOTES, 418,
     "Family named by Haskell as the source of Zaccaria's Carracci drawings; identity and collection history are not independently checked."),
    (8590, "Unidentified Carracci drawings bought by Zaccaria Sagredo from the Bonfiglioli family", "work", NOTES, 418,
     "Drawing group without individual titles or object identities; do not infer a catalogue match."),
    (8591, "Unidentified pictures commissioned by Zaccaria Sagredo from Giuseppe Maria Crespi", "work", NOTES, 418,
     "Works are not titled in this note; keep separate from Crespi's named works elsewhere."),
    (8592, "Archivio di Stato di Venezia (repository named in pp.263 notes)", "institution", NOTES, 414,
     "Repository as reported by Haskell; the cited manuscripts were not independently consulted."),
    (8593, "Pietro Grigis (notary named in the Zaccaria Sagredo will locator)", "person", NOTES, 419,
     "Notary named by Haskell; no identity beyond the archival locator is assumed."),
    (8594, "Zaccaria Sagredo's will (22 May 1729, notary Pietro Grigis, 17:93)", "archive", NOTES, 419,
     "Will locator quoted and paraphrased by Haskell; the archival original was not independently consulted."),
    (8595, "Sagredo inventory of 1738 at the death of the Procuratore Sagredo (Biblioteca Correr, MSS. P.D.)", "archive", NOTES, 420,
     "Inventory identity as cited by Haskell; the Procuratore is not assumed to be Zaccaria or Gherardo."),
    (8596, "Horace Walpole, 1767, page viii (citation locator)", "archive", NOTES, 421,
     "Citation locator for Walpole's report of a proposed collection sale; cited source not independently consulted."),
    (8597, "Posse, 1931, Letter no.8, July 1743 (citation locator)", "archive", NOTES, 422,
     "Haskell cites the letter for a proposal to sell the pictures as a complete collection; publication title and letter not independently checked."),
    (8598, "Sagredo-archive document published by Blunt, 1957, page 24", "archive", NOTES, 423,
     "Haskell cites this document for Joseph Smith's purchases from Zaccaria's heirs in 1751-1752; publication and underlying document not independently consulted."),
    (8599, "1762 Sagredo picture list sought by Zuane Udni (Biblioteca Correr, MSS. P.D. C2193/V)", "archive", NOTES, 424,
     "List title and locator as cited by Haskell; the record does not by itself establish a completed purchase."),
    (8600, "M. Brunetti, 1951, pages 158-160 (citation locator for Pietro Longhi inventory)", "archive", NOTES, 425,
     "Citation locator for Haskell's correction that Longhi's inventory survives; cited publication not independently consulted."),
    (8601, "Baldinucci, volume VI (1728), page 421 (citation locator)", "archive", NOTES, 426,
     "Citation locator for the claim that Borgognone's battle scenes were painted for Doge Niccolò; cited page not independently consulted."),
    (8602, "Unidentified Borgognone battle scenes painted for Doge Niccolò Sagredo", "work", P264, 243,
     "Plural group reported as among the most highly valued pictures; individual paintings and catalogue identities are not supplied."),
    (8603, "Portrait reproduction of Zaccaria Sagredo identified as Plate 48b", "work", P263, 233,
     "Haskell's plate reference; the original portrait object is not identified in the p.263 sentence."),
    (8604, "Anonymous sale, 2 February 1764, Prestage, first day, lots 89 ff. (citation locator)", "archive", P264, 249,
     "Haskell thanks Anthony Blunt for pointing out that some Sagredo pictures appear in this sale; catalogue not independently consulted."),
    (8605, "Bologna as the location of the Bonfiglioli family named in p.263 n.5", "place", NOTES, 418,
     "Geographic place in Haskell's citation; remains a local S2 candidate pending global alignment."),
]
natural_keys = {(r["canonical_name"], r["suggested_type"]) for r in candidates}
for n, name, kind, source_segment, line_no, detail in candidate_specs:
    cid = f"cand-{n:04d}"
    if cid in candidate_ids or (name, kind) in natural_keys:
        raise SystemExit(f"candidate ID/natural-key collision: {cid} {name} / {kind}")
    candidates.append({"candidate_id": cid, "index_entry_id": "", "canonical_name": name,
                       "index_page_range": "", "suggested_type": kind, "status": "open",
                       "index_source_file": "", "sub_entry": "", "detail": detail,
                       "exclude_reason": "", "candidate_origin": "body-mention",
                       "candidate_source_ref": f"{source_segment}#L{line_no}"})
    candidate_ids.add(cid)
    natural_keys.add((name, kind))

existing_mention_ids = {r["mention_id"] for r in mentions}
existing_spans = {(r["segment_id"], r["start_char"], r["end_char"]) for r in mentions}
new_mentions = []
offset_cache = {}


def segment_offsets(segment_id):
    if segment_id not in offset_cache:
        meta = segment_by_id[segment_id]
        lines = source_lines_by_id[segment_id]
        offset, offsets = 0, {}
        for n in range(meta["line_start"], meta["line_end"] + 1):
            offsets[n] = offset
            offset += len(lines[n - 1]) + 1
        offset_cache[segment_id] = offsets
    return offset_cache[segment_id]


def mention(segment_id, line, suffix, cid, surface, note="", occurrence=0):
    mid = f"m-chp9-p263264-{suffix}"
    if mid in existing_mention_ids or any(r["mention_id"] == mid for r in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mid}")
    line_text = source_lines_by_id[segment_id][line - 1]
    start_at, pos = 0, -1
    for _ in range(occurrence + 1):
        pos = line_text.find(surface, start_at)
        actual_surface = surface
        if pos < 0 and "\ufffd" in surface:
            parts = re.split("\ufffd+", surface)
            pattern = "".join(re.escape(part) + (r"\S" if i < len(parts) - 1 else "")
                               for i, part in enumerate(parts))
            match = re.search(pattern, line_text[start_at:])
            if match:
                pos = start_at + match.start()
                actual_surface = match.group(0)
        if pos < 0:
            raise SystemExit(f"surface not found at {segment_id} L{line}: {surface!r}")
        start_at = pos + len(actual_surface)
    surface = actual_surface
    start = segment_offsets(segment_id)[line] + pos
    end = start + len(surface)
    span = (segment_id, str(start), str(end))
    if span in existing_spans or any((r["segment_id"], r["start_char"], r["end_char"]) == span for r in new_mentions):
        raise SystemExit(f"duplicate mention span: {mid}")
    if cid not in candidate_ids:
        raise SystemExit(f"missing candidate for {mid}: {cid}")
    new_mentions.append({"mention_id": mid, "segment_id": segment_id, "candidate_id": cid,
                         "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


M = [
    (P263,233,"zaccaria-plate","cand-2329","Zaccaria Sagredo","Page-specific Sagredo index candidate; S3 identity alignment remains pending."),
    (P263,233,"plate48b","cand-8603","Plate 48b","Internal illustration cross-reference; caption segment is processed after p.264."),
    (P263,234,"sagredo-family","cand-8571","The Sagredo","Family-level subject; keep distinct from Zaccaria and other Sagredo persons."),
    (P263,234,"republic","cand-8572","Republic","Political entity, not Venice as a city."),
    (P263,234,"niccolo","cand-2327","Niccol��","OCR form; print reads Niccolò."),
    (P263,234,"zaccaria-nephew","cand-2329","young Zaccaria","Named nephew; candidate follows the p.263 index entry."),
    (P263,234,"bergamo-governor","cand-8574","Bergamo","Location of the reported governorship; not globally aligned."),
    (P263,234,"venetian-aristocrats","cand-8108","Venetian aristocrats","Collective social group, not a list of individual persons."),
    (P263,234,"venice-city","cand-8573","Venice","City in Haskell's account; keep separate from the Republic."),
    (P263,234,"breval","cand-0451","John Breval","Author named in Haskell's nested report."),
    (P263,235,"noble-sagredo","cand-2329","the noble Sagredo","Breval quotation; same p.263 index candidate."),
    (P263,236,"zaccaria-nervous","cand-2338","Zaccaria Sagredo","Index sub-entry for nervous disposition."),
    (P263,236,"sofia-palace","cand-8575","S. Sofia","Palace location as given; full place identity unresolved."),
    (P263,236,"tommaso-servant","cand-2357","Tommaso de�� Santi","OCR form; printed will uses Tomaso de Santi."),
    (P263,236,"gherardo-heir","cand-2326","Gherardo","Nephew named as heir."),
    (P263,237,"keysler","cand-8578","Keysler","Surname-only author reference."),
    (P263,237,"venice-after-death","cand-8573","Venice","City in Keysler chronology."),
    (P263,237,"cochin","cand-0793","Cochin","Author named in the account of pictures."),
    (P263,238,"biblioteca-correr","cand-8262","Biblioteca Correr","Repository named for the anonymous manuscript."),
    (P263,238,"gradenigo-manuscript","cand-8581","Cod. Gradenigo 185","Manuscript locator; the codex was not independently consulted."),
    (P263,238,"zaccaria-manuscript","cand-2329","Zaccaria Sagredo","Person named in the manuscript's 1710 entry."),
    (P264,241,"gherardo-death","cand-2336","his death","Context resolves the pronoun to Gherardo, who survived Zaccaria; manuscript and inventory evidence remain separate."),
    (P264,241,"walpole","cand-2798","Horace Walpole","Traveler named as hearing of a proposed sale."),
    (P264,241,"algarotti","cand-0041","Francesco Algarotti","Named as also hearing of the proposed sale."),
    (P264,241,"sagredo-heirs","cand-8571","Sagredo��s heirs","OCR apostrophe form; heirs are described collectively."),
    (P264,241,"joseph-first","cand-2468","Joseph","First half of line-broken Joseph Smith name; linked to index sub-entry for Sagredo purchases."),
    (P264,242,"joseph-smith","cand-2468","Smith","Second half of line-broken Joseph Smith name."),
    (P264,242,"john-udney","cand-2668","John Udney","Haskell describes him as Smith's successor and one of the buyers."),
    (P264,243,"tiepolo-inventories","cand-2569","Tiepolo","Named as an inventory maker in 1743."),
    (P264,243,"piazzetta-inventories","cand-1901","Tiazzetta","OCR form; scan reads Piazzetta."),
    (P264,243,"longhi-inventory","cand-1429","Pietro Longhi","Named as a later inventory maker in 1762."),
    (P264,243,"zaccaria-evidence","cand-2337","Zaccaria Sagredo","Index sub-entry for collection inventories."),
    (P264,243,"borgognone","cand-0399","Borgognone","Artist named for battle-scene group."),
    (P264,243,"niccolo-battle-scenes","cand-2327","Niccol��","OCR form; scan reads Niccolò; Doge who commissioned the battle scenes per Haskell."),
    (P264,244,"zaccaria-late-life","cand-2339","Zaccaria","Index sub-entry for patronage of younger Venetian artists."),
    (P264,244,"sagredo-younger-generation","cand-8571","Sagredo��s","OCR apostrophe form; family context."),
    (P264,249,"blunt-acknowledgement","cand-0379","Sir Anthony Blunt","Acknowledged by Haskell as pointing out the sale reference."),
    (P264,249,"prestage-sale","cand-8604","Prestage","Auction-catalogue citation locator; sale catalogue not independently consulted."),
    (NOTES,414,"barbaro-source","cand-8577","Barbaro","Genealogical source named by Haskell."),
    (NOTES,414,"archivio-di-stato","cand-8592","Archivio di Stato","Repository as cited; not normalized to another state archive candidate."),
    (NOTES,414,"stessano-sagredo","cand-2328","Stessano Sagredo","OCR form; p.263 scan reads Steffano Sagredo. Identity remains for S3."),
    (NOTES,414,"vienna-foscarini","cand-8576","Vienna Foscarini","Named as Zaccaria's mother by the cited genealogy."),
    (NOTES,414,"bergamo-podesta","cand-8574","Bergamo","Location of the office in Barbaro's account."),
    (NOTES,415,"da-canal","cand-6593","Da Canal","Page 36 locator in the cited Da Canal work; no new bibliographic identity inferred."),
    (NOTES,415,"meschini-source","cand-8583","Meschini, 1806, IH, p. 93","OCR form IH; scan reads volume III."),
    (NOTES,416,"breval-source","cand-7713","Breval, 1738, I, p. 230","Published work locator; not independently consulted."),
    (NOTES,417,"wright-source","cand-8582","Edward Wright, I, p. 77","Citation locator; not independently consulted."),
    (NOTES,418,"carracci","cand-0576","Carracci","Drawings attributed to the Carracci; individual makers and sheets unspecified."),
    (NOTES,418,"bonfiglioli","cand-8589","Bonfiglioli family","Named as the family from whom drawings were bought."),
    (NOTES,418,"bologna","cand-8605","Bologna","Place named for the Bonfiglioli family."),
    (NOTES,418,"bottari-source","cand-8584","Bottari, H, p. 186","OCR form H; scan reads volume II."),
    (NOTES,418,"crespi-commission","cand-0871","Crespi","Artist named for commissioned pictures."),
    (NOTES,418,"crespi-pictures","cand-8591","pictures","Unidentified works commissioned from Crespi."),
    (NOTES,418,"zanotti-source","cand-8585","Zanotti, H, p. 62","OCR form H; scan reads volume II."),
    (NOTES,418,"piazzetta","cand-1901","Piazzetta","Artist named in purchase report."),
    (NOTES,418,"angelo-custode","cand-8569","Angelo Custode","Same p.262 work candidate; purchase at S. Rocco as reported in p.263 n.5."),
    (NOTES,418,"srocco-exhibition","cand-8587","S. Rocco exhibition","Annual exhibition series; specific year not supplied."),
    (NOTES,418,"dargen-source","cand-8586","d��Argenville, I, p. 319","OCR form; citation locator as printed."),
    (NOTES,419,"zaccaria-will","cand-8594","Zaccaria Sagredo��s will","Will locator; quoted passage continues in p.264 source segment L245-248."),
    (NOTES,419,"venetian-archivio","cand-8592","Archivio di Stato","Repository for the will locator."),
    (NOTES,419,"pietro-grigis","cand-8593","Pietro Grigis","Notary named in the will locator."),
    (NOTES,420,"inventory-1738","cand-8595","Inventario del 1738","Inventory title as cited; the named Procuratore is not identified here."),
    (NOTES,420,"correr-1738","cand-8262","Biblioteca Correr","Repository for the 1738 inventory."),
    (NOTES,421,"walpole-source","cand-8596","Horace Walpole, 1767, p. viii","Citation locator; the source was not independently consulted."),
    (NOTES,422,"posse-source","cand-8597","Posse, 1931","Citation locator; the publication and letter were not independently checked."),
    (NOTES,423,"sagredo-archive-doc","cand-8598","document from the Sagredo archives","Published documentary locator cited by Haskell."),
    (NOTES,423,"blunt-source","cand-0379","Blunt, 1957, p. 24","Publication named as the source for the archive document."),
    (NOTES,423,"smith-buying","cand-2468","Smith","Index sub-entry for purchases of Sagredo pictures."),
    (NOTES,424,"udney-list","cand-8599","list of pictures dated 1762","Archive list as cited; a list does not itself establish purchase."),
    (NOTES,424,"udney","cand-2668","Zuane Udni","OCR form; index name John Udney; spelling difference is retained for S3."),
    (NOTES,424,"correr-udney","cand-8262","Biblioteca Correr","Repository for the 1762 picture list."),
    (NOTES,425,"brunetti-source","cand-8600","M. Brunetti, 1951, pp. 158-60","Citation locator; publication not independently consulted."),
    (NOTES,425,"longhi-inventory-source","cand-1429","Longhi inventory","Inventory attributed to Pietro Longhi; source identity handled separately from the artist."),
    (NOTES,425,"correr-longhi","cand-8262","Biblioteca Correr","Repository for the surviving Longhi inventory."),
    (NOTES,426,"baldinucci-source","cand-8601","Baldinucci, VI, 1728, p. 421","Citation locator; cited page not independently consulted."),
]
for row in M:
    mention(*row)

new_statements = []
existing_statement_ids = {r["statement_id"] for r in statements}


def statement(suffix, segment_id, first, last, subject, obj, predicate, claim, qualification,
              mentioned, marker=None, speaker="Haskell", text_layer="authorial narrative", extras=None,
              printed_page=None):
    sid = f"st-chp9-p263264-{suffix}"
    if sid in existing_statement_ids or any(r["statement_id"] == sid for r in new_statements):
        raise SystemExit(f"duplicate statement ID: {sid}")
    meta = segment_by_id[segment_id]
    if first < meta["line_start"] or last > meta["line_end"]:
        raise SystemExit(f"statement span out of segment: {sid}")
    page = printed_page or (263 if segment_id == P263 else 264)
    physical = page - 238
    q = {"source_line_start": first, "source_line_end": last, "printed_page": page,
         "pdf_physical_page": physical, "claim": claim, "speaker": speaker,
         "text_layer": text_layer, "qualification": qualification,
         "mentioned_candidate_ids": list(dict.fromkeys(x for x in mentioned if x))}
    if marker is not None:
        q["footnote_marker"] = marker
    if extras:
        q.update(extras)
    new_statements.append({"statement_id": sid, "segment_id": segment_id,
                           "subject_candidate_id": subject, "object_candidate_id": obj,
                           "predicate": predicate, "qualifiers": q,
                           "original_quote": quote(segment_id, first, last), "origin": "book",
                           "source_file": meta["source_file"]})


def b(suffix, first, last, subject, obj, predicate, claim, qualification, mentioned,
      marker=None, extras=None):
    statement(suffix, P263, first, last, subject, obj, predicate, claim, qualification,
              mentioned, marker, extras=extras, printed_page=263)


def p264(suffix, first, last, subject, obj, predicate, claim, qualification, mentioned,
         marker=None, extras=None):
    statement(suffix, P264, first, last, subject, obj, predicate, claim, qualification,
              mentioned, marker, extras=extras, printed_page=264)


def n(suffix, first, last, subject, obj, predicate, claim, qualification, mentioned,
      marker, *, speaker="Haskell's footnote", text_layer="footnote claim", extras=None,
      printed_page=263, segment_id=NOTES):
    statement(suffix, segment_id, first, last, subject, obj, predicate, claim, qualification,
              mentioned, marker, speaker, text_layer, extras, printed_page)


b("sagredo-patron-collector",232,234,"cand-2329",None,
  "haskell_identifies_sagredo_as_the_individual_patron_among_venetian_nobility",
  "Haskell characterizes Venetian noble support for the arts in the first half of the eighteenth century as unimaginative outside ceiling decoration, and singles out Zaccaria Sagredo as a patron and collector of individuality.",
  "Authorial comparative judgement, not a census of all Venetian patrons; Plate 48b is an internal illustration reference.",
  ["cand-2329","cand-8571","cand-8572","cand-8108","cand-8603"],
  extras={"cross_reference_segments":[{"segment_id":"chp-9:09_CHP-9_intro:l287-289","source_line_start":287,"source_line_end":289}]})
b("niccolo-and-zaccaria-kinship",234,234,"cand-2327","cand-2329",
  "niccolo_sagredo_was_zaccarias_uncle_and_doge_elected_1675_dying_after_eighteen_months",
  "Haskell calls Niccolò Zaccaria's uncle, describes him as an impressive Doge elected in 1675, and says he lived only eighteen months after election; Zaccaria was then 21.",
  "The kinship and chronology are Haskell's account; the adjective 'impressive' is evaluative. Do not calculate a precise death date from 'eighteen months'.",
   ["cand-2327","cand-2329","cand-8571","cand-8572"],extras={"relation_candidate":True})
b("zaccaria-public-service-and-collection",234,234,"cand-2329","cand-8574",
  "zaccaria_sagredo_governed_bergamo_in_1690_and_amassed_a_multi_medium_collection",
  "Haskell says Zaccaria Sagredo served public office, reached no higher post than the governorship of Bergamo in 1690, and used his resources to amass paintings, drawings, sculpture, books and armour.",
  "The passage describes a highest post, not a complete office chronology or itemized collection inventory.",
  ["cand-2329","cand-8574","cand-8573"],marker=1,
  extras={"relation_candidate":True,"cross_reference_segments":[{"segment_id":NOTES,"source_line_start":414,"source_line_end":414}]})
b("breval-patron-reputation",234,235,"cand-2329","cand-0451",
  "sagredo_gained_reputation_as_venices_greatest_patron_and_breval_heard_of_one_remarkable_dilettante",
  "Haskell says the collection later gave Sagredo a reputation as Venice's greatest patron and, among foreign visitors, almost the only one; Breval said he could hear of but one remarkable dilettante, the noble Sagredo.",
  "Both are reported reputations and nested quotations; they are not a count of patrons or independent assessments.",
  ["cand-2329","cand-0451","cand-7713","cand-8573"],marker=2,
  extras={"cross_reference_segments":[{"segment_id":NOTES,"source_line_start":415,"source_line_end":416}]})
b("sagredo-temperament",235,236,"cand-2338",None,
  "sagredo_seems_excessively_nervous_and_avoided_meeting_foreigners",
  "Haskell says Zaccaria seems to have had an excessively nervous temperament and recounts that he hurried downstairs to avoid meeting foreigners.",
  "The interpretation is explicitly hedged by 'seems'; the anecdote is reported through Edward Wright, not independently checked.",
  ["cand-2338","cand-8578","cand-8579"],marker=4,
  extras={"cross_reference_segments":[{"segment_id":NOTES,"source_line_start":417,"source_line_end":417}]})
b("sagredo-palace-collection",236,236,"cand-2329","cand-8575",
  "sagredo_never_married_and_filled_his_s_sofia_palace_with_old_and_new_pictures",
  "Haskell says Zaccaria never married and filled his palace at S. Sofia with old and new pictures bought from previous collectors, commissioned directly from artists, or acquired at exhibitions.",
  "The passage does not name or inventory individual pictures; palace identity remains unresolved at S2.",
  ["cand-2329","cand-8575"],extras={"relation_candidate":True})
b("will-arrangements-summary",236,236,"cand-2329","cand-2326",
  "sagredo_intended_to_preserve_collection_under_tommaso_de_santi_and_leave_it_to_gherardo",
  "Haskell says Zaccaria attempted to keep his collection intact after death by placing it in the care of Tommaso de' Santi and leaving it to his nephew Gherardo.",
  "The will quotation continues on printed p.264 L245-248; its archival locator and quoted text are handled separately. The plan proved unsuccessful.",
  ["cand-2329","cand-2357","cand-2326","cand-8594"],marker=6,
  extras={"relation_candidate":True,"cross_reference_segments":[{"segment_id":NOTES,"source_line_start":419,"source_line_end":419},{"segment_id":P264,"source_line_start":245,"source_line_end":248}]})
b("sagredo-death-gherardo",236,236,"cand-2329","cand-2326",
  "zaccaria_died_in_1729_and_gherardo_survived_him_about_ten_years",
  "Haskell says Zaccaria died in 1729 and Gherardo survived him for ten years.",
  "The approximate interval is retained alongside p.264's report that Gherardo died aged 49 in 1738; no precise birth date is inferred.",
  ["cand-2329","cand-2326"],extras={"relation_candidate":True,
   "cross_reference_segments":[{"segment_id":P264,"source_line_start":241,"source_line_end":241}]})
b("keysler-gallery-report",237,237,"cand-8578","cand-2329",
  "keysler_reported_sagredo_gallery_as_mainly_antiquities_natural_curiosities_and_foreign_arms_but_could_not_enter",
  "Haskell reports that Keysler described the celebrated gallery as consisting chiefly of antiquities, natural curiosities and foreign arms and weapons, but could not enter because repairs were under way; Cochin discussed many pictures.",
  "The gallery description is second-hand and Keysler did not inspect the collection on that visit; cited works were not independently consulted.",
  ["cand-8578","cand-8579","cand-2329","cand-0793","cand-8580"],
  extras={"cross_reference_segments":[{"segment_id":P263,"source_line_start":237,"source_line_end":237}]})
b("gradenigo-1710-art-collection",238,238,"cand-2329","cand-8581",
  "anonymous_gradenigo_manuscript_says_sagredo_spent_greatly_on_thousands_of_prints_and_drawings_by_1710",
  "An anonymous manuscript cited by Haskell says that in 1710 Zaccaria Sagredo, at great expense, had acquired thousands of prints and drawings by the first and most excellent men in the world.",
  "Nested manuscript report quoted through Haskell; manuscript and microfilm were not independently consulted. The count and praise remain the source's wording.",
  ["cand-2329","cand-8581","cand-8262"],
  extras={"ocr_corrections":[{"source_line":238,"ocr":"Air anonymous manuscript","print":"An anonymous manuscript","basis":"CHP-9.pdf physical page 25."}]})

n("barbaro-genealogy",414,414,"cand-8577","cand-2329",
  "barbaro_genealogy_reports_zaccaria_birth_parentage_bergamo_office_gallery_and_death",
  "Barbaro's genealogy, as cited by Haskell, says Zaccaria was born on 15 October 1653 to Steffano Sagredo and Vienna Foscarini, served as Podestà at Bergamo, made a gallery of sculptures, paintings and prints, and died in May 1729.",
  "Citation and quotation are reported by Haskell; the genealogy was not independently consulted. The p.263 scan reads 'Steffano'; OCR has 'Stessano'.",
  ["cand-8577","cand-2329","cand-2328","cand-8576","cand-8574","cand-8592"],1,
  extras={"relation_candidate":True,"ocr_corrections":[{"source_line":414,"ocr":"Stessano Sagredo","print":"Steffano Sagredo","basis":"CHP-9.pdf physical page 25."}]})
n("da-canal-meschini-praise",415,415,"cand-2329",None,
  "da_canal_calls_sagredos_gallery_one_of_europes_richest_and_meschini_calls_him_friend_of_painting",
  "Haskell quotes Da Canal describing Sagredo's gallery as one of Europe's richest and Meschini calling him a great friend of painting.",
  "Two retrospective characterizations relayed by Haskell; cited pages were not independently consulted.",
  ["cand-2329","cand-6593","cand-8583"],2)
n("breval-dilettante",416,416,"cand-0451","cand-2329",
  "breval_describes_sagredo_as_the_only_remarkable_dilettante_he_heard_of_in_venice",
  "Haskell cites Breval, volume I, page 230, for the quoted phrase 'the noble Sagredo'.",
  "Citation and quotation are nested through Haskell; Breval's cited page was not independently consulted.",
  ["cand-0451","cand-7713","cand-2329"],3,text_layer="footnote citation and nested quotation")
n("wright-anecdote-locator",417,417,"cand-8578","cand-2329",
  "edward_wright_page_cited_for_sagredos_avoidance_of_foreigners",
  "Haskell cites Edward Wright, volume I, page 77, for the anecdote about Sagredo avoiding contact with foreigners.",
  "Citation locator only; Wright's cited page was not independently consulted.",
  ["cand-8578","cand-8582","cand-2329"],4,text_layer="footnote citation")
n("purchases-from-artists",418,418,"cand-2329",None,
  "sagredo_bought_carracci_drawings_commissioned_pictures_from_crespi_and_bought_piazzetta_angelo_custode",
  "Haskell's note says Zaccaria bought Carracci drawings from the Bonfiglioli family in Bologna, commissioned pictures from Crespi, and bought Piazzetta's Angelo Custode at the S. Rocco exhibition.",
  "Three transactions cited to Bottari, Zanotti and d'Argenville; the sources were not independently consulted. The works remain unidentified except for Angelo Custode.",
  ["cand-2329","cand-0576","cand-8589","cand-8590","cand-0871","cand-8591","cand-1901","cand-8569","cand-8587","cand-8588","cand-8584","cand-8585","cand-8586"],5,
  extras={"relation_candidate":True})
n("will-archival-locator",419,419,"cand-2329","cand-8594",
  "zaccaria_will_located_in_archivio_di_stato_dated_22_may_1729_before_notary_pietro_grigis",
  "Haskell gives the location, date and notary for Zaccaria Sagredo's will and begins quoting it.",
  "The will is quoted on the following printed page at source segment L245-248; the archival original was not independently examined.",
  ["cand-2329","cand-8594","cand-8592","cand-8593"],6,text_layer="footnote archival locator",
  extras={"cross_reference_segments":[{"segment_id":P264,"source_line_start":245,"source_line_end":248}]})
n("will-quoted-provisions",245,248,"cand-2329","cand-2357",
  "sagredo_will_assigns_tommaso_de_santi_care_of_collection_and_leaves_residue_to_gherardo",
  "The will passage quoted by Haskell directs that the books, prints, drawings, arms and pictures not be dispersed, appoints Tommaso de Santi to care for them and the apartments with quarterly support, and leaves the residue of Zaccaria's estate to his nephew Girardo P.O. Sagredio.",
  "Archival quotation reproduced by Haskell; notary's manuscript not independently consulted. The will's spelling forms are preserved; the relation to index candidate Gherardo remains for S3 reconciliation.",
  ["cand-2329","cand-2357","cand-2326","cand-8594","cand-8593"],6,
  speaker="Zaccaria Sagredo's will, quoted by Haskell",text_layer="nested archival quotation",
  extras={"relation_candidate":True,"cross_reference_segments":[{"segment_id":NOTES,"source_line_start":419,"source_line_end":419}]},
   printed_page=263,segment_id=P264)
n("will-gifts-to-varda",247,247,"cand-2329","cand-2700",
  "sagredo_will_left_a_rubens_and_a_moroni_portrait_to_salvator_varda",
  "Haskell says Zaccaria left a Rubens and a portrait by Moroni to his friend Salvator Varda.",
  "Reported in the continuation of the will note; the named works and the friend identity are not independently verified.",
  ["cand-2329","cand-2293","cand-1704","cand-2700","cand-8594"],6,
  speaker="Haskell's narration of the will",text_layer="footnote continuation",
  extras={"relation_candidate":True,"cross_reference_segments":[{"segment_id":NOTES,"source_line_start":419,"source_line_end":419}]},
  printed_page=263,segment_id=P264)

p264("gherardo-death-and-dispersal",241,241,"cand-2326","cand-2336",
     "gherardo_died_aged_49_in_1738_and_plans_to_disperse_collection_began",
     "Haskell says that after Gherardo's death aged 49 in 1738, plans immediately began to disperse the collection.",
     "The referent is Gherardo, not Zaccaria; p.263 says he survived Zaccaria by ten years, an approximate interval retained without recalculation.",
     ["cand-2326","cand-2336","cand-2329"],marker=1,
      extras={"cross_reference_segments":[{"segment_id":P263,"source_line_start":236,"source_line_end":236},{"segment_id":NOTES,"source_line_start":420,"source_line_end":420}]})
p264("sale-heirs-and-consuls",241,242,"cand-8571","cand-2468",
     "sagredo_heirs_sold_collection_piecemeal_to_foreigners_including_smith_and_udney",
     "Haskell says the collection was broken up piecemeal over a long period; the heirs contacted interested buyers and sold to foreigners, including British Consul Joseph Smith and his successor John Udney.",
     "Haskell's characterization is broad; the 1762 Udney list cited in note 5 documents a list sought, not by itself a completed purchase. Smith's 1751-52 purchases are separately cited in note 4.",
     ["cand-8571","cand-2468","cand-2668","cand-8598","cand-8599"],marker=4,
     extras={"relation_candidate":True,"cross_reference_segments":[{"segment_id":NOTES,"source_line_start":423,"source_line_end":424}]})
p264("sagredo-inventory-makers",243,243,"cand-2329",None,
     "tiepolo_and_piazzetta_drew_1743_inventory_and_pietro_longhi_followed_in_1762",
     "Haskell says Tiepolo and Piazzetta were required to draw up inventories in 1743 and that Pietro Longhi followed nearly twenty years later, in 1762.",
     "This is Haskell's report about inventory production; it does not establish the full surviving contents. OCR 'Tiazzetta' is corrected from the scan.",
     ["cand-2329","cand-2569","cand-1901","cand-1429","cand-8595","cand-8599"],marker=6,
     extras={"relation_candidate":True,"cross_reference_segments":[{"segment_id":NOTES,"source_line_start":420,"source_line_end":420},{"segment_id":NOTES,"source_line_start":424,"source_line_end":425}],
             "ocr_corrections":[{"source_line":243,"ocr":"Tiazzetta","print":"Piazzetta","basis":"CHP-9.pdf physical page 26."},{"source_line":243,"ocr":"'appraise","print":"appraise","basis":"CHP-9.pdf physical page 26."}]})
p264("preexisting-collection-and-borgognone",243,243,"cand-2329","cand-8602",
     "many_family_pictures_preceded_zaccaria_and_borgognones_battle_scenes_were_painted_for_doge_niccolo",
     "Haskell warns that the evidence for Zaccaria's individual contribution is difficult to assess because many pictures were already in the family collection; he says the prized Borgognone battle scenes had been painted for Doge Niccolò and many other pictures must be earlier.",
     "The attribution and chronology are Haskell's report, with the Borgognone claim cited to Baldinucci; preserve 'must' as an inference and do not assign individual battle-painting identities.",
     ["cand-2329","cand-8571","cand-8602","cand-0399","cand-2327","cand-8601"],marker=7,
     extras={"relation_candidate":True,"cross_reference_segments":[{"segment_id":NOTES,"source_line_start":426,"source_line_end":426}]})
p264("zaccaria-head-of-branch-and-late-passion",244,244,"cand-2329","cand-2328",
     "zaccaria_became_head_of_his_family_branch_after_fathers_death_and_artistic_passion_is_reported_only_late",
     "Haskell says Zaccaria became head of his family branch only ten years after the preceding event, that his passion for art is first heard of much later when he was already old, and that his sympathies in his last years extended to younger Venetian artists.",
     "The phrase 'ten years after this' is kept relative; no exact year is inferred. His support for younger artists is a bounded authorial account.",
     ["cand-2329","cand-2328","cand-2339","cand-8571"],marker=8,
     extras={"relation_candidate":True,"cross_reference_segments":[{"segment_id":NOTES,"source_line_start":427,"source_line_end":427}]})
n("inventory-1738-locator",420,420,"cand-2326","cand-8595",
  "haskell_cites_a_1738_sagredo_inventory_at_gherardos_death",
  "Haskell cites an inventory from 1738, dated to the death of a Procuratore Sagredo, at Biblioteca Correr MSS. P.D.",
  "The Procuratore is not identified in this note; do not equate the inventory with Zaccaria's or Gherardo's personal collection without further evidence.",
  ["cand-2326","cand-8595","cand-8262","cand-8571"],1,printed_page=264)
n("walpole-proposed-sale",421,421,"cand-2798","cand-2336",
  "walpole_heard_of_the_proposed_sagredo_collection_sale",
  "Haskell cites Horace Walpole, 1767, page viii, for knowledge of the proposed sale.",
  "Citation locator only; Walpole's cited text was not independently consulted.",
  ["cand-2798","cand-8596","cand-2336"],2,text_layer="footnote citation",printed_page=264)
n("posse-complete-sale-report",422,422,"cand-8597","cand-2336",
  "posse_letter_reports_pictures_were_to_be_sold_as_a_complete_collection_in_july_1743",
  "Haskell says Posse's Letter no.8 of July 1743 reports that the pictures were to be sold as a complete collection.",
  "This is a reported plan; Haskell separately says the collection was in fact broken up piecemeal over a long period.",
  ["cand-8597","cand-2336","cand-2329"],3,text_layer="footnote citation and reported claim",printed_page=264)
n("smith-purchases-document",423,423,"cand-2468","cand-8598",
  "sagredo_archive_document_shows_smith_bought_paintings_and_drawings_from_heirs_in_1751_1752",
  "Haskell cites a Sagredo-archive document published by Blunt showing Joseph Smith buying paintings and drawings from Zaccaria's heirs in 1751-1752.",
  "Nested documentary claim as cited by Haskell; neither the document nor Blunt's publication was independently consulted.",
  ["cand-2468","cand-8598","cand-0379","cand-8571"],4,text_layer="footnote citation and nested archival claim",printed_page=264,
  extras={"relation_candidate":True})
n("udney-1762-list",424,424,"cand-2668","cand-8599",
  "udney_sought_a_list_of_sagredo_pictures_in_1762",
  "Haskell cites a list of pictures dated 1762 and described as sought by the English consul Zuane Udni.",
  "The list's locator is reported; it is not by itself proof that Udney completed a purchase. OCR 'Udni' is retained alongside the indexed John Udney candidate for later S3 review.",
  ["cand-2668","cand-8599","cand-8262","cand-2329"],5,text_layer="footnote archival locator",printed_page=264)
n("longhi-inventory-survival",425,425,"cand-1429","cand-8600",
  "longhi_inventory_survives_in_the_sagredo_papers_despite_brunettis_claim_it_was_lost",
  "Haskell says M. Brunetti maintains that the Longhi inventory was lost, but that it survives with other Sagredo papers in Biblioteca Correr MSS. P.D. C2193/I.",
  "This is Haskell's correction of Brunetti; neither the inventory nor cited publication was independently examined.",
  ["cand-1429","cand-8600","cand-8262","cand-2329"],6,text_layer="footnote citation and authorial correction",printed_page=264)
n("baldinucci-borgognone-locator",426,426,"cand-0399","cand-8601",
  "baldinucci_cited_for_borgognone_battle_scenes_made_for_doge_niccolo",
  "Haskell cites Baldinucci, volume VI, 1728, page 421, for the Borgognone battle-scene claim.",
  "Citation locator only; the cited source was not independently consulted.",
  ["cand-0399","cand-8601","cand-2327","cand-8602"],7,text_layer="footnote citation",printed_page=264)
n("direct-acquisition-limit-partial",427,427,"cand-2329",None,
  "haskell_limits_sure_direct_acquisitions_to_pictures_dated_1685_1729_partial_note",
  "Haskell begins to delimit which inventory pictures can safely be treated as directly acquired by Zaccaria, pointing to works dated between 1685 and 1729.",
  "The note is cut off at L427 and continues in the p.265 page OCR at L295-296; do not treat this partial excerpt as a complete claim until that continuation is reviewed.",
  ["cand-2329"],8,speaker="Haskell's footnote",text_layer="footnote claim (partial at segment end)",printed_page=264,
  extras={"continuation_pending":{"segment_id":"chp-9:09_CHP-9_intro:l291-301","source_line_start":295,"source_line_end":296}})

all_candidate_ids = {r["candidate_id"] for r in candidates}
if len({r["mention_id"] for r in mentions + new_mentions}) != len(mentions) + len(new_mentions):
    raise SystemExit("mention IDs are not unique")
if len({r["statement_id"] for r in statements + new_statements}) != len(statements) + len(new_statements):
    raise SystemExit("statement IDs are not unique")
for row in new_mentions:
    sid = row["segment_id"]
    start, end = int(row["start_char"]), int(row["end_char"])
    meta = segment_by_id[sid]
    text = "\n".join(source_lines_by_id[sid][n - 1] for n in range(meta["line_start"], meta["line_end"] + 1))
    if text[start:end] != row["surface_form"]:
        raise SystemExit(f"mention span mismatch: {row['mention_id']}")
for row in new_statements:
    q = row["qualifiers"]
    refs = set(q.get("mentioned_candidate_ids", []))
    refs.update(x for x in [row.get("subject_candidate_id"), row.get("object_candidate_id")] if x)
    if not refs <= all_candidate_ids:
        raise SystemExit(f"statement foreign key error {row['statement_id']}: {refs-all_candidate_ids}")
    if row["original_quote"] != quote(row["segment_id"], q["source_line_start"], q["source_line_end"]):
        raise SystemExit(f"quote mismatch: {row['statement_id']}")

coverage_by_id[P263].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L232-238",
    "note": "Printed p.263 (CHP-9.pdf physical p.25) reviewed against scan. Body claims, nested quotations and p.263 notes 1-6 are migrated or cross-linked. Zaccaria's will note 6 continues at p.264 source L245-248; p.263 reference to Plate 48b links to the later Plate 48 segment. OCR corrections are recorded in S2; source OCR remains unchanged."})
coverage_by_id[P264].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L241-249; p.263 note 6 continuation",
    "note": "Printed p.264 (CHP-9.pdf physical p.26) reviewed against scan. Body claims and notes 1-8 at consolidated L420-427 are represented; p.263 will quotation continues through this page OCR L245-248. The p.264 note 8 is explicitly partial and cross-linked to p.265 source L295-296. The 1764 anonymous-sale acknowledgement at L249 is retained. No source OCR was rewritten."})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L349-427; p.255 L155 continuation; p.263 note 6 continues at p.264 L245-248",
    "note": "Consolidated notes through p.264 notes 1-8 migrated at L414-427. P.263 note 6 continues at p.264 OCR L245-248; p.264 note 8 continues at p.265 OCR L295-296 and remains explicitly partial pending that segment. L428 is a repeated OCR extraction of the Plate 46 heading already present at L258-277; it is excluded as duplicate text and will be cross-referenced when the plate segment is reviewed. Later notes from L429 remain unprocessed."})

summary = {
    "new_candidates": len(candidate_specs), "new_mentions": len(new_mentions), "new_statements": len(new_statements),
    "coverage": {sid: [coverage_by_id[sid]["disposition"], coverage_by_id[sid]["migration_status"], coverage_by_id[sid]["source_line_ranges"]]
                 for sid in (P263, P264, NOTES)},
    "cross_page_closures": ["p.263 note 6 L419 -> p.264 L245-248", "p.264 note 8 L427 -> p.265 L295-296 (pending)"],
    "duplicate_ocr_excluded": "notes L428 repeats Plate 46 caption OCR at L258-277",
    "next_segment": "chp-9:09_CHP-9_intro:l251-256 (Plate 45)",
}
print(json.dumps(summary, ensure_ascii=False, indent=2))
parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the preflighted migration")
args = parser.parse_args()
if args.apply:
    paths = [candidate_path, mention_path, statement_path, coverage_path]
    backups = [p.with_name(p.name + BACKUP_SUFFIX) for p in paths]
    if any(p.exists() for p in backups):
        raise SystemExit("one or more recovery backups already exist; inspect before retrying")
    for src, bak in zip(paths, backups):
        shutil.copy2(src, bak)
    try:
        write_csv(candidate_path, candidate_fields, candidates)
        write_csv(mention_path, mention_fields, mentions + new_mentions)
        write_jsonl(statement_path, statements + new_statements)
        write_csv(coverage_path, coverage_fields, list(coverage_by_id.values()))
    except Exception:
        for dst, bak in zip(paths, backups):
            shutil.copy2(bak, dst)
        raise
    print("APPLIED; recovery backups retained: " + ", ".join(p.name for p in backups))
else:
    print("DRY RUN: no S2 table rows written")
