"""Guarded S2 semantic review for printed p.235, body and footnote 6 continuation."""
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
COVERAGE = TABLES / "s2-coverage.csv"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE = ROOT / SOURCE_REL
SEGMENT = "chp-8:08_CHP-8_sec_ii:l291-301"
BACKUP_SUFFIX = ".bak-s2-chp8-p235-l291-301-semantic-review-20261014"
EXPECTED = {
    STATEMENTS: "f51ea35b9e3fd75e4a5c352a46351cb68108bdecd0f0e54bd153acf6575bbb33",
    COVERAGE: "753ec3e24f2b108fac8def35d5e955a63f73af20ce9fc78adbf7d9457ecc4a42",
}
EXPECTED_STATEMENTS = {
    "st-chp8-p235-allegory-destroyed",
    "st-chp8-p235-crates-and-landscapes",
    "st-chp8-p235-giordano-pictures-and-visit",
    "st-chp8-p235-haskell-patronage-assessment",
    "st-chp8-p235-marucelli-patronage",
    "st-chp8-p235-note6-farsetti-quote-tail",
    "st-chp8-p235-poggio-visit-postponed",
    "st-chp8-p235-ricci-commission",
    "st-chp8-p235-ricci-contact-context",
    "st-chp8-p235-ricci-visit-and-cassana-advice",
    "st-chp8-p235-surviving-decorations",
}
NOTE_LINKS = {
    "st-chp8-p235-note1-letter75": ["st-chp8-p235-giordano-livorno-visit"],
    "st-chp8-p235-note1-martini": ["st-chp8-p235-giordano-worked-for-ferdinand"],
    "st-chp8-p235-note2-fogolari-letters": [
        "st-chp8-p235-ricci-commission",
        "st-chp8-p235-crucifixion-replaces-madonna",
        "st-chp8-p235-madonna-acquisition",
    ],
    "st-chp8-p235-note3-ricci-letters": [
        "st-chp8-p235-ricci-assists-cassana",
        "st-chp8-p235-cassana-market-duty",
    ],
    "st-chp8-p235-note4-letter197-and-exhibition": [
        "st-chp8-p235-crates-and-landscapes",
        "st-chp8-p235-shipment-includes-landscapes",
        "st-chp8-p235-marco-painted-landscapes",
    ],
    "st-chp8-p235-note5-letter200": [
        "st-chp8-p235-poggio-visit-postponed",
        "st-chp8-p235-ferdinand-postpones-poggio-scheme",
    ],
    "st-chp8-p235-note6-farsetti-reference": [
        "st-chp8-p235-allegory-destroyed",
        "st-chp8-p235-note6-farsetti-quote-tail",
    ],
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
               ocr_corrections=None):
    row["subject_candidate_id"] = subject
    row["object_candidate_id"] = object_
    row["predicate"] = predicate
    row["original_quote"] = quote
    q = row.setdefault("qualifiers", {})
    q.update({
        "source_line_start": lines[0], "source_line_end": lines[1],
        "printed_page": 235, "pdf_physical_page": 41,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": note, "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation, "relation_candidate_note": note,
        "speaker_judgment": speaker_judgment,
    })
    q.pop("ocr_corrections", None)
    if ocr_corrections:
        q["ocr_corrections"] = ocr_corrections
    q.pop("linked_note_statement_ids", None)


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


def set_note_links(by_id):
    for note_id, body_ids in NOTE_LINKS.items():
        note = by_id.get(note_id)
        if note is None:
            raise SystemExit(f"missing p.235 footnote statement: {note_id}")
        note.setdefault("qualifiers", {})["linked_body_statement_ids"] = body_ids
        for body_id in body_ids:
            body = by_id.get(body_id)
            if body is None:
                raise SystemExit(f"missing linked p.235 body statement: {body_id}")
            links = body.setdefault("qualifiers", {}).setdefault("linked_note_statement_ids", [])
            if note_id not in links:
                links.append(note_id)


