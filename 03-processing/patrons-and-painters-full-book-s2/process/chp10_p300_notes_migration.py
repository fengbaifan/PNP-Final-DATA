"""Controlled S2 migration of p.300 notes 1-7 and scattered note continuations; dry-run unless --apply."""
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
BODY_SEG = "chp-10:10_CHP-10_intro:l368-380"
NOTES_SEG = "chp-10:10_CHP-10_intro:l491-634"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
BODY_SHA = "a58eea87703095acaf4a07377eb5d7100bd76a790c0f082e230997e995d686a6"
NOTES_SHA = "9836ce7985ec06a07b8801d319995a534a59cdf8e1c7fc20a64ee89e4651e829"
BACKUP_SUFFIX = ".bak-s2-chp10-p300-notes-20261002"
EXPECTED_MAX_CANDIDATE = 9494


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
body_text = "\n".join(source_lines[367:380])
notes_text = "\n".join(source_lines[581:588])
if hashlib.sha256(body_text.encode("utf-8")).hexdigest() != BODY_SHA:
    raise SystemExit("p.300 body segment L368-L380 changed")
if hashlib.sha256(notes_text.encode("utf-8")).hexdigest() != NOTES_SHA:
    raise SystemExit("p.300 consolidated notes L582-L588 changed")
for line_no, prefix in {
    582: "1 Public Record Office",
    583: "2 See Goldoni",
    584: "3 For many vivid comments",
    585: "4 [Andrea Memmo]",
    586: "5 B. Brunelli",
    587: "6 Public Record Office",
    588: "7 Letter from Smith",
}.items():
    if not source_lines[line_no - 1].startswith(prefix):
        raise SystemExit(f"p.300 note at L{line_no} changed")
if not source_lines[378].startswith("See also Arcbivio di Stato"):
    raise SystemExit("p.300 note 1 continuation at L379 changed")
if not source_lines[379].startswith("32,802, f. 182"):
    raise SystemExit("p.300 note 7 continuation at L380 changed")

bib_text = BIB.read_text(encoding="utf-8-sig")
for fragment in (
    "Goldoni, Carlo: Tutte le opere", "1935-1956",
    "Brunelli, Bruno: Un’amica del Casanova", "Milano 1923",
    "Elementi dell", "Roma 1786",
    "Blunt, Anthony and Croft-Murray, Edward: Venetian drawings of the XVII and XVIII centuries",
    "London 1957",
):
    if fragment not in bib_text:
        raise SystemExit(f"local bibliography match changed: {fragment}")

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
    BODY_SEG: ("reviewed", "partial", "L369-378"),
    NOTES_SEG: ("reviewed", "partial", "L492-581"),
}
for segment_id, expected in expected_coverage.items():
    row = cov.get(segment_id)
    actual = (row["disposition"], row["migration_status"], row["source_line_ranges"]) if row else None
    if actual != expected:
        raise SystemExit(f"coverage changed: {segment_id}: {actual}")

REUSED = {
    "smith": "cand-2440", "goldoni_index": "cand-1207", "goldoni_play": "cand-9184",
    "ricci": "cand-2149", "zanetti": "cand-2838", "gherardi": "cand-1155",
    "muratori": "cand-1717", "memmo": "cand-1642", "memmo_elementi": "cand-1647",
    "newcastle": "cand-1738", "brunelli_blunt_book": "cand-9340",
    "public_record_office": "cand-8289", "venice_archive": "cand-8592",
    "estense": "cand-8539", "modena": "cand-3416", "florence": "cand-3397",
    "british_museum": "cand-5986",
}
if any(cid not in cids for cid in REUSED.values()):
    raise SystemExit("a required existing candidate is missing")
if by_cid[REUSED["goldoni_index"]]["canonical_name"] != "Goldoni, Carlo":
    raise SystemExit("indexed Goldoni candidate changed")
if by_cid[REUSED["memmo_elementi"]]["sub_entry"] != "Elementi dell'Architettura lodoliana":
    raise SystemExit("indexed Memmo publication candidate changed")
if not by_cid[REUSED["brunelli_blunt_book"]]["canonical_name"].startswith("Blunt and Croft-Murray, 1957"):
    raise SystemExit("existing Blunt/Croft-Murray citation candidate changed")

