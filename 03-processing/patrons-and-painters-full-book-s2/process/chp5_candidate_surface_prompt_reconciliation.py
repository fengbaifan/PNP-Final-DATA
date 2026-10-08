"""Adjudicate all current chapter 5 candidate-surface prompts.

The locator is a heuristic, not an extractor. This locked plan records exact
accepted mentions and no-write decisions, retains collections without forcing
them into an unsupported type, and writes only after every precondition passes.
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
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
sys.path.insert(0, str(ROOT / "scripts"))
import audit_s2_candidate_surfaces as surface_audit

EXPECTED_HASHES = {
    "04-knowledge/tables/entity-candidates.csv": "7261bd27b8ccf019aa417ff09fce2175d1eb834ad101bff0c62fe96475c29843",
    "04-knowledge/tables/mentions.csv": "6d3cfff1c47345f922f96673479928d0848072fc040ce5381866dc158e2ef3be",
    "04-knowledge/tables/book-statements.jsonl": "66cfa79868e5401e48423a6a353c6fc4da4242e0d400f0a77433a490e3568b3d",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/s2-coverage.csv": "84f8497a7ce0100f4785acd8bf8ed88bb4c69fe5254cd89d172577b0400eb6c1",
    "scripts/audit_s2_candidate_surfaces.py": "44874e88e4940af624ad7b91b6f3e7d016f8c4083c203114e354b6e6622901ba",
    "02-sources/02-Markdown/05_CHP-5_intro.md": "fe8a452c80f8ae012b224084037696b0f5459544e1919685e92dd2ef932b7265",
    "02-sources/02-Markdown/05_CHP-5_sec_i.md": "8ef51cd646ed6abf398c9faeb47df9a03f70de696d9a871c6d0b734b2adeeeee",
    "02-sources/02-Markdown/05_CHP-5_sec_iii.md": "9b095b1a93570102ad2cdb117580f2fbeccd2ff017033a2f66557c58a0d1ef0a",
    "02-sources/02-Markdown/05_CHP-5_sec_iv.md": "805df7b2bdc296cf987069cb0cea829bc07ec8932e28b075e9575f0c2ac67c4f",
}

SI3 = "chp-5:05_CHP-5_sec_i:l3-7"
SI9 = "chp-5:05_CHP-5_sec_i:l9-15"
SI17 = "chp-5:05_CHP-5_sec_i:l17-26"
SI28 = "chp-5:05_CHP-5_sec_i:l28-33"
SI35 = "chp-5:05_CHP-5_sec_i:l35-49"
SI60 = "chp-5:05_CHP-5_sec_i:l60-74"
SI76 = "chp-5:05_CHP-5_sec_i:l76-83"
SI85 = "chp-5:05_CHP-5_sec_i:l85-97"
SI99 = "chp-5:05_CHP-5_sec_i:l99-106"
SI108 = "chp-5:05_CHP-5_sec_i:l108-113"
SI115 = "chp-5:05_CHP-5_sec_i:l115-123"
SIII5 = "chp-5:05_CHP-5_sec_iii:l5-10"
SIII12 = "chp-5:05_CHP-5_sec_iii:l12-18"
SIII20 = "chp-5:05_CHP-5_sec_iii:l20-26"
SIII28 = "chp-5:05_CHP-5_sec_iii:l28-34"
SIII70 = "chp-5:05_CHP-5_sec_iii:l70-80"
SIII82 = "chp-5:05_CHP-5_sec_iii:l82-93"
SIII95 = "chp-5:05_CHP-5_sec_iii:l95-101"
SIII103 = "chp-5:05_CHP-5_sec_iii:l103-113"
SIII126 = "chp-5:05_CHP-5_sec_iii:l126-165"
SIV3 = "chp-5:05_CHP-5_sec_iv:l3-12"
SIV14 = "chp-5:05_CHP-5_sec_iv:l14-21"
SIV23 = "chp-5:05_CHP-5_sec_iv:l23-31"
SIV39 = "chp-5:05_CHP-5_sec_iv:l39-54"


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
    accepted(SI28, 789, "palace", "cand-0398",
             "Ferrante Carlo lived in Cardinal Borghese’s palace; the index-derived Borghese Palace candidate is the local referent."),
    accepted(SI28, 1522, "collection", "cand-11479",
             "Ferrante Carlo’s notable collection of pictures is a source-described collection; retain it untyped because the taxonomy has no collection type."),
    accepted(SI35, 874, "collection", "cand-11480",
             "Simonelli’s mixed collection is explicitly assembled by him and includes drawings, paintings, antiquities and cameos; retain its collection type unresolved."),
    accepted(SI60, 1329, "old masters", "cand-4288",
             "The phrase is the same art-historical category as the existing Old masters term candidate."),
    accepted(SI60, 2992, "canvas", "cand-3571",
             "Canvas denotes the painting support, matching the existing material term candidate."),
    accepted(SI76, 2258, "old masters", "cand-4288",
             "The phrase uses the existing broad art-historical category, not a particular work."),
    accepted(SI76, 3126, "old masters", "cand-4288",
             "The phrase uses the existing broad art-historical category, not a particular work."),
    accepted(SI85, 315, "Holy Year", "cand-11481",
             "This is the specific Jubilee of 1675, recorded separately from the generic Holy Year term cand-3453."),
    accepted(SI85, 1474, "Holy Year", "cand-11481",
             "This is the same specific Jubilee of 1675 referenced in the preceding exhibition account."),
    accepted(SI85, 2976, "old masters", "cand-4288",
             "The phrase uses the existing broad art-historical category, not a particular work."),
    accepted(SI9, 1726, "old masters", "cand-4288",
             "The phrase uses the existing broad art-historical category, not a particular work."),
    accepted(SI99, 196, "old masters", "cand-4288",
             "The phrase uses the existing broad art-historical category, not a particular work."),
    accepted(SI99, 2413, "Italian painting", "cand-11017",
             "The phrase denotes Italian painting as an artistic field, matching the existing term candidate."),
    accepted(SIII126, 2287, "collection", "cand-11482",
             "Ghezzi’s notes refer to the Colonna collection; preserve it as a distinct but untyped collection because ownership and boundaries are not specified."),
    accepted(SIII126, 4839, "collection", "cand-11483",
             "The note describes pictures held by Chigi descendants; retain this source-described collection separately from Cardinal Chigi’s historical inventory."),
    accepted(SIII126, 5265, "palace", "cand-6211",
             "The apposition identifies this as the palace later called Palazzo Odescalchi, matching the existing place candidate."),
    accepted(SIII126, 5613, "battle", "cand-6203",
             "The footnote identifies one particular Cerquozzi battle picture bought by Don Antonio Ruffo; use its dedicated work candidate."),
    accepted(SIII20, 1271, "Italian painting", "cand-11017",
             "The phrase denotes Italian painting as an artistic field, matching the existing term candidate."),
    accepted(SIII5, 2843, "bamboccianti", "cand-0173",
             "The phrase names the Bamboccianti group; use the bare group term, not candidates for topic subentries."),
    accepted(SIII95, 273, "Italian art", "cand-4131",
             "The phrase denotes the field of Italian art, matching the existing term candidate."),
    accepted(SIII95, 595, "palace", "cand-5112",
             "The local referent is Cardinal Bernardino Spada’s unnamed palace; keep it distinct from the pictures collected there and from Palazzo Spada pending S3."),
    accepted(SIV14, 85, "in Rome", "cand-3126",
             "The locator phrase is not itself an entity; record only the exact city span Rome.",
             mention_surface="Rome", mention_start=88),
    accepted(SIV23, 827, "altarpieces", "cand-11485",
             "These are an unnamed but locally bounded group of Rosa paintings in De’ Rossi’s family chapel; keep the work group distinct from the chapel."),
    accepted(SIV23, 1625, "canvas", "cand-3571",
             "Canvas denotes the painting support, matching the existing material term candidate."),
    accepted(SIV39, 439, "collection", "cand-11484",
             "The footnote’s De’ Rossi collection reference points back to the private museum of Rosa’s works described in the preceding body passage."),
]

NO_WRITE = [
    no_write(SI108, 448, "subject", "generic_art_subject"),
    no_write(SI108, 1309, "subject", "generic_art_subject"),
    no_write(SI108, 2213, "earnings", "generic_market_reference"),
    no_write(SI108, 2789, "altarpieces", "generic_art_category"),
    no_write(SI115, 2409, "subject", "generic_art_subject"),
    no_write(SI115, 2591, "amateur", "ordinary_amateur_role"),
    no_write(SI17, 711, "battle", "generic_art_category"),
    no_write(SI28, 829, "temperament", "ordinary_character_quality"),
    no_write(SI3, 395, "battle", "generic_art_category"),
    no_write(SI3, 395, "battle pictures", "generic_art_category"),
    no_write(SI3, 1134, "churches", "generic_art_category"),
    no_write(SI3, 1271, "aristocracy", "city_specific_index_subentry"),
    no_write(SI35, 888, "drawings", "generic_art_category"),
    no_write(SI76, 223, "portraits", "generic_art_category"),
    no_write(SI76, 2204, "aristocracy", "city_specific_index_subentry"),
    no_write(SI99, 990, "portraits", "generic_art_category"),
    no_write(SI99, 1004, "battle", "generic_art_category"),
    no_write(SI99, 1004, "battle pictures", "generic_art_category"),
    no_write(SI99, 1926, "altarpieces", "generic_art_category"),
    no_write(SI99, 1961, "churches", "generic_art_category"),
    no_write(SI99, 3058, "palace", "generic_palace_reference"),
    no_write(SIII103, 301, "palace", "generic_palace_reference"),
    no_write(SIII12, 2594, "character", "ordinary_character_quality"),
    no_write(SIII20, 845, "churches", "generic_art_category"),
    no_write(SIII20, 1660, "amateur", "ordinary_amateur_role"),
    no_write(SIII28, 916, "prince", "generic_conceptual_reference"),
    no_write(SIII28, 2119, "amateur", "ordinary_amateur_role"),
    no_write(SIII5, 352, "attacks on", "generic_conceptual_reference"),
    no_write(SIII5, 1945, "brigand", "generic_conceptual_reference"),
    no_write(SIII5, 2500, "subject", "generic_art_subject"),
    no_write(SIII70, 1241, "battle", "generic_art_category"),
    no_write(SIII70, 1888, "subject", "generic_art_subject"),
    no_write(SIII70, 2123, "prices", "generic_market_reference"),
    no_write(SIII82, 2696, "battle", "generic_art_category"),
    no_write(SIII95, 1364, "subject", "generic_art_subject"),
    no_write(SIII95, 1471, "portraits", "generic_art_category"),
    no_write(SIII95, 2302, "presentation", "generic_conceptual_reference"),
    no_write(SIII126, 5065, "payment", "generic_market_reference"),
    no_write(SIV3, 283, "amateur", "ordinary_amateur_role"),
    no_write(SIV3, 755, "histories", "generic_art_category"),
    no_write(SIV3, 2266, "histories", "generic_art_category"),
    no_write(SIV14, 11, "poetry", "generic_conceptual_reference"),
    no_write(SIV14, 876, "fortune", "generic_conceptual_reference"),
    no_write(SIV23, 2701, "garden", "generic_conceptual_reference"),
]

NO_WRITE_TEXT = {
    "generic_art_subject": "Subject describes artistic content or a topic of discussion, not the indexed patronal-subject concept or a distinct entity.",
    "generic_market_reference": "The word describes a general economic measure or the absence of a documented payment, not a distinct entity.",
    "generic_art_category": "The plural or genre term denotes a broad class of artworks or settings; no particular work or bounded group is identified by this span.",
    "ordinary_amateur_role": "Amateur describes an ordinary occupational or audience role, not the existing social-category term in its source context.",
    "ordinary_character_quality": "The word describes personal disposition or a general quality, not a distinct entity.",
    "city_specific_index_subentry": "The matching index subentry is attached to Genoa; this Rome reference does not identify that candidate or a standalone entity.",
    "generic_palace_reference": "The palace is a general or imaginary architectural category, not a locally identified building.",
    "generic_conceptual_reference": "The phrase is an ordinary description, metaphor, role, or activity rather than a distinct entity represented by the matched candidate.",
}
EXPECTED_NO_WRITE_COUNTS = {
    "generic_art_subject": 6,
    "generic_market_reference": 3,
    "generic_art_category": 18,
    "ordinary_amateur_role": 4,
    "ordinary_character_quality": 2,
    "city_specific_index_subentry": 2,
    "generic_palace_reference": 2,
    "generic_conceptual_reference": 7,
}


def candidate(candidate_id: str, canonical_name: str, suggested_type: str,
              source_ref: str, detail: str) -> dict[str, str]:
    return {
        "candidate_id": candidate_id, "index_entry_id": "",
        "canonical_name": canonical_name, "index_page_range": "",
        "suggested_type": suggested_type, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": source_ref,
    }


NEW_CANDIDATES = [
    candidate("cand-11479", "Ferrante Carlo’s collection of pictures", "",
              "chp-5:05_CHP-5_sec_i:l28-33#L31",
              "Haskell says Carlo owned a notable collection and describes pictures on his walls. Individual works and the collection’s formal identity are not supplied; retain it as a type-pending source-derived collection."),
    candidate("cand-11480", "Niccolò Simonelli’s mixed art collection", "",
              "chp-5:05_CHP-5_sec_i:l35-49#L37",
              "Haskell says Simonelli assembled drawings by Giulio Romano, Polidoro da Caravaggio and Annibale Carracci, as well as paintings, antiquities and cameos. The project has no collection type; do not split the described holdings into invented works."),
    candidate("cand-11481", "Holy Year of 1675 (Jubilee)", "event",
              "chp-5:05_CHP-5_sec_i:l85-97#L88",
              "The specific 1675 Holy Year is the event context for exhibitions on pp.128–129. Keep it distinct from generic Holy Year term cand-3453."),
    candidate("cand-11482", "Colonna collection cited in Ghezzi’s notes", "",
              "chp-5:05_CHP-5_sec_iii:l126-165#L141",
              "Haskell reports that Ghezzi’s notes on the Colonna collection mention two bambocciate. The owner and collection boundaries are not identified; retain it type-pending and distinct from the archive of Ghezzi’s notes."),
    candidate("cand-11483", "Collection of paintings held by the Chigi descendants", "",
              "chp-5:05_CHP-5_sec_iii:l126-165#L154",
              "The footnote says the Cerquozzi pictures and other recorded paintings remained with Chigi descendants. Preserve this present collection grouping separately from the disputed claim that the pictures were painted for Cardinal Chigi."),
    candidate("cand-11484", "De’ Rossi’s private museum of Salvator Rosa’s works", "",
              "chp-5:05_CHP-5_sec_iv:l23-31#L24",
              "Haskell describes a large gallery and several rooms assembled as a private museum of Rosa’s works; a later note refers to De’ Rossi’s collection in Bellori’s Nota de Musei. Retain the collection type unresolved and distinct from the gallery/place candidate cand-6951."),
    candidate("cand-11485", "Salvator Rosa’s unnamed altarpieces in De’ Rossi’s family chapel", "work",
              "chp-5:05_CHP-5_sec_iv:l23-31#L27",
              "Haskell describes plural altarpieces by Rosa in the Madonna di Montesanto family chapel, painted without charge for public display. Titles, number and dates are not given; represent the locally bounded group separately from chapel candidate cand-6228."),
]

EXTRA_MENTIONS = [
    {"segment_id": SIV23, "candidate_id": "cand-11484",
     "surface_form": "private museum", "start_char": 97,
     "end_char": 111,
     "note": "The phrase identifies the same De’ Rossi collection later referenced in the footnote; the statement preserves the source’s ‘what amounted to’ qualification and Rosa’s works."},
]

STATEMENT_UPDATES = {
    "st-chp5-p123-carlo-collecting": {"collection_candidate_id": "cand-11479"},
    "st-chp5-p124-simonelli-collection": {"collection_candidate_id": "cand-11480"},
    "st-chp5-p128-medici-1675-exhibition": {"holy_year_event_candidate_id": "cand-11481"},
    "st-chp5-p128-1675-salvatore-reputation": {"holy_year_event_candidate_id": "cand-11481"},
    "st-chp5-notes-l141-ghezzi-velasco-pictures": {"collection_candidate_id": "cand-11482"},
    "st-chp5-notes-l154-colonna-acquisition-alternative": {"collection_candidate_id": "cand-11483"},
    "st-chp5-p139-spada-assembled-collection": {"place_candidate_id": "cand-5112"},
    "st-chp5-p144-de-rossi-private-museum-of-rosa-works": {"collection_candidate_id": "cand-11484"},
    "st-chp5-seciv-note-l47-p144-marker2": {"collection_candidate_id": "cand-11484"},
    "st-chp5-p144-rosa-painted-altarpieces-for-family-chapel": {"work_candidate_id": "cand-11485"},
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
    parser.add_argument("--apply", action="store_true", help="write the source-locked candidate, mention and statement updates")
    args = parser.parse_args()

    for relative, expected in EXPECTED_HASHES.items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit(f"source hash changed: {relative}: expected={expected} actual={actual}")

    summary, hits = surface_audit.audit("chp-5", 6)
    if summary.get("reviewed_segments_scanned") != 35 or len(hits) != 69:
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

    candidate_fields, candidate_rows, candidate_raw = read_csv(CANDIDATES)
    mention_fields, mention_rows, mention_raw = read_csv(MENTIONS)
    statement_raw = STATEMENTS.read_bytes()
    statement_text = statement_raw.decode("utf-8-sig")
    statement_lines = statement_text.splitlines()
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    if len(candidate_by_id) != len(candidate_rows):
        raise SystemExit("duplicate candidate IDs")
    if max(int(cid.split("-")[1]) for cid in candidate_by_id) != 11478:
        raise SystemExit("candidate ID allocation precondition changed")
    for row in NEW_CANDIDATES:
        if row["candidate_id"] in candidate_by_id:
            raise SystemExit(f"new candidate ID already exists: {row['candidate_id']}")
        if row["candidate_origin"] != "body-mention" or row["status"] != "open":
            raise SystemExit(f"new candidate is not source-derived/open: {row['candidate_id']}")
        expected_type = {"cand-11481": "event", "cand-11485": "work"}.get(row["candidate_id"], "")
        if row["suggested_type"] != expected_type:
            raise SystemExit(f"candidate type changed: {row['candidate_id']}")
    candidate_by_id.update({row["candidate_id"]: row for row in NEW_CANDIDATES})

    segments = {
        row["segment_id"]: row
        for row in (json.loads(line) for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip())
    }
    existing_keys = {(row["segment_id"], int(row["start_char"]), int(row["end_char"])) for row in mention_rows}
    existing_ids = {row["mention_id"] for row in mention_rows}
    planned_keys: set[tuple[str, int, int]] = set()
    planned_spans: list[tuple[str, int, int]] = []
    new_mentions: list[dict[str, str]] = []
    source_cache: dict[str, str] = {}

    planned = [(item, True) for item in ACCEPTED] + [(item, False) for item in EXTRA_MENTIONS]
    for item, is_prompt in planned:
        segment_id = str(item["segment_id"])
        segment = segments.get(segment_id)
        if not segment:
            raise SystemExit(f"unknown segment: {segment_id}")
        if segment_id not in source_cache:
            lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8-sig").splitlines()
            source_cache[segment_id] = "\n".join(lines[segment["line_start"] - 1:segment["line_end"]])
        text = source_cache[segment_id]
        candidate_id = str(item["candidate_id"])
        if candidate_id not in candidate_by_id:
            raise SystemExit(f"unknown planned candidate: {candidate_id}")
        start, end, surface = int(item["start_char"]), int(item["end_char"]), str(item["surface_form"])
        if text[start:end] != surface:
            raise SystemExit(f"planned mention source span mismatch: {segment_id} {start}:{end} {surface!r}")
        if is_prompt:
            prompt_start, prompt_end = int(item["prompt_start"]), int(item["prompt_end"])
            if text[prompt_start:prompt_end] != str(item["prompt_surface"]):
                raise SystemExit(f"prompt source span mismatch: {segment_id} {prompt_start}:{prompt_end}")
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
        mention_id = f"m-s2-chp5-surface-{digest}"
        if mention_id in existing_ids:
            raise SystemExit(f"mention ID already exists: {mention_id}")
        new_mentions.append({
            "mention_id": mention_id, "segment_id": segment_id,
            "candidate_id": candidate_id, "surface_form": surface,
            "start_char": str(start), "end_char": str(end),
            "note": str(item["note"]),
        })
        existing_ids.add(mention_id)
        planned_keys.add(natural_key)
        planned_spans.append((segment_id, start, end))

    if len(new_mentions) != 26:
        raise SystemExit(f"unexpected mention write count: {len(new_mentions)}")
    for item in NEW_CANDIDATES:
        if not item["suggested_type"] and item["candidate_id"] not in candidate_by_id:
            raise SystemExit(f"type-pending collection was not retained: {item['candidate_id']}")

    statement_rows = []
    statement_by_id = {}
    changed_statement_lines = []
    for i, line in enumerate(statement_lines):
        row = json.loads(line)
        statement_id = row.get("statement_id")
        if statement_id in statement_by_id:
            raise SystemExit(f"duplicate statement ID: {statement_id}")
        statement_by_id[statement_id] = row
        if statement_id in STATEMENT_UPDATES:
            qualifiers = row.setdefault("qualifiers", {})
            for field, candidate_id in STATEMENT_UPDATES[statement_id].items():
                if candidate_id not in candidate_by_id:
                    raise SystemExit(f"statement update references unknown candidate: {candidate_id}")
                if field in qualifiers and qualifiers[field] != candidate_id:
                    raise SystemExit(f"statement qualifier precondition changed: {statement_id} {field}")
                qualifiers[field] = candidate_id
            changed_statement_lines.append(i)
        statement_rows.append(row)
    if set(STATEMENT_UPDATES) - set(statement_by_id):
        raise SystemExit(f"missing statement update targets: {sorted(set(STATEMENT_UPDATES)-set(statement_by_id))}")
    if len(changed_statement_lines) != len(STATEMENT_UPDATES):
        raise SystemExit("statement update count changed")

    planned_spans_set = planned_spans
    residual = {
        key for key in no_write_by_sig
        if not any(seg == key[0] and start < key[2] and end > key[1]
                   for seg, start, end in planned_spans_set)
    }
    plan_sha = hashlib.sha256(json.dumps(
        {"accepted": ACCEPTED, "no_write": NO_WRITE, "extra_mentions": EXTRA_MENTIONS,
         "new_candidates": NEW_CANDIDATES, "statement_updates": STATEMENT_UPDATES,
         "no_write_reasons": NO_WRITE_TEXT},
        ensure_ascii=False, sort_keys=True,
    ).encode("utf-8")).hexdigest()

    print("chapter=chp-5")
    print(f"reviewed_segments_scanned={summary['reviewed_segments_scanned']}")
    print(f"candidate_surface_prompts={len(hits)}")
    print(f"accepted_prompt_signatures={len(ACCEPTED)}")
    print(f"new_candidates={len(NEW_CANDIDATES)}")
    print(f"new_mentions={len(new_mentions)} (including {len(EXTRA_MENTIONS)} source-backed body span)")
    print(f"no_write_prompt_signatures={len(NO_WRITE)}")
    for reason, count in sorted(reason_counts.items()):
        print(f"no_write[{reason}]={count}: {NO_WRITE_TEXT[reason]}")
    print(f"candidate_rows_before={len(candidate_rows)} candidate_rows_after={len(candidate_rows)+len(NEW_CANDIDATES)}")
    print(f"mention_rows_before={len(mention_rows)} mention_rows_after={len(mention_rows)+len(new_mentions)}")
    print(f"statement_rows={len(statement_rows)} updated_statements={len(changed_statement_lines)}")
    print(f"expected_post_write_prompts={len(residual)}")
    print(f"plan_sha256={plan_sha}")
    if not args.apply:
        print("mode=dry-run; no files written")
        return 0

    candidate_payload = encode_csv(candidate_fields, candidate_rows + NEW_CANDIDATES, candidate_raw)
    mention_payload = encode_csv(mention_fields, mention_rows + new_mentions, mention_raw)
    newline = "\r\n" if b"\r\n" in statement_raw else "\n"
    statement_payload = newline.join(
        json.dumps(row, ensure_ascii=False) if i in changed_statement_lines else line
        for i, (row, line) in enumerate(zip(statement_rows, statement_lines))
    ) + (newline if statement_text.endswith(("\n", "\r")) else "")
    statement_payload = statement_payload.encode("utf-8")
    if statement_raw.startswith(b"\xef\xbb\xbf"):
        statement_payload = b"\xef\xbb\xbf" + statement_payload

    recovery = Path(tempfile.gettempdir()) / ("pnp-s2-chp5-surface-prompts-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    recovery.mkdir(parents=True, exist_ok=False)
    backups = {path: recovery / path.name for path in (CANDIDATES, MENTIONS, STATEMENTS)}
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    print(f"recovery_directory={recovery}")
    try:
        atomic_write(CANDIDATES, candidate_payload)
        atomic_write(MENTIONS, mention_payload)
        atomic_write(STATEMENTS, statement_payload)
        post_summary, post_hits = surface_audit.audit("chp-5", 6)
        post_residual = {signature(hit) for hit in post_hits}
        if int(post_summary["uncovered_candidate_surface_spans"]) != len(residual) or post_residual != residual:
            raise RuntimeError(f"post-write prompt set mismatch: expected={sorted(residual)} actual={sorted(post_residual)}")
        written_candidates = read_csv(CANDIDATES)[1]
        valid_candidate_ids = {row["candidate_id"] for row in written_candidates}
        written_mentions = read_csv(MENTIONS)[1]
        if any(row["candidate_id"] not in valid_candidate_ids for row in written_mentions):
            raise RuntimeError("post-write mention has an unknown candidate foreign key")
        for row in new_mentions:
            segment = segments[row["segment_id"]]
            source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8-sig").splitlines()
            source_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
            if source_text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]:
                raise RuntimeError(f"post-write source span changed: {row['mention_id']}")
        final_statements = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        final_by_id = {row["statement_id"]: row for row in final_statements}
        for statement_id, fields in STATEMENT_UPDATES.items():
            for field, candidate_id in fields.items():
                if final_by_id[statement_id]["qualifiers"].get(field) != candidate_id:
                    raise RuntimeError(f"statement candidate link did not persist: {statement_id} {field}")
        print(f"post_write_candidate_surface_prompts={len(post_residual)}")
        print(f"candidates_sha256={hashlib.sha256(CANDIDATES.read_bytes()).hexdigest()}")
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
