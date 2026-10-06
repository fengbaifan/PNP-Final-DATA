#!/usr/bin/env python3
"""Controlled S2 migration for the Appendix 6 continuation and Appendix 7, p.395."""

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "19_CHP-19Appendix.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-19Appendix.pdf"
EXPECTED_HASHES = {
    SOURCE: "725dc16a2983bec379ce2a8b608542ab3defe348d2b2f2a336632ac4905388f1",
    PDF: "2a1c29e6c2864527482d231a85c4252e55524b436ae4dff5b0d55d9d5a67a9eb",
}
P394 = "chp-19:19_CHP-19Appendix:l157-183"
P395 = "chp-19:19_CHP-19Appendix:l185-208"
P395_FOOTNOTE = "chp-19:19_CHP-19Appendix:l210-211"
CH17_BODY = "chp-17:17_CHP-17_sec_i:l8-20"
CH17_NOTES = "chp-17:17_CHP-17_sec_i:l26-35"
BACKUP_SUFFIX = ".bak-s2-chp19-p395-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed S2 migration")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


for path, expected in EXPECTED_HASHES.items():
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f"registered input changed: {path.relative_to(ROOT)} ({actual})")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = [
    json.loads(line)
    for line in statement_path.read_text(encoding="utf-8-sig").splitlines()
    if line.strip()
]
coverage_fields, coverage = read_csv(coverage_path)
segments = [
    json.loads(line)
    for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
    if line.strip()
]
segment_by_id = {row["segment_id"]: row for row in segments}
candidate_by_id = {row["candidate_id"]: row for row in candidates}
coverage_by_id = {row["segment_id"]: row for row in coverage}
statement_by_id = {row["statement_id"]: row for row in statements}

if any(seg not in segment_by_id or seg not in coverage_by_id for seg in (P394, P395, P395_FOOTNOTE)):
    raise SystemExit("missing S0 or S2 row for p.394–395 sequence")
if (coverage_by_id[P394]["disposition"], coverage_by_id[P394]["migration_status"]) != (
    "reviewed", "complete"
):
    raise SystemExit(f"p.394 must be reviewed/complete before continuing: {coverage_by_id[P394]}")
if (coverage_by_id[P395]["disposition"], coverage_by_id[P395]["migration_status"]) != (
    "queued", "pending"
):
    raise SystemExit(f"p.395 should be queued/pending before migration: {coverage_by_id[P395]}")
if (coverage_by_id[P395_FOOTNOTE]["disposition"], coverage_by_id[P395_FOOTNOTE]["migration_status"]) != (
    "queued", "pending"
):
    raise SystemExit(f"p.395 footnote segment should remain queued/pending: {coverage_by_id[P395_FOOTNOTE]}")

segment = segment_by_id[P395]
if segment["sha256"] != "a5cd45b0170686ae85bb3860f458c495375188f1e32d08a8ec4af4b8ccc4f60a":
    raise SystemExit("registered p.395 S0 hash changed")
if segment["asset_sha256"] != EXPECTED_HASHES[SOURCE]:
    raise SystemExit("p.395 source asset hash is inconsistent")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
text395 = "\n".join(source_lines[segment["line_start"] - 1 : segment["line_end"]])
if hashlib.sha256(text395.encode("utf-8")).hexdigest() != segment["sha256"]:
    raise SystemExit("p.395 S0 segment hash mismatch")
line_offset = {}
offset = 0
for line_number in range(segment["line_start"], segment["line_end"] + 1):
    line_offset[line_number] = offset
    offset += len(source_lines[line_number - 1]) + 1


def quote(first_line, last_line):
    return "\n".join(source_lines[first_line - 1 : last_line])


