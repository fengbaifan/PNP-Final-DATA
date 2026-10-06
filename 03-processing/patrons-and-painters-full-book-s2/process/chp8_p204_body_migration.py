"""Controlled S2 migration for chapter 8 printed p.204 body text.

Default invocation is a read-only dry run. Source OCR stays unchanged; print
readings confirmed against CHP-8.pdf are preserved in statement qualifiers.
"""
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
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_i.md"
SOURCE_PATH = ROOT / SOURCE_REL
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l14-21"
PREVIOUS_SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l3-12"
PREVIOUS_STATEMENT_ID = "st-chp8-p203-merchant-group-open-continuation"
BACKUP_SUFFIX = ".bak-s2-chp8-p204-body-20260930"
EXPECTED_MAX_CANDIDATE = 7390


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl_atomic(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
segment_path = TABLES / "segments.jsonl"
candidate_fields, candidate_rows = read_csv(candidate_path)
mention_fields, mention_rows = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statement_rows = read_jsonl(statement_path)
segment_rows = read_jsonl(segment_path)
segments = {row["segment_id"]: row for row in segment_rows}
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}

meta = segments.get(SEGMENT_ID)
if not meta or meta["source_file"] != SOURCE_REL or (int(meta["line_start"]), int(meta["line_end"])) != (14, 21):
    raise SystemExit("p.204 segment metadata changed; review before migration")
raw_source = SOURCE_PATH.read_bytes()
if hashlib.sha256(raw_source).hexdigest() != meta["asset_sha256"]:
    raise SystemExit("source file fingerprint changed; rebuild segments and review")
source_lines = SOURCE_PATH.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[13:21])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != meta["sha256"]:
    raise SystemExit("p.204 segment text hash changed; review before migration")
if coverage_by_id.get(SEGMENT_ID, {}).get("disposition") != "queued":
    raise SystemExit("expected queued p.204 coverage; inspect before rerunning")
if any(row["segment_id"] == SEGMENT_ID for row in mention_rows):
    raise SystemExit("mentions already exist for p.204; inspect before rerunning")
if any(row["segment_id"] == SEGMENT_ID for row in statement_rows):
    raise SystemExit("statements already exist for p.204; inspect before rerunning")

candidate_ids = {row["candidate_id"] for row in candidate_rows}
existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_statement_ids = {row["statement_id"] for row in statement_rows}
current_max = max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows)
if current_max != EXPECTED_MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: expected {EXPECTED_MAX_CANDIDATE}, found {current_max}")


def candidate(cid, name, typ, detail, line):
    return {
        "candidate_id": cid,
        "index_entry_id": "",
        "canonical_name": name,
        "index_page_range": "",
        "suggested_type": typ,
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": detail,
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L{line}",
    }


new_candidates = [
    candidate("cand-7391", "Unidentified pictures painted by Giuseppe Maria Crespi for Giovanni Ricci", "work", "Collective works mentioned as painted for Ricci; no individual title, date, medium, or present location is supplied in the body passage.", 15),
    candidate("cand-7392", "Central Italy", "place", "Region named as one destination of Ricci's trips with Crespi; the source gives no route or more exact boundary.", 15),
    candidate("cand-7393", "Shaftesbury named as Giuseppe Valletta's friend", "person", "The body gives only the surname. Identity relative to the indexed Shaftesbury candidates is intentionally deferred to S3.", 18),
    candidate("cand-7394", "Great Roman picture collections in Haskell's p.204 comparison", "", "Collective collection reference, not one named collection; the current taxonomy has no collection type, so preserve as type-undetermined.", 21),
    candidate("cand-7395", "Enlightened despots in Haskell's account of early eighteenth-century Italy", "term", "Unnamed collective political actors associated with reforms; no rulers, states, or measures are identified in this sentence.", 21),
    candidate("cand-7396", "Italian city-states whose cosmopolitan importance revived", "term", "Collective political category in the early eighteenth-century comparison; the particular states are not enumerated.", 21),
    candidate("cand-7397", "Classical-Venetian synthesis in Haskell's account of Cassiano dal Pozzo", "term", "Haskell's interpretive description of a combination of artistic sensibilities; retain it as an attributed analytical concept.", 21),
    candidate("cand-7398", "Cassiano dal Pozzo and his circle as a patronage-intellectual group", "term", "Collective reference in Haskell's example; the membership of the circle is not given here.", 21),
    candidate("cand-7399", "Italian patrons who collected beyond their native towns (unnamed group)", "term", "Haskell's group of expatriates or citizens whose collections included works by foreign artists; no members are named in the passage.", 21),
    candidate("cand-7400", "Unidentified Venetian painter in Haskell's Bologna-Genoa comparison", "term", "Unnamed artist category in the example of a Venetian picture rarely found in Genoa; no individual painter or work is identified.", 21),
]
new_candidate_ids = {row["candidate_id"] for row in new_candidates}
if len(new_candidate_ids) != len(new_candidates) or new_candidate_ids & candidate_ids:
    raise SystemExit("planned candidate ID collision")
