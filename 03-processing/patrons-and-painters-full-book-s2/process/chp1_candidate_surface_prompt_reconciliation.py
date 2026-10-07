"""Adjudicate the 64 remaining chapter 1 candidate-surface prompts.

The locator is a prompt generator only. This fixed, source-locked plan records
the 27 accepted mentions and rules for the 37 no-write prompts. Default mode
preflights without writing; --apply writes atomically and checks the residual
prompt set, restoring the recovery copy if that postcondition fails.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
import tempfile
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
MENTIONS = TABLES / "mentions.csv"
SEGMENTS = TABLES / "segments.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
sys.path.insert(0, str(ROOT / "scripts"))
import audit_s2_candidate_surfaces as surface_audit

EXPECTED_HASHES = {
    "02-sources/02-Markdown/01_CHP-1_sec_i.md": "fb6198d0392e70a23a2d9ed05c0d432d4466de4ba75cc96762e3b4e45a204c40",
    "02-sources/02-Markdown/01_CHP-1_sec_ii.md": "1b5890ce028c421718abcb28e4c6dc4070be1bc71597a96247b32ebee42e2268",
    "02-sources/02-Markdown/02_CHP-2_sec_vii.md": "5f2ec3c85927ed4aded258d7a6b1801ccb3b8e0416f0f3f9e57ad7b2fae8dd4c",
    "04-knowledge/tables/entity-candidates.csv": "b45c5ad6c5be4f2e16ea51ed2c782aa06745d7b80af993066df42255395f570f",
    "04-knowledge/tables/mentions.csv": "1b2bc6054376e91560c087be94119a3283d262bd72fa6c56be96306a9235a1cd",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/units/places/rome.md": "dde5ccd45f555b6f8de18c0e51bf8480ff444b457e5ccd2628fcb925a19dd53c",
    "04-knowledge/units/institutions/accademia-di-san-luca.md": "104034d12d618cd4f54e50891197034068b465e36916341d528dc18ca1b60fd3",
}


def item(
    segment_id: str,
    candidate_id: str,
    surface_form: str,
    start_char: int,
    note: str,
    *,
    prompt_surface: str | None = None,
    prompt_start: int | None = None,
    prompt_end: int | None = None,
) -> dict[str, object]:
    end_char = start_char + len(surface_form)
    return {
        "segment_id": segment_id,
        "candidate_id": candidate_id,
        "surface_form": surface_form,
        "start_char": start_char,
        "end_char": end_char,
        "note": note,
        "prompt_surface": prompt_surface if prompt_surface is not None else surface_form,
        "prompt_start": prompt_start if prompt_start is not None else start_char,
        "prompt_end": prompt_end if prompt_end is not None else end_char,
    }


PLAN = [
    item(
        "chp-1:01_CHP-1_sec_ii:l48-60", "cand-3126", "Rome", 243,
        "Exact city substring within the locator's longer “in Rome” match; unrelated person and institution subentries are not the referent.",
        prompt_surface="in Rome", prompt_start=240, prompt_end=247,
    ),
    item(
        "chp-1:01_CHP-1_sec_ii:l48-60", "cand-3126", "Rome", 2589,
        "Exact city substring within the locator's longer “in Rome” match; unrelated person and institution subentries are not the referent.",
        prompt_surface="in Rome", prompt_start=2586, prompt_end=2593,
    ),
    item(
        "chp-1:01_CHP-1_sec_ii:l137-146", "cand-3126", "Rome", 1428,
        "Exact city substring within the locator's longer “in Rome” match; unrelated person and institution subentries are not the referent.",
        prompt_surface="in Rome", prompt_start=1425, prompt_end=1432,
    ),
    item(
        "chp-1:01_CHP-1_sec_ii:l137-146", "cand-3470", "Accademia di S. Luca", 1946,
        "Second full-name occurrence; the sentence identifies Pieter van Laer as a member of the Roman artists’ academy.",
    ),
    item(
        "chp-1:01_CHP-1_sec_ii:l118-127", "cand-3470", "Academy", 1101,
        "Capitalized anaphor for the Accademia discussed immediately before; the later doctrinal characterization remains temporally qualified.",
    ),
    item(
        "chp-1:01_CHP-1_sec_ii:l148-153", "cand-2477", "social position of the artist", 1194,
        "Exact indexed concept in Haskell’s Rome–Venice comparison.",
    ),
    item(
        "chp-1:01_CHP-1_sec_ii:l28-38", "cand-0837", "contracts", 41,
        "General term for artistic contracts; not a specific archival instrument.",
    ),
    item(
        "chp-1:01_CHP-1_sec_ii:l28-38", "cand-0837", "Contracts", 278,
        "General term for artistic contracts; not a specific archival instrument.",
    ),
    item(
        "chp-1:01_CHP-1_sec_ii:l148-153", "cand-0837", "contracts", 1382,
        "General term for artistic contracts; not a specific archival instrument.",
    ),
    item(
        "chp-1:01_CHP-1_sec_ii:l168-239", "cand-0837", "contracts", 1933,
        "General term for artistic contracts; not a specific archival instrument.",
    ),
    item(
        "chp-1:01_CHP-1_sec_ii:l19-26", "cand-0840", "subject", 2613,
        "Commissioned picture’s subject, discussed as a term of patronal control.",
    ),
    item(
        "chp-1:01_CHP-1_sec_ii:l19-26", "cand-0840", "subject", 2873,
        "Subject of a religious fresco or altarpiece, discussed as a term of patronal control.",
    ),
    item(
        "chp-1:01_CHP-1_sec_ii:l28-38", "cand-0840", "subject", 435,
        "Contract instructions identify the outline of a subject, leaving elaboration to the painter.",
    ),
    item(
        "chp-1:01_CHP-1_sec_ii:l28-38", "cand-0840", "subject", 2710,
        "A particular commissioned subject within the discussion of contract terms and price.",
    ),
    item(
        "chp-1:01_CHP-1_sec_ii:l40-46", "cand-0840", "subject", 903,
        "Subject is discussed with size in the same indexed commission and collecting passage; no individual work is inferred.",
    ),
    item(
        "chp-1:01_CHP-1_sec_ii:l40-46", "cand-0840", "subject", 1586,
        "Subject-matter of pictures is contrasted with stylistic affinities in a patron’s collection.",
    ),
    item(
        "chp-1:01_CHP-1_sec_ii:l40-46", "cand-0840", "subject", 1777,
        "The commission explicitly leaves sacred or profane subject choice to Paolo Girolamo Piola.",
    ),
    item(
        "chp-1:01_CHP-1_sec_ii:l40-46", "cand-0840", "subject", 2985,
        "The commission requests any subject representing an aspect of Painting.",
    ),
    item(
        "chp-1:01_CHP-1_sec_ii:l62-71", "cand-0840", "subject", 1513,
        "Subject-matter is listed among the commission terms decided before the time limit.",
    ),
    item(
        "chp-1:01_CHP-1_sec_ii:l79-84", "cand-0840", "subject", 2281,
        "Subject is listed among the likely terms agreed between client and artist.",
    ),
    item(
        "chp-1:01_CHP-1_sec_ii:l168-239", "cand-0840", "subject", 1072,
        "The S. Antonino commission assigned the subject while allowing the painter freedom to elaborate.",
    ),
    item(
        "chp-1:01_CHP-1_sec_ii:l168-239", "cand-0840", "subject", 2422,
        "Subject occurs in a quoted letter about Cortona’s refusal to make a proposal without one.",
    ),
    item(
        "chp-1:01_CHP-1_sec_ii:l168-239", "cand-3451", "modelli", 3000,
        "Plural of the existing preparatory modello term; the reported Cortona studies remain disputed as works.",
    ),
    item(
        "chp-1:01_CHP-1_sec_ii:l168-239", "cand-3451", "modelli", 3519,
        "Plural of the existing preparatory modello term in the Sacchi examples; no individual study is identified.",
    ),
    item(
        "chp-1:01_CHP-1_sec_ii:l62-71", "cand-0841", "time limit", 1577,
        "Exact contract term describing the deadline imposed on a commission.",
    ),
    item(
        "chp-1:01_CHP-1_sec_ii:l96-104", "cand-1660", "Michelangelo", 1973,
        "Person reference in the comparison of Bernini’s opportunities with Michelangelo’s.",
    ),
    item(
        "chp-1:01_CHP-1_sec_ii:l168-239", "cand-4957", "palace", 3228,
        "The definite place reference follows “Barberini Salone”; mapped to the existing Palazzo Barberini candidate, with cross-chapter identity retained for S3.",
    ),
]

NO_WRITE_REASON = {
    "palace": "generic_palace",
    "altarpieces": "generic_work_class",
    "churches": "generic_place_class",
    "collection": "unnamed_collection",
    "prince": "title_or_anonymous_role",
    "prices": "generic_market_term",
    "drawings": "generic_medium",
    "subject": "ordinary_subject_matter",
    "portraits": "generic_work_class_portraits",
    "battle": "metaphor",
    "payment": "generic_payment",
    "temperament": "ordinary_personality_trait",
    "character": "ordinary_quality",
}
REASON_TEXT = {
    "generic_palace": "Residence or palace is generic/unnamed; no particular building is established.",
    "generic_work_class": "Generic work category; no distinct work is identified by this span.",
    "generic_place_class": "Generic plural reference to churches; no single site is identified.",
    "unnamed_collection": "Collection is descriptive or lacks an independent identity as an object.",
    "title_or_anonymous_role": "Title/role or anonymous prince, not the indexed work The Prince or a specific person.",
    "generic_market_term": "Generic prices, not a distinct entity.",
    "generic_medium": "Generic drawing medium, not a separately identified work.",
    "ordinary_subject_matter": "Ordinary subject-matter reference about Academy membership, outside the contracts/subject concept.",
    "generic_work_class_portraits": "Generic portrait category, not an individually identified work.",
    "metaphor": "Metaphorical use of battle, not a named work or event.",
    "generic_payment": "Generic payment practice, not a distinct document or entity.",
    "ordinary_personality_trait": "Ordinary artist trait here; distinct from the indexed development of the artistic-temperament concept on pp. 21–23.",
    "ordinary_quality": "Ordinary use of character as a quality, not a specific person’s indexed attribute.",
}
EXPECTED_NO_WRITE_COUNTS = {
    "generic_palace": 6,
    "generic_work_class": 2,
    "generic_place_class": 6,
    "unnamed_collection": 2,
    "title_or_anonymous_role": 6,
    "generic_market_term": 3,
    "generic_medium": 3,
    "ordinary_subject_matter": 1,
    "generic_work_class_portraits": 2,
    "metaphor": 1,
    "generic_payment": 2,
    "ordinary_personality_trait": 1,
    "ordinary_quality": 2,
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed mention plan")
ARGS = parser.parse_args()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def signature(hit: dict[str, object]) -> tuple[str, int, int]:
    return (
        str(hit["segment_id"]),
        int(hit["start_char"]),
        int(hit["end_char"]),
    )


for relative_path, expected_hash in EXPECTED_HASHES.items():
    actual_hash = sha256(ROOT / relative_path)
    if actual_hash != expected_hash:
        raise SystemExit(f"input hash mismatch: {relative_path}: {actual_hash}")

mention_fields, rows = read_csv(MENTIONS)
expected_fields = [
    "mention_id", "segment_id", "candidate_id", "surface_form",
    "start_char", "end_char", "note",
]
if mention_fields != expected_fields:
    raise SystemExit(f"unexpected mentions.csv schema: {mention_fields}")

segments = {
    row["segment_id"]: row
    for row in (
        json.loads(line)
        for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    )
}
candidate_fields, candidate_rows = read_csv(CANDIDATES)
candidates = {row["candidate_id"]: row for row in candidate_rows}
summary, hits = surface_audit.audit("chp-1", 6)
if int(summary["uncovered_candidate_surface_spans"]) != 64:
    raise SystemExit(f"expected 64 prompts, found {summary['uncovered_candidate_surface_spans']}")

plan_by_prompt = {}
for planned_item in PLAN:
    prompt_key = (
        str(planned_item["segment_id"]),
        int(planned_item["prompt_start"]),
        int(planned_item["prompt_end"]),
    )
    if prompt_key in plan_by_prompt:
        raise SystemExit(f"duplicate accepted prompt in plan: {prompt_key}")
    plan_by_prompt[prompt_key] = planned_item

hits_by_signature = {signature(hit): hit for hit in hits}
if len(hits_by_signature) != len(hits):
    raise SystemExit("duplicate prompt signatures from locator")
if not set(plan_by_prompt).issubset(hits_by_signature):
    missing = sorted(set(plan_by_prompt) - set(hits_by_signature))
    raise SystemExit(f"accepted plan is not grounded in current prompts: {missing}")

planned_rows = []
existing_ids = {row["mention_id"] for row in rows}
existing_keys = {
    (row["segment_id"], int(row["start_char"]), int(row["end_char"]))
    for row in rows
}
for prompt_key, planned_item in plan_by_prompt.items():
    hit = hits_by_signature[prompt_key]
    if hit["surface_form"] != planned_item["prompt_surface"]:
        raise SystemExit(f"prompt text mismatch: {prompt_key}")
    segment_id = str(planned_item["segment_id"])
    candidate_id = str(planned_item["candidate_id"])
    if segment_id not in segments:
        raise SystemExit(f"unknown segment: {segment_id}")
    if candidate_id not in candidates:
        raise SystemExit(f"unknown candidate: {candidate_id}")
    if candidates[candidate_id]["suggested_type"] not in {
        "person", "place", "institution", "work", "family", "event", "archive", "term"
    }:
        raise SystemExit(f"candidate type cannot receive a mention: {candidate_id}")
    segment = segments[segment_id]
    source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
    start, end = int(planned_item["start_char"]), int(planned_item["end_char"])
    surface = str(planned_item["surface_form"])
    if source_text[start:end] != surface:
        raise SystemExit(f"source span mismatch: {segment_id} {start}:{end} {surface!r}")
    natural_key = (segment_id, start, end)
    if natural_key in existing_keys:
        raise SystemExit(f"mention natural key already exists: {natural_key}")
    if any(
        old["segment_id"] == segment_id
        and start < int(old["end_char"])
        and end > int(old["start_char"])
        for old in rows
    ):
        raise SystemExit(f"new mention overlaps an existing mention: {natural_key}")
    digest = hashlib.sha256(
        f"{segment_id}|{start}|{end}|{candidate_id}".encode("utf-8")
    ).hexdigest()[:16]
    mention_id = f"m-s2-surface-{digest}"
    if mention_id in existing_ids:
        raise SystemExit(f"mention ID already exists: {mention_id}")
    planned_rows.append({
        "mention_id": mention_id,
        "segment_id": segment_id,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": str(planned_item["note"]),
    })
    existing_ids.add(mention_id)
    existing_keys.add(natural_key)

no_write_hits = [hit for hit in hits if signature(hit) not in plan_by_prompt]
no_write_counts: Counter[str] = Counter()
for hit in no_write_hits:
    surface = str(hit["surface_form"]).casefold()
    reason = NO_WRITE_REASON.get(surface)
    if reason is None:
        raise SystemExit(f"no adjudication rule for prompt: {signature(hit)} {surface!r}")
    no_write_counts[reason] += 1
if len(PLAN) != 27 or len(no_write_hits) != 37 or dict(no_write_counts) != EXPECTED_NO_WRITE_COUNTS:
    raise SystemExit(
        f"decision partition mismatch: accepted={len(PLAN)}, no_write={len(no_write_hits)}, "
        f"no_write_counts={dict(no_write_counts)}"
    )

plan_sha = hashlib.sha256(
    json.dumps(
        {"accepted": PLAN, "no_write_counts": EXPECTED_NO_WRITE_COUNTS, "no_write_reasons": REASON_TEXT},
        ensure_ascii=False,
        sort_keys=True,
    ).encode("utf-8")
).hexdigest()
print(f"chapter={summary['chapter']}")
print(f"reviewed_segments_scanned={summary['reviewed_segments_scanned']}")
print(f"candidate_surface_prompts={len(hits)}")
print(f"accepted_mentions={len(planned_rows)}")
print(f"no_write_prompts={len(no_write_hits)}")
for reason, count in sorted(no_write_counts.items()):
    print(f"no_write[{reason}]={count}: {REASON_TEXT.get(reason, '')}")
print(f"mentions_before={len(rows)}")
print(f"mentions_after={len(rows) + len(planned_rows)}")
print(f"plan_sha256={plan_sha}")
if not ARGS.apply:
    print("mode=dry-run; no files written")
    raise SystemExit(0)

recovery = Path(tempfile.gettempdir()) / (
    "pnp-s2-chp1-surface-prompts-" + datetime.now().strftime("%Y%m%d-%H%M%S")
)
recovery.mkdir(parents=True, exist_ok=False)
backup = recovery / MENTIONS.name
shutil.copy2(MENTIONS, backup)
print(f"recovery_copy={backup}")

raw = MENTIONS.read_bytes()
line_ending = "\r\n" if b"\r\n" in raw else "\n"
encoding = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
with tempfile.NamedTemporaryFile(
    "w", encoding=encoding, newline="", dir=TABLES, delete=False
) as stream:
    writer = csv.DictWriter(stream, fieldnames=mention_fields, lineterminator=line_ending)
    writer.writeheader()
    writer.writerows(rows)
    writer.writerows(planned_rows)
    temporary = Path(stream.name)
temporary.replace(MENTIONS)

post_summary, post_hits = surface_audit.audit("chp-1", 6)
expected_residual = {signature(hit) for hit in no_write_hits}
actual_residual = {signature(hit) for hit in post_hits}
if (
    int(post_summary["uncovered_candidate_surface_spans"]) != 37
    or actual_residual != expected_residual
):
    shutil.copy2(backup, MENTIONS)
    raise SystemExit(
        "post-write prompt check failed; mentions.csv restored from recovery copy"
    )
print(f"mentions_sha256_after={sha256(MENTIONS)}")
print(f"post_write_prompts={post_summary['uncovered_candidate_surface_spans']}")
print(f"written_mentions={len(planned_rows)}")
