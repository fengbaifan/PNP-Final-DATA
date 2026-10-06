"""Controlled S2 migration for printed p.278; dry-run by default."""
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
SEGMENT = "chp-10:10_CHP-10_intro:l26-41"
PREVIOUS = "chp-10:10_CHP-10_intro:l15-24"
NEXT = "chp-10:10_CHP-10_intro:l43-49"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
SEGMENT_SHA = "11109dec2da0c22589297ae786772e434dfb0571e62cde36113512f37e6db0ab"
MAX_CANDIDATE = 8851
BACKUP_SUFFIX = ".bak-s2-chp10-p278-20261002"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
PREVIOUS_CLOSURE_ID = "st-chp10-p277-incomplete-commission-contrast"
CLOSURE_ID = "st-chp10-p278-taste-divergence-closure"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl_atomic(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


source_bytes = SOURCE.read_bytes()
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if hashlib.sha256(source_bytes).hexdigest() != ASSET_SHA:
    raise SystemExit("Chapter 10 intro source asset changed")
if source_lines[25].strip() != "[Page 278]" or not source_lines[26].startswith("commissions there was a divergence"):
    raise SystemExit("expected p.278 source text changed")
if "poets.6 He belonged" not in source_lines[33]:
    raise SystemExit("expected p.278 OCR footnote marker changed")
if not source_lines[40].endswith("and then to"):
    raise SystemExit("expected p.278 sentence continuation changed")

segment_rows = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {row["segment_id"]: row for row in segment_rows}
segment_meta = segment_by_id.get(SEGMENT)
previous_meta = segment_by_id.get(PREVIOUS)
next_meta = segment_by_id.get(NEXT)
if not segment_meta or segment_meta.get("sha256") != SEGMENT_SHA or segment_meta.get("asset_sha256") != ASSET_SHA:
    raise SystemExit("p.278 source segment missing or changed")
if not previous_meta or not next_meta:
    raise SystemExit("expected adjacent p.277/p.279 source segments missing")
segment_text = "\n".join(source_lines[segment_meta["line_start"] - 1 : segment_meta["line_end"]])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("p.278 source segment content hash mismatch")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_ids = {row["candidate_id"] for row in candidates}
mention_ids = {row["mention_id"] for row in mentions}
statement_ids = {row["statement_id"] for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}
maximum = max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates)
if maximum != MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: expected {MAX_CANDIDATE}, found {maximum}")
expected_states = {
    PREVIOUS: ("reviewed", "partial"),
    SEGMENT: ("queued", "pending"),
    NEXT: ("queued", "pending"),
}
for segment_id, expected in expected_states.items():
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"unexpected coverage state for {segment_id}: {row}")
if PREVIOUS_CLOSURE_ID not in statement_ids:
    raise SystemExit("p.277 partial contrast statement missing")

E = {
    "german_princes": "cand-8841",
    "italy": "cand-3461",
    "hapsburg_empire": "cand-4222",
    "bombelli": "cand-0383",
    "vienna": "cand-2772",
    "bellucci": "cand-0282",
    "bencovich": "cand-0286",
    "diziani": "cand-0922",
    "dresden": "cand-0947",
    "augustus_strong": "cand-0146",
    "munich": "cand-7155",
    "max_emmanuel": "cand-1586",
    "venetian_artists": "cand-8104",
    "austria": "cand-7201",
    "germany": "cand-5529",
    "france": "cand-5317",
    "manchester": "cand-1504",
    "ricci": "cand-2149",
    "pellegrini": "cand-1870",
    "carlisle": "cand-0559",
    "vanbrugh": "cand-2690",
    "england_polity": "cand-4439",
    "venice_city": "cand-2719",
    "republic": "cand-8838",
    "doge": "cand-8450",
    "palladio": "cand-1807",
    "duchess": "cand-1552",
    "london": "cand-1422",
    "scarlatti": "cand-2393",
    "europe": "cand-3462",
}
for key, candidate_id in E.items():
    if candidate_id not in candidate_ids:
        raise SystemExit(f"required existing candidate missing: {key}={candidate_id}")

