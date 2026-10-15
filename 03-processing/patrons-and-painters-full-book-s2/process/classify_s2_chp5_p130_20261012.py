from __future__ import annotations

import argparse
import codecs
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path.cwd()
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "05_CHP-5_sec_i.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-5.pdf"
PAGE_IMAGE = PROCESS / "p130_page_review_20261012.png"
SEGMENT = "chp-5:05_CHP-5_sec_i:l108-113"
SOURCE_FILE = "02-sources/02-Markdown/05_CHP-5_sec_i.md"
EXPECTED = {
    "book-statements.jsonl": "82e4e551ffe4395562a6352246ba2f0a097c0288871d71e7a7ca7298f28c0690",
    "entity-candidates.csv": "2a5718c17365008fcb20992aeb1c9577ce1456cd6e6b6be131bb7fda4f9f7685",
    "mentions.csv": "0f21a1df5a8b4559cb923ef0fc916d98cd2dcb9ed5880ac6a3d1ece1d3b0d064",
}
SOURCE_SHA = "8ef51cd646ed6abf398c9faeb47df9a03f70de696d9a871c6d0b734b2adeeeee"
PDF_SHA = "f63dca79808fde73ba10aa9414fef89bc8ca5e77ed829b2d5c86f23719e0674a"
IMAGE_SHA = "4672ad1b87e787057f3adeec0c191677987f668a72c19cb8723018dcb87ae095"
SEGMENT_SHA = "4d9e900d455df7d1db1be2a849344aae3fb4ba1517e6600c677e84d20bed5af5"
NEW_CANDIDATE_ID = "cand-11795"
NEW_MENTION_IDS = {"m-chp5-p130-0024", "m-chp5-p130-0025", "m-chp5-p130-0026"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
segment_text = "\n".join(source_lines[107:113])


def exact(text: str, needle: str, expected_start: int | None = None) -> str:
    if expected_start is not None:
        actual = text[expected_start:expected_start + len(needle)]
        need(actual == needle, f"source span moved or changed: {needle!r}: {actual!r} != {needle!r}")
        return needle
    at = text.find(needle)
    need(at >= 0, f"source quote not found: {needle!r}")
    return needle


STATEMENT_NOTES = {
    "st-chp5-p130-aesthetic-view-and-connoisseurs":
        "Haskell's account of a broad change in aesthetic appreciation and the emergence of an unnamed judging group; it is not a dyadic relation.",
    "st-chp5-p130-anonymous_patrons_in_literature":
        "The passage reports a recurring reference pattern in unspecified artistic literature; no bounded literary corpus or individual patron is identified as a relation endpoint.",
    "st-chp5-p130-artist-impressions-closure":
        "Cross-page continuation of artists' public visibility and general conduct; the artist group and individual initiation event are unnamed, so retain it as a source claim.",
    "st-chp5-p130-caravaggio_flowers_figures_comment":
        "The source explicitly reports Caravaggio making the comment to Vincenzo Giustiniani; the note remains a reported utterance, not a directly consulted Caravaggio document.",
    "st-chp5-p130-devotional_mass_produced_or_copied":
        "A source-level generalization about the likely picture holdings of an unnamed public; no specific work, maker, or ownership edge is asserted.",
    "st-chp5-p130-haskell_estimate_of_public_pictures":
        "A qualified authorial estimate introduced by 'We can safely assume'; preserve it as an interpretation, not a relationship.",
    "st-chp5-p130-higher_social_scale_limited_information":
        "The passage states an information limit and introduces possibilities; it does not assert a specific relationship involving the occupational groups.",
    "st-chp5-p130-mancini_addresses_public":
        "The source explicitly says Mancini was among the first to address the anonymous patron group; the group is source-defined and unnamed.",
    "st-chp5-p130-mancini_bargaining_advice":
        "The passage attributes practical price-bargaining advice to Mancini for the named-in-source lower-status group; the conditional wording is retained.",
    "st-chp5-p130-mancini_social_categories":
        "This is Mancini's reported distinction and assessment of social categories, not a formal person-to-person, work, or institution relation.",
    "st-chp5-p130-mancini_treatise_section":
        "The source identifies the Treatise as Mancini's and describes its section; this is an author-work candidate only. The title and edition remain unresolved, and cand-6066 is not equated with the index lead.",
    "st-chp5-p130-mancini_two_rooms_and_hanging":
        "The passage reports Mancini's guidance to the lower-status picture-buying group; preserve the source's likelihood and normative wording.",
    "st-chp5-p130-modern_attitude_and_giustiniani":
        "A source-relative historical interpretation that names Giustiniani as one example; the abstract attitude is not independently named as a bounded entity here.",
    "st-chp5-p130-new_subjects_in_early_seventeenth_century":
        "Haskell's causal interpretation of changing subject matter; it names genres but no individual works or explicit work-level relation.",
    "st-chp5-p130-sassoferrato_possible_public_patronage":
        "The patronage is posed as a hypothetical question, while the follower attribution is anonymous and the referenced plate does not identify the plural work group; retain the source claim without asserting a formal edge.",
    "st-chp5-p130-shift_and_theoretical_counterattacks":
        "A comparative authorial assessment; the theorists and their texts are unnamed and no bounded relation is asserted.",
    "st-chp5-p130-subject_matter_loses_primacy":
        "A generalized historical interpretation of a change in painting, not a formal relation between identified entities.",
    "st-chp5-p130-wider_public_takes_interest":
        "A broad source-level account of public interest and its influence on painting; the object of influence is a general process rather than a bounded entity.",
    "st-chp5-p130-young_artists_public_employment":
        "The artist-to-public link is Haskell's explicit 'no doubt' inference about livelihood bargaining. The artist group is kept source-local; Rome is arrival context, not the relation's other endpoint.",
}

RELATION_FLAGS = {
    "st-chp5-p130-aesthetic-view-and-connoisseurs": False,
    "st-chp5-p130-anonymous_patrons_in_literature": False,
    "st-chp5-p130-artist-impressions-closure": False,
    "st-chp5-p130-caravaggio_flowers_figures_comment": True,
    "st-chp5-p130-devotional_mass_produced_or_copied": False,
    "st-chp5-p130-haskell_estimate_of_public_pictures": False,
    "st-chp5-p130-higher_social_scale_limited_information": False,
    "st-chp5-p130-mancini_addresses_public": True,
    "st-chp5-p130-mancini_bargaining_advice": True,
    "st-chp5-p130-mancini_social_categories": False,
    "st-chp5-p130-mancini_treatise_section": True,
    "st-chp5-p130-mancini_two_rooms_and_hanging": True,
    "st-chp5-p130-modern_attitude_and_giustiniani": False,
    "st-chp5-p130-new_subjects_in_early_seventeenth_century": False,
    "st-chp5-p130-sassoferrato_possible_public_patronage": False,
    "st-chp5-p130-shift_and_theoretical_counterattacks": False,
    "st-chp5-p130-subject_matter_loses_primacy": False,
    "st-chp5-p130-wider_public_takes_interest": False,
    "st-chp5-p130-young_artists_public_employment": True,
}

NEW_CANDIDATE = {
    "candidate_id": NEW_CANDIDATE_ID,
    "index_entry_id": "",
    "canonical_name": "Young artists newly arrived in Rome (unnamed group)",
    "index_page_range": "",
    "suggested_type": "term",
    "status": "open",
    "index_source_file": "",
    "sub_entry": "",
    "detail": "A source-defined group of young artists described as arriving in Rome and bargaining with the broad picture-buying public for a livelihood. Individuals, ages, and exact membership are unknown; keep distinct from the foreign-artist colony cand-3467 and the artists sought by foreign patrons cand-11789.",
    "exclude_reason": "",
    "candidate_origin": "body-mention",
    "candidate_source_ref": f"{SEGMENT}#L113",
}

MENTION_SPECS = [
    ("m-chp5-p130-0024", NEW_CANDIDATE_ID, "young artists", 2819,
     "Explicit source-defined collective; no individuals or exact membership are named."),
    ("m-chp5-p130-0025", NEW_CANDIDATE_ID, "they", 2866,
     "Corefers to the young artists arriving in Rome."),
    ("m-chp5-p130-0026", NEW_CANDIDATE_ID, "they", 2935,
     "Corefers to the young artists bargaining with the public for their livelihood."),
]


def read_jsonl(path: Path) -> tuple[list[dict], list[str]]:
    raw_lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    return [json.loads(line) for line in raw_lines if line.strip()], raw_lines


def read_csv(path: Path) -> tuple[list[dict], list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames or [])
        return list(reader), fields


def make_mention(mid: str, cid: str, surface: str, at: int, note: str) -> dict:
    exact(segment_text, surface, at)
    return {"mention_id": mid, "segment_id": SEGMENT, "candidate_id": cid,
            "surface_form": surface, "start_char": str(at),
            "end_char": str(at + len(surface)), "note": note}


def build_plan() -> dict:
    for filename, digest in EXPECTED.items():
        path = TABLES / filename
        need(path.exists() and sha256(path) == digest, f"table changed since review: {filename}")
    need(not (TABLES / "book-statements.jsonl").read_bytes().startswith(codecs.BOM_UTF8),
         "statement JSONL encoding changed; refusing rewrite")
    need(sha256(SOURCE) == SOURCE_SHA, "source asset changed since review")
    need(sha256(PDF) == PDF_SHA, "CHP-5.pdf changed since review")
    need(sha256(PAGE_IMAGE) == IMAGE_SHA, "p.130 page image changed since review")
    need(hashlib.sha256(segment_text.encode("utf-8")).hexdigest() == SEGMENT_SHA,
         "p.130 segment fingerprint changed")

    statements_path = TABLES / "book-statements.jsonl"
    statements, raw_statement_lines = read_jsonl(statements_path)
    by_id = {row["statement_id"]: row for row in statements}
    target_rows = [row for row in statements if row.get("segment_id") == SEGMENT]
    target_ids = {row["statement_id"] for row in target_rows}
    need(target_ids == set(RELATION_FLAGS),
         f"p.130 statement inventory changed: {sorted(target_ids ^ set(RELATION_FLAGS))}")
    for row in target_rows:
        need((row.get("qualifiers") or {}).get("relation_candidate") is None,
             f"expected unclassified p.130 statement: {row['statement_id']}")
        need(row.get("original_quote", "") in segment_text,
             f"statement quote no longer matches the p.130 segment: {row['statement_id']}")
    need(set(STATEMENT_NOTES) == target_ids, "relation classification notes do not cover all statements")

    candidates_path = TABLES / "entity-candidates.csv"
    candidates, candidate_fields = read_csv(candidates_path)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    need(NEW_CANDIDATE_ID not in candidate_by_id, "new candidate ID already exists")
    natural_key = (NEW_CANDIDATE["canonical_name"].strip().casefold(), NEW_CANDIDATE["suggested_type"].strip().casefold())
    need(not any((r["canonical_name"].strip().casefold(), r["suggested_type"].strip().casefold()) == natural_key
                 for r in candidates), "duplicate candidate natural key")

    mentions_path = TABLES / "mentions.csv"
    mentions, mention_fields = read_csv(mentions_path)
    mention_by_id = {row["mention_id"]: row for row in mentions}
    need(not (NEW_MENTION_IDS & set(mention_by_id)), "one or more new mention IDs already exist")
    p130_mentions = [row for row in mentions if row.get("segment_id") == SEGMENT]
    for row in p130_mentions:
        start, end = int(row["start_char"]), int(row["end_char"])
        need(segment_text[start:end] == row["surface_form"],
             f"existing p.130 mention span mismatch: {row['mention_id']}")
    new_mentions = [make_mention(*spec) for spec in MENTION_SPECS]
    spans = [(int(m["start_char"]), int(m["end_char"])) for m in p130_mentions + new_mentions]
    need(len(spans) == len(set(spans)), "duplicate p.130 mention spans")

    updates = {}
    for sid, relation in RELATION_FLAGS.items():
        row = by_id[sid]
        q = dict(row.get("qualifiers") or {})
        q["relation_candidate"] = relation
        q["relation_candidate_note"] = STATEMENT_NOTES[sid]
        update = {"qualifiers": q}
        if sid == "st-chp5-p130-mancini_treatise_section":
            update["predicate"] = "authored_treatise_with_picture_acquisition_and_display_section"
        if sid == "st-chp5-p130-young_artists_public_employment":
            update.update({
                "subject_candidate_id": NEW_CANDIDATE_ID,
                "object_candidate_id": "cand-6064",
                "predicate": "bargained_with_picture_buying_public_for_livelihood",
            })
            q["claim"] = "Haskell reports that young artists were often employed on devotional pictures when first arriving in Rome, and infers that this was the public with whom they bargained for their livelihood."
            q["qualification"] = "The phrase 'no doubt' marks the public-as-livelihood link as Haskell's inference; individual artists, buyers, and specific transactions are unnamed. Rome is arrival context, not the relation's other endpoint."
            q["mentioned_candidate_ids"] = [NEW_CANDIDATE_ID, "cand-6064", "cand-4490"]
            q["group_identity_status"] = "source_defined_group; no identity merge"
        updates[sid] = update

    for sid, update in updates.items():
        if update["qualifiers"]["relation_candidate"]:
            row = by_id[sid]
            subject = update.get("subject_candidate_id", row.get("subject_candidate_id"))
            obj = update.get("object_candidate_id", row.get("object_candidate_id"))
            need(subject and obj, f"true relation candidate missing endpoint: {sid}")

    return {
        "statements": statements,
        "raw_statement_lines": raw_statement_lines,
        "updates": updates,
        "candidates": candidates,
        "candidate_fields": candidate_fields,
        "mentions": mentions,
        "mention_fields": mention_fields,
        "new_mentions": new_mentions,
        "p130_existing_mentions": len(p130_mentions),
    }


def render_jsonl(plan: dict) -> bytes:
    updates = plan["updates"]
    out = []
    for raw in plan["raw_statement_lines"]:
        if not raw.strip():
            out.append(raw)
            continue
        obj = json.loads(raw)
        update = updates.get(obj.get("statement_id"))
        if update:
            obj.update(update)
            ending = "\r\n" if raw.endswith("\r\n") else "\n" if raw.endswith("\n") else ""
            out.append(json.dumps(obj, ensure_ascii=False) + (ending or "\n"))
        else:
            out.append(raw)
    return "".join(out).encode("utf-8")


def render_csv(rows: list[dict], fields: list[str], new_rows: list[dict], bom: bool) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="raise", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows + new_rows)
    content = buffer.getvalue().encode("utf-8")
    return (codecs.BOM_UTF8 + content) if bom else content


