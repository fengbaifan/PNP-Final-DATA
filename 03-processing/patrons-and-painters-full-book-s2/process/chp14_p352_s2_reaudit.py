"""Controlled semantic re-audit of p.352 S2 rows; dry-run by default."""
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
BODY = "chp-14:14_CHP-14_intro:l55-61"
NOTES = "chp-14:14_CHP-14_intro:l168-220"
SOURCE_FILE = "02-sources/02-Markdown/14_CHP-14_intro.md"
SOURCE_SHA = "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7"
PDF_SHA = "f871a00a63cfa5a9f229930cfd4b0d979baa0491ca4e7fe4d50404fa020a52e0"
EXPECTED_HASHES = {
    "book-statements.jsonl": "8f8137a3c8544b77cae3ed11797ea3cccab99779e2968af7bc1588341c31eb2f",
    "mentions.csv": "f29153aa995e9962804b1bbe33f5e9652810d8ac7b6ce49c6063f27ece677723",
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed p.352 re-audit")
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
    raise SystemExit("canonical p.352 Markdown/PDF source changed; refusing to write")

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
p352_rows = [row for row in statements if row["statement_id"].startswith("st-chp14-p352-")]
p352_mentions = [row for row in mentions if row["mention_id"].startswith("m-chp14-p352-")]
if len(p352_rows) != 21 or len(p352_mentions) != 73:
    raise SystemExit(f"unexpected p.352 baseline: {len(p352_rows)} statements, {len(p352_mentions)} mentions")

required_ids = {
    "st-chp14-p351-patronage-effect-visible-in-painting",
    "st-chp14-p351-five-selected-pictures-painted-and-lost",
    "st-chp14-p352-banquet-ordered-for-king",
    "st-chp14-p352-first-indication-of-relations",
    "st-chp14-p352-no-evidence-prior-venice-contact",
    "st-chp14-p352-tiepolo-appraisal-and-reservation",
    "st-chp14-p352-contact-and-purchase-advice",
    "st-chp14-p352-tiepolo-recognition",
    "st-chp14-p352-algarotti-position-and-mission",
    "st-chp14-p352-mutual-rapport",
    "st-chp14-p352-friendly-letter-from-villa-cordellina",
    "st-chp14-p352-january-1744-proposed-picture-to-bruhl",
    "st-chp14-p352-smith-original-patron-qualified",
    "st-chp14-p352-two-versions-related-to-double-commission",
    "st-chp14-p352-modello-paris-version",
    "st-chp14-p352-large-melbourne-version",
    "st-chp14-p352-versions-painterly-quality-differ",
    "st-chp14-p352-sketch-outdoor-setting",
    "st-chp14-p352-large-version-loggia-and-capital",
    "st-chp14-p352-cleopatra-description-continuation",
    "st-chp14-p352-note1-picture-history",
    "st-chp14-p352-note2-prior-contact",
    "st-chp14-p352-note3-tiepolo-letter",
    "st-chp9-p252-morassi-citation-note3",
    "st-chp9-p256-note5-tiepolo-letter-publication",
    "st-chp21-bib-l577-614-entry-04",
    "st-chp21-bib-l658-699-entry-13",
}
missing = required_ids - statement_by_id.keys()
if missing:
    raise SystemExit(f"required statements missing: {sorted(missing)}")

body = "\n".join(source_lines[54:61])
note_text = "\n".join(source_lines[167:220])
segment_texts = {BODY: body, NOTES: note_text}
if not body.startswith("[Page 352]\n") or "1737" not in note_text or "light" not in body:
    raise SystemExit("p.352 source excerpt did not match the registered page and note text")


def exact_quote(start, end, quote):
    excerpt = "\n".join(source_lines[start - 1:end])
    if quote not in excerpt:
        raise SystemExit(f"quote is not present at L{start}-L{end}: {quote[:100]!r}")
    return quote


def update(statement_id, *, subject=None, obj=None, predicate=None, quote=None,
           claim=None, qualification=None, mentioned=None, relation=None,
           remove_relation=False, extra=None):
    row = statement_by_id[statement_id]
    qrow = row.setdefault("qualifiers", {})
    if subject is not None:
        row["subject_candidate_id"] = subject
    if obj is not None:
        row["object_candidate_id"] = obj
    if predicate is not None:
        row["predicate"] = predicate
    if quote is not None:
        row["original_quote"] = quote
    if claim is not None:
        qrow["claim"] = claim
    if qualification is not None:
        qrow["qualification"] = qualification
    if mentioned is not None:
        qrow["mentioned_candidate_ids"] = list(dict.fromkeys(mentioned))
    if relation is not None:
        qrow["relation_candidate"] = relation
    if remove_relation:
        qrow.pop("relation_candidate", None)
    if extra:
        qrow.update(extra)
    return row


def add_statement(statement_id, segment_id, subject, obj, predicate, qualifiers, quote):
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
        "printed_page": 352,
        "pdf_physical_page": 6,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": layer,
        "qualification": qualification,
        "mentioned_candidate_ids": candidate_ids,
    }
    out.update(extra)
    return out


