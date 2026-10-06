"""Controlled S2 migration for chapter 8 printed p.214 body.

Default invocation is read-only. It validates the canonical S0 segment,
closes p.213's open Durazzo sentence, validates mention offsets and statement
quotes, and then --apply writes the four S2 tables with recovery backups.
"""
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
BODY_REL = "02-sources/02-Markdown/08_CHP-8_sec_i.md"
BODY_ID = "chp-8:08_CHP-8_sec_i:l120-124"
PREVIOUS_ID = "chp-8:08_CHP-8_sec_i:l108-118"
PREVIOUS_STATEMENT = "st-chp8-p213-durazzo-local-collection-and-bologna-open"
CONTINUATION_STATEMENT = "st-chp8-p214-durazzo-naples-continuation"
CURRENT_MAX_CANDIDATE = 7573
BACKUP_SUFFIX = ".bak-s2-chp8-p214-body-20260930"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent,
                                     delete=False, suffix=".tmp") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl_atomic(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent,
                                     delete=False, suffix=".tmp") as stream:
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
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}

segment = segments.get(BODY_ID)
if not segment or segment["source_file"] != BODY_REL or (int(segment["line_start"]), int(segment["line_end"])) != (120, 124):
    raise SystemExit(f"segment metadata changed; review before migration: {BODY_ID}")
source_path = ROOT / BODY_REL
source_bytes = source_path.read_bytes()
if hashlib.sha256(source_bytes).hexdigest() != segment["asset_sha256"]:
    raise SystemExit(f"source asset fingerprint changed: {BODY_REL}")
source_lines = source_path.read_text(encoding="utf-8-sig").splitlines()
segment_lines = source_lines[119:124]
segment_text = "\n".join(segment_lines)
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != segment["sha256"]:
    raise SystemExit(f"source line-slice hash changed: {BODY_ID}")
if (coverage_by_id.get(BODY_ID, {}).get("disposition"), coverage_by_id.get(BODY_ID, {}).get("migration_status")) != ("queued", "pending"):
    raise SystemExit(f"unexpected coverage state for {BODY_ID}")

candidate_ids = {row["candidate_id"] for row in candidate_rows}
mention_ids = {row["mention_id"] for row in mention_rows}
statement_ids = {row["statement_id"] for row in statement_rows}
current_max = max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows)
if current_max != CURRENT_MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: expected {CURRENT_MAX_CANDIDATE}, found {current_max}")

candidate_specs = [
    ("solimena_two_histories", "Two further Old Testament history paintings by Francesco Solimena, c.1704 (Durazzo collection context)", "work",
     "Haskell names Judith with the Head of Holofernes and Deborah and Barach as two further histories in the continuing Girolamo Durazzo collection discussion. The date is approximate; the sentence does not repeat the patron's name, so retain that contextual qualification.", 122),
    ("baglioni_family_venice", "Baglioni family of wealthy publishers in Venice", "family",
     "Family described by Haskell as rich publishers who entered the nobility early in the eighteenth century. Keep distinct from the Baglioni family candidate cand-4279 from the Perugia passage until S3 alignment establishes identity.", 123),
    ("baglioni_picture_group", "Baglioni collection pictures by Luca Giordano and Francesco Solimena", "work",
     "Source-described paintings by the same two artists said to hang together in the Baglioni collection. The passage specifies several Giordano pictures and two Solimena works, naming Jacob and Rebecca and Rebecca and Eliezer; do not infer a complete inventory or resolve the antecedent of the final 'whose influence' beyond the wording.", 124),
    ("neapolitan_art_baglioni", "Neapolitan art in the Baglioni collection passage", "term",
     "Haskell's source-specific category for the Baglioni family's interest in art from Naples; keep cross-chapter concept alignment for S3.", 124),
]

candidate_by_key = {}
new_candidates = []
next_number = current_max + 1
for key, name, typ, detail, line in candidate_specs:
    candidate_id = f"cand-{next_number:04d}"
    next_number += 1
    candidate_by_key[key] = candidate_id
    new_candidates.append({
        "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": typ, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY_ID}#L{line}",
    })

