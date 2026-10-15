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
SEGMENT_ID = "chp-2:02_CHP-2_sec_i:l82-93"
BACKUP_SUFFIX = ".bak-s2-chp2-sec-i-l82-93-20261010"

EXPECTED_HASHES = {
    "book-statements.jsonl": "d1e2adc02bd5ae5c5feb3a3bdeff9b729500ef10fed2451fe7541ebee03cd5c0",
    "entity-candidates.csv": "b214ec44c825690db146c4efdcb96e1de4acbbc5d682104ec0c35535d53b2dae",
    "mentions.csv": "e6179e8cf85a5313d16bad9b24a2d7a529b6d368a39ff6339270181f084888ad",
    "s2-coverage.csv": "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    "02_CHP-2_sec_i.md": "5eca92acb03fe9934be85c82a6ec6806d3c564002955e99bd317916f3c7c8dc6",
}

JOINT_GROUP_ID = "cand-11578"
SOCIETY_GROUP_ID = "cand-11579"
JOINT_GROUP_MENTION_ID = "m-chp2-seci-l82-93-0053"
SOCIETY_GROUP_MENTION_ID = "m-chp2-seci-l82-93-0054"
JOINT_GROUP_SURFACE = "The new Pope and his vigorous young nephew Ludovico\nLudovisi"
SOCIETY_GROUP_SURFACE = "the most hedonistic society that Rome had known since the Renaissance"

# Each entry fixes the pre-edit endpoints, predicate, source lines, and a source-text anchor.
EXPECTED_ROWS = {
    "st-chp2-seci-l82-93-agucchi-guidance-principle": ("cand-0018", "cand-4304", "patronage_theory_reported", 87, 87, "guided by men ‘of enlightened knowledge’"),
    "st-chp2-seci-l82-93-agucchi-ideal": ("cand-0018", "cand-4299", "artistic_ideal_reported", 88, 88, "aim at an ideal"),
    "st-chp2-seci-l82-93-agucchi-office": ("cand-0018", "cand-4294", "held_office_reported", 87, 87, "Holding the influential post of Secretary of State"),
    "st-chp2-seci-l82-93-agucchi-power-window": ("cand-0018", "cand-4296", "political_opportunity_reported", 89, 89, "two brief years to assert these views"),
    "st-chp2-seci-l82-93-agucchi-rejects-imitation": ("cand-0018", "cand-4298", "rejected_view_reported", 87, 88, "views attributed to Caravaggio and his followers"),
    "st-chp2-seci-l82-93-agucchi-theory-development": ("cand-0018", "cand-4296", "developed_theory_reported", 87, 87, "sketched out a theory of art"),
    "st-chp2-seci-l82-93-agucchi-watched-carracci": ("cand-0018", "cand-0576", "observed_artist_at_work_reported", 87, 87, "watched Annibale Carracci at work"),
    "st-chp2-seci-l82-93-aurora-creator": ("cand-4290", "cand-2124", "created_by_reported", 83, 83, "who painted his fresco of Aurora"),
    "st-chp2-seci-l82-93-aurora-venue": ("cand-4290", "cand-4291", "located_at_reported", 83, 83, "for one of the Cardinal’s casini"),
    "st-chp2-seci-l82-93-bernini-commission": ("cand-0394", "cand-0295", "commissioned_from_reported", 83, 83, "to Bernini and to innumerable other artists"),
    "st-chp2-seci-l82-93-del-monte-representative": ("cand-1691", "cand-4302", "represented_person_reported", 92, 93, "representative of the Grand\nDuke of Tuscany"),
    "st-chp2-seci-l82-93-del-monte-residence": ("cand-1691", "cand-4303", "resided_at_reported", 92, 93, "splendid official residence behind the Piazza Navona"),
    "st-chp2-seci-l82-93-domenichino-pupil": ("cand-0932", "cand-0576", "pupil_of_reported", 87, 87, "young pupil Domenichino"),
    "st-chp2-seci-l82-93-domenichino-supremacy": ("cand-1456", "cand-0932", "patronage_preeminence_reported", 86, 87, JOINT_GROUP_SURFACE),
    "st-chp2-seci-l82-93-guercino-supremacy": ("cand-1456", "cand-1258", "patronage_preeminence_reported", 86, 87, "Bolognese compatriots Domenichino and Guercino complete supremacy"),
    "st-chp2-seci-l82-93-paul-v-succession": ("cand-1455", "cand-0393", "succeeded_reported", 84, 85, "after a short conclave was succeeded by the old and ill\nGregory XV"),
    "st-chp2-seci-l82-93-reni-commission": ("cand-0394", "cand-2124", "commissioned_from_reported", 83, 83, "Scipione’s actual commissions to Guido Reni"),
    "st-chp2-seci-l82-93-villa-social-setting": ("cand-4289", "cand-3126", "historical_characterization", 83, 83, SOCIETY_GROUP_SURFACE),
}

