"""Controlled S2 migration of printed p.301 notes 1-7; dry-run unless --apply."""
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
NOTES_SEG = "chp-10:10_CHP-10_intro:l491-634"
P301_BODY = "chp-10:10_CHP-10_intro:l382-389"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
NOTES_SEG_SHA = "33d2557d3e681434a9c964316a7a24fe2c00faa934add1381c12fc4d8a7c7f76"
P301_NOTES_SHA = "ed89fd30a50fe10e30d32415c29a6f45c09c65346c1ff1807a2f91b8b5fdaaab"
BACKUP_SUFFIX = ".bak-s2-chp10-p301-notes-20261002"
EXPECTED_MAX_CANDIDATE = 9505


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
notes_segment_text = "\n".join(source_lines[490:634])
if hashlib.sha256(notes_segment_text.encode("utf-8")).hexdigest() != NOTES_SEG_SHA:
    raise SystemExit("consolidated notes segment changed")
if hashlib.sha256("\n".join(source_lines[588:594]).encode("utf-8")).hexdigest() != P301_NOTES_SHA:
    raise SystemExit("p.301 notes L589-L594 changed")
for line_no, prefix in {
    589: "1 See p. 299, note 4.",
    590: "3 See Previtali.",
    591: "4 There are two very friendly letters",
    592: "6 See p. 299, note 4.",
    593: "6 Smith and Pasquali published many books",
    594: "7 Levey, in Burlington Magazine",
}.items():
    if not source_lines[line_no - 1].startswith(prefix):
        raise SystemExit(f"canonical p.301 note line changed: L{line_no}")
if "2 The case os Canaletto" not in source_lines[588]:
    raise SystemExit("p.301 note 2 no longer shares L589 with note 1")
bib_text = BIB.read_text(encoding="utf-8-sig")
for fragment in (
    "[Grosley, Pierre Jean]: Nouveaux Mémoires ou observations sur l’Italie et sur les italiens,",
    "Arrighi-Landini, Orazio: Il-Tempio della Filosofia, Venezia 1755.",
    "Previtali, G.: ‘Collezionisti di primitivi nel Settecento’ in Paragone, 1959, 113, pp. 3-32.",
    "Previtali, G.: La Fortuna dei Primitivi dal Vasari ai Neoclassici’, Torino 1964",
    "Levey, M.: ‘Wilson and Zuccarelli at Venice’ in Burlington Magazine, 1959, pp.139-143.",
):
    if fragment not in bib_text:
        raise SystemExit(f"local bibliography reference changed: {fragment}")

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
by_candidate = {row["candidate_id"]: row for row in candidates}
by_statement = {row["statement_id"]: row for row in statements}
maximum = max(int(row["candidate_id"].split("-")[-1]) for row in candidates if row["candidate_id"].startswith("cand-"))
if maximum != EXPECTED_MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: {maximum}")
if (cov[NOTES_SEG]["disposition"], cov[NOTES_SEG]["migration_status"], cov[NOTES_SEG]["source_line_ranges"]) != (
    "reviewed", "partial", "L492-588"
):
    raise SystemExit("consolidated-note coverage pre-state changed")
if (cov[P301_BODY]["disposition"], cov[P301_BODY]["migration_status"], cov[P301_BODY]["source_line_ranges"]) != (
    "reviewed", "partial", "L383-389"
):
    raise SystemExit("p.301 body coverage pre-state changed")

BODY_LINKS = {
    1: ["st-chp10-p301-smith-pasquali-publication-activity"],
    2: ["st-chp10-p301-smith-artists-business-arrangements"],
    3: ["st-chp10-p301-lodoli-collection"],
    4: ["st-chp10-p301-poleni-profile"],
    5: ["st-chp10-p301-smith-mead-letter"],
    6: ["st-chp10-p301-mead-newton-friendship"],
    7: ["st-chp10-p301-smith-official-visitors"],
}
for marker, ids in BODY_LINKS.items():
    for sid in ids:
        row = by_statement.get(sid)
        if not row or row.get("qualifiers", {}).get("footnote_marker") != marker:
            raise SystemExit(f"missing p.301 body footnote target {marker}: {sid}")
        if row["qualifiers"].get("footnote_text_pending") is not True:
            raise SystemExit(f"p.301 body footnote is not pending: {sid}")

