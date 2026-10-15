"""Recover omitted p.270 S2 mentions and classify its remaining statements.

The two earlier migration specifications are parsed as literal data only; neither
script is imported or executed. This recovery is pinned to the current source,
segment and table hashes and defaults to a no-write preflight.
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
BODY_SPEC = PROCESS / "chp9_p270_body_migration.py"
NOTE_SPEC = PROCESS / "chp9_p268_p275_notes_migration.py"
SCAN = PROCESS / "p270_page_review_20261014.png"

MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
COVERAGE = TABLES / "s2-coverage.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
SEGMENTS = TABLES / "segments.jsonl"

BODY_SEGMENT = "chp-9:09_CHP-9_sec_ii:l27-36"
NOTES_SEGMENT = "chp-9:09_CHP-9_sec_ii:l85-127"
BACKUP_SUFFIX = ".bak-s2-chp9-p270-reconciliation-20261014"

EXPECTED_HASHES = {
    MENTIONS: "325ab1e435e8bb3740b822b675ca080ef2394cb214edb33d84d5196a34e5c555",
    STATEMENTS: "8a6b0b6ad7f6013e731638722b17c280d6d8a9675940c0a3dc11c860b00e6434",
    COVERAGE: "2c0f09168b675abefc1b58324878fd76e67faa19f7fa3ef5d06a98fffa0b4639",
    CANDIDATES: "80b34fbf58fe9f0436184452b52a1656f29b40faa3cd5fc6488779d5bd8c642b",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "67d60205c246f2f126433bab8a22ddb29ed73e2af2fed5fff5978c319b3ee923",
    BODY_SPEC: "9c8eec8ef31d912d0bc7975f268152c9d5199dc27d97116e2b6de392d3cf73e2",
    NOTE_SPEC: "8c02184e04b490be86791aca891241bd1d77e1d466374ea34b6bff4a477ab3b3",
    SCAN: "389997dd5cf3018ae027e71ecaec3b2d8b7b9ada286b872fea24298871f2f00a",
}
EXPECTED_SEGMENT_HASHES = {
    BODY_SEGMENT: "93efb8db0766c4e0f568e4c49f04cfa8f41c4ae584666445c0682d070e260026",
    NOTES_SEGMENT: "d00ced6fff3f96f5cf574f47f45eea80ef1b6867c581d7d017f217ee2a8a5a99",
}

CLASSIFICATIONS = {
    "st-chp9-p270-1742-visitor-description-partial": False,
    "st-chp9-p270-carmelite-patronage-comparison": True,
    "st-chp9-p270-complaint-had-force-and-church-style": False,
    "st-chp9-p270-critic-architectural-objection": False,
    "st-chp9-p270-dominican-commission": True,
    "st-chp9-p270-n01": False,
    "st-chp9-p270-n02": False,
    "st-chp9-p270-n03": False,
    "st-chp9-p270-n04": False,
    "st-chp9-p270-n05": False,
    "st-chp9-p270-n06": True,
    "st-chp9-p270-n07": False,
    "st-chp9-p270-pamphlet-architectural-comparison": False,
    "st-chp9-p270-scuola-carmini-association": True,
}
REASONS = {
    "st-chp9-p270-1742-visitor-description-partial": "S2: p.270 contains only the opening fragment of the visitor's description; retain the fragment and attribution, while the continuation remains anchored to its own source span.",
    "st-chp9-p270-carmelite-patronage-comparison": "S2: Haskell explicitly compares the mother Carmelite Order's patronage with that of the Scalzi; preserve the broad institutional scope without naming individual commissions.",
    "st-chp9-p270-complaint-had-force-and-church-style": "S2: this is Haskell's architectural interpretation of Roman Baroque grandeur and Palladian tradition, not a formal relation between historical entities.",
    "st-chp9-p270-critic-architectural-objection": "S2: an unnamed critic's evaluative objection about architectural richness and gold, not a formal historical relation.",
    "st-chp9-p270-dominican-commission": "S2: the text links Piazzetta's named fresco commission and work to the Dominican Order, chapel and date range; retain its source-level attribution.",
    "st-chp9-p270-n01": "S2: bibliographic locator only; cited pages were not independently consulted.",
    "st-chp9-p270-n02": "S2: bibliographic locator only; the scan corrects the OCR spelling, but the cited page was not independently consulted.",
    "st-chp9-p270-n03": "S2: citation locator only; the Brera location claim is recorded separately in st-chp9-p270-n03-madonna-brera-location.",
    "st-chp9-p270-n04": "S2: publication locator for documents not identified in this note; no separate archive or publisher relation is established here.",
    "st-chp9-p270-n05": "S2: bibliographic locator only; cited page was not independently consulted.",
    "st-chp9-p270-n06": "S2: this note identifies a specific letter, sender, addressee, date and repository, supporting authored_by/addressed_to/held_by candidates; do not claim independent consultation of the letter.",
    "st-chp9-p270-n07": "S2: source attribution and date only. The note's Dominican content is recorded in separate statements; its printed attachment to the Gesuati sentence is a preserved mismatch, not evidence for that sentence.",
    "st-chp9-p270-pamphlet-architectural-comparison": "S2: this records an anonymous pamphleteer's rhetorical comparison of Jerusalem and Italian buildings, not a formal relation among those places.",
    "st-chp9-p270-scuola-carmini-association": "S2: Haskell identifies the Scuola Grande dei Carmini as the headquarters of a specific lay and religious association under Carmelite inspiration; preserve the institutional relation without inferring membership lists.",
}
EXPECTED_CLASSIFICATIONS_BEFORE = {True: 9696, False: 4038, None: 1095}


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
    values = {}
    nodes = {}
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
    meta = segment_meta.get(segment_id)
    if not meta:
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
    line = source_lines[line_no - 1]
    positions = []
    cursor = 0
    while True:
        position = line.find(surface, cursor)
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
        "mention_id": mention_id,
        "segment_id": segment_id,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    }


def source_mentions_from_original_specs(source_lines, segment_meta, candidate_ids):
    # Read the prior body migration's explicit mention calls as literals; do not execute its stale preconditions.
    body_tree, body_values, _ = literal_assignments(BODY_SPEC)
    if body_values.get("SEGMENT_ID") != BODY_SEGMENT:
        raise SystemExit("original p.270 body specification points to another source segment")
    max_candidate = body_values["EXPECTED_MAX_CANDIDATE"]
    body_candidate_ids = {
        row[0]: f"cand-{max_candidate + index:04d}"
        for index, row in enumerate(body_values["CANDIDATE_SPECS"], 1)
    }
    body_existing = body_values["EXISTING"]
    planned = []
    for node in ast.walk(body_tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "add_mention"):
            continue
        if not node.args or not isinstance(node.args[0], ast.Constant) or not str(node.args[0].value).startswith("m-chp9-p270-"):
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
        surface = ast.literal_eval(node.args[3])
        note = ast.literal_eval(node.args[4])
        occurrence = ast.literal_eval(node.args[5]) if len(node.args) > 5 else 0
        planned.append(make_mention(mention_id, BODY_SEGMENT, line_no, candidate_id, surface, note,
                                    occurrence, source_lines, segment_meta))
    if len(planned) != 49:
        raise SystemExit(f"expected 49 p.270 body mentions in the pinned specification, found {len(planned)}")

    # Extract only p.270 footnote/continuation rows from the consolidated notes specification.
    note_tree, note_values, note_nodes = literal_assignments(NOTE_SPEC)
    note_keys = {key: note_values[key] for key in ("NOTES", "P270", "P271", "P272", "P273", "P275")}
    note_max = note_values["MAX_CANDIDATE"]
    note_specs = note_values["CANDIDATE_SPECS"]
    note_candidate_ids = {row[0]: f"cand-{note_max + index:04d}" for index, row in enumerate(note_specs, 1)}
    for row in note_specs:
        key, _name, _kind, detail, line_no, surface = row
        if line_no not in {36, 96, 97, 98, 99, 100, 101}:
            continue
        segment_id = BODY_SEGMENT if line_no == 36 else NOTES_SEGMENT
        planned.append(make_mention(f"m-chp9-notes-{key}", segment_id, line_no,
                                    note_candidate_ids[key], surface, detail, 0,
                                    source_lines, segment_meta))

    extra_node = note_nodes.get("EXTRA_MENTIONS")
    if extra_node is None or not isinstance(extra_node, ast.List):
        raise SystemExit("literal EXTRA_MENTIONS list is missing from p.268-275 note specification")
    for index, item in enumerate(extra_node.elts, 1):
        segment_id, line_no, key, surface, note = eval_literal_or_name(item, note_keys)
        if (segment_id, line_no) == (NOTES_SEGMENT, 102):
            planned.append(make_mention(f"m-chp9-note-extra-{index:03d}", segment_id, line_no,
                                        note_candidate_ids[key], surface, note, 0,
                                        source_lines, segment_meta))

    # The p.270 note 6 endpoints were in the statement specification but omitted from its mention list.
    manual_specs = [
        ("m-chp9-p270-n06-letter", NOTES_SEGMENT, 101, "cand-8640", "Letter", "Specific letter identified by the note; the manuscript itself was not consulted."),
        ("m-chp9-p270-n06-marchesini", NOTES_SEGMENT, 101, "cand-1539", "Alessandro Marchesini", "Named sender of the cited letter."),
        ("m-chp9-p270-n06-conti", NOTES_SEGMENT, 101, "cand-0833", "Stefano Conti", "Named addressee of the cited letter."),
        ("m-chp9-p270-n06-library", NOTES_SEGMENT, 101, "cand-7803", "Biblioteca Governativa", "Repository named for the cited letter."),
        ("m-chp9-p270-n06-lucca", NOTES_SEGMENT, 101, "cand-1454", "Lucca", "City named in the manuscript repository locator."),
        ("m-chp9-p270-n05-lorenzetti", NOTES_SEGMENT, 100, "cand-8791", "Lorenzetti, 1956", "Repeated bibliographic source in note 5; this cited page was not independently consulted."),
        ("m-chp9-p270-n07-zanetti", NOTES_SEGMENT, 102, "cand-2861", "Girolamo Zanetti", "Named reporter in the footnote attribution."),
        ("m-chp9-p270-n07-dominicans", NOTES_SEGMENT, 102, "cand-0941", "the Dominicans", "Order discussed in the note; its attachment to the Gesuati sentence is mismatched."),
        ("m-chp9-p270-n07-church", NOTES_SEGMENT, 102, "cand-8828", "their church", "The Dominican church described in the note."),
        ("m-chp9-p270-n07-marciana", NOTES_SEGMENT, 102, "cand-9448", "Marciana", "Repository named in the Benigna manuscript locator."),
        ("m-chp9-p270-n07-manuscript", NOTES_SEGMENT, 102, "cand-8778", "MS. Itai.", "Beginning of the cited manuscript locator; OCR spelling is retained."),
        ("m-chp9-p270-n07-dominicans-continuation", BODY_SEGMENT, 36, "cand-0941", "Domenicani Osservanti", "The Italian note continuation identifies the Dominican Observants."),
        ("m-chp9-p270-n07-zattere", BODY_SEGMENT, 36, "cand-8707", "sopra le Zattere", "The note continuation locates the Dominican convent on the Zattere."),
        ("m-chp9-p270-n07-manuscript-continuation", BODY_SEGMENT, 36, "cand-8778", "Cl. VII, 1620", "Continuation of the Marciana manuscript locator split across the source lines."),
    ]
    for mention_id, segment_id, line_no, candidate_id, surface, note in manual_specs:
        planned.append(make_mention(mention_id, segment_id, line_no, candidate_id, surface, note, 0,
                                    source_lines, segment_meta))

    unknown = sorted({row["candidate_id"] for row in planned} - candidate_ids)
    if unknown:
        raise SystemExit(f"recovered mentions reference missing candidates: {unknown}")
    ids = [row["mention_id"] for row in planned]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate mention IDs in recovered p.270 rows")
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
        actual = segment_meta.get(segment_id, {}).get("sha256")
        if actual != expected:
            raise SystemExit(f"pinned segment changed: {segment_id}: {actual}")
    if (coverage_by_id[BODY_SEGMENT]["disposition"], coverage_by_id[BODY_SEGMENT]["migration_status"]) != ("reviewed", "complete"):
        raise SystemExit("p.270 body coverage is not in the expected reviewed/complete state")
    if coverage_by_id[NOTES_SEGMENT]["migration_status"] != "partial":
        raise SystemExit("shared p.268-275 notes coverage should remain partial until p.271-275 are processed")

    body_rows = source_mentions_from_original_specs(source_lines, segment_meta, candidate_ids)
    if len(body_rows) != 74 or sum(row["segment_id"] == BODY_SEGMENT for row in body_rows) != 54:
        raise SystemExit(f"unexpected p.270 recovery counts: total={len(body_rows)}, body_and_note7={sum(row['segment_id'] == BODY_SEGMENT for row in body_rows)}")
    body_segment_rows = [row for row in mentions if row["segment_id"] == BODY_SEGMENT]
    note_p270_existing = []
    note_start, note_end = 85, 127
    note_text_lines = source_lines[note_start - 1:note_end]
    note_offsets = {}
    position = 0
    for line_no, line in zip(range(note_start, note_end + 1), note_text_lines):
        note_offsets[line_no] = (position, position + len(line))
        position += len(line) + 1
    for row in mentions:
        if row["segment_id"] != NOTES_SEGMENT:
            continue
        start = int(row["start_char"])
        line_no = next((line for line, (a, b) in note_offsets.items() if a <= start <= b), None)
        if line_no and 96 <= line_no <= 102:
            note_p270_existing.append(row)
    if body_segment_rows or note_p270_existing:
        raise SystemExit(f"unexpected existing p.270 mentions: body={len(body_segment_rows)}, notes={len(note_p270_existing)}")
    new_mentions = body_rows
    if any(row["mention_id"] in mention_ids for row in new_mentions):
        raise SystemExit("one or more recovered p.270 mention IDs already exist")

    current_counts = {
        True: sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in statements),
        False: sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in statements),
        None: sum("relation_candidate" not in row.get("qualifiers", {}) or row.get("qualifiers", {}).get("relation_candidate") is None for row in statements),
    }
    if current_counts != EXPECTED_CLASSIFICATIONS_BEFORE:
        raise SystemExit(f"unexpected global statement classification counts: {current_counts}")
    if set(CLASSIFICATIONS) != set(REASONS):
        raise SystemExit("every p.270 classification must have one source-based reason")
    if not set(CLASSIFICATIONS) <= set(statements_by_id):
        raise SystemExit(f"expected p.270 statements missing: {sorted(set(CLASSIFICATIONS) - set(statements_by_id))}")
    for statement_id in CLASSIFICATIONS:
        qualifiers = statements_by_id[statement_id].get("qualifiers", {})
        if qualifiers.get("relation_candidate") is not None:
            raise SystemExit(f"p.270 statement is no longer unclassified: {statement_id}")

    for row in new_mentions:
        if row["mention_id"] in mention_ids:
            raise SystemExit(f"duplicate mention ID: {row['mention_id']}")
    unresolved_relation = []
    for statement_id, value in CLASSIFICATIONS.items():
        if value:
            row = statements_by_id[statement_id]
            q = row.get("qualifiers", {})
            refs = {row.get("subject_candidate_id"), row.get("object_candidate_id"), *q.get("mentioned_candidate_ids", [])} - {None}
            if len(refs) < 2:
                unresolved_relation.append((statement_id, sorted(refs)))
    if unresolved_relation:
        raise SystemExit(f"relation candidates need at least two explicit entity endpoints: {unresolved_relation}")

    row = coverage_by_id[BODY_SEGMENT]
    row["source_line_ranges"] = "L28-36"
    row["note"] = (
        "Printed p.270 (CHP-9.pdf physical p.36) body L28-35 and note 7 continuation at L36 were read against the scan. "
        "2026-10-14 reconciliation restored the 49 exact body mentions from the earlier hash-pinned p.270 specification, "
        "restored the p.270 footnote mentions from the consolidated note specification plus source-checked named endpoints, "
        "and classified 14 previously unset statements (4 relation candidates, 10 non-relational). "
        "The visitor quotation continues at p.271. Printed note 7 follows the Gesuati funding sentence but concerns the Dominicans; "
        "its placement/content mismatch is preserved and it is not evidence for Gesuati funding. "
        "Scan corrections are recorded in S2 only; S0 is unchanged."
    )

    class_after = dict(current_counts)
    for value in CLASSIFICATIONS.values():
        class_after[value] += 1
        class_after[None] -= 1
    if class_after != {True: 9700, False: 4048, None: 1081}:
        raise SystemExit(f"unexpected post-reconciliation classification totals: {class_after}")

    print(json.dumps({
        "body_segment": BODY_SEGMENT,
        "notes_segment": NOTES_SEGMENT,
        "restored_p270_body_mentions": 49,
        "restored_notes_mentions": sum(row["segment_id"] == NOTES_SEGMENT for row in new_mentions),
        "restored_p270_segment_mentions_including_note7_continuation": sum(row["segment_id"] == BODY_SEGMENT for row in new_mentions),
        "restored_note7_continuation_mentions": sum(row["segment_id"] == BODY_SEGMENT and row["mention_id"].startswith("m-chp9-p270-n07-") for row in new_mentions) + 2,
        "classifications": {"true": sum(CLASSIFICATIONS.values()), "false": len(CLASSIFICATIONS) - sum(CLASSIFICATIONS.values())},
        "classification_totals_after": class_after,
        "mentions_after": len(mentions) + len(new_mentions),
        "statements_after": len(statements),
        "coverage": "p.270 complete; consolidated p.268-275 notes remain partial pending p.271-275",
    }, ensure_ascii=False, indent=2))

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the preflighted p.270 reconciliation")
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
        q = statements_by_id[statement_id].setdefault("qualifiers", {})
        q["relation_candidate"] = value
        q["relation_candidate_reason"] = REASONS[statement_id]
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
