"""Controlled S2 migration for printed p.372 and the remaining p.372 note."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-15.pdf"
SOURCE_SHA = "eea847f75c7876dc5b8ea38ef4b64ad30cdd6c629df6a064125ac5f63917d31f"
PDF_SHA = "357e830cc4e880909edd62975bfcd06ade1c2b432d8866229831025fe86f2885"
BODY_PREV = "chp-15:15_CHP-15_sec_ii:l69-83"
BODY = "chp-15:15_CHP-15_sec_ii:l85-88"
NOTES = "chp-15:15_CHP-15_sec_ii:l90-113"
PREV_STATEMENT = "st-chp15-p371-querini-renier-canova-bust-commission-partial"
BACKUP_SUFFIX = ".bak-s2-chp15-p372-querini-apply-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply the reviewed p.372 S2 migration")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


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
    raise SystemExit("chapter 15 source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-15 PDF asset changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
for line_number, terms in {
    86: ("to become Doge in 1779", "Renier compromised", "Querini flung the bust", "Altar of"),
    87: ("shrines and temples of paganism", "Scipione Maffei", "antique sculpture", "Winckelmann"),
    88: ("influence of Rousseau", "died in 1796", "Temple of Pallas"),
    113: ("Brunelli Bonetti, 1951", "bust (in terracotta)", "Museo Civico", "Padua", "Querini"),
}.items():
    for term in terms:
        if term.casefold() not in source_lines[line_number - 1].casefold():
            raise SystemExit(f"required source text changed at L{line_number}: {term}")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
coverage_fields, coverage = read_csv(coverage_path)
candidate_by_id = {row["candidate_id"]: row for row in candidates}
mention_by_id = {row["mention_id"]: row for row in mentions}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}

for segment_id in (BODY_PREV, BODY, NOTES):
    if segment_id not in coverage_by_id:
        raise SystemExit(f"missing coverage row: {segment_id}")
if (coverage_by_id[BODY_PREV]["migration_status"] != "partial"
        or coverage_by_id[BODY]["migration_status"] != "pending"
        or coverage_by_id[NOTES]["migration_status"] != "partial"
        or coverage_by_id[NOTES]["source_line_ranges"] != "L91-112"):
    raise SystemExit("S2 coverage preconditions changed")
if PREV_STATEMENT not in statement_by_id or statement_by_id[PREV_STATEMENT].get("qualifiers", {}).get("predicate_status") != "partial":
    raise SystemExit("expected p.371 continuation statement is not partial")
if any(row["segment_id"] == BODY for row in mentions):
    raise SystemExit("p.372 body already has mention rows")
notes_l113_start = sum(len(source_lines[number - 1]) + 1 for number in range(90, 113))
notes_l113_end = notes_l113_start + len(source_lines[112])
if any(row["segment_id"] == NOTES and int(row["start_char"]) < notes_l113_end
       and int(row["end_char"]) > notes_l113_start for row in mentions):
    raise SystemExit("p.372 note L113 already has mention rows")
if any(row.get("statement_id", "").startswith("st-chp15-p372-") for row in statements):
    raise SystemExit("p.372 statements already exist")

new_candidates = [
    ("cand-10595", "Altar of Furies in Querini's garden at Alticchiero", "work", 86,
     "Haskell reports that Querini flung Canova's bust of Paolo Renier against this altar in anger; the altar's object history and present state are not given."),
    ("cand-10596", "Temple of Pallas in Querini's garden at Alticchiero", "place", 88,
     "Haskell says Querini requested that his heart be buried there in 1796; the structure's precise identity and survival are not established here."),
    ("cand-10597", "Museo Civico at Padua (museum reported to hold the terracotta bust)", "institution", 113,
     "Haskell's note says that what must be the Renier bust survives there in terracotta; exact institutional identity and the custody claim are not independently verified."),
]
for cid, name, suggested_type, source_line, detail in new_candidates:
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {cid}")
    row = {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": suggested_type, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY}#L{source_line}" if source_line < 90 else f"{NOTES}#L{source_line}",
    }
    candidates.append(row)
    candidate_by_id[cid] = row
candidate_by_id["cand-10586"]["detail"] = (
    "Haskell reports that Querini commissioned a bust of Paolo Renier from Canova and later flung it against the "
    "Altar of Furies; a 1951 note tentatively identifies a terracotta bust at Museo Civico, Padua as this object. "
    "The note's identification and custody claims remain unverified."
)

segment_lines = {
    BODY: {number: source_lines[number - 1] for number in range(85, 89)},
    NOTES: {number: source_lines[number - 1] for number in range(90, 114)},
}
segment_offsets = {}
for segment_id, lines in segment_lines.items():
    offset = 0
    segment_offsets[segment_id] = {}
    for number, line in lines.items():
        segment_offsets[segment_id][number] = offset
        offset += len(line) + 1

planned_mentions = []


def add_mention(candidate_id, surface, segment_id, source_line, note=""):
    if candidate_id not in candidate_by_id:
        raise SystemExit(f"mention candidate missing: {candidate_id}")
    if "\n" in surface:
        segment_text = "\n".join(segment_lines[segment_id].values())
        start = segment_text.find(surface)
        if start < 0:
            raise SystemExit(f"surface not found across lines from L{source_line}: {surface!r}")
        end = start + len(surface)
    else:
        line = segment_lines[segment_id][source_line]
        pos = line.find(surface)
        if pos < 0:
            raise SystemExit(f"surface not found at L{source_line}: {surface}")
        start = segment_offsets[segment_id][source_line] + pos
        end = start + len(surface)
    occupied = [(int(row["start_char"]), int(row["end_char"])) for row in mentions + planned_mentions if row["segment_id"] == segment_id]
    if any(start < other_end and other_start < end for other_start, other_end in occupied):
        raise SystemExit(f"mention overlaps an existing span: {surface} at L{source_line}")
    mention_id = f"m-chp15-p372-querini-{len(planned_mentions) + 1:04d}"
    if mention_id in mention_by_id:
        raise SystemExit(f"mention ID already exists: {mention_id}")
    planned_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })
    return mention_id


mention_specs = [
    ("cand-8450", "Doge", BODY, 86, ""),
    ("cand-2133", "Renier", BODY, 86, ""),
    ("cand-2075", "Querini", BODY, 86, ""),
    ("cand-10586", "the bust", BODY, 86, ""),
    ("cand-10595", "Altar of\nFuries", BODY, 86, ""),
    ("cand-0086", "his garden", BODY, 87, "Contextual reference to the Alticchiero garden described on the preceding pages."),
    ("cand-1487", "Scipione Maffei", BODY, 87, ""),
    ("cand-2816", "Winckelmann", BODY, 87, ""),
    ("cand-2075", "Querini", BODY, 88, ""),
    ("cand-2289", "Rousseau", BODY, 88, ""),
    ("cand-10596", "Temple of Pallas", BODY, 88, ""),
    ("cand-0086", "his garden", BODY, 88, "Contextual reference to the Alticchiero garden described on the preceding pages."),
    ("cand-10515", "Brunelli Bonetti, 1951", NOTES, 113, ""),
    ("cand-10586", "the bust", NOTES, 113, ""),
    ("cand-10597", "Museo Civico", NOTES, 113, ""),
    ("cand-1803", "Padua", NOTES, 113, ""),
    ("cand-2075", "Querini", NOTES, 113, ""),
]
for candidate_id, surface, segment_id, source_line, note in mention_specs:
    add_mention(candidate_id, surface, segment_id, source_line, note)


def make_statement(statement_id, segment_id, subject_id, object_id, predicate, start_line, end_line,
                   printed_page, physical_page, claim, speaker, text_layer, qualification,
                   mentioned_ids, quote, relation_candidate=False, **extra_qualifiers):
    qualifiers = {
        "source_line_start": start_line,
        "source_line_end": end_line,
        "printed_page": printed_page,
        "pdf_physical_page": physical_page,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned_ids,
    }
    if relation_candidate:
        qualifiers["relation_candidate"] = True
    qualifiers.update(extra_qualifiers)
    statements.append({
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject_id, "object_candidate_id": object_id,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote, "origin": "book",
        "source_file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
    })


cross = statement_by_id[PREV_STATEMENT]
cross["qualifiers"]["source_line_end"] = 83
cross["qualifiers"]["claim"] = (
    "Haskell says Querini had been closely associated with the potential reformer Paolo Renier and commissioned "
    "Canova to make a bust of him after Renier's successful, though exceedingly corrupt in Haskell's description, "
    "campaign; p.372 continues by specifying that the campaign was to become Doge in 1779."
)
cross["qualifiers"]["qualification"] = (
    "P.372 closes the sentence and specifies the campaign's aim and year in a separate statement. "
    "'Exceedingly corrupt' is Haskell's characterization, not an independently established fact."
)
cross["qualifiers"]["mentioned_candidate_ids"] = ["cand-2075", "cand-2133", "cand-0532", "cand-10586"]
cross["qualifiers"]["predicate_status"] = "complete"
cross["qualifiers"]["cross_reference_text"] = "P.371 L83 ends with 'campaign'; p.372 L86 completes it with 'to become Doge in 1779.'"
cross["qualifiers"]["cross_reference_text_pending"] = False
cross["qualifiers"]["cross_reference_statement_ids"] = ["st-chp15-p372-renier-became-doge-1779"]

body86 = source_lines[85]
body87 = source_lines[86]
body88 = source_lines[87]
note113 = source_lines[112]
note_ids = [
    "st-chp15-p372-note1-cites-brunelli-bonetti-1951",
    "st-chp15-p372-note1-bust-at-museo-civico-padua",
    "st-chp15-p372-note1-suggested-servants-lavatories",
]
footnote_link = {
    "footnote_marker": "1", "footnote_segment": NOTES, "footnote_line_range": "L113-L113",
    "footnote_text_pending": False, "footnote_body_link_status": "linked",
    "footnote_body_line_range": "L87", "footnote_note_statement_ids": note_ids,
    "footnote_link_note": "Note 1 reports the likely surviving bust and an unattributed suggestion about its later location.",
}

make_statement(
    "st-chp15-p372-renier-became-doge-1779", BODY, "cand-2133", "cand-8450",
    "became_doge_of_venice_in_1779", 86, 86, 372, 12,
    "Haskell says Paolo Renier's successful campaign was to become Doge in 1779.",
    "Haskell", "authorial report",
    "This closes the p.371 sentence about Querini commissioning Canova's bust; no independent verification is made.",
    ["cand-2133", "cand-8450"], body86.split(". When, later", 1)[0] + ".",
    relation_candidate=True,
)
make_statement(
    "st-chp15-p372-renier-compromised-with-opposing-forces", BODY, "cand-2133", None,
    "later_compromised_with_forces_he_had_once_attacked", 86, 86, 372, 12,
    "Haskell says that later Renier compromised with forces he had once attacked.",
    "Haskell", "authorial report",
    "The forces and political circumstances are not further identified in this passage.",
    ["cand-2133"], body86,
)
make_statement(
    "st-chp15-p372-querini-threw-renier-bust-at-furies-altar", BODY, "cand-2075", "cand-10586",
    "flung_renier_bust_against_altar_of_furies_after_renier_compromise", 86, 87, 372, 12,
    "Haskell says Querini, in rage and disappointment after Renier's compromise, flung the bust against the Altar of Furies in his garden.",
    "Haskell", "authorial report",
    "The altar is identified by name, but the passage gives no date for this episode. The garden is linked contextually to Alticchiero.",
    ["cand-2075", "cand-2133", "cand-10586", "cand-10595", "cand-0086"], body86 + "\n" + body87,
    relation_candidate=True, **footnote_link,
)
make_statement(
    "st-chp15-p372-querini-pagan-shrines-personal-significance", BODY, "cand-2075", None,
    "pagan_shrines_and_temples_had_personal_significance_to_querini", 87, 87, 372, 12,
    "Haskell says pagan shrines and temples had genuine significance for Querini, although he allows that this might have been sentimental or romantic, unlike their significance for most scholars and antiquarians of his age.",
    "Haskell", "authorial interpretation",
    "This is Haskell's interpretation of Querini's relation to pagan antiquity; it does not establish Querini's formal religious beliefs.",
    ["cand-2075"], body87,
)
make_statement(
    "st-chp15-p372-maffei-collected-sculpture-and-recorded-past", BODY, "cand-1487", None,
    "collected_antique_sculpture_and_recorded_evidence_of_the_past", 87, 87, 372, 12,
    "Haskell says Scipione Maffei, in an earlier generation, also collected antique sculpture and lovingly recorded evidence of the past.",
    "Haskell", "authorial comparison",
    "The comparison is Haskell's; this passage does not specify particular objects collected by Maffei.",
    ["cand-1487"], body87,
)
make_statement(
    "st-chp15-p372-querini-distinguished-from-maffei", BODY, "cand-2075", "cand-1487",
    "distinguished_from_maffei_by_personal_significance_of_pagan_antiquity", 87, 87, 372, 12,
    "Haskell says Querini's activities were distinguished from those of Maffei by the real significance ancient pagan shrines and temples held for Querini.",
    "Haskell", "authorial interpretation",
    "This is Haskell's comparison and should not be converted into an objective difference without further evidence.",
    ["cand-2075", "cand-1487"], body87,
)
make_statement(
    "st-chp15-p372-querini-returned-to-ideal-past-compared-with-winckelmann", BODY, "cand-2075", "cand-2816",
    "returned_to_ideal_past_after_political_retirement_in_comparison_with_winckelmann", 87, 88, 372, 12,
    "Haskell says that after his baffled retirement from contemporary politics and insoluble problems, Querini returned to an ideal world of the past, comparing this return with Winckelmann while judging Querini to have far less intellectual or critical insight.",
    "Haskell", "authorial interpretation",
    "Both the comparison with Winckelmann and the assessment of Querini's intellectual or critical insight are Haskell's evaluations.",
    ["cand-2075", "cand-2816"], body87 + "\n" + body88,
)
make_statement(
    "st-chp15-p372-rousseau-influence-on-querini-view-of-past", BODY, "cand-2075", "cand-2289",
    "view_of_the_past_bound_up_with_rousseau", 88, 88, 372, 12,
    "Haskell says Querini's view of the past was inextricably bound up with the influence of Rousseau.",
    "Haskell", "authorial interpretation",
    "The statement records Haskell's interpretation, not an independently established causal account.",
    ["cand-2075", "cand-2289"], body88,
    relation_candidate=True,
)
make_statement(
    "st-chp15-p372-querini-heart-buried-at-temple-of-pallas", BODY, "cand-2075", "cand-10596",
    "heart_buried_in_temple_of_pallas_at_querinis_request_in_1796", 88, 88, 372, 12,
    "Haskell says that when Querini died in 1796, his heart was buried at his request in the Temple of Pallas in his garden.",
    "Haskell", "authorial report",
    "The claim concerns the burial of Querini's heart, not his whole body; the temple is not independently identified here.",
    ["cand-2075", "cand-10596", "cand-0086"], body88,
    relation_candidate=True,
)

note_shared = {
    "footnote_marker": "1", "footnote_segment": NOTES, "footnote_line_range": "L113-L113",
    "footnote_text_pending": False, "footnote_body_link_status": "linked",
    "footnote_body_line_range": "L87", "footnote_note_statement_ids": note_ids,
    "footnote_link_note": "Note 1 follows Haskell's account of Querini throwing the bust against the Altar of Furies.",
}
make_statement(
    note_ids[0], NOTES, None, "cand-10515", "note_cites_brunelli_bonetti_1951", 113, 113, 372, 12,
    "Haskell's note cites Brunelli Bonetti, 1951.", "Haskell's note", "bibliographic citation",
    "The cited work is not independently consulted in this pass.", ["cand-10515"], note113,
    cited_source_independently_consulted=False, **note_shared,
)
make_statement(
    note_ids[1], NOTES, "cand-10586", "cand-10597", "likely_renier_bust_survives_at_museo_civico_padua", 113, 113, 372, 12,
    "Haskell's note says that what must be the bust survives in terracotta at the Museo Civico in Padua.",
    "Haskell's note", "secondary report",
    "'What must be the bust' marks Haskell's tentative identification with Canova's Renier bust; museum identity and custody are not independently verified.",
    ["cand-2075", "cand-10586", "cand-10597", "cand-1803"], note113,
    relation_candidate=True, **note_shared,
)
make_statement(
    note_ids[2], NOTES, "cand-2075", "cand-10586", "unattributed_suggestion_querini_kept_bust_in_servants_lavatories", 113, 113, 372, 12,
    "Haskell's note reports an unnamed suggestion that Querini kept the bust in the servants' lavatories, reasoning that it shows no obvious signs of irreparable damage.",
    "Haskell's note reporting an unnamed suggestion", "reported speculation",
    "The proposer is not identified and the claim is explicitly presented as a suggestion, not an established fact.",
    ["cand-2075", "cand-10586"], note113,
    relation_candidate=True, **note_shared,
)

coverage_by_id[BODY_PREV]["migration_status"] = "complete"
coverage_by_id[BODY_PREV]["note"] = (
    "Printed p.371 checked against CHP-15.pdf physical p.11. The final Renier/Canova sentence is closed by p.372 L86; "
    "the p.371 body and notes 1-2 at L111-112 are fully migrated. Print corrections remain in S2 only; S0 is unchanged."
)
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L86-88",
    "note": "Printed p.372 checked against CHP-15.pdf physical p.12. Closes the p.371 Renier/Canova sentence; records Querini's response to Renier's compromise, Haskell's comparisons with Maffei and Winckelmann, the Rousseau interpretation, and the requested burial of Querini's heart.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L91-113",
    "note": "Consolidated notes through p.372 note 1 are migrated: p.365 L91-92, p.367 L93-96, p.368 L97-104, p.369 L105-108, p.370 L109-110, p.371 L111-112, and p.372 L113.",
})

new_statement_ids = [row["statement_id"] for row in statements if row.get("statement_id", "").startswith("st-chp15-p372-")]
if not args.apply:
    print(json.dumps({
        "mode": "dry-run", "new_candidates": len(new_candidates), "new_mentions": len(planned_mentions),
        "new_statements": len(new_statement_ids), "closed_cross_page_statement": PREV_STATEMENT,
        "coverage": {BODY_PREV: "complete", BODY: "complete", NOTES: "complete"},
        "new_candidate_ids": [row[0] for row in new_candidates],
        "new_statement_ids": new_statement_ids,
    }, ensure_ascii=False))
    raise SystemExit(0)

for path in (candidate_path, mention_path, statement_path, coverage_path):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup.name}")
    shutil.copy2(path, backup)

mentions.extend(planned_mentions)
write_csv(candidate_path, candidate_fields, candidates)
write_csv(mention_path, mention_fields, mentions)
write_jsonl(statement_path, statements)
write_csv(coverage_path, coverage_fields, coverage)
print(json.dumps({
    "mode": "applied", "new_candidates": len(new_candidates), "new_mentions": len(planned_mentions),
    "new_statements": len(new_statement_ids),
    "backups": [path.name + BACKUP_SUFFIX for path in (candidate_path, mention_path, statement_path, coverage_path)],
}, ensure_ascii=False))
