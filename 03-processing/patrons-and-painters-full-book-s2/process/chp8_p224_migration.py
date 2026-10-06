"""Controlled S2 migration for Chapter 8 printed page 224 and notes 1-4."""
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
P223 = "chp-8:08_CHP-8_sec_ii:l140-150"
P224 = "chp-8:08_CHP-8_sec_ii:l152-161"
P225 = "chp-8:08_CHP-8_sec_ii:l163-177"
NOTES = "chp-8:08_CHP-8_sec_ii:l372-461"
TARGET_IDS = {P223, P224, P225, NOTES}
BACKUP_SUFFIX = ".bak-s2-chp8-p224-20261001"


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
segment_texts = {}
line_offsets = {}
for segment_id in TARGET_IDS:
    meta = segment_by_id[segment_id]
    lines = source_lines[meta["line_start"] - 1:meta["line_end"]]
    text = "\n".join(lines)
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != meta["sha256"]:
        raise SystemExit(f"segment content hash changed: {segment_id}")
    segment_texts[segment_id] = text
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
    raise SystemExit("s2-coverage.csv contains duplicate segment IDs")

expected = {
    P223: ("reviewed", "partial", "L140-150"),
    P224: ("queued", "pending", ""),
}
for segment_id, state in expected.items():
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != state:
        raise SystemExit(f"unexpected coverage state for {segment_id}: {row}")
if coverage_by_id[NOTES]["source_line_ranges"] != "L373-388":
    raise SystemExit("footnote coverage changed; inspect before proceeding")
if any(row["segment_id"] == P224 for row in mention_rows + statement_rows):
    raise SystemExit("p.224 rows already exist; inspect before rerunning")

new_candidates = [
    ("cand-7747", "Earlier palace on the site of Raimondo Buonaccorsi's palace (unidentified)", "place", 153,
     "Unnamed predecessor building; the source reports that it had been acquired in 1701 by Raimondo's father."),
    ("cand-7748", "Raimondo Buonaccorsi's unnamed father", "person", 153,
     "The source identifies this person only as Raimondo's father and reports an acquisition in 1701."),
    ("cand-7749", "Long gallery in Raimondo Buonaccorsi's palace at Macerata", "place", 154,
     "Interior space in the palace; distinguish it from the palace building and from the frescoes displayed there."),
    ("cand-7750", "Apotheosis of Aeneas fresco in Raimondo Buonaccorsi's gallery (1707)", "work", 157,
     "The source says Carlo Antonio Rambaldi and Antonio Dardani were summoned in 1707 to paint the vault fresco."),
    ("cand-7751", "Venus in the Forge of Vulcan (Buonaccorsi gallery painting)", "work", 157,
     "The sole Roman painting selected for the gallery in Haskell's account; attribution to Luigi Garzi is qualified as apparent."),
    ("cand-7752", "Vulcan (mythological figure named in the painting subject)", "person", 157,
     "Named only through the title Forge of Vulcan."),
    ("cand-7753", "Three other unnamed paintings by Francesco Solimena for the Buonaccorsi", "work", 391,
     "De Dominici is reported to mention three additional pictures; none is individually named here."),
    ("cand-7754", "Letter from Raimondo Buonaccorsi dated 6 July 1714 (Buonaccorsi family archives)", "archive", 391,
     "Cited as recording the arrival of Solimena's Dido painting; the letter itself was not consulted."),
    ("cand-7755", "Amico Ricci source cited as volume II, page 436 (title unresolved)", "archive", 389,
     "Footnote citation only; title and cited page were not independently identified or read."),
    ("cand-7756", "Amico Ricci", "person", 389,
     "Named as the author in a footnote citation; bibliographic identity is not otherwise supplied in this passage."),
    ("cand-7757", "Unidentified D. Miller publication from 1963", "archive", 390,
     "The footnote gives author abbreviation and year only; title and publication details are unresolved."),
    ("cand-7758", "Unidentified D. Miller publication from 1964", "archive", 390,
     "The footnote gives author abbreviation and year only; title and publication details are unresolved."),
    ("cand-7759", "Publication cited as Bologna (Plate 209; identity unresolved)", "archive", 161,
     "The footnote presents 'Bologna (Plate 209)' as the source publishing a replica; do not infer that it means the city."),
    ("cand-7760", "Replica of Solimena's Dido welcoming Aeneas to the Royal Hunt in the Scholz-Forni collection", "work", 161,
     "Replica reported through the unresolved citation 'Bologna (Plate 209)'; no further identity or date is supplied."),
    ("cand-7761", "Scholz-Forni collection", "", 161,
     "Collection is an independently meaningful referent, but current taxonomy has no collection type; preserve type as pending."),
    ("cand-7762", "Hamburg", "place", 161,
     "City named as the location of the Scholz-Forni collection in the footnote."),
    ("cand-7763", "Virgil's Aeneid (epic named as the source of the gallery paintings)", "archive", 155,
     "Literary source explicitly named as the single story represented by the palace paintings; identity relationship to index subentry cand-2778 remains for S3."),
    ("cand-7764", "Buonaccorsi family archives (repository not further identified)", "archive", 391,
     "Repository named for the 1714 letter; no institution or shelfmark is supplied."),
]
candidate_ids = {row["candidate_id"] for row in candidate_rows}
if any(candidate_id in candidate_ids for candidate_id, *_ in new_candidates):
    raise SystemExit("new candidate ID already exists")