existing_natural_keys = {(row["canonical_name"].casefold(), row["suggested_type"].casefold()) for row in candidate_rows}
for row in new_candidates:
    key = (row["canonical_name"].casefold(), row["suggested_type"].casefold())
    if key in existing_natural_keys:
        raise SystemExit(f"candidate natural-key duplicate: {row['canonical_name']} ({row['suggested_type']})")
    existing_natural_keys.add(key)

mention_specs = []


def add_mention(surface, cid, note, occurrence=1):
    mention_specs.append((surface, cid, note, occurrence))


add_mention("Giovanni Ricci", "cand-2148", "Index subentry for Ricci's patronage of Crespi on p.204.")
add_mention("Burrini", "cand-0473", "Artist named among Ricci's admired contemporary painters.")
add_mention("Crespi", "cand-0871", "Giuseppe Maria Crespi; first p.204 occurrence, described as young.", 1)
add_mention("Crespi", "cand-0872", "Index candidate for Crespi and G. Ricci; this occurrence identifies pictures painted for Ricci.", 2)
add_mention("pictures that Crespi painted for him", "cand-7391", "Unidentified works by Crespi for Ricci, nested within the artist mention.")
add_mention("Bologna", "cand-0381", "City where Crespi is described as working in a provincial atmosphere.", 1)
add_mention("Venice", "cand-3401", "Destination of Crespi's reported visits with Ricci.", 1)
add_mention("Central Italy", "cand-7392", "Second destination named for Crespi's visits.")
add_mention("Ricci", "cand-2148", "Short form in the sentence describing Ricci's activity as a dealer.", 2)
add_mention("Crespi", "cand-0872", "Index subentry matches the Ricci-Crespi dealings; third p.204 occurrence.", 3)
add_mention("Crespi", "cand-0872", "Crespi named as the beneficiary of the dealer arrangement; fourth p.204 occurrence.", 4)
add_mention("Naples", "cand-1722", "City whose lawyers are described as important arts patrons.")
add_mention("Giuseppe\nValletta", "cand-2686", "Index candidate with p.204 coverage; the name is split across source lines.")
add_mention("Shaftesbury", "cand-7393", "Surname only in this body passage; do not select an indexed earl before S3.")
add_mention("Luca Giordano", "cand-1172", "Painter named as one of Valletta's clients/patrons.")
add_mention("Solimena", "cand-2484", "Painter named as one of Valletta's clients/patrons.")
add_mention("Italy", "cand-3461", "Place in which painting's survival is discussed.", 1)
add_mention("Barberini", "cand-3464", "Family named as the Rome-based patronage climate's example.")
add_mention("their circle", "cand-4969", "Unspecified wider Barberini artistic/intellectual circle; this remains separate from the family entity.")
add_mention("Rome", "cand-4490", "Location of the Barberini family and circle.", 1)
add_mention("Italy", "cand-3461", "Country described as under foreign domination.", 2)
add_mention("Venice", "cand-3401", "Possible exception to the provincial status of the Italian cities.", 2)
add_mention("Rome", "cand-4490", "City characterized as Italy's only competing capital between about 1600 and 1670.", 2)
add_mention("Europe", "cand-3462", "Nation-state towns in Europe are the prestige comparison.", 1)
add_mention("Italy", "cand-3461", "Country in the prestige comparison of Rome with the leading towns of European nation-states.", 3)
add_mention("Italy", "cand-3461", "Country in the early eighteenth-century revival account.", 4)
add_mention("Spain", "cand-4591", "State named in the decline-of-Spain clause; cross-chapter identity alignment remains open.")
add_mention("enlightened despots", "cand-7395", "Unnamed collective actors associated with reforms.")
add_mention("Italian city states", "cand-7396", "Collective category whose cosmopolitan importance was revived.")
add_mention("professional classes", "cand-2065", "Index candidate for professional-class patronage in Italian provinces.")
add_mention("local schools of painting", "cand-7380", "Collective painting-school category introduced on p.203 and revisited here.")
add_mention("Roman collections", "cand-7394", "Collective collection reference; no individual collection is identified.")
add_mention("Roman", "cand-4490", "Place demonym nested within the Roman collections mention.")
add_mention("Italy", "cand-3461", "Artists represented in Roman collections are described as coming from Italy.", 5)
add_mention("Europe", "cand-3462", "Artists represented in Roman collections also came from Europe.", 2)
add_mention("classical-Venetian synthesis", "cand-7397", "Haskell's analytical phrase for a combination of artistic sensibilities.")
add_mention("Cassiano dal Pozzo", "cand-2036", "Historical person named as an example associated with the synthesis.")
add_mention("Cassiano dal Pozzo and his circle", "cand-7398", "Named person and unnamed circle as a collective example; the person mention is nested.")
add_mention("Bologna", "cand-0381", "City in the example of a contemporary Neapolitan picture being rare.", 2)
add_mention("Neapolitan", "cand-1722", "Demonym for the unnamed contemporary painter in the Bologna example.")
add_mention("Genoa", "cand-1131", "City in the example of a Venetian picture being rare.")
add_mention("Venetian", "cand-7400", "Unnamed painter category in the Genoa comparison; this is the second Venetian occurrence in the segment.", 2)
add_mention("Italy", "cand-3461", "Country containing the few patrons who looked beyond their native towns.", 6)
add_mention("a few patrons within Italy itself, either expatriates or citizens", "cand-7399", "Unnamed translocal patron group; exact membership and locations are not supplied.")

