"""Guarded S2 semantic review for printed p.218, lines 79-84."""
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
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE = ROOT / SOURCE_REL
PDF = ROOT / "02-sources" / "01-book" / "CHP-8.pdf"
PAGE_IMAGE = ROOT / "scripts" / ".tmp_s2_chp8_p218_review.png"
SEGMENT_ID = "chp-8:08_CHP-8_sec_ii:l78-84"
SEGMENT_SHA = "a9adfb724cd4f057a4de3aa9bd62f9818990c72c1612a9072e223c978569ae22"
BACKUP_SUFFIX = ".bak-s2-chp8-p218-l79-84-relation-review-20261014"
EXPECTED_HASHES = {
    STATEMENTS: "3f1478965e9c41c85d8594fcaec3da518d26c62c988bc3b47fdef007aaea8960",
    CANDIDATES: "0c5d7c3bc28bb1a6ac28074256ff8026694163dda42a11d2633fae69439a6aa9",
    MENTIONS: "79e0c309cc2eabb60a9760fe0a8e8c655c8ef7e57d842f3dcdcc5dca04f9cd29",
    COVERAGE: "6207ec3734deacfe3e02ec341c3a558440f7273ad4f9c2c964ad94ab2710fc34",
    SOURCE: "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    PDF: "cb11451ac726f37ed5badf21a569af88f790f858f1c39eb63f2efb58a0fe4ac3",
    PAGE_IMAGE: "6d3a2a02c09e9385ae2aa05859f8b0f51b1c94f04daa8c7c603417a61a5bfc03",
}

OLD_NOTES = {
    "st-chp8-p218-ferri-arrival-contract": "This combines Ferri's arrival in Bergamo with the later contract and its media. The reported arrival and contract terms are retained as one chronology item in the source; preserve September and December 1665 separately in the claim.",
    "st-chp8-p218-ferri-invitation-response": "This combines the p.217 request's completion, committee agreement, delay, cooling relations, and Ferri's arrival. The request continuation, agreement, delay, and arrival are now linked to separate statements.",
    "st-chp8-p218-ferri-private-letters-and-subject": "This combines reports about Ferri's private letters, the fresco sites, the planned overdoor subject, Ferri's quoted description, and its iconography. The distinct claims are recorded below.",
    "st-chp8-p218-ferri-schedule-and-work-progress": "This combines Ferri's duration estimate, Haskell's speed assessment, dated fresco progress, Ferri's first-person complaint, and the p.218 completion status. These are linked to separate source-anchored statements.",
    "st-chp8-p218-ferri-completion-status-1667": "This combines the June 1667 completion snapshot with Haskell's stylistic evaluation of the frescoes. Preserve the full source excerpt and record the status and style separately.",
    "st-chp8-p218-ferri-leaves": "This combines the committee's review of an unnamed side-door picture with Ferri's angry departure and unfinished contract. The reviewed picture is retained as an open work candidate; review and departure are separated below.",
    "st-chp8-p218-zanchi-selected-for-moses": "This combines the remaining works, open artist proposals, Zanchi's selection, the committee's caution, and the painting title. The source's title-marker correction and linked footnote are retained on the atomic selection statement.",
    "st-chp8-p218-zanchi-terms": "This combines conditional payment/return terms, price-setting, Haskell's judgment of the terms, and Zanchi's agreement. Each distinct term and action is linked below.",
    "st-chp8-p218-zanchi-canvas-accepted": "This combines Zanchi's site visit and permission, canvas delivery, urging letters, completion, committee deliberation, acceptance, payment, and Haskell's praise. The p.219 continuation is moved to the separate praise statement.",
}

