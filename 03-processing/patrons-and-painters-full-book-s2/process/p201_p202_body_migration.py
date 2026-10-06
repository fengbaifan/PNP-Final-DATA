"""Controlled S2 migration for the body text on printed pp.201-202.

Default invocation is a read-only dry run. Source OCR remains unchanged; scan
corrections are recorded only in statement qualifiers.
"""
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
SOURCE_REL = "02-sources/02-Markdown/07_CHP-7_sec_v.md"
SOURCE_PATH = ROOT / SOURCE_REL
CANDIDATE_PATH = TABLES / "entity-candidates.csv"
MENTION_PATH = TABLES / "mentions.csv"
STATEMENT_PATH = TABLES / "book-statements.jsonl"
COVERAGE_PATH = TABLES / "s2-coverage.csv"
SEGMENT_PATH = TABLES / "segments.jsonl"
SEGMENT_IDS = {
    "p201": "chp-7:07_CHP-7_sec_v:l42-55",
    "p202": "chp-7:07_CHP-7_sec_v:l57-60",
}
EXPECTED_MAX_CANDIDATE = 7305
BACKUP_SUFFIX = ".bak-s2-chp7-p201-p202-body-20260930"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


source_lines = SOURCE_PATH.read_text(encoding="utf-8-sig").splitlines()
segment_records = read_jsonl(SEGMENT_PATH)
segments = {row["segment_id"]: row for row in segment_records}
if len(segments) != len(segment_records):
    raise SystemExit("segments.jsonl contains duplicate IDs")
for key, segment_id in SEGMENT_IDS.items():
    row = segments.get(segment_id)
    if row is None or row["source_file"] != SOURCE_REL:
        raise SystemExit(f"missing or unexpected segment: {segment_id}")
    if hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest() != row["asset_sha256"]:
        raise SystemExit("source asset fingerprint changed; rebuild segments and review")

candidate_fields, candidate_rows = read_csv(CANDIDATE_PATH)
mention_fields, mention_rows = read_csv(MENTION_PATH)
coverage_fields, coverage_rows = read_csv(COVERAGE_PATH)
statement_rows = read_jsonl(STATEMENT_PATH)
candidate_ids = {row["candidate_id"] for row in candidate_rows}
existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_statement_ids = {row["statement_id"] for row in statement_rows}
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}

for key, segment_id in SEGMENT_IDS.items():
    row = coverage_by_id.get(segment_id)
    if not row or row["disposition"] != "queued" or row["migration_status"] != "pending":
        raise SystemExit(f"expected queued/pending coverage: {segment_id}")
    if any(m["segment_id"] == segment_id for m in mention_rows):
        raise SystemExit(f"mentions already exist for {segment_id}; inspect before rerunning")
    if any(s["segment_id"] == segment_id for s in statement_rows):
        raise SystemExit(f"statements already exist for {segment_id}; inspect before rerunning")


def candidate(cid, name, typ, detail, line, sub_entry=""):
    return {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": typ, "status": "open",
        "index_source_file": "", "sub_entry": sub_entry, "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_IDS['p201'] if line <= 55 else SEGMENT_IDS['p202']}#L{line}",
    }


