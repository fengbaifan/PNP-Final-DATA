"""Guarded S2 semantic review for printed p.222, body lines 127-138."""
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
PAGE_IMAGE = ROOT / "scripts" / ".tmp_s2_chp8_p222_review.png"
NEXT_PAGE_IMAGE = ROOT / "scripts" / ".tmp_s2_chp8_p223_review.png"
SEGMENT_ID = "chp-8:08_CHP-8_sec_ii:l126-138"
SEGMENT_SHA = "d33e574b0f519d4de385bb3ed6c7dbe5803124f72c2456c86ee64c546919668d"
BACKUP_SUFFIX = ".bak-s2-chp8-p222-l126-138-semantic-review-20261014"
EXPECTED_HASHES = {
    STATEMENTS: "c4ca51ab9e29c4586b63698e4090d8a903d580d60c5c7ac7613afedbfe039fbb",
    CANDIDATES: "de932dd84ac36b0cc5929fad7e9e55fa25ca469b5c577417c0a2ffe112b21b38",
    MENTIONS: "5c98a2687169365dfa43f7d81332705971370890e76cd1e59721c24e30f652c6",
    COVERAGE: "6207ec3734deacfe3e02ec341c3a558440f7273ad4f9c2c964ad94ab2710fc34",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    PDF: "cb11451ac726f37ed5badf21a569af88f790f858f1c39eb63f2efb58a0fe4ac3",
    PAGE_IMAGE: "49a923028c46be0a8227185f5c9782471015f58e04b35e975cfdc7830309fa0f",
    NEXT_PAGE_IMAGE: "53e868519a85851c4f7e264695975594b6bcdb546ce2d25f2b690ffad4c43605",
}

OLD_NOTES = {
    "st-chp8-p222-bigari-ceiling-fresco":
        "This combines Bigari's career characterization, the fresco, its allegorical subject, its provincial imagery, and Ruffo's service context. These claims are separated below; the artist and fresco endpoints are corrected.",
    "st-chp8-p222-crespi-creti-style-comparison":
        "This combines Haskell's stylistic description of two paintings with a qualified comparison between Crespi and Creti and an inference about Ruffo's taste. The descriptive and interpretive claims are separated below.",
    "st-chp8-p222-crespi-four-works":
        "This combines the source of Ruffo's modern pictures, Crespi's representation by four works, and the two named commissions. These collection and commission claims are separated below.",
    "st-chp8-p222-italian-masters-in-ruffo-collection":
        "This combines works attributed to a list of Italian masters with additional works by Rubens and Van Dyck. The source preserves attribution language and an incomplete inventory.",
    "st-chp8-p222-n4-pareja-exhibition":
        "This combines the inventory wording describing the portrait with its loan to the S. Salvatore in Lauro exhibition. These are separated below and remain attributed to Haskell's report of the inventory.",
    "st-chp8-p222-n4-pareja-museum-and-hamilton":
        "This combines the portrait's reported later museum location with its earlier presence in Sir William Hamilton's collection. The two location/collection claims are separated below.",
    "st-chp8-p222-pareja-portrait-to-rome-exhibition":
        "This combines Haskell's superlative assessment, the portrait attribution and sitter, and Ruffo's 1704 exhibition loan. These claims are separated below; the ranking remains Haskell's judgment.",
    "st-chp8-p222-ruffo-commissioned-two-crespi-works":
        "This combines two separate Crespi paintings commissioned during Ruffo's Ferrara legateship. Each named work is recorded as its own commission.",
    "st-chp8-p222-ruffo-setting-and-gallery":
        "This combines Haskell's description of the setting, Ruffo's collaborative design, the already recorded collection location, and a retrospective assessment. The design and evaluative claims are separated below.",
    "st-chp8-p222-staircase-stucco-medallions":
        "This combines Ferrerio's design credit, the six papal medallions and their stated beneficiaries, Innocent XII's patronage of Ruffo, and the separate Clement XI relief. These are separated below.",
}

LINKS = {
    "st-chp8-p222-bigari-ceiling-fresco": [
        "st-chp8-p222-bigari-known-for-architectural-fantasies",
        "st-chp8-p222-bigari-paints-catholic-religion-fresco",
        "st-chp8-p222-fresco-represents-catholic-religion-through-papacy",
        "st-chp8-p222-fresco-depicts-three-provinces",
        "st-chp8-p222-ruffo-principally-served-three-cities",
    ],
    "st-chp8-p222-crespi-creti-style-comparison": [
        "st-chp8-p222-religious-themes-subdued-romanticism",
        "st-chp8-p222-creti-crespi-counterpart-and-ruffo-taste",
    ],
    "st-chp8-p222-crespi-four-works": [
        "st-chp8-p222-ruffo-modern-pictures-from-bologna",
        "st-chp8-p222-crespi-four-works-in-collection",
        "st-chp8-p222-ruffo-commissioned-abigail-giving-presents",
        "st-chp8-p222-ruffo-commissioned-finding-of-moses",
    ],
    "st-chp8-p222-italian-masters-in-ruffo-collection": [
        "st-chp8-p222-collection-holds-works-attributed-to-italian-masters",
        "st-chp8-p222-collection-holds-works-by-rubens-and-van-dyck",
    ],
    "st-chp8-p222-n4-pareja-exhibition": [
        "st-chp8-p222-n4-inventory-portrait-of-velasquez-servant",
        "st-chp8-p222-n4-portrait-lent-to-salvatore-exhibition",
    ],
    "st-chp8-p222-n4-pareja-museum-and-hamilton": [
        "st-chp8-p222-n4-portrait-at-metropolitan-museum",
        "st-chp8-p222-n4-portrait-in-hamilton-collection",
    ],
    "st-chp8-p222-pareja-portrait-to-rome-exhibition": [
        "st-chp8-p222-pareja-portrait-by-velasquez",
        "st-chp8-p222-ruffo-sends-pareja-portrait-to-rome-exhibition",
        "st-chp8-p222-pareja-portrait-most-remarkable-assessment",
    ],
    "st-chp8-p222-ruffo-commissioned-two-crespi-works": [
        "st-chp8-p222-ruffo-commissioned-abigail-giving-presents",
        "st-chp8-p222-ruffo-commissioned-finding-of-moses",
    ],
    "st-chp8-p222-ruffo-setting-and-gallery": [
        "st-chp8-p222-ruffo-designed-palace-setting-collaboratively",
        "st-chp8-p222-haskell-assessed-setting-and-collection",
    ],
    "st-chp8-p222-staircase-stucco-medallions": [
        "st-chp8-p222-ferrerio-designed-staircase-stucco",
        "st-chp8-p222-stucco-includes-six-papal-medallions",
        "st-chp8-p222-six-popes-benefited-ferrara-or-legate",
        "st-chp8-p222-innocent-xii-patron-of-ruffo",
        "st-chp8-p222-clement-xi-medallion-on-top-floor",
    ],
}


