"""Recover p.274 S2 mentions and classify its open page and note claims.

Legacy migration files are parsed as literal specifications only. This script
is pinned to current inputs and defaults to dry-run.
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
BODY_SPEC = PROCESS / "chp9_p274_migration.py"
NOTE_SPEC = PROCESS / "chp9_p268_p275_notes_migration.py"
SCAN = PROCESS / "p274_page_review_20261014.png"

MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
COVERAGE = TABLES / "s2-coverage.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
SEGMENTS = TABLES / "segments.jsonl"
BODY_SEGMENT = "chp-9:09_CHP-9_sec_ii:l70-78"
NOTES_SEGMENT = "chp-9:09_CHP-9_sec_ii:l85-127"
BACKUP_SUFFIX = ".bak-s2-chp9-p274-reconciliation-20261014"

EXPECTED_HASHES = {
    MENTIONS: "f8378455d97664017787b938bc46477b3d71fe68fd14cf5ac852a881a1c75971",
    STATEMENTS: "c91b7e3f53a583250dae1cf81df38688e70a2c6f0d0c6610b4fe9b5404ecbb84",
    COVERAGE: "aff6b6f2ab33299eac76b01c723172055979e7c8e374f64ed250855993707738",
    CANDIDATES: "dcd538f63b57d3b52554eaa548248ef363b13ccb57d8c44d38dfdeb47613ccd4",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "67d60205c246f2f126433bab8a22ddb29ed73e2af2fed5fff5978c319b3ee923",
    BODY_SPEC: "2dbb2d8bccc34037286b692eec0d6cd98fe3b550fea39aea1b2a17fd3ad7677a",
    NOTE_SPEC: "8c02184e04b490be86791aca891241bd1d77e1d466374ea34b6bff4a477ab3b3",
    SCAN: "61c4f2e11e0e574469e0a6b30731f3d15f10e479e6ee870d4ba57cf86f428214",
}
EXPECTED_SEGMENT_HASHES = {
    BODY_SEGMENT: "83927497827eff20a3eb9dfc87075c96affdf5b18f53022088980960c4c868ad",
    NOTES_SEGMENT: "d00ced6fff3f96f5cf574f47f45eea80ef1b6867c581d7d017f217ee2a8a5a99",
}

CLASSIFICATIONS = {
    "st-chp9-p274-angeli-compared-to-roman-counterreformation": False,
    "st-chp9-p274-angeli-style-softened": False,
    "st-chp9-p274-corner-born-1693": False,
    "st-chp9-p274-corner-latin-books": False,
    "st-chp9-p274-corner-monastery-intention": False,
    "st-chp9-p274-corner-palace-relics": True,
    "st-chp9-p274-corner-religious-patron": False,
    "st-chp9-p274-n01": False,
    "st-chp9-p274-n02": False,
    "st-chp9-p274-n03": False,
    "st-chp9-p274-n04": False,
    "st-chp9-p274-n05": True,
    "st-chp9-p274-n06": False,
    "st-chp9-p274-programmes-followed-artist-initiative": False,
}
REASONS = {
    "st-chp9-p274-angeli-compared-to-roman-counterreformation": "S2: Haskell's stylistic comparison with an unspecified group of Roman and Venetian painters, not a historical relation between identified endpoints.",
    "st-chp9-p274-angeli-style-softened": "S2: an evaluative account of Angeli's style and its contrast with Piazzetta, not a formal historical relation.",
    "st-chp9-p274-corner-born-1693": "S2: a biographical date claim about one person, not a relation candidate.",
    "st-chp9-p274-corner-latin-books": "S2: a general account of Corner's scholarly activity without an identified book endpoint.",
    "st-chp9-p274-corner-monastery-intention": "S2: the source names no monastery and records a youthful intention, not a completed relation or appointment.",
    "st-chp9-p274-corner-palace-relics": "S2: Haskell explicitly says Corner assembled a large relic collection in his palace; retain the person-to-collection relation candidate.",
    "st-chp9-p274-corner-religious-patron": "S2: a broad authorial description of Corner's interests, without a specified artwork or commission endpoint.",
    "st-chp9-p274-n01": "S2: a source locator for Girolamo Zanetti's dated report; the cited publication page was not independently consulted.",
    "st-chp9-p274-n02": "S2: a short bibliographic locator only; the cited page was not independently consulted.",
    "st-chp9-p274-n03": "S2: the note scopes the following account to Costadoni; it does not assert a relation between identified historical entities.",
    "st-chp9-p274-n04": "S2: a short bibliographic locator only; the cited memoir page was not independently consulted.",
    "st-chp9-p274-n05": "S2: the quoted Correr record explicitly attributes Corner's relic collection and its devotional use to him; preserve the source attribution and collection endpoint.",
    "st-chp9-p274-n06": "S2: a short bibliographic locator only; the cited pages were not independently consulted.",
    "st-chp9-p274-programmes-followed-artist-initiative": "S2: an authorial synthesis about programme discipline and artistic initiative, not a discrete relation with bounded endpoints.",
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
    body_tree, body, _ = literal_assignments(BODY_SPEC)
    if body.get("SEGMENT") != BODY_SEGMENT or body.get("MAX_CANDIDATE") != 8754:
        raise SystemExit("p.274 body migration specification changed")
    body_new = {row[0]: f"cand-{body['MAX_CANDIDATE'] + index:04d}"
                for index, row in enumerate(body["SPECS"], 1)}
    planned = []
    for mid, line_no, key, surface, note, occurrence in body["mention_specs"]:
        candidate_id = body_new[key] if key in body_new else body["E"][key]
        planned.append(mention_row(f"m-chp9-p274-{mid}", BODY_SEGMENT, line_no, candidate_id,
                                   surface, note, occurrence, source_lines, segment_meta))

    _, note, note_nodes = literal_assignments(NOTE_SPEC)
    note_new = {row[0]: f"cand-{note['MAX_CANDIDATE'] + index:04d}"
                for index, row in enumerate(note["CANDIDATE_SPECS"], 1)}
    for key, _name, _kind, detail, line_no, surface in note["CANDIDATE_SPECS"]:
        if not 120 <= line_no <= 125:
            continue
        planned.append(mention_row(f"m-chp9-notes-{key}", NOTES_SEGMENT, line_no, note_new[key],
                                   surface, detail, 0, source_lines, segment_meta))

    extra_node = note_nodes.get("EXTRA_MENTIONS")
    if not isinstance(extra_node, ast.List):
        raise SystemExit("literal shared-note EXTRA_MENTIONS list is missing")
    names = {key: note[key] for key in ("NOTES", "P270", "P271", "P272", "P273", "P275")}
    candidate_by_key = {**note["EXISTING"], **note_new}
    for index, item in enumerate(extra_node.elts, 1):
        segment_id, line_no, key, surface, detail = eval_names(item, names)
        if segment_id == NOTES_SEGMENT and 120 <= line_no <= 125:
            planned.append(mention_row(f"m-chp9-note-extra-{index:03d}", segment_id, line_no,
                                       candidate_by_key[key], surface, detail, 0, source_lines, segment_meta))

    manual = [
        ("m-chp9-p274-n01-zanetti", 120, "cand-2861", "Girolamo Zanetti", "Named author of the cited 1743 report."),
        ("m-chp9-p274-n02-urbani", 121, "cand-8793", "Urbani de Ghelthof", "Named author within the cited 1879 publication locator."),
        ("m-chp9-p274-n04-casanova", 123, "cand-0591", "Casanova", "Author of the cited memoir; reuse the existing person candidate."),
        ("m-chp9-p274-n05-relics", 124, "cand-8762", "Reliquie autentiche di Santi", "Relics in Corner's collection as reported by the quoted record."),
        ("m-chp9-p274-n06-pallucchini", 125, "cand-10319", "Pallucchini", "Author named in the cited 1931 publication; reuse the existing person candidate."),
    ]
    for mention_id, line_no, candidate_id, surface, detail in manual:
        planned.append(mention_row(mention_id, NOTES_SEGMENT, line_no, candidate_id,
                                   surface, detail, 0, source_lines, segment_meta))

    missing = sorted({row["candidate_id"] for row in planned} - candidate_ids)
    if missing:
        raise SystemExit(f"recovered mentions reference absent candidates: {missing}")
    ids = [row["mention_id"] for row in planned]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate mention IDs in p.274 recovery plan")
    return planned


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write verified p.274 reconciliation")
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
            raise SystemExit(f"pinned S0 segment changed: {segment_id}")

    coverage_by_id = {row["segment_id"]: row for row in coverage}
    if (coverage_by_id[BODY_SEGMENT]["disposition"], coverage_by_id[BODY_SEGMENT]["migration_status"]) != ("reviewed", "complete"):
        raise SystemExit("p.274 body is not reviewed/complete")
    if (coverage_by_id[NOTES_SEGMENT]["disposition"], coverage_by_id[NOTES_SEGMENT]["migration_status"]) != ("reviewed", "partial"):
        raise SystemExit("shared p.268-275 notes are not reviewed/partial")

    note_text = "\n".join(source_lines[84:127])
    existing_body = [row for row in mentions if row["segment_id"] == BODY_SEGMENT]
    existing_notes = [row for row in mentions if row["segment_id"] == NOTES_SEGMENT
                      and 120 <= 85 + note_text[:int(row["start_char"])].count("\n") <= 125]
    if existing_body or existing_notes:
        raise SystemExit(f"unexpected existing p.274 mentions: body={len(existing_body)}, notes={len(existing_notes)}")

    statements_by_id = {row["statement_id"]: row for row in statements}
    unresolved = {row["statement_id"] for row in statements
                  if row.get("qualifiers", {}).get("printed_page") == 274
                  and "relation_candidate" not in row.get("qualifiers", {})}
    if unresolved != set(CLASSIFICATIONS):
        raise SystemExit(f"unexpected p.274 classification set: {sorted(unresolved ^ set(CLASSIFICATIONS))}")

    planned_mentions = recover_mentions(source_lines, segment_meta, candidates)
    ids = {row["mention_id"] for row in mentions}
    collision = ids & {row["mention_id"] for row in planned_mentions}
    if collision:
        raise SystemExit(f"recovered mention IDs already exist: {sorted(collision)}")
    mention_rows = [*mentions, *planned_mentions]
    mention_rows.sort(key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]))

    for statement_id, is_relation in CLASSIFICATIONS.items():
        statement = statements_by_id[statement_id]
        qualifiers = statement.setdefault("qualifiers", {})
        qualifiers["relation_candidate"] = is_relation
        qualifiers["relation_candidate_reason"] = REASONS[statement_id]

    relics = statements_by_id["st-chp9-p274-n05"]
    relics["object_candidate_id"] = "cand-8762"
    relics["qualifiers"]["mentioned_candidate_ids"] = sorted({
        *relics["qualifiers"].get("mentioned_candidate_ids", []), "cand-8262", "cand-8762",
    })
    relics["qualifiers"]["relation_candidate"] = True
    relics["qualifiers"]["relation_candidate_reason"] = REASONS["st-chp9-p274-n05"]
    relics["qualifiers"]["qualification"] = (
        "The note quotes a Correr manuscript but gives no folio locator. Preserve the report as source-attributed; "
        "the relic collection is a source-local candidate and its formal type remains unresolved."
    )

    casanova = statements_by_id["st-chp9-p274-n04"]
    casanova["qualifiers"]["mentioned_candidate_ids"] = sorted({
        *casanova["qualifiers"].get("mentioned_candidate_ids", []), "cand-0591",
    })
    pallucchini = statements_by_id["st-chp9-p274-n06"]
    pallucchini["qualifiers"]["mentioned_candidate_ids"] = sorted({
        *pallucchini["qualifiers"].get("mentioned_candidate_ids", []), "cand-10319",
    })

    coverage_note = coverage_by_id[NOTES_SEGMENT]["note"]
    marker = "p.274-275 remain to be reconciled, so coverage stays partial."
    if marker not in coverage_note:
        raise SystemExit("shared notes handoff marker has changed")
    coverage_by_id[NOTES_SEGMENT]["note"] = coverage_note.replace(
        marker,
        "P.274 note and continuation mentions were reconciled on 2026-10-14; p.275 remains to be reconciled, so coverage stays partial.",
    )

    print(json.dumps({
        "mode": "apply" if args.apply else "dry-run",
        "mentions_to_add": len(planned_mentions),
        "body_mentions": sum(row["segment_id"] == BODY_SEGMENT for row in planned_mentions),
        "notes_mentions": sum(row["segment_id"] == NOTES_SEGMENT for row in planned_mentions),
        "open_classifications": len(CLASSIFICATIONS),
        "relation_classifications": {"true": sum(CLASSIFICATIONS.values()), "false": len(CLASSIFICATIONS) - sum(CLASSIFICATIONS.values())},
        "corrected_endpoints": ["Corner -> relic collection (cand-8762)"],
        "coverage": {"p274_body": "reviewed/complete", "shared_notes": "reviewed/partial; p275 pending"},
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