NEW_SPECS = [
    ("state_papers_99_70", "Public Record Office, State Papers 99/70: letters dated 10 and 31 January, 10 May and 10 June 1766 (citation locator)", "archive",
     "P.300 note 1 cites four 1766 letters in State Papers 99/70 for the temporary consulship account. The letters and register were not consulted.", f"{NOTES_SEG}#L582"),
    ("goldoni_opere_v", "Goldoni, Opere, vol. V, p. 259 (citation locator; edition unspecified)", "archive",
     "P.300 note 2 cites Goldoni's dedication of Il Filosofo Inglese to Smith at this locator. The local bibliography lists Goldoni's Tutte le opere (Giuseppe Ortolani ed., 1935–1956), a possible collection match; neither edition nor cited page was consulted.", f"{NOTES_SEG}#L583"),
    ("operatic_caricatures", "Unidentified collection of operatic caricatures owned by Joseph Smith, attributed to Marco Ricci, A. M. Zanetti and others", "work",
     "The p.300 note's 'He' continues the Smith-focused body claim that he was an opera-goer; the intervening Goldoni dedication is a citation example. No individual caricatures, quantity or catalogue is identified.", f"{NOTES_SEG}#L583"),
    ("gherardi_muratori_letters", "Letters from P. E. Gherardi to L. A. Muratori cited for publishing activities (Biblioteca Estense; dates unspecified)", "archive",
     "P.300 note 3 points to an unspecified plural set of letters and Chapter 13. Keep this locator distinct from individually cited dated Gherardi–Muratori letters; the correspondence was not consulted.", f"{NOTES_SEG}#L584"),
    ("lami_memorabilia", "Lami, Memorabilia (Firenze, 1742), p. 386 (citation locator; author identity unresolved)", "archive",
     "P.300 note 4 says Memmo's 1786 text refers to this work. Only surname, generic title, place and year are supplied; cited text and page were not consulted.", f"{NOTES_SEG}#L585"),
    ("lami_person", "Lami (surname only; author named in p.300 note 4)", "person",
     "Named only by surname as the author of Memorabilia; do not expand or align the identity in S2.", f"{NOTES_SEG}#L585"),
    ("brunelli_book", "Bruno Brunelli, Un’amica del Casanova (Milano, 1923; citation locator)", "archive",
     "Matched by author, title and year to the local bibliography. P.300 note 5 cites it in the discussion of Giustiniana Wynne; the book and cited content were not consulted.", f"{NOTES_SEG}#L586"),
    ("brunelli_person", "Bruno Brunelli (author named in p.300 note 5)", "person",
     "Full name supplied by the matching local bibliography entry for Un’amica del Casanova (Milano, 1923); identity is retained as a candidate for S3.", f"{NOTES_SEG}#L586"),
    ("state_papers_99_69", "Public Record Office, State Papers 99/69, p. 224r (citation locator)", "archive",
     "P.300 note 6 cites p.224r. S0 OCR reads '2241'; the printed page reads '224r'. The archival item was not consulted.", f"{NOTES_SEG}#L587"),
    ("smith_newcastle_letter", "Joseph Smith to Thomas Pelham-Holles, Duke of Newcastle, 26 August 1740 (British Museum, Add. MSS. 32,802, f. 182)", "archive",
     "P.300 note 7 identifies a letter and locator; the physical page supplies the continuation '32,802, f. 182' at L380, omitted from the canonical OCR. The letter was not consulted.", f"{NOTES_SEG}#L588"),
    ("esposizione_principi_register", "Archivio di Stato, Venice, Esposizione Principi, Reg. 112 (citation locator)", "archive",
     "Additional source cited in the continuation of p.300 note 1 at canonical L379. The repository label follows the source; the register was not consulted.", f"{BODY_SEG}#L379"),
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

# Clarify two reused bibliography/source candidates without replacing their earlier p.284 or p.287 scope.
by_cid[REUSED["brunelli_blunt_book"]]["canonical_name"] = (
    "Anthony Blunt and Edward Croft-Murray, Venetian drawings of the XVII and XVIII centuries in the collection "
    "of Her Majesty the Queen at Windsor Castle (London, 1957; p.284 note 5 pp.61–63; p.300 note 2 pp.137 ff.)"
)
by_cid[REUSED["brunelli_blunt_book"]]["detail"] = (
    "Matched to the joint local bibliography entry. P.284 note 5 cites pp.61–63 and p.300 note 2 cites pp.137 ff.; "
    "neither cited passage nor the book was independently consulted."
)
by_cid[REUSED["memmo_elementi"]]["detail"] = (
    "Indexed subentry for Elementi dell'Architettura lodoliana. The local bibliography has a title/year match, but OCR reads "
    "the author as 'Memnio'; the index supplies Andrea Memmo for the same title. P.300 note 4's cited text/page were not consulted."
)
by_cid[REUSED["british_museum"]]["detail"] += (
    " P.300 note 7 also locates a Joseph Smith letter to the Duke of Newcastle in Add. MSS. 32,802, f.182; "
    "this manuscript was not consulted."
)

BODY_LINKS = {
    1: ["st-chp10-p300-consul-resumption-and-death"],
    2: ["st-chp10-p300-smith-patron-and-painters", "st-chp10-p300-smith-connoisseur-contacts"],
    3: ["st-chp10-p300-palace-meeting-place-and-publishing"],
    4: ["st-chp10-p300-lodoli-memmo-and-smith-meetings"],
    5: ["st-chp10-p300-lodoli-memmo-wynne-rivalry"],
    6: ["st-chp10-p300-smith-influence-after-1744"],
    7: ["st-chp10-p300-smith-claimed-government-friendships"],
}
for marker, target_ids in BODY_LINKS.items():
    for sid in target_ids:
        row = by_sid.get(sid)
        if not row:
            raise SystemExit(f"body target missing for footnote {marker}: {sid}")
        if row.get("qualifiers", {}).get("footnote_marker") == marker and not row["qualifiers"].get("footnote_text_pending"):
            raise SystemExit(f"body footnote already resolved: {sid}")
        if row.get("qualifiers", {}).get("footnote_marker") not in (None, marker):
            raise SystemExit(f"body marker mismatch for footnote {marker}: {sid}")


def make_segment(start_line, end_line):
    text = "\n".join(source_lines[start_line - 1:end_line])
    offsets = {}
    offset = 0
    for line_no in range(start_line, end_line + 1):
        offsets[line_no] = offset
        offset += len(source_lines[line_no - 1]) + 1
    return text, offsets


SEGMENT_TEXTS = {
    BODY_SEG: make_segment(368, 380),
    NOTES_SEG: make_segment(491, 634),
}
new_mentions = []
new_statements = []
new_mids = set()
new_sids = set()


def add_mention(local_id, segment_id, line_no, surface, candidate_id, note, occurrence=0):
    mention_id = f"m-chp10-p300-{local_id}"
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
    segment_text, offsets = SEGMENT_TEXTS[segment_id]
    start = offsets[line_no] + positions[occurrence]
    end = start + len(surface)
    if segment_text[start:end] != surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })
    new_mids.add(mention_id)


