#!/usr/bin/env python3
"""Classify p.472 index entries, repair print locators, and close cited S2 links."""

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
MARKER_SEGMENT = "chp-22:22_CHP-22Index:l3294-3294"
LEFT_SEGMENT = "chp-22:22_CHP-22Index:l3296-3349"
RIGHT_SEGMENT = "chp-22:22_CHP-22Index:l3351-3405"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p472-l3294-3405-20261007"

EXPECTED_HASHES = {
    "02-sources/02-Markdown/22_CHP-22Index.md": "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081",
    "02-sources/01-book/CHP-22Index.pdf": "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    "02-sources/03-Index/03-2-Index-CSV/UVWXYZ.csv": "19a9e5db94a3da83c673a7fa03b003ed501317de161e4664ca572b0f0d6d5e21",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "04-knowledge/tables/entity-candidates.csv": "8dd8a83b79996375e9ae9a0856c8bc91c1263c93bd8b7ca23b01df17b21e02f5",
    "04-knowledge/tables/s2-coverage.csv": "573dead389d1f08f5c04b2bed80404be851f7fa873b428f464ba8f2997a015a8",
    "04-knowledge/tables/book-statements.jsonl": "fe7e32ae9a6fc4d9c3b69b138b9b1534fdc119d3a18613a65d11d76ba3a0921e",
    "02-sources/02-Markdown/05_CHP-5_sec_i.md": "8ef51cd646ed6abf398c9faeb47df9a03f70de696d9a871c6d0b734b2adeeeee",
    "02-sources/02-Markdown/06_CHP-6_sec_i.md": "e1bf27cf13961032d4587a1787a1b89f00a9076cf7a8c9dd4434000e84add42d",
    "02-sources/02-Markdown/07_CHP-7_sec_iv.md": "d620659a2f3567ea9a1d91b7657390e9824768c320c3cf534bd30069d6c72077",
    "02-sources/02-Markdown/13_CHP-13_intro.md": "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8",
}

TYPE_BY_ENTRY = {f"UVWXYZ.csv#{i}": "person" for i in range(5, 100)}
for entity_type, indices in {
    "event": (5, 6, 8, 46),
    "work": (14, 16, 17, 18, 31, 32, 33, 34, 35, 41, 48, 49, 50, 51, 52, 89, 92, 93, 96, 97, 98, 99),
    "place": (11, 40, 55),
    "family": (24,),
    "archive": (54,),
    "term": tuple(i for i in range(56, 86) if i != 67),
}.items():
    for index in indices:
        TYPE_BY_ENTRY[f"UVWXYZ.csv#{index}"] = entity_type

EXPECTED_TYPE_COUNTS = {
    "person": 35,
    "work": 22,
    "term": 29,
    "event": 4,
    "place": 3,
    "family": 1,
    "archive": 1,
}

CORRECTIONS = {
    "cand-2693": {
        "field": "index_page_range",
        "before": "37n",
        "after": "377n",
        "detail": "The CSV has 37n; CHP-22Index.pdf physical p.30 prints 377n. Candidate locator follows print.",
    },
    "cand-2709": {
        "field": "index_page_range",
        "before": "60, 113, 116, 119, 126, 122, 136, 158, 172, 190, 192, 385, 400",
        "after": "60, 113, 116, 119, 126, 133, 136, 138, 172, 190, 192, 384, 400",
        "detail": "UVWXYZ.csv has 122, 158 and 385; the p.472 scan and S0 transcription read 133, 138 and 384. Candidate locators follow print.",
    },
    "cand-2718": {
        "field": "index_page_range",
        "before": "252n",
        "after": "335n",
        "detail": "The CSV says 252n and S0 OCR reads 3^5n; p.472 print and chapter 13 p.335 n.2 confirm 335n. The full-title body candidate cand-9993 remains a separate S3 alignment lead.",
    },
    "cand-2755": {
        "field": "index_page_range",
        "before": "160, 178, 207, 216, 231, 232, 241, 246, 248, 262, 279n, 283, 340, 348, 353, 354, 355, 359, 373",
        "after": "160, 178, 207, 216, 231, 232, 241, 246, 248, 262, 279, 283, 340, 348, 353, 354, 356, 359, 373",
        "detail": "UVWXYZ.csv has 279n and 355; the p.472 print reads 279 and 356. Candidate locators follow print.",
    },
}

