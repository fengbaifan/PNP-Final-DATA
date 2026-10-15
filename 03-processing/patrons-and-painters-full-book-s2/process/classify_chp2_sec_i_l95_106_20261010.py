from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_i.md"
SEGMENT_ID = "chp-2:02_CHP-2_sec_i:l95-106"
BACKUP_SUFFIX = ".bak-s2-chp2-sec-i-l95-106-20261010"
GROUP_ID = "cand-11580"
GROUP_MENTION_ID = "m-chp2-seci-l95-106-0091"
GROUP_SURFACE = "Dr. Salerno and other investigators"
MISSING_MENTIONS = [
    ("m-chp2-seci-l95-106-0087", "cand-4305", "a series of canvases of effeminate young boys",
     "Untitled, uncounted canvas group attributed to Caravaggio."),
    ("m-chp2-seci-l95-106-0088", "cand-4315", "‘large room with old pictures’",
     "Room in Giustiniani’s palace where the thirteen Caravaggio paintings were hung."),
    ("m-chp2-seci-l95-106-0089", "cand-4338", "contemporary art",
     "Category of contemporary art described as receiving the highest level in the collection display."),
    ("m-chp2-seci-l95-106-0090", "cand-4322", "an essay to theorise his eclecticism",
     "Untitled essay by Vincenzo Giustiniani; no title or independent consultation is supplied."),
]
EXPECTED_MISSING_ENDPOINTS = {"cand-4305", "cand-4315", "cand-4338", "cand-4322"}

EXPECTED_HASHES = {
    "book-statements.jsonl": "8dcf7a68aeae95d94b666b8f379af3ab7b5a061e66616f2257094b5876656688",
    "entity-candidates.csv": "74c13ddfd8b5ebbe933fd602830288c199b46deb0ae806b2d7d03902147d8f56",
    "mentions.csv": "7f7b189100c8ccfbec588141eb527d13179cc6614bf31bdb19141a2c6bc0e7fc",
    "s2-coverage.csv": "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    "02_CHP-2_sec_i.md": "5eca92acb03fe9934be85c82a6ec6806d3c564002955e99bd317916f3c7c8dc6",
}

EXPECTED_ROWS = {
    "st-chp2-seci-l95-106-canvases-by-caravaggio": ("cand-4305", "cand-0544", "created_by_reported", 97, 97, "a series of canvases of effeminate young boys by Caravaggio"),
    "st-chp2-seci-l95-106-caravaggio-household": ("cand-0544", "cand-1691", "resided_in_household_of_reported", 97, 97, "who had lived in his household"),
    "st-chp2-seci-l95-106-committee-influence": ("cand-1691", "cand-4306", "influence_on_committee_reported", 97, 97, "used his overwhelming influence on the Committee"),
    "st-chp2-seci-l95-106-contemporary-art-level": ("cand-1200", "cand-4338", "collection_display_interpreted_as", 103, 103, "placed contemporary art on the very highest level"),
    "st-chp2-seci-l95-106-contrast-fragment": ("cand-1200", "cand-4313", "authorial_argument_fragment", 103, 103, "And yet his taste, as revealed in his actual collection"),
    "st-chp2-seci-l95-106-country-house-design": ("cand-4311", "cand-1200", "designed_by_reported", 100, 100, "which he himself had helped to design"),
    "st-chp2-seci-l95-106-country-house-location": ("cand-4311", "cand-4312", "located_at_reported", 100, 100, "country house at Bassano di Sutri"),
    "st-chp2-seci-l95-106-cupid-iconography": ("cand-4320", "cand-4321", "depicts_reported", 102, 102, "the winged, yet all too human, Cupid sitting on a rumpled bed"),
    "st-chp2-seci-l95-106-cupid-interest-inference": ("cand-4320", "cand-1691", "authorial_inference", 102, 102, "only one to suggest that Giustiniani shared Cardinal del Monte’s specialised interest in Caravaggio"),
    "st-chp2-seci-l95-106-essay-purpose": ("cand-4322", "cand-4337", "artistic_argument_reported", 103, 103, "he even wrote an essay to theorise his eclecticism"),
    "st-chp2-seci-l95-106-followers-employed": ("cand-1200", "cand-4317", "employed_group_reported", 101, 101, "Vincenzo continued to employ some of Caravaggio’s Northern followers"),
    "st-chp2-seci-l95-106-hopf-publication": ("cand-4336", "cand-4335", "publication_history_reported", 105, 106, "was published in the\nGiornale Linguistico"),
    "st-chp2-seci-l95-106-hopf-publication-place": ("cand-4336", "cand-1131", "publication_place_reported", 106, 106, "Giornale Linguistico, Genoa, in 1881 and 1882"),
    "st-chp2-seci-l95-106-hopf-relevance": ("cand-4336", "cand-1200", "authorial_relevance_assessment", 106, 106, "of no importance for the Marchese Vincenzo"),
    "st-chp2-seci-l95-106-hopf-untraceable": ("cand-4323", "cand-4336", "reported_unable_to_trace", 105, 105, "Dr. Salerno and other investigators have been unable to trace"),
    "st-chp2-seci-l95-106-launched-dangeli": ("cand-1691", "cand-0105", "launched_artist_reported", 97, 97, "He launched the landscape painter Filippo d’Angeli"),
    "st-chp2-seci-l95-106-lighting-comparison": ("cand-0488", "cand-0544", "authorial_qualified_comparison", 102, 102, "may well have seemed to anticipate those of Caravaggio"),
    "st-chp2-seci-l95-106-owner-preference": ("cand-1200", "cand-4320", "preferred_work_reported", 102, 102, "most appealed to its proorictor"),
    "st-chp2-seci-l95-106-painting-collection-location": ("cand-4313", "cand-3126", "located_in_reported", 100, 100, "one of the most remarkable collections of paintings in Rome"),
    "st-chp2-seci-l95-106-palace-near-church": ("cand-4310", "cand-0706", "located_near_reported", 100, 100, "palace near S. Luigi dei Frances!"),
    "st-chp2-seci-l95-106-sacchi-commission": ("cand-1691", "cand-2318", "secured_commission_reported", 97, 98, "obtain an important commission for the virtually unknown Andrea Sacchi"),
    "st-chp2-seci-l95-106-sacchi-employment": ("cand-1691", "cand-2318", "employed_artist_at_reported", 97, 98, "whom he had employed in his casino near the Piazza del"),
    "st-chp2-seci-l95-106-sandart-advice": ("cand-2353", "cand-4320", "display_advice_reported", 102, 102, "on the advice of the German Joachim von Sandrart"),
    "st-chp2-seci-l95-106-thirteen-displayed": ("cand-4315", "cand-4316", "displayed_works_reported", 101, 101, "in his palace were hung thirteen by Caravaggio"),
}

