"""Guarded S2 semantic review for printed p.220, lines 101-110."""
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
PAGE_IMAGE = ROOT / "scripts" / ".tmp_s2_chp8_p220_review.png"
SEGMENT_ID = "chp-8:08_CHP-8_sec_ii:l100-110"
SEGMENT_SHA = "cd70a832c602b19706438fe592610bfe7538613b21f1f8f5c66cd2056e88d72f"
BACKUP_SUFFIX = ".bak-s2-chp8-p220-l101-110-relation-review-20261014"
EXPECTED_HASHES = {
    STATEMENTS: "7a3b293b9832e86081b9fcee9959fb5b3bd949621454b7d41eb5f6bcc0d4b1af",
    CANDIDATES: "41619604d0734a104ef721508f603cf3c55244eca5b2e4f7a3317e4bd493de01",
    MENTIONS: "eed69d12aae2cb1b50785de44d91ba0ad8cafad650a9165681f07af1e907f23c",
    COVERAGE: "6207ec3734deacfe3e02ec341c3a558440f7273ad4f9c2c964ad94ab2710fc34",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    PDF: "cb11451ac726f37ed5badf21a569af88f790f858f1c39eb63f2efb58a0fe4ac3",
    PAGE_IMAGE: "8588921bde641ae85a4faf86b389f85a5627dc61862178e009318205fb6acd5b",
}

OLD_NOTES = {
    "st-chp8-p220-cignani-forli-cupola":
        "This combines Cignani's Forlì cupola painting, his intended comparison with Correggio's Parma work, and two artists' responses to restricted space. The work, comparison, and separate spatial claims are recorded below.",
    "st-chp8-p220-committee-self-funded-alternative":
        "This combines the committee's proposal to painters across Italy with the intended work group. The committee-to-group proposal and group-to-project relation are recorded separately.",
    "st-chp8-p220-david-offer":
        "This combines David learning of the project through an unnamed colleague, his full-project offer, and his alternative offer to share the scheme with other artists. The source and two offers are separated below.",
    "st-chp8-p220-david-payment-terms-objection":
        "This combines David's report of his previous payment practice with his objection to the committee's proposed terms. These are separated below; the former payment parties are not identified.",
    "st-chp8-p220-franceschini-approached":
        "This combines the committee's approach to Franceschini, a price comparison, his reduction after hearing of a potential rival, and the committee's move elsewhere. These claims are separated below; the rival remains unidentified.",
    "st-chp8-p220-giordano-spain-cignani-reapproached":
        "This combines Giordano's departure for Spain, the reported ten-year interval, and the committee's renewed approach to Cignani. These are separated below.",
    "st-chp8-p220-melanconici-abraham-open":
        "This combines Melanconici's pupilage, agreement to paint an experimental Abraham, and the picture's quick arrival, which continues into the p.221 approval statement. These are separated below.",
}

