#!/usr/bin/env python3
"""Classify and repair the p.102 S2 relation review segment.

Default mode is a hash-guarded dry run. Pass --apply to create recoverable
backups and write the candidate, mention, and statement tables. This script
does not create S6 relations or change source files.
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
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l33-44"
SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
SEGMENT_SHA256 = "b58e75c02a220218d26467325369277c99d76b05ff11d3ce57af8b100d0038bf"
EXPECTED_SHA256 = {
    "book-statements.jsonl": "20b306df2fc249db980339730313d01012749d61936b20d59332c0597fee3e9e",
    "entity-candidates.csv": "6fe602bb0a8313ea754281efe537a85426943fc65e3b0eab9697a89729ed7b75",
    "mentions.csv": "ab281c6ba89343b4aacf7859d996274642c32c9db30e96302c4abb0a637127af",
}
BACKUP_SUFFIX = "bak-s2-chp4-sec-ii-l33-44-relations-20261011"

UNCLASSIFIED_DUAL_IDS = {
    "st-chp4-sec-ii-l33-44-artists-share-antiquarian-rational-interest",
    "st-chp4-sec-ii-l33-44-caravaggio-attributed-picture",
    "st-chp4-sec-ii-l33-44-cassiano-supporter-of-vouet",
    "st-chp4-sec-ii-l33-44-cigoli-leads-florentine-style-shift",
    "st-chp4-sec-ii-l33-44-codazzi-architectural-scenes",
    "st-chp4-sec-ii-l33-44-employed-vouet-for-original-painting",
    "st-chp4-sec-ii-l33-44-galileo-favorite-painter-cigoli",
    "st-chp4-sec-ii-l33-44-galileo-occasional-collaborator-cigoli",
    "st-chp4-sec-ii-l33-44-owned-vouet-genre-picture",
    "st-chp4-sec-ii-l33-44-preferred-vouet-portrait-busts",
    "st-chp4-sec-ii-l33-44-van-laer-genre-picture",
    "st-chp4-sec-ii-l33-44-volume-subject-organization",
    "st-chp4-sec-ii-l33-44-vouet-arrived-rome",
    "st-chp4-sec-ii-l33-44-vouet-busts-motifs-from-caravaggio",
    "st-chp4-sec-ii-l33-44-vouet-paintings-count",
    "st-chp4-sec-ii-l33-44-vouet-reputation-caravaggio-follower",
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
    segment_text = "\n".join(source_lines[32:44])
    if not source_lines[32].startswith("[Page 102]") or hashlib.sha256(segment_text.encode()).hexdigest() != SEGMENT_SHA256:
        raise SystemExit("preflight failed: segment text or hash changed")

    statements = load_jsonl(statements_path)
    candidate_fields, candidates = read_csv(candidates_path)
    mention_fields, mentions = read_csv(mentions_path)
    segment_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    segment_ids = {row["statement_id"] for row in segment_rows}
    if len(segment_rows) != 25:
        raise SystemExit(f"preflight failed: expected 25 segment statements, got {len(segment_rows)}")
    dual_unknown = {
        row["statement_id"]
        for row in segment_rows
        if row.get("subject_candidate_id") and row.get("object_candidate_id")
        and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    if dual_unknown != UNCLASSIFIED_DUAL_IDS:
        raise SystemExit(f"preflight failed: unclassified dual IDs differ: {sorted(dual_unknown ^ UNCLASSIFIED_DUAL_IDS)}")

    by_statement = {row["statement_id"]: row for row in statements}
    by_candidate = {row["candidate_id"]: row for row in candidates}
    by_mention_id = {row["mention_id"] for row in mentions}
    if by_candidate["cand-5717"]["suggested_type"] != "term":
        raise SystemExit("preflight failed: cand-5717 no longer has the expected misclassification")
    if any(phrase in m["surface_form"] for m in mentions for phrase in (
        "artists who worked for\nCassiano", "painters whom he took under his wing"
    ) if m["segment_id"] == SEGMENT_ID):
        raise SystemExit("preflight failed: one of the exact group mentions is already present")

    next_candidate = max(int(row["candidate_id"].split("-")[1]) for row in candidates) + 1
    group_working_artists = f"cand-{next_candidate:04d}"
    group_protected_painters = f"cand-{next_candidate + 1:04d}"
    expected_candidate_ids = ("cand-11638", "cand-11639")
    if (group_working_artists, group_protected_painters) != expected_candidate_ids:
        raise SystemExit(f"preflight failed: next candidate IDs differ: {(group_working_artists, group_protected_painters)}")

    working_phrase = "artists who worked for\nCassiano"
    protected_phrase = "painters whom he took under his wing"
    working_start = segment_text.index(working_phrase)
    protected_start = segment_text.index(protected_phrase)

    new_candidates = [
        {
            "candidate_id": group_working_artists,
            "index_entry_id": "",
            "canonical_name": "Unidentified artists who worked for Cassiano",
            "index_page_range": "",
            "suggested_type": "",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "An unnamed group of artists who worked for Cassiano and absorbed material from his iconographical collection; membership is not supplied here.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L36",
        },
        {
            "candidate_id": group_protected_painters,
            "index_entry_id": "",
            "canonical_name": "Unidentified painters Cassiano took under his wing",
            "index_page_range": "",
            "suggested_type": "",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "An unnamed collective explicitly described as painters Cassiano took under his wing; membership and the precise support roles are not supplied.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L42",
        },
    ]
    new_mentions = [
        {
            "mention_id": "m-chp4-sec-ii-l33-44-0053",
            "segment_id": SEGMENT_ID,
            "candidate_id": group_working_artists,
            "surface_form": working_phrase,
            "start_char": str(working_start),
            "end_char": str(working_start + len(working_phrase)),
            "note": "Unnamed group explicitly described as artists who worked for Cassiano; the membership is not listed.",
        },
        {
            "mention_id": "m-chp4-sec-ii-l33-44-0054",
            "segment_id": SEGMENT_ID,
            "candidate_id": group_protected_painters,
            "surface_form": protected_phrase,
            "start_char": str(protected_start),
            "end_char": str(protected_start + len(protected_phrase)),
            "note": "Unnamed collective explicitly described as painters Cassiano took under his wing; membership is not listed.",
        },
    ]
    if any(row["mention_id"] in by_mention_id for row in new_mentions):
        raise SystemExit("preflight failed: a planned mention ID already exists")

    decisions = {
        "st-chp4-sec-ii-l33-44-artists-share-antiquarian-rational-interest": (
            True,
            "Haskell links Cassiano's training to the antiquarian and rational passion shared or potentially adopted by nearly all his supported painters; retain the scope and alternative without treating every artist as identical.",
        ),
        "st-chp4-sec-ii-l33-44-caravaggio-attributed-picture": (
            True,
            "The source states that Cassiano owned an unidentified picture while qualifying its attribution to Caravaggio; ownership is explicit and attribution remains reported.",
        ),
        "st-chp4-sec-ii-l33-44-cassiano-supporter-of-vouet": (
            True,
            "Haskell identifies Cassiano as Vouet's most consistent Roman supporter, with 'appears to have been' retained as qualification.",
        ),
        "st-chp4-sec-ii-l33-44-cigoli-leads-florentine-style-shift": (
            True,
            "The source explicitly describes Cigoli as leader of the Florentine artists; their collective identity remains open.",
        ),
        "st-chp4-sec-ii-l33-44-codazzi-architectural-scenes": (
            True,
            "The passage places two unidentified Codazzi architectural scenes in Cassiano's collection; count and Haskell's stylistic qualification are retained.",
        ),
        "st-chp4-sec-ii-l33-44-employed-vouet-for-original-painting": (
            True,
            "Haskell explicitly says Cassiano employed Vouet on a large scale for original painting; the contrast with illustration is retained.",
        ),
        "st-chp4-sec-ii-l33-44-galileo-favorite-painter-cigoli": (
            True,
            "The sentence explicitly names Cigoli as Galileo's favourite painter; the cited correspondence remains a locator, not independent verification.",
        ),
        "st-chp4-sec-ii-l33-44-galileo-occasional-collaborator-cigoli": (
            True,
            "The sentence explicitly identifies Cigoli as Galileo's occasional collaborator; retain 'occasional' and Haskell's attribution.",
        ),
        "st-chp4-sec-ii-l33-44-owned-vouet-genre-picture": (
            True,
            "The source states that Cassiano owned one such Vouet picture; its title and identity remain unspecified.",
        ),
        "st-chp4-sec-ii-l33-44-preferred-vouet-portrait-busts": (
            True,
            "Haskell attributes Cassiano's evident preference for the unidentified group of Vouet portrait busts; retain 'evidently' and group scope.",
        ),
        "st-chp4-sec-ii-l33-44-van-laer-genre-picture": (
            True,
            "The source identifies one unidentified Van Laer genre picture among Cassiano's examples; Haskell's 'cautious' characterization remains attributed.",
        ),
        "st-chp4-sec-ii-l33-44-volume-subject-organization": (
            False,
            "This describes how the paper-museum drawings were organized internally; the person and collection are contextual endpoints, not a binary relation asserted by the classification claim.",
        ),
        "st-chp4-sec-ii-l33-44-vouet-arrived-rome": (
            True,
            "The source explicitly places Vouet's arrival in Rome at about 1614; keep the date approximate and the footnote as a locator.",
        ),
        "st-chp4-sec-ii-l33-44-vouet-busts-motifs-from-caravaggio": (
            True,
            "Haskell explicitly derives motifs in the bust group from pages and subsidiary figures in Caravaggio's religious paintings; no individual source painting is inferred.",
        ),
        "st-chp4-sec-ii-l33-44-vouet-paintings-count": (
            True,
            "Haskell reports Cassiano owned 'some fourteen' pictures by Vouet; the count remains approximate and the works remain an unidentified group.",
        ),
        "st-chp4-sec-ii-l33-44-vouet-reputation-caravaggio-follower": (
            True,
            "The source asserts a reputational relationship: Vouet quickly acquired a reputation as a follower of Caravaggio. This does not establish training or a direct personal tie.",
        ),
    }
    if set(decisions) != UNCLASSIFIED_DUAL_IDS:
        raise SystemExit("script error: decision set does not match the expected unclassified dual statements")

    for statement_id, (status, note) in decisions.items():
        relation_decision(by_statement[statement_id], status, note)

    # The unnamed group is necessary for the source's explicit collection-to-artist relation.
    collection_to_artists = by_statement["st-chp4-sec-ii-l33-44-collection-informed-artists"]
    if collection_to_artists.get("subject_candidate_id") != "cand-5666" or collection_to_artists.get("object_candidate_id") is not None:
        raise SystemExit("preflight failed: collection-to-artist statement endpoints changed")
    collection_to_artists["object_candidate_id"] = group_working_artists
    collection_to_artists.setdefault("qualifiers", {})["mentioned_candidate_ids"] = [
        "cand-5666", group_working_artists, "cand-2036"
    ]
    collection_to_artists["qualifiers"]["qualification"] = (
        "The artists are an unnamed group described as working for Cassiano; the statement says the collection supplied material that they absorbed into their own pictures, without naming the artists or pictures."
    )
    relation_decision(
        collection_to_artists,
        True,
        "The text explicitly says the iconographical collection provided material to the artists who worked for Cassiano and that they absorbed it into their pictures; retain the unnamed group as an open endpoint.",
    )

    # Preserve the supported painters' group as a separate endpoint and record the explicit support relation.
    supported_artists = by_statement["st-chp4-sec-ii-l33-44-artists-share-antiquarian-rational-interest"]
    supported_artists.setdefault("qualifiers", {})["mentioned_candidate_ids"] = [
        "cand-2036", group_protected_painters, "cand-5716"
    ]
    support_statement_id = "st-chp4-sec-ii-l33-44-cassiano-took-painters-under-wing"
    if support_statement_id in {row["statement_id"] for row in statements}:
        raise SystemExit("preflight failed: planned support statement already exists")
    support_statement = {
        "statement_id": support_statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-2036",
        "object_candidate_id": group_protected_painters,
        "predicate": "took_painters_under_his_wing",
        "qualifiers": {
            "source_line_start": 42,
            "source_line_end": 43,
            "claim": "Haskell describes an unnamed group of painters as those Cassiano took under his wing.",
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "pdf_physical_page": 9,
            "printed_page_locator": "p.102",
            "mentioned_candidate_ids": ["cand-2036", group_protected_painters],
            "qualification": "The collective and its members are unnamed; 'under his wing' records Haskell's support characterization but does not specify employment, commissions, or a complete roster.",
            "relation_candidate": True,
            "relation_candidate_note": "The source explicitly states that Cassiano took the unnamed painters under his wing; keep this support relation distinct from the following claim about shared or adopted artistic interests.",
        },
        "original_quote": "the painters whom he took under his wing",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
    }
    statements.insert(statements.index(supported_artists) + 1, support_statement)

    by_candidate["cand-5717"]["suggested_type"] = ""
    candidates.extend(new_candidates)
    mentions.extend(new_mentions)

    preview = {
        "mode": "apply" if args.apply else "dry-run",
        "segment_id": SEGMENT_ID,
        "segment_sha256": SEGMENT_SHA256,
        "initial_dual_unclassified": len(UNCLASSIFIED_DUAL_IDS),
        "decisions_true": sum(status for status, _ in decisions.values()),
        "decisions_false": sum(not status for status, _ in decisions.values()),
        "new_candidates": new_candidates,
        "new_mentions": new_mentions,
        "new_statement": support_statement,
        "changed_candidates": {"cand-5717.suggested_type": "term -> empty (anonymous artist collective)"},
        "revised_statements": [
            {
                "statement_id": collection_to_artists["statement_id"],
                "object_candidate_id": collection_to_artists["object_candidate_id"],
                "relation_candidate": collection_to_artists["qualifiers"]["relation_candidate"],
            },
            {
                "statement_id": supported_artists["statement_id"],
                "subject_candidate_id": supported_artists["subject_candidate_id"],
                "object_candidate_id": supported_artists["object_candidate_id"],
                "relation_candidate": supported_artists["qualifiers"]["relation_candidate"],
            },
        ],
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
