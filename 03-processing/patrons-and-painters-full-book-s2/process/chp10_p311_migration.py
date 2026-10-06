"""Controlled S2 migration for printed p.311; dry-run unless --apply."""
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_sec_ii.md"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_sec_ii.md"
SEGMENT = "chp-10:10_CHP-10_sec_ii:l7-15"
EXPECTED_ASSET_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
EXPECTED_SEGMENT_SHA = "d1ecabafafb97a33a1b33afebe2048844aac6d981489d52bc56291d668e4b225"
BACKUP_SUFFIX = ".bak-s2-chp10-p311-20261002"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("source asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
first, last, PRINTED_PAGE, PHYSICAL_PAGE = 7, 15, 311, 40
segment_text = "\n".join(source_lines[first - 1:last])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != EXPECTED_SEGMENT_SHA:
    raise SystemExit("S2 source segment changed")
if source_lines[first - 1] != "[Page 1661]" or "Johann Matthias Schulenburg" not in segment_text:
    raise SystemExit("p.311 OCR segment does not match the reviewed source")

candidate_path, mention_path, statement_path, coverage_path = [TABLES / name for name in (
    "entity-candidates.csv", "mentions.csv", "book-statements.jsonl", "s2-coverage.csv"
)]
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_ids = {row["candidate_id"] for row in candidates}
mention_ids = {row["mention_id"] for row in mentions}
statement_ids = {row["statement_id"] for row in statements}
coverage = {row["segment_id"]: row for row in coverage_rows}
maximum = max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates)
if (len(candidates), maximum) != (9554, 9567):
    raise SystemExit(f"candidate state changed: count={len(candidates)}, max={maximum}")
if (coverage[SEGMENT]["disposition"], coverage[SEGMENT]["migration_status"], coverage[SEGMENT]["source_line_ranges"]) != ("queued", "pending", ""):
    raise SystemExit(f"coverage state changed: {coverage[SEGMENT]}")
if any(row["segment_id"] == SEGMENT for row in mentions) or any(row["segment_id"] == SEGMENT for row in statements):
    raise SystemExit("p.311 already has S2 mention or statement rows")

EXISTING = {
    "schulenburg": "cand-2401", "schulenburg_corfu_index": "cand-2405",
    "charles_xii": "cand-0659", "eugene": "cand-2384", "spanish_succession": "cand-2502",
    "frederick": "cand-1079", "france": "cand-5317", "germany": "cand-5529",
    "europe": "cand-3462", "italy": "cand-3461", "london": "cand-1422",
    "berlin": "cand-9073", "dresden": "cand-0947", "holland": "cand-6084",
    "venice": "cand-2719", "verona": "cand-8681", "republic_venice": "cand-8838",
    "corfu": "cand-8118", "farnese_family": "cand-5006",
}
for key, cid in EXISTING.items():
    if cid not in candidate_ids:
        raise SystemExit(f"required candidate missing: {key}={cid}")

