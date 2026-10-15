"""Recover omitted p.271 S2 mentions and classify its remaining statements.

Prior migration specifications are parsed as literal data only. This script is
pinned to the current source, segment and table hashes and defaults to dry-run.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_sec_ii.md"
BODY_SPEC = PROCESS / "chp9_p271_migration.py"
NOTE_SPEC = PROCESS / "chp9_p268_p275_notes_migration.py"
SCAN = PROCESS / "p271_page_review_20261014.png"

MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
COVERAGE = TABLES / "s2-coverage.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
SEGMENTS = TABLES / "segments.jsonl"
BODY_SEGMENT = "chp-9:09_CHP-9_sec_ii:l38-51"
NOTES_SEGMENT = "chp-9:09_CHP-9_sec_ii:l85-127"
BACKUP_SUFFIX = ".bak-s2-chp9-p271-reconciliation-20261014"

EXPECTED_HASHES = {
    MENTIONS: "b72fe1a790695cf4eb2ba51fa3a4f5f83acc7b96582c4b38907a190a1e1af2ff",
    STATEMENTS: "91b47fcf23701e82917377b89b4f508cf9c211bbdd6c24a1abaf649c6c615889",
    COVERAGE: "2ab8712b3656ab6644a5c2d10660c6711a2070c589b70ef081ddbd7809324319",
    CANDIDATES: "80b34fbf58fe9f0436184452b52a1656f29b40faa3cd5fc6488779d5bd8c642b",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "67d60205c246f2f126433bab8a22ddb29ed73e2af2fed5fff5978c319b3ee923",
    BODY_SPEC: "6c78ce372d108d9cbfebb8ad966bd751bfaea0911b65bcc353dbf539c469fbcd",
    NOTE_SPEC: "8c02184e04b490be86791aca891241bd1d77e1d466374ea34b6bff4a477ab3b3",
    SCAN: "560d5385938950f56164a220782db9e7a3d14f31e508fab7ec443244db05b604",
}
EXPECTED_SEGMENT_HASHES = {
    BODY_SEGMENT: "578273f40983a11f02023c2753bbb564ecf08eae523a74fccd1576ab212c487f",
    NOTES_SEGMENT: "d00ced6fff3f96f5cf574f47f45eea80ef1b6867c581d7d017f217ee2a8a5a99",
}

CLASSIFICATIONS = {
    "st-chp9-p271-dominican-church-exaltation": False,
    "st-chp9-p271-hostile-pamphlet-introduction-partial": False,
    "st-chp9-p271-n01": True,
    "st-chp9-p271-n02": False,
    "st-chp9-p271-n03": False,
    "st-chp9-p271-n03-vecchi-ambiguous-british-museum-works": False,
    "st-chp9-p271-n04": False,
    "st-chp9-p271-n05": False,
    "st-chp9-p271-n06": False,
    "st-chp9-p271-visitor-alms-funding": False,
    "st-chp9-p271-visitor-church-description-continuation": False,
}
REASONS = {
    "st-chp9-p271-dominican-church-exaltation": "S2: this is Haskell's symbolic and evaluative interpretation of a church's suitability, not a historical relation between identified endpoints.",
    "st-chp9-p271-hostile-pamphlet-introduction-partial": "S2: the p.271 clause introduces a cross-page quotation and source context; the pamphlet allegation is separately recorded at p.272, so this fragment is not an additional historical relation.",
    "st-chp9-p271-n01": "S2: the note identifies a specific dated letter, sender, addressee and repository. Record those source-level relation candidates without claiming independent consultation of the letter.",
    "st-chp9-p271-n02": "S2: two short bibliographic locators only; the cited texts were not independently consulted.",
    "st-chp9-p271-n03": "S2: a bibliographic locator for Vecchi's discussion of Concina; the work and cited pages were not independently consulted.",
    "st-chp9-p271-n03-vecchi-ambiguous-british-museum-works": "S2: the pronoun 'him' is unresolved between Concina and Alberto Vecchi; do not assign authorship of the reported works.",
    "st-chp9-p271-n04": "S2: short bibliographic locator only; full identity is deferred to the bibliography pass.",
    "st-chp9-p271-n05": "S2: a broad authorial characterization of Benedictine patronage without a bounded commission or recipient.",
    "st-chp9-p271-n06": "S2: an attributed assessment of Jesuit standing, not a formal historical relation between Cardinal de Bernis and the Jesuits.",
    "st-chp9-p271-visitor-alms-funding": "S2: preserve the visitor's reported funding claim, but the current endpoints identify the visitor and church rather than an alms-source entity and funded building relation.",
    "st-chp9-p271-visitor-church-description-continuation": "S2: a nested visitor description of church furnishings and architecture, not a formal historical relation.",
}
EXPECTED_CLASSIFICATIONS_BEFORE = {True: 9700, False: 4048, None: 1081}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(f.name)
    temporary.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(f.name)
    temporary.replace(path)


def literal_assignments(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
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


def eval_literal_or_name(node, names):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name) and node.id in names:
        return names[node.id]
    if isinstance(node, ast.Tuple):
        return tuple(eval_literal_or_name(item, names) for item in node.elts)
    if isinstance(node, ast.List):
        return [eval_literal_or_name(item, names) for item in node.elts]
    raise ValueError(f"non-literal expression in migration specification: {ast.dump(node)}")


def make_mention(mention_id, segment_id, line_no, candidate_id, surface, note, occurrence,
                 source_lines, segment_meta):
    if segment_id not in segment_meta:
        raise SystemExit(f"missing segment metadata: {segment_id}")
    match = re.search(r":l(\d+)-(\d+)$", segment_id)
    if not match:
        raise SystemExit(f"unrecognized source segment ID: {segment_id}")
    first_line, last_line = map(int, match.groups())
    if not first_line <= line_no <= last_line:
        raise SystemExit(f"L{line_no} falls outside {segment_id}")
    lines = source_lines[first_line - 1:last_line]
    segment_text = "\n".join(lines)
    if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != EXPECTED_SEGMENT_HASHES[segment_id]:
        raise SystemExit(f"source text does not match pinned segment: {segment_id}")
    source_line = source_lines[line_no - 1]
    positions, cursor = [], 0
    while True:
        position = source_line.find(surface, cursor)
        if position < 0:
            break
        positions.append(position)
        cursor = position + 1
    if occurrence >= len(positions):
        raise SystemExit(f"surface missing at L{line_no}: {surface!r}")
    local_line = line_no - first_line
    start = sum(len(value) + 1 for value in lines[:local_line]) + positions[occurrence]
    end = start + len(surface)
    if segment_text[start:end] != surface:
        raise SystemExit(f"invalid exact source span: {mention_id}")
    return {
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    }


def recover_mentions(source_lines, segment_meta, candidate_ids):
    body_tree, body_values, _ = literal_assignments(BODY_SPEC)
    if body_values.get("SEGMENT_ID") != BODY_SEGMENT:
        raise SystemExit("p.271 body migration spec points to another segment")
    body_max = body_values["EXPECTED_MAX_CANDIDATE"]
    body_candidate_ids = {
        row[0]: f"cand-{body_max + index:04d}"
        for index, row in enumerate(body_values["CANDIDATE_SPECS"], 1)
    }
    body_existing = body_values["EXISTING"]
    planned = []
    for node in ast.walk(body_tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "add_mention"):
            continue
        if not node.args or not isinstance(node.args[0], ast.Constant) or not str(node.args[0].value).startswith("m-chp9-p271-"):
            continue
        mention_id = ast.literal_eval(node.args[0])
        line_no = ast.literal_eval(node.args[1])
        candidate_expr = node.args[2]
        if isinstance(candidate_expr, ast.Constant):
            candidate_id = candidate_expr.value
        elif isinstance(candidate_expr, ast.Call) and isinstance(candidate_expr.func, ast.Name):
            key = ast.literal_eval(candidate_expr.args[0])
            mapping = body_candidate_ids if candidate_expr.func.id == "c" else body_existing
            candidate_id = mapping[key]
        else:
            raise SystemExit(f"unsupported candidate expression in {mention_id}")
        surface, note = ast.literal_eval(node.args[3]), ast.literal_eval(node.args[4])
        occurrence = ast.literal_eval(node.args[5]) if len(node.args) > 5 else 0
        planned.append(make_mention(mention_id, BODY_SEGMENT, line_no, candidate_id, surface, note,
                                    occurrence, source_lines, segment_meta))
    if len(planned) != 50:
        raise SystemExit(f"expected 50 p.271 body mentions in the pinned specification, found {len(planned)}")

    note_tree, note_values, note_nodes = literal_assignments(NOTE_SPEC)
    note_max = note_values["MAX_CANDIDATE"]
    note_specs = note_values["CANDIDATE_SPECS"]
    note_candidate_ids = {row[0]: f"cand-{note_max + index:04d}" for index, row in enumerate(note_specs, 1)}
    candidate_by_key = {**note_values["EXISTING"], **note_candidate_ids}
    for key, _name, _kind, detail, line_no, surface in note_specs:
        if line_no in range(103, 109):
            planned.append(make_mention(f"m-chp9-notes-{key}", NOTES_SEGMENT, line_no,
                                        note_candidate_ids[key], surface, detail, 0,
                                        source_lines, segment_meta))

    extra_node = note_nodes.get("EXTRA_MENTIONS")
    if not isinstance(extra_node, ast.List):
        raise SystemExit("literal EXTRA_MENTIONS list is missing")
    name_values = {key: note_values[key] for key in ("NOTES", "P270", "P271", "P272", "P273", "P275")}
    for index, item in enumerate(extra_node.elts, 1):
        segment_id, line_no, key, surface, note = eval_literal_or_name(item, name_values)
        if segment_id != NOTES_SEGMENT or line_no not in (105, 107):
            continue
        candidate_id = candidate_by_key[key]
        if line_no == 105 and surface == "Concina":
            # The prior spec wrongly mapped this explicit surname to Alberto Vecchi.
            candidate_id = "cand-0819"
            note = "Explicit source mention of Padre Daniele Concina; corrected from the legacy spec's Vecchi mapping."
        planned.append(make_mention(f"m-chp9-note-extra-{index:03d}", segment_id, line_no,
                                    candidate_id, surface, note, 0, source_lines, segment_meta))

    # Named endpoints and locators required by the existing p.271 footnote statements.
    manual_specs = [
        ("m-chp9-p271-n01-gherardi", 103, "cand-1155", "P. E. Gherardi", "Named author of the cited 1742 letter."),
        ("m-chp9-p271-n01-muratori", 103, "cand-1717", "Muratori", "Named addressee of the cited 1742 letter."),
        ("m-chp9-p271-n01-library", 103, "cand-8539", "Biblioteca Estense", "Repository named for the cited letter."),
        ("m-chp9-p271-n01-modena", 103, "cand-3416", "Modena", "City in the manuscript repository locator."),
        ("m-chp9-p271-n02-lorenzetti", 104, "cand-8791", "Lorenzetti, 1956", "Repeated bibliographic locator; the cited page was not independently consulted."),
        ("m-chp9-p271-n06-jesuits", 108, "cand-1322", "the Jesuits", "Entity assessed in Cardinal de Bernis's reported statement."),
    ]
    for mention_id, line_no, candidate_id, surface, note in manual_specs:
        planned.append(make_mention(mention_id, NOTES_SEGMENT, line_no, candidate_id, surface, note, 0,
                                    source_lines, segment_meta))

    missing = sorted({row["candidate_id"] for row in planned} - candidate_ids)
    if missing:
        raise SystemExit(f"recovered mentions reference missing candidates: {missing}")
    ids = [row["mention_id"] for row in planned]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate mention IDs in recovered p.271 rows")
    return planned


def main():
    for path, expected in EXPECTED_HASHES.items():
        actual = sha256(path)
        if actual != expected:
            raise SystemExit(f"pinned input changed: {path.name}: expected {expected}, found {actual}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    candidate_fields, candidates = read_csv(CANDIDATES)
    mention_fields, mentions = read_csv(MENTIONS)
    statements = read_jsonl(STATEMENTS)
    coverage_fields, coverage = read_csv(COVERAGE)
    segment_meta = {row["segment_id"]: row for row in read_jsonl(SEGMENTS)}
    candidate_ids = {row["candidate_id"] for row in candidates}
    mention_ids = {row["mention_id"] for row in mentions}
    statements_by_id = {row["statement_id"]: row for row in statements}
    coverage_by_id = {row["segment_id"]: row for row in coverage}

    for segment_id, expected in EXPECTED_SEGMENT_HASHES.items():
        if segment_meta.get(segment_id, {}).get("sha256") != expected:
            raise SystemExit(f"pinned segment changed: {segment_id}")
    if (coverage_by_id[BODY_SEGMENT]["disposition"], coverage_by_id[BODY_SEGMENT]["migration_status"]) != ("reviewed", "complete"):
        raise SystemExit("p.271 body coverage is not in the expected reviewed/complete state")
    if coverage_by_id[NOTES_SEGMENT]["migration_status"] != "partial":
        raise SystemExit("shared p.268-275 notes coverage should remain partial pending p.272-275")

    new_mentions = recover_mentions(source_lines, segment_meta, candidate_ids)
    body_existing = [row for row in mentions if row["segment_id"] == BODY_SEGMENT]
    note_start_offsets = {}
    offset = 0
    for line_no in range(85, 128):
        line = source_lines[line_no - 1]
        note_start_offsets[line_no] = (offset, offset + len(line))
        offset += len(line) + 1
    p271_note_existing = []
    for row in mentions:
        if row["segment_id"] != NOTES_SEGMENT:
            continue
        start = int(row["start_char"])
        line_no = next((line for line, (a, b) in note_start_offsets.items() if a <= start <= b), None)
        if line_no and 103 <= line_no <= 108:
            p271_note_existing.append(row)
    if body_existing or p271_note_existing:
        raise SystemExit(f"unexpected existing p.271 mentions: body={len(body_existing)}, notes={len(p271_note_existing)}")
    if len(new_mentions) != 71 or sum(row["segment_id"] == BODY_SEGMENT for row in new_mentions) != 50:
        raise SystemExit(f"unexpected recovery counts: total={len(new_mentions)}, body={sum(row['segment_id'] == BODY_SEGMENT for row in new_mentions)}")
    if any(row["mention_id"] in mention_ids for row in new_mentions):
        raise SystemExit("one or more recovered p.271 mention IDs already exist")

    current_counts = {
        True: sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in statements),
        False: sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in statements),
        None: sum("relation_candidate" not in row.get("qualifiers", {}) or row.get("qualifiers", {}).get("relation_candidate") is None for row in statements),
    }
    if current_counts != EXPECTED_CLASSIFICATIONS_BEFORE:
        raise SystemExit(f"unexpected global statement classification counts: {current_counts}")
    if set(CLASSIFICATIONS) != set(REASONS) or not set(CLASSIFICATIONS) <= set(statements_by_id):
        raise SystemExit("p.271 classification list/reasons do not match the current statement table")
    for statement_id in CLASSIFICATIONS:
        if statements_by_id[statement_id].get("qualifiers", {}).get("relation_candidate") is not None:
            raise SystemExit(f"p.271 statement is no longer unclassified: {statement_id}")

    # The older note spec attached the explicit Concina mention to Vecchi.
    # Correct both note statements' candidate references while leaving the
    # later pronoun unresolved between the two people.
    concina_ref_repairs = {
        "st-chp9-p271-n03": {"cand-8798", "cand-8797"},
        "st-chp9-p271-n03-vecchi-ambiguous-british-museum-works": {"cand-8797", "cand-8798", "cand-5986"},
    }
    for statement_id, expected_refs in concina_ref_repairs.items():
        q = statements_by_id[statement_id].setdefault("qualifiers", {})
        current_refs = q.get("mentioned_candidate_ids", [])
        if set(current_refs) != expected_refs:
            raise SystemExit(f"unexpected p.271 Concina/Vecchi reference state in {statement_id}: {current_refs}")
        q["mentioned_candidate_ids"] = list(dict.fromkeys([*current_refs, "cand-0819"]))
    relation_without_endpoints = []
    for statement_id, value in CLASSIFICATIONS.items():
        if value:
            row = statements_by_id[statement_id]
            q = row.get("qualifiers", {})
            refs = {row.get("subject_candidate_id"), row.get("object_candidate_id"), *q.get("mentioned_candidate_ids", [])} - {None}
            if len(refs) < 2:
                relation_without_endpoints.append(statement_id)
    if relation_without_endpoints:
        raise SystemExit(f"relation candidates have fewer than two explicit endpoints: {relation_without_endpoints}")

    coverage_by_id[BODY_SEGMENT]["source_line_ranges"] = "L39-51"
    coverage_by_id[BODY_SEGMENT]["note"] = (
        "Printed p.271 (CHP-9.pdf physical p.37) body read against the scan. "
        "2026-10-14 reconciliation restored the 50 exact body mentions from the earlier hash-pinned p.271 specification "
        "and classified 11 previously unset statements (1 relation candidate, 10 non-relational). "
        "The visitor's p.270 church description closes at L39-40; the p.271 final sentence closes at p.272 L54. "
        "Footnotes 1-6 remain in the shared p.268-275 notes segment, which is partial while p.272-275 mentions are reconciled. "
        "Printed punctuation corrections are recorded in S2 only; S0 is unchanged."
    )
    coverage_by_id[NOTES_SEGMENT]["note"] = (
        "Consolidated p.268-275 notes read against their page scans. P.270 note 7 continuation at L36 and p.272 L59-60 / "
        "p.275 L83 continuations remain anchored to their source segments; printed p.270 note 7 is preserved as a marker/content "
        "mismatch and is not evidence for Gesuati funding. Bibliographic locators are not independent source verification. "
        "2026-10-14 reconciliation restored p.268 (11) and p.269 (20) note mentions; p.270 (20) note/continuation mentions; "
        "and p.271 (21) note mentions, including the 1742 letter endpoints. The legacy p.271 note specification mapped the explicit "
        "name Concina to Alberto Vecchi; the restored occurrence is correctly mapped to cand-0819, while the later pronoun remains unresolved. "
        "P.272-275 note mentions remain to be reconciled; coverage stays partial."
    )

    after_counts = dict(current_counts)
    for value in CLASSIFICATIONS.values():
        after_counts[value] += 1
        after_counts[None] -= 1
    if after_counts != {True: 9701, False: 4058, None: 1070}:
        raise SystemExit(f"unexpected post-reconciliation classification totals: {after_counts}")

    print(json.dumps({
        "body_segment": BODY_SEGMENT,
        "notes_segment": NOTES_SEGMENT,
        "restored_body_mentions": 50,
        "restored_p271_note_mentions": 21,
        "restored_mentions_total": len(new_mentions),
        "repaired_concina_candidate_references": len(concina_ref_repairs),
        "classifications": {"true": sum(CLASSIFICATIONS.values()), "false": len(CLASSIFICATIONS) - sum(CLASSIFICATIONS.values())},
        "classification_totals_after": after_counts,
        "mentions_after": len(mentions) + len(new_mentions),
        "statements_after": len(statements),
        "notes_coverage": "partial until p.272-275 footnote mentions are reconciled",
    }, ensure_ascii=False, indent=2))

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the preflighted p.271 reconciliation")
    args = parser.parse_args()
    if not args.apply:
        print("DRY RUN: no table rows written")
        return

    paths = [MENTIONS, STATEMENTS, COVERAGE]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("a recovery backup already exists; inspect it before retrying")
    for source_path, backup_path in zip(paths, backups):
        shutil.copy2(source_path, backup_path)
    for statement_id, value in CLASSIFICATIONS.items():
        qualifiers = statements_by_id[statement_id].setdefault("qualifiers", {})
        qualifiers["relation_candidate"] = value
        qualifiers["relation_candidate_reason"] = REASONS[statement_id]
    try:
        write_csv(MENTIONS, mention_fields, mentions + new_mentions)
        write_jsonl(STATEMENTS, statements)
        write_csv(COVERAGE, coverage_fields, list(coverage_by_id.values()))
    except Exception:
        for target, backup in zip(paths, backups):
            shutil.copy2(backup, target)
        raise
    print("APPLIED; recovery backups retained: " + ", ".join(path.name for path in backups))


if __name__ == "__main__":
    main()
