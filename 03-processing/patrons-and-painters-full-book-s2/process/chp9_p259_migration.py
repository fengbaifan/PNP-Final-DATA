"""Controlled S2 migration for printed p.259; defaults to a read-only dry run."""
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
P258 = "chp-9:09_CHP-9_intro:l179-186"
P259 = "chp-9:09_CHP-9_intro:l188-200"
P260 = "chp-9:09_CHP-9_intro:l202-210"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
PLATES = "front-matter:00_05_List_of_Plates:l123-138"
EXPECTED_HASH = "717631e0c86fc16769da90d83e6363ce28a3576fbe24c8be41eb46d2d6958d2b"
EXPECTED_ASSET_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
BACKUP_SUFFIX = ".bak-s2-chp9-p259-20261001"


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
for sid in (P258, P259, P260, NOTES, PLATES):
    if sid not in segment_by_id:
        raise SystemExit(f"missing source segment: {sid}")
meta = segment_by_id[P259]
if meta["sha256"] != EXPECTED_HASH or meta["asset_sha256"] != EXPECTED_ASSET_HASH:
    raise SystemExit("p.259 source segment or source asset fingerprint changed")
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


offsets_by_segment = {sid: line_offsets(sid) for sid in (P259, NOTES)}


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
    P258: ("reviewed", "partial", "L180-186"),
    P259: ("queued", "pending", ""),
    NOTES: ("reviewed", "partial", "L349-388; p.255 L155 continuation"),
}
for sid, expected in expected_states.items():
    row = coverage_by_id.get(sid)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != expected:
        raise SystemExit(f"unexpected coverage state for {sid}: {row}")

candidate_ids = {r["candidate_id"] for r in candidates}
if len(candidate_ids) != len(candidates) or max(int(x.split("-")[1]) for x in candidate_ids) != 8457:
    raise SystemExit("candidate inventory changed; inspect before allocating IDs")
