"""Controlled S2 migration for printed p.257; defaults to a read-only dry run."""
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
P256 = "chp-9:09_CHP-9_intro:l157-165"
P257 = "chp-9:09_CHP-9_intro:l167-177"
P258 = "chp-9:09_CHP-9_intro:l179-186"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
EXPECTED_HASH = "57910b1c32121abe9cf27530e7548251827005fa067d300c430d902496245e2c"
EXPECTED_ASSET_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
BACKUP_SUFFIX = ".bak-s2-chp9-p257-20261001"


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
for sid in (P256, P257, P258, NOTES):
    if sid not in segment_by_id:
        raise SystemExit(f"missing source segment: {sid}")
meta = segment_by_id[P257]
if meta["sha256"] != EXPECTED_HASH or meta["asset_sha256"] != EXPECTED_ASSET_HASH:
    raise SystemExit("p.257 source segment or source asset fingerprint changed")
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


offsets_by_segment = {sid: line_offsets(sid) for sid in (P257, NOTES)}


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
    P256: ("reviewed", "partial", "L158-165"),
    P257: ("queued", "pending", ""),
    NOTES: ("reviewed", "partial", "L349-379; p.255 L155 continuation"),
}
for sid, expected in expected_states.items():
    row = coverage_by_id.get(sid)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != expected:
        raise SystemExit(f"unexpected coverage state for {sid}: {row}")

candidate_ids = {r["candidate_id"] for r in candidates}
if len(candidate_ids) != len(candidates) or max(int(x.split("-")[1]) for x in candidate_ids) != 8408:
    raise SystemExit("candidate inventory changed; inspect before allocating IDs")
