"""Controlled semantic re-audit of p.367 body and notes 1-4."""

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-15.pdf"
SOURCE_SHA = "eea847f75c7876dc5b8ea38ef4b64ad30cdd6c629df6a064125ac5f63917d31f"
PDF_SHA = "357e830cc4e880909edd62975bfcd06ade1c2b432d8866229831025fe86f2885"
INPUT_SHA = {
    "book-statements.jsonl": "0826462b0f3010c5e46886307465b76e14f719063464ad61d3b7a34a170eceb1",
    "entity-candidates.csv": "815e8fb1c13abccb26a978771303a55f5320762c715d5e089bf09e561d03a458",
    "mentions.csv": "c865af50f35f2192db4be965d6202bf127e3093993a51c779ff97f0dcf7873c2",
}
SOURCE_FILE = "02-sources/02-Markdown/15_CHP-15_sec_ii.md"
BODY = "chp-15:15_CHP-15_sec_ii:l30-36"
NOTES = "chp-15:15_CHP-15_sec_ii:l90-113"
NEXT = "chp-15:15_CHP-15_sec_ii:l38-47"
BACKUP_SUFFIX = ".bak-s2-chp15-p367-semantic-reaudit-20261009"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply the reviewed p.367 S2 corrections")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp = Path(handle.name)
    temp.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp = Path(handle.name)
    temp.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("chapter 15 source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-15 PDF asset changed")
paths = {name: TABLES / name for name in INPUT_SHA}
for name, expected in INPUT_SHA.items():
    actual = hashlib.sha256(paths[name].read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f"table changed since review: {name}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
required = {
    31: ["Elementi dell’Architettura lodolianaf", "the first and only work", "utilitarian basis"],
    32: ["returned to Venice", "fifty-eight of Lodoli’s Apologhi", "The panegyric"],
    33: ["Huge debts", "amphitheatre were rejected", "Casanova and asked"],
    34: ["Waldstein, might not be prepared", "Giovanni Dubravio Skala"],
    35: ["Giovanni Adalbertho Veith"],
    36: ["Canova", "Antonio Cappello", "rococo sculpture", "Middle Ages", "dust robs the Prà della"],
    93: ["See della Valle", "published only the first volume", "full two-volume edition"],
    94: ["Apologhi immaginati", "Carlo de’ Conti Lodoli", "Bassano"],
    95: ["A Sua Eccellenza", "Zana, 1787"],
    96: ["Molmenti", "Torcellan"],
}
for number, phrases in required.items():
    for phrase in phrases:
        if phrase not in source_lines[number - 1]:
            raise SystemExit(f"required source text changed at L{number}: {phrase}")

candidate_path = paths["entity-candidates.csv"]
mention_path = paths["mentions.csv"]
statement_path = paths["book-statements.jsonl"]
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
candidate_by_id = {row["candidate_id"]: row for row in candidates}
mention_by_id = {row["mention_id"]: row for row in mentions}
statement_by_id = {row["statement_id"]: row for row in statements}

for cid in ("cand-11530", "cand-11531"):
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID collision: {cid}")
if "m-chp15-p367-memmo-0065" in mention_by_id:
    raise SystemExit("mention ID collision: m-chp15-p367-memmo-0065")
expected_old = {
    "st-chp15-p367-elementi-publication-in-rome",
    "st-chp15-p367-elementi-account-of-lodoli-theories",
    "st-chp15-p367-prato-utilitarian-basis-tribute-to-lodoli",
    "st-chp15-p367-memmo-return-procurator-1787",
    "st-chp15-p367-memmo-appointment-two-years-before-1787",
    "st-chp15-p367-apologhi-publication-and-content",
    "st-chp15-p367-apologhi-satirised-leading-figures",
    "st-chp15-p367-panegyric-praise-and-memmo-dissatisfaction",
    "st-chp15-p367-memmo-dissatisfied-with-progress",
    "st-chp15-p367-debts-amphitheatre-and-statue-progress",
    "st-chp15-p367-amphitheatre-plan-rejected-further-statues-needed",
    "st-chp15-p367-letter-to-casanova-about-waldstein",
    "st-chp15-p367-skala-possible-statue-subject",
    "st-chp15-p367-veith-alternative-statue-subject",
    "st-chp15-p367-results-difficult-to-assess",
    "st-chp15-p367-patronage-and-speed-caused-variation",
    "st-chp15-p367-canova-poleni-statue-for-venier",
    "st-chp15-p367-canova-only-sculptor-survived-his-age",
    "st-chp15-p367-canova-statue-commissioned-by-cappello-from-ferrari",
    "st-chp15-p367-canova-statue-only-contemporary-honoured",
    "st-chp15-p367-sculptural-quality-and-rococo-remains",
    "st-chp15-p367-hero-subjects-and-medieval-costumes",
    "st-chp15-p367-climate-and-prato-impression-partial",
    "st-chp15-p367-note1-della-valle-quotation",
    "st-chp15-p367-note1-elementi-first-volume-1786",
    "st-chp15-p367-note1-elementi-completion-1834",
    "st-chp15-p367-note2-apologhi-publication-1787",
    "st-chp15-p367-note3-memmo-panegyric-1787",
    "st-chp15-p367-note4-memmo-friends-citations",
}
if not expected_old.issubset(statement_by_id):
    raise SystemExit("expected p.367 first-pass statements are missing")
if sum(row["segment_id"] == BODY for row in statements) < 23:
    raise SystemExit("p.367 body statements changed")

body_text = "\n".join(source_lines[29:36])
notes_text = "\n".join(source_lines[89:113])


def quote(parts):
    out = []
    for line_number, excerpt in parts:
        source_line = source_lines[line_number - 1]
        if excerpt not in source_line:
            raise SystemExit(f"quote not present on L{line_number}: {excerpt}")
        out.append(excerpt)
    return "\n".join(out)


def set_row_quote(row, parts):
    row["original_quote"] = quote(parts)
    row["qualifiers"]["source_line_start"] = min(line for line, _ in parts)
    row["qualifiers"]["source_line_end"] = max(line for line, _ in parts)


def revise(statement_id, subject, obj, predicate, claim, parts, mentioned,
           qualification=None, relation_note=None, q_updates=None):
    row = statement_by_id[statement_id]
    row["subject_candidate_id"] = subject
    row["object_candidate_id"] = obj
    row["predicate"] = predicate
    q = row["qualifiers"]
    q["claim"] = claim
    q["mentioned_candidate_ids"] = list(dict.fromkeys(mentioned))
    if qualification is not None:
        q["qualification"] = qualification
    if relation_note is None:
        q.pop("relation_candidate", None)
        q.pop("relation_candidate_note", None)
    else:
        q["relation_candidate"] = True
        q["relation_candidate_note"] = relation_note
    if q_updates:
        q.update(q_updates)
    set_row_quote(row, parts)


def add_candidate(cid, name, kind, detail, source_line):
    row = {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY}#L{source_line}",
    }
    candidates.append(row)
    candidate_by_id[cid] = row


