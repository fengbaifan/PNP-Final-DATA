from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/03_CHP-3_sec_ii.md"
PDF = ROOT / "02-sources/01-book/CHP-3.pdf"
SEGMENT_ID = "chp-3:03_CHP-3_sec_ii:l74-81"
SOURCE_FILE = "02-sources/02-Markdown/03_CHP-3_sec_ii.md"
BACKUP_SUFFIX = ".bak-s2-chp3-sec-ii-l74-81-relations-20261010"

HASHES = {
    STATEMENTS: "9a3ec11ef7d043f612e5367a9e78fb2fb03d5f918e1f1d6ec71771de7434c876",
    CANDIDATES: "c8be066459de9f9819989899c04a85e6b86287843b3c67751b469daa3dc812ca",
    MENTIONS: "136c4227f382f12d0156a92d34c5572072be0ee6a5ccdcda0a1a9cac4947c0f8",
    COVERAGE: "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    SOURCE: "cb17a400fc5a79d895e31fe4a112c83e010f5e5b859883852b3985b7010eb1e6",
    PDF: "362e08518334ae5cda65cc1758f92ef4de6874b5982bfb6600187d889dc6785d",
}

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-11590",
        "index_entry_id": "",
        "canonical_name": "Lanfranco and Domenichino as a pair in the S. Andrea commission",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Bounded local collective referent for ‘the two artists’ at L78: Giovanni Lanfranco and "
            "Domenichino. This records the passage's pair reference, not a separate institution or a new "
            "artist identity; individual artist relations are also recorded separately."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L78",
    },
    {
        "candidate_id": "cand-11591",
        "index_entry_id": "",
        "canonical_name": "Correggio’s dome fresco at Parma (unnamed in source)",
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Haskell's elliptical comparison ‘Correggio’s in Parma’ refers back to the dome fresco just "
            "named for Lanfranco. The exact title and building are not supplied in this passage; do not "
            "add a canonical title without separate evidence."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L79",
    },
]

