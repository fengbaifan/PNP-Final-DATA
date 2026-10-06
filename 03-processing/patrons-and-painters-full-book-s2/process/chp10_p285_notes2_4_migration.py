"""Controlled S2 migration for p.285 notes 2-4 at merged source L529-L531."""
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
NOTES_SEGMENT = "chp-10:10_CHP-10_intro:l491-634"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_NOTES_SHA = "33d2557d3e681434a9c964316a7a24fe2c00faa934add1381c12fc4d8a7c7f76"
EXPECTED_LINES_SHA = "0825e13a6b2ec0521ab0d634f42262e3aff5c69646a0acc7b874f91d31fe5386"
BACKUP = ".bak-s2-chp10-p285-notes2-4-20261002"


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
src = SOURCE.read_text(encoding="utf-8-sig").splitlines()
notes_body = "\n".join(src[490:634])
if hashlib.sha256(notes_body.encode("utf-8")).hexdigest() != EXPECTED_NOTES_SHA:
    raise SystemExit("merged note segment changed")
if hashlib.sha256("\n".join(src[528:531]).encode("utf-8")).hexdigest() != EXPECTED_LINES_SHA:
    raise SystemExit("p.285 notes 2-4 changed")
if not src[528].startswith("2 Quoted by Sensier") or not src[529].startswith("3 For the Couvent des Augustins") or not src[530].startswith("4 Sensier"):
    raise SystemExit("p.285 footnote markers or text changed")

cp, mp, sp, vp = [TABLES / name for name in ("entity-candidates.csv", "mentions.csv", "book-statements.jsonl", "s2-coverage.csv")]
cf, candidates = read_csv(cp)
mf, mentions = read_csv(mp)
vf, coverage = read_csv(vp)
statements = read_jsonl(sp)
cids = {row["candidate_id"] for row in candidates}
mids = {row["mention_id"] for row in mentions}
sids = {row["statement_id"] for row in statements}
cov = {row["segment_id"]: row for row in coverage}
maximum = max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates)
if maximum != 9343:
    raise SystemExit(f"candidate sequence changed: {maximum}")
