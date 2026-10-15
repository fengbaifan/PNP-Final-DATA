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
PAGE_IMAGE = PROCESS / "p129_page_review_20261012.png"
P129_SEGMENT = "chp-5:05_CHP-5_sec_i:l99-106"
P128_SEGMENT = "chp-5:05_CHP-5_sec_i:l85-97"
EXPECTED = {
    "book-statements.jsonl": "4076c417cd3429dfebb087d9ef414fd9b8f8a3af904549f2a94595054ff8905b",
    "entity-candidates.csv": "93e29fc48ff4de524a7649eb6029a6bc0bef7be751b2d2b5d9be86a52403e6f6",
    "mentions.csv": "d8858ebe1c83e0cfd6138ff404d435f28a7d104018010c1e109bb35fde78d066",
}
SOURCE_SHA = "8ef51cd646ed6abf398c9faeb47df9a03f70de696d9a871c6d0b734b2adeeeee"
PDF_SHA = "f63dca79808fde73ba10aa9414fef89bc8ca5e77ed829b2d5c86f23719e0674a"
IMAGE_SHA = "75ef06ee23d1ce99286fb2b47fefa81cea96bb817811fb507fcba2cf95c2834e"
P129_SEGMENT_SHA = "1096a4da306376fcd90adfdebcee1c52752b8c72cf0792ebef1a1b6fe005018f"
P128_SEGMENT_SHA = "9c8360e14542de083d5e2414f7fdbf81b4f52f087f158d9d62239bcc023278d7"
SOURCE_FILE = "02-sources/02-Markdown/05_CHP-5_sec_i.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
p129_text = "\n".join(source_lines[98:106])
p128_text = "\n".join(source_lines[84:97])


def exact(text: str, needle: str, expected_start: int | None = None) -> str:
    at = text.find(needle)
    need(at >= 0, f"source quote not found: {needle!r}")
    if expected_start is not None:
        need(at == expected_start, f"source quote moved: {needle!r}: {at} != {expected_start}")
    return needle


def candidate(cid: str, name: str, kind: str, line: int, detail: str, segment: str = P129_SEGMENT) -> dict:
    return {
        "candidate_id": cid,
        "index_entry_id": "",
        "canonical_name": name,
        "index_page_range": "",
        "suggested_type": kind,
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": detail,
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{segment}#L{line}",
    }


NEW_CANDIDATES = [
    candidate("cand-11781", "Marchese Ruspoli's 194 pictures (unnamed group)", "work", 100,
              "The source says Ruspoli initially insisted that only these 194 pictures be exhibited; no titles or makers are identified."),
    candidate("cand-11782", "Monsignor Olivieri's 23 pictures permitted at the 1708 exhibition (unnamed group)", "work", 100,
              "The source says Olivieri was allowed to hang 23 of his pictures; permission is stated, but actual display is not independently confirmed."),
    candidate("cand-11783", "1708 exhibition episode involving Marchese Ruspoli (unnamed event)", "event", 97,
              "Introduced as a similar situation immediately after the 1697 S. Salvatore exhibition account. The p.129 continuation does not restate venue or series; keep the contextual association open." , P128_SEGMENT),
    candidate("cand-11784", "Twenty-three Venetian-style history pictures sent by Cardinal Grimani in 1707 (unnamed group)", "work", 101,
              "The source calls these historié di maniera veneziana and attributes them to Antonio Molinari; individual titles are not given."),
    candidate("cand-11785", "Pictures by Francesco Trevisani shown by Cardinal Pietro Ottoboni (unnamed group)", "work", 101,
              "Unnamed pictures by Trevisani shown by Ottoboni; the source supplies no titles or individual work identities."),
    candidate("cand-11786", "Widow of King John of Poland (unnamed woman)", "person", 103,
              "The passage calls her only 'his widow'; it does not name her. Do not infer an identity from outside this source."),
    candidate("cand-11787", "Portraits and battle pictures proposed for loan in 1704 (unnamed group)", "work", 103,
              "A series of portraits and battle pictures the Pope encouraged King John's widow to lend for publicity; the source does not say the loan or exhibition occurred."),
    candidate("cand-11788", "Foreign rulers and patrons seeking artists from their own countries (unnamed group)", "term", 105,
              "The source describes collective ambitions of foreign rulers and patrons; no members or country list is supplied."),
    candidate("cand-11789", "Artists from foreign rulers' countries sought to record Rome (unnamed group)", "term", 105,
              "Artists whom the rulers and patrons wanted to use to record Rome and reproduce Italian painting; individuals are not named and this group is not equated with settled Roman colonies."),
    candidate("cand-11790", "Pictures, tapestries, and banners used decoratively at Roman exhibitions (unnamed group)", "work", 104,
              "The source describes media used decoratively across the exhibitions under discussion; no individual objects are identified."),
    candidate("cand-11791", "Art of alien cultures introduced into Rome through exhibitions (unnamed cultural category)", "term", 105,
              "Haskell's broad category for cultural art introduced into Rome; the source identifies no individual works or bounded culture."),
    candidate("cand-11792", "Roman collectors in the 1707 example (unnamed group)", "term", 101,
              "Unnamed collectors whom Haskell says remained unfamiliar with Antonio Molinari; no membership or private/public boundary is supplied."),
    candidate("cand-11793", "Victories won by King John of Poland in the 1704 publicity reference (unnamed event group)", "event", 102,
              "The passage attributes victories to King John but does not name campaigns, battles, dates, or their number."),
    candidate("cand-11794", "Four regular annual exhibitions in Rome by the end of the seventeenth century (unnamed group)", "event", 104,
              "The source counts four regular annual exhibition occasions in Rome and names their months, but does not identify the four series individually."),
]