existing_candidate_keys = {(row["canonical_name"], row["suggested_type"])
                           for row in candidate_rows if not row["index_entry_id"]}
new_candidate_keys = set()
for candidate_id, name, kind, line, detail in new_candidates:
    if (name, kind) in existing_candidate_keys or (name, kind) in new_candidate_keys:
        raise SystemExit(f"candidate natural-key collision: {(name, kind)}")
    new_candidate_keys.add((name, kind))
    candidate_rows.append({
        "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{P224 if line < 300 else NOTES}#L{line}" if line in range(152, 162) else
                                f"{NOTES}#L{line}",
    })
    candidate_ids.add(candidate_id)

new_mentions = []
existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mention_rows}


def mention(segment_id, source_line, mention_id, candidate_id, surface, note, occurrence=0):
    if mention_id in existing_mention_ids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in candidate_ids:
        raise SystemExit(f"missing mention candidate: {mention_id} -> {candidate_id}")
    meta = segment_by_id[segment_id]
    line = source_lines[source_line - 1]
    offset = line_offsets[(segment_id, source_line)]
    found_at = -1
    search_at = 0
    for _ in range(occurrence + 1):
        found_at = line.find(surface, search_at)
        if found_at < 0:
            raise SystemExit(f"mention surface not found at L{source_line}: {surface!r} #{occurrence}")
        search_at = found_at + 1
    start = offset + found_at
    end = start + len(surface)
    key = (segment_id, str(start), str(end))
    if key in existing_spans or any((row["segment_id"], row["start_char"], row["end_char"]) == key for row in new_mentions):
        raise SystemExit(f"duplicate mention span: {key}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


# Body: close the palace continuation, then preserve the page's narrative, reported attributions and modal language.
mention(P224, 153, "m-chp8-p224-states", "cand-1831", "States of the Church", "Political territory in Haskell's description of Macerata.")
mention(P224, 153, "m-chp8-p224-raimondo-1", "cand-0467", "Raimondo", "Patron for whom the palace was built.")
mention(P224, 153, "m-chp8-p224-earlier-palace", "cand-7747", "an earlier one", "Unnamed predecessor palace/building on the site; it is not described as a church.")
mention(P224, 153, "m-chp8-p224-father", "cand-7748", "his father", "Unnamed father of Raimondo; source reports acquisition of the predecessor building in 1701.")
mention(P224, 153, "m-chp8-p224-contini", "cand-0836", "Giovanni Battista Contini", "Reuse the index subentry for Contini's work on the Buonaccorsi palace.")
mention(P224, 153, "m-chp8-p224-raimondo-2", "cand-0467", "Raimondo", "Subject of the palace-decoration chronology.", 1)
mention(P224, 154, "m-chp8-p224-gallery-1", "cand-7749", "the long gallery", "Interior space in the palace.")
mention(P224, 154, "m-chp8-p224-gallery-fresco", "cand-7750", "a single fresco", "The vault fresco later identified as the Apotheosis of Aeneas.")
mention(P224, 155, "m-chp8-p224-gallery-windows", "cand-7749", "the gallery", "The room's windows and orientation.")
mention(P224, 155, "m-chp8-p224-palace-front", "cand-7731", "the palace", "Raimondo Buonaccorsi's palace in Macerata.")
mention(P224, 155, "m-chp8-p224-aeneid", "cand-7763", "the Aeneid", "Virgil's epic, named as the source narrative for the canvases.")
mention(P224, 155, "m-chp8-p224-italy", "cand-3461", "Italy", "Geographic scope of Haskell's comparison.")
mention(P224, 156, "m-chp8-p224-raimondo-summoned", "cand-0467", "Raimondo Buonaccorsi", "Patron who summoned the two painters in 1707.")
mention(P224, 156, "m-chp8-p224-rambaldi-first", "cand-2095", "Carlo Antonio", "Artist named across the line break; index subentry is for the Apotheosis with Dardani.")
mention(P224, 157, "m-chp8-p224-rambaldi", "cand-2095", "Rambaldi", "Continuation of the artist's name from p.224 L156.")
mention(P224, 157, "m-chp8-p224-dardani", "cand-0903", "Antonio Dardani", "Reuse the index subentry for the Apotheosis with Rambaldi.")
mention(P224, 157, "m-chp8-p224-apotheosis", "cand-7750", "the fresco of the Apotheosis of Aeneas", "The 1707 vault fresco commissioned for the gallery.")
mention(P224, 157, "m-chp8-p224-aeneas-apotheosis", "cand-4164", "Aeneas", "Mythological subject named in the fresco title.")
mention(P224, 157, "m-chp8-p224-epic", "cand-7763", "the epic", "Coreference to the Aeneid named earlier on p.224.")
mention(P224, 157, "m-chp8-p224-raimondo-he", "cand-0467", "he", "Coreference to Raimondo Buonaccorsi.")
mention(P224, 157, "m-chp8-p224-rome", "cand-4490", "Rome", "City described as capital of the Papal States.")
mention(P224, 157, "m-chp8-p224-papal-states", "cand-1831", "the papal states", "Political entity in which Raimondo lived, as reported by Haskell.")
mention(P224, 157, "m-chp8-p224-raimondo-he-chose", "cand-0467", "he", "Coreference to Raimondo Buonaccorsi.", 1)
mention(P224, 157, "m-chp8-p224-gallery-his", "cand-7749", "his gallery", "Coreference to Raimondo's gallery.")
mention(P224, 157, "m-chp8-p224-venus", "cand-4171", "Venus", "Mythological figure named in the painting subject.")
mention(P224, 157, "m-chp8-p224-venus-work", "cand-7751", "a picture of Venus in the Forge of Vulcan", "Painting selected for Raimondo's gallery; Haskell qualifies Garzi's authorship as apparent.")
mention(P224, 157, "m-chp8-p224-vulcan", "cand-7752", "Vulcan", "Mythological figure named in the painting subject.")
mention(P224, 157, "m-chp8-p224-garzi", "cand-1115", "Luigi Garzi", "Artist to whom the painting is apparently attributed.")
mention(P224, 158, "m-chp8-p224-naples", "cand-3534", "Naples", "City in which Haskell says Raimondo concentrated his attention.")
mention(P224, 158, "m-chp8-p224-bologna", "cand-3398", "Bologna", "City in the list of places on which Raimondo focused.")
mention(P224, 158, "m-chp8-p224-venice", "cand-3401", "Venice", "City in the list of places on which Raimondo focused.")
mention(P224, 159, "m-chp8-p224-solimena", "cand-2484", "Francesco Solimena", "Artist named for the Dido painting.")
mention(P224, 159, "m-chp8-p224-dido-work", "cand-2486", "Dido welcoming Aeneas to the Royal Hunt", "Reuse the work-specific Solimena index candidate.")
mention(P224, 159, "m-chp8-p224-aeneas-title", "cand-4164", "Aeneas", "Mythological figure named in the work title.")
mention(P224, 159, "m-chp8-p224-juno", "cand-3432", "Juno", "Mythological figure whose instructions frame the depicted storm.")
mention(P224, 159, "m-chp8-p224-aeneas-hero", "cand-4164", "the young Trojan hero", "Coreference to Aeneas in the narrative represented by the painting.")
mention(P224, 159, "m-chp8-p224-cupid", "cand-4321", "Cupid", "Mythological figure represented through the arrow aimed at Aeneas.")
mention(P224, 159, "m-chp8-p224-dido", "cand-4163", "Dido", "Mythological figure represented in the painting.")
mention(P224, 159, "m-chp8-p224-picture-enthusiasm", "cand-2486", "The picture", "Coreference to Solimena's Dido painting; the sentence continues on p.225.")

# Footnotes: citations remain bibliographic pointers; claims are reported at Haskell's level.
mention(NOTES, 389, "m-chp8-p224-n1-ricci-citation", "cand-7755", "Amico Ricci, H, p. 436", "Footnote citation; the PDF reads volume II, p. 436; the cited page was not independently read.")
mention(NOTES, 389, "m-chp8-p224-n1-ricci-author", "cand-7756", "Amico Ricci", "Author nested within the citation span.")
mention(P224, 160, "m-chp8-p224-n2-zanotti-citation", "cand-7115", "Zanotti, L PP396 and 418", "Footnote OCR citation; the printed text reads I, pp. 396 and 418; cited pages not independently read.")
mention(P224, 160, "m-chp8-p224-n2-zanotti-author", "cand-7114", "Zanotti", "Author nested within the citation span.")
mention(NOTES, 390, "m-chp8-p224-n3-miller-1963", "cand-7757", "1963", "One of two abbreviated D. Miller citations; title and cited pages are not supplied.")
mention(NOTES, 390, "m-chp8-p224-n3-miller-author", "cand-7735", "D. Miller", "Abbreviated author; possible identity with Dwight Miller acknowledged on p.223 is left for S3.")
mention(NOTES, 390, "m-chp8-p224-n3-miller-1964", "cand-7758", "1964", "Second abbreviated D. Miller citation; title and cited pages are not supplied.")
mention(NOTES, 391, "m-chp8-p224-n4-dominici-citation", "cand-4835", "De Dominici, IV, p. 428", "Footnote citation to volume IV, p. 428; the cited page was not independently read.")
mention(NOTES, 391, "m-chp8-p224-n4-dominici-author", "cand-7116", "De Dominici", "Author nested within the citation span.")
mention(NOTES, 391, "m-chp8-p224-n4-three-works", "cand-7753", "three other pictures", "Additional unnamed Solimena paintings reported by De Dominici.")
mention(NOTES, 391, "m-chp8-p224-n4-solimena", "cand-2484", "Solimena", "Artist associated with the three additional pictures.")
mention(NOTES, 391, "m-chp8-p224-n4-buonaccorsi-family", "cand-7729", "the Buonaccorsi", "Family/patronal referent; the passage does not specify which members commissioned the pictures.")
mention(NOTES, 391, "m-chp8-p224-n4-dido-arrival", "cand-2486", "Its arrival", "Coreference to the Dido painting; the letter is reported to record its arrival.")
mention(NOTES, 391, "m-chp8-p224-n4-letter", "cand-7754", "a letter from Raimondo", "Archival letter dated 6 July 1714; the document was not consulted.")
mention(NOTES, 391, "m-chp8-p224-n4-raimondo", "cand-0467", "Raimondo", "Sender named for the 6 July 1714 letter.")
mention(NOTES, 391, "m-chp8-p224-n4-family-archives", "cand-7764", "the family archives", "Repository for the letter, not further identified.")
mention(P224, 161, "m-chp8-p224-n4-bologna-publication", "cand-7759", "Bologna (Plate 209)", "Unresolved bibliographic reference, treated as a publication pointer rather than the city.")
mention(P224, 161, "m-chp8-p224-n4-replica", "cand-7760", "a replica", "Reported replica of Solimena's Dido painting.")
mention(P224, 161, "m-chp8-p224-n4-collection", "cand-7761", "the Scholz-Forni collection", "Collection identity retained with type pending under the current taxonomy.")
mention(P224, 161, "m-chp8-p224-n4-hamburg", "cand-7762", "Hamburg", "City where the collection is reported to be located.")


def quote(segment_id: str, first: int, last: int) -> str:
    return "\n".join(source_lines[first - 1:last])


ocr = [
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 155, "ocr": "fight", "print": "light", "basis": "CHP-8.pdf physical page 26."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 155, "ocr": "iconographie", "print": "iconographic", "basis": "CHP-8.pdf physical page 26."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 159, "ocr": "The dies primus leti primusque malorum/Causa suit", "print": "Ille dies primus leti primusque malorum/Causa fuit", "basis": "CHP-8.pdf physical page 26."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 389, "ocr": "Amico Ricci, H, p. 436", "print": "Amico Ricci, II, p. 436", "basis": "CHP-8.pdf physical page 26."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 160, "ocr": "Zanotti, L PP396 and 418", "print": "Zanotti, I, pp. 396 and 418", "basis": "CHP-8.pdf physical page 26."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 390, "ocr": "D. Miller, 1963 and 1964. -", "print": "D. Miller, 1963 and 1964.", "basis": "CHP-8.pdf physical page 26."},
]