NEW_SPECS = [
    ("house_savoy", "House of Savoy", "family",
     "Named on p.311 as one of the powers for which Schulenburg fought; keep distinct from the geographic candidate 'Savoy' (cand-2379).", 10),
    ("malplaquet", "Malplaquet", "place",
     "Location named for Schulenburg's service under Prince Eugene in the War of the Spanish Succession; this passage does not identify a particular engagement or give a date.", 10),
    ("hanoverian_dynasty", "Hanoverian dynasty", "family",
     "Haskell says Schulenburg was closely related to the Hanoverian dynasty but names no particular relative or line of descent.", 13),
    ("palazzo_loredan", "Palazzo Loredan", "place",
     "Named as Schulenburg's residence in Venice; the building is not further identified in this passage.", 14),
    ("bourbon_dynasty", "Bourbon dynasty", "family",
     "One of four dynastic groups whose portraits Haskell says lined the walls of the Palazzo Loredan; individual sitters and portraits are not identified.", 14),
    ("hapsburg_dynasty", "Hapsburg dynasty", "family",
     "Source spelling retained. One of four dynastic groups whose portraits Haskell says lined the walls of the Palazzo Loredan; individual sitters are not identified.", 14),
    ("hohenzollern_dynasty", "Hohenzollern dynasty", "family",
     "One of four dynastic groups whose portraits Haskell says lined the walls of the Palazzo Loredan; individual sitters are not identified.", 14),
    ("hungarian_forces", "Hungarians for whom Schulenburg fought (force or political unit unspecified)", "term",
     "Haskell says Schulenburg fought for 'the Hungarians'; no ruler, army, or specific unit is identified.", 10),
    ("saxon_forces", "Saxons for whom Schulenburg fought (force or political unit unspecified)", "term",
     "Haskell says Schulenburg fought for 'the Saxons' against Charles XII; no ruler, army, or specific unit is identified.", 10),
    ("turkish_forces", "Turkish forces in Haskell's account of the Corfu attacks (specific force unidentified)", "term",
     "The p.311 passage refers to Turkish onslaughts but does not name a ruler or military unit; keep distinct from other generic 'Turks' candidates pending S3.", 10),
    ("corfu_defense", "Schulenburg's defense of Corfu in 1715 and 1716", "event",
     "Haskell describes Schulenburg's defense against Turkish attacks in 1715 and 1716. Keep separate from cand-8119, which labels Venice's 1716 Siege of Corfu, pending global event alignment.", 10),
    ("corfu_commemorative_works", "Unidentified works of art commemorating the Corfu campaign commissioned by Schulenburg and the Venetian State", "work",
     "Haskell says various works commemorated the campaign and were commissioned by Schulenburg and the State; no individual title, artist, or medium is identified here.", 10),
    ("loredan_dynastic_portraits", "Unidentified portraits of Bourbon, Hapsburg, Farnese, and Hohenzollern dynasties at Palazzo Loredan", "work",
     "A group of portraits named by their dynastic subjects; individual works, sitters, artists, and dates are not supplied in this passage.", 14),
    ("schulenburg_statue", "Statue of Marshal Johann Matthias Schulenburg erected by Venice", "work",
     "Haskell says Venice erected a statue to Schulenburg after describing the Corfu campaign; location, artist, and date are not given here.", 11),
    ("unnamed_english_nobleman", "Unnamed young English nobleman treated by Schulenburg during his Italian tour", "person",
     "Haskell leaves the nobleman unnamed. P.311 note 6 cites a letter from Lord Rockingham to Lord Essex, but the cited letter's relation to this person must be checked before any identification.", 15),
    ("schulenburg_will", "Will of Marshal Johann Matthias Schulenburg drawn up in 1740", "archive",
     "Haskell summarizes a will drawn up in 1740; this passage gives no repository or shelfmark and the document has not been independently consulted.", 15),
    ("crowned_heads_group", "Crowned heads of Europe said to be on friendly terms with Schulenburg (individuals unspecified)", "term",
     "Haskell's phrase 'half the crowned heads of Europe' is a generalization; no individual members of the group are named in this passage.", 13),
]
new_candidates = []
candidate_by_key = {}
existing_names = {(row["canonical_name"], row["suggested_type"]) for row in candidates}
for number, (key, name, kind, detail, line_no) in enumerate(NEW_SPECS, maximum + 1):
    cid = f"cand-{number:04d}"
    if cid in candidate_ids or (name, kind) in existing_names:
        raise SystemExit(f"candidate already exists or ID collision: {cid} {name}")
    candidate_by_key[key] = cid
    new_candidates.append({
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L{line_no}",
    })

all_candidate_ids = candidate_ids | {row["candidate_id"] for row in new_candidates}
new_mentions = []
new_mention_ids = set()


def occurrences(line, surface):
    found = []
    for match in re.finditer(re.escape(surface), line):
        before = line[match.start() - 1] if match.start() else ""
        after = line[match.end()] if match.end() < len(line) else ""
        if surface.isalpha() and ((before and (before.isalnum() or before == "_")) or (after and (after.isalnum() or after == "_"))):
            continue
        found.append(match.start())
    return found