LINKS = {
    "st-chp8-p218-ferri-arrival-contract": [
        "st-chp8-p218-ferri-arrives-september-1665", "st-chp8-p218-ferri-contract-december-1665",
    ],
    "st-chp8-p218-ferri-invitation-response": [
        "st-chp8-p218-ferri-request-for-sketch-approval", "st-chp8-p218-committee-agrees-sketch-submission",
        "st-chp8-p218-delay-cools-relations", "st-chp8-p218-ferri-arrives-september-1665",
    ],
    "st-chp8-p218-ferri-private-letters-and-subject": [
        "st-chp8-p218-private-letters-pleasure-and-site-size", "st-chp8-p218-overdoor-crossing-planned",
        "st-chp8-p218-ferri-grandest-composition-description",
    ],
    "st-chp8-p218-ferri-schedule-and-work-progress": [
        "st-chp8-p218-ferri-task-duration-estimate", "st-chp8-p218-ferri-worked-faster-than-expected",
        "st-chp8-p218-fresco-progress-by-may-and-november", "st-chp8-p218-ferri-working-day-and-night",
        "st-chp8-p218-ferri-bored-in-bergamo",
    ],
    "st-chp8-p218-ferri-completion-status-1667": [
        "st-chp8-p218-ferri-june-1667-completion-snapshot", "st-chp8-p218-frescoes-variations-on-cortona-style",
    ],
    "st-chp8-p218-ferri-leaves": [
        "st-chp8-p218-committee-reviews-side-door-picture", "st-chp8-p218-ferri-leaves-before-contract-complete",
    ],
    "st-chp8-p218-zanchi-selected-for-moses": [
        "st-chp8-p218-three-paintings-remain", "st-chp8-p218-artists-propose-for-remaining-works",
        "st-chp8-p218-zanchi-selected-for-moses-rock", "st-chp8-p218-zanchi-described-as-venetian",
        "st-chp8-p218-committee-more-cautious-after-ferri",
    ],
    "st-chp8-p218-zanchi-terms": [
        "st-chp8-p218-zanchi-no-fee-and-return-terms", "st-chp8-p218-experts-set-price-if-accepted",
        "st-chp8-p218-terms-exceptionally-hard", "st-chp8-p218-zanchi-agrees-to-terms",
    ],
    "st-chp8-p218-zanchi-canvas-accepted": [
        "st-chp8-p218-zanchi-site-visit-and-venice-permission", "st-chp8-p218-zanchi-canvas-sent",
        "st-chp8-p218-letters-urge-zanchi-to-hurry", "st-chp8-p218-zanchi-canvas-completed-four-months",
        "st-chp8-p218-committee-deliberates-on-zanchi-canvas", "st-chp8-p218-committee-accepts-zanchi-canvas",
        "st-chp8-p218-zanchi-receives-825-ducats", "st-chp8-p218-zanchi-merits-praise-open",
    ],
}


def row(statement_id, subject, object_, predicate, lines, claim, quote, note, *, relation=True,
        qualification=None, mentioned=None, speaker="Haskell", extra=None):
    return {
        "statement_id": statement_id, "subject": subject, "object": object_, "predicate": predicate,
        "line_start": lines[0], "line_end": lines[1], "claim": claim, "quote": quote,
        "note": note, "relation": relation,
        "qualification": qualification or "Preserve the source's attribution and stated limits; do not infer an unstated date, identity, or outcome.",
        "mentioned": mentioned or [], "speaker": speaker, "extra": extra or {},
    }