new_candidate_specs = [
    {
        "candidate_id": "cand-10844",
        "canonical_name": "Duke Cosimo named in Andrea Memmo's research note (identity unresolved)",
        "suggested_type": "person",
        "source_line": 187,
        "detail": "The note asks readers to look for orders, chapters, and privileges granted by a Duke Cosimo to painters. It does not give a numeral or enough context here to resolve which Cosimo; no specific grant is asserted as verified.",
    },
    {
        "candidate_id": "cand-10845",
        "canonical_name": "Carlo VI, King of France (as named in Memmo's note)",
        "suggested_type": "person",
        "source_line": 194,
        "detail": "Named in a statement that he granted painters certain fiscal and housing exemptions. The citation to Monier p.179 is not independently consulted; the claim is preserved as a statement in the preparatory note, not externally verified here.",
    },
    {
        "candidate_id": "cand-10846",
        "canonical_name": "Monier, p.179 (citation locator in Memmo's note)",
        "suggested_type": "archive",
        "source_line": 194,
        "detail": "Abbreviated citation locator attached to Memmo's note about privileges granted to painters by Carlo VI of France. No title, edition, or full bibliographical identity is supplied; the cited page was not consulted.",
    },
    {
        "candidate_id": "cand-10847",
        "canonical_name": "Sculptors as a professional group in Memmo's guild-statute queries",
        "suggested_type": "term",
        "source_line": 192,
        "detail": "Sculptors are listed with painters and architects in a query about guild statutes; no individual sculptor or particular guild is named.",
    },
    {
        "candidate_id": "cand-10848",
        "canonical_name": "Bronze casters as a professional group in Memmo's guild-statute queries",
        "suggested_type": "term",
        "source_line": 193,
        "detail": "Bronze casters are one of the trades whose statutes and access to schools or communities Memmo proposes to investigate; no individual caster or community is named.",
    },
    {
        "candidate_id": "cand-10849",
        "canonical_name": "Girolamo Manfrin to Pietro Edwards, 3 December 1793 (letter about forming Manfrin's picture gallery)",
        "suggested_type": "archive",
        "source_line": 197,
        "detail": "Letter printed in full in Appendix 7 and located by Haskell in Biblioteca Correr, Venice—Epistolario Moschini. Chapter 17 p.380 note 6 identifies the same letter. The manuscript was not independently consulted.",
    },
]
existing_keys = {
    (
        (row.get("canonical_name") or "").strip().casefold(),
        (row.get("suggested_type") or "").strip().casefold(),
    )
    for row in candidates
}
for spec in new_candidate_specs:
    cid = spec["candidate_id"]
    name = spec["canonical_name"]
    kind = spec["suggested_type"]
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {cid}")
    key = (name.strip().casefold(), kind.casefold())
    if key in existing_keys:
        raise SystemExit(f"candidate natural key already exists: {name} / {kind}")
    row = {
        "candidate_id": cid,
        "index_entry_id": "",
        "canonical_name": name,
        "index_page_range": "",
        "suggested_type": kind,
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": spec["detail"],
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{P395}#L{spec['source_line']}",
    }
    candidates.append(row)
    candidate_by_id[cid] = row
    existing_keys.add(key)

