"""Controlled S2 migration for printed p.289 notes 1-2; dry-run by default."""
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
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
TRANSCRIPT = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro_notes_p289_visual-transcription.md"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
TRANSCRIPT_FILE = "02-sources/02-Markdown/10_CHP-10_intro_notes_p289_visual-transcription.md"
BODY_SEG = "chp-10:10_CHP-10_intro:l229-238"
NOTES_SEG = "chp-10:10_CHP-10_intro:l491-634"
TABLE_SEG = "chp-10:10_CHP-10_intro_notes_p289_visual-transcription:l1-12"
EXPECTED_SOURCE_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_TRANSCRIPT_SHA = "8cf5ec82dbf1d8040a860f7e386ec5b45d83059da643d5d12c0d0ef3d415a3d2"
EXPECTED_NOTES_LINES_SHA = "e60cdcc4504c137837cad5ce607c3a0d387a867710ec8a0d01ade89adb94bb81"
EXPECTED_TRANSCRIPT_SEG_SHA = "0378a7dc2c28046644de5925a89c138e4048172fc7e3506bf25b6e644b270089"
BACKUP_SUFFIX = ".bak-s2-chp10-p289-notes-20261002"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_SOURCE_SHA:
    raise SystemExit("chapter 10 source asset changed")
if hashlib.sha256(TRANSCRIPT.read_bytes()).hexdigest() != EXPECTED_TRANSCRIPT_SHA:
    raise SystemExit("p.289 table transcription asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
transcript_lines = TRANSCRIPT.read_text(encoding="utf-8-sig").splitlines()
if hashlib.sha256("\n".join(source_lines[542:544]).encode("utf-8")).hexdigest() != EXPECTED_NOTES_LINES_SHA:
    raise SystemExit("merged notes L543-L544 changed")
if hashlib.sha256("\n".join(transcript_lines).encode("utf-8")).hexdigest() != EXPECTED_TRANSCRIPT_SEG_SHA:
    raise SystemExit("p.289 visual transcription L1-L12 changed")
if len(transcript_lines) != 12 or not transcript_lines[1].startswith("The Venetian artists concerned"):
    raise SystemExit("p.289 table caption/line count changed")
if not source_lines[228].strip() == "[Page 289]" or not source_lines[543].startswith("2 Constable, 1954"):
    raise SystemExit("p.289 page or note 2 anchor changed")

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
if maximum != 9380:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for sid, expected in (
    (BODY_SEG, ("reviewed", "partial")),
    (NOTES_SEG, ("reviewed", "partial")),
    (TABLE_SEG, ("queued", "pending")),
):
    row = cov.get(sid)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {sid}: {row}")
if cov[NOTES_SEG]["source_line_ranges"] != "L492-539; L540-542":
    raise SystemExit(f"merged note coverage range changed: {cov[NOTES_SEG]['source_line_ranges']}")
if cov[TABLE_SEG]["source_line_ranges"]:
    raise SystemExit("p.289 transcription is no longer queued")

BODY_TARGETS = {
    "st-chp10-p289-devonshire-monument-subject": 1,
    "st-chp10-p289-marco-ricci-collaborated": 1,
    "st-chp10-p289-sebastiano-ricci-collaborated": 1,
    "st-chp10-p289-ricci-fee-inference": 1,
    "st-chp10-p289-pictures-started-richmond-acquisition": 2,
}
by_sid = {row["statement_id"]: row for row in statements}
if not set(BODY_TARGETS) <= by_sid.keys():
    raise SystemExit("p.289 body footnote statement targets changed")
for sid, marker in BODY_TARGETS.items():
    q = by_sid[sid].get("qualifiers", {})
    if q.get("footnote_marker") != marker or not q.get("footnote_text_pending"):
        raise SystemExit(f"p.289 body footnote status changed: {sid}")

E = {
    "artist_group": "cand-9009", "scheme": "cand-9007", "canaletto_somers": "cand-0523",
    "cimaroli_somers": "cand-0761", "piazzetta_somers": "cand-1915", "marco_devonshire": "cand-2151",
    "sebastiano_devonshire": "cand-2171", "devonshire_person": "cand-0918", "devonshire_work": "cand-9016",
    "william_iii": "cand-2814", "balestra_william_iii": "cand-0169", "cimaroli_william_iii": "cand-0763",
    "pittoni_newton": "cand-1956", "newton_person": "cand-1739", "newton_work": "cand-9375",
    "fitzwilliam": "cand-4893", "canaletto_tillotson": "cand-0524", "cimaroli_tillotson": "cand-0762",
    "pittoni_tillotson": "cand-1955", "paltronieri": "cand-1813", "cimaroli_dorset": "cand-0760",
    "pittoni_dorset": "cand-1957", "dorset_person": "cand-9033", "rome": "cand-4490",
    "marco_shovel": "cand-2152", "sebastiano_shovel": "cand-2172", "shovel_person": "cand-9021",
    "canaletto_stanhope": "cand-0512", "cimaroli_stanhope": "cand-0764", "pittoni_stanhope": "cand-1958",
    "mcswiny": "cand-1466", "richmond": "cand-2194", "marlborough_work": "cand-9015",
    "goodwood": "cand-9025", "tombeaux_1741": "cand-9032", "locke": "cand-1410",
    "george_i": "cand-1140", "cadogan": "cand-0477", "vertue_book": "cand-7255",
    "vertue_person": "cand-8933", "blunt": "cand-0379", "constable_person": "cand-9368",
    "constable_citation": "cand-9369", "bologna": "cand-0381",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")

# A fresh S2 candidate preserves the two individually printed Valeriani names;
# combined index entries cand-2681/2682 remain for global S3 reconciliation.
NEW_SPECS = [
    ("domenico_valeriani", "Domenico Valeriani (individual name in p.289 note 1; compare combined index entry at S3)", "person", "Individually named in the p.289 table; the index also has a combined Domenico-and-Giuseppe entry. Do not merge or assign an individual work role before S3.", TABLE_SEG, 7),
    ("giuseppe_valeriani", "Giuseppe Valeriani (individual name in p.289 note 1; compare combined index entry at S3)", "person", "Individually named in the p.289 table; the index also has a combined Domenico-and-Giuseppe entry. Do not merge or assign an individual work role before S3.", TABLE_SEG, 7),
    ("somers_person", "Lord Somers (monument subject in p.289 note 1; identity unresolved)", "person", "Named as a monument subject in the p.289 artist table. Personal identity is not supplied by this note.", TABLE_SEG, 5),
    ("somers_work", "Unidentified McSwiny-series monument for Lord Somers", "work", "An unnamed monument represented by the p.289 table under Lord Somers. The table does not provide a title, execution date, or verified current location.", TABLE_SEG, 5),
    ("birmingham_place", "Birmingham (p.289 note 1 parenthetical label)", "place", "Bare city label in the Somers row; keep distinct from Birmingham City Art Gallery (cand-9283). It is not a current-holding verification.", TABLE_SEG, 5),
    ("barber_institute", "Barber Institute (p.289 note 1 parenthetical label)", "institution", "Parenthetical label in the Devonshire row, recorded as Haskell's source-time wording; current custody is not independently verified.", TABLE_SEG, 6),
    ("william_iii_work", "Unidentified McSwiny-series monument for William III", "work", "Monument subject in the p.289 artist table and the 1741 list. No title or version is supplied; source-to-source object identity remains for S3.", TABLE_SEG, 7),
    ("duke_of_kent", "Duke of Kent (p.289 note 1 parenthetical label; role and identity unresolved)", "person", "A title-only parenthetical label in the William III row. The note does not clarify whether it identifies a person, collection context, or another role.", TABLE_SEG, 7),
    ("tillotson_person", "Archbishop Tillotson (monument subject in p.289 notes; align with accepted John Tillotson at S3)", "person", "Source-form person candidate for the named monument subject. Do not merge with the accepted John Tillotson KU until global identity alignment.", TABLE_SEG, 9),
    ("tillotson_work", "Unidentified McSwiny-series monument for Archbishop Tillotson", "work", "Unnamed monument listed under Archbishop Tillotson in the p.289 table and 1741 list. No title, date, or version is supplied.", TABLE_SEG, 9),
    ("english_private_collection", "English private collection (p.289 note 1 label; unidentified)", "", "Unidentified collection label printed with the Tillotson row. Do not invent an institution or current location.", TABLE_SEG, 9),
    ("dorset_work", "Unidentified McSwiny-series monument for Lord Dorset", "work", "Unnamed monument listed under Lord Dorset in the p.289 table and 1741/Vertue subject lists. Object version and title remain unspecified.", TABLE_SEG, 10),
    ("rome_private_collection", "Private collection in Rome (p.289 note 1 label; unidentified)", "", "The table prints 'Rome, private collection'. Keep the city (cand-4490) separate from this unidentified collection label; do not treat as a current holding.", TABLE_SEG, 10),
    ("shovel_work", "Unidentified McSwiny-series monument for Sir Cloudesly Shovel", "work", "Unnamed monument listed under the source-spelled Sir Cloudesly Shovel in the p.289 table and 1741 list. Version identity remains unresolved.", TABLE_SEG, 11),
    ("washington_place", "Washington (p.289 note 1 parenthetical label; exact referent unresolved)", "place", "Bare location label in the Shovel row. Separate from another ambiguous Washington candidate and not expanded to a museum or current holding.", TABLE_SEG, 11),
    ("stanhope_person", "Lord Stanhope (p.289 note 1 subject; identity unresolved)", "person", "Named as a monument subject. No personal identity is supplied by the table.", TABLE_SEG, 12),
    ("stanhope_work", "Unidentified McSwiny-series monument for Lord Stanhope", "work", "Unnamed monument in the p.289 table. Canaletto and Cimaroli carry printed question marks; no individual artist role is inferred.", TABLE_SEG, 12),
    ("chrysler_collection", "Walter Chrysler collection (p.289 note 1 label; status unresolved)", "", "Parenthetical label in the Stanhope row. Its institutional status and present location are not established.", TABLE_SEG, 12),
    ("bernard_person", "Sir Robert Bernard (sale owner named in p.289 note 1; identity unresolved)", "person", "Named only in Haskell's report of a 1789 Christie's sale; personal identity is not resolved here.", BODY_SEG, 235),
    ("christies", "Christie's (auction institution named in p.289 note 1)", "institution", "Named as the venue of Sir Robert Bernard's sale on 9 May 1789; no catalogue or sale record was independently consulted.", BODY_SEG, 235),
    ("bernard_sale_event", "Sir Robert Bernard sale at Christie's, 9 May 1789 (p.289 note 1)", "event", "Sale event reported by Haskell on the basis of information attributed to Sir Anthony Blunt; no independent sale record was consulted.", BODY_SEG, 235),
    ("bernard_lot68_record", "Christie's lot 68, Sir Robert Bernard sale, 9 May 1789 (catalogue record)", "archive", "The sale lot as described in Haskell's note: 'Petoni—A pair of Triumphal Mausoleums'. This is a reported catalogue description, not an independently checked record.", BODY_SEG, 235),
    ("petoni", "Petoni (artist name in Bernard sale lot 68; identity unresolved)", "person", "Retain the reported catalogue form Petoni separately from Paltronieri and Pittoni. No identity or spelling correction is inferred.", BODY_SEG, 235),
    ("triumphal_mausoleums", "A pair of Triumphal Mausoleums (work named in Bernard sale lot 68)", "work", "Work title as reported in Haskell's account of lot 68. Do not identify it with a work by Paltronieri or Pittoni.", BODY_SEG, 235),
    ("malborough_person", "Malborough (source form in p.289 note 2; personal identity unresolved)", "person", "Haskell's 1741 subject list spells the name Malborough. Preserve this form separately from the p.278 Duke of Marlborough candidate for S3.", NOTES_SEG, 544),
    ("godolphin_person", "Godolphin (p.289 note 2 monument subject; identity unresolved)", "person", "Surname-only subject in the 1741 list and Vertue list; identity is not supplied.", NOTES_SEG, 544),
    ("godolphin_work", "Unidentified McSwiny-series picture listed for Godolphin", "work", "Picture associated with Godolphin in Haskell's 1741 subject list and later Vertue list. Title and version are unknown.", NOTES_SEG, 544),
    ("cowper_person", "Cowper (p.289 note 2 monument subject; identity unresolved)", "person", "Surname-only subject in the 1741 list; identity is not supplied.", NOTES_SEG, 544),
    ("cowper_work", "Unidentified McSwiny-series picture listed for Cowper", "work", "Picture associated with Cowper in Haskell's 1741 subject list; title and version are unknown.", NOTES_SEG, 544),
    ("boyle_person", "Boyle (p.289 note 2 monument subject; identity unresolved)", "person", "Surname in the printed Boyle/Locke/Sydenham grouping; personal identity is not supplied.", NOTES_SEG, 544),
    ("sydenham_person", "Sydenham (p.289 note 2 monument subject; identity unresolved)", "person", "Surname in the printed Boyle/Locke/Sydenham grouping; personal identity is not supplied.", NOTES_SEG, 544),
    ("boyle_locke_sydenham_work", "Unidentified McSwiny-series picture listed as Boyle/Locke/Sydenham", "work", "One entry in Haskell's list of nine, printed as Boyle/Locke/Sydenham. Preserve the slash grouping; do not infer whether it names one combined subject or several versions.", NOTES_SEG, 544),
    ("goodwood_ten_group", "Ten pictures recorded by Vertue after a visit to Goodwood (p.289 note 2)", "work", "Group of ten pictures summarized by Haskell from Vertue, vol. V, p.149. Individual works, versions, and identity with the 1741 list remain qualified.", BODY_SEG, 237),
    ("george_i_work", "Unidentified McSwiny-series picture listed for George I by Vertue", "work", "Vertue's Goodwood list associates a picture with George I; title and version are unknown.", BODY_SEG, 237),
    ("wharton_person", "Wharton (p.289 note 2 monument subject; identity unresolved)", "person", "Surname-only subject in Vertue's Goodwood list; personal identity is not supplied.", BODY_SEG, 237),
    ("wharton_work", "Unidentified McSwiny-series picture listed for Wharton by Vertue", "work", "Vertue's Goodwood list associates a picture with Wharton; title and version are unknown.", BODY_SEG, 237),
    ("addison_person", "Addison (p.289 note 2 monument subject; identity unresolved)", "person", "Surname-only subject in Vertue's Goodwood list; personal identity is not supplied.", BODY_SEG, 237),
    ("addison_work", "Unidentified McSwiny-series picture listed for Addison by Vertue", "work", "Vertue's Goodwood list associates a picture with Addison; title and version are unknown.", BODY_SEG, 237),
    ("cadogan_work", "Unidentified McSwiny-series picture listed for Cadogan by Vertue", "work", "Vertue's Goodwood list associates a picture with Lord Cadogan; title and version are unknown.", BODY_SEG, 237),
]
new_candidates, C = [], {}
next_candidate = maximum
for key, name, kind, detail, segment_id, line in NEW_SPECS:
    next_candidate += 1
    cid = f"cand-{next_candidate:04d}"
    if cid in cids:
        raise SystemExit(f"candidate id already exists: {cid}")
    C[key] = cid
    new_candidates.append({
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{segment_id}#L{line}",
    })

# Enrich index-seeded candidates without resolving their identities.
cand_by_id = {row["candidate_id"]: row for row in candidates}
DETAIL_UPDATES = {
    "cand-2681": " P.289 note 1 prints Domenico and Giuseppe Valeriani as separate names; the combined index entry remains unresolved for S3 and is not used for either individual mention.",
    "cand-2682": " P.289 note 1 prints Domenico and Giuseppe Valeriani as separate names; the combined index entry remains unresolved for S3 and is not used for either individual mention.",
    "cand-7255": " P.289 note 2 cites Vertue, vol. V, p.149 for the ten pictures after the Goodwood visit; the cited page was not independently consulted.",
    "cand-8933": " P.289 note 2 names Vertue as the source of the ten-picture Goodwood list; this report is not an independent reading of the cited page.",
    "cand-9015": " P.289 note 2 gives the 1741 list spelling 'Malborough'; keep the source form and its personal identity unresolved at S3.",
    "cand-9016": " P.289 note 1's table also lists the Devonshire subject with Marco and Sebastiano Ricci and the Barber Institute parenthetical; this records Haskell's table, not current custody or an independently verified creator relation.",
    "cand-9021": " P.289 note 1's table and note 2's 1741 list also name this source-spelled subject; identity and picture-version alignment remain unresolved.",
    "cand-9032": " P.289 note 2 says the 1741 volume published nine scheme pictures and reported them as belonging to the Duke of Richmond; the cited edition was not independently consulted.",
    "cand-9033": " P.289 note 1's table and note 2's two lists also name Lord Dorset; the personal identity remains unresolved.",
    "cand-9009": " P.289 note 1's table has now been migrated. The caption calls the list Venetian artists concerned in the enterprise but does not assign each artist an execution or authorship role.",
    "cand-9368": " P.289 note 2 repeats the Constable 1954, p.154 citation; retain the surname-only author candidate and do not merge it with the painter John Constable.",
    "cand-9369": " P.289 note 2 repeats this locator. The cited page was not independently consulted.",
    "cand-9375": " P.289 note 1's table also names Isaac Newton as a monument subject with a Fitzwilliam Museum label. Preserve this source link without asserting a verified object version or current holding.",
}
for cid, addition in DETAIL_UPDATES.items():
    if cid not in cand_by_id:
        raise SystemExit(f"missing candidate for detail update: {cid}")
    if addition.strip() not in cand_by_id[cid].get("detail", ""):
        existing = cand_by_id[cid].get("detail", "").strip()
        cand_by_id[cid]["detail"] = (existing + addition).strip()


SEGMENT_TEXT = {
    BODY_SEG: (source_lines, 229, 238, SOURCE_FILE),
    NOTES_SEG: (source_lines, 491, 634, SOURCE_FILE),
    TABLE_SEG: (transcript_lines, 1, 12, TRANSCRIPT_FILE),
}
segment_offsets = {}
segment_quotes = {}
for sid, (lines, start, end, _source_file) in SEGMENT_TEXT.items():
    offset = 0
    offsets = {}
    for line_number in range(start, end + 1):
        offsets[line_number] = offset
        offset += len(lines[line_number - 1]) + 1
    segment_offsets[sid] = offsets
    segment_quotes[sid] = "\n".join(lines[start - 1:end])

new_mentions = []
new_mids = set()


def add_m(local, segment_id, line, surface, cid, note="", occurrence=0):
    mid = f"m-chp10-p289-{local}"
    if mid in mids or mid in new_mids:
        raise SystemExit(f"duplicate mention: {mid}")
    if cid not in cids | {row["candidate_id"] for row in new_candidates}:
        raise SystemExit(f"missing candidate for mention {mid}: {cid}")
    lines = SEGMENT_TEXT[segment_id][0]
    positions, at = [], 0
    while True:
        at = lines[line - 1].find(surface, at)
        if at < 0:
            break
        positions.append(at)
        at += max(1, len(surface))
    if occurrence >= len(positions):
        raise SystemExit(f"surface absent at L{line}: {surface!r} in {segment_id}")
    start = segment_offsets[segment_id][line] + positions[occurrence]
    end = start + len(surface)
    if segment_quotes[segment_id][start:end] != surface:
        raise SystemExit(f"span mismatch: {mid}")
    new_mentions.append({
        "mention_id": mid, "segment_id": segment_id, "candidate_id": cid,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })
    new_mids.add(mid)


add_m("table-caption-venetian-artists", TABLE_SEG, 2, "Venetian artists", E["artist_group"], "Printed table caption; editorial column labels and Markdown separators are not source text.")

TABLE_ROWS = [
    {"line": 5, "subject": "Lord Somers", "person": "somers_person", "work": "somers_work", "label": "Birmingham", "label_key": "birmingham_place", "artists": [("Canaletto", "canaletto_somers"), ("Cimaroli", "cimaroli_somers"), ("Piazzetta", "piazzetta_somers")]},
    {"line": 6, "subject": "Duke of Devonshire", "person": None, "person_id": "devonshire_person", "work_id": "devonshire_work", "label": "Barber Institute", "label_key": "barber_institute", "artists": [("Marco Ricci", "marco_devonshire"), ("Sebastiano Ricci", "sebastiano_devonshire")]},
    {"line": 7, "subject": "William III", "person_id": "william_iii", "work": "william_iii_work", "label": "Duke of Kent", "label_key": "duke_of_kent", "artists": [("Domenico Valeriani", "domenico_valeriani"), ("Giuseppe Valeriani", "giuseppe_valeriani"), ("Cimaroli", "cimaroli_william_iii"), ("Balestra", "balestra_william_iii")]},
    {"line": 8, "subject": "Isaac Newton", "person_id": "newton_person", "work_id": "newton_work", "label": "Fitzwilliam Museum", "label_existing": "fitzwilliam", "artists": [("Domenico Valeriani", "domenico_valeriani"), ("Giuseppe Valeriani", "giuseppe_valeriani"), ("Pittoni", "pittoni_newton")]},
    {"line": 9, "subject": "Archbishop Tillotson", "person": "tillotson_person", "work": "tillotson_work", "label": "English private collection", "label_key": "english_private_collection", "artists": [("Canaletto", "canaletto_tillotson"), ("Cimaroli", "cimaroli_tillotson"), ("Pittoni", "pittoni_tillotson")]},
    {"line": 10, "subject": "Lord Dorset", "person_id": "dorset_person", "work": "dorset_work", "label": "Rome", "label_key": "rome_private_collection", "artists": [("Paltronieri", "paltronieri"), ("Cimaroli", "cimaroli_dorset"), ("Pittoni", "pittoni_dorset")]},
    {"line": 11, "subject": "Sir Cloudesly Shovel", "person_id": "shovel_person", "work": "shovel_work", "label": "Washington", "label_key": "washington_place", "artists": [("Marco Ricci", "marco_shovel"), ("Sebastiano Ricci", "sebastiano_shovel")]},
    {"line": 12, "subject": "Lord Stanhope", "person": "stanhope_person", "work": "stanhope_work", "label": "Walter Chrysler collection", "label_key": "chrysler_collection", "artists": [("Canaletto?", "canaletto_stanhope"), ("Cimaroli?", "cimaroli_stanhope"), ("Pittoni", "pittoni_stanhope")]},
]

TABLE_STATEMENTS = []
for index, row in enumerate(TABLE_ROWS, 1):
    person_cid = C[row["person"]] if row.get("person") else E[row["person_id"]]
    work_cid = C[row["work"]] if row.get("work") else E[row["work_id"]]
    label_cid = C[row["label_key"]] if row.get("label_key") else E[row["label_existing"]]
    line = row["line"]
    quote = transcript_lines[line - 1]
    artist_ids = []
    for artist_index, (surface, artist_key) in enumerate(row["artists"], 1):
        artist_cid = C[artist_key] if artist_key in C else E[artist_key]
        artist_ids.append(artist_cid)
        marker_note = "Printed question mark retained; individual contribution is not confirmed." if surface.endswith("?") else "Table association only; no specific author/execution role is stated."
        add_m(f"table-row{index}-artist{artist_index}", TABLE_SEG, line, surface, artist_cid, marker_note)
        TABLE_STATEMENTS.append({
            "statement_id": f"st-chp10-p289-note1-row{index:02d}-artist{artist_index}",
            "segment_id": TABLE_SEG, "source_line_start": line, "source_line_end": line,
            "subject_candidate_id": artist_cid, "object_candidate_id": work_cid,
            "predicate": "artist_listed_as_concerned_in_enterprise_for_monument_subject",
            "claim": f"The p.289 table places {surface} in its artists column on the row for the monument subject {row['subject']}.",
            "qualification": "The caption calls the listed names Venetian artists concerned in the enterprise. Row placement supports an association candidate only; the table does not define this individual's creative, execution, or commission role. Printed question marks remain uncertainty.",
            "mentioned_candidate_ids": [artist_cid, work_cid, person_cid, label_cid, E["scheme"]],
            "original_quote": quote, "speaker": "Haskell, footnote table", "text_layer": "authorial note/table",
            "relation_candidate": True, "footnote_number": 1,
            "related_body_statement_ids": list(BODY_TARGETS)[:4],
        })
    add_m(f"table-row{index}-subject", TABLE_SEG, line, row["subject"], person_cid, "Monument subject as printed; personal identity is not inferred beyond the named person candidate.")
    if row["label"] == "Rome":
        add_m(f"table-row{index}-place", TABLE_SEG, line, "Rome", E["rome"], "City label in the table; not a current collection location.")
        add_m(f"table-row{index}-collection", TABLE_SEG, line, "private collection", C["rome_private_collection"], "Unidentified private collection; retained separately from Rome.")
    else:
        label_note = "Source-time location label; no current holding is asserted." if row.get("label_key") in {"barber_institute", "birmingham_place", "washington_place"} else "Parenthetical label only; its current status/location is not verified."
        add_m(f"table-row{index}-label", TABLE_SEG, line, row["label"], label_cid, label_note)
    TABLE_STATEMENTS.append({
        "statement_id": f"st-chp10-p289-note1-row{index:02d}-subject",
        "segment_id": TABLE_SEG, "source_line_start": line, "source_line_end": line,
        "subject_candidate_id": work_cid, "object_candidate_id": person_cid,
        "predicate": "table_lists_monument_subject_and_parenthetical_label",
        "claim": f"The p.289 table pairs a McSwiny-series monument entry with the subject {row['subject']} and the label {row['label']}.",
        "qualification": "The column labels and Markdown separators in the transcription are editorial aids. Parenthetical labels reproduce Haskell's source-time table and do not verify present-day holdings. The table does not supply a formal work title or version.",
        "mentioned_candidate_ids": [work_cid, person_cid, label_cid, *artist_ids, E["scheme"]],
        "original_quote": quote, "speaker": "Haskell, footnote table", "text_layer": "authorial note/table",
        "relation_candidate": True, "footnote_number": 1,
        "related_body_statement_ids": list(BODY_TARGETS)[:4],
    })

# P.289 note 1's printed introductory caption.
TABLE_STATEMENTS.insert(0, {
    "statement_id": "st-chp10-p289-note1-table-introduction", "segment_id": TABLE_SEG,
    "source_line_start": 2, "source_line_end": 2, "subject_candidate_id": E["artist_group"],
    "object_candidate_id": E["scheme"], "predicate": "caption_identifies_artists_concerned_in_enterprise",
    "claim": "The printed caption introduces the following list as 'The Venetian artists concerned in the enterprise'.",
    "qualification": "This records the caption's own group description; it does not independently establish every individual's origin or work role. Editorial Markdown headers and separators are excluded.",
    "mentioned_candidate_ids": [E["artist_group"], E["scheme"]],
    "original_quote": transcript_lines[1], "speaker": "Haskell, footnote", "text_layer": "authorial note/table caption",
    "relation_candidate": False, "footnote_number": 1, "related_body_statement_ids": list(BODY_TARGETS)[:4],
})

new_statements = []
new_sids = set()


def add_statement(sid, segment_id, lo, hi, subject, obj, predicate, claim, qualification,
                  mentioned, speaker, layer, relation=False, marker=None, quote=None,
                  cited_not_consulted=False):
    if sid in sids or sid in new_sids:
        raise SystemExit(f"duplicate statement: {sid}")
    if quote is None:
        start = SEGMENT_TEXT[segment_id][0][lo - 1]
        quote = start
    text = segment_quotes[segment_id]
    if quote not in text:
        raise SystemExit(f"statement quote is not anchored in {segment_id} L{lo}-L{hi}: {sid}")
    q = {
        "source_line_start": lo, "source_line_end": hi, "printed_page": 289,
        "pdf_physical_page": 18, "claim": claim, "speaker": speaker,
        "text_layer": layer, "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)), "relation_candidate": relation,
    }
    if marker is not None:
        q["footnote_number"] = marker
        q["related_body_statement_ids"] = [sid for sid, body_marker in BODY_TARGETS.items() if body_marker == marker]
    if cited_not_consulted:
        q["cited_material_not_independently_consulted"] = True
    source_file = SEGMENT_TEXT[segment_id][3]
    new_statements.append({
        "statement_id": sid, "segment_id": segment_id, "subject_candidate_id": subject,
        "object_candidate_id": obj, "predicate": predicate, "qualifiers": q,
        "original_quote": quote, "source_file": source_file, "origin": "book",
    })
    new_sids.add(sid)


new_statements.extend([])
for original_spec in TABLE_STATEMENTS:
    spec = dict(original_spec)
    sid = spec.pop("statement_id")
    segment_id = spec.pop("segment_id")
    lo = spec.pop("source_line_start")
    hi = spec.pop("source_line_end")
    subject = spec.pop("subject_candidate_id")
    obj = spec.pop("object_candidate_id")
    predicate = spec.pop("predicate")
    claim = spec.pop("claim")
    qualification = spec.pop("qualification")
    mentioned = spec.pop("mentioned_candidate_ids")
    quote = spec.pop("original_quote")
    speaker = spec.pop("speaker")
    layer = spec.pop("text_layer")
    relation = spec.pop("relation_candidate")
    marker = spec.pop("footnote_number")
    related = spec.pop("related_body_statement_ids")
    # Keep same-chapter note cross-references explicit in the standard fields.
    add_statement(sid, segment_id, lo, hi, subject, obj, predicate, claim, qualification,
                  mentioned, speaker, layer, relation, marker, quote)
    new_statements[-1]["qualifiers"]["related_body_statement_ids"] = related

add_m("note1-paltronieri-name", BODY_SEG, 234, "Paltronieri", E["paltronieri"], "Repeated name in note 1 prose; do not merge with Petoni.")
add_m("note1-blunt", BODY_SEG, 234, "Sir Anthony Blunt", E["blunt"], "Named by Haskell as the person who pointed out the sale description.")
add_m("note1-bernard", BODY_SEG, 235, "Sir Robert Bernard", C["bernard_person"], "Identity not resolved.")
add_m("note1-christies", BODY_SEG, 235, "Christie’s", C["christies"], "Auction venue named in Haskell's report.")
add_m("note1-sale-event", BODY_SEG, 235, "9 May 1789", C["bernard_sale_event"], "Date of the reported sale event; no independent sale record consulted.")
add_m("note1-lot68", BODY_SEG, 235, "lot 68", C["bernard_lot68_record"], "Reported sale catalogue lot; contents were not independently checked.")
add_m("note1-petoni", BODY_SEG, 235, "Petoni", C["petoni"], "Reported catalogue attribution form; not identified with Paltronieri or Pittoni.")
add_m("note1-triumphal-mausoleums", BODY_SEG, 235, "A pair of Triumphal", C["triumphal_mausoleums"], "Work title continues on L236; the exact complete title is recorded by the candidate.")

add_statement(
    "st-chp10-p289-note1-paltronieri-bolognese", BODY_SEG, 234, 234,
    E["paltronieri"], E["bologna"], "described_as_bolognese_painter",
    "Haskell describes Paltronieri as a Bolognese painter.",
    "This is Haskell's description in the note, not an independently verified birthplace or training history. The later sale name Petoni remains separate.",
    [E["paltronieri"], E["bologna"]], "Haskell, footnote", "authorial note",
    relation=True, marker=1, quote=source_lines[233],
)
sale_quote = "\n".join(source_lines[233:236])
add_statement(
    "st-chp10-p289-note1-bernard-sale-lot68", BODY_SEG, 234, 236,
    C["bernard_lot68_record"], C["triumphal_mausoleums"], "sale_lot_reported_as_attributed_to_petoni",
    "Haskell thanks Sir Anthony Blunt for pointing out that lot 68 in Sir Robert Bernard's Christie's sale of 9 May 1789 was described as 'Petoni—A pair of Triumphal Mausoleums'.",
    "This is Haskell's report of information supplied by Blunt. The sale catalogue was not independently consulted; Petoni is not identified with Paltronieri or Pittoni.",
    [E["blunt"], C["bernard_person"], C["christies"], C["bernard_sale_event"], C["bernard_lot68_record"], C["petoni"], C["triumphal_mausoleums"], E["paltronieri"]],
    "Haskell, reporting information from Sir Anthony Blunt", "authorial note reporting a catalogue description",
    relation=True, marker=1, quote=sale_quote,
)

line544 = source_lines[543]
line237 = source_lines[236]
line238 = source_lines[237]
constable_quote = "Constable, 1954, p. 154."
confusion_quote = line544[line544.index("In fact"):line544.index(" In 1741")].rstrip()
publication_quote = line544[line544.index("In 1741"):line544.index(" These were")].rstrip()
owned_quote = "and said that they all belonged to the Duke."
subjects_quote = line544[line544.index("These were those to"):].strip()
vertue_quote = line237
probably_quote = line238

add_m("note2-constable-author", NOTES_SEG, 544, "Constable", E["constable_person"], "Surname-only cited author; identity is unresolved and not assumed to be the painter John Constable.")
add_m("note2-constable-locator", NOTES_SEG, 544, "1954, p. 154", E["constable_citation"], "Bibliographic locator; cited page not independently consulted.")
add_m("note2-nine-of-them", NOTES_SEG, 544, "nine of them", E["scheme"], "Count in Haskell's account of the 1741 publication; the list contains nine entries, one printed as Boyle/Locke/Sydenham.")
add_m("note2-mcswiny", NOTES_SEG, 544, "McSwiny", E["mcswiny"], "Named as publisher of the 1741 volume in Haskell's account.")
add_m("note2-tombeaux", NOTES_SEG, 544, "Tombeaux des Princes", E["tombeaux_1741"], "Specific 1741 edition candidate; the volume was not independently consulted.")
add_m("note2-richmond-first", NOTES_SEG, 544, "Duke of Richmond", E["richmond"], "Title reference in the note; identity remains subject to S3.")
subjects_1741 = [
    ("William III", E["william_iii"]), ("Tillotson", C["tillotson_person"]),
    ("Malborough", C["malborough_person"]), ("Godolphin", C["godolphin_person"]),
    ("Dorset", E["dorset_person"]), ("Cowper", C["cowper_person"]),
    ("Sir Cloudesly Shovel", E["shovel_person"]), ("Newton", E["newton_person"]),
    ("Boyle", C["boyle_person"]), ("Locke", E["locke"]), ("Sydenham", C["sydenham_person"]),
]
for i, (surface, cid) in enumerate(subjects_1741, 1):
    add_m(f"note2-1741-subject-{i:02d}", NOTES_SEG, 544, surface, cid, "Subject name in Haskell's 1741 nine-entry list; preserve source spelling and identity uncertainty.")

add_statement(
    "st-chp10-p289-note2-constable-citation", NOTES_SEG, 544, 544,
    E["constable_person"], E["constable_citation"], "haskell_cites_constable_1954_p154",
    "Haskell cites Constable (1954, p.154).",
    "The cited page was not independently consulted; this is a citation locator, not independent evidence for the note's claims.",
    [E["constable_person"], E["constable_citation"]], "Haskell, footnote", "bibliographical note",
    marker=2, quote=constable_quote, cited_not_consulted=True,
)
add_statement(
    "st-chp10-p289-note2-acquisition-confusion", NOTES_SEG, 544, 544,
    E["scheme"], E["richmond"], "haskell_reports_confusion_over_which_pictures_richmond_acquired",
    "Haskell says there is considerable confusion over which pictures were actually acquired by the Duke of Richmond.",
    "This records Haskell's explicit caution; the note does not resolve a definitive acquisition list.",
    [E["scheme"], E["richmond"], *[cid for _, cid in subjects_1741]],
    "Haskell, footnote", "authorial note", marker=2, quote=confusion_quote,
)
add_statement(
    "st-chp10-p289-note2-1741-publication", NOTES_SEG, 544, 544,
    E["mcswiny"], E["tombeaux_1741"], "mcswiny_published_tombeaux_des_princes_in_1741",
    "Haskell says McSwiny published nine scheme pictures in the 1741 Tombeaux des Princes.",
    "This is Haskell's account of the publication; the cited edition was not independently examined.",
    [E["mcswiny"], E["tombeaux_1741"], E["scheme"]], "Haskell, footnote", "authorial note",
    relation=True, marker=2, quote=publication_quote, cited_not_consulted=True,
)
add_statement(
    "st-chp10-p289-note2-1741-reported-ownership", NOTES_SEG, 544, 544,
    E["tombeaux_1741"], E["richmond"], "1741_volume_reported_nine_pictures_belonged_to_duke_of_richmond",
    "Haskell says the 1741 volume claimed that all nine pictures belonged to the Duke of Richmond.",
    "This is the volume's reported claim as summarized by Haskell, not independently verified ownership; note 2 explicitly warns that the acquisition history is confused.",
    [E["tombeaux_1741"], E["richmond"], E["scheme"]], "Haskell reporting the 1741 volume", "authorial note reporting a source",
    relation=True, marker=2, quote=owned_quote, cited_not_consulted=True,
)
works_1741 = [E["william_iii"] if False else C["william_iii_work"], C["tillotson_work"], E["marlborough_work"], C["godolphin_work"], C["dorset_work"], C["cowper_work"], C["shovel_work"], E["newton_work"], C["boyle_locke_sydenham_work"]]
persons_1741 = [cid for _, cid in subjects_1741]
add_statement(
    "st-chp10-p289-note2-1741-subject-list", NOTES_SEG, 544, 544,
    E["tombeaux_1741"], E["scheme"], "1741_volume_lists_nine_pictures_by_named_subject",
    "Haskell lists nine 1741 picture subjects: William III, Tillotson, Malborough, Godolphin, Dorset, Cowper, Sir Cloudesly Shovel, Newton, and Boyle/Locke/Sydenham.",
    "Preserve the source spelling 'Malborough' and the Boyle/Locke/Sydenham slash grouping. Work candidates are descriptive S2 records; exact titles, versions, and personal identities remain open.",
    [E["tombeaux_1741"], E["scheme"], *persons_1741, *works_1741],
    "Haskell, footnote", "authorial note reporting a published list", marker=2, quote=subjects_quote,
    cited_not_consulted=True,
)

add_m("note2-vertue-person", BODY_SEG, 237, "Vertue", E["vertue_person"], "Person named by Haskell as the source of a later list; cited notebook page not independently consulted.")
add_m("note2-vertue-locator", BODY_SEG, 237, "V, p. 149", E["vertue_book"], "Citation to George Vertue's Notebooks, vol. V, p.149; cited page not independently consulted.")
add_m("note2-goodwood-ten-group", BODY_SEG, 237, "ten", C["goodwood_ten_group"], "Count for the later list Haskell attributes to Vertue.")
add_m("note2-goodwood-place", BODY_SEG, 237, "Goodwood", E["goodwood"], "The visit location reported by Haskell; no precise building/site identity is added.")
subjects_vertue = [
    (237, "William HI", E["william_iii"]), (237, "George I", E["george_i"]),
    (237, "Devonshire", E["devonshire_person"]), (237, "Wharton", C["wharton_person"]),
    (237, "Addison", C["addison_person"]), (237, "Dorset", E["dorset_person"]),
    (238, "Tillotson", C["tillotson_person"]), (238, "Stanhope", C["stanhope_person"]),
    (238, "Cadogan", E["cadogan"]), (238, "Godolphin", C["godolphin_person"]),
]
for i, (line, surface, cid) in enumerate(subjects_vertue, 1):
    note = "S0 OCR reads 'William HI'; the printed page reads 'William III'. Identity/edition alignment remains open." if surface == "William HI" else "Subject name in Haskell's summary of Vertue's later list; identity/edition alignment remains open."
    add_m(f"note2-vertue-subject-{i:02d}", BODY_SEG, line, surface, cid, note)
add_m("note2-richmond-probable", BODY_SEG, 238, "Duke of Richmond", E["richmond"], "Title reference in Haskell's explicitly probable explanation.")
add_m("note2-goodwood-place-repeat", BODY_SEG, 238, "Goodwood", E["goodwood"], "Place named in Haskell's qualified explanation; not a current display verification.")

works_vertue = [
    C["william_iii_work"], C["george_i_work"], E["devonshire_work"], C["wharton_work"],
    C["addison_work"], C["dorset_work"], C["tillotson_work"], C["stanhope_work"],
    C["cadogan_work"], C["godolphin_work"],
]
add_statement(
    "st-chp10-p289-note2-vertue-goodwood-list", BODY_SEG, 237, 238,
    E["vertue_person"], C["goodwood_ten_group"], "haskell_says_vertue_recorded_ten_pictures_after_goodwood_visit",
    "Haskell says Vertue recorded ten pictures after a visit to Goodwood: William III, George I, Devonshire, Wharton, Addison, Dorset, Tillotson, Stanhope, Cadogan, and Godolphin.",
    "Haskell's summary is based on Vertue, vol. V, p.149, which was not independently consulted. The list does not wholly coincide with the 1741 list; shared subject names do not by themselves settle object/version identity.",
    [E["vertue_person"], E["vertue_book"], C["goodwood_ten_group"], E["goodwood"], E["richmond"], *[cid for _, _, cid in subjects_vertue], *works_vertue],
    "Haskell reporting George Vertue", "authorial note summarizing cited source", relation=True,
    marker=2, quote=vertue_quote, cited_not_consulted=True,
)
add_statement(
    "st-chp10-p289-note2-richmond-probable-total", BODY_SEG, 238, 238,
    E["richmond"], C["goodwood_ten_group"], "haskell_probably_explains_fourteen_or_fifteen_pictures_not_all_kept_at_goodwood",
    "Haskell says the explanation is probably that the Duke of Richmond owned some fourteen or fifteen pictures but did not keep them all at Goodwood.",
    "Retain 'probably' as Haskell's inference, not a verified total or a confirmed ownership/display history.",
    [E["richmond"], C["goodwood_ten_group"], E["goodwood"], E["scheme"], *works_vertue],
    "Haskell, footnote", "authorial note with qualified inference", relation=True,
    marker=2, quote=probably_quote,
)

# Link the page-body footnote markers to the complete note statements.
note1_ids = [row["statement_id"] for row in TABLE_STATEMENTS] + [
    "st-chp10-p289-note1-paltronieri-bolognese", "st-chp10-p289-note1-bernard-sale-lot68",
]
note2_ids = [
    "st-chp10-p289-note2-constable-citation", "st-chp10-p289-note2-acquisition-confusion",
    "st-chp10-p289-note2-1741-publication", "st-chp10-p289-note2-1741-reported-ownership",
    "st-chp10-p289-note2-1741-subject-list", "st-chp10-p289-note2-vertue-goodwood-list",
    "st-chp10-p289-note2-richmond-probable-total",
]
for sid, marker in BODY_TARGETS.items():
    q = by_sid[sid]["qualifiers"]
    q["footnote_text_pending"] = False
    q["footnote_body_link_status"] = "linked"
    q["footnote_segment"] = NOTES_SEG
    q["footnote_source_line"] = 543 if marker == 1 else 544
    q["footnote_note_statement_ids"] = note1_ids if marker == 1 else note2_ids
    q["cited_material_not_independently_consulted"] = True

# Update three source segments. The p.289 OCR tail at L233 duplicates Pittoni in
# the table, while L234-238 contain the note 1 prose tail and note 2 continuation.
cov[BODY_SEG].update({
    "migration_status": "complete", "source_line_ranges": "L230-238; p.290 L241",
    "note": "Printed p.289 body segment checked against CHP-10.pdf physical p.18. L230-232 narrative and its p.290 L241 continuation were already migrated; this pass completes L234-236 note 1 prose and L237-238 note 2 continuation. L233 'Pittoni' is a duplicate OCR tail of the note 1 table, not an additional mention. The note 1 table rows are anchored in the companion visual transcription; the note 2 list and its 'probably' explanation preserve source attribution and uncertainty.",
})
cov[NOTES_SEG].update({
    "source_line_ranges": "L492-544",
    "note": (cov[NOTES_SEG].get("note", "") +
             " P.289 printed notes 1-2 at L543-L544 are now migrated. The collapsed L543 OCR table is represented by a 12-line companion visual transcription with row groupings preserved; note 1 prose also continues in body L234-L236. Note 2 begins at L544 and continues in body L237-L238. The later Vertue list is distinct as a reported list; shared subject names do not prove identical versions. L545 onward remains pending.").strip(),
})
cov[TABLE_SEG].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L1-12",
    "note": "Printed p.289 note 1 table checked against CHP-10.pdf physical p.18. L2 is the printed heading; L5-L12 are the eight printed rows. L1 is transcription metadata; L3-L4 are editorial column labels and Markdown separators. Artist names, subject names and parenthetical labels are recorded; question marks on Canaletto? and Cimaroli? are retained. Parenthetical locations/collections are source-time wording, not current-holding verification.",
})

