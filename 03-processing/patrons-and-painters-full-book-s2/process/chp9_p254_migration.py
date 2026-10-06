"""Controlled S2 migration for printed p.254; defaults to a read-only dry run."""
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
P253 = "chp-9:09_CHP-9_intro:l124-132"
P254 = "chp-9:09_CHP-9_intro:l134-146"
P255 = "chp-9:09_CHP-9_intro:l148-155"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
EXPECTED_HASH = "eb1487c89b2d4870fe0c30240ce67972acec96ea7dbbebbccd1192a691f43382"
EXPECTED_ASSET_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
BACKUP_SUFFIX = ".bak-s2-chp9-p254-20261001"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


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
segment_by_id = {row["segment_id"]: row for row in segments}
for sid in (P253, P254, P255, NOTES):
    if sid not in segment_by_id:
        raise SystemExit(f"missing source segment: {sid}")
meta = segment_by_id[P254]
if meta["sha256"] != EXPECTED_HASH or meta["asset_sha256"] != EXPECTED_ASSET_HASH:
    raise SystemExit("p.254 source segment or source asset fingerprint changed")
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_HASH:
    raise SystemExit("source asset hash changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()


def line_offsets(segment_id):
    m = segment_by_id[segment_id]
    offsets, offset = {}, 0
    for n in range(m["line_start"], m["line_end"] + 1):
        offsets[n] = offset
        offset += len(source_lines[n - 1]) + 1
    return offsets


offsets_by_segment = {sid: line_offsets(sid) for sid in (P253, P254, NOTES)}


def quote(segment_id, first, last):
    return "\n".join(source_lines[n - 1] for n in range(first, last + 1))


candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)
coverage_by_id = {r["segment_id"]: r for r in coverage}
expected_states = {
    P253: ("reviewed", "partial", "L125-132"),
    P254: ("queued", "pending", ""),
    NOTES: ("reviewed", "partial", "L349-363"),
}
for sid, expected in expected_states.items():
    row = coverage_by_id.get(sid)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != expected:
        raise SystemExit(f"unexpected coverage state for {sid}: {row}")

candidate_ids = {r["candidate_id"] for r in candidates}
if len(candidate_ids) != len(candidates) or max(int(x.split("-")[1]) for x in candidate_ids) != 8299:
    raise SystemExit("candidate inventory changed; inspect before allocating IDs")
