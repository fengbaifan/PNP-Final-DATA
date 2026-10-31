"""Register source-defined S1 candidates for four unresolved endpoint backlogs.

Default execution is a dry run. Use --apply once after reviewing the proposed
rows. The write is hash-guarded and keeps byte-for-byte recovery copies.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import os
from pathlib import Path
import re
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
CANDIDATE_PATH = TABLES / "entity-candidates.csv"
BACKLOG_PATH = TABLES / "candidate-backlog.csv"
COVERAGE_PATH = TABLES / "s2-coverage.csv"
RECOVERY_DIR = ROOT / "06-runtime" / "recovery" / "s1-backlog-candidates-20261031"

EXPECTED_HASHES = {
    CANDIDATE_PATH.name: "36f31e7e49522a093b4e9ca578ea377ec8af5ba98173a94bf656510a477237ff",
    BACKLOG_PATH.name: "21b374354feeec3d7185f6c651cf576dfd3e52ebe0f498711db2579bed898f4a",
}

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-12460",
        "index_entry_id": "",
        "canonical_name": "L. Toesca (author form in Haskell bibliography; identity unresolved)",
        "index_page_range": "",
        "suggested_type": "person",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Haskell's bibliography prints the author form Toesca, L. for the 1957 article. "
            "Keep this source-defined person candidate distinct from I. Toesca (cand-4332) "
            "and Ilaria Toesca (cand-9345) until S3 resolves the initials; do not infer a "
            "biography or formal authored_by relation."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-21:21_CHP-21Bibliography:l1141-1177#L1169",
    },
    {
        "candidate_id": "cand-12461",
        "index_entry_id": "",
        "canonical_name": "Hôtel Jacquemart-André (physical building and staircase named by the official work record)",
        "index_page_range": "",
        "suggested_type": "place",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "The official Musée Jacquemart-André work record (source src-821d4b71d11ff434, "
            "'The Staircase' section) identifies the physical Hôtel and staircase separately "
            "from institution candidate cand-8358. This source-limited place candidate does "
            "not establish present-day custody or a formal current-location relation."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-9:09_CHP-9_intro:l323-445#L373",
    },
    {
        "candidate_id": "cand-12462",
        "index_entry_id": "",
        "canonical_name": "First edition of Newtonianismo per le Dame (specific edition endpoint; metadata unspecified)",
        "index_page_range": "",
        "suggested_type": "archive",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Haskell identifies a first-edition endpoint for the frontispiece statement, distinct "
            "from the title-level publication candidate cand-10258. No date, imprint, or copy is "
            "supplied. Keep edition identity and registration undecided; do not infer metadata."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-14:14_CHP-14_intro:l85-95#L90",
    },
    {
        "candidate_id": "cand-12463",
        "index_entry_id": "",
        "canonical_name": "Angelo Contarini's ambassadorial report for 1627-1629 (reporting document; exact title unspecified)",
        "index_page_range": "",
        "suggested_type": "archive",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Haskell cites a report by Venetian ambassador Angelo Contarini for 1627-1629, "
            "published in volume I. Keep the source-defined report document distinct from person "
            "candidate cand-4875 and publication-volume candidate cand-4365. Its exact title and "
            "document identity remain unresolved; no relation is formalized."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-2:02_CHP-2_sec_iv:l190-245#L232",
    },
]

BACKLOG_LINKS = {
    "bl-0037": "cand-12460",
    "bl-0044": "cand-12461",
    "bl-0059": "cand-12462",
    "bl-0081": "cand-12463",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_csv_text(text: str) -> tuple[list[str], list[list[str]]]:
    rows = list(csv.reader(io.StringIO(text, newline="")))
    if not rows:
        raise ValueError("CSV is empty")
    return rows[0], rows[1:]


def split_csv_field_span(line: str, field_index: int) -> tuple[int, int]:
    """Return a raw CSV field span without reserializing neighboring fields."""
    commas: list[int] = []
    in_quotes = False
    index = 0
    while index < len(line):
        char = line[index]
        if char == '"':
            if in_quotes and index + 1 < len(line) and line[index + 1] == '"':
                index += 2
                continue
            in_quotes = not in_quotes
        elif char == "," and not in_quotes:
            commas.append(index)
        index += 1
    start = 0 if field_index == 0 else commas[field_index - 1] + 1
    end = len(line) if field_index == len(commas) else commas[field_index]
    return start, end


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temp_path = Path(handle.name)
        handle.write(data)
    os.replace(temp_path, path)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="apply after preflight")
    args = parser.parse_args()

    candidate_bytes = CANDIDATE_PATH.read_bytes()
    backlog_bytes = BACKLOG_PATH.read_bytes()
    for path, data in ((CANDIDATE_PATH, candidate_bytes), (BACKLOG_PATH, backlog_bytes)):
        actual = sha256(data)
        expected = EXPECTED_HASHES[path.name]
        if actual != expected:
            raise SystemExit(f"{path.name}: precondition hash mismatch: {actual}")

    candidate_text = candidate_bytes.decode("utf-8")
    backlog_text = backlog_bytes.decode("utf-8")
    candidate_header, candidate_rows = parse_csv_text(candidate_text)
    backlog_header, backlog_rows = parse_csv_text(backlog_text)
    candidate_header[0] = candidate_header[0].removeprefix("\ufeff")
    backlog_header[0] = backlog_header[0].removeprefix("\ufeff")
    if candidate_header != list(NEW_CANDIDATES[0]):
        raise SystemExit("entity-candidates.csv header changed")
    if "candidate_id" not in backlog_header or "backlog_id" not in backlog_header:
        raise SystemExit("candidate-backlog.csv required columns are missing")

    candidate_id_index = candidate_header.index("candidate_id")
    backlog_id_index = backlog_header.index("backlog_id")
    backlog_candidate_index = backlog_header.index("candidate_id")
    current_ids = {row[candidate_id_index] for row in candidate_rows}
    expected_new_ids = {row["candidate_id"] for row in NEW_CANDIDATES}
    if current_ids & expected_new_ids:
        raise SystemExit("one or more proposed candidate IDs already exist")
    numeric_ids = [int(value.removeprefix("cand-")) for value in current_ids]
    if max(numeric_ids) != 12459:
        raise SystemExit(f"unexpected candidate ID high-water mark: {max(numeric_ids)}")

    backlog_by_id = {row[backlog_id_index]: row for row in backlog_rows}
    if len(backlog_by_id) != len(backlog_rows):
        raise SystemExit("backlog_id is not unique")
    for backlog_id, candidate_id in BACKLOG_LINKS.items():
        row = backlog_by_id.get(backlog_id)
        if row is None or row[backlog_candidate_index]:
            raise SystemExit(f"unexpected current candidate mapping for {backlog_id}")
        if candidate_id not in expected_new_ids:
            raise SystemExit(f"unsupported target candidate for {backlog_id}")

    coverage_header, coverage_rows = parse_csv_text(COVERAGE_PATH.read_text(encoding="utf-8"))
    coverage_id_index = coverage_header.index("segment_id")
    coverage_disposition_index = coverage_header.index("disposition")
    coverage_line_ranges_index = coverage_header.index("source_line_ranges")
    for candidate in NEW_CANDIDATES:
        match = re.fullmatch(r"(.+)#L(\d+)", candidate["candidate_source_ref"])
        if not match:
            raise SystemExit(f"invalid candidate source ref: {candidate['candidate_id']}")
        segment_id, line_number = match.group(1), int(match.group(2))
        coverage = [row for row in coverage_rows if row[coverage_id_index] == segment_id]
        if len(coverage) != 1 or coverage[0][coverage_disposition_index] != "reviewed":
            raise SystemExit(f"source segment is not reviewed: {segment_id}")
        ranges = [
            (int(start), int(end))
            for start, end in re.findall(r"L(\d+)-(\d+)", coverage[0][coverage_line_ranges_index])
        ]
        if not any(start <= line_number <= end for start, end in ranges):
            raise SystemExit(f"source line is outside reviewed coverage: {candidate['candidate_id']}")

    delimiter = "\r\n" if b"\r\n" in candidate_bytes else "\n"
    append_buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        append_buffer,
        fieldnames=candidate_header,
        lineterminator=delimiter,
        extrasaction="raise",
    )
    for candidate in NEW_CANDIDATES:
        writer.writerow(candidate)
    candidate_append = append_buffer.getvalue()
    if candidate_text and not candidate_text.endswith(("\n", "\r")):
        candidate_text += delimiter
    new_candidate_text = candidate_text + candidate_append

    updated_backlog_lines: list[str] = []
    seen_links: set[str] = set()
    for raw_line in backlog_text.splitlines(keepends=True):
        content = raw_line.rstrip("\r\n")
        parsed = next(csv.reader([content]))
        if parsed and parsed[0] in BACKLOG_LINKS:
            backlog_id = parsed[0]
            field_start, field_end = split_csv_field_span(content, backlog_candidate_index)
            if content[field_start:field_end] != "":
                raise SystemExit(f"candidate_id field is not empty in {backlog_id}")
            content = content[:field_start] + BACKLOG_LINKS[backlog_id] + content[field_end:]
            raw_line = content + raw_line[len(raw_line.rstrip("\r\n")) :]
            seen_links.add(backlog_id)
        updated_backlog_lines.append(raw_line)
    if seen_links != set(BACKLOG_LINKS):
        raise SystemExit(f"not all target backlog rows were updated: {sorted(seen_links)}")
    new_backlog_text = "".join(updated_backlog_lines)

    print(f"candidate_count: {len(candidate_rows)} -> {len(candidate_rows) + len(NEW_CANDIDATES)}")
    print("new candidates:")
    for candidate in NEW_CANDIDATES:
        print(f"  {candidate['candidate_id']} | {candidate['suggested_type']} | {candidate['canonical_name']}")
    print("backlog mappings:")
    for backlog_id, candidate_id in BACKLOG_LINKS.items():
        print(f"  {backlog_id} -> {candidate_id}")
    print("unmapped backlog rows intentionally remain pending: bl-0011, bl-0012, bl-0085")

    if not args.apply:
        print("dry-run only; no files changed")
        return

    RECOVERY_DIR.mkdir(parents=True, exist_ok=False)
    (RECOVERY_DIR / "entity-candidates.csv.before").write_bytes(candidate_bytes)
    (RECOVERY_DIR / "candidate-backlog.csv.before").write_bytes(backlog_bytes)
    atomic_write(CANDIDATE_PATH, new_candidate_text.encode("utf-8"))
    atomic_write(BACKLOG_PATH, new_backlog_text.encode("utf-8"))
    print(f"applied; recovery copies: {RECOVERY_DIR.relative_to(ROOT).as_posix()}")
    print(f"entity-candidates.csv sha256: {sha256(CANDIDATE_PATH.read_bytes())}")
    print(f"candidate-backlog.csv sha256: {sha256(BACKLOG_PATH.read_bytes())}")


if __name__ == "__main__":
    main()