new_candidates = [
    candidate("cand-7306", "Prince Eugene's Winter Palace in Vienna", "place",
              "Building named in Haskell's p.201 account; this passage does not provide a formal architectural name or address.", 46),
    candidate("cand-7307", "The two Belvederes associated with Prince Eugene in Vienna", "place",
              "The pair of palaces named in Haskell's p.201 account; preserve as a pair until the specific Upper/Lower building references are resolved.", 46),
    candidate("cand-7308", "Marble Apotheosis by Balthasar Permoser", "work",
              "Sculpture described by Haskell as designed by Prince Eugene and executed by Permoser; no current location is supplied here.", 48),
    candidate("cand-7309", "Prince Eugene's dispersed collection of pictures", "",
              "Historical collection described as dispersed and as formerly containing Flemish primitives; retain as a source-derived candidate pending type and identity review.", 48),
    candidate("cand-7310", "Unidentified paintings commissioned by Marshal Caprara in Bologna", "work",
              "Haskell reports many commissions but names no individual pictures or complete count.", 43),
    candidate("cand-7311", "Unidentified frescoes in the Upper and Lower Belvederes", "work",
              "Collective work group painted by the Italian artists named in the passage; no subjects, rooms, or one-to-one artist assignments are supplied.", 50),
    candidate("cand-7312", "Unidentified statues made for Prince Eugene's hall and gardens", "work",
              "Haskell names Lorenzo Mattielli and Domenico Antonio Parodi but does not assign individual statues or precise sites.", 50),
    candidate("cand-7313", "Unidentified altarpieces sent by Francesco Solimena for the chapel", "work",
              "Collective works; the chapel's precise building and the altarpiece titles are not given in this passage.", 50),
    candidate("cand-7314", "Unidentified painting of Virgil writing the Aeneid commissioned from Giacomo Antonio Boni", "work",
              "Haskell calls the commission a 'portrait'; retain that wording and do not infer a surviving object, title, date, or location.", 51),
    candidate("cand-7315", "Prince Eugene's gallery in Vienna (site unspecified)", "place",
              "Gallery in which the passage says pictures were hung; the text does not identify it with the Winter Palace or either Belvedere.", 50),
    candidate("cand-7316", "Prince Eugene's chapel (building unspecified)", "place",
              "The chapel for which Solimena sent altarpieces; no precise palace or church is identified in this passage.", 50),
    candidate("cand-7317", "Liechtenstein family town palace in Vienna", "place",
              "Town palace that Domenico Martinelli came to build in 1691; keep distinct from the family's garden palace.", 54),
    candidate("cand-7318", "Liechtenstein family garden palace in Vienna", "place",
              "Garden palace whose hall ceiling Andrea Pozzo began painting in 1704; distinct from the town palace.", 54),
    candidate("cand-7319", "Hall in the Liechtenstein family's garden palace", "place",
              "Interior space named as the location of Pozzo's ceiling painting; no formal room name is supplied.", 54),
    candidate("cand-7320", "Ceiling painting begun by Andrea Pozzo in 1704 in the Liechtenstein garden palace", "work",
              "Unfinished or completed status is not stated; Haskell says Pozzo began to paint the hall ceiling in 1704.", 54),
    candidate("cand-7321", "Viennese palaces of the Italian-origin Imperial commanders (unnamed group)", "place",
              "The p.200 sentence continues here; the passage gives neither palace names nor individual commanders beyond its collective description.", 43),
    candidate("cand-7322", "Pictures from the commanders' native land intended for their Viennese palaces", "work",
              "Unidentified group of pictures in the p.200–201 continuation; no individual title, maker, or completed transfer is specified.", 43),
    candidate("cand-7323", "Venetian painters working in Vienna for other patrons (unnamed group)", "term",
              "Collective group only; the passage does not name its members or individual patronage acts.", 52),
    candidate("cand-7324", "Other Bolognese painters represented in Prince Eugene's gallery (unnamed group)", "term",
              "The passage names Crespi and dal Sole separately, then refers to many other Bolognese painters without enumerating them.", 50),
    candidate("cand-7325", "Other nobles commissioning Italian art in Vienna (unnamed group)", "term",
              "Haskell presents Prince Eugene as one among many; the other nobles and their individual commissions are not identified here.", 53),
    candidate("cand-7326", "New art collections being formed in Vienna (unnamed group)", "",
              "Aggregate collections named as recipients of pictures from Italy; keep type and membership unresolved rather than treating them as one institution.", 55),
    candidate("cand-7327", "Italian pictures arriving in Vienna's new collections (unidentified group)", "work",
              "Collective movement of pictures is described without titles, makers, quantities, or receiving collection names.", 55),
    candidate("cand-7328", "Painters travelling north to Germany who stopped to work in Vienna (unnamed group)", "term",
              "Haskell's collective travel claim; no individuals, dates, or works are supplied.", 54),
    candidate("cand-7329", "Sculptures made by Lorenzo Mattielli for aristocratic gardens (unidentified group)", "work",
              "Haskell describes sculpture for many aristocratic gardens without naming individual works or locations.", 54),
    candidate("cand-7330", "Vienna's feudal aristocracy (collective social group)", "term",
              "Collective social actor in Haskell's explanation of Vienna's cultural setting; membership is not supplied.", 55),
    candidate("cand-7331", "Vienna's all-powerful religious foundations (unnamed institutional group)", "institution",
              "Haskell's collective reference to religious foundations; no individual institution is named here.", 55),
    candidate("cand-7332", "Local artists in Turin (unnamed group)", "term",
              "The passage says local talent was rare but does not name individuals or define the group.", 59),
    candidate("cand-7333", "Painters who refused to travel to Turin (unnamed group)", "term",
              "Repeated refusals are described without naming artists, dates, or specific recruitment attempts.", 59),
    candidate("cand-7334", "Successive dukes of Savoy discussed in the Turin patronage account (unnamed group)", "term",
              "The passage generalizes about several dukes without naming each ruler or assigning an individual decision.", 59),
    candidate("cand-7335", "Patrons in other artistically uncreative centres (unnamed group)", "term",
              "Haskell compares Turin's policy with other centres but supplies no names in this passage.", 60),
    candidate("cand-7336", "Smaller provincial towns that preceded Turin's artist-attraction policy (unnamed group)", "term",
              "The passage says several towns anticipated Turin but defers their discussion; no towns are named here.", 60),
    candidate("cand-7337", "Unidentified Flemish primitive paintings formerly in Prince Eugene's collection", "work",
              "The source says the collection once contained these works but names no individual painting.", 48),
    candidate("cand-7338", "Italians of Prince Eugene's own time (unnamed audience group)", "term",
              "Haskell reports their contemporary perception of Eugene; no individual informants are named.", 49),
    candidate("cand-7339", "Italian painters and sculptors patronized by Prince Eugene (partially named group)", "term",
              "Collective category in Haskell's account; he says the named artists are only the most famous.", 49),
    candidate("cand-7340", "Prince Eugene's hall and gardens (specific residences unresolved)", "place",
              "Haskell mentions statues made for these spaces but does not identify the particular hall or gardens.", 50),
    candidate("cand-7341", "Neapolitan painters represented in Prince Eugene's gallery (named group)", "term",
              "The source applies the regional label to Giacomo del Po and Solimena; preserve that attribution without external identity claims.", 50),
    candidate("cand-7342", "Ancient poets used as subjects in Prince Eugene's preferred pictures (unnamed group)", "term",
              "Haskell names Virgil as the particular example but does not enumerate the other poets.", 51),
    candidate("cand-7343", "Aristocratic gardens where Mattielli made sculpture (unnamed group)", "place",
              "Haskell refers to many gardens without naming their owners or locations.", 54),
    candidate("cand-7344", "Leading painters attracted to Turin by Victor Amadeus and Juvarra (unnamed group)", "term",
              "The passage gives no names or individual recruitment outcomes in this clause.", 60),
    candidate("cand-7345", "Pictures of leading painters attracted to Turin (unidentified group)", "work",
              "Haskell says patrons attracted painters, or at least their pictures; no titles or source cities are specified.", 60),
    candidate("cand-7346", "Unidentified pictures by painters represented in the gallery passage", "work",
              "Collective gallery holdings are named by artist rather than title; the passage does not list individual pictures or formally name the gallery.", 50),
]
new_candidate_ids = {row["candidate_id"] for row in new_candidates}
if len(new_candidate_ids) != len(new_candidates) or new_candidate_ids & candidate_ids:
    raise SystemExit("planned candidate IDs collide")
if max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows) != EXPECTED_MAX_CANDIDATE:
    raise SystemExit("candidate ID boundary changed; review before assigning IDs")


