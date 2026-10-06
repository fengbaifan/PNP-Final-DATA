"""Controlled S2 migration for printed p.275 body and its OCR footnote tail."""
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_sec_ii.md"
SEGMENT = "chp-9:09_CHP-9_sec_ii:l80-83"
NEXT = "chp-9:09_CHP-9_sec_ii:l85-127"
ASSET_SHA = "67d60205c246f2f126433bab8a22ddb29ed73e2af2fed5fff5978c319b3ee923"
SEGMENT_SHA = "8bd47a66043c6a768047973686dfe99eb1f79c02e7ca8b228e7229b788fb07bc"
MAX_CANDIDATE = 8769
BACKUP_SUFFIX = ".bak-s2-chp9-p275-20261002"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def read_jsonl(path: Path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8-sig").splitlines() if x.strip()]


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
        tmp = Path(f.name)
    tmp.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(path)


raw = SOURCE.read_bytes()
lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if hashlib.sha256(raw).hexdigest() != ASSET_SHA:
    raise SystemExit("section-II source asset has changed")
segments = {x["segment_id"]: x for x in read_jsonl(TABLES / "segments.jsonl")}
if segments.get(SEGMENT, {}).get("sha256") != SEGMENT_SHA or segments[SEGMENT].get("asset_sha256") != ASSET_SHA:
    raise SystemExit("p.275 source segment missing or changed")
if lines[79].strip() != "[Page 275]" or not lines[80].startswith("Comer was also interested"):
    raise SystemExit("expected p.275 text has changed")
if "the Carita." not in lines[80] or "1778/" not in lines[81] or "eesere" not in lines[82]:
    raise SystemExit("expected p.275 OCR readings have changed")

segment_text = "\n".join(lines[79:83])
offsets, offset = {}, 0
for n in range(80, 84):
    offsets[n] = offset
    offset += len(lines[n - 1]) + 1

cp = TABLES / "entity-candidates.csv"
mp = TABLES / "mentions.csv"
sp = TABLES / "book-statements.jsonl"
vp = TABLES / "s2-coverage.csv"
cf, candidates = read_csv(cp)
mf, mentions = read_csv(mp)
statements = read_jsonl(sp)
vf, coverage = read_csv(vp)
candidate_ids = {x["candidate_id"] for x in candidates}
mention_ids = {x["mention_id"] for x in mentions}
statement_ids = {x["statement_id"] for x in statements}
cov = {x["segment_id"]: x for x in coverage}
maximum = max(int(re.search(r"\d+", x["candidate_id"]).group()) for x in candidates)
if maximum != MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: expected {MAX_CANDIDATE}, found {maximum}")
if (cov.get(SEGMENT, {}).get("disposition"), cov.get(SEGMENT, {}).get("migration_status")) != ("queued", "pending"):
    raise SystemExit("p.275 is not queued/pending")
if (cov.get(NEXT, {}).get("disposition"), cov.get(NEXT, {}).get("migration_status")) != ("queued", "pending"):
    raise SystemExit("consolidated notes segment is not queued/pending")

E = {
    "corner": "cand-0844", "srocco": "cand-3916", "sanciano": "cand-0731",
    "venice": "cand-2719", "virgin": "cand-3427",
}
for key, cid in E.items():
    if cid not in candidate_ids:
        raise SystemExit(f"required candidate missing: {key}={cid}")

SPECS = [
    ("carita_site", "Carità (religious site named in Flaminio Corner's façade account; exact identity unresolved)", "", "The source names only the Carità alongside S. Rocco; do not normalize it to a specific church, school, or confraternity before S3.", 81),
    ("sanciano_altars", "Unidentified marble altars associated with Flaminio Corner at S. Canciano", "work", "Haskell's p.275 account and an unnamed priest's 1778 funeral speech associate these altars with Corner. Keep distinct from the Giuseppe Angeli altarpieces mentioned on p.274.", 82),
    ("corner_altar_principle", "Flaminio Corner's preference for uniform marble church altars", "term", "A source-reported design preference: altars should use matching marble and have identical shape and size. Do not treat this as an independently verified architectural programme.", 82),
]
new_candidates, C = [], {}
for i, (key, name, kind, detail, line_no) in enumerate(SPECS, 1):
    cid = f"cand-{MAX_CANDIDATE+i:04d}"
    if cid in candidate_ids or any(x["canonical_name"] == name and x["suggested_type"] == kind for x in candidates):
        raise SystemExit(f"candidate ID/natural key exists: {cid} {name}")
    C[key] = cid
    new_candidates.append({
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name, "index_page_range": "",
        "suggested_type": kind, "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L{line_no}",
    })
candidate_ids |= {x["candidate_id"] for x in new_candidates}


def c(key):
    return C[key]


def e(key):
    return E[key]


new_mentions = []


def mention(mid, line_no, cid, surface, note="", occurrence=0):
    if mid in mention_ids or any(x["mention_id"] == mid for x in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mid}")
    line = lines[line_no - 1]
    found, pos = [], 0
    while True:
        at = line.find(surface, pos)
        if at < 0:
            break
        found.append(at)
        pos = at + 1
    if occurrence >= len(found):
        raise SystemExit(f"surface absent on L{line_no}: {surface!r}")
    start = offsets[line_no] + found[occurrence]
    end = start + len(surface)
    if segment_text[start:end] != surface or cid not in candidate_ids:
        raise SystemExit(f"bad mention span/ref: {mid}")
    new_mentions.append({
        "mention_id": mid, "segment_id": SEGMENT, "candidate_id": cid, "surface_form": surface,
        "start_char": str(start), "end_char": str(end), "note": note,
    })


mention_specs = [
    ("corner", 81, "corner", "Comer", "Flaminio Corner named as the subject of the page's architecture and patronage discussion.", 0),
    ("srocco", 81, "srocco", "S. Rocco", "Church of S. Rocco; reuse existing accepted candidate and leave identity alignment to S3.", 0),
    ("carita", 81, "carita_site", "Carita", "OCR omits the accent visible in the scan: Carità. Exact site identity remains unresolved.", 0),
    ("corner_marble", 82, "corner_altar_principle", "marble", "Material that Corner wanted used in church altars in place of stone.", 0),
    ("venetian_churches_1", 82, "venice", "Venetian", "Regional adjective refers to churches in Venice.", 0),
    ("altars", 82, "sanciano_altars", "All the altars", "General rule stated by Corner for altars within a church; not an individually named set.", 0),
    ("same_marble", 82, "corner_altar_principle", "identical marble", "Part of the described standard for altar material.", 0),
    ("harmony_creed", 82, "corner_altar_principle", "‘Harmony is delightful in everything’", "Quoted as Corner's creed; attribution is by Haskell.", 0),
    ("corner_patronage", 82, "corner", "his patronage", "Refers to Flaminio Corner.", 0),
    ("sanciano", 82, "sanciano", "S. Canciano", "Corner's parish church and the site of the surviving altar example.", 0),
    ("corner_style", 82, "corner_altar_principle", "the style he encouraged", "The design style Haskell associates with Corner.", 0),
    ("corner_altar_group", 82, "sanciano_altars", "These very altars", "The altars discussed at S. Canciano; distinct from the p.274 Angeli altarpiece candidate.", 0),
    ("corner_built", 82, "corner", "him", "The anonymous priest's funeral speech refers to Corner.", 0),
    ("corner_columns", 82, "sanciano_altars", "black and blue-veined marble columns", "Architectural detail in Haskell's description of the S. Canciano altars.", 0),
    ("corner_capitals", 82, "sanciano_altars", "gold Corinthian capitals", "Architectural detail in Haskell's description of the S. Canciano altars.", 0),
    ("venetian_churches_2", 82, "venice", "Venetian", "Regional adjective in Haskell's comparison with more exuberant contemporary church style.", 1),
    ("madonna", 83, "virgin", "Madonna", "Generic Marian images in the continuation of the p.275 footnote 2 quotation.", 0),
]
for mid, n, key, surface, note, occurrence in mention_specs:
    mention(f"m-chp9-p275-{mid}", n, c(key) if key in C else e(key), surface, note, occurrence)

new_statements = []


def piece(line_no, start, end):
    line = lines[line_no - 1]
    return line[line.index(start):line.index(end, line.index(start)) + len(end)]


def statement(sid, a, b, sub, obj, pred, quote, claim, qualification, refs=(), rel=False, fn=None, cross=(), text_layer="authorial narrative"):
    if sid in statement_ids or any(x["statement_id"] == sid for x in new_statements):
        raise SystemExit(f"duplicate statement ID: {sid}")
    if quote not in segment_text:
        raise SystemExit(f"quote not anchored: {sid}")
    refs = set(refs) | {x for x in (sub, obj) if x}
    if not refs <= candidate_ids:
        raise SystemExit(f"unknown candidate in {sid}: {sorted(refs - candidate_ids)}")
    q = {
        "source_line_start": a, "source_line_end": b, "printed_page": 275, "pdf_physical_page": 41,
        "claim": claim, "speaker": "Haskell", "text_layer": text_layer,
        "qualification": qualification, "mentioned_candidate_ids": sorted(refs),
    }
    if rel:
        q["relation_candidate"] = True
    if fn is not None:
        q["footnote_marker"] = fn
        q["footnote_text_pending"] = True
    if cross:
        q["cross_reference_segments"] = list(cross)
    new_statements.append({
        "statement_id": sid, "segment_id": SEGMENT, "subject_candidate_id": sub,
        "object_candidate_id": obj, "predicate": pred, "qualifiers": q,
        "original_quote": quote, "source_file": SOURCE.relative_to(ROOT).as_posix(), "origin": "book",
    })


statement("st-chp9-p275-corner-architecture-interest", 81, 81, e("corner"), None,
          "corner_interested_in_church_architecture_decoration_and_grandeur", piece(81, "Comer was also interested", "decoration."),
          "Haskell says Corner was interested in church architecture and decoration and welcomed grandeur.",
          "Authorial narrative; the next statement qualifies the report about his advice on two façade projects.")
statement("st-chp9-p275-corner-advised-srocco-facade", 81, 81, e("corner"), e("srocco"),
          "corner_reportedly_encouraged_marble_facade_building_at_s_rocco", piece(81, "He welcomed grandeur", "Carita."),
          "Haskell reports that Corner encouraged the building of the great marble façade of S. Rocco with advice.",
          "Haskell explicitly says it may have been advice without money; do not infer that Corner funded the façade.", [c("carita_site")], True)
statement("st-chp9-p275-corner-advised-carita-facade", 81, 81, e("corner"), c("carita_site"),
          "corner_reportedly_encouraged_marble_facade_building_at_carita", piece(81, "He welcomed grandeur", "Carita."),
          "Haskell reports that Corner encouraged the building of a great marble façade at the Carità with advice.",
          "Haskell says 'if not with money'; the exact site identity and any financial contribution remain unresolved.", [e("srocco")], True)
statement("st-chp9-p275-corner-marble-altar-preference", 82, 82, e("corner"), c("corner_altar_principle"),
          "corner_wanted_marble_to_replace_stone_in_venetian_church_altars", piece(82, "Indeed, he laid especial stress", "Venetian churches."),
          "Haskell says Corner stressed the importance of marble and wanted it to replace stone in the altars of Venetian churches.",
          "This is a preference reported by Haskell, not proof that every Venetian church followed it.", [e("venice")], True)
statement("st-chp9-p275-corner-rejected-theatrical-friezes", 82, 82, e("corner"), None,
          "corner_deplored_the_profane_use_of_friezes_as_if_in_a_theatre", piece(82, "But though he admired richness", "same size."),
          "Haskell says Corner deplored the profane use of friezes as though in a theatre and insisted on uniform decoration.",
          "Retain Haskell's report of Corner's view; it is not a general claim about all Venetian decoration.", [c("corner_altar_principle")])
statement("st-chp9-p275-corner-uniform-altar-rules", 82, 82, e("corner"), c("corner_altar_principle"),
          "corner_wanted_church_altars_to_match_in_marble_shape_and_size", piece(82, "All the altars", "same size."),
          "Haskell says Corner wanted all altars in a church to use identical marble and have the same shape and size.",
          "A source-reported design preference. The passage does not say every church adopted it.", [], True)
statement("st-chp9-p275-corner-harmony-creed", 82, 82, e("corner"), c("corner_altar_principle"),
          "harmony_was_corner_creed_and_he_tried_to_apply_it_in_patronage", piece(82, "‘Harmony is delightful", "his patronage."),
          "Haskell quotes 'Harmony is delightful in everything' as Corner's creed and says he tried to apply it wherever he extended his patronage.",
          "The statement and quotation are reported by Haskell; preserve them as the source's characterization.", [], True)
statement("st-chp9-p275-sanciano-surviving-style", 82, 82, e("sanciano"), c("sanciano_altars"),
          "s_canciano_contains_most_complete_surviving_example_of_corner_encouraged_style", piece(82, "The most complete surviving example", "S. Canciano."),
          "Haskell identifies Corner's parish church of S. Canciano as the most complete surviving example of the style Corner encouraged.",
          "Do not merge this altar group with the Giuseppe Angeli altarpieces discussed on p.274.", [e("corner"), c("corner_altar_principle")], True)
statement("st-chp9-p275-priest-says-corner-built-altars", 82, 82, e("corner"), c("sanciano_altars"),
          "anonymous_priest_at_1778_funeral_said_corner_built_sanciano_altars_with_decorum", piece(82, "‘These very altars", "1778/"),
          "Haskell quotes an unnamed priest at Corner's 1778 funeral service saying that the altars had been built by Corner with decorum.",
          "Nested quotation reported by Haskell; the priest's funeral speech is not independently consulted. Printed note 1 remains pending in the consolidated notes segment.", [e("sanciano")], True, 1)
statement("st-chp9-p275-sanciano-material-description", 82, 82, c("sanciano_altars"), None,
          "sanciano_altars_described_with_veined_marble_columns_and_gold_corinthian_capitals", piece(82, "and even today", "Corinthian capitals,"),
          "Haskell describes black and blue-veined marble columns topped with gold Corinthian capitals at the S. Canciano altars.",
          "Architectural description as observed by Haskell; the source does not give dimensions or identify individual altar components.")
statement("st-chp9-p275-sanciano-austerity-comparison", 82, 82, c("sanciano_altars"), e("venice"),
          "sanciano_altars_described_as_symmetric_and_austere_against_contemporary_venetian_style", piece(82, "which are yet designed", "churches.2"),
          "Haskell says the S. Canciano altars combine symmetry and strict austerity, making no concession to the more exuberant style prevalent in contemporary Venetian churches.",
          "Comparative aesthetic judgement by Haskell. Printed note 2 remains to be reviewed in the consolidated notes segment.", [e("corner")], False, 2)
statement("st-chp9-p275-gerardi-madonna-complaint-tail", 83, 83, None, None,
          "footnote_quote_describes_multiplied_madonna_images_in_venetian_churches_and_haskell_says_complaint_persists", lines[82],
          "The surviving tail of printed footnote 2 quotes a complaint about churches displaying multiple Madonna images and a smaller image on a bench; Haskell says the complaint remains valid.",
          "This is a footnote continuation, not body prose. Its citation and opening attribution are in the consolidated notes segment L127 and remain pending; the Italian OCR 'eesere' is read 'essere' against the scan.",
          [e("virgin"), c("corner_altar_principle")], False, 2,
          [{"segment_id": NEXT, "source_line_start": 127, "source_line_end": 127}], text_layer="footnote continuation")

cov[SEGMENT].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L81-83",
    "note": "Printed p.275 body (PDF physical p.41) read against scan. L81-82 records Corner's architectural preferences, advice concerning the S. Rocco and Carità façades, and the S. Canciano altar example. L83 is the tail of printed footnote 2, not body prose; its text is migrated here and cross-linked to the citation/opening in the consolidated notes segment L127. Printed footnotes 1-2 remain pending there. OCR corrections stored only in S2: L81 'Carita'→'Carità'; L82 'os'→'of', 'exfended'→'extended', '1778/'→printed footnote 1 marker; L83 'eesere'→'essere'. S0 is unchanged. The Carità's exact identity remains unresolved; p.275 S. Canciano altars are distinct from p.274 Angeli altarpieces.",
})

