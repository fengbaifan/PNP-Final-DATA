"""Controlled S2 migration for printed pp.299-301; dry-run unless --apply."""
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
P299 = "chp-10:10_CHP-10_intro:l354-366"
P300 = "chp-10:10_CHP-10_intro:l368-380"
P301 = "chp-10:10_CHP-10_intro:l382-389"
P302 = "chp-10:10_CHP-10_intro:l391-400"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_SEGMENT_SHA = {
    P299: "052f44412749144ce984c01086091fe86db19f44be97dda9455894ac4620406b",
    P300: "a58eea87703095acaf4a07377eb5d7100bd76a790c0f082e230997e995d686a6",
    P301: "81d50c04e66752729a137c595c19a54e93fa8ac153a2b324f8e1ac515a108784",
}
BACKUP = ".bak-s2-chp10-p299-p301-20261002"


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
src = SOURCE.read_text(encoding="utf-8-sig").splitlines()
SEGMENT_LINES = {P299: (354, 366, 299, 28), P300: (368, 380, 300, 29), P301: (382, 389, 301, 30)}
bodies, offsets = {}, {}
for seg, (first, last, _page, _physical) in SEGMENT_LINES.items():
    body = "\n".join(src[first - 1:last])
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    if digest != EXPECTED_SEGMENT_SHA[seg]:
        raise SystemExit(f"source segment changed: {seg}: {digest}")
    bodies[seg] = body
    line_offsets, offset = {}, 0
    for line_no in range(first, last + 1):
        line_offsets[line_no] = offset
        offset += len(src[line_no - 1]) + 1
    offsets[seg] = line_offsets

cp, mp, sp, vp = [TABLES / name for name in ("entity-candidates.csv", "mentions.csv", "book-statements.jsonl", "s2-coverage.csv")]
cf, candidates = read_csv(cp)
mf, mentions = read_csv(mp)
vf, coverage = read_csv(vp)
statements = read_jsonl(sp)
cids = {row["candidate_id"] for row in candidates}
mids = {row["mention_id"] for row in mentions}
sids = {row["statement_id"] for row in statements}
cov = {row["segment_id"]: row for row in coverage}
maximum = max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates)
if maximum != 9165:
    raise SystemExit(f"candidate sequence changed: {maximum}")
expected_states = {
    "chp-10:10_CHP-10_intro:l345-352": ("reviewed", "complete"),
    P299: ("queued", "pending"), P300: ("queued", "pending"),
    P301: ("queued", "pending"), P302: ("queued", "pending"), NOTES: ("queued", "pending"),
}
for seg, expected in expected_states.items():
    row = cov.get(seg)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {seg}: {row}")
if any(row["segment_id"] in {P299, P300, P301} for row in mentions):
    raise SystemExit("target segments already have mention rows")
if any(row["segment_id"] in {P299, P300, P301} for row in statements):
    raise SystemExit("target segments already have statements")