CANDIDATE_SPECS = [
    ("german_courts", "German courts obtaining and commissioning art from Italy (unnamed collective, Haskell p.278)", "term",
     "Haskell's collective reference to many German courts and the more powerful courts that attracted artists. It is not a named single institution.", 28),
    ("late_baroque", "Late Baroque painting style familiar to the German courts (Haskell p.278)", "term",
     "The style of pictures the German courts continued to purchase; retain as Haskell's characterization, not a dating or attribution of individual works.", 29),
    ("german_court_artists", "Artists attracted to German courts (unnamed collective, Haskell p.278)", "term",
     "Unnamed artists whom the more powerful courts could attract along with their pictures; the passage does not specify their origin or enumerate the group.", 29),
    ("german_court_artists_pictures", "Unidentified pictures of artists attracted to German courts (collective group, Haskell p.278)", "work",
     "The source says powerful courts could attract the artists and their pictures; no individual painting or catalogue identity is supplied.", 29),
    ("hapsburg_authority", "The Hapsburgs as the appointing and commissioning authority in Haskell's p.278 account (scope unresolved)", "",
     "The source uses the plural Hapsburgs for summoning Bombelli and employing Bellucci. Whether this denotes dynasty, court, or political institution remains for S3; do not equate automatically with the existing Hapsburg Empire candidate.", 29),
    ("amigoni", "Giacomo Amigoni named in Haskell's p.278 account", "person",
     "Body-only candidate for the p.278 mention. Same-name Amigoni index candidates elsewhere are retained for later global S3 alignment.", 31),
    ("french_craftsmen", "French craftsmen working in the Nymphenburg gardens (unnamed collective, Haskell p.278)", "term",
     "Unnamed craftsmen described as working alongside Amigoni; no individual or formal workshop is named.", 32),
    ("nymphenburg_gardens", "Nymphenburg gardens at Munich as the setting for the p.278 account", "place",
     "Named garden grounds in which the rococo pavilions stood; distinguish the gardens from the palace and from the pavilions.", 32),
    ("rococo_pavilions", "Rococo pavilions in the Nymphenburg gardens (individual structures unidentified, p.278)", "place",
     "Architectural spaces named collectively as the setting for Amigoni and French craftsmen; the source does not identify individual pavilions.", 32),
    ("south_germany", "South Germany as a region in Haskell's p.278 patronage comparison", "place",
     "Geographic region contrasted with England and Austria; do not collapse it into the whole of Germany.", 33),
    ("autocratic_princes", "Autocratic princes of South Germany or Austria in Haskell's p.278 comparison (unnamed collective)", "term",
     "Unspecified rulers contrasted with English patrons; do not equate them with the separate p.277 group of German princes.", 33),
    ("english_patrons", "English patrons making Venetian artists' departure worthwhile (unnamed collective, p.278)", "term",
     "Collective patrons contrasted with autocratic South German and Austrian princes; the passage does not identify all members.", 33),
    ("dilettantes_poets", "Influential group of dilettantes and poets in contact with Lord Manchester (unnamed, p.278)", "term",
     "Haskell says Manchester was in close touch with this unnamed group; do not turn it into a formal institution.", 34),
    ("whig_nobles", "Society of Whig noblemen in Haskell's p.278 account (collective)", "term",
     "Political-social collective to which Haskell says Manchester belonged; do not infer membership for every person named as his friend.", 34),
    ("whig_victory_1688", "Whig victory of 1688 over the King in Haskell's account (event; parties not fully identified)", "event",
     "Event as characterized by Haskell. Preserve the wording and date; the passage does not name the King or independently establish the event's actors.", 34),
    ("unnamed_king", "The King opposed in Haskell's account of the 1688 Whig victory (identity unspecified here)", "person",
     "The passage uses only the title 'the King'; do not infer a personal identity at S2.", 34),
    ("new_dynasty", "The new dynasty expected to seek Whig support (identity unspecified, p.278)", "family",
     "The source names no dynasty or family; preserve it as an unresolved dynasty rather than identifying it from context.", 34),
    ("duke_marlborough", "Duke of Marlborough named among Lord Manchester's friends (personal identity not supplied on p.278)", "person",
     "Body-only titled-person candidate. The passage does not give a personal name; defer identity resolution to S3.", 34),
    ("whig_country_houses", "Great country houses of Lord Manchester and his friends, named collectively on p.278", "place",
     "Unidentified houses said to be built for Manchester and his friends by Vanbrugh; p.279 continues with named examples, which remain separate until the cross-page evidence is processed.", 35),
    ("revived_feudal_aristocracy", "Revived feudal aristocracy in Haskell's interpretation of English rule (p.278)", "term",
     "Interpretive social-political characterization attributed to Haskell; not an independently verified institutional structure.", 35),
    ("manchester_friends_group", "Lord Manchester and his friends, including the Duke of Marlborough, Lord Carlisle and others (collective, p.278)", "term",
     "Collective referent of 'He and his friends'; do not equate this named circle with the entire society of Whig noblemen.", 34),
    ("manchester_1709_embassy", "Lord Manchester's embassy to Venice described on p.278 as 1709 (same-event relation to p.276 visit unresolved)", "event",
     "Haskell dates this embassy to 1709. P.276 describes a 1707 second official visit followed by departure 'a year later'; do not merge these events or reconcile their dates during S2.", 34),
    ("whig_sons", "Sons of Lord Manchester and his friends looking back to Venice and Palladio (unnamed group, p.278)", "term",
     "Immediate referent of 'their sons' is Manchester and his friends; no individuals are named.", 35),
    ("venetian_oligarchy", "Venetian oligarchy in Haskell's p.278 analogy (political-social structure)", "term",
     "The governing oligarchy is described as ruled by a Doge. Keep this political-social structure distinct from Venice as a city and from the Republic as a polity.", 35),
    ("contemporary_venetians", "Venetians of Haskell's own day in the p.278 comparison (unnamed collective)", "term",
     "Collective group contrasted with the English Whig noblemen; do not treat the city of Venice as the group itself.", 36),
    ("duchess_letter", "Letter from the Duchess of Marlborough to Lord Manchester about music, quoted by Haskell on p.278", "archive",
     "The passage presents a quotation as a letter. Exact date, manuscript or edition identity remain pending note 6 and independent source review.", 36),
    ("music_in_english", "Music in England as described in the Duchess of Marlborough's p.278 letter quotation", "term",
     "Subject of the quoted analogy about music's development and future encouragement; preserve the Duchess as speaker through Haskell.", 37),
    ("italian_music_model", "Italian musical model named by the Duchess as the best master (p.278 quotation)", "term",
     "The Duchess's evaluation of the Italian model for music; this is an artistic reference, not Italy as a geographic entity.", 39),
    ("french_air", "French air as a musical influence associated with gaiety and fashion (p.278 quotation)", "term",
     "The Duchess's phrase for a musical influence; do not map this style reference to France as a place or political entity.", 39),
    ("painting_analogy", "Painting as the art-form analogized to the Duchess's account of music (Haskell p.278)", "term",
     "Haskell's brief authorial transition 'So too with painting'; retain as analogy, not as a specific painting or programme.", 39),
    ("scarlatti_opera", "Alessandro Scarlatti's opera Pyrrhus and Demetrius named on p.278", "work",
     "Named opera in Haskell's account; edition, performance date, and production identity are not supplied in this segment.", 41),
    ("opera_scenes", "Unidentified painted scenes for the London production of Pyrrhus and Demetrius (p.278; sentence continues)", "work",
     "Haskell says Pellegrini and Marco Ricci were set to paint scenes for the opera. The exact scenic objects and what they were next set to do remain unresolved across the page break.", 40),
]

new_candidates = []
C = {}
for offset, (key, name, kind, detail, source_line) in enumerate(CANDIDATE_SPECS, 1):
    candidate_id = f"cand-{MAX_CANDIDATE + offset:04d}"
    if candidate_id in candidate_ids or any(
        row["canonical_name"] == name and row["suggested_type"] == kind for row in candidates
    ):
        raise SystemExit(f"candidate ID/natural key exists: {candidate_id} {name}")
    C[key] = candidate_id
    new_candidates.append({
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
        "candidate_source_ref": f"{SEGMENT}#L{source_line}",
    })


