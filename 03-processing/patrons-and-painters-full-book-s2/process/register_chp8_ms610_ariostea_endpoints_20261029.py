from __future__ import annotations

import argparse
import csv
import hashlib
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SEGMENT_ID = "chp-8:08_CHP-8_sec_ii:l372-461"
SOURCE_FILE = ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_ii.md"
MENTION_ID = "m-chp8-p222-n1-ariostea"
SURFACE = "Biblioteca Ariostea"
PATHS = {
    "cand-7711": "units/archives/antonelli-ms-610-ferrara-episcopal-palace-gallery-manuscript",
    "cand-7712": "units/institutions/biblioteca-ariostea-ferrara",
}
EXPECTED_DETAIL = (
    "Haskell identifies this manuscript in Biblioteca Ariostea, Ferrara, as the source for his account of Ruffo's palace. "
    "Its contents were not independently consulted; the title spelling is transcribed from the page image."
)
UPDATED_DETAIL = (
    "Haskell identifies this manuscript in Biblioteca Ariostea, Ferrara, as the source for his account of Ruffo's palace. "
    "Its contents and catalogue were not independently consulted. S0 OCR at L382 reads 'Calleria'; the physical print image "
    "(PDF p. 24) reads 'Galleria'."
)


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def unique_by(rows, field, value):
    matches = [row for row in rows if row.get(field) == value]
    if len(matches) != 1:
        raise SystemExit(f"expected one {field}={value!r}; found {len(matches)}")
    return matches[0]


candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
alignment_path = TABLES / "alignment.csv"
manifest_path = TABLES / "ku-manifest.csv"
accepted_path = ROOT / "04-knowledge" / "accepted.yml"
segments_path = TABLES / "segments.jsonl"

candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
alignment_fields, alignments = read_csv(alignment_path)
manifest_fields, manifest = read_csv(manifest_path)

segments = [json.loads(line) for line in segments_path.read_text(encoding="utf-8").splitlines() if line.strip()]
segment = unique_by(segments, "segment_id", SEGMENT_ID)
if segment["source_file"] != "02-sources/02-Markdown/08_CHP-8_sec_ii.md":
    raise SystemExit("unexpected source file for target segment")
if hashlib.sha256(SOURCE_FILE.read_bytes()).hexdigest() != segment["asset_sha256"]:
    raise SystemExit("source asset hash changed")
source_lines = SOURCE_FILE.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != segment["sha256"]:
    raise SystemExit("target segment content hash changed")
start = segment_text.index(SURFACE)
end = start + len(SURFACE)

if any(row["mention_id"] == MENTION_ID for row in mentions):
    raise SystemExit(f"mention already exists: {MENTION_ID}")
overlaps = [
    row for row in mentions
    if row["segment_id"] == SEGMENT_ID
    and start < int(row["end_char"])
    and int(row["start_char"]) < end
]
if overlaps:
    raise SystemExit(f"mention span overlaps existing rows: {overlaps}")

candidate = unique_by(candidates, "candidate_id", "cand-7711")
if candidate["detail"] != EXPECTED_DETAIL:
    raise SystemExit("cand-7711 detail changed since review")
for candidate_id, ku_id in PATHS.items():
    alignment = unique_by(alignments, "candidate_id", candidate_id)
    if alignment["decision"] != "new" or alignment["ku_id"]:
        raise SystemExit(f"unexpected S3/S4 state for {candidate_id}: {alignment}")
    if any(row["ku_id"] == ku_id for row in manifest):
        raise SystemExit(f"manifest entry already exists: {ku_id}")
    card = ROOT / "04-knowledge" / f"{ku_id}.md"
    if not card.is_file():
        raise SystemExit(f"new card is missing: {card}")

if any(row["mention_id"] == MENTION_ID for row in mentions):
    raise SystemExit("duplicate mention ID")
mention = {
    "mention_id": MENTION_ID,
    "segment_id": SEGMENT_ID,
    "candidate_id": "cand-7712",
    "surface_form": SURFACE,
    "start_char": str(start),
    "end_char": str(end),
    "note": "Haskell identifies the manuscript's reported repository; the current holding was not independently checked.",
}
manifest_additions = [
    {
        "ku_id": ku_id,
        "type": "archive" if candidate_id == "cand-7711" else "institution",
        "canonical_name": (
            "安东内利藏品第610号费拉拉主教宫画廊手稿"
            if candidate_id == "cand-7711"
            else "费拉拉阿里奥斯托图书馆"
        ),
        "name_en": (
            "Collezione Antonelli MS. 610: Galleria di Pitture raccolte, ed esposte nel Palazzo Vescovale di Ferrara"
            if candidate_id == "cand-7711"
            else "Biblioteca Ariostea, Ferrara"
        ),
        "source_task": "patrons-and-painters-full-book-s2",
        "card_path": f"04-knowledge/{ku_id}.md",
    }
    for candidate_id, ku_id in PATHS.items()
]
accepted_lines = [f"- 04-knowledge/{ku_id}.md" for ku_id in PATHS.values()]

preview = {
    "mode": "dry-run",
    "s3_decisions_preserved": {candidate_id: "new" for candidate_id in PATHS},
    "s4_mappings": PATHS,
    "restored_mention": {**mention, "source_slice": segment_text[start:end]},
    "candidate_detail_change": {"cand-7711": {"before": EXPECTED_DETAIL, "after": UPDATED_DETAIL}},
    "manifest_additions": manifest_additions,
    "accepted_additions": accepted_lines,
}

parser = argparse.ArgumentParser(description="Register the two S3-new Chapter 8 manuscript/repository endpoints.")
parser.add_argument("--apply", action="store_true", help="apply the reviewed registration and mention repair")
args = parser.parse_args()
if not args.apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)

candidate["detail"] = UPDATED_DETAIL
mentions.append(mention)
for candidate_id, ku_id in PATHS.items():
    unique_by(alignments, "candidate_id", candidate_id)["ku_id"] = ku_id
manifest.extend(manifest_additions)

accepted_raw = accepted_path.read_bytes().decode("utf-8")
line_ending = "\r\n" if "\r\n" in accepted_raw else "\n"
marker = f"claims:{line_ending}"
if accepted_raw.count(marker) != 1:
    raise SystemExit("accepted.yml lacks a unique claims section marker")
accepted_raw = accepted_raw.replace(marker, line_ending.join(accepted_lines) + line_ending + marker, 1)

write_csv_atomic(candidate_path, candidate_fields, candidates)
write_csv_atomic(mention_path, mention_fields, mentions)
write_csv_atomic(alignment_path, alignment_fields, alignments)
write_csv_atomic(manifest_path, manifest_fields, manifest)
accepted_path.write_bytes(accepted_raw.encode("utf-8"))
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
