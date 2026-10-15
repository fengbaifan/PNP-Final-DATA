"""Guarded S2 semantic review for printed p.227, body lines 190-204."""
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
SEGMENTS = TABLES / "segments.jsonl"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE = ROOT / SOURCE_REL
PAGE_IMAGE = ROOT / "scripts" / ".tmp_s2_chp8_p227_review.png"
SEGMENT = "chp-8:08_CHP-8_sec_ii:l190-204"
P226_SEGMENT = "chp-8:08_CHP-8_sec_ii:l179-188"
BACKUP_SUFFIX = ".bak-s2-chp8-p227-l190-204-semantic-review-20261014"
EXPECTED = {
    STATEMENTS: "a3288f1ddabea53ec52e226cad7dea2a670be1afed73708a17809b4d1fd57563",
    CANDIDATES: "3318d991e641e67733e56ab1be0282136c11bde71547f5bfccca5dfb6f255ed8",
    MENTIONS: "2229d2ce28ff1d7c4046f083f7ab9cee64375793ecc7503563b542a299596b49",
    SOURCE: "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    PAGE_IMAGE: "45395f53790aa4dd041110a55d7207f7459a9ffb8b8d252670b2e92ec9ab07c3",
}

CLASSIFICATIONS = {
    "st-chp8-p227-gallery-academic-style": (True, "This row is narrowed to the explicitly named group of painters Conti selected; Haskell's stylistic judgments are separated below."),
    "st-chp8-p227-pricing-problems": (True, "This closes the p.226 per-figure payment statement and attributes the reported practical problem to Franceschini's response."),
    "st-chp8-p227-venetian-subjects": (False, "This is Haskell's broad and evaluative characterization of Venetian subject choices, not a formal relation."),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def jsonl_bytes(rows):
    return ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")


def csv_bytes(path: Path, rows):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        fields = next(csv.reader(stream))
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def atomic_write(path: Path, data: bytes):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(data)
    temporary.replace(path)


def check_inputs():
    for path, expected in EXPECTED.items():
        actual = sha(path.read_bytes())
        if actual != expected:
            raise SystemExit(f"input changed: {path.relative_to(ROOT)} sha256={actual}")
    segment_meta = {row["segment_id"]: row for row in read_jsonl(SEGMENTS)}.get(SEGMENT)
    if not segment_meta or segment_meta["line_start"] != 190 or segment_meta["line_end"] != 204:
        raise SystemExit("unexpected p227 S0 segment metadata")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[segment_meta["line_start"] - 1:segment_meta["line_end"]])
    if sha(segment_text.encode("utf-8")) != segment_meta["sha256"]:
        raise SystemExit("p227 source segment content hash mismatch")
    checks = [
        (191, "And the suggestion was accepted"),
        (192, "Conti was equally ready to accept a picture of this kind"),
        (193, "painted six subjects from the Old and New Testaments"),
        (195, "The artists he had chosen"),
        (197, "Sebastiano Bombelli"),
        (198, "seven pictures of fruit and animals"),
        (203, "he began to resume collecting"),
        (204, "the artistic situation in Venice had been completely transformed"),
    ]
    for line_no, text in checks:
        if text not in source_lines[line_no - 1]:
            raise SystemExit(f"source excerpt mismatch at L{line_no}: {text}")
    return segment_text


def new_statement(statement_id, subject, object_, predicate, lines, claim, quote, *,
                  relation, note, mentioned, extra=None):
    q = {
        "source_line_start": lines[0], "source_line_end": lines[1],
        "printed_page": 227, "pdf_physical_page": 29, "claim": claim,
        "speaker": "Haskell", "text_layer": "body", "qualification": note,
        "mentioned_candidate_ids": mentioned, "relation_candidate": relation,
        "relation_candidate_note": note,
    }
    if extra:
        q.update(extra)
    return {"statement_id": statement_id, "segment_id": SEGMENT,
            "subject_candidate_id": subject, "object_candidate_id": object_,
            "predicate": predicate, "qualifiers": q, "original_quote": quote,
            "origin": "book", "source_file": SOURCE_REL}