EXISTING = {
    "durazzo": "cand-0953", "durazzo_family": "cand-7360",
    "durazzo_local_collection": "cand-7572", "durazzo_giordano_pictures": "cand-7573",
    "bologna": "cand-0381", "naples": "cand-3534",
    "giordano": "cand-1172", "tasso": "cand-2544",
    "giordano_sophronia": "cand-1184", "giordano_seneca": "cand-1177",
    "giordano_jezebel": "cand-1180", "giordano_perseus": "cand-1183",
    "solimena": "cand-2484", "solimena_judith": "cand-2488",
    "solimena_deborah": "cand-2485", "baglioni_collection": "cand-0159",
    "venice": "cand-2719", "preti": "cand-2056",
    "solimena_jacob": "cand-2487", "solimena_rebecca": "cand-2491",
    "pittoni": "cand-1950", "tiepolo": "cand-2569",
}


def cid(key: str) -> str:
    return candidate_by_key[key] if key in candidate_by_key else EXISTING[key]


mention_specs = [
    (121, "Naples", "naples", 0, "Completes p.213's open contrast: Durazzo turned to Naples as well as Bologna."),
    (121, "Luca Giordano", "giordano", 0, "Artist named as painter of four canvases for the Durazzo family."),
    (121, "four canvases", "durazzo_giordano_pictures", 0, "The Durazzo Giordano picture group reserved on p.213; this page identifies four canvases and lists their subjects."),
    (121, "the family", "durazzo_family", 0, "Anaphoric reference to Girolamo Durazzo's family, introduced at p.213 L117-118; not the Del Rosso family discussed earlier."),
    (122, "Tasso", "tasso", 0, "Surname only in the source, mapped to the existing Torquato Tasso index candidate; retain the full-name alignment for S3."),
    (122, "Sophronia and Olindo", "giordano_sophronia", 0, "One of Giordano's four canvases for the Durazzo family; the index-derived candidate is reused."),
    (122, "The Death of Seneca", "giordano_seneca", 0, "One of the four Giordano canvases; reuse the p.214 Giordano index candidate, distinct from Pittoni's similarly titled work."),
    (122, "the Old Testament", "giordano_jezebel", 0, "Subject category for the following Jezebel canvas."),
    (122, "Queen Jezebel torn to pieces by Dogs", "giordano_jezebel", 0, "One of the four Giordano canvases; title and source spelling follow p.214."),
    (122, "mythology", "giordano_perseus", 0, "Subject category for the following Perseus canvas."),
    (122, "Perseus and Andromeda", "giordano_perseus", 0, "One of the four Giordano canvases; reuse the p.214 Giordano index candidate."),
    (122, "about 1704", "solimena_two_histories", 0, "Approximate date for Solimena's two further histories."),
    (122, "Francesco Solimena", "solimena", 0, "Artist named in the Durazzo collection discussion; reuse the index candidate."),
    (122, "two further vast histories", "solimena_two_histories", 0, "Group of two Old Testament history paintings attributed to Solimena in the continuing Durazzo context."),
    (122, "the Old Testament", "solimena_two_histories", 1, "Subject category for Solimena's two further histories."),
    (122, "Judith with the Head of", "solimena_judith", 0, "First part of the title split across the source line boundary."),
    (123, "Holofernes", "solimena_judith", 0, "Title continuation from p.214 L122; the page image confirms the printed spelling."),
    (123, "Deborah and Barach", "solimena_deborah", 0, "Source and page image read 'Barach'; the p.214 index seed spells the sub-entry 'Barak'. Preserve the source form and leave the discrepancy unresolved."),
    (123, "Pictures by the same two artists", "baglioni_picture_group", 0, "Collective reference to pictures by Luca Giordano and Francesco Solimena; the following clauses specify some holdings."),
    (123, "one other important collection", "baglioni_collection", 0, "The collection outside Naples identified as belonging to the Baglioni."),
    (123, "outside Naples", "naples", 0, "Geographical contrast for the Baglioni collection, not a claim about the origin of each picture."),
    (123, "Baglioni", "baglioni_family_venice", 0, "Family name in the phrase 'the Baglioni in Venice'; keep distinct from the separate Perugia Baglioni candidate until S3."),
    (123, "Venice", "venice", 0, "Location of the Baglioni collection and family in this passage."),
    (123, "a family of rich publishers", "baglioni_family_venice", 0, "Apposition identifying the Baglioni as a family of wealthy publishers."),
    (123, "bought their way into the nobility", "baglioni_family_venice", 0, "Haskell's characterization of the family's early-eighteenth-century entry into nobility; preserve as source attribution."),
    (123, "They", "baglioni_family_venice", 0, "Anaphoric reference to the Baglioni family."),
    (123, "a great interest in Neapolitan art", "neapolitan_art_baglioni", 0, "Haskell's description of the family's interest; do not expand this to an external classification."),
    (123, "Mattia", "preti", 0, "First part of the artist's name, split across the S0 line boundary."),
    (124, "Preti", "preti", 0, "Continuation of the artist name at the start of p.214 L124."),
    (124, "they owned", "baglioni_family_venice", 0, "The Baglioni family, subject of the holdings statement."),
    (124, "several by Luca Giordano", "baglioni_picture_group", 0, "Unquantified several Giordano pictures in the Baglioni collection; no titles are given here."),
    (124, "Luca Giordano", "giordano", 0, "Artist whose pictures the Baglioni owned; reuse the existing candidate."),
    (124, "two by Solimena", "baglioni_picture_group", 0, "Two Solimena pictures in the Baglioni holdings, named immediately afterward."),
    (124, "Solimena", "solimena", 0, "Artist whose two named pictures were owned by the Baglioni."),
    (124, "Jacob and Rebecca", "solimena_jacob", 0, "One of the two Solimena pictures in the Baglioni collection; reuse the p.214 index candidate."),
    (124, "Rebecca and Eliezer", "solimena_rebecca", 0, "The other named Solimena picture in the Baglioni collection; reuse the p.214 index candidate."),
    (124, "whose influence", "baglioni_picture_group", 0, "The antecedent may be the two immediately named Solimena pictures or the wider Baglioni holdings by both artists; do not assign influence item by item."),
    (124, "Pittoni", "pittoni", 0, "Artist named as a recipient of the influence Haskell describes."),
    (124, "the young Tiepolo", "tiepolo", 0, "Tiepolo is described only as young here; reuse the index candidate and leave identity alignment to S3."),
]


