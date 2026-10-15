from __future__ import annotations

import argparse
import codecs
import copy
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "05_CHP-5_sec_iii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-5.pdf"
PAGE_IMAGE = PROCESS / "p134_page_review_20261012.png"
SOURCE_FILE = "02-sources/02-Markdown/05_CHP-5_sec_iii.md"
BODY_SEGMENT = "chp-5:05_CHP-5_sec_iii:l20-26"
NOTES_SEGMENT = "chp-5:05_CHP-5_sec_iii:l126-165"

EXPECTED = {
    "book-statements.jsonl": "b0163b24ffdacc3871e086b5df79380eccf4f3d87aeaaf9fd76b6b3f72e45b81",
    "entity-candidates.csv": "e0d5ccdb53d6f3b7a8d69ec334467745c75310249c2e32f2ca51eee7391a969e",
    "mentions.csv": "f6403bd6b6f81169f5cb05c3d0d95f4e523c8e7f5bbab16edb7535d2c9b12eae",
}
SOURCE_SHA = "9b095b1a93570102ad2cdb117580f2fbeccd2ff017033a2f66557c58a0d1ef0a"
PDF_SHA = "f63dca79808fde73ba10aa9414fef89bc8ca5e77ed829b2d5c86f23719e0674a"
IMAGE_SHA = "54d3bacbe3e32303bf5a23dfba599ca7282233f6a5de1485e750e760ce414a58"
BODY_SHA = "75ca5d81ada4ae3a81e8096bfb49752c7db39763799d21e2c21d77abd8a507c3"

BODY_IDS = {
    "st-chp5-p134-annibale-beaneater-and-drawings",
    "st-chp5-p134-bassano-caravaggio-precedents",
    "st-chp5-p134-caravaggio-followers-and-picaresque-mode",
    "st-chp5-p134-caravaggio-later-religious-scenes",
    "st-chp5-p134-caravaggio-no-secular-ordinary-work-painting",
    "st-chp5-p134-caravaggio-proletarian-models-and-taste",
    "st-chp5-p134-caravaggio-revolution-and-prominence-of-poor",
    "st-chp5-p134-doni-shepherd-quotation-closure",
    "st-chp5-p134-expanding-backgrounds-and-picturesque-poor",
    "st-chp5-p134-good-poor-and-small-scale",
    "st-chp5-p134-passeri-small-figures",
    "st-chp5-p134-rosa-poem-protest",
    "st-chp5-p134-rosa-quote-translation-and-limit",
    "st-chp5-p134-van-laer-new-material",
}
NOTE_IDS = {
    "st-chp5-notes-l130-doni-pastoral-quote",
    "st-chp5-notes-l131-rosa-della-pittura",
    "st-chp5-notes-l132-passeri-p72",
    "st-chp5-notes-l133-doni-quote-continuation",
}

RELATION_NOTE = "Source-grounded S2 relation candidate only; no formal S6 edge is created."
NON_RELATION_NOTE = "Source claim retained in S2; no formal entity relation is proposed."


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def read_csv(path: Path) -> tuple[list[dict], list[str], bool]:
    raw = path.read_bytes()
    bom = raw.startswith(codecs.BOM_UTF8)
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return list(reader), list(reader.fieldnames or []), bom


def render_csv(rows: list[dict], fields: list[str], bom: bool) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="raise", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    data = buffer.getvalue().encode("utf-8")
    return codecs.BOM_UTF8 + data if bom else data