# Note 1: two separate archive pointers support the same p.300 body marker.
add_mention("n1-state-papers", NOTES_SEG, 582, "State Papers 99/70", C["state_papers_99_70"], "Archival locator; letters unread.")
add_mention("n1-dates", NOTES_SEG, 582, "10 and 31 January, 10 May and 10 June 1766", C["state_papers_99_70"], "Dates as cited by Haskell.")
add_mention("n1-archivio", BODY_SEG, 379, "Arcbivio di Stato", REUSED["venice_archive"], "S0 OCR spelling; the printed page reads Archivio.")
add_mention("n1-esposizione", BODY_SEG, 379, "Esposizione Principi", C["esposizione_principi_register"], "Additional source in the p.300 note 1 continuation.")
add_mention("n1-registry", BODY_SEG, 379, "Reg. 112", C["esposizione_principi_register"], "Register locator; manuscript not consulted.")

# Note 2: the dedication is identifiable; the pronoun describing the caricature collection is not.
add_mention("n2-goldoni", NOTES_SEG, 583, "Goldoni", REUSED["goldoni_index"], "Index candidate covers the p.300 dedication context.")
add_mention("n2-recipient", NOTES_SEG, 583, "him", REUSED["smith"], "Recipient of Goldoni's dedication in the source context.")
add_mention("n2-play-title", NOTES_SEG, 583, "Filososo Inglese", REUSED["goldoni_play"], "S0 OCR reads 'Filososo'; p.300 scan reads 'Il Filosofo Inglese'.")
add_mention("n2-opere-v", NOTES_SEG, 583, "Opere, V, p. 259", C["goldoni_opere_v"], "Citation locator; edition identity remains open.")
add_mention("n2-caricature-group", NOTES_SEG, 583, "operatic caricatures", C["operatic_caricatures"], "Collective work object; individual sheets not identified.")
add_mention("n2-ricci", NOTES_SEG, 583, "Marco Ricci", REUSED["ricci"], "Artist named as creator of some caricatures.")
add_mention("n2-zanetti", NOTES_SEG, 583, "A. M. Zanetti", REUSED["zanetti"], "Indexed Zanetti candidate reused; full identity remains for S3.")
add_mention("n2-blunt-croft", NOTES_SEG, 583, "Blunt and Croft-Murray", REUSED["brunelli_blunt_book"], "Joint bibliography match to the 1957 Venetian drawings catalogue.")
add_mention("n2-pages", NOTES_SEG, 583, "pp. 137 if", REUSED["brunelli_blunt_book"], "S0 OCR reads 'if'; p.300 print reads 'ff.'.")