candidate_specs = [
    (8409, "Nobles' competitions to provide the most expensive banquets", "procedure", P257, 168,
     "The memoir report introduced on p.256; the recurring practice is recorded as Haskell's report, not independently verified."),
    (8410, "Unidentified Tiepolo Banquet of Antony and Cleopatra version at Labia Palace", "work", P257, 168,
     "A particular version at the Labia palace described as Tiepolo's most magnificent; keep distinct from the recurring subject and alignments pending S3."),
    (8411, "Maria Labia's famous jewelry collection (individual objects unspecified)", "", P257, 168,
     "An aggregate collection of jewelry, not an identified artwork or named collection; retain without forcing a type."),
    (8412, "Cleopatra's pearl-wager narrative invoked in Haskell's account", "event", P257, 168,
     "Narrative used by Haskell to explain Maria Labia's identification with Cleopatra; no external historicity claim is made."),
    (8413, "French nobility as comparison group for Venetian nobles on p.257", "term", P257, 169,
     "Haskell's unnamed social comparison group; no particular persons are identified."),
    (8414, "French middle classes in Haskell's history-painting comparison", "term", P257, 170,
     "Collective social group as described by Haskell; no membership is inferred."),
    (8415, "David (surname form in the history-painting revival account)", "person", P257, 170,
     "Surname-only reference in Haskell's account; do not expand the identity at S2."),
    (8416, "Frenchmen concerned with reviving native history painting (unnamed group)", "term", P257, 171,
     "Unnamed group of Frenchmen described as interested in national history painting; membership is not inferred."),
    (8417, "Unnamed Director of the French Academy in Rome addressed in 1754", "person", P257, 171,
     "The letter names the institutional office, not its holder; retain as unidentified."),
    (8418, "Students sent to copy Tiepolo's frescoes at Villa Contarini-Pisani", "term", P257, 172,
     "Unnamed students in the Academy instruction; no number or individual identity is supplied."),
    (8419, "Villa Contarini-Pisani named as a Tiepolo fresco site", "place", P257, 173,
     "Place as named in Haskell's passage; no further architectural or ownership identity is added."),
    (8420, "Unspecified Tiepolo frescoes at Villa Contarini-Pisani", "work", P257, 172,
     "Specific frescoes identified only as copying targets at the villa; the passage does not name individual scenes."),
    (8421, "Bozzetti as preparatory sketches contrasted with full-scale decoration", "term", P257, 175,
     "Art-historical category in Haskell's evaluation; the source does not identify any particular sketch."),
    (8422, "Contemporary connoisseurs who may have preferred bozzetti (unnamed group)", "term", P257, 175,
     "Haskell's conjectural group; neither individuals nor a definite consensus are supplied."),
    (8423, "Exaggerated dignity in Venetian portraiture", "term", P257, 177,
     "Haskell's interpretive description of portraiture; retain as a concept, not a named work."),
    (8424, "Erotic and frivolous painting in the French rococo comparison", "term", P257, 177,
     "Painting category described by Haskell; no specific works are identified."),
    (8425, "1754 letter from Marquis de Vandières to the French Academy in Rome about copying Tiepolo frescoes", "archive", P257, 171,
     "Letter described and quoted by Haskell through Byam Shaw; neither the letter nor the cited publication was independently consulted."),
    (8426, "Antonio Longo, 1820, volume I, pages 81–90 (citation locator)", "archive", NOTES, 380,
     "Citation for the reported banquet competitions; title details are not supplied in this note."),
    (8427, "Tassini (surname-only citation form in p.257 note 2)", "person", NOTES, 381,
     "Retain the source's surname-only form; do not expand the given name."),
    (8428, "Tassini, 1915, page 335 (citation locator)", "archive", NOTES, 381,
     "Citation locator only; title and cited text are not supplied or independently consulted."),
    (8429, "De Brosses, volume I, page 149 (citation locator)", "archive", NOTES, 382,
     "Citation locator for the report concerning Maria Labia; not independently consulted."),
    (8430, "T. M. Marcellino (source form in p.257 note 4)", "person", NOTES, 383,
     "Name as printed in the citation; no further identity is inferred."),
    (8431, "Marcellino, page 18, note 32 (citation locator)", "archive", NOTES, 383,
     "Citation locator for the quoted description of Maria Labia; publication title is not supplied."),
    (8432, "Byam Shaw (surname citation form in p.257 note 5)", "person", NOTES, 384,
     "Retain the source's citation form; no given name is inferred."),
    (8433, "Byam Shaw, 1960, page 530 (citation locator)", "archive", NOTES, 384,
     "Citation locator for the Vandières letter quotation; page image confirms 1960 and printed note 5."),
    (8434, "Villot (surname-only citation form in p.257 note 6)", "person", NOTES, 385,
     "Retain the source's citation form; no given name is inferred."),
    (8435, "Villot, pages 169–176 (citation locator)", "archive", NOTES, 385,
     "Citation locator only; title and cited text are not supplied or independently consulted."),
    (8436, "Levey, 1959, relevant chapter (citation locator)", "archive", NOTES, 386,
     "Haskell refers readers to a relevant chapter without title or page range; citation not independently checked."),
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
    mid = f"m-chp9-p257-{suffix}"
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
    (P257, 168, "nobles-banquet-competition", "cand-8108", "nobles", "Venetian nobles in the preceding context."),
    (P257, 168, "banquet-competition", "cand-8409", "competitions as to who could offer the most expensive banquets", "Report attributed by Haskell to Antonio Longo; citation is note 1."),
    (P257, 168, "labia-family", "cand-1349", "the Labia", "Labia family in the Venice patronage context."),
    (P257, 168, "labia-palace", "cand-8201", "whose palace", "Palace of the Labia family; index candidate reused."),
    (P257, 168, "tiepolo-banquet-version", "cand-8410", "Tiepolo’s most magnificent version of the subject", "Specific Labia Palace version; keep distinct from the generic recurring motif pending S3."),
    (P257, 168, "banquet-subject", "cand-2577", "the subject", "Anaphoric reference to the indexed Banquet of Cleopatra subject."),
    (P257, 168, "labia-extravagance", "cand-1349", "their extravagance", "Anaphoric reference to the Labia family."),
    (P257, 168, "maria-labia", "cand-1350", "Maria Labia", "Existing index person candidate reused."),
    (P257, 168, "labia-doyenne", "cand-1349", "the family", "Labia family named in Maria's role description."),
    (P257, 168, "labia-jewelry-collection", "cand-8411", "famous collection of jewelry", "Unnamed aggregate collection; no individual items identified."),
    (P257, 168, "tiepolo-compliment-person", "cand-2569", "Tiepolo", "Second occurrence on the line, in Haskell's statement about artistic intention.", 168, 1),
    (P257, 168, "cleopatra-queen", "cand-4157", "beautiful Egyptian queen", "Cleopatra by the preceding Banquet context; candidate identity retained for S3."),
    (P257, 168, "cleopatra-pearl-wager", "cand-8412", "her wager by dissolving a priceless pearl in wine", "Narrative allusion in Haskell's interpretation."),
    (P257, 169, "venetian-nobles-state-power", "cand-8108", "Venetian nobles", "Haskell's account of the Venetian ruling estate."),
    (P257, 169, "french-equivalents", "cand-8413", "their equivalents in France", "Unnamed French noble comparison group."),
    (P257, 169, "venetian-state-power", "cand-8105", "the State", "Political entity in the claim about state power; do not conflate with Venice as place."),
    (P257, 169, "history-painting", "cand-6179", "history painting", "History painting as a genre; existing source-level term candidate reused."),
    (P257, 169, "venice-place", "cand-2719", "in Venice", "Venice as a place where history painting remained active."),
    (P257, 169, "europe-place", "cand-3462", "throughout Europe", "Geographic comparison in Haskell's claim."),
    (P257, 170, "paolo-renier", "cand-2133", "Paolo Renier", "Existing indexed person candidate reused."),
    (P257, 170, "free-republic", "cand-8105", "a free Republic", "Venetian political entity as the quotation's context."),
    (P257, 170, "french-middle-classes", "cand-8414", "French middle classes", "Collective social group as described by Haskell."),
    (P257, 170, "history-painting-revival", "cand-6179", "revival of history painting", "Same genre concept as line 169."),
    (P257, 170, "david-surname", "cand-8415", "David", "Surname-only form; identity not expanded at S2."),
    (P257, 170, "aristocracy", "cand-8108", "the aristocracy", "Venetian aristocratic group in Haskell's comparison."),
    (P257, 170, "tiepolo-champion", "cand-2569", "Tiepolo", "Tiepolo described as the champion of the cause."),
    (P257, 170, "tiepolo-french-admirers", "cand-2569", "Tiepolo", "Second occurrence on the line, in the statement that French history-painting advocates admired him.", 170, 1),
    (P257, 170, "frenchmen-history-revival", "cand-8416", "those Frenchmen", "Unnamed group interested in native history painting."),
    (P257, 170, "native-history-painting", "cand-6179", "native history painting", "History painting as a genre in the French revival clause."),
    (P257, 171, "vandieres-marigny", "cand-2692", "Marquis de Vandières (later Marquis de Marigny)", "Parenthetical alias is explicit in the source; existing index candidate reused."),
    (P257, 171, "academy-director", "cand-8417", "the Director", "Unnamed holder of the French Academy office.", 172),
    (P257, 171, "french-academy", "cand-1081", "French\nAcademy in Rome", "Institution name crosses an OCR line boundary.", 172),
    (P257, 172, "academy-students", "cand-8418", "students", "Unnamed students instructed to copy the frescoes."),
    (P257, 172, "tiepolo-frescoes", "cand-8420", "the artist’s frescoes", "Specific unnamed works at the named villa."),
    (P257, 173, "contarini-pisani-villa", "cand-8419", "Villa Contarini-Pisani", "Place named as the copying site."),
    (P257, 173, "france-in-quoted-letter", "cand-5317", "l’histoire de France", "Country named in the French quotation from Vandières's reported letter."),
    (P257, 174, "cochin", "cand-0793", "Cochin", "Existing indexed person candidate reused."),
    (P257, 174, "tiepolo-cochin-praise", "cand-2569", "Tiepolo", "Artist praised by Cochin as reported by Haskell."),
    (P257, 175, "bozzetti", "cand-8421", "bozzetti", "Source term for preparatory sketches; no particular sketch identified."),
    (P257, 175, "rococo", "cand-6555", "‘rococo’ art", "Existing term candidate for French rococo reused."),
    (P257, 175, "fragonard-first", "cand-1063", "Fragonard", "Jean Honoré Fragonard; index candidate reused."),
    (P257, 175, "connoisseurs", "cand-8422", "some connoisseurs of the time", "Unnamed group in Haskell's conjecture."),
    (P257, 175, "tiepolo-full-scale", "cand-2569", "Tiepolo’s full-scale decorations", "Anaphoric reference to Tiepolo's decoration practice."),
    (P257, 176, "tiepolo-moral-commitment", "cand-2569", "Tiepolo’s marvellous colour and fantasy", "Artist and qualities named in Haskell's interpretive comparison."),
    (P257, 176, "rubens", "cand-2293", "Rubens", "Existing indexed person candidate reused."),
    (P257, 177, "venetian-nobility-portraiture", "cand-8108", "Venetian nobility", "Venetian aristocratic group in Haskell's causal interpretation."),
    (P257, 177, "portraiture", "cand-8423", "their portraiture", "Portraiture treated as a genre/category."),
    (P257, 177, "erotic-frivolous-painting", "cand-8424", "erotic and frivolous painting", "Generic category in Haskell's comparison."),
    (P257, 177, "french-rococo", "cand-6555", "French rococo", "Existing style candidate reused."),
    (P257, 177, "boucher", "cand-0421", "Boucher", "Existing indexed person candidate reused."),
    (P257, 177, "fragonard-second", "cand-1063", "Fragonard", "Jean Honoré Fragonard, named in the final comparison."),
    (NOTES, 380, "longo-author", "cand-1435", "Antonio Longo", "Existing index candidate reused as the cited memoir author."),
    (NOTES, 380, "longo-memoir-citation", "cand-8426", "Antonio Longo, 1820,1, pp. 81-90", "Raw citation surface; page scan confirms volume I and punctuation."),
    (NOTES, 381, "tassini-author", "cand-8427", "Tassini", "Surname-only citation form."),
    (NOTES, 381, "tassini-citation", "cand-8428", "Tassini, 1915, p. 335", "Bibliographic locator as printed."),
    (NOTES, 382, "de-brosses-author", "cand-0455", "De Brosses", "Existing index person candidate reused."),
    (NOTES, 382, "de-brosses-citation", "cand-8429", "De Brosses, I, p. 149", "Citation locator as printed."),
    (NOTES, 383, "marcellino-author", "cand-8430", "T. M. Marcellino", "Source form in note 4."),
    (NOTES, 383, "marcellino-citation", "cand-8431", "p. 18, note 32", "Citation locator for the quoted description."),
    (NOTES, 384, "byam-shaw-author", "cand-8432", "Byam Shaw", "Surname citation form; printed note number is 5 although OCR says 6."),
    (NOTES, 384, "byam-shaw-citation", "cand-8433", "i960, p. 530", "Raw OCR citation; page scan reads 1960, p. 530."),
    (NOTES, 385, "villot-author", "cand-8434", "Villot", "Surname-only citation form."),
    (NOTES, 385, "villot-citation", "cand-8435", "Villot, pp. 169-76", "Raw citation range; page scan confirms the locator."),
    (NOTES, 386, "levey-author", "cand-3843", "Levey", "Existing Levey person candidate reused; identity alignment remains for S3."),
    (NOTES, 386, "levey-citation", "cand-8436", "Levey, 1959", "Citation locator as printed; the referenced chapter is not specified."),
]
for spec in MENTION_SPECS:
    mention(*spec)

