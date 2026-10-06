"""Controlled S2 migration of the section-II opening on p.267; dry-run by default."""
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_sec_ii.md"
HEADING_ID = "chp-9:09_CHP-9_sec_ii:l1-1"
SEGMENT_ID = "chp-9:09_CHP-9_sec_ii:l3-4"
EXPECTED_SEGMENT_SHA = "4a2b6206e3c4df9b60be079003432ebc618752ba7791e3904f2267eb9b5b964b"
EXPECTED_ASSET_SHA = "67d60205c246f2f126433bab8a22ddb29ed73e2af2fed5fff5978c319b3ee923"
EXPECTED_MAX_CANDIDATE = 8664
BACKUP_SUFFIX = ".bak-s2-chp9-sec-ii-opening-20261001"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(handle.name)
    temporary.replace(path)


candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
segment_path = TABLES / "segments.jsonl"
source_bytes = SOURCE.read_bytes()
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if hashlib.sha256(source_bytes).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("section-II source asset has changed")
segments = {row["segment_id"]: row for row in read_jsonl(segment_path)}
if segments.get(SEGMENT_ID, {}).get("sha256") != EXPECTED_SEGMENT_SHA:
    raise SystemExit("section-II opening segment is missing or changed")
if segments[SEGMENT_ID].get("asset_sha256") != EXPECTED_ASSET_SHA:
    raise SystemExit("section-II source asset fingerprint mismatch")
if source_lines[2].startswith("During the seventeenth and eighteenth centuries Venice") is False:
    raise SystemExit("expected p.267 opening text has changed")
if source_lines[3] != "a See, for instance, the attitude of Casanova as described by A. Bozzôla.":
    raise SystemExit("expected p.267 note 6 OCR line has changed")
segment_text = "\n".join(source_lines[2:4])

candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)
candidate_ids = {row["candidate_id"] for row in candidates}
mention_ids = {row["mention_id"] for row in mentions}
statement_ids = {row["statement_id"] for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}
max_candidate = max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates)
if max_candidate != EXPECTED_MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: expected {EXPECTED_MAX_CANDIDATE}, found {max_candidate}")
heading_cov = coverage_by_id.get(HEADING_ID)
segment_cov = coverage_by_id.get(SEGMENT_ID)
if not heading_cov or (heading_cov["disposition"], heading_cov["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"unexpected heading coverage state: {heading_cov}")
if not segment_cov or (segment_cov["disposition"], segment_cov["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"unexpected section-II opening coverage state: {segment_cov}")

EXISTING = {
    "venice_republic": "cand-8572",
    "papacy": "cand-4223",
    "jesuits_index": "cand-1322",
}
for key, candidate_id in EXISTING.items():
    if candidate_id not in candidate_ids:
        raise SystemExit(f"required existing candidate is missing: {key}={candidate_id}")

CANDIDATE_SPECS = [
    ("casanova_local", "Casanova (surname-only reference in p.267 note 6; identity pending)", "person", "P.267 note 6 refers only to Casanova's attitude as described by A. Bozzòla. Keep separate from the indexed Casanova de Seingalt candidate until S3 establishes identity.", 4),
    ("bozzola_person", "A. Bozzòla (initial and surname only in p.267 note 6)", "person", "The scan reads Bozzòla with a grave accent; S0 OCR reads Bozzôla. No full name or publication locator is supplied, so identity remains open.", 4),
    ("bozzola_description", "Unidentified description of Casanova by A. Bozzòla (cited at p.267 note 6)", "archive", "Haskell points to a description by A. Bozzòla but gives no title, date, page, repository or quotation from it. It is a source pointer only, not independent evidence in this task.", 4),
    ("venetian_government", "Venetian government in Haskell's p.267 policy account", "institution", "The passage distinguishes the government from the state as the actor insisting on religious orthodoxy. S3 must decide whether this is represented by the existing Republic of Venice candidate or separately.", 3),
    ("religious_orthodoxy", "Religious orthodoxy as Venetian state policy in Haskell's p.267 account", "term", "Concept named in Haskell's account of the government's policy; the comparison with Rome is preserved as the author's characterization.", 3),
    ("religious_political_dissent", "Religious and political dissent as a paired maxim in Haskell's p.267 account", "term", "The passage reports a maxim that religious and political dissent went hand in hand, even among sceptics. Do not convert this authorial generalization into an independently verified social rule.", 3),
    ("jesuit_readmission_1657", "Readmission of the Jesuits to Venice in 1657", "event", "Haskell reports readmission in return for papal support under financial necessity. The date, actors and stated exchange are preserved as the source's account, not independently verified.", 3),
]

candidate_by_key = {}
new_candidates = []
for offset, (key, name, kind, detail, line_no) in enumerate(CANDIDATE_SPECS, 1):
    candidate_id = f"cand-{EXPECTED_MAX_CANDIDATE + offset:04d}"
    if candidate_id in candidate_ids:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    if any(row["canonical_name"] == name and row["suggested_type"] == kind for row in candidates):
        raise SystemExit(f"candidate natural key already exists: {name}")
    candidate_by_key[key] = candidate_id
    new_candidates.append({
        "candidate_id": candidate_id,
        "index_entry_id": "",
        "canonical_name": name,
        "index_page_range": "",
        "suggested_type": kind,
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": detail,
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L{line_no}",
    })
candidate_ids |= {row["candidate_id"] for row in new_candidates}

line_offsets = {3: 0, 4: len(source_lines[2]) + 1}
new_mentions = []
def add_mention(mention_id, line_no, candidate_id, surface, note, occurrence=0):
    if mention_id in mention_ids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    line = source_lines[line_no - 1]
    positions = []
    cursor = 0
    while True:
        found = line.find(surface, cursor)
        if found < 0:
            break
        positions.append(found)
        cursor = found + 1
    if occurrence >= len(positions):
        raise SystemExit(f"surface missing on L{line_no}: {surface!r}")
    start = line_offsets[line_no] + positions[occurrence]
    end = start + len(surface)
    if segment_text[start:end] != surface:
        raise SystemExit(f"invalid exact mention span: {mention_id}")
    if candidate_id not in candidate_ids:
        raise SystemExit(f"unknown mention candidate: {candidate_id}")
    new_mentions.append({
        "mention_id": mention_id,
        "segment_id": SEGMENT_ID,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    })


add_mention("m-chp9-sec2-p267-venice-polity", 3, EXISTING["venice_republic"], "Venice", "Acts as a political community maintaining independence from papal authority; read as polity, not city.")
add_mention("m-chp9-sec2-p267-rome-authority-1", 3, EXISTING["papacy"], "Rome", "Metonym for papal authority in the independence policy claim, not the city of Rome.", 0)
add_mention("m-chp9-sec2-p267-jesuits", 3, EXISTING["jesuits_index"], "the Jesuits", "Reuse the p.267 index candidate; institutional typing and cross-chapter identity remain for later stages.")
add_mention("m-chp9-sec2-p267-1657-event", 3, candidate_by_key["jesuit_readmission_1657"], "in 1657 to readmit the Jesuits", "The date and act identify the reported readmission event; reason and exchange remain Haskell's framing.")
add_mention("m-chp9-sec2-p267-papal-support", 3, EXISTING["papacy"], "papal support", "Papal authority is the reported source of support exchanged for Jesuit readmission.")
add_mention("m-chp9-sec2-p267-state", 3, EXISTING["venice_republic"], "the State", "Refers to the Venetian political entity in the following government-policy clause.")
add_mention("m-chp9-sec2-p267-government", 3, candidate_by_key["venetian_government"], "the government", "Institutional actor is distinguished in the prose from the state; identity linkage deferred.")
add_mention("m-chp9-sec2-p267-orthodoxy", 3, candidate_by_key["religious_orthodoxy"], "religious orthodoxy", "Policy concept named by Haskell; the Rome comparison is an authorial claim.")
add_mention("m-chp9-sec2-p267-rome-comparison", 3, EXISTING["papacy"], "Rome", "Metonym for papal standards in the comparative orthodoxy claim, not the city of Rome.", 1)
add_mention("m-chp9-sec2-p267-dissent-maxim", 3, candidate_by_key["religious_political_dissent"], "religious and political dissent", "Paired concepts in a reported maxim, not a universally established fact.")
add_mention("m-chp9-sec2-p267-casanova", 4, candidate_by_key["casanova_local"], "Casanova", "Surname only in this note; identity is not presumed to match the indexed Casanova candidate.")
add_mention("m-chp9-sec2-p267-bozzola", 4, candidate_by_key["bozzola_person"], "A. Bozzôla", "Exact S0 surface retained; the scan reads Bozzòla. Initial and surname only.")

new_statements = []
def add_statement(statement_id, line_no, subject, object_, predicate, quote, claim, qualification, mentioned, *, relation=False, crossrefs=(), speaker="Haskell", text_layer="authorial narrative", footnote=None):
    if statement_id in statement_ids or any(row["statement_id"] == statement_id for row in new_statements):
        raise SystemExit(f"duplicate statement ID: {statement_id}")
    if quote not in segment_text:
        raise SystemExit(f"statement quote not anchored in source segment: {statement_id}")
    refs = set(mentioned)
    refs.update(candidate for candidate in (subject, object_) if candidate)
    if not refs <= candidate_ids:
        raise SystemExit(f"unknown statement candidate in {statement_id}: {sorted(refs - candidate_ids)}")
    qualifiers = {
        "source_line_start": line_no,
        "source_line_end": line_no,
        "printed_page": 267,
        "pdf_physical_page": 33,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": sorted(refs),
    }
    if crossrefs:
        qualifiers["cross_reference_segments"] = list(crossrefs)
    if relation:
        qualifiers["relation_candidate"] = True
    if footnote is not None:
        qualifiers["footnote_marker"] = footnote
    new_statements.append({
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "source_file": SOURCE.relative_to(ROOT).as_posix(),
        "origin": "book",
    })


body_quote = source_lines[2]
footnote_quote = source_lines[3]
add_statement("st-chp9-sec2-venice-independence-from-rome", 3, EXISTING["venice_republic"], EXISTING["papacy"], "venice_maintained_political_independence_from_rome", body_quote, "Haskell says Venice maintained an independence from Rome that had long marked its policy.", "In this policy context Venice is the Republic and Rome is papal authority, not either city. This is Haskell's account, not an independently verified constitutional finding.", [EXISTING["venice_republic"], EXISTING["papacy"]], relation=True, speaker="Haskell", text_layer="authorial narrative")
add_statement("st-chp9-sec2-1657-readmission-jesuits", 3, candidate_by_key["jesuit_readmission_1657"], EXISTING["jesuits_index"], "venice_readmitted_jesuits_in_1657_in_exchange_for_papal_support", body_quote, "Haskell says financial necessity compelled Venice in 1657 to readmit the Jesuits in return for papal support.", "Preserve the source's causal and exchange wording; 'financial necessity' is Haskell's explanation. Venice is the Republic and papal support is institutional, not a location.", [candidate_by_key["jesuit_readmission_1657"], EXISTING["venice_republic"], EXISTING["papacy"], EXISTING["jesuits_index"]], relation=True, speaker="Haskell", text_layer="authorial narrative")
add_statement("st-chp9-sec2-government-religious-orthodoxy", 3, candidate_by_key["venetian_government"], candidate_by_key["religious_orthodoxy"], "venetian_government_insisted_on_rigorous_religious_orthodoxy", body_quote, "Haskell says the Venetian government insisted on religious orthodoxy as rigorous as anything Rome could have desired.", "The rigor comparison is Haskell's characterization; Rome denotes the papal standard. Government and Republic are separate candidates until identity is reviewed.", [candidate_by_key["venetian_government"], candidate_by_key["religious_orthodoxy"], EXISTING["venice_republic"], EXISTING["papacy"]], relation=True, speaker="Haskell", text_layer="authorial narrative")
add_statement("st-chp9-sec2-religious-political-dissent-maxim", 3, candidate_by_key["religious_political_dissent"], None, "haskell_reports_dissent_as_a_maxim_even_among_sceptics", body_quote, "Haskell reports a maxim, held even by sceptics, that religious and political dissent went hand in hand.", "This is a reported social maxim in Haskell's narrative, not an unqualified statement about every Venetian or an independently tested generalization.", [candidate_by_key["religious_political_dissent"], candidate_by_key["venetian_government"], candidate_by_key["religious_orthodoxy"]], crossrefs=[{"segment_id": SEGMENT_ID, "source_line_start": 4, "source_line_end": 4}], speaker="Haskell", text_layer="authorial generalization")
add_statement("st-chp9-sec2-casanova-attitude-source-reference", 4, candidate_by_key["casanova_local"], candidate_by_key["bozzola_description"], "bozzola_description_cited_for_casanova_attitude_example", footnote_quote, "Haskell directs readers to A. Bozzòla's description of Casanova's attitude as an example relevant to the preceding claim.", "The note gives no title, page, quotation or account of the attitude; do not infer the content of Bozzòla's description or merge this Casanova with the index candidate before S3.", [candidate_by_key["casanova_local"], candidate_by_key["bozzola_person"], candidate_by_key["bozzola_description"], candidate_by_key["religious_political_dissent"]], footnote=6, speaker="Haskell's footnote", text_layer="footnote source pointer")

if len({row["statement_id"] for row in statements + new_statements}) != len(statements) + len(new_statements):
    raise SystemExit("duplicate statement ID within migration")
if len({row["mention_id"] for row in mentions + new_mentions}) != len(mentions) + len(new_mentions):
    raise SystemExit("duplicate mention ID within migration")

heading_cov.update({
    "disposition": "excluded",
    "migration_status": "complete",
    "source_line_ranges": "L1-1",
    "note": "Section-II Markdown heading only; navigational structure, no independent entity or claim content.",
})
segment_cov.update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L3-4",
    "note": "Printed p.267 section-II opening (CHP-9.pdf physical p.33) read against the scan, including footnote 6 at L4. S2 corrects the OCR marker 'a' to printed 6 and Bozzôla to Bozzòla without changing S0. Rome is papal authority and Venice is the Republic in this context; the 1657 Jesuit readmission, the government's orthodoxy policy, and Haskell's dissent maxim are separate claims. The Casanova note supplies only an author/source pointer; no attitude details are inferred.",
})

summary = {
    "segments": {"excluded_heading": HEADING_ID, "reviewed_content": SEGMENT_ID},
    "new_candidates": len(new_candidates),
    "new_candidate_ids": [row["candidate_id"] for row in new_candidates],
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "verified_source_correction": "p.267 printed note 6 is present at section-II L4; S0 marker 'a' is an OCR error, so no duplicate transcription segment is needed",
    "scan_corrections": ["footnote marker a -> 6", "Bozzôla -> Bozzòla", "maxim,’held -> maxim, held", "hand injiand -> hand in hand"],
    "counts_after": {
        "candidates": len(candidates) + len(new_candidates),
        "mentions": len(mentions) + len(new_mentions),
        "statements": len(statements) + len(new_statements),
        "coverage_rows": len(coverage),
    },
}
print(json.dumps(summary, ensure_ascii=False, indent=2))

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the preflighted migration")
args = parser.parse_args()
if args.apply:
    paths = [candidate_path, mention_path, statement_path, coverage_path]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("one or more recovery backups already exist; inspect before retrying")
    for source_path, backup_path in zip(paths, backups):
        shutil.copy2(source_path, backup_path)
    try:
        write_csv(candidate_path, candidate_fields, candidates + new_candidates)
        write_csv(mention_path, mention_fields, mentions + new_mentions)
        write_jsonl(statement_path, statements + new_statements)
        write_csv(coverage_path, coverage_fields, list(coverage_by_id.values()))
    except Exception:
        for target, backup in zip(paths, backups):
            shutil.copy2(backup, target)
        raise
    print("APPLIED; recovery backups retained: " + ", ".join(path.name for path in backups))
else:
    print("DRY RUN: no S2 table rows written")
