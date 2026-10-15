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
PAGE = ROOT / ".tmp_s2_ch3_phys18-18.png"
SEGMENT = "chp-3:03_CHP-3_sec_ii:l137-142"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp3-sec-ii-l137-142-relations-20261010")
EXPECTED_HASHES = {
    TABLE: "2dbbd28ffabb45cca3800a30cca33e0044c84f8d3d0adef67f7b5e15b8bf2900",
    CANDIDATES: "1c36e0fa29ea9f353eb8ac121ede84eca7414b08b122fa3afb5ea09b4d54789e",
    COVERAGE: "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "cb17a400fc5a79d895e31fe4a112c83e010f5e5b859883852b3985b7010eb1e6",
    PDF: "362e08518334ae5cda65cc1758f92ef4de6874b5982bfb6600187d889dc6785d",
    PAGE: "b8c9b0696003334ddc7ba7779fb6f8aeee8af50324df9ce2111faeb1fe84b09f",
}
TRUE_NOTES = {
    "st-chp3-secii-l137-142-borromini-barocci-sensibility": "Haskell explicitly compares Borromini and Barocci as interpreters of the same specified sensibility; this is a source comparison, not a biographical association.",
    "st-chp3-secii-l137-142-oratorian-intention": "Haskell infers that the Oratorians deliberately hoped for Borromini because the Trinitarian brothers admired his revolutionary qualities; retain the inference as Haskell's.",
    "st-chp3-secii-l137-142-oratorian-sensibility-contribution": "Haskell attributes this strain of Counter Reformation sensibility to the Oratorians and contrasts it with the Jesuits.",
    "st-chp3-secii-l137-142-oratorio-design-known-plans": "Haskell says Borromini was asked to design the Oratorio in 1637 and that his Scalzi church plans were already known.",
    "st-chp3-secii-l137-142-scalzi-plan-quotation": "The Scalzi explicitly describe the plan of their church as exceptional and unmatched; retain the quotation's speaker and its later date as reported by Haskell.",
    "st-chp3-secii-l137-142-scalzi-satisfaction": "Haskell says Borromini's originality and cheapness caused special satisfaction to the Scalzi.",
    "st-chp3-secii-l137-142-site-solution-praise": "Haskell attributes a great measure of Borromini's praise to the ingenuity with which he solved the site's problems.",
    "st-chp3-secii-l137-142-style-departure": "Haskell says the church style marked a radical departure from anything previously seen in Rome.",
    "st-chp3-secii-l137-142-trinitarian-admiration": "Haskell reports that the Trinitarian brothers found Borromini admirable for his revolutionary qualities.",
}
FALSE_NOTES = {
    "st-chp3-secii-l137-142-facade-curves": "This is an aesthetic description: the façade's broken curves match the emotional tone of unspecified music played inside. The current church endpoint only supplies context and does not make the claim a relation between the façade and the church; do not invent a separate music entity.",
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


def encode_jsonl(rows: list[dict], raw: bytes) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    prefix = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    return prefix + b"".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + newline for row in rows
    )