REL_TRUE = "Source-grounded S2 relation candidate only; no S6 formal edge is created."
REL_FALSE = "Retained as a source claim, but not a candidate for a formal entity relation."


def qualifiers(line_start: int, line_end: int, claim: str, qualification: str,
               mentioned: list[str], relation: bool, **extra) -> dict:
    q = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "authorial narrative",
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "pdf_physical_page": 10,
        "printed_page_locator": "p.129",
        "relation_candidate": relation,
        "relation_candidate_note": REL_TRUE if relation else REL_FALSE,
    }
    q.update(extra)
    return q


def update(statement_id: str, subject: str | None, obj: str | None, predicate: str,
           quote: str, q: dict) -> dict:
    return {
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "original_quote": quote,
        "qualifiers": q,
    }


updates = {
    "st-chp5-p129-1708-ruspoli-condition-and-concession": update(
        "st-chp5-p129-1708-ruspoli-condition-and-concession", "cand-2311", "cand-11781",
        "initially_demanded_exclusive_display_of_picture_group",
        exact(p129_text, "insisted that only his 194 pictures should be exhibited"),
        qualifiers(100, 100,
                   "In the 1708 episode, Ruspoli initially insisted that only his 194 pictures be exhibited.",
                   "This is the initial condition, not evidence that all 194 pictures were actually shown. The episode is contextually adjacent to the S. Salvatore series but its venue is not restated here.",
                   ["cand-2311", "cand-11781", "cand-11783"], True,
                   event_candidate_id="cand-11783", reported_count=194)),
    "st-chp5-p129-artists_more_visible_open": update(
        "st-chp5-p129-artists_more_visible_open", None, None, "artists_more_visible_in_public_spaces",
        exact(p129_text, "The artists themselves were more visible than they had been: sketching in the ruins or among the great modern buildings that sprang up everywhere and sketching each other so doing; making rapid impressions"),
        qualifiers(106, 106,
                   "Haskell says artists had become more visible through sketching in ruins and modern buildings, sketching one another, and making rapid impressions.",
                   "The sentence continues in p.130 L109 and is completed there by st-chp5-p130-artist-impressions-closure; do not duplicate the continuation as a second independent claim.",
                   [], False, continuation_segment_id="chp-5:05_CHP-5_sec_i:l108-113",
                   continuation_completed_by_statement_id="st-chp5-p130-artist-impressions-closure")),
    "st-chp5-p129-current_painting_access": update(
        "st-chp5-p129-current_painting_access", None, None, "some_exhibitions_enabled_access_to_current_painting",
        exact(p129_text, "Sometimes, however, they provided an opportunity for the public to see current painting of a kind that would not normally be easily accessible."),
        qualifiers(101, 101,
                   "Sometimes exhibitions let the public see current painting that was not normally easily accessible.",
                   "The source explicitly limits this to some occasions with 'Sometimes'; it is a generalized contextual claim rather than a relation between identified entities.",
                   ["cand-0130"], False)),
    "st-chp5-p129-dealers_and_travellers": update(
        "st-chp5-p129-dealers_and_travellers", "cand-4490", "cand-3562", "became_more_accessible_to_travellers",
        exact(p129_text, "Rome became more easily accessible to travellers of all kinds, including Protestants"),
        qualifiers(105, 105,
                   "Rome became more accessible to travellers of all kinds, including Protestants.",
                   "Haskell presents accessibility as context for the increasing prevalence of art dealers; this row isolates the place-to-audience claim.",
                   ["cand-4490", "cand-3562"], True)),
    "st-chp5-p129-decorative_use": update(
        "st-chp5-p129-decorative_use", "cand-0130", "cand-11790", "used_pictures_textiles_and_banners_for_decoration",
        exact(p129_text, "Essentially all of them made use of pictures, as of tapestries and banners, for decorative purposes."),
        qualifiers(104, 104,
                   "The exhibitions under discussion used pictures, tapestries, and banners for decoration.",
                   "'All of them' refers to the exhibition practices discussed in the surrounding account; the individual objects and each exhibition instance are not identified.",
                   ["cand-0130", "cand-11790"], True)),
    "st-chp5-p129-exhibitions_introduced_alien_cultures": update(
        "st-chp5-p129-exhibitions_introduced_alien_cultures", "cand-0130", "cand-11791",
        "contributed_to_introducing_alien_cultural_art_into_rome",
        exact(p129_text, "exhibitions were among a number of factors that introduced into Rome the art of alien cultures"),
        qualifiers(105, 105,
                   "Haskell treats exhibitions as one among several factors that introduced art of alien cultures into Rome.",
                   "The source says exhibitions were among several factors, and that the introduced art often had little organic relationship to conditions in the city; it does not identify specific works or cultures.",
                   ["cand-0130", "cand-11791", "cand-4490"], True,
                   causal_scope="contributing_factor_not_sole_cause")),
    "st-chp5-p129-foreign_patron_ambitions": update(
        "st-chp5-p129-foreign_patron_ambitions", "cand-11788", "cand-11789",
        "wanted_home_country_artists_to_record_rome_and_reproduce_italian_painting",
        exact(p129_text, "foreign rulers and patrons who wanted artists from their own countries to record the glories of Rome and reproduce for them the triumphs of Italian painting"),
        qualifiers(105, 105,
                   "Foreign rulers and patrons wanted artists from their own countries to record Rome's glories and reproduce the triumphs of Italian painting.",
                   "This records the source's stated ambitions, not proof that particular artists were commissioned or that the works were produced.",
                   ["cand-11788", "cand-11789", "cand-4490", "cand-11017"], True,
                   intention_only=True)),
    "st-chp5-p129-four_annual_exhibitions": update(
        "st-chp5-p129-four_annual_exhibitions", "cand-11794", "cand-4490",
        "held_each_year_in_rome",
        exact(p129_text, "by the end of the century there were four regular exhibitions in Rome each year"),
        qualifiers(104, 104,
                   "By the end of the seventeenth century, Rome had four regular exhibition occasions each year, in March, July, August, and December.",
                   "The source gives a count and months but does not name or individually identify the four recurring series.",
                   ["cand-0130", "cand-11794", "cand-4490"], True,
                   annual_months=["March", "July", "August", "December"], reported_count=4,
                   temporal_scope="by_the_end_of_the_seventeenth_century")),
    "st-chp5-p129-grimani_molinari": update(
        "st-chp5-p129-grimani_molinari", "cand-1233", "cand-11784", "sent_23_history_pictures_into_exhibition",
        exact(p129_text, "in 1707 Cardinal Grimani, in a sit of patriotic enthusiasm, sent in 23 \u2018histori\u00e9 di maniera veneziana\u2019 by Antonio Molinari"),
        qualifiers(101, 101,
                   "In 1707 Cardinal Grimani sent in 23 Venetian-style history pictures by Antonio Molinari.",
                   "The exhibition occasion is not named. The scan reads 'fit' where the OCR has 'sit'; preserve the OCR source and record the correction here. The works' authorship is split into a separate statement.",
                   ["cand-1233", "cand-11784", "cand-1679"], True,
                   printed_reading_correction={"ocr": "sit", "print": "fit"}, reported_count=23)),
    "st-chp5-p129-informal_shows_fruitful": update(
        "st-chp5-p129-informal_shows_fruitful", None, None, "informal_showings_assessed_as_more_artistically_fruitful",
        exact(p129_text, "From the strictly artistic point of view it is probable therefore that the more informal showings were the most fruitful"),
        qualifiers(104, 104,
                   "From the strictly artistic point of view, Haskell considers informal showings probably the most fruitful.",
                   "Keep both the standpoint ('strictly artistic') and uncertainty ('probable'); this is Haskell's comparative assessment.",
                   ["cand-0130"], False)),
    "st-chp5-p129-national_artist_colonies": update(
        "st-chp5-p129-national_artist_colonies", "cand-3467", "cand-4490", "settled_in_rome_as_national_artist_colonies",
        exact(p129_text, "the consequent settling in Rome of different national colonies of artists"),
        qualifiers(105, 105,
                   "Different national colonies of artists settled in Rome.",
                   "The passage names no colonies or members. This source mention is linked provisionally to the existing broad foreign-artists candidate; membership and identity alignment remain open for S3.",
                   ["cand-3467", "cand-4490"], True,
                   group_identity_status="candidate_mapping_not_member_identification")),
    "st-chp5-p129-occasional_exhibitions": update(
        "st-chp5-p129-occasional_exhibitions", None, None, "many_occasional_exhibitions_accompanied_regular_schedule",
        exact(p129_text, "quite apart from a large number of occasional ones arranged for special events and casual affairs spontaneously organised by a particular patron or artist"),
        qualifiers(104, 104,
                   "Many additional occasional exhibitions were arranged for special events or spontaneously by a patron or artist.",
                   "The source gives no list or number of these occasions; 'a large number' and spontaneous organization are retained as reported.",
                   ["cand-0130"], False)),
    "st-chp5-p129-old_masters_repeated": update(
        "st-chp5-p129-old_masters_repeated", None, None, "old_masters_more_prominent_and_pictures_repeated",
        exact(p129_text, "In all these exhibitions old masters were given far greater prominence than contemporary work and many pictures were repeatedly shown year after year."),
        qualifiers(101, 101,
                   "Across the exhibitions discussed, old masters received greater prominence than contemporary work, and many pictures were shown repeatedly in successive years.",
                   "'All these exhibitions' refers back across the preceding examples; neither individual exhibitions nor the pictures are enumerated here.",
                   ["cand-0130", "cand-4288"], False)),
    "st-chp5-p129-ottoboni_trevisani": update(
        "st-chp5-p129-ottoboni_trevisani", "cand-1795", "cand-2650", "assiduously_employed_artist",
        exact(p129_text, "whom he assiduously employed"),
        qualifiers(101, 101,
                   "Cardinal Pietro Ottoboni assiduously employed Francesco Trevisani.",
                   "The pronoun 'he' refers to Ottoboni. The separate exhibition of pictures by Trevisani is recorded independently.",
                   ["cand-1795", "cand-2650"], True,
                   employment_frequency="assiduously")),
    "st-chp5-p129-painting_public_business": update(
        "st-chp5-p129-painting_public_business", None, None, "exhibitions_helped_make_painting_more_public",
        exact(p129_text, "Still more significant, exhibitions helped to make painting a far more \u2018public\u2019 business than it had ever been before."),
        qualifiers(106, 106,
                   "Haskell argues that exhibitions helped make painting a much more public business than before.",
                   "This is the author's comparative interpretation, not a relation between identified entities.",
                   ["cand-0130"], False)),
    "st-chp5-p129-patronage_little_affected": update(
        "st-chp5-p129-patronage_little_affected", None, None, "regular_patronage_little_affected_by_exhibitions",
        exact(p129_text, "the importance of regular patronage, and the need to exhibit work on a permanent basis by painting altarpieces in the more frequented churches, were comparatively little affected by seventeenth-century exhibitions"),
        qualifiers(104, 104,
                   "Haskell says the importance of regular patronage and permanent altarpieces in frequented churches was comparatively little affected by seventeenth-century exhibitions.",
                   "Preserve the comparative limitation ('comparatively little'); the sentence contrasts exhibition practices with more permanent church patronage.",
                   ["cand-0130"], False)),
    "st-chp5-p129-pope_polish_victories": update(
        "st-chp5-p129-pope_polish_victories", "cand-0022", "cand-11793", "sought_publicity_for_victory_group",
        exact(p129_text, "In 1704, for instance, the Pope wished to make better known the victories won by\nKing John of Poland"),
        qualifiers(102, 103,
                   "In 1704 the Pope wished to make the victories won by King John of Poland better known.",
                   "The passage does not name the Pope; the p.129 index lead points to candidate cand-0022 (Pope Clement XI), but identity is not treated as resolved until S3.",
                   ["cand-0022", "cand-1332", "cand-11793"], True,
                   pope_identity_status="index_lead_only_not_named_in_passage", king_candidate_id="cand-1332",
                   year=1704)),
    "st-chp5-p129-propagandist_use": update(
        "st-chp5-p129-propagandist_use", None, None, "some_exhibitions_used_for_propagandist_purposes",
        exact(p129_text, "At other times the exhibition was used for more directly propagandist purposes."),
        qualifiers(101, 101,
                   "Haskell says some exhibitions served more directly propagandist purposes.",
                   "This is a general characterization; the 1704 example is retained separately with the source's stated purpose and intended loan.",
                   ["cand-0130"], False)),
    "st-chp5-p129-public_picture_access_and_circulation": update(
        "st-chp5-p129-public_picture_access_and_circulation", None, None, "pictures_became_accessible_beyond_altar_and_family_palace",
        exact(p129_text, "Pictures were readily available and within the reach of everybody: no longer confined to the altar or to the family palace"),
        qualifiers(106, 106,
                   "Pictures became readily available to a broad public and were no longer confined to altars or family palaces.",
                   "This is the opening claim of a broader account of public display and circulation, which is split into separate statements below.",
                   ["cand-0130"], False)),
    "st-chp5-p129-regular_shows_not_new_work": update(
        "st-chp5-p129-regular_shows_not_new_work", None, None, "regular_exhibitions_not_primarily_for_new_work",
        exact(p129_text, "none of the regular exhibitions had as its primary.aim the opportunity for a painter to show new work, and some deliberately excluded this"),
        qualifiers(104, 104,
                   "None of the regular exhibitions primarily aimed to let painters show new work, and some deliberately excluded it.",
                   "The scan reads 'primary aim'; OCR inserts a dot before 'aim'. No footnote marker is visible at this position. Preserve the OCR source.",
                   ["cand-0130"], False,
                   printed_reading_correction={"ocr": "primary.aim", "print": "primary aim"})),
}


