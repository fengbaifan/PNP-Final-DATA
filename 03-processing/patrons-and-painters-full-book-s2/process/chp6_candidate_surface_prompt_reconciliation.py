"""Semantically adjudicate the 23 current Chapter 6 surface prompts.

The locator is only a heuristic. This locked reconciliation records exact
mentions that refer to reusable source objects and individual no-write
decisions for generic language and mismatched index labels. It writes only
after all source, partition, span, and foreign-key checks pass.
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
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
sys.path.insert(0, str(ROOT / "scripts"))
import audit_s2_candidate_surfaces as surface_audit

EXPECTED_HASHES = {
    "04-knowledge/tables/entity-candidates.csv": "465463a534129239b1ec06ad0f2614cc8e553cd7639d3a1ce56911e33e06ae23",
    "04-knowledge/tables/mentions.csv": "c43354eddb206f135ba3b638d4a4949e74dae129c4bbeb30158daf2a219c7541",
    "04-knowledge/tables/book-statements.jsonl": "5999d2851d45c5b0ab2157478d8926d0ca4fc5aa1abcbcae164aab2ebdd9c1a6",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/s2-coverage.csv": "84f8497a7ce0100f4785acd8bf8ed88bb4c69fe5254cd89d172577b0400eb6c1",
    "scripts/audit_s2_candidate_surfaces.py": "44874e88e4940af624ad7b91b6f3e7d016f8c4083c203114e354b6e6622901ba",
    "02-sources/02-Markdown/01_CHP-1_sec_ii.md": "1b5890ce028c421718abcb28e4c6dc4070be1bc71597a96247b32ebee42e2268",
    "02-sources/02-Markdown/04_CHP-4_sec_i.md": "3961adefb7ea2e1f2e44e02173a494c509964e7273b6b3867619643bbd9ecb64",
    "02-sources/02-Markdown/06_CHP-6_intro.md": "ea2413fc5e957515a60e7284a1e1410f27dbe4bffaa4edaf896ff8cc96db4678",
    "02-sources/02-Markdown/06_CHP-6_sec_i.md": "e1bf27cf13961032d4587a1787a1b89f00a9076cf7a8c9dd4434000e84add42d",
    "02-sources/02-Markdown/06_CHP-6_sec_iv.md": "65de7b08cd2bad4cbf783d807160ef15e80cb031a47e1f28a6cb6c0f2b29e775",
    "02-sources/02-Markdown/06_CHP-6_sec_v.md": "724f421d1c98612a8820404c82dda956dadaf6006483fcdf394cc53af4e72d15",
}

INTRO = "chp-6:06_CHP-6_intro:l7-11"
SI13 = "chp-6:06_CHP-6_sec_i:l13-24"
SI26 = "chp-6:06_CHP-6_sec_i:l26-36"
SI3 = "chp-6:06_CHP-6_sec_i:l3-11"
SI38 = "chp-6:06_CHP-6_sec_i:l38-46"
SI59 = "chp-6:06_CHP-6_sec_i:l59-67"
SI69 = "chp-6:06_CHP-6_sec_i:l69-76"
SI91 = "chp-6:06_CHP-6_sec_i:l91-100"
SI102 = "chp-6:06_CHP-6_sec_i:l102-110"
SI120 = "chp-6:06_CHP-6_sec_i:l120-157"
SIV40 = "chp-6:06_CHP-6_sec_iv:l40-50"
SIV55 = "chp-6:06_CHP-6_sec_iv:l55-72"
SV14 = "chp-6:06_CHP-6_sec_v:l14-19"
SV28 = "chp-6:06_CHP-6_sec_v:l28-33"
SV42 = "chp-6:06_CHP-6_sec_v:l42-45"
SV47 = "chp-6:06_CHP-6_sec_v:l47-70"


def accepted(segment_id: str, start: int, surface: str, candidate_id: str,
             note: str, mention_surface: str | None = None,
             mention_start: int | None = None) -> dict[str, object]:
    target = mention_surface if mention_surface is not None else surface
    target_start = mention_start if mention_start is not None else start
    return {
        "segment_id": segment_id,
        "prompt_start": start,
        "prompt_end": start + len(surface),
        "prompt_surface": surface,
        "candidate_id": candidate_id,
        "surface_form": target,
        "start_char": target_start,
        "end_char": target_start + len(target),
        "note": note,
    }


def no_write(segment_id: str, start: int, surface: str, reason: str) -> dict[str, object]:
    return {"segment_id": segment_id, "start_char": start,
            "end_char": start + len(surface), "surface_form": surface,
            "reason": reason}


ACCEPTED = [
    accepted(INTRO, 186, "in Rome", "cand-3126",
             "The prompt includes a preposition; the exact city mention is only Rome.",
             mention_surface="Rome", mention_start=189),
    accepted(SI120, 1937, "in Rome", "cand-3126",
             "The cited catalogue was published in the named city; record only the exact city span.",
             mention_surface="Rome", mention_start=1940),
    accepted(SI120, 2438, "collection", "cand-6389",
             "The note refers to Antonio degli Effetti’s collection. Reuse its existing type-pending collection candidate; the inventory’s exact relation and collection boundaries remain unresolved."),
    accepted(SIV40, 2681, "collection", "cand-5565",
             "This is the same Queen Christina picture gallery already described as looted from Prague; reuse its type-pending collection candidate."),
    accepted(SIV55, 261, "foreign travellers", "cand-3562",
             "The phrase denotes the same generic actor category as in Chapter 1. It describes visitors here; it does not identify individuals or claim the same travellers."),
    accepted(SIV55, 1287, "Renaissance", "cand-3578",
             "The word denotes the same broad historical and artistic period represented by the existing term candidate."),
    accepted(SV47, 1217, "theatre", "cand-6545",
             "Footnote 3’s ‘this theatre’ refers to the Ottoboni theatre introduced in the linked p.164 passage; reuse its venue candidate."),
    accepted(SV47, 2062, "in Rome", "cand-3126",
             "The locator phrase includes a preposition; record only the city Rome.",
             mention_surface="Rome", mention_start=2065),
]

NO_WRITE = [
    no_write(SI102, 2328, "subject", "generic_art_subject"),
    no_write(SI102, 2811, "drawings", "generic_art_category"),
    no_write(SI13, 2135, "palace", "generic_architecture"),
    no_write(SI26, 11, "character", "architectural_quality"),
    no_write(SI3, 2243, "temperament", "ordinary_personality_quality"),
    no_write(SI38, 838, "financial difficulties", "economic_condition"),
    no_write(SI59, 2310, "churches", "generic_building_list"),
    no_write(SI59, 2856, "churches", "generic_building_class"),
    no_write(SI69, 3185, "garden", "metaphorical_reference"),
    no_write(SI91, 2635, "portraits", "generic_portrait_class"),
    no_write(SIV55, 2403, "poetry", "generic_literary_genre"),
    no_write(SV14, 656, "prices", "generic_market_measure"),
    no_write(SV28, 1277, "operatic librettos", "compositional_activity"),
    no_write(SV28, 1827, "character", "ordinary_personality_quality"),
    no_write(SV42, 143, "subject", "generic_art_subject"),
]

NO_WRITE_TEXT = {
    "generic_art_subject": "The phrase describes the subject matter of a picture, not a distinct entity or the indexed contracts/subject term.",
    "generic_art_category": "This is a broad artwork class; the passage does not identify a particular work or bounded group.",
    "generic_architecture": "The ‘usual great family palace’ is a generic building category, not an identifiable palace.",
    "architectural_quality": "‘Character’ describes the quality of buildings, not a person, work, or other independent object.",
    "ordinary_personality_quality": "The word describes disposition or character, not an independent entity.",
    "economic_condition": "This is a financial state affecting named parties, not a distinct object or event.",
    "generic_building_list": "The plural occurs in a general list of new construction; no individual church is identified.",
    "generic_building_class": "‘Other churches’ is a generic class of patronised buildings with no bounded or named set.",
    "metaphorical_reference": "The garden occurs in Rosa’s metaphor about abandoning painting, not as a referenced place.",
    "generic_portrait_class": "The sentence names a broad category of Gaulli’s pictures, not a specific portrait or bounded group; it is separate from the expressly counted ceiling group of thirty-six women.",
    "generic_literary_genre": "Poetry is a broad literary genre in a general statement; no text or bounded corpus is identified.",
    "generic_market_measure": "Prices describe a general economic condition affecting crops, not a separately identified entity.",
    "compositional_activity": "Ottoboni’s description as a composer of operatic librettos states a general activity; no title or bounded body of texts is identified. The matched archive candidate belongs to Pope Clement IX and is not this referent.",
}

EXPECTED_NO_WRITE_COUNTS = {
    "generic_art_subject": 2,
    "generic_art_category": 1,
    "generic_architecture": 1,
    "architectural_quality": 1,
    "ordinary_personality_quality": 2,
    "economic_condition": 1,
    "generic_building_list": 1,
    "generic_building_class": 1,
    "metaphorical_reference": 1,
    "generic_portrait_class": 1,
    "generic_literary_genre": 1,
    "generic_market_measure": 1,
    "compositional_activity": 1,
}

MENTIONED_CANDIDATE_ADDITIONS = {
    "st-chp6-notes-l157-p156-n2": ["cand-6389"],
    "st-chp6-p164-n3-cite": ["cand-6545"],
}

QUALIFICATION_UPDATES = {
    "st-chp6-p164-v1-14": {
        "expected": "The theatre is unnamed and footnote 3 remains pending.",
        "replacement": "The theatre is unnamed in this p.164 passage. Footnote 3 supplies a Rava 1942 citation locator, but that source has not been independently consulted.",
    }
}


def signature(item: dict[str, object]) -> tuple[str, int, int, str]:
    return (str(item["segment_id"]),
            int(item.get("start_char", item.get("prompt_start", 0))),
            int(item.get("end_char", item.get("prompt_end", 0))),
            str(item.get("surface_form", item.get("prompt_surface", ""))))


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bytes]:
    raw = path.read_bytes()
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    if not reader.fieldnames:
        raise SystemExit(f"missing CSV header: {path}")
    return list(reader.fieldnames), list(reader), raw


def encode_csv(fields: list[str], rows: list[dict[str, str]], raw_before: bytes) -> bytes:
    ending = "\r\n" if b"\r\n" in raw_before else "\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="raise", lineterminator=ending)
    writer.writeheader()
    writer.writerows(rows)
    payload = stream.getvalue().encode("utf-8")
    return b"\xef\xbb\xbf" + payload if raw_before.startswith(b"\xef\xbb\xbf") else payload


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
    parser.add_argument("--apply", action="store_true", help="write the locked mention and statement reconciliation")
    args = parser.parse_args()

    for relative, expected in EXPECTED_HASHES.items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit(f"source hash changed: {relative}: expected={expected} actual={actual}")

    summary, hits = surface_audit.audit("chp-6", 6)
    if summary.get("reviewed_segments_scanned") != 28 or len(hits) != 23:
        raise SystemExit(f"unexpected locator result: {summary}")
    hit_by_sig = {signature(hit): hit for hit in hits}
    no_write_by_sig = {signature(item): item for item in NO_WRITE}
    reason_counts = Counter(str(item["reason"]) for item in NO_WRITE)
    accepted_by_sig = {}
    for item in ACCEPTED:
        key = (str(item["segment_id"]), int(item["prompt_start"]),
               int(item["prompt_end"]), str(item["prompt_surface"]))
        if key in accepted_by_sig:
            raise SystemExit(f"duplicate accepted signature: {key}")
        accepted_by_sig[key] = item
    if len(no_write_by_sig) != len(NO_WRITE) or dict(reason_counts) != EXPECTED_NO_WRITE_COUNTS:
        raise SystemExit(f"no-write plan changed: {dict(reason_counts)}")
    if set(accepted_by_sig) & set(no_write_by_sig):
        raise SystemExit("prompt marked both accepted and no-write")
    if set(hit_by_sig) != set(accepted_by_sig) | set(no_write_by_sig):
        raise SystemExit("prompt partition mismatch: "
                         f"missing={sorted((set(accepted_by_sig)|set(no_write_by_sig))-set(hit_by_sig))} "
                         f"extra={sorted(set(hit_by_sig)-(set(accepted_by_sig)|set(no_write_by_sig)))}")
    for key, item in accepted_by_sig.items():
        if hit_by_sig[key]["surface_form"] != item["prompt_surface"]:
            raise SystemExit(f"accepted source prompt mismatch: {key}")

    candidate_rows = read_csv(TABLES / "entity-candidates.csv")[1]
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    if len(candidate_by_id) != len(candidate_rows):
        raise SystemExit("duplicate candidate IDs")
    expected_types = {
        "cand-3126": "place", "cand-6389": "", "cand-5565": "",
        "cand-3562": "term", "cand-3578": "term", "cand-6545": "place",
    }
    for candidate_id, expected_type in expected_types.items():
        if candidate_id not in candidate_by_id:
            raise SystemExit(f"planned candidate does not exist: {candidate_id}")
        if candidate_by_id[candidate_id]["suggested_type"] != expected_type:
            raise SystemExit(f"candidate type changed: {candidate_id}")

    mention_fields, mention_rows, mention_raw = read_csv(MENTIONS)
    statement_raw = STATEMENTS.read_bytes()
    statement_text = statement_raw.decode("utf-8-sig")
    statement_lines = statement_text.splitlines()
    segments = {
        row["segment_id"]: row
        for row in (json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip())
    }
    existing_keys = {(row["segment_id"], int(row["start_char"]), int(row["end_char"])) for row in mention_rows}
    existing_ids = {row["mention_id"] for row in mention_rows}
    planned_keys: set[tuple[str, int, int]] = set()
    planned_spans: list[tuple[str, int, int]] = []
    new_mentions: list[dict[str, str]] = []
    source_cache: dict[str, str] = {}
    for item in ACCEPTED:
        segment_id = str(item["segment_id"])
        segment = segments.get(segment_id)
        if not segment:
            raise SystemExit(f"unknown segment: {segment_id}")
        if segment_id not in source_cache:
            lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8-sig").splitlines()
            source_cache[segment_id] = "\n".join(lines[segment["line_start"] - 1:segment["line_end"]])
        text = source_cache[segment_id]
        candidate_id = str(item["candidate_id"])
        start, end, surface = int(item["start_char"]), int(item["end_char"]), str(item["surface_form"])
        prompt_start, prompt_end = int(item["prompt_start"]), int(item["prompt_end"])
        if text[start:end] != surface:
            raise SystemExit(f"planned mention source span mismatch: {segment_id} {start}:{end} {surface!r}")
        if text[prompt_start:prompt_end] != str(item["prompt_surface"]):
            raise SystemExit(f"prompt source span mismatch: {segment_id} {prompt_start}:{prompt_end}")
        if candidate_id not in candidate_by_id:
            raise SystemExit(f"unknown planned candidate: {candidate_id}")
        if start >= prompt_end or end <= prompt_start:
            raise SystemExit(f"mention does not overlap accepted prompt: {segment_id} {start}:{end}")
        natural_key = (segment_id, start, end)
        if natural_key in existing_keys or natural_key in planned_keys:
            raise SystemExit(f"mention span already present or planned: {natural_key}")
        for old in mention_rows:
            old_start, old_end = int(old["start_char"]), int(old["end_char"])
            if old["segment_id"] == segment_id and start < old_end and end > old_start:
                raise SystemExit(f"planned mention overlaps existing mention: {natural_key}")
        for old_segment, old_start, old_end in planned_spans:
            if old_segment == segment_id and start < old_end and end > old_start:
                raise SystemExit(f"planned mentions overlap: {natural_key}")
        digest = hashlib.sha256(f"{segment_id}|{start}|{end}|{candidate_id}".encode("utf-8")).hexdigest()[:16]
        mention_id = f"m-s2-chp6-surface-{digest}"
        if mention_id in existing_ids:
            raise SystemExit(f"mention ID already exists: {mention_id}")
        new_mentions.append({
            "mention_id": mention_id, "segment_id": segment_id,
            "candidate_id": candidate_id, "surface_form": surface,
            "start_char": str(start), "end_char": str(end), "note": str(item["note"]),
        })
        existing_ids.add(mention_id)
        planned_keys.add(natural_key)
        planned_spans.append(natural_key)
    if len(new_mentions) != len(ACCEPTED):
        raise SystemExit(f"unexpected mention write count: {len(new_mentions)}")

    statement_rows = []
    statement_by_id = {}
    changed_statement_lines = []
    for i, line in enumerate(statement_lines):
        row = json.loads(line)
        statement_id = row.get("statement_id")
        if statement_id in statement_by_id:
            raise SystemExit(f"duplicate statement ID: {statement_id}")
        statement_by_id[statement_id] = row
        if statement_id in MENTIONED_CANDIDATE_ADDITIONS:
            qualifiers = row.setdefault("qualifiers", {})
            ids = qualifiers.setdefault("mentioned_candidate_ids", [])
            for candidate_id in MENTIONED_CANDIDATE_ADDITIONS[statement_id]:
                if candidate_id not in candidate_by_id:
                    raise SystemExit(f"statement qualifier references unknown candidate: {statement_id} {candidate_id}")
                if candidate_id not in ids:
                    ids.append(candidate_id)
            changed_statement_lines.append(i)
        if statement_id in QUALIFICATION_UPDATES:
            qualifiers = row.setdefault("qualifiers", {})
            update = QUALIFICATION_UPDATES[statement_id]
            if qualifiers.get("qualification") != update["expected"]:
                raise SystemExit(f"statement qualification precondition changed: {statement_id}")
            qualifiers["qualification"] = update["replacement"]
            changed_statement_lines.append(i)
        statement_rows.append(row)
    required_statement_ids = set(MENTIONED_CANDIDATE_ADDITIONS) | set(QUALIFICATION_UPDATES)
    if required_statement_ids - set(statement_by_id):
        raise SystemExit(f"missing statement update targets: {sorted(required_statement_ids-set(statement_by_id))}")
    if len(set(changed_statement_lines)) != len(required_statement_ids):
        raise SystemExit("statement update count changed")

    residual = set(no_write_by_sig)
    plan_sha = hashlib.sha256(json.dumps(
        {"accepted": ACCEPTED, "no_write": NO_WRITE,
         "no_write_reasons": NO_WRITE_TEXT,
         "mentioned_candidate_additions": MENTIONED_CANDIDATE_ADDITIONS,
         "qualification_updates": QUALIFICATION_UPDATES},
        ensure_ascii=False, sort_keys=True,
    ).encode("utf-8")).hexdigest()

    print("chapter=chp-6")
    print(f"reviewed_segments_scanned={summary['reviewed_segments_scanned']}")
    print(f"candidate_surface_prompts={len(hits)}")
    print(f"accepted_prompt_signatures={len(ACCEPTED)}")
    print(f"new_mentions={len(new_mentions)}")
    print("new_candidates=0; all accepted targets reuse existing candidate IDs")
    print(f"no_write_prompt_signatures={len(NO_WRITE)}")
    for reason, count in sorted(reason_counts.items()):
        print(f"no_write[{reason}]={count}: {NO_WRITE_TEXT[reason]}")
    print(f"candidate_rows={len(candidate_rows)} mention_rows_before={len(mention_rows)} mention_rows_after={len(mention_rows)+len(new_mentions)}")
    print(f"statement_rows={len(statement_rows)} updated_statements={len(required_statement_ids)}")
    print(f"expected_post_write_prompts={len(residual)}")
    print(f"plan_sha256={plan_sha}")
    if not args.apply:
        print("mode=dry-run; no files written")
        return 0

    mention_payload = encode_csv(mention_fields, mention_rows + new_mentions, mention_raw)
    newline = "\r\n" if b"\r\n" in statement_raw else "\n"
    statement_payload = newline.join(
        json.dumps(row, ensure_ascii=False) if i in set(changed_statement_lines) else line
        for i, (row, line) in enumerate(zip(statement_rows, statement_lines))
    ) + (newline if statement_text.endswith(("\n", "\r")) else "")
    statement_payload = statement_payload.encode("utf-8")
    if statement_raw.startswith(b"\xef\xbb\xbf"):
        statement_payload = b"\xef\xbb\xbf" + statement_payload

    recovery = Path(tempfile.gettempdir()) / ("pnp-s2-chp6-surface-prompts-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    recovery.mkdir(parents=True, exist_ok=False)
    backups = {path: recovery / path.name for path in (MENTIONS, STATEMENTS)}
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    print(f"recovery_directory={recovery}")
    try:
        atomic_write(MENTIONS, mention_payload)
        atomic_write(STATEMENTS, statement_payload)
        post_summary, post_hits = surface_audit.audit("chp-6", 6)
        post_residual = {signature(hit) for hit in post_hits}
        if int(post_summary["uncovered_candidate_surface_spans"]) != len(residual) or post_residual != residual:
            raise RuntimeError(f"post-write prompt set mismatch: expected={sorted(residual)} actual={sorted(post_residual)}")
        written_candidates = read_csv(TABLES / "entity-candidates.csv")[1]
        valid_candidate_ids = {row["candidate_id"] for row in written_candidates}
        written_mentions = read_csv(MENTIONS)[1]
        if any(row["candidate_id"] not in valid_candidate_ids for row in written_mentions):
            raise RuntimeError("post-write mention has an unknown candidate foreign key")
        final_statements = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        final_by_id = {row["statement_id"]: row for row in final_statements}
        for statement_id, candidate_ids in MENTIONED_CANDIDATE_ADDITIONS.items():
            actual = final_by_id[statement_id]["qualifiers"]["mentioned_candidate_ids"]
            if not set(candidate_ids).issubset(actual):
                raise RuntimeError(f"statement candidate link did not persist: {statement_id}")
        for statement_id, update in QUALIFICATION_UPDATES.items():
            if final_by_id[statement_id]["qualifiers"].get("qualification") != update["replacement"]:
                raise RuntimeError(f"statement qualification did not persist: {statement_id}")
        for row in new_mentions:
            segment = segments[row["segment_id"]]
            source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8-sig").splitlines()
            source_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
            if source_text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]:
                raise RuntimeError(f"post-write source span changed: {row['mention_id']}")
        print(f"post_write_candidate_surface_prompts={len(post_residual)}")
        print(f"mentions_sha256={hashlib.sha256(MENTIONS.read_bytes()).hexdigest()}")
        print(f"statements_sha256={hashlib.sha256(STATEMENTS.read_bytes()).hexdigest()}")
        print("mode=apply; verification passed")
    except Exception:
        for path, backup in backups.items():
            atomic_write(path, backup.read_bytes())
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
