from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import sys
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE_DIR = ROOT / "04-knowledge/tables"
STATEMENTS = TABLE_DIR / "book-statements.jsonl"
CANDIDATES = TABLE_DIR / "entity-candidates.csv"
MENTIONS = TABLE_DIR / "mentions.csv"
SEGMENTS = TABLE_DIR / "segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/10_CHP-10_intro.md"
EXPECTED_HASHES = {
    STATEMENTS: "a96e42435fbb1016f74b6fbde0e25da686d9552159339d56dce46479d2ba403f",
    CANDIDATES: "81a9d427215fa8ab92d6641b7593c48322eb308ccfe4c98baa466e6c56cfcfde",
    MENTIONS: "83b23c837298461a75f16ba8bfef5ff267fd2840dda0c68b2db07ea05cf64d91",
}
SOURCE_SHA256 = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
SEGMENT_ID = "chp-10:10_CHP-10_intro:l491-634"
SEGMENT_SHA256 = "33d2557d3e681434a9c964316a7a24fe2c00faa934add1381c12fc4d8a7c7f76"
BACKUPS = {
    STATEMENTS: STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp10-p276n1-atomic-claims-20261015"),
    CANDIDATES: CANDIDATES.with_name("entity-candidates.csv.bak-s2-chp10-p276n1-atomic-claims-20261015"),
    MENTIONS: MENTIONS.with_name("mentions.csv.bak-s2-chp10-p276n1-atomic-claims-20261015"),
}

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-12401",
        "index_entry_id": "",
        "canonical_name": "Guido Reni's very late 'chalky' manner (Haskell's description)",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell's characterization of the late manner Crespi may have had in mind. Preserve the wording and the author's inference; do not equate it with all of Guido Reni's work or an independently established style category.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-10:10_CHP-10_intro:l491-634#L492",
    },
    {
        "candidate_id": "cand-12402",
        "index_entry_id": "",
        "canonical_name": "Eighteenth-century connoisseurs described as receptive to Guido Reni's late manner",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell's broad, time-bounded reception group for the claim that the late 'chalky' manner would be attractive. The passage names no individuals or membership; leave the group untyped.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-10:10_CHP-10_intro:l491-634#L492",
    },
    {
        "candidate_id": "cand-12403",
        "index_entry_id": "",
        "canonical_name": "Rosalba Carriera's pastel work referenced in Crespi's 1703 comparison",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "The source refers collectively to Carriera's work in pastel in Crespi's comparison with Guido Reni. No individual pastel or complete corpus is identified; keep this source-defined work group untyped.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-10:10_CHP-10_intro:l491-634#L492",
    },
]

NEW_MENTIONS = [
    {
        "mention_id": "m-chp10-p276n1-guido-chalky-manner",
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-12401",
        "surface_form": "very late, ‘chalky’ manner",
        "start_char": "539",
        "end_char": "565",
        "note": "The manner description follows the separate possessive mention of Guido; it is modeled as a term, not as the painter himself.",
    },
    {
        "mention_id": "m-chp10-p276n1-eighteenth-century-connoisseurs",
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-12402",
        "surface_form": "eighteenth-century connoisseurs",
        "start_char": "599",
        "end_char": "630",
        "note": "Haskell's unnamed, broad reception group; membership is not supplied.",
    },
    {
        "mention_id": "m-chp10-p276n1-carriera-pastel-work",
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-12403",
        "surface_form": "her work in this medium",
        "start_char": "436",
        "end_char": "459",
        "note": "Carriera's pastel work as a source-defined group, not an individual painting.",
    },
]