def add_question(row, candidate_id, question):
    items = row.setdefault("qualifiers", {}).setdefault("candidate_identity_questions", [])
    if isinstance(items, dict):
        items = [items]
        row["qualifiers"]["candidate_identity_questions"] = items
    if not any(item.get("candidate_id") == candidate_id and item.get("question") == question for item in items):
        items.append({"candidate_id": candidate_id, "question": question})


def add_mention(mention_id, candidate_id, segment_id, needle, surface=None, note="", surface_offset=0):
    if mention_id in mention_by_id:
        raise SystemExit(f"mention ID already exists: {mention_id}")
    text = segment_texts[segment_id]
    if text.count(needle) != 1:
        raise SystemExit(f"expected one source occurrence for {mention_id}: {needle!r}")
    start = text.index(needle) + surface_offset
    form = needle if surface is None else surface
    if text[start:start + len(form)] != form:
        raise SystemExit(f"mention surface is not at the requested source offset: {mention_id}")
    row = {
        "mention_id": mention_id,
        "segment_id": segment_id,
        "candidate_id": candidate_id,
        "surface_form": form,
        "start_char": str(start),
        "end_char": str(start + len(form)),
        "note": note,
    }
    mentions.append(row)
    mention_by_id[mention_id] = row
    return row


def unique_ids(values):
    return list(dict.fromkeys(values))


# Candidate re-anchoring: the index has separate person and work candidates for Tiepolo.
for number in list(range(1, 10)) + [51, 63, 69, 70, 71, 76]:
    mid = f"m-chp14-p352-{number:04d}"
    if mid not in mention_by_id:
        raise SystemExit(f"expected p.352 Tiepolo mention missing: {mid}")
    mention_by_id[mid]["candidate_id"] = "cand-2572"
mention_by_id["m-chp14-p352-0055"]["candidate_id"] = "cand-0072"
mention_by_id["m-chp14-p352-0056"]["candidate_id"] = "cand-0072"
mention_by_id["m-chp14-p352-0062"]["candidate_id"] = "cand-2572"
mention_by_id["m-chp14-p352-0064"]["candidate_id"] = "cand-0052"
mention_by_id["m-chp14-p352-0024"]["candidate_id"] = "cand-4101"
mentions = [row for row in mentions if row["mention_id"] != "m-chp14-p352-0075"]
mention_by_id.pop("m-chp14-p352-0075")
add_mention(
    "m-chp14-p352-0077", "cand-0151", BODY, "the greatest of European collectors",
    note="Contextual epithet refers to the King mentioned earlier; it is Haskell’s characterization, not an independent ranking.",
)
add_mention(
    "m-chp14-p352-0078", "cand-2440", BODY, "another patron",
    note="The next sentence identifies the original patron as almost certainly Consul Smith; preserve Haskell’s qualification.",
)
add_mention(
    "m-chp14-p352-0079", "cand-4157", BODY, "her servants", surface="her",
    note="Corefers with Cleopatra, named at the start of the same sentence.",
)
add_mention(
    "m-chp14-p352-0080", "cand-8258", NOTES, "(1955, p. 21)", surface="1955, p. 21", surface_offset=1,
    note="Locator for the Morassi publication; reused from the earlier chapter citation, not independently consulted.",
)

