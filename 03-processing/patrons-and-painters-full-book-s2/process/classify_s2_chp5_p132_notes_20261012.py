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
SEGMENT = "chp-5:05_CHP-5_sec_iii:l126-165"
SOURCE_FILE = "02-sources/02-Markdown/05_CHP-5_sec_iii.md"
EXPECTED = {
    "book-statements.jsonl": "c4265cf26489e01616211c4912bb7b008afb43481d8acd8299343f6c6ef5bfcd",
    "entity-candidates.csv": "012efa6759909bc8a1e9b7c16929f331b0b0c065279090c488810b00b25c8df4",
    "mentions.csv": "665ebc1635b2af8282feba756bffe34d609786bea45c3f2f937f90a3b235681a",
}
SOURCE_SHA = "9b095b1a93570102ad2cdb117580f2fbeccd2ff017033a2f66557c58a0d1ef0a"
PDF_SHA = "f63dca79808fde73ba10aa9414fef89bc8ca5e77ed829b2d5c86f23719e0674a"
IMAGE_SHA = "58d8cef4152d2c383e4019caac0e1d9be2b3db2de1cefac8345d598a44f53489"
SEGMENT_SHA = "183b8dbbc0e05624d35d19fdc7f140e588145c5503bbd898b15c65a77e3c58c8"

