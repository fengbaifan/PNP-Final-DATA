from __future__ import annotations

import argparse
import codecs
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path.cwd()
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "05_CHP-5_sec_i.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-5.pdf"
PAGE_IMAGE = PROCESS / "p131_page_review_20261012.png"
SEGMENT = "chp-5:05_CHP-5_sec_i:l115-123"
SOURCE_FILE = "02-sources/02-Markdown/05_CHP-5_sec_i.md"
EXPECTED = {
    "book-statements.jsonl": "1cda591a07de1cc49d2ce55de1932726f291303b987f40c069a614dc09206f0b",
    "entity-candidates.csv": "df039573b75fb0d72c08773e058c009cda2f70730629471e2b06465b69abf235",
    "mentions.csv": "ab090632eb7b56a6814d79264669a1648e5c7ca093e5e3d42ad3bf7353384c45",
}
SOURCE_SHA = "8ef51cd646ed6abf398c9faeb47df9a03f70de696d9a871c6d0b734b2adeeeee"
PDF_SHA = "f63dca79808fde73ba10aa9414fef89bc8ca5e77ed829b2d5c86f23719e0674a"
IMAGE_SHA = "9231ae7a3aca9649bd6a5f8cfb3218a7b3fbe6927f839b97207e69572a7f8a96"
SEGMENT_SHA = "78c4b953b87c595419bae0aff8a0c1c68ee336b56a5061ce28a9c475b2979986"

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-11796", "index_entry_id": "",
        "canonical_name": "Unidentified patrons of Sassoferrato's works (source-defined group)",
        "index_page_range": "", "suggested_type": "term", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "Haskell says the great bulk of Sassoferrato's work was for unknown patrons. No patrons or individual works are named. Keep this source-defined group distinct from the wider public in cand-6064 and from the hypothesized professional community in cand-6075.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L123",
    },
    {
        "candidate_id": "cand-11797", "index_entry_id": "",
        "canonical_name": "Sassoferrato's recurring Holy Family pictures (unnamed work group)",
        "index_page_range": "", "suggested_type": "work", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "Source-defined group described as Sassoferrato's recurring Holy Family pictures, based on three or four prototypes and almost polemical against the current Baroque style. No individual titles are supplied; keep distinct from the Raphael Holy Family cand-2101 and the rosary painting cand-4095.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L117",
    },
    {
        "candidate_id": "cand-11798", "index_entry_id": "",
        "canonical_name": "Clerics portrayed by Sassoferrato (unnamed group)",
        "index_page_range": "", "suggested_type": "term", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "Haskell says Sassoferrato drew and painted many clerics, including an occasional cardinal and governor of some papal states. No individual sitters or specific portraits are identified.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L123",
    },
]

NEW_MENTIONS = [
    {"mention_id": "m-chp5-p131-0063", "segment_id": SEGMENT,
     "candidate_id": "cand-11797", "surface_form": "pictures of tire Holy Family",
     "start_char": "192", "end_char": "220",
     "note": "Source-defined Holy Family work group; print reads 'the Holy Family', while OCR has 'tire'. Keep distinct from the Raphael Holy Family and the Plate 21a painting."},
    {"mention_id": "m-chp5-p131-0064", "segment_id": SEGMENT,
     "candidate_id": "cand-11798", "surface_form": "many clerics",
     "start_char": "2189", "end_char": "2201",
     "note": "Unnamed sitter group Sassoferrato drew and painted; the source names no individual cleric."},
]

