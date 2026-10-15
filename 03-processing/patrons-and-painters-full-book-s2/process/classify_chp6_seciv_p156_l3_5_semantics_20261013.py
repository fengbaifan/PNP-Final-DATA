from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "06_CHP-6_sec_iv.md"
SOURCE_FILE = "02-sources/02-Markdown/06_CHP-6_sec_iv.md"
SEGMENT = "chp-6:06_CHP-6_sec_iv:l3-5"
BACKUP_SUFFIX = ".bak-s2-chp6-seciv-p156-l3-5-semantics-20261013"

EXPECTED_HASHES = {
    SOURCE: "65de7b08cd2bad4cbf783d807160ef15e80cb031a47e1f28a6cb6c0f2b29e775",
    STATEMENTS: "20371e3097ee51f9c4564d50e40ca0e91018a1bf1c9c919602743afd2b4bd5eb",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    COVERAGE: "0d260baba0651c22d9d45ee7d3362485c44e30fc809cb09c6b56520fd5355611",
}

TARGETS = {
    "st-chp6-p156-seciv-patronage-decline",
    "st-chp6-p156-seciv-massimi-exception",
    "st-chp6-p156-seciv-effetti-characterization",
    "st-chp6-p156-seciv-effetti-pictures-disappeared",
    "st-chp6-p156-seciv-effetti-taste-fragment",
}

TRUE_NOTE = (
    "Retain this source-grounded person–collection status as an S2 relation "
    "candidate. The collection type and boundaries remain unresolved; no "
    "individual picture is identified, and no S6 edge is created."
)
FALSE_NOTE = (
    "This is a general, evaluative, or epistemic statement rather than a "
    "specific entity relation candidate."
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path):
    raw = path.read_bytes()
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader), raw.startswith(b"\xef\xbb\xbf")


def csv_bytes(fields, rows, bom):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\r\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return (b"\xef\xbb\xbf" if bom else b"") + stream.getvalue().encode("utf-8")


