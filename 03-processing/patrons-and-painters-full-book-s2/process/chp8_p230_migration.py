"""Controlled S2 migration for Chapter 8 printed page 230 and notes 1–5."""
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_ii.md"
P229 = "chp-8:08_CHP-8_sec_ii:l216-225"
P230 = "chp-8:08_CHP-8_sec_ii:l227-236"
P231 = "chp-8:08_CHP-8_sec_ii:l238-249"
NOTES = "chp-8:08_CHP-8_sec_ii:l372-461"
TARGET_IDS = {P229, P230, P231, NOTES}
BACKUP_SUFFIX = ".bak-s2-chp8-p230-20261001"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


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


segments = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {row["segment_id"]: row for row in segments}
if len(segment_by_id) != len(segments) or not TARGET_IDS <= set(segment_by_id):
    raise SystemExit("missing or duplicate target segment metadata")
for segment_id in TARGET_IDS:
    meta = segment_by_id[segment_id]
    asset = ROOT / meta["source_file"]
    if hashlib.sha256(asset.read_bytes()).hexdigest() != meta["asset_sha256"]:
        raise SystemExit(f"source asset hash changed: {meta['source_file']}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
line_offsets = {}
for segment_id in TARGET_IDS:
    meta = segment_by_id[segment_id]
    lines = source_lines[meta["line_start"] - 1:meta["line_end"]]
    if hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest() != meta["sha256"]:
        raise SystemExit(f"segment content hash changed: {segment_id}")
    offset = 0
    for line_no, line in zip(range(meta["line_start"], meta["line_end"] + 1), lines):
        line_offsets[(segment_id, line_no)] = offset
        offset += len(line) + 1

candidate_fields, candidate_rows = read_csv(TABLES / "entity-candidates.csv")
mention_fields, mention_rows = read_csv(TABLES / "mentions.csv")
statement_rows = read_jsonl(TABLES / "book-statements.jsonl")
coverage_fields, coverage_rows = read_csv(TABLES / "s2-coverage.csv")
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
if len(coverage_by_id) != len(coverage_rows):
    raise SystemExit("duplicate S2 coverage segment IDs")
expected = {
    P229: ("reviewed", "complete", "L216-225"),
    P230: ("queued", "pending", ""),
}
for segment_id, state in expected.items():
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != state:
        raise SystemExit(f"unexpected coverage for {segment_id}: {row}")
if coverage_by_id[NOTES]["source_line_ranges"] != "L373-404":
    raise SystemExit("footnote coverage changed; inspect before proceeding")
if any(row["segment_id"] == P230 for row in mention_rows + statement_rows):
    raise SystemExit("p.230 rows already exist; inspect before rerunning")

new_candidates = [
    ("cand-7838", "Pratolino", "place", 228,
     "Country residence named with Poggio a Caiano; also the location of Ferdinand's theatre. Identity and boundaries are for global S3 alignment."),
    ("cand-7839", "Theatre at Pratolino (Grand Prince Ferdinand's theatre)", "place", 229,
     "Haskell refers to Ferdinand's theatre at Pratolino and its theatrical productions; the exact building identity is not supplied."),
    ("cand-7840", "Bibbiena family", "family", 229,
     "Named collectively as a family whose members worked as stage designers for Ferdinand's theatre; no individual member is identified in this passage."),
    ("cand-7841", "Unidentified Regent in the Louis XIV comparison", "person", 231,
     "Haskell uses 'the Regent' in a hypothetical comparison with Louis XIV without naming the person; do not automatically align to an indexed Regent."),
    ("cand-7842", "Castellani (Venetian carnival faction; organizational type unresolved)", "", 234,
     "Named as one side of the fight with the Nicolotti during Venetian carnival; the passage does not define the group's organization or formal status."),
    ("cand-7843", "Nicolotti (Venetian carnival faction; organizational type unresolved)", "", 234,
     "Named as one side of the fight with the Castellani during Venetian carnival; the passage does not define the group's organization or formal status."),
    ("cand-7844", "Letters from Alessandro Scarlatti to Grand Prince Ferdinand in the Archivio Mediceo (files unspecified)", "archive", 405,
     "Footnote 1 says a remarkable series of letters is in the Archivio Mediceo; individual letters and file numbers are not supplied or independently consulted."),
    ("cand-7845", "Alessandro Scarlatti e il Principe Ferdinando de’ Medici (Mario Fabbri, Firenze 1961)", "archive", 235,
     "Identified from the book bibliography as a cited source on Ferdinand's musical activities; not independently read."),
    ("cand-7846", "Cenni storici della vita del Serenissimo Ferdinando dei Medici, Gran Principe di Toscana (L. Puliti, Firenze 1875)", "archive", 235,
     "Identified from the book bibliography as a source for Ferdinand's musical activities; not independently read."),
    ("cand-7847", "Descrizione della Regia Villa, Fontane e Fabbriche di Pratolino (Bernardo Sansone Sgrilli, Firenze 1742)", "archive", 406,
     "Bibliography identifies the work cited in p.230 note 2 about the Pratolino theatre; the cited work was not independently read."),
    ("cand-7848", "Elogio del fu Serenissimo Ferdinando de’ Medici Principe di Toscana (1714)", "archive", 407,
     "Work cited in note 3; the scan supplies the title and publication context, but no author is named here and the source was not independently read."),
    ("cand-7849", "Giornale de’ Letterati Italiani, volume XVII (1714)", "archive", 407,
     "Periodical volume cited for the 1714 Elogio; Haskell says Ferdinand had been its patron. Not independently consulted."),
    ("cand-7850", "Letter from Scipione Maffei, 1710-04-14, no.370, Archivio Mediceo Filza 5905", "archive", 407,
     "Note 3 cites this letter as a source locator; the letter and archival file were not independently consulted."),
    ("cand-7851", "Luca Ombrosi (probable author of Vita del Gran Principe Ferdinando di Toscana)", "person", 408,
     "Note 4 says the anonymous mid-eighteenth-century writer was probably the lawyer Luca Ombrosi; retain the qualification."),
    ("cand-7852", "Vita del Gran Principe Ferdinando di Toscana (attributed to Luca Ombrosi; Firenze 1887)", "archive", 408,
     "Book bibliography lists this work in Biblioteca Grassoccia; note 4 cites p.96 for the probable identification of the contemporary admirer. Not independently read."),
    ("cand-7853", "Biblioteca Grassoccia", "institution", 408,
     "Repository named in the bibliography entry for Vita del Gran Principe Ferdinando di Toscana; exact institutional identity is not further established here."),
    ("cand-7854", "Archivio Mediceo, Filza 3050D: Matteo del Teglia, Carteggio e Avvisi da Venezia (1695–1697)", "archive", 236,
     "Note 5 supplies this archival locator for the Venetian correspondence and avvisi; the file was not independently consulted."),
    ("cand-7855", "Matteo del Teglia", "person", 236,
     "Named in the title of the Archivio Mediceo correspondence and avvisi cited at p.230 note 5; no further identity is inferred."),
]
candidate_ids = {row["candidate_id"] for row in candidate_rows}
existing_keys = {(row["canonical_name"], row["suggested_type"])
                 for row in candidate_rows if not row["index_entry_id"]}
new_keys = set()
for candidate_id, name, kind, source_line, detail in new_candidates:
    if candidate_id in candidate_ids:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    if (name, kind) in existing_keys or (name, kind) in new_keys:
        raise SystemExit(f"candidate natural-key collision: {(name, kind)}")
    new_keys.add((name, kind))
    anchor_segment = NOTES if source_line >= 405 else P230
    candidate_rows.append({
        "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{anchor_segment}#L{source_line}",
    })
    candidate_ids.add(candidate_id)

new_mentions = []
existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mention_rows}


