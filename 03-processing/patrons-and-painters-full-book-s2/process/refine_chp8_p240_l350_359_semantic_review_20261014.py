"""Atomize p.240 statements and correct a person/work endpoint mismatch."""
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
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
MENTIONS = ROOT / "04-knowledge" / "tables" / "mentions.csv"
SEGMENTS = ROOT / "04-knowledge" / "tables" / "segments.jsonl"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE = ROOT / SOURCE_REL
SEGMENT = "chp-8:08_CHP-8_sec_ii:l350-359"
PREVIOUS_SEGMENT = "chp-8:08_CHP-8_sec_ii:l338-348"
NEXT_SEGMENT = "chp-8:08_CHP-8_sec_ii:l361-370"
BACKUP_SUFFIX = ".bak-s2-chp8-p240-l350-359-semantic-review-20261014"
EXPECTED_TABLE_SHA256 = "D90F00FDAD3AC4041DBB5345E786F9AE59A254A213AA4DB06AFC5800E5FC2E33"
EXPECTED_MENTIONS_SHA256 = "0B1D645F972BC7DEF5B2E8800865D57768227D13C7460E3C93757905E7EAC94B"
EXPECTED_EXISTING = {
    "st-chp8-p240-1706-exhibition-and-san-rocco",
    "st-chp8-p240-catalogue-and-reconstruction",
    "st-chp8-p240-collections-at-pratolino-and-castello",
    "st-chp8-p240-corpus-domini-exhibitions",
    "st-chp8-p240-exhibition-as-art-direction",
    "st-chp8-p240-exhibition-date-and-venue",
    "st-chp8-p240-ferdinand-displays-gabbiani",
    "st-chp8-p240-ferdinand-displays-sacconi-and-cassana",
    "st-chp8-p240-ferdinand-mehus-canvases-and-son",
    "st-chp8-p240-mehus-appeal",
    "st-chp8-p240-mehus-collection",
    "st-chp8-p240-mehus-death-and-patronage",
    "st-chp8-p240-room-and-ricci",
}
NEW_IDS = {
    "st-chp8-p240-venetian-pictures-ten-titian-attributions",
    "st-chp8-p240-other-flemish-works-in-collection",
    "st-chp8-p240-contemporary-roman-painting-scarce",
    "st-chp8-p240-florentine-school-one-artist-in-bulk",
    "st-chp8-p240-mehus-most-venetian-in-entourage",
    "st-chp8-p240-ferdinand-collected-mehus-canvases",
    "st-chp8-p240-special-room-at-poggio-a-caiano",
    "st-chp8-p240-collections-at-villa-di-castello",
    "st-chp8-p240-ferdinand-displayed-policy-to-sacconi",
    "st-chp8-p240-ferdinand-admired-cassana-portrait-cook",
}
RICCI_PERSON_MENTION_IDS = {
    "m-chp8-p235-ricci-full",
    "m-chp8-p235-artist-ricci",
    "m-chp8-p235-him-commission",
    "m-chp8-p235-ricci-visit",
    "m-chp8-p235-ricci-found-patrons",
    "m-chp8-p235-ricci-employed-him",
    "m-chp8-p235-ricci-sent-paintings",
    "m-chp8-p235-ricci-nephew",
    "m-chp8-p235-ricci-proposed-visit",
    "m-chp8-p235-ricci-arrival",
    "m-chp8-p235-ricci-painted",
    "m-chp8-p235-ricci-activities",
    "m-chp8-p235-ricci-note3",
    "m-chp8-p235-sebastiano-ricci-note4",
    "m-chp8-p236-gherardi-ricci",
    "m-chp8-p236-ricci-letter106",
    "m-chp8-p236-ricci-figures",
    "m-chp8-p240-241-ricci-first-name",
    "m-chp8-p240-241-ricci-surname",
    "m-chp8-p240-241-ricci-acquired-mehus",
}
RICCI_PERSON_SUBJECT_IDS = {
    "st-chp8-p235-crates-and-landscapes",
    "st-chp8-p235-note3-ricci-letters",
    "st-chp8-p235-poggio-visit-postponed",
    "st-chp8-p235-ricci-visit-and-cassana-advice",
    "st-chp8-p235-surviving-decorations",
    "st-chp8-p236-note1-gherardi-report",
    "st-chp8-p240-note1-fogolari-mehus-acquisition",
    "st-chp8-p240-room-and-ricci",
    "st-chp8-p235-ricci-absent-from-venice",
    "st-chp8-p235-ricci-assists-cassana",
    "st-chp8-p235-allegory-arrival",
    "st-chp8-p235-pitti-decoration",
}
RICCI_PERSON_OBJECT_IDS = {"st-chp8-p235-marucelli-patronage"}
RICCI_PERSON_MENTION_ONLY_IDS = {
    "st-chp8-p235-allegory-destroyed",
    "st-chp8-p235-note4-letter197-and-exhibition",
    "st-chp8-p235-ricci-commission",
    "st-chp8-p235-ricci-contact-context",
    "st-chp8-p236-note3-letter106-attribution-uncertain",
    "st-chp8-p236-note3-saluzzi-painting-at-lucca",
    "st-chp8-p235-marco-painted-landscapes",
}
RICCI_WORK_STATEMENT_ID = "st-chp19-p390-crespi-praises-ricci"
RICCI_WORK_MENTION_ID = "m-chp19-p390-039"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def jsonl_bytes(rows):
    return ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")