def add_statement(statement_id, segment_id, subject, obj, predicate, claim, parts, mentioned,
                  speaker="Haskell", text_layer="authorial report", qualification="",
                  relation_note=None, **q_updates):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID collision: {statement_id}")
    q = {
        "source_line_start": min(line for line, _ in parts),
        "source_line_end": max(line for line, _ in parts),
        "printed_page": 367, "pdf_physical_page": 7,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    q.update(q_updates)
    if relation_note is not None:
        q["relation_candidate"] = True
        q["relation_candidate_note"] = relation_note
    row = {
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": q,
        "original_quote": quote(parts), "origin": "book", "source_file": SOURCE_FILE,
    }
    statements.append(row)
    statement_by_id[statement_id] = row
    return row


def add_body(statement_id, subject, obj, predicate, claim, parts, mentioned,
             qualification="", relation_note=None):
    return add_statement(
        statement_id, BODY, subject, obj, predicate, claim, parts, mentioned,
        qualification=qualification, relation_note=relation_note,
    )


def add_note(statement_id, subject, obj, predicate, claim, parts, mentioned,
             qualification="", relation_note=None):
    return add_statement(
        statement_id, NOTES, subject, obj, predicate, claim, parts, mentioned,
        speaker="Haskell’s note", text_layer="citation trail",
        qualification=qualification, relation_note=relation_note,
        cited_source_independently_consulted=False,
    )


# Two distinct sculptures are identifiable in the text and the p.367 index.
add_candidate(
    "cand-11530",
    "Statue of Marchese Poleni commissioned from Antonio Canova for Leonardo Venier (1781)",
    "work",
    "Haskell reports an 1781 commission for a statue of Marchese Poleni, made for Leonardo Venier and associated with the Prà della Valle. The commissioner is not named; completion and surviving object are not independently verified.",
    36,
)
add_candidate(
    "cand-11531",
    "Statue of Antonio Canova commissioned by Antonio Cappello from Giovanni Ferrari",
    "work",
    "Haskell reports that within fifteen years this statue was to find a place among the heroes at the Prà della Valle. The phrase ‘the sculptor’s own statue’ and the p.367 index identify Canova as its subject; no external catalogue has been consulted.",
    36,
)

# Clarify indexed subentries and the already existing Prà place candidate.
candidate_by_id["cand-1650"]["detail"] = (
    "Index subentry M.csv#190 is ‘plan for Prà della Valle, Padua’. In S2 this candidate denotes Memmo’s plan/scheme, "
    "not the physical square or an individual statue."
)
candidate_by_id["cand-1804"]["detail"] = (
    "Index subentry P.csv#3 is Prà della Valle under the Padua headword. This candidate is retained for the city Padua; "
    "the distinct square/site is represented by place candidate cand-3960."
)
candidate_by_id["cand-1413"]["detail"] = (
    "The Lodoli index subentry identifies the Apologhi as a text. P.367 note 2 gives the full title and a Bassano "
    "[Remondini], 1787 edition; the edition has not been independently consulted."
)
candidate_by_id["cand-1651"]["detail"] = (
    "Index subentry M.csv#191 denotes the 1787 publication event, distinct from the Apologhi text/archive candidate "
    "cand-1413. P.367 note 2 links the event to Memmo’s solemn entry as Procurator."
)
candidate_by_id["cand-10505"]["suggested_type"] = "archive"
candidate_by_id["cand-10505"]["detail"] = (
    "Printed oration identified by Haskell’s p.367 note 3; classified as archive under the project rule for "
    "documents and published texts, not as an artwork. It has not been independently consulted."
)

# Correct literal entity mentions and remove generic noun phrases misread as entities.
for mention_id in ("m-chp15-p367-memmo-0004", "m-chp15-p367-memmo-0019"):
    if mention_id not in mention_by_id:
        raise SystemExit(f"expected erroneous generic mention missing: {mention_id}")
    mentions.remove(mention_by_id.pop(mention_id))

for mention_id in ("m-chp15-p367-memmo-0012", "m-chp15-p367-memmo-0049"):
    mention_by_id[mention_id]["candidate_id"] = "cand-1413"
    mention_by_id[mention_id]["note"] = "The surface form denotes the Apologhi text/archive, not the publication event cand-1651."

for mention_id in (
    "m-chp15-p367-memmo-0006", "m-chp15-p367-memmo-0014",
    "m-chp15-p367-memmo-0015", "m-chp15-p367-memmo-0029",
    "m-chp15-p367-memmo-0037", "m-chp15-p367-memmo-0043",
    "m-chp15-p367-memmo-0045", "m-chp15-p368-querini-0001",
    "m-chp15-p368-querini-0002",
):
    mention_by_id[mention_id]["candidate_id"] = "cand-3960"
    mention_by_id[mention_id]["note"] = "Prà della Valle is the square/site in Padua; retain it separately from Padua city candidate cand-1804."

poleni_mention = mention_by_id["m-chp15-p367-memmo-0031"]
poleni_mention.update({
    "candidate_id": "cand-11530", "surface_form": "a statue",
    "start_char": "1645", "end_char": "1653",
    "note": "The sculpture is a distinct work candidate; Marchese Poleni is separately mentioned at the adjacent span.",
})
canova_mention = mention_by_id["m-chp15-p367-memmo-0034"]
canova_mention.update({
    "surface_form": "the sculptor", "start_char": "1748", "end_char": "1760",
    "note": "Coreferential mention of Canova; the artwork noun is separately mentioned as cand-11531.",
})
new_work_mention = {
    "mention_id": "m-chp15-p367-memmo-0065", "segment_id": BODY,
    "candidate_id": "cand-11531", "surface_form": "statue",
    "start_char": "1767", "end_char": "1773",
    "note": "The distinct statue of Canova, commissioned by Cappello from Ferrari.",
}
mentions.append(new_work_mention)
mention_by_id[new_work_mention["mention_id"]] = new_work_mention

body_line36_offset = sum(len(source_lines[n - 1]) + 1 for n in range(30, 36))
if body_text[1748:1773] != "the sculptor’s own statue":
    raise SystemExit("p.367 sculptor/statue mention span changed")
if body_text[1645:1660] != "a statue of the":
    raise SystemExit("p.367 Poleni statue mention span changed")
for mention in mentions:
    segment_text = body_text if mention["segment_id"] == BODY else (
        notes_text if mention["segment_id"] == NOTES else None
    )
    if segment_text is None or mention["segment_id"] not in (BODY, NOTES):
        continue
    start, end = int(mention["start_char"]), int(mention["end_char"])
    if segment_text[start:end] != mention["surface_form"]:
        raise SystemExit(f"mention span mismatch: {mention['mention_id']}")

# Narrow first-pass whole-line quotes and correct entity roles.
revise(
    "st-chp15-p367-elementi-publication-in-rome", "cand-1642", "cand-1647",
    "published_elementi_in_rome_during_last_year",
    "Haskell says that during his last year in Rome Andrea Memmo published the Elementi dell’Architettura lodoliana.",
    [(31, "his last year in Rome he published the Elementi dell’Architettura lodolianaf")],
    ["cand-1642", "cand-1647", "cand-4490"],
)
revise(
    "st-chp15-p367-elementi-account-of-lodoli-theories", "cand-1647", "cand-1411",
    "described_as_first_and_only_complete_account_of_lodoli_theories",
    "Haskell describes the Elementi as the first and only work to give a complete account of Carlo Lodoli’s architectural theories.",
    [(31, "the first and only work to give a complete account of his master’s architectural theories.")],
    ["cand-1647", "cand-1411"],
)
revise(
    "st-chp15-p367-prato-utilitarian-basis-tribute-to-lodoli", "cand-1650", "cand-1411",
    "haskell_inference_utilitarian_prato_as_tribute_to_lodoli",
    "Haskell says Memmo must certainly have felt that the essentially utilitarian basis of the Prà della Valle was as much a tribute to Lodoli’s teaching as the Elementi was a defence of his system.",
    [(31, "He must - certainly have felt that the essentially utilitarian basis of the Prato della Valle was as much a tribute to the teaching of Lodoli as was this extensive defence of his system.")],
    ["cand-1642", "cand-1650", "cand-1411", "cand-1647", "cand-3960"],
    qualification="Retain Haskell’s inference (‘must certainly have felt’); the printed page reads Prà where OCR has Prato.",
    relation_note="The source explicitly frames the scheme as a tribute to Lodoli’s teaching, but Haskell presents this as an inference; keep it as an S2 candidate, not an established influence edge.",
)
revise(
    "st-chp15-p367-memmo-return-procurator-1787", "cand-1642", "cand-2719",
    "returned_to_venice_in_1787",
    "Haskell says Memmo returned to Venice in 1787.",
    [(32, "In 1787 he returned to Venice")],
    ["cand-1642", "cand-2719"],
    relation_note="Explicit person-to-place movement reported by Haskell; retain the year and return direction.",
)
add_body(
    "st-chp15-p367-memmo-assumed-procurator-office-1787", "cand-1642", "cand-8449",
    "assumed_procurator_office_in_1787",
    "Haskell says Memmo returned to take up the post of Procuratore di San Marco.",
    [(32, "to take up the post of Procuratore di San Marco")],
    ["cand-1642", "cand-8449"],
    qualification="The source distinguishes taking up the post in 1787 from the appointment two years earlier.",
    relation_note="Explicit office-taking statement; do not merge it with the earlier appointment event.",
)
revise(
    "st-chp15-p367-memmo-appointment-two-years-before-1787", "cand-1642", "cand-1644",
    "appointed_to_procurator_two_years_before_1787_return",
    "Haskell says Memmo had been appointed to the Procuratore di San Marco two years before his 1787 return.",
    [(32, "to which he had been appointed two years earlier.")],
    ["cand-1642", "cand-1644", "cand-8449"],
    qualification="The source gives a relative interval; no exact appointment date is inferred.",
    relation_note="Explicit appointment event; preserve the relative two-year interval.",
)
revise(
    "st-chp15-p367-apologhi-publication-and-content", "cand-1642", "cand-1413",
    "published_58_lodoli_apologhi_to_celebrate_official_entry",
    "Haskell says Memmo published fifty-eight of Lodoli’s Apologhi to celebrate his official assumption of office.",
    [(32, "To celebrate his official assumption of office he published fifty-eight of Lodoli’s Apologhi")],
    ["cand-1642", "cand-1411", "cand-1413", "cand-1651", "cand-8449"],
    qualification="The text/archive and the publication event are distinct candidates; note 2 gives the 1787 edition details.",
    relation_note="Explicit publication relation between Memmo and the Apologhi text; the publication event remains a separate candidate.",
)
revise(
    "st-chp15-p367-apologhi-satirised-leading-figures", "cand-1413", None,
    "apologhi_satirised_leading_venetian_figures",
    "Haskell describes the Apologhi as incisive fables that satirised many leading figures of Venetian society.",
    [(32, "a series of incisive fables which satirised many of the leading figures of Venetian society.")],
    ["cand-1413"],
)
revise(
    "st-chp15-p367-panegyric-praise-and-memmo-dissatisfaction", "cand-10505", "cand-1642",
    "panegyric_praised_memmos_achievement_at_prato",
    "Haskell says the panegyric greeting Memmo’s return praised his achievement in organising the Prà della Valle.",
    [(32, "The panegyric which greeted his return spoke enthusiastically of his great achievement in organising the Prà della"), (33, "Valle")],
    ["cand-10505", "cand-1642", "cand-1650", "cand-3960"],
    qualification="The source for the panegyric is identified in note 3 but has not been independently consulted.",
    relation_note="The printed account explicitly attributes praise to the identified panegyric; keep the relation source-bound.",
)
revise(
    "st-chp15-p367-memmo-dissatisfied-with-progress", "cand-1642", "cand-1650",
    "memmo_far_from_satisfied_with_prato_progress",
    "Haskell says Memmo himself was far from satisfied with the progress made on the Prà della Valle scheme.",
    [(33, "but Memmo himself was far from satisfied with the progress that had been made.")],
    ["cand-1642", "cand-1650", "cand-3960"],
)
revise(
    "st-chp15-p367-debts-amphitheatre-and-statue-progress", "cand-1650", None,
    "huge_prato_project_debts_had_to_be_cleared",
    "Haskell says huge debts associated with the Prà della Valle scheme had to be cleared.",
    [(33, "Huge debts had to be cleared up")],
    ["cand-1650", "cand-3960"],
    qualification="The passage does not name the debtor or assign the full debt to Memmo personally.",
)
revise(
    "st-chp15-p367-amphitheatre-plan-rejected-further-statues-needed", "cand-10509", "cand-10506",
    "municipal_authorities_rejected_amphitheatre_plan",
    "Haskell says unnamed municipal authorities rejected the more grandiose amphitheatre plan.",
    [(33, "more grandiose plans for an amphitheatre were rejected by the municipal authorities")],
    ["cand-10509", "cand-10506", "cand-3960"],
    qualification="The municipal body is unnamed; the passage does not identify a design or completed amphitheatre.",
    relation_note="Explicit rejection relation between the unnamed municipal authorities and the unrealised proposal.",
)
add_body(
    "st-chp15-p367-further-statues-still-needed", "cand-3960", None,
    "further_statues_still_needed_for_prato",
    "Haskell says further statues still needed to be installed at the Prà della Valle.",
    [(33, "further statues needed to be installed.")],
    ["cand-3960"],
    qualification="No individual statues or installer is identified.",
    relation_note="The required sculptures are an unnamed work set; keep the work endpoint open rather than map the phrase to Memmo’s plan.",
)
revise(
    "st-chp15-p367-letter-to-casanova-about-waldstein", "cand-1642", "cand-0591",
    "memmo_wrote_to_casanova",
    "Haskell says Memmo wrote to his old friend Casanova.",
    [(33, "Memmo wrote to his old friend Casanova and asked")],
    ["cand-1642", "cand-0591"],
    qualification="The specific letter is not dated or identified, and the correspondence has not been consulted.",
    relation_note="A single writing event is reported; do not generalize it into a lasting corresponded_with relation.",
    q_updates={
        "cross_reference_segments": [NOTES],
        "cross_reference_text": "P.367 note 4 cites other examples of Memmo writing to friends; the note is at consolidated L96.",
        "cross_reference_text_pending": False,
    },
)
add_body(
    "st-chp15-p367-casanova-patron-waldstein", "cand-0591", "cand-2797",
    "patronized_by",
    "Haskell describes Count Waldstein as Casanova’s patron at Dux.",
    [(33, "his patron at Dux, the Count of"), (34, "Waldstein")],
    ["cand-0591", "cand-2797", "cand-10507"],
    qualification="The possessive refers to Casanova in the reported letter context; no broader duration is stated.",
    relation_note="Explicit patronage role in Haskell’s wording, limited to the p.367 account.",
)
add_body(
    "st-chp15-p367-waldstein-might-fund-statue", "cand-2797", None,
    "might_be_willing_to_pay_for_one_prato_statue",
    "Haskell says Memmo asked whether Waldstein might be willing to pay for one statue.",
    [(33, "whether his patron at Dux, the Count of"), (34, "Waldstein, might not be prepared to pay for one—")],
    ["cand-2797", "cand-10507", "cand-3960"],
    qualification="This is a question/proposal, not an accepted commission or payment; the particular statue is unidentified.",
    relation_note="The possible work endpoint is open; preserve the conditional wording and do not treat payment as completed.",
)
revise(
    "st-chp15-p367-skala-possible-statue-subject", "cand-2436", None,
    "suggested_as_possible_subject_of_waldstein_statue",
    "Haskell tentatively suggests Giovanni Dubravio Skala as one possible subject for the statue.",
    [(34, "Giovanni Dubravio Skala, perhaps")],
    ["cand-2436", "cand-2797", "cand-3960"],
    qualification="The question mark and ‘perhaps’ are retained; no statue or commission is established.",
    relation_note="The proposed statue endpoint is unidentified; this is only a conditional subject suggestion in Haskell’s reported letter context.",
)
add_body(
    "st-chp15-p367-skala-student-description", "cand-2436", None,
    "described_as_first_german_student_at_padua_after_league_of_cambrai",
    "Haskell describes Skala as the first German student to study at Padua after the League of Cambrai.",
    [(34, "the first German student to study at Padua after the League of Cambrai?")],
    ["cand-2436", "cand-10508", "cand-1803", "cand-8351"],
    qualification="This is Haskell’s description; no exact study date is supplied.",
)
revise(
    "st-chp15-p367-veith-alternative-statue-subject", "cand-2708", None,
    "offered_as_alternative_possible_subject_of_waldstein_statue",
    "Haskell offers Giovanni Adalbertho Veith as an alternative possible subject for the statue.",
    [(35, "Or Giovanni Adalbertho Veith")],
    ["cand-2708", "cand-2797", "cand-3960"],
    qualification="This remains a suggestion in the reported letter context; no statue or commission is established.",
    relation_note="The proposed statue endpoint is unidentified; retain the conditional alternative without treating it as a commissioned work.",
)
add_body(
    "st-chp15-p367-veith-student-fame-1709", "cand-2708", None,
    "student_of_some_fame_in_1709",
    "Haskell describes Veith as a student of some fame in 1709.",
    [(35, "a student of some fame in 1709?")],
    ["cand-2708"],
    qualification="The question mark and evaluative phrase ‘some fame’ are preserved.",
)
revise(
    "st-chp15-p367-results-difficult-to-assess", "cand-1650", None,
    "haskell_says_final_results_difficult_to_assess",
    "Haskell says the final results of the Prà della Valle scheme are difficult to assess.",
    [(36, "The final results of the Prato della Valle are difficult to assess.")],
    ["cand-1650", "cand-3960"],
)
revise(
    "st-chp15-p367-patronage-and-speed-caused-variation", "cand-1650", None,
    "divided_patronage_and_low_cost_speed_led_to_variations",
    "Haskell attributes variations in quality and style to divided patronage and anxiety to complete the scheme cheaply and quickly.",
    [(36, "The strange division of patronage and the anxiety to complete the work cheaply and quickly led to notable, variations in quality and style.")],
    ["cand-1650"],
    qualification="The OCR comma in ‘notable, variations’ is unsupported by the print, which hyphenates ‘notable- variations’.",
)
revise(
    "st-chp15-p367-canova-poleni-statue-for-venier", "cand-0532", "cand-11530",
    "commissioned_to_make_poleni_statue_in_1781",
    "Haskell says Canova was commissioned in 1781 to make a statue of Marchese Poleni for Leonardo Venier.",
    [(36, "who was commissioned in 1781 to make a statue of the Marchese Poleni for Leonardo Venier")],
    ["cand-0532", "cand-11530", "cand-1968", "cand-2750"],
    qualification="The commissioner is not named; ‘for Leonardo Venier’ is not normalized to ‘commissioned by Venier’.",
    relation_note="Explicit commission-to-make statement with both named artist and proposed work; retain Haskell’s wording without inferring the commissioner.",
)
add_body(
    "st-chp15-p367-poleni-statue-depicts-poleni", "cand-11530", "cand-1968",
    "depicts",
    "Haskell identifies Marchese Poleni as the subject of the statue commissioned from Canova.",
    [(36, "a statue of the Marchese Poleni")],
    ["cand-11530", "cand-1968"],
    relation_note="Explicit work-to-depicted-person relation in Haskell’s report.",
)
add_body(
    "st-chp15-p367-poleni-statue-made-for-venier", "cand-11530", "cand-2750",
    "made_for",
    "Haskell says the statue of Marchese Poleni was made for Leonardo Venier.",
    [(36, "for Leonardo Venier")],
    ["cand-11530", "cand-2750"],
    qualification="‘For’ is preserved; the source does not explicitly name Venier as the commissioning party.",
    relation_note="The source explicitly identifies the intended beneficiary/patron context, not necessarily the legal commissioner.",
)
revise(
    "st-chp15-p367-canova-only-sculptor-survived-his-age", "cand-0532", None,
    "canova_only_sculptor_involved_to_survive_his_age",
    "Haskell says that among the sculptors involved only Canova had survived his age.",
    [(36, "Of the sculptors involved only Canova, who was commissioned in 1781 to make a statue of the Marchese Poleni for Leonardo Venier, has survived his age.")],
    ["cand-0532"],
    qualification="‘Survived his age’ is retained as Haskell’s wording/evaluation; it is not normalized into a precise lifespan or reputation claim.",
)
revise(
    "st-chp15-p367-canova-statue-commissioned-by-cappello-from-ferrari", "cand-11531", "cand-0537",
    "commissioned_by",
    "Haskell says Antonio Cappello commissioned the statue of Canova.",
    [(36, "the sculptor’s own statue, commissioned by Antonio Cappello")],
    ["cand-11531", "cand-0534", "cand-0537"],
    qualification="The statue is of Canova; Giovanni Ferrari is separately recorded as the maker. The statement describes Haskell’s retrospective account.",
    relation_note="Explicit work-to-commissioner relation in Haskell’s sentence.",
)
add_body(
    "st-chp15-p367-canova-statue-made-by-ferrari", "cand-11531", "cand-1020",
    "created_by",
    "Haskell says Giovanni Ferrari made the statue of Canova.",
    [(36, "from Giovanni Ferrari")],
    ["cand-11531", "cand-1020", "cand-0534"],
    relation_note="The source’s ‘commissioned by Cappello from Ferrari’ identifies Ferrari as the maker.",
)
add_body(
    "st-chp15-p367-canova-statue-depicts-canova", "cand-11531", "cand-0534",
    "depicts",
    "The phrase ‘the sculptor’s own statue’ identifies Canova as the statue’s subject.",
    [(36, "the sculptor’s own statue")],
    ["cand-11531", "cand-0534"],
    qualification="The p.367 Canova index subentry specifically identifies a Ferrari statue of Canova.",
    relation_note="The possessive and the p.367 index subentry support the subject attribution; preserve it as a source-bound candidate.",
)
add_body(
    "st-chp15-p367-canova-statue-placed-at-prato", "cand-11531", "cand-3960",
    "installed_at",
    "Haskell says the statue of Canova was to find its place among the heroes at the Prà della Valle within fifteen years.",
    [(36, "was to find its place among a host of great and legendary heroes")],
    ["cand-11531", "cand-0534", "cand-3960"],
    qualification="The narrative is retrospective but gives only a relative interval, not an exact installation date.",
    relation_note="Haskell reports the eventual place of the statue; keep the relative timing and source attribution.",
)
revise(
    "st-chp15-p367-canova-statue-only-contemporary-honoured", "cand-11531", None,
    "only_contemporary_statue_honoured",
    "Haskell calls the statue of Canova the only contemporary to be honoured among the great and legendary heroes.",
    [(36, "the only contemporary to be so honoured")],
    ["cand-11531", "cand-0534", "cand-3960"],
)
add_body(
    "st-chp15-p367-canova-statue-tribute-to-reputation", "cand-11531", "cand-0534",
    "assessed_as_tribute_to_artist_reputation",
    "Haskell calls the statue an astonishing tribute to Canova’s reputation.",
    [(36, "an astonishing tribute to the artist’s reputation.")],
    ["cand-11531", "cand-0534"],
)
revise(
    "st-chp15-p367-sculptural-quality-and-rococo-remains", None, None,
    "other_sculptors_assessed_as_competent_and_sometimes_elegant",
    "Haskell says many of the other sculptors involved showed great competence and sometimes graceful elegance.",
    [(36, "Many of the others, however, show great competence and sometimes a graceful elegance")],
    ["cand-3960"],
    qualification="‘The others’ refers to unnamed sculptors involved in the scheme; no individual identities are inferred.",
)
add_body(
    "st-chp15-p367-rococo-sculpture-remains-at-prato", "cand-3960", "cand-10510",
    "pra_best_place_to_view_rococo_remains_before_neoclassicism",
    "Haskell presents the Prà della Valle as one of Italy’s best places to view remaining Rococo sculpture before Neo-classicism swept it away.",
    [(36, "which curiously enough makes the Prato della Valle one of the best places in Italy to look at the last remaining vestiges of rococo sculpture before neo-classicism swept it all away.")],
    ["cand-3960", "cand-10510", "cand-6439"],
    qualification="This is Haskell’s aesthetic evaluation of the site and surviving sculpture, not an exhaustive claim about every statue.",
)
revise(
    "st-chp15-p367-hero-subjects-and-medieval-costumes", "cand-3960", None,
    "heroes_at_prato_range_from_donors_ancestors_to_livy_and_galileo",
    "Haskell says the heroes represented at the Prà della Valle range in distinction from a donor’s insignificant ancestor to Livy or Galileo.",
    [(36, "Very many of the heroes celebrated, who vary in distinction between some noble donor’s insignificant ancestor to Livy or Galileo")],
    ["cand-3960", "cand-6836", "cand-1105"],
    qualification="No specific anonymous ancestor or unnamed statue is identified.",
)
add_body(
    "st-chp15-p367-heroes-period-middle-ages", "cand-3960", "cand-10511",
    "many_heroes_date_from_middle_ages",
    "Haskell says very many of the heroes celebrated at the Prà della Valle date from the Middle Ages.",
    [(36, "date from the Middle Ages")],
    ["cand-3960", "cand-10511"],
)
add_body(
    "st-chp15-p367-hero-costumes-reproduced", "cand-3960", None,
    "hero_costumes_reproduced_with_varying_accuracy_and_seriousness",
    "Haskell says the heroes’ costumes are reproduced with varying degrees of accuracy and seriousness.",
    [(36, "their costumes are reproduced with varying degrees of accuracy and seriousness.")],
    ["cand-3960"],
)
revise(
    "st-chp15-p367-climate-and-prato-impression-partial", "cand-3960", None,
    "time_climate_and_summer_conditions_modify_prato_impression",
    "Haskell says time and the Italian climate modified the original impression; in summer vegetation withers and dust removes the Prà della Valle’s original oasis-like effect.",
    [(36, "Now time and the Italian climate have modified much of the original impression. In summer the vegetation withers and dust robs the Prà della")],
    ["cand-3960"],
    qualification="The source sentence continues on p.368 L39 with ‘Valle of the effect it must originally have made of an oasis…’; that continuation has been read and linked.",
    q_updates={
        "predicate_status": "complete",
        "cross_reference_segments": [NEXT],
        "cross_reference_text": "P.367 L36 ends ‘dust robs the Prà della’; p.368 L39 continues ‘Valle of the effect it must originally have made of an oasis…’.",
        "cross_reference_text_pending": False,
    },
)

# Separate the publication event, its text, authorship, and occasion in note 2.
revise(
    "st-chp15-p367-note1-della-valle-quotation", None, "cand-10503",
    "note_quotes_della_valle_on_prato_lodoli_and_patronage",
    "Haskell’s note quotes a passage cited to Della Valle, volume III, p.459, praising the Prà della Valle statues, the partly published Lodolian system, and its addressee as among the first patrons.",
    [(93, source_lines[92])],
    ["cand-10503", "cand-1642", "cand-3960", "cand-10504", "cand-1411", "cand-1647"],
    qualification="The Italian passage is reproduced by Haskell; the cited source is not independently consulted. The second-person addressee is contextually associated with Memmo, without external verification.",
)
revise(
    "st-chp15-p367-note1-elementi-first-volume-1786", "cand-1642", "cand-1647",
    "note_says_only_first_elementi_volume_published_1786",
    "P.367 note 1 says that for some reason Memmo published only the first volume of the Elementi in 1786.",
    [(93, "For some reason Memmo published only the first volume of his Elementi in 1786")],
    ["cand-1642", "cand-1647"],
    qualification="The note’s wording ‘for some reason’ signals that it does not explain why; the work has not been independently consulted.",
)
revise(
    "st-chp15-p367-note1-elementi-completion-1834", "cand-1642", "cand-1647",
    "note_says_elementi_completed_before_death_full_edition_1834",
    "P.367 note 1 says Memmo completed the whole work before his death, but the full two-volume edition did not appear until 1834.",
    [(93, "though he completed the whole work before his death the full two-volume edition did not appear until 1834")],
    ["cand-1642", "cand-1647"],
    qualification="Recorded as Haskell’s note, not independently verified publication history.",
)
revise(
    "st-chp15-p367-note2-apologhi-publication-1787", "cand-1651", "cand-1413",
    "publication_event_produced_apologhi_1787",
    "P.367 note 2 gives the full Apologhi title and identifies the Bassano [Remondini], 1787 edition.",
    [(94, source_lines[93])],
    ["cand-1651", "cand-1413", "cand-1411", "cand-1642", "cand-8449", "cand-10052", "cand-2122"],
    qualification="The title and imprint are transcribed from Haskell’s note; the edition has not been independently consulted. OCR ‘Procurala’ is corrected to print ‘Procuratia’ in S2 only.",
    relation_note="The note identifies a publication event and its resulting text/archive; retain the 1787 edition as source-level evidence.",
)
add_note(
    "st-chp15-p367-note2-apologhi-authored-by-lodoli", "cand-1413", "cand-1411",
    "authored_by",
    "P.367 note 2 attributes the Apologhi to Carlo de’ Conti Lodoli and says he devised and presented them orally to his friends.",
    [(94, "dal Fu Carlo de’ Conti Lodoli")],
    ["cand-1413", "cand-1411"],
    qualification="This is the attribution printed in Haskell’s note; the cited edition has not been independently consulted.",
    relation_note="Explicit source attribution in the full title; do not treat the book’s author as independently verified.",
)
add_note(
    "st-chp15-p367-note2-publication-occasion-memmo-entry", "cand-1651", "cand-1642",
    "publication_on_occasion_of_memmos_procurator_entry",
    "P.367 note 2 says the publication occurred on the occasion of Memmo’s solemn entry as Procurator di San Marco.",
    [(94, "nell'occasione del Solenne Ingresso che fa alla Procurala di S. Marco l’eccellentissimo Signor Andrea Memmo")],
    ["cand-1651", "cand-1642", "cand-8449"],
    qualification="The note’s print spelling is corrected in S2; no separate entry-event date beyond 1787 is inferred.",
    relation_note="Explicit occasion link in the printed title; it does not conflate the 1787 office entry with the appointment two years earlier.",
)
revise(
    "st-chp15-p367-note3-memmo-panegyric-1787", "cand-10505", "cand-1642",
    "oration_for_memmo_procurator_entry_printed_1787",
    "P.367 note 3 identifies an oration for Andrea Memmo’s solemn entry as Procurator di San Marco, printed in Venice by Zatta in 1787.",
    [(95, "A Sua Eccellenza il Signor Andrea Memmo Cavaliere e Procurator di San Marco in occasione del suo ingresso solenne—orazione, Venezia, Zana, 1787.")],
    ["cand-10505", "cand-1642", "cand-8449", "cand-2719", "cand-2865"],
    qualification="The note is linked to the panegyric statement on the preceding body lines; the oration has not been independently consulted. OCR ‘Zana’ is corrected to print ‘Zatta’ in S2 only.",
    relation_note="The printed title explicitly identifies the oration as being for Memmo’s solemn entry.",
)
revise(
    "st-chp15-p367-note4-memmo-friends-citations", "cand-1642", "cand-10475",
    "note_cites_molmenti_and_torcellan_on_memmo_letters",
    "P.367 note 4 cites Molmenti’s Un nobil huomo, pages 143–144, and directs readers to Torcellan (1963) for other examples of Memmo writing to friends in this way.",
    [(96, "Molmenti: Un nobil huomo, pp. 143-4. For many other examples of Memmo writing to his friends in this way see Torcellan, 1963.")],
    ["cand-1642", "cand-10474", "cand-10475", "cand-10476"],
    qualification="Neither cited work has been independently consulted. The printed marker follows the Veith sentence; the second citation concerns Memmo’s letter-writing context on this page.",
)

# Link the two note-2 source statements from the body footnote and attach the note to the
# source text candidate without duplicating any new footnote layer.
note2_ids = [
    "st-chp15-p367-note2-apologhi-publication-1787",
    "st-chp15-p367-note2-apologhi-authored-by-lodoli",
    "st-chp15-p367-note2-publication-occasion-memmo-entry",
]
for statement_id in (
    "st-chp15-p367-apologhi-publication-and-content",
    "st-chp15-p367-apologhi-satirised-leading-figures",
):
    statement_by_id[statement_id]["qualifiers"]["footnote_note_statement_ids"] = note2_ids
    statement_by_id[statement_id]["qualifiers"]["footnote_text_pending"] = False
    statement_by_id[statement_id]["qualifiers"]["footnote_body_link_status"] = "linked"

# The existing p.368 continuation shares the same physical square; do not leave its
# antecedent attached to the Padua city candidate.
for statement_id in (
    "st-chp15-p368-prato-effect-of-decay",
    "st-chp15-p368-prato-beauty-utility-and-enlightenment",
):
    row = statement_by_id[statement_id]
    if row["subject_candidate_id"] == "cand-1804":
        row["subject_candidate_id"] = "cand-3960"
    q = row["qualifiers"]
    q["mentioned_candidate_ids"] = [
        "cand-3960" if cid == "cand-1804" else cid
        for cid in q.get("mentioned_candidate_ids", [])
    ]

# All additions must stay on the already reviewed source spans and preserve source text.
new_p367 = [
    row for row in statements
    if row["statement_id"].startswith("st-chp15-p367-")
]
if len(new_p367) != 46:
    raise SystemExit(f"expected 46 current p.367 statements, found {len(new_p367)}")
if len([row for row in new_p367 if row["segment_id"] == BODY]) != 38:
    raise SystemExit("unexpected p.367 body statement count")
if len([row for row in new_p367 if row["segment_id"] == NOTES]) != 8:
    raise SystemExit("unexpected p.367 note statement count")
if any(row["qualifiers"].get("predicate_status") == "partial" for row in new_p367):
    raise SystemExit("p.367 retained a partial statement despite the completed p.368 continuation")

candidate_ids = {row["candidate_id"] for row in candidates}
statement_ids = [row["statement_id"] for row in statements]
if len(statement_ids) != len(set(statement_ids)):
    raise SystemExit("duplicate statement IDs")
for row in statements:
    for key in ("subject_candidate_id", "object_candidate_id"):
        cid = row.get(key)
        if cid and cid not in candidate_ids:
            raise SystemExit(f"unresolved {key}: {row['statement_id']} -> {cid}")
    for cid in row.get("qualifiers", {}).get("mentioned_candidate_ids", []):
        if cid not in candidate_ids:
            raise SystemExit(f"unresolved mentioned candidate: {row['statement_id']} -> {cid}")

new_mentions = [row for row in mentions if row["mention_id"] == "m-chp15-p367-memmo-0065"]
if len(new_mentions) != 1:
    raise SystemExit("expected the single added Canova-statue mention")
relation_candidates = [
    row for row in new_p367 if row.get("qualifiers", {}).get("relation_candidate") is True
]
open_relations = [
    row for row in relation_candidates
    if not row.get("subject_candidate_id") or not row.get("object_candidate_id")
]

result = {
    "mode": "apply" if args.apply else "preview",
    "printed_page": 367,
    "pdf_physical_page": 7,
    "candidates_added": 2,
    "candidate_type_correction": "cand-10505 work -> archive",
    "p367_statements": len(new_p367),
    "p367_body_statements": 38,
    "p367_note_statements": 8,
    "p367_mentions": len([row for row in mentions if row["mention_id"].startswith("m-chp15-p367-memmo-")]),
    "p367_relation_candidates": len(relation_candidates),
    "p367_open_relation_candidates": len(open_relations),
    "generic_mentions_removed": ["m-chp15-p367-memmo-0004", "m-chp15-p367-memmo-0019"],
    "p368_square_references_reassigned": 4,
    "next_segment": NEXT,
}

if args.apply:
    touched = [candidate_path, mention_path, statement_path]
    backups = [(path, path.with_name(path.name + BACKUP_SUFFIX)) for path in touched]
    collision = next((backup for _, backup in backups if backup.exists()), None)
    if collision:
        raise SystemExit(f"backup already exists: {collision.name}")
    for path, backup in backups:
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions)
    write_jsonl(statement_path, statements)
print(json.dumps(result, ensure_ascii=False, indent=2))
