#!/usr/bin/env python3
"""Semantically adjudicate Chapter 8's candidate-surface prompts.

The scanner is a locator only. This locked writer checks the full prompt
partition, source spans, candidate foreign keys, mention overlaps, and
statement preconditions before it can write the reviewed S2 decisions.
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
    "04-knowledge/tables/entity-candidates.csv": "2a68ced91ee0662e1e3515769eef7ac3d2981d3d00f5773613891a1e4acd22e5",
    "04-knowledge/tables/mentions.csv": "29a2d397cd6c1b32cf90b13d56ab5a68f15ba0011f01d23374f42de4394eea55",
    "04-knowledge/tables/book-statements.jsonl": "a4a942d1f71c7735f03289129503d899683fcd84f9c8011e757e70855d67ed7e",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/s2-coverage.csv": "84f8497a7ce0100f4785acd8bf8ed88bb4c69fe5254cd89d172577b0400eb6c1",
    "scripts/audit_s2_candidate_surfaces.py": "130b53da86d940daad454079960415ac5e7043e0b71239370b66226158cd1ee2",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "02-sources/02-Markdown/08_CHP-8_intro.md": "29f190c6512fa5512cc31f73ae1f9cc68f5943139e49cedf88303f88660a0c10",
    "02-sources/02-Markdown/08_CHP-8_sec_i.md": "8449a867c1b0459a35c8ebbf7d37c0f770cd71ef0be987b12b7a1281d41e12bf",
    "02-sources/02-Markdown/08_CHP-8_sec_i_notes_p211_visual-transcription.md": "2a50e65bd1add38adc02bce184d6e58d286424588ef617411bd5e5c9e22877a4",
    "02-sources/02-Markdown/08_CHP-8_sec_i_notes_p214_visual-transcription.md": "7ab316ce528ffc7cdf49c1304339ed6337ac5b29b7839df3160ac281ee2e15dd",
    "02-sources/02-Markdown/08_CHP-8_sec_ii.md": "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    "02-sources/02-Markdown/08_CHP-8_sec_ii_plates_p232_visual-transcription.md": "8ad8a26c7b8086289177728145cb9fa42a71e19c29278fbf241a743fa1b52405",
    "02-sources/02-Markdown/08_CHP-8_sec_ii_plates_visual-transcription.md": "a46536e973afbdae837b99a9bdc9178f9040c75aca781dea3e730950d04cc7cb",
}


def accepted(
    prompt_index: int,
    candidate_id: str,
    note: str,
    mention_start: int | None = None,
    mention_surface: str | None = None,
) -> dict[str, object]:
    return {
        "prompt_index": prompt_index,
        "candidate_id": candidate_id,
        "mention_start": mention_start,
        "mention_surface": mention_surface,
        "note": note,
    }


ACCEPTED = [
    accepted(2, "cand-1041", "Direct city reference in the p.213 discussion; reuse the in-book Florence candidate."),
    accepted(13, "cand-11489", "Roomer's first, unnamed Naples residence, distinguished from Via Monteoliveto as a street and from the later Palazzo della Stella.", 761, "his palace"),
    accepted(15, "cand-1722", "Naples is named as the city whose painters could satisfy Roomer's taste."),
    accepted(16, "cand-1132", "The Genoese mercantile aristocracy is the stated social group; use the existing term candidate."),
    accepted(17, "cand-4288", "The phrase denotes the broad category of old-master pictures in the Genoese holdings."),
    accepted(18, "cand-1723", "The Neapolitan feudal landowners are a social class, not a place-name; reuse the term candidate."),
    accepted(19, "cand-4288", "Haskell uses old masters for the broad category in Roomer's collection, not for a single painting."),
    accepted(22, "cand-1722", "The sentence names the city of Naples as the setting of the painting's reception."),
    accepted(26, "cand-2117", "The source names Rembrandt as a person; the surrounding work-title matches are separate candidates."),
    accepted(27, "cand-4288", "The phrase is the broad old-master category in Russo's collection discussion."),
    accepted(30, "cand-11492", "The note refers to a distinct palace used by the Del Rosso family; its name and location are not supplied.", 186, "their palace"),
    accepted(31, "cand-3126", "Rome is the city named in the footnote's direction to Mattia Loret.", 987, "Rome"),
    accepted(34, "cand-3578", "Renaissance is the historical/artistic period invoked in the church's architectural history."),
    accepted(35, "cand-7743", "Bergamo is the city named as the site of Santa Maria Maggiore; keep distinct from the index-seeded Bergamo candidate pending S3."),
    accepted(36, "cand-2307", "Ruffo's collection is the object assembled in Ferrara; reuse the existing type-unresolved collection candidate."),
    accepted(37, "cand-2306", "The palace adjoining the Cathedral is Ruffo's Archbishop's Palace in Ferrara."),
    accepted(38, "cand-11490", "The note reports a portrait in Sir William Hamilton's collection in Naples by 1798; collection title and scope remain unresolved."),
    accepted(40, "cand-3540", "Roman artists is a collective social-group term; it does not identify individual artists."),
    accepted(41, "cand-2481", "Canvas refers to the already indexed Andromache weeping before Aeneas painting by Giovan Gioseffo dal Sole."),
    accepted(42, "cand-7731", "Raimondo's palace is the already registered Macerata place candidate."),
    accepted(46, "cand-0381", "Bologna is the city in which Torelli proposed his painting; take the city subspan from the false larger prompt."),
    accepted(48, "cand-2719", "Venice is the city named as the successful setting for the tenebrosi."),
    accepted(51, "cand-4131", "Italian art names the historical field discussed in the interregnum passage."),
    accepted(57, "cand-10725", "Ridotto refers to the Venetian gambling room already represented by the Ch.17 place candidate."),
    accepted(67, "cand-4131", "Italian art is the stated field of the collections discussed in the section introduction."),
    accepted(70, "cand-1609", "The Grand Prince is Ferdinand de' Medici; expand the prompt's Prince subspan to the explicit title." , 1134, "Grand Prince"),
    accepted(73, "cand-1041", "Florence is the city Crespi visited; reuse the existing place candidate."),
    accepted(75, "cand-4131", "Italian art is the field in which Haskell situates Crespi's informal portrait group."),
    accepted(78, "cand-4131", "Italian art is the field in which the treatment of poor and simple subjects remained exceptional."),
    accepted(80, "cand-1041", "Florence is directly named as a city where pictures were exhibited."),
    accepted(81, "cand-4288", "Venetian old masters is the broad art-historical category for the seven listed loans."),
    accepted(82, "cand-4131", "Italian art names the field in the statement about Ferdinand's role in art patronage."),
    accepted(83, "cand-1609", "The lower-case prince refers to Ferdinand in the quoted assessment; the candidate is the person, not a generic office."),
    accepted(85, "cand-7743", "Bergamo is directly named in the note about artists employed by S. Paolo d'Argan."),
    accepted(86, "cand-2306", "The Archbishop's Palace is the same Ferrara building described in the p.222 note."),
    accepted(88, "cand-2306", "The later reference to the palace in the same note points back to Ruffo's Archbishop's Palace."),
    accepted(89, "cand-1017", "Ferrara is the city named in the quoted manuscript account."),
    accepted(93, "cand-2630", "Titian is the named painter whose St Peter Martyr Loth planned to copy."),
    accepted(94, "cand-7865", "Ferdinand's 1716 collection reference is linked to the broader Leopoldo collection candidate, which Haskell says Ferdinand later amplified."),
    accepted(99, "cand-1609", "The Grand Prince is Ferdinand; expand the prompt's Prince subspan to the explicit title.", 11032, "Grand Prince"),
    accepted(101, "cand-1041", "Florence is named as the city in which Gerini followed Ferdinand's patronage."),
    accepted(103, "cand-7664", "Canvas refers to the already registered painting The Flood by Pietro Liberi."),
    accepted(105, "cand-2719", "Venice is the city in which the committee's earlier attempts failed."),
    accepted(107, "cand-11491", "Zanchi's submitted drawings form a source-bounded design group; title, number, survival, and intended picture remain unspecified."),
    accepted(108, "cand-7743", "Bergamo is the named city where Zanchi inspected the site; reuse the Ch.8 body-origin city candidate."),
    accepted(109, "cand-7670", "Canvas refers to Zanchi's already registered Moses striking the Rock painting."),
    accepted(111, "cand-1609", "The plate heading names Grand Prince Ferdinand; expand the false archive hit to the full person name.", 0, "GRAND PRINCE FERDINAND"),
]


NO_WRITE = [
    (1, "The larger 'in Florence' hit is an unrelated index/person pattern; the precise Florence city subspan is accepted at prompt 2."),
    (3, "Subject means the subject of the cited painting, not an independently identified entity."),
    (4, "This is the raw OCR duplicate of the p.211 note; the Del Rosso collection is already mentioned in the page-image transcription."),
    (5, "'Same collection of documents' is a generic reference to archival records, not a separately identified collection object."),
    (6, "The title Italian Art and Britain is already linked to its archive candidate in the p.211 visual transcription; this raw OCR occurrence is duplicate coverage."),
    (7, "This raw OCR palace phrase duplicates the p.214 visual note, where the specific unnamed Del Rosso palace is recorded."),
    (8, "The Bologna citation belongs to p.214 note 3 and is already linked to the publication candidate in the visual transcription."),
    (9, "The Bologna citation belongs to p.214 note 4 and is already linked to the publication candidate in the visual transcription."),
    (10, "The p.214 raw OCR duplicates the visual transcription; the phrase is not a separate collective entity."),
    (11, "The Venice mention is already recorded against the p.214 visual transcription; do not duplicate the parallel raw OCR occurrence."),
    (12, "Fortune means Roomer's wealth in this sentence, not the indexed work Fortune."),
    (14, "Fortune means the wealth Roomer left, not a separately identified work or entity."),
    (20, "The later 'his palace' reference does not distinguish which of Roomer's multiple residences is meant."),
    (21, "The larger 'in Naples' hit matches unrelated index people; the precise Naples city subspan is accepted at prompt 22."),
    (23, "Subject refers to the commission's chosen subject matter, not a separate entity."),
    (24, "Fortune is a common-language reference to inherited wealth."),
    (25, "Subject means the painter's choice of subject matter, not an independently identified entity."),
    (28, "The garden is descriptive scenery around an unnamed house; no separately identifiable garden is given."),
    (29, "'Same collection of documents' is a generic reference to records, not a bounded archive candidate."),
    (32, "Payment is a general financial term, not an identified payment record."),
    (33, "'Neglect of Roman painting' is Haskell's interpretive description, not a named entity."),
    (39, "Histories means the broad genre of history paintings, not a named work or bounded group."),
    (43, "Subject-matter is generic; the source does not identify a separate concept entity."),
    (44, "Subject and date are generic requirements in the guarantee, not entities."),
    (45, "The larger 'in Bologna' hit is an unrelated index/person pattern; the precise city subspan is accepted at prompt 46."),
    (47, "Subject is the general category of Biblical and mythological topics."),
    (49, "Contracts is an unbounded plural reference; the passage identifies no individual contract or record."),
    (50, "Subject refers to The Infant Jupiter handed over by Cybele, already registered as a work."),
    (52, "Subject identifies the topic of the already named work The Levites, not a separate entity."),
    (53, "Subject identifies the topic of the already named Story of Esther painting, not a separate entity."),
    (54, "Private memoirs is a generic source category, not a separately bounded archive."),
    (55, "Character means an ordinary personal quality in Haskell's prose."),
    (56, "Artistic tastes describes Ferdinand's dispositions, not a separate entity."),
    (58, "Churches is a generic category in a comparison, without individually named buildings."),
    (59, "Average noble collection is a generic comparison class, not a bounded collection."),
    (60, "Subject refers to a narrative subject of painting, not a distinct entity."),
    (61, "The churches from which paintings were bought are unnamed and unbounded."),
    (62, "Patronage of contemporary artists describes Ferdinand's activity, not a separate object."),
    (63, "Prince and painter are generic roles in a comparison, not named individuals."),
    (64, "Subject means the chosen Old Testament topic, not a separately identified entity."),
    (65, "Portraits of the Prince and his household is an unbounded genre/group description, not a defined portrait set."),
    (66, "Local school means an unspecified artistic tradition, not a named institution or bounded group."),
    (68, "Character is an ordinary description of Ferdinand's personality."),
    (69, "Temperament is a common personal-quality term."),
    (71, "Subject is the generic topic of a still life."),
    (72, "Histories is a broad religious/secular painting genre, not a bounded work group."),
    (74, "Temperament is an ordinary descriptive term."),
    (76, "Subject is a generic topic category for the painting."),
    (77, "Portraits of Ferdinand's courtiers is an unbounded group description; no separate set identity is supplied."),
    (79, "The larger 'in Florence' hit is an unrelated index/person pattern; the precise Florence city subspan is accepted at prompt 80."),
    (84, "Subject introduces the represented subject already preserved as the source-reported Hymn of Liberation candidate."),
    (87, "The nested 'palace' hit is contained in the accepted Archbishop's Palace phrase at prompt 86."),
    (90, "Churches refers to a generic set of Florentine and other buildings, none identified individually here."),
    (91, "Payments is a generic note heading for records; the archival source is already represented separately."),
    (92, "Payments to other painters is a generic citation heading, not an individually identified payment record."),
    (95, "Subject is the topic of the named work in the adjacent statement, not another entity."),
    (96, "Subject is the biblical topic of the already identified painting, not an independent entity."),
    (97, "Portraits refers to a broad category of pictures, not a bounded group."),
    (98, "Bologna is the publication place in the citation for the already registered Mostra Celebrativa catalogue, not a narrative city reference."),
    (100, "Subject means the same topic already attached to the registered Crossing of the Red Sea candidate."),
    (102, "Drawings describes Gabburri's professional field and practice, not a distinct drawing group."),
    (104, "Payments is a general financial category in the quoted contract, not a discrete record."),
    (106, "Payment refers to the general no-fee condition for submitting designs, not an identified payment object."),
    (110, "Subject is an anaphoric reference to the painting already represented by the Crossing of the Red Sea candidate."),
]


NEW_CANDIDATES = [
    {
        "candidate_id": "cand-11489", "index_entry_id": "",
        "canonical_name": "Gaspar Roomer's unidentified first palace on Via Monteoliveto",
        "index_page_range": "", "suggested_type": "place", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "Haskell distinguishes the palace in which Roomer first entertained Neapolitan nobility from the later Palazzo della Stella and says it was on Via Monteoliveto. The building's name and independent identity are not supplied; keep it distinct from the street and later residence.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-8:08_CHP-8_sec_i:l23-28#L25",
    },
    {
        "candidate_id": "cand-11490", "index_entry_id": "",
        "canonical_name": "Sir William Hamilton's collection including the portrait later in the Metropolitan Museum (scope unresolved)",
        "index_page_range": "", "suggested_type": "", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "Haskell says the portrait then in the Metropolitan Museum had been in Sir William Hamilton's collection in Naples by 1798. The collection has no supplied formal name or boundary; keep it type-unresolved and distinct from the portrait and Hamilton himself.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-8:08_CHP-8_sec_ii:l126-138#L137",
    },
    {
        "candidate_id": "cand-11491", "index_entry_id": "",
        "canonical_name": "Drawings submitted by Antonio Zanchi for committee approval (intended picture unspecified)",
        "index_page_range": "", "suggested_type": "work", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "Haskell says Zanchi received no payment for submitting drawings and describes conditional approval and execution terms. Their title, number, survival, and intended picture are not established; do not conflate them with Moses striking the Rock or another proposed painting.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-8:08_CHP-8_sec_ii:l78-84#L82",
    },
    {
        "candidate_id": "cand-11492", "index_entry_id": "",
        "canonical_name": "Unidentified palace used by the Del Rosso family (location unspecified)",
        "index_page_range": "", "suggested_type": "place", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "Haskell's p.214 note says the Del Rosso family summoned Giacomo Antonio Boni to decorate rooms in their palace with mythological frescoes. The building's name and location are not supplied; keep the place distinct from the fresco group and the family.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-8:08_CHP-8_sec_i_notes_p214_visual-transcription:l1-4#L1",
    },
]

STATEMENT_LINKS = {
    "st-chp8-p203-genoese-family-collections": ["cand-4288"],
    "st-chp8-p205-roomer-hosted-neapolitan-nobility": ["cand-11489"],
    "st-chp8-p206-bassano-animal-pieces-qualified-authorial-inference": ["cand-4288"],
    "st-chp8-p214-n1-boni-mythological-frescoes": ["cand-11492"],
    "st-chp8-p214-n4-cite-loret": ["cand-3126"],
    "st-chp8-p214-n4-venetian-admirers": ["cand-2719"],
    "st-chp8-p215-renaissance-campanile-sacristy": ["cand-3578"],
    "st-chp8-p217-ferri-selected-invited-open": ["cand-2719"],
    "st-chp8-p218-zanchi-terms": ["cand-11491", "cand-7743"],
    "st-chp8-p221-governors-ambition": ["cand-7743"],
    "st-chp8-p221-provincial-patronage-context": ["cand-7743"],
    "st-chp8-p222-n4-pareja-museum-and-hamilton": ["cand-11490"],
    "st-chp8-p223-ruffo-opinion-of-roman-artists": ["cand-3540"],
    "st-chp8-p233-note5-inventory": ["cand-7865"],
    "st-chp8-p233-note5-loth-letter": ["cand-2630"],
    "st-chp8-p237-ferdinand-role-in-crespi-career": ["cand-1041"],
    "st-chp8-p241-note5-gerini-follower": ["cand-1041"],
    "st-chp8-p241-quoted-praise-and-art-patronage": ["cand-4131"],
    "st-chp8-p241-twenty-odd-loans": ["cand-4288"],
    "st-chp8-sec-ii-intro-collections_in_nonlocal_centres": ["cand-4131"],
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(relative: str) -> str:
    return sha256_bytes((ROOT / relative).read_bytes())


def verify_hashes() -> dict[str, str]:
    actual = {relative: sha256_path(relative) for relative in EXPECTED_HASHES}
    mismatches = {
        relative: {"expected": EXPECTED_HASHES[relative], "actual": actual[relative]}
        for relative in EXPECTED_HASHES
        if actual[relative] != EXPECTED_HASHES[relative]
    }
    if mismatches:
        raise RuntimeError(f"Locked inputs changed; re-review before writing: {json.dumps(mismatches)}")
    return actual


def read_csv_rows(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(text)))
    reader = csv.DictReader(io.StringIO(text))
    return raw, list(reader.fieldnames or []), rows


def append_csv_rows(raw: bytes, columns: list[str], rows: list[dict[str, str]]) -> bytes:
    eol = b"\r\n" if b"\r\n" in raw else b"\n"
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator=eol.decode("ascii"))
    for row in rows:
        writer.writerow(row)
    addition = buffer.getvalue().encode("utf-8")
    separator = b"" if raw.endswith((b"\n", b"\r")) else eol
    return raw + separator + addition


def jsonl_records(raw: bytes) -> tuple[list[str], list[dict[str, object]], str, bool]:
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    eol = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines()
    records = [json.loads(line) for line in lines if line.strip()]
    if len(records) != len(lines):
        raise ValueError("Unexpected blank JSONL line; refusing to rewrite the table.")
    return lines, records, eol, has_bom


def mention_id(row: dict[str, object]) -> str:
    key = "|".join(str(row[key]) for key in ("segment_id", "start_char", "end_char", "candidate_id"))
    return "m-s2-chp8-surface-" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def build_plan() -> dict[str, object]:
    summary, prompts = surface_audit.audit("chp-8", 6)
    if len(ACCEPTED) != 47 or len(NO_WRITE) != 64:
        raise ValueError(f"The prompt partition is malformed: accepted={len(ACCEPTED)}, no_write={len(NO_WRITE)}")
    if len({int(row["prompt_index"]) for row in ACCEPTED}) != len(ACCEPTED):
        raise ValueError("Accepted prompt indices are duplicated.")
    no_write_indices = [int(index) for index, _ in NO_WRITE]
    if len(set(no_write_indices)) != len(no_write_indices):
        raise ValueError("No-write prompt indices are duplicated.")
    accepted_indices = {int(row["prompt_index"]) for row in ACCEPTED}
    if accepted_indices & set(no_write_indices):
        raise ValueError("Accepted and no-write prompt indices overlap.")
    if accepted_indices | set(no_write_indices) != set(range(1, 112)):
        missing = sorted(set(range(1, 112)) - accepted_indices - set(no_write_indices))
        extra = sorted((accepted_indices | set(no_write_indices)) - set(range(1, 112)))
        raise ValueError(f"Prompt partition does not cover 1..111: missing={missing}; extra={extra}")
    if int(summary["reviewed_segments_scanned"]) != 56 or int(summary["uncovered_candidate_surface_spans"]) != 111:
        raise ValueError(f"Unexpected scanner scope or count: {summary}")
    prompts_by_index = {index: row for index, row in enumerate(prompts, 1)}

    segment_rows = [
        json.loads(line)
        for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line
    ]
    segment_text: dict[str, str] = {}
    for segment in segment_rows:
        if segment.get("chapter") != "chp-8":
            continue
        source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8-sig").splitlines()
        segment_text[segment["segment_id"]] = "\n".join(
            source_lines[int(segment["line_start"]) - 1 : int(segment["line_end"])]
        )

    for item in ACCEPTED:
        prompt = prompts_by_index[int(item["prompt_index"])]
        segment_id = str(prompt["segment_id"])
        text = segment_text.get(segment_id)
        if text is None:
            raise ValueError(f"Accepted prompt is outside Chapter 8: {prompt}")
        start = int(item["mention_start"] if item["mention_start"] is not None else prompt["start_char"])
        surface = str(item["mention_surface"] if item["mention_surface"] is not None else prompt["surface_form"])
        end = start + len(surface)
        if text[start:end] != surface:
            raise ValueError(f"Accepted mention does not match its source span: {item}; actual={text[start:end]!r}")
        prompt_start, prompt_end = int(prompt["start_char"]), int(prompt["end_char"])
        if start >= prompt_end or end <= prompt_start:
            raise ValueError(f"Accepted mention does not cover its adjudicated prompt: {item}; prompt={prompt}")

    candidate_raw, candidate_columns, existing_candidates = read_csv_rows(CANDIDATES)
    mention_raw, mention_columns, existing_mentions = read_csv_rows(MENTIONS)
    candidate_ids = {row["candidate_id"] for row in existing_candidates}
    numeric_ids = [
        int(value.split("-", 1)[1])
        for value in candidate_ids
        if value.startswith("cand-") and value.split("-", 1)[1].isdigit()
    ]
    if max(numeric_ids, default=0) != 11488:
        raise ValueError(f"Candidate sequence changed; expected cand-11488, got {max(numeric_ids, default=0)}")
    new_ids = [str(row["candidate_id"]) for row in NEW_CANDIDATES]
    if new_ids != ["cand-11489", "cand-11490", "cand-11491", "cand-11492"]:
        raise ValueError(f"Unexpected candidate allocation: {new_ids}")
    if len(set(new_ids)) != len(new_ids) or set(new_ids) & candidate_ids:
        raise ValueError("New candidate IDs are duplicated or already present.")

    mention_ids = {row["mention_id"] for row in existing_mentions}
    occupied: dict[str, list[tuple[int, int]]] = {}
    for row in existing_mentions:
        occupied.setdefault(row["segment_id"], []).append((int(row["start_char"]), int(row["end_char"])))
    planned_mentions: list[dict[str, str]] = []
    for item in ACCEPTED:
        prompt = prompts_by_index[int(item["prompt_index"])]
        start = int(item["mention_start"] if item["mention_start"] is not None else prompt["start_char"])
        surface = str(item["mention_surface"] if item["mention_surface"] is not None else prompt["surface_form"])
        record = {
            "segment_id": str(prompt["segment_id"]),
            "candidate_id": str(item["candidate_id"]),
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(start + len(surface)),
            "note": str(item["note"]),
        }
        record["mention_id"] = mention_id({**record, "start_char": start, "end_char": start + len(surface)})
        if record["mention_id"] in mention_ids:
            raise ValueError(f"Mention ID already exists: {record['mention_id']}")
        if record["candidate_id"] not in candidate_ids | set(new_ids):
            raise ValueError(f"Mention refers to a missing candidate: {record}")
        a, b = int(record["start_char"]), int(record["end_char"])
        if any(a < old_end and b > old_start for old_start, old_end in occupied.get(record["segment_id"], [])):
            raise ValueError(f"Mention overlaps an existing span: {record}")
        if any(
            a < int(other["end_char"]) and b > int(other["start_char"])
            for other in planned_mentions
            if other["segment_id"] == record["segment_id"]
        ):
            raise ValueError(f"Planned mentions overlap: {record}")
        mention_ids.add(record["mention_id"])
        planned_mentions.append(record)

    statements_raw = STATEMENTS.read_bytes()
    statement_lines, statement_rows, statement_eol, statement_bom = jsonl_records(statements_raw)
    statement_map = {str(row["statement_id"]): row for row in statement_rows}
    if len(statement_map) != len(statement_rows):
        raise ValueError("Statement IDs are not unique.")
    if not set(STATEMENT_LINKS) <= statement_map.keys():
        raise ValueError(f"Missing statement update targets: {sorted(set(STATEMENT_LINKS) - statement_map.keys())}")
    all_candidate_ids = candidate_ids | set(new_ids)
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
    for statement_id, record in updates.items():
        for field in ("subject_candidate_id", "object_candidate_id"):
            value = record.get(field)
            if value is not None and value not in all_candidate_ids:
                raise ValueError(f"Updated {statement_id} has missing {field} candidate {value}")
        for value in record.get("qualifiers", {}).get("mentioned_candidate_ids", []):
            if value not in all_candidate_ids:
                raise ValueError(f"Updated {statement_id} has missing mentioned candidate {value}")

    candidate_output = append_csv_rows(candidate_raw, candidate_columns, NEW_CANDIDATES)
    mention_output = append_csv_rows(mention_raw, mention_columns, planned_mentions)
    statement_output_lines = list(statement_lines)
    for index, line in enumerate(statement_lines):
        record = json.loads(line)
        statement_id = str(record["statement_id"])
        if statement_id in updates:
            statement_output_lines[index] = json.dumps(updates[statement_id], ensure_ascii=False)
    statement_text = statement_eol.join(statement_output_lines) + statement_eol
    if statement_bom:
        statement_text = "\ufeff" + statement_text
    statement_output = statement_text.encode("utf-8")

    plan_content = {
        "accepted": ACCEPTED,
        "no_write": NO_WRITE,
        "new_candidates": NEW_CANDIDATES,
        "statement_links": STATEMENT_LINKS,
    }
    plan_sha = hashlib.sha256(
        json.dumps(plan_content, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "scanner_summary": summary,
        "prompts": prompts,
        "accepted": ACCEPTED,
        "no_write": NO_WRITE,
        "new_candidates": NEW_CANDIDATES,
        "planned_mentions": planned_mentions,
        "statement_updates": updates,
        "plan_sha256": plan_sha,
        "outputs": {CANDIDATES: candidate_output, MENTIONS: mention_output, STATEMENTS: statement_output},
        "before_hashes": {
            "04-knowledge/tables/entity-candidates.csv": sha256_bytes(candidate_raw),
            "04-knowledge/tables/mentions.csv": sha256_bytes(mention_raw),
            "04-knowledge/tables/book-statements.jsonl": sha256_bytes(statements_raw),
        },
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
    recovery = Path(tempfile.gettempdir()) / f"pnp-s2-chp8-surface-prompts-{datetime.now():%Y%m%d-%H%M%S}"
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
        "plan_sha256": plan["plan_sha256"],
        "before_hashes": plan["before_hashes"],
    }, ensure_ascii=False))
    if not args.apply:
        return 0
    recovery = apply_plan(plan)
    try:
        after_hashes = {path.name: sha256_bytes(data) for path, data in plan["outputs"].items()}
        summary, prompts = surface_audit.audit("chp-8", 6)
        no_write_signatures = {
            (str(plan["prompts"][index - 1]["segment_id"]), int(plan["prompts"][index - 1]["start_char"]), int(plan["prompts"][index - 1]["end_char"]), str(plan["prompts"][index - 1]["surface_form"]))
            for index, _reason in plan["no_write"]
        }
        planned_spans = [
            (row["segment_id"], int(row["start_char"]), int(row["end_char"]))
            for row in plan["planned_mentions"]
        ]
        expected_after = {
            signature for signature in no_write_signatures
            if not any(
                signature[0] == segment_id and signature[1] < end and signature[2] > start
                for segment_id, start, end in planned_spans
            )
        }
        after_signatures = {
            (str(hit["segment_id"]), int(hit["start_char"]), int(hit["end_char"]), str(hit["surface_form"]))
            for hit in prompts
        }
        if after_signatures != expected_after:
            raise RuntimeError(
                f"Post-write scanner set differs from surviving no-write decisions: "
                f"summary={summary}; missing={sorted(expected_after-after_signatures)}; "
                f"extra={sorted(after_signatures-expected_after)}"
            )
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
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