# Note 3: the corpus locator is kept separate from individually dated letters.
add_mention("n3-gherardi", NOTES_SEG, 584, "P. E. Gherardi", REUSED["gherardi"], "Author named in Haskell's source pointer.")
add_mention("n3-muratori", NOTES_SEG, 584, "L. A. Muratori", REUSED["muratori"], "Recipient named in Haskell's source pointer.")
add_mention("n3-estense", NOTES_SEG, 584, "Biblioteca Estense", REUSED["estense"], "Repository named in the citation.")
add_mention("n3-modena", NOTES_SEG, 584, "Modena", REUSED["modena"], "City named in the repository locator.")

# Note 4: local matching is possible for Memmo; Lami is supplied only by surname.
add_mention("n4-memmo", NOTES_SEG, 585, "Andrea Memmo", REUSED["memmo"], "Author named in a bracketed citation.")
add_mention("n4-memmo-date", NOTES_SEG, 585, "1786, p. 1", REUSED["memmo_elementi"], "Unique local bibliography match by author and year; book/page unread.")
add_mention("n4-lami", NOTES_SEG, 585, "Lami", C["lami_person"], "Surname-only cited author; identity unresolved.")
add_mention("n4-memorabilia", NOTES_SEG, 585, "Memorabilia", C["lami_memorabilia"], "Generic title as reported by Haskell.")
add_mention("n4-firenze", NOTES_SEG, 585, "Firenze", REUSED["florence"], "Italian city name; reused Florence candidate.")
add_mention("n4-lami-date-page", NOTES_SEG, 585, "1742, p. 386", C["lami_memorabilia"], "Publication locator nested in Haskell's citation.")

# Note 5: exact local bibliography match; cited text unread.
add_mention("n5-brunelli", NOTES_SEG, 586, "B. Brunelli", C["brunelli_person"], "Expanded to Bruno from the matching local bibliography entry.")
add_mention("n5-year", NOTES_SEG, 586, "1923", C["brunelli_book"], "Year matches the local Un’amica del Casanova entry.")

# Note 6: print reading is recto, not the OCR digit 1.
add_mention("n6-state-papers", NOTES_SEG, 587, "State Papers 99/69", C["state_papers_99_69"], "Archive volume cited by Haskell; not consulted.")
add_mention("n6-folio-ocr", NOTES_SEG, 587, "p. 2241", C["state_papers_99_69"], "S0 OCR; printed page reads p.224r.")

# Note 7 and its source-line continuation supply one manuscript locator across two segments.
add_mention("n7-letter", NOTES_SEG, 588, "Letter from Smith to the Duke of Newcastle", C["smith_newcastle_letter"], "Letter identified in the note; manuscript unread.")
add_mention("n7-date", NOTES_SEG, 588, "26 August 1740", C["smith_newcastle_letter"], "Letter date as cited.")
add_mention("n7-repository", NOTES_SEG, 588, "British Museum", REUSED["british_museum"], "Repository named by Haskell.")
add_mention("n7-add-mss", NOTES_SEG, 588, "Add. MSS.", C["smith_newcastle_letter"], "Abbreviation as printed in the note.")
add_mention("n7-folio-continuation", BODY_SEG, 380, "32,802, f. 182.", C["smith_newcastle_letter"], "Physical p.300 continuation; absent from canonical OCR line 588.")


