#!/usr/bin/env python3
"""Classify p.115 S2 statements and add missing anchored claims."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_ii.md"
SOURCE_REL = "02-sources/02-Markdown/04_CHP-4_sec_ii.md"
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l180-189"
SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
EXPECTED_SHA256 = {
    "book-statements.jsonl": "a45e8914519f01861c89ddfcb7293d5224c4a74deb39367844d2d0096eceb27a",
    "entity-candidates.csv": "c14f778b5f2d4973aff41e0819e84b894ccf4b6ccd5c6bb2dd825a701729dbc7",
    "mentions.csv": "b999b4e0b5440c8dbbf71ac24abf63884bd68c665749f0502e51278c1a71a830",
}
BACKUP_SUFFIX = "bak-s2-chp4-p115-relations-20261011"
P115_IDS = {
    "st-chp4-sec-ii-p115-direct-patronal-link",
    "st-chp4-sec-ii-p115-drawings-adone",
    "st-chp4-sec-ii-p115-drawings-massimi-felibien",
    "st-chp4-sec-ii-p115-drawings-original-commission",
    "st-chp4-sec-ii-p115-elder-camillo-companion",
    "st-chp4-sec-ii-p115-elder-camillo-executor",
    "st-chp4-sec-ii-p115-elder-camillo-nephew",
    "st-chp4-sec-ii-p115-equal-subject-interest",
    "st-chp4-sec-ii-p115-first-work-early-commission",
    "st-chp4-sec-ii-p115-first-work-exceptional-patron",
    "st-chp4-sec-ii-p115-first-work-josephus",
    "st-chp4-sec-ii-p115-fn1-exposition",
    "st-chp4-sec-ii-p115-fn2-archive-copy",
    "st-chp4-sec-ii-p115-fn2-elder-camillo-book",
    "st-chp4-sec-ii-p115-fn2-elder-camillo-will",
    "st-chp4-sec-ii-p115-inheritance-inference",
    "st-chp4-sec-ii-p115-marino-bequest",
    "st-chp4-sec-ii-p115-massimi-acquired-drawings",
    "st-chp4-sec-ii-p115-massimi-artistic-taste",
    "st-chp4-sec-ii-p115-massimi-birth",
    "st-chp4-sec-ii-p115-massimi-education",
    "st-chp4-sec-ii-p115-massimi-estate-name",
    "st-chp4-sec-ii-p115-massimi-new-court",
    "st-chp4-sec-ii-p115-no-moses-episodes-for-cassiano",
    "st-chp4-sec-ii-p115-second-work-early-commission",
    "st-chp4-sec-ii-p115-second-work-title",
    "st-chp4-sec-ii-p115-two-works-style",
    "st-chp4-sec-ii-p115-younger-camillo-kinship",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def slice_between(text: str, start: str, end: str) -> str:
    left = text.index(start)
    right = text.index(end, left) + len(end)
    return text[left:right]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the validated p.115 changes")
    args = parser.parse_args()

    source_bytes = SOURCE.read_bytes()
    if digest(source_bytes) != SOURCE_SHA256:
        raise SystemExit("source SHA-256 changed; stop and review the source")
    source_lines = source_bytes.decode("utf-8").splitlines()
    segment_text = "\n".join(source_lines[179:189])
    line = {n: source_lines[n - 1] for n in range(181, 190)}

    paths = {name: TABLES / name for name in EXPECTED_SHA256}
    originals = {name: path.read_bytes() for name, path in paths.items()}
    for name, expected in EXPECTED_SHA256.items():
        actual = digest(originals[name])
        if actual != expected:
            raise SystemExit(f"{name} changed since p.114; expected {expected}, got {actual}")

    rows: list[dict] = []
    line_rows: list[bytes] = []
    for raw in originals["book-statements.jsonl"].splitlines(keepends=True):
        data = raw.rstrip(b"\r\n")
        if not data:
            line_rows.append(raw)
            continue
        row = json.loads(data.decode("utf-8"))
        rows.append(row)
        line_rows.append(raw)
    p115 = [r for r in rows if r.get("segment_id") == SEGMENT_ID]
    if {r["statement_id"] for r in p115} != P115_IDS:
        raise SystemExit(f"expected exactly 28 original p.115 statements; found {len(p115)}")
    preclassified = {
        r["statement_id"]: r["qualifiers"].get("relation_candidate")
        for r in p115 if "relation_candidate" in r.get("qualifiers", {})
    }
    if preclassified and preclassified != {"st-chp4-sec-ii-p115-elder-camillo-nephew": True}:
        raise SystemExit(f"unexpected preclassified p.115 statements: {preclassified}")

    def qline(number: int, start: str, end: str) -> str:
        return slice_between(line[number], start, end)

    updates = {
        "st-chp4-sec-ii-p115-direct-patronal-link": {
            "relation": False,
            "note": "‘Direct link’ summarizes Haskell’s patronage narrative but does not state a distinct, typed relation; kinship and inferred inheritance are recorded separately.",
        },
        "st-chp4-sec-ii-p115-drawings-adone": {
            "relation": True,
            "note": "The source explicitly links the drawing group’s mainly mythological subjects to Adone as loose inspiration; retain both qualifications.",
        },
        "st-chp4-sec-ii-p115-drawings-massimi-felibien": {
            "relation": True,
            "note": "The source says the drawings belonged to Massimi during Félibien’s 1647–1650 Roman visit; preserve that temporal context.",
            "qualifiers": {"time": "1647–1650, when Félibien was in Rome"},
        },
        "st-chp4-sec-ii-p115-drawings-original-commission": {
            "relation": True,
            "note": "The source explicitly says Marino originally commissioned this group of Poussin drawings.",
        },
        "st-chp4-sec-ii-p115-elder-camillo-companion": {
            "relation": True,
            "note": "Companion is a distinct role explicitly attributed to the elder Camillo in relation to Vincenzo Giustiniani.",
        },
        "st-chp4-sec-ii-p115-elder-camillo-executor": {
            "relation": True,
            "note": "The source explicitly identifies the elder Camillo as Vincenzo Giustiniani’s testamentary executor.",
        },
        "st-chp4-sec-ii-p115-elder-camillo-nephew": {
            "relation": True,
            "note": "The source explicitly identifies the elder Camillo as Vincenzo Giustiniani’s nephew.",
        },
        "st-chp4-sec-ii-p115-equal-subject-interest": {
            "relation": False,
            "note": "This is Haskell’s comparative assessment of the two subjects, not an entity relation.",
        },
        "st-chp4-sec-ii-p115-first-work-early-commission": {
            "relation": True,
            "note": "Haskell infers this commission from the two pictures’ timing; retain ‘must have been’ and the 1644 political context.",
        },
        "st-chp4-sec-ii-p115-first-work-exceptional-patron": {
            "relation": True,
            "note": "Haskell infers an exceptional patron from the first picture’s subject and identifies Massimi in the immediately following passage; this remains an authorial inference.",
        },
        "st-chp4-sec-ii-p115-first-work-josephus": {
            "relation": True,
            "note": "This row now records only Haskell’s attribution of the represented story to Josephus; recurrence, rarity, scene detail, and Bible comparison are separate claims.",
            "predicate": "depicted_story_attributed_to",
            "object": "cand-5948",
            "claim": "Haskell says the story represented in the first Poussin picture was taken from Josephus.",
            "quote": qline(182, "The story which does not occur", "Josephus"),
            "mentioned": ["cand-5945", "cand-5948"],
        },
        "st-chp4-sec-ii-p115-fn1-exposition": {
            "relation": False,
            "note": "This footnote is a bibliographic locator for the episode, not a relation between the painting and the catalogue.",
        },
        "st-chp4-sec-ii-p115-fn2-archive-copy": {
            "relation": True,
            "note": "The source explicitly places the photographic copy at the Warburg Institute Library; the copy remains distinct from the Vatican original.",
        },
        "st-chp4-sec-ii-p115-fn2-elder-camillo-book": {
            "relation": False,
            "note": "The footnote cites a volume concerning the elder Camillo; it does not assert that he is part of or related to that book.",
        },
        "st-chp4-sec-ii-p115-fn2-elder-camillo-will": {
            "relation": False,
            "note": "The will is cited as a source concerning the elder Camillo; citation alone is not a relation claim.",
        },
        "st-chp4-sec-ii-p115-inheritance-inference": {
            "relation": True,
            "note": "Haskell infers inheritance of artistic and antiquarian interests from the distinguished ancestor; discourse identifies that ancestor as Vincenzo Giustiniani, without specifying the exact genealogical degree.",
            "predicate": "inherited_artistic_and_antiquarian_interests_from",
            "object": "cand-1200",
            "claim": "Haskell infers that Camillo inherited his interest in art and antiquities from Vincenzo Giustiniani, identified contextually as his distinguished ancestor; the precise genealogical degree is not stated.",
            "quote": qline(183, "there can be little doubt", "his distinguished ancestor."),
            "mentioned": ["cand-1564", "cand-1200"],
        },
        "st-chp4-sec-ii-p115-marino-bequest": {
            "relation": True,
            "note": "The source identifies a singular but unnamed friend as recipient and only proposes Cassiano as a possible identity; do not equate the two candidates.",
            "predicate": "bequeathed_drawings_to_unidentified_friend",
            "object": "cand-11654",
            "claim": "Haskell says Marino bequeathed the drawings to an unidentified friend, who may have been Cassiano dal Pozzo.",
            "quote": qline(186, "Marino bequeathed them", "Cassiano dal Pozzo"),
            "mentioned": ["cand-1548", "cand-11654", "cand-2036"],
        },
        "st-chp4-sec-ii-p115-massimi-acquired-drawings": {
            "relation": True,
            "note": "The passage connects Massimi’s acquisition to the Marino-commissioned group in the same sentence; ‘large number’ remains unquantified.",
            "qualifiers": {"time": "during the early years of Massimi’s advancement, beginning around 1644"},
        },
        "st-chp4-sec-ii-p115-massimi-artistic-taste": {
            "relation": False,
            "note": "This is Haskell’s evaluation of Massimi’s taste, with no named object or person endpoint.",
        },
        "st-chp4-sec-ii-p115-massimi-birth": {
            "relation": False,
            "note": "Birth year and family background are scalar biographical claims; the family is not specifically named in this sentence.",
        },
        "st-chp4-sec-ii-p115-massimi-education": {
            "relation": True,
            "note": "This row now records only Massimi’s education at the Sapienza; private tutors are a separate unnamed group and relation candidate.",
            "predicate": "educated_at",
            "claim": "Haskell says Massimi received a humanist education at the Sapienza.",
            "quote": qline(183, "He received a sound humanist education", "the Sapienza."),
            "mentioned": ["cand-1564", "cand-5169"],
        },
        "st-chp4-sec-ii-p115-massimi-estate-name": {
            "relation": True,
            "note": "This row now records succession to the cousin’s estate at age 20; adoption of the cousin’s name is recorded separately.",
            "predicate": "succeeded_to_cousins_estate",
            "claim": "Haskell says that at age 20 the younger Camillo succeeded to his cousin Camillo’s estate.",
            "quote": qline(183, "When aged 20", "estate of his cousin Camillo"),
            "mentioned": ["cand-1564", "cand-1563"],
        },
        "st-chp4-sec-ii-p115-massimi-new-court": {
            "relation": True,
            "note": "The source describes Massimi’s association with the centre of Innocent X’s new court; it does not identify a specific building.",
        },
        "st-chp4-sec-ii-p115-no-moses-episodes-for-cassiano": {
            "relation": True,
            "note": "This is an explicit negative work–patron claim; preserve the negative scope and Haskell’s qualification about Poussin’s interest in Moses episodes.",
        },
        "st-chp4-sec-ii-p115-second-work-early-commission": {
            "relation": True,
            "note": "Haskell infers this commission from the two pictures’ timing; retain ‘must have been’ and the 1644 political context.",
        },
        "st-chp4-sec-ii-p115-second-work-title": {
            "relation": False,
            "note": "This statement names the painting’s title and is not an entity relation; the erroneous Poussin object endpoint is removed, while authorship is recorded separately.",
            "object": None,
            "mentioned": ["cand-5946", "cand-4144", "cand-5947"],
        },
        "st-chp4-sec-ii-p115-two-works-style": {
            "relation": False,
            "note": "This is Haskell’s stylistic and compositional assessment of the two paintings, not a relation candidate.",
        },
        "st-chp4-sec-ii-p115-younger-camillo-kinship": {
            "relation": True,
            "note": "The source states a kinship through the younger Camillo’s grandmother but gives no precise degree; retain that uncertainty.",
        },
    }

    for row in p115:
        item = updates[row["statement_id"]]
        q = row["qualifiers"]
        q["relation_candidate"] = item["relation"]
        q["relation_candidate_note"] = item["note"]
        for key, value in item.get("qualifiers", {}).items():
            q[key] = value
        if "predicate" in item:
            row["predicate"] = item["predicate"]
        if "object" in item:
            row["object_candidate_id"] = item["object"]
        if "claim" in item:
            q["claim"] = item["claim"]
        if "quote" in item:
            row["original_quote"] = item["quote"]
        if "mentioned" in item:
            q["mentioned_candidate_ids"] = item["mentioned"]

    def new_statement(statement_id: str, subject: str | None, object_: str | None,
                      predicate: str, claim: str, source_start: int, source_end: int,
                      quote: str, relation: bool, note: str,
                      mentioned: list[str], qualification: str | None = None,
                      time: str | None = None) -> dict:
        qualifiers = {
            "source_line_start": source_start,
            "source_line_end": source_end,
            "pdf_physical_page": 26,
            "printed_page_locator": "p.115",
            "claim": claim,
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "mentioned_candidate_ids": mentioned,
            "relation_candidate": relation,
            "relation_candidate_note": note,
        }
        if qualification:
            qualifiers["qualification"] = qualification
        if time:
            qualifiers["time"] = time
        return {
            "statement_id": statement_id,
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": subject,
            "object_candidate_id": object_,
            "predicate": predicate,
            "qualifiers": qualifiers,
            "original_quote": quote,
            "origin": "book",
            "source_file": SOURCE_REL,
        }

    additions = [
        new_statement(
            "st-chp4-sec-ii-p115-moses-aaron-subjects-recur", "cand-4144", None,
            "recurs_in_art_from_time_to_time",
            "Haskell says depictions of Moses and Aaron’s Rod appeared from time to time in art, without naming a bounded set of works.",
            182, 182, qline(182, "Aaron", "from time to time in art"), False,
            "This is a general iconographic recurrence claim with no identified work or bounded group endpoint.",
            ["cand-4144", "cand-5947"],
        ),
        new_statement(
            "st-chp4-sec-ii-p115-first-work-scene-detail", "cand-5945", None,
            "depicts_moses_childhood_episode_details",
            "The first painting’s episode shows Moses as a child accidentally trampling Pharaoh’s crown and narrowly escaping being stabbed to death.",
            182, 182, qline(182, "the scene where as a child", "being stabbed to death"), False,
            "This records the represented scene’s content; no separately identified event entity is supplied.",
            ["cand-5945", "cand-4144", "cand-4145"],
        ),
        new_statement(
            "st-chp4-sec-ii-p115-first-work-rare-scene", "cand-5945", None,
            "depicts_a_rarely_painted_scene",
            "Haskell characterizes the childhood scene as very rare in Poussin’s work.",
            182, 182, qline(182, "was very.", "rare."), False,
            "This is Haskell’s frequency assessment, not an entity relation; the print reads ‘very rare’ although S0 has an OCR punctuation split.",
            ["cand-5945", "cand-1984"],
            qualification="Haskell’s authorial assessment; scan confirms ‘very rare’, while the preserved S0 OCR reads ‘very. rare.’",
        ),
        new_statement(
            "st-chp4-sec-ii-p115-first-work-story-not-in-bible", "cand-5945", "cand-5965",
            "depicted_story_not_found_in",
            "Haskell says the story represented in the first painting does not occur in the Bible.",
            182, 182, qline(182, "The story which does not occur", "the Bible"), True,
            "This is an explicit negative source-text claim about the depicted story; it is not a positive formal relation.",
            ["cand-5945", "cand-5965"],
        ),
        new_statement(
            "st-chp4-sec-ii-p115-first-work-created-by-poussin", "cand-5945", "cand-1984",
            "created_by",
            "Haskell identifies the first previously named painting as a work by Poussin.",
            184, 184, qline(184, "The two pictures by Poussin", "earliest commissions"), True,
            "The sentence explicitly identifies both previously named pictures as by Poussin; separate statements preserve each work endpoint.",
            ["cand-5945", "cand-1984"],
        ),
        new_statement(
            "st-chp4-sec-ii-p115-second-work-created-by-poussin", "cand-5946", "cand-1984",
            "created_by",
            "Haskell identifies the second previously named painting as a work by Poussin.",
            184, 184, qline(184, "The two pictures by Poussin", "earliest commissions"), True,
            "The sentence explicitly identifies both previously named pictures as by Poussin; separate statements preserve each work endpoint.",
            ["cand-5946", "cand-1984"],
        ),
        new_statement(
            "st-chp4-sec-ii-p115-income-inheritance-inference", "cand-1564", "cand-1200",
            "inherited_sizeable_income_from",
            "Haskell infers that Camillo inherited a sizeable income from Vincenzo Giustiniani, identified contextually as his distinguished ancestor; the precise genealogical degree is not stated.",
            183, 183, qline(183, "there can be little doubt", "his distinguished ancestor."), True,
            "This is Haskell’s qualified inference; the discourse identifies the ancestor as Vincenzo Giustiniani but does not state the exact degree of kinship.",
            ["cand-1564", "cand-1200"],
            qualification="Haskell’s inference (‘there can be little doubt’), not a separately cited inheritance record.",
        ),
        new_statement(
            "st-chp4-sec-ii-p115-massimi-private-tutors-education", "cand-1564", "cand-11653",
            "educated_by_private_tutors",
            "Haskell says Massimi received a humanist education from unnamed private tutors.",
            183, 183, qline(183, "He received a sound humanist education", "private tutors"), True,
            "The passage names only an unnamed plural group of tutors; preserve the group endpoint without inventing individuals.",
            ["cand-1564", "cand-11653"],
        ),
        new_statement(
            "st-chp4-sec-ii-p115-massimi-adopted-cousins-name", "cand-1564", "cand-1563",
            "adopted_name_of_cousin",
            "Haskell says the younger Camillo took the name of his cousin Camillo at age 20.",
            183, 183, qline(183, "When aged 20", "took his name."), True,
            "Name adoption is separated from succession to the cousin’s estate; the source explicitly identifies the cousin as the elder Camillo.",
            ["cand-1564", "cand-1563"],
        ),
        new_statement(
            "st-chp4-sec-ii-p115-adone-created-by-marino", "cand-1549", "cand-1548",
            "created_by",
            "Haskell identifies Adone as Marino’s most famous poem.",
            186, 186, qline(186, "Marino", "the Adone"), True,
            "The source explicitly identifies Marino as the author of the named poem Adone; the drawing group’s inspiration from it is a separate statement.",
            ["cand-1549", "cand-1548"],
        ),
        new_statement(
            "st-chp4-sec-ii-p115-marino-first-known-admirer", "cand-1548", "cand-1984",
            "first_known_admirer_of",
            "Haskell describes Marino as Poussin’s first known admirer.",
            186, 186, qline(186, "Poussin that had originally been commissioned", "the poet Giambattista Marino"), True,
            "This is an explicit attributed role; ‘first known’ is preserved as Haskell’s qualifier.",
            ["cand-1548", "cand-1984"],
            qualification="Haskell’s wording ‘first known’; not a claim that Marino was necessarily Poussin’s first admirer chronologically.",
        ),
        new_statement(
            "st-chp4-sec-ii-p115-felibien-in-rome", "cand-1015", "cand-4490",
            "was_in",
            "Haskell says Félibien was in Rome between 1647 and 1650.",
            186, 186, qline(186, "when the French writer Felibien was in Rome", "between 1647 and 1650"), True,
            "This is a dated person–place statement used to contextualize the reported Massimi ownership of the drawings.",
            ["cand-1015", "cand-4490"], time="1647–1650",
        ),
        new_statement(
            "st-chp4-sec-ii-p115-inventory-original-vatican-library", "cand-5959", "cand-4380",
            "original_inventory_held_by",
            "The footnote identifies the original Massimi inventory with the Biblioteca Vaticana’s Capponi manuscript series; the original is distinct from the Warburg photographic copy.",
            187, 187, line[187 - 0], True,
            "The parenthetical ‘Biblioteca Vaticana: Capponi’ identifies the original’s repository/series; the next clause separately locates the photographic copy at Warburg.",
            ["cand-5959", "cand-4380"],
        ),
        new_statement(
            "st-chp4-sec-ii-p115-drawings-created-by-poussin", "cand-5949", "cand-1984",
            "created_by",
            "Haskell identifies the drawings originally commissioned by Marino as drawings by Poussin.",
            185, 186, qline(186, "Poussin that had originally been commissioned", "the painter"), True,
            "The sentence continuation names the Marino-commissioned group as Poussin’s drawings; ‘by Poussin’ is also repeated in the quotation below.",
            ["cand-5949", "cand-1984"],
        ),
        new_statement(
            "st-chp4-sec-ii-p115-drawings-kept-among-other-drawings", "cand-5949", "cand-11655",
            "kept_among_other_drawings_by_poussin",
            "Félibien’s quoted wording says the Marino-commissioned drawings were kept among several other drawings by Poussin.",
            186, 186, qline(186, "who kept them most carefully among", "hand."), True,
            "The source distinguishes the Marino-commissioned drawing group from several other Poussin drawings; exact works and count are unknown.",
            ["cand-5949", "cand-11655", "cand-1984"],
        ),
        new_statement(
            "st-chp4-sec-ii-p115-other-drawings-held-by-massimi", "cand-11655", "cand-1564",
            "held_by",
            "Haskell’s wording places the additional Poussin drawings among those Massimi kept with the Marino-commissioned group during the reported period.",
            186, 186, qline(186, "they belonged to Massimi", "hand."), True,
            "Group-level holding is inferred from ‘kept them … among several others’; retain the source’s group scope and do not infer individual works.",
            ["cand-11655", "cand-1564", "cand-5949", "cand-1984"],
            qualification="The additional group’s presence in Massimi’s holdings is inferred from Haskell’s ‘among several others’ wording.",
            time="when Félibien was in Rome, 1647–1650",
        ),
        new_statement(
            "st-chp4-sec-ii-p115-other-drawings-created-by-poussin", "cand-11655", "cand-1984",
            "created_by",
            "Haskell identifies the additional drawings kept with Marino’s group as works by Poussin.",
            186, 186, qline(186, "among several others by Poussin", "hand."), True,
            "The maker is explicit; the additional drawings remain an unidentified group with no supplied count beyond ‘several’.",
            ["cand-11655", "cand-1984"],
        ),
    ]

    candidates = [
        {
            "candidate_id": "cand-11653", "index_entry_id": "", "canonical_name": "Unidentified private tutors who educated Camillo Massimi",
            "index_page_range": "", "suggested_type": "", "status": "open", "index_source_file": "", "sub_entry": "",
            "detail": "The passage identifies an unnamed plural group of private tutors but supplies no names or bounded membership.",
            "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT_ID}#L183",
        },
        {
            "candidate_id": "cand-11654", "index_entry_id": "", "canonical_name": "Unidentified friend to whom Giambattista Marino bequeathed the Poussin drawings",
            "index_page_range": "", "suggested_type": "person", "status": "open", "index_source_file": "", "sub_entry": "",
            "detail": "The source identifies a singular unnamed recipient and only suggests that the person may have been Cassiano dal Pozzo; identity is unresolved.",
            "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT_ID}#L186",
        },
        {
            "candidate_id": "cand-11655", "index_entry_id": "", "canonical_name": "Several other unidentified Poussin drawings kept with the Marino-commissioned group",
            "index_page_range": "", "suggested_type": "work", "status": "open", "index_source_file": "", "sub_entry": "",
            "detail": "Félibien’s quoted wording distinguishes several other Poussin drawings from the Marino-commissioned group; titles and exact count are not supplied.",
            "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT_ID}#L186",
        },
    ]

    def mention(mention_id: str, candidate_id: str, surface: str, note: str) -> dict:
        start = segment_text.index(surface)
        if segment_text.find(surface, start + 1) != -1:
            raise SystemExit(f"mention surface is not unique in p.115: {surface!r}")
        return {"mention_id": mention_id, "segment_id": SEGMENT_ID, "candidate_id": candidate_id,
                "surface_form": surface, "start_char": str(start), "end_char": str(start + len(surface)), "note": note}

    other_surface = slice_between(line[186], "several others by Poussin", "hand")
    mentions = [
        mention("m-chp4-sec-ii-p115-0051", "cand-11653", "private tutors", "Unnamed plural group; no individual tutors are identified."),
        mention("m-chp4-sec-ii-p115-0052", "cand-11654", "some unidentified friend", "Singular recipient; Cassiano is only proposed as a possible identity."),
        mention("m-chp4-sec-ii-p115-0053", "cand-11655", other_surface, "Additional unidentified Poussin drawings, distinct from the Marino-commissioned group."),
    ]
    if len({m["mention_id"] for m in mentions}) != len(mentions):
        raise SystemExit("duplicate new mention ID")

    new_ids = {r["statement_id"] for r in additions}
    if len(new_ids) != len(additions) or any(r["statement_id"] in {x["statement_id"] for x in rows} for r in additions):
        raise SystemExit("duplicate statement ID")
    if len({c["candidate_id"] for c in candidates}) != len(candidates):
        raise SystemExit("duplicate candidate ID")

    # Build a byte-preserving JSONL update: only the 28 p.115 rows and inserted rows change.
    by_id = {r["statement_id"]: r for r in p115}
    if set(updates) != P115_IDS or len(additions) != 17:
        raise SystemExit("update/addition manifest mismatch")
    new_statement_bytes = [
        (json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
        for row in additions
    ]
    statement_output: list[bytes] = []
    inserted = False
    for raw in line_rows:
        data = raw.rstrip(b"\r\n")
        if data:
            obj = json.loads(data.decode("utf-8"))
            sid = obj.get("statement_id")
            if sid in by_id:
                updated = by_id[sid]
                # Keep the existing object mutations above, serialized only for this row.
                raw = (json.dumps(updated, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
        statement_output.append(raw)
        if data and json.loads(data.decode("utf-8")).get("statement_id") == "st-chp4-sec-ii-p115-younger-camillo-kinship":
            statement_output.extend(new_statement_bytes)
            inserted = True
    if not inserted:
        raise SystemExit("could not locate the last p.115 statement for insertion")
    statement_bytes = b"".join(statement_output)

    def append_csv(data: bytes, new_rows: list[dict], path: Path) -> bytes:
        header_line = data.splitlines()[0].decode("utf-8")
        fields = next(csv.reader([header_line]))
        stream = io.StringIO(newline="")
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n", extrasaction="raise")
        writer.writerows(new_rows)
        prefix = data if data.endswith((b"\n", b"\r")) else data + b"\n"
        return prefix + stream.getvalue().encode("utf-8")

    candidate_bytes = append_csv(originals["entity-candidates.csv"], candidates, paths["entity-candidates.csv"])
    mention_bytes = append_csv(originals["mentions.csv"], mentions, paths["mentions.csv"])
    outputs = {
        "book-statements.jsonl": statement_bytes,
        "entity-candidates.csv": candidate_bytes,
        "mentions.csv": mention_bytes,
    }

    classified = [r for r in p115]
    true_count = sum(updates[sid]["relation"] for sid in updates) + sum(r["qualifiers"]["relation_candidate"] for r in additions)
    false_count = len(updates) - sum(updates[sid]["relation"] for sid in updates) + len(additions) - sum(r["qualifiers"]["relation_candidate"] for r in additions)
    print(f"p.115 original statements: {len(classified)}; classified: {len(updates)}/{len(classified)}")
    print(f"new statements: {len(additions)} (relation candidates {sum(r['qualifiers']['relation_candidate'] for r in additions)}, non-relations {len(additions)-sum(r['qualifiers']['relation_candidate'] for r in additions)})")
    print(f"p.115 after write: {len(classified)+len(additions)} statements; relation candidates {true_count}; non-relations {false_count}; unclassified 0")
    print(f"new candidates: {len(candidates)}; new mentions: {len(mentions)}")
    print("new mention offsets:", [(m["mention_id"], m["surface_form"], m["start_char"], m["end_char"]) for m in mentions])
    print("logical writes preserve existing CSV bytes and all non-p.115 JSONL rows")
    if not args.apply:
        print("dry-run only; no files written")
        return

    backups = {name: paths[name].with_name(f"{paths[name].name}.{BACKUP_SUFFIX}") for name in paths}
    if any(path.exists() for path in backups.values()):
        raise SystemExit("recovery backup already exists; stop and inspect")
    for name, path in backups.items():
        shutil.copy2(paths[name], path)
    temp_paths = {name: paths[name].with_name(paths[name].name + ".p115-tmp") for name in paths}
    try:
        for name, data in outputs.items():
            temp_paths[name].write_bytes(data)
        for name in paths:
            os.replace(temp_paths[name], paths[name])
    except Exception:
        for name, path in paths.items():
            shutil.copy2(backups[name], path)
        for temp in temp_paths.values():
            temp.unlink(missing_ok=True)
        raise
    for name, path in paths.items():
        print(f"wrote {name}: {digest(path.read_bytes())}")
    print("recovery copies:", ", ".join(str(p.relative_to(ROOT)) for p in backups.values()))


if __name__ == "__main__":
    main()
