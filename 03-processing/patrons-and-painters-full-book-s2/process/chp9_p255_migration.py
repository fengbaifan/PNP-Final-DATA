"""Controlled S2 migration for printed p.255; defaults to a read-only dry run."""
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
P254 = "chp-9:09_CHP-9_intro:l134-146"
P255 = "chp-9:09_CHP-9_intro:l148-155"
P256 = "chp-9:09_CHP-9_intro:l157-165"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
PLATE_LIST = "front-matter:00_05_List_of_Plates:l83-118"
EXPECTED_HASH = "f88796ddd6e409c8850bf64361d76760ed61b8c36cc02b18a32bfe7b35010e3d"
EXPECTED_ASSET_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
BACKUP_SUFFIX = ".bak-s2-chp9-p255-20261001"


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
for sid in (P254, P255, P256, NOTES, PLATE_LIST):
    if sid not in segment_by_id:
        raise SystemExit(f"missing source segment: {sid}")
meta = segment_by_id[P255]
if meta["sha256"] != EXPECTED_HASH or meta["asset_sha256"] != EXPECTED_ASSET_HASH:
    raise SystemExit("p.255 source segment or source asset fingerprint changed")
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


offsets_by_segment = {sid: line_offsets(sid) for sid in (P255, NOTES)}


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
    P254: ("reviewed", "partial", "L135-146"),
    P255: ("queued", "pending", ""),
    NOTES: ("reviewed", "partial", "L349-369"),
}
for sid, expected in expected_states.items():
    row = coverage_by_id.get(sid)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != expected:
        raise SystemExit(f"unexpected coverage state for {sid}: {row}")

candidate_ids = {r["candidate_id"] for r in candidates}
if len(candidate_ids) != len(candidates) or max(int(x.split("-")[1]) for x in candidate_ids) != 8332:
    raise SystemExit("candidate inventory changed; inspect before allocating IDs")
