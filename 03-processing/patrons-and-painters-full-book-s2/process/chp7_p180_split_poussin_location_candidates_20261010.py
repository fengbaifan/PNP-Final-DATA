from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
MENTIONS = ROOT / "04-knowledge/tables/mentions.csv"
SOURCE = ROOT / "02-sources/02-Markdown/07_CHP-7_sec_i.md"
BACKUP = TABLE.with_name(
    TABLE.name + ".bak-s2-handoff-chp7-p180-location-split-20261010"
)
EXPECTED_TABLE_SHA256 = "cc4999d553a61436df57abe97d5525c093de9186dba562a2f5228c59f77aa996"
OLD_ID = "st-chp7-p180-n4-pair-location"
BODY_ID = "st-chp7-p180-i34"
NEW_ROWS = [
    {
        "statement_id": "st-chp7-p180-n4-inspiration-louvre-location",
        "subject_candidate_id": "cand-6773",
        "object_candidate_id": "cand-3254",
        "predicate": "book_note_reports_work_location_at_publication",
        "claim": "Haskell's note reports Inspiration du Poète in the Louvre.",
    },
    {
        "statement_id": "st-chp7-p180-n4-diana-detroit-location",
        "subject_candidate_id": "cand-6774",
        "object_candidate_id": "cand-7072",
        "predicate": "book_note_reports_work_location_at_publication",
        "claim": "Haskell's note reports Diana and Endymion in the Institute of Arts, Detroit.",
    },
]
NOTE_QUOTE = (
    "4 In the Louvre and Institute of Arts, Detroit—see "
    "Nicolas Poussin, pp. 46 and 65."
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def check_candidates() -> None:
    rows = {row["candidate_id"]: row for row in read_rows(CANDIDATES)}
    expected = {
        "cand-6773": "work",
        "cand-6774": "work",
        "cand-3254": "institution",
        "cand-7072": "institution",
        "cand-4633": "archive",
    }
    for candidate_id, expected_type in expected.items():
        row = rows.get(candidate_id)
        if not row or row.get("suggested_type") != expected_type:
            raise SystemExit(
                f"candidate precondition failed: {candidate_id} should be {expected_type}"
            )
    if rows["cand-3254"].get("candidate_origin") != "accepted-ku":
        raise SystemExit("cand-3254 is no longer the accepted Louvre candidate")


def check_mentions() -> None:
    rows = read_rows(MENTIONS)
    expected = {
        ("Louvre", "cand-3254"),
        ("Institute of Arts, Detroit", "cand-7072"),
    }
    actual = {
        (row.get("surface_form", ""), row.get("candidate_id", ""))
        for row in rows
        if row.get("segment_id") == "chp-7:07_CHP-7_sec_i:l293-389"
        and row.get("surface_form") in {"Louvre", "Institute of Arts, Detroit"}
    }
    if not expected <= actual:
        raise SystemExit(f"mention mapping precondition failed: {actual!r}")


def make_relation(row: dict[str, str]) -> dict[str, object]:
    return {
        "statement_id": row["statement_id"],
        "segment_id": "chp-7:07_CHP-7_sec_i:l293-389",
        "subject_candidate_id": row["subject_candidate_id"],
        "object_candidate_id": row["object_candidate_id"],
        "predicate": row["predicate"],
        "qualifiers": {
            "source_line_start": 338,
            "source_line_end": 338,
            "printed_page": 180,
            "pdf_physical_page": 14,
            "claim": row["claim"],
            "speaker": "Haskell, authorial footnote",
            "text_layer": "authorial footnote location claim",
            "qualification": (
                "The note omits 'respectively'. The pairing follows the parallel order "
                "in the linked passage: the two works are named Inspiration du Poète "
                "then Diana and Endymion; note 4 lists the Louvre then the Institute of "
                "Arts, Detroit and cites Nicolas Poussin pp. 46 then 65. The cited "
                "catalogue pages were not independently consulted. This remains a "
                "source-attributed S2 relation candidate, not a formal S6 relation."
            ),
            "footnote_marker": 4,
            "mentioned_candidate_ids": [
                row["subject_candidate_id"],
                row["object_candidate_id"],
                "cand-4633",
            ],
            "linked_body_statement_ids": [BODY_ID],
            "cited_material_not_independently_consulted": True,
            "relation_candidate": True,
        },
        "original_quote": NOTE_QUOTE,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
    }


def prepare() -> tuple[bytes, bytes, list[dict[str, object]]]:
    original = TABLE.read_bytes()
    actual_hash = sha256(original)
    if actual_hash != EXPECTED_TABLE_SHA256:
        raise SystemExit(
            f"table hash changed: expected {EXPECTED_TABLE_SHA256}, got {actual_hash}"
        )

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    if source_lines[337].strip() != NOTE_QUOTE:
        raise SystemExit("source line 338 no longer matches the audited note")
    check_candidates()
    check_mentions()

    text = original.decode("utf-8")
    lines = text.splitlines(keepends=True)
    matching = [i for i, line in enumerate(lines) if json.loads(line).get("statement_id") == OLD_ID]
    if len(matching) != 1:
        raise SystemExit(f"expected one {OLD_ID}, found {len(matching)}")

    rows = [json.loads(line) for line in lines]
    by_id = {row.get("statement_id"): row for row in rows}
    old = by_id[OLD_ID]
    body = by_id.get(BODY_ID)
    if not body:
        raise SystemExit(f"linked body statement missing: {BODY_ID}")
    q = old["qualifiers"]
    endpoint_sets = q.get("candidate_endpoint_sets", {})
    if endpoint_sets.get("subject_candidate_ids") != ["cand-6773", "cand-6774"]:
        raise SystemExit("work endpoint set changed since the reviewed snapshot")
    if endpoint_sets.get("object_candidate_ids") != ["cand-4589", "cand-7072"]:
        raise SystemExit("location endpoint set changed since the reviewed snapshot")
    if "cand-3254" not in q.get("mentioned_candidate_ids", []):
        raise SystemExit("accepted Louvre candidate is absent from the aggregate statement")
    if any(row["statement_id"] in by_id for row in NEW_ROWS):
        raise SystemExit("a proposed statement ID already exists")

    updated = json.loads(json.dumps(old))
    uq = updated["qualifiers"]
    uq["mentioned_candidate_ids"] = [
        candidate_id
        for candidate_id in uq["mentioned_candidate_ids"]
        if candidate_id != "cand-4589"
    ]
    uq["candidate_endpoint_sets"]["object_candidate_ids"] = [
        "cand-3254",
        "cand-7072",
    ]
    uq["candidate_endpoint_sets"]["mapping_status"] = (
        "decomposed by ordered parallel lists into the two scalar relation "
        "candidates recorded in decomposed_into_statement_ids; the footnote omits "
        "'respectively'"
    )
    uq["qualification"] = (
        "This aggregate record preserves the wording of note 4. The parallel order "
        "between the two works in the linked passage and the two locations/pages in "
        "note 4 supports the scalar pair candidates listed in "
        "decomposed_into_statement_ids, although the note omits 'respectively'. "
        "The cited catalogue pages were not independently consulted."
    )
    uq["decomposed_into_statement_ids"] = [row["statement_id"] for row in NEW_ROWS]
    uq["relation_candidate"] = False

    replacement = [updated, *(make_relation(row) for row in NEW_ROWS)]
    new_lines = [json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in replacement]
    idx = matching[0]
    lines[idx:idx + 1] = new_lines
    result = "".join(lines).encode("utf-8")
    return original, result, replacement


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    original, result, replacement = prepare()
    print(
        json.dumps(
            {
                "mode": "apply" if args.apply else "dry-run",
                "before_sha256": sha256(original),
                "after_sha256": sha256(result),
                "replaced_statement_ids": [OLD_ID],
                "new_relation_candidates": [row["statement_id"] for row in replacement[1:]],
                "new_relation_rows": replacement,
                "write": args.apply,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if not args.apply:
        return
    if BACKUP.exists():
        raise SystemExit(f"recovery copy already exists: {BACKUP}")
    shutil.copy2(TABLE, BACKUP)
    if sha256(BACKUP.read_bytes()) != sha256(original):
        raise SystemExit("recovery copy does not match the preimage")
    TABLE.write_bytes(result)
    if sha256(TABLE.read_bytes()) != sha256(result):
        TABLE.write_bytes(original)
        raise SystemExit("post-write hash mismatch; original bytes restored")
    print(f"backup={BACKUP}")
    print(f"applied_sha256={sha256(result)}")


if __name__ == "__main__":
    main()