candidate_specs = [
    (8458, "Church of the Carmini, Venice (as named by Haskell)", "place", P259, 192,
     "Church/building opposite the indexed Foscarini palace; distinct from the Carmini district and Scuola Grande dei Carmini."),
    (8459, "Angelo Querini's proposed reforms of 1762", "term", P259, 189,
     "The reform proposals are mentioned as the political issue opposed by Marco Foscarini; their content is not summarized here."),
    (8460, "Integrity and learning as older Venetian civic virtues", "term", P259, 190,
     "Values that Haskell says contemporaries associated with Venetian statesmen and Marco Foscarini."),
    (8461, "Seven unidentified Tintoretto paintings left in the Foscarini palace", "", P259, 193,
     "A source-described group of seven paintings; the works are unnamed and the taxonomy has no collection/group-of-works type, so this candidate is intentionally untyped."),
    (8462, "Marco Foscarini's library of manuscripts and history books", "archive", P259, 194,
     "A source-described documentary/book collection; distinguish the collection from a library building or institution."),
    (8463, "Palazzo di S. Marco, Rome (as named by Haskell)", "place", P259, 195,
     "Palace named as Pompeo Batoni's residence during Foscarini's Roman embassy; no modern building identity is inferred."),
    (8464, "Unidentified portrait of Marco Foscarini drawn by Pompeo Batoni", "work", P259, 195,
     "A portrait named in the account but without a title or further object identifier; keep separate from Batoni's Triumph of Venice."),
    (8465, "Pietro Visconti (architectural painter cited in p.259 note 3)", "person", NOTES, 391,
     "Named as the sender of the 1749 letter used for the palace income estimate; identity is limited to the cited name."),
    (8466, "Pietro Visconti's letter to Gian Pietro Ligari (1749; published locator)", "archive", NOTES, 391,
     "Letter cited for the palace income estimate, published by Arslan in 1952, p.63; neither letter nor publication was independently consulted."),
    (8467, "Arslan (publisher/editor named in p.259 note 3)", "person", NOTES, 391,
     "Surname-only citation form; no full name or identity is inferred."),
    (8468, "Fontana, page 291 (citation locator in p.259 note 2)", "archive", NOTES, 390,
     "Haskell supplies only the surname and page locator here; do not infer a particular Fontana or work."),
    (8469, "Pietro Foscarini's will (Biblioteca Correr, Cod. Cicogna MMDCCCCXLV-2686)", "archive", NOTES, 392,
     "Archival document cited with the manuscript shelfmark; not independently consulted."),
    (8470, "Inventory of Pietro Foscarini's pictures (Biblioteca Correr, Cod. Cicogna MMDCCCCXLV-2686)", "archive", NOTES, 392,
     "Archival inventory cited with the same shelfmark as Pietro Foscarini's will; not independently consulted."),
    (8471, "Austrian government (recipient in Haskell's library-transfer account)", "institution", NOTES, 393,
     "Political recipient named in the report of the library's 1800 sale; no more specific institution is inferred."),
    (8472, "Hofbibliothek, Vienna (library holding Marco Foscarini's collection in Haskell's account)", "institution", NOTES, 393,
     "Institution named as the collection's later location; distinct from the city of Vienna."),
    (8473, "Kress Foundation, New York (repository named in p.259 note 6)", "institution", NOTES, 394,
     "Repository wording in Haskell's note; keep separate from the front-matter caption's Raleigh museum and Samuel H. Kress Collection labels pending review."),
    (8474, "Greek sages represented in Batoni's Triumph of Venice", "term", P259, 197,
     "Unnamed group of figures in the painting; do not invent individual identities."),
    (8475, "Mercury represented in Batoni's Triumph of Venice", "term", P259, 197,
     "Mythological figure as an iconographic role in this painting, not a person KU."),
    (8476, "Roman warrior represented in Batoni's Triumph of Venice", "term", P259, 197,
     "Unnamed figure as an iconographic role in the painting, not an identified historical person."),
    (8477, "Neptune represented in Batoni's Triumph of Venice", "term", P259, 197,
     "Mythological figure as an iconographic role in this painting, not a person KU."),
    (8478, "Minerva represented in Batoni's Triumph of Venice", "term", P259, 198,
     "Mythological figure as an iconographic role in this painting, not a person KU."),
    (8479, "Arts represented in Batoni's Triumph of Venice", "term", P259, 198,
     "Allegorical group/role in the painting; no individual arts or figures are specified."),
    (8480, "History represented in Batoni's Triumph of Venice", "term", P259, 198,
     "Personified allegorical role in the painting, not a person KU."),
    (8481, "Fame represented in Batoni's Triumph of Venice", "term", P259, 198,
     "Personified allegorical role in the painting, not a person KU."),
    (8482, "Foscarini palace gallery or art holdings valued at 200,000 ducats (object scope unresolved)", "", P259, 193,
     "The 1749 quotation values a gallery, but does not clarify whether the object is the room, its paintings, or the collection; intentionally untyped."),
    (8483, "A. Clark (author cited in p.259 note 6; identity unresolved)", "person", NOTES, 394,
     "Initial and surname only; kept separate from other A. Clark citations pending S3 identity alignment."),
    (8484, "A. Clark, 1959, pages 232-236 (citation locator for Batoni's Triumph of Venice)", "archive", NOTES, 394,
     "Haskell's bibliographic locator; title is not supplied and the cited pages were not independently consulted."),
    (8485, "Marco Foscarini's other pictures (unnamed group, continued at p.260)", "", P259, 200,
     "Open source-defined group; the sentence continues on p.260 and supplies the needed description there. Intentionally untyped until the object scope is clear."),
    (8486, "Venetian statesmen as a source-described civic group", "term", P259, 191,
     "Collective category in Haskell's generalization; no individual list is supplied."),
    (8487, "Paintings commissioned by Marco Foscarini to illustrate his literary interests", "", P259, 194,
     "Plural, not individually identified as a unified collection or single work; intentionally untyped pending the continuation and object-level distinction."),
    (8488, "Doge Lionardo Loredano (historical person named in the painting programme)", "person", P259, 195,
     "Individual named as the Doge associated with the Republic's recovery; preserve the spelling variant Loredano/Loredan in source mentions."),
    (8489, "Venetian taste as an art-historical concept in Haskell's account", "term", P259, 199,
     "Aesthetic category in Haskell's judgment of Batoni; distinct from Venice the city and the Venetian State."),
    (8490, "Other unidentified Venetian classic paintings left in the Foscarini palace", "", P259, 193,
     "Works distinct from the seven Tintorettos, but no individual titles are supplied; intentionally untyped as an unnamed group."),
]
natural_keys = {(r["canonical_name"], r["suggested_type"]) for r in candidates}
for n, name, kind, source_segment, line_no, detail in candidate_specs:
    cid = f"cand-{n:04d}"
    if cid in candidate_ids or (name, kind) in natural_keys:
        raise SystemExit(f"candidate ID or natural-key collision: {cid} {name} / {kind}")
    candidates.append({
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open", "index_source_file": "",
        "sub_entry": "", "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{source_segment}#L{line_no}",
    })
    candidate_ids.add(cid)
    natural_keys.add((name, kind))

existing_mention_ids = {r["mention_id"] for r in mentions}
existing_spans = {(r["segment_id"], r["start_char"], r["end_char"]) for r in mentions}
new_mentions = []