# Split the page-opening clause and correct its cross-page antecedent.
update(
    "st-chp14-p352-banquet-ordered-for-king",
    subject="cand-0072",
    predicate="ordered_painting_for_king",
    quote=exact_quote(56, 56, "which was ordered by him for the King on his own initiative."),
    claim="Haskell completes the p.351 sentence by saying that Algarotti ordered the Tiepolo picture for the King on his own initiative.",
    qualification="The pronouns ‘him’ and ‘his’ continue the p.351 Algarotti antecedent cand-0072. Plate 61b is the large Melbourne picture; this statement is about the order, not a completed transfer.",
    mentioned=["cand-0072", "cand-4101", "cand-0151"],
    extra={"cross_reference_statement_ids": [
        "st-chp14-p351-patronage-effect-visible-in-painting",
        "st-chp14-p352-large-version-created-by-tiepolo",
        "st-chp14-p352-large-version-not-in-original-series",
        "st-chp14-p352-large-version-intended-for-king",
    ]},
)

creator = add_statement(
    "st-chp14-p352-large-version-created-by-tiepolo", BODY, "cand-4101", "cand-2572", "created_by",
    q(56, 56, "The large picture identified at the p.351–352 page break is by Giambattista Tiepolo.",
      "authorial attribution", "The source explicitly says ‘by Tiepolo’; this identifies the large Melbourne version, not the small modello.",
      ["cand-4101", "cand-2572"], relation_candidate=True,
      cross_reference_statement_ids=["st-chp14-p351-patronage-effect-visible-in-painting", "st-chp14-p352-banquet-ordered-for-king"]),
    exact_quote(56, 56, "by Tiepolo"),
)
add_statement(
    "st-chp14-p352-large-version-not-in-original-series", BODY, "cand-4101", "cand-10273", "not_part_of_original_five_work_series",
    q(56, 56, "Haskell explicitly distinguishes this Tiepolo picture from the five-work series discussed on p.351.",
      "authorial narrative", "This is an exclusion from the p.351 group, not evidence that the painting was one of its lost five works.",
      ["cand-4101", "cand-10273"],
      cross_reference_statement_ids=["st-chp14-p351-five-selected-pictures-painted-and-lost"]),
    exact_quote(56, 56, "which did not form part of the original series"),
)
add_statement(
    "st-chp14-p352-large-version-intended-for-king", BODY, "cand-4101", "cand-0151", "ordered_for",
    q(56, 56, "Haskell says the picture was ordered for the King on Algarotti’s own initiative.",
      "authorial narrative", "The King is the stated intended beneficiary; the separate Algarotti-to-picture order is recorded in st-chp14-p352-banquet-ordered-for-king.",
      ["cand-4101", "cand-0151", "cand-0072"], relation_candidate=True,
      cross_reference_statement_ids=["st-chp14-p352-banquet-ordered-for-king"]),
    exact_quote(56, 56, "which was ordered by him for the King on his own initiative."),
)
add_question(
    statement_by_id["st-chp14-p352-banquet-ordered-for-king"], "cand-0052",
    "Compare Algarotti candidates cand-0052, cand-0054, cand-0071, cand-0072, and cand-0045 in global S3; they have separate index anchors and remain unmerged in S2.",
)

# Correct the person/work candidate mix-up and expose endpoints used by the claims.
update("st-chp14-p352-first-indication-of-relations", obj="cand-2572",
       mentioned=["cand-0052", "cand-2572", "cand-2577", "cand-4101", "cand-9559"])
update("st-chp14-p352-no-evidence-prior-venice-contact", obj="cand-2572",
       mentioned=["cand-0052", "cand-2572", "cand-2719"])
update("st-chp14-p352-tiepolo-appraisal-and-reservation", obj="cand-2572",
       mentioned=["cand-0071", "cand-2572", "cand-10272", "cand-9091"])
update("st-chp14-p352-contact-and-purchase-advice", obj="cand-2572",
       mentioned=["cand-0052", "cand-2572", "cand-2719", "cand-0947", "cand-9091"])
update("st-chp14-p352-tiepolo-recognition", subject="cand-2572",
       mentioned=["cand-2572", "cand-2719"])
add_question(
    statement_by_id["st-chp14-p352-tiepolo-recognition"], "cand-2569",
    "Compare the general Tiepolo person index candidate cand-2569 with the p.352 topical person candidate cand-2572 in global S3; keep both source anchors until alignment.",
)
update("st-chp14-p352-mutual-rapport", obj="cand-2572",
       mentioned=["cand-0052", "cand-2572"])