def add_mention(local_id, line_no, surface, cid, note="", occurrence=0):
    mid = f"m-s2-ch10-p311-{local_id}"
    if mid in mention_ids or mid in new_mention_ids:
        raise SystemExit(f"duplicate mention ID: {mid}")
    if cid not in all_candidate_ids:
        raise SystemExit(f"missing candidate for {mid}: {cid}")
    if "\n" in surface:
        matches = [match.start() for match in re.finditer(re.escape(surface), segment_text)]
        if occurrence >= len(matches):
            raise SystemExit(f"cross-line surface not found from L{line_no}: {surface!r}; matches={len(matches)}")
        start = matches[occurrence]
    else:
        matches = occurrences(source_lines[line_no - 1], surface)
        if occurrence >= len(matches):
            raise SystemExit(f"surface not found on L{line_no}: {surface!r}; matches={len(matches)}")
        offset = len("\n".join(source_lines[first - 1:line_no - 1])) + (1 if line_no > first else 0)
        start = offset + matches[occurrence]
    end = start + len(surface)
    if segment_text[start:end] != surface:
        raise SystemExit(f"mention span mismatch: {mid}")
    new_mentions.append({
        "mention_id": mid, "segment_id": SEGMENT, "candidate_id": cid,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })
    new_mention_ids.add(mid)