def mention(segment_id, first_line, suffix, cid, surface, note="", last_line=None, occurrence=0):
    mid = f"m-chp9-p259-{suffix}"
    if mid in existing_mention_ids or any(r["mention_id"] == mid for r in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mid}")
    last_line = first_line if last_line is None else last_line
    search_text = "\n".join(source_lines[n - 1] for n in range(first_line, last_line + 1))
    start_at = 0
    pos = -1
    for _ in range(occurrence + 1):
        pos = search_text.find(surface, start_at)
        if pos < 0:
            raise SystemExit(f"surface not found at L{first_line}-{last_line}: {surface!r}")
        start_at = pos + len(surface)
    start = offsets_by_segment[segment_id][first_line] + pos
    end = start + len(surface)
    span = (segment_id, str(start), str(end))
    if span in existing_spans or any((r["segment_id"], r["start_char"], r["end_char"]) == span for r in new_mentions):
        raise SystemExit(f"duplicate mention span: {mid}")
    if cid not in candidate_ids:
        raise SystemExit(f"missing candidate for mention {mid}: {cid}")
    new_mentions.append({"mention_id": mid, "segment_id": segment_id, "candidate_id": cid,
                         "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


MENTION_SPECS = [
    (P259, 189, "querini-surname", "cand-2075", "Querini", "Closes p.258's first-name-only reference to Angelo Querini."),
    (P259, 189, "querini-reforms", "cand-8459", "reforms", "The proposed reform programme of 1762; details are not stated here."),
    (P259, 190, "doge-office", "cand-8450", "Doge", "Office Marco Foscarini attained; the manner is explicitly said to be suspect."),
    (P259, 190, "old-virtues", "cand-8460", "integrity and learning", "Values attributed to the earlier Venetian statesman ideal."),
    (P259, 190, "venetian-statesmen", "cand-8486", "Venetian\nStatesmen", "Source-defined collective group across the OCR line break.", 191),
    (P259, 192, "foscarini-palace", "cand-1059", "The family palace", "Indexed Foscarini palace candidate reused; specific church relation recorded as a claim."),
    (P259, 192, "carmini-church", "cand-8458", "the church of the Carmini", "Venice church building; distinct from Carmini area and Scuola Grande dei Carmini."),
    (P259, 192, "foscarini-family-richest", "cand-1057", "the family", "Foscarini family in the painter's reported quotation."),
    (P259, 192, "venice-richest", "cand-2719", "Venice", "City named in the quoted wealth claim."),
    (P259, 192, "visconti-body-role", "cand-8465", "one architectural painter", "Haskell's unnamed body reference is linked to Pietro Visconti by note 3."),
    (P259, 193, "gallery-valuation", "cand-8482", "a gallery worth 200,000 ducats", "A source-defined gallery or holding, kept untyped because object scope is unclear."),
    (P259, 193, "seven-tintorettos", "cand-8461", "seven Tintorettos", "Unidentified group of seven paintings attributed to Tintoretto in the passage."),
    (P259, 193, "other-venetian-classics", "cand-8490", "other Venetian classics", "A second, unnamed group distinct from the seven Tintorettos."),
    (P259, 193, "pietro-former-owner", "cand-1056", "Pietro Foscarini", "Existing indexed person candidate reused; keep distinct from Marco Foscarini."),
    (P259, 193, "procuratore-pietro", "cand-8449", "Procuratore di San Marco", "Office named for Pietro Foscarini."),
    (P259, 194, "marco-library-passage", "cand-8462", "his magnificent library of manuscripts and other works", "Collection of manuscripts/books, distinct from a library building.", 194),
    (P259, 194, "venice-history-library", "cand-2719", "history of Venice", "Subject of most books in Marco Foscarini's library."),
    (P259, 194, "commissioned-paintings", "cand-8487", "The paintings he commissioned", "Unidentified plural group described by their intended function."),
    (P259, 194, "literary-interests", "cand-8462", "his literary interests", "Purpose assigned to commissioned paintings; connected to the library account."),
    (P259, 194, "rome-embassy", "cand-4490", "Rome", "City of Foscarini's embassy; the 1737–1740 interval is retained in the statement."),
    (P259, 195, "pompeo-batoni", "cand-0262", "Pompeo Batoni", "Existing indexed person candidate reused."),
    (P259, 195, "palazzo-san-marco-rome", "cand-8463", "the Palazzo di S. Marco", "Roman palace named as the shared residence of Foscarini and Batoni."),
    (P259, 195, "batoni-portrait", "cand-8464", "his portrait", "Unidentified portrait of Marco Foscarini by Batoni."),
    (P259, 195, "triumph-venice-work", "cand-4085", "Triumph 0/ Venice", "OCR surface; existing accepted work candidate for Batoni's plate 45 painting reused; scan reads 'Triumph of Venice'."),
    (P259, 195, "republic-in-programme", "cand-8105", "the Repubhc", "Raw OCR surface for the Venetian State; the statement records the scan reading 'Republic'."),
    (P259, 195, "league-cambrai", "cand-8351", "league of Cambrai", "Existing event candidate reused."),
    (P259, 195, "venice-recovery", "cand-2719", "Venice", "City in the painting programme's history of recovery."),
    (P259, 196, "lionardo-loredano-programme", "cand-8488", "Doge Lionardo Loredano", "Historical person named in the work's programme."),
    (P259, 196, "venice-recovery-state", "cand-8105", "Venice", "Political entity in Haskell's interpretation of the painting's historic programme."),
    (P259, 197, "triumph-venice-again", "cand-4085", "the picture", "Anaphoric reference to The Triumph of Venice."),
    (P259, 197, "greek-sages", "cand-8474", "Greek sages", "Unnamed iconographic group; no identities are inferred."),
    (P259, 197, "mercury-figure", "cand-8475", "Mercury", "Iconographic role in the painting, typed as a term rather than a person KU."),
    (P259, 197, "venice-achievements", "cand-8105", "Venice", "The Venetian State whose achievements are represented in the picture."),
    (P259, 197, "state-exalted", "cand-8105", "the State", "The Venetian political entity named as the painting's subject."),
    (P259, 197, "roman-warrior", "cand-8476", "a Roman warrior", "Unnamed iconographic role, not an identified historical person."),
    (P259, 197, "neptune-figure", "cand-8477", "Neptune", "Iconographic role in the painting, typed as a term rather than a person KU."),
    (P259, 198, "minerva-figure", "cand-8478", "Minerva", "Iconographic role in the painting, typed as a term rather than a person KU."),
    (P259, 198, "arts-allegory", "cand-8479", "the arts", "Allegorical group represented in the foreground."),
    (P259, 198, "republic-chariot", "cand-8105", "the Republic", "Venetian State represented by the chariot."),
    (P259, 198, "loredano-chariot", "cand-8488", "Doge Loredan", "Raw OCR name form for Doge Lionardo Loredano; scan confirms final -o."),
    (P259, 199, "history-personification", "cand-8480", "History", "Personified allegorical role in the painting, not a person KU."),
    (P259, 199, "fame-personification", "cand-8481", "Fame", "Personified allegorical role in the painting, not a person KU."),
    (P259, 199, "minerva-classical", "cand-8478", "Minerva", "The figure's style is discussed in the source."),
    (P259, 199, "roman-warrior-classical", "cand-8476", "the Roman warrior", "The figure's style is discussed in the source."),
    (P259, 199, "batoni-taste", "cand-0262", "Batoni", "Existing artist candidate reused for Haskell's style judgment."),
    (P259, 199, "venetian-taste", "cand-8489", "Venetian taste", "Art-historical concept, distinct from the city and State."),
    (P259, 200, "other-pictures", "cand-8485", "other pictures", "Open group whose description continues on p.260."),
    (NOTES, 389, "querini-note", "cand-2075", "Angelo Querini", "Cross-reference to a later chapter; no new biographical claim."),
    (NOTES, 390, "fontana-citation", "cand-8468", "Fontana, p. 291", "Incomplete bibliographic locator as printed."),
    (NOTES, 391, "visconti-note-author", "cand-8465", "Pietro Visconti", "Author of the letter cited for the painter's 1749 estimate."),
    (NOTES, 391, "ligari-note-addressee", "cand-1408", "Gian Pietro Ligari", "Existing indexed person candidate reused."),
    (NOTES, 391, "visconti-ligari-letter", "cand-8466", "Pietro Visconti to Gian Pietro Ligari", "The cited archival letter; its exact date is not given in this note."),
    (NOTES, 391, "arslan-editor", "cand-8467", "Arslan", "Surname-only publisher/editor citation form."),
    (NOTES, 392, "pietro-will-author", "cand-1056", "Pietro Foscarini", "Existing indexed person candidate reused; distinct from Marco."),
    (NOTES, 392, "pietro-will", "cand-8469", "Pietro Foscarini’s will", "Archival document as named in the note."),
    (NOTES, 392, "pietro-inventory", "cand-8470", "the inventory of his pictures", "Separate archival document listed with the will."),
    (NOTES, 392, "biblioteca-correr", "cand-8262", "Biblioteca Correr", "Existing repository institution candidate reused."),
    (NOTES, 392, "cod-cicogna-shelfmark", "cand-8469", "Cod. Cicogna, MMDCCCCXLV—2686", "Shelfmark cited for the will and inventory."),
    (NOTES, 393, "foscarini-library-sale", "cand-8462", "The library", "Anaphoric reference to Marco Foscarini's collection."),
    (NOTES, 393, "foscarini-descendants", "cand-1057", "Marco Foscarini’s descendants", "The descendants are not enumerated; no individual family members are inferred."),
    (NOTES, 393, "austrian-government", "cand-8471", "die Austrian government", "Raw OCR surface; the statement records the scan reading 'the Austrian government'."),
    (NOTES, 393, "hofbibliothek", "cand-8472", "the Hofbibliothek", "Institution named as the collection's current location in Haskell's account."),
    (NOTES, 393, "vienna-hofbibliothek", "cand-2772", "Vienna", "City named as the location of the Hofbibliothek."),
    (NOTES, 394, "kress-foundation", "cand-8473", "the Kress Foundation at New York", "Repository claim for the painting in Haskell's note; compare the front-matter caption without resolving the difference here."),
    (NOTES, 394, "new-york-location", "cand-7473", "New York", "City named in the repository locator; existing place candidate reused."),
    (NOTES, 394, "a-clark-p259", "cand-8483", "A. Clark", "Initial and surname only; keep this p.259 citation candidate open for S3 alignment."),
    (NOTES, 394, "clark-1959-pages", "cand-8484", "1959, PP2Z2-6", "Raw OCR locator; the scan reads 1959, pp.232–6."),
]
for spec in MENTION_SPECS:
    mention(*spec)

new_statements = []
existing_statement_ids = {r["statement_id"] for r in statements}


def statement(suffix, segment_id, first, last, subject, obj, predicate, claim, qualification,
              mentioned, marker=None, speaker="Haskell", text_layer="body", extras=None):
    sid = f"st-chp9-p259-{suffix}"
    if sid in existing_statement_ids or any(r["statement_id"] == sid for r in new_statements):
        raise SystemExit(f"duplicate statement ID: {sid}")
    m = segment_by_id[segment_id]
    if first < m["line_start"] or last > m["line_end"]:
        raise SystemExit(f"statement lines outside segment {segment_id}: {sid}")
    if any(cid and cid not in candidate_ids for cid in [subject, obj, *mentioned]):
        raise SystemExit(f"missing candidate in statement: {sid}")
    q = {"source_line_start": first, "source_line_end": last, "printed_page": 259,
         "pdf_physical_page": 21, "claim": claim, "speaker": speaker, "text_layer": text_layer,
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


statement("querini-reforms-context", P259, 189, 189, "cand-1053", "cand-2075",
          "strongest_stand_against_querini_and_proposed_reforms_1762",
          "Haskell says Foscarini took the strongest stand against Angelo Querini and his proposed reforms in 1762.",
          "The reform content is not supplied here; p.258's split first-name mention is closed by this surname. This remains a source claim and relation candidate.",
          ["cand-1053", "cand-2075", "cand-8459"], marker=1,
          extras={"relation_candidate": True, "cross_reference_segments": [{"segment_id": P258, "source_line_start": 186, "source_line_end": 186}]})
statement("foscarini-doge-accession-suspected", P259, 190, 190, "cand-1053", "cand-8450",
          "methods_of_becoming_doge_open_to_suspicion",
          "Haskell says the methods by which Foscarini became Doge were open to suspicion.",
          "The source gives no detail of the suspected methods; preserve this caution without specifying a cause.",
          ["cand-1053", "cand-8450"])
statement("contemporaries-saw-old-virtues", P259, 190, 191, "cand-1053", "cand-8460",
          "contemporaries_saw_foscarini_as_last_incarnation_of_old_venetian_virtues",
          "Haskell says Foscarini seemed to his contemporaries to represent the last surviving incarnation of the integrity and learning that had made Venetian statesmen respected.",
          "Preserve 'seemed to his contemporaries' and the author's broad historical characterization; it is not an independent consensus measurement.",
          ["cand-1053", "cand-8460", "cand-8486"])
statement("foscarini-proud-cultivated-and-scholarly", P259, 191, 191, "cand-1053", None,
          "proud_cultivated_character_and_ambitious_scholarly_tastes",
          "Haskell characterizes Foscarini as proud and cultivated and says his patronage shows ambitious and scholarly tastes.",
          "Authorial characterization; keep it attributed to Haskell.", ["cand-1053"])
statement("foscarini-palace-location-and-decoration", P259, 192, 192, "cand-1059", "cand-8458",
          "palace_opposite_church_of_carmini_and_repeatedly_decorated",
          "Haskell says the Foscarini family palace stood opposite the Church of the Carmini and was repeatedly decorated with great lavishness.",
          "Use the index palace candidate as the source-named building; exact building identity and decoration phases remain for S3/S5, and no decorator is inferred.",
          ["cand-1059", "cand-8458", "cand-1057"], marker=2, extras={"relation_candidate": True})
statement("visconti-1749-wealth-quotation", P259, 192, 193, "cand-8465", "cand-1057",
          "reported_foscarini_family_income_and_palace_holdings",
          "Haskell quotes an architectural painter working at the palace in 1749 as calling the Foscarini family the richest in Venice and reporting 130,000 ducats annual income, many palaces and jewels, and a gallery worth 200,000 ducats.",
          "Nested report: the estimate is attributed by note 3 to Pietro Visconti and preserved as a 1749 quotation; the figures and superlative are not independently verified. The scan clarifies the OCR reading '13 0,000' as '130,000'.",
          ["cand-8465", "cand-1057", "cand-2719", "cand-1059", "cand-8482"], speaker="Pietro Visconti as cited by Haskell",
          extras={"relation_candidate": True, "ocr_corrections": [{"source_line": 192, "ocr": "13 0,000", "print": "130,000", "basis": "CHP-9.pdf physical page 21"}, {"source_line": 193, "ocr": "- number", "print": "number", "basis": "CHP-9.pdf physical page 21; line-leading dash is an OCR/layout artifact."}]})
statement("pietro-left-picture-group-with-palace", P259, 193, 193, None, "cand-1059",
          "former_owner_left_pictures_with_palace",
          "Haskell says many pictures, including seven Tintorettos and other Venetian classics, had been left with the palace by its former owner Pietro Foscarini, who died in 1745.",
          "Pietro Foscarini is the index candidate distinct from Marco Foscarini; the several works are unnamed and remain a source-described group. Preserve the printed date and do not infer how or when the group was transferred.",
          ["cand-8461", "cand-8490", "cand-1059", "cand-1056", "cand-1057"], marker=4,
          extras={"relation_candidate": True, "ocr_corrections": [{"source_line": 193, "ocr": "1745?", "print": "1745", "basis": "CHP-9.pdf physical page 21; superscript note marker 4 follows the year."}]})
statement("pietro-foscarini-procuratore", P259, 193, 193, "cand-1056", "cand-8449",
          "pietro_foscarini_was_procuratore_di_san_marco",
          "Haskell identifies the former owner, Pietro Foscarini, as a Procuratore di San Marco.",
          "Source-reported office; do not merge Pietro Foscarini with Marco Foscarini.", ["cand-1056", "cand-8449"], extras={"relation_candidate": True})
statement("marco-library-versus-pictures", P259, 194, 194, "cand-1053", "cand-8462",
          "more_interested_in_books_and_library_than_pictures",
          "Haskell says Marco Foscarini was more interested in books than pictures and devoted his main attention to a magnificent library of manuscripts and other works, mostly about Venetian history.",
          "Keep the author's comparative assessment and the collection as source-described; no book titles or contents are supplied.",
          ["cand-1053", "cand-8462", "cand-2719"])
statement("marco-commissioned-pictures-literary-purpose", P259, 194, 194, "cand-1053", "cand-8487",
          "commissioned_paintings_intended_to_illustrate_literary_interests",
          "Haskell says the paintings Foscarini commissioned were intended primarily to illustrate his literary interests.",
          "The plural group is not a single identified work; keep it untyped and do not infer all the subjects from this page.",
          ["cand-8487", "cand-1053", "cand-8462"], extras={"relation_candidate": True})
statement("leading-artists-exception", P259, 194, 194, "cand-1053", None,
          "unlikely_to_have_used_leading_artists_except_one",
          "Haskell says that, with one exception, it is unlikely Foscarini used any leading artists of his day.",
          "Preserve 'unlikely' and 'with one exception'; the next sentence describes Batoni, but the identification of him as the exception remains an immediate-context reading.",
          ["cand-1053", "cand-0262"])
statement("batoni-rome-embassy-portrait", P259, 194, 195, "cand-1053", "cand-8464",
          "batoni_employed_to_draw_foscarini_portrait_during_rome_embassy",
          "Haskell says that during Foscarini's embassy in Rome from 1737 to 1740 he employed Pompeo Batoni, who lived in the Palazzo di S. Marco like him, to draw his portrait.",
          "The portrait is unnamed and distinct from The Triumph of Venice; preserve the reported embassy interval and shared residence without identifying the modern palace.",
          ["cand-1053", "cand-0262", "cand-4490", "cand-8463", "cand-8464"], marker=6,
          extras={"relation_candidate": True, "cross_reference_segments": [{"segment_id": PLATES, "source_line_start": 123, "source_line_end": 123}],
                  "ocr_corrections": [{"source_line": 195, "ocr": "Eke him", "print": "like him", "basis": "CHP-9.pdf physical page 21."}]})
statement("batoni-triumph-painted-to-marco-programme", P259, 195, 195, "cand-0262", "cand-4085",
          "batoni_painted_triumph_of_venice_to_marco_programme",
          "Haskell says Batoni painted The Triumph of Venice according to a programme clearly drawn up by Foscarini himself.",
          "Reuse the Plate 45 work candidate, distinct from Bambini's earlier Triumph of Venice; authorship/programme here are Haskell's report, not an external attribution check.",
          ["cand-0262", "cand-4085", "cand-1053"], marker=6, extras={"relation_candidate": True,
          "cross_reference_segments": [{"segment_id": PLATES, "source_line_start": 123, "source_line_end": 123}],
          "ocr_corrections": [{"source_line": 195, "ocr": "Triumph 0/ Venice", "print": "Triumph of Venice", "basis": "CHP-9.pdf physical page 21."}]})
statement("triumph-programme-venetian-recovery", P259, 195, 196, "cand-4085", "cand-8105",
          "programme_celebrated_republic_recovering_after_cambrai_wars",
          "The programme for The Triumph of Venice represented the flourishing state of the Republic after the wars incited by the League of Cambrai, when peace returned and the fine arts flourished again in Venice, fostered by Doge Lionardo Loredano.",
          "This is the programme as quoted by Haskell; it does not independently verify the historical explanation or turn the depicted doge into a patron of Batoni's painting.",
          ["cand-4085", "cand-8105", "cand-8351", "cand-2719", "cand-8488"],
          extras={"ocr_corrections": [{"source_line": 195, "ocr": "Repubhc", "print": "Republic", "basis": "CHP-9.pdf physical page 21."}, {"source_line": 196, "ocr": "- by Doge", "print": "by Doge", "basis": "CHP-9.pdf physical page 21; line-leading dash is an OCR/layout artifact."}]})
statement("triumph-as-encouragement-from-past", P259, 196, 196, "cand-4085", "cand-1053",
          "subject_typified_foscarini_seeking_encouragement_from_past",
          "Haskell says the subject, harking back to Venice's recovery after earlier disasters, typified Foscarini's desire to seek encouragement from past history.",
          "Interpretive reading by Haskell, not a direct statement of Foscarini's intention beyond the programme attributed to him.",
          ["cand-4085", "cand-8105", "cand-1053"])
statement("triumph-exalted-state-over-family", P259, 196, 197, "cand-4085", "cand-8105",
          "historical_picture_exalted_state_without_family_triumphs",
          "Haskell calls the painting one of very few historical pictures for a Venetian patron with no reference to the patron's family triumphs and devoted purely to exalting the State.",
          "Comparative claim and interpretation belong to Haskell; do not quantify the wider corpus from this sentence.",
          ["cand-4085", "cand-8105", "cand-1053"])
statement("triumph-depicts-sages-and-warrior", P259, 197, 197, "cand-4085", None,
          "mercury_shows_venetian_achievements_to_greek_sages_neptune_shows_grandeur_to_roman_warrior",
          "Haskell describes Greek sages on the right being shown Venice's recorded achievements by Mercury, while Neptune points out Venice's present grandeur to a Roman warrior on the left.",
          "Iconographic description of the painting; unnamed sages and warrior remain generic, and mythological roles are terms rather than person KUs.",
          ["cand-4085", "cand-8474", "cand-8475", "cand-8105", "cand-8476", "cand-8477"])
statement("triumph-depicts-arts-republic-history-fame", P259, 198, 198, "cand-4085", None,
          "minerva_and_arts_in_foreground_republic_chariot_surveyed_by_history_and_fame",
          "Haskell says the arts are at Minerva's feet in the foreground; at the centre, History and Fame survey the chariot of the Republic with Doge Loredano.",
          "Composition description, not a real political event or an additional relationship among the allegorical figures.",
          ["cand-4085", "cand-8478", "cand-8479", "cand-8105", "cand-8488", "cand-8480", "cand-8481"],
          extras={"ocr_corrections": [{"source_line": 198, "ocr": "Doge Loredan", "print": "Doge Loredano", "basis": "CHP-9.pdf physical page 21."}]})
statement("batoni-classicism-and-venetian-taste", P259, 199, 199, "cand-4085", "cand-0262",
          "figures_unusually_classical_and_batoni_made_no_concessions_to_venetian_taste",
          "Haskell says Minerva and the Roman warrior were extraordinarily classical for the period and that Batoni made no concessions to Venetian taste.",
          "Authorial style judgment; no broader claim about all Venetian viewers or artists is inferred.",
          ["cand-4085", "cand-8478", "cand-8476", "cand-0262", "cand-8489"])
statement("note1-querini-cross-reference", NOTES, 389, 389, "cand-2075", None,
          "cross_reference_to_angelo_querini_chapter_15",
          "Haskell's note 1 directs readers to Chapter 15 for Angelo Querini.",
          "Editorial cross-reference only; not a biographical fact or independent evidence.",
          ["cand-2075"], marker=1, speaker="Haskell's footnote", text_layer="footnote citation",
          extras={"cross_reference_segments": [{"segment_id": P259, "source_line_start": 189, "source_line_end": 189}]})
statement("note2-fontana-citation", NOTES, 390, 390, None, "cand-8468",
          "citation_locator_fontana_page_291",
          "Haskell's note 2 cites Fontana, page 291.",
          "Bibliographic locator only; the surname and work are not resolved and the cited page was not consulted.",
          ["cand-8468"], marker=2, speaker="Haskell's footnote", text_layer="footnote citation",
          extras={"cross_reference_segments": [{"segment_id": P259, "source_line_start": 192, "source_line_end": 192}]})
statement("note3-visconti-letter-citation", NOTES, 391, 391, "cand-8466", None,
          "visconti_letter_to_ligari_published_by_arslan_1952_page_63",
          "Haskell's note 3 identifies a letter from Pietro Visconti to Gian Pietro Ligari, published by Arslan in 1952, page 63.",
          "Citation locator for the 1749 income quotation; neither the letter nor the publication was independently consulted.",
          ["cand-8465", "cand-1408", "cand-8467", "cand-8466"], marker=3,
          speaker="Haskell's footnote", text_layer="footnote citation",
          extras={"cross_reference_segments": [{"segment_id": P259, "source_line_start": 192, "source_line_end": 193}]})
statement("note4-pietro-will-inventory-location", NOTES, 392, 392, "cand-8469", "cand-8262",
          "pietro_foscarini_will_held_at_biblioteca_correr",
          "Haskell's note 4 says Pietro Foscarini's will is in Biblioteca Correr, Cod. Cicogna, MMDCCCCXLV-2686.",
          "Archival locator only; the document and shelfmark were not independently checked. The same call number is retained for the separately named picture inventory.",
          ["cand-8469", "cand-8470", "cand-1056", "cand-8262"], marker=4,
          speaker="Haskell's footnote", text_layer="footnote citation",
          extras={"cross_reference_segments": [{"segment_id": P259, "source_line_start": 193, "source_line_end": 193}]})
statement("note4-pietro-picture-inventory-location", NOTES, 392, 392, "cand-8470", "cand-8262",
          "pietro_foscarini_picture_inventory_held_at_biblioteca_correr",
          "Haskell's note 4 says the inventory of Pietro Foscarini's pictures is in Biblioteca Correr, Cod. Cicogna, MMDCCCCXLV-2686.",
          "Archival locator only; the inventory and shelfmark were not independently checked.",
          ["cand-8469", "cand-8470", "cand-1056", "cand-8262"], marker=4,
          speaker="Haskell's footnote", text_layer="footnote citation",
          extras={"cross_reference_segments": [{"segment_id": P259, "source_line_start": 193, "source_line_end": 193}]})
statement("note5-foscarini-library-transfer", NOTES, 393, 393, "cand-8462", "cand-8471",
          "descendants_sold_library_to_austrian_government_in_1800",
          "Haskell's note 5 says Marco Foscarini's descendants sold the library to the Austrian government in 1800.",
          "Reported transfer as stated in Haskell; no individual descendants or modern institutional identity is inferred. The scan corrects OCR 'die Austrian' to 'the Austrian'.",
          ["cand-8462", "cand-1057", "cand-8471"], marker=5,
          speaker="Haskell's footnote", text_layer="footnote citation",
          extras={"relation_candidate": True, "ocr_corrections": [{"source_line": 393, "ocr": "die Austrian", "print": "the Austrian", "basis": "CHP-9.pdf physical page 21."}],
                  "cross_reference_segments": [{"segment_id": P259, "source_line_start": 194, "source_line_end": 194}]})
statement("note5-library-current-location", NOTES, 393, 393, "cand-8462", "cand-8472",
          "foscarini_library_now_in_hofbibliothek_vienna",
          "Haskell's note 5 says the library is now in the Hofbibliothek, Vienna.",
          "Location as reported in Haskell; do not infer the current-day name or status of the institution.",
          ["cand-8462", "cand-8472", "cand-2772"], marker=5,
          speaker="Haskell's footnote", text_layer="footnote citation",
          extras={"relation_candidate": True,
                  "cross_reference_segments": [{"segment_id": P259, "source_line_start": 194, "source_line_end": 194}]})
statement("note6-kress-location", NOTES, 394, 394, "cand-4085", "cand-8473",
          "triumph_picture_located_at_kress_foundation_new_york",
          "Haskell's note 6 says the picture is at the Kress Foundation in New York.",
          "Repository as reported by Haskell, not independently verified. The front-matter Plate 45 entry separately names the North Carolina Museum of Art, Raleigh and Samuel H. Kress Collection; retain both source statements for later reconciliation.",
          ["cand-4085", "cand-8473", "cand-7473", "cand-4176", "cand-3672"], marker=6,
          speaker="Haskell's footnote", text_layer="footnote citation",
          extras={"relation_candidate": True, "cross_reference_segments": [{"segment_id": P259, "source_line_start": 195, "source_line_end": 195},
                                                                           {"segment_id": PLATES, "source_line_start": 123, "source_line_end": 123}]})
statement("note6-clark-citation", NOTES, 394, 394, None, "cand-8484",
          "citation_locator_clark_1959_pages_232_236_for_triumph",
          "Haskell's note 6 refers readers to A. Clark, 1959, pages 232–236, for a detailed discussion of the painting.",
          "Bibliographic locator only; title is not supplied and the cited pages were not independently consulted. The scan corrects OCR 'PP2Z2-6' to 'pp.232-6'.",
          ["cand-4085", "cand-8483", "cand-8484"], marker=6,
          speaker="Haskell's footnote", text_layer="footnote citation",
          extras={"cross_reference_segments": [{"segment_id": P259, "source_line_start": 195, "source_line_end": 195}],
                  "ocr_corrections": [{"source_line": 394, "ocr": "PP2Z2-6", "print": "pp.232-6", "basis": "CHP-9.pdf physical page 21."}]})

if len({r["mention_id"] for r in mentions + new_mentions}) != len(mentions) + len(new_mentions):
    raise SystemExit("mention IDs are not unique")
if len({r["statement_id"] for r in statements + new_statements}) != len(statements) + len(new_statements):
    raise SystemExit("statement IDs are not unique")

for cid, suggested_type, detail in [
    ("cand-1053", "person", "Haskell's p.258–259 account presents Marco Foscarini as a Venetian statesman and writer, covering family descent, education, embassy, historiography, library, patronage, Doge accession and political positions; these remain source-reported claims."),
    ("cand-1059", "place", "Indexed Foscarini family palace at the Carmini in Venice; Haskell p.259 locates it opposite the Church of the Carmini and reports repeated decoration. Exact architectural identity remains for later alignment."),
    ("cand-1057", "family", "Named as Marco Foscarini's family in Haskell's descent claim and as the source-reported owners/descendants in p.259; family relations are not externally verified here."),
]:
    matches = [r for r in candidates if r["candidate_id"] == cid]
    if len(matches) != 1:
        raise SystemExit(f"expected one candidate to update: {cid}")
    matches[0]["suggested_type"] = suggested_type
    matches[0]["detail"] = detail

prior = [r for r in statements if r.get("statement_id") == "st-chp9-p258-marco-strongest-stand-against-querini"]
if len(prior) != 1:
    raise SystemExit("expected p.258's split Angelo Querini statement")
prior[0]["qualifiers"]["qualification"] = "P.259 L189 closes the split name as Angelo Querini and refers to his proposed reforms in 1762; preserve the stated political opposition as an S2 relation candidate, not a formal relation."

coverage_by_id[P258].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L180-186",
    "note": "Printed p.258 (CHP-9.pdf physical p.20) reviewed against the scan. L186's first name Angelo is completed by p.259 L189 'Querini'; notes 1-3 were processed at consolidated L387-388.",
})
coverage_by_id[P259].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L189-200",
    "note": "Printed p.259 (CHP-9.pdf physical p.21) reviewed against the scan. L200 begins a sentence about Foscarini's other pictures that continues in p.260 L201; notes 1-6 are consolidated at L389-394. Keep the internal source discrepancy between the p.259 Kress Foundation note and Plate 45 location/collection caption for reconciliation.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L349-394; p.255 L155 continuation",
    "note": "Consolidated notes through p.259 notes 1-6 are processed at L349-394; p.255 note 1 continuation at L155 remains cross-linked to L370. Later notes from L395 remain queued; citations are locators, not independent verification.",
})

summary = {"segments": {sid: [coverage_by_id[sid]["disposition"], coverage_by_id[sid]["migration_status"],
                               coverage_by_id[sid]["source_line_ranges"]] for sid in (P258, P259, NOTES)},
           "new_candidates": len(candidate_specs), "new_mentions": len(new_mentions),
           "new_statements": len(new_statements), "source_hash": meta["sha256"],
           "next_body_segment": f"{P260}#L202 closes p.259 L200", "next_note_line": 395}
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