def add_statement(local_id, segment_id, start_line, end_line, marker, predicate, claim, subject=None, obj=None,
                  mentioned=(), relation=False, text_layer="footnote narrative", qualification="", citations=(),
                  related_body_ids=(), extra=None):
    statement_id = f"st-chp10-p300-{local_id}"
    if statement_id in sids or statement_id in new_sids:
        raise SystemExit(f"duplicate statement id: {statement_id}")
    page = 300
    physical_page = 29
    qualifiers = {
        "source_line_start": start_line, "source_line_end": end_line,
        "printed_page": page, "pdf_physical_page": physical_page,
        "claim": claim, "speaker": "Haskell, footnote", "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
        "relation_candidate": relation, "footnote_marker": marker,
        "footnote_text_pending": False,
        "related_body_statement_ids": list(related_body_ids),
    }
    if citations:
        qualifiers["citations"] = list(citations)
        qualifiers["cited_material_not_independently_consulted"] = True
    if extra:
        qualifiers.update(extra)
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
    "note1-state-papers-99-70", NOTES_SEG, 582, 582, 1, "footnote_citation",
    "P.300 note 1 cites Public Record Office, State Papers 99/70, letters dated 10 and 31 January, 10 May and 10 June 1766.",
    obj=C["state_papers_99_70"], mentioned=[REUSED["public_record_office"], C["state_papers_99_70"]],
    text_layer="archival bibliographic pointer",
    qualification="The four dates are given without individual correspondents or letter contents; the cited letters were not consulted.",
    citations=[{"source_candidate_id": C["state_papers_99_70"], "repository_candidate_id": REUSED["public_record_office"],
                "series": "State Papers", "reference": "99/70", "dates": ["1766-01-10", "1766-01-31", "1766-05-10", "1766-06-10"], "bibliography_match": "source locator"}],
    related_body_ids=BODY_LINKS[1],
)
add_statement(
    "note1-esposizione-register", BODY_SEG, 379, 379, 1, "footnote_citation",
    "The continuation of p.300 note 1 also cites Archivio di Stato, Venice, Esposizione Principi, Reg. 112.",
    obj=C["esposizione_principi_register"], mentioned=[REUSED["venice_archive"], C["esposizione_principi_register"]],
    text_layer="archival bibliographic pointer",
    qualification="L379 is a continuation of p.300 note 1, not a second source segment or duplicate chapter content. The register was not consulted; S0 OCR 'Arcbivio' is read as printed 'Archivio'.",
    citations=[{"source_candidate_id": C["esposizione_principi_register"], "repository_candidate_id": REUSED["venice_archive"],
                "series": "Esposizione Principi", "register": "112", "bibliography_match": "source locator"}],
    related_body_ids=BODY_LINKS[1],
)
add_statement(
    "note2-goldoni-dedication", NOTES_SEG, 583, 583, 2, "goldoni_dedicated_il_filosofo_inglese_to_joseph_smith",
    "Haskell identifies the play Goldoni dedicated to Joseph Smith as Il Filosofo Inglese and cites Opere, vol. V, p.259.",
    subject=REUSED["goldoni_index"], obj=REUSED["goldoni_play"],
    mentioned=[REUSED["goldoni_index"], REUSED["smith"], REUSED["goldoni_play"], C["goldoni_opere_v"]],
    relation=True, text_layer="bibliographic pointer",
    qualification="The print reads 'Il Filosofo Inglese'; canonical OCR has '1/ Filososo Inglese'. The cited volume was not consulted; a local bibliography entry for Tutte le opere is only a possible edition match.",
    citations=[{"source_candidate_id": C["goldoni_opere_v"], "volume": "V", "page": "259", "possible_local_match": "Goldoni, Tutte le opere, ed. Giuseppe Ortolani, 1935-1956", "bibliography_match": "possible"}],
    related_body_ids=BODY_LINKS[2],
)
add_statement(
    "note2-operatic-caricature-collection", NOTES_SEG, 583, 583, 2, "smith_owned_operatic_caricature_collection",
    "Haskell says Joseph Smith owned a large collection of operatic caricatures by Marco Ricci, A. M. Zanetti and others, and cites Blunt and Croft-Murray, pp.137 ff.",
    subject=REUSED["smith"], obj=C["operatic_caricatures"],
    mentioned=[REUSED["smith"], C["operatic_caricatures"], REUSED["ricci"], REUSED["zanetti"], REUSED["brunelli_blunt_book"]],
    relation=True, text_layer="bibliographic pointer",
    qualification="The note's 'He' continues the Smith-focused body topic and refers to the recipient 'him' in the Goldoni-dedication citation. The collection and cited pages are not independently identified or consulted. The local joint bibliography match is the 1957 Venetian drawings catalogue.",
    citations=[{"source_candidate_id": REUSED["brunelli_blunt_book"], "pages": "137 ff.", "bibliography_match": "local"}],
    related_body_ids=BODY_LINKS[2],
)
add_statement(
    "note3-gherardi-muratori-letters", NOTES_SEG, 584, 584, 3, "footnote_citation",
    "Haskell directs readers to letters from P. E. Gherardi to L. A. Muratori at Biblioteca Estense, Modena for comments on Smith and Pasquali's publishing activities, and also refers readers to Chapter 13.",
    obj=C["gherardi_muratori_letters"],
    mentioned=[REUSED["gherardi"], REUSED["muratori"], REUSED["estense"], REUSED["modena"], C["gherardi_muratori_letters"]],
    text_layer="archival bibliographic pointer and internal cross-reference",
    qualification="The cited correspondence is a plural, undated locator and remains distinct from individually dated Gherardi–Muratori letters. Chapter 13 is not yet read; neither letters nor referenced chapter content were consulted for this note.",
    citations=[{"source_candidate_id": C["gherardi_muratori_letters"], "repository_candidate_id": REUSED["estense"], "correspondents": ["P. E. Gherardi", "L. A. Muratori"], "dates": "unspecified", "bibliography_match": "source locator"}],
    related_body_ids=BODY_LINKS[3],
    extra={"internal_cross_reference": {"chapter": 13, "status": "not yet read"}},
)
add_statement(
    "note4-memmo-publication", NOTES_SEG, 585, 585, 4, "footnote_citation",
    "P.300 note 4 cites [Andrea Memmo], 1786, p.1; its title/year match the local bibliography's Elementi dell'architettura lodoliana entry, whose OCR author is 'Memnio', and the index identifies the same work under Andrea Memmo.",
    subject=REUSED["memmo"], obj=REUSED["memmo_elementi"],
    mentioned=[REUSED["memmo"], REUSED["memmo_elementi"]],
    text_layer="bibliographic pointer",
    qualification="The match uses the local title/year entry plus the index's Andrea Memmo subentry; the bibliography OCR reads 'Memnio'. Neither the work nor p.1 was consulted. Brackets around Andrea Memmo are retained from Haskell's citation.",
    citations=[{"source_candidate_id": REUSED["memmo_elementi"], "year": "1786", "page": "1", "bibliography_match": "local title/year plus indexed author; bibliography OCR says Memnio"}],
    related_body_ids=BODY_LINKS[4],
)
add_statement(
    "note4-nested-lami-reference", NOTES_SEG, 585, 585, 4, "memmo_citation_reportedly_refers_to_lami_memorabilia",
    "Haskell says Memmo's 1786 citation in turn refers to Lami, Memorabilia, Firenze 1742, p.386.",
    subject=REUSED["memmo_elementi"], obj=C["lami_memorabilia"],
    mentioned=[REUSED["memmo_elementi"], C["lami_person"], C["lami_memorabilia"], REUSED["florence"]],
    relation=True, text_layer="nested bibliographic pointer",
    qualification="Only surname, generic title, place and year are given for Lami. The bibliographic chain is reported by Haskell; neither cited text nor page was independently consulted.",
    citations=[{"source_candidate_id": C["lami_memorabilia"], "author_surface": "Lami", "place": "Firenze", "year": "1742", "page": "386", "bibliography_match": "not established"}],
    related_body_ids=BODY_LINKS[4],
)
add_statement(
    "note5-brunelli-citation", NOTES_SEG, 586, 586, 5, "footnote_citation",
    "P.300 note 5 cites Bruno Brunelli, Un’amica del Casanova (Milano, 1923).",
    subject=C["brunelli_person"], obj=C["brunelli_book"],
    mentioned=[C["brunelli_person"], C["brunelli_book"]],
    text_layer="bibliographic pointer",
    qualification="Matched to the local bibliography by author, title and year; the book and the cited content were not consulted.",
    citations=[{"source_candidate_id": C["brunelli_book"], "year": "1923", "place": "Milano", "bibliography_match": "local exact title/author/year"}],
    related_body_ids=BODY_LINKS[5],
)
add_statement(
    "note6-state-papers-99-69", NOTES_SEG, 587, 587, 6, "footnote_citation",
    "P.300 note 6 cites Public Record Office, State Papers 99/69, p.224r.",
    obj=C["state_papers_99_69"], mentioned=[REUSED["public_record_office"], C["state_papers_99_69"]],
    text_layer="archival bibliographic pointer",
    qualification="The print reads p.224r; canonical OCR has p.2241. The archive and cited page were not consulted.",
    citations=[{"source_candidate_id": C["state_papers_99_69"], "repository_candidate_id": REUSED["public_record_office"], "series": "State Papers", "reference": "99/69", "page": "224r", "bibliography_match": "source locator"}],
    related_body_ids=BODY_LINKS[6],
)
add_statement(
    "note7-newcastle-letter-citation", NOTES_SEG, 588, 588, 7, "footnote_citation",
    "P.300 note 7 cites a letter from Joseph Smith to the Duke of Newcastle dated 26 August 1740, held as British Museum Add. MSS.",
    subject=REUSED["smith"], obj=C["smith_newcastle_letter"],
    mentioned=[REUSED["smith"], REUSED["newcastle"], REUSED["british_museum"], C["smith_newcastle_letter"]],
    text_layer="archival bibliographic pointer",
    qualification="The letter is not read. Its call-number continuation is recorded separately at L380 in the p.300 body segment.",
    citations=[{"source_candidate_id": C["smith_newcastle_letter"], "repository_candidate_id": REUSED["british_museum"], "date": "1740-08-26", "collection": "Add. MSS.", "call_number_continuation_segment": BODY_SEG, "call_number_continuation_line": 380, "bibliography_match": "source locator"}],
    related_body_ids=BODY_LINKS[7],
)
add_statement(
    "note7-call-number-continuation", BODY_SEG, 380, 380, 7, "archival_call_number_continuation",
    "The p.300 scan continues note 7's British Museum Add. MSS. locator with call number 32,802, f.182.",
    obj=C["smith_newcastle_letter"], mentioned=[REUSED["british_museum"], C["smith_newcastle_letter"]],
    text_layer="footnote continuation",
    qualification="This line is present in the printed p.300 scan but was omitted from the canonical OCR note line L588; it completes that same letter locator and is not a separate source item.",
    citations=[{"source_candidate_id": C["smith_newcastle_letter"], "repository_candidate_id": REUSED["british_museum"], "collection": "Add. MSS.", "call_number": "32,802", "folio": "f.182", "bibliography_match": "source locator"}],
    related_body_ids=BODY_LINKS[7],
)

