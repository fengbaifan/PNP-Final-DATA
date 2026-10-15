"""Guarded S2 semantic review for printed p.219, lines 87-98."""
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
PAGE_IMAGE = ROOT / "scripts" / ".tmp_s2_chp8_p219_review.png"
SEGMENT_ID = "chp-8:08_CHP-8_sec_ii:l86-98"
SEGMENT_SHA = "d588ce2a605af3756d243d0a62602eb45490b090f6ca5e465ebb2e82c2b113df"
BACKUP_SUFFIX = ".bak-s2-chp8-p219-l87-98-relation-review-20261014"
EXPECTED_HASHES = {
    STATEMENTS: "90dfc0517f4def14c19bcd552f4a707e3d57128e5ad9407b281658b9565eecba",
    CANDIDATES: "f5ad2ebb8c340618a1bf18316af4c01bddb42d054213d845fc234f3e6bc6c2e7",
    MENTIONS: "eed69d12aae2cb1b50785de44d91ba0ad8cafad650a9165681f07af1e907f23c",
    COVERAGE: "6207ec3734deacfe3e02ec341c3a558440f7273ad4f9c2c964ad94ab2710fc34",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    PDF: "cb11451ac726f37ed5badf21a569af88f790f858f1c39eb63f2efb58a0fe4ac3",
    PAGE_IMAGE: "79eb50bf4092d1cb37696dae1f427c67ace1c1b55318c77eb5fe5388a34fe5a0",
}

OLD_NOTES = {
    "st-chp8-p219-central-nave-requirement":
        "This combines the fourteen-painting requirement with the start of negotiations. The work-group to central-nave assignment is recorded separately; the source does not name an agent for the requirement or negotiations.",
    "st-chp8-p219-ceresa-modello":
        "This combines Ceresa's model submission, an unspecified party's praise, and Haskell's interpretation of that praise as concealment of a higher target. The submission, praise, and interpretation are separated below.",
    "st-chp8-p219-cervelli-wins-noah":
        "This combines the competition result, Cervelli's visit to Bergamo, and a payment with no named payer. These are recorded separately below.",
    "st-chp8-p219-cignani-negotiation-fails":
        "This combines Cignani's requested terms and arrival, the committee's response, and the failed outcome. Each action is recorded separately below.",
    "st-chp8-p219-cignani-reputation":
        "Haskell's qualified ranking of Cignani is an attributed reputation assessment, not a relation between entities.",
    "st-chp8-p219-giordano-contract-not-performed":
        "This combines the committee's ability to meet Giordano's conditions, an unsigned-by-name contract report, and Giordano's nonperformance. These claims are separated below; the signatories are not named.",
    "st-chp8-p219-giordano-crossing-description":
        "This combines Giordano's Naples career context, the sending of the picture, its visual description, and Haskell's assessment of the committee's hopes. The location and artist-to-work action are separated below; the remaining description and evaluation are non-relational.",
    "st-chp8-p219-giordano-gift-and-remainder":
        "This combines a payment report with the committee's unsuccessful request that Giordano undertake the remaining church decoration. The payer for the gift is unstated; the request is separated below.",
    "st-chp8-p219-giordano-project-terms":
        "This combines the initial fee request, its reduction, and the board-and-lodging condition. The three reported terms are separated below; footnote 2 is attached to the lodging condition.",
    "st-chp8-p219-giordano-speed-and-court-success":
        "This combines the committee's attraction to Giordano's speed, an unspecified sequence of evasive replies, and Haskell's assessment of Giordano's court success as a drawback. These are separated below with the reply agent left open.",
    "st-chp8-p219-noah-competition-entrants":
        "This groups three individually named competition entrants. Their separate sketch submissions are recorded below.",
    "st-chp8-p219-terms-stiffen-cignani-open":
        "This combines the report that Giordano's terms stiffened with Haskell's speculative alternative about Cignani. The reported change and the continuing speculation are separated below.",
}