def e(key):
    return E[key]


def c(key):
    return C[key]


line_offsets = {}
offset = 0
for line_no in range(segment_meta["line_start"], segment_meta["line_end"] + 1):
    line_offsets[line_no] = offset
    offset += len(source_lines[line_no - 1]) + 1

new_mentions = []


def add_mention(local_id, line_no, surface, candidate_id, note, occurrence=0):
    mention_id = f"m-chp10-p278-{local_id}"
    if mention_id in mention_ids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    known = candidate_ids | {row["candidate_id"] for row in new_candidates}
    if candidate_id not in known:
        raise SystemExit(f"mention references missing candidate: {mention_id} -> {candidate_id}")
    line = source_lines[line_no - 1]
    positions, start = [], 0
    while True:
        at = line.find(surface, start)
        if at < 0:
            break
        positions.append(at)
        start = at + 1
    if occurrence >= len(positions):
        raise SystemExit(f"surface absent at L{line_no}: {surface!r}; line={line!r}")
    start_char = line_offsets[line_no] + positions[occurrence]
    end_char = start_char + len(surface)
    if segment_text[start_char:end_char] != surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
    new_mentions.append({
        "mention_id": mention_id,
        "segment_id": SEGMENT,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start_char),
        "end_char": str(end_char),
        "note": note,
    })


MENTION_SPECS = [
    ("german_courts", 28, "German courts", "german_courts", "Unnamed plurality of courts; collective term, not a single institution."),
    ("italy", 29, "Italy", "italy", "Origin named for the works of art obtained by German courts."),
    ("late_baroque", 29, "late Baroque style", "late_baroque", "Style to which the courts had grown accustomed, as Haskell phrases it."),
    ("powerful_courts", 29, "The more powerful of them", "german_courts", "Them refers to the German courts in the preceding sentence."),
    ("court_artists", 29, "the artists themselves", "german_court_artists", "Unnamed artists the powerful courts could attract; the text does not enumerate them."),
    ("court_artists_pictures", 29, "their pictures", "german_court_artists_pictures", "Pictures associated with the artists the courts could attract; no individual work is named."),
    ("hapsburgs", 29, "The Hapsburgs", "hapsburg_authority", "Actor in the source; dynasty/court/political-institution boundary unresolved."),
    ("bombelli", 30, "Sebastiano Bombelli", "bombelli", "Reuse the p.278 index candidate."),
    ("vienna_summon", 30, "Vienna", "vienna", "Destination of the Hapsburg summons."),
    ("bellucci", 30, "Antonio Bellucci", "bellucci", "Reuse the p.278 index candidate."),
    ("hapsburg_their", 30, "their court painter", "hapsburg_authority", "Their refers to the Hapsburg authority; preserve its unresolved scope."),
    ("bencovich", 30, "Federico Bencovich", "bencovich", "Reuse the p.278 index candidate; source calls him Dalmatian."),
    ("diziani", 31, "Diziani", "diziani", "Continuation of Gaspare's name across the OCR line break."),
    ("dresden", 31, "Dresden", "dresden", "Destination named for Diziani's work."),
    ("augustus_strong", 31, "Augustus the Strong", "augustus_strong", "Reuse the page-278 index candidate; identity consolidation remains S3."),
    ("amigoni", 31, "Giacomo Amigoni", "amigoni", "Body-only p.278 candidate; related index candidates elsewhere remain for S3."),
    ("munich", 31, "Munich", "munich", "City where Amigoni was already painting."),
    ("max_emmanuel", 32, "Elector Max Emmanuel", "max_emmanuel", "Reuse the page-278 index candidate."),
    ("french_craftsmen", 32, "French craftsmen", "french_craftsmen", "Unnamed collective working alongside Amigoni."),
    ("rococo_pavilions", 32, "rococo pavilions", "rococo_pavilions", "Unidentified architectural spaces, distinct from the gardens."),
    ("nymphenburg_gardens", 32, "Nymphenburg gardens", "nymphenburg_gardens", "Named garden grounds; distinguish from the palace and pavilions."),
    ("english_patrons", 33, "The English", "english_patrons", "Collective national patron group, not England as a polity."),
    ("venetian_artists", 33, "Venetian artists", "venetian_artists", "Reuse the existing collective artist candidate."),
    ("native_country", 33, "their native country", "venice_city", "Their refers to Venetian artists; the passage's native-country reference is Venice."),
    ("autocratic_princes", 33, "autocratic princes", "autocratic_princes", "Unspecified South German or Austrian rulers in the comparison."),
    ("south_germany_south", 33, "South", "south_germany", "First token of the region name, broken across the OCR line boundary."),
    ("south_germany_germany", 34, "Germany", "south_germany", "Continuation of the region name from the preceding OCR line."),
    ("austria", 34, "Austria", "austria", "Country named alongside South Germany."),
    ("manchester", 34, "Lord Manchester", "manchester", "Reuse the indexed person candidate."),
    ("ricci", 34, "Marco Ricci", "ricci", "Reuse the indexed person candidate."),
    ("pellegrini", 34, "Pellegrini", "pellegrini", "Reuse the indexed person candidate."),
    ("venice_embassy", 34, "Venice", "venice_city", "Destination of Manchester's embassy as stated on p.278."),
    ("manchester_embassy", 34, "his embassy to Venice in 1709", "manchester_1709_embassy", "Embassy event as dated by Haskell; relation to the 1707 visit described on p.276 remains unresolved."),
    ("dilettantes_poets", 34, "an influential group of dilettantes and poets", "dilettantes_poets", "Unnamed group; note marker is printed 5, although S0 OCR reads 6."),
    ("manchester_he", 34, "He", "manchester", "Pronoun refers to Lord Manchester."),
    ("whig_nobles", 34, "society of Whig noblemen", "whig_nobles", "Collective political-social group; not a formal organization by evidence in this passage."),
    ("whig_victory", 34, "their victory of 1688", "whig_victory_1688", "Victory attributed to the Whig noblemen by Haskell."),
    ("king", 34, "the King", "unnamed_king", "Only a title is supplied; do not identify the person at S2."),
    ("new_dynasty", 34, "the new dynasty", "new_dynasty", "Dynasty unnamed in the passage."),
    ("whig_them", 34, "them for support", "whig_nobles", "Them refers to the Whig noblemen."),
    ("manchester_friends", 34, "He and his friends", "manchester_friends_group", "He refers to Manchester; preserve the named circle as distinct from the wider Whig society."),
    ("duke_marlborough", 34, "the Duke of Marlborough", "duke_marlborough", "Title only in this passage; keep separate from the indexed Duchess."),
    ("carlisle_name", 35, "Carlisle", "carlisle", "Completes the Lord Carlisle mention begun on L34; provisional index crosswalk remains for S3."),
    ("country_houses", 35, "their great country houses", "whig_country_houses", "Unidentified houses as a group; p.279 supplies further named examples."),
    ("vanbrugh", 35, "Vanbrugh", "vanbrugh", "Reuse the indexed architect candidate."),
    ("aristocracy", 35, "a revived feudal aristocracy", "revived_feudal_aristocracy", "Haskell's interpretation of the emerging English order."),
    ("england", 35, "England", "england_polity", "Political realm governed by the aristocracy in Haskell's account."),
    ("venetian_oligarchy", 35, "the Venetian oligarchy", "venetian_oligarchy", "Political-social structure used in Haskell's analogy; distinct from Venice city and Republic."),
    ("doge", 35, "a Doge", "doge", "Reuse the existing office candidate; Haskell qualifies the Doge's powers as nominal."),
    ("whig_sons", 35, "their sons", "whig_sons", "Unidentified sons of the Whig noblemen; no individuals named."),
    ("sixteenth_century", 35, "sixteenth-century", "venice_city", "Time qualifier for the Venice reference continued on the next OCR line."),
    ("sixteenth_century_venice", 36, "Venice", "venice_city", "Completes the sixteenth-century Venice reference; exact city/republic aspect remains broad."),
    ("palladio", 36, "Palladio", "palladio", "Reuse the indexed architect candidate."),
    ("contemporary_venetians", 36, "the Venetians of their own day", "contemporary_venetians", "Contemporary people, not the city or Republic as an actor."),
    ("whig_these_men", 36, "these men", "whig_nobles", "Refers to the English Whig noblemen in the comparison."),
    ("england_country", 36, "their country", "england_polity", "Their refers to the English Whig noblemen."),
    ("continent", 36, "the Continent", "europe", "Unspecified continental source area; no country is inferred."),
    ("music", 36, "‘Music’", "music_in_english", "Subject named for the Duchess's letter quotation."),
    ("duchess", 36, "the Duchess of Marlborough", "duchess", "Reuse the page-278 index candidate; distinct from the Duke."),
    ("manchester_recipient", 36, "Lord Manchester", "manchester", "Recipient named in Haskell's introduction to the quotation."),
    ("music_england", 38, "England", "england_polity", "Setting for the hoped-for encouragement in the quoted letter."),
    ("italian_master", 39, "Italian", "italian_music_model", "Named as a musical model in the Duchess's analogy; preserve as her evaluation."),
    ("french_air", 39, "French air", "french_air", "Musical influence described by the Duchess; not a named composition."),
    ("painting", 39, "painting", "painting_analogy", "Art-form named in Haskell's analogy."),
    ("pellegrini_london", 40, "Pellegrini", "pellegrini", "Reuse the indexed person candidate."),
    ("ricci_london", 40, "Marco Ricci", "ricci", "Reuse the indexed person candidate."),
    ("london", 40, "London", "london", "City of arrival in the narrative."),
    ("manchester_lord", 40, "Lord", "manchester", "Title begins at the end of L40 and is completed as Lord Manchester at L41."),
    ("manchester_name", 41, "Manchester", "manchester", "Completes the Lord Manchester mention begun on L40."),
    ("scarlatti", 41, "Scarlatti", "scarlatti", "Reuse the page-278 index candidate."),
    ("opera_title", 41, "Pyrrhus and Demetrius", "scarlatti_opera", "Named opera, distinguished from the painted scenes prepared for it."),
    ("paint_scenes", 41, "paint scenes", "opera_scenes", "Unidentified painted scenes for the opera; the clause continues on p.279."),
]
for local_id, line_no, surface, key, note in MENTION_SPECS:
    add_mention(local_id, line_no, surface, C[key] if key in C else E[key], note)

