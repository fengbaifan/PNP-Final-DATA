"""Guarded S2 semantic review for printed p.233, body lines 272-279."""
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
COVERAGE = TABLES / "s2-coverage.csv"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE = ROOT / SOURCE_REL
PDF = ROOT / "02-sources" / "01-book" / "CHP-8.pdf"
PAGE_IMAGE = ROOT / "scripts" / ".tmp_s2_chp8_p233_review_20261014.png"
SEGMENT = "chp-8:08_CHP-8_sec_ii:l271-279"
BACKUP_SUFFIX = ".bak-s2-chp8-p233-l271-279-semantic-review-20261014"
EXPECTED = {
    STATEMENTS: "8aeab006e147b2a7101ba5db88c6c42256a7ef9d346df4fa180c41b6ea2499e1",
    CANDIDATES: "40bbc368b7286291604c132b3d1c577d554dba1f13906801bc67f88210e9832d",
    COVERAGE: "15c271191dcbc3445aa380930f6e9165d0bc0520bea5bb5c94a928722fd69bf3",
    SOURCE: "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    PDF: "cb11451ac726f37ed5badf21a569af88f790f858f1c39eb63f2efb58a0fe4ac3",
    PAGE_IMAGE: "97dd94e2437c31f05175b83094e0077ffd44a16fa78a336c6cee001e7f3d7f19",
}
EXPECTED_STATEMENTS = {
    "st-chp8-p233-bassi-loyalty",
    "st-chp8-p233-gabbiani-1699-visit",
    "st-chp8-p233-gabbiani-control-and-venetian-ambition",
    "st-chp8-p233-gabbiani-employment",
    "st-chp8-p233-loth-and-responsive-artist",
    "st-chp8-p233-loth-employment",
    "st-chp8-p233-modelli-purposes",
    "st-chp8-p233-painting-process",
    "st-chp8-p233-sacconi-colour-and-exhibition",
    "st-chp8-p233-sacconi-orders",
    "st-chp8-p233-sacconi-outcome",
    "st-chp8-p233-sacconi-patronage",
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


def set_review(row, *, subject, object_, predicate, lines, claim, quote, note,
               mentioned, relation, speaker="Haskell", text_layer="body", speaker_judgment=True):
    row["subject_candidate_id"] = subject
    row["object_candidate_id"] = object_
    row["predicate"] = predicate
    row["original_quote"] = quote
    row["qualifiers"].update({
        "source_line_start": lines[0],
        "source_line_end": lines[1],
        "printed_page": 233,
        "pdf_physical_page": 39,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": note,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation,
        "relation_candidate_note": note,
        "speaker_judgment": speaker_judgment,
    })


def new_statement(statement_id, subject, object_, predicate, lines, claim, quote, *, note,
                  mentioned, relation, speaker="Haskell", text_layer="body", speaker_judgment=True):
    row = {
        "statement_id": statement_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": {},
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_REL,
    }
    set_review(row, subject=subject, object_=object_, predicate=predicate, lines=lines,
               claim=claim, quote=quote, note=note, mentioned=mentioned, relation=relation,
               speaker=speaker, text_layer=text_layer, speaker_judgment=speaker_judgment)
    return row


def plan():
    for path, expected in EXPECTED.items():
        actual = sha(path.read_bytes())
        if actual != expected:
            raise SystemExit(f"input changed: {path.relative_to(ROOT)} sha256={actual}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    if sha("\n".join(source_lines[270:279]).encode("utf-8")) != read_jsonl(SEGMENTS)[
            next(i for i, row in enumerate(read_jsonl(SEGMENTS)) if row["segment_id"] == SEGMENT)
        ]["sha256"]:
        raise SystemExit("p.233 source segment hash mismatch")
    meta = next((row for row in read_jsonl(SEGMENTS) if row["segment_id"] == SEGMENT), None)
    if not meta or (meta["line_start"], meta["line_end"]) != (271, 279):
        raise SystemExit("unexpected p.233 segment metadata")

    candidate_fields, candidates = read_csv(CANDIDATES)
    candidate_ids = {row["candidate_id"] for row in candidates}
    required_candidates = {
        "cand-0259", "cand-0593", "cand-1087", "cand-1093", "cand-1100", "cand-1156",
        "cand-1442", "cand-1609", "cand-1625", "cand-1674", "cand-2325", "cand-2340",
        "cand-3401", "cand-6024", "cand-7873", "cand-7918", "cand-7919", "cand-7920",
        "cand-7921", "cand-7922", "cand-7923", "cand-7938",
    }
    if missing := required_candidates - candidate_ids:
        raise SystemExit(f"required p.233 candidates missing: {sorted(missing)}")

    statements = read_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statements}
    target_rows = [row for row in statements if row.get("segment_id") == SEGMENT]
    if len(target_rows) != 12 or {row["statement_id"] for row in target_rows} != EXPECTED_STATEMENTS:
        raise SystemExit(f"unexpected p.233 statement set: {len(target_rows)} rows")
    if any(row.get("qualifiers", {}).get("relation_candidate") not in (True, False, None) for row in target_rows):
        raise SystemExit("p.233 has an invalid relation_candidate value")

    _, coverage = read_csv(COVERAGE)
    coverage_row = next((row for row in coverage if row["segment_id"] == SEGMENT), None)
    if not coverage_row or (coverage_row["disposition"], coverage_row["migration_status"]) != ("reviewed", "complete"):
        raise SystemExit(f"unexpected p.233 coverage state: {coverage_row}")

    l272, l273, l274, l275, l276, l277, l278, l279 = (source_lines[n - 1] for n in range(272, 280))
    p233_text = "\n".join(source_lines[271:279])
    quotes = {
        "bassi": cut(l274, "It may have been that same feeling of loyalty", " landscape painter", include_end=True) + "\n" +
                 cut(l275, "Francesco Bassi", "work.", include_end=True),
        "gabbiani_employment": cut(l273, "he employed for so long", " painter", include_end=True),
        "gabbiani_style": cut(l274, "Florentine artists such as", " tastes", include_end=True),
        "gabbiani_puzzle": cut(l273, "The reasons why") + "\n" +
                           cut(l274, "Florentine artists such as", " fathom.", include_end=True),
        "gabbiani_control": cut(l275, "More likely", "ambitions.", include_end=True),
        "gabbiani_visit": cut(l275, "a special visit to Venice which", " colour.", include_end=True),
        "gabbiani_outcome": cut(l275, "Whatever the reasons, the outcome", " very successful", include_end=True),
        "modelli_purposes": cut(l272, "much for purely aesthetic reasons", " content.", include_end=True),
        "modelli_collected": cut(l272, "Indeed he collected modelli", " later became.", include_end=True),
        "painting_process": cut(l272, "He enjoyed watching artists at work", " so on.", include_end=True),
        "sacconi_interest": cut(l276, "Prince took the deepest interest", " career.", include_end=True),
        "sacconi_financial": cut(l276, "He provided for him financially", " and kept him working"),
        "sacconi_cassana": cut(l276, "and kept him working under", " Cassana.", include_end=True),
        "sacconi_sent_venice": cut(l275, "though he too was sent to", "Venice.", include_end=True),
        "sacconi_st_sebastian": cut(l276, "for a St Sebastian", " a St Giustina"),
        "sacconi_st_giustina": cut(l276, "a St Giustina", " a Bacchanal"),
        "sacconi_bacchanal": cut(l276, "a Bacchanal", ".", include_end=True),
        "sacconi_learning": cut(l276, "as he must learn to paint full length figures", "’", include_end=True),
        "sacconi_colour": cut(l276 + "\n" + l277, "Ferdinand notes that his colour is improving under", "guidance", include_end=True),
        "sacconi_warning": cut(l277, "but warns him", "‘meno flemmatico’. ", include_end=True),
        "sacconi_exhibition": cut(l277, "He arranges for his pictures", "Corpus Domini", include_end=True),
        "sacconi_humour": cut(l277, "and is delighted with their humour", ".", include_end=True),
        "sacconi_outcome": cut(l277, "But it seems that not even Venice", " artist.", include_end=True),
        "loth_employment": cut(l279, "this German artist was already painting for him", " seven years later.", include_end=True),
        "loth_first_visit": cut(l279, "Karl Loth with whom he must have got in touch on his first visit", ", for this German"),
        "loth_figures": cut(l279, "although he made particular efforts to get hold", ", Ferdinand had already"),
        "responsive_artist": cut(l279, "Ferdinand had already paid his second visit", " The"),
    }
    for quote in quotes.values():
        if quote not in p233_text:
            raise SystemExit(f"quote is not an exact p.233 source span: {quote!r}")

    # Keep the original stable IDs for existing claims while making their scopes atomic.
    set_review(by_id["st-chp8-p233-bassi-loyalty"], subject="cand-1609", object_="cand-0259",
               predicate="may_have_protected_bassi_out_of_loyalty_despite_doubts", lines=(274, 275),
               claim="Haskell suggests Ferdinand may have taken particular trouble not to hurt the ageing landscape painter Francesco Bassi despite doubts about the value of Bassi's work.",
               quote=quotes["bassi"], note="Haskell presents loyalty as a possible motive, not an established fact; the doubts concern the value of Bassi's work.",
               mentioned=["cand-1609", "cand-0259"], relation=True)
    set_review(by_id["st-chp8-p233-gabbiani-1699-visit"], subject="cand-1093", object_="cand-7922",
               predicate="visited_venice_in_1699_to_improve_colour_for_ferdinand", lines=(275, 275),
               claim="Haskell says Gabbiani made a special visit to Venice in 1699, aged 47, to oblige Ferdinand by improving his colour.",
               quote=quotes["gabbiani_visit"], note="The visit and its stated purpose are reported by Haskell; the outcome is recorded separately as his evaluation.",
               mentioned=["cand-1093", "cand-7922", "cand-3401", "cand-1609"], relation=True)
    set_review(by_id["st-chp8-p233-gabbiani-control-and-venetian-ambition"], subject="cand-1609", object_="cand-1093",
               predicate="haskell_speculates_ferdinand_saw_gabbiani_as_a_means_for_venetian_artistic_ambitions", lines=(275, 275),
               claim="Haskell speculates that Ferdinand's sense of control over Gabbiani, who professed attachment to Venetian painting, could help express Ferdinand's artistic ambitions.",
               quote=quotes["gabbiani_control"], note="This is Haskell's proposed explanation, signalled by 'More likely'; it is not independently established evidence of Ferdinand's motive.",
               mentioned=["cand-1609", "cand-1093", "cand-5756", "cand-1622"], relation=True)
    set_review(by_id["st-chp8-p233-gabbiani-employment"], subject="cand-1609", object_="cand-1093",
               predicate="employed_gabbiani_for_a_long_period", lines=(273, 273),
               claim="Haskell says Ferdinand employed Gabbiani for a long time.", quote=quotes["gabbiani_employment"],
               note="This records the reported employment only; Haskell's stylistic comparison and inability to explain Ferdinand's preference are separate judgments.",
               mentioned=["cand-1609", "cand-1093"], relation=True)
    set_review(by_id["st-chp8-p233-loth-and-responsive-artist"], subject="cand-1609", object_="cand-1087",
               predicate="found_fumiani_responsive_to_his_patronal_pressure_on_second_venice_visit", lines=(279, 279),
               claim="Haskell says Ferdinand had made a second visit to Venice and found an artist there who, despite mediocre abilities, was ideally responsive to the kind of pressure Ferdinand liked to exert.",
               quote=quotes["responsive_artist"], note="P.233 calls the painter only 'an artist'; p.234 L282 identifies Fumiani in the immediately following account. The identification is contextual, and the claim does not name a particular commission.",
               mentioned=["cand-1609", "cand-1087", "cand-3401", "cand-7938"], relation=True)
    responsive = by_id["st-chp8-p233-loth-and-responsive-artist"]
    loth_continuation_fields = {
        "continuation_status": "closed",
        "continuation_to_segment_id": "chp-8:08_CHP-8_sec_ii:l281-289",
        "continuation_to_source_line": 282,
        "continued_to_segment_id": "chp-8:08_CHP-8_sec_ii:l281-289",
        "continued_to_source_line": 282,
        "continuation_closed_by_statement_id": "st-chp8-p234-fumiani-relations",
    }
    responsive["qualifiers"].update(loth_continuation_fields)
    set_review(by_id["st-chp8-p233-loth-employment"], subject="cand-1609", object_="cand-1442",
               predicate="employed_loth_by_1691_until_about_seven_years_later", lines=(279, 279),
               claim="Haskell says Karl Loth was painting for Ferdinand by 1691 and continued until his death about seven years later.",
               quote=quotes["loth_employment"], note="The date of the first contact is an inference and is recorded separately; the death interval remains relative, not converted into an exact year.",
               mentioned=["cand-1609", "cand-1442"], relation=True)
    loth_employment = by_id["st-chp8-p233-loth-employment"]
    for key in loth_continuation_fields:
        loth_employment["qualifiers"].pop(key, None)
    modelli = by_id["st-chp8-p233-modelli-purposes"]
    set_review(modelli, subject="cand-1609", object_="cand-1674",
               predicate="inspected_modelli_for_aesthetic_and_content_accuracy_reasons", lines=(272, 272),
               claim="Completing the p.232 sentence, Haskell says Ferdinand wanted to see modelli for aesthetic reasons as well as to check the accuracy of their content.",
               quote=quotes["modelli_purposes"], note="This closes the p.232 continuation. It describes a general practice and identifies no particular model or commissioned picture.",
               mentioned=["cand-1609", "cand-1674"], relation=False)
    modelli["qualifiers"].update({
        "continued_from_segment_id": "chp-8:08_CHP-8_sec_ii:l251-257",
        "continued_from_statement_id": "st-chp8-p232-modelli-order-and-review-open",
        "continuation_status": "closed",
    })
    set_review(by_id["st-chp8-p233-painting-process"], subject="cand-1609", object_=None,
               predicate="watched_artists_and_discussed_painting_procedure", lines=(272, 272),
               claim="Haskell says Ferdinand enjoyed watching artists work and discussing practical painting procedures, including colours and canvas thickness.",
               quote=quotes["painting_process"], note="The passage names no artists or particular painting; it remains a general description of Ferdinand's interests.",
               mentioned=["cand-1609", "cand-3571"], relation=False)
    set_review(by_id["st-chp8-p233-sacconi-colour-and-exhibition"], subject="cand-1609", object_="cand-2325",
               predicate="noted_sacconis_colour_was_improving_under_cassana", lines=(276, 277),
               claim="Haskell reports that Ferdinand noted Sacconi's colour was improving under Cassana's guidance.",
               quote=quotes["sacconi_colour"], note="This is an attributed appraisal reported by Haskell, not a formal relation or an independently checked letter.",
               mentioned=["cand-1609", "cand-2325", "cand-0593"], relation=False,
               speaker="Ferdinand as reported by Haskell", text_layer="reported appraisal")
    set_review(by_id["st-chp8-p233-sacconi-orders"], subject="cand-1609", object_="cand-7919",
               predicate="ordered_st_sebastian_subject_painting_for_sacconi", lines=(276, 276),
               claim="Haskell reports that an order followed Sacconi for a St Sebastian painting, tied to the need for him to learn full-length figures.",
               quote=quotes["sacconi_st_sebastian"], note="This is an order for a subject painting; it does not establish that the work was completed.",
               mentioned=["cand-1609", "cand-2325", "cand-7919"], relation=True)
    set_review(by_id["st-chp8-p233-sacconi-outcome"], subject="cand-1609", object_="cand-2325",
               predicate="haskell_judged_sacconi_unsuccessful_despite_venice_and_encouraging_patronage", lines=(277, 277),
               claim="Haskell judges that even Venice and an encouraging patron could not make much of Sacconi as an artist.",
               quote=quotes["sacconi_outcome"], note="This is Haskell's evaluative conclusion about Sacconi, not a discrete relationship or an independently verified assessment.",
               mentioned=["cand-1609", "cand-2325", "cand-3401"], relation=False)
    set_review(by_id["st-chp8-p233-sacconi-patronage"], subject="cand-1609", object_="cand-2325",
               predicate="provided_financial_support_to_sacconi_after_his_father_died", lines=(276, 276),
               claim="Haskell says Ferdinand provided for Sacconi financially after Sacconi's father died.",
               quote=quotes["sacconi_financial"], note="The support is explicit; the passage does not name Sacconi's father or give the amount or date.",
               mentioned=["cand-1609", "cand-2325", "cand-7918"], relation=True)

    additions = [
        new_statement("st-chp8-p233-florentine-artists-better-fit", "cand-1609", None,
            "haskell_judged_other_florentine_artists_styles_closer_to_ferdinands_taste", (274, 274),
            "Haskell says Gherardini, Sagrestani, and Galeotti had styles that corresponded more closely to Ferdinand's tastes than Gabbiani's did.",
            quotes["gabbiani_style"], note="This is Haskell's comparative aesthetic judgment, not a formal relation to the three painters.",
            mentioned=["cand-1609", "cand-1156", "cand-2340", "cand-1100", "cand-3397", "cand-1625"], relation=False),
        new_statement("st-chp8-p233-gabbiani-preference-unfathomable", "cand-1609", "cand-1093",
            "haskell_said_ferdinands_reason_for_long_gabbiani_preference_was_impossible_to_fathom", (273, 274),
            "Haskell says Ferdinand's reasons for employing Gabbiani for so long while overlooking other Florentine artists are impossible to fathom.",
            quotes["gabbiani_puzzle"], note="This preserves Haskell's explicit uncertainty about Ferdinand's preference; it does not supply a motive.",
            mentioned=["cand-1609", "cand-1093", "cand-1156", "cand-2340", "cand-1100"], relation=False),
        new_statement("st-chp8-p233-gabbiani-outcome", "cand-1609", "cand-1093",
            "haskell_judged_outcome_of_gabbiani_patronage_unsuccessful", (275, 275),
            "Haskell judges the outcome of Ferdinand's dealings with Gabbiani as hardly successful.",
            quotes["gabbiani_outcome"], note="This is Haskell's evaluative judgment; the text does not isolate the 1699 visit as the sole cause.",
            mentioned=["cand-1609", "cand-1093"], relation=False),
        new_statement("st-chp8-p233-modelli-collected-for-other-patrons", "cand-1609", "cand-1674",
            "collected_modelli_of_pictures_painted_for_other_patrons_before_the_practice_was_common", (272, 272),
            "Haskell says Ferdinand collected modelli of pictures made for other patrons before this became common practice.",
            quotes["modelli_collected"], note="The statement concerns an unspecified class of models and pictures, not a particular work or relation endpoint.",
            mentioned=["cand-1609", "cand-1674"], relation=False),
        new_statement("st-chp8-p233-sacconi-deep-interest", "cand-1609", "cand-2325",
            "took_a_deep_interest_in_sacconis_career", (276, 276),
            "Haskell says Ferdinand took a deep interest in Sacconi's career.", quotes["sacconi_interest"],
            note="This is Haskell's characterization of Ferdinand's personal patronage of Sacconi.",
            mentioned=["cand-1609", "cand-2325"], relation=True),
        new_statement("st-chp8-p233-sacconi-under-cassana", "cand-2325", "cand-0593",
            "worked_under_cassana_with_ferdinands_support", (276, 276),
            "Haskell says Ferdinand kept Sacconi working under Niccolò Cassana.", quotes["sacconi_cassana"],
            note="The stated work relationship is Sacconi under Cassana; Haskell attributes its continuation to Ferdinand's support.",
            mentioned=["cand-1609", "cand-2325", "cand-0593"], relation=True),
        new_statement("st-chp8-p233-sacconi-sent-to-venice", "cand-2325", "cand-3401",
            "was_sent_to_venice_agent_unspecified", (275, 275),
            "Haskell says Sacconi too was sent to Venice, without naming who sent him.", quotes["sacconi_sent_venice"],
            note="The passive wording leaves the agent unidentified; this statement does not attribute the act to Ferdinand.",
            mentioned=["cand-2325", "cand-3401"], relation=True),
        new_statement("st-chp8-p233-sacconi-st-giustina-order", "cand-1609", "cand-7920",
            "ordered_st_giustina_subject_painting_for_sacconi", (276, 276),
            "Haskell reports an order for a St Giustina painting for Sacconi.", quotes["sacconi_st_giustina"],
            note="This is an order for a subject painting; it does not establish that the work was completed.",
            mentioned=["cand-1609", "cand-2325", "cand-7920"], relation=True),
        new_statement("st-chp8-p233-sacconi-bacchanal-order", "cand-1609", "cand-7921",
            "ordered_bacchanal_subject_painting_for_sacconi", (276, 276),
            "Haskell reports an order for a Bacchanal painting for Sacconi.", quotes["sacconi_bacchanal"],
            note="This is an order for a subject painting; it does not establish that the work was completed.",
            mentioned=["cand-1609", "cand-2325", "cand-7921"], relation=True),
        new_statement("st-chp8-p233-sacconi-full-length-figure-instruction", "cand-1609", "cand-2325",
            "instructed_sacconi_to_learn_full_length_figure_painting", (276, 276),
            "Haskell says Ferdinand's St Sebastian order reflected the need for Sacconi to learn to paint full-length figures.",
            quotes["sacconi_learning"], note="The instruction is quoted in Haskell's account; the St Sebastian painting is separately recorded as an order.",
            mentioned=["cand-1609", "cand-2325", "cand-7919"], relation=True),
        new_statement("st-chp8-p233-sacconi-warning", "cand-1609", "cand-2325",
            "warned_sacconi_to_be_less_flemmatic", (277, 277),
            "Haskell reports that Ferdinand warned Sacconi to be meno flemmatico.", quotes["sacconi_warning"],
            note="This is a reported direct admonition from Ferdinand to Sacconi; the cited correspondence is not independently checked.",
            mentioned=["cand-1609", "cand-2325"], relation=True,
            speaker="Ferdinand as reported by Haskell", text_layer="reported instruction"),
        new_statement("st-chp8-p233-sacconi-corpus-domini-exhibition", "cand-1609", "cand-2325",
            "arranged_exhibition_of_sacconis_pictures_on_corpus_domini", (277, 277),
            "Haskell says Ferdinand arranged for Sacconi's pictures to be exhibited on Corpus Domini.", quotes["sacconi_exhibition"],
            note="The source identifies the painter and feast occasion but not the individual pictures or exhibition venue.",
            mentioned=["cand-1609", "cand-2325", "cand-6024"], relation=True),
        new_statement("st-chp8-p233-sacconi-picture-humour", "cand-1609", "cand-2325",
            "was_delighted_by_humour_of_sacconis_pictures", (277, 277),
            "Haskell says Ferdinand was delighted by the humour of Sacconi's pictures.", quotes["sacconi_humour"],
            note="This is Ferdinand's reported response to unspecified pictures; no individual work is identified and the statement is an appraisal, not a formal relation.",
            mentioned=["cand-1609", "cand-2325"], relation=False,
            speaker="Ferdinand as reported by Haskell", text_layer="reported appraisal"),
        new_statement("st-chp8-p233-loth-first-visit-contact", "cand-1609", "cand-1442",
            "haskell_inferred_contact_with_loth_on_first_venice_visit", (279, 279),
            "Haskell infers Ferdinand must have got in touch with Karl Loth on Ferdinand's first visit to Venice.",
            quotes["loth_first_visit"], note="Haskell marks the contact as an inference ('must have'); the passage does not independently date the first visit.",
            mentioned=["cand-1609", "cand-1442", "cand-3401"], relation=True),
        new_statement("st-chp8-p233-loth-half-length-figures", "cand-1609", "cand-7923",
            "sought_half_length_figures_by_loth", (279, 279),
            "Haskell says Ferdinand made particular efforts to obtain some half-length figures by Loth, whom Ferdinand considered best at them.",
            quotes["loth_figures"], note="The source reports an effort to obtain the figure paintings, not their acquisition; the work-group candidate remains unidentified.",
            mentioned=["cand-1609", "cand-1442", "cand-7923", "cand-7938"], relation=True),
    ]

    new_ids = {row["statement_id"] for row in additions}
    if len(additions) != 15 or len(new_ids) != len(additions) or new_ids & set(by_id):
        raise SystemExit("unexpected or duplicate p.233 atomic statements")
    final_target = target_rows + additions
    for row in final_target:
        q = row["qualifiers"]
        if q.get("relation_candidate") not in (True, False):
            raise SystemExit(f"p.233 statement remains unclassified: {row['statement_id']}")
        refs = set(q.get("mentioned_candidate_ids", []))
        refs.update(x for x in (row.get("subject_candidate_id"), row.get("object_candidate_id")) if x)
        if missing := refs - candidate_ids:
            raise SystemExit(f"unknown candidate refs in {row['statement_id']}: {sorted(missing)}")

    counts = {"true": 0, "false": 0, "unset": 0}
    for row in final_target:
        value = row["qualifiers"]["relation_candidate"]
        counts["true" if value is True else "false"] += 1
    coverage_row["note"] += (
        " Semantic review 2026-10-14 rechecked all 12 existing statements against CHP-8.pdf physical page 39; "
        "split aesthetic judgments from reported actions, separated Gabbiani's employment, proposed motive and visit outcome, "
        "closed the p.232 modelli continuation, split Loth's figures/contact/employment from the Fumiani cross-page account, "
        "and atomized Sacconi's support, Cassana work, Venice trip, three ordered subjects, instruction, warning, exhibition and appraisals. "
        "The unnamed agent who sent Sacconi to Venice remains unspecified. Fifteen atomic statements were added; no KU, mention, or formal relation was created."
    )

    preview = {
        "mode": "dry-run", "segment": SEGMENT, "pdf_physical_page": 39,
        "existing_statements_reviewed": len(target_rows),
        "new_statements": sorted(new_ids),
        "final_statement_counts": counts,
        "quote_spans_verified": len(quotes),
        "candidate_refs_checked": len(required_candidates),
        "continuation_closed": "st-chp8-p233-modelli-purposes",
        "cross_page_identity": "unnamed artist on p.233 linked contextually to Fumiani on p.234 L282",
    }
    payload = {
        STATEMENTS: jsonl_bytes(statements + additions),
        COVERAGE: csv_bytes(read_csv(COVERAGE)[0], coverage),
    }
    return preview, payload


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="apply the preflighted p.233 S2 semantic review")
args = parser.parse_args()
preview, payload = plan()
if not args.apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)
for path in (STATEMENTS, COVERAGE):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(path, backup)
for path, data in payload.items():
    atomic_write(path, data)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