NOTES = {
    "st-chp2-seci-l82-93-agucchi-guidance-principle": "The passage attributes this patronage principle to Agucchi. The endpoint is his reported view, not a documented social tie to particular princes.",
    "st-chp2-seci-l82-93-agucchi-ideal": "Haskell reports Agucchi’s artistic ideal and names its exemplars; the claim does not identify unnamed ancient artists or protégés.",
    "st-chp2-seci-l82-93-agucchi-office": "The source explicitly says Agucchi held the Secretary of State office; it does not identify an appointing authority or tenure.",
    "st-chp2-seci-l82-93-agucchi-power-window": "The pronoun ‘these views’ refers to Agucchi’s theory. Preserve the reported two-year window without inferring calendar dates.",
    "st-chp2-seci-l82-93-agucchi-rejects-imitation": "The passage says Agucchi rejected a view attributed to Caravaggio and his followers; it does not establish a direct statement by Caravaggio.",
    "st-chp2-seci-l82-93-agucchi-theory-development": "Haskell directly links Agucchi’s theory to his contacts, reading, temperament, and retirement period; retain the stated 1607–1615 range.",
    "st-chp2-seci-l82-93-agucchi-watched-carracci": "Haskell says Agucchi watched Annibale Carracci at work in the Farnese palace; the palace candidate’s identity remains provisional.",
    "st-chp2-seci-l82-93-aurora-creator": "The source identifies Guido Reni as the painter of the Aurora fresco; its specific identity, date, and casino remain unspecified.",
    "st-chp2-seci-l82-93-aurora-venue": "The source places the fresco in one of the Cardinal’s casinos but does not identify which casino.",
    "st-chp2-seci-l82-93-bernini-commission": "Bernini is explicitly included among Scipione’s actual commissions; the individual work is not identified.",
    "st-chp2-seci-l82-93-del-monte-representative": "Haskell calls del Monte representative of the Grand Duke of Tuscany; the title-holder’s identity is not supplied here.",
    "st-chp2-seci-l82-93-del-monte-residence": "Haskell reports del Monte lived in the residence behind Piazza Navona; the residence itself is not individually identified.",
    "st-chp2-seci-l82-93-domenichino-pupil": "The sentence directly identifies Domenichino as Annibale Carracci’s pupil; ‘his’ refers to Carracci.",
    "st-chp2-seci-l82-93-domenichino-supremacy": "The source gives Gregory XV and Ludovico Ludovisi as joint actors. A source-defined collective endpoint preserves that joint subject without attributing separate action to either person.",
    "st-chp2-seci-l82-93-guercino-supremacy": "The source gives Gregory XV and Ludovico Ludovisi as joint actors. A source-defined collective endpoint preserves that joint subject without attributing separate action to either person.",
    "st-chp2-seci-l82-93-paul-v-succession": "Haskell reports Gregory XV succeeded Paul V after a short conclave; no exact duration is inferred.",
    "st-chp2-seci-l82-93-reni-commission": "The passage explicitly includes Guido Reni among Scipione’s actual commissions and gives the Aurora fresco as an example.",
    "st-chp2-seci-l82-93-villa-social-setting": "Haskell calls the villa the centre of this unnamed social collective. Rome is its geographic setting, not the relational object; the author’s superlative remains an evaluation.",
}