LINKS = {
    "st-chp8-p219-central-nave-requirement": [
        "st-chp8-p219-paintings-for-central-nave",
    ],
    "st-chp8-p219-ceresa-modello": [
        "st-chp8-p219-ceresa-submitted-modello",
        "st-chp8-p219-modello-praised",
        "st-chp8-p219-haskell-interprets-modello-praise",
    ],
    "st-chp8-p219-cervelli-wins-noah": [
        "st-chp8-p219-cervelli-wins-competition",
        "st-chp8-p219-cervelli-visits-bergamo",
        "st-chp8-p219-cervelli-payment",
    ],
    "st-chp8-p219-cignani-negotiation-fails": [
        "st-chp8-p219-cignani-requests-commission-terms",
        "st-chp8-p219-cignani-arrives-bergamo",
        "st-chp8-p219-committee-compromise-for-cignani",
        "st-chp8-p219-cignani-holds-position",
    ],
    "st-chp8-p219-cignani-reputation": [],
    "st-chp8-p219-giordano-contract-not-performed": [
        "st-chp8-p219-committee-can-meet-giordano-terms",
        "st-chp8-p219-giordano-contract-signed",
        "st-chp8-p219-giordano-ignores-contract",
    ],
    "st-chp8-p219-giordano-crossing-description": [
        "st-chp8-p219-giordano-in-naples",
        "st-chp8-p219-giordano-sends-crossing",
        "st-chp8-p219-crossing-visual-description",
        "st-chp8-p219-crossing-justifies-hopes",
    ],
    "st-chp8-p219-giordano-gift-and-remainder": [
        "st-chp8-p219-giordano-gift",
        "st-chp8-p219-committee-presses-giordano-for-remainder",
    ],
    "st-chp8-p219-giordano-project-terms": [
        "st-chp8-p219-giordano-asks-6000",
        "st-chp8-p219-giordano-agrees-5000",
        "st-chp8-p219-giordano-board-lodging-condition",
    ],
    "st-chp8-p219-giordano-speed-and-court-success": [
        "st-chp8-p219-committee-attracted-by-giordano-speed",
        "st-chp8-p219-giordano-evasive-replies",
        "st-chp8-p219-giordano-court-success-drawback",
    ],
    "st-chp8-p219-noah-competition-entrants": [
        "st-chp8-p219-cervelli-enters-noah-competition",
        "st-chp8-p219-negri-enters-noah-competition",
        "st-chp8-p219-perugino-enters-noah-competition",
    ],
    "st-chp8-p219-terms-stiffen-cignani-open": [
        "st-chp8-p219-giordano-terms-stiffen",
        "st-chp8-p219-cignani-might-suit-better",
    ],
}


def row(statement_id, subject, object_, predicate, lines, claim, quote, note, *,
        relation=True, qualification=None, mentioned=None, speaker="Haskell", extra=None):
    return {
        "statement_id": statement_id, "subject": subject, "object": object_,
        "predicate": predicate, "line_start": lines[0], "line_end": lines[1],
        "claim": claim, "quote": quote, "note": note, "relation": relation,
        "qualification": qualification or
            "Preserve Haskell's attribution and the source's stated limits; do not infer an unnamed identity or outcome.",
        "mentioned": mentioned or [], "speaker": speaker, "extra": extra or {},
    }