REUSED = {
    "grosley": "cand-1235", "venice": "cand-3401", "smith": "cand-2440",
    "pasquali": "cand-1844", "pasquali_firm": "cand-9172",
    "canaletto": "cand-0498", "visentini": "cand-2783", "poleni": "cand-9182",
    "marciana": "cand-9448", "gori_letters": "cand-9229", "arrighi": "cand-0122",
    "arrighi_indexed_work": "cand-0123", "newton": "cand-1739",
    "levey": "cand-9442", "burlington": "cand-5903",
}
if any(cid not in cids for cid in REUSED.values()):
    raise SystemExit("a required existing candidate is missing")
if by_candidate[REUSED["arrighi_indexed_work"]]["sub_entry"] != "Tempio della Filosofia":
    raise SystemExit("indexed Arrighi-Landini work candidate changed")

NEW_SPECS = [
    ("grosley_u_p99", "Grosley, U., p.99 (p.301 note 1 citation locator; possible local match to Nouveaux Mémoires)", "archive",
     "Haskell cites Grosley as U, p.99 and quotes a report about Pasquali's press and Smith. The local bibliography lists a Grosley title, Nouveaux Mémoires ou observations sur l’Italie et sur les italiens, without edition details; this is a possible match only. The cited work was not consulted.", 589),
    ("consulate_venue", "Consulat d’Angleterre à Venise (entity type unresolved in p.301 note 1 quotation)", "",
     "The quotation describes Smith as having grown old in the English Consulate at Venice. The source does not clarify whether this refers to the diplomatic institution, premises or office; keep distinct from the British Consul post candidate cand-9173.", 589),
    ("previtali_author", "Previtali, G. (author named in p.301 note 3; full identity unresolved)", "person",
     "The note gives only the surname. The local bibliography lists two G. Previtali works, so the exact cited work and the author's full identity are unresolved for S3.", 590),
    ("previtali_short_citation", "Previtali (p.301 note 3 short-form citation; exact work and page unspecified)", "archive",
     "The note says only “See Previtali.” The local bibliography contains a 1959 article and a 1964 book by G. Previtali; neither can be selected from this note, and neither was consulted.", 590),
    ("poleni_to_smith_1747_04_09", "Giovanni Poleni to Joseph Smith, 9 April 1747 (Biblioteca Marciana, MSS. Ital:Cl.X, Cod CCLXXXVIII-6580)", "archive",
     "Identified by the date, correspondents and shared codex locator in p.301 note 4. Haskell describes this as one of two very friendly Poleni letters. The manuscript was not consulted; folio is not supplied.", 591),
    ("poleni_to_smith_1747_04_17", "Giovanni Poleni to Joseph Smith, 17 April 1747 (Biblioteca Marciana, MSS. Ital:Cl.X, Cod CCLXXXVIII-6580)", "archive",
     "Identified by the date, correspondents and shared codex locator in p.301 note 4. Haskell describes this as one of two very friendly Poleni letters. The manuscript was not consulted; folio is not supplied.", 591),
    ("smith_to_poleni_1747_04_14", "Joseph Smith to Giovanni Poleni, 14 April 1747 (reply to Poleni’s 9 April letter; Biblioteca Marciana, MSS. Ital:Cl.X, Cod CCLXXXVIII-6580)", "archive",
     "P.301 note 4 identifies this as Smith’s answer to the first cited Poleni letter and transcribes a phrase from it. The manuscript was not consulted; folio is not supplied.", 591),
    ("poleni_visentini_drawings", "Unidentified drawings Poleni asked Smith to obtain from Visentini (p.301 note 4)", "work",
     "Haskell says Poleni asked Smith to obtain some drawings for him from Visentini. The note does not identify titles, number, maker, owner or whether Smith completed the request; do not infer that Visentini created them.", 591),
    ("tempio_1757", "Arrighi-Landini, Tempio della Filosofia (cited as 1757, p.30; edition unresolved)", "archive",
     "P.301 note 6 cites page 30 of a Tempio della Filosofia dated 1757. The local bibliography lists Arrighi-Landini’s Il-Tempio della Filosofia, Venezia 1755, and the index has a title subentry; the two-year discrepancy is unresolved. Neither edition nor page was consulted.", 593),
    ("pope_surname", "Pope (surname-only author of the epitaph in p.301 note 6)", "person",
     "The source gives only Pope’s surname for the author of a famous epitaph. Do not expand the identity or infer the epitaph’s subject from the surrounding Newton discussion at S2.", 593),
    ("pope_epitaph", "Pope’s famous epitaph (title and subject unspecified in p.301 note 6)", "work",
     "Haskell’s note describes a copy supplied by Smith to Arrighi-Landini but gives no formal title or subject. Keep distinct from any indexed Newton monument or epitaph until S3.", 593),
    ("levey_author", "M. Levey (author cited in p.301 note 7; identity alignment deferred)", "person",
     "The note gives only Levey; the local bibliography identifies M. Levey for the matching article. Reconciliation with other Levey candidates and the accepted person remains for S3.", 594),
    ("levey_wilson_zuccarelli_article", "M. Levey, “Wilson and Zuccarelli at Venice” (Burlington Magazine, 1959, pp.139–143; citation locator)", "archive",
     "P.301 note 7 cites pages 139 and 143. The local bibliography has an exact title, author-initial, year and page-range match. The article and cited pages were not independently consulted.", 594),
]
new_candidates = []
C = {}
for offset, (key, name, kind, detail, source_line) in enumerate(NEW_SPECS, maximum + 1):
    cid = f"cand-{offset:04d}"
    if cid in cids:
        raise SystemExit(f"candidate id already exists: {cid}")
    C[key] = cid
    new_candidates.append({
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name, "index_page_range": "",
        "suggested_type": kind, "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{NOTES_SEG}#L{source_line}",
    })

