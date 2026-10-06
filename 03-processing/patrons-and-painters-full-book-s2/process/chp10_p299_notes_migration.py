"""Controlled migration of p.299 notes 1-4 and note 4's OCR continuation; dry-run unless --apply."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
BIB = ROOT / "02-sources" / "02-Markdown" / "21_CHP-21Bibliography.md"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
BODY_SEG = "chp-10:10_CHP-10_intro:l354-366"
NOTES_SEG = "chp-10:10_CHP-10_intro:l491-634"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
BODY_SHA = "052f44412749144ce984c01086091fe86db19f44be97dda9455894ac4620406b"
NOTES_SHA = "9651951dcf1392baf67d24469fba60cd9bf736dd13314c97d335195e1b2e00b5"
BACKUP_SUFFIX = ".bak-s2-chp10-p299-notes-20261002"
EXPECTED_MAX_CANDIDATE = 9483


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


parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the validated migration")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != ASSET_SHA:
    raise SystemExit("canonical source asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
body_text = "\n".join(source_lines[353:366])
notes_text = "\n".join(source_lines[577:581])
if hashlib.sha256(body_text.encode("utf-8")).hexdigest() != BODY_SHA:
    raise SystemExit("p.299 body segment L354-L366 changed")
if hashlib.sha256(notes_text.encode("utf-8")).hexdigest() != NOTES_SHA:
    raise SystemExit("p.299 consolidated notes L578-L581 changed")
for line_no, prefix in {
    578: "1 For the fullest account of his career see Parker, 1948,",
    579: "2 We can get some impression of Smith",
    580: "3 Public Record Office",
    581: "4 See letters from Joseph Smith to A. F. Gori",
}.items():
    if not source_lines[line_no - 1].startswith(prefix):
        raise SystemExit(f"p.299 note {line_no - 577} changed")
if "These extend from 1727 to 1744" not in source_lines[365]:
    raise SystemExit("L366 no longer contains the p.299 note 4 continuation")

bib_text = BIB.read_text(encoding="utf-8-sig")
for fragment in ("Parker, K. T.: Canaletto drawings", "London 1948"):
    if fragment not in bib_text:
        raise SystemExit(f"local Parker bibliography match changed: {fragment}")

cp, mp, sp, vp = [TABLES / name for name in (
    "entity-candidates.csv", "mentions.csv", "book-statements.jsonl", "s2-coverage.csv"
)]
cf, candidates = read_csv(cp)
mf, mentions = read_csv(mp)
vf, coverage = read_csv(vp)
statements = read_jsonl(sp)
cids = {row["candidate_id"] for row in candidates}
mids = {row["mention_id"] for row in mentions}
sids = {row["statement_id"] for row in statements}
cov = {row["segment_id"]: row for row in coverage}
by_cid = {row["candidate_id"]: row for row in candidates}
by_mid = {row["mention_id"]: row for row in mentions}
by_sid = {row["statement_id"]: row for row in statements}

maximum = max(int(row["candidate_id"].split("-")[-1]) for row in candidates if row["candidate_id"].startswith("cand-"))
if maximum != EXPECTED_MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: {maximum}")
expected_coverage = {
    BODY_SEG: ("reviewed", "partial", "L354-365"),
    NOTES_SEG: ("reviewed", "partial", "L492-577"),
}
for segment_id, expected in expected_coverage.items():
    row = cov.get(segment_id)
    actual = (row["disposition"], row["migration_status"], row["source_line_ranges"]) if row else None
    if actual != expected:
        raise SystemExit(f"coverage changed: {segment_id}: {actual}")

REUSED = {
    "smith": "cand-2440", "parker_person": "cand-8660", "smith_will": "cand-8651",
    "public_record_office": "cand-8289", "archivio_venezia": "cand-8592",
    "gabrieli": "cand-1096", "gori": "cand-1214", "salumieri": "cand-9167",
    "london": "cand-1422", "pasquali_person": "cand-1844", "pasquali_firm": "cand-9172",
    "guicciardini_person": "cand-1276", "gori_subentry": "cand-1215",
    "gori_letters": "cand-9229", "florence": "cand-3397",
}
if any(cid not in cids for cid in REUSED.values()):
    raise SystemExit("a required existing candidate is missing")
if by_cid[REUSED["archivio_venezia"]]["canonical_name"] != "Archivio di Stato di Venezia (repository named in pp.263 notes)":
    raise SystemExit("existing Archivio di Stato di Venezia candidate changed")
if not by_cid[REUSED["gori_letters"]]["canonical_name"].startswith("Joseph Smith’s 1737–1738 correspondence with A. F. Gori"):
    raise SystemExit("existing Smith-Gori correspondence candidate changed")

NEW_SPECS = [
    ("parker_book", "K. T. Parker, Canaletto drawings in the Royal Library at Windsor Castle (London, 1948; citation locator)", "archive",
     "Matched by author, title and year to the local bibliography. P.299 note 1 cites pp.10 ff. and says the publication also prints Smith’s will and other documents; neither publication nor cited pages were consulted.", f"{NOTES_SEG}#L578"),
    ("gabrieli_registers", "Atti del Notaio Lodovico Gabrieli, Sezione Notarile, Buste 7559–7570 (1740–1770; citation locator)", "archive",
     "Archival series and shelfmark cited by Haskell for frequent references to Smith after about 1740. The registers were not consulted; Haskell says he could not trace Smith’s notary before that date.", f"{NOTES_SEG}#L579"),
    ("avogaria", "Avogaria di Comun (record-producing office named in p.299 note 2)", "institution",
     "Historical office named as the source context for Civil 263/16. Formal institutional identity and scope remain for S3; the record was not consulted.", f"{NOTES_SEG}#L579"),
    ("civil_record", "Avogaria di Comun, Civil 263/16 (account of a dispute between Smith and Arte de’ Salumieri; citation locator)", "archive",
     "Specific archival file cited by Haskell as containing an account of a dispute. The file and its contents were not consulted.", f"{NOTES_SEG}#L579"),
    ("tron_letter", "Public Record Office, State Papers 99/60: letter from an unnamed British Resident, 18 May 1714 (citation locator)", "archive",
     "Haskell quotes part of this letter in p.299 note 3. It is known here through that quotation only; the archival item was not consulted.", f"{NOTES_SEG}#L580"),
    ("resident_1714", "Unidentified British Resident who authored the 18 May 1714 State Papers 99/60 letter", "person",
     "The letter's author is identified only by office. Keep distinct from other unidentified British Residents until identity evidence is available.", f"{NOTES_SEG}#L580"),
    ("tron_1714", "Signor Tron, described as going as Ambassador to London in a 1714 letter (identity unresolved)", "person",
     "The quoted letter gives only the surname/title and intended diplomatic destination; do not merge with other Tron candidates without identity evidence.", f"{NOTES_SEG}#L580"),
    ("williams_smith_merchants", "Messrs. Williams and Smith, British merchants named in a 1714 letter (entity boundary unresolved)", "",
     "The wording may denote a merchant house or two individuals. No given names are supplied; do not equate the reference with Joseph Smith’s p.299 residence.", f"{NOTES_SEG}#L580"),
    ("guicciardini_histories", "Guicciardini’s Histories (reprint discussed by Smith and Gori; exact title and edition unspecified)", "archive",
     "Haskell refers to this work in the p.299 account and says it was eventually published by Pasquali in 1738. Exact title, edition and the publication itself were not independently verified.", f"{BODY_SEG}#L364"),
    ("marucelliana", "Biblioteca Marucelliana, Florence (repository named for Joseph Smith–A. F. Gori letters)", "institution",
     "Repository named in p.299 note 4. The cited letters and shelfmark were not independently consulted.", f"{NOTES_SEG}#L581"),
    ("museum_etruscum", "Museum Etruscum (Gori publication promised English subscribers by Smith; edition unspecified)", "archive",
     "Work title named in Haskell’s p.299 account of the proposed publishing project. Exact edition and publication details are not supplied here.", f"{BODY_SEG}#L364"),
]
new_candidates = []
C = {}
for offset, (key, name, kind, detail, source_ref) in enumerate(NEW_SPECS, maximum + 1):
    cid = f"cand-{offset:04d}"
    if cid in cids:
        raise SystemExit(f"candidate id already exists: {cid}")
    C[key] = cid
    new_candidates.append({
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name, "index_page_range": "",
        "suggested_type": kind, "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": source_ref,
    })

GUICCIARDINI_MENTION_ID = "m-chp10-p299-guicciardini"
MUSEUM_MENTION_ID = "m-chp10-p299-museum-etruscum"
old_guicciardini = by_mid.get(GUICCIARDINI_MENTION_ID)
old_museum = by_mid.get(MUSEUM_MENTION_ID)
if not old_guicciardini or old_guicciardini["candidate_id"] != REUSED["guicciardini_person"] or not old_guicciardini["surface_form"].endswith("Histories"):
    raise SystemExit("p.299 Guicciardini mention changed; review title/person boundary")
if not old_museum or old_museum["candidate_id"] != REUSED["gori_subentry"] or old_museum["surface_form"] != "Museum Etruscum":
    raise SystemExit("p.299 Museum Etruscum mention changed")
mentions = [row for row in mentions if row["mention_id"] != GUICCIARDINI_MENTION_ID]
mids.remove(GUICCIARDINI_MENTION_ID)
by_mid.pop(GUICCIARDINI_MENTION_ID)

by_cid[REUSED["gori_letters"]]["canonical_name"] = (
    "Joseph Smith’s letters to A. F. Gori, Biblioteca Marucelliana, MSS. B. VIII, 4 (1727–1744)"
)
by_cid[REUSED["gori_letters"]]["detail"] = (
    "P.299 note 4 identifies MSS. B. VIII, 4 and says the letters span 1727–1744, most written 1735–1737; "
    "p.306 refers to the 1737–1738 gems-and-cameos subset. The letters were not consulted. The printed shelfmark "
    "is B. VIII, 4; canonical OCR reads B. Vin, 4."
)

BODY_LINKS = {
    1: ["st-chp10-p299-smith-life-and-education"],
    2: ["st-chp10-p299-smith-trade-and-guild-dispute"],
    3: ["st-chp10-p299-residence-diplomatic-meetings"],
    4: ["st-chp10-p299-gori-guicciardini-and-museum", "st-chp10-p299-publication-obstacles", "st-chp10-p299-smith-books-gems-pictures"],
}
for marker, target_ids in BODY_LINKS.items():
    for sid in target_ids:
        row = by_sid.get(sid)
        if not row or row.get("qualifiers", {}).get("footnote_marker") != marker:
            raise SystemExit(f"body target changed for footnote {marker}: {sid}")
        if not row["qualifiers"].get("footnote_text_pending"):
            raise SystemExit(f"body footnote was already resolved: {sid}")


def segment_text_and_offsets(start_line, end_line):
    text = "\n".join(source_lines[start_line - 1:end_line])
    offsets = {}
    offset = 0
    for line_no in range(start_line, end_line + 1):
        offsets[line_no] = offset
        offset += len(source_lines[line_no - 1]) + 1
    return text, offsets


BODY_TEXT, BODY_OFFSETS = segment_text_and_offsets(354, 366)
NOTES_TEXT, NOTES_OFFSETS = segment_text_and_offsets(491, 634)
new_mentions = []
new_statements = []
new_mids = set()
new_sids = set()


def add_mention(local_id, segment_id, line_no, surface, candidate_id, note, occurrence=0):
    mention_id = f"m-chp10-p299-{local_id}"
    if mention_id in mids or mention_id in new_mids:
        raise SystemExit(f"duplicate mention id: {mention_id}")
    allowed = cids | {row["candidate_id"] for row in new_candidates}
    if candidate_id not in allowed:
        raise SystemExit(f"missing candidate for {mention_id}: {candidate_id}")
    line = source_lines[line_no - 1]
    positions, cursor = [], 0
    while True:
        found = line.find(surface, cursor)
        if found < 0:
            break
        positions.append(found)
        cursor = found + max(1, len(surface))
    if occurrence >= len(positions):
        raise SystemExit(f"surface absent at L{line_no}: {surface!r}")
    base = BODY_OFFSETS[line_no] if segment_id == BODY_SEG else NOTES_OFFSETS[line_no]
    segment_text = BODY_TEXT if segment_id == BODY_SEG else NOTES_TEXT
    start = base + positions[occurrence]
    end = start + len(surface)
    if segment_text[start:end] != surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })
    new_mids.add(mention_id)


# Split the p.299 body phrase into the named author and the separately cited book.
add_mention("guicciardini-author", BODY_SEG, 364, "Guicciardini", REUSED["guicciardini_person"],
            "Author named in the possessive phrase; separate from the cited book title.")
add_mention("guicciardini-histories", BODY_SEG, 364, "Histories", C["guicciardini_histories"],
            "Title element of the cited work; exact full title and edition unspecified.")
add_mention("p299-note4-guicciardini-work", BODY_SEG, 366, "Guicciardini", C["guicciardini_histories"],
            "Here the surname refers metonymically to the Histories named in the preceding body passage.")
add_mention("p299-note4-pasquali-publisher", BODY_SEG, 366, "Pasquali", REUSED["pasquali_person"],
            "Surname used in the publishing context; person/press role is not expanded beyond the source.")
add_mention("n1-parker-author", NOTES_SEG, 578, "Parker", REUSED["parker_person"],
            "Surname-only author reference; identity remains for S3.")
add_mention("n1-parker-locator", NOTES_SEG, 578, "1948, pp. 10 ff.", C["parker_book"],
            "Matched by author/year to the local Parker bibliography entry; cited pages unread.")
add_mention("n1-smith-will", NOTES_SEG, 578, "his will", REUSED["smith_will"],
            "The will is a document published in the cited Parker work; it is distinct from that publication.")
add_mention("n2-smith-business", NOTES_SEG, 579, "Smith", REUSED["smith"], "Joseph Smith named in the archival-source note.", occurrence=0)
add_mention("n2-gabrieli-1", NOTES_SEG, 579, "Lodovico Gabrieli", REUSED["gabrieli"], "Named notary; person identity remains for S3.", occurrence=0)
add_mention("n2-archivio-1", NOTES_SEG, 579, "Archivio di Stato", REUSED["archivio_venezia"],
            "Short repository form; reused Venice archive candidate, with branch distinction pending S3.", occurrence=0)
add_mention("n2-notarial-series", NOTES_SEG, 579, "Atti del Notaio", C["gabrieli_registers"],
            "Series title within the Sezione Notarile citation.")
add_mention("n2-gabrieli-2", NOTES_SEG, 579, "Lodovico Gabrieli", REUSED["gabrieli"], "The notary is repeated in the archival series title.", occurrence=1)
add_mention("n2-buste-locator", NOTES_SEG, 579, "Buste 7559-7570", C["gabrieli_registers"],
            "Exact busta range and date range as printed; registers unread.")
add_mention("n2-smith-references", NOTES_SEG, 579, "Smith", REUSED["smith"], "The cited papers are said to mention Smith frequently.", occurrence=1)
add_mention("n2-archivio-2", NOTES_SEG, 579, "Archivio di Stato", REUSED["archivio_venezia"],
            "Short repository form in the second archival reference.", occurrence=1)
add_mention("n2-avogaria", NOTES_SEG, 579, "Avogaria di Comun", C["avogaria"],
            "Record-producing office named by Haskell; exact institutional boundary pending S3.")
add_mention("n2-civil-file", NOTES_SEG, 579, "Civil 263/16", C["civil_record"], "Specific archival file locator; file unread.")
add_mention("n2-smith-dispute", NOTES_SEG, 579, "Smith", REUSED["smith"], "Joseph Smith named in the reported dispute.", occurrence=2)
add_mention("n2-salumieri", NOTES_SEG, 579, "Arte de’ Salumieri", REUSED["salumieri"], "Guild named in the reported dispute.")
add_mention("n3-public-record-office", NOTES_SEG, 580, "Public Record Office", REUSED["public_record_office"],
            "Repository name retained as printed; no modern institutional identity substituted.")
add_mention("n3-state-papers", NOTES_SEG, 580, "State Papers 99/60", C["tron_letter"], "Specific cited letter locator; archival letter unread.")
add_mention("n3-resident-author", NOTES_SEG, 580, "British Resident", C["resident_1714"], "Office-only attribution; author identity unknown.")
add_mention("n3-tron", NOTES_SEG, 580, "Signor Tron", C["tron_1714"], "Surname/title only; identity unresolved.")
add_mention("n3-london", NOTES_SEG, 580, "London", REUSED["london"], "Destination named in the quoted letter.")
add_mention("n3-williams-smith-house", NOTES_SEG, 580, "Williams and Smith", C["williams_smith_merchants"],
            "Collective/business boundary unresolved; not equated with Smith’s residence.")
add_mention("n4-letters", NOTES_SEG, 581, "letters", REUSED["gori_letters"], "Letters cited by Haskell; exact contents unread.")
add_mention("n4-joseph-smith", NOTES_SEG, 581, "Joseph Smith", REUSED["smith"], "Sender named in the short citation.")
add_mention("n4-gori", NOTES_SEG, 581, "A. F. Gori", REUSED["gori"], "Recipient named; indexed candidate retained for S3.")
add_mention("n4-library", NOTES_SEG, 581, "Biblioteca Marucelliana", C["marucelliana"], "Repository named in the source locator.")
add_mention("n4-florence", NOTES_SEG, 581, "Florence", REUSED["florence"], "City given in the manuscript locator.")
add_mention("n4-shelfmark", NOTES_SEG, 581, "MSS. B. Vin, 4", REUSED["gori_letters"],
            "Canonical OCR reads B. Vin, 4; the printed page reads MSS. B. VIII, 4.")

# Reassign the existing indexed subentry mention to a real work candidate; retain the person mention separately.
old_museum["candidate_id"] = C["museum_etruscum"]
old_museum["note"] = "Publication/work named in the passage; distinct from Gori and from the index subentry candidate."


def add_statement(local_id, segment_id, start_line, end_line, marker, predicate, claim, subject=None, obj=None,
                  mentioned=(), relation=False, text_layer="footnote narrative", qualification="", citations=(),
                  related_body_ids=(), speaker="Haskell, footnote"):
    statement_id = f"st-chp10-p299-{local_id}"
    if statement_id in sids or statement_id in new_sids:
        raise SystemExit(f"duplicate statement id: {statement_id}")
    qualifiers = {
        "source_line_start": start_line, "source_line_end": end_line,
        "printed_page": 299, "pdf_physical_page": 28,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
        "relation_candidate": relation, "footnote_marker": marker,
        "footnote_text_pending": False,
        "related_body_statement_ids": list(related_body_ids),
    }
    if citations:
        qualifiers["citations"] = list(citations)
        qualifiers["cited_material_not_independently_consulted"] = True
    row = {
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": "\n".join(source_lines[start_line - 1:end_line]),
        "origin": "book", "source_file": SOURCE_FILE,
    }
    new_statements.append(row)
    new_sids.add(statement_id)
    return statement_id


add_statement(
    "note1-parker-career-citation", NOTES_SEG, 578, 578, 1, "footnote_citation",
    "P.299 note 1 directs readers to Parker’s 1948 publication, pages 10 ff., for a fuller account of Smith’s career and says it also publishes his will and other documents.",
    obj=C["parker_book"], mentioned=[REUSED["parker_person"], C["parker_book"], REUSED["smith_will"]],
    text_layer="bibliographic pointer",
    qualification="The Parker publication is matched to the local bibliography. Neither it, the cited pages nor the will were independently consulted.",
    citations=[{"source_candidate_id": C["parker_book"], "year": "1948", "pages": "10 ff.", "bibliography_match": "local"}],
    related_body_ids=BODY_LINKS[1],
)
add_statement(
    "note2-gabrieli-notarial-records", NOTES_SEG, 579, 579, 2, "footnote_citation",
    "Haskell points to Lodovico Gabrieli’s notarial papers, where he says references to Smith are frequent after about 1740; he says he could not trace who Smith’s notary was before that date.",
    subject=REUSED["smith"], obj=C["gabrieli_registers"],
    mentioned=[REUSED["smith"], REUSED["gabrieli"], REUSED["archivio_venezia"], C["gabrieli_registers"]],
    text_layer="archival bibliographic pointer",
    qualification="The registers were not consulted. The lack of an identified earlier notary is Haskell’s research limitation, not proof that none existed.",
    citations=[{"source_candidate_id": C["gabrieli_registers"], "repository_candidate_id": REUSED["archivio_venezia"],
                "call_number": "Buste 7559-7570", "date_range": "1740-1770", "bibliography_match": "source locator"}],
    related_body_ids=BODY_LINKS[2],
)
add_statement(
    "note2-avogaria-dispute-account", NOTES_SEG, 579, 579, 2, "archival_account_of_dispute_between_smith_and_arte_de_salumieri",
    "Haskell says Archivio di Stato file Avogaria di Comun—Civil 263/16 contains an account of a dispute between Smith and the Arte de’ Salumieri.",
    subject=REUSED["smith"], obj=REUSED["salumieri"],
    mentioned=[REUSED["smith"], REUSED["salumieri"], C["avogaria"], C["civil_record"], REUSED["archivio_venezia"]],
    relation=True, text_layer="archival source locator",
    qualification="This records Haskell’s description of the file; the file and the dispute details were not independently consulted.",
    citations=[{"source_candidate_id": C["civil_record"], "repository_candidate_id": REUSED["archivio_venezia"],
                "call_number": "Civil 263/16", "bibliography_match": "source locator"}],
    related_body_ids=BODY_LINKS[2],
)
add_statement(
    "note3-state-papers-letter-citation", NOTES_SEG, 580, 580, 3, "footnote_citation",
    "P.299 note 3 cites Public Record Office, State Papers 99/60, a letter from an unnamed British Resident dated 18 May 1714, and quotes a passage about Signor Tron.",
    obj=C["tron_letter"], mentioned=[REUSED["public_record_office"], C["tron_letter"], C["resident_1714"], C["tron_1714"], REUSED["london"], C["williams_smith_merchants"]],
    text_layer="archival bibliographic pointer",
    qualification="The archive record was not consulted; the quotation is available only through Haskell’s footnote.",
    citations=[{"source_candidate_id": C["tron_letter"], "repository_candidate_id": REUSED["public_record_office"],
                "series": "State Papers", "reference": "99/60", "date": "1714-05-18", "bibliography_match": "source locator"}],
    related_body_ids=BODY_LINKS[3],
)
add_statement(
    "note3-tron-ambassador-to-london", NOTES_SEG, 580, 580, 3, "letter_describes_tron_as_going_as_ambassador_to_london",
    "In Haskell’s quotation, the British Resident describes Signor Tron as going as Ambassador to London.",
    subject=C["tron_1714"], obj=REUSED["london"],
    mentioned=[C["tron_1714"], REUSED["london"], C["tron_letter"]],
    relation=True, text_layer="archival letter quoted by Haskell",
    qualification="The text says Tron was going as Ambassador; it does not provide a full name or establish a separate appointment date. The letter was not consulted.",
    related_body_ids=BODY_LINKS[3],
)
add_statement(
    "note3-tron-meeting-request", NOTES_SEG, 580, 580, 3, "tron_requested_meeting_with_british_resident_at_williams_smith_house",
    "The quoted letter says Tron wanted to see its unnamed British Resident before departing and desired to meet at the house of Messrs. Williams and Smith, described as British merchants.",
    subject=C["tron_1714"], obj=C["resident_1714"],
    mentioned=[C["tron_1714"], C["resident_1714"], C["williams_smith_merchants"], C["tron_letter"]],
    relation=True, text_layer="archival letter quoted by Haskell",
    qualification="The quote reports a desired meeting, not that it occurred. Haskell links this note to Smith’s house, but the named merchant house is kept separate and is not identified with that residence.",
    related_body_ids=BODY_LINKS[3],
)
add_statement(
    "note4-gori-letters-citation", NOTES_SEG, 581, 581, 4, "footnote_citation",
    "P.299 note 4 locates Joseph Smith’s letters to A. F. Gori in Biblioteca Marucelliana, MSS. B. VIII, 4.",
    obj=REUSED["gori_letters"], mentioned=[REUSED["smith"], REUSED["gori"], C["marucelliana"], REUSED["florence"], REUSED["gori_letters"]],
    text_layer="archival bibliographic pointer",
    qualification="The shelfmark was read from the printed p.299 scan (OCR: ‘B. Vin, 4’); the letters were not consulted.",
    citations=[{"source_candidate_id": REUSED["gori_letters"], "repository_candidate_id": C["marucelliana"],
                "shelfmark": "MSS. B. VIII, 4", "date_range": "1727-1744", "bibliography_match": "source locator"}],
    related_body_ids=BODY_LINKS[4],
)
add_statement(
    "note4-gori-letter-date-range", BODY_SEG, 366, 366, 4, "smith_gori_letters_ranged_1727_1744_most_written_1735_1737",
    "Haskell says the Smith–Gori letters extend from 1727 to 1744, with most written between 1735 and 1737.",
    subject=REUSED["smith"], obj=REUSED["gori_letters"],
    mentioned=[REUSED["smith"], REUSED["gori"], REUSED["gori_letters"]],
    relation=True, text_layer="footnote continuation",
    qualification="The p.299 scan confirms this is the continuation of footnote 4. OCR spaces in ‘173 5’ and ‘173 7’ are scan-corrected in S2 only; the correspondence was not consulted.",
    related_body_ids=BODY_LINKS[4],
)
add_statement(
    "note4-guicciardini-publication", BODY_SEG, 366, 366, 4, "guicciardini_histories_eventually_published_by_pasquali_in_1738",
    "Haskell says the Guicciardini Histories were eventually published by Pasquali in 1738.",
    subject=C["guicciardini_histories"], obj=REUSED["pasquali_person"],
    mentioned=[C["guicciardini_histories"], REUSED["pasquali_person"], C["museum_etruscum"]],
    relation=True, text_layer="footnote continuation",
    qualification="The title and edition are unspecified. ‘Pasquali’ is retained as the surname in the source’s publishing context; no imprint or publication copy was consulted.",
    related_body_ids=BODY_LINKS[4],
)

all_candidate_ids = cids | {row["candidate_id"] for row in new_candidates}
for row in new_statements:
    q = row["qualifiers"]
    for endpoint in (row["subject_candidate_id"], row["object_candidate_id"]):
        if endpoint and endpoint not in all_candidate_ids:
            raise SystemExit(f"unknown statement endpoint: {row['statement_id']} {endpoint}")
    for cid in q["mentioned_candidate_ids"]:
        if cid not in all_candidate_ids:
            raise SystemExit(f"unknown mentioned candidate: {row['statement_id']} {cid}")
    for citation in q.get("citations", []):
        for key in ("source_candidate_id", "repository_candidate_id"):
            cid = citation.get(key)
            if cid and cid not in all_candidate_ids:
                raise SystemExit(f"unknown citation candidate: {row['statement_id']} {cid}")
    for sid in q["related_body_statement_ids"]:
        if sid not in by_sid:
            raise SystemExit(f"unknown related body statement: {row['statement_id']} {sid}")
    if not row["original_quote"]:
        raise SystemExit(f"empty source quote: {row['statement_id']}")

# Add source-title candidates to the existing p.299 body statements; leave the indexed person candidates for S3.
for sid in ("st-chp10-p299-gori-guicciardini-and-museum", "st-chp10-p299-publication-obstacles"):
    q = by_sid[sid]["qualifiers"]
    q["mentioned_candidate_ids"] = [cid for cid in q["mentioned_candidate_ids"] if cid != REUSED["gori_subentry"]]
    q["mentioned_candidate_ids"] = list(dict.fromkeys(q["mentioned_candidate_ids"] + [C["guicciardini_histories"], C["museum_etruscum"]]))
    q["qualification"] = q["qualification"].replace(
        "The work titles are index candidates pending S3; authorship/work identity retained for S3 resolution.",
        "The work titles have separate archive candidates; their exact editions remain unspecified."
    )
    q["qualification"] = q["qualification"].replace(
        "The family and dedicatee are unnamed; ",
        "The Guicciardini Histories candidate is separate from its author; the family and dedicatee are unnamed; "
    )

for marker, target_ids in BODY_LINKS.items():
    for sid in target_ids:
        q = by_sid[sid]["qualifiers"]
        q["footnote_text_pending"] = False
        if marker == 1:
            q["qualification"] = "The cited Parker publication and pages are not independently consulted; retain the approximate birth date and the source's account as stated."
        elif marker == 2:
            q["qualification"] = "Footnote 2 cites an archival account of a dispute in Civil 263/16, but the file is unread and supplies no dispute details here."
        elif marker == 3:
            q["qualification"] = "The 1714 letter is quoted in footnote 3 but was not consulted directly. Its ‘Williams and Smith’ house remains distinct from the unidentified Smith residence pending identity/context review."
        elif sid == "st-chp10-p299-gori-guicciardini-and-museum":
            q["qualification"] = "The Guicciardini Histories and Museum Etruscum have separate archive candidates; exact editions remain unspecified and the letters were not consulted."
        elif sid == "st-chp10-p299-publication-obstacles":
            q["qualification"] = "The family and dedicatee are unnamed; ‘famous painter’ remains Haskell’s characterization. The cited letters are unread."
        else:
            q["qualification"] = "Footnote 4 concerns the Gori correspondence and publication context; it does not independently document each purchase of books, gems or pictures."

# The p.299 body is now complete through its note 4 continuation at L366; p.300 closes the consular sentence.
body_cov = cov[BODY_SEG]
body_cov["migration_status"] = "complete"
body_cov["source_line_ranges"] = "L354-366"
body_cov["note"] = (
    "Printed p.299 body and footnotes 1-4 checked against CHP-10.pdf physical page 28. Footnote 4 continues at L366 "
    "in the canonical body OCR; that line is linked to the consolidated note at L581. P.299 consular sentence closes "
    "at p.300 L369. All page body ranges and footnote markers are now migrated."
)
notes_cov = cov[NOTES_SEG]
notes_cov["source_line_ranges"] = "L492-581"
notes_cov["note"] = (
    "Merged-note source processed in order through p.299 notes 1-4. P.299 note 4 continues at canonical body L366; "
    "the p.299 scan confirms its date-range and Guicciardini publication lines belong to the footnote. Notes and "
    "archival citations are linked; cited books, letters and records were not independently consulted. "
    "Next source range: p.300 note 1 at L582."
)

# Refuse duplicate or intersecting new mention spans, including overlaps with existing anchors in the two target segments.
new_ids = {row["mention_id"] for row in new_mentions}
if len(new_ids) != len(new_mentions):
    raise SystemExit("duplicate new mention ID")
target_existing = [row for row in mentions if row["segment_id"] in {BODY_SEG, NOTES_SEG}]
for item in new_mentions:
    for existing in target_existing:
        if existing["segment_id"] == item["segment_id"] and int(existing["start_char"]) < int(item["end_char"]) and int(item["start_char"]) < int(existing["end_char"]):
            raise SystemExit(f"new mention overlaps an existing anchor: {item['mention_id']} / {existing['mention_id']}")
for i, left in enumerate(new_mentions):
    for right in new_mentions[i + 1:]:
        if left["segment_id"] == right["segment_id"] and int(left["start_char"]) < int(right["end_char"]) and int(right["start_char"]) < int(left["end_char"]):
            raise SystemExit(f"new mention spans overlap: {left['mention_id']} / {right['mention_id']}")

print(json.dumps({
    "mode": "apply" if args.apply else "dry-run",
    "new_candidates": [row["candidate_id"] for row in new_candidates],
    "new_mentions": len(new_mentions),
    "replaced_overlapping_index_mention": GUICCIARDINI_MENTION_ID,
    "new_statements": [row["statement_id"] for row in new_statements],
    "p299_markers_resolved": [1, 2, 3, 4],
    "coverage_changes": {BODY_SEG: "reviewed/complete L354-366", NOTES_SEG: "reviewed/partial through L581"},
    "next_source_range": "p.300 note 1 (L582)",
}, ensure_ascii=False, indent=2))

if args.apply:
    paths = [cp, mp, sp, vp]
    backups = [Path(str(path) + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("a p.299 migration backup already exists; inspect before applying")
    for path, backup in zip(paths, backups):
        shutil.copy2(path, backup)
    candidates.extend(new_candidates)
    mentions.extend(new_mentions)
    statements.extend(new_statements)
    write_csv(cp, cf, candidates)
    write_csv(mp, mf, mentions)
    write_jsonl(sp, statements)
    write_csv(vp, vf, coverage)
    print("applied; backups=" + ", ".join(path.name for path in backups))
