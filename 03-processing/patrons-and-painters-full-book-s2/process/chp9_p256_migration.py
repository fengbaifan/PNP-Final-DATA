"""Controlled S2 migration for printed p.256; defaults to a read-only dry run."""
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
P255 = "chp-9:09_CHP-9_intro:l148-155"
P256 = "chp-9:09_CHP-9_intro:l157-165"
P257 = "chp-9:09_CHP-9_intro:l167-177"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
EXPECTED_HASH = "2962dfdf9f25c1a0a8e2fa89b192fe3d26b5118a976e05a05f8812fa1bdf6c50"
EXPECTED_ASSET_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
BACKUP_SUFFIX = ".bak-s2-chp9-p256-20261001"


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
for sid in (P255, P256, P257, NOTES):
    if sid not in segment_by_id:
        raise SystemExit(f"missing source segment: {sid}")
meta = segment_by_id[P256]
if meta["sha256"] != EXPECTED_HASH or meta["asset_sha256"] != EXPECTED_ASSET_HASH:
    raise SystemExit("p.256 source segment or source asset fingerprint changed")
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


offsets_by_segment = {sid: line_offsets(sid) for sid in (P256, NOTES)}


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
    P255: ("reviewed", "partial", "L149-155"),
    P256: ("queued", "pending", ""),
    NOTES: ("reviewed", "partial", "L349-373; p.255 L155 continuation"),
}
for sid, expected in expected_states.items():
    row = coverage_by_id.get(sid)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != expected:
        raise SystemExit(f"unexpected coverage state for {sid}: {row}")

candidate_ids = {r["candidate_id"] for r in candidates}
if len(candidate_ids) != len(candidates) or max(int(x.split("-")[1]) for x in candidate_ids) != 8371:
    raise SystemExit("candidate inventory changed; inspect before allocating IDs")