def atomic_write(path: Path, content: bytes) -> None:
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main() -> None:
    parser = argparse.ArgumentParser(description="Controlled S2 p.130 writeback; dry-run by default.")
    parser.add_argument("--apply", action="store_true", help="write the reviewed exact change set")
    args = parser.parse_args()
    plan = build_plan()

    statement_path = TABLES / "book-statements.jsonl"
    candidate_path = TABLES / "entity-candidates.csv"
    mention_path = TABLES / "mentions.csv"
    outputs = {
        statement_path: render_jsonl(plan),
        candidate_path: render_csv(plan["candidates"], plan["candidate_fields"], [NEW_CANDIDATE],
                                  candidate_path.read_bytes().startswith(codecs.BOM_UTF8)),
        mention_path: render_csv(plan["mentions"], plan["mention_fields"], plan["new_mentions"],
                                 mention_path.read_bytes().startswith(codecs.BOM_UTF8)),
    }
    true_count = sum(RELATION_FLAGS.values())
    false_count = len(RELATION_FLAGS) - true_count
    print("S2 p.130 dry-run / exact plan")
    print(f"source sha256: {sha256(SOURCE)}")
    print(f"PDF sha256: {sha256(PDF)}")
    print(f"page image sha256: {sha256(PAGE_IMAGE)}")
    print(f"existing statements classified: {len(RELATION_FLAGS)} ({true_count} relation candidates, {false_count} non-relational)")
    print(f"new candidates: 1 ({NEW_CANDIDATE_ID}); new precise mentions: {len(plan['new_mentions'])}; existing page mentions validated: {plan['p130_existing_mentions']}")
    for path, content in outputs.items():
        print(f"{path.relative_to(ROOT)}: {sha256(path)} -> {hashlib.sha256(content).hexdigest()} ({len(content)} bytes)")
    if not args.apply:
        print("dry-run only; no tables written")
        return

    backups = {}
    suffix = ".bak-s2-chp5-p130-20261012"
    for path in outputs:
        backup = path.with_name(path.name + suffix)
        need(not backup.exists(), f"recovery copy already exists; refusing overwrite: {backup.name}")
        shutil.copy2(path, backup)
        need(sha256(backup) == EXPECTED[path.name], f"recovery copy hash mismatch: {backup.name}")
        backups[path] = backup
    for path, content in outputs.items():
        atomic_write(path, content)
    for path in outputs:
        print(f"applied {path.relative_to(ROOT)} sha256={sha256(path)} backup={backups[path].name}")
    print("apply complete")


if __name__ == "__main__":
    main()
