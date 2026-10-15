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
    STATEMENTS.name + ".bak-s2-handoff-chp2-p60-note2-citation-split-20261010"
)
EXPECTED_STATEMENTS_SHA256 = "ae8b93e83640ba6d6a56c05bf242a8d19c50a583d400a08d83503f6cd7dd0f03"
EXPECTED_SOURCE_SHA256 = "5f2ec3c85927ed4aded258d7a6b1801ccb3b8e0416f0f3f9e57ad7b2fae8dd4c"
BOOK_ID = "cand-2962"
SEGMENT_ID = "chp-2:02_CHP-2_sec_vii:l38-54"
SOURCE_FILE = "02-sources/02-Markdown/02_CHP-2_sec_vii.md"
OLD_ID = "st-chp2-secvii-l38-54-fn-p60-2-bellori-and-mezzetti-citations"
NEW_ID = "st-chp2-secvii-l38-54-fn-p60-2-mezzetti-full-history-citation"
BODY_ID = "st-chp2-secvii-l21-30-maratta-continues-apostles-series"
BELLORI_ID = "cand-4831"
MEZZETTI_ID = "cand-4948"
WORK_ID = "cand-4920"


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
    for cid in (BELLORI_ID, MEZZETTI_ID):
        if candidates.get(cid, {}).get("suggested_type") != "archive":
            raise SystemExit(f"cited publication is absent or not archive typed: {cid}")
    if candidates[MEZZETTI_ID].get("status") != "open":
        raise SystemExit("Mezzetti candidate status changed; review before applying")

    rows = [json.loads(line) for line in before.decode("utf-8").splitlines() if line.strip()]
    by_id = {r["statement_id"]: r for r in rows}
    if len(by_id) != len(rows) or OLD_ID not in by_id or NEW_ID in by_id:
        raise SystemExit("duplicate/missing statement IDs")
    row = by_id[OLD_ID]
    q = dict(row.get("qualifiers") or {})
    if (
        row.get("segment_id") != SEGMENT_ID
        or row.get("source_file") != SOURCE_FILE
        or row.get("origin") != "book"
        or row.get("predicate") != "footnote-claim"
        or row.get("subject_candidate_id") != WORK_ID
        or row.get("object_candidate_id") != BELLORI_ID
        or q.get("relation_candidate") is not None
        or q.get("source_line_start") != 45
        or q.get("source_line_end") != 45
        or q.get("print_page") != 60
        or q.get("footnote_marker") != 2
        or MEZZETTI_ID not in (q.get("additional_source_candidate_ids") or [])
        or q.get("bellori_page") != "84"
        or q.get("mezzetti_page") != "253"
    ):
        raise SystemExit("fixed mixed-citation contract changed")
    source_line = source.decode("utf-8-sig").splitlines()[44]
    if row.get("original_quote") != source_line:
        raise SystemExit("source quote no longer matches footnote line 45")
    body = by_id.get(BODY_ID)
    if not body:
        raise SystemExit("linked body statement missing")
    body_q = dict(body.get("qualifiers") or {})
    refs = body_q.get("footnote_refs") or []
    matching = [ref for ref in refs if isinstance(ref, dict)
        and ref.get("segment_id") == SEGMENT_ID and ref.get("source_line") == 45
        and ref.get("marker") == 2 and OLD_ID in (ref.get("statement_ids") or [])]
    if len(matching) != 1:
        raise SystemExit("body footnote backlink is missing or ambiguous")
    prior_claim = str(q.get("claim") or "").strip()
    if not prior_claim:
        raise SystemExit("prior mixed-citation claim missing")

    output = []
    new_row = dict(row)
    new_q = dict(q)
    # Keep the historical statement ID for the Bellori edge to preserve its existing backlinks.
    row = dict(row)
    row.update({"subject_candidate_id": BOOK_ID, "object_candidate_id": BELLORI_ID, "predicate": "cites"})
    q.pop("additional_source_candidate_ids", None)
    q.pop("mezzetti_page", None)
    q.update({
        "claim": (
            "Haskell cites Bellori, 1942, p. 84, in footnote 2 concerning the Apostles series. "
            f"Prior S2 context: {prior_claim}"
        ),
        "citation_context_candidate_id": WORK_ID,
        "citation_publication_candidate_id": BELLORI_ID,
        "citations": [{
            "source_candidate_id": BELLORI_ID,
            "publication_candidate_id": BELLORI_ID,
            "locator": "p. 84",
            "reference_as_printed": "Bellori, 1942, p. 84",
        }],
        "related_body_statement_ids": [BODY_ID],
        "text_layer": "bibliographic citation to publication",
        "qualification": "Bellori citation only; p. 84 is the printed locator. The cited page was not independently consulted.",
        "relation_candidate": True,
        "relation_candidate_note": (
            "S2 citation candidate for the cited Bellori publication. This does not establish "
            "the content of the cited page or create a formal S6 edge."
        ),
        "cited_material_not_independently_consulted": True,
    })
    row["qualifiers"] = q

    new_row["statement_id"] = NEW_ID
    new_row["subject_candidate_id"] = BOOK_ID
    new_row["object_candidate_id"] = MEZZETTI_ID
    new_row["predicate"] = "cites"
    new_q.pop("additional_source_candidate_ids", None)
    new_q.pop("bellori_page", None)
    new_q.update({
        "claim": (
            "Haskell directs readers to the Mezzetti 1955 publication at p. 253 for the full "
            "history of the Apostles series. S0 OCR reads “Mozzetti”; the print and in-book "
            "bibliography identify “Mezzetti”."
        ),
        "citation_context_candidate_id": WORK_ID,
        "citation_publication_candidate_id": MEZZETTI_ID,
        "citations": [{
            "source_candidate_id": MEZZETTI_ID,
            "publication_candidate_id": MEZZETTI_ID,
            "locator": "p. 253",
            "reference_as_printed": "Mezzetti, 1955, p. 253",
            "s0_ocr": "Mozzetti, 1955, p. 253",
        }],
        "related_body_statement_ids": [BODY_ID],
        "text_layer": "bibliographic citation to publication",
        "qualification": (
            "The printed p. 60 spelling and bibliography entry at p. 429 support Mezzetti; "
            "candidate identity remains open and the article was not independently consulted."
        ),
        "print_ocr_correction": (
            "S0 OCR reads Mozzetti; print p. 60 reads Mezzetti. The p. 429 bibliography "
            "entry identifies A. Mezzetti, Contributi a Carlo Maratti, 1955."
        ),
        "relation_candidate": True,
        "relation_candidate_note": (
            "S2 citation candidate to the in-book bibliography record cand-4948. The candidate "
            "remains open; the article itself was not independently consulted and no formal "
            "S6 edge is created."
        ),
        "cited_material_not_independently_consulted": True,
    })
    new_row["qualifiers"] = new_q

    body = dict(body)
    body_q = dict(body.get("qualifiers") or {})
    updated = False
    new_refs = []
    for ref in body_q.get("footnote_refs") or []:
        if isinstance(ref, dict) and (
            ref.get("segment_id") == SEGMENT_ID and ref.get("source_line") == 45 and ref.get("marker") == 2
            and OLD_ID in (ref.get("statement_ids") or [])
        ):
            ref = dict(ref)
            ids = list(ref.get("statement_ids") or [])
            if NEW_ID not in ids:
                ids.append(NEW_ID)
            ref["statement_ids"] = ids
            updated = True
        new_refs.append(ref)
    if not updated:
        raise SystemExit("could not update the reciprocal body backlink")
    body_q["footnote_refs"] = new_refs
    body["qualifiers"] = body_q

    for r in rows:
        if r["statement_id"] == OLD_ID:
            output.append(row)
        elif r["statement_id"] == BODY_ID:
            output.append(body)
        else:
            output.append(r)
        if r["statement_id"] == OLD_ID:
            output.append(new_row)

    after = ("\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in output) + "\n").encode("utf-8")
    true_rows = [r for r in output if (r.get("qualifiers") or {}).get("relation_candidate") is True]
    complete = sum(bool(r.get("subject_candidate_id") and r.get("object_candidate_id")) for r in true_rows)
    open_count = len(true_rows) - complete
    dual_unclassified = sum(
        bool(r.get("subject_candidate_id") and r.get("object_candidate_id"))
        and (r.get("qualifiers") or {}).get("relation_candidate") is None
        for r in output
    )
    footnote_unclassified = sum(
        r.get("predicate") == "footnote-claim"
        and (r.get("qualifiers") or {}).get("relation_candidate") is None
        for r in output
    )
    if (len(output), len(true_rows), complete, open_count, dual_unclassified, footnote_unclassified) != (12665, 3635, 3621, 14, 4438, 14):
        raise SystemExit("unexpected post-state counts")
    return before, after, {
        "mode": "dry-run",
        "split_statement": OLD_ID,
        "new_statement": NEW_ID,
        "new_citation_target": MEZZETTI_ID,
        "body_backlink_updated": BODY_ID,
        "statement_rows": len(output),
        "relation_candidates": len(true_rows),
        "complete_endpoints": complete,
        "open_endpoints": open_count,
        "dual_endpoint_unclassified": dual_unclassified,
        "remaining_unclassified_footnote_claims": footnote_unclassified,
        "before_sha256": sha(before),
        "after_sha256": sha(after),
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
    temp = STATEMENTS.with_name(STATEMENTS.name + ".tmp-chp2-p60-note2-split")
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