def atomic_write(path: Path, data: bytes):
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def build_outputs():
    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        if sha256(raw[path]) != expected:
            raise SystemExit(f"input SHA mismatch: {path.relative_to(ROOT)}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    statements = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("duplicate statement IDs")
    unset = {
        sid for sid, row in by_id.items()
        if row.get("segment_id") == SEGMENT and row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if unset != TARGETS:
        raise SystemExit(f"p.156 sec_iv unset target set changed: {sorted(unset ^ TARGETS)}")

    _, candidates, _ = read_csv(CANDIDATES)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    for cid in {"cand-1564", "cand-5974", "cand-6345", "cand-6389", "cand-6405"}:
        if cid not in candidate_by_id:
            raise SystemExit(f"required p.156 candidate missing: {cid}")

    def classify(sid, relation, note, *, ocr_correction=None):
        row = by_id[sid]
        q = row.setdefault("qualifiers", {})
        q["relation_candidate"] = relation
        q["relation_candidate_note"] = note
        if ocr_correction:
            q["ocr_correction"] = ocr_correction
        return row

    classify(
        "st-chp6-p156-seciv-patronage-decline", False,
        "Haskell’s contrast between surviving grand schemes and declining contemporary-art patronage is a broad historical interpretation, not a specific entity relation.",
    )
    classify(
        "st-chp6-p156-seciv-massimi-exception", False,
        "The contrast between Massimi and an unnamed group of literary collectors is contextual characterization; the group is not treated as a named entity or formal endpoint.",
        ocr_correction="S0 has a leading hyphen before 'Cardinal Massimi'; print p.156 begins the sentence without it. S0 is unchanged.",
    )
    classify(
        "st-chp6-p156-seciv-effetti-characterization", False,
        "Haskell’s superlative and the occupational descriptions 'antiquarian' and 'local historian' are person characterization, not a specific entity relation.",
    )
    classify(
        "st-chp6-p156-seciv-effetti-pictures-disappeared", True, TRUE_NOTE,
    )
    classify(
        "st-chp6-p156-seciv-effetti-taste-fragment", False,
        "This records Haskell’s epistemic claim about the only stated basis for knowing Antonio’s taste. The explicit person-to-catalogue authorship relation is handled with the linked p.157 continuation, not inferred from the footnote’s distinct manuscript inventory.",
    )

    for sid in TARGETS:
        row = by_id[sid]
        q = row["qualifiers"]
        start = int(q["source_line_start"])
        end = int(q["source_line_end"])
        if start != end or row["original_quote"] not in source_lines[start - 1]:
            raise SystemExit(f"source anchor changed: {sid}")
        refs = set(q.get("mentioned_candidate_ids", []))
        endpoints = {row.get("subject_candidate_id"), row.get("object_candidate_id")} - {None, ""}
        if not (refs | endpoints) <= set(candidate_by_id):
            raise SystemExit(f"candidate reference missing: {sid}")

    # Confirm the cross-page statement and footnote remain linked to existing rows.
    taste = by_id["st-chp6-p156-seciv-effetti-taste-fragment"]["qualifiers"]
    if taste.get("continued_by_statement_id") != "st-chp6-p157-catalogue-continuation":
        raise SystemExit("p.156 taste fragment continuation target changed")
    if taste.get("footnote_link_status") != "linked" or taste.get("footnote_pending") is not False:
        raise SystemExit("p.156 note 2 backlink changed")

    coverage_fields, coverage, coverage_bom = read_csv(COVERAGE)
    cov = next((row for row in coverage if row["segment_id"] == SEGMENT), None)
    if not cov or (cov["disposition"], cov["migration_status"]) != ("reviewed", "complete"):
        raise SystemExit(f"unexpected p.156 segment coverage state: {cov}")
    cov["note"] = (
        "印刷p.156正文L3–5已完成语义分类：赞助衰退、Massimi对比、Antonio人物特征及taste证据范围为非关系陈述；"
        "图片群组消失保留为带开放集合类型的S2候选。L4行首OCR连字符据印本记校，S0不改；L5跨页续句与p.157 L56保持互链，"
        "注2双向回链至本段与sec_i注释行L157。"
    )

    segment_rows = [row for row in statements if row.get("segment_id") == SEGMENT]
    true_count = sum(row["qualifiers"].get("relation_candidate") is True for row in segment_rows)
    false_count = sum(row["qualifiers"].get("relation_candidate") is False for row in segment_rows)
    unset_count = sum(row["qualifiers"].get("relation_candidate") is None for row in segment_rows)
    if (len(segment_rows), true_count, false_count, unset_count) != (5, 1, 4, 0):
        raise SystemExit(f"unexpected p.156 sec_iv totals: {(len(segment_rows), true_count, false_count, unset_count)}")

    outputs = {
        STATEMENTS: ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in statements) + "\n").encode("utf-8"),
        COVERAGE: csv_bytes(coverage_fields, coverage, coverage_bom),
    }
    summary = {
        "segment": SEGMENT,
        "classified_statements": len(TARGETS),
        "relation_candidates": true_count,
        "non_relational": false_count,
        "unset": unset_count,
        "source_correction": "L4 leading hyphen before Cardinal Massimi; print has none; S0 unchanged",
        "cross_page_taste_relation": "epistemic claim classified here; explicit catalogue authorship remains linked to p.157 continuation",
        "mode": "dry-run",
    }
    return outputs, summary


def main():
    parser = argparse.ArgumentParser(description="Classify p.156 sec_iv S2 statements with protected writes.")
    parser.add_argument("--apply", action="store_true", help="Back up and apply the reviewed p.156 batch.")
    args = parser.parse_args()
    outputs, summary = build_outputs()
    summary["mode"] = "apply" if args.apply else "dry-run"
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not args.apply:
        return
    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in outputs}
    if any(path.exists() for path in backups.values()):
        raise SystemExit("backup already exists; refusing to overwrite")
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    for path, data in outputs.items():
        atomic_write(path, data)
    print("APPLIED; backups:")
    for backup in backups.values():
        print(backup.relative_to(ROOT))


if __name__ == "__main__":
    main()
