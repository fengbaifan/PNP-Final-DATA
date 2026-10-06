"""Controlled S2 migration for the p.310 Schulenburg section opening."""
import argparse
import csv
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_sec_ii.md"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_sec_ii.md"
SEGMENT = "chp-10:10_CHP-10_sec_ii:l3-5"
EXPECTED_ASSET_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
EXPECTED_SEGMENT_SHA = "0ed00d7c5e58ddce2377dcd19f0e1c4b37a175c79004f7a230faa08e40b253a1"
BACKUP_SUFFIX = ".bak-s2-chp10-sec-ii-l3-5-20261002"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("source asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[2:5])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != EXPECTED_SEGMENT_SHA:
    raise SystemExit("S2 segment changed")
if source_lines[2] != "MARSHAL SCHULENBURG" or "There is no record that they were on close terms" not in segment_text:
    raise SystemExit("section opening changed")

cp, mp, sp, vp = [TABLES / name for name in (
    "entity-candidates.csv", "mentions.csv", "book-statements.jsonl", "s2-coverage.csv"
)]
cf, candidates = read_csv(cp)
mf, mentions = read_csv(mp)
vf, coverage = read_csv(vp)
statements = read_jsonl(sp)
cids = {row["candidate_id"] for row in candidates}
mids = {row["mention_id"] for row in mentions}
sids = {row["statement_id"] for row in statements}
cov = {row["segment_id"]: row for row in coverage}
maximum = max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates)
if (len(candidates), maximum) != (9554, 9567):
    raise SystemExit(f"candidate state changed: {len(candidates)}, {maximum}")
if (cov[SEGMENT]["disposition"], cov[SEGMENT]["migration_status"], cov[SEGMENT]["source_line_ranges"]) != ("queued", "pending", ""):
    raise SystemExit(f"coverage state changed: {cov[SEGMENT]}")
ENTITIES = {"schulenburg": "cand-2401", "smith": "cand-2440", "venice": "cand-2738"}
for key, cid in ENTITIES.items():
    if cid not in cids:
        raise SystemExit(f"candidate missing: {key} {cid}")

new_mentions = []
new_statements = []
new_mids = set()
new_sids = set()


def add_mention(mid, line_no, surface, cid, note=""):
    if mid in mids or mid in new_mids or cid not in cids:
        raise SystemExit(f"mention precondition failed: {mid} -> {cid}")
    line = source_lines[line_no - 1]
    local = line.find(surface)
    if local < 0:
        raise SystemExit(f"surface not found on L{line_no}: {surface!r}")
    prefix = "\n".join(source_lines[2:line_no - 1])
    start = len(prefix) + (1 if prefix else 0) + local
    new_mentions.append({"mention_id": mid, "segment_id": SEGMENT, "candidate_id": cid,
                         "surface_form": surface, "start_char": str(start),
                         "end_char": str(start + len(surface)), "note": note})
    new_mids.add(mid)


add_mention("m-s2-ch10-sec-ii-opening-schulenburg", 5, "Marshal Schulenburg", "cand-2401",
            "Person named by the section subheading and identified in the opening comparison; index-candidate identity remains for S3.")
add_mention("m-s2-ch10-sec-ii-opening-smith", 4, "Joseph Smith", "cand-2440",
            "Collector used as the comparison point.")
add_mention("m-s2-ch10-sec-ii-opening-venice", 4, "Venice", "cand-2738",
            "Place where the two collectors commissioned and collected pictures.")
add_mention("m-s2-ch10-sec-ii-opening-english-consul", 5, "English Consul", "cand-2440",
            "Corefers to Joseph Smith in this comparative passage.")


