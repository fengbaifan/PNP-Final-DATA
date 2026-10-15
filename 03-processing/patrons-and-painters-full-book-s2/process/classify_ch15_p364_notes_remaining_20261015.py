import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from collections import Counter
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_sec_i.md"
SEGMENT = "chp-15:15_CHP-15_sec_i:l43-56"
BOOK = "cand-2962"
BACKUP_TAG = ".bak-s2-ch15-p364-notes-classification-20261015"
EXPECTED = {
    "statements": "1fd06466d25256d5d7c9b133b6afdcc2f9177df0effb513d51994983fda3db81",
    "candidates": "7b60fb5af28ecf4ccc08c5c597a1f07255628ab430541da29b76d587d42ef495",
    "coverage": "54b015888631649fb078342a10dd788b1eba7ead2a27f21123f5838f8b37dd78",
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

def sha(data):
    return hashlib.sha256(data).hexdigest()

paths = {"statements": STATEMENTS, "candidates": CANDIDATES, "coverage": COVERAGE}
for key, path in paths.items():
    if sha(path.read_bytes()) != EXPECTED[key]:
        raise SystemExit(f"unexpected pre-write hash: {key}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if not (
    source_lines[45].startswith("1 De Tipaldo, 1833, and Mazzotti, 1954, p. 133.")
    and source_lines[52].strip() == "3 See Chapter 12."
    and source_lines[54].strip() == "5 See Chapter 11."
    and source_lines[55].startswith("6 Tabacco, pp. 32 if.")
):
    raise SystemExit("p.363–364 note source text changed")

statements = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
by_id = {row["statement_id"]: row for row in statements}
candidate_rows = list(csv.DictReader(CANDIDATES.open(encoding="utf-8-sig", newline="")))
candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
coverage_rows = list(csv.DictReader(COVERAGE.open(encoding="utf-8-sig", newline="")))

citations = {
    "st-chp15-p363-note1-life-citations": {
        "archive": "cand-10451", "line": 46, "locator": "De Tipaldo, 1833",
        "quote": "1 De Tipaldo, 1833",
        "claim": "P.363 note 1 cites De Tipaldo (1833) among the sources for Filippo Farsetti's life.",
        "note": "This records Haskell's citation path only; neither the cited text nor the locator was independently consulted.",
    },
    "st-chp15-p363-note3-archival-act": {
        "archive": "cand-10453", "line": 47, "locator": "Lodovico Gabrieli, Atti 7567, p.788v (11 April 1764)",
        "quote": None,
        "claim": "P.363 note 3 cites the 1764 notarial record for the reported yearly allowance from Filippo Farsetti to Francesco Algarotti.",
        "note": "This records the citation trail. The archival record was not consulted; the allowance remains attributed to Haskell's note.",
    },
    "st-chp15-p363-note4-malamani-canova": {
        "archive": "cand-10454", "line": 48, "locator": "Malamani, Canova, p.6",
        "quote": None,
        "claim": "P.363 note 4 cites Malamani's Canova, page 6, for the first works placed on the palace staircase.",
        "note": "This records Haskell's citation path only; the cited page was not independently consulted.",
    },
    "st-chp15-p363-note5-canova-quaderni": {
        "archive": "cand-10455", "line": 49, "locator": "Canova, Quaderni, pp.18 and 31",
        "quote": None,
        "claim": "P.363 note 5 cites Canova's Quaderni, pages 18 and 31, for Canova's diary comments.",
        "note": "This records Haskell's citation path only; the cited pages were not independently consulted.",
    },
    "st-chp15-p363-note6-haskell-levey": {
        "archive": "cand-10456", "line": 50, "locator": "Haskell and Levey, 1958, p.185",
        "quote": None,
        "claim": "P.363 note 6 cites Haskell and Levey (1958), page 185, for Daniele Farsetti and the S. Rocco exhibition.",
        "note": "This records Haskell's citation path only; the cited page was not independently consulted.",
    },
    "st-chp15-p364-note1-inquisitors-record": {
        "archive": "cand-10462", "line": 51, "locator": "Archivio di Stato, Inquisitori di Stato, Busta 540, Annotazioni, p.164 (30 May 1792)",
        "quote": None,
        "claim": "P.364 note 1 cites the Inquisitori di Stato record, Busta 540, Annotazioni, page 164, dated 30 May 1792.",
        "note": "The archival record was not independently consulted; this is a citation trail, not confirmation of its contents.",
    },
    "st-chp15-p364-note2-moschini": {
        "archive": "cand-10463", "line": 52, "locator": "Moschini, 1806, volume II, p.114",
        "quote": None,
        "claim": "P.364 note 2 cites Moschini (1806), volume II, page 114, for the reported property breakup and collection sale.",
        "note": "This records the short-form citation only; the cited page and full bibliographic title were not independently checked.",
    },
    "st-chp15-p364-memmo-note4-molmenti-biography": {
        "archive": "cand-10475", "line": 54, "locator": "P. Molmenti, 'Un nobil huomo veneziano del secolo XVIII', n.d.",
        "quote": None,
        "claim": "P.364 note 4 cites P. Molmenti's undated article for a brief general biography of Andrea Memmo.",
        "note": "This records Haskell's citation path only; the article and its publication details were not independently checked.",
    },
    "st-chp15-p364-memmo-note4-torcellan-biography": {
        "archive": "cand-10476", "line": 54, "locator": "Torcellan, 1963",
        "quote": None,
        "claim": "P.364 note 4 cites Torcellan (1963) as the principal source for a brief general biography of Andrea Memmo.",
        "note": "This records Haskell's citation path only; the work and cited contents were not independently consulted.",
    },
    "st-chp15-p364-memmo-note6-tabacco": {
        "archive": "cand-10477", "line": 56, "locator": "Tabacco, pp.32 ff.",
        "quote": None,
        "claim": "P.364 note 6 cites Tabacco, pages 32 and following.",
        "note": "This records a short-form citation only; the exact work and cited pages were not independently checked.",
    },
}
false_notes = {
    "st-chp15-p364-memmo-note3-chapter12-crossref":
        "This is an internal pointer to Chapter 12, not a citation to a separately identified source or a relation between entities. Preserve the locator only.",
    "st-chp15-p364-memmo-note5-chapter11-crossref":
        "This is an internal pointer to Chapter 11, not a citation to a separately identified source or a relation between entities. Preserve the locator only.",
}
if len(citations) != 10 or len(false_notes) != 2:
    raise SystemExit("internal note classification count changed")
unresolved_ids = set(citations) | set(false_notes)
if "st-chp15-p363-note1-mazzotti-citation" in by_id:
    raise SystemExit("new p.363 Mazzotti statement ID already exists")
if not unresolved_ids.issubset(by_id):
    raise SystemExit("p.363–364 unresolved note statement set changed")
note_rows = [row for row in statements if row.get("segment_id") == SEGMENT]
if len(note_rows) != 16:
    raise SystemExit(f"unexpected note segment statement count: {len(note_rows)}")
for sid in unresolved_ids:
    row = by_id[sid]
    if row.get("segment_id") != SEGMENT or row.get("qualifiers", {}).get("relation_candidate") is not None:
        raise SystemExit(f"unexpected note statement pre-state: {sid}")
for spec in citations.values():
    archive = spec["archive"]
    if archive not in candidate_by_id or candidate_by_id[archive]["suggested_type"] != "archive":
        raise SystemExit(f"citation archive candidate missing or wrong type: {archive}")
if BOOK not in candidate_by_id or candidate_by_id[BOOK]["suggested_type"] != "archive":
    raise SystemExit("book archive candidate missing")

def classify_citation(row, spec):
    row["subject_candidate_id"] = BOOK
    row["object_candidate_id"] = spec["archive"]
    row["predicate"] = "cites"
    if spec["quote"] is not None:
        row["original_quote"] = spec["quote"]
    q = row.setdefault("qualifiers", {})
    q.update({
        "claim": spec["claim"],
        "relation_candidate": True,
        "relation_candidate_note": spec["note"],
        "citation_locator": spec["locator"],
        "footnote_segment_id": SEGMENT,
        "footnote_source_lines": [spec["line"]],
        "footnote_text_pending": False,
        "cited_source_independently_consulted": False,
    })
    mids = q.setdefault("mentioned_candidate_ids", [])
    for candidate_id in (BOOK, spec["archive"]):
        if candidate_id not in mids:
            mids.append(candidate_id)

for sid, spec in citations.items():
    classify_citation(by_id[sid], spec)

by_id["st-chp15-p363-note1-life-citations"]["qualifiers"]["mentioned_candidate_ids"] = [
    candidate_id for candidate_id in by_id["st-chp15-p363-note1-life-citations"]["qualifiers"]["mentioned_candidate_ids"]
    if candidate_id != "cand-10452"
]

base = by_id["st-chp15-p363-note1-life-citations"]
second = deepcopy(base)
second["statement_id"] = "st-chp15-p363-note1-mazzotti-citation"
second["original_quote"] = "and Mazzotti, 1954, p. 133."
classify_citation(second, {
    "archive": "cand-10452", "line": 46, "locator": "Mazzotti, 1954, p.133",
    "quote": None,
    "claim": "P.363 note 1 cites Mazzotti (1954, p.133) among the sources for Filippo Farsetti's life.",
    "note": "This records Haskell's citation path only; neither the cited text nor the locator was independently consulted.",
})
second["qualifiers"]["mentioned_candidate_ids"] = [
    candidate_id for candidate_id in second["qualifiers"]["mentioned_candidate_ids"]
    if candidate_id != "cand-10451"
]
statements.append(second)
by_id[second["statement_id"]] = second

for sid, note in false_notes.items():
    q = by_id[sid].setdefault("qualifiers", {})
    q["relation_candidate"] = False
    q["relation_candidate_note"] = note

coverage_matches = [row for row in coverage_rows if row["segment_id"] == SEGMENT]
if len(coverage_matches) != 1:
    raise SystemExit("p.364 note coverage row missing or duplicated")
append_note = (
    " 2026-10-15 semantic classification: all citation and cross-reference statements in the merged note segment are classified. "
    "The 11 cited-source claims are represented as Haskell's book cand-2962 citing archive candidates; the cited archival and published sources were not independently consulted. "
    "The Chapter 12 and Chapter 11 pointers remain internal references, not graph relations. P.363 note 1 is split into atomic De Tipaldo and Mazzotti citations."
)
if "2026-10-15 semantic classification:" in coverage_matches[0]["note"]:
    raise SystemExit("note coverage already contains this classification note")
coverage_matches[0]["note"] += append_note

for row in statements:
    if row.get("segment_id") == SEGMENT:
        for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if endpoint and endpoint not in candidate_by_id:
                raise SystemExit(f"unknown note statement endpoint {endpoint} in {row['statement_id']}")
        for endpoint in row.get("qualifiers", {}).get("mentioned_candidate_ids", []):
            if endpoint not in candidate_by_id:
                raise SystemExit(f"unknown note statement mention endpoint {endpoint} in {row['statement_id']}")

final_note_rows = [row for row in statements if row.get("segment_id") == SEGMENT]
counts = Counter(row.get("qualifiers", {}).get("relation_candidate") for row in final_note_rows)
if len(final_note_rows) != 17 or counts[True] != 15 or counts[False] != 2 or counts[None] != 0:
    raise SystemExit(f"unexpected note segment closure: {len(final_note_rows)} {counts}")

from io import StringIO
stream = StringIO(newline="")
writer = csv.DictWriter(stream, fieldnames=list(coverage_rows[0]), lineterminator="\n", extrasaction="raise")
writer.writeheader()
writer.writerows(coverage_rows)
coverage_output = ("\ufeff" + stream.getvalue()).encode("utf-8")
statement_output = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in statements) + "\n").encode("utf-8")
outputs = {STATEMENTS: statement_output, COVERAGE: coverage_output}

