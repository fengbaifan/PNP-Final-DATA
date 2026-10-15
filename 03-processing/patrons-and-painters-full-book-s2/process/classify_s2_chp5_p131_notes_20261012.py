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
PAGE_IMAGE = PROCESS / "p131_page_review_20261012.png"
SEGMENT = "chp-5:05_CHP-5_sec_i:l125-147"
SOURCE_FILE = "02-sources/02-Markdown/05_CHP-5_sec_i.md"
EXPECTED = {
    "book-statements.jsonl": "94e49cde4b1c7adc35c95ecadf0494d6414ebb7736006f446c6987f6c1f61ef8",
    "entity-candidates.csv": "311cf9ed9935f5c12c6f3b4d1a23571a01ff0d69208af2f488bee39d1c6ee687",
    "mentions.csv": "3c5dfb6aa984776063f2f74822eec6382394831049495908192316222cb3d842",
}
SOURCE_SHA = "8ef51cd646ed6abf398c9faeb47df9a03f70de696d9a871c6d0b734b2adeeeee"
PDF_SHA = "f63dca79808fde73ba10aa9414fef89bc8ca5e77ed829b2d5c86f23719e0674a"
IMAGE_SHA = "9231ae7a3aca9649bd6a5f8cfb3218a7b3fbe6927f839b97207e69572a7f8a96"
SEGMENT_SHA = "5fdb179fd5637ce1d0a0b6b3da66e4e871452e25debcd265e4749060845324e8"

source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
segment_text = "\n".join(source_lines[124:147])


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def exact(quote: str) -> str:
    need(quote in segment_text, f"source quote not found: {quote!r}")
    return quote


def relation_qualifier(line_start: int, line_end: int, claim: str,
                       qualification: str, mentioned: list[str], **extra) -> dict:
    q = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page_locator": "p.131n3",
        "pdf_physical_page": 12,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "authorial footnote reporting a portrait and career detail",
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": True,
        "relation_candidate_note": "S2 source-grounded relation candidate only; no formal S6 edge is created.",
    }
    q.update(extra)
    return q