update(
    "st-chp14-p352-algarotti-position-and-mission",
    obj="cand-0151", predicate="official_mission_for_collector_to_buy_pictures",
    claim="Haskell contrasts Algarotti’s earlier status with his new position on an official mission to buy pictures for the King, described as the greatest of European collectors.",
    qualification="The indirect ‘greatest of European collectors’ refers contextually to the King named in the preceding sentence; preserve Haskell’s characterization without treating it as an objective ranking or a lasting employment claim.",
    mentioned=["cand-0052", "cand-0151"], relation=True,
    extra={"cross_reference_statement_ids": ["st-chp14-p352-banquet-ordered-for-king"]},
)

# Record the explicitly stated Villa decoration, then separate letter endpoints from its narrative report.
update("st-chp14-p352-friendly-letter-from-villa-cordellina", subject="cand-2572", obj="cand-10280",
       mentioned=["cand-2572", "cand-0052", "cand-10279", "cand-10280", "cand-8381"], remove_relation=True)
add_statement(
    "st-chp14-p352-tiepolo-decorated-villa-cordellina", BODY, "cand-2572", "cand-10279", "decorating",
    q(57, 57, "In October 1743, Tiepolo was decorating Villa Cordellina when he wrote the letter reported in the following clause.",
      "authorial narrative", "The activity is reported by Haskell; the 26 October date is supplied by note 3, not independently checked against the letter.",
      ["cand-2572", "cand-10279"], relation_candidate=True,
      cross_reference_statement_ids=["st-chp14-p352-friendly-letter-from-villa-cordellina"]),
    exact_quote(57, 57, "which he was then decorating"),
)
letter_edge_q = {
    "source_line_start": 57, "source_line_end": 57, "printed_page": 352, "pdf_physical_page": 6,
    "speaker": "Haskell", "text_layer": "authorial report of correspondence",
    "qualification": "The individual letter and Fogolari publication were not independently consulted; note 3 identifies the letter as 26 October 1743.",
    "mentioned_candidate_ids": ["cand-10280", "cand-2572"], "relation_candidate": True,
    "footnote_marker": "3", "footnote_segment": NOTES, "footnote_line_range": "L184",
    "footnote_text_pending": False, "footnote_body_link_status": "linked",
    "footnote_note_statement_ids": ["st-chp14-p352-note3-tiepolo-letter"],
}
add_statement(
    "st-chp14-p352-1743-letter-authored-by-tiepolo", BODY, "cand-10280", "cand-2572", "authored_by",
    dict(letter_edge_q, claim="The letter identified in note 3 was authored by Giambattista Tiepolo.",
         cross_reference_statement_ids=["st-chp14-p352-friendly-letter-from-villa-cordellina", "st-chp14-p352-note3-tiepolo-letter"]),
    exact_quote(57, 57, "Tiepolo wrote Algarotti an exceedingly friendly letter"),
)
add_statement(
    "st-chp14-p352-1743-letter-addressed-to-algarotti", BODY, "cand-10280", "cand-0052", "addressed_to",
    dict(letter_edge_q, claim="The letter identified in note 3 was addressed to Francesco Algarotti.",
         mentioned_candidate_ids=["cand-10280", "cand-0052"],
         cross_reference_statement_ids=["st-chp14-p352-friendly-letter-from-villa-cordellina", "st-chp14-p352-note3-tiepolo-letter"]),
    exact_quote(57, 57, "Tiepolo wrote Algarotti an exceedingly friendly letter"),
)

# Preserve the speaking recipient of the January 1744 report separately from the painting's planned destination.
update(
    "st-chp14-p352-january-1744-proposed-picture-to-bruhl",
    predicate="planned_to_send_picture",
    quote=exact_quote(57, 58, "It was a few months after this, in January 1744, that Algarotti mentioned for the first time to Count Briihl in\nDresden that he was planning to send a large picture by Tiepolo that had already been begun for another patron."),
    claim="In January 1744, Algarotti first told Count Brühl in Dresden that he planned to send a large Tiepolo picture already begun for another patron.",
    qualification="Count Brühl is the person told about the plan; the source does not say the picture was to be sent to him. The transfer remained planned, not completed. The next sentence identifies the original patron as almost certainly Consul Smith.",
    mentioned=["cand-0045", "cand-0458", "cand-0947", "cand-2572", "cand-4101", "cand-2440"],
)
add_question(
    statement_by_id["st-chp14-p352-january-1744-proposed-picture-to-bruhl"], "cand-0072",
    "Compare Algarotti index candidates cand-0045, cand-0052, and cand-0072 at global S3; this report to Brühl and the p.351 antecedent remain source-specific in S2.",
)

