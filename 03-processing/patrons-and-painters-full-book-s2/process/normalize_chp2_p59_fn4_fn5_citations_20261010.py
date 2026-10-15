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
    STATEMENTS.name + ".bak-s2-handoff-chp2-p59-fn4-fn5-citations-20261010"
)
EXPECTED_STATEMENTS_SHA256 = "541177b39b20e9030d756b31ca04c635b20d0dc68ed67c275a86582250979c1b"
EXPECTED_SOURCE_SHA256 = "5f2ec3c85927ed4aded258d7a6b1801ccb3b8e0416f0f3f9e57ad7b2fae8dd4c"
BOOK_ID = "cand-2962"
SOURCE_FILE = "02-sources/02-Markdown/02_CHP-2_sec_vii.md"
SEGMENT_ID = "chp-2:02_CHP-2_sec_vii:l38-54"
TARGETS = {
    "st-chp2-secvii-l38-54-fn-p59-4-feliciangeli-citation": {
        "archive": "cand-4576", "line": 42, "page": 59, "marker": 4,
        "reference_as_printed": "Feliciangeli.",
        "body_ids": ["st-chp2-secvii-l5-19-bernini-completes-urban-tomb"],
    },
    "st-chp2-secvii-l38-54-fn-p59-5-u-barberini-1950": {
        "archive": "cand-4947", "line": 43, "page": 59, "marker": 5,
        "reference_as_printed": "U. Barberini, 1950.",
        "body_ids": ["st-chp2-secvii-l5-19-tapestry-series-production"],
    },
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def prepare():
    before = STATEMENTS.read_bytes()
    source = SOURCE.read_bytes()
    if sha(before) != EXPECTED_STATEMENTS_SHA256:
        raise SystemExit(f"statement table changed: {sha(before)}")
    if sha(source) != EXPECTED_SOURCE_SHA256:
        raise SystemExit(f"source changed: {sha(source)}")
    with CANDIDATES.open(encoding="utf-8-sig", newline="") as f:
        candidates = {r["candidate_id"]: r for r in csv.DictReader(f)}
    if candidates.get(BOOK_ID, {}).get("suggested_type") != "archive":
        raise SystemExit("book candidate missing or not archive typed")

    rows = [json.loads(line) for line in before.decode("utf-8").splitlines() if line.strip()]
    by_id = {r["statement_id"]: r for r in rows}
    if len(by_id) != len(rows) or set(TARGETS) - set(by_id):
        raise SystemExit("duplicate or missing target statement IDs")
    source_lines = source.decode("utf-8-sig").splitlines()
    changed, output = [], []
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
            or row.get("subject_candidate_id") is not None
            or row.get("object_candidate_id") != spec["archive"]
            or q.get("relation_candidate") is not None
            or q.get("source_line_start") != spec["line"]
            or q.get("source_line_end") != spec["line"]
            or q.get("print_page") != spec["page"]
            or q.get("footnote_marker") != spec["marker"]
        ):
            raise SystemExit(f"fixed source contract changed: {sid}")
        if row["original_quote"] not in source_lines[spec["line"] - 1]:
            raise SystemExit(f"source quote mismatch: {sid}")
        archive = candidates.get(spec["archive"])
        if not archive or archive.get("suggested_type") != "archive":
            raise SystemExit(f"archive candidate missing or wrong type: {sid}")
        for body_id in spec["body_ids"]:
            body = by_id.get(body_id)
            if not body:
                raise SystemExit(f"body statement missing: {sid} -> {body_id}")
            if not any(
                isinstance(ref, dict)
                and ref.get("segment_id") == SEGMENT_ID
                and ref.get("source_line") == spec["line"]
                and ref.get("marker") == spec["marker"]
                and sid in (ref.get("statement_ids") or [])
                for ref in (body.get("qualifiers") or {}).get("footnote_refs", [])
            ):
                raise SystemExit(f"body backlink missing: {sid} -> {body_id}")

        prior = str(q.get("claim") or "").strip()
        if not prior:
            raise SystemExit(f"prior claim missing: {sid}")
        row = dict(row)
        row.update({
            "subject_candidate_id": BOOK_ID,
            "object_candidate_id": spec["archive"],
            "predicate": "cites",
        })
        q.update({
            "claim": (
                f"Haskell’s book cites the source recorded as {spec['reference_as_printed']} "
                f"in footnote {spec['marker']}; no page locator is supplied. "
                f"Prior S2 context: {prior}"
            ),
            "citation_publication_candidate_id": spec["archive"],
            "citations": [{
                "source_candidate_id": spec["archive"],
                "publication_candidate_id": spec["archive"],
                "reference_as_printed": spec["reference_as_printed"],
            }],
            "related_body_statement_ids": spec["body_ids"],
            "text_layer": "bibliographic citation to publication",
            "relation_candidate": True,
            "relation_candidate_note": (
                "S2 citation candidate points to the source record represented by the "
                "incomplete footnote. No title/page locator is inferred; the cited content "
                "was not independently consulted and no formal S6 edge is created."
            ),
            "cited_material_not_independently_consulted": True,
        })
        row["qualifiers"] = q
        output.append(row)
        changed.append({"statement_id": sid, "archive_candidate_id": spec["archive"], "body_statement_ids": spec["body_ids"]})

    after = ("\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in output) + "\n").encode("utf-8")
    true_rows = [r for r in output if (r.get("qualifiers") or {}).get("relation_candidate") is True]
    complete = sum(bool(r.get("subject_candidate_id") and r.get("object_candidate_id")) for r in true_rows)
    open_count = len(true_rows) - complete
    dual_unclassified = sum(
        bool(r.get("subject_candidate_id") and r.get("object_candidate_id"))
        and (r.get("qualifiers") or {}).get("relation_candidate") is None
        for r in output
    )
    remaining = sum(
        r.get("predicate") == "footnote-claim"
        and (r.get("qualifiers") or {}).get("relation_candidate") is None
        for r in output
    )
    if (len(output), len(changed), len(true_rows), complete, open_count, dual_unclassified, remaining) != (12664, 2, 3633, 3619, 14, 4439, 15):
        raise SystemExit("unexpected post-state counts")
    return before, after, {
        "mode": "dry-run", "changed_citations": changed,
        "statement_rows": len(output), "relation_candidates": len(true_rows),
        "complete_endpoints": complete, "open_endpoints": open_count,
        "dual_endpoint_unclassified": dual_unclassified,
        "remaining_unclassified_footnote_claims": remaining,
        "before_sha256": sha(before), "after_sha256": sha(after),
    }


def main():
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
    temp = STATEMENTS.with_name(STATEMENTS.name + ".tmp-chp2-p59-fn4-fn5")
    try:
        temp.write_bytes(after)
        os.replace(temp, STATEMENTS)
    finally:
        if temp.exists():
            temp.unlink()
    print(json.dumps({**report, "mode": "applied", "backup": str(BACKUP.relative_to(ROOT))}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
