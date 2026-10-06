"""Reconcile composite p.211 note OCR with the already processed visual transcription."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
COMPOSITE_ID = "chp-8:08_CHP-8_sec_i:l126-157"
VISUAL_ID = "chp-8:08_CHP-8_sec_i_notes_p211_visual-transcription:l1-4"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_i.md"
VISUAL_REL = "02-sources/02-Markdown/08_CHP-8_sec_i_notes_p211_visual-transcription.md"
SEGMENT_REL = "04-knowledge/tables/segments.jsonl"
BACKUP_SUFFIX = ".bak-s2-chp8-p211-overlap-20261001"
EXPECTED_COMPOSITE_LINES = [
    "1 The main sources for the collection of the del Rosso brothers are the account given of it in 1677 by Cinelli and the complete inventory drawn up twelve years later by Andrea del Rosso himself published in Gualandi, II, pp. 113-28. Both these documents provide a certain amount of incidental biographical information. To supplement these I have drawn heavily on a number of published and manuscript sources in Florentine archives and libraries. I am most grateful to Dottoressa Paola Zambelli of the Archivio di Stato for her help. ' ’ General information about the family and genealogies exist in the manuscript collections of Passerini in the Biblioteca Nazionale—in particular, Passerini 19(25): Informazione sopra la Nobiltà della Famiglia del Rosso di Firenze mandata a i SStri Falconieri di Roma, da me GiotBatta Dei, quest’anno 1747. There are also a number of references drawn from a variety of sources in the Poligrafo Gargano in the same library.",
    "2 A copy of the decree conferring the Appalto Generale della rendita della Farine della Città, e Dominio di Firenze for nine years as from I June 1676 is preserved in the Archivio di Stato—Miscellanea Medicea 533, Uffizio delle Farine, and some information about its functioning can be found elsewhere in the same collection of documents.",
    "8 Baldinucci, VI, 1728, p. 500. This picture, which is still at Burghley, was exhibited in London in i960—Italian Art and Britain, p. 24.",
]
VISUAL_LINE_PREFIX = "1 The main sources for the collection of the del Rosso brothers are the account given of it in 1677 by Cinelli and the complete inventory drawn up twelve years later by Andrea del Rosso himself published in Gualandi, II, pp. 113-28."
STATEMENT_ID = "st-chp8-p211-principal-sources-for-del-rosso-collection"
MENTION_ID = "m-chp8-p211-060"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl_atomic(path: Path, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
segment_path = TABLES / "segments.jsonl"

candidate_fields, candidate_rows = read_csv(candidate_path)
mention_fields, mention_rows = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statement_rows = read_jsonl(statement_path)
segment_rows = read_jsonl(segment_path)
segments = {row["segment_id"]: row for row in segment_rows}
candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
mention_by_id = {row["mention_id"]: row for row in mention_rows}
statement_by_id = {row["statement_id"]: row for row in statement_rows}
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}

for segment_id, source_rel, expected_range in [
    (COMPOSITE_ID, SOURCE_REL, (126, 157)),
    (VISUAL_ID, VISUAL_REL, (1, 4)),
]:
    segment = segments.get(segment_id)
    if not segment or segment["source_file"] != source_rel:
        raise SystemExit(f"missing/changed segment metadata: {segment_id}")
    if (int(segment["line_start"]), int(segment["line_end"])) != expected_range:
        raise SystemExit(f"unexpected segment line range: {segment_id}")
    source_path = ROOT / source_rel
    if hashlib.sha256(source_path.read_bytes()).hexdigest() != segment["asset_sha256"]:
        raise SystemExit(f"source asset fingerprint changed: {source_rel}")
    source_lines = source_path.read_text(encoding="utf-8-sig").splitlines()
    section_lines = source_lines[expected_range[0] - 1: expected_range[1]]
    if hashlib.sha256("\n".join(section_lines).encode("utf-8")).hexdigest() != segment["sha256"]:
        raise SystemExit(f"source segment hash changed: {segment_id}")

composite_source = (ROOT / SOURCE_REL).read_text(encoding="utf-8-sig").splitlines()
if composite_source[145:148] != EXPECTED_COMPOSITE_LINES:
    raise SystemExit("p.211 composite OCR lines changed; re-review before reconciliation")
visual_source = (ROOT / VISUAL_REL).read_text(encoding="utf-8-sig").splitlines()
if len(visual_source) != 4 or not visual_source[0].startswith(VISUAL_LINE_PREFIX):
    raise SystemExit("p.211 visual transcription changed; compare overlap before reuse")

if coverage_by_id[COMPOSITE_ID]["source_line_ranges"] != "L127-145":
    raise SystemExit("composite coverage no longer ends at L145")
if (coverage_by_id[COMPOSITE_ID]["disposition"], coverage_by_id[COMPOSITE_ID]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("unexpected composite-note coverage status")
if (coverage_by_id[VISUAL_ID]["disposition"], coverage_by_id[VISUAL_ID]["migration_status"], coverage_by_id[VISUAL_ID]["source_line_ranges"]) != ("reviewed", "complete", "L1-4"):
    raise SystemExit("p.211 visual transcription is not already complete; do not reuse blindly")

if MENTION_ID not in mention_by_id or mention_by_id[MENTION_ID]["candidate_id"] != "cand-7501":
    raise SystemExit("expected Gualandi mention is missing or remapped")
if mention_by_id[MENTION_ID]["note"] != "Cited publication location for the inventory, pp.113-128.":
    raise SystemExit("Gualandi mention note changed; review before correcting")
if STATEMENT_ID not in statement_by_id:
    raise SystemExit("p.211 principal-sources statement is missing")
statement = statement_by_id[STATEMENT_ID]
if statement["segment_id"] != VISUAL_ID or "pp. 113-28" not in statement["original_quote"]:
    raise SystemExit("p.211 statement no longer matches expected transcription")
for cid in ("cand-7500", "cand-7501"):
    if cid not in candidate_by_id or "pp.113-128" not in candidate_by_id[cid]["detail"]:
        raise SystemExit(f"expected old Gualandi locator is missing from {cid}")

candidate_new = [dict(row) for row in candidate_rows]
for row in candidate_new:
    if row["candidate_id"] in {"cand-7500", "cand-7501"}:
        row["detail"] = row["detail"].replace("pp.113-128", "pp.115-128")
mention_new = [dict(row) for row in mention_rows]
for row in mention_new:
    if row["mention_id"] == MENTION_ID:
        row["note"] = "Cited publication location for the inventory, pp.115-128 (print; section OCR and visual transcription read 113-28)."
statement_new = [dict(row) for row in statement_rows]
for row in statement_new:
    if row["statement_id"] == STATEMENT_ID:
        q = dict(row["qualifiers"])
        q["claim"] = "Haskell identifies Cinelli's 1677 account and Andrea del Rosso's complete inventory, drawn up twelve years later and published in Gualandi volume II, pp.115-128, as principal sources for the brothers' collection."
        q["qualification"] = "The cited account, inventory and publication are bibliographic or archival locators; neither document was independently consulted here. The printed page locator is pp.115-128; both the composite OCR and the visual transcription read 113-28."
        q["citations"] = [{"source_candidate_id": "cand-7501", "volume": "II", "page_start": "115", "page_end": "128"}]
        corrections = list(q.get("ocr_corrections", []))
        corrections.extend([
            {"source_file": SOURCE_REL, "source_line": 146, "ocr": "pp. 113-28", "print": "pp. 115-28", "basis": "CHP-8.pdf physical page 9."},
            {"source_file": VISUAL_REL, "source_line": 1, "ocr": "pp. 113-28", "print": "pp. 115-28", "basis": "CHP-8.pdf physical page 9."},
            {"source_file": SOURCE_REL, "source_line": 148, "ocr": "8 Baldinucci", "print": "3 Baldinucci", "basis": "CHP-8.pdf physical page 9."},
            {"source_file": SOURCE_REL, "source_line": 148, "ocr": "i960", "print": "1960", "basis": "CHP-8.pdf physical page 9."},
        ])
        q["ocr_corrections"] = corrections
        row["qualifiers"] = q

coverage_new = []
for row in coverage_rows:
    copied = dict(row)
    if copied["segment_id"] == COMPOSITE_ID:
        copied["source_line_ranges"] = "L127-148"
        copied["note"] += " L146-148 (p.211 notes 1-3) were compared with the already complete visual-transcription segment chp-8:08_CHP-8_sec_i_notes_p211_visual-transcription:l1-4 and physical page 9. The visual segment already carries 22 mentions and 8 statements, so no duplicate rows were created. Reused its page-image readings for the overlap; corrected the Gualandi inventory locator from 113-28 to printed 115-28 in S2 metadata. p.212-214 notes L149-157 remain pending; p.214 note 4 still requires image-based completion."
    coverage_new.append(copied)


def preview():
    print("validated composite source L146-148 and complete p.211 visual segment L1-4")
    print("overlap result: p.211 notes 1-3 already represented by 22 mentions and 8 statements")
    print("new mentions/statements: 0; no duplicate rows planned")
    print("corrected print locator: Gualandi II pp.115-128 (OCR/transcription pp.113-128)")
    print("composite-note coverage: L127-148, still partial; next L149-157")


def apply():
    paths = [candidate_path, mention_path, statement_path, coverage_path]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("one or more recovery backups already exist; inspect before retrying")
    for source, backup in zip(paths, backups):
        shutil.copy2(source, backup)
    write_csv_atomic(candidate_path, candidate_fields, candidate_new)
    write_csv_atomic(mention_path, mention_fields, mention_new)
    write_jsonl_atomic(statement_path, statement_new)
    write_csv_atomic(coverage_path, coverage_fields, coverage_new)
    print("APPLIED; recovery backups retained pending audits:")
    for backup in backups:
        print(backup.relative_to(ROOT))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after all preflight checks pass")
    args = parser.parse_args()
    preview()
    if args.apply:
        apply()
    else:
        print("DRY RUN: no files written")


if __name__ == "__main__":
    main()
