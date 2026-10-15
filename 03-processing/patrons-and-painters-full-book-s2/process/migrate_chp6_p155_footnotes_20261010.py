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
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
MENTIONS = ROOT / "04-knowledge/tables/mentions.csv"
SOURCE = ROOT / "02-sources/02-Markdown/06_CHP-6_sec_i.md"
EXPECTED_SHA256 = "acbd74bfa6cd7a43905209a4bfbc04bd95d20ef33087e31d332d070751b2f471"
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-chp6-p155-footnotes-20261010")

BOOK_ID = "cand-2962"
RELATION_NOTE = (
    "The footnote explicitly cites this identified archive. This records a bibliographic candidate; "
    "the cited work has not been independently consulted and its contents are not verified here."
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    original = TABLE.read_bytes()
    current_sha = digest(original)
    if current_sha != EXPECTED_SHA256:
        raise SystemExit(f"input SHA mismatch: expected {EXPECTED_SHA256}, got {current_sha}")

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as f:
        candidates = {r["candidate_id"]: r for r in csv.DictReader(f)}
    required_types = {
        BOOK_ID: "archive",
        "cand-6006": "archive",
        "cand-6380": "archive",
        "cand-6381": "archive",
        "cand-6383": "archive",
        "cand-4834": "archive",
        "cand-6338": "archive",
        "cand-6200": "archive",
        "cand-4638": "family",
    }
    for cid, kind in required_types.items():
        if cid not in candidates or candidates[cid].get("suggested_type") != kind:
            raise SystemExit(f"candidate preflight failed: {cid} must exist as {kind}")

    with MENTIONS.open(encoding="utf-8-sig", newline="") as f:
        mention_rows = list(csv.DictReader(f))
    mention_pairs = {(r["segment_id"], r["candidate_id"]) for r in mention_rows}
    mention_requirements = {
        "chp-6:06_CHP-6_sec_i:l120-157": {
            "cand-6006", "cand-6380", "cand-6381", "cand-6382", "cand-6383", "cand-6200", "cand-4638"
        },
        "chp-6:06_CHP-6_sec_i:l102-110": {"cand-1842", "cand-4834", "cand-0272", "cand-6338"},
    }
    for segment_id, candidate_ids in mention_requirements.items():
        for cid in candidate_ids:
            if (segment_id, cid) not in mention_pairs:
                raise SystemExit(f"mention preflight failed: {cid} absent from {segment_id}")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    anchors = {
        151: "Barozzi e Berchet, II, p. 245.",
        152: "Prospero Colonna, 1925.",
        153: "the catalogue of the collection published anonymously in Rome in 1783 and the brief modern account by Corti.",
        154: "Seventeenth-century artistic literature contains a large number of references to Colonna patronage.",
        155: "Bottari, II, pp. 115-16.",
        110: "Pascoli, I, pp. 35, 60, 72, 115, 125, 139, and also Bcllori, 1942, p. 128.",
    }
    for line_no, anchor in anchors.items():
        if anchor not in source_lines[line_no - 1]:
            raise SystemExit(f"source anchor mismatch at L{line_no}")

    target_ids = {
        "st-chp6-notes-l151-p155-n1",
        "st-chp6-notes-l152-p155-n2",
        "st-chp6-notes-l153-p155-n3",
        "st-chp6-p155-note4-bibliographic-continuation",
        "st-chp6-notes-l155-p155-n5-5",
        "st-chp6-p155-lorenzo-commissions-claude",
    }
    new_ids = {
        "st-chp6-notes-l153-p155-n3-corti-citation",
        "st-chp6-notes-l110-p155-n4-bellori-citation",
        "st-chp6-notes-l154-p155-n4-patronage-literature-claim",
    }
    rows = [json.loads(line) for line in original.decode("utf-8").splitlines() if line.strip()]
    by_id = {r.get("statement_id"): r for r in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs in input table")
    if not target_ids.issubset(by_id):
        raise SystemExit(f"missing source statements: {sorted(target_ids - set(by_id))}")
    if new_ids & set(by_id):
        raise SystemExit(f"new statement ID collision: {sorted(new_ids & set(by_id))}")

    expected_predicates = {
        "st-chp6-notes-l151-p155-n1": "footnote_citation",
        "st-chp6-notes-l152-p155-n2": "footnote_citation",
        "st-chp6-notes-l153-p155-n3": "footnote_citation",
        "st-chp6-p155-note4-bibliographic-continuation": "cited-with-in-footnote",
        "st-chp6-notes-l155-p155-n5-5": "footnote_citation",
    }
    for sid, predicate in expected_predicates.items():
        row = by_id[sid]
        q = row.get("qualifiers", {})
        if row.get("predicate") != predicate or q.get("relation_candidate") is not None:
            raise SystemExit(f"classification preflight failed: {sid}")
        if row.get("origin") != "book" or row.get("source_file") != "02-sources/02-Markdown/06_CHP-6_sec_i.md":
            raise SystemExit(f"source provenance mismatch: {sid}")

    # Exact line and marker checks prevent applying this batch to neighboring notes.
    for sid, line_no, marker, page in [
        ("st-chp6-notes-l151-p155-n1", 151, 1, "155"),
        ("st-chp6-notes-l152-p155-n2", 152, 2, "155"),
        ("st-chp6-notes-l153-p155-n3", 153, 3, "155"),
        ("st-chp6-notes-l155-p155-n5-5", 155, 5, "155"),
    ]:
        q = by_id[sid]["qualifiers"]
        if q.get("source_line_start") != line_no or q.get("source_line_end") != line_no or q.get("footnote_marker") != marker or q.get("printed_page") != page:
            raise SystemExit(f"source line/page/marker mismatch: {sid}")

    before = {sid: deepcopy(by_id[sid]) for sid in target_ids}
    out = {sid: deepcopy(by_id[sid]) for sid in target_ids}

    def make_cite(sid: str, object_id: str, claim: str, locator: str, mentions: list[str], quote: str | None = None) -> None:
        row = out[sid]
        q = row["qualifiers"]
        row["subject_candidate_id"] = BOOK_ID
        row["object_candidate_id"] = object_id
        row["predicate"] = "cites"
        q["claim"] = claim
        q["citation_locator"] = locator
        q["mentioned_candidate_ids"] = mentions
        q["relation_candidate"] = True
        q["relation_candidate_note"] = RELATION_NOTE
        if quote is not None:
            row["original_quote"] = quote

    make_cite(
        "st-chp6-notes-l151-p155-n1", "cand-6006",
        "Footnote 1 cites Barozzi e Berchet, volume II, page 245.", "vol. II, p. 245", ["cand-6006"]
    )
    make_cite(
        "st-chp6-notes-l152-p155-n2", "cand-6380",
        "Footnote 2 cites Prospero Colonna (1925); the publication title is not supplied in the note.", "1925; title not supplied", ["cand-6380"]
    )

    note3_id = "st-chp6-notes-l153-p155-n3"
    note3 = out[note3_id]
    make_cite(
        note3_id, "cand-6381",
        "Footnote 3 refers to the anonymous catalogue of the Colonna collection, published in Rome in 1783.",
        "Rome, 1783", ["cand-6381"],
        "See the catalogue of the collection published anonymously in Rome in 1783"
    )
    corti = deepcopy(note3)
    corti["statement_id"] = "st-chp6-notes-l153-p155-n3-corti-citation"
    corti["object_candidate_id"] = "cand-6383"
    cq = corti["qualifiers"]
    cq["claim"] = "Footnote 3 also refers to Corti’s brief modern account of the Colonna collection; publication details are not supplied."
    cq["citation_locator"] = "brief modern account; publication details unspecified"
    cq["mentioned_candidate_ids"] = ["cand-6382", "cand-6383"]
    corti["original_quote"] = "and the brief modern account by Corti."

    n4_id = "st-chp6-p155-note4-bibliographic-continuation"
    pascoli = out[n4_id]
    pascoli["subject_candidate_id"] = BOOK_ID
    pascoli["object_candidate_id"] = "cand-4834"
    pascoli["predicate"] = "cites"
    pq = pascoli["qualifiers"]
    pq["claim"] = "The continuation of footnote 4 cites Pascoli, volume I, at pages 35, 60, 72, 115, 125, and 139, for references to Colonna patronage."
    pq["citation_locator"] = "vol. I, pp. 35, 60, 72, 115, 125, 139"
    pq["mentioned_candidate_ids"] = ["cand-1842", "cand-4834"]
    pq["relation_candidate"] = True
    pq["relation_candidate_note"] = RELATION_NOTE
    pq["footnote_source_lines"] = [154, 110]
    bellori = deepcopy(pascoli)
    bellori["statement_id"] = "st-chp6-notes-l110-p155-n4-bellori-citation"
    bellori["object_candidate_id"] = "cand-6338"
    bq = bellori["qualifiers"]
    bq["claim"] = "The continuation of footnote 4 also cites a Bellori publication identified only as 1942, page 128, for references to Colonna patronage."
    bq["citation_locator"] = "1942, p. 128; title and edition unspecified"
    bq["mentioned_candidate_ids"] = ["cand-0272", "cand-6338"]
    bq["ocr_correction"] = "S0 reads 'Bcllori'; the printed page reads 'Bellori'. S0 is unchanged."
    bellori["original_quote"] = "and also Bcllori, 1942, p. 128."

    make_cite(
        "st-chp6-notes-l155-p155-n5-5", "cand-6200",
        "Footnote 5 cites Bottari, volume II, pages 115–116, for the preceding quotation attributed to Padre Sebastiano Resta.",
        "vol. II, pp. 115–116", ["cand-3507", "cand-6200"]
    )

    claim_id = "st-chp6-notes-l154-p155-n4-patronage-literature-claim"
    claim = {
        "statement_id": claim_id,
        "segment_id": "chp-6:06_CHP-6_sec_i:l120-157",
        "subject_candidate_id": "cand-4638",
        "object_candidate_id": None,
        "predicate": "footnote_claim",
        "qualifiers": {
            "source_line_start": 154,
            "source_line_end": 154,
            "printed_page": "155",
            "pdf_physical_page": 10,
            "printed_page_locator": "p.155 n.4",
            "claim": "Haskell states that seventeenth-century artistic literature contains many references to Colonna patronage.",
            "speaker": "Haskell",
            "text_layer": "authorial claim in footnote",
            "qualification": "This is Haskell’s general bibliographic assertion. The note does not enumerate all references, and the cited materials have not been independently consulted.",
            "mentioned_candidate_ids": ["cand-4638"],
            "footnote_segment": "chp-6:06_CHP-6_sec_i:l120-157",
            "footnote_marker": 4,
            "footnote_body_link_status": "linked",
            "linked_body_statement_ids": ["st-chp6-p155-lorenzo-commissions-claude"],
            "related_segment": "chp-6:06_CHP-6_sec_i:l102-110",
            "related_source_lines": [107],
            "relation_candidate": False,
            "relation_candidate_note": "This is a general claim about the literature, not a directed relation between the family and a specific cited work.",
        },
        "original_quote": source_lines[153],
        "origin": "book",
        "source_file": "02-sources/02-Markdown/06_CHP-6_sec_i.md",
    }

    body = out["st-chp6-p155-lorenzo-commissions-claude"]
    bq_body = body["qualifiers"]
    old_note4 = "st-chp6-p155-note4-bibliographic-continuation"
    bq_body["footnote_source_lines"] = [154, 110]
    bq_body["footnote_statement_ids"] = [claim_id, old_note4, "st-chp6-notes-l110-p155-n4-bellori-citation"]
    bq_body["footnote_citation_statement_ids"] = [old_note4, "st-chp6-notes-l110-p155-n4-bellori-citation"]

    for sid, row in out.items():
        q = row.get("qualifiers", {})
        if q.get("relation_candidate") is not True:
            raise SystemExit(f"expected relation candidate missing for {sid}")
    for sid, row in [("n3-corti", corti), ("n4-bellori", bellori)]:
        if row["subject_candidate_id"] != BOOK_ID or not row["object_candidate_id"]:
            raise SystemExit(f"new citation endpoints invalid: {sid}")

    lines = original.decode("utf-8").splitlines()
    output_lines: list[str] = []
    seen = set()
    inserted: set[str] = set()
    rows_by_id = {**by_id, **out}
    for raw in lines:
        if not raw.strip():
            output_lines.append(raw)
            continue
        row = json.loads(raw)
        sid = row.get("statement_id")
        if sid in out:
            seen.add(sid)
            row = out[sid]
            output_lines.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            if sid == note3_id:
                output_lines.append(json.dumps(corti, ensure_ascii=False, separators=(",", ":")))
                inserted.add(corti["statement_id"])
            if sid == n4_id:
                output_lines.append(json.dumps(bellori, ensure_ascii=False, separators=(",", ":")))
                inserted.add(bellori["statement_id"])
            continue
        output_lines.append(raw)
    output_lines.append(json.dumps(claim, ensure_ascii=False, separators=(",", ":")))

    if seen != target_ids or inserted != {corti["statement_id"], bellori["statement_id"]}:
        raise SystemExit("write coverage mismatch")
    result = ("\n".join(output_lines) + "\n").encode("utf-8")
    print(f"preflight passed: existing_rows={len(target_ids)} new_statements=3 input_sha256={current_sha}")
    print("citation candidates: 7; standalone note claims: 1 (relation_candidate=false)")
    print("all cited archives, family subject, source spans, note links and candidate mentions exist")
    if not args.apply:
        print("dry-run only; table unchanged")
        return

    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")
    shutil.copy2(TABLE, BACKUP)
    fd, temp_name = tempfile.mkstemp(prefix=TABLE.name + ".", suffix=".tmp", dir=TABLE.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(result)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_name, TABLE)
    except Exception:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
        raise
    print(f"applied: backup={BACKUP.relative_to(ROOT)} output_sha256={digest(result)}")


if __name__ == "__main__":
    main()