def mention(segment_id, source_line, suffix, candidate_id, surface, note, occurrence=0):
    mention_id = f"m-chp8-p230-{suffix}"
    if mention_id in existing_mention_ids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in candidate_ids:
        raise SystemExit(f"missing mention candidate: {mention_id} -> {candidate_id}")
    line = source_lines[source_line - 1]
    search_at = 0
    found_at = -1
    for _ in range(occurrence + 1):
        found_at = line.find(surface, search_at)
        if found_at < 0:
            raise SystemExit(f"surface not found at L{source_line}: {surface!r} #{occurrence}")
        search_at = found_at + 1
    start = line_offsets[(segment_id, source_line)] + found_at
    end = start + len(surface)
    span = (segment_id, str(start), str(end))
    if span in existing_spans or any((row["segment_id"], row["start_char"], row["end_char"]) == span for row in new_mentions):
        raise SystemExit(f"duplicate mention span: {span}")
    new_mentions.append({"mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
                         "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


mentions = [
    (P230,228,"ferdinand-1","cand-1609","Ferdinand","Grand Prince Ferdinand; closes p.229's heir-related continuation."),
    (P230,228,"poggio","cand-1966","Poggio a Caiano","Country residence named in the source."),
    (P230,228,"pratolino-1","cand-7838","Pratolino","Country residence named in the source."),
    (P230,229,"he-music","cand-1609","He","Coreference to Ferdinand at the start of the music paragraph."),
    (P230,229,"scarlatti-body","cand-2393","Alessandro Scarlatti","Named composer employed by Ferdinand."),
    (P230,229,"pratolino-theatre","cand-7839","theatre at Pratolino","Ferdinand's theatre and stage venue; the building identity is not established."),
    (P230,229,"italy","cand-3461","Italy","Country in which Haskell says the theatre was famous."),
    (P230,229,"bibbiena","cand-7840","Bibbiena family","Collective family reference to stage designers; individuals not enumerated."),
    (P230,229,"zeno","cand-2869","Apostolo Zeno","Writer Ferdinand supported."),
    (P230,230,"menzini","cand-1653","Benedetto Menzini","Writer named in the continuation of the p.230 sentence."),
    (P230,230,"maffei-body","cand-1487","Scipione Maffei","Writer supported by Ferdinand and author of a letter cited in n.3."),
    (P230,230,"redi","cand-2112","Francesco Redi","Poet whose editions Ferdinand financed, as reported by Haskell."),
    (P230,230,"father","cand-1607","His tyrannical old father","Coreference to Cosimo III; retain the author's characterization."),
    (P230,231,"regent","cand-7841","Regent","Unnamed person in Haskell's comparison; defer identification to S3."),
    (P230,231,"louisxiv","cand-1447","Louis XIV","French king named in the hypothetical comparison."),
    (P230,232,"florence-1","cand-3397","Florence","Place named in the contemporary admirer quotation."),
    (P230,232,"tuscany","cand-6232","Tuscany","Region named in the contemporary admirer quotation."),
    (P230,233,"ferdinand-life","cand-1609","Ferdinand’s life","Coreference to Ferdinand in the description of his two Venetian visits."),
    (P230,233,"venice-1","cand-3401","Venice","City of Ferdinand's two visits."),
    (P230,233,"city","cand-3401","The city","Coreference to Venice."),
    (P230,233,"grand-prince","cand-1609","the Grand Prince","Ferdinand, who took advantage of Venice's pleasures."),
    (P230,234,"country-coref","cand-3401","this country","Coreference to Venice in the quoted letter."),
    (P230,234,"venetian","cand-3401","Venetian","Adjectival reference to Venetian carnival entertainment."),
    (P230,234,"forze-castellani","cand-7842","the Castellani","Named carnival group; type and organizational status remain unresolved."),
    (P230,234,"nicolotti","cand-7843","the Nicolotti","Named carnival group; type and organizational status remain unresolved."),
    (P230,234,"republic","cand-6255","The Republic","Political Republic of Venice; reuse the existing candidate."),
    (P230,234,"florence-2","cand-3397","Florence","Contrast with Venice in Ferdinand's account."),
    (P230,234,"venice-2","cand-3401","Venice","Intended destination for the next carnival and remembered city."),
    (P230,234,"florentine-agents","cand-3397","Florentine","Agents whose reports recorded the pleasures; adjective references Florence."),
    (P230,235,"fabbri","cand-7845","Fabbri","Bibliography-identified publication cited for Ferdinand's music."),
    (P230,235,"puliti","cand-7846","Puliti","Bibliography-identified publication cited for Ferdinand's music."),
    (P230,236,"filza3050d","cand-7854","Archivio Mediceo, Filza 3050","Specific archival locator in note 5; page image confirms a D suffix after 3050."),
    (P230,236,"matteo-del-teglia","cand-7855","Matteo del Teglia","Name in the cited archival correspondence and avvisi title."),
    (NOTES,405,"scarlatti-letters","cand-7844","The remarkable series of letters from Alessandro Scarlattito Ferdinand are in the Archivio Mediceo","Note 1's archival source group; OCR joins `Scarlatti to`, corrected in S2."),
    (NOTES,405,"scarlatti-note","cand-2393","Alessandro Scarlatti","Person named within note 1's archival description."),
    (NOTES,405,"ferdinand-note","cand-1609","Ferdinand","Recipient named in note 1."),
    (NOTES,406,"sgrilli","cand-7847","Sgrilli","Citation for the Pratolino theatre; bibliography identifies the cited work."),
    (NOTES,407,"elogio","cand-7848","Elogio del su Serenissimo Ferdinando de' Medici Principe di Toscana","Specific title cited in note 3; scan reads `fu` where OCR has `su`."),
    (NOTES,407,"ferdinand-title","cand-1609","Ferdinando","Name in the Elogio title."),
    (NOTES,407,"giornale","cand-7849","Giornale de’ Letterati Italiani","Periodical containing the cited Elogio."),
    (NOTES,407,"maffei-note","cand-1487","Scipione Maffei","Author of the cited 1710 letter."),
    (NOTES,407,"maffei-letter","cand-7850","letter from Scipione Maffei, dated 14 April 1710, No. 370, Filza $903 of the Archivio Mediceo","Archival letter cited in note 3; scan reads Filza 5905."),
    (NOTES,408,"ombrosi","cand-7851","Luca Ombrosi","Note 4 says the lawyer identification is probable."),
    (NOTES,408,"vita","cand-7852","Vita del Cran Principe Ferdinando di Toscana","OCR title; page image reads `Gran Principe`."),
    (NOTES,408,"grassoccia","cand-7853","Biblioteca Grassoccia","Repository named in note 4 and the bibliography."),
    (NOTES,408,"firenze","cand-3397","Firenze","Italian name for Florence in the citation."),
]
for row in mentions:
    mention(*row)


def quote(segment_id: str, first: int, last: int) -> str:
    return "\n".join(source_lines[first - 1:last])


def make_statement(statement_id, segment_id, first, last, subject, obj, predicate, claim,
                   qualification, mentioned, text_layer="body", extras=None):
    meta = segment_by_id[segment_id]
    if first < meta["line_start"] or last > meta["line_end"]:
        raise SystemExit(f"statement lines outside segment: {statement_id}")
    if any(candidate_id not in candidate_ids for candidate_id in [subject, obj, *mentioned] if candidate_id):
        raise SystemExit(f"statement has missing candidate: {statement_id}")
    qualifiers = {"source_line_start": first, "source_line_end": last, "printed_page": 230,
                  "pdf_physical_page": 32, "claim": claim, "speaker": "Haskell",
                  "text_layer": text_layer, "qualification": qualification,
                  "mentioned_candidate_ids": list(dict.fromkeys(mentioned))}
    if extras:
        qualifiers.update(extras)
    return {"statement_id": statement_id, "segment_id": segment_id,
            "subject_candidate_id": subject, "object_candidate_id": obj, "predicate": predicate,
            "qualifiers": qualifiers, "original_quote": quote(segment_id, first, last),
            "origin": "book", "source_file": meta["source_file"]}


new_statements = [
    make_statement("st-chp8-p230-heir-attempts-closed", P230,228,228,"cand-1609",None,
                   "other_family_members_attempted_to_secure_heir_without_success",
                   "The p.229 sentence closes: other family members were called upon to try where Ferdinand had failed; Haskell says their efforts also came to nothing.",
                   "This closes the open continuation from p.229; the family members are unnamed and are not expanded.",
                   ["cand-1609","cand-5179"], extras={"continued_from_segment_id":P229,"continued_from_statement_id":"st-chp8-p229-family-called-to-provide-heir-open","continuation_status":"closed"}),
    make_statement("st-chp8-p230-retirement-and-houses", P230,228,228,"cand-1609",None,
                   "gave_up_heir_effort_and_retired_to_country_houses",
                   "Haskell says Ferdinand gave up the effort to secure an heir and retired to country houses, especially Poggio a Caiano and Pratolino, where he enjoyed himself and organized theatrical displays and picture collections.",
                   "The motivation is read from the immediately preceding heir discussion; do not convert it into a dated abdication or formal retirement.",
                   ["cand-1609","cand-1966","cand-7838"], extras={"speaker_judgment":True}),
    make_statement("st-chp8-p230-scarlatti-music", P230,229,229,"cand-1609","cand-2393",
                   "employed_scarlatti_for_operas_and_participated_in_composition",
                   "Ferdinand was passionately fond of music, employed Alessandro Scarlatti for many years to write operas, and played a notable part in their composition.",
                   "Haskell's account does not name the operas; no title or individual composition is added.",
                   ["cand-1609","cand-2393"], extras={"relation_candidate":True}),
    make_statement("st-chp8-p230-pratolino-theatre", P230,229,229,"cand-1609","cand-7839",
                   "theatre_at_pratolino_famous_and_used_bibbiena_stage_designers",
                   "Haskell says Ferdinand's theatre at Pratolino was famous throughout Italy and employed leading stage designers, including members of the Bibbiena family.",
                   "The theatre's exact architectural identity and the individual Bibbiena designers are not supplied.",
                   ["cand-1609","cand-7838","cand-7839","cand-3461","cand-7840"], extras={"relation_candidate":True}),
    make_statement("st-chp8-p230-discerning-patron-and-scholars", P230,229,229,"cand-1609",None,
                   "corresponded_with_artists_and_musicians_and_welcomed_scholars",
                   "Haskell says Ferdinand corresponded with artists and musicians, was a discriminating patron of painters, and welcomed foreign scholars to see his collections.",
                   "The description of Ferdinand's sensibilities and discrimination is Haskell's assessment; specific letters and visitors are not named here.",
                   ["cand-1609"], extras={"speaker_judgment":True,"scope":"generalized account"}),
    make_statement("st-chp8-p230-writers-and-redi-editions", P230,229,230,"cand-1609",None,
                   "supported_zeno_menzini_maffei_and_financed_redi_editions",
                   "Haskell says Ferdinand supported Apostolo Zeno, Benedetto Menzini and Scipione Maffei, and financed sumptuous editions of Francesco Redi and other poets.",
                   "No titles, edition details, amounts or formal commissions are supplied in these lines.",
                   ["cand-1609","cand-2869","cand-1653","cand-1487","cand-2112"], extras={"relation_candidate":True}),
    make_statement("st-chp8-p230-illness-death", P230,230,230,"cand-1609",None,
                   "ill_health_epilepsy_and_death_in_1713_at_age_50",
                   "Haskell says Ferdinand suffered ill health and epileptic fits, apparently as inevitable consequences of earlier dissipation, and died in 1713 aged 50.",
                   "The cause is explicitly qualified as apparent and attributed to Haskell; it is not asserted as a verified medical diagnosis.",
                   ["cand-1609"], extras={"date":"1713","age_at_death":"50","speaker_judgment":True}),
    make_statement("st-chp8-p230-cosimo-reign", P230,230,230,"cand-1607",None,
                   "cosimo_iii_still_ruled_after_43_years",
                   "Haskell says Ferdinand's old father remained on the throne after forty-three years.",
                   "The passage's characterization of Cosimo as tyrannical is retained as Haskell's wording.",
                   ["cand-1607","cand-1609"], extras={"duration_years":43}),
    make_statement("st-chp8-p230-regent-louis-comparison", P230,230,231,"cand-1609","cand-1447",
                   "death_compared_to_regent_preceding_louis_xiv",
                   "Haskell compares Ferdinand's death to a hypothetical death of 'the Regent' before Louis XIV.",
                   "The Regent is unnamed in this passage and remains a separate unresolved candidate; do not identify the person from the analogy alone.",
                   ["cand-1609","cand-7841","cand-1447"], extras={"speaker_judgment":True,"comparison_not_literal_event":True}),
    make_statement("st-chp8-p230-contemporary-obituary-praise", P230,231,232,None,None,
                   "anonymous_contemporary_mourning_ferdinand_as_protector_of_arts",
                   "An unnamed contemporary admirer says Ferdinand's death took joyfulness from Florence and Tuscany and removed a protector of painting, sculpture, letters and liberal arts; other princes lacked his magnanimous tastes.",
                   "Speaker remains unnamed. Note 4 only says the writer was probably the lawyer Luca Ombrosi; this does not establish authorship.",
                   ["cand-1609","cand-3397","cand-6232"], text_layer="reported contemporary quotation", extras={"reported_speaker":"anonymous contemporary admirer","speaker_attribution_status":"probable attribution only"}),
    make_statement("st-chp8-p230-two-venice-visits", P230,233,233,"cand-1609","cand-3401",
                   "two_visits_to_venice_identified_as_most_important_life_events",
                   "Haskell identifies Ferdinand's two visits to Venice as the most important events in his life and describes Venice as encouraging every pleasure except political unorthodoxy.",
                   "The ranking and moral characterization of Venice are Haskell's judgments.",
                   ["cand-1609","cand-3401"], extras={"speaker_judgment":True}),
    make_statement("st-chp8-p230-venice-1696-mask-quote", P230,233,234,"cand-1609","cand-3401",
                   "february_march_1696_visit_and_letter_praises_masked_freedom",
                   "Haskell follows Ferdinand in February and March 1696 and quotes him as delighted by the country's freedom, especially a mask that let him go anywhere without attracting attention.",
                   "The quotation is reported through Haskell and linked by footnote to archival correspondence; that correspondence was not independently checked. OCR punctuation at the end of the quote is normalized only in the S2 reading note.",
                   ["cand-1609","cand-3401","cand-7844"], extras={"date_start":"1696-02","date_end":"1696-03","reported_speaker":"Grand Prince Ferdinand","text_layer":"reported direct quotation","relation_candidate":True}),
    make_statement("st-chp8-p230-carnival-entertainment", P230,234,234,"cand-1609",None,
                   "attended_opera_ridotto_and_venetian_carnival_entertainments",
                   "Haskell says Ferdinand went nightly to opera and the ridotto and attended Venetian carnival entertainments, including forze d'Ercole contests, the Castellani-Nicolotti fight and masked balls.",
                   "The cited paintings are described as beginning to record these entertainments for tourists; no specific painting is identified here.",
                   ["cand-1609","cand-3401","cand-7842","cand-7843"], extras={"relation_candidate":True}),
    make_statement("st-chp8-p230-republic-gifts-and-return", P230,234,234,"cand-6255","cand-1609",
                   "republic_gave_ferdinand_presents_and_he_intended_to_return",
                   "Haskell says the Republic gave Ferdinand lavish presents and he reciprocated; Ferdinand announced an intention to return the next carnival but never did.",
                   "The Republic is the Venetian political entity in this context. The gifts and intention are reported by Haskell; no gifts are individually identified.",
                   ["cand-6255","cand-1609","cand-3401","cand-3397"], extras={"relation_candidate":True}),
    make_statement("st-chp8-p230-venice-memory-observation-open", P230,234,234,"cand-1609",None,
                   "venice_memory_influenced_ferdinands_later_use_of_observation",
                   "Haskell says the memory of Venice haunted Ferdinand and that he put it to good use; the sentence turns to the pleasures recorded by Florentine agents and what Ferdinand had also been studying.",
                   "The final clause continues at p.231 L239 ('the great pictures'); keep the statement open until that source page is processed.",
                   ["cand-1609","cand-3401","cand-3397"], extras={"speaker_judgment":True,"continuation_status":"open","continuation_expected_segment_id":P231,"continuation_expected_source_line":239}),
    make_statement("st-chp8-p230-note1-archival-letters", NOTES,405,405,"cand-7844",None,
                   "footnote_cites_scarlatti_ferdinand_letters_in_archivio_mediceo",
                   "Footnote 1 says that a remarkable series of letters from Alessandro Scarlatti to Ferdinand is in the Archivio Mediceo.",
                   "The files are unspecified and the letters were not independently consulted; the scan shows `Scarlatti to` where OCR fuses the words.",
                   ["cand-7844","cand-2393","cand-1609"], text_layer="footnote citation", extras={"relation_candidate":False,"linked_body_statement_ids":["st-chp8-p230-scarlatti-music"],"ocr_corrections":[{"source_line":405,"ocr":"Scarlattito","print":"Scarlatti to","basis":"CHP-8.pdf physical page 32"}]}),
    make_statement("st-chp8-p230-note1-fabbri-puliti", P230,235,235,None,None,
                   "footnote_cites_fabbri_and_puliti_for_musical_activities",
                   "Footnote 1 also cites Fabbri and Puliti, pointing particularly to Puliti for an account of Ferdinand's musical activities.",
                   "Bibliographic entries identify the cited works; neither work was independently read.",
                   ["cand-7845","cand-7846","cand-1609"], text_layer="footnote citation", extras={"relation_candidate":False,"linked_body_statement_ids":["st-chp8-p230-scarlatti-music"]}),
    make_statement("st-chp8-p230-note2-sgrilli", NOTES,406,406,"cand-7847","cand-7839",
                   "footnote_cites_sgrilli_for_pratolino_theatre",
                   "Footnote 2 cites Sgrilli, identified from the bibliography as Descrizione della Regia Villa, Fontane e Fabbriche di Pratolino.",
                   "The cited work was not independently consulted.",
                   ["cand-7847","cand-7839","cand-7838"], text_layer="footnote citation", extras={"relation_candidate":False,"linked_body_statement_ids":["st-chp8-p230-pratolino-theatre"]}),
    make_statement("st-chp8-p230-note3-elogio-journal-maffei", NOTES,407,407,"cand-7848",None,
                   "footnote_cites_1714_elogio_journal_and_maffei_letter",
                   "Footnote 3 cites the Elogio in volume XVII (1714) of Giornale de’ Letterati Italiani and a Scipione Maffei letter dated 14 April 1710, no.370, Filza 5905.",
                   "The scan corrects OCR XVH to XVII and `$903` to 5905; cited publications and archival letter were not independently consulted. The footnote also reports Ferdinand had been patron of the journal.",
                   ["cand-7848","cand-7849","cand-1487","cand-7850","cand-1609"], text_layer="footnote citation", extras={"relation_candidate":False,"linked_body_statement_ids":["st-chp8-p230-writers-and-redi-editions","st-chp8-p230-contemporary-obituary-praise"],"ocr_corrections":[{"source_line":407,"ocr":"XVH","print":"XVII","basis":"CHP-8.pdf physical page 32"},{"source_line":407,"ocr":"$903","print":"5905","basis":"CHP-8.pdf physical page 32"},{"source_line":407,"ocr":"su Serenissimo","print":"fu Serenissimo","basis":"CHP-8.pdf physical page 32"}]}),
    make_statement("st-chp8-p230-note4-ombrosi-attribution", NOTES,408,408,"cand-7851","cand-7852",
                   "footnote_probably_attributes_contemporary_admirer_to_ombrosi",
                   "Footnote 4 says the contemporary admirer was probably the lawyer Luca Ombrosi, citing Vita del Gran Principe Ferdinando di Toscana in Biblioteca Grassoccia, Firenze 1887, p.96.",
                   "The probable attribution remains tentative; note and book bibliography identify the work, but it and the cited page were not independently read. Scan corrects OCR Cran to Gran.",
                   ["cand-7851","cand-7852","cand-7853","cand-3397","cand-1609"], text_layer="footnote citation", extras={"relation_candidate":False,"linked_body_statement_ids":["st-chp8-p230-contemporary-obituary-praise"],"ocr_corrections":[{"source_line":408,"ocr":"Cran Principe","print":"Gran Principe","basis":"CHP-8.pdf physical page 32"}]}),
    make_statement("st-chp8-p230-note5-venice-avvisi", P230,236,236,"cand-7854",None,
                   "footnote_cites_matteeo_del_teglia_venice_correspondence_and_avvisi",
                   "Footnote 5 cites Archivio Mediceo, Filza 3050D, Matteo del Teglia, Carteggio e Avvisi da Venezia, 1695–1697.",
                   "This is an archival locator only; the file and records were not independently consulted. It is linked to the p.230 account of Ferdinand's Venetian visit.",
                   ["cand-7854","cand-7855","cand-1609","cand-3401"], text_layer="footnote citation", extras={"relation_candidate":False,"linked_body_statement_ids":["st-chp8-p230-venice-1696-mask-quote","st-chp8-p230-carnival-entertainment"],"ocr_corrections":[{"source_line":236,"ocr":"Filza 3050","print":"Filza 3050 D","basis":"CHP-8.pdf physical page 32"}]}),
]

statement_ids = {row["statement_id"] for row in statement_rows}
if len(statement_ids) != len(statement_rows) or any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("duplicate statement ID")
prior_id = "st-chp8-p229-family-called-to-provide-heir-open"
prior = next((row for row in statement_rows if row["statement_id"] == prior_id), None)
if not prior or prior["qualifiers"].get("continuation_status") != "open":
    raise SystemExit("expected open p.229 heir statement not found")
patched_prior = json.loads(json.dumps(prior))
patched_prior["qualifiers"].update({"continuation_status":"closed","continuation_to_segment_id":P230,
                                   "continuation_to_source_line":228,"continued_to_segment_id":P230,
                                   "continued_to_source_line":228,"continuation_closed_by_statement_id":"st-chp8-p230-heir-attempts-closed"})

for row in coverage_rows:
    if row["segment_id"] == P230:
        row.update({"disposition":"reviewed","migration_status":"partial","source_line_ranges":"L227-236",
                    "note":"p.230 body, embedded notes 1 and 5, and notes 1–4 at L405–408 reviewed against CHP-8.pdf physical page 32; final body clause continues at p.231 L239."})
    elif row["segment_id"] == NOTES:
        row.update({"disposition":"reviewed","migration_status":"partial","source_line_ranges":"L373-408",
                    "note":"p.228 n.1 L403, p.229 n.1 L404 and p.230 n.1–4 L405–408 migrated; p.230 n.5 is embedded at L236; later consolidated notes remain queued."})

preview = {"mode":"dry-run","candidate_additions":len(new_candidates),"mention_additions":len(new_mentions),
           "statement_additions":len(new_statements),"closed_continuation":{"statement_id":prior_id,"segment_id":P230,"line":228},
           "open_continuation":{"statement_id":"st-chp8-p230-venice-memory-observation-open","segment_id":P231,"line":239},
           "coverage":{P230:"partial",NOTES:"L373-408 partial"},
           "ocr_corrections":["L230 pubheation -> publication","L405 Scarlattito -> Scarlatti to","L407 XVH -> XVII and $903 -> 5905","L408 Cran -> Gran"]}

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="apply the preflighted S2 migration")
args = parser.parse_args()
if not args.apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)

for path in (TABLES / "entity-candidates.csv", TABLES / "mentions.csv", TABLES / "book-statements.jsonl", TABLES / "s2-coverage.csv"):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(path, backup)
patched_statements = [patched_prior if row["statement_id"] == prior_id else row for row in statement_rows]
patched_statements.extend(new_statements)
write_csv_atomic(TABLES / "entity-candidates.csv", candidate_fields, candidate_rows)
write_csv_atomic(TABLES / "mentions.csv", mention_fields, mention_rows + new_mentions)
write_jsonl_atomic(TABLES / "book-statements.jsonl", patched_statements)
write_csv_atomic(TABLES / "s2-coverage.csv", coverage_fields, coverage_rows)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
