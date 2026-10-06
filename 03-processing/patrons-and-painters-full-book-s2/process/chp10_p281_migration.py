"""Controlled S2 migration for printed p.281; dry-run by default."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
PREVIOUS = "chp-10:10_CHP-10_intro:l51-61"
SEGMENT = "chp-10:10_CHP-10_intro:l125-139"
NEXT = "chp-10:10_CHP-10_intro:l141-149"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
SEGMENT_SHA = "7e689041c9b0207a52353811729a8bdc21d1b5c92a79bc80a67fcc0559aa98e8"
MAX_CANDIDATE = 8939
BACKUP_SUFFIX = ".bak-s2-chp10-p281-20261002"
OPEN_STATEMENT = "st-chp10-p280-sheffield-description-open"


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


def backup(path: Path):
    target = Path(str(path) + BACKUP_SUFFIX)
    if target.exists():
        raise SystemExit(f"backup already exists: {target}")
    shutil.copy2(path, target)
    return target


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != ASSET_SHA:
    raise SystemExit("Chapter 10 intro source asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[124:139])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("p.281 source segment hash mismatch")
if source_lines[124].strip() != "[Page 281]" or not source_lines[125].startswith("1712 as "):
    raise SystemExit("expected p.281 source text changed")
if "Queen Arme" not in source_lines[125] or "tfie-more" not in source_lines[136]:
    raise SystemExit("expected p.281 OCR text changed")
if not source_lines[138].endswith("serious revolt,"):
    raise SystemExit("expected open p.281 sentence changed")

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
for segment_id, expected in {
    PREVIOUS: ("reviewed", "partial"),
    SEGMENT: ("queued", "pending"),
    NEXT: ("queued", "pending"),
}.items():
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"unexpected coverage state for {segment_id}: {row}")

existing_open = next((row for row in statements if row["statement_id"] == OPEN_STATEMENT), None)
if not existing_open or existing_open["segment_id"] != PREVIOUS:
    raise SystemExit("p.280 Prince Eugene statement is missing or moved")
if existing_open["original_quote"] != "He was described by Prince Eugene in":
    raise SystemExit("p.280 Prince Eugene statement has unexpected source quote")

E = {
    "anne": "cand-0110", "sheffield": "cand-0465", "duchess": "cand-8930",
    "sheffield_house": "cand-8928", "dido": "cand-4163", "aeneas": "cand-4164",
    "bellucci": "cand-0282", "brydges": "cand-0647", "canons": "cand-0531",
    "handel": "cand-1288", "pepusch": "cand-1873", "bagutti": "cand-0161",
    "sleter": "cand-2439", "london": "cand-1422", "nativity": "cand-0284",
    "descent": "cand-0283", "instruments": "cand-5868", "pellegrini": "cand-1870",
    "ricci": "cand-2154", "dusseldorf": "cand-0955", "damini": "cand-0898",
    "leoni": "cand-1394", "palladianism": "cand-8921", "paris": "cand-4653",
    "palatinate": "cand-3947", "johann_wilhelm": "cand-1325", "louis_xiv": "cand-1447",
    "england": "cand-4439",
}
for key, candidate_id in E.items():
    if candidate_id not in candidate_ids:
        raise SystemExit(f"required existing candidate missing: {key}={candidate_id}")

CANDIDATE_SPECS = [
    ("edgware", "Edgware, location of Canons in Haskell's p.281 account", "place",
     "Locality given for James Brydges's acquisition of Canons; no more exact site is inferred.", 129),
    ("brydges_london_house", "Unidentified London house of James Brydges, 1st Duke of Chandos (p.281)", "place",
     "A second residence whose individual name and exact location are not supplied in this passage.", 131),
    ("canons_chapel", "Chapel at Canons decorated for James Brydges, 1st Duke of Chandos (p.281)", "place",
     "Interior space distinguished from the Canons estate/house as a whole.", 132),
    ("sheffield_staircase_scenes", "Bellucci's staircase wall scenes of Dido and Aeneas at Sheffield's London house (p.281)", "work",
     "Collective decorative work; the passage names mythological subjects but no individual scene titles.", 126),
    ("sheffield_allegorical_tribute", "Allegorical ceiling tribute to John Sheffield and his Duchess (p.281)", "work",
     "Unidentified decorative painting described in another room of Sheffield's mansion.", 127),
    ("canons_three_large_canvases", "Three large Bellucci canvases for the Canons chapel ceiling (p.281)", "work",
     "Collective group with three named subjects; the individual work identities should be resolved against the index at S3.", 132),
    ("canons_ascension", "The Ascension by Antonio Bellucci for the Canons chapel (p.281)", "work",
     "Disambiguated from other works titled The Ascension; only this Canons commission is asserted here.", 132),
    ("canons_small_canvases", "Twenty smaller canvases with putti holding Instruments of the Passion at Canons (p.281)", "work",
     "Collective group as described by Haskell; no individual subjects or present locations are supplied.", 132),
    ("venetian_history_painters", "Venetian history painters discussed as a group in England before c.1720 (p.281)", "term",
     "Authorial collective category, not a formal organization; includes named painters provisionally.", 134),
    ("english_elite_patron_class", "English elite patrons employing Venetian history painters before c.1720 (p.281)", "term",
     "Collective description of the rich, powerful, and leaders of fashion; no membership list is given.", 134),
    ("palatinate_revolt", "Unidentified serious revolt in Johann Wilhelm's state soon after 1690 (p.281)", "event",
     "The revolt is unnamed; its later course must be read in the p.282 continuation.", 139),
]
new_candidates = []
C = {}
for offset, (key, name, kind, detail, source_line) in enumerate(CANDIDATE_SPECS, 1):
    candidate_id = f"cand-{MAX_CANDIDATE + offset:04d}"
    if candidate_id in candidate_ids or any(row["canonical_name"] == name and row["suggested_type"] == kind for row in candidates):
        raise SystemExit(f"candidate ID/natural key exists: {candidate_id} {name}")
    C[key] = candidate_id
    new_candidates.append({
        "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open", "index_source_file": "",
        "sub_entry": "", "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L{source_line}",
    })

line_offsets = {}
offset = 0
for line_no in range(125, 140):
    line_offsets[line_no] = offset
    offset += len(source_lines[line_no - 1]) + 1
new_mentions = []


def add_mention(local_id, line_no, surface, candidate_id, note, occurrence=0):
    mention_id = f"m-chp10-p281-{local_id}"
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
        "mention_id": mention_id, "segment_id": SEGMENT, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start_char), "end_char": str(end_char), "note": note,
    })


MENTION_SPECS = [
    ("queen_anne", 126, "Queen Arme", "anne", "OCR reads Arme; print reads Anne."),
    ("anne_she", 126, "she", "anne", "Queen Anne, named immediately before."),
    ("sheffield_retired", 126, "he retired from politics", "sheffield", "John Sheffield; retirement follows Anne's death in Haskell's account."),
    ("sheffield_age", 126, "He was by then aged 67", "sheffield", "Pronoun refers to John Sheffield."),
    ("sheffield_affiliations", 126, "his political affiliations", "sheffield", "Pronoun refers to John Sheffield."),
    ("sheffield_mansion", 126, "his mansion", "sheffield_house", "The mansion begun in 1703, described in the preceding p.280 segment."),
    ("bellucci_staircase", 126, "Bellucci", "bellucci", "Painter employed at Sheffield's mansion."),
    ("dido", 126, "Dido", "dido", "Mythological subject of the staircase wall scenes."),
    ("aeneas", 126, "Aeneas", "aeneas", "Mythological subject paired with Dido."),
    ("sheffield_own_words", 126, "his own words", "sheffield", "The following ceiling description is directly attributed to Sheffield."),
    ("bellucci_tribute", 126, "Bellucci", "bellucci", "Painter of the ceiling tribute; second occurrence on this source line.", 1),
    ("sheffield_himself", 126, "himself", "sheffield", "Refers to John Sheffield in the allegorical tribute."),
    ("sheffield_duchess", 126, "his", "sheffield", "Possessive introducing Sheffield's Duchess.", 3),
    ("sheffield_duchess_title", 127, "Duchess", "duchess", "The unnamed Duchess is linked to Sheffield in p.280 as his third wife."),
    ("duchess_paid", 127, "she", "duchess", "Refers to the Duchess."),
    ("duchess_husband", 127, "her husband", "sheffield", "Refers to John Sheffield."),
    ("bellucci_patron", 128, "Bellucci’s", "bellucci", "The painter whose most important English patron is identified."),
    ("james_brydges", 128, "James Brydges", "brydges", "Indexed candidate for the first Duke of Chandos."),
    ("duke_of_chandos", 128, "Duke of Chandos", "brydges", "Title acquired in 1719; identity resolution remains for S3."),
    ("brydges_himself", 128, "himself", "brydges", "Refers to James Brydges."),
    ("brydges_birth_poverty", 128, "born in poverty", "brydges", "Biographical characterization of James Brydges."),
    ("brydges_he_acquired", 128, "he acquired", "brydges", "Pronoun refers to James Brydges."),
    ("canons", 129, "Canons", "canons", "Manor acquired by Brydges in 1713."),
    ("edgware", 129, "Edgware", "edgware", "Locality named as the location of Canons."),
    ("brydges_spent", 129, "he spent the next few years", "brydges", "Pronoun refers to James Brydges."),
    ("canons_palace", 129, "a vast palace", "canons", "Canons after Brydges's transformation."),
    ("handel", 129, "Handel", "handel", "Concert organizer at Canons in Haskell's account."),
    ("pepusch_dr", 129, "Dr", "pepusch", "Title immediately before Pepusch across an OCR line break."),
    ("pepusch", 130, "Pepusch", "pepusch", "Name completes the previous line's Dr."),
    ("canons_ceilings", 130, "Canons", "canons", "One of two locations whose state-room ceilings Bellucci painted."),
    ("brydges_his_house", 130, "his", "brydges", "Possessive refers to James Brydges."),
    ("brydges_london_house", 131, "London house", "brydges_london_house", "Second residence of James Brydges; no name supplied."),
    ("london", 131, "London", "london", "Geographic locator for the unnamed Brydges house."),
    ("bellucci_ceilings", 131, "Bellucci", "bellucci", "Painter of allegorical state-room ceilings."),
    ("bellucci_chapel", 131, "this artist", "bellucci", "Refers to Bellucci, named in the preceding line."),
    ("bagutti", 131, "Bagutti", "bagutti", "Bolognese stuccatore employed for the Canons chapel."),
    ("sleter", 132, "Francesco Sleter", "sleter", "Described by Haskell as a mysterious figure."),
    ("canons_chapel", 132, "the chapel", "canons_chapel", "Interior space at Canons; distinct from the manor."),
    ("bellucci_canvases", 132, "Bellucci", "bellucci", "Painter of the chapel canvases."),
    ("large_canvases", 132, "three large", "canons_three_large_canvases", "Number and scale of the first group of canvases."),
    ("small_canvases", 132, "twenty smaller canvases", "canons_small_canvases", "Second group of canvases in the chapel ceiling."),
    ("canons_rococo_ceiling", 132, "the rococo ceiling", "canons_chapel", "The architectural surface into which the canvases were let."),
    ("nativity", 132, "The Nativity", "nativity", "Indexed Bellucci work sub-entry; identity to be resolved at S3."),
    ("descent_cross", 132, "The Descent from the Cross", "descent", "Indexed Bellucci work sub-entry; identity to be resolved at S3."),
    ("ascension", 132, "The Ascension", "canons_ascension", "Bellucci work at Canons; keep distinct from similarly titled works."),
    ("instruments_passion", 133, "Instruments of the Passion", "instruments", "Iconographic objects held by putti; not a separate person or painting here."),
    ("venetian_history_painters", 134, "Venetian history painters", "venetian_history_painters", "Collective category used by Haskell; no formal organization is implied."),
    ("england", 134, "England", "england", "Geographical setting; current candidate type remains for later alignment review."),
    ("the_rich", 134, "The rich", "english_elite_patron_class", "Unnamed class of patrons."),
    ("powerfully_placed", 134, "the powerfully placed", "english_elite_patron_class", "Unnamed class of patrons."),
    ("leaders_fashion", 134, "the leaders of fashion", "english_elite_patron_class", "Unnamed class of patrons."),
    ("these_men", 134, "these men", "english_elite_patron_class", "Refers to the unnamed patrons just described."),
    ("artists_working", 134, "the artists who worked for them", "venetian_history_painters", "Collective artist group; 'them' refers to the unnamed patrons."),
    ("pellegrini", 134, "Pellegrini", "pellegrini", "Reuse page-relevant indexed candidate; cross-candidate identity remains for S3."),
    ("ricci", 134, "Ricci", "ricci", "Sebastiano Ricci in the English-work comparison."),
    ("bellucci_assessment", 134, "Bellucci", "bellucci", "Named as one of three painters whose English work is assessed."),
    ("pellegrini_left", 135, "Pellegrini", "pellegrini", "Artist who left England in 1712 for Düsseldorf."),
    ("england_pellegrini", 135, "England", "england", "Pellegrini's point of departure."),
    ("dusseldorf_pellegrini", 135, "Düsseldorf", "dusseldorf", "Destination of Pellegrini's 1712 move."),
    ("bellucci_arrived", 135, "Bellucci", "bellucci", "Artist who later arrived in London from Düsseldorf."),
    ("london_bellucci", 135, "London", "london", "Arrival city for Bellucci."),
    ("dusseldorf_bellucci", 135, "Düsseldorf", "dusseldorf", "Bellucci's point of departure.", 1),
    ("venetian_artists", 136, "Venetian artists", "venetian_history_painters", "Group label for Damini and Leoni."),
    ("england_artists", 136, "England", "england", "Destination of the two artists."),
    ("damini", 136, "Vincenzo Damini", "damini", "Described by Haskell as a minor painter."),
    ("leoni", 137, "Giacomo Leoni", "leoni", "Architect who helped inaugurate the Palladian movement, according to Haskell."),
    ("palladian_movement", 137, "the Palladian movement", "palladianism", "Reuse the related Palladianism candidate from p.280; exact concept identity remains for S3."),
    ("dusseldorf_center", 137, "Düsseldorf", "dusseldorf", "One of three named centers."),
    ("london_center", 137, "London", "london", "One of three named centers."),
    ("paris_center", 137, "Paris", "paris", "One of three named centers."),
    ("adventurous_artists", 137, "Venetian artists", "venetian_history_painters", "Haskell's grouping, not a formal organization."),
    ("town", 137, "The town", "dusseldorf", "Anaphoric reference to Düsseldorf."),
    ("palatinate", 137, "the Palatinate", "palatinate", "Electoral territory named by Haskell."),
    ("johann_wilhelm", 137, "Elector Johann Wilhelm", "johann_wilhelm", "Ruler of the Palatinate in Haskell's account."),
    ("johann_wilhelm_power", 139, "Johann Wilhelm", "johann_wilhelm", "Subject of the accession and revolt statements."),
    ("the_state", 139, "a state", "palatinate", "In context, the state ruled by Johann Wilhelm; source-bounded interpretation."),
    ("louis_xiv", 139, "Louis XIV", "louis_xiv", "Named ruler whose troops devastated the state, as Haskell says."),
    ("serious_revolt", 139, "a serious revolt", "palatinate_revolt", "Unnamed revolt; the narrative continues on p.282."),
]
for spec in MENTION_SPECS:
    local_id, line_no, surface, key, note, *occurrence = spec
    add_mention(local_id, line_no, surface, C[key] if key in C else E[key], note, occurrence[0] if occurrence else 0)


def quote_between(first: str, last: str):
    start = segment_text.find(first)
    if start < 0:
        raise SystemExit(f"quote start absent: {first!r}")
    end_start = segment_text.find(last, start)
    if end_start < 0:
        raise SystemExit(f"quote end absent after {first!r}: {last!r}")
    return segment_text[start:end_start + len(last)]


new_statements = []


def add_statement(sid, line_start, line_end, subject, obj, predicate, first, last, claim, qualification,
                  refs=(), relation=False, footnote=None, cross=(), speaker="Haskell",
                  text_layer="authorial narrative", ocr=()):
    if sid in statement_ids or any(row["statement_id"] == sid for row in new_statements):
        raise SystemExit(f"duplicate statement ID: {sid}")
    quote = quote_between(first, last)
    linked = set(refs) | {value for value in (subject, obj) if value}
    known = candidate_ids | {row["candidate_id"] for row in new_candidates}
    if not linked <= known:
        raise SystemExit(f"unknown candidate in {sid}: {sorted(linked - known)}")
    qualifiers = {
        "source_line_start": line_start, "source_line_end": line_end,
        "printed_page": 281, "pdf_physical_page": 10, "claim": claim,
        "speaker": speaker, "text_layer": text_layer, "qualification": qualification,
        "mentioned_candidate_ids": sorted(linked),
    }
    if relation:
        qualifiers["relation_candidate"] = True
    if footnote is not None:
        qualifiers.update({"footnote_marker": footnote, "footnote_text_pending": True,
                           "footnote_link_status": "pending_source_migration"})
    if cross:
        qualifiers["cross_reference_segments"] = [
            {"segment_id": NEXT, "source_line_start": start, "source_line_end": end}
            for start, end in cross
        ]
    if ocr:
        qualifiers["ocr_corrections"] = [
            {"source_file": SOURCE_FILE, "source_line": line_no, "ocr": raw, "print": printed,
             "basis": "CHP-10.pdf physical page 10."}
            for line_no, raw, printed in ocr
        ]
    new_statements.append({
        "statement_id": sid, "segment_id": SEGMENT, "subject_candidate_id": subject,
        "object_candidate_id": obj, "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote, "source_file": SOURCE_FILE, "origin": "book",
    })


add_statement(
    "st-chp10-p281-sheffield-favourite-anne", 126, 126, E["sheffield"], E["anne"],
    "sheffield_became_queen_annes_favourite", "He became a special favourite", "retired from politics.",
    "Haskell says John Sheffield became a special favourite of Queen Anne and retired from politics when she died.",
    "Favour and retirement are reported by Haskell; no formal appointment or precise retirement date is stated.",
    relation=True, ocr=[(126, "Arme", "Anne")],
)
add_statement(
    "st-chp10-p281-sheffield-social-position", 126, 126, E["sheffield"], None,
    "sheffield_was_67_and_had_acquired_influential_social_position", "He was by then aged 67", "position in society.",
    "Haskell says Sheffield was then 67 and had acquired a great and influential position in society despite his political affiliations.",
    "The age and social assessment are Haskell's account; 'by then' refers to the period after Anne's death.",
)
add_statement(
    "st-chp10-p281-bellucci-sheffield-staircase", 126, 126, E["bellucci"], C["sheffield_staircase_scenes"],
    "bellucci_painted_dido_and_aeneas_scenes_on_sheffield_mansion_staircase", "as his mansion neared completion", "Dido and Aeneas",
    "Haskell says Bellucci painted scenes of Dido and Aeneas on the staircase walls of Sheffield's mansion as it neared completion.",
    "The source names subjects but no individual picture titles; the mansion is the unidentified London house from p.280.",
    [E["sheffield"], E["sheffield_house"], E["dido"], E["aeneas"]], relation=True,
)
add_statement(
    "st-chp10-p281-sheffield-ceiling-description", 126, 126, E["sheffield"], None,
    "sheffield_described_ceiling_as_filled_with_gods_and_goddesses", "while the ceiling was", "gods and goddesses’,",
    "Haskell quotes Sheffield describing the ceiling as filled with figures of gods and goddesses.",
    "Nested direct quotation attributed to Sheffield by Haskell; room and individual figures are unidentified.",
    [E["sheffield_house"]], speaker="John Sheffield, quoted by Haskell",
    text_layer="nested first-person quotation",
)
add_statement(
    "st-chp10-p281-bellucci-allegorical-tribute", 126, 127, E["bellucci"], C["sheffield_allegorical_tribute"],
    "bellucci_painted_allegorical_tribute_to_sheffield_and_duchess", "on the ceiling of another room", "husband’s death.",
    "Haskell says Bellucci painted an allegorical tribute to Sheffield and his Duchess on another room's ceiling.",
    "The work is unidentified. 'She' refers to the Duchess and 'her husband' to Sheffield.",
    [E["sheffield"], E["duchess"], E["sheffield_house"]], relation=True,
)
add_statement(
    "st-chp10-p281-duchess-paid-tribute", 127, 127, E["duchess"], C["sheffield_allegorical_tribute"],
    "sheffield_duchess_paid_for_allegorical_tribute_in_year_of_his_death", "Duchess, which she paid for", "husband’s death.",
    "Haskell says Sheffield's Duchess paid for the allegorical ceiling tribute in the year of her husband's death.",
    "The Duchess is the unnamed woman linked to Sheffield as his third wife in p.280; no year is stated here.",
    [E["sheffield"]], relation=True,
)
add_statement(
    "st-chp10-p281-brydges-bellucci-patron", 128, 128, E["brydges"], E["bellucci"],
    "james_brydges_was_bellucci_most_important_english_patron", "Bellucci’s most important English patron", "James Brydges",
    "Haskell identifies James Brydges as Bellucci's most important English patron.",
    "This is Haskell's comparative assessment; the specific commissions follow.",
    relation=True,
)
add_statement(
    "st-chp10-p281-brydges-created-duke", 128, 128, E["brydges"], None,
    "brydges_created_first_duke_of_chandos_in_1719_at_age_46", "James Brydges", "at the age of 46.1",
    "Haskell says James Brydges was created first Duke of Chandos in 1719 at age 46.",
    "Retain Haskell's wording 'managed to get himself created'; note 1 is pending the consolidated notes segment.",
    footnote=1,
)
add_statement(
    "st-chp10-p281-brydges-fortune-paymaster", 128, 128, E["brydges"], None,
    "brydges_acquired_fortune_from_war_profiteering_after_eight_years_as_paymaster", "Though born in poverty", "Paymaster to the Forces.",
    "Haskell says Brydges, though born in poverty, acquired an immense fortune from war profiteering after eight years as Paymaster to the Forces.",
    "This is Haskell's characterization; no independent financial or office record is consulted here.",
)
add_statement(
    "st-chp10-p281-brydges-acquired-canons", 128, 129, E["brydges"], E["canons"],
    "brydges_acquired_canons_in_1713_and_transformed_it_into_palace", "In 1713 he acquired", "a vast palace",
    "Haskell says Brydges acquired the old Elizabethan manor of Canons at Edgware in 1713 and spent the next few years transforming it into a vast palace.",
    "The palace is Canons after rebuilding, not a separate named residence; no exact completion date is supplied.",
    [C["edgware"]], relation=True,
)
add_statement(
    "st-chp10-p281-brydges-canons-concerts", 129, 130, E["brydges"], E["canons"],
    "brydges_entertained_friends_at_canons_with_handel_pepusch_concerts", "he entertained his friends", "Pepusch.",
    "Haskell says Brydges entertained friends at Canons with magnificent concerts organised by Handel and Dr Pepusch.",
    "The passage gives no concert dates or programmes.",
    [E["handel"], E["pepusch"]], relation=True,
)
add_statement(
    "st-chp10-p281-bellucci-state-room-ceilings", 130, 131, E["bellucci"], E["canons"],
    "bellucci_painted_allegorical_ceilings_at_canons_and_brydges_london_house", "He had a number of ceilings", "allegorical subjects by Bellucci",
    "Haskell says Bellucci painted allegorical subjects on several state-room ceilings at Canons and Brydges's London house.",
    "The London house is unnamed and distinct from Canons; the passage gives neither exact room count nor subjects.",
    [C["brydges_london_house"], E["london"]], relation=True,
)
add_statement(
    "st-chp10-p281-bellucci-chandos-chapel-team", 131, 132, E["brydges"], C["canons_chapel"],
    "brydges_employed_bellucci_bagutti_sleter_to_decorate_canons_chapel", "above all, he employed this artist", "to decorate the chapel.",
    "Haskell says Brydges employed Bellucci, the Bolognese stuccatore Bagutti, and Francesco Sleter to decorate the chapel.",
    "The division of labour is not specified; Haskell calls Sleter a mysterious figure.",
    [E["bellucci"], E["bagutti"], E["sleter"], E["canons"]], relation=True,
)
add_statement(
    "st-chp10-p281-bellucci-canons-large-canvases", 132, 133, E["bellucci"], C["canons_three_large_canvases"],
    "bellucci_painted_three_large_canons_canvases_with_named_subjects", "Bellucci painted three large", "The Ascension,",
    "Haskell says Bellucci painted three large canvases for the Canons chapel ceiling, representing The Nativity, The Descent from the Cross, and The Ascension.",
    "The named subjects map provisionally to indexed candidates; exact identities and authorship alignment remain for S3.",
    [E["canons"], C["canons_chapel"], E["nativity"], E["descent"], C["canons_ascension"]],
    relation=True, footnote=2,
)
add_statement(
    "st-chp10-p281-bellucci-canons-small-canvases", 132, 133, E["bellucci"], C["canons_small_canvases"],
    "twenty_smaller_canvases_with_putti_and_instruments_of_passion_grouped_around_large_works", "twenty smaller canvases", "Instruments of the Passion.2",
    "Haskell describes twenty smaller canvases let into the rococo ceiling around the three large works, with putti holding Instruments of the Passion.",
    "The smaller canvases are not individually identified; 'around which' refers to the three large canvases.",
    [E["canons"], C["canons_chapel"], E["instruments"]], relation=True, footnote=2,
)
add_statement(
    "st-chp10-p281-english-support-venetian-painters", 134, 134, C["venetian_history_painters"], E["england"],
    "venetian_history_painters_received_wide_english_support_before_c1720", "Thus for a decade before about 1720", "wide support in England.",
    "Haskell says Venetian history painters received wide support in England for about a decade before c.1720.",
    "Approximate period and general pattern, not an exhaustive artist or patron list.",
    [C["english_elite_patron_class"]],
)
add_statement(
    "st-chp10-p281-patronage-and-mansions", 134, 134, C["english_elite_patron_class"], C["venetian_history_painters"],
    "english_elite_patron_groups_employed_venetian_painters_on_new_mansions", "The rich, the powerfully placed", "fruitful vitality.",
    "Haskell says wealthy, influential, and fashionable patrons employed Venetian painters on new mansions and interprets their freedom from long hereditary patronage traditions as inspiring artistic vitality.",
    "Broad authorial interpretation; the passage identifies neither all patrons nor a single causal mechanism.",
    relation=True,
)
add_statement(
    "st-chp10-p281-english-work-assessment", 134, 134, None, None,
    "historians_assessed_english_work_of_three_painters_as_their_greatest_achievements", "Most historians are agreed", "greatest achievements.",
    "Haskell reports a scholarly consensus that the English work of Pellegrini, Ricci, and Bellucci constituted their greatest achievements.",
    "The consensus is reported by Haskell; no individual historians or works are identified.",
    [E["pellegrini"], E["ricci"], E["bellucci"]], speaker="Haskell reporting unnamed historians",
    text_layer="authorial report of scholarly consensus",
)
add_statement(
    "st-chp10-p281-pellegrini-bellucci-dusseldorf-movements", 135, 135, E["pellegrini"], E["dusseldorf"],
    "pellegrini_left_england_1712_for_dusseldorf_bellucci_later_arrived_in_london_from_there", "When Pellegrini left England in 1712", "came from Düsseldorf.",
    "Haskell says Pellegrini went from England to Düsseldorf in 1712 and that Bellucci arrived in London a few years later from Düsseldorf.",
    "Bellucci's arrival date is approximate; the two artists' movements are distinct.",
    [E["england"], E["bellucci"], E["london"]], relation=True,
)
add_statement(
    "st-chp10-p281-damini-leoni-arrivals", 135, 137, E["damini"], E["england"],
    "damini_and_leoni_arrived_in_england_from_dusseldorf_damini_painter_leoni_architect", "When Bellucci arrived in London", "Palladian movement.",
    "Haskell says Vincenzo Damini and Giacomo Leoni also arrived in England from Düsseldorf, describing Damini as a minor painter and Leoni as an architect who helped inaugurate the Palladian movement.",
    "The text distinguishes Damini's and Leoni's professions; do not classify Leoni as a painter on this evidence.",
    [E["dusseldorf"], E["leoni"], E["palladianism"]], relation=True,
)
add_statement(
    "st-chp10-p281-european-centres-venetian-artists", 137, 137, C["venetian_history_painters"], None,
    "dusseldorf_london_paris_briefly_centres_for_adventurous_venetian_artists", "In fact, for a short time", "adventurous Venetian artists.",
    "Haskell says Düsseldorf, London, and Paris were briefly among the great centres for more adventurous Venetian artists.",
    "The duration is qualified as short; 'great centres' is Haskell's assessment.",
    [E["dusseldorf"], E["london"], E["paris"]],
    ocr=[(137, "tfie-more", "the more")],
)
add_statement(
    "st-chp10-p281-johann-wilhelm-palatinate-patron", 137, 138, E["johann_wilhelm"], E["palatinate"],
    "dusseldorf_capital_of_palatinate_under_johann_wilhelm_and_haskell_assesses_him_as_major_patron", "The town was the capital", "eighteenth century.",
    "Haskell says Düsseldorf was the Palatinate's capital under Elector Johann Wilhelm and calls him the most interesting German art patron of the first two decades of the eighteenth century.",
    "The superlative is Haskell's evaluative judgment, not an independent ranking.",
    [E["dusseldorf"]], relation=True,
)
add_statement(
    "st-chp10-p281-johann-wilhelm-accession-revolt", 139, 139, E["johann_wilhelm"], C["palatinate_revolt"],
    "johann_wilhelm_came_to_power_1690_in_war_devastated_state_and_was_forced_to_quell_revolt", "Johann Wilhelm came to power in 1690", "a serious revolt,",
    "Haskell says Johann Wilhelm came to power in 1690 in a state devastated by Louis XIV's troops and was almost at once forced to quell a serious revolt.",
    "The revolt is unnamed and the sentence continues on p.282; read and link its continuation before closing coverage.",
    [E["palatinate"], E["louis_xiv"]], relation=True, cross=[(142, 142)],
)

# Close the Prince Eugene report in place so all existing references remain stable.
continuation = source_lines[125].split(" He became", 1)[0]
existing_open["predicate"] = "reported_characterization_of_sheffield_by_prince_eugene"
existing_open["qualifiers"]["continuation_quote"] = continuation
existing_open["qualifiers"]["claim"] = (
    "Haskell reports that Prince Eugene described John Sheffield in 1712 as 'a sanguine man, but of great parts and esteemed a true patriot.'"
)
existing_open["qualifiers"]["text_layer"] = "nested reported characterization"
existing_open["qualifiers"]["qualification"] = (
    "The judgement is attributed to Prince Eugene through Haskell; print corrects the merged OCR 'andesteemed' to 'and esteemed'."
)
existing_open["qualifiers"]["cross_reference_segments"] = [
    {"segment_id": SEGMENT, "source_line_start": 126, "source_line_end": 126}
]
existing_open["qualifiers"]["ocr_corrections"] = [{
    "source_file": SOURCE_FILE, "source_line": 126, "ocr": "andesteemed", "print": "and esteemed",
    "basis": "CHP-10.pdf physical page 10.",
}]

coverage_by_id[PREVIOUS]["migration_status"] = "complete"
coverage_by_id[PREVIOUS]["note"] += (
    " Closed the Prince Eugene description begun at L61 with its continuation at p.281 L126 after Plates 49-52; "
    "the existing statement was completed in place with cross-page provenance retained."
)
coverage_by_id[SEGMENT]["disposition"] = "reviewed"
coverage_by_id[SEGMENT]["migration_status"] = "partial"
coverage_by_id[SEGMENT]["source_line_ranges"] = "L126-139"
coverage_by_id[SEGMENT]["note"] = (
    "Printed p.281 body read against CHP-10.pdf physical page 10. Completed the Prince Eugene characterization begun at p.280 L61; "
    "recorded Sheffield's favour under Queen Anne, retirement and social position; Bellucci's Sheffield-mansion decorations; "
    "James Brydges/Canons, its London house and chapel, Handel/Pepusch concerts, Bellucci-Bagutti-Sleter decoration and the "
    "Canons canvas programme; the English patronage context, Pellegrini/Ricci/Bellucci assessment, Düsseldorf-London movements, "
    "Damini and Leoni, and Johann Wilhelm's Palatinate rule. OCR corrections recorded in S2 only: L126 'Arme'->'Anne' and "
    "'andesteemed'->'and esteemed'; L137 'tfie-more'->'the more'; S0 remains unchanged. Footnote 1 at L128 and footnote 2 at "
    "L133 point to p.281 notes at source L518-L519 in the queued consolidated notes segment L491-634; note content remains pending. "
    "L139's revolt sentence continues at p.282 L142, so this segment remains partial."
)
coverage_by_id[NEXT]["note"] = (
    "Next source-order body segment; expected to continue the p.281 L139 sentence after 'a serious revolt,' at p.282 L142. "
    "Read and link the continuation before closing p.281 coverage."
)

new_candidates_final = candidates + new_candidates
new_mentions_final = mentions + new_mentions
new_statements_final = statements + new_statements
new_coverage_final = [coverage_by_id[row["segment_id"]] for row in coverage]

print(json.dumps({
    "mode": "APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN",
    "segment": SEGMENT,
    "new_candidates": len(new_candidates),
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "candidate_range": [new_candidates[0]["candidate_id"], new_candidates[-1]["candidate_id"]],
    "open_statement_completed_in_place": OPEN_STATEMENT,
    "coverage_updates": {
        PREVIOUS: [coverage_by_id[PREVIOUS]["disposition"], coverage_by_id[PREVIOUS]["migration_status"]],
        SEGMENT: [coverage_by_id[SEGMENT]["disposition"], coverage_by_id[SEGMENT]["migration_status"]],
        NEXT: [coverage_by_id[NEXT]["disposition"], coverage_by_id[NEXT]["migration_status"]],
    },
}, ensure_ascii=False, indent=2))

if sys.argv[-1:] != ["--apply"]:
    raise SystemExit(0)
for path in (candidate_path, mention_path, statement_path, coverage_path):
    backup(path)
write_csv_atomic(candidate_path, candidate_fields, new_candidates_final)
write_csv_atomic(mention_path, mention_fields, new_mentions_final)
write_jsonl_atomic(statement_path, new_statements_final)
write_csv_atomic(coverage_path, coverage_fields, new_coverage_final)
print("Applied p.281 S2 migration; backups retained.")