RELATION_NOTES = {
    "st-chp5-p131-1636-transfer-to-barberini": "The source says the Dominicans gave the picture to Barberini on an understanding he would compensate them; it does not state the amount or confirm payment.",
    "st-chp5-p131-1641-calabrian-church-commission": "The priests commissioned a painting from Sassoferrato. The painting candidate identifies the commissioned subject; completion is not independently established by this sentence.",
    "st-chp5-p131-1643-replacement-commission": "The Princess decided to replace the Raphael Holy Family with this work; preserve the decision and replacement context without asserting the earlier sale was completed.",
    "st-chp5-p131-almost-certain-association": "Haskell qualifies the association as 'almost certain'; keep the attribution and its uncertainty.",
    "st-chp5-p131-barberini-took-picture": "The source reports that Barberini took the picture and regarded the matter as closed; do not infer completed payment or legal ownership.",
    "st-chp5-p131-camillo-nephew-of-innocent-x": "Explicit kinship statement; the page image reads 'Pamfili' where the OCR has 'Pamftli'.",
    "st-chp5-p131-classicism-and-raphael-guides": "A generalized account of later artistic guides and likely acquisition timing; not a relation between the named artist and a specific work or patron.",
    "st-chp5-p131-clerical-portraits": "The source explicitly says Sassoferrato drew and painted an unnamed group of clerics; the sitter group is source-defined and no individuals are identified.",
    "st-chp5-p131-congenial-task-and-masterpiece": "Haskell links an especially congenial task with Sassoferrato's masterpiece, identified later in the passage with the rosary painting. Preserve 'what must have been' as inference.",
    "st-chp5-p131-cozza-altarpiece": "The priests employed Cozza on an altar painting; preserve the artist-to-employer relation and retain the unnamed painting as context.",
    "st-chp5-p131-cozza-probably-recommended": "Haskell's recommendation attribution is explicitly probable, not certain.",
    "st-chp5-p131-current-style-opposition": "The source says the work group appears almost polemical against the current Baroque style; 'appears' and 'almost' remain Haskell's interpretation.",
    "st-chp5-p131-dominicans-decided-to-sell-raphael-holy-family": "The Dominicans decided to sell the picture; Giustiniani's offer is recorded separately, and the text says negotiations fell through rather than that this sale was completed.",
    "st-chp5-p131-early-career-success": "A qualified authorial summary of career success, not a dyadic relation.",
    "st-chp5-p131-gigli-diary": "The source says Gigli kept the diary; note 4 is linked to the citation. The bibliographic edition candidate is not independently consulted here.",
    "st-chp5-p131-gigli-profile": "A descriptive profile of Gigli; the scan reads 'Gigli' and 'diligently' where OCR has 'GigE' and 'diEgently'.",
    "st-chp5-p131-holy-family-pictures-and-prototypes": "The passage describes an almost-exclusive recurring subject and source-defined picture group; print reads 'the Holy Family' where OCR has 'tire Holy Family'.",
    "st-chp5-p131-models": "Raphael is one of three named models. The full list is split into scalar person-to-person influence candidates; Domenichino's 'most austere' qualification is retained on its own row.",
    "st-chp5-p131-paid-one-hundred-scudi": "The Princess paid Sassoferrato 100 scudi for the rosary painting; keep the artwork as context and the price as a qualifier.",
    "st-chp5-p131-patrician-collections-and-late-acquisition": "The works and collections are unnamed and the late-acquisition timing is qualified as probable; retain as a source claim without an entity edge.",
    "st-chp5-p131-picture-reception-public-commissions": "Haskell says the picture evidently did not please; preserve 'evidently' as authorial inference. The subsequent rarity of public commissions is split into a separate claim.",
    "st-chp5-p131-princess-wife-of-camillo": "Explicit spousal relationship in the source.",
    "st-chp5-p131-professional-community-inference": "Haskell strongly suggests Sassoferrato was principally employed by this professional community; preserve the claim as an inference, not a verified employment history.",
    "st-chp5-p131-sassoferrato-location-and-career": "The source places Sassoferrato's arrival in Rome during Urban VIII's reign and names the Marche as his native region; Rome is the destination endpoint and Marche remains an origin qualifier. Print reads 'the Holy Family' where OCR has 'tire Holy Family'.",
    "st-chp5-p131-shared-pupilage": "This row records Cozza's pupilage under Domenichino; the same sentence separately supports Sassoferrato's pupilage.",
    "st-chp5-p131-unknown-patrons": "The passage says most of Sassoferrato's work was for unknown patrons. This unnamed patron group is distinct from p.130's wider public and from the professional community Haskell only hypothesizes.",
}

