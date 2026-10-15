"""Atomize and classify the p.239 body statements against the printed page."""
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
SEGMENT = "chp-8:08_CHP-8_sec_ii:l338-348"
NEXT_SEGMENT = "chp-8:08_CHP-8_sec_ii:l350-359"
BACKUP_SUFFIX = ".bak-s2-chp8-p239-l338-348-semantic-review-20261014"
EXPECTED_TABLE_SHA256 = "2C94C1A424CD544DEB77B74EA26A8DBC517235366432EEEC6B21FA7371ACC6CF"
EXPECTED_EXISTING = {
    "st-chp8-p239-chardin-counterfactual",
    "st-chp8-p239-close-partnership",
    "st-chp8-p239-contemporaries-misread-crespi-humour",
    "st-chp8-p239-crespi-claimed-tintoretto-picture",
    "st-chp8-p239-crespi-humour-melancholy-sympathy",
    "st-chp8-p239-crespi-studies-venetian-painters",
    "st-chp8-p239-ferdinand-distinctive-patronage",
    "st-chp8-p239-ferdinand-removal-and-bologna",
    "st-chp8-p239-ferdinand-sensitive-collector",
    "st-chp8-p239-ferdinand-supported-history-picture-break",
    "st-chp8-p239-ferdinand-view-as-humourist",
    "st-chp8-p239-last-known-artist",
    "st-chp8-p239-longhi-on-restricting-effect",
    "st-chp8-p239-pictures-distributed-among-medici-residences",
    "st-chp8-p239-restraint-and-ferdinand-appreciation",
    "st-chp8-p239-three-hundred-pitti-pictures",
    "st-chp8-p239-venetian-emphasis",
}
NEW_IDS = {
    "st-chp8-p239-ferdinand-great-days-patronage-over",
    "st-chp8-p239-crespi-took-advantage-of-gallery",
    "st-chp8-p239-new-ventures-loss-prestige",
    "st-chp8-p239-genre-scenes-expected-humorous",
    "st-chp8-p239-crespi-poetic-sympathy",
    "st-chp8-p239-ferdinand-shared-misconceptions-uncertain",
    "st-chp8-p239-crespi-restraint-bawdy-subjects",
    "st-chp8-p239-ferdinand-modern-prince",
    "st-chp8-p239-only-princes-influential-patrons",
    "st-chp8-p239-pictures-distributed-in-country-houses",
    "st-chp8-p239-pictures-number-considerable",
    "st-chp8-p239-earlier-family-pictures-included",
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
        "printed_page": 239, "pdf_physical_page": 45,
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


def plan():
    table_bytes = TABLE.read_bytes()
    if sha(table_bytes).lower() != EXPECTED_TABLE_SHA256.lower():
        raise SystemExit("statement table changed since p.238 review; refusing write")
    meta = next((r for r in read_jsonl(SEGMENTS) if r.get("segment_id") == SEGMENT), None)
    if not meta or (meta.get("line_start"), meta.get("line_end")) != (338, 348):
        raise SystemExit("unexpected p.239 segment metadata")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[337:348])
    if sha(segment_text.encode("utf-8")) != meta.get("sha256"):
        raise SystemExit("p.239 source segment hash mismatch")
    l339, l340, l341, l342, l343, l344, l345, l346, l347, l348 = (
        source_lines[n - 1] for n in range(339, 349)
    )
    q = {
        "patronage_over": cut(l339, "great days of his patronage were over", "1 Crespi", include_end=False),
        "last_artist": cut(l339, "Crespi is indeed the last artist whom we know to have worked for him..."),
        "close_partnership": cut(l340, "Both painter and patron had benefited greatly from the close partnership between them."),
        "sensitive_collector": cut(l340, "Ferdinand was the most cultivated and sensitive collector that Crespi had yet (or ever was to) come across"),
        "gallery_study": "\n".join([
            cut(l340, "and in his gallery the artist was able to study at length those"),
            cut(l341, "Venetian painters whom they both loved", " That he took"),
        ]),
        "took_advantage": cut(l341, "That he took full advantage of this is proved by a letter", "2 Fully as important"),
        "tintoretto_letter": cut(l341, "in which he speaks of having been shown in the Medici collections a picture attributed to Tintoretto which had in fact been painted by himself", "2 Fully as important"),
        "support": cut(l341, "Fully as important was die support", " Such new ventures"),
        "ventures": cut(l341, "Such new ventures were bound to result in some loss of prestige and to meet with derision.", " The humour"),
        "contemporaries": cut(l341, "The humour with which all his contemporaries approached Crespi", " Genre scenes"),
        "genre_expectation": cut(l341, "Genre scenes were expected to be humorous and so they laughed", ", without realising"),
        "melancholy": cut(l341, "Crcspi’s humour was often tinged with melancholy", " and was in any case"),
        "sympathy": cut(l341, "and was in any case counteracted by a deep, poetic sympathy for the people whom he painted.", " It is difficult"),
        "ferdinand_uncertain": cut(l341, "It is difficult to say how much Ferdinand himself shared these misconceptions about Crespi’s art."),
        "ferdinand_humourist": cut(l342, "His recorded opinions and—much more important—his letters suggest that he too saw him primarily as a humourist", "3;"),
        "restraint": cut(l342, "the very great restraint with which the artist painted for him subjects which lay themselves open to gross or bawdy treatment (Plate 36b)", " makes clear"),
        "reliance": cut(l342, "makes clear that he must have relied on Ferdinand’s appreciating a side ef his temperament that was ignored by many.", " Indeed"),
        "distinctive_patronage": "\n".join([
            cut(l342, "Indeed, the unique place held by"),
            cut(l343, "Ferdinand in the history of Italian patronage is shown by the fact that such sober, sympathetic treatment of the poor and simple remained quite exceptional in Italian art."),
        ]),
        "chardin": cut(l344, "With the backing of a cultivated middle class Crespi might have turned into the Chardin to whom he is sometimes so near", "; in fact"),
        "modern_prince": cut(l344, "Ferdinand, the most ‘modern’ prince of the age in Italy", "—and as yet"),
        "only_princes": cut(l344, "and as yet only princes could be influential patrons", "—Crespi retired"),
        "retired_bologna": cut(l344, "Crespi retired into the provincial backwater of Bologna", ".4"),
        "pitti_distribution": "\n".join([
            cut(l345, "The pictures that Ferdinand amassed were distributed in his apartments in the Pitti"),
            cut(l346, "Palace", " and in the various"),
        ]),
        "country_houses": cut(l346, "and in the various country houses through which he moved during the year."),
        "numbers": cut(l347, "By the end of his life their numbers were very considerable.", " In the Pitti"),
        "pitti_300": cut(l347, "In the Pitti alone were 300 entirely from his private collection", ", quite apart"),
        "earlier_family": cut(l347, ", quite apart from the many which had been assembled by earlier members of the family", ".5"),
        "venetian_emphasis": cut(l347, "The accent was strongly on Venetian pictures", None),
        "longhi_note": cut(l348, "4 The restricting effect of this on Crespi’s art has been pointed out by R. Longhi in his introduction to the 1948 exhibition catalogue."),
    }
    ranges = {
        "patronage_over": (339, 339), "last_artist": (339, 339),
        "close_partnership": (340, 340), "sensitive_collector": (340, 340),
        "gallery_study": (340, 341), "took_advantage": (341, 341),
        "tintoretto_letter": (341, 341), "support": (341, 341),
        "ventures": (341, 341), "contemporaries": (341, 341),
        "genre_expectation": (341, 341), "melancholy": (341, 341),
        "sympathy": (341, 341), "ferdinand_uncertain": (341, 341),
        "ferdinand_humourist": (342, 342), "restraint": (342, 342),
        "reliance": (342, 342), "distinctive_patronage": (342, 343),
        "chardin": (344, 344), "modern_prince": (344, 344),
        "only_princes": (344, 344), "retired_bologna": (344, 344),
        "pitti_distribution": (345, 346), "country_houses": (346, 346),
        "numbers": (347, 347), "pitti_300": (347, 347),
        "earlier_family": (347, 347), "venetian_emphasis": (347, 347),
        "longhi_note": (348, 348),
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
        raise SystemExit(f"unexpected p.239 statement set: {len(existing)} rows")
    if set(by_id) & NEW_IDS:
        raise SystemExit("one or more planned p.239 statement IDs already exist")

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

    revise("st-chp8-p239-chardin-counterfactual",
        subject="cand-0871", object_="cand-0649", predicate="might_have_become_chardin_with_middle_class_backing",
        claim="Haskell speculates that with support from a cultivated middle class Crespi might have become the Chardin to whom he was sometimes close.",
        quote=q["chardin"], lines=(344, 344),
        qualification="This is a counterfactual comparison, not a claim that Crespi studied with or was directly influenced by Chardin.",
        mentioned=["cand-0871", "cand-0649"], relation=False,
        relation_note="The passage is a conditional art-historical comparison, not a historical relationship.")
    revise("st-chp8-p239-close-partnership",
        subject="cand-0871", object_="cand-1609", predicate="close_partnership_benefited_painter_and_patron",
        claim="Haskell says both painter and patron benefited greatly from their close partnership.",
        quote=q["close_partnership"], lines=(340, 340),
        qualification="The source explicitly calls the relationship a close partnership; the benefit is Haskell’s evaluation.",
        mentioned=["cand-0871", "cand-1609"], relation=True,
        relation_note="The source directly describes a close partnership between Crespi and Ferdinand.")
    revise("st-chp8-p239-contemporaries-misread-crespi-humour",
        subject="cand-0871", object_=None, predicate="contemporaries_humour_reflected_bewilderment_at_unconventional_painting",
        claim="Haskell says the humour with which Crespi’s contemporaries approached him reflected their bewilderment at his unconventional painting and coloured their appreciation of his art.",
        quote=q["contemporaries"], lines=(341, 341),
        qualification="This is Haskell’s general account of reception, not a named individual’s opinion.",
        mentioned=["cand-0871"], relation=False,
        relation_note="The claim concerns generalized artistic reception and has no identified relation endpoint.",
        extras={"ocr_corrections": [{"source_line": 341, "ocr": "Crcspi", "print": "Crespi", "basis": "CHP-8.pdf physical page 45"}]})
    revise("st-chp8-p239-crespi-claimed-tintoretto-picture",
        subject="cand-0871", object_="cand-8049", predicate="letter_reports_crespi_painted_picture_attributed_to_tintoretto",
        claim="Haskell says Crespi’s letter reports that he was shown in the Medici collections a picture attributed to Tintoretto but actually painted by Crespi.",
        quote=q["tintoretto_letter"], lines=(341, 341),
        qualification="The letter is unidentified and known here only through Haskell’s account; its report does not independently establish the work’s attribution.",
        mentioned=["cand-0871", "cand-8050", "cand-8052", "cand-8049", "cand-2627"], relation=True,
        relation_note="The source attributes a specific claim about the painting to Crespi’s letter; the cited letter remains unresolved as an archive candidate.",
        extras={"quoted_speaker": "Giuseppe Maria Crespi, as reported by Haskell",
                "footnote_marker": 2,
                "footnote_statement_ids": ["st-chp8-p239-note2-cross-reference"]})
    revise("st-chp8-p239-crespi-humour-melancholy-sympathy",
        subject="cand-0871", object_=None, predicate="crespis_humour_often_tinged_with_melancholy",
        claim="Haskell says Crespi’s humour was often tinged with melancholy.",
        quote=q["melancholy"], lines=(341, 341),
        qualification="This is Haskell’s characterization of Crespi’s humour.",
        mentioned=["cand-0871"], relation=False,
        relation_note="A biographical and interpretive characterization, not a formal relation.")
    revise("st-chp8-p239-crespi-studies-venetian-painters",
        subject="cand-0871", object_="cand-8051", predicate="studied_venetian_painters_in_ferdinands_gallery",
        claim="Haskell says Crespi was able to study at length the Venetian painters he and Ferdinand both loved in Ferdinand’s gallery.",
        quote=q["gallery_study"], lines=(340, 341),
        qualification="The gallery’s physical location is unspecified; do not equate it with the Medici collections or Pitti Palace.",
        mentioned=["cand-0871", "cand-1609", "cand-8051", "cand-8052"], relation=True,
        relation_note="The source directly states Crespi’s study of works in Ferdinand’s gallery.")
    revise("st-chp8-p239-ferdinand-distinctive-patronage",
        subject="cand-1609", object_="cand-4131", predicate="unique_patronage_position_shown_by_exceptional_sympathetic_art",
        claim="Haskell argues that Ferdinand’s distinctive place in Italian patronage is shown by sober, sympathetic treatment of poor and simple subjects remaining exceptional in Italian art.",
        quote=q["distinctive_patronage"], lines=(342, 343),
        qualification="This is Haskell’s assessment of Ferdinand’s historical significance and of Italian art.",
        mentioned=["cand-1609", "cand-4131", "cand-0871"], relation=False,
        relation_note="An art-historical evaluation, not a specific patronage relation candidate.")
    revise("st-chp8-p239-ferdinand-removal-and-bologna",
        subject="cand-0871", object_="cand-3398", predicate="retired_to_bologna_after_ferdinands_removal_from_scene",
        claim="After Ferdinand’s removal from the scene, Haskell says Crespi retired to Bologna, which he calls a provincial backwater.",
        quote=q["retired_bologna"], lines=(344, 344),
        qualification="The source’s phrase ‘removal from the scene’ is retained without converting it into a more specific event; ‘provincial backwater’ is Haskell’s evaluation.",
        mentioned=["cand-0871", "cand-1609", "cand-3398"], relation=True,
        relation_note="The source explicitly reports Crespi retiring to Bologna; the preceding clause gives Ferdinand’s removal as context.",
        extras={"footnote_marker": 4,
                "footnote_statement_ids": ["st-chp8-p239-longhi-on-restricting-effect"]})
    revise("st-chp8-p239-ferdinand-sensitive-collector",
        subject="cand-1609", object_=None, predicate="most_cultivated_and_sensitive_collector_crespi_had_known",
        claim="Haskell describes Ferdinand as the most cultivated and sensitive collector Crespi had yet—or ever was to—encounter.",
        quote=q["sensitive_collector"], lines=(340, 340),
        qualification="The ranking is Haskell’s characterization through Crespi’s perspective, not an independently established comparison.",
        mentioned=["cand-1609", "cand-0871"], relation=False,
        relation_note="A comparative characterization of Ferdinand, not a formal relation.")
    revise("st-chp8-p239-ferdinand-supported-history-picture-break",
        subject="cand-1609", object_="cand-0871", predicate="supported_crespis_attempt_to_break_from_history_picture",
        claim="Haskell calls Ferdinand’s support fully as important to Crespi’s attempts to break away from the conventional history picture.",
        quote=q["support"], lines=(341, 341),
        qualification="This records Haskell’s assessment of Ferdinand’s support; the phrase does not identify a specific commission or work.",
        mentioned=["cand-1609", "cand-0871", "cand-1612"], relation=True,
        relation_note="The source explicitly says Ferdinand supported Crespi’s attempts to move beyond the conventional history picture.",
        extras={"ocr_corrections": [{"source_line": 341, "ocr": "die support", "print": "the support", "basis": "CHP-8.pdf physical page 45"}]})
    revise("st-chp8-p239-ferdinand-view-as-humourist",
        subject="cand-1609", object_="cand-0871", predicate="letters_suggest_ferdinand_saw_crespi_primarily_as_humourist",
        claim="Haskell says Ferdinand’s recorded opinions, especially his letters, suggest that he saw Crespi primarily as a humourist.",
        quote=q["ferdinand_humourist"], lines=(342, 342),
        qualification="The view is Haskell’s inference from unspecified records and letters; it is not a direct quotation from Ferdinand.",
        mentioned=["cand-1609", "cand-0871", "cand-8056"], relation=True,
        relation_note="The source explicitly attributes this view of Crespi to Ferdinand’s recorded opinions and letters, with Haskell’s evidential qualification.",
        extras={"footnote_marker": 3,
                "footnote_statement_ids": ["st-chp8-p239-note3-zanotti-and-letter-357"]})
    revise("st-chp8-p239-last-known-artist",
        subject="cand-0871", object_="cand-1609", predicate="last_artist_known_to_have_worked_for_ferdinand",
        claim="Haskell identifies Crespi as the last artist whom he knows to have worked for Ferdinand.",
        quote=q["last_artist"], lines=(339, 339),
        qualification="‘Whom we know’ limits the statement to Haskell’s documentary knowledge; it does not assert that Crespi was Ferdinand’s final artist in fact.",
        mentioned=["cand-0871", "cand-1609"], relation=True,
        relation_note="The source explicitly reports a work relationship while qualifying its documentary scope.",
        extras={"ocr_corrections": [{"source_line": 339, "ocr": "him...", "print": "him.", "basis": "CHP-8.pdf physical page 45"}]})
    revise("st-chp8-p239-longhi-on-restricting-effect",
        subject="cand-8058", object_="cand-0871", predicate="longhi_noted_restricting_effect_on_crespis_art",
        claim="Note 4 says R. Longhi pointed out the restricting effect on Crespi’s art in his introduction to the 1948 exhibition catalogue.",
        quote=q["longhi_note"], lines=(348, 348),
        qualification="The note does not establish the full identity of ‘R. Longhi’ or the exact catalogue; both remain for later alignment.",
        mentioned=["cand-8058", "cand-0871", "cand-8022"], relation=False,
        relation_note="This is a bibliographic claim in a note, not a formal relation between Longhi and Crespi.")
    revise("st-chp8-p239-pictures-distributed-among-medici-residences",
        subject="cand-1609", object_="cand-1949", predicate="amassed_pictures_distributed_in_pitti_apartments",
        claim="Haskell says pictures Ferdinand amassed were distributed in his apartments in the Pitti Palace.",
        quote=q["pitti_distribution"], lines=(345, 346),
        qualification="The pictures are an unspecified aggregate; ‘the Pitti’ is resolved to Pitti Palace, but no individual work or group endpoint is identified.",
        mentioned=["cand-1609", "cand-1949"], relation=False,
        relation_note="The statement concerns an unidentified aggregate of pictures and does not support a formal work-to-place edge.")
    revise("st-chp8-p239-restraint-and-ferdinand-appreciation",
        subject="cand-0871", object_="cand-1609", predicate="restraint_suggests_crespi_relied_on_ferdinands_appreciation",
        claim="Haskell infers from Crespi’s restraint that he must have relied on Ferdinand appreciating a side of his temperament ignored by many.",
        quote=q["reliance"], lines=(342, 342),
        qualification="This is Haskell’s inference from the manner of painting, not a statement from Crespi about his own motive.",
        mentioned=["cand-0871", "cand-1609"], relation=True,
        relation_note="The source explicitly infers reliance between the named artist and patron; preserve it as an interpretive relation candidate.",
        extras={"ocr_corrections": [{"source_line": 342, "ocr": "ef his temperament", "print": "of his temperament", "basis": "CHP-8.pdf physical page 45"}]})
    revise("st-chp8-p239-three-hundred-pitti-pictures",
        subject="cand-1609", object_="cand-1949", predicate="pitti_housed_300_pictures_from_ferdinands_private_collection",
        claim="Haskell says the Pitti alone held 300 pictures entirely from Ferdinand’s private collection.",
        quote=q["pitti_300"], lines=(347, 347),
        qualification="The claim is attributed to Haskell and his cited inventory; the exact inventory count and scope remain tied to note 5.",
        mentioned=["cand-1609", "cand-1949"], relation=False,
        relation_note="The 300 works are not individually identified as a work-group endpoint; retain the count as a source claim.",
        extras={"footnote_marker": 5,
                "footnote_statement_ids": ["st-chp8-p239-note5-inventory-description", "st-chp8-p239-note5-spf-mark"]})
    revise("st-chp8-p239-venetian-emphasis",
        subject="cand-8055", object_="cand-1609", predicate="venetian_picture_group_in_ferdinands_collection",
        claim="Haskell says the Venetian pictures in Ferdinand’s amassed collection were strongly emphasized.",
        quote=q["venetian_emphasis"], lines=(347, 347),
        qualification="The scope of the Venetian group is not limited to the 300 pictures in the Pitti; the sentence continues with examples on p.240.",
        mentioned=["cand-1609", "cand-8055"], relation=True,
        relation_note="The source explicitly identifies this work-group as a strong component of Ferdinand’s amassed pictures; individual paintings are not inferred.",
        extras={"continuation_closed_by_segment_id": NEXT_SEGMENT,
                "continuation_closed_by_line": 351})

    rows.extend([
        new_statement("st-chp8-p239-ferdinand-great-days-patronage-over",
            subject="cand-1609", object_=None, predicate="great_days_of_ferdinands_patronage_were_over",
            claim="Haskell says Ferdinand’s great days of patronage were over.", quote=q["patronage_over"], lines=(339, 339),
            qualification="This clause continues the p.238 sentence about Ferdinand’s final illness; note 1 concerns Crespi’s Florentine visits and is retained at the printed marker.",
            mentioned=["cand-1609", "cand-0871"], relation=False,
            relation_note="An authorial assessment of a historical period, not a distinct formal relation.",
            extras={"continuation_from_segment_id": "chp-8:08_CHP-8_sec_ii:l327-336",
                    "footnote_marker": 1,
                    "footnote_statement_ids": ["st-chp8-p239-note1-luigi-crespi-stay", "st-chp8-p239-note1-haskell-eight-month-maximum", "st-chp8-p239-note1-zanotti-multiple-visits"]}),
        new_statement("st-chp8-p239-crespi-took-advantage-of-gallery",
            subject="cand-0871", object_=None, predicate="haskell_says_crespi_took_full_advantage_of_ferdinands_gallery",
            claim="Haskell says Crespi took full advantage of the opportunity to study paintings in Ferdinand’s gallery, citing a letter about a picture attributed to Tintoretto.", quote=q["took_advantage"], lines=(341, 341),
            qualification="This is Haskell’s inference from the letter; the letter itself is unidentified and the pictured work is separately recorded.",
            mentioned=["cand-0871", "cand-1609", "cand-8050", "cand-8049"], relation=False,
            relation_note="An authorial interpretation of an artist’s use of a collection, not a separate formal relation."),
        new_statement("st-chp8-p239-new-ventures-loss-prestige",
            subject="cand-0871", object_=None, predicate="new_ventures_risked_loss_of_prestige_and_derision",
            claim="Haskell says Crespi’s new artistic ventures were bound to bring some loss of prestige and derision.", quote=q["ventures"], lines=(341, 341),
            qualification="This is Haskell’s general assessment of the reception risk, not a claim that a particular event occurred.",
            mentioned=["cand-0871", "cand-1612"], relation=False,
            relation_note="A general interpretive statement with no specific relation endpoint."),
        new_statement("st-chp8-p239-genre-scenes-expected-humorous",
            subject="cand-0871", object_=None, predicate="viewers_expected_genre_scenes_to_be_humorous",
            claim="Haskell says viewers expected genre scenes to be humorous and therefore laughed at them.", quote=q["genre_expectation"], lines=(341, 341),
            qualification="The claim describes a generalized response, not named viewers or a specific work.",
            mentioned=["cand-0871"], relation=False,
            relation_note="General reception claim without an identified person or work endpoint."),
        new_statement("st-chp8-p239-crespi-poetic-sympathy",
            subject="cand-0871", object_=None, predicate="painted_people_with_deep_poetic_sympathy",
            claim="Haskell says Crespi’s humour was counteracted by deep poetic sympathy for the people he painted.", quote=q["sympathy"], lines=(341, 341),
            qualification="This is Haskell’s interpretation of Crespi’s artistic temperament and subject matter.",
            mentioned=["cand-0871"], relation=False,
            relation_note="An artistic characterization, not a formal relationship."),
        new_statement("st-chp8-p239-ferdinand-shared-misconceptions-uncertain",
            subject="cand-1609", object_="cand-0871", predicate="haskell_uncertain_how_far_ferdinand_shared_misconceptions",
            claim="Haskell says it is difficult to determine how much Ferdinand shared common misconceptions about Crespi’s art.", quote=q["ferdinand_uncertain"], lines=(341, 341),
            qualification="This is an explicit statement of uncertainty; the subsequent letter-based view is recorded separately.",
            mentioned=["cand-1609", "cand-0871"], relation=False,
            relation_note="The source foregrounds uncertainty rather than asserting a confirmed relation or belief."),
        new_statement("st-chp8-p239-crespi-restraint-bawdy-subjects",
            subject="cand-0871", object_=None, predicate="painted_with_restraint_on_subjects_open_to_bawdy_treatment",
            claim="Haskell says Crespi used great restraint when painting subjects open to gross or bawdy treatment.", quote=q["restraint"], lines=(342, 342),
            qualification="Plate 36b is cited as an example; the work is not identified here as a separate candidate.",
            mentioned=["cand-0871"], relation=False,
            relation_note="A characterization of artistic treatment, not a formal relation."),
        new_statement("st-chp8-p239-ferdinand-modern-prince",
            subject="cand-1609", object_="cand-3461", predicate="haskell_called_ferdinand_most_modern_prince_of_age_in_italy",
            claim="Haskell calls Ferdinand the most modern prince of his age in Italy.", quote=q["modern_prince"], lines=(344, 344),
            qualification="‘Most modern’ is Haskell’s evaluative characterization, not a standardized political status.",
            mentioned=["cand-1609", "cand-3461"], relation=False,
            relation_note="An authorial characterization, not a formal relation."),
        new_statement("st-chp8-p239-only-princes-influential-patrons",
            subject="cand-1609", object_=None, predicate="haskell_says_only_princes_could_be_influential_patrons",
            claim="Haskell says that at the time only princes could be influential patrons.", quote=q["only_princes"], lines=(344, 344),
            qualification="This is Haskell’s broad historical generalization in the sentence explaining the counterfactual middle-class backing.",
            mentioned=["cand-1609", "cand-0871"], relation=False,
            relation_note="A broad historical generalization, not a specific relationship."),
        new_statement("st-chp8-p239-pictures-distributed-in-country-houses",
            subject="cand-1609", object_=None, predicate="amassed_pictures_also_distributed_among_country_houses",
            claim="Haskell says Ferdinand’s amassed pictures were also distributed among the country houses through which he moved during the year.", quote=q["country_houses"], lines=(346, 346),
            qualification="The country houses are not individually identified; no additional place candidates are created.",
            mentioned=["cand-1609"], relation=False,
            relation_note="The locations and picture group are unspecified, so this remains a source claim rather than a formal edge."),
        new_statement("st-chp8-p239-pictures-number-considerable",
            subject="cand-1609", object_=None, predicate="picture_collection_numbers_very_considerable_by_end_of_life",
            claim="Haskell says the number of pictures Ferdinand amassed was very considerable by the end of his life.", quote=q["numbers"], lines=(347, 347),
            qualification="This is a qualitative count claim; no numeric total beyond the Pitti figure is inferred.",
            mentioned=["cand-1609"], relation=False,
            relation_note="A quantitative characterization without an independent work-group endpoint."),
        new_statement("st-chp8-p239-earlier-family-pictures-included",
            subject="cand-5179", object_=None, predicate="earlier_medici_family_members_assembled_many_pictures",
            claim="Haskell distinguishes many pictures assembled by earlier members of the Medici family from Ferdinand’s private collection.", quote=q["earlier_family"], lines=(347, 347),
            qualification="The earlier family members are not individually identified; note 5 documents the inventory and S.P.F. marking.",
            mentioned=["cand-5179", "cand-1609", "cand-1949"], relation=False,
            relation_note="An aggregate collection statement; no named historical owner or work endpoint is identified.",
            extras={"footnote_marker": 5,
                    "footnote_statement_ids": ["st-chp8-p239-note5-inventory-description", "st-chp8-p239-note5-spf-mark"]}),
    ])

    if {row["statement_id"] for row in rows} & NEW_IDS != NEW_IDS:
        raise SystemExit("not all planned p.239 statements were created")
    current = [row for row in rows if row.get("segment_id") == SEGMENT]
    if len(current) != len(EXPECTED_EXISTING) + len(NEW_IDS):
        raise SystemExit(f"unexpected p.239 post-edit row count: {len(current)} expected {len(EXPECTED_EXISTING) + len(NEW_IDS)}")
    flags = {str(row.get("qualifiers", {}).get("relation_candidate")): 0 for row in current}
    for row in current:
        key = str(row.get("qualifiers", {}).get("relation_candidate"))
        flags[key] = flags.get(key, 0) + 1
    if flags.get("None", 0):
        raise SystemExit(f"p.239 still has unset relation_candidate rows: {flags}")
    preview = {
        "mode": "dry-run", "p239_existing": len(existing), "p239_added": len(NEW_IDS),
        "p239_statement_total": len(current), "statement_total": len(rows),
        "p239_relation_candidate_flags": flags,
        "p239_ocr_corrections": [
            "p.239 L339 him... -> him.", "p.239 L341 Crcspi -> Crespi",
            "p.239 L341 die support -> the support", "p.239 L342 ef his temperament -> of his temperament",
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
