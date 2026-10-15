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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "05_CHP-5_sec_iii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-5.pdf"
PAGE_IMAGE = PROCESS / "p132_page_review_20261012.png"
SOURCE_FILE = "02-sources/02-Markdown/05_CHP-5_sec_iii.md"
OPENER_SEGMENT = "chp-5:05_CHP-5_sec_iii:l3-3"
BODY_SEGMENT = "chp-5:05_CHP-5_sec_iii:l5-10"
EXPECTED = {
    "book-statements.jsonl": "9f7e0afbcab377046e424239c700619cfdb2fc4bf3815b0c62ac7d8c76972ac7",
    "entity-candidates.csv": "e1ec0370f8250872ee452e0f70546652cd22078705871000f735954de7952dc5",
    "mentions.csv": "723ae0da9bec22eb6379a4999f094f3d8010b2c0d71707e2fced87651432d4f2",
}
SOURCE_SHA = "9b095b1a93570102ad2cdb117580f2fbeccd2ff017033a2f66557c58a0d1ef0a"
PDF_SHA = "f63dca79808fde73ba10aa9414fef89bc8ca5e77ed829b2d5c86f23719e0674a"
IMAGE_SHA = "58d8cef4152d2c383e4019caac0e1d9be2b3db2de1cefac8345d598a44f53489"
OPENER_SHA = "80f0e4c372eccb56f69bdcc201a74504380a1c88ead844d4b31c231e323d1277"
BODY_SHA = "e306d5e3b7c6e8bb64829e9dcc00a3b612e066a4669ab6a0ef0920ddfbb21e38"

source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
opener_text = "\n".join(source_lines[2:3])
body_text = "\n".join(source_lines[4:10])


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def exact(text: str, quote: str) -> str:
    need(quote in text, f"source quote not found: {quote!r}")
    return quote


def qualifier(segment: str, line_start: int, line_end: int, claim: str,
              qualification: str, mentioned: list[str], relation: bool,
              printed_page: str = "p.132", **extra) -> dict:
    q = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page_locator": printed_page,
        "pdf_physical_page": 13,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "authorial narrative",
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation,
        "relation_candidate_note": (
            "Source-grounded S2 relation candidate only; no formal S6 edge is created."
            if relation else
            "Retained as a source claim, but not a candidate for a formal entity relation."
        ),
    }
    q.update(extra)
    return q


NEW_CANDIDATES = [
    {
        "candidate_id": "cand-11799", "index_entry_id": "",
        "canonical_name": "Highest ranks of society supporting the bambocciate (source-defined group)",
        "index_page_range": "", "suggested_type": "term", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "Haskell says support for the bambocciate eventually came from society's highest ranks. Members are not named; keep this later group distinct from the source-quoted people of middling and lower status.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY_SEGMENT}#L7",
    },
    {
        "candidate_id": "cand-11800", "index_entry_id": "",
        "canonical_name": "Artists willing to gratify self-made patrons' taste (source-defined group)",
        "index_page_range": "", "suggested_type": "term", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "Conditional group in Haskell's account of non-elite patrons: artists attracted by patrons influential enough to gratify their taste. No members or particular works are named.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY_SEGMENT}#L6",
    },
]

NEW_MENTIONS = []


def new_statement(sid: str, subject: str | None, obj: str | None, predicate: str,
                  quote: str, line_start: int, claim: str, qualification: str,
                  mentioned: list[str], relation: bool, **extra) -> dict:
    return {
        "statement_id": sid,
        "segment_id": BODY_SEGMENT,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifier(BODY_SEGMENT, line_start, line_start, claim, qualification,
                                mentioned, relation, **extra),
        "original_quote": exact(body_text, quote),
        "origin": "book",
        "source_file": SOURCE_FILE,
    }