NEW_STATEMENTS = [
    {
        "statement_id": "st-chp10-notes-p276n1-crespi-pastel-work-compared-with-guido",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-12403",
        "object_candidate_id": "cand-2124",
        "predicate": "pastel_work_compared_to_guido_reni_by_crespi",
        "qualifiers": {
            "source_line_start": 492,
            "source_line_end": 492,
            "printed_page": 276,
            "pdf_physical_page": 1,
            "claim": "Haskell reports that Crespi compared Carriera's pastel work to Guido Reni on 26 June 1703.",
            "speaker": "Haskell",
            "text_layer": "authorial note reporting a dated comparison",
            "qualification": "The cited Malamani 1899, p. 99 locator was not independently consulted. The compared work is a source-defined group; no individual pastel or specific Reni work is named.",
            "mentioned_candidate_ids": ["cand-12403", "cand-0871", "cand-2124", "cand-9282"],
            "parent_body_statement_ids": ["st-chp10-p276-cole-carriera-pastel-portraits"],
            "footnote_number": 1,
            "cited_material_not_independently_consulted": True,
            "date": "1703-06-26",
            "relation_candidate": True,
            "relation_candidate_note": "This records Haskell's report of Crespi's comparison, with Crespi preserved as the comparing agent in the claim and mentioned candidates. It does not identify a particular painting by either artist.",
            "ocr_corrections": [{"source_line": 492, "source_form": "ason", "print_reading": "as on", "locator": "CHP-10.pdf physical page 1 / print p. 276"}],
        },
        "original_quote": "ason 26 June 1703 Crespi had already compared her work in this medium to Guido Reni—Malamani, 1899, p. 99.",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
    },
    {
        "statement_id": "st-chp10-notes-p276n1-guido-manner-connoisseur-reception",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-12401",
        "object_candidate_id": "cand-12402",
        "predicate": "haskell_describes_late_chalky_manner_as_attractive_to_connoisseurs",
        "qualifiers": {
            "source_line_start": 492,
            "source_line_end": 492,
            "printed_page": 276,
            "pdf_physical_page": 1,
            "claim": "Haskell says Guido Reni's late 'chalky' manner was to be attractive to eighteenth-century connoisseurs.",
            "speaker": "Haskell",
            "text_layer": "authorial interpretation of reception",
            "qualification": "This is Haskell's broad reception assessment, not a report about named connoisseurs or independently verified responses.",
            "mentioned_candidate_ids": ["cand-12401", "cand-12402", "cand-2124"],
            "parent_body_statement_ids": ["st-chp10-p276-cole-carriera-pastel-portraits"],
            "footnote_number": 1,
            "cited_material_not_independently_consulted": True,
            "relation_candidate": True,
            "relation_candidate_note": "This preserves Haskell's reception claim as a relation between the described manner and an unnamed, untyped group; it does not imply uniform response by every connoisseur.",
        },
        "original_quote": "which was to be so attractive to eighteenth-century connoisseurs.",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
    },
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_open(row: dict) -> bool:
    q = row.get("qualifiers") or {}
    return q.get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def csv_bytes(rows: list[dict], fields: list[str], has_bom: bool) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8-sig" if has_bom else "utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        if digest(raw[path]) != expected:
            raise ValueError(f"protected table changed: {path.name} ({digest(raw[path])})")
    if digest(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise ValueError("chapter 10 source asset changed")
    segments = {
        row["segment_id"]: row
        for row in (
            json.loads(line)
            for line in (TABLE_DIR / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
            if line.strip()
        )
    }
    segment = segments.get(SEGMENT_ID)
    if not segment or segment.get("sha256") != SEGMENT_SHA256 or segment.get("asset_sha256") != SOURCE_SHA256:
        raise ValueError("reviewed p.276 note segment changed")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[490:634])
    source_quotes = [
        "But Zanetti is mistaken when he says that this occurred in 1708",
        "ason 26 June 1703 Crespi had already compared her work in this medium to Guido Reni—Malamani, 1899, p. 99.",
        "Crespi must have been thinking of Guido’s very late, ‘chalky’ manner",
        "which was to be so attractive to eighteenth-century connoisseurs.",
    ]
    if any(quote not in segment_text for quote in source_quotes):
        raise ValueError("p.276 note text changed or quote boundary no longer matches")
    for mention in NEW_MENTIONS:
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if segment_text[start:end] != mention["surface_form"]:
            raise ValueError(f"source span mismatch: {mention['mention_id']}")

    statements = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise ValueError("duplicate statement IDs")
    style = by_id.get("st-chp10-notes-p276n1-guido-manner-interpretation")
    correction = by_id.get("st-chp10-notes-p276n1-zanetti-date-correction")
    if not style or not correction:
        raise ValueError("expected p.276 note statements are missing")
    if (
        style.get("subject_candidate_id") is not None
        or style.get("object_candidate_id") is not None
        or (style.get("qualifiers") or {}).get("relation_candidate") is not True
        or correction.get("subject_candidate_id") is not None
        or correction.get("object_candidate_id") is not None
        or (correction.get("qualifiers") or {}).get("relation_candidate") is not True
    ):
        raise ValueError("reviewed p.276 note statements changed")
    for item in NEW_CANDIDATES:
        if item["candidate_id"] in {row["candidate_id"] for row in csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig")))}:
            raise ValueError(f"candidate ID already exists: {item['candidate_id']}")
    for item in NEW_MENTIONS:
        if item["mention_id"] in {row["mention_id"] for row in csv.DictReader(io.StringIO(raw[MENTIONS].decode("utf-8-sig")))}:
            raise ValueError(f"mention ID already exists: {item['mention_id']}")
    for item in NEW_STATEMENTS:
        if item["statement_id"] in by_id:
            raise ValueError(f"statement ID already exists: {item['statement_id']}")

    open_before = sum(is_open(row) for row in statements)
    no_reason_before = sum(is_open(row) and not (row.get("qualifiers") or {}).get("open_endpoint_reason") for row in statements)
    if (open_before, no_reason_before) != (381, 61):
        raise ValueError(f"unexpected full-table open state: {open_before}, {no_reason_before}")

    style["subject_candidate_id"] = "cand-0871"
    style["object_candidate_id"] = "cand-12401"
    style["original_quote"] = source_quotes[2]
    style["qualifiers"]["claim"] = "Haskell infers that Crespi had in mind Guido Reni's very late 'chalky' manner."
    style["qualifiers"]["mentioned_candidate_ids"].append("cand-12401")
    style["qualifiers"]["relation_candidate_note"] = "This preserves Haskell's explicitly speculative inference about Crespi's intended reference. The target is the described manner (cand-12401), not Guido Reni as a person or a named work."

    correction["predicate"] = "haskell-corrects-zanettis-date-for-pastel-advice"
    correction["original_quote"] = source_quotes[0]
    correction["qualifiers"]["claim"] = "Haskell says Zanetti's 1708 date for the first pastel advice is mistaken, citing Crespi's comparison of Carriera's pastel work to Guido Reni by 26 June 1703."
    correction["qualifiers"]["relation_candidate"] = False
    correction["qualifiers"]["relation_candidate_note"] = "This is Haskell's source-attributed chronological correction. The Crespi comparison is recorded as a separate relation statement; the cited Malamani page was not independently consulted."
    correction["qualifiers"].pop("open_endpoint_reason", None)

    for item in NEW_STATEMENTS:
        statements.append(item)
    with CANDIDATES.open(encoding="utf-8-sig", newline="") as handle:
        candidate_reader = csv.DictReader(handle)
        candidate_fields = candidate_reader.fieldnames
        candidates = list(candidate_reader)
    with MENTIONS.open(encoding="utf-8-sig", newline="") as handle:
        mention_reader = csv.DictReader(handle)
        mention_fields = mention_reader.fieldnames
        mentions = list(mention_reader)
    candidates.extend(NEW_CANDIDATES)
    mentions.extend(NEW_MENTIONS)

    outputs = {
        STATEMENTS: "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in statements).encode("utf-8"),
        CANDIDATES: csv_bytes(candidates, candidate_fields, raw[CANDIDATES].startswith(b"\xef\xbb\xbf")),
        MENTIONS: csv_bytes(mentions, mention_fields, raw[MENTIONS].startswith(b"\xef\xbb\xbf")),
    }
    open_after = sum(is_open(row) for row in statements)
    no_reason_after = sum(is_open(row) and not (row.get("qualifiers") or {}).get("open_endpoint_reason") for row in statements)
    true_after = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in statements)
    false_after = sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in statements)
    if (open_after, no_reason_after, true_after, false_after, len(statements)) != (379, 59, 10394, 4753, 15147):
        raise ValueError(f"unexpected resulting semantic state: {(open_after, no_reason_after, true_after, false_after, len(statements))}")

    print("reviewed=chapter 10 p.276 note 1; separated chronology correction, dated comparison, Crespi inference and connoisseur reception")
    print("changes=3 source-bounded candidates, 3 exact mentions, 2 atomic statements added, 1 date-correction claim reclassified as non-relation, 1 inference relation completed")
    print(f"open_endpoints={open_before}->{open_after}; open_without_reason={no_reason_before}->{no_reason_after}; relation_true={true_after}; relation_false={false_after}")
    for path, output in outputs.items():
        print(f"{path.name} sha256 {digest(raw[path])}->{digest(output)}")
    if args.preview:
        return 0

    for backup in BACKUPS.values():
        if backup.exists():
            raise FileExistsError(f"recovery copy already exists: {backup.name}")
    temps = {path: path.with_name(path.name + ".tmp-s2-chp10-p276n1-atomic-claims-20261015") for path in outputs}
    if any(path.exists() for path in temps.values()):
        raise FileExistsError("protected temporary output already exists")
    for path, backup in BACKUPS.items():
        shutil.copy2(path, backup)
    try:
        for path, output in outputs.items():
            temps[path].write_bytes(output)
        for path in outputs:
            temps[path].replace(path)
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        for path, backup in BACKUPS.items():
            shutil.copy2(backup, path)
        raise
    print("backups=" + ", ".join(path.name for path in BACKUPS.values()))
    print("applied_hashes=" + ", ".join(f"{path.name}:{digest(path.read_bytes())}" for path in outputs))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
