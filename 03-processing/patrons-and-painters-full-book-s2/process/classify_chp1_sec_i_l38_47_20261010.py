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
STATEMENTS = TABLES / "book-statements.jsonl"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp1-sec-i-l38-47-20261010"
SEGMENT_ID = "chp-1:01_CHP-1_sec_i:l38-47"

EXPECTED_HASHES = {
    "04-knowledge/tables/book-statements.jsonl": "1d36eb8d063f2fc1f33d0659042c44d95a576373425a05a7d5cd02f8b56a91bf",
    "04-knowledge/tables/entity-candidates.csv": "b214ec44c825690db146c4efdcb96e1de4acbbc5d682104ec0c35535d53b2dae",
    "04-knowledge/tables/mentions.csv": "10eb1687c3af1f4515cae4c68273a263f530dd3c8bb3613a3d2b26ddd9a54647",
    "04-knowledge/tables/s2-coverage.csv": "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    "02-sources/02-Markdown/01_CHP-1_sec_i.md": "fb6198d0392e70a23a2d9ed05c0d432d4466de4ba75cc96762e3b4e45a204c40",
    "02-sources/02-Markdown/01_CHP-1.md": "2c99c1b372f756b1482d746f5714fe930b538118792b52a3de0834f585d4f3fb",
}

TARGETS = {
    "st-chp1-l89-92-ameyden-piety": ("cand-0093", "cand-3104", "attributed_historical_testimony", 89, 92),
    "st-chp1-l142-citation-chain": ("cand-3411", "cand-3412", "citation_transmission", 142, 142),
    "st-chp1-l179-180-vasalli-testimony-context": ("cand-3414", "cand-1676", "testified_on_behalf_of", 179, 180),
    "st-chp1-l180-185-vasalli-princely-service": ("cand-3414", "cand-1814", "court_service_obligation_testimony", 180, 185),
    "st-chp1-l186-187-pio-travel": ("cand-3415", "cand-0385", "sent_protege_to_cities", 186, 187),
    "st-chp1-l186-187-rospigliosi-travel": ("cand-2263", "cand-1169", "sent_artist_to_venice", 186, 187),
    "st-chp1-l188-189-baldoini-appointment": ("cand-2387", "cand-0167", "appointed_as_painter", 188, 189),
}

DECISIONS = {
    "st-chp1-l89-92-ameyden-piety": (False,
        "Ameyden is the cited reporter and Urban VIII is the historical subject/time context. The endpoints do not state a direct relation between these people; preserve the attributed testimony."),
    "st-chp1-l142-citation-chain": (False,
        "The footnote gives a bibliographic transmission chain (Panciroli p. 800 through Ortolani). These endpoints are person candidates, not identified archive/work records, so the note does not establish a person-to-person relation. Preserve the citation attribution; a source-to-source citation needs identified archive endpoints."),
    "st-chp1-l179-180-vasalli-testimony-context": (True,
        "The source directly states that Alessandro Vasalli testified on Mola's behalf. Keep the dispute with Prince Pamfili and the secondary-source attribution as context."),
    "st-chp1-l180-185-vasalli-princely-service": (False,
        "The embedded testimony describes a general obligation for artists receiving a household allowance; Vasalli and Prince Pamfili are the witness and dispute context, not endpoints of that rule. Do not generalize the testimony beyond its source."),
    "st-chp1-l186-187-pio-travel": (True,
        "Haskell's note, citing Pascoli, says Cardinal Pio sent his protege Giovanni Bonari on the stated city itinerary. Preserve the unresolved identity of Cardinal Pio and the Bonari/Bonati reading note."),
    "st-chp1-l186-187-rospigliosi-travel": (True,
        "The note directly says Cardinal Rospigliosi sent Lodovico Gimignani to Venice. Preserve the cited-source scope and do not add details about the trip."),
    "st-chp1-l188-189-baldoini-appointment": (True,
        "The note directly records Cardinal Maurizio di Savoia appointing Gio. Gasparo Baldoini as per nostro pittore. Preserve the stated role and bibliographic attribution."),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"PRECONDITION FAILED: {message}")