M = [
    ("schulenburg-full-name", 8, "Johann Matthias Schulenburg", EXISTING["schulenburg"], "Index candidate for the p.311 Schulenburg entry; KU identity remains for S3."),
    ("france", 9, "France", EXISTING["france"], "Country named as a place of study."),
    ("germany-study", 9, "Germany", EXISTING["germany"], "Country named as a place of study."),
    ("he-served", 9, "he", EXISTING["schulenburg"], "Corefers to Schulenburg."),
    ("europe", 9, "Europe", EXISTING["europe"], "Geographic scope of the military service summary."),
    ("hungarians", 10, "Hungarians", candidate_by_key["hungarian_forces"], "Collective as phrased by Haskell; no specific force identified."),
    ("house-of-savoy", 10, "House of Savoy", candidate_by_key["house_savoy"], "Dynastic house, distinct from the place candidate Savoy."),
    ("saxons", 10, "Saxons", candidate_by_key["saxon_forces"], "Collective as phrased by Haskell; no specific force identified."),
    ("charles-xii", 10, "Charles XII of Sweden", EXISTING["charles_xii"], "Index entry specifically covers p.311."),
    ("eugene-first", 10, "Prince Eugene", EXISTING["eugene"], "Index candidate for Prince Eugene of Savoy."),
    ("spanish-succession", 10, "the wars of the Spanish Succession", EXISTING["spanish_succession"], "War named as context for Schulenburg's service."),
    ("malplaquet", 10, "Malplaquet", candidate_by_key["malplaquet"], "Place named in the service account; no specific engagement or date is asserted here."),
    ("venice-association", 10, "Venice", EXISTING["venice"], "Venice as the place/context of Schulenburg's association; the later 'Republic' is recorded separately as a political entity.", 0),
    ("republic-appeal", 10, "the Republic", EXISTING["republic_venice"], "Political entity that appealed to Prince Eugene in 1715."),
    ("eugene-advice", 10, "Eugene", EXISTING["eugene"], "Second mention on this line; Eugene is the person giving the recommendation.", 1),
    ("turks", 10, "the Turks", candidate_by_key["turkish_forces"], "Generic force described by Haskell; not identified with a particular unit."),
    ("schulenburg-recommendation", 10, "Schulenburg", EXISTING["schulenburg"], "Recipient of Eugene's recommendation."),
    ("marshal-corfu", 10, "the Marshal", EXISTING["schulenburg_corfu_index"], "Context matches the index subentry 'defence of Corfu'."),
    ("corfu", 10, "Corfù", EXISTING["corfu"], "Printed p.311 spells the place Corfù; candidate canonical form is Corfu."),
    ("corfu-campaign", 10, "The campaign", candidate_by_key["corfu_defense"], "Anaphor to the 1715–1716 Corfu defense just described; distinct candidate retained pending event alignment."),
    ("commemorative-works", 10, "various works of art", candidate_by_key["corfu_commemorative_works"], "Individual works and makers are not named."),
    ("state-commission", 10, "the State", EXISTING["republic_venice"], "Read in the immediate Venetian Republic context; individual state commission records are not identified."),
    ("venice-gratitude", 10, "Venice", EXISTING["republic_venice"], "Second Venice mention on this line; here it acts as the political entity that rewards Schulenburg.", 1),
    ("he-continued", 11, "He", EXISTING["schulenburg"], "Corefers to Schulenburg."),
    ("republic-service", 11, "the Republic", EXISTING["republic_venice"], "Political entity he continued to serve."),
    ("italy-travel", 11, "Italy", EXISTING["italy"], "Country named in the travel summary."),
    ("london-travel", 11, "London", EXISTING["london"], "City named as a travel destination."),
    ("berlin-travel", 12, "Berlin", EXISTING["berlin"], "City named as a travel destination."),
    ("dresden-travel", 12, "Dresden", EXISTING["dresden"], "City named as a travel destination."),
    ("holland-travel", 12, "Holland", EXISTING["holland"], "Region named as a travel destination; not normalized to a political entity."),
    ("he-divided-years", 12, "He", EXISTING["schulenburg"], "Corefers to Schulenburg."),
    ("venice-residence", 12, "Venice", EXISTING["venice"], "City named as one of the places where he spent his final years."),
    ("verona", 12, "Verona", EXISTING["verona"], "Place candidate; the reading of 'where' for the funeral is retained with the statement qualification."),
    ("schulenburg-retirement", 13, "Schulenburg", EXISTING["schulenburg"], "Explicit name at the start of the retirement paragraph."),
    ("hanoverian-dynasty", 13, "the Hanoverian dynasty", candidate_by_key["hanoverian_dynasty"], "Kinship group named without a specific relative."),
    ("crowned-heads", 13, "half the crowned heads of\nEurope", candidate_by_key["crowned_heads_group"], "Unenumerated group; 'half' is Haskell's generalization. The source phrase crosses OCR lines 13–14."),
    ("europe-crowned-heads", 14, "Europe", EXISTING["europe"], "Geographic term nested within the unnamed crowned-heads group."),
    ("bourbons", 14, "Bourbons", candidate_by_key["bourbon_dynasty"], "Dynastic group named as portrait subjects; individual sitters unknown."),
    ("hapsburgs", 14, "Hapsburgs", candidate_by_key["hapsburg_dynasty"], "Source spelling retained; individual sitters unknown."),
    ("farneses", 14, "Farneses", EXISTING["farnese_family"], "Family candidate; individual sitters unknown."),
    ("hohenzollerns", 14, "Hohenzollerns", candidate_by_key["hohenzollern_dynasty"], "Dynastic group named as portrait subjects; individual sitters unknown."),
    ("palazzo-loredan", 14, "Palazzo Loredan", candidate_by_key["palazzo_loredan"], "Building named as Schulenburg's residence."),
    ("he-lived", 14, "he", EXISTING["schulenburg"], "Corefers to Schulenburg."),
    ("they-visited", 14, "They", candidate_by_key["crowned_heads_group"], "Corefers to the unenumerated crowned heads of Europe."),
    ("him-called-on", 14, "him", EXISTING["schulenburg"], "Corefers to Schulenburg.", 0),
    ("venice-visits", 14, "Venice", EXISTING["venice"], "City visited by the crowned heads.", 0),
    ("him-wrote-to", 14, "him", EXISTING["schulenburg"], "Corefers to Schulenburg.", 1),
    ("frederick", 14, "Crown Prince Frederick of Prussia", EXISTING["frederick"], "The parenthetical 'later the Great' explicitly identifies the person; S3 still governs candidate-to-KU alignment."),
    ("frederick-epithet", 14, "the Great", EXISTING["frederick"], "Appositional epithet in Haskell's parenthetical identification."),
    ("him-applied", 14, "him", EXISTING["schulenburg"], "Corefers to Schulenburg as the recipient of Frederick's request.", 2),
    ("schulenburg-after-request", 14, "Schulenburg", EXISTING["schulenburg"], "Subject of the report about the request's outcome."),
    ("old-marshal", 14, "The old Marshal", EXISTING["schulenburg"], "Corefers to Schulenburg."),
    ("he-liked", 14, "He", EXISTING["schulenburg"], "Corefers to Schulenburg."),
    ("english-nobleman", 15, "English nobleman", candidate_by_key["unnamed_english_nobleman"], "Unnamed person; do not identify him from note 6 without verifying the citation link."),
    ("italy-tour", 15, "Italy", EXISTING["italy"], "Country named as the setting of the unnamed nobleman's tour."),
    ("schulenburg-doctor-story", 15, "Schulenburg", EXISTING["schulenburg"], "Person who summoned the doctor and questioned him, as reported by Haskell."),
    ("schulenburg-younger-men", 15, "Schulenburg", EXISTING["schulenburg"], "Subject of the younger men's reported descriptions.", 1),
    ("he-remained", 15, "he", EXISTING["schulenburg"], "Corefers to Schulenburg.", 0),
    ("will", 15, "The will that he drew up in 1740", candidate_by_key["schulenburg_will"], "Unverified archival object described by Haskell; note the nested Schulenburg coreference."),
    ("he-drew-up-will", 15, "he", EXISTING["schulenburg"], "Corefers to Schulenburg within the will mention.", 1),
    ("he-no-children", 15, "he", EXISTING["schulenburg"], "Corefers to Schulenburg.", 2),
]
for spec in M:
    add_mention(*spec)