source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
segment_text = "\n".join(source_lines[125:165])


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def exact(quote: str) -> str:
    need(quote in segment_text, f"source quote not found: {quote!r}")
    return quote


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
    need(hashlib.sha256(segment_text.encode("utf-8")).hexdigest() == SEGMENT_SHA,
         "p.132 notes segment fingerprint changed")

    statement_path = TABLES / "book-statements.jsonl"
    statements, raw_statement_lines = read_jsonl(statement_path)
    by_id = {r["statement_id"]: r for r in statements}
    target_ids = {
        "st-chp5-notes-l127-passeri-vanlaer",
        "st-chp5-notes-l128-briganti-survey",
    }
    need(target_ids <= set(by_id), "p.132 footnote statement inventory changed")
    for sid in target_ids:
        row = by_id[sid]
        need(row.get("segment_id") == SEGMENT, f"unexpected segment for {sid}")
        need((row.get("qualifiers") or {}).get("relation_candidate") is None,
             f"unexpected prior classification for {sid}")
        need(row.get("original_quote", "") in segment_text, f"source quote moved for {sid}")

    # The existing Passeri quote is a source-attributed characterization of Van Laer.
    updates = {}
    passeri = by_id["st-chp5-notes-l127-passeri-vanlaer"]
    q = dict(passeri.get("qualifiers") or {})
    q.update({
        "relation_candidate": True,
        "relation_candidate_note": "S2 attributed characterization from Passeri to Van Laer; the cited edition was not independently consulted and no S6 edge is created.",
        "mentioned_candidate_ids": ["cand-1856", "cand-1351"],
    })
    updates[passeri["statement_id"]] = {"qualifiers": q}

    # The original row remains a bibliographic pointer. Record the author's role separately.
    citation = by_id["st-chp5-notes-l128-briganti-survey"]
    citation_q = dict(citation.get("qualifiers") or {})
    citation_q.update({
        "relation_candidate": False,
        "relation_candidate_note": "Bibliographic pointer to an exhibition catalogue; the author's contribution is recorded in a separate atomic statement.",
        "mentioned_candidate_ids": ["cand-6180", "cand-6181"],
    })
    updates[citation["statement_id"]] = {"qualifiers": citation_q}

    mention_path = TABLES / "mentions.csv"
    mentions, mention_fields = read_csv(mention_path)
    mention_by_id = {r["mention_id"]: r for r in mentions}
    cited_passeri_source = mention_by_id.get("m-chp5-note-127-001")
    need(cited_passeri_source and cited_passeri_source.get("candidate_id") == "cand-4376",
         "existing Passeri archive mention changed")
    existing_vanlaer = mention_by_id.get("m-chp5-note-127-002")
    need(existing_vanlaer and existing_vanlaer.get("candidate_id") == "cand-1351",
         "existing Van Laer mention changed")
    # The existing same-span mention maps "Passeri" to the cited archive. Do not
    # add an overlapping person mention; the person endpoint is named in the
    # linked body segment and remains explicit in this statement's endpoint.
    new_mentions = []

    new_statement = {
        "statement_id": "st-chp5-notes-l128-briganti-authored-introduction",
        "segment_id": SEGMENT,
        "subject_candidate_id": "cand-6180",
        "object_candidate_id": "cand-6181",
        "predicate": "authored_introduction_for",
        "qualifiers": {
            "source_line_start": 128,
            "source_line_end": 128,
            "printed_page_locator": "p.132n2",
            "pdf_physical_page": 13,
            "claim": "Haskell identifies Giulio Briganti as the author of the introduction to the I Bamboccianti exhibition catalogue.",
            "speaker": "Haskell",
            "text_layer": "bibliographic pointer",
            "qualification": "The note attributes the introduction to Briganti; the catalogue was not independently consulted.",
            "printed_reading_correction": {"ocr": "Brigand", "print": "Briganti"},
            "mentioned_candidate_ids": ["cand-6180", "cand-6181"],
            "relation_candidate": True,
            "relation_candidate_note": "Explicit bibliographic author-role relation in the cited footnote; S2 candidate only, no formal S6 edge is created.",
            "footnote_segment": SEGMENT,
            "footnote_marker": 2,
            "linked_body_statement_ids": ["st-chp5-p132-rome-and-campagna-date"],
            "related_segment": "chp-5:05_CHP-5_sec_iii:l5-10",
            "related_source_lines": [9],
            "citation_body_statement_ids": ["st-chp5-p132-rome-and-campagna-date"],
            "footnote_body_link_status": "linked",
        },
        "original_quote": exact("introduction by Giulio Brigand to I Bamboccianti exhibition"),
        "origin": "book",
        "source_file": SOURCE_FILE,
    }
    need(new_statement["statement_id"] not in by_id, "new statement id collision")

    candidate_path = TABLES / "entity-candidates.csv"
    candidates, candidate_fields = read_csv(candidate_path)
    candidate_ids = {r["candidate_id"] for r in candidates}
    need({"cand-1856", "cand-1351", "cand-6180", "cand-6181"} <= candidate_ids,
         "required p.132 footnote candidate missing")
    for row in [new_statement]:
        need(row["subject_candidate_id"] in candidate_ids and row["object_candidate_id"] in candidate_ids,
             "new relation endpoint missing")
    for mention in new_mentions:
        start, end = int(mention["start_char"]), int(mention["end_char"])
        need(segment_text[start:end] == mention["surface_form"], "new Passeri mention span mismatch")

    return {
        "raw_statement_lines": raw_statement_lines,
        "updates": updates,
        "new_statements": [new_statement],
        "candidates": candidates,
        "candidate_fields": candidate_fields,
        "mentions": mentions,
        "mention_fields": mention_fields,
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
    parser = argparse.ArgumentParser(description="Controlled S2 p.132 footnote writeback; dry-run by default.")
    parser.add_argument("--apply", action="store_true", help="write the reviewed exact change set")
    args = parser.parse_args()
    plan = build_plan()
    statement_path = TABLES / "book-statements.jsonl"
    outputs = {
        statement_path: render_jsonl(plan),
    }
    print("S2 p.132 footnotes dry-run / exact plan")
    print(f"source sha256: {sha256(SOURCE)}; page image sha256: {sha256(PAGE_IMAGE)}")
    print("classified existing statements: 2; added atomic relation statements: 1; added mentions: 0")
    for path, data in outputs.items():
        print(f"{path.relative_to(ROOT)}: {sha256(path)} -> {hashlib.sha256(data).hexdigest()} ({len(data)} bytes)")
    if not args.apply:
        print("dry-run only; no tables written")
        return

    backups = {}
    suffix = ".bak-s2-chp5-p132-notes-20261012"
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