segment_offsets = {}
offset = 0
for line_no in range(491, 635):
    segment_offsets[line_no] = offset
    offset += len(source_lines[line_no - 1]) + 1
segment_text = "\n".join(source_lines[490:634])
new_mentions = []
new_statements = []
new_mention_ids = set()
new_statement_ids = set()
all_candidate_ids = cids | {row["candidate_id"] for row in new_candidates}


def add_mention(local_id, line_no, surface, candidate_id, note="", occurrence=0):
    mention_id = f"m-chp10-p301-{local_id}"
    if mention_id in mids or mention_id in new_mention_ids:
        raise SystemExit(f"duplicate mention id: {mention_id}")
    if candidate_id not in all_candidate_ids:
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
    start = segment_offsets[line_no] + positions[occurrence]
    end = start + len(surface)
    if segment_text[start:end] != surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": NOTES_SEG, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })
    new_mention_ids.add(mention_id)


def add_statement(local_id, start_line, end_line, marker, predicate, claim, subject=None, obj=None,
                  mentioned=(), relation=False, speaker="Haskell, footnote",
                  text_layer="footnote narrative", qualification="", citations=(),
                  related_body_ids=(), extra=None):
    statement_id = f"st-chp10-p301-note{marker}-{local_id}"
    if statement_id in sids or statement_id in new_statement_ids:
        raise SystemExit(f"duplicate statement id: {statement_id}")
    qualifiers = {
        "source_line_start": start_line, "source_line_end": end_line,
        "printed_page": 301, "pdf_physical_page": 30,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification, "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
        "relation_candidate": relation, "footnote_marker": marker,
        "footnote_text_pending": False, "related_body_statement_ids": list(related_body_ids),
    }
    if citations:
        qualifiers["citations"] = list(citations)
        qualifiers["cited_material_not_independently_consulted"] = True
    if extra:
        qualifiers.update(extra)
    row = {
        "statement_id": statement_id, "segment_id": NOTES_SEG,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": "\n".join(source_lines[start_line - 1:end_line]),
        "origin": "book", "source_file": SOURCE_FILE,
    }
    new_statements.append(row)
    new_statement_ids.add(statement_id)
    return statement_id


