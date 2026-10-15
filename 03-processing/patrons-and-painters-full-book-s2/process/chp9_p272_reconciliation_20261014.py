"""Recover omitted p.272 S2 mentions and classify its open claims.

The legacy migration files are parsed as literal specifications only. This
reconciliation is pinned to the current source and table state and defaults
to dry-run; it does not add or renumber entity candidates.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_sec_ii.md"
BODY_SPEC = PROCESS / "chp9_p272_migration.py"
NOTE_SPEC = PROCESS / "chp9_p268_p275_notes_migration.py"
SCAN = PROCESS / "p272_page_review_20261014.png"

MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
COVERAGE = TABLES / "s2-coverage.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
SEGMENTS = TABLES / "segments.jsonl"
BODY_SEGMENT = "chp-9:09_CHP-9_sec_ii:l53-60"
NOTES_SEGMENT = "chp-9:09_CHP-9_sec_ii:l85-127"
BACKUP_SUFFIX = ".bak-s2-chp9-p272-reconciliation-20261014"

EXPECTED_HASHES = {
    MENTIONS: "9be43a3416fec1b132f7bcdea11ae8a965cdd8fffaa9f517064409e05bef17cd",
    STATEMENTS: "26c5d0c3d559464d1c1647312d9ddbbc02c37c1e86662415e35b94b9b5a87b18",
    COVERAGE: "b40a431522dc962c76db0365af3cc1e51b258dcd9a57edd1c24e99605339d663",
    CANDIDATES: "80b34fbf58fe9f0436184452b52a1656f29b40faa3cd5fc6488779d5bd8c642b",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "67d60205c246f2f126433bab8a22ddb29ed73e2af2fed5fff5978c319b3ee923",
    BODY_SPEC: "018741b6cd7b50fdfac37a994f468a1fd56dd98aeea7467eb8d84db07ee3ac08",
    NOTE_SPEC: "8c02184e04b490be86791aca891241bd1d77e1d466374ea34b6bff4a477ab3b3",
    SCAN: "30461168c69cc9a053b768b941a24fff315976ec202674356f08d2c183bd792f",
}
EXPECTED_SEGMENT_HASHES = {
    BODY_SEGMENT: "e3d0127b7c4570ec1a149a6b7a32502fec7af85a366dbd06f2e81be679f5bb17",
    NOTES_SEGMENT: "d00ced6fff3f96f5cf574f47f45eea80ef1b6867c581d7d017f217ee2a8a5a99",
}

CLASSIFICATIONS = {
    "st-chp9-p272-jesuit-church-isolation": False,
    "st-chp9-p272-jesuit-church-marble": False,
    "st-chp9-p272-jesuit-funding-precedent": False,
    "st-chp9-p272-jesuit-visual-anonymity": False,
    "st-chp9-p272-no-leading-painters": False,
    "st-chp9-p272-official-patronage-decline": False,
    "st-chp9-p272-pieta-governors-funding": False,
    "st-chp9-p272-pieta-new-church": False,
    "st-chp9-p272-n01": False,
    "st-chp9-p272-n02": False,
    "st-chp9-p272-n03": True,
    "st-chp9-p272-n03-wilde-no-venice-evidence": False,
    "st-chp9-p272-n04": False,
    "st-chp9-p272-n05": False,
    "st-chp9-p272-n06": False,
}
REASONS = {
    "st-chp9-p272-jesuit-church-isolation": "S2: Haskell's comparative geographic and artistic characterization, not a discrete historical relation between specified entities.",
    "st-chp9-p272-jesuit-church-marble": "S2: an aesthetic evaluation and reported superlative, not a discrete relation between the church and a specified entity.",
    "st-chp9-p272-jesuit-funding-precedent": "S2: the general precedent is unnamed and not bounded to a specific event or entity.",
    "st-chp9-p272-jesuit-visual-anonymity": "S2: Haskell's visual interpretation of the church's style and institutional presence, not a formal historical relation.",
    "st-chp9-p272-no-leading-painters": "S2: a broad negative claim with no identified painter endpoints; note 3 does not establish that the proposed altarpiece was for this church.",
    "st-chp9-p272-official-patronage-decline": "S2: a general evaluative comparison of patronage, without a bounded commission or identified endpoints.",
    "st-chp9-p272-pieta-governors-funding": "S2: this describes the Governors' capacity and inability to pay but names no artist or commission endpoint.",
    "st-chp9-p272-pieta-new-church": "S2: a broad construction and periodization claim with no identified builder or other relation endpoint; preserve it as a source claim.",
    "st-chp9-p272-n01": "S2: a citation locator for a 1762 pamphlet; the cited text was not independently consulted.",
    "st-chp9-p272-n02": "S2: a short bibliographic locator only; the cited text was not independently consulted.",
    "st-chp9-p272-n03": "S2: the note reports a named collector's ownership of a named modello, with a catalogue locator as its evidence; retain the secondhand attribution.",
    "st-chp9-p272-n03-wilde-no-venice-evidence": "S2: this records an evidential limit and an unresolved planned destination, not a positive historical relation.",
    "st-chp9-p272-n04": "S2: a short bibliographic locator only; the cited page and the antecedent of 'It' are not independently resolved.",
    "st-chp9-p272-n05": "S2: a citation locator only; the cited publication was not independently consulted.",
    "st-chp9-p272-n06": "S2: a short bibliographic locator only; the cited text was not independently consulted.",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(handle.name)
    temporary.replace(path)


def literal_assignments(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    values, nodes = {}, {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name):
                    nodes[target.id] = node.value
                    try:
                        values[target.id] = ast.literal_eval(node.value)
                    except (ValueError, TypeError):
                        pass
    return tree, values, nodes


def eval_names(node, names):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name) and node.id in names:
        return names[node.id]
    if isinstance(node, ast.Tuple):
        return tuple(eval_names(child, names) for child in node.elts)
    if isinstance(node, ast.List):
        return [eval_names(child, names) for child in node.elts]
    raise ValueError(f"non-literal migration value: {ast.dump(node)}")


def mention_row(mention_id, segment_id, line_no, candidate_id, surface, note, occurrence,
               source_lines, segment_meta):
    segment = segment_meta.get(segment_id)
    if not segment:
        raise SystemExit(f"missing source segment: {segment_id}")
    first_line, last_line = int(segment["line_start"]), int(segment["line_end"])
    if not first_line <= line_no <= last_line:
        raise SystemExit(f"L{line_no} is outside {segment_id}")
    segment_lines = source_lines[first_line - 1:last_line]
    text = "\n".join(segment_lines)
    source_line = source_lines[line_no - 1]
    positions, cursor = [], 0
    while True:
        at = source_line.find(surface, cursor)
        if at < 0:
            break
        positions.append(at)
        cursor = at + 1
    if occurrence < 0 or occurrence >= len(positions):
        raise SystemExit(f"surface missing at L{line_no}: {surface!r}")
    offset = sum(len(value) + 1 for value in segment_lines[:line_no - first_line])
    start = offset + positions[occurrence]
    end = start + len(surface)
    if text[start:end] != surface:
        raise SystemExit(f"invalid exact source span: {mention_id}")
    return {
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    }


def recover_mentions(source_lines, segment_meta, candidates):
    candidate_ids = {row["candidate_id"] for row in candidates}
    body_tree, body_values, _ = literal_assignments(BODY_SPEC)
    if body_values.get("SEGMENT") != BODY_SEGMENT or body_values.get("MAX_CANDIDATE") != 8721:
        raise SystemExit("p.272 body specification points to a changed segment or candidate sequence")
    body_candidate_ids = {
        row[0]: f"cand-{body_values['MAX_CANDIDATE'] + index:04d}"
        for index, row in enumerate(body_values["SPECS"], 1)
    }
    body_existing = body_values["E"]
    planned = []
    for mid, line_no, key, surface, note in body_values["mentions_to_add"]:
        cid = body_candidate_ids[key] if key in body_candidate_ids else body_existing[key]
        planned.append(mention_row(f"m-chp9-p272-{mid}", BODY_SEGMENT, line_no, cid, surface, note, 0,
                                   source_lines, segment_meta))

    for node in ast.walk(body_tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "mention"):
            continue
        if not node.args or not isinstance(node.args[0], ast.Constant):
            continue
        mention_id = node.args[0].value
        if not isinstance(mention_id, str) or not mention_id.startswith("m-chp9-p272-"):
            continue
        line_no = ast.literal_eval(node.args[1])
        candidate_expr = node.args[2]
        if not (isinstance(candidate_expr, ast.Call) and isinstance(candidate_expr.func, ast.Name)):
            raise SystemExit(f"unsupported candidate expression for {mention_id}")
        key = ast.literal_eval(candidate_expr.args[0])
        mapping = body_candidate_ids if candidate_expr.func.id == "c" else body_existing
        surface, note = ast.literal_eval(node.args[3]), ast.literal_eval(node.args[4])
        occurrence = ast.literal_eval(node.args[5]) if len(node.args) > 5 else 0
        planned.append(mention_row(mention_id, BODY_SEGMENT, line_no, mapping[key], surface, note, occurrence,
                                   source_lines, segment_meta))

    if sum(row["segment_id"] == BODY_SEGMENT for row in planned) < 36:
        raise SystemExit("legacy p.272 body specification yielded fewer than 36 expected mentions")

    note_tree, note_values, note_nodes = literal_assignments(NOTE_SPEC)
    candidate_specs = note_values["CANDIDATE_SPECS"]
    note_candidate_ids = {
        row[0]: f"cand-{note_values['MAX_CANDIDATE'] + index:04d}"
        for index, row in enumerate(candidate_specs, 1)
    }
    names = {key: note_values[key] for key in ("NOTES", "P270", "P271", "P272", "P273", "P275")}
    for key, _name, _kind, detail, line_no, surface in candidate_specs:
        if 53 <= line_no <= 60:
            segment_id = BODY_SEGMENT
        elif 109 <= line_no <= 114:
            segment_id = NOTES_SEGMENT
        else:
            continue
        planned.append(mention_row(f"m-chp9-notes-{key}", segment_id, line_no, note_candidate_ids[key],
                                   surface, detail, 0, source_lines, segment_meta))

    extra_node = note_nodes.get("EXTRA_MENTIONS")
    if not isinstance(extra_node, ast.List):
        raise SystemExit("literal p.268-275 EXTRA_MENTIONS specification is missing")
    extra_keys = {**note_values["EXISTING"], **note_candidate_ids}
    for index, item in enumerate(extra_node.elts, 1):
        segment_id, line_no, key, surface, note = eval_names(item, names)
        if not ((segment_id == BODY_SEGMENT and line_no == 59) or
                (segment_id == NOTES_SEGMENT and line_no in (111, 112))):
            continue
        candidate_id = extra_keys[key]
        # The source names these entities directly; the legacy map linked each
        # surface to the associated artwork instead of to the person.
        if segment_id == NOTES_SEGMENT and line_no == 111 and surface == "S. Luigi Gonzaga":
            candidate_id = "cand-5453"
            note = "Explicit mention of Blessed Luigi Gonzaga, the modello's subject; reuse the existing person candidate."
        if segment_id == NOTES_SEGMENT and line_no == 112 and surface == "Rubens":
            candidate_id = "cand-2293"
            note = "Painter named as creator of the Antwerp series; reuse the existing person candidate."
        planned.append(mention_row(f"m-chp9-note-extra-{index:03d}", segment_id, line_no, candidate_id,
                                   surface, note, 0, source_lines, segment_meta))

    missing = sorted({row["candidate_id"] for row in planned} - candidate_ids)
    if missing:
        raise SystemExit(f"recovered mentions reference absent candidates: {missing}")
    ids = [row["mention_id"] for row in planned]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate mention IDs in recovery plan")
    return planned


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the verified recovery and classifications")
    args = parser.parse_args()

    for path, expected in EXPECTED_HASHES.items():
        actual = sha256(path)
        if actual != expected:
            raise SystemExit(f"pinned input changed: {path.name}: expected {expected}, found {actual}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    _, candidates = read_csv(CANDIDATES)
    mention_fields, mentions = read_csv(MENTIONS)
    statements = read_jsonl(STATEMENTS)
    coverage_fields, coverage = read_csv(COVERAGE)
    segment_meta = {row["segment_id"]: row for row in read_jsonl(SEGMENTS)}
    for segment_id, expected in EXPECTED_SEGMENT_HASHES.items():
        if segment_meta.get(segment_id, {}).get("sha256") != expected:
            raise SystemExit(f"pinned S0 source segment changed: {segment_id}")

    coverage_by_id = {row["segment_id"]: row for row in coverage}
    if (coverage_by_id[BODY_SEGMENT]["disposition"], coverage_by_id[BODY_SEGMENT]["migration_status"]) != ("reviewed", "complete"):
        raise SystemExit("p.272 body coverage is not reviewed/complete")
    if (coverage_by_id[NOTES_SEGMENT]["disposition"], coverage_by_id[NOTES_SEGMENT]["migration_status"]) != ("reviewed", "partial"):
        raise SystemExit("shared p.268-275 notes coverage is not reviewed/partial")

    existing_ids = {row["mention_id"] for row in mentions}
    body_existing = [row for row in mentions if row["segment_id"] == BODY_SEGMENT]
    note_segment_text = "\n".join(source_lines[
        int(segment_meta[NOTES_SEGMENT]["line_start"]) - 1:int(segment_meta[NOTES_SEGMENT]["line_end"])
    ])
    note_start_line = int(segment_meta[NOTES_SEGMENT]["line_start"])
    note_existing = [
        row for row in mentions
        if row["segment_id"] == NOTES_SEGMENT
        and 109 <= note_start_line + note_segment_text[:int(row["start_char"])].count("\n") <= 114
    ]
    if body_existing or note_existing:
        raise SystemExit(f"unexpected prior p.272 mentions: body={len(body_existing)}, notes={len(note_existing)}")

    statements_by_id = {row["statement_id"]: row for row in statements}
    unresolved = {
        row["statement_id"] for row in statements
        if row.get("segment_id") in {BODY_SEGMENT, NOTES_SEGMENT}
        and row.get("statement_id", "").startswith("st-chp9-p272-")
        and "relation_candidate" not in row.get("qualifiers", {})
    }
    if unresolved != set(CLASSIFICATIONS):
        raise SystemExit(f"unexpected open p.272 classification set: {sorted(unresolved ^ set(CLASSIFICATIONS))}")

    planned_mentions = recover_mentions(source_lines, segment_meta, candidates)
    mention_rows = [*mentions, *planned_mentions]
    mention_rows.sort(key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]))

    for statement_id, is_relation in CLASSIFICATIONS.items():
        statement = statements_by_id[statement_id]
        qualifiers = statement.setdefault("qualifiers", {})
        qualifiers["relation_candidate"] = is_relation
        qualifiers["relation_candidate_reason"] = REASONS[statement_id]

    # The named saint in note 3 is an explicit person endpoint. Keep it in the
    # note statement's mention map, separate from the modello work mention.
    note3 = statements_by_id["st-chp9-p272-n03"]
    ids = set(note3["qualifiers"].get("mentioned_candidate_ids", []))
    ids.add("cand-5453")
    note3["qualifiers"]["mentioned_candidate_ids"] = sorted(ids)

    coverage_note = coverage_by_id[NOTES_SEGMENT]["note"]
    marker = "P.272-275 note mentions remain to be reconciled; coverage stays partial."
    if marker not in coverage_note:
        raise SystemExit("shared notes coverage note did not match its pinned p.272-275 handoff marker")
    coverage_by_id[NOTES_SEGMENT]["note"] = coverage_note.replace(
        marker,
        "P.272 note and continuation mentions were reconciled on 2026-10-14; p.273-275 remain to be reconciled, so coverage stays partial.",
    )

    print(json.dumps({
        "mode": "apply" if args.apply else "dry-run",
        "mentions_to_add": len(planned_mentions),
        "body_mentions": sum(row["segment_id"] == BODY_SEGMENT for row in planned_mentions),
        "notes_mentions": sum(row["segment_id"] == NOTES_SEGMENT for row in planned_mentions),
        "classifications": {"true": sum(CLASSIFICATIONS.values()), "false": len(CLASSIFICATIONS) - sum(CLASSIFICATIONS.values())},
        "coverage": {"p272_body": "reviewed/complete", "shared_notes": "reviewed/partial; p273-275 pending"},
        "corrected_legacy_mentions": ["S. Luigi Gonzaga -> cand-5453", "Rubens -> cand-2293"],
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    for path in (MENTIONS, STATEMENTS, COVERAGE):
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"recovery backup already exists: {backup.name}")
        shutil.copy2(path, backup)
    write_csv(MENTIONS, mention_fields, mention_rows)
    write_jsonl(STATEMENTS, statements)
    write_csv(COVERAGE, coverage_fields, coverage)


if __name__ == "__main__":
    main()