NEW_ROWS = [
    row("st-chp8-p219-noah-competition-for-work", "cand-7679", "cand-7678",
        "competition_held_for_replacement_painting", (88, 88),
        "The 1677 competition was for a Sacrifice of Noah painting intended to replace Ciro Ferri's unsuccessful effort above the door of the Colleoni chapel.",
        "For the picture of the Sacrifice of Noah to replace Ciro Ferri’s unsuccessful effort above the door of the Colleoni chapel",
        "The source identifies the replacement painting and location but does not explicitly equate Ferri's unsuccessful effort with his earlier planned Crossing of the Red Sea.",
        mentioned=["cand-7679", "cand-7678", "cand-1027", "cand-7673", "cand-7671"]),
    row("st-chp8-p219-cervelli-enters-noah-competition", "cand-0638", "cand-7679",
        "submitted_sketch_for_competition", (88, 89),
        "Federico Cervelli took part in the 1677 competition and submitted a sketch.",
        "Three artists took part and submitted sketches:\nFederico Cervelli of Milan",
        "The sentence introduces Cervelli as one of the three artists who took part and submitted sketches.",
        mentioned=["cand-0638", "cand-7679", "cand-3418"]),
    row("st-chp8-p219-negri-enters-noah-competition", "cand-1731", "cand-7679",
        "submitted_sketch_for_competition", (88, 89),
        "Pietro Negri took part in the 1677 competition and submitted a sketch.",
        "Three artists took part and submitted sketches:\nFederico Cervelli of Milan, Pietro Negri of Venice",
        "The sentence introduces Negri as one of the three artists who took part and submitted sketches.",
        mentioned=["cand-1731", "cand-7679", "cand-3401"]),
    row("st-chp8-p219-perugino-enters-noah-competition", "cand-7682", "cand-7679",
        "submitted_sketch_for_competition", (88, 89),
        "The Turinese Cavaliere Perugino took part in the 1677 competition and submitted a sketch.",
        "Three artists took part and submitted sketches:\nFederico Cervelli of Milan, Pietro Negri of Venice, who had followed Zanchi in painting for the Scuola di San Rocco a picture to commemorate the cessation of the plague of 1630, and the Turinese Cavaliere Perugino",
        "The title-only painter remains unresolved; do not identify him with Pietro Perugino.",
        mentioned=["cand-7682", "cand-7679"]),
    row("st-chp8-p219-cervelli-wins-competition", "cand-0638", "cand-7679",
        "won_competition", (90, 90),
        "Federico Cervelli won the competition.",
        "This was won by Cervelli",
        "The preceding sentence identifies the event as the 1677 competition for The Sacrifice of Noah.",
        mentioned=["cand-0638", "cand-7679"]),
    row("st-chp8-p219-cervelli-visits-bergamo", "cand-0638", "cand-6208",
        "visited_for_alterations", (90, 90),
        "After visiting Bergamo to make certain alterations, Cervelli was paid.",
        "after a visit to Bergamo to make certain alterations",
        "The source does not specify what was altered; preserve the visit and purpose without identifying an object.",
        mentioned=["cand-0638", "cand-6208"]),
    row("st-chp8-p219-cervelli-payment", "cand-0638", None,
        "received_payment_of_370_ducats", (90, 90),
        "Cervelli was paid 370 ducats after his visit to Bergamo.",
        "was paid 370 ducats",
        "The amount is reported by Haskell; the payer is not named in this clause, so it is retained as a person-level claim, not a two-entity relation.",
        relation=False, mentioned=["cand-0638"]),
    row("st-chp8-p219-paintings-for-central-nave", "cand-7686", "cand-7685",
        "painting_group_required_for_space", (94, 94),
        "The fourteen-painting group was required for the central nave of Santa Maria Maggiore.",
        "Fourteen more paintings were now required for the central nave",
        "This records the work-group-to-space assignment. The agent behind the requirement is not named.",
        mentioned=["cand-7686", "cand-7685", "cand-7627"]),
    row("st-chp8-p219-ceresa-submitted-modello", "cand-0624", "cand-7687",
        "submitted_modello_for_project", (95, 96),
        "In 1682 Carlo Ceresa submitted a modello for the central-nave project.",
        "A year later a local artist Carlo\nCeresa submitted a tnodello",
        "The source's 'a year later' follows Tencala's 1681 approach; the model's subject and fate are unspecified.",
        mentioned=["cand-0624", "cand-7687", "cand-7686"],
        extra={"ocr_corrections": [{
            "source_file": SOURCE_REL, "source_line": 96, "ocr": "tnodello",
            "print": "modello", "basis": "CHP-8.pdf physical page 21."
        }]}),
    row("st-chp8-p219-modello-praised", "cand-7687", None,
        "reported_positive_assessment_of_modello", (96, 96),
        "The modello was considered 'very beautiful and precious'; the assessor is not identified.",
        "which was considered to be ‘very beautiful and precious’",
        "The evaluator is grammatically unstated and cannot be assigned to the committee as a formal endpoint.",
        relation=False, mentioned=["cand-7687"]),
    row("st-chp8-p219-haskell-interprets-modello-praise", "cand-7687", "cand-7641",
        "haskell_interpreted_praise_as_masking_higher_target", (96, 96),
        "Haskell characterizes the praise as flattering language intended to conceal that the committee had set a higher target.",
        "flattering words designed to conceal the fact that the committee had now set their target much higher",
        "This is Haskell's interpretation, not a quotation from the committee or a separate verified motive.",
        relation=False, mentioned=["cand-7687", "cand-7641", "cand-7686"]),
    row("st-chp8-p219-cignani-requests-commission-terms", "cand-0749", "cand-7686",
        "requested_commission_terms", (96, 96),
        "Carlo Cignani asked for large sums and all his expenses for the central-nave commission.",
        "Carlo Cignani of Bologna, at this time probably the most famous painter in Italy, asked for exorbitant sums as well as all his expenses.",
        "The sums and expenses are not itemized; Haskell's word 'exorbitant' is an attributed evaluation.",
        mentioned=["cand-0749", "cand-7686", "cand-7641"]),
    row("st-chp8-p219-cignani-arrives-bergamo", "cand-0749", "cand-6208",
        "arrived_to_press_commission_claims", (96, 96),
        "Cignani arrived in Bergamo to press his claims for the commission.",
        "He was obviously anxious to be given the commission, for he arrived in Bergamo to press his claims.",
        "The source does not give the arrival date.",
        mentioned=["cand-0749", "cand-6208", "cand-7686"]),
    row("st-chp8-p219-committee-compromise-for-cignani", "cand-7641", "cand-0749",
        "committee_considered_and_proposed_compromise", (96, 96),
        "The committee was tempted, wavered, and suggested a compromise to Cignani.",
        "The committee were sorely tempted, wavered, and suggested a compromise.",
        "The committee's wavering is Haskell's characterization; the compromise terms are not supplied.",
        mentioned=["cand-7641", "cand-0749", "cand-7686"]),
    row("st-chp8-p219-cignani-holds-position", "cand-0749", "cand-7686",
        "negotiation_failed_after_artist_held_terms", (96, 96),
        "Cignani held to his position and the central-nave commission plan fell through.",
        "But Cignani stuck to his position, and the plan fell through.",
        "The source does not state the exact terms or identify the document or decision that ended the plan.",
        mentioned=["cand-0749", "cand-7686", "cand-7641"]),
    row("st-chp8-p219-giordano-asks-6000", "cand-1172", "cand-7686",
        "requested_6000_ducats_for_paintings", (96, 96),
        "Giordano first asked for 6,000 ducats to paint ten frescoes and four oil paintings.",
        "He had first asked for 6000 ducats to paint the ten frescoes and four oils",
        "The amount and work count are Haskell's report; the source gives no fee document here.",
        mentioned=["cand-1172", "cand-7686"]),
    row("st-chp8-p219-giordano-agrees-5000", "cand-1172", "cand-7686",
        "agreed_to_reduced_5000_ducat_fee_under_pressure", (96, 96),
        "Under pressure, Giordano agreed to reduce his requested amount to 5,000 ducats.",
        "but under pressure agreed to reduce this to 5000",
        "The amount is reported by Haskell; the source does not specify who applied the pressure.",
        mentioned=["cand-1172", "cand-7686", "cand-7641"]),
    row("st-chp8-p219-giordano-board-lodging-condition", "cand-1172", "cand-7686",
        "conditioned_terms_on_board_and_lodging", (96, 96),
        "Giordano's reduced fee was conditional on free board and lodging for him, an assistant, and a servant for as long as they were required to stay in Bergamo.",
        "provided that he himself, an assistant and a servant were given free board and lodging for as long as they \"should be required to stay in Bergamo.2",
        "The assistant and servant are unnamed. The printed page has no opening quotation mark before 'should'; footnote 2 is linked to this reported condition.",
        mentioned=["cand-1172", "cand-7686", "cand-6208"],
        extra={
            "footnote_markers": [2], "footnote_link_status": "linked",
            "footnote_segment": "chp-8:08_CHP-8_sec_ii:l372-461",
            "footnote_target_line": 378,
            "footnote_citation_statement_ids": ["st-chp8-p219-n2-citation"],
            "footnote_pending": False,
            "ocr_corrections": [{
                "source_file": SOURCE_REL, "source_line": 96,
                "ocr": "\"should be required", "print": "should be required",
                "basis": "CHP-8.pdf physical page 21."
            }]
        }),
    row("st-chp8-p219-committee-can-meet-giordano-terms", "cand-7641", "cand-1172",
        "committee_could_meet_artist_conditions", (96, 96),
        "The committee could just manage Giordano's conditions.",
        "The committee could just manage these conditions",
        "The conditions refer to the fee and board-and-lodging terms immediately above.",
        mentioned=["cand-7641", "cand-1172", "cand-7686"]),
    row("st-chp8-p219-giordano-contract-signed", None, "cand-7688",
        "contract_reported_signed", (96, 96),
        "Haskell reports that a contract for the Giordano project was signed.",
        "a contract was signed",
        "The signatories and date are not named in this clause; do not infer the parties from context as endpoints.",
        relation=False, mentioned=["cand-7688", "cand-1172", "cand-7641"]),
    row("st-chp8-p219-giordano-ignores-contract", "cand-1172", "cand-7688",
        "artist_ignored_signed_contract", (96, 96),
        "Haskell says Giordano ignored the signed contract.",
        "only to be ignored by the artist",
        "The source does not specify what obligations he left unperformed or why.",
        mentioned=["cand-1172", "cand-7688"]),
    row("st-chp8-p219-giordano-in-naples", "cand-1172", "cand-1722",
        "career_located_in_naples_in_1682", (92, 93),
        "In 1682 Giordano was at the height of his career in Naples.",
        "The artist was then at the height of his career in\nNaples",
        "The location is stated in Haskell's account; it does not establish a permanent residence.",
        mentioned=["cand-1172", "cand-1722"]),
    row("st-chp8-p219-giordano-sends-crossing", "cand-1172", "cand-7641",
        "sent_crossing_picture_to_committee", (93, 93),
        "Giordano sent the Crossing of the Red Sea picture to the committee.",
        "the picture which he sent them",
        "The antecedent is the Crossing of the Red Sea painting entrusted to Giordano; 'them' refers to the committee. The surviving canvas is not independently identified.",
        mentioned=["cand-1172", "cand-7668", "cand-7641"],
        extra={"anaphora_resolution": {
            "surface": "the picture", "antecedent": "The Crossing of the Red Sea painting entrusted to Giordano at chp-8:08_CHP-8_sec_ii:l86-98#L91-92"
        }}),
    row("st-chp8-p219-crossing-visual-description", "cand-7668", None,
        "reported_visual_description_of_painting", (93, 93),
        "Haskell describes the picture's warm light and the faithful emerging from a dark-green, tempestuous sea.",
        "with its warm glow of light bathing the faithful who have just emerged from the dark-green tempestuous sea",
        "This is a reported description of the picture; no individual figures or independent visual inspection are identified here.",
        relation=False, mentioned=["cand-7668"]),
    row("st-chp8-p219-crossing-justifies-hopes", "cand-7668", "cand-7641",
        "haskell_assessed_picture_as_justifying_committee_hopes", (93, 93),
        "Haskell says the picture justified the committee's great hopes.",
        "justified their great hopes",
        "This is Haskell's evaluation of the committee's expectations, not an independent quality assessment.",
        relation=False, mentioned=["cand-7668", "cand-7641"]),
    row("st-chp8-p219-giordano-gift", "cand-1172", None,
        "received_100_scudi_in_addition_to_700_promised", (93, 93),
        "Giordano received a present of 100 scudi in addition to the 700 previously promised.",
        "He was given a present of 100 setidi in addition to the 700 he had already been promised",
        "The giver and terms of the earlier promise are not named; the payment is retained as a person-level claim.",
        relation=False, mentioned=["cand-1172"],
        extra={"ocr_corrections": [{
            "source_file": SOURCE_REL, "source_line": 93, "ocr": "setidi",
            "print": "scudi", "basis": "CHP-8.pdf physical page 21 high-resolution crop."
        }]}),
    row("st-chp8-p219-committee-presses-giordano-for-remainder", "cand-7641", "cand-1172",
        "committee_unsuccessfully_asked_artist_for_remaining_decoration", (93, 93),
        "The committee unsuccessfully pressed Giordano to undertake all the remaining decoration of the church.",
        "was pressed, unsuccessfully, to undertake all the remaining decoration of the church",
        "The source does not give the reason for Giordano's refusal or enumerate the remaining work.",
        mentioned=["cand-7641", "cand-1172", "cand-7627"]),
    row("st-chp8-p219-committee-attracted-by-giordano-speed", "cand-7641", "cand-1172",
        "committee_sought_artist_for_speed", (96, 96),
        "One attraction of asking Giordano was his legendary speed.",
        "One of the attractions of asking Giordano in the first place was his legendary speed.",
        "The characterization of his speed as legendary is Haskell's; no completion-rate comparison is supplied.",
        mentioned=["cand-7641", "cand-1172"]),
    row("st-chp8-p219-giordano-evasive-replies", None, None,
        "correspondence_met_with_evasive_replies", (96, 96),
        "As years passed, repeated letters received conciliatory but evasive replies; the speaker, recipient, and direction are not made explicit.",
        "Now as year followed year, and letter after letter was met with conciliatory but evasive replies,",
        "The wording uses a passive construction and does not identify who sent the letters or who replied; this clause continues across the source line break.",
        relation=False, mentioned=["cand-1172", "cand-7641"]),
    row("st-chp8-p219-giordano-court-success-drawback", "cand-1172", None,
        "haskell_assessed_court_success_as_negotiation_drawback", (97, 97),
        "Haskell says Giordano's success with the courts of Italy and Europe became a real drawback in the negotiations.",
        "Giordano’s.success with all the courts of Italy and Europe was seen to be a real drawback",
        "This is Haskell's assessment. The courts are not individually identified as entities, and the passage does not state that Giordano had a particular court appointment.",
        relation=False, mentioned=["cand-1172", "cand-3461", "cand-3462", "cand-7641"],
        extra={"ocr_corrections": [{
            "source_file": SOURCE_REL, "source_line": 97,
            "ocr": "Giordano’s.success", "print": "Giordano’s success",
            "basis": "CHP-8.pdf physical page 21."
        }]}),
    row("st-chp8-p219-giordano-terms-stiffen", "cand-1172", "cand-7686",
        "artist_terms_became_stiffer_over_time", (98, 98),
        "Haskell says Giordano's terms became stiffer over time.",
        "Moreover, as time went by, his terms became stiffer and stiffer.",
        "The statement concerns the terms for the central-nave commission; the exact changes are not listed.",
        mentioned=["cand-1172", "cand-7686"]),
    row("st-chp8-p219-cignani-might-suit-better", None, None,
        "haskell_speculated_cignani_might_be_more_satisfactory", (98, 98),
        "Haskell speculates that Cignani might prove more satisfactory after all; the sentence continues on p.220.",
        "Perhaps Cignani would",
        "This is the author's tentative comparison, not an appointment, accepted commission, or relation between Cignani and Giordano.",
        relation=False, mentioned=["cand-0749", "cand-1172"],
        extra={
            "continuation_status": "closed",
            "continuation_to_segment_id": "chp-8:08_CHP-8_sec_ii:l100-110",
            "continuation_to_source_line": 101,
            "continuation_fragment": "prove more satisfactory after all",
            "continued_to_segment_id": "chp-8:08_CHP-8_sec_ii:l100-110",
            "continued_to_source_line": 101,
            "continued_to_statement_id": "st-chp8-p220-cignani-satisfactory",
        }),
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path):
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader), raw.startswith(b"\xef\xbb\xbf")