# Note 1 quotes Grosley about Pasquali's press and Smith, with an internal link to p.299 note 4.
add_mention("n1-grosley", 589, "Grosley", REUSED["grosley"], "Indexed author; identity is not re-adjudicated here.")
add_mention("n1-venice", 589, "Venice", REUSED["venice"], "Haskell dates Grosley's visit to 1758.")
add_mention("n1-grosley-u-page", 589, "U, p. 99", C["grosley_u_p99"], "Short-form locator; possible local bibliography match only.")
add_mention("n1-pasquali-firm", 589, "LJImprimerie de JeanBaptiste Pasquali", REUSED["pasquali_firm"], "OCR artifact; the scan reads L’Imprimerie de Jean-Baptiste Pasquali. S0 unchanged.")
add_mention("n1-smith", 589, "M. Joseph Smith", REUSED["smith"], "Named in the quoted Grosley passage.")
add_mention("n1-consulate", 589, "Consulat d’Angleterre", C["consulate_venue"], "Entity type remains unresolved from the quoted wording.")

# Note 2 is Haskell's explicitly probabilistic inference, not a formal Smith-Visentini edge.
add_mention("n2-canaletto", 589, "Canaletto", REUSED["canaletto"], "The note says his case is discussed separately but gives no page.")
add_mention("n2-visentini", 589, "Visentini", REUSED["visentini"], "Artist named in Haskell's probable comparison.")

# Note 3 gives an unresolved surname-only bibliographic pointer.
add_mention("n3-previtali", 590, "Previtali", C["previtali_author"], "Local bibliography has two possible works; the note gives neither title nor page.")

# Note 4 locates three letters, reports Poleni's request, and quotes Smith's reply.
add_mention("n4-poleni-to-smith", 591, "Poleni", REUSED["poleni"], "First correspondent in the two dated letters.")
add_mention("n4-date-09-apr", 591, "dated 9", C["poleni_to_smith_1747_04_09"], "Date opening for the first Poleni-to-Smith letter.")
add_mention("n4-date-17-apr", 591, "17 April 1747", C["poleni_to_smith_1747_04_17"], "Date assigned to the second Poleni-to-Smith letter.")
add_mention("n4-smith-recipient", 591, "Smith", REUSED["smith"], "Recipient of both Poleni letters.")
add_mention("n4-marciana", 591, "Biblioteca Marciana", REUSED["marciana"], "Repository named by Haskell; not independently consulted.")
add_mention("n4-shelfmark", 591, "MSS. Ital:Cl.X. Cod CCLXXXVIII—6580", C["poleni_to_smith_1747_04_09"], "Shared codex locator as printed; no folio supplied.")
add_mention("n4-poleni-request", 591, "Polòni", REUSED["poleni"], "S0 OCR form; the scan reads Poleni. Source text remains unchanged.")
add_mention("n4-smith-request-recipient", 591, "Smith", REUSED["smith"], "Recipient of Poleni's request.", occurrence=1)
add_mention("n4-drawings", 591, "some drawings", C["poleni_visentini_drawings"], "Unidentified plural group; authorship and ownership are not stated.")
add_mention("n4-request-beneficiary", 591, "for him", REUSED["poleni"], "Pronoun refers to Poleni, the requester.")
add_mention("n4-visentini", 591, "Visentini", REUSED["visentini"], "Named as the person from whom Smith was asked to obtain the drawings; not necessarily their maker.")
add_mention("n4-reply-to-first", 591, "answer to the first of these letters", C["smith_to_poleni_1747_04_14"], "Identifies Smith's reply to the 9 April letter.")
add_mention("n4-reply-date", 591, "14 April 1747", C["smith_to_poleni_1747_04_14"], "Date of Smith's answer as cited by Haskell.")
add_mention("n4-smith-reply", 591, "Smith", REUSED["smith"], "Sender named in the reply.", occurrence=2)
add_mention("n4-quoted-phrase", 591, "l’antica mia servitù et perpetua stima", C["smith_to_poleni_1747_04_14"], "Short phrase transcribed by Haskell; manuscript not checked.")