NEW_ROWS = [
    row("st-chp8-p218-ferri-request-for-sketch-approval", "cand-1027", "cand-7641", "ferri_requested_details_to_prepare_sketches_for_committee_approval", (79,79),
        "The p.217 request continues: Ferri asked for the necessary details so that he could begin sketches for the committee's approval.",
        "once begin work on the sketches which he would then submit -for the committee’s approval.",
        "This closes Ferri's request begun on p.217 L76. The source print retains the hyphen before 'for'; no correction is made.",
        qualification="The request is attributed to Ferri through Haskell; no sketch title or completed sketch is identified.",
        mentioned=["cand-1027","cand-7641"], extra={"continued_from_segment_id":"chp-8:08_CHP-8_sec_ii:l69-76","continued_from_source_line":76,"continued_from_statement_id":"st-chp8-p217-ferri-request-details-open","continuation_status":"closed"}),
    row("st-chp8-p218-committee-agrees-sketch-submission", "cand-7641", "cand-1027", "committee_agreed_to_sketch_submission", (79,79),
        "Haskell says the committee agreed to Ferri's proposed sketch submission.", "This was agreed",
        "The agreement concerns Ferri's submission of sketches for the committee's approval.", mentioned=["cand-7641","cand-1027"]),
    row("st-chp8-p218-delay-cools-relations", "cand-1027", None, "delay_and_cooling_relations_between_artist_and_patrons", (79,79),
        "After some months of delay, Haskell says relations between Ferri and the patrons had cooled.",
        "after some months of delay, during which the relations between artist and patrons rather cooled",
        "The patrons are not individually identified; do not reduce the plural group to the committee alone.",
        mentioned=["cand-1027","cand-7641"], qualification="Haskell reports a temporal delay and cooling relationship; the patron group and precise cause of delay are not specified."),
    row("st-chp8-p218-ferri-arrives-september-1665", "cand-1027", "cand-6208", "ferri_arrived_in_bergamo_september_1665", (79,80),
        "Haskell says Ferri arrived in Bergamo in September 1665.",
        "Ciro Ferri finally arrived in Bergamo in\nSeptember 1665",
        "The date and arrival are Haskell's reported chronology.", mentioned=["cand-1027","cand-6208"]),
    row("st-chp8-p218-ferri-contract-december-1665", "cand-1027", "cand-7663", "ferri_contracted_for_sixteen_pictures_in_oil_and_fresco", (80,80),
        "Haskell says Ferri signed a contract in December 1665 to paint the sixteen pictures partly in oil and partly in fresco.",
        "in December signed a contract to paint the sixteen pictures—partly - in oil and partly in fresco.",
        "The contract itself is not independently consulted; preserve the stated media and date.",
        mentioned=["cand-1027","cand-7663"], qualification="The source reports a December contract after Ferri's September arrival; the printed dash/hyphen sequence is retained as it appears in the page image."),
    row("st-chp8-p218-private-letters-pleasure-and-site-size", "cand-1027", "cand-7667", "private_letters_reported_pleasure_and_small_fresco_sites", (80,80),
        "Haskell says Ferri wrote privately of his pleasure, while admitting that the fresco sites were rather too small.",
        "In private letters Ferri wrote of his pleasure, though he admitted that the sites for the frescoes were rather too small.",
        "The letter dates and recipients are not supplied; the statements are reported through Haskell.",
        mentioned=["cand-1027","cand-7667","cand-7644"], qualification="This preserves the two points attributed to Ferri's private letters without inferring a recipient or the specific fresco surfaces."),
    row("st-chp8-p218-overdoor-crossing-planned", "cand-7663", "cand-7668", "large_overdoor_picture_planned_as_crossing_of_red_sea", (80,80),
        "Haskell says the large picture over the door was planned to represent the Crossing of the Red Sea.",
        "On the other hand the large picture over the door was to represent the Crossing of the Red Sea",
        "This is a plan for the subject; it does not by itself identify a completed surviving canvas.", mentioned=["cand-7663","cand-7668"]),
    row("st-chp8-p218-ferri-grandest-composition-description", "cand-1027", "cand-7668", "ferri_called_composition_his_grandest_and_described_scene", (80,81),
        "In a quotation transmitted by Haskell, Ferri called the composition his grandest and described Hebrews who had crossed the sea and Moses raising his rod.",
        "and this ‘is the grandest composition that I have ever done. On one side\nI am painting the Hebrews who have already crossed and Moses raising his rod above the sea.’",
        "The words are attributed to Ferri in Haskell's account; they describe a planned composition, not proof of the finished picture's final iconography.",
        speaker="Ciro Ferri, quoted by Haskell", mentioned=["cand-1027","cand-7668","cand-4144"]),
    row("st-chp8-p218-ferri-task-duration-estimate", "cand-1027", "cand-7663", "ferri_estimated_task_at_two_and_a_half_years", (81,81),
        "Haskell reports that Ferri estimated the whole task would take about two and a half years.",
        "The whole task, wrote Ferri, would take some two and a half years.",
        "This is Ferri's reported estimate, not an elapsed completion time.", speaker="Ciro Ferri, reported by Haskell", mentioned=["cand-1027","cand-7663"]),
    row("st-chp8-p218-ferri-worked-faster-than-expected", "cand-1027", None, "haskell_says_ferri_worked_quicker_than_expected", (81,81),
        "Haskell says Ferri worked much quicker than he had expected.", "In fact, he worked much quicker than he had expected.",
        "This is Haskell's comparison of actual pace with expectation, not an independently measured productivity assessment.",
        relation=False, mentioned=["cand-1027"]),
    row("st-chp8-p218-fresco-progress-by-may-and-november", "cand-1027", "cand-7663", "four_frescoes_by_may_and_six_more_by_november_1666", (81,81),
        "Haskell reports four frescoes completed by May 1666 and six more by November, all with Old Testament subjects.",
        "By May 1666 he had completed four of the frescoes; and by November a further six—all of subjects taken from the Old Testament.",
        "The dates and counts are Haskell's reported chronology; they do not imply the entire commission was complete.",
        mentioned=["cand-1027","cand-7663","cand-7677"]),
    row("st-chp8-p218-ferri-working-day-and-night", "cand-1027", "cand-7663", "ferri_reported_working_day_and_night_to_finish", (81,81),
        "In a first-person quotation reported by Haskell, Ferri says he was working day and night to get through quickly.",
        "T ana working day and night to get through quickly",
        "This is Ferri's quoted first-person report, transmitted through Haskell.", speaker="Ciro Ferri, quoted by Haskell",
        mentioned=["cand-1027","cand-7663"], extra={"ocr_corrections":[{"source_file":SOURCE_REL,"source_line":81,"ocr":"T ana working day and night","print":"I am working day and night","basis":"CHP-8.pdf physical page 20."}]}),
    row("st-chp8-p218-ferri-bored-in-bergamo", "cand-1027", "cand-6208", "ferri_reported_boredom_and_wish_not_to_remain", (81,81),
        "Ferri says he was bored and could not stay longer in the place, which the passage locates as Bergamo.",
        "for I’m so bored that I can’t stay any longer in this place",
        "The place is resolved to Bergamo from Ferri's arrival and work context; this remains Ferri's quoted view, not an objective condition of the city.",
        speaker="Ciro Ferri, quoted by Haskell", mentioned=["cand-1027","cand-6208"],
        extra={"anaphora_resolution":{"surface":"this place","antecedent":"Bergamo, the location of Ferri's commission and arrival in chp-8:08_CHP-8_sec_ii:l78-84#L79"}}),
    row("st-chp8-p218-ferri-june-1667-completion-snapshot", "cand-1027", "cand-7663", "june_1667_snapshot_thirteen_frescoes_one_oil_complete_other_pending", (82,82),
        "By June 1667, eighteen months after Ferri's arrival, Haskell says all thirteen frescoed compartments and one large oil painting were complete, while the other oil painting remained to be finished so the two could be shown together.",
        "June 1667, however, eighteen months after his arrival, the business was nearly over. The thirteen frescoed compartments were all complete—little more than mannered and insipid variations on Pietro’s style—so was one of the large oil paintings, and he was waiting to finish the other so that they could both be shown to the public together.",
        "The source does not identify which large oil painting was finished. Haskell's style assessment is separately recorded below.",
        mentioned=["cand-1027","cand-7663","cand-0342","cand-7668"], extra={"qualification_terms":["June 1667","eighteen months after his arrival","one of the large oil paintings","waiting to finish the other"]}),
    row("st-chp8-p218-frescoes-variations-on-cortona-style", "cand-7663", "cand-0342", "frescoes_described_as_mannered_insipid_variations_on_cortona_style", (82,82),
        "Haskell describes the thirteen frescoed compartments as mannered and insipid variations on Pietro da Cortona's style.",
        "little more than mannered and insipid variations on Pietro’s style",
        "This is Haskell's stylistic evaluation and comparison; it is not an authorship attribution.",
        mentioned=["cand-7663","cand-0342"]),
    row("st-chp8-p218-committee-reviews-side-door-picture", "cand-7641", "cand-12059", "committee_doubted_side_door_picture_and_consulted_experts", (83,83),
        "Haskell says the committee doubted the quality of an unnamed picture planned above the side door adjoining the Colleoni chapel and decided to consult expert opinion.",
        "They had doubts about the quality of the picture to be placed above the side door adjoining the Colleoni chapel and they decided to consult expert opinion as to its merits.",
        "The picture and experts are unnamed. Its identity relative to the works later said to remain after Ferri's departure is not explicit.",
        mentioned=["cand-7641","cand-12059","cand-7673","cand-7671"]),
    row("st-chp8-p218-ferri-leaves-before-contract-complete", "cand-1027", "cand-6208", "ferri_left_bergamo_before_completing_contract_after_review", (83,83),
        "Haskell says Ferri left Bergamo in anger at the committee's review before completing his contract.",
        "Ciro Ferri, in a fit of rage at this insult, left Bergamo without completing his contract.",
        "The anger and insult are Haskell's characterization; the source does not specify what Ferri did after leaving Bergamo.",
        mentioned=["cand-1027","cand-6208","cand-7641","cand-7663"]),
    row("st-chp8-p218-three-paintings-remain", "cand-7641", "cand-12060", "three_paintings_remained_after_ferri_departed", (84,84),
        "After Ferri left, three pictures remained: two large door paintings and one slightly smaller picture for the inner wall of the North transept.",
        "Three pictures remained to be painted—two large ones for the North and West doors and one, slightly smaller, for the inner wall of the North transept.",
        "The group is source-bounded; the smaller work's subject and whether the side-door picture above is among these three are not stated.",
        mentioned=["cand-7641","cand-12060","cand-7669","cand-12061","cand-7674","cand-7675","cand-7672"]),
    row("st-chp8-p218-artists-propose-for-remaining-works", None, "cand-12060", "various_unnamed_artists_proposed_for_remaining_pictures", (84,84),
        "Haskell says various artists proposed themselves for the remaining pictures.", "Various artists proposed themselves",
        "No artists are named; leave the proposing group open rather than creating individual candidates.",
        mentioned=["cand-12060"]),
    row("st-chp8-p218-zanchi-selected-for-moses-rock", "cand-7641", "cand-7670", "committee_accepted_zanchi_and_required_moses_striking_the_rock", (84,84),
        "The committee accepted Antonio Zanchi and required him to paint Moses striking the Rock.",
        "eventually the young Venetian, Antonio Zanchi, was accepted and required to paint Moses striking the RockJ",
        "The printed footnote marker follows the title. The painting is the named work in the remaining commission; no location beyond the commission is inferred.",
        mentioned=["cand-7641","cand-2834","cand-7670","cand-3401"],
        extra={"ocr_corrections":[{"source_file":SOURCE_REL,"source_line":84,"ocr":"Moses striking the RockJ","print":"Moses striking the Rock.¹","basis":"CHP-8.pdf physical page 20."}],
               "footnote_markers":[1],"footnote_link_status":"linked","footnote_segment":"chp-8:08_CHP-8_sec_ii:l372-461","footnote_target_line":376,"footnote_citation_statement_ids":["st-chp8-p218-bottari-citation"],"footnote_pending":False}),
    row("st-chp8-p218-zanchi-described-as-venetian", "cand-2834", "cand-3401", "described_as_venetian", (84,84),
        "Haskell describes Antonio Zanchi as a young Venetian.", "the young Venetian, Antonio Zanchi",
        "This records the source's regional descriptor; it does not independently establish birthplace, residence, or citizenship.",
        mentioned=["cand-2834","cand-3401"]),
    row("st-chp8-p218-committee-more-cautious-after-ferri", "cand-7641", "cand-1027", "haskell_described_committee_as_more_wary_after_ferri", (84,84),
        "Haskell says the committee was more wary after its experience engaging Ferri.",
        "By now the committee were in a much more wary frame of mind than they had been when engaging Ciro Ferri.",
        "This is Haskell's characterization of the committee's attitude, not a separate contractual term.",
        relation=False, mentioned=["cand-7641","cand-1027"]),
    row("st-chp8-p218-zanchi-no-fee-and-return-terms", "cand-7641", "cand-2834", "no_fee_for_drawings_and_return_without_fee_if_picture_unsatisfactory", (84,84),
        "Zanchi was to receive no payment for submitting drawings; even if approved, an unsatisfactory painting made in Bergamo would be returned without fee.",
        "Zanchi was to get no payment for submitting his drawings; even if they were approved and if the picture itself—which was to be painted in Bergamo—then turned out to be unsatisfactory it would be returned to him without fee.",
        "These are conditional terms reported by Haskell, not a statement that Zanchi's drawings or painting were rejected.",
        mentioned=["cand-7641","cand-2834","cand-11491","cand-7670","cand-6208"]),
    row("st-chp8-p218-experts-set-price-if-accepted", "cand-7641", "cand-7670", "experts_to_set_price_if_picture_accepted", (84,84),
        "Haskell says experts would decide the price if the picture was accepted.", "If it was accepted, experts would decide on the price.",
        "The experts are not identified, and the statement is a conditional term rather than a completed price decision.",
        mentioned=["cand-7641","cand-7670"]),
    row("st-chp8-p218-terms-exceptionally-hard", "cand-7641", "cand-2834", "haskell_judged_zanchi_terms_exceptionally_hard", (84,84),
        "Haskell judges the terms exceptionally hard and unlike those of a normal contract.",
        "These terms were exceptionally hard and quite unlike those laid down in a normal contract.",
        "This is Haskell's evaluation of the conditions, not an independently established comparison across contracts.",
        relation=False, mentioned=["cand-7641","cand-2834"]),
    row("st-chp8-p218-zanchi-agrees-to-terms", "cand-2834", "cand-7641", "zanchi_agreed_to_all_terms", (84,84),
        "Haskell says Zanchi agreed to everything.", "He agreed to everything",
        "This records the reported acceptance of the terms; it does not imply that every later event went smoothly.", mentioned=["cand-2834","cand-7641"]),
    row("st-chp8-p218-zanchi-site-visit-and-venice-permission", "cand-2834", "cand-3401", "zanchi_visited_bergamo_and_received_permission_to_paint_in_venice", (84,84),
        "During a visit to Bergamo to inspect the site, Zanchi asked for and received permission to paint the picture in Venice.",
        "on a visit to Bergamo to inspect the site he asked, and was given, permission to paint the picture in Venice.",
        "The permission is explicit; the reason for the location change is not supplied.",
        mentioned=["cand-2834","cand-6208","cand-3401","cand-7670"]),
    row("st-chp8-p218-zanchi-canvas-sent", "cand-7670", "cand-2834", "canvas_sent_to_zanchi_in_venice", (84,84),
        "Haskell says the canvas was sent to Zanchi in Venice.", "There the canvas was sent to him",
        "'There' refers to Venice; the sender is not named in this sentence.", mentioned=["cand-7670","cand-2834","cand-3401"]),
    row("st-chp8-p218-letters-urge-zanchi-to-hurry", "cand-7676", "cand-2834", "letters_complained_of_delay_and_urged_zanchi_to_hurry", (84,84),
        "Haskell reports letters that complained of delay and asked Zanchi to hurry.",
        "followed by letters complaining of the delay and asking him to hurry.",
        "The sender and dates are not stated; the archive candidate is normalized below to avoid assigning the letters to the committee without explicit wording.",
        mentioned=["cand-7676","cand-2834","cand-7670"]),
    row("st-chp8-p218-zanchi-canvas-completed-four-months", "cand-2834", "cand-7670", "zanchi_canvas_completed_within_four_months", (84,84),
        "Haskell says the canvas was completed within four months.", "In fact, it was completed within four months",
        "The source does not state the exact starting point for the four-month interval.", mentioned=["cand-2834","cand-7670"]),
    row("st-chp8-p218-committee-deliberates-on-zanchi-canvas", "cand-7641", "cand-7670", "committee_deliberated_almost_as_long_again", (84,84),
        "Haskell says the cautious committee took almost as long again to decide about the completed canvas.",
        "and it took the cautious committee almost as long again to make up their minds about it.",
        "This is Haskell's relative timing; no calendar dates for deliberation are specified.", mentioned=["cand-7641","cand-7670"]),
    row("st-chp8-p218-committee-accepts-zanchi-canvas", "cand-7641", "cand-7670", "committee_accepted_canvas_with_obvious_enthusiasm", (84,84),
        "Haskell says the committee accepted Zanchi's canvas with obvious enthusiasm.", "Eventually it was accepted with obvious enthusiasm",
        "The acceptance is reported by Haskell; the committee's deliberation record is not independently consulted.", mentioned=["cand-7641","cand-2834","cand-7670"]),
    row("st-chp8-p218-zanchi-receives-825-ducats", "cand-2834", "cand-7670", "zanchi_received_fee_of_825_ducats", (84,84),
        "Haskell says Zanchi was paid a fee of 825 ducats for the accepted painting.",
        "for Zanchi was paid the considerable fee of 825 ducats",
        "The fee is Haskell's reported amount; this does not independently establish the payment record.", mentioned=["cand-2834","cand-7670"]),
    row("st-chp8-p218-zanchi-merits-praise-open", "cand-7670", None, "haskell_praised_paintings_merits_and_colouring", (84,84),
        "Haskell says the fee was well deserved in view of the painting's dramatic merits and richly coloured appearance; the sentence continues on p.219.",
        "which he well deserved in view of the oustanding merits of this dramatic and richly",
        "This is Haskell's evaluation, not a relation or independent quality assessment. The p.219 continuation completes the description as richly coloured.",
        relation=False, mentioned=["cand-2834","cand-7670"],
        extra={"ocr_corrections":[{"source_file":SOURCE_REL,"source_line":84,"ocr":"oustanding","print":"outstanding","basis":"CHP-8.pdf physical page 20."}],
               "continuation_status":"closed","continuation_to_segment_id":"chp-8:08_CHP-8_sec_ii:l86-98","continuation_to_source_line":87,
               "continuation_fragment":"richly coloured picture in which the blues, reds and greens...",
               "continuation_resolved_by_segment":"chp-8:08_CHP-8_sec_ii:l86-98","continuation_resolved_by_source_line":87,
               "continuation_resolved_by_statement_id":"st-chp8-p219-zanchi-coloured-picture"}),
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
    writer.writeheader(); writer.writerows(rows)
    data = output.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" + data) if bom else data


def atomic_write(path, data):
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False, suffix=".tmp") as stream:
        stream.write(data); temporary = Path(stream.name)
    temporary.replace(path)


