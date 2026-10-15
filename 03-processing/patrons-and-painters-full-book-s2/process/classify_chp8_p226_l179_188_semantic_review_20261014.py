"""Guarded S2 semantic review for printed p.226, body lines 179-188."""
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
PAGE_IMAGE = ROOT / "scripts" / ".tmp_s2_chp8_p226_review.png"
SEGMENT = "chp-8:08_CHP-8_sec_ii:l179-188"
BACKUP_SUFFIX = ".bak-s2-chp8-p226-l179-188-semantic-review-20261014"
EXPECTED = {
    STATEMENTS: "0371c0b91c883a1a662828d351c6140034f1ec6e617c228b396b3b34abcb6b3e",
    CANDIDATES: "3d3472fdae013a94f3f9a86e789a44bb7aec513783b11dc21d0ef1ce45fb58c2",
    MENTIONS: "17c1321cac4c87189794b6c906e66c98aa04fedadf852a372d5cfa1fe1605628",
    SOURCE: "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    PAGE_IMAGE: "b4e8ef8669cdc11451862431ca750c8e17d176b7f986ae5711461c5223391c33",
}

CLASSIFICATIONS = {
    "st-chp8-p226-conti-birth": (False, "Birth date is a biographical attribute, not a relation candidate."),
    "st-chp8-p226-conti-business-and-documents": (False, "Trade and Haskell's assessment of business acumen are descriptive claims; no distinct relation endpoint is asserted."),
    "st-chp8-p226-conti-collection-compared-to-buonaccorsi": (False, "This is Haskell's comparative art-historical framing, not a controlled relation between the two collections."),
    "st-chp8-p226-conti-collection-period": (True, "The source directly links Conti's collecting activity to his collection and reports its beginning and duration; Haskell's inference about his temperament is separated below."),
    "st-chp8-p226-conti-price-policy": (True, "This records Conti's reported payment rule within his picture-commission practice."),
    "st-chp8-p226-enlightenment-private-apartments-close": (True, "This is the qualified cross-page continuation of Haskell's tentative placement of Raimondo among the patron group; the modality remains explicit."),
    "st-chp8-p226-marchesini-profile-and-cignani-school": (True, "Marchesini's study at Cignani's school is an explicit person-to-school relation; other profile and authorial claims are separated below."),
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
    segments = {row["segment_id"]: row for row in read_jsonl(SEGMENTS)}
    meta = segments.get(SEGMENT)
    if not meta or meta["line_start"] != 179 or meta["line_end"] != 188:
        raise SystemExit("unexpected S0 segment metadata")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[meta["line_start"] - 1:meta["line_end"]])
    if sha(segment_text.encode("utf-8")) != meta["sha256"]:
        raise SystemExit("p226 source segment content hash mismatch")
    checks = [
        (181, "somewhat similar conflict in the contemporary collection of Stefano Conti"),
        (181, "He confined himself to Bologna and Venice"),
        (182, "pictures by Crespi, Sebastiano Ricci, Canaletto"),
        (183, "He married in 1685, but outlived both his wife and only son"),
        (183, "his will and other documents that he was an acute man of business"),
        (184, "each work should be an originals painted for him alone"),
        (186, "whom he appointed his agent"),
        (187, "suggesting new artists, and even proposing alterations"),
    ]
    for line_no, text in checks:
        if text not in source_lines[line_no - 1]:
            raise SystemExit(f"source excerpt mismatch at L{line_no}: {text}")
    return segment_text


def new_statement(statement_id, subject, object_, predicate, line_start, line_end,
                  claim, quote, *, relation, note, mentioned, extra=None):
    q = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 226,
        "pdf_physical_page": 28,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "body",
        "qualification": note,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation,
        "relation_candidate_note": note,
    }
    if extra:
        q.update(extra)
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": q,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_REL,
    }


