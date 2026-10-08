#!/usr/bin/env python3
"""Reconcile Chapter 20 candidate-surface prompts against reviewed text.

The locator only finds existing candidate strings. This controlled edit records
two source-bounded objects and four entity mentions; generic terms
and an already represented relation remain unmapped. Default execution is
read-only; pass --apply after reviewing the dry-run output.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_s2_candidate_surfaces as surface_audit  # noqa: E402

TABLES = ROOT / "04-knowledge" / "tables"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md"

EXPECTED_HASHES = {
    "04-knowledge/tables/entity-candidates.csv": "07dfe219540afe7dbf3b17a73b6cafb32fcc2724b41ed0576c6fa39efa5ab0a0",
    "04-knowledge/tables/mentions.csv": "414fc34bbe5819c54bb83d2f55cdd3c2f52eca0b9e69224f8db9c0112b677112",
    "04-knowledge/tables/book-statements.jsonl": "29cefb618b838db67dd8fe97cf07c3e11b5f203eb8d2146672a7632e9374a4ad",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/s2-coverage.csv": "84f8497a7ce0100f4785acd8bf8ed88bb4c69fe5254cd89d172577b0400eb6c1",
    "02-sources/02-Markdown/20_CHP-20Postscript.md": "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90",
    "scripts/audit_s2_candidate_surfaces.py": "130b53da86d940daad454079960415ac5e7043e0b71239370b66226158cd1ee2",
    "scripts/audit_tables.py": "066bbdcd5fc397713af266c0d1fe2bd23f2a66e7affa3ed797f2c104a8d3d5de",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
}

PROMPT_SIGNATURES = {
    ("chp-20:20_CHP-20Postscript:l110-121", 988, 995, "subject"),
    ("chp-20:20_CHP-20Postscript:l137-148", 196, 203, "subject"),
    ("chp-20:20_CHP-20Postscript:l14-24", 733, 740, "subject"),
    ("chp-20:20_CHP-20Postscript:l14-24", 2021, 2036, "artistic tastes"),
    ("chp-20:20_CHP-20Postscript:l14-24", 2557, 2566, "character"),
    ("chp-20:20_CHP-20Postscript:l150-162", 472, 479, "subject"),
    ("chp-20:20_CHP-20Postscript:l150-162", 1455, 1463, "drawings"),
    ("chp-20:20_CHP-20Postscript:l164-172", 2965, 2975, "collection"),
    ("chp-20:20_CHP-20Postscript:l174-185", 1623, 1630, "subject"),
    ("chp-20:20_CHP-20Postscript:l187-199", 1660, 1669, "portraits"),
    ("chp-20:20_CHP-20Postscript:l201-209", 1533, 1543, "collection"),
    ("chp-20:20_CHP-20Postscript:l201-209", 1801, 1808, "fortune"),
    ("chp-20:20_CHP-20Postscript:l201-209", 1836, 1846, "collection"),
    ("chp-20:20_CHP-20Postscript:l26-36", 2095, 2103, "churches"),
    ("chp-20:20_CHP-20Postscript:l3-12", 931, 940, "character"),
    ("chp-20:20_CHP-20Postscript:l3-12", 945, 951, "poetry"),
    ("chp-20:20_CHP-20Postscript:l3-12", 945, 954, "poetry of"),
    ("chp-20:20_CHP-20Postscript:l38-44", 518, 529, "altarpieces"),
    ("chp-20:20_CHP-20Postscript:l38-44", 620, 629, "character"),
    ("chp-20:20_CHP-20Postscript:l38-44", 698, 709, "altarpieces"),
    ("chp-20:20_CHP-20Postscript:l38-44", 804, 811, "subject"),
    ("chp-20:20_CHP-20Postscript:l81-96", 2401, 2421, "patronage of Bernini"),
    ("chp-20:20_CHP-20Postscript:l98-108", 903, 910, "subject"),
    ("chp-20:20_CHP-20Postscript:l98-108", 1599, 1606, "subject"),
}

NO_WRITE = {
    ("chp-20:20_CHP-20Postscript:l110-121", 988, 995): "Generic description of Isham's exhibition role; not an entity.",
    ("chp-20:20_CHP-20Postscript:l137-148", 196, 203): "Sacred subject is a generic iconographic category.",
    ("chp-20:20_CHP-20Postscript:l14-24", 733, 740): "Generic reference to prior literature on a topic.",
    ("chp-20:20_CHP-20Postscript:l14-24", 2021, 2036): "Del Monte's attribute; the index subentry belongs to Joseph Smith and is not an entity.",
    ("chp-20:20_CHP-20Postscript:l14-24", 2557, 2566): "A general character attribute, not the unrelated Barberini index subentry.",
    ("chp-20:20_CHP-20Postscript:l150-162", 472, 479): "Generic description of a research topic.",
    ("chp-20:20_CHP-20Postscript:l150-162", 1455, 1463): "Drawings names a medium/class in Tessin's collecting activity, not a bounded group; the Carracci index subentry is unrelated.",
    ("chp-20:20_CHP-20Postscript:l174-185", 1623, 1630): "Generic picture subject matter, not an entity.",
    ("chp-20:20_CHP-20Postscript:l201-209", 1801, 1808): "Fortune means wealth here, not Salvator Rosa's painting.",
    ("chp-20:20_CHP-20Postscript:l26-36", 2095, 2103): "Generic plural for Jesuit churches; the many same-label index entries are unrelated places or works.",
    ("chp-20:20_CHP-20Postscript:l3-12", 931, 940): "Maffeo Barberini's general attribute, not a separate work or entity.",
    ("chp-20:20_CHP-20Postscript:l3-12", 945, 951): "Generic body of poetry; no bounded or titled corpus is identified.",
    ("chp-20:20_CHP-20Postscript:l3-12", 945, 954): "An index subject phrase for Maffeo Barberini, not an independently bounded entity.",
    ("chp-20:20_CHP-20Postscript:l38-44", 518, 529): "Generic class of altarpieces, not a named or bounded group.",
    ("chp-20:20_CHP-20Postscript:l38-44", 620, 629): "General attribute of the iconographic programme, not an entity.",
    ("chp-20:20_CHP-20Postscript:l38-44", 698, 709): "Generic class of altarpieces; no individual works are named.",
    ("chp-20:20_CHP-20Postscript:l38-44", 804, 811): "Generic iconographic subject, not an entity.",
    ("chp-20:20_CHP-20Postscript:l81-96", 2401, 2421): "This phrase describes Clement IX's patronage relation to Bernini, already recorded in the statement and relation-candidate flag; index hits name unrelated popes.",
    ("chp-20:20_CHP-20Postscript:l98-108", 903, 910): "Generic description of the chapter's subject.",
    ("chp-20:20_CHP-20Postscript:l98-108", 1599, 1606): "Generic reference to the subject as a whole, not an entity.",
}

WRITE_PROMPTS = {
    ("chp-20:20_CHP-20Postscript:l164-172", 2965, 2975),
    ("chp-20:20_CHP-20Postscript:l187-199", 1660, 1669),
    ("chp-20:20_CHP-20Postscript:l201-209", 1533, 1543),
    ("chp-20:20_CHP-20Postscript:l201-209", 1836, 1846),
}

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-11517",
        "index_entry_id": "",
        "canonical_name": "Group of Francesco Algarotti portraits reported as derived from Georg Friedrich Schmidt's 1752 print",
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Haskell reports that Santifaller found the vast majority of Algarotti portraits to derive "
            "from Schmidt's 1752 print and illustrated some previously unknown examples. The group "
            "is not quantified or itemized. Keep distinct from the source print cand-11135, the "
            "separate Salimbeni print cand-11136, and the unfinished Tiepolo portrait reference cand-2574."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-20:20_CHP-20Postscript:l187-199#L195",
    },
    {
        "candidate_id": "cand-11518",
        "index_entry_id": "",
        "canonical_name": "Girolamo Manfrin's dispersed art collection (scope unresolved)",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Haskell describes the dispersal of Manfrin's collection, says it once included Giorgione's "
            "Tempesta, and reports that tobacco-manufacturing wealth helped build it. No inventory, "
            "complete membership, or acquisition chronology is supplied. The taxonomy has no "
            "collection type; retain type unresolved and distinguish this picture group from Manfrin "
            "the person and from individual works."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-20:20_CHP-20Postscript:l201-209#L208",
    },
]

NEW_MENTIONS = [
    ("m-chp20-p407-047", "chp-20:20_CHP-20Postscript:l164-172", "cand-9622", "his collection", 2961, 2975,
     "Anaphoric reference in Rossi's quoted interpretation to Schulenburg's picture collection candidate."),
    ("m-chp20-p409-053", "chp-20:20_CHP-20Postscript:l187-199", "cand-11517", "vast majority of portraits of him", 1643, 1676,
     "Unquantified portrait group that Haskell reports Santifaller traced to Schmidt's 1752 print."),
    ("m-chp20-p410-028", "chp-20:20_CHP-20Postscript:l201-209", "cand-11518", "Manfrin collection", 1525, 1543,
     "Reuse the source-local art-collection candidate, distinct from Girolamo Manfrin the person."),
    ("m-chp20-p410-029", "chp-20:20_CHP-20Postscript:l201-209", "cand-11518", "his collection", 1832, 1846,
     "Anaphoric reference to the Manfrin collection in the passage on tobacco wealth."),
]

STATEMENT_EDITS = {
    "st-chp20-p409-santifaller-algarotti-portraits-schmidt-print": {
        "subject": "cand-11137", "object": "cand-11135", "add": ["cand-11517"], "remove": [],
    },
    "st-chp20-p410-manfrin-tempesta-collection": {
        "subject": "cand-1512", "object": "cand-10695", "add": ["cand-11518"], "remove": [],
        "new_subject": "cand-11518",
        "new_qualification": (
            "The collection is a type-unresolved source-local candidate. The text supplies neither "
            "an inventory nor its complete membership or acquisition chronology; do not infer a "
            "direct personal ownership transfer."
        ),
    },
    "st-chp20-p410-manfrin-acquisition-sources-uncertain": {
        "subject": "cand-1512", "object": None, "add": ["cand-11518"], "remove": [],
    },
    "st-chp20-p410-fontana-manfrin-tobacco-article": {
        "subject": "cand-1512", "object": "cand-11155", "add": ["cand-11518"], "remove": [],
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_hashes() -> None:
    for relative, expected in EXPECTED_HASHES.items():
        path = ROOT / relative
        require(path.exists(), f"missing preflight input: {relative}")
        actual = sha256(path)
        require(actual == expected, f"stale preflight input {relative}: expected {expected}, got {actual}")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> Path:
    tmp = path.with_name(path.name + ".chp20-tmp")
    with tmp.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)
    return tmp


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line]


def write_jsonl_preserving_lines(path: Path, rows: list[dict[str, object]], changed_ids: set[str]) -> Path:
    by_id = {str(row["statement_id"]): row for row in rows}
    original = path.read_bytes()
    bom = original.startswith(b"\xef\xbb\xbf")
    text = original.decode("utf-8-sig")
    output: list[str] = []
    for raw_line in text.splitlines(keepends=True):
        line = raw_line.rstrip("\r\n")
        ending = raw_line[len(line):]
        if not line:
            output.append(raw_line)
            continue
        row = json.loads(line)
        statement_id = str(row.get("statement_id", ""))
        if statement_id in changed_ids:
            output.append(json.dumps(by_id[statement_id], ensure_ascii=False, separators=(",", ":")) + ending)
        else:
            output.append(raw_line)
    tmp = path.with_name(path.name + ".chp20-tmp")
    with tmp.open("wb") as handle:
        if bom:
            handle.write(b"\xef\xbb\xbf")
        handle.write("".join(output).encode("utf-8"))
    return tmp


def source_text_for(segment_id: str, segment_rows: list[dict[str, object]]) -> str:
    segment = next((row for row in segment_rows if row["segment_id"] == segment_id), None)
    require(segment is not None, f"missing source segment {segment_id}")
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    return "\n".join(lines[int(segment["line_start"]) - 1:int(segment["line_end"])])


def prepare():
    verify_hashes()
    c_fields, candidates = read_csv(CANDIDATES)
    m_fields, mentions = read_csv(MENTIONS)
    statements = read_jsonl(STATEMENTS)
    segment_rows = read_jsonl(SEGMENTS)
    summary, hits = surface_audit.audit("chp-20", 6)
    found = {(str(h["segment_id"]), int(h["start_char"]), int(h["end_char"]), str(h["surface_form"])) for h in hits}
    require(found == PROMPT_SIGNATURES, f"prompt set changed; missing={sorted(PROMPT_SIGNATURES-found)!r}; extra={sorted(found-PROMPT_SIGNATURES)!r}")
    require(summary["reviewed_segments_scanned"] == 20 and len(hits) == 24, "unexpected Chapter 20 scan scope/count")
    prompt_keys = {(s, a, b) for s, a, b, _ in PROMPT_SIGNATURES}
    require(not (set(NO_WRITE) & WRITE_PROMPTS), "a prompt is both write and no-write")
    require(set(NO_WRITE) | WRITE_PROMPTS == prompt_keys, "incomplete prompt disposition plan")

    for seg, start, end, surface in PROMPT_SIGNATURES:
        text = source_text_for(seg, segment_rows)
        require(text[start:end] == surface, f"source span drift at {seg}:{start}-{end}")

    candidate_ids = {row["candidate_id"] for row in candidates}
    require(len(candidates) == 11495 and len(mentions) == 27391 and len(statements) == 12263,
            "unexpected starting table counts")
    require(not ({"cand-11517", "cand-11518"} & candidate_ids), "planned candidate ID already exists")
    require("cand-9622" in candidate_ids and "cand-11135" in candidate_ids, "required existing candidates missing")
    mention_by_id = {row["mention_id"]: row for row in mentions}
    require(len(mention_by_id) == len(mentions), "duplicate mention IDs exist")
    require(not ({row[0] for row in NEW_MENTIONS} & set(mention_by_id)), "planned mention ID already exists")
    statement_by_id = {str(row["statement_id"]): row for row in statements}
    require(len(statement_by_id) == len(statements), "duplicate statement IDs exist")
    for statement_id, edit in STATEMENT_EDITS.items():
        require(statement_id in statement_by_id, f"missing statement {statement_id}")
        row = statement_by_id[statement_id]
        require(row.get("subject_candidate_id") == edit["subject"], f"{statement_id} subject changed")
        require(row.get("object_candidate_id") == edit["object"], f"{statement_id} object changed")
        old_ids = row["qualifiers"].get("mentioned_candidate_ids")
        require(isinstance(old_ids, list) and len(old_ids) == len(set(old_ids)), f"invalid mention list in {statement_id}")
        require(not (set(edit["add"]) & set(old_ids)), f"planned candidates already linked in {statement_id}")
    return c_fields, candidates, m_fields, mentions, statements, summary, hits


def apply_changes(c_fields, candidates, m_fields, mentions, statements):
    candidates.extend(NEW_CANDIDATES)
    for mention_id, segment_id, candidate_id, surface, start, end, note in NEW_MENTIONS:
        mentions.append({
            "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
            "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
        })
    statement_by_id = {str(row["statement_id"]): row for row in statements}
    for statement_id, edit in STATEMENT_EDITS.items():
        row = statement_by_id[statement_id]
        row["qualifiers"]["mentioned_candidate_ids"] = row["qualifiers"]["mentioned_candidate_ids"] + edit["add"]
        if "new_subject" in edit:
            row["subject_candidate_id"] = edit["new_subject"]
        if "new_qualification" in edit:
            row["qualifiers"]["qualification"] = edit["new_qualification"]
    return candidates, mentions, statements


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write after exact source/table preflight")
    args = parser.parse_args()
    c_fields, candidates, m_fields, mentions, statements, summary, hits = prepare()
    no_write = [
        {"segment_id": seg, "start_char": start, "end_char": end, "reason": reason}
        for (seg, start, end), reason in sorted(NO_WRITE.items())
    ]
    print(json.dumps({
        "mode": "apply" if args.apply else "dry-run",
        "verified_prompt_count": len(hits),
        "planned_new_candidates": len(NEW_CANDIDATES),
        "planned_new_mentions": len(NEW_MENTIONS),
        "planned_statement_repairs": len(STATEMENT_EDITS),
        "no_write_count": len(no_write),
        "no_write": no_write,
        "before_counts": {"candidates": len(candidates), "mentions": len(mentions), "statements": len(statements)},
        "scan_summary": summary,
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        return 0

    candidates, mentions, statements = apply_changes(c_fields, candidates, m_fields, mentions, statements)
    require(len(candidates) == 11497 and len(mentions) == 27395 and len(statements) == 12263,
            "unexpected planned output counts")
    backups = Path(tempfile.mkdtemp(prefix="pnp-s2-chp20-surface-"))
    paths = (CANDIDATES, MENTIONS, STATEMENTS)
    try:
        for path in paths:
            shutil.copy2(path, backups / path.name)
        staged = [
            (write_csv(CANDIDATES, c_fields, candidates), CANDIDATES),
            (write_csv(MENTIONS, m_fields, mentions), MENTIONS),
            (write_jsonl_preserving_lines(STATEMENTS, statements, set(STATEMENT_EDITS)), STATEMENTS),
        ]
        for temporary, destination in staged:
            os.replace(temporary, destination)
    except Exception:
        for path in paths:
            backup = backups / path.name
            if backup.exists():
                shutil.copy2(backup, path)
        raise

    after_summary, after_hits = surface_audit.audit("chp-20", 6)
    remaining = {(str(h["segment_id"]), int(h["start_char"]), int(h["end_char"])) for h in after_hits}
    require(remaining == set(NO_WRITE), f"post-write residual prompts differ from no-write plan: {remaining ^ set(NO_WRITE)}")
    print(json.dumps({
        "backup_dir": str(backups),
        "after_counts": {"candidates": len(candidates), "mentions": len(mentions), "statements": len(statements)},
        "after_surface_summary": after_summary,
        "after_surface_residual_count": len(after_hits),
        "after_hashes": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