DETAIL_UPDATES = {
    "cand-2705": "Index subentry identifies the Scala Regia as a work within the Vatican palace; body candidate cand-6309 records Bernini's design and remains separate for S3 alignment.",
    "cand-2711": "Index subentry is a Velasquez person-context, not an institution. Chapter 5 p.126 names both member institutions; its two endpoint-specific statements are preserved, while this index lead remains separate for S3.",
    "cand-2731": "The subentry describes unnamed foreign patrons as a group; it does not identify individuals or establish formal patronage edges.",
    "cand-2762": "Index shorthand points to Verrio's A Sea triumph (body candidate cand-7206, pp.195-196); keep this index lead separate for S3 alignment.",
    "cand-2763": "Index shorthand points to the unidentified allegorical fresco at Hampton Court (body candidate cand-7213, p.196); keep this index lead separate for S3 alignment.",
}

COVERAGE_NOTES = {
    MARKER_SEGMENT: (
        "no_semantic_content: S0 L3294 [Page 472] is a generated navigation marker, confirmed on "
        "CHP-22Index.pdf physical p.30; it is not an indexed object or factual claim."
    ),
    LEFT_SEGMENT: (
        "no_semantic_content: index-navigation-only. Index-seed classification only. CHP-22Index.pdf "
        "physical p.30 prints p.472. The segment contains "
        "UVWXYZ.csv#4-52 (49 rows): #4 Urban VIII is the already excluded see-under cross-reference; the other "
        "48 candidates are 26 person, 15 work, 4 event, 2 place and 1 family. Political devolution of Urbino, "
        "the Papal takeover of pictures and the Utrecht Treaty are event contexts. Named artworks and the "
        "McSwiny monument entries are work candidates; the Vatican palace remains a place while its Scala "
        "Regia is a work per the p.151 body statement. Velasquez's actions and memberships remain person/event "
        "contexts, not new relations inferred from the index."
    ),
    RIGHT_SEGMENT: (
        "no_semantic_content: index-navigation-only. Index-seed classification only. CHP-22Index.pdf "
        "physical p.30 prints p.472. The segment contains "
        "UVWXYZ.csv#53-99 (47 rows): 9 person, 7 work, 29 term, 1 place and 1 archive. Venice is the city "
        "(place); its historiographic and social themes are terms, while foreign patrons remain an unnamed "
        "person-group context. Padre Antonio da Venezia is a person and La Chiesa di Gesu Cristo vendicata an "
        "archive. Specific Verrio work contexts follow the separately described Sea triumph and Hampton Court "
        "fresco candidates. Four printed locator errors were corrected on candidates cand-2693, cand-2709, "
        "cand-2718 and cand-2755; the index CSV and S0 source remain unchanged. Relationship references were "
        "reconciled to existing body statements; no formal relation edge was added."
    ),
}

STATEMENT_EXPECTATIONS = {
    "st-chp5-p126-velasquez-memberships": ("cand-2709", "cand-0821", "institution_membership_reported"),
    "st-chp5-p126-velasquez-innocent-portrait": ("cand-2709", "cand-6035", "portrait_commission_reported"),
    "st-chp5-p126-velasquez-pareja-1650": ("cand-2709", "cand-6034", "portrait_shown_at_exhibition_reported"),
    "st-chp6-p151-bernini-designs-scala-regia": ("cand-0312", "cand-6309", "designs-scala-regia"),
    "st-chp7-p195-verrio-brought-by-ambassador": ("cand-7203", "cand-2759", "brought_verrio_over_to_england"),
    "st-chp7-p195-verrio-employed-by-charlesii": ("cand-0656", "cand-2759", "employed_verrio_with_little_discrimination"),
    "st-chp7-p195-sea-triumph-open": ("cand-2759", "cand-7206", "earliest_royal_picture_description_continues"),
    "st-chp7-p196-sea-triumph-description": ("cand-7206", "cand-0656", "depicted_king_in_flattering_but_politically_irrelevant_picture"),
    "st-chp7-p196-hampton_fresco_subject": ("cand-7213", "cand-2814", "depicted_williamiii_victory_over_france_led_catholic_powers"),
    "st-chp7-p196-verrio-windsor-fresco-series": ("cand-2759", "cand-7208", "employed_on_fresco_series_at"),
    "st-chp7-p196-verrio_career_alignment": ("cand-2759", None, "served_louisxiv_and_his_greatest_enemy_williamiii"),
    "st-chp7-p196-verrio_hampton_court_employment": ("cand-2759", "cand-7212", "employed_by_new_regime_at_hampton_court"),
    "st-chp7-p198-exeter-employs-verrio-burghley": ("cand-0984", "cand-2759", "employed_to_paint_ceiling_frescoes_at"),
}

