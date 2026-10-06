"""Controlled S2 migration for printed p.276 footnote 1; dry-run unless --apply."""
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
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
BODY = "chp-10:10_CHP-10_intro:l3-13"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_NOTES_SHA = "33d2557d3e681434a9c964316a7a24fe2c00faa934add1381c12fc4d8a7c7f76"
EXPECTED_LINE_SHA = "d711e0424ea85b3d45a418a45c544b8fbbacb9cf340b650ef838344eb0b92eca"
BACKUP = ".bak-s2-chp10-p276-note1-20261002"


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
note_line = src[491]
if hashlib.sha256(note_line.encode("utf-8")).hexdigest() != EXPECTED_LINE_SHA:
    raise SystemExit("p.276 note 1 changed")
note_body = "\n".join(src[490:634])
if hashlib.sha256(note_body.encode("utf-8")).hexdigest() != EXPECTED_NOTES_SHA:
    raise SystemExit("merged note segment changed")
if not note_line.startswith("1 Most early biographers report") or "26 June 1703 Crespi" not in note_line:
    raise SystemExit("p.276 note 1 content mismatch")

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
if maximum != 9278:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for seg, expected in ((BODY, ("reviewed", "complete")), (NOTES, ("queued", "pending"))):
    row = cov.get(seg)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {seg}: {row}")
target_statement = next((row for row in statements if row["statement_id"] == "st-chp10-p276-cole-carriera-pastel-portraits"), None)
if not target_statement or target_statement["qualifiers"].get("footnote_marker") != 1 or not target_statement["qualifiers"].get("footnote_text_pending"):
    raise SystemExit("p.276 body statement or footnote state changed")

NEW_CANDIDATES = [
    ("cand-9279", "Memorie intorno alla vita di Rosalba Carriera celebre pittrice veneziana (Padova, 1843 edition)", "archive",
     "Footnote title describes a life of Carriera written by an anonymous abate in 1755 and cites a Padova 1843 edition, p.12. The print reads 'alla', 'nel' and 'p.12'; S0 OCR has 'alia', 'net' and 'P12'. Do not infer the anonymous author's identity."),
    ("cand-9280", "Girolamo Zanetti", "person",
     "Named in the p.276 footnote as author of Elogio. Do not merge with index candidates for A. M. Zanetti the Elder; identity and biography are deferred to S3."),
    ("cand-9281", "Girolamo Zanetti, Elogio (1781; published 1818)", "archive",
     "Footnote cites p.16 and distinguishes the work's 1781 date from publication in 1818. The cited text has not been independently consulted."),
    ("cand-9282", "Malamani, 1899, p.99 (citation locator; full title unresolved)", "archive",
     "Citation locator in p.276 note 1 for Crespi's comparison dated 26 June 1703. The cited page has not been independently consulted; S3 may align this locator with other Malamani 1899 citations."),
]
new_ids = {row[0] for row in NEW_CANDIDATES}
if new_ids & cids:
    raise SystemExit("one or more planned candidate IDs already exist")

newc = []
for cid, name, kind, detail in NEW_CANDIDATES:
    newc.append({
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name, "index_page_range": "",
        "suggested_type": kind, "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{NOTES}#L492",
    })

first, last = 491, 634
offsets, offset = {}, 0
for line_no in range(first, last + 1):
    offsets[line_no] = offset
    offset += len(src[line_no - 1]) + 1

newm = []
def add_mention(local, surface, candidate_id, note="", occurrence=0):
    mention_id = f"m-chp10-p276n1-{local}"
    if mention_id in mids or any(row["mention_id"] == mention_id for row in newm):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in cids | new_ids:
        raise SystemExit(f"missing candidate for {mention_id}: {candidate_id}")
    positions, start = [], 0
    while True:
        at = note_line.find(surface, start)
        if at < 0:
            break
        positions.append(at)
        start = at + max(1, len(surface))
    if occurrence >= len(positions):
        raise SystemExit(f"surface absent in L492: {surface!r}")
    start_char = offsets[492] + positions[occurrence]
    end_char = start_char + len(surface)
    if note_body[start_char:end_char] != surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
    newm.append({
        "mention_id": mention_id, "segment_id": NOTES, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start_char), "end_char": str(end_char), "note": note,
    })

add_mention("cole-attribution", "Colle inglese", "cand-0801", "The note's phrase is an early-biographical attribution; link to the indexed Christian Cole candidate without treating the cited biographies as independently verified.")
add_mention("carriera", "Rosalba Carriera", "cand-0581", "Named in the title of the cited biography.")
add_mention("memorie-title", "Memorie", "cand-9279", "Title opening; print corrections are recorded in the candidate detail.")
add_mention("zanetti-full-name", "Girolamo Zanetti", "cand-9280")
add_mention("zanetti-work", "Elogio", "cand-9281")
add_mention("zanetti-second-reference", "Zanetti", "cand-9280", "The note disputes the 1708 date reported by Zanetti.", occurrence=1)
add_mention("crespi", "Crespi", "cand-0871")
add_mention("crespi-inference", "Crespi", "cand-0871", "Repeated in Haskell's interpretation of Crespi's likely reference.", occurrence=1)
add_mention("guido-reni", "Guido Reni", "cand-2124")
add_mention("guido-possessive", "Guido’s", "cand-2124", "Possessive reference to Guido Reni in Haskell's conjecture.")
add_mention("malamani-locator", "Malamani, 1899, p. 99", "cand-9282")