candidate_specs = [
    (8333, "Fatherland personified in the Pisani family allegory", "term", P255, 149,
     "Allegorical figure in Haskell's account of the fresco; do not equate the figure with a political state."),
    (8334, "Living Pisani family members represented in the Plate 44 ceiling allegory", "term", P255, 149,
     "Collective group described as living family members and actual portraits; only Almorò is named here."),
    (8335, "Unnamed mother of Pisani Almorò represented in the Plate 44 allegory", "person", P255, 149,
     "Unidentified woman described as Almorò's mother and represented with him in her lap; identity and genealogy remain unresolved."),
    (8336, "Theological virtues represented around the Virgin in the Pisani allegory", "term", P255, 149,
     "Named as a group in Haskell's iconographic description; individual personifications are separately mentioned."),
    (8337, "Faith personified in the Pisani family allegory", "term", P255, 149,
     "One of the theological virtues named in this work; cross-work identity is for S3."),
    (8338, "Hope personified in the Pisani family allegory", "term", P255, 149,
     "One of the theological virtues named in this work; cross-work identity is for S3."),
    (8339, "Charity personified in the Pisani family allegory", "term", P255, 149,
     "One of the theological virtues named in this work; cross-work identity is for S3."),
    (8340, "Wisdom personified in the Pisani family allegory", "term", P255, 149,
     "Allegorical figure named alongside the theological virtues; keep distinct from other Wisdom candidates pending S3."),
    (8341, "Fame personified in the Pisani family allegory", "person", P255, 149,
     "Figure said to spread the Pisani family's glory; keep separate from other Fame depictions pending S3."),
    (8342, "Africa named in the Pisani allegory's global reach", "place", P255, 150,
     "Geographic continent in Haskell's description of Fame spreading the family's glory."),
    (8343, "Asia named in the Pisani allegory's global reach", "place", P255, 150,
     "Geographic continent in Haskell's description of Fame spreading the family's glory."),
    (8344, "America named in the Pisani allegory's global reach", "place", P255, 150,
     "Geographic continent in Haskell's description of Fame spreading the family's glory."),
    (8345, "England as political actor in Haskell's 1762 comparison", "institution", P255, 150,
     "Political realm named as taking Canada and India from France; keep distinct from place and later-state candidates pending S3."),
    (8346, "Canada named as territory taken from France in Haskell's 1762 comparison", "place", P255, 150,
     "Territorial reference in Haskell's wording; no narrower colony or political status is inferred."),
    (8347, "India named as territory taken from France in Haskell's 1762 comparison", "place", P255, 150,
     "Territorial reference in Haskell's wording; no narrower region or political status is inferred."),
    (8348, "Robespierre (source form; said to be aged four in 1762)", "person", P255, 150,
     "Preserve the surname-only source form; first name and identity alignment are not added at S2."),
    (8349, "Time personified as a standard figure in family allegories", "term", P255, 152,
     "A symbolic figure whose presence could suggest family age, wisdom and virtue; preserve Haskell's modal interpretation."),
    (8350, "Venice as political polity in the League of Cambrai account", "institution", P255, 153,
     "The phrase 'Venice's finest hour' occurs in a political and military context; keep distinct from the city/place candidates."),
    (8351, "League of Cambrai", "event", P255, 153,
     "Named historical conflict in which an unnamed Corner family member is said to have distinguished himself."),
    (8352, "Unidentified Corner family member distinguished during the League of Cambrai", "person", P255, 153,
     "The source says a member of the Corner family distinguished himself but supplies no name."),
    (8353, "Tiepolo's unidentified Soderini historical reconstruction and family apotheosis cycle", "work", P255, 153,
     "A cycle of three fifteenth-century scenes leading to a family apotheosis on a ceiling; do not invent a formal title or villa name."),
    (8354, "Unidentified Contarini family villa at Mira", "place", P255, 153,
     "The villa is named only by family and locality; exact building identity is not supplied in this passage."),
    (8355, "Mira as the locality of the Contarini villa", "place", P255, 153,
     "Locality named for the Contarini villa; modern identification is left for later verification."),
    (8356, "Sandi family named at the close of p.255", "family", P255, 154,
     "The sentence is unfinished at the page break; family context is clear, while its ensuing claim is deferred to p.256."),
    (8357, "Unidentified villa associated with the Soderini fresco cycle", "place", NOTES, 372,
     "Footnote 3 says 'the villa' was destroyed in the First World War; association with the immediately preceding Soderini cycle is contextual, and the villa is unnamed."),
    (8358, "Musée Jacquemart-André named in p.255 note 4", "institution", NOTES, 373,
     "An isolated note label following the Contarini passage; retain as Haskell's locator without inferring more than the source says."),
    (8359, "Zannandreis, author cited in p.255 note 1", "person", NOTES, 370,
     "Surname-only writer reference; full name and identity are not inferred."),
    (8360, "Zannandreis biographical account of Francesco Lorenzi, page 426 (title unspecified)", "archive", NOTES, 370,
     "Citation locator reported by Haskell; the cited text was not independently consulted and the title is not supplied here."),
    (8361, "Reported allegorical scheme for glorifying the unnamed King of Spain, proposed to Tiepolo", "work", NOTES, 370,
     "Zannandreis is reported as saying Lorenzi supplied Tiepolo with a scheme; whether it was realized is not established."),
    (8362, "Unidentified King of Spain named as the subject of the reported allegorical scheme", "person", NOTES, 370,
     "The king is unnamed; do not infer which monarch or align to another King of Spain candidate before S3."),
    (8363, "Pietro Novelli's Memoirs, cited at page 62 (edition/title unspecified)", "archive", P255, 155,
     "Haskell cites Novelli's Memoirs in note 1; the cited page and edition were not independently consulted."),
    (8364, "Pietro Novelli's unidentified work recording the greatness of the Collalto family", "work", P255, 155,
     "The source describes Novelli's choice of subject but gives no formal title; connect to the p.254 Collalto passage without claiming independent identity verification."),
    (8365, "Preparation and patron inspection of modelli for Venetian decorative works", "procedure", P255, 155,
     "A general studio practice described by Haskell; retain the modal and frequency qualifiers in the statement."),
    (8366, "Henri III's 1574 welcome at the Contarini villa in Mira", "event", P255, 153,
     "Haskell identifies a welcome during Henri III's visit; do not infer a formal event title."),
    (8367, "Tiepolo's unidentified Contarini fresco of Henri III's 1574 welcome at Mira", "work", P255, 153,
     "The passage says Tiepolo painted the Contarini at this moment; no formal title or commission is supplied."),
    (8368, "First World War", "event", NOTES, 372,
     "Historical event named only as the time of the villa's destruction."),
    (8369, "Battistella 1903 reference cited in p.255 note 3 (title unspecified)", "archive", NOTES, 372,
     "Citation locator only; title and cited passage were not independently consulted."),
    (8370, "Artist-initiated choice of subject in Venetian decorative commissions", "procedure", P255, 151,
     "Haskell's general claim that artists sometimes initiated subjects; note 1 supplies reported examples and qualifications."),
    (8371, "Lazzarini's unidentified Corner family decoration concerning a member distinguished in the League of Cambrai", "work", P255, 153,
     "The passage says Gregorio Lazzarini was commissioned to paint an unnamed family member; no title, medium beyond painting, or site is supplied."),
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


def mention(segment_id, line_no, suffix, cid, surface, note="", occurrence=0):
    mid = f"m-chp9-p255-{suffix}"
    if mid in existing_mention_ids or any(r["mention_id"] == mid for r in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mid}")
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
    (P255, 149, "pisani-palace-anaphor", "cand-1946", "it", "Anaphor to the Pisani country house at Stra in p.254 L145; place identity remains for S3."),
    (P255, 149, "tiepolo-pisani-design", "cand-2569", "Tiepolo", "Same page-local artist candidate as the p.254 work description."),
    (P255, 149, "pisani-allegory-work", "cand-8316", "the most extraordinary family allegory", "Continuation of the p.254 Apotheosis of the Pisani passage; cross-reference Plate 44 caption without writing a global alignment."),
    (P255, 149, "pisani-family", "cand-3614", "the Pisani family", "Named family subject of the allegory."),
    (P255, 149, "living-family-members", "cand-8334", "the family’s living members", "Collective group depicted as portraits in this particular work."),
    (P255, 149, "youngest-son-role", "cand-1941", "youngest son", "Role of Almorò in Haskell's description; index candidate is retained pending S3."),
    (P255, 149, "almoro", "cand-1941", "Almorô", "Raw OCR spelling; page image reads Almorò. Identity remains for S3."),
    (P255, 149, "almoro-mother", "cand-8335", "his mother", "Unnamed woman described as Almorò's mother; no name or independent genealogical proof."),
    (P255, 149, "ceiling-portraits", "cand-8316", "Actual portraits of these", "Reference to the living family members shown in the work's ceiling."),
    (P255, 149, "fatherland-figure", "cand-8333", "the Fatherland", "Personified figure in the allegory, not an identified polity."),
    (P255, 149, "virgin-first", "cand-3427", "the Virgin", "First occurrence, after 'points out their merits to'."),
    (P255, 149, "theological-virtues-group", "cand-8336", "the theological virtues", "Group named in the iconographic description."),
    (P255, 149, "faith", "cand-8337", "Faith", "Personified theological virtue in the Pisani allegory."),
    (P255, 149, "hope", "cand-8338", "Hope", "Personified theological virtue in the Pisani allegory."),
    (P255, 149, "charity", "cand-8339", "Charity", "Personified theological virtue in the Pisani allegory."),
    (P255, 149, "wisdom", "cand-8340", "Wisdom", "Allegorical subject named alongside the theological virtues."),
    (P255, 149, "virgin-second", "cand-3427", "The Virgin", "Second occurrence, named as surrounded by the allegorical virtues."),
    (P255, 149, "fresco", "cand-8316", "the fresco", "Anaphoric reference to the Pisani family allegory."),
    (P255, 149, "fame", "cand-8341", "Fame", "Allegorical personification in the Pisani work; distinct source-local candidate."),
    (P255, 150, "europe", "cand-3462", "Europe", "Geographic region named in the stated global reach of Fame."),
    (P255, 150, "africa", "cand-8342", "Africa", "Geographic continent named in the stated global reach of Fame."),
    (P255, 150, "asia", "cand-8343", "Asia", "Geographic continent named in the stated global reach of Fame."),
    (P255, 150, "america", "cand-8344", "America", "Geographic region named in the stated global reach of Fame."),
    (P255, 150, "england", "cand-8345", "England", "Named as a political actor; do not resolve its period-specific state identity at S2."),
    (P255, 150, "canada", "cand-8346", "Canada", "Territorial reference in Haskell's 1762 comparison."),
    (P255, 150, "india", "cand-8347", "India", "Territorial reference in Haskell's 1762 comparison."),
    (P255, 150, "france", "cand-8308", "France", "France as a political entity in the preceding p.254 candidate context."),
    (P255, 150, "robespierre", "cand-8348", "Robespierre", "Preserve the surname-only source form."),
    (P255, 151, "artist-subject-choice", "cand-8370", "choosing the subject", "The statement is general and not restricted to Tiepolo; note 1 supplies qualified examples."),
    (P255, 152, "time-figure", "cand-8349", "Time", "Standard allegorical figure; Haskell says it could suggest family age and virtue."),
    (P255, 152, "older-aristocracy", "cand-8108", "the older members of the Venetian aristocracy", "Social group in Haskell's contrast; not individually enumerated."),
    (P255, 152, "new-aristocracy", "cand-8108", "the new aristocracy", "Source-local occurrence of the changing Venetian aristocracy."),
    (P255, 153, "corner-family", "cand-0847", "the Corner", "Family name in the 1700 commission."),
    (P255, 153, "lazzarini", "cand-1368", "Gregorio Lazzarini", "Index candidate for the named painter."),
    (P255, 153, "corner-member", "cand-8352", "a member of their family", "Unnamed male family member, described as distinguished during the League of Cambrai."),
    (P255, 153, "league-of-cambrai", "cand-8351", "the League of Cambrai", "Named historical event."),
    (P255, 153, "venice-polity", "cand-8350", "Venice’s", "Political referent in 'Venice's finest hour', not the city as a place."),
    (P255, 153, "old-families", "cand-8108", "other old families", "Collective category in Haskell's account."),
    (P255, 153, "widmann-family", "cand-2812", "a Widmann", "Family named as beyond the reach of the historical subject."),
    (P255, 153, "grassi-family", "cand-1228", "a Grassi", "Family named as beyond the reach of the historical subject."),
    (P255, 153, "tiepolo-soderini-cycle-artist", "cand-2569", "Tiepolo", "Artist named in the Soderini reconstruction passage."),
    (P255, 153, "soderini-family", "cand-2478", "the Sodcrini", "Raw OCR surface; the page image reads 'Soderini'. Reuse the existing index family candidate, with the OCR correction recorded on the statement."),
    (P255, 153, "florentine-ancestry", "cand-3397", "Florentine", "Geographic origin described adjectivally; do not expand the lineage."),
    (P255, 153, "soderini-three-scenes", "cand-8353", "three scenes from the fifteenth century", "Part of the unnamed Soderini historical reconstruction cycle."),
    (P255, 153, "soderini-apotheosis", "cand-8353", "the family apotheosis on the ceiling", "Climax of the same unnamed Soderini decoration cycle."),
    (P255, 153, "contarini-family", "cand-0824", "the Contarini", "Family named in the Tiepolo passage."),
    (P255, 153, "tiepolo-contarini-fresco", "cand-2569", "he", "Coreference to Tiepolo in the immediately preceding sentence."),
    (P255, 153, "contarini-welcome-event", "cand-8366", "the welcome they gave in 1574", "Haskell's description of the Contarini family's reception of Henri III."),
    (P255, 153, "henri-iii", "cand-1294", "Henri III of France", "Index candidate for the named visitor."),
    (P255, 153, "contarini-villa", "cand-8354", "their villa at Mira", "Unidentified family villa; its exact building identity remains unresolved."),
    (P255, 153, "mira-locality", "cand-8355", "Mira", "Locality named as the villa's site."),
    (P255, 154, "sandi-family", "cand-8356", "The Sandi", "The body sentence continues on p.256; only the family referent is registered here."),
    (P255, 154, "allusive-patronage", "cand-8370", "Sometimes the subject could be more allusive", "Haskell's general account of artist choice; no specific work is identified."),
    (NOTES, 370, "contracts-note1", "cand-0837", "contracts", "Generic contracts for secular decorations; no surviving document is identified."),
    (NOTES, 370, "venice-note1", "cand-2719", "Venice", "City named as the setting for eighteenth-century secular decoration practice."),
    (NOTES, 370, "zannandreis-author", "cand-8359", "Zannandreis", "Surname-only author reference in Haskell's footnote."),
    (NOTES, 370, "lorenzi-note1", "cand-1439", "Francesco Lorenzi", "Index candidate for the Veronese painter."),
    (NOTES, 370, "tiepolo-note1", "cand-2569", "Tiepolo", "Named artist in the reported proposed scheme."),
    (NOTES, 370, "scheme-note1", "cand-8361", "an allegorical scheme", "Unrealized status remains possible; the source says only that Lorenzi supplied a scheme."),
    (NOTES, 370, "king-of-spain-note1", "cand-8362", "the King of Spain", "Unnamed ruler; do not infer an individual monarch."),
    (P255, 155, "lorenzi-story", "cand-1439", "Lorenzi’s culture", "This continuation qualifies the scheme report in note 1 at L370."),
    (P255, 155, "novelli-note1", "cand-1758", "Novelli", "Index candidate for the painter; the note attributes the claim to his Memoirs."),
    (P255, 155, "novelli-memoirs", "cand-8363", "his Memoirs", "Citation to Novelli's Memoirs, page 62; no edition independently consulted."),
    (P255, 155, "collalto-work-note1", "cand-8364", "the Greatness of the Collalto family", "Unformalized work description; refer to the p.254 Collalto passage."),
    (P255, 155, "collalto-family-note1", "cand-8313", "the Collalto family", "Nested in the description of the subject of Novelli's work."),
    (P255, 155, "modelli-note1", "cand-1674", "modelli", "Indexed term; here it denotes proposed works presented for patron inspection."),
    (P255, 155, "modelli-approval-practice", "cand-8365", "inspection by the patron", "General practice described in Haskell's footnote."),
    (NOTES, 371, "da-canal-citation", "cand-6593", "Da Canal, p. 57", "Reuse the existing archive candidate for Da Canal's Vita di Gregorio Lazzarini; exact edition/page reconciliation remains subject to bibliography review."),
    (NOTES, 371, "da-canal-author", "cand-7781", "Da Canal", "Nested surname mention for the author of the cited work."),
    (NOTES, 372, "battistella-citation", "cand-8369", "Battistella, 1903", "Citation locator only; title and cited passage are not supplied here."),
    (NOTES, 372, "soderini-villa-note3", "cand-8357", "The villa", "Contextual antecedent is likely the Soderini residence, but the note does not name it."),
    (NOTES, 372, "world-war-one", "cand-8368", "the First World War", "War named as the time of the villa's destruction."),
    (NOTES, 373, "jacquemart-museum", "cand-8358", "Musée Jacquemart-André", "Museum label in note 4."),
    (NOTES, 373, "paris-note4", "cand-4653", "Paris", "City in the museum location label."),
]
for spec in MENTION_SPECS:
    mention(*spec)