def new_statement(statement_id: str, subject: str | None, obj: str | None, predicate: str,
                  line_start: int, line_end: int, quote: str, claim: str,
                  qualification: str, mentioned: list[str], relation: bool, **extra) -> dict:
    return {
        "statement_id": statement_id,
        "segment_id": P129_SEGMENT,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers(line_start, line_end, claim, qualification, mentioned, relation, **extra),
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_FILE,
    }


NEW_STATEMENTS = [
    new_statement("st-chp5-p129-1708-ghezzi-suggestion", "cand-1157", "cand-1778",
                  "suggested_permitting_olivieri_to_hang_his_pictures", 100, 100,
                  exact(p129_text, "Ghezzi\u2019s tactful suggestion that Monsignor Olivieri be allowed to hang 23 of his"),
                  "Ghezzi tactfully suggested that Olivieri be allowed to hang 23 of his pictures in the 1708 exhibition episode.",
                  "The 23-picture group is represented by cand-11782. The sentence states permission, not independently verified display.",
                  ["cand-1157", "cand-1778", "cand-11782", "cand-11783"], True,
                  event_candidate_id="cand-11783", work_group_candidate_id="cand-11782", tone="tactful"),
    new_statement("st-chp5-p129-1708-ruspoli-agreement", "cand-2311", "cand-1778",
                  "agreed_to_allow_olivieri_to_hang_pictures", 100, 100,
                  exact(p129_text, "finally agreed to Ghezzi\u2019s tactful suggestion that Monsignor Olivieri be allowed to hang 23 of his"),
                  "Ruspoli finally agreed to Ghezzi's suggestion that Olivieri be allowed to hang 23 pictures.",
                  "The statement records agreement to a proposed permission; it does not assert that the pictures were actually hung.",
                  ["cand-2311", "cand-1157", "cand-1778", "cand-11782", "cand-11783"], True,
                  event_candidate_id="cand-11783", work_group_candidate_id="cand-11782"),
    new_statement("st-chp5-p129-1708-olivieri-permitted-display", "cand-1778", "cand-11782",
                  "was_allowed_to_hang_picture_group", 100, 100,
                  exact(p129_text, "Monsignor Olivieri be allowed to hang 23 of his"),
                  "Olivieri was allowed to hang a group of 23 of his pictures.",
                  "Permission is explicit; actual hanging is not separately confirmed. The exhibition episode is identified contextually from p.128 L97.",
                  ["cand-1778", "cand-11782", "cand-11783"], True,
                  event_candidate_id="cand-11783", actual_display="not_established"),
    new_statement("st-chp5-p129-molinari-authorship", "cand-1679", "cand-11784", "author_of_picture_group",
                  101, 101, exact(p129_text, "23 \u2018histori\u00e9 di maniera veneziana\u2019 by Antonio Molinari"),
                  "The 23 Venetian-style history pictures sent by Grimani are attributed to Antonio Molinari.",
                  "The source identifies the artist but supplies no individual titles.",
                  ["cand-1679", "cand-11784"], True, reported_count=23),
    new_statement("st-chp5-p129-molinari-death-relative", "cand-1679", None, "reported_dead_25_years_before_1707",
                  101, 101, exact(p129_text, "although he had died 25 years earlier"),
                  "Haskell says Molinari had died 25 years before the 1707 exhibition account.",
                  "Retain the source-relative interval; do not convert it to an exact death date by arithmetic.",
                  ["cand-1679"], False, temporal_reference_year=1707),
    new_statement("st-chp5-p129-molinari-reception", "cand-1679", "cand-11792", "remained_unknown_to_collectors",
                  101, 101, exact(p129_text, "was still quite unknown to Roman collectors"),
                  "Molinari was still quite unknown to Roman collectors at the time described.",
                  "This is Haskell's source-reported assessment of reception; the unnamed collector group has no specified membership.",
                  ["cand-1679", "cand-11792"], True, temporal_reference_year=1707),
    new_statement("st-chp5-p129-king-john-victory-group", "cand-1332", "cand-11793", "won_victory_group",
                  102, 103, exact(p129_text, "victories won by\nKing John of Poland"),
                  "The source attributes the unnamed victories to King John of Poland.",
                  "No campaigns, individual battles, exact count, or dates are supplied; the separate Pope statement records the wish to publicize these victories.",
                  ["cand-1332", "cand-11793"], True, year_context=1704),
    new_statement("st-chp5-p129-ottoboni-showed-trevisani-pictures", "cand-1795", "cand-11785",
                  "showed_picture_group_by_trevisani", 101, 101,
                  exact(p129_text, "Cardinal Ottoboni showed pictures by Trevisani"),
                  "Cardinal Pietro Ottoboni showed a group of pictures by Trevisani.",
                  "The source gives no titles; Trevisani's authorship is linked in a separate statement.",
                  ["cand-1795", "cand-2650", "cand-11785"], True),
    new_statement("st-chp5-p129-trevisani-authorship", "cand-2650", "cand-11785", "author_of_picture_group",
                  101, 101, exact(p129_text, "pictures by Trevisani"),
                  "The pictures shown by Ottoboni were by Francesco Trevisani.",
                  "The individual pictures are not identified.",
                  ["cand-2650", "cand-11785"], True),
    new_statement("st-chp5-p129-john-sobieski-widow", "cand-11786", "cand-1332", "widow_of",
                  103, 103, exact(p129_text, "his widow"),
                  "The woman described as the Pope's intended lender was the widow of King John of Poland.",
                  "The passage does not name her; no personal identity is inferred.",
                  ["cand-11786", "cand-1332"], True),
    new_statement("st-chp5-p129-widow-picture-loan-encouragement", "cand-11786", "cand-11787",
                  "was_encouraged_to_lend_picture_group_for_publicity", 103, 103,
                  exact(p129_text, "encouraged his widow to lend a series of portraits and battle pictures for this purpose"),
                  "The Pope encouraged King John's widow to lend portraits and battle pictures to publicize the victories.",
                  "The source reports encouragement to lend, not a completed loan, display, or named exhibition.",
                  ["cand-0022", "cand-11786", "cand-11787", "cand-1332"], True,
                  encourager_candidate_id="cand-0022", intended_purpose="publicize_King_Johns_victories",
                  actual_loan="not_reported", pope_identity_status="index_lead_only_not_named_in_passage"),
    new_statement("st-chp5-p129-dealers-increased-presence", "cand-0125", "cand-4490",
                  "increasing_prevalence_in_rome_alongside_greater_accessibility", 105, 105,
                  exact(p129_text, "the increasing prevalence of dealers as Rome became more easily accessible"),
                  "Haskell reports an increasing prevalence of art dealers in Rome as the city became more accessible.",
                  "This isolates the art-dealer trend from the adjacent claim about travellers' access; the source gives no individual dealer names or count.",
                  ["cand-0125", "cand-4490", "cand-3562"], True),
    new_statement("st-chp5-p129-public-display-practices", None, None, "pictures_displayed_in_public_church_and_cloister_spaces",
                  106, 106,
                  exact(p129_text, "they now hung outside the church on ceremonial occasions, were propped up against the walls of cloisters on specified days of the year"),
                  "Pictures were hung outside churches during ceremonial occasions and placed against cloister walls on specified days.",
                  "The source gives general practices without identifying particular pictures, churches, or cloisters.",
                  ["cand-0130"], False),
    new_statement("st-chp5-p129-public-picture-market-and-criticism", None, None,
                  "pictures_bought_sold_exchanged_and_publicly_discussed", 106, 106,
                  exact(p129_text, "were bought, sold, exchanged, criticised, argued about"),
                  "Pictures were bought, sold, exchanged, criticized, and debated.",
                  "This is Haskell's broad account of public circulation; the passage names no individual transaction, picture, or critic.",
                  ["cand-0130"], False),
]


