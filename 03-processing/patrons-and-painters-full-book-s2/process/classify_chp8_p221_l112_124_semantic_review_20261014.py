"""Guarded S2 semantic review for printed p.221, body lines 113-124."""
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
PAGE_IMAGE = ROOT / "scripts" / ".tmp_s2_chp8_p221_review.png"
SEGMENT_ID = "chp-8:08_CHP-8_sec_ii:l112-124"
SEGMENT_SHA = "d2da0e390237cbab6a9b1ca7e8c3cf52be8034c1aff7a35369072ccf12bf88f4"
BACKUP_SUFFIX = ".bak-s2-chp8-p221-l112-124-semantic-review-20261014"
EXPECTED_HASHES = {
    STATEMENTS: "b0ff4087c0681bed4528c3d2e0daac6553abc34b55b62ca7ed01dae089534b3e",
    CANDIDATES: "88f4dbfea900a74d08428d200869d34336f705991ac249f2dfef402928ae10b0",
    MENTIONS: "e36a6b348a0c7469b386b4f4c863edb105b4887a9cfdc3fba542db63b72b8f62",
    COVERAGE: "6207ec3734deacfe3e02ec341c3a558440f7273ad4f9c2c964ad94ab2710fc34",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    PDF: "cb11451ac726f37ed5badf21a569af88f790f858f1c39eb63f2efb58a0fe4ac3",
    PAGE_IMAGE: "360ef030d8253fe4dc39aba4b89f222d58055ba474bbac1625e84df85a64d89d",
}

OLD_NOTES = {
    "st-chp8-p221-archbishop-palace-and-vigilance-statue-open":
        "This combines the gallery's location, the palace's patron and architect, its relation to the Cathedral, the stairway and piano nobile, and the Vigilance statue. These building, spatial, and artwork claims are separated below; the statue's Ferrerio clause continues on p.222.",
    "st-chp8-p221-governors-ambition":
        "This is Haskell's comparative assessment of the Governors' campaign, not itself a relation. The actual commission aim is recorded separately.",
    "st-chp8-p221-melanconici-commission":
        "This combines the Abraham picture's approval with the subsequent award of the full commission and fee. They are separated below; the approval clause continues the p.220 arrival statement.",
    "st-chp8-p221-melanconici-oils-and-frescoes":
        "This combines the oil paintings' location with Melanconici's arrival to undertake frescoes. The work group, location, and artist's activity are separated below.",
    "st-chp8-p221-melanconici-results-and-additional-pictures":
        "This combines Haskell's assessment, the committee's reported comment, the fee rationale, additional pictures, and permission for a signature. The source-specific claims are separated below; permission does not establish that the signature was actually appended.",
    "st-chp8-p221-provincial-patronage-context":
        "This combines a comparison with private patrons, an unnamed group of provincial figures, and Ruffo as one example. The general context and source-bounded group are separated below.",
    "st-chp8-p221-ruffo-cardinal-and-legate-appointments":
        "This combines Ruffo's cardinalate, return to Ravenna, Ferrara offices, and Bologna interval. The office, place, and date claims are separated below; Ferrara's 'particularly close' connection remains an attributed assessment.",
    "st-chp8-p221-ruffo-early-ecclesiastical-career":
        "This combines Church entry, a papal appointment, service in Malta and Tuscany, and chamberlain service to an unnamed Pope. These are recorded separately without identifying the unnamed Pope.",
    "st-chp8-p221-ruffo-gallery-taste":
        "This combines Ruffo's opportunities to seek works, Haskell's interpretation of his taste, and collection assembly in Ferrara. The relational fact and the attributed assessment are separated below.",
    "st-chp8-p221-ruffo-origin-and-family":
        "This combines Ruffo's reported birthplace and date with Haskell's shared-family statement about Don Antonio. Birth and family affiliation are separated below; the OCR corrections remain recorded.",
    "st-chp8-p221-ruffo-rome-palace-and-death":
        "This combines Ruffo's residence, the palace's location, its purchase from the Cibo family, and his death. These claims are separated below; age and date remain source-reported.",
}

LINKS = {
    "st-chp8-p221-archbishop-palace-and-vigilance-statue-open": [
        "st-chp8-p221-ruffo-gallery-kept-in-palace",
        "st-chp8-p221-palace-built-for-ruffo",
        "st-chp8-p221-palace-built-by-mattei",
        "st-chp8-p221-palace-adjoins-cathedral",
        "st-chp8-p221-stairway-leads-to-piano-nobile",
        "st-chp8-p221-vigilance-statue-on-balustrade",
        "st-chp8-p221-vigilance-statue-commissioned-by-ruffo",
        "st-chp8-p221-ferrerio-sculptor-of-vigilance",
    ],
    "st-chp8-p221-governors-ambition": [
        "st-chp8-p221-governors-seek-artists-from-italian-schools",
    ],
    "st-chp8-p221-melanconici-commission": [
        "st-chp8-p221-abraham-picture-approved",
        "st-chp8-p221-melanconici-entire-commission",
    ],
    "st-chp8-p221-melanconici-oils-and-frescoes": [
        "st-chp8-p221-oil-paintings-made-in-naples",
        "st-chp8-p221-melanconici-arrives-for-frescoes",
    ],
    "st-chp8-p221-melanconici-results-and-additional-pictures": [
        "st-chp8-p221-fresco-results-controversial",
        "st-chp8-p221-committee-criticism-unavoidable",
        "st-chp8-p221-willing-artist-reasonable-fee-rationale",
        "st-chp8-p221-melanconici-additional-pictures",
        "st-chp8-p221-melanconici-signature-permitted",
    ],
    "st-chp8-p221-provincial-patronage-context": [
        "st-chp8-p221-private-patron-resource-comparison",
        "st-chp8-p221-small-town-figures-break-isolation",
        "st-chp8-p221-ruffo-example-of-provincial-patronage",
    ],
    "st-chp8-p221-ruffo-cardinal-and-legate-appointments": [
        "st-chp8-p221-ruffo-cardinalate-1706",
        "st-chp8-p221-ruffo-returns-as-legate-to-ravenna",
        "st-chp8-p221-ruffo-legate-in-ferrara-from-1710",
        "st-chp8-p221-ruffo-archbishop-in-ferrara-1717-1738",
        "st-chp8-p221-ruffo-bologna-interval-1721-1727",
        "st-chp8-p221-ruffo-ferrara-connection-close",
    ],
    "st-chp8-p221-ruffo-early-ecclesiastical-career": [
        "st-chp8-p221-ruffo-enters-church",
        "st-chp8-p221-innocent-xii-appoints-vice-legate",
        "st-chp8-p221-ruffo-inquisitor-in-malta",
        "st-chp8-p221-ruffo-nunzio-in-tuscany",
        "st-chp8-p221-ruffo-maestro-de-camera-to-pope",
    ],
    "st-chp8-p221-ruffo-gallery-taste": [
        "st-chp8-p221-ruffo-opportunities-to-seek-artists",
        "st-chp8-p221-ruffo-gallery-taste-assessment",
        "st-chp8-p221-ruffo-assembles-collection-in-ferrara",
    ],
    "st-chp8-p221-ruffo-origin-and-family": [
        "st-chp8-p221-ruffo-born-in-naples",
        "st-chp8-p221-ruffo-shares-family-with-don-antonio",
    ],
    "st-chp8-p221-ruffo-rome-palace-and-death": [
        "st-chp8-p221-ruffo-lives-in-rome-palace",
        "st-chp8-p221-rome-palace-opposite-trevi-fountain",
        "st-chp8-p221-ruffo-buys-palace-from-cibo-family",
        "st-chp8-p221-ruffo-dies-in-palace",
    ],
}