new_statements = []
existing_statement_ids = {r["statement_id"] for r in statements}


def statement(suffix, segment_id, first, last, subject, obj, predicate, claim, qualification,
              mentioned, marker=None, speaker="Haskell", text_layer="body", extras=None):
    sid = f"st-chp9-p255-{suffix}"
    if sid in existing_statement_ids or any(r["statement_id"] == sid for r in new_statements):
        raise SystemExit(f"duplicate statement ID: {sid}")
    m = segment_by_id[segment_id]
    if first < m["line_start"] or last > m["line_end"]:
        raise SystemExit(f"statement lines outside segment {segment_id}: {sid}")
    if any(cid and cid not in candidate_ids for cid in [subject, obj, *mentioned]):
        raise SystemExit(f"missing candidate in statement: {sid}")
    q = {"source_line_start": first, "source_line_end": last, "printed_page": 255,
         "pdf_physical_page": 17, "claim": claim, "speaker": speaker, "text_layer": text_layer,
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


statement("tiepolo-designed-pisani-allegory", P255, 149, 149, "cand-2569", "cand-8316",
          "designed_family_allegory_for_pisani_palace",
          "Continuing the p.254 sentence, Haskell says Tiepolo designed for the Pisani palace the most extraordinary family allegory he had yet painted and cites Plate 44.",
          "The plate list calls the work 'Glorification of the Pisani family' and locates it at Villa Pisani, Stra; p.254 calls it the 'Apotheosis of the Pisani'. Preserve both source forms and defer candidate-to-KU alignment to S3.",
          ["cand-2569", "cand-8316", "cand-1946", "cand-8317", "cand-3614"],
          extras={"relation_candidate": True, "cross_reference_segments": [
              {"segment_id": P254, "source_line_start": 145, "source_line_end": 145},
              {"segment_id": PLATE_LIST, "source_line_start": 118, "source_line_end": 118}],
              "plate_ref": "44", "ocr_corrections": [
                  {"line": 149, "ocr": "Almorô", "reading": "Almorò", "basis": "CHP-9.pdf physical p.17"}]})
statement("pisani-living-members-and-portraits", P255, 149, 149, "cand-8316", "cand-8334",
          "depicts_living_pisani_family_members_as_actual_portraits_in_the_ceiling",
          "Haskell says the allegory celebrates living family members rather than founding fathers or heroes, including the youngest son Almorò seated in his mother's lap, and that actual portraits appear in the ceiling.",
          "The mother is unnamed. This records Haskell's description of the represented figures, not independent identification of the sitters or proof of their genealogy.",
          ["cand-8316", "cand-3614", "cand-8334", "cand-1941", "cand-8335"],
          extras={"relation_candidate": True})
statement("fatherland-invokes-virgin", P255, 149, 149, "cand-8333", "cand-3427",
          "points_out_pisani_members_merits_and_invokes_virgins_blessing",
          "Haskell says the personified Fatherland points out the living members' merits to the Virgin and invokes her blessing on them.",
          "This is the iconographic arrangement described for the Plate 44 fresco; 'Fatherland' is not identified with a state.",
          ["cand-8333", "cand-8316", "cand-8334", "cand-3427"], extras={"relation_candidate": True})
statement("theological-virtues-around-virgin", P255, 149, 149, "cand-8316", "cand-8336",
          "shows_faith_hope_charity_and_wisdom_around_virgin",
          "Haskell says the Virgin is surrounded by the theological virtues Faith, Hope and Charity, and by Wisdom.",
          "The named virtues are preserved as allegorical concepts; cross-work identity is for S3.",
          ["cand-8316", "cand-3427", "cand-8336", "cand-8337", "cand-8338", "cand-8339", "cand-8340"],
          extras={"relation_candidate": True})
statement("fame-spreads-pisani-glory", P255, 149, 150, "cand-8341", "cand-3614",
          "spreads_pisani_family_glory_through_four_named_world_regions",
          "Haskell describes Fame flying on the other side of the fresco to spread the Pisani family's glory throughout Europe, Africa, Asia and America.",
          "This is the allegorical scope reported in the source, not a claim that the family exercised political control over these regions.",
          ["cand-8341", "cand-8316", "cand-3614", "cand-3462", "cand-8342", "cand-8343", "cand-8344"],
          extras={"relation_candidate": True})
statement("pisani-allegory-dated-1762", P255, 150, 150, "cand-8316", None,
          "set_in_or_dated_to_1762",
          "Haskell dates the described allegory's contemporary setting to 1762.",
          "The year is stated in the text; no independent dating judgment is added.", ["cand-8316"])
statement("england-canada-india-france-claim", P255, 150, 150, "cand-8345", "cand-8308",
          "had_just_wrested_canada_and_india_from_france_by_1762",
          "Haskell says that by 1762 England had just wrested Canada and India from France.",
          "Preserve the source's geopolitical wording and relative time marker; this S2 statement does not independently verify or refine the historical claim.",
          ["cand-8345", "cand-8346", "cand-8347", "cand-8308"], extras={"relation_candidate": True})
statement("robespierre-aged-four", P255, 150, 150, "cand-8348", None,
          "was_aged_four_in_1762",
          "Haskell says Robespierre was four years old in 1762.",
          "Retain the surname-only source form; no given name or external birth date is added.", ["cand-8348"])
statement("artist-initiative-in-subject-choice", P255, 151, 151, None, "cand-8370",
          "artists_sometimes_initiated_choice_of_decorative_subject",
          "Haskell says there is evidence that in at least some cases the artist himself took the initiative in choosing the subject.",
          "The statement is explicitly limited to some cases and is not assigned only to Tiepolo; note 1 supplies both examples and qualifications.",
          ["cand-8370", "cand-2569"], marker=1,
          extras={"cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 370, "source_line_end": 370},
                                                {"segment_id": P255, "source_line_start": 155, "source_line_end": 155}]})
