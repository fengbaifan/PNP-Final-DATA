from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
SOURCE_I = ROOT / "02-sources/02-Markdown/15_CHP-15_sec_i.md"
SOURCE_II = ROOT / "02-sources/02-Markdown/15_CHP-15_sec_ii.md"
GROUP_ID = "st-chp15-p362-lodoli-direct-inspirer-of-three-patrons"
TARGETS = [
    ("cand-1002", "Farsetti, Filippo", "farsetti", "Filippo Farsetti"),
    ("cand-1642", "Memmo, Andrea", "memmo", "Andrea Memmo"),
    ("cand-2075", "Querini, Angelo", "querini", "Angelo Querini"),
]
NEW_IDS = [f"st-chp15-p362-lodoli-direct-inspirer-of-{slug}" for _, _, slug, _ in TARGETS]
CLAUSE = (
    "Filippo Farsetti.1 He was born in 1703 of an exceedingly rich family that had only acquired "
    "patrician status in 1664, and at about the age of 17 or 18 he became the pupil of Padre "
    "Lodoli2—the direct inspirer of all three patrons discussed in this chapter."
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_lines() -> tuple[bytes, list[str], list[dict]]:
    raw = TABLE.read_bytes()
    text = raw.decode("utf-8")
    lines = text.splitlines(keepends=True)
    records = [json.loads(line) for line in lines if line.strip()]
    return raw, lines, records


def validate_source_and_candidates() -> None:
    source_i = SOURCE_I.read_text(encoding="utf-8").splitlines()
    source_ii = SOURCE_II.read_text(encoding="utf-8").splitlines()
    if len(source_i) < 17 or CLAUSE not in source_i[16]:
        raise SystemExit("S0 line 17 no longer contains the exact p.362 quotation.")
    if source_i[2].strip().casefold() != "filippo farsetti":
        raise SystemExit("Chapter section heading for Filippo Farsetti does not match the reviewed source.")
    headings = {line.strip().casefold() for line in source_ii}
    if "andrea memmo" not in headings or "angelo querini" not in headings:
        raise SystemExit("The chapter's Andrea Memmo and Angelo Querini headings were not both found.")
    with CANDIDATES.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    by_id = {row.get("candidate_id"): row for row in rows}
    for candidate_id, canonical_name, _, _ in TARGETS + [("cand-1411", "Lodoli, Padre Carlo", "lodoli", "Padre Carlo Lodoli")]:
        row = by_id.get(candidate_id)
        if row is None or row.get("canonical_name") != canonical_name or row.get("suggested_type") != "person":
            raise SystemExit(f"Candidate identity/type precondition failed for {candidate_id}.")


def build_rows(group: dict) -> tuple[dict, list[dict]]:
    parent = json.loads(json.dumps(group))
    parent["qualifiers"]["relation_candidate"] = False
    parent["qualifiers"]["qualification"] = (
        "This retained group-level statement records Haskell's explicit claim that Lodoli directly inspired all three "
        "patrons discussed in the chapter. The named patron sections identify them as Farsetti, Memmo, and Querini; "
        "three scalar S2 relation-candidate statements resolve that collective reference. The group statement retains "
        "the original source context and footnote link."
    )

    children = []
    for (candidate_id, _, _, name), statement_id in zip(TARGETS, NEW_IDS, strict=True):
        qualifiers = {
            "source_line_start": 17,
            "source_line_end": 17,
            "printed_page": 362,
            "pdf_physical_page": 2,
            "claim": f"Haskell identifies Padre Carlo Lodoli as the direct inspirer of {name}, one of the chapter's three patrons.",
            "speaker": "Haskell",
            "text_layer": "authorial report",
            "qualification": (
                "The phrase 'all three patrons discussed in this chapter' is resolved from the chapter's named patron "
                "sections: Filippo Farsetti, Andrea Memmo, and Angelo Querini. This is a source-grounded S2 referent "
                "resolution, not independent historical verification or S3 identity alignment."
            ),
            "mentioned_candidate_ids": ["cand-1411", "cand-1002"],
            "referent_resolution_basis": "Chapter 15 section headings on the two source files identify the three patron subjects.",
            "parent_body_statement_ids": [GROUP_ID],
            "relation_candidate": True,
        }
        children.append(
            {
                "statement_id": statement_id,
                "segment_id": group["segment_id"],
                "subject_candidate_id": "cand-1411",
                "object_candidate_id": candidate_id,
                "predicate": "described_as_direct_inspirer_of",
                "qualifiers": qualifiers,
                "original_quote": CLAUSE,
                "origin": "book",
                "source_file": group["source_file"],
            }
        )
    return parent, children


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve the p.362 group referent to the three chapter patron candidates.")
    parser.add_argument("--apply", action="store_true", help="Write the reviewed changes after the exact table hash is supplied.")
    parser.add_argument("--expected-table-sha256", help="SHA-256 printed by the dry run; required with --apply.")
    args = parser.parse_args()

    validate_source_and_candidates()
    raw, lines, records = load_lines()
    current_hash = sha256(raw)
    matches = [record for record in records if record.get("statement_id") == GROUP_ID]
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one group statement; found {len(matches)}.")
    group = matches[0]
    if group.get("subject_candidate_id") != "cand-1411" or group.get("object_candidate_id") is not None:
        raise SystemExit("The p.362 group statement no longer has the reviewed Lodoli/open-target endpoints.")
    if group.get("qualifiers", {}).get("relation_candidate") is not True:
        raise SystemExit("The p.362 group statement is already not an open relation candidate.")
    if any(record.get("statement_id") in NEW_IDS for record in records):
        raise SystemExit("One or more planned child statement IDs already exist; inspect current state before retrying.")

    parent, children = build_rows(group)
    print(f"table_sha256={current_hash}")
    print(f"group_statement={GROUP_ID}: relation_candidate true -> false; object endpoint remains group-level/null")
    print("resolved_targets=" + ", ".join(f"{name} ({candidate_id})" for candidate_id, _, _, name in TARGETS))
    print("new_relation_statements=" + ", ".join(NEW_IDS))
    print("expected_counts_after_apply: statements +3; relation_candidates +2; complete_endpoints +3; open_endpoints -1")
    if not args.apply:
        print("DRY-RUN: no files changed.")
        return
    if not args.expected_table_sha256 or args.expected_table_sha256 != current_hash:
        raise SystemExit("--apply requires --expected-table-sha256 equal to the current dry-run hash.")

    backup = TABLE.with_name("book-statements.jsonl.bak-s2-handoff-p362-lodoli-endpoints-20261009")
    if backup.exists():
        raise SystemExit(f"Refusing to overwrite existing recovery copy: {backup}")
    shutil.copy2(TABLE, backup)

    newline = "\r\n" if b"\r\n" in raw else "\n"
    output_lines: list[str] = []
    inserted = False
    for line in lines:
        if not line.strip():
            output_lines.append(line)
            continue
        record = json.loads(line)
        if record.get("statement_id") == GROUP_ID:
            output_lines.append(json.dumps(parent, ensure_ascii=False, separators=(",", ":")) + newline)
            output_lines.extend(json.dumps(child, ensure_ascii=False, separators=(",", ":")) + newline for child in children)
            inserted = True
        else:
            output_lines.append(line)
    if not inserted:
        raise SystemExit("The group row disappeared during preflight; no table write performed.")

    temp = TABLE.with_name(TABLE.name + ".tmp-s2-handoff-p362")
    temp.write_bytes("".join(output_lines).encode("utf-8"))
    os.replace(temp, TABLE)
    print(f"APPLIED: {TABLE}")
    print(f"recovery_copy={backup}")
    print(f"recovery_sha256={sha256(backup.read_bytes())}")
    print(f"new_table_sha256={sha256(TABLE.read_bytes())}")


if __name__ == "__main__":
    main()