candidate_specs = [
    (8372, "Lucrative legal profession linked to the Sandi family's fortunes", "term", P256, 158,
     "Haskell links the family's fortunes to law; this is a social-economic category, not an identified institution."),
    (8373, "Non-noble patrons who had the opportunity to employ Tiepolo (unnamed group)", "term", P256, 158,
     "A very small, unnamed social group in Haskell's comparison; no membership is inferred."),
    (8374, "Unidentified wife of Carlo Cordellina", "person", P256, 160,
     "Named only through her marital role; no name or further identity is supplied."),
    (8375, "Unidentified Carlo Cordellina house in Vicenza", "place", P256, 160,
     "One of two houses Haskell says Cordellina built; exact building identity is not supplied."),
    (8376, "Unidentified Carlo Cordellina country house at Montecchio", "place", P256, 160,
     "The latter of two houses Cordellina built and the venue for Tiepolo's decoration; exact building identity is not supplied."),
    (8377, "Montecchio, locality of Cordellina's country house", "place", P256, 160,
     "Locality as named in the source; no modern jurisdiction is inferred."),
    (8378, "G. B. Fontanella (bracketed source reference in Haskell's note)", "person", NOTES, 376,
     "The name is bracketed in the printed footnote; identity, role and cited work remain unspecified."),
    (8379, "Letter from Giambattista Tiepolo to Francesco Algarotti, 26 October 1743", "archive", NOTES, 377,
     "Specific letter as cited by Haskell through Fogolari; the letter and publication were not independently consulted."),
    (8380, "Fogolari (surname form in p.256 note 5)", "person", NOTES, 377,
     "Retain the source's surname-only form; do not expand the given name from other candidates at S2."),
    (8381, "Fogolari 1942 publication, page 34 (title unspecified)", "archive", NOTES, 377,
     "Publication locator for the Tiepolo letter; bibliographic title is not supplied in this note."),
    (8382, "La Rappresentanza del vero merito (oration for Pietro Loredan, Venice, 1724)", "archive", NOTES, 378,
     "Printed oration as identified by Haskell's note; corrected title and role spellings are recorded only in S2."),
    (8383, "Orazione on Antonio Loredan's departure from Padua (title and date as cited)", "archive", NOTES, 379,
     "Printed oration cited without a publication year; the text was not independently consulted."),
    (8384, "Mucius Scaevola (source form in the Loredan oration account)", "person", P256, 164,
     "Roman hero named as the orator's comparison; no expanded identity or external claim is added."),
    (8385, "Pompey (source form in the Antonio Loredan comparison)", "person", P256, 164,
     "Roman figure used in Haskell's report; no more specific identity is inferred at S2."),
    (8386, "Loredan family named in the Antonio Loredan passage", "family", P256, 164,
     "Family membership is stated by Haskell; no wider genealogy is inferred."),
    (8387, "Scipio named in Tiepolo's Continence of Scipio", "person", P256, 160,
     "Named figure in the work title; distinguish the represented subject from other Scipio candidates pending S3."),
    (8388, "Darius named in the Family of Darius before Alexander the Great", "person", P256, 160,
     "Named figure in the work title; no expanded identity is asserted at S2."),
    (8389, "Alexander the Great named in the Family of Darius before Alexander the Great", "person", P256, 160,
     "Named figure in the work title; identity alignment is deferred to S3."),
    (8390, "Amphion in the Sandi ceiling story", "person", NOTES, 375,
     "Named mythological figure in a story listed by Haskell's note; retain the source-level candidate."),
    (8391, "Thebes named in the Amphion story", "place", NOTES, 375,
     "Mythological city named in the cited subject description; no historical site is asserted."),
    (8392, "Cecrops in the Sandi ceiling story", "person", NOTES, 375,
     "Named mythological figure in a story listed by Haskell's note; retain the source-level candidate."),
    (8393, "Orpheus in the Sandi ceiling story", "person", NOTES, 375,
     "Named mythological figure in a story listed by Haskell's note; retain the source-level candidate."),
    (8394, "Eurydice in the Sandi ceiling story", "person", NOTES, 375,
     "Named mythological figure in a story listed by Haskell's note; retain the source-level candidate."),
    (8395, "Perseus in the Sandi ceiling story", "person", NOTES, 375,
     "Named mythological figure in a story listed by Haskell's note; retain the source-level candidate."),
    (8396, "Pegasus named as Perseus's mount in the Sandi ceiling story", "", NOTES, 375,
     "Named mythological creature; leave type unset because the current taxonomy has no animal type."),
    (8397, "Amphion building the walls of Thebes with his song", "event", NOTES, 375,
     "One of four subjects listed for the Powers of Eloquence ceiling; the cited Morassi pages were not independently read."),
    (8398, "Hercules with the chained Cecrops", "event", NOTES, 375,
     "One of four subjects listed for the Powers of Eloquence ceiling; retain the exact source description."),
    (8399, "Orpheus claiming Eurydice", "event", NOTES, 375,
     "One of four subjects listed for the Powers of Eloquence ceiling; retain the exact source description."),
    (8400, "Perseus on Pegasus slaying the Sea Monster", "event", NOTES, 375,
     "One of four subjects listed for the Powers of Eloquence ceiling; the monster is unnamed."),
    (8401, "Antony in the Banquet of Antony and Cleopatra subject", "person", P256, 164,
     "Preserve the source spelling 'Antony'; align with other title forms only at S3."),
    (8402, "Greek and Roman narrative repertory used for aristocratic virtues", "term", P256, 162,
     "Haskell's account of classical subjects codified for the display of aristocratic virtues."),
    (8403, "Sacrifice as a popular history-painting theme", "term", P256, 164,
     "Haskell's general claim about the theme's popularity and political meaning."),
    (8404, "New theories of political economy named in Haskell's account", "term", P256, 165,
     "Contemporary theories said to be gaining ground; no particular school or text is identified."),
    (8405, "Officials serving the Venetian state (unnamed collective group)", "term", P256, 163,
     "Unnamed public officials whom Haskell says were accustomed to comparisons with Roman heroes."),
    (8406, "City of Padua as civic body named in the Antonio Loredan oration", "institution", NOTES, 379,
     "The oration is said to be delivered in the city's name; retain as a source-level civic body distinct from the place."),
    (8407, "Fortress of Legnano commanded by Pietro Loredan", "place", P256, 164,
     "Fortress as named in Haskell's account; no present-day site identification is added."),
    (8408, "Aristocratic extravagance as the subject's political meaning", "term", P256, 165,
     "Haskell's interpretive description of the Banquet theme; preserve it as an authorial concept."),
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


def mention(segment_id, first_line, suffix, cid, surface, note="", last_line=None):
    mid = f"m-chp9-p256-{suffix}"
    if mid in existing_mention_ids or any(r["mention_id"] == mid for r in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mid}")
    last_line = first_line if last_line is None else last_line
    search_text = "\n".join(source_lines[n - 1] for n in range(first_line, last_line + 1))
    pos = search_text.find(surface)
    if pos < 0:
        raise SystemExit(f"surface not found at L{first_line}-{last_line}: {surface!r}")
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
    (P256, 158, "tiepolo-sandi-first-employment", "cand-2569", "Tiepolo", "Named painter in the Sandi passage."),
    (P256, 158, "law-profession", "cand-8372", "the extremely lucrative profession of the law", "The family's fortunes are said to be closely linked to this profession."),
    (P256, 158, "sandi-palace", "cand-2352", "their palace", "Anaphoric reference to the Sandi palace index candidate."),
    (P256, 158, "powers-of-eloquence", "cand-2602", "Powers of Eloquence", "Work title as printed; use the existing index candidate."),
    (P256, 158, "four-stories-antiquity", "cand-8402", "four stories from antiquity", "The Sandi ceiling's four narrative subjects."),
    (P256, 158, "goldoni-status", "cand-1205", "Goldoni", "Named source of the reported claim about lawyers' status."),
    (P256, 158, "goldoni-memoirs", "cand-1209", "his Memoirs", "Index sub-entry for Goldoni's Memoirs; edition is not supplied here."),
    (P256, 158, "lawyers", "cand-8372", "lawyers", "Professional group in Goldoni's reported status comparison."),
    (P256, 158, "venice-lawyer-status", "cand-2748", "Venice", "City in the index sub-entry on lawyers' eighteenth-century status."),
    (P256, 158, "nobility", "cand-8108", "the nobility", "Social estate used as the comparison group."),
    (P256, 158, "non-nobles", "cand-8373", "non-nobles", "Unnamed social group contrasted with the nobility."),
    (P256, 158, "cordellina-first-name", "cand-0842", "Carlo", "Given name before the surname continues at the start of L159."),
    (P256, 159, "cordellina-surname", "cand-0842", "Cordellina", "Surname completing the L158/L159 reference to Carlo Cordellina."),
    (P256, 159, "cordellina-leading-advocate", "cand-0842", "the leading advocate of the day", "Haskell's description of Cordellina's contemporary standing."),
    (P256, 160, "cordellina-wife", "cand-8374", "his wife", "Unidentified wife; the passage does not give her name."),
    (P256, 160, "vicenza-house", "cand-8375", "one in his native Vicenza", "Unidentified urban house built by Cordellina."),
    (P256, 160, "vicenza", "cand-2769", "Vicenza", "City named as Cordellina's native place and site of one house."),
    (P256, 160, "montecchio-country-house", "cand-8376", "one in the country at Montecchio", "Unidentified country house; this is the latter house decorated by Tiepolo."),
    (P256, 160, "montecchio", "cand-8377", "Montecchio", "Locality named for Cordellina's country house."),
    (P256, 160, "tiepolo-summoned", "cand-2569", "Tiepolo", "Artist summoned to decorate Cordellina's country house."),
    (P256, 160, "cordellina-entertainment", "cand-0842", "Cordellina", "Named as renowned for extensive entertainment."),
    (P256, 160, "continence-of-scipio-work", "cand-2583", "The Continence of Scipio", "Title as printed and indexed."),
    (P256, 160, "scipio-figure", "cand-8387", "Scipio", "Figure named within the indexed work title."),
    (P256, 160, "family-of-darius-work", "cand-2589", "the Family of Darius before Alexander the\nGreat", "The title crosses the OCR line boundary; exact source span is retained.", 161),
    (P256, 160, "darius-figure", "cand-8388", "Darius", "Figure named within the work title."),
    (P256, 160, "alexander-figure", "cand-8389", "Alexander the\nGreat", "The source title line-breaks the name; exact source span is retained.", 161),
    (P256, 161, "triumph-of-arts-work", "cand-2610", "the Triumph of the Arts", "Title as printed; identified as the ceiling work in this passage."),
    (P256, 162, "classical-stories", "cand-8402", "Greek and Roman stories", "Haskell's account of a familiar classical narrative repertory."),
    (P256, 162, "aristocratic-virtues", "cand-8108", "aristocratic virtues", "The virtues are the purpose for which the stories were codified, not a named group of persons."),
    (P256, 163, "patrician-families", "cand-8108", "patrician famines", "OCR reads 'famines'; scan confirms 'families'. Collective aristocratic families in Haskell's statement about Roman descent."),
    (P256, 163, "state-officials", "cand-8405", "officials in the service of the state", "Unnamed collective group in Haskell's account."),
    (P256, 163, "venetian-state", "cand-8350", "the state", "The political state is the Venetian polity in context."),
    (P256, 163, "pietro-loredan", "cand-1438", "Pietro\nLoredan", "The name crosses the OCR line boundary." ,164),
    (P256, 164, "neutral-venice", "cand-8350", "neutral Venice", "Political Venice in the 1724 Loredan account, distinct from the city-as-place candidate."),
    (P256, 164, "legnano-fortress", "cand-8407", "the fortress of Legnano", "Pietro Loredan is said to command this fortress."),
    (P256, 164, "mucius-scaevola", "cand-8384", "Mucius Scaevola", "Roman hero invoked by an orator; note 6 provides the cited oration locator."),
    (P256, 164, "loredan-family", "cand-8386", "the Loredan family", "Family named as Antonio's family; do not infer the exact kinship to Pietro."),
    (P256, 164, "antonio-loredan", "cand-1437", "Antonio", "The source names this family member by first name only in the passage."),
    (P256, 164, "padua-governorship", "cand-1803", "governorship of Padua", "Padua is the location of Antonio Loredan's stated governorship."),
    (P256, 164, "padua-city", "cand-1803", "Padua", "Place named as the governorship location."),
    (P256, 164, "pompey", "cand-8385", "Pompey", "Roman comparator in Haskell's account."),
    (P256, 164, "sacrifice-theme", "cand-8403", "The theme of Sacrifice", "Capitalized subject treated as a history-painting theme."),
    (P256, 164, "antiquity-scenes", "cand-8402", "antiquity", "Antiquity as the source of more exhilarating narrative subjects."),
    (P256, 164, "tiepolo-banquet", "cand-2569", "Tiepolo", "Artist named as a frequent painter of the banquet subject."),
    (P256, 164, "banquet-cleopatra-index", "cand-2577", "The Banquet of Antony and Cleopatra", "Use the page-specific index candidate; this passage describes a recurrent subject, not a single confirmed version."),
    (P256, 164, "antony-banquet", "cand-8401", "Antony", "Source spelling in the work title; identity alignment is for S3."),
    (P256, 164, "cleopatra-banquet", "cand-4157", "Cleopatra", "Named figure in the work title."),
    (P256, 165, "eastern-queen", "cand-4157", "Eastern queen", "Anaphoric description of Cleopatra in the preceding sentence."),
    (P256, 165, "roman-hero-west", "cand-8401", "rough Roman hero from the West", "Anaphoric description of Antony in the preceding sentence."),
    (P256, 165, "venice-policy", "cand-8350", "Venice’s own pohey", "OCR reads 'pohey'; scan confirms 'policy'. Political Venice in Haskell's qualified interpretation."),
    (P256, 165, "political-economy", "cand-8404", "new theories of political economy", "Unnamed theories said to be gaining ground."),
    (P256, 165, "aristocratic-extravagance", "cand-8408", "aristocratic extravagance", "Social-political concept in Haskell's interpretation."),
    (P256, 165, "carlo-gozzi", "cand-1219", "Carlo Gozzi", "Named writer whose writings are said to provide a literary equivalent."),
    (P256, 165, "antonio-longo", "cand-1435", "Antonio Longo", "Name introduced at the start of a sentence continuing at p.257 L168."),
    (NOTES, 374, "biblioteca-correr", "cand-8262", "Biblioteca Correr", "Repository named in the note; existing institution candidate reused."),
    (NOTES, 374, "venezia-correr", "cand-2719", "Venezia", "Italian city name in the manuscript locator."),
    (NOTES, 375, "morassi-author", "cand-8257", "Morassi", "Author named in the citation; existing candidate reused."),
    (NOTES, 375, "amphion-story", "cand-8397", "Amphion building the walls of Thebes with his song", "One subject listed in note 2."),
    (NOTES, 375, "amphion-person", "cand-8390", "Amphion", "Mythological figure in the listed subject."),
    (NOTES, 375, "thebes-place", "cand-8391", "Thebes", "Mythological location in the listed subject."),
    (NOTES, 375, "hercules-cecrops-story", "cand-8398", "Hercules with the chained Cecrops", "One subject listed in note 2."),
    (NOTES, 375, "hercules-person", "cand-4162", "Hercules", "Existing source-local person candidate reused."),
    (NOTES, 375, "cecropos-person", "cand-8392", "Cecrops", "Mythological figure in the listed subject."),
    (NOTES, 375, "orpheus-eurydice-story", "cand-8399", "Orpheus claiming Eurydice", "One subject listed in note 2."),
    (NOTES, 375, "orpheus-person", "cand-8393", "Orpheus", "Mythological figure in the listed subject."),
    (NOTES, 375, "eurydice-person", "cand-8394", "Eurydice", "Mythological figure in the listed subject."),
    (NOTES, 375, "perseus-pegasus-story", "cand-8400", "Perseus on Pegasus slaying the Sea Monster", "One subject listed in note 2; the monster is unnamed."),
    (NOTES, 375, "perseus-person", "cand-8395", "Perseus", "Mythological figure in the listed subject."),
    (NOTES, 375, "pegasus-figure", "cand-8396", "Pegasus", "Named mythological creature; type remains unset pending taxonomy review."),
    (NOTES, 376, "goldoni-note-source", "cand-1205", "Goldoni", "Author named in the source locator; existing person candidate reused."),
    (NOTES, 376, "goldoni-memoirs-note", "cand-1209", "Mémoires", "Publication named in the source locator; edition is not supplied."),
    (NOTES, 376, "fontanella-cited-name", "cand-8378", "G. B. Fontanella", "Source form bracketed in the printed note; identity remains unresolved."),
    (NOTES, 377, "tiepolo-letter-author", "cand-2569", "Tiepolo", "Author named in the letter locator."),
    (NOTES, 377, "algarotti-recipient", "cand-0041", "Francesco Algarotti", "Recipient named in the letter locator; existing index candidate reused."),
    (NOTES, 377, "fogolari-editor", "cand-8380", "Fogolari", "Surname-only form from the printed note."),
    (NOTES, 377, "tiepolo-algarotti-letter", "cand-8379", "Letter from Tiepolo to Francesco Algarotti of 26 October 1743", "Specific cited correspondence; not independently consulted."),
    (NOTES, 377, "fogolari-publication", "cand-8381", "Fogolari, 1.942, p. 34", "Raw OCR citation surface; page image reads 1942, p. 34."),
    (NOTES, 378, "pietro-orazione-title", "cand-8382", "La Rappresentanza del veto merito", "Raw OCR title surface; page image reads 'vero merito'."),
    (NOTES, 378, "pietro-orazione-pietro", "cand-1438", "Pietro Loredan", "Person named in the title of the cited oration."),
    (NOTES, 378, "pietro-orazione-legnano", "cand-8407", "Fortezza di Legnano", "Fortress named in the cited title; OCR role spelling is corrected in S2 only."),
    (NOTES, 378, "pietro-orazione-venezia", "cand-2719", "Venezia", "Publication city in the cited title."),
    (NOTES, 379, "antonio-orazione-title", "cand-8383", "Orazione detta in nome della magnificá Citd di Padova", "Raw OCR title surface; the page image reads 'magnifica Città'."),
    (NOTES, 379, "padua-civic-body", "cand-8406", "Citd di Padova", "Raw OCR reference to the civic body of Padua; page image reads 'Città di Padova'."),
    (NOTES, 379, "antonio-orazione-padua", "cand-1803", "Padova", "Publication and civic location in the cited title."),
    (NOTES, 379, "antonio-orazione-antonio", "cand-1437", "Antonio Loredan", "Person named in the cited oration title."),
]
for spec in MENTION_SPECS:
    mention(*spec)