def add_mentions():
    line_offsets = {}
    offset = 0
    for number in range(120, 125):
        line_offsets[number] = offset
        offset += len(source_lines[number - 1]) + 1
    result = []
    for number, surface, key, occurrence, note in mention_specs:
        spans = [m.span() for m in re.finditer(re.escape(surface), source_lines[number - 1])]
        if occurrence >= len(spans):
            raise SystemExit(f"mention not found: {BODY_ID} L{number} {surface!r} occurrence {occurrence}; found {len(spans)}")
        start_local, end_local = spans[occurrence]
        start_char = line_offsets[number] + start_local
        end_char = line_offsets[number] + end_local
        if segment_text[start_char:end_char] != surface:
            raise SystemExit(f"mention offset mismatch: {BODY_ID} L{number} {surface!r}")
        result.append({
            "mention_id": f"m-chp8-p214-{len(result)+1:03d}", "segment_id": BODY_ID,
            "candidate_id": cid(key), "surface_form": surface,
            "start_char": str(start_char), "end_char": str(end_char), "note": note,
        })
    return result


new_mentions = add_mentions()
if len({row["candidate_id"] for row in new_candidates}) != len(new_candidates) or candidate_ids & {row["candidate_id"] for row in new_candidates}:
    raise SystemExit("planned candidate ID collision")
if len({row["mention_id"] for row in new_mentions}) != len(new_mentions) or mention_ids & {row["mention_id"] for row in new_mentions}:
    raise SystemExit("planned mention ID collision")
if statement_ids & {CONTINUATION_STATEMENT,
                     "st-chp8-p214-giordano-four-canvases-for-durazzo",
                     "st-chp8-p214-solimena-two-histories",
                     "st-chp8-p214-baglioni-pictures-in-collection",
                     "st-chp8-p214-baglioni-family-publishers-and-nobility",
                     "st-chp8-p214-baglioni-neapolitan-holdings",
                     "st-chp8-p214-influence-on-pittoni-and-tiepolo"}:
    raise SystemExit("planned statement ID collision")

all_candidate_ids = candidate_ids | {row["candidate_id"] for row in new_candidates}
previous = next((row for row in statement_rows if row["statement_id"] == PREVIOUS_STATEMENT), None)
if not previous:
    raise SystemExit(f"previous open statement not found: {PREVIOUS_STATEMENT}")