ORIGINALS = {
    "st-chp3-secii-l74-81-apse-scenes-depicted-life-of-andrew": {
        "subject": "cand-0934", "object": "cand-5067",
        "predicate": "portrayed_scenes_from_saint_life_in_apse", "relation": True,
        "note": "The source explicitly says Domenichino portrayed scenes from St Andrew's life in the apse; the specific scenes remain unnamed.",
    },
    "st-chp3-secii-l74-81-barberini-planning-after-work-proceeded": {
        "subject": "cand-0209", "object": "cand-4252",
        "predicate": "began_planning_family_chapel_after_project_progress", "relation": True,
        "note": "Haskell says work proceeded quickly enough for Maffeo Barberini to start planning his chapel a year later; preserve the relative interval and infer no exact year.",
    },
    "st-chp3-secii-l74-81-church-completed-by-1628": {
        "subject": "cand-11590", "object": "cand-5064",
        "predicate": "both_artists_completed_tasks_by_1628", "relation": False,
        "note": "This aggregate parent states that both artists completed their tasks; scalar artist-to-project rows below preserve the two individual relations without treating a temporary artist pair as one person.",
        "extras": {"artist_candidate_ids": ["cand-1359", "cand-0934"], "year": 1628},
    },
    "st-chp3-secii-l74-81-compromise-shared-commission-and-enmity": {
        "subject": "cand-11590", "object": "cand-5064",
        "predicate": "compromise_shared_commission_and_artist_enmity", "relation": False,
        "note": "This parent combines the compromise, the shared commission and the artists' enmity; scalar relations below separate collaboration from rivalry.",
        "extras": {"artist_candidate_ids": ["cand-1359", "cand-0934"], "compromise_status": "agreed; exact division beyond the dome is not specified here"},
        "ocr_corrections": [{
            "source_file": SOURCE_FILE, "source_line": 78, "ocr": "tire commission", "print": "the commission",
            "basis": "CHP-3.pdf physical page 10 (printed p.72).",
        }],
    },
    "st-chp3-secii-l74-81-decoration-major-baroque-achievement": {
        "subject": "cand-5064", "object": "cand-4500",
        "predicate": "called_most_important_baroque_achievement_yet", "relation": True,
        "note": "Haskell explicitly characterizes the decoration programme as a major Baroque achievement; preserve this as the author's attributed art-historical interpretation.",
    },
    "st-chp3-secii-l74-81-dome-light-and-heavenly-choirs": {
        "subject": "cand-5065", "object": "cand-5071",
        "predicate": "depicted_light_and_choirs_hymning_praise", "relation": False,
        "note": "This parent combines the Christic light and a choir group; scalar artwork-to-figure/group statements below keep the depicted endpoints distinct. The object is the dome choir group, not the putti in Domenichino's pendentives.",
    },
    "st-chp3-secii-l74-81-domenichino-evangelists-derived-from-michelangelo": {
        "subject": "cand-0934", "object": "cand-5066",
        "predicate": "produced_evangelist_figures_derived_from_michelangelo", "relation": False,
        "note": "This parent combines Domenichino's production of the pendentive figures with Haskell's Michelangelo comparison; scalar rows below separate the artist-to-work and work-to-artist claims.",
        "extras": {"comparison_artist_candidate_id": "cand-1661"},
    },
    "st-chp3-secii-l74-81-domenichino-requested-lanfranco-commission": {
        "subject": "cand-0934", "object": "cand-1459",
        "predicate": "asked_ludovisi_for_commission_instead_of_lanfranco", "relation": True,
        "note": "The source reports Domenichino's request to Ludovico Ludovisi; it does not give Domenichino an initial right to the commission or say that Ludovisi formally awarded it.",
        "extras": {"alternative_artist_candidate_id": "cand-1359"},
    },
    "st-chp3-secii-l74-81-finest-modern-church-and-theatine-comparison": {
        "subject": "cand-5197", "object": "cand-2565",
        "predicate": "church_evaluation_and_order_comparison_by_1628", "relation": False,
        "note": "This parent combines Haskell's evaluative ranking of S. Andrea with the Theatines' comparison to two other orders; scalar institutional comparisons are recorded separately, with no objective ranking implied.",
        "extras": {"comparison_institution_candidate_ids": ["cand-1321", "cand-1782"], "comparison_place_candidate_id": "cand-4490"},
    },
    "st-chp3-secii-l74-81-florentine-families-competed-over-chapels": {
        "subject": "cand-5044", "object": None,
        "predicate": "families_competed_to_make_chapels_most_beautiful", "relation": True,
        "note": "The passage describes other Florentine families competing over their chapels; individual families and chapel identities/counts are not supplied, so the object endpoint remains open.",
        "extras": {
            "speaker": "Anonymous Avviso author (as cited by Haskell)",
            "quoted_source_candidate_id": "cand-5155",
            "qualification": "Footnote 1 identifies the Avviso but not its speaker; no chapel is identified with Maffeo Barberini's earlier family chapel.",
            "open_endpoint_reason": "The text names a source-bounded group of other Florentine families but does not identify or count their individual chapels.",
        },
    },
    "st-chp3-secii-l74-81-lanfranco-dome-completed-and-influential": {
        "subject": "cand-5065", "object": None,
        "predicate": "dome_completion_comparison_and_later_model_influence", "relation": False,
        "note": "This parent combines a completion date, Haskell's comparison with Correggio and a later influence claim; the three scalar statements below preserve the separate status, work comparison and open influence endpoint.",
        "extras": {"artist_candidate_id": "cand-1359", "comparison_artist_candidate_id": "cand-0852", "comparison_place_candidate_id": "cand-3417"},
    },
    "st-chp3-secii-l74-81-largest-single-artist-commission-so-far": {
        "subject": "cand-5064", "object": "cand-1359",
        "predicate": "described_as_largest_commission_of_kind_yet_for_artist", "relation": True,
        "note": "Haskell describes the promised tribune-and-dome commission as the largest of its kind yet given to a single artist; the promise remains conditional and is not recorded as a completed award.",
    },
    "st-chp3-secii-l74-81-ludovisi-influence-overrode-no-formal-rights": {
        "subject": "cand-1459", "object": None,
        "predicate": "no_church_rights_and_influence_over_montalto", "relation": False,
        "note": "This parent combines Ludovisi's lack of rights in the church with his influence over Montalto; separate scalar negative-rights and influence relations are recorded below.",
        "extras": {"rights_target_candidate_id": "cand-5061", "influence_target_candidate_id": "cand-1876"},
    },
    "st-chp3-secii-l74-81-ludovisi-patron-of-domenichino": {
        "subject": "cand-1459", "object": None,
        "predicate": "nephew_of_gregory_xv_and_particular_patron_of_domenichino", "relation": False,
        "note": "This parent combines Ludovico Ludovisi's kinship to Gregory XV and patronage of Domenichino; separate person-to-person statements are recorded below.",
        "extras": {"kinship_target_candidate_id": "cand-1455", "patronage_target_candidate_id": "cand-0934"},
    },
    "st-chp3-secii-l74-81-montalto-insisted-lanfranco-get-dome": {
        "subject": "cand-1876", "object": "cand-1359",
        "predicate": "insisted_artist_receive_at_least_dome_commission", "relation": True,
        "note": "Haskell says Montalto insisted that Lanfranco receive at least the dome; this records the insistence, not a claim that the entire promised tribune commission was awarded.",
    },
    "st-chp3-secii-l74-81-montalto-promised-lanfranco-tribune-and-dome": {
        "subject": "cand-1876", "object": "cand-1359",
        "predicate": "conditionally_promised_tribune_and_dome_commission", "relation": True,
        "note": "The promise is dated to about 1616 and conditional on the time coming; it does not establish that the promised full commission was completed.",
    },
    "st-chp3-secii-l74-81-montalto-reserved-decoration-features": {
        "subject": "cand-1876", "object": "cand-5064",
        "predicate": "reserved_decoration_features_and_had_grandiose_plans", "relation": False,
        "note": "This parent combines Montalto reserving the decoration's main features for himself and having grandiose plans; scalar project relations below separate these claims.",
    },
    "st-chp3-secii-l74-81-paul-v-succeeded-by-gregory-xv": {
        "subject": "cand-0393", "object": "cand-1455",
        "predicate": "paul_v_death_and_gregory_xv_succession", "relation": False,
        "note": "This parent combines Paul V's death with Gregory XV's succession; the death is a person-level date attribute and the succession is recorded as a separate directed relation.",
        "extras": {
            "print_date": "1621",
            "ocr_note": "The source Markdown transcription reads ‘1625’; CHP-3.pdf physical page 10 (printed p.72) visibly reads ‘1621’. The source transcription is preserved in original_quote.",
            "ocr_corrections": [{
                "source_file": SOURCE_FILE, "source_line": 77, "ocr": "1625", "print": "1621",
                "basis": "CHP-3.pdf physical page 10 (printed p.72).",
            }],
        },
    },
    "st-chp3-secii-l74-81-pressure-awarded-job-to-domenichino": {
        "subject": "cand-1459", "object": "cand-0934",
        "predicate": "ludovisi_pressure_was_decisive_in_artist_receiving_job", "relation": True,
        "note": "Haskell says the pressure following Ludovisi's intervention was decisive and Domenichino received the job; the passive sentence does not identify the formal awarder.",
    },
    "st-chp3-secii-l74-81-theatines-not_part_of_commission_decisions": {
        "subject": "cand-2565", "object": "cand-5064",
        "predicate": "played_no_part_in_decoration_commission_decisions", "relation": True,
        "note": "This is an explicit negative relation: Haskell says the Theatines took no part in these decoration decisions.",
        "extras": {"negation": True},
    },
    "st-chp3-secii-l74-81-virgin-and-saints-in-dome-composition": {
        "subject": "cand-5065", "object": None,
        "predicate": "dome_composition_with_virgin_and_four_named_saints", "relation": False,
        "note": "This parent describes five distinct figures and their gestures/positions; scalar artwork-to-figure statements below record each depicted figure without asserting historical relations among the saints.",
        "extras": {"saint_candidate_ids": ["cand-4412", "cand-5068", "cand-4231", "cand-5069"], "figure_candidate_id": "cand-3427"},
    },
}