# Separate Smith's probable patron identity from the reported waiver of his claim.
update(
    "st-chp14-p352-smith-original-patron-qualified",
    quote=exact_quote(58, 58, "The picture was The Banquet of Cleopatra and the original patron was almost certainly Consul Smith"),
    claim="Haskell identifies Consul Smith as almost certainly the original patron of the Melbourne Banquet picture.",
    qualification="‘Almost certainly’ qualifies the identification of the original patron; the following sentence separately reports that Smith agreed to waive his claims.",
    mentioned=["cand-2440", "cand-4101"], relation=True,
)
add_statement(
    "st-chp14-p352-consul-smith-waived-claims", BODY, "cand-2440", "cand-4101", "waived_claims_to_picture",
    q(58, 58, "Haskell says Consul Smith agreed to waive his claims to the picture; the reason was probably financial.",
      "authorial report with qualified motive", "The waiver is reported as having occurred; only the financial explanation is marked ‘probably’.",
      ["cand-2440", "cand-4101"], relation_candidate=True,
      cross_reference_statement_ids=["st-chp14-p352-smith-original-patron-qualified", "st-chp14-p352-january-1744-proposed-picture-to-bruhl"]),
    exact_quote(58, 58, "who for some reason (probably financial) had agreed to waive his claims."),
)

# The two versions, edition-era locations, and the modello's stated relation to Tiepolo's intentions.
update("st-chp14-p352-two-versions-related-to-double-commission",
       extra={"cross_reference_statement_ids": ["st-chp14-p352-modello-paris-version", "st-chp14-p352-large-melbourne-version"]})
add_question(
    statement_by_id["st-chp14-p352-two-versions-related-to-double-commission"], "cand-2577",
    "The T.csv#40 index candidate names the Banquet generally; compare it with version candidates cand-4100 and cand-4101 in S3 without collapsing the composition and versions in S2.",
)
add_question(
    statement_by_id["st-chp14-p352-two-versions-related-to-double-commission"], "cand-2578",
    "The T.csv#41 index candidate specifies the Banquet modello; compare it with accepted work candidate cand-4100 in S3 and retain both source anchors until then.",
)
update(
    "st-chp14-p352-modello-paris-version",
    obj="cand-3659", predicate="held_by",
    quote=exact_quote(59, 60, "The first is the small modello (now in the Musée Cognacq-\n‘Jay in Paris)"),
    claim="The first version is the small modello, described in Haskell’s edition as held by Musée Cognacq-Jay in Paris (Plate 61a).",
    qualification="The museum name is wrapped and corrupted in OCR; the print and plate list read Musée Cognacq-Jay. ‘Now in’ is the 1980-edition location, not a claim about present custody.",
    mentioned=["cand-4100", "cand-3659", "cand-3955"], relation=True,
)
add_question(
    statement_by_id["st-chp14-p352-modello-paris-version"], "cand-2578",
    "The index's Banquet modello candidate cand-2578 may identify the same object as this Cognacq-Jay work candidate cand-4100; resolve the object scope in S3.",
)
add_statement(
    "st-chp14-p352-modello-shows-tiepolo-original-intentions", BODY, "cand-4100", "cand-2572", "shows_artists_original_intentions",
    q(60, 60, "Haskell says the small modello shows Tiepolo’s original intentions.",
      "authorial visual interpretation", "This describes what the modello shows; it does not by itself establish a separate authorship attribution for the modello.",
      ["cand-4100", "cand-2572"]),
    exact_quote(60, 60, "which shows what were Tiepolo’s original intentions"),
)
update(
    "st-chp14-p352-large-melbourne-version",
    obj="cand-3937", predicate="located_at",
    claim="The second version is the large picture located in Melbourne (Plate 61b).",
    qualification="The reviewed plate list identifies 61b as the National Gallery of Victoria, Felton Bequest, Melbourne; the body states Melbourne only. This is the edition-era location.",
    mentioned=["cand-4101", "cand-3937"], relation=True,
)