def plan():
    segment_text = check_inputs()
    statements = read_jsonl(STATEMENTS)
    _, candidates = read_csv(CANDIDATES)
    _, mentions = read_csv(MENTIONS)
    by_id = {row["statement_id"]: row for row in statements}
    target = [row for row in statements if row.get("segment_id") == SEGMENT]
    unset = {row["statement_id"] for row in target
             if "relation_candidate" not in row.get("qualifiers", {})}
    if len(target) != 10 or unset != set(CLASSIFICATIONS):
        raise SystemExit(f"unexpected p227 state: rows={len(target)}, unset={sorted(unset)}")
    if P226_SEGMENT not in {row.get("segment_id") for row in statements}:
        raise SystemExit("missing p226 parent segment")

    candidate_ids = {row["candidate_id"] for row in candidates}
    mention_ids = {row["mention_id"] for row in mentions}
    new_candidate_ids = {"cand-12089", "cand-12090"}
    new_mention_ids = {"m-chp8-p227-selected-painters-group", "m-chp8-p227-three-purchases-group"}
    new_statement_ids = [
        "st-chp8-p227-franceschini-writes-to-conti",
        "st-chp8-p227-franceschini-asks-conti-to-choose",
        "st-chp8-p227-franceschini-pastoral-accepted",
        "st-chp8-p227-torelli-scene-accepted",
        "st-chp8-p227-conti-asks-what-arrived-picture-represented",
        "st-chp8-p227-venetian-six-lazzarini-pictures",
        "st-chp8-p227-lazzarini-morality-judgment",
        "st-chp8-p227-gallery-academic-appearance-judgment",
        "st-chp8-p227-selected-artists-style-judgment",
        "st-chp8-p227-franchi-suitability-judgment",
        "st-chp8-p227-commissioned-landscapes",
        "st-chp8-p227-commissioned-carlevarijs-views",
        "st-chp8-p227-gallery-completed-by-busts",
        "st-chp8-p227-mazza-created-busts",
        "st-chp8-p227-advice-from-marchesini-1725",
        "st-chp8-p227-attempted-extra-carlevarijs-views",
        "st-chp8-p227-attempted-bassi-landscape",
        "st-chp8-p227-spare-room-inference",
        "st-chp8-p227-conti-bought-correggio-christ",
        "st-chp8-p227-conti-bought-guercino-flight",
        "st-chp8-p227-conti-bought-brugiori-cain-abel",
        "st-chp8-p227-venetian-scene-transformed-judgment",
    ]
    if candidate_ids.intersection(new_candidate_ids) or mention_ids.intersection(new_mention_ids) or set(new_statement_ids).intersection(by_id):
        raise SystemExit("one or more planned p227 IDs already exist")

    for sid, (relation, note) in CLASSIFICATIONS.items():
        by_id[sid]["qualifiers"]["relation_candidate"] = relation
        by_id[sid]["qualifiers"]["relation_candidate_note"] = note

    def revise(sid, *, predicate, subject, object_, claim, quote, relation, note,
               lines=None, mentioned=None, extra=None):
        row = by_id[sid]
        q = row["qualifiers"]
        row["predicate"] = predicate
        row["subject_candidate_id"] = subject
        row["object_candidate_id"] = object_
        row["original_quote"] = quote
        q["claim"] = claim
        q["relation_candidate"] = relation
        q["relation_candidate_note"] = note
        q["qualification"] = note
        if lines:
            q["source_line_start"], q["source_line_end"] = lines
        if mentioned is not None:
            q["mentioned_candidate_ids"] = mentioned
        if extra:
            q.update(extra)

    # Keep one evidence-backed assertion in each existing composite row.
    revise("st-chp8-p227-carlevarijs-transformed-scene-open",
        predicate="marchesini_begins_to_testify_about_carlevarijs", subject="cand-1540", object_="cand-0554",
        claim="Haskell introduces a statement by Marchesini about Carlevarijs that continues onto p.228.",
        quote="Carlevarijs, wrote Marchesini, was", relation=True,
        note="This is the opening of Marchesini's reported testimony about Carlevarijs; its content continues on p.228.",
        mentioned=["cand-0554", "cand-1540"], lines=(204, 204))
    revise("st-chp8-p227-franceschini-proposes-pastoral",
        predicate="proposed_sacred_profane_and_fanciful_pastoral_subjects", subject="cand-1069", object_="cand-7797",
        claim="Franceschini proposed sacred and profane subjects, including a fanciful pastoral with a shepherd, a nymph and two or three putti.",
        quote="However, he went on to propose various subjects—sacred and profane at random: Adam and Eve, Bacchus and Ariadne and so on, ending up that ‘what I would really like to do would be a fanciful pastoral with a shepherd, a nymph and two or three putti in atto bizzarre e curio so",
        relation=True, note="The pastoral proposal is recorded as a proposed subject; acceptance is recorded separately and does not prove the painting was completed.",
        mentioned=["cand-1069", "cand-7797", "cand-0833", "cand-7812", "cand-7813", "cand-7814", "cand-7815"], lines=(191, 191),
        extra={"ocr_corrections": [{"source_file": SOURCE_REL, "source_line": 191, "ocr": "curio so .", "print": "curioso.", "basis": "CHP-8.pdf physical page 29."}]})
    revise("st-chp8-p227-gallery-academic-style",
        predicate="conti_selected_named_painters_for_gallery", subject="cand-0833", object_="cand-12089",
        claim="Haskell names the painters Conti selected for the gallery: Marchesini, Lazzarini, Balestra, Fumiani, Bellucci, Angiolo Trevisani, Segala, Dal Sole and Franceschini.",
        quote="The artists he had chosen—Marchesini himself, Lazzarini, Balestra, Fumiani, Bellucci, Angiolo Trevisani, Segala, Dal Sole and Franceschini—",
        relation=True, note="The source explicitly identifies this selected group; the artists' generation and stylistic characterization are separated below.",
        mentioned=["cand-0833", "cand-7785", "cand-12089", "cand-1540", "cand-1368", "cand-0168", "cand-1087", "cand-0282", "cand-7808", "cand-2417", "cand-2480", "cand-1069"], lines=(195, 196))
    by_id["st-chp8-p227-gallery-academic-style"]["qualifiers"].pop("ocr_corrections", None)
    revise("st-chp8-p227-conti-portraits",
        predicate="commissioned_family_portraits_from_bombelli", subject="cand-0833", object_="cand-7800",
        claim="Conti had portraits of his wife, son and himself painted by Sebastiano Bombelli.",
        quote="He had the portraits of his wife, his son and himself painted by Sebastiano Bombelli",
        relation=True, note="The source reports these three portraits as painted by Bombelli; Franchi's possible suitability for the daughters' portraits is separated below.",
        mentioned=["cand-0833", "cand-7800", "cand-0383", "cand-7792", "cand-7793"], lines=(197, 197))
    revise("st-chp8-p227-gallery-other-works",
        predicate="commissioned_seven_fruit_and_animal_pictures_from_cassana", subject="cand-0833", object_="cand-7804",
        claim="Conti commissioned seven pictures of fruit and animals from Giovanni Agostino Cassana.",
        quote="he also commissioned seven pictures of fruit and animals from Giovanni Agostino Cassana",
        relation=True, note="The number and subject group are reported by Haskell; individual titles are not given.",
        mentioned=["cand-0833", "cand-0592", "cand-7804"], lines=(198, 199))
    revise("st-chp8-p227-pricing-problems",
        predicate="per_figure_payment_practice_caused_reported_problems", subject="cand-0833", object_="cand-7787",
        claim="Haskell says Conti's per-figure payment practice sometimes caused problems, illustrated by Franceschini's difficulty in finding a suitable subject.",
        quote="and this sometimes led to problems.", relation=True,
        note="This closes the p.226 open statement; Franceschini's letter is presented as Haskell's report, and the quoted difficulty is not an independently checked contract rule.",
        mentioned=["cand-0833", "cand-7787"], lines=(191, 191),
        extra={"continued_from_segment_id": P226_SEGMENT, "continued_from_statement_id": "st-chp8-p226-conti-per-figure-payment-open", "continuation_status": "closed"})
    revise("st-chp8-p227-resumed-collecting-1725",
        predicate="resumed_collecting_in_1725", subject="cand-0833", object_="cand-7784",
        claim="Haskell says Conti resumed collecting in 1725.",
        quote="he began to resume collecting.", relation=True,
        note="The resumption is separated from Conti's advice-seeking and intended acquisitions; the date is retained as printed.",
        mentioned=["cand-0833", "cand-7784"], lines=(203, 203),
        extra={"date": "1725", "ocr_corrections": [{"source_file": SOURCE_REL, "source_line": 203, "ocr": "- 1725", "print": "1725", "basis": "CHP-8.pdf physical page 29."}]})
    revise("st-chp8-p227-three-purchases",
        predicate="bought_only_three_pictures_in_nearly_twenty_years", subject="cand-0833", object_="cand-12090",
        claim="For nearly twenty years, Conti bought only three pictures.",
        quote="With all this Stefano Conti was satisfied for nearly twenty years, during which he bought only three pictures",
        relation=True, note="The three-work group is separate from the individual works listed below; titles and reported attributions are preserved.",
        mentioned=["cand-0833", "cand-12090"], lines=(201, 202),
        extra={"duration_years": "nearly 20"})
    revise("st-chp8-p227-torelli-proposed-scene",
        predicate="proposed_painting_of_pyrrhus_killing_polyxena", subject="cand-2645", object_="cand-7798",
        claim="Felice Torelli proposed a Trojan-history painting of Pyrrhus killing Polyxena, with additional named figures and the tomb of Achilles.",
        quote="Felice Torelli wanted to paint a scene from Trojan history2—‘Pyrrhus killing Polyxena in the temple and there will be Chalchas, the soothsayer, and other half-length figures or heads depicting Aeneas and Antinorus-—in fact everything that is needed for the history, and also the tomb of Acliilles, the father of Pyrrhus.’",
        relation=True, note="This records Torelli's proposed composition; Conti's acceptance and the later question about the delivered picture are separate.",
        mentioned=["cand-2645", "cand-7798", "cand-7816", "cand-7817", "cand-7818", "cand-4164", "cand-7820", "cand-7821"], lines=(192, 192),
        extra={"ocr_corrections": [{"source_file": SOURCE_REL, "source_line": 192, "ocr": "Acliilles", "print": "Achilles", "basis": "CHP-8.pdf physical page 29."}]})
    revise("st-chp8-p227-venetian-subjects",
        predicate="haskell_generalizes_about_venetian_subject_choices", subject="cand-1368", object_=None,
        claim="Haskell characterizes Venetian artists as generally less imaginative in subject choice, relying on stock biblical and mythological scenes, and notes a preponderance of religious paintings.",
        quote="The Venetian artists were on the whole less imaginative in their choice of subject— stock scenes from the Bible and mythology were their usual standby; there is a definite preponderance of religious painting",
        relation=False, note="This is Haskell's generalization about regional artistic practice; Lazzarini's six paintings and the moral assessment are separated below.",
        mentioned=["cand-1368", "cand-3401"], lines=(193, 193), extra={"speaker_judgment": True})
    by_id["st-chp8-p227-venetian-subjects"]["qualifiers"].pop("ocr_corrections", None)

    # Close the p.226 payment continuation in both directions.
    parent = by_id["st-chp8-p226-conti-per-figure-payment-open"]
    parent["qualifiers"].update({
        "continuation_status": "closed",
        "continued_to_segment_id": SEGMENT,
        "continued_to_source_line": 191,
        "continuation_closed_by_statement_id": "st-chp8-p227-pricing-problems",
    })

    # Candidate labels from the index used the indexed subject (artist) as the displayed work name.
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    candidate_by_id["cand-0853"].update({
        "canonical_name": "Christ in the Garden of Olives (reported as a ‘Correggio’)",
        "detail": "Haskell reports that Conti bought this painting, retaining the attribution in quotation marks; the attribution is not independently verified.",
    })
    candidate_by_id["cand-1264"].update({
        "canonical_name": "Flight into Egypt (painting attributed to Guercino)",
        "detail": "Work named in Haskell's account of Conti's three purchases; the work is distinct from the artist candidate cand-1258.",
    })
    candidate_by_id["cand-0457"].update({
        "canonical_name": "Cain and Abel (painting by Domenico Brugiori)",
        "detail": "Work named in Haskell's account of Conti's three purchases; the artist is separately represented by cand-0456.",
    })

    candidates.extend([
        {"candidate_id": "cand-12089", "index_entry_id": "", "canonical_name": "Painters selected by Stefano Conti for his gallery (unnamed group)", "index_page_range": "", "suggested_type": "", "status": "open", "index_source_file": "", "sub_entry": "", "detail": "Haskell names Marchesini, Lazzarini, Balestra, Fumiani, Bellucci, Angiolo Trevisani, Segala, Dal Sole and Franceschini as the artists Conti had chosen; group membership is represented without replacing the individual candidates.", "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT}#L195"},
        {"candidate_id": "cand-12090", "index_entry_id": "", "canonical_name": "Three pictures bought by Stefano Conti over nearly twenty years (work group)", "index_page_range": "", "suggested_type": "work", "status": "open", "index_source_file": "", "sub_entry": "", "detail": "Haskell says Conti bought only three pictures during this period: the Christ in the Garden of Olives attributed to Correggio, Guercino's Flight into Egypt, and Brugiori's Cain and Abel.", "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT}#L201"},
    ])

    additions = [
        new_statement("st-chp8-p227-franceschini-writes-to-conti", "cand-1069", "cand-0833",
            "wrote_to_conti_from_bologna_about_commission", (191, 191),
            "Franceschini wrote to Conti from Bologna about the difficulty of choosing a subject under the payment practice.",
            "‘It is a little difficult’, wrote Marcantonio Franceschini from Bologna,1 ‘to find a history or fable with two figures and putti",
            relation=True, note="The source explicitly attributes the letter to Franceschini and identifies Conti as the gentleman addressed; the cited letter itself remains to be reviewed in the notes segment.",
            mentioned=["cand-1069", "cand-0833", "cand-3398"]),
        new_statement("st-chp8-p227-franceschini-asks-conti-to-choose", "cand-1069", "cand-0833",
            "asked_patron_to_choose_subject", (191, 191),
            "Franceschini said he would like Conti himself to choose the subject.",
            "I would like the gentleman himself to choose what he wants",
            relation=True, note="The 'gentleman' is resolved to Conti by the adjacent context; this records Franceschini's request, not a completed choice.",
            mentioned=["cand-1069", "cand-0833"]),
        new_statement("st-chp8-p227-franceschini-pastoral-accepted", "cand-0833", "cand-7797",
            "accepted_franceschinis_pastoral_proposal", (191, 191),
            "Conti accepted Franceschini's fanciful pastoral subject proposal.", "And the suggestion was accepted.",
            relation=True, note="Acceptance concerns the subject proposal only; the source does not say the painting was completed.",
            mentioned=["cand-0833", "cand-1069", "cand-7797"]),
        new_statement("st-chp8-p227-torelli-scene-accepted", "cand-0833", "cand-7798",
            "accepted_torellis_proposed_picture_type", (192, 192),
            "Conti was ready to accept a picture of the kind Torelli proposed.",
            "Conti was equally ready to accept a picture of this kind",
            relation=True, note="The source reports acceptance of a picture of this kind; it does not establish that the delivered work was identical to the proposed composition.",
            mentioned=["cand-0833", "cand-2645", "cand-7798"]),
        new_statement("st-chp8-p227-conti-asks-what-arrived-picture-represented", "cand-0833", "cand-7798",
            "asked_what_arrived_picture_represented", (192, 192),
            "After a picture of this kind eventually arrived, Conti wrote to ask what it represented.",
            "but when it eventually arrived he wrote to ask once more what exactly it represented",
            relation=True, note="Haskell reports the later question but leaves the delivered picture's exact identity uncertain.",
            mentioned=["cand-0833", "cand-7798"]),
        new_statement("st-chp8-p227-venetian-six-lazzarini-pictures", "cand-1368", "cand-7799",
            "painted_six_old_and_new_testament_subjects", (193, 193),
            "Haskell says Lazzarini painted six subjects from the Old and New Testaments.",
            "painted six subjects from the Old and New Testaments",
            relation=True, note="The six-picture group is identified by subject category only; Haskell's moral judgment is separated.",
            mentioned=["cand-1368", "cand-7799"]),
        new_statement("st-chp8-p227-lazzarini-morality-judgment", "cand-1368", None,
            "haskell_notes_lazzarini_reception_and_judges_religious_subjects", (193, 193),
            "Haskell notes that Lazzarini was admired for his nudes and describes his Old and New Testament subjects as having impeccable morality.",
            "evenLazzarini, who was so much admired for his nudes, painted six subjects from the Old and New Testaments of impeccable morality",
            relation=False, note="This is Haskell's evaluative characterization of the subjects, not an independent property of the works.",
            mentioned=["cand-1368", "cand-7799"], extra={"speaker_judgment": True, "ocr_corrections": [{"source_file": SOURCE_REL, "source_line": 193, "ocr": "evenLazzarini", "print": "even Lazzarini", "basis": "CHP-8.pdf physical page 29."}]}),
        new_statement("st-chp8-p227-gallery-academic-appearance-judgment", "cand-7785", None,
            "haskell_infers_gallery_had_academic_appearance", (194, 195),
            "Haskell infers that the gallery completed around 1707 must have presented a notably academic appearance.",
            "Conti’s gallery, when completed by about 1707, must have presented a notably\n’ ‘academic’ appearance",
            relation=False, note="Both the completion date and 'academic' appearance are presented as Haskell's inference and characterization.",
            mentioned=["cand-7785"], extra={"speaker_judgment": True, "approximate_date": "c.1707", "ocr_corrections": [{"source_file": SOURCE_REL, "source_line": 195, "ocr": "’ ‘academic’", "print": "‘academic’", "basis": "CHP-8.pdf physical page 29."}]}),
        new_statement("st-chp8-p227-selected-artists-style-judgment", "cand-12089", None,
            "haskell_characterizes_selected_artists_generation_and_style", (195, 196),
            "Haskell says the selected artists were Conti's generation and mostly followed correct drawing and blond tonality, in opposition to the successful Venetian tenebrosi.",
            "were all of his own generation and mostly adhered to ‘correct’ drawing and blond tonality in opposition to the violent tenebrosi who had enjoyed such a success in Venice",
            relation=False, note="This is Haskell's stylistic and generational characterization of the group.",
            mentioned=["cand-12089", "cand-0833", "cand-7809", "cand-3401"], extra={"speaker_judgment": True}),
        new_statement("st-chp8-p227-franchi-suitability-judgment", "cand-1074", None,
            "haskell_says_franchi_was_considered_suitable_for_daughters_portraits", (197, 197),
            "Haskell says local artist Antonio Franchi was considered good enough to paint portraits of Conti's three daughters.",
            "a local artist, Antonio Franchi, was considered good enough for his three daughters",
            relation=False, note="This is a reported suitability judgment, not an assertion that Franchi received or completed a commission.",
            mentioned=["cand-1074", "cand-7810", "cand-0833"], extra={"speaker_judgment": True}),
        new_statement("st-chp8-p227-commissioned-landscapes", "cand-0833", "cand-7805",
            "commissioned_unnamed_landscapes", (198, 199),
            "Conti commissioned a number of landscapes by unnamed artists.", "a number of landscapes by other artists",
            relation=True, note="Haskell's sentence places the landscapes in the list of works Conti commissioned; the landscape makers and titles remain unspecified.",
            mentioned=["cand-0833", "cand-7805"]),
        new_statement("st-chp8-p227-commissioned-carlevarijs-views", "cand-0833", "cand-7806",
            "commissioned_three_venice_views_from_carlevarijs", (199, 200),
            "Conti commissioned three views of Venice by Luca Carlevarijs.", "three views of Venice by Luca\nCarlevarijs",
            relation=True, note="The artist's name spans the source line break; titles of the three views are not given.",
            mentioned=["cand-0833", "cand-7806", "cand-0554"]),
        new_statement("st-chp8-p227-gallery-completed-by-busts", "cand-7785", "cand-7807",
            "gallery_completed_by_bust_pair", (200, 200),
            "A pair of busts of Diana and Endymion completed Conti's gallery.",
            "Busts of Diana and Endymion by the Bolognese Giuseppe Mazza completed the gallery",
            relation=True, note="The source says the pair completed the gallery; the individual busts are not separately identified.",
            mentioned=["cand-7785", "cand-7807", "cand-4136", "cand-7811", "cand-1602"]),
        new_statement("st-chp8-p227-mazza-created-busts", "cand-7807", "cand-1602",
            "created_by_giuseppe_mazza", (200, 200),
            "Haskell attributes the bust pair to Giuseppe Mazza of Bologna.",
            "by the Bolognese Giuseppe Mazza",
            relation=True, note="The creator attribution is explicit in Haskell's account.", mentioned=["cand-7807", "cand-1602"]),
        new_statement("st-chp8-p227-advice-from-marchesini-1725", "cand-0833", "cand-1540",
            "sought_marchesinis_advice_in_1725", (203, 203),
            "In 1725 Conti turned to Marchesini again for advice.", "To Alessandro Marchesini’s great delight, Conti turned once more to him for advice",
            relation=True, note="The source directly reports Conti seeking advice; Marchesini's delight is attributed by Haskell.",
            mentioned=["cand-0833", "cand-1540"], extra={"date": "1725", "reported_emotion": "Marchesini's great delight"}),
        new_statement("st-chp8-p227-attempted-extra-carlevarijs-views", "cand-0833", "cand-7823",
            "tried_to_obtain_two_additional_carlevarijs_views", (203, 203),
            "Conti was trying to obtain two further views by Carlevarijs to add to the three views he already owned.",
            "Conti was trying to get two further views by Carlevarijs to add to the three that he already owned",
            relation=True, note="The acquisition was only being attempted; the two views are distinct from the three already owned.",
            mentioned=["cand-0833", "cand-7823", "cand-0554", "cand-7806"], extra={"date": "1725", "modality": "trying to obtain"}),
        new_statement("st-chp8-p227-attempted-bassi-landscape", "cand-0833", "cand-7822",
            "tried_to_obtain_bassi_landscape_for_set_of_four", (203, 204),
            "Conti was trying to obtain one landscape by Francesco Bassi to make a complete set of four.",
            "and one landscape by Francesco Bassi, il\nCremonese, to make a complete set of four",
            relation=True, note="This is an intended acquisition, not proof of ownership or completion; 'il Cremonese' remains an alias of Bassi.",
            mentioned=["cand-0833", "cand-7822", "cand-0259"], extra={"date": "1725", "modality": "trying to obtain"}),
        new_statement("st-chp8-p227-spare-room-inference", "cand-0833", None,
            "haskell_infers_spare_room_from_intended_acquisitions", (203, 203),
            "Haskell infers that Conti must have found spare room because he was trying to obtain further works.",
            "Evidently some spare room had been found",
            relation=False, note="This is Haskell's inference from planned acquisitions, not a separately evidenced fact about the gallery.",
            mentioned=["cand-0833", "cand-7785"], extra={"speaker_judgment": True}),
        new_statement("st-chp8-p227-conti-bought-correggio-christ", "cand-0833", "cand-0853",
            "bought_christ_in_garden_of_olives_reported_as_correggio", (201, 201),
            "Conti bought a Christ in the Garden of Olives attributed in Haskell's text to 'Correggio'.",
            "a ‘Correggio’ Christ in the Garden of Olives",
            relation=True, note="The painter attribution is reported with quotation marks and is not independently verified.",
            mentioned=["cand-0833", "cand-0853"], extra={"attribution_status": "reported, qualified by source quotation marks"}),
        new_statement("st-chp8-p227-conti-bought-guercino-flight", "cand-0833", "cand-1264",
            "bought_flight_into_egypt_attributed_to_guercino", (201, 202),
            "Conti bought a Flight into Egypt attributed to Guercino.", "a Guercino\nFlight into Egypt",
            relation=True, note="The source names the work and its reported attribution; the artist and work remain separate candidates.",
            mentioned=["cand-0833", "cand-1258", "cand-1264"]),
        new_statement("st-chp8-p227-conti-bought-brugiori-cain-abel", "cand-0833", "cand-0457",
            "bought_cain_and_abel_by_brugiori", (202, 202),
            "Conti bought Cain and Abel by the local artist Domenico Brugiori.",
            "a Cain and Abel by the local artist Domenico Brugiori",
            relation=True, note="The work and artist are represented by distinct candidates.",
            mentioned=["cand-0833", "cand-0457", "cand-0456"]),
        new_statement("st-chp8-p227-venetian-scene-transformed-judgment", "cand-3401", None,
            "haskell_says_venetian_artistic_scene_changed_completely", (204, 204),
            "Haskell says the artistic situation in Venice had been completely transformed over the previous twenty years.",
            "But in the previous twenty years the artistic situation in Venice had been completely transformed",
            relation=False, note="This is Haskell's historical interpretation, separate from Marchesini's testimony about Carlevarijs.",
            mentioned=["cand-3401"], extra={"speaker_judgment": True, "duration_years": 20}),
    ]
    statements.extend(additions)

    for mention_id, candidate_id, surface, note in [
        ("m-chp8-p227-selected-painters-group", "cand-12089", "The artists he had chosen", "Named group of painters Conti selected for the gallery; individual candidates remain separately recorded."),
        ("m-chp8-p227-three-purchases-group", "cand-12090", "only three pictures", "Aggregate group of the three works acquired over nearly twenty years; individual titles are separately recorded."),
    ]:
        start = segment_text.find(surface)
        if start < 0 or segment_text.find(surface, start + 1) >= 0:
            raise SystemExit(f"mention text is absent or ambiguous: {surface}")
        mentions.append({"mention_id": mention_id, "segment_id": SEGMENT, "candidate_id": candidate_id,
                         "surface_form": surface, "start_char": str(start), "end_char": str(start + len(surface)), "note": note})

    target_after = [row for row in statements if row.get("segment_id") == SEGMENT]
    if any("relation_candidate" not in row.get("qualifiers", {}) for row in target_after):
        raise SystemExit("an unset relation_candidate remains in p227")
    counts = {str(value): sum(row["qualifiers"]["relation_candidate"] is value for row in target_after)
              for value in (True, False)}
    summary = {"segment_id": SEGMENT, "existing_statements": len(target), "classified_unset": len(unset),
               "new_statements": len(additions), "new_candidates": len(new_candidate_ids), "new_mentions": 2,
               "final_statements": len(target_after), "relation_candidate_true": counts["True"],
               "relation_candidate_false": counts["False"], "relation_candidate_unset": 0}
    return summary, jsonl_bytes(statements), csv_bytes(CANDIDATES, candidates), csv_bytes(MENTIONS, mentions)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after all input guards and plan checks pass")
    args = parser.parse_args()
    summary, statement_data, candidate_data, mention_data = plan()
    print(json.dumps({"mode": "apply" if args.apply else "dry-run", **summary}, ensure_ascii=False, indent=2))
    if not args.apply:
        return
    outputs = {STATEMENTS: statement_data, CANDIDATES: candidate_data, MENTIONS: mention_data}
    for path in outputs:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if not backup.exists():
            shutil.copy2(path, backup)
    for path, data in outputs.items():
        atomic_write(path, data)


if __name__ == "__main__":
    main()
