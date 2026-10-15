from __future__ import annotations

import argparse
import copy
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
MENTIONS = TABLES / "mentions.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "06_CHP-6_sec_iv.md"
SOURCE_FILE = "02-sources/02-Markdown/06_CHP-6_sec_iv.md"
SEGMENT = "chp-6:06_CHP-6_sec_iv:l7-10"
BACKUP_SUFFIX = ".bak-s2-chp6-seciv-p157-l7-10-semantics-20261013"

EXPECTED_HASHES = {
    SOURCE: "65de7b08cd2bad4cbf783d807160ef15e80cb031a47e1f28a6cb6c0f2b29e775",
    STATEMENTS: "eca74d4685ae3ef0442865f9097d8d7dfb4e252c538bc42e651815db7685798d",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    COVERAGE: "15bb6cc1d466e7483ff80d9471abe5a8786223ff82f6eed7f33f46a8736f74a9",
}

TARGETS = {
    "st-chp6-p157-collection-accessibility-interpretation",
    "st-chp6-p157-cortona-single-picture",
    "st-chp6-p157-gallery-literary-interest",
    "st-chp6-p157-maratta-single-picture",
    "st-chp6-p157-marucelli-introduction-partial",
    "st-chp6-p157-modest-artists-and-claims",
    "st-chp6-p157-other-represented-painters",
    "st-chp6-p157-pinax-english-version-note",
}