# Split and attribute note 2: Morassi's relationship claim, Haskell's possibility, and Haskell's evidence limit.
morassi_quote = exact_quote(183, 183, "Despite Morassi’s claim (1955, p. 21) that by 1743 ‘the friendship between them was of long standing’.")
meeting_quote = exact_quote(183, 183, "It is in fact just possible that they may have met in Milan in 1737 when Tiepolo was painting in the Palazzo Clerici and Algarotti preparing the publication of his Newtonianismo,")
no_evidence_quote = exact_quote(183, 183, "but there is no real evidence of any contact before 1743.")
update(
    "st-chp14-p352-note2-prior-contact",
    subject="cand-0052", obj="cand-2572", predicate="no_evidence_of_contact_before_1743",
    quote=no_evidence_quote,
    claim="Haskell says there is no real evidence of contact between Algarotti and Tiepolo before 1743.",
    qualification="‘No real evidence’ is not a claim that no contact occurred. It follows Haskell’s statement that a Milan meeting in 1737 is just possible; note 2 does not resolve whether they met.",
    mentioned=["cand-0052", "cand-2572"],
    extra={"text_layer": "authorial evidence qualification",
           "cross_reference_statement_ids": ["st-chp14-p352-no-evidence-prior-venice-contact", "st-chp14-p352-note2-possible-milan-meeting"]},
)
add_statement(
    "st-chp14-p352-note2-morassi-friendship-claim", NOTES, "cand-0052", "cand-2572",
    "morassi_claimed_longstanding_friendship_by_1743",
    q(183, 183, "Haskell reports Morassi’s claim that the friendship between Algarotti and Tiepolo was of long standing by 1743.",
      "Haskell's report of Morassi's attributed claim", "The friendship claim is attributed to Morassi, not endorsed as established fact by Haskell; the cited book and page were not independently consulted.",
      ["cand-8257", "cand-8258", "cand-0052", "cand-2572"], relation_candidate=True,
      citations=[{"author_candidate_id": "cand-8257", "publication_candidate_id": "cand-8258", "year": "1955", "page": "21"}],
      cross_reference_statement_ids=["st-chp14-p352-no-evidence-prior-venice-contact", "st-chp9-p252-morassi-citation-note3"]),
    morassi_quote,
)
add_statement(
    "st-chp14-p352-note2-possible-milan-meeting", NOTES, "cand-0052", "cand-2572",
    "may_have_met_in_milan_1737",
    q(183, 183, "Haskell says it is just possible that Algarotti and Tiepolo met in Milan in 1737; their reported activities there are context, not proof of a meeting.",
      "Haskell's qualified possibility", "Retain ‘just possible’ and ‘may have met’; the note expressly says there is no real evidence of contact before 1743.",
      ["cand-0052", "cand-2572", "cand-3418", "cand-10283", "cand-10258"], relation_candidate=True,
      cross_reference_statement_ids=["st-chp14-p352-note2-prior-contact", "st-chp14-p352-no-evidence-prior-venice-contact"]),
    meeting_quote,
)
update(
    "st-chp14-p352-no-evidence-prior-venice-contact",
    extra={"footnote_note_statement_ids": [
        "st-chp14-p352-note2-morassi-friendship-claim",
        "st-chp14-p352-note2-possible-milan-meeting",
        "st-chp14-p352-note2-prior-contact",
    ]},
)

# Update the note-to-bibliography and cross-chapter identity handoffs.
update(
    "st-chp14-p352-note1-picture-history",
    extra={"cross_reference_statement_ids": [
        "st-chp14-p352-first-indication-of-relations",
        "st-chp21-bib-l577-614-entry-04",
        "st-chp21-bib-l658-699-entry-13",
    ]},
)
add_question(
    statement_by_id["st-chp14-p352-note1-picture-history"], "cand-11373",
    "Compare short locator candidate cand-10281 (pp.193–203) with bibliography candidate cand-11373 (pp.199–203); preserve the printed page discrepancy for S3.",
)
update(
    "st-chp14-p352-note3-tiepolo-letter",
    extra={"cross_reference_statement_ids": [
        "st-chp14-p352-friendly-letter-from-villa-cordellina",
        "st-chp14-p352-1743-letter-authored-by-tiepolo",
        "st-chp14-p352-1743-letter-addressed-to-algarotti",
        "st-chp9-p256-note5-tiepolo-letter-publication",
    ]},
)
add_question(
    statement_by_id["st-chp14-p352-note3-tiepolo-letter"], "cand-8379",
    "Potential same-letter candidate from the p.256 note: both records identify Tiepolo’s letter to Algarotti dated 26 October 1743 and cite Fogolari 1942, p.34; compare in S3 and keep candidates separate until then.",
)