LINKS = {
    "st-chp8-p220-cignani-forli-cupola": [
        "st-chp8-p220-cignani-paints-forli-cupola",
        "st-chp8-p220-cignani-work-rivals-correggio",
        "st-chp8-p220-cignani-reluctant-about-reduced-space",
        "st-chp8-p220-ferri-disconcerted-by-space",
    ],
    "st-chp8-p220-committee-self-funded-alternative": [
        "st-chp8-p220-committee-cautious",
        "st-chp8-p220-committee-proposes-to-painters",
        "st-chp8-p220-painters-self-fund-central-nave-pictures",
    ],
    "st-chp8-p220-david-offer": [
        "st-chp8-p220-david-hears-about-project-from-colleague",
        "st-chp8-p220-david-wishes-to-prove-himself",
        "st-chp8-p220-david-writes-career-details",
        "st-chp8-p220-david-offers-all-pictures",
        "st-chp8-p220-david-offers-share-with-artists",
    ],
    "st-chp8-p220-david-payment-terms-objection": [
        "st-chp8-p220-david-reports-payment-practice",
        "st-chp8-p220-david-rejects-committee-terms",
    ],
    "st-chp8-p220-franceschini-approached": [
        "st-chp8-p220-committee-approaches-franceschini",
        "st-chp8-p220-franceschini-terms-costlier",
        "st-chp8-p220-franceschini-lowers-terms-after-rival",
        "st-chp8-p220-committee-turns-to-naples",
    ],
    "st-chp8-p220-giordano-spain-cignani-reapproached": [
        "st-chp8-p220-giordano-goes-to-spain",
        "st-chp8-p220-ten-year-interval",
        "st-chp8-p220-committee-reapproaches-cignani",
    ],
    "st-chp8-p220-melanconici-abraham-open": [
        "st-chp8-p220-melanconici-pupil-of-giordano",
        "st-chp8-p220-melanconici-agrees-abraham-experiment",
        "st-chp8-p220-abraham-picture-arrives-quickly",
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
    row("st-chp8-p220-cignani-paints-forli-cupola", "cand-0749", "cand-0751",
        "painted_cupola_work", (102, 103),
        "In 1692 Carlo Cignani was painting the cupola work of Forlì Cathedral.",
        "He was now painting the cupola of Forlì\nCathedral",
        "The index subentry is normalized as the cupola painting, kept distinct from Forlì Cathedral and the city.",
        mentioned=["cand-0749", "cand-0751", "cand-7692"]),
    row("st-chp8-p220-cignani-work-rivals-correggio", "cand-0751", "cand-11591",
        "work_intended_to_rival_comparator", (103, 103),
        "Cignani intended the Forlì cupola painting to rival Correggio's work at Parma.",
        "a work which he intended should rival Correggio’s at Parma",
        "The passage does not supply a title for Correggio's work; candidate cand-11591 preserves the earlier source-bounded Parma dome reference.",
        mentioned=["cand-0749", "cand-0751", "cand-11591", "cand-0852", "cand-3417"]),
    row("st-chp8-p220-cignani-reluctant-about-reduced-space", "cand-0749", "cand-7686",
        "reluctant_to_accept_reduced_space_for_project", (103, 103),
        "Haskell attributes Cignani's reluctance to work in a reduced space to his preoccupation with vast expanses.",
        "His preoccupation with vast expanses made him reluctant to engage on a reduced space",
        "The reduced space is discussed in the context of the fourteen central-nave paintings; the exact bay dimensions are not given.",
        mentioned=["cand-0749", "cand-7686", "cand-7685"]),
    row("st-chp8-p220-ferri-disconcerted-by-space", "cand-1027", "cand-7685",
        "earlier_disconcerted_by_reduced_church_space", (103, 103),
        "Haskell says the limitations of the reduced space had disconcerted Ciro Ferri about a quarter of a century earlier.",
        "the limitations of which had already disconcerted Ciro Ferri a quarter of a century earlier",
        "The passage does not identify the particular bay or surface; the surrounding account locates the space in the central-nave work at Santa Maria Maggiore.",
        mentioned=["cand-1027", "cand-7685", "cand-7627"]),
    row("st-chp8-p220-david-hears-about-project-from-colleague", "cand-0911", "cand-12062",
        "heard_about_project_from_colleague", (106, 106),
        "While in Rome, Ludovico David heard from an unnamed colleague and friend about the fourteen pictures required for the church.",
        "In Rome meanwhile the Swiss painter Ludovico David heard ‘from a colleague and friend of mine’ about the fourteen pictures that were needed.",
        "The colleague and friend is one unnamed source; do not infer identity or merge this person with David's later proposed collaborators.",
        speaker="Ludovico David, quoted by Haskell",
        mentioned=["cand-0911", "cand-4490", "cand-12062", "cand-7686"],
        extra={
            "footnote_markers": [1], "footnote_link_status": "linked",
            "footnote_segment": "chp-8:08_CHP-8_sec_ii:l372-461",
            "footnote_target_line": 379,
            "footnote_citation_statement_ids": ["st-chp8-p220-n1-bottari-citation"],
            "footnote_pending": False,
        }),
    row("st-chp8-p220-david-offers-all-pictures", "cand-0911", "cand-7686",
        "offered_to_paint_entire_project_for_fee", (106, 106),
        "David offered to paint all fourteen pictures within two and a half years for 3,500 scudi.",
        "offered to paint all the pictures within two and a half years at a price of 3500 scudi",
        "This is the reported offer; no acceptance or contract is stated.",
        speaker="Haskell reporting David's proposal",
        mentioned=["cand-0911", "cand-7686"]),
    row("st-chp8-p220-david-offers-share-with-artists", "cand-0911", "cand-12064",
        "offered_to_share_scheme_with_other_artists", (106, 106),
        "Alternatively, David offered to take a share of the scheme at a price to be agreed with other artists.",
        "or alternatively to take a share of the scheme at a price to be agreed with other artists",
        "The other artists are not named; this group is kept distinct from the two painters in David's later competitive proposal.",
        speaker="Haskell reporting David's proposal",
        mentioned=["cand-0911", "cand-12064", "cand-7686"]),
    row("st-chp8-p220-committee-proposes-to-painters", "cand-7641", "cand-12063",
        "proposed_self_funded_scheme_to_painters", (106, 106),
        "The committee proposed that painters across Italy produce three pictures each at their own expense, with no payment if the result proved unsatisfactory.",
        "The committee, whose experiences over the last half-century had understandably made them cautious, proposed instead that painters all over Italy should paint three pictures each, entirely at their own expense, and that if these proved unsatisfactory no payment at all would be made.",
        "This is a proposed arrangement, not evidence that painters accepted it or that the pictures were produced.",
        mentioned=["cand-7641", "cand-12063", "cand-3461", "cand-7686"]),
    row("st-chp8-p220-committee-cautious", "cand-7641", None,
        "haskell_assessed_committee_as_cautious", (106, 106),
        "Haskell attributes the committee's caution to its experience over the preceding half-century.",
        "The committee, whose experiences over the last half-century had understandably made them cautious",
        "This is Haskell's explanation of the committee's attitude, not a separately documented committee statement.",
        relation=False, mentioned=["cand-7641"]),
    row("st-chp8-p220-painters-self-fund-central-nave-pictures", "cand-12063", "cand-7686",
        "proposed_painters_to_produce_project_pictures", (106, 106),
        "Under the committee's proposal, painters across Italy would each paint three pictures for the fourteen-picture commission.",
        "painters all over Italy should paint three pictures each, entirely at their own expense",
        "The source describes a proposal only; the group and work count remain open, and no execution is asserted.",
        mentioned=["cand-12063", "cand-7686", "cand-7641"]),
    row("st-chp8-p220-david-reports-payment-practice", "cand-0911", None,
        "reported_prior_payment_practice", (106, 106),
        "David said he had previously received at least one quarter of an agreed price in advance and the balance immediately on completion.",
        "Hitherto he had always been paid at least a quarter of the agreed price in advance and the remainder immediately on completion of the work.",
        "The patrons and projects are not identified; this remains David's account of his own earlier practice.",
        relation=False, speaker="Ludovico David, quoted by Haskell",
        mentioned=["cand-0911"]),
    row("st-chp8-p220-david-wishes-to-prove-himself", "cand-0911", None,
        "reported_motive_to_prove_himself_at_site", (106, 106),
        "Haskell says David was anxious to prove himself at the notable site.",
        "Anxious to prove himself in ‘such a notable site’",
        "This is Haskell's account of David's motive, not evidence that the proposed commission was awarded.",
        relation=False, mentioned=["cand-0911", "cand-7686"]),
    row("st-chp8-p220-david-writes-career-details", "cand-0911", None,
        "wrote_with_details_of_career", (106, 106),
        "Haskell says David wrote giving details of his career before making his offer.",
        "he wrote giving details of his career",
        "The recipient and letter date are not specified in this clause.",
        relation=False, mentioned=["cand-0911", "cand-7686"]),
    row("st-chp8-p220-david-rejects-committee-terms", "cand-0911", "cand-7641",
        "rejected_committee_terms_on_professional_grounds", (106, 106),
        "David objected to the committee's proposed terms, saying that accepting them would shame him and degrade his profession.",
        "T could not without shaming myself allow it to be remembered by posterity that I had degraded my noble profession in this way.’",
        "The preceding sentences identify the committee's proposal as the object of David's objection; the quoted first-person wording is corrected from the OCR.",
        speaker="Ludovico David, quoted by Haskell",
        mentioned=["cand-0911", "cand-7641", "cand-7686"],
        extra={"ocr_corrections": [{
            "source_file": SOURCE_REL, "source_line": 106, "ocr": "T could not",
            "print": "I could not", "basis": "CHP-8.pdf physical page 22."
        }]}),
    row("st-chp8-p220-committee-approaches-franceschini", "cand-7641", "cand-1069",
        "approached_artist_for_project", (108, 109),
        "After finding David's proposal too complicated, the committee approached Marcantonio Franceschini for the project.",
        "All this was much too complicated for the committee, which applied instead to a\nBolognese pupil of Cignani, Marcantonio Franceschini.",
        "The committee is the grammatical actor; Franceschini is the named artist approached.",
        mentioned=["cand-7641", "cand-1069", "cand-7686"]),
    row("st-chp8-p220-franceschini-terms-costlier", "cand-1069", None,
        "reported_terms_costlier_than_other_artists", (109, 109),
        "Haskell says Franceschini's terms were more expensive than Cignani's or Giordano's.",
        "His terms were, however, even more expensive than his master’s or Luca Giordano’s had been",
        "This is a comparative assessment of terms; exact amounts and the comparison documents are not supplied.",
        relation=False, mentioned=["cand-1069", "cand-0749", "cand-1172"]),
    row("st-chp8-p220-franceschini-lowers-terms-after-rival", "cand-1069", "cand-12066",
        "reduced_terms_after_hearing_of_potential_rival", (109, 109),
        "After hearing of a potential rival, Franceschini hurriedly lowered his terms.",
        "on hearing of a potential rival he hurriedly brought them down",
        "The rival is unnamed and is not identified with Cignani, Giordano, or Melanconici.",
        mentioned=["cand-1069", "cand-12066", "cand-7686"]),
    row("st-chp8-p220-committee-turns-to-naples", "cand-7641", "cand-1722",
        "turned_to_naples_after_franceschini_negotiation", (109, 110),
        "After Franceschini lowered his terms, Haskell says the committee had already turned elsewhere and identifies the destination as Naples.",
        "the committee had already turned elsewhere.\nTo Naples, in fact—",
        "The next clause names Melanconici in Naples, but the source does not explicitly state that the committee directly approached him.",
        mentioned=["cand-7641", "cand-1722", "cand-1069", "cand-1636"]),
    row("st-chp8-p220-giordano-goes-to-spain", "cand-1172", "cand-5120",
        "went_to_spain_in_1692", (101, 101),
        "Luca Giordano went to Spain in 1692.",
        "when Giordano finally went to Spain",
        "The source supplies the year; it does not say that he completed the earlier Bergamo commission.",
        mentioned=["cand-1172", "cand-5120"]),
    row("st-chp8-p220-ten-year-interval", None, None,
        "reported_interval_since_original_approach", (101, 101),
        "Haskell says Giordano's departure for Spain came ten years after the committee's original approach.",
        "ten years after their original approach",
        "This is a chronology statement; it does not by itself identify all parties to or dates of the earlier approach.",
        relation=False, mentioned=["cand-1172", "cand-7641"]),
    row("st-chp8-p220-committee-reapproaches-cignani", "cand-7641", "cand-0749",
        "reapproached_artist_for_commission", (101, 101),
        "In 1692 the committee turned to Cignani once again.",
        "the committee turned to Cignani once again",
        "The source does not say whether Cignani accepted this renewed approach.",
        mentioned=["cand-7641", "cand-0749"]),
    row("st-chp8-p220-melanconici-pupil-of-giordano", "cand-1636", "cand-1172",
        "pupil_of_artist", (110, 110),
        "Haskell identifies Niccolò Melanconici as a pupil of Luca Giordano.",
        "a pupil of Luca Giordano, Niccolò Melanconici",
        "This is the relationship as stated by Haskell; no training dates or institution are given.",
        mentioned=["cand-1636", "cand-1172"]),
    row("st-chp8-p220-melanconici-agrees-abraham-experiment", "cand-1636", "cand-1637",
        "agreed_to_paint_abraham_at_own_expense_as_experiment", (110, 110),
        "Melanconici agreed to paint an Abraham at his own expense as an experiment.",
        "Niccolò Melanconici agreed to paint an Abraham at his own expense as an experiment.",
        "The source supplies no fuller title; the outcome of the experiment continues on p.221.",
        mentioned=["cand-1636", "cand-1637", "cand-7641", "cand-7686"]),
    row("st-chp8-p220-abraham-picture-arrives-quickly", "cand-1637", None,
        "picture_reported_arrived_quickly", (110, 110),
        "Haskell says the Abraham picture arrived quickly; the sentence continues with its reception on p.221.",
        "The picture arrived quickly",
        "The arrival destination is not stated in this clause; approval is recorded in the following segment.",
        relation=False, mentioned=["cand-1637"],
        extra={
            "continuation_status": "closed",
            "continuation_to_segment_id": "chp-8:08_CHP-8_sec_ii:l112-124",
            "continuation_to_source_line": 113,
            "continuation_fragment": "and met with approval",
            "continued_to_segment_id": "chp-8:08_CHP-8_sec_ii:l112-124",
            "continued_to_source_line": 113,
            "continued_to_statement_id": "st-chp8-p221-melanconici-commission",
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
        "printed_page": 220, "pdf_physical_page": 22, "claim": item["claim"],
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
    mention_fields, mention_rows, mention_bom = read_csv(MENTIONS)
    by_id = {r["statement_id"]: r for r in statement_rows}
    target_ids = set(OLD_NOTES) | {
        "st-chp8-p220-cignani-letter-perspective-objection",
        "st-chp8-p220-david-competitive-scheme",
        "st-chp8-p220-david-guild-review",
    }
    unset = {r["statement_id"] for r in statement_rows
             if r.get("segment_id") == SEGMENT_ID and "relation_candidate" not in r.get("qualifiers", {})}
    if unset != target_ids:
        raise SystemExit(f"unexpected p.220 unset statements: {sorted(unset)}")
    if not target_ids <= by_id.keys():
        raise SystemExit("expected p.220 source statements changed")
    new_ids = {x["statement_id"] for x in NEW_ROWS}
    if len(new_ids) != len(NEW_ROWS) or new_ids & by_id.keys():
        raise SystemExit("new statement IDs collide")
    linked_new_ids = set().union(*[set(x) for x in LINKS.values()])
    if linked_new_ids != new_ids:
        raise SystemExit("new statement link coverage differs")

    candidate_by_id = {r["candidate_id"]: r for r in candidate_rows}
    max_candidate = max(int(r["candidate_id"].split("-")[1]) for r in candidate_rows)
    if max_candidate != 12061:
        raise SystemExit(f"candidate sequence changed: max={max_candidate}")
    expected_candidates = {
        "cand-0749": ("place", "Cignani, Carlo"),
        "cand-0751": ("work", "Cignani, Carlo"),
        "cand-0911": ("place", "David, Ludovico"),
        "cand-1637": ("work", "Melanconici, Niccolò"),
    }
    for cid, state in expected_candidates.items():
        r = candidate_by_id.get(cid)
        if not r or (r.get("suggested_type"), r.get("canonical_name")) != state:
            raise SystemExit(f"candidate state changed: {cid}")
    if candidate_by_id["cand-0751"].get("sub_entry") != "cupola of Forli Cathedral":
        raise SystemExit("cand-0751 cupola subentry changed")
    if candidate_by_id["cand-1637"].get("sub_entry") != "Abraham":
        raise SystemExit("cand-1637 Abraham subentry changed")

    candidate_specs = [
        ("cand-12062", "Unnamed colleague and friend who told Ludovico David about the fourteen pictures",
         "person", 106, "One unnamed person identified by David as a colleague and friend; the source supplies no name or further biographical detail."),
        ("cand-12063", "Painters across Italy in the committee's proposed self-funded three-picture scheme",
         "", 106, "A generic artist group addressed by the committee's proposal; membership, number, and implementation are not supplied."),
        ("cand-12064", "Unnamed other artists in Ludovico David's proposed shared commission offer",
         "", 106, "The offer leaves the other artists and agreed fee unspecified; keep distinct from the later two-painter proposal."),
        ("cand-12065", "Two unnamed painters in Ludovico David's proposed competitive scheme",
         "", 106, "David's proposed group consists of himself and two other painters; neither other painter is identified and the scheme is not reported as implemented."),
        ("cand-12066", "Unidentified potential rival who prompted Franceschini to lower his terms",
         "person", 109, "Haskell reports only that Franceschini heard of a potential rival; the passage does not identify the painter."),
    ]
    existing_candidate_ids = set(candidate_by_id)
    existing_names = {r.get("canonical_name", "").casefold() for r in candidate_rows}
    for cid, name, _typ, _line, _detail in candidate_specs:
        if cid in existing_candidate_ids or name.casefold() in existing_names:
            raise SystemExit(f"candidate natural key or ID already exists: {cid}")

    segment_text = "\n".join(SOURCE.read_text(encoding="utf-8-sig").splitlines()[99:110])
    mention_specs = [
        ("m-chp8-p220-colleague-friend", "cand-12062", "a colleague and friend of mine",
         "One unnamed source identified by David; not an identity match to his proposed co-painters."),
        ("m-chp8-p220-italian-painters", "cand-12063", "painters all over Italy",
         "Generic group addressed by the committee's proposed self-funded scheme."),
        ("m-chp8-p220-other-artists-share", "cand-12064", "other artists",
         "Unnamed artists in David's alternative shared-price offer; not assumed to be the later two painters."),
        ("m-chp8-p220-two-painters", "cand-12065", "any two other painters",
         "Two unnamed co-painters in David's proposed one-year scheme."),
        ("m-chp8-p220-potential-rival", "cand-12066", "a potential rival",
         "Unidentified painter whose prospect prompted Franceschini to lower his terms."),
        ("m-chp8-p220-cignani-master", "cand-0749", "his master’s",
         "Possessive in 'his master's' resolves to Cignani, named immediately before Franceschini is identified as his Bolognese pupil."),
    ]
    existing_mention_ids = {r["mention_id"] for r in mention_rows}
    new_mentions = []
    for mid, cid, surface, note in mention_specs:
        if mid in existing_mention_ids:
            raise SystemExit(f"mention ID exists: {mid}")
        if segment_text.count(surface) != 1:
            raise SystemExit(f"mention surface is absent or ambiguous: {mid}")
        start = segment_text.index(surface)
        new_mentions.append({"mention_id": mid, "segment_id": SEGMENT_ID, "candidate_id": cid,
                             "surface_form": surface, "start_char": str(start),
                             "end_char": str(start + len(surface)), "note": note})
    correggio_mention = next((r for r in mention_rows if r["mention_id"] == "m-chp8-p220-correggio"), None)
    if not correggio_mention or (correggio_mention.get("candidate_id"), correggio_mention.get("surface_form")) != ("cand-0852", "Correggio"):
        raise SystemExit("Correggio mention state changed")
    if "cand-11591" not in candidate_by_id:
        raise SystemExit("existing Correggio Parma dome-work candidate is missing")

    for old_id, note in OLD_NOTES.items():
        q = by_id[old_id]["qualifiers"]
        q["relation_candidate"] = False
        q["relation_candidate_note"] = note
        q["linked_statement_ids"] = LINKS[old_id]

    # Correct candidate types and labels where the index subentry is a person or a distinct work.
    candidate_by_id["cand-0749"]["suggested_type"] = "person"
    candidate_by_id["cand-0751"]["canonical_name"] = "Cupola painting of Forlì Cathedral by Carlo Cignani"
    candidate_by_id["cand-0751"]["detail"] = (
        "Index subentry and Haskell's p.220 account identify the cupola painting at Forlì Cathedral; keep this work distinct from the cathedral and the city."
    )
    candidate_by_id["cand-0911"]["suggested_type"] = "person"
    candidate_by_id["cand-1637"]["canonical_name"] = "Abraham (painting by Niccolò Melanconici)"
    candidate_by_id["cand-1637"]["detail"] = (
        "Haskell reports that Melanconici agreed to paint an Abraham at his own expense as an experiment. The source supplies no fuller title; the painting's arrival and reception continue on p.221."
    )

    # Re-map the possessive work reference without merging it with a separate Correggio person mention.
    correggio_mention["candidate_id"] = "cand-11591"
    correggio_mention["note"] = (
        "Possessive painter-name denotes Correggio's work at Parma in this cupola comparison; mapped to the existing unnamed Parma dome-work candidate. Exact identity remains for S3."
    )
    by_id["st-chp8-p220-cignani-forli-cupola"]["qualifiers"]["mentioned_candidate_ids"] = [
        "cand-0749", "cand-0751", "cand-7692", "cand-11591", "cand-3417", "cand-1027", "cand-7685"
    ]

    # The two coherent proposals remain relation candidates, with proposal modality explicit.
    david_scheme = by_id["st-chp8-p220-david-competitive-scheme"]
    david_scheme["qualifiers"]["relation_candidate"] = True
    david_scheme["qualifiers"]["relation_candidate_note"] = (
        "This is David's proposed selection and exhibition scheme, not a realized commission; the two unnamed painters are separately mapped as a source-bounded group."
    )
    david_scheme["qualifiers"]["mentioned_candidate_ids"] = list(dict.fromkeys(
        david_scheme["qualifiers"].get("mentioned_candidate_ids", []) + ["cand-12065"]
    ))
    david_guild = by_id["st-chp8-p220-david-guild-review"]
    david_guild["object_candidate_id"] = "cand-7693"
    david_guild["predicate"] = "proposed_canvas_review_by_painters_guilds"
    david_guild["qualifiers"]["relation_candidate"] = True
    david_guild["qualifiers"]["relation_candidate_note"] = (
        "David proposed that canvases be sent to the three local painters' guilds for review; no review or award is reported as having occurred."
    )

    cignani_letter = by_id["st-chp8-p220-cignani-letter-perspective-objection"]["qualifiers"]
    cignani_letter["relation_candidate"] = True
    cignani_letter["relation_candidate_note"] = (
        "Cignani's August 1692 letter directly addresses whether he could undertake the central-nave picture work; the cited letter is not independently consulted."
    )

    # The footnote cites the letter account and the terms/proposals reported from it.
    citation = by_id["st-chp8-p220-n1-bottari-citation"]["qualifiers"]
    citation["linked_body_statement_ids"] = [
        "st-chp8-p220-david-hears-about-project-from-colleague",
        "st-chp8-p220-david-offers-all-pictures",
        "st-chp8-p220-david-offers-share-with-artists",
        "st-chp8-p220-david-reports-payment-practice",
        "st-chp8-p220-david-rejects-committee-terms",
        "st-chp8-p220-david-competitive-scheme",
        "st-chp8-p220-david-guild-review",
    ]

    # Re-home the p.220 -> p.221 clause continuation from the now-composite row to the arrival atom.
    old_melanconici_q = by_id["st-chp8-p220-melanconici-abraham-open"]["qualifiers"]
    for key in ("continuation_to_segment_id", "continuation_to_source_line", "continuation_fragment",
                "continuation_status", "continued_to_segment_id", "continued_to_source_line",
                "continued_to_statement_id"):
        old_melanconici_q.pop(key, None)
    p221_q = by_id["st-chp8-p221-melanconici-commission"]["qualifiers"]
    if p221_q.get("continued_from_statement_id") != "st-chp8-p220-melanconici-abraham-open":
        raise SystemExit("p.221 continuation source changed")
    p221_q["continued_from_statement_id"] = "st-chp8-p220-abraham-picture-arrives-quickly"

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

    statement_bytes = ("\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":"))
                                  for r in statement_rows) + "\n").encode("utf-8")
    candidate_bytes = csv_bytes(candidate_fields, candidate_rows, candidate_bom)
    mention_bytes = csv_bytes(mention_fields, mention_rows, mention_bom)
    page_rows = [r for r in statement_rows if r.get("segment_id") == SEGMENT_ID]
    summary = {
        "existing_rows_classified_or_refined": len(target_ids),
        "new_statements": len(NEW_ROWS),
        "new_true": sum(x["relation"] for x in NEW_ROWS),
        "new_false": sum(not x["relation"] for x in NEW_ROWS),
        "new_source_candidates": len(candidate_specs),
        "new_mentions": len(new_mentions),
        "retyped_or_renamed_candidates": 4,
        "corrected_existing_mention_mapping": 1,
        "p220_final_statements": len(page_rows),
        "p220_final_true": sum(r["qualifiers"].get("relation_candidate") is True for r in page_rows),
        "p220_final_false": sum(r["qualifiers"].get("relation_candidate") is False for r in page_rows),
        "p220_final_unset": sum("relation_candidate" not in r.get("qualifiers", {}) for r in page_rows),
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