def csv_bytes(fields, rows, bom):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    data = output.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" + data) if bom else data


def atomic_write(path, data):
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False, suffix=".tmp") as stream:
        stream.write(data)
        temporary = Path(stream.name)
    temporary.replace(path)


def make_statement(item):
    q = {
        "source_line_start": item["line_start"], "source_line_end": item["line_end"],
        "printed_page": 219, "pdf_physical_page": 21, "claim": item["claim"],
        "speaker": item["speaker"], "text_layer": "body", "qualification": item["qualification"],
        "mentioned_candidate_ids": item["mentioned"], "relation_candidate": item["relation"],
        "relation_candidate_note": item["note"],
    }
    q.update(item["extra"])
    return {"statement_id": item["statement_id"], "segment_id": SEGMENT_ID,
            "subject_candidate_id": item["subject"], "object_candidate_id": item["object"],
            "predicate": item["predicate"], "qualifiers": q, "original_quote": item["quote"],
            "origin": "book", "source_file": SOURCE_REL}


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
    by_id = {r["statement_id"]: r for r in statement_rows}
    target_ids = set(OLD_NOTES) | {
        "st-chp8-p219-giordano-crossing-assigned",
        "st-chp8-p219-negri-san-rocco-picture",
        "st-chp8-p219-perugino-protege",
        "st-chp8-p219-project-funds-strained",
        "st-chp8-p219-tencala-approached",
        "st-chp8-p219-zanchi-coloured-picture",
        "st-chp8-p219-noah-competition",
    }
    unset = {r["statement_id"] for r in statement_rows
             if r.get("segment_id") == SEGMENT_ID and "relation_candidate" not in r.get("qualifiers", {})}
    if unset != target_ids:
        raise SystemExit(f"unexpected p.219 unset statements: {sorted(unset)}")
    if not target_ids <= by_id.keys():
        raise SystemExit("expected p.219 source statements changed")
    new_ids = {x["statement_id"] for x in NEW_ROWS}
    if len(new_ids) != len(NEW_ROWS) or new_ids & by_id.keys():
        raise SystemExit("new statement IDs collide")
    linked_new_ids = set().union(*[set(x) for x in LINKS.values()])
    linked_new_ids.add("st-chp8-p219-noah-competition-for-work")
    if linked_new_ids != new_ids:
        raise SystemExit("new statement link coverage differs")
    if any(link not in new_ids for links in LINKS.values() for link in links):
        raise SystemExit("old statement links to an unknown new row")

    candidate_by_id = {r["candidate_id"]: r for r in candidate_rows}
    painting = candidate_by_id.get("cand-7668")
    if (not painting or painting.get("canonical_name") !=
            "Crossing of the Red Sea (large picture planned for Santa Maria Maggiore by Ciro Ferri)"):
        raise SystemExit("cand-7668 state changed")
    if painting.get("detail", "").find("At p.219 Haskell calls it the third large oil painting") < 0:
        raise SystemExit("cand-7668 detail no longer records the source's continuity")

    for old_id, note in OLD_NOTES.items():
        q = by_id[old_id]["qualifiers"]
        q["relation_candidate"] = False
        q["relation_candidate_note"] = note
        q["linked_statement_ids"] = LINKS[old_id]

    # The competition is an event between the committee and the replacement painting.
    # Keep each relation as a pair: committee -> event; event -> painting.
    competition = by_id["st-chp8-p219-noah-competition"]
    competition["subject_candidate_id"] = "cand-7641"
    competition["object_candidate_id"] = "cand-7679"
    competition["predicate"] = "committee_decided_to_organize_competition"
    competition["qualifiers"]["claim"] = "The committee decided in 1677, after a delay of some years, to organize the competition."
    competition["qualifiers"]["relation_candidate"] = True
    competition["qualifiers"]["relation_candidate_note"] = "The competition event is an explicit source-bounded candidate; its purpose and replacement painting are recorded in a separate linked statement."
    competition["qualifiers"]["linked_statement_ids"] = ["st-chp8-p219-noah-competition-for-work"]

    # Repoint the school painting relation to the institution, not to the unnamed work.
    negri = by_id["st-chp8-p219-negri-san-rocco-picture"]
    negri["object_candidate_id"] = "cand-2351"
    negri["predicate"] = "painting_for_institution"
    negri["qualifiers"]["relation_candidate"] = True
    negri["qualifiers"]["relation_candidate_note"] = "The explicit relation is Pietro Negri painting for Scuola di San Rocco; the unnamed commemorative picture and plague context remain in mentioned_candidate_ids."
    negri["qualifiers"]["mentioned_candidate_ids"] = ["cand-1731", "cand-2351", "cand-7680", "cand-7681", "cand-2834"]

    # Correct the direction of Perugino's patron-protege relation.
    protege = by_id["st-chp8-p219-perugino-protege"]
    protege["subject_candidate_id"], protege["object_candidate_id"] = "cand-7682", "cand-7683"
    protege["qualifiers"]["relation_candidate"] = True
    protege["qualifiers"]["relation_candidate_note"] = "The source says the title-only Turinese painter was a protege of the King of Savoy; direction is painter -> patron. Both identities remain unresolved."

    true_notes = {
        "st-chp8-p219-giordano-crossing-assigned":
            "The committee entrusted the named Crossing of the Red Sea commission to Luca Giordano in 1682; Ciro Ferri is retained as earlier subject context, not as the executing artist.",
        "st-chp8-p219-project-funds-strained":
            "The source attributes the funding constraint to the committee's project for the fourteen central-nave paintings; no account or donor is identified.",
        "st-chp8-p219-tencala-approached":
            "Tencala was approached for the central-nave project in 1681; the agent and reason no arrangement followed are unstated.",
    }
    for sid, note in true_notes.items():
        q = by_id[sid]["qualifiers"]
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note

    by_id["st-chp8-p219-zanchi-coloured-picture"]["qualifiers"]["relation_candidate"] = False
    by_id["st-chp8-p219-zanchi-coloured-picture"]["qualifiers"]["relation_candidate_note"] = (
        "This continues Haskell's description and praise of the painting's appearance; the visual content is retained as a source claim, not a formal relation."
    )

    # The p.219 sentence about the alternative Cignani closes on p.220.
    old_alternative = by_id["st-chp8-p219-terms-stiffen-cignani-open"]["qualifiers"]
    for key in ("continuation_to_segment_id", "continuation_to_source_line", "continuation_fragment",
                "continuation_status", "continued_to_segment_id", "continued_to_source_line",
                "continued_to_statement_id"):
        old_alternative.pop(key, None)
    p220 = by_id["st-chp8-p220-cignani-satisfactory"]["qualifiers"]
    if p220.get("continued_from_statement_id") != "st-chp8-p219-terms-stiffen-cignani-open":
        raise SystemExit("p.220 continuation source changed")
    p220["continued_from_statement_id"] = "st-chp8-p219-cignani-might-suit-better"
    p220["relation_candidate"] = False
    p220["relation_candidate_note"] = "This closes Haskell's speculative assessment begun on p.219; it does not assert that Cignani accepted or received the commission."

    # Keep the linked footnote on the atomic statement carrying the printed marker.
    n1 = by_id["st-chp8-p219-n1-citation"]["qualifiers"]
    n1["linked_body_statement_ids"] = ["st-chp8-p219-giordano-crossing-assigned"]
    n2 = by_id["st-chp8-p219-n2-citation"]["qualifiers"]
    n2["linked_body_statement_ids"] = ["st-chp8-p219-giordano-board-lodging-condition"]

    # This work candidate tracks the same planned subject across the source's Ferri and Giordano passages.
    painting["canonical_name"] = (
        "Crossing of the Red Sea (large oil picture for Santa Maria Maggiore; first planned for Ciro Ferri, later entrusted to Luca Giordano)"
    )
    painting["detail"] = (
        "Haskell first reports the planned overdoor subject for Ferri, then identifies it as the third large oil painting entrusted to Giordano in 1682 and says Giordano sent the picture to the committee. This candidate tracks the source's continuity of the painting commission; it does not independently establish the surviving canvas, completion history, or current location. Haskell's note 1 reports an alternative represented subject from an unconsulted anonymous article."
    )

    for item in NEW_ROWS:
        statement_rows.append(make_statement(item))

    candidate_bytes = csv_bytes(candidate_fields, candidate_rows, candidate_bom)
    statement_bytes = ("\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":"))
                                  for r in statement_rows) + "\n").encode("utf-8")
    page_rows = [r for r in statement_rows if r.get("segment_id") == SEGMENT_ID]
    summary = {
        "existing_rows_classified_or_refined": len(target_ids),
        "new_statements": len(NEW_ROWS),
        "new_true": sum(x["relation"] for x in NEW_ROWS),
        "new_false": sum(not x["relation"] for x in NEW_ROWS),
        "corrected_relation_directions": 2,
        "corrected_work_candidate": "cand-7668",
        "p219_final_statements": len(page_rows),
        "p219_final_true": sum(r["qualifiers"].get("relation_candidate") is True for r in page_rows),
        "p219_final_false": sum(r["qualifiers"].get("relation_candidate") is False for r in page_rows),
        "p219_final_unset": sum("relation_candidate" not in r.get("qualifiers", {}) for r in page_rows),
    }
    return statement_bytes, candidate_bytes, summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write guarded plan; default dry-run")
    args = parser.parse_args()
    verify_inputs()
    statements_out, candidates_out, summary = plan()
    print(json.dumps({"mode": "apply" if args.apply else "dry-run", **summary},
                     ensure_ascii=False, indent=2))
    if not args.apply:
        return
    verify_inputs()
    output_map = {STATEMENTS: statements_out, CANDIDATES: candidates_out}
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