new_statements = []


def quote_between(first: str, last: str):
    start = segment_text.find(first)
    if start < 0:
        raise SystemExit(f"quote start absent: {first!r}")
    end_start = segment_text.find(last, start)
    if end_start < 0:
        raise SystemExit(f"quote end absent after {first!r}: {last!r}")
    return segment_text[start : end_start + len(last)]


def add_statement(sid, line_start, line_end, subject, obj, predicate, quote, claim, qualification,
                  refs=(), relation=False, footnote=None, cross=(), previous_cross=(),
                  speaker="Haskell", text_layer="authorial narrative", ocr=(), continuation_of=None):
    if sid in statement_ids or any(row["statement_id"] == sid for row in new_statements):
        raise SystemExit(f"duplicate statement ID: {sid}")
    if quote not in segment_text:
        raise SystemExit(f"quote not anchored in p.278 source segment: {sid}")
    linked = set(refs) | {value for value in (subject, obj) if value}
    known = candidate_ids | {row["candidate_id"] for row in new_candidates}
    if not linked <= known:
        raise SystemExit(f"unknown candidate in {sid}: {sorted(linked - known)}")
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 278,
        "pdf_physical_page": 3,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": sorted(linked),
    }
    if relation:
        qualifiers["relation_candidate"] = True
    if footnote is not None:
        qualifiers.update({
            "footnote_marker": footnote,
            "footnote_text_pending": True,
            "footnote_link_status": "pending_source_migration",
        })
    references = []
    references.extend(
        {"segment_id": NEXT, "source_line_start": start, "source_line_end": end}
        for start, end in cross
    )
    references.extend(
        {"segment_id": PREVIOUS, "source_line_start": start, "source_line_end": end}
        for start, end in previous_cross
    )
    if references:
        qualifiers["cross_reference_segments"] = references
    if continuation_of:
        qualifiers["continuation_of_statement_id"] = continuation_of
    if ocr:
        qualifiers["ocr_corrections"] = [
            {
                "source_file": SOURCE_FILE,
                "source_line": line_no,
                "ocr": raw,
                "print": printed,
                "basis": "CHP-10.pdf physical page 3.",
            }
            for line_no, raw, printed in ocr
        ]
    new_statements.append({
        "statement_id": sid,
        "segment_id": SEGMENT,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "source_file": SOURCE_FILE,
        "origin": "book",
    })