candidate_specs = [
    (8300, "Unidentified Venetian palace purchased by Aurelio Rezzonico from the Bon family", "place", P254, 138,
     "The passage does not give the palace's formal name; keep separate from the later Pisani country house."),
    (8301, "Bon family who sold a palace to Aurelio Rezzonico", "family", P254, 139,
     "The family is named only as the seller of the Venetian palace; individual members are not specified."),
    (8302, "Office of Procuratore di S. Marco", "institution", P254, 138,
     "Office named in the source; preserve the Italian title and do not identify it with a particular procurator."),
    (8303, "Haskell's aristocratic dream world of private deeds and family histories", "term", P254, 135,
     "Authorial metaphor for the turn from absent public exploits to celebration of private deeds and family histories."),
    (8304, "Tiepolo's eulogistic allegories recording the aristocratic calendar", "work", P254, 136,
     "Unspecified series/group of works; no individual allegory is identified by this phrase."),
    (8305, "Haskell's comparison of everyday life and artistic fantasy in eighteenth-century Venice", "term", P254, 136,
     "Authorial characterization of an unusually large and unbridgeable gap; preserve its temporal and Venetian scope."),
    (8306, "Red Indians represented in Venetian aristocratic frescoes (Haskell's wording)", "term", P254, 142,
     "Source wording for depicted figures; this is not a claim identifying a specific people or painting."),
    (8307, "Black savages represented in Venetian aristocratic frescoes (Haskell's wording)", "term", P254, 142,
     "Source wording for depicted figures; preserve the historical phrasing as quotation-level evidence."),
    (8308, "France as a political-cultural neighbour in Haskell's p.254 account", "institution", P254, 142,
     "National shorthand in a comparison of aristocratic attitudes; alignment with other France candidates is for S3."),
    (8309, "Austria as a political-cultural neighbour in Haskell's p.254 account", "institution", P254, 142,
     "National shorthand in a comparison of aristocratic attitudes; alignment with other Austria candidates is for S3."),
    (8310, "Unidentified family-apotheosis frescoes for the Grassi, Widmann, Giustiniani and Soderini", "work", P254, 142,
     "Group of works reported for four families; the body does not assign all of them to Tiepolo, and note 2 gives a separate attribution report for the Grassi fresco."),
    (8311, "Unidentified Grassi-family apotheosis fresco discussed in p.254 note 2", "work", P254, 142,
     "The note's marker follows 'The Grassi'; keep the work unnamed and distinguish the cited Fabio Canal attribution from Haskell's body wording."),
    (8312, "Living family members depicted in aristocratic apotheosis frescoes", "term", P254, 143,
     "Collective, unnamed sitters said to appear in the more excessive forms of the frescoes."),
    (8313, "Collalto family whose greatness Pietro Novelli recorded in 1794", "family", P254, 143,
     "The source names the family collectively and does not enumerate its members."),
    (8314, "Fresco Strength protecting Wisdom painted for Pietro Barbarigo in 1745", "work", P254, 144,
     "Work title as printed; preserve the reported patronage and date as Haskell's statement."),
    (8315, "Pietro Barbarigo's unnamed nephews depicted in Strength protecting Wisdom", "term", P254, 143,
     "The nephews are not named or individually identified in the passage."),
    (8316, "The Apotheosis of the Pisani at their country house in Stra", "work", P254, 145,
     "Title and location as stated on p.254; align with the index candidate and existing Pisani-family work candidate only at S3."),
    (8317, "Stra as the site of the Pisani country house named on p.254", "place", P254, 145,
     "Locality named as the setting of the Pisani work; retain as a chapter candidate for later alignment."),
    (8318, "Apollo represented in the Rezzonico marriage allegory", "person", P254, 141,
     "Mythological figure named as accompanying the bridal pair in the described scene; cross-chapter identity is for S3."),
    (8319, "Fame represented in the Rezzonico marriage allegory", "person", P254, 141,
     "Allegorical personification said to sound the event to the world; cross-chapter identity is for S3."),
    (8320, "Solar chariot drawn by four white horses in the Rezzonico marriage allegory", "term", P254, 140,
     "Group motif in the described scene; no individual horses are identified."),
    (8321, "Constancy, strength and justice represented as family virtues", "term", P254, 142,
     "Grouped virtues named by Haskell as proclaimed in family ceilings."),
    (8322, "Pagan and Christian deities in Haskell's aristocratic dream-world description", "term", P254, 135,
     "Generic group only; no additional deity is named in this passage."),
    (8323, "Extreme Catholic faction named in the Pietro Barbarigo passage", "term", P254, 143,
     "Unnamed political-religious group in which Haskell describes Barbarigo as a leading member."),
    (8324, "Livan 1935, pages 406-408, cited on p.254 note 1", "archive", NOTES, 364,
     "Citation locator only; title and cited pages were not independently consulted and should be reconciled when S2 reaches the bibliography."),
    (8325, "Unspecified Giussani reference cited on p.254 note 1", "archive", NOTES, 364,
     "The footnote gives only the surname; do not infer a title, date or identity from this locator."),
    (8326, "Molmenti 1909, pages 177-188, cited on p.254 note 2", "archive", P254, 146,
     "Citation locator for the Grassi fresco attribution report; title and cited pages were not independently consulted."),
    (8327, "Brunelli and Callegari 1931, pages 38 and 118, cited on p.254 note 3", "archive", NOTES, 365,
     "Citation locator only; title and cited pages were not independently consulted."),
    (8328, "Novelli publication, page 62, cited on p.254 note 4", "archive", NOTES, 366,
     "Citation locator only; do not assume a title from the artist reference in the body."),
    (8329, "Muraro article in Gazette des Beaux Arts, 1960, pages 19-34", "archive", NOTES, 367,
     "Citation locator for the Pietro Barbarigo affiliation note; article title and pages were not independently consulted."),
    (8330, "Tabacco publication, page 38, cited on p.254 note 5", "archive", NOTES, 367,
     "Citation locator for Pietro Barbarigo's political affiliations; the cited page was not independently consulted."),
    (8331, "Gallo 1945 reference cited on p.254 note 6", "archive", NOTES, 368,
     "Citation locator only; full title and cited page are not supplied in this note."),
    (8332, "G. A. Moschini 1806, volume II, page 105, cited on p.254 note 7", "archive", NOTES, 369,
     "Citation locator for the description of the Pisani palace; the cited page was not independently consulted."),
]
natural_keys = {(r["canonical_name"], r["suggested_type"]) for r in candidates}
for n, name, kind, source_segment, line_no, detail in candidate_specs:
    if f"cand-{n:04d}" in candidate_ids or (name, kind) in natural_keys:
        raise SystemExit(f"candidate ID or natural-key collision: {n} {name} / {kind}")
    candidates.append({
        "candidate_id": f"cand-{n:04d}", "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open", "index_source_file": "",
        "sub_entry": "", "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{source_segment}#L{line_no}",
    })
    candidate_ids.add(f"cand-{n:04d}")
    natural_keys.add((name, kind))

existing_mention_ids = {r["mention_id"] for r in mentions}
existing_spans = {(r["segment_id"], r["start_char"], r["end_char"]) for r in mentions}
new_mentions = []


