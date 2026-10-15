"""Refine p.238 body statements against the printed page and classify open items."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SEGMENTS = ROOT / "04-knowledge" / "tables" / "segments.jsonl"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE = ROOT / SOURCE_REL
SEGMENT = "chp-8:08_CHP-8_sec_ii:l327-336"
BACKUP_SUFFIX = ".bak-s2-chp8-p238-l327-336-semantic-review-20261014"
EXPECTED_TABLE_SHA256 = "eb0d549f6d04b33ae01d527df25db3197345307f88365fc9233841bbc7bdd6c9"
EXPECTED_EXISTING = {
    "st-chp8-p238-copy-st-william-sent",
    "st-chp8-p238-crespi-worked-for-ferdinand-through-1708",
    "st-chp8-p238-genre-scenes-and-fair",
    "st-chp8-p238-genre-scenes-and-subject-popularity",
    "st-chp8-p238-letters-prevented-fresco-destruction",
    "st-chp8-p238-many-pictures-gifts-and-godfather",
    "st-chp8-p238-mutual-patronage-connection",
    "st-chp8-p238-nativity-and-selfportrait-sent",
    "st-chp8-p238-painters-family-sent-and-evaluated",
    "st-chp8-p238-pepoli-frescoes-and-reputation",
    "st-chp8-p238-pittore-attuale-recognition",
    "st-chp8-p238-return-bologna-and-possible-third-visit",
    "st-chp8-p238-return-to-bologna",
    "st-chp8-p238-returned-to-florence-and-housed-at-pratolino",
    "st-chp8-p238-ricci-acquired-work",
    "st-chp8-p238-ricci-financed-travels",
    "st-chp8-p238-selfportrait-response-and-friendship",
    "st-chp8-p238-silva-satirical-picture",
    "st-chp8-p238-son-named-in-ferdinands-honour",
    "st-chp8-p238-vassalage-promise",
}
NEW_IDS = {
    "st-chp8-p238-ferdinand-eager-to-use-crespi",
    "st-chp8-p238-selfportrait-arrived-a-month-later",
    "st-chp8-p238-eternal-remembrance-assurance",
    "st-chp8-p238-friendship-sealed-after-selfportrait",
    "st-chp8-p238-frescoes-established-crespis-reputation",
    "st-chp8-p238-pepoli-considered-palace-alterations",
    "st-chp8-p238-many-genre-scenes-after-court-appointment",
    "st-chp8-p238-fair-masterpiece-assessment",
    "st-chp8-p238-fair-includes-courtier-portraits",
    "st-chp8-p238-women-washing-scene-sent",
    "st-chp8-p238-laundry-subject-popularity",
    "st-chp8-p238-ferdinand-collected-crespi-work",
    "st-chp8-p238-ferdinand-gave-lavish-presents",
    "st-chp8-p238-ferdinand-godfather-to-crespi-son",
    "st-chp8-p238-ferdinand-gave-rooms-at-pratolino",
    "st-chp8-p238-crespi-stayed-at-pratolino",
    "st-chp8-p238-possible-third-florence-visit",
    "st-chp8-p238-ferdinand-final-illness",
    "st-chp8-p238-painters-family-informal-group-assessment",
    "st-chp8-p238-painters-family-confidence-in-ferdinands-taste",
}


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
        "printed_page": 238, "pdf_physical_page": 44,
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
                  text_layer="body", extras=None):
    row = {
        "statement_id": statement_id, "segment_id": SEGMENT,
        "subject_candidate_id": subject, "object_candidate_id": object_,
        "predicate": predicate, "qualifiers": {}, "original_quote": quote,
        "origin": "book", "source_file": SOURCE_REL,
    }
    set_statement(row, subject=subject, object_=object_, predicate=predicate,
        claim=claim, quote=quote, lines=lines, qualification=qualification,
        mentioned=mentioned, relation=relation, relation_note=relation_note,
        text_layer=text_layer, extras=extras)
    return row


def plan():
    table_bytes = TABLE.read_bytes()
    if sha(table_bytes) != EXPECTED_TABLE_SHA256:
        raise SystemExit("statement table changed since p.237 review; refusing write")
    meta = next((r for r in read_jsonl(SEGMENTS) if r.get("segment_id") == SEGMENT), None)
    if not meta or (meta.get("line_start"), meta.get("line_end")) != (327, 336):
        raise SystemExit("unexpected p.238 segment metadata")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[326:336])
    if sha(segment_text.encode("utf-8")) != meta.get("sha256"):
        raise SystemExit("p.238 source segment hash mismatch")
    l328, l329, l330, l331, l332, l333, l334, l335, l336 = (
        source_lines[n - 1] for n in range(328, 337)
    )
    q = {
        "crespi_maintains": cut(l328, "was clearly as anxious to maintain his connection with Ferdinand", " as was the latter"),
        "ferdinand_uses": cut(l328, "as was the latter to make use of a painter", " Hardly had he returned"),
        "return_february": cut(l328, "Hardly had he returned to Bologna", " before he began"),
        "nativity": cut(l328, "a Nativity arrived early in March", ", followed by"),
        "selfportrait_sent": cut(l328, "followed by a Self portrait a month later", " with assurances"),
        "remembrance": cut(l328, "with assurances of the artist’s eternal remembrance of the Prince’s kindness", " and promises"),
        "vassallaggio": cut(l328, "promises of his own ‘vasallaggio’", " The Prince"),
        "prince_delighted": "\n".join([
            cut(l328, "The Prince wrote back to say how delighted he was with the"),
            cut(l329, "Selfportrait that showed the artist’s good humour1", " and thereafter"),
        ]),
        "friendship": cut(l329, "and thereafter the friendship between the two men was sealed.", " Indeed"),
        "ricci_financed": cut(l329, "the rich marchandamateur", " and subsequently acquired"),
        "ricci_acquired": cut(l329, "and subsequently acquired a very large proportion of his work", "; and also the Pepoli family"),
        "pepoli_frescoes": cut(l329, "in whose palace he had some fifteen years earlier painted the great ceiling frescoes", " which first established"),
        "fresco_reputation": cut(l329, "which first established his reputation as a considerable and highly original master.", " Now in 1708"),
        "pepoli_plan": cut(l329, "Now in 1708 the Pepoli were considering structural alterations to the palace which would involve destroying the frescoes", ", and only two urgent letters"),
        "letters_stopped_plan": cut(l329, "only two urgent letters from Ferdinand stopped this plan being carried out.2"),
        "worked_for_ferdinand": cut(l330, "Meanwhile throughout 1708 Crespi continued to work for him.", " In December"),
        "st_william": cut(l330, "In December he sent a copy of Guercino’s St William of Aquitaine", " as well as"),
        "painters_family_sent": "\n".join([
            cut(l330, "as well as his own small painting of"),
            cut(l331, "The Painter’s Family", ", the most informal portrait group"),
        ]),
        "family_informal": cut(l331, "the most informal portrait group that had yet appeared in Italian art", " and a striking testimony"),
        "family_confidence": cut(l331, "and a striking testimony to Crespi’s confidence in Ferdinand’s tastes", " (Plate 37a)"),
        "silva_picture": cut(l332, "During these months he also sent a satirical picture", ", as well as two small genre scenes"),
        "two_genre_scenes": cut(l332, "as well as two small genre scenes of Children at Play and Women washing their Laundry at a Fountain", "—an early treatment"),
        "laundry_popularity": cut(l332, "an early treatment of a subject", ".4", include_end=True),
        "returned_florence": cut(l333, "In 1709 Crespi returned to Florence with his family", " and was given rooms"),
        "gave_rooms": "\n".join([
            cut(l333, "and was given rooms by"),
            cut(l334, "Ferdinand in his villa at Pratolino", " where he stayed"),
        ]),
        "stayed_months": cut(l334, "where he stayed for several months", ". During this visit"),
        "many_pictures": cut(l334, "During this visit he painted a large number of pictures for the Grand Prince", ", who collected his work"),
        "collected_work": cut(l334, "who collected his work with increasing enthusiasm", " and who showed his appreciation"),
        "lavish_presents": cut(l334, "who showed his appreciation with lavish presents", " and by consenting"),
        "godfather": cut(l334, "and by consenting to become godfather to Crespi’s newborn son", ", called Ferdinando"),
        "son_named": cut(l334, "called Ferdinando in his honour", ". At the same time"),
        "court_title": cut(l334, "At the same time he gave official recognition to Crespi’s position at court by naming him his ‘pittore attuale’", ". Crespi responded"),
        "genre_scenes_1709": cut(l334, "Crespi responded with a great many genre scenes", " and one of his masterpieces"),
        "fair_work": cut(l334, "Crespi responded with a great many genre scenes and one of his masterpieces, the Fair at Poggio a Caiano", " which included portraits"),
        "fair_masterpiece": cut(l334, "one of his masterpieces, the Fair at Poggio a Caiano", " which included portraits"),
        "fair_portraits": "\n".join([
            cut(l334, "which included portraits of"),
            cut(l335, "Ferdinand’s courtiers", " (Plate 37b).6"),
        ]),
        "return_november": cut(l336, "By the beginning of November he was back in Bologna", " It is possible"),
        "third_visit": cut(l336, "It is possible that he paid a third visit to Florence", ", but by this time"),
        "final_illness": cut(l336, "Ferdinand’s final illness was upon him", " and the"),
    }
    ranges = {
        "crespi_maintains": (328, 328), "ferdinand_uses": (328, 328), "return_february": (328, 328),
        "nativity": (328, 328), "selfportrait_sent": (328, 328), "remembrance": (328, 328),
        "vassallaggio": (328, 328), "prince_delighted": (328, 329), "friendship": (329, 329),
        "ricci_financed": (329, 329), "ricci_acquired": (329, 329), "pepoli_frescoes": (329, 329),
        "fresco_reputation": (329, 329), "pepoli_plan": (329, 329), "letters_stopped_plan": (329, 329),
        "worked_for_ferdinand": (330, 330), "st_william": (330, 330), "painters_family_sent": (330, 331),
        "family_informal": (331, 331), "family_confidence": (331, 331), "silva_picture": (332, 332),
        "two_genre_scenes": (332, 332), "laundry_popularity": (332, 332), "returned_florence": (333, 333),
        "gave_rooms": (333, 334), "stayed_months": (334, 334), "many_pictures": (334, 334),
        "collected_work": (334, 334), "lavish_presents": (334, 334), "godfather": (334, 334),
        "son_named": (334, 334), "court_title": (334, 334), "genre_scenes_1709": (334, 334),
        "fair_work": (334, 335), "fair_masterpiece": (334, 334), "fair_portraits": (334, 335),
        "return_november": (336, 336), "third_visit": (336, 336), "final_illness": (336, 336),
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
        raise SystemExit(f"unexpected p.238 statement set: {len(existing)} rows")
    if set(by_id) & NEW_IDS:
        raise SystemExit("one or more planned p.238 statement IDs already exist")

    def revise(statement_id, *, subject, object_, predicate, claim, quote, lines,
               qualification, mentioned, relation, relation_note, extras=None):
        qualifiers = by_id[statement_id].setdefault("qualifiers", {})
        for key in ("ocr_corrections", "continuation_to_segment_id", "footnote_marker", "footnote_statement_ids"):
            if not extras or key not in extras:
                qualifiers.pop(key, None)
        set_statement(by_id[statement_id], subject=subject, object_=object_, predicate=predicate,
            claim=claim, quote=quote, lines=lines, qualification=qualification,
            mentioned=mentioned, relation=relation, relation_note=relation_note,
            extras=extras)

    revise("st-chp8-p238-copy-st-william-sent",
        subject="cand-0871", object_="cand-0875", predicate="sent_copy_of_guercinos_st_william_in_december_1708",
        claim="In December 1708 Crespi sent Ferdinand a copy of Guercino’s St William of Aquitaine.",
        quote=q["st_william"], lines=(330, 330),
        qualification="The index candidate identifies Crespi’s copy; keep it distinct from Guercino’s original painting.",
        mentioned=["cand-0871", "cand-1609", "cand-0875", "cand-1258", "cand-1269"], relation=True,
        relation_note="The source says Crespi sent the copy while continuing to work for Ferdinand.")
    revise("st-chp8-p238-crespi-worked-for-ferdinand-through-1708",
        subject="cand-0871", object_="cand-1609", predicate="continued_working_for_ferdinand_throughout_1708",
        claim="Haskell says Crespi continued to work for Ferdinand throughout 1708.",
        quote=q["worked_for_ferdinand"], lines=(330, 330),
        qualification="This is Haskell’s summary of the patronage relationship during 1708.",
        mentioned=["cand-0871", "cand-1609"], relation=True,
        relation_note="Directly stated artist-to-patron work relationship.")
    revise("st-chp8-p238-genre-scenes-and-subject-popularity",
        subject="cand-0871", object_="cand-0874", predicate="sent_children_at_play_to_ferdinand",
        claim="During these months Crespi sent a small genre scene, Children at Play, in the context of his 1708 work for Ferdinand.",
        quote=q["two_genre_scenes"], lines=(332, 332),
        qualification="The sentence presents the two scenes as part of Crespi’s sending; the preceding sentence states that he continued working for Ferdinand.",
        mentioned=["cand-0871", "cand-1609", "cand-0874", "cand-0887"], relation=True,
        relation_note="The source reports Crespi sending the named scene during his 1708 work for Ferdinand.",
        extras={"footnote_marker": 4, "footnote_statement_ids": ["st-chp8-p238-note4-pictures-at-pisa-cabinet"]})
    revise("st-chp8-p238-letters-prevented-fresco-destruction",
        subject="cand-1609", object_="cand-8041", predicate="two_urgent_letters_stopped_pepoli_plan_against_frescoes",
        claim="Two urgent letters from Ferdinand stopped the Pepoli plan that would have destroyed Crespi’s ceiling frescoes.",
        quote=q["letters_stopped_plan"], lines=(329, 329),
        qualification="Haskell reports the intervention; note 2 cites correspondence but does not identify which two of its three Pepoli letter locators are the urgent pair.",
        mentioned=["cand-1609", "cand-7377", "cand-1872", "cand-8041", "cand-8042"], relation=True,
        relation_note="The text explicitly attributes prevention of the planned destruction to Ferdinand’s two urgent letters.",
        extras={"footnote_marker": 2, "footnote_statement_ids": ["st-chp8-p238-note2-ricci-pepoli-correspondence"]})
    revise("st-chp8-p238-many-pictures-gifts-and-godfather",
        subject="cand-0871", object_="cand-1609", predicate="painted_many_pictures_for_ferdinand_in_1709",
        claim="During his 1709 visit to Pratolino, Crespi painted a large number of pictures for Ferdinand.",
        quote=q["many_pictures"], lines=(334, 334),
        qualification="The works are not individually identified in this clause; collecting, gifts and godfatherhood are recorded separately.",
        mentioned=["cand-0871", "cand-1609", "cand-7838"], relation=True,
        relation_note="The source directly states that Crespi painted pictures for the Grand Prince.")
    revise("st-chp8-p238-mutual-patronage-connection",
        subject="cand-0871", object_="cand-1609", predicate="anxious_to_maintain_connection_with_ferdinand",
        claim="Haskell says Crespi was anxious to maintain his connection with Ferdinand.",
        quote=q["crespi_maintains"], lines=(328, 328),
        qualification="This is the Crespi-to-Ferdinand direction; Ferdinand’s reciprocal interest is separated below.",
        mentioned=["cand-0871", "cand-1609"], relation=True,
        relation_note="The source explicitly reports Crespi’s wish to maintain his patronage connection.")
    revise("st-chp8-p238-nativity-and-selfportrait-sent",
        subject="cand-0871", object_="cand-0883", predicate="nativity_arrived_early_march_1708",
        claim="After returning to Bologna, Crespi began sending pictures to Ferdinand; a Nativity arrived early in March.",
        quote=q["nativity"], lines=(328, 328),
        qualification="The sentence says the Nativity arrived early in March; the separate Selfportrait followed about a month later.",
        mentioned=["cand-0871", "cand-3398", "cand-1609", "cand-0883"], relation=True,
        relation_note="The source reports the arrival of a named Crespi work for his new patron.")
    revise("st-chp8-p238-painters-family-sent-and-evaluated",
        subject="cand-0871", object_="cand-0884", predicate="sent_painters_family_to_ferdinand",
        claim="In December 1708 Crespi sent his small painting The Painter’s Family.",
        quote=q["painters_family_sent"], lines=(330, 331),
        qualification="The painting is distinct from the copy of Guercino’s St William; the critical assessment and cited location are recorded separately.",
        mentioned=["cand-0871", "cand-1609", "cand-0884"], relation=True,
        relation_note="The source directly reports Crespi sending the named painting to Ferdinand.",
        extras={"footnote_marker": 3, "footnote_statement_ids": ["st-chp8-p238-note3-ferdinand-letter-draft", "st-chp8-p238-note3-painters-family-uffizi"]})
    revise("st-chp8-p238-pepoli-frescoes-and-reputation",
        subject="cand-0871", object_="cand-8041", predicate="painted_ceiling_frescoes_in_pepoli_palace",
        claim="About fifteen years before 1708, Crespi painted the great ceiling frescoes in the Pepoli palace.",
        quote=q["pepoli_frescoes"], lines=(329, 329),
        qualification="The fresco group is not individuated into separate scenes; Haskell’s claim about its role in Crespi’s reputation is separate.",
        mentioned=["cand-0871", "cand-7377", "cand-1872", "cand-8041"], relation=True,
        relation_note="The source explicitly attributes the ceiling frescoes in the Pepoli palace to Crespi.")
    revise("st-chp8-p238-pittore-attuale-recognition",
        subject="cand-1609", object_="cand-0871", predicate="officially_recognized_crespis_court_position_as_pittore_attuale",
        claim="Ferdinand officially recognized Crespi’s position at court by naming him his ‘pittore attuale’.",
        quote=q["court_title"], lines=(334, 334),
        qualification="Retain the Italian designation; no modern office equivalent is imposed.",
        mentioned=["cand-1609", "cand-0871", "cand-8010", "cand-8044"], relation=True,
        relation_note="The source directly reports Ferdinand conferring the court designation.")
    revise("st-chp8-p238-return-bologna-and-possible-third-visit",
        subject="cand-0871", object_="cand-3398", predicate="back_in_bologna_by_early_november_1709",
        claim="Haskell says Crespi was back in Bologna by the beginning of November 1709.",
        quote=q["return_november"], lines=(336, 336),
        qualification="The printed footnote is no. 6 and cites a letter dated 3 November 1709; the letter date is not treated as the exact travel date.",
        mentioned=["cand-0871", "cand-3398", "cand-8039"], relation=True,
        relation_note="The source reports Crespi’s return to Bologna by early November.",
        extras={"footnote_marker": 6, "footnote_statement_ids": ["st-chp8-p238-note6-return-letter"],
                "ocr_corrections": [{"source_line": 336, "ocr": "8", "print": "6", "basis": "CHP-8.pdf physical page 44"}]})
    revise("st-chp8-p238-return-to-bologna",
        subject="cand-0871", object_="cand-3398", predicate="returned_to_bologna_at_end_of_february_1708",
        claim="Haskell says Crespi returned to Bologna at the end of February 1708.",
        quote=q["return_february"], lines=(328, 328),
        qualification="This agrees with p.237 note 5, which places Crespi back in Bologna by 26 February; neither wording fixes an exact travel day.",
        mentioned=["cand-0871", "cand-3398", "cand-8015"], relation=True,
        relation_note="The source explicitly places Crespi’s return to Bologna at the end of February.",
        extras={"cross_reference_statement_ids": ["st-chp8-p237-note5-return-to-bologna"]})
    revise("st-chp8-p238-returned-to-florence-and-housed-at-pratolino",
        subject="cand-0871", object_="cand-3397", predicate="returned_to_florence_with_family_in_1709",
        claim="In 1709 Crespi returned to Florence with his family.", quote=q["returned_florence"], lines=(333, 333),
        qualification="The return with family is separate from Ferdinand’s provision of rooms at Pratolino and the duration of Crespi’s stay.",
        mentioned=["cand-0871", "cand-3397"], relation=True,
        relation_note="The source directly reports Crespi returning to Florence with his family.")
    revise("st-chp8-p238-ricci-acquired-work",
        subject="cand-2147", object_="cand-0871", predicate="acquired_very_large_proportion_of_crespis_work",
        claim="Giovanni Ricci subsequently acquired a very large proportion of Crespi’s work.",
        quote=q["ricci_acquired"], lines=(329, 329),
        qualification="Haskell gives a broad proportion, not an itemized list or exact count of works.",
        mentioned=["cand-2147", "cand-0871"], relation=True,
        relation_note="The source explicitly reports Ricci acquiring a large share of Crespi’s work.")
    revise("st-chp8-p238-ricci-financed-travels",
        subject="cand-2147", object_="cand-0871", predicate="financed_crespis_early_travels_through_italy",
        claim="Haskell describes Giovanni Ricci as a wealthy marchand-amateur who financed Crespi’s early travels throughout Italy.",
        quote=q["ricci_financed"], lines=(329, 329),
        qualification="The cited biography and financing details were not independently checked.",
        mentioned=["cand-2147", "cand-0871", "cand-3461"], relation=True,
        relation_note="The source directly attributes financing of Crespi’s early travels to Giovanni Ricci.",
        extras={"ocr_corrections": [{"source_line": 329, "ocr": "marchandamateur", "print": "marchand-amateur", "basis": "CHP-8.pdf physical page 44"}]})
    revise("st-chp8-p238-selfportrait-response-and-friendship",
        subject="cand-1609", object_="cand-0886", predicate="replied_delighted_with_crespi_selfportrait",
        claim="Ferdinand wrote back that he was delighted with Crespi’s Selfportrait, which showed the artist’s good humour.",
        quote=q["prince_delighted"], lines=(328, 329),
        qualification="This records Ferdinand’s reported response to the painting; Haskell’s separate statement that their friendship was sealed is split out.",
        mentioned=["cand-1609", "cand-0871", "cand-0886"], relation=True,
        relation_note="The source reports Ferdinand’s written response to Crespi’s named portrait.",
        extras={"footnote_marker": 1, "footnote_statement_ids": ["st-chp8-p238-note1-march-april-letter-locators"]})
    revise("st-chp8-p238-silva-satirical-picture",
        subject="cand-0871", object_="cand-0885", predicate="sent_satirical_picture_of_silva_as_gift_to_ferdinand",
        claim="During these months Crespi sent Ferdinand a satirical picture of Don Carlo Silva, the priest who had commissioned the Massacre of the Innocents and then failed to keep the agreement.",
        quote=q["silva_picture"], lines=(332, 332),
        qualification="P.237 note 2 identifies the priest as Don Carlo Silva and reports the commission/default; the picture itself remains unidentified beyond the index subentry.",
        mentioned=["cand-0871", "cand-0885", "cand-2433", "cand-0882", "cand-1609"], relation=True,
        relation_note="The source states that Crespi sent the satirical picture as a gift to Ferdinand.",
        extras={"footnote_marker": 4, "footnote_statement_ids": ["st-chp8-p238-note4-pictures-at-pisa-cabinet"]})
    revise("st-chp8-p238-son-named-in-ferdinands-honour",
        subject="cand-8043", object_="cand-1609", predicate="named_ferdinando_in_honour_of_ferdinand",
        claim="Crespi’s newborn son was called Ferdinando in honour of Ferdinand.",
        quote=q["son_named"], lines=(334, 334),
        qualification="Only the naming and its stated honouree are recorded; no later identity or biography is inferred.",
        mentioned=["cand-0871", "cand-8043", "cand-1609"], relation=True,
        relation_note="The source directly states that Crespi named his son in Ferdinand’s honour.")
    revise("st-chp8-p238-vassalage-promise",
        subject="cand-0871", object_="cand-1609", predicate="promised_own_vasallaggio_to_ferdinand",
        claim="With the Selfportrait, Crespi promised his own ‘vasallaggio’ to Ferdinand.",
        quote=q["vassallaggio"], lines=(328, 328),
        qualification="Retain the quoted Italian word; this does not establish a legal feudal status.",
        mentioned=["cand-0871", "cand-1609", "cand-0886", "cand-8045"], relation=True,
        relation_note="The source reports Crespi’s own promise of service or allegiance to Ferdinand.")

    def add(statement_id, subject, object_, predicate, key, claim, lines, qualification,
            mentioned, relation, relation_note, extras=None):
        row = new_statement(statement_id, subject=subject, object_=object_, predicate=predicate,
            claim=claim, quote=q[key], lines=lines, qualification=qualification,
            mentioned=mentioned, relation=relation, relation_note=relation_note, extras=extras)
        rows.append(row)
        by_id[statement_id] = row

    add("st-chp8-p238-ferdinand-eager-to-use-crespi", "cand-1609", "cand-0871",
        "eager_to_use_crespi_as_painter_suited_to_his_temperament", "ferdinand_uses",
        "Haskell says Ferdinand was as anxious to make use of Crespi, whose gifts suited the Prince’s temperament.", (328, 328),
        "This records Ferdinand’s direction of the patronage connection, separately from Crespi’s wish to maintain it.",
        ["cand-1609", "cand-0871"], True,
        "The source directly attributes the wish to make use of the painter to Ferdinand.")
    add("st-chp8-p238-selfportrait-arrived-a-month-later", "cand-0871", "cand-0886",
        "sent_selfportrait_about_a_month_after_nativity", "selfportrait_sent",
        "Crespi sent Ferdinand a Selfportrait about a month after the Nativity arrived.", (328, 328),
        "The source says ‘a month later’ without specifying a calendar date; the print spells Selfportrait as one word.",
        ["cand-0871", "cand-1609", "cand-0883", "cand-0886"], True,
        "The source reports a dated sequence of two pictures sent by Crespi to his patron.",
        {"ocr_corrections": [{"source_line": 328, "ocr": "Self portrait", "print": "Selfportrait", "basis": "CHP-8.pdf physical page 44"}]})
    add("st-chp8-p238-eternal-remembrance-assurance", "cand-0871", "cand-1609",
        "assured_ferdinand_of_eternal_remembrance_for_his_kindness", "remembrance",
        "With the Selfportrait Crespi sent assurances of eternal remembrance for the Prince’s kindness.", (328, 328),
        "This is a reported assurance in the picture correspondence, not an independently consulted letter text.",
        ["cand-0871", "cand-1609", "cand-0886"], True,
        "The source directly reports an assurance from Crespi to Ferdinand.")
    add("st-chp8-p238-friendship-sealed-after-selfportrait", "cand-0871", "cand-1609",
        "friendship_sealed_after_selfportrait_exchange", "friendship",
        "Haskell says the friendship between Crespi and Ferdinand was sealed after the Selfportrait exchange.", (329, 329),
        "This is Haskell’s characterization of the relationship following Ferdinand’s reply.",
        ["cand-0871", "cand-1609", "cand-0886"], True,
        "The source explicitly describes the friendship between the two named men.")
    add("st-chp8-p238-frescoes-established-crespis-reputation", "cand-8041", "cand-0871",
        "established_crespis_reputation_as_original_master", "fresco_reputation",
        "Haskell says the Pepoli palace frescoes first established Crespi’s reputation as a considerable and highly original master.", (329, 329),
        "This is Haskell’s retrospective assessment of the frescoes’ role in Crespi’s reputation.",
        ["cand-8041", "cand-0871", "cand-1872"], True,
        "The source explicitly attributes this effect on Crespi’s reputation to the fresco group.")
    add("st-chp8-p238-pepoli-considered-palace-alterations", "cand-7377", "cand-8041",
        "considered_palace_alterations_that_would_destroy_frescoes_in_1708", "pepoli_plan",
        "In 1708 the Pepoli were considering alterations to their palace that would involve destroying Crespi’s ceiling frescoes.", (329, 329),
        "The text reports a contemplated plan, not completed alterations; the individual Pepoli decision-makers are unnamed.",
        ["cand-7377", "cand-1872", "cand-8041"], True,
        "The source directly attributes a possible destructive plan to the Pepoli family.")
    add("st-chp8-p238-many-genre-scenes-after-court-appointment", "cand-0871", None,
        "responded_to_court_position_with_many_genre_scenes", "genre_scenes_1709",
        "Haskell says Crespi responded to his court position with a great many genre scenes.", (334, 334),
        "The scenes are not individually identified in this sentence; no additional group-work candidate is created.",
        ["cand-0871", "cand-8010", "cand-8044"], False,
        "This is a source statement about an unspecified body of work, not a separately identified work endpoint.")
    add("st-chp8-p238-fair-masterpiece-assessment", "cand-0878", None,
        "haskell_called_fair_at_poggio_a_caiano_a_masterpiece", "fair_masterpiece",
        "Haskell calls The Fair at Poggio a Caiano one of Crespi’s masterpieces.", (334, 334),
        "This is Haskell’s critical assessment of the named painting.",
        ["cand-0878", "cand-0871", "cand-1966"], False,
        "An authorial evaluation of a work, not a separate historical relationship.")
    add("st-chp8-p238-fair-includes-courtier-portraits", "cand-0878", None,
        "included_portraits_of_ferdinands_courtiers", "fair_portraits",
        "The Fair at Poggio a Caiano includes portraits of Ferdinand’s courtiers.", (334, 335),
        "The courtiers are not individuated as a distinct endpoint; the claim is retained as a work-content assertion.",
        ["cand-0878", "cand-8010", "cand-1609"], False,
        "The source describes the contents of the painting without identifying the portrayed courtiers.",
        {"footnote_marker": 5, "footnote_statement_ids": ["st-chp8-p238-note5-fair-at-uffizi"],
         "ocr_corrections": [{"source_line": 335, "ocr": "6", "print": "5", "basis": "CHP-8.pdf physical page 44"}]})
    add("st-chp8-p238-women-washing-scene-sent", "cand-0871", "cand-0887",
        "sent_women_washing_laundry_at_fountain_scene", "two_genre_scenes",
        "During these months Crespi also sent a small genre scene, Women washing their Laundry at a Fountain.", (332, 332),
        "The recipient is understood from the sentence’s continuation of Crespi’s 1708 work for Ferdinand; the individual scene is identified by the index.",
        ["cand-0871", "cand-1609", "cand-0887", "cand-0874"], True,
        "The source presents the named scene as one of the pictures Crespi sent.",
        {"footnote_marker": 4, "footnote_statement_ids": ["st-chp8-p238-note4-pictures-at-pisa-cabinet"]})
    add("st-chp8-p238-laundry-subject-popularity", "cand-0887", None,
        "early_treatment_of_subject_later_popular_in_eighteenth_century", "laundry_popularity",
        "Haskell describes the Laundry at a Fountain scene as an early treatment of a subject that would become immensely popular with eighteenth-century artists.", (332, 332),
        "The future popularity claim is Haskell’s; the exact referent of ‘a subject’ remains the Laundry at a Fountain motif.",
        ["cand-0887", "cand-0871"], False,
        "This is a historical-artistic assessment of a subject’s later popularity.",
        {"footnote_marker": 4, "footnote_statement_ids": ["st-chp8-p238-note4-pictures-at-pisa-cabinet"]})
    add("st-chp8-p238-ferdinand-collected-crespi-work", "cand-1609", "cand-0871",
        "collected_crespis_work_with_increasing_enthusiasm", "collected_work",
        "During Crespi’s 1709 visit, Ferdinand collected his work with increasing enthusiasm.", (334, 334),
        "The passage gives no itemized list or total; the collection relationship is attributed to Ferdinand.",
        ["cand-1609", "cand-0871", "cand-7838"], True,
        "The source directly states that Ferdinand collected Crespi’s work.")
    add("st-chp8-p238-ferdinand-gave-lavish-presents", "cand-1609", "cand-0871",
        "showed_appreciation_to_crespi_with_lavish_presents", "lavish_presents",
        "Ferdinand showed his appreciation of Crespi with lavish presents during the 1709 visit.", (334, 334),
        "The presents are not identified individually.",
        ["cand-1609", "cand-0871"], True,
        "The source explicitly attributes the presents to Ferdinand and their recipient to Crespi.")
    add("st-chp8-p238-ferdinand-godfather-to-crespi-son", "cand-1609", "cand-8043",
        "consented_to_become_godfather_to_crespis_newborn_son", "godfather",
        "Ferdinand consented to become godfather to Crespi’s newborn son.", (334, 334),
        "The son’s later identity and biography are not inferred.",
        ["cand-1609", "cand-0871", "cand-8043"], True,
        "The source explicitly reports Ferdinand’s consent to be godfather to the named artist’s son.")
    add("st-chp8-p238-ferdinand-gave-rooms-at-pratolino", "cand-1609", "cand-0871",
        "provided_crespi_rooms_in_villa_at_pratolino", "gave_rooms",
        "Ferdinand gave Crespi rooms in his villa at Pratolino in 1709.", (333, 334),
        "The source names Pratolino as the villa location; this row records provision of rooms, not ownership or title to the villa.",
        ["cand-1609", "cand-0871", "cand-7838"], True,
        "The source directly reports Ferdinand providing rooms for Crespi.")
    add("st-chp8-p238-crespi-stayed-at-pratolino", "cand-0871", "cand-7838",
        "stayed_at_pratolino_for_several_months", "stayed_months",
        "Crespi stayed at Ferdinand’s Pratolino villa for several months.", (334, 334),
        "The duration is approximate; the exact villa identity remains for S3 alignment.",
        ["cand-0871", "cand-1609", "cand-7838"], True,
        "The source directly locates Crespi’s several-month stay at the named Pratolino villa.")
    add("st-chp8-p238-possible-third-florence-visit", "cand-0871", "cand-3397",
        "may_have_paid_third_visit_to_florence", "third_visit",
        "Haskell says Crespi may have paid a third visit to Florence.", (336, 336),
        "The possibility is preserved; the source does not assert that this visit occurred.",
        ["cand-0871", "cand-3397"], True,
        "The source presents a possible travel relation, not a confirmed journey.")
    add("st-chp8-p238-ferdinand-final-illness", "cand-1609", None,
        "final_illness_reported_by_haskell_in_1709", "final_illness",
        "Haskell says Ferdinand’s final illness was upon him by this time.", (336, 336),
        "This is a contextual authorial report; the sentence continues on p.239, where Haskell says Ferdinand’s great days of patronage were over.",
        ["cand-1609"], False,
        "A biographical condition, not a formal relation candidate.",
        {"continuation_to_segment_id": "chp-8:08_CHP-8_sec_ii:l338-348"})
    add("st-chp8-p238-painters-family-informal-group-assessment", "cand-0884", None,
        "haskell_called_painters_family_most_informal_portrait_group_yet", "family_informal",
        "Haskell calls The Painter’s Family the most informal portrait group yet to appear in Italian art.", (331, 331),
        "This is Haskell’s comparative art-historical evaluation of the painting.",
        ["cand-0884", "cand-0871"], False,
        "A critical assessment, not a distinct historical relationship.",
        {"footnote_marker": 3, "footnote_statement_ids": ["st-chp8-p238-note3-painters-family-uffizi"]})
    add("st-chp8-p238-painters-family-confidence-in-ferdinands-taste", "cand-0884", "cand-1609",
        "haskell_interpreted_painters_family_as_confidence_in_ferdinands_taste", "family_confidence",
        "Haskell interprets The Painter’s Family as a striking testimony to Crespi’s confidence in Ferdinand’s taste.", (331, 331),
        "This is Haskell’s interpretation of the painting’s significance, not an independently verified statement of Crespi’s motive.",
        ["cand-0884", "cand-0871", "cand-1609"], False,
        "An authorial interpretation of a work; the source does not make this a formal relation.",
        {"footnote_marker": 3, "footnote_statement_ids": ["st-chp8-p238-note3-painters-family-uffizi"]})

    if {row["statement_id"] for row in rows} & NEW_IDS != NEW_IDS:
        raise SystemExit("not all planned p.238 statements were created")
    current = [row for row in rows if row.get("segment_id") == SEGMENT]
    if sum(row.get("segment_id") == SEGMENT for row in rows) != len(EXPECTED_EXISTING) + len(NEW_IDS):
        raise SystemExit("unexpected p.238 post-edit row count")
    preview = {
        "mode": "dry-run", "p238_existing": len(existing), "p238_added": len(NEW_IDS),
        "p238_statement_total": len(current), "statement_total": len(rows),
        "classified_unset_rows": [
            "st-chp8-p238-mutual-patronage-connection",
            "st-chp8-p238-return-to-bologna",
            "st-chp8-p238-son-named-in-ferdinands-honour",
            "st-chp8-p238-vassalage-promise",
        ],
        "ocr_corrections": [
            "p.238 L328 Self portrait -> Selfportrait",
            "p.238 L329 marchandamateur -> marchand-amateur",
            "p.238 L335 footnote marker 6 -> printed 5",
            "p.238 L336 footnote marker 8 -> printed 6",
        ],
        "new_statement_ids": sorted(NEW_IDS),
    }
    return preview, rows


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
preview, rows = plan()
if not args.apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)
backup = TABLE.with_name(TABLE.name + BACKUP_SUFFIX)
if backup.exists():
    raise SystemExit(f"backup already exists: {backup}")
shutil.copy2(TABLE, backup)
atomic_write(TABLE, jsonl_bytes(rows))
preview["mode"] = "applied"
preview["backup"] = str(backup.relative_to(ROOT))
print(json.dumps(preview, ensure_ascii=False, indent=2))