new_statements = []
existing_statement_ids = {r["statement_id"] for r in statements}


def statement(suffix, segment_id, first, last, subject, obj, predicate, claim, qualification,
              mentioned, marker=None, speaker="Haskell", text_layer="body", extras=None):
    sid = f"st-chp9-p257-{suffix}"
    if sid in existing_statement_ids or any(r["statement_id"] == sid for r in new_statements):
        raise SystemExit(f"duplicate statement ID: {sid}")
    m = segment_by_id[segment_id]
    if first < m["line_start"] or last > m["line_end"]:
        raise SystemExit(f"statement lines outside segment {segment_id}: {sid}")
    if any(cid and cid not in candidate_ids for cid in [subject, obj, *mentioned]):
        raise SystemExit(f"missing candidate in statement: {sid}")
    q = {"source_line_start": first, "source_line_end": last, "printed_page": 257,
         "pdf_physical_page": 19, "claim": claim, "speaker": speaker, "text_layer": text_layer,
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


statement("longo-banquet-competitions", P257, 168, 168, "cand-8108", "cand-8409",
          "nobles_competed_to_offer_the_most_expensive_banquets",
          "Haskell reports from Antonio Longo's memoirs that nobles used to organise competitions to offer the most expensive banquets.",
          "This completes the introduction to Longo at p.256 L165. It is a report mediated by Haskell; Longo's memoirs were not independently consulted.",
          ["cand-8108", "cand-8409", "cand-1435", "cand-8426"], marker=1,
          extras={"cross_reference_segments": [{"segment_id": P256, "source_line_start": 165, "source_line_end": 165},
                                                 {"segment_id": NOTES, "source_line_start": 380, "source_line_end": 380}]})
statement("labia-palace-banquet-version", P257, 168, 168, "cand-8201", "cand-8410",
          "contained_tiepolo_version_of_banquet_subject",
          "Haskell says the Labia palace contained Tiepolo's most magnificent version of the Banquet subject.",
          "The passage does not identify an individual surviving fresco or supply independent object verification; keep this specific version distinct from the generic subject candidate pending S3.",
          ["cand-8201", "cand-1349", "cand-2569", "cand-2577", "cand-8410", "cand-8427", "cand-8428"], marker=2,
          extras={"relation_candidate": True, "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 381, "source_line_end": 381}]})
statement("labia-extravagance-reputation", P257, 168, 168, "cand-1349", None,
          "became_legendary_for_extravagance",
          "Haskell says the Labia family became legendary for its extravagance.",
          "This is Haskell's characterization, not a separately measured wealth claim; note 2 is the cited locator.",
          ["cand-1349", "cand-8201", "cand-8427", "cand-8428"], marker=2,
          extras={"cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 381, "source_line_end": 381}]})
statement("maria-labia-doyenne-and-description", P257, 168, 168, "cand-1350", "cand-1349",
          "described_as_family_doyenne_and_femme_sur_le_retour",
          "Haskell identifies Maria Labia as the family's doyenne and reproduces a French description of her as a woman on the decline who had once been very beautiful and gallant.",
          "Keep the French wording as a quoted characterization; it is not an independently verified biographical assessment.",
          ["cand-1350", "cand-1349", "cand-0455", "cand-8429"], marker=3,
          extras={"relation_candidate": True, "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 382, "source_line_end": 382}]})
statement("maria-labia-jewelry-collection", P257, 168, 168, "cand-1350", "cand-8411",
          "owned_famous_jewelry_collection_and_was_proud_of_it",
          "Haskell says Maria Labia owned a famous jewelry collection of which she was especially proud.",
          "The individual pieces and collection identity are not supplied; the cited De Brosses locator was not independently consulted.",
          ["cand-1350", "cand-8411", "cand-0455", "cand-8429"], marker=3,
          extras={"relation_candidate": True, "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 382, "source_line_end": 382}]})
statement("tiepolo-delicate-compliment-to-maria", P257, 168, 168, "cand-2569", "cand-1350",
          "intended_delicate_compliment_to_maria_labia",
          "Haskell says Tiepolo intended a delicate compliment to Maria Labia.",
          "Preserve Haskell's 'There can be little doubt' as an authorial inference about artistic intention, not direct testimony from Tiepolo.",
          ["cand-2569", "cand-1350", "cand-8410"])
statement("maria-labia-identifies-with-cleopatra", P257, 168, 168, "cand-1350", "cand-4157",
          "identified_with_cleopatra_in_the_banquet_subject",
          "Haskell says Maria Labia had little difficulty identifying herself with Cleopatra in the Banquet subject and its pearl-wager story.",
          "This is Haskell's interpretation of a delicate compliment; do not convert it into a documented self-identification by Maria.",
          ["cand-1350", "cand-4157", "cand-8412", "cand-8410"])
statement("venetian-nobles-retained-state-power", P257, 169, 169, "cand-8108", "cand-8105",
          "venetian_nobles_still_held_real_state_power_unlike_french_equivalents",
          "Haskell says Venetian nobles remained acutely aware that, unlike their French equivalents, they still represented the only real power in the State.",
          "This is Haskell's social-political generalization; France and the Venetian State are recorded in their distinct contexts.",
          ["cand-8108", "cand-8413", "cand-5317", "cand-8105"], extras={"relation_candidate": True})
statement("history-painting-kept-alive-in-venice", P257, 169, 169, "cand-8108", "cand-6179",
          "nobles_awareness_kept_history_painting_alive_in_venice",
          "Haskell links Venetian nobles' dreams of power and awareness of state power to the continuation of history painting in Venice while its expressive force and importance declined elsewhere in Europe.",
          "Preserve this as Haskell's broad explanatory argument, not a quantified comparison.",
          ["cand-8108", "cand-6179", "cand-2719", "cand-3462", "cand-8105"],
          extras={"ocr_corrections": [{"line": 169, "ocr": "ahve", "reading": "alive", "basis": "CHP-9.pdf physical p.19"}]})
statement("renier-free-republic-quote", P257, 170, 170, "cand-2133", "cand-8105",
          "contrasted_subject_service_with_free_republican_participation",
          "Haskell quotes Paolo Renier in 1772 contrasting a minister serving his Prince as a subject with a person granted the privilege of living in a free Republic and being an essential part of the whole.",
          "Attributed quotation mediated by Haskell; preserve Renier's date and wording, and do not treat the translated quotation as an independently consulted original.",
          ["cand-2133", "cand-8105", "cand-8430", "cand-8431"], marker=4, speaker="Paolo Renier as quoted by Haskell",
          extras={"cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 383, "source_line_end": 383}]})
statement("french-middle-class-history-painting-revival", P257, 170, 170, "cand-8414", "cand-6179",
          "moral_fervour_led_to_history_painting_revival_and_david",
          "Haskell says some of the French middle classes' moral fervour led to a revival of history painting culminating in David's rhetoric.",
          "Keep the collective attribution and surname-only David form; this is Haskell's retrospective account.",
          ["cand-8414", "cand-6179", "cand-8415", "cand-3462"])
statement("venetian-aristocracy-and-tiepolo-as-champion", P257, 170, 170, "cand-8108", "cand-2569",
          "moral_fervour_expressed_by_aristocracy_and_championed_by_tiepolo",
          "Haskell says a comparable moral fervour was expressed by the Venetian aristocracy and found its champion in Tiepolo, though with wholly different results in elegance, colour and subject matter.",
          "This is Haskell's comparison; do not equate the French and Venetian outcomes.",
          ["cand-8108", "cand-2569", "cand-8414", "cand-6179"])
statement("french-history-painters-admired-tiepolo", P257, 170, 170, "cand-8416", "cand-2569",
          "french_revival_advocates_were_keen_admirers_of_tiepolo",
          "Haskell says Frenchmen especially concerned to revive native history painting in the mid-eighteenth century were keen admirers of Tiepolo.",
          "The group is unnamed; the following Vandières and Cochin examples are recorded separately.",
          ["cand-8416", "cand-6179", "cand-2569"])
statement("vandieres-1754-letter-copies-tiepolo-frescoes", P257, 171, 173, "cand-2692", "cand-8420",
          "instructed_academy_director_to_send_students_to_copy_tiepolo_frescoes",
          "Haskell says the Marquis de Vandières, later Marquis de Marigny, wrote to the Director of the French Academy in Rome in 1754 instructing him to send students to copy Tiepolo's frescoes at Villa Contarini-Pisani.",
          "A specific letter is described, but only through the cited page in Byam Shaw; the original correspondence and cited book were not independently consulted.",
          ["cand-2692", "cand-8417", "cand-1081", "cand-8418", "cand-2569", "cand-8420", "cand-8419", "cand-8425", "cand-8433"],
          marker=5, extras={"relation_candidate": True, "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 384, "source_line_end": 384}]})
statement("vandieres-french-history-painting-purpose", P257, 173, 173, "cand-2692", "cand-6179",
          "copying_frescoes_would_support_french_history_painting",
          "In Haskell's quotation, Vandières says that copying the frescoes would produce another good result for the history of France by providing customs and clothing of those times.",
          "Retain this as the letter's purpose as quoted in French by Haskell; the letter and Byam Shaw citation were not independently checked.",
          ["cand-2692", "cand-6179", "cand-5317", "cand-8420", "cand-8433"], marker=5,
          speaker="Marquis de Vandières as quoted by Haskell",
          extras={"cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 384, "source_line_end": 384}]})
statement("cochin-also-admired-tiepolo", P257, 174, 174, "cand-0793", "cand-2569",
          "cochin_also_thought_highly_of_tiepolo",
          "Haskell says Cochin, who shared the interest in history painting, also thought very highly of Tiepolo.",
          "This is Haskell's report; note 6 supplies only the Villot citation locator, not an independently consulted Cochin text.",
          ["cand-0793", "cand-2569", "cand-8434", "cand-8435"], marker=6,
          extras={"cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 385, "source_line_end": 385}]})
statement("present-day-taste-prefers-bozzetti", P257, 175, 175, None, "cand-8421",
          "present_taste_prefers_bozzetti_and_misses_full_scale_grandeur",
          "Haskell says present-day taste finds Tiepolo's bozzetti more appealing and, attracted by rococo glamour, misses the grandeur and megalomania of his full-scale decorations.",
          "This is Haskell's criticism of modern taste; the source does not identify specific sketches or decorations.",
          ["cand-2569", "cand-8421", "cand-6555"])
statement("fragonard-connoisseurs-may-share-distinction", P257, 175, 175, "cand-1063", "cand-8422",
          "fragonard_and_connoisseurs_may_have_shared_bozzetti_preference",
          "Haskell says there is reason to believe painters like Fragonard and some connoisseurs of the time may have made the same distinction between bozzetti and full-scale decoration.",
          "Preserve 'reason to believe' and 'may have'; no individual connoisseur is identified.",
          ["cand-1063", "cand-8422", "cand-8421", "cand-2569"])
statement("tiepolo-moral-commitment-compared-to-rubens", P257, 176, 176, "cand-2569", "cand-2293",
          "admiration_should_not_obscure_tiepolo_moral_commitment_as_with_rubens",
          "Haskell says admiration for Tiepolo's colour and fantasy should not blind readers to his moral commitment to the cause he served, just as in Rubens's case.",
          "This is Haskell's evaluative analogy; the cause is not specified further in the sentence.",
          ["cand-2569", "cand-2293"])
statement("nobility-awareness-and-portraiture-dignity", P257, 177, 177, "cand-8108", "cand-8423",
          "awareness_of_privileges_and_obligations_probably_shaped_portraiture_dignity",
          "Haskell says it was probably Venetian nobility's awareness of real privileges and obligations that caused the exaggerated dignity of their portraiture.",
          "Preserve the author's 'probably'; this is a proposed explanation, not an established causal finding.",
          ["cand-8108", "cand-8423", "cand-3843"], marker=7,
          extras={"cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 386, "source_line_end": 386}]})
statement("venetian-erotic-painting-comparison", P257, 177, 177, "cand-8108", "cand-8424",
          "awareness_probably_responsible_for_small_amount_of_french_rococo_erotic_painting",
          "Haskell says it was probably Venetian nobility's awareness of their privileges and obligations that was responsible for the surprisingly small amount of erotic and frivolous painting typical of French rococo.",
          "Retain the author's 'probably' and the qualitative comparison; no corpus or quantitative measure is supplied.",
          ["cand-8108", "cand-8424", "cand-6555"])
statement("no-venetian-equivalent-to-boucher-fragonard", P257, 177, 177, "cand-8108", None,
          "no_venetian_equivalent_to_boucher_or_fragonard",
          "Haskell says there was no Venetian equivalent to Boucher or Fragonard.",
          "The printed sentence ends with 'and' and continues at p.258 L180; this clause is recorded, but the source segment remains partial until the continuation is processed.",
          ["cand-8108", "cand-0421", "cand-1063"], extras={"cross_reference_segments": [{"segment_id": P258, "source_line_start": 180, "source_line_end": 180}]})

statement("note1-longo-memoirs-citation", NOTES, 380, 380, "cand-1435", "cand-8426",
          "citation_locator_longo_1820_volume_one_pages_81_to_90",
          "Haskell's note 1 cites Antonio Longo, 1820, volume I, pages 81–90, for the banquet-competition report.",
          "Citation locator only; no title or independently consulted source is supplied.",
          ["cand-1435", "cand-8426"], marker=1, speaker="Haskell's footnote", text_layer="footnote citation",
          extras={"ocr_corrections": [{"line": 380, "ocr": "1820,1", "reading": "1820, I", "basis": "CHP-9.pdf physical p.19"}],
                  "cross_reference_segments": [{"segment_id": P257, "source_line_start": 168, "source_line_end": 168}]})
statement("note2-tassini-citation", NOTES, 381, 381, None, "cand-8428",
          "citation_locator_tassini_1915_page_335",
          "Haskell's note 2 cites Tassini, 1915, page 335, for the Labia palace's Banquet subject.",
          "Citation locator only; publication details and cited page were not independently checked.",
          ["cand-8427", "cand-8428", "cand-8201", "cand-8410"], marker=2, speaker="Haskell's footnote", text_layer="footnote citation",
          extras={"cross_reference_segments": [{"segment_id": P257, "source_line_start": 168, "source_line_end": 168}]})
statement("note3-de-brosses-citation", NOTES, 382, 382, "cand-0455", "cand-8429",
          "citation_locator_de_brosses_volume_one_page_149",
          "Haskell's note 3 cites De Brosses, volume I, page 149, in connection with Maria Labia's jewelry collection.",
          "Citation locator only; the cited text was not independently consulted.",
          ["cand-0455", "cand-8429", "cand-1350", "cand-8411"], marker=3, speaker="Haskell's footnote", text_layer="footnote citation",
          extras={"cross_reference_segments": [{"segment_id": P257, "source_line_start": 168, "source_line_end": 168}]})
statement("note4-marcellino-citation", NOTES, 383, 383, None, "cand-8431",
          "citation_locator_marcellino_page_18_note_32",
          "Haskell's note 4 attributes the quoted description to T. M. Marcellino, page 18, note 32.",
          "Citation locator only; title and cited text were not independently consulted.",
          ["cand-8430", "cand-8431", "cand-1350"], marker=4, speaker="Haskell's footnote", text_layer="footnote citation",
          extras={"cross_reference_segments": [{"segment_id": P257, "source_line_start": 168, "source_line_end": 168}]})
statement("note5-byam-shaw-citation", NOTES, 384, 384, "cand-8432", "cand-8433",
          "citation_locator_byam_shaw_1960_page_530",
          "Haskell's printed note 5 cites Byam Shaw, 1960, page 530, for the Vandières letter quotation.",
          "The OCR gives note marker 6 and year 'i960'; the scan reads printed note 5 and 1960. The cited publication was not independently consulted.",
          ["cand-8432", "cand-8433", "cand-2692", "cand-8425"], marker=5, speaker="Haskell's footnote", text_layer="footnote citation",
          extras={"ocr_corrections": [{"line": 384, "ocr": "6 Byam Shaw, i960", "reading": "5 Byam Shaw, 1960", "basis": "CHP-9.pdf physical p.19"}],
                  "cross_reference_segments": [{"segment_id": P257, "source_line_start": 171, "source_line_end": 173}]})
statement("note6-villot-citation", NOTES, 385, 385, None, "cand-8435",
          "citation_locator_villot_pages_169_to_176",
          "Haskell's note 6 cites Villot, pages 169–176, for the Cochin reference.",
          "Citation locator only; title and cited pages were not independently consulted.",
          ["cand-8434", "cand-8435", "cand-0793"], marker=6, speaker="Haskell's footnote", text_layer="footnote citation",
          extras={"cross_reference_segments": [{"segment_id": P257, "source_line_start": 174, "source_line_end": 174}]})
statement("note7-levey-citation", NOTES, 386, 386, None, "cand-8436",
          "citation_locator_levey_1959_relevant_chapter",
          "Haskell's note 7 directs readers to the relevant chapter in Levey, 1959.",
          "No chapter title or pages are supplied; the citation was not independently checked.",
          ["cand-3843", "cand-8436", "cand-8108", "cand-0421", "cand-1063"], marker=7, speaker="Haskell's footnote", text_layer="footnote citation",
          extras={"cross_reference_segments": [{"segment_id": P257, "source_line_start": 177, "source_line_end": 177}]})

if len({r["mention_id"] for r in mentions + new_mentions}) != len(mentions) + len(new_mentions):
    raise SystemExit("mention IDs are not unique")
if len({r["statement_id"] for r in statements + new_statements}) != len(statements) + len(new_statements):
    raise SystemExit("statement IDs are not unique")

longo = [r for r in candidates if r["candidate_id"] == "cand-1435"]
if len(longo) != 1:
    raise SystemExit(f"expected one Antonio Longo candidate, found {len(longo)}")
longo[0]["detail"] = "Named in Haskell's p.256–257 passage as the memoir author whose report is cited for Venetian nobles' banquet competitions; the memoirs are recorded as a citation locator, not independently consulted."

coverage_by_id[P256].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L158-165",
    "note": "Printed p.256 (CHP-9.pdf physical p.18) reviewed against the scan. The unfinished Antonio Longo introduction at L165 closes in p.257 L168. Notes 1-7 for p.256 are processed through consolidated L379.",
})
coverage_by_id[P257].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L168-177",
    "note": "Printed p.257 (CHP-9.pdf physical p.19) reviewed against the scan. L168 closes p.256 L165; L177 ends with 'and' and continues at p.258 L180, so retain partial. Printed notes 1-7 are consolidated at L380-386.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L349-386; p.255 L155 continuation",
    "note": "Consolidated notes through p.257 notes 1-7 are processed at L349-386; p.255 note 1 continuation at L155 remains cross-linked to L370. Later notes from L387 remain queued; citation locators are not independent verification.",
})

summary = {"segments": {sid: [coverage_by_id[sid]["disposition"], coverage_by_id[sid]["migration_status"],
                               coverage_by_id[sid]["source_line_ranges"]] for sid in (P256, P257, NOTES)},
           "new_candidates": len(candidate_specs), "new_mentions": len(new_mentions),
           "new_statements": len(new_statements), "source_hash": meta["sha256"],
           "next_body_segment": f"{P258}#L180 closes p.257 L177"}
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
