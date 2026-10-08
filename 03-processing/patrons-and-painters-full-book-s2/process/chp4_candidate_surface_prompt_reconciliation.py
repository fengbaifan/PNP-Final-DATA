"""Adjudicate the 54 current chapter 4 candidate-surface prompts.

The locator is heuristic only. This source-locked plan reuses locally
identified candidates, records exact alias spans and no-write decisions, and
keeps type-pending collections untyped. Default mode is read-only; --apply
appends mentions.csv with a recovery copy and verifies the post-write set.
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
    "04-knowledge/tables/mentions.csv": "4fb171e97a25f3c67f99d79b774272daf6d83ec18592e39659b165e564ab7f3c",
    "04-knowledge/tables/book-statements.jsonl": "66cfa79868e5401e48423a6a353c6fc4da4242e0d400f0a77433a490e3568b3d",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/s2-coverage.csv": "84f8497a7ce0100f4785acd8bf8ed88bb4c69fe5254cd89d172577b0400eb6c1",
    "scripts/audit_s2_candidate_surfaces.py": "44874e88e4940af624ad7b91b6f3e7d016f8c4083c203114e354b6e6622901ba",
    "02-sources/02-Markdown/04_CHP-4_intro.md": "6703a3c57834a1ec42d3c292d3883571c9f17c67831b38570125b588d225b40b",
    "02-sources/02-Markdown/04_CHP-4_sec_i.md": "3961adefb7ea2e1f2e44e02173a494c509964e7273b6b3867619643bbd9ecb64",
    "02-sources/02-Markdown/04_CHP-4_sec_ii.md": "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575",
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


INTRO = "chp-4:04_CHP-4_intro:l3-8"
SI6 = "chp-4:04_CHP-4_sec_i:l6-18"
SI26 = "chp-4:04_CHP-4_sec_i:l26-33"
SI42 = "chp-4:04_CHP-4_sec_i:l42-67"
SII15 = "chp-4:04_CHP-4_sec_ii:l15-22"
SII24 = "chp-4:04_CHP-4_sec_ii:l24-31"
SII33 = "chp-4:04_CHP-4_sec_ii:l33-44"
SII46 = "chp-4:04_CHP-4_sec_ii:l46-51"
SII53 = "chp-4:04_CHP-4_sec_ii:l53-63"
SII80 = "chp-4:04_CHP-4_sec_ii:l80-89"
SII91 = "chp-4:04_CHP-4_sec_ii:l91-99"
SII101 = "chp-4:04_CHP-4_sec_ii:l101-107"
SII109 = "chp-4:04_CHP-4_sec_ii:l109-119"
SII121 = "chp-4:04_CHP-4_sec_ii:l121-128"
SII130 = "chp-4:04_CHP-4_sec_ii:l130-137"
SII139 = "chp-4:04_CHP-4_sec_ii:l139-149"
SII161 = "chp-4:04_CHP-4_sec_ii:l161-170"
SII180 = "chp-4:04_CHP-4_sec_ii:l180-189"
SII191 = "chp-4:04_CHP-4_sec_ii:l191-205"
SII207 = "chp-4:04_CHP-4_sec_ii:l207-216"
SII218 = "chp-4:04_CHP-4_sec_ii:l218-227"
SII232 = "chp-4:04_CHP-4_sec_ii:l232-308"

ACCEPTED = [
    accepted(SI42, 635, "collection", "cand-5606", "collection", 635,
             "The documents are identified locally as Fondo Orsini; this mention denotes the archival fonds, not the repository."),
    accepted(SII109, 839, "collection", "cand-5822", "collection", 839,
             "The quoted collection is the writings Cassiano showed Dupuy, recorded by the existing source-derived archive candidate."),
    accepted(SII121, 1637, "collection", "cand-5654", "collection", 1637,
             "Cassiano's antiquities are described as holdings of his previously identified library and museum; retain its unresolved collection type."),
    accepted(SII15, 1893, "palace", "cand-5652", "palace", 1893,
             "The definite reference is Cassiano's residence on Via Chiavari, already represented by the unidentified-palace candidate."),
    accepted(SII161, 557, "collection", "cand-5921", "collection", 557,
             "The passage concerns Cassiano's painting collection as a group; preserve its unresolved type."),
    accepted(SII218, 767, "connoisseurship", "cand-3567", "connoisseurship", 767,
             "Connoisseurship is used as the same art-historical practice represented by the existing term candidate."),
    accepted(SII218, 884, "palace", "cand-0090", "palace", 884,
             "The new palace is locally identified as the Altieri palace in the same sentence."),
    accepted(SII218, 1747, "subject", "cand-0840", "subject", 1747,
             "The painting subject is explicitly said to have been chosen by the patron."),
    accepted(SII232, 3338, "collection", "cand-5921", "collection", 3338,
             "The note cites accounts of Cassiano's painting collection."),
    accepted(SII232, 4331, "collection", "cand-5921", "collection", 4331,
             "Skippon is said to have been shown Cassiano's painting collection; the bird-painting group remains a separate candidate."),
    accepted(SII232, 4545, "in Rome", "cand-3126", "Rome", 4548,
             "The longer indexed phrase collides with unrelated subentries; record the exact city span."),
    accepted(SII232, 5374, "drawings", "cand-5784", "drawings", 5374,
             "These are Poussin's drawings made for Leonardo's Trattato, already represented by the source-derived work candidate."),
    accepted(SII232, 8389, "Flight into Egypt", "cand-5876", "Flight into Egypt", 8389,
             "The note refers to other representations of the biblical episode, not to one of the indexed paintings."),
    accepted(SII232, 9288, "visit to Paris", "cand-4653", "Paris", 9297,
             "The index phrase is a travel event, while the precise entity mention here is the destination city."),
    accepted(SII24, 2422, "drawings", "cand-5666", "drawings", 2422,
             "The drawings bound into volumes are the content of Cassiano's locally named paper museum; its collection type remains unresolved."),
    accepted(SII24, 2823, "drawings", "cand-5744", "drawings", 2823,
             "The divided corpus is the approximately fifteen hundred Roman-antiquity drawings represented by the existing grouped-work candidate."),
    accepted(SII24, 3120, "drawings", "cand-5694", "drawings", 3120,
             "The Windsor subset is specifically attributed to Testa by Blunt and has its own grouped-work candidate."),
    accepted(SII33, 304, "drawings", "cand-5850", "drawings", 304,
             "The quotation specifies Cassiano's volumes copied from ancient marbles; keep them distinct from the deity-and-sacrifice volume."),
    accepted(SII53, 1548, "altarpieces", "cand-5741", "altarpieces", 1548,
             "The phrase identifies one work appositionally as the St Romualdo altarpiece of 1638."),
    accepted(SII80, 1721, "collection", "cand-5921", "collection", 1721,
             "The passage explicitly counts Poussin paintings in Cassiano's painting collection."),
    accepted(SII91, 170, "subject", "cand-0840", "subject", 170,
             "Cassiano proposes the subject of the Marriage of Peleus to Poussin."),
    accepted(SII91, 771, "visit to Paris", "cand-4653", "Paris", 780,
             "The longer indexed phrase is not an entity; record its exact destination city."),
    accepted(SII91, 2755, "drawings", "cand-5784", "drawings", 2755,
             "The demonstrative refers back to Poussin's drawings made for the Trattato."),
]

NO_WRITE = [
    no_write(INTRO, 764, "poetry", "ordinary_poetry_reference"),
    no_write(INTRO, 837, "drawings", "generic_artwork_class"),
    no_write(SI26, 1808, "churches", "generic_place_class"),
    no_write(SI6, 867, "subject", "generic_art_subject"),
    no_write(SI6, 2409, "love of music and spectacle", "ordinary_personal_interest"),
    no_write(SI6, 3503, "subject", "generic_art_subject"),
    no_write(SII101, 19, "subject", "generic_art_subject"),
    no_write(SII101, 510, "religious views", "ordinary_religious_views"),
    no_write(SII101, 946, "religious views", "ordinary_religious_views"),
    no_write(SII101, 2085, "temperament", "ordinary_temperament"),
    no_write(SII109, 1227, "religious views", "ordinary_religious_views"),
    no_write(SII121, 576, "fortune", "ordinary_fortune_reference"),
    no_write(SII130, 2557, "subject", "generic_art_subject"),
    no_write(SII139, 1571, "character", "ordinary_character_quality"),
    no_write(SII139, 2502, "character", "ordinary_character_quality"),
    no_write(SII15, 2062, "drawings", "generic_artwork_class"),
    no_write(SII180, 1286, "subject", "ordinary_study_subject"),
    no_write(SII191, 1251, "portraits", "generic_portrait_class"),
    no_write(SII191, 1607, "character", "ordinary_character_quality"),
    no_write(SII191, 2562, "theatre", "generic_roman_theatre"),
    no_write(SII207, 2685, "amateur", "ordinary_profession"),
    no_write(SII232, 2863, "portraits", "generic_portrait_class"),
    no_write(SII232, 4187, "subject", "ordinary_subject_matter"),
    no_write(SII232, 5633, "subject", "ordinary_subject_matter"),
    no_write(SII24, 2247, "drawings", "generic_artwork_class"),
    no_write(SII24, 2778, "subject", "ordinary_subject_matter"),
    no_write(SII33, 82, "subject", "ordinary_subject_matter"),
    no_write(SII33, 610, "histories", "generic_historical_category"),
    no_write(SII46, 62, "views on painting", "ordinary_viewpoint"),
    no_write(SII53, 2469, "subject", "ordinary_subject_matter"),
    no_write(SII80, 1856, "subject", "ordinary_subject_matter"),
]

NO_WRITE_TEXT = {
    "ordinary_poetry_reference": "Poetry describes Ghibbesio's literary ability, not a distinct work or entity.",
    "generic_artwork_class": "Plural or medium-level reference to drawings; no specific work is identified by this span.",
    "generic_place_class": "Plural churches on estates, with no individually identified site.",
    "generic_art_subject": "Subject describes the content or treatment of an artwork, without a patronal choice or distinct named subject entity.",
    "ordinary_personal_interest": "A biographical description of Virginio's interests, not a separate conceptual entity.",
    "ordinary_religious_views": "General beliefs or opinions attributed to Poussin, not a separately identified doctrine or person.",
    "ordinary_temperament": "Ordinary personal disposition, not the indexed concept-history use of temperament.",
    "ordinary_fortune_reference": "Fortune means opportunity or luck in this sentence, not the indexed work.",
    "ordinary_character_quality": "Character is used as a general personal quality, not a distinct entity.",
    "ordinary_study_subject": "The phrase refers to Camillo as the subject of Haskell's study, not the patronal subject concept.",
    "generic_portrait_class": "Plural portraits are a general class here; no one portrait or bounded portrait group is identified by this span.",
    "generic_roman_theatre": "A Roman theatre is mentioned generically without a named or locally identified site.",
    "ordinary_profession": "Amateur describes Massimi's role as an artist, not a named group or institution.",
    "ordinary_subject_matter": "Subject refers to a topic, scholarly discussion, or generic artistic subject-matter, not the patronal subject concept.",
    "generic_historical_category": "Roman histories and fables describe imagery on reliefs, not a distinct archive or historical work.",
    "ordinary_viewpoint": "Galileo's personal opinions about painting, not a named school or separately established concept.",
}

EXPECTED_NO_WRITE_COUNTS = {
    "ordinary_poetry_reference": 1,
    "generic_artwork_class": 3,
    "generic_place_class": 1,
    "generic_art_subject": 4,
    "ordinary_personal_interest": 1,
    "ordinary_religious_views": 3,
    "ordinary_temperament": 1,
    "ordinary_fortune_reference": 1,
    "ordinary_character_quality": 3,
    "ordinary_study_subject": 1,
    "generic_portrait_class": 2,
    "generic_roman_theatre": 1,
    "ordinary_profession": 1,
    "ordinary_subject_matter": 6,
    "generic_historical_category": 1,
    "ordinary_viewpoint": 1,
}

ALLOWED_UNTYPED_CANDIDATES = {"cand-5654", "cand-5666", "cand-5921"}


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


def encode_csv(fields: list[str], rows: list[dict[str, str]], raw_before: bytes) -> bytes:
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

    summary, hits = surface_audit.audit("chp-4", 6)
    if summary.get("reviewed_segments_scanned") != 37 or len(hits) != 54:
        raise SystemExit(f"unexpected locator result: {summary}")
    hit_by_sig = {signature(hit): hit for hit in hits}
    if len(hit_by_sig) != len(hits):
        raise SystemExit("duplicate candidate-surface signatures in locator output")

    no_write_by_sig = {signature(item): item for item in NO_WRITE}
    reason_counts = Counter(item["reason"] for item in NO_WRITE)
    if len(no_write_by_sig) != len(NO_WRITE) or dict(reason_counts) != EXPECTED_NO_WRITE_COUNTS:
        raise SystemExit(f"no-write adjudication changed: signatures={len(no_write_by_sig)} reasons={dict(reason_counts)}")
    accepted_by_sig = {}
    for item in ACCEPTED:
        key = (
            str(item["segment_id"]), int(item["prompt_start"]),
            int(item["prompt_end"]), str(item["prompt_surface"]),
        )
        if key in accepted_by_sig:
            raise SystemExit(f"duplicate accepted prompt signature: {key}")
        accepted_by_sig[key] = item
    if set(accepted_by_sig) & set(no_write_by_sig):
        raise SystemExit("one prompt signature is both accepted and no-write")
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
    if len(candidate_by_id) != len(candidate_rows):
        raise SystemExit("duplicate candidate IDs")
    segments = {
        row["segment_id"]: row
        for row in (json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip())
    }
    source_cache: dict[str, str] = {}
    existing_natural_keys = {
        (row["segment_id"], int(row["start_char"]), int(row["end_char"])) for row in mention_rows
    }
    existing_ids = {row["mention_id"] for row in mention_rows}
    planned_keys: set[tuple[str, int, int]] = set()
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
            raise SystemExit(f"unknown accepted candidate: {candidate_id}")
        if not candidate["suggested_type"]:
            if candidate_id not in ALLOWED_UNTYPED_CANDIDATES or candidate["candidate_origin"] != "body-mention" or candidate["status"] != "open":
                raise SystemExit(f"untyped candidate is not an explicitly retained collection: {candidate_id}")
        start, end = int(item["start_char"]), int(item["end_char"])
        surface = str(item["surface_form"])
        if source_text[start:end] != surface or start >= prompt_end or end <= prompt_start:
            raise SystemExit(f"accepted source span mismatch: {segment_id} {start}:{end} {surface!r}")
        natural_key = (segment_id, start, end)
        if natural_key in existing_natural_keys or natural_key in planned_keys:
            raise SystemExit(f"mention natural key already present or planned: {natural_key}")
        for old in mention_rows:
            old_start, old_end = int(old["start_char"]), int(old["end_char"])
            if old["segment_id"] == segment_id and start < old_end and end > old_start:
                raise SystemExit(f"planned mention overlaps existing mention: {natural_key}")
        for old_segment, old_start, old_end in planned_spans:
            if old_segment == segment_id and start < old_end and end > old_start:
                raise SystemExit(f"planned mentions overlap: {natural_key}")
        digest = hashlib.sha256(f"{segment_id}|{start}|{end}|{candidate_id}".encode("utf-8")).hexdigest()[:16]
        mention_id = f"m-s2-chp4-surface-{digest}"
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
        planned_keys.add(natural_key)
        planned_spans.append((segment_id, start, end))

    expected_residual = {
        key for key in no_write_by_sig
        if not any(
            segment_id == key[0] and start < key[2] and end > key[1]
            for segment_id, start, end in planned_spans
        )
    }
    if len(new_mentions) != 23 or len(expected_residual) != 31:
        raise SystemExit(f"unexpected write/residual counts: mentions={len(new_mentions)} residual={len(expected_residual)}")

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

    recovery = Path(tempfile.gettempdir()) / ("pnp-s2-chp4-surface-prompts-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    recovery.mkdir(parents=True, exist_ok=False)
    backup = recovery / MENTIONS.name
    shutil.copy2(MENTIONS, backup)
    print(f"recovery_copy[mentions.csv]={backup}")
    payload = encode_csv(mention_fields, mention_rows + new_mentions, mention_raw)
    try:
        atomic_write(MENTIONS, payload)
        post_summary, post_hits = surface_audit.audit("chp-4", 6)
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