mention_specs = [
    ("cand-0005", "n.A.", 186, 186, "Abbreviation is retained; context from p.394 and p.330 suggests 'our Academy', but expansion remains provisional.", 0),
    ("cand-10844", "Duca Cosimo", 187, 187, "Duke named in a research instruction; identity is not resolved from this wording.", 0),
    ("cand-10839", "Pittori", 187, 187, "Painters named as recipients of privileges Memmo proposes to look up.", 0),
    ("cand-2702", "Vasari", 187, 187, "Vasari is marked 'lett.' (read) in the note; no external edition/page is specified here.", 0),
    ("cand-1699", "Montorsoli", 188, 188, "Artist whose life in Vasari is marked 'Letta.' (read) in the note.", 0),
    ("cand-9864", "vita del Montorsoli in Vasari", 188, 188, "Work referred to in the reading instruction; edition and page are not given.", 0),
    ("cand-10836", "Acc.a di Parigi", 189, 189, "Paris Academy abbreviation; its secretary's identity is not supplied.", 0),
    ("cand-4653", "Parigi", 189, 189, "Paris in the Academy secretary query; nested in the institution mention.", 0),
    ("cand-10836", "Diretore", 190, 190, "The director is queried after the Paris Academy secretary; the referent is kept with that institution, but no person is named.", 0),
    ("cand-3398", "Bologna", 191, 191, "City where the note asks whether the secretary is alive; secretary is unnamed.", 0),
    ("cand-10839", "Pittori", 192, 192, "Painters named in the proposed search for guild statutes.", 0),
    ("cand-10847", "Scult:", 192, 192, "Printed abbreviation for sculptors in the statute query; retained as printed.", 0),
    ("cand-10838", "Archit.", 192, 192, "Printed abbreviation for architects in the statute query; retained as printed.", 0),
    ("cand-9854", "intagliatori in Rame", 193, 193, "Copper engravers named among the trades whose statutes are to be sought.", 0),
    ("cand-10848", "gittatori in bronzo", 193, 193, "Bronze casters named among the trades whose statutes are to be sought.", 0),
    ("cand-0005", "dell’Acc.a", 193, 193, "The Academy whose younger members might be given privileges; exact referent remains contextual.", 0),
    ("cand-10845", "Carlo VI Re di Francia", 194, 194, "Name and title as stated in the note; the accompanying exemption claim is not independently verified.", 0),
    ("cand-10839", "Pittori", 194, 194, "Painters named as recipients of the exemptions attributed in the note to Carlo VI.", 0),
    ("cand-10846", "Monier 179", 194, 194, "Citation locator as printed; source and page were not independently consulted.", 0),
    ("cand-9867", "belle Arti", 195, 195, "Arts described in Memmo's normative passage as liberal; retain this as the note's argument.", 0),
    ("cand-9867", "liberali", 195, 195, "Liberal arts term in the note's explanation; original spelling is retained.", 0),
    ("cand-1512", "Girolamo Manfrin", 197, 197, "Sender named in the Appendix 7 heading; p.395 index subentry cand-1515 points to this letter.", 0),
    ("cand-0965", "Pietro Edwards", 197, 197, "Recipient named in the Appendix 7 heading.", 0),
    ("cand-10849", "Letter from Girolamo Manfrin to Pietro Edwards of 3 December 1793", 197, 197, "Letter identified in the appendix heading; exact manuscript locator is supplied in the same sentence.", 0),
    ("cand-1513", "his picture gallery", 197, 197, "Manfrin's gallery, the subject of the letter; the candidate reuses the index subentry for his collection.", 0),
    ("cand-8262", "Biblioteca Correr", 197, 197, "Repository named for the letter; the archival manuscript was not consulted.", 0),
    ("cand-2719", "Vertice", 197, 197, "Raw OCR; the page image reads Venice.", 0),
    ("cand-10605", "Epistolario Moschini", 197, 197, "Manuscript collection named as the source of the letter; exact individual shelfmark is not supplied.", 0),
    ("cand-1513", "mia Galleria", 199, 199, "Manfrin's own gallery named in his letter.", 0),
    ("cand-1670", "Gio. Batta Mingardi", 200, 200, "Source's abbreviated form; the index candidate expands this as Giovanni Battista Mingardi, pending S3.", 0),
    ("cand-1670", "Mingardi", 201, 201, "Mingardi's knowledge is praised in the letter; this does not prove a completed selection.", 0),
    ("cand-0965", "Pietro Edwards", 207, 207, "Recipient named in the letter's address.", 0),
    ("cand-1512", "Girolamo Manfrin", 207, 207, "Sender named in the letter's signature; linked to the p.395 index subentry cand-1515.", 0),
    ("cand-2719", "Venezia", 208, 208, "Place stated at the end of the address.", 0),
]