def load_jsonl() -> list[dict]:
    return [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8").splitlines() if line.strip()]


def flag(row: dict):
    return row.get("qualifiers", {}).get("relation_candidate")


def bilateral(row: dict) -> bool:
    return bool(row.get("subject_candidate_id") and row.get("object_candidate_id"))


def counts(rows: list[dict]) -> dict[str, int]:
    return {
        "statements": len(rows),
        "relation_true": sum(flag(row) is True for row in rows),
        "relation_false": sum(flag(row) is False for row in rows),
        "true_bilateral": sum(flag(row) is True and bilateral(row) for row in rows),
        "true_open": sum(flag(row) is True and not bilateral(row) for row in rows),
        "false_bilateral": sum(flag(row) is False and bilateral(row) for row in rows),
        "unclassified_bilateral": sum(bilateral(row) and flag(row) is None for row in rows),
    }


def preflight() -> list[dict]:
    for relative, expected in EXPECTED_HASHES.items():
        path = ROOT / relative
        require(path.exists() and sha256(path) == expected, f"input hash changed: {relative}")

    expected_types = {
        "cand-0093": "person", "cand-3104": "person", "cand-3411": "person", "cand-3412": "person",
        "cand-3414": "person", "cand-1676": "person", "cand-1814": "person", "cand-3415": "person",
        "cand-0385": "person", "cand-2263": "person", "cand-1169": "person", "cand-2387": "person",
        "cand-0167": "person",
    }
    candidates = {
        row["candidate_id"]: row
        for row in csv.DictReader((TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline=""))
    }
    for candidate_id, expected_type in expected_types.items():
        require(candidate_id in candidates, f"missing candidate {candidate_id}")
        require(candidates[candidate_id]["suggested_type"] == expected_type,
                f"unexpected candidate type for {candidate_id}")

    coverage = list(csv.DictReader((TABLES / "s2-coverage.csv").open(encoding="utf-8-sig", newline="")))
    matching = [row for row in coverage if row.get("segment_id") == SEGMENT_ID]
    require(len(matching) == 1 and matching[0].get("disposition") == "reviewed"
            and matching[0].get("migration_status") == "complete", "coverage must be reviewed/complete")

    mentions = list(csv.DictReader((TABLES / "mentions.csv").open(encoding="utf-8-sig", newline="")))
    segment_candidates = {row.get("candidate_id") for row in mentions if row.get("segment_id") == SEGMENT_ID}
    require(set(expected_types) <= segment_candidates, "an endpoint candidate lacks a mention in the segment")

    source = (ROOT / "02-sources/02-Markdown/01_CHP-1.md").read_text(encoding="utf-8").splitlines()
    for line_number, phrase in {
        89: "Ameyden, Relatione della città di Roma",
        142: "Panciroli, p. 800, quoted by Ortolani.",
        179: "Alessandro Vasalli, a painter who testified on Mola",
        180: "behalf in his troubles with Prince Pamfili",
        186: "Cardinal Pio sent his protégé Giovanni Bonari to Florence",
        187: "Cardinal Rospigliosi sent Lodovico Gimignani to Venice",
        188: "The appointment of Gio. Gasparo Baldoini",
    }.items():
        require(phrase in source[line_number - 1], f"source anchor changed at line {line_number}")

    rows = load_jsonl()
    by_id = {row.get("statement_id"): row for row in rows}
    require(len(by_id) == len(rows), "statement IDs are not unique")
    require(set(TARGETS) <= set(by_id), "one or more target statements are missing")
    require(counts(rows) == {
        "statements": 12692, "relation_true": 3874, "relation_false": 1797,
        "true_bilateral": 3847, "true_open": 27, "false_bilateral": 432,
        "unclassified_bilateral": 4210,
    }, "current statement totals changed")

    selected = []
    for statement_id, (subject, object_, predicate, start, end) in TARGETS.items():
        row = by_id[statement_id]
        q = row.get("qualifiers", {})
        require(row.get("segment_id") == SEGMENT_ID, f"segment changed for {statement_id}")
        require(row.get("subject_candidate_id") == subject and row.get("object_candidate_id") == object_,
                f"endpoints changed for {statement_id}")
        require(row.get("predicate") == predicate, f"predicate changed for {statement_id}")
        require(q.get("source_line_start") == start and q.get("source_line_end") == end,
                f"source anchor changed for {statement_id}")
        require(flag(row) is None, f"already classified: {statement_id}")
        selected.append(row)
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify first chapter section i statements L38-47 with source-hash preflight.")
    parser.add_argument("--apply", action="store_true", help="write the preflighted classifications")
    args = parser.parse_args()
    selected = preflight()
    rows = load_jsonl()
    updated = [dict(row) for row in rows]
    for row in updated:
        sid = row.get("statement_id")
        if sid in DECISIONS:
            value, note = DECISIONS[sid]
            row["qualifiers"] = dict(row.get("qualifiers", {}))
            row["qualifiers"]["relation_candidate"] = value
            row["qualifiers"]["relation_candidate_note"] = note

    print("PREVIEW: chp-1:01_CHP-1_sec_i:l38-47")
    for row in selected:
        print(f"  {row['statement_id']}: {row['predicate']} -> relation_candidate={DECISIONS[row['statement_id']][0]}")
    print("  no endpoint, predicate, source quote, candidate, mention or statement-count changes")
    print("  counts before:", json.dumps(counts(rows), sort_keys=True))
    print("  counts after: ", json.dumps(counts(updated), sort_keys=True))
    if not args.apply:
        print("DRY RUN ONLY; no files written. Use --apply to apply the classifications.")
        return

    require(not BACKUP.exists(), f"backup already exists: {BACKUP.relative_to(ROOT)}")
    shutil.copy2(STATEMENTS, BACKUP)
    payload = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in updated) + "\n"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", dir=STATEMENTS.parent, delete=False) as handle:
        temp_path = Path(handle.name)
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp_path, STATEMENTS)
    print(f"APPLIED; backup: {BACKUP.relative_to(ROOT)}")
    print(f"new SHA-256: {sha256(STATEMENTS)}")


if __name__ == "__main__":
    main()