previous_qualifiers = dict(previous.get("qualifiers", {}))
if previous_qualifiers.get("continuation_status") != "open" or previous_qualifiers.get("continuation_expected_segment_id") != BODY_ID:
    raise SystemExit("p.213 Durazzo continuation changed; inspect before closing")
candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
expected_group = candidate_by_id.get("cand-7573")
if not expected_group or expected_group.get("canonical_name") != "Unidentified Luca Giordano pictures acquired by Girolamo Durazzo for the Durazzo family":
    raise SystemExit("reserved p.213 Durazzo-Giordano picture group changed; inspect before refining")


def make_statement(tail, start, end, predicate, claim, qualification, quote,
                   subject=None, object_=None, mentioned=(), extra=None):
    row = {
        "statement_id": f"st-chp8-p214-{tail}", "segment_id": BODY_ID,
        "subject_candidate_id": cid(subject) if subject else None,
        "object_candidate_id": cid(object_) if object_ else None,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": start, "source_line_end": end,
            "printed_page": 214, "pdf_physical_page": 12,
            "claim": claim, "speaker": "Haskell", "text_layer": "body",
            "qualification": qualification,
            "mentioned_candidate_ids": list(dict.fromkeys(cid(key) for key in mentioned)),
        },
        "original_quote": quote, "origin": "book", "source_file": BODY_REL,
    }
    if extra:
        row["qualifiers"].update(extra)
    return row