mention_specs = [
    # p.201 continuation of the open p.200 sentence.
    ("their Viennese palaces", "cand-7321", "Continuation of the p.200 account of high Italian-origin commanders.", 43, 43),
    ("pictures", "cand-7322", "Unidentified pictures intended for the commanders' Viennese palaces.", 43, 43),
    ("Marshal Caprara", "cand-0538", "Existing index candidate.", 43, 43),
    ("many paintings", "cand-7310", "Unidentified paintings; the source gives no titles or count beyond 'many'.", 43, 43),
    ("Bologna", "cand-3398", "Existing source-derived city candidate; do not conflate city and polity.", 43, 43),
    ("Prince Eugene of\nSavoy", "cand-2385", "Index subentry for Prince Eugene's patronage on p.201; cross-line printed name.", 43, 44),
    ("Italy", "cand-3461", "Existing geographic candidate; Haskell's characterization concerns loyalty in peacetime arts.", 44, 44),
    ("Austria", "cand-7284", "Existing political-military candidate; keep distinct from the geographic place candidate.", 44, 44),
    ("Prince Eugene", "cand-2385", "Index subentry for p.201 patronage.", 45, 45),
    ("Europe", "cand-3462", "Existing place candidate; the author's superlative remains attributed.", 46, 46),
    ("Winter Palace", "cand-7306", "Unidentified palace named in this account.", 46, 46),
    ("Fischer von Erlach", "cand-0978", "Existing index candidate.", 46, 46),
    ("two Belvederes", "cand-7307", "Pair of buildings; avoid silently splitting the source's collective reference.", 46, 46),
    ("Lucas von Hildebrandt", "cand-1299", "Existing index candidate.", 47, 47),
    ("marble\nApotheosis", "cand-7308", "Unidentified sculpture described as designed by Prince Eugene and made by Permoser; the printed name crosses a source line.", 47, 48),
    ("Permoser", "cand-1880", "Existing index candidate for Balthasar Permoser.", 48, 48),
    ("he himself designed", "cand-2385", "Pronoun refers to Prince Eugene; claim is design attribution, not proof of execution.", 48, 48),
    ("his collection of pictures", "cand-7309", "Collection is an aggregate; type remains unresolved.", 48, 48),
    ("Flemish primitives", "cand-7337", "Unidentified group of pictures formerly contained in the collection.", 48, 48),
    ("Italians of his own time", "cand-7338", "Collective audience in Haskell's account; not a named institution.", 49, 49),
    ("Eugene", "cand-2385", "Existing p.201 patronage subentry.", 49, 49),
    ("Italian painters and sculptors", "cand-7339", "Collective category; no complete membership list is supplied.", 49, 49),
    ("Louis Dorigny", "cand-0944", "Existing index candidate with p.201 coverage.", 49, 49),
    ("Marc’antonio Chiarini", "cand-0662", "Existing index candidate; source capitalization retained.", 49, 49),
    ("Gaetano Fanti", "cand-0993", "Existing index candidate.", 50, 50),
    ("Carlo Carlone", "cand-0561", "Use the index entry for Carlo; do not merge with Gianandrea Carlone.", 50, 50),
    ("Italy", "cand-3461", "Country of origin stated for the artists.", 50, 50),
    ("frescoes", "cand-7311", "Collective, unidentified fresco works in the two Belvederes.", 50, 50),
    ("Upper and Lower Belvederes", "cand-7307", "Same pair as 'two Belvederes'; no individual room attribution supplied.", 50, 50),
    ("Lorenzo Mattielli", "cand-1584", "Existing index candidate.", 50, 50),
    ("Domenico Antonio Parodi", "cand-1841", "Existing index candidate; source gives full name in the same paragraph.", 50, 50),
    ("statues", "cand-7312", "Unidentified group of statues for the hall and gardens.", 50, 50),
    ("the hall and gardens", "cand-7340", "Prince Eugene's hall/gardens in context; exact buildings are not specified.", 50, 50),
    ("Solimena", "cand-2484", "Existing index candidate for Francesco Solimena; first occurrence, sending altar pieces.", 50, 50, 0),
    ("altarpieces", "cand-7313", "Unidentified works sent by Solimena.", 50, 50),
    ("the chapel", "cand-7316", "Unspecified chapel; do not assign to a named palace from context alone.", 50, 50),
    ("the gallery", "cand-7315", "Gallery site is not identified with a palace in the passage.", 50, 50),
    ("Crespi", "cand-0871", "Existing index candidate for Giuseppe Maria Crespi; his pictures are said to hang in the gallery.", 50, 50),
    ("pictures", "cand-7346", "Unidentified gallery works described by the artists named in this sentence.", 50, 50),
    ("whom", "cand-0871", "Relative pronoun refers to Crespi in the employment claim.", 50, 50),
    ("he", "cand-2385", "Pronoun in the employment clause refers to Prince Eugene.", 50, 50),
    ("dal Sole", "cand-2480", "Existing index candidate with p.201 coverage.", 50, 50),
    ("many other Bolognese painters", "cand-7324", "Unenumerated group distinct from Crespi and dal Sole.", 50, 50),
    ("the Neapolitans", "cand-7341", "Collective regional designation for the two named painters that follow.", 50, 50),
    ("Giacomo del Po", "cand-1963", "Existing index candidate with p.201 coverage.", 50, 50),
    ("Solimena", "cand-2484", "Existing index candidate; second occurrence in the gallery list.", 50, 50, 1),
    ("Vittore\nGhislandi", "cand-1101", "Existing index candidate; the printed name breaks across source lines.", 50, 51),
    ("Bergamo", "cand-6208", "Existing place candidate; source says Ghislandi was from Bergamo.", 51, 51),
    ("he", "cand-2386", "Anaphora to Prince Eugene in the preference statement.", 51, 51, 0),
    ("he", "cand-2385", "Anaphora to Prince Eugene in the commissioning statement.", 51, 51, 1),
    ("ancient poets", "cand-7342", "Collective source category for preferred subjects; no complete membership is supplied.", 51, 51),
    ("Virgil", "cand-2779", "Existing index candidate for the poet.", 51, 51),
    ("the Aeneid", "cand-4115", "Existing accepted candidate for Virgil's work.", 51, 51),
    ("‘portrait’ writing the Aeneid", "cand-7314", "Unidentified painting described metaphorically in the source; retain its quotation marks.", 51, 51),
    ("Giacomo Antonio Boni", "cand-0389", "Index subentry for the p.201 Virgil 'portrait' commission.", 51, 52),
    ("Bologna", "cand-3398", "Existing source-derived city candidate.", 52, 52),
    ("His taste", "cand-2386", "Anaphora to Prince Eugene; the author's characterization is retained as reported.", 52, 52),
    ("he", "cand-2386", "Anaphora to Prince Eugene in the lifespan and Venetian-manner statements.", 52, 52, 0),
    ("he", "cand-2386", "Second anaphora to Prince Eugene in the same sentence.", 52, 52, 1),
    ("the Venetians", "cand-7323", "Unnamed group of artists associated with the lighter manner.", 52, 52),
    ("Vienna", "cand-2772", "Existing index city candidate.", 52, 52),
    ("Prince Eugene", "cand-2385", "Existing p.201 patronage subentry.", 53, 53),
    ("nobles", "cand-7325", "Unnamed group of patrons in Vienna.", 53, 53),
    ("Italian art", "cand-4131", "Existing concept candidate; used here for the source's general patronage category.", 53, 53),
    ("the Turks", "cand-7153", "Existing source-derived political-military group; do not identify a specific battle from this wording.", 53, 53),
    ("the\nFrench", "cand-4221", "Existing political-actor candidate; no specific French victory or event is named here; printed name crosses a source line.", 53, 54),
    ("the city", "cand-2772", "Anaphora to Vienna.", 54, 54),
    ("new Rome", "cand-4490", "Metaphorical comparison with Rome; it does not rename or duplicate Vienna.", 54, 54),
    ("Domenico Martinelli", "cand-1553", "Existing index candidate with p.201 coverage.", 54, 54),
    ("town palace", "cand-7317", "Distinct from the Liechtenstein garden palace mentioned later in the sentence.", 54, 54),
    ("Liechtenstein family", "cand-1407", "Existing index candidate for the family, not an individual prince.", 54, 54),
    ("Andrea Pozzo", "cand-2033", "Existing index candidate with p.201 coverage.", 54, 54),
    ("the Emperor", "cand-4531", "Unidentified emperor; do not infer identity from the date in this passage.", 54, 54),
    ("the ceiling", "cand-7320", "Painting project begun in 1704; source does not say it was completed.", 54, 54),
    ("the hall", "cand-7319", "Hall inside the garden palace; keep distinct from the hall/gardens in Eugene's patronage paragraph.", 54, 54),
    ("their garden palace", "cand-7318", "Liechtenstein family garden palace; distinct from its town palace.", 54, 54),
    ("Mattielli", "cand-1584", "Existing index candidate; source gives surname only here.", 54, 54),
    ("sculpture", "cand-7329", "Unidentified sculptures for aristocratic gardens.", 54, 54),
    ("aristocratic garden", "cand-7343", "Repeated generic garden settings; no individual garden is named.", 54, 54),
    ("Ferdinando Galli-Bibbiena", "cand-1112", "Existing index candidate; scan reads Galli-Bibiena, correcting OCR's doubled b.", 54, 54),
    ("Painters travelling north to Germany", "cand-7328", "Unnamed travel group; the passage says they stopped to work in Vienna.", 54, 54),
    ("Germany", "cand-5529", "Existing place candidate.", 54, 54),
    ("the city", "cand-2772", "Anaphora to Vienna in the account of the new collections.", 55, 55),
    ("Italy", "cand-3461", "Existing geographic candidate; source describes pictures arriving from throughout Italy.", 55, 55),
    ("pictures", "cand-7327", "Unidentified group of Italian pictures entering Vienna's new collections.", 55, 55),
    ("new collections", "cand-7326", "Plural and unnamed; do not merge as one institution.", 55, 55),
    ("Vienna", "cand-2772", "Existing city candidate; first occurrence, painters' destination.", 55, 55, 0),
    ("Vienna", "cand-2772", "Existing city candidate; second occurrence, cultural setting.", 55, 55, 1),
    ("feudal aristocracy", "cand-7330", "Collective social group named by Haskell.", 55, 55),
    ("religious foundations", "cand-7331", "Collective institutional group; no individual foundation is named.", 55, 55),
    ("the Italians", "cand-7338", "Collective group in Haskell's account of cultural intelligibility.", 55, 55),
    ("the Baroque", "cand-3569", "Existing period/concept candidate; keep Haskell's metaphorical historical claim attributed.", 58, 58),
    # p.202, including the continuation at the start of the printed page.
    ("Savoy", "cand-2379", "Existing polity/place candidate; the referent is the continental state in the sentence.", 59, 59),
    ("war of the Spanish succession", "cand-2502", "Existing event candidate; no separate victory event is identified here.", 59, 59),
    ("Turin", "cand-2663", "Index candidate with p.202 coverage.", 59, 59),
    ("Local talent", "cand-7332", "Unnamed local artists; source characterizes their availability as rare.", 59, 59),
    ("artists from other towns", "cand-7333", "The recruitment failures are not assigned to named artists.", 59, 59),
    ("Painter after painter", "cand-7333", "Repeated but unnamed artists who refused the journey north.", 59, 59),
    ("successive dukes", "cand-7334", "Unnamed rulers as a group; no individual motives are assigned.", 59, 59),
    ("Victor Amadeus", "cand-2388", "Existing index candidate with p.202 coverage.", 59, 59),
    ("Filippo Juvarra", "cand-1339", "Existing index candidate with p.202 coverage.", 60, 60),
    ("patrons in other uncreative centres", "cand-7335", "Unnamed comparative group; retain Haskell's evaluative phrase as his wording.", 60, 60),
    ("leading painters", "cand-7344", "Unnamed group attracted by the Turin policy; no artists or city assignments are listed here.", 60, 60),
    ("their pictures", "cand-7345", "Unidentified pictures attracted in lieu of or alongside painters.", 60, 60),
    ("smaller provincial towns", "cand-7336", "Unnamed towns that the author says had anticipated the policy.", 60, 60),
]