NOTES = {
    "st-chp2-seci-l95-106-canvases-by-caravaggio": "Haskell attributes the described series of canvases to Caravaggio; the works remain untitled and uncounted.",
    "st-chp2-seci-l95-106-caravaggio-household": "The sentence directly says Caravaggio lived in del Monte’s household; this does not identify the household with the separately described official residence.",
    "st-chp2-seci-l95-106-committee-influence": "Haskell says del Monte used his influence on the decorating committee; the committee, not del Monte personally, remains the stated intermediary for the commission.",
    "st-chp2-seci-l95-106-contemporary-art-level": "This is Haskell’s interpretation of Giustiniani’s display arrangement, not a quantified ranking.",
    "st-chp2-seci-l95-106-contrast-fragment": "The unfinished sentence connects Giustiniani’s taste to his actual collection; preserve it as an argument fragment and do not infer the contrast’s conclusion before L108–119.",
    "st-chp2-seci-l95-106-country-house-design": "Haskell says Vincenzo helped design the house; do not upgrade this to sole authorship.",
    "st-chp2-seci-l95-106-country-house-location": "The unnamed country house and Bassano di Sutri are distinct endpoints.",
    "st-chp2-seci-l95-106-cupid-iconography": "The source describes the painting’s iconography but supplies neither title nor artist attribution.",
    "st-chp2-seci-l95-106-cupid-interest-inference": "The endpoints are Giustiniani and del Monte, whose shared interest Haskell infers from the Cupid picture; retain the picture as evidence context and do not infer friendship or Caravaggio authorship.",
    "st-chp2-seci-l95-106-essay-purpose": "Haskell reports that the essay theorized Giustiniani’s eclecticism; the essay itself has not been identified or consulted.",
    "st-chp2-seci-l95-106-followers-employed": "The source says Vincenzo employed some of Caravaggio’s Northern followers; keep the subset unnamed and do not identify individual artists.",
    "st-chp2-seci-l95-106-hopf-publication": "Haskell reports publication in Giornale Linguistico in 1881 and 1882; this does not establish that investigators later located the work.",
    "st-chp2-seci-l95-106-hopf-publication-place": "Genoa is the reported publication place; its index candidate lacks this page and remains for S3 alignment.",
    "st-chp2-seci-l95-106-hopf-relevance": "This is Haskell’s relevance judgment concerning Vincenzo, not an objective assessment of the work’s scholarly value.",
    "st-chp2-seci-l95-106-hopf-untraceable": "Haskell names Dr. Salerno together with unnamed investigators. A collective endpoint preserves the plural subject; the index seed’s full identity remains unresolved, and the report does not prove the work never existed.",
    "st-chp2-seci-l95-106-launched-dangeli": "Haskell says del Monte launched Filippo d’Angeli; the alias Napoletano is retained without expanding identity beyond the source.",
    "st-chp2-seci-l95-106-lighting-comparison": "Retain Haskell’s qualification ‘may well have seemed’; the comparison does not establish direct influence.",
    "st-chp2-seci-l95-106-owner-preference": "Haskell identifies the unidentified Cupid painting as the one that most appealed to its proprietor, Vincenzo.",
    "st-chp2-seci-l95-106-painting-collection-location": "The reported location applies to Giustiniani’s collection as a whole, not every individual painting.",
    "st-chp2-seci-l95-106-palace-near-church": "Haskell locates the palace near S. Luigi dei Francesi. The OCR reading is retained in the quote; the open index sub-entry remains for S3 identity alignment.",
    "st-chp2-seci-l95-106-sacchi-commission": "Del Monte’s influence works through the named committee to obtain Sacchi’s commission; do not say del Monte personally issued it.",
    "st-chp2-seci-l95-106-sacchi-employment": "Haskell reports Sacchi’s employment by del Monte at his casino; the casino and Piazza del Popolo remain distinct place references.",
    "st-chp2-seci-l95-106-sandart-advice": "The source attributes the decision to display the picture behind a curtain to Sandrart’s advice; it does not establish ownership or curtain design.",
    "st-chp2-seci-l95-106-thirteen-displayed": "The room is said to contain a group of thirteen Caravaggio paintings; keep the group aggregated and do not invent individual titles.",
}