def atomic_write(path: Path, data: bytes) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def citation_statement(statement_id: str, object_id: str, claim: str, quote: str,
                       source_line: int, body_ids: list[str], qualification: str) -> dict:
    return {
        "statement_id": statement_id,
        "segment_id": NOTES_SEGMENT,
        "subject_candidate_id": "cand-2962",
        "object_candidate_id": object_id,
        "predicate": "cites",
        "qualifiers": {
            "source_line_start": source_line,
            "source_line_end": source_line,
            "claim": claim,
            "speaker": "Haskell",
            "text_layer": "bibliographic pointer",
            "print_page": "134",
            "pdf_physical_page": 15,
            "qualification": qualification,
            "footnote_segment": NOTES_SEGMENT,
            "footnote_marker": 1,
            "linked_body_statement_ids": body_ids,
            "related_segment": BODY_SEGMENT,
            "related_source_lines": [21],
            "citation_body_statement_ids": body_ids,
            "footnote_body_link_status": "linked",
            "relation_candidate": True,
            "relation_candidate_note": (
                "S2 cites candidate: the footnote explicitly cites this archive from Haskell's book. "
                "The citation does not independently validate the quoted claim; no formal S6 edge is created."
            ),
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_FILE,
    }


def source_statement(statement_id: str, subject: str | None, obj: str | None,
                     predicate: str, line: int, claim: str, quote: str,
                     mentioned: list[str], qualification: str, relation: bool,
                     speaker: str = "Haskell", text_layer: str = "authorial narration",
                     **extra) -> dict:
    relation_note = RELATION_NOTE if relation else NON_RELATION_NOTE
    qualifiers = {
        "source_line_start": line,
        "source_line_end": line,
        "printed_page": 134,
        "pdf_physical_page": 15,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation,
        "relation_candidate_note": relation_note,
    }
    qualifiers.update(extra)
    return {
        "statement_id": statement_id,
        "segment_id": BODY_SEGMENT,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_FILE,
    }


def build_plan() -> dict:
    need(sha256(SOURCE) == SOURCE_SHA, "source asset hash changed")
    need(sha256(PDF) == PDF_SHA, "CHP-5 PDF hash changed")
    need(sha256(PAGE_IMAGE) == IMAGE_SHA, "p.134 review image hash changed")
    for name, expected in EXPECTED.items():
        need(sha256(TABLES / name) == expected, f"unexpected pre-write hash: {name}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    body_text = "\n".join(source_lines[19:26])
    need(sha256_bytes(body_text.encode("utf-8")) == BODY_SHA, "p.134 body segment hash changed")
    need("one palmo" not in body_text and "on e palmo (221 cm.)" in body_text,
         "expected S0 OCR for the Passeri measurement changed")

    statements_path = TABLES / "book-statements.jsonl"
    statements = [json.loads(line) for line in statements_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    statement_map = {row["statement_id"]: row for row in statements}
    need(len(statement_map) == len(statements), "duplicate statement IDs already exist")
    body_rows = [row for row in statements if row.get("segment_id") == BODY_SEGMENT]
    need({row["statement_id"] for row in body_rows} == BODY_IDS, "p.134 statement set changed")
    for row in body_rows:
        need(row.get("qualifiers", {}).get("relation_candidate") is None,
             f"p.134 statement already classified: {row['statement_id']}")
    for statement_id in NOTE_IDS:
        need(statement_id in statement_map, f"missing expected p.134 note statement: {statement_id}")
    need(statement_map["st-chp5-notes-l131-rosa-della-pittura"]["qualifiers"].get("relation_candidate") is True,
         "p.134 note 2 citation classification changed")
    for statement_id in NOTE_IDS - {"st-chp5-notes-l131-rosa-della-pittura"}:
        need(statement_map[statement_id]["qualifiers"].get("relation_candidate") is None,
             f"p.134 note already classified: {statement_id}")
    need("st-chp5-notes-l130-doni-citation" not in statement_map,
         "Doni citation statement ID already exists")

    candidates, candidate_fields, candidate_bom = read_csv(TABLES / "entity-candidates.csv")
    candidate_map = {row["candidate_id"]: row for row in candidates}
    need(len(candidate_map) == len(candidates), "duplicate candidate IDs already exist")
    new_candidate_ids = {f"cand-{n}" for n in range(11806, 11812)}
    need(not (new_candidate_ids & set(candidate_map)), "one or more p.134 candidate IDs already exist")
    need(candidate_map["cand-6121"]["suggested_type"] == "",
         "Colonna gallery candidate type changed")
    need(candidate_map["cand-11017"]["suggested_type"] == "term",
         "Italian painting candidate type changed")

    mentions, mention_fields, mention_bom = read_csv(TABLES / "mentions.csv")
    mention_map = {row["mention_id"]: row for row in mentions}
    need(len(mention_map) == len(mentions), "duplicate mention IDs already exist")
    vanlaer_group_mention = mention_map.get("m-chp5-sec-iii-l20-26-010")
    need(vanlaer_group_mention is not None
         and vanlaer_group_mention["candidate_id"] == "cand-0173"
         and vanlaer_group_mention["surface_form"] == "Ms followers",
         "Van Laer followers mention changed")
    doni_citation_mention = mention_map.get("m-chp5-note-130-007")
    need(doni_citation_mention is not None
         and doni_citation_mention["candidate_id"] == "cand-0943"
         and doni_citation_mention["surface_form"] == "G. B. Doni",
         "Doni footnote mention changed")

    def body_span(line_number: int, needle: str) -> tuple[int, int]:
        line = source_lines[line_number - 1]
        position = line.find(needle)
        need(position >= 0 and line.find(needle, position + 1) < 0,
             f"expected unique source phrase at L{line_number}: {needle!r}")
        prefix = "\n".join(source_lines[19:line_number - 1])
        start = len(prefix) + (1 if line_number > 20 else 0) + position
        return start, start + len(needle)

    def note_span(line_number: int, needle: str) -> tuple[int, int]:
        line = source_lines[line_number - 1]
        position = line.find(needle)
        need(position >= 0 and line.find(needle, position + 1) < 0,
             f"expected unique source phrase at L{line_number}: {needle!r}")
        prefix = "\n".join(source_lines[125:line_number - 1])
        start = len(prefix) + (1 if line_number > 126 else 0) + position
        return start, start + len(needle)

    def need_quote(line_number: int, quote: str) -> None:
        need(quote in source_lines[line_number - 1],
             f"statement quote not found in S0 L{line_number}: {quote!r}")

    edited_statements = copy.deepcopy(statements)
    edited_map = {row["statement_id"]: row for row in edited_statements}

    def edit(statement_id: str, *, subject=None, obj=None, predicate=None,
             quote=None, claim=None, qualification=None, mentioned=None,
             relation=None, speaker=None, text_layer=None, ocr_note=None,
             remove_qualifiers=(), add_qualifiers=None):
        row = edited_map[statement_id]
        if subject is not None or "subject" in edit_args.get(statement_id, {}):
            row["subject_candidate_id"] = subject
        if obj is not None or "obj" in edit_args.get(statement_id, {}):
            row["object_candidate_id"] = obj
        if predicate is not None:
            row["predicate"] = predicate
        if quote is not None:
            row["original_quote"] = quote
        q = row.setdefault("qualifiers", {})
        if claim is not None:
            q["claim"] = claim
        if qualification is not None:
            q["qualification"] = qualification
        if mentioned is not None:
            q["mentioned_candidate_ids"] = mentioned
        if relation is not None:
            q["relation_candidate"] = relation
            q["relation_candidate_note"] = RELATION_NOTE if relation else NON_RELATION_NOTE
        if speaker is not None:
            q["speaker"] = speaker
        if text_layer is not None:
            q["text_layer"] = text_layer
        if ocr_note is not None:
            q["ocr_note"] = ocr_note
        for key in remove_qualifiers:
            q.pop(key, None)
        if add_qualifiers:
            q.update(add_qualifiers)

    edit_args: dict[str, dict] = {}

    def edit_row(statement_id: str, **kwargs) -> None:
        edit_args[statement_id] = kwargs
        edit(statement_id, **kwargs)

    edit_row(
        "st-chp5-p134-doni-shepherd-quotation-closure",
        relation=False,
        qualification=("Nested quotation by Doni, reported by Haskell; note 1 cites an unidentified Doni volume, "
                       "and note 4 continues this same quotation."),
    )
    edit_row(
        "st-chp5-p134-rosa-poem-protest",
        relation=True,
        qualification=("Haskell's framing of the poem is distinct from the quoted lines; the note cites Rosa's "
                       "Della Pittura but the cited passage was not independently inspected."),
        add_qualifiers={"source_line_start": 22, "source_line_end": 22},
    )
    edit_row(
        "st-chp5-p134-rosa-quote-translation-and-limit",
        subject=None,
        obj=None,
        predicate="audience_reception_contrast_in_rosa_translation",
        relation=False,
        claim=("Haskell translates Rosa as contrasting rejection of poor people in real life with an audience's "
               "liking for their painted images, then limits the claim with 'within limits at least.'"),
        qualification=("The audience is unnamed; this is Haskell's translation and contextual interpretation, "
                       "not a direct relation between the Bambocciate category and all poor people."),
        mentioned=["cand-6099", "cand-6118"],
        quote="What they abhor in real life they like to see in a picture",
    )
    edit_row(
        "st-chp5-p134-good-poor-and-small-scale",
        subject="cand-6099",
        obj="cand-6122",
        predicate="depicts_as_good_poor",
        relation=True,
        claim="Haskell says figures in the bambocciate are represented as the 'good poor.'",
        qualification=("The quoted category and its application are Haskell's interpretation; it is not an "
                       "externally verified social classification."),
        mentioned=["cand-6099", "cand-6122"],
        quote="The figures in the bambocciate are the ‘good poor’",
    )
    edit_row(
        "st-chp5-p134-passeri-small-figures",
        subject="cand-1351",
        obj=None,
        predicate="painted_figures_kept_small",
        relation=False,
        claim=("Haskell quotes Passeri as reporting that Van Laer painted pictures of varying sizes but kept "
               "their figures small, about one palmo high and never larger."),
        qualification=("The statement is Passeri's description as quoted by Haskell; the cited edition was not "
                       "independently consulted. Print p.134 reads one palmo (22½ cm.); S0 remains unchanged."),
        mentioned=["cand-1856", "cand-1351"],
        speaker="Giambattista Passeri, quoted by Haskell",
        text_layer="quotation reported in authorial narration",
        ocr_note="Print reads 'one palmo (22½ cm.)'; S0 OCR reads 'on e palmo (221 cm.)'.",
    )
    edit_row(
        "st-chp5-p134-expanding-backgrounds-and-picturesque-poor",
        relation=False,
        qualification=("Haskell's aesthetic characterization of later backgrounds and their treatment of poor "
                       "figures; print reads 'hills' where S0 OCR has 'Mils'."),
    )
    edit_row(
        "st-chp5-p134-van-laer-new-material",
        subject="cand-1351",
        obj="cand-11017",
        predicate="introduced_new_material_into_italian_painting",
        relation=True,
        claim="Haskell credits Pieter Van Laer with introducing something new into Italian painting.",
        qualification=("This is Haskell's art-historical assessment, not an independently established novelty. "
                       "The joint contribution of Van Laer and his followers is recorded separately."),
        mentioned=["cand-1351", "cand-11017"],
        quote="Pieter Van Laer did introduce something quite new into Italian painting",
        remove_qualifiers=(
            "footnote_target_line", "footnote_link_status", "citation_segment_id",
            "citation_source_line_start", "citation_source_line_end", "footnote_refs",
        ),
        ocr_note="Print reads 'his followers' and 'within'; S0 OCR has 'Ms followers' and 'witMn'.",
    )
    edit_row(
        "st-chp5-p134-bassano-caravaggio-precedents",
        subject="cand-0257",
        obj="cand-0173",
        predicate="possible_precedent_for",
        relation=True,
        claim="Haskell tentatively identifies Jacopo Bassano as a precedent for the Bamboccianti approach.",
        qualification=("The source's 'perhaps' is retained; it identifies no specific Bassano painting or direct "
                       "transmission of influence."),
        mentioned=["cand-0257", "cand-0173"],
        quote="Bassano",
    )
    edit_row(
        "st-chp5-p134-caravaggio-no-secular-ordinary-work-painting",
        relation=False,
        qualification=("This is Haskell's categorical negative claim about Caravaggio's corpus. Print confirms "
                       "'himself', 'painting', and 'ordinary'; S0 OCR remains unchanged."),
    )
    edit_row(
        "st-chp5-p134-caravaggio-proletarian-models-and-taste",
        subject="cand-11808",
        obj="cand-6124",
        predicate="depicts",
        relation=True,
        claim="Haskell says Caravaggio's earlier works include proletarian models.",
        qualification=("The work group is limited to the earlier pictures referenced in this passage; neither "
                       "individual works nor the models' identities are supplied."),
        mentioned=["cand-11808", "cand-6124"],
        quote="The proletarian models of Ms earlier works",
        ocr_note="Print reads 'his earlier works'; S0 OCR reads 'Ms earlier works'.",
    )
    edit_row(
        "st-chp5-p134-caravaggio-later-religious-scenes",
        subject="cand-11809",
        obj="cand-6116",
        predicate="depicts_peasants_in_conventional_religious_scenes",
        relation=True,
        claim=("Haskell says peasants in Caravaggio's later pictures take part in conventional religious scenes."),
        qualification=("The work group and peasantry are source-defined; 'always' is Haskell's generalization, "
                       "and no individual painting is identified."),
        mentioned=["cand-11809", "cand-6116"],
        quote="the deeply moving peasants of Ms later pictures always take part in a conventional religious scene",
        ocr_note="Print reads 'his later pictures'; S0 OCR reads 'Ms later pictures'.",
    )
    edit_row(
        "st-chp5-p134-caravaggio-revolution-and-prominence-of-poor",
        subject="cand-0544",
        obj="cand-6118",
        predicate="gave_poor_prominence_equal_to_great_or_sacred",
        relation=True,
        claim=("Haskell says that, for the first time, the poor emerged from the background and received as much "
               "prominence as the great or the sacred."),
        qualification=("This is Haskell's art-historical interpretation and periodization, not an independently "
                       "established first-occurrence claim."),
        mentioned=["cand-0544", "cand-6118"],
        quote=("For the first time the poor emerge from a shadowy background and are given as much prominence "
               "as the great or the sacred"),
    )
    edit_row(
        "st-chp5-p134-doni-shepherd-quotation-closure",
        add_qualifiers={
            "footnote_refs": [{
                "marker": 1,
                "segment_id": NOTES_SEGMENT,
                "source_line": 130,
                "citation_statement_ids": [
                    "st-chp5-notes-l130-doni-citation",
                    "st-chp5-notes-l130-doni-pastoral-quote",
                ],
            }],
        },
    )
    edit_row(
        "st-chp5-p134-caravaggio-followers-and-picaresque-mode",
        subject="cand-6123",
        obj="cand-0544",
        predicate="rarely_pursued_development_associated_with",
        relation=True,
        claim=("Haskell says Caravaggio's immediate followers in Italy only rarely pursued the development "
               "implicit in his elevation of the poor."),
        qualification=("The group remains unnamed and distinct from other follower candidates pending S3; "
                       "'rarely' is preserved. Print reads 'this attitude'; S0 OCR reads 'tMs attitude'."),
        mentioned=["cand-6123", "cand-0544", "cand-6118"],
        quote="His immediate followers in Italy only rarely pursued the line of development implicit in tMs attitude",
        ocr_note="Print reads 'this attitude'; S0 OCR reads 'tMs attitude'.",
    )
    edit_row(
        "st-chp5-p134-annibale-beaneater-and-drawings",
        subject=None,
        obj=None,
        predicate="assessed_as_more_significant_examples",
        relation=False,
        claim=("Haskell calls certain Carracci pictures more significant examples within this discussion of "
               "depicting working people."),
        qualification=("This is Haskell's comparative assessment. The Beaneater, its location, and Carracci's "
                       "drawings are recorded in separate relation statements; p.135 continues with 'But these'."),
        mentioned=["cand-0576", "cand-6119", "cand-6120", "cand-6121"],
        quote="More significant had been some of the pictures of Anfflbale Carracci",
        ocr_note="Print reads 'Annibale'; S0 OCR reads 'Anfflbale'.",
    )

    # Set the two established p.134 footnote claims to explicit S2 classifications.
    edit_row(
        "st-chp5-notes-l130-doni-pastoral-quote",
        relation=False,
        quote=source_lines[129].split(": ", 1)[1],
        qualification=("Nested quotation by Doni as printed in Haskell's note; the cited work and edition are "
                       "not identified beyond volume II and page 16."),
    )
    edit_row(
        "st-chp5-notes-l131-rosa-della-pittura",
        qualification=("The citation identifies Rosa's Della Pittura and lines 255-258 and 262-265; the cited "
                       "passage was not independently inspected."),
    )
    edit_row(
        "st-chp5-notes-l132-passeri-p72",
        subject="cand-2962",
        obj="cand-4376",
        predicate="cites",
        relation=True,
        claim="Haskell's book cites Passeri, page 72, in this footnote.",
        qualification=("The footnote points to the existing provisional Passeri archive candidate; its cited "
                       "edition was not independently consulted."),
    )
    edit_row(
        "st-chp5-notes-l133-doni-quote-continuation",
        relation=False,
        qualification=("Continuation of Doni's quoted distinction in note 1; the source OCR differs from the "
                       "printed Italian, and the source transcript is retained."),
    )

    # Move the p.134 body links from compound claims to their exact atomic claims.
    note4 = edited_map["st-chp5-notes-l133-doni-quote-continuation"]["qualifiers"]
    note4["linked_body_statement_ids"] = ["st-chp5-p134-van-laer-shepherds-pastoral-contrast"]
    note4["citation_body_statement_ids"] = ["st-chp5-p134-van-laer-shepherds-pastoral-contrast"]
    note4["related_source_lines"] = [25]

    added_statements = [
        source_statement(
            "st-chp5-p134-van-laer-followers-new-material",
            "cand-11806", "cand-11017", "introduced_new_subject_matter_into",
            25,
            "Haskell says Pieter Van Laer and his unnamed followers brought a wide range of new subject matter into art.",
            "he and Ms followers brought witMn the scope of art an enormous range of new material",
            ["cand-11806", "cand-11017"],
            ("The source defines the group only as Van Laer's followers. It is not automatically equated with all "
             "Bamboccianti; the OCR corrections are recorded without editing S0."),
            True,
            ocr_note="Print reads 'his followers' and 'within'; S0 OCR reads 'Ms followers' and 'witMn'.",
        ),
        source_statement(
            "st-chp5-p134-van-laer-shepherds-pastoral-contrast",
            "cand-1351", None, "shepherds_contrasted_with_noble_pastoral_past",
            25,
            "Haskell distinguishes Van Laer's shepherds from those of an earlier period when shepherding was still a noble profession.",
            "Ms shepherds were not those ‘of the past when the profession was still a noble one’",
            ["cand-1351", "cand-0943"],
            ("This is Haskell's comparison, with the older ideal continued in footnote 4's Doni quotation; it does "
             "not identify a particular painting."),
            False,
            ocr_note="Print reads 'his shepherds'; S0 OCR reads 'Ms shepherds'.",
            footnote_target_line=133,
            footnote_link_status="linked",
            citation_segment_id=NOTES_SEGMENT,
            citation_source_line_start=133,
            citation_source_line_end=133,
            footnote_refs=[{
                "marker": 4,
                "segment_id": NOTES_SEGMENT,
                "source_line": 133,
                "citation_statement_ids": ["st-chp5-notes-l133-doni-quote-continuation"],
            }],
        ),
        source_statement(
            "st-chp5-p134-caravaggio-possible-precedent",
            "cand-0544", "cand-0173", "possible_precedent_for",
            25,
            "Haskell tentatively identifies Caravaggio as a possible precedent for the Bamboccianti approach.",
            "Caravaggio perhaps",
            ["cand-0544", "cand-0173"],
            ("The source's 'perhaps' is retained; no individual Caravaggio work or direct transmission of influence "
             "is identified."),
            True,
        ),
        source_statement(
            "st-chp5-p134-bellori-links-bassano-caravaggio",
            None, None, "reported_textual_link_in_bellori_denunciation",
            25,
            "Haskell says Bassano and Caravaggio are linked together in Bellori's denunciation of the trend.",
            "who are linked together m Bellori’s denunciation of the trend",
            ["cand-0257", "cand-0544", "cand-0272", "cand-0173"],
            ("This reports Haskell's account of Bellori's text; the cited Bellori work is not identified here, and "
             "the textual association is not modeled as a personal relation between the artists."),
            False,
            ocr_note="Print reads 'in'; S0 OCR reads 'm'.",
        ),
        source_statement(
            "st-chp5-p134-bassano-caravaggio-amateur-evaluation",
            None, None, "evaluated_as_more_satisfying_to_cultivated_amateur",
            25,
            "Haskell judges the earlier examples by Bassano and Caravaggio more satisfying to the cultivated amateur.",
            "but how much more satisfying they had been for the cultivated amateur",
            ["cand-0257", "cand-0544"],
            "This is Haskell's aesthetic evaluation; the audience is not identified as a specific group.",
            False,
        ),
        source_statement(
            "st-chp5-p134-caravaggio-model-presentation-adapted-to-taste",
            "cand-11808", None, "model_presentation_adapted_to_sophisticated_taste",
            25,
            "Haskell says the presentation of Caravaggio's proletarian models was adapted to a sophisticated, even corrupt, taste.",
            "are clearly adapted to a sophisticated, not to say corrupt, taste",
            ["cand-11808", "cand-6124"],
            ("'Sophisticated' and 'corrupt' are Haskell's aesthetic judgments; no audience or particular painting "
             "is identified."),
            False,
        ),
        source_statement(
            "st-chp5-p134-caravaggio-revolution-cleared-ground",
            "cand-0544", "cand-0173", "cleared_ground_for",
            26,
            "Haskell presents Caravaggio's spiritual and aesthetic revolution as clearing the ground for the Bamboccianti.",
            "Caravaggio’s was the spiritual and aesthetic revolution that cleared the ground for the bamboccianti",
            ["cand-0544", "cand-0173"],
            "This is Haskell's art-historical interpretation, not an independently verified causal claim.",
            True,
        ),
        source_statement(
            "st-chp5-p134-caravaggio-followers-of",
            "cand-6123", "cand-0544", "followers_of",
            26,
            "Haskell identifies the unnamed immediate Italian group as Caravaggio's followers.",
            "His immediate followers in Italy",
            ["cand-6123", "cand-0544"],
            "The group remains unnamed and is not merged with other Caravaggio follower candidates.",
            True,
        ),
        source_statement(
            "st-chp5-p134-caravaggio-followers-picaresque-resemblance",
            "cand-11811", "cand-11807", "recalled_incidents_of",
            26,
            "Haskell says the followers' work recalls fanciful and sometimes grotesque incidents of the picaresque novel rather than sober daily-life observation.",
            "their work, wMch recalls far more the fanciful and sometimes grotèsque mcidents of the picaresque novel",
            ["cand-11811", "cand-11807"],
            ("This is Haskell's comparison, not a claim that a particular novel or painting is identified; print "
             "reads 'which', 'grotesque', and 'incidents'."),
            True,
            ocr_note="Print reads 'which', 'grotesque', and 'incidents'; S0 OCR reads 'wMch', 'grotèsque', and 'mcidents'.",
        ),
        source_statement(
            "st-chp5-p134-bambocciate-small-proportions",
            "cand-6099", None, "figures_reduced_to_safe_small_proportions",
            24,
            "Haskell says the figures in the bambocciate are cut down to safely small proportions.",
            "they are cut down to safely small proportions",
            ["cand-6099", "cand-6122"],
            "The word 'safely' is Haskell's interpretive characterization; the cited figures are not individually identified.",
            False,
        ),
        source_statement(
            "st-chp5-p134-beaneater-created-by-annibale",
            "cand-6119", "cand-0576", "created_by",
            26,
            "Haskell identifies The Beaneater as one of Annibale Carracci's pictures.",
            "the Beaneater",
            ["cand-6119", "cand-0576"],
            "This records the source's attribution; it does not independently verify authorship.",
            True,
        ),
        source_statement(
            "st-chp5-p134-annibale-drawings-created-by",
            "cand-6120", "cand-0576", "created_by",
            26,
            "Haskell identifies the drawings of working people at daily occupations as Annibale Carracci's.",
            "Ms drawings of the working classes at their daily occupations",
            ["cand-6120", "cand-0576"],
            ("The drawings remain an unidentified group; print reads 'his drawings', while S0 OCR reads 'Ms drawings'. "
             "Authorship follows Haskell's attribution."),
            True,
            ocr_note="Print reads 'his drawings'; S0 OCR reads 'Ms drawings'.",
        ),
        source_statement(
            "st-chp5-p134-beaneater-colonna-gallery-location",
            "cand-6119", "cand-6121", "located_at",
            26,
            "Haskell locates The Beaneater in the Colonna gallery.",
            "in the Colonna gallery",
            ["cand-6119", "cand-6121"],
            "The exact gallery or room identity and the time represented by this location are not specified.",
            True,
        ),
    ]

    doni_citation = citation_statement(
        "st-chp5-notes-l130-doni-citation",
        "cand-11810",
        "Haskell's book cites an unidentified work by G. B. Doni, volume II, page 16.",
        "G. B. Doni, II, p. 16",
        130,
        ["st-chp5-p134-doni-shepherd-quotation-closure"],
        ("The cited title and edition are not given. The open archive candidate preserves only the author, volume, "
         "and page supplied by the note; no work identity is inferred."),
    )
    added_statements.append(doni_citation)

    new_candidates = [
        {
            "candidate_id": "cand-11806", "index_entry_id": "", "canonical_name": "Pieter Van Laer and his unnamed followers (source-defined group)",
            "index_page_range": "", "suggested_type": "", "status": "open", "index_source_file": "", "sub_entry": "",
            "detail": "Joint source-defined artistic group named as introducing a wide range of new subject matter. The followers are unidentified; do not equate the group with all Bamboccianti without further evidence.",
            "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{BODY_SEGMENT}#L25",
        },
        {
            "candidate_id": "cand-11807", "index_entry_id": "", "canonical_name": "Picaresque novel as a literary genre referenced by Haskell",
            "index_page_range": "", "suggested_type": "term", "status": "open", "index_source_file": "", "sub_entry": "",
            "detail": "Literary genre used by Haskell to compare the fanciful incidents in the work of Caravaggio's immediate Italian followers. No specific novel or painting is identified.",
            "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{BODY_SEGMENT}#L26",
        },
        {
            "candidate_id": "cand-11808", "index_entry_id": "", "canonical_name": "Caravaggio's earlier paintings described through proletarian models (source-defined group)",
            "index_page_range": "", "suggested_type": "work", "status": "open", "index_source_file": "", "sub_entry": "",
            "detail": "Source-defined group of earlier Caravaggio works in which Haskell says proletarian models appear. No titles, dates, or individual models are supplied; do not expand to all early works.",
            "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{BODY_SEGMENT}#L25",
        },
        {
            "candidate_id": "cand-11809", "index_entry_id": "", "canonical_name": "Caravaggio's later religious pictures featuring peasants (source-defined group)",
            "index_page_range": "", "suggested_type": "work", "status": "open", "index_source_file": "", "sub_entry": "",
            "detail": "Source-defined group of later Caravaggio pictures in which Haskell says peasants participate in conventional religious scenes. No individual painting is identified.",
            "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{BODY_SEGMENT}#L25",
        },
        {
            "candidate_id": "cand-11810", "index_entry_id": "", "canonical_name": "Unidentified work by G. B. Doni, volume II, page 16",
            "index_page_range": "", "suggested_type": "archive", "status": "open", "index_source_file": "", "sub_entry": "",
            "detail": "Work cited by Haskell in the p.134 note as 'G. B. Doni, II, p. 16'. The title, edition, and publication details are absent; do not infer a specific Doni work.",
            "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{NOTES_SEGMENT}#L130",
        },
        {
            "candidate_id": "cand-11811", "index_entry_id": "", "canonical_name": "Works by Caravaggio's immediate Italian followers (source-defined group)",
            "index_page_range": "", "suggested_type": "work", "status": "open", "index_source_file": "", "sub_entry": "",
            "detail": "Work group referred to as 'their work' in Haskell's comparison with the picaresque novel. No individual painting is identified; keep distinct from the unnamed follower artists candidate.",
            "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{BODY_SEGMENT}#L26",
        },
    ]

    new_mentions = []

    def add_body_mention(number: int, candidate_id: str, line: int, surface: str, note: str = "") -> None:
        start, end = body_span(line, surface)
        new_mentions.append({
            "mention_id": f"m-chp5-sec-iii-l20-26-{number:03d}",
            "segment_id": BODY_SEGMENT,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(end),
            "note": note,
        })

    add_body_mention(24, "cand-11807", 26, "picaresque novel")
    add_body_mention(25, "cand-11808", 25, "Ms earlier works",
                     "S0 OCR reads 'Ms'; print reads 'his'. The group is limited to the works described here.")
    add_body_mention(26, "cand-11809", 25, "Ms later pictures",
                     "S0 OCR reads 'Ms'; print reads 'his'. The group is limited to the works described here.")
    add_body_mention(27, "cand-6116", 25, "peasants",
                     "Keep the peasantry wording distinct from the broader poor-class candidate cand-6118.")
    add_body_mention(28, "cand-11811", 26, "their work",
                     "The source-defined works of the unnamed immediate Italian follower group; no individual painting is named.")

    new_ids = {row["statement_id"] for row in added_statements}
    need(len(new_ids) == len(added_statements), "duplicate IDs in p.134 write plan")
    need(not (new_ids & set(statement_map)), "one or more new p.134 statement IDs already exist")
    for row in added_statements:
        q = row["qualifiers"]
        line = q["source_line_start"]
        need_quote(line, row["original_quote"])
        need(q["relation_candidate"] is not None, f"new statement lacks classification: {row['statement_id']}")
        if q["relation_candidate"]:
            need(row["subject_candidate_id"] and row["object_candidate_id"],
                 f"new relation candidate has an open endpoint: {row['statement_id']}")

    candidate_ids = {row["candidate_id"] for row in new_candidates}
    need(len(candidate_ids) == len(new_candidates), "duplicate candidate IDs in p.134 write plan")
    need(candidate_ids.isdisjoint(candidate_map), "one or more new p.134 candidate IDs already exist")
    new_mention_ids = {row["mention_id"] for row in new_mentions}
    need(len(new_mention_ids) == len(new_mentions), "duplicate IDs in p.134 mention plan")
    need(new_mention_ids.isdisjoint(mention_map), "one or more new p.134 mention IDs already exist")

    follower_start, follower_end = body_span(25, "he and Ms followers")
    note_doni_start, note_doni_end = note_span(130, "G. B. Doni, II, p. 16")
    mention_updates = {
        "m-chp5-sec-iii-l20-26-010": {
            "candidate_id": "cand-11806",
            "surface_form": "he and Ms followers",
            "start_char": str(follower_start),
            "end_char": str(follower_end),
            "note": "Print reads 'he and his followers'; preserve S0 OCR and keep this source-defined group distinct from all Bamboccianti.",
        },
        "m-chp5-note-130-007": {
            "candidate_id": "cand-11810",
            "surface_form": "G. B. Doni, II, p. 16",
            "start_char": str(note_doni_start),
            "end_char": str(note_doni_end),
            "note": "Bibliographic citation fragment; title and edition are not specified, so it maps to an open archive candidate.",
        },
    }
    for mention_id, updates in mention_updates.items():
        need(mention_id in mention_map, f"missing mention to update: {mention_id}")
        mention_map[mention_id].update(updates)

    # Ensure every new mention is exact and does not overlap any existing mention in its segment.
    for new_row in new_mentions:
        start, end = int(new_row["start_char"]), int(new_row["end_char"])
        for old in mentions:
            if old["segment_id"] != new_row["segment_id"]:
                continue
            old_start, old_end = int(old["start_char"]), int(old["end_char"])
            if start < old_end and old_start < end:
                raise SystemExit(f"new mention overlaps {old['mention_id']}: {new_row['mention_id']}")
    for segment_id, updated_row in [(BODY_SEGMENT, mention_map["m-chp5-sec-iii-l20-26-010"]),
                                    (NOTES_SEGMENT, mention_map["m-chp5-note-130-007"])]:
        start, end = int(updated_row["start_char"]), int(updated_row["end_char"])
        for other in mentions:
            if other["mention_id"] == updated_row["mention_id"] or other["segment_id"] != segment_id:
                continue
            old_start, old_end = int(other["start_char"]), int(other["end_char"])
            if start < old_end and old_start < end:
                raise SystemExit(f"updated mention overlaps {other['mention_id']}: {updated_row['mention_id']}")

    candidate_map["cand-6121"]["suggested_type"] = "place"
    candidate_map["cand-6121"]["detail"] = (
        "Place candidate for the gallery in which Haskell locates The Beaneater. "
        "The exact building, room, and identity are not specified."
    )

    # Add the new bibliography edge to the existing Doni quotation statement.
    quote_q = edited_map["st-chp5-notes-l130-doni-pastoral-quote"]["qualifiers"]
    quote_q["linked_body_statement_ids"] = ["st-chp5-p134-doni-shepherd-quotation-closure"]
    quote_q["citation_body_statement_ids"] = ["st-chp5-p134-doni-shepherd-quotation-closure"]
    quote_q["related_segment"] = BODY_SEGMENT
    quote_q["related_source_lines"] = [21]

    # Add exact S2 relation-candidate classification to the page's note 1 bibliography statement.
    # Verify all new and modified quotations against the unchanged OCR source.
    for row in edited_map.values():
        if row.get("segment_id") != BODY_SEGMENT:
            continue
        if row["statement_id"] in BODY_IDS:
            quote = row["original_quote"]
            line_number = row["qualifiers"]["source_line_start"]
            need_quote(line_number, quote)
    for row in added_statements:
        q = row["qualifiers"]
        if row["segment_id"] == BODY_SEGMENT:
            need_quote(q["source_line_start"], row["original_quote"])
        else:
            need_quote(q["source_line_start"], row["original_quote"])

    # Reject any missing candidate referenced by the final p.134 statements.
    final_candidate_ids = set(candidate_map) | candidate_ids
    for row in edited_map.values():
        if row.get("segment_id") != BODY_SEGMENT:
            continue
        q = row.get("qualifiers", {})
        for cid in [row.get("subject_candidate_id"), row.get("object_candidate_id")]:
            need(cid is None or cid in final_candidate_ids, f"unknown endpoint {cid} in {row['statement_id']}")
        for cid in q.get("mentioned_candidate_ids", []):
            need(cid in final_candidate_ids, f"unknown mention candidate {cid} in {row['statement_id']}")
    for row in added_statements:
        q = row["qualifiers"]
        for cid in [row.get("subject_candidate_id"), row.get("object_candidate_id")]:
            need(cid is None or cid in final_candidate_ids, f"unknown new endpoint {cid} in {row['statement_id']}")
        for cid in q.get("mentioned_candidate_ids", []):
            need(cid in final_candidate_ids, f"unknown new mention candidate {cid} in {row['statement_id']}")

    # Prepare exact serialized outputs while preserving the original JSONL and CSV conventions.
    final_statements = []
    for row in edited_statements:
        final_statements.append(row)
    final_statements.extend(added_statements)
    statement_bytes = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in final_statements).encode("utf-8")

    final_candidates = [candidate_map[row["candidate_id"]] for row in candidates] + new_candidates
    candidate_bytes = render_csv(final_candidates, candidate_fields, candidate_bom)
    # Restore the edited mention rows into the output list after constructing the updated map.
    mention_map = {row["mention_id"]: row for row in mentions}
    for mention_id, updates in mention_updates.items():
        mention_map[mention_id].update(updates)
    final_mentions = [mention_map[row["mention_id"]] for row in mentions] + new_mentions
    mention_bytes = render_csv(final_mentions, mention_fields, mention_bom)

    return {
        "outputs": {
            "book-statements.jsonl": statement_bytes,
            "entity-candidates.csv": candidate_bytes,
            "mentions.csv": mention_bytes,
        },
        "backup_suffix": ".bak-s2-chp5-p134-20261012",
        "body_classified": len(BODY_IDS),
        "new_statements": added_statements,
        "new_candidates": new_candidates,
        "new_mentions": new_mentions,
        "mention_updates": mention_updates,
        "note_ids": NOTE_IDS,
        "source_sha256": SOURCE_SHA,
        "pdf_sha256": PDF_SHA,
        "image_sha256": IMAGE_SHA,
        "body_sha256": BODY_SHA,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Controlled S2 review and writeback for printed p.134.")
    parser.add_argument("--apply", action="store_true", help="write the reviewed exact change set")
    args = parser.parse_args()
    plan = build_plan()
    print("S2 p.134 dry-run passed")
    print(f"existing body statements classified: {plan['body_classified']}")
    print(f"new atomic statements: {len(plan['new_statements'])}")
    print(f"new source-limited candidates: {len(plan['new_candidates'])}")
    print(f"new exact mentions: {len(plan['new_mentions'])}")
    print("classification: p.134 body 14 existing; note 1 and note 3 citation edges; note 1 and note 4 quotations remain non-relational")
    for name, data in plan["outputs"].items():
        print(f"planned {name}: {sha256_bytes(data)}")
    if not args.apply:
        print("No files were written. Pass --apply to write the verified change set.")
        return

    for name, expected in EXPECTED.items():
        path = TABLES / name
        need(sha256(path) == expected, f"pre-write hash changed before apply: {name}")
    for name in EXPECTED:
        path = TABLES / name
        backup = path.with_name(path.name + plan["backup_suffix"])
        need(not backup.exists(), f"recovery copy already exists: {backup.name}")
    for name in EXPECTED:
        path = TABLES / name
        backup = path.with_name(path.name + plan["backup_suffix"])
        shutil.copy2(path, backup)
        need(sha256(backup) == EXPECTED[name], f"recovery copy hash mismatch: {backup.name}")
        print(f"recovery copy: {backup.name} {sha256(backup)}")
    for name, data in plan["outputs"].items():
        atomic_write(TABLES / name, data)
    for name, data in plan["outputs"].items():
        actual = sha256(TABLES / name)
        need(actual == sha256_bytes(data), f"post-write hash mismatch: {name}")
        print(f"written {name}: {actual}")
    print("p.134 structured-table writeback verified; relations.csv was not changed")


if __name__ == "__main__":
    main()
