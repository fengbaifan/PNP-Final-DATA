from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
SOURCE = ROOT / "02-sources/02-Markdown/13_CHP-13_intro.md"
PDF = ROOT / "02-sources/01-book/CHP-13.pdf"
SEGMENTS = TABLES / "segments.jsonl"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
P342 = "chp-13:13_CHP-13_intro:l98-105"
P343 = "chp-13:13_CHP-13_intro:l107-114"
P343_SHA = "743ef09cf9ff747cb574bdd900aabff98a8567d461a268ca362c5aa3dfd5ef71"
BACKUP_SUFFIX = ".bak-s2-ch13-p343-semantic-review-20261014"

EXPECTED_HASHES = {
    SOURCE: "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8",
    PDF: "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc",
    STATEMENTS: "0ea81e0824492a9ec87de1a952b6f803c48e3093db4a9cab8e0c78d5bc4e07ce",
    CANDIDATES: "36ac91154bdd308d1f990c643b9d211649e343ee279ab6970ccb09e945503fe3",
    MENTIONS: "cbac853854d77cdb22e3aa5373ea5c97c07b1463a1a9d7ed304458e34574beb4",
}

UNSET_DECISIONS = {
    "st-chp13-p343-algarotti_retained_style_synthesis_but_worried": True,
    "st-chp13-p343-haskell_on_woodcuts_and_scholarly_fanciful_taste": True,
    "st-chp13-p343-haskell_places_zanetti_in_first_print_group": True,
    "st-chp13-p343-rococo_and_neo_classical_not_in_conflict": True,
    "st-chp13-p343-younger_zanetti_on_general_public_print_preferences": True,
    "st-chp13-p343-younger_zanetti_on_lively_print_preferences": True,
    "st-chp13-p343-zanetti_completeness_and_selective_preferences": True,
    "st-chp13-p343-zanetti_disregarded_multiple_examples": True,
    "st-chp13-p343-zanetti_exchanged_spares_for_missing_print": True,
    "st-chp13-p343-zanetti_felt_no_style_qualms": True,
    "st-chp13-p343-zanetti_never_seen_giulio_romano_prints": True,
    "st-chp13-p343-zanetti_passion_for_antiquity_and_tiepolo_etchings": True,
    "st-chp13-p343-zanetti_preferred_mannerist_picturesque_works": True,
    "st-chp13-p343-zanetti_preferred_single_fine_copy": True,
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_atomic(path: Path, data: bytes) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def jsonl_bytes(rows: list[dict]) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")


def csv_bytes(fields: list[str], rows: list[dict]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return ("\ufeff" + stream.getvalue()).encode("utf-8")


def add_statement(template: dict, statement_id: str, subject: str | None, obj: str | None,
                  predicate: str, claim: str, quote: str, qualification: str,
                  mentioned: list[str], relation: bool, start: int = 108,
                  end: int = 108, speaker: str = "Haskell",
                  ocr: list[dict] | None = None) -> dict:
    row = json.loads(json.dumps(template, ensure_ascii=False))
    row["statement_id"] = statement_id
    row["segment_id"] = P343
    row["subject_candidate_id"] = subject
    row["object_candidate_id"] = obj
    row["predicate"] = predicate
    row["original_quote"] = quote
    q = row.setdefault("qualifiers", {})
    q.update({
        "source_line_start": start,
        "source_line_end": end,
        "printed_page": 343,
        "pdf_physical_page": 12,
        "claim": claim,
        "speaker": speaker,
        "text_layer": "authorial narrative" if speaker == "Haskell" else "quoted letter as reported by Haskell",
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "ocr_corrections": ocr or [],
        "relation_candidate": relation,
    })
    for key in ("footnote_refs", "footnote_marker", "footnote_printed_page", "footnote_text_pending",
                "footnote_body_link_status", "cross_reference_segments", "footnote_note_statement_ids"):
        if key in q and key in row:
            row[key] = json.loads(json.dumps(q[key], ensure_ascii=False))
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after all prechecks pass")
    args = parser.parse_args()

    for path, expected in EXPECTED_HASHES.items():
        actual = digest(path)
        if actual != expected:
            raise SystemExit(f"precheck failed: {path.relative_to(ROOT)} sha256={actual}")

    segment_rows = read_jsonl(SEGMENTS)
    expected_segments = {
        P342: "784beac28408e154b50a6afebd080e5c3de774cd0bd6bc8093bfbee712c4c0a0",
        P343: P343_SHA,
    }
    for segment_id, expected in expected_segments.items():
        matches = [row for row in segment_rows if row.get("segment_id") == segment_id]
        if len(matches) != 1 or matches[0].get("sha256") != expected:
            raise SystemExit(f"precheck failed: segment identity/hash mismatch for {segment_id}")

    statements = read_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("precheck failed: duplicate statement IDs")
    p342_rows = [row for row in statements if row.get("segment_id") == P342]
    p343_rows = [row for row in statements if row.get("segment_id") == P343]
    if len(p342_rows) != 27 or len(p343_rows) != 24:
        raise SystemExit(f"precheck failed: expected p342=27 and p343=24, got {len(p342_rows)} and {len(p343_rows)}")
    unset = {row["statement_id"] for row in p343_rows if row.get("qualifiers", {}).get("relation_candidate") is None}
    if unset != set(UNSET_DECISIONS):
        raise SystemExit(f"precheck failed: p343 unset statement IDs changed: {sorted(unset)}")

    candidate_fields: list[str]
    with CANDIDATES.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        candidate_fields = list(reader.fieldnames or [])
        candidates = list(reader)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    if "cand-12173" in candidate_by_id or "cand-12174" in candidate_by_id:
        raise SystemExit("precheck failed: planned candidate ID already exists")
    if "cand-10090" not in candidate_by_id:
        raise SystemExit("precheck failed: p342 cross-page print candidate is absent")

    mention_fields: list[str]
    with MENTIONS.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        mention_fields = list(reader.fieldnames or [])
        mentions = list(reader)
    mention_by_id = {row["mention_id"]: row for row in mentions}
    new_mention_ids = {"m-s2-ch13-p343-060", "m-s2-ch13-p343-061", "m-s2-ch13-p343-062"}
    if new_mention_ids & mention_by_id.keys():
        raise SystemExit("precheck failed: planned mention ID already exists")

    local_text = "\n".join(SOURCE.read_text(encoding="utf-8").splitlines()[106:114])
    for row in mentions:
        if row.get("segment_id") != P343:
            continue
        start, end = int(row["start_char"]), int(row["end_char"])
        if local_text[start:end] != row["surface_form"]:
            raise SystemExit(f"precheck failed: p343 mention span mismatch for {row['mention_id']}")
    for surface, start, end in (("these", 102, 107), ("these men", 2444, 2453), ("the plates", 2033, 2043)):
        if local_text[start:end] != surface:
            raise SystemExit(f"precheck failed: planned mention span mismatch for {surface}")

    # Resolve the two page-spanning quoted references without inferring ownership.
    p342_exception = by_id["st-chp13-p342-zanetti_1752_rare_print_exception_fragment"]
    p342_exception["qualifiers"]["qualification"] = (
        "The quotation continues on p.343: Zanetti says he had never seen these items in Italy, Holland, France, or England. "
        "This is his self-report; do not infer ownership or an independent account of availability."
    )
    p342_exception["qualifiers"]["cross_reference_segments"] = [P343]
    p342_exception["cross_reference_segments"] = [P343]

    # Add source-defined collective and printing-plate candidates; keep the matrix distinct from the impressions.
    candidates.extend([
        {
            "candidate_id": "cand-12173", "index_entry_id": "", "canonical_name": "Zanetti and similar European amateurs whose taste combined scholarly and fanciful elements",
            "index_page_range": "", "suggested_type": "term", "status": "open", "index_source_file": "", "sub_entry": "",
            "detail": "The source describes these amateurs as similar to Zanetti and identifies them as the antecedent of 'these men' in the statement that Rococo and neo-classical styles were not in conflict. Members are unnamed.",
            "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{P343}#L113",
        },
        {
            "candidate_id": "cand-12174", "index_entry_id": "", "canonical_name": "Printing plates used to produce Zanetti's chiaroscuro woodcut set",
            "index_page_range": "", "suggested_type": "", "status": "open", "index_source_file": "", "sub_entry": "",
            "detail": "The source says Zanetti destroyed these plates after producing the woodcut set. The taxonomy does not define a separate printing-matrix type; keep these distinct from the finished woodcuts in cand-2853.",
            "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{P343}#L112",
        },
    ])
    candidate_by_id["cand-10090"]["detail"] = (
        "The p.342 quotation continues on p.343: Zanetti says he had never seen this dish and the Giulio Romano prints in Italy, Holland, France, or England. "
        "This remains his quoted self-report and does not establish ownership."
    )

    mention_updates = {
        "m-s2-ch13-p343-005": "The plural 'these' refers to both cand-10091 and the Annibale Bacchanal dish cand-10090; the corresponding dish mention is recorded separately at this same span.",
        "m-s2-ch13-p343-054": "The apparent contradictions concern the Rococo and neo-classical synthesis represented by cand-10102.",
    }
    for mention_id, note in mention_updates.items():
        if mention_id not in mention_by_id:
            raise SystemExit(f"precheck failed: expected mention missing: {mention_id}")
        mention_by_id[mention_id]["note"] = note
    mention_by_id["m-s2-ch13-p343-054"]["candidate_id"] = "cand-10102"
    mentions.extend([
        {"mention_id": "m-s2-ch13-p343-060", "segment_id": P343, "candidate_id": "cand-10090", "surface_form": "these", "start_char": "102", "end_char": "107", "note": "Cross-page plural anaphor also refers to the Annibale Bacchanal dish named at the end of p.342."},
        {"mention_id": "m-s2-ch13-p343-061", "segment_id": P343, "candidate_id": "cand-12173", "surface_form": "these men", "start_char": "2444", "end_char": "2453", "note": "Anaphoric group: Zanetti and the similar European amateurs whose scholarly/fanciful taste is described in the preceding sentence."},
        {"mention_id": "m-s2-ch13-p343-062", "segment_id": P343, "candidate_id": "cand-12174", "surface_form": "the plates", "start_char": "2033", "end_char": "2043", "note": "The physical printing plates destroyed after production of the woodcut set; distinct from the finished works in cand-2853."},
    ])

    def revise(statement_id: str, *, subject: str | None, obj: str | None, predicate: str,
               claim: str, quote: str, qualification: str, mentioned: list[str],
               relation: bool, start: int, end: int, ocr: list[dict] | None = None,
               cross_refs: list[str] | None = None) -> None:
        row = by_id[statement_id]
        row["subject_candidate_id"] = subject
        row["object_candidate_id"] = obj
        row["predicate"] = predicate
        row["original_quote"] = quote
        q = row.setdefault("qualifiers", {})
        q.update({
            "source_line_start": start, "source_line_end": end,
            "claim": claim, "qualification": qualification,
            "mentioned_candidate_ids": mentioned,
            "relation_candidate": relation,
        })
        if ocr is not None:
            q["ocr_corrections"] = ocr
        if cross_refs is not None:
            q["cross_reference_segments"] = cross_refs
            row["cross_reference_segments"] = cross_refs

    # Split and classify p.343 statements, repairing source roles and anaphoric endpoints.
    revise(
        "st-chp13-p343-algarotti_retained_style_synthesis_but_worried",
        subject="cand-0041", obj="cand-10102", predicate="retained_synthesis_of_rococo_and_neo_classical_styles",
        claim="Haskell says Algarotti was among the last to retain the synthesis of Rococo and neo-classical styles.",
        quote="Francesco Algarotti was one of the last men to retain this synthesis of opposing styles",
        qualification="Haskell's description; 'this synthesis' refers to the linked style pair. Algarotti's theoretical disposition and concern about contradictions are recorded separately.",
        mentioned=["cand-0041", "cand-10102"], relation=True, start=113, end=113,
    )
    revise(
        "st-chp13-p343-haskell_on_woodcuts_and_scholarly_fanciful_taste",
        subject="cand-2853", obj="cand-12173", predicate="woodcuts_reflected_scholarly_fanciful_taste_of_zanetti_and_similar_amateurs",
        claim="Haskell says the woodcuts faithfully reflected the combination of scholarly and fanciful elements in Zanetti's taste and that of similar European amateurs.",
        quote="they are important because they reflect so faithfully that combination of the scholarly and the fanciful which was such a feature of Zanetti\u2019s taste and that of similar amateurs elsewhere in Europe.",
        qualification="This records Haskell's stated interpretive significance of the woodcuts; their separate aesthetic evaluation is recorded as a non-relational statement.",
        mentioned=["cand-2853", "cand-2838", "cand-12173"], relation=True, start=112, end=113,
    )
    revise(
        "st-chp13-p343-haskell_places_zanetti_in_first_print_group",
        subject="cand-2838", obj="cand-10099", predicate="belonged_to_group_preferring_lively_broad_stroke_prints",
        claim="Haskell concludes that Zanetti belonged to the first of the two print-preference groups described by the younger namesake.",
        quote="There can be no doubt that Zanetti belonged in the first of these two groups.",
        qualification="The pronoun resolves to the previously described artists and expert-connoisseur collectors who preferred lively, broad-stroke prints.",
        mentioned=["cand-2838", "cand-10099"], relation=True, start=111, end=111,
    )
    revise(
        "st-chp13-p343-rococo_and_neo_classical_not_in_conflict",
        subject="cand-12173", obj="cand-10102", predicate="styles_not_in_conflict_for_zanetti_and_similar_amateurs",
        claim="For Zanetti and similar European amateurs whose taste combined scholarly and fanciful elements, Haskell says Rococo and neo-classical styles were not in conflict.",
        quote="For these men the rococo and the neo-classical were not in conflict.",
        qualification="'These men' refers to Zanetti and the similar amateurs in the immediately preceding sentence; their individual identities are not given.",
        mentioned=["cand-12173", "cand-2838", "cand-10102"], relation=True, start=113, end=113,
    )
    revise(
        "st-chp13-p343-younger_zanetti_on_general_public_print_preferences",
        subject="cand-2856", obj="cand-10100", predicate="said_general_public_preferred_carefully_finished_high_contrast_prints",
        claim="The younger A. M. Zanetti says the general public likes carefully finished prints with strong light-and-shade contrasts that strike the imagination at first sight.",
        quote="On the other hand the general public likes carefully finished prints, and especially those with strong contrasts of light and shade, which strike the imagination at first sight.",
        qualification="This is the younger namesake's quoted account of the general public's preference, reported by Haskell.",
        mentioned=["cand-2856", "cand-10100"], relation=True, start=111, end=111,
    )
    revise(
        "st-chp13-p343-younger_zanetti_on_lively_print_preferences",
        subject="cand-2856", obj="cand-10099", predicate="said_artists_and_expert_connoisseurs_preferred_lively_broad_stroke_prints",
        claim="The younger A. M. Zanetti says artists and collectors regarded as perfect connoisseurs like prints engraved with speed, liveliness, and broad strokes.",
        quote="\u2018There are people\u2019, wrote his namesake the younger A. M. Zanetti,2 \u2018who like prints engraved with great speed and liveliness and with broad strokes. Such people are artists and, with them, those collectors who are held to be perfect connoisseurs.",
        qualification="This is the younger namesake's quoted account, reported by Haskell; it does not identify individual artists or collectors.",
        mentioned=["cand-2856", "cand-10099"], relation=True, start=111, end=111,
    )
    revise(
        "st-chp13-p343-zanetti_completeness_and_selective_preferences",
        subject="cand-2838", obj="cand-2850", predicate="aimed_for_completeness_in_print_collection",
        claim="Haskell says completeness was the principal aim of Zanetti's print collection.",
        quote="completeness was his principal aim",
        qualification="The following preferences for particular kinds of prints are recorded in the separate statement st-chp13-p343-zanetti_preferred_mannerist_picturesque_works.",
        mentioned=["cand-2838", "cand-2850"], relation=True, start=109, end=109,
    )
    revise(
        "st-chp13-p343-zanetti_disregarded_multiple_examples",
        subject="cand-2838", obj="cand-2850", predicate="took_little_account_of_multiple_examples_of_a_print",
        claim="Zanetti says that when he owned several different examples of one print, even a rare one, he took little account of them.",
        quote="And so, when I have owned several different examples of one, even a rare one, I have taken little account of it.",
        qualification="This is Zanetti's self-report in the 1752 letter; the print and its copies remain unidentified.",
        mentioned=["cand-2838", "cand-2850"], relation=True, start=108, end=108,
    )
    revise(
        "st-chp13-p343-zanetti_exchanged_spares_for_missing_print",
        subject="cand-2838", obj="cand-2850", predicate="exchanged_spare_print_copies_for_missing_prints",
        claim="Zanetti says he often gave away his spare copies for a print missing from his collection that he had been unable to buy, and frequently made such exchanges.",
        quote="And for one little print missing from my collection which I have been unable to buy I have often given all the spare copies I have owned. And to tell you the truth I have frequently made mad exchanges of this kind.",
        qualification="This is Zanetti's self-report in the 1752 letter. The missing print, exchange partners, and individual copies are unidentified.",
        mentioned=["cand-2838", "cand-2850"], relation=True, start=108, end=108,
    )
    revise(
        "st-chp13-p343-zanetti_felt_no_style_qualms",
        subject="cand-2838", obj="cand-10102", predicate="felt_no_qualms_about_apparent_style_contradictions",
        claim="Haskell says Zanetti felt no qualms about the apparent contradictions in his taste between Rococo and neo-classical styles.",
        quote="Zanetti felt no such qualms.",
        qualification="'Such qualms' refers to the apparent contradictions in taste described in the preceding sentence.",
        mentioned=["cand-2838", "cand-10102"], relation=True, start=113, end=113,
    )
    revise(
        "st-chp13-p343-zanetti_never_seen_giulio_romano_prints",
        subject="cand-2838", obj="cand-10091", predicate="reported_never_having_seen_giulio_romano_prints",
        claim="In the 1752 quotation, Zanetti says he had never seen the Giulio Romano prints engraved by Marc\u2019Antonio with Aretino\u2019s sonnets in Italy, Holland, France, or England.",
        quote="prints of Giulio Romano engraved by Marc\u2019Antonio with Aretino\u2019s sonnets. I have never seen these in all my life—either in Italy, or in Holland, France or England.",
        qualification="The plural 'these' refers to both the Giulio Romano prints and the Annibale Bacchanal dish named across the p.342 page break. This statement isolates the prints; Zanetti's self-report is not independently verified.",
        mentioned=["cand-2838", "cand-10090", "cand-10091"], relation=True, start=108, end=108,
        ocr=[{"source_line": 108, "ocr": "Aretino\u2019s.sonnets", "print": "Aretino\u2019s sonnets", "basis": "CHP-13.pdf physical page 12."}],
        cross_refs=[P342],
    )
    revise(
        "st-chp13-p343-zanetti_passion_for_antiquity_and_tiepolo_etchings",
        subject="cand-2838", obj="cand-10103", predicate="was_just_as_enthusiastic_about_tiepolo_etchings",
        claim="Haskell says Zanetti was just as enthusiastic about Tiepolo's etchings as he was passionate about antiquity.",
        quote="but he was just as enthusiastic about the etchings of Tiepolo",
        qualification="This records Haskell's comparison of Zanetti's interest in antiquity and in Tiepolo's etchings; the following praise is a separate quotation.",
        mentioned=["cand-2838", "cand-10103"], relation=True, start=113, end=113,
        ocr=[{"source_line": 113, "ocr": "Zanetti, had", "print": "Zanetti had", "basis": "CHP-13.pdf physical page 12."}],
    )
    revise(
        "st-chp13-p343-zanetti_preferred_mannerist_picturesque_works",
        subject="cand-2838", obj="cand-10095", predicate="preferred_mannerist_and_picturesque_works_resembling_rococo",
        claim="Haskell says Zanetti particularly preferred Mannerist and picturesque works that most closely resembled the rococo.",
        quote="above all for those Mannerist and \u2018picturesque\u2019 works which bore the closest resemblance to the rococo",
        qualification="This is Haskell's account of Zanetti's print preferences; no individual print titles are supplied here.",
        mentioned=["cand-2838", "cand-10095"], relation=True, start=109, end=110,
    )
    revise(
        "st-chp13-p343-zanetti_preferred_single_fine_copy",
        subject="cand-2838", obj="cand-2850", predicate="preferred_one_fine_copy_over_multiple_copies",
        claim="Zanetti says he considered one fine copy sufficient and did not share the showy collectors' habit of boasting about several copies of a rare print.",
        quote="but for me it is enough to have a single fine copy—for I am not one of those collectors who make a great flourish and boast of having three or four or even more copies of a rare print.",
        qualification="This is Zanetti's self-description in the 1752 letter; it does not establish the identities of the collectors he contrasts himself with.",
        mentioned=["cand-2838", "cand-2850"], relation=True, start=108, end=108,
    )
    revise(
        "st-chp13-p343-zanetti_destroyed_plates_and_dedicated_woodcut_set",
        subject="cand-2853", obj="cand-10094", predicate="woodcut_set_dedicated_to_prince_of_liechtenstein",
        claim="Zanetti dedicated the woodcut set as a whole to the Prince of Liechtenstein.",
        quote="He then destroyed the plates and dedicated the set as a whole to the Prince of Liechtenstein,",
        qualification="This statement records the dedication and its recipient. The destruction of the distinct printing plates is recorded separately.",
        mentioned=["cand-2838", "cand-2853", "cand-10094"], relation=True, start=112, end=112,
    )
    revise(
        "st-chp13-p343-zanetti_dedicated_individual_sheets_to_friends",
        subject="cand-2853", obj="cand-10101", predicate="individual_woodcut_sheets_dedicated_to_english_french_and_venetian_friends",
        claim="Individual sheets were dedicated to English, French, and Venetian friends.",
        quote="while individual sheets were dedicated to English, French and Venetian friends.",
        qualification="The source does not name the friends or identify which individual sheet went to each recipient.",
        mentioned=["cand-2838", "cand-2853", "cand-10101"], relation=True, start=112, end=112,
    )
    # S0 contains several spacing and punctuation OCR artifacts verified against the page image.
    revise(
        "st-chp13-p343-zanetti_bought_rembrandt_callot_prints_abroad",
        subject="cand-2838", obj="cand-10097", predicate="bought_prints_by_rembrandt_and_callot_on_foreign_travels",
        claim="Zanetti bought prints by Rembrandt and Callot during his foreign travels.",
        quote="Rembrandt and Callot whom he bought on his foreign travels;",
        qualification="Haskell identifies the artists and says Zanetti bought their prints during foreign travel; the individual prints are not identified.",
        mentioned=["cand-2838", "cand-10097", "cand-2117", "cand-0482"], relation=True, start=111, end=111,
        ocr=[
            {"source_line": 111, "ocr": "Rembrandtand", "print": "Rembrandt and", "basis": "CHP-13.pdf physical page 12."},
            {"source_line": 111, "ocr": "whomhe", "print": "whom he", "basis": "CHP-13.pdf physical page 12."},
        ],
    )
    revise(
        "st-chp13-p343-zanetti_revived_technique_and_made_about_fifty_cuts",
        subject="cand-2838", obj="cand-2853", predicate="revived_chiaroscuro_woodcut_technique_in_london_and_produced_about_fifty_cuts",
        claim="During his stay in London, Zanetti revived the sixteenth-century chiaroscuro woodcut technique and produced about fifty cuts, mostly copied or adapted from his Parmigianino drawings.",
        quote="He revived this technique, which had been familiar to sixteenth-century artists, during his stay in London, and he produced about fifty cuts in all, mostly copied or adapted from his Parmigianino drawings.",
        qualification="The count is approximate; the source does not list the individual cuts.",
        mentioned=["cand-2838", "cand-2853", "cand-1422", "cand-1839"], relation=True, start=112, end=112,
        ocr=[
            {"source_line": 112, "ocr": "He - revived", "print": "He revived", "basis": "CHP-13.pdf physical page 12."},
            {"source_line": 112, "ocr": "his \" stay", "print": "his stay", "basis": "CHP-13.pdf physical page 12."},
        ],
    )

    # Add atomic statements for the resolved cross-page referent and previously bundled clauses.
    template = by_id["st-chp13-p343-zanetti_never_seen_giulio_romano_prints"]
    additions = [
        add_statement(
            template, "st-chp13-p343-zanetti_never_seen_annibale_bacchanal_dish",
            "cand-2838", "cand-10090", "reported_never_having_seen_annibale_bacchanal_dish",
            "In the 1752 quotation, Zanetti says he had never seen the Annibale Bacchanal dish in Italy, Holland, France, or England.",
            "prints of Giulio Romano engraved by Marc\u2019Antonio with Aretino\u2019s sonnets. I have never seen these in all my life—either in Italy, or in Holland, France or England.",
            "The plural 'these' also refers to the dish named on p.342; this is Zanetti's self-report, not independent verification.",
            ["cand-2838", "cand-10090", "cand-10091"], True, 108, 108,
            speaker="Zanetti, as quoted by Haskell",
            ocr=[{"source_line": 108, "ocr": "Aretino\u2019s.sonnets", "print": "Aretino\u2019s sonnets", "basis": "CHP-13.pdf physical page 12."}],
        ),
        add_statement(
            template, "st-chp13-p343-algarotti_worried_about_style_contradictions",
            "cand-0041", "cand-10102", "more_theoretical_cast_of_mind_worried_about_apparent_taste_contradictions",
            "Haskell says Algarotti's more theoretical cast of mind made him more worried by apparent contradictions in his taste.",
            "but being of a more theoretical cast of mind, he was more worried by apparent contradictions in his taste.",
            "Haskell's comparison is retained as written; the sentence does not name another comparator explicitly.",
            ["cand-0041", "cand-10102"], True, 113, 113,
        ),
        add_statement(
            template, "st-chp13-p343-woodcuts_not_very_attractive_as_works_of_art",
            "cand-2853", None, "woodcuts_not_very_attractive_as_works_of_art",
            "Haskell says the woodcuts were not very attractive as works of art.",
            "As works of art these are not very attractive",
            "This is Haskell's aesthetic judgment, kept separate from the following claim about what the woodcuts reflect.",
            ["cand-2853"], False, 112, 112,
        ),
        add_statement(
            template, "st-chp13-p343-zanetti_had_passion_for_antiquity",
            "cand-2838", None, "had_a_passion_for_antiquity",
            "Haskell says Zanetti had a passion for antiquity.",
            "Zanetti had a passion for antiquity",
            "This is a biographical characterization; the separate enthusiasm for Tiepolo's etchings is recorded independently.",
            ["cand-2838"], False, 113, 113,
            ocr=[{"source_line": 113, "ocr": "Zanetti, had", "print": "Zanetti had", "basis": "CHP-13.pdf physical page 12."}],
        ),
        add_statement(
            template, "st-chp13-p343-zanetti_destroyed_printing_plates",
            "cand-2838", "cand-12174", "destroyed_printing_plates_for_chiaroscuro_woodcuts",
            "Haskell says Zanetti destroyed the printing plates used for the described chiaroscuro woodcut set.",
            "He then destroyed the plates",
            "The plates are the physical printing matrices, distinct from the finished woodcuts in cand-2853.",
            ["cand-2838", "cand-12174", "cand-2853"], True, 112, 112,
        ),
    ]
    additions[0]["qualifiers"]["cross_reference_segments"] = [P342]
    additions[0]["cross_reference_segments"] = [P342]
    statements.extend(additions)

    if len([row for row in statements if row.get("segment_id") == P343]) != 29:
        raise SystemExit("precheck failed: expected 29 final p343 statements")
    if any(row.get("qualifiers", {}).get("relation_candidate") is None for row in statements if row.get("segment_id") == P343):
        raise SystemExit("precheck failed: p343 still has unset relation_candidate values")
    normalize = lambda value: re.sub(r"\s+", " ", value).strip()
    for row in (item for item in statements if item.get("segment_id") == P343):
        corrected_source = local_text
        for correction in row.get("qualifiers", {}).get("ocr_corrections", []):
            corrected_source = corrected_source.replace(correction.get("ocr", ""), correction.get("print", ""))
        if normalize(row.get("original_quote", "")) not in normalize(corrected_source):
            raise SystemExit(f"precheck failed: quote does not match S0/page correction for {row['statement_id']}")
    if len(candidates) != len(candidate_by_id) + 2 or len(mentions) != len(mention_by_id) + 3:
        raise SystemExit("precheck failed: candidate or mention additions do not match plan")

    print(f"segment={P343}; source_sha256={P343_SHA}; base_statements=24; added_statements={len(additions)}; final=29")
    print("decisions: unset statements classified; source OCR and endpoints corrected; cross-page plural referent split into two quoted claims")
    print("new candidates: cand-12173 (unnamed amateur group, term); cand-12174 (printing plates, type pending)")
    print("new mentions: 3; no KU or S6 relation changes")
    print("p343 classification", {str(v): sum(row.get("qualifiers", {}).get("relation_candidate") is v for row in statements if row.get("segment_id") == P343) for v in (True, False, None)})
    if not args.apply:
        print("dry-run: no files changed")
        return

    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in (STATEMENTS, CANDIDATES, MENTIONS)]
    if any(path.exists() for path in backups):
        raise SystemExit("refusing to overwrite an existing recovery copy")
    for original, backup in zip((STATEMENTS, CANDIDATES, MENTIONS), backups):
        shutil.copy2(original, backup)

    write_atomic(STATEMENTS, jsonl_bytes(statements))
    write_atomic(CANDIDATES, csv_bytes(candidate_fields, candidates))
    write_atomic(MENTIONS, csv_bytes(mention_fields, mentions))

    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        print(f"{path.relative_to(ROOT)} sha256={digest(path)}")
    print("APPLIED. Recovery copies saved for statements, candidates, and mentions.")


if __name__ == "__main__":
    main()
