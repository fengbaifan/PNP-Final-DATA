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
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
MENTIONS = ROOT / "04-knowledge/tables/mentions.csv"
COVERAGE = ROOT / "04-knowledge/tables/s2-coverage.csv"
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/03_CHP-3_sec_iv.md"
PDF = ROOT / "02-sources/01-book/CHP-3.pdf"
PAGE_77 = ROOT / ".tmp_s2_chp3_p77_notes.png"
PAGE_78 = ROOT / ".tmp_s2_chp3_phys20_l14_20261010.png"
SEGMENT = "chp-3:03_CHP-3_sec_iv:l8-14"
BACKUP_TABLE = TABLE.with_name(TABLE.name + ".bak-s2-chp3-sec-iv-l8-14-relations-20261010")
BACKUP_COVERAGE = COVERAGE.with_name(COVERAGE.name + ".bak-s2-chp3-sec-iv-l8-14-print-correction-20261010")
EXPECTED = {
    TABLE: "60f779ce221a01471fc28af2563dceb0bb6fd3791834ffc1682f37ef3bff69ae",
    CANDIDATES: "1c36e0fa29ea9f353eb8ac121ede84eca7414b08b122fa3afb5ea09b4d54789e",
    MENTIONS: "95c7e31ddd47c0122c86019eda1a7b337e5a2e3ace30fcbcf0b49c84e3a28438",
    COVERAGE: "961a48a14deadd1c5faa727946a48df97ab242cd8935840c119e2584ba99ec9b",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed",
    PDF: "362e08518334ae5cda65cc1758f92ef4de6874b5982bfb6600187d889dc6785d",
    PAGE_77: "5c7f5f5094d21285585a619430d95e7f6369f862f4f4d6cf84f8561370baa55d",
    PAGE_78: "b2e30f8f48bee9052d6fa34b3036a4f7ebe1ce3e2f7ae966fe02e24122f890ca",
}
EXPECTED_COVERAGE_NOTE = (
    "Printed p.77 body L9-14; L9 closes the prior sentence and L14 continues at p.78 L17, now closed. "
    "Footnotes 1-2 are migrated and linked to notes L190-191. Segment complete."
)
CORRECTION_NOTE = (
    " Page-image readings on print p.77 (PDF physical p.19): L11 “self-contained” "
    "(S0 OCR “selfcontained”); L12 “filled him” (S0 OCR “filled'him”). Source OCR remains unchanged."
)