ENDPOINT_REVISIONS = {
    "st-chp2-seci-l95-106-cupid-interest-inference": {
        "subject_candidate_id": "cand-1200",
        "object_candidate_id": "cand-1691",
        "predicate": "shared_interest_in_caravaggio_inferred",
        "mentioned_candidate_ids": ["cand-1200", "cand-1691", "cand-4320", "cand-0544"],
    },
    "st-chp2-seci-l95-106-hopf-untraceable": {
        "subject_candidate_id": GROUP_ID,
        "mentioned_candidate_ids": ["cand-4323", GROUP_ID, "cand-4336"],
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"PRECONDITION FAILED: {message}")


def load_jsonl() -> tuple[list[dict], list[str]]:
    lines = STATEMENTS.read_text(encoding="utf-8").splitlines(keepends=True)
    return [json.loads(line) for line in lines], lines


def flag(row: dict):
    return (row.get("qualifiers") or {}).get("relation_candidate")


def bilateral(row: dict) -> bool:
    return bool(row.get("subject_candidate_id") and row.get("object_candidate_id"))


def counts(rows: list[dict]) -> dict[str, int]:
    flags = Counter(flag(row) for row in rows)
    return {
        "statements": len(rows),
        "relation_true": flags[True],
        "relation_false": flags[False],
        "true_bilateral": sum(flag(row) is True and bilateral(row) for row in rows),
        "true_open": sum(flag(row) is True and not bilateral(row) for row in rows),
        "false_bilateral": sum(flag(row) is False and bilateral(row) for row in rows),
        "unclassified_bilateral": sum(flag(row) is None and bilateral(row) for row in rows),
    }


def csv_records(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(path.read_text(encoding="utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader)


def append_csv_bytes(path: Path, fieldnames: list[str], additions: list[dict[str, str]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    for row in additions:
        writer.writerow(row)
    old = path.read_bytes()
    separator = b"" if old.endswith((b"\n", b"\r")) else b"\n"
    return old + separator + stream.getvalue().encode("utf-8")


def atomic_write(path: Path, payload: bytes) -> None:
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        tmp = Path(handle.name)
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def candidate_row() -> dict[str, str]:
    return {
        "candidate_id": GROUP_ID,
        "index_entry_id": "",
        "canonical_name": "Dr. Salerno and other investigators unable to trace Carlo Hopf’s work",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell reports Dr. Salerno together with unnamed other investigators as unable to trace Carlo Hopf’s work on Giustiniani. The membership and organization of this collective are unspecified; the index seed Salerno, L. is not identity-resolved here. The report does not establish that the work never existed. The candidate remains untyped/open and is not a KU.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L105",
    }


def mention_row(start: int, end: int) -> dict[str, str]:
    return {
        "mention_id": GROUP_MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": GROUP_ID,
        "surface_form": GROUP_SURFACE,
        "start_char": str(start),
        "end_char": str(end),
        "note": "Source-defined collective of Dr. Salerno and unnamed other investigators; preserve the plural subject without inferring membership or organization.",
    }


def preflight():
    paths = {
        "book-statements.jsonl": STATEMENTS,
        "entity-candidates.csv": CANDIDATES,
        "mentions.csv": MENTIONS,
        "s2-coverage.csv": COVERAGE,
        "02_CHP-2_sec_i.md": SOURCE,
    }
    for name, expected in EXPECTED_HASHES.items():
        require(paths[name].is_file(), f"missing file {name}")
        require(sha256(paths[name]) == expected, f"unexpected pre-state for {name}")
        require(not paths[name].with_name(paths[name].name + BACKUP_SUFFIX).exists(),
                f"backup already exists for {name}")

    rows, raw_lines = load_jsonl()
    by_id = {row.get("statement_id"): row for row in rows}
    require(len(by_id) == len(rows), "statement IDs are not unique")
    require(set(EXPECTED_ROWS) == set(NOTES), "target and decision-note sets differ")
    require(set(EXPECTED_ROWS) <= set(by_id), "a target statement is missing")
    for statement_id, (subject, object_id, predicate, start, end, anchor) in EXPECTED_ROWS.items():
        row = by_id[statement_id]
        qualifiers = row.get("qualifiers") or {}
        require(row.get("segment_id") == SEGMENT_ID, f"wrong segment for {statement_id}")
        require(row.get("subject_candidate_id") == subject and row.get("object_candidate_id") == object_id,
                f"unexpected endpoints for {statement_id}")
        require(row.get("predicate") == predicate, f"unexpected predicate for {statement_id}")
        require((qualifiers.get("source_line_start"), qualifiers.get("source_line_end")) == (start, end),
                f"unexpected source range for {statement_id}")
        require(flag(row) is None, f"already classified: {statement_id}")
        require(anchor in row.get("original_quote", ""), f"quote anchor missing for {statement_id}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[94:106])
    require(GROUP_SURFACE in segment_text, "group subject source phrase changed")
    group_start = segment_text.index(GROUP_SURFACE)
    all_new_mentions = [
        {
            "mention_id": mention_id,
            "segment_id": SEGMENT_ID,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(segment_text.index(surface)),
            "end_char": str(segment_text.index(surface) + len(surface)),
            "note": note,
        }
        for mention_id, candidate_id, surface, note in MISSING_MENTIONS
    ]
    all_new_mentions.append({
        "mention_id": GROUP_MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": GROUP_ID,
        "surface_form": GROUP_SURFACE,
        "start_char": str(group_start),
        "end_char": str(group_start + len(GROUP_SURFACE)),
        "note": "Source-defined collective of Dr. Salerno and unnamed other investigators; preserve the plural subject without inferring membership or organization.",
    })

    coverage_fields, coverage = csv_records(COVERAGE)
    matches = [row for row in coverage if row.get("segment_id") == SEGMENT_ID]
    require(len(matches) == 1 and matches[0].get("disposition") == "reviewed"
            and matches[0].get("migration_status") == "complete", "coverage is not reviewed/complete")

    candidate_fields, candidates = csv_records(CANDIDATES)
    candidate_ids = {row.get("candidate_id") for row in candidates}
    require(GROUP_ID not in candidate_ids, "candidate ID already exists")
    mention_fields, mentions = csv_records(MENTIONS)
    mention_ids = {row.get("mention_id") for row in mentions}
    require({row["mention_id"] for row in all_new_mentions}.isdisjoint(mention_ids),
            "one or more mention IDs already exist")
    mention_candidates = {row.get("candidate_id") for row in mentions if row.get("segment_id") == SEGMENT_ID}
    missing_endpoints = {
        candidate_id
        for subject, object_id, *_ in EXPECTED_ROWS.values()
        for candidate_id in (subject, object_id)
        if candidate_id not in mention_candidates
    }
    require(missing_endpoints == EXPECTED_MISSING_ENDPOINTS,
            f"unexpected endpoint mention gaps: {sorted(missing_endpoints)}")

    before = counts(rows)
    require(before == {
        "statements": 12700,
        "relation_true": 3972,
        "relation_false": 1814,
        "true_bilateral": 3945,
        "true_open": 27,
        "false_bilateral": 449,
        "unclassified_bilateral": 4103,
    }, "global statement counts changed")
    return rows, raw_lines, before, candidate_fields, mention_fields, group_start, all_new_mentions


def update_rows(rows: list[dict]) -> list[dict]:
    result = []
    for original in rows:
        row = dict(original)
        statement_id = row.get("statement_id")
        if statement_id in NOTES:
            row["qualifiers"] = dict(row.get("qualifiers") or {})
            row["qualifiers"]["relation_candidate"] = True
            row["qualifiers"]["relation_candidate_note"] = NOTES[statement_id]
            if statement_id == "st-chp2-seci-l95-106-cupid-interest-inference":
                for key, value in ENDPOINT_REVISIONS[statement_id].items():
                    if key == "mentioned_candidate_ids":
                        row["qualifiers"][key] = value
                    else:
                        row[key] = value
                row["qualifiers"]["qualification"] = (
                    "Haskell infers shared interest from the Cupid picture and collection context; this is not a "
                    "direct social relationship and does not identify the picture as by Caravaggio."
                )
            elif statement_id == "st-chp2-seci-l95-106-hopf-untraceable":
                for key, value in ENDPOINT_REVISIONS[statement_id].items():
                    if key == "mentioned_candidate_ids":
                        row["qualifiers"][key] = value
                    else:
                        row[key] = value
                row["qualifiers"]["qualification"] = (
                    "Haskell names Dr. Salerno with unnamed other investigators. The index seed Salerno, L. remains "
                    "for S3 identity resolution; this reported inability does not establish that the work never existed."
                )
        result.append(row)
    return result


def serialize_jsonl(raw_lines: list[str], old_rows: list[dict], new_rows: list[dict]) -> bytes:
    require(len(raw_lines) == len(old_rows) == len(new_rows), "JSONL row count changed")
    output = []
    for raw, old, new in zip(raw_lines, old_rows, new_rows):
        if old == new:
            output.append(raw)
            continue
        ending = "\r\n" if raw.endswith("\r\n") else "\n" if raw.endswith("\n") else ""
        output.append(json.dumps(new, ensure_ascii=False, separators=(",", ":")) + ending)
    return "".join(output).encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify chapter 2 section i L95-106 relationship statements.")
    parser.add_argument("--apply", action="store_true", help="apply the preflighted changes")
    args = parser.parse_args()
    rows, raw_lines, before, candidate_fields, mention_fields, group_start, new_mentions = preflight()
    changed = update_rows(rows)
    after = counts(changed)
    candidate_payload = append_csv_bytes(CANDIDATES, candidate_fields, [candidate_row()])
    mention_payload = append_csv_bytes(MENTIONS, mention_fields, new_mentions)
    statement_payload = serialize_jsonl(raw_lines, rows, changed)

    print(f"PREVIEW: {SEGMENT_ID}")
    for statement_id, note in NOTES.items():
        print(f"  {statement_id}: relation_candidate=true — {note}")
    print(f"  correct the shared-interest inference to Giustiniani → del Monte; retain the Cupid picture as evidence context")
    print("  add four missing exact mentions for canvases, room, contemporary-art category, and essay")
    print(f"  add {GROUP_ID} and {GROUP_MENTION_ID} for the joint Salerno/investigators subject")
    print("  no new KU, formal S6 relation, source edit, or statement deletion")
    print("  counts before:", json.dumps(before, sort_keys=True))
    print("  counts after: ", json.dumps(after, sort_keys=True))
    print("  candidates after:", len(csv_records(CANDIDATES)[1]) + 1)
    print("  mentions after:", len(csv_records(MENTIONS)[1]) + len(new_mentions))
    if not args.apply:
        print("DRY RUN ONLY; no files written. Use --apply to apply the changes.")
        return

    targets = [STATEMENTS, CANDIDATES, MENTIONS]
    for path in targets:
        shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
    atomic_write(STATEMENTS, statement_payload)
    atomic_write(CANDIDATES, candidate_payload)
    atomic_write(MENTIONS, mention_payload)
    print("APPLIED")
    for path in targets:
        print(path.relative_to(ROOT), sha256(path))
        print("  backup", path.with_name(path.name + BACKUP_SUFFIX).relative_to(ROOT))
    print("final counts:", json.dumps(counts(load_jsonl()[0]), sort_keys=True))


if __name__ == "__main__":
    main()
