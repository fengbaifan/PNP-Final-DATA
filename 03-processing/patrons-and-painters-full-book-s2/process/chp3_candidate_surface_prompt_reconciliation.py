"""Adjudicate all 40 current chapter 3 candidate-surface prompts.

The locator is heuristic only. This source-locked plan records exact accepted
mentions and explicit no-write decisions. Default mode is a read-only dry-run;
--apply appends mentions.csv with a recovery copy and verifies the exact
post-write prompt set.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
MENTIONS = TABLES / "mentions.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
COVERAGE = TABLES / "s2-coverage.csv"
sys.path.insert(0, str(ROOT / "scripts"))
import audit_s2_candidate_surfaces as surface_audit

EXPECTED_HASHES = {
    "04-knowledge/tables/entity-candidates.csv": "7261bd27b8ccf019aa417ff09fce2175d1eb834ad101bff0c62fe96475c29843",
    "04-knowledge/tables/mentions.csv": "52d986b885741abcec92e5d4e1a4d9fbf8d8ced4c3d6cb7040a621290bfe0f9a",
    "04-knowledge/tables/book-statements.jsonl": "66cfa79868e5401e48423a6a353c6fc4da4242e0d400f0a77433a490e3568b3d",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/s2-coverage.csv": "84f8497a7ce0100f4785acd8bf8ed88bb4c69fe5254cd89d172577b0400eb6c1",
    "scripts/audit_s2_candidate_surfaces.py": "44874e88e4940af624ad7b91b6f3e7d016f8c4083c203114e354b6e6622901ba",
    "02-sources/02-Markdown/03_CHP-3_sec_i.md": "a18f48c7b8bf5b161fa13a7ce26ed2935e72d9a14d555f82dfc1d85f84314255",
    "02-sources/02-Markdown/03_CHP-3_sec_ii.md": "cb17a400fc5a79d895e31fe4a112c83e010f5e5b859883852b3985b7010eb1e6",
    "02-sources/02-Markdown/03_CHP-3_sec_iv.md": "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed",
}


def accepted(
    segment_id: str,
    prompt_start: int,
    prompt_surface: str,
    candidate_id: str,
    mention_surface: str,
    mention_start: int,
    note: str,
) -> dict[str, object]:
    return {
        "segment_id": segment_id,
        "prompt_start": prompt_start,
        "prompt_end": prompt_start + len(prompt_surface),
        "prompt_surface": prompt_surface,
        "candidate_id": candidate_id,
        "surface_form": mention_surface,
        "start_char": mention_start,
        "end_char": mention_start + len(mention_surface),
        "note": note,
    }


def no_write(segment_id: str, start: int, surface: str, reason: str) -> dict[str, object]:
    return {
        "segment_id": segment_id,
        "start_char": start,
        "end_char": start + len(surface),
        "surface_form": surface,
        "reason": reason,
    }


SI26 = "chp-3:03_CHP-3_sec_i:l26-33"
SI3 = "chp-3:03_CHP-3_sec_i:l3-14"
SII19 = "chp-3:03_CHP-3_sec_ii:l19-31"
SII33 = "chp-3:03_CHP-3_sec_ii:l33-38"
SII40 = "chp-3:03_CHP-3_sec_ii:l40-52"
SII62 = "chp-3:03_CHP-3_sec_ii:l62-72"
SII102 = "chp-3:03_CHP-3_sec_ii:l102-113"
SII115 = "chp-3:03_CHP-3_sec_ii:l115-123"
SII144 = "chp-3:03_CHP-3_sec_ii:l144-179"
SIV8 = "chp-3:03_CHP-3_sec_iv:l8-14"
SIV16 = "chp-3:03_CHP-3_sec_iv:l16-24"
SIV26 = "chp-3:03_CHP-3_sec_iv:l26-33"
SIV58 = "chp-3:03_CHP-3_sec_iv:l58-67"
SIV69 = "chp-3:03_CHP-3_sec_iv:l69-73"
SIV75 = "chp-3:03_CHP-3_sec_iv:l75-81"
SIV96 = "chp-3:03_CHP-3_sec_iv:l96-104"
SIV106 = "chp-3:03_CHP-3_sec_iv:l106-116"
SIV118 = "chp-3:03_CHP-3_sec_iv:l118-128"
SIV130 = "chp-3:03_CHP-3_sec_iv:l130-139"
SIV152 = "chp-3:03_CHP-3_sec_iv:l152-163"
SIV165 = "chp-3:03_CHP-3_sec_iv:l165-177"
SIV179 = "chp-3:03_CHP-3_sec_iv:l179-187"
SIV189 = "chp-3:03_CHP-3_sec_iv:l189-243"

ACCEPTED = [
    accepted(SII19, 637, "subject", "cand-0840", "subject", 637,
             "Art-historical subject-matter innovation; maps to the indexed patronal subject concept."),
    accepted(SII33, 502, "subject", "cand-0840", "subject", 502,
             "The fresco subject is explicitly discussed as sermon-like subject-matter."),
    accepted(SIV130, 3159, "subject", "cand-0840", "subject", 3159,
             "Subject-matter and treatment are compared with earlier work."),
    accepted(SIV189, 490, "subject", "cand-0840", "subject", 490,
             "The selected subject is compared with the one chosen for Carlone."),
    accepted(SIV58, 2431, "subject", "cand-0840", "subject", 2431,
             "A different artistic subject is explicitly identified."),
    accepted(SIV75, 209, "subject", "cand-0840", "subject", 209,
             "The Adoration of the Lamb is discussed as a revived subject."),
    accepted(SIV152, 3294, "Jesuits", "cand-1321", "Jesuits", 3294,
             "Named religious institution in the historical account."),
    accepted(SIV165, 357, "Jesuits", "cand-1321", "Jesuits", 357,
             "Named religious institution in the historical account."),
    accepted(SIV179, 1326, "Jesuits", "cand-1321", "Jesuits", 1326,
             "Named religious institution in the historical account."),
    accepted(SIV189, 3750, "Jesuits", "cand-1321", "Jesuits", 3750,
             "Named religious institution in the debate footnote."),
    accepted(SIV189, 4424, "Jesuits", "cand-1321", "Jesuits", 4424,
             "Named religious institution in the debate footnote."),
    accepted(SIV118, 2721, "canvas", "cand-3571", "canvas", 2721,
             "Canvas is the material of theatrical apparatus in this passage, not a claim about painting support."),
    accepted(SIV189, 1895, "drawings", "cand-5478", "drawings", 1895,
             "Specific drawings of The Blood of Christ associated with Bernini/Gaulli programmes; retain the existing grouped work candidate."),
    accepted(SIV8, 3007, "in Rome", "cand-3126", "Rome", 3010,
             "The prompt collides with unrelated indexed phrases; record only the exact city span."),
]

NO_WRITE = [
    no_write(SI26, 1166, "palace", "generic_palace"),
    no_write(SI3, 860, "Churches", "generic_place_class"),
    no_write(SII102, 1608, "school", "ordinary_school_days"),
    no_write(SII115, 251, "churches", "generic_place_class"),
    no_write(SII144, 984, "churches", "generic_place_class"),
    no_write(SII144, 1424, "churches", "generic_place_class"),
    no_write(SII144, 4126, "churches", "generic_place_class"),
    no_write(SII33, 2589, "financial difficulties", "generic_financial_condition"),
    no_write(SII40, 2954, "character", "ordinary_character_quality"),
    no_write(SII62, 521, "altarpieces", "generic_artwork_class"),
    no_write(SIV106, 716, "payment", "generic_payment"),
    no_write(SIV106, 1070, "school", "generic_art_school"),
    no_write(SIV118, 914, "altarpieces", "generic_artwork_class"),
    no_write(SIV118, 1478, "churches", "generic_place_class"),
    no_write(SIV118, 1910, "churches", "generic_place_class"),
    no_write(SIV130, 1774, "financial difficulties", "generic_financial_condition"),
    no_write(SIV16, 2195, "battle", "generic_genre"),
    no_write(SIV179, 715, "character", "ordinary_character_quality"),
    no_write(SIV179, 1098, "churches", "generic_place_class"),
    no_write(SIV179, 1821, "churches", "generic_place_class"),
    no_write(SIV26, 199, "earnings", "generic_artist_income"),
    no_write(SIV58, 34, "subject", "ordinary_grammatical_subject"),
    no_write(SIV69, 32, "churches", "generic_place_class"),
    no_write(SIV75, 1641, "temperament", "ordinary_temperament"),
    no_write(SIV96, 165, "churches", "generic_place_class"),
    no_write(SIV96, 2937, "churches", "generic_place_class"),
]

NO_WRITE_TEXT = {
    "generic_palace": "Narrative or generic architectural reference; no individually identified building is meant.",
    "generic_place_class": "Plural or broad reference to churches; no individually identified site is meant.",
    "ordinary_school_days": "School refers to the painter's period of education, not an institution candidate.",
    "generic_art_school": "School denotes an art-historical circle, with no named school entity intended.",
    "generic_financial_condition": "General financial difficulty, not a named event, institution, or document.",
    "ordinary_character_quality": "Character is used as a general quality or emotional effect, not a distinct entity.",
    "generic_artwork_class": "Generic plural class of altarpieces; no specific work is identified by this span.",
    "generic_payment": "Ordinary payment in the narrative, not an independently identified entity.",
    "generic_genre": "Battle describes a painter's subject genre, not Salvator Rosa's indexed Battle work.",
    "generic_artist_income": "General artist earnings, not a distinct financial record or entity.",
    "ordinary_grammatical_subject": "Subject is part of the phrase 'subject to', not the patronal subject concept.",
    "ordinary_temperament": "Ordinary personal disposition, not the indexed concept-history use of temperament.",
}

EXPECTED_NO_WRITE_COUNTS = {
    "generic_palace": 1,
    "generic_place_class": 12,
    "ordinary_school_days": 1,
    "generic_art_school": 1,
    "generic_financial_condition": 2,
    "ordinary_character_quality": 2,
    "generic_artwork_class": 2,
    "generic_payment": 1,
    "generic_genre": 1,
    "generic_artist_income": 1,
    "ordinary_grammatical_subject": 1,
    "ordinary_temperament": 1,
}


def signature(item: dict[str, object]) -> tuple[str, int, int, str]:
    return (
        str(item["segment_id"]),
        int(item.get("start_char", item.get("prompt_start", 0))),
        int(item.get("end_char", item.get("prompt_end", 0))),
        str(item.get("surface_form", item.get("prompt_surface", ""))),
    )


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bytes]:
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if not reader.fieldnames:
        raise SystemExit(f"missing CSV header: {path}")
    return list(reader.fieldnames), list(reader), raw


def encode_csv(path: Path, fields: list[str], rows: list[dict[str, str]], raw_before: bytes) -> bytes:
    line_ending = "\r\n" if b"\r\n" in raw_before else "\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="raise", lineterminator=line_ending)
    writer.writeheader()
    writer.writerows(rows)
    payload = stream.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" + payload) if raw_before.startswith(b"\xef\xbb\xbf") else payload


def atomic_write(path: Path, payload: bytes) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="append the reviewed mentions after all preconditions pass")
    args = parser.parse_args()

    for relative, expected in EXPECTED_HASHES.items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit(f"source hash changed: {relative}: expected={expected} actual={actual}")

    summary, hits = surface_audit.audit("chp-3", 6)
    if summary.get("reviewed_segments_scanned") != 42 or len(hits) != 40:
        raise SystemExit(f"unexpected locator result: {summary}")
    hit_by_sig = {signature(hit): hit for hit in hits}
    if len(hit_by_sig) != len(hits):
        raise SystemExit("duplicate candidate-surface signatures in locator output")

    no_write_by_sig = {signature(item): item for item in NO_WRITE}
    if len(no_write_by_sig) != len(NO_WRITE):
        raise SystemExit("duplicate no-write signatures")
    reason_counts = Counter(item["reason"] for item in NO_WRITE)
    if dict(reason_counts) != EXPECTED_NO_WRITE_COUNTS:
        raise SystemExit(f"no-write reason counts changed: {dict(reason_counts)}")

    accepted_by_sig = {}
    for item in ACCEPTED:
        key = (
            str(item["segment_id"]), int(item["prompt_start"]),
            int(item["prompt_end"]), str(item["prompt_surface"]),
        )
        if key in accepted_by_sig:
            raise SystemExit(f"duplicate accepted prompt signature: {key}")
        accepted_by_sig[key] = item
    overlap = set(accepted_by_sig) & set(no_write_by_sig)
    if overlap:
        raise SystemExit(f"prompt both accepted and rejected: {sorted(overlap)}")
    expected_all = set(accepted_by_sig) | set(no_write_by_sig)
    actual_all = set(hit_by_sig)
    if actual_all != expected_all:
        raise SystemExit(
            "prompt partition mismatch; "
            f"missing={sorted(expected_all - actual_all)} extra={sorted(actual_all - expected_all)}"
        )
    for key, item in accepted_by_sig.items():
        if hit_by_sig[key]["surface_form"] != item["prompt_surface"]:
            raise SystemExit(f"accepted prompt text mismatch: {key}")

    candidate_fields, candidate_rows, _ = read_csv(CANDIDATES)
    mention_fields, mention_rows, mention_raw = read_csv(MENTIONS)
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    segments = {
        row["segment_id"]: row
        for row in (json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip())
    }
    source_cache: dict[str, str] = {}
    existing_natural_keys = {
        (row["segment_id"], int(row["start_char"]), int(row["end_char"])) for row in mention_rows
    }
    existing_ids = {row["mention_id"] for row in mention_rows}
    planned_natural_keys: set[tuple[str, int, int]] = set()
    planned_spans: list[tuple[str, int, int]] = []
    new_mentions: list[dict[str, str]] = []

    for item in ACCEPTED:
        segment_id = str(item["segment_id"])
        segment = segments.get(segment_id)
        if not segment:
            raise SystemExit(f"unknown segment: {segment_id}")
        if segment_id not in source_cache:
            source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8-sig").splitlines()
            source_cache[segment_id] = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
        source_text = source_cache[segment_id]
        prompt_start, prompt_end = int(item["prompt_start"]), int(item["prompt_end"])
        prompt_surface = str(item["prompt_surface"])
        if source_text[prompt_start:prompt_end] != prompt_surface:
            raise SystemExit(f"prompt source span mismatch: {segment_id} {prompt_start}:{prompt_end}")
        candidate_id = str(item["candidate_id"])
        candidate = candidate_by_id.get(candidate_id)
        if not candidate:
            raise SystemExit(f"unknown candidate: {candidate_id}")
        if not candidate["suggested_type"]:
            raise SystemExit(f"accepted mention target has no type: {candidate_id}")
        start, end = int(item["start_char"]), int(item["end_char"])
        surface = str(item["surface_form"])
        if source_text[start:end] != surface or start >= prompt_end or end <= prompt_start:
            raise SystemExit(f"accepted source span mismatch: {segment_id} {start}:{end} {surface!r}")
        natural_key = (segment_id, start, end)
        if natural_key in existing_natural_keys or natural_key in planned_natural_keys:
            raise SystemExit(f"mention natural key already present or planned: {natural_key}")
        for old in mention_rows:
            old_start, old_end = int(old["start_char"]), int(old["end_char"])
            if old["segment_id"] == segment_id and start < old_end and end > old_start:
                raise SystemExit(f"planned mention overlaps existing mention: {natural_key}")
        for old_segment, old_start, old_end in planned_spans:
            if old_segment == segment_id and start < old_end and end > old_start:
                raise SystemExit(f"planned mentions overlap: {natural_key}")
        digest = hashlib.sha256(f"{segment_id}|{start}|{end}|{candidate_id}".encode("utf-8")).hexdigest()[:16]
        mention_id = f"m-s2-chp3-surface-{digest}"
        if mention_id in existing_ids:
            raise SystemExit(f"mention ID already exists: {mention_id}")
        new_mentions.append({
            "mention_id": mention_id,
            "segment_id": segment_id,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(end),
            "note": str(item["note"]),
        })
        existing_ids.add(mention_id)
        planned_natural_keys.add(natural_key)
        planned_spans.append((segment_id, start, end))

    expected_residual = {
        key for key in no_write_by_sig
        if not any(
            segment_id == key[0] and start < key[2] and end > key[1]
            for segment_id, start, end in planned_spans
        )
    }
    if len(new_mentions) != 14 or len(expected_residual) != 26:
        raise SystemExit(f"unexpected write/residual counts: new_mentions={len(new_mentions)} residual={len(expected_residual)}")

    plan_sha = hashlib.sha256(json.dumps(
        {"accepted": ACCEPTED, "no_write": NO_WRITE, "no_write_reasons": NO_WRITE_TEXT},
        ensure_ascii=False, sort_keys=True,
    ).encode("utf-8")).hexdigest()
    print(f"chapter={summary['chapter']}")
    print(f"reviewed_segments_scanned={summary['reviewed_segments_scanned']}")
    print(f"candidate_surface_prompts={len(hits)}")
    print(f"accepted_prompt_signatures={len(ACCEPTED)}")
    print(f"new_mentions={len(new_mentions)}")
    print(f"no_write_prompt_signatures={len(NO_WRITE)}")
    for reason, count in sorted(reason_counts.items()):
        print(f"no_write[{reason}]={count}: {NO_WRITE_TEXT[reason]}")
    print(f"mentions_before={len(mention_rows)} mentions_after={len(mention_rows) + len(new_mentions)}")
    print(f"expected_post_write_prompts={len(expected_residual)}")
    print(f"plan_sha256={plan_sha}")
    if not args.apply:
        print("mode=dry-run; no files written")
        return 0

    recovery = Path(tempfile.gettempdir()) / ("pnp-s2-chp3-surface-prompts-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    recovery.mkdir(parents=True, exist_ok=False)
    backup = recovery / MENTIONS.name
    shutil.copy2(MENTIONS, backup)
    print(f"recovery_copy[mentions.csv]={backup}")
    payload = encode_csv(MENTIONS, mention_fields, mention_rows + new_mentions, mention_raw)
    try:
        atomic_write(MENTIONS, payload)
        post_summary, post_hits = surface_audit.audit("chp-3", 6)
        post_residual = {signature(hit) for hit in post_hits}
        if int(post_summary["uncovered_candidate_surface_spans"]) != len(expected_residual) or post_residual != expected_residual:
            raise RuntimeError(f"post-write prompt set mismatch: expected={sorted(expected_residual)} actual={sorted(post_residual)}")
        candidate_ids = {row["candidate_id"] for row in candidate_rows}
        written_mentions = read_csv(MENTIONS)[1]
        if any(row["candidate_id"] not in candidate_ids for row in written_mentions):
            raise RuntimeError("post-write mention has an unknown candidate FK")
        print(f"post_write_candidate_surface_prompts={len(post_residual)}")
        print("mode=apply; verification passed")
    except Exception:
        atomic_write(MENTIONS, backup.read_bytes())
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