NEW_ROWS = [
    {
        "id": "st-chp3-secii-l74-81-lanfranco-completed-task-by-1628",
        "subject": "cand-1359", "object": "cand-5064", "predicate": "completed_task_on_project_by_year",
        "start": 81, "end": 81, "quote": "By 1628, when both artists had completed their tasks",
        "claim": "Haskell says Giovanni Lanfranco had completed his task on the S. Andrea decoration by 1628.",
        "note": "The group-level statement is made scalar for the named artist; the source gives 1628 as the outer date, not an exact completion day.",
        "extras": {"year": 1628, "project_candidate_id": "cand-5064"},
    },
    {
        "id": "st-chp3-secii-l74-81-domenichino-completed-task-by-1628",
        "subject": "cand-0934", "object": "cand-5064", "predicate": "completed_task_on_project_by_year",
        "start": 81, "end": 81, "quote": "By 1628, when both artists had completed their tasks",
        "claim": "Haskell says Domenichino had completed his task on the S. Andrea decoration by 1628.",
        "note": "The group-level statement is made scalar for the named artist; the source gives 1628 as the outer date, not an exact completion day.",
        "extras": {"year": 1628, "project_candidate_id": "cand-5064"},
    },
    {
        "id": "st-chp3-secii-l74-81-lanfranco-domenichino-became-enemies",
        "subject": "cand-1359", "object": "cand-0934", "predicate": "became_irreconcilable_enemies",
        "start": 78, "end": 78, "quote": "the two artists, by now irreconcilable enemies",
        "claim": "Haskell says Giovanni Lanfranco and Domenichino had become irreconcilable enemies by this point.",
        "note": "The source directly characterizes the two artists as enemies; no cause or date of the enmity is supplied.",
    },
    {
        "id": "st-chp3-secii-l74-81-lanfranco-domenichino-shared-commission",
        "subject": "cand-1359", "object": "cand-0934", "predicate": "shared_decoration_commission_with",
        "start": 78, "end": 78, "quote": "shared tire commission",
        "claim": "Haskell says Lanfranco and Domenichino shared the S. Andrea decoration commission after a compromise.",
        "note": "The printed page reads ‘the commission’; retain the compromise and shared commission while leaving the exact allocation beyond Lanfranco's dome unspecified.",
        "extras": {"commission_candidate_id": "cand-5064", "compromise_status": "agreed"},
        "ocr_corrections": [{
            "source_file": SOURCE_FILE, "source_line": 78, "ocr": "tire commission", "print": "the commission",
            "basis": "CHP-3.pdf physical page 10 (printed p.72).",
        }],
    },
    {
        "id": "st-chp3-secii-l74-81-lanfranco-dome-depicts-christ-as-light-source",
        "subject": "cand-5065", "object": "cand-4141", "predicate": "depicts_christ_as_source_of_lantern_light",
        "start": 79, "end": 79,
        "quote": "Light is the centre, radiating out from Christ, its source in the lantern",
        "claim": "Haskell describes Christ as the source of the light radiating from the lantern in Lanfranco's dome fresco.",
        "note": "This records Haskell's visual description of the fresco, not a theological assertion.",
        "extras": {"location_in_work": "lantern; light radiates across the dome surface"},
    },
    {
        "id": "st-chp3-secii-l74-81-lanfranco-dome-choirs-hymn-praises",
        "subject": "cand-5065", "object": "cand-5071", "predicate": "depicts_choir_group_hymning_praises",
        "start": 79, "end": 79,
        "quote": "around which the choirs of saints, martyrs, prophets, apostles and cherubs hymn their praises",
        "claim": "Haskell describes the choir group of saints, martyrs, prophets, apostles and cherubs in Lanfranco's dome fresco as hymning praise.",
        "note": "The choir group is the existing collective candidate cand-5071; the separate putti cand-5072 belong to Domenichino's pendentive figures on the next page line.",
    },
    {
        "id": "st-chp3-secii-l74-81-domenichino-produced-evangelist-figures",
        "subject": "cand-0934", "object": "cand-5066", "predicate": "produced_pendentive_evangelist_figures",
        "start": 80, "end": 80,
        "quote": "he produced in the pendentives four monumental figures of the Evangelists",
        "claim": "Haskell says Domenichino produced four monumental Evangelist figures in the pendentives at S. Andrea della Valle.",
        "note": "This records the named artist-to-work relation; the following Michelangelo comparison is a separate interpretive claim.",
    },
    {
        "id": "st-chp3-secii-l74-81-evangelist-figures-derived-from-michelangelo",
        "subject": "cand-5066", "object": "cand-1661", "predicate": "figures_described_as_derived_from_artist",
        "start": 80, "end": 80,
        "quote": "four monumental figures of the Evangelists, clearly derived from Michelangelo",
        "claim": "Haskell describes the Evangelist figures in Domenichino's pendentives as clearly derived from Michelangelo.",
        "note": "This is Haskell's art-historical interpretation, not an independently verified influence claim.",
        "extras": {"interpretation_by_candidate_id": "cand-1661"},
    },
    {
        "id": "st-chp3-secii-l74-81-theatines-outdistanced-jesuits",
        "subject": "cand-2565", "object": "cand-1321", "predicate": "outdistanced_order_in_church_patronage_by_1628",
        "start": 81, "end": 81,
        "quote": "the Theatines without much effort on their part had far outdistanced the Jesuits and the Oratorians",
        "claim": "Haskell says the Theatines had far outdistanced the Jesuits in the S. Andrea church and decoration context by 1628.",
        "note": "Preserve Haskell's comparative evaluation and ‘without much effort’ qualification; no objective measure is implied.",
        "extras": {"comparison_context_candidate_id": "cand-5064", "year": 1628, "qualification": "Haskell's evaluative comparison; no quantitative measure is supplied."},
    },
    {
        "id": "st-chp3-secii-l74-81-theatines-outdistanced-oratorians",
        "subject": "cand-2565", "object": "cand-1782", "predicate": "outdistanced_order_in_church_patronage_by_1628",
        "start": 81, "end": 81,
        "quote": "the Theatines without much effort on their part had far outdistanced the Jesuits and the Oratorians",
        "claim": "Haskell says the Theatines had far outdistanced the Oratorians in the S. Andrea church and decoration context by 1628.",
        "note": "Preserve Haskell's comparative evaluation and ‘without much effort’ qualification; no objective measure is implied.",
        "extras": {"comparison_context_candidate_id": "cand-5064", "year": 1628, "qualification": "Haskell's evaluative comparison; no quantitative measure is supplied."},
    },
    {
        "id": "st-chp3-secii-l74-81-lanfranco-dome-completed-1627",
        "subject": "cand-5065", "object": None, "predicate": "completed_in_year",
        "start": 79, "end": 79, "quote": "Lanfranco’s dome, which was completed in 1627",
        "claim": "Haskell says Lanfranco's dome fresco was completed in 1627.",
        "note": "This is a work completion-date attribute; footnote 3 follows this date and cites Pastor as the source locator.",
        "relation": False, "extras": {"year": 1627, "artist_candidate_id": "cand-1359"},
    },
    {
        "id": "st-chp3-secii-l74-81-lanfranco-dome-compared-with-correggio-parma",
        "subject": "cand-5065", "object": "cand-11591", "predicate": "first_of_kind_since_comparison_dome_fresco",
        "start": 79, "end": 79,
        "quote": "was the first of its kind since Correggio’s in Parma more than a century earlier",
        "claim": "Haskell characterizes Lanfranco's dome as the first of its kind since Correggio's dome fresco at Parma, more than a century earlier.",
        "note": "The comparison directly relates two dome fresco works; the Correggio work is retained without an inferred title or building identity.",
        "extras": {"comparison_artist_candidate_id": "cand-0852", "comparison_place_candidate_id": "cand-3417", "time_relation": "more than a century earlier", "qualification": "Haskell's historical characterization."},
    },
    {
        "id": "st-chp3-secii-l74-81-lanfranco-dome-model-for-later-artists",
        "subject": "cand-5065", "object": None, "predicate": "served_as_model_to_later_artists",
        "start": 79, "end": 79, "quote": "it served as a model to artists for the next hundred years",
        "claim": "Haskell says Lanfranco's dome fresco served as a model to artists for the next hundred years.",
        "note": "The source identifies a broad artist class but no bounded artists or group; leave the object endpoint open and retain Haskell's duration claim.",
        "extras": {"time_horizon": "the next hundred years (Haskell's wording)", "open_endpoint_reason": "The source names no individual artists or bounded artist group who used the dome as a model."},
    },
    {
        "id": "st-chp3-secii-l74-81-ludovisi-had-no-rights-in-the-church",
        "subject": "cand-1459", "object": "cand-5061", "predicate": "held_no_rights_in_the_theatine_church",
        "start": 78, "end": 78, "quote": "Ludovisi had no rights whatsoever in the church",
        "claim": "Haskell says Ludovico Ludovisi had no rights in the Theatine church project under discussion.",
        "note": "This is an explicit negative rights claim about the prior Theatine church candidate cand-5061; its identity relation to the separately named S. Andrea candidate remains for S3 alignment.",
        "speaker": "Haskell", "extras": {"negation": True, "candidate_identity_question": ["cand-5061", "cand-5197"]},
    },
    {
        "id": "st-chp3-secii-l74-81-ludovisi-influence-over-montalto",
        "subject": "cand-1459", "object": "cand-1876", "predicate": "applied_papal_nephew_influence_over",
        "start": 78, "end": 78,
        "quote": "he had all the irresistible power that came from his position as papal nephew and he began to apply it to Montalto",
        "claim": "As Haskell reports Passeri, Ludovico Ludovisi applied the influence of his papal-nephew position to Cardinal Peretti-Montalto.",
        "note": "Attribute the ‘irresistible power’ characterization to Passeri through Haskell; keep this influence relation separate from the statement that Ludovisi had no church rights.",
        "speaker": "Haskell reporting Passeri", "text_layer": "authorial narrative with cited interpretation",
    },
    {
        "id": "st-chp3-secii-l74-81-ludovico-nephew-of-gregory-xv",
        "subject": "cand-1459", "object": "cand-1455", "predicate": "nephew_of",
        "start": 77, "end": 77, "quote": "whose nephew Cardinal Ludovisi",
        "claim": "Haskell identifies Cardinal Ludovico Ludovisi as a nephew of Gregory XV.",
        "note": "The kinship direction is nephew to uncle; this is distinct from Ludovisi's patronage of Domenichino.",
    },
    {
        "id": "st-chp3-secii-l74-81-ludovico-particular-patron-of-domenichino",
        "subject": "cand-1459", "object": "cand-0934", "predicate": "particular_patron_of",
        "start": 77, "end": 77, "quote": "Cardinal Ludovisi was the particular patron of Domenichino",
        "claim": "Haskell identifies Cardinal Ludovico Ludovisi as Domenichino's particular patron.",
        "note": "Preserve Haskell's specific ‘particular patron’ wording; this statement does not establish who formally awarded the commission.",
    },
    {
        "id": "st-chp3-secii-l74-81-montalto-retained-decoration-control",
        "subject": "cand-1876", "object": "cand-5064", "predicate": "reserved_main_features_of_decoration_for_himself",
        "start": 76, "end": 76, "quote": "had reserved the main features of the decoration for himself",
        "claim": "Haskell says Cardinal Peretti-Montalto reserved the main features of the S. Andrea decoration for himself.",
        "note": "This records control over the decoration features; the separate grandiose-plans claim remains in its own statement.",
    },
    {
        "id": "st-chp3-secii-l74-81-montalto-grandiose-decoration-plans",
        "subject": "cand-1876", "object": "cand-5064", "predicate": "had_grandiose_plans_for_decoration",
        "start": 76, "end": 76, "quote": "he too had grandiose plans",
        "claim": "Haskell says Cardinal Peretti-Montalto also had grandiose plans for the church decoration.",
        "note": "The source supplies no further detail about the plans; do not infer their content or execution.",
    },
    {
        "id": "st-chp3-secii-l74-81-paul-v-died-1621",
        "subject": "cand-0393", "object": None, "predicate": "died_in_year",
        "start": 77, "end": 77, "quote": "in 1625 Pope Paul V died",
        "claim": "The printed page says Pope Paul V died in 1621.",
        "note": "This is a person-level death-year attribute. The source Markdown's 1625 transcription is retained in original_quote and corrected against the page image in S2.",
        "relation": False, "extras": {
            "year": 1621,
            "ocr_corrections": [{
                "source_file": SOURCE_FILE, "source_line": 77, "ocr": "1625", "print": "1621",
                "basis": "CHP-3.pdf physical page 10 (printed p.72).",
            }],
        },
    },
    {
        "id": "st-chp3-secii-l74-81-gregory-xv-succeeded-paul-v",
        "subject": "cand-1455", "object": "cand-0393", "predicate": "succeeded_as_pope",
        "start": 77, "end": 77, "quote": "was succeeded by Gregory XV",
        "claim": "Haskell says Gregory XV succeeded Paul V as pope in 1621.",
        "note": "The direction is successor Gregory XV to predecessor Paul V; the source gives the sequence, and the printed date 1621 is separately recorded on the death statement.",
        "extras": {"year": 1621, "office": "pope"},
    },
    {
        "id": "st-chp3-secii-l74-81-lanfranco-dome-depicts-virgin",
        "subject": "cand-5065", "object": "cand-3427", "predicate": "depicts_iconographic_figure",
        "start": 79, "end": 79, "quote": "Towards that light the Virgin gazes in ecstasy",
        "claim": "Haskell describes the Virgin gazing toward the light in Lanfranco's dome fresco.",
        "note": "This is a visual relation in the composition, not a historical relation between the Virgin and the named saints.",
        "extras": {"iconographic_role": "central figure; gazes toward the light; arms extended to welcome it and gesture toward surrounding figures"},
    },
    {
        "id": "st-chp3-secii-l74-81-lanfranco-dome-depicts-st-andrew",
        "subject": "cand-5065", "object": "cand-4412", "predicate": "depicts_iconographic_figure",
        "start": 79, "end": 79, "quote": "St Andrew who sponsors S. Gaetano",
        "claim": "Haskell identifies St Andrew as one of the figures on either side of the Virgin in Lanfranco's dome fresco.",
        "note": "The sponsor wording describes the iconographic composition; do not convert it into a historical patronage edge between the saints.",
        "extras": {"iconographic_role": "adoring figure beside the Virgin; shown as sponsor of S. Gaetano in the composition"},
    },
    {
        "id": "st-chp3-secii-l74-81-lanfranco-dome-depicts-s-gaetano",
        "subject": "cand-5065", "object": "cand-5068", "predicate": "depicts_iconographic_figure",
        "start": 79, "end": 79, "quote": "S. Gaetano, founder of the Theatine order",
        "claim": "Haskell identifies S. Gaetano as one of the figures on either side of the Virgin in Lanfranco's dome fresco.",
        "note": "This is an iconographic figure relation; the source's founder description is retained as context.",
        "extras": {"iconographic_role": "adoring figure beside the Virgin; identified as founder of the Theatine order"},
    },
    {
        "id": "st-chp3-secii-l74-81-lanfranco-dome-depicts-st-peter",
        "subject": "cand-5065", "object": "cand-4231", "predicate": "depicts_iconographic_figure",
        "start": 79, "end": 79, "quote": "St Peter with St Andrew Avellino",
        "claim": "Haskell identifies St Peter as one of the figures on either side of the Virgin in Lanfranco's dome fresco.",
        "note": "This is a visual relation in the composition; no historical relation between the two named figures is inferred from ‘with’. ",
        "extras": {"iconographic_role": "adoring figure beside the Virgin; shown with St Andrew Avellino"},
    },
    {
        "id": "st-chp3-secii-l74-81-lanfranco-dome-depicts-st-andrew-avellino",
        "subject": "cand-5065", "object": "cand-5069", "predicate": "depicts_iconographic_figure",
        "start": 79, "end": 79, "quote": "St Andrew Avellino, the Theatine beatified in 1624",
        "claim": "Haskell identifies St Andrew Avellino as one of the figures on either side of the Virgin in Lanfranco's dome fresco.",
        "note": "This is a visual relation in the composition; the 1624 beatification date is retained as the author's identifying context.",
        "extras": {"iconographic_role": "adoring figure beside the Virgin; Haskell identifies him as beatified in 1624"},
    },
]