# Validate ID references and disjoint exact mention anchors before any write.
all_cids = cids | {row["candidate_id"] for row in new_candidates}
for row in new_mentions:
    if row["candidate_id"] not in all_cids:
        raise SystemExit(f"mention has unresolved candidate: {row['mention_id']}")
by_segment = {}
for row in new_mentions:
    by_segment.setdefault(row["segment_id"], []).append(row)
for segment_id, rows in by_segment.items():
    rows.sort(key=lambda row: (int(row["start_char"]), int(row["end_char"])))
    for left, right in zip(rows, rows[1:]):
        if int(right["start_char"]) < int(left["end_char"]):
            raise SystemExit(f"overlapping mention anchors: {left['mention_id']} / {right['mention_id']}")
for row in TABLE_STATEMENTS:
    if not row["original_quote"] in segment_quotes[TABLE_SEG]:
        raise SystemExit(f"table row quote lost: {row['statement_id']}")

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="write the validated migration")
args = parser.parse_args()
all_new_statements = new_statements
print(json.dumps({
    "mode": "APPLY" if args.apply else "DRY-RUN",
    "source_segments": [BODY_SEG, NOTES_SEG, TABLE_SEG],
    "new_candidate_count": len(new_candidates),
    "new_candidate_ids": {key: value for key, value in C.items()},
    "new_mentions": len(new_mentions), "new_statements": len(all_new_statements),
    "body_note_links": {"marker1": len(note1_ids), "marker2": len(note2_ids)},
    "coverage": {sid: {"disposition": cov[sid]["disposition"], "migration_status": cov[sid]["migration_status"], "source_line_ranges": cov[sid]["source_line_ranges"]} for sid in (BODY_SEG, NOTES_SEG, TABLE_SEG)},
}, ensure_ascii=False, indent=2))
if not args.apply:
    print("dry-run only; no tables written")
    raise SystemExit(0)

for path in (cp, mp, sp, vp):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup}")
    shutil.copy2(path, backup)
write_csv(cp, cf, candidates + new_candidates)
write_csv(mp, mf, mentions + new_mentions)
write_jsonl(sp, statements + all_new_statements)
write_csv(vp, vf, [cov[row["segment_id"]] for row in coverage])
print(f"applied; four recovery copies use suffix {BACKUP_SUFFIX}")