def plan():
    segment_text = check_inputs()
    statements = read_jsonl(STATEMENTS)
    candidate_fields, candidates = read_csv(CANDIDATES)
    mention_fields, mentions = read_csv(MENTIONS)
    by_id = {row["statement_id"]: row for row in statements}
    target = [row for row in statements if row.get("segment_id") == SEGMENT]
    unset = {row["statement_id"] for row in target
             if "relation_candidate" not in row.get("qualifiers", {})}
    if len(target) != 18 or unset != set(CLASSIFICATIONS):
        raise SystemExit(f"unexpected p226 state: rows={len(target)}, unset={sorted(unset)}")

    candidate_ids = {row["candidate_id"] for row in candidates}
    mention_ids = {row["mention_id"] for row in mentions}
    existing_statement_ids = set(by_id)
    new_candidate_ids = [f"cand-{n}" for n in range(12085, 12089)]
    new_mention_ids = [
        "m-chp8-p226-leading-artists-group",
        "m-chp8-p226-delayed-artists-group",
        "m-chp8-p226-suggested-artists-group",
        "m-chp8-p226-established-masters-group",
    ]
    additions = []
    planned_statement_ids = [
        "st-chp8-p226-conti-business-acumen-documents",
        "st-chp8-p226-conti-collecting-temperament",
        "st-chp8-p226-gallery-displays-collection",
        "st-chp8-p226-conti-refuses-sale",
        "st-chp8-p226-will-seeks-collection-preservation",
        "st-chp8-p226-conti-outlives-wife",
        "st-chp8-p226-conti-outlives-son",
        "st-chp8-p226-conti-death-age-and-year",
        "st-chp8-p226-birthplace-pressure-interpretation",
        "st-chp8-p226-conti-size-requirement",
        "st-chp8-p226-conti-written-guarantee-requirement",
        "st-chp8-p226-conti-visits-venice-studios",
        "st-chp8-p226-conti-visits-bologna-studios",
        "st-chp8-p226-conti-appoints-marchesini-agent",
        "st-chp8-p226-marchesini-presses-delayed-artists",
        "st-chp8-p226-marchesini-distributes-advances",
        "st-chp8-p226-marchesini-suggests-new-artists",
        "st-chp8-p226-marchesini-proposes-work-alterations",
        "st-chp8-p226-marchesini-agency-efficiency-judgment",
        "st-chp8-p226-marchesini-veronese-description",
        "st-chp8-p226-marchesini-resides-venice",
        "st-chp8-p226-cignani-school-produces-bolognese-artists",
        "st-chp8-p226-marchesini-suitability-judgment",
        "st-chp8-p226-marchesini-close-contact-claim",
    ]
    if (candidate_ids.intersection(new_candidate_ids) or
            mention_ids.intersection(new_mention_ids) or
            existing_statement_ids.intersection(planned_statement_ids)):
        raise SystemExit("a planned p226 candidate, mention or statement ID already exists")

    for statement_id, (relation, note) in CLASSIFICATIONS.items():
        by_id[statement_id]["qualifiers"]["relation_candidate"] = relation
        by_id[statement_id]["qualifiers"]["relation_candidate_note"] = note

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

    # Preserve only the atomic fact represented by each existing row.
    revise("st-chp8-p226-conti-business-and-documents",
        predicate="traded_in_silks_and_cloth", subject="cand-0833", object_=None,
        claim="Haskell says Conti carried on a flourishing trade in silks and cloth.",
        quote="He himself carried on a flourishing trade in silks and cloth",
        relation=False, note="This describes Conti's occupation and commodities; the documentary assessment is recorded separately.",
        mentioned=["cand-0833"], extra={"ocr_corrections": [{"source_file": SOURCE_REL, "source_line": 183, "ocr": "cloth,,", "print": "cloth, and", "basis": "CHP-8.pdf physical page 28."}]})
    revise("st-chp8-p226-conti-collection-period",
        predicate="collected_pictures_from_1704_for_three_years", subject="cand-0833", object_="cand-7784",
        claim="After a journey to Venice and Bologna, Conti began collecting at the end of 1704 and acquired pictures in both cities for the next three years.",
        quote="He began collecting quite suddenly at the end of 1704 after a journey which had taken him to Venice and Bologna, and for the next three years he methodically acquired a number of pictures in both cities",
        relation=True, note="The dates and collecting activity are reported by Haskell; his reading of Conti's temperament is separated below.",
        mentioned=["cand-0833", "cand-7784", "cand-3401", "cand-3398"], lines=(183, 183),
        extra={"date_start": "1704-12 (approx.)", "duration_years": 3})
    revise("st-chp8-p226-conti-gallery-and-preservation",
        predicate="employed_local_architect_to_construct_gallery", subject="cand-0833", object_="cand-7794",
        claim="Conti employed an unnamed local architect to construct a well-lit gallery.",
        quote="He employed a local architect to construct a well-lit gallery",
        relation=True, note="The architect is unnamed but explicitly serves as the endpoint of Conti's employment for this construction.",
        mentioned=["cand-0833", "cand-7794", "cand-7785"], lines=(183, 183),
        extra={"ocr_corrections": [{"source_file": SOURCE_REL, "source_line": 183, "ocr": "silled", "print": "filled", "basis": "CHP-8.pdf physical page 28."}]})
    revise("st-chp8-p226-conti-looks-outside-lucca",
        predicate="collection_sourcing_limited_to_bologna_and_venice", subject="cand-0833", object_="cand-7784",
        claim="Haskell says Conti confined his picture sourcing to artists in Bologna and Venice, partly by accident and partly by design.",
        quote="He confined himself to Bologna and Venice, and—partly by accident and partly by design —lie managed in the process to acquire pictures",
        relation=True, note="The source directly limits Conti's artist-sourcing centers to Bologna and Venice; the birthplace-based causal explanation is separated below.",
        mentioned=["cand-0833", "cand-7784", "cand-3398", "cand-3401"], lines=(181, 182),
        extra={"ocr_corrections": [{"source_file": SOURCE_REL, "source_line": 182, "ocr": "lie", "print": "he", "basis": "CHP-8.pdf physical page 28."}]})
    revise("st-chp8-p226-conti-marriage-and-death",
        predicate="married_unnamed_woman_in_1685", subject="cand-0833", object_="cand-7792",
        claim="Haskell reports that Conti married an unnamed woman in 1685.",
        quote="He married in 1685",
        relation=True, note="The source explicitly states the marriage and year; the wife remains unnamed.",
        mentioned=["cand-0833", "cand-7792"], lines=(183, 183),
        extra={"date": 1685})
    revise("st-chp8-p226-conti-subject-size-and-guarantees",
        predicate="allowed_artists_to_choose_subjects", subject="cand-0833", object_="cand-7787",
        claim="Conti allowed his artists complete freedom to choose picture subjects.",
        quote="Though he allowed his artists complete freedom of choice as regards subject-matter",
        relation=True, note="This is one distinct part of Conti's reported commissioning practice; size and guarantee requirements are separate.",
        mentioned=["cand-0833", "cand-7787"], lines=(184, 184))
    revise("st-chp8-p226-conti-visits-studios-and-commissions",
        predicate="drew_up_first_picture_commissions", subject="cand-0833", object_="cand-7787",
        claim="Conti drew up his first picture commissions during this period of studio visits.",
        quote="drew up his first commissions",
        relation=True, note="This records the initial commissions separately from the visits to individual cities and the later order from Marchesini.",
        mentioned=["cand-0833", "cand-7787"], lines=(185, 185))
    revise("st-chp8-p226-marchesini-agent-work",
        predicate="author_assesses_marchesini_agent_work_as_efficient", subject="cand-1540", object_=None,
        claim="Haskell characterizes Marchesini as carrying out his post with keenness and efficiency.",
        quote="he carried out his job with keenness and efficiency",
        relation=False, note="This is Haskell's assessment of Marchesini's performance, not a relationship claim.",
        mentioned=["cand-1540"], lines=(187, 187),
        extra={"speaker_judgment": True})
    revise("st-chp8-p226-marchesini-profile-and-cignani-school",
        predicate="studied_at_carlo_cignani_school_in_bologna", subject="cand-1540", object_="cand-7789",
        claim="Marchesini had studied at Carlo Cignani's school in Bologna.",
        quote="He lived in Venice, but had studied in the school of Carlo Cignani in Bologna",
        relation=True, note="The source directly states Marchesini's study at the named school; its status as a formal institution is unresolved.",
        mentioned=["cand-1540", "cand-0748", "cand-7789", "cand-3398"], lines=(186, 187),
        extra={"ocr_corrections": [{"source_file": SOURCE_REL, "source_line": 187, "ocr": "siom", "print": "from", "basis": "CHP-8.pdf physical page 28."}]})

    # Correct the cross-page continuation without losing Haskell's modality.
    enlightenment = by_id["st-chp8-p226-enlightenment-private-apartments-close"]
    enlightenment["subject_candidate_id"] = "cand-0467"
    enlightenment["object_candidate_id"] = "cand-12084"
    enlightenment["predicate"] = "may_have_had_intimate_pictures_in_private_apartments"
    enlightenment["qualifiers"].update({
        "claim": "In the continuation of Haskell's tentative comparison, Raimondo may have been among patrons whose private apartments held smaller, more intimate pictures, which Haskell reads as a new range of sensibility.",
        "qualification": "The cross-page statement inherits 'possible to suggest' and 'may have been'; the group and Raimondo's membership remain interpretive, not certain.",
        "relation_candidate": True,
        "relation_candidate_note": "This closes the p.225 group comparison while retaining its explicit uncertainty.",
        "mentioned_candidate_ids": ["cand-0467", "cand-12084", "cand-7731", "cand-7779"],
        "modality": "possible to suggest; may have been among",
        "continued_from_statement_id": "st-chp8-p225-enlightenment-patron-inference-open",
        "continuation_status": "closed",
    })
    enlightenment["original_quote"] = "apartments were silled with smaller and more intimate pictures betraying a wholly new range of sensibility."
    enlightenment["qualifiers"]["ocr_corrections"] = [{
        "source_file": SOURCE_REL, "source_line": 180, "ocr": "silled", "print": "filled",
        "basis": "CHP-8.pdf physical page 28.",
    }]
    parent = by_id["st-chp8-p225-enlightenment-patron-inference-open"]
    parent["qualifiers"]["qualification"] = "Both 'possible to suggest' and 'may have been' qualify the full public/private contrast; its final clause continues on p.226 L180."
    parent["qualifiers"]["mentioned_candidate_ids"] = ["cand-0467", "cand-12084", "cand-0974", "cand-7765"]

    # Fix OCR-derived plural and retain the printed singular.
    original = by_id["st-chp8-p226-conti-original-works-only"]
    original["qualifiers"]["ocr_corrections"] = [{
        "source_file": SOURCE_REL, "source_line": 184, "ocr": "originals", "print": "original",
        "basis": "CHP-8.pdf physical page 28.",
    }]
    original["original_quote"] = "He insisted that each work should be an originals painted for him alone and not copied."
    original["qualifiers"]["claim"] = "Conti required each commissioned picture to be an original painted for him alone, not a copy."
    original["qualifiers"]["qualification"] = "This is the reported originality requirement; the source's OCR plural is corrected to the printed singular."
    original["qualifiers"]["relation_candidate_note"] = original["qualifiers"]["qualification"]

    by_id["st-chp8-p226-conti-birth"]["qualifiers"]["ocr_corrections"] = [{
        "source_file": SOURCE_REL, "source_line": 183, "ocr": "Conti_was", "print": "Conti was",
        "basis": "CHP-8.pdf physical page 28.",
    }]

    # One statement per distinct assertion or relation.
    additions.extend([
        new_statement("st-chp8-p226-conti-business-acumen-documents", "cand-0833", None,
            "haskell_characterizes_conti_as_acute_businessman", 183, 183,
            "Haskell says Conti's will and other documents show him to have been an acute businessman.",
            "we can see siom his will and other documents that he was an acute man of business",
            relation=False, note="This is Haskell's interpretation of documents not independently consulted here.",
            mentioned=["cand-0833", "cand-7786", "cand-7796"], extra={"speaker_judgment": True, "ocr_corrections": [{"source_file": SOURCE_REL, "source_line": 183, "ocr": "siom", "print": "from", "basis": "CHP-8.pdf physical page 28."}]}),
        new_statement("st-chp8-p226-conti-collecting-temperament", "cand-0833", None,
            "haskell_infers_deliberate_collecting_temperament", 183, 183,
            "Haskell infers from Conti's systematic acquisitions that he knew what he wanted and avoided undue enthusiasm.",
            "in a spirit that suggests that he knew exactly what he wanted and had no intention of letting himself be carried away by any undue enthusiasm",
            relation=False, note="This is Haskell's inference about Conti's motives, distinct from the reported chronology and acquisitions.",
            mentioned=["cand-0833", "cand-7784"], extra={"speaker_judgment": True}),
        new_statement("st-chp8-p226-gallery-displays-collection", "cand-7785", "cand-7784",
            "gallery_filled_with_conti_collection_pictures", 183, 183,
            "Haskell says the gallery was filled with the right number of pictures from Conti's collection.",
            "silled it with the right number of pictures",
            relation=True, note="The gallery is the antecedent of 'it'; the text gives no exact count for the pictures placed there.",
            mentioned=["cand-7785", "cand-7784"], extra={"ocr_corrections": [{"source_file": SOURCE_REL, "source_line": 183, "ocr": "silled", "print": "filled", "basis": "CHP-8.pdf physical page 28."}]}),
        new_statement("st-chp8-p226-conti-refuses-sale", "cand-0833", "cand-7784",
            "refused_to_sell_collection_pictures_when_pressed", 183, 183,
            "Haskell says Conti refused to sell the pictures when pressed to do so.",
            "refused to sell them when pressed",
            relation=True, note="The source reports Conti's refusal concerning his collection; no prospective buyer is identified and no sale is asserted.",
            mentioned=["cand-0833", "cand-7784"]),
        new_statement("st-chp8-p226-will-seeks-collection-preservation", "cand-7786", "cand-7784",
            "will_attempted_to_preserve_collection_as_a_whole", 183, 183,
            "Haskell says Conti's will tried to ensure that the collection would be preserved as a whole.",
            "in his will tried to make sure that the collection should be preserved as a whole",
            relation=True, note="This is an attempted testamentary provision, not proof that preservation succeeded.",
            mentioned=["cand-7786", "cand-7784"]),
        new_statement("st-chp8-p226-conti-outlives-wife", "cand-0833", "cand-7792",
            "outlived_unnamed_wife", 183, 183,
            "Haskell says Conti outlived his unnamed wife.", "outlived both his wife and only son",
            relation=True, note="The source explicitly identifies the spouse relation and relative survival; her name and death date are unknown.",
            mentioned=["cand-0833", "cand-7792"]),
        new_statement("st-chp8-p226-conti-outlives-son", "cand-0833", "cand-7793",
            "outlived_only_son", 183, 183,
            "Haskell says Conti outlived his only son, whose identity is not supplied.", "outlived both his wife and only son",
            relation=True, note="'His only son' explicitly establishes the parent-child endpoint; the son's name and death date are unknown.",
            mentioned=["cand-0833", "cand-7793"]),
        new_statement("st-chp8-p226-conti-death-age-and-year", "cand-0833", None,
            "died_in_1739_at_reported_age_85", 183, 183,
            "Haskell reports that Conti died in 1739 at age 85.", "died in 1739 at the age of 85",
            relation=False, note="Death year and reported age are biographical attributes; Haskell's age is retained as stated.",
            mentioned=["cand-0833"], extra={"date": 1739, "reported_age": 85}),
        new_statement("st-chp8-p226-birthplace-pressure-interpretation", "cand-0833", None,
            "haskell_attributes_outside_artist_search_to_birthplace", 181, 181,
            "Haskell says the nature of Conti's birthplace forced him to seek talented artists beyond his native province.",
            "he too was forced by the very nature of his birthplace to look far outside his native province for talented artists",
            relation=False, note="This is Haskell's causal interpretation; the separate artist-sourcing scope is recorded in the linked collection statement.",
            mentioned=["cand-0833", "cand-1454"], extra={"speaker_judgment": True}),
        new_statement("st-chp8-p226-conti-size-requirement", "cand-0833", "cand-7787",
            "required_commissioned_pictures_to_follow_specified_sizes", 184, 184,
            "Conti required commissioned pictures to conform to specified sizes.",
            "their pictures had to conform to certain specified sizes",
            relation=True, note="This preserves the format constraint separately from subject choice and written guarantees.",
            mentioned=["cand-0833", "cand-7787"]),
        new_statement("st-chp8-p226-conti-written-guarantee-requirement", "cand-0833", "cand-7787",
            "required_written_guarantee_of_subject_and_date", 184, 184,
            "Conti required each artist to send a written guarantee giving the exact subject and date of the works.",
            "every artist was required to send him a written guarantee certifying the exact subject and date of his works",
            relation=True, note="This is a separate documentation requirement in Conti's commissioning practice.",
            mentioned=["cand-0833", "cand-7787"]),
        new_statement("st-chp8-p226-conti-visits-venice-studios", "cand-0833", "cand-3401",
            "visited_artists_studios_in_venice", 185, 185,
            "Conti visited leading artists' studios in Venice.",
            "When in Venice and Bologna—to which he subsequently returned on a number of occasions—Stefano Conti went to the studios of some of the leading artists",
            relation=True,
            note="Venice is one of the two cities where the source locates Conti's studio visits.", mentioned=["cand-0833", "cand-3401"]),
        new_statement("st-chp8-p226-conti-visits-bologna-studios", "cand-0833", "cand-3398",
            "visited_artists_studios_in_bologna", 185, 185,
            "Conti visited leading artists' studios in Bologna.",
            "When in Venice and Bologna—to which he subsequently returned on a number of occasions—Stefano Conti went to the studios of some of the leading artists",
            relation=True,
            note="Bologna is the other city where the source locates Conti's studio visits.", mentioned=["cand-0833", "cand-3398"]),
        new_statement("st-chp8-p226-conti-appoints-marchesini-agent", "cand-1540", "cand-0833",
            "appointed_as_contis_agent_by", 186, 186,
            "Conti appointed Marchesini as his agent.", "whom he appointed his agent", relation=True,
            note="The endpoint direction follows the appointee-to-appointor relation; the source explicitly states Marchesini's agency role.",
            mentioned=["cand-1540", "cand-0833"], extra={"role": "agent"}),
        new_statement("st-chp8-p226-marchesini-presses-delayed-artists", "cand-1540", "cand-12086",
            "pressed_artists_who_delayed_conti_commissions", 187, 187,
            "Marchesini pressed artists who showed signs of delay in their work for Conti.",
            "pressing on those who showed signs of delay",
            relation=True, note="The delayed artists are an explicitly described but unnamed group; group membership is open.",
            mentioned=["cand-1540", "cand-12086"]),
        new_statement("st-chp8-p226-marchesini-distributes-advances", "cand-1540", "cand-0833",
            "administered_advance_payments_for_conti", 187, 187,
            "Marchesini handed out advance payments as part of his agency work for Conti.",
            "handing out the advance payments", relation=True,
            note="The source states that Marchesini distributed advances in his agency role; recipients and individual payments are not identified.",
            mentioned=["cand-1540", "cand-0833", "cand-7787"]),
        new_statement("st-chp8-p226-marchesini-suggests-new-artists", "cand-1540", "cand-0833",
            "recommended_new_artists_to_conti", 187, 187,
            "Marchesini suggested new artists to Conti.", "suggesting new artists", relation=True,
            note="The source identifies Conti as Marchesini's patron and reports the recommendation; the artists remain unnamed.",
            mentioned=["cand-1540", "cand-0833", "cand-12087"]),
        new_statement("st-chp8-p226-marchesini-proposes-work-alterations", "cand-1540", "cand-12088",
            "proposed_alterations_to_established_masters_works", 187, 187,
            "Marchesini proposed alterations to works by established masters.",
            "proposing alterations in the work of established masters", relation=True,
            note="The source refers to unidentified works by established masters; neither works nor artists are individually identified.",
            mentioned=["cand-1540", "cand-12088"]),
        new_statement("st-chp8-p226-marchesini-veronese-description", "cand-1540", None,
            "described_as_veronese_painter", 185, 185,
            "Haskell describes Marchesini as a Veronese painter.", "a Veronese painter", relation=False,
            note="This is a regional biographical description, not a relationship claim.", mentioned=["cand-1540"]),
        new_statement("st-chp8-p226-marchesini-resides-venice", "cand-1540", "cand-3401",
            "lived_in_venice", 186, 186,
            "Marchesini lived in Venice.", "He lived in Venice", relation=True,
            note="The source explicitly links Marchesini's residence to Venice.", mentioned=["cand-1540", "cand-3401"]),
        new_statement("st-chp8-p226-cignani-school-produces-bolognese-artists", "cand-7789", "cand-12085",
            "school_was_source_of_bolognas_leading_artists", 187, 187,
            "Haskell says the school of Carlo Cignani produced all the leading artists in Bologna.",
            "siom which sprung all the leading artists in the city", relation=True,
            note="This is Haskell's broad claim; the artists are unnamed and the school group remains untyped and open.",
            mentioned=["cand-7789", "cand-3398", "cand-12085"], extra={"ocr_corrections": [{"source_file": SOURCE_REL, "source_line": 187, "ocr": "siom", "print": "from", "basis": "CHP-8.pdf physical page 28."}]}),
        new_statement("st-chp8-p226-marchesini-suitability-judgment", "cand-1540", None,
            "haskell_judges_marchesini_suitable_despite_limited_gifts", 186, 186,
            "Haskell considers Marchesini suitable as agent despite his very limited gifts.",
            "For this post Marchesini was ideally suitable despite his very limited gifts", relation=False,
            note="This is Haskell's assessment of Marchesini's aptitude and abilities.", mentioned=["cand-1540"],
            extra={"speaker_judgment": True}),
        new_statement("st-chp8-p226-marchesini-close-contact-claim", "cand-1540", None,
            "haskell_says_marchesini_was_in_close_contact_with_everybody", 187, 187,
            "Haskell says Marchesini was in close contact with everybody in Bologna's artistic scene.",
            "He was thus in close contact with everybody", relation=False,
            note="This is a broad authorial generalization; 'everybody' does not identify a usable relation endpoint.",
            mentioned=["cand-1540", "cand-3398"], extra={"speaker_judgment": True}),
    ])

    # Add only the unnamed groups needed as explicit relationship endpoints.
    new_candidates = [
        {"candidate_id": "cand-12085", "index_entry_id": "", "canonical_name": "Leading artists associated with the school of Carlo Cignani in Bologna (unnamed group)", "index_page_range": "", "suggested_type": "", "status": "open", "index_source_file": "", "sub_entry": "", "detail": "Haskell says the school produced all leading artists in Bologna; no artists are named and the school's formal status remains unresolved.", "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT}#L187"},
        {"candidate_id": "cand-12086", "index_entry_id": "", "canonical_name": "Artists who delayed work for Stefano Conti (unnamed group)", "index_page_range": "", "suggested_type": "", "status": "open", "index_source_file": "", "sub_entry": "", "detail": "Marchesini pressed those who showed signs of delay; members, works and dates are unspecified.", "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT}#L187"},
        {"candidate_id": "cand-12087", "index_entry_id": "", "canonical_name": "New artists suggested by Alessandro Marchesini to Stefano Conti (unnamed group)", "index_page_range": "", "suggested_type": "", "status": "open", "index_source_file": "", "sub_entry": "", "detail": "Marchesini suggested new artists to Conti; no names or number are supplied, and the group is not assumed to match artists already commissioned.", "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT}#L187"},
        {"candidate_id": "cand-12088", "index_entry_id": "", "canonical_name": "Unidentified works by established masters that Marchesini proposed altering (work group)", "index_page_range": "", "suggested_type": "work", "status": "open", "index_source_file": "", "sub_entry": "", "detail": "Marchesini proposed alterations in the works of unnamed established masters; no individual work or artist is identified.", "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT}#L187"},
    ]
    candidates.extend(new_candidates)

    spans = [
        ("m-chp8-p226-leading-artists-group", "cand-12085", "all the leading artists in the city", "The unnamed group in Haskell's generalization about the Cignani school; membership is unknown."),
        ("m-chp8-p226-delayed-artists-group", "cand-12086", "those who showed signs of delay", "Artists whose delayed work Marchesini pressed; individuals and works are not specified."),
        ("m-chp8-p226-suggested-artists-group", "cand-12087", "new artists", "Artists Marchesini suggested to Conti; no names or number are supplied."),
        ("m-chp8-p226-established-masters-group", "cand-12088", "the work of established masters", "Unidentified works by established masters that Marchesini proposed altering."),
    ]
    for mention_id, candidate_id, surface, note in spans:
        start = segment_text.find(surface)
        if start < 0 or segment_text.find(surface, start + 1) >= 0:
            raise SystemExit(f"mention text is absent or ambiguous: {surface}")
        mentions.append({"mention_id": mention_id, "segment_id": SEGMENT, "candidate_id": candidate_id,
                         "surface_form": surface, "start_char": str(start), "end_char": str(start + len(surface)), "note": note})

    statements.extend(additions)
    target_after = [row for row in statements if row.get("segment_id") == SEGMENT]
    if any("relation_candidate" not in row.get("qualifiers", {}) for row in target_after):
        raise SystemExit("an unset relation_candidate remains in p226")
    counts = {str(value): sum(row["qualifiers"]["relation_candidate"] is value for row in target_after)
              for value in (True, False)}
    summary = {
        "segment_id": SEGMENT,
        "existing_statements": len(target),
        "classified_unset": len(unset),
        "new_statements": len(additions),
        "new_candidates": len(new_candidates),
        "new_mentions": len(spans),
        "final_statements": len(target_after),
        "relation_candidate_true": counts["True"],
        "relation_candidate_false": counts["False"],
        "relation_candidate_unset": 0,
        "ocr_corrections_recorded": 8,
    }
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