for index, left in enumerate(new_mentions):
    left_start, left_end = int(left["start_char"]), int(left["end_char"])
    for right in new_mentions[index + 1:]:
        right_start, right_end = int(right["start_char"]), int(right["end_char"])
        if max(left_start, right_start) < min(left_end, right_end):
            nested = ((left_start <= right_start and right_end <= left_end) or
                      (right_start <= left_start and left_end <= right_end))
            if not nested or left["candidate_id"] == right["candidate_id"] or (left_start == right_start and left_end == right_end):
                raise SystemExit(f"invalid mention overlap: {left['mention_id']} / {right['mention_id']}")

new_statements = []
new_statement_ids = set()


def add_statement(sid, subject, obj, predicate, claim, line_start, line_end, qualification,
                  mentioned, relation=False, marker=None, speaker="Haskell", layer="authorial narrative",
                  quote_override=None):
    if sid in statement_ids or sid in new_statement_ids:
        raise SystemExit(f"duplicate statement ID: {sid}")
    for cid in (subject, obj, *mentioned):
        if cid and cid not in all_candidate_ids:
            raise SystemExit(f"missing candidate FK for {sid}: {cid}")
    quote = quote_override if quote_override is not None else "\n".join(source_lines[line_start - 1:line_end])
    source_span = "\n".join(source_lines[line_start - 1:line_end])
    if quote not in source_span:
        raise SystemExit(f"statement quote cannot be reproduced from source lines for {sid}")
    qualifiers = {
        "source_line_start": line_start, "source_line_end": line_end,
        "printed_page": PRINTED_PAGE, "pdf_physical_page": PHYSICAL_PAGE,
        "claim": claim, "speaker": speaker, "text_layer": layer,
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
        "relation_candidate": relation,
    }
    if marker is not None:
        qualifiers["footnote_marker"] = marker
        qualifiers["footnote_text_pending"] = True
    new_statements.append({
        "statement_id": sid, "segment_id": SEGMENT,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote, "origin": "book", "source_file": SOURCE_FILE,
    })
    new_statement_ids.add(sid)


S = EXISTING["schulenburg"]
R = EXISTING["republic_venice"]
E = EXISTING["eugene"]
CORFU_EVENT = candidate_by_key["corfu_defense"]
ARTS = candidate_by_key["corfu_commemorative_works"]
ROYAL_PORTRAITS = candidate_by_key["loredan_dynastic_portraits"]
add_statement("st-chp10-p311-schulenburg-birth-and-origin", S, None,
              "born_in_1661_to_saxon_family",
              "Haskell says Johann Matthias Schulenburg came from a Saxon family and was born in 1661.",
              8, 8, "The particular Saxon family is not identified. Footnote 1 is pending review.",
              [S], marker=1)
add_statement("st-chp10-p311-schulenburg-studied-in-france-and-germany", S, None,
              "studied_in_france_and_germany",
              "Haskell says Schulenburg studied in France and Germany before his military career.",
              9, 9, "No institutions or dates of study are given.",
              [S, EXISTING["france"], EXISTING["germany"]])
add_statement("st-chp10-p311-schulenburg-professional-soldier", S, None,
              "served_as_professional_soldier_in_european_wars",
              "Haskell describes Schulenburg as a professional soldier in most of the major European wars around the turn of the century.",
              9, 9, "This is a broad summary, not an exhaustive list of campaigns.",
              [S, EXISTING["europe"]])