def make_statement(statement_id, segment_id, first_line, last_line, subject, obj, predicate,
                   claim, qualification, mentioned, text_layer="body", extras=None):
    qualifiers = {
        "source_line_start": first_line, "source_line_end": last_line,
        "printed_page": 224, "pdf_physical_page": 26,
        "claim": claim, "speaker": "Haskell", "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    if extras:
        qualifiers.update(extras)
    return {
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote(segment_id, first_line, last_line),
        "origin": "book", "source_file": segment_by_id[segment_id]["source_file"],
    }


new_statements = [
    make_statement("st-chp8-p224-palace-construction", P224, 153, 153, "cand-0467", "cand-7731",
                   "palace_built_for_patron_on_predecessor_site",
                   "Haskell completes the p.223 comparison by identifying the palace as Raimondo Buonaccorsi's: it was being built for him during the first two decades of the eighteenth century on the site of an earlier building acquired in 1701 by his father.",
                   "The predecessor is unnamed; retain the reported chronology and the ambiguity over the precise acquisition object.",
                   ["cand-0467", "cand-7731", "cand-7747", "cand-7748"], extras={
                       "continued_from_segment_id": P223, "continued_from_statement_id": "st-chp8-p223-palace-superlative-open",
                       "continuation_status": "closed", "date_range": "first two decades of the eighteenth century",
                       "predecessor_acquisition_date": "1701", "relation_candidate": True}),
    make_statement("st-chp8-p224-contini-architect", P224, 153, 153, "cand-0836", "cand-7731",
                   "architect_of",
                   "Haskell names the Roman architect Giovanni Battista Contini as architect of Raimondo Buonaccorsi's palace at Macerata.",
                   "The passage reports the attribution; no architectural record is independently consulted.",
                   ["cand-0836", "cand-7731"], extras={"relation_candidate": True}),
    make_statement("st-chp8-p224-gallery-decoration-start", P224, 153, 154, "cand-0467", "cand-7749",
                   "began_gallery_decoration_by_1707",
                   "By 1707, enough progress had been made for Raimondo Buonaccorsi to begin decorating the palace's long gallery.",
                   "The date indicates that work on the palace had advanced sufficiently; it does not date completion of the building.",
                   ["cand-0467", "cand-7731", "cand-7749"], extras={"date": "1707", "relation_candidate": True}),
    make_statement("st-chp8-p224-gallery-survival-and-vault-fresco", P224, 154, 154, "cand-7749", "cand-7750",
                   "vault_covered_by_single_fresco",
                   "Haskell says the long gallery survived intact at the time of writing and that a single fresco covered the low barrel vault from end to end, giving some unity to the varied decoration.",
                   "'Today' is relative to Haskell's publication, not a current-condition check. The following sentence identifies the fresco as the Apotheosis of Aeneas.",
                   ["cand-7749", "cand-7750"], extras={"relation_candidate": True, "temporal_reference": "at time of Haskell's writing"}),
    make_statement("st-chp8-p224-gallery-window-material-description", P224, 155, 155, "cand-7749", "cand-7731",
                   "has_windows_opening_to_courtyard_and_palace_front",
                   "Haskell describes three windows on each side of the gallery opening toward the courtyard and palace front, with incoming light revealing coloured marble and elaborate wood and stucco ornament.",
                   "This is the source's description of the room and its decoration, not a present-day architectural survey.",
                   ["cand-7749", "cand-7731"], extras={"ocr_corrections": [ocr[0]]}),
    make_statement("st-chp8-p224-aeneid-cycle-and-style", P224, 155, 155, "cand-7749", "cand-7763",
                   "pictures_depict_aeneid_episodes_in_diverse_styles",
                   "Haskell describes the gallery's large canvases as stylistically diverse while representing episodes from the Aeneid; he attributes the decoration's exceptional effect in Italy to iconographic unity combined with stylistic diversity rather than intrinsic merit in the canvases.",
                   "The statement preserves Haskell's aesthetic judgment and does not assert an independent assessment of the paintings.",
                   ["cand-7749", "cand-7763", "cand-3461"], extras={"speaker_judgment": True, "ocr_corrections": [ocr[1]]}),
    make_statement("st-chp8-p224-rambaldi-dardani-apotheosis", P224, 156, 157, "cand-0467", "cand-7750",
                   "summoned_artists_to_paint_vault_fresco",
                   "Haskell says Raimondo summoned Carlo Antonio Rambaldi and Antonio Dardani in 1707 to paint the Apotheosis of Aeneas fresco on the gallery vault.",
                   "The statement records Haskell's report; it does not independently verify authorship or completion.",
                   ["cand-0467", "cand-2095", "cand-0903", "cand-7750", "cand-4164"], extras={
                       "date": "1707", "relation_candidate": True, "artist_candidate_ids": ["cand-2095", "cand-0903"]}),
    make_statement("st-chp8-p224-commissioned-aeneid-episodes", P224, 157, 157, "cand-0467", "cand-7763",
                   "commissioned_pictures_of_episodes_from",
                   "Soon after the vault fresco, Raimondo began commissioning pictures of individual episodes from the Aeneid for the gallery walls.",
                   "The source gives no complete list of paintings or their dates.",
                   ["cand-0467", "cand-7763", "cand-7749"], extras={"relation_candidate": True, "commission_start": "soon after 1707"}),
    make_statement("st-chp8-p224-roman-painting-and-garzi-picture", P224, 157, 157, "cand-0467", "cand-7751",
                   "selected_single_roman_example_for_gallery",
                   "Haskell says Roman painting had little appeal to Raimondo, who chose only one Roman example for the gallery: Venus in the Forge of Vulcan, apparently painted by Luigi Garzi.",
                   "'Apparently' qualifies the attribution to Garzi; the statement does not imply that he commissioned the painting.",
                   ["cand-0467", "cand-7749", "cand-4490", "cand-1831", "cand-4171", "cand-7751", "cand-7752", "cand-1115"],
                   extras={"relation_candidate": True, "attribution_modality": "apparently", "reported_artist_candidate_id": "cand-1115"}),
    make_statement("st-chp8-p224-regional-focus", P224, 158, 158, "cand-0467", None,
                   "author_characterizes_focus_on_naples_bologna_venice",
                   "Haskell characterizes Raimondo's attention as firmly concentrated on Naples, Bologna and Venice.",
                   "This is a summary of the patron's geographic focus, not a complete itinerary or list of commissions.",
                   ["cand-0467", "cand-3534", "cand-3398", "cand-3401"]),
    make_statement("st-chp8-p224-solimena-dido-arrival", P224, 159, 159, "cand-2484", "cand-2486",
                   "painting_among_first_to_arrive_and_author_calls_masterpiece",
                   "Haskell calls Solimena's Dido welcoming Aeneas to the Royal Hunt the masterpiece of the series and says it was among the first pictures to arrive.",
                   "'Masterpiece' is Haskell's evaluation; 'among the first' is preserved without an exact date.",
                   ["cand-2484", "cand-2486", "cand-4163", "cand-4164"], extras={"relation_candidate": True, "speaker_judgment": True, "ocr_corrections": [ocr[2]]}),
    make_statement("st-chp8-p224-dido-picture-narrative", P224, 159, 159, "cand-2486", "cand-4163",
                   "depicts_dido_and_aeneas_in_storm_scene",
                   "Haskell describes the painting as a storm scene in which Juno directs the winds, Aeneas approaches Dido while oblivious to Cupid's arrow, and Dido looks back at him with tender passion.",
                   "These are elements of the mythological narrative represented in the painting, not claims about historical events.",
                   ["cand-2486", "cand-3432", "cand-4164", "cand-4321", "cand-4163"]),
    make_statement("st-chp8-p224-dido-enthusiasm-open", P224, 159, 159, "cand-2486", None,
                   "aroused_great_enthusiasm_open_continuation",
                   "Haskell says the painting aroused the greatest enthusiasm and begins a continuation about interest that closes on p.225.",
                   "Keep the sentence open until the next page is reviewed.",
                   ["cand-2486"], extras={"continuation_status": "open", "continuation_to_segment_id": P225, "continuation_to_source_line": 164}),
    make_statement("st-chp8-p224-n1-ricci-citation", NOTES, 389, 389, "cand-7756", "cand-7755",
                   "cites_source",
                   "Footnote 1 cites Amico Ricci, volume II, page 436.",
                   "Citation verified against the page image; cited source and page were not independently read.",
                   ["cand-7756", "cand-7755"], text_layer="footnote citation", extras={"relation_candidate": False, "ocr_corrections": [ocr[3]]}),
    make_statement("st-chp8-p224-n2-zanotti-citation", P224, 160, 160, "cand-7114", "cand-7115",
                   "cites_source",
                   "Footnote 2 cites Zanotti, volume I, pages 396 and 418.",
                   "Citation wording checked against the page image; cited pages were not independently read.",
                   ["cand-7114", "cand-7115"], text_layer="footnote citation", extras={"relation_candidate": False, "ocr_corrections": [ocr[4]]}),
    make_statement("st-chp8-p224-n3-miller-citations", NOTES, 390, 390, "cand-7735", None,
                   "cites_two_publications_by_abbreviated_author",
                   "Footnote 3 cites D. Miller, 1963 and 1964.",
                   "Titles and page references are absent; identity with Dwight Miller acknowledged on p.223 remains an S3 alignment question.",
                   ["cand-7735", "cand-7757", "cand-7758"], text_layer="footnote citation", extras={"relation_candidate": False, "ocr_corrections": [ocr[5]]}),
    make_statement("st-chp8-p224-n4-dominici-citation", NOTES, 391, 391, "cand-7116", "cand-4835",
                   "cites_source",
                   "Footnote 4 cites De Dominici, volume IV, page 428.",
                   "The cited page was not independently read.",
                   ["cand-7116", "cand-4835"], text_layer="footnote citation", extras={"relation_candidate": False}),
    make_statement("st-chp8-p224-n4-dominici-reports-three-pictures", NOTES, 391, 391, "cand-7116", "cand-7753",
                   "mentions_three_other_pictures_by_solimena_for_buonaccorsi",
                   "Haskell reports that De Dominici also mentions three other pictures painted by Solimena for the Buonaccorsi.",
                   "The three works are not individually identified, and the cited page was not independently read.",
                   ["cand-7116", "cand-7753", "cand-2484", "cand-7729"], text_layer="footnote report",
                   extras={"relation_candidate": True, "quantity": 3, "work_group_candidate_id": "cand-7753"}),
    make_statement("st-chp8-p224-letter-records-dido-arrival", NOTES, 391, 391, "cand-7754", "cand-2486",
                   "records_arrival_of_painting",
                   "Footnote 4 says the arrival of Solimena's Dido painting is recorded in a letter from Raimondo dated 6 July 1714 in the family archives.",
                   "This is Haskell's report of an archival letter; the letter and archive were not consulted.",
                   ["cand-7754", "cand-0467", "cand-2486", "cand-7764"], text_layer="footnote report",
                   extras={"relation_candidate": True, "date": "1714-07-06", "repository_candidate_id": "cand-7764"}),
    make_statement("st-chp8-p224-replica-publication-report", P224, 161, 161, "cand-7759", "cand-7760",
                   "publishes_replica_reported_in_collection",
                   "The footnote says the source cited as Bologna (Plate 209) publishes a replica of the Dido painting in the Scholz-Forni collection in Hamburg.",
                   "The bibliographic identity behind 'Bologna' and the replica's identity are unresolved; retain the source wording and do not map it to the city.",
                   ["cand-7759", "cand-7760", "cand-7761", "cand-7762", "cand-2486"], text_layer="footnote report",
                   extras={"relation_candidate": True, "collection_type_pending": True}),
]

if len({row["statement_id"] for row in statement_rows}) != len(statement_rows):
    raise SystemExit("existing duplicate statement IDs")
statement_ids = {row["statement_id"] for row in statement_rows}
if any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("new statement ID already exists")
prior_id = "st-chp8-p223-palace-superlative-open"
prior = next((row for row in statement_rows if row["statement_id"] == prior_id), None)
if not prior or prior["qualifiers"].get("continuation_status") != "open":
    raise SystemExit("expected open p.223 palace statement not found")
patched_prior = json.loads(json.dumps(prior))
patched_prior["qualifiers"].update({
    "continuation_status": "closed", "continued_to_segment_id": P224,
    "continued_to_source_line": 153,
    "continuation_closed_by_statement_id": "st-chp8-p224-palace-construction",
})

new_coverage = []
for row in coverage_rows:
    sid = row["segment_id"]
    if sid == P223:
        row.update({"disposition": "reviewed", "migration_status": "complete",
                    "source_line_ranges": "L140-150", "note": "p.223 palace comparison closes at p.224 L153."})
    elif sid == P224:
        row.update({"disposition": "reviewed", "migration_status": "partial",
                    "source_line_ranges": "L152-161", "note": "p.224 read against CHP-8.pdf physical page 26; final Dido-painting sentence continues on p.225 L164."})
    elif sid == NOTES:
        row.update({"source_line_ranges": "L373-391", "migration_status": "partial",
                    "note": "p.224 notes 1, 3 and 4 migrated from the composite notes segment; note 2 is embedded at p.224 L160; later consolidated notes remain queued by printed page."})
    new_coverage.append(row)

preview = {
    "mode": "dry-run", "candidate_additions": len(new_candidates),
    "mention_additions": len(new_mentions), "statement_additions": len(new_statements),
    "statement_ids": [row["statement_id"] for row in new_statements],
    "continuations": [
        {"statement_id": prior_id, "status": "closed", "to": P224, "line": 153},
        {"statement_id": "st-chp8-p224-dido-enthusiasm-open", "status": "open", "to": P225, "line": 164},
    ],
    "coverage_updates": {
        P223: {"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L140-150"},
        P224: {"disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L152-161"},
        NOTES: {"source_line_ranges": "L373-391", "migration_status": "partial"},
    },
    "ocr_corrections": [f"L{x['source_line']} {x['ocr']} -> {x['print']}" for x in ocr],
}

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
write_csv_atomic(TABLES / "s2-coverage.csv", coverage_fields, new_coverage)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