print(json.dumps({
    "mode": "apply" if args.apply else "dry-run",
    "segment": SEGMENT,
    "statements": {"total": len(final_note_rows), "true": counts[True], "false": counts[False], "unset": counts[None]},
    "normalized_citations": [{"statement_id": sid, "subject": BOOK, "object": spec["archive"], "predicate": "cites", "locator": spec["locator"]} for sid, spec in citations.items()],
    "new_statement": second["statement_id"],
    "internal_cross_references_false": sorted(false_notes),
    "after_sha256": {path.name: sha(data) for path, data in outputs.items()},
}, ensure_ascii=False, indent=2))

if args.apply:
    for key, path in (("statements", STATEMENTS), ("coverage", COVERAGE)):
        backup = path.with_name(path.name + BACKUP_TAG)
        if backup.exists() and sha(backup.read_bytes()) != EXPECTED[key]:
            raise SystemExit(f"backup differs: {backup.name}")
        if not backup.exists():
            shutil.copy2(path, backup)
    for path, data in outputs.items():
        with tempfile.NamedTemporaryFile("wb", delete=False, dir=path.parent) as handle:
            handle.write(data)
            temp = Path(handle.name)
        temp.replace(path)
    print(json.dumps({"written_sha256": {path.name: sha(path.read_bytes()) for path in outputs}}, ensure_ascii=False, indent=2))
