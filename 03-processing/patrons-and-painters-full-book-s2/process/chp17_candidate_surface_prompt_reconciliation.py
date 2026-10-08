#!/usr/bin/env python3
"""Reconcile Chapter 17 candidate-surface prompts against completed S2 evidence.

The locator is only a prompt source. The reviewed decisions below distinguish
the city, biblical figures, general narrative subjects, and unrelated index
hits. Default execution is a read-only preflight; pass --apply to write.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_s2_candidate_surfaces as surface_audit  # noqa: E402

TASK = ROOT / "03-processing" / "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"

EXPECTED_HASHES = {
    "04-knowledge/tables/entity-candidates.csv": "6023c8aa8fcc959e854a101728e655867417e0ba62b1d35f1915ad1030d77c83",
    "04-knowledge/tables/mentions.csv": "79dae349284d081e8f5fe222eb2214dcd251bebd4c1025ff16c7a6dabfb57d3a",
    "04-knowledge/tables/book-statements.jsonl": "39974e07b374feb299aa067cf1123f11e870f889e0059fdd2042668c0a4f50f2",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/s2-coverage.csv": "84f8497a7ce0100f4785acd8bf8ed88bb4c69fe5254cd89d172577b0400eb6c1",
    "02-sources/02-Markdown/17_CHP-17_sec_i.md": "cbcb4e8f0eb163564f0b0c8e060c79f1a48981db45072a772c3ea16642ad3ca4",
    "02-sources/02-Markdown/17_CHP-17_sec_ii.md": "d23af9f50ab9ac84fb250f5c7c5c260908096616ca83773a647977b8e07f4ff3",
    "scripts/audit_s2_candidate_surfaces.py": "130b53da86d940daad454079960415ac5e7043e0b71239370b66226158cd1ee2",
    "scripts/audit_tables.py": "066bbdcd5fc397713af266c0d1fe2bd23f2a66e7affa3ed797f2c104a8d3d5de",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "01-domain/stage-artifact-schema.md": "929b8a55f92103de962e8bd509d02d883683b0eea3a9ffe307e5de8229a86abe",
    "03-processing/patrons-and-painters-full-book-s2/process/stages.md": "96cebe56836cb2db1dd92c41d93a3a90b1f2a9fc48bfffbf415035016e36e9b2",
}

SEGMENT = "chp-17:17_CHP-17_sec_i:l22-24"
COMPETITION_STATEMENT = "st-chp17-p381-manfrin-competitions"
JOSEPH_MENTION = "m-s2-surface-c606f489f1a86215"

PROMPT_SIGNATURES = [
    (SEGMENT, 301, 307, "Venice"),
    (SEGMENT, 811, 820, "Bathsheba"),
    (SEGMENT, 830, 851, "Lot and his Daughters"),
    (SEGMENT, 853, 860, "Susanna"),
    (SEGMENT, 853, 875, "Susanna and the Elders"),
    ("chp-17:17_CHP-17_sec_i:l3-6", 1470, 1477, "fortune"),
    ("chp-17:17_CHP-17_sec_ii:l3-5", 214, 223, "character"),
    ("chp-17:17_CHP-17_sec_ii:l7-17", 2496, 2505, "portraits"),
]

NO_WRITE_REASONS = {
    6: "Fortune means Manfrin's wealth here; the index subentry is a specific Salvator Rosa painting at other pages.",
    7: "Character is a generic noun in the comparison of Correr and Manfrin, not the Barberini index subentry.",
    8: "Portraits of the clergy names a generic picture genre, not Schulenburg's indexed portrait group or a bounded set.",
}

SOURCE_REF = "chp-17:17_CHP-17_sec_i:l22-24#L24"

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-11503",
        "index_entry_id": "",
        "canonical_name": "Joseph and Potiphar's Wife as a biblical narrative subject in Manfrin's competition themes",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell lists this biblical narrative among the themes Manfrin devised for painting competitions. The passage does not identify a resulting painting or establish the narrative as a historical event. Keep this subject term distinct from the named figures and any individual work.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": SOURCE_REF,
    },
    {
        "candidate_id": "cand-11504",
        "index_entry_id": "",
        "canonical_name": "Potiphar (biblical figure named in Manfrin's p.381 competition theme)",
        "index_page_range": "",
        "suggested_type": "person",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Named through the possessive in Haskell's competition subject 'Potiphar's Wife'. This is a source-relative biblical figure mention, not evidence for an independent historical event or identified painting.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": SOURCE_REF,
    },
    {
        "candidate_id": "cand-11505",
        "index_entry_id": "",
        "canonical_name": "Bathsheba (biblical figure named in Manfrin's p.381 competition theme)",
        "index_page_range": "",
        "suggested_type": "person",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Named as a biblical figure within the competition theme 'Bathsheba bathing'. The source does not identify a competition painting; keep this figure distinct from same-titled works and from the general subject term.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": SOURCE_REF,
    },
    {
        "candidate_id": "cand-11506",
        "index_entry_id": "",
        "canonical_name": "Lot and his Daughters as a biblical narrative subject in Manfrin's competition themes",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell lists this biblical narrative among the themes Manfrin devised for painting competitions. The passage does not identify a resulting painting. Keep this subject term distinct from the Lot figure and from the separate Carlo Loth and Amigoni works named elsewhere.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": SOURCE_REF,
    },
    {
        "candidate_id": "cand-11507",
        "index_entry_id": "",
        "canonical_name": "Lot (biblical figure named in Manfrin's p.381 competition theme)",
        "index_page_range": "",
        "suggested_type": "person",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Named as a biblical figure within the competition theme 'Lot and his Daughters'. The daughters are unnamed in the passage and are not represented as a separate person or family candidate.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": SOURCE_REF,
    },
    {
        "candidate_id": "cand-11508",
        "index_entry_id": "",
        "canonical_name": "Susanna (biblical figure named in Manfrin's p.381 competition theme)",
        "index_page_range": "",
        "suggested_type": "person",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Named as a biblical figure within the competition theme 'Susanna and the Elders'. The passage does not identify a resulting painting; keep this figure distinct from the generic subject term and similarly titled works.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": SOURCE_REF,
    },
]

NEW_MENTIONS = [
    {
        "mention_id": "m-s2-chp17-surface-venice-p381",
        "segment_id": SEGMENT,
        "candidate_id": "cand-2719",
        "surface_form": "Venice",
        "start_char": "301",
        "end_char": "307",
        "note": "City named in the gallery evaluation, distinct from Venice inside the earlier painting title; reuse the index candidate whose page range covers p.381.",
    },
    {
        "mention_id": "m-s2-chp17-surface-joseph-potiphar-theme-p381",
        "segment_id": SEGMENT,
        "candidate_id": "cand-11503",
        "surface_form": "Joseph and Potiphars Wife",
        "start_char": "784",
        "end_char": "809",
        "note": "Narrative subject in Manfrin's proposed competition themes; source spelling is preserved, with the printed apostrophe correction recorded on the statement.",
    },
    {
        "mention_id": "m-s2-chp17-surface-potiphar-p381",
        "segment_id": SEGMENT,
        "candidate_id": "cand-11504",
        "surface_form": "Potiphars",
        "start_char": "795",
        "end_char": "804",
        "note": "Potiphar is named possessively in the subject phrase; the source OCR omits the printed apostrophe, already corrected in the statement qualifier.",
    },
    {
        "mention_id": "m-s2-chp17-surface-bathsheba-person-p381",
        "segment_id": SEGMENT,
        "candidate_id": "cand-11505",
        "surface_form": "Bathsheba",
        "start_char": "811",
        "end_char": "820",
        "note": "Biblical figure named within the competition theme; keep distinct from paintings attributed to Maratta or Amigoni.",
    },
    {
        "mention_id": "m-s2-chp17-surface-bathsheba-theme-p381",
        "segment_id": SEGMENT,
        "candidate_id": "cand-8438",
        "surface_form": "Bathsheba bathing",
        "start_char": "811",
        "end_char": "828",
        "note": "Reuses the existing general subject term; this occurrence names a competition theme, not an identified picture.",
    },
    {
        "mention_id": "m-s2-chp17-surface-lot-theme-p381",
        "segment_id": SEGMENT,
        "candidate_id": "cand-11506",
        "surface_form": "Lot and his Daughters",
        "start_char": "830",
        "end_char": "851",
        "note": "Narrative subject in Manfrin's proposed competition themes; no resulting work is identified.",
    },
    {
        "mention_id": "m-s2-chp17-surface-lot-person-p381",
        "segment_id": SEGMENT,
        "candidate_id": "cand-11507",
        "surface_form": "Lot",
        "start_char": "830",
        "end_char": "833",
        "note": "Biblical figure named at the start of the competition subject; the daughters are unnamed.",
    },
    {
        "mention_id": "m-s2-chp17-surface-susanna-person-p381",
        "segment_id": SEGMENT,
        "candidate_id": "cand-11508",
        "surface_form": "Susanna",
        "start_char": "853",
        "end_char": "860",
        "note": "Biblical figure named within the competition theme; distinct from St Susanna and from specific paintings.",
    },
    {
        "mention_id": "m-s2-chp17-surface-susanna-theme-p381",
        "segment_id": SEGMENT,
        "candidate_id": "cand-8439",
        "surface_form": "Susanna and the Elders",
        "start_char": "853",
        "end_char": "875",
        "note": "Reuses the existing general subject term; this occurrence names a competition theme, not an identified picture.",
    },
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_hashes() -> None:
    changed = {}
    for relative, expected in EXPECTED_HASHES.items():
        actual = sha256((ROOT / relative).read_bytes())
        if actual != expected:
            changed[relative] = {"expected": expected, "actual": actual}
    if changed:
        raise RuntimeError(f"Locked inputs changed; re-review before writing: {json.dumps(changed, ensure_ascii=False)}")


def read_csv(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    return raw, list(reader.fieldnames or []), list(reader)


def append_csv_rows(raw: bytes, columns: list[str], rows: list[dict[str, object]]) -> bytes:
    if not rows:
        return raw
    eol = b"\r\n" if b"\r\n" in raw else b"\n"
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=columns, extrasaction="raise", lineterminator=eol.decode("ascii"))
    for row in rows:
        writer.writerow(row)
    prefix = b"" if raw.endswith((b"\n", b"\r")) else eol
    return raw + prefix + buffer.getvalue().encode("utf-8")


def patch_csv_row(
    raw: bytes,
    columns: list[str],
    rows: list[dict[str, str]],
    key: str,
    identifier: str,
    patch: dict[str, str],
) -> tuple[bytes, dict[str, str]]:
    text = raw.decode("utf-8-sig")
    lines = text.splitlines(keepends=True)
    reader = csv.reader(io.StringIO(text, newline=""))
    header = next(reader)
    if header != columns:
        raise ValueError("CSV header changed while locating the record")
    key_index = columns.index(key)
    start_line = reader.line_num
    match = None
    for record in reader:
        end_line = reader.line_num
        if len(record) != len(columns):
            raise ValueError("Malformed CSV record encountered while locating the target")
        if record[key_index] == identifier:
            if match is not None:
                raise ValueError(f"Expected one {key}={identifier}, found multiple")
            match = (start_line, end_line)
        start_line = end_line
    if match is None:
        raise ValueError(f"Expected one {key}={identifier}, found none")
    row_match = [row for row in rows if row.get(key) == identifier]
    if len(row_match) != 1:
        raise ValueError(f"Parsed CSV records disagree on {key}={identifier}")
    updated = dict(row_match[0])
    for field, expected in {"candidate_id": "cand-3428", "surface_form": "Joseph", "start_char": "784", "end_char": "790"}.items():
        if updated.get(field) != expected:
            raise ValueError(f"Unexpected prior Joseph mention {field}: {updated.get(field)!r}")
    updated.update(patch)
    buffer = io.StringIO(newline="")
    eol = "\r\n" if "\r\n" in text else "\n"
    csv.DictWriter(buffer, fieldnames=columns, extrasaction="raise", lineterminator=eol).writerow(updated)
    record_start, record_end = match
    lines[record_start:record_end] = [buffer.getvalue()]
    output = "".join(lines)
    if raw.startswith(b"\xef\xbb\xbf"):
        output = "\ufeff" + output
    return output.encode("utf-8"), updated


def json_bytes(row: dict[str, object]) -> str:
    return json.dumps(row, ensure_ascii=False, separators=(",", ":"))


def update_statement(raw: bytes) -> bytes:
    text = raw.decode("utf-8-sig")
    eol = "\r\n" if "\r\n" in text else "\n"
    output = []
    found = 0
    for line in text.splitlines():
        row = json.loads(line)
        if row.get("statement_id") != COMPETITION_STATEMENT:
            output.append(line)
            continue
        found += 1
        qualifiers = row["qualifiers"]
        expected_subjects = [
            "Joseph and Potiphar’s Wife",
            "Bathsheba bathing",
            "Lot and his Daughters",
            "Susanna and the Elders",
        ]
        if qualifiers.get("competition_subjects") != expected_subjects:
            raise ValueError("The Chapter 17 competition subjects changed; re-review before writing")
        expected_refs = ["cand-1512", "cand-0817", "cand-1313"]
        if qualifiers.get("mentioned_candidate_ids") != expected_refs:
            raise ValueError(f"Unexpected prior competition candidate refs: {qualifiers.get('mentioned_candidate_ids')}")
        qualifiers["qualification"] = (
            "The four named biblical subjects are themes Manfrin devised for competitions, not identified competition outputs. "
            "Narrative subjects are kept distinct from named biblical figures and from same-titled works elsewhere; the source does not say that any competition picture was completed."
        )
        qualifiers["mentioned_candidate_ids"] = expected_refs + [
            "cand-11503",
            "cand-4140",
            "cand-11504",
            "cand-8438",
            "cand-11505",
            "cand-11506",
            "cand-11507",
            "cand-8439",
            "cand-11508",
        ]
        output.append(json_bytes(row))
    if found != 1:
        raise ValueError(f"Expected one competition statement, found {found}")
    if raw.startswith(b"\xef\xbb\xbf"):
        return ("\ufeff" + eol.join(output) + eol).encode("utf-8")
    return (eol.join(output) + eol).encode("utf-8")


def candidate_rows_by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    result = {}
    for row in rows:
        candidate_id = row["candidate_id"]
        if candidate_id in result:
            raise ValueError(f"Duplicate candidate ID: {candidate_id}")
        result[candidate_id] = row
    return result


def mention_rows_by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    result = {}
    for row in rows:
        mention_id = row["mention_id"]
        if mention_id in result:
            raise ValueError(f"Duplicate mention ID: {mention_id}")
        result[mention_id] = row
    return result


def build_plan() -> dict[str, object]:
    summary, prompts = surface_audit.audit("chp-17", 6)
    signatures = [
        (str(hit["segment_id"]), int(hit["start_char"]), int(hit["end_char"]), str(hit["surface_form"]))
        for hit in prompts
    ]
    if summary["reviewed_segments_scanned"] != 10 or signatures != PROMPT_SIGNATURES:
        raise ValueError(f"Chapter 17 prompt surface changed; re-review before writing: {summary} {signatures}")

    candidate_raw, candidate_columns, candidates = read_csv(CANDIDATES)
    mention_raw, mention_columns, mentions = read_csv(MENTIONS)
    statement_raw = STATEMENTS.read_bytes()
    existing_candidates = candidate_rows_by_id(candidates)
    existing_mentions = mention_rows_by_id(mentions)

    required_candidates = {
        "cand-2719": ("place", "Venice"),
        "cand-4140": ("person", "Joseph (son of Jacob)"),
        "cand-8438": ("term", "Bathsheba bathing as an erotic painting subject in Haskell's comparison"),
        "cand-8439": ("term", "Susanna and the Elders as an erotic painting subject in Haskell's comparison"),
    }
    for candidate_id, (expected_type, expected_name) in required_candidates.items():
        row = existing_candidates.get(candidate_id)
        if not row or row.get("suggested_type") != expected_type or row.get("canonical_name") != expected_name:
            raise ValueError(f"Required candidate changed or missing: {candidate_id}")
    page_range = existing_candidates["cand-2719"].get("index_page_range", "")
    covered_pages = {int(page) for page in re.findall(r"\d+", page_range)}
    for start, end in re.findall(r"(\d+)\s*[-–—]\s*(\d+)", page_range):
        covered_pages.update(range(int(start), int(end) + 1))
    if 381 not in covered_pages:
        raise ValueError("Venice index candidate no longer covers p.381")

    current_joseph = existing_mentions.get(JOSEPH_MENTION)
    if not current_joseph:
        raise ValueError(f"Joseph mention missing: {JOSEPH_MENTION}")
    if current_joseph.get("segment_id") != SEGMENT:
        raise ValueError("Joseph mention moved from the reviewed Chapter 17 segment")

    new_candidate_ids = [row["candidate_id"] for row in NEW_CANDIDATES]
    if new_candidate_ids != [f"cand-{number}" for number in range(11503, 11509)]:
        raise ValueError(f"Unexpected Chapter 17 candidate IDs: {new_candidate_ids}")
    collision_candidates = sorted(set(new_candidate_ids) & set(existing_candidates))
    if collision_candidates:
        raise ValueError(f"New candidate IDs already exist: {collision_candidates}")
    new_mention_ids = [row["mention_id"] for row in NEW_MENTIONS]
    collision_mentions = sorted(set(new_mention_ids) & set(existing_mentions))
    if collision_mentions:
        raise ValueError(f"New mention IDs already exist: {collision_mentions}")

    source_path = ROOT / "02-sources" / "02-Markdown" / "17_CHP-17_sec_i.md"
    source_lines = source_path.read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[21:24])
    span_checks = [
        ("Venice", 301, 307),
        ("Joseph and Potiphars Wife", 784, 809),
        ("Potiphars", 795, 804),
        ("Bathsheba", 811, 820),
        ("Bathsheba bathing", 811, 828),
        ("Lot and his Daughters", 830, 851),
        ("Lot", 830, 833),
        ("Susanna", 853, 860),
        ("Susanna and the Elders", 853, 875),
    ]
    for surface, start, end in span_checks:
        if source_text[start:end] != surface:
            raise ValueError(f"Source span changed: {surface} {start}:{end} -> {source_text[start:end]!r}")

    mention_after_joseph, _ = patch_csv_row(
        mention_raw,
        mention_columns,
        mentions,
        "mention_id",
        JOSEPH_MENTION,
        {
            "candidate_id": "cand-4140",
            "note": "The competition theme identifies the biblical Joseph son of Jacob; keep distinct from St Joseph cand-3428.",
        },
    )
    mention_after = append_csv_rows(mention_after_joseph, mention_columns, NEW_MENTIONS)
    candidate_after = append_csv_rows(candidate_raw, candidate_columns, NEW_CANDIDATES)
    statement_after = update_statement(statement_raw)

    outputs = {
        CANDIDATES: candidate_after,
        MENTIONS: mention_after,
        STATEMENTS: statement_after,
    }
    before_hashes = {path.name: sha256(path.read_bytes()) for path in outputs}
    after_hashes = {path.name: sha256(data) for path, data in outputs.items()}
    plan_payload = {
        "chapter": "chp-17",
        "scanner_summary": summary,
        "prompt_signatures": signatures,
        "no_write_reasons": NO_WRITE_REASONS,
        "new_candidates": NEW_CANDIDATES,
        "new_mentions": NEW_MENTIONS,
        "repointed_mention": JOSEPH_MENTION,
        "updated_statement": COMPETITION_STATEMENT,
        "before_hashes": before_hashes,
        "after_hashes": after_hashes,
    }
    return {
        "scanner_summary": summary,
        "prompts": prompts,
        "outputs": outputs,
        "before_hashes": before_hashes,
        "after_hashes": after_hashes,
        "plan_hash": sha256(json.dumps(plan_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")),
    }


def atomic_write(path: Path, data: bytes) -> None:
    import os

    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def apply_plan(plan: dict[str, object]) -> dict[str, object]:
    recovery = Path(tempfile.gettempdir()) / f"pnp-s2-chp17-surface-prompts-{datetime.now():%Y%m%d-%H%M%S}"
    recovery.mkdir(parents=True, exist_ok=False)
    for path in plan["outputs"]:
        shutil.copy2(path, recovery / path.name)
    try:
        for path, data in plan["outputs"].items():
            atomic_write(path, data)

        after_summary, remaining = surface_audit.audit("chp-17", 6)
        expected_remaining = {
            PROMPT_SIGNATURES[index - 1]
            for index in NO_WRITE_REASONS
        }
        actual_remaining = {
            (str(hit["segment_id"]), int(hit["start_char"]), int(hit["end_char"]), str(hit["surface_form"]))
            for hit in remaining
        }
        if actual_remaining != expected_remaining:
            raise RuntimeError(
                f"Post-write prompts differ from no-write residue: "
                f"missing={sorted(expected_remaining-actual_remaining)}; extra={sorted(actual_remaining-expected_remaining)}"
            )

        audit_run = subprocess.run(
            [sys.executable, "-X", "utf8", "scripts/audit_tables.py", "--strict-stage"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        strict_audit = json.loads(audit_run.stdout)
        if strict_audit.get("errors") or strict_audit.get("s2_missing"):
            raise RuntimeError(f"Strict S2 audit failed: {strict_audit}")
        if strict_audit.get("candidates") != 11487 or strict_audit.get("mentions") != 27371 or strict_audit.get("book_statements") != 12263:
            raise RuntimeError(f"Unexpected post-write table counts: {strict_audit}")
        relation_candidate_count = sum(
            1
            for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines()
            if line and json.loads(line).get("qualifiers", {}).get("relation_candidate") is True
        )
        if relation_candidate_count != 2331:
            raise RuntimeError(f"Relation candidate count changed unexpectedly: {relation_candidate_count}")
        return {
            "post_write_scanner": after_summary,
            "remaining_prompts_match_no_write_residue": True,
            "strict_audit": strict_audit,
            "relation_candidate_count": relation_candidate_count,
            "after_hashes": {path.name: sha256(data) for path, data in plan["outputs"].items()},
            "recovery_directory": str(recovery),
        }
    except Exception:
        for path in plan["outputs"]:
            shutil.copy2(recovery / path.name, path)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the locked and preflighted S2 decisions")
    args = parser.parse_args()
    verify_hashes()
    plan = build_plan()
    print(
        json.dumps(
            {
                "mode": "apply" if args.apply else "dry-run",
                "scanner": plan["scanner_summary"],
                "new_candidates": [row["candidate_id"] for row in NEW_CANDIDATES],
                "new_mentions": [row["mention_id"] for row in NEW_MENTIONS],
                "repointed_mention": JOSEPH_MENTION,
                "updated_statement": COMPETITION_STATEMENT,
                "no_write_prompts": sorted(NO_WRITE_REASONS),
                "before_hashes": plan["before_hashes"],
                "planned_after_hashes": plan["after_hashes"],
                "plan_sha256": plan["plan_hash"],
            },
            ensure_ascii=False,
        )
    )
    if not args.apply:
        return 0
    print(json.dumps(apply_plan(plan), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