ENDPOINT_REVISIONS = {
    "st-chp2-seci-l82-93-domenichino-supremacy": ("subject_candidate_id", JOINT_GROUP_ID),
    "st-chp2-seci-l82-93-guercino-supremacy": ("subject_candidate_id", JOINT_GROUP_ID),
    "st-chp2-seci-l82-93-villa-social-setting": ("object_candidate_id", SOCIETY_GROUP_ID),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"PRECONDITION FAILED: {message}")


def load_jsonl() -> tuple[list[dict], list[str]]:
    lines = STATEMENTS.read_text(encoding="utf-8").splitlines(keepends=True)
    rows = [json.loads(line) for line in lines]
    return rows, lines


def relation_flag(row: dict):
    return (row.get("qualifiers") or {}).get("relation_candidate")


def is_bilateral(row: dict) -> bool:
    return bool(row.get("subject_candidate_id") and row.get("object_candidate_id"))


def counts(rows: list[dict]) -> dict[str, int]:
    flags = Counter(relation_flag(row) for row in rows)
    return {
        "statements": len(rows),
        "relation_true": flags[True],
        "relation_false": flags[False],
        "true_bilateral": sum(relation_flag(row) is True and is_bilateral(row) for row in rows),
        "true_open": sum(relation_flag(row) is True and not is_bilateral(row) for row in rows),
        "false_bilateral": sum(relation_flag(row) is False and is_bilateral(row) for row in rows),
        "unclassified_bilateral": sum(relation_flag(row) is None and is_bilateral(row) for row in rows),
    }