NEW_STATEMENTS = [
    new_statement(
        "st-chp5-p132-highest-ranks-support-bambocciate", "cand-11799", "cand-6099",
        "eventually_supported", "this support eventually came from the highest ranks of society", 7,
        "Haskell says support for the bambocciate eventually came from society's highest ranks.",
        "The group is unnamed and unenumerated; 'eventually' is retained as the source's temporal qualification.",
        ["cand-11799", "cand-6099"], True,
        temporal_context="eventually; no dates or members specified",
        additional_cause_of_indignation=True,
    ),
    new_statement(
        "st-chp5-p132-nonelite-denunciations-after-influence", "cand-6096", None,
        "denunciations_became_many_and_scathing", "denunciations have been many and scathing. Such was the case in Baroque Italy.", 6,
        "Haskell says the rise of influential self-made patrons in Baroque Italy brought numerous and severe denunciations.",
        "The critics and objects of individual denunciations are not named; preserve this as the author's general historical account.",
        ["cand-6096", "cand-6098", "cand-3461"], False,
        temporal_context="Baroque Italy; no individual event or critic identified",
    ),
    new_statement(
        "st-chp5-p132-bamboccianti-set-in-campagna", "cand-0173", "cand-4243",
        "represented_world_set_in", "The setting is Rome and the campagna", 10,
        "Haskell places the represented world of the Bamboccianti in the campagna as well as Rome.",
        "The source uses the generic lower-case 'campagna'; its exact geographic extent is unspecified.",
        ["cand-0173", "cand-4243", "cand-4490"], True,
        spatial_role="rural setting",
        temporal_context="the 1630s and 1640s",
    ),
]

RELATION_FLAGS = {
    "st-chp5-sec-iii-l3-self-made-taste": True,
    "st-chp5-p132-bambocciate-support-and-origin": True,
    "st-chp5-p132-brigand-violence-scene": False,
    "st-chp5-p132-group-name-and-leader": True,
    "st-chp5-p132-historical-subjects-as-everyday-life": False,
    "st-chp5-p132-ignorant-patrons-attacked": False,
    "st-chp5-p132-leisure-and-festival-scenes": False,
    "st-chp5-p132-movement-history-and-patronage": False,
    "st-chp5-p132-nonelite-taste-and-denunciation": True,
    "st-chp5-p132-passeri-window-on-life": True,
    "st-chp5-p132-picturesque-taste-across-cultures": False,
    "st-chp5-p132-rare-donkey-death-narrative": False,
    "st-chp5-p132-rome-and-campagna-date": True,
    "st-chp5-p132-rome-not-tourist-city": False,
    "st-chp5-p132-rome-remains-and-trade": False,
    "st-chp5-p132-work-scenes": False,
}