# Note 5 is a cross-reference; page 211 is a printed-book page, not a manuscript folio.
add_mention("n5-cross-reference", 592, "p. 299, note 4", REUSED["gori_letters"], "Internal reference to the Smith-Gori manuscript locator.")
add_mention("n5-undated-letter", 592, "undated letter", REUSED["gori_letters"], "The note does not identify a separate manuscript item.")
add_mention("n5-page-211", 592, "page 211", REUSED["gori_letters"], "Page in the cited book's discussion; not an archival folio.")

# Note 6's printed 1757 conflicts with the local 1755 bibliography entry; preserve both.
add_mention("n6-smith", 593, "Smith", REUSED["smith"], "First party named in the publication claim.")
add_mention("n6-pasquali", 593, "Pasquali", REUSED["pasquali"], "Named jointly with Smith.")
add_mention("n6-newton", 593, "Newton", REUSED["newton"], "Named in the general publication claim.")
add_mention("n6-tempio", 593, "Tempio della Filosofia", C["tempio_1757"], "Title as printed in the footnote.")
add_mention("n6-year", 593, "1757", C["tempio_1757"], "Citation year; local bibliography entry instead gives 1755.")
add_mention("n6-page", 593, "page 30", C["tempio_1757"], "Cited page, not independently consulted.")
add_mention("n6-arrighi", 593, "Arrighi-Landini", REUSED["arrighi"], "Index candidate identifies Orazio Arrighi-Landini; identity remains an S3 question.")
add_mention("n6-smith-supplied", 593, "Smith", REUSED["smith"], "Person said to have supplied a copy.", occurrence=1)
add_mention("n6-pope", 593, "Pope", C["pope_surname"], "Surname only; do not expand or infer the epitaph's subject.")
add_mention("n6-epitaph", 593, "famous epitaph", C["pope_epitaph"], "Title and subject are not supplied.")

# Note 7 is matched to a local bibliography entry, but the article itself remains unread.
add_mention("n7-levey", 594, "Levey", REUSED["levey"], "The note gives surname only; bibliography match gives initial M.")
add_mention("n7-journal", 594, "Burlington Magazine", REUSED["burlington"], "Journal named in the citation.")
add_mention("n7-year", 594, "1959", C["levey_wilson_zuccarelli_article"], "Year matches the local bibliography entry.")
add_mention("n7-pages", 594, "pp. 139 and 143", C["levey_wilson_zuccarelli_article"], "Pages cited by Haskell within the bibliography range 139–143.")

