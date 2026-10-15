from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
COVERAGE = ROOT / "04-knowledge/tables/s2-coverage.csv"
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/03_CHP-3_sec_ii.md"
PDF = ROOT / "02-sources/01-book/CHP-3.pdf"
PROCESS = ROOT / "03-processing/patrons-and-painters-full-book-s2/process/stages.md"
SEGMENT = "chp-3:03_CHP-3_sec_ii:l102-113"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp3-sec-ii-l102-113-relations-20261010")

HASHES = {
    TABLE: "ef3da8f75b4c3e1d595e0a02eecf63148357fd98a1e1eadd1a584661ae466aa2",
    CANDIDATES: "badce6cd43479d2e8a6aabcbfb2c11fb0d5103856c1f109459c8923067ae9374",
    COVERAGE: "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "cb17a400fc5a79d895e31fe4a112c83e010f5e5b859883852b3985b7010eb1e6",
    PDF: "362e08518334ae5cda65cc1758f92ef4de6874b5982bfb6600187d889dc6785d",
}

DECISIONS = {
    "st-chp3-secii-l102-113-church-funding": (
        "cand-3073", "cand-3967", "pledged_funds_for", True,
        "The passage explicitly says Ludovisi laid down 100,000 scudi for the church; the superlative remains Haskell's assessment.",
    ),
    "st-chp3-secii-l102-113-church-plan": (
        "cand-3073", "cand-3967", "decided_to_build", True,
        "The passage explicitly attributes the decision to build the Jesuit church to Ludovisi.",
    ),
    "st-chp3-secii-l102-113-competition-organized": (
        "cand-3073", "cand-5083", "organized", True,
        "Haskell explicitly says all sources agree that Ludovisi organized the architectural competition.",
    ),
    "st-chp3-secii-l102-113-conclave-opposition": (
        "cand-3073", "cand-3104", "attempted_to_prevent_election_of", True,
        "The passage explicitly reports Ludovisi's attempt to prevent Maffeo Barberini's election in 1623.",
    ),
    "st-chp3-secii-l102-113-construction-start": (
        "cand-3967", None, "construction_began", False,
        "The 1626 date is a construction-time property of the church; this row has no distinct event or relation endpoint.",
    ),
    "st-chp3-secii-l102-113-domenichino-submitted": (
        "cand-3024", "cand-5083", "participated_in", True,
        "Haskell explicitly names Domenichino among those who submitted plans to the competition.",
    ),
    "st-chp3-secii-l102-113-farnese-instructions": (
        "cand-3403", "cand-0995", "followed_instructions_of", True,
        "The passage explicitly contrasts Jesuits' earlier acceptance of Cardinal Farnese's instructions with the later situation.",
    ),
    "st-chp3-secii-l102-113-initial-site": (
        "cand-3967", "cand-5080", "planned_near", True,
        "The passage explicitly places Ludovisi's first church plan near the novitiate of S. Andrea.",
    ),
    "st-chp3-secii-l102-113-jesuit-difficulties": (
        "cand-3073", "cand-3403", "conflict_with", True,
        "Haskell explicitly locates Ludovisi's subsequent difficulties with the Jesuits.",
    ),
    "st-chp3-secii-l102-113-ludovisi-collection": (
        "cand-3073", "cand-5075", "assembled_collection", True,
        "The passage says Ludovisi built up the collection; the collection's superlative remains Haskell's assessment.",
    ),
    "st-chp3-secii-l102-113-ludovisi-death": (
        "cand-3073", None, "died", False,
        "Death in 1632 and age 37 are biographical time/age attributes, not an inter-entity relation.",
    ),
    "st-chp3-secii-l102-113-ludovisi-estates": (
        "cand-3073", "cand-3126", "estates_located_in", True,
        "The passage explicitly locates Ludovisi's accumulated estates in and around Rome.",
    ),
    "st-chp3-secii-l102-113-ludovisi-explanation": (
        "cand-3073", "cand-3403", "explained_admiration_by", True,
        "This is a source-attributed relation of Ludovisi's expressed admiration for the Jesuits, not an independently verified motive.",
    ),
    "st-chp3-secii-l102-113-ludovisi-protege": (
        "cand-3024", "cand-3073", "protected_by", True,
        "Haskell explicitly describes Domenichino as Ludovisi's special protégé.",
    ),
    "st-chp3-secii-l102-113-ludovisi-spain": (
        "cand-3073", "cand-4591", "acted_in_interest_of", True,
        "The passage explicitly says Ludovisi acted in the interests of Spain; his political prominence remains source context.",
    ),
    "st-chp3-secii-l102-113-passeri-testimony": (
        "cand-3024", "cand-5083", "participated_in", True,
        "Passeri's quoted account says Domenico competed; preserve this attribution and Passeri's stated reticence.",
    ),
    "st-chp3-secii-l102-113-pope-health": (
        "cand-3061", None, "described_as", False,
        "Age and ill-health are attributes of Gregory XV, not an inter-entity relation.",
    ),
    "st-chp3-secii-l102-113-pope-objection": (
        "cand-3061", "cand-3967", "objected_to", True,
        "The passage explicitly reports Gregory XV's objection to the proposed church's height and placement.",
    ),
    "st-chp3-secii-l102-113-relocation": (
        "cand-3967", "cand-5082", "relocated_next_to", True,
        "The passage says the proposed church was moved next to Collegio Romano; the two places remain distinct.",
    ),
    "st-chp3-secii-l102-113-return-order": (
        "cand-3073", "cand-5079", "ordered_to_return_to", True,
        "The passage explicitly states Ludovisi was ordered to return to his archbishopric; it does not identify who issued the order.",
    ),
    "st-chp3-secii-p73-note2-corsini-ms": (
        None, "cand-5129", "footnote_citation", True,
        "Haskell's footnote explicitly cites this manuscript. The source book cand-2962 is the citing endpoint; authorship and manuscript contents remain unverified.",
    ),
}

