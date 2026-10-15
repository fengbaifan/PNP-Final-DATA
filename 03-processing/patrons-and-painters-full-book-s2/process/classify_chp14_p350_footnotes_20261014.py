"""Classify the two remaining p.350 footnote records and anchor the citation locator."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
MENTIONS = TABLES / "mentions.csv"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "14_CHP-14_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-14.pdf"
NOTES_SEGMENT = "chp-14:14_CHP-14_intro:l168-220"
SEGMENT_SHA256 = "72edc0571341795562aee96338a6bf5de6261bf0ee2f9948cd29ce23318edaa4"
STATEMENTS_SHA256 = "bdc9b771675e3d991ed790da748a7322ba7502d12d26ca54df0b3efda8276be2"
MENTIONS_SHA256 = "5a1dbc154604455332c5df508164f91ecc8d864ccd57eadb06cb8379fa4e3ff5"
SOURCE_SHA256 = "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7"
PDF_SHA256 = "f871a00a63cfa5a9f229930cfd4b0d979baa0491ca4e7fe4d50404fa020a52e0"
BACKUP_SUFFIX = ".bak-s2-ch14-p350-footnotes-20261014"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    for path, expected in ((STATEMENTS, STATEMENTS_SHA256), (MENTIONS, MENTIONS_SHA256),
                           (SOURCE, SOURCE_SHA256), (PDF, PDF_SHA256)):
        if sha(path) != expected:
            raise SystemExit(f"precondition failed: {path.relative_to(ROOT)}")
    segments = [json.loads(x) for x in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if x.strip()]
    segment = next(x for x in segments if x["segment_id"] == NOTES_SEGMENT)
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if segment.get("sha256") != SEGMENT_SHA256 or hashlib.sha256(text.encode("utf-8")).hexdigest() != SEGMENT_SHA256:
        raise SystemExit("note segment hash mismatch")

    original = STATEMENTS.read_text(encoding="utf-8-sig").splitlines()
    rows = [json.loads(x) for x in original if x.strip()]
    by_id = {r["statement_id"]: r for r in rows}
    expected = {"st-chp14-p350-note2-opere", "st-chp14-p350-note3-chapter12"}
    for sid in expected:
        if sid not in by_id or (by_id[sid].get("qualifiers") or {}).get("relation_candidate") is not None:
            raise SystemExit(f"expected unset note statement changed: {sid}")

    field_bytes = MENTIONS.read_bytes()
    has_bom = field_bytes.startswith(b"\xef\xbb\xbf")
    with MENTIONS.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f); fields = list(reader.fieldnames or []); mentions = list(reader)
    if any(x["segment_id"] == NOTES_SEGMENT and x["surface_form"] == "Opere, Vin" for x in mentions):
        raise SystemExit("Opere locator mention already exists")
    if "Opere, Vin" not in text:
        raise SystemExit("exact OCR citation locator not found in note segment")
    start = text.index("Opere, Vin")
    candidate_ids = {r["candidate_id"] for r in csv.DictReader((TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline=""))}
    if "cand-10266" not in candidate_ids:
        raise SystemExit("citation-locator candidate cand-10266 missing")

    q = by_id["st-chp14-p350-note2-opere"].setdefault("qualifiers", {})
    q.update({
        "claim": "Note 2 gives a citation locator to Opere, volume VIII, pages 351–388.",
        "qualification": "The note supplies a volume and page range but no source-document endpoint for a formal citation edge; retain the locator candidate and do not infer an additional relationship.",
        "mentioned_candidate_ids": ["cand-10266"],
        "relation_candidate": False,
        "relation_candidate_note": "Bibliographic locator only; no separate entity-relation claim is asserted in this note record.",
        "ocr_corrections": [{"source_line": 179, "ocr": "Vin", "print": "VIII", "basis": "CHP-14.pdf physical page 4."}],
    })
    q = by_id["st-chp14-p350-note3-chapter12"].setdefault("qualifiers", {})
    q.update({
        "claim": "Note 3 directs the reader to Chapter 12.",
        "qualification": "This is an internal navigation cue rather than a formal relation; no content from Chapter 12 is imported into this statement.",
        "mentioned_candidate_ids": [],
        "relation_candidate": False,
        "relation_candidate_note": "Internal chapter navigation does not by itself assert an entity relationship.",
    })
    mention = {
        "mention_id": "m-s2-ch14-p350-note-20261014-001", "segment_id": NOTES_SEGMENT,
        "candidate_id": "cand-10266", "surface_form": "Opere, Vin",
        "start_char": str(start), "end_char": str(start + len("Opere, Vin")),
        "note": "Exact OCR locator; physical print reads Opere, VIII. Edition was not independently consulted.",
    }
    mentions.append(mention)

    statement_by_id = {r["statement_id"]: r for r in rows}
    payload = ("\n".join(json.dumps(statement_by_id[json.loads(line)["statement_id"]], ensure_ascii=False, separators=(",", ":"))
                           if json.loads(line)["statement_id"] in expected else line for line in original) + "\n").encode("utf-8")
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n", extrasaction="raise")
    writer.writeheader(); writer.writerows(mentions)
    mention_payload = stream.getvalue().encode("utf-8")
    if has_bom: mention_payload = b"\xef\xbb\xbf" + mention_payload
    print(f"p350_unset_notes=2; note2_locator_span=[{start},{start+len('Opere, Vin')}); note3_internal_navigation=false")
    print(f"statement_sha256={hashlib.sha256(payload).hexdigest()}; mentions_sha256={hashlib.sha256(mention_payload).hexdigest()}")
    if not args.apply:
        print("dry_run=true; no files written")
        return 0
    files = ((STATEMENTS, payload), (MENTIONS, mention_payload))
    backups = [(p, p.with_name(p.name + BACKUP_SUFFIX)) for p, _ in files]
    if any(b.exists() for _, b in backups):
        raise SystemExit("p.350 footnote backup already exists; inspect before applying")
    for src, backup in backups: shutil.copy2(src, backup)
    try:
        for path, data in files: path.write_bytes(data)
        for path, data in files:
            if sha(path) != hashlib.sha256(data).hexdigest(): raise OSError(f"write hash mismatch: {path.name}")
    except Exception:
        for src, backup in backups: shutil.copy2(backup, src)
        raise
    print("applied=true")
    for src, backup in backups: print(f"backup={backup.name}; written_sha256={sha(src)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