new_mentions = []
mention_ids = {row["mention_id"] for row in mentions}
for ordinal, (cid, surface, first_line, last_line, note, occurrence) in enumerate(mention_specs, start=1):
    mid = f"m-chp19-p395-{ordinal:03d}"
    if mid in mention_ids:
        raise SystemExit(f"mention ID already exists: {mid}")
    candidate = candidate_by_id.get(cid)
    if not candidate or candidate.get("status") != "open":
        raise SystemExit(f"mention targets missing or closed candidate: {cid}")
    lower = line_offset[first_line]
    upper = line_offset[last_line] + len(source_lines[last_line - 1])
    cursor = lower
    found = -1
    for _ in range(occurrence + 1):
        found = text395.find(surface, cursor, upper)
        if found < 0:
            raise SystemExit(
                f"surface not found in p.395 lines {first_line}-{last_line}: {surface!r}"
            )
        cursor = found + 1
    end = found + len(surface)
    if text395[found:end] != surface:
        raise SystemExit(f"span mismatch for {mid}")
    new_mentions.append({
        "mention_id": mid,
        "segment_id": P395,
        "candidate_id": cid,
        "surface_form": surface,
        "start_char": str(found),
        "end_char": str(end),
        "note": note,
    })
    mention_ids.add(mid)

intervals = sorted(
    (int(row["start_char"]), int(row["end_char"]), row["mention_id"])
    for row in [*mentions, *new_mentions]
    if row["segment_id"] == P395
)
for index, left in enumerate(intervals):
    for right in intervals[index + 1 :]:
        if right[0] >= left[1]:
            break
        exact_duplicate = left[:2] == right[:2]
        strictly_nested = (
            (left[0] <= right[0] and right[1] <= left[1])
            or (right[0] <= left[0] and left[1] <= right[1])
        )
        if exact_duplicate or not strictly_nested:
            raise SystemExit(
                f"duplicate or crossing p.395 mention spans: {left[2]} and {right[2]}"
            )


def statement(statement_id, first, last, subject, object_, predicate, claim, speaker, text_layer,
              qualification, candidate_ids, date=None, relation=False, **extra):
    qualifiers = {
        "source_line_start": first,
        "source_line_end": last,
        "printed_page": 395,
        "pdf_physical_page": 10,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": candidate_ids,
        "relation_candidate": relation,
        "cited_material_not_independently_consulted": True,
    }
    if date:
        qualifiers["date"] = date
    qualifiers.update(extra)
    return {
        "statement_id": statement_id,
        "segment_id": P395,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote(first, last),
        "source_file": "02-sources/02-Markdown/19_CHP-19Appendix.md",
        "origin": "book",
    }


