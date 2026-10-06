"""Controlled S2 migration for printed page 249; default is a read-only dry run."""
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
PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
P248 = "chp-9:09_CHP-9_intro:l38-46"
P249 = "chp-9:09_CHP-9_intro:l77-88"
P250 = "chp-9:09_CHP-9_intro:l90-104"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
EXPECTED_HASH = "73ab39a6a928011b2397ba2020cb978873200751bd57a8913d385d59ad081dce"
EXPECTED_ASSET_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
BACKUP_SUFFIX = ".bak-s2-chp9-p249-20261001"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(stream.name)
    tmp.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(stream.name)
    tmp.replace(path)


segments = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {row["segment_id"]: row for row in segments}
for sid in (P248, P249, P250, NOTES):
    if sid not in segment_by_id:
        raise SystemExit(f"missing segment metadata: {sid}")
meta = segment_by_id[P249]
if meta["sha256"] != EXPECTED_HASH or meta["asset_sha256"] != EXPECTED_ASSET_HASH:
    raise SystemExit("source segment or asset hash changed; inspect before migration")
asset = ROOT / meta["source_file"]
if hashlib.sha256(asset.read_bytes()).hexdigest() != EXPECTED_ASSET_HASH:
    raise SystemExit("source asset hash changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
selected = source_lines[meta["line_start"] - 1:meta["line_end"]]
if hashlib.sha256("\n".join(selected).encode("utf-8")).hexdigest() != EXPECTED_HASH:
    raise SystemExit("p.249 text changed; inspect before migration")
line_offsets = {}
offset = 0
for line_no, line in zip(range(meta["line_start"], meta["line_end"] + 1), selected):
    line_offsets[line_no] = offset
    offset += len(line) + 1

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)
coverage_by_id = {row["segment_id"]: row for row in coverage}
expected_states = {
    P248: ("reviewed", "partial", "L38-46"),
    P249: ("queued", "pending", ""),
    P250: ("queued", "pending", ""),
    NOTES: ("queued", "pending", ""),
}
for sid, state in expected_states.items():
    row = coverage_by_id.get(sid)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != state:
        raise SystemExit(f"unexpected coverage for {sid}: {row}")

candidate_ids = {row["candidate_id"] for row in candidates}
if len(candidate_ids) != len(candidates) or max(int(cid.split("-")[1]) for cid in candidate_ids) != 8169:
    raise SystemExit("candidate inventory changed; inspect before allocating IDs")
candidate_specs = [
    (8170, "Tempio Malatestiano", "place", 78, "Church at Rimini used by Haskell as a comparison for the façade's human glorification."),
    (8171, "Rimini", "place", 78, "City named as the location of the Tempio Malatestiano."),
    (8172, "Morosini palace opposite S. Maria del Giglio", "place", 79, "Palace identified by its relation to the church; distinct from the Morosini family."),
    (8173, "Venetian constitution as a constitutional order", "term", 80, "The political constitution discussed by contemporary writers, rather than an individual writer or publication."),
    (8174, "Foreign observers of Venetian political power", "term", 80, "Unnamed foreign observers noted the government's concern to prevent a single noble gaining excessive power and popularity."),
    (8175, "Wealth-based admission to the Venetian nobility", "procedure", 81, "Admission to the nobility is described as depending purely on wealth."),
    (8176, "Old and new Venetian families asserting claims", "term", 81, "Collective social groups distinguished by age and status as they asserted claims; no complete list is supplied here."),
    (8177, "Pesaro family", "family", 86, "Old Venetian family cited as an example of inherited political privilege."),
    (8178, "Grand Canal", "place", 84, "Venice waterway along which the Pesaro palace façade is located."),
    (8179, "New mercantile classes entering the Venetian aristocracy", "term", 86, "Collective social group described as buying entry into the aristocracy and asserting influence through patronage."),
    (8180, "Façade of the Pesaro family palace on the Grand Canal", "work", 84, "Architectural frontage described as dramatic and completed about seventeen years after Leonardo Pesaro's death."),
    (8181, "Political status as civic standing", "term", 86, "Civic/political standing that lavish building could help secure in provincial settings."),
    (8182, "Damerini, 1928 publication cited in p.249 note 1", "archive", 87, "Bibliographic source locator for the account of Barbaro's hostility toward Morosini; full title and author identity are unresolved here."),
    (8183, "E. Bassi, 1959 publication cited in p.249 note 4", "archive", 88, "Bibliographic citation continued from consolidated note 4; full title is not stated in this continuation line."),
]
if any(f"cand-{n:04d}" in candidate_ids for n, *_ in candidate_specs):
    raise SystemExit("one or more planned candidate IDs already exist")