def source_excerpt(start: int, end: int) -> str:
    return "\n".join(source_lines[start - 1:end])


def segment_text(segment_id: str) -> str:
    meta = segments[segment_id]
    return source_excerpt(meta["line_start"], meta["line_end"])


new_mentions = []
for spec in mention_specs:
    surface, candidate_id, note, line_start, line_end, *occurrence_data = spec
    occurrence_index = occurrence_data[0] if occurrence_data else 0
    if candidate_id not in candidate_ids | new_candidate_ids:
        raise SystemExit(f"mention references missing candidate: {surface} -> {candidate_id}")
    matching_segments = [sid for sid, meta in SEGMENT_IDS.items()
                         if meta and segments[meta]["line_start"] <= line_start <= line_end <= segments[meta]["line_end"]]
    if len(matching_segments) != 1:
        raise SystemExit(f"mention range does not belong to exactly one target segment: {surface} L{line_start}-{line_end}")
    segment_id = SEGMENT_IDS[matching_segments[0]]
    start_line = segment_lines_start = segments[segment_id]["line_start"]
    line_chunk = "\n".join(source_lines[line_start - 1:line_end])
    pattern = re.compile(r"(?<![^\W\d_])" + re.escape(surface) + r"(?![^\W\d_])", re.IGNORECASE)
    matches = [match.start() for match in pattern.finditer(line_chunk)]
    if occurrence_index >= len(matches) or not matches:
        raise SystemExit(f"mention span not found within its line range: {surface!r} L{line_start}-{line_end}")
    if len(matches) > 1 and not occurrence_data:
        raise SystemExit(f"ambiguous repeated mention needs an occurrence index: {surface!r} L{line_start}-{line_end}")
    local_start = matches[occurrence_index]
    base_offset = sum(len(source_lines[n - 1]) + 1 for n in range(segment_lines_start, line_start))
    start = base_offset + local_start
    end = start + len(surface)
    text = segment_text(segment_id)
    if text[start:end].casefold() != surface.casefold():
        raise SystemExit(f"mention offset does not recover exact text: {surface!r}")
    new_mentions.append({
        "mention_id": f"m-chp7-p201-p202-{len(new_mentions)+1:03d}",
        "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


def statement(statement_id, segment_id, start, end, printed_page, pdf_page,
              predicate, claim, qualification, subject=None, obj=None,
              mentioned=(), quote=None, extra=None):
    qualifiers = {
        "source_line_start": start, "source_line_end": end,
        "printed_page": printed_page, "pdf_physical_page": pdf_page,
        "claim": claim, "speaker": "Haskell", "text_layer": "body",
        "qualification": qualification,
        "mentioned_candidate_ids": list(mentioned),
    }
    if extra:
        qualifiers.update(extra)
    return {
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote or source_excerpt(start, end),
        "origin": "book", "source_file": SOURCE_REL,
    }


p201 = SEGMENT_IDS["p201"]
p202 = SEGMENT_IDS["p202"]
statements = [
    statement("st-chp7-p201-v-italian-commanders-furnish-palaces", p201, 43, 43, 201, 43,
              "intended_to_furnish_palaces_with_native_pictures",
              "Continuing the p.200 sentence, Haskell says the high Italian-origin commanders were keen to furnish their Viennese palaces with pictures from their native land.",
              "The passage describes their stated interest; it does not enumerate pictures, identify palaces, or establish which purchases were completed.",
              subject="cand-7303", obj="cand-7322",
              mentioned=["cand-7303", "cand-7304", "cand-7321", "cand-7322"],
              quote="their Viennese palaces with pictures from their native land.",
              extra={"continuation_of_statement_id": "st-chp7-p200-v-italian-commanders-open-continuation"}),
    statement("st-chp7-p201-v-caprara-commissions-bologna-paintings", p201, 43, 43, 201, 43,
              "commissioned_paintings_in", "Haskell says Marshal Caprara commissioned many paintings in Bologna.",
              "The individual works, date, recipient, and exact number are not supplied here.",
              subject="cand-0538", obj="cand-7310", mentioned=["cand-0538", "cand-7310", "cand-3398"],
              quote="Thus Marshal Caprara commissioned many paintings in 'Bologna",
              extra={"footnote_marker": 1, "ocr_corrections": [{"source_line": 43, "ocr": "'Bologna1", "print": "Bologna¹"}]}),
    statement("st-chp7-p201-v-eugene-loyalty-characterization", p201, 43, 44, 201, 43,
              "characterized_as_loyal_to_italy_and_austria",
              "Haskell characterizes Prince Eugene as loyal to Italy in the arts of peace and to Austria in war.",
              "This is the author's comparison, not an independently verified political or artistic identity claim.",
              subject="cand-2385", obj="cand-3461", mentioned=["cand-2385", "cand-3461", "cand-7284"],
              quote="the great Prince Eugene of\nSavoy proved as loyal to Italy in the arts of peace as he was to Austria in those of war."),
    statement("st-chp7-p201-v-eugene-private-patron", p201, 45, 46, 201, 43,
              "described_as_grandiose_influential_private_patron",
              "Haskell calls Prince Eugene the most grandiose and influential private patron in Europe.",
              "Retain the superlative and evaluative wording as Haskell's characterization.",
              subject="cand-2385", mentioned=["cand-2385", "cand-3462"],
              quote="Prince Eugene was indeed the most grandiose and influential private patron in\nEurope.2",
              extra={"footnote_marker": 2}),
    statement("st-chp7-p201-v-winter-palace-begun-by-fischer", p201, 46, 46, 201, 43,
              "building_begun_by_architect", "Haskell says Fischer von Erlach began Prince Eugene's Winter Palace.",
              "The passage does not state the construction dates or define Fischer's full role.",
              subject="cand-7306", obj="cand-0978", mentioned=["cand-7306", "cand-0978", "cand-2385"],
              quote="His Winter Palace begun by Fischer von Erlach"),
    statement("st-chp7-p201-v-belvederes-by-hildebrandt", p201, 46, 47, 201, 43,
              "buildings_attributed_to_architect", "Haskell attributes the two Belvederes to Lucas von Hildebrandt.",
              "The source does not assign distinct buildings or phases beyond the collective wording.",
              subject="cand-7307", obj="cand-1299", mentioned=["cand-7307", "cand-1299", "cand-2385"],
              quote="the two Belvederes by\n-Lucas von Hildebrandt"),
    statement("st-chp7-p201-v-apotheosis-executed-by-permoser", p201, 47, 48, 201, 43,
              "sculpture_attributed_to", "Haskell attributes the marble Apotheosis to Balthasar Permoser.",
              "No location or later history is supplied beyond the statement that it survives.",
              subject="cand-7308", obj="cand-1880", mentioned=["cand-7308", "cand-1880"],
              quote="the marble\nApotheosis by Permoser"),
    statement("st-chp7-p201-v-apotheosis-designed-by-eugene", p201, 48, 48, 201, 43,
              "work_designed_by", "Haskell says Prince Eugene himself designed the marble Apotheosis.",
              "Design and execution are distinct roles in the source; Permoser is named as maker.",
              subject="cand-7308", obj="cand-2385", mentioned=["cand-7308", "cand-2385", "cand-1880"],
              quote="which he himself designed"),
    statement("st-chp7-p201-v-apotheosis-evaluative-interpretation", p201, 48, 48, 201, 43,
              "interpreted_as_sign_of_megalomania_not_taste",
              "Haskell presents the surviving Apotheosis as an illustration of Eugene's megalomania, if not his taste.",
              "This is the author's interpretation and not a factual psychological diagnosis.",
              subject="cand-7308", obj="cand-2385", mentioned=["cand-7308", "cand-2385"],
              quote="survives as an illustration of his megalomania if not of his taste"),
    statement("st-chp7-p201-v-picture-collection-dispersed", p201, 48, 48, 201, 43,
              "collection_dispersed", "Haskell says Prince Eugene's picture collection has been dispersed.",
              "The passage does not enumerate holdings or trace the dispersal.",
              subject="cand-7309", mentioned=["cand-7309", "cand-2385"],
              quote="but his collection of pictures has been dispersed"),
    statement("st-chp7-p201-v-collection-contained-flemish-primitives", p201, 48, 49, 201, 43,
              "collection_contained_flemish_primitives", "Haskell says the collection is chiefly celebrated for the unique Flemish primitives it once contained.",
              "The works are not individually identified; preserve 'unique' as the author's characterization.",
              subject="cand-7309", obj="cand-7337", mentioned=["cand-7309", "cand-7337", "cand-2385"],
              quote="Today it is celebrated chiefly for the unique Flemish primitives it once contained"),
    statement("st-chp7-p201-v-eugene-reputation-among-italians", p201, 49, 49, 201, 43,
              "reported_as_generous_protector_of_italian_arts",
              "Haskell reports that Italians of Eugene's own time knew him as a generous protector and supreme lover of the fine arts, especially those of their native land.",
              "The statement is explicitly reported through a quoted characterization; footnote 3 remains to be reviewed in the composite note segment.",
              subject="cand-2385", obj="cand-7338", mentioned=["cand-2385", "cand-7338", "cand-7339"],
              quote="Eugene was famous as a ‘generous protector and supreme lover of the sine arts, especially those of our native land...’.3",
              extra={"footnote_marker": 3, "ocr_corrections": [{"source_line": 49, "ocr": "sine arts", "print": "fine arts"}]}),
    statement("st-chp7-p201-v-eugene-patronage-of-italian-artists", p201, 49, 50, 201, 43,
              "patronage_of_italian_painters_and_sculptors", "Haskell says Eugene demonstrated his support for Italian painters and sculptors through magnificent patronage.",
              "This broad account does not establish a separate formal commission for every artist or work listed next.",
              subject="cand-2385", obj="cand-7339", mentioned=["cand-2385", "cand-7339"],
              quote="He proved this by his magnificent patronage of Italian painters and sculptors."),
    statement("st-chp7-p201-v-artists-painted-belvedere-frescoes", p201, 49, 50, 201, 43,
              "artists_came_from_italy_to_paint_frescoes", "Haskell says Louis Dorigny, Marc’antonio Chiarini, Gaetano Fanti, Carlo Carlone, and others came from Italy to paint frescoes in the Upper and Lower Belvederes.",
              "The frescoes and individual artist-to-building assignments are not specified.",
              subject="cand-7339", obj="cand-7311",
              mentioned=["cand-0944", "cand-0662", "cand-0993", "cand-0561", "cand-3461", "cand-7307", "cand-7311"],
              quote="Louis Dorigny, Marc’antonio Chiarini,\nGaetano Fanti, Carlo Carlone and others came from Italy to paint frescoes in the Upper and Lower Belvederes"),
    statement("st-chp7-p201-v-mattielli-parodi-statues", p201, 50, 50, 201, 43,
              "made_statues_for_hall_and_gardens", "Haskell says Lorenzo Mattielli and Domenico Antonio Parodi made statues for the hall and gardens.",
              "The individual statues and exact building or garden locations are not identified.",
              subject=None, obj=None, mentioned=["cand-1584", "cand-1841", "cand-7312", "cand-7340"],
              quote="Lorenzo Mattielli and Domenico Antonio Parodi made statues for the hall and gardens"),
    statement("st-chp7-p201-v-solimena-sends-altarpieces", p201, 50, 50, 201, 43,
              "sent_altarpieces_for_chapel", "Haskell says Solimena sent altarpieces for the chapel.",
              "The chapel, number of altarpieces, dates, and titles are not supplied.",
              subject="cand-2484", obj="cand-7316", mentioned=["cand-2484", "cand-7313", "cand-7316"],
              quote="Solimena sent altarpieces for the chapel"),
    statement("st-chp7-p201-v-eugene-gallery-pictures", p201, 50, 51, 201, 43,
              "gallery_hung_pictures_by_named_painters", "Haskell says Prince Eugene's gallery held pictures by Crespi, dal Sole, other Bolognese painters, Giacomo del Po, Solimena, and Vittore Ghislandi.",
              "The passage gives no picture titles and does not formally name the gallery or assign works to a room or collection catalog; it calls Ghislandi a painter from Bergamo.",
              subject="cand-7315", obj="cand-7346",
              mentioned=["cand-7315", "cand-7346", "cand-0871", "cand-2480", "cand-7324", "cand-1963", "cand-2484", "cand-1101", "cand-6208"],
              quote="In the gallery hung pictures by Crespi, whom he employed for five years, dal Sole and many other Bolognese painters4; by the Neapolitans Giacomo del Po and Solimena, and by Vittore\nGhislandi from Bergamo.5",
              extra={"footnote_markers": [4, 5]}),
    statement("st-chp7-p201-v-eugene-employed-crespi-five-years", p201, 50, 50, 201, 43,
              "employed_painter_for_five_years", "Haskell says Prince Eugene employed Crespi for five years.",
              "The source gives a duration but no dates or contract terms.",
              subject="cand-2385", obj="cand-0871", mentioned=["cand-2385", "cand-0871"],
              quote="whom he employed for five years"),
    statement("st-chp7-p201-v-pictures-by-neapolitan-painters", p201, 50, 51, 201, 43,
              "gallery_pictures_by_neapolitan_painters", "Haskell identifies Giacomo del Po and Solimena among the Neapolitan painters represented in the gallery.",
              "This regional label is the author's wording; it does not resolve the painters' modern identity or birthplace.",
              subject="cand-7346", mentioned=["cand-1963", "cand-2484", "cand-7341", "cand-7315", "cand-7346"],
              quote="by the Neapolitans Giacomo del Po and Solimena"),
    statement("st-chp7-p201-v-list-not-exhaustive", p201, 51, 51, 201, 43,
              "named_artists_are_non_exhaustive", "Haskell says the named artists are only the most famous and that the list could be doubled or trebled.",
              "This signals an incomplete list; it does not license adding unnamed members.",
              subject="cand-7339", mentioned=["cand-7339"],
              quote="These are only the most famous and the list could be doubled or trebled without difficulty."),
    statement("st-chp7-p201-v-eugene-preferred-ancient-poetic-subjects", p201, 51, 51, 201, 43,
              "preferred_subjects_from_ancient_poets", "From surviving records and inventories, Haskell infers that Eugene especially liked subjects drawn from ancient poets, particularly Virgil.",
              "The author's wording marks this as an impression drawn from records and inventories, not a complete preference list.",
              subject="cand-2386", obj="cand-2779", mentioned=["cand-2386", "cand-7342", "cand-2779"],
              quote="From the records and inventories that have survived we gain the impression that the subjects he loved best were those taken from the ancient poets, especially Virgil"),
    statement("st-chp7-p201-v-eugene-boni-virgil-portrait", p201, 51, 52, 201, 43,
              "commissioned_portrait_of_virgil_writing_aeneid", "Haskell says Eugene commissioned Giacomo Antonio Boni in Bologna to paint a 'portrait' of Virgil writing the Aeneid.",
              "The work is unidentified; retain the source's metaphorical quotation marks and do not infer title, date, survival, or location.",
              subject="cand-2385", obj="cand-7314",
              mentioned=["cand-2385", "cand-7314", "cand-2779", "cand-4115", "cand-0389", "cand-3398"],
              quote="whose ‘portrait’ writing the Aeneid he commissioned from\nGiacomo Antonio Boni in Bologna",
              extra={"footnote_marker": 6}),
    statement("st-chp7-p201-v-eugene-taste-sumptuous-heavy", p201, 52, 52, 201, 43,
              "taste_characterized_as_sumptuous_and_heavy", "Haskell characterizes Eugene's taste as above all sumptuous and heavy.",
              "Keep this as the author's evaluative description.",
              subject="cand-2386", mentioned=["cand-2386"],
              quote="His taste was above all for the sumptuous and heavy."),
    statement("st-chp7-p201-v-eugene-no-interest-in-venetian-manner", p201, 52, 52, 201, 43,
              "seems_to_have_shown_no_interest_in_lighter_venetian_manner",
              "Haskell says that although Eugene lived until 1736, he seems to have shown no interest in the lighter manner of the Venetians, many of whom worked in Vienna for other patrons.",
              "Preserve 'seems' and the scope of this claim; it does not say Eugene rejected all Venetian art or identify the other patrons.",
              subject="cand-2386", obj="cand-7323", mentioned=["cand-2386", "cand-7323", "cand-2772"],
              quote="Though he lived until 1736 he seems to have shown no interest whatsoever in the lighter manner of the Venetians, many of whom came to work in Vienna for other patrons."),
    statement("st-chp7-p201-v-vienna-many-nobles-patronize-italian-art", p201, 53, 53, 201, 43,
              "many_nobles_commissioned_italian_art", "Haskell says Prince Eugene was one among many nobles commissioning Italian art at the time.",
              "The other nobles and their commissions are not individually named.",
              subject="cand-7325", obj="cand-4131", mentioned=["cand-2385", "cand-7325", "cand-4131"],
              quote="For Prince Eugene was only one among a multitude of nobles who were commissioning Italian art at the time."),
    statement("st-chp7-p201-v-vienna-rise-after-military-victories", p201, 53, 54, 201, 43,
              "military_outcomes_contributed_to_vienna's_rise", "Haskell says relief from the Turks and then victory against the French established Vienna as a great European capital and a new Rome in its appeal to artists.",
              "No specific siege, battle, date, or causal mechanism is named in this passage; 'new Rome' is a comparison, not an identity.",
              subject="cand-2772", obj="cand-3462", mentioned=["cand-2772", "cand-4490", "cand-7153", "cand-4221", "cand-7325"],
              quote="Delivery from the Turks and then victory against the\nFrench established the city as a great European capital—a new Rome, which rivalled the old in its appeal to artists"),
    statement("st-chp7-p201-v-martinelli-town-palace-1691", p201, 54, 54, 201, 43,
              "came_to_build_town_palace_in_1691", "Haskell says Domenico Martinelli came to build the Liechtenstein family's town palace in 1691.",
              "The source says 'came to build'; it does not provide completion date or identify a construction contract.",
              subject="cand-7317", obj="cand-1553", mentioned=["cand-7317", "cand-1553", "cand-1407", "cand-2772"],
              quote="Domenico Martinelli came to build the town palace of the Liechtenstein family in 1691"),
    statement("st-chp7-p201-v-pozzo-garden-palace-ceiling-1704", p201, 54, 54, 201, 43,
              "summoned_and_began_ceiling_painting_in_1704", "Haskell says Andrea Pozzo, summoned by the Emperor, began painting the hall ceiling in the Liechtenstein family's garden palace in 1704.",
              "The Emperor is unnamed; 'began to paint' does not establish completion or a formal commission.",
              subject="cand-7320", obj="cand-2033", mentioned=["cand-2033", "cand-4531", "cand-7318", "cand-7319", "cand-7320"],
              quote="in 1704 Andrea Pozzo, who had been summoned by the Emperor, began to paint the ceiling of the hall in their garden palace"),
    statement("st-chp7-p201-v-mattielli-aristocratic-gardens", p201, 54, 54, 201, 43,
              "made_sculpture_for_aristocratic_gardens", "Haskell says Mattielli made sculpture for many aristocratic gardens.",
              "No gardens or individual sculptures are named; do not merge these with the hall-and-garden statues above.",
              subject="cand-1584", obj="cand-7329", mentioned=["cand-1584", "cand-7329", "cand-7343"],
              quote="Mattielli made sculpture for many an aristocratic garden"),
    statement("st-chp7-p201-v-galli-bibiena-theatrical-spectacles", p201, 54, 54, 201, 43,
              "produced_theatrical_spectacles", "Haskell says Ferdinando Galli-Bibiena produced marvellous theatrical spectacles.",
              "'Marvellous' is the author's evaluation; individual productions, dates, and venues are not named.",
              subject="cand-1112", mentioned=["cand-1112"],
              quote="Ferdinando Galli-Bibbiena produced marvellous theatrical spectacles",
              extra={"ocr_corrections": [{"source_line": 54, "ocr": "Galli-Bibbiena", "print": "Galli-Bibiena"}]}),
    statement("st-chp7-p201-v-painters-stopped-in-vienna", p201, 54, 55, 201, 43,
              "travelling_painters_stopped_to_work_in_vienna", "Haskell says painters travelling north to Germany all stopped to work in Vienna.",
              "This is a broad authorial generalization; it gives no individuals or dates.",
              subject="cand-7328", obj="cand-2772", mentioned=["cand-7328", "cand-5529", "cand-2772"],
              quote="Painters travelling north to Germany all stopped to.\nwork in Vienna"),
    statement("st-chp7-p201-v-italian-pictures-enriched-vienna-collections", p201, 55, 55, 201, 43,
              "pictures_from_italy_enriched_vienna_collections", "Haskell says pictures poured in from across Italy to enrich the new collections being formed in Vienna.",
              "The collections and pictures remain unnamed; no count or individual transfer is established.",
              subject="cand-7327", obj="cand-7326", mentioned=["cand-3461", "cand-7327", "cand-7326", "cand-2772"],
              quote="And from everywhere in Italy pictures poured in to enrich the new collections that were being formed in the city"),
    statement("st-chp7-p201-v-vienna-cultural-setting", p201, 55, 55, 201, 43,
              "vienna_social_and_religious_setting_supported_italian_civilisation", "Haskell says Vienna's feudal aristocracy and all-powerful religious foundations provided a civilization that Italians could understand.",
              "The sentence continues on p.202 L58; this is Haskell's broad cultural interpretation.",
              subject="cand-2772", obj="cand-7338", mentioned=["cand-2772", "cand-7330", "cand-7331", "cand-7338"],
              quote="With its feudal aristocracy and allpowerful religious foundations Vienna provided a civilisation that the Italians could",
              extra={"continuation_status": "open", "continuation_expected_segment_id": p202,
                     "ocr_corrections": [{"source_line": 55, "ocr": "allpowerful", "print": "all-powerful"}]}),
    statement("st-chp7-p202-v-baroque-conquest-transition", p202, 58, 58, 202, 44,
              "baroque_conquest_before_values_changed", "Haskell calls Vienna the last conquest of the Baroque in a world whose values were already changing.",
              "This is an interpretive periodization and metaphor, not a claim that the artistic style ended everywhere.",
              subject="cand-2772", obj="cand-3569", mentioned=["cand-2772", "cand-3569"],
              quote="It was the last conquest of the Baroque in a world whose values were already changing."),
    statement("st-chp7-p202-v-savoy-transformed-after-war", p202, 59, 59, 202, 44,
              "state_transformed_after_war_and_victory", "Haskell says Savoy was transformed by the War of the Spanish Succession and that victory accompanied a flourishing of the arts.",
              "The source does not separately identify which victory or specify a single causal mechanism.",
              subject="cand-2379", obj="cand-2502", mentioned=["cand-2379", "cand-2502"],
              quote="Savoy was the other continental state which emerged transformed from the war of the Spanish succession and here too victory was accompanied by a wonderful flowering of the arts.1",
              extra={"footnote_marker": 1}),
    statement("st-chp7-p202-v-turin-architecture-and-painting-patronage", p202, 59, 59, 202, 44,
              "architecture_significant_painting_patronage_ineffective", "Haskell says Turin's architecture had European significance during much of the seventeenth century while its painting patronage had been futile.",
              "The phrase 'almost laughable in its futility' is Haskell's evaluation.",
              subject="cand-2663", mentioned=["cand-2663"],
              quote="During much of the seventeenth century the architecture of Turin had been of European significance, but patronage of painting had been almost laughable in its futility."),
    statement("st-chp7-p202-v-turin-recruitment-failures", p202, 59, 59, 202, 44,
              "local_talent_rare_and_artist_recruitment_failed", "Haskell says local talent was rare, repeated attempts to attract artists failed, and successive painters refused the journey north.",
              "The painters and attempts remain unidentified; do not create individual identities from the generalization.",
              subject="cand-2663", obj="cand-7333", mentioned=["cand-2663", "cand-7332", "cand-7333"],
              quote="Local talent was rare and attempts to attract artists from other towns had met with a long scries of failures. Painter after painter had refused to makejhejourney north",
              extra={"ocr_corrections": [{"source_line": 59, "ocr": "scries", "print": "series"}, {"source_line": 59, "ocr": "makejhejourney", "print": "make the journey"}]}),
    statement("st-chp7-p202-v-savoy-dukes-preferred-hunting-and-military", p202, 59, 59, 202, 44,
              "dukes_more_addicted_to_hunting_and_military_pursuits", "Haskell says successive dukes were more attached to hunting and military pursuits than to cultivating art, and seemed resigned to the situation.",
              "This is a generalized authorial characterization; it does not assign a motive or action to a named individual.",
              subject="cand-7334", obj="cand-2663", mentioned=["cand-7334", "cand-2663"],
              quote="successive dukes, who were in any case more addicted to hunting and military pursuits than the cultivation of art, seemed generally resigned to the situation"),
    statement("st-chp7-p202-v-victor-amadeus-and-juvarra-change-turin", p202, 59, 60, 202, 44,
              "ruler_and_artistic_adviser_changed_patronage", "Haskell says Victor Amadeus, with the help of his 'artistic dictator' Filippo Juvarra, was able to change Turin's artistic situation.",
              "The quoted epithet is Haskell's; the passage does not define Juvarra's formal office or specific measures here.",
              subject="cand-2388", obj="cand-1339", mentioned=["cand-2388", "cand-1339", "cand-2663"],
              quote="Now in his hour of triumph Victor Amadeus was able, with the help of his artistic dictator\nFilippo Juvarra, to change all this"),
    statement("st-chp7-p202-v-turin-attracted-painters-or-pictures", p202, 60, 60, 202, 44,
              "attracted_painters_or_pictures_from_richer_cities", "Haskell says Victor Amadeus and Juvarra followed other centres' example by attracting leading painters, or at least their pictures, from richer cities.",
              "The source leaves the artists, pictures, and source cities unnamed; the disjunction 'or at least' is retained.",
              subject=None, mentioned=["cand-2388", "cand-1339", "cand-2663", "cand-7335", "cand-7344", "cand-7345"],
              quote="They followed the example of patrons in other uncreative centres and attracted leading painters, or at least their pictures, from a wide variety of more richly endowed cities."),
    statement("st-chp7-p202-v-smaller-towns-anticipated-turin", p202, 60, 60, 202, 44,
              "smaller_towns_anticipated_turin_policy", "Haskell says several smaller provincial towns had already anticipated this policy and announces that the account will turn to them.",
              "The towns are not named in this segment; the final clause is a forward reference in the narrative.",
              subject="cand-7336", obj="cand-2663", mentioned=["cand-7336", "cand-2663"],
              quote="they had already been anticipated in a number of smaller provincial towns and it is to them that we must turn in order to understand the significance of its origins and development."),
]

if len({row["statement_id"] for row in statements}) != len(statements):
    raise SystemExit("duplicate planned statement IDs")
if {row["statement_id"] for row in statements} & existing_statement_ids:
    raise SystemExit("planned statement ID already exists")
for row in statements:
    q = row["qualifiers"]
    excerpt = source_excerpt(q["source_line_start"], q["source_line_end"])
    if row["original_quote"] not in excerpt:
        raise SystemExit(f"quote not present in source: {row['statement_id']}")
    meta = segments[row["segment_id"]]
    if not (meta["line_start"] <= q["source_line_start"] <= q["source_line_end"] <= meta["line_end"]):
        raise SystemExit(f"statement line range falls outside its segment: {row['statement_id']}")
    if not set(q["mentioned_candidate_ids"]) <= candidate_ids | new_candidate_ids:
        raise SystemExit(f"statement references missing candidate: {row['statement_id']}")

previous_statement_id = "st-chp7-p200-v-italian-commanders-open-continuation"
previous_statement = next((row for row in statement_rows if row["statement_id"] == previous_statement_id), None)
if not previous_statement or previous_statement["qualifiers"].get("continuation_status") != "open":
    raise SystemExit("expected the p.200 continuation to remain open")

new_mentions.sort(key=lambda row: (row["segment_id"], int(row["start_char"])))
for row in new_mentions:
    if row["mention_id"] in existing_mention_ids:
        raise SystemExit(f"mention ID collision: {row['mention_id']}")

updated_coverage = []
for row in coverage_rows:
    row = dict(row)
    if row["segment_id"] == SEGMENT_IDS["p201"]:
        row.update({
            "disposition": "reviewed", "migration_status": "complete",
            "source_line_ranges": "L43-55",
            "note": "Printed p.201 body read against CHP-7.pdf physical p.43. Closes the p.200 L17 sentence at L43; records the Prince Eugene patronage account, Vienna transition, named palace/work references, and OCR corrections 'sine arts'→'fine arts', 'Galli-Bibbiena'→'Galli-Bibiena'. Footnotes 1-6 remain in composite note segment L62-76.",
        })
    elif row["segment_id"] == SEGMENT_IDS["p202"]:
        row.update({
            "disposition": "reviewed", "migration_status": "complete",
            "source_line_ranges": "L58-60",
            "note": "Printed p.202 body read; L58 closes the p.201 Vienna-civilisation sentence. L59-60 covers the Savoy/Turin transition. The printed note 1 remains in composite note segment L62-76.",
        })
    elif row["segment_id"] == "chp-7:07_CHP-7_sec_v:l9-18":
        row["note"] = "p.200 body and footnote 6 (the text present at L18) read against CHP-7.pdf physical p.38 and migrated. Footnotes 1-5 and 7 occur in the later composite note block L62-76 and remain queued there. The L17 sentence ending 'furnishing' is closed by p.201 L43 after intervening plate segments. S2 corrections: printed 'further' for OCR 'Anther'; printed 'Pascoli, II' for OCR 'H'; printed 'Ghislandi' for OCR 'Gliislandi'. Source text unchanged."
    updated_coverage.append(row)

preview = {
    "mode": "dry-run", "segments": list(SEGMENT_IDS.values()),
    "new_candidates": len(new_candidates), "new_mentions": len(new_mentions),
    "new_statements": len(statements), "closed_p200_statement": previous_statement_id,
    "coverage": {SEGMENT_IDS["p201"]: "reviewed/complete", SEGMENT_IDS["p202"]: "reviewed/complete"},
    "deferred_footnotes": ["p.201 notes 1-6", "p.202 note 1", "p.200 notes 1-5 and 7"],
    "ocr_corrections": ["'Bologna1 -> Bologna¹", "sine arts -> fine arts", "Galli-Bibbiena -> Galli-Bibiena", "allpowerful -> all-powerful", "scries -> series", "makejhejourney -> make the journey"],
    "statement_ids": [row["statement_id"] for row in statements],
    "mentions": [{"segment_id": row["segment_id"], "surface": row["surface_form"], "candidate_id": row["candidate_id"], "start_char": row["start_char"], "end_char": row["end_char"]} for row in new_mentions],
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
if not parser.parse_args().apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)

previous_statement["predicate"] = "intended_to_furnish_palaces_with_native_pictures"
previous_statement["qualifiers"].update({
    "claim": "Haskell says high Italian-origin commanders serving in the Imperial army were keen to furnish their Viennese palaces with pictures from their native land.",
    "qualification": "The sentence continues across the plate-page interruption and closes at p.201 L43. It describes an interest, not a completed purchase or a named picture.",
    "continuation_status": "completed",
    "continuation_completed_in_segment_id": SEGMENT_IDS["p201"],
    "continuation_source_lines": [43],
    "continuation_note": "The p.200 phrase 'furnishing' continues on p.201 as 'their Viennese palaces with pictures from their native land.'",
    "mentioned_candidate_ids": ["cand-7288", "cand-7303", "cand-7304", "cand-7321", "cand-7322"],
})
previous_statement["qualifiers"].pop("continuation_expected_segment_id", None)
vienna_statement_id = "st-chp7-p201-v-vienna-cultural-setting"
vienna_statement = next((row for row in statements if row["statement_id"] == vienna_statement_id), None)
if not vienna_statement or vienna_statement["qualifiers"].get("continuation_status") != "open":
    raise SystemExit("expected the p.201 cultural-setting statement to await p.202")
vienna_statement["qualifiers"].update({
    "continuation_status": "completed",
    "continuation_completed_in_segment_id": p202,
    "continuation_source_lines": [58],
    "continuation_note": "The p.201 sentence ending 'could' closes with 'understand' at p.202 L58.",
})
vienna_statement["qualifiers"].pop("continuation_expected_segment_id", None)

for path in (CANDIDATE_PATH, MENTION_PATH, STATEMENT_PATH, COVERAGE_PATH):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(path, backup)


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


candidate_rows.extend(new_candidates)
mention_rows.extend(new_mentions)
statement_rows.extend(statements)
write_csv_atomic(CANDIDATE_PATH, candidate_fields, candidate_rows)
write_csv_atomic(MENTION_PATH, mention_fields, mention_rows)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=STATEMENT_PATH.parent, delete=False, suffix=".tmp") as stream:
    for row in statement_rows:
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    temporary = Path(stream.name)
temporary.replace(STATEMENT_PATH)
write_csv_atomic(COVERAGE_PATH, coverage_fields, updated_coverage)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