TRUE_NOTE = (
    "This is a source-grounded S2 relation candidate. Preserve the source "
    "attribution and qualifications; no formal S6 edge is created."
)
FALSE_NOTE = (
    "This is an evaluative, inferential, descriptive, or epistemic claim "
    "rather than a specific entity relation candidate."
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


def add_candidate_row(base, statement_id, *, subject, object_, predicate, claim, quote, qualification,
                      mentioned, source_line, extra=None):
    row = copy.deepcopy(base)
    row["statement_id"] = statement_id
    row["subject_candidate_id"] = subject
    row["object_candidate_id"] = object_
    row["predicate"] = predicate
    row["original_quote"] = quote
    q = row.setdefault("qualifiers", {})
    q.update({
        "source_line_start": source_line,
        "source_line_end": source_line,
        "printed_page": "157",
        "pdf_physical_page": 12,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "authorial historical account",
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": True,
        "relation_candidate_note": TRUE_NOTE,
    })
    if extra:
        q.update(extra)
    return row


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
        raise SystemExit(f"p.157 unset target set changed: {sorted(unset ^ TARGETS)}")

    _, candidates, _ = read_csv(CANDIDATES)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    required_candidates = {
        "cand-2962", "cand-5974", "cand-6389", "cand-0342", "cand-1526", "cand-6390",
        "cand-6406", "cand-6407", "cand-1098", "cand-0084", "cand-4652", "cand-1554",
        "cand-3397", "cand-6408",
    }
    missing = required_candidates - set(candidate_by_id)
    if missing:
        raise SystemExit(f"required p.157 candidate missing: {sorted(missing)}")
    if candidate_by_id["cand-6407"]["suggested_type"] != "archive":
        raise SystemExit("English version candidate type changed")

    mention_fields, mentions, mention_bom = read_csv(MENTIONS)
    segment_text = "\n".join(source_lines[6:10])
    segment_mentions = [row for row in mentions if row["segment_id"] == SEGMENT]
    for row in segment_mentions:
        start, end = int(row["start_char"]), int(row["end_char"])
        if segment_text[start:end] != row["surface_form"]:
            raise SystemExit(f"p.157 mention span changed: {row['mention_id']}")

    def classify(sid, relation, note, *, extra=None):
        row = by_id[sid]
        q = row.setdefault("qualifiers", {})
        q["relation_candidate"] = relation
        q["relation_candidate_note"] = note
        if extra:
            q.update(extra)
        return row

    classify(
        "st-chp6-p157-collection-accessibility-interpretation", False,
        "This is Haskell’s economic inference from reputation and dimensions. Its antecedent combines painters and pictures, so it does not establish a determinate person-to-work relation.",
    )
    classify(
        "st-chp6-p157-cortona-single-picture", True,
        "The collection’s reported one-picture representation of Cortona is a source-grounded candidate; the individual picture is not identified.",
    )
    classify(
        "st-chp6-p157-gallery-literary-interest", True,
        "This records Haskell’s source-attributed account of Antonio’s interest in the literary possibilities of his gallery; it is not independent evidence of private motive.",
    )
    classify(
        "st-chp6-p157-maratta-single-picture", True,
        "The collection’s reported one-picture representation of Maratta is a source-grounded candidate; the individual picture is not identified.",
    )
    classify(
        "st-chp6-p157-marucelli-introduction-partial", False,
        "This introduces Marucelli through descriptive attributes. The separate residence relation is preserved in the linked p.158 continuation; 'Florentine' alone does not establish birthplace.",
    )
    classify(
        "st-chp6-p157-modest-artists-and-claims", False,
        "This is Haskell’s evaluative and inferential assessment of the artists and Antonio’s claims, not a specific entity relation.",
    )

    # Recast the mixed artist list as two named collection-to-artist relations and an open Flemish-group claim.
    original = by_id["st-chp6-p157-other-represented-painters"]
    source_line = source_lines[7]
    quote_gagliardi = "The' others were' meri like' Bernardino Gagliardi"
    quote_allegrini = "The' others were' meri like' Bernardino Gagliardi, Francesco' Allegrini"
    quote_flemish = "and; above all, a great number of Flemish artists."
    for quote in (quote_gagliardi, quote_allegrini, quote_flemish):
        if quote not in source_line:
            raise SystemExit(f"source quote missing from p.157 L8: {quote}")

    original["subject_candidate_id"] = "cand-6389"
    original["object_candidate_id"] = None
    original["predicate"] = "collection_includes_unnamed_flemish_artists"
    original["original_quote"] = quote_flemish
    q = original.setdefault("qualifiers", {})
    q.update({
        "claim": "Haskell says a great number of Flemish artists were among the other painters represented in Antonio degli Effetti’s collection.",
        "qualification": "The group is described only as 'a great number of Flemish artists'; individual members and a group identity are not supplied. The existing Flemish mention identifies a regional descriptor, not an artist-group endpoint.",
        "mentioned_candidate_ids": ["cand-6389", "cand-4652"],
        "relation_candidate": True,
        "relation_candidate_note": "This is a source-grounded open S2 collection-content candidate; the unnamed collective remains an open endpoint and is not conflated with Flanders as a place.",
        "open_endpoint_reason": "The represented Flemish artists are unnamed as a group and no individual members are identified in this clause; retain the source-defined open endpoint without creating a false place-to-person mapping.",
        "pdf_print_corrections": ["Print p.157 reads 'The others were men like Bernardino Gagliardi, Francesco Allegrini and, above all'; S0 OCR punctuation/spelling is retained."],
    })
    extra_rows = [
        add_candidate_row(
            original, "st-chp6-p157-collection-includes-work-by-gagliardi",
            subject="cand-6389", object_="cand-1098", predicate="collection_includes_work_by",
            claim="Haskell names Bernardino Gagliardi among the other painters represented in Antonio degli Effetti’s collection.",
            quote=quote_gagliardi,
            qualification="The source gives Gagliardi as an example, not a complete roster; no individual picture is identified.",
            mentioned=["cand-6389", "cand-1098"], source_line=8,
            extra={"pdf_print_corrections": ["Print p.157 reads 'The others were men like Bernardino Gagliardi'; S0 OCR punctuation/spelling is retained."]},
        ),
        add_candidate_row(
            original, "st-chp6-p157-collection-includes-work-by-allegrini",
            subject="cand-6389", object_="cand-0084", predicate="collection_includes_work_by",
            claim="Haskell names Francesco Allegrini among the other painters represented in Antonio degli Effetti’s collection.",
            quote=quote_allegrini,
            qualification="The source gives Allegrini as an example, not a complete roster; no individual picture is identified.",
            mentioned=["cand-6389", "cand-0084"], source_line=8,
            extra={"pdf_print_corrections": ["Print p.157 reads 'The others were men like Bernardino Gagliardi, Francesco Allegrini'; S0 OCR punctuation/spelling is retained."]},
        ),
    ]

    # The p.157 footnote continuation explicitly reports Haskell's use of an English source version.
    pinax = by_id["st-chp6-p157-pinax-english-version-note"]
    pinax["subject_candidate_id"] = "cand-2962"
    pinax["object_candidate_id"] = "cand-6407"
    pinax["predicate"] = "uses_as_source"
    pq = pinax.setdefault("qualifiers", {})
    pq.update({
        "claim": "Haskell’s book reports using the English version by H. E. Seebohm, with Chipping Campden and 1906 recorded in the note.",
        "text_layer": "authorial footnote source-use statement",
        "qualification": "The exact title and publisher are not stated. This preserves Haskell’s report of source use; the edition was not independently consulted.",
        "mentioned_candidate_ids": ["cand-2962", "cand-6390", "cand-6406", "cand-6407"],
        "citation_locator": "English version by H. E. Seebohm, Chipping Campden, 1906",
        "cited_material_not_independently_consulted": True,
        "relation_candidate": True,
        "relation_candidate_note": "The footnote explicitly reports that Haskell used this English version as a source. The bibliographic identity remains source-limited and no formal S6 edge is created.",
    })

    for sid in TARGETS:
        row = by_id[sid]
        q = row["qualifiers"]
        start, end = int(q["source_line_start"]), int(q["source_line_end"])
        if start != end or row["original_quote"] not in source_lines[start - 1]:
            raise SystemExit(f"p.157 source anchor changed: {sid}")

    coverage_fields, coverage, coverage_bom = read_csv(COVERAGE)
    cov = next((row for row in coverage if row["segment_id"] == SEGMENT), None)
    if not cov or (cov["disposition"], cov["migration_status"]) != ("reviewed", "complete"):
        raise SystemExit(f"unexpected p.157 coverage state: {cov}")
    cov["note"] = (
        "完成印刷p.157 L8–10：拆分Antonio收藏中Cortona与Maratta的单幅作品关系、Gagliardi与Allegrini的具名画家关系；"
        "未名Flemish艺术家群保留开放端点，不映射为Flanders地点。人物评价、名望推论与Marucelli引介按非关系陈述记录。"
        "页底注2续行登记《赞助人与画家》使用Seebohm英译本的来源关系，版本未独立查阅；S0原文和OCR跨度保留。"
    )

    ordered = []
    for row in statements:
        ordered.append(row)
        if row["statement_id"] == original["statement_id"]:
            ordered.extend(extra_rows)
    statements = ordered
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("duplicate statement ID after p.157 split")
    for row in extra_rows:
        for cid in set(row["qualifiers"].get("mentioned_candidate_ids", [])) | {row.get("subject_candidate_id"), row.get("object_candidate_id")}:
            if cid and cid not in candidate_by_id:
                raise SystemExit(f"candidate reference missing in new statement: {row['statement_id']} -> {cid}")

    segment_rows = [row for row in statements if row.get("segment_id") == SEGMENT]
    true_count = sum(row["qualifiers"].get("relation_candidate") is True for row in segment_rows)
    false_count = sum(row["qualifiers"].get("relation_candidate") is False for row in segment_rows)
    unset_count = sum(row["qualifiers"].get("relation_candidate") is None for row in segment_rows)
    if (len(segment_rows), true_count, false_count, unset_count) != (10, 7, 3, 0):
        raise SystemExit(f"unexpected p.157 segment totals: {(len(segment_rows), true_count, false_count, unset_count)}")

    outputs = {
        STATEMENTS: ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in statements) + "\n").encode("utf-8"),
        COVERAGE: csv_bytes(coverage_fields, coverage, coverage_bom),
    }
    summary = {
        "segment": SEGMENT,
        "classified_statements": len(TARGETS),
        "new_atomic_statements": len(extra_rows),
        "new_rows": [
            {"statement_id": row["statement_id"], "subject": row["subject_candidate_id"], "object": row["object_candidate_id"], "predicate": row["predicate"], "claim": row["qualifiers"]["claim"]}
            for row in extra_rows
        ],
        "relation_candidates_after": true_count,
        "non_relational_after": false_count,
        "unset_after": unset_count,
        "pinax_note_predicate": pinax["predicate"],
        "mode": "dry-run",
    }
    return outputs, summary


def main():
    parser = argparse.ArgumentParser(description="Classify p.157 sec_iv S2 statements with protected writes.")
    parser.add_argument("--apply", action="store_true", help="Back up and apply the reviewed p.157 batch.")
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
