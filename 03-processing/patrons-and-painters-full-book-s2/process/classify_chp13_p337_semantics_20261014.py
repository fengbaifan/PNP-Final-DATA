#!/usr/bin/env python3
"""Review p.337 body statements and repair source mention mappings; dry-run by default."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SEGMENT_ID = "chp-13:13_CHP-13_intro:l52-59"
SEGMENT_SHA256 = "7ef0d455d825a64771a87aa0ebbd3e7b14cd82f3b0e88c56f8c7919de474e986"
PRE_HASHES = {
    STATEMENTS.name: "24ddeb3c6b29c1df76bc9c40826eb27bbf5f9f380974caa71ee2cb5ecd8f2a91",
    CANDIDATES.name: "d844a9803942ecb175d79b8350aa714235dbb144116ff6f0c93c96820636f49a",
    MENTIONS.name: "96c9a94c87254b8d3fc1e55b3242baa94ebcf5e5cea33bb3897c48a0365469d8",
}
BACKUP_SUFFIX = ".bak-s2-ch13-p337-semantic-review-20261014"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_atomic(path: Path, data: bytes) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def csv_bytes(fields: list[str], rows: list[dict]) -> bytes:
    with tempfile.SpooledTemporaryFile(
        mode="w+", encoding="utf-8-sig", newline="", max_size=8 * 1024 * 1024
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        stream.seek(0)
        return stream.read().encode("utf-8-sig")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after all preflight checks")
    args = parser.parse_args()

    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        actual = digest(path)
        expected = PRE_HASHES[path.name]
        if actual != expected:
            raise SystemExit(f"preflight failed: {path.name} SHA-256 {actual} != {expected}")
    segment = next(
        (row for row in read_jsonl(TABLES / "segments.jsonl") if row.get("segment_id") == SEGMENT_ID),
        None,
    )
    if not segment or segment.get("sha256") != SEGMENT_SHA256:
        raise SystemExit("preflight failed: p.337 segment identity/hash changed")

    statements = read_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("preflight failed: duplicate statement_id")
    local = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    if len(local) != 30:
        raise SystemExit(f"preflight failed: expected 30 p.337 body statements, found {len(local)}")
    unset = {
        row["statement_id"]
        for row in local
        if row.get("qualifiers", {}).get("relation_candidate") is None
    }
    decisions = {
        "st-chp13-p337-dactylografa-latin-only-scholarly-audience": True,
        "st-chp13-p337-dactylografa-neoclassical-style": False,
        "st-chp13-p337-dactylografa-simpler-presentation-than-albrizzi-book": True,
        "st-chp13-p337-goldoni-acknowledged-higher-cost": False,
        "st-chp13-p337-goldoni-edition-designed-as-new-departure": False,
        "st-chp13-p337-goldoni-favoured-elegant-clean-page": True,
        "st-chp13-p337-haskell-goldoni-edition-not-luxury-enterprise": False,
        "st-chp13-p337-officium-distinct-from-pasquali-general-output": True,
        "st-chp13-p337-officium-plates-religious-intimacy": False,
        "st-chp13-p337-pasquali-admired-lodoli": True,
        "st-chp13-p337-pasquali-limited-ceremonial-pamphlets": False,
    }
    if unset != set(decisions):
        raise SystemExit(f"preflight failed: unexpected unset IDs: {sorted(unset ^ set(decisions))}")
    for statement_id, value in decisions.items():
        by_id[statement_id]["qualifiers"]["relation_candidate"] = value

    # Source-defined groups and concepts are distinct candidates; do not collapse them into
    # indexed people, or imply a membership, title list, or exact censoring authority.
    new_candidates = [
        {
            "candidate_id": "cand-12143",
            "index_entry_id": "",
            "canonical_name": "Scholarly public intended for Dactylografa Smithiana",
            "index_page_range": "",
            "suggested_type": "term",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell identifies an intended scholarly readership for the Latin-only text; no individual readers, membership, or reception evidence is specified.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": SEGMENT_ID + "#L55",
        },
        {
            "candidate_id": "cand-12144",
            "index_entry_id": "",
            "canonical_name": "General publishing output of Giambattista Pasquali (unnamed group)",
            "index_page_range": "",
            "suggested_type": "archive",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Source-defined publication group used as the comparator for the specially commissioned Officium; Haskell names no complete title list. Keep distinct from the p.336 fine and luxurious books group cand-12142.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": SEGMENT_ID + "#L57",
        },
        {
            "candidate_id": "cand-12145",
            "index_entry_id": "",
            "canonical_name": "Clients who bought copies of Beccaria's forbidden book from Pasquali",
            "index_page_range": "",
            "suggested_type": "term",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell says Pasquali disclosed the names of these buyers under pressure. No client is named or individually identifiable in this passage.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": SEGMENT_ID + "#L53",
        },
        {
            "candidate_id": "cand-12146",
            "index_entry_id": "",
            "canonical_name": "Elegant pamphlets for aristocratic ceremonies (publishing category)",
            "index_page_range": "",
            "suggested_type": "term",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "A publication category in Haskell's statement about Pasquali's limited interest; no individual pamphlet is named.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": SEGMENT_ID + "#L53",
        },
        {
            "candidate_id": "cand-12147",
            "index_entry_id": "",
            "canonical_name": "Publishing censorship that constrained Pasquali (authority unspecified)",
            "index_page_range": "",
            "suggested_type": "term",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell says Pasquali implied that censorship prevented him publishing what he wanted. The specific rule, censor, and administrative decision are not identified; leave alignment with the broader Venice censorship candidate cand-9708 for later review.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": SEGMENT_ID + "#L53",
        },
    ]

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        candidate_fields = reader.fieldnames
        candidates = list(reader)
    candidate_ids = {row["candidate_id"] for row in candidates}
    if any(row["candidate_id"] in candidate_ids for row in new_candidates):
        raise SystemExit("preflight failed: one or more new candidate IDs already exist")
    candidates.extend(new_candidates)

    with MENTIONS.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        mention_fields = reader.fieldnames
        mentions = list(reader)
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if len(mention_by_id) != len(mentions):
        raise SystemExit("preflight failed: duplicate mention_id")
    expected_old_mappings = {
        "m-s2-ch13-p337-003": "cand-1850",
        "m-s2-ch13-p337-004": "cand-1850",
        "m-s2-ch13-p337-008": "cand-1850",
        "m-s2-ch13-p337-009": "cand-1844",
    }
    for mention_id, expected_candidate in expected_old_mappings.items():
        if mention_id not in mention_by_id or mention_by_id[mention_id]["candidate_id"] != expected_candidate:
            raise SystemExit(f"preflight failed: unexpected candidate mapping for {mention_id}")
    mention_by_id["m-s2-ch13-p337-003"]["candidate_id"] = "cand-12147"
    mention_by_id["m-s2-ch13-p337-003"]["note"] = (
        "Source-specific censorship concept; the authority and exact measure are unnamed."
    )
    mention_by_id["m-s2-ch13-p337-004"]["candidate_id"] = "cand-10167"
    mention_by_id["m-s2-ch13-p337-004"]["note"] = (
        "The consolidated note identifies Pasquali's letter to Niccola Mazzoni and cites it through Nuti; "
        "the letter was not independently consulted."
    )
    mention_by_id["m-s2-ch13-p337-008"]["candidate_id"] = "cand-12145"
    mention_by_id["m-s2-ch13-p337-008"]["note"] = (
        "Source-defined group of buyers; Haskell names no individual clients."
    )
    mention_by_id["m-s2-ch13-p337-009"]["candidate_id"] = "cand-12146"
    mention_by_id["m-s2-ch13-p337-009"]["note"] = (
        "Publication category, not an identified pamphlet."
    )

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    # Existing mention offsets include the S0 page marker at L52 before the body text at L53.
    segment_text = "\n".join(source_lines[51:59])
    if mention_by_id["m-s2-ch13-p337-003"]["start_char"] != str(segment_text.find("the censorship")):
        raise SystemExit("preflight failed: current p.337 mention offsets do not match the body text")
    new_mentions = []
    for mention_id, candidate_id, surface, note in [
        (
            "m-s2-ch13-p337-045",
            "cand-12143",
            "a more scholarly public",
            "Haskell's stated intended readership; no individual members are identified.",
        ),
        (
            "m-s2-ch13-p337-046",
            "cand-12144",
            "general run of Pasquali",
            "The raw S0 surface contains OCR errors; the scan reads 'general run of Pasquali's publications'.",
        ),
    ]:
        if mention_id in mention_by_id:
            raise SystemExit(f"preflight failed: {mention_id} already exists")
        start = segment_text.find(surface)
        if start < 0 or segment_text.find(surface, start + 1) >= 0:
            raise SystemExit(f"preflight failed: mention surface is missing or ambiguous: {surface!r}")
        end = start + len(surface)
        if mention_id.endswith("-046"):
            end = segment_text.find(".", start)
            if end < 0:
                raise SystemExit("preflight failed: end of general-publications mention is missing")
        new_mentions.append(
            {
                "mention_id": mention_id,
                "segment_id": SEGMENT_ID,
                "candidate_id": candidate_id,
                "surface_form": segment_text[start:end],
                "start_char": str(start),
                "end_char": str(end),
                "note": note,
            }
        )
    mentions.extend(new_mentions)

    latin = by_id["st-chp13-p337-dactylografa-latin-only-scholarly-audience"]
    latin["object_candidate_id"] = "cand-12143"
    latin["qualifiers"]["mentioned_candidate_ids"] = ["cand-1848", "cand-12143"]
    latin["qualifiers"]["qualification"] = (
        "Haskell explicitly identifies intended scholarly readership; this is not evidence of actual readership or reception."
    )

    comparison = by_id["st-chp13-p337-officium-distinct-from-pasquali-general-output"]
    comparison["object_candidate_id"] = "cand-12144"
    comparison["qualifiers"]["mentioned_candidate_ids"] = ["cand-1849", "cand-12144"]
    comparison["qualifiers"]["qualification"] = (
        "This is Haskell's explicit contrast between the specially commissioned Officium and an unnamed aggregate of Pasquali publications."
    )

    censorship = by_id["st-chp13-p337-pasquali-chafed-under-censorship"]
    if censorship.get("object_candidate_id") != "cand-1850":
        raise SystemExit("preflight failed: censorship statement endpoint changed")
    censorship["object_candidate_id"] = "cand-12147"
    censorship["qualifiers"]["mentioned_candidate_ids"] = ["cand-1844", "cand-12147", "cand-10167"]
    censorship["qualifiers"]["qualification"] = (
        "The body says Pasquali implied in a letter that censorship prevented desired publication; "
        "the cited letter is identified at p.337 note 2 but was not independently consulted."
    )

    clients = by_id["st-chp13-p337-pasquali-revealed-book-clients-under-pressure"]
    if clients.get("object_candidate_id") is not None:
        raise SystemExit("preflight failed: client disclosure statement already has an endpoint")
    clients["object_candidate_id"] = "cand-12145"
    clients["qualifiers"]["relation_candidate"] = True
    clients["qualifiers"]["mentioned_candidate_ids"] = ["cand-1844", "cand-12145", "cand-9707"]
    clients["qualifiers"]["qualification"] = (
        "The statement links Pasquali to an unnamed source-defined group of buyers; it does not identify any client individually."
    )

    pamphlets = by_id["st-chp13-p337-pasquali-limited-ceremonial-pamphlets"]
    pamphlets["qualifiers"]["mentioned_candidate_ids"] = ["cand-1844", "cand-12146"]
    pamphlets["qualifiers"]["qualification"] = (
        "This is a qualified claim about Pasquali's interest in a publication category, not a claim that he never produced such pamphlets."
    )

    cost = by_id["st-chp13-p337-goldoni-acknowledged-higher-cost"]
    cost["subject_candidate_id"] = "cand-1851"
    cost["object_candidate_id"] = None
    cost["predicate"] = "expected_to_cost_more_with_improved_production"
    cost["qualifiers"]["claim"] = (
        "Haskell says that greater attention to paper, printing, and illustration would make the edition more expensive."
    )
    cost["qualifiers"]["speaker"] = "Haskell"
    cost["qualifiers"]["text_layer"] = "authorial narrative"
    cost["qualifiers"]["qualification"] = (
        "This is Haskell's narrative bridge before the direct Goldoni quotation beginning after 'but'; no price is given."
    )
    cost["qualifiers"]["mentioned_candidate_ids"] = ["cand-1851"]

    luxury = by_id["st-chp13-p337-haskell-goldoni-edition-not-luxury-enterprise"]
    luxury["subject_candidate_id"] = "cand-1851"
    luxury["object_candidate_id"] = None
    luxury["qualifiers"]["mentioned_candidate_ids"] = ["cand-1851", "cand-1844", "cand-1205"]

    print(f"segment={SEGMENT_ID}; SHA-256={SEGMENT_SHA256}; statements={len(local)}; classified={len(decisions)}")
    for statement_id, value in decisions.items():
        print(f"  {statement_id}: {value}")
    print("endpoint repairs: Latin audience -> cand-12143; Officium comparator -> cand-12144")
    print("relation endpoint repairs: censorship -> cand-12147; unnamed buyers -> cand-12145")
    print("mention repairs: censorship, Prato letter, unnamed buyers, and pamphlet category")
    print("speaker correction: higher-cost sentence is Haskell's narrative, not Goldoni's quotation")
    for row in new_mentions:
        print(f"new mention: {row['mention_id']} {row['candidate_id']} [{row['start_char']},{row['end_char']}): {row['surface_form']!r}")
    print("new candidates: cand-12143 through cand-12147")
    if not args.apply:
        print("DRY RUN only; no files written. Pass --apply to write after review.")
        return

    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"refusing to overwrite existing backup: {backup.name}")
    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
    statement_bytes = (
        "\n".join(json.dumps(row, ensure_ascii=False) for row in statements) + "\n"
    ).encode("utf-8")
    write_atomic(STATEMENTS, statement_bytes)
    write_atomic(CANDIDATES, csv_bytes(candidate_fields, candidates))
    write_atomic(MENTIONS, csv_bytes(mention_fields, mentions))
    print("APPLIED. Backups saved for statements, candidates, and mentions.")
    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        print(f"  {path.name}: {digest(path)}")


if __name__ == "__main__":
    main()