ORIGINAL_ENDPOINTS = {
    "st-chp3-secii-l74-81-apse-scenes-depicted-life-of-andrew": ("cand-0934", "cand-5067"),
    "st-chp3-secii-l74-81-barberini-planning-after-work-proceeded": ("cand-0209", "cand-4252"),
    "st-chp3-secii-l74-81-church-completed-by-1628": ("cand-0697", "cand-5064"),
    "st-chp3-secii-l74-81-compromise-shared-commission-and-enmity": ("cand-1360", "cand-0934"),
    "st-chp3-secii-l74-81-decoration-major-baroque-achievement": ("cand-0697", "cand-4500"),
    "st-chp3-secii-l74-81-dome-light-and-heavenly-choirs": ("cand-5065", "cand-5072"),
    "st-chp3-secii-l74-81-domenichino-evangelists-derived-from-michelangelo": ("cand-0934", "cand-5066"),
    "st-chp3-secii-l74-81-domenichino-requested-lanfranco-commission": ("cand-0934", "cand-1459"),
    "st-chp3-secii-l74-81-finest-modern-church-and-theatine-comparison": ("cand-0697", "cand-2565"),
    "st-chp3-secii-l74-81-florentine-families-competed-over-chapels": ("cand-5044", None),
    "st-chp3-secii-l74-81-lanfranco-dome-completed-and-influential": ("cand-1360", "cand-5065"),
    "st-chp3-secii-l74-81-largest-single-artist-commission-so-far": ("cand-5064", "cand-1360"),
    "st-chp3-secii-l74-81-ludovisi-influence-overrode-no-formal-rights": ("cand-1459", "cand-1877"),
    "st-chp3-secii-l74-81-ludovisi-patron-of-domenichino": ("cand-1455", "cand-1459"),
    "st-chp3-secii-l74-81-montalto-insisted-lanfranco-get-dome": ("cand-1877", "cand-1360"),
    "st-chp3-secii-l74-81-montalto-promised-lanfranco-tribune-and-dome": ("cand-1877", "cand-1360"),
    "st-chp3-secii-l74-81-montalto-reserved-decoration-features": ("cand-1877", "cand-5064"),
    "st-chp3-secii-l74-81-paul-v-succeeded-by-gregory-xv": ("cand-0393", "cand-1455"),
    "st-chp3-secii-l74-81-pressure-awarded-job-to-domenichino": ("cand-1459", "cand-0934"),
    "st-chp3-secii-l74-81-theatines-not_part_of_commission_decisions": ("cand-2565", "cand-5064"),
    "st-chp3-secii-l74-81-virgin-and-saints-in-dome-composition": ("cand-5065", "cand-3427"),
}