statement("wealthy-nobles-access-to-flattery", P255, 151, 151, "cand-8108", None,
          "family_flattery_was_available_to_any_noble_with_money",
          "Haskell says such flattering allegories were available to any noble with the money.",
          "This is Haskell's generalization, not a claim that every noble commissioned such a work.", ["cand-8108", "cand-8316"])
statement("time-as-suggestive-family-symbol", P255, 152, 152, "cand-8349", None,
          "could_suggest_family_age_wisdom_and_virtue_without_precise_reference",
          "Haskell says a standard figure of Time could suggest that a family was old in wisdom and virtue, while the reference need not be too precise.",
          "Preserve 'could' and the author's qualification about imprecision.", ["cand-8349"])
statement("ancestral-glorification-older-aristocracy", P255, 152, 152, "cand-8108", None,
          "ancestral_glorification_confined_to_older_venetian_aristocracy",
          "Haskell says another kind of ancestral glorification was necessarily confined to the older members of the Venetian aristocracy.",
          "Authorial social-historical generalization; no unnamed individuals or family branches are inferred.", ["cand-8108"])
statement("new-aristocracy-refuge-in-past", P255, 152, 153, "cand-8108", None,
          "recording_past_achievements_appealed_as_new_aristocracy_flaunted_titles_and_wealth",
          "Haskell explains that recording specific past achievements first appeared as the new aristocracy flaunted titles and wealth and became more attractive when the past compensated for an inglorious present.",
          "This is Haskell's explanatory interpretation. The sentence runs into the Corner example at p.255 L153, which follows below.",
          ["cand-8108", "cand-8350"], extras={"relation_candidate": False})