def atomic_write(path: Path, data: bytes):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(data)
    temporary.replace(path)


def normalized(text: str) -> str:
    return " ".join(text.split())


def cut(text: str, start: str, end: str | None = None, *, include_end=False) -> str:
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


def set_statement(row, *, subject, object_, predicate, claim, quote, lines,
                  qualification, mentioned, relation, relation_note,
                  text_layer="body", extras=None):
    row["subject_candidate_id"] = subject
    row["object_candidate_id"] = object_
    row["predicate"] = predicate
    row["original_quote"] = quote
    q = row.setdefault("qualifiers", {})
    q.update({
        "source_line_start": lines[0], "source_line_end": lines[1],
        "printed_page": 240, "pdf_physical_page": 46,
        "claim": claim, "speaker": "Haskell", "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation,
        "relation_candidate_note": relation_note,
    })
    if extras:
        q.update(extras)


def new_statement(statement_id, *, subject, object_, predicate, claim, quote,
                  lines, qualification, mentioned, relation, relation_note,
                  extras=None):
    row = {
        "statement_id": statement_id, "segment_id": SEGMENT,
        "subject_candidate_id": subject, "object_candidate_id": object_,
        "predicate": predicate, "qualifiers": {}, "original_quote": quote,
        "origin": "book", "source_file": SOURCE_REL,
    }
    set_statement(row, subject=subject, object_=object_, predicate=predicate,
        claim=claim, quote=quote, lines=lines, qualification=qualification,
        mentioned=mentioned, relation=relation, relation_note=relation_note,
        extras=extras)
    return row


def revise_mentions(data: bytes) -> tuple[bytes, int]:
    bom = data.startswith(b"\xef\xbb\xbf")
    text = data.decode("utf-8-sig")
    lines = text.splitlines(keepends=True)
    changed = 0
    found = set()
    for i, line in enumerate(lines):
        raw = line.rstrip("\r\n")
        parsed = next(csv.reader([raw]))
        if parsed and parsed[0] in RICCI_PERSON_MENTION_IDS:
            mention_id = parsed[0]
            if mention_id in found or parsed[2] != "cand-2179":
                raise SystemExit(f"unexpected Ricci mention mapping for {mention_id}")
            updated = raw.replace(",cand-2179,", ",cand-2154,", 1)
            if mention_id == "m-chp8-p235-ricci-full":
                updated = updated.replace(
                    "Indexed artist candidate; multiple index entries are resolved later in S3.",
                    "Sebastiano Ricci as painter; person candidate cand-2154, distinct from work candidate cand-2179.")
            elif mention_id == "m-chp8-p240-241-ricci-first-name":
                updated = updated.replace(
                    "index entry concerns work for Ferdinand.",
                    "Sebastiano Ricci as painter; distinct from work candidate cand-2179.")
            elif mention_id == "m-chp8-p240-241-ricci-surname":
                updated = updated.replace(
                    "Continuation of the name Sebastiano Ricci on the following OCR line.",
                    "Continuation of the painter name Sebastiano Ricci; maps to person cand-2154, distinct from work candidate cand-2179.")
            elif mention_id == "m-chp8-p240-241-ricci-acquired-mehus":
                updated = updated.replace(
                    "Sebastiano Ricci in the cited acquisition reference.",
                    "Sebastiano Ricci as the person acquiring Mehus works; use person cand-2154, not work candidate cand-2179.")
            if updated == raw:
                raise SystemExit(f"Ricci mention note not found for {mention_id}")
            fields = next(csv.reader([updated]))
            if fields[2] != "cand-2154":
                raise SystemExit(f"Ricci mention endpoint not corrected for {mention_id}")
            ending = line[len(raw):]
            lines[i] = updated + ending
            found.add(mention_id)
            changed += 1
    if found != RICCI_PERSON_MENTION_IDS:
        raise SystemExit(f"unexpected Ricci person mention set: {sorted(found)}")
    output = "".join(lines).encode("utf-8")
    if bom:
        output = b"\xef\xbb\xbf" + output
    return output, changed


