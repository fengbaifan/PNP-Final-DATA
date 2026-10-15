#!/usr/bin/env python3
"""Separate Palomino's portrait attribution, Haskell's inference, chronology, and citation.

Default mode performs a guarded dry run. Pass --apply to write after all checks.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge/tables/book-statements.jsonl"
MENTIONS = ROOT / "04-knowledge/tables/mentions.csv"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
SOURCE = ROOT / "02-sources/02-Markdown/02_CHP-2_sec_vii.md"
STATEMENTS_SHA = "334eef0f81f03918311196131053020e6286af822a1a63e136ec294cbc32dbea"
MENTIONS_SHA = "ad57d10340723ec589285d0ad37a1ea0e5963a96360896febbe6e07abf5e31a9"
CANDIDATES_SHA = "b4ac5c42748249c553bf133ab9267acb9fbb85422d1198208b19b7e8b8c250de"
SOURCE_SHA = "5f2ec3c85927ed4aded258d7a6b1801ccb3b8e0416f0f3f9e57ad7b2fae8dd4c"
BACKUP_SUFFIX = ".bak-s2-handoff-chp2-p60-note5-20261010"

ATTRIBUTION_ID = "st-chp2-secvii-l38-54-fn-p60-5a-palomino-attribution"
CHRONOLOGY_ID = "st-chp2-secvii-l38-54-fn-p60-5b-antonio-return-chronology"
INFERENCE_ID = "st-chp2-secvii-l38-54-fn-p60-5c-palomino-confusion-inference"
SITTER_ID = "st-chp2-secvii-l38-54-fn-p60-5a-sitter-identification"
CITATION_ID = "st-chp2-secvii-l38-54-fn-p60-5d-palomino-citation"
BODY_ID = "st-chp2-secvii-l21-30-velasquez-francesco-portrait-uncertain"

WORK = "cand-4956"
PALOMINO = "cand-4954"
PALOMINO_BOOK = "cand-4955"
VELASQUEZ = "cand-2709"
ANTONIO = "cand-0187"
FRANCESCO = "cand-0199"
FRANCE_PLACE = "cand-4266"
POSSIBLE_FRANCESCO_WORK = "cand-4929"
BOOK = "cand-2962"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"preflight failed: {message}")


def read_statements() -> tuple[list[dict], list[bytes], bool]:
    raw = STATEMENTS.read_bytes()
    lines = raw.splitlines(keepends=True)
    rows = [json.loads(line.decode("utf-8-sig")) for line in lines if line.strip()]
    return rows, lines, raw.startswith(b"\xef\xbb\xbf")


def counts(rows: list[dict]) -> dict[str, int]:
    relations = [s for s in rows if s.get("qualifiers", {}).get("relation_candidate") is True]
    return {
        "statements": len(rows),
        "relations": len(relations),
        "complete_relations": sum(bool(s.get("subject_candidate_id") and s.get("object_candidate_id")) for s in relations),
        "open_relations": sum(not (s.get("subject_candidate_id") and s.get("object_candidate_id")) for s in relations),
        "dual_unclassified": sum(
            bool(s.get("subject_candidate_id") and s.get("object_candidate_id"))
            and "relation_candidate" not in s.get("qualifiers", {})
            for s in rows
        ),
        "footnote_claims": sum(s.get("predicate") == "footnote-claim" for s in rows),
        "cites": sum(s.get("predicate") == "cites" and s.get("qualifiers", {}).get("relation_candidate") is True for s in rows),
    }


def preflight():
    for path, expected in (
        (STATEMENTS, STATEMENTS_SHA),
        (MENTIONS, MENTIONS_SHA),
        (CANDIDATES, CANDIDATES_SHA),
        (SOURCE, SOURCE_SHA),
    ):
        require(sha(path) == expected, f"unexpected SHA-256 for {path.relative_to(ROOT)}")

    statements, statement_lines, statement_bom = read_statements()
    import csv
    with CANDIDATES.open(encoding="utf-8-sig", newline="") as f:
        candidates = list(csv.DictReader(f))
    with MENTIONS.open(encoding="utf-8-sig", newline="") as f:
        mentions = list(csv.DictReader(f))
    by_id = {s["statement_id"]: s for s in statements}
    require(len(by_id) == len(statements), "duplicate statement_id")
    for target in (ATTRIBUTION_ID, CHRONOLOGY_ID, INFERENCE_ID, BODY_ID):
        require(target in by_id, f"missing statement {target}")
    require(SITTER_ID not in by_id and CITATION_ID not in by_id, "new statement ID already exists")

    attribution, chronology, inference = by_id[ATTRIBUTION_ID], by_id[CHRONOLOGY_ID], by_id[INFERENCE_ID]
    quote = "5 Palomino (III, p. 336) says that when in Rome Velasquez painted a portrait of Cardinal Antonio Barberini. In fact Antonio did not return from France until 1653, long after the departure of Velasquez, and Palomino must be confusing Antonio with Francesco."
    for s in (attribution, chronology, inference):
        q = s.get("qualifiers", {})
        require(s["predicate"] == "footnote-claim" and s["original_quote"] == quote, f"statement source changed: {s['statement_id']}")
        require(q.get("source_line_start") == 48 and q.get("print_page") == 60 and q.get("footnote_marker") == 5,
                f"statement locator changed: {s['statement_id']}")
    require(attribution["subject_candidate_id"] == PALOMINO and attribution["object_candidate_id"] == WORK,
            "attribution statement endpoints changed")
    require(chronology["subject_candidate_id"] == ANTONIO and chronology["object_candidate_id"] is None,
            "chronology statement endpoints changed")
    require(inference["subject_candidate_id"] == PALOMINO and inference["object_candidate_id"] == FRANCESCO,
            "inference statement endpoints changed")
    require(attribution["qualifiers"].get("cited_publication_candidate_id") == PALOMINO_BOOK,
            "Palomino publication reference changed")
    require(chronology["qualifiers"].get("place_candidate_id") == FRANCE_PLACE and chronology["qualifiers"].get("year") == "1653",
            "chronology qualifiers changed")
    require(inference["qualifiers"].get("disputed_work_candidate_id") == WORK
            and inference["qualifiers"].get("possible_francesco_work_candidate_id") == POSSIBLE_FRANCESCO_WORK,
            "inference work candidates changed")

    candidate_by_id = {c["candidate_id"]: c for c in candidates}
    kinds = {
        WORK: "work", PALOMINO: "person", PALOMINO_BOOK: "archive", VELASQUEZ: "person",
        ANTONIO: "person", FRANCESCO: "person", FRANCE_PLACE: "place",
        POSSIBLE_FRANCESCO_WORK: "work", BOOK: "archive",
    }
    for candidate_id, kind in kinds.items():
        c = candidate_by_id.get(candidate_id)
        require(c is not None and c["suggested_type"] == kind and c["status"] == "open",
                f"candidate {candidate_id} changed")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    require(source_lines[47] == quote, "source note 5 changed")
    segment = "\n".join(source_lines[37:54])
    expected_spans = {
        "Palomino": (802, 810),
        "p. 336": (817, 823),
        "Velasquez": (848, 857),
        "a portrait of Cardinal Antonio Barberini": (866, 906),
        "Antonio": (916, 923),
        "France": (944, 950),
        "Velasquez_after_departure": (991, 1000),
        "Antonio_again": (1033, 1040),
        "Francesco": (1046, 1055),
    }
    exact = {
        "Palomino": "Palomino", "p. 336": "p. 336", "Velasquez": "Velasquez",
        "a portrait of Cardinal Antonio Barberini": "a portrait of Cardinal Antonio Barberini",
        "Antonio": "Antonio", "France": "France", "Velasquez_after_departure": "Velasquez",
        "Antonio_again": "Antonio", "Francesco": "Francesco",
    }
    mention_by_id = {m["mention_id"]: m for m in mentions}
    mention_ids = {
        "Palomino": ("m-chp2-secvii-l38-54-0025", PALOMINO),
        "p. 336": ("m-chp2-secvii-l38-54-0033", PALOMINO_BOOK),
        "Velasquez": ("m-chp2-secvii-l38-54-0028", VELASQUEZ),
        "a portrait of Cardinal Antonio Barberini": ("m-chp2-secvii-l38-54-0026", WORK),
        "Antonio": ("m-chp2-secvii-l38-54-0027", ANTONIO),
        "France": ("m-chp2-secvii-l38-54-0029", FRANCE_PLACE),
        "Velasquez_after_departure": ("m-chp2-secvii-l38-54-0030", VELASQUEZ),
        "Antonio_again": ("m-chp2-secvii-l38-54-0031", ANTONIO),
        "Francesco": ("m-chp2-secvii-l38-54-0032", FRANCESCO),
    }
    for key, (start, end) in expected_spans.items():
        require(segment[start:end] == exact[key], f"source span changed: {key}")
        mention_id, candidate_id = mention_ids[key]
        m = mention_by_id.get(mention_id)
        require(m is not None and m["candidate_id"] == candidate_id and m["start_char"] == str(start)
                and m["end_char"] == str(end) and m["surface_form"] == exact[key], f"mention changed: {mention_id}")

    body = by_id[BODY_ID]
    refs = body.get("qualifiers", {}).get("footnote_refs", [])
    ref = next((r for r in refs if isinstance(r, dict) and r.get("marker") == 5
                and r.get("segment_id") == attribution["segment_id"] and r.get("source_line") == 48), None)
    require(ref is not None and ref.get("statement_ids") == [ATTRIBUTION_ID, CHRONOLOGY_ID, INFERENCE_ID],
            "body marker 5 references changed")

    before = counts(statements)
    expected_before = {
        "statements": 12669, "relations": 3642, "complete_relations": 3628,
        "open_relations": 14, "dual_unclassified": 4434, "footnote_claims": 10, "cites": 109,
    }
    require(before == expected_before, f"current ledger counts differ: {before}")
    return statements, statement_lines, statement_bom, mentions, candidates


def make_changes(statements: list[dict]):
    rows = copy.deepcopy(statements)
    by_id = {s["statement_id"]: s for s in rows}
    attribution, chronology, inference = by_id[ATTRIBUTION_ID], by_id[CHRONOLOGY_ID], by_id[INFERENCE_ID]
    body = by_id[BODY_ID]

    attribution["subject_candidate_id"] = WORK
    attribution["object_candidate_id"] = VELASQUEZ
    attribution["predicate"] = "attributed_to"
    aq = attribution["qualifiers"]
    aq["claim"] = "Palomino, as quoted by Haskell, attributes this disputed portrait to Velasquez and identifies Cardinal Antonio as its sitter."
    aq["speaker"] = "Palomino, as reported by Haskell"
    aq["text_layer"] = "source attribution reported in authorial footnote"
    aq["qualification"] = "The Palomino volume and page were not independently consulted. Haskell's chronology disputes Antonio as the sitter; this preserves Palomino's attributed_to claim without accepting it as fact."
    aq.pop("cited_publication_candidate_id", None)
    aq["reported_via_author_candidate_id"] = PALOMINO
    aq["reported_via_publication_candidate_id"] = PALOMINO_BOOK
    aq["reported_sitter_candidate_id"] = ANTONIO
    aq["relation_candidate"] = True
    aq["relation_candidate_note"] = "This is Palomino's reported artist attribution as transmitted by Haskell, not a verified authorship claim; candidate only and no formal S6 relation."
    aq["related_body_statement_ids"] = [BODY_ID]

    chronology["object_candidate_id"] = None
    chronology["predicate"] = "reported_return_from_france_by_1653"
    cq = chronology["qualifiers"]
    cq["claim"] = "Haskell says Antonio had not returned from France before 1653, after Velasquez had already left Rome."
    cq["speaker"] = "Haskell"
    cq["text_layer"] = "authorial footnote chronology"
    cq["qualification"] = "The chronology is Haskell's reason for doubting that Palomino meant Antonio; no exact departure or return date is supplied. This is a contextual claim, not a formal relation candidate."
    cq["year_qualification"] = "1653 is the earliest return year implied by 'did not return ... until 1653'; exact date is not given."
    cq["relation_candidate"] = False
    cq["related_body_statement_ids"] = [BODY_ID]

    inference["subject_candidate_id"] = WORK
    inference["object_candidate_id"] = FRANCESCO
    inference["predicate"] = "depicts"
    iq = inference["qualifiers"]
    iq["claim"] = "Haskell infers that Palomino confused Cardinal Antonio with Francesco, suggesting that the disputed portrait may depict Francesco."
    iq["speaker"] = "Haskell"
    iq["text_layer"] = "authorial inference"
    iq["qualification"] = "This is Haskell's inference from chronology, not a confirmed sitter identification. Keep the disputed Antonio-portrait candidate separate from the possible Francesco portrait candidate."
    iq["possible_sitter_candidate_id"] = FRANCESCO
    iq["relation_candidate"] = True
    iq["relation_candidate_note"] = "S2 candidate depicting relation derived from Haskell's explicit inference; sitter and work identity remain unresolved, so no formal S6 edge is asserted."
    iq["related_body_statement_ids"] = [BODY_ID]

    sitter = {
        "statement_id": SITTER_ID,
        "segment_id": attribution["segment_id"],
        "subject_candidate_id": WORK,
        "object_candidate_id": ANTONIO,
        "predicate": "depicts",
        "qualifiers": {
            "source_line_start": 48,
            "source_line_end": 48,
            "claim": "Palomino identifies Cardinal Antonio as the sitter of the portrait attributed to Velasquez.",
            "speaker": "Palomino, as reported by Haskell",
            "text_layer": "reported sitter identification",
            "print_page": 60,
            "pdf_physical_page": 49,
            "footnote_marker": 5,
            "qualification": "Haskell's chronology challenges Antonio as the sitter and infers Palomino may have confused him with Francesco. The cited Palomino page was not independently consulted.",
            "reported_via_author_candidate_id": PALOMINO,
            "reported_via_publication_candidate_id": PALOMINO_BOOK,
            "relation_candidate": True,
            "relation_candidate_note": "This preserves the sitter identification in Palomino's reported account as a contested S2 candidate, not a formal S6 relation.",
            "related_body_statement_ids": [BODY_ID],
        },
        "original_quote": attribution["original_quote"],
        "origin": attribution["origin"],
        "source_file": attribution["source_file"],
    }
    citation = {
        "statement_id": CITATION_ID,
        "segment_id": attribution["segment_id"],
        "subject_candidate_id": BOOK,
        "object_candidate_id": PALOMINO_BOOK,
        "predicate": "cites",
        "qualifiers": {
            "source_line_start": 48,
            "source_line_end": 48,
            "claim": "Haskell's footnote cites Palomino, volume III, p. 336, for the report that Velasquez painted a portrait of Cardinal Antonio.",
            "speaker": "Haskell, footnote",
            "text_layer": "bibliographic citation",
            "qualification": "This records Haskell's citation only. Volume III, page 336 was not independently consulted and does not independently verify the attribution or sitter.",
            "footnote_marker": 5,
            "print_page": 60,
            "pdf_physical_page": 49,
            "volume": "III",
            "page": 336,
            "citation_publication_candidate_id": PALOMINO_BOOK,
            "citation_context_candidate_ids": [WORK, VELASQUEZ, ANTONIO, FRANCESCO],
            "linked_body_statement_ids": [BODY_ID],
            "citations": [{
                "source_candidate_id": PALOMINO_BOOK,
                "publication_candidate_id": PALOMINO_BOOK,
                "locator": "vol. III, p. 336",
                "reference_as_printed": "Palomino (III, p. 336)",
            }],
            "cited_material_not_independently_consulted": True,
            "relation_candidate": True,
            "relation_candidate_note": "This records the Haskell book's bibliographic link only; it does not validate the cited claim or create a formal S6 edge.",
        },
        "original_quote": attribution["original_quote"],
        "origin": attribution["origin"],
        "source_file": attribution["source_file"],
    }

    new_rows: list[dict] = []
    for row in rows:
        new_rows.append(row)
        if row["statement_id"] == ATTRIBUTION_ID:
            new_rows.append(sitter)
        if row["statement_id"] == INFERENCE_ID:
            new_rows.append(citation)

    for ref in body["qualifiers"]["footnote_refs"]:
        if isinstance(ref, dict) and ref.get("marker") == 5 and ref.get("source_line") == 48:
            ref["statement_ids"] = [ATTRIBUTION_ID, SITTER_ID, CHRONOLOGY_ID, INFERENCE_ID, CITATION_ID]
    return new_rows


def serialize_statements(rows: list[dict], original_lines: list[bytes], bom: bool) -> bytes:
    newline = b"\r\n" if any(line.endswith(b"\r\n") for line in original_lines) else b"\n"
    output = []
    for index, row in enumerate(rows):
        line = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if index == 0 and bom:
            line = b"\xef\xbb\xbf" + line
        output.append(line + newline)
    return b"".join(output)


def write_atomic(path: Path, content: bytes) -> Path:
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".tmp-", delete=False) as tmp:
        tmp.write(content)
        return Path(tmp.name)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the audited statement changes")
    args = parser.parse_args()
    statements, statement_lines, statement_bom, mentions, candidates = preflight()
    updated = make_changes(statements)
    after = counts(updated)
    expected_after = {
        "statements": 12671, "relations": 3646, "complete_relations": 3632,
        "open_relations": 14, "dual_unclassified": 4432, "footnote_claims": 7, "cites": 110,
    }
    require(after == expected_after, f"projected counts differ: {after}")
    preview = {
        "action": "apply" if args.apply else "dry-run",
        "before": counts(statements),
        "after": after,
        "candidate_rows": len(candidates),
        "mention_rows": len(mentions),
        "statement_updates": [ATTRIBUTION_ID, CHRONOLOGY_ID, INFERENCE_ID, BODY_ID],
        "new_statements": [SITTER_ID, CITATION_ID],
        "relation_candidates": [
            {"id": ATTRIBUTION_ID, "predicate": "attributed_to", "subject": WORK, "object": VELASQUEZ},
            {"id": SITTER_ID, "predicate": "depicts", "subject": WORK, "object": ANTONIO},
            {"id": INFERENCE_ID, "predicate": "depicts", "subject": WORK, "object": FRANCESCO, "status": "Haskell inference"},
            {"id": CITATION_ID, "predicate": "cites", "subject": BOOK, "object": PALOMINO_BOOK, "volume": "III", "page": 336},
        ],
        "chronology": {"id": CHRONOLOGY_ID, "predicate": "reported_return_from_france_by_1653", "subject": ANTONIO, "object": None, "relation_candidate": False},
        "body_marker_5_links": [ATTRIBUTION_ID, SITTER_ID, CHRONOLOGY_ID, INFERENCE_ID, CITATION_ID],
    }
    print(json.dumps(preview, ensure_ascii=True, indent=2))
    if not args.apply:
        return

    backup = STATEMENTS.with_name(STATEMENTS.name + BACKUP_SUFFIX)
    require(not backup.exists(), "recovery backup already exists")
    shutil.copy2(STATEMENTS, backup)
    temp = None
    try:
        temp = write_atomic(STATEMENTS, serialize_statements(updated, statement_lines, statement_bom))
        os.replace(temp, STATEMENTS)
        result, _, _ = read_statements()
        require(counts(result) == expected_after, "post-write statement counts mismatch")
        by_id = {s["statement_id"]: s for s in result}
        require(by_id[ATTRIBUTION_ID]["predicate"] == "attributed_to"
                and by_id[SITTER_ID]["predicate"] == "depicts"
                and by_id[INFERENCE_ID]["predicate"] == "depicts"
                and by_id[CITATION_ID]["predicate"] == "cites", "post-write predicate verification failed")
        refs = by_id[BODY_ID]["qualifiers"]["footnote_refs"]
        ref = next(r for r in refs if isinstance(r, dict) and r.get("marker") == 5 and r.get("source_line") == 48)
        require(ref["statement_ids"] == preview["body_marker_5_links"], "post-write reciprocal footnote links failed")
        print(json.dumps({"result": "applied", "statements_sha256": sha(STATEMENTS),
                          "backup": str(backup.relative_to(ROOT))}, indent=2))
    except Exception:
        shutil.copy2(backup, STATEMENTS)
        raise
    finally:
        if temp is not None and temp.exists():
            temp.unlink()


if __name__ == "__main__":
    main()