# These are distinct page-indexed candidates reused as the S2 anchors; global identity is deferred to S3.
E = {
    "smith": "cand-2440", "venice": "cand-3401", "amsterdam": "cand-6617",
    "venetian_nobility": "cand-8108", "pasquali": "cand-1844", "gori": "cand-1214",
    "guicciardini_histories": "cand-1276", "museum_etruscum": "cand-1215",
    "ferretti": "cand-1026", "florence": "cand-3397", "george_iii": "cand-1141",
    "lodoli": "cand-1411", "memmo": "cand-1642", "wynne": "cand-2824",
    "resident_1761": "cand-8287", "zeno": "cand-2869", "algarotti": "cand-0041",
    "zanetti": "cand-2838", "goldoni": "cand-1207", "padua": "cand-1803",
    "facciolati": "cand-0986", "mead": "cand-1604", "newton": "cand-1739",
    "breval": "cand-0451", "walpole": "cand-2798", "wilson": "cand-2815",
    "reynolds": "cand-2135", "wyatt": "cand-2823", "adam": "cand-0012",
    "grand_canal": "cand-8178", "republic": "cand-8838",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")

NEW_SPECS = [
    ("westminster", "Westminster School", "institution", "School at which Joseph Smith was educated, as stated by Haskell; no independent verification is implied.", 361),
    ("salumieri", "Arte de’ Salumieri (guild involved in disputes with Joseph Smith)", "institution", "Guild involved in disputes over Smith’s import activity; keep the guild distinct from the food trade and from the cited archive record.", 362),
    ("english_diplomats", "English diplomats meeting Venetian nobles at Joseph Smith’s residence", "term", "Collective diplomatic role named in Haskell’s account; individuals are not identified in this passage.", 362),
    ("foreign_representatives", "Foreign diplomatic representatives in Venice (unnamed group)", "term", "Collective group in Haskell’s explanation of government limits on contacts with the nobility; not restricted to English diplomats.", 376),
    ("palace_visitors", "Unnamed nobles and intellectuals meeting at Joseph Smith’s Venetian palace", "term", "Collective visitors described as more adventurously inclined; no individual participants are named here.", 372),
    ("smith_residence", "Joseph Smith’s unnamed Venetian house or palace", "place", "Residence used for meetings and later described as a palace near the Church of the Apostoli; whether both descriptions denote the same building remains unresolved.", 362),
    ("pasquali_firm", "G. B. Pasquali’s Venetian publishing firm", "institution", "Publishing venture launched by Smith for the young printer Pasquali in the early 1730s; its formal business name is not supplied.", 362),
    ("british_consul_office", "British Consul post at Venice", "term", "Diplomatic office held by Joseph Smith from 1744; the source distinguishes it from the higher-status Residency he had hoped for.", 365),
    ("british_residency", "British Residency at Venice (post sought by Joseph Smith)", "term", "Higher-status diplomatic post for which Smith had hoped; not conflated with his consular appointment.", 365),
    ("apostoli_church", "Church of the Apostoli in Venice", "place", "Church used as a location reference for Smith’s palace on the Grand Canal; exact dedication and building identity await global reconciliation.", 372),
    ("protestant_cemetery", "Protestant cemetery at S. Niccolò al Lido, Venice", "place", "Burial place named for Joseph Smith; scan reads S. Niccolò al Lido, while OCR omits the accent.", 369),
    ("smith_library", "Joseph Smith’s library sold in part to George III in 1762", "", "The bulk of Smith’s library was included in the 1762 sale; individual books and the collection’s knowledge-unit type are unresolved.", 369),
    ("smith_picture_holdings", "Joseph Smith’s picture holdings sold mostly to George III in 1762", "", "Most of Smith’s pictures were included in the 1762 sale; the passage does not identify individual works or settle collection typing.", 369),
    ("facciolati_collection", "Abate Facciolati’s picture collection and private museum in Padua", "", "Collection described as illustrating the history and progress of art, beginning with Byzantine paintings; collection versus institution/place typing remains open.", 386),
    ("facciolati_byzantine_series", "Unidentified Byzantine paintings in Facciolati’s art-history collection", "", "A series within the collection; no individual paintings or coherent authored group are identified in the passage.", 386),
    ("lodoli_collection", "Carlo Lodoli’s unidentified art collection", "", "Haskell says Lodoli collected art on a principle similar to Facciolati’s; individual objects, dates and collection identity are not supplied.", 387),
    ("poleni", "Giovanni Poleni", "person", "Italian friend of Joseph Smith, described as a University professor, engineer and architect; full identity alignment is deferred to S3.", 387),
    ("padua_university", "University of Padua", "institution", "University at which Facciolati and Giovanni Poleni are described as professors.", 385),
    ("filosofo_inglese", "Il Filosofo Inglese (Goldoni play dedicated to Joseph Smith)", "archive", "Literary work named in the passage and footnote; preserved as a distinct candidate from Goldoni as author and from the dedication event.", 383),
    ("british_resident_report", "Unidentified British Resident cited in the account of Smith’s post-1744 position", "person", "Unnamed Resident whose report is invoked to compare Smith’s position with that of a more senior colleague; do not merge with other unidentified Residents without source-level evidence.", 376),
]
newc, C = [], {}
for i, (key, name, kind, detail, line) in enumerate(NEW_SPECS, maximum + 1):
    cid = f"cand-{i:04d}"
    if cid in cids:
        raise SystemExit(f"candidate id already exists: {cid}")
    C[key] = cid
    newc.append({"candidate_id": cid, "index_entry_id": "", "canonical_name": name,
                 "index_page_range": "", "suggested_type": kind, "status": "open",
                 "index_source_file": "", "sub_entry": "", "detail": detail,
                 "exclude_reason": "", "candidate_origin": "body-mention",
                 "candidate_source_ref": f"{P299 if line <= 365 else P300 if line <= 378 else P301}#L{line}"})

newm = []


def add_m(local, seg, line, surface, cid, note="", end_line=None, occurrence=0):
    mid = f"m-chp10-{local}"
    if mid in mids or any(row["mention_id"] == mid for row in newm):
        raise SystemExit(f"duplicate mention: {mid}")
    if cid not in cids | {row["candidate_id"] for row in newc}:
        raise SystemExit(f"missing candidate for {mid}: {cid}")
    end_line = end_line or line
    line_start, line_end = offsets[seg][line], offsets[seg][end_line] + len(src[end_line - 1])
    positions, at = [], line_start
    while True:
        at = bodies[seg].find(surface, at)
        if at < 0 or at + len(surface) > line_end:
            break
        positions.append(at)
        at += max(1, len(surface))
    if occurrence >= len(positions):
        raise SystemExit(f"surface absent in {seg} L{line}-{end_line}: {surface!r}; occurrences={len(positions)}")
    start = positions[occurrence]
    end = start + len(surface)
    if bodies[seg][start:end] != surface:
        raise SystemExit(f"span mismatch: {mid}")
    newm.append({"mention_id": mid, "segment_id": seg, "candidate_id": cid,
                 "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


# p.299 body, chapter/section opening and Joseph Smith account.
M = [
    ("p299-heading-foreign-residents",P299,356,"THE FOREIGN RESIDENTS","cand-9165","Chapter heading; collective category, not an individual identity."),
    ("p299-heading-smith",P299,358,"JOSEPH SMITH",E["smith"],"Section heading names the subject."),
    ("p299-smith",P299,360,"Joseph Smith",E["smith"],"Named Englishman and art patron; the initial-capital T at L360 duplicates the printed drop cap at L359."),
    ("p299-venice-link",P299,359,"Venice itself",E["venice"],"Place in Haskell’s opening characterization of Smith as a link between the city and the outside world."),
    ("p299-westminster",P299,361,"Westminster School",C["westminster"],"Education named by Haskell."),
    ("p299-venice",P299,361,"Venice",E["venice"],"City where Smith settled."),
    ("p299-amsterdam",P299,361,"Amsterdam",E["amsterdam"],"Trading partner city."),
    ("p299-traded-coreference",P299,361,"He traded",E["smith"],"Corefers to Joseph Smith as merchant."),
    ("p299-salumieri",P299,361,"the\nSalumieri",C["salumieri"],"Guild name broken across OCR lines; footnote 2 gives an archival dispute account, reserved for the consolidated notes segment.",362),
    ("p299-smith-venetian-residence",P299,362,"his house",C["smith_residence"],"Smith’s unnamed residence; do not assume its identity with the later palace without evidence."),
    ("p299-venetian-nobility",P299,362,"Venetian nobility",E["venetian_nobility"],"Collective social estate."),
    ("p299-english-diplomats",P299,362,"English diplomats",C["english_diplomats"],"Unnamed collective; no individual diplomat inferred."),
    ("p299-pasquali",P299,362,"G. B.\nPasquali",E["pasquali"],"Printer’s name crosses the OCR line break; reuse the page-indexed Pasquali candidate." ,363),
    ("p299-pasquali-firm",P299,362,"the firm",C["pasquali_firm"],"Smith launched the firm for Pasquali; formal firm name is absent."),
    ("p299-smith-began-publishing",P299,362,"he began",E["smith"],"Corefers to Smith as the subject of the early-1730s publishing activity."),
    ("p299-smith-concern",P299,363,"Smith’s concern",E["smith"],"Named coreference to Joseph Smith in the publishing account."),
    ("p299-gori",P299,363,"A. F. Gori",E["gori"],"Florentine scholar; indexed page candidate reused."),
    ("p299-guicciardini",P299,364,"Guicciardini’s Histories",E["guicciardini_histories"],"Work subentry from the index; authorship/work identity retained for S3 resolution."),
    ("p299-museum-etruscum",P299,364,"Museum Etruscum",E["museum_etruscum"],"Work title indexed under Gori; kept distinct from the person candidate."),
    ("p299-ferretti",P299,364,"Gian\nDomenico Ferretti",E["ferretti"],"Painter’s full name crosses a line break; scan confirms Gian Domenico Ferretti.",365),
    ("p299-florence",P299,365,"Florence",E["florence"],"Place associated with Ferretti in Haskell’s wording."),
    ("p299-smith-production",P299,365,"Smith exerted himself",E["smith"],"Named coreference to Smith in the publication-production account."),
    ("p299-british-consul",P299,365,"British Consul",C["british_consul_office"],"Office title; distinct from the Residency mentioned at the page turn."),
    ("p299-smith-client-pictures",P299,365,"his clients",E["smith"],"Possessive coreference to Smith; footnote marker 4 links to the Gori letters in the consolidated notes segment."),
    # p.300 body, including the continuation of the p.299 sentence.
    ("p300-residency",P300,369,"the Residency",C["british_residency"],"Continuation of the p.299 sentence; higher-status post Smith had hoped to obtain."),
    ("p300-smith-sold",P300,369,"he sold",E["smith"],"Corefers to Joseph Smith as seller in the 1762 transaction."),
    ("p300-smith-library",P300,369,"his library",C["smith_library"],"Smith’s library; individual books and collection type remain unresolved."),
    ("p300-smith-pictures",P300,369,"his pictures",C["smith_picture_holdings"],"Smith’s picture holdings; individual works are not identified here."),
    ("p300-george-iii",P300,369,"King George III",E["george_iii"],"Buyer named by Haskell."),
    ("p300-consul-resumption",P300,369,"the post of consul",C["british_consul_office"],"Smith’s temporary return to the consular office; footnote 1 source is pending in the consolidated notes segment."),
    ("p300-smith",P300,369,"He finally died",E["smith"],"Pronoun corefers to Joseph Smith."),
    ("p300-protestant-cemetery",P300,369,"Protestant cemetery at S. Niccolo al Lido",C["protestant_cemetery"],"Burial place; scan reads S. Niccolò al Lido."),
    ("p300-venetian-background",P300,369,"Venetian",E["venice"],"One of the two backgrounds named in the passage."),
    ("p300-smith-taste",P300,369,"His taste",E["smith"],"Corefers to Smith in the description of his picture taste."),
    ("p300-smith-patron-coreference",P300,370,"he was well known",E["smith"],"Corefers to Joseph Smith as patron and library owner."),
    ("p300-superb-library",P300,370,"superb library",C["smith_library"],"Smith’s library, described by Haskell as superb."),
    ("p300-residence-palace",P300,371,"his palace",C["smith_residence"],"Later palace description; whether identical to the meeting house at p.299 remains unresolved."),
    ("p300-grand-canal",P300,372,"Grand Canal",E["grand_canal"],"Venice location."),
    ("p300-apostoli",P300,372,"church of the Apostoli",C["apostoli_church"],"Venetian church used as a location reference; not the Roman SS. Apostoli."),
    ("p300-palace-visitors",P300,372,"nobles and intellectuals",C["palace_visitors"],"Unnamed collective meeting at Smith’s palace; not treated as a single organized institution."),
    ("p300-lodoli",P300,373,"Padre Lodoli",E["lodoli"],"Index candidate reused; described as sarcastic and anti-conformist by Haskell."),
    ("p300-memmo",P300,373,"Andrea Memmo",E["memmo"],"Patrician pupil of Lodoli."),
    ("p300-giustiniana",P300,373,"Giustiniana Wynne",E["wynne"],"Named woman courted by Lodoli and Memmo; identity remains subject to S3 reconciliation."),
    ("p300-memmo-age",P300,374,"Memmo",E["memmo"],"Corefers to Andrea Memmo."),
    ("p300-smith-consul",P300,374,"English\nConsul",E["smith"],"Corefers to Joseph Smith; the phrase crosses the source line break.",375),
    ("p300-giustiniana-again",P300,375,"Giustiniana",E["wynne"],"Corefers to Giustiniana Wynne."),
    ("p300-foreign-representatives",P300,376,"foreign representatives",C["foreign_representatives"],"General diplomatic group; kept distinct from the specifically English diplomats at p.299."),
    ("p300-british-resident",P300,376,"the Resident himself",C["british_resident_report"],"Unidentified source speaker; do not merge with the separately indexed 1761 Resident without source-level identity evidence."),
    ("p300-smith-influence-coreference",P300,376,"Smith’s activities",E["smith"],"Names the subject of the possible post-1744 change in influence."),
    ("p300-smith-appointment-claim",P300,376,"Smith in his claim",E["smith"],"Named subject of the appointment claim reported by Haskell."),
    ("p300-government",P300,377,"the Government",E["republic"],"Government of Venice in context; institutional referent retained separately from the city."),
    ("p300-zeno",P300,377,"Apostolo Zeno",E["zeno"],"Connoisseur and Smith’s friendly contact in the passage."),
    ("p300-algarotti",P300,377,"Francesco Algarotti",E["algarotti"],"Use the index candidate covering p.300; cross-index identity remains for S3."),
    ("p300-zanetti",P300,378,"Antonio Maria Zanetti",E["zanetti"],"The Elder candidate from the p.300 index context is reused."),
    ("p300-smith-connoisseur-coreference",P300,377,"he had had friendly relations",E["smith"],"Corefers to Smith in the account of connoisseur contacts."),
    ("p300-goldoni",P300,378,"Goldoni",E["goldoni"],"Carlo Goldoni; index subentry covers the dedication to Smith."),
    ("p300-play",P300,378,"one of his plays",C["filosofo_inglese"],"Footnote 2 identifies Il Filosofo Inglese; the body title is resolved by the note, not inferred from this phrase alone."),
    # p.301 body closes p.300 and opens the next page continuation.
    ("p301-play-title",P301,383,"II Filosofo Inglese",C["filosofo_inglese"],"S0 reads II; scan confirms the italic title Il Filosofo Inglese. Footnote 2 on p.300 identifies its dedication to Smith."),
    ("p301-englishman",P301,383,"the Englishman",E["smith"],"Corefers to Joseph Smith."),
    ("p301-will",P301,383,"his will",E["smith"],"Smith’s will, drawn up in 1761; the underlying document is not independently read here."),
    ("p301-smith",P301,383,"Smith had few close contacts",E["smith"],"Named coreference to Joseph Smith in the 1761-will account."),
    ("p301-pasquali",P301,383,"his client Pasquali",E["pasquali"],"Joseph Smith’s client and printer; footnote 1 gives supporting published correspondence references."),
    ("p301-smith-artist-arrangements",P301,383,"he had certain definite business arrangements",E["smith"],"Corefers to Smith in Haskell’s explicitly qualified inference."),
    ("p301-smith-friends",P301,384,"his most interesting Italian friends",E["smith"],"Possessive coreference to Smith."),
    ("p301-friends-padua",P301,384,"Padua",E["padua"],"Place where Smith’s two Italian friends lived."),
    ("p301-facciolati",P301,385,"Abate Facciolati",E["facciolati"],"Italian friend and professor of history."),
    ("p301-university",P301,385,"the University",C["padua_university"],"University of Padua in context."),
    ("p301-facciolati-collection",P301,386,"collection of pictures",C["facciolati_collection"],"Collection described as an art-historical teaching/display resource; object type remains open."),
    ("p301-byzantine-paintings",P301,386,"Byzantine paintings",C["facciolati_byzantine_series"],"Beginning of the collection’s sequence; no individual paintings are identified."),
    ("p301-lodoli",P301,387,"Padre LodoE",E["lodoli"],"OCR form; scan reads Padre Lodoli. No source edit made."),
    ("p301-lodoli-collection",P301,387,"collected works of art",C["lodoli_collection"],"Haskell describes Lodoli’s own collection, not Facciolati’s."),
    ("p301-poleni",P301,387,"Giovanni Poleni",C["poleni"],"New open person candidate; identity and authority alignment deferred to S3."),
    ("p301-smith-poleni",P301,387,"Smith’s other acquaintance",E["smith"],"Named coreference to Smith in the Poleni sentence."),
    ("p301-university-second",P301,387,"the University",C["padua_university"],"University of Padua; second occurrence."),
    ("p301-smith-scholarly-context",P301,387,"Smith was most at home",E["smith"],"Named coreference in Haskell’s interpretation of Smith’s social setting."),
    ("p301-gori",P301,389,"Gori",E["gori"],"A. F. Gori by the preceding context; footnote 5 evidence is pending."),
    ("p301-mead",P301,389,"‘celeberrimo S.r Dottor Mead’",E["mead"],"Dr Richard Mead as named in Smith’s letter to Gori; quotation remains Haskell’s transcription."),
    ("p301-smith-writing",P301,389,"him writing",E["smith"],"Corefers to Smith as the author of the letter."),
    ("p301-newton",P301,389,"Sir Isaac Newton",E["newton"],"Friend of Mead, named in the authorial narrative."),
    ("p301-breval",P301,389,"John Breval",E["breval"],"One of the English visitors welcomed by Smith; footnote 7 remains pending."),
    ("p301-walpole",P301,389,"Horace Walpole",E["walpole"],"One of the English visitors; the sentence continues after this page."),
    ("p301-wilson",P301,389,"Richard Wilson",E["wilson"],"One of the English visitors."),
    ("p301-reynolds",P301,389,"Sir Joshua Reynolds",E["reynolds"],"The scan breaks the printed name at a line-end hyphen; the S0 transcription has the unhyphenated name."),
    ("p301-wyatt",P301,389,"James Wyatt",E["wyatt"],"One of the English visitors."),
    ("p301-adam",P301,389,"Robert Adam",E["adam"],"One of the English visitors."),
    ("p301-smith-visitors",P301,389,"he treated with great courtesy",E["smith"],"Corefers to Smith as host of English visitors."),
    ("p301-merchant-of-venice",P301,389,"the Merchant of Venice",E["smith"],"Walpole’s jeering label for Joseph Smith, not a formal title or a reference to Shakespeare’s play."),
]
for row in M:
    add_m(*row)

new_s = []


def add_s(local, seg, lo, hi, subject, obj, predicate, claim, qualification,
          relation=False, footnote=None, cross=None, layer="authorial narrative"):
    sid = f"st-chp10-{local}"
    if sid in sids or any(row["statement_id"] == sid for row in new_s):
        raise SystemExit(f"duplicate statement: {sid}")
    page = SEGMENT_LINES[seg][2]
    physical = SEGMENT_LINES[seg][3]
    # Use the source line of each anchored mention to construct an accurate mention set.
    mentioned = []
    for mention in newm:
        if mention["segment_id"] != seg:
            continue
        start = int(mention["start_char"])
        line_no = max((n for n, offset in offsets[seg].items() if offset <= start), default=SEGMENT_LINES[seg][0])
        if lo <= line_no <= hi and mention["candidate_id"] not in mentioned:
            mentioned.append(mention["candidate_id"])
    qualifiers = {"source_line_start": lo, "source_line_end": hi,
                  "printed_page": page, "pdf_physical_page": physical,
                  "claim": claim, "speaker": "Haskell", "text_layer": layer,
                  "qualification": qualification, "mentioned_candidate_ids": mentioned,
                  "relation_candidate": relation}
    if footnote is not None:
        qualifiers["footnote_marker"] = footnote
        qualifiers["footnote_text_pending"] = True
        qualifiers["cross_reference_segments"] = [NOTES]
    if cross:
        qualifiers["cross_reference_segments"] = list(dict.fromkeys(qualifiers.get("cross_reference_segments", []) + cross))
        qualifiers["cross_reference_printed_pages"] = [302 if P302 in cross else 301 if P301 in cross else 300 if P300 in cross else 299]
    quote = "\n".join(src[lo - 1:hi])
    new_s.append({"statement_id": sid, "segment_id": seg,
                  "subject_candidate_id": subject, "object_candidate_id": obj,
                  "predicate": predicate, "qualifiers": qualifiers,
                  "original_quote": quote, "source_file": SOURCE_FILE, "origin": "book"})


# p.299: biography, trade, diplomacy and Pasquali/Gori publishing work.
add_s("p299-smith-importance",P299,359,360,E["smith"],E["venice"],"described_as_link_between_venice_and_outside_world_and_major_art_patron",
      "Haskell introduces Joseph Smith as the most important link between Venice and the outside world and calls him the greatest art patron of his day.",
      "Both superlatives are Haskell’s evaluative framing, not independently measured rankings.",layer="authorial interpretation")
add_s("p299-smith-life-and-education",P299,360,361,E["smith"],None,"birth_education_migration_and_occupation",
      "Haskell says Joseph Smith was English, born about 1675, educated at Westminster School, and settled in Venice in the early eighteenth century as a businessman and merchant.",
      "The birth year is approximate; the passage is Haskell’s account and does not independently document the school record or arrival date.",footnote=1)
add_s("p299-smith-trade-and-guild-dispute",P299,361,362,E["smith"],C["salumieri"],"trade_and_guild_dispute",
      "Smith traded extensively with Amsterdam and imported meat and fish, an activity that sometimes brought him into disputes with the Arte de’ Salumieri.",
      "The source does not enumerate the disputes; footnote 2 cites archival papers and an account of a dispute, which remain to be read in the consolidated notes stage.",relation=True,footnote=2)
add_s("p299-residence-diplomatic-meetings",P299,362,362,C["smith_residence"],C["english_diplomats"],"residence_used_for_meetings_between_venetian_nobles_and_english_diplomats",
      "Smith’s house was occasionally used for meetings between Venetian nobles and English diplomats; Haskell says public meetings would have been awkward.",
      "The participants are unnamed, and the house’s identity relative to the palace described on p.300 is unresolved.",relation=True,footnote=3)
add_s("p299-pasquali-firm-launched",P299,362,363,E["smith"],C["pasquali_firm"],"launched_publishing_firm_for_g_b_pasquali",
      "In the early 1730s Smith launched a publishing firm for the young G. B. Pasquali and took an intellectual interest in the venture beyond its finances.",
      "The firm’s formal name and precise legal structure are not supplied; the phrase ‘young man’ is Haskell’s description.",relation=True)
add_s("p299-smith-intellectual-work",P299,363,363,E["smith"],E["pasquali"],"participated_in_intellectual_work_of_publishing_venture",
      "For the venture’s first few years Smith was actively engaged in its intellectual work.",
      "This is Haskell’s summary; the next sentence gives a 1735 example.",relation=True)
add_s("p299-gori-guicciardini-and-museum",P299,363,364,E["smith"],E["gori"],"sought_gori_help_for_guicciardini_reprint_and_promised_english_subscribers_for_museum_etruscum",
      "In 1735 Smith tried to enlist A. F. Gori’s help in reprinting Guicciardini’s Histories and promised English subscribers for Gori’s Museum Etruscum.",
      "The work titles are index candidates pending S3; the promise is reported by Haskell and is not independently verified here.",relation=True,footnote=4)
add_s("p299-publication-obstacles",P299,364,365,E["smith"],E["ferretti"],"publication_obstacles_and_frontispiece_engraving",
      "The reprint required unpublished material from Guicciardini’s family, a frontispiece drawn by Gian Domenico Ferretti of Florence to be engraved, and an as-yet-unspecified dedicatee.",
      "The family and dedicatee are unnamed; ‘famous painter’ is Haskell’s quoted characterization, not an independently assessed status.",relation=True,footnote=4)
add_s("p299-smith-books-gems-pictures",P299,365,365,E["smith"],None,"continued_personal_and_client_purchases",
      "Smith exerted himself in the production and continued buying books, gems and pictures for himself and his clients.",
      "Individual objects and clients are not identified in this passage; footnote 4’s letters are pending in the consolidated notes segment.",footnote=4)
add_s("p299-smith-consul-appointment",P299,365,365,E["smith"],C["british_consul_office"],"appointed_british_consul_in_1744",
      "In 1744 Smith was made British Consul, a post Haskell says was inferior in status to the Residency for which he had hoped.",
      "The sentence continues at p.300; the continuation is linked rather than duplicated, and the comparison remains Haskell’s account.",relation=True,cross=[P300])

# p.300: transfer to George III, Venetian social networks, and post-1744 influence.
add_s("p300-smith-residency-and-sale",P300,369,369,E["smith"],E["george_iii"],"sold_bulk_of_library_and_pictures_to_george_iii_in_1762",
      "A year after resigning the consulship, Smith sold the bulk of his library and most of his pictures to King George III in 1762.",
      "The passage does not list individual objects; the sale is reported by Haskell and does not by itself establish the present identity or custody of every item.",relation=True)
add_s("p300-consul-resumption-and-death",P300,369,369,E["smith"],C["british_consul_office"],"temporarily_resumed_consulship_after_successor_bankruptcy_and_died_in_1770",
      "Five years after the 1762 sale, Smith temporarily resumed the consul’s post when his successor went bankrupt; he died in 1770 and was buried at the Protestant cemetery on S. Niccolò al Lido.",
      "The source says he was nearly 90, not exactly 90; footnote 1’s state-paper references remain pending.",relation=True,footnote=1)
add_s("p300-smith-taste-backgrounds",P300,369,370,E["smith"],E["venice"],"picture_taste_reflected_english_and_venetian_backgrounds",
      "Haskell says Smith’s taste in pictures reflected his English and Venetian backgrounds.",
      "This is Haskell’s interpretive characterization, not a measured or independently verified account.",layer="authorial interpretation")
add_s("p300-smith-patron-and-painters",P300,370,371,E["smith"],None,"patron_library_owner_and_contact_with_painters",
      "As an arts patron and owner of a library, Smith was well known in Venice and in close contact with leading painters; he also regularly attended theatre and opera.",
      "The passage names no painter in this sentence; footnote 2’s source and collection details remain pending.",footnote=2)
add_s("p300-palace-meeting-place-and-publishing",P300,371,372,C["smith_residence"],C["palace_visitors"],"palace_meeting_place_for_nobles_and_intellectuals_and_site_of_controversial_publishing",
      "Smith’s palace near the Church of the Apostoli on the Grand Canal served as a meeting place for adventurous nobles and intellectuals; his scholarly interests and publishing made books appear controversial or subversive in Haskell’s description of Venice.",
      "The palace is not identified by name; Haskell’s evaluative terms ‘hidebound’, ‘controversial’ and ‘subversive’ are retained as authorial framing.",relation=True,footnote=3)
add_s("p300-lodoli-memmo-and-smith-meetings",P300,373,373,E["lodoli"],E["memmo"],"lodoli_and_memmo_visited_smith_palace_and_memmo_acknowledged_influence",
      "Padre Lodoli visited Smith’s palace with his pupil Andrea Memmo; both later played roles in Venice’s art world, and Memmo acknowledged that the meetings influenced his taste.",
      "‘Sarcastic’ and ‘anti-conformist’ are Haskell’s descriptions; the reported acknowledgment and its source remain pending in footnote 4.",relation=True,footnote=4)
add_s("p300-lodoli-memmo-wynne-rivalry",P300,373,375,E["lodoli"],E["wynne"],"rivalry_in_courtship_of_giustiniana_wynne",
      "Haskell says Lodoli and Memmo’s friendship did not survive their rivalry in courting Giustiniana Wynne, whom he describes as the illegitimate daughter of an English gentleman and a Greek adventuress; Memmo was about 54 years younger than Smith, and Giustiniana later linked patrons and writers.",
      "The parents remain unnamed; the age difference and characterization are Haskell’s, and footnote 5 remains pending.",relation=True,footnote=5)
add_s("p300-smith-influence-after-1744",P300,376,376,E["smith"],E["republic"],"possible_decline_in_influence_after_1744_due_to_government_policy",
      "Haskell suggests Smith’s influence may have diminished after 1744 because the government discouraged contact between nobles and foreign representatives, while a Resident reportedly said Smith was better placed than a more senior colleague.",
      "‘May have’ is retained; the cited Resident’s identity and the comparison are not independently verified. Footnote 6 is pending.",relation=True,footnote=6,layer="authorial interpretation")
add_s("p300-smith-claimed-government-friendships",P300,376,377,E["smith"],E["republic"],"claimed_friendships_with_principal_government_members",
      "In his claim for the appointment, Smith specifically boasted that he had contracted friendships with principal men in the government.",
      "This is Smith’s quoted claim as reported by Haskell, not proof that the relationships existed; the 1740 letter is pending in footnote 7.",relation=True,footnote=7,layer="nested quotation")
add_s("p300-smith-connoisseur-contacts",P300,377,378,E["smith"],E["zeno"],"friendly_relations_with_zeno_algarotti_and_zanetti_and_goldoni_dedication",
      "Haskell says Smith had friendly relations with Apostolo Zeno, Francesco Algarotti and Antonio Maria Zanetti, and that Goldoni dedicated a play to him.",
      "The play is identified as Il Filosofo Inglese by p.300 footnote 2; its text and dedication remain pending.",relation=True,cross=[P301,NOTES])

# p.301: close p.300’s Goldoni sentence; continue the account through Smith’s Italian and English networks.
add_s("p301-goldoni-and-smith-will",P301,383,383,E["goldoni"],E["smith"],"goldoni_dedicated_play_and_said_smith_was_among_his_admirers",
      "Goldoni’s dedication of Il Filosofo Inglese says Smith had been among his keen admirers; Haskell says Smith’s 1761 will suggests he then had few close Venetian contacts beyond business.",
      "The will is summarized by Haskell rather than read directly; p.300 footnote 2 cites the dedication and remains pending in the consolidated notes segment.",relation=True,cross=[P300,NOTES])
add_s("p301-smith-pasquali-publication-activity",P301,383,383,E["smith"],E["pasquali"],"pasquali_published_smith_catalogues_and_works_suggested_by_him",
      "Pasquali, Smith’s most important client, published catalogues of Smith’s gems, paintings and books, as well as literature and philosophy works that Haskell says Smith clearly suggested.",
      "The source does not list all titles; footnote 1 and its cited letters remain pending.",relation=True,footnote=1)
add_s("p301-smith-artists-business-arrangements",P301,383,383,E["smith"],None,"likely_business_arrangements_with_employed_artists",
      "Haskell considers it very likely that Smith had definite business arrangements with some artists whom he employed for himself and others.",
      "The source marks this as likelihood; no artist or contract is identified here.",relation=True,footnote=2,layer="authorial inference")
add_s("p301-facciolati-friendship-and-books",P301,384,385,E["smith"],E["facciolati"],"friendship_and_bequest_of_three_books_to_facciolati",
      "Two of Smith’s most interesting Italian friends lived in Padua; one was Abate Facciolati, a history professor at the University, to whom Smith left three books with a statement of esteem and gratitude for their long friendship.",
      "The quotation’s bracketed ‘he has’ is editorial; the source document is not independently checked.",relation=True)
add_s("p301-facciolati-picture-collection",P301,386,386,E["facciolati"],C["facciolati_collection"],"picture_collection_designed_to_illustrate_history_of_art",
      "Facciolati had a remarkable picture collection designed to illustrate art history, beginning with Byzantine paintings.",
      "The source does not name individual paintings or say whether this was a building, institution or private collection; type remains open.",relation=True)
add_s("p301-private-museum-pattern",P301,386,386,C["facciolati_collection"],None,"private_art_museums_were_unusual_in_the_first_half_of_the_eighteenth_century",
      "Haskell says private museums of this kind were still unusual during the first half of the eighteenth century.",
      "This is a period-level generalization; the collection’s type remains unresolved.",layer="authorial generalization")
add_s("p301-lodoli-collection",P301,387,387,E["lodoli"],C["lodoli_collection"],"lodoli_collected_art_on_a_similar_principle",
      "Haskell says Lodoli collected works of art on a principle similar to Facciolati’s art-history collection.",
      "Lodoli’s collection is unidentified and kept separate from Facciolati’s; footnote 3 remains pending.",relation=True,footnote=3)
add_s("p301-poleni-profile",P301,387,387,E["smith"],C["poleni"],"smiths_padua_acquaintance_poleni_was_a_university_professor_engineer_and_architect",
      "Smith’s other acquaintance in Padua was Giovanni Poleni, a professor at the University, engineer and architect of distinction.",
      "The source does not establish a precise faculty or appointment date; footnote 4’s letters remain pending.",relation=True,footnote=4)
add_s("p301-scholarly-surroundings",P301,387,388,E["smith"],None,"relationships_suggested_scholarly_social_context",
      "Haskell says Smith’s relationships suggest that he was most at home in scholarly surroundings and calls this all that is known of his participation in Venetian life.",
      "This is an authorial interpretation and transition, not a claim that Smith had no other social contacts.",layer="authorial interpretation")
add_s("p301-smith-mead-letter",P301,388,389,E["smith"],E["mead"],"smith_described_mead_as_his_friend_in_a_letter_to_gori",
      "Haskell says Smith wrote to Gori of his friend Dr Richard Mead, whom he describes as a stimulating early eighteenth-century English art collector.",
      "The quoted letter is cited through footnote 5; the manuscript or full letter is not independently read here.",relation=True,footnote=5)
add_s("p301-mead-newton-friendship",P301,389,389,E["mead"],E["newton"],"mead_was_a_close_friend_of_isaac_newton",
      "Haskell describes Richard Mead as a great friend of Sir Isaac Newton and says Smith himself was closely interested in Newton.",
      "The Newton reference is supported by footnote 6, which remains pending in the consolidated notes segment.",relation=True,footnote=6)
add_s("p301-smith-official-visitors",P301,389,389,E["smith"],E["breval"],"official_duties_and_hospitality_to_english_visitors",
      "Smith’s official duties brought important visitors to Venice; Haskell says his house also welcomed English connoisseurs and artists including John Breval, Horace Walpole, Richard Wilson, Joshua Reynolds, James Wyatt and Robert Adam.",
      "The sentence continues at p.302; the list is not exhaustive, and footnote 7 remains pending.",relation=True,footnote=7,cross=[P302])
add_s("p301-smith-unpopularity-and-walpole",P301,389,389,E["smith"],E["walpole"],"haskell_described_smith_as_unpopular_and_walpole_jeered_at_him",
      "Haskell says no one really liked Smith and reports that Walpole jeered at him as ‘the Merchant of Venice’.",
      "This is Haskell’s summary and quoted characterization; the paragraph continues on p.302.",relation=True,cross=[P302],layer="authorial summary with nested quotation")

new_ids = {row["candidate_id"] for row in newc}
all_ids = cids | new_ids
for row in new_s:
    q = row["qualifiers"]
    first, last, _page, _physical = SEGMENT_LINES[row["segment_id"]]
    if q["source_line_start"] < first or q["source_line_end"] > last:
        raise SystemExit(f"statement range outside segment: {row['statement_id']}")
    for cid in (row["subject_candidate_id"], row["object_candidate_id"]):
        if cid is not None and cid not in all_ids:
            raise SystemExit(f"statement foreign key missing: {row['statement_id']} -> {cid}")
    if not all(cid in all_ids for cid in q["mentioned_candidate_ids"]):
        raise SystemExit(f"mentioned candidate missing: {row['statement_id']}")
spans = sorted((row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]) for row in newm)
for left, right in zip(spans, spans[1:]):
    if left[0] == right[0] and right[1] < left[2]:
        raise SystemExit(f"overlapping mentions: {left[3]} / {right[3]}")

cov[P299].update({"disposition":"reviewed", "migration_status":"partial", "source_line_ranges":"L354-365",
    "note":"Printed p.299 opening and Joseph Smith body checked against CHP-10.pdf physical page 28. Recorded the foreign-resident chapter opening; Smith’s approximate birth, Westminster education, Venetian settlement and merchant activity; Amsterdam trade and Salumieri guild disputes; his residence as a diplomatic meeting place; Pasquali’s publishing firm; the 1735 Gori/Guicciardini/Museum Etruscum project; Ferretti’s frontispiece; Smith’s book/gem/picture purchases; and his 1744 consular appointment. Reused page-indexed candidates for Smith, Venice, Amsterdam, Venetian nobility, Pasquali, Gori, Guicciardini, Museum Etruscum and Ferretti; added candidates for Westminster School, the guild, unnamed diplomatic group, residence, publishing firm and consular offices. Scan correction: the OCR-initial T at L360 duplicates the printed drop cap at L359; the opening reads ‘The ... was an Englishman’. The L366 note-4 excerpt is not remigrated; footnotes 1–4 remain for the consolidated notes segment, and the consular-status sentence closes on p.300."})
cov[P300].update({"disposition":"reviewed", "migration_status":"partial", "source_line_ranges":"L369-378",
    "note":"Printed p.300 body checked against CHP-10.pdf physical page 29. Closed p.299’s consular-status sentence; recorded the 1762 sale to George III, temporary 1767 return to the consulship, death and burial, Haskell’s English/Venetian taste interpretation, Smith’s library/patronage, palace meetings and publishing, the Lodoli–Memmo–Wynne social account, and Smith’s political and connoisseur contacts. Reused the indexed Smith, George III, Lodoli, Memmo, Wynne, Zeno, Algarotti, Zanetti and Goldoni candidates; added candidates for the unnamed residence, collections, Apostoli church, cemetery, diplomatic offices, literary play and unidentified Resident. Scan-only OCR corrections: ‘tins’→‘this’, ‘Use’→‘life’, ‘sine editions’→‘fine editions’, ‘sifty-four’→‘fifty-four’, and ‘eighteenthcentury’→‘eighteenth-century’; ‘S. Niccolo’ reads S. Niccolò. L379–380 are note excerpts reserved for the consolidated notes segment; body sentence continues at p.301, so this segment remains partial."})
cov[P301].update({"disposition":"reviewed", "migration_status":"partial", "source_line_ranges":"L383-389",
    "note":"Printed p.301 body checked against CHP-10.pdf physical page 30. Closed p.300’s Goldoni dedication sentence; recorded Smith’s 1761 will, Pasquali publishing activity, likely artist business arrangements, Facciolati and Poleni in Padua, Facciolati’s untyped picture collection, Haskell’s scholarly-surroundings interpretation, and Smith’s English connections to Mead, Newton and named visitors. Added open candidates for Giovanni Poleni, the University of Padua, Facciolati’s type-unresolved collection and Il Filosofo Inglese; reused indexed candidates for Facciolati, Lodoli, Gori, Mead, Newton, Breval, Walpole, Wilson, Reynolds, Wyatt and Adam. Scan-only OCR corrections include ‘Efe’→‘life’, ‘Eterature’→‘literature’, ‘LodoE’→‘Lodoli’, ‘EngEsh’→‘English’, ‘aU’→‘all’, and ‘Rey-nolds’→‘Reynolds’; S0 unchanged. Page-end sentence continues at p.302; footnotes 1–7 remain in the consolidated notes segment, so this segment remains partial."})
for seg in (P299, P300, P301):
    if NOTES not in cov[seg]["note"] and not cov[seg]["note"]:
        raise SystemExit(f"missing coverage note: {seg}")

summary = {"mode":"APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN",
           "segments":[{"segment":s,"sha256":EXPECTED_SEGMENT_SHA[s]} for s in (P299,P300,P301)],
           "new_candidates":len(newc),"candidate_ids":[r["candidate_id"] for r in newc],
           "new_mentions":len(newm),"new_statements":len(new_s),
           "coverage":{s:cov[s]["migration_status"] for s in (P299,P300,P301)}}
print(json.dumps(summary,ensure_ascii=False,indent=2))

if sys.argv[-1:] == ["--apply"]:
    for path in (cp,mp,sp,vp):
        backup = Path(str(path) + BACKUP)
        if backup.exists():
            raise SystemExit(f"backup already exists: {backup}")
        shutil.copy2(path,backup)
    write_csv(cp,cf,candidates+newc)
    write_csv(mp,mf,mentions+newm)
    write_jsonl(sp,statements+new_s)
    write_csv(vp,vf,[cov[row["segment_id"]] for row in coverage])
    print("Applied p.299-301 body migration; page footnotes remain in the consolidated notes segment.")