def plan():
    for path, expected in EXPECTED.items():
        if sha(path.read_bytes()) != expected:
            raise SystemExit(f"input changed: {path.relative_to(ROOT)}")

    segments = read_jsonl(SEGMENTS)
    meta = next((row for row in segments if row["segment_id"] == SEGMENT), None)
    if not meta or (meta["line_start"], meta["line_end"]) != (291, 301):
        raise SystemExit("unexpected p.235 segment metadata")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[290:301])
    if sha(segment_text.encode("utf-8")) != meta["sha256"]:
        raise SystemExit("p.235 source segment hash mismatch")

    full_text = SOURCE.read_text(encoding="utf-8-sig")
    l292, l293, l294, l295, l296, l297, l298, l299, l300, l301 = (
        source_lines[n - 1] for n in range(292, 302)
    )
    quotes = {
        "giordano_glass": cut(l292, "Much more valuable were", "The great Neapolitan painter"),
        "giordano_visit": cut(l292 + "\n" + l293, "The great Neapolitan painter", " and is known to have worked"),
        "giordano_worked": cut(l293, "and is known to have worked", "1"),
        "assessment": cut(l294, "The history of Ferdinand’s patronage", " And indeed he would be remembered"),
        "two_artists": cut(l294, "And indeed he would be remembered", "striking work.", include_end=True),
        "contact_unclear": cut(l295, "It is not clear how Ferdinand", " However that may be"),
        "not_in_venice": cut(l295, "for the artist was not in Venice", " However that may be"),
        "commission": cut(l295 + "\n" + l296, "However that may be, in 1704 Ferdinand commissioned", " to replace Andrea del Sarto"),
        "replacement": "to replace Andrea del Sarto’s Madonna delle Arpie",
        "madonna_purchase": cut(l296, "which he had bought from the nuns of S. Francesco de’ Macci", "gallery.", include_end=True),
        "ricci_visit": cut(l296, "Ricci seems to have paid a short visit", " and thereafter"),
        "ricci_assists": cut(l296, "and thereafter to have assisted Cassana", " Within a year or two"),
        "cassana_duty": cut(l296, "keeping the Prince informed", "market.", include_end=True),
        "marucelli_employment": cut(l297, "were employing him", " In May 1706"),
        "francesco_death": cut(l296 + "\n" + l297, "Francesco, the most distinguished", " were employing him"),
        "shipment": cut(l297 + "\n" + l298, "In May 1706 he enclosed some paintings", ". included"),
        "landscapes_in_shipment": cut(l297 + "\n" + l298, ". included a couple of small landscapes", "4"),
        "marco_painter": cut(l297 + "\n" + l298, ". included a couple of small landscapes", "4"),
        "poggio_visit": cut(l298, "At the same time he made his first allusion", " Ferdinand’s reply"),
        "ferdinand_postpones": cut(l298 + "\n" + l299, "Ferdinand’s reply a week later", "However, shortly afterwards"),
        "allegory_arrival": cut(l299 + "\n" + l300, "However, shortly afterwards the situation improved", " This work has unfortunately"),
        "allegory_destroyed": cut(l299 + "\n" + l300, "This work has unfortunately been destroyed,", " but dazzling"),
        "marucelli_decorations": cut(l300, "but dazzling testimonials to Ricci’s Florentine activities survive", " and for the Grand Prince"),
        "pitti_decoration": cut(l300, "and for the Grand Prince himself in a small room in the Pitti.", None),
    }
    for name, quote in quotes.items():
        if not quote or quote not in segment_text:
            raise SystemExit(f"quote is not an exact p.235 source span ({name}): {quote!r}")

    statements = read_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statements}
    target_rows = [row for row in statements if row.get("segment_id") == SEGMENT]
    if len(target_rows) != len(EXPECTED_STATEMENTS) or {row["statement_id"] for row in target_rows} != EXPECTED_STATEMENTS:
        raise SystemExit(f"unexpected p.235 statement set: {len(target_rows)} rows")
    _, coverage = read_csv(COVERAGE)
    coverage_row = next((row for row in coverage if row["segment_id"] == SEGMENT), None)
    if not coverage_row or (coverage_row["disposition"], coverage_row["migration_status"]) != ("reviewed", "complete"):
        raise SystemExit(f"unexpected p.235 coverage state: {coverage_row}")

    candidate_fields, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_ids = {row["candidate_id"] for row in candidates}
    def review(statement_id, *, subject, object_, predicate, lines, claim, quote, note, mentioned,
               relation, ocr_corrections=None):
        set_review(by_id[statement_id], subject=subject, object_=object_, predicate=predicate,
                   lines=lines, claim=claim, quote=quote, note=note, mentioned=mentioned,
                   relation=relation, ocr_corrections=ocr_corrections)

    shared_correction_basis = "CHP-8.pdf physical page 41"
    prince_dash = [
        {"source_line": 297, "ocr": "Grand Princewhich", "print": "Grand Prince—which", "basis": shared_correction_basis},
        {"source_line": 298, "ocr": ". included", "print": "included", "basis": shared_correction_basis},
    ]
    note6_uncertainty = "Footnote 6 is attached to the destruction claim. Farsetti describes a ceiling in the Venetian-pictures room at Poggio; the source does not establish that it is this Allegory of the Arts."

    review("st-chp8-p235-giordano-pictures-and-visit", subject="cand-1172", object_="cand-7956",
        predicate="painted_glass_pictures_of_flight_into_egypt_for_ferdinand", lines=(292, 292),
        claim="Haskell says Luca Giordano painted pictures on glass depicting The Flight into Egypt for Ferdinand.",
        quote=quotes["giordano_glass"], note="The passage gives no number, present location, or date for the glass pictures.",
        mentioned=["cand-1172", "cand-7956", "cand-1609"], relation=True,
        ocr_corrections=[{"source_line": 292, "ocr": "painted, for Ferdinand", "print": "painted for Ferdinand", "basis": shared_correction_basis}])
    review("st-chp8-p235-haskell-patronage-assessment", subject="cand-1609", object_=None,
        predicate="haskell_evaluated_ferdinand_as_more_interesting_than_most_painters", lines=(294, 294),
        claim="Haskell judges Ferdinand more interesting than the painters who worked for him, while leaving the antecedent of ‘this one exception’ unstated.",
        quote=quotes["assessment"], note="This is Haskell’s evaluation. The exception is not identified here, so it is not assigned to a named painter.",
        mentioned=["cand-1609"], relation=False)
    review("st-chp8-p235-marucelli-patronage", subject="cand-7959", object_="cand-2179",
        predicate="employed_ricci_to_decorate_rooms_in_their_palace", lines=(296, 297),
        claim="Within a year or two of the preceding events, the Marucelli brothers employed Ricci to decorate several rooms in their palace.",
        quote=quotes["marucelli_employment"], note="Haskell does not identify which brother or brothers arranged the employment, or give an exact year.",
        mentioned=["cand-7959", "cand-2179", "cand-3397", "cand-1609"], relation=True,
        ocr_corrections=[{"source_line": 296, "ocr": "Marucelli.of whom", "print": "Marucelli, of whom", "basis": shared_correction_basis}])
    review("st-chp8-p235-poggio-visit-postponed", subject="cand-2179", object_="cand-7963",
        predicate="alluded_to_a_proposed_visit_to_paint_a_room_at_poggio_a_caiano", lines=(298, 298),
        claim="Ricci alluded to a forthcoming visit to Florence to paint a room in Ferdinand’s gallery of Venetian pictures at Poggio a Caiano.",
        quote=quotes["poggio_visit"], note="This is a proposed visit and painting, not a completed project; it is distinct from the later favourite gallery and Farsetti’s ceiling description.",
        mentioned=["cand-2179", "cand-3397", "cand-1609", "cand-7963", "cand-1966"], relation=True)
    review("st-chp8-p235-ricci-commission", subject="cand-1609", object_="cand-7957",
        predicate="commissioned_crucifixion_from_ricci_in_1704", lines=(295, 296),
        claim="In 1704 Ferdinand commissioned from Ricci a Crucifixion with the Madonna, St John, and St Charles Borromeo.",
        quote=quotes["commission"], note="This records the commission. The work’s replacement relation to Andrea del Sarto’s Madonna and Ferdinand’s acquisition of that painting are separately recorded below.",
        mentioned=["cand-1609", "cand-2179", "cand-7957"], relation=True)
    review("st-chp8-p235-ricci-contact-context", subject="cand-1609", object_=None,
        predicate="haskell_said_first_contact_with_ricci_was_unclear", lines=(295, 295),
        claim="Haskell says it is unclear how Ferdinand first got into touch with Sebastiano Ricci.",
        quote=quotes["contact_unclear"], note="The source explicitly marks the contact history as unclear; this does not establish a specific contact event.",
        mentioned=["cand-1609", "cand-2179"], relation=False)
    review("st-chp8-p235-ricci-visit-and-cassana-advice", subject="cand-2179", object_="cand-3397",
        predicate="seems_to_have_made_short_florence_visit_to_paint_commission_on_site", lines=(296, 296),
        claim="Haskell says Ricci seems to have made a short visit to Florence to paint the commissioned picture on site.",
        quote=quotes["ricci_visit"], note="The visit and purpose remain inferential in Haskell’s wording (‘seems to have’).",
        mentioned=["cand-2179", "cand-7957", "cand-3397"], relation=True)
    review("st-chp8-p235-surviving-decorations", subject="cand-2179", object_="cand-7966",
        predicate="painted_surviving_decorations_for_the_marucelli", lines=(300, 300),
        claim="Haskell says Ricci painted surviving great decorations for Ferdinand’s friends the Marucelli.",
        quote=quotes["marucelli_decorations"], note="The decoration subjects, dates, and precise locations are not specified; they are distinct from the destroyed Allegory of the Arts.",
        mentioned=["cand-2179", "cand-7966", "cand-7959", "cand-1609"], relation=True)
    review("st-chp8-p235-allegory-destroyed", subject="cand-7965", object_=None,
        predicate="haskell_reported_the_allegory_of_the_arts_destroyed", lines=(299, 300),
        claim="Haskell says the Allegory of the Arts had unfortunately been destroyed.",
        quote=quotes["allegory_destroyed"], note=note6_uncertainty,
        mentioned=["cand-7965", "cand-2179", "cand-1609"], relation=False)

    additions = [
        new_statement("st-chp8-p235-giordano-livorno-visit", "cand-1172", "cand-7969",
            "visited_ferdinand_at_livorno_in_may_1702", (292, 293),
            "Haskell says Giordano called on the Grand Prince at Livorno in May 1702 while returning from Spain.",
            quotes["giordano_visit"], note="The main text says Giordano was returning from Spain; note 1 quotes a letter saying Naples. These may describe successive stages, so the itinerary is not collapsed into one route.",
            mentioned=["cand-1172", "cand-1609", "cand-7969"], relation=True),
        new_statement("st-chp8-p235-giordano-worked-for-ferdinand", "cand-1172", "cand-1609",
            "worked_for_ferdinand_for_a_time", (293, 293),
            "Haskell says Giordano worked for Ferdinand for a time before setting out for home.",
            quotes["giordano_worked"], note="The duration and destination described as ‘home’ are not specified.",
            mentioned=["cand-1172", "cand-1609"], relation=True),
        new_statement("st-chp8-p235-two-unnamed-artists-met_ferdinands_demands", "cand-7958", "cand-1609",
            "painted_some_of_their_most_striking_work_for_ferdinand", (294, 294),
            "Haskell says that near the end of Ferdinand’s life two unidentified artists met his demands and painted some of their most striking work for him.",
            quotes["two_artists"], note="Neither artist is named here. The statement does not resolve whether either is the ‘one exception’ in the preceding sentence.",
            mentioned=["cand-7958", "cand-1609"], relation=True),
        new_statement("st-chp8-p235-ricci-absent-from-venice", "cand-2179", "cand-3401",
            "was_not_in_venice_during_ferdinands_two_visits", (295, 295),
            "Haskell says Ricci was not in Venice during either of Ferdinand’s two visits there.",
            quotes["not_in_venice"], note="The two visits are not dated in this passage; this is a source-reported negative location claim, not a positive relation.",
            mentioned=["cand-2179", "cand-3401", "cand-7970"], relation=False),
        new_statement("st-chp8-p235-crucifixion-replaces-madonna", "cand-7957", "cand-7862",
            "was_commissioned_to_replace_madonna_delle_arpie", (296, 296),
            "Haskell says the commissioned Crucifixion was to replace Andrea del Sarto’s Madonna delle Arpie.",
            quotes["replacement"], note="The replacement purpose is stated in the source; no completed installation or removal date is given.",
            mentioned=["cand-7957", "cand-7862"], relation=True),
        new_statement("st-chp8-p235-madonna-acquisition", "cand-1609", "cand-7862",
            "bought_madonna_delle_arpie_from_nuns_for_his_own_gallery", (296, 296),
            "Haskell says Ferdinand had bought Andrea del Sarto’s Madonna delle Arpie from the nuns of S. Francesco de’ Macci for his own gallery.",
            quotes["madonna_purchase"], note="The seller group and Ferdinand’s gallery are identified in the source, but the convent/gallery’s institutional or physical location is not resolved.",
            mentioned=["cand-1609", "cand-7862", "cand-7960", "cand-7961", "cand-2362"], relation=True),
        new_statement("st-chp8-p235-ricci-assists-cassana", "cand-2179", "cand-0593",
            "seems_to_have_assisted_cassana_with_his_market_information_duties", (296, 296),
            "Haskell says Ricci thereafter seems to have assisted Cassana with Cassana’s duties concerning pictures available on the Venetian market.",
            quotes["ricci_assists"], note="The assistance is inferential (‘seems to have’); no specific transaction or painting is identified.",
            mentioned=["cand-2179", "cand-0593", "cand-1609", "cand-3401", "cand-7968"], relation=True),
        new_statement("st-chp8-p235-cassana-market-duty", "cand-0593", "cand-1609",
            "had_duty_to_keep_ferdinand_informed_about_available_venetian_market_pictures", (296, 296),
            "Haskell describes Cassana’s duty of keeping Ferdinand informed about pictures available on the Venetian market.",
            quotes["cassana_duty"], note="The statement records the duty as Haskell describes it; this clause does not enumerate particular pictures or prove that every item was sent.",
            mentioned=["cand-0593", "cand-1609", "cand-3401", "cand-7968"], relation=True),
        new_statement("st-chp8-p235-francesco-marucelli-death", "cand-1554", "cand-4490",
            "died_in_rome_in_1703", (296, 297),
            "Haskell says Francesco Marucelli, described as the most distinguished of the brothers, had died in Rome in 1703.",
            quotes["francesco_death"], note="This is Haskell’s report. No independent biographical source is asserted here.",
            mentioned=["cand-1554", "cand-4490", "cand-7959"], relation=True,
            ocr_corrections=[{"source_line": 296, "ocr": "Marucelli.of whom", "print": "Marucelli, of whom", "basis": shared_correction_basis}]),
        new_statement("st-chp8-p235-shipment-includes-landscapes", "cand-7983", "cand-7962",
            "included_two_small_landscapes_by_marco_ricci", (297, 298),
            "Haskell says the two crates included a couple of small landscapes by Marco Ricci.",
            quotes["landscapes_in_shipment"], note="The OCR breaks the printed relative clause across lines; the source image reads ‘Prince—which included’. The landscapes are treated as a work group, without individual titles or locations.",
            mentioned=["cand-7983", "cand-7962", "cand-2149"], relation=True,
            ocr_corrections=prince_dash),
        new_statement("st-chp8-p235-marco-painted-landscapes", "cand-2149", "cand-7962",
            "painted_the_two_small_landscapes_in_the_shipment", (297, 298),
            "Haskell attributes the two small landscapes in the shipment to Ricci’s nephew Marco.",
            quotes["marco_painter"], note="The attribution and kinship are Haskell’s report; no independent verification is claimed.",
            mentioned=["cand-2149", "cand-2179", "cand-7962", "cand-7983"], relation=True,
            ocr_corrections=prince_dash),
        new_statement("st-chp8-p235-ferdinand-postpones-poggio-scheme", "cand-1609", "cand-7963",
            "postponed_the_proposed_poggio_room_scheme_due_to_ill_health", (298, 298),
            "Haskell says Ferdinand replied a week later that ill health was causing him to postpone the proposed scheme.",
            quotes["ferdinand_postpones"], note="This is Ferdinand’s reported response to a proposed room project; the passage does not say that Ricci completed the visit or painting.",
            mentioned=["cand-1609", "cand-7963", "cand-1966"], relation=True),
        new_statement("st-chp8-p235-allegory-arrival", "cand-2179", "cand-7965",
            "arrived_to_paint_the_allegory_of_the_arts_for_ferdinand", (299, 300),
            "Shortly afterward, Ricci arrived to paint an Allegory of the Arts for Ferdinand in his favourite gallery in his favourite villa.",
            quotes["allegory_arrival"], note="The gallery and villa are unnamed here. Their identification with Poggio a Caiano remains unresolved.",
            mentioned=["cand-2179", "cand-7965", "cand-1609", "cand-7964", "cand-7987"], relation=True),
        new_statement("st-chp8-p235-pitti-decoration", "cand-2179", "cand-7967",
            "painted_surviving_decoration_for_ferdinand_in_a_small_pitti_room", (300, 300),
            "Haskell says Ricci painted surviving decoration for Ferdinand in a small room in the Pitti.",
            quotes["pitti_decoration"], note="The subject and date of the decoration are not specified; it is not identified with the destroyed Allegory of the Arts.",
            mentioned=["cand-2179", "cand-7967", "cand-1609", "cand-7662"], relation=True),
    ]

    # Keep the exact source quote for the shipment; store the print correction as S2 metadata.
    review("st-chp8-p235-crates-and-landscapes", subject="cand-2179", object_="cand-7983",
        predicate="sent_two_crates_of_paintings_for_the_marucelli_to_ferdinand_in_may_1706", lines=(297, 297),
        claim="In May 1706 Ricci enclosed paintings for the Marucelli in two crates sent to Ferdinand.",
        quote=quotes["shipment"], note="The paintings are described as being for the Marucelli, while the crates were sent to Ferdinand. The shipment contents are separately stated; the number and subjects of the other paintings are unknown.",
        mentioned=["cand-2179", "cand-7983", "cand-7959", "cand-1609"], relation=True,
        ocr_corrections=prince_dash[:1])

    additions_by_id = {row["statement_id"]: row for row in additions}
    for statement_id in ("st-chp8-p235-giordano-livorno-visit", "st-chp8-p235-giordano-worked-for-ferdinand",
                         "st-chp8-p235-two-unnamed-artists-met_ferdinands_demands",
                         "st-chp8-p235-ricci-absent-from-venice", "st-chp8-p235-crucifixion-replaces-madonna",
                         "st-chp8-p235-madonna-acquisition", "st-chp8-p235-ricci-assists-cassana",
                         "st-chp8-p235-cassana-market-duty", "st-chp8-p235-francesco-marucelli-death",
                         "st-chp8-p235-shipment-includes-landscapes", "st-chp8-p235-marco-painted-landscapes",
                         "st-chp8-p235-ferdinand-postpones-poggio-scheme", "st-chp8-p235-allegory-arrival",
                         "st-chp8-p235-pitti-decoration"):
        if statement_id in by_id or statement_id not in additions_by_id:
            raise SystemExit(f"unexpected or duplicate p.235 statement ID: {statement_id}")
    if len(additions) != 14 or len(additions_by_id) != len(additions):
        raise SystemExit(f"unexpected p.235 atomic statement count: {len(additions)}")

    # The footnote markers on the printed page govern these links; replace stale composite links.
    all_rows = statements + additions
    by_id = {row["statement_id"]: row for row in all_rows}
    for note_id, body_ids in NOTE_LINKS.items():
        note = by_id.get(note_id)
        if note is None:
            raise SystemExit(f"missing p.235 note statement: {note_id}")
        note.setdefault("qualifiers", {})["linked_body_statement_ids"] = body_ids
    for note_id, body_ids in NOTE_LINKS.items():
        for body_id in body_ids:
            body = by_id[body_id]
            links = body.setdefault("qualifiers", {}).setdefault("linked_note_statement_ids", [])
            if note_id not in links:
                links.append(note_id)
    by_id["st-chp8-p235-note6-farsetti-quote-tail"].setdefault("qualifiers", {})[
        "linked_body_statement_ids"
    ] = ["st-chp8-p235-allegory-destroyed"]

    final_target = [row for row in all_rows if row.get("segment_id") == SEGMENT]
    all_candidate_ids = candidate_ids
    counts = {"true": 0, "false": 0, "unset": 0}
    for row in final_target:
        q = row.get("qualifiers", {})
        value = q.get("relation_candidate")
        if value not in (True, False):
            raise SystemExit(f"p.235 statement remains unclassified: {row['statement_id']}")
        counts["true" if value else "false"] += 1
        refs = set(q.get("mentioned_candidate_ids", []))
        refs.update(x for x in (row.get("subject_candidate_id"), row.get("object_candidate_id")) if x)
        if missing := refs - all_candidate_ids:
            raise SystemExit(f"unknown candidate refs in {row['statement_id']}: {sorted(missing)}")

    coverage_row["note"] += (
        " Semantic review 2026-10-14 rechecked the p.235 body and note 6 continuation against CHP-8.pdf physical page 41. "
        "Separated Giordano’s glass paintings, Livorno visit, and period working for Ferdinand; Haskell’s evaluation from "
        "the two unnamed artists’ work; Ricci’s unclear contact history from his absence in Venice; the 1704 commission, "
        "replacement purpose, and Madonna acquisition; Ricci’s Florence visit and assistance to Cassana; the Cassana duty; "
        "Marucelli employment and Francesco’s death; the two-crate shipment, landscape group, and Marco attribution; "
        "the proposed Poggio visit and Ferdinand’s postponement; the Allegory’s arrival and destruction; and the separate "
        "surviving Marucelli and Pitti decorations. Corrected OCR only in S2 qualifiers and linked notes 1–6 to their claims. "
        "No candidate, mention, KU, or formal S6 relation was added."
    )
    preview = {
        "mode": "dry-run", "segment": SEGMENT, "pdf_physical_page": 41,
        "existing_statements_reviewed": len(target_rows), "new_statements": sorted(additions_by_id),
        "final_statement_count": len(final_target), "final_relation_candidate_counts": counts,
        "quote_spans_verified": len(quotes), "note_links": NOTE_LINKS,
        "new_candidates": 0, "new_mentions": 0, "formal_relations_created": 0,
    }
    payload = {
        STATEMENTS: jsonl_bytes(all_rows),
        COVERAGE: csv_bytes(read_csv(COVERAGE)[0], coverage),
    }
    return preview, payload


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="apply the preflighted p.235 S2 review")
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