if len({x["mention_id"] for x in mentions + new_mentions}) != len(mentions) + len(new_mentions):
    raise SystemExit("duplicate mention ID")
if len({x["statement_id"] for x in statements + new_statements}) != len(statements) + len(new_statements):
    raise SystemExit("duplicate statement ID")

summary = {
    "segment": SEGMENT, "next": NEXT, "status": "reviewed/complete",
    "new_candidates": len(new_candidates), "candidate_ids": [x["candidate_id"] for x in new_candidates],
    "new_mentions": len(new_mentions), "new_statements": len(new_statements),
    "footnote_tail": "L83 is footnote 2 continuation, cross-linked to notes segment L127",
    "counts_after": {
        "candidates": len(candidates) + len(new_candidates),
        "mentions": len(mentions) + len(new_mentions),
        "statements": len(statements) + len(new_statements), "coverage_rows": len(coverage),
    },
}
print(json.dumps(summary, ensure_ascii=False, indent=2))

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
if args.apply:
    paths = [cp, mp, sp, vp]
    backups = [p.with_name(p.name + BACKUP_SUFFIX) for p in paths]
    if any(p.exists() for p in backups):
        raise SystemExit("recovery backup already exists; inspect before retrying")
    for src, dst in zip(paths, backups):
        shutil.copy2(src, dst)
    try:
        write_csv(cp, cf, candidates + new_candidates)
        write_csv(mp, mf, mentions + new_mentions)
        write_jsonl(sp, statements + new_statements)
        write_csv(vp, vf, list(cov.values()))
    except Exception:
        for target, backup in zip(paths, backups):
            shutil.copy2(backup, target)
        raise
    print("APPLIED; recovery backups retained: " + ", ".join(p.name for p in backups))
else:
    print("DRY RUN: no S2 table rows written")
