from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/00_05_List_of_Plates.md"
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
MENTIONS = ROOT / "04-knowledge/tables/mentions.csv"
COVERAGE = ROOT / "04-knowledge/tables/s2-coverage.csv"
EXPECTED_TABLE_SHA256 = "106558dbb3e56e182990e3774733ed16fc864d2d7c220fd9ad21da0c953fe0c0"
EXPECTED_SOURCE_SHA256 = "96aa11521c311c17676147c3ec99fb47d7cf9042a13bc58768c3742553ac5f83"
EXPECTED_CANDIDATES_SHA256 = "b214ec44c825690db146c4efdcb96e1de4acbbc5d682104ec0c35535d53b2dae"
EXPECTED_MENTIONS_SHA256 = "10eb1687c3af1f4515cae4c68273a263f530dd3c8bb3613a3d2b26ddd9a54647"
SEGMENT = "front-matter:00_05_List_of_Plates:l190-196"
SOURCE_RELATIVE = "02-sources/02-Markdown/00_05_List_of_Plates.md"
BACKUP = TABLE.with_name(
    "book-statements.jsonl.bak-s2-front-matter-second-edition-intro-l190-196-20261010"
)

DECISIONS = {
    "st-fm-2ed-l190-196-01-rome-patronage-continuation": {
        "predicate": "authorial_historical_claim",
        "old_subject": "cand-3770",
        "old_object": "cand-3126",
        "lines": (191, 191),
        "relation": False,
        "note": "This completes Haskell's historical assessment that Rome's attractions as an art-patronage centre had declined. Haskell is the speaker and Rome is the topic; the statement does not assert a relation between them.",
    },
    "st-fm-2ed-l190-196-02-poerson-letter-introduction": {
        "predicate": "reported_letter_context",
        "old_subject": "cand-3746",
        "old_object": "cand-3608",
        "new_subject": "cand-3608",
        "new_object": "cand-3746",
        "lines": (191, 192),
        "relation": True,
        "note": "Haskell directly says Charles-François Poerson wrote the identified 1708 letter. Correct the direction to archive-to-author; the French Academy role and Rome location remain contextual qualifiers.",
    },
    "st-fm-2ed-l190-196-03-poerson-financial-claim": {
        "predicate": "quoted_patronage_explanation",
        "old_subject": "cand-3746",
        "old_object": "cand-3126",
        "lines": (192, 192),
        "relation": False,
        "note": "This is Poerson's attributed causal explanation for the decline of painting: poor financial prospects in Rome. It is retained as a historical claim, not an entity-to-entity relation; the editorial insertion and unresolved addressee remain qualified.",
    },
    "st-fm-2ed-l190-196-04-poerson-war-claim": {
        "predicate": "quoted_war_effect",
        "old_subject": "cand-3746",
        "old_object": "cand-3923",
        "new_subject": None,
        "new_object": "cand-3126",
        "lines": (192, 192),
        "relation": True,
        "note": "Poerson's quoted letter says wars across Europe prevented foreigners from coming to Rome. Preserve the source attribution and causal qualification; Europe is not the destination endpoint.",
        "open_reason": "The destination is resolved to Rome from context, but the source identifies neither a particular war nor a bounded group of prevented visitors.",
    },
    "st-fm-2ed-l190-196-05-poerson-patronage-groups": {
        "predicate": "quoted_group_generalization",
        "old_subject": "cand-3746",
        "old_object": None,
        "new_subject": None,
        "new_object": None,
        "lines": (192, 192),
        "relation": True,
        "note": "Poerson's quoted letter makes a broad contrast between foreigners who rewarded the virtuous and Italian men described as generous only in embraces. Preserve this attributed group-level patronage claim without turning it into individual transactions or verified behaviour.",
        "open_reason": "The quote names broad social categories and no bounded individual, recipient, or transaction; both group endpoints remain open.",
    },
    "st-fm-2ed-l190-196-06-qualitative-judgment": {
        "predicate": "authorial_method_statement",
        "old_subject": "cand-3770",
        "old_object": None,
        "lines": (193, 193),
        "relation": False,
        "note": "This is Haskell's explicit characterization of his final assessment as qualitative, not a historical relation.",
    },
    "st-fm-2ed-l190-196-07-clement-redecoration": {
        "predicate": "reported_redecoration_event",
        "old_subject": "cand-3022",
        "old_object": "cand-3613",
        "new_subject": "cand-3613",
        "new_object": "cand-3022",
        "lines": (193, 193),
        "relation": True,
        "note": "Haskell reports a specific S. Clemente redecoration event in the second decade of the eighteenth century and attributes the action to Clement XI. Orient the event-to-participant candidate; retain the physical church, patron saint, time range, and citation as separate qualifiers.",
    },
    "st-fm-2ed-l190-196-08-assumed-employment": {
        "predicate": "authorial_inference_about_commissioning",
        "old_subject": "cand-3770",
        "old_object": "cand-3613",
        "new_subject": "cand-3022",
        "new_object": None,
        "lines": (193, 193),
        "relation": True,
        "note": "Haskell infers from Clement XI's affection for the church that the pope went out of his way to employ the best available artists. Keep the actual actor as subject, Haskell as speaker, and the inference distinct from a documented contract.",
        "open_reason": "The artists are described only as the best available; no bounded artist group or individual is assigned to this inferred employment claim.",
    },
    "st-fm-2ed-l190-196-09-selected-artists": {
        "predicate": "reported_group_commission_participants",
        "old_subject": "cand-3770",
        "old_object": "cand-3613",
        "new_subject": None,
        "new_object": "cand-3613",
        "lines": (193, 195),
        "relation": True,
        "note": "The source identifies seven named artists as those chosen for the S. Clemente decoration. Retain all seven candidate IDs in participant_candidate_ids; do not assign individual paintings or create seven unsupported contracts.",
        "open_reason": "The source names seven participants, but the scalar subject slot cannot represent their collective without a group candidate. All named participants remain individually mapped in the qualifier.",
    },
    "st-fm-2ed-l190-196-10-commission-comparison": {
        "predicate": "authorial_qualitative_assessment",
        "old_subject": "cand-3770",
        "old_object": "cand-3613",
        "lines": (195, 195),
        "relation": False,
        "note": "This is Haskell's subjective comparison of the commission's quality with other commissions; it is an evaluative claim rather than a relation between the compared commissions.",
    },
    "st-fm-2ed-l190-196-11-waterhouse-clark-painters": {
        "predicate": "reported_scholarly_demonstration",
        "old_subject": "cand-3770",
        "old_object": None,
        "lines": (196, 196),
        "relation": False,
        "note": "Haskell credits Waterhouse and Anthony Clark with scholarship about painters working in Rome, but gives no publication or individual painter endpoint here. Preserve the scholarly attribution in the statement qualifiers; do not infer collaboration or a direct relation to Rome.",
    },
    "st-fm-2ed-l190-196-12-opinion-comparison": {
        "predicate": "reported_historical_opinion",
        "old_subject": "cand-3770",
        "old_object": "cand-3096",
        "lines": (196, 196),
        "relation": False,
        "note": "This reports a broad historical and contemporary opinion comparing Roman painters' achievements with the age of Pietro da Cortona. The author and comparison figure are not the opinion's agent and object endpoints; retain it as an attributed interpretive claim.",
    },
    "st-fm-2ed-l190-196-13-medium-scope-qualification": {
        "predicate": "authorial_scope_qualification",
        "old_subject": "cand-3770",
        "old_object": None,
        "lines": (196, 196),
        "relation": False,
        "note": "This explains why Haskell considers the assessment appropriate for a book about painting but not architecture or sculpture. It is a scope justification, not a relation to those media.",
    },
}

