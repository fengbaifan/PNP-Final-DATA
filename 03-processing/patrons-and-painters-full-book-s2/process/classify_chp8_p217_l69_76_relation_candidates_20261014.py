"""Guarded S2 semantic review for printed p.217, lines 69-76."""
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
PAGE_IMAGE = ROOT / "scripts" / ".tmp_s2_chp8_p217_review.png"
SEGMENT_ID = "chp-8:08_CHP-8_sec_ii:l69-76"
SEGMENT_SHA = "424e930247b9ca7b94a47d08addacc2514789fa1eaed04515ade100ac939b7d1"
NEW_FRESCO_CANDIDATE = "cand-12058"
BACKUP_SUFFIX = ".bak-s2-chp8-p217-l69-76-relation-review-20261014"
EXPECTED_HASHES = {
    STATEMENTS: "119865bb85ab9b59c3635d5a92a42972960946f6db746516f640669270d97f91",
    CANDIDATES: "9fb6e5f4c1a91b222dc9aee880661ab99dab31c275603050e212cbad9c18e857",
    MENTIONS: "c0215326495ebc3370f48f7c8d399299060ad4ace75e7b962224eda8a59264a6",
    COVERAGE: "6207ec3734deacfe3e02ec341c3a558440f7273ad4f9c2c964ad94ab2710fc34",
    SOURCE: "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    PDF: "cb11451ac726f37ed5badf21a569af88f790f858f1c39eb63f2efb58a0fe4ac3",
    PAGE_IMAGE: "3d1d2c301ffd11e923366879f14fd85f63ecdb0be08ddc6b8b9f3cf2a2d1b604",
}

OLD_IDS = {
    "st-chp8-p217-north-transept-scheme",
    "st-chp8-p217-liberi-contract",
    "st-chp8-p217-flood-rejected",
    "st-chp8-p217-flood-repainted-placed",
    "st-chp8-p217-last-judgement-cancelled",
    "st-chp8-p217-liberi-reception-uncertain-cause",
    "st-chp8-p217-ferri-selected-invited-open",
    "st-chp8-p217-ferri-cannot-leave-open",
}

FALSE_NOTES = {
    "st-chp8-p217-liberi-contract": (
        "This excerpt combines the committee's move from Milan to Venice, Liberi's reputation, "
        "the 1660 contract and its terms, Haskell's impression about Santa Maria Maggiore, and "
        "the later arrival of The Flood. These claims are separated below."
    ),
    "st-chp8-p217-flood-rejected": (
        "This excerpt bundles The Flood's arrival, the committee's rejection and letter, the "
        "repainting and placement, Liberi's return to Venice, the later sketch, and cancellation. "
        "The distinct actions are recorded below."
    ),
    "st-chp8-p217-flood-repainted-placed": (
        "This excerpt bundles the first canvas's arrival and rejection, the letter's demands, "
        "Liberi's later arrival, repainting and placement, his return to Venice, the second-picture "
        "sketch, and cancellation. The distinct actions are recorded below."
    ),
    "st-chp8-p217-last-judgement-cancelled": (
        "This combines the sending of a sketch, its rejection, and cancellation of Liberi's "
        "contract. Each action is recorded separately below."
    ),
    "st-chp8-p217-liberi-reception-uncertain-cause": (
        "This is Haskell's broader interpretation of the hostile reception, combining uncertainty, "
        "stylistic judgments, comparisons with other painters, a probable local objection, and an "
        "assessment of Liberi's use of the subjects. Preserve the attribution and uncertainty; the "
        "probable-cause claim is isolated below."
    ),
    "st-chp8-p217-ferri-selected-invited-open": (
        "This combines Ferri's selection, his invitation, Haskell's description of him as Cortona's "
        "follower, his work on Cortona's frescoes at Palazzo Pitti, and Ferri's response. The claims "
        "are separated below; follower remains a source descriptor, not a formal pupil claim."
    ),
    "st-chp8-p217-ferri-cannot-leave-open": (
        "This combines Ferri's inability to leave Florence with his request for details to begin "
        "sketches. They are recorded separately; the open request continues at p.218 L79."
    ),
}