def make_statement(item):
    q = {
        "source_line_start": item["line_start"], "source_line_end": item["line_end"],
        "printed_page": 218, "pdf_physical_page": 20, "claim": item["claim"],
        "speaker": item["speaker"], "text_layer": "body", "qualification": item["qualification"],
        "mentioned_candidate_ids": item["mentioned"], "relation_candidate": item["relation"],
        "relation_candidate_note": item["note"],
    }
    q.update(item["extra"])
    return {"statement_id":item["statement_id"],"segment_id":SEGMENT_ID,
            "subject_candidate_id":item["subject"],"object_candidate_id":item["object"],
            "predicate":item["predicate"],"qualifiers":q,"original_quote":item["quote"],
            "origin":"book","source_file":SOURCE_REL}


def verify_inputs():
    for path, expected in EXPECTED_HASHES.items():
        actual = sha(path.read_bytes())
        if actual != expected:
            raise SystemExit(f"input changed: {path.relative_to(ROOT)} expected={expected} actual={actual}")
    segments = {r["segment_id"]:r for r in read_jsonl(TABLES/"segments.jsonl")}
    if SEGMENT_ID not in segments or segments[SEGMENT_ID].get("sha256") != SEGMENT_SHA:
        raise SystemExit("S0 segment identity or hash changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    for item in NEW_ROWS:
        excerpt = "\n".join(source_lines[item["line_start"]-1:item["line_end"]])
        if item["quote"] not in excerpt:
            raise SystemExit(f"quote is not an exact excerpt in its source lines: {item['statement_id']}")


def plan():
    statement_rows = read_jsonl(STATEMENTS)
    candidate_fields, candidate_rows, candidate_bom = read_csv(CANDIDATES)
    mention_fields, mention_rows, mention_bom = read_csv(MENTIONS)
    by_id = {r["statement_id"]:r for r in statement_rows}
    target_ids = {"st-chp8-p218-ferri-arrival-contract","st-chp8-p218-ferri-invitation-response",
        "st-chp8-p218-ferri-private-letters-and-subject","st-chp8-p218-ferri-schedule-and-work-progress",
        "st-chp8-p218-ferri-completion-status-1667","st-chp8-p218-ferri-leaves",
        "st-chp8-p218-zanchi-selected-for-moses","st-chp8-p218-zanchi-terms",
        "st-chp8-p218-zanchi-canvas-accepted"}
    unset = {r["statement_id"] for r in statement_rows if r.get("segment_id")==SEGMENT_ID and "relation_candidate" not in r.get("qualifiers",{})}
    if unset != target_ids - {"st-chp8-p218-zanchi-canvas-accepted"}:
        raise SystemExit(f"unexpected p.218 unset statements: {sorted(unset)}")
    if not target_ids <= by_id.keys(): raise SystemExit("expected p.218 source statements changed")
    if by_id["st-chp8-p218-zanchi-canvas-accepted"].get("qualifiers",{}).get("relation_candidate") is not True:
        raise SystemExit("the preclassified Zanchi row changed")
    new_ids={x["statement_id"] for x in NEW_ROWS}
    if len(new_ids)!=len(NEW_ROWS) or new_ids & by_id.keys(): raise SystemExit("new statement IDs collide")
    if set().union(*[set(x) for x in LINKS.values()]) != new_ids: raise SystemExit("new statement link coverage differs")

    candidate_by_id={r["candidate_id"]:r for r in candidate_rows}
    if max(int(r["candidate_id"].split("-")[1]) for r in candidate_rows)!=12058: raise SystemExit("candidate sequence changed")
    candidate_specs=[
        ("cand-12059","Unidentified picture planned above the side door adjoining Cappella Colleoni","work","chp-8:08_CHP-8_sec_ii:l78-84#L83","Haskell reports that the committee questioned its quality and consulted experts; this picture's identity relative to the later three remaining works is not explicit."),
        ("cand-12060","Three unidentified paintings remaining after Ciro Ferri left Santa Maria Maggiore","work","chp-8:08_CHP-8_sec_ii:l78-84#L84","Haskell identifies two large door paintings and one slightly smaller inner-wall painting; their individual subjects and identity links to other candidates are not specified."),
        ("cand-12061","Unidentified smaller painting for the inner wall of the North transept at Santa Maria Maggiore","work","chp-8:08_CHP-8_sec_ii:l78-84#L84","One of three paintings remaining after Ferri left; the source gives its relative size and location, but no subject or maker."),
    ]
    for cid,name,typ,ref,detail in candidate_specs:
        if cid in candidate_by_id or any(r.get("canonical_name","").casefold()==name.casefold() for r in candidate_rows):
            raise SystemExit(f"candidate natural key or ID already exists: {cid}")
    old_letter=candidate_by_id.get("cand-7676")
    if not old_letter or old_letter.get("canonical_name")!="Committee letters urging Antonio Zanchi to finish his canvas":
        raise SystemExit("cand-7676 state changed")
    if any(r.get("candidate_id")!="cand-7676" and r.get("canonical_name","").casefold()=="letters urging antonio zanchi to finish his canvas".casefold() for r in candidate_rows):
        raise SystemExit("normalized letter candidate natural key already exists")

    segment_text="\n".join(SOURCE.read_text(encoding="utf-8-sig").splitlines()[78:84])
    new_mentions=[
        {"mention_id":"m-chp8-p218-side-door-picture","segment_id":SEGMENT_ID,"candidate_id":"cand-12059","surface_form":"the picture","start_char":"1686","end_char":"1697","note":"The unnamed picture whose quality the committee questioned; the adjoining side door is a separate place mention."},
        {"mention_id":"m-chp8-p218-three-pictures","segment_id":SEGMENT_ID,"candidate_id":"cand-12060","surface_form":"Three pictures remained to be painted","start_char":"1913","end_char":"1950","note":"Open work group of three paintings remaining after Ferri left."},
        {"mention_id":"m-chp8-p218-smaller-inner-wall-picture","segment_id":SEGMENT_ID,"candidate_id":"cand-12061","surface_form":"one, slightly smaller","start_char":"1999","end_char":"2020","note":"Unidentified smaller painting for the inner wall of the North transept."},
        {"mention_id":"m-chp8-p218-zanchi-venetian","segment_id":SEGMENT_ID,"candidate_id":"cand-3401","surface_form":"Venetian","start_char":"2201","end_char":"2209","note":"Regional adjective in Haskell's description; it does not independently establish birthplace or citizenship."},
    ]
    for m in new_mentions:
        if m["mention_id"] in {r["mention_id"] for r in mention_rows}: raise SystemExit(f"mention ID exists: {m['mention_id']}")
        start,end=int(m["start_char"]),int(m["end_char"])
        if segment_text[start:end] != m["surface_form"]: raise SystemExit(f"mention span mismatch: {m['mention_id']} got={segment_text[start:end]!r}")

    for old_id,note in OLD_NOTES.items():
        q=by_id[old_id]["qualifiers"]
        q["relation_candidate"]=False
        q["relation_candidate_note"]=note
        q["linked_statement_ids"]=LINKS[old_id]

    # Resolve the p.217 -> p.218 phrase on the atomic request statement.
    p217=by_id["st-chp8-p217-ferri-request-details-open"]["qualifiers"]
    p217["continuation_status"]="closed"
    p217["continuation_fragment"]="once begin work on the sketches which he would then submit -for the committee’s approval."
    # The old composite carries no exclusive continuity pointer after atomization.
    p218_old=by_id["st-chp8-p218-ferri-invitation-response"]["qualifiers"]
    for key in ("continued_from_segment_id","continued_from_source_line","continued_from_statement_id","continuation_status"):
        p218_old.pop(key,None)

    # Rehome the cross-page close of the p.218 -> p.219 authorial evaluation.
    p218_accept=by_id["st-chp8-p218-zanchi-canvas-accepted"]["qualifiers"]
    p218_accept.setdefault("ocr_corrections",[]).append({"source_file":SOURCE_REL,"source_line":84,"ocr":"oustanding","print":"outstanding","basis":"CHP-8.pdf physical page 20."})
    p219=by_id["st-chp8-p219-zanchi-coloured-picture"]["qualifiers"]
    if p219.get("continued_from_statement_id")!="st-chp8-p218-zanchi-canvas-accepted": raise SystemExit("p.219 continuation source changed")
    p219["continued_from_statement_id"]="st-chp8-p218-zanchi-merits-praise-open"
    # Correct the old quoted-title OCR while preserving the normalized source.
    by_id["st-chp8-p218-zanchi-selected-for-moses"]["qualifiers"].setdefault("ocr_corrections",[]).append(
        {"source_file":SOURCE_REL,"source_line":84,"ocr":"Moses striking the RockJ","print":"Moses striking the Rock.¹","basis":"CHP-8.pdf physical page 20."})

    # Move footnote 1 from the mixed source row to the selected painting statement.
    citation=by_id["st-chp8-p218-bottari-citation"]
    citation["qualifiers"]["linked_body_statement_ids"]=["st-chp8-p218-zanchi-selected-for-moses-rock"]

    # The existing archive candidate did not name its sender in this passage.
    old_letter["canonical_name"]="Letters urging Antonio Zanchi to finish his canvas"
    old_letter["detail"]="Haskell reports letters that followed the sent canvas, complained of delay, and urged Zanchi to hurry; this passage does not name the sender or dates."

    for item in NEW_ROWS: statement_rows.append(make_statement(item))
    candidate_rows.extend({"candidate_id":cid,"index_entry_id":"","canonical_name":name,"index_page_range":"",
        "suggested_type":typ,"status":"open","index_source_file":"","sub_entry":"","detail":detail,
        "exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":ref}
        for cid,name,typ,ref,detail in candidate_specs)
    mention_rows.extend(new_mentions)

    statements_out=("\n".join(json.dumps(r,ensure_ascii=False,separators=(",",":")) for r in statement_rows)+"\n").encode("utf-8")
    summary={"existing_rows_reclassified_or_refined":len(target_ids),"new_statements":len(NEW_ROWS),
        "new_true":sum(x["relation"] for x in NEW_ROWS),"new_false":sum(not x["relation"] for x in NEW_ROWS),
        "new_work_candidates":3,"new_mentions":len(new_mentions),"candidate_detail_corrected":1,
        "p218_final_statements":sum(1 for r in statement_rows if r.get("segment_id")==SEGMENT_ID)}
    return statements_out,csv_bytes(candidate_fields,candidate_rows,candidate_bom),csv_bytes(mention_fields,mention_rows,mention_bom),summary


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--apply",action="store_true",help="write guarded plan; default dry-run")
    args=parser.parse_args(); verify_inputs(); outputs=plan()
    statements_out,candidates_out,mentions_out,summary=outputs
    print(json.dumps({"mode":"apply" if args.apply else "dry-run",**summary},ensure_ascii=False,indent=2))
    if not args.apply:return
    verify_inputs()
    output_map={STATEMENTS:statements_out,CANDIDATES:candidates_out,MENTIONS:mentions_out}
    for path,data in output_map.items():
        backup=path.with_name(path.name+BACKUP_SUFFIX)
        if backup.exists():
            if backup.read_bytes()!=path.read_bytes(): raise SystemExit(f"existing backup differs: {backup.name}")
        else: shutil.copy2(path,backup)
        if sha(backup.read_bytes())!=EXPECTED_HASHES[path]: raise SystemExit(f"backup hash mismatch: {backup.name}")
    for path,data in output_map.items():atomic_write(path,data)
    print("written_sha256="+json.dumps({path.name:sha(path.read_bytes()) for path in output_map},ensure_ascii=False))


if __name__=="__main__": main()