NEW_STATEMENTS = [
    {
        "statement_id": "st-chp5-note-p131-n3-portrait-located-galleria",
        "segment_id": SEGMENT,
        "subject_candidate_id": "cand-6091",
        "object_candidate_id": "cand-3247",
        "predicate": "portrait_reported_at_institution",
        "qualifiers": relation_qualifier(
            147, 147,
            "Haskell reports that the signed portrait of Ottaviano Prati was in the Galleria Nazionale di Arte Antica in Rome.",
            "Location as reported in this footnote; present custody and current institutional identity are not independently checked.",
            ["cand-6091", "cand-3247", "cand-4490"],
            ocr_correction="Galleria N azionale -> Galleria Nazionale; pp. 102 if -> pp. 102 ff.; verified against the p.131 print scan",
        ),
        "original_quote": exact("In the Galleria N azionale di Arte Antica in Rome is a signed portrait of Monsignor Ottaviano Prati"),
        "origin": "book",
        "source_file": SOURCE_FILE,
    },
    {
        "statement_id": "st-chp5-note-p131-n3-prati-governor-benevento",
        "segment_id": SEGMENT,
        "subject_candidate_id": "cand-6090",
        "object_candidate_id": "cand-6093",
        "predicate": "served_as_governor_of",
        "qualifiers": relation_qualifier(
            147, 147,
            "Haskell reports that Ottaviano Prati served as governor of Benevento.",
            "The source says the appointments were at different times but supplies no dates.",
            ["cand-6090", "cand-6093"],
            office_title="Governor",
            temporal_context="at different times; dates unspecified",
        ),
        "original_quote": exact("who at different times was Governor of Benevento and Viterbo"),
        "origin": "book",
        "source_file": SOURCE_FILE,
    },
    {
        "statement_id": "st-chp5-note-p131-n3-prati-governor-viterbo",
        "segment_id": SEGMENT,
        "subject_candidate_id": "cand-6090",
        "object_candidate_id": "cand-6094",
        "predicate": "served_as_governor_of",
        "qualifiers": relation_qualifier(
            147, 147,
            "Haskell reports that Ottaviano Prati served as governor of Viterbo.",
            "The source says the appointments were at different times but supplies no dates.",
            ["cand-6090", "cand-6094"],
            office_title="Governor",
            temporal_context="at different times; dates unspecified",
        ),
        "original_quote": exact("who at different times was Governor of Benevento and Viterbo"),
        "origin": "book",
        "source_file": SOURCE_FILE,
    },
]


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
    need(sha256(PAGE_IMAGE) == IMAGE_SHA, "p.131 page image changed since review")
    need(hashlib.sha256(segment_text.encode("utf-8")).hexdigest() == SEGMENT_SHA,
         "p.131 notes segment fingerprint changed")

    statement_path = TABLES / "book-statements.jsonl"
    statements, raw_statement_lines = read_jsonl(statement_path)
    by_id = {r["statement_id"]: r for r in statements}
    targets = {
        "st-chp5-note-p131-n1-citation": True,
        "st-chp5-note-p131-n2-citation": True,
        "st-chp5-note-p131-n3-prati-portrait": True,
        "st-chp5-note-p131-n4-citation": True,
    }
    need(all(sid in by_id and by_id[sid].get("segment_id") == SEGMENT for sid in targets),
         "p.131 note statement inventory changed")
    for sid in targets:
        q = by_id[sid].get("qualifiers") or {}
        need(q.get("relation_candidate") is None, f"unexpected prior classification for {sid}")
        need(by_id[sid].get("original_quote", "") in segment_text, f"source quote moved for {sid}")

    candidate_path = TABLES / "entity-candidates.csv"
    candidates, candidate_fields = read_csv(candidate_path)
    candidate_ids = {r["candidate_id"] for r in candidates}
    required_candidates = {
        "cand-2962", "cand-4556", "cand-11246", "cand-6076",
        "cand-6090", "cand-6091", "cand-6093", "cand-6094", "cand-3247", "cand-4490",
    }
    need(required_candidates <= candidate_ids, f"missing required candidates: {sorted(required_candidates - candidate_ids)}")

    mention_path = TABLES / "mentions.csv"
    mentions, mention_fields = read_csv(mention_path)
    mention_ids = {r["mention_id"] for r in mentions}
    mention_by_id = {r["mention_id"]: r for r in mentions}
    need("m-chp5-note-L147-050" in mention_by_id and
         mention_by_id["m-chp5-note-L147-050"].get("candidate_id") == "cand-4142",
         "Galleria mention mapping changed")
    new_mentions = []
    for mention_id, candidate_id, surface, note in [
        ("m-chp5-note-p131-n1-pollak-work", "cand-4556", "Pollak, I, 1927, p. 129",
         "Volume I locator; the bibliography identifies the two-volume work as cand-11421, retained separately for later volume reconciliation."),
        ("m-chp5-note-p131-n2-berthier-work", "cand-11246", "Berthier, p. 315",
         "Bibliographic work identified from the book's bibliography; contents not independently consulted."),
        ("m-chp5-note-p131-n4-gigli-diary", "cand-6076", "Gigli passim",
         "Diary edition identified in the book bibliography; edition not independently consulted."),
    ]:
        need(mention_id not in mention_ids, f"mention id already exists: {mention_id}")
        start = segment_text.find(surface)
        need(start >= 0, f"mention surface not found: {surface}")
        new_mentions.append({
            "mention_id": mention_id,
            "segment_id": SEGMENT,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(start + len(surface)),
            "note": note,
        })

    updates = {}
    for sid in targets:
        q = dict(by_id[sid].get("qualifiers") or {})
        q["relation_candidate"] = True
        q["relation_candidate_note"] = "S2 source-attributed relation candidate only; this classification does not create a formal S6 edge."
        updates[sid] = {"qualifiers": q}

    updates["st-chp5-note-p131-n1-citation"].update({
        "subject_candidate_id": "cand-2962",
        "object_candidate_id": "cand-4556",
        "predicate": "cites",
        "qualifiers": {
            **updates["st-chp5-note-p131-n1-citation"]["qualifiers"],
            "claim": "Haskell cites volume I of Pollak's 1927 publication, p.129, for the p.131 account of Sassoferrato and Cozza.",
            "qualification": "The book's bibliography identifies the two-volume work as cand-11421; the cited volume-I locator remains a separate open candidate for later volume-level reconciliation. The cited page was not independently consulted.",
            "mentioned_candidate_ids": ["cand-2962", "cand-4556"],
            "bibliography_match_candidate_id": "cand-11421",
        },
    })
    updates["st-chp5-note-p131-n2-citation"].update({
        "subject_candidate_id": "cand-2962",
        "object_candidate_id": "cand-11246",
        "predicate": "cites",
        "qualifiers": {
            **updates["st-chp5-note-p131-n2-citation"]["qualifiers"],
            "claim": "Haskell cites Berthier, p.315, in support of the p.131 commission and payment account.",
            "qualification": "The bibliography identifies the Rome 1910 publication; the cited page was not independently consulted.",
            "mentioned_candidate_ids": ["cand-2962", "cand-11246"],
        },
    })
    updates["st-chp5-note-p131-n3-prati-portrait"].update({
        "subject_candidate_id": "cand-6091",
        "object_candidate_id": "cand-6090",
        "predicate": "depicts",
        "original_quote": exact("a signed portrait of Monsignor Ottaviano Prati"),
        "qualifiers": {
            **updates["st-chp5-note-p131-n3-prati-portrait"]["qualifiers"],
            "claim": "Haskell reports that the signed portrait depicts Monsignor Ottaviano Prati.",
            "qualification": "The source reports the sitter; artist and date are not stated. Cited pages were not independently checked.",
            "mentioned_candidate_ids": ["cand-6091", "cand-6090"],
            "ocr_correction": "Galleria N azionale -> Galleria Nazionale; pp. 102 if -> pp. 102 ff.; verified against the p.131 print scan",
        },
    })
    mention_updates = {
        "m-chp5-note-L147-050": {
            "candidate_id": "cand-3247",
            "note": "The print identifies Galleria Nazionale di Arte Antica; mapped to the existing accepted institution KU. S0 OCR spacing is retained in the surface form.",
        }
    }
    updates["st-chp5-note-p131-n4-citation"].update({
        "subject_candidate_id": "cand-2962",
        "object_candidate_id": "cand-6076",
        "predicate": "cites",
        "qualifiers": {
            **updates["st-chp5-note-p131-n4-citation"]["qualifiers"],
            "claim": "Haskell cites Gigli passim for the diary mentioned on p.131.",
            "qualification": "The book bibliography identifies the published Diario Romano edition; no particular diary passage is identified and the edition was not independently consulted.",
            "mentioned_candidate_ids": ["cand-2962", "cand-6076"],
        },
    })

    existing_ids = set(by_id)
    new_ids = {r["statement_id"] for r in NEW_STATEMENTS}
    need(len(new_ids) == len(NEW_STATEMENTS) and not (new_ids & existing_ids), "new statement id collision")
    for sid, upd in updates.items():
        need(upd.get("subject_candidate_id") and upd.get("object_candidate_id"), f"missing endpoint: {sid}")
        need(upd["subject_candidate_id"] in candidate_ids and upd["object_candidate_id"] in candidate_ids,
             f"unknown endpoint: {sid}")
    for row in NEW_STATEMENTS:
        need(row["subject_candidate_id"] in candidate_ids and row["object_candidate_id"] in candidate_ids,
             f"unknown endpoint: {row['statement_id']}")

    return {
        "statements": statements,
        "raw_statement_lines": raw_statement_lines,
        "updates": updates,
        "new_statements": NEW_STATEMENTS,
        "candidates": candidates,
        "candidate_fields": candidate_fields,
        "mentions": mentions,
        "mention_fields": mention_fields,
        "mention_updates": mention_updates,
        "new_mentions": new_mentions,
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


def render_csv(rows: list[dict], fields: list[str], updates: dict, new_rows: list[dict], bom: bool) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="raise", lineterminator="\n")
    writer.writeheader()
    prepared = []
    for row in rows:
        row = dict(row)
        row.update(updates.get(row.get("mention_id"), {}))
        prepared.append(row)
    writer.writerows(prepared + new_rows)
    content = buffer.getvalue().encode("utf-8")
    return codecs.BOM_UTF8 + content if bom else content


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
    parser = argparse.ArgumentParser(description="Controlled S2 p.131 footnote writeback; dry-run by default.")
    parser.add_argument("--apply", action="store_true", help="write the reviewed exact change set")
    args = parser.parse_args()
    plan = build_plan()
    statement_path = TABLES / "book-statements.jsonl"
    mention_path = TABLES / "mentions.csv"
    outputs = {
        statement_path: render_jsonl(plan),
        mention_path: render_csv(plan["mentions"], plan["mention_fields"], plan["mention_updates"], plan["new_mentions"],
                                 mention_path.read_bytes().startswith(codecs.BOM_UTF8)),
    }
    print("S2 p.131 footnotes dry-run / exact plan")
    print(f"segment sha256: {hashlib.sha256(segment_text.encode('utf-8')).hexdigest()}")
    print(f"existing statements classified: 4; added atomic statements: {len(NEW_STATEMENTS)}; new citations: 3")
    print(f"new archive mentions: {len(plan['new_mentions'])}; candidate additions: 0")
    for path, content in outputs.items():
        print(f"{path.relative_to(ROOT)}: {sha256(path)} -> {hashlib.sha256(content).hexdigest()} ({len(content)} bytes)")
    if not args.apply:
        print("dry-run only; no tables written")
        return

    backups = {}
    suffix = ".bak-s2-chp5-p131-notes-20261012"
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