add_statement(
    CLOSURE_ID, 27, 27, None, None, "english_and_german_patronage_tastes_diverged_for_other_commissions",
    quote_between("commissions there was a divergence of taste", "very pronounced."),
    "Haskell closes the p.277 contrast by saying that taste diverged over other, more important commissions and would soon become very pronounced.",
    "This closes the sentence begun on p.277 L24. The page states that tastes diverged but does not yet identify each commission or fully specify the nature of the divergence.",
    previous_cross=[(24, 24)], continuation_of=PREVIOUS_CLOSURE_ID,
    text_layer="continuation of authorial narrative",
)

add_statement(
    "st-chp10-p278-german-courts-art-from-italy-late-baroque", 28, 29, None, None,
    "german_courts_obtained_art_from_italy_and_kept_buying_familiar_late_baroque_pictures",
    quote_between("It has been seen that many German courts", "grown accustomed.1"),
    "Haskell says many German courts had obtained art from Italy for at least a generation and continued buying pictures in the late Baroque style to which they were accustomed.",
    "This is Haskell's historical summary. 'At least a generation' is preserved as phrased; late Baroque names the pictures' style, not the purchased object. Note 1 is a source trail and remains pending.",
    [c("german_courts"), e("italy"), c("late_baroque")], False, 1,
)
add_statement(
    "st-chp10-p278-powerful-courts-attract-artists", 29, 29, c("german_courts"), c("german_court_artists"),
    "powerful_german_courts_could_attract_the_artists_themselves",
    quote_between("The more powerful of them were able", "the artists themselves"),
    "Haskell says the more powerful German courts could attract the artists themselves.",
    "The antecedent of 'them' is the German courts. The artists are an unnamed group.",
    [], True,
)
add_statement(
    "st-chp10-p278-powerful-courts-attract-artists-pictures", 29, 29, c("german_courts"), c("german_court_artists_pictures"),
    "powerful_german_courts_could_attract_artists_and_their_pictures",
    quote_between("The more powerful of them were able", "as well as their pictures."),
    "Haskell says the more powerful German courts could attract pictures associated with the artists as well as the artists themselves.",
    "The pictures are unnamed and not individually identifiable in this passage; no specific painting is asserted.",
    [c("german_court_artists")], True,
)
add_statement(
    "st-chp10-p278-hapsburgs-summon-bombelli", 29, 30, c("hapsburg_authority"), e("bombelli"),
    "hapsburg_authority_summoned_bombelli_to_vienna",
    quote_between("The Hapsburgs summoned", "to Vienna,"),
    "Haskell says the Hapsburgs summoned Sebastiano Bombelli to Vienna.",
    "Preserve the source's plural actor. Its dynastic, court, or political-institution scope remains unresolved; no appointment beyond summoning is stated.",
    [e("vienna")], True,
)
add_statement(
    "st-chp10-p278-bellucci-court-painter", 30, 30, c("hapsburg_authority"), e("bellucci"),
    "hapsburg_authority_employed_bellucci_as_court_painter_in_1709",
    quote_between("in 1709 employed Antonio Bellucci", "court painter."),
    "Haskell says the Hapsburgs employed Antonio Bellucci as their court painter in 1709.",
    "The possessive 'their' refers to the Hapsburg actor, whose exact institutional or dynastic boundary remains open.",
    [], True,
)
add_statement(
    "st-chp10-p278-bencovich-followed-to-vienna", 30, 30, e("bencovich"), e("vienna"),
    "bencovich_followed_them_to_vienna_in_1716",
    quote_between("In 1716 the Dalmatian Federico Bencovich", "followed them there.2"),
    "Haskell says Federico Bencovich followed 'them' to Vienna in 1716.",
    "The place reference 'there' is Vienna. The plural antecedent of 'them' is not certain from this sentence; do not infer employment by the Hapsburgs or membership in a particular artist group. Printed note 2 remains pending.",
    [e("hapsburg_empire"), e("bellucci"), e("bombelli")], True, 2,
)
add_statement(
    "st-chp10-p278-diziani-augustus-scene-painter", 30, 31, e("diziani"), e("augustus_strong"),
    "diziani_worked_for_augustus_the_strong_as_scene_painter_for_three_years_from_1717",
    quote_between("Gaspare\nDiziani went to Dresden", "Augustus the Strong.3"),
    "Haskell says Gaspare Diziani went to Dresden in 1717 and worked for three years as scene painter for Augustus the Strong.",
    "The page-278 index candidate is used provisionally for the title Augustus the Strong; global identity resolution remains S3. Note 3 is pending.",
    [e("dresden")], True, 3,
)
add_statement(
    "st-chp10-p278-amigoni-max_emmanuel", 31, 32, c("amigoni"), e("max_emmanuel"),
    "amigoni_was_painting_for_elector_max_emmanuel_at_munich",
    quote_between("By this time Giacomo Amigoni", "Elector Max Emmanuel"),
    "Haskell says Giacomo Amigoni was already in Munich painting for Elector Max Emmanuel.",
    "The passage does not name a particular painting or commission. The body-only Amigoni candidate is left for S3 comparison with same-name index entries.",
    [e("munich")], True,
)
add_statement(
    "st-chp10-p278-amigoni-french-craftsmen-nymphenburg", 31, 32, c("amigoni"), c("french_craftsmen"),
    "amigoni_worked_alongside_french_craftsmen_in_nymphenburg_rococo_pavilions",
    quote_between("and working alongside French craftsmen", "Nymphenburg gardens.4"),
    "Haskell says Amigoni worked alongside French craftsmen in the rococo pavilions of the Nymphenburg gardens.",
    "The source names no individual craftsman or pavilion. Note 4's date and cited works remain pending; the gardens and pavilions are separate place candidates.",
    [c("rococo_pavilions"), c("nymphenburg_gardens")], True, 4,
)
add_statement(
    "st-chp10-p278-english-patrons-enable-venetian-artists", 33, 33, c("english_patrons"), e("venetian_artists"),
    "english_patronage_made_leaving_venice_worthwhile_for_venetian_artists",
    quote_between("The English too made it worthwhile", "leave their native country,"),
    "Haskell says English patrons made it worthwhile for Venetian artists to leave their native country.",
    "A broad authorial comparison, not evidence that every English patron hired every Venetian artist.",
    [e("venice_city")], True,
)
add_statement(
    "st-chp10-p278-english-german-austrian-patronage-difference", 33, 34, c("english_patrons"), c("autocratic_princes"),
    "english_patrons_differed_from_autocratic_south_german_and_austrian_princes",
    quote_between("but as patrons they were very different", "Germany or Austria."),
    "Haskell contrasts English patrons with autocratic princes of South Germany or Austria.",
    "Preserve the author's comparison and its geographic scope; it does not name the individual princes.",
    [c("south_germany"), e("austria")],
)
add_statement(
    "st-chp10-p278-manchester-brings-back-ricci-pellegrini-1709", 34, 34, e("manchester"), e("ricci"),
    "manchester_brought_back_ricci_and_pellegrini_from_venice_embassy_in_1709",
    quote_between("Lord Manchester, who brought back Marco Ricci and Pellegrini", "from his embassy to Venice in 1709,"),
    "Haskell says Lord Manchester brought Marco Ricci and Pellegrini back from his embassy to Venice in 1709; this statement records the Marco Ricci endpoint.",
    "The same clause names Pellegrini, recorded separately as the second endpoint. This conflicts chronologically with p.276's account of a 1707 visit followed by departure 'a year later' with the artists. Preserve both book statements; do not reconcile them during S2.",
    [e("pellegrini"), e("venice_city")], True,
    cross=(), previous_cross=[(11, 12)],
)
add_statement(
    "st-chp10-p278-manchester-1709-embassy", 34, 34, e("manchester"), c("manchester_1709_embassy"),
    "manchester_embassy_to_venice_was_in_1709_in_haskells_account",
    quote_between("his embassy to Venice in 1709", "his embassy to Venice in 1709"),
    "Haskell describes the Venice embassy from which Manchester returned with the artists as occurring in 1709.",
    "P.276 describes a 1707 second official visit and departure 'a year later'; whether this is the same event is unresolved. Preserve both source accounts and do not normalize the date.",
    [e("venice_city")], True, previous_cross=[(11, 12)],
)
add_statement(
    "st-chp10-p278-manchester-brings-back-pellegrini-1709", 34, 34, e("manchester"), e("pellegrini"),
    "manchester_brought_back_pellegrini_from_venice_embassy_in_1709",
    quote_between("Lord Manchester, who brought back Marco Ricci and Pellegrini", "from his embassy to Venice in 1709,"),
    "Haskell says Lord Manchester brought Pellegrini back from his embassy to Venice in 1709.",
    "This clause also names Marco Ricci, which is recorded in a separate relation-candidate statement. The date conflicts with p.276's 'a year later' departure account; preserve both without reconciliation.",
    [e("ricci"), e("venice_city")], True, previous_cross=[(11, 12)],
)
add_statement(
    "st-chp10-p278-manchester-profile-and-social-circle", 34, 34, e("manchester"), c("dilettantes_poets"),
    "manchester_was_a_cultivated_diplomat_and_was_close_to_dilettantes_and_poets",
    quote_between("was a cultivated diplomat", "poets.6"),
    "Haskell describes Manchester as a cultivated, widely experienced diplomat, a passionate opera lover, and closely connected to an influential group of dilettantes and poets.",
    "The group is unnamed. The OCR footnote marker after 'poets' reads 6, but the scan prints 5; note 5 is pending. These descriptions are Haskell's account.",
    [], True, 5, ocr=[(34, "6", "5")],
)
add_statement(
    "st-chp10-p278-manchester-member-whig-society", 34, 34, e("manchester"), c("whig_nobles"),
    "manchester_belonged_to_society_of_whig_noblemen",
    quote_between("He belonged to that society of Whig noblemen", "society of Whig noblemen"),
    "Haskell says Lord Manchester belonged to a society of Whig noblemen.",
    "He refers to Manchester. The collective is described further in separate statements for its political activity and relation to the unnamed new dynasty.",
    [], True,
)
add_statement(
    "st-chp10-p278-whigs-consolidated-victory-1688", 34, 34, c("whig_nobles"), c("whig_victory_1688"),
    "whig_noblemen_consolidated_their_1688_victory_over_the_king",
    quote_between("who were consolidating their victory of 1688", "over the King"),
    "Haskell says the Whig noblemen were consolidating their victory of 1688 over the King.",
    "Their refers to the Whig noblemen. The King is identified only by title here; preserve this as Haskell's historical framing and do not infer identity at S2.",
    [c("unnamed_king")], True,
)
add_statement(
    "st-chp10-p278-whigs-secured-new-dynasty-support", 34, 34, c("whig_nobles"), c("new_dynasty"),
    "whig_noblemen_sought_to_make_new_dynasty_depend_on_their_support",
    quote_between("and making sure that the new dynasty", "for support."),
    "Haskell says the Whig group was making sure the new dynasty should look to them for support.",
    "Them refers to the Whig noblemen. The dynasty is unnamed; retain Haskell's prospective wording without identifying its members.",
    [], True,
)
add_statement(
    "st-chp10-p278-manchester-friends-country-houses-vanbrugh", 34, 35, c("manchester_friends_group"), c("whig_country_houses"),
    "manchester_and_friends_had_great_country_houses_built_by_vanbrugh",
    quote_between("He and his friends, the Duke of Marlborough", "gentleman-architect Vanbrugh"),
    "Haskell says Manchester and his friends, including the Duke of Marlborough and Lord Carlisle, were having great country houses built for them by Vanbrugh.",
    "He refers to Manchester. The sentence presents the houses collectively and does not enumerate each building or state an individual commission for every named friend.",
    [e("manchester"), c("duke_marlborough"), e("carlisle"), e("vanbrugh")], True,
)
add_statement(
    "st-chp10-p278-vanbrugh-built-friends-country-houses", 34, 35, e("vanbrugh"), c("whig_country_houses"),
    "vanbrugh_built_country_houses_for_manchester_and_his_friends",
    quote_between("their great country houses built for them by the gentleman-architect Vanbrugh", "Vanbrugh"),
    "Haskell identifies Vanbrugh as the architect building the unnamed country houses for Manchester and his friends.",
    "The houses are not individually identified on p.278; the sentence continues with specific examples on p.279. This statement records the builder-to-building relation candidate.",
    [e("manchester"), c("manchester_friends_group")], True,
)
add_statement(
    "st-chp10-p278-whigs-foundations-feudal_aristocracy", 35, 35, c("manchester_friends_group"), c("revived_feudal_aristocracy"),
    "whig_nobles_laid_foundations_of_revived_feudal_aristocracy_governing_england",
    quote_between("and were laying the foundations", "over a century."),
    "Haskell says Manchester and his friends were laying the foundations of a revived feudal aristocracy that would govern England for over a century.",
    "This is Haskell's social-historical interpretation and projected duration, not an independently verified institutional finding.",
    [e("england_polity")], True,
)
add_statement(
    "st-chp10-p278-whigs-venetian-oligarchy-analogy", 35, 35, c("manchester_friends_group"), c("venetian_oligarchy"),
    "whig_nobles_resembled_venetian_oligarchy_ruled_by_doge_with_nominal_powers",
    quote_between("In some ways they resembled", "nominal powers,"),
    "Haskell says the English group resembled the Venetian oligarchy, ruled by a Doge with little more than nominal powers.",
    "The explicit 'in some ways' marks an analogy, not identity between the English and Venetian governments. Doge authority is described as nominal by Haskell.",
    [e("doge")],
)
add_statement(
    "st-chp10-p278-whig-sons-admired-venice-and-palladio", 35, 36, c("whig_sons"), e("palladio"),
    "whig_noblemen_sons_admired_sixteenth_century_venice_and_palladio",
    quote_between("and it is not surprising that their sons", "their own ambitions and tastes."),
    "Haskell says it is not surprising that their sons should have looked back admiringly to sixteenth-century Venice and Palladio as embodiments of their ambitions and tastes.",
    "Their refers to Manchester and his friends. Preserve the modal 'should have' as Haskell's rhetorical expectation; no individual son is named or independently shown to hold this view.",
    [e("venice_city")], True,
)
add_statement(
    "st-chp10-p278-whigs-optimistic-about-england", 36, 36, c("manchester_friends_group"), e("england_polity"),
    "english_whig_nobles_were_optimistic_about_englands_future_prestige_and_wealth",
    quote_between("Unlike the Venetians of their own day", "unparalleled prestige and riches."),
    "Haskell describes the English men as optimistic and aware that their country was entering an age of unprecedented prestige and riches.",
    "The text contrasts the Whig noblemen with unnamed contemporary Venetians; this is Haskell's characterization, not a measured forecast.",
    [c("contemporary_venetians")],
)
add_statement(
    "st-chp10-p278-whigs-borrow-from-continent", 36, 36, c("manchester_friends_group"), e("europe"),
    "english_whig_nobles_could_borrow_from_continent_while_confident_in_future",
    quote_between("They could afford to borrow from the Continent", "the future lay with them."),
    "Haskell says the men could borrow from the Continent while remaining confident that the future lay with them.",
    "They refers to the English men; the passage does not specify which cultural forms were borrowed in this sentence.",
)
add_statement(
    "st-chp10-p278-duchess-wrote-manchester-music-letter", 36, 36, e("duchess"), c("duchess_letter"),
    "duchess_of_marlborough_wrote_music_letter_to_lord_manchester",
    quote_between("‘Music’, wrote the Duchess of Marlborough", "Lord Manchester,6"),
    "Haskell introduces the following words as a letter from the Duchess of Marlborough to Lord Manchester about music.",
    "The letter is quoted through Haskell. Printed note 6 is pending and will be assessed with the canonical page-note segment.",
    [e("manchester")], True, 6,
    speaker="Haskell", text_layer="letter identification in authorial narrative",
)
add_statement(
    "st-chp10-p278-duchess-music-nonage-and-encouragement", 37, 39, c("music_in_english"), e("england_polity"),
    "duchess_described_music_as_young_and_hopeful_if_english_masters_received_encouragement",
    quote_between("‘is yet in its nonage", "more encouragement."),
    "In the quotation Haskell attributes to the Duchess, music is a froward child whose future in England holds promise if its masters receive more encouragement.",
    "Nested letter quotation reported by Haskell; the letter itself is not independently consulted. Preserve the metaphor and conditional wording.",
    [c("duchess_letter")], speaker="Duchess of Marlborough", text_layer="nested letter quotation reported by Haskell",
)
add_statement(
    "st-chp10-p278-duchess-music-italian-french-influence", 37, 39, c("music_in_english"), c("french_air"),
    "duchess_described_music_as_learning_from_italian_and_french_models",
    quote_between("It is now learning", "gaiety and fashion.’"),
    "The quoted Duchess says music is learning the Italian model, which she calls the best master, and studying a little of the French air for gaiety and fashion.",
    "The evaluation and personification belong to the quoted speaker; retain the quotation layer and do not turn the metaphor into an external historical fact.",
    [c("italian_music_model"), c("french_air"), c("duchess_letter")], speaker="Duchess of Marlborough",
    text_layer="nested letter quotation reported by Haskell",
)
add_statement(
    "st-chp10-p278-haskell-painting-analogy", 39, 39, c("painting_analogy"), c("music_in_english"),
    "haskell_compared_painting_to_the_musical_development_just_described",
    quote_between("So too with painting.", "So too with painting."),
    "Haskell briefly says the analogy also applies to painting.",
    "Authorial transition following a nested letter quotation; do not attribute the phrase to the Duchess.",
)
add_statement(
    "st-chp10-p278-manchester-sets-pellegrini-opera-scenes", 40, 41, e("manchester"), e("pellegrini"),
    "manchester_set_pellegrini_to_paint_scenes_for_scarlatti_opera",
    quote_between("When Pellegrini and Marco Ricci arrived in London", "and then to"),
    "Haskell says Pellegrini arrived in London with Marco Ricci and was set by Lord Manchester to paint scenes for Scarlatti's opera Pyrrhus and Demetrius.",
    "This statement isolates Pellegrini's assignment; Ricci's is recorded separately. The clause does not establish that the scenes were completed or survive, and 'set by' is retained without deciding whether it denotes employment or commission. The sentence continues on p.279 L44.",
    [e("ricci"), e("london"), c("opera_scenes"), e("scarlatti"), c("scarlatti_opera")],
    True, cross=[(44, 44)],
)
add_statement(
    "st-chp10-p278-manchester-sets-ricci-opera-scenes", 40, 41, e("manchester"), e("ricci"),
    "manchester_set_ricci_to_paint_scenes_for_scarlatti_opera",
    quote_between("When Pellegrini and Marco Ricci arrived in London", "and then to"),
    "Haskell says Marco Ricci arrived in London with Pellegrini and was set by Lord Manchester to paint scenes for Scarlatti's opera Pyrrhus and Demetrius.",
    "This statement isolates Ricci's assignment; Pellegrini's is recorded separately. The clause does not establish that the scenes were completed or survive, and 'set by' is retained without deciding whether it denotes employment or commission. The sentence continues on p.279 L44.",
    [e("pellegrini"), e("london"), c("opera_scenes"), e("scarlatti"), c("scarlatti_opera")],
    True, cross=[(44, 44)],
)