new_mentions = []
for index, (surface, cid, note, occurrence) in enumerate(mention_specs, 1):
    if cid not in candidate_ids | new_candidate_ids:
        raise SystemExit(f"mention references missing candidate: {cid}")
    starts = []
    cursor = 0
    while True:
        found = segment_text.find(surface, cursor)
        if found < 0:
            break
        starts.append(found)
        cursor = found + 1
    if occurrence > len(starts):
        raise SystemExit(f"surface occurrence {occurrence} missing for {surface!r}; found {len(starts)}")
    start = starts[occurrence - 1]
    end = start + len(surface)
    if segment_text[start:end] != surface:
        raise SystemExit(f"mention offset mismatch for {surface!r}")
    new_mentions.append({
        "mention_id": f"m-chp8-p204-{index:03d}",
        "segment_id": SEGMENT_ID,
        "candidate_id": cid,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    })

new_mentions.sort(key=lambda row: (int(row["start_char"]), int(row["end_char"])))
for i, first in enumerate(new_mentions):
    if first["mention_id"] in existing_mention_ids:
        raise SystemExit(f"mention ID collision: {first['mention_id']}")
    for second in new_mentions[i + 1:]:
        a, b = int(first["start_char"]), int(first["end_char"])
        c, d = int(second["start_char"]), int(second["end_char"])
        if a < d and c < b:
            nested = (a <= c and d <= b and (a, b) != (c, d)) or (c <= a and b <= d and (a, b) != (c, d))
            if not nested:
                raise SystemExit(f"overlapping non-nested mentions: {first!r} / {second!r}")


def quote_between(start_token, end_token):
    start = segment_text.find(start_token)
    if start < 0:
        raise SystemExit(f"quote start token missing: {start_token!r}")
    stop = segment_text.find(end_token, start + len(start_token))
    if stop < 0:
        raise SystemExit(f"quote end token missing: {end_token!r}")
    return segment_text[start:stop + len(end_token)]