LINKS = {
    "st-chp8-p217-liberi-contract": [
        "st-chp8-p217-committee-turns-to-venice",
        "st-chp8-p217-contract-signed-1660",
        "st-chp8-p217-contract-terms",
        "st-chp8-p217-liberi-reputation",
        "st-chp8-p217-smm-attracts-considerable-painter",
        "st-chp8-p217-flood-arrives-after-seven-months",
    ],
    "st-chp8-p217-flood-rejected": [
        "st-chp8-p217-flood-arrives-after-seven-months",
        "st-chp8-p217-committee-rejects-flood",
        "st-chp8-p217-committee-sends-letter",
        "st-chp8-p217-letter-demands-repaint-and-suspension",
    ],
    "st-chp8-p217-flood-repainted-placed": [
        "st-chp8-p217-flood-arrives-after-seven-months",
        "st-chp8-p217-committee-rejects-flood",
        "st-chp8-p217-letter-demands-repaint-and-suspension",
        "st-chp8-p217-liberi-arrives-after-year",
        "st-chp8-p217-flood-repainted",
        "st-chp8-p217-flood-placed-south-door",
        "st-chp8-p217-liberi-returns-to-venice",
        "st-chp8-p217-last-judgement-sketch-sent",
        "st-chp8-p217-last-judgement-sketch-rejected",
        "st-chp8-p217-liberi-contract-cancelled",
    ],
    "st-chp8-p217-last-judgement-cancelled": [
        "st-chp8-p217-last-judgement-sketch-sent",
        "st-chp8-p217-last-judgement-sketch-rejected",
        "st-chp8-p217-liberi-contract-cancelled",
    ],
    "st-chp8-p217-liberi-reception-uncertain-cause": [
        "st-chp8-p217-liberi-nudes-upset-bergamasque-susceptibilities",
    ],
    "st-chp8-p217-ferri-selected-invited-open": [
        "st-chp8-p217-committee-turns-to-venice",
        "st-chp8-p217-ferri-chosen-to-replace-liberi",
        "st-chp8-p217-ferri-follower-of-cortona",
        "st-chp8-p217-ferri-completing-cortona-frescoes",
        "st-chp8-p217-ferri-invited-to-bergamo",
    ],
    "st-chp8-p217-ferri-cannot-leave-open": [
        "st-chp8-p217-ferri-cannot-leave-florence",
        "st-chp8-p217-ferri-request-details-open",
    ],
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader), raw.startswith(b"\xef\xbb\xbf")


def csv_bytes(fields: list[str], rows: list[dict[str, str]], bom: bool) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    data = output.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" + data) if bom else data


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False, suffix=".tmp") as stream:
        stream.write(data)
        temporary = Path(stream.name)
    temporary.replace(path)


def make_statement(row: dict) -> dict:
    qualifiers = {
        "source_line_start": row["line_start"],
        "source_line_end": row["line_end"],
        "printed_page": 217,
        "pdf_physical_page": 19,
        "claim": row["claim"],
        "speaker": row.get("speaker", "Haskell"),
        "text_layer": "body",
        "qualification": row["qualification"],
        "mentioned_candidate_ids": row["mentioned"],
        "relation_candidate": row.get("relation", True),
        "relation_candidate_note": row["note"],
    }
    qualifiers.update(row.get("extra_qualifiers", {}))
    return {
        "statement_id": row["statement_id"],
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": row.get("subject"),
        "object_candidate_id": row.get("object"),
        "predicate": row["predicate"],
        "qualifiers": qualifiers,
        "original_quote": row["quote"],
        "origin": "book",
        "source_file": SOURCE_REL,
    }