CANDIDATE_TYPES = {
    "cand-2719": "place",
    "cand-3022": "person",
    "cand-3096": "person",
    "cand-3126": "place",
    "cand-3608": "archive",
    "cand-3613": "event",
    "cand-3746": "person",
    "cand-3770": "person",
    "cand-3923": "place",
}


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Classify the second-edition introduction continuation segment; default is dry-run."
    )
    parser.add_argument("--apply", action="store_true", help="write after preflight")
    args = parser.parse_args()

    raw = TABLE.read_bytes()
    actual_table_hash = digest(raw)
    if actual_table_hash != EXPECTED_TABLE_SHA256:
        raise SystemExit(
            f"statement-table SHA mismatch: expected {EXPECTED_TABLE_SHA256}, got {actual_table_hash}"
        )
    source_raw = SOURCE.read_bytes()
    if digest(source_raw) != EXPECTED_SOURCE_SHA256:
        raise SystemExit("S0 source SHA mismatch")
    if digest(CANDIDATES.read_bytes()) != EXPECTED_CANDIDATES_SHA256:
        raise SystemExit("candidate-table SHA mismatch")
    if digest(MENTIONS.read_bytes()) != EXPECTED_MENTIONS_SHA256:
        raise SystemExit("mention-table SHA mismatch")

    source_lines = source_raw.decode("utf-8-sig").splitlines()
    if len(source_lines) < 196 or not all(
        marker in "\n".join(source_lines[190:196])
        for marker in ("Poerson", "1708", "Clement XI", "Waterhouse", "architecture or sculpture")
    ):
        raise SystemExit("source line 191-196 content anchor mismatch")

    segment = next(
        (r for r in read_jsonl(SEGMENTS) if r.get("segment_id") == SEGMENT), None
    )
    if (
        segment is None
        or segment.get("source_file") != SOURCE_RELATIVE
        or segment.get("line_start") != 190
        or segment.get("line_end") != 196
        or segment.get("asset_sha256") != EXPECTED_SOURCE_SHA256
    ):
        raise SystemExit("S0 segment/source mapping mismatch")
    coverage = next(
        (r for r in read_csv(COVERAGE) if r.get("segment_id") == SEGMENT), None
    )
    if not coverage or (coverage.get("disposition"), coverage.get("migration_status")) != (
        "reviewed",
        "complete",
    ):
        raise SystemExit("S2 segment coverage is not reviewed/complete")

    candidates = {r["candidate_id"]: r for r in read_csv(CANDIDATES)}
    for candidate_id, expected_type in CANDIDATE_TYPES.items():
        row = candidates.get(candidate_id)
        if row is None or row.get("suggested_type") != expected_type:
            raise SystemExit(f"candidate/type mismatch: {candidate_id}")

    rows = read_jsonl(TABLE)
    by_id = {r.get("statement_id"): r for r in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")
    segment_rows = [r for r in rows if r.get("segment_id") == SEGMENT]
    expected_ids = set(DECISIONS)
    if {r.get("statement_id") for r in segment_rows} != expected_ids:
        raise SystemExit("segment statement coverage mismatch")

    updated_by_id: dict[str, dict] = {}
    for statement_id, decision in DECISIONS.items():
        row = by_id[statement_id]
        q = row.get("qualifiers") or {}
        expected = (
            decision["predicate"],
            decision["old_subject"],
            decision["old_object"],
            decision["lines"][0],
            decision["lines"][1],
        )
        actual = (
            row.get("predicate"),
            row.get("subject_candidate_id"),
            row.get("object_candidate_id"),
            q.get("source_line_start"),
            q.get("source_line_end"),
        )
        if (
            row.get("source_file") != SOURCE_RELATIVE
            or row.get("origin") != "book"
            or actual != expected
            or "relation_candidate" in q
        ):
            raise SystemExit(f"statement preflight mismatch: {statement_id}")
        updated = deepcopy(row)
        updated["subject_candidate_id"] = decision.get("new_subject", decision["old_subject"])
        updated["object_candidate_id"] = decision.get("new_object", decision["old_object"])
        updated["qualifiers"]["relation_candidate"] = decision["relation"]
        updated["qualifiers"]["relation_candidate_note"] = decision["note"]
        if decision["relation"] and decision.get("open_reason"):
            updated["qualifiers"]["open_endpoint_reason"] = decision["open_reason"]
        updated_by_id[statement_id] = updated

    output_lines: list[str] = []
    seen: set[str] = set()
    for line in raw.decode("utf-8").splitlines():
        if not line.strip():
            output_lines.append(line)
            continue
        current = json.loads(line)
        statement_id = current.get("statement_id")
        if statement_id in updated_by_id:
            output_lines.append(
                json.dumps(updated_by_id[statement_id], ensure_ascii=False, separators=(",", ":"))
            )
            seen.add(statement_id)
        else:
            output_lines.append(line)
    if seen != expected_ids:
        raise SystemExit("write coverage mismatch")
    result = ("\n".join(output_lines) + "\n").encode("utf-8")

    positives = sum(1 for d in DECISIONS.values() if d["relation"])
    opens = sum(
        1
        for d in DECISIONS.values()
        if d["relation"]
        and (
            d.get("new_subject", d["old_subject"]) is None
            or d.get("new_object", d["old_object"]) is None
        )
    )
    print(
        f"preflight passed: source/segment/coverage, table SHA, candidate and mention SHA, "
        f"candidate types, and all {len(DECISIONS)} statement anchors verified"
    )
    print(f"classification: relation_candidate=true {positives}; false {len(DECISIONS)-positives}; open endpoints {opens}")
    print("endpoint corrections: letter -> Poerson; war/visitor claim -> Rome with open subject; redecoration event -> Clement XI; Clement XI employment inference -> open artist object; selected artist group -> redecoration event")
    print(f"output_sha256={digest(result)}")
    if not args.apply:
        print(f"dry-run only; table unchanged; input_sha256={actual_table_hash}")
        return

    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")
    shutil.copy2(TABLE, BACKUP)
    fd, temp_name = tempfile.mkstemp(prefix=TABLE.name + ".", suffix=".tmp", dir=TABLE.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(result)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, TABLE)
    except Exception:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
        raise
    print(f"applied: backup={BACKUP.relative_to(ROOT)} output_sha256={digest(result)}")


if __name__ == "__main__":
    main()