# Each pending body footnote must resolve to its same numbered note; preserve any non-pending cross-reference target.
for marker, target_ids in BODY_LINKS.items():
    for sid in target_ids:
        row = by_sid[sid]
        if row.get("qualifiers", {}).get("footnote_marker") == marker:
            row["qualifiers"]["footnote_text_pending"] = False

all_candidate_ids = cids | {row["candidate_id"] for row in new_candidates}
for row in new_statements:
    q = row["qualifiers"]
    segment_start, segment_end = (368, 380) if row["segment_id"] == BODY_SEG else (491, 634)
    if q["source_line_start"] < segment_start or q["source_line_end"] > segment_end:
        raise SystemExit(f"statement range outside segment: {row['statement_id']}")
    for endpoint in (row["subject_candidate_id"], row["object_candidate_id"]):
        if endpoint and endpoint not in all_candidate_ids:
            raise SystemExit(f"statement foreign key missing: {row['statement_id']} -> {endpoint}")
    if not all(cid in all_candidate_ids for cid in q["mentioned_candidate_ids"]):
        raise SystemExit(f"mentioned candidate missing: {row['statement_id']}")
    if q.get("footnote_text_pending") is not False:
        raise SystemExit(f"new note statement unexpectedly pending: {row['statement_id']}")
