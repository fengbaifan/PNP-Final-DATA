"""Controlled semantic repair for the p.247 S2 segment.

Default invocation is a read-only preflight.  The source OCR is never modified.
The script restores this segment's source-grounded mentions from the pinned
baseline and atomizes/classifies its existing statements.
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
PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
SEGMENT_ID = "chp-9:09_CHP-9_intro:l27-36"
BASELINE_REV = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_SEGMENT_HASH = "7b7c85bfda0e96fa9e2d3d69aee031457433796ae97125cba42ae80f5f3db2ee"
EXPECTED_ASSET_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
BACKUP_SUFFIX = ".bak-s2-chp9-p247-semantic-review-20261014"


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


segment_rows = read_jsonl(TABLES / "segments.jsonl")
segment = next((row for row in segment_rows if row["segment_id"] == SEGMENT_ID), None)
if segment is None:
    raise SystemExit(f"missing segment metadata: {SEGMENT_ID}")
if segment["sha256"] != EXPECTED_SEGMENT_HASH or segment["asset_sha256"] != EXPECTED_ASSET_HASH:
    raise SystemExit("p.247 source hashes changed; inspect before repair")
source_asset = ROOT / segment["source_file"]
if hashlib.sha256(source_asset.read_bytes()).hexdigest() != EXPECTED_ASSET_HASH:
    raise SystemExit("source asset hash changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
selected_lines = source_lines[segment["line_start"] - 1:segment["line_end"]]
if hashlib.sha256("\n".join(selected_lines).encode("utf-8")).hexdigest() != EXPECTED_SEGMENT_HASH:
    raise SystemExit("p.247 segment content hash changed")
line_offsets = {}
offset = 0
for line_number, line in zip(range(segment["line_start"], segment["line_end"] + 1), selected_lines):
    line_offsets[line_number] = offset
    offset += len(line) + 1

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidate_rows = read_csv(candidate_path)
mention_fields, mention_rows = read_csv(mention_path)
statement_rows = read_jsonl(statement_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
candidate_ids = {row["candidate_id"] for row in candidate_rows}
mention_ids = {row["mention_id"] for row in mention_rows}
statement_ids = {row["statement_id"] for row in statement_rows}
statement_by_id = {row["statement_id"]: row for row in statement_rows}
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
current_coverage = coverage_by_id.get(SEGMENT_ID)
if not current_coverage or (current_coverage["disposition"], current_coverage["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit(f"unexpected p.247 coverage: {current_coverage}")

target_statements = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
expected_existing_ids = {
    "st-chp9-p247-academy-established", "st-chp9-p247-antichiesetta-frescoes",
    "st-chp9-p247-bambini-frescoes", "st-chp9-p247-bourgeois-culture",
    "st-chp9-p247-church-submission", "st-chp9-p247-constitution-criticism",
    "st-chp9-p247-goldoni-left", "st-chp9-p247-gozzi-attached",
    "st-chp9-p247-guardi-visit", "st-chp9-p247-new-nobles-exclusion",
    "st-chp9-p247-new-nobles-integration", "st-chp9-p247-noble-fortunes-and-division",
    "st-chp9-p247-nobles-resist-change", "st-chp9-p247-patronage-status",
    "st-chp9-p247-patronage-tastes", "st-chp9-p247-rich-poor-patrician-politics",
    "st-chp9-p247-senate-admission", "st-chp9-p247-state-administration",
    "st-chp9-p247-state-patronage-decline", "st-chp9-p247-tiepolo-palazzo",
}
if {row["statement_id"] for row in target_statements} != expected_existing_ids:
    raise SystemExit("p.247 statement inventory changed; inspect before repair")
if any(row.get("qualifiers", {}).get("relation_candidate") is not None for row in target_statements if row["statement_id"] in {
    "st-chp9-p247-bourgeois-culture", "st-chp9-p247-constitution-criticism",
    "st-chp9-p247-new-nobles-exclusion", "st-chp9-p247-new-nobles-integration",
    "st-chp9-p247-noble-fortunes-and-division", "st-chp9-p247-patronage-status",
    "st-chp9-p247-patronage-tastes", "st-chp9-p247-rich-poor-patrician-politics",
}):
    raise SystemExit("p.247 classification pre-state changed; inspect before repair")
if any(row["segment_id"] == SEGMENT_ID for row in mention_rows):
    raise SystemExit("p.247 already has current mentions; inspect instead of duplicating")

baseline_text = subprocess.check_output(
    ["git", "show", f"{BASELINE_REV}:04-knowledge/tables/mentions.csv"],
    cwd=ROOT, text=True, encoding="utf-8",
)
baseline_mentions = list(csv.DictReader(io.StringIO(baseline_text)))
restored_mentions = [row for row in baseline_mentions if row["segment_id"] == SEGMENT_ID]
if len(restored_mentions) != 62:
    raise SystemExit(f"pinned baseline has {len(restored_mentions)} p.247 mentions, expected 62")
segment_text = "\n".join(selected_lines)
for row in restored_mentions:
    start, end = int(row["start_char"]), int(row["end_char"])
    if row["candidate_id"] not in candidate_ids:
        raise SystemExit(f"restored mention has missing candidate: {row['mention_id']}")
    if segment_text[start:end] != row["surface_form"]:
        raise SystemExit(f"restored mention span differs from S0: {row['mention_id']}")
    if row["mention_id"] in mention_ids:
        raise SystemExit(f"mention ID already exists: {row['mention_id']}")

line36 = source_lines[35]
quote_start = line36.find("‘Pericoloso")
quote_end = line36.find("’—Marcellino", quote_start)
if quote_start < 0 or quote_end < 0:
    raise SystemExit("could not isolate the Renier quotation in S0 line 36")
renier_quote = line36[quote_start:quote_end + 1]
renier_mention = {
    "mention_id": "m-chp9-p247-renier-1767-statement",
    "segment_id": SEGMENT_ID,
    "candidate_id": "cand-8145",
    "surface_form": renier_quote,
    "start_char": str(line_offsets[36] + quote_start),
    "end_char": str(line_offsets[36] + quote_end + 1),
    "note": "Quoted 1767 statement attributed to Renier and cited through Marcellino, p. 30, note 78.",
}
if renier_mention["candidate_id"] not in candidate_ids or renier_mention["mention_id"] in mention_ids:
    raise SystemExit("Renier quotation candidate/mention precondition failed")
if segment_text[int(renier_mention["start_char"]):int(renier_mention["end_char"])] != renier_quote:
    raise SystemExit("Renier quotation span differs from S0")
restored_mentions.append(renier_mention)

def source_quote(first: int, last: int | None = None):
    last = first if last is None else last
    return "\n".join(source_lines[first - 1:last])


def classify(statement_id: str, *, subject: str | None, object_: str | None, predicate: str,
             claim: str, qualification: str, mentioned: list[str], relation: bool,
             first: int, last: int | None = None, quote: str | None = None):
    row = statement_by_id[statement_id]
    row["subject_candidate_id"] = subject
    row["object_candidate_id"] = object_
    row["predicate"] = predicate
    qualifiers = row.setdefault("qualifiers", {})
    qualifiers.update({
        "source_line_start": first,
        "source_line_end": first if last is None else last,
        "printed_page": 247,
        "pdf_physical_page": 5,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "unnumbered page note" if first >= 35 else "body",
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation,
        "semantic_review": "2026-10-14 source-order review; compound claims atomized where needed",
    })
    row["original_quote"] = source_quote(first, last) if quote is None else quote


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
        "printed_page": 247,
        "pdf_physical_page": 5,
        "claim": claim,
        "speaker": speaker,
        "text_layer": "unnumbered page note" if first >= 35 else "body",
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
        "original_quote": source_quote(first) if quote is None else quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
    }


classify(
    "st-chp9-p247-bourgeois-culture", subject="cand-8131", object_="cand-8108",
    predicate="formed_as_consequence_of_noble_withdrawal_from_trade",
    claim="Haskell describes the formation of a rich bourgeoisie as the natural consequence of the nobles' withdrawal from trade.",
    qualification="This is Haskell's causal account of a collective social change; no individual bourgeois or noble is named.",
    mentioned=["cand-8131", "cand-8108"], relation=True, first=29,
)
classify(
    "st-chp9-p247-constitution-criticism", subject="cand-2726", object_=None,
    predicate="constitution_faced_heavy_foreign_criticism_by_early_18th_century",
    claim="Haskell says the Venetian constitution, once admired in Europe, faced heavy criticism from abroad by the beginning of the eighteenth century.",
    qualification="General political context; the passage names no critic, institution, or specific proposal as an endpoint.",
    mentioned=["cand-2726", "cand-3462"], relation=False, first=28,
)
classify(
    "st-chp9-p247-noble-fortunes-and-division", subject="cand-8147", object_=None,
    predicate="noble_families_had_trade_dependent_fortunes_and_land_derived_income",
    claim="Haskell says noble families' histories and fortunes depended on trade while they had long since drawn their incomes from the land.",
    qualification="Collective socioeconomic description; no individual family or named trade is identified.",
    mentioned=["cand-8147", "cand-8108"], relation=False, first=28,
)
classify(
    "st-chp9-p247-rich-poor-patrician-politics", subject="cand-8132", object_="cand-8105",
    predicate="wealthier_nobles_monopolized_leading_administrative_positions",
    claim="Haskell says wealthier nobles increasingly monopolized all leading positions in the administration.",
    qualification="The families and offices are unnamed; retain the claim as a collective political relation.",
    mentioned=["cand-8132", "cand-8105"], relation=True, first=28,
)
classify(
    "st-chp9-p247-new-nobles-exclusion", subject="cand-8134", object_="cand-8105",
    predicate="excluded_from_important_administrative_spheres",
    claim="Haskell says newer nobles were excluded from the more important spheres of the administration.",
    qualification="The newer families and particular administrative spheres are not named.",
    mentioned=["cand-8134", "cand-8105"], relation=True, first=28,
)
classify(
    "st-chp9-p247-new-nobles-integration", subject="cand-8134", object_=None,
    predicate="aimed_to_disguise_mercantile_origins_and_integrate_into_existing_order",
    claim="Haskell says newer nobles aimed to disguise their mercantile origins and integrate themselves into the existing order.",
    qualification="This is the collective aim attributed by Haskell; no individual family or specific institution is named.",
    mentioned=["cand-8134"], relation=True, first=28,
)
classify(
    "st-chp9-p247-patronage-status", subject="cand-2720", object_="cand-8108",
    predicate="art_patronage_regarded_as_appurtenance_of_aristocratic_status",
    claim="Haskell says art patronage was regarded as a necessary appurtenance of aristocratic status.",
    qualification="The sentence continues at p.248 L39; this completed clause is independently intelligible.",
    mentioned=["cand-8124", "cand-8108"], relation=True, first=31,
)
classify(
    "st-chp9-p247-patronage-tastes", subject="cand-2720", object_="cand-8108",
    predicate="art_patronage_history_reflected_forces_shaping_aristocratic_tastes",
    claim="Haskell frames eighteenth-century Venetian art patronage as the history of forces shaping aristocratic tastes, which were reflected in choices of artists, subjects, and styles.",
    qualification="Authorial synthesis about patronage and aristocratic taste; it does not identify a specific commission.",
    mentioned=["cand-2720", "cand-8108"], relation=True, first=29,
)

classify(
    "st-chp9-p247-church-submission", subject="cand-8130", object_="cand-8108",
    predicate="governed_by_nobility",
    claim="Haskell says the Church was governed entirely by the nobility.",
    qualification="The source signals that its account of the Church will be developed later; no specific church body is named.",
    mentioned=["cand-8130", "cand-8108"], relation=True, first=29,
)
statement_by_id["st-chp9-p247-church-submission"]["qualifiers"].pop("ocr_corrections", None)
classify(
    "st-chp9-p247-senate-admission", subject="cand-8129", object_="cand-8134",
    predicate="admitted_new_families_as_state_resources_drained",
    claim="Haskell says the Senate was compelled to admit more new families as State resources drained during the seventeenth-century wars against the Turks.",
    qualification="The wars are not identified by campaign or date; the new families remain collective and unnamed.",
    mentioned=["cand-8129", "cand-8134", "cand-8136", "cand-8105"], relation=True, first=28,
)

line35 = source_lines[34]
first_note_sentence_end = line35.find(". Thus in")
if first_note_sentence_end < 0:
    raise SystemExit("could not isolate the nobles' constitutional position in line 35")
nobles_sentence = line35[:first_note_sentence_end + 1]
classify(
    "st-chp9-p247-nobles-resist-change", subject="cand-8108", object_="cand-2726",
    predicate="intelligent_and_open_minded_nobles_opposed_constitutional_change",
    claim="Haskell says even the more intelligent and open-minded nobles opposed changes in the constitution.",
    qualification="The passage's note marker is not visible in the scan; preserve its unnumbered note-like status.",
    mentioned=["cand-8108", "cand-2726"], relation=True, first=35, quote=nobles_sentence,
)
ocr_corrections = [
    {"source_line": 36, "ocr": "alia pace", "print": "alla pace", "basis": "CHP-9.pdf physical page 5"},
    {"source_line": 36, "ocr": "tranquillité", "print": "tranquillità", "basis": "CHP-9.pdf physical page 5"},
    {"source_line": 36, "ocr": "di fiiori", "print": "di fuori", "basis": "CHP-9.pdf physical page 5"},
    {"source_line": 36, "ocr": "Fordinario", "print": "l'ordinario", "basis": "CHP-9.pdf physical page 5"},
]

new_statements = [
    new_statement(
        "st-chp9-p247-bourgeoisie-lacked-political-power-culture", first=29,
        subject="cand-8131", object_="cand-2736",
        predicate="lacked_political_power_and_autonomous_culture",
        claim="Haskell says the rich bourgeoisie never acquired political power or an autonomous culture.",
        qualification="This is an attributed negative social characterization, not an interaction between named actors.",
        mentioned=["cand-8131", "cand-2736"], relation=False,
    ),
    new_statement(
        "st-chp9-p247-rich-poor-division-stability", first=28,
        subject="cand-8132", object_="cand-8105",
        predicate="division_between_rich_and_poor_families_endangered_government_stability",
        claim="Haskell says the division between rich and poor families became critical and began to endanger the stability of government.",
        qualification="The opposing family groups are collective and unnamed; preserve the causal political claim.",
        mentioned=["cand-8132", "cand-8133", "cand-8105"], relation=True,
    ),
    new_statement(
        "st-chp9-p247-poorer-patricians-depend-and-plot", first=28,
        subject="cand-8133", object_="cand-8132",
        predicate="alternately_depended_on_and_plotted_against_wealthier_relations",
        claim="Haskell says poorer patrician families alternately depended on and plotted against their more fortunate relations.",
        qualification="The source describes a collective and alternating social relation; no individual family is named.",
        mentioned=["cand-8133", "cand-8132"], relation=True,
    ),
    new_statement(
        "st-chp9-p247-patricians-opposed-widening-government", first=28,
        subject="cand-8133", object_="cand-8105",
        predicate="agreed_with_wealthier_nobles_against_widening_basis_of_government",
        claim="Haskell says poorer patrician families agreed with wealthier nobles that the basis of government should not be widened.",
        qualification="This records the stated shared political position, not a named vote or formal decision.",
        mentioned=["cand-8133", "cand-8132", "cand-8105"], relation=True,
    ),
    new_statement(
        "st-chp9-p247-new-nobles-contempt", first=28,
        subject="cand-8134", object_="cand-8137",
        predicate="treated_with_contempt_by_older_aristocracy",
        claim="Haskell says newer nobles were often treated with contempt by the older aristocracy.",
        qualification="Neither group is identified by individual family names.",
        mentioned=["cand-8134", "cand-8137"], relation=True,
    ),
    new_statement(
        "st-chp9-p247-new-nobles-no-radical-ideas", first=28,
        subject="cand-8134", object_=None,
        predicate="unlikely_to_introduce_radical_ideas_into_society",
        claim="Haskell infers that newer nobles were unlikely to introduce radical ideas into society.",
        qualification="The phrase is explicitly inferential ('hardly likely') and characterizes an unnamed group.",
        mentioned=["cand-8134"], relation=False,
    ),
    new_statement(
        "st-chp9-p247-venetian-conservative-customs-proverb", first=28,
        subject="cand-2738", object_=None,
        predicate="conservative_tone_of_venetian_life_characterized_by_proverb",
        claim="Haskell says the conservative tone of Venetian life became a byword and quotes a French proverb about following ancient customs.",
        qualification="This is an authorial cultural synthesis; the proverb is not attributed to a named speaker in this passage.",
        mentioned=["cand-2738"], relation=False,
    ),
    new_statement(
        "st-chp9-p247-church-maintenance-submission", first=29,
        subject="cand-8130", object_="cand-8105",
        predicate="maintained_in_splendour_through_absolute_submission_to_state",
        claim="Haskell says the Church was maintained with great splendour only at the price of absolute submission to the State.",
        qualification="The source's OCR reads 'pf'; the page image reads 'of'. No specific church body is named.",
        mentioned=["cand-8130", "cand-8105"], relation=True,
        extras={"ocr_corrections": [{"source_line": 29, "ocr": "price pf absolute", "print": "price of absolute", "basis": "CHP-9.pdf physical page 5"}]},
    ),
    new_statement(
        "st-chp9-p247-new-families-purchase-nobility", first=28,
        subject="cand-8134", object_="cand-8135",
        predicate="permitted_to_purchase_noble_status",
        claim="Haskell says newly admitted families were allowed to buy themselves into the nobility.",
        qualification="The source supplies no formal name or procedure details for the purchase.",
        mentioned=["cand-8134", "cand-8135", "cand-8108"], relation=True,
    ),
    new_statement(
        "st-chp9-p247-renier-avoid-novelty", first=36,
        subject="cand-2133", object_="cand-8145",
        predicate="quoted_1767_warning_against_novelty_in_military_and_civil_bodies",
        claim="Haskell quotes Paolo Renier's 1767 warning against introducing novelty in military and civil bodies, citing Marcellino, p. 30, note 78.",
        qualification="The quotation is mediated through Haskell and the cited Marcellino reference; neither source has been independently consulted here. The printed passage has no visible footnote number.",
        mentioned=["cand-2133", "cand-8145", "cand-8146"], relation=True,
        speaker="Haskell quoting Paolo Renier", quote=renier_quote,
        extras={"ocr_corrections": ocr_corrections},
    ),
]

planned_ids = {row["statement_id"] for row in new_statements}
if len(planned_ids) != len(new_statements) or statement_ids & planned_ids:
    raise SystemExit("duplicate new statement ID")
for statement in new_statements:
    if any(candidate_id not in candidate_ids for candidate_id in statement["qualifiers"]["mentioned_candidate_ids"]):
        raise SystemExit(f"new statement mentions missing candidate: {statement['statement_id']}")

# Preserve the established source-local ordering of recovered rows by their offsets.
restored_mentions.sort(key=lambda row: (int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
all_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mention_rows}
for row in restored_mentions:
    span = (row["segment_id"], row["start_char"], row["end_char"])
    if span in all_spans:
        raise SystemExit(f"mention span already exists: {row['mention_id']}")
    all_spans.add(span)

# Update the coverage note only to record the restored source-local mention audit.
current_coverage["note"] = (
    "Printed p.247 (CHP-9.pdf physical p.5) reviewed against the page image. "
    "The p.247 body, continuation of p.246 note 4, and unnumbered Renier quotation are represented with source-line anchors; "
    "the Renier quote is cited through Marcellino, p.30 n.78, and its missing printed marker remains unresolved. "
    "The body sentence at L31 continues at p.248 L39. Numbered notes 1-3 remain in the separate notes segment L332-334. "
    "This repair restored and span-checked 62 baseline mentions plus one mention for the quoted Renier statement."
)

statement_rows.extend(new_statements)
mention_rows.extend(restored_mentions)
final_p247 = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
if len(final_p247) != 30 or any(row.get("qualifiers", {}).get("relation_candidate") is None for row in final_p247):
    raise SystemExit("post-plan p.247 inventory/classification check failed")

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply the preflighted p.247 S2 repair")
args = parser.parse_args()
print(json.dumps({
    "segment_id": SEGMENT_ID,
    "baseline_revision": BASELINE_REV,
    "source_segment_sha256": segment["sha256"],
    "existing_statements_classified": len(expected_existing_ids),
    "new_atomic_statements": len(new_statements),
    "p247_statements_after": len(final_p247),
    "restored_baseline_mentions": 62,
    "new_quoted_statement_mentions": 1,
    "p247_mentions_after": len(restored_mentions),
    "no_new_candidates": True,
}, ensure_ascii=False, indent=2))
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