notes_cov = cov.get(NOTES_SEGMENT)
if not notes_cov or (notes_cov["disposition"], notes_cov["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("merged note coverage status changed")
if notes_cov["source_line_ranges"] != "L492-528":
    raise SystemExit(f"merged note coverage range changed: {notes_cov['source_line_ranges']}")

TARGETS = {
    "st-chp10-p285-mariette-assessment": (2, 529),
    "st-chp10-p285-pellegrini-other-paris-works": (3, 530),
    "st-chp10-p285-carriera-academie-admission": (4, 531),
}
by_sid = {row["statement_id"]: row for row in statements}
if not set(TARGETS) <= by_sid.keys():
    raise SystemExit(f"p.285 body note targets missing: {set(TARGETS)-by_sid.keys()}")
for sid, (marker, source_line) in TARGETS.items():
    q = by_sid[sid].get("qualifiers", {})
    if q.get("footnote_marker") != marker or not q.get("footnote_text_pending"):
        raise SystemExit(f"p.285 marker {marker} state changed on {sid}")

required_existing = {"cand-7137", "cand-9290", "cand-9291"}
if not required_existing <= cids:
    raise SystemExit(f"required existing candidates missing: {required_existing-cids}")
NEW_CANDIDATE = (
    "cand-9344", "Couvent des Augustins Déchaussés (Paris convent/place named in p.285 note 3)", "place",
    "Haskell's p.285 note 3 points to the Couvent des Augustins Déchaussés via Sensier, p.107, in the context of Pellegrini's statement that he painted at least one Paris altarpiece. The cited page was not consulted; the precise building and what the note establishes about the altarpiece remain unverified. The French name could refer to a physical convent or its institution; place is a provisional reading of the specific convent in this Paris-work context.",
)
if NEW_CANDIDATE[0] in cids:
    raise SystemExit("planned candidate ID already exists")
new_candidate = {
    "candidate_id": NEW_CANDIDATE[0], "index_entry_id": "", "canonical_name": NEW_CANDIDATE[1], "index_page_range": "",
    "suggested_type": NEW_CANDIDATE[2], "status": "open", "index_source_file": "", "sub_entry": "",
    "detail": NEW_CANDIDATE[3], "exclude_reason": "", "candidate_origin": "body-mention",
    "candidate_source_ref": f"{NOTES_SEGMENT}#L530",
}

new_mentions = []
notes_start = sum(len(src[n - 1]) + 1 for n in range(491, 529))


def add_mention(local, line_no, surface, candidate_id, note=""):
    mention_id = f"m-chp10-p285notes-{local}"
    if mention_id in mids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in cids | {NEW_CANDIDATE[0]}:
        raise SystemExit(f"missing candidate for {mention_id}: {candidate_id}")
    line = src[line_no - 1]
    at = line.find(surface)
    if at < 0:
        raise SystemExit(f"surface absent at L{line_no}: {surface!r}")
    start = notes_start + sum(len(src[n - 1]) + 1 for n in range(529, line_no)) + at
    end = start + len(surface)
    if notes_body[start:end] != surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": NOTES_SEGMENT, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


add_mention("n2-sensier-author", 529, "Sensier", "cand-9291", "Surname-only author/intermediary; identity unresolved.")
add_mention("n2-abecedario", 529, "the Abecedario, pp. 102-3", "cand-7137", "Haskell says Sensier quoted Mariette from these pages; neither the cited pages nor Sensier's intermediary text was consulted.")
add_mention("n3-convent", 530, "Couvent des Augustins Déchaussés", NEW_CANDIDATE[0], "Specific convent/place candidate; its exact relation to the unnamed altarpiece is not established by the locator alone.")
add_mention("n3-sensier-author", 530, "Sensier", "cand-9291", "Surname-only author; identity unresolved.")
add_mention("n3-sensier-source", 530, "Sensier, p. 107", "cand-9290", "Short-form source locator; title unresolved and cited page unread. Not assumed identical to other Sensier references.")
add_mention("n4-sensier-author", 531, "Sensier", "cand-9291", "Surname-only author; identity unresolved.")
add_mention("n4-sensier-source", 531, "Sensier, pp. 199 and 211", "cand-9290", "Short-form source locator; title unresolved and cited pages unread. Not assumed identical to other Sensier references.")

if len(new_mentions) != 7:
    raise SystemExit("planned p.285 notes 2-4 mention count changed")

appends = {
    "cand-7137": " P.285 note 2 says Sensier quotes Mariette from Abecedario, pp.102-103; neither intermediary source nor cited pages were consulted.",
    "cand-9290": " P.285 notes 3-4 add short-form Sensier locators at p.107 and pp.199/211. The title remains unresolved; these citations are not assumed to identify the same publication as one another or earlier locators.",
}
cand_by_id = {row["candidate_id"]: row for row in candidates}
for cid, detail in appends.items():
    cand_by_id[cid]["detail"] = (cand_by_id[cid].get("detail", "") + detail).strip()

qualifications = {
    2: "P.285 note 2 says Sensier quotes Mariette from Abecedario, pp.102-103. This locates the mediated quotation but does not independently verify it; the pages and Sensier text remain unread.",
    3: "P.285 note 3 points to Couvent des Augustins Déchaussés through Sensier, p.107. The cited page is unread; no specific altarpiece or formal relation to the convent is inferred from this locator alone.",
    4: "P.285 note 4 cites Sensier, pp.199 and 211. The title and identity of the referenced publication remain unresolved and the cited pages were not consulted.",
}
for sid, (marker, source_line) in TARGETS.items():
    row = by_sid[sid]
    q = row["qualifiers"]
    q["footnote_text_pending"] = False
    q["footnote_link_status"] = "resolved_source_migration"
    q["footnote_segment"] = NOTES_SEGMENT
    q["footnote_source_line"] = source_line
    q["footnote_note_statement_ids"] = []
    q["qualification"] = (q.get("qualification", "") + " " + qualifications[marker]).strip()
    if marker == 3:
        mentioned = q.setdefault("mentioned_candidate_ids", [])
        if NEW_CANDIDATE[0] not in mentioned:
            mentioned.append(NEW_CANDIDATE[0])
        q["cited_material_not_independently_consulted"] = True
    elif marker == 2:
        q["cited_material_not_independently_consulted"] = True

notes_cov["source_line_ranges"] = "L492-531"
notes_cov["note"] = (notes_cov.get("note", "") +
    " P.285 notes 2-4 at L529-L531 are migrated. Note 2 locates Sensier's mediated quotation from the Abecedario; note 3 points to Couvent des Augustins Déchaussés via Sensier p.107; note 4 cites Sensier pp.199/211. No cited text was independently consulted, no new statement was inferred, and the possible altarpiece/convent relation remains unresolved. L532 onward remains pending.").strip()

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the validated changes")
args = parser.parse_args()
print("p285 notes L529-L531 verified against CHP-10.pdf physical page 14")
print("planned new candidates=1, mentions=7, statements=0; closes body footnote markers 2-4")
print("Sensier short-form references remain unresolved; no cited content or altarpiece relation is inferred")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

for path in (cp, mp, sp, vp):
    backup = path.with_name(path.name + BACKUP)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup}")
    shutil.copy2(path, backup)
candidates.append(new_candidate)
mentions.extend(new_mentions)
write_csv(cp, cf, candidates)
write_csv(mp, mf, mentions)
write_jsonl(sp, statements)
write_csv(vp, vf, coverage)
print(f"applied; recovery copies use suffix {BACKUP}")