NEW_ROWS = [
    {
        "statement_id": "st-chp8-p217-committee-turns-to-venice",
        "subject": "cand-7641", "object": "cand-3401", "predicate": "committee_turns_to_venice_for_artists",
        "line_start": 71, "line_end": 71,
        "claim": "Haskell says the committee, after first looking to Milan for artists, turned to Venice as another traditional source.",
        "quote": "Whereas in the first stage of the decoration they had looked primarily to Milan for artists they now turned instead to their other traditional source—Venice.",
        "qualification": "The pronoun refers to the committee in the preceding account; this records the change in source for artists, not the origin of any individual painter.",
        "mentioned": ["cand-7641", "cand-3418", "cand-3401"],
        "note": "This is the committee's source selection for artists. It does not identify or assign authorship to a particular Venetian painter.",
    },
    {
        "statement_id": "st-chp8-p217-contract-signed-1660",
        "subject": "cand-1401", "object": "cand-7663", "predicate": "contracted_to_paint_sixteen_picture_scheme",
        "line_start": 71, "line_end": 71,
        "claim": "Haskell reports that a contract for the sixteen-picture scheme was signed with Pietro Liberi in 1660.",
        "quote": "In 1660 a contract was signed with Pietro Liberi",
        "qualification": "The contract itself is not independently consulted; Haskell's report is the evidence here.",
        "mentioned": ["cand-1401", "cand-7663"],
        "note": "This records the reported contract between Liberi and the sixteen-picture scheme, without asserting that the contract document was independently verified.",
    },
    {
        "statement_id": "st-chp8-p217-contract-terms",
        "subject": "cand-1401", "object": "cand-7663", "predicate": "agreed_to_sixteen_pictures_for_3800_ducats_with_500_advance",
        "line_start": 71, "line_end": 71,
        "claim": "Haskell says Liberi agreed to paint all sixteen pictures for 3,800 ducats and received the first 500 as an advance guarantee.",
        "quote": "Liberi agreed to paint the entire sixteen pictures for 3 800 ducats and was paid the first 500 as an advance guarantee.",
        "qualification": "The amounts and terms are reported by Haskell and are not independently checked against the contract.",
        "mentioned": ["cand-1401", "cand-7663"],
        "note": "The statement preserves the reported total and advance as contract terms; it does not imply that all payments were made.",
        "extra_qualifiers": {"qualification_terms": ["3 800 ducats", "first 500", "advance guarantee"]},
    },
    {
        "statement_id": "st-chp8-p217-liberi-reputation",
        "subject": "cand-1401", "object": None, "predicate": "haskell_described_liberi_as_best_known_in_venice_with_european_reputation",
        "line_start": 71, "line_end": 71,
        "claim": "Haskell describes Liberi as the best-known artist in Venice at the time and already a man with a European reputation.",
        "quote": "Pietro Liberi, at that time the best known artist in the city and already a man with a European reputation.",
        "qualification": "The city is Venice from the immediately preceding sentence. This is Haskell's reputation assessment, not an independently measured ranking.",
        "mentioned": ["cand-1401", "cand-3401"],
        "relation": False,
        "note": "This is an attributed description of reputation, not a discrete relation between two entities.",
    },
    {
        "statement_id": "st-chp8-p217-smm-attracts-considerable-painter",
        "subject": "cand-7627", "object": "cand-1401", "predicate": "haskell_impression_of_attracting_a_considerable_painter",
        "line_start": 71, "line_end": 71,
        "claim": "Haskell says it must have seemed that Santa Maria Maggiore was at last able to attract a considerable painter.",
        "quote": "It must have seemed that Santa Maria Maggiore was at last able to attract a considerable painter.",
        "qualification": "This is Haskell's retrospective impression about the commission, not a direct statement by the committee.",
        "mentioned": ["cand-7627", "cand-1401"],
        "relation": False,
        "note": "This is an authorial evaluation of the commission's significance rather than a distinct entity relation.",
    },
    {
        "statement_id": "st-chp8-p217-flood-arrives-after-seven-months",
        "subject": "cand-7664", "object": "cand-6208", "predicate": "first_canvas_arrived_in_bergamo_after_seven_months",
        "line_start": 71, "line_end": 72,
        "claim": "Haskell says Liberi's first canvas, The Flood, arrived in Bergamo seven months after the contract.",
        "quote": "Seven-months later, his first canvas—The\nFlood—arrived in Bergamo.",
        "qualification": "The source gives a relative interval, not a calendar arrival date.",
        "mentioned": ["cand-1401", "cand-7664", "cand-6208", "cand-7663"],
        "note": "The canvas is identified with The Flood; preserve the seven-month relative interval and do not infer a calendar date.",
        "extra_qualifiers": {"qualification_terms": ["Seven months later"], "ocr_corrections": [{"source_file": SOURCE_REL, "source_line": 71, "ocr": "Seven-months", "print": "Seven months", "basis": "CHP-8.pdf physical page 19."}]},
    },
    {
        "statement_id": "st-chp8-p217-committee-rejects-flood",
        "subject": "cand-7641", "object": "cand-7664", "predicate": "committee_rejected_first_canvas",
        "line_start": 72, "line_end": 72,
        "claim": "Haskell says the committee did not like The Flood.",
        "quote": "But the committee did not like it.",
        "qualification": "The pronoun refers to Liberi's first canvas, The Flood.",
        "mentioned": ["cand-7641", "cand-7664"],
        "note": "The rejection is explicit in Haskell's account; the committee's quoted letter is recorded separately.",
    },
    {
        "statement_id": "st-chp8-p217-committee-sends-letter",
        "subject": "cand-7641", "object": "cand-7666", "predicate": "sent_letter_to_liberi_concerning_the_flood",
        "line_start": 72, "line_end": 72,
        "claim": "Haskell reports that the committee sent Liberi a letter about its dissatisfaction with The Flood.",
        "quote": "A cold letter was sent off to Liberi",
        "qualification": "The letter is identified through Haskell's account and has not been independently examined.",
        "mentioned": ["cand-7641", "cand-7666", "cand-1401", "cand-7664"],
        "note": "The archive candidate represents the specific reported letter; its text is available here only through Haskell's quotation.",
    },
    {
        "statement_id": "st-chp8-p217-letter-demands-repaint-and-suspension",
        "subject": "cand-7666", "object": "cand-7664", "predicate": "letter_demanded_repainting_and_suspension_of_other_work_and_payments",
        "line_start": 72, "line_end": 72,
        "claim": "The quoted letter demanded that The Flood be redone satisfactorily and that work and payments on the other commissioned pictures stop in the meantime.",
        "quote": "that it does not satisfy us and in no way corresponds to the promises that you made us, still less to what we expected. And so we require you to re-do it in a praiseworthy manner that satisfies us—meanwhile you must stop work on the other pictures which we commissioned and which you agreed to undertake, just as we will stop the payments in conformity with the contract.",
        "qualification": "These are demands as quoted by Haskell, not independently verified actions or proof that the suspension was fully carried out.",
        "mentioned": ["cand-7666", "cand-7664", "cand-7663", "cand-1401"],
        "note": "This records the reported contents of the committee's letter, distinguishing its instructions from completed repainting or payment events.",
    },
    {
        "statement_id": "st-chp8-p217-liberi-arrives-after-year",
        "subject": "cand-1401", "object": "cand-6208", "predicate": "liberi_arrived_in_bergamo_after_a_year",
        "line_start": 72, "line_end": 72,
        "claim": "Haskell says a year elapsed before Liberi arrived in Bergamo.",
        "quote": "It was a year before Liberi arrived in Bergamo",
        "qualification": "This sentence does not specify the exact starting event for the year interval or a calendar year.",
        "mentioned": ["cand-1401", "cand-6208"],
        "note": "Preserve the source's one-year interval without assigning it a more precise starting point.",
        "extra_qualifiers": {"qualification_terms": ["a year"]},
    },
    {
        "statement_id": "st-chp8-p217-flood-repainted",
        "subject": "cand-1401", "object": "cand-7664", "predicate": "liberi_repainted_the_flood_after_demand",
        "line_start": 72, "line_end": 72,
        "claim": "Haskell says Liberi repainted The Flood as demanded.",
        "quote": "after he had repainted the picture as demanded",
        "qualification": "Haskell attributes the repainting to Liberi; no exact date or distinct repainting version is supplied.",
        "mentioned": ["cand-1401", "cand-7664", "cand-7666"],
        "note": "The source explicitly links the repainting to the committee's demand; do not infer a date or present-day condition from this clause.",
    },
    {
        "statement_id": "st-chp8-p217-flood-placed-south-door",
        "subject": "cand-7664", "object": "cand-7631", "predicate": "flood_placed_above_south_door",
        "line_start": 72, "line_end": 72,
        "claim": "Haskell says the repainted Flood was placed above the south door and remained there at the time of his account.",
        "quote": "it was placed above the South door, where it still is.",
        "qualification": "'Still is' is time-bound to Haskell's account and is not a claim about current location.",
        "mentioned": ["cand-7664", "cand-7631", "cand-7627"],
        "note": "This records the reported placement of The Flood at the church and preserves the source's time boundary.",
    },
    {
        "statement_id": "st-chp8-p217-liberi-returns-to-venice",
        "subject": "cand-1401", "object": "cand-3401", "predicate": "returned_to_venice_to_continue_commission",
        "line_start": 72, "line_end": 72,
        "claim": "Haskell says Liberi returned to Venice to continue the commission.",
        "quote": "He then returned to Venice to carry on with the commission.",
        "qualification": "The source does not specify a date for the return.",
        "mentioned": ["cand-1401", "cand-3401", "cand-7663"],
        "note": "This is Liberi's reported return and continuing commission after the repainting; it is separate from the earlier committee turn to Venice for artists.",
    },
    {
        "statement_id": "st-chp8-p217-last-judgement-sketch-sent",
        "subject": "cand-1401", "object": "cand-7665", "predicate": "sent_sketch_instead_of_completing_second_picture",
        "line_start": 72, "line_end": 72,
        "claim": "Instead of completing the second picture, The Last Judgement, Liberi sent a sketch.",
        "quote": "instead of completing the second picture, The Last Judgement,he sent a sketch",
        "qualification": "The source reports a sketch, not a completed painting; it does not say that the sketch was executed as a separate finished work.",
        "mentioned": ["cand-1401", "cand-7665", "cand-7663"],
        "note": "Keep the sketch distinct from a completed second painting and preserve the second-picture role in the commission.",
        "extra_qualifiers": {"ocr_corrections": [{"source_file": SOURCE_REL, "source_line": 72, "ocr": "The Last Judgement,he", "print": "The Last Judgement, he", "basis": "CHP-8.pdf physical page 19."}]},
    },
    {
        "statement_id": "st-chp8-p217-last-judgement-sketch-rejected",
        "subject": "cand-7641", "object": "cand-7665", "predicate": "committee_rejected_last_judgement_sketch_as_deficient",
        "line_start": 72, "line_end": 72,
        "claim": "Haskell says the committee found Liberi's sketch for The Last Judgement deficient in every respect.",
        "quote": "This too was a total failure. The committee found it ‘deficient in every respect’",
        "qualification": "The judgment is reported by Haskell; the committee's record is not independently consulted.",
        "mentioned": ["cand-7641", "cand-7665", "cand-1401"],
        "note": "The rejected object is Liberi's sketch for the second picture, not a completed painting.",
    },
    {
        "statement_id": "st-chp8-p217-liberi-contract-cancelled",
        "subject": "cand-7641", "object": "cand-1401", "predicate": "contract_with_liberi_cancelled_after_sketch_rejection",
        "line_start": 72, "line_end": 72,
        "claim": "Haskell says the contract with Liberi was cancelled after the committee rejected his sketch.",
        "quote": "thereafter the contract with Liberi was cancelled.",
        "qualification": "The cancellation is Haskell's report; no separate cancellation document is quoted here.",
        "mentioned": ["cand-7641", "cand-1401", "cand-7665", "cand-7663"],
        "note": "The cancellation follows the committee's rejection of the second-picture sketch in Haskell's narrative.",
    },
    {
        "statement_id": "st-chp8-p217-liberi-nudes-upset-bergamasque-susceptibilities",
        "subject": "cand-1401", "object": None, "predicate": "haskell_probable_cause_liberi_nudes_upset_local_sensibilities",
        "line_start": 74, "line_end": 74,
        "claim": "Haskell considers it most probable that Liberi's highly erotic nudes upset Bergamasque susceptibilities.",
        "quote": "In fact it seems most probable that Pietro Liberi, who was notorious for the extreme indecency of his highly erotic nudes, had upset Bergamasque susceptibilities",
        "qualification": "This is Haskell's explicitly probable explanation, not a documented statement by the committee. Bergamasque is retained as a regional descriptor; the affected group is unnamed.",
        "mentioned": ["cand-1401", "cand-6208"],
        "note": "Retain Haskell's 'most probable' qualification and leave the affected local group unresolved instead of treating Bergamo city as the endpoint.",
        "extra_qualifiers": {"qualification_terms": ["seems most probable", "Bergamasque susceptibilities"], "linked_statement_ids": ["st-chp8-p217-liberi-reception-uncertain-cause"]},
    },
    {
        "statement_id": "st-chp8-p217-ferri-chosen-to-replace-liberi",
        "subject": "cand-7641", "object": "cand-1027", "predicate": "committee_chose_ferri_to_replace_liberi",
        "line_start": 75, "line_end": 75,
        "claim": "After its failed attempts in Venice, the committee chose Ciro Ferri to replace Pietro Liberi.",
        "quote": "Ciro Ferri, the artist whom they chose to replace Pietro Liberi",
        "qualification": "The pronoun refers to the committee; this records selection, separately from Ferri's invitation and response.",
        "mentioned": ["cand-7641", "cand-1027", "cand-1401"],
        "note": "The source names Ferri as the committee's replacement choice; selection does not imply that he had yet accepted or arrived.",
        "extra_qualifiers": {"linked_statement_ids": ["st-chp8-p217-committee-turns-to-venice"]},
    },
    {
        "statement_id": "st-chp8-p217-ferri-follower-of-cortona",
        "subject": "cand-1027", "object": "cand-0342", "predicate": "described_as_most_faithful_follower_of_cortona",
        "line_start": 75, "line_end": 75,
        "claim": "Haskell describes Ciro Ferri as Pietro da Cortona's most faithful follower.",
        "quote": "was the most faithful follower of Pietro da Cortona",
        "qualification": "'Follower' is Haskell's description and is not converted into a formal teacher-pupil relation.",
        "mentioned": ["cand-1027", "cand-0342"],
        "note": "Preserve the source's artistic-follower wording without asserting a formal apprenticeship.",
    },
    {
        "statement_id": "st-chp8-p217-ferri-completing-cortona-frescoes",
        "subject": "cand-1027", "object": NEW_FRESCO_CANDIDATE, "predicate": "completing_cortona_frescoes_at_palazzo_pitti",
        "line_start": 75, "line_end": 75,
        "claim": "Haskell says Ferri was then in Florence completing Pietro da Cortona's frescoes at Palazzo Pitti.",
        "quote": "was at this time in Florence completing his master’s frescoes in the Palazzo Pitti",
        "qualification": "The frescoes are not individually named. A new open work-group candidate records the source's identifiable group; no specific fresco is inferred.",
        "mentioned": ["cand-1027", "cand-0342", NEW_FRESCO_CANDIDATE, "cand-3397", "cand-7662"],
        "note": "This records Ferri's reported work on the unidentified Cortona fresco group at Palazzo Pitti; it does not assign Ferri authorship of Cortona's frescoes.",
        "extra_qualifiers": {
            "footnote_markers": [1], "footnote_link_status": "linked",
            "footnote_segment": "chp-8:08_CHP-8_sec_ii:l372-461", "footnote_target_line": 375,
            "footnote_citation_statement_ids": ["st-chp8-p217-bottari-citation"], "footnote_pending": False,
        },
    },
    {
        "statement_id": "st-chp8-p217-ferri-invited-to-bergamo",
        "subject": "cand-7641", "object": "cand-1027", "predicate": "committee_invited_ferri_to_bergamo_immediately",
        "line_start": 75, "line_end": 76,
        "claim": "Haskell says Ferri was asked to come to Bergamo at once to inspect the site, receive measurements and subjects, and arrange the price.",
        "quote": "He was asked to come at once to\nBergamo ‘to see where the pictures were to be painted, be given the measurements and the subjects, and arrange the price’.",
        "qualification": "The invitation is attributed to the committee from the surrounding context; it is distinct from Ferri's reply.",
        "mentioned": ["cand-7641", "cand-1027", "cand-6208", "cand-7663"],
        "note": "The requested visit concerned the site and commission terms; the statement does not imply that Ferri traveled at once.",
    },
    {
        "statement_id": "st-chp8-p217-ferri-cannot-leave-florence",
        "subject": "cand-1027", "object": "cand-3397", "predicate": "unable_to_leave_florence_at_that_moment",
        "line_start": 76, "line_end": 76,
        "claim": "Ferri replied that he was unable to leave Florence for the moment.",
        "quote": "He replied that he was unable to leave Florence for the moment",
        "qualification": "The source does not specify how long Ferri would be unable to leave.",
        "mentioned": ["cand-1027", "cand-3397"],
        "note": "This preserves Ferri's reported temporary inability to leave Florence without inferring its cause or duration.",
        "extra_qualifiers": {"linked_statement_ids": ["st-chp8-p217-ferri-invited-to-bergamo"]},
    },
    {
        "statement_id": "st-chp8-p217-ferri-request-details-open",
        "subject": "cand-1027", "object": "cand-7641", "predicate": "ferri_requested_details_to_begin_sketches",
        "line_start": 76, "line_end": 76,
        "claim": "Ferri asked for all necessary details to be sent to him so he could begin the sketches; the sentence continues on p.218 L79.",
        "quote": "but asked for all the necessary details to be sent to him so that he could at",
        "qualification": "The phrase is open at 'at' in this segment and closes with 'once begin work on the sketches' at p.218 L79.",
        "mentioned": ["cand-1027", "cand-7641"],
        "note": "This is Ferri's request to the committee; retain the cross-page continuation and do not treat the sketches as already completed.",
        "extra_qualifiers": {
            "continuation_status": "open",
            "continuation_to_segment_id": "chp-8:08_CHP-8_sec_ii:l78-84",
            "continuation_to_source_line": 79,
            "continuation_fragment": "once begin work on the sketches",
            "continuation_resolved_by_segment": "chp-8:08_CHP-8_sec_ii:l78-84",
            "continuation_resolved_by_source_line": 79,
            "continuation_resolved_by_statement_id": "st-chp8-p218-ferri-invitation-response",
            "linked_statement_ids": ["st-chp8-p217-ferri-invited-to-bergamo", "st-chp8-p217-ferri-cannot-leave-florence"],
        },
    },
]