new_statements = []
existing_statement_ids = {r["statement_id"] for r in statements}


def statement(suffix, segment_id, first, last, subject, obj, predicate, claim, qualification,
              mentioned, marker=None, speaker="Haskell", text_layer="body", extras=None):
    sid = f"st-chp9-p256-{suffix}"
    if sid in existing_statement_ids or any(r["statement_id"] == sid for r in new_statements):
        raise SystemExit(f"duplicate statement ID: {sid}")
    m = segment_by_id[segment_id]
    if first < m["line_start"] or last > m["line_end"]:
        raise SystemExit(f"statement lines outside segment {segment_id}: {sid}")
    if any(cid and cid not in candidate_ids for cid in [subject, obj, *mentioned]):
        raise SystemExit(f"missing candidate in statement: {sid}")
    q = {"source_line_start": first, "source_line_end": last, "printed_page": 256,
         "pdf_physical_page": 18, "claim": claim, "speaker": speaker, "text_layer": text_layer,
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


statement("sandi-ennobled-1685", P256, 158, 158, "cand-8356", None,
          "ennobled_in_1685",
          "Haskell says the Sandi had been ennobled only in 1685.",
          "This closes the p.255 L154 sentence. Footnote 1 cites a Correr genealogy manuscript; it was not independently consulted.",
          ["cand-8356", "cand-8262", "cand-8263"], marker=1,
          extras={"cross_reference_segments": [{"segment_id": P255, "source_line_start": 154, "source_line_end": 154},
                                                {"segment_id": NOTES, "source_line_start": 374, "source_line_end": 374}]})
statement("sandi-early-tiepolo-employers", P256, 158, 158, "cand-8356", "cand-2569",
          "among_the_first_to_employ_tiepolo",
          "Haskell says the Sandi were among the first to employ Tiepolo.",
          "The family is the same source-local Sandi candidate introduced at p.255; formal identity alignment remains for S3.",
          ["cand-8356", "cand-2569"], extras={"relation_candidate": True,
                                               "cross_reference_segments": [{"segment_id": P255, "source_line_start": 154, "source_line_end": 154}]})
statement("sandi-fortunes-linked-to-law", P256, 158, 158, "cand-8356", "cand-8372",
          "family_fortunes_closely_linked_to_law_profession",
          "Haskell says the Sandi's fortunes were closely linked to the extremely lucrative profession of the law.",
          "Preserve Haskell's causal/social interpretation; no individual lawyer or legal institution is inferred.",
          ["cand-8356", "cand-8372"])
statement("sandi-ceiling-powers-of-eloquence", P256, 158, 158, "cand-8356", "cand-2602",
          "commissioned_palace_ceiling_illustrating_powers_of_eloquence",
          "Haskell says the Sandi commissioned a ceiling in their palace illustrating the Powers of Eloquence through four ancient stories.",
          "The passage identifies the indexed subject and a four-story program; the named scene list is supplied in note 2 and preserved separately below.",
          ["cand-8356", "cand-2352", "cand-2602", "cand-8402"], marker=2,
          extras={"relation_candidate": True,
                  "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 375, "source_line_end": 375}]})
statement("goldoni-lawyers-status", P256, 158, 158, "cand-8372", "cand-8108",
          "lawyers_status_second_only_to_nobility",
          "Haskell reports that Goldoni's Memoirs say lawyers in eighteenth-century Venice enjoyed a status second only to the nobility.",
          "Nested report: Goldoni as quoted/reported by Haskell. It is not independently checked against the cited Memoirs.",
          ["cand-1205", "cand-1209", "cand-8372", "cand-2748", "cand-8108"], marker=3,
          extras={"quoted_speaker": "Carlo Goldoni (as reported by Haskell)",
                  "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 376, "source_line_end": 376}]})
statement("cordellina-one-of-few-non-noble-tiepolo-patrons", P256, 158, 159, "cand-0842", "cand-2569",
          "one_of_few_non_nobles_able_to_employ_tiepolo",
          "Haskell identifies Carlo Cordellina as one of the very few non-nobles who had the chance to employ Tiepolo.",
          "The source does not enumerate the other non-noble patrons or define the count meant by 'very few'.",
          ["cand-0842", "cand-8373", "cand-2569"], extras={"relation_candidate": True})
statement("cordellina-described-as-leading-advocate", P256, 159, 159, "cand-0842", None,
          "described_as_leading_advocate_of_the_day",
          "Haskell describes Cordellina as the leading advocate of the day.",
          "Retain this as Haskell's characterization; no office or legal record is added.", ["cand-0842", "cand-8372"])
statement("cordellina-lifestyle-and-wife", P256, 159, 160, "cand-0842", "cand-8374",
          "rejected_useless_luxury_but_believed_in_splendid_living",
          "Haskell says Cordellina disliked useless luxury such as loading his wife with precious stones, but believed in splendid living.",
          "Haskell attributes this characterization to a bracketed Fontanella reference in note 4; the source was not independently consulted. The passage does not say that his wife actually wore or owned the stones.",
          ["cand-0842", "cand-8374", "cand-8378"], marker=4,
          extras={"cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 376, "source_line_end": 376}]})
statement("cordellina-built-vicenza-house", P256, 160, 160, "cand-0842", "cand-8375",
          "built_house_in_native_vicenza",
          "Haskell says Cordellina built a house in his native Vicenza.",
          "The exact building is unidentified; Vicenza is separately recorded as the locality.", ["cand-0842", "cand-8375", "cand-2769"],
          extras={"relation_candidate": True})
statement("cordellina-built-montecchio-house", P256, 160, 160, "cand-0842", "cand-8376",
          "built_country_house_at_montecchio",
          "Haskell says Cordellina built a country house at Montecchio.",
          "The exact building and the modern locality boundary are not established by this passage.", ["cand-0842", "cand-8376", "cand-8377"],
          extras={"relation_candidate": True})
statement("cordellina-summoned-tiepolo-to-country-house", P256, 160, 160, "cand-0842", "cand-2569",
          "summoned_tiepolo_to_decorate_montecchio_house",
          "Haskell says Cordellina summoned Tiepolo to decorate the country house at Montecchio.",
          "The place is the house identified as the latter of Cordellina's two homes; the particular decoration is described in the following lines.",
          ["cand-0842", "cand-2569", "cand-8376"], extras={"relation_candidate": True})
statement("tiepolo-irritated-by-cordellina-entertainment", P256, 160, 160, "cand-2569", "cand-0842",
          "artist_reportedly_irritated_by_cordellina_entertainment",
          "Haskell says Tiepolo was much irritated by the extensive entertainment for which Cordellina was renowned.",
          "The sentence cites a Tiepolo letter in note 5; the letter is a citation locator only and was not independently consulted.",
          ["cand-2569", "cand-0842", "cand-8379", "cand-8380", "cand-8381"], marker=5,
          extras={"cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 377, "source_line_end": 377}]})
statement("tiepolo-painted-continence-scipio", P256, 160, 160, "cand-2569", "cand-2583",
          "painted_continence_of_scipio_on_country_house_wall",
          "Haskell says Tiepolo frescoed The Continence of Scipio on the walls of Cordellina's country house.",
          "Use the page-specific index work candidate; formal work identity remains for S3.",
          ["cand-2569", "cand-2583", "cand-8376", "cand-8387"], extras={"relation_candidate": True})
statement("tiepolo-painted-family-of-darius", P256, 160, 161, "cand-2569", "cand-2589",
          "painted_family_of_darius_before_alexander_on_country_house_wall",
          "Haskell says Tiepolo frescoed The Family of Darius before Alexander the Great on the walls of Cordellina's country house.",
          "The printed title runs over an OCR line boundary; use the existing index work candidate and defer work identity to S3.",
          ["cand-2569", "cand-2589", "cand-8376", "cand-8388", "cand-8389"], extras={"relation_candidate": True})
statement("tiepolo-painted-triumph-of-arts", P256, 161, 161, "cand-2569", "cand-2610",
          "painted_triumph_of_arts_on_country_house_ceiling",
          "Haskell says Tiepolo frescoed The Triumph of the Arts on the ceiling of Cordellina's country house.",
          "Use the existing index work candidate; the passage does not supply a separate date or independent object identification.",
          ["cand-2569", "cand-2610", "cand-8376"], extras={"relation_candidate": True})
statement("wall-paintings-allude-to-cordellina-magnanimity", P256, 161, 161, "cand-0842", None,
          "wall-scenes_are_clear_allusions_to_patron_magnanimity",
          "Haskell interprets the wall scenes as clear allusions to the magnanimity of Cordellina, their patron.",
          "This is Haskell's reading of the Continence of Scipio and Family of Darius scenes, not an independently verified commission statement.",
          ["cand-0842", "cand-2583", "cand-2589"])
statement("classical-repertoire-codified-for-aristocratic-virtues", P256, 162, 162, "cand-8402", "cand-8108",
          "classical-stories-codified_for_display_of_aristocratic_virtues",
          "Haskell says a familiar Greek and Roman story repertory had been codified in the sixteenth and seventeenth centuries for displaying aristocratic virtues, and later artists drew heavily on it.",
          "The source's OCR 'famihar' is read as 'familiar' from the scan; the statement remains Haskell's art-historical generalization.",
          ["cand-8402", "cand-8108"], extras={"ocr_corrections": [{"line": 162, "ocr": "famihar", "reading": "familiar", "basis": "CHP-9.pdf physical p.18"}]})
statement("classical-scenes-may-have-precise-meanings", P256, 162, 162, None, "cand-8402",
          "scenes_may_have_more_precise_meanings_than_currently_understood",
          "Haskell says it is probable that such scenes may often have had more precise meanings than are presently understood.",
          "Preserve both 'probable' and 'may often'; do not supply the unrecorded meanings.", ["cand-8402"])
statement("patrician-families-claimed-roman-descent", P256, 163, 163, "cand-8108", None,
          "many_patrician_families_claimed_roman_descent",
          "Haskell says many patrician families claimed Roman descent.",
          "This is Haskell's report of claims made by families, not a verification of those genealogies.", ["cand-8108"],
          extras={"ocr_corrections": [{"line": 163, "ocr": "famines", "reading": "families", "basis": "CHP-9.pdf physical p.18"}]})
statement("state-officials-heard-roman-hero-comparisons", P256, 163, 163, "cand-8405", None,
          "officials_accustomed_to_comparisons_with_roman_heroes",
          "Haskell says officials serving the state were accustomed to hearing themselves compared with Roman heroes on trivial pretexts.",
          "Collective authorial generalization; no individual official is inferred.", ["cand-8405", "cand-8350"])
statement("pietro-loredan-1724-mucius-comparison", P256, 163, 164, "cand-1438", "cand-8384",
          "pietro_loredan_departure_compared_to_mucius_scaevola",
          "Haskell says that in 1724 Pietro Loredan left a neutral Venice for the fortress of Legnano, which he commanded, and an orator alluded to Mucius Scaevola's heroism.",
          "The comparison is reported by Haskell and linked to the printed 1724 oration cited in note 6; that oration was not independently consulted.",
          ["cand-1438", "cand-8350", "cand-8407", "cand-8384", "cand-8382"], marker=6,
          extras={"relation_candidate": True, "cross_reference_segments": [
              {"segment_id": NOTES, "source_line_start": 378, "source_line_end": 378}]})
statement("antonio-loredan-pompey-comparison", P256, 164, 164, "cand-1437", "cand-8385",
          "antonio_loredan_departure_from_padua_compared_to_pompey",
          "Haskell says that at about the same time Antonio Loredan, another member of the Loredan family, was compared to Pompey when leaving the governorship of Padua.",
          "Keep 'at about the same time'; the source does not assign the 1724 date to Antonio's departure. Note 7 cites an undated Padua oration, not independently consulted.",
          ["cand-1437", "cand-8386", "cand-8385", "cand-1803", "cand-8383"], marker=7,
          extras={"relation_candidate": True, "cross_reference_segments": [
              {"segment_id": NOTES, "source_line_start": 379, "source_line_end": 379}]})
statement("sacrifice-theme-links-melodrama-and-power", P256, 164, 164, "cand-8403", None,
          "popular_theme_satisfied_melodrama_and_evoked_power_responsibilities",
          "Haskell says the theme of Sacrifice was especially popular because it satisfied the century's love of melodrama while alluding to the responsibilities of power.",
          "Authorial explanation of the theme's appeal; no specific painting is named here.", ["cand-8403"])
statement("antiquity-offered-exhilarating-scenes", P256, 164, 164, None, "cand-8402",
          "antiquity_provided_more_exhilarating_scenes",
          "Haskell says antiquity provided a fund of more exhilarating scenes.",
          "A general transition to the following account of the Banquet theme.", ["cand-8402"])
statement("tiepolo-followers-frequently-painted-banquet", P256, 164, 164, "cand-2569", "cand-2577",
          "tiepolo_and_followers_frequently_painted_banquet_subject",
          "Haskell says Tiepolo and his followers frequently painted The Banquet of Antony and Cleopatra.",
          "The passage describes a recurring subject and does not identify one individual painting or version; the page-specific index candidate is retained for S3.",
          ["cand-2569", "cand-2577", "cand-8401", "cand-4157"], extras={"relation_candidate": True})
statement("banquet-glorifies-cleopatra-over-antony", P256, 164, 165, "cand-2577", "cand-4157",
          "banquet_glorifies_cleopatra_challenging_antony_by_astuteness_and_wealth",
          "Haskell says the banquet glorified Cleopatra, a beautiful Eastern queen who successfully challenged the rough Roman hero Antony through astuteness and wealth.",
          "This is the source's iconographic and evaluative account of the recurrent subject, not an identification of a particular surviving work.",
          ["cand-2577", "cand-4157", "cand-8401"])
statement("banquet-as-allusion-to-venetian-policy", P256, 165, 165, "cand-2577", "cand-8350",
          "banquet_surely_a_veiled_allusion_to_venetian_policy",
          "Haskell says the Banquet was surely a veiled allusion to Venice's own policy during those years.",
          "Preserve the author's interpretive 'surely'; the policy is not specified or independently reconstructed.",
          ["cand-2577", "cand-8350"], extras={"relation_candidate": True})
statement("banquet-as-aristocratic-extravagance-against-political-economy", P256, 165, 165, "cand-2577", "cand-8404",
          "banquet_symbolized_final_aristocratic_extravagance_against_economic_theories",
          "Haskell says the theme also symbolized a final enthusiastic fling of aristocratic extravagance against new theories of political economy gaining ground everywhere.",
          "Keep this as Haskell's interpretation; 'final fling' is his characterization, not a measured end date.",
          ["cand-2577", "cand-8408", "cand-8404"])
statement("gozzi-literary-equivalent", P256, 165, 165, "cand-8408", "cand-1219",
          "literary_equivalent_in_writings_of_carlo_gozzi",
          "Haskell says the reactionary manifesto found its literary equivalent in some writings of Carlo Gozzi.",
          "The passage does not identify particular writings; retain 'some' and do not assign titles.", ["cand-8408", "cand-1219"])

statement("note1-correr-manuscript-locator", NOTES, 374, 374, "cand-8356", "cand-8263",
          "haskell_cites_correr_genealogy_manuscript_for_sandi_reference",
          "Haskell's note 1 cites the Discendenze Patrizie manuscript, Biblioteca Correr, MSS XI, E 2/6.",
          "Citation locator only; the manuscript was not independently consulted.",
          ["cand-8356", "cand-8262", "cand-8263", "cand-2719"], marker=1,
          speaker="Haskell's footnote", text_layer="footnote citation",
          extras={"cross_reference_segments": [{"segment_id": P256, "source_line_start": 158, "source_line_end": 158}]})
statement("note2-morassi-citation", NOTES, 375, 375, None, "cand-8258",
          "citation_locator_morassi_1955_pages_4_to_12",
          "Haskell's note 2 cites A. Morassi, 1955, pages 4–12, for the four subjects listed for the Sandi ceiling.",
          "Citation locator only; the publication and cited pages were not independently consulted.",
          ["cand-8257", "cand-8258", "cand-2602"], marker=2,
          speaker="Haskell's footnote", text_layer="footnote citation",
          extras={"cross_reference_segments": [{"segment_id": P256, "source_line_start": 158, "source_line_end": 158}]})
for suffix, event_id, participants, predicate, claim in [
    ("note2-amphion-story", "cand-8397", ["cand-8390", "cand-8391"], "lists_amphion_building_thebes_with_song",
     "Haskell's note 2 lists Amphion building the walls of Thebes with his song as one of the ceiling's subjects."),
    ("note2-hercules-cecrops-story", "cand-8398", ["cand-4162", "cand-8392"], "lists_hercules_with_chained_cecrops",
     "Haskell's note 2 lists Hercules with the chained Cecrops as one of the ceiling's subjects."),
    ("note2-orpheus-eurydice-story", "cand-8399", ["cand-8393", "cand-8394"], "lists_orpheus_claiming_eurydice",
     "Haskell's note 2 lists Orpheus claiming Eurydice as one of the ceiling's subjects."),
    ("note2-perseus-pegasus-story", "cand-8400", ["cand-8395", "cand-8396"], "lists_perseus_on_pegasus_slays_sea_monster",
     "Haskell's note 2 lists Perseus on Pegasus slaying the Sea Monster as one of the ceiling's subjects."),
]:
    statement(suffix, NOTES, 375, 375, "cand-2602", event_id, predicate, claim,
              "Subject list as printed in Haskell's note, which cites Morassi 1955, pages 4–12; no external source verification is claimed.",
              ["cand-2602", event_id, *participants, "cand-8257", "cand-8258"], marker=2,
              speaker="Haskell's footnote", text_layer="footnote report",
              extras={"relation_candidate": True,
                      "cross_reference_segments": [{"segment_id": P256, "source_line_start": 158, "source_line_end": 158}]})
statement("note3-goldoni-memoirs-citation", NOTES, 376, 376, "cand-1205", "cand-1209",
          "citation_locator_goldoni_memoires_volume_one_chapter_twenty_three",
          "Haskell's note 3 identifies the citation as Goldoni, volume I, pages 105 ff., chapter XXIII of the Mémoires.",
          "Citation locator only; the cited edition and pages were not independently consulted.",
          ["cand-1205", "cand-1209"], marker=3, speaker="Haskell's footnote", text_layer="footnote citation",
          extras={"cross_reference_segments": [{"segment_id": P256, "source_line_start": 158, "source_line_end": 158}]})
statement("note4-fontanella-citation", NOTES, 376, 376, None, "cand-8378",
          "bracketed_fontanella_source_reference",
          "Haskell's note 4 gives the bracketed name G. B. Fontanella.",
          "The footnote supplies no title, page or explicit role; retain the bracketed citation without inferring more.",
          ["cand-8378", "cand-0842"], marker=4, speaker="Haskell's footnote", text_layer="footnote citation",
          extras={"cross_reference_segments": [{"segment_id": P256, "source_line_start": 159, "source_line_end": 160}]})
statement("note5-tiepolo-letter-publication", NOTES, 377, 377, "cand-8379", "cand-8381",
          "letter_cited_as_published_by_fogolari_1942_page_34",
          "Haskell's note 5 cites a letter from Tiepolo to Francesco Algarotti dated 26 October 1743, published by Fogolari in 1942, page 34.",
          "Neither the letter nor the cited publication was independently consulted. OCR has note marker 8 and year 1.942; the scan reads marker 5 and 1942.",
          ["cand-8379", "cand-2569", "cand-0041", "cand-8380", "cand-8381"], marker=5,
          speaker="Haskell's footnote", text_layer="footnote citation",
          extras={"ocr_corrections": [{"line": 377, "ocr": "8 Letter ... 1.942", "reading": "5 Letter ... 1942", "basis": "CHP-9.pdf physical p.18"}],
                  "cross_reference_segments": [{"segment_id": P256, "source_line_start": 160, "source_line_end": 160}]})
statement("note6-pietro-loredan-orazione", NOTES, 378, 378, None, "cand-8382",
          "citation_locator_1724_pietro_loredan_departure_orazione",
          "Haskell's note 6 cites La Rappresentanza del vero merito, an oration for Pietro Loredan's departure to Legnano, published at Venice in 1724.",
          "Citation locator only; the printed oration was not independently consulted. The title OCR 'veto' and role 'Proweditore' are corrected from the scan to 'vero' and 'Provveditore' in S2 only.",
          ["cand-8382", "cand-1438", "cand-8407", "cand-2719"], marker=6,
          speaker="Haskell's footnote", text_layer="footnote citation",
          extras={"ocr_corrections": [{"line": 378, "ocr": "veto merito; Proweditore", "reading": "vero merito; Provveditore", "basis": "CHP-9.pdf physical p.18"}],
                  "cross_reference_segments": [{"segment_id": P256, "source_line_start": 163, "source_line_end": 164}]})
statement("note7-antonio-loredan-orazione", NOTES, 379, 379, None, "cand-8383",
          "citation_locator_padua_orazione_for_antonio_loredan_departure",
          "Haskell's note 7 cites an oration delivered in the name of the City of Padua to Antonio Loredan on his departure from office; no year is supplied.",
          "Citation locator only; the text was not independently consulted. The scan reads 'magnifica Città' where OCR has 'magnificá Citd'.",
          ["cand-8383", "cand-8406", "cand-1437", "cand-1803"], marker=7,
          speaker="Haskell's footnote", text_layer="footnote citation",
          extras={"ocr_corrections": [{"line": 379, "ocr": "magnificá Citd", "reading": "magnifica Città", "basis": "CHP-9.pdf physical p.18"}],
                  "cross_reference_segments": [{"segment_id": P256, "source_line_start": 164, "source_line_end": 164}]})

# The previous page's incomplete Sandi clause now closes; p.256's own final clause remains open.
prior_candidate = [r for r in candidates if r["candidate_id"] == "cand-8356"]
if len(prior_candidate) != 1:
    raise SystemExit(f"expected one p.255 Sandi candidate, found {len(prior_candidate)}")
prior_candidate[0]["detail"] = "P.255 names the Sandi; p.256 says they were ennobled in 1685, among the first to employ Tiepolo, and commissioned a ceiling at their palace. Cross-page claim is recorded; family identity remains for S3."

for statement_id in ("st-chp9-p255-allusive-forms-of-patron-flattery",):
    prior = [r for r in statements if r.get("statement_id") == statement_id]
    if len(prior) != 1:
        raise SystemExit(f"expected one p.255 clause statement {statement_id}, found {len(prior)}")
    q = prior[0]["qualifiers"]
    q["qualification"] = "The two complete clauses end at p.255 L154; the following Sandi clause closes at p.256 L158. The unfinished fragment is not treated as part of this claim."
    refs = q.setdefault("cross_reference_segments", [])
    ref = {"segment_id": P256, "source_line_start": 158, "source_line_end": 158}
    if ref not in refs:
        refs.append(ref)

if len({r["mention_id"] for r in mentions + new_mentions}) != len(mentions) + len(new_mentions):
    raise SystemExit("mention IDs are not unique")
if len({r["statement_id"] for r in statements + new_statements}) != len(statements) + len(new_statements):
    raise SystemExit("statement IDs are not unique")

coverage_by_id[P255].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L149-155",
    "note": "P.255 L154's Sandi sentence closes at p.256 L158. L155 is note 1 continuation linked to consolidated notes L370; all source lines L149-155 are covered.",
})
coverage_by_id[P256].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L158-165",
    "note": "Printed p.256 (CHP-9.pdf physical p.18) reviewed against the scan. L158 closes p.255 L154. L165 ends with the unfinished introduction to Antonio Longo's memoirs and continues at p.257 L168; retain partial. Notes 1-7 are in consolidated lines L374-379.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L349-379; p.255 L155 continuation",
    "note": "Consolidated notes through p.256 notes 1-7 are processed at L349-379; p.255 note 1 continuation at L155 is cross-linked to L370. Later notes from L380 remain queued; citation locators are not independent verification.",
})

summary = {"segments": {sid: [coverage_by_id[sid]["disposition"], coverage_by_id[sid]["migration_status"],
                               coverage_by_id[sid]["source_line_ranges"]] for sid in (P255, P256, NOTES)},
           "new_candidates": len(candidate_specs), "new_mentions": len(new_mentions),
           "new_statements": len(new_statements), "source_hash": meta["sha256"],
           "next_body_segment": f"{P257}#L168 closes p.256 L165"}
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