add_statement("st-chp10-p311-schulenburg-fought-for-hungarians", S, candidate_by_key["hungarian_forces"],
              "fought_for_hungarian_forces",
              "Haskell says Schulenburg fought for the Hungarians.",
              10, 10, "The source does not identify a ruler, army, or unit; relation endpoint remains a source-level collective.",
              [S, candidate_by_key["hungarian_forces"]], relation=True)
add_statement("st-chp10-p311-schulenburg-fought-for-house-of-savoy", S, candidate_by_key["house_savoy"],
              "fought_for_dynastic_house",
              "Haskell says Schulenburg fought for the House of Savoy.",
              10, 10, "Keep the dynastic house distinct from the geographic candidate Savoy; no dates or specific unit are given.",
              [S, candidate_by_key["house_savoy"]], relation=True)
add_statement("st-chp10-p311-schulenburg-fought-for-saxons-against-charles-xii", S, EXISTING["charles_xii"],
              "fought_for_saxons_against_charles_xii",
              "Haskell says Schulenburg fought for the Saxons in several engagements against Charles XII of Sweden and liked to talk about them later.",
              10, 10, "The Saxon force is not specified. The later recollection is reported by Haskell, not independently sourced here.",
              [S, candidate_by_key["saxon_forces"], EXISTING["charles_xii"]], relation=True)
add_statement("st-chp10-p311-schulenburg-served-under-eugene-at-malplaquet", S, E,
              "served_under_prince_eugene_at_malplaquet",
              "Haskell places Schulenburg's service under Prince Eugene at Malplaquet during the War of the Spanish Succession.",
              10, 10, "The source names Malplaquet but gives no date or more specific unit; preserve the cited war context without adding an event date.",
              [S, E, EXISTING["spanish_succession"], candidate_by_key["malplaquet"]], relation=True)
add_statement("st-chp10-p311-eugene-recommended-schulenburg-to-republic", E, S,
              "recommended_schulenburg_to_venetian_republic",
              "Haskell says that in 1715 Prince Eugene advised the Republic of Venice to turn to Schulenburg for help against the Turks.",
              10, 10, "The pronoun 'them' refers to the Republic in context. This records Haskell's account of a recommendation, not a surviving appointment document.",
              [E, S, R, candidate_by_key["turkish_forces"]], relation=True)
add_statement("st-chp10-p311-schulenburg-defended-corfu-1715-1716", EXISTING["schulenburg_corfu_index"], CORFU_EVENT,
              "defended_corfu_against_turkish_attacks",
              "Haskell says Schulenburg's defense of Corfu against Turkish attacks in 1715 and 1716 justified Eugene's recommendation.",
              10, 10, "'Brilliant' is Haskell's evaluation. The 1715–1716 campaign is kept distinct from the existing 1716 siege candidate cand-8119 pending S3.",
              [S, EXISTING["corfu"], CORFU_EVENT, candidate_by_key["turkish_forces"]], relation=True,
              layer="authorial narrative with evaluative wording")
add_statement("st-chp10-p311-schulenburg-commissioned-corfu-memorial-works", S, ARTS,
              "commissioned_artworks_commemorating_corfu_campaign",
              "Haskell says Schulenburg commissioned some of the unnamed works of art commemorating the Corfu campaign.",
              10, 10, "No titles, makers, media, or number of works are specified.",
              [S, CORFU_EVENT, ARTS], relation=True)
add_statement("st-chp10-p311-venetian-state-commissioned-corfu-memorial-works", R, ARTS,
              "commissioned_artworks_commemorating_corfu_campaign",
              "Haskell says the Venetian State also commissioned unnamed works of art commemorating the Corfu campaign.",
              10, 10, "The source says 'the State'; its identification with the Venetian Republic follows the immediate context. No individual commissions are identified.",
              [R, CORFU_EVENT, ARTS], relation=True)
add_statement("st-chp10-p311-venice-honored-schulenburg-with-statue-and-pension", R, S,
              "honored_with_statue_and_life_pension",
              "Haskell says Venice erected a statue to Schulenburg and awarded him a life pension of 5,000 ducats a year.",
              10, 11, "The amount and lifetime status follow the book's wording; the specific statue and pension records are not identified here. Footnote 2 is pending review.",
              [R, S, candidate_by_key["schulenburg_statue"]], relation=True, marker=2)