def verify_inputs() -> None:
    for path, expected in EXPECTED_HASHES.items():
        actual = sha(path.read_bytes())
        if actual != expected:
            raise SystemExit(f"input changed: {path.relative_to(ROOT)} expected={expected} actual={actual}")
    segments = {row["segment_id"]: row for row in read_jsonl(TABLES / "segments.jsonl")}
    segment = segments.get(SEGMENT_ID)
    if not segment or segment.get("sha256") != SEGMENT_SHA:
        raise SystemExit("S0 segment identity or hash changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    for row in NEW_ROWS:
        excerpt = "\n".join(source_lines[row["line_start"] - 1:row["line_end"]])
        if row["quote"] not in excerpt:
            raise SystemExit(f"quote is not an exact excerpt in its source lines: {row['statement_id']}")


def plan() -> tuple[bytes, bytes, bytes, dict[str, int]]:
    statement_rows = read_jsonl(STATEMENTS)
    candidate_fields, candidate_rows, candidate_bom = read_csv(CANDIDATES)
    mention_fields, mention_rows, mention_bom = read_csv(MENTIONS)
    by_id = {row["statement_id"]: row for row in statement_rows}
    target_unset = {
        row["statement_id"] for row in statement_rows
        if row.get("segment_id") == SEGMENT_ID and "relation_candidate" not in row.get("qualifiers", {})
    }
    if target_unset != OLD_IDS:
        raise SystemExit(f"unexpected unset statement set: {sorted(target_unset)}")
    if not OLD_IDS <= by_id.keys():
        raise SystemExit("one or more expected source statements disappeared")
    p218 = by_id.get("st-chp8-p218-ferri-invitation-response")
    if not p218 or p218.get("qualifiers", {}).get("continued_from_statement_id") != "st-chp8-p217-ferri-cannot-leave-open":
        raise SystemExit("p.218 continuation link differs from the reviewed source state")

    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    if NEW_FRESCO_CANDIDATE in candidate_by_id:
        raise SystemExit("reserved candidate ID already exists")
    new_name = "Unidentified frescoes by Pietro da Cortona at Palazzo Pitti"
    if any(row.get("canonical_name", "").casefold() == new_name.casefold() for row in candidate_rows):
        raise SystemExit("natural-key candidate already exists; reuse its ID instead")
    max_id = max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows)
    if max_id != 12057:
        raise SystemExit(f"candidate sequence changed: expected max 12057, found {max_id}")

    required_mention_values = {
        "m-chp8-p217-master-frescoes": ("cand-0365", "his master’s frescoes"),
        "m-s2-surface-20b7b1f69c58ec12": ("cand-0712", "S. Maria Maggiore"),
    }
    seen_mentions = set()
    for row in mention_rows:
        if row["mention_id"] in required_mention_values:
            seen_mentions.add(row["mention_id"])
            expected_candidate, expected_surface = required_mention_values[row["mention_id"]]
            if row["candidate_id"] != expected_candidate or row["surface_form"] != expected_surface:
                raise SystemExit(f"mention state changed: {row['mention_id']}")
    if seen_mentions != set(required_mention_values):
        raise SystemExit("expected mentions for the source-mapping corrections are missing")

    false_link_ids = set().union(*[set(values) for values in LINKS.values()])
    new_ids = {row["statement_id"] for row in NEW_ROWS}
    if len(new_ids) != len(NEW_ROWS) or new_ids & by_id.keys():
        raise SystemExit("new statement IDs are duplicated or already present")
    if false_link_ids != new_ids:
        raise SystemExit(f"link coverage mismatch: unlinked={sorted(new_ids-false_link_ids)} stale={sorted(false_link_ids-new_ids)}")

    for statement_id, note in FALSE_NOTES.items():
        row = by_id[statement_id]
        qualifiers = row.setdefault("qualifiers", {})
        qualifiers["relation_candidate"] = False
        qualifiers["relation_candidate_note"] = note
        qualifiers["linked_statement_ids"] = LINKS[statement_id]

    # Close the p.216 -> p.217 scheme statement on the source text and preserve the cross-page link.
    north = by_id["st-chp8-p217-north-transept-scheme"]
    north["original_quote"] = (
        "paintings were required to correspond to those in the south, as well as one on the inner wall "
        "and two huge ones to be placed above the main North and South doors, in view of\n"
        "Guercino’s reluctance to comply with their request."
    )
    north["qualifiers"]["source_line_end"] = 71
    north["qualifiers"]["relation_candidate"] = True
    north["qualifiers"]["relation_candidate_note"] = (
        "This closes the committee's northern-transept plan begun on p.216 L35. The scheme's count and "
        "placement are source-reported; Guercino's reluctance explains the context, not an authorship assignment."
    )

    # Record visible OCR corrections without changing the normalized S0 source.
    reception = by_id["st-chp8-p217-liberi-reception-uncertain-cause"]["qualifiers"]
    reception.setdefault("ocr_corrections", []).append({
        "source_file": SOURCE_REL, "source_line": 74, "ocr": "them?'", "print": "them.",
        "basis": "CHP-8.pdf physical page 19.",
    })

    ferri_source = by_id["st-chp8-p217-ferri-selected-invited-open"]
    old_mentions = ferri_source["qualifiers"].get("mentioned_candidate_ids", [])
    ferri_source["qualifiers"]["mentioned_candidate_ids"] = [
        NEW_FRESCO_CANDIDATE if candidate_id == "cand-0365" else candidate_id
        for candidate_id in old_mentions
    ]

    cannot_leave = by_id["st-chp8-p217-ferri-cannot-leave-open"]["qualifiers"]
    for key in (
        "continuation_to_segment_id", "continuation_to_source_line", "continuation_fragment",
        "continuation_status", "continuation_resolved_by_segment", "continuation_resolved_by_source_line",
        "continuation_resolved_by_statement_id",
    ):
        cannot_leave.pop(key, None)
    p218["qualifiers"]["continued_from_statement_id"] = "st-chp8-p217-ferri-request-details-open"

    for row in NEW_ROWS:
        statement_rows.append(make_statement(row))

    candidate_rows.append({
        "candidate_id": NEW_FRESCO_CANDIDATE,
        "index_entry_id": "",
        "canonical_name": new_name,
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell reports that Ciro Ferri was completing this unidentified group of Cortona frescoes at Palazzo Pitti; no individual fresco or commission is named.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-8:08_CHP-8_sec_ii:l69-76#L75",
    })

    for row in mention_rows:
        if row["mention_id"] == "m-chp8-p217-master-frescoes":
            row["candidate_id"] = NEW_FRESCO_CANDIDATE
            row["note"] = "Unidentified group of Pietro da Cortona's frescoes at Palazzo Pitti; represented as a work group rather than the artist's index entry."
        elif row["mention_id"] == "m-s2-surface-20b7b1f69c58ec12":
            row["candidate_id"] = "cand-7627"
            row["note"] = "S. Maria Maggiore in Bergamo, the specific church discussed in this passage."

    statements_out = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in statement_rows) + "\n").encode("utf-8")
    candidates_out = csv_bytes(candidate_fields, candidate_rows, candidate_bom)
    mentions_out = csv_bytes(mention_fields, mention_rows, mention_bom)
    summary = {
        "old_classified": len(OLD_IDS),
        "new_statements": len(NEW_ROWS),
        "new_true": sum(row.get("relation", True) for row in NEW_ROWS),
        "new_false": sum(not row.get("relation", True) for row in NEW_ROWS),
        "new_candidates": 1,
        "corrected_mentions": 2,
        "p217_final_statements": len(OLD_IDS) + len(NEW_ROWS),
    }
    return statements_out, candidates_out, mentions_out, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the guarded plan; default is dry-run")
    args = parser.parse_args()
    verify_inputs()
    outputs = plan()
    statements_out, candidates_out, mentions_out, summary = outputs
    print(json.dumps({"mode": "apply" if args.apply else "dry-run", **summary}, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    verify_inputs()
    output_map = {STATEMENTS: statements_out, CANDIDATES: candidates_out, MENTIONS: mentions_out}
    for path, data in output_map.items():
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            if backup.read_bytes() != path.read_bytes():
                raise SystemExit(f"existing backup differs from current input: {backup.name}")
        else:
            shutil.copy2(path, backup)
        if sha(backup.read_bytes()) != EXPECTED_HASHES[path]:
            raise SystemExit(f"backup hash mismatch: {backup.name}")
    for path, data in output_map.items():
        atomic_write(path, data)
    print("written_sha256=" + json.dumps({path.name: sha(path.read_bytes()) for path in output_map}, ensure_ascii=False))


if __name__ == "__main__":
    main()