quotes = {
    "biographical_attribution": "Most early biographers report that a ‘certo signor Colle inglese’ was the first to advise Rosalba to turn to pastels—see Memorie intorno alia vita di Rosalba Carriera celebre pittrice veneziana scritta dall'abate N.N. net 1755 (Padova, 1843), P12, and Girolamo Zanetti: Elogio, 1781 (published 1818), p. 16.",
    "zanetti_date": "But Zanetti is mistaken when he says that this occurred in 1708, ason 26 June 1703 Crespi had already compared her work in this medium to Guido Reni—Malamani, 1899, p. 99.",
    "guido_manner": "Crespi must have been thinking of Guido’s very late, ‘chalky’ manner which was to be so attractive to eighteenth-century connoisseurs.",
}
for key, quote in quotes.items():
    if quote not in note_line:
        raise SystemExit(f"quote mismatch: {key}")

def make_statement(statement_id, predicate, quote, claim, qualification, ids, layer):
    if statement_id in sids:
        raise SystemExit(f"duplicate statement ID: {statement_id}")
    return {
        "statement_id": statement_id,
        "segment_id": NOTES,
        "subject_candidate_id": None,
        "object_candidate_id": None,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": 492, "source_line_end": 492, "printed_page": 276, "pdf_physical_page": 1,
            "claim": claim, "speaker": "Haskell", "text_layer": layer,
            "qualification": qualification, "mentioned_candidate_ids": ids,
            "parent_body_statement_ids": ["st-chp10-p276-cole-carriera-pastel-portraits"],
            "footnote_number": 1, "cited_material_not_independently_consulted": True,
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_FILE,
    }

newstatements = [
    make_statement(
        "st-chp10-notes-p276n1-biographical-attribution", "haskell_reports_early_biographers_on_colle_and_pastel_advice",
        quotes["biographical_attribution"],
        "Haskell reports that most early biographers identify an English signor Colle as the first to advise Rosalba to turn to pastels, citing an anonymous 1843 edition of Memorie and Girolamo Zanetti's Elogio.",
        "This is Haskell's report of earlier biographers, not an independently checked account. The print reads 'alla' and 'nel' where the OCR segment has 'alia' and 'net'; the anonymous abate remains unidentified.",
        ["cand-0801", "cand-0581", "cand-9279", "cand-9280", "cand-9281"], "authorial note reporting earlier biographies",
    ),
    make_statement(
        "st-chp10-notes-p276n1-zanetti-date-correction", "haskell_disputes_zanettis_1708_date_using_crespis_1703_comparison",
        quotes["zanetti_date"],
        "Haskell rejects Zanetti's 1708 date and reports that Crespi had compared Rosalba's work in pastel with Guido Reni on 26 June 1703.",
        "The day and comparison are Haskell's note as supported by a Malamani 1899 page locator; the cited page has not been independently consulted. OCR has 'ason' for printed 'as on'; S0 remains unchanged.",
        ["cand-9280", "cand-0871", "cand-0581", "cand-2124", "cand-9282"], "authorial note disputing an earlier chronology",
    ),
    make_statement(
        "st-chp10-notes-p276n1-guido-manner-interpretation", "haskell_infers_crespi_meant_guidos_late_chalky_manner",
        quotes["guido_manner"],
        "Haskell infers that Crespi had in mind Guido Reni's very late chalky manner, which Haskell says appealed to eighteenth-century connoisseurs.",
        "This is Haskell's interpretation of what Crespi was thinking, not an independently established account of Crespi's intention.",
        ["cand-0871", "cand-2124"], "authorial interpretation",
    ),
]

for statement in newstatements:
    if statement["original_quote"] not in note_body:
        raise SystemExit(f"quote not anchored: {statement['statement_id']}")

target_statement["qualifiers"]["footnote_text_pending"] = False
target_statement["qualifiers"]["footnote_link_status"] = "resolved_source_migration"
target_statement["qualifiers"]["footnote_segment"] = NOTES
target_statement["qualifiers"]["footnote_source_line"] = 492
target_statement["qualifiers"]["qualification"] = (
    "Retain Haskell's chronology and comparison. Note 1 reports earlier biographical attribution, disputes Zanetti's 1708 date "
    "using a 26 June 1703 Crespi comparison, and gives Haskell's interpretation of Guido's late chalky manner. "
    "The cited works were not independently consulted."
)

body_cov = cov[BODY]
body_cov["note"] = (
    body_cov["note"] + " Note 1 at canonical L492 is now semantically migrated and linked to the Cole-Carriera statement. "
    "S2 image comparison also found that source L13's Cole supplement is absent from the CHP-10.pdf physical p.1 scan; "
    "the supplied text and its existing statements are retained pending source-discrepancy review."
)
notes_cov = cov[NOTES]
notes_cov["disposition"] = "reviewed"
notes_cov["migration_status"] = "partial"
notes_cov["source_line_ranges"] = "L492-492"
notes_cov["note"] = (
    "Processed printed p.276 note 1 at L492: recorded its layered biographical attribution, Zanetti date dispute, "
    "Crespi comparison, Haskell's interpretation, citations and S2-only print readings. Remaining L493-L634 is pending."
)

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the validated changes")
args = parser.parse_args()

print(f"p276 note1 sha256={hashlib.sha256(note_line.encode('utf-8')).hexdigest()}")
print(f"planned candidates={len(newc)} mentions={len(newm)} statements={len(newstatements)}")
print("body footnote link: st-chp10-p276-cole-carriera-pastel-portraits -> canonical L492")
print("source scan discrepancy: L13 supplement absent from printed physical p.1; retained pending review")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

paths = [cp, mp, sp, vp]
for path in paths:
    backup = path.with_name(path.name + BACKUP)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup}")
    shutil.copy2(path, backup)

candidates.extend(newc)
mentions.extend(newm)
statements.extend(newstatements)
write_csv(cp, cf, candidates)
write_csv(mp, mf, mentions)
write_jsonl(sp, statements)
write_csv(vp, vf, coverage)
print(f"applied; recovery copies use suffix {BACKUP}")