ALREADY_CLASSIFIED = {
    "st-chp3-secii-l102-113-aurora-created",
    "st-chp3-secii-l102-113-aurora-location",
    "st-chp3-secii-l102-113-casino-purchase",
    "st-chp3-secii-l102-113-ludovisi-emilia-patronage",
    "st-chp3-secii-l102-113-ludovisi-nephew",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def normalized(value: str) -> str:
    return " ".join(value.split())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="apply reviewed S2 relation classifications")
    args = parser.parse_args()
    for path, expected in HASHES.items():
        require(digest(path) == expected, f"preflight hash changed for {path.relative_to(ROOT)}")
    require(not BACKUP.exists(), "recovery backup already exists; refusing to overwrite it")

    raw = TABLE.read_bytes()
    rows = read_jsonl(TABLE)
    require(len(rows) == 12748, "unexpected statement row count")
    require(len({row["statement_id"] for row in rows}) == len(rows), "duplicate statement_id")
    by_id = {row["statement_id"]: row for row in rows}
    segment_rows = [row for row in rows if row.get("segment_id") == SEGMENT]
    require(len(segment_rows) == 26, f"expected 26 statements for L102–113, found {len(segment_rows)}")
    require({row["statement_id"] for row in segment_rows if (row.get("qualifiers") or {}).get("relation_candidate") is None} == set(DECISIONS), "unclassified statement set changed")
    require({row["statement_id"] for row in segment_rows if (row.get("qualifiers") or {}).get("relation_candidate") is True} == ALREADY_CLASSIFIED, "already-classified statement set changed")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    manifest = {row["segment_id"]: row for row in read_jsonl(SEGMENTS)}.get(SEGMENT)
    require(manifest is not None and (manifest.get("source_file"), manifest.get("line_start"), manifest.get("line_end")) == ("02-sources/02-Markdown/03_CHP-3_sec_ii.md", 102, 113), "S0 segment boundary changed")
    segment_text = "\n".join(source_lines[101:113])
    for statement_id, (subject, obj, predicate, decision, note) in DECISIONS.items():
        row = by_id.get(statement_id)
        require(row is not None and row.get("segment_id") == SEGMENT, f"target statement missing: {statement_id}")
        require((row.get("subject_candidate_id"), row.get("object_candidate_id"), row.get("predicate")) == (subject, obj, predicate), f"endpoint or predicate changed: {statement_id}")
        quote = normalized(row.get("original_quote", ""))
        require(quote and quote in normalized(segment_text), f"source quote no longer matches S0 segment: {statement_id}")
        require((row.get("qualifiers") or {}).get("relation_candidate") is None, f"target already classified: {statement_id}")

    with COVERAGE.open(encoding="utf-8-sig", newline="") as handle:
        coverage = list(csv.DictReader(handle))
    coverage_row = next((row for row in coverage if row["segment_id"] == SEGMENT), None)
    require(coverage_row is not None and (coverage_row["disposition"], coverage_row["migration_status"]) == ("reviewed", "complete"), "coverage is not complete")
    coverage_note = coverage_row.get("note", "")
    require("print-p.73 body" in coverage_note and "visual footnotes 2-4" in coverage_note, "target coverage note changed")
    process_text = PROCESS.read_text(encoding="utf-8-sig")
    require("L102–113核对`CHP-3.pdf`物理页15" in process_text, "existing page-image comparison is not recorded in the process log")

    candidates = {row["candidate_id"]: row for row in csv.DictReader(CANDIDATES.open(encoding="utf-8-sig", newline=""))}
    for candidate_id in ("cand-2962", "cand-5129"):
        require(candidate_id in candidates, f"citation endpoint missing: {candidate_id}")
    require(candidates["cand-2962"].get("canonical_name") == "《赞助人与画家》", "citing book candidate changed")
    require(candidates["cand-5129"].get("suggested_type") == "archive", "cited manuscript candidate type changed")

    for statement_id, (subject, obj, predicate, decision, note) in DECISIONS.items():
        row = by_id[statement_id]
        if statement_id == "st-chp3-secii-p73-note2-corsini-ms":
            row["subject_candidate_id"] = "cand-2962"
            q = dict(row.get("qualifiers") or {})
            require(q.get("footnote_marker") == 2 and q.get("cited_source_candidate_id") == "cand-5129", "footnote citation anchor changed")
        else:
            q = dict(row.get("qualifiers") or {})
        q["relation_candidate"] = decision
        q["relation_candidate_note"] = note
        row["qualifiers"] = q

    bilateral = [row for row in rows if row.get("subject_candidate_id") and row.get("object_candidate_id")]
    bilateral_true = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in bilateral)
    bilateral_false = sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in bilateral)
    bilateral_pending = sum((row.get("qualifiers") or {}).get("relation_candidate") is None for row in bilateral)
    relation_total = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in rows)
    relation_open = sum((row.get("qualifiers") or {}).get("relation_candidate") is True and not (row.get("subject_candidate_id") and row.get("object_candidate_id")) for row in rows)
    require((bilateral_true, bilateral_false, bilateral_pending, relation_total, relation_open) == (4722, 473, 3342, 4771, 49), "unexpected projected whole-book totals")
    segment_counts = {
        "statements": len(segment_rows),
        "relation_candidates": sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in segment_rows),
        "nonrelations": sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in segment_rows),
        "unclassified": sum((row.get("qualifiers") or {}).get("relation_candidate") is None for row in segment_rows),
    }
    require(segment_counts == {"statements": 26, "relation_candidates": 23, "nonrelations": 3, "unclassified": 0}, "unexpected segment classification totals")

    bom = raw.startswith(b"\xef\xbb\xbf")
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    encoded_rows = []
    for index, row in enumerate(rows):
        encoded = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if index == 0 and bom:
            encoded = b"\xef\xbb\xbf" + encoded
        encoded_rows.append(encoded + newline)
    payload = b"".join(encoded_rows)
    result = {
        "action": "apply" if args.apply else "dry-run",
        "segment_id": SEGMENT,
        "classified_statement_ids": list(DECISIONS),
        "citation_source_endpoint": "cand-2962",
        "segment_after": segment_counts,
        "bilateral_after": {"relation_true": bilateral_true, "relation_false": bilateral_false, "unclassified": bilateral_pending},
        "relation_candidates_total": relation_total,
        "relation_candidates_open": relation_open,
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not args.apply:
        print("Dry run only. Pass --apply to write.")
        return

    shutil.copy2(TABLE, BACKUP)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(dir=TABLE.parent, prefix=TABLE.name + ".s2tmp-", delete=False) as handle:
            handle.write(payload)
            temp_path = Path(handle.name)
        os.replace(temp_path, TABLE)
        written = read_jsonl(TABLE)
        written_by_id = {row["statement_id"]: row for row in written}
        require(len(written) == 12748, "post-write statement count changed")
        require(all((written_by_id[sid].get("qualifiers") or {}).get("relation_candidate") is decision for sid, (_, _, _, decision, _) in DECISIONS.items()), "post-write classification readback failed")
        citation = written_by_id["st-chp3-secii-p73-note2-corsini-ms"]
        require(citation.get("subject_candidate_id") == "cand-2962" and citation.get("object_candidate_id") == "cand-5129", "post-write citation endpoints failed")
        require(digest(TABLE) == hashlib.sha256(payload).hexdigest(), "post-write SHA mismatch")
    except Exception:
        if temp_path and temp_path.exists():
            temp_path.unlink()
        shutil.copy2(BACKUP, TABLE)
        raise
    result["result"] = "applied"
    result["backup"] = str(BACKUP.relative_to(ROOT))
    result["sha256_after"] = digest(TABLE)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