RELATION_FLAGS = {
    "st-chp5-p131-1636-transfer-to-barberini": True,
    "st-chp5-p131-1641-calabrian-church-commission": True,
    "st-chp5-p131-1643-replacement-commission": True,
    "st-chp5-p131-almost-certain-association": True,
    "st-chp5-p131-barberini-took-picture": True,
    "st-chp5-p131-camillo-nephew-of-innocent-x": True,
    "st-chp5-p131-classicism-and-raphael-guides": False,
    "st-chp5-p131-clerical-portraits": True,
    "st-chp5-p131-congenial-task-and-masterpiece": True,
    "st-chp5-p131-cozza-altarpiece": True,
    "st-chp5-p131-cozza-probably-recommended": True,
    "st-chp5-p131-current-style-opposition": True,
    "st-chp5-p131-dominicans-decided-to-sell-raphael-holy-family": True,
    "st-chp5-p131-early-career-success": False,
    "st-chp5-p131-gigli-diary": True,
    "st-chp5-p131-gigli-profile": False,
    "st-chp5-p131-holy-family-pictures-and-prototypes": True,
    "st-chp5-p131-models": True,
    "st-chp5-p131-paid-one-hundred-scudi": True,
    "st-chp5-p131-patrician-collections-and-late-acquisition": False,
    "st-chp5-p131-picture-reception-public-commissions": False,
    "st-chp5-p131-princess-wife-of-camillo": True,
    "st-chp5-p131-professional-community-inference": True,
    "st-chp5-p131-sassoferrato-location-and-career": True,
    "st-chp5-p131-shared-pupilage": True,
    "st-chp5-p131-unknown-patrons": True,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
segment_text = "\n".join(source_lines[114:123])


def exact(text: str, needle: str) -> str:
    need(needle in text, f"source quote not found: {needle!r}")
    return needle


def qualifier(line_start: int, line_end: int, claim: str, qualification: str,
              mentioned: list[str], relation: bool, **extra) -> dict:
    q = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page_locator": "p.131",
        "pdf_physical_page": 12,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "authorial narrative",
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation,
        "relation_candidate_note": ("Source-grounded S2 relation candidate only; no S6 formal edge is created."
                                    if relation else
                                    "Retained as a source claim, but not a candidate for a formal entity relation."),
    }
    q.update(extra)
    return q


def new_statement(sid: str, subject: str | None, obj: str | None, predicate: str,
                  quote: str, line_start: int, line_end: int, claim: str,
                  qualification: str, mentioned: list[str], relation: bool, **extra) -> dict:
    return {
        "statement_id": sid,
        "segment_id": SEGMENT,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifier(line_start, line_end, claim, qualification, mentioned, relation, **extra),
        "original_quote": exact(segment_text, quote),
        "origin": "book",
        "source_file": SOURCE_FILE,
    }