add_statement("st-chp10-p311-schulenburg-continued-to-serve-republic", S, R,
              "continued_to_serve_venetian_republic",
              "Haskell says Schulenburg continued to serve the Republic after the Corfu defense, although no further opportunity for actual fighting arose.",
              11, 11, "Continued service is not equated with further combat or a specific office.",
              [S, R], relation=True)
add_statement("st-chp10-p311-schulenburg-travel-and-settlement", S, None,
              "travelled_europe_and_settled_in_venetian_territory",
              "Haskell says Schulenburg travelled in Italy and to London, Berlin, Dresden, and Holland before settling in Venetian territory.",
              11, 12, "The itinerary is given without dates or route order. 'Venetian territory' is retained without inferring a precise settlement location.",
              [S, EXISTING["italy"], EXISTING["london"], EXISTING["berlin"], EXISTING["dresden"], EXISTING["holland"]])
add_statement("st-chp10-p311-schulenburg-last-years-and-funeral-at-verona", S, EXISTING["verona"],
              "spent_last_years_between_venice_and_verona_died_and_was_buried_at_verona",
              "Haskell says Schulenburg divided his last years between Venice and Verona, where he died and received a splendid funeral in 1747.",
              12, 12, "The relative 'where' most directly refers to Verona; the scan confirms 1747 and footnote 3 is pending review.",
              [S, EXISTING["venice"], EXISTING["verona"]], marker=3)
add_statement("st-chp10-p311-schulenburg-grandiose-retirement", S, None,
              "described_as_grandiose_in_retirement",
              "Haskell characterizes Schulenburg as a grandiose figure in retirement.",
              13, 13, "This is Haskell's evaluative characterization, not a neutral biographical attribute.",
              [S], layer="authorial evaluation")
add_statement("st-chp10-p311-schulenburg-related-to-hanoverian-dynasty", S, candidate_by_key["hanoverian_dynasty"],
              "closely_related_to_dynasty",
              "Haskell says Schulenburg was closely related to the Hanoverian dynasty.",
              13, 13, "No particular relative or line of descent is named; retain the relationship at the source's broad level.",
              [S, candidate_by_key["hanoverian_dynasty"]], relation=True)
add_statement("st-chp10-p311-schulenburg-friendly-with-crowned-heads", S, candidate_by_key["crowned_heads_group"],
              "on_friendly_terms_with_crowned_heads",
              "Haskell says Schulenburg was on friendly terms with 'half the crowned heads of Europe'.",
              13, 14, "'Half' is the source's generalization; the individuals are not enumerated.",
              [S, candidate_by_key["crowned_heads_group"], EXISTING["europe"]],
              layer="authorial narrative with generalized quantity")
add_statement("st-chp10-p311-dynastic-portraits-at-palazzo-loredan", ROYAL_PORTRAITS,
              candidate_by_key["palazzo_loredan"], "portraits_displayed_at_residence",
              "Haskell says portraits representing Bourbons, Hapsburgs, Farneses, and Hohenzollerns lined the walls of Schulenburg's Palazzo Loredan residence.",
              14, 14, "The passage does not identify individual sitters, portrait titles, artists, or dates; dynastic labels are not treated as specific people.",
              [ROYAL_PORTRAITS, candidate_by_key["bourbon_dynasty"], candidate_by_key["hapsburg_dynasty"],
               EXISTING["farnese_family"], candidate_by_key["hohenzollern_dynasty"], candidate_by_key["palazzo_loredan"]],
              relation=True)
add_statement("st-chp10-p311-crowned-heads-visited-and-sought-advice", candidate_by_key["crowned_heads_group"], S,
              "visited_and_wrote_for_help_or_advice",
              "Haskell says the crowned heads visited Schulenburg in Venice and wrote to him for help and advice.",
              14, 14, "The visitors and letters are not individually identified; do not infer the identity of any correspondent from this aggregate statement.",
              [candidate_by_key["crowned_heads_group"], S, EXISTING["venice"]])
add_statement("st-chp10-p311-frederick-requested-young-castrato", EXISTING["frederick"], S,
              "requested_a_young_castrato",
              "Haskell says Crown Prince Frederick of Prussia asked Schulenburg to find a castrato aged 14 or 15, but Schulenburg found only a woman described as nearly thirty.",
              14, 14, "The unnamed castrato and woman are not independent identities in this passage; preserve the French wording and do not infer who either person was. Footnote 4 is pending review.",
              [EXISTING["frederick"], S], marker=4,
              layer="reported anecdote with embedded French quotation")