statements = [
    make_statement("durazzo-naples-continuation", 121, 121,
        "durazzo_picture_sources_include_bologna_and_naples",
        "Haskell completes p.213's sentence: Girolamo Durazzo turned to Naples as well as Bologna for many of his pictures; the phrase 'as was usual enough' qualifies the Bologna route.",
        "This closes the open p.213 sentence. The following Giordano and Solimena paintings are presented in the continuing Durazzo collection discussion, but their precise acquisition path should not be strengthened beyond the wording.",
        "usual enough),1 but also to Naples.", subject="durazzo", object_="naples",
        mentioned=["durazzo_family", "durazzo_local_collection", "durazzo_giordano_pictures", "bologna", "naples"]),
    make_statement("giordano-four-canvases-for-durazzo", 121, 122,
        "giordano_painted_four_canvases_for_durazzo_family",
        "Haskell says Luca Giordano painted four canvases for Girolamo Durazzo's family: Sophronia and Olindo, The Death of Seneca, Queen Jezebel torn to pieces by Dogs, and Perseus and Andromeda.",
        "The referent of 'the family' is Durazzo, the patron just introduced on p.213, not the Del Rosso family discussed earlier. Haskell places this account after Durazzo's turn to Naples but does not give an individual commission date or say each canvas followed the same route.",
        "Luca Giordano painted four canvases for the family\n—one scene from Tasso (Sophronia and Olindo), one from Roman history (The Death of Seneca), one from the Old Testament (Queen Jezebel torn to pieces by Dogs) and one from mythology (Perseus and Andromeda).",
        subject="giordano", object_="durazzo_family",
        mentioned=["durazzo_giordano_pictures", "durazzo_family", "tasso", "giordano_sophronia", "giordano_seneca", "giordano_jezebel", "giordano_perseus"]),
    make_statement("solimena-two-histories", 122, 123,
        "solimena_added_two_old_testament_histories_about_1704",
        "Haskell says that about 1704 Francesco Solimena added two further large Old Testament histories, Judith with the Head of Holofernes and Deborah and Barach.",
        "The approximate date and source spelling 'Barach' are preserved. The passage continues the Durazzo collection account, but the clause does not repeat the family name; do not turn contextual placement into a more specific commission claim.",
        "And, in about 1704, Francesco Solimena added two further vast histories from the Old Testament-Judith with the Head of\nHolofernes and Deborah and Barach.",
        subject="solimena", object_="solimena_two_histories",
        mentioned=["solimena", "solimena_two_histories", "solimena_judith", "solimena_deborah", "durazzo_family"],
        extra={"ocr_corrections": [{"source_line": 122, "ocr": "Old Testament-Judith", "print": "Old Testament—Judith", "basis": "CHP-8.pdf physical page 12 image; the printed dash is an em dash, recorded in S2 only."}]}),
    make_statement("baglioni-pictures-in-collection", 123, 123,
        "giordano_and_solimena_pictures_hung_together_in_baglioni_collection",
        "Haskell identifies the Baglioni collection in Venice as another important collection outside Naples in which pictures by Luca Giordano and Francesco Solimena hung together.",
        "The passage does not name which pictures in this clause; later on the same page it names several Giordano works without titles and two Solimena pictures. Do not infer that the four Durazzo canvases were also in the Baglioni collection.",
        "Pictures by the same two artists hung together in one other important collection outside Naples, that of the Baglioni in Venice",
        object_="baglioni_collection",
        mentioned=["baglioni_picture_group", "baglioni_collection", "baglioni_family_venice", "venice", "naples", "giordano", "solimena"]),
    make_statement("baglioni-family-publishers-and-nobility", 123, 123,
        "baglioni_family_publishers_entered_nobility_early_eighteenth_century",
        "Haskell describes the Venetian Baglioni as a family of wealthy publishers who entered the nobility early in the eighteenth century, in his phrase, 'bought their way into the nobility'.",
        "This is Haskell's characterization; no named family members, date of ennoblement or independent source is supplied in this passage.",
        "a family of rich publishers who early in the eighteenth century bought their way into the nobility.",
        subject="baglioni_family_venice", mentioned=["baglioni_family_venice", "baglioni_collection", "venice"]),
    make_statement("baglioni-neapolitan-holdings", 123, 124,
        "baglioni_family_interested_in_neapolitan_art_and_owned_pictures",
        "Haskell says the Baglioni showed great interest in Neapolitan art: besides pictures by Mattia Preti, they owned several by Luca Giordano and two by Francesco Solimena, including Jacob and Rebecca and Rebecca and Eliezer.",
        "The Giordano titles and the total number of their pictures are not supplied here. Reuse the indexed Solimena title candidates; the printed/S0 reading 'Deborah and Barach' above differs from the index sub-entry 'Deborah and Barak' and remains unresolved.",
        "They showed a great interest in Neapolitan art, for besides pictures by Mattia\nPreti they owned several by Luca Giordano and two by Solimena—Jacob and Rebecca and Rebecca and Eliezer4—",
        subject="baglioni_family_venice", object_="baglioni_collection",
        mentioned=["baglioni_family_venice", "neapolitan_art_baglioni", "preti", "baglioni_picture_group", "giordano", "solimena", "solimena_jacob", "solimena_rebecca"]),
    make_statement("influence-on-pittoni-and-tiepolo", 124, 124,
        "preceding_baglioni_picture_influence_on_pittoni_and_tiepolo",
        "Haskell says that the influence referred to by 'whose' on Pittoni and the young Tiepolo was considerable.",
        "The exact antecedent of 'whose' is unresolved: it may be the two immediately named Solimena pictures, or more broadly the preceding Baglioni holdings by Giordano and Solimena. Preserve the source-level claim without assigning influence to each individual painting or specifying a mechanism.",
        "whose influence on Pittoni and the young Tiepolo was considerable.",
        subject="baglioni_picture_group",
        mentioned=["baglioni_picture_group", "solimena_jacob", "solimena_rebecca", "pittoni", "tiepolo"]),
]

if len({row["statement_id"] for row in statements}) != len(statements) or statement_ids & {row["statement_id"] for row in statements}:
    raise SystemExit("planned statement ID collision")
for row in statements:
    q = row["qualifiers"]
    start, end = q["source_line_start"], q["source_line_end"]
    cited = "\n".join(source_lines[start - 1:end])
    if " ".join(row["original_quote"].split()) not in " ".join(cited.split()):
        raise SystemExit(f"quote not reproducible: {row['statement_id']}\n{row['original_quote']}")
    referenced = set(q.get("mentioned_candidate_ids", []))
    if row.get("subject_candidate_id"):
        referenced.add(row["subject_candidate_id"])
    if row.get("object_candidate_id"):
        referenced.add(row["object_candidate_id"])
    if not referenced <= all_candidate_ids:
        raise SystemExit(f"missing candidate FK: {row['statement_id']}: {referenced - all_candidate_ids}")