add_statement(
    "grosley-quote", 589, 589, 1, "quoted_report_of_smith_funding_pasquali_press",
    "Haskell identifies Grosley as having been in Venice in 1758 and quotes him as saying that most of Jean-Baptiste Pasquali’s printing press operated on Joseph Smith’s funds; the quotation describes Smith as a wealthy Englishman who grew old in the English Consulate at Venice.",
    subject=REUSED["grosley"], obj=REUSED["pasquali_firm"],
    mentioned=[REUSED["grosley"], C["grosley_u_p99"], REUSED["venice"], REUSED["pasquali"], REUSED["pasquali_firm"], REUSED["smith"], C["consulate_venue"]],
    relation=True, speaker="Grosley as quoted by Haskell",
    text_layer="nested quotation and citation",
    qualification="The statement records what Haskell quotes, not an independently checked historical fact. The local Grosley bibliography entry is a possible match to “U,” not a resolved one.",
    citations=[{"source_candidate_id": C["grosley_u_p99"], "page": "99", "short_form": "U", "possible_local_match": "Nouveaux Mémoires ou observations sur l’Italie et sur les italiens", "bibliography_match": "possible; edition unresolved"}],
    related_body_ids=BODY_LINKS[1],
    extra={"internal_cross_reference": {"printed_page": 299, "footnote": 4, "target_statement_id": "st-chp10-p299-note4-gori-letters-citation"}},
)
add_statement(
    "canaletto-visentini-comparison", 589, 589, 2, "haskell_inferred_similar_smith_visentini_business_arrangement",
    "Haskell says Canaletto’s case is discussed separately and considers it likely that Smith had some similar arrangement with Visentini.",
    subject=REUSED["smith"], obj=REUSED["visentini"],
    mentioned=[REUSED["canaletto"], REUSED["smith"], REUSED["visentini"]],
    relation=True, text_layer="authorial inference",
    qualification="The wording is explicitly probabilistic (“seems likely”); the separate Canaletto discussion is not located by page here, and no contract or completed arrangement is cited.",
    related_body_ids=BODY_LINKS[2],
    extra={"internal_cross_reference": {"target": "Canaletto case discussed separately", "location": "not specified in note"}},
)
add_statement(
    "previtali-short-citation", 590, 590, 3, "footnote_citation",
    "P.301 note 3 directs the reader to Previtali without giving a title or page.",
    subject=C["previtali_author"], obj=C["previtali_short_citation"],
    mentioned=[C["previtali_author"], C["previtali_short_citation"]],
    text_layer="unresolved bibliographic pointer",
    qualification="The local bibliography lists two G. Previtali works (a 1959 article and a 1964 book); the note does not identify which one. Neither was consulted.",
    citations=[{"source_candidate_id": C["previtali_short_citation"], "possible_local_matches": [
        "G. Previtali, Collezionisti di primitivi nel Settecento (Paragone, 1959, 113, pp.3–32)",
        "G. Previtali, La Fortuna dei Primitivi dal Vasari ai Neoclassici (Torino, 1964)"
    ], "bibliography_match": "ambiguous"}],
    related_body_ids=BODY_LINKS[3],
)
add_statement(
    "poleni-letter-locators", 591, 591, 4, "cites_poleni_smith_letters_and_smith_reply",
    "Haskell cites two described-as-friendly letters from Poleni to Smith dated 9 and 17 April 1747, and an answer from Smith to the first letter dated 14 April 1747, all located in Biblioteca Marciana, MSS. Ital:Cl.X, Cod CCLXXXVIII-6580.",
    obj=C["poleni_to_smith_1747_04_09"],
    mentioned=[C["poleni_to_smith_1747_04_09"], C["poleni_to_smith_1747_04_17"], C["smith_to_poleni_1747_04_14"], REUSED["poleni"], REUSED["smith"], REUSED["marciana"]],
    text_layer="archival bibliographic pointer",
    qualification="Haskell calls the two Poleni letters “very friendly.” The manuscript has not been consulted; the cited codex locator supplies no folio numbers.",
    citations=[{"source_candidate_ids": [C["poleni_to_smith_1747_04_09"], C["poleni_to_smith_1747_04_17"], C["smith_to_poleni_1747_04_14"]], "repository_candidate_id": REUSED["marciana"], "shelfmark_as_printed": "MSS. Ital:Cl.X. Cod CCLXXXVIII—6580", "folio": "not supplied", "bibliography_match": "source locator"}],
    related_body_ids=BODY_LINKS[4],
)
add_statement(
    "poleni-requested-drawings", 591, 591, 4, "poleni_asked_smith_to_obtain_drawings_from_visentini",
    "Haskell says Poleni asked Smith in the two letters to obtain some drawings for him from Visentini.",
    subject=REUSED["poleni"], obj=C["poleni_visentini_drawings"],
    mentioned=[REUSED["poleni"], REUSED["smith"], C["poleni_visentini_drawings"], REUSED["visentini"], C["poleni_to_smith_1747_04_09"], C["poleni_to_smith_1747_04_17"]],
    relation=True, text_layer="authorial report of manuscript contents",
    qualification="This is a request reported by Haskell, not evidence that Smith fulfilled it. The drawings’ maker, owner and identities are not given.",
    citations=[{"source_candidate_ids": [C["poleni_to_smith_1747_04_09"], C["poleni_to_smith_1747_04_17"]], "repository_candidate_id": REUSED["marciana"], "bibliography_match": "source locator"}],
    related_body_ids=BODY_LINKS[4],
)
add_statement(
    "smith-replied-to-poleni", 591, 591, 4, "smith_answered_poleni_first_letter",
    "Haskell says Smith’s answer to Poleni’s first letter was dated 14 April 1747 and quotes Smith as referring to “l’antica mia servitù et perpetua stima”.",
    subject=REUSED["smith"], obj=C["smith_to_poleni_1747_04_14"],
    mentioned=[REUSED["smith"], REUSED["poleni"], C["poleni_to_smith_1747_04_09"], C["smith_to_poleni_1747_04_14"]],
    relation=True, speaker="Haskell reporting and quoting Smith",
    text_layer="authorial report of manuscript contents with nested quotation",
    qualification="The manuscript and full letter were not consulted; the quote and date are transcribed as Haskell presents them.",
    citations=[{"source_candidate_id": C["smith_to_poleni_1747_04_14"], "repository_candidate_id": REUSED["marciana"], "reply_to_candidate_id": C["poleni_to_smith_1747_04_09"], "quoted_phrase": "l’antica mia servitù et perpetua stima", "bibliography_match": "source locator"}],
    related_body_ids=BODY_LINKS[4],
)
add_statement(
    "smith-gori-undated-letter-cross-reference", 592, 592, 5, "internal_reference_to_undated_smith_gori_letter",
    "P.301 note 5 points back to p.299 note 4 and says the undated letter is on page 211.",
    subject=REUSED["smith"], obj=REUSED["gori_letters"],
    mentioned=[REUSED["smith"], REUSED["gori_letters"]],
    text_layer="internal cross-reference",
    qualification="Page 211 is a printed-book page, not an archival folio. This locator is linked to the p.301 Smith-to-Gori discussion but does not independently identify or verify the manuscript.",
    related_body_ids=BODY_LINKS[5],
    extra={"internal_cross_reference": {"printed_page": 299, "footnote": 4, "target_statement_id": "st-chp10-p299-note4-gori-letters-citation", "letter_page_in_book": 211}},
)
add_statement(
    "smith-pasquali-newton-books", 593, 593, 6, "smith_and_pasquali_published_books_referring_to_newton",
    "Haskell says Smith and Pasquali published many books referring to Newton.",
    subject=REUSED["smith"], obj=REUSED["pasquali"],
    mentioned=[REUSED["smith"], REUSED["pasquali"], REUSED["newton"]],
    relation=True, qualification="This is Haskell’s summary in a footnote; the books are not listed or independently checked.",
    related_body_ids=BODY_LINKS[6],
)
add_statement(
    "arrighi_pope_epitaph_report", 593, 593, 6, "smith_reportedly_supplied_arrighi_landini_a_copy_of_popes_epitaph",
    "Haskell says Arrighi-Landini’s note in the cited Tempio della Filosofia reports that Smith supplied him with a copy of Pope’s famous epitaph.",
    subject=REUSED["smith"], obj=REUSED["arrighi"],
    mentioned=[REUSED["smith"], REUSED["arrighi"], REUSED["arrighi_indexed_work"], C["tempio_1757"], C["pope_surname"], C["pope_epitaph"]],
    relation=True, speaker="Haskell citing Arrighi-Landini",
    text_layer="nested bibliographic report",
    qualification="Haskell cites 1757, while the local bibliography lists a title match dated 1755; edition identity is unresolved. The cited page was not read. The note gives no title or subject for the epitaph; it is not asserted here to concern Newton.",
    citations=[{"source_candidate_id": C["tempio_1757"], "page": "30", "cited_year": "1757", "indexed_title_candidate_id": REUSED["arrighi_indexed_work"], "local_bibliography_entry": "Arrighi-Landini, Orazio: Il-Tempio della Filosofia, Venezia 1755", "bibliography_match": "title/index possible; year conflicts"}],
    related_body_ids=BODY_LINKS[6],
)
add_statement(
    "levey-wilson-zuccarelli-citation", 594, 594, 7, "footnote_citation",
    "P.301 note 7 cites Levey, Burlington Magazine (1959), pages 139 and 143; the local bibliography identifies the article as “Wilson and Zuccarelli at Venice,” pages 139–143.",
    subject=REUSED["levey"], obj=C["levey_wilson_zuccarelli_article"],
    mentioned=[REUSED["levey"], REUSED["burlington"], C["levey_wilson_zuccarelli_article"]],
    text_layer="bibliographic pointer",
    qualification="The title, author initial, year and page range match the local bibliography. The article and cited pages were not independently consulted; identity alignment with the other Levey candidates remains for S3.",
    citations=[{"source_candidate_id": C["levey_wilson_zuccarelli_article"], "journal_candidate_id": REUSED["burlington"], "author_initial": "M.", "year": "1959", "pages_cited": ["139", "143"], "bibliography_pages": "139–143", "bibliography_match": "local exact title/year/pages"}],
    related_body_ids=BODY_LINKS[7],
)