def row(statement_id, subject, object_, predicate, lines, claim, quote, note, *,
        relation=True, qualification=None, mentioned=None, speaker="Haskell", extra=None):
    return {
        "statement_id": statement_id, "subject": subject, "object": object_,
        "predicate": predicate, "line_start": lines[0], "line_end": lines[1],
        "claim": claim, "quote": quote, "note": note, "relation": relation,
        "qualification": qualification or
            "Preserve Haskell's attribution and the source's stated limits; do not infer a painting identity or a complete collection inventory.",
        "mentioned": mentioned or [], "speaker": speaker, "extra": extra or {},
    }


NEW_ROWS = [
    row("st-chp8-p222-ferrerio-designed-staircase-stucco", "cand-1024", "cand-7704",
        "designed_staircase_stucco_decoration", (127, 127),
        "Andrea Ferrerio designed the rich stucco decoration on the Archbishop's Palace staircase wall.",
        "The same artist designed the rich stucco decoration of the staircase wall",
        "The same artist resolves to Andrea Ferrerio, the sculptor named on p.221; the stucco work is distinct from the staircase and ceiling fresco.",
        mentioned=["cand-1024", "cand-7704"],
        extra={
            "footnote_markers": [1], "footnote_link_status": "linked",
            "footnote_segment": "chp-8:08_CHP-8_sec_ii:l372-461",
            "footnote_target_line": 382,
            "footnote_citation_statement_ids": ["st-chp8-p222-n1-manuscript-citation"],
        }),
    row("st-chp8-p222-stucco-includes-six-papal-medallions", "cand-7704", "cand-12077",
        "stucco_decoration_includes_papal_medallion_group", (127, 128),
        "The staircase stucco included medallions of six popes who had benefited Ferrara or its Legate.",
        "medallions of the six popes who had in some way benefited the City of Ferrara or her Legate",
        "The page names only Innocent XII within this six-pope group; the identities of the other five are not supplied.",
        mentioned=["cand-7704", "cand-12077", "cand-1017", "cand-2304"]),
    row("st-chp8-p222-six-popes-benefited-ferrara-or-legate", "cand-12077", "cand-1017",
        "reported_benefit_to_ferrara_or_its_legate", (127, 128),
        "Haskell says the six popes represented in the staircase medallions had in some way benefited Ferrara or its Legate.",
        "the six popes who had in some way benefited the City of Ferrara or her Legate",
        "The source does not specify which pope benefited the city and which benefited its Legate, or identify five members of the group.",
        mentioned=["cand-12077", "cand-1017", "cand-2304"]),
    row("st-chp8-p222-innocent-xii-patron-of-ruffo", "cand-1929", "cand-2304",
        "served_as_patron_of", (127, 128),
        "Haskell identifies Pope Innocent XII as Ruffo's patron.",
        "culminating in Innocent\nXII, Russo’s own patron",
        "The page image reads Ruffo; preserve the reported patron relationship without inferring its exact institutional form.",
        mentioned=["cand-1929", "cand-2304"],
        extra={"ocr_corrections": [{
            "source_file": SOURCE_REL, "source_line": 128, "ocr": "Russo’s", "print": "Ruffo’s",
            "basis": "CHP-8.pdf physical page 24."
        }]}),
    row("st-chp8-p222-clement-xi-medallion-on-top-floor", "cand-12078", "cand-0022",
        "medallion_depicts_reigning_pope", (128, 128),
        "A full-relief medallion on the palace's top floor depicted the reigning Pope, Clement XI.",
        "On the top floor was another medallion in full relief of the reigning Pope, Clement XL",
        "The page image reads Clement XI; this is a separate medallion from the preceding six-pope series.",
        mentioned=["cand-12078", "cand-0022", "cand-7704"],
        extra={"ocr_corrections": [{
            "source_file": SOURCE_REL, "source_line": 128, "ocr": "Clement XL", "print": "Clement XI",
            "basis": "CHP-8.pdf physical page 24."
        }]}),
    row("st-chp8-p222-bigari-paints-catholic-religion-fresco", "cand-0374", "cand-0375",
        "painted_ceiling_fresco", (129, 129),
        "The Bolognese painter Vittorio Bigari painted a ceiling fresco of the Catholic Religion.",
        "Vittorio Bigari, known primarily for his later architectural fantasies, painted a fresco of the Catholic Religion",
        "Candidate cand-0375 is the fresco work; cand-0374 is the painter. The source gives no separate formal title.",
        mentioned=["cand-0374", "cand-0375", "cand-7708"],
        extra={"footnote_markers": [1], "footnote_link_status": "linked",
               "footnote_segment": "chp-8:08_CHP-8_sec_ii:l372-461", "footnote_target_line": 382,
               "footnote_citation_statement_ids": ["st-chp8-p222-n1-manuscript-citation"]}),
    row("st-chp8-p222-bigari-known-for-architectural-fantasies", "cand-0374", None,
        "haskell_characterized_bigari_as_known_for_later_architectural_fantasies", (129, 129),
        "Haskell says Bigari was known primarily for his later architectural fantasies.",
        "Vittorio Bigari, known primarily for his later architectural fantasies",
        "This is Haskell's characterization of Bigari's reputation, not a relation to a separately identified work.",
        relation=False, mentioned=["cand-0374"]),
    row("st-chp8-p222-fresco-represents-catholic-religion-through-papacy", "cand-0375", "cand-7708",
        "fresco_represents_catholic_religion_through_papacy", (129, 129),
        "The fresco represented the Catholic Religion through the Papacy.",
        "of the Catholic Religion, represented by the Papacy",
        "The Catholic Religion is an allegorical subject and the Papacy is a distinct institution in the taxonomy.",
        mentioned=["cand-0375", "cand-7708", "cand-4223"]),
    row("st-chp8-p222-fresco-depicts-three-provinces", "cand-0375", "cand-12079",
        "fresco_depicts_three_provinces_symbolically", (129, 130),
        "Bigari's fresco showed the provinces of Ravenna, Bologna, and Ferrara symbolically in heroic dress.",
        "presiding over the provinces of\nRavenna, Bologna and Ferrara shown symbolically in heroic dress",
        "The group represents the three named cities in the fresco; the source does not identify separate personifications.",
        mentioned=["cand-0375", "cand-12079", "cand-7697", "cand-3398", "cand-1017"]),
    row("st-chp8-p222-ruffo-principally-served-three-cities", "cand-2304", "cand-12079",
        "principally_served_in_three_cities", (130, 130),
        "Haskell identifies Ravenna, Bologna, and Ferrara as the three cities where Ruffo principally served.",
        "the three cities where Russo had principally served",
        "The page image reads Ruffo; the city group is limited to these three places in this passage.",
        mentioned=["cand-2304", "cand-12079", "cand-7697", "cand-3398", "cand-1017"],
        extra={"ocr_corrections": [{
            "source_file": SOURCE_REL, "source_line": 130, "ocr": "Russo", "print": "Ruffo",
            "basis": "CHP-8.pdf physical page 24."
        }]}),
    row("st-chp8-p222-ruffo-designed-palace-setting-collaboratively", "cand-2304", "cand-2306",
        "designed_palace_setting_with_architect_and_sculptor", (130, 130),
        "Haskell says Ruffo carefully designed the palace setting in collaboration with his architect and sculptor.",
        "carefully designed by the Cardinal in collaboration with his architect and sculptor",
        "The Cardinal resolves to Ruffo; the adjacent account identifies his architect as Tommaso Mattei and sculptor as Andrea Ferrerio.",
        mentioned=["cand-2304", "cand-2306", "cand-1580", "cand-1024"],
        extra={"footnote_markers": [1], "footnote_link_status": "linked",
               "footnote_segment": "chp-8:08_CHP-8_sec_ii:l372-461", "footnote_target_line": 382,
               "footnote_citation_statement_ids": ["st-chp8-p222-n1-manuscript-citation"]}),
    row("st-chp8-p222-haskell-assessed-setting-and-collection", "cand-2307", None,
        "haskell_assessed_setting_and_collection_positively", (130, 130),
        "Haskell calls the setting grandiose and says Ruffo's collection impressed contemporaries and still seems remarkably varied and impressive in retrospect.",
        "in this grandiose setting, carefully designed by the Cardinal in collaboration with his architect and sculptor, that Russo kept a collection of paintings which aroused the enthusiasm of his contemporaries and which to us in retrospect still seems remarkably varied and impressive",
        "This preserves Haskell's evaluative language; the collection's location in the Archbishop's Palace is already recorded on p.221.",
        relation=False, mentioned=["cand-2304", "cand-2306", "cand-2307"],
        extra={"ocr_corrections": [
            {"source_file": SOURCE_REL, "source_line": 130, "ocr": "Russo", "print": "Ruffo",
             "basis": "CHP-8.pdf physical page 24."},
            {"source_file": SOURCE_REL, "source_line": 130, "ocr": "rctrospect", "print": "retrospect",
             "basis": "CHP-8.pdf physical page 24."},
        ]}),
    row("st-chp8-p222-collection-holds-works-attributed-to-italian-masters", "cand-2307", "cand-12080",
        "collection_contains_works_attributed_to_italian_masters", (131, 132),
        "Haskell says Ruffo's collection included works attributed to Giorgione, Titian, Bassano, Correggio, Raphael, Parmigianino, Caravaggio, the Carracci, Guido Reni, and Guercino.",
        "Russo owned a number of works attributed to the great Italianjmasters of the sixteenth and seventeenth centuries—Giorgione, Titian, Bassano, Correggio, Raphael,\nParmigianino, Caravaggio, the Carracci, Guido Reni and Guercino",
        "The attribution language is retained; individual work titles and a complete inventory are not supplied.",
        mentioned=["cand-2307", "cand-12080", "cand-1188", "cand-2630", "cand-0257", "cand-0852",
                   "cand-2098", "cand-1839", "cand-0544", "cand-4318", "cand-2124", "cand-1258"],
        extra={"footnote_markers": [2], "footnote_link_status": "linked",
               "footnote_segment": "chp-8:08_CHP-8_sec_ii:l372-461", "footnote_target_line": 383,
               "footnote_citation_statement_ids": ["st-chp8-p222-n2-agnelli-citation"],
               "qualification_terms": ["a number of works", "attributed to"],
               "ocr_corrections": [
                   {"source_file": SOURCE_REL, "source_line": 131, "ocr": "Russo", "print": "Ruffo",
                    "basis": "CHP-8.pdf physical page 24."},
                   {"source_file": SOURCE_REL, "source_line": 131, "ocr": "Italianjmasters", "print": "Italian masters",
                    "basis": "CHP-8.pdf physical page 24."}
               ]}),
    row("st-chp8-p222-collection-holds-works-by-rubens-and-van-dyck", "cand-2307", "cand-12081",
        "collection_contains_works_by_northern_masters", (132, 132),
        "Haskell says Ruffo's collection also included works by Rubens and Van Dyck that were less familiar in Italian collections.",
        "as well as others by Rubens and Van Dyck less familiar in Italian collections",
        "The passage gives no titles or count for these works.",
        mentioned=["cand-2307", "cand-12081", "cand-2293", "cand-2155"],
        extra={"footnote_markers": [2], "footnote_link_status": "linked",
               "footnote_segment": "chp-8:08_CHP-8_sec_ii:l372-461", "footnote_target_line": 383,
               "footnote_citation_statement_ids": ["st-chp8-p222-n2-agnelli-citation"]}),
    row("st-chp8-p222-ruffo-modern-pictures-from-bologna", "cand-2307", "cand-3398",
        "modern_collection_pictures_came_mostly_from_city", (134, 134),
        "Haskell says most of Ruffo's modern pictures came from Bologna.",
        "The bulk of his modern pictures came from Bologna",
        "This is a source-level statement about the modern pictures, not a complete provenance list.",
        mentioned=["cand-2307", "cand-3398"]),
    row("st-chp8-p222-crespi-four-works-in-collection", "cand-2307", "cand-7707",
        "collection_included_four_works_by_crespi", (134, 134),
        "Crespi was represented in Ruffo's collection by four works.",
        "Crespi was represented by four works",
        "The four-work group is distinct from the two individually named paintings and from the unresolved Crespi index subentry.",
        mentioned=["cand-2307", "cand-7707", "cand-0871"],
        extra={"quantity": 4, "footnote_markers": [5], "footnote_link_status": "linked",
               "footnote_segment": "chp-8:08_CHP-8_sec_ii:l372-461", "footnote_target_line": 385,
               "footnote_citation_statement_ids": [
                   "st-chp8-p222-n5-luigi-crespi-citation",
                   "st-chp8-p222-n5-santangelo-citation",
                   "st-chp8-p222-n5-zanotti-citation"]}),
    row("st-chp8-p222-ruffo-commissioned-abigail-giving-presents", "cand-2304", "cand-7719",
        "commissioned_painting_during_ferrara_legateship", (134, 135),
        "Ruffo commissioned Crespi's Abigail giving Presents to David during his Ferrara legateship.",
        "two of which were commissioned during Russo’s legateship in the city:\nAbigail giving Presenti to David",
        "The page image reads Ruffo and Presents; the painting is one of Crespi's four reported works.",
        mentioned=["cand-2304", "cand-7719", "cand-0871", "cand-1017"],
        extra={"ocr_corrections": [
            {"source_file": SOURCE_REL, "source_line": 134, "ocr": "Russo’s", "print": "Ruffo’s",
             "basis": "CHP-8.pdf physical page 24."},
            {"source_file": SOURCE_REL, "source_line": 135, "ocr": "Presenti", "print": "Presents",
             "basis": "CHP-8.pdf physical page 24."},
        ], "footnote_markers": [5], "footnote_link_status": "linked",
               "footnote_segment": "chp-8:08_CHP-8_sec_ii:l372-461", "footnote_target_line": 385,
               "footnote_citation_statement_ids": [
                   "st-chp8-p222-n5-luigi-crespi-citation",
                   "st-chp8-p222-n5-santangelo-citation",
                   "st-chp8-p222-n5-zanotti-citation"]}),
    row("st-chp8-p222-ruffo-commissioned-finding-of-moses", "cand-2304", "cand-7720",
        "commissioned_painting_during_ferrara_legateship", (134, 135),
        "Ruffo commissioned Crespi's The Finding of Moses during his Ferrara legateship.",
        "two of which were commissioned during Russo’s legateship in the city:\nAbigail giving Presenti to David and The Finding of Moses",
        "The painting is one of Crespi's four reported works; its identity remains separate from the unresolved index candidate.",
        mentioned=["cand-2304", "cand-7720", "cand-0871", "cand-1017"],
        extra={"ocr_corrections": [{
            "source_file": SOURCE_REL, "source_line": 134, "ocr": "Russo’s", "print": "Ruffo’s",
            "basis": "CHP-8.pdf physical page 24."
        }], "footnote_markers": [5], "footnote_link_status": "linked",
               "footnote_segment": "chp-8:08_CHP-8_sec_ii:l372-461", "footnote_target_line": 385,
               "footnote_citation_statement_ids": [
                   "st-chp8-p222-n5-luigi-crespi-citation",
                   "st-chp8-p222-n5-santangelo-citation",
                   "st-chp8-p222-n5-zanotti-citation"]}),
    row("st-chp8-p222-religious-themes-subdued-romanticism", "cand-7707", None,
        "haskell_described_religious_themes_as_subdued_and_tender", (135, 135),
        "Haskell describes the religious themes in Crespi's two paintings as subdued and tenderly romantic.",
        "Both these religious themes are treated in a spirit of subdued and tender romanticism",
        "This is Haskell's characterization of the paintings, not an independently assessed stylistic fact.",
        relation=False, mentioned=["cand-7707", "cand-7719", "cand-7720"]),
    row("st-chp8-p222-creti-crespi-counterpart-and-ruffo-taste", "cand-2304", "cand-0889",
        "haskell_inferred_style_affinity_between_ruffo_and_creti", (135, 135),
        "Haskell suggests this quality may have appealed to Ruffo in Donato Creti, whom he calls Crespi's more aristocratic counterpart in depicting such themes.",
        "it was perhaps this quality that Russo sound so congenial in Crespi’s more aristocratic counterpart in the depiction of such subjects—Donato Creti",
        "The 'perhaps' marks Haskell's inference; the page image reads Ruffo and 'found'.",
        relation=False, mentioned=["cand-2304", "cand-0889", "cand-0871", "cand-7719", "cand-7720"],
        extra={"qualification_terms": ["perhaps", "more aristocratic counterpart"],
               "ocr_corrections": [
                   {"source_file": SOURCE_REL, "source_line": 135, "ocr": "Russo", "print": "Ruffo",
                    "basis": "CHP-8.pdf physical page 24."},
                   {"source_file": SOURCE_REL, "source_line": 135, "ocr": "sound", "print": "found",
                    "basis": "CHP-8.pdf physical page 24."},
               ]}),
    row("st-chp8-p222-pareja-portrait-by-velasquez", "cand-2709", "cand-2714",
        "painted_portrait_of_juan_de_pareja", (133, 133),
        "Haskell identifies the picture in Ruffo's collection as Velasquez's portrait of his servant Juan de Pareja.",
        "Velasquez’s portrait of his servant Juan de Pareja",
        "The source's attribution is preserved; no independent authentication is claimed.",
        mentioned=["cand-2709", "cand-2714", "cand-1834", "cand-2307"],
        extra={"footnote_markers": [4], "footnote_link_status": "linked",
               "footnote_segment": SEGMENT_ID, "footnote_target_line": 136,
               "footnote_statement_ids": [
                   "st-chp8-p222-n4-inventory-portrait-of-velasquez-servant",
                   "st-chp8-p222-n4-portrait-lent-to-salvatore-exhibition"]}),
    row("st-chp8-p222-ruffo-sends-pareja-portrait-to-rome-exhibition", "cand-2304", "cand-2714",
        "sent_portrait_to_exhibition_in_rome", (133, 133),
        "Ruffo sent the portrait of Juan de Pareja to an exhibition in Rome in 1704.",
        "which in 1704 he sent to an exhibition in Rome",
        "The source reports the loan; footnote 4 identifies the S. Salvatore in Lauro exhibition and inventory wording.",
        mentioned=["cand-2304", "cand-2714", "cand-1834", "cand-4490", "cand-6051"],
        extra={"date": "1704", "footnote_markers": [4], "footnote_link_status": "linked",
               "footnote_segment": SEGMENT_ID, "footnote_target_line": 136,
               "footnote_statement_ids": [
                   "st-chp8-p222-n4-inventory-portrait-of-velasquez-servant",
                   "st-chp8-p222-n4-portrait-lent-to-salvatore-exhibition"]}),
    row("st-chp8-p222-pareja-portrait-most-remarkable-assessment", "cand-2714", None,
        "haskell_ranked_portrait_as_most_remarkable", (133, 133),
        "Haskell says Velasquez's portrait of Juan de Pareja must have been the most remarkable of Ruffo's seventeenth-century pictures and quotes cosa stupenda.",
        "But the most remarkable of all Russo’s seventeenth-century pictures must have been Velasquez’s portrait of his servant Juan de Pareja, ‘cosa stupenda’",
        "The superlative and quoted phrase are Haskell's reported assessment, not a measured ranking.",
        relation=False, mentioned=["cand-2304", "cand-2714", "cand-1834"],
        extra={"qualification_terms": ["must have been", "cosa stupenda"],
               "ocr_corrections": [{
                   "source_file": SOURCE_REL, "source_line": 133, "ocr": "Russo’s", "print": "Ruffo’s",
                   "basis": "CHP-8.pdf physical page 24."
               }]}),
    row("st-chp8-p222-n4-inventory-portrait-of-velasquez-servant", "cand-2714", "cand-1834",
        "inventory_described_portrait_as_velasquez_servant", (136, 137),
        "The quoted inventory describes the portrait as showing a servant of Diego Velasquez, identified in the body as Juan de Pareja.",
        "The picture ‘11 Ritratto da tre palmi rappresentante un servo che Ri serv.re del S.r Diego Velasquez famoso pitt.re e cosa stupenda’",
        "The inventory's wording is transcribed through Haskell; the OCR corrections are retained and no new sitter identity is inferred beyond the body text.",
        mentioned=["cand-2714", "cand-1834", "cand-2709"],
        speaker="Haskell quoting an inventory",
        extra={"footnote_marker": 4, "printed_page_locator": "p.222 n.4",
               "ocr_corrections": [
                   {"source_file": SOURCE_REL, "source_line": 136, "ocr": "11 Ritratto", "print": "Il Ritratto",
                    "basis": "CHP-8.pdf physical page 24."},
                   {"source_file": SOURCE_REL, "source_line": 136, "ocr": "Ri serv.re", "print": "fu serv.re",
                    "basis": "CHP-8.pdf physical page 24."},
               ]}),
    row("st-chp8-p222-n4-portrait-lent-to-salvatore-exhibition", "cand-2714", "cand-6051",
        "lent_to_s_s_alvatore_exhibition", (136, 137),
        "Haskell says the portrait was among the pictures lent to the 1704 exhibition at S. Salvatore in Lauro.",
        "was among those lent to the exhibition in S. Salvatore in Lauro in 1704",
        "The note identifies the exhibition and venue; it is linked to the body statement that Ruffo sent the portrait to an exhibition in Rome.",
        mentioned=["cand-2714", "cand-6051", "cand-6052"],
        extra={"date": "1704", "footnote_marker": 4, "printed_page_locator": "p.222 n.4"}),
    row("st-chp8-p222-n4-portrait-at-metropolitan-museum", "cand-2714", "cand-7472",
        "reported_later_location_in_museum", (137, 137),
        "Haskell says the portrait was in the Metropolitan Museum at the time of his account.",
        "It is the picture now in the Metropolitan Museum",
        "The word 'now' is relative to Haskell's source-time account.",
        mentioned=["cand-2714", "cand-7472"],
        extra={"footnote_marker": 4, "printed_page_locator": "p.222 n.4"}),
    row("st-chp8-p222-n4-portrait-in-hamilton-collection", "cand-2714", "cand-11490",
        "reported_in_collection_by_1798", (137, 138),
        "Haskell says the portrait had been in Sir William Hamilton's collection in Naples by 1798.",
        "which was in the collection of Sir\nWilliam Hamilton in Naples by 1798.",
        "The collection has no formal title in this passage; the named owner and place remain attached as mentions.",
        mentioned=["cand-2714", "cand-11490", "cand-7714", "cand-1722"],
        extra={"date": "1798", "date_qualifier": "by", "footnote_marker": 4,
               "printed_page_locator": "p.222 n.4"}),
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
        "printed_page": 222, "pdf_physical_page": 24, "claim": item["claim"],
        "speaker": item["speaker"], "text_layer": "body" if item["line_start"] < 136 else "footnote",
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
        "st-chp8-p222-ferrerio-pupil",
        "st-chp8-p222-breval-castigliones",
        "st-chp8-p222-breval-lucretia",
        "st-chp8-p222-breval-masanella",
        "st-chp8-p222-ruffo-fondness-for-creti-open",
    }
    segment_ids = {r["statement_id"] for r in statement_rows if r.get("segment_id") == SEGMENT_ID}
    if segment_ids != target_ids or len(target_ids) != 15:
        raise SystemExit(f"p.222 statement scope changed: {sorted(segment_ids)}")
    new_ids = {x["statement_id"] for x in NEW_ROWS}
    if len(new_ids) != len(NEW_ROWS) or new_ids & by_id.keys():
        raise SystemExit("new statement IDs collide")
    linked_new_ids = set().union(*[set(x) for x in LINKS.values()])
    if linked_new_ids != new_ids:
        raise SystemExit(f"new statement link coverage differs: unlinked={sorted(new_ids-linked_new_ids)} extra={sorted(linked_new_ids-new_ids)}")

    candidate_by_id = {r["candidate_id"]: r for r in candidate_rows}
    max_candidate = max(int(r["candidate_id"].split("-")[1]) for r in candidate_rows)
    if max_candidate != 12076:
        raise SystemExit(f"candidate sequence changed: max={max_candidate}")
    expected_candidates = {
        "cand-0374": ("person", "Bigari, Vittorio", ""),
        "cand-0375": ("person", "Bigari, Vittorio", "work in Archbishop's Palace, Ferrara"),
        "cand-0579": ("person", "Carracci, Annibale", "Lucretia"),
        "cand-2714": ("work", "Velasquez", "portrait of his servant Juan de Pareja"),
    }
    for cid, state in expected_candidates.items():
        r = candidate_by_id.get(cid)
        if not r or (r.get("suggested_type"), r.get("canonical_name"), r.get("sub_entry")) != state:
            raise SystemExit(f"candidate state changed: {cid}")
    candidate_specs = [
        ("cand-12077", "Six popes represented in Ferrara palace staircase medallions as benefactors of the city or its Legate",
         "", 127, "The page names Innocent XII within the six-pope group but does not identify the other five; Clement XI is introduced as a separate additional medallion."),
        ("cand-12078", "Full-relief medallion of Pope Clement XI on the top floor of the Ferrara Archbishop's Palace",
         "work", 128, "A specific papal relief distinct from the six-medallion series and from the whole stucco decoration."),
        ("cand-12079", "Provinces of Ravenna, Bologna and Ferrara represented in Bigari's ceiling fresco",
         "", 130, "A source-bounded group of three cities represented symbolically; it is not a separate political institution."),
        ("cand-12080", "Works attributed to Italian masters in Cardinal Tommaso Ruffo's collection",
         "", 131, "An unspecified group of works attributed to the named sixteenth- and seventeenth-century Italian painters; individual titles are not supplied."),
        ("cand-12081", "Works by Rubens and Van Dyck in Cardinal Tommaso Ruffo's collection",
         "", 132, "An unspecified group of works by the two named artists; number and titles are not supplied."),
    ]
    existing_ids = set(candidate_by_id)
    existing_names = {r.get("canonical_name", "").casefold() for r in candidate_rows}
    for cid, name, _typ, _line, _detail in candidate_specs:
        if cid in existing_ids or name.casefold() in existing_names:
            raise SystemExit(f"candidate natural key or ID already exists: {cid}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[125:138])
    mention_specs = [
        ("m-chp8-p222-six-papal-medallions", "cand-12077",
         "medallions of the six popes who had in some way benefited the City of Ferrara or her Legate",
         "Six popes represented in the staircase stucco; only Innocent XII is named within this group."),
        ("m-chp8-p222-clement-medallion", "cand-12078",
         "another medallion in full relief of the reigning Pope, Clement XL",
         "The page image reads Clement XI; this relief is separate from the preceding six-pope group."),
        ("m-chp8-p222-bigari-fresco", "cand-0375", "a fresco of the Catholic Religion",
         "Vittorio Bigari's ceiling fresco; its allegorical subject is represented by the Papacy."),
        ("m-chp8-p222-three-provinces-in-fresco", "cand-12079",
         "the provinces of\nRavenna, Bologna and Ferrara shown symbolically in heroic dress",
         "The fresco represents the three cities as provinces; no separate political body is named."),
        ("m-chp8-p222-works-attributed-italian-masters", "cand-12080",
         "a number of works attributed to the great Italianjmasters of the sixteenth and seventeenth centuries",
         "The source OCR joins 'Italian' and 'masters'; the printed page separates them."),
        ("m-chp8-p222-works-by-rubens-van-dyck", "cand-12081",
         "others by Rubens and Van Dyck less familiar in Italian collections",
         "Unspecified additional works in Ruffo's collection; the passage gives no titles or count."),
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

    for old_id, note in OLD_NOTES.items():
        q = by_id[old_id]["qualifiers"]
        q["relation_candidate"] = False
        q["relation_candidate_note"] = note
        q["linked_statement_ids"] = LINKS[old_id]
    for sid, note in {
        "st-chp8-p222-ferrerio-pupil":
            "The named pupil relationship is reported directly; the following architectural account begins with footnote 1.",
        "st-chp8-p222-breval-castigliones":
            "The quoted wording is attributed to John Breval by Haskell; it describes four paintings from Ruffo's collection.",
        "st-chp8-p222-breval-lucretia":
            "Breval's quoted description links the Lucretia painting to Hannibal Carache; candidate cand-0579 is corrected to the work, not the painter.",
        "st-chp8-p222-breval-masanella":
            "Breval's quoted description is a work-level relation; the printed [sic] spelling and unresolved sitter identity are retained.",
        "st-chp8-p222-ruffo-fondness-for-creti-open":
            "Haskell reports a direct patron-artist affinity and Ruffo's repeated attendance while Creti worked; the sentence closes on p.223.",
    }.items():
        q = by_id[sid]["qualifiers"]
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note

    # Preserve the direct quotation source and printed-page footnote links.
    for sid in ("st-chp8-p222-breval-castigliones", "st-chp8-p222-breval-lucretia",
                "st-chp8-p222-breval-masanella"):
        q = by_id[sid]["qualifiers"]
        q["footnote_markers"] = [3]
        q["footnote_link_status"] = "linked"
        q["footnote_segment"] = "chp-8:08_CHP-8_sec_ii:l372-461"
        q["footnote_target_line"] = 384
        q["footnote_citation_statement_ids"] = ["st-chp8-p222-n3-breval-citation"]
    by_id["st-chp8-p222-breval-castigliones"]["qualifiers"]["mentioned_candidate_ids"] = [
        "cand-0451", "cand-1017", "cand-0602", "cand-7705", "cand-2307"
    ]
    by_id["st-chp8-p222-breval-lucretia"]["qualifiers"]["mentioned_candidate_ids"] = [
        "cand-0451", "cand-0579", "cand-0576"
    ]
    by_id["st-chp8-p222-breval-masanella"]["qualifiers"]["mentioned_candidate_ids"] = [
        "cand-0451", "cand-7706", "cand-4150"
    ]

    # Correct the Bigari painter/fresco direction while keeping the original composite as a linked record.
    bigari = by_id["st-chp8-p222-bigari-ceiling-fresco"]
    bigari["subject_candidate_id"] = "cand-0374"
    bigari["object_candidate_id"] = "cand-0375"

    # Correct candidate types and labels resolved by this page.
    candidate_by_id["cand-0375"]["suggested_type"] = "work"
    candidate_by_id["cand-0375"]["canonical_name"] = (
        "Ceiling fresco of the Catholic Religion by Vittorio Bigari in Ferrara"
    )
    candidate_by_id["cand-0375"]["detail"] = (
        "The ceiling fresco described on p.222; the Catholic Religion is represented by the Papacy and the provinces of Ravenna, Bologna and Ferrara."
    )
    candidate_by_id["cand-0579"]["suggested_type"] = "work"
    candidate_by_id["cand-0579"]["canonical_name"] = "Lucretia (painting attributed to Annibale Carracci)"
    candidate_by_id["cand-0579"]["detail"] = (
        "Index subentry and Breval's quoted p.222 description identify a Lucretia painting; keep the work distinct from Annibale Carracci as a person."
    )
    candidate_by_id["cand-2714"]["canonical_name"] = "Portrait of Juan de Pareja by Diego Velasquez"
    candidate_by_id["cand-2714"]["detail"] = (
        "The portrait named by Haskell as Velasquez's picture of his servant Juan de Pareja; later note 4 supplies inventory, exhibition, and location information."
    )

    # Rebuild the p.220-223 cross-page destination for the affinity statement.
    fondness = by_id["st-chp8-p222-ruffo-fondness-for-creti-open"]["qualifiers"]
    if fondness.get("continuation_closed_by_statement_id") != "st-chp8-p223-ruffo-affinity-for-creti":
        raise SystemExit("p.223 Creti continuation target changed")
    by_id["st-chp8-p223-ruffo-affinity-for-creti"]["qualifiers"]["continued_from_statement_id"] = (
        "st-chp8-p222-ruffo-fondness-for-creti-open"
    )

    # Update note/body links after decomposing cited claims.
    by_id["st-chp8-p222-n1-manuscript-source"]["qualifiers"]["linked_body_statement_ids"] = [
        "st-chp8-p221-palace-built-for-ruffo",
        "st-chp8-p221-palace-built-by-mattei",
        "st-chp8-p221-palace-adjoins-cathedral",
        "st-chp8-p221-stairway-leads-to-piano-nobile",
        "st-chp8-p221-vigilance-statue-on-balustrade",
        "st-chp8-p221-vigilance-statue-commissioned-by-ruffo",
        "st-chp8-p221-ferrerio-sculptor-of-vigilance",
        "st-chp8-p222-ferrerio-designed-staircase-stucco",
        "st-chp8-p222-stucco-includes-six-papal-medallions",
        "st-chp8-p222-clement-xi-medallion-on-top-floor",
        "st-chp8-p222-bigari-paints-catholic-religion-fresco",
        "st-chp8-p222-ruffo-designed-palace-setting-collaboratively",
        "st-chp8-p221-ruffo-gallery-kept-in-palace",
    ]
    by_id["st-chp8-p222-n2-agnelli-publication"]["qualifiers"]["linked_body_statement_ids"] = [
        "st-chp8-p222-collection-holds-works-attributed-to-italian-masters",
        "st-chp8-p222-collection-holds-works-by-rubens-and-van-dyck",
    ]
    by_id["st-chp8-p222-n2-agnelli-citation"]["qualifiers"]["linked_body_statement_ids"] = [
        "st-chp8-p222-collection-holds-works-attributed-to-italian-masters",
        "st-chp8-p222-collection-holds-works-by-rubens-and-van-dyck",
    ]
    by_id["st-chp8-p222-n4-pareja-exhibition"]["qualifiers"]["linked_body_statement_ids"] = [
        "st-chp8-p222-pareja-portrait-by-velasquez",
        "st-chp8-p222-ruffo-sends-pareja-portrait-to-rome-exhibition",
    ]
    by_id["st-chp8-p222-n4-pareja-museum-and-hamilton"]["qualifiers"]["linked_body_statement_ids"] = [
        "st-chp8-p222-n4-portrait-at-metropolitan-museum",
        "st-chp8-p222-n4-portrait-in-hamilton-collection",
    ]
    by_id["st-chp8-p222-n5-crespi-works-at-museo-palazzo-venezia"]["qualifiers"]["linked_body_statement_ids"] = [
        "st-chp8-p222-crespi-four-works-in-collection",
        "st-chp8-p222-ruffo-commissioned-abigail-giving-presents",
        "st-chp8-p222-ruffo-commissioned-finding-of-moses",
    ]

    statement_rows.extend(make_statement(item) for item in NEW_ROWS)
    candidate_rows.extend({
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": typ, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L{line}",
    } for cid, name, typ, line, detail in candidate_specs)
    mention_rows.extend(new_mentions)

    page_rows = [r for r in statement_rows if r.get("segment_id") == SEGMENT_ID]
    statement_bytes = (
        "\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in statement_rows) + "\n"
    ).encode("utf-8")
    candidate_bytes = csv_bytes(candidate_fields, candidate_rows, candidate_bom)
    mention_bytes = csv_bytes(mention_fields, mention_rows, mention_bom)
    summary = {
        "existing_rows_finalized_or_refined": len(target_ids),
        "new_statements": len(NEW_ROWS),
        "new_true": sum(x["relation"] for x in NEW_ROWS),
        "new_false": sum(not x["relation"] for x in NEW_ROWS),
        "new_source_candidates": len(candidate_specs),
        "new_mentions": len(new_mentions),
        "candidate_types_corrected": 2,
        "candidate_names_or_details_corrected": 3,
        "p222_final_statements": len(page_rows),
        "p222_final_true": sum(r["qualifiers"].get("relation_candidate") is True for r in page_rows),
        "p222_final_false": sum(r["qualifiers"].get("relation_candidate") is False for r in page_rows),
        "p222_final_unset": sum("relation_candidate" not in r.get("qualifiers", {}) for r in page_rows),
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
