#!/usr/bin/env python3
"""Controlled S2 migration of the bibliography scope note and repository list (lines 3-45)."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "21_CHP-21Bibliography.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-21Bibliography.pdf"
SEGMENT = "chp-21:21_CHP-21Bibliography:l3-45"
HEADER = "chp-21:21_CHP-21Bibliography:l1-1"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
SEGMENT_SHA = "1ee5744976bdd867c4482b078eeaf352b2596aed3a2b4c0585010e0e08c8183b"
BACKUP = ".bak-s2-chp21-bibliography-repositories-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
ARGS = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp = Path(handle.name)
    temp.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp = Path(handle.name)
    temp.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("bibliography Markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("bibliography PDF changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[2:45])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 segment text/hash changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage = read_csv(coverage_path)
statements = read_jsonl(statement_path)
if (len(candidates), len(mentions), len(statements), len(coverage)) != (11192, 25919, 11228, 832):
    raise SystemExit("unexpected bibliography S2 pre-state")

candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}
if SEGMENT not in coverage_by_id or (coverage_by_id[SEGMENT]["disposition"], coverage_by_id[SEGMENT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("repository-list segment is not queued")
if HEADER not in coverage_by_id or (coverage_by_id[HEADER]["disposition"], coverage_by_id[HEADER]["migration_status"]) != ("excluded", "complete"):
    raise SystemExit("generated-heading segment was not excluded")

candidate_specs = [
    ("cand-11214", "King’s College Library, Cambridge", "institution", 18, "Listed under Cambridge as a manuscript repository; current institutional name/continuity is not inferred."),
    ("cand-11215", "Archivio di Stato, Florence", "institution", 30, "Listed under Florence; kept distinct from the Rome, Venice, Verona, and branch-unspecified repositories until S3."),
    ("cand-11216", "Biblioteca Nazionale, Florence", "institution", 33, "Listed under Florence; kept distinct from the branch-unspecified Biblioteca Nazionale candidate until S3."),
    ("cand-11217", "Archivio della Compagnia di Gesù, Rome", "institution", 11, "Repository named in the bibliography under Rome; no modern institutional identity is inferred."),
    ("cand-11218", "Archivio Secreto Vaticano", "institution", 13, "Repository named in the printed source under Rome; historical source spelling is preserved."),
    ("cand-11219", "Archivio Storico Capitolino, Rome", "institution", 15, "Repository named in the bibliography under Rome; no current administrative identity is inferred."),
    ("cand-11220", "Accademia dei Concordi, Rovigo", "institution", 26, "Listed under Rovigo as a manuscript repository; current institutional identity is not independently checked."),
    ("cand-11221", "Chiesa del Gesù, Perugia", "place", 45, "Church named under Perugia in the manuscript-repository list; type preserves the physical church reference."),
    ("cand-11222", "Archivio di Stato, Verona", "institution", 36, "Listed under Verona; kept distinct from other State Archives until S3."),
    ("cand-11223", "Staatsarchiv, Hanover", "institution", 42, "Repository named under Hanover; distinct from the specific Schulenburg inventories cited elsewhere."),
    ("cand-11224", "Kunglige Biblioteket, Sweden", "institution", 45, "Repository named under Sweden; source wording is preserved and modern identity is not inferred."),
]
natural_keys = {
    (row["canonical_name"].strip().casefold(), row["suggested_type"].strip().casefold())
    for row in candidates
}
new_candidates = []
for candidate_id, name, kind, line_number, detail in candidate_specs:
    key = (name.strip().casefold(), kind.casefold())
    if candidate_id in candidate_by_id or key in natural_keys:
        raise SystemExit(f"candidate collision: {candidate_id} {name}")
    row = {field: "" for field in candidate_fields}
    row.update(
        candidate_id=candidate_id,
        canonical_name=name,
        suggested_type=kind,
        status="open",
        detail=detail,
        candidate_origin="body-mention",
        candidate_source_ref=f"{SEGMENT}#L{line_number}",
    )
    new_candidates.append(row)
    candidate_by_id[candidate_id] = row
    natural_keys.add(key)

# Exact locality grouping was verified against the bibliography PDF's first page;
# the OCR's two-column reading order interleaves some city headings.
repositories = [
    (12, "British Museum", "cand-5986", "London, Great Britain", 0, "institution"),
    (14, "Public Record Office", "cand-8289", "London, Great Britain", 0, "institution"),
    (18, "King’s College Library", "cand-11214", "Cambridge, Great Britain", 0, "institution"),
    (24, "Biblioteca Comunale", "cand-7386", "Bologna, Italy", 0, "institution"),
    (26, "Biblioteca Governativa", "cand-8556", "Cremona, Italy", 0, "institution"),
    (28, "Biblioteca Ariostea", "cand-7712", "Ferrara, Italy", 0, "institution"),
    (30, "Archivio di Stato", "cand-11215", "Florence, Italy", 0, "institution"),
    (31, "Biblioteca Laurenziana", "cand-9531", "Florence, Italy", 0, "institution"),
    (32, "Biblioteca Marucelliana", "cand-9493", "Florence, Italy", 0, "institution"),
    (33, "Biblioteca Nazionale", "cand-11216", "Florence, Italy", 0, "institution"),
    (34, "Soprintendenza alle Gallerie", "cand-8053", "Florence, Italy", 0, "institution"),
    (37, "Biblioteca Governativa", "cand-7803", "Lucca, Italy", 0, "institution"),
    (41, "Biblioteca Estense", "cand-8539", "Modena, Italy", 0, "institution"),
    (44, "Biblioteca Augusta", "cand-3531", "Perugia, Italy", 0, "institution"),
    (45, "Chiesa del Gesù", "cand-11221", "Perugia, Italy", 0, "place"),
    (9, "Accademia di S. Luca", "cand-3470", "Rome, Italy", 0, "institution"),
    (11, "Archivio della Compagnia di Gesù", "cand-11217", "Rome, Italy", 0, "institution"),
    (13, "Archivio Secreto Vaticano", "cand-11218", "Rome, Italy", 0, "institution"),
    (15, "Archivio Storico Capitolino", "cand-11219", "Rome, Italy", 0, "institution"),
    (17, "Biblioteca Vallicelliana", "cand-5605", "Rome, Italy; printed in parentheses", 0, "institution"),
    (18, "Archivio di Stato", "cand-5962", "Rome, Italy", 0, "institution"),
    (19, "Biblioteca Casanatense", "cand-3409", "Rome, Italy", 0, "institution"),
    (21, "Biblioteca Corsini", "cand-5131", "Rome, Italy", 0, "institution"),
    (23, "Biblioteca Vaticana", "cand-4380", "Rome, Italy", 0, "institution"),
    (24, "Museo di Roma", "cand-6030", "Rome, Italy; preceded by a printed mark", 0, "institution"),
    (26, "Accademia dei Concordi", "cand-11220", "Rovigo, Italy", 0, "institution"),
    (28, "Biblioteca Comunale", "cand-9450", "Treviso, Italy", 0, "institution"),
    (30, "Archivio di Stato", "cand-8592", "Venice, Italy", 1, "institution"),
    (31, "Biblioteca Correr", "cand-8262", "Venice, Italy", 0, "institution"),
    (32, "Biblioteca Marciana", "cand-9448", "Venice, Italy", 0, "institution"),
    (33, "Seminario Patriarcale", "cand-6589", "Venice, Italy", 0, "institution"),
    (36, "Archivio di Stato", "cand-11222", "Verona, Italy", 0, "institution"),
    (42, "Staatsarchiv", "cand-11223", "Hanover, Germany", 0, "institution"),
    (45, "Kunglige Biblioteket", "cand-11224", "Sweden", 0, "institution"),
]

mentions = list(mentions)
mention_keys = {
    (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"]))
    for row in mentions
}
new_mentions = []
line_offsets = {}
offset = 0
for line_number in range(3, 46):
    line_offsets[line_number] = offset
    offset += len(source_lines[line_number - 1]) + 1


def add_mention(line_number, surface, candidate_id, location, occurrence, kind):
    line = source_lines[line_number - 1]
    starts = []
    cursor = 0
    while True:
        found = line.find(surface, cursor)
        if found < 0:
            break
        starts.append(found)
        cursor = found + len(surface)
    if occurrence >= len(starts):
        raise SystemExit(f"missing mention L{line_number}: {surface} occurrence {occurrence}")
    start = line_offsets[line_number] + starts[occurrence]
    end = start + len(surface)
    if segment_text[start:end] != surface:
        raise SystemExit(f"mention offset mismatch L{line_number}: {surface}")
    key = (SEGMENT, candidate_id, str(start), str(end))
    if key in mention_keys or any(
        (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"])) == key
        for row in new_mentions
    ):
        raise SystemExit(f"duplicate mention L{line_number}: {surface}")
    row = {field: "" for field in mention_fields}
    row.update(
        mention_id=f"m-s2-chp21-repositories-{len(new_mentions) + 1:03d}",
        segment_id=SEGMENT,
        candidate_id=candidate_id,
        surface_form=surface,
        start_char=start,
        end_char=end,
        note=f"Printed bibliography repository list; locality from PDF physical page 1: {location}.",
    )
    new_mentions.append(row)


for line_number, surface, candidate_id, location, occurrence, kind in repositories:
    if candidate_id not in candidate_by_id:
        raise SystemExit(f"repository candidate missing: {candidate_id}")
    if candidate_by_id[candidate_id].get("suggested_type") != kind:
        raise SystemExit(f"repository candidate type mismatch: {candidate_id}")
    add_mention(line_number, surface, candidate_id, location, occurrence, kind)

scope_id = "st-chp21-bibliography-scope"
list_id = "st-chp21-bibliography-repository-list"
for statement_id in [scope_id, list_id]:
    if statement_id in statement_by_id:
        raise SystemExit(f"statement exists: {statement_id}")
scope_quote = source_lines[4]
list_quote = "\n".join(source_lines[6:45])
repository_ids = [item[2] for item in repositories]
new_statements = [
    {
        "statement_id": scope_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": None,
        "object_candidate_id": None,
        "predicate": "bibliography_scope_statement",
        "qualifiers": {
            "source_line_start": 5,
            "source_line_end": 5,
            "claim": "Haskell says the bibliography is selective, omits contributions not directly relevant to its purpose, and includes sources referred to in the text and notes.",
            "speaker": "Haskell",
            "text_layer": "bibliographic scope note",
            "qualification": "This describes the compilation’s selection rules and limitation, not completeness of the wider scholarship or any individual book claim.",
            "anonymous_author_format": "author names are bracketed",
            "journals_and_exhibition_catalogues_italicized": True,
            "relation_candidate": False,
            "mentioned_candidate_ids": [],
        },
        "original_quote": scope_quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
    },
    {
        "statement_id": list_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": None,
        "object_candidate_id": None,
        "predicate": "bibliography_lists_manuscript_repositories",
        "qualifiers": {
            "source_line_start": 7,
            "source_line_end": 45,
            "claim": "The bibliography names manuscript repositories grouped by locality; the list alone does not identify a particular manuscript or establish a separate holding claim for each item.",
            "speaker": "Haskell's bibliography",
            "text_layer": "repository directory",
            "qualification": "Locality grouping and cross-column order are checked against CHP-21Bibliography.pdf physical page 1; the source's historical names and uncertainty are preserved.",
            "relation_candidate": False,
            "mentioned_candidate_ids": list(dict.fromkeys(repository_ids)),
            "repositories": [
                {"candidate_id": cid, "surface_form": surface, "source_line": line_number, "locality": location}
                for line_number, surface, cid, location, occurrence, kind in repositories
            ],
        },
        "original_quote": list_quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
    },
]

coverage_row = coverage_by_id[SEGMENT]
coverage_row.update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L3-45",
    note="Bibliography purpose/selection statement and manuscript-repository directory reviewed. PDF physical page 1 resolves OCR's interleaved two-column localities; repository names are mentions with locality in notes. This section is not treated as art-historical prose or as proof of any particular manuscript holding.",
)

spans = sorted(
    (int(row["start_char"]), int(row["end_char"]), row["mention_id"])
    for row in [*mentions, *new_mentions]
    if row["segment_id"] == SEGMENT
)
for index, left in enumerate(spans):
    for right in spans[index + 1:]:
        if right[0] >= left[1]:
            break
        nested = (left[0] <= right[0] and right[1] <= left[1]) or (right[0] <= left[0] and left[1] <= right[1])
        if left[:2] == right[:2] or not nested:
            raise SystemExit(f"overlapping/duplicate repository mentions: {left[2]} / {right[2]}")

paths = [candidate_path, mention_path, statement_path, coverage_path]
backups = [path.with_name(path.name + BACKUP) for path in paths]
if ARGS.apply:
    present = [path.exists() for path in backups]
    if any(present) and not all(present):
        raise SystemExit("incomplete recovery backup set exists")
    if all(present):
        if any(hashlib.sha256(path.read_bytes()).digest() != hashlib.sha256(backup.read_bytes()).digest() for path, backup in zip(paths, backups)):
            raise SystemExit("existing backups differ from current pre-state")
    else:
        for path, backup in zip(paths, backups):
            shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, [*candidates, *new_candidates])
    write_csv(mention_path, mention_fields, [*mentions, *new_mentions])
    write_jsonl(statement_path, [*statements, *new_statements])
    write_csv(coverage_path, coverage_fields, coverage)
    print(f"applied bibliography lines 3-45: candidates +{len(new_candidates)}, mentions +{len(new_mentions)}, statements +{len(new_statements)}")
    print(f"recovery suffix {BACKUP}")
else:
    print(json.dumps({
        "mode": "dry-run",
        "segment": SEGMENT,
        "material": "bibliography scope note plus manuscript-repository directory",
        "repository_mentions": len(repositories),
        "new_candidates": [{"candidate_id": row["candidate_id"], "name": row["canonical_name"], "type": row["suggested_type"]} for row in new_candidates],
        "statements": [row["statement_id"] for row in new_statements],
        "coverage_after": "reviewed/complete L3-45",
    }, ensure_ascii=False, indent=2))