def statement(sid, start, end, predicate, claim, qualification, *, subject=None, obj=None,
              mentioned=(), quote=None, extra=None):
    qualifiers = {
        "source_line_start": start,
        "source_line_end": end,
        "printed_page": 204,
        "pdf_physical_page": 2,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "body",
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    if extra:
        qualifiers.update(extra)
    return {
        "statement_id": sid,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote or "\n".join(source_lines[start - 1:end]),
        "origin": "book",
        "source_file": SOURCE_REL,
    }


body_statements = [
    statement("st-chp8-p204-ricci-leading-patron", 15, 15, "described_as_most_cultivated_and_interesting_merchant",
              "Continuing p.203, Haskell identifies Giovanni Ricci as the most cultivated and interesting member of the small group of enlightened merchants.",
              "The superlative is Haskell's characterization; the first half of the sentence is anchored in the preceding p.203 segment.", subject="cand-2148",
              mentioned=["cand-2148"], quote=quote_between("group of enlightened merchants", "Giovanni Ricci."),
              extra={"footnote_marker": 1, "continuation_of_statement_id": PREVIOUS_STATEMENT_ID}),
    statement("st-chp8-p204-ricci-admired-contemporary-artists", 15, 15, "patron_appreciated_contemporary_artists",
              "Haskell says Ricci was a rich and discriminating patron who appreciated many contemporary artists, especially Burrini and the young Crespi.",
              "The passage gives examples rather than a complete list of artists or commissions.", subject="cand-2148",
              mentioned=["cand-2148", "cand-0473", "cand-0871"],
              quote=quote_between("He was a rich and discriminating patron", "above all Burrini and the young Crespi.")),
    statement("st-chp8-p204-ricci-sent-crespi-to-absorb-influences", 15, 15, "patron_sent_artist_on_study_travel",
              "Haskell says Ricci judged Bologna's provincial atmosphere likely to stifle Crespi's imaginative gifts and sent him on long visits to Venice and Central Italy to absorb varied influences.",
              "The assessment of Crespi's gifts and the causal account of travel are Haskell's interpretation; no dates or exact itinerary are supplied.",
              subject="cand-2148", obj="cand-0872", mentioned=["cand-2148", "cand-0872", "cand-0381", "cand-3401", "cand-7392"],
              quote=quote_between("He soon realised", "long visits to Venice and Central Italy"),
              extra={"footnote_marker": 2, "ocr_corrections": [{"source_line": 15, "ocr": "latter��s", "print": "latter's", "basis": "CHP-8.pdf physical page 2."}]}),
    statement("st-chp8-p204-crespi-paintings-reflect-travel-influences", 15, 15, "artist_work_reflected_absorbed_influences",
              "Haskell says the influences acquired on Crespi's visits soon appeared in pictures he painted for Ricci.",
              "The pictures are not individually identified; candidate cand-7391 records the group without implying a complete surviving corpus.",
              subject="cand-7391", obj="cand-2148", mentioned=["cand-7391", "cand-0872", "cand-2148", "cand-3401", "cand-7392"],
              quote=quote_between("influences which soon made themselves felt", "pictures that Crespi painted for him.")),
    statement("st-chp8-p204-ricci-dealer-terms", 16, 16, "dealer_agreed_to_buy_available_work_and_transfer_profits",
              "Haskell says Ricci acted as Crespi's dealer on unusual terms: he agreed to buy any of the painter's work that became available and passed all resale profits to Crespi.",
              "No dates, number of works, or legal contract are supplied; the passage reports an arrangement rather than a documented contract.",
              subject="cand-2148", obj="cand-0872", mentioned=["cand-2148", "cand-0872"],
              quote=quote_between("Ricci also acted as a dealer", "over all the profits to him"),
              extra={"ocr_corrections": [{"source_line": 16, "ocr": "painter��s", "print": "painter's", "basis": "CHP-8.pdf physical page 2."}]}),
    statement("st-chp8-p204-crespi-biographer-evaluates-ricci-treatment", 16, 16, "biographer_evaluated_patronage_arrangement",
              "The artist's unnamed biographer, as quoted by Haskell, says Ricci's treatment was unusually noble and generous and greatly benefited Crespi.",
              "The biographer is not named in this passage. Preserve the nested reporting: Haskell quotes an unidentified biographer; the cited work is addressed in note 1.",
              subject="cand-2148", obj="cand-0872", mentioned=["cand-2148", "cand-0872"],
              quote=quote_between("and it is certain", "enormous advantage to Crespi"),
              extra={"speaker": "Crespi's unnamed biographer, quoted by Haskell", "ocr_corrections": [{"source_line": 16, "ocr": "��and it is certain��", "print": "'and it is certain'", "basis": "CHP-8.pdf physical page 2."}]}),
    statement("st-chp8-p204-naples-lawyers-supported-arts", 17, 18, "professional_lawyers_prominent_as_arts_patrons",
              "Haskell says lawyers were especially prominent in supporting the arts in Naples and had a vital role in the city's cultural life.",
              "This is a collective characterization; the sentence introduces Giuseppe Valletta as its leading example.",
              subject="cand-1722", mentioned=["cand-1722", "cand-2686"],
              quote=quote_between("In Naples the lawyers", "support of the arts.")),
    statement("st-chp8-p204-valletta-professions", 17, 18, "identified_as_poet_and_arbiter_of_taste",
              "Haskell describes Giuseppe Valletta as a poet and arbiter of taste.",
              "Roles are recorded as Haskell presents them; no dates or institutional office are supplied.",
              subject="cand-2686", mentioned=["cand-2686"], quote=quote_between("Giuseppe\nValletta", "poet and arbiter of taste")),
    statement("st-chp8-p204-valletta-friend-of-shaftesbury", 18, 18, "friendship_with_person",
              "Haskell says Valletta was a friend of Shaftesbury.",
              "The body gives only the surname Shaftesbury; person identity remains unresolved for S3.",
              subject="cand-2686", obj="cand-7393", mentioned=["cand-2686", "cand-7393"], quote="friend of Shaftesbury"),
    statement("st-chp8-p204-valletta-patron-of-giordano", 18, 18, "patron_of_artist",
              "Haskell identifies Valletta as a patron of Luca Giordano.",
              "No specific commission, date, or work is named in the body sentence; footnote 3 adds reported examples and remains to be processed.",
              subject="cand-2686", obj="cand-1172", mentioned=["cand-2686", "cand-1172"], quote="the patron of Luca Giordano"),
    statement("st-chp8-p204-valletta-patron-of-solimena", 18, 18, "patron_of_artist",
              "Haskell identifies Valletta as a patron of Solimena.",
              "No specific commission, date, or work is named in the body sentence; footnote 3 remains to be processed.",
              subject="cand-2686", obj="cand-2484", mentioned=["cand-2686", "cand-2484"], quote="and Solimena.",
              extra={"footnote_marker": 3}),
    statement("st-chp8-p204-provincial-patrons-could-not-recreate-rome", 19, 19, "local_patrons_could_not_create_roman_patronage_climate",
              "Haskell says these local patrons were crucial to painting's survival in Italy but could not create the climate established by the Barberini family and their circle in Rome.",
              "This is the author's comparative interpretation, not a claim that local support was unimportant. 'These men' refers to the preceding Naples lawyers and patrons.",
              subject="cand-2065", obj="cand-4969", mentioned=["cand-2065", "cand-3461", "cand-3464", "cand-4969", "cand-4490"],
              quote=quote_between("However, all these men", "circle in Rome."),
              extra={"ocr_corrections": [{"source_line": 19, "ocr": "men��and", "print": "men—and", "basis": "CHP-8.pdf physical page 2."}, {"source_line": 19, "ocr": "them��crucial", "print": "them—crucial", "basis": "CHP-8.pdf physical page 2."}]}),
    statement("st-chp8-p204-italian-cities-remained-provincial", 20, 20, "cities_remained_provincial_after_foreign_domination_and_peace",
              "Haskell says Italy's general collapse under foreign domination and the peace that followed left its cities essentially provincial, possibly excepting Venice.",
              "The exception is explicitly qualified as possible; the sentence does not identify a single foreign power or peace treaty.",
              subject="cand-3461", mentioned=["cand-3461", "cand-3401"],
              quote=quote_between("With the general collapse", "remained essentially provincial."),
              extra={"ocr_corrections": [{"source_line": 20, "ocr": "only ��capital��", "print": "only 'capital'", "basis": "CHP-8.pdf physical page 2."}]}),
    statement("st-chp8-p204-rome-only-competing-italian-capital", 20, 20, "rome_only_italian_capital_competing_in_prestige",
              "Haskell says that between about 1600 and 1670 Rome was the only Italian capital able to compete in prestige with the principal towns of Europe's nation-states.",
              "The time span is approximate and the comparison is about prestige, not administrative status.",
              subject="cand-4490", obj="cand-3462", mentioned=["cand-4490", "cand-3461", "cand-3462"],
              quote=quote_between("Between about 1600 and 1670", "nation states of Europe.")),
    statement("st-chp8-p204-early-eighteenth-century-revival", 20, 21, "historical_factors_revived_city_state_cosmopolitanism",
              "Haskell says wars, increased foreign travel, Spain's decline, and reforms by enlightened despots helped revive the cosmopolitan importance of some Italian city-states in the early eighteenth century.",
              "The source does not enumerate the wars, rulers, reforms, or city-states, and 'helped' does not assert a single cause.",
              subject="cand-7396", obj="cand-7395", mentioned=["cand-3461", "cand-4591", "cand-7395", "cand-7396"],
              quote=quote_between("At the beginning of the eighteenth century", "importance of some of the Italian city states.")),
    statement("st-chp8-p204-local-traditions-and-taste-stagnation", 21, 21, "local_patronage_preserved_schools_but_isolation_stagnated_taste",
              "Haskell says seventeenth-century Italian nobility and professional classes kept valuable local painting schools alive, while their isolation and strong local traditions led to stagnation of taste.",
              "This is Haskell's broad evaluative argument; 'certainly' and 'inevitably' are retained as his emphases, not independent measurements.",
              subject="cand-2065", obj="cand-7380", mentioned=["cand-3461", "cand-2065", "cand-7380"],
              quote=quote_between("During most of the seventeenth century", "led to a stagnation of taste."),
              extra={"ocr_corrections": [{"source_line": 21, "ocr": "hot only", "print": "not only", "basis": "CHP-8.pdf physical page 2; OCR error in the sentence's later clause."}]}),
    statement("st-chp8-p204-roman-collections-broadened-appreciation", 21, 21, "roman_collections_stimulated_broad_artistic_appreciation",
              "Haskell contrasts broad Roman collections of Italian and European artists with provincial collecting, saying they stimulated wide appreciation and new combinations of artistic sensibility, including a classical-Venetian synthesis associated with Cassiano dal Pozzo and his circle.",
              "The collections and artistic synthesis are collective/interpretive references; the passage names no specific collection or work and attributes the analysis to Haskell.",
              subject="cand-7394", obj="cand-7397", mentioned=["cand-7394", "cand-4490", "cand-3461", "cand-3462", "cand-7397", "cand-2036", "cand-7398"],
              quote=quote_between("Whereas the great Roman collections", "Cassiano dal Pozzo and his circle"),
              extra={"ocr_corrections": [{"source_line": 21, "ocr": "sensibility�� such", "print": "sensibility—such", "basis": "CHP-8.pdf physical page 2."}, {"source_line": 21, "ocr": "his circle��it", "print": "his circle—it", "basis": "CHP-8.pdf physical page 2."}]}),
    statement("st-chp8-p204-cross-regional-pictures-and-patrons", 21, 21, "cross_regional_pictures_rare_but_translocal_patrons_prevented_stagnation",
              "Haskell says contemporary Neapolitan pictures were rare in Bologna and Venetian pictures rare in Genoa, but not impossible; foreign intervention and a few Italian expatriate or citizen patrons who collected foreign art averted stagnation.",
              "The city examples are illustrative, not universal counts. Foreign intervention is not specified here; patron identities and works are unnamed.",
              subject="cand-7399", mentioned=["cand-7382", "cand-1722", "cand-0381", "cand-1131", "cand-3401", "cand-3461", "cand-7399", "cand-7400"],
              quote=quote_between("it was rare in Bologna", "works by foreign artists."),
              extra={"ocr_corrections": [{"source_line": 21, "ocr": "Rare��but", "print": "Rare—but", "basis": "CHP-8.pdf physical page 2."}]})
]

if len({row["statement_id"] for row in body_statements}) != len(body_statements):
    raise SystemExit("duplicate planned statement IDs")
new_statement_ids = {row["statement_id"] for row in body_statements}
if new_statement_ids & existing_statement_ids:
    raise SystemExit("planned statement ID collision")
for row in body_statements:
    q = row["qualifiers"]
    excerpt = "\n".join(source_lines[q["source_line_start"] - 1:q["source_line_end"]])
    if row["original_quote"] not in excerpt:
        raise SystemExit(f"quote is not reproducible in S0 source: {row['statement_id']}")
    if not (14 <= q["source_line_start"] <= q["source_line_end"] <= 21):
        raise SystemExit(f"statement line range outside segment: {row['statement_id']}")
    mentioned = set(q.get("mentioned_candidate_ids", []))
    if row.get("subject_candidate_id"):
        mentioned.add(row["subject_candidate_id"])
    if row.get("object_candidate_id"):
        mentioned.add(row["object_candidate_id"])
    if not mentioned <= candidate_ids | new_candidate_ids:
        raise SystemExit(f"statement references missing candidate: {row['statement_id']}")

previous_statement = next((row for row in statement_rows if row["statement_id"] == PREVIOUS_STATEMENT_ID), None)
if not previous_statement or previous_statement["qualifiers"].get("continuation_status") != "open":
    raise SystemExit("expected p.203 continuation statement to be open")
if coverage_by_id.get(PREVIOUS_SEGMENT_ID, {}).get("migration_status") != "partial":
    raise SystemExit("expected p.203 body coverage to be partial")

updated_coverage = []
for row in coverage_rows:
    row = dict(row)
    if row["segment_id"] == PREVIOUS_SEGMENT_ID:
        row.update({
            "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L3-12",
            "note": "P.203 body and note 5 are migrated; the closing sentence is completed by p.204 L15. OCR corrections remain in S2 qualifiers and S0 is unchanged.",
        })
    elif row["segment_id"] == SEGMENT_ID:
        row.update({
            "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L15-21",
            "note": "P.204 body read against CHP-8.pdf physical p.2. Closes the p.203 open sentence and records Ricci, Valletta, city comparisons, local patronage and cross-regional collecting. Footnotes 1-3 are in the later composite source segment L127-129 and remain to be migrated; S0 OCR remains unchanged.",
        })
    updated_coverage.append(row)

for row in body_statements:
    if row["statement_id"] == "st-chp8-p204-ricci-leading-patron":
        row["qualifiers"]["continuation_of_statement_id"] = PREVIOUS_STATEMENT_ID

preview = {
    "mode": "dry-run",
    "segment": SEGMENT_ID,
    "new_candidates": len(new_candidates),
    "candidate_ids": [row["candidate_id"] for row in new_candidates],
    "new_mentions": len(new_mentions),
    "new_statements": len(body_statements),
    "coverage": {PREVIOUS_SEGMENT_ID: "reviewed/complete", SEGMENT_ID: "reviewed/partial"},
    "footnotes_pending": ["p.204 notes 1-3 at source lines 127-129"],
    "ocr_corrections": ["latter��s -> latter's", "painter��s -> painter's", "men��and/them��crucial -> em dashes", "capital quote markers normalized", "hot only -> not only", "sensibility��/circle�� -> em dashes"],
    "mention_preview": [{"candidate_id": row["candidate_id"], "surface": row["surface_form"], "start": int(row["start_char"]), "end": int(row["end_char"])} for row in new_mentions],
    "statement_ids": [row["statement_id"] for row in body_statements],
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write validated tables and create recovery backups")
if not parser.parse_args().apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)

for path in (candidate_path, mention_path, statement_path, coverage_path):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(path, backup)

candidate_rows.extend(new_candidates)
mention_rows.extend(new_mentions)
statement_rows.extend(body_statements)
previous_statement["qualifiers"].update({
    "continuation_status": "completed",
    "continuation_completed_in_segment_id": SEGMENT_ID,
    "continuation_source_lines": [15],
    "continuation_note": "The p.203 phrase 'this little' continues on p.204 L15 as 'group of enlightened merchants was certainly Giovanni Ricci.'",
})
previous_statement["qualifiers"].pop("continuation_expected_segment_id", None)
write_csv_atomic(candidate_path, candidate_fields, candidate_rows)
write_csv_atomic(mention_path, mention_fields, mention_rows)
write_jsonl_atomic(statement_path, statement_rows)
write_csv_atomic(coverage_path, coverage_fields, updated_coverage)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