MENTION_SPECS = [
    ("m-chp5-p129-0016", "cand-11781", "194 pictures", 34, "Count-bearing mention of Ruspoli's unnamed picture group."),
    ("m-chp5-p129-0017", "cand-11782", "23 of his", 160, "The possessive refers to Olivieri; the source says he was allowed to hang these pictures."),
    ("m-chp5-p129-0018", "cand-11784", "23 \u2018histori\u00e9 di maniera veneziana\u2019", 620, "Count-bearing unnamed work group; authorship by Molinari is separately stated."),
    ("m-chp5-p129-0020", "cand-0022", "the Pope", 867, "The passage leaves the Pope unnamed; the index candidate is a lead only."),
    ("m-chp5-p129-0021", "cand-11786", "his widow", 960, "Anaphoric to King John of Poland; the woman is not named."),
    ("m-chp5-p129-0022", "cand-11787", "a series of portraits and battle pictures", 978, "Unidentified picture group proposed for a loan; the source does not report that the loan occurred."),
    ("m-chp5-p129-0023", "cand-11794", "four regular exhibitions in Rome", 1080, "The source gives four recurring annual occasions but names none of them individually."),
    ("m-chp5-p129-0024", "cand-0125", "dealers", 2159, "General art-dealer category in the discussion of Rome's accessibility."),
    ("m-chp5-p129-0025", "cand-3562", "travellers of all kinds, including Protestants", 2208, "Collective traveller category; no individuals are named."),
    ("m-chp5-p129-0026", "cand-11788", "foreign rulers and patrons", 2273, "Unnamed collective group expressing ambitions for artists from their countries."),
    ("m-chp5-p129-0027", "cand-11789", "artists from their own countries", 2311, "Unidentified artists sought by the foreign rulers and patrons."),
    ("m-chp5-p129-0028", "cand-3467", "different national colonies of artists", 2466, "Collective foreign-artist category; no colony members are named, and exact overlap with other artist groups is unresolved."),
    ("m-chp5-p129-0029", "cand-11790", "pictures, as of tapestries and banners", 1495, "The source's full phrase for unnamed media used decoratively; no individual objects are identified."),
    ("m-chp5-p129-0030", "cand-11791", "the art of alien cultures", 2728, "Broad source-defined cultural-art category, not individual works."),
    ("m-chp5-p129-0031", "cand-11793", "the victories", 904, "Plural but unnamed victories attributed to King John; the source gives no campaigns or individual battles."),
]


