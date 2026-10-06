"""Controlled S2 migration for chapter 8 printed p.203.

Default invocation is a read-only dry run. OCR source files stay unchanged;
confirmed print readings are recorded in statement qualifiers.
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
SOURCE_RELS = {
    "intro": "02-sources/02-Markdown/08_CHP-8_intro.md",
    "body": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
}
SEGMENT_IDS = {
    "intro_header": "chp-8:08_CHP-8_intro:l1-1",
    "intro_title": "chp-8:08_CHP-8_intro:l3-5",
    "intro_notes": "chp-8:08_CHP-8_intro:l7-10",
    "body_header": "chp-8:08_CHP-8_sec_i:l1-1",
    "body_p203": "chp-8:08_CHP-8_sec_i:l3-12",
    "body_p204": "chp-8:08_CHP-8_sec_i:l14-21",
}
BACKUP_SUFFIX = ".bak-s2-chp8-p203-20260930"
EXPECTED_MAX_CANDIDATE = 7356
EXPECTED_SEGMENTS = {
    "intro_header": (1, 1),
    "intro_title": (3, 5),
    "intro_notes": (7, 10),
    "body_header": (1, 1),
    "body_p203": (3, 12),
}


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
if len(segments) != len(segment_rows):
    raise SystemExit("segments.jsonl contains duplicate IDs")
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
if len(coverage_by_id) != len(coverage_rows):
    raise SystemExit("s2-coverage.csv contains duplicate segment IDs")

source_lines = {}
source_bytes = {}
for key, relative in SOURCE_RELS.items():
    path = ROOT / relative
    source_bytes[key] = path.read_bytes()
    source_lines[key] = path.read_text(encoding="utf-8-sig").splitlines()

segment_texts = {}
for key, segment_id in SEGMENT_IDS.items():
    if key not in EXPECTED_SEGMENTS:
        continue
    meta = segments.get(segment_id)
    if not meta:
        raise SystemExit(f"missing source segment: {segment_id}")
    source_key = "intro" if "_intro:" in segment_id else "body"
    relative = SOURCE_RELS[source_key]
    if meta["source_file"] != relative:
        raise SystemExit(f"unexpected source file for {segment_id}: {meta['source_file']}")
    expected_start, expected_end = EXPECTED_SEGMENTS[key]
    if (int(meta["line_start"]), int(meta["line_end"])) != (expected_start, expected_end):
        raise SystemExit(f"segment bounds changed for {segment_id}; review before migration")
    if hashlib.sha256(source_bytes[source_key]).hexdigest() != meta["asset_sha256"]:
        raise SystemExit(f"source fingerprint changed for {relative}; rebuild segments and review")
    excerpt = "\n".join(source_lines[source_key][expected_start - 1:expected_end])
    if hashlib.sha256(excerpt.encode("utf-8")).hexdigest() != meta["sha256"]:
        raise SystemExit(f"segment text hash changed for {segment_id}; review before migration")
    segment_texts[segment_id] = excerpt

for key in ("intro_header", "intro_title", "intro_notes", "body_header", "body_p203"):
    segment_id = SEGMENT_IDS[key]
    if coverage_by_id.get(segment_id, {}).get("disposition") != "queued":
        raise SystemExit(f"expected queued coverage for {segment_id}; inspect before rerunning")
    if any(row["segment_id"] == segment_id for row in mention_rows):
        raise SystemExit(f"mentions already exist for {segment_id}; inspect before rerunning")
    if any(row["segment_id"] == segment_id for row in statement_rows):
        raise SystemExit(f"statements already exist for {segment_id}; inspect before rerunning")

candidate_ids = {row["candidate_id"] for row in candidate_rows}
existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_statement_ids = {row["statement_id"] for row in statement_rows}
current_max = max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows)
if current_max != EXPECTED_MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: expected {EXPECTED_MAX_CANDIDATE}, found {current_max}")


def candidate(cid, name, typ, detail, segment_key, line):
    segment_id = SEGMENT_IDS[segment_key]
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
        "candidate_source_ref": f"{segment_id}#L{line}",
    }


new_candidates = [
    candidate("cand-7357", "Balbi family in Haskell's Genoa account", "family", "Named among Genoa's mercantile aristocratic families; keep distinct from Paolo Battista Balbi, the individual named later on p.203.", "body_p203", 5),
    candidate("cand-7358", "Brignole family in Haskell's Genoa account", "family", "Named as one of the principal Genoese mercantile families; no individual members are identified here.", "body_p203", 5),
    candidate("cand-7359", "Doria family in Haskell's Genoa account", "family", "Named as one of the principal Genoese mercantile families; no branch or individual member is specified here.", "body_p203", 5),
    candidate("cand-7360", "Durazzo family in Haskell's Genoa account", "family", "Named as one of the principal Genoese mercantile families; no branch or individual member is specified here.", "body_p203", 5),
    candidate("cand-7361", "Imperiali family in Haskell's Genoa account", "family", "The OCR surface is 'Imperial!'; the p.203 scan reads 'Imperiali'. No specific branch is identified.", "body_p203", 5),
    candidate("cand-7362", "Lomellini family in Haskell's Genoa account", "family", "Named as one of the principal Genoese mercantile families; no individual member is identified here.", "body_p203", 6),
    candidate("cand-7363", "Negroni family in Haskell's Genoa account", "family", "Named as one of the principal Genoese mercantile families; do not merge with the separately indexed Cardinal Negroni.", "body_p203", 6),
    candidate("cand-7364", "Pallavicini family in Haskell's Genoa account", "family", "Named as one of the principal Genoese mercantile families; no branch or individual member is specified here.", "body_p203", 6),
    candidate("cand-7365", "Saluzzi family in Haskell's Genoa account", "family", "Named as one of the principal Genoese mercantile families; do not identify a member from the surname alone.", "body_p203", 6),
    candidate("cand-7366", "Sauli family in Haskell's Genoa account", "family", "Named as one of the principal Genoese mercantile families; no individual member is identified here.", "body_p203", 6),
    candidate("cand-7367", "Spinola family in Haskell's Genoa account", "family", "Named as one of the principal Genoese mercantile families; no branch or individual member is specified here.", "body_p203", 6),
    candidate("cand-7368", "Colonna family in Haskell's Naples account", "family", "Named among the Neapolitan feudal landowning families; branch and identity relative to other Colonna candidates remain for S3.", "body_p203", 7),
    candidate("cand-7369", "Maddaloni family in Haskell's Naples account", "family", "Named among the Neapolitan feudal landowning families; no individual member is identified here.", "body_p203", 7),
    candidate("cand-7370", "Monteleone family in Haskell's Naples account", "family", "Named among the Neapolitan feudal landowning families; no individual member is identified here.", "body_p203", 7),
    candidate("cand-7371", "Sonnino family in Haskell's Naples account", "family", "Named among the Neapolitan feudal landowning families; no individual member is identified here.", "body_p203", 7),
    candidate("cand-7372", "Tarsia Spinelli family in Haskell's Naples account", "family", "The OCR splits the pluralized family form across source lines; preserve the source span and defer branch identity.", "body_p203", 7),
    candidate("cand-7373", "Albergati family in Haskell's Bologna account", "family", "Named as one of Bologna's senatorial families; no branch or individual member is specified here.", "body_p203", 8),
    candidate("cand-7374", "Aldrovandi family in Haskell's Bologna account", "family", "Named as one of Bologna's senatorial families; no branch or individual member is specified here.", "body_p203", 8),
    candidate("cand-7375", "Ercolani family in Haskell's Bologna account", "family", "Named as one of Bologna's senatorial families; no branch or individual member is specified here.", "body_p203", 8),
    candidate("cand-7376", "Ghisilieri family in Haskell's Bologna account", "family", "Named as one of Bologna's senatorial families; no branch or individual member is specified here.", "body_p203", 8),
    candidate("cand-7377", "Pepoli family in Haskell's Bologna account", "family", "Named as one of Bologna's senatorial families; no branch or individual member is specified here.", "body_p203", 8),
    candidate("cand-7378", "Sampieri family in Haskell's Bologna account", "family", "Named as one of Bologna's senatorial families; no branch or individual member is specified here.", "body_p203", 8),
    candidate("cand-7379", "Republic of Genoa in Haskell's p.203 account", "institution", "Political entity dominated by Genoa's mercantile aristocracy in the author's account; its formal historical designation is not externally aligned in S2.", "body_p203", 4),
    candidate("cand-7380", "Local painting schools in Italian provincial cities", "term", "Collective category in Haskell's opening comparison; the passage does not enumerate each school or make them one institution.", "body_p203", 4),
    candidate("cand-7381", "Legate and Vicelegate offices in Bologna", "term", "The passage refers to officeholders who were usually Genoese; it does not name the individuals or establish a single officeholder identity.", "body_p203", 6),
    candidate("cand-7382", "Neapolitan school of painting described on p.203", "term", "Local school supported by Neapolitan landowning families and compared by Haskell with Rome; no institutional name or membership is supplied.", "body_p203", 8),
    candidate("cand-7383", "Carracci artists and their followers in Haskell's Bologna account", "term", "Collective artistic influence invoked to characterize Bologna's family collections; do not reduce the reference to Annibale Carracci alone.", "body_p203", 8),
    candidate("cand-7384", "Painting of S. Luigi Gonzaga by Guido Reni mentioned by Malpighi", "work", "Unspecified painting cited in Malpighi's quoted comment; no date, location, or present attribution status is supplied on p.203.", "body_p203", 8),
    candidate("cand-7385", "Marcello Oretti", "person", "Named as the author of the B.109 manuscript title in Haskell's p.203 note 5; biographical identity is not independently aligned here.", "body_p203", 12),
    candidate("cand-7386", "Biblioteca Comunale, Bologna", "institution", "Repository named by Haskell for manuscript B.109; the precise institutional form and current catalogue record are not checked here.", "body_p203", 11),
    candidate("cand-7387", "Marcello Oretti, Descrizione delle Pitture che ornano le Case de’ Cittadini della Città di Bologna (manuscript B.109)", "archive", "Manuscript named as an essential source for Belloni, Bellucci and Bolognese family collections. Title spelling is normalized from the page image; the manuscript was not consulted.", "body_p203", 11),
    candidate("cand-7388", "A. Maresca di Serracapriola, Il museo del duca di Martina (Napoli Nobilissima, 1893)", "archive", "Bibliographic candidate identified from the book's bibliography for the p.203 note 2 citation; cited page and article not independently read, and the bibliography segment remains to be reviewed in S2.", "intro_notes", 8),
    candidate("cand-7389", "A. Maresca di Serracapriola", "person", "Author named in the p.203 note 2 citation; the source provides only the initial and surname form here.", "intro_notes", 8),
    candidate("cand-7390", "Bolognese families whose collections are described in manuscript B.109", "term", "Collective scope of the p.203 note 5 claim; it is not a single family and does not identify every constituent family.", "body_p203", 11),
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


def mention(segment_key, surface, cid, note, occurrence=1):
    mention_specs.append((SEGMENT_IDS[segment_key], surface, cid, note, occurrence))


# Citation mentions in the four chapter-opening footnotes.
mention("intro_notes", "Soprani", "cand-5160", "Citation to Soprani; the general reference does not independently verify a specific p.203 claim.")
mention("intro_notes", "de Dominici", "cand-4835", "Citation to de Dominici; cited pages are not specified in this note.")
mention("intro_notes", "Maresca di Serracapriola", "cand-7389", "Author name in the bibliography citation; the article is separately referenced in the statement citation metadata.")
mention("intro_notes", "Malvasia", "cand-6933", "Citation to Malvasia's Felsina Pittrice; general reference only.")
mention("intro_notes", "Zanotti", "cand-7115", "Citation to Storia dell'Accademia Clementina; general reference only.")
mention("intro_notes", "Ruffo", "cand-7261", "Short citation resolved through the bibliography to Agnelli's Galleria di pitture del Card. Tomm. Ruffo; cited pages are not independently read.")

# Main p.203 text: source forms and candidate mapping are explicit; cross-chapter
# identity questions remain for S3.
mention("body_p203", "Italy", "cand-3461", "Country within which patronage is being discussed.")
mention("body_p203", "Genoa", "cand-1131", "City whose mercantile aristocracy is described.")
mention("body_p203", "Genoese", "cand-1131", "Demonym for the unnamed Bologna officeholders; no individual is inferred.")
for surface, cid, note in [
    ("Balbi", "cand-7357", "Genoese family, distinct from the later individual Paolo Battista Balbi."),
    ("Brignole", "cand-7358", "Genoese family named in the aristocratic group."),
    ("Doria", "cand-7359", "Genoese family named in the aristocratic group."),
    ("Durazzo", "cand-7360", "Genoese family named in the aristocratic group."),
    ("Imperial!", "cand-7361", "Literal OCR surface; the scan reads Imperiali. Source OCR remains unchanged."),
    ("Lomellini", "cand-7362", "Genoese family named in the aristocratic group."),
    ("Negroni", "cand-7363", "Genoese family; do not merge with Cardinal Giovan Francesco Negroni."),
    ("Pallavicini", "cand-7364", "Genoese family named in the aristocratic group."),
    ("Saluzzi", "cand-7365", "Genoese family; no individual member is inferred from the surname."),
    ("Sauli", "cand-7366", "Genoese family named in the aristocratic group."),
    ("Spinola", "cand-7367", "Genoese family named in the aristocratic group."),
]:
    mention("body_p203", surface, cid, note)
mention("body_p203", "Bologna", "cand-0381", "City from which an occasional contemporary picture was brought to Genoa.", 1)
mention("body_p203", "Legate", "cand-7381", "Office title in the Bologna political context; no officeholder is named.")
mention("body_p203", "Vicelcgate", "cand-7381", "Literal OCR surface for the second Bologna office title; no scan correction is asserted here.")
mention("body_p203", "Naples", "cand-1722", "City in the account of local landowning patrons.")
mention("body_p203", "South", "cand-5563", "The source's regional wording for the feudal landowners; mapped to Southern Italy as a place candidate.")
for surface, cid in [
    ("Colonnas", "cand-7368"), ("Maddalonis", "cand-7369"),
    ("Monteleones", "cand-7370"), ("Sonninos", "cand-7371"),
]:
    mention("body_p203", surface, cid, "Family named among the Neapolitan feudal landowners; branch identity remains unresolved.")
mention("body_p203", "Tarsia\nSpinellis", "cand-7372", "Family name split across S0 source lines; preserve its pluralized OCR span.")
mention("body_p203", "Spanish", "cand-4591", "Polity's rule is invoked as the political setting; this does not resolve the candidate's cross-chapter identity.")
mention("body_p203", "school of art", "cand-7382", "The specific Neapolitan school described in the sentence.")
mention("body_p203", "Rome", "cand-4490", "City used as the comparison point for the Neapolitan school.", 1)
mention("body_p203", "papal states", "cand-1831", "Political territory in which Bologna is situated in Haskell's account.")
mention("body_p203", "Bologna", "cand-0382", "Index subentry for Bologna as a second capital ruled by senatorial families.", 2)
mention("body_p203", "senatorial families", "cand-0382", "Bologna index subentry; the named families remain separate candidates.")
for surface, cid in [
    ("Albergati", "cand-7373"), ("Aldrovandi", "cand-7374"),
    ("Ercolani", "cand-7375"), ("Ghisilieri", "cand-7376"),
    ("Pepoli", "cand-7377"), ("Sampieri", "cand-7378"),
]:
    mention("body_p203", surface, cid, "Family named among Bologna's senatorial families; no individual member is inferred.")
mention("body_p203", "Carracci and their followers", "cand-7383", "Collective artistic influence in Haskell's description; do not assign the phrase to one Carracci or infer its full membership.")
mention("body_p203", "Florence", "cand-3397", "City in Haskell's comparison of provincial centres.")
mention("body_p203", "Venice", "cand-3401", "City in Haskell's comparison of provincial centres.")
mention("body_p203", "professional classes", "cand-2065", "Index candidate for patronage by professional classes in Italian provinces.")
mention("body_p203", "Bologna", "cand-0381", "City in the account of doctors as picture owners.", 3)
mention("body_p203", "Paolo Battista Balbi", "cand-0164", "Individual picture owner; not the Genoese Balbi family candidate.")
mention("body_p203", "Beccari", "cand-0264", "Index candidate is only identified as 'Dr'; personal identity remains unresolved.")
mention("body_p203", "Marcello Malpighi", "cand-1500", "Physician and picture owner named by Haskell.")
mention("body_p203", "S. Luigi Gonzaga", "cand-5453", "Saint represented in the Reni painting; the work is separately represented as a candidate.")
mention("body_p203", "Guido Reni", "cand-2132", "Artist identified by the index subentry for S. Luigi Gonzaga on p.203.")
mention("body_p203", "Guercino", "cand-1258", "Artist named as Malpighi's friend.")
mention("body_p203", "Cignani", "cand-0748", "Artist named as Malpighi's friend.")
mention("body_p203", "merchants", "cand-2065", "Professional-class patron group discussed in the continuation of the passage.")
mention("body_p203", "Giovanni Antonio Belloni", "cand-0271", "Merchant and picture owner named in the p.203 account.")
mention("body_p203", "James III", "cand-1318", "Source's exiled royal title; identity and regnal convention are deferred to S3.")
mention("body_p203", "Giovan Gioseffo dal Sole", "cand-2480", "Artist named in Belloni's collection account.")
mention("body_p203", "Felice Torelli", "cand-2645", "Artist named in Belloni's collection account.")
mention("body_p203", "Crespi", "cand-0871", "Index candidate covers p.203; first occurrence refers to Belloni's collection.", 1)
mention("body_p203", "Gambarini", "cand-1113", "Artist referred to as 'the last artist' in the next clause.")
mention("body_p203", "Rome", "cand-4490", "Destination of Gambarini's reported journey.", 2)
mention("body_p203", "Giovanni Battista Bellucci", "cand-0285", "Second merchant named as a picture owner.")
mention("body_p203", "Crespi", "cand-0871", "Second occurrence refers to Bellucci's collection.", 2)
mention("body_p203", "dal Sole", "cand-2480", "Later short form for Giovan Gioseffo dal Sole; the earlier full name is already recorded.", 2)

# Substantive manuscript note on p.203.
mention("body_p203", "Zanotti", "cand-7115", "Citation to volume I, p.389; the cited page is not independently read.")
mention("body_p203", "Belloni", "cand-0271", "The manuscript is described as a source for Belloni's collection.", 2)
mention("body_p203", "Bellucci", "cand-0285", "The manuscript is described as a source for Bellucci's collection.", 2)
mention("body_p203", "all the\nBolognese families", "cand-7390", "Collective scope claimed by the note; preserve the source line break and do not infer a full membership list.")
mention("body_p203", "B.109", "cand-7387", "Manuscript shelfmark stated in the note.")
mention("body_p203", "Biblioteca Comunale", "cand-7386", "Repository named for B.109; exact institutional identity awaits S3/verification.")
mention("body_p203", "Bologna", "cand-0381", "City in the repository locator.", 4)
body_segment_text = segment_texts[SEGMENT_IDS["body_p203"]]
title_start = body_segment_text.find("Descrizione delle")
title_end = body_segment_text.find(".", title_start)
if title_start < 0 or title_end < 0:
    raise SystemExit("could not locate the manuscript title span in the S0 segment")
title_surface = body_segment_text[title_start:title_end]
mention("body_p203", title_surface, "cand-7387", "Full source title span; OCR reads 'eke' and 'Cittd', corrected only in the candidate's normalized title from the page image.")
mention("body_p203", "Marcello Oretti", "cand-7385", "Author named in the manuscript title; the work and its author remain separate candidates.")
mention("body_p203", "Bologna", "cand-0381", "City in the manuscript title; nested within the title span.", 5)


new_mentions = []
for segment_id, surface, cid, note, occurrence in mention_specs:
    if cid not in candidate_ids | new_candidate_ids:
        raise SystemExit(f"mention references missing candidate: {cid}")
    text = segment_texts[segment_id]
    starts = []
    cursor = 0
    while True:
        found = text.find(surface, cursor)
        if found < 0:
            break
        starts.append(found)
        cursor = found + 1
    if occurrence > len(starts):
        raise SystemExit(f"surface occurrence {occurrence} not found for {surface!r} in {segment_id}; found {len(starts)}")
    start = starts[occurrence - 1]
    end = start + len(surface)
    if text[start:end] != surface:
        raise SystemExit(f"mention offset mismatch: {surface!r}")
    new_mentions.append({
        "mention_id": f"m-chp8-p203-{len(new_mentions)+1:03d}",
        "segment_id": segment_id,
        "candidate_id": cid,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    })

new_mentions.sort(key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"])))
for i, first in enumerate(new_mentions):
    if first["mention_id"] in existing_mention_ids:
        raise SystemExit(f"mention ID collision: {first['mention_id']}")
    for second in new_mentions[i + 1:]:
        if second["segment_id"] != first["segment_id"]:
            continue
        a, b = int(first["start_char"]), int(first["end_char"])
        c, d = int(second["start_char"]), int(second["end_char"])
        if a < d and c < b:
            nested = (a < c and d < b) or (c < a and b < d)
            if not nested:
                raise SystemExit(f"overlapping non-nested mentions: {first!r} / {second!r}")


def source_excerpt(segment_id, start_line, end_line):
    meta = segments[segment_id]
    source_key = "intro" if "_intro:" in segment_id else "body"
    return "\n".join(source_lines[source_key][start_line - 1:end_line])


def quote_between(segment_id, start_line, end_line, start_token, end_token):
    text = source_excerpt(segment_id, start_line, end_line)
    start = text.find(start_token)
    if start < 0:
        raise SystemExit(f"quote start token missing: {start_token!r}")
    stop = text.find(end_token, start + len(start_token))
    if stop < 0:
        raise SystemExit(f"quote end token missing: {end_token!r}")
    return text[start:stop + len(end_token)]


def statement(sid, segment_key, start, end, predicate, claim, qualification,
              *, subject=None, obj=None, mentioned=(), quote=None, speaker="Haskell",
              text_layer="body", extra=None):
    segment_id = SEGMENT_IDS[segment_key]
    qualifiers = {
        "source_line_start": start,
        "source_line_end": end,
        "printed_page": 203,
        "pdf_physical_page": 1,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    if extra:
        qualifiers.update(extra)
    return {
        "statement_id": sid,
        "segment_id": segment_id,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote or source_excerpt(segment_id, start, end),
        "origin": "book",
        "source_file": segments[segment_id]["source_file"],
    }


family_ids = [f"cand-{n}" for n in range(7357, 7368)]
naples_family_ids = [f"cand-{n}" for n in range(7368, 7373)]
bologna_family_ids = [f"cand-{n}" for n in range(7373, 7379)]
body_statements = [
    statement("st-chp8-p203-local-schools-support", "body_p203", 3, 4,
              "local_painting_schools_supported_by_families_and_orders",
              "Haskell contrasts the New World with Italy and says patronage remained extensive there; local painting schools flourished with support from noble families and religious orders.",
              "This is Haskell's broad account of local artistic conditions, not a claim that the named cities shared one school or one patronage institution.",
              subject="cand-2066", obj="cand-7380", mentioned=["cand-3461", "cand-2066", "cand-7380"],
              quote=quote_between(SEGMENT_IDS["body_p203"], 3, 4, "HE new world", "religious orders."),
              extra={"ocr_corrections": [{"source_line": 3, "ocr": "HE", "print": "THE", "basis": "CHP-8.pdf physical page 1; drop-cap T is omitted from OCR."}, {"source_line": 4, "ocr": "Titself", "print": "itself", "basis": "CHP-8.pdf physical page 1."}]}),
    statement("st-chp8-p203-genoa-republic", "body_p203", 4, 4,
              "mercantile_aristocracy_dominated_polity",
              "Haskell says a rich mercantile aristocracy in Genoa dominated the Republic.",
              "The source names no particular officeholders or political mechanism.", subject="cand-1132", obj="cand-7379",
              mentioned=["cand-1131", "cand-1132", "cand-7379"],
              quote=quote_between(SEGMENT_IDS["body_p203"], 4, 4, "In Genoa", "dominated the Republic.")),
    statement("st-chp8-p203-genoese-family-collections", "body_p203", 5, 6,
              "families_collected_local_contemporary_and_old_master_pictures",
              "Haskell says principal Genoese mercantile families filled their palaces with works by native painters, occasional contemporary pictures brought from Bologna, and selected old masters.",
              "The sentence describes the group collectively. It does not assign specific works, palaces, or acquisition acts to individual families.",
              subject="cand-1132", mentioned=["cand-1131", "cand-1132", *family_ids, "cand-0381", "cand-7381"],
              quote=quote_between(SEGMENT_IDS["body_p203"], 5, 6, "Its principal members", "and a selection of old masters."),
              extra={"ocr_corrections": [{"source_line": 5, "ocr": "Imperial!", "print": "Imperiali", "basis": "CHP-8.pdf physical page 1."}]}),
    statement("st-chp8-p203-naples-families-and-school", "body_p203", 6, 8,
              "neapolitan_landowners_supported_local_school_under_spanish_rule",
              "Haskell says Neapolitan feudal landowners prospered under Spanish rule and lavishly supported a local school of art.",
              "The named families are a collective list; the school is not identified as a formal institution.",
              obj="cand-7382", mentioned=["cand-1722", "cand-1723", *naples_family_ids, "cand-5563", "cand-4591", "cand-7382"],
              quote=quote_between(SEGMENT_IDS["body_p203"], 6, 8, "It was the same in Naples", "second only to that of Rome in brilliance and diversity.")),
    statement("st-chp8-p203-bologna-senatorial-collections", "body_p203", 8, 8,
              "senatorial_families_preserved_autonomy_and_collected_carracci_influenced_works",
              "Haskell describes Bologna as the second capital of the Papal States, with senatorial families retaining some autonomy and building large collections of works by artists living in the reflected glory of the Carracci and their followers.",
              "The autonomy is qualified as a semblance; the collection and artistic influence are described collectively, without naming individual works or assigning them to each family.",
              subject="cand-0382", obj="cand-7383", mentioned=["cand-1831", "cand-0382", *bologna_family_ids, "cand-7383"],
              quote=quote_between(SEGMENT_IDS["body_p203"], 8, 8, "And within the papal states themselves", "the Carracci and their followers."),
              extra={"ocr_corrections": [{"source_line": 8, "ocr": "second.capital", "print": "second capital", "basis": "CHP-8.pdf physical page 1."}]}),
    statement("st-chp8-p203-professional-class-patrons", "body_p203", 8, 8,
              "professional_classes_important_as_patrons_in_cities",
              "Haskell says patrons from professional classes were important in Bologna, Florence, Venice, and other towns.",
              "The claim is a generalization about patronage; it does not identify all patrons or imply equal importance in each city.",
              subject="cand-2065", mentioned=["cand-2065", "cand-3397", "cand-3401", "cand-0381"],
              quote=quote_between(SEGMENT_IDS["body_p203"], 8, 8, "And similarly in Florence", "of importance.")),
    statement("st-chp8-p203-bolognese-doctors-picture-owners", "body_p203", 8, 8,
              "doctors_owned_pictures",
              "Haskell says Paolo Battista Balbi, Beccari, and Marcello Malpighi all owned pictures.",
              "Beccari is identified only as 'Dr'; the passage does not identify the pictures or equate the personal Balbi with the Genoese Balbi family.",
              subject="cand-0381", mentioned=["cand-0381", "cand-0164", "cand-0264", "cand-1500"],
              quote=quote_between(SEGMENT_IDS["body_p203"], 8, 8, "In Bologna there were the doctors:", "all owned pictures."),
              extra={"ocr_corrections": [{"source_line": 8, "ocr": "great - Marcello", "print": "great Marcello", "basis": "CHP-8.pdf physical page 1; stray OCR punctuation removed."}]}),
    statement("st-chp8-p203-malpighi-reni-painting-and-taste", "body_p203", 8, 8,
              "malpighi_comment_on_reni_painting_as_evidence_of_taste",
              "Haskell characterizes Malpighi as a connoisseur with fine and decided tastes and quotes his comment about a painting of S. Luigi Gonzaga by Guido Reni.",
              "The quoted Italian phrase is Malpighi's reported writing; the painting's identity, location, and quotation context are not independently verified here.",
              subject="cand-1500", obj="cand-7384", mentioned=["cand-1500", "cand-7384", "cand-5453", "cand-2132"],
              quote=quote_between(SEGMENT_IDS["body_p203"], 8, 8, "Indeed the latter", "by Guido Reni),")),
    statement("st-chp8-p203-malpighi-friends-and-collector", "body_p203", 8, 8,
              "malpighi_friends_with_artists_and_collected_pictures",
              "Haskell says Malpighi was a friend of artists such as Guercino and Cignani and was a keen collector.",
              "The wording 'such as' gives examples, not a complete list of Malpighi's artistic friendships.",
              subject="cand-1500", mentioned=["cand-1500", "cand-1258", "cand-0748"],
              quote=quote_between(SEGMENT_IDS["body_p203"], 8, 8, "the friend of artists such as", "and a keen collector.")),
    statement("st-chp8-p203-merchants-role", "body_p203", 8, 8,
              "merchants_influential_in_bologna_artistic_life",
              "Haskell says merchants, especially at the end of the century, played a very influential role in Bologna's artistic life.",
              "This is an authorial summary; the passage gives Belloni and Bellucci as examples rather than a complete merchant group.",
              subject="cand-2065", mentioned=["cand-2065", "cand-0271", "cand-0285"],
              quote=quote_between(SEGMENT_IDS["body_p203"], 8, 8, "And above all there were the merchants", "artistic life of the city.")),
    statement("st-chp8-p203-belloni-hospitality-james-iii", "body_p203", 8, 8,
              "belloni_hosted_exiled_james_iii",
              "Haskell says Giovanni Antonio Belloni gave splendid hospitality to the exiled James III.",
              "The title is retained as the source gives it; the identity and regnal convention await global alignment.",
              subject="cand-0271", obj="cand-1318", mentioned=["cand-0271", "cand-1318"],
              quote=quote_between(SEGMENT_IDS["body_p203"], 8, 8, "Giovanni Antonio Belloni, for instance", "owned large numbers of pictures by")),
    statement("st-chp8-p203-belloni-collection", "body_p203", 8, 8,
              "belloni_owned_pictures_by_named_artists",
              "Haskell says Belloni owned large numbers of pictures by Giovan Gioseffo dal Sole, Felice Torelli, Crespi, and Gambarini.",
              "No individual painting, date, or current location is specified.",
              subject="cand-0271", mentioned=["cand-0271", "cand-2480", "cand-2645", "cand-0871", "cand-1113"],
              quote=quote_between(SEGMENT_IDS["body_p203"], 8, 8, "owned large numbers of pictures by", "Gambarini,")),
    statement("st-chp8-p203-belloni-sent-gambarini-to-rome", "body_p203", 8, 8,
              "merchant_sent_artist_on_journey_to_city",
              "Haskell says Belloni sent Gambarini on a journey to Rome.",
              "The source gives no date, purpose, or evidence that Belloni financed the journey.",
              subject="cand-0271", obj="cand-1113", mentioned=["cand-0271", "cand-1113", "cand-4490"],
              quote=quote_between(SEGMENT_IDS["body_p203"], 8, 8, "and he sent the last artist", "on a journey to Rome"),
              extra={"destination_candidate_id": "cand-4490"}),
    statement("st-chp8-p203-bellucci-crespi-pictures", "body_p203", 8, 9,
              "merchant_owned_pictures_by_artist",
              "Haskell says Giovanni Battista Bellucci owned works by Crespi.",
              "The work or works are not individually identified.", subject="cand-0285", obj="cand-0871",
              mentioned=["cand-0285", "cand-0871"],
              quote=quote_between(SEGMENT_IDS["body_p203"], 8, 9, "Giovanni Battista Bellucci", "Crespi and many more by dal Sole.")),
    statement("st-chp8-p203-bellucci-dal-sole-pictures", "body_p203", 8, 9,
              "merchant_owned_pictures_by_artist",
              "Haskell says Bellucci owned many works by dal Sole.",
              "The comparative wording 'many more' is retained; no individual work is named.", subject="cand-0285", obj="cand-2480",
              mentioned=["cand-0285", "cand-2480"],
              quote=quote_between(SEGMENT_IDS["body_p203"], 8, 9, "Giovanni Battista Bellucci", "Crespi and many more by dal Sole.")),
    statement("st-chp8-p203-merchant-group-open-continuation", "body_p203", 9, 9,
              "descriptive_sentence_open_continuation",
              "Haskell begins to identify the most cultivated and interesting member of the small group of enlightened merchants, but the sentence continues on p.204.",
              "No person is named within this segment; the clause must be completed from p.204 before semantic closure.",
              mentioned=[], quote=source_excerpt(SEGMENT_IDS["body_p203"], 9, 9),
              extra={"continuation_status": "open", "continuation_expected_segment_id": SEGMENT_IDS["body_p204"]}),
]


def note_statement(sid, segment_key, line_start, line_end, predicate, claim, qualification,
                   *, obj=None, mentioned=(), quote=None, marker=None, linked=(), citations=None,
                   text_layer="bibliographic citation", extra=None):
    qextra = {
        "footnote_marker": marker,
        "linked_body_statement_ids": list(linked),
        "citations": citations or [],
    }
    if extra:
        qextra.update(extra)
    return statement(sid, segment_key, line_start, line_end, predicate, claim, qualification,
                     obj=obj, mentioned=mentioned, quote=quote, speaker="Haskell footnote",
                     text_layer=text_layer, extra=qextra)


footnote_statements = [
    note_statement("st-chp8-p203-n1-soprani", "intro_notes", 8, 8, "footnote_citation",
                   "P.203 note 1 cites Soprani as a general reference for the Genoa account.",
                   "The note gives no specific page; the cited work's pages are not independently consulted.",
                   obj="cand-5160", mentioned=["cand-5160"], quote="Soprani, passim.", marker=1,
                   linked=["st-chp8-p203-genoese-family-collections"],
                   citations=[{"source_candidate_id": "cand-5160", "locator": "passim"}]),
    note_statement("st-chp8-p203-n2-naples-citations", "intro_notes", 8, 8, "footnote_citation",
                   "P.203 note 2 cites de Dominici and Maresca di Serracapriola in connection with the Naples account.",
                   "The citation to de Dominici is general; Maresca is cited at p.49. Neither cited passage is independently read. The Maresca publication identification comes from the bibliography, whose segment remains to be reviewed in S2.",
                   obj="cand-4835", mentioned=["cand-4835", "cand-7389"],
                   quote="de Dominici, passim, and Maresca di Serracapriola, p. 49.", marker=2,
                   linked=["st-chp8-p203-naples-families-and-school"],
                   citations=[{"source_candidate_id": "cand-4835", "locator": "passim"}, {"source_candidate_id": "cand-7388", "page": "49"}]),
    note_statement("st-chp8-p203-n3-bologna-citations", "intro_notes", 9, 9, "footnote_citation",
                   "P.203 note 3 cites Malvasia and Zanotti as general references for the Bologna family collections.",
                   "The note specifies no page; the cited passages are not independently read.",
                   obj="cand-6933", mentioned=["cand-6933", "cand-7115"], quote="Malvasia and Zanotti, passim.", marker=3,
                   linked=["st-chp8-p203-bologna-senatorial-collections"],
                   citations=[{"source_candidate_id": "cand-6933", "locator": "passim"}, {"source_candidate_id": "cand-7115", "locator": "passim"}]),
    note_statement("st-chp8-p203-n4-ruffo-citation", "intro_notes", 10, 10, "footnote_citation",
                   "P.203 note 4 cites Ruffo at pp.122–123 for the Malpighi/Reni passage.",
                   "The short citation is resolved through the book bibliography to Agnelli's Galleria di pitture del Card. Tomm. Ruffo; the cited pages are not independently read.",
                   obj="cand-7261", mentioned=["cand-7261"], quote="Ruffo, pp. 122-3.", marker=4,
                   linked=["st-chp8-p203-malpighi-reni-painting-and-taste"],
                   citations=[{"source_candidate_id": "cand-7261", "pages": ["122", "123"]}]),
    note_statement("st-chp8-p203-n5-zanotti-and-b109", "body_p203", 10, 12, "identifies_manuscript_as_essential_source",
                   "Haskell cites Zanotti I, p.389, then identifies manuscript B.109 in the Biblioteca Comunale, Bologna, by Marcello Oretti as an essential source for Belloni's, Bellucci's, and Bolognese family collections.",
                   "This records Haskell's description of the manuscript, not independent consultation of B.109. The manuscript title is OCR-transcribed in S0; the p.203 scan confirms 'che' for OCR 'eke' and 'Città' for OCR 'Cittd'. The cited Zanotti page is not independently read.",
                   obj="cand-7387", mentioned=["cand-7115", "cand-7385", "cand-7386", "cand-7387", "cand-0271", "cand-0285", "cand-7390", "cand-0381"],
                   quote=source_excerpt(SEGMENT_IDS["body_p203"], 10, 12), marker=5,
                   linked=["st-chp8-p203-bologna-senatorial-collections", "st-chp8-p203-belloni-collection", "st-chp8-p203-bellucci-crespi-pictures", "st-chp8-p203-bellucci-dal-sole-pictures"],
                   citations=[{"source_candidate_id": "cand-7115", "volume": "I", "page": "389"}, {"source_candidate_id": "cand-7387", "shelfmark": "B.109"}],
                   text_layer="authorial footnote and manuscript identification",
                   extra={"ocr_corrections": [{"source_line": 12, "ocr": "eke", "print": "che", "basis": "CHP-8.pdf physical page 1."}, {"source_line": 12, "ocr": "Cittd", "print": "Città", "basis": "CHP-8.pdf physical page 1."}]}),
]

new_statements = body_statements + footnote_statements
if len({row["statement_id"] for row in new_statements}) != len(new_statements):
    raise SystemExit("duplicate planned statement IDs")
for row in new_statements:
    sid = row["statement_id"]
    if sid in existing_statement_ids:
        raise SystemExit(f"statement ID collision: {sid}")
    q = row["qualifiers"]
    segment_id = row["segment_id"]
    excerpt = source_excerpt(segment_id, q["source_line_start"], q["source_line_end"])
    if row["original_quote"] not in excerpt:
        raise SystemExit(f"quote is not reproducible in source: {sid}")
    meta = segments[segment_id]
    if not (int(meta["line_start"]) <= q["source_line_start"] <= q["source_line_end"] <= int(meta["line_end"])):
        raise SystemExit(f"statement line range outside segment: {sid}")
    mentioned_ids = set(q.get("mentioned_candidate_ids", []))
    if row.get("subject_candidate_id"):
        mentioned_ids.add(row["subject_candidate_id"])
    if row.get("object_candidate_id"):
        mentioned_ids.add(row["object_candidate_id"])
    if not mentioned_ids <= candidate_ids | new_candidate_ids:
        raise SystemExit(f"statement references missing candidate: {sid}")
    linked = q.get("linked_body_statement_ids", [])
    if any(linked_id not in {item["statement_id"] for item in body_statements} for linked_id in linked):
        raise SystemExit(f"footnote statement has invalid body link: {sid}")


updated_coverage = []
for row in coverage_rows:
    row = dict(row)
    segment_id = row["segment_id"]
    if segment_id == SEGMENT_IDS["intro_header"]:
        row.update({"disposition": "excluded", "migration_status": "complete", "source_line_ranges": "", "note": "Generated Markdown filename heading; not original book content."})
    elif segment_id == SEGMENT_IDS["intro_title"]:
        row.update({"disposition": "excluded", "migration_status": "complete", "source_line_ranges": "", "note": "Printed page marker and chapter title/navigation only; retained as source structure, not an entity or factual passage."})
    elif segment_id == SEGMENT_IDS["intro_notes"]:
        row.update({"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L8-10", "note": "P.203 notes 1-4 migrated as bibliographic pointers and linked to the corresponding Genoa, Naples, Bologna, and Malpighi/Reni statements. Cited pages are not treated as independently verified; Maresca publication identified from the bibliography but that bibliography segment remains pending S2 review."})
    elif segment_id == SEGMENT_IDS["body_header"]:
        row.update({"disposition": "excluded", "migration_status": "complete", "source_line_ranges": "", "note": "Generated Markdown filename heading; not original book content."})
    elif segment_id == SEGMENT_IDS["body_p203"]:
        row.update({"disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L3-12", "note": "P.203 body and note 5 semantically read against CHP-8.pdf physical p.1 and migrated. The last body sentence ends 'this little' and remains open for p.204 L14-21; the statement is linked forward. OCR corrections are recorded in S2 qualifiers; S0 text is unchanged."})
    updated_coverage.append(row)

preview = {
    "mode": "dry-run",
    "segments": [SEGMENT_IDS[key] for key in ("intro_header", "intro_title", "intro_notes", "body_header", "body_p203")],
    "new_candidates": len(new_candidates),
    "candidate_ids": [row["candidate_id"] for row in new_candidates],
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "coverage": {row["segment_id"]: f"{row['disposition']}/{row['migration_status']}" for row in updated_coverage if row["segment_id"] in SEGMENT_IDS.values()},
    "open_continuation": {"statement_id": "st-chp8-p203-merchant-group-open-continuation", "expected_segment_id": SEGMENT_IDS["body_p204"]},
    "ocr_corrections": ["HE -> THE", "Titself -> itself", "Imperial! -> Imperiali", "second.capital -> second capital", "great - Marcello -> great Marcello", "eke -> che", "Cittd -> Città"],
    "mention_preview": [{"segment_id": row["segment_id"], "candidate_id": row["candidate_id"], "surface": row["surface_form"], "start": int(row["start_char"]), "end": int(row["end_char"])} for row in new_mentions],
    "statement_ids": [row["statement_id"] for row in new_statements],
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the validated migration and create recovery backups")
if not parser.parse_args().apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)

for path in (candidate_path, mention_path, statement_path, coverage_path):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing to overwrite: {backup}")
    shutil.copy2(path, backup)

candidate_rows.extend(new_candidates)
mention_rows.extend(new_mentions)
statement_rows.extend(new_statements)
write_csv_atomic(candidate_path, candidate_fields, candidate_rows)
write_csv_atomic(mention_path, mention_fields, mention_rows)
write_jsonl_atomic(statement_path, statement_rows)
write_csv_atomic(coverage_path, coverage_fields, updated_coverage)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