TRUE_NOTES = {
    "st-chp3-seciv-l8-14-abandoned-illusionism": "Haskell says Pietro abandoned illusionistic devices used earlier on the Palazzo Barberini ceiling in the Chiesa Nuova nave-vault scene; preserve the comparison between the two works.",
    "st-chp3-seciv-l8-14-alexander-vii-delays": "Haskell attributes renewed delays in the Oratorian work to Pope Alexander VII's intervention; retain this as a source-reported causal relation.",
    "st-chp3-seciv-l8-14-cupola-cartoons-date": "Haskell dates Pietro's beginning of the Chiesa Nuova cupola cartoons to November 1646.",
    "st-chp3-seciv-l8-14-cupola-style-comparison": "Haskell compares Pietro's Chiesa Nuova cupola decoration with the cupola at S. Andrea della Valle; retain the evaluative comparison as source-reported.",
    "st-chp3-seciv-l8-14-four-pendentives-unfinished": "Haskell says Pietro had not completed the four pendentives by May 1651; preserve the date limit and unfinished status as a source-reported work relation.",
    "st-chp3-seciv-l8-14-innocent-x-halts-oratorian-plans": "Haskell says Innocent X temporarily ended the Oratorians' plans to complete their church decoration; preserve the temporary scope.",
    "st-chp3-seciv-l8-14-innocent-x-palace-commission": "Haskell says Innocent X turned to Pietro after hesitation to fresco the vault of the Pamfili family palace in Piazza Navona.",
    "st-chp3-seciv-l8-14-lanfranco-precedent": "Haskell says Lanfranco had solved the basic problems posed by the cupola project about a quarter-century earlier; retain the historical comparison and attribution.",
    "st-chp3-seciv-l8-14-most-completely-decorated": "Haskell reports the Oratorians' claim that Chiesa Nuova was the most completely decorated church of any Order in Rome; this does not establish legal title.",
    "st-chp3-seciv-l8-14-mysticism-difficult": "Haskell says mysticism did not come easily to Pietro; retain the artist-to-concept relation as the author's assessment.",
    "st-chp3-seciv-l8-14-nave-vault-commission": "Haskell says Pietro undertook the church's last and most important commission, the nave vault, in 1664.",
    "st-chp3-seciv-l8-14-nave-vault-miracle": "Haskell says the nave-vault fresco depicted a miraculous intervention of the Virgin during Chiesa Nuova's construction; retain the source's reported depiction.",
    "st-chp3-seciv-l8-14-pietro-subordinate-to-patrons": "This is Haskell's comparative interpretation of Pietro's relationship with the Oratorians and higher-placed patrons; do not infer identities for the unnamed patrons.",
    "st-chp3-seciv-l8-14-resta-oval-scenes": "Haskell says Padre Sebastiano Resta selected artists to paint fifteen oval scenes around 1700; preserve Resta's selection role and the stated count and date.",
    "st-chp3-seciv-l8-14-resumed-after-pamfili-work": "Haskell says Pietro could resume work on the Oratorian church only after completing the Pamfili palace decoration at the end of 1654.",
    "st-chp3-seciv-l8-14-short-absence": "Haskell says Pietro had to convince the Grand Duke that his absence from Florence would be short; this does not establish that leave was granted.",
    "st-chp3-seciv-l8-14-st-philip-goodwill": "Haskell says St Philip's passionate nature filled Pietro with goodwill but did not raise his work to comparable heights; preserve the author's evaluative relation.",
}
FALSE_BILATERAL_NOTES = {
    "st-chp3-seciv-l8-14-resumption-fragment": (
        "This subordinate clause repeats the Chiesa Nuova resumption already stated with fuller context in "
        "st-chp3-seciv-l8-14-resumed-after-pamfili-work and functions as the temporal frame for the next segment's "
        "S. Andrea decoration sentence. It adds no independent entity relation; the agent of the further decorations remains unstated."
    )
}
FALSE_SINGLE_NOTES = {
    "st-chp3-seciv-l8-14-aesthetic-assessment": "This is Haskell's aesthetic assessment of Pietro's Oratorian frescoes, not a relation to a second entity.",
    "st-chp3-seciv-l8-14-cupola-frescoes-not-ready": "This records the cupola frescoes' completion state and date, not a relation between independently identified entities.",
    "st-chp3-seciv-l8-14-scene-withdrawn-from-spectator": "This describes the nave-vault fresco's visual presentation, not a relation to a second entity.",
    "st-chp3-seciv-l8-14-two-planes": "This describes the composition represented within one fresco, not a relation between independently identified entities.",
    "st-chp3-seciv-l8-14-viewer-not-participant": "This describes the fresco's intended viewing experience; no bounded viewer entity is identified.",
    "st-chp3-seciv-l8-14-worldly-inspiration": "This is Haskell's assessment of Pietro's artistic inspiration, not a relation to a second entity.",
}
EXISTING_TRUE = {
    "st-chp3-seciv-l8-14-assumption-apse",
    "st-chp3-seciv-l8-14-four-prophets-pendentives",
}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def encode_jsonl(rows: list[dict], raw: bytes) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    prefix = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    return prefix + b"".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + newline for row in rows)


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str], bytes]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader), list(reader.fieldnames or []), raw


def encode_csv(rows: list[dict[str, str]], fieldnames: list[str], raw: bytes) -> bytes:
    newline = "\r\n" if b"\r\n" in raw else "\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator=newline)
    writer.writeheader()
    writer.writerows(rows)
    prefix = "\ufeff" if raw.startswith(b"\xef\xbb\xbf") else ""
    return (prefix + stream.getvalue()).encode("utf-8")