def atomic_write(path: Path, payload: bytes) -> None:
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as handle:
            handle.write(payload)
            temp_path = Path(handle.name)
        os.replace(temp_path, path)
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="apply reviewed S2 relation classifications")
    args = parser.parse_args()
    for path, expected in EXPECTED_HASHES.items():
        require(path.exists() and digest(path) == expected, f"preflight hash changed for {path.relative_to(ROOT)}")
    require(not BACKUP.exists(), "a recovery backup already exists")

    raw = TABLE.read_bytes()
    statements = read_jsonl(TABLE)
    require(len(statements) == 12750 and len({r["statement_id"] for r in statements}) == len(statements), "statement table state changed")
    by_id = {row["statement_id"]: row for row in statements}
    segment_rows = [row for row in statements if row.get("segment_id") == SEGMENT]
    expected_ids = set(TRUE_NOTES) | set(FALSE_NOTES)
    require({r["statement_id"] for r in segment_rows} == expected_ids and len(segment_rows) == 10, "L137–142 statement set changed")
    require(all((r.get("qualifiers") or {}).get("relation_candidate") is None for r in segment_rows), "L137–142 has pre-classified statements")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[136:142])
    require("highly ingenious manner" in segment_text and "the more rough-and-ready spirits of the Jesuits" in segment_text, "source text changed")
    require(all(normalized(r.get("original_quote", "")) in normalized(segment_text) for r in segment_rows), "a statement quote no longer matches the source segment")
    manifest = {r["segment_id"]: r for r in read_jsonl(SEGMENTS)}.get(SEGMENT)
    require(manifest and (manifest.get("source_file"), manifest.get("line_start"), manifest.get("line_end")) == ("02-sources/02-Markdown/03_CHP-3_sec_ii.md", 137, 142), "S0 segment boundary changed")
    with COVERAGE.open(encoding="utf-8-sig", newline="") as handle:
        coverage = next((r for r in csv.DictReader(handle) if r["segment_id"] == SEGMENT), None)
    require(coverage and (coverage["disposition"], coverage["migration_status"]) == ("reviewed", "complete"), "S2 coverage is not complete")

    candidates = {r["candidate_id"] for r in csv.DictReader(CANDIDATES.open(encoding="utf-8-sig", newline=""))}
    require(all(r.get("subject_candidate_id") in candidates and r.get("object_candidate_id") in candidates for r in segment_rows), "a statement endpoint is missing")
    for statement_id, note in TRUE_NOTES.items():
        q = dict(by_id[statement_id].get("qualifiers") or {})
        q.update(relation_candidate=True, relation_candidate_note=note)
        by_id[statement_id]["qualifiers"] = q
    for statement_id, note in FALSE_NOTES.items():
        q = dict(by_id[statement_id].get("qualifiers") or {})
        q.update(relation_candidate=False, relation_candidate_note=note)
        by_id[statement_id]["qualifiers"] = q

    bilateral = [r for r in statements if r.get("subject_candidate_id") and r.get("object_candidate_id")]
    flag = lambda r: (r.get("qualifiers") or {}).get("relation_candidate")
    b_true = sum(flag(r) is True for r in bilateral)
    b_false = sum(flag(r) is False for r in bilateral)
    b_pending = sum(flag(r) is None for r in bilateral)
    relation_total = sum(flag(r) is True for r in statements)
    relation_open = sum(flag(r) is True and not (r.get("subject_candidate_id") and r.get("object_candidate_id")) for r in statements)
    require((len(statements), len(bilateral), b_true, b_false, b_pending, relation_total, relation_open) == (12750, 8543, 4775, 475, 3293, 4824, 49), "projected whole-book totals differ")
    segment_after = [r for r in statements if r.get("segment_id") == SEGMENT]
    seg_true = sum(flag(r) is True for r in segment_after)
    seg_false = sum(flag(r) is False for r in segment_after)
    seg_pending = sum(flag(r) is None for r in segment_after)
    require((len(segment_after), seg_true, seg_false, seg_pending) == (10, 9, 1, 0), "projected segment totals differ")
    payload = encode_jsonl(statements, raw)
    report = {
        "action": "apply" if args.apply else "dry-run",
        "segment_id": SEGMENT,
        "relation_candidates": seg_true,
        "nonrelations": seg_false,
        "unclassified": seg_pending,
        "bilateral_after": {"total": len(bilateral), "relation_candidates": b_true, "nonrelations": b_false, "unclassified": b_pending},
        "relation_candidates_total": relation_total,
        "relation_candidates_open": relation_open,
        "post_write_sha256": hashlib.sha256(payload).hexdigest(),
    }
    print(json.dumps(report, ensure_ascii=True, indent=2))
    if not args.apply:
        print("Dry run only. Pass --apply to write.")
        return

    shutil.copy2(TABLE, BACKUP)
    try:
        atomic_write(TABLE, payload)
        saved = read_jsonl(TABLE)
        saved_by_id = {r["statement_id"]: r for r in saved}
        require(len(saved) == 12750 and all((saved_by_id[sid].get("qualifiers") or {}).get("relation_candidate") is True for sid in TRUE_NOTES), "post-write true classifications differ")
        require(all((saved_by_id[sid].get("qualifiers") or {}).get("relation_candidate") is False for sid in FALSE_NOTES), "post-write false classifications differ")
        require(digest(TABLE) == hashlib.sha256(payload).hexdigest(), "post-write hash differs")
    except Exception:
        if BACKUP.exists():
            shutil.copy2(BACKUP, TABLE)
        raise
    report["result"] = "applied"
    report["backup"] = str(BACKUP.relative_to(ROOT))
    report["sha256_after"] = digest(TABLE)
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