add_statement("st-chp10-p311-schulenburg-talked-about-women", S, None,
              "talked_to_guests_about_women",
              "Haskell says Schulenburg liked to talk with his guests about women.",
              14, 14, "This is a reported characterization; p.311 footnote 5 remains pending review.",
              [S], marker=5)
add_statement("st-chp10-p311-schulenburg-questioned-unnamed-nobleman-about-health", S,
              candidate_by_key["unnamed_english_nobleman"], "summoned_doctor_and_questioned_nobleman_about_illness",
              "Haskell recounts that Schulenburg summoned a doctor for an unnamed young English nobleman and required the doctor to say whether the nobleman had clap.",
              14, 15, "The OCR reads 'claps'; the printed p.311 scan reads 'clapt'. The young nobleman is not identified, and the connection between footnote 6's letter citation and this person remains unverified.",
              [S, candidate_by_key["unnamed_english_nobleman"]], marker=6,
              layer="reported anecdote with embedded quotation")
add_statement("st-chp10-p311-younger-men-called-schulenburg-old-fellow", S, None,
              "younger_men_described_schulenburg_as_old_fellow",
              "Haskell reports that younger men called Schulenburg 'un vieux bonhomme' or 'the oddest old fellow in the world'.",
              15, 15, "These are attributed descriptions by unnamed younger men, not neutral facts about Schulenburg.",
              [S], speaker="Younger men, as reported by Haskell", layer="reported quoted characterization")
add_statement("st-chp10-p311-haskell-described-schulenburg-as-proud-and-rude", S, None,
              "described_as_amiable_proud_and_sometimes_rude",
              "Haskell says Schulenburg could be amiable but was excessively proud and could be very rude.",
              15, 15, "This is Haskell's evaluative characterization.",
              [S], layer="authorial evaluation")
will_quote = "The will that he drew up in 1740 reveals a commanding spirit, keen to assert its authority over distant descendants—he had no children of his own"
add_statement("st-chp10-p311-will-asserted-authority-no-children", candidate_by_key["schulenburg_will"], S,
              "will_described_as_asserting_authority_over_descendants",
              "Haskell says Schulenburg's 1740 will revealed a commanding spirit asserting authority over distant descendants, while noting that he had no children of his own.",
              15, 15, "The source sentence continues on printed p.312 after 'and determined to maintain'; the continuation and object of 'maintain' are deferred. The will itself has not been independently consulted.",
              [candidate_by_key["schulenburg_will"], S], layer="authorial interpretation of an archival document",
              quote_override=will_quote)

coverage[SEGMENT].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L7-15",
    "note": "Printed p.311 body checked against CHP-10.pdf physical page 40. The source marker [Page 1661] is inconsistent with the printed page; scan confirms p.311. S2 records OCR corrections 'scries'→'series', 'I747?'→1747 with marker 3, and 'claps'→'clapt' without altering S0. Sentence at L15 continues at L18 on p.312; body footnote markers 1–6 point to the later notes block and remain pending, so this segment is partial until cross-page and note links close."
})

args = argparse.ArgumentParser()
args.add_argument("--apply", action="store_true")
apply = args.parse_args().apply
report = {
    "mode": "APPLY" if apply else "DRY-RUN", "segment": SEGMENT,
    "new_candidates": len(new_candidates), "new_mentions": len(new_mentions),
    "new_statements": len(new_statements), "coverage": "reviewed/partial L7-15",
    "next_source_segment": "chp-10:10_CHP-10_sec_ii:l17-32",
    "candidate_ids": [row["candidate_id"] for row in new_candidates],
    "statement_ids": [row["statement_id"] for row in new_statements],
}
print(json.dumps(report, ensure_ascii=False, indent=2))
if apply:
    for path in (candidate_path, mention_path, statement_path, coverage_path):
        backup = Path(str(path) + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists: {backup}")
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates + new_candidates)
    write_csv(mention_path, mention_fields, mentions + new_mentions)
    write_jsonl(statement_path, statements + new_statements)
    write_csv(coverage_path, coverage_fields, [coverage[row["segment_id"]] for row in coverage_rows])
    print("Applied with four recoverable backups.")