NEW_STATEMENT_IDS = {
    "st-chp5-p126-velasquez-membership-accademia",
    "st-chp7-p196-verrio-served-williamiii",
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    return raw.startswith(b"\xef\xbb\xbf"), "\r\n" if "\r\n" in text else "\n", list(csv.DictReader(io.StringIO(text, newline="")))


def write_csv(path, rows, bom, line_ending):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator=line_ending)
    writer.writeheader()
    writer.writerows(rows)
    payload = output.getvalue().encode("utf-8")
    if bom:
        payload = b"\xef\xbb\xbf" + payload
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(payload)
    os.replace(temporary, path)


def read_jsonl(path):
    raw = path.read_bytes()
    return raw.startswith(b"\xef\xbb\xbf"), raw.decode("utf-8-sig").splitlines(keepends=True)


def write_jsonl(path, lines, bom):
    payload = "".join(lines).encode("utf-8")
    if bom:
        payload = b"\xef\xbb\xbf" + payload
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(payload)
    os.replace(temporary, path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Write the guarded migration; default is dry-run.")
    args = parser.parse_args()

    for relative, expected in EXPECTED_HASHES.items():
        path = ROOT / relative
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"preflight hash mismatch: {relative}")

    source_path = ROOT / "02-sources/02-Markdown/22_CHP-22Index.md"
    manifest = [
        json.loads(line)
        for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    segment_by_id = {row["segment_id"]: row for row in manifest}
    expected_segment_hashes = {
        MARKER_SEGMENT: "e4efda574d8949a5ff0b48f413e83b74811cf39f11e19c9706f238fe9345fb0b",
        LEFT_SEGMENT: "90f04015f35072b872427aa6c9e1539e0b83778092c4d99bb69a5dd1a8590b95",
        RIGHT_SEGMENT: "86a6168a8e058f03ddbd4ade29e9c8e4d25d65fa8cc665430f27902f0e02068e",
    }
    source_lines = source_path.read_text(encoding="utf-8-sig").splitlines()
    for segment_id, expected in expected_segment_hashes.items():
        segment = segment_by_id.get(segment_id)
        if not segment or segment["sha256"] != expected:
            raise SystemExit(f"segment manifest changed: {segment_id}")
        text = "\n".join(source_lines[segment["line_start"] - 1 : segment["line_end"]])
        if hashlib.sha256(text.encode("utf-8")).hexdigest() != expected:
            raise SystemExit(f"segment source text changed: {segment_id}")

    candidate_path = TABLES / "entity-candidates.csv"
    coverage_path = TABLES / "s2-coverage.csv"
    statement_path = TABLES / "book-statements.jsonl"
    candidate_bom, candidate_eol, candidates = read_csv(candidate_path)
    coverage_bom, coverage_eol, coverage = read_csv(coverage_path)
    statement_bom, statement_lines = read_jsonl(statement_path)
    candidate_by_entry = {row["index_entry_id"]: row for row in candidates if row["index_entry_id"]}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}

    if len(TYPE_BY_ENTRY) != 95 or Counter(TYPE_BY_ENTRY.values()) != Counter(EXPECTED_TYPE_COUNTS):
        raise SystemExit("the p.472 classification map is incomplete or its type totals changed")
    urban = candidate_by_entry.get("UVWXYZ.csv#4")
    if not urban or urban["canonical_name"] != "Urban VIII" or urban["status"] != "excluded":
        raise SystemExit("the Urban VIII see-under row is no longer the excluded cross-reference")
    for entry_id in TYPE_BY_ENTRY:
        candidate = candidate_by_entry.get(entry_id)
        if not candidate or candidate["status"] != "open" or candidate["suggested_type"]:
            raise SystemExit(f"unexpected or missing p.472 candidate: {entry_id}")

    correction_summary = []
    for candidate_id, correction in CORRECTIONS.items():
        row = candidate_by_id.get(candidate_id)
        if not row or row[correction["field"]] != correction["before"]:
            raise SystemExit(f"unexpected pre-correction candidate: {candidate_id}")
        if row["detail"]:
            raise SystemExit(f"candidate detail already populated: {candidate_id}")
        row[correction["field"]] = correction["after"]
        row["detail"] = correction["detail"]
        correction_summary.append({
            "candidate_id": candidate_id,
            "field": correction["field"],
            "before": correction["before"],
            "after": correction["after"],
        })

    for candidate_id, detail in DETAIL_UPDATES.items():
        row = candidate_by_id.get(candidate_id)
        if not row or row["detail"]:
            raise SystemExit(f"unexpected candidate detail prestate: {candidate_id}")
        row["detail"] = detail

    for entry_id, entity_type in TYPE_BY_ENTRY.items():
        candidate_by_entry[entry_id]["suggested_type"] = entity_type

    coverage_by_id = {row["segment_id"]: row for row in coverage}
    for segment_id, disposition, line_range in (
        (MARKER_SEGMENT, "excluded", "L3294-3294"),
        (LEFT_SEGMENT, "reviewed", "L3296-3349"),
        (RIGHT_SEGMENT, "reviewed", "L3351-3405"),
    ):
        row = coverage_by_id.get(segment_id)
        if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"], row["note"]) != (
            "queued", "pending", "", "",
        ):
            raise SystemExit(f"p.472 coverage is not queued/pending: {segment_id}")
        row.update({
            "disposition": disposition,
            "migration_status": "complete",
            "source_line_ranges": line_range,
            "note": COVERAGE_NOTES[segment_id],
        })

    parsed = {}
    for line in statement_lines:
        body = line.rstrip("\r\n")
        if body.strip():
            record = json.loads(body)
            parsed[record.get("statement_id")] = record
    if NEW_STATEMENT_IDS & set(parsed):
        raise SystemExit("a planned statement ID already exists")
    for statement_id, expected in STATEMENT_EXPECTATIONS.items():
        row = parsed.get(statement_id)
        if not row or (row.get("subject_candidate_id"), row.get("object_candidate_id"), row.get("predicate")) != expected:
            raise SystemExit(f"statement identity changed or missing: {statement_id}")
        if row.get("qualifiers", {}).get("relation_candidate") is not None:
            raise SystemExit(f"unexpected relation-candidate prestate: {statement_id}")
    if set(STATEMENT_EXPECTATIONS) - set(parsed):
        raise SystemExit("one or more required relation-candidate statements are absent")

    statement_updates = []
    statement_additions = []
    rewritten_lines = []
    for line in statement_lines:
        newline = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
        body = line.rstrip("\r\n")
        if not body.strip():
            rewritten_lines.append(line)
            continue
        row = json.loads(body)
        statement_id = row.get("statement_id")
        qualifiers = row.get("qualifiers", {})
        if statement_id == "st-chp5-p126-velasquez-memberships":
            if row["segment_id"] != "chp-5:05_CHP-5_sec_i:l60-74" or qualifiers.get("source_line_start") != 67:
                raise SystemExit("Velasquez membership anchor changed")
            row["qualifiers"]["claim"] = "Haskell says Velasquez belonged to the Congregazione dei Virtuosi."
            row["qualifiers"]["qualification"] = (
                "This row isolates the Congregazione membership; the Accademia di S. Luca membership is "
                "captured in st-chp5-p126-velasquez-membership-accademia. Index lead cand-2711 remains "
                "separate for S3 alignment."
            )
            row["qualifiers"]["relation_candidate"] = True
            new_row = json.loads(json.dumps(row, ensure_ascii=False))
            new_row["statement_id"] = "st-chp5-p126-velasquez-membership-accademia"
            new_row["object_candidate_id"] = "cand-0007"
            new_row["qualifiers"]["claim"] = "Haskell says Velasquez belonged to the Accademia di S. Luca."
            new_row["qualifiers"]["qualification"] = (
                "This row isolates the Accademia membership; the Congregazione membership is captured in "
                "st-chp5-p126-velasquez-memberships. Index lead cand-2711 remains separate for S3 alignment."
            )
            statement_additions.append(new_row["statement_id"])
            rewritten_lines.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + newline)
            rewritten_lines.append(json.dumps(new_row, ensure_ascii=False, separators=(",", ":")) + newline)
            statement_updates.append(statement_id)
            continue

        if statement_id == "st-chp7-p196-verrio_career_alignment":
            if row.get("object_candidate_id") is not None or row["segment_id"] != "chp-7:07_CHP-7_sec_iv:l48-61":
                raise SystemExit("Verrio service statement anchor or endpoint changed")
            row["object_candidate_id"] = "cand-1447"
            row["predicate"] = "put_art_at_service_of_monarch"
            row["qualifiers"]["claim"] = "Haskell says Verrio put his art at the service of Louis XIV."
            row["qualifiers"]["qualification"] = (
                "This row isolates the Louis XIV endpoint from the two-monarch sentence; 'greatest enemy' "
                "is Haskell's characterization, and no date or specific commission is given."
            )
            row["qualifiers"]["relation_candidate"] = True
            new_row = json.loads(json.dumps(row, ensure_ascii=False))
            new_row["statement_id"] = "st-chp7-p196-verrio-served-williamiii"
            new_row["object_candidate_id"] = "cand-2814"
            new_row["qualifiers"]["claim"] = (
                "Haskell says Verrio put his art at the service of William III, whom he calls Louis XIV's greatest enemy."
            )
            new_row["qualifiers"]["qualification"] = (
                "This row isolates the William III endpoint from the two-monarch sentence; 'greatest enemy' "
                "is Haskell's characterization, and no date or specific commission is given."
            )
            statement_additions.append(new_row["statement_id"])
            rewritten_lines.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + newline)
            rewritten_lines.append(json.dumps(new_row, ensure_ascii=False, separators=(",", ":")) + newline)
            statement_updates.append(statement_id)
            continue

        if statement_id in STATEMENT_EXPECTATIONS:
            qualifiers["relation_candidate"] = True
            statement_updates.append(statement_id)
        rewritten_lines.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + newline)

    if set(statement_updates) != set(STATEMENT_EXPECTATIONS):
        raise SystemExit("one or more relation-candidate statements were not updated")
    if set(statement_additions) != NEW_STATEMENT_IDS:
        raise SystemExit("one or more endpoint-specific relation statements were not created")

    type_counts = dict(sorted(Counter(TYPE_BY_ENTRY.values()).items()))
    summary = {
        "segments": {
            MARKER_SEGMENT: "excluded/complete",
            LEFT_SEGMENT: "reviewed/complete",
            RIGHT_SEGMENT: "reviewed/complete",
        },
        "classified_candidates": len(TYPE_BY_ENTRY),
        "excluded_cross_reference": "UVWXYZ.csv#4 Urban VIII -> Barberini, Maffeo",
        "classified_types": type_counts,
        "candidate_corrections": correction_summary,
        "candidate_context_updates": len(DETAIL_UPDATES),
        "relation_candidate_statements_marked": len(statement_updates) + len(statement_additions),
        "new_endpoint_specific_statements": statement_additions,
        "mentions_added": False,
        "formal_relations_added": False,
        "apply": args.apply,
    }

    if args.apply:
        backup_paths = [
            candidate_path.with_name(candidate_path.name + BACKUP_SUFFIX),
            coverage_path.with_name(coverage_path.name + BACKUP_SUFFIX),
            statement_path.with_name(statement_path.name + BACKUP_SUFFIX),
        ]
        if any(path.exists() for path in backup_paths):
            raise SystemExit("a backup with this task suffix already exists")
        for original, backup in zip((candidate_path, coverage_path, statement_path), backup_paths):
            shutil.copy2(original, backup)
        write_csv(candidate_path, candidates, candidate_bom, candidate_eol)
        write_csv(coverage_path, coverage, coverage_bom, coverage_eol)
        write_jsonl(statement_path, rewritten_lines, statement_bom)
        summary["backups"] = [str(path.relative_to(ROOT)) for path in backup_paths]

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