previous_statement = next(row for row in statements if row["statement_id"] == PREVIOUS_CLOSURE_ID)
if previous_statement["predicate"] != "unfinished_contrast_about_other_and_more_important_commissions":
    raise SystemExit("p.277 contrast statement has changed; inspect before updating")
previous_qualifiers = previous_statement["qualifiers"]
previous_qualifiers.update({
    "claim": "The p.277 contrast concludes that taste diverged over other, more important commissions and would soon become very pronounced.",
    "text_layer": "authorial narrative",
    "qualification": "The sentence continues at p.278 L27, which closes it. Preserve the widening taste divergence without inferring specific commissions or parties beyond the surrounding comparison.",
})
previous_qualifiers["continued_by_statement_ids"] = [CLOSURE_ID]
previous_statement["predicate"] = "english_and_german_patronage_tastes_diverged_for_other_commissions"

coverage_by_id[PREVIOUS].update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L15-24",
    "note": "Printed p.277 body read against CHP-10.pdf physical page 2. The unfinished contrast at L24 is now closed by p.278 L27 and linked to st-chp10-p278-taste-divergence-closure; the page body is complete. Printed p.277 notes 1-5 remain pending in canonical L495-499. Preserve the printed unusual 'not-an.' punctuation and the S2-only removal of the stray OCR apostrophe at L21. Index/body identity decisions remain for S3.",
})
coverage_by_id[SEGMENT].update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "source_line_ranges": "L26-41",
    "note": "Printed p.278 body read against CHP-10.pdf physical page 3. Closed p.277 L24's unfinished taste-divergence clause at L27. Recorded German-court purchases and artist recruitment; Hapsburg summons/employment; Bencovich's ambiguous 'them'; Diziani's Dresden work; Amigoni at Munich/Nymphenburg; the English/Whig comparison; Manchester's 1709 embassy statement, social circle and architect-patronage context; the Duchess's nested music letter; and the assignment of Pellegrini/Ricci to paint scenes for Scarlatti's Pyrrhus and Demetrius. The p.276 'a year later' departure chronology and p.278 1709 embassy chronology remain unreconciled. The OCR marker after 'poets' is 6, but the scan prints 5; correction is recorded in S2 only. Printed p.278 notes 1-6 remain pending at canonical L500-505. L41's 'and then to' continues at p.279 L44, so this segment remains partial.",
})

