"""Controlled S2 migration of chapter 8 notes on printed pp.212-214.

Default invocation validates and previews only.  --apply writes candidates,
mentions, statements, and coverage after checking source hashes, spans, quotes,
footnote links, and foreign keys.  The p.214 visual transcription is a
page-image-derived supplement to the unchanged S0 OCR.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
COMPOSITE_REL = "02-sources/02-Markdown/08_CHP-8_sec_i.md"
VISUAL_REL = "02-sources/02-Markdown/08_CHP-8_sec_i_notes_p214_visual-transcription.md"
COMPOSITE_ID = "chp-8:08_CHP-8_sec_i:l126-157"
VISUAL_ID = "chp-8:08_CHP-8_sec_i_notes_p214_visual-transcription:l1-4"
BODY_P212 = "chp-8:08_CHP-8_sec_i:l98-106"
BODY_P213 = "chp-8:08_CHP-8_sec_i:l108-118"
BODY_P214 = "chp-8:08_CHP-8_sec_i:l120-124"
EXPECTED_MAX_CANDIDATE = 7600
BACKUP_SUFFIX = ".bak-s2-chp8-p212-214-notes-20261001"

IDS = {
    "richa_person": "cand-7601",
    "richa_book": "cand-7602",
    "longhi_person": "cand-7603",
    "longhi_article": "cand-7604",
    "bilivert_person": "cand-7605",
    "dolci_group": "cand-7606",
    "bilivert_group": "cand-7607",
    "cortona_small_madonna": "cand-7608",
    "cortona_early_madonna": "cand-7609",
    "s_agostino_cortona": "cand-7610",
    "nicola_del_rosso": "cand-7611",
    "mediceo_filza": "cand-7612",
    "panciatichi_letter": "cand-7613",
    "ferri_altarpieces": "cand-7614",
    "boni_frescoes": "cand-7615",
    "dal_sole_monti_pictures": "cand-7616",
    "giovanelli_family": "cand-7617",
    "monaco_book": "cand-7618",
    "monaco_prints": "cand-7619",
    "valery_person": "cand-7620",
    "valery_book": "cand-7621",
    "palazzo_contarini": "cand-7622",
    "valery_giordano_group": "cand-7623",
    "aeneas_anchises_painting": "cand-7624",
    "loret_person": "cand-7625",
    "anchises_person": "cand-7626",
}

EXISTING = {
    "cinelli": "cand-0765",
    "baldinucci_person": "cand-0166",
    "baldinucci_book": "cand-4846",
    "cinelli_book": "cand-7499",
    "fall_manna": "cand-7529",
    "moses_rock": "cand-7530",
    "del_rosso_family": "cand-7489",
    "dolci_person": "cand-0923",
    "dolci_flight": "cand-7495",
    "lord_exeter": "cand-0984",
    "pietro_cortona": "cand-0342",
    "ciro_ferri": "cand-1027",
    "luca_giordano": "cand-1172",
    "gualandi_ii": "cand-7501",
    "mostra_cortona": "cand-4472",
    "biblioteca_nazionale": "cand-7503",
    "florence": "cand-3397",
    "poligrafo_gargano": "cand-7504",
    "panciatichi": "cand-1825",
    "naples": "cand-3534",
    "ribera": "cand-2140",
    "preti": "cand-2056",
    "paceco_de_rosa": "cand-2235",
    "dal_sole": "cand-2480",
    "francesco_monti": "cand-1698",
    "zanotti_book": "cand-7115",
    "boni": "cand-0388",
    "soprani_book": "cand-5160",
    "de_dominici_person": "cand-7116",
    "de_dominici_book": "cand-4835",
    "bologna_book": "cand-7348",
    "giordano": "cand-1172",
    "solimena": "cand-2484",
    "venice": "cand-2719",
    "labia_family": "cand-1349",
    "procuratore_canale": "cand-0497",
    "flaminio_corner": "cand-0844",
    "widmann_family": "cand-2812",
    "pietro_monaco": "cand-1682",
    "aeneas": "cand-4164",
    "loret_article": "cand-6583",
}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent,
                                     delete=False, suffix=".tmp") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl_atomic(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent,
                                     delete=False, suffix=".tmp") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
segment_path = TABLES / "segments.jsonl"

candidate_fields, candidate_rows = read_csv(candidate_path)
mention_fields, mention_rows = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statement_rows = read_jsonl(statement_path)
segment_rows = read_jsonl(segment_path)

segments = {row["segment_id"]: row for row in segment_rows}
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
candidate_ids = set(candidate_by_id)
mention_ids = {row["mention_id"] for row in mention_rows}
statement_ids = {row["statement_id"] for row in statement_rows}

segment_sources = {
    COMPOSITE_ID: (COMPOSITE_REL, 126, 157),
    VISUAL_ID: (VISUAL_REL, 1, 4),
}
source_lines = {}
segment_texts = {}
for segment_id, (relative, line_start, line_end) in segment_sources.items():
    segment = segments.get(segment_id)
    if not segment or segment.get("source_file") != relative:
        raise SystemExit(f"source segment missing or changed: {segment_id}")
    if (int(segment["line_start"]), int(segment["line_end"])) != (line_start, line_end):
        raise SystemExit(f"source segment interval changed: {segment_id}")
    source_path = ROOT / relative
    raw = source_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != segment["asset_sha256"]:
        raise SystemExit(f"source asset fingerprint changed: {relative}")
    lines = source_path.read_text(encoding="utf-8-sig").splitlines()
    exact = lines[line_start - 1:line_end]
    if hashlib.sha256("\n".join(exact).encode("utf-8")).hexdigest() != segment["sha256"]:
        raise SystemExit(f"source line-slice hash changed: {segment_id}")
    source_lines[segment_id] = lines
    segment_texts[segment_id] = "\n".join(exact)

if segment_sources[VISUAL_ID][0] != VISUAL_REL:
    raise SystemExit("p.214 visual transcription source changed")
if not all(x in "\n".join(source_lines[COMPOSITE_ID]) for x in [
    "1 Richa, III, p. 215.", "2 Cinelli, p. 163", "4 Biblioteca Nazionale, Florence",
    "Senator Francesco Panciatichi", "1 Besides those mentioned", "Giovan GiosefFo dal SHe",
    "8 ib d.. IV p. 428", "Flaminio Comer", "Nos.",
]):
    raise SystemExit("one or more expected OCR note passages changed; re-review before migration")

expected_coverage = {
    COMPOSITE_ID: ("reviewed", "partial", "L127-148"),
    BODY_P212: ("reviewed", "partial", "L99-106"),
    BODY_P213: ("reviewed", "partial", "L109-118"),
    BODY_P214: ("reviewed", "partial", "L121-124"),
}
for segment_id, expected in expected_coverage.items():
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row.get("source_line_ranges")) != expected:
        raise SystemExit(f"unexpected coverage state for {segment_id}: {row}")
if VISUAL_ID in coverage_by_id:
    raise SystemExit(f"visual segment already has coverage; inspect before retry: {VISUAL_ID}")

current_max = max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows)
if current_max != EXPECTED_MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: expected {EXPECTED_MAX_CANDIDATE}, found {current_max}")


def candidate(candidate_id, name, kind, detail, segment_id, line):
    source_file = segment_sources[segment_id][0]
    return {
        "candidate_id": candidate_id,
        "index_entry_id": "",
        "canonical_name": name,
        "index_page_range": "",
        "suggested_type": kind,
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": detail,
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{segment_id}#L{line}",
    }


candidate_specs = [
    candidate(IDS["richa_person"], "Richa, Giuseppe", "person",
              "The bibliography names Giuseppe Richa. The footnote cites volume III, p.215; the bibliography OCR title/volume count remains subject to its later S2 review, and the cited page was not read here.", COMPOSITE_ID, 149),
    candidate(IDS["richa_book"], "Giuseppe Richa, Notizie istoriche delle chiese Fiorentine (volume III cited)", "archive",
              "Bibliography OCR identifies Richa's multi-volume Florentine church history as the likely cited work; preserve its OCR uncertainties in the later bibliography pass. Haskell cites vol. III, p.215; that page was not read here.", COMPOSITE_ID, 149),
    candidate(IDS["longhi_person"], "R. Longhi", "person",
              "The note and bibliography give only R. Longhi; initials are not expanded. Identity alignment remains for S3.", COMPOSITE_ID, 150),
    candidate(IDS["longhi_article"], "Un collezionista di pittura napoletana nella Firenze del ’600 (R. Longhi, Paragone 75, 1956, pp.61-64)", "archive",
              "Identified from the book bibliography's R. Longhi entry. The footnotes say it publishes the cited Del Rosso collection pictures; the article was not independently read.", COMPOSITE_ID, 150),
    candidate(IDS["bilivert_person"], "Giovanni Bilivert", "person",
              "Artist named in p.212 note 3; no matching index candidate is present in the current candidate table. Keep identity open for S3.", COMPOSITE_ID, 151),
    candidate(IDS["dolci_group"], "Three Carlo Dolci pictures owned by the Del Rosso family (including Flight into Egypt)", "work",
              "Haskell reports three pictures by Carlo Dolci in the Del Rosso collection and names one, Flight into Egypt, said to have been sold to Lord Exeter. Keep the group distinct from the named painting candidate.", COMPOSITE_ID, 151),
    candidate(IDS["bilivert_group"], "Four religious pictures by Giovanni Bilivert owned by the Del Rosso family", "work",
              "Source-described group only; the four individual titles are not supplied. Haskell says all four were religious subjects.", COMPOSITE_ID, 151),
    candidate(IDS["cortona_small_madonna"], "Pietro da Cortona’s Madonna and Four Saints (smaller Del Rosso version)", "work",
              "Haskell describes a smaller version obtained for the Del Rosso family in Naples by Luca Giordano. Keep distinct from the earlier picture at S. Agostino, Cortona; the passage gives no present location.", COMPOSITE_ID, 151),
    candidate(IDS["cortona_early_madonna"], "Pietro da Cortona’s earlier Madonna and Four Saints at S. Agostino, Cortona", "work",
              "Earlier picture named only as the comparator for the smaller Del Rosso version. Do not merge the two paintings.", COMPOSITE_ID, 151),
    candidate(IDS["s_agostino_cortona"], "S. Agostino, Cortona", "place",
              "Church named as the location of Pietro da Cortona’s earlier Madonna and Four Saints; the cited pages were not independently checked.", COMPOSITE_ID, 151),
    candidate(IDS["nicola_del_rosso"], "Nicola del Rosso (fourth brother in Haskell’s account)", "person",
              "Named in p.212 note 5 as the fourth brother and son-in-law of Senator Francesco Panciatichi. Preserve this source-level identification for global S3 alignment.", COMPOSITE_ID, 153),
    candidate(IDS["mediceo_filza"], "Archivio Mediceo, Filza 4123", "archive",
              "Archival locator given by Haskell for a letter dated 1686-04-02. Repository catalogue and archival item were not independently consulted.", COMPOSITE_ID, 153),
    candidate(IDS["panciatichi_letter"], "Letter from Naples to Francesco Panciatichi (1686-04-02; Archivio Mediceo, Filza 4123)", "archive",
              "Haskell quotes an otherwise unnamed writer thanking Panciatichi for forwarding the Viceroy's letter to painter Giordani and sending on a reply. Do not infer the writer's identity or identify the Viceroy.", COMPOSITE_ID, 153),
    candidate(IDS["ferri_altarpieces"], "Unidentified Ciro Ferri altarpieces owned by the Del Rosso family", "work",
              "The note reports altarpieces by Ciro Ferri but supplies no title, count, or location. Keep the work group unidentified.", COMPOSITE_ID, 151),
    candidate(IDS["boni_frescoes"], "Mythological frescoes commissioned from Giacomo Antonio Boni for the Del Rosso palace rooms", "work",
              "Haskell says Boni was summoned to decorate the family palace rooms. No individual fresco titles or present locations are given.", VISUAL_ID, 1),
    candidate(IDS["dal_sole_monti_pictures"], "Large historical pictures by Giovan Gioseffo dal Sole and Francesco Monti in the Del Rosso collection", "work",
              "Source-described group; Haskell gives no individual titles or counts in this note. Keep the two named artists and source-level collection context.", VISUAL_ID, 1),
    candidate(IDS["giovanelli_family"], "Giovanelli family (Venice picture owners named by Haskell)", "family",
              "Haskell refers to 'the Giovanelli' as owners of pictures by Luca Giordano or Solimena. Keep distinct from the existing Giovanelli collection candidate until S3 resolves the referent.", VISUAL_ID, 4),
    candidate(IDS["monaco_book"], "Raccolta di centododici stampe di pittura della storia sacra (Pietro Monaco, Venezia 1763)", "archive",
              "Bibliography identifies Pietro Monaco's 1763 print publication. The footnote cites engravings nos. 42, 51, and 89; neither those prints nor the volume were independently inspected beyond the p.214 note and bibliography entry.", VISUAL_ID, 4),
    candidate(IDS["monaco_prints"], "Pietro Monaco engravings nos. 42, 51, and 89 (published 1763)", "work",
              "Three prints identified only by catalogue numbers in Haskell's p.214 note; individual subjects are not supplied here.", VISUAL_ID, 4),
    candidate(IDS["valery_person"], "Valéry (A. C. P.)", "person",
              "Named as a French traveller by Haskell; the bibliography supplies only the initials A. C. P. Do not expand the name without later evidence.", VISUAL_ID, 4),
    candidate(IDS["valery_book"], "Voyages historiques, littéraires et artistiques en Italie (A. C. P. Valery, 2nd ed., 3 vols., Paris 1838)", "archive",
              "Identified from the book bibliography. Haskell quotes vol. I, p.342; that page was not independently read.", VISUAL_ID, 4),
    candidate(IDS["palazzo_contarini"], "Palazzo Contarini mentioned by Valéry (exact palace unresolved)", "place",
              "Haskell's note reports Valéry's reference to a Palazzo Contarini in Venice but does not identify which Contarini palace. Keep separate from existing Contarini family/villa candidates pending S3.", VISUAL_ID, 4),
    candidate(IDS["valery_giordano_group"], "Four Luca Giordano paintings reported at Palazzo Contarini by Valéry", "work",
              "Source-reported group of four paintings; one is described as Aeneas carrying Anchises. Do not infer titles or identity for the other three.", VISUAL_ID, 4),
    candidate(IDS["aeneas_anchises_painting"], "Luca Giordano painting of Aeneas carrying his father Anchises (Valéry quotation)", "work",
              "Painting identified within Valéry's quoted French phrase; its real-world identity and the Palazzo Contarini attribution remain unverified.", VISUAL_ID, 4),
    candidate(IDS["loret_person"], "Mattia Loret", "person",
              "Named in Haskell's note; the bibliography lists the cited article under M. Loret. Do not expand identity beyond the in-book naming without S3 review.", VISUAL_ID, 4),
    candidate(IDS["anchises_person"], "Anchises (named in Valéry’s Aeneas painting description)", "person",
              "Mythological figure named in the quoted title phrase. The note identifies him as Aeneas's father; no separate identity research is part of S2.", VISUAL_ID, 4),
]

new_candidate_ids = {row["candidate_id"] for row in candidate_specs}
if len(new_candidate_ids) != len(candidate_specs) or candidate_ids & new_candidate_ids:
    raise SystemExit("planned candidate IDs collide")
if set(IDS.values()) != new_candidate_ids:
    raise SystemExit("candidate spec list and declared candidate IDs differ")


mention_specs = [
    (COMPOSITE_ID, 149, "Richa", IDS["richa_person"], "Author named in the note; the cited volume is represented by a separate archive candidate."),
    (COMPOSITE_ID, 150, "Cinelli", EXISTING["cinelli"], "Author named in the note; the 1677 collection account is a separate existing archive candidate."),
    (COMPOSITE_ID, 150, "Baldinucci", EXISTING["baldinucci_person"], "Author named in the citation."),
    (COMPOSITE_ID, 150, "The Fäll of Manna", EXISTING["fall_manna"], "S0 OCR reads 'Fäll'; the p.212 print reads 'Fall'. Preserve the source span and record the page-image correction in S2."),
    (COMPOSITE_ID, 150, "Moses striking the Rock", EXISTING["moses_rock"], "Vannini painting named in the note; existing work candidate reused."),
    (COMPOSITE_ID, 150, "R. Longhi", IDS["longhi_person"], "Initials as printed/OCRed; do not expand the author name."),
    (COMPOSITE_ID, 150, "del Rosso collection", EXISTING["del_rosso_family"], "Collection reference in the article title; mapped to its Del Rosso family context without equating a collection with a family KU."),
    (COMPOSITE_ID, 151, "Carlo Dolci", EXISTING["dolci_person"], "Artist named in the note."),
    (COMPOSITE_ID, 151, "three pictures by Carlo Dolci", IDS["dolci_group"], "Source-described group of three; one title is specified immediately afterward."),
    (COMPOSITE_ID, 151, "Flight into Egypt", EXISTING["dolci_flight"], "Named Dolci painting said in the note to have been sold to Lord Exeter."),
    (COMPOSITE_ID, 151, "Lord Exeter", EXISTING["lord_exeter"], "Recipient/sale endpoint named in the source; identity alignment remains global S3 work."),
    (COMPOSITE_ID, 151, "Giovanni Bilivert", IDS["bilivert_person"], "Artist named in the note; new source-derived candidate."),
    (COMPOSITE_ID, 151, "four by Giovanni Bilivert", IDS["bilivert_group"], "Four unnamed religious pictures described as one work group."),
    (COMPOSITE_ID, 151, "Pietro da Cortona", EXISTING["pietro_cortona"], "Artist named as owner/creator of Del Rosso altarpieces."),
    (COMPOSITE_ID, 151, "Ciro Ferri", EXISTING["ciro_ferri"], "Artist named as creator of unnamed Del Rosso altarpieces."),
    (COMPOSITE_ID, 151, "altarpieces by Pietro da Cortona and Ciro Ferri", IDS["ferri_altarpieces"], "Exact collective phrase from the source; the Ferri altarpiece subgroup is unnamed, while the named Cortona Madonna is recorded separately."),
    (COMPOSITE_ID, 151, "Madonna and Four Saints", IDS["cortona_small_madonna"], "Named smaller painting owned by the Del Rosso family."),
    (COMPOSITE_ID, 151, "the early picture in S. Agostino, Cortona", IDS["cortona_early_madonna"], "The earlier comparator, distinct from the smaller Del Rosso version."),
    (COMPOSITE_ID, 151, "S. Agostino, Cortona", IDS["s_agostino_cortona"], "Church location named for the earlier painting."),
    (COMPOSITE_ID, 151, "Naples", EXISTING["naples"], "Location from which Luca Giordano obtained the smaller Cortona painting for the family."),
    (COMPOSITE_ID, 151, "Luca Giordano", EXISTING["luca_giordano"], "Artist and intermediary named in the note."),
    (COMPOSITE_ID, 151, "Gualandi", EXISTING["gualandi_ii"], "Bibliographic source named for the acquisition locator."),
    (COMPOSITE_ID, 151, "Mostra di Pietro da Cortona", EXISTING["mostra_cortona"], "Exhibition publication named as a locator."),
    (COMPOSITE_ID, 151, "Pietro da Cortona", EXISTING["pietro_cortona"], "Author/artist repeated in the publication title.", 1),
    (COMPOSITE_ID, 152, "Biblioteca Nazionale", EXISTING["biblioteca_nazionale"], "Institution named as the archival locator; exact branch is not inferred."),
    (COMPOSITE_ID, 152, "Florence", EXISTING["florence"], "City named in the archival locator."),
    (COMPOSITE_ID, 152, "Poligrafo Gargano", EXISTING["poligrafo_gargano"], "Manuscript collection named in the locator."),
    (COMPOSITE_ID, 153, "Baldinucci", EXISTING["baldinucci_person"], "Author named in the note."),
    (COMPOSITE_ID, 153, "Senator Francesco Panciatichi", EXISTING["panciatichi"], "Historical person named in the note."),
    (COMPOSITE_ID, 153, "Nicola del Rosso", IDS["nicola_del_rosso"], "Named as the fourth brother and Panciatichi's son-in-law; leave identity alignment to S3."),
    (COMPOSITE_ID, 153, "Archivio Mediceo", IDS["mediceo_filza"], "Archive named in the locator."),
    (COMPOSITE_ID, 153, "Filza 4123", IDS["mediceo_filza"], "Specific archival file locator; same archive candidate reused."),
    (COMPOSITE_ID, 153, "Naples", EXISTING["naples"], "Place from which the letter is reported to have been sent."),
    (COMPOSITE_ID, 153, "Pittore Giordani", EXISTING["luca_giordano"], "The quote spells the artist's surname Giordani; map to the existing Luca Giordano candidate while preserving the quoted wording."),
    (COMPOSITE_ID, 154, "Ribera", EXISTING["ribera"], "Artist named among further Del Rosso holdings."),
    (COMPOSITE_ID, 154, "Preti", EXISTING["preti"], "Artist named among further Del Rosso holdings."),
    (COMPOSITE_ID, 154, "Paceco de Rosa", EXISTING["paceco_de_rosa"], "Source spelling preserved; identity alignment remains for S3."),
    (COMPOSITE_ID, 154, "R. Longhi", IDS["longhi_person"], "Same author initials as p.212 note 2; candidate reused."),
    (VISUAL_ID, 1, "Giovan Gioseffo dal Sole", EXISTING["dal_sole"], "Artist named in the page-image transcription; existing candidate reused."),
    (VISUAL_ID, 1, "Francesco Monti", EXISTING["francesco_monti"], "Artist named in the page-image transcription; existing candidate reused."),
    (VISUAL_ID, 1, "large historical pictures", IDS["dal_sole_monti_pictures"], "Source-described group, without individual titles or count."),
    (VISUAL_ID, 1, "Zanotti", EXISTING["zanotti_book"], "First volume locator; bibliography-identified work reused."),
    (VISUAL_ID, 1, "Zanotti", EXISTING["zanotti_book"], "Second volume locator; same work candidate reused.", 1),
    (VISUAL_ID, 1, "Giacomo Antonio Boni", EXISTING["boni"], "Decorator named in the note."),
    (VISUAL_ID, 1, "mythological frescoes", IDS["boni_frescoes"], "Source-described palace decoration group; individual frescoes are unnamed."),
    (VISUAL_ID, 1, "Soprani", EXISTING["soprani_book"], "Bibliography-identified volume-II source reused."),
    (VISUAL_ID, 2, "De Dominici", EXISTING["de_dominici_person"], "Author named in the citation."),
    (VISUAL_ID, 2, "De Dominici, IV", EXISTING["de_dominici_book"], "Volume-IV publication cited; same page also mentions its author."),
    (VISUAL_ID, 3, "Ibid.", EXISTING["de_dominici_book"], "Resolves to De Dominici volume IV from p.214 note 2."),
    (VISUAL_ID, 3, "Bologna", EXISTING["bologna_book"], "Ferdinando Bologna publication candidate reused."),
    (VISUAL_ID, 4, "De Dominici", EXISTING["de_dominici_person"], "Author named in the first citation on the line."),
    (VISUAL_ID, 4, "De Dominici, IV", EXISTING["de_dominici_book"], "Volume-IV publication cited at the start of note 4."),
    (VISUAL_ID, 4, "Bologna", EXISTING["bologna_book"], "Ferdinando Bologna publication cited at p.164."),
    (VISUAL_ID, 4, "Luca Giordano", EXISTING["luca_giordano"], "Artist described as having admirers in Venice."),
    (VISUAL_ID, 4, "Solimena", EXISTING["solimena"], "Artist described as having admirers in Venice."),
    (VISUAL_ID, 4, "Venice", EXISTING["venice"], "Place where Haskell says both artists had admirers."),
    (VISUAL_ID, 4, "the Labia", EXISTING["labia_family"], "Family named among picture owners; chapter 9 is cross-referenced, not processed here."),
    (VISUAL_ID, 4, "Procuratore Canale", EXISTING["procuratore_canale"], "Title and surname as given by Haskell; identity alignment remains for S3."),
    (VISUAL_ID, 4, "Flaminio Corner", EXISTING["flaminio_corner"], "Physical p.214 reads Corner; composite S0 OCR reads Comer. Correction is recorded in S2."),
    (VISUAL_ID, 4, "the Giovanelli", IDS["giovanelli_family"], "Family referent in Haskell's sentence; distinct from the existing collection candidate until S3."),
    (VISUAL_ID, 4, "the Widmann", EXISTING["widmann_family"], "Family named among picture owners."),
    (VISUAL_ID, 4, "Pietro Monaco", EXISTING["pietro_monaco"], "Printmaker named in the note."),
    (VISUAL_ID, 4, "engravings of Pietro Monaco published in 1763, Nos. 42, 51 and 89", IDS["monaco_prints"], "Three source-identified prints, individually untitled in this note."),
    (VISUAL_ID, 4, "published in 1763", IDS["monaco_book"], "Bibliographic year matched to the Monaco publication entry; the publication itself was not independently examined."),
    (VISUAL_ID, 4, "Valéry", IDS["valery_person"], "French traveller named by Haskell; bibliography uses unaccented Valery and initials A. C. P."),
    (VISUAL_ID, 4, "I, p. 342", IDS["valery_book"], "Volume and page locator attached to Valéry in the note; the bibliography supplies the book title, and the cited page was not independently read."),
    (VISUAL_ID, 4, "the Palazzo Contarini", IDS["palazzo_contarini"], "Palace named by Valéry; exact building remains unresolved."),
    (VISUAL_ID, 4, "quatre des meilleurs tableaux de Luc Giordano", IDS["valery_giordano_group"], "Valéry's quoted report of four Giordano paintings in the palace."),
    (VISUAL_ID, 4, "Luc Giordano", EXISTING["luca_giordano"], "French quotation form of the existing Luca Giordano candidate."),
    (VISUAL_ID, 4, "l’Enée emportant son père Anchise", IDS["aeneas_anchises_painting"], "Painting phrase quoted by Valéry; real-world identification remains open."),
    (VISUAL_ID, 4, "l’Enée", EXISTING["aeneas"], "Aeneas named within Valéry's quoted painting description."),
    (VISUAL_ID, 4, "Anchise", IDS["anchises_person"], "Anchises named within Valéry's quoted painting description."),
    (VISUAL_ID, 4, "Mattia Loret", IDS["loret_person"], "Author named in the note; his cited publication has an existing archive candidate."),
]


def mention_row(index, spec):
    segment_id, line_number, surface, candidate_id, note, *occurrence_arg = spec
    occurrence = occurrence_arg[0] if occurrence_arg else 0
    source_file, segment_start, _ = segment_sources[segment_id]
    file_lines = source_lines[segment_id]
    segment_lines_local = file_lines[segment_start - 1:segment_start - 1 + (4 if segment_id == VISUAL_ID else 32)]
    target_line = file_lines[line_number - 1]
    starts = []
    cursor = 0
    while True:
        found = target_line.find(surface, cursor)
        if found < 0:
            break
        starts.append(found)
        cursor = found + max(1, len(surface))
    if occurrence >= len(starts):
        raise SystemExit(f"mention surface absent: {segment_id} L{line_number} {surface!r} occurrence={occurrence}")
    local_line = line_number - segment_start
    line_offset = sum(len(line) + 1 for line in segment_lines_local[:local_line])
    start = line_offset + starts[occurrence]
    end = start + len(surface)
    if segment_texts[segment_id][start:end] != surface:
        raise SystemExit(f"mention span does not reproduce: {segment_id} L{line_number} {surface!r}")
    return {
        "mention_id": f"m-chp8-p212-214-notes-{index:03d}",
        "segment_id": segment_id,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    }


new_mentions = [mention_row(i, spec) for i, spec in enumerate(mention_specs, 1)]
if len({row["mention_id"] for row in new_mentions}) != len(new_mentions) or mention_ids & {row["mention_id"] for row in new_mentions}:
    raise SystemExit("planned mention IDs collide")

BODY_LINKS = {
    "st-chp8-p212-altar-picture-left-for-pupil-completion": 1,
    "st-chp8-p212-four-scenes-made-for-house-and-considered-finest": 2,
    "st-chp8-p212-carlo-dolci-painted-for-del-rosso-family": 3,
    "st-chp8-p212-1613-grand-duke-letter-about-antonio-sons": 4,
    "st-chp8-p212-giordano-visited-florence-and-stayed-at-family-house-1679": 5,
    "st-chp8-p213-collection-emphasis-on-naples-and-neglect-of-rome": 1,
    "st-chp8-p214-durazzo-naples-continuation": 1,
    "st-chp8-p214-giordano-four-canvases-for-durazzo": 2,
    "st-chp8-p214-solimena-two-histories": 3,
    "st-chp8-p214-baglioni-neapolitan-holdings": 4,
}
statement_by_id = {row["statement_id"]: row for row in statement_rows}
for statement_id, marker in BODY_LINKS.items():
    row = statement_by_id.get(statement_id)
    if not row:
        raise SystemExit(f"body statement missing for footnote link: {statement_id}")
    if row.get("qualifiers", {}).get("footnote_marker") not in (None, marker):
        raise SystemExit(f"unexpected footnote marker on {statement_id}")
BODY_BY_MARKER = {}
for statement_id, marker in BODY_LINKS.items():
    BODY_BY_MARKER.setdefault(marker, []).append(statement_id)


def stmt(statement_id, segment_id, start, end, page, marker, predicate, claim, qualification,
         quote, speaker="Haskell footnote", text_layer="footnote content", subject=None,
         object_=None, mentioned=(), citations=(), extra=None, linked=None):
    return {
        "statement_id": statement_id,
        "segment_id": segment_id,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": start,
            "source_line_end": end,
            "printed_page": page,
            "pdf_physical_page": {212: 10, 213: 11, 214: 12}[page],
            "claim": claim,
            "speaker": speaker,
            "text_layer": text_layer,
            "qualification": qualification,
            "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
            "footnote_marker": marker,
            "linked_body_statement_ids": linked if linked is not None else BODY_BY_MARKER[marker],
            "footnote_segment": segment_id,
            "footnote_body_link_status": "linked",
            "citations": list(citations),
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": segment_sources[segment_id][0],
        **({"qualifiers": {**{
            "source_line_start": start,
            "source_line_end": end,
            "printed_page": page,
            "pdf_physical_page": {212: 10, 213: 11, 214: 12}[page],
            "claim": claim,
            "speaker": speaker,
            "text_layer": text_layer,
            "qualification": qualification,
            "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
            "footnote_marker": marker,
            "linked_body_statement_ids": linked if linked is not None else BODY_BY_MARKER[marker],
            "footnote_segment": segment_id,
            "footnote_body_link_status": "linked",
            "citations": list(citations),
        }, **extra}} if extra else {}),
    }


book = EXISTING
new_statements = [
    stmt("st-chp8-p212-n1-cite-richa", COMPOSITE_ID, 149, 149, 212, 1,
         "footnote_citation", "Haskell cites Richa, volume III, p.215, for the p.212 account of Ottavio Vannini's altar picture being left for completion by a pupil.",
         "Only the bibliographic locator is represented; the cited volume and page were not independently read.",
         "Richa, III, p. 215.", object_=IDS["richa_book"], mentioned=[IDS["richa_person"], IDS["richa_book"]],
         citations=[{"source_candidate_id": IDS["richa_book"], "volume": "III", "page": "215"}]),
    stmt("st-chp8-p212-n2-cite-cinelli-baldinucci", COMPOSITE_ID, 150, 150, 212, 2,
         "footnote_citation", "Haskell cites Cinelli, p.163, and Baldinucci, volume VI (1728), p.145, for Vannini's four named scenes.",
         "The cited pages were not independently read; preserve this as a locator rather than additional confirmation.",
         "Cinelli, p. 163, and Baldinucci, VI, 1728, p. 145.", mentioned=[book["cinelli"], book["cinelli_book"], book["baldinucci_person"], book["baldinucci_book"]],
         citations=[{"source_candidate_id": book["cinelli_book"], "page": "163"}, {"source_candidate_id": book["baldinucci_book"], "volume": "VI", "year": 1728, "page": "145"}]),
    stmt("st-chp8-p212-n2-longhi-publishes-vannini-scenes", COMPOSITE_ID, 150, 150, 212, 2,
         "pictures_published_by_longhi", "Haskell says The Fall of Manna and Moses striking the Rock were published by R. Longhi in a 1956 article about the Del Rosso collection.",
         "The original OCR misreads 'Fall' as 'Fäll'; the printed page reads 'Fall'. The bibliography identifies the article, which was not independently read.",
         "Two of the pictures—The Fäll of Manna and Moses striking the Rock—are published by R. Longhi, 1956, in an article on the del Rosso collection.",
         subject=IDS["longhi_person"], object_=IDS["longhi_article"],
         mentioned=[book["fall_manna"], book["moses_rock"], IDS["longhi_person"], IDS["longhi_article"], book["del_rosso_family"]],
         citations=[{"source_candidate_id": IDS["longhi_article"], "year": 1956}],
         extra={"ocr_corrections": [{"source_file": COMPOSITE_REL, "source_line": 150, "ocr": "The Fäll of Manna", "print": "The Fall of Manna", "basis": "CHP-8.pdf physical page 10."}]}),
    stmt("st-chp8-p212-n3-dolci-and-bilivert-pictures", COMPOSITE_ID, 151, 151, 212, 3,
         "del_rosso_family_owned_dolci_and_bilivert_pictures", "Haskell reports that the Del Rosso family owned three pictures by Carlo Dolci, including a Flight into Egypt said to have been sold to Lord Exeter, and four pictures by Giovanni Bilivert; he says all these were religious subjects.",
         "The Bilivert picture titles are not given. 'Sold to Lord Exeter' is Haskell's report, not a provenance independently checked here.",
         "They owned three pictures by Carlo Dolci—including the Flight into Egypt sold to Lord Exeter— and four by Giovanni Bilivert. All these were of religious subjects.",
         subject=book["del_rosso_family"], object_=IDS["dolci_group"],
         mentioned=[book["del_rosso_family"], book["dolci_person"], IDS["dolci_group"], book["dolci_flight"], book["lord_exeter"], IDS["bilivert_person"], IDS["bilivert_group"]]),
    stmt("st-chp8-p212-n3-bilivert-picture-group", COMPOSITE_ID, 151, 151, 212, 3,
         "del_rosso_family_owned_bilivert_picture_group", "Haskell reports four religious pictures by Giovanni Bilivert in the Del Rosso collection.",
         "The four individual works are unnamed; the source provides no titles or separate descriptions.",
         "and four by Giovanni Bilivert. All these were of religious subjects.",
         subject=book["del_rosso_family"], object_=IDS["bilivert_group"],
         mentioned=[book["del_rosso_family"], IDS["bilivert_person"], IDS["bilivert_group"]]),
    stmt("st-chp8-p212-n3-ferri-altarpieces", COMPOSITE_ID, 151, 151, 212, 3,
         "del_rosso_family_owned_ferri_altarpieces", "Haskell says the Del Rosso family also owned altarpieces by Ciro Ferri.",
         "No individual title, count, date, location, or version is supplied for Ferri's altarpiece(s).",
         "They also owned altarpieces by Pietro da Cortona and Ciro Ferri.",
         subject=book["del_rosso_family"], object_=IDS["ferri_altarpieces"],
         mentioned=[book["del_rosso_family"], book["pietro_cortona"], book["ciro_ferri"], IDS["ferri_altarpieces"]]),
    stmt("st-chp8-p212-n3-cortona-madonna-four-saints", COMPOSITE_ID, 151, 151, 212, 3,
         "cortona_madonna_small_version_obtained_for_del_rosso_family", "Haskell identifies Pietro da Cortona's Madonna and Four Saints as a smaller version of an earlier picture at S. Agostino, Cortona, and says Luca Giordano obtained the smaller painting for the Del Rosso family in Naples.",
         "The two versions are kept distinct. Haskell does not give the smaller version's present location or a date for its acquisition; the cited pages were not independently read.",
         "Pietro da Cortona’s Madonna and Four Saints—a smaller version of the early picture in S. Agostino, Cortona—was obtained for them in-Naples by Luca Giordano—",
         subject=IDS["cortona_small_madonna"], object_=book["del_rosso_family"],
         mentioned=[book["pietro_cortona"], IDS["cortona_small_madonna"], IDS["cortona_early_madonna"], IDS["s_agostino_cortona"], book["del_rosso_family"], book["naples"], book["luca_giordano"]]),
    stmt("st-chp8-p212-n3-cite-gualandi-mostra", COMPOSITE_ID, 151, 151, 212, 3,
         "footnote_citation", "Haskell points to Gualandi, volume II, p.122, and Mostra di Pietro da Cortona, p.28, for the smaller Cortona picture.",
         "The cited pages were not independently read; the exhibition publication is reused from the existing candidate table.",
         "Gualandi, II, p. 122, and Mostra di Pietro da Cortona, p. 28.", mentioned=[book["gualandi_ii"], book["mostra_cortona"]],
         citations=[{"source_candidate_id": book["gualandi_ii"], "volume": "II", "page": "122"}, {"source_candidate_id": book["mostra_cortona"], "page": "28"}]),
    stmt("st-chp8-p212-n4-polgigrafo-archive-locator", COMPOSITE_ID, 152, 152, 212, 4,
         "archival_locator", "Haskell identifies the Biblioteca Nazionale in Florence and its Poligrafo Gargano collection as the archival locator.",
         "This preserves the printed locator only; the collection and shelfmark were not independently checked.",
         "Biblioteca Nazionale, Florence—Poligrafo Gargano.", object_=book["poligrafo_gargano"],
         mentioned=[book["biblioteca_nazionale"], book["florence"], book["poligrafo_gargano"]],
         citations=[{"source_candidate_id": book["poligrafo_gargano"]}]),
    stmt("st-chp8-p212-n5-cite-baldinucci", COMPOSITE_ID, 153, 153, 212, 5,
         "footnote_citation", "Haskell cites Baldinucci, volume VI (1728), p.506, for the Panciatichi passage.",
         "The cited page was not independently read.", "Baldinucci, VI, 1728, p. 506.",
         mentioned=[book["baldinucci_person"], book["baldinucci_book"]],
         citations=[{"source_candidate_id": book["baldinucci_book"], "volume": "VI", "year": 1728, "page": "506"}]),
    stmt("st-chp8-p212-n5-panciatichi-office", COMPOSITE_ID, 153, 153, 212, 5,
         "panciatichi_held_primo_segretario_from_1682", "Haskell says Senator Francesco Panciatichi held the office of Primo Segretario from 1682.",
         "The source's date and office wording are retained; the office tenure was not independently verified.",
         "Senator Francesco Panciatichi, who from 1682 held the important post of Primo Segretario",
         subject=book["panciatichi"], mentioned=[book["panciatichi"]]),
    stmt("st-chp8-p212-n5-panciatichi-nicola-kinship", COMPOSITE_ID, 153, 153, 212, 5,
         "panciatichi_was_father_in_law_of_nicola_del_rosso", "Haskell identifies Nicola del Rosso as Francesco Panciatichi's son-in-law and as the fourth Del Rosso brother.",
         "Preserve Haskell's source-level identity and kinship claim; the personal identities and family relationship remain for later S3/S5 review.",
         "was the father-in-law of Nicola del Rosso, the fourth brother.",
         subject=book["panciatichi"], object_=IDS["nicola_del_rosso"],
         mentioned=[book["panciatichi"], IDS["nicola_del_rosso"], book["del_rosso_family"]]),
    stmt("st-chp8-p212-n5-archivio-letter-content", COMPOSITE_ID, 153, 153, 212, 5,
         "archival_letter_reports_viceroy_letter_forwarded_to_giordani", "Haskell reports a letter in Archivio Mediceo, Filza 4123, addressed to Panciatichi from Naples and dated 2 April 1686. Its unnamed writer thanks him for ensuring that a Viceroy's letter to painter Giordani was delivered and for forwarding the reply.",
         "The writer and Viceroy are not named. The original archival letter and file were not consulted; preserve the nested quotation/reporting level and the source spelling 'Giordani'.",
         "In the Archivio Mediceo (Filza 4123) is a letter to him from Naples, dated 2 April 1686: ‘Molto obbligantemente resto da V.S.IlLma favorito nel particolare della lettera del Sig.r V.Re diretta al Pittore Giordani, mentre oltre la briga presasi di fargliela sicuramente recapitare, s’è degnata anche d’assumersi il pensiero deviarmene la risposta, che già da me è stata presentata à S.E.",
         object_=IDS["panciatichi_letter"],
         mentioned=[IDS["mediceo_filza"], IDS["panciatichi_letter"], book["panciatichi"], book["naples"], book["luca_giordano"]],
         citations=[{"source_candidate_id": IDS["mediceo_filza"], "file": "Filza 4123"}]),
    stmt("st-chp8-p213-n1-more-del-rosso-pictures", COMPOSITE_ID, 154, 154, 213, 1,
         "del_rosso_family_owned_pictures_by_ribera_preti_and_paceco_de_rosa", "Haskell adds pictures by Ribera, Preti, and Paceco de Rosa to the Del Rosso holdings.",
         "The source spelling Paceco de Rosa is preserved. The artist identities and individual works remain for global S3; no titles are given.",
         "Besides those mentioned, they also owned pictures by Ribera, Preti and Paceco de Rosa",
         subject=book["del_rosso_family"], mentioned=[book["del_rosso_family"], book["ribera"], book["preti"], book["paceco_de_rosa"]]),
    stmt("st-chp8-p213-n1-longhi-publication", COMPOSITE_ID, 154, 154, 213, 1,
         "paceco_de_rosa_pictures_published_by_longhi", "Haskell says the Paceco de Rosa pictures are published by R. Longhi in 1956.",
         "The bibliography identifies the Longhi article, but it was not independently read; 'the latter' refers to Paceco de Rosa, not to all three named artists.",
         "the latter are published by R. Longhi, 1956.", subject=IDS["longhi_person"], object_=IDS["longhi_article"],
         mentioned=[book["paceco_de_rosa"], IDS["longhi_person"], IDS["longhi_article"]],
         citations=[{"source_candidate_id": IDS["longhi_article"], "year": 1956}]),
    stmt("st-chp8-p214-n1-cite-zanotti-vol-i", VISUAL_ID, 1, 1, 214, 1,
         "footnote_citation", "Haskell cites Zanotti, volume I, p.299, for the Del Rosso collection's historical pictures.",
         "The cited page was not independently read; bibliography-identified Zanotti publication is reused.",
         "Zanotti, I, p. 299", mentioned=[book["zanotti_book"]], citations=[{"source_candidate_id": book["zanotti_book"], "volume": "I", "page": "299"}]),
    stmt("st-chp8-p214-n1-cite-zanotti-vol-ii", VISUAL_ID, 1, 1, 214, 1,
         "footnote_citation", "Haskell cites Zanotti, volume II, pp.120 and 231, for the Del Rosso paintings and Boni decoration.",
         "The cited pages were not independently read. The page-image transcription corrects OCR 'H' to printed 'II'.",
         "and II, p. 120", mentioned=[book["zanotti_book"]], citations=[{"source_candidate_id": book["zanotti_book"], "volume": "II", "page": "120"}],
         extra={"ocr_corrections": [{"source_file": COMPOSITE_REL, "source_line": 155, "ocr": "H", "print": "II", "basis": "CHP-8.pdf physical page 12."}]}),
    stmt("st-chp8-p214-n1-dal-sole-monti-historical-pictures", VISUAL_ID, 1, 1, 214, 1,
         "del_rosso_family_owned_historical_pictures_by_dal_sole_and_monti", "Haskell says the Del Rosso family owned large historical pictures by Giovan Gioseffo dal Sole and Francesco Monti.",
         "No individual picture title, count, or location is supplied in the note.",
         "They owned large historical pictures by Giovan Gioseffo dal Sole and Francesco Monti",
         subject=book["del_rosso_family"], object_=IDS["dal_sole_monti_pictures"],
         mentioned=[book["del_rosso_family"], book["dal_sole"], book["francesco_monti"], IDS["dal_sole_monti_pictures"]],
         extra={"ocr_corrections": [{"source_file": COMPOSITE_REL, "source_line": 155, "ocr": "Giovan GiosefFo dal SHe", "print": "Giovan Gioseffo dal Sole", "basis": "CHP-8.pdf physical page 12."}]}),
    stmt("st-chp8-p214-n1-cite-soprani", VISUAL_ID, 1, 1, 214, 1,
         "footnote_citation", "Haskell cites Soprani, volume II, pp.376-380, for the Boni decoration.",
         "The cited pages were not independently read; the bibliography-identified edition is reused. The page image corrects OCR 'H' to printed 'II'.",
         "and Soprani, II, pp. 376-80.", mentioned=[book["soprani_book"]],
         citations=[{"source_candidate_id": book["soprani_book"], "volume": "II", "pages": "376-380"}],
         extra={"ocr_corrections": [{"source_file": COMPOSITE_REL, "source_line": 155, "ocr": "H", "print": "II", "basis": "CHP-8.pdf physical page 12."}]}),
    stmt("st-chp8-p214-n1-boni-mythological-frescoes", VISUAL_ID, 1, 1, 214, 1,
         "del_rosso_family_summoned_boni_to_decorate_palace_rooms", "Haskell says the Del Rosso family summoned Giacomo Antonio Boni to decorate rooms in their palace with mythological frescoes.",
         "The palace is not identified by name in this note; no fresco titles or completion dates are supplied.",
         "they summoned Giacomo Antonio Boni to decorate the rooms of their palace with mythological frescoes",
         subject=book["del_rosso_family"], object_=IDS["boni_frescoes"],
         mentioned=[book["del_rosso_family"], book["boni"], IDS["boni_frescoes"]]),
    stmt("st-chp8-p214-n2-cite-de-dominici", VISUAL_ID, 2, 2, 214, 2,
         "footnote_citation", "Haskell cites De Dominici, volume IV, p.188, for the p.214 Giordano canvases.",
         "The cited page was not independently read.", "De Dominici, IV, p. 188.",
         mentioned=[book["de_dominici_person"], book["de_dominici_book"]],
         citations=[{"source_candidate_id": book["de_dominici_book"], "volume": "IV", "page": "188"}],
         extra={"ocr_corrections": [{"source_file": COMPOSITE_REL, "source_line": 156, "ocr": "8 ib d.. IV", "print": "3 Ibid., IV", "basis": "CHP-8.pdf physical page 12; note numbering corrected from OCR 8 to printed 3."}]}),
    stmt("st-chp8-p214-n3-cite-de-dominici-bologna", VISUAL_ID, 3, 3, 214, 3,
         "footnote_citation", "Haskell cites De Dominici, volume IV, p.428, and Ferdinando Bologna, pp.89-90, for Solimena's two further histories.",
         "The cited pages were not independently read. 'Ibid.' resolves to De Dominici IV, cited in p.214 note 2.",
         "Ibid., IV, p. 428, and Bologna, pp. 89-90.", mentioned=[book["de_dominici_person"], book["de_dominici_book"], book["bologna_book"]],
         citations=[{"source_candidate_id": book["de_dominici_book"], "volume": "IV", "page": "428"}, {"source_candidate_id": book["bologna_book"], "pages": "89-90"}],
         extra={"ocr_corrections": [{"source_file": COMPOSITE_REL, "source_line": 156, "ocr": "8 ib d.. IV p. 428, and Bologna", "print": "3 Ibid., IV, p. 428, and Bologna", "basis": "CHP-8.pdf physical page 12; note numbering and citation punctuation corrected in S2."}]}),
    stmt("st-chp8-p214-n4-cite-de-dominici-bologna", VISUAL_ID, 4, 4, 214, 4,
         "footnote_citation", "Haskell cites De Dominici, volume IV, pp.87, 188, and 428, and Bologna, p.164, for the Venetian picture-owner discussion.",
         "The cited pages were not independently read.",
         "De Dominici, IV, pp. 87, 188 and 428, and Bologna, p. 164.",
         mentioned=[book["de_dominici_person"], book["de_dominici_book"], book["bologna_book"]],
         citations=[{"source_candidate_id": book["de_dominici_book"], "volume": "IV", "pages": "87, 188, 428"}, {"source_candidate_id": book["bologna_book"], "page": "164"}],
         extra={"ocr_corrections": [{"source_file": COMPOSITE_REL, "source_line": 157, "ocr": "Flaminio Comer", "print": "Flaminio Corner", "basis": "CHP-8.pdf physical page 12."}, {"source_file": COMPOSITE_REL, "source_line": 157, "ocr": "Nos.", "print": "Nos. 42, 51 and 89 ... Mattia Loret.", "basis": "Continuation transcribed from CHP-8.pdf physical page 12; see derived p.214 visual-transcription segment."}]}),
    stmt("st-chp8-p214-n4-venetian-admirers", VISUAL_ID, 4, 4, 214, 4,
         "giordano_and_solimena_had_admirers_in_venice", "Haskell says both Luca Giordano and Francesco Solimena had a number of admirers in Venice.",
         "This is Haskell's summary; the following list names picture-owning families and officials, but does not assign each owner to one artist or work.",
         "Both Luca Giordano and Solimena had a number of admirers in Venice.",
         mentioned=[book["luca_giordano"], book["solimena"], book["venice"]]),
    stmt("st-chp8-p214-n4-venetian-patrons-owned-pictures", VISUAL_ID, 4, 4, 214, 4,
         "venetian_patrons_owned_pictures_by_giordano_or_solimena", "Haskell says the Labia, Procuratore Canale, Flaminio Corner, the Giovanelli, and the Widmann all owned pictures by one or the other of Giordano and Solimena.",
         "The wording does not identify which patron owned works by which artist, and no individual picture is named. Keep assignments unresolved.",
         "Besides the Labia, who are discussed separately in Chapter 9, the Procuratore Canale, Flaminio Corner, the Giovanelli and the Widmann all owned pictures by one or other of them",
         mentioned=[book["labia_family"], book["procuratore_canale"], book["flaminio_corner"], IDS["giovanelli_family"], book["widmann_family"], book["luca_giordano"], book["solimena"]]),
    stmt("st-chp8-p214-n4-cite-monaco-engravings", VISUAL_ID, 4, 4, 214, 4,
         "footnote_citation", "Haskell points readers to Pietro Monaco's 1763 engravings, nos.42, 51, and 89.",
         "The bibliography identifies Monaco's print publication. The three prints were not independently inspected; no subject titles are supplied in this note.",
         "and the engravings of Pietro Monaco published in 1763, Nos. 42, 51 and 89.",
         object_=IDS["monaco_book"], mentioned=[book["pietro_monaco"], IDS["monaco_prints"], IDS["monaco_book"]],
         citations=[{"source_candidate_id": IDS["monaco_book"], "numbers": "42, 51, 89", "year": 1763}]),
    stmt("st-chp8-p214-n4-valery-contarini-paintings", VISUAL_ID, 4, 4, 214, 4,
         "valery_reported_four_giordano_paintings_at_palazzo_contarini", "Haskell quotes Valéry as saying Palazzo Contarini contained four of Luca Giordano's best paintings, including one of Aeneas carrying his father Anchises.",
         "This is a nested report: Valéry as quoted by Haskell. The cited volume/page, building identity, attribution, and painting identity were not independently verified; the other three paintings remain unnamed.",
         "Early in the nineteenth century the French traveller Valéry (I, p. 342) said that the Palazzo Contarini contained ‘quatre des meilleurs tableaux de Luc Giordano, parmi lesquels l’Enée emportant son père Anchise.’",
         speaker="Valéry, as quoted by Haskell", text_layer="nested quotation",
         subject=IDS["valery_giordano_group"], object_=IDS["palazzo_contarini"],
         mentioned=[IDS["valery_person"], IDS["valery_book"], IDS["palazzo_contarini"], IDS["valery_giordano_group"], book["luca_giordano"], IDS["aeneas_anchises_painting"], book["aeneas"], IDS["anchises_person"]],
         citations=[{"source_candidate_id": IDS["valery_book"], "volume": "I", "page": "342"}]),
    stmt("st-chp8-p214-n4-cite-loret", VISUAL_ID, 4, 4, 214, 4,
         "footnote_citation", "Haskell directs readers to Mattia Loret for Neapolitan artists in Rome.",
         "The note gives no page locator. The bibliography identifies Loret's article; it was not independently read.",
         "For Neapolitan artists in Rome see Mattia Loret.",
         object_=book["loret_article"], mentioned=[IDS["loret_person"], book["loret_article"]],
         citations=[{"source_candidate_id": book["loret_article"]}]),
]

planned_statement_ids = {row["statement_id"] for row in new_statements}
if len(planned_statement_ids) != len(new_statements) or statement_ids & planned_statement_ids:
    raise SystemExit("planned statement IDs collide")

all_candidate_ids = candidate_ids | new_candidate_ids
new_candidate_by_id = {row["candidate_id"]: row for row in candidate_specs}
all_candidate_by_id = {**candidate_by_id, **new_candidate_by_id}
for row in new_mentions:
    if row["candidate_id"] not in all_candidate_ids:
        raise SystemExit(f"mention has unknown candidate: {row['mention_id']} -> {row['candidate_id']}")
for row in new_statements:
    q = row["qualifiers"]
    source_lines_for_statement = source_lines[row["segment_id"]]
    start, end = q["source_line_start"], q["source_line_end"]
    cited = "\n".join(source_lines_for_statement[start - 1:end])
    normalize = lambda s: " ".join(s.split())
    if normalize(row["original_quote"]) not in normalize(cited):
        raise SystemExit(f"statement quote not reproducible: {row['statement_id']}\n{row['original_quote']}")
    refs = set(q.get("mentioned_candidate_ids", []))
    if row.get("subject_candidate_id"):
        refs.add(row["subject_candidate_id"])
    if row.get("object_candidate_id"):
        refs.add(row["object_candidate_id"])
    for citation in q.get("citations", []):
        if citation.get("source_candidate_id"):
            refs.add(citation["source_candidate_id"])
    if not refs <= all_candidate_ids:
        raise SystemExit(f"statement has missing candidate FK: {row['statement_id']}: {refs-all_candidate_ids}")
    if not set(q["linked_body_statement_ids"]) <= set(statement_by_id):
        raise SystemExit(f"footnote links to absent body statement: {row['statement_id']}")

body_new = []
for original in statement_rows:
    row = dict(original)
    if row["statement_id"] in BODY_LINKS:
        q = dict(row.get("qualifiers", {}))
        q["footnote_marker"] = BODY_LINKS[row["statement_id"]]
        q["footnote_segment"] = COMPOSITE_ID if row["statement_id"].startswith("st-chp8-p212") or row["statement_id"].startswith("st-chp8-p213") else VISUAL_ID
        q["footnote_statement_ids"] = [s["statement_id"] for s in new_statements if BODY_LINKS[row["statement_id"]] == s["qualifiers"]["footnote_marker"] and s["qualifiers"].get("printed_page") == ({1: 212, 2: 212, 3: 212, 4: 212, 5: 212}[BODY_LINKS[row["statement_id"]]] if row["statement_id"].startswith("st-chp8-p212") else (213 if row["statement_id"].startswith("st-chp8-p213") else 214))]
        row["qualifiers"] = q
    body_new.append(row)

coverage_new = []
coverage_updates = {
    COMPOSITE_ID: {
        "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L127-157",
        "note": "P.204 notes 1-3 (L127-129), p.205 notes 1-4 (L130-133), p.206 notes 1-2 (L134-135), p.207 notes 1-2 (L136-137), p.208 notes 1-7 (L138-144), p.209 note 1 (L145), p.211 notes 1-3 (L146-148) and p.212-213 notes 1-5/1 (L149-154) have been read and migrated or reused. L146-148 reuse the previously completed p.211 visual transcription without duplicate mentions/statements. P.214 notes 1-4 (L155-157) are canonically transcribed in the derived p.214 visual segment; note 2 was absent from S0 OCR and note 4 was truncated after 'Nos.'. Page-image corrections and continuation are recorded in S2; S0 remains unchanged. All note statements link to printed body markers; cited pages and archival objects not otherwise noted remain unread/unverified.",
    },
    BODY_P212: {
        "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L99-106",
        "note": "P.212 body read against CHP-8.pdf physical p.10. Notes 1-5 from composite lines L149-153 have been migrated and linked to the corresponding body statement markers. Page-image corrections are recorded in S2; source OCR remains unchanged.",
    },
    BODY_P213: {
        "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L109-118",
        "note": "P.213 body read against CHP-8.pdf physical p.11. Note 1 from composite line L154 has been migrated and linked to the collection marker. Cross-page Durazzo sentence is closed by p.214 L121; source OCR remains unchanged.",
    },
    BODY_P214: {
        "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L121-124",
        "note": "P.214 body read against CHP-8.pdf physical p.12. Notes 1-4 are transcribed in the derived visual segment and migrated; footnote markers are attached to the respective p.214 body statements. OCR note 2 was absent and note 4 was truncated, both corrected only in the S2 supplement; the existing Old Testament dash correction remains recorded in S2.",
    },
}
found_coverage = set()
for original in coverage_rows:
    row = dict(original)
    if row["segment_id"] in coverage_updates:
        row.update(coverage_updates[row["segment_id"]])
        found_coverage.add(row["segment_id"])
    coverage_new.append(row)
if found_coverage != set(coverage_updates):
    raise SystemExit(f"coverage targets missing: {set(coverage_updates)-found_coverage}")
coverage_new.append({
    "chapter": "chp-8",
    "segment_id": VISUAL_ID,
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L1-4",
    "note": "Derived page-image transcription of CHP-8.pdf physical p.12 notes 1-4. It fills the S0 OCR omission of note 2 and the p.214 note 4 continuation after 'Nos.'; it also supplies print readings for the overlapping OCR text L155-L157. Notes 1-4 are linked to p.214 body markers. The overlapping composite OCR lines are not duplicated in mentions/statements; the original S0 OCR is unchanged.",
})


def preview():
    print(f"validated sources: {COMPOSITE_ID} L149-157 and {VISUAL_ID} L1-4")
    print(f"new candidates: {len(candidate_specs)} ({min(new_candidate_ids)} through {max(new_candidate_ids)})")
    print(f"new mentions: {len(new_mentions)}")
    print(f"new statements: {len(new_statements)}")
    print("coverage: p.212, p.213, p.214 body segments and composite notes complete; new p.214 visual segment complete")
    print("footnote links: p.212 notes 1-5; p.213 note 1; p.214 notes 1-4")
    print("overlap: p.211 L146-148 reused; no duplicate mentions/statements")
    print("source corrections: S0 unchanged; p.214 note 2 omission and note 4 continuation preserved in visual transcription")


def apply():
    paths = [candidate_path, mention_path, statement_path, coverage_path]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("one or more recovery backups already exist; inspect before retrying")
    for source, backup in zip(paths, backups):
        shutil.copy2(source, backup)
    updated_candidates = candidate_rows + candidate_specs
    updated_mentions = mention_rows + new_mentions
    updated_statements = body_new + new_statements
    write_csv_atomic(candidate_path, candidate_fields, updated_candidates)
    write_csv_atomic(mention_path, mention_fields, updated_mentions)
    write_jsonl_atomic(statement_path, updated_statements)
    write_csv_atomic(coverage_path, coverage_fields, coverage_new)
    print("APPLIED; recovery backups retained pending audit:")
    for backup in backups:
        print(backup.relative_to(ROOT))


parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write after all preflight checks pass")
args = parser.parse_args()
preview()
if args.apply:
    apply()
else:
    print("DRY RUN: no S2 table files written")
