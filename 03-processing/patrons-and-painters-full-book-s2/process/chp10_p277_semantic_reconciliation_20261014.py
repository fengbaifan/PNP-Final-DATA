"""Resolve p.277 S2 statements and its linked p.278 sentence continuation."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "02-sources/02-Markdown/10_CHP-10_intro.md"
PDF = ROOT / "02-sources/01-book/CHP-10.pdf"
TABLES = ROOT / "04-knowledge/tables"
BODY = "chp-10:10_CHP-10_intro:l15-24"
CONTINUATION = "chp-10:10_CHP-10_intro:l26-41"
NEW_STATEMENT = "st-chp10-p277-crozat-met-watteau"
NEW_MENTION = "m-chp10-p277-foreigners-clientele"
BACKUP_SUFFIX = ".bak-s2-chp10-p277-semantic-reconciliation-20261014"

EXPECTED_SHA256 = {
    SOURCE: "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f",
    PDF: "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb",
    TABLES / "entity-candidates.csv": "e2099a487fe6dd6bf8ac27d968e9faaf4a9f0425e3b753e5ecbb850a9a42de15",
    TABLES / "mentions.csv": "279f17a6df73151841fb77d18b27946537a3661b5bb890e787b779de5ba2ef5d",
    TABLES / "book-statements.jsonl": "aebdb03ab023636df8dd470e64b2d8471467c66ab5562f62725a043516fe5f06",
    TABLES / "s2-coverage.csv": "215a6273f231eb408a8e290d1d72a52249e7422b438b663d13b3153d73366097",
}
SEGMENT_SHA256 = {
    BODY: "805e94a2f007dadc0e072f08626951f78aa77c3f304e43af0768aff09c9746ed",
    CONTINUATION: "11109dec2da0c22589297ae786772e434dfb0571e62cde36113512f37e6db0ab",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp_path = Path(handle.name)
    temp_path.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp_path = Path(handle.name)
    temp_path.replace(path)


for path, expected in EXPECTED_SHA256.items():
    actual = sha256(path)
    if actual != expected:
        raise SystemExit(f"input changed: {path.relative_to(ROOT)} sha256={actual}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if "foreigners" not in source_lines[21] or "whom he met on his return to France at the end of the year" not in source_lines[21]:
    raise SystemExit("p.277 Crozat/foreign-client text anchors changed")
segment_rows = [json.loads(line) for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
segment_by_id = {row["segment_id"]: row for row in segment_rows}
for segment_id, expected in SEGMENT_SHA256.items():
    if segment_by_id.get(segment_id, {}).get("sha256") != expected:
        raise SystemExit(f"source segment changed: {segment_id}")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage = read_csv(coverage_path)
statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]

candidate_by_id = {row["candidate_id"]: row for row in candidates}
mention_ids = {row["mention_id"] for row in mentions}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}
if max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates) != 12107:
    raise SystemExit("candidate sequence changed")
if NEW_MENTION in mention_ids or NEW_STATEMENT in statement_by_id:
    raise SystemExit("planned p.277 row already exists")

CLASSIFICATIONS = {
    "st-chp10-p277-republic-not-impoverished": False,
    "st-chp10-p277-venetian-inhabitants-stereotype": False,
    "st-chp10-p277-venetian-palaces-art": False,
    "st-chp10-p277-courtesans-reputation": False,
    "st-chp10-p277-carriera-foreign-work": True,
    "st-chp10-p277-crozat-description-of-watteau": True,
    "st-chp10-p277-french-collector-crozat": False,
    "st-chp10-p277-visitors-agree-carriera-merits": True,
    "st-chp10-p277-incomplete-commission-contrast": False,
    "st-chp10-p278-taste-divergence-closure": False,
}
if not set(CLASSIFICATIONS) <= statement_by_id.keys():
    raise SystemExit("one or more p.277/278 source statements are missing")
for statement_id in CLASSIFICATIONS:
    row = statement_by_id[statement_id]
    expected_segment = CONTINUATION if statement_id == "st-chp10-p278-taste-divergence-closure" else BODY
    if row.get("segment_id") != expected_segment or row.get("qualifiers", {}).get("relation_candidate") is not None:
        raise SystemExit(f"target statement changed or is already classified: {statement_id}")

new_candidate_id = "cand-12108"
if new_candidate_id in candidate_by_id or any(row["canonical_name"] == "Foreign clientele of Rosalba Carriera before the 1721 Crozat visit (membership unknown)" for row in candidates):
    raise SystemExit("foreign-client group candidate already exists")
new_candidate = {
    "candidate_id": new_candidate_id,
    "index_entry_id": "",
    "canonical_name": "Foreign clientele of Rosalba Carriera before the 1721 Crozat visit (membership unknown)",
    "index_page_range": "",
    "suggested_type": "",
    "status": "open",
    "index_source_file": "",
    "sub_entry": "",
    "detail": "Haskell says Carriera had worked mainly for foreigners before Crozat's 1721 visit. The source does not identify individual clients or establish that the later English, French, and German visitor group is identical to this clientele; type and membership remain unresolved.",
    "exclude_reason": "",
    "candidate_origin": "body-mention",
    "candidate_source_ref": f"{BODY}#L22",
}

segment_start, segment_end = 15, 24
segment_text = "\n".join(source_lines[segment_start - 1:segment_end])
line_offset = sum(len(line) + 1 for line in source_lines[segment_start - 1:21])
surface = "foreigners"
pos = source_lines[21].find(surface)
if pos < 0 or source_lines[21].find(surface, pos + 1) >= 0:
    raise SystemExit("expected unique p.277 foreigners span changed")
start, end = line_offset + pos, line_offset + pos + len(surface)
if segment_text[start:end] != surface:
    raise SystemExit("foreign-client mention span does not match the source segment")
new_mention = {
    "mention_id": NEW_MENTION,
    "segment_id": BODY,
    "candidate_id": new_candidate_id,
    "surface_form": surface,
    "start_char": str(start),
    "end_char": str(end),
    "note": "Broad, unnamed client group in Haskell's p.277 summary; do not merge with the explicitly named visitor nationalities later on the page.",
}

foreign_row = statement_by_id["st-chp10-p277-carriera-foreign-work"]
foreign_row["object_candidate_id"] = new_candidate_id
foreign_row["predicate"] = "rosalba_worked_mainly_for_unnamed_foreign_clients_before_1721"
foreign_row["qualifiers"]["qualification"] = "Broad authorial summary; the passage gives no proportion, exhaustive client list, or exact start date. Keep this source-limited clientele separate from the English, French, and German visitor group in the following sentence."
foreign_row["qualifiers"]["mentioned_candidate_ids"] = ["cand-0581", "cand-0894", new_candidate_id]

crozat_row = statement_by_id["st-chp10-p277-crozat-description-of-watteau"]
crozat_row["qualifiers"]["claim"] = "Haskell reports Crozat's view that Watteau was the only artist able to produce something worthy of Rosalba's work."
crozat_row["qualifiers"]["qualification"] = "Nested quotation in Haskell's account; footnote 4 cites Malamani and Sensier, neither of which was independently consulted. The separate meeting clause is recorded in its own statement."
crozat_row["qualifiers"]["mentioned_candidate_ids"] = ["cand-0581", "cand-0894", "cand-2804"]
crozat_row["original_quote"] = "the only man ‘able to produce something worthy of you’"

visitors_row = statement_by_id["st-chp10-p277-visitors-agree-carriera-merits"]
visitors_row["qualifiers"]["qualification"] = "Group-level reception reported by Haskell; it does not establish that every visitor agreed, and no particular Carriera artwork is identified."

new_statement = {
    "statement_id": NEW_STATEMENT,
    "segment_id": BODY,
    "subject_candidate_id": "cand-0894",
    "object_candidate_id": "cand-2804",
    "predicate": "crozat_met_watteau_on_return_to_france",
    "qualifiers": {
        "source_line_start": 22,
        "source_line_end": 22,
        "printed_page": 277,
        "pdf_physical_page": 2,
        "claim": "Haskell says Crozat met Watteau on his return to France at the end of the year.",
        "speaker": "Haskell",
        "text_layer": "authorial narrative",
        "qualification": "The clause follows the account of Crozat's 1715 visit to Rosalba, but does not repeat the year in the meeting clause; the underlying account was not independently checked.",
        "mentioned_candidate_ids": ["cand-0894", "cand-2804", "cand-5317"],
        "relation_candidate": True,
    },
    "original_quote": "this artist whom he met on his return to France at the end of the year",
    "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
    "origin": "book",
}

for statement_id, value in CLASSIFICATIONS.items():
    statement_by_id[statement_id]["qualifiers"]["relation_candidate"] = value

if not {"cand-0581", "cand-0894", "cand-2804", new_candidate_id} <= set(candidate_by_id) | {new_candidate_id}:
    raise SystemExit("p.277 relation endpoints are incomplete")

p277_cov = coverage_by_id[BODY]
p278_cov = coverage_by_id[CONTINUATION]
if (p277_cov["disposition"], p277_cov["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("p.277 coverage state changed")
if (p278_cov["disposition"], p278_cov["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("p.278 continuation coverage state changed")
p277_cov["note"] += " 2026-10-14 semantic reconciliation reviewed all nine existing p.277 statements, added the source-limited foreign-client group candidate and mention, split Crozat's meeting with Watteau from his evaluation of Watteau, and classified the cross-page p.278 sentence continuation. The foreign-client group membership remains unknown."
p278_cov["note"] += " 2026-10-14 semantic reconciliation classified the p.277 taste-divergence continuation as a general source claim without identified endpoints; it is linked to the p.277 opening fragment."

for statement_id, row in statement_by_id.items():
    if statement_id == NEW_STATEMENT:
        refs = {row.get("subject_candidate_id"), row.get("object_candidate_id"), *row["qualifiers"]["mentioned_candidate_ids"]} - {None}
        if not refs <= set(candidate_by_id) | {new_candidate_id}:
            raise SystemExit("new Crozat/Watteau statement has an unresolved candidate FK")

print(json.dumps({
    "source": "p.277, CHP-10.pdf physical page 2; plus the p.278 L27 continuation",
    "page_scan_sha256": EXPECTED_SHA256[PDF],
    "existing_statements_classified": len(CLASSIFICATIONS),
    "new_candidate": new_candidate["candidate_id"],
    "new_mention": {"id": NEW_MENTION, "span": [start, end], "surface": surface},
    "new_statement": NEW_STATEMENT,
    "planned_totals": {
        "candidates": len(candidates) + 1,
        "mentions": len(mentions) + 1,
        "statements": len(statements) + 1,
        "p277_p278_true": sum(CLASSIFICATIONS.values()) + 1,
        "p277_p278_false": len(CLASSIFICATIONS) - sum(CLASSIFICATIONS.values()),
        "p277_p278_unset": 0,
    },
}, ensure_ascii=False, indent=2))

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
if args.apply:
    paths = [candidate_path, mention_path, statement_path, coverage_path]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("recovery backup already exists; inspect before retrying")
    for source, backup in zip(paths, backups):
        shutil.copy2(source, backup)
    try:
        write_csv(candidate_path, candidate_fields, candidates + [new_candidate])
        write_csv(mention_path, mention_fields, mentions + [new_mention])
        write_jsonl(statement_path, statements + [new_statement])
        write_csv(coverage_path, coverage_fields, coverage)
    except Exception:
        for target, backup in zip(paths, backups):
            shutil.copy2(backup, target)
        raise
    print("APPLIED; backups=" + ", ".join(str(path.relative_to(ROOT)) for path in backups))