NEW_STATEMENTS = [
    new_statement("st-chp5-p131-holy-family-subject", "cand-11797", "cand-6071",
                  "picture_group_has_holy_family_subject", "pictures of tire Holy Family", 117, 117,
                  "The source describes Sassoferrato's recurring picture group as paintings of the Holy Family.",
                  "This is the source's subject description, not an identification of individual works.",
                  ["cand-11797", "cand-6071"], True),
    new_statement("st-chp5-p131-holy-family-prototypes", "cand-11797", "cand-6070",
                  "based_on_and_varied_three_or_four_prototypes",
                  "basing himself on three or four prototypes which he varied from time to time", 117, 117,
                  "Haskell says Sassoferrato based this picture group on three or four prototypes and varied them over time.",
                  "The count is approximate and no prototype is individually identified.",
                  ["cand-11797", "cand-6070"], True, reported_count="three or four"),
    new_statement("st-chp5-p131-model-annibale-carracci", "cand-2369", "cand-0576",
                  "modeled_his_practice_on", "His models were Raphael, Annibale Carracci and\nDomenichino at his most austere", 117, 118,
                  "Haskell names Annibale Carracci as one of Sassoferrato's models.",
                  "Scalar relation split from a three-painter list; the source gives no specific copied work.",
                  ["cand-2369", "cand-0576"], True),
    new_statement("st-chp5-p131-model-domenichino", "cand-2369", "cand-0932",
                  "modeled_his_practice_on", "His models were Raphael, Annibale Carracci and\nDomenichino at his most austere", 117, 118,
                  "Haskell names Domenichino, specifically at his most austere, as one of Sassoferrato's models.",
                  "Scalar relation split from a three-painter list; 'at his most austere' is preserved as a style qualifier.",
                  ["cand-2369", "cand-0932"], True, model_qualification="at his most austere"),
    new_statement("st-chp5-p131-sassoferrato-pupil-of-domenichino", "cand-2369", "cand-0932",
                  "trained_by", "for both had been pupils of Domenichino", 119, 119,
                  "Haskell says Sassoferrato had been a pupil of Domenichino.",
                  "This scalar row resolves the second person in the source's 'both'; the existing row records Cozza.",
                  ["cand-2369", "cand-0932", "cand-0867"], True),
    new_statement("st-chp5-p131-dominicans-held-raphael-holy-family", "cand-2101", "cand-0941",
                  "held_by", "a Raphael Holy Family in their possession", 119, 119,
                  "A Raphael Holy Family was in the Dominicans' possession before the proposed sale.",
                  "The source establishes possession, not the legal title or the final outcome of the proposed sale.",
                  ["cand-2101", "cand-0941", "cand-3969"], True),
    new_statement("st-chp5-p131-giustiniani-offer", "cand-1200", "cand-2101",
                  "offered_2000_scudi_for", "to Vincenzo Giustiniani, who offered 2000 scudi", 119, 119,
                  "Vincenzo Giustiniani offered 2,000 scudi for the Raphael Holy Family.",
                  "This is an offer in negotiations that later fell through, not a completed purchase.",
                  ["cand-1200", "cand-2101", "cand-2098", "cand-0941"], True,
                  amount="2000 scudi", transaction_status="offer; negotiations_failed"),
    new_statement("st-chp5-p131-public-commissions-became-rare", "cand-2369", None,
                  "public_commissions_became_exceedingly_rare", "for thereafter Sassoferrato’s public commissions became exceedingly rare", 123, 123,
                  "Haskell says Sassoferrato's public commissions became exceedingly rare after the picture failed to please.",
                  "This is a generalized reception and career claim; commissioners and commissions are not individually identified.",
                  ["cand-2369", "cand-4095"], False),
]


def read_jsonl(path: Path) -> tuple[list[dict], list[str]]:
    raw_lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    return [json.loads(line) for line in raw_lines if line.strip()], raw_lines


def read_csv(path: Path) -> tuple[list[dict], list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader), list(reader.fieldnames or [])