spans = sorted((row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]) for row in new_mentions)
for left, right in zip(spans, spans[1:]):
    if left[0] == right[0] and right[1] < left[2]:
        raise SystemExit(f"overlapping mentions: {left[3]} / {right[3]}")

cov[BODY_SEG].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L369-380",
    "note": "Printed p.300 body and the two scattered footnote continuations at L379–380 checked against CHP-10.pdf physical page 29. P.300 footnotes 1–7 are now linked. L379 continues note 1 with Archivio di Stato, Esposizione Principi, Reg.112; scan spelling is Archivio (S0 OCR 'Arcbivio'). L380 continues note 7 with Add. MSS. 32,802, f.182, missing from canonical OCR L588. The body sentence closes on p.301; S0 remains unchanged.",
})
cov[NOTES_SEG].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L492-588",
    "note": "Merged notes processed through p.300 notes 1–7 at L582–588; note 1 also has its L379 continuation and note 7 its L380 call-number continuation in the p.300 body segment. Cited letters, registers, books and pages were not independently consulted. Note 2's 'He' refers to Smith, continuing the main-text subject and dedication recipient; the collection itself remains without titles or individual items. Note 3's Chapter 13 cross-reference remains unread. Next source range: p.301 note 1 at L589.",
})

summary = {
    "mode": "APPLY" if args.apply else "DRY-RUN",
    "source_sha256": ASSET_SHA,
    "segments": {BODY_SEG: BODY_SHA, NOTES_SEG: NOTES_SHA},
    "new_candidates": len(new_candidates), "candidate_ids": [row["candidate_id"] for row in new_candidates],
    "new_mentions": len(new_mentions), "new_statements": len(new_statements),
    "proposed_candidates": [{"candidate_id": row["candidate_id"], "name": row["canonical_name"],
                             "type": row["suggested_type"], "detail": row["detail"]} for row in new_candidates],
    "proposed_mentions": [{"mention_id": row["mention_id"], "segment_id": row["segment_id"],
                           "candidate_id": row["candidate_id"], "surface_form": row["surface_form"],
                           "start_char": row["start_char"], "end_char": row["end_char"]} for row in new_mentions],
    "proposed_statements": [{"statement_id": row["statement_id"], "segment_id": row["segment_id"],
                             "lines": [row["qualifiers"]["source_line_start"], row["qualifiers"]["source_line_end"]],
                             "predicate": row["predicate"], "claim": row["qualifiers"]["claim"],
                             "subject": row["subject_candidate_id"], "object": row["object_candidate_id"],
                             "relation_candidate": row["qualifiers"]["relation_candidate"]} for row in new_statements],
    "updated_existing_candidates": [
        {"candidate_id": REUSED["brunelli_blunt_book"], "name": by_cid[REUSED["brunelli_blunt_book"]]["canonical_name"]},
        {"candidate_id": REUSED["memmo_elementi"], "detail": by_cid[REUSED["memmo_elementi"]]["detail"]},
        {"candidate_id": REUSED["british_museum"], "detail": by_cid[REUSED["british_museum"]]["detail"]},
    ],
    "resolved_body_markers": list(BODY_LINKS),
    "coverage": {BODY_SEG: cov[BODY_SEG]["migration_status"], NOTES_SEG: cov[NOTES_SEG]["source_line_ranges"]},
}
print(json.dumps(summary, ensure_ascii=False, indent=2))

if args.apply:
    for path in (cp, mp, sp, vp):
        backup = Path(str(path) + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists: {backup}")
        shutil.copy2(path, backup)
    write_csv(cp, cf, candidates + new_candidates)
    write_csv(mp, mf, mentions + new_mentions)
    write_jsonl(sp, statements + new_statements)
    write_csv(vp, vf, [cov[row["segment_id"]] for row in coverage])
    print("Applied p.300 notes 1-7 and their L379/L380 continuations; p.301 notes remain pending.")
