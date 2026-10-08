#!/usr/bin/env python3
"""Semantically adjudicate Chapter 9 candidate-surface prompts.

The scanner is a locator only. This locked writer checks the full prompt
partition, exact source spans, candidate foreign keys, mention overlap, and
statement preconditions before writing reviewed S2 decisions.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"

sys.path.insert(0, str(ROOT / "scripts"))
import audit_s2_candidate_surfaces as surface_audit

EXPECTED_HASHES = {
    "04-knowledge/tables/entity-candidates.csv": "64b00d3499f13c8340fa9a55250ecaec2f46326197d5eb169ec49615a789691c",
    "04-knowledge/tables/mentions.csv": "c9b56e91864305d3f87436bc685a38fac94c0f49ba240638c7ed745802bae551",
    "04-knowledge/tables/book-statements.jsonl": "ece9290d813a686b35da105ba17d4690a561f88f7534cc63c1026193363e2d20",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/s2-coverage.csv": "84f8497a7ce0100f4785acd8bf8ed88bb4c69fe5254cd89d172577b0400eb6c1",
    "scripts/audit_s2_candidate_surfaces.py": "130b53da86d940daad454079960415ac5e7043e0b71239370b66226158cd1ee2",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "01-domain/stage-artifact-schema.md": "929b8a55f92103de962e8bd509d02d883683b0eea3a9ffe307e5de8229a86abe",
    "02-sources/02-Markdown/09_CHP-9_intro.md": "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3",
    "02-sources/02-Markdown/09_CHP-9_intro_notes_p260_visual-transcription.md": "7b2cec96604bd1dad6609e67c9f94d771b36b4ec975cf05f410f711ffceab95d",
    "02-sources/02-Markdown/09_CHP-9_intro_notes_p262_visual-transcription.md": "19d871e4a76f86368b71b4f11528fab11181863a2361ed2b8d46407408a73e8f",
    "02-sources/02-Markdown/09_CHP-9_intro_plates_visual-transcription.md": "1e37527d1115bf27159527ba08d832f30a2ac551b41b5e954c7de93f72a88857",
    "02-sources/02-Markdown/09_CHP-9_sec_ii.md": "67d60205c246f2f126433bab8a22ddb29ed73e2af2fed5fff5978c319b3ee923",
}


def accepted(
    prompt_index: int,
    candidate_id: str,
    note: str,
    mention_surface: str | None = None,
) -> dict[str, object]:
    return {
        "prompt_index": prompt_index,
        "candidate_id": candidate_id,
        "mention_surface": mention_surface,
        "note": note,
    }


ACCEPTED = [
    accepted(2, "cand-3398", "Bologna is the city in the Manin passage; reuse the candidate already linked to the corresponding Ch.9 statement, leaving S3 identity reconciliation open."),
    accepted(3, "cand-2719", "Venice is the named city in which the Jesuit church stands; choose the place candidate, not index subentries whose canonical label also says Venice."),
    accepted(4, "cand-8426", "The memoirs are the source cited for the banquet report; use the Ch.9 volume-and-page citation locator, not Goldoni's memoirs or the unaligned bibliography record."),
    accepted(8, "cand-2719", "Venice is the city contrasted with success abroad; reuse the in-book place candidate."),
    accepted(12, "cand-1059", "The palace is the indexed Foscarini family palace described in this paragraph; the false Pamfili index hit is unrelated."),
    accepted(13, "cand-2719", "Venice is the city whose recovery is invoked in the painting's subject; reuse the in-book place candidate."),
    accepted(16, "cand-3570", "Amateur is used as a social/artistic role for Almorò Pisani; map the exact term without inferring training or professional status."),
    accepted(18, "cand-3571", "Canvas is the painting support Tiepolo had to pay for; it is not a work title."),
    accepted(19, "cand-4288", "Old masters denotes the broad art-historical category in the Grassi comparison."),
    accepted(20, "cand-4288", "Old masters denotes the broad category of works bought by the Giovanelli, not an individual painting."),
    accepted(21, "cand-8201", "The ceiling paintings are located in the Labia palace; the existing palace candidate was created from this chapter's p.250 account."),
    accepted(22, "cand-11493", "Haskell explicitly describes the large multi-medium collection Sagredo amassed; the candidate preserves its unresolved boundary and type."),
    accepted(25, "cand-8575", "The palace at S. Sofia is the unnamed Sagredo residence already recorded from the preceding source sentence."),
    accepted(26, "cand-11493", "The collection is the same Sagredo collection he attempted to preserve after death; distinguish its broad scope from individual works."),
    accepted(27, "cand-11493", "Cochin's account concerns pictures in the same Sagredo collection; the cited volume and pages remain unconsulted."),
    accepted(28, "cand-11493", "The collection planned for dispersal is the broad Sagredo collection described on p.263."),
    accepted(29, "cand-11493", "The collection broken up piecemeal is the same Sagredo collection; retain the source's gradual-disposal wording."),
    accepted(30, "cand-11493", "The inventories are used to assess the same Sagredo collection; do not equate them with individual works or a complete itemized catalogue."),
    accepted(31, "cand-11493", "The family collection includes pictures predating Zaccaria's own additions; its exact boundary remains unresolved."),
    accepted(32, "cand-8602", "The battle scenes are the unidentified Borgognone group already recorded and are explicitly linked to Doge Niccolò in the source."),
    accepted(33, "cand-8575", "The later reference to the palace points back to Sagredo's unnamed S. Sofia residence; do not merge it with Palazzo Sagredo before S3."),
    accepted(35, "cand-11493", "The estimate refers to the Sagredo collection whose prestige is discussed in this paragraph."),
    accepted(36, "cand-8607", "The several drawings recorded in 1743 are the already registered unidentified Tiepolo drawing group."),
    accepted(38, "cand-11493", "The hundreds of works in the note belong to the broad Sagredo collection; individual old-master pictures remain unidentified."),
    accepted(39, "cand-8614", "Cochin's phrase is specifically 'Sagredo palace'; map to the chapter's named Palazzo Sagredo candidate while preserving its unresolved identity with the S. Sofia residence.", "Sagredo palace"),
    accepted(40, "cand-2334", "Breval's 'Collection of Prints' is the indexed Sagredo print-and-drawing collection subentry, distinct from the broad multi-medium collection candidate.", "Collection of Prints"),
    accepted(41, "cand-4288", "German old masters is a broad art-historical category in the volumes, not a named work group."),
    accepted(42, "cand-8627", "'These drawings' refers back to the volume of Diziani drawings just described; the statement remains limited to Haskell's account of their later sale."),
    accepted(43, "cand-3567", "Connoisseurship names the collecting expertise inferred from the surviving volumes; map to the existing term candidate."),
    accepted(44, "cand-8636", "The admired prints and drawings are the previously registered Castiglione drawing set; the individual sheets remain unidentified."),
    accepted(45, "cand-2719", "Venice is the city where Castiglione's prints and drawings were admired; use the place candidate."),
    accepted(48, "cand-2719", "Venice is the city named as the destination of the Duke's art shipment; this does not establish the drawings' provenance."),
    accepted(49, "cand-8636", "The phrase identifies Sagredo's collection of the Castiglione drawing set, not the full multi-medium collection.", "collection of these drawings"),
    accepted(58, "cand-1348", "The note refers to the Labia collection in the cited 1749 inventory; inventory entries remain separate work candidates."),
    accepted(59, "cand-3462", "Italian Europa means geographic Europe in Da Canal's quotation, not the mythological figure or Ricci's work."),
    accepted(60, "cand-8590", "The Carracci drawings bought from the Bonfiglioli family are the already registered unidentified group."),
    accepted(61, "cand-11493", "Posse's letter says the pictures were to be sold as a complete collection; use the broad Sagredo collection candidate."),
    accepted(63, "cand-2734", "The index term 'identification of aristocracy with state' precisely matches this Venetian political concept; the adjacent State mention remains a separate candidate."),
    accepted(64, "cand-1886", "The private-palace reference occurs within the Pesaro commission account and is contextually tied to the indexed Pesaro palace; retain that contextual basis.", "private palace"),
    accepted(65, "cand-2719", "Cochin's presence 'in Venice' is a direct city reference in the inventory discussion."),
    accepted(71, "cand-2719", "Venice is the city in the comparison of the Scalzi façade with Europe; the clergy-power index candidate is a separate term."),
    accepted(74, "cand-2719", "Venice is the city used as the comparison for the Jesuit church's marble decoration."),
    accepted(84, "cand-3396", "Counter-Reformation names the art-historical religious movement in Haskell's comparison."),
    accepted(90, "cand-1322", "The Jesuits are the named religious institution in de Bernis's report; reuse the index candidate already present in the note statement."),
]

NO_WRITE = [
    (1, "Churches is an unbounded category in the Manin passage; no individual building is identified by this word."),
    (5, "Prince is a generic political role in Renier's contrast, not an identified person."),
    (6, "Subject means a person subject to a ruler in the quoted political contrast, not a work's subject."),
    (7, "Subject-matter is a generic description of painting content, not an independent entity."),
    (9, "Character describes an ordinary personal quality in the reported funeral oration."),
    (10, "Character is a generic personal-quality term, not a named concept in this sentence."),
    (11, "Family histories means the subject matter of paintings, not a bounded work group."),
    (14, "Subject is the topic represented by the already identified painting, not another object."),
    (15, "Prince is a generic honorific/role in Novelli's praise of Marco Foscarini, not a separate named person."),
    (17, "Prices is a generic market category used for comparison; no particular price record is named."),
    (23, "Drawings is one medium in the multi-medium collection list; no distinct drawing group is identified by this span."),
    (24, "Temperament is an ordinary personal disposition, not a separately named entity."),
    (34, "The phrase 'Venetian artists' is a generic group description; the index matches are patronage subentries, not this group."),
    (37, "Drawings is a generic category in Crespi's quoted estimate; no bounded set is identified."),
    (46, "Subject-matter describes the content and technique of etchings, not an independent object."),
    (47, "The source explicitly says there is no specific reference to drawings among the works sent to the Duke; do not create an object from this negative statement."),
    (50, "This nested 'drawings' span is covered by the accepted phrase 'collection of these drawings' at prompt 49."),
    (51, "Poetry is a figurative description of Castiglione's work, not a named literary object."),
    (52, "The nested 'poetry of' hit is metaphorical prose and does not identify a separate work."),
    (53, "Character is a generic quality inferred by Haskell, not a distinct object."),
    (54, "Subject means the depicted topic of a Vienna canvas; the statement concerns its identification, not a separate entity."),
    (55, "Subject is the generic choice left to the patron and painter in a commission."),
    (56, "Veneto is part of the cited honorific 'Veneto Senatore', not a geographic reference to the region."),
    (57, "Prices is a note's generic cross-reference to amounts discussed elsewhere, not a separate record."),
    (62, "Paintings and drawings bought from Sagredo's heirs are an unbounded plural set in the archival citation; the statement preserves the sale without inventing a separate group."),
    (66, "The caption already records the Barbaro family and façade; 'portraits' is a generic depiction mode, not an independently identified portrait group."),
    (67, "'Venetian artists in England' is a section-like caption heading, not a named entity."),
    (68, "Churches is a generic category in the comparison of religious funding; the sentence does not name a particular church building."),
    (69, "Churches is a generic class before the separately named parish examples; no bounded group is intended."),
    (70, "Churches of several religious orders is an unenumerated group; named orders and individual sites remain represented separately."),
    (72, "Churches is a generic architectural category in a comparison; the named regions and cities are separate place references."),
    (73, "Modello means an architectural model of the Redentore, not the existing term candidate for a preparatory oil sketch."),
    (75, "Subject is the depicted topic associated with the already registered Elijah painting, not a separate entity."),
    (76, "Altarpieces is a generic work category, not a bounded set."),
    (77, "Churches is a generic category in the comparison with palaces; no separate building group is identified."),
    (78, "Palace is used generically alongside church, not as a reference to one identifiable palace."),
    (79, "Churches is an unbounded category in the account of private donations."),
    (80, "Subject is the generic topic left to the patron's choice, not an independently identified work."),
    (81, "Churches refers to the general context of earlier schemes, not a bounded group of buildings."),
    (82, "Subject is a generic topic in the discussion of patron choice."),
    (83, "Venetian churches is a generic subject of Corner's scholarship, not an identifiable group entity."),
    (85, "The nested 'Reformation' hit is part of the accepted compound term 'Counter Reformation' at prompt 84."),
    (86, "Churches is generic in the discussion of altar materials; individual buildings are not named here."),
    (87, "Theatre is a simile for profane decorative style, not a venue."),
    (88, "Churches is a generic category in the quoted criticism; no specific building is identified."),
    (89, "Loreto is part of a generic devotional image/dedication phrase, not the town candidate; no individual Madonna work is named."),
    (91, "Venetian churches is an unbounded comparison class, not a separate collective entity."),
]

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-11493", "index_entry_id": "",
        "canonical_name": "Zaccaria Sagredo's multi-medium collection of paintings, drawings, sculpture, books and armour (scope unresolved)",
        "index_page_range": "", "suggested_type": "", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "Haskell reports that Zaccaria amassed paintings, drawings, sculpture, books and armour, and later discusses the collection's inventories, reputation and dispersal. The exact boundary and itemized contents are not supplied. Keep distinct from the narrower index-seeded print-and-drawing collection candidate cand-2334; do not infer that every pre-existing family picture was Zaccaria's own addition.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-9:09_CHP-9_intro:l231-238#L234",
    },
]

STATEMENT_LINKS = {
    "st-chp9-p251-manin-style-sites": ["cand-2719"],
    "st-chp9-p258-pellegrini-carriera-more-success-abroad": ["cand-2719"],
    "st-chp9-p261-pisani-special-patrons-zais": ["cand-3570"],
    "st-chp9-p262-tiepolo-martyrdom-payment": ["cand-3571"],
    "st-chp9-p262-grassi-old-masters-preference": ["cand-4288"],
    "st-chp9-p262-giovanelli-purchases": ["cand-4288"],
    "st-chp9-p262-note5-cignaroli-ceiling-paintings": ["cand-8201"],
    "st-chp9-p263264-sagredo-patron-collector": ["cand-11493"],
    "st-chp9-p263264-breval-patron-reputation": ["cand-11493"],
    "st-chp9-p263264-sagredo-palace-collection": ["cand-11493"],
    "st-chp9-p263264-will-arrangements-summary": ["cand-11493"],
    "st-chp9-p263264-keysler-gallery-report": ["cand-11493"],
    "st-chp9-p263264-gherardo-death-and-dispersal": ["cand-11493"],
    "st-chp9-p263264-sale-heirs-and-consuls": ["cand-11493"],
    "st-chp9-p263264-heirs-sold-pictures-to-smith": ["cand-11493"],
    "st-chp9-p263264-heirs-sold-to-udney-report": ["cand-11493"],
    "st-chp9-p263264-sagredo-inventory-makers": ["cand-11493"],
    "st-chp9-p263264-tiepolo-drew-1743-inventory": ["cand-11493"],
    "st-chp9-p263264-piazzetta-drew-1743-inventory": ["cand-11493"],
    "st-chp9-p263264-longhi-drew-1762-inventory": ["cand-11493"],
    "st-chp9-p263264-preexisting-collection-and-borgognone": ["cand-11493", "cand-8575"],
    "st-chp9-p265-angelo-valuation-and-reputation": ["cand-11493"],
    "st-chp9-p265-note8-assessment-and-collection-dispersal": ["cand-11493"],
    "st-chp9-p265-cochin-called-angelo-tableau-fort-beau": ["cand-8614"],
    "st-chp9-p266-attributed-artists-in-volumes": ["cand-4288"],
    "st-chp9-p266-sagredo-heirs-sold-volumes": ["cand-8627"],
    "st-chp9-p266-volumes-survive-royal-collection": ["cand-3567"],
    "st-chp9-p266-castiglione-set-and-later-taste": ["cand-2719"],
    "st-chp9-p267-tentative-mantuan-origin-of-sagredo-drawings": ["cand-2719"],
    "st-chp9-p267-entourage-member-may-have-owned-sagredo-drawings": ["cand-2719"],
    "st-chp9-p267-sagredo-drawings-relate-to-mantuan-pictures": ["cand-2719"],
    "st-chp9-p262-note5-labia-inventory": ["cand-1348"],
    "st-chp9-p263264-da-canal-meschini-praise": ["cand-3462"],
    "st-chp9-p263264-posse-complete-sale-report": ["cand-11493"],
    "st-chp9-p249-bambini-triumph-venice": ["cand-1886"],
    "st-chp9-p269-frontage-praise": ["cand-2719"],
    "st-chp9-p272-jesuit-church-marble": ["cand-2719"],
    "st-chp9-p274-angeli-compared-to-roman-counterreformation": ["cand-3396"],
}

NEW_STATEMENT_ID = "st-chp9-p263-zaccaria-amassed-multimedia-collection"
SPLIT_SOURCE_STATEMENT = "st-chp9-p263264-zaccaria-public-service-and-collection"
EXPECTED_OLD_PREDICATE = "zaccaria_sagredo_governed_bergamo_in_1690_and_amassed_a_multi_medium_collection"
GOVERNANCE_QUOTE = "Though he too, like all Venetian aristocrats, was destined for public service, his ambitions clearly lay elsewhere, and he never achieved any higher post than the governorship of Bergamo in 1690.1"
COLLECTION_QUOTE = "He used his considerable resources to amass a large collection of paintings, drawings, sculpture, books and armour"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_hashes() -> dict[str, str]:
    actual = {relative: sha256_bytes((ROOT / relative).read_bytes()) for relative in EXPECTED_HASHES}
    mismatches = {
        key: {"expected": EXPECTED_HASHES[key], "actual": actual[key]}
        for key in EXPECTED_HASHES if actual[key] != EXPECTED_HASHES[key]
    }
    if mismatches:
        raise RuntimeError(f"Locked inputs changed; re-review before writing: {json.dumps(mismatches)}")
    return actual


def read_csv_rows(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    return raw, list(reader.fieldnames or []), list(reader)


def append_csv_rows(raw: bytes, columns: list[str], rows: list[dict[str, str]]) -> bytes:
    eol = b"\r\n" if b"\r\n" in raw else b"\n"
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator=eol.decode("ascii"))
    writer.writerows(rows)
    separator = b"" if raw.endswith((b"\n", b"\r")) else eol
    return raw + separator + buffer.getvalue().encode("utf-8")


def read_jsonl(raw: bytes) -> tuple[list[str], list[dict[str, object]], str, bool]:
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    eol = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines()
    records = [json.loads(line) for line in lines if line.strip()]
    if len(records) != len(lines):
        raise ValueError("Unexpected blank JSONL line; refusing to rewrite the table.")
    return lines, records, eol, bom


def mention_id(row: dict[str, object]) -> str:
    key = "|".join(str(row[field]) for field in ("segment_id", "start_char", "end_char", "candidate_id"))
    return "m-s2-chp9-surface-" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def build_plan() -> dict[str, object]:
    summary, prompts = surface_audit.audit("chp-9", 6)
    if len(ACCEPTED) != 44 or len(NO_WRITE) != 47:
        raise ValueError(f"Malformed prompt partition: accepted={len(ACCEPTED)}, no_write={len(NO_WRITE)}")
    accepted_indices = {int(row["prompt_index"]) for row in ACCEPTED}
    no_write_indices = {int(index) for index, _reason in NO_WRITE}
    if len(accepted_indices) != len(ACCEPTED) or len(no_write_indices) != len(NO_WRITE):
        raise ValueError("Prompt decisions contain duplicate indices.")
    if accepted_indices & no_write_indices or accepted_indices | no_write_indices != set(range(1, 92)):
        raise ValueError("Accepted and no-write decisions do not form an exact partition of prompts 1..91.")
    if summary["reviewed_segments_scanned"] != 46 or summary["uncovered_candidate_surface_spans"] != 91:
        raise ValueError(f"Unexpected scanner scope: {summary}")
    prompts_by_index = {index: row for index, row in enumerate(prompts, 1)}

    segment_rows = [json.loads(line) for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if line]
    segment_by_id = {str(row["segment_id"]): row for row in segment_rows}
    segment_text: dict[str, str] = {}
    for segment in segment_rows:
        if segment.get("chapter") != "chp-9":
            continue
        lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8-sig").splitlines()
        segment_text[str(segment["segment_id"])] = "\n".join(lines[int(segment["line_start"]) - 1:int(segment["line_end"])])

    candidate_raw, candidate_columns, existing_candidates = read_csv_rows(CANDIDATES)
    mention_raw, mention_columns, existing_mentions = read_csv_rows(MENTIONS)
    statements_raw = STATEMENTS.read_bytes()
    statement_lines, statement_rows, statement_eol, statement_bom = read_jsonl(statements_raw)

    candidate_ids = {row["candidate_id"] for row in existing_candidates}
    numeric_ids = [int(value.split("-", 1)[1]) for value in candidate_ids if value.startswith("cand-") and value.split("-", 1)[1].isdigit()]
    if max(numeric_ids, default=0) != 11492:
        raise ValueError(f"Candidate sequence changed; expected cand-11492, got {max(numeric_ids, default=0)}")
    if [row["candidate_id"] for row in NEW_CANDIDATES] != ["cand-11493"] or "cand-11493" in candidate_ids:
        raise ValueError("Unexpected or already allocated candidate ID.")

    mention_ids = {row["mention_id"] for row in existing_mentions}
    occupied: dict[str, list[tuple[int, int]]] = {}
    for row in existing_mentions:
        occupied.setdefault(row["segment_id"], []).append((int(row["start_char"]), int(row["end_char"])))

    planned_mentions: list[dict[str, str]] = []
    for item in ACCEPTED:
        prompt = prompts_by_index[int(item["prompt_index"])]
        segment_id = str(prompt["segment_id"])
        text = segment_text[segment_id]
        surface = str(item["mention_surface"] or prompt["surface_form"])
        prompt_start = int(prompt["start_char"])
        prompt_end = int(prompt["end_char"])
        if surface == prompt["surface_form"]:
            start = prompt_start
        else:
            start = text.find(surface, max(0, prompt_start - 100), min(len(text), prompt_end + 100))
        end = start + len(surface)
        if start < 0 or text[start:end] != surface:
            raise ValueError(f"Accepted mention does not match source text: {item}; got={text[max(0,start):max(0,end)]!r}")
        if start >= prompt_end or end <= prompt_start:
            raise ValueError(f"Accepted mention does not cover its adjudicated prompt: {item}; prompt={prompt}")
        row = {
            "segment_id": segment_id,
            "candidate_id": str(item["candidate_id"]),
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(end),
            "note": str(item["note"]),
        }
        row["mention_id"] = mention_id({**row, "start_char": start, "end_char": end})
        planned_mentions.append(row)

    new_candidate_ids = {row["candidate_id"] for row in NEW_CANDIDATES}
    all_candidate_ids = candidate_ids | new_candidate_ids
    planned_ids: set[str] = set()
    for row in planned_mentions:
        if row["mention_id"] in mention_ids or row["mention_id"] in planned_ids:
            raise ValueError(f"Duplicate mention ID: {row['mention_id']}")
        planned_ids.add(row["mention_id"])
        if row["candidate_id"] not in all_candidate_ids:
            raise ValueError(f"Mention refers to a missing candidate: {row}")
        a, b = int(row["start_char"]), int(row["end_char"])
        if any(a < old_end and b > old_start for old_start, old_end in occupied.get(row["segment_id"], [])):
            raise ValueError(f"Mention overlaps an existing mention: {row}")
        for other in planned_mentions:
            if other is row or other["segment_id"] != row["segment_id"]:
                continue
            if a < int(other["end_char"]) and b > int(other["start_char"]):
                raise ValueError(f"Planned mentions overlap: {row} / {other}")

    statement_map = {str(row["statement_id"]): row for row in statement_rows}
    if len(statement_map) != len(statement_rows):
        raise ValueError("Statement IDs are not unique.")
    if NEW_STATEMENT_ID in statement_map:
        raise ValueError(f"New statement ID already exists: {NEW_STATEMENT_ID}")
    required_statement_ids = set(STATEMENT_LINKS) | {SPLIT_SOURCE_STATEMENT}
    if not required_statement_ids <= statement_map.keys():
        missing = required_statement_ids - statement_map.keys()
        raise ValueError(f"Missing statement update targets: {sorted(missing)}")

    split = statement_map[SPLIT_SOURCE_STATEMENT]
    if split.get("predicate") != EXPECTED_OLD_PREDICATE or split.get("subject_candidate_id") != "cand-2329" or split.get("object_candidate_id") != "cand-8574":
        raise ValueError("The compound Sagredo statement changed; re-review before splitting.")
    if GOVERNANCE_QUOTE not in split.get("original_quote", "") or COLLECTION_QUOTE not in split.get("original_quote", ""):
        raise ValueError("The compound statement no longer contains the exact source clauses to split.")

    updates: dict[str, dict[str, object]] = {}
    for statement_id, ids in STATEMENT_LINKS.items():
        record = statement_map[statement_id]
        qualifiers = record.setdefault("qualifiers", {})
        current = qualifiers.setdefault("mentioned_candidate_ids", [])
        for candidate_id in ids:
            if candidate_id not in all_candidate_ids:
                raise ValueError(f"Statement {statement_id} refers to missing candidate {candidate_id}")
            if candidate_id not in current:
                current.append(candidate_id)
        updates[statement_id] = record

    gov = json.loads(json.dumps(split, ensure_ascii=False))
    gov["predicate"] = "zaccaria_sagredo_governed_bergamo_in_1690"
    gov["original_quote"] = GOVERNANCE_QUOTE
    gq = gov["qualifiers"]
    gq["claim"] = "Haskell says Zaccaria, like Venetian aristocrats generally, was destined for public service but never achieved a higher post than the governorship of Bergamo in 1690."
    gq["qualification"] = "This describes the highest post he achieved, not a complete office chronology; the date and office follow Haskell's report."
    gq["mentioned_candidate_ids"] = ["cand-2329", "cand-8574"]
    updates[SPLIT_SOURCE_STATEMENT] = gov

    collection_statement = {
        "statement_id": NEW_STATEMENT_ID,
        "segment_id": "chp-9:09_CHP-9_intro:l231-238",
        "subject_candidate_id": "cand-2329",
        "object_candidate_id": "cand-11493",
        "predicate": "zaccaria_sagredo_amassed_multi_medium_collection",
        "qualifiers": {
            "source_line_start": 234, "source_line_end": 234,
            "printed_page": 263, "pdf_physical_page": 25,
            "claim": "Haskell says Zaccaria used his resources to amass a large collection of paintings, drawings, sculpture, books and armour.",
            "speaker": "Haskell", "text_layer": "authorial narrative",
            "qualification": "The list names media but not individual objects or an itemized inventory; the boundary with earlier family holdings remains unspecified.",
            "mentioned_candidate_ids": ["cand-2329", "cand-11493"],
            "relation_candidate": True,
        },
        "original_quote": COLLECTION_QUOTE,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
    }

    candidate_output = append_csv_rows(candidate_raw, candidate_columns, NEW_CANDIDATES)
    mention_output = append_csv_rows(mention_raw, mention_columns, planned_mentions)
    output_lines: list[str] = []
    inserted = False
    for line in statement_lines:
        row = json.loads(line)
        statement_id = str(row["statement_id"])
        if statement_id in updates:
            row = updates[statement_id]
            output_lines.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
        else:
            output_lines.append(line)
        if statement_id == SPLIT_SOURCE_STATEMENT:
            output_lines.append(json.dumps(collection_statement, ensure_ascii=False, separators=(",", ":")))
            inserted = True
    if not inserted:
        raise ValueError("Could not place the new collection statement beside its source statement.")
    statement_text = statement_eol.join(output_lines) + statement_eol
    if statement_bom:
        statement_text = "\ufeff" + statement_text
    statement_output = statement_text.encode("utf-8")

    plan_content = {
        "accepted": ACCEPTED, "no_write": NO_WRITE,
        "new_candidates": NEW_CANDIDATES,
        "statement_links": STATEMENT_LINKS,
        "statement_split": {"source": SPLIT_SOURCE_STATEMENT, "new": collection_statement},
    }
    plan_sha = hashlib.sha256(json.dumps(plan_content, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return {
        "scanner_summary": summary, "prompts": prompts,
        "accepted": ACCEPTED, "no_write": NO_WRITE,
        "new_candidates": NEW_CANDIDATES, "planned_mentions": planned_mentions,
        "statement_updates": updates, "plan_sha256": plan_sha,
        "outputs": {CANDIDATES: candidate_output, MENTIONS: mention_output, STATEMENTS: statement_output},
        "before_hashes": {path: sha256_bytes((ROOT / path).read_bytes()) for path in EXPECTED_HASHES if path.startswith("04-knowledge/tables/") and path.rsplit("/",1)[-1] in {"entity-candidates.csv","mentions.csv","book-statements.jsonl"}},
    }


def atomic_write(path: Path, data: bytes) -> None:
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def apply_plan(plan: dict[str, object]) -> Path:
    recovery = Path(tempfile.gettempdir()) / f"pnp-s2-chp9-surface-prompts-{datetime.now():%Y%m%d-%H%M%S}"
    recovery.mkdir(parents=True, exist_ok=False)
    paths = list(plan["outputs"].keys())
    for path in paths:
        shutil.copy2(path, recovery / path.name)
    try:
        for path, data in plan["outputs"].items():
            atomic_write(path, data)
    except Exception:
        for path in paths:
            shutil.copy2(recovery / path.name, path)
        raise
    return recovery


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the locked, preflighted changes")
    args = parser.parse_args()
    verify_hashes()
    plan = build_plan()
    print(json.dumps({
        "mode": "apply" if args.apply else "dry-run",
        "scanner": plan["scanner_summary"],
        "accepted_mentions": len(plan["planned_mentions"]),
        "no_write_prompts": len(plan["no_write"]),
        "new_candidates": len(plan["new_candidates"]),
        "updated_statements": len(plan["statement_updates"]),
        "new_statements": 1,
        "plan_sha256": plan["plan_sha256"],
        "before_hashes": plan["before_hashes"],
    }, ensure_ascii=False))
    if not args.apply:
        return 0
    recovery = apply_plan(plan)
    try:
        after_hashes = {path.name: sha256_bytes(data) for path, data in plan["outputs"].items()}
        summary, remaining = surface_audit.audit("chp-9", 6)
        no_write_signatures = {
            (str(plan["prompts"][index - 1]["segment_id"]), int(plan["prompts"][index - 1]["start_char"]), int(plan["prompts"][index - 1]["end_char"]), str(plan["prompts"][index - 1]["surface_form"]))
            for index, _reason in plan["no_write"]
        }
        spans = [(row["segment_id"], int(row["start_char"]), int(row["end_char"])) for row in plan["planned_mentions"]]
        expected_after = {
            sig for sig in no_write_signatures
            if not any(sig[0] == segment_id and sig[1] < end and sig[2] > start for segment_id, start, end in spans)
        }
        actual_after = {
            (str(hit["segment_id"]), int(hit["start_char"]), int(hit["end_char"]), str(hit["surface_form"]))
            for hit in remaining
        }
        if actual_after != expected_after:
            raise RuntimeError(f"Post-write prompts differ from no-write residue: missing={sorted(expected_after-actual_after)}; extra={sorted(actual_after-expected_after)}; scanner={summary}")
    except Exception:
        for path in plan["outputs"]:
            shutil.copy2(recovery / path.name, path)
        raise
    print(json.dumps({
        "post_write_scanner": summary,
        "remaining_prompts_match_no_write_residue": True,
        "after_hashes": after_hashes,
        "recovery_directory": str(recovery),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