MENTION_UPDATES = {
    "m-chp3-secii-l74-81-0006": ("cand-1876", None),
    "m-chp3-secii-l74-81-0008": ("cand-1359", None),
    "m-chp3-secii-l74-81-0016": ("cand-5061", "The definite ‘church’ refers to the Theatine building candidate carried from the preceding paragraph; its identity with cand-5197 remains for S3 alignment."),
    "m-chp3-secii-l74-81-0018": ("cand-1876", None),
    "m-chp3-secii-l74-81-0020": ("cand-1359", None),
    "m-chp3-secii-l74-81-0021": ("cand-5064", "S0 reads ‘tire commission’; the printed page reads ‘the commission’. The object is the shared S. Andrea decoration commission."),
    "m-chp3-secii-l74-81-0023": ("cand-11590", "Bounded local pair reference to Giovanni Lanfranco and Domenichino; not an independent organization."),
    "m-chp3-secii-l74-81-0025": ("cand-5197", None),
    "m-chp3-secii-l74-81-0027": ("cand-1359", None),
    "m-chp3-secii-l74-81-0032": ("cand-5071", "This mention is the choir group in Lanfranco's dome; the putti in Domenichino's pendentives remain cand-5072."),
    "m-chp3-secii-l74-81-0048": ("cand-5197", None),
}