new_statements = [
    statement(
        "st-chp19-p395-memmo-patron-saint-and-vasari-reading", 186, 188, "cand-1642", None,
        "memmo_listed_academy_patron_saint_and_cosimo_privileges_as_research_topics_and_marked_vasari_read",
        "The continuing note asks which saint protects the abbreviated 'n.A.', directs the reader to seek orders, chapters, and privileges granted by Duke Cosimo to painters, marks Vasari as read, and marks the life of Montorsoli in Vasari as read.",
        "Andrea Memmo as transcribed by Haskell", "transcribed working queries and reading marks",
        "The note's tasks and 'read' marks are recorded as written; they do not independently verify the Academy's patron saint or any privilege granted by Cosimo. 'n.A.' is left abbreviated, with its likely Academy referent linked to p.394 and p.330 context.",
        ["cand-1642", "cand-9857", "cand-0005", "cand-10844", "cand-10839", "cand-2702", "cand-1699", "cand-9864"],
        relation=True,
        cross_reference_segments=[P394, "chp-10:10_CHP-10_sec_ii:l258-267"],
        cross_reference_statement_ids=["st-chp19-p394-memmo-academy-emblem-name-query", "st-chp10-p330-memmo-vasari-academy-queries"],
    ),
    statement(
        "st-chp19-p395-academy-secretaries-status", 189, 191, "cand-1642", None,
        "memmo_noted_that_paris_academy_officials_and_bologna_secretary_were_in_life",
        "The note asks whether the secretary and director of the Paris Academy are alive and records 'in vita'; it asks the same about the secretary in Bologna and records 'e in vita'.",
        "Andrea Memmo as transcribed by Haskell", "transcribed query with answer marks",
        "The officials are unnamed, the date of the status note is uncertain, and the 'in vita' entries are statements in the document rather than independently checked biographical facts.",
        ["cand-1642", "cand-9857", "cand-10836", "cand-4653", "cand-3398"],
        cross_reference_segments=[P394],
        cross_reference_statement_ids=["st-chp19-p394-memmo-paris-academy-privileges-and-teaching"],
    ),
    statement(
        "st-chp19-p395-memmo-guild-statutes-and-academy-access", 192, 193, "cand-1642", None,
        "memmo_proposed_researching_trade_statutes_and_academy_youth_access_to_schools_or_communities",
        "The note directs the reader to seek statutes for painters, sculptors, architects, copper engravers, bronze casters, and other trades, and asks how to grant Academy youths privileges to enter the relevant schools or communities.",
        "Andrea Memmo as transcribed by Haskell", "transcribed working query and proposal",
        "No particular guild, school, or community is identified, and the note does not say that access privileges were enacted. Occupational groups are retained without inventing named organizations.",
        ["cand-1642", "cand-9857", "cand-10839", "cand-10847", "cand-10838", "cand-9854", "cand-10848", "cand-0005"],
        relation=True,
        cross_reference_segments=[P394],
        cross_reference_statement_ids=["st-chp19-p394-memmo-professional-tax-comparisons"],
    ),
    statement(
        "st-chp19-p395-charles-vi-painters-exemptions", 194, 194, "cand-10845", "cand-10839",
        "memmo_note_attributed_fiscal_and_housing_exemptions_for_painters_to_charles_vi_of_france",
        "The note states that Carlo VI, King of France, granted painters exemptions from taxes, duties, subsidies, and housing obligations, and cites Monier p.179.",
        "Andrea Memmo as transcribed by Haskell", "transcribed historical assertion with citation",
        "This is a direct assertion in the preparatory note, not an independently verified legal or historical fact. The Monier citation is incomplete and was not consulted.",
        ["cand-1642", "cand-9857", "cand-10845", "cand-10839", "cand-10846"],
        relation=True,
    ),
    statement(
        "st-chp19-p395-memmo-liberal-arts-normative-argument", 195, 195, "cand-1642", "cand-9867",
        "memmo_argued_that_speculative_painting_should_be_free_from_practical_subjection",
        "The note says painting's speculative part should be practised freely and nobly, that genius should not be subjected in the practice of the fine arts, and that this is why they were called liberal.",
        "Andrea Memmo as transcribed by Haskell", "transcribed normative argument",
        "This records Memmo's argument in the note, not a description of an enacted legal status. The printed spellings 'denono' and 'prattica' are preserved unless separately corrected by page-image evidence.",
        ["cand-1642", "cand-9857", "cand-9867", "cand-10839"],
        cross_reference_segments=[P394],
        cross_reference_statement_ids=["st-chp19-p394-memmo-liberal-arts-query"],
    ),
    statement(
        "st-chp19-p395-manfrin-edwards-letter-source", 197, 197, "cand-10849", "cand-10605",
        "appendix_7_identified_the_full_1793_manfrin_edwards_letter_and_its_repository",
        "The Appendix 7 heading identifies a letter from Girolamo Manfrin to Pietro Edwards dated 3 December 1793, concerning the formation of Manfrin's picture gallery, and locates it in Biblioteca Correr, Venice—Epistolario Moschini.",
        "Haskell's appendix heading", "source identification and archival locator",
        "Chapter 17 p.380 note 6 identifies the same letter and says Appendix 7 prints it in full. The manuscript itself was not independently consulted; the appendix transcription is the evidence processed here.",
        ["cand-10849", "cand-1512", "cand-1515", "cand-0965", "cand-1513", "cand-8262", "cand-2719", "cand-10605"],
        date="1793-12-03", relation=True,
        cross_reference_segments=[CH17_BODY, CH17_NOTES],
        cross_reference_statement_ids=["st-chp17-p380-edwards-advised-manfrin", "st-chp17-p380-note6-edwards-letter-source"],
        ocr_corrections=[
            {"source_line": 197, "ocr": "thè", "print": "the", "basis": "CHP-19Appendix.pdf physical page 10."},
            {"source_line": 197, "ocr": "formatioh", "print": "formation", "basis": "CHP-19Appendix.pdf physical page 10."},
            {"source_line": 197, "ocr": "Vertice", "print": "Venice", "basis": "CHP-19Appendix.pdf physical page 10."},
        ],
    ),
    statement(
        "st-chp19-p395-manfrin-selection-criteria-and-experts", 199, 201, "cand-1512", "cand-1513",
        "manfrin_requested_edwards_and_mingardi_select_gallery_pictures_by_expertise_and_merit",
        "Manfrin says he wants good order in choosing pictures for his gallery and wanted Edwards and Gio. Batta Mingardi, whom he describes as experienced and famous in painting, to choose, identify, and exclude pictures as they thought fit without regard to cost; he wanted only works of real merit and 'assoluto' in his collection. He thanks Edwards for agreeing and says he trusts Edwards's erudition and Mingardi's knowledge.",
        "Girolamo Manfrin in the letter transcribed by Haskell", "quoted archival letter",
        "This is the Italian letter printed in Appendix 7 and corresponds to the English extract summarized at p.380. It expresses a request and selection criterion, not proof that any particular picture was selected, bought, or admitted to the gallery. The printed phrase 'reale merito ed assoluto' is preserved without supplying an omitted noun.",
        ["cand-1512", "cand-1515", "cand-0965", "cand-1670", "cand-1513", "cand-10849"],
        relation=True,
        cross_reference_segments=[CH17_BODY],
        cross_reference_statement_ids=["st-chp17-p380-manfrin-delegated-picture-selection"],
        ocr_corrections=[
            {"source_line": 199, "ocr": "bramare_", "print": "bramare", "basis": "CHP-19Appendix.pdf physical page 10."}
        ],
    ),
    statement(
        "st-chp19-p395-manfrin-confidential-judgment-condition", 202, 203, "cand-1512", "cand-0965",
        "manfrin_accepted_private_confidentiality_for_edwards_picture_rejections",
        "Manfrin tells Edwards not to hesitate to judge severely and says exclusions will not cause displeasure, differences, or enmity; he accepts the condition that Edwards never publish his disapproval, which will serve only as a secret rule and private guide for Manfrin's decisions.",
        "Girolamo Manfrin in the letter transcribed by Haskell", "quoted archival letter and confidentiality term",
        "This is a stated condition and promise in the letter, not proof that all objections were in fact kept private. The p.380 English extract summarizes the same arrangement; this statement links the full Italian text.",
        ["cand-1512", "cand-1515", "cand-0965", "cand-1670", "cand-1513", "cand-10849"],
        relation=True,
        cross_reference_segments=[CH17_BODY],
        cross_reference_statement_ids=["st-chp17-p380-manfrin-kept-experts-objections-private"],
        ocr_corrections=[
            {"source_line": 202, "ocr": "diferenze", "print": "differenze", "basis": "CHP-19Appendix.pdf physical page 10."}
        ],
    ),
    statement(
        "st-chp19-p395-manfrin-letter-closure-and-signature", 204, 208, "cand-1512", "cand-0965",
        "manfrin_reaffirmed_his_estimate_and_signed_the_1793_letter_from_venice",
        "Manfrin reiterates his esteem for Edwards and says he will later show gratitude; the letter closes from his house on 3 December 1793, is addressed to Pietro Edwards in Venice, and is signed Girolamo Manfrin.",
        "Girolamo Manfrin in the letter transcribed by Haskell", "quoted archival letter closing and signature",
        "The date, place, addressee, and signature are read from the printed transcription. The original letter was not independently consulted.",
        ["cand-1512", "cand-1515", "cand-0965", "cand-2719", "cand-10849"],
        date="1793-12-03", relation=True,
    ),
]