statement("corner-commission-lazzarini", P255, 153, 153, "cand-0847", "cand-8371",
          "corner_family_commissioned_lazzarini_to_paint_unnamed_distinguished_member",
          "Haskell says the Corner commissioned Gregorio Lazzarini in 1700 to paint a member of their family who had distinguished himself during the League of Cambrai.",
          "The family member, work title and site are not named. Note 2 cites Da Canal, page 57; the cited page was not independently read.",
          ["cand-0847", "cand-1368", "cand-8371", "cand-8352", "cand-8351", "cand-8350"], marker=2,
          extras={"relation_candidate": True,
                  "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 371, "source_line_end": 371}]})
statement("old-families-followed-historical-subjects", P255, 153, 153, None, "cand-8108",
          "other_old_families_followed_suit_but_subjects_beyond_widmann_and_grassi_means",
          "Haskell says other old families followed suit, while these kinds of historical subjects were beyond the reach of a Widmann or a Grassi.",
          "The Widmann and Grassi are referenced as family names; the source does not enumerate commissions or works for each.",
          ["cand-8108", "cand-2812", "cand-1228"])
statement("tiepolo-soderini-historical-cycle", P255, 153, 153, "cand-2569", "cand-8353",
          "painted_earlier_period_reconstruction_for_soderini_family",
          "Haskell identifies Tiepolo's first elaborate reconstruction of an earlier period as work for the Soderini, noting their 1656 ennoblement, Florentine ancestry and three fifteenth-century scenes leading to a family apotheosis on the ceiling.",
          "OCR 'Sodcrini' is read as 'Soderini' from the page image. The work cycle and villa remain unnamed; note 3 reports destruction of 'the villa' but does not name it.",
          ["cand-2569", "cand-2478", "cand-8353", "cand-3397", "cand-8357"], marker=3,
          extras={"relation_candidate": True, "cross_reference_segments": [
              {"segment_id": NOTES, "source_line_start": 372, "source_line_end": 372}],
              "ocr_corrections": [{"line": 153, "ocr": "Sodcrini", "reading": "Soderini", "basis": "CHP-9.pdf physical p.17"}]})
statement("tiepolo-contarini-henri-welcome", P255, 153, 153, "cand-2569", "cand-8367",
          "painted_contarini_welcome_to_henri_iii_at_mira_in_1574",
          "Haskell says Tiepolo painted the Contarini at their greatest glory, represented by the welcome they gave Henri III of France at their villa in Mira in 1574.",
          "The work has no formal title here. Note 4's isolated Musée Jacquemart-André, Paris label is linked as a likely location locator, with that inference kept explicit.",
          ["cand-2569", "cand-0824", "cand-8367", "cand-8366", "cand-1294", "cand-8354", "cand-8355", "cand-8358", "cand-4653"], marker=4,
          extras={"relation_candidate": True, "cross_reference_segments": [
              {"segment_id": NOTES, "source_line_start": 373, "source_line_end": 373}]})
statement("social-prestige-over-military-prowess", P255, 153, 153, None, None,
          "social_prestige_made_greater_appeal_than_military_prowess",
          "Haskell concludes that social prestige now made a greater appeal than military prowess.",
          "Authorial interpretation of the patronage contrast in the preceding examples.", [])
statement("allusive-forms-of-patron-flattery", P255, 154, 154, None, None,
          "family_allegories_not_only_form_of_patron_flattery_and_subject_could_be_allusive",
          "Haskell says family allegories were not the only way noble patrons could be flattered and that subjects could be more allusive.",
          "These two clauses are complete at p.255 L154. The following Sandi clause is an unfinished separate sentence and is tracked as an open continuation to p.256.", [])

statement("contracts-and-consultation-limits", NOTES, 370, 370, None, "cand-0837",
          "near_absence_of_secular_decoration_contracts_limits_knowledge_of_subject_choice",
          "Haskell says the almost complete absence of contracts for secular decorations makes it difficult to decide how much choice of subject was left to the artist; he says there must have been considerable consultation between patron and painter.",
          "The near absence and consultation are Haskell's assertions, not a census of surviving contracts. OCR 'ofconsultation' is corrected to 'of consultation' from the page image.",
          ["cand-0837", "cand-8370"], marker=1, speaker="Haskell's footnote", text_layer="footnote",
          extras={"cross_reference_segments": [{"segment_id": P255, "source_line_start": 151, "source_line_end": 151},
                                                {"segment_id": P255, "source_line_start": 155, "source_line_end": 155}],
                  "continued_to_segment_id": P255, "continued_to_source_line": 155,
                  "ocr_corrections": [{"line": 370, "ocr": "ofconsultation", "reading": "of consultation", "basis": "CHP-9.pdf physical p.17"}]})
statement("lorenzi-scheme-report", NOTES, 370, 370, "cand-1439", "cand-2569",
          "lorenzi_reportedly_supplied_tiepolo_scheme_to_glorify_king_of_spain",
          "Haskell reports that Zannandreis says Francesco Lorenzi supplied Tiepolo with an allegorical scheme for glorifying the King of Spain.",
          "This is nested reporting via Zannandreis and remains possibly apocryphal according to the continuation at p.255 L155; the scheme is not assumed completed.",
          ["cand-1439", "cand-2569", "cand-8359", "cand-8360", "cand-8361", "cand-8362"], marker=1,
          speaker="Haskell's footnote", text_layer="footnote report and citation",
          extras={"relation_candidate": True, "quoted_speaker": "Zannandreis (as reported by Haskell)",
                  "continued_to_segment_id": P255, "continued_to_source_line": 155,
                  "cross_reference_segments": [{"segment_id": P255, "source_line_start": 151, "source_line_end": 151},
                                                {"segment_id": P255, "source_line_start": 155, "source_line_end": 155}]})
statement("lorenzi-story-qualified-as-possibly-apocryphal", P255, 155, 155, "cand-1439", "cand-8370",
          "story_may_be_apocryphal_but_suggests_artist_freedom",
          "Haskell says the story about Lorenzi may have been apocryphal and designed to show off his culture, but still suggests the artist had considerable freedom.",
          "This is a qualification of note 1's Zannandreis report, not an independent confirmation of the scheme.",
          ["cand-1439", "cand-8359", "cand-8360", "cand-8361", "cand-8370"], marker=1,
          speaker="Haskell's footnote", text_layer="footnote continuation",
          extras={"continued_from_segment_id": NOTES, "continued_from_source_line": 370,
                  "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 370, "source_line_end": 370}],
                  "linked_body_statement_ids": ["st-chp9-p255-lorenzi-scheme-report"]})
statement("novelli-chose-collalto-subject", P255, 155, 155, "cand-1758", "cand-8364",
          "novelli_said_he_chose_subject_recording_collalto_greatness",
          "Haskell says Novelli's Memoirs, page 62, specifically state that Novelli himself chose to record the greatness of the Collalto family.",
          "The cited Memoirs page was not independently consulted; the work is not given a formal title. Cross-reference the p.254 body report without treating it as separate identity verification.",
          ["cand-1758", "cand-8363", "cand-8364", "cand-8313"], marker=1,
          speaker="Haskell's footnote", text_layer="footnote continuation",
          extras={"continued_from_segment_id": NOTES, "continued_from_source_line": 370,
                  "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 370, "source_line_end": 370},
                                                {"segment_id": P254, "source_line_start": 142, "source_line_end": 143}],
                  "linked_body_statement_ids": ["st-chp9-p254-novelli-records-collalto"]})
statement("modelli-presented-for-inspection", P255, 155, 155, None, "cand-8365",
          "most_venetian_artists_submitted_proposed_modelli_for_patron_inspection",
          "Haskell says most eighteenth-century Venetian artists first produced modelli of proposed work for inspection by the patron.",
          "Preserve 'most' and the source's description of a customary practice, not a universal rule.",
          ["cand-8365", "cand-1674"], marker=1, speaker="Haskell's footnote", text_layer="footnote continuation",
          extras={"continued_from_segment_id": NOTES, "continued_from_source_line": 370,
                  "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 370, "source_line_end": 370}]})
statement("few-model-decoration-discrepancies", P255, 155, 155, None, "cand-8365",
          "few_cases_of_great_discrepancy_between_modello_and_completed_decoration",
          "Haskell says there are only a very few cases of great discrepancy between proposed modelli and completed decoration.",
          "A qualified generalization; Haskell uses this as evidence about instruction and artist freedom.",
          ["cand-8365", "cand-1674"], marker=1, speaker="Haskell's footnote", text_layer="footnote continuation",
          extras={"continued_from_segment_id": NOTES, "continued_from_source_line": 370,
                  "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 370, "source_line_end": 370}]})
statement("painter-not-bound-too-rigidly", P255, 155, 155, None, "cand-8370",
          "modelli_evidence_suggests_painter_not_tied_down_too_rigidly",
          "Haskell concludes that these practices suggest the painter was not tied down too rigidly by instructions.",
          "This is Haskell's inference from the reported practice, not a claim that patrons exercised no control.",
          ["cand-8365", "cand-8370"], marker=1, speaker="Haskell's footnote", text_layer="footnote continuation",
          extras={"continued_from_segment_id": NOTES, "continued_from_source_line": 370,
                  "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 370, "source_line_end": 370}]})
statement("note2-da-canal-citation", NOTES, 371, 371, None, "cand-6593",
          "citation_locator_da_canal_page_57",
          "Haskell's note 2 cites Da Canal, page 57, after the Corner–Lazzarini commission.",
          "Citation locator only; the cited page is not independently consulted. Reuse the existing Da Canal archive candidate while leaving exact edition reconciliation for the bibliography pass.",
          ["cand-6593", "cand-7781", "cand-0847", "cand-1368"], marker=2,
          speaker="Haskell's footnote", text_layer="footnote citation")
statement("note3-soderini-villa-destroyed", NOTES, 372, 372, "cand-8357", "cand-8368",
          "villa_associated_with_soderini_cycle_reported_destroyed_in_first_world_war",
          "Haskell's note 3 cites Battistella, 1903, and says the villa was destroyed in the First World War.",
          "The villa's antecedent is contextual and it is unnamed; do not claim a confirmed modern site or work identity. OCR note marker 8 is corrected to printed note 3.",
          ["cand-8357", "cand-8368", "cand-8369", "cand-2478", "cand-8353"], marker=3,
          speaker="Haskell's footnote", text_layer="footnote report and citation",
          extras={"relation_candidate": True, "cross_reference_segments": [
              {"segment_id": P255, "source_line_start": 153, "source_line_end": 153}],
              "ocr_corrections": [{"line": 372, "ocr": "8 See Battistella", "reading": "3 See Battistella", "basis": "CHP-9.pdf physical p.17"}]})
statement("note4-contarini-work-location-label", NOTES, 373, 373, "cand-8367", "cand-8358",
          "note4_lists_musee_jacquemart_andre_paris_after_contarini_work_reference",
          "Haskell's note 4 gives the location label Musée Jacquemart-André, Paris after the Contarini passage.",
          "The short footnote does not name the work or state the relation in a full sentence; treat it as a likely work locator, not a verified current custody record.",
          ["cand-8367", "cand-8358", "cand-4653", "cand-0824", "cand-1294"], marker=4,
          speaker="Haskell's footnote", text_layer="footnote location label",
          extras={"cross_reference_segments": [{"segment_id": P255, "source_line_start": 153, "source_line_end": 153}]})

# Close p.254 statements whose source sentence was left open at the page break.
for statement_id in ("st-chp9-p254-apotheosis-of-pisani-last-great-work", "st-chp9-p254-pisani-palace-comparison"):
    prior = [r for r in statements if r.get("statement_id") == statement_id]
    if len(prior) != 1:
        raise SystemExit(f"expected one p.254 continuation statement {statement_id}, found {len(prior)}")
    q = prior[0]["qualifiers"]
    if q.get("continuation_segment") != P255:
        raise SystemExit(f"unexpected p.254 continuation pointer for {statement_id}: {q.get('continuation_segment')}")
    q.pop("continuation_segment", None)
    refs = q.setdefault("cross_reference_segments", [])
    ref = {"segment_id": P255, "source_line_start": 149, "source_line_end": 149}
    if ref not in refs:
        refs.append(ref)
    if statement_id.endswith("apotheosis-of-pisani-last-great-work"):
        q["qualification"] = "The Tiepolo/Pisani work is described further at p.255 L149 and cross-referenced to Plate 44; formal candidate-to-KU alignment remains for S3."
    else:
        q["qualification"] = "The palace sentence continues at p.255 L149 with Tiepolo's design for it; this statement records only the printed comparison and does not assign the palace to Villa Pisani before S3."

if len({r["mention_id"] for r in mentions + new_mentions}) != len(mentions) + len(new_mentions):
    raise SystemExit("mention IDs are not unique")
if len({r["statement_id"] for r in statements + new_statements}) != len(statements) + len(new_statements):
    raise SystemExit("statement IDs are not unique")

coverage_by_id[P254].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L135-146",
    "note": "P.254 L145 continues at p.255 L149; the continuation has now been read and the sentence closed. The Pisani work description is cross-referenced to p.255 and Plate 44; candidate-to-KU alignment remains for S3.",
})
coverage_by_id[P255].update({
    "disposition": "reviewed", "migration_status": "partial",
    "source_line_ranges": "L149-155",
    "note": "Printed p.255 (CHP-9.pdf physical p.17) reviewed against the scan. L149 closes p.254 L145; body L154 continues at p.256 L158 and remains partial. OCR L155 is footnote 1 continuation from the notes segment L370, not body prose. Plate 44 list-caption evidence at front-matter L118 is cross-referenced.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L349-373; p.255 L155 continuation",
    "note": "Consolidated notes through p.255 note 4 are processed at L349-373. Note 1 continues in the p.255 body OCR segment at L155 and is cross-linked; p.255 notes 2-4 are L371-373. Later notes remain unprocessed; citations are locators unless explicitly described otherwise.",
})

summary = {"segments": {sid: [coverage_by_id[sid]["disposition"], coverage_by_id[sid]["migration_status"],
                               coverage_by_id[sid]["source_line_ranges"]] for sid in (P254, P255, NOTES)},
           "new_candidates": len(candidate_specs), "new_mentions": len(new_mentions),
           "new_statements": len(new_statements), "source_hash": meta["sha256"],
           "next_body_segment": f"{P256}#L158 closes p.255 L154"}
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