NEW_MENTION = {
    "mention_id": "m-chp3-secii-l74-81-0053",
    "segment_id": SEGMENT_ID,
    "candidate_id": "cand-11591",
    "surface_form": "Correggio’s in Parma",
    "start_char": "1856",
    "end_char": "1876",
    "note": "Elliptical reference to Correggio's dome fresco; title and exact building are not named in the passage.",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path) -> tuple[list[str], list[dict], bytes]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader), raw


def encode_jsonl(rows: list[dict], raw: bytes) -> bytes:
    bom = raw.startswith(b"\xef\xbb\xbf")
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    output = []
    for index, row in enumerate(rows):
        encoded = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if index == 0 and bom:
            encoded = b"\xef\xbb\xbf" + encoded
        output.append(encoded + newline)
    return b"".join(output)


def encode_csv(fields: list[str], rows: list[dict], raw: bytes) -> bytes:
    bom = raw.startswith(b"\xef\xbb\xbf")
    newline = "\r\n" if b"\r\n" in raw else "\n"
    with tempfile.SpooledTemporaryFile(mode="w+", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator=newline)
        writer.writeheader()
        writer.writerows(rows)
        handle.seek(0)
        payload = handle.read().encode("utf-8")
    return (b"\xef\xbb\xbf" + payload) if bom else payload


def exact_row(rows: list[dict], key: str, value: str) -> dict:
    matches = [row for row in rows if row.get(key) == value]
    require(len(matches) == 1, f"expected exactly one {key}={value}; found {len(matches)}")
    return matches[0]


def is_bilateral(row: dict) -> bool:
    return bool(row.get("subject_candidate_id") and row.get("object_candidate_id"))


def stats(statements: list[dict], candidates: list[dict], mentions: list[dict]) -> dict:
    bilateral = [row for row in statements if is_bilateral(row)]
    relation_true = [row for row in statements if (row.get("qualifiers") or {}).get("relation_candidate") is True]
    return {
        "statements": len(statements),
        "candidates": len(candidates),
        "mentions": len(mentions),
        "segment_statements": sum(row.get("segment_id") == SEGMENT_ID for row in statements),
        "bilateral": len(bilateral),
        "bilateral_true": sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in bilateral),
        "bilateral_false": sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in bilateral),
        "bilateral_pending": sum((row.get("qualifiers") or {}).get("relation_candidate") is None for row in bilateral),
        "relation_candidates_total": len(relation_true),
        "relation_candidates_open": sum(not is_bilateral(row) for row in relation_true),
    }