RELATION_NOTES = {
    "st-chp5-sec-iii-l3-self-made-taste": "Explicit relation between Haskell's source-defined social category and the established canons; the evaluative term 'offensive' remains Haskell's wording.",
    "st-chp5-p132-bambocciate-support-and-origin": "Haskell says there is reason to believe the initial support came from the quoted middling/lower-status group; this is his qualified attribution, not a complete patron list.",
    "st-chp5-p132-brigand-violence-scene": "A generalized description of a pictorial scene; no individual work or separately identified subject entity is named.",
    "st-chp5-p132-group-name-and-leader": "The source connects the derisive group name to the nickname of its leader Pieter van Laer; the nickname itself is not supplied.",
    "st-chp5-p132-historical-subjects-as-everyday-life": "A generalized account of how historical subjects function as settings in an artistic mode; no specific picture is identified.",
    "st-chp5-p132-ignorant-patrons-attacked": "An authorial generalization about attacks on a social category; the attackers and individual attacks are not identified.",
    "st-chp5-p132-leisure-and-festival-scenes": "A list of generic depicted activities, not relations to named or individually identifiable works.",
    "st-chp5-p132-movement-history-and-patronage": "A methodological and evaluative statement about what the movement's history reveals, not a dyadic entity relation.",
    "st-chp5-p132-nonelite-taste-and-denunciation": "Conditional relation from influential self-made patrons to artists willing to gratify their taste; the separate general claim about denunciations is split into its own non-relational statement.",
    "st-chp5-p132-passeri-window-on-life": "Haskell attributes the characterization of the Bamboccianti as opening a window onto life to critic Giambattista Passeri.",
    "st-chp5-p132-picturesque-taste-across-cultures": "A broad cross-cultural generalization about uninitiated taste and artistic response; the artists and resulting works are not bounded entities.",
    "st-chp5-p132-rare-donkey-death-narrative": "An illustrative, unnamed narrative scene; the source does not identify a particular picture.",
    "st-chp5-p132-rome-and-campagna-date": "The source locates the Bamboccianti's represented world in Rome during the 1630s and 1640s; the campagna location is split into a separate endpoint statement.",
    "st-chp5-p132-rome-not-tourist-city": "A contrast in the author's portrayal of Rome, without a separately identifiable second city or entity endpoint.",
    "st-chp5-p132-rome-remains-and-trade": "Generalized description of urban scenery and commerce; the sentence continues onto p.133 and names no individual transaction or work.",
    "st-chp5-p132-work-scenes": "A generalized list of labor subjects represented in the genre; no individual picture or bounded work group is identified.",
}


def read_jsonl(path: Path) -> tuple[list[dict], list[str]]:
    raw = path.read_text(encoding="utf-8").splitlines(keepends=True)
    return [json.loads(line) for line in raw if line.strip()], raw


def read_csv(path: Path) -> tuple[list[dict], list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader), list(reader.fieldnames or [])