def plan():
    table_bytes = TABLE.read_bytes()
    if sha(table_bytes).lower() != EXPECTED_TABLE_SHA256.lower():
        raise SystemExit("statement table changed since p.239 review; refusing write")
    mentions_bytes = MENTIONS.read_bytes()
    if sha(mentions_bytes).lower() != EXPECTED_MENTIONS_SHA256.lower():
        raise SystemExit("mentions table changed since p.239 review; refusing write")
    meta = next((r for r in read_jsonl(SEGMENTS) if r.get("segment_id") == SEGMENT), None)
    if not meta or (meta.get("line_start"), meta.get("line_end")) != (350, 359):
        raise SystemExit("unexpected p.240 segment metadata")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[349:359])
    if sha(segment_text.encode("utf-8")) != meta.get("sha256"):
        raise SystemExit("p.240 source segment hash mismatch")
    l351, l352, l353, l354, l355, l356, l357, l358, l359 = (
        source_lines[n - 1] for n in range(351, 360)
    )
    q = {
        "titian_group": cut(l351, "including about ten attributed to Titian", ". There were also"),
        "flemish_works": cut(l351, "There were also Flemish works", ", but only"),
        "roman_scarce": cut(l351, "but only the barest representation of contemporary Roman painting", ". Of the Florentine"),
        "florentine_bulk": cut(l351, "Of the Florentine school of the day only one artist was present in bulk", "; the Flemish Livio Mehus"),
        "mehus_30": cut(l351, "thirty of whose works Ferdinand owned", ". Such prominence"),
        "mehus_venetian": cut(l351, "Such prominence is not surprising, for Mehus was by far the most Venetian of all the artists in his entourage", " and his tremendous"),
        "mehus_appeal": cut(l351, "and his tremendous vivacity combined with a slightly troubled eroticism made an obvious appeal to Ferdinand", ". Only the death"),
        "mehus_death": cut(l351, "Only the death of this painter in 1691, before Ferdinand’s patronage had reached its fullest extent, can have prevented him working directly for the Grand Prince", " who sought to make amends"),
        "mehus_canvases": cut(l351, "who sought to make amends for this neglect by assiduously collecting his canvases", " and giving support to his son"),
        "mehus_son": cut(l351, "and giving support to his son", ".1"),
        "special_room": cut(l352, "In Poggio a Caiano Ferdinand had a special room in which he kept small examples of each of his favourite artists, ancient and contemporary", ", and it was this"),
        "ricci_room_work": "\n".join([
            cut(l352, ", and it was this that Sebastiano"),
            cut(l353, "Ricci painted for him in 1707", ". He kept"),
        ]),
        "pratolino_collections": cut(l353, "He kept further large collections at Pratolino", " and the"),
        "castello_collections": "\n".join([
            cut(l353, "and the"),
            cut(l354, "Villa di Castello", None),
        ]),
        "art_direction": cut(l355, "He was also anxious to guide the whole direction taken by painters in the Florence of his day.", " Pictures had been exhibited"),
        "corpus": cut(l355, "Pictures had been exhibited in Florence, as in many other Italian cities, on the occasion of the Corpus Domini processions", ", and Ferdinand regularly"),
        "gabbiani_display": "\n".join([
            cut(l355, "and Ferdinand regularly showed works painted for him by those artists of whom he approved, such as"),
            cut(l356, "Gabbiani, whose Flight into Egypt he put on view to the public in the Piazza del Duomo", ".2"),
        ]),
        "sacconi_policy": cut(l357, "He adopted the same policy towards Sacconi", "3 and especially"),
        "cassana_display": cut(l357, "and especially Cassana", "? But Ferdinand probably"),
        "cassana_admiration": cut(l357, "full of admiration for the ‘gran gusto’ of his Portrait of a Cook", " which he intended"),
        "exhibition_grander": cut(l357, "But Ferdinand probably found such exhibitions too casual to produce the effect he hoped for", None),
        "catalogue": cut(l358, "A printed catalogue was issued—and this in itself was an innovation for Italy.5 From this catalogue we can reconstruct the event."),
        "event_date_venue": "\n".join([
            cut(l358, "The exhibition was held on St Luke’s day (18"),
            cut(l359, "October) in the chapel dedicated to that saint in the cloisters of the Annunziata.", " About"),
        ]),
    }
    ranges = {
        "titian_group": (351, 351), "flemish_works": (351, 351), "roman_scarce": (351, 351),
        "florentine_bulk": (351, 351), "mehus_30": (351, 351), "mehus_venetian": (351, 351),
        "mehus_appeal": (351, 351), "mehus_death": (351, 351), "mehus_canvases": (351, 351),
        "mehus_son": (351, 351), "special_room": (352, 352), "ricci_room_work": (352, 353),
        "pratolino_collections": (353, 353), "castello_collections": (353, 354),
        "art_direction": (355, 355), "corpus": (355, 355), "gabbiani_display": (355, 356),
        "sacconi_policy": (357, 357), "cassana_display": (357, 357),
        "cassana_admiration": (357, 357), "exhibition_grander": (357, 357),
        "catalogue": (358, 358), "event_date_venue": (358, 359),
    }
    for name, quote in q.items():
        start, end = ranges[name]
        cited = "\n".join(source_lines[start - 1:end])
        if normalized(quote) not in normalized(cited):
            raise SystemExit(f"quote is not an exact source span ({name})")

    rows = read_jsonl(TABLE)
    by_id = {row["statement_id"]: row for row in rows}
    existing = {row["statement_id"] for row in rows if row.get("segment_id") == SEGMENT}
    if existing != EXPECTED_EXISTING:
        raise SystemExit(f"unexpected p.240 statement set: {len(existing)} rows")
    if set(by_id) & NEW_IDS:
        raise SystemExit("one or more planned p.240 statement IDs already exist")
    person_statement_ids = RICCI_PERSON_SUBJECT_IDS | RICCI_PERSON_OBJECT_IDS | RICCI_PERSON_MENTION_ONLY_IDS
    actual_cand2179_statement_ids = {
        row["statement_id"] for row in rows
        if row.get("subject_candidate_id") == "cand-2179"
        or row.get("object_candidate_id") == "cand-2179"
        or "cand-2179" in row.get("qualifiers", {}).get("mentioned_candidate_ids", [])
    }
    if actual_cand2179_statement_ids != person_statement_ids | {RICCI_WORK_STATEMENT_ID}:
        raise SystemExit(f"unexpected cand-2179 statement references: {sorted(actual_cand2179_statement_ids)}")
    for sid in RICCI_PERSON_SUBJECT_IDS:
        if by_id[sid].get("subject_candidate_id") != "cand-2179":
            raise SystemExit(f"unexpected Ricci person subject mapping in {sid}")
        by_id[sid]["subject_candidate_id"] = "cand-2154"
    for sid in RICCI_PERSON_OBJECT_IDS:
        if by_id[sid].get("object_candidate_id") != "cand-2179":
            raise SystemExit(f"unexpected Ricci person object mapping in {sid}")
        by_id[sid]["object_candidate_id"] = "cand-2154"
    for sid in person_statement_ids:
        mentioned = by_id[sid].get("qualifiers", {}).get("mentioned_candidate_ids", [])
        if "cand-2179" in mentioned:
            by_id[sid]["qualifiers"]["mentioned_candidate_ids"] = [
                "cand-2154" if cid == "cand-2179" else cid for cid in mentioned
            ]
    if by_id[RICCI_WORK_STATEMENT_ID].get("object_candidate_id") != "cand-2179":
        raise SystemExit("Ricci work-group statement mapping changed unexpectedly")
    next_rows = read_jsonl(SEGMENTS)
    if not any(r.get("segment_id") == PREVIOUS_SEGMENT for r in next_rows):
        raise SystemExit("p.239 continuation segment is missing")
    if not any(r.get("segment_id") == NEXT_SEGMENT for r in next_rows):
        raise SystemExit("p.241 next body segment is missing")

    def revise(statement_id, *, subject, object_, predicate, claim, quote, lines,
               qualification, mentioned, relation, relation_note, extras=None):
        qualifiers = by_id[statement_id].setdefault("qualifiers", {})
        for key in ("ocr_corrections", "continuation_from_segment_id", "continuation_to_segment_id",
                    "continuation_closed_by_segment_id", "continuation_closed_by_line",
                    "footnote_marker", "footnote_statement_ids"):
            if not extras or key not in extras:
                qualifiers.pop(key, None)
        set_statement(by_id[statement_id], subject=subject, object_=object_, predicate=predicate,
            claim=claim, quote=quote, lines=lines, qualification=qualification,
            mentioned=mentioned, relation=relation, relation_note=relation_note,
            extras=extras)

    revise("st-chp8-p240-1706-exhibition-and-san-rocco",
        subject="cand-1609", object_="cand-7977", predicate="organized_a_larger_1706_exhibition_probably_inspired_by_san_rocco",
        claim="Haskell says Ferdinand probably found earlier displays too casual and by 1706 had organized something grander, perhaps taking the idea from S. Rocco exhibitions in Venice while running his own on more spectacular lines.",
        quote=q["exhibition_grander"], lines=(357, 357),
        qualification="Both the S. Rocco inspiration and Haskell’s explanation are qualified; no exact S. Rocco event or direct borrowing is asserted.",
        mentioned=["cand-1609", "cand-7977", "cand-0128", "cand-0138", "cand-2719"], relation=True,
        relation_note="The source describes Ferdinand’s organization of the 1706 exhibition and a probable model; retain the uncertainty.")
    revise("st-chp8-p240-catalogue-and-reconstruction",
        subject="cand-8069", object_="cand-7977", predicate="printed_catalogue_documents_1706_exhibition",
        claim="Haskell says a printed catalogue, an innovation for Italy, was issued for the exhibition and enables reconstruction of the event.",
        quote=q["catalogue"], lines=(358, 358),
        qualification="The catalogue is identified in note 5; it has not been independently consulted.",
        mentioned=["cand-8069", "cand-7977", "cand-3461"], relation=True,
        relation_note="The source explicitly uses the catalogue as documentation for the exhibition.",
        extras={"footnote_marker": 5, "footnote_statement_ids": ["st-chp8-p240-note5-catalogue-title"]})
    revise("st-chp8-p240-collections-at-pratolino-and-castello",
        subject="cand-1609", object_="cand-7838", predicate="kept_a_large_collection_at_pratolino",
        claim="Haskell says Ferdinand kept a further large collection at Pratolino.",
        quote=q["pratolino_collections"], lines=(353, 353),
        qualification="This is separate from the special room at Poggio a Caiano described immediately before.",
        mentioned=["cand-1609", "cand-7838"], relation=True,
        relation_note="The source explicitly locates one of Ferdinand’s further large collections at Pratolino.")
    revise("st-chp8-p240-corpus-domini-exhibitions",
        subject="cand-6024", object_="cand-1041", predicate="pictures_displayed_during_corpus_domini_processions_in_florence_and_italian_cities",
        claim="Haskell says pictures had been exhibited during Corpus Domini processions in Florence and many other Italian cities.",
        quote=q["corpus"], lines=(355, 355),
        qualification="This is a general practice, not a dated single exhibition or proof that Ferdinand used each procession.",
        mentioned=["cand-6024", "cand-1041", "cand-3461", "cand-0128"], relation=False,
        relation_note="The statement describes a recurring general context and supplies no specific event endpoint.")
    revise("st-chp8-p240-exhibition-as-art-direction",
        subject="cand-1609", object_="cand-0128", predicate="used_exhibitions_to_guide_florentine_painting_in_a_new_way",
        claim="Haskell says Ferdinand wanted to guide painting in Florence and used the still-rudimentary art exhibition in an entirely new way for that purpose.",
        quote=q["art_direction"], lines=(355, 355),
        qualification="The wording concerns Ferdinand’s program and use of exhibitions; it does not establish the actual effect on all Florentine painters.",
        mentioned=["cand-1609", "cand-0128", "cand-1041"], relation=True,
        relation_note="The source explicitly connects Ferdinand’s use of exhibitions with his effort to guide painting in Florence.",
        extras={"ocr_corrections": [
            {"source_line": 355, "ocr": "confmed", "print": "confined", "basis": "CHP-8.pdf physical page 46"},
            {"source_line": 355, "ocr": "instrumentof", "print": "instrument of", "basis": "CHP-8.pdf physical page 46"},
        ]})
    revise("st-chp8-p240-exhibition-date-and-venue",
        subject="cand-7977", object_="cand-8067", predicate="held_on_saint_lukes_day_in_annunziata_chapel",
        claim="Haskell dates the exhibition to St Luke’s day, 18 October, in the chapel dedicated to that saint in the Annunziata cloisters.",
        quote=q["event_date_venue"], lines=(358, 359),
        qualification="The passage identifies the day and venue; the catalogue is cited separately.",
        mentioned=["cand-7977", "cand-8066", "cand-8067", "cand-8068"], relation=True,
        relation_note="The source directly gives the exhibition date and chapel venue.")
    revise("st-chp8-p240-ferdinand-displays-gabbiani",
        subject="cand-1609", object_="cand-1095", predicate="regularly_showed_approved_artists_work_and_displayed_gabbianis_flight_into_egypt",
        claim="Haskell says Ferdinand regularly showed works painted for him by artists he approved, including Gabbiani’s Flight into Egypt, which Ferdinand displayed publicly in Piazza del Duomo.",
        quote=q["gabbiani_display"], lines=(355, 356),
        qualification="This is one named example of the stated policy; note 2 cites Hugford, p.10.",
        mentioned=["cand-1609", "cand-1093", "cand-1095", "cand-8065", "cand-0128"], relation=True,
        relation_note="The source explicitly reports Ferdinand displaying the named painting in a public place.",
        extras={"footnote_marker": 2, "footnote_statement_ids": ["st-chp8-p240-note2-hugford-locator"]})
    revise("st-chp8-p240-ferdinand-displays-sacconi-and-cassana",
        subject="cand-1609", object_="cand-7940", predicate="intended_to_exhibit_cassanas_portrait_of_a_cook_after_1707_letter",
        claim="Haskell says Ferdinand wrote to Cassana in 1707, praised the ‘gran gusto’ of his Portrait of a Cook, and intended to exhibit it so local artists could see how timidly they painted.",
        quote=q["cassana_display"], lines=(357, 357),
        qualification="The exhibition is an intention, not a report that the picture was actually displayed; the quoted first-person remark is reported through Haskell.",
        mentioned=["cand-1609", "cand-0593", "cand-7940", "cand-0128"], relation=True,
        relation_note="The source explicitly reports Ferdinand’s plan to exhibit the named painting; the plan’s execution is not established.",
        extras={"quoted_speaker": "Ferdinand, as reported by Haskell",
                "footnote_marker": 4,
                "footnote_statement_ids": ["st-chp8-p240-note4-fogolari-letter120"],
                "ocr_corrections": [{"source_line": 357, "ocr": "?", "print": "4", "basis": "CHP-8.pdf physical page 46"}]})
    revise("st-chp8-p240-ferdinand-mehus-canvases-and-son",
        subject="cand-1609", object_="cand-8059", predicate="gave_support_to_livio_mehuss_son",
        claim="Haskell says Ferdinand sought to make amends for neglecting Livio Mehus by giving support to Mehus’s son.",
        quote=q["mehus_son"], lines=(351, 351),
        qualification="Mehus’s son is unnamed; no identity or later career is inferred.",
        mentioned=["cand-1609", "cand-1632", "cand-8059"], relation=True,
        relation_note="The source directly reports Ferdinand giving support to Mehus’s son.")
    revise("st-chp8-p240-mehus-appeal",
        subject="cand-1632", object_="cand-1609", predicate="vivacity_and_troubled_eroticism_appealed_to_ferdinand",
        claim="Haskell says Mehus’s tremendous vivacity and slightly troubled eroticism made an obvious appeal to Ferdinand.",
        quote=q["mehus_appeal"], lines=(351, 351),
        qualification="This is Haskell’s characterization of Ferdinand’s aesthetic response, not a direct statement from Ferdinand.",
        mentioned=["cand-1632", "cand-1609"], relation=True,
        relation_note="The source explicitly describes Mehus’s qualities as appealing to Ferdinand; preserve Haskell’s attribution.")
    revise("st-chp8-p240-mehus-collection",
        subject="cand-8060", object_="cand-1609", predicate="owned_by_ferdinand_about_thirty_works_by_livio_mehus",
        claim="Haskell says Ferdinand owned thirty works by Livio Mehus.",
        quote=q["mehus_30"], lines=(351, 351),
        qualification="The thirty works are an aggregate with no titles or individual identities supplied.",
        mentioned=["cand-1609", "cand-1632", "cand-8060"], relation=True,
        relation_note="The source explicitly states that Ferdinand owned thirty works by Mehus.")
    revise("st-chp8-p240-mehus-death-and-patronage",
        subject="cand-1632", object_="cand-1609", predicate="death_may_have_prevented_direct_work_for_ferdinand",
        claim="Haskell argues that Mehus’s death in 1691, before Ferdinand’s patronage reached its fullest extent, may have prevented Mehus from working directly for the Grand Prince.",
        quote=q["mehus_death"], lines=(351, 351),
        qualification="This is a counterfactual explanation; it does not establish that Mehus worked directly for Ferdinand.",
        mentioned=["cand-1632", "cand-1609"], relation=False,
        relation_note="The statement is a counterfactual about a relationship that may not have occurred.")
    revise("st-chp8-p240-room-and-ricci",
        subject="cand-2154", object_="cand-8063", predicate="painted_unidentified_work_for_ferdinand_in_1707",
        claim="Haskell says Sebastiano Ricci painted ‘this’ for Ferdinand in 1707; the referent is an unidentified work associated with the special room at Poggio a Caiano.",
        quote=q["ricci_room_work"], lines=(352, 353),
        qualification="The wording ‘this’ is ambiguous; retain candidate cand-8063 without deciding whether it means the room, its decoration, or an associated work. Sebastiano Ricci is the person candidate cand-2154; cand-2179 is a work candidate.",
        mentioned=["cand-2154", "cand-1609", "cand-1966", "cand-8062", "cand-8063"], relation=True,
        relation_note="The source explicitly says Ricci painted something for Ferdinand in 1707; the work endpoint remains unresolved.")

    for sid, subject, object_, predicate, claim, key, lines, qualification, mentioned, relation, note, extras in [
        ("st-chp8-p240-venetian-pictures-ten-titian-attributions", "cand-8093", "cand-1609",
         "collection_included_about_ten_pictures_attributed_to_titian",
         "The continuation says Ferdinand’s Venetian-picture group included about ten works attributed to Titian.", "titian_group", (351, 351),
         "The count is approximate and the attribution is retained; the works are not individually identified.",
         ["cand-1609", "cand-8093", "cand-2630"], True,
         "The passage continues the preceding collection statement and places this work group among Ferdinand’s amassed pictures.",
         {"continuation_from_segment_id": PREVIOUS_SEGMENT}),
        ("st-chp8-p240-other-flemish-works-in-collection", "cand-8061", "cand-1609",
         "unspecified_flemish_works_in_ferdinands_collection",
         "Haskell says Ferdinand’s collection also included Flemish works.", "flemish_works", (351, 351),
         "The works’ makers, titles, and count are not supplied.",
         ["cand-8061", "cand-1609"], True,
         "The source directly places the unspecified Flemish works in the collection described on this page.", None),
        ("st-chp8-p240-contemporary-roman-painting-scarce", "cand-1609", "cand-8095",
         "collection_had_only_barest_representation_of_contemporary_roman_painting",
         "Haskell says contemporary Roman painting was represented only minimally in the collection.", "roman_scarce", (351, 351),
         "This is a statement about category-level representation, not about a specifically identified work group.",
         ["cand-1609", "cand-8095"], False,
         "No individual work or bounded group is identified for a formal relation.", None),
        ("st-chp8-p240-florentine-school-one-artist-in-bulk", "cand-8102", "cand-1632",
         "only_one_florentine_school_artist_present_in_bulk_in_collection",
         "Haskell says only one artist of the Florentine school was present in bulk and names the Flemish Livio Mehus.", "florentine_bulk", (351, 351),
         "The source’s juxtaposition of ‘Florentine school’ and ‘Flemish Livio Mehus’ is preserved without recategorizing Mehus.",
         ["cand-8102", "cand-1632", "cand-1609"], False,
         "A category and collection-composition claim; it does not by itself establish a formal relation.", None),
        ("st-chp8-p240-mehus-most-venetian-in-entourage", "cand-1632", None,
         "haskell_called_mehus_most_venetian_artist_in_ferdinands_entourage",
         "Haskell calls Mehus by far the most Venetian of the artists in Ferdinand’s entourage.", "mehus_venetian", (351, 351),
         "‘Most Venetian’ is Haskell’s comparative characterization, not a formal school membership claim.",
         ["cand-1632", "cand-1609"], False,
         "An art-historical characterization rather than a distinct relation.", None),
        ("st-chp8-p240-ferdinand-collected-mehus-canvases", "cand-8060", "cand-1609",
         "assiduously_collected_mehus_canvases_to_make_amends_for_neglect",
         "Haskell says Ferdinand sought to make amends for neglecting Mehus by assiduously collecting his canvases.", "mehus_canvases", (351, 351),
         "The canvases are not individually identified; do not assume this acquisition claim refers only to the thirty works mentioned earlier.",
         ["cand-8060", "cand-1632", "cand-1609"], True,
         "The source explicitly attributes the collection of Mehus’s canvases to Ferdinand.",
         {"footnote_marker": 1, "footnote_statement_ids": ["st-chp8-p240-note1-fogolari-mehus-acquisition"]}),
        ("st-chp8-p240-special-room-at-poggio-a-caiano", "cand-8062", "cand-1966",
         "special_room_at_poggio_held_small_examples_of_favourite_artists",
         "Haskell says Ferdinand had a special room at Poggio a Caiano containing small examples by his favourite ancient and contemporary artists.", "special_room", (352, 352),
         "The relation to any other Medici room is unresolved; the small examples are not individually identified.",
         ["cand-1609", "cand-8062", "cand-1966"], True,
         "The source directly locates the described room at Poggio a Caiano.", None),
        ("st-chp8-p240-collections-at-villa-di-castello", "cand-1609", "cand-8064",
         "kept_a_large_collection_at_villa_di_castello",
         "Haskell says Ferdinand kept a further large collection at the Villa di Castello.", "castello_collections", (353, 354),
         "The residence is retained as named; no identity with another Medici site is inferred.",
         ["cand-1609", "cand-8064"], True,
         "The source explicitly names the Villa di Castello as a location for Ferdinand’s further collection.", None),
        ("st-chp8-p240-ferdinand-displayed-policy-to-sacconi", "cand-1609", "cand-2325",
         "applied_exhibition_policy_to_sacconi",
         "Haskell says Ferdinand adopted the same exhibition policy toward Marco Sacconi.", "sacconi_policy", (357, 357),
         "The specific work or display is not identified in this sentence; note 3 cites a letter locator.",
         ["cand-1609", "cand-2325", "cand-0128"], True,
         "The source directly says Ferdinand extended the exhibition policy to Sacconi.",
         {"footnote_marker": 3, "footnote_statement_ids": ["st-chp8-p240-note3-fogolari-letter12"]}),
        ("st-chp8-p240-ferdinand-admired-cassana-portrait-cook", "cand-1609", "cand-7940",
         "praised_gran_gusto_of_cassanas_portrait_of_a_cook",
         "Haskell says Ferdinand wrote in 1707 admiring the ‘gran gusto’ of Cassana’s Portrait of a Cook.", "cassana_admiration", (357, 357),
         "This is Haskell’s report of Ferdinand’s aesthetic judgment; the letter is cited in note 4.",
         ["cand-1609", "cand-0593", "cand-7940"], False,
         "Aesthetic evaluation is preserved as a claim, not a separate formal relation.",
         {"footnote_marker": 4, "footnote_statement_ids": ["st-chp8-p240-note4-fogolari-letter120"]}),
    ]:
        extras = extras or {}
        rows.append(new_statement(sid, subject=subject, object_=object_, predicate=predicate,
            claim=claim, quote=q[key], lines=lines, qualification=qualification,
            mentioned=mentioned, relation=relation, relation_note=note, extras=extras))
        by_id[sid] = rows[-1]

    for row in rows:
        if row.get("statement_id") == "st-chp8-p240-mehus-collection":
            row.setdefault("qualifiers", {}).pop("continuation_from_segment_id", None)
        if row.get("statement_id") == "st-chp8-p240-ferdinand-mehus-canvases-and-son":
            row.setdefault("qualifiers", {}).pop("continuation_closed_by_segment_id", None)

    if {row["statement_id"] for row in rows} & NEW_IDS != NEW_IDS:
        raise SystemExit("not all planned p.240 statements were created")
    current = [row for row in rows if row.get("segment_id") == SEGMENT]
    if len(current) != len(EXPECTED_EXISTING) + len(NEW_IDS):
        raise SystemExit(f"unexpected p.240 post-edit row count: {len(current)}")
    flags = {}
    for row in current:
        key = str(row.get("qualifiers", {}).get("relation_candidate"))
        flags[key] = flags.get(key, 0) + 1
    if flags.get("None", 0):
        raise SystemExit(f"p.240 still has unset relation_candidate rows: {flags}")
    mentions_output, mention_changes = revise_mentions(mentions_bytes)
    preview = {
        "mode": "dry-run", "p240_existing": len(existing), "p240_added": len(NEW_IDS),
        "p240_statement_total": len(current), "statement_total": len(rows),
        "p240_relation_candidate_flags": flags,
        "ricci_person_mentions_corrected": mention_changes,
        "ricci_person_statement_endpoints_corrected": len(RICCI_PERSON_SUBJECT_IDS) + len(RICCI_PERSON_OBJECT_IDS),
        "ricci_work_group_reference_preserved": RICCI_WORK_STATEMENT_ID,
        "ocr_corrections": [
            "p.240 L355 confmed -> confined", "p.240 L355 instrumentof -> instrument of",
            "p.240 L357 superscript ? -> footnote 4",
        ],
        "wrong_mapping_corrected": "Sebastiano Ricci person cand-2179 -> cand-2154 across p.235-p.240; the p.390 work-group reference remains cand-2179",
        "new_statement_ids": sorted(NEW_IDS),
    }
    return preview, rows, mentions_output


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
preview, rows, mentions_output = plan()
if not args.apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)
table_backup = TABLE.with_name(TABLE.name + BACKUP_SUFFIX)
mentions_backup = MENTIONS.with_name(MENTIONS.name + BACKUP_SUFFIX)
if table_backup.exists() or mentions_backup.exists():
    raise SystemExit("a planned backup already exists; refusing apply")
shutil.copy2(TABLE, table_backup)
shutil.copy2(MENTIONS, mentions_backup)
atomic_write(TABLE, jsonl_bytes(rows))
atomic_write(MENTIONS, mentions_output)
preview["mode"] = "applied"
preview["backups"] = [str(table_backup.relative_to(ROOT)), str(mentions_backup.relative_to(ROOT))]
print(json.dumps(preview, ensure_ascii=False, indent=2))
