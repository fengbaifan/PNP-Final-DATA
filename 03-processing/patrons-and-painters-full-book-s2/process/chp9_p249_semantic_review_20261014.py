"""Controlled semantic repair for printed p.249 in the full-book S2 pass.

Default invocation is a read-only preflight.  Source OCR is never modified.
This restores p.249 mentions from a pinned prior table and resolves its open
statement classifications after checking the page image and cross-page text.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
SEGMENT_ID = "chp-9:09_CHP-9_intro:l77-88"
PREVIOUS_SEGMENT = "chp-9:09_CHP-9_intro:l38-46"
BASELINE_REV = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_SEGMENT_HASH = "73ab39a6a928011b2397ba2020cb978873200751bd57a8913d385d59ad081dce"
EXPECTED_ASSET_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
BACKUP_SUFFIX = ".bak-s2-chp9-p249-semantic-review-20261014"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl_atomic(path: Path, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


segments = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {row["segment_id"]: row for row in segments}
segment = segment_by_id.get(SEGMENT_ID)
if segment is None or PREVIOUS_SEGMENT not in segment_by_id:
    raise SystemExit(f"missing segment metadata: {SEGMENT_ID} or its p.248 continuation")
if segment["sha256"] != EXPECTED_SEGMENT_HASH or segment["asset_sha256"] != EXPECTED_ASSET_HASH:
    raise SystemExit("p.249 source hashes changed; inspect before repair")
source_asset = ROOT / segment["source_file"]
if hashlib.sha256(source_asset.read_bytes()).hexdigest() != EXPECTED_ASSET_HASH:
    raise SystemExit("source asset hash changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
selected_lines = source_lines[segment["line_start"] - 1:segment["line_end"]]
if hashlib.sha256("\n".join(selected_lines).encode("utf-8")).hexdigest() != EXPECTED_SEGMENT_HASH:
    raise SystemExit("p.249 segment content hash changed")
line_offsets = {}
offset = 0
for line_number, line in zip(range(segment["line_start"], segment["line_end"] + 1), selected_lines):
    line_offsets[line_number] = offset
    offset += len(line) + 1
segment_text = "\n".join(selected_lines)

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
_, candidate_rows = read_csv(candidate_path)
mention_fields, mention_rows = read_csv(mention_path)
statement_rows = read_jsonl(statement_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
candidate_ids = {row["candidate_id"] for row in candidate_rows}
mention_ids = {row["mention_id"] for row in mention_rows}
statement_ids = {row["statement_id"] for row in statement_rows}
statement_by_id = {row["statement_id"]: row for row in statement_rows}
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
coverage = coverage_by_id.get(SEGMENT_ID)
if not coverage or (coverage["disposition"], coverage["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit(f"unexpected p.249 coverage: {coverage}")

expected_existing_ids = {
    "st-chp9-p249-bambini-triumph-venice", "st-chp9-p249-barbaro-conduct",
    "st-chp9-p249-barbaro-will-location", "st-chp9-p249-bassi-citation-continuation",
    "st-chp9-p249-damerini-citation", "st-chp9-p249-family-wealth-and-patronage-pattern",
    "st-chp9-p249-government-limits-noble-power", "st-chp9-p249-old-and-mercantile-families",
    "st-chp9-p249-pesaro-monument", "st-chp9-p249-pesaro-ostentation-and-virtue",
    "st-chp9-p249-pesaro-palace", "st-chp9-p249-tempio-comparison",
}
target_rows = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
if {row["statement_id"] for row in target_rows} != expected_existing_ids:
    raise SystemExit("p.249 statement inventory changed; inspect before repair")
unset_ids = {
    "st-chp9-p249-bassi-citation-continuation", "st-chp9-p249-damerini-citation",
    "st-chp9-p249-government-limits-noble-power", "st-chp9-p249-pesaro-ostentation-and-virtue",
    "st-chp9-p249-pesaro-palace", "st-chp9-p249-tempio-comparison",
}
# This p.249 segment has six unset classifications in the current table.
if any(statement_by_id[sid].get("qualifiers", {}).get("relation_candidate") is not None for sid in unset_ids):
    raise SystemExit("p.249 classification pre-state changed; inspect before repair")
if any(row["segment_id"] == SEGMENT_ID for row in mention_rows):
    raise SystemExit("p.249 already has current mentions; inspect instead of duplicating")

baseline_text = subprocess.check_output(
    ["git", "show", f"{BASELINE_REV}:04-knowledge/tables/mentions.csv"],
    cwd=ROOT, text=True, encoding="utf-8",
)
baseline_mentions = list(csv.DictReader(io.StringIO(baseline_text)))
restored_mentions = [row.copy() for row in baseline_mentions if row["segment_id"] == SEGMENT_ID]
if len(restored_mentions) != 38:
    raise SystemExit(f"pinned baseline has {len(restored_mentions)} p.249 mentions, expected 38")
for row in restored_mentions:
    start, end = int(row["start_char"]), int(row["end_char"])
    if row["candidate_id"] not in candidate_ids:
        raise SystemExit(f"restored mention has missing candidate: {row['mention_id']}")
    if segment_text[start:end] != row["surface_form"]:
        raise SystemExit(f"restored mention span differs from S0: {row['mention_id']}")
    if row["mention_id"] in mention_ids:
        raise SystemExit(f"mention ID already exists: {row['mention_id']}")

# The source-derived façade candidate exists, while the baseline mention was mis-mapped
# to the Damerini archive candidate.  Correct only this p.249 surface span.
facade_mention = next((row for row in restored_mentions if row["mention_id"] == "m-chp9-p249-palace-facade"), None)
if not facade_mention or facade_mention["candidate_id"] != "cand-8182" or "cand-8180" not in candidate_ids:
    raise SystemExit("unexpected Pesaro façade mention mapping; inspect before repair")
facade_mention["candidate_id"] = "cand-8180"
facade_mention["note"] = "Façade of Leonardo Pesaro's family palace, a separate work candidate from the Damerini citation."


def quote_lines(first: int, last: int | None = None):
    last = first if last is None else last
    return "\n".join(source_lines[first - 1:last])


def update(statement_id: str, *, subject: str | None, object_: str | None, predicate: str,
           claim: str, qualification: str, mentioned: list[str], relation: bool,
           first: int, last: int | None = None, speaker: str = "Haskell", quote: str | None = None):
    row = statement_by_id[statement_id]
    row["subject_candidate_id"] = subject
    row["object_candidate_id"] = object_
    row["predicate"] = predicate
    qualifiers = row.setdefault("qualifiers", {})
    qualifiers.update({
        "source_line_start": first,
        "source_line_end": first if last is None else last,
        "printed_page": 249,
        "pdf_physical_page": 11,
        "claim": claim,
        "speaker": speaker,
        "text_layer": "body" if first <= 86 else "footnote continuation",
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation,
        "semantic_review": "2026-10-14 source-order review; quotation, endpoint scope, and attribution checked",
    })
    row["original_quote"] = quote_lines(first, last) if quote is None else quote


def new_statement(statement_id: str, *, first: int, subject: str | None, object_: str | None,
                  predicate: str, claim: str, qualification: str, mentioned: list[str],
                  relation: bool, speaker: str = "Haskell", quote: str | None = None,
                  extras: dict | None = None):
    if statement_id in statement_ids:
        raise SystemExit(f"new statement ID already exists: {statement_id}")
    for candidate_id in [subject, object_, *mentioned]:
        if candidate_id is not None and candidate_id not in candidate_ids:
            raise SystemExit(f"new statement has missing candidate: {statement_id} {candidate_id}")
    qualifiers = {
        "source_line_start": first,
        "source_line_end": first,
        "printed_page": 249,
        "pdf_physical_page": 11,
        "claim": claim,
        "speaker": speaker,
        "text_layer": "body",
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation,
        "semantic_review": "2026-10-14 source-order review; atomized statement",
    }
    if extras:
        qualifiers.update(extras)
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote_lines(first) if quote is None else quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
    }


update(
    "st-chp9-p249-bassi-citation-continuation", subject="cand-8183", object_=None,
    predicate="bibliographic_citation_continues_from_p248_note_4",
    claim="The printed p.249 continuation gives E. Bassi (1959), pp. 240-264, completing p.248 note 4's citation.",
    qualification="Citation only; the article is identifiable from this book's bibliography but has not been independently consulted.",
    mentioned=["cand-8183"], relation=False, first=88,
)
update(
    "st-chp9-p249-damerini-citation", subject="cand-8182", object_=None,
    predicate="bibliographic_citation_for_barbaro_morosini_account",
    claim="Printed note 1 cites a 1928 work by Damerini for the preceding account of Barbaro and Morosini.",
    qualification="Citation only; full title, author identity, and cited passage remain unverified.",
    mentioned=["cand-8182"], relation=False, first=87,
)
update(
    "st-chp9-p249-government-limits-noble-power", subject="cand-8105", object_="cand-8108",
    predicate="government_concern_sought_to_limit_single_noble_power_and_popularity",
    claim="Haskell reports that constitutional writers and foreign observers noticed the government's concern to prevent a single noble from gaining excessive power and popularity; he says the façade shows the background against which this concern was expressed.",
    qualification="Haskell summarizes contemporary observations. Note 2 points to a 1704 British Resident report; that cited document remains unverified. The single noble is unnamed.",
    mentioned=["cand-8173", "cand-8174", "cand-8105", "cand-8108", "cand-8153", "cand-0736"],
    relation=True, first=79, last=80,
)
update(
    "st-chp9-p249-pesaro-ostentation-and-virtue", subject="cand-1885", object_=None,
    predicate="contemporaries_linked_leonardo_pesaro_virtue_to_unprecedented_splendour",
    claim="Contemporaries concluded that Leonardo Pesaro's unprecedented splendour could measure the greatness of his virtue.",
    qualification="This is a judgement attributed to contemporaries, reported by Haskell; retain 'with some justification' and the source's characterization of their conclusion.",
    mentioned=["cand-1885", "cand-3791"], relation=False, first=83, last=83,
    speaker="Contemporaries (reported by Haskell)",
)
update(
    "st-chp9-p249-pesaro-palace", subject="cand-1885", object_="cand-1886",
    predicate="continued_pesaro_family_palace_with_facade_completed_about_17_years_after_his_death",
    claim="Leonardo continued the vast Pesaro family palace; its dramatic façade on the Grand Canal was completed about seventeen years after his death.",
    qualification="Preserve 'about' and the stated interval; the sentence gives no exact completion year. The façade is candidate cand-8180, not the Damerini archive.",
    mentioned=["cand-1885", "cand-1886", "cand-8180", "cand-8178"], relation=True, first=84,
)
update(
    "st-chp9-p249-tempio-comparison", subject="cand-8153", object_="cand-8170",
    predicate="façade_compared_with_tempio_malatestiano_as_human_glorification_in_sacred_setting",
    claim="Closing p.248 L46, Haskell says Barbaro's façade was devoid of a religious symbol and compares its glorification of humanity in a sacred setting with the Tempio Malatestiano at Rimini.",
    qualification="This is Haskell's art-historical comparison. The next sentence, that the façade's motives had immediate political origins, is kept in a separate statement. Correct the page-image reading 'os' to 'of'.",
    mentioned=["cand-8153", "cand-0736", "cand-8170", "cand-8171"], relation=True, first=78,
)
update(
    "st-chp9-p249-barbaro-conduct", subject="cand-0185", object_="cand-1705",
    predicate="dismissed_by_morosini_for_incompetence_after_war_of_candia_conduct",
    claim="Haskell says Antonio Barbaro's conduct in the War of Candia was somewhat discreditable and Francesco Morosini dismissed him for incompetence.",
    qualification="The evaluation 'somewhat discreditable' belongs to Haskell; the stated dismissal reason is incompetence.",
    mentioned=["cand-0185", "cand-8154", "cand-1705"], relation=True, first=79,
)

new_statements = [
    new_statement(
        "st-chp9-p249-facade-immediate-political-origins", first=78,
        subject="cand-8153", object_=None,
        predicate="motives_for_facade_had_immediate_political_origins",
        claim="Haskell says the motives for the S. Maria del Giglio façade had immediate political origins.",
        qualification="Authorial interpretation; the following passage supplies political context but does not name a single formal commission or decision as the cause.",
        mentioned=["cand-8153", "cand-0736"], relation=False,
    ),
    new_statement(
        "st-chp9-p249-nobility-ostentation-increased", first=82,
        subject="cand-8108", object_=None,
        predicate="noble_ostentation_increased_in_late_17th_century",
        claim="Haskell says the ostentation of the nobility increased dramatically in the last years of the seventeenth century.",
        qualification="Broad authorial social characterization; the following Leonardo Pesaro example and contemporaries' judgement are recorded separately.",
        mentioned=["cand-8108", "cand-1885"], relation=False,
        extras={"time": "last years of the seventeenth century"},
    ),
    new_statement(
        "st-chp9-p249-barbaro-returned-and-opposed-morosini", first=79,
        subject="cand-0185", object_="cand-1705",
        predicate="returned_to_venice_and_tried_to_stir_hostility_against_morosini",
        claim="After his dismissal, Haskell says Barbaro returned to Venice and did everything possible to stir hostility against Morosini.",
        qualification="Preserve the author's account of Barbaro's action; no specific act or named supporter is identified.",
        mentioned=["cand-0185", "cand-2719", "cand-1705"], relation=True,
    ),
]

if len({row["statement_id"] for row in new_statements}) != len(new_statements):
    raise SystemExit("duplicate new statement IDs in plan")
for row in new_statements:
    if row["statement_id"] in statement_ids:
        raise SystemExit(f"new statement ID already exists: {row['statement_id']}")
    for candidate_id in [row["subject_candidate_id"], row["object_candidate_id"], *row["qualifiers"]["mentioned_candidate_ids"]]:
        if candidate_id is not None and candidate_id not in candidate_ids:
            raise SystemExit(f"new statement has missing candidate: {row['statement_id']} {candidate_id}")
    if row["original_quote"] not in "\n".join(source_lines[row["qualifiers"]["source_line_start"] - 1:row["qualifiers"]["source_line_end"]]):
        raise SystemExit(f"new statement quote is not reproduced by its source lines: {row['statement_id']}")

mention_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mention_rows}
for row in restored_mentions:
    span = (row["segment_id"], row["start_char"], row["end_char"])
    if span in mention_spans:
        raise SystemExit(f"p.249 mention span already exists: {row['mention_id']}")
    mention_spans.add(span)
mention_rows.extend(restored_mentions)
statement_rows.extend(new_statements)
coverage["note"] = (
    "Printed p.249 reviewed against CHP-9.pdf physical p.11. L78 completes the p.248 façade sentence; "
    "the comparison, political-origin interpretation, and later government concern are separately represented. "
    "Notes 1-5 remain linked to consolidated note locations. This repair restored and span-checked 38 baseline mentions, "
    "corrected the Pesaro façade mention from the Damerini archive to its own façade candidate, and split Barbaro's dismissal/retaliation and Pesaro's social trend/contemporary judgement."
)

final_target = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
if len(final_target) != 15 or any(row.get("qualifiers", {}).get("relation_candidate") is None for row in final_target):
    raise SystemExit("post-plan p.249 inventory/classification check failed")

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply the preflighted p.249 S2 repair")
args = parser.parse_args()
print(json.dumps({
    "segment_id": SEGMENT_ID,
    "baseline_revision": BASELINE_REV,
    "source_segment_sha256": segment["sha256"],
    "existing_statements_classified": len(expected_existing_ids),
    "new_atomic_statements": len(new_statements),
    "p249_statements_after": len(final_target),
    "restored_baseline_mentions": len(restored_mentions),
    "corrected_façade_mention_candidate": "cand-8182 -> cand-8180",
}, ensure_ascii=True, indent=2))
if not args.apply:
    print("DRY RUN: no files changed")
else:
    paths = [mention_path, statement_path, coverage_path]
    backups = []
    for path in paths:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists; inspect before applying: {backup}")
        shutil.copy2(path, backup)
        backups.append(backup)
    write_csv_atomic(mention_path, mention_fields, mention_rows)
    write_jsonl_atomic(statement_path, statement_rows)
    write_csv_atomic(coverage_path, coverage_fields, coverage_rows)
    print("applied; backups=" + ", ".join(path.name for path in backups))