existing_keys = {(r["canonical_name"], r["suggested_type"]) for r in candidates}
for number, name, kind, line_no, detail in candidate_specs:
    if (name, kind) in existing_keys:
        raise SystemExit(f"candidate natural-key collision: {name} / {kind}")
    candidates.append({
        "candidate_id": f"cand-{number:04d}", "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open", "index_source_file": "",
        "sub_entry": "", "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{P249}#L{line_no}",
    })
    candidate_ids.add(f"cand-{number:04d}")

existing_mention_ids = {r["mention_id"] for r in mentions}
existing_spans = {(r["segment_id"], r["start_char"], r["end_char"]) for r in mentions}
new_mentions = []


def mention(line_no, suffix, cid, surface, note="", occurrence=0):
    mid = f"m-chp9-p249-{suffix}"
    if mid in existing_mention_ids:
        raise SystemExit(f"duplicate mention ID: {mid}")
    line = source_lines[line_no - 1]
    start_at = 0
    pos = -1
    for _ in range(occurrence + 1):
        pos = line.find(surface, start_at)
        if pos < 0:
            raise SystemExit(f"surface not found at L{line_no}: {surface!r}")
        start_at = pos + len(surface)
    start = line_offsets[line_no] + pos
    end = start + len(surface)
    span = (P249, str(start), str(end))
    if span in existing_spans or any((r["segment_id"], r["start_char"], r["end_char"]) == span for r in new_mentions):
        raise SystemExit(f"duplicate mention span: {mid}")
    if cid not in candidate_ids:
        raise SystemExit(f"missing candidate for mention: {mid} -> {cid}")
    new_mentions.append({"mention_id": mid, "segment_id": P249, "candidate_id": cid,
                         "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


MENTION_SPECS = [
    (78, "tempio", "cand-8170", "Tempio Malatestiano", "Named comparison building."),
    (78, "rimini", "cand-8171", "Rimini", "City location."),
    (79, "antonio-barbaro", "cand-0185", "Antonio Barbaro", "Named patrician; page-248 identity candidate reused."),
    (79, "war-candia", "cand-8154", "war of Candia", "War named in connection with Barbaro's conduct."),
    (79, "francesco-morosini", "cand-1705", "Francesco Morosini", "Named commander and political opponent in Haskell's account."),
    (79, "venice", "cand-2719", "Venice", "City to which Barbaro returned."),
    (79, "morosini-second", "cand-1705", "Morosini", "Surname reference to Francesco Morosini.", 1),
    (79, "church", "cand-0736", "the church", "Coreference to S. Maria del Giglio."),
    (79, "morosini-palace", "cand-8172", "the Morosini palace", "Palace located opposite the church in Barbaro's will."),
    (80, "venetian-constitution", "cand-8173", "Venetian constitution", "Subject of writers' observations."),
    (80, "foreign-observers", "cand-8174", "foreign observers", "Unnamed observer group."),
    (80, "government", "cand-8105", "the government", "Venetian governing entity; existing candidate reused."),
    (80, "single-noble", "cand-8108", "any single noble", "Social estate/person category in the political-power claim."),
    (80, "giglio-church", "cand-0736", "S. Maria del Giglio", "Church whose façade is interpreted as background to the political concern."),
    (81, "state", "cand-8105", "The State", "Venetian political entity, kept distinct from the city."),
    (81, "individual-families", "cand-8176", "individual families", "Collective old and new family interests."),
    (81, "nobility", "cand-8108", "the nobility", "Venetian social estate."),
    (81, "wealth", "cand-8175", "wealth", "Criterion for admission to the nobility."),
    (81, "new-families", "cand-8134", "new families", "Newly admitted families discussed on p.247–248."),
    (82, "leonardo", "cand-1885", "Leonardo", "First part of index-named Leonardo Pesaro across a source line break."),
    (83, "leonardo-surname", "cand-1885", "Pesaro", "Surname completing Leonardo Pesaro; index candidate reused."),
    (83, "doge", "cand-3791", "the Doge", "Context resolves the Doge as Giovanni Pesaro, the subject of Plate 41b."),
    (83, "monument", "cand-4063", "a monument to his uncle", "Specific monument to Doge Giovanni Pesaro."),
    (84, "frari", "cand-3917", "Frari", "Church of the Frari."),
    (84, "pesaro-palace", "cand-1886", "the vast family palace", "Pesaro palace indexed on p.249."),
    (84, "grand-canal", "cand-8178", "the Grand Canal", "Venice waterway bordering the palace."),
    (84, "palace-facade", "cand-8182", "façade", "Pesaro palace architectural frontage."),
    (84, "niccolo", "cand-3846", "Niccolo", "First part of Niccolo Bambini across a source line break."),
    (85, "bambini", "cand-3846", "Bambini", "Surname completing Niccolo Bambini."),
    (85, "triumph-venice", "cand-4066", "the Triumph of Venice", "Ceiling painting title; accepted-KU candidate reused."),
    (86, "old-families", "cand-8176", "Old families", "Established Venetian family group."),
    (86, "pesaro-family", "cand-8177", "the Pesaro", "Family used as example of old political privileges."),
    (86, "mercantile-classes", "cand-8179", "new mercantile classes", "Unnamed social group buying entry into the aristocracy."),
    (86, "aristocracy", "cand-8108", "the aristocracy", "Venetian nobility as a social estate."),
    (86, "political-status", "cand-8181", "political status", "Civic standing associated with provincial building."),
    (87, "damerini-1928", "cand-8182", "Damerini, 1928.", "Footnote 1 bibliographic locator; full title not supplied here."),
    (88, "bassi-1959", "cand-8183", "Bassi, 1959, pp. 240-64.", "Continuation of footnote 4 bibliographic locator."),
]
for spec in MENTION_SPECS:
    mention(*spec)


def quote(first, last):
    return "\n".join(source_lines[first - 1:last])


def statement(sid, first, last, subject, obj, predicate, claim, qualification, mentioned,
              marker=None, note_segment=None, note_start=None, note_end=None, extras=None):
    if first < meta["line_start"] or last > meta["line_end"]:
        raise SystemExit(f"statement lines outside p.249 segment: {sid}")
    if any(cid not in candidate_ids for cid in [subject, obj, *mentioned] if cid):
        raise SystemExit(f"missing candidate in statement: {sid}")
    q = {"source_line_start": first, "source_line_end": last, "printed_page": 249,
         "pdf_physical_page": 11, "claim": claim, "speaker": "Haskell", "text_layer": "body",
         "qualification": qualification, "mentioned_candidate_ids": list(dict.fromkeys(mentioned))}
    if marker is not None:
        q["footnote_marker"] = marker
    if note_segment is not None:
        q["cross_reference_segments"] = [{"segment_id": note_segment,
                                             "source_line_start": note_start,
                                             "source_line_end": note_end}]
    if extras:
        q.update(extras)
    return {"statement_id": sid, "segment_id": P249, "subject_candidate_id": subject,
            "object_candidate_id": obj, "predicate": predicate, "qualifiers": q,
            "original_quote": quote(first, last), "origin": "book", "source_file": meta["source_file"]}


new_statements = [
    statement("st-chp9-p249-tempio-comparison", 78, 78, "cand-8153", "cand-8170",
        "façade_compared_with_tempio_malatestiano", "Closing p.248's sentence, Haskell compares the S. Maria del Giglio façade with the Tempio Malatestiano at Rimini as an extraordinary glorification of humanity in a usually sacred setting, then says the façade had immediate political origins.",
        "The opening 'os' is an OCR error for printed 'of'; comparison and political interpretation remain Haskell's account.",
        ["cand-8153", "cand-0736", "cand-8170", "cand-8171"],
        extras={"continued_from_segment_id": P248, "continued_from_source_line": 46,
                "cross_reference_segments": [{"segment_id": P248, "source_line_start": 46, "source_line_end": 46}],
                "ocr_corrections": [{"source_line": 78, "ocr": "os", "print": "of", "basis": "CHP-9.pdf physical page 11"}]}),
    statement("st-chp9-p249-barbaro-conduct", 79, 79, "cand-0185", "cand-1705",
        "returned_to_venice_and_opposed_morosini", "Haskell says Antonio Barbaro's conduct in the War of Candia was somewhat discreditable; Francesco Morosini dismissed him for incompetence, after which Barbaro returned to Venice and tried to turn hostility against Morosini.",
        "Retain 'somewhat' and the author's evaluative/reporting layer; footnote 1 is a citation locator, not independently checked evidence.",
        ["cand-0185", "cand-8154", "cand-1705", "cand-2719"], marker=1,
        note_segment=P249, note_start=87, note_end=87, extras={"relation_candidate": True}),
    statement("st-chp9-p249-barbaro-will-location", 79, 79, "cand-0185", "cand-8172",
        "will_identified_church_opposite_morosini_palace", "Haskell says Barbaro's will emphasized that the church stood directly opposite the Morosini palace.",
        "The source uses this as part of Barbaro's self-justification; the will itself is only cited and has not been independently examined.",
        ["cand-0185", "cand-0736", "cand-8172"], marker=1,
        note_segment=P249, note_start=87, note_end=87, extras={"relation_candidate": True,
        "additional_citation_context": {"segment_id": P248, "source_line_start": 338, "source_line_end": 338,
                                        "reason": "p.248 note 4 cites publication of Barbaro's will"}}),
    statement("st-chp9-p249-government-limits-noble-power", 79, 80, "cand-8105", "cand-8108",
        "government_sought_to_limit_single_noble_power_and_popularity", "Haskell reports that constitutional writers and foreign observers around this time noticed the government's concern to prevent one noble from gaining excessive power and popularity.",
        "This is Haskell's summary of contemporary observations. Marker 2 links to a 1704 British Resident report; that cited document remains unverified.",
        ["cand-8173", "cand-8174", "cand-8105", "cand-8108"], marker=2,
        note_segment=NOTES, note_start=339, note_end=339),
    statement("st-chp9-p249-family-wealth-and-patronage-pattern", 81, 81, "cand-8105", "cand-8175",
        "wealth_governed_noble_admission_amid_war_exhaustion", "Haskell says the State was exhausted by long wars while families remained as wealthy as before, and admission to the nobility depended purely on wealth; old and new families then asserted claims in a pattern later important to painting.",
        "Preserve the comparative wording 'as rich or richer than ever' and the author's causal/historical interpretation; no family is individually named here.",
        ["cand-8105", "cand-8176", "cand-8134", "cand-8108", "cand-8175"], extras={"relation_candidate": True}),
    statement("st-chp9-p249-pesaro-ostentation-and-virtue", 82, 83, "cand-1885", "cand-8108",
        "contemporaries_measured_leonardo_pesaro_virtue_by_splendour", "Haskell says noble ostentation increased through the late seventeenth century and singles out Leonardo Pesaro; contemporaries claimed his unprecedented splendour measured the greatness of his virtue.",
        "Retain 'with some justification' and the attribution to contemporaries, rather than treating their judgement as an objective measurement.",
        ["cand-1885", "cand-8108", "cand-3791"], marker=3, note_segment=NOTES, note_start=340, note_end=340),
    statement("st-chp9-p249-pesaro-monument", 83, 84, "cand-1885", "cand-4063",
        "built_monument_to_uncle_in_frari_in_1669", "In 1669 Leonardo Pesaro had a monument to his uncle, Doge Giovanni Pesaro, built in the Frari; Haskell says it surpassed earlier monuments in grandeur.",
        "The uncle's identity is resolved from the monument named in Plate 41b; preserve Haskell's comparative assessment.",
        ["cand-1885", "cand-3791", "cand-4063", "cand-3917"], extras={"relation_candidate": True}),
    statement("st-chp9-p249-pesaro-palace", 84, 84, "cand-1885", "cand-1886",
        "continued_family_palace_on_grand_canal", "Leonardo continued the vast Pesaro family palace; its dramatic façade on the Grand Canal was completed about seventeen years after his death.",
        "Preserve 'about' and the stated interval; the sentence does not give an exact completion year.",
        ["cand-1885", "cand-1886", "cand-8178", "cand-8182"]),
    statement("st-chp9-p249-bambini-triumph-venice", 84, 85, "cand-1885", "cand-4066",
        "commissioned_bambini_ceiling_painting_in_1682", "In 1682 Leonardo commissioned Niccolo Bambini to paint a ceiling representing the Triumph of Venice, which Haskell calls the first appearance of that theme in a private palace.",
        "Preserve the stated title and priority claim. Footnote 4 says the subject appears to be Venice and gives alternate title history; it is a cited interpretation, not an unqualified identity correction.",
        ["cand-1885", "cand-3846", "cand-4066"], marker=4,
        note_segment=NOTES, note_start=341, note_end=341, extras={"relation_candidate": True,
        "additional_citation_continuation": {"segment_id": P249, "source_line_start": 88, "source_line_end": 88}}),
    statement("st-chp9-p249-old-and-mercantile-families", 86, 86, "cand-8179", "cand-8108",
        "new_mercantile_classes_used_patronage_to_assert_status", "Haskell contrasts the political privileges of old families such as the Pesaro with new mercantile classes buying into the aristocracy and gaining visibility through patronage; in provincial settings, lavish building could be essential to political advancement.",
        "Retain the author's scope markers 'like' and 'at least' and the modal 'sometimes'; note 5's Montanari example is linked but not independently checked.",
        ["cand-8177", "cand-8179", "cand-8108", "cand-2720", "cand-8181"], marker=5,
        note_segment=NOTES, note_start=342, note_end=342, extras={"relation_candidate": True,
        "continuation_to_segment_id": P250, "continuation_to_source_line": 91}),
    statement("st-chp9-p249-damerini-citation", 87, 87, "cand-8182", None,
        "footnote_citation", "Printed note 1 cites a 1928 work by Damerini in connection with the preceding account of Barbaro and Morosini.",
        "Citation only; the work's full title, author identity and cited passage have not been independently verified.",
        ["cand-8182"], marker=1),
    statement("st-chp9-p249-bassi-citation-continuation", 88, 88, "cand-8183", None,
        "continues_footnote_citation", "The printed continuation line gives E. Bassi, 1959, pages 240–264, completing note 4's bibliographic list.",
        "This page-bottom citation line continues the consolidated OCR note at L341, which ends with 'and E.'; it is not a new footnote.",
        ["cand-8183"], marker=4, note_segment=NOTES, note_start=341, note_end=341,
        extras={"continued_from_segment_id": NOTES, "continued_from_source_line": 341}),
]
statement_ids = {r["statement_id"] for r in statements}
new_statement_ids = {r["statement_id"] for r in new_statements}
if len(statement_ids) != len(statements) or len(new_statement_ids) != len(new_statements) or statement_ids & new_statement_ids:
    raise SystemExit("duplicate statement ID")

coverage_by_id[P248].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L38-46",
    "note": "Printed p.248 reviewed against the page image. The final sentence ending 'devoid' is closed at p.249 L78 ('of a single religious symbol') and cross-linked in book-statements. Its body claims and note markers link to consolidated notes L335-338. Plate 41-44 are handled as separate visual material."
})
coverage_by_id[P249].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L77-88",
    "note": "Printed p.249 (CHP-9.pdf physical p.11) reviewed against the page image. L78 closes p.248 L46; L86 ends 'At' and continues at p.250 L91. Body claims, note markers 1-5, the printed note 1 locator at L87, and the note 4 citation continuation at L88 are separated and linked. Consolidated notes L339-342 remain the citation/evidence text layer for markers 2-5 and will be semantically migrated in source order. OCR 'os' at L78 is 'of' in print; source OCR is unchanged."
})

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
print(json.dumps({"segments": [P248, P249], "new_candidates": len(candidate_specs),
                  "new_mentions": len(new_mentions), "new_statements": len(new_statements),
                  "coverage": {sid: [coverage_by_id[sid]["disposition"], coverage_by_id[sid]["migration_status"]]
                               for sid in (P248, P249)},
                  "continuations": [f"{P248} L46 -> {P249} L78", f"{P249} L86 -> {P250} L91"],
                  "note_links": [f"marker 1 -> {P249} L87", f"marker 2 -> {NOTES} L339",
                                 f"marker 3 -> {NOTES} L340", f"marker 4 -> {NOTES} L341 + {P249} L88",
                                 f"marker 5 -> {NOTES} L342"]}, ensure_ascii=False))
if not args.apply:
    print("DRY RUN: no files changed")
else:
    paths = [candidate_path, mention_path, statement_path, coverage_path]
    backups = []
    for path in paths:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"refusing to overwrite existing backup: {backup.name}")
        backups.append((path, backup))
    for path, backup in backups:
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions + new_mentions)
    write_jsonl(statement_path, statements + new_statements)
    write_csv(coverage_path, coverage_fields, list(coverage_by_id.values()))
    print("applied; backups=" + ", ".join(backup.name for _, backup in backups))