def mention(segment_id, line_no, suffix, cid, surface, note="", occurrence=0):
    mid = f"m-chp9-p254-{suffix}"
    if mid in existing_mention_ids or any(r["mention_id"] == mid for r in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mid}")
    if "\n" in surface:
        line_end = segment_by_id[segment_id]["line_end"]
        search_text = quote(segment_id, line_no, line_end)
    else:
        search_text = source_lines[line_no - 1]
    start_at = 0
    pos = -1
    for _ in range(occurrence + 1):
        pos = search_text.find(surface, start_at)
        if pos < 0:
            raise SystemExit(f"surface not found at L{line_no}: {surface!r}")
        start_at = pos + len(surface)
    start = offsets_by_segment[segment_id][line_no] + pos
    end = start + len(surface)
    span = (segment_id, str(start), str(end))
    if span in existing_spans or any((r["segment_id"], r["start_char"], r["end_char"]) == span for r in new_mentions):
        raise SystemExit(f"duplicate mention span: {mid}")
    if cid not in candidate_ids:
        raise SystemExit(f"missing candidate for mention {mid}: {cid}")
    new_mentions.append({"mention_id": mid, "segment_id": segment_id, "candidate_id": cid,
                         "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


MENTION_SPECS = [
    (P254, 135, "aristocracy-private-deeds", "cand-8108", "the aristocracy", "Venetian aristocracy in the p.253–254 continuation."),
    (P254, 135, "public-exploits", "cand-8303", "great public exploits", "Haskell's contrastive description of public deeds."),
    (P254, 135, "private-deeds", "cand-8303", "private deeds", "The private achievements celebrated in Haskell's account."),
    (P254, 135, "nobles", "cand-8108", "The nobles", "Collective aristocratic group, not individually enumerated."),
    (P254, 135, "dream-world", "cand-8303", "a fabulous dream world", "Haskell's figurative characterization."),
    (P254, 135, "marriages", "cand-8303", "marriages", "Family events transformed into public allegorical subjects."),
    (P254, 135, "family-histories", "cand-8303", "family histories", "Family histories transformed into allegorical subjects."),
    (P254, 135, "pagan-christian-deities", "cand-8322", "all the deities of the pagan and even Christian religions", "Generic group as described by Haskell."),
    (P254, 136, "tiepolo-allegories-artist", "cand-2569", "Tiepolo", "Artist named as giving the allegorical world permanence."),
    (P254, 136, "aristocratic-calendar", "cand-8304", "the more notable events in the aristocratic calendar", "Events recorded through the described series of allegories."),
    (P254, 136, "eulogistic-allegories", "cand-8304", "a scries of eulogistic allegories", "S0 OCR reads 'scries'; page image reads 'series'."),
    (P254, 136, "tense-world", "cand-8305", "a tense and unrelaxed world", "Haskell's evaluative characterization."),
    (P254, 136, "everyday-life-fantasy-gap", "cand-8305", "everyday Use and artistic fantasy", "S0 OCR reads 'Use'; page image reads 'life'."),
    (P254, 136, "venice-midcentury", "cand-2719", "Venice", "The city named as the setting for Haskell's comparison."),
    (P254, 137, "faustina", "cand-2378", "Faustina Savorgnan", "Index candidate for the named bride."),
    (P254, 137, "select-nobility", "cand-8108", "the most select nobility", "Social setting as described by Haskell."),
    (P254, 137, "lodovico-bridegroom", "cand-2138", "Lodovico Rezzonico", "Index candidate for the named bridegroom."),
    (P254, 137, "rezzonico-family-rise", "cand-3615", "a family whose rise had been as spectacular as it was recent", "The family referent is Rezzonico from the immediately preceding name and the Plate 43 caption candidate."),
    (P254, 137, "genoese-origin", "cand-1131", "Of Genoese origin", "Genoa named as the family origin."),
    (P254, 137, "ennobled-family", "cand-3615", "ennobled only in 1687", "Date and status reported for the Rezzonico family."),
    (P254, 137, "rezzonico-wealth", "cand-3615", "their great wealth", "The pronoun refers to the Rezzonico family."),
    (P254, 137, "state-positions", "cand-8105", "the leading positions in the State", "Venetian government/State; distinct from Venice as a city."),
    (P254, 137, "aurelio-name", "cand-2136", "Aurelio", "Rezzonico, as listed in the index."),
    (P254, 137, "lodovico-father", "cand-2136", "Lodovico’s father", "Coreference to Aurelio Rezzonico."),
    (P254, 137, "lodovico-family-reference", "cand-2138", "Lodovico", "Nested in the explicit 'Lodovico’s father' relation."),
    (P254, 138, "procuratore-office", "cand-8302", "Procuratore di S. Marco", "Office title is preserved in the Italian form."),
    (P254, 138, "venetian-palace-purchase", "cand-8300", "one of the grandest palaces", "The palace is unnamed; do not identify it with the Pisani palace mentioned later."),
    (P254, 139, "venice-palace-location", "cand-2719", "Venice", "City where Aurelio bought the palace."),
    (P254, 139, "bon-family-seller", "cand-8301", "the Bon family", "Family named as the seller."),
    (P254, 139, "aurelio-brother-carlo", "cand-2137", "his brother Carlo", "The possessive refers to Aurelio, Lodovico's father."),
    (P254, 140, "clement-election", "cand-2137", "Clement XIII", "Carlo is explicitly said to have been elected Pope as Clement XIII; retain the indexed identity candidate."),
    (P254, 140, "tiepolo-marriage-artist", "cand-2569", "Tiepolo", "Artist named in the body; cross-reference the existing Plate 43 caption candidate."),
    (P254, 140, "pope-nephew", "cand-2138", "the Pope’s nephew", "Contextually refers to Lodovico, introduced as the bridegroom; retain the contextual basis."),
    (P254, 140, "rezzonico-marriage-fresco", "cand-4105", "his marriage fresco", "Existing Plate 43 caption candidate; body and caption are cross-referenced without adding a new title."),
    (P254, 140, "solar-chariot", "cand-8320", "the chariot of the sun", "Motif described in the Rezzonico marriage allegory."),
    (P254, 140, "white-horses", "cand-8320", "four hurtling white horses", "Four horses drawing the solar chariot; no individual horses identified."),
    (P254, 141, "apollo", "cand-8318", "Apollo", "Mythological figure named in the scene; local candidate for later S3 alignment."),
    (P254, 141, "fame", "cand-8319", "Fame", "Allegorical personification named in the scene; local candidate for later S3 alignment."),
    (P254, 142, "aristocracy-declining-importance", "cand-8108", "the aristocracy", "Second p.254 occurrence; group said to decline in international importance."),
    (P254, 142, "tiepolo-glorification", "cand-2569", "Tiepolo’s hands", "The phrase describes Haskell's account of the artist's glorification of the aristocracy."),
    (P254, 142, "family-virtues", "cand-8321", "their virtues of constancy, strength and justice", "Grouped values presented on state-room ceilings."),
    (P254, 142, "red-indians", "cand-8306", "Red Indians", "Historical source wording for depicted figures; no specific work or people identified."),
    (P254, 142, "black-savages", "cand-8307", "black savages", "Historical source wording for depicted figures; no specific work or people identified."),
    (P254, 142, "france-neighbour", "cand-8308", "France", "National shorthand in Haskell's cultural-political comparison."),
    (P254, 142, "austria-neighbour", "cand-8309", "Austria", "National shorthand in Haskell's cultural-political comparison."),
    (P254, 142, "grassi-family", "cand-1228", "The Grassi", "Index family candidate; footnote 2 supplies a separate attribution report for its fresco."),
    (P254, 142, "widmann-family", "cand-2812", "the Widmann", "Index family candidate."),
    (P254, 142, "giustiniani-family", "cand-1197", "the Giustiniani", "Index family candidate."),
    (P254, 142, "soderini-family", "cand-2478", "the Soderini", "Index family candidate."),
    (P254, 142, "family-apotheoses", "cand-8310", "apotheoses of their families", "Group-level work reference; do not attribute every fresco to Tiepolo."),
    (P254, 142, "pietro-novelli", "cand-1758", "Pietro Novelli", "The index locates Novelli, Pietro Antonio on p.254; preserve source form and leave candidate alignment to S3."),
    (P254, 143, "collalto-family", "cand-8313", "Collalto", "Family named collectively; the preceding article falls at the end of the prior line, while the family name itself is anchored here."),
    (P254, 143, "family-frescoes-reprise", "cand-8310", "these frescoes", "Anaphoric reference to the previously described family apotheoses."),
    (P254, 143, "portraits-living-members", "cand-8312", "actual portraits of living members of the family", "The source does not name the represented family members."),
    (P254, 143, "pietro-barbarigo", "cand-0183", "Pietro Barbarigo", "Index candidate for the patron named on p.254."),
    (P254, 143, "catholic-faction", "cand-8314", "the extreme Catholic faction", "Unnamed faction in Haskell's characterization."),
    (P254, 143, "leading-member-barbarigo", "cand-0183", "the leading member of the extreme Catholic faction", "Descriptive role assigned by Haskell."),
    (P254, 143, "barbarigo-nephews", "cand-8315", "his nephews", "Unnamed nephews of Pietro Barbarigo, said to be included in the fresco."),
    (P254, 144, "strength-protecting-wisdom", "cand-8314", "Strength protecting Wisdom", "Printed fresco title; keep distinct from the Tiepolo index subentry pending S3."),
    (P254, 144, "tiepolo-strength-fresco", "cand-2569", "Tiepolo", "Artist named as the fresco's painter."),
    (P254, 145, "venice-departure", "cand-2719", "Venice", "City Tiepolo is said to leave for ever."),
    (P254, 145, "apotheosis-pisani-title", "cand-8316", "the Apotheosis of the Pisani", "Printed work title; compare the Tiepolo index subentry and accepted KU only at S3."),
    (P254, 144, "tiepolo-pisani-work", "cand-2569", "Tiepolo", "Artist identified as painter of the last great work.", 1),
    (P254, 145, "pisani-family", "cand-3614", "the Pisani", "Existing family candidate; the title names the family as the work's subject."),
    (P254, 145, "stra-country-house", "cand-1946", "their country house at Stra", "Uses the p.254 Pisani-palace index candidate; exact alignment with the accepted Villa Pisani place remains for S3."),
    (P254, 145, "stra-locality", "cand-8317", "Stra", "Locality named as the country-house site; separate chapter candidate for S3."),
    (P254, 145, "pisani-palace", "cand-1946", "The palace", "Anaphoric reference to the Pisani country house at Stra."),
    (P254, 145, "venice-near-palace", "cand-2719", "Venice", "Geographic reference in the palace comparison.", 1),
    (P254, 146, "molmenti-reference", "cand-8326", "Mohnenti, 1909, pp. 177-88", "OCR surface; page image reads Molmenti, 1909, pp. 177-88."),
    (P254, 146, "grassi-attribution-fresco", "cand-8311", "the fresco", "Footnote marker 2 follows 'The Grassi' in L142; this identifies the note's Grassi-fresco referent."),
    (P254, 146, "fabio-canal-attribution", "cand-0495", "Fabio Canal", "Index candidate cited for the attribution reported by Haskell's note."),
    (NOTES, 364, "livan-1935-reference", "cand-8324", "Livan, 1935, pp. 406-8", "Footnote citation only; no independent consultation."),
    (NOTES, 364, "giussani-reference", "cand-8325", "Giussani", "Surname-only reference; full identity and publication are not specified here."),
    (NOTES, 365, "brunelli-callegari-reference", "cand-8327", "Brunelli e Callegari, 1931, pp. 38 and 118", "Footnote citation only; OCR note marker 8 is corrected to 3 against the page image."),
    (NOTES, 366, "novelli-source-reference", "cand-8328", "Novelli, p. 62", "Footnote citation only; the cited page was not independently consulted."),
    (NOTES, 366, "novelli-source-author", "cand-1758", "Novelli", "Index locates Novelli, Pietro Antonio on p.254; this mention is a citation name, not independent author verification."),
    (NOTES, 367, "muraro-reference", "cand-8329", "Muraro, in Gazette des Beaux Arts, i960, pp. 19-34", "OCR year i960 is corrected to 1960 against the page image; citation not independently consulted."),
    (NOTES, 367, "tabacco-reference", "cand-8330", "Tabacco, p. 38", "Footnote citation only; the cited page was not independently consulted."),
    (NOTES, 367, "barbarigo-note-reference", "cand-0183", "Pietro Barbarigo’s political affiliations", "The note points to a source for the body characterization; it is not independent confirmation."),
    (NOTES, 368, "gallo-reference", "cand-8331", "Gallo, 1945", "Footnote citation only; full title and cited page are not supplied here."),
    (NOTES, 369, "moschini-reference", "cand-8332", "G. A. Moschini, 1806, II, p. 105", "Footnote citation only; the cited page was not independently consulted."),
    (NOTES, 369, "moschini-author", "cand-1709", "G. A. Moschini", "Index author candidate; bibliographic identity remains subject to later alignment."),
]
for spec in MENTION_SPECS:
    mention(*spec)

new_statements = []
existing_statement_ids = {r["statement_id"] for r in statements}


def statement(suffix, segment_id, first, last, subject, obj, predicate, claim, qualification,
              mentioned, marker=None, speaker="Haskell", text_layer="body", extras=None):
    sid = f"st-chp9-p254-{suffix}"
    if sid in existing_statement_ids or any(r["statement_id"] == sid for r in new_statements):
        raise SystemExit(f"duplicate statement ID: {sid}")
    m = segment_by_id[segment_id]
    if first < m["line_start"] or last > m["line_end"]:
        raise SystemExit(f"statement lines outside segment {segment_id}: {sid}")
    if any(cid and cid not in candidate_ids for cid in [subject, obj, *mentioned]):
        raise SystemExit(f"missing candidate in statement: {sid}")
    q = {"source_line_start": first, "source_line_end": last, "printed_page": 254,
         "pdf_physical_page": 16, "claim": claim, "speaker": speaker, "text_layer": text_layer,
         "qualification": qualification,
         "mentioned_candidate_ids": list(dict.fromkeys(x for x in mentioned if x))}
    if marker is not None:
        q["footnote_marker"] = marker
    if extras:
        q.update(extras)
    new_statements.append({"statement_id": sid, "segment_id": segment_id,
                           "subject_candidate_id": subject, "object_candidate_id": obj,
                           "predicate": predicate, "qualifiers": q,
                           "original_quote": quote(segment_id, first, last), "origin": "book",
                           "source_file": segment_by_id[segment_id]["source_file"]})


statement("private-deeds-and-dream-world", P254, 135, 135, "cand-8108", "cand-8303",
          "absence_of_public_exploits_and_turn_to_private_deeds",
          "Haskell contrasts a generation earlier, when the aristocracy lacked great public exploits and turned to celebrating private deeds; he describes nobles' marriage and family histories as entering a fabulous allegorical dream world.",
          "This completes p.253 L132's contrast. The dream-world language is Haskell's metaphor, not a literal social institution.",
          ["cand-8108", "cand-8303", "cand-8322"],
          extras={"cross_reference_segments": [{"segment_id": P253, "source_line_start": 132, "source_line_end": 132}]})
statement("tiepolo-allegorical-calendar", P254, 135, 136, "cand-2569", "cand-8304",
          "gave_permanence_to_allegories_recording_aristocratic_calendar",
          "Haskell says Tiepolo gave the aristocratic dream world imperishable existence by recording notable events in an eulogistic series of allegories.",
          "The series is not enumerated; the claim is Haskell's characterization and does not attribute every family apotheosis on this page to Tiepolo.",
          ["cand-2569", "cand-8303", "cand-8304"])
statement("tense-world-and-life-fantasy-gap", P254, 136, 136, "cand-8305", "cand-2719",
          "unbridgeable_gap_between_everyday_life_and_artistic_fantasy",
          "Haskell characterizes the allegorical world as tense, continuously on display and hard in expression, and says the gap between everyday life and artistic fantasy was exceptionally wide and unbridgeable in mid-eighteenth-century Venice.",
          "Authorial interpretation; OCR 'everyday Use' is read as 'everyday life' from the page image. The source OCR is unchanged.",
          ["cand-8305", "cand-2719"], extras={"ocr_corrections": [
              {"line": 136, "ocr": "a scries", "reading": "a series", "basis": "CHP-9.pdf physical p.16"},
              {"line": 136, "ocr": "everyday Use", "reading": "everyday life", "basis": "CHP-9.pdf physical p.16"}]})
statement("faustina-lodovico-marriage", P254, 137, 137, "cand-2378", "cand-2138",
          "married_in_1758",
          "Haskell says Faustina Savorgnan married Lodovico Rezzonico in 1758.",
          "The statement is from Haskell's narrative; note 1 cites Livan and Giussani but neither is independently consulted here.",
          ["cand-2378", "cand-2138", "cand-3615"], marker=1,
          extras={"relation_candidate": True,
                  "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 364, "source_line_end": 364}]})
statement("rezzonico-origin-and-ennoblement", P254, 137, 137, "cand-3615", "cand-1131",
          "family_origin_in_genoa_and_ennobled_in_1687",
          "Haskell describes the Rezzonico family as Genoese in origin and ennobled only in 1687.",
          "The family-level origin and status are source claims; note 1 is a citation locator only.",
          ["cand-3615", "cand-1131"], marker=1, extras={"relation_candidate": True,
          "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 364, "source_line_end": 364}]})
statement("rezzonico-wealth-and-state-positions", P254, 137, 138, "cand-3615", "cand-8105",
          "wealth_secured_leading_positions_in_the_venetian_state",
          "Haskell says the Rezzonico family's great wealth secured its leading positions in the State.",
          "The State is the Venetian governing entity in this context, distinct from Venice as a place; the causal account is Haskell's.",
          ["cand-3615", "cand-8105"], marker=1, extras={"relation_candidate": True,
          "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 364, "source_line_end": 364}]})
statement("aurelio-father-of-lodovico", P254, 137, 137, "cand-2136", "cand-2138",
          "father_of_lodovico_rezzonico",
          "Haskell identifies Aurelio Rezzonico as Lodovico's father.",
          "Direct kinship statement in the source. OCR '��' in the possessive is read as an apostrophe from the page image.",
          ["cand-2136", "cand-2138"], extras={"relation_candidate": True, "ocr_corrections": [
              {"line": 137, "ocr": "Lodovico��s", "reading": "Lodovico's", "basis": "CHP-9.pdf physical p.16"}]})
statement("aurelio-appointed-procuratore", P254, 138, 138, "cand-2136", "cand-8302",
          "made_procuratore_di_s_marco_in_1751",
          "Haskell says Aurelio was made Procuratore di S. Marco in 1751.",
          "The Italian office title is retained; the statement records appointment, not a broader claim about his powers.",
          ["cand-2136", "cand-8302"], extras={"relation_candidate": True})
statement("aurelio-bought-bon-palace", P254, 138, 139, "cand-2136", "cand-8300",
          "bought_grand_palace_from_bon_family_in_venice_in_1751",
          "Haskell says Aurelio bought one of the grandest palaces in Venice from the Bon family in 1751.",
          "The palace is unnamed and is not identified with the later Pisani country house.",
          ["cand-2136", "cand-8300", "cand-8301", "cand-2719"], extras={"relation_candidate": True})
statement("carlo-rezzonico-elected-pope", P254, 139, 140, "cand-2136", "cand-2137",
          "brother_carlo_elected_pope_as_clement_xiii_seven_years_later",
          "Haskell says Aurelio's brother Carlo was elected Pope as Clement XIII seven years after Aurelio bought the palace in 1751.",
          "The source itself identifies Carlo with Clement XIII; the separate index redirect candidate is not treated as another person.",
          ["cand-2136", "cand-2137"], extras={"relation_candidate": True})
statement("tiepolo-rezzonico-marriage-fresco", P254, 140, 140, "cand-2569", "cand-4105",
          "envisaged_marriage_fresco_for_the_popes_nephew",
           "After recounting Faustina Savorgnan and Lodovico Rezzonico's marriage, Haskell describes Tiepolo's marriage fresco for the Pope's nephew; the Plate 43 caption names the work as the Marriage Allegory of the Rezzonico family.",
           "The page sequence contextually identifies the nephew with Lodovico, while the caption names the Rezzonico family as subject and does not name both partners. Cross-reference the existing caption rather than creating a duplicate work.",
           ["cand-2569", "cand-4105", "cand-3615", "cand-2138", "cand-2378"],
           extras={"relation_candidate": True,
                   "ocr_corrections": [{"line": 140, "ocr": "Pope��s", "reading": "Pope's", "basis": "CHP-9.pdf physical p.16"}],
                   "cross_reference_segments": [{"segment_id": "chp-9:09_CHP-9_intro_plates_visual-transcription:l4-4", "source_line_start": 4, "source_line_end": 4}]})
statement("solar-chariot-scene", P254, 140, 141, "cand-4105", "cand-3615",
          "bridal_pair_carried_in_solar_chariot_with_apollo_and_fame",
          "Haskell describes the bridal pair as carried by a solar chariot drawn by four white horses, accompanied by Apollo, while Fame sounds the event to the world.",
          "This is the scene as described in Haskell's text; the named figures and the family caption are not an independent iconographic attribution.",
          ["cand-4105", "cand-3615", "cand-2378", "cand-2138", "cand-8320", "cand-8318", "cand-8319"])
statement("tiepolo-glorification-of-aristocracy", P254, 142, 142, "cand-2569", "cand-8108",
          "glorification_of_aristocracy_reached_new_peaks_as_international_importance_declined",
          "Haskell says that as the aristocracy declined in international importance, its glorification at Tiepolo's hands reached new peaks.",
          "Authorial interpretation; the passage does not assert that Tiepolo painted every family apotheosis named next.",
          ["cand-2569", "cand-8108"], extras={"relation_candidate": True, "ocr_corrections": [
              {"line": 142, "ocr": "Tiepolo��s", "reading": "Tiepolo's", "basis": "CHP-9.pdf physical p.16"}]})
statement("family-virtues-and-pictorial-neighbours", P254, 142, 142, "cand-8108", "cand-8321",
          "family_virtues_proclaimed_on_state_room_ceilings",
          "Haskell says families could see constancy, strength and justice proclaimed on state-room ceilings; depictions of Red Indians or black savages might compensate for coldness and scorn from neighbours such as France or Austria.",
          "The modal 'might' is retained. 'Red Indians' and 'black savages' are source terms for depicted figures, not modern identifications of a particular people or fresco.",
          ["cand-8108", "cand-8321", "cand-8306", "cand-8307", "cand-8308", "cand-8309"])
statement("four-family-apotheosis-report", P254, 142, 142, None, "cand-8310",
          "four_families_had_apotheoses_painted_in_their_residences",
          "Haskell reports that the Grassi, Widmann, Giustiniani and Soderini had family apotheoses painted in their palaces or country houses.",
          "The body does not assign all four works to Tiepolo or name their locations. Note 2, attached to the Grassi, reports a separate Fabio Canal attribution; preserve both source layers.",
          ["cand-1228", "cand-2812", "cand-1197", "cand-2478", "cand-8310", "cand-8311"],
          extras={"relation_candidate": True,
                  "cross_reference_segments": [{"segment_id": P254, "source_line_start": 146, "source_line_end": 146}]})
statement("novelli-records-collalto", P254, 142, 143, "cand-1758", "cand-8313",
          "pietro_novelli_recorded_collalto_greatness_in_1794",
          "Haskell says that as late as 1794 the artist Pietro Novelli recorded the greatness of the Collalto.",
          "The index locates Novelli, Pietro Antonio on p.254; this is a candidate link only, with cross-candidate alignment for S3.",
          ["cand-1758", "cand-8313"], extras={"relation_candidate": True,
          "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 366, "source_line_end": 366}]})
statement("living-family-portraits-in-frescoes", P254, 143, 143, "cand-8310", "cand-8312",
          "more_excessive_frescoes_showed_portraits_of_living_family_members",
          "Haskell says that in their more excessive forms the frescoes showed actual portraits of living family members sharing in the general exaltation.",
          "The families and individuals represented in each fresco are not assigned beyond the passage.",
          ["cand-8310", "cand-8312"])
statement("barbarigo-nephews-in-strength-fresco", P254, 143, 144, "cand-0183", "cand-8314",
          "pietro_barbarigo_had_nephews_included_in_tiepolo_fresco_in_1745",
          "Haskell identifies Pietro Barbarigo as a leading member of the extreme Catholic faction and says his nephews were included in Strength protecting Wisdom, painted by Tiepolo for him in 1745.",
          "The nephews are unnamed; the printed footnote marker is 5, although the OCR gives 8. Note 5 cites Muraro and Tabacco but neither is independently consulted.",
          ["cand-0183", "cand-8314", "cand-8315", "cand-2569", "cand-8323"], marker=5,
          extras={"relation_candidate": True, "ocr_corrections": [
              {"line": 144, "ocr": "1745.8", "reading": "1745.5", "basis": "CHP-9.pdf physical p.16"}],
              "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 367, "source_line_end": 367}]})
statement("apotheosis-of-pisani-last-great-work", P254, 144, 145, "cand-2569", "cand-8316",
          "painted_apotheosis_of_pisani_before_leaving_venice_for_ever",
          "Haskell describes the Apotheosis of the Pisani at their country house in Stra as Tiepolo's last great work before he left Venice for ever.",
          "Printed title and place are preserved as a new page-level candidate; align with the index subentry and existing accepted Pisani work/place candidates only at S3. The sentence continues on p.255 L149.",
          ["cand-2569", "cand-8316", "cand-3614", "cand-1946", "cand-8317"], marker=6,
          extras={"relation_candidate": True, "ocr_corrections": [
                      {"line": 145, "ocr": "for ever��the Apotheosis", "reading": "for ever—the Apotheosis", "basis": "CHP-9.pdf physical p.16"}],
                  "continuation_segment": P255,
                  "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 368, "source_line_end": 368},
                                                {"segment_id": P255, "source_line_start": 149, "source_line_end": 149}]})
statement("pisani-palace-comparison", P254, 145, 145, "cand-1946", "cand-2719",
          "pisani_palace_acknowledged_as_grandest_near_venice_in_eighteenth_century",
          "Haskell says the palace at Stra was acknowledged as the grandest built near Venice in the eighteenth century.",
          "The antecedent is the Pisani country house in the same sentence. Note 7 cites Moschini, 1806, volume II, page 105; the cited page was not independently consulted. The sentence continues on p.255 L149.",
          ["cand-1946", "cand-2719", "cand-8317", "cand-8332"], marker=7,
          extras={"continuation_segment": P255,
                  "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 369, "source_line_end": 369},
                                                {"segment_id": P255, "source_line_start": 149, "source_line_end": 149}]})

statement("note1-livan-reference", NOTES, 364, 364, None, "cand-8324",
          "citation_locator_livan_1935_pages_406_408",
          "Haskell's note 1 cites Livan, 1935, pages 406-408, for the preceding Rezzonico account.",
          "Citation locator only; no independent consultation is claimed.", ["cand-8324", "cand-3615", "cand-2378", "cand-2138"],
          marker=1, speaker="Haskell's footnote", text_layer="footnote")
statement("note1-giussani-reference", NOTES, 364, 364, None, "cand-8325",
          "citation_locator_giussani",
          "Haskell's note 1 also cites Giussani without supplying fuller bibliographic details in this note.",
          "The surname-only reference is retained without inferring a title or full identity.", ["cand-8325"],
          marker=1, speaker="Haskell's footnote", text_layer="footnote")
statement("note2-molmenti-fabio-canal-attribution", P254, 146, 146, "cand-8311", "cand-0495",
          "molmenti_1909_attributes_grassi_fresco_to_fabio_canal",
          "Haskell's note 2 says Molmenti attributes the Grassi fresco to Fabio Canal and discusses its iconography.",
          "This is a report within Haskell's footnote, not a claim that the cited page or attribution was independently verified or accepted by Haskell. OCR 'Mohnenti' is read as 'Molmenti' from the page image.",
          ["cand-8311", "cand-0495", "cand-8326", "cand-1228"], marker=2,
          speaker="Haskell's footnote", text_layer="footnote", extras={"relation_candidate": True,
          "ocr_corrections": [{"line": 146, "ocr": "Mohnenti", "reading": "Molmenti", "basis": "CHP-9.pdf physical p.16"}],
          "cross_reference_segments": [{"segment_id": P254, "source_line_start": 142, "source_line_end": 142}]})
statement("note3-brunelli-callegari-reference", NOTES, 365, 365, None, "cand-8327",
          "citation_locator_brunelli_callegari_1931",
          "Haskell's note 3 cites Brunelli and Callegari, 1931, pages 38 and 118, following the Giustiniani reference.",
          "Citation locator only; the cited pages were not independently consulted. OCR note number 8 is corrected to printed note 3.",
          ["cand-8327", "cand-1197"], marker=3, speaker="Haskell's footnote", text_layer="footnote",
          extras={"ocr_corrections": [{"line": 365, "ocr": "8 Brunelli", "reading": "3 Brunelli", "basis": "CHP-9.pdf physical p.16"}]})
statement("note4-novelli-reference", NOTES, 366, 366, None, "cand-8328",
          "citation_locator_novelli_page_62",
          "Haskell's note 4 cites Novelli, page 62, after the Collalto passage.",
          "Citation locator only; the cited page was not independently consulted.", ["cand-8328", "cand-1758", "cand-8313"],
          marker=4, speaker="Haskell's footnote", text_layer="footnote")
statement("note5-muraro-reference", NOTES, 367, 367, None, "cand-8329",
          "citation_locator_muraro_gazette_des_beaux_arts_1960",
          "Haskell's note 5 cites Muraro in Gazette des Beaux Arts, 1960, pages 19-34, concerning Pietro Barbarigo's political affiliations.",
          "Citation locator only; the article was not independently consulted. OCR 'i960' and note number 8 are corrected against the page image.",
          ["cand-8329", "cand-0183"], marker=5, speaker="Haskell's footnote", text_layer="footnote",
          extras={"ocr_corrections": [{"line": 367, "ocr": "8 Muraro ... i960", "reading": "5 Muraro ... 1960", "basis": "CHP-9.pdf physical p.16"}]})
statement("note5-tabacco-reference", NOTES, 367, 367, None, "cand-8330",
          "citation_locator_tabacco_page_38",
          "Haskell's note 5 also cites Tabacco, page 38, for Pietro Barbarigo's political affiliations.",
          "Citation locator only; the cited page was not independently consulted.", ["cand-8330", "cand-0183"],
          marker=5, speaker="Haskell's footnote", text_layer="footnote")
statement("note6-gallo-reference", NOTES, 368, 368, None, "cand-8331",
          "citation_locator_gallo_1945",
          "Haskell's note 6 cites Gallo, 1945, after the Pisani work reference.",
           "Citation locator only; no title or cited page is supplied in this note, and no independent consultation is claimed.",
           ["cand-8331", "cand-8316"], marker=6, speaker="Haskell's footnote", text_layer="footnote")
statement("note7-moschini-reference", NOTES, 369, 369, None, "cand-8332",
          "citation_locator_moschini_1806_volume_ii_page_105",
          "Haskell's note 7 cites G. A. Moschini, 1806, volume II, page 105, after the palace comparison.",
          "Citation locator only; the cited page was not independently consulted.", ["cand-8332", "cand-1946"],
          marker=7, speaker="Haskell's footnote", text_layer="footnote")

prior_id = "st-chp9-p253-candidate-absence-becoming-commonplace"
prior = [r for r in statements if r.get("statement_id") == prior_id]
if len(prior) != 1:
    raise SystemExit(f"expected one p.253 continuation statement, found {len(prior)}")
pq = prior[0]["qualifiers"]
if not any(x.get("segment_id") == P254 and x.get("source_line_start") == 135 for x in pq.get("cross_reference_segments", [])):
    raise SystemExit("unexpected p.253 -> p.254 continuation pointer")
pq["qualification"] = "P.254 L135 completes the sentence and turns to a contrast: the earlier aristocracy lacked public exploits and celebrated private deeds. This does not restate the absence of a successor to Zen."

if len({r["mention_id"] for r in mentions + new_mentions}) != len(mentions) + len(new_mentions):
    raise SystemExit("mention IDs are not unique")
if len({r["statement_id"] for r in statements + new_statements}) != len(statements) + len(new_statements):
    raise SystemExit("statement IDs are not unique")

coverage_by_id[P253].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L125-132",
    "note": "P.253 L132 continues at p.254 L135 and is now closed. The continuation begins a contrast about an earlier aristocracy's private deeds; the statement is updated to preserve that distinction.",
})
coverage_by_id[P254].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L135-146",
    "note": "Printed p.254 (CHP-9.pdf physical p.16) reviewed against the page image. Body L135 closes p.253 L132; L145 ends with 'and' and continues at p.255 L149. Footnote 2 is embedded in this segment at L146; notes 1 and 3-7 are in the consolidated note segment L364-369. The Grassi fresco attribution in note 2 is preserved as a cited report, not a general attribution of the four-family group to Tiepolo.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L349-369",
    "note": "Consolidated notes through p.254 note 7 are processed in source order at L349-369. P.254 note 2 appears separately in body OCR segment L146. Later notes remain unprocessed; citation locators are not independent verification.",
})

summary = {"segments": {sid: [coverage_by_id[sid]["disposition"], coverage_by_id[sid]["migration_status"],
                               coverage_by_id[sid]["source_line_ranges"]] for sid in (P253, P254, NOTES)},
           "new_candidates": len(candidate_specs), "new_mentions": len(new_mentions),
           "new_statements": len(new_statements), "source_hash": meta["sha256"],
           "next_body_segment": f"{P255}#L149 closes p.254 L145"}
print(json.dumps(summary, ensure_ascii=False, indent=2))

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the preflighted migration")
args = parser.parse_args()
if args.apply:
    paths = [candidate_path, mention_path, statement_path, coverage_path]
    backups = []
    for path in paths:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists: {backup}")
        shutil.copy2(path, backup)
        backups.append(backup)
    try:
        write_csv(candidate_path, candidate_fields, candidates)
        write_csv(mention_path, mention_fields, mentions + new_mentions)
        write_jsonl(statement_path, statements + new_statements)
        write_csv(coverage_path, coverage_fields, list(coverage_by_id.values()))
    except Exception:
        for path, backup in zip(paths, backups):
            shutil.copy2(backup, path)
        raise
    print("applied; backups: " + ", ".join(str(x.relative_to(ROOT)) for x in backups))
else:
    print("dry-run only; no files written")
