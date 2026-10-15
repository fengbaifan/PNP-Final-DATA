#!/usr/bin/env python3
"""Classify the p.113 S2 statements against the printed page."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_ii.md"
SOURCE_REL = "02-sources/02-Markdown/04_CHP-4_sec_ii.md"
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l161-170"
SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
SEGMENT_SHA256 = "531080d40c510db5e2739ecb41a954ff6c033c03daf433ae010679686e8c4714"
EXPECTED_SHA256 = {
    "book-statements.jsonl": "be1d18449bb720e475ad02d488178acd2a0f346590da0d9909585ceee82fc901",
    "entity-candidates.csv": "01eaae9a76cc32c5a12e78820594517a3382bbea6ac9447c121cd57bd141b1a2",
    "mentions.csv": "1300136c3dd1173dcb91c1ca44ae5556709ba1f08f7cea41c0987fbb4dddacea",
}
STATEMENT_BACKUP_SUFFIX = "bak-s2-chp4-sec-ii-l161-170-relations-20261011"
ORIGINAL_IDS = {
    "st-chp4-sec-ii-p113-archbishop-letter-velasquez",
    "st-chp4-sec-ii-p113-carlo-antonio-survival",
    "st-chp4-sec-ii-p113-cassiano-death",
    "st-chp4-sec-ii-p113-cassiano-health",
    "st-chp4-sec-ii-p113-cassiano-retirement-influence",
    "st-chp4-sec-ii-p113-collection-growth-slowed",
    "st-chp4-sec-ii-p113-drawings-enrich-museum",
    "st-chp4-sec-ii-p113-few-pictures-after-urban",
    "st-chp4-sec-ii-p113-first-private-patron-influence",
    "st-chp4-sec-ii-p113-friendship-may-have_cooled",
    "st-chp4-sec-ii-p113-leonardo-research",
    "st-chp4-sec-ii-p113-men-continued-seeing",
    "st-chp4-sec-ii-p113-only-picture-for-cassiano",
    "st-chp4-sec-ii-p113-patronage-political-status",
    "st-chp4-sec-ii-p113-portrait-result-uncertain",
    "st-chp4-sec-ii-p113-poussin-french-clients",
    "st-chp4-sec-ii-p113-scholar-encouragement",
    "st-chp4-sec-ii-p113-scholarly-scientific-activity",
    "st-chp4-sec-ii-p113-storm-passage",
    "st-chp4-sec-ii-p113-taste-currents-fragment",
    "st-chp4-sec-ii-p113-tempest-dughet-influence",
    "st-chp4-sec-ii-p113-tempest-foreground-story",
    "st-chp4-sec-ii-p113-tempest-identification",
    "st-chp4-sec-ii-p113-tempest-unique-cooperation",
}
NEW_IDS = {
    "st-chp4-sec-ii-p113-carlo-antonio-brother-of-cassiano",
    "st-chp4-sec-ii-p113-tempest-unique-in-production",
}
UPDATES = {
    "st-chp4-sec-ii-p113-archbishop-letter-velasquez": {
        "relation": True,
        "note": "The passage explicitly says the Archbishop wrote to Cassiano; the pronoun is resolved from the preceding sentence.",
    },
    "st-chp4-sec-ii-p113-carlo-antonio-survival": {
        "relation": True,
        "note": "The passage explicitly states that Carlo Antonio outlived Cassiano; the duration remains approximate.",
    },
    "st-chp4-sec-ii-p113-cassiano-death": {
        "relation": True,
        "note": "The death event and reported year are explicit in Haskell's account.",
    },
    "st-chp4-sec-ii-p113-cassiano-health": {"relation": False},
    "st-chp4-sec-ii-p113-cassiano-retirement-influence": {"relation": False},
    "st-chp4-sec-ii-p113-collection-growth-slowed": {"relation": False},
    "st-chp4-sec-ii-p113-drawings-enrich-museum": {
        "relation": True,
        "note": "Haskell explicitly says the drawings continued to enrich Cassiano's museum; the makers remain unnamed.",
    },
    "st-chp4-sec-ii-p113-few-pictures-after-urban": {"relation": False},
    "st-chp4-sec-ii-p113-first-private-patron-influence": {
        "relation": True,
        "open_reason": "The target 'arts of his day' is broad and not represented by a bounded entity in this passage.",
        "note": "Retain Haskell's probable historical influence claim as a relation candidate with an open target.",
    },
    "st-chp4-sec-ii-p113-friendship-may-have_cooled": {
        "relation": True,
        "note": "This is a qualified claim about the Poussin–Cassiano friendship; both uncertainty markers remain in the statement.",
    },
    "st-chp4-sec-ii-p113-leonardo-research": {
        "relation": True,
        "subject": "cand-1984",
        "object": "cand-2036",
        "predicate": "undertook_research_into_leonardo_at_cassiano_request",
        "note": "Cassiano is the requesting party and Poussin the researcher; Leonardo is the topic, not the relation endpoint.",
    },
    "st-chp4-sec-ii-p113-men-continued-seeing": {
        "relation": True,
        "note": "The immediate context identifies the two men as Poussin and Cassiano.",
    },
    "st-chp4-sec-ii-p113-only-picture-for-cassiano": {
        "relation": True,
        "note": "Retain the reported Poussin–Cassiano picture relation and the source's 'apparently' qualification.",
    },
    "st-chp4-sec-ii-p113-patronage-political-status": {"relation": False},
    "st-chp4-sec-ii-p113-portrait-result-uncertain": {
        "relation": True,
        "open_reason": "The antecedents of 'the two men' and the portrait's maker and sitter are unresolved in this passage.",
        "note": "Keep the portrait relation as a qualified candidate without assigning a person endpoint by guess.",
    },
    "st-chp4-sec-ii-p113-poussin-french-clients": {
        "relation": True,
        "open_reason": "The French friends and clients are unnamed and are not a bounded candidate group.",
        "note": "The passage describes Poussin's work for an unnamed group; 'almost exclusively' is retained.",
    },
    "st-chp4-sec-ii-p113-scholar-encouragement": {
        "relation": True,
        "open_reason": "The scholars encouraged by Cassiano are not identified or bounded in this passage.",
        "note": "Retain the explicit encouragement relation and Haskell's comparative assessment, with the group endpoint open.",
    },
    "st-chp4-sec-ii-p113-scholarly-scientific-activity": {"relation": False},
    "st-chp4-sec-ii-p113-storm-passage": {
        "relation": True,
        "subject": "cand-5923",
        "object": "cand-5778",
        "predicate": "based_on_passage_in",
        "note": "The artwork is described as based on the Trattato passage; this remains Haskell's report, not independent consultation of Poussin's letter.",
    },
    "st-chp4-sec-ii-p113-taste-currents-fragment": {
        "relation": True,
        "open_reason": "The abstract 'currents of taste' are not represented by a bounded entity; the sentence continues on p.114.",
        "note": "Preserve Haskell's influence claim as an open-target relation candidate and link its continuation to p.114.",
    },
    "st-chp4-sec-ii-p113-tempest-dughet-influence": {
        "relation": True,
        "note": "The possible influence of Dughet's landscapes on the Tempest is explicitly qualified as 'perhaps'.",
    },
    "st-chp4-sec-ii-p113-tempest-foreground-story": {
        "relation": False,
        "subject": "cand-5923",
        "object": None,
        "predicate": "foreground_story_introduces_human_grief_into_desolation",
    },
    "st-chp4-sec-ii-p113-tempest-identification": {
        "relation": False,
        "subject": "cand-5923",
        "object": None,
        "predicate": "identified_as_tempest_with_pyramus_and_thisbe",
    },
    "st-chp4-sec-ii-p113-tempest-unique-cooperation": {
        "relation": True,
        "subject": "cand-1984",
        "object": "cand-2036",
        "predicate": "cooperation_climax_marked_by_picture",
        "quote": "marks a worthy climax to his long co-operation with Cassiano.",
        "claim": "Haskell says the Tempest marks a worthy climax to Poussin's long cooperation with Cassiano.",
        "note": "The cooperation claim is separated from the scalar statement that the picture is unique in Poussin's production.",
    },
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def segment_counts(rows: list[dict]) -> dict[str, int]:
    segment = [row for row in rows if row.get("segment_id") == SEGMENT_ID]
    dual = [row for row in segment if row.get("subject_candidate_id") and row.get("object_candidate_id")]
    relation = [row for row in segment if row.get("qualifiers", {}).get("relation_candidate") is True]
    return {
        "statements": len(segment),
        "dual": len(dual),
        "relation_true": len(relation),
        "relation_false": sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in segment),
        "dual_true": sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in dual),
        "dual_false": sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in dual),
        "open_relation": sum(
            row.get("qualifiers", {}).get("relation_candidate") is True
            and (not row.get("subject_candidate_id") or not row.get("object_candidate_id"))
            for row in segment
        ),
        "unclassified": sum("relation_candidate" not in row.get("qualifiers", {}) for row in segment),
    }


def make_new_rows(segment_text: str) -> list[dict]:
    sibling_quote = "his brother Carlo Antonio"
    unique_quote = "the picture is unique in\nPoussin’s production"
    for quote in (sibling_quote, unique_quote):
        if quote not in segment_text:
            raise SystemExit(f"preflight failed: new quote not found in source segment: {quote!r}")
    return [
        {
            "statement_id": "st-chp4-sec-ii-p113-carlo-antonio-brother-of-cassiano",
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": "cand-2035",
            "object_candidate_id": "cand-2036",
            "predicate": "sibling_of",
            "qualifiers": {
                "source_line_start": 162,
                "source_line_end": 162,
                "pdf_physical_page": 24,
                "printed_page_locator": "p.113",
                "claim": "Haskell explicitly identifies Carlo Antonio as Cassiano’s brother.",
                "speaker": "Haskell",
                "text_layer": "authorial narrative",
                "mentioned_candidate_ids": ["cand-2035", "cand-2036"],
                "qualification": "The possessive 'his' refers to Cassiano in the preceding clause.",
                "relation_candidate": True,
                "relation_candidate_note": "The phrase 'his brother Carlo Antonio' explicitly states the sibling relation.",
            },
            "original_quote": sibling_quote,
            "origin": "book",
            "source_file": SOURCE_REL,
        },
        {
            "statement_id": "st-chp4-sec-ii-p113-tempest-unique-in-production",
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": "cand-5923",
            "object_candidate_id": None,
            "predicate": "unique_in_poussin_production",
            "qualifiers": {
                "source_line_start": 165,
                "source_line_end": 166,
                "pdf_physical_page": 24,
                "printed_page_locator": "p.113",
                "claim": "Haskell calls the Tempest unique in Poussin’s production.",
                "speaker": "Haskell",
                "text_layer": "authorial narrative",
                "mentioned_candidate_ids": ["cand-5923", "cand-1984"],
                "qualification": "This is Haskell’s evaluative description of the picture, not an entity relation.",
                "relation_candidate": False,
            },
            "original_quote": unique_quote,
            "origin": "book",
            "source_file": SOURCE_REL,
        },
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the validated p.113 statement changes")
    args = parser.parse_args()

    statement_path = TABLES / "book-statements.jsonl"
    candidate_path = TABLES / "entity-candidates.csv"
    mention_path = TABLES / "mentions.csv"
    expected_paths = {
        "book-statements.jsonl": statement_path,
        "entity-candidates.csv": candidate_path,
        "mentions.csv": mention_path,
    }
    for name, path in expected_paths.items():
        if sha(path.read_bytes()) != EXPECTED_SHA256[name]:
            raise SystemExit(f"preflight failed: unexpected {name} SHA-256")

    source_bytes = SOURCE.read_bytes()
    if sha(source_bytes) != SOURCE_SHA256:
        raise SystemExit("preflight failed: source file changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[160:170])
    if sha(segment_text.encode("utf-8")) != SEGMENT_SHA256:
        raise SystemExit("preflight failed: p.113 segment changed")

    with (TABLES / "segments.jsonl").open(encoding="utf-8") as handle:
        segment_rows = [json.loads(line) for line in handle if line.strip()]
    manifest = [row for row in segment_rows if row.get("segment_id") == SEGMENT_ID]
    if len(manifest) != 1 or manifest[0].get("sha256") != SEGMENT_SHA256:
        raise SystemExit("preflight failed: segment manifest changed")

    rows = read_jsonl(statement_path)
    mentions = list(csv.DictReader(mention_path.open(encoding="utf-8-sig", newline="")))
    with candidate_path.open(encoding="utf-8-sig", newline="") as handle:
        candidate_ids = {row["candidate_id"] for row in csv.DictReader(handle)}
    p113_rows = [row for row in rows if row.get("segment_id") == SEGMENT_ID]
    if {row["statement_id"] for row in p113_rows} != ORIGINAL_IDS or len(p113_rows) != 24:
        raise SystemExit("preflight failed: p.113 statement set changed")
    if len(rows) != 13030 or len(mentions) != 27565:
        raise SystemExit("preflight failed: unexpected table totals")
    if any(row.get("original_quote") not in segment_text for row in p113_rows):
        raise SystemExit("preflight failed: a current p.113 quote is not exact in the source segment")
    p113_mentions = [row for row in mentions if row["segment_id"] == SEGMENT_ID]
    if len(p113_mentions) != 27 or any(
        segment_text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]
        for row in p113_mentions
    ):
        raise SystemExit("preflight failed: p.113 mention set or spans changed")

    by_id = {row["statement_id"]: row for row in rows}
    for statement_id, change in UPDATES.items():
        row = by_id[statement_id]
        row["qualifiers"]["relation_candidate"] = change["relation"]
        for key in ("subject", "object", "predicate", "quote", "claim"):
            if key in change:
                if key == "claim":
                    row["qualifiers"]["claim"] = change[key]
                    continue
                field = {
                    "subject": "subject_candidate_id",
                    "object": "object_candidate_id",
                    "predicate": "predicate",
                    "quote": "original_quote",
                }.get(key, key)
                row[field] = change[key]
        if change.get("relation"):
            row["qualifiers"]["relation_candidate_note"] = change["note"]
        if "open_reason" in change:
            row["qualifiers"]["open_endpoint_reason"] = change["open_reason"]
        elif "open_endpoint_reason" in row["qualifiers"]:
            del row["qualifiers"]["open_endpoint_reason"]
        if statement_id == "st-chp4-sec-ii-p113-taste-currents-fragment":
            row["qualifiers"]["continued_in_segment"] = "chp-4:04_CHP-4_sec_ii:l172-178"

    new_rows = make_new_rows(segment_text)
    if {row["statement_id"] for row in new_rows} != NEW_IDS or any(row["statement_id"] in by_id for row in new_rows):
        raise SystemExit("preflight failed: new statement IDs are not unique")
    for row in [*by_id.values(), *new_rows]:
        for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if endpoint and endpoint not in candidate_ids:
                raise SystemExit(f"preflight failed: unresolved candidate endpoint {endpoint}")

    original_positions = [i for i, row in enumerate(rows) if row.get("segment_id") == SEGMENT_ID]
    rows[max(original_positions) + 1:max(original_positions) + 1] = new_rows
    expected_counts = {
        "statements": 26,
        "dual": 14,
        "relation_true": 17,
        "relation_false": 9,
        "dual_true": 12,
        "dual_false": 2,
        "open_relation": 5,
        "unclassified": 0,
    }
    counts = segment_counts(rows)
    if counts != expected_counts:
        raise SystemExit(f"preflight failed: unexpected p.113 counts {counts}")
    if len(rows) != 13032 or len({row["statement_id"] for row in rows}) != len(rows):
        raise SystemExit("preflight failed: statement total or identifier uniqueness check failed")

    plan = {
        "mode": "apply" if args.apply else "dry-run",
        "segment_id": SEGMENT_ID,
        "source_sha256": SOURCE_SHA256,
        "segment_sha256": SEGMENT_SHA256,
        "original_statements": len(ORIGINAL_IDS),
        "new_statements": len(new_rows),
        "resulting_segment_counts": counts,
        "table_totals": {"statements": len(rows), "mentions": len(mentions), "candidates": len(candidate_ids)},
        "classification_plan": [
            {
                "statement_id": row["statement_id"],
                "predicate": row["predicate"],
                "subject": row.get("subject_candidate_id"),
                "object": row.get("object_candidate_id"),
                "relation_candidate": row.get("qualifiers", {}).get("relation_candidate"),
                "open_endpoint_reason": row.get("qualifiers", {}).get("open_endpoint_reason"),
            }
            for row in rows if row.get("segment_id") == SEGMENT_ID
        ],
    }
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backup = statement_path.with_name(f"{statement_path.name}.{STATEMENT_BACKUP_SUFFIX}")
    temp = statement_path.with_name(statement_path.name + ".p113.tmp")
    if backup.exists() or temp.exists():
        raise SystemExit("apply refused: p.113 recovery or temporary file already exists")
    backup.write_bytes(statement_path.read_bytes())
    temp.write_bytes(("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)).encode("utf-8"))
    try:
        os.replace(temp, statement_path)
        written = read_jsonl(statement_path)
        written_segment = [row for row in written if row.get("segment_id") == SEGMENT_ID]
        if len(written) != 13032 or segment_counts(written) != expected_counts or any(
            row.get("qualifiers", {}).get("relation_candidate") is None for row in written_segment
        ):
            raise RuntimeError("post-write p.113 validation failed")
    except Exception:
        shutil.copy2(backup, statement_path)
        temp.unlink(missing_ok=True)
        raise
    print(json.dumps({
        "write": "success",
        "statement_sha256": sha(statement_path.read_bytes()),
        "recovery_copy": backup.name,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