def build_plan() -> dict:
    for filename, digest in EXPECTED.items():
        path = TABLES / filename
        need(path.exists() and sha256(path) == digest, f"table changed since review: {filename}")
    need(sha256(SOURCE) == SOURCE_SHA, "source asset changed since review")
    need(sha256(PDF) == PDF_SHA, "CHP-5.pdf changed since review")
    need(sha256(PAGE_IMAGE) == IMAGE_SHA, "p.132 page image changed since review")
    need(hashlib.sha256(opener_text.encode("utf-8")).hexdigest() == OPENER_SHA, "p.132 opener segment changed")
    need(hashlib.sha256(body_text.encode("utf-8")).hexdigest() == BODY_SHA, "p.132 body segment changed")

    statement_path = TABLES / "book-statements.jsonl"
    statements, raw_statement_lines = read_jsonl(statement_path)
    by_id = {r["statement_id"]: r for r in statements}
    targets = [r for r in statements if r.get("segment_id") in {OPENER_SEGMENT, BODY_SEGMENT}]
    target_ids = {r["statement_id"] for r in targets}
    need(target_ids == set(RELATION_FLAGS), f"p.132 statement inventory changed: {sorted(target_ids ^ set(RELATION_FLAGS))}")
    need(set(RELATION_NOTES) == target_ids, "classification notes do not cover every p.132 statement")
    for row in targets:
        text = opener_text if row.get("segment_id") == OPENER_SEGMENT else body_text
        need(row.get("original_quote", "") in text, f"source quote moved: {row['statement_id']}")
        need((row.get("qualifiers") or {}).get("relation_candidate") is None,
             f"unexpected prior classification: {row['statement_id']}")

    candidate_path = TABLES / "entity-candidates.csv"
    candidates, candidate_fields = read_csv(candidate_path)
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    new_candidate_ids = {r["candidate_id"] for r in NEW_CANDIDATES}
    need(not (new_candidate_ids & set(candidate_by_id)), "new candidate id collision")
    natural_keys = {(r["canonical_name"].strip().casefold(), r["suggested_type"].strip().casefold()) for r in candidates}
    for row in NEW_CANDIDATES:
        key = (row["canonical_name"].strip().casefold(), row["suggested_type"].strip().casefold())
        need(key not in natural_keys, f"duplicate candidate natural key: {row['canonical_name']}")
        natural_keys.add(key)

    mention_path = TABLES / "mentions.csv"
    mentions, mention_fields = read_csv(mention_path)
    mention_by_id = {r["mention_id"]: r for r in mentions}
    page_mentions = [r for r in mentions if r.get("segment_id") in {OPENER_SEGMENT, BODY_SEGMENT}]
    for row in page_mentions:
        text = opener_text if row.get("segment_id") == OPENER_SEGMENT else body_text
        start, end = int(row["start_char"]), int(row["end_char"])
        need(text[start:end] == row["surface_form"], f"existing p.132 mention span mismatch: {row['mention_id']}")
    new_candidate_ids |= set(candidate_by_id)
    for mention_id, candidate_id, surface, line_hint in [
        ("m-chp5-p132-0017", "cand-11799", "the highest ranks of society", 7),
        ("m-chp5-p132-0018", "cand-11800", "artists willing to gratify him", 6),
    ]:
        need(mention_id not in mention_by_id, f"mention id collision: {mention_id}")
        start = body_text.find(surface)
        need(start >= 0 and body_text.count(surface) == 1, f"mention surface not unique: {surface}")
        NEW_MENTIONS.append({
            "mention_id": mention_id, "segment_id": BODY_SEGMENT, "candidate_id": candidate_id,
            "surface_form": surface, "start_char": str(start), "end_char": str(start + len(surface)),
            "note": ("Unnamed, source-defined social group; no members are specified." if line_hint == 7
                     else "Unnamed, conditional artist group in Haskell's account; no members or specific works are named."),
        })

    updates = {}
    for row in targets:
        q = dict(row.get("qualifiers") or {})
        q["relation_candidate"] = RELATION_FLAGS[row["statement_id"]]
        q["relation_candidate_note"] = RELATION_NOTES[row["statement_id"]]
        updates[row["statement_id"]] = {"qualifiers": q}

    def update_row(sid: str, **fields) -> None:
        updates[sid].update(fields)

    update_row("st-chp5-sec-iii-l3-self-made-taste",
               qualifiers={**updates["st-chp5-sec-iii-l3-self-made-taste"]["qualifiers"],
                           "claim": "Haskell says the self-made man has often expressed an artistic taste offensive to established canons.",
                           "printed_reading_correction": {"ocr": "estabhshed canons", "print": "established canons"},
                           "mentioned_candidate_ids": ["cand-6096", "cand-6097", "cand-6098"]})
    update_row("st-chp5-p132-bambocciate-support-and-origin",
               subject_candidate_id="cand-6065", object_candidate_id="cand-6099",
               predicate="initial_support_for_bambocciate_probably_came_from",
               original_quote=exact(body_text, "there is reason to believe that it started with the ‘uomini di stato mediocre e di stato basso’"),
               qualifiers={**updates["st-chp5-p132-bambocciate-support-and-origin"]["qualifiers"],
                           "claim": "Haskell says there is reason to believe initial support for the bambocciate came from people of middling and lower status.",
                           "qualification": "Haskell's inferred origin; the quoted social categories are retained as a source-defined group, not a member list.",
                           "mentioned_candidate_ids": ["cand-6065", "cand-6099"],
                           "claim_status": "qualified authorial inference"})
    update_row("st-chp5-p132-group-name-and-leader",
               original_quote=exact(body_text, "so called in derision from the nickname given to their deformed leader Pieter van Laer"),
               qualifiers={**updates["st-chp5-p132-group-name-and-leader"]["qualifiers"],
                           "mentioned_candidate_ids": ["cand-0173", "cand-1351"],
                           "qualification": "The nickname is not supplied; 'deformed' is Haskell's description and is not treated as an identity attribute."})
    update_row("st-chp5-p132-nonelite-taste-and-denunciation",
               subject_candidate_id="cand-6096", object_candidate_id="cand-11800",
               predicate="influence_attracted_artists_willing_to_gratify_taste",
               original_quote=exact(body_text, "when singly or in concert with his fellows he has become sufficiently influential to attract artists willing to gratify him"),
               qualifiers={**updates["st-chp5-p132-nonelite-taste-and-denunciation"]["qualifiers"],
                           "claim": "Haskell says self-made patrons who gain sufficient influence, singly or with peers, can attract artists willing to gratify their taste.",
                           "mentioned_candidate_ids": ["cand-6096", "cand-6097", "cand-6098", "cand-11800", "cand-3461"],
                           "related_statement_ids": ["st-chp5-p132-nonelite-denunciations-after-influence"]})
    update_row("st-chp5-p132-passeri-window-on-life",
               subject_candidate_id="cand-1856", object_candidate_id="cand-0173",
               predicate="characterized_group_as_opening_window_onto_life",
               original_quote=exact(body_text, "(in the words of the critic Giambattista Passeri) opening a window on to life"),
               qualifiers={**updates["st-chp5-p132-passeri-window-on-life"]["qualifiers"],
                           "mentioned_candidate_ids": ["cand-1856", "cand-0173"]})
    update_row("st-chp5-p132-rome-and-campagna-date",
               subject_candidate_id="cand-0173", object_candidate_id="cand-4490",
               predicate="represented_world_set_in_during_period",
               original_quote=exact(body_text, "The setting is Rome and the campagna"),
               qualifiers={**updates["st-chp5-p132-rome-and-campagna-date"]["qualifiers"],
                           "claim": "Haskell places the Bamboccianti's represented world in Rome in the 1630s and 1640s.",
                           "mentioned_candidate_ids": ["cand-0173", "cand-4490", "cand-4243"],
                           "temporal_context": "the 1630s and 1640s",
                           "related_statement_ids": ["st-chp5-p132-bamboccianti-set-in-campagna"]})

    updates["st-chp5-p132-nonelite-taste-and-denunciation"]["qualifiers"]["relation_candidate_note"] = RELATION_NOTES["st-chp5-p132-nonelite-taste-and-denunciation"]
    updates["st-chp5-p132-nonelite-taste-and-denunciation"]["qualifiers"]["relation_candidate"] = True
    existing_ids = set(by_id)
    new_ids = {r["statement_id"] for r in NEW_STATEMENTS}
    need(len(new_ids) == len(NEW_STATEMENTS) and not (new_ids & existing_ids), "new statement id collision")
    all_candidate_ids = set(candidate_by_id) | {r["candidate_id"] for r in NEW_CANDIDATES}
    for row in NEW_STATEMENTS:
        for key in ("subject_candidate_id", "object_candidate_id"):
            cid = row.get(key)
            if row["qualifiers"]["relation_candidate"]:
                need(cid and cid in all_candidate_ids, f"new relation endpoint invalid: {row['statement_id']} {key}={cid}")
    for sid, update in updates.items():
        row = by_id[sid]
        q = update["qualifiers"]
        if q["relation_candidate"]:
            for key in ("subject_candidate_id", "object_candidate_id"):
                cid = update.get(key, row.get(key))
                need(cid and cid in all_candidate_ids, f"relation endpoint invalid: {sid} {key}={cid}")
        for cid in q.get("mentioned_candidate_ids", []):
            need(cid in all_candidate_ids, f"mentioned candidate invalid: {sid} -> {cid}")
    for mention in NEW_MENTIONS:
        need(mention["candidate_id"] in all_candidate_ids, f"mention candidate invalid: {mention['mention_id']}")
        start, end = int(mention["start_char"]), int(mention["end_char"])
        need(body_text[start:end] == mention["surface_form"], f"new mention span mismatch: {mention['mention_id']}")

    return {
        "raw_statement_lines": raw_statement_lines,
        "updates": updates,
        "new_statements": NEW_STATEMENTS,
        "candidates": candidates,
        "candidate_fields": candidate_fields,
        "mentions": mentions,
        "mention_fields": mention_fields,
    }


