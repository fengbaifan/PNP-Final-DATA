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
EXPECTED_TABLE_SHA256 = "7362ec1384966b34658b59dea936e6b6e0dfb81eb4f31e3b3e6e90e6eaf84961"
EXPECTED_SOURCE_SHA256 = "96aa11521c311c17676147c3ec99fb47d7cf9042a13bc58768c3742553ac5f83"
EXPECTED_CANDIDATES_SHA256 = "b214ec44c825690db146c4efdcb96e1de4acbbc5d682104ec0c35535d53b2dae"
EXPECTED_MENTIONS_SHA256 = "10eb1687c3af1f4515cae4c68273a263f530dd3c8bb3613a3d2b26ddd9a54647"
SEGMENT = "front-matter:00_05_List_of_Plates:l174-185"
SOURCE_RELATIVE = "02-sources/02-Markdown/00_05_List_of_Plates.md"
BACKUP = TABLE.with_name(
    "book-statements.jsonl.bak-s2-front-matter-second-edition-intro-l174-185-20261010"
)


DECISIONS = {
    "st-fm-2ed-l174-185-01-objection": {
        "predicate": "authorial_problem_statement",
        "old_subject": "cand-3770",
        "old_object": "cand-3126",
        "lines": (176, 176),
        "relation": False,
        "note": "This frames Haskell's assessment of a criticism about the book's treatment of Rome. It is an authorial problem statement, not a historical relation between Haskell and Rome.",
    },
    "st-fm-2ed-l174-185-02-preface-awareness": {
        "predicate": "authorial_prior_awareness",
        "old_subject": "cand-3770",
        "old_object": None,
        "lines": (176, 176),
        "relation": False,
        "note": "This is Haskell's retrospective account of his awareness when writing the earlier preface; it does not assert a relation between independently identified entities.",
    },
    "st-fm-2ed-l174-185-03-honour-review": {
        "predicate": "reported_review_characterization",
        "old_subject": "cand-3807",
        "old_object": "cand-3770",
        "lines": (176, 176),
        "relation": False,
        "note": "The quotation records a reviewer's characterization of Haskell's attitude. The cited review and its evaluative content remain in the statement and citation context; this wording does not establish a separate historical relation between the two people.",
    },
    "st-fm-2ed-l174-185-04-attitude-change": {
        "predicate": "authorial_revision_of_tone",
        "old_subject": "cand-3770",
        "old_object": None,
        "lines": (177, 177),
        "relation": False,
        "note": "This is Haskell's self-reported change in attitude and proposed revision of tone, not a relation between historical entities.",
    },
    "st-fm-2ed-l174-185-05-question": {
        "predicate": "authorial_question",
        "old_subject": "cand-3770",
        "old_object": None,
        "lines": (177, 177),
        "relation": False,
        "note": "This is an explicitly posed question about possible bias, not an established historical relation or conclusion.",
    },
    "st-fm-2ed-l174-185-06-waterhouse-judgment": {
        "predicate": "reported_criticism",
        "old_subject": "cand-3757",
        "old_object": "cand-3770",
        "lines": (177, 177),
        "relation": True,
        "note": "Haskell explicitly attributes to Waterhouse the judgment that Haskell's anti-Roman prejudice distorted his historical sense. Retain as a source-attributed intellectual criticism candidate only; it is not a settled finding or S6 edge.",
    },
    "st-fm-2ed-l174-185-07-article-target": {
        "predicate": "reported_article_argument",
        "old_subject": "cand-3757",
        "old_object": "cand-3879",
        "lines": (178, 178),
        "relation": True,
        "note": "Haskell says Waterhouse's article centrally set out to refute Wittkower's thesis. This is a mediated scholarly-dispute candidate; the article is not treated as a direct personal encounter or as a formal S6 edge.",
    },
    "st-fm-2ed-l174-185-08-wittkower-thesis": {
        "predicate": "quoted_historical_thesis",
        "old_subject": "cand-3879",
        "old_object": "cand-2719",
        "lines": (179, 179),
        "relation": False,
        "note": "This preserves Wittkower's mediated thesis about Venetian painting. The current person-to-place endpoints identify the reported speaker and a term within the thesis, not a direct historical relation suitable for the relation layer.",
    },
    "st-fm-2ed-l174-185-09-waterhouse-critique": {
        "predicate": "reported_criticism_of_historical_periodization",
        "old_subject": "cand-3757",
        "old_object": "cand-3770",
        "lines": (179, 180),
        "relation": True,
        "note": "Waterhouse's quoted article directly criticizes Haskell's periodization and attributed motive. Keep the criticism attributed to Waterhouse and contested; this is an S2 candidate only.",
    },
    "st-fm-2ed-l174-185-10-group-migration": {
        "predicate": "reported_group_migration",
        "old_subject": None,
        "old_object": "cand-3126",
        "lines": (180, 182),
        "relation": True,
        "note": "Waterhouse reports that an unspecified set of painters, with Conca, Giaquinto and Batoni as examples, moved to Rome. The source does not pair Naples or Tuscany with individual painters; retain the group claim without inventing those pairings.",
        "open_reason": "The source gives an unbounded painter group rather than a group candidate. Named examples remain participants, and the two possible origin regions are not paired to them.",
    },
    "st-fm-2ed-l174-185-11-refusal-explanation": {
        "predicate": "reported_group_motive",
        "old_subject": None,
        "old_object": "cand-3126",
        "lines": (182, 183),
        "relation": True,
        "note": "Waterhouse proposes fear of competition as the explanation for an attributed group's refusal to settle in Rome despite pressure. Preserve the attribution and uncertainty; do not treat the motive as verified testimony by the painters.",
        "open_reason": "The named participants are only surname-level references in the source and are retained as unresolved candidates; no bounded group endpoint is identified.",
    },
    "st-fm-2ed-l174-185-12-guido-guercino-comparison": {
        "predicate": "reported_group_historical_comparison",
        "old_subject": None,
        "old_object": "cand-3126",
        "lines": (183, 183),
        "relation": True,
        "note": "Waterhouse reports that Guido and Guercino refused to stay in Rome in the seventeenth century as a comparison. Preserve the source's comparison and unresolved identity of Guido; do not infer a specific occasion.",
        "open_reason": "The source supplies no bounded group endpoint, and Guido is only a first name here; participant identities and scope remain open.",
    },
    "st-fm-2ed-l174-185-13-haskell-response": {
        "predicate": "authorial_assessment_of_criticism",
        "old_subject": "cand-3770",
        "old_object": "cand-3757",
        "lines": (184, 184),
        "relation": True,
        "note": "Haskell explicitly responds to Waterhouse's criticism, acknowledges its weight and ultimately rejects it as unpersuasive. This is a documented scholarly disagreement candidate, not a resolution of the historical question.",
    },
    "st-fm-2ed-l174-185-14-disjunctive-painter-claim": {
        "predicate": "authorial_counterargument",
        "old_subject": "cand-3770",
        "old_object": "cand-3126",
        "new_subject": None,
        "new_object": "cand-3126",
        "lines": (184, 184),
        "relation": True,
        "note": "Haskell asserts a claim about an unnamed group of Italian painters in relation to Rome's principal churches, palaces and visits. Crespi and Solimena are examples only; the disjunctive alternatives are not assigned to either artist individually.",
        "open_reason": "The actual subject is an unnamed painter group, not Haskell. No bounded group candidate is present; Crespi and Solimena remain examples with unresolved identities.",
    },
    "st-fm-2ed-l174-185-15-quality-comparison": {
        "predicate": "authorial_qualitative_assessment",
        "old_subject": "cand-3770",
        "old_object": "cand-3881",
        "lines": (184, 184),
        "relation": False,
        "note": "This is Haskell's subjective quality judgment comparing Crespi and Solimena with Conca. It does not assert a historical relation between the painters.",
    },
    "st-fm-2ed-l174-185-16-conca-chronology": {
        "predicate": "reported_arrival_and_commission_chronology",
        "old_subject": "cand-3881",
        "old_object": "cand-3126",
        "lines": (184, 184),
        "relation": True,
        "note": "Haskell directly reports Conca's arrival in Rome in 1707 and a seven-year interval before his first public commission. Keep the commission unnamed and preserve the source's chronology.",
    },
    "st-fm-2ed-l174-185-17-later-generation": {
        "predicate": "reported_group_chronology",
        "old_subject": None,
        "old_object": "cand-3126",
        "lines": (184, 184),
        "relation": True,
        "note": "Haskell says Giaquinto and Batoni came to Rome a generation later, when the situation had begun to change. Retain the relative chronology and inherited destination without converting it to an exact date.",
        "open_reason": "The passage names two participants but does not define a group entity or give an exact date for the relative chronology.",
    },
    "st-fm-2ed-l174-185-18-tiepolo-veneto": {
        "predicate": "authorial_activity_context",
        "old_subject": "cand-3781",
        "old_object": "cand-4207",
        "lines": (184, 184),
        "relation": True,
        "note": "Haskell places Tiepolo's work activity in the Veneto at this point in the argument. The source names no individual work or exact date; retain Veneto as a region, distinct from Venice city.",
    },
    "st-fm-2ed-l174-185-19-innocent-xi-quotation": {
        "predicate": "quoted_claim_about_papal_spending",
        "old_subject": "cand-3808",
        "old_object": None,
        "lines": (185, 185),
        "relation": True,
        "note": "The attributed quotation asserts that Innocent XI deliberately withheld money from the arts. Preserve it as a source-limited policy relation candidate; the broad target is not mapped to a specific bounded entity and the claim is not independently verified.",
        "open_reason": "The source names a broad field, the arts, but identifies no specific funded or unfunded work or bounded group; no object endpoint is assigned.",
    },
    "st-fm-2ed-l174-185-20-patronage-condition": {
        "predicate": "authorial_temporal_assessment",
        "old_subject": "cand-3770",
        "old_object": "cand-3126",
        "lines": (185, 185),
        "relation": False,
        "note": "This is Haskell's qualitative assessment that Rome's patronage situation improved after Innocent XI's death but remained bleak; it is not a separate relation between Haskell and Rome.",
    },
    "st-fm-2ed-l174-185-21-clement-xi-quotation": {
        "predicate": "quoted_claim_about_nepotism",
        "old_subject": "cand-3022",
        "old_object": None,
        "lines": (185, 185),
        "relation": False,
        "note": "This is a quoted characterization of Clement XI's policy. It names no beneficiary or counterparty and is retained as an attributed governance claim, not a relation candidate.",
    },
    "st-fm-2ed-l174-185-22-employment-implication": {
        "predicate": "authorial_inference_about_employment",
        "old_subject": "cand-3770",
        "old_object": "cand-3022",
        "new_subject": "cand-3022",
        "new_object": None,
        "lines": (185, 185),
        "relation": True,
        "note": "Haskell infers that Clement XI's lack of nepotism would not encourage painters seeking employment. Record Clement as the policy actor, keep Haskell as speaker, and do not infer a commission or any named painter.",
        "open_reason": "The affected painters are an unspecified class looking for employment; the passage names no bounded group or individual endpoint.",
    },
}