def build_plan() -> dict:
    for filename, digest in EXPECTED.items():
        path = TABLES / filename
        need(path.exists() and sha256(path) == digest, f"table changed since review: {filename}")
    need(not (TABLES / "book-statements.jsonl").read_bytes().startswith(codecs.BOM_UTF8),
         "statement JSONL encoding changed; refusing rewrite")
    need(sha256(SOURCE) == SOURCE_SHA, "source asset changed since review")
    need(sha256(PDF) == PDF_SHA, "CHP-5.pdf changed since review")
    need(sha256(PAGE_IMAGE) == IMAGE_SHA, "p.131 page image changed since review")
    need(hashlib.sha256(segment_text.encode("utf-8")).hexdigest() == SEGMENT_SHA,
         "p.131 segment fingerprint changed")

    statements_path = TABLES / "book-statements.jsonl"
    statements, raw_statement_lines = read_jsonl(statements_path)
    by_id = {row["statement_id"]: row for row in statements}
    targets = [row for row in statements if row.get("segment_id") == SEGMENT]
    target_ids = {row["statement_id"] for row in targets}
    need(target_ids == set(RELATION_FLAGS), f"p.131 statement inventory changed: {sorted(target_ids ^ set(RELATION_FLAGS))}")
    for row in targets:
        need(row.get("original_quote", "") in segment_text, f"source quote moved: {row['statement_id']}")
        current = (row.get("qualifiers") or {}).get("relation_candidate")
        need(current is None or (row["statement_id"] == "st-chp5-p131-camillo-nephew-of-innocent-x" and current is True),
             f"unexpected prior classification: {row['statement_id']}={current}")
    need(set(RELATION_NOTES) == target_ids, "classification notes do not cover every existing statement")

    candidates_path = TABLES / "entity-candidates.csv"
    candidates, candidate_fields = read_csv(candidates_path)
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    new_candidate_ids = {r["candidate_id"] for r in NEW_CANDIDATES}
    need(not (new_candidate_ids & set(candidate_by_id)), "new candidate ID already exists")
    natural_keys = {(r["canonical_name"].strip().casefold(), r["suggested_type"].strip().casefold()) for r in candidates}
    for c in NEW_CANDIDATES:
        key = (c["canonical_name"].strip().casefold(), c["suggested_type"].strip().casefold())
        need(key not in natural_keys, f"duplicate candidate natural key: {c['canonical_name']}")
        natural_keys.add(key)

    mentions_path = TABLES / "mentions.csv"
    mentions, mention_fields = read_csv(mentions_path)
    mention_by_id = {r["mention_id"]: r for r in mentions}
    need(not ({m["mention_id"] for m in NEW_MENTIONS} & set(mention_by_id)), "new mention ID already exists")
    page_mentions = [r for r in mentions if r.get("segment_id") == SEGMENT]
    for r in page_mentions:
        start, end = int(r["start_char"]), int(r["end_char"])
        need(segment_text[start:end] == r["surface_form"], f"existing p.131 mention span mismatch: {r['mention_id']}")
    for r in NEW_MENTIONS:
        start, end = int(r["start_char"]), int(r["end_char"])
        need(segment_text[start:end] == r["surface_form"], f"new mention span mismatch: {r['mention_id']}")
    need("m-chp5-p131-0057" in mention_by_id and mention_by_id["m-chp5-p131-0057"]["candidate_id"] == "cand-6064",
         "unknown-patrons mention mapping changed")

    updates = {}
    for sid, relation in RELATION_FLAGS.items():
        q = dict(by_id[sid].get("qualifiers") or {})
        q["relation_candidate"] = relation
        q["relation_candidate_note"] = RELATION_NOTES[sid]
        updates[sid] = {"qualifiers": q}

    def update_row(sid: str, **fields) -> None:
        updates[sid].update(fields)

    update_row("st-chp5-p131-1636-transfer-to-barberini",
               qualifiers={**updates["st-chp5-p131-1636-transfer-to-barberini"]["qualifiers"],
                           "printed_reading_correction": {"ocr": "163 6", "print": "1636"},
                           "transaction_status": "transfer_on_compensation_understanding; payment_not_stated"})
    update_row("st-chp5-p131-1641-calabrian-church-commission",
               subject_candidate_id="cand-6068", object_candidate_id="cand-2369",
               predicate="commissioned_painting_from_artist",
               qualifiers={**updates["st-chp5-p131-1641-calabrian-church-commission"]["qualifiers"],
                           "mentioned_candidate_ids": ["cand-6068", "cand-2369", "cand-2370", "cand-6067", "cand-6072"],
                           "commissioned_work_candidate_id": "cand-2370", "completion_not_established": True})
    update_row("st-chp5-p131-1643-replacement-commission",
               subject_candidate_id="cand-4095", object_candidate_id="cand-2267",
               predicate="commissioned_by_princess_as_replacement_for_raphael_holy_family",
               qualifiers={**updates["st-chp5-p131-1643-replacement-commission"]["qualifiers"],
                           "mentioned_candidate_ids": ["cand-2267", "cand-4095", "cand-2101", "cand-1814", "cand-1819"],
                           "replacement_status": "decided_and_commissioned; earlier_sale_not_completed"})
    update_row("st-chp5-p131-camillo-nephew-of-innocent-x",
               qualifiers={**updates["st-chp5-p131-camillo-nephew-of-innocent-x"]["qualifiers"],
                           "printed_reading_correction": {"ocr": "Pamftli", "print": "Pamfili"}})
    update_row("st-chp5-p131-clerical-portraits",
               subject_candidate_id="cand-2369", object_candidate_id="cand-11798",
               predicate="drew_and_painted_portraits_of_clerics",
               qualifiers={**updates["st-chp5-p131-clerical-portraits"]["qualifiers"],
                           "mentioned_candidate_ids": ["cand-2369", "cand-11798", "cand-1831"]})
    update_row("st-chp5-p131-cozza-altarpiece",
               subject_candidate_id="cand-0867", object_candidate_id="cand-6068",
               predicate="employed_by_priests_for_altar_painting",
               qualifiers={**updates["st-chp5-p131-cozza-altarpiece"]["qualifiers"],
                           "mentioned_candidate_ids": ["cand-0867", "cand-6068", "cand-6069"]})
    update_row("st-chp5-p131-current-style-opposition",
               subject_candidate_id="cand-11797", object_candidate_id="cand-6073",
               qualifiers={**updates["st-chp5-p131-current-style-opposition"]["qualifiers"],
                           "mentioned_candidate_ids": ["cand-2369", "cand-11797", "cand-6073"]})
    update_row("st-chp5-p131-dominicans-decided-to-sell-raphael-holy-family",
               subject_candidate_id="cand-0941", object_candidate_id="cand-2101",
               predicate="planned_sale_of_raphael_holy_family",
               original_quote=exact(segment_text, "The Dominicans of Santa Sabina, anxious to raise money, had decided to sell a Raphael Holy Family in their possession"),
               qualifiers={**updates["st-chp5-p131-dominicans-decided-to-sell-raphael-holy-family"]["qualifiers"],
                           "claim": "The Dominicans of Santa Sabina, seeking money, decided to sell the Raphael Holy Family in their possession.",
                           "mentioned_candidate_ids": ["cand-0941", "cand-2101", "cand-3969", "cand-2098", "cand-1200"],
                           "planned_sale_not_completed": True, "buyer_offer_statement_id": "st-chp5-p131-giustiniani-offer"})
    update_row("st-chp5-p131-gigli-diary",
               qualifiers={**updates["st-chp5-p131-gigli-diary"]["qualifiers"],
                           "printed_reading_correction": {"ocr": "diEgently", "print": "diligently"}})
    update_row("st-chp5-p131-gigli-profile",
               qualifiers={**updates["st-chp5-p131-gigli-profile"]["qualifiers"],
                           "printed_reading_correction": {"ocr": "Giacinto GigE", "print": "Giacinto Gigli"}})
    update_row("st-chp5-p131-holy-family-pictures-and-prototypes",
               subject_candidate_id="cand-2369", object_candidate_id="cand-11797",
               predicate="produced_recurring_holy_family_picture_group",
               original_quote=exact(segment_text, "There he confined himself almost exclusively to pictures of tire Holy Family"),
               qualifiers={**updates["st-chp5-p131-holy-family-pictures-and-prototypes"]["qualifiers"],
                           "claim": "Haskell says Sassoferrato confined himself almost exclusively to pictures of the Holy Family.",
                           "mentioned_candidate_ids": ["cand-2369", "cand-11797", "cand-6071"],
                           "printed_reading_correction": {"ocr": "tire Holy Family", "print": "the Holy Family"},
                           "prototypes_statement_id": "st-chp5-p131-holy-family-prototypes"})
    update_row("st-chp5-p131-models",
               subject_candidate_id="cand-2369", object_candidate_id="cand-2098",
               predicate="modeled_his_practice_on",
               original_quote=exact(segment_text, "His models were Raphael, Annibale Carracci and\nDomenichino at his most austere"),
               qualifiers={**updates["st-chp5-p131-models"]["qualifiers"],
                           "claim": "Haskell names Raphael as one of Sassoferrato's models.",
                           "mentioned_candidate_ids": ["cand-2369", "cand-2098", "cand-0576", "cand-0932"],
                           "scalarized_model_list": True})
    update_row("st-chp5-p131-paid-one-hundred-scudi",
               subject_candidate_id="cand-2267", object_candidate_id="cand-2369",
               predicate="paid_artist_100_scudi_for_rosary_painting",
               qualifiers={**updates["st-chp5-p131-paid-one-hundred-scudi"]["qualifiers"],
                           "mentioned_candidate_ids": ["cand-2267", "cand-2369", "cand-4095"],
                           "amount": "100 scudi", "payment_for_work_candidate_id": "cand-4095"})
    update_row("st-chp5-p131-picture-reception-public-commissions",
               subject_candidate_id="cand-4095", object_candidate_id=None,
               predicate="work_evidently_did_not_please",
               original_quote=exact(segment_text, "Despite its great beauty the picture evidently did not please"),
               qualifiers={**updates["st-chp5-p131-picture-reception-public-commissions"]["qualifiers"],
                           "claim": "Haskell says the picture evidently did not please.",
                           "mentioned_candidate_ids": ["cand-4095"],
                           "split_statement_id": "st-chp5-p131-public-commissions-became-rare"})
    update_row("st-chp5-p131-princess-wife-of-camillo",
               qualifiers={**updates["st-chp5-p131-princess-wife-of-camillo"]["qualifiers"],
                           "printed_reading_correction": {"ocr": "Pamftli", "print": "Pamfili"}})
    update_row("st-chp5-p131-sassoferrato-location-and-career",
               subject_candidate_id="cand-2369", object_candidate_id="cand-4490",
               predicate="came_to_rome_from_native_marche_region",
               qualifiers={**updates["st-chp5-p131-sassoferrato-location-and-career"]["qualifiers"],
                           "mentioned_candidate_ids": ["cand-2369", "cand-4490", "cand-6058", "cand-0209"],
                           "origin_place_candidate_id": "cand-6058", "temporal_context_candidate_id": "cand-0209",
                           "printed_reading_correction": {"ocr": "tire Holy Family", "print": "the Holy Family"}})
    update_row("st-chp5-p131-shared-pupilage",
               subject_candidate_id="cand-0867", object_candidate_id="cand-0932",
               predicate="trained_by",
               qualifiers={**updates["st-chp5-p131-shared-pupilage"]["qualifiers"],
                           "claim": "Haskell says Cozza had been a pupil of Domenichino.",
                           "mentioned_candidate_ids": ["cand-0867", "cand-2369", "cand-0932"],
                           "scalarized_shared_pupilage": True})
    update_row("st-chp5-p131-unknown-patrons",
               subject_candidate_id="cand-2369", object_candidate_id="cand-11796",
               predicate="worked_for_unidentified_patron_group",
               qualifiers={**updates["st-chp5-p131-unknown-patrons"]["qualifiers"],
                           "mentioned_candidate_ids": ["cand-2369", "cand-11796", "cand-6075"]})

    new_model = next(s for s in NEW_STATEMENTS if s["statement_id"] == "st-chp5-p131-model-annibale-carracci")
    new_pupil = next(s for s in NEW_STATEMENTS if s["statement_id"] == "st-chp5-p131-sassoferrato-pupil-of-domenichino")
    # Expand the existing rows' cross-reference lists after all scalar statements are known.
    updates["st-chp5-p131-models"]["qualifiers"]["related_statement_ids"] = [
        "st-chp5-p131-model-annibale-carracci", "st-chp5-p131-model-domenichino"]
    updates["st-chp5-p131-shared-pupilage"]["qualifiers"]["related_statement_ids"] = [
        "st-chp5-p131-sassoferrato-pupil-of-domenichino"]

    new_statements = NEW_STATEMENTS
    existing_ids = set(by_id)
    new_ids = {s["statement_id"] for s in new_statements}
    need(len(new_ids) == len(new_statements) and not (new_ids & existing_ids), "new statement ID collision")
    for s in new_statements:
        if s["qualifiers"]["relation_candidate"]:
            need(s["subject_candidate_id"] and s["object_candidate_id"],
                 f"new true candidate missing endpoint: {s['statement_id']}")
    for sid, update in updates.items():
        if update["qualifiers"]["relation_candidate"]:
            row = by_id[sid]
            need(update.get("subject_candidate_id", row.get("subject_candidate_id")) and
                 update.get("object_candidate_id", row.get("object_candidate_id")),
                 f"true candidate missing endpoint: {sid}")

    mention_updates = {
        "m-chp5-p131-0057": {
            "candidate_id": "cand-11796",
            "note": "Unnamed patrons of Sassoferrato's work; distinct from the wider anonymous public in p.130 and the professional community Haskell only hypothesizes here.",
        }
    }
    return {
        "statements": statements, "raw_statement_lines": raw_statement_lines,
        "updates": updates, "new_statements": new_statements,
        "candidates": candidates, "candidate_fields": candidate_fields,
        "mentions": mentions, "mention_fields": mention_fields,
        "mention_updates": mention_updates, "new_mentions": NEW_MENTIONS,
        "existing_mentions": len(page_mentions),
    }