def render_jsonl(plan: dict) -> bytes:
    out = []
    for raw in plan["raw_statement_lines"]:
        if not raw.strip():
            out.append(raw)
            continue
        row = json.loads(raw)
        update = plan["updates"].get(row.get("statement_id"))
        if update:
            row.update(update)
            ending = "\r\n" if raw.endswith("\r\n") else "\n" if raw.endswith("\n") else "\n"
            out.append(json.dumps(row, ensure_ascii=False) + ending)
        else:
            out.append(raw)
    out.extend(json.dumps(row, ensure_ascii=False) + "\n" for row in plan["new_statements"])
    return "".join(out).encode("utf-8")


def render_csv(rows: list[dict], fields: list[str], new_rows: list[dict], bom: bool) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="raise", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows + new_rows)
    data = buffer.getvalue().encode("utf-8")
    return codecs.BOM_UTF8 + data if bom else data


def atomic_write(path: Path, data: bytes) -> None:
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main() -> None:
    parser = argparse.ArgumentParser(description="Controlled S2 p.132 writeback; dry-run by default.")
    parser.add_argument("--apply", action="store_true", help="write the reviewed exact change set")
    args = parser.parse_args()
    plan = build_plan()
    statement_path = TABLES / "book-statements.jsonl"
    candidate_path = TABLES / "entity-candidates.csv"
    mention_path = TABLES / "mentions.csv"
    outputs = {
        statement_path: render_jsonl(plan),
        candidate_path: render_csv(plan["candidates"], plan["candidate_fields"], NEW_CANDIDATES,
                                   candidate_path.read_bytes().startswith(codecs.BOM_UTF8)),
        mention_path: render_csv(plan["mentions"], plan["mention_fields"], NEW_MENTIONS,
                                 mention_path.read_bytes().startswith(codecs.BOM_UTF8)),
    }
    true_count = sum(bool(x) for x in RELATION_FLAGS.values()) + sum(bool(x["qualifiers"]["relation_candidate"]) for x in NEW_STATEMENTS)
    total_count = len(RELATION_FLAGS) + len(NEW_STATEMENTS)
    print("S2 p.132 dry-run / exact plan")
    print(f"source sha256: {sha256(SOURCE)}")
    print(f"page image sha256: {sha256(PAGE_IMAGE)}")
    print(f"existing statements classified: {len(RELATION_FLAGS)}; added statements: {len(NEW_STATEMENTS)}")
    print(f"final statements: {total_count} ({true_count} relation candidates, {total_count - true_count} non-relational)")
    print(f"new candidates: {len(NEW_CANDIDATES)}; new mentions: {len(NEW_MENTIONS)}; existing body mentions checked: {sum(1 for r in plan['mentions'] if r.get('segment_id') in {OPENER_SEGMENT, BODY_SEGMENT})}")
    for path, data in outputs.items():
        print(f"{path.relative_to(ROOT)}: {sha256(path)} -> {hashlib.sha256(data).hexdigest()} ({len(data)} bytes)")
    if not args.apply:
        print("dry-run only; no tables written")
        return

    backups = {}
    suffix = ".bak-s2-chp5-p132-20261012"
    for path in outputs:
        backup = path.with_name(path.name + suffix)
        need(not backup.exists(), f"recovery copy already exists: {backup.name}")
        shutil.copy2(path, backup)
        need(sha256(backup) == EXPECTED[path.name], f"recovery copy hash mismatch: {backup.name}")
        backups[path] = backup
    for path, data in outputs.items():
        atomic_write(path, data)
    for path in outputs:
        print(f"applied {path.relative_to(ROOT)} sha256={sha256(path)} backup={backups[path].name}")
    print("apply complete")


if __name__ == "__main__":
    main()