for marker, ids in BODY_LINKS.items():
    for sid in ids:
        by_statement[sid]["qualifiers"]["footnote_text_pending"] = False

for row in new_statements:
    q = row["qualifiers"]
    if q["source_line_start"] < 589 or q["source_line_end"] > 594:
        raise SystemExit(f"statement range outside p.301 notes: {row['statement_id']}")
    for endpoint in (row["subject_candidate_id"], row["object_candidate_id"]):
        if endpoint is not None and endpoint not in all_candidate_ids:
            raise SystemExit(f"statement foreign key missing: {row['statement_id']} -> {endpoint}")
    if not all(cid in all_candidate_ids for cid in q["mentioned_candidate_ids"]):
        raise SystemExit(f"mentioned candidate missing: {row['statement_id']}")
    if not all(sid in sids for sid in q["related_body_statement_ids"]):
        raise SystemExit(f"related body statement missing: {row['statement_id']}")
spans = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"]) for row in new_mentions)
for left, right in zip(spans, spans[1:]):
    if right[0] < left[1]:
        raise SystemExit(f"overlapping mentions: {left[2]} / {right[2]}")

cov[NOTES_SEG].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L492-594",
    "note": "Merged notes processed through p.301 notes 1–7 at L589–594; p.301 notes 1 and 2 share OCR line L589. P.300 notes 1–7 and their L379/L380 continuations remain recorded above. P.301 note 1 quotes Grosley and has only a possible local bibliography match; note 2 is Haskell’s probabilistic Smith–Visentini comparison; note 3 is an unresolved Previtali pointer; note 4 describes three Poleni–Smith letters and a request for unidentified drawings; printed note 5 at OCR L592 cross-refers to the p.299 Smith–Gori locator and printed p.211; note 6 cites Tempio as 1757 although the local bibliography gives 1755; note 7 matches Levey’s 1959 Burlington Magazine article by title/pages. None of the cited manuscripts or publications were independently consulted. Physical p.301 shows note 5 where canonical OCR L592 reads 6, and reads 'of Canaletto' at L589 where OCR has 'os'; S0 unchanged. Next source range: p.302 note 1 at L595."
})
cov[P301_BODY].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L383-389",
    "note": "Printed p.301 body checked against CHP-10.pdf physical page 30; notes 1–7 are now linked to their corresponding body statements. The p.301 sentence ending in 'Lady' closes with Mary Wortley Montagu at p.302, already reviewed and cross-linked. Scan-only OCR correction: p.301 note 5 is printed as 5, not the OCR 6 at L593; S0 unchanged."
})

summary = {
    "mode": "APPLY" if args.apply else "DRY-RUN",
    "source_sha256": ASSET_SHA, "notes_segment_sha256": NOTES_SEG_SHA, "p301_notes_sha256": P301_NOTES_SHA,
    "new_candidates": len(new_candidates), "candidate_ids": [row["candidate_id"] for row in new_candidates],
    "new_mentions": len(new_mentions), "new_statements": len(new_statements),
    "statements": [{"id": row["statement_id"], "lines": [row["qualifiers"]["source_line_start"], row["qualifiers"]["source_line_end"]], "predicate": row["predicate"], "relation_candidate": row["qualifiers"]["relation_candidate"]} for row in new_statements],
    "resolved_body_markers": list(BODY_LINKS),
    "coverage": {NOTES_SEG: cov[NOTES_SEG]["source_line_ranges"], P301_BODY: cov[P301_BODY]["migration_status"]},
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
    print("Applied p.301 notes 1-7; next source range is p.302 note 1 at L595.")