def row(statement_id, subject, object_, predicate, lines, claim, quote, note, *,
        relation=True, qualification=None, mentioned=None, speaker="Haskell", extra=None):
    return {
        "statement_id": statement_id, "subject": subject, "object": object_,
        "predicate": predicate, "line_start": lines[0], "line_end": lines[1],
        "claim": claim, "quote": quote, "note": note, "relation": relation,
        "qualification": qualification or
            "Keep the claim at Haskell's reported level; do not infer an unnamed identity, office-holder, or completed outcome.",
        "mentioned": mentioned or [], "speaker": speaker, "extra": extra or {},
    }


NEW_ROWS = [
    row("st-chp8-p221-abraham-picture-approved", "cand-1637", None,
        "experimental_picture_met_with_approval", (113, 113),
        "Haskell says the experimental Abraham picture met with approval.",
        "and met with approval",
        "The approver is not named in this clause; the statement continues the p.220 report that the picture arrived quickly.",
        mentioned=["cand-1637"],
        extra={
            "continued_from_segment_id": "chp-8:08_CHP-8_sec_ii:l100-110",
            "continued_from_source_line": 110,
            "continued_from_statement_id": "st-chp8-p220-abraham-picture-arrives-quickly",
            "continuation_status": "closed",
            "continuation_fragment": "and met with approval",
        }),
    row("st-chp8-p221-melanconici-entire-commission", "cand-1636", "cand-7686",
        "received_entire_fourteen_picture_commission", (113, 113),
        "Melanconici was to receive the entire commission for a fee of 4,000 ducats, including travel, board, and lodging expenses.",
        "It was arranged that Melanconici should be given the entire commission for a fee of 4000 ducats, which was to include all his expenses for travel and for board and lodging",
        "The entire commission refers to the fourteen central-nave pictures established in the preceding account; the passage does not name who made the arrangement.",
        mentioned=["cand-1636", "cand-7686"],
        extra={"amount": 4000, "currency": "ducats", "included_expenses": ["travel", "board", "lodging"]}),
    row("st-chp8-p221-oil-paintings-made-in-naples", "cand-7686", "cand-1722",
        "oil_paintings_made_in_city", (113, 113),
        "The oil paintings in the commission were painted in Naples.",
        "The oils were painted in Naples",
        "The source distinguishes the oil paintings from the frescoes Melanconici later undertook in Bergamo.",
        mentioned=["cand-7686", "cand-1722"]),
    row("st-chp8-p221-melanconici-arrives-for-frescoes", "cand-1636", "cand-6208",
        "arrived_in_city_to_undertake_frescoes", (113, 113),
        "Melanconici arrived in Bergamo in June 1693 to undertake the church frescoes.",
        "then in June 1693 the artist himself arrived in Bergamo to undertake the frescoes",
        "The artist is identified by the preceding sentence; the source does not give individual fresco titles.",
        mentioned=["cand-1636", "cand-6208", "cand-12067"],
        extra={"date": "1693-06"}),
    row("st-chp8-p221-fresco-results-controversial", "cand-12067", None,
        "results_reported_as_controversial", (113, 113),
        "Haskell reports that the results of Melanconici's fresco work were controversial.",
        "The results were controversial",
        "This is Haskell's summary of reception; no particular critic or individual fresco is identified.",
        relation=False, mentioned=["cand-12067"]),
    row("st-chp8-p221-committee-criticism-unavoidable", "cand-7641", "cand-12067",
        "committee_regarded_criticism_as_unavoidable", (113, 113),
        "Haskell reports that the committee regarded criticism of the fresco results as unavoidable.",
        "criticism, as the committee pointed out, ‘is unavoidable’.",
        "The committee's words are reported through Haskell; no specific review or critic is named.",
        speaker="Haskell reporting the committee",
        mentioned=["cand-7641", "cand-12067"]),
    row("st-chp8-p221-willing-artist-reasonable-fee-rationale", None, None,
        "haskell_generalized_about_willing_artists_and_fees", (113, 113),
        "Haskell says a willing artist working for a reasonable fee was too rare to turn down.",
        "a willing artist working for a reasonable fee was too rare to be turned down",
        "This is Haskell's general rationale, not evidence of a separate committee rule or a named fee comparison.",
        relation=False),
    row("st-chp8-p221-melanconici-additional-pictures", "cand-1636", "cand-7702",
        "given_additional_church_pictures_to_paint", (113, 113),
        "Melanconici was given an unspecified number of additional pictures to paint in the church.",
        "Melanconici was given a certain number of other pictures to paint in the church",
        "The number and subjects of the additional pictures are not supplied; they remain distinct from the fourteen-picture commission.",
        mentioned=["cand-1636", "cand-7702", "cand-7627"]),
    row("st-chp8-p221-melanconici-signature-permitted", "cand-1636", "cand-1638",
        "permitted_to_append_signature_beneath_work", (113, 113),
        "Melanconici was allowed to append a very large signature beneath David with the Head of Goliath.",
        "allowed to append a gigantic signature, easily visible to the naked eye, beneath the colourful, if slightly academic, figure of David with the Head of Goliath",
        "The source reports permission and location; it does not explicitly say that the signature was actually added.",
        mentioned=["cand-1636", "cand-1638"],
        extra={"signature_visibility": "easily visible to the naked eye"}),
    row("st-chp8-p221-governors-seek-artists-from-italian-schools", "cand-7640", "cand-12068",
        "sought_to_commission_artists_from_italian_schools", (114, 115),
        "The Governors of Santa Maria Maggiore sought to commission artists from all the schools of Italy for their church decoration.",
        "The long-drawn-out and complicated manœuvres of the Governors of S. Maria\nMaggiore in Bergamo to commission artists from all the schools of Italy for the decoration of their church",
        "This records the commissioning aim, not proof that artists from every school were hired; the artist group has no named members.",
        mentioned=["cand-7640", "cand-12068", "cand-7627", "cand-7743", "cand-3461"]),
    row("st-chp8-p221-private-patron-resource-comparison", None, "cand-7640",
        "private_patron_lacked_comparable_resources_and_time", (115, 115),
        "Haskell says no private patron had the Governors' resources or available time to compete with them.",
        "No private patron had either the resources or the available time to compete with this body.",
        "This is a broad comparative assessment; the private patrons are not an identified or bounded group.",
        relation=False, mentioned=["cand-7640"]),
    row("st-chp8-p221-small-town-figures-break-isolation", "cand-12069", "cand-12070",
        "helped_to_break_provincial_cultural_isolation", (115, 115),
        "Haskell says men in other small towns helped, on a modest scale, to break the cultural isolation of the Italian provinces.",
        "Yet in other small towns there were men who were helping, on however modest a scale, to break the cultural isolation of the Italian provinces.",
        "The group is source-bounded only by this activity and setting; its members and towns are not enumerated.",
        mentioned=["cand-12069", "cand-12070"]),
    row("st-chp8-p221-ruffo-example-of-provincial-patronage", "cand-2304", "cand-12069",
        "named_as_one_example_of_provincial_patronage", (115, 115),
        "Haskell presents Cardinal Tommaso Ruffo as one example of the men helping to break provincial cultural isolation.",
        "One such was Cardinal Tommaso Russo.",
        "The page image confirms Ruffo; 'one such' links him to the source-bounded group without supplying other members.",
        mentioned=["cand-2304", "cand-12069"],
        extra={"ocr_corrections": [{
            "source_file": SOURCE_REL, "source_line": 115, "ocr": "Russo", "print": "Ruffo",
            "basis": "CHP-8.pdf physical page 23."
        }]}),
    row("st-chp8-p221-ruffo-born-in-naples", "cand-2304", "cand-1722",
        "reported_birthplace", (115, 116),
        "Haskell reports that Tommaso Ruffo was born in Naples in 1663.",
        "He was bom in Naples in 1663",
        "The birth year and birthplace are reported by Haskell; the page image reads 'born'.",
        mentioned=["cand-2304", "cand-1722"],
        extra={"date": "1663", "ocr_corrections": [{
            "source_file": SOURCE_REL, "source_line": 115, "ocr": "bom", "print": "born",
            "basis": "CHP-8.pdf physical page 23."
        }]}),
    row("st-chp8-p221-ruffo-shares-family-with-don-antonio", "cand-2304", "cand-7694",
        "reported_member_of_same_family_as_don_antonio", (115, 116),
        "Haskell places Cardinal Tommaso Ruffo and Don Antonio Ruffo in the same unspecified great southern family.",
        "of the same great southern family which had given birth to Don\nAntonio in Messina.",
        "The source does not identify the family's name, branch, or a more precise kinship; it does not establish a parent-child relation.",
        mentioned=["cand-2304", "cand-7694", "cand-2297", "cand-1655"]),
    row("st-chp8-p221-ruffo-enters-church", "cand-2304", "cand-3400",
        "entered_catholic_church", (116, 116),
        "Haskell says Ruffo entered the Catholic Church.",
        "He entered the Church",
        "The source gives no date for this entry.",
        mentioned=["cand-2304", "cand-3400"]),
    row("st-chp8-p221-innocent-xii-appoints-vice-legate", "cand-1929", "cand-2304",
        "appointed_vice_legate_in_ravenna", (116, 117),
        "Pope Innocent XII made Ruffo Vice-Legate in Ravenna in 1692.",
        "in 1692 was made Vice-Legate in\nRavenna by Pope Innocent XII.",
        "The appointment and location are reported by Haskell; the source supplies no separate appointment instrument.",
        mentioned=["cand-1929", "cand-2304", "cand-7697"],
        extra={"date": "1692"}),
    row("st-chp8-p221-ruffo-inquisitor-in-malta", "cand-2304", "cand-6938",
        "served_as_inquisitor_in", (117, 117),
        "Haskell says Ruffo served as Inquisitor in Malta.",
        "He then served as Inquisitor in Malta",
        "No dates for this service are supplied.",
        mentioned=["cand-2304", "cand-6938"]),
    row("st-chp8-p221-ruffo-nunzio-in-tuscany", "cand-2304", "cand-6232",
        "served_as_nunzio_in", (117, 118),
        "Haskell says Ruffo served as Nunzio in Tuscany before becoming maestro de camera to the Pope.",
        "and Nunzio in\nTuscany",
        "The source names the office and region but gives no service dates; the following Pope is left unidentified.",
        mentioned=["cand-2304", "cand-6232"]),
    row("st-chp8-p221-ruffo-maestro-de-camera-to-pope", "cand-2304", "cand-12071",
        "served_as_maestro_de_camera_to", (118, 118),
        "Ruffo became maestro de camera to an unnamed Pope.",
        "before becoming maestro de camera to the Pope",
        "The Pope is not named; do not equate this reference with Pope Innocent XII.",
        mentioned=["cand-2304", "cand-12071"]),
    row("st-chp8-p221-ruffo-cardinalate-1706", "cand-2304", None,
        "reported_cardinalate_attainment", (118, 118),
        "Haskell reports that Ruffo was made Cardinal in 1706.",
        "He was made Cardinal in 1706",
        "The appointing agent is not identified; cardinalate is retained here as a biographical status, not a formal edge to an unnamed appointing person.",
        relation=False, mentioned=["cand-2304"], extra={"date": "1706"}),
    row("st-chp8-p221-ruffo-returns-as-legate-to-ravenna", "cand-2304", "cand-7697",
        "returned_to_ravenna_as_legate", (118, 118),
        "After becoming a Cardinal, Ruffo returned to Ravenna as Legate for a short time.",
        "after which he returned to Ravenna as Legate for a short time",
        "The source gives no exact dates for this brief legation.",
        mentioned=["cand-2304", "cand-7697"]),
    row("st-chp8-p221-ruffo-legate-in-ferrara-from-1710", "cand-2304", "cand-1017",
        "served_as_legate_in_ferrara", (118, 119),
        "Haskell says Ruffo went to Ferrara and served there as Legate from 1710.",
        "before going to Ferrara, with which his connection was particularly close. He remained there from 1710 as\nLegate",
        "The date marks the reported start of his Ferrara legateship; Haskell's separate characterization of the connection is not an objective measure.",
        mentioned=["cand-2304", "cand-1017"], extra={"start_date": "1710"}),
    row("st-chp8-p221-ruffo-ferrara-connection-close", "cand-2304", "cand-1017",
        "haskell_characterized_connection_as_particularly_close", (118, 118),
        "Haskell characterizes Ruffo's connection with Ferrara as particularly close.",
        "with which his connection was particularly close",
        "This is Haskell's evaluative characterization, not an independently measured degree of connection.",
        relation=False, mentioned=["cand-2304", "cand-1017"]),
    row("st-chp8-p221-ruffo-archbishop-in-ferrara-1717-1738", "cand-2304", "cand-1017",
        "served_as_archbishop_in_ferrara", (119, 120),
        "Haskell says Ruffo was Archbishop in Ferrara from 1717 until 1738, apart from the Bologna interval.",
        "and from 1717 as Archbishop until 1738, except for six years in Bologna from\n1721 to 1727.",
        "The exception is kept explicit; the passage does not identify the office Ruffo held while in Bologna.",
        mentioned=["cand-2304", "cand-1017", "cand-3398"],
        extra={"start_date": "1717", "end_date": "1738", "exception_place": "cand-3398", "exception_dates": ["1721", "1727"]}),
    row("st-chp8-p221-ruffo-bologna-interval-1721-1727", "cand-2304", "cand-3398",
        "resided_in_bologna_during_ferrara_exception", (119, 120),
        "Haskell says Ruffo spent six years in Bologna from 1721 to 1727 during the Ferrara period.",
        "except for six years in Bologna from\n1721 to 1727",
        "The source reports the interval but does not specify an office held in Bologna.",
        mentioned=["cand-2304", "cand-3398"],
        extra={"start_date": "1721", "end_date": "1727", "duration_years": 6}),
    row("st-chp8-p221-ruffo-lives-in-rome-palace", "cand-2304", "cand-0746",
        "resided_in_rome_palace", (120, 121),
        "Haskell says Ruffo later lived in Rome in a palace opposite the Trevi Fountain.",
        "As an old man he then lived in Rome in a palace opposite the Trevi\nFountain",
        "The residence is the Cibo palace candidate; the palace's position opposite the fountain is also recorded separately.",
        mentioned=["cand-2304", "cand-4490", "cand-0746", "cand-7698"]),
    row("st-chp8-p221-rome-palace-opposite-trevi-fountain", "cand-0746", "cand-7698",
        "palace_opposite_landmark", (120, 121),
        "The palace where Ruffo lived in Rome stood opposite the Trevi Fountain.",
        "a palace opposite the Trevi\nFountain",
        "The printed page confirms the line break; the relation is positional, not an assertion that the palace was part of the fountain.",
        mentioned=["cand-0746", "cand-7698"]),
    row("st-chp8-p221-ruffo-buys-palace-from-cibo-family", "cand-2304", "cand-7699",
        "bought_rome_palace_from_family", (121, 121),
        "Haskell says Ruffo bought the Rome palace from the Cibo family.",
        "which he bought from the Cibo family",
        "The source does not identify an individual seller or the family's branch.",
        mentioned=["cand-2304", "cand-0746", "cand-7699"]),
    row("st-chp8-p221-ruffo-dies-in-palace", "cand-2304", "cand-0746",
        "died_at_rome_palace", (121, 121),
        "Haskell says Ruffo died in the palace in 1753, aged 90.",
        "He died there, aged 90, in 1753.",
        "The age and date are retained as Haskell reports them.",
        mentioned=["cand-2304", "cand-0746"], extra={"date": "1753", "age": 90}),
    row("st-chp8-p221-ruffo-opportunities-to-seek-artists", "cand-2304", "cand-12072",
        "had_opportunities_to_seek_works_by_artists", (122, 122),
        "Haskell says Ruffo had opportunities to seek works by most leading Italian artists, except those in Venice.",
        "Ruffo had plenty of opportunities for seeking works by most of the leading Italian artists with the notable exception of those in Venice.",
        "The artists are an open, source-bounded group; no individual artist or complete member list is supplied.",
        mentioned=["cand-2304", "cand-12072", "cand-3401"]),
    row("st-chp8-p221-ruffo-gallery-taste-assessment", "cand-2307", None,
        "gallery_contents_interpreted_as_evidence_of_taste", (122, 122),
        "Haskell interprets the varied contents of Ruffo's gallery as evidence of broad taste and enthusiasm.",
        "the very varied contents of his gallery testify to the width of his tastes as well as to his enthusiasm",
        "This is Haskell's interpretation of the collection, not an independently assessed complete inventory.",
        relation=False, mentioned=["cand-2304", "cand-2307"]),
    row("st-chp8-p221-ruffo-assembles-collection-in-ferrara", "cand-2304", "cand-2307",
        "assembled_collection_in_city", (122, 122),
        "Haskell says Ruffo brought his collection together in Ferrara.",
        "It was in Ferrara that he brought the collection together",
        "The passage locates the collection's assembly in Ferrara; it does not enumerate where each object was acquired.",
        mentioned=["cand-2304", "cand-2307", "cand-1017"]),
    row("st-chp8-p221-ruffo-gallery-kept-in-palace", "cand-2307", "cand-2306",
        "collection_kept_in_palace", (123, 123),
        "Haskell says Ruffo's gallery was kept in the new Archbishop's Palace in Ferrara.",
        "The gallery was kept in the new Archbishop’s Palace",
        "The Ferrara Archbishop's Palace is distinct from Ruffo's later Roman residence.",
        mentioned=["cand-2307", "cand-2306"]),
    row("st-chp8-p221-palace-built-for-ruffo", "cand-2306", "cand-2304",
        "palace_built_for_patron", (123, 124),
        "The new Ferrara Archbishop's Palace was built for Cardinal Tommaso Ruffo in 1710.",
        "which was built for him in\n1710'by the Roman architect Tommaso Mattei",
        "The page image reads '1710 by'; 'him' resolves to Ruffo from the preceding clause.",
        mentioned=["cand-2306", "cand-2304"],
        extra={"date": "1710", "ocr_corrections": [{
            "source_file": SOURCE_REL, "source_line": 124, "ocr": "1710'by", "print": "1710 by",
            "basis": "CHP-8.pdf physical page 23."
        }]}),
    row("st-chp8-p221-palace-built-by-mattei", "cand-1580", "cand-2306",
        "built_palace_as_architect", (123, 124),
        "The Roman architect Tommaso Mattei built the Archbishop's Palace in Ferrara in 1710.",
        "1710'by the Roman architect Tommaso Mattei",
        "The page image reads '1710 by'; the source names Mattei as architect and builder.",
        mentioned=["cand-1580", "cand-2306"], extra={"date": "1710"}),
    row("st-chp8-p221-palace-adjoins-cathedral", "cand-2306", "cand-7700",
        "palace_adjoins_cathedral", (124, 124),
        "The Archbishop's Palace adjoined an unnamed Cathedral in Ferrara.",
        "this vast palace adjoining the Cathedral",
        "The text does not name the Cathedral; the open place candidate preserves that limit.",
        mentioned=["cand-2306", "cand-7700"]),
    row("st-chp8-p221-stairway-leads-to-piano-nobile", "cand-12074", "cand-12075",
        "stairway_leads_to_piano_nobile", (124, 124),
        "A white stone stairway in two flights led to the piano nobile; the flights bent back on one another.",
        "a white stone stairway leads up to the' piano nobile in two great flights of steps which bend back on each other",
        "The page image reads 'the piano'; the stairway is an architectural work component, while the piano nobile is a palace space.",
        mentioned=["cand-12074", "cand-12075", "cand-2306"],
        extra={"flight_count": 2, "material": "white stone", "ocr_corrections": [{
            "source_file": SOURCE_REL, "source_line": 124, "ocr": "the' piano", "print": "the piano",
            "basis": "CHP-8.pdf physical page 23."
        }]}),
    row("st-chp8-p221-vigilance-statue-on-balustrade", "cand-7701", "cand-12076",
        "statue_placed_at_midpoint_of_balustrade", (124, 124),
        "The Statue of Vigilance stood halfway along the palace stairway's balustrade.",
        "At the halfway mark on the balustrade stands a statue of Vigilance",
        "The source gives the location on the balustrade; the balustrade is kept distinct from the statue and the stairway.",
        mentioned=["cand-7701", "cand-12076", "cand-2306"]),
    row("st-chp8-p221-vigilance-statue-commissioned-by-ruffo", "cand-7701", "cand-2304",
        "work_commissioned_by_patron", (124, 124),
        "Ruffo commissioned the Statue of Vigilance for the palace staircase.",
        "a statue of Vigilance commissioned by Ruffo from the sculptor Andrea Ferrerio,",
        "The statue is a work distinct from the palace; the named sculptor is recorded in a separate artist-to-work statement.",
        mentioned=["cand-7701", "cand-2304", "cand-1024"]),
    row("st-chp8-p221-ferrerio-sculptor-of-vigilance", "cand-1024", "cand-7701",
        "sculptor_credited_with_statue", (124, 124),
        "Haskell identifies Andrea Ferrerio as the sculptor from whom Ruffo commissioned the Statue of Vigilance.",
        "a statue of Vigilance commissioned by Ruffo from the sculptor Andrea Ferrerio,",
        "The page ends mid-description; the sentence continues with Ferrerio's pupilage on p.222.",
        mentioned=["cand-1024", "cand-7701", "cand-2304"],
        extra={
            "continuation_to_segment_id": "chp-8:08_CHP-8_sec_ii:l126-138",
            "continuation_to_source_line": 127,
            "continuation_fragment": "a pupil of the Bolognese Giuseppe Mazza.",
            "continuation_status": "closed",
            "continued_to_segment_id": "chp-8:08_CHP-8_sec_ii:l126-138",
            "continued_to_source_line": 127,
            "continued_to_statement_id": "st-chp8-p222-ferrerio-pupil",
        }),
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line]