def make_child(spec: dict, source_lines: list[str]) -> dict:
    q = {
        "source_line_start": spec["start"],
        "source_line_end": spec["end"],
        "claim": spec["claim"],
        "speaker": spec.get("speaker", "Haskell"),
        "text_layer": spec.get("text_layer", "authorial narrative"),
        "print_page": 72,
        "pdf_physical_page": 10,
        "relation_candidate": spec.get("relation", True),
        "relation_candidate_note": spec["note"],
    }
    q.update(spec.get("extras", {}))
    if spec.get("ocr_corrections"):
        q["ocr_corrections"] = spec["ocr_corrections"]
    row = {
        "statement_id": spec["id"],
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": spec["subject"],
        "object_candidate_id": spec.get("object"),
        "predicate": spec["predicate"],
        "qualifiers": q,
        "original_quote": spec["quote"],
        "origin": "book",
        "source_file": SOURCE_FILE,
    }
    anchor = "\n".join(source_lines[spec["start"] - 1:spec["end"]])
    normalize = lambda value: re.sub(r"\s+", " ", value).strip()
    require(normalize(spec["quote"]) in normalize(anchor), f"quote is not in its source lines: {spec['id']}")
    return row


def atomic_write(path: Path, payload: bytes) -> None:
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as handle:
            handle.write(payload)
            temp_path = Path(handle.name)
        os.replace(temp_path, path)
    except Exception:
        if temp_path and temp_path.exists():
            temp_path.unlink()
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="apply the reviewed S2 classifications and endpoint corrections")
    args = parser.parse_args()

    for path, expected in HASHES.items():
        actual = digest(path)
        require(actual == expected, f"preflight hash changed for {path.relative_to(ROOT)}: {actual}")

    table_raw = STATEMENTS.read_bytes()
    candidate_fields, candidates, candidate_raw = read_csv(CANDIDATES)
    mention_fields, mentions, mention_raw = read_csv(MENTIONS)
    coverage_fields, coverage, _ = read_csv(COVERAGE)
    statement_rows = read_jsonl(STATEMENTS)
    require((len(statement_rows), len(candidates), len(mentions), len(coverage)) == (12722, 11567, 27506, 832), "unexpected S2 pre-state totals")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    manifest = {row["segment_id"]: row for row in read_jsonl(SEGMENTS)}
    segment = manifest.get(SEGMENT_ID)
    require(segment is not None, "target segment missing from S0 manifest")
    segment_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
    require(segment.get("source_file") == SOURCE_FILE and segment.get("line_start") == 74 and segment.get("line_end") == 81, "S0 segment range changed")
    require(hashlib.sha256(segment_text.encode("utf-8")).hexdigest() == segment.get("sha256") == "881c76485302a6fe279c20dc914ac52a85000e88dbf6981c2ffcf670a7d5f133", "S0 segment content hash changed")
    require(segment.get("asset_sha256") == HASHES[SOURCE], "S0 segment asset hash mismatch")
    require("1625 Pope Paul V died" in source_lines[76] and "shared tire commission" in source_lines[77], "expected S0 OCR readings changed")

    coverage_row = exact_row(coverage, "segment_id", SEGMENT_ID)
    require((coverage_row["disposition"], coverage_row["migration_status"], coverage_row["source_line_ranges"]) == ("reviewed", "complete", "L75-81"), "target coverage state changed")

    by_id = {row["statement_id"]: row for row in statement_rows}
    target_rows = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
    require(len(target_rows) == 21, f"expected 21 target statements, found {len(target_rows)}")
    require({row["statement_id"] for row in target_rows} == set(ORIGINALS), "target statement ID set changed")
    for statement_id, expected_endpoints in ORIGINAL_ENDPOINTS.items():
        row = by_id[statement_id]
        require((row.get("subject_candidate_id"), row.get("object_candidate_id")) == expected_endpoints, f"pre-state endpoints changed: {statement_id}")
        q = row.get("qualifiers") or {}
        require(q.get("relation_candidate") is None, f"target statement already classified: {statement_id}")
        start, end = q.get("source_line_start"), q.get("source_line_end")
        require(isinstance(start, int) and isinstance(end, int) and 75 <= start <= end <= 81, f"invalid source anchor on {statement_id}")
        anchor = "\n".join(source_lines[start - 1:end])
        normalize = lambda value: re.sub(r"\s+", " ", value).strip()
        require(normalize(row.get("original_quote", "")) in normalize(anchor), f"original quote no longer matches S0 on {statement_id}")

    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    require("cand-11590" not in candidate_by_id and "cand-11591" not in candidate_by_id, "a proposed candidate ID already exists")
    require(max(int(row["candidate_id"].split("-")[1]) for row in candidates) == 11589, "candidate ID sequence changed")
    canonical_names = {row["canonical_name"].casefold() for row in candidates}
    require(all(row["canonical_name"].casefold() not in canonical_names for row in NEW_CANDIDATES), "natural-key duplicate candidate exists")

    mention_by_id = {row["mention_id"]: row for row in mentions}
    target_mentions = [row for row in mentions if row.get("segment_id") == SEGMENT_ID]
    require(len(target_mentions) == 52, f"expected 52 target mentions, found {len(target_mentions)}")
    require("m-chp3-secii-l74-81-0053" not in mention_by_id, "new mention ID already exists")
    require(segment_text[1856:1876] == NEW_MENTION["surface_form"], "new Correggio work mention span does not match the page-72 segment")
    for mention_id, (candidate_id, note) in MENTION_UPDATES.items():
        row = mention_by_id.get(mention_id)
        require(row is not None and row.get("segment_id") == SEGMENT_ID, f"mention missing or moved: {mention_id}")
        require(row["candidate_id"] != candidate_id or note is not None, f"mention already has target mapping: {mention_id}")

    new_statement_ids = [spec["id"] for spec in NEW_ROWS]
    require(len(new_statement_ids) == 26 and len(set(new_statement_ids)) == 26, "new statement plan must contain 26 unique IDs")
    require(not (set(new_statement_ids) & set(by_id)), "a proposed statement ID already exists")
    require(set(ORIGINALS) == set(ORIGINAL_ENDPOINTS), "original statement plan mismatch")

    for statement_id, config in ORIGINALS.items():
        row = by_id[statement_id]
        q = dict(row.get("qualifiers") or {})
        row["subject_candidate_id"] = config["subject"]
        row["object_candidate_id"] = config["object"]
        row["predicate"] = config["predicate"]
        q["relation_candidate"] = config["relation"]
        q["relation_candidate_note"] = config["note"]
        q.update(config.get("extras", {}))
        if "ocr_corrections" in config:
            q["ocr_corrections"] = config["ocr_corrections"]
        if statement_id == "st-chp3-secii-l74-81-paul-v-succeeded-by-gregory-xv":
            q["ocr_note"] = config["extras"]["ocr_note"]
        row["qualifiers"] = q

    for mention_id, (candidate_id, note) in MENTION_UPDATES.items():
        row = mention_by_id[mention_id]
        row["candidate_id"] = candidate_id
        if note is not None:
            row["note"] = note
    mentions.append(NEW_MENTION)
    candidates.extend(NEW_CANDIDATES)

    for spec in NEW_ROWS:
        statement_rows.append(make_child(spec, source_lines))

    note2 = exact_row(statement_rows, "statement_id", "st-chp3-secii-p72-note2-passeri")
    note3 = exact_row(statement_rows, "statement_id", "st-chp3-secii-p72-note3-pastor")
    q2 = dict(note2.get("qualifiers") or {})
    q3 = dict(note3.get("qualifiers") or {})
    require(q2.get("linked_body_statement_ids") == ["st-chp3-secii-l74-81-ludovisi-influence-overrode-no-formal-rights"], "p.72 note 2 backlink changed")
    require(q3.get("linked_body_statement_ids") == ["st-chp3-secii-l74-81-lanfranco-dome-completed-and-influential"], "p.72 note 3 backlink changed")
    q2["linked_body_statement_ids"] = [
        "st-chp3-secii-l74-81-ludovisi-had-no-rights-in-the-church",
        "st-chp3-secii-l74-81-ludovisi-influence-over-montalto",
    ]
    q3["linked_body_statement_ids"] = ["st-chp3-secii-l74-81-lanfranco-dome-completed-1627"]
    note2["qualifiers"] = q2
    note3["qualifiers"] = q3

    all_candidate_ids = {row["candidate_id"] for row in candidates}
    require(len(all_candidate_ids) == len(candidates), "duplicate candidate_id after plan")
    require(len({row["statement_id"] for row in statement_rows}) == len(statement_rows), "duplicate statement_id after plan")
    require(len({row["mention_id"] for row in mentions}) == len(mentions), "duplicate mention_id after plan")
    require(all(row.get("candidate_id") in all_candidate_ids for row in mentions), "mention references missing candidate")
    for row in statement_rows:
        for key in ("subject_candidate_id", "object_candidate_id"):
            candidate_id = row.get(key)
            require(not candidate_id or candidate_id in all_candidate_ids, f"statement has missing {key}: {row['statement_id']} -> {candidate_id}")

    after = stats(statement_rows, candidates, mentions)
    expected_after = {
        "statements": 12748,
        "candidates": 11569,
        "mentions": 27507,
        "segment_statements": 47,
        "bilateral": 8536,
        "bilateral_true": 4700,
        "bilateral_false": 473,
        "bilateral_pending": 3363,
        "relation_candidates_total": 4749,
        "relation_candidates_open": 49,
    }
    require(after == expected_after, f"unexpected projected counts: {after}")

    statement_payload = encode_jsonl(statement_rows, table_raw)
    candidate_payload = encode_csv(candidate_fields, candidates, candidate_raw)
    mention_payload = encode_csv(mention_fields, mentions, mention_raw)
    payloads = {STATEMENTS: statement_payload, CANDIDATES: candidate_payload, MENTIONS: mention_payload}
    result = {
        "action": "apply" if args.apply else "dry-run",
        "segment_id": SEGMENT_ID,
        "printed_page": 72,
        "pdf_physical_page": 10,
        "original_statement_count": len(ORIGINALS),
        "original_bilateral_count": 20,
        "new_statement_count": len(NEW_ROWS),
        "new_candidate_ids": [row["candidate_id"] for row in NEW_CANDIDATES],
        "mention_remappings": len(MENTION_UPDATES),
        "new_mentions": 1,
        "p72_note2_links": q2["linked_body_statement_ids"],
        "p72_note3_links": q3["linked_body_statement_ids"],
        "before": {"statements": 12722, "candidates": 11567, "mentions": 27506},
        "after": after,
        "payload_sha256": {path.name: hashlib.sha256(payload).hexdigest() for path, payload in payloads.items()},
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not args.apply:
        print("Dry run only. Pass --apply to write.")
        return

    paths = list(payloads)
    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in paths}
    require(all(not backup.exists() for backup in backups.values()), "a recovery backup already exists; refusing to overwrite")
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    try:
        for path, payload in payloads.items():
            atomic_write(path, payload)
        require(all(digest(path) == hashlib.sha256(payload).hexdigest() for path, payload in payloads.items()), "written hash mismatch")
        written_statements = read_jsonl(STATEMENTS)
        written_candidates = read_csv(CANDIDATES)[1]
        written_mentions = read_csv(MENTIONS)[1]
        require(stats(written_statements, written_candidates, written_mentions) == expected_after, "post-write readback totals differ")
        written_by_id = {row["statement_id"]: row for row in written_statements}
        require(all((written_by_id[sid].get("qualifiers") or {}).get("relation_candidate") is config["relation"] for sid, config in ORIGINALS.items()), "one or more original statements failed classification readback")
        require(all((written_by_id[spec["id"]].get("qualifiers") or {}).get("relation_candidate") is spec.get("relation", True) for spec in NEW_ROWS), "one or more scalar statements failed readback")
    except Exception:
        for path, backup in backups.items():
            if backup.exists():
                shutil.copy2(backup, path)
        raise
    result["result"] = "applied"
    result["backups"] = [str(path.relative_to(ROOT)) for path in backups.values()]
    result["sha256_after"] = {path.name: digest(path) for path in payloads}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