existing_statement_ids = {row["statement_id"] for row in statements}
for row in new_statements:
    sid = row["statement_id"]
    if sid in existing_statement_ids:
        raise SystemExit(f"statement ID already exists: {sid}")
    existing_statement_ids.add(sid)
    if row["original_quote"] not in text395:
        raise SystemExit(f"statement quote not contained in p.395 segment: {sid}")
    for cid in row["qualifiers"].get("mentioned_candidate_ids", []):
        if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
            raise SystemExit(f"statement {sid} references unavailable candidate {cid}")
    for ref_id in row["qualifiers"].get("cross_reference_statement_ids", []):
        if ref_id not in statement_by_id:
            raise SystemExit(f"statement {sid} references missing statement {ref_id}")

statements.extend(new_statements)
mentions.extend(new_mentions)
coverage_by_id[P395]["disposition"] = "reviewed"
coverage_by_id[P395]["migration_status"] = "complete"
coverage_by_id[P395]["source_line_ranges"] = "L186-208"
coverage_by_id[P395]["note"] = (
    "Printed p.395 (PDF physical page 10) read against the page image. Completes the remaining Appendix 6 notes "
    "and transcribes the Appendix 7 Manfrin-to-Edwards letter. Queries, reading marks, the cited Charles VI "
    "exemption claim, and the letter's selection/confidentiality terms are distinguished; the letter cross-links "
    "to Chapter 17 p.380 and its note 6. Named individuals and institutions are mapped to existing candidates where "
    "available; unresolved Cosimo, Paris Academy, and occupational group candidates remain open. Page-image corrections "
    "are recorded on statements; cited works and the archival manuscript were not independently consulted."
)
coverage_by_id[P395_FOOTNOTE]["disposition"] = "excluded"
coverage_by_id[P395_FOOTNOTE]["migration_status"] = "complete"
coverage_by_id[P395_FOOTNOTE]["source_line_ranges"] = "L210-211"
coverage_by_id[P395_FOOTNOTE]["note"] = (
    "Excluded as a duplicate OCR extraction of the Giacinto Brandi receipt beginning on printed p.386. "
    "The canonical receipt was already semantically processed from the derived visual transcription "
    "segment `chp-19:19_CHP-19Appendix_p386_receipt_visual-transcription:l4-4` and its continuation "
    "in `chp-19:19_CHP-19Appendix:l22-41`; this appended `Footnotes` block has no separate printed-page anchor."
)

files_to_backup = [candidate_path, mention_path, statement_path, coverage_path]
if args.apply:
    for path in files_to_backup:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists; refusing overwrite: {backup.name}")
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions)
    write_jsonl(statement_path, statements)
    write_csv(coverage_path, coverage_fields, coverage)
    print("applied p.395 S2 migration; backups:")
    for path in files_to_backup:
        print(f"  {path.name}{BACKUP_SUFFIX}")
else:
    print("DRY RUN: no files written")
    print(f"new candidates: {len(new_candidate_specs)}; mentions: {len(new_mentions)}; statements: {len(new_statements)}")
    print("p.395: queued/pending -> reviewed/complete; duplicate receipt OCR l.210-211: queued/pending -> excluded/complete")
    print("linked the Appendix 7 original-language letter to the Chapter 17 p.380 summary and source note")
    print("preserved Memmo's questions, his cited exemption assertion, and the letter's requests without treating them as completed actions")
