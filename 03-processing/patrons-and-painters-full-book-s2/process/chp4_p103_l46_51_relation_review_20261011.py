#!/usr/bin/env python3
"""Classify and repair the p.103 S2 relation-review segment.

Default mode is a hash-guarded dry run. Pass --apply to create recoverable
backups and write the candidate, mention, and statement tables. No S6 edges or
source-file changes are made.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_ii.md"
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l46-51"
SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
SEGMENT_SHA256 = "5d759fc28c9dd1319dcd6f90f3fdf51004910ce09f4de69b80242712d4c95f4c"
EXPECTED_SHA256 = {
    "book-statements.jsonl": "501148ac0878c2ddddf8d54818f7ceac9dc6ca85042438b5ffada800af12539d",
    "entity-candidates.csv": "bfb6c0fcb4177484e57a34969e3b22c27ffec49c392dc3b8aac473fc28db6e93",
    "mentions.csv": "70fc9b0a0cbbe07c782115b5600fd35c7fd77c4845da377a9f9f98eb13da2dbb",
}
BACKUP_SUFFIX = "bak-s2-chp4-sec-ii-l46-51-relations-20261011"

UNCLASSIFIED_DUAL_IDS = {
    "st-chp4-sec-ii-l46-51-1620s-generation-taken-up-by-cassiano",
    "st-chp4-sec-ii-l46-51-artists-enrolled-in-papal-service",
    "st-chp4-sec-ii-l46-51-bust-depicts-uncle",
    "st-chp4-sec-ii-l46-51-cassiano-distaste-pietro-friendship",
    "st-chp4-sec-ii-l46-51-cassiano-employs-artists-on-occasion",
    "st-chp4-sec-ii-l46-51-cassiano-travel-before-pietro-works",
    "st-chp4-sec-ii-l46-51-galileo-orlando-furioso-imagery",
    "st-chp4-sec-ii-l46-51-style-balance-distorted-under-urban",
    "st-chp4-sec-ii-l46-51-uncle-kinship",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def read_csv(path: Path) -> tuple[list[str], list[dict]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(rows)


def relation_decision(row: dict, status: bool, note: str) -> None:
    qualifiers = row.setdefault("qualifiers", {})
    qualifiers["relation_candidate"] = status
    qualifiers["relation_candidate_note"] = note


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the reviewed changes after hash checks")
    args = parser.parse_args()

    statements_path = TABLES / "book-statements.jsonl"
    candidates_path = TABLES / "entity-candidates.csv"
    mentions_path = TABLES / "mentions.csv"
    paths = [statements_path, candidates_path, mentions_path]
    for path in paths:
        actual = sha256(path)
        expected = EXPECTED_SHA256[path.name]
        if actual != expected:
            raise SystemExit(f"preflight failed: {path.name} hash {actual} != expected {expected}")
    if sha256(SOURCE) != SOURCE_SHA256:
        raise SystemExit("preflight failed: source file hash changed")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[45:51])
    if not source_lines[45].startswith("[Page 103]") or hashlib.sha256(segment_text.encode()).hexdigest() != SEGMENT_SHA256:
        raise SystemExit("preflight failed: segment text or hash changed")

    statements = load_jsonl(statements_path)
    candidate_fields, candidates = read_csv(candidates_path)
    mention_fields, mentions = read_csv(mentions_path)
    segment_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    if len(segment_rows) != 22:
        raise SystemExit(f"preflight failed: expected 22 segment statements, got {len(segment_rows)}")
    by_statement = {row["statement_id"]: row for row in statements}
    dual_unknown = {
        row["statement_id"]
        for row in segment_rows
        if row.get("subject_candidate_id") and row.get("object_candidate_id")
        and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    if dual_unknown != UNCLASSIFIED_DUAL_IDS:
        raise SystemExit(f"preflight failed: unclassified dual IDs differ: {sorted(dual_unknown ^ UNCLASSIFIED_DUAL_IDS)}")

    by_candidate = {row["candidate_id"]: row for row in candidates}
    by_mention = {row["mention_id"]: row for row in mentions}
    if by_candidate["cand-5728"]["suggested_type"] != "term" or by_candidate["cand-5732"]["suggested_type"] != "term":
        raise SystemExit("preflight failed: expected collective type misclassifications changed")
    if by_mention["m-chp4-sec-ii-l46-51-0030"]["candidate_id"] != "cand-0342":
        raise SystemExit("preflight failed: Pietro work-group mention mapping changed")
    if by_mention["m-chp4-sec-ii-l46-51-0060"]["candidate_id"] != "cand-4490":
        raise SystemExit("preflight failed: Roman-buildings mention mapping changed")
    if any(f"m-chp4-sec-ii-l46-51-{i:04d}" in by_mention for i in range(61, 67)):
        raise SystemExit("preflight failed: planned mention ID already exists")

    next_candidate = max(int(row["candidate_id"].split("-")[1]) for row in candidates) + 1
    if next_candidate != 11640:
        raise SystemExit(f"preflight failed: expected next candidate cand-11640, got cand-{next_candidate:04d}")
    pope_collective, pretravel_works, roman_buildings = (f"cand-{next_candidate+i:04d}" for i in range(3))

    phrases = {
        "pope_collective": "the\nPope and his nephews",
        "artists_took_up": "eagerly took them up",
        "large_scale_artists": "these artists capable of working on a large scale",
        "employment_pronoun": "employ them",
        "all_artists": "all these artists",
        "restorers": "the other restorers of this great art",
    }
    spans = {}
    for key, phrase in phrases.items():
        start = segment_text.index(phrase)
        spans[key] = (start, start + len(phrase))

    new_candidates = [
        {
            "candidate_id": pope_collective,
            "index_entry_id": "",
            "canonical_name": "Pope Urban VIII and his unnamed nephews as an employer collective",
            "index_page_range": "",
            "suggested_type": "",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Collective in Haskell's account of large-scale artists being enrolled in the service of Pope Urban VIII and his nephews. Individual nephews and artist-to-employer pairings are not supplied.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L48",
        },
        {
            "candidate_id": pretravel_works,
            "index_entry_id": "",
            "canonical_name": "Unidentified works by Pietro da Cortona in Cassiano's pre-travel collection",
            "index_page_range": "",
            "suggested_type": "work",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell reports that before travelling to France and Spain, Cassiano owned 'a number of things' by Pietro da Cortona. The works are unspecified and are not equated with the two large pictures named later.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L48",
        },
        {
            "candidate_id": roman_buildings,
            "index_entry_id": "",
            "canonical_name": "Unidentified Roman buildings cited as sources for architectural proportions",
            "index_page_range": "",
            "suggested_type": "",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Unspecified plural buildings named in Cassiano's quotation as the source from which restorers took proportions of regular architectural orders. No individual building is identified.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L51",
        },
    ]
    new_mentions = [
        {
            "mention_id": "m-chp4-sec-ii-l46-51-0061",
            "segment_id": SEGMENT_ID,
            "candidate_id": pope_collective,
            "surface_form": phrases["pope_collective"],
            "start_char": str(spans["pope_collective"][0]),
            "end_char": str(spans["pope_collective"][1]),
            "note": "Collective endpoint for the Pope and unnamed nephews; do not equate the group with all Barberini family members or infer individual employers.",
        },
        {
            "mention_id": "m-chp4-sec-ii-l46-51-0062",
            "segment_id": SEGMENT_ID,
            "candidate_id": "cand-5728",
            "surface_form": "them",
            "start_char": str(spans["artists_took_up"][0] + len("eagerly took ")),
            "end_char": str(spans["artists_took_up"][0] + len("eagerly took them")),
            "note": "Pronoun refers to the named 1620s artists as a collective; no individual patronage is implied.",
        },
        {
            "mention_id": "m-chp4-sec-ii-l46-51-0063",
            "segment_id": SEGMENT_ID,
            "candidate_id": "cand-5728",
            "surface_form": phrases["large_scale_artists"],
            "start_char": str(spans["large_scale_artists"][0]),
            "end_char": str(spans["large_scale_artists"][1]),
            "note": "Anaphoric description of the previously named 1620s artist cohort.",
        },
        {
            "mention_id": "m-chp4-sec-ii-l46-51-0064",
            "segment_id": SEGMENT_ID,
            "candidate_id": "cand-5728",
            "surface_form": "them",
            "start_char": str(spans["employment_pronoun"][0] + len("employ ")),
            "end_char": str(spans["employment_pronoun"][0] + len("employ them")),
            "note": "Pronoun refers to the named 1620s artists as a collective; the statement records only occasional employment.",
        },
        {
            "mention_id": "m-chp4-sec-ii-l46-51-0065",
            "segment_id": SEGMENT_ID,
            "candidate_id": "cand-5728",
            "surface_form": phrases["all_artists"],
            "start_char": str(spans["all_artists"][0]),
            "end_char": str(spans["all_artists"][1]),
            "note": "Collective reference to the artists named earlier in the paragraph.",
        },
        {
            "mention_id": "m-chp4-sec-ii-l46-51-0066",
            "segment_id": SEGMENT_ID,
            "candidate_id": "cand-5732",
            "surface_form": phrases["restorers"],
            "start_char": str(spans["restorers"][0]),
            "end_char": str(spans["restorers"][1]),
            "note": "Unnamed additional restorers following the six individually named figures; keep the collective open.",
        },
    ]

    decisions = {
        "st-chp4-sec-ii-l46-51-1620s-generation-taken-up-by-cassiano": (
            True,
            "Haskell explicitly says Cassiano eagerly took up the named 1620s cohort; preserve this as a collective support claim and do not infer individual commissions.",
        ),
        "st-chp4-sec-ii-l46-51-artists-enrolled-in-papal-service": (
            True,
            "Haskell describes the large-scale artists collectively as enrolled in the service of the Pope and his nephews; the collective employer endpoint preserves the source without pairing individuals.",
        ),
        "st-chp4-sec-ii-l46-51-bust-depicts-uncle": (
            True,
            "The source explicitly identifies Cassiano's unnamed uncle, Archbishop of Pisa, as the sitter; the sitter's personal identity remains unresolved.",
        ),
        "st-chp4-sec-ii-l46-51-cassiano-employs-artists-on-occasion": (
            True,
            "Haskell explicitly says Cassiano employed the artist group on occasion; retain the collective scope and do not infer an individual contract for each member.",
        ),
        "st-chp4-sec-ii-l46-51-cassiano-travel-before-pietro-works": (
            True,
            "The statement asserts ownership of an unspecified group of Pietro works before Cassiano's France and Spain travels; the work-group endpoint avoids treating Pietro himself as the owned object.",
        ),
        "st-chp4-sec-ii-l46-51-galileo-orlando-furioso-imagery": (
            True,
            "Galileo's quotation explicitly presents an interpretive response to Orlando Furioso through an imagined gallery; retain the rhetorical scene as commentary, not as an inventory of actual works.",
        ),
        "st-chp4-sec-ii-l46-51-style-balance-distorted-under-urban": (
            False,
            "Urban VIII's reign supplies the time frame for Haskell's account of stylistic change; the text does not assert a binary relation between the style balance and the Pope.",
        ),
        "st-chp4-sec-ii-l46-51-uncle-kinship": (
            True,
            "Haskell explicitly identifies the Archbishop of Pisa as Cassiano's uncle; preserve the unnamed person's unresolved identity.",
        ),
    }
    if set(decisions) != UNCLASSIFIED_DUAL_IDS - {"st-chp4-sec-ii-l46-51-cassiano-distaste-pietro-friendship"}:
        raise SystemExit("script error: decision set differs from the seven retained dual claims")
    for statement_id, (status, note) in decisions.items():
        relation_decision(by_statement[statement_id], status, note)

    # The Pope and his nephews form one source-defined collective employer endpoint.
    enrolled = by_statement["st-chp4-sec-ii-l46-51-artists-enrolled-in-papal-service"]
    if enrolled.get("object_candidate_id") != "cand-0209":
        raise SystemExit("preflight failed: papal-service object endpoint changed")
    enrolled["object_candidate_id"] = pope_collective
    enrolled["qualifiers"]["mentioned_candidate_ids"] = [
        "cand-5728", pope_collective, "cand-0209", "cand-0198", "cand-0295", "cand-0342", "cand-2318", "cand-1984", "cand-2792"
    ]
    enrolled["qualifiers"]["qualification"] = (
        "Collective observation only; it does not pair each named artist with a specific employer or identify individual nephews. The Pope-and-nephews collective is a source-defined group."
    )

    # Correct the work endpoint for Cassiano's vague pre-travel ownership claim.
    travel_works = by_statement["st-chp4-sec-ii-l46-51-cassiano-travel-before-pietro-works"]
    if travel_works.get("object_candidate_id") != "cand-0342":
        raise SystemExit("preflight failed: pre-travel work claim endpoint changed")
    travel_works["object_candidate_id"] = pretravel_works
    travel_works["predicate"] = "owned_unspecified_works_before_travels"
    travel_works["qualifiers"]["claim"] = "Haskell says Cassiano owned a number of unspecified works by Pietro da Cortona before travelling to France and Spain."
    travel_works["qualifiers"]["mentioned_candidate_ids"] = ["cand-2036", pretravel_works, "cand-0342", "cand-4266", "cand-5120"]
    travel_works["qualifiers"]["qualification"] = (
        "The count is vague and the works remain unidentified; do not equate them with the two named large pictures later in the passage."
    )
    travel_works["original_quote"] = "he owned ‘a number of things’ by Pietro da Cortona."
    travel_works["qualifiers"]["relation_candidate_note"] = decisions[travel_works["statement_id"]][1]

    # Record the source-defined artist cohort at its pronoun and descriptive mentions.
    style_balance = by_statement["st-chp4-sec-ii-l46-51-style-balance-distorted-under-urban"]
    style_balance["qualifiers"]["mentioned_candidate_ids"] = [
        "cand-5729", "cand-0209", "cand-5728", "cand-0295", "cand-0342", "cand-2318", "cand-1984", "cand-2792"
    ]

    # Separate Cassiano's evaluative reaction from the explicit friendship relation.
    distaste = by_statement["st-chp4-sec-ii-l46-51-cassiano-distaste-pietro-friendship"]
    if distaste.get("object_candidate_id") != "cand-0342":
        raise SystemExit("preflight failed: compound distaste/friendship endpoints changed")
    friendship_footnotes = distaste["qualifiers"].pop("footnote_refs", [])
    distaste["object_candidate_id"] = None
    distaste["predicate"] = "found_artistic_effects_distasteful"
    distaste["qualifiers"]["claim"] = "Haskell says Cassiano found the described artistic effects clearly distasteful."
    distaste["qualifiers"]["mentioned_candidate_ids"] = ["cand-2036", "cand-5729", "cand-0209", "cand-0295", "cand-0342", "cand-4968"]
    distaste["qualifiers"]["qualification"] = (
        "'All this' refers to the artistic effects and stylistic changes described immediately before; this is Cassiano's evaluative reaction, not a relation to Pietro as a person. The source's footnote marker 2 follows the separate friendship clause."
    )
    distaste["original_quote"] = "To Cassiano dal Pozzo all this was clearly most distasteful"

    friendship_id = "st-chp4-sec-ii-l46-51-cassiano-remained-friendly-with-pietro"
    if friendship_id in {row["statement_id"] for row in statements}:
        raise SystemExit("preflight failed: friendship statement ID already exists")
    friendship = {
        "statement_id": friendship_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-2036",
        "object_candidate_id": "cand-0342",
        "predicate": "remained_friendly_with",
        "qualifiers": {
            "source_line_start": 50,
            "source_line_end": 50,
            "claim": "Haskell says Cassiano remained on friendly terms with Pietro da Cortona despite disliking the described artistic effects.",
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "pdf_physical_page": 10,
            "printed_page_locator": "p.103",
            "mentioned_candidate_ids": ["cand-2036", "cand-0342"],
            "qualification": "The friendship statement is distinct from Cassiano's negative evaluation of the art; footnote 2 provides a letter locator, not independent verification or a precise time range.",
            "footnote_refs": friendship_footnotes,
            "relation_candidate": True,
            "relation_candidate_note": "The source explicitly says Cassiano remained on friendly terms with Pietro; the preceding distaste is a separate evaluative claim and does not imply a break in friendship.",
        },
        "original_quote": "although he remained on friendly terms with Pietro",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
    }
    statements.insert(statements.index(distaste) + 1, friendship)

    # Split the source's group-level architectural provenance claim from Cassiano's general critique.
    architectural_id = "st-chp4-sec-ii-l46-51-restorers-took-proportions-from-roman-buildings"
    if architectural_id in {row["statement_id"] for row in statements}:
        raise SystemExit("preflight failed: architectural-relation statement ID already exists")
    architectural = {
        "statement_id": architectural_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-5732",
        "object_candidate_id": roman_buildings,
        "predicate": "took_architectural_proportions_from",
        "qualifiers": {
            "source_line_start": 50,
            "source_line_end": 51,
            "claim": "In Cassiano's quotation, the named restorers of classical architecture and unspecified additional restorers took proportions of regular architectural orders from Roman buildings.",
            "speaker": "Cassiano as quoted by Haskell",
            "text_layer": "nested quotation",
            "pdf_physical_page": 10,
            "printed_page_locator": "p.103",
            "mentioned_candidate_ids": ["cand-0459", "cand-5733", "cand-0443", "cand-2419", "cand-1807", "cand-2775", "cand-5732", "cand-5730", roman_buildings],
            "qualification": "Cassiano's assertion is mediated by Haskell. The collective includes six named figures and unspecified other restorers; the buildings and individual orders are not identified. Retain the printed 'Buonarotti' form pending identity alignment.",
            "footnote_refs": by_statement["st-chp4-sec-ii-l46-51-cassiano-architectural-critique"]["qualifiers"].get("footnote_refs", []),
            "relation_candidate": True,
            "relation_candidate_note": "Cassiano's quotation explicitly says the architectural restorers took proportions from Roman buildings; preserve the collective and unspecified source buildings without inventing individual matches.",
        },
        "original_quote": "Brunelleschi, Buonarotti,\nBramante, Serlio, Palladio, Vignola and the other restorers of this great art, who took the true proportions of those perfectly regular orders from Roman buildings.",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
    }
    statements.insert(statements.index(by_statement["st-chp4-sec-ii-l46-51-cassiano-architectural-critique"]) + 1, architectural)

    # The existing one-endpoint claim has a precise stylistic-concept endpoint.
    pietro_illusionism = by_statement["st-chp4-sec-ii-l46-51-pietro-painted-frame-illusionism"]
    if pietro_illusionism.get("object_candidate_id") is not None:
        raise SystemExit("preflight failed: Pietro illusionism statement already has an object")
    pietro_illusionism["object_candidate_id"] = "cand-4968"
    relation_decision(
        pietro_illusionism,
        True,
        "Haskell explicitly connects Pietro's treatment of painted frames and stucco borders to stronger illusionism; the specific work remains unidentified.",
    )

    # Correct collective typing and re-map two false person/place mentions to their actual group objects.
    by_candidate["cand-5728"]["suggested_type"] = ""
    by_candidate["cand-5732"]["suggested_type"] = ""
    by_mention["m-chp4-sec-ii-l46-51-0030"]["candidate_id"] = pretravel_works
    by_mention["m-chp4-sec-ii-l46-51-0030"]["note"] = "The vague phrase denotes unidentified works by Pietro owned by Cassiano before travel; not equated with the two named pictures later."
    by_mention["m-chp4-sec-ii-l46-51-0060"]["candidate_id"] = roman_buildings
    by_mention["m-chp4-sec-ii-l46-51-0060"]["note"] = "Unspecified Roman buildings are the quoted source of architectural proportions; not merely a location mention of Rome."
    candidates.extend(new_candidates)
    mentions.extend(new_mentions)

    preview = {
        "mode": "apply" if args.apply else "dry-run",
        "segment_id": SEGMENT_ID,
        "segment_sha256": SEGMENT_SHA256,
        "initial_dual_unclassified": len(UNCLASSIFIED_DUAL_IDS),
        "retained_dual_decisions": {"true": sum(status for status, _ in decisions.values()), "false": sum(not status for status, _ in decisions.values())},
        "new_candidates": new_candidates,
        "new_mentions": new_mentions,
        "reassigned_mentions": {
            "m-chp4-sec-ii-l46-51-0030": pretravel_works,
            "m-chp4-sec-ii-l46-51-0060": roman_buildings,
        },
        "new_statements": [friendship, architectural],
        "changed_endpoints": {
            "artists-enrolled-in-papal-service": pope_collective,
            "cassiano-travel-before-pietro-works": pretravel_works,
            "pietro-painted-frame-illusionism": "cand-4968",
        },
        "changed_candidates": {
            "cand-5728.suggested_type": "term -> empty (collective artist cohort)",
            "cand-5732.suggested_type": "term -> empty (collective of restorers)",
        },
        "expected_after": {"candidates": len(candidates), "mentions": len(mentions), "statements": len(statements)},
    }
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups = []
    for path in paths:
        backup = path.with_name(f"{path.name}.{BACKUP_SUFFIX}")
        if backup.exists():
            raise SystemExit(f"apply failed: backup already exists: {backup.name}")
        shutil.copy2(path, backup)
        backups.append(backup)
    try:
        write_jsonl(statements_path, statements)
        write_csv(candidates_path, candidate_fields, candidates)
        write_csv(mentions_path, mention_fields, mentions)
    except Exception:
        for path, backup in zip(paths, backups):
            shutil.copy2(backup, path)
        raise
    print("APPLY_OK")
    for path in paths:
        print(f"SHA256 {path.name} {sha256(path)}")
    print("BACKUPS " + ",".join(path.name for path in backups))


if __name__ == "__main__":
    main()