updated_candidates = []
refined_durazzo_group = False
for original in candidate_rows:
    row = dict(original)
    if row["candidate_id"] == "cand-7573":
        row["canonical_name"] = "Four Luca Giordano canvases painted for Girolamo Durazzo's family"
        row["detail"] = "Created from p.213's open reference to Durazzo pictures and resolved on p.214: Haskell says Giordano painted four canvases for the family and lists the subjects. Keep the group tied to this sentence; its precise acquisition path from Bologna or Naples is not stated item by item."
        refined_durazzo_group = True
    updated_candidates.append(row)
if not refined_durazzo_group:
    raise SystemExit("reserved Durazzo-Giordano candidate not found")
updated_candidates.extend(new_candidates)

updated_statements = []
closed_previous = False
for original in statement_rows:
    row = dict(original)
    if row["statement_id"] == PREVIOUS_STATEMENT:
        q = dict(row.get("qualifiers", {}))
        q.update({
            "continuation_status": "closed",
            "continuation_source_segment_id": BODY_ID,
            "continuation_source_line": 121,
            "continuation_statement_id": CONTINUATION_STATEMENT,
            "continuation_resolution": "p.214 L121 completes p.213 L118: 'usual enough), but also to Naples.' This continues Girolamo Durazzo's turn to Bologna for pictures and adds Naples.",
        })
        q.pop("continuation_expected_segment_id", None)
        q.pop("continuation_note", None)
        ids = list(q.get("mentioned_candidate_ids", []))
        if cid("naples") not in ids:
            ids.append(cid("naples"))
        row["qualifiers"] = q
        closed_previous = True
    updated_statements.append(row)
if not closed_previous:
    raise SystemExit("expected p.213 open statement was not closed")
updated_statements.extend(statements)

coverage_updates = {
    PREVIOUS_ID: {
        "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L109-118",
        "note": "p.213 body read against CHP-8.pdf physical p.11. Its Durazzo/Bologna sentence is closed by p.214 L121 ('usual enough), but also to Naples'); p.213 footnote 1 and p.212–213 notes remain in the later canonical notes segment. Other OCR corrections remain recorded in S2 only.",
    },
    BODY_ID: {
        "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L121-124",
        "note": "p.214 body read against CHP-8.pdf physical p.12. Closes p.213's Durazzo/Bologna sentence, identifies Giordano's four canvases for the Durazzo family and Solimena's two further histories, then describes the Baglioni collection and its Neapolitan holdings. 'The family' refers to Durazzo; Baglioni is kept distinct from the Perugia Baglioni candidate. Page-image correction 'Old Testament-Judith'→'Old Testament—Judith' is recorded in S2 only. Printed notes 1–4 remain in the canonical notes segment; the OCR copy of p.214 note 4 truncates at 'Nos.' and its print continuation requires a derived visual transcription before note coverage can close.",
    },
}
updated_coverage = []
found = set()
for original in coverage_rows:
    row = dict(original)
    if row["segment_id"] in coverage_updates:
        row.update(coverage_updates[row["segment_id"]])
        found.add(row["segment_id"])
    updated_coverage.append(row)
if found != set(coverage_updates):
    raise SystemExit(f"coverage update targets not found: {set(coverage_updates)-found}")

preview = {
    "mode": "dry-run", "segment_id": BODY_ID,
    "new_candidates": len(new_candidates), "candidate_ids": [r["candidate_id"] for r in new_candidates],
    "refined_candidate": "cand-7573",
    "new_mentions": len(new_mentions), "new_statements": len(statements),
    "closed_previous_statement": PREVIOUS_STATEMENT,
    "closed_by_statement": CONTINUATION_STATEMENT,
    "coverage": coverage_updates,
    "note_scope_warning": "p.214 note 4 OCR source ends at 'Nos.'; page-image transcription remains to be added during the canonical notes segment.",
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write validated tables and create recovery backups")
if not parser.parse_args().apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)

for path in (candidate_path, mention_path, statement_path, coverage_path):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(path, backup)

updated_mentions = [dict(row) for row in mention_rows] + new_mentions
write_csv_atomic(candidate_path, candidate_fields, updated_candidates)
write_csv_atomic(mention_path, mention_fields, updated_mentions)
write_jsonl_atomic(statement_path, updated_statements)
write_csv_atomic(coverage_path, coverage_fields, updated_coverage)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
