from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
SOURCE = ROOT / "02-sources/02-Markdown/02_CHP-2_sec_vii.md"
BACKUP = STATEMENTS.with_name(
    STATEMENTS.name + ".bak-s2-handoff-chp2-p60-p61-citations-20261010"
)
EXPECTED_STATEMENTS_SHA256 = (
    "6f3782a870f7ace3a82f1706c7b616e20497bafdd5b7161b08613152b85ea1d1"
)
EXPECTED_SOURCE_SHA256 = (
    "5f2ec3c85927ed4aded258d7a6b1801ccb3b8e0416f0f3f9e57ad7b2fae8dd4c"
)
BOOK_ID = "cand-2962"
SOURCE_FILE = "02-sources/02-Markdown/02_CHP-2_sec_vii.md"
SEGMENT_ID = "chp-2:02_CHP-2_sec_vii:l38-54"

TARGETS = {
    "st-chp2-secvii-l38-54-fn-p60-1-passeri-citation": {
        "old_subject": None,
        "archive": "cand-4376",
        "old_object": "cand-4376",
        "line": 45,
        "page": 60,
        "marker": 1,
        "locator": "Passeri, p. 301",
        "body_statement_ids": [
            "st-chp2-secvii-l21-30-sacchi-refuses-antonio-fresco-commission"
        ],
    },
    "st-chp2-secvii-l38-54-fn-p60-6-pollak-citation": {
        "old_subject": "cand-2208",
        "archive": "cand-4359",
        "old_object": "cand-4359",
        "line": 49,
        "page": 60,
        "marker": 6,
        "locator": "Pollak, 1913, p. 60",
        "body_statement_ids": [
            "st-chp2-secvii-l21-30-romanelli-marriage-of-peleus",
            "st-chp2-secvii-l21-30-romanelli-bacchus-and-ariadne",
            "st-chp2-secvii-l21-30-romanelli-death-1662-retirement",
        ],
    },
    "st-chp2-secvii-l38-54-fn-p61-2-bellori-citation": {
        "old_subject": None,
        "archive": "cand-4831",
        "old_object": "cand-4831",
        "line": 52,
        "page": 61,
        "marker": 2,
        "locator": "Bellori, 1942, p. 85",
        "body_statement_ids": [
            "st-chp2-secvii-l32-36-barberini-patronage-younger-artists",
            "st-chp2-secvii-l32-36-maffeo-son-of-taddeo",
        ],
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_candidates() -> dict[str, dict[str, str]]:
    with CANDIDATES.open(encoding="utf-8-sig", newline="") as f:
        return {row["candidate_id"]: row for row in csv.DictReader(f)}


def prepare() -> tuple[bytes, bytes, dict]:
    before = STATEMENTS.read_bytes()
    source_bytes = SOURCE.read_bytes()
    if sha256(before) != EXPECTED_STATEMENTS_SHA256:
        raise SystemExit(f"statement table changed: {sha256(before)}")
    if sha256(source_bytes) != EXPECTED_SOURCE_SHA256:
        raise SystemExit(f"source file changed: {sha256(source_bytes)}")

    candidates = load_candidates()
    if candidates.get(BOOK_ID, {}).get("suggested_type") != "archive":
        raise SystemExit("book candidate is absent or not archive typed")
    by_id = {}
    rows = [json.loads(line) for line in before.decode("utf-8").splitlines() if line.strip()]
    for row in rows:
        sid = row.get("statement_id")
        if sid in by_id:
            raise SystemExit(f"duplicate statement ID: {sid}")
        by_id[sid] = row
    if set(TARGETS) - set(by_id):
        raise SystemExit("one or more fixed target statements are missing")

    source_lines = source_bytes.decode("utf-8-sig").splitlines()
    changed = []
    output = []
    for row in rows:
        spec = TARGETS.get(row["statement_id"])
        if spec is None:
            output.append(row)
            continue
        sid = row["statement_id"]
        q = dict(row.get("qualifiers") or {})
        if (
            row.get("segment_id") != SEGMENT_ID
            or row.get("source_file") != SOURCE_FILE
            or row.get("origin") != "book"
            or row.get("predicate") != "footnote-claim"
            or row.get("subject_candidate_id") != spec["old_subject"]
            or row.get("object_candidate_id") != spec["old_object"]
            or q.get("relation_candidate") is not None
            or q.get("source_line_start") != spec["line"]
            or q.get("source_line_end") != spec["line"]
            or q.get("print_page") != spec["page"]
            or q.get("footnote_marker") != spec["marker"]
        ):
            raise SystemExit(f"fixed source contract changed: {sid}")
        if spec["line"] > len(source_lines) or row["original_quote"] not in source_lines[spec["line"] - 1]:
            raise SystemExit(f"source quote mismatch: {sid}")
        archive = candidates.get(spec["archive"])
        if not archive or archive.get("suggested_type") != "archive":
            raise SystemExit(f"cited archive is absent or wrong type: {sid}")
        prior_claim = str(q.get("claim") or "").strip()
        if not prior_claim:
            raise SystemExit(f"prior S2 claim missing: {sid}")

        for body_id in spec["body_statement_ids"]:
            body = by_id.get(body_id)
            if not body:
                raise SystemExit(f"linked body statement missing: {sid} -> {body_id}")
            found = False
            for ref in (body.get("qualifiers") or {}).get("footnote_refs") or []:
                if isinstance(ref, dict) and (
                    ref.get("segment_id") == SEGMENT_ID
                    and ref.get("source_line") == spec["line"]
                    and ref.get("marker") == spec["marker"]
                    and sid in (ref.get("statement_ids") or [])
                ):
                    found = True
                    break
            if not found:
                raise SystemExit(f"body footnote backlink missing: {sid} -> {body_id}")

        row = dict(row)
        row["subject_candidate_id"] = BOOK_ID
        row["object_candidate_id"] = spec["archive"]
        row["predicate"] = "cites"
        q.update({
            "claim": (
                f"Haskell’s book cites {archive['canonical_name']} in footnote "
                f"{spec['marker']}; the printed locator is {spec['locator']}. "
                f"Prior S2 context: {prior_claim}"
            ),
            "citation_publication_candidate_id": spec["archive"],
            "citations": [{
                "source_candidate_id": spec["archive"],
                "publication_candidate_id": spec["archive"],
                "locator": spec["locator"],
            }],
            "related_body_statement_ids": spec["body_statement_ids"],
            "text_layer": "bibliographic citation to publication",
            "relation_candidate": True,
            "relation_candidate_note": (
                "S2 citation candidate: the footnote points to the cited publication. "
                "The cited pages were not independently consulted; this does not create "
                "a formal S6 edge."
            ),
            "cited_material_not_independently_consulted": True,
        })
        if spec["old_subject"]:
            q["citation_context_candidate_id"] = spec["old_subject"]
        row["qualifiers"] = q
        output.append(row)
        changed.append({
            "statement_id": sid,
            "archive_candidate_id": spec["archive"],
            "body_statement_ids": spec["body_statement_ids"],
        })

    after = (
        "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in output)
        + "\n"
    ).encode("utf-8")
    true_rows = [r for r in output if (r.get("qualifiers") or {}).get("relation_candidate") is True]
    complete = sum(bool(r.get("subject_candidate_id") and r.get("object_candidate_id")) for r in true_rows)
    open_endpoints = len(true_rows) - complete
    dual_unclassified = sum(
        bool(r.get("subject_candidate_id") and r.get("object_candidate_id"))
        and (r.get("qualifiers") or {}).get("relation_candidate") is None
        for r in output
    )
    if (
        len(output),
        len(changed),
        len(true_rows),
        complete,
        open_endpoints,
        dual_unclassified,
    ) != (12664, 3, 3631, 3617, 14, 4439):
        raise SystemExit("unexpected post-state counts")
    return before, after, {
        "mode": "dry-run",
        "changed_citations": changed,
        "statement_rows": len(output),
        "relation_candidates": len(true_rows),
        "complete_endpoints": complete,
        "open_endpoints": open_endpoints,
        "dual_endpoint_unclassified": dual_unclassified,
        "before_sha256": sha256(before),
        "after_sha256": sha256(after),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    before, after, report = prepare()
    if not args.apply:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    if BACKUP.exists():
        raise SystemExit(f"recovery copy already exists: {BACKUP}")
    if STATEMENTS.read_bytes() != before:
        raise SystemExit("statement table changed after dry-run")
    shutil.copy2(STATEMENTS, BACKUP)
    temporary = STATEMENTS.with_name(STATEMENTS.name + ".tmp-chp2-p60-p61-citations")
    try:
        temporary.write_bytes(after)
        os.replace(temporary, STATEMENTS)
    finally:
        if temporary.exists():
            temporary.unlink()
    print(json.dumps({
        **report,
        "mode": "applied",
        "backup": str(BACKUP.relative_to(ROOT)),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