def render_jsonl(plan: dict) -> bytes:
    updates = plan["updates"]
    out = []
    for raw in plan["raw_statement_lines"]:
        if not raw.strip():
            out.append(raw)
            continue
        obj = json.loads(raw)
        update = updates.get(obj.get("statement_id"))
        if update:
            obj.update(update)
            ending = "\r\n" if raw.endswith("\r\n") else "\n" if raw.endswith("\n") else ""
            out.append(json.dumps(obj, ensure_ascii=False) + (ending or "\n"))
        else:
            out.append(raw)
    out.extend(json.dumps(row, ensure_ascii=False) + "\n" for row in plan["new_statements"])
    return "".join(out).encode("utf-8")


def render_csv(rows: list[dict], fields: list[str], updates: dict, key: str,
               new_rows: list[dict], bom: bool) -> bytes:
    prepared = []
    for source_row in rows:
        row = dict(source_row)
        row.update(updates.get(row.get(key), {}))
        prepared.append(row)
    prepared.extend(new_rows)
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="raise", lineterminator="\n")
    writer.writeheader()
    writer.writerows(prepared)
    content = buffer.getvalue().encode("utf-8")
    return (codecs.BOM_UTF8 + content) if bom else content


def atomic_write(path: Path, content: bytes) -> None:
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main() -> None:
    parser = argparse.ArgumentParser(description="Controlled S2 p.131 writeback; dry-run by default.")
    parser.add_argument("--apply", action="store_true", help="write the reviewed exact change set")
    args = parser.parse_args()
    plan = build_plan()
    statement_path = TABLES / "book-statements.jsonl"
    candidate_path = TABLES / "entity-candidates.csv"
    mention_path = TABLES / "mentions.csv"
    outputs = {
        statement_path: render_jsonl(plan),
        candidate_path: render_csv(plan["candidates"], plan["candidate_fields"], {}, "candidate_id",
                                  NEW_CANDIDATES, candidate_path.read_bytes().startswith(codecs.BOM_UTF8)),
        mention_path: render_csv(plan["mentions"], plan["mention_fields"], plan["mention_updates"], "mention_id",
                                 NEW_MENTIONS, mention_path.read_bytes().startswith(codecs.BOM_UTF8)),
    }
    true_count = sum(RELATION_FLAGS.values()) + sum(s["qualifiers"]["relation_candidate"] for s in NEW_STATEMENTS)
    total_count = len(RELATION_FLAGS) + len(NEW_STATEMENTS)
    print("S2 p.131 dry-run / exact plan")
    print(f"source sha256: {sha256(SOURCE)}")
    print(f"PDF sha256: {sha256(PDF)}")
    print(f"page image sha256: {sha256(PAGE_IMAGE)}")
    print(f"existing statements classified: {len(RELATION_FLAGS)}; added statements: {len(NEW_STATEMENTS)}")
    print(f"final page statements: {total_count} ({true_count} relation candidates, {total_count - true_count} non-relational)")
    print(f"new candidates: {len(NEW_CANDIDATES)}; new mentions: {len(NEW_MENTIONS)}; existing mentions checked: {plan['existing_mentions']}; one existing patron mention remapped")
    for path, content in outputs.items():
        print(f"{path.relative_to(ROOT)}: {sha256(path)} -> {hashlib.sha256(content).hexdigest()} ({len(content)} bytes)")
    if not args.apply:
        print("dry-run only; no tables written")
        return

    backups = {}
    suffix = ".bak-s2-chp5-p131-20261012"
    for path in outputs:
        backup = path.with_name(path.name + suffix)
        need(not backup.exists(), f"recovery copy already exists; refusing overwrite: {backup.name}")
        shutil.copy2(path, backup)
        need(sha256(backup) == EXPECTED[path.name], f"recovery copy hash mismatch: {backup.name}")
        backups[path] = backup
    for path, content in outputs.items():
        atomic_write(path, content)
    for path in outputs:
        print(f"applied {path.relative_to(ROOT)} sha256={sha256(path)} backup={backups[path].name}")
    print("apply complete")


if __name__ == "__main__":
    main()