def read_jsonl(path: Path) -> tuple[list[dict], list[str]]:
    raw_lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    return [json.loads(line) for line in raw_lines if line.strip()], raw_lines


def read_csv(path: Path) -> tuple[list[dict], list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    return rows, fieldnames


def make_mention(mid: str, segment: str, cid: str, surface: str, at: int, text: str, note: str) -> dict:
    exact(text, surface, at)
    return {"mention_id": mid, "segment_id": segment, "candidate_id": cid,
            "surface_form": surface, "start_char": str(at),
            "end_char": str(at + len(surface)), "note": note}


def build_plan():
    for filename, digest in EXPECTED.items():
        path = TABLES / filename
        need(path.exists() and sha256(path) == digest, f"table changed since review: {filename}")
    need(not (TABLES / "book-statements.jsonl").read_bytes().startswith(codecs.BOM_UTF8),
         "statement JSONL encoding changed; refusing rewrite")
    need(sha256(SOURCE) == SOURCE_SHA, "source asset changed since review")
    need(sha256(PDF) == PDF_SHA, "CHP-5.pdf changed since review")
    need(sha256(PAGE_IMAGE) == IMAGE_SHA, "p.129 page image changed since review")
    need(hashlib.sha256(p129_text.encode("utf-8")).hexdigest() == P129_SEGMENT_SHA,
         "p.129 segment fingerprint changed")
    need(hashlib.sha256(p128_text.encode("utf-8")).hexdigest() == P128_SEGMENT_SHA,
         "p.128 segment fingerprint changed")
    need(exact(p128_text, "1708", 3374) == "1708", "p.128 year span changed")

    statements_path = TABLES / "book-statements.jsonl"
    statements, raw_statement_lines = read_jsonl(statements_path)
    by_id = {row["statement_id"]: row for row in statements}
    target_ids = {row["statement_id"] for row in statements if row.get("segment_id") == P129_SEGMENT}
    need(target_ids == set(updates), f"p.129 statement inventory changed: {sorted(target_ids ^ set(updates))}")
    for sid, fields in updates.items():
        need((by_id[sid].get("qualifiers") or {}).get("relation_candidate") is None,
             f"expected unclassified target statement: {sid}")
        need(fields["original_quote"] in p129_text, f"quote not in p.129 segment: {sid}")
    need("st-chp5-p128-1708-ruspoli-opening" in by_id, "p.128 bridge statement missing")
    bridge = by_id["st-chp5-p128-1708-ruspoli-opening"]
    need(bridge.get("segment_id") == P128_SEGMENT, "p.128 bridge segment changed")
    bridge_quote = bridge.get("original_quote", "")
    need(bridge_quote in p128_text, "p.128 bridge quote no longer matches source")

    candidates_path = TABLES / "entity-candidates.csv"
    candidates, candidate_fields = read_csv(candidates_path)
    candidate_ids = {row["candidate_id"] for row in candidates}
    need(not ({c["candidate_id"] for c in NEW_CANDIDATES} & candidate_ids), "one or more new candidate IDs already exist")
    natural_keys = {(r["canonical_name"].strip().casefold(), r["suggested_type"].strip().casefold()) for r in candidates}
    for c in NEW_CANDIDATES:
        key = (c["canonical_name"].strip().casefold(), c["suggested_type"].strip().casefold())
        need(key not in natural_keys, f"duplicate candidate natural key: {c['canonical_name']}")
        natural_keys.add(key)

    mentions_path = TABLES / "mentions.csv"
    mentions, mention_fields = read_csv(mentions_path)
    mention_by_id = {row["mention_id"]: row for row in mentions}
    need("m-chp5-p129-0009" in mention_by_id, "Roman mention mapping missing")
    need(mention_by_id["m-chp5-p129-0009"]["candidate_id"] == "cand-4490", "Roman mention mapping changed")
    p129_mentions = [make_mention(mid, P129_SEGMENT, cid, surface, at, p129_text, note)
                     for mid, cid, surface, at, note in MENTION_SPECS]
    p128_mention = make_mention("m-chp5-p128-0064", P128_SEGMENT, "cand-11783", "1708", 3374, p128_text,
                                "Year introducing the 1708 Ruspoli episode; the following p.129 text completes the account. Venue and series are not restated.")
    new_mention_ids = {m["mention_id"] for m in p129_mentions + [p128_mention]}
    need(not (new_mention_ids & set(mention_by_id)), "one or more new mention IDs already exist")

    existing_statement_ids = set(by_id)
    new_statement_ids = {s["statement_id"] for s in NEW_STATEMENTS}
    need(not (existing_statement_ids & new_statement_ids), "one or more new statement IDs already exist")
    need(len(new_statement_ids) == len(NEW_STATEMENTS), "duplicate new statement IDs")
    for s in NEW_STATEMENTS:
        need(s["original_quote"] in p129_text, f"new quote not in p.129 segment: {s['statement_id']}")
        need(s["statement_id"].startswith("st-chp5-p129-"), "new statement ID outside p.129")
        if s["qualifiers"]["relation_candidate"]:
            need(s["subject_candidate_id"] and s["object_candidate_id"],
                 f"true relation candidate missing endpoint: {s['statement_id']}")

    update_mentions = {
        "m-chp5-p129-0009": {"candidate_id": "cand-11792", "surface_form": "Roman collectors",
                             "start_char": "746", "end_char": "762",
                             "note": "Collective reference to unnamed Roman collectors in the 1707 reception report; this phrase denotes an audience group, not the city alone."}
    }
    return {
        "statements": statements,
        "raw_statement_lines": raw_statement_lines,
        "statement_updates": updates,
        "new_statements": NEW_STATEMENTS,
        "candidates": candidates,
        "candidate_fields": candidate_fields,
        "new_candidates": NEW_CANDIDATES,
        "mentions": mentions,
        "mention_fields": mention_fields,
        "mention_updates": update_mentions,
        "new_mentions": p129_mentions + [p128_mention],
    }


def render_jsonl(plan) -> bytes:
    updated = plan["statement_updates"]
    new_rows = plan["new_statements"]
    out = []
    for raw in plan["raw_statement_lines"]:
        if not raw.strip():
            out.append(raw)
            continue
        obj = json.loads(raw)
        sid = obj.get("statement_id")
        if sid in updated:
            obj.update(updated[sid])
            ending = "\r\n" if raw.endswith("\r\n") else "\n" if raw.endswith("\n") else ""
            out.append(json.dumps(obj, ensure_ascii=False) + (ending or "\n"))
        else:
            out.append(raw)
    out.extend(json.dumps(row, ensure_ascii=False) + "\n" for row in new_rows)
    return "".join(out).encode("utf-8")


def render_csv(rows: list[dict], fields: list[str], updates_by_id: dict,
               update_key: str, new_rows: list[dict], bom: bool) -> bytes:
    updated = []
    for row in rows:
        row = dict(row)
        if row.get(update_key) in updates_by_id:
            row.update(updates_by_id[row[update_key]])
        updated.append(row)
    updated.extend(new_rows)
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="raise", lineterminator="\n")
    writer.writeheader()
    writer.writerows(updated)
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
    parser = argparse.ArgumentParser(description="Controlled S2 writeback for CHP-5 p.129; dry-run by default.")
    parser.add_argument("--apply", action="store_true", help="write the reviewed exact change set")
    args = parser.parse_args()
    plan = build_plan()

    statement_path = TABLES / "book-statements.jsonl"
    candidate_path = TABLES / "entity-candidates.csv"
    mention_path = TABLES / "mentions.csv"
    statement_bytes = render_jsonl(plan)
    candidate_bytes = render_csv(plan["candidates"], plan["candidate_fields"], {}, "candidate_id",
                                 plan["new_candidates"], candidate_path.read_bytes().startswith(codecs.BOM_UTF8))
    mention_bytes = render_csv(plan["mentions"], plan["mention_fields"], plan["mention_updates"], "mention_id",
                               plan["new_mentions"], mention_path.read_bytes().startswith(codecs.BOM_UTF8))
    outputs = {statement_path: statement_bytes, candidate_path: candidate_bytes, mention_path: mention_bytes}

    print("S2 p.129 dry-run / exact plan")
    print(f"source sha256: {sha256(SOURCE)}")
    print(f"PDF sha256: {sha256(PDF)}")
    print(f"page image sha256: {sha256(PAGE_IMAGE)}")
    print(f"p.129 existing statements classified: {len(plan['statement_updates'])}; final page rows={len(plan['statement_updates']) + len(plan['new_statements'])} (21 relation candidates, 13 non-relational)")
    print(f"new statements: {len(plan['new_statements'])}")
    print(f"new candidates: {len(plan['new_candidates'])} ({plan['new_candidates'][0]['candidate_id']}–{plan['new_candidates'][-1]['candidate_id']})")
    print(f"new mentions: p.129={len(MENTION_SPECS)}, p.128 bridge={1}; existing Roman mention remapped=1")
    for path, content in outputs.items():
        print(f"{path.relative_to(ROOT)}: {sha256(path)} -> {hashlib.sha256(content).hexdigest()} ({len(content)} bytes)")
    if not args.apply:
        print("dry-run only; no tables written")
        return

    backups = {}
    for path in outputs:
        backup = path.with_name(path.name + ".bak-s2-chp5-p129-20261012")
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