def add_statement(sid, subject, obj, predicate, claim, lines, speaker, layer, qualification,
                  mentioned, relation=False):
    if sid in sids or sid in new_sids:
        raise SystemExit(f"duplicate statement ID: {sid}")
    first, last = lines
    quote = "\n".join(source_lines[first - 1:last])
    q = {"source_line_start": first, "source_line_end": last, "printed_page": 310,
         "pdf_physical_page": 39, "claim": claim, "speaker": speaker, "text_layer": layer,
         "qualification": qualification,
         "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
         "relation_candidate": relation}
    new_statements.append({"statement_id": sid, "segment_id": SEGMENT,
                           "subject_candidate_id": subject, "object_candidate_id": obj,
                           "predicate": predicate, "qualifiers": q,
                           "original_quote": quote, "source_file": SOURCE_FILE, "origin": "book"})
    new_sids.add(sid)


add_statement("st-chp10-p310-schulenburg-venetian-collector", "cand-2401", "cand-2738",
              "commissioned_and_collected_pictures_in_venice",
              "Haskell introduces Marshal Schulenburg as a foreigner who commissioned and collected pictures in Venice at approximately the same time as Joseph Smith.",
              (4, 5), "Haskell", "authorial narrative",
              "The relative chronology is approximate; no exact date is given in this opening paragraph.",
              ["cand-2401", "cand-2440", "cand-2738"])
add_statement("st-chp10-p310-schulenburg-smith-aesthetic-contrast", "cand-2401", "cand-2440",
              "background_activity_and_aesthetic_tastes_contrasted",
              "Haskell says the contrasts between Schulenburg's and Smith's backgrounds and activities are closely reflected in their aesthetic tastes.",
              (4, 5), "Haskell", "authorial comparative interpretation",
              "This records Haskell's comparative interpretation, not a claim that the two men had a personal relationship.",
              ["cand-2401", "cand-2440"])
add_statement("st-chp10-p310-schulenburg-no-close-terms-recorded", "cand-2401", "cand-2440",
              "no_record_of_close_terms",
              "Haskell says there is no record that Schulenburg and Smith were on close terms.",
              (5, 5), "Haskell", "authorial report about the record",
              "This is a statement about absence of a record, not evidence that the two men had no contact or were not close.",
              ["cand-2401", "cand-2440"])
add_statement("st-chp10-p310-schulenburg-shared-artists-distinct-collections", "cand-2401", "cand-2440",
              "often_employed_same_artists_but_collections_differed",
              "Haskell says the two collectors often employed the same artists, while their collections were very different.",
              (5, 5), "Haskell", "authorial comparative statement",
              "The artists are not identified in this paragraph; no person-to-artist relations are inferred here.",
              ["cand-2401", "cand-2440"])

for row in new_statements:
    for cid in [row["subject_candidate_id"], row["object_candidate_id"], *row["qualifiers"]["mentioned_candidate_ids"]]:
        if cid and cid not in cids:
            raise SystemExit(f"missing candidate FK: {row['statement_id']} -> {cid}")
cov[SEGMENT].update({"disposition": "reviewed", "migration_status": "complete",
                     "source_line_ranges": "L3-5",
                     "note": "Printed p.310 section opening checked against the lower portion of CHP-10.pdf physical page 39. The subheading names Marshal Schulenburg; the paragraph contrasts his Venetian collecting and artistic tastes with Joseph Smith, preserves Haskell's 'no record' wording, and does not infer personal closeness or named artist relations."})

summary = {"mode": "APPLY" if __import__("sys").argv[-1:] == ["--apply"] else "DRY-RUN",
           "segment": SEGMENT, "new_candidates": 0, "new_mentions": len(new_mentions),
           "new_statements": len(new_statements), "coverage": "L3-5 complete"}
print(json.dumps(summary, ensure_ascii=True, indent=2))
if __import__("sys").argv[-1:] == ["--apply"]:
    for path in (mp, sp, vp):
        backup = Path(str(path) + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists: {backup}")
        shutil.copy2(path, backup)
    write_csv(mp, mf, mentions + new_mentions)
    write_jsonl(sp, statements + new_statements)
    write_csv(vp, vf, [cov[row["segment_id"]] for row in coverage])
    print("Applied with three recoverable backups.")