def atomic_write(path: Path, payload: bytes) -> None:
    temp: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as stream:
            stream.write(payload)
            temp = Path(stream.name)
        os.replace(temp, path)
    finally:
        if temp and temp.exists():
            temp.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify the pending S2 statements for print p.77 L9-14.")
    parser.add_argument("--apply", action="store_true", help="Write after all fixed preflight checks pass; default is dry-run.")
    args = parser.parse_args()

    for path, expected in EXPECTED.items():
        require(path.exists() and digest(path) == expected, f"preflight hash changed: {path.relative_to(ROOT)}")
    require(not BACKUP_TABLE.exists() and not BACKUP_COVERAGE.exists(), "recovery backup already exists")

    raw_table = TABLE.read_bytes()
    rows = read_jsonl(TABLE)
    require(len(rows) == 12753 and len({row["statement_id"] for row in rows}) == len(rows), "statement table count or unique IDs changed")
    by_id = {row["statement_id"]: row for row in rows}
    segment_rows = [row for row in rows if row.get("segment_id") == SEGMENT]
    require(len(segment_rows) == 26, "source-segment statement count changed")
    flag = lambda row: (row.get("qualifiers") or {}).get("relation_candidate")
    pending_bilateral = {
        row["statement_id"] for row in segment_rows
        if row.get("subject_candidate_id") and row.get("object_candidate_id") and flag(row) is None
    }
    pending_single = {
        row["statement_id"] for row in segment_rows
        if bool(row.get("subject_candidate_id")) != bool(row.get("object_candidate_id")) and flag(row) is None
    }
    require(pending_bilateral == set(TRUE_NOTES) | set(FALSE_BILATERAL_NOTES), "pending bilateral statement set changed")
    require(pending_single == set(FALSE_SINGLE_NOTES), "pending single-ended statement set changed")
    require({row["statement_id"] for row in segment_rows if flag(row) is True} == EXISTING_TRUE, "preclassified relation statements changed")

    candidates = {row["candidate_id"] for row in read_csv(CANDIDATES)[0]}
    for row in segment_rows:
        for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            require(not endpoint or endpoint in candidates, f"missing candidate endpoint in {row['statement_id']}: {endpoint}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    normalize = lambda value: " ".join(value.split())
    for statement_id in pending_bilateral | pending_single:
        row = by_id[statement_id]
        qualifiers = row.get("qualifiers") or {}
        start, end = qualifiers.get("source_line_start"), qualifiers.get("source_line_end")
        require(isinstance(start, int) and isinstance(end, int) and 9 <= start <= end <= 14, f"source line range changed: {statement_id}")
        source_span = normalize("\n".join(source_lines[start - 1:end]))
        quote = normalize(row.get("original_quote", ""))
        require(quote and quote in source_span, f"source quote mismatch: {statement_id}")
    require("selfcontained" in source_lines[10] and "filled'him" in source_lines[11], "expected S0 OCR readings changed")

    manifest = {row["segment_id"]: row for row in read_jsonl(SEGMENTS)}.get(SEGMENT)
    require(manifest and (manifest.get("source_file"), manifest.get("line_start"), manifest.get("line_end"), manifest.get("asset_sha256")) == (
        "02-sources/02-Markdown/03_CHP-3_sec_iv.md", 8, 14, EXPECTED[SOURCE]
    ), "S0 segment boundary or source fingerprint changed")
    coverage_rows, coverage_fields, raw_coverage = read_csv(COVERAGE)
    coverage = next((row for row in coverage_rows if row["segment_id"] == SEGMENT), None)
    require(coverage and (coverage["disposition"], coverage["migration_status"], coverage["source_line_ranges"], coverage["note"]) == (
        "reviewed", "complete", "L9-14", EXPECTED_COVERAGE_NOTE
    ), "S2 coverage row changed")
    coverage["note"] += CORRECTION_NOTE
    payload_coverage = encode_csv(coverage_rows, coverage_fields, raw_coverage)

    for statement_id, note in TRUE_NOTES.items():
        qualifiers = dict(by_id[statement_id].get("qualifiers") or {})
        qualifiers.update(relation_candidate=True, relation_candidate_note=note)
        by_id[statement_id]["qualifiers"] = qualifiers
    for statement_id, note in (FALSE_BILATERAL_NOTES | FALSE_SINGLE_NOTES).items():
        qualifiers = dict(by_id[statement_id].get("qualifiers") or {})
        qualifiers.update(relation_candidate=False, relation_candidate_note=note)
        by_id[statement_id]["qualifiers"] = qualifiers

    bilateral = [row for row in rows if row.get("subject_candidate_id") and row.get("object_candidate_id")]
    relation_total = sum(flag(row) is True for row in rows)
    relation_open = sum(flag(row) is True and not (row.get("subject_candidate_id") and row.get("object_candidate_id")) for row in rows)
    projected = (
        len(rows), len(bilateral), sum(flag(row) is True for row in bilateral),
        sum(flag(row) is False for row in bilateral), sum(flag(row) is None for row in bilateral),
        relation_total, relation_open,
    )
    require(projected == (12753, 8546, 4818, 476, 3252, 4867, 49), f"projected whole-book counts differ: {projected}")
    final_segment = [row for row in rows if row.get("segment_id") == SEGMENT]
    segment_counts = (
        len(final_segment), sum(flag(row) is True for row in final_segment),
        sum(flag(row) is False for row in final_segment), sum(flag(row) is None for row in final_segment),
    )
    require(segment_counts == (26, 19, 7, 0), f"projected segment counts differ: {segment_counts}")

    payload_table = encode_jsonl(rows, raw_table)
    report = {
        "action": "apply" if args.apply else "dry-run",
        "segment_id": SEGMENT,
        "bilateral_candidates_added": len(TRUE_NOTES),
        "bilateral_nonrelations_added": len(FALSE_BILATERAL_NOTES),
        "single_endpoint_nonrelations_added": len(FALSE_SINGLE_NOTES),
        "segment_after": {"statements": segment_counts[0], "relation_candidates": segment_counts[1], "nonrelations": segment_counts[2], "unclassified": segment_counts[3]},
        "whole_book_after": {"bilateral": projected[1], "relation_candidates": projected[2], "nonrelations": projected[3], "unclassified": projected[4], "all_relation_candidates": projected[5], "open_relation_candidates": projected[6]},
        "post_write_sha256": {"statements": hashlib.sha256(payload_table).hexdigest(), "coverage": hashlib.sha256(payload_coverage).hexdigest()},
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not args.apply:
        print("Dry run only. Pass --apply to write.")
        return

    shutil.copy2(TABLE, BACKUP_TABLE)
    shutil.copy2(COVERAGE, BACKUP_COVERAGE)
    try:
        atomic_write(TABLE, payload_table)
        atomic_write(COVERAGE, payload_coverage)
        saved = read_jsonl(TABLE)
        saved_by_id = {row["statement_id"]: row for row in saved}
        require(len(saved) == 12753 and all(saved_by_id[statement_id]["qualifiers"].get("relation_candidate") is True for statement_id in TRUE_NOTES), "statement post-write checks failed")
        require(all(saved_by_id[statement_id]["qualifiers"].get("relation_candidate") is False for statement_id in (FALSE_BILATERAL_NOTES | FALSE_SINGLE_NOTES)), "nonrelation post-write checks failed")
        require(digest(TABLE) == hashlib.sha256(payload_table).hexdigest(), "statement post-write digest differs")
        saved_coverage = read_csv(COVERAGE)[0]
        saved_row = next(row for row in saved_coverage if row["segment_id"] == SEGMENT)
        require(saved_row["note"] == EXPECTED_COVERAGE_NOTE + CORRECTION_NOTE, "coverage post-write note differs")
        require(digest(COVERAGE) == hashlib.sha256(payload_coverage).hexdigest(), "coverage post-write digest differs")
    except Exception:
        shutil.copy2(BACKUP_TABLE, TABLE)
        shutil.copy2(BACKUP_COVERAGE, COVERAGE)
        raise
    report.update(
        result="applied",
        backups=[str(BACKUP_TABLE.relative_to(ROOT)), str(BACKUP_COVERAGE.relative_to(ROOT))],
        sha256_after={"statements": digest(TABLE), "coverage": digest(COVERAGE)},
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
