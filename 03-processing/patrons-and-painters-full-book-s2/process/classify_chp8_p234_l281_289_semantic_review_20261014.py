"""Guarded S2 semantic review for printed p.234, body and page-end note lines 282-289."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE = ROOT / SOURCE_REL
PDF = ROOT / "02-sources" / "01-book" / "CHP-8.pdf"
PAGE_IMAGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "p234_page_review.png"
SEGMENT = "chp-8:08_CHP-8_sec_ii:l281-289"
BACKUP_SUFFIX = ".bak-s2-chp8-p234-l281-289-semantic-review-20261014"
NEW_MODELO_ID = "cand-12097"
NEW_PORTRAITS_ID = "cand-12098"
EXPECTED = {
    STATEMENTS: "79ac05eac83a7a7de874bdfe581522b1aece06eb7966c165deeebfb197eb55f6",
    CANDIDATES: "40bbc368b7286291604c132b3d1c577d554dba1f13906801bc67f88210e9832d",
    MENTIONS: "142227f26f8be93f0b5f80e2378de352b6aeb8e2f1c30ebe824bd20e13a037d9",
    COVERAGE: "5fe027b7632d2b52e6b993e70d6dd70b56fe9c86537e3f61760f0152a2b9255f",
    SOURCE: "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    PDF: "cb11451ac726f37ed5badf21a569af88f790f858f1c39eb63f2efb58a0fe4ac3",
    PAGE_IMAGE: "4bcdc983bcfe2b03d31f0bf45cb78eb6ef5a4b2c83d26191445d99097cad0312",
}
EXPECTED_STATEMENTS = {
    "st-chp8-p234-cassana-history-pictures",
    "st-chp8-p234-cassana-role",
    "st-chp8-p234-cook-arrival",
    "st-chp8-p234-cook-reception",
    "st-chp8-p234-fumiani-model-review",
    "st-chp8-p234-fumiani-programme",
    "st-chp8-p234-fumiani-relations",
    "st-chp8-p234-langetti-report",
    "st-chp8-p234-subject-change",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def jsonl_bytes(rows):
    return ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")


def csv_bytes(fields, rows):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def atomic_write(path: Path, data: bytes):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(data)
    temporary.replace(path)


def cut(text: str, start: str, end: str | None = None, *, include_end: bool = False) -> str:
    a = text.find(start)
    if a < 0:
        raise SystemExit(f"source fragment not found: {start!r}")
    if end is None:
        return text[a:].rstrip()
    b = text.find(end, a + len(start))
    if b < 0:
        raise SystemExit(f"source end fragment not found after {start!r}: {end!r}")
    if include_end:
        b += len(end)
    return text[a:b].rstrip()


def set_review(row, *, subject, object_, predicate, lines, claim, quote, note, mentioned,
               relation, speaker="Haskell", text_layer="body", speaker_judgment=True,
               ocr_corrections=None, clear_ocr=False):
    row["subject_candidate_id"] = subject
    row["object_candidate_id"] = object_
    row["predicate"] = predicate
    row["original_quote"] = quote
    q = row["qualifiers"]
    q.update({
        "source_line_start": lines[0], "source_line_end": lines[1],
        "printed_page": 234, "pdf_physical_page": 40,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": note, "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation, "relation_candidate_note": note,
        "speaker_judgment": speaker_judgment,
    })
    if clear_ocr:
        q.pop("ocr_corrections", None)
    if ocr_corrections is not None:
        q["ocr_corrections"] = ocr_corrections


def new_statement(statement_id, subject, object_, predicate, lines, claim, quote, *, note,
                  mentioned, relation, speaker="Haskell", text_layer="body", speaker_judgment=True,
                  ocr_corrections=None):
    row = {"statement_id": statement_id, "segment_id": SEGMENT,
           "subject_candidate_id": subject, "object_candidate_id": object_, "predicate": predicate,
           "qualifiers": {}, "original_quote": quote, "origin": "book", "source_file": SOURCE_REL}
    set_review(row, subject=subject, object_=object_, predicate=predicate, lines=lines,
               claim=claim, quote=quote, note=note, mentioned=mentioned, relation=relation,
               speaker=speaker, text_layer=text_layer, speaker_judgment=speaker_judgment,
               ocr_corrections=ocr_corrections)
    return row


def add_link(row, field, statement_id):
    values = row["qualifiers"].setdefault(field, [])
    if statement_id not in values:
        values.append(statement_id)


def plan():
    for path, expected in EXPECTED.items():
        if sha(path.read_bytes()) != expected:
            raise SystemExit(f"input changed: {path.relative_to(ROOT)}")

    segments = read_jsonl(SEGMENTS)
    meta = next((row for row in segments if row["segment_id"] == SEGMENT), None)
    if not meta or (meta["line_start"], meta["line_end"]) != (281, 289):
        raise SystemExit("unexpected p.234 segment metadata")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    if sha("\n".join(source_lines[280:289]).encode("utf-8")) != meta["sha256"]:
        raise SystemExit("p.234 source segment hash mismatch")
    l282, l283, l284, l285, l286, l287, l288, l289 = (source_lines[n - 1] for n in range(282, 290))
    segment_text = "\n".join(source_lines[281:289])

    candidate_fields, candidates = read_csv(CANDIDATES)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    numeric_ids = [int(row["candidate_id"][5:]) for row in candidates
                   if row["candidate_id"].startswith("cand-") and row["candidate_id"][5:].isdigit()]
    if max(numeric_ids) != 12096 or NEW_MODELO_ID in candidate_by_id or NEW_PORTRAITS_ID in candidate_by_id:
        raise SystemExit("candidate ID sequence changed; refusing to allocate p.234 candidates")
    required_candidates = {
        "cand-0593", "cand-0932", "cand-1087", "cand-1363", "cand-1609", "cand-1674",
        "cand-3397", "cand-3401", "cand-4268", "cand-5160", "cand-5756", "cand-7893",
        "cand-7936", "cand-7939", "cand-7940", "cand-7941", "cand-7942", "cand-7943",
        "cand-7944", "cand-7945", "cand-7946", "cand-7947", "cand-7948", "cand-7951",
    }
    if missing := required_candidates - set(candidate_by_id):
        raise SystemExit(f"required p.234 candidates missing: {sorted(missing)}")

    mention_fields, mentions = read_csv(MENTIONS)
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if mention_by_id.get("m-chp8-p234-modello", {}).get("candidate_id") != "cand-1674":
        raise SystemExit("unexpected current modello mention mapping")
    if mention_by_id.get("m-chp8-p234-ferdinand-inventory", {}).get("candidate_id") != "cand-1609":
        raise SystemExit("unexpected current inventory mention mapping")
    full_source_text = "\n".join(source_lines[280:289])
    portrait_offset = full_source_text.find("portraits of the Prince and his household")
    if portrait_offset < 0:
        raise SystemExit("portrait work-group phrase not found in p.234 source")
    portrait_span = (portrait_offset, portrait_offset + len("portraits"))
    if portrait_span[0] <= 1709 < portrait_span[1] or portrait_span[1] > int(mention_by_id["m-chp8-p234-prince-household"]["start_char"]):
        raise SystemExit("portrait group mention would overlap the existing Prince mention")

    statements = read_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statements}
    target_rows = [row for row in statements if row.get("segment_id") == SEGMENT]
    if len(target_rows) != 9 or {row["statement_id"] for row in target_rows} != EXPECTED_STATEMENTS:
        raise SystemExit(f"unexpected p.234 statement set: {len(target_rows)} rows")
    _, coverage = read_csv(COVERAGE)
    coverage_row = next((row for row in coverage if row["segment_id"] == SEGMENT), None)
    if not coverage_row or (coverage_row["disposition"], coverage_row["migration_status"]) != ("reviewed", "complete"):
        raise SystemExit(f"unexpected p.234 coverage state: {coverage_row}")

    raw_quotes = {
        "fumiani_frame": cut(l282, "relations between Giannaritonio", "by the artists who worked for him.1", include_end=True),
        "fumiani_match": cut(l283, "He wanted a picture to match one by Domenichino", " and he proceeded"),
        "fumiani_dimensions": cut(l283, "and he proceeded to give Fumiani its dimensions", " It must show"),
        "programme_content": cut(l283, "It must show, he wrote to his agent") + "\n" +
                             cut(l284, "Cassana, an architectural background", " at prayer.", include_end=True),
        "cassana_david": cut(l284, "Cassana himself is to paint the figure of David", ", though if Fumiani"),
        "fumiani_option": cut(l284, "though if Fumiani insists", " later.", include_end=True),
        "model_request": cut(l284, "He must send the modello to Ferdinand for inspection", " It duly arrived"),
        "model_arrival": cut(l284, "It duly arrived", " and proved satisfactory"),
        "model_approval": cut(l284, "and proved satisfactory", ", but David"),
        "david_movement": cut(l284, "David, commented the Prince, should display more", "movement.", include_end=True),
        "angel_punishments": cut(l284, "Perhaps it would be improved by", " punishments.", include_end=True),
        "david_surprise": cut(l284, "David must show great surprise", "expressing movement.", include_end=True),
        "david_attributes": cut(l284, "Besides, the composition could be enriched by", "diadem.", include_end=True),
        "subject_change": cut(l284, "And then Ferdinand changed his mind.", " a picture which"),
        "zechariah_inventory": cut(l284, "a picture which was recorded in Ferdinand’s inventory", " and which is now"),
        "zechariah_uffizi": cut(l284, "and which is now in the Uffizi", " (Plate 40b)."),
        "subject_interpretation": cut(l284, "It seems clear that these subjects", " fanciful composition.", include_end=True),
        "cassana_role": cut(l285, "Niccolo Cassana also worked a good deal for Ferdinand", " adviser.", include_end=True),
        "cassana_portraits": cut(l285, "He visited Florence on various occasions chiefly so as to paint portraits of the Prince and his household", ", and from time to time"),
        "cassana_sent": cut(l285, "from time to time he would send pictures from") + "\nVenice.",
        "cook_arrival": cut(l286, "In September 1707 his Portrait os a Cook reached Florence", " to the delight"),
        "cook_delight": "to the delight of the\nPrince",
        "cook_details": cut(l287, "who commented on its realistic details", " (he particularly"),
        "cook_sitter": cut(l287, "he particularly wanted to know who the sitter was", " and above all"),
        "cook_quality": cut(l287, "and above all on its bold", " native Florentine artists.", include_end=True),
        "cassana_bacchanal": cut(l287, "a Bacchanal", ", a Venus"),
        "cassana_venus": cut(l287, "a Venus playing with Cupid", " and so on"),
        "cassana_catiline": cut(l287, "a Conspiracy of Catiline", ".", include_end=True),
        "langetti_pictures": cut(l289, "Ratti (Soprani/Ratti, H, 26)", " says that Langetti was actually"),
        "langetti_employment": cut(l289, "says that Langetti was actually employed by Ferdinand in", "Florence.", include_end=True),
        "langetti_chronology": cut(l289, "But this is impossible as Langetti died in 1676", " aged 11.", include_end=True),
    }
    for quote in raw_quotes.values():
        if quote not in segment_text:
            raise SystemExit(f"quote is not an exact p.234 source span: {quote!r}")

    # Keep source quotes byte-for-byte aligned with the Markdown layer; print corrections remain in qualifiers.
    quotes = dict(raw_quotes)

    required_mentions = {
        "m-chp8-p234-ferdinand-inventory", "m-chp8-p234-modello", "m-chp8-p234-uffizi",
        "m-chp8-p234-bacchanal", "m-chp8-p234-venus-cupid", "m-chp8-p234-catiline",
        "m-chp8-p234-langetti-portrait", "m-chp8-p234-langetti-card-players",
        "m-chp8-p234-medici-collection",
    }
    if missing := required_mentions - set(mention_by_id):
        raise SystemExit(f"required p.234 mentions missing: {sorted(missing)}")

    # Existing IDs are kept but narrowed to one assertion each.
    set_review(by_id["st-chp8-p234-cassana-history-pictures"], subject="cand-0593", object_="cand-7941",
        predicate="painted_a_bacchanal_for_ferdinand", lines=(287, 287),
        claim="Haskell says Niccolò Cassana painted an unidentified Bacchanal history picture for the Grand Prince.",
        quote=quotes["cassana_bacchanal"], note="The source names the subject and patron but gives no title, date, or present location.",
        mentioned=["cand-0593", "cand-1609", "cand-7941"], relation=True)
    set_review(by_id["st-chp8-p234-cassana-role"], subject="cand-0593", object_="cand-1609",
        predicate="worked_for_ferdinand_as_painter_and_artistic_adviser", lines=(285, 285),
        claim="Haskell says Niccolò Cassana worked for Ferdinand as a painter and artistic adviser.",
        quote=quotes["cassana_role"], note="The two stated professional roles are retained together as Cassana's service to Ferdinand; visits, portraits, and pictures sent from Venice are separate claims.",
        mentioned=["cand-0593", "cand-1609"], relation=True,
        ocr_corrections=[{"source_line": 285, "ocr": "Niccolo", "print": "Niccolò", "basis": "CHP-8.pdf physical page 40"}])
    set_review(by_id["st-chp8-p234-cook-arrival"], subject="cand-7940", object_="cand-3397",
        predicate="reached_florence_in_september_1707", lines=(286, 286),
        claim="Haskell says Niccolò Cassana's Portrait of a Cook reached Florence in September 1707.",
        quote=quotes["cook_arrival"], note="The source does not identify the sitter or give the painting's present location; the title's OCR error is corrected against the print.",
        mentioned=["cand-0593", "cand-7940", "cand-3397"], relation=True,
        ocr_corrections=[{"source_line": 286, "ocr": "Portrait os a Cook", "print": "Portrait of a Cook", "basis": "CHP-8.pdf physical page 40"}])
    set_review(by_id["st-chp8-p234-cook-reception"], subject="cand-1609", object_="cand-7940",
        predicate="was_delighted_by_arrival_of_cooks_portrait", lines=(286, 287),
        claim="Haskell says the Portrait of a Cook reached Florence to the Prince's delight.",
        quote=quotes["cook_delight"], note="This is a reported emotional response, not a formal relation or an independent appraisal.",
        mentioned=["cand-1609", "cand-7940"], relation=False,
        speaker="Ferdinand as reported by Haskell", text_layer="reported appraisal")

    model_review = by_id["st-chp8-p234-fumiani-model-review"]
    old_model_note_links = list(model_review["qualifiers"].pop("linked_note_statement_ids", []))
    set_review(model_review, subject=NEW_MODELO_ID, object_="cand-1609",
        predicate="modello_arrived_at_ferdinand_for_inspection", lines=(284, 284),
        claim="Haskell says the modello for Fumiani's composition duly arrived at Ferdinand for inspection.",
        quote=quotes["model_arrival"], note="The passage records arrival but does not identify who sent the modello; the model itself is distinct from the proposed finished picture.",
        mentioned=[NEW_MODELO_ID, "cand-7893", "cand-1087", "cand-1609", "cand-1674"], relation=True)

    programme = by_id["st-chp8-p234-fumiani-programme"]
    set_review(programme, subject="cand-7893", object_="cand-7944",
        predicate="fumiani_composition_requested_to_match_domenichino_painting", lines=(283, 283),
        claim="Haskell says Ferdinand wanted Fumiani's picture to match an unidentified painting by Domenichino.",
        quote=quotes["fumiani_match"], note="The Domenichino painting is not titled; the relation records Ferdinand's stated design aim, not proof the comparison was realized.",
        mentioned=["cand-1609", "cand-7893", "cand-7944", "cand-0932", "cand-1087"], relation=True, clear_ocr=True)
    frame = by_id["st-chp8-p234-fumiani-relations"]
    set_review(frame, subject="cand-1609", object_=None,
        predicate="haskell_interpreted_fumiani_account_as_revealing_ferdinands_fantasies", lines=(282, 282),
        claim="Haskell interprets the account of Ferdinand's relations with Giannantonio Fumiani as revealing his eagerness to have artists express his fantasies.",
        quote=quotes["fumiani_frame"], note="This is Haskell's interpretation of Ferdinand's artistic psychology, not a discrete relationship claim.",
        mentioned=["cand-1609", "cand-1087"], relation=False,
        ocr_corrections=[
            {"source_line": 282, "ocr": "Giannaritonio", "print": "Giannantonio", "basis": "CHP-8.pdf physical page 40"},
            {"source_line": 282, "ocr": "ns", "print": "us", "basis": "CHP-8.pdf physical page 40"},
        ])

    langetti = by_id["st-chp8-p234-langetti-report"]
    set_review(langetti, subject="cand-1363", object_="cand-1609",
        predicate="ratti_reported_langetti_employed_by_ferdinand_in_florence", lines=(289, 289),
        claim="Haskell reports that Ratti says Giovanni Battista Langetti was employed by Ferdinand in Florence.",
        quote=quotes["langetti_employment"], note="This is Ratti's indirect report as cited by Haskell; Haskell's chronological objection is a separate statement. The accompanying Fogolari Letter 92 reference continues in note line 429.",
        mentioned=["cand-1363", "cand-1609", "cand-3397", "cand-5160", "cand-7894", "cand-7951"],
        relation=True, speaker="Ratti as reported by Haskell", text_layer="page-end note/report",
        ocr_corrections=[{"source_line": 289, "ocr": "Ratti, H, 26", "print": "Ratti, II, 26", "basis": "CHP-8.pdf physical page 40"}])
    langetti["qualifiers"]["cross_reference_segments"] = [{
        "segment_id": "chp-8:08_CHP-8_sec_ii:l372-461", "source_line_start": 429, "source_line_end": 429,
    }]

    subject_change = by_id["st-chp8-p234-subject-change"]
    subject_change["qualifiers"].pop("linked_note_statement_ids", None)
    set_review(subject_change, subject="cand-1609", object_="cand-7939",
        predicate="changed_requested_subject_to_probable_stoning_of_zechariah", lines=(284, 284),
        claim="Haskell says Ferdinand changed his mind and wanted another Old Testament subject; Haskell infers from the lost instructions that the intended subject was The Stoning of Zechariah.",
        quote=quotes["subject_change"], note="The instructions are lost, so identification as The Stoning of Zechariah remains Haskell's inference ('evidently'); bizzarra is retained as his source characterization.",
        mentioned=["cand-1609", "cand-7939", "cand-4173", "cand-4268"], relation=True)

    note_ids = {
        "stoning": "st-chp8-p234-note3-stoning-record",
        "catiline": "st-chp8-p234-note5-catiline",
    }
    if any(note_id not in by_id for note_id in note_ids.values()):
        raise SystemExit("expected p.234 note statements are missing")

    additions = [
        new_statement("st-chp8-p234-fumiani-dimensions", "cand-1609", "cand-7893",
            "provided_dimensions_and_programme_for_fumiani_composition", (283, 283),
            "Haskell says Ferdinand gave Fumiani the dimensions and an elaborate programme for the requested picture.",
            quotes["fumiani_dimensions"], note="This records Ferdinand's design instructions for the unidentified Fumiani composition; it does not establish that the planned picture was completed.",
            mentioned=["cand-1609", "cand-7893", "cand-1087", "cand-0593"], relation=True),
        new_statement("st-chp8-p234-fumiani-programme-content", "cand-7893", None,
            "programme_specified_architectural_background_guards_and_david_at_prayer", (283, 284),
            "The programme called for an architectural background with guards and David praying in the foreground.",
            quotes["programme_content"], note="These are requested contents of the composition, not evidence that they were executed.",
            mentioned=["cand-7893", "cand-4268", "cand-0593"], relation=False),
        new_statement("st-chp8-p234-cassana-david-figure-assignment", "cand-0593", "cand-7893",
            "was_to_paint_david_figure_in_fumiani_composition", (284, 284),
            "Haskell says Cassana was to paint the figure of David in Fumiani's composition.",
            quotes["cassana_david"], note="This is the planned assignment; the passage does not establish that Cassana completed the figure.",
            mentioned=["cand-0593", "cand-7893", "cand-4268", "cand-1087"], relation=True),
        new_statement("st-chp8-p234-fumiani-option-to-paint-david", "cand-1087", "cand-7893",
            "could_paint_david_figure_if_he_insisted", (284, 284),
            "Haskell says Fumiani could paint David himself if he insisted, with the figure open to later change.",
            quotes["fumiani_option"], note="The source presents this as a conditional alternative to Cassana's planned role, not a completed collaboration.",
            mentioned=["cand-1087", "cand-0593", "cand-7893", "cand-4268"], relation=True),
        new_statement("st-chp8-p234-fumiani-modello-for-composition", NEW_MODELO_ID, "cand-7893",
            "was_modello_for_fumiani_composition", (284, 284),
            "The modello sent for Ferdinand's inspection was for the unidentified Fumiani composition.",
            quotes["model_request"], note="The specific preparatory model is distinguished from the proposed finished composition.",
            mentioned=[NEW_MODELO_ID, "cand-7893", "cand-1674", "cand-1087", "cand-1609"], relation=True),
        new_statement("st-chp8-p234-ferdinand-required-modello", "cand-1609", NEW_MODELO_ID,
            "required_modello_to_be_sent_for_inspection", (284, 284),
            "Haskell says Ferdinand required the modello to be sent to him for inspection.",
            quotes["model_request"], note="The source does not specify whether Fumiani or Cassana was responsible for sending the modello.",
            mentioned=["cand-1609", NEW_MODELO_ID, "cand-7893", "cand-1087", "cand-0593"], relation=True),
        new_statement("st-chp8-p234-modello-approved", "cand-1609", NEW_MODELO_ID,
            "modello_was_judged_satisfactory", (284, 284),
            "Haskell says the arrived modello proved satisfactory before Ferdinand requested changes to David's movement.",
            quotes["model_approval"], note="The clause does not explicitly name the evaluator; the next clause reports Ferdinand's comments. This remains an attributed appraisal.",
            mentioned=["cand-1609", NEW_MODELO_ID, "cand-7893"], relation=False),
        new_statement("st-chp8-p234-david-movement", "cand-1609", "cand-7893",
            "requested_more_movement_in_david_figure", (284, 284),
            "Haskell reports that Ferdinand wanted David to display more movement.", quotes["david_movement"],
            note="This is a reported design instruction for the proposed composition; it does not establish that the change was made.",
            mentioned=["cand-1609", "cand-7893", "cand-4268"], relation=True,
            speaker="Ferdinand as reported by Haskell", text_layer="reported instruction"),
        new_statement("st-chp8-p234-angel-punishments", "cand-1609", "cand-7893",
            "suggested_flying_angel_with_flaming_sword_and_three_punishments", (284, 284),
            "Haskell says Ferdinand suggested improving the composition with a flying angel carrying a flaming sword and offering the king a choice of three punishments.",
            quotes["angel_punishments"], note="This is Ferdinand's reported proposal, not evidence that the angel or sword was painted.",
            mentioned=["cand-1609", "cand-7893", "cand-4268"], relation=True,
            speaker="Ferdinand as reported by Haskell", text_layer="reported proposal"),
        new_statement("st-chp8-p234-david-surprise", "cand-1609", "cand-7893",
            "specified_david_should_show_surprise", (284, 284),
            "Haskell says Ferdinand wanted David to show great surprise.", quotes["david_surprise"],
            note="This is a reported figure instruction for the proposed composition; execution is not established.",
            mentioned=["cand-1609", "cand-7893", "cand-4268"], relation=True,
            speaker="Ferdinand as reported by Haskell", text_layer="reported instruction"),
        new_statement("st-chp8-p234-david-attributes", "cand-1609", "cand-7893",
            "suggested_harp_sceptre_and_diadem_beside_david", (284, 284),
            "Haskell says Ferdinand proposed enriching the composition by placing David's harp, sceptre, and diadem beside him.",
            quotes["david_attributes"], note="The proposed attributes are not evidence that they were included in a completed painting.",
            mentioned=["cand-1609", "cand-7893", "cand-4268"], relation=True,
            speaker="Ferdinand as reported by Haskell", text_layer="reported proposal",
            ocr_corrections=[{"source_line": 284, "ocr": "lais sceptre", "print": "his sceptre", "basis": "CHP-8.pdf physical page 40"}]),
        new_statement("st-chp8-p234-zechariah-inventory-record", "cand-7939", "cand-7936",
            "stoning_of_zechariah_recorded_in_1716_inventory", (284, 284),
            "Haskell says The Stoning of Zechariah was recorded in Ferdinand's 1716 inventory.",
            quotes["zechariah_inventory"], note="Footnote 3 identifies the inventory as the 1716 inventory; it was not independently consulted.",
            mentioned=["cand-7939", "cand-7936", "cand-1609"], relation=True),
        new_statement("st-chp8-p234-zechariah-uffizi-location", "cand-7939", "cand-7945",
            "stoning_of_zechariah_reported_at_uffizi", (284, 284),
            "Haskell says The Stoning of Zechariah is now at the Uffizi.", quotes["zechariah_uffizi"],
            note="The source names the Uffizi, but the candidate's distinction between institution and physical gallery remains unresolved.",
            mentioned=["cand-7939", "cand-7945"], relation=True),
        new_statement("st-chp8-p234-subjects-as-compositional-pretexts", "cand-1609", None,
            "haskell_saw_unusual_subjects_as_pretexts_for_fanciful_composition", (284, 284),
            "Haskell says the unusual subjects had no special significance for Ferdinand beyond serving as pretexts for fanciful composition.",
            quotes["subject_interpretation"], note="This is Haskell's interpretation of Ferdinand's motives, not an independently established fact or a discrete relation.",
            mentioned=["cand-1609", "cand-7893", "cand-7939"], relation=False),
        new_statement("st-chp8-p234-cassana-portraits-group", "cand-0593", NEW_PORTRAITS_ID,
            "painted_portraits_of_ferdinand_and_his_household", (285, 285),
            "Haskell says Cassana visited Florence chiefly to paint portraits of Ferdinand and his household.",
            quotes["cassana_portraits"], note="The passage identifies a work group by painter and sitters but gives no count, individual portrait identities, or present locations.",
            mentioned=["cand-0593", "cand-1609", NEW_PORTRAITS_ID, "cand-3397"], relation=True),
        new_statement("st-chp8-p234-cassana-florence-visits", "cand-0593", "cand-3397",
            "visited_florence_on_various_occasions_to_paint_princely_portraits", (285, 285),
            "Haskell says Cassana visited Florence on various occasions chiefly to paint portraits of the Prince and his household.",
            quotes["cassana_portraits"], note="The source gives repeated visits but no dates; the portrait group is separately registered as an open work candidate.",
            mentioned=["cand-0593", "cand-3397", "cand-1609", NEW_PORTRAITS_ID], relation=True),
        new_statement("st-chp8-p234-cassana-sent-pictures-from-venice", "cand-0593", "cand-3401",
            "sent_unspecified_pictures_from_venice", (285, 286),
            "Haskell says Cassana sent pictures from Venice from time to time.", quotes["cassana_sent"],
            note="Venice is the stated origin; the passage does not identify the pictures, destination, or recipient.",
            mentioned=["cand-0593", "cand-3401"], relation=True),
        new_statement("st-chp8-p234-cook-realistic-details", "cand-1609", "cand-7940",
            "commented_on_cooks_portraits_realistic_details", (287, 287),
            "Haskell reports that Ferdinand commented on the Portrait of a Cook's realistic details.", quotes["cook_details"],
            note="This is a reported aesthetic observation, not an independently verified quality assessment.",
            mentioned=["cand-1609", "cand-7940"], relation=False,
            speaker="Ferdinand as reported by Haskell", text_layer="reported appraisal"),
        new_statement("st-chp8-p234-cook-sitter-identity", "cand-1609", "cand-7940",
            "wanted_to_know_identity_of_cooks_portrait_sitter", (287, 287),
            "Haskell says Ferdinand particularly wanted to know who the sitter in the portrait was.", quotes["cook_sitter"],
            note="The sitter remains unidentified; the statement records Ferdinand's reported question, not a relation to an identified sitter.",
            mentioned=["cand-1609", "cand-7940"], relation=False,
            speaker="Ferdinand as reported by Haskell", text_layer="reported inquiry"),
        new_statement("st-chp8-p234-cook-painterly-quality", "cand-1609", "cand-7940",
            "praised_cooks_portraits_venetian_painterly_quality", (287, 287),
            "Haskell reports Ferdinand praised the portrait's bold Venetian painterly quality and contrasted it with the timid efforts of native Florentine artists.",
            quotes["cook_quality"], note="This is an attributed aesthetic comparison; no individual Florentine artist is named.",
            mentioned=["cand-1609", "cand-7940", "cand-5756", "cand-3397"], relation=False,
            speaker="Ferdinand as reported by Haskell", text_layer="reported appraisal"),
        new_statement("st-chp8-p234-cassana-venus-work", "cand-0593", "cand-7942",
            "painted_venus_playing_with_cupid_for_ferdinand", (287, 287),
            "Haskell lists an unidentified Venus playing with Cupid among Cassana's history pictures for the Grand Prince.",
            quotes["cassana_venus"], note="The work is identified by subject only; no date or present location is supplied.",
            mentioned=["cand-0593", "cand-1609", "cand-7942"], relation=True),
        new_statement("st-chp8-p234-catiline-work-for-ferdinand", "cand-0593", "cand-7943",
            "painted_conspiracy_of_catiline_for_ferdinand", (287, 287),
            "Haskell says Cassana also painted a Conspiracy of Catiline for the Grand Prince.",
            quotes["cassana_catiline"], note="Footnote 5 says this is probably a copy after Rosa and identifies Pitti no. 111; the attribution and location were not independently checked.",
            mentioned=["cand-0593", "cand-1609", "cand-7943", "cand-7662"], relation=True),
        new_statement("st-chp8-p234-langetti-portrait-in-medici-collection", "cand-7946", "cand-7948",
            "ratti_reported_langetti_portrait_seen_in_medici_collection", (289, 289),
            "Haskell says Ratti reported seeing a portrait by Langetti in the Medici collection.",
            quotes["langetti_pictures"], note="This is Ratti's report as cited by Haskell; the work and repository are unidentified, and the repository candidate's type/location remain unresolved.",
            mentioned=["cand-1363", "cand-7946", "cand-7948", "cand-5160"], relation=True,
            speaker="Ratti as reported by Haskell", text_layer="page-end note/report",
            ocr_corrections=[{"source_line": 289, "ocr": "Ratti, H, 26", "print": "Ratti, II, 26", "basis": "CHP-8.pdf physical page 40"}]),
        new_statement("st-chp8-p234-langetti-card-players-in-medici-collection", "cand-7947", "cand-7948",
            "ratti_reported_langetti_card_players_picture_seen_in_medici_collection", (289, 289),
            "Haskell says Ratti reported seeing a card-players picture by Langetti in the Medici collection.",
            quotes["langetti_pictures"], note="This is Ratti's report as cited by Haskell; the work and repository are unidentified, and the repository candidate's type/location remain unresolved.",
            mentioned=["cand-1363", "cand-7947", "cand-7948", "cand-5160"], relation=True,
            speaker="Ratti as reported by Haskell", text_layer="page-end note/report",
            ocr_corrections=[{"source_line": 289, "ocr": "Ratti, H, 26", "print": "Ratti, II, 26", "basis": "CHP-8.pdf physical page 40"}]),
        new_statement("st-chp8-p234-langetti-chronology-objection", "cand-1363", "cand-1609",
            "haskell_rejected_langetti_employment_claim_on_chronological_grounds", (289, 289),
            "Haskell says Langetti died in 1676, when Ferdinand was only eleven, and therefore could not have been employed by him in Florence.",
            quotes["langetti_chronology"], note="This is Haskell's chronological objection to Ratti's report, not an independently verified biographical conclusion or a relation.",
            mentioned=["cand-1363", "cand-1609", "cand-3397", "cand-5160"], relation=False,
            text_layer="page-end note/report"),
    ]

    # Add two source-local work candidates: the individual modello and the identified-by-sitters portrait group.
    candidate_additions = [
        {"candidate_id": NEW_MODELO_ID, "index_entry_id": "", "canonical_name": "Modello for Fumiani's unidentified David composition submitted to Ferdinand",
         "index_page_range": "", "suggested_type": "work", "status": "open", "index_source_file": "", "sub_entry": "",
         "detail": "A specific preparatory modello for cand-7893; Haskell says it arrived for Ferdinand's inspection and was satisfactory. Its medium, completion history, and present location are not given.",
         "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": "chp-8:08_CHP-8_sec_ii:l281-289#L284"},
        {"candidate_id": NEW_PORTRAITS_ID, "index_entry_id": "", "canonical_name": "Portraits of Grand Prince Ferdinand and his household by Niccolò Cassana",
         "index_page_range": "", "suggested_type": "work", "status": "open", "index_source_file": "", "sub_entry": "",
         "detail": "An unidentified portrait group named as the purpose of Cassana's repeated Florence visits; count, individual sitters beyond the Prince and household, and present locations are unspecified.",
         "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": "chp-8:08_CHP-8_sec_ii:l281-289#L285"},
    ]
    portrait_mention = {"mention_id": "m-chp8-p234-cassana-portraits-group", "segment_id": SEGMENT,
        "candidate_id": NEW_PORTRAITS_ID, "surface_form": "portraits", "start_char": str(portrait_span[0]),
        "end_char": str(portrait_span[1]), "note": "Work-group noun; the source identifies Cassana as painter and Ferdinand and his household as sitters."}
    mention_by_id["m-chp8-p234-modello"]["candidate_id"] = NEW_MODELO_ID
    mention_by_id["m-chp8-p234-modello"]["note"] = "Specific preparatory model for the Fumiani composition; registered as its own work candidate."
    mention_by_id["m-chp8-p234-ferdinand-inventory"]["candidate_id"] = "cand-7936"
    mention_by_id["m-chp8-p234-ferdinand-inventory"]["note"] = "The 1716 collection inventory; note 3 identifies the record."
    mentions.append(portrait_mention)
    candidates.extend(candidate_additions)
    candidate_by_id.update({row["candidate_id"]: row for row in candidate_additions})

    # Keep the p.234 notes connected to the newly atomic body claims.
    additions_by_id = {row["statement_id"]: row for row in additions}
    for statement_id in old_model_note_links:
        if statement_id not in by_id:
            raise SystemExit(f"missing linked p.234 note statement: {statement_id}")
        add_link(by_id[statement_id], "linked_body_statement_ids", "st-chp8-p234-angel-punishments")
        old_links = by_id[statement_id]["qualifiers"].get("linked_body_statement_ids", [])
        if "st-chp8-p234-fumiani-model-review" in old_links:
            old_links.remove("st-chp8-p234-fumiani-model-review")
    for note_statement_id in (note_ids["stoning"],):
        for body_id in ("st-chp8-p234-zechariah-inventory-record", "st-chp8-p234-zechariah-uffizi-location"):
            add_link(by_id[note_statement_id], "linked_body_statement_ids", body_id)
            add_link(additions_by_id[body_id], "linked_note_statement_ids", note_statement_id)
    catiline_note = by_id[note_ids["catiline"]]
    add_link(catiline_note, "linked_body_statement_ids", "st-chp8-p234-catiline-work-for-ferdinand")
    catiline_row = additions_by_id["st-chp8-p234-catiline-work-for-ferdinand"]
    add_link(catiline_row, "linked_note_statement_ids", note_ids["catiline"])

    new_ids = {row["statement_id"] for row in additions}
    if len(additions) != 25 or len(new_ids) != len(additions) or new_ids & set(by_id):
        raise SystemExit(f"unexpected or duplicate p.234 atomic statements: {len(additions)}")
    if {row["candidate_id"] for row in candidate_additions} != {NEW_MODELO_ID, NEW_PORTRAITS_ID}:
        raise SystemExit("unexpected p.234 candidate additions")
    final_target = target_rows + additions
    all_candidate_ids = set(candidate_by_id)
    for row in final_target:
        q = row["qualifiers"]
        if q.get("relation_candidate") not in (True, False):
            raise SystemExit(f"p.234 statement remains unclassified: {row['statement_id']}")
        refs = set(q.get("mentioned_candidate_ids", []))
        refs.update(x for x in (row.get("subject_candidate_id"), row.get("object_candidate_id")) if x)
        if missing := refs - all_candidate_ids:
            raise SystemExit(f"unknown candidate refs in {row['statement_id']}: {sorted(missing)}")
    if any(row["statement_id"] in new_ids for row in additions) is False:
        raise SystemExit("p.234 new statement IDs did not persist in plan")

    counts = {"true": 0, "false": 0, "unset": 0}
    for row in final_target:
        value = row["qualifiers"]["relation_candidate"]
        counts["true" if value is True else "false"] += 1
    coverage_row["note"] += (
        " Semantic review 2026-10-14 rechecked all 9 existing statements against CHP-8.pdf physical page 40; "
        "split Fumiani's design programme, model receipt/approval and individual revisions; separated Cassana's work roles, "
        "portrait group, Florence visits, Venice dispatches and three named history pictures; split the Cook portrait's arrival "
        "from Ferdinand's reported appraisals; and separated Ratti's Langetti report from Haskell's chronological objection. "
        "Added two source-local work candidates (the specific modello and Cassana portrait group), remapped the model and 1716 inventory mentions, "
        "and linked body claims to existing notes 3 and 5. No KU or formal S6 relation was created."
    )
    preview = {
        "mode": "dry-run", "segment": SEGMENT, "pdf_physical_page": 40,
        "existing_statements_reviewed": len(target_rows), "new_statements": sorted(new_ids),
        "new_candidates": [row["candidate_id"] for row in candidate_additions],
        "new_mentions": [portrait_mention["mention_id"]],
        "mention_remaps": {"m-chp8-p234-modello": NEW_MODELO_ID, "m-chp8-p234-ferdinand-inventory": "cand-7936"},
        "final_statement_counts": counts, "quote_spans_verified": len(raw_quotes),
        "new_candidate_refs_checked": len(required_candidates),
        "existing_note_links_reused": list(note_ids.values()),
    }
    payload = {
        STATEMENTS: jsonl_bytes(statements + additions),
        CANDIDATES: csv_bytes(candidate_fields, candidates),
        MENTIONS: csv_bytes(mention_fields, mentions),
        COVERAGE: csv_bytes(read_csv(COVERAGE)[0], coverage),
    }
    return preview, payload


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="apply the preflighted p.234 S2 review")
args = parser.parse_args()
preview, payload = plan()
if not args.apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)
for path in (STATEMENTS, CANDIDATES, MENTIONS, COVERAGE):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(path, backup)
for path, data in payload.items():
    atomic_write(path, data)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