candidate_ids = {row["candidate_id"] for row in read_csv(TABLES / "entity-candidates.csv")[1]}
statement_ids = set(statement_by_id)
for row in mentions:
    if row["mention_id"].startswith("m-chp14-p352-"):
        start, end = int(row["start_char"]), int(row["end_char"])
        if row["segment_id"] not in segment_texts or segment_texts[row["segment_id"]][start:end] != row["surface_form"]:
            raise SystemExit(f"p.352 mention span mismatch: {row['mention_id']}")
        if row["candidate_id"] not in candidate_ids:
            raise SystemExit(f"p.352 mention has unresolved candidate: {row['mention_id']}")
for row in statements:
    if row["statement_id"].startswith("st-chp14-p352-"):
        quote_text = segment_texts[row["segment_id"]]
        if row["original_quote"] not in quote_text:
            raise SystemExit(f"p.352 quote does not match source: {row['statement_id']}")
        for cid in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if cid and cid not in candidate_ids:
                raise SystemExit(f"p.352 candidate endpoint missing: {row['statement_id']} -> {cid}")
        qrow = row.get("qualifiers", {})
        for cid in qrow.get("mentioned_candidate_ids", []):
            if cid not in candidate_ids:
                raise SystemExit(f"p.352 mentioned candidate missing: {row['statement_id']} -> {cid}")
        for item in qrow.get("candidate_identity_questions", []):
            if item.get("candidate_id") not in candidate_ids:
                raise SystemExit(f"p.352 identity question candidate missing: {row['statement_id']} -> {item}")
        for key in ("cross_reference_statement_ids", "linked_body_statement_ids", "linked_note_statement_ids", "footnote_note_statement_ids"):
            for ref in qrow.get(key, []):
                if ref not in statement_ids:
                    raise SystemExit(f"p.352 statement reference missing: {row['statement_id']} -> {ref}")
        if qrow.get("relation_candidate") is True and not (row.get("subject_candidate_id") and row.get("object_candidate_id")):
            raise SystemExit(f"p.352 relation candidate lacks a scalar endpoint: {row['statement_id']}")

new_p352 = [row for row in statements if row["statement_id"].startswith("st-chp14-p352-")]
relation_rows = [row for row in new_p352 if row.get("qualifiers", {}).get("relation_candidate") is True]
statement_bytes = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in statements) + "\n").encode("utf-8")
from io import StringIO
buf = StringIO(newline="")
writer = csv.DictWriter(buf, fieldnames=mention_fields, extrasaction="ignore", lineterminator="\n")
writer.writeheader()
writer.writerows(mentions)
mention_bytes = buf.getvalue().encode("utf-8")

report = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "p352_statements_before": 21,
    "p352_statements_after": len(new_p352),
    "statement_rows_added": len(new_p352) - 21,
    "p352_relation_candidates_after": len(relation_rows),
    "all_p352_relation_candidates_have_scalar_endpoints": all(r.get("subject_candidate_id") and r.get("object_candidate_id") for r in relation_rows),
    "p352_mentions_before": 73,
    "p352_mentions_after": len([row for row in mentions if row["mention_id"].startswith("m-chp14-p352-")]),
    "mentions_removed": ["m-chp14-p352-0075"],
    "mentions_added": ["m-chp14-p352-0077", "m-chp14-p352-0078", "m-chp14-p352-0079", "m-chp14-p352-0080"],
    "candidate_reanchors": ["Tiepolo person references: cand-2577 -> cand-2572", "m-chp14-p352-0055/0056: Algarotti -> cand-0072", "m-chp14-p352-0062: Tiepolo -> cand-2572", "m-chp14-p352-0064: Algarotti -> cand-0052"],
    "statement_hash_before": EXPECTED_HASHES["book-statements.jsonl"],
    "statement_hash_after": sha(statement_bytes),
    "mention_hash_before": EXPECTED_HASHES["mentions.csv"],
    "mention_hash_after": sha(mention_bytes),
}
print(json.dumps(report, ensure_ascii=False, indent=2))

if ARGS.apply:
    backup_dir = Path(tempfile.mkdtemp(prefix="pnp-chp14-p352-reaudit-"))
    originals = {statement_path: statement_path.read_bytes(), mention_path: mention_path.read_bytes()}
    (backup_dir / "book-statements.jsonl.before").write_bytes(originals[statement_path])
    (backup_dir / "mentions.csv.before").write_bytes(originals[mention_path])
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
    print(json.dumps({"recovery_backup_dir": str(backup_dir)}, ensure_ascii=False))