def csv_records(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    text = path.read_text(encoding="utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return list(reader.fieldnames or []), list(reader)


def csv_append_bytes(path: Path, fieldnames: list[str], additions: list[dict[str, str]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    for row in additions:
        writer.writerow(row)
    old = path.read_bytes()
    separator = b"" if old.endswith((b"\n", b"\r")) else b"\n"
    return old + separator + stream.getvalue().encode("utf-8")


def candidate_row(candidate_id: str, name: str, detail: str, source_ref: str) -> dict[str, str]:
    return {
        "candidate_id": candidate_id,
        "index_entry_id": "",
        "canonical_name": name,
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": detail,
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": source_ref,
    }


def mention_row(mention_id: str, candidate_id: str, surface: str, start: int, end: int, note: str) -> dict[str, str]:
    return {
        "mention_id": mention_id,
        "segment_id": SEGMENT_ID,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
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
    require(set(EXPECTED_ROWS) == set(NOTES), "classification target and note sets differ")
    require(set(EXPECTED_ROWS) <= set(by_id), "a target statement is missing")
    for statement_id, (subject, object_id, predicate, start, end, anchor) in EXPECTED_ROWS.items():
        row = by_id[statement_id]
        qualifiers = row.get("qualifiers") or {}
        require(row.get("segment_id") == SEGMENT_ID, f"wrong segment for {statement_id}")
        require(row.get("subject_candidate_id") == subject and row.get("object_candidate_id") == object_id,
                f"unexpected endpoint for {statement_id}")
        require(row.get("predicate") == predicate, f"unexpected predicate for {statement_id}")
        require((qualifiers.get("source_line_start"), qualifiers.get("source_line_end")) == (start, end),
                f"unexpected source lines for {statement_id}")
        require(relation_flag(row) is None, f"already classified: {statement_id}")
        require(anchor in row.get("original_quote", ""), f"quote anchor missing for {statement_id}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[81:93])
    require(JOINT_GROUP_SURFACE in segment_text, "joint-actor source phrase changed")
    require(SOCIETY_GROUP_SURFACE in segment_text, "society source phrase changed")
    joint_start = segment_text.index(JOINT_GROUP_SURFACE)
    society_start = segment_text.index(SOCIETY_GROUP_SURFACE)

    coverage_fields, coverage = csv_records(COVERAGE)
    matching_coverage = [row for row in coverage if row.get("segment_id") == SEGMENT_ID]
    require(len(matching_coverage) == 1 and matching_coverage[0].get("disposition") == "reviewed"
            and matching_coverage[0].get("migration_status") == "complete", "coverage is not reviewed/complete")

    candidate_fields, candidates = csv_records(CANDIDATES)
    candidate_ids = {row.get("candidate_id") for row in candidates}
    require(JOINT_GROUP_ID not in candidate_ids and SOCIETY_GROUP_ID not in candidate_ids,
            "a proposed candidate ID already exists")
    require(not any(row.get("canonical_name") == "Gregory XV and Ludovico Ludovisi acting jointly in patronage"
                    for row in candidates), "the proposed joint-actor candidate already exists")

    mention_fields, mentions = csv_records(MENTIONS)
    mention_ids = {row.get("mention_id") for row in mentions}
    require(JOINT_GROUP_MENTION_ID not in mention_ids and SOCIETY_GROUP_MENTION_ID not in mention_ids,
            "a proposed mention ID already exists")
    segment_candidates = {row.get("candidate_id") for row in mentions if row.get("segment_id") == SEGMENT_ID}
    for subject, object_id, *_ in EXPECTED_ROWS.values():
        require(subject in segment_candidates and object_id in segment_candidates,
                f"an existing endpoint mention is missing: {subject}, {object_id}")

    before = counts(rows)
    require(before == {
        "statements": 12700,
        "relation_true": 3954,
        "relation_false": 1814,
        "true_bilateral": 3927,
        "true_open": 27,
        "false_bilateral": 449,
        "unclassified_bilateral": 4121,
    }, "current global statement totals changed")

    new_candidates = [
        candidate_row(
            JOINT_GROUP_ID,
            "Gregory XV and Ludovico Ludovisi acting jointly in patronage",
            "Source-defined, passage-specific collective of Gregory XV (cand-1455) and Ludovico Ludovisi (cand-1456), jointly described as monopolizing the finest talents and giving their Bolognese compatriots complete supremacy. No separate agency is assigned to either person; this is not a named organization and remains untyped/open. No KU is created.",
            f"{SEGMENT_ID}#L86",
        ),
        candidate_row(
            SOCIETY_GROUP_ID,
            "Unnamed social collective centered on Scipione Borghese’s Pincio villa",
            "Haskell calls Scipione’s villa the centre of the most hedonistic society Rome had known since the Renaissance. The phrase denotes an unnamed social collective; no membership, organization, or boundaries are given. It remains untyped/open, and Rome is the geographic setting rather than the collective.",
            f"{SEGMENT_ID}#L83",
        ),
    ]
    new_mentions = [
        mention_row(
            JOINT_GROUP_MENTION_ID,
            JOINT_GROUP_ID,
            JOINT_GROUP_SURFACE,
            joint_start,
            joint_start + len(JOINT_GROUP_SURFACE),
            "The coordinated source subject Gregory XV and nephew Ludovico Ludovisi; preserve the line break.",
        ),
        mention_row(
            SOCIETY_GROUP_MENTION_ID,
            SOCIETY_GROUP_ID,
            SOCIETY_GROUP_SURFACE,
            society_start,
            society_start + len(SOCIETY_GROUP_SURFACE),
            "The unnamed social collective described as centered on Scipione Borghese’s villa; membership is not given.",
        ),
    ]
    return rows, raw_lines, by_id, before, candidate_fields, new_candidates, mention_fields, new_mentions


def updated_rows(rows: list[dict], by_id: dict) -> list[dict]:
    result = []
    for original in rows:
        row = dict(original)
        statement_id = row.get("statement_id")
        if statement_id in NOTES:
            row["qualifiers"] = dict(row.get("qualifiers") or {})
            row["qualifiers"]["relation_candidate"] = True
            row["qualifiers"]["relation_candidate_note"] = NOTES[statement_id]
            if statement_id in ENDPOINT_REVISIONS:
                field, value = ENDPOINT_REVISIONS[statement_id]
                row[field] = value
            if statement_id in {
                "st-chp2-seci-l82-93-domenichino-supremacy",
                "st-chp2-seci-l82-93-guercino-supremacy",
            }:
                row["qualifiers"]["qualification"] = (
                    "The source gives Gregory XV and Ludovico Ludovisi as joint actors; the collective endpoint "
                    "preserves this shared subject without asserting that either acted alone."
                )
                row["qualifiers"]["mentioned_candidate_ids"] = [
                    "cand-1455", "cand-1456", JOINT_GROUP_ID, row["object_candidate_id"]
                ]
            if statement_id == "st-chp2-seci-l82-93-villa-social-setting":
                row["qualifiers"]["qualification"] = (
                    "Haskell’s superlative is authorial evaluation. Rome locates the society; the object endpoint "
                    "is the unnamed social collective. Its members, organizational status, and boundaries are unspecified."
                )
                row["qualifiers"]["mentioned_candidate_ids"] = [
                    "cand-4289", SOCIETY_GROUP_ID, "cand-3126"
                ]
        result.append(row)
    return result


def serialize_jsonl(original_lines: list[str], before_rows: list[dict], after_rows: list[dict]) -> bytes:
    require(len(original_lines) == len(before_rows) == len(after_rows), "JSONL row count changed")
    out = []
    for raw, old, new in zip(original_lines, before_rows, after_rows):
        if old == new:
            out.append(raw)
            continue
        ending = "\r\n" if raw.endswith("\r\n") else "\n" if raw.endswith("\n") else ""
        out.append(json.dumps(new, ensure_ascii=False, separators=(",", ":")) + ending)
    return "".join(out).encode("utf-8")


def atomic_write(path: Path, payload: bytes) -> None:
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        tmp = Path(handle.name)
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify chapter 2 section i L82-93 relationship statements.")
    parser.add_argument("--apply", action="store_true", help="apply the preflighted changes")
    args = parser.parse_args()
    rows, raw_lines, by_id, before, candidate_fields, new_candidates, mention_fields, new_mentions = preflight()
    changed = updated_rows(rows, by_id)
    after = counts(changed)
    candidate_payload = csv_append_bytes(CANDIDATES, candidate_fields, new_candidates)
    mention_payload = csv_append_bytes(MENTIONS, mention_fields, new_mentions)
    statement_payload = serialize_jsonl(raw_lines, rows, changed)

    print(f"PREVIEW: {SEGMENT_ID}")
    for statement_id, note in NOTES.items():
        print(f"  {statement_id}: relation_candidate=true — {note}")
    print(f"  add {JOINT_GROUP_ID} and {SOCIETY_GROUP_ID}: two source-defined, untyped/open group candidates")
    print(f"  add {JOINT_GROUP_MENTION_ID} and {SOCIETY_GROUP_MENTION_ID}: exact source spans")
    print("  correct two joint-patron subjects to their collective candidate")
    print("  correct villa social-setting object from geographic Rome to the unnamed social collective")
    print("  no new KU, formal S6 relation, source edit, or statement deletion")
    print("  counts before:", json.dumps(before, sort_keys=True))
    print("  counts after: ", json.dumps(after, sort_keys=True))
    print("  candidate rows after:", len(csv_records(CANDIDATES)[1]) + len(new_candidates))
    print("  mention rows after:", len(csv_records(MENTIONS)[1]) + len(new_mentions))
    if not args.apply:
        print("DRY RUN ONLY; no files written. Use --apply to apply the changes.")
        return

    targets = [STATEMENTS, CANDIDATES, MENTIONS]
    for path in targets:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        require(not backup.exists(), f"backup already exists: {backup.name}")
        shutil.copy2(path, backup)
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