def read_csv(path):
    data = path.read_bytes()
    bom = data.startswith(b"\xef\xbb\xbf")
    text = data.decode("utf-8-sig" if bom else "utf-8")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return reader.fieldnames, list(reader), bom


def csv_bytes(fields, rows, bom):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    data = stream.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" + data) if bom else data


def atomic_write(path, data):
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False, suffix=".tmp") as stream:
        stream.write(data)
        temporary = Path(stream.name)
    temporary.replace(path)


def make_statement(item):
    q = {
        "source_line_start": item["line_start"], "source_line_end": item["line_end"],
        "printed_page": 221, "pdf_physical_page": 23, "claim": item["claim"],
        "speaker": item["speaker"], "text_layer": "body",
        "qualification": item["qualification"],
        "mentioned_candidate_ids": item["mentioned"],
        "relation_candidate": item["relation"],
        "relation_candidate_note": item["note"],
    }
    q.update(item["extra"])
    return {
        "statement_id": item["statement_id"], "segment_id": SEGMENT_ID,
        "subject_candidate_id": item["subject"], "object_candidate_id": item["object"],
        "predicate": item["predicate"], "qualifiers": q,
        "original_quote": item["quote"], "origin": "book", "source_file": SOURCE_REL,
    }


def verify_inputs():
    for path, expected in EXPECTED_HASHES.items():
        actual = sha(path.read_bytes())
        if actual != expected:
            raise SystemExit(f"input changed: {path.relative_to(ROOT)} expected={expected} actual={actual}")
    segments = {r["segment_id"]: r for r in read_jsonl(SEGMENTS)}
    if SEGMENT_ID not in segments or segments[SEGMENT_ID].get("sha256") != SEGMENT_SHA:
        raise SystemExit("S0 segment identity or hash changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    for item in NEW_ROWS:
        excerpt = "\n".join(source_lines[item["line_start"] - 1:item["line_end"]])
        if item["quote"] not in excerpt:
            raise SystemExit(f"quote is not an exact excerpt in its source lines: {item['statement_id']}")


def plan():
    statement_rows = read_jsonl(STATEMENTS)
    candidate_fields, candidate_rows, candidate_bom = read_csv(CANDIDATES)
    mention_fields, mention_rows, mention_bom = read_csv(MENTIONS)
    by_id = {r["statement_id"]: r for r in statement_rows}
    target_ids = set(OLD_NOTES) | {
        "st-chp8-p221-decoration-completed-1695",
        "st-chp8-p221-ruffo-commissioning-in-resident-towns",
    }
    unset = {
        r["statement_id"] for r in statement_rows
        if r.get("segment_id") == SEGMENT_ID and "relation_candidate" not in r.get("qualifiers", {})
    }
    if unset != target_ids:
        raise SystemExit(f"unexpected p.221 unset statements: {sorted(unset)} expected={sorted(target_ids)}")
    if len(target_ids) != 13 or not target_ids <= by_id.keys():
        raise SystemExit("expected p.221 source statements changed")
    new_ids = {x["statement_id"] for x in NEW_ROWS}
    if len(new_ids) != len(NEW_ROWS) or new_ids & by_id.keys():
        raise SystemExit("new statement IDs collide")
    linked_new_ids = set().union(*[set(x) for x in LINKS.values()])
    if linked_new_ids != new_ids:
        raise SystemExit(f"new statement link coverage differs: unlinked={sorted(new_ids-linked_new_ids)} extra={sorted(linked_new_ids-new_ids)}")

    candidate_by_id = {r["candidate_id"]: r for r in candidate_rows}
    max_candidate = max(int(r["candidate_id"].split("-")[1]) for r in candidate_rows)
    if max_candidate != 12066:
        raise SystemExit(f"candidate sequence changed: max={max_candidate}")
    expected_candidates = {
        "cand-1024": ("work", "Ferrerio, Andrea", "Vigilance"),
        "cand-1580": ("place", "Mattei, Tommaso", "Archbishop's Palace, Ferrara"),
        "cand-1638": ("work", "Melanconici, Niccolò", "David with the Head of Goliath"),
        "cand-2306": ("place", "Ruffo, Cardinal Tommaso", "Archbishop's Palace, Ferrara"),
        "cand-2307": ("", "Ruffo, Cardinal Tommaso", "collection"),
    }
    for cid, state in expected_candidates.items():
        r = candidate_by_id.get(cid)
        if not r or (r.get("suggested_type"), r.get("canonical_name"), r.get("sub_entry")) != state:
            raise SystemExit(f"candidate state changed: {cid}")
    candidate_specs = [
        ("cand-12067", "Frescoes at Santa Maria Maggiore undertaken by Niccolò Melanconici",
         "work", 113, "An unnamed work group in the church commission; individual fresco titles and number are not supplied."),
        ("cand-12068", "Artists from all the schools of Italy considered for Santa Maria Maggiore",
         "", 115, "A generic, unnamed artist group in the Governors' commissioning aim; no school members or completed hiring list is given."),
        ("cand-12069", "Men in other small towns helping to break provincial cultural isolation",
         "", 115, "A source-bounded group described by its setting and activity; Haskell names Ruffo as one example but does not enumerate members."),
        ("cand-12070", "Cultural isolation of the Italian provinces",
         "term", 115, "Haskell's description of a provincial cultural condition; the text supplies no metric or bounded membership."),
        ("cand-12071", "Unnamed Pope served by Tommaso Ruffo as maestro de camera",
         "person", 118, "The text identifies the role-holder only as 'the Pope'; do not equate this person with Innocent XII."),
        ("cand-12072", "Leading Italian artists outside Venice whose works Ruffo could seek",
         "", 122, "An open artist group in Haskell's summary; members are not enumerated and Venice is stated as the notable exception."),
        ("cand-12073", "Paintings Ruffo commissioned in most towns where he resided",
         "", 123, "An unspecified group of paintings; Haskell does not enumerate works or towns."),
        ("cand-12074", "White stone stairway in the Archbishop's Palace of Ferrara",
         "work", 124, "Architectural work component described as two flights leading to the piano nobile and bending back on one another."),
        ("cand-12075", "Piano nobile of the Archbishop's Palace of Ferrara",
         "place", 124, "Palace floor/space reached by the described stairway; distinct from the palace as a whole."),
        ("cand-12076", "Balustrade of the Archbishop's Palace stairway in Ferrara",
         "work", 124, "Architectural component on which the Statue of Vigilance stood at the halfway mark."),
    ]
    existing_ids = set(candidate_by_id)
    existing_names = {r.get("canonical_name", "").casefold() for r in candidate_rows}
    for cid, name, _typ, _line, _detail in candidate_specs:
        if cid in existing_ids or name.casefold() in existing_names:
            raise SystemExit(f"candidate natural key or ID already exists: {cid}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[111:124])
    mention_specs = [
        ("m-chp8-p221-frescoes", "cand-12067", "the frescoes",
         "Unnamed fresco group Melanconici undertook in Bergamo; no individual fresco title is supplied."),
        ("m-chp8-p221-artists-all-schools", "cand-12068", "artists from all the schools of Italy",
         "Generic artist group sought for the Santa Maria Maggiore decoration; no members are named."),
        ("m-chp8-p221-small-town-figures", "cand-12069", "men who were helping, on however modest a scale",
         "Unnamed source-bounded group; Cardinal Tommaso Ruffo is given as one example."),
        ("m-chp8-p221-cultural-isolation", "cand-12070", "the cultural isolation of the Italian provinces",
         "Abstract condition described by Haskell, not a quantified or bounded entity."),
        ("m-chp8-p221-unnamed-pope", "cand-12071", "the Pope",
         "Unidentified Pope to whom Ruffo served as maestro de camera; not equated with Innocent XII."),
        ("m-chp8-p221-leading-italian-artists", "cand-12072", "most of the leading Italian artists with the notable exception of those in Venice",
         "Open artist group in Haskell's summary; no names or complete membership list are supplied."),
        ("m-chp8-p221-commissioned-paintings-in-towns", "cand-12073", "paintings in most of the towns in which he resided",
         "Open group of paintings commissioned by Ruffo; the source does not enumerate the works or towns."),
        ("m-chp8-p221-white-stone-stairway", "cand-12074", "a white stone stairway",
         "Architectural work component of the Ferrara Archbishop's Palace."),
        ("m-chp8-p221-piano-nobile", "cand-12075", "the' piano nobile",
         "S0 OCR includes an extra apostrophe; the page image reads 'the piano nobile'."),
        ("m-chp8-p221-balustrade", "cand-12076", "the balustrade",
         "Architectural component distinct from the statue and stairway."),
    ]
    existing_mention_ids = {r["mention_id"] for r in mention_rows}
    new_mentions = []
    for mid, cid, surface, note in mention_specs:
        if mid in existing_mention_ids:
            raise SystemExit(f"mention ID exists: {mid}")
        if segment_text.count(surface) != 1:
            raise SystemExit(f"mention surface is absent or ambiguous: {mid}, count={segment_text.count(surface)}")
        start = segment_text.index(surface)
        new_mentions.append({
            "mention_id": mid, "segment_id": SEGMENT_ID, "candidate_id": cid,
            "surface_form": surface, "start_char": str(start),
            "end_char": str(start + len(surface)), "note": note,
        })

    # Split composite source rows while retaining their original quotes and stable IDs.
    for old_id, note in OLD_NOTES.items():
        q = by_id[old_id]["qualifiers"]
        q["relation_candidate"] = False
        q["relation_candidate_note"] = note
        q["linked_statement_ids"] = LINKS[old_id]

    # The two pre-existing atomic statements receive their final classification.
    complete = by_id["st-chp8-p221-decoration-completed-1695"]["qualifiers"]
    complete["relation_candidate"] = True
    complete["relation_candidate_note"] = (
        "The completion event is linked to the Santa Maria Maggiore decoration programme; the 1695 date and approximate interval remain source-reported."
    )
    complete.update({
        "footnote_markers": [1],
        "footnote_link_status": "linked",
        "footnote_segment": "chp-8:08_CHP-8_sec_ii:l372-461",
        "footnote_target_line": 380,
        "footnote_citation_statement_ids": ["st-chp8-p221-n1-pinetti-citation"],
    })

    commissions = by_id["st-chp8-p221-ruffo-commissioning-in-resident-towns"]
    commissions["object_candidate_id"] = "cand-12073"
    commissions["predicate"] = "commissioned_paintings_in_towns_of_residence"
    commissions_q = commissions["qualifiers"]
    commissions_q["relation_candidate"] = True
    commissions_q["relation_candidate_note"] = (
        "The statement concerns an unspecified group of paintings commissioned in most towns Ruffo resided in; it is not the same object as his assembled gallery collection."
    )
    commissions_q["mentioned_candidate_ids"] = ["cand-2304", "cand-12073"]

    # Correct candidate type/name mistakes that the page itself resolves.
    candidate_by_id["cand-1024"]["suggested_type"] = "person"
    candidate_by_id["cand-1580"]["suggested_type"] = "person"
    candidate_by_id["cand-1638"]["canonical_name"] = (
        "David with the Head of Goliath (painting by Niccolò Melanconici)"
    )
    candidate_by_id["cand-1638"]["detail"] = (
        "Haskell describes this painting beneath which Melanconici was allowed to append a signature; the source gives no separate formal title."
    )
    candidate_by_id["cand-2306"]["canonical_name"] = (
        "Archbishop's Palace of Cardinal Tommaso Ruffo in Ferrara"
    )
    candidate_by_id["cand-2306"]["detail"] = (
        "The palace identified by Haskell as Ruffo's Ferrara gallery location; a later note gives the name Palazzo Vescovale di Ferrara. It is distinct from Ruffo's Roman residence."
    )
    candidate_by_id["cand-2307"]["canonical_name"] = (
        "Cardinal Tommaso Ruffo's picture collection"
    )
    candidate_by_id["cand-2307"]["detail"] = (
        "The collection gathered in Ferrara and kept in Ruffo's Archbishop's Palace. The current taxonomy has no collection type, so the candidate remains untyped pending S3."
    )

    for item in NEW_ROWS:
        statement_rows.append(make_statement(item))
    candidate_rows.extend({
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": typ, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L{line}",
    } for cid, name, typ, line, detail in candidate_specs)
    mention_rows.extend(new_mentions)

    # Move the p.220 arrival continuation to the approval atom that closes it.
    p220_arrival = by_id["st-chp8-p220-abraham-picture-arrives-quickly"]["qualifiers"]
    if p220_arrival.get("continued_to_statement_id") != "st-chp8-p221-melanconici-commission":
        raise SystemExit("p.220 arrival continuation target changed")
    p220_arrival["continued_to_statement_id"] = "st-chp8-p221-abraham-picture-approved"
    p220_arrival["continuation_fragment"] = "and met with approval"
    p221_commission_q = by_id["st-chp8-p221-melanconici-commission"]["qualifiers"]
    for key in ("continued_from_segment_id", "continued_from_source_line",
                "continued_from_statement_id", "continuation_status", "continuation_fragment"):
        p221_commission_q.pop(key, None)

    # Move the p.221 -> p.222 continuation to the Ferrerio artist credit.
    palace_q = by_id["st-chp8-p221-archbishop-palace-and-vigilance-statue-open"]["qualifiers"]
    for key in ("continuation_to_segment_id", "continuation_to_source_line", "continuation_fragment",
                "continuation_status", "continued_to_segment_id", "continued_to_source_line",
                "continued_to_statement_id"):
        palace_q.pop(key, None)
    p222_ferrerio = by_id["st-chp8-p222-ferrerio-pupil"]["qualifiers"]
    if p222_ferrerio.get("continued_from_statement_id") != "st-chp8-p221-archbishop-palace-and-vigilance-statue-open":
        raise SystemExit("p.222 Ferrerio continuation source changed")
    p222_ferrerio["continued_from_segment_id"] = SEGMENT_ID
    p222_ferrerio["continued_from_source_line"] = 124
    p222_ferrerio["continued_from_statement_id"] = "st-chp8-p221-ferrerio-sculptor-of-vigilance"

    # The Moroni footnote refers to the whole career outline; keep its source links atomic.
    note2 = by_id["st-chp8-p221-n2-moroni-citation"]["qualifiers"]
    note2["linked_body_statement_ids"] = [
        "st-chp8-p221-ruffo-born-in-naples",
        "st-chp8-p221-ruffo-shares-family-with-don-antonio",
        "st-chp8-p221-ruffo-enters-church",
        "st-chp8-p221-innocent-xii-appoints-vice-legate",
        "st-chp8-p221-ruffo-inquisitor-in-malta",
        "st-chp8-p221-ruffo-nunzio-in-tuscany",
        "st-chp8-p221-ruffo-maestro-de-camera-to-pope",
        "st-chp8-p221-ruffo-cardinalate-1706",
        "st-chp8-p221-ruffo-returns-as-legate-to-ravenna",
        "st-chp8-p221-ruffo-legate-in-ferrara-from-1710",
        "st-chp8-p221-ruffo-ferrara-connection-close",
        "st-chp8-p221-ruffo-archbishop-in-ferrara-1717-1738",
        "st-chp8-p221-ruffo-bologna-interval-1721-1727",
        "st-chp8-p221-ruffo-lives-in-rome-palace",
        "st-chp8-p221-rome-palace-opposite-trevi-fountain",
        "st-chp8-p221-ruffo-buys-palace-from-cibo-family",
        "st-chp8-p221-ruffo-dies-in-palace",
    ]

    statement_bytes = (
        "\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in statement_rows) + "\n"
    ).encode("utf-8")
    candidate_bytes = csv_bytes(candidate_fields, candidate_rows, candidate_bom)
    mention_bytes = csv_bytes(mention_fields, mention_rows, mention_bom)
    page_rows = [r for r in statement_rows if r.get("segment_id") == SEGMENT_ID]
    summary = {
        "existing_rows_finalized": len(target_ids),
        "new_statements": len(NEW_ROWS),
        "new_true": sum(x["relation"] for x in NEW_ROWS),
        "new_false": sum(not x["relation"] for x in NEW_ROWS),
        "new_source_candidates": len(candidate_specs),
        "new_mentions": len(new_mentions),
        "candidate_types_corrected": 2,
        "candidate_names_or_details_corrected": 3,
        "p221_final_statements": len(page_rows),
        "p221_final_true": sum(r["qualifiers"].get("relation_candidate") is True for r in page_rows),
        "p221_final_false": sum(r["qualifiers"].get("relation_candidate") is False for r in page_rows),
        "p221_final_unset": sum("relation_candidate" not in r.get("qualifiers", {}) for r in page_rows),
    }
    return statement_bytes, candidate_bytes, mention_bytes, summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write guarded plan; default dry-run")
    args = parser.parse_args()
    verify_inputs()
    statements_out, candidates_out, mentions_out, summary = plan()
    print(json.dumps({"mode": "apply" if args.apply else "dry-run", **summary},
                     ensure_ascii=False, indent=2))
    if not args.apply:
        return
    verify_inputs()
    output_map = {STATEMENTS: statements_out, CANDIDATES: candidates_out, MENTIONS: mentions_out}
    for path in output_map:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            if backup.read_bytes() != path.read_bytes():
                raise SystemExit(f"existing backup differs: {backup.name}")
        else:
            shutil.copy2(path, backup)
        if sha(backup.read_bytes()) != EXPECTED_HASHES[path]:
            raise SystemExit(f"backup hash mismatch: {backup.name}")
    for path, data in output_map.items():
        atomic_write(path, data)
    print("written_sha256=" + json.dumps(
        {path.name: sha(path.read_bytes()) for path in output_map}, ensure_ascii=False))


if __name__ == "__main__":
    main()
