"""Recover p.273 S2 mentions and finish the page's relation-candidate review.

Prior migration files are parsed as literal specifications only. This script
is pinned to the current source and table state and defaults to dry-run.
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
BODY_SPEC = PROCESS / "chp9_p273_migration.py"
NOTE_SPEC = PROCESS / "chp9_p268_p275_notes_migration.py"
SCAN = PROCESS / "p273_page_review_20261014.png"

MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
COVERAGE = TABLES / "s2-coverage.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
SEGMENTS = TABLES / "segments.jsonl"
BODY_SEGMENT = "chp-9:09_CHP-9_sec_ii:l62-68"
NOTES_SEGMENT = "chp-9:09_CHP-9_sec_ii:l85-127"
BACKUP_SUFFIX = ".bak-s2-chp9-p273-reconciliation-20261014"

EXPECTED_HASHES = {
    MENTIONS: "94c0747159a036e22021c2fd7c25fe8b0e342423c11900679b5f02272ea2a94e",
    STATEMENTS: "a939330cb6637e2ebb4fa6b06ac389bf67a8d042e78cd597118c894f00756e90",
    COVERAGE: "0a77bb22c902d1734bfa6e72b181f347a97fb32af660299c20ba34a40669271b",
    CANDIDATES: "80b34fbf58fe9f0436184452b52a1656f29b40faa3cd5fc6488779d5bd8c642b",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "67d60205c246f2f126433bab8a22ddb29ed73e2af2fed5fff5978c319b3ee923",
    BODY_SPEC: "78e0662bfc4f33108d4b00353ba83fe898f5927eff3eb7d7564f656a5acf223f",
    NOTE_SPEC: "8c02184e04b490be86791aca891241bd1d77e1d466374ea34b6bff4a477ab3b3",
    SCAN: "f19813ca954624f8fbffe7e3946f20f9c42a458309a53b54364d9c5297fda9ab",
}
EXPECTED_SEGMENT_HASHES = {
    BODY_SEGMENT: "28948f51a1b46a06efca67df6597c58b2d22369b628a0d2396491eeff5a3d7bc",
    NOTES_SEGMENT: "d00ced6fff3f96f5cf574f47f45eea80ef1b6867c581d7d017f217ee2a8a5a99",
}

CLASSIFICATIONS = {
    "st-chp9-p273-church-paintings-triumphant-tone": False,
    "st-chp9-p273-control-over-artist-uncertain": False,
    "st-chp9-p273-dominicans-carmelites-order-emphasis": False,
    "st-chp9-p273-education-virgin-tenderness": False,
    "st-chp9-p273-first-scheme-doctrinal-subjects": True,
    "st-chp9-p273-n01": False,
    "st-chp9-p273-n02": False,
    "st-chp9-p273-n03": True,
    "st-chp9-p273-n04": False,
    "st-chp9-p273-n05": False,
    "st-chp9-p273-oratorian-mystical-ecstasy": False,
    "st-chp9-p273-second-scheme-virtues": False,
    "st-chp9-p273-tiepolo-madonna-omits-purgatorial-fires": False,
}
REASONS = {
    "st-chp9-p273-church-paintings-triumphant-tone": "S2: a broad authorial synthesis of the preceding church examples, not a discrete historical relation with bounded endpoints.",
    "st-chp9-p273-control-over-artist-uncertain": "S2: this states Haskell's uncertainty about the general degree of artistic control; it does not identify a specific controlling act or endpoint pair.",
    "st-chp9-p273-dominicans-carmelites-order-emphasis": "S2: a comparative characterization of two Orders' painting programmes, not a bounded commission or formal relation.",
    "st-chp9-p273-education-virgin-tenderness": "S2: Haskell's aesthetic comparison of tenderness with certain Roman paintings, not a historical relation between the paintings.",
    "st-chp9-p273-first-scheme-doctrinal-subjects": "S2: the first proposed scheme explicitly assigns the purgatorial-rescue subject to its canvases; retain the directed planned-content relation.",
    "st-chp9-p273-n01": "S2: a short bibliographic locator; the cited pages were not independently consulted.",
    "st-chp9-p273-n02": "S2: the line is a repository and shelfmark locator for the separately recorded bequest claim.",
    "st-chp9-p273-n03": "S2: the note reports the modello's location in a named museum; preserve the secondhand source attribution.",
    "st-chp9-p273-n04": "S2: an internal footnote cross-reference only; the appeal and subsequent Milan chronology are recorded in separate statements.",
    "st-chp9-p273-n05": "S2: a short bibliographic locator; the cited pages were not independently consulted.",
    "st-chp9-p273-oratorian-mystical-ecstasy": "S2: an attributed interpretation of a general effect of Oratorian church paintings, without a bounded artwork endpoint.",
    "st-chp9-p273-second-scheme-virtues": "S2: this preserves the aggregate claim; the three named virtues are separately recorded below as directed planned-content candidates.",
    "st-chp9-p273-tiepolo-madonna-omits-purgatorial-fires": "S2: this is a negative depiction claim about a named work and motif, not a positive formal relation.",
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
    if body.get("SEGMENT") != BODY_SEGMENT or body.get("MAX_CANDIDATE") != 8732:
        raise SystemExit("p.273 body migration specification changed")
    body_new = {row[0]: f"cand-{body['MAX_CANDIDATE'] + index:04d}" for index, row in enumerate(body["SPECS"], 1)}
    planned = []
    for mid, line_no, key, surface, note, occurrence in body["mention_specs"]:
        candidate_id = body_new[key] if key in body_new else body["E"][key]
        # The index has separate candidates for Cesare Ripa and his Iconologia.
        if mid == "ripa":
            candidate_id = "cand-2202"
            note = "Named author of the following manual; reuse the separate person candidate."
        elif mid == "ripa_manual":
            candidate_id = "cand-2203"
            note = "Index sub-entry identifies Iconologia as the cited manual; bibliographic identity remains unverified."
        planned.append(mention_row(f"m-chp9-p273-{mid}", BODY_SEGMENT, line_no, candidate_id,
                                   surface, note, occurrence, source_lines, segment_meta))

    note_tree, note, note_nodes = literal_assignments(NOTE_SPEC)
    note_new = {row[0]: f"cand-{note['MAX_CANDIDATE'] + index:04d}"
                for index, row in enumerate(note["CANDIDATE_SPECS"], 1)}
    names = {key: note[key] for key in ("NOTES", "P270", "P271", "P272", "P273", "P275")}
    for key, _name, _kind, detail, line_no, surface in note["CANDIDATE_SPECS"]:
        if not 115 <= line_no <= 119:
            continue
        planned.append(mention_row(f"m-chp9-notes-{key}", NOTES_SEGMENT, line_no, note_new[key],
                                   surface, detail, 0, source_lines, segment_meta))

    extra_node = note_nodes.get("EXTRA_MENTIONS")
    if not isinstance(extra_node, ast.List):
        raise SystemExit("literal shared-note EXTRA_MENTIONS list is missing")
    extra_keys = {**note["EXISTING"], **note_new}
    for index, item in enumerate(extra_node.elts, 1):
        segment_id, line_no, key, surface, detail = eval_names(item, names)
        if (segment_id, line_no) not in {(BODY_SEGMENT, 65), (NOTES_SEGMENT, 116), (NOTES_SEGMENT, 118)}:
            continue
        planned.append(mention_row(f"m-chp9-note-extra-{index:03d}", segment_id, line_no,
                                   extra_keys[key], surface, detail, 0, source_lines, segment_meta))

    # Existing index entities omitted by the legacy note specification.
    manual = [
        ("m-chp9-p273-n01-urbani", NOTES_SEGMENT, 115, "cand-8793", "Urbani de Ghelthof",
         "Author of the cited 1879 work; reuse the existing archive candidate."),
        ("m-chp9-p273-n02-foscarini", NOTES_SEGMENT, 116, "cand-1056", "Pietro Foscarini",
         "Named donor in the reported 1745 bequest; identity alignment remains for S3."),
        ("m-chp9-p273-n02-will", NOTES_SEGMENT, 116, "cand-8469", "his will",
         "The archival will named as the source of the bequest."),
        ("m-chp9-p273-n02-altar", NOTES_SEGMENT, 116, "__MARBLE_ALTAR__", "altare di marmo fine",
         "Planned fine-marble altar; source does not establish that it was completed."),
        ("m-chp9-p273-n02-correr", NOTES_SEGMENT, 116, "cand-8262", "Biblioteca Correr",
         "Repository named in the manuscript locator."),
        ("m-chp9-p273-n02-shelfmark", NOTES_SEGMENT, 116, "cand-8469", "Cod. Cicogna, MMDCCCCXLV—2686",
         "Exact manuscript shelfmark for Pietro Foscarini's will."),
    ]
    for mention_id, segment_id, line_no, candidate_id, surface, detail in manual:
        planned.append(mention_row(mention_id, segment_id, line_no, candidate_id,
                                   surface, detail, 0, source_lines, segment_meta))

    missing = sorted({row["candidate_id"] for row in planned if row["candidate_id"] != "__MARBLE_ALTAR__"} - candidate_ids)
    if missing:
        raise SystemExit(f"recovered mentions reference absent candidates: {missing}")
    ids = [row["mention_id"] for row in planned]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate mention IDs in p.273 recovery plan")
    return planned


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write verified p.273 reconciliation")
    args = parser.parse_args()
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
    for segment_id, expected in EXPECTED_SEGMENT_HASHES.items():
        if segment_meta.get(segment_id, {}).get("sha256") != expected:
            raise SystemExit(f"pinned S0 segment changed: {segment_id}")

    coverage_by_id = {row["segment_id"]: row for row in coverage}
    if (coverage_by_id[BODY_SEGMENT]["disposition"], coverage_by_id[BODY_SEGMENT]["migration_status"]) != ("reviewed", "complete"):
        raise SystemExit("p.273 body is not reviewed/complete")
    if (coverage_by_id[NOTES_SEGMENT]["disposition"], coverage_by_id[NOTES_SEGMENT]["migration_status"]) != ("reviewed", "partial"):
        raise SystemExit("shared p.268-275 notes are not reviewed/partial")

    note_text = "\n".join(source_lines[84:127])
    existing_body = [row for row in mentions if row["segment_id"] == BODY_SEGMENT]
    existing_p273_notes = [row for row in mentions if row["segment_id"] == NOTES_SEGMENT
                           and 115 <= 85 + note_text[:int(row["start_char"])].count("\n") <= 119]
    if existing_body or existing_p273_notes:
        raise SystemExit(f"unexpected existing p.273 mentions: body={len(existing_body)}, notes={len(existing_p273_notes)}")

    statements_by_id = {row["statement_id"]: row for row in statements}
    unresolved = {row["statement_id"] for row in statements
                  if row.get("qualifiers", {}).get("printed_page") == 273
                  and "relation_candidate" not in row.get("qualifiers", {})}
    if unresolved != set(CLASSIFICATIONS):
        raise SystemExit(f"unexpected p.273 classification set: {sorted(unresolved ^ set(CLASSIFICATIONS))}")

    candidate_ids = {row["candidate_id"] for row in candidates}
    candidate_names = {(row["canonical_name"], row["suggested_type"]) for row in candidates}
    altar_name = "Planned fine-marble altar for the Pietà funded by Pietro Foscarini's 1745 bequest"
    if (altar_name, "work") in candidate_names:
        altar_id = next(row["candidate_id"] for row in candidates
                        if row["canonical_name"] == altar_name and row["suggested_type"] == "work")
        new_candidate = None
    else:
        maximum = max(int(row["candidate_id"].split("-")[1]) for row in candidates)
        altar_id = f"cand-{maximum + 1:04d}"
        if altar_id in candidate_ids:
            raise SystemExit(f"next candidate id is already used: {altar_id}")
        new_candidate = {
            "candidate_id": altar_id, "index_entry_id": "", "canonical_name": altar_name,
            "index_page_range": "", "suggested_type": "work", "status": "open",
            "index_source_file": "", "sub_entry": "",
            "detail": "Haskell reports that Pietro Foscarini left money in his 1745 will for a fine-marble altar to be erected in the Pietà. The source does not establish whether it was completed; retain it as a planned work.",
            "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{NOTES_SEGMENT}#L116",
        }
        candidates.append(new_candidate)
        candidate_ids.add(altar_id)

    planned_mentions = recover_mentions(source_lines, segment_meta, candidates)
    for row in planned_mentions:
        if row["candidate_id"] == "__MARBLE_ALTAR__":
            row["candidate_id"] = altar_id
    mention_ids = {row["mention_id"] for row in mentions}
    collision = mention_ids & {row["mention_id"] for row in planned_mentions}
    if collision:
        raise SystemExit(f"recovered mention IDs already exist: {sorted(collision)}")
    mention_rows = [*mentions, *planned_mentions]
    mention_rows.sort(key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]))

    for statement_id, is_relation in CLASSIFICATIONS.items():
        statement = statements_by_id[statement_id]
        qualifiers = statement.setdefault("qualifiers", {})
        qualifiers["relation_candidate"] = is_relation
        qualifiers["relation_candidate_reason"] = REASONS[statement_id]

    bequest = statements_by_id["st-chp9-p273-n02-foscarini-will-marble-altar-bequest"]
    bequest["object_candidate_id"] = altar_id
    bequest["qualifiers"]["mentioned_candidate_ids"] = sorted({
        *bequest["qualifiers"].get("mentioned_candidate_ids", []), altar_id,
    })
    bequest["qualifiers"]["qualification"] = (
        "The will supplies no amount in this passage; preserve 'left money' and do not infer a completed altar. "
        "The fine-marble altar is recorded as a planned work; the church remains its stated location."
    )

    # Ripa the author and the indexed Iconologia are distinct entities.
    ripa_statement = statements_by_id["st-chp9-p273-tiepolo-drew-virtues-from-ripa"]
    ripa_statement["qualifiers"]["mentioned_candidate_ids"] = sorted({
        *ripa_statement["qualifiers"].get("mentioned_candidate_ids", []), "cand-2202",
    })

    second_quote = "According to the second scheme, the surrounding canvases were to depict the virtues which should inspire the Brethren—‘Faith, Hope and Charity represented in the way everyone knows’ and a host of others."
    source_line = source_lines[66]
    if second_quote not in source_line:
        raise SystemExit("second-scheme source quote changed")
    additions = []
    virtues = [("faith", "cand-8748"), ("hope", "cand-8749"), ("charity", "cand-8750")]
    for key, object_id in virtues:
        statement_id = f"st-chp9-p273-second-scheme-depicts-{key}"
        if statement_id in statements_by_id:
            raise SystemExit(f"planned relation statement already exists: {statement_id}")
        additions.append({
            "statement_id": statement_id, "segment_id": BODY_SEGMENT,
            "subject_candidate_id": "cand-8742", "object_candidate_id": object_id,
            "predicate": f"second_scheme_canvases_depicted_{key}",
            "qualifiers": {
                "source_line_start": 67, "source_line_end": 67, "printed_page": 273,
                "pdf_physical_page": 39,
                "claim": f"Haskell says the second scheme's surrounding canvases were to depict {key.title()} as a virtue inspiring the Brethren.",
                "speaker": "Haskell", "text_layer": "authorial narrative",
                "qualification": "This extracts one named virtue from the proposed second scheme; the source says the plan was later chosen and carried out with modifications, but does not identify a surviving canvas for this virtue.",
                "mentioned_candidate_ids": ["cand-8706", "cand-8742", object_id],
                "relation_candidate": True,
                "relation_candidate_reason": "S2: the source explicitly includes this named virtue among the subjects of the second scheme's surrounding canvases.",
            },
            "original_quote": second_quote,
            "source_file": SOURCE.relative_to(ROOT).as_posix(), "origin": "book",
        })
    statement_rows = [*statements, *additions]

    note = coverage_by_id[NOTES_SEGMENT]["note"]
    marker = "p.273-275 remain to be reconciled, so coverage stays partial."
    if marker not in note:
        raise SystemExit("shared notes handoff marker has changed")
    coverage_by_id[NOTES_SEGMENT]["note"] = note.replace(
        marker,
        "P.273 note and continuation mentions were reconciled on 2026-10-14; p.274-275 remain to be reconciled, so coverage stays partial.",
    )

    print(json.dumps({
        "mode": "apply" if args.apply else "dry-run",
        "mentions_to_add": len(planned_mentions),
        "body_mentions": sum(row["segment_id"] == BODY_SEGMENT for row in planned_mentions),
        "notes_mentions": sum(row["segment_id"] == NOTES_SEGMENT for row in planned_mentions),
        "candidate_to_add": new_candidate is not None,
        "open_classifications": len(CLASSIFICATIONS),
        "relation_classifications": {"true": sum(CLASSIFICATIONS.values()), "false": len(CLASSIFICATIONS) - sum(CLASSIFICATIONS.values())},
        "new_endpoint_relations": len(additions),
        "corrected_entities": ["Ripa author -> cand-2202", "Iconologia manual -> cand-2203", f"planned marble altar -> {altar_id}"],
        "coverage": {"p273_body": "reviewed/complete", "shared_notes": "reviewed/partial; p274-275 pending"},
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    paths = (CANDIDATES, MENTIONS, STATEMENTS, COVERAGE)
    for path in paths:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"recovery backup already exists: {backup.name}")
        shutil.copy2(path, backup)
    write_csv(CANDIDATES, candidate_fields, candidates)
    write_csv(MENTIONS, mention_fields, mention_rows)
    write_jsonl(STATEMENTS, statement_rows)
    write_csv(COVERAGE, coverage_fields, coverage)


if __name__ == "__main__":
    main()