CANDIDATE_TYPES = {
    "cand-2719": "place",
    "cand-3022": "person",
    "cand-3062": "person",
    "cand-3126": "place",
    "cand-3757": "person",
    "cand-3770": "person",
    "cand-3781": "person",
    "cand-3786": "person",
    "cand-3807": "person",
    "cand-3808": "person",
    "cand-3871": "person",
    "cand-3879": "person",
    "cand-3881": "person",
    "cand-3884": "person",
    "cand-4202": "person",
    "cand-4203": "person",
    "cand-4204": "person",
    "cand-4205": "person",
    "cand-4206": "person",
    "cand-4207": "place",
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
        description="Classify all statements in the second-edition introduction segment; default is dry-run."
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
    if len(source_lines) < 188 or not all(
        marker in "\n".join(source_lines[175:185])
        for marker in ("Hugh Honour", "Waterhouse", "Clement XI", "Innocent XI", "Tiepolo")
    ):
        raise SystemExit("source line 176-185 content anchor mismatch")

    segment = next(
        (r for r in read_jsonl(SEGMENTS) if r.get("segment_id") == SEGMENT), None
    )
    if (
        segment is None
        or segment.get("source_file") != SOURCE_RELATIVE
        or segment.get("line_start") != 174
        or segment.get("line_end") != 185
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
    actual_ids = {r.get("statement_id") for r in segment_rows}
    if actual_ids != expected_ids:
        raise SystemExit(
            f"segment statement coverage mismatch: expected {len(expected_ids)}, found {len(actual_ids)}"
        )

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

    relation_true = sum(1 for d in DECISIONS.values() if d["relation"])
    relation_false = len(DECISIONS) - relation_true
    open_true = sum(
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
    print(f"classification: relation_candidate=true {relation_true}; false {relation_false}; open endpoints {open_true}")
    print("endpoint corrections: disjunctive painter group subject -> unresolved; employment inference subject -> Clement XI, object -> unresolved")
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
