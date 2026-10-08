"""Controlled semantic re-audit of the p.351 S2 table rows; dry-run by default."""
import argparse
import csv
import hashlib
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "14_CHP-14_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-14.pdf"
BODY = "chp-14:14_CHP-14_intro:l46-53"
NOTES = "chp-14:14_CHP-14_intro:l168-220"
SOURCE_FILE = "02-sources/02-Markdown/14_CHP-14_intro.md"
SOURCE_SHA = "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7"
PDF_SHA = "f871a00a63cfa5a9f229930cfd4b0d979baa0491ca4e7fe4d50404fa020a52e0"
EXPECTED_HASHES = {
    "book-statements.jsonl": "be1b395307bb0868eeea390308e0bdff360800e1a213676d84061925a232af38",
    "mentions.csv": "e9b0909d16300d7bf3d62b185fdceb15be2ad63db8f648409ee2c88c4676196f",
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed re-audit")
ARGS = parser.parse_args()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


if sha(SOURCE.read_bytes()) != SOURCE_SHA or sha(PDF.read_bytes()) != PDF_SHA:
    raise SystemExit("canonical p.351 Markdown/PDF source changed; refusing to write")

statement_path = TABLES / "book-statements.jsonl"
mention_path = TABLES / "mentions.csv"
for path in (statement_path, mention_path):
    current_hash = sha(path.read_bytes())
    if current_hash != EXPECTED_HASHES[path.name]:
        raise SystemExit(f"table baseline changed: {path.name} ({current_hash})")

statements = read_jsonl(statement_path)
mention_fields, mentions = read_csv(mention_path)
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
statement_by_id = {row["statement_id"]: row for row in statements}
mention_by_id = {row["mention_id"]: row for row in mentions}

p351_rows = [row for row in statements if row["statement_id"].startswith("st-chp14-p351-")]
p351_mentions = [row for row in mentions if row["mention_id"].startswith("m-chp14-p351-")]
if len(p351_rows) != 23 or len(p351_mentions) != 67:
    raise SystemExit(f"unexpected p.351 baseline: {len(p351_rows)} statements, {len(p351_mentions)} mentions")

required_statements = {
    "st-chp14-p350-appraisal-of-venetian-artists",
    "st-chp14-p350-proposed-living-artist-commissions",
    "st-chp14-p351-style-based-subject-choice",
    "st-chp14-p351-piazzetta-appraisal",
    "st-chp14-p351-pittoni-appraisal",
    "st-chp14-p351-tiepolo-appraisal",
    "st-chp14-p351-history-painters-in-plan",
    "st-chp14-p351-zuccarelli-proposed-subject",
    "st-chp14-p351-pannini-subject",
    "st-chp14-p351-canaletto-omitted",
    "st-chp14-p351-boucher-subjects-and-cooperation",
    "st-chp14-p351-neapolitan-subjects",
    "st-chp14-p351-bologna-subjects",
    "st-chp14-p351-venetian-artists-and-amigoni",
    "st-chp14-p351-rome-artists",
    "st-chp14-p351-time-away-and-evidence-basis",
    "st-chp14-p351-returned-to-implement-proposals",
    "st-chp14-p351-old-master-preference-and-modern-art-success",
    "st-chp14-p351-five-selected-pictures-painted-and-lost",
    "st-chp14-p351-note2-lost-pictures",
    "st-chp14-p352-banquet-ordered-for-king",
    "st-chp14-p352-no-evidence-prior-venice-contact",
    "st-chp10-p331-algarotti-letter-and-salon-comparison",
    "st-chp21-bib-l461-496-entry-08",
    "st-chp21-bib-l985-1020-entry-13",
}
missing = required_statements - statement_by_id.keys()
if missing:
    raise SystemExit(f"required statements missing: {sorted(missing)}")

body = "\n".join(source_lines[45:53])
note_text = "\n".join(source_lines[167:220])
segment_texts = {BODY: body, NOTES: note_text}
if not body.startswith("[Page 351]\n") or "We can, however, see the effect of his patronage in a painting" not in body:
    raise SystemExit("p.351 cross-page fragment did not match the registered source text")


def exact_quote(start, end, quote):
    excerpt = "\n".join(source_lines[start - 1:end])
    if quote not in excerpt:
        raise SystemExit(f"quote is not present at L{start}-L{end}: {quote[:100]!r}")
    return quote


def statement(statement_id, segment_id, subject, obj, predicate, qualifiers, quote):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    row = {
        "statement_id": statement_id,
        "segment_id": segment_id,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_FILE,
    }
    statements.append(row)
    statement_by_id[statement_id] = row
    return row


def q(start, end, claim, layer, qualification, candidate_ids, **extra):
    out = {
        "source_line_start": start,
        "source_line_end": end,
        "printed_page": 351,
        "pdf_physical_page": 5,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": layer,
        "qualification": qualification,
        "mentioned_candidate_ids": candidate_ids,
    }
    out.update(extra)
    return out


def update(identifier, *, subject=None, obj=None, predicate=None, claim=None,
           qualification=None, mentioned=None, relation=None, remove_relation=False,
           add_extra=None, cross_refs=None, quote=None):
    row = statement_by_id[identifier]
    if subject is not None:
        row["subject_candidate_id"] = subject
    if obj is not None:
        row["object_candidate_id"] = obj
    if predicate is not None:
        row["predicate"] = predicate
    if quote is not None:
        row["original_quote"] = quote
    qualifiers = row["qualifiers"]
    if claim is not None:
        qualifiers["claim"] = claim
    if qualification is not None:
        qualifiers["qualification"] = qualification
    if mentioned is not None:
        qualifiers["mentioned_candidate_ids"] = mentioned
    if relation is not None:
        qualifiers["relation_candidate"] = relation
    if remove_relation:
        qualifiers.pop("relation_candidate", None)
    if cross_refs is not None:
        qualifiers["cross_reference_statement_ids"] = cross_refs
    if add_extra:
        qualifiers.update(add_extra)
    return row


# Correct two possessive mentions: these refer to Algarotti, not Pittoni.
for mention_id, note in (
    ("m-chp14-p351-0062", "In ‘one of his most attractive characteristics’, ‘his’ refers to Algarotti."),
    ("m-chp14-p351-0063", "In ‘his influence on individual painters’, ‘his’ refers to Algarotti."),
):
    row = mention_by_id[mention_id]
    if row["candidate_id"] != "cand-1950":
        raise SystemExit(f"unexpected prior referent mapping: {mention_id}")
    row["candidate_id"] = "cand-0072"
    row["note"] = note

# Add seven singular-person coreference mentions omitted in the first pass.
new_mentions = [
    ("m-chp14-p351-0068", "he", 1173, 1175, "cand-0072", "In ‘artists he proposes’, ‘he’ refers to Algarotti."),
    ("m-chp14-p351-0069", "his", 1534, 1537, "cand-1827", "In ‘his vedute’, the possessive refers to Pannini."),
    ("m-chp14-p351-0070", "his", 1715, 1718, "cand-0072", "In ‘his foreign travels’, the possessive refers to Algarotti."),
    ("m-chp14-p351-0071", "he", 1838, 1840, "cand-0072", "In ‘he included Boucher’, ‘he’ refers to Algarotti."),
    ("m-chp14-p351-0072", "He", 2095, 2097, "cand-0072", "In ‘He found subjects’, the subject refers to Algarotti."),
    ("m-chp14-p351-0073", "his", 2372, 2375, "cand-0072", "In ‘his detachment from Roman values’, the possessive refers to Algarotti."),
    ("m-chp14-p351-0074", "his", 2679, 2682, "cand-0072", "In ‘his comments’, the possessive refers to Algarotti."),
]
added_mentions = []
for mention_id, surface, start, end, candidate_id, note in new_mentions:
    if mention_id in mention_by_id:
        raise SystemExit(f"mention ID already exists: {mention_id}")
    if body[start:end] != surface:
        raise SystemExit(f"mention span mismatch before write: {mention_id} -> {body[start:end]!r}")
    row = {
        "mention_id": mention_id,
        "segment_id": BODY,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    }
    added_mentions.append(row)

last_p351_index = max(i for i, row in enumerate(mentions) if row["mention_id"].startswith("m-chp14-p351-"))
mentions[last_p351_index + 1:last_p351_index + 1] = added_mentions

# Complete the cross-page continuation from p.350 to p.351.
update(
    "st-chp14-p350-appraisal-of-venetian-artists",
    qualification="The quoted appraisal is complete on p.350 L44. Its following sentence is completed at p.351 L47 and recorded as st-chp14-p351-style-based-subject-choice.",
    cross_refs=["st-chp14-p351-style-based-subject-choice"],
    add_extra={"cross_reference_segments": [BODY], "cross_reference_text": "continuation at p.351 L47 completes the next sentence"},
)
update(
    "st-chp14-p351-style-based-subject-choice",
    cross_refs=["st-chp14-p350-appraisal-of-venetian-artists"],
    add_extra={"cross_reference_text": "completes the sentence opened at p.350 L44"},
)

# Record that the three named artists are classified as history painters.
statement(
    "st-chp14-p351-history-painters-named", BODY, "cand-10278", None,
    "classification_applied_to_three_named_artists",
    q(47, 47, "Haskell calls Tiepolo, Pittoni, and Piazzetta history painters in the gallery proposal.",
      "authorial report of a proposal", "This is Haskell’s category for the proposed list, not a claim of formal school membership.",
      ["cand-10278", "cand-2572", "cand-1950", "cand-1902"],
      ocr_corrections=[{"source_line": 47, "ocr": "Piazzctta", "print": "Piazzetta", "basis": "CHP-14.pdf physical page 5."}]),
    exact_quote(47, 47, "Thus Tiepolo, Pittoni and Piazzctta were all ‘history painters’"),
)

# The clause explicitly says Algarotti chose different subjects for the three artists.
subject_clause = exact_quote(
    47, 47,
    "Thus Tiepolo, Pittoni and Piazzctta were all ‘history painters’: but Algarotti chose very different subjects for them, because",
)
for suffix, candidate_id, label in (
    ("tiepolo", "cand-2572", "Tiepolo"),
    ("pittoni", "cand-1950", "Pittoni"),
    ("piazzetta", "cand-1902", "Piazzetta"),
):
    statement(
        f"st-chp14-p351-{suffix}-subject-choice", BODY, "cand-0072", candidate_id,
        "chose_different_subject_for_artist_in_gallery_plan",
        q(47, 47, f"Algarotti chose a different subject for {label} within the proposed gallery scheme.",
          "authorial report of a proposal", "The individual subject is not specified by this comparison; later examples remain separately recorded and are not forced into a one-to-one mapping.",
          ["cand-0072", candidate_id, "cand-10278"], relation_candidate=True,
          ocr_corrections=[{"source_line": 47, "ocr": "Piazzctta", "print": "Piazzetta", "basis": "CHP-14.pdf physical page 5."}]),
        subject_clause,
    )

# Recast the existing rows into scalar artist endpoints where the text permits.
update(
    "st-chp14-p351-zuccarelli-proposed-subject",
    obj="cand-2879", predicate="assigned_possible_subject_to_artist",
    claim="Algarotti’s proposal gave Zuccarelli a possible subject such as The Hunt of Meleager and Atalanta, or another sad or cheerful story matching the landscape’s mood.",
    qualification="The named subject is introduced as an example and followed by alternatives; it is not evidence that this exact work was painted.",
    relation=True,
)
update("st-chp14-p351-pannini-subject", relation=True)
update("st-chp14-p351-canaletto-omitted", relation=True)

# Keep the group-level cooperation statement separate from scalar subject relations.
update(
    "st-chp14-p351-boucher-subjects-and-cooperation",
    obj=None, predicate="rare_proposed_french_italian_artist_cooperation",
    claim="Haskell calls the proposed venture involving Boucher, Balestra, and Donato Creti a rare case of French and Italian artists being required to cooperate.",
    qualification="This describes one proposed venture. The source gives no division of labour or evidence that the scheme was implemented; individual subject assignments are recorded separately.",
    mentioned=["cand-0072", "cand-0421", "cand-0168", "cand-0889", "cand-10277"],
    remove_relation=True,
)
statement_by_id["st-chp14-p351-boucher-subjects-and-cooperation"]["object_candidate_id"] = None
assignment_quote = exact_quote(
    50, 51,
    "For instance, despite rather a scornful aside, he included Boucher among the artists to be given\n‘soggetti. graziosi e leggeri’, along with Balestra and Donato Creti",
)
phrase_ocr = [{"source_line": 51, "ocr": "soggetti. graziosi", "print": "soggetti graziosi", "basis": "CHP-14.pdf physical page 5."}]
for suffix, candidate_id, label in (
    ("boucher", "cand-0421", "Boucher"),
    ("balestra", "cand-0168", "Balestra"),
    ("creti-graceful", "cand-0889", "Donato Creti"),
):
    statement(
        f"st-chp14-p351-{suffix}-subject-assignment", BODY, "cand-0072", candidate_id,
        "assigned_graceful_light_subjects_to_artist",
        q(50, 51, f"Algarotti included {label} among the artists assigned ‘soggetti graziosi e leggeri’.",
          "authorial report of a proposal", "The Italian phrase is a proposed subject category; no individual painting or completed commission is identified.",
          ["cand-0072", candidate_id, "cand-10277"], relation_candidate=True,
          ocr_corrections=phrase_ocr),
        assignment_quote,
    )

coop_quote = exact_quote(
    50, 51,
    "For instance, despite rather a scornful aside, he included Boucher among the artists to be given\n‘soggetti. graziosi e leggeri’, along with Balestra and Donato Creti—one of the very rare occasions in the eighteenth century when French and Italian artists were required to co-operate in a single venture.",
)
for suffix, first, second, pair in (
    ("boucher-balestra", "cand-0421", "cand-0168", "Boucher and Balestra"),
    ("boucher-creti", "cand-0421", "cand-0889", "Boucher and Donato Creti"),
    ("balestra-creti", "cand-0168", "cand-0889", "Balestra and Donato Creti"),
):
    statement(
        f"st-chp14-p351-{suffix}-proposed-cooperation", BODY, first, second,
        "proposed_joint_venture_with",
        q(50, 51, f"The source places {pair} in one proposed venture requiring French and Italian artists to cooperate.",
          "authorial report and interpretation of a proposal", "This pairwise relation is only a scalar candidate encoding of Haskell’s group-level cooperation statement; it does not establish separate contracts, individual roles, or implementation.",
          ["cand-0072", "cand-0421", "cand-0168", "cand-0889", "cand-10277"], relation_candidate=True,
          ocr_corrections=phrase_ocr),
        coop_quote,
    )

# The regional list is elliptical: “found subjects for” carries through the listed cities.
update(
    "st-chp14-p351-neapolitan-subjects",
    obj="cand-1716", predicate="found_subject_for_artist",
    claim="Algarotti found subjects for Francesco de Mura among the Neapolitan artists.",
    qualification="‘Among the Neapolitans’ is retained as regional context; the passage does not identify a specific city or formal organization.",
    relation=True,
)
statement(
    "st-chp14-p351-solimena-subject", BODY, "cand-0072", "cand-2484",
    "found_subject_for_artist",
    q(51, 51, "Algarotti found subjects for Solimena among the Neapolitan artists.",
      "authorial report of a proposal", "The source gives regional context but does not identify a specific city or formal organization.",
      ["cand-0072", "cand-2484"], relation_candidate=True),
    exact_quote(51, 51, "He found subjects for Francesco de Mura and Solimena among the Neapolitans"),
)
update(
    "st-chp14-p351-bologna-subjects",
    obj="cand-1383", predicate="found_subject_for_artist_in_city_context",
    claim="In the elliptical regional list, Haskell names Ercole Lelli as an artist for whom Algarotti found subjects in the Bologna context.",
    qualification="‘Found subjects for’ carries forward from the prior clause. Bologna is a context in the list, not an asserted birthplace. The scanned print reads Lelli; the OCR surface remains unchanged in S0.",
    relation=True,
    add_extra={"ocr_corrections": [{"source_line": 51, "ocr": "Ercole Lefli", "print": "Ercole Lelli", "basis": "CHP-14.pdf physical page 5."}]},
)
statement(
    "st-chp14-p351-creti-bologna-subject", BODY, "cand-0072", "cand-0889",
    "found_subject_for_artist_in_city_context",
    q(51, 51, "In the elliptical regional list, Haskell names Donato Creti as an artist for whom Algarotti found subjects in the Bologna context.",
      "authorial report of a proposal", "‘Found subjects for’ carries forward from the prior clause. Bologna is a context in the list, not an asserted birthplace.",
      ["cand-0072", "cand-0889", "cand-0381"], relation_candidate=True,
      ocr_corrections=[{"source_line": 51, "ocr": "Ercole Lefli", "print": "Ercole Lelli", "basis": "CHP-14.pdf physical page 5."}]),
    exact_quote(51, 51, "Ercole Lefli and Donato Creti in Bologna"),
)

# Amigoni is explicitly named; the four-Venetian referent stays unresolved because Canaletto was just excluded.
update(
    "st-chp14-p351-venetian-artists-and-amigoni",
    obj="cand-0094", predicate="found_subject_for_artist_in_elliptical_list",
    claim="In the continuation of the regional list, Haskell names Jacopo Amigoni among the artists for whom Algarotti found subjects.",
    qualification="The phrase ‘the four Venetians already mentioned’ is not resolved here: Canaletto was just described as ignored altogether. This statement records the explicit Amigoni endpoint and does not infer which four Venetians were selected or assign subjects to Canaletto.",
    relation=True,
    cross_refs=["st-chp14-p351-canaletto-omitted", "st-chp14-p351-tiepolo-subject-choice", "st-chp14-p351-pittoni-subject-choice", "st-chp14-p351-piazzetta-subject-choice"],
)
update(
    "st-chp14-p351-rome-artists",
    obj="cand-1506", predicate="found_subject_for_artist_in_city_context",
    claim="Haskell says Algarotti found subjects in Rome for Mancini, besides the separately described special case of Pannini.",
    qualification="‘Only’ is preserved as a limit on this part of the list; Pannini’s special case remains a separate statement.",
    relation=True,
)

# Cross-link the Venice return to the immediately preceding p.350 proposal.
update(
    "st-chp14-p351-returned-to-implement-proposals",
    obj="cand-2719", relation=True,
    qualification="‘Try to put them into effect’ expresses an attempt, not completed implementation; no date is inferred. The proposals are linked to the p.350 statement on commissioning works by living artists.",
    cross_refs=["st-chp14-p350-proposed-living-artist-commissions"],
)
update(
    "st-chp14-p350-proposed-living-artist-commissions",
    cross_refs=["st-chp14-p351-returned-to-implement-proposals"],
    add_extra={"cross_reference_segments": [BODY], "cross_reference_text": "Algarotti came to Venice soon after making these proposals, to try to put them into effect"},
)

# Separate the Augustus comparison from Algarotti's partial success.
update(
    "st-chp14-p351-old-master-preference-and-modern-art-success",
    predicate="modern_art_promotion_plan_partly_successful",
    claim="Haskell says Algarotti’s plans to promote modern art were successful to some extent.",
    qualification="‘To some extent’ is retained. Augustus’s greater enthusiasm for old masters is recorded in a separate comparison statement.",
    mentioned=["cand-0072", "cand-0151", "cand-4288"],
    add_extra={"ocr_corrections": [{"source_line": 52, "ocr": "modem", "print": "modern", "basis": "CHP-14.pdf physical page 5."}],
               "cross_reference_statement_ids": ["st-chp14-p351-augustus-old-master-preference"]},
)
statement(
    "st-chp14-p351-augustus-old-master-preference", BODY, "cand-0151", "cand-4288",
    "greater_enthusiasm_for_old_masters_than_modern_art_plan",
    q(52, 52, "Haskell contrasts Augustus’s greater enthusiasm for old masters with Algarotti’s plans to promote modern art.",
      "authorial assessment", "This is a comparative report, not a claim that Augustus exclusively preferred or collected old masters.",
      ["cand-0151", "cand-4288", "cand-0072"]),
    exact_quote(52, 52, "Despite Augustus’s far greater enthusiasm for old masters"),
)

# Separate selection, individual painting claims, and the report that the works were lost.
selection_id = "st-chp14-p351-five-selected-pictures-painted-and-lost"
selection_quote = exact_quote(52, 53, "Amigoni, Piazzetta,\nPittoni, Tiepolo and Zuccarelli painted the pictures that he chose for them")
update(
    selection_id, predicate="selected_five_picture_group_for_named_artists",
    claim="Algarotti chose the five-picture group for Amigoni, Piazzetta, Pittoni, Tiepolo, and Zuccarelli.",
    qualification="The group has no individual titles on p.351. The following sentence reports that the artists painted the selected pictures and that all were lost; those claims are separated below.",
    quote=selection_quote,
    mentioned=["cand-0072", "cand-0094", "cand-1902", "cand-1950", "cand-2572", "cand-2879", "cand-10273"],
    relation=True,
    remove_relation=False,
)
statement(
    "st-chp14-p351-pictures-reported-lost", BODY, "cand-10273", None,
    "reported_as_lost",
    q(53, 53, "Haskell reports that all five pictures in the group were lost.",
      "authorial report", "The source gives no individual titles, present locations, or independent evidence of loss; do not merge this group with other lost commissions in the chapter.",
      ["cand-10273", "cand-0094", "cand-1902", "cand-1950", "cand-2572", "cand-2879"],
      footnote_marker="2", footnote_segment=NOTES, footnote_line_range="L181",
      footnote_text_pending=False, footnote_body_link_status="linked",
      footnote_note_statement_ids=["st-chp14-p351-note2-lost-pictures"]),
    exact_quote(53, 53, "but unfortunately all have been lost.2"),
)
painting_quote = exact_quote(52, 53, "Amigoni, Piazzetta,\nPittoni, Tiepolo and Zuccarelli painted the pictures that he chose for them")
for suffix, artist, label in (
    ("amigoni", "cand-0094", "Amigoni"),
    ("piazzetta", "cand-1902", "Piazzetta"),
    ("pittoni", "cand-1950", "Pittoni"),
    ("tiepolo", "cand-2572", "Tiepolo"),
    ("zuccarelli", "cand-2879", "Zuccarelli"),
):
    statement(
        f"st-chp14-p351-{suffix}-painted-selected-picture", BODY, artist, "cand-10273",
        "painted_selected_picture_within_group",
        q(52, 53, f"Haskell includes {label} among the named painters of the pictures selected by Algarotti.",
          "authorial report", "This scalar candidate links the artist to the five-work group; it does not claim the artist painted all five works, and the individual title-to-artist mapping is not supplied.",
          ["cand-0072", artist, "cand-10273"], relation_candidate=True,
          cross_reference_statement_ids=[selection_id, "st-chp14-p351-pictures-reported-lost"]),
        painting_quote,
    )

# The possessive reference to “his patronage” starts a sentence completed on p.352.
fragment_quote = exact_quote(53, 53, "We can, however, see the effect of his patronage in a painting")
statement(
    "st-chp14-p351-patronage-effect-visible-in-painting", BODY, "cand-0072", None,
    "patronage_effect_visible_in_painting_continues_on_next_page",
    q(53, 53, "Haskell says the effect of Algarotti’s patronage can be seen in a painting.",
      "authorial narrative fragment", "The p.351 sentence stops before identifying the painting. P.352 identifies a Tiepolo painting ordered for the King and explicitly says it was outside the original five-work series; it is not one of the five lost pictures.",
      ["cand-0072"], cross_reference_statement_ids=["st-chp14-p352-banquet-ordered-for-king"]),
    fragment_quote,
)
update(
    "st-chp14-p352-banquet-ordered-for-king",
    cross_refs=["st-chp14-p351-patronage-effect-visible-in-painting"],
    add_extra={"cross_reference_text": "completes p.351 L53; the painting is outside the five-work series recorded there"},
)

# Preserve the print punctuation anomaly and link the evidence limitation across pages.
time_row = statement_by_id["st-chp14-p351-time-away-and-evidence-basis"]
time_row["qualifiers"]["qualification"] = (
    "Preserves ‘nearly’ and Haskell’s modal ‘must have’; no individual comment is assigned a specific informant. "
    "The printed source itself reads ‘after.he’ with a period, so this is not logged as an OCR correction and S0 remains unchanged."
)
time_row["qualifiers"]["cross_reference_statement_ids"] = ["st-chp14-p352-no-evidence-prior-venice-contact"]
update(
    "st-chp14-p352-no-evidence-prior-venice-contact",
    cross_refs=["st-chp14-p351-time-away-and-evidence-basis"],
    add_extra={"cross_reference_text": "p.351 records the nearly five-year absence from Venice; preserve Haskell’s limited ‘no evidence’ claim about the 1737 stay"},
)

# Update the group statement's ellipsis resolution without deciding the four-Venetian set.
update(
    "st-chp14-p351-venetian-artists-and-amigoni",
    cross_refs=[
        "st-chp14-p351-canaletto-omitted",
        "st-chp14-p351-tiepolo-subject-choice",
        "st-chp14-p351-pittoni-subject-choice",
        "st-chp14-p351-piazzetta-subject-choice",
    ],
)

# Add note 2 letter endpoints and bibliography/identity cross-references.
note2 = statement_by_id["st-chp14-p351-note2-lost-pictures"]["qualifiers"]
note2["linked_body_statement_ids"] = ["st-chp14-p351-pictures-reported-lost"]
note2["footnote_number"] = 2
note2["candidate_identity_questions"] = [
    {
        "candidate_id": "cand-9460",
        "question": "Compare this short Ferrari citation (cand-10275) with bibliography entry st-chp21-bib-l461-496-entry-08 (cand-9460); retain separate candidates until S3 alignment.",
    },
    {
        "candidate_id": "cand-9869",
        "question": "Compare the 13 February 1751 letter to Mariette cited here (cand-10274) with the S. Rocco exhibition letter reported by st-chp10-p331-algarotti-letter-and-salon-comparison (cand-9869). They may be the same letter, but neither source establishes that identity; retain both until S3 alignment.",
    },
]
note2["linked_bibliography_statement_ids"] = [
    "st-chp21-bib-l461-496-entry-08",
    "st-chp21-bib-l985-1020-entry-13",
]
note2["cross_reference_statement_ids"] = [
    "st-chp14-p351-pictures-reported-lost",
    "st-chp10-p331-algarotti-letter-and-salon-comparison",
    "st-chp21-bib-l461-496-entry-08",
    "st-chp21-bib-l985-1020-entry-13",
]
note2["cross_reference_text"] = "note 2 supports the report that the five works were lost and links its Ferrari, 1751 letter, and Posse citations to the book bibliography and related chapter passage"

note_relation_base = {
    "source_line_start": 181,
    "source_line_end": 181,
    "printed_page": 351,
    "pdf_physical_page": 5,
    "speaker": "Haskell’s footnote",
    "text_layer": "bibliographic note reporting correspondence",
    "qualification": "The note explicitly names the letter’s author and addressee; the original letter and Opere edition were not independently consulted.",
    "mentioned_candidate_ids": ["cand-10274", "cand-0072", "cand-1547"],
    "footnote_number": 2,
    "footnote_marker": "2",
    "footnote_segment": NOTES,
    "footnote_line_range": "L181",
    "footnote_text_pending": False,
    "footnote_body_link_status": "linked",
    "linked_body_statement_ids": ["st-chp14-p351-pictures-reported-lost"],
    "linked_note_statement_ids": ["st-chp14-p351-note2-lost-pictures"],
    "cross_reference_statement_ids": ["st-chp14-p351-note2-lost-pictures", "st-chp14-p351-pictures-reported-lost"],
    "relation_candidate": True,
}
statement(
    "st-chp14-p351-note2-letter-authored-by-algarotti", NOTES, "cand-10274", "cand-0072",
    "authored_by", dict(note_relation_base, claim="Haskell identifies the cited 13 February 1751 letter to Mariette as Algarotti’s letter."),
    exact_quote(181, 181, "Algarotti’s letter to Mariette of 13 February 1751"),
)
statement(
    "st-chp14-p351-note2-letter-addressed-to-mariette", NOTES, "cand-10274", "cand-1547",
    "addressed_to", dict(note_relation_base, claim="Haskell identifies Pierre-Jean Mariette as the addressee of Algarotti’s letter dated 13 February 1751."),
    exact_quote(181, 181, "Algarotti’s letter to Mariette of 13 February 1751"),
)

# Validate all p.351 offsets and candidate/statement references before preview or write.
candidate_ids = {row["candidate_id"] for row in read_csv(TABLES / "entity-candidates.csv")[1]}
statement_ids = set(statement_by_id)
for row in mentions:
    if row["mention_id"].startswith("m-chp14-p351-"):
        start, end = int(row["start_char"]), int(row["end_char"])
        if segment_texts[row["segment_id"]][start:end] != row["surface_form"]:
            raise SystemExit(f"p.351 mention span mismatch: {row['mention_id']}")
        if row["candidate_id"] not in candidate_ids:
            raise SystemExit(f"p.351 mention has unresolved candidate: {row['mention_id']}")
for row in statements:
    if row["statement_id"].startswith("st-chp14-p351-") or row["statement_id"] in {
        "st-chp14-p350-appraisal-of-venetian-artists",
        "st-chp14-p350-proposed-living-artist-commissions",
        "st-chp14-p352-banquet-ordered-for-king",
        "st-chp14-p352-no-evidence-prior-venice-contact",
    }:
        for cid in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if cid and cid not in candidate_ids:
                raise SystemExit(f"candidate endpoint missing: {row['statement_id']} -> {cid}")
        qrow = row.get("qualifiers", {})
        for cid in qrow.get("mentioned_candidate_ids", []):
            if cid not in candidate_ids:
                raise SystemExit(f"mentioned candidate missing: {row['statement_id']} -> {cid}")
        for ref in qrow.get("cross_reference_statement_ids", []) + qrow.get("linked_body_statement_ids", []) + qrow.get("linked_note_statement_ids", []) + qrow.get("footnote_note_statement_ids", []):
            if ref not in statement_ids:
                raise SystemExit(f"statement reference missing: {row['statement_id']} -> {ref}")

new_p351 = [row for row in statements if row["statement_id"].startswith("st-chp14-p351-")]
relation_rows = [row for row in new_p351 if row.get("qualifiers", {}).get("relation_candidate") is True]
statement_bytes = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in statements) + "\n").encode("utf-8")
from io import StringIO
buf = StringIO(newline="")
writer = csv.DictWriter(buf, fieldnames=mention_fields, extrasaction="ignore", lineterminator="\n")
writer.writeheader()
writer.writerows(mentions)
mention_bytes = buf.getvalue().encode("utf-8")

report = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "p351_statements_before": 23,
    "p351_statements_after": len(new_p351),
    "p351_statement_rows_added": len(new_p351) - 23,
    "p351_relation_candidates_after": len(relation_rows),
    "mentions_before": len(p351_mentions),
    "mentions_after": len([row for row in mentions if row["mention_id"].startswith("m-chp14-p351-")]),
    "mention_rows_added": len(added_mentions),
    "corrected_mentions": ["m-chp14-p351-0062", "m-chp14-p351-0063"],
    "statement_hash_before": EXPECTED_HASHES["book-statements.jsonl"],
    "statement_hash_after": sha(statement_bytes),
    "mention_hash_before": EXPECTED_HASHES["mentions.csv"],
    "mention_hash_after": sha(mention_bytes),
}
print(json.dumps(report, ensure_ascii=False, indent=2))

if ARGS.apply:
    originals = {statement_path: statement_path.read_bytes(), mention_path: mention_path.read_bytes()}
    temp_paths = []
    try:
        for path, data in ((statement_path, statement_bytes), (mention_path, mention_bytes)):
            with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as f:
                f.write(data)
                temp_paths.append((Path(f.name), path))
        for temp, target in temp_paths:
            temp.replace(target)
    except Exception:
        for path, data in originals.items():
            path.write_bytes(data)
        for temp, _ in temp_paths:
            if temp.exists():
                temp.unlink()
        raise