if len({row["candidate_id"] for row in candidates + new_candidates}) != len(candidates) + len(new_candidates):
    raise SystemExit("duplicate candidate ID")
if len({row["mention_id"] for row in mentions + new_mentions}) != len(mentions) + len(new_mentions):
    raise SystemExit("duplicate mention ID")
if len({row["statement_id"] for row in statements + new_statements}) != len(statements) + len(new_statements):
    raise SystemExit("duplicate statement ID")

summary = {
    "segment": SEGMENT,
    "previous": PREVIOUS,
    "next": NEXT,
    "p277_status_after": "reviewed/complete",
    "p278_status_after": "reviewed/partial",
    "new_candidates": len(new_candidates),
    "candidate_ids": [row["candidate_id"] for row in new_candidates],
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "updated_previous_statement": PREVIOUS_CLOSURE_ID,
    "notes_pending": "p.278 printed footnotes 1-6 are consolidated at canonical L500-505",
    "cross_page": "p.278 L41 'and then to' continues at p.279 L44",
    "counts_after": {
        "candidates": len(candidates) + len(new_candidates),
        "mentions": len(mentions) + len(new_mentions),
        "statements": len(statements) + len(new_statements),
        "coverage_complete": sum(row["migration_status"] == "complete" for row in coverage),
        "coverage_partial": sum(row["migration_status"] == "partial" for row in coverage),
        "coverage_queued": sum(row["disposition"] == "queued" for row in coverage),
    },
}
print(json.dumps(summary, ensure_ascii=False, indent=2))

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
if args.apply:
    paths = [candidate_path, mention_path, statement_path, coverage_path]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("recovery backup already exists; inspect before retrying")
    for source, backup in zip(paths, backups):
        shutil.copy2(source, backup)
    try:
        write_csv_atomic(candidate_path, candidate_fields, candidates + new_candidates)
        write_csv_atomic(mention_path, mention_fields, mentions + new_mentions)
        write_jsonl_atomic(statement_path, statements + new_statements)
        write_csv_atomic(coverage_path, coverage_fields, coverage)
    except Exception:
        for target, backup in zip(paths, backups):
            shutil.copy2(backup, target)
        raise
    print("APPLIED; recovery backups retained: " + ", ".join(path.name for path in backups))
else:
    print("DRY RUN: no S2 table rows written")
