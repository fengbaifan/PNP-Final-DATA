#!/usr/bin/env python3
"""Classify and atomize the p.101 S2 relation-review segment.

Default mode is a hash-guarded dry run. Pass --apply to back up and write the
three affected tables. No S6 relations are created.
"""
from __future__ import annotations

import argparse
import csv
import copy
import hashlib
import io
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_ii.md"
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l24-31"
SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
EXPECTED_SHA256 = {
    "book-statements.jsonl": "867046d48c2f5e3a863fc97f1f538f94f3f54df3e54cfdaefc20e52820a46762",
    "entity-candidates.csv": "6351f6cc9d758391424b1360de27dcf2d428b3b57f442b19f32def026b5a0d50",
    "mentions.csv": "a7f7a97d192f872d94ab6fc804d30a3866190c44a9201b94f5873aa0feeb2b29",
}
BACKUP_SUFFIX = "bak-s2-chp4-sec-ii-l24-31-relations-20261011"

UNKNOWN_IDS = {
    "st-chp4-sec-ii-l24-31-ancient-remains-as-historical-clues",
    "st-chp4-sec-ii-l24-31-cortona-drawings-citations",
    "st-chp4-sec-ii-l24-31-embryonic-university-closure",
    "st-chp4-sec-ii-l24-31-florence-gladiator-report",
    "st-chp4-sec-ii-l24-31-giustiniani-wealth",
    "st-chp4-sec-ii-l24-31-information-exchange",
    "st-chp4-sec-ii-l24-31-milan-plague-report",
    "st-chp4-sec-ii-l24-31-paper-museum-and-volumes",
    "st-chp4-sec-ii-l24-31-priapic-idol-recorded",
    "st-chp4-sec-ii-l24-31-provence-copyist-report",
    "st-chp4-sec-ii-l24-31-reclining-statue-recorded",
    "st-chp4-sec-ii-l24-31-recording-enterprise",
    "st-chp4-sec-ii-l24-31-spain-report",
    "st-chp4-sec-ii-l24-31-surviving-evidence-valued",
    "st-chp4-sec-ii-l24-31-testa-drawings-attribution",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def read_csv(path: Path) -> tuple[list[str], list[dict]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(rows)


def quote_between(text: str, left: str, right: str) -> str:
    start = text.index(left)
    end = text.index(right, start)
    return text[start:end]


def add_decision(row: dict, status: bool, note: str) -> None:
    row["qualifiers"]["relation_candidate"] = status
    row["qualifiers"]["relation_candidate_note"] = note


def update_claim(
    row: dict,
    *,
    claim: str,
    note: str,
    subject: str | None = None,
    object_: str | None = None,
    predicate: str | None = None,
    quote: str | None = None,
    mentioned: list[str] | None = None,
    speaker: str | None = None,
    text_layer: str | None = None,
    relation_candidate: bool,
) -> None:
    q = row["qualifiers"]
    q["claim"] = claim
    q["qualification"] = note
    add_decision(row, relation_candidate, note)
    if subject is not None:
        row["subject_candidate_id"] = subject
    if object_ is not None:
        row["object_candidate_id"] = object_
    if predicate is not None:
        row["predicate"] = predicate
    if quote is not None:
        row["original_quote"] = quote
    if mentioned is not None:
        q["mentioned_candidate_ids"] = mentioned
    if speaker is not None:
        q["speaker"] = speaker
    if text_layer is not None:
        q["text_layer"] = text_layer


def new_statement(
    template: dict,
    *,
    statement_id: str,
    subject: str | None,
    object_: str | None,
    predicate: str,
    claim: str,
    note: str,
    quote: str,
    mentioned: list[str],
    relation_candidate: bool,
    speaker: str | None = None,
    text_layer: str | None = None,
) -> dict:
    row = copy.deepcopy(template)
    row["statement_id"] = statement_id
    row["subject_candidate_id"] = subject
    row["object_candidate_id"] = object_
    row["predicate"] = predicate
    row["original_quote"] = quote
    q = row["qualifiers"]
    q["claim"] = claim
    q["qualification"] = note
    q["mentioned_candidate_ids"] = mentioned
    q.pop("continuation_from", None)
    q.pop("continuation_to", None)
    if speaker is not None:
        q["speaker"] = speaker
    if text_layer is not None:
        q["text_layer"] = text_layer
    add_decision(row, relation_candidate, note)
    return row


def classify_counts(rows: list[dict]) -> tuple[int, int, int, int]:
    dual = [r for r in rows if r.get("subject_candidate_id") and r.get("object_candidate_id")]
    true_count = sum(r.get("qualifiers", {}).get("relation_candidate") is True for r in dual)
    false_count = sum(r.get("qualifiers", {}).get("relation_candidate") is False for r in dual)
    unknown_count = len(dual) - true_count - false_count
    return len(dual), true_count, false_count, unknown_count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after creating recovery copies")
    args = parser.parse_args()

    statement_path = TABLES / "book-statements.jsonl"
    candidate_path = TABLES / "entity-candidates.csv"
    mention_path = TABLES / "mentions.csv"
    paths = {p.name: p for p in (statement_path, candidate_path, mention_path)}
    for name, expected in EXPECTED_SHA256.items():
        actual = sha256(paths[name])
        if actual != expected:
            raise SystemExit(f"FAIL: {name} hash changed: {actual}")
    if sha256(SOURCE) != SOURCE_SHA256:
        raise SystemExit("FAIL: source hash changed")

    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(lines[23:31])
    if len(segment_text) != 3149 or segment_text[2939:2957] != "a group at Windsor":
        raise SystemExit("FAIL: source segment or planned mention span changed")
    line26, line29, line30 = lines[25], lines[28], lines[29]

    statements = load_jsonl(statement_path)
    candidates_fields, candidates = read_csv(candidate_path)
    mentions_fields, mentions = read_csv(mention_path)
    target = [r for r in statements if r.get("segment_id") == SEGMENT_ID]
    by_id = {r["statement_id"]: r for r in target}
    if len(target) != 21 or set(by_id) != {r["statement_id"] for r in target}:
        raise SystemExit(f"FAIL: expected 21 unique statements in segment, found {len(target)}")
    before_snapshot = {
        r["statement_id"]: {
            "subject": r.get("subject_candidate_id"),
            "object": r.get("object_candidate_id"),
            "predicate": r.get("predicate"),
            "quote": r.get("original_quote"),
        }
        for r in target
    }
    unknown_dual = {
        r["statement_id"]
        for r in target
        if r.get("subject_candidate_id")
        and r.get("object_candidate_id")
        and r.get("qualifiers", {}).get("relation_candidate") not in (True, False)
    }
    if unknown_dual != UNKNOWN_IDS:
        raise SystemExit(f"FAIL: target unresolved dual set changed: {sorted(unknown_dual)}")

    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    expected_candidates = {
        "cand-2036", "cand-0342", "cand-2556", "cand-3627", "cand-3263",
        "cand-5744", "cand-5691", "cand-5694", "cand-5692", "cand-4727",
        "cand-5698", "cand-5697", "cand-5681", "cand-5695", "cand-5666",
        "cand-5682", "cand-5677", "cand-5678", "cand-0747", "cand-2418",
    }
    if not expected_candidates.issubset(candidate_by_id):
        raise SystemExit("FAIL: one or more semantic endpoints are absent")
    if candidate_by_id["cand-5681"].get("suggested_type") != "term" or candidate_by_id["cand-5695"].get("suggested_type") != "term":
        raise SystemExit("FAIL: anonymous group candidate types changed")
    if any(m.get("mention_id") == "m-chp4-sec-ii-l24-31-0050" for m in mentions):
        raise SystemExit("FAIL: planned mention ID already exists")

    def row(statement_id: str) -> dict:
        return by_id[statement_id]

    quote_info_request = quote_between(line26, "From all over the Continent", " and in return")
    quote_info_reports = line26[line26.index("and in return"):]
    quote_cortona = quote_between(line30, "Blunt and Cooke, i960", ", and Vitzthum")
    quote_vitzthum = quote_between(line30, "Vitzthum, 1961", " adds a few more") + " adds a few more."
    quote_paper = quote_between(line29, "He then bound these drawings", "—the direct ancestor")
    analogy_end = line29.index(" Veneration")
    quote_analogy = line29[line29.index("which constituted what he himself called"):analogy_end]
    if quote_analogy.endswith("3"):
        quote_analogy = quote_analogy[:-1]
    quote_project = quote_between(line29, "He therefore undertook", " He collected")
    quote_collected = quote_between(line29, "He collected the drawings", " and for many years")
    quote_employed = quote_between(line29, "for many years he employed", " city.") + " city."

    false_notes = {
        "st-chp4-sec-ii-l24-31-ancient-remains-as-historical-clues": "Haskell describes Cassiano's interpretation of ancient Roman remains; naming Rome supplies context, not a relation between Cassiano and the city.",
        "st-chp4-sec-ii-l24-31-embryonic-university-closure": "The collection is metaphorically compared with an instrument of study; this does not make it a university or establish an entity relation.",
        "st-chp4-sec-ii-l24-31-giustiniani-wealth": "This is Haskell's report of a remark about Giustiniani's wealth, not an asserted interpersonal tie, transfer, or shared activity.",
        "st-chp4-sec-ii-l24-31-surviving-evidence-valued": "Haskell interprets surviving antiquities as possible evidence about Roman customs; Rome is context, not the object of a relation from Cassiano.",
    }
    for statement_id, note in false_notes.items():
        add_decision(row(statement_id), False, note)

    update_claim(
        row("st-chp4-sec-ii-l24-31-cortona-drawings-citations"),
        claim="Haskell reports Blunt and Cooke's attribution of a Windsor drawing group to Pietro da Cortona and his studio.",
        note="The source reports an attribution, not an independently checked authorship; individual drawings are not identified. The scan reads 1960 where S0 OCR reads i960.",
        subject="cand-5691", object_="cand-0342", predicate="reported_attribution_to_pietro_da_cortona_and_studio",
        quote=quote_cortona,
        mentioned=["cand-5691", "cand-0342", "cand-5698", "cand-5697", "cand-4627"],
        speaker="Haskell reporting Blunt and Cooke", text_layer="reported scholarly attribution", relation_candidate=True,
    )
    update_claim(
        row("st-chp4-sec-ii-l24-31-drawings-held-in-two-collections"),
        claim="Haskell says part of the grouped drawings of ancient Rome are held by the British Museum.",
        note="The passage says the drawings are divided between two institutions; individual sheets are not identified and the current collection status was not checked.",
        subject="cand-5744", object_="cand-3627", predicate="reported_held_by_institution",
        mentioned=["cand-5744", "cand-3627"], relation_candidate=True,
    )
    row("st-chp4-sec-ii-l24-31-drawings-held-in-two-collections")["qualifiers"]["speaker"] = "Haskell"
    row("st-chp4-sec-ii-l24-31-drawings-held-in-two-collections")["qualifiers"]["text_layer"] = "authorial narrative"
    update_claim(
        row("st-chp4-sec-ii-l24-31-florence-gladiator-report"),
        claim="An unidentified peasant reportedly dug up two bronze gladiators near Florence.",
        note="This is an antiquarian report in the correspondence context; the peasant is unnamed and the bronze objects are not identified further.",
        subject="cand-5672", object_="cand-5671", predicate="reportedly_unearthed_two_bronze_gladiators",
        mentioned=["cand-5672", "cand-5671", "cand-3397"],
        speaker="Unidentified correspondent as reported by Haskell", text_layer="reported excavation", relation_candidate=True,
    )
    update_claim(
        row("st-chp4-sec-ii-l24-31-giustiniani-wealth"),
        claim="Haskell says Cassiano once referred rather wistfully to Giustiniani's very great wealth.",
        note=false_notes["st-chp4-sec-ii-l24-31-giustiniani-wealth"], relation_candidate=False,
    )
    update_claim(
        row("st-chp4-sec-ii-l24-31-information-exchange"),
        claim="Scholars and dilettantes from the Continent wrote to Cassiano asking for information.",
        note="Direction is from the unnamed correspondent group to Cassiano; the passage does not say that Cassiano answered.",
        subject="cand-5695", object_="cand-2036", predicate="sought_information_from",
        quote=quote_info_request, mentioned=["cand-5695", "cand-2036", "cand-3462"], relation_candidate=True,
    )
    update_claim(
        row("st-chp4-sec-ii-l24-31-manuscripts-rescued"),
        claim="Cassiano rescued the unspecified Cicero manuscript from a goldsmith; Haskell reports that it was several hundred years old and bore notes he considered not contemptible.",
        note="The Cicero manuscript, its exact title and date, the annotator, and the goldsmith are unidentified; this is Haskell's report of Cassiano's record.",
        object_="cand-5677", predicate="rescued_manuscript_from_goldsmith",
        mentioned=["cand-2036", "cand-5677", "cand-0747"], relation_candidate=True,
    )
    update_claim(
        row("st-chp4-sec-ii-l24-31-milan-plague-report"),
        claim="An unnamed Milan correspondent wrote of ointments allegedly used by diabolic agents to spread plague.",
        note="The correspondent is described as half convinced and half sceptical; the report does not establish use of the ointments or plague causation as fact.",
        subject="cand-5670", object_="cand-5669", predicate="correspondent_reported_qualified_plague_allegation",
        mentioned=["cand-5670", "cand-5669", "cand-3418"],
        speaker="Unidentified correspondent as reported by Haskell", text_layer="nested reported allegation", relation_candidate=True,
    )
    update_claim(
        row("st-chp4-sec-ii-l24-31-paper-museum-and-volumes"),
        claim="Cassiano bound the drawings into more than 23 volumes according to contemporaries; Haskell says they formed the collection Cassiano called his paper museum.",
        note="The volume count is attributed to contemporaries. The paper museum remains distinct from the library-and-museum candidate; footnote 3 is a source pointer, not independent verification.",
        predicate="bound_drawings_into_paper_museum", quote=quote_paper,
        mentioned=["cand-2036", "cand-5666"], relation_candidate=True,
    )
    update_claim(
        row("st-chp4-sec-ii-l24-31-priapic-idol-recorded"),
        claim="Cassiano recorded a Priapic idol in his collection that was found near S. Agnese beyond Porta Pia.",
        note="The idol and site remain unidentified; do not conflate this place reference with other S. Agnese sites.",
        relation_candidate=True,
    )
    update_claim(
        row("st-chp4-sec-ii-l24-31-provence-copyist-report"),
        claim="A report described an unnamed artist carefully copying Roman remains in Provence.",
        note="This records the artist's reported copying activity in Provence; no personal relation between Cassiano and the artist is asserted, and the remains are unspecified.",
        subject="cand-5674", object_="cand-5673", predicate="reported_copying_activity_in_place",
        mentioned=["cand-5674", "cand-5673", "cand-4490"],
        speaker="Unidentified report relayed by Haskell", text_layer="reported activity", relation_candidate=True,
    )
    update_claim(
        row("st-chp4-sec-ii-l24-31-reclining-statue-recorded"),
        claim="Cassiano recorded an unidentified reclining statue with an inscription in praise of Epicurean life, unearthed during excavation for the baldacchino at St Peter's.",
        note="The statue and inscription are not identified further; 'immoral' is Haskell's quoted evaluation.",
        relation_candidate=True,
    )
    update_claim(
        row("st-chp4-sec-ii-l24-31-recording-enterprise"),
        claim="Cassiano undertook a project to record all traces of Roman civilisation that had survived.",
        note="The project is described by Haskell as an amazing enterprise; the evaluation belongs to the author.",
        predicate="undertook_project_to_record_roman_traces", quote=quote_project,
        mentioned=["cand-2036", "cand-5680"], relation_candidate=True,
    )
    update_claim(
        row("st-chp4-sec-ii-l24-31-spain-report"),
        claim="A report sent to Cassiano included a Spanish story of vegetables growing out of a man's stomach.",
        note="This is recorded as a strange report, not a verified occurrence.", relation_candidate=True,
    )
    update_claim(
        row("st-chp4-sec-ii-l24-31-surviving-evidence-valued"),
        claim="Haskell says every surviving trace mattered because a battered relief or imperfect inscription might illuminate Roman custom or ceremony.",
        note=false_notes["st-chp4-sec-ii-l24-31-surviving-evidence-valued"], relation_candidate=False,
    )
    update_claim(
        row("st-chp4-sec-ii-l24-31-testa-drawings-attribution"),
        claim="Haskell reports Blunt's attribution of a large Windsor drawing group to Pietro Testa.",
        note="This is an attribution reported by Haskell, not independently checked; neither the group nor its individual drawings are enumerated.",
        subject="cand-5694", object_="cand-2556", predicate="reported_attribution_to_pietro_testa",
        mentioned=["cand-5694", "cand-2556", "cand-0379", "cand-5693", "cand-4627"],
        speaker="Haskell reporting Blunt", text_layer="reported scholarly attribution", relation_candidate=True,
    )

    info_template = row("st-chp4-sec-ii-l24-31-information-exchange")
    info_reports = new_statement(
        info_template,
        statement_id="st-chp4-sec-ii-l24-31-information-reports-sent",
        subject="cand-5695", object_="cand-2036", predicate="sent_reports_to",
        claim="The same scholars and dilettantes sent Cassiano reports of strange natural occurrences and local antiquarian investigations.",
        note="The reports are attributed to the unnamed correspondent group; their contents are not independently verified.",
        quote=quote_info_reports, mentioned=["cand-5695", "cand-2036", "cand-3462"],
        relation_candidate=True,
    )
    drawing_template = row("st-chp4-sec-ii-l24-31-drawings-held-in-two-collections")
    drawings_royal = new_statement(
        drawing_template,
        statement_id="st-chp4-sec-ii-l24-31-drawings-held-royal-collection",
        subject="cand-5744", object_="cand-3263", predicate="reported_held_by_institution",
        claim="Haskell says part of the grouped drawings of ancient Rome are held by the Royal Collection.",
        note="The passage says the drawings are divided between two institutions; individual sheets are not identified and the current collection status was not checked.",
        quote=drawing_template["original_quote"], mentioned=["cand-5744", "cand-3263"], relation_candidate=True,
        speaker="Haskell", text_layer="authorial narrative",
    )
    manuscript_template = row("st-chp4-sec-ii-l24-31-manuscripts-rescued")
    manuscript_seneca = new_statement(
        manuscript_template,
        statement_id="st-chp4-sec-ii-l24-31-manuscripts-seneca-rescued",
        subject="cand-2036", object_="cand-5678", predicate="rescued_manuscript_from_goldsmith",
        claim="Cassiano rescued the unspecified Seneca manuscript from a goldsmith; Haskell reports that it was several hundred years old and bore notes he considered not contemptible.",
        note="The Seneca manuscript, its exact title and date, the annotator, and the goldsmith are unidentified; this is Haskell's report of Cassiano's record.",
        quote=manuscript_template["original_quote"], mentioned=["cand-2036", "cand-5678", "cand-2418"],
        relation_candidate=True, speaker="Haskell reporting Cassiano's record", text_layer="reported antiquarian record",
    )
    paper_template = row("st-chp4-sec-ii-l24-31-paper-museum-and-volumes")
    paper_analogy = new_statement(
        paper_template,
        statement_id="st-chp4-sec-ii-l24-31-paper-museum-analogy",
        subject="cand-5666", object_="cand-5682", predicate="paper_museum_analogized_as_ancestor_of_musee_imaginaire",
        claim="Haskell calls Cassiano's paper museum the direct ancestor of the modern musée imaginaire.",
        note="This is Haskell's conceptual analogy, not evidence of a direct historical lineage or a formal relation.",
        quote=quote_analogy, mentioned=["cand-5666", "cand-5682"], relation_candidate=False,
        speaker="Haskell", text_layer="authorial analogy",
    )
    if paper_template["qualifiers"].get("footnote_refs"):
        paper_analogy["qualifiers"]["footnote_refs"] = copy.deepcopy(paper_template["qualifiers"]["footnote_refs"])
    project_template = row("st-chp4-sec-ii-l24-31-recording-enterprise")
    collected = new_statement(
        project_template,
        statement_id="st-chp4-sec-ii-l24-31-drawings-collected",
        subject="cand-2036", object_="cand-5666", predicate="collected_drawings_and_prints_for_paper_museum",
        claim="Cassiano collected drawings and prints by earlier artists for the paper museum corpus.",
        note="The immediately following 'these drawings' connects the collected material to the volumes; exact sheets are not identified.",
        quote=quote_collected, mentioned=["cand-2036", "cand-5666"], relation_candidate=True,
        speaker="Haskell", text_layer="authorial narrative",
    )
    employed = new_statement(
        project_template,
        statement_id="st-chp4-sec-ii-l24-31-draughtsmen-employed",
        subject="cand-2036", object_="cand-5681", predicate="employed_young_draughtsmen",
        claim="Cassiano employed unnamed young draughtsmen for many years to copy antiquities throughout Rome.",
        note="The draftsmen are an unnamed collective with no individuals identified; Rome is the stated work area.",
        quote=quote_employed, mentioned=["cand-2036", "cand-5681", "cand-4490"], relation_candidate=True,
        speaker="Haskell", text_layer="authorial narrative",
    )
    citation_template = row("st-chp4-sec-ii-l24-31-cortona-drawings-citations")
    vitzthum = new_statement(
        citation_template,
        statement_id="st-chp4-sec-ii-l24-31-vitzthum-adds-drawings",
        subject="cand-5692", object_=None, predicate="cited_as_adding_further_drawings",
        claim="Haskell says Vitzthum adds a few more drawings to the discussion.",
        note="The individual drawings and any attribution they support are unspecified; this is a bibliographic/source claim, not a historical relation.",
        quote=quote_vitzthum, mentioned=["cand-5692", "cand-4727"], relation_candidate=False,
        speaker="Haskell", text_layer="authorial bibliographic summary",
    )

    additions = [info_reports, drawings_royal, manuscript_seneca, paper_analogy, collected, employed, vitzthum]
    if any(r["statement_id"] in {x["statement_id"] for x in statements} for r in additions):
        raise SystemExit("FAIL: one or more planned statement IDs already exist")
    statements.extend(additions)

    for candidate_id in ("cand-5681", "cand-5695"):
        candidate_by_id[candidate_id]["suggested_type"] = ""

    mention_id = "m-chp4-sec-ii-l24-31-0050"
    new_mention = {
        "mention_id": mention_id,
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-5691",
        "surface_form": "a group at Windsor",
        "start_char": "2939",
        "end_char": "2957",
        "note": "Unidentified Windsor drawing group reported as deriving from Pietro da Cortona and his studio.",
    }
    mentions.append(new_mention)

    for s in additions + [r for r in target if r["statement_id"] in UNKNOWN_IDS]:
        if s.get("segment_id") != SEGMENT_ID or s.get("original_quote") not in segment_text:
            raise SystemExit(f"FAIL: source quote is not anchored in segment: {s['statement_id']}")
        refs = s.get("qualifiers", {}).get("mentioned_candidate_ids", [])
        if not set(refs).issubset(candidate_by_id):
            raise SystemExit(f"FAIL: dangling mentioned candidate in {s['statement_id']}")
        for endpoint in (s.get("subject_candidate_id"), s.get("object_candidate_id")):
            if endpoint and endpoint not in candidate_by_id:
                raise SystemExit(f"FAIL: dangling endpoint in {s['statement_id']}: {endpoint}")

    if segment_text[int(new_mention["start_char"]):int(new_mention["end_char"])] != new_mention["surface_form"]:
        raise SystemExit("FAIL: new mention span does not match source")
    target_after = [r for r in statements if r.get("segment_id") == SEGMENT_ID]
    dual, true_count, false_count, unknown_count = classify_counts(target_after)
    if (len(target_after), dual, true_count, false_count, unknown_count) != (28, 23, 18, 5, 0):
        raise SystemExit(f"FAIL: unexpected target post-state: {(len(target_after), dual, true_count, false_count, unknown_count)}")
    if candidate_by_id["cand-5681"]["suggested_type"] or candidate_by_id["cand-5695"]["suggested_type"]:
        raise SystemExit("FAIL: anonymous group type correction did not apply")

    print("mode:", "apply" if args.apply else "dry-run")
    print("source sha256:", SOURCE_SHA256)
    print("table pre-state sha256:", json.dumps(EXPECTED_SHA256, ensure_ascii=True))
    print("target statements: 21 -> 28; dual-endpoint classification: 23 total, 18 true, 5 false, 0 unclassified")
    print("new statement IDs:", json.dumps([r["statement_id"] for r in additions], ensure_ascii=True))
    print("candidate type corrections: cand-5681 term -> blank; cand-5695 term -> blank")
    print("new mention:", json.dumps(new_mention, ensure_ascii=True))
    for s in target_after:
        q = s.get("qualifiers", {})
        status = q.get("relation_candidate")
        if status not in (True, False):
            continue
        before = before_snapshot.get(s["statement_id"], {})
        plan = {
            "statement_id": s["statement_id"],
            "from": [before.get("subject"), before.get("object")],
            "to": [s.get("subject_candidate_id"), s.get("object_candidate_id")],
            "predicate": s.get("predicate"),
            "relation_candidate": status,
            "note": q.get("relation_candidate_note", ""),
            "new_row": s["statement_id"] not in before_snapshot,
            "quote_changed": before.get("quote") != s.get("original_quote"),
        }
        print("plan:", json.dumps(plan, ensure_ascii=True))

    if not args.apply:
        return 0

    backups: dict[str, Path] = {}
    for name, path in paths.items():
        backup = path.with_name(f"{path.name}.{BACKUP_SUFFIX}")
        if backup.exists():
            raise SystemExit(f"FAIL: recovery copy already exists: {backup.name}")
        shutil.copy2(path, backup)
        backups[name] = backup
    temp_statement = statement_path.with_name(statement_path.name + ".tmp-s2-chp4-l24-31")
    temp_candidate = candidate_path.with_name(candidate_path.name + ".tmp-s2-chp4-l24-31")
    temp_mention = mention_path.with_name(mention_path.name + ".tmp-s2-chp4-l24-31")
    write_jsonl(temp_statement, statements)
    write_csv(temp_candidate, candidates_fields, candidates)
    original_mentions = mention_path.read_bytes()
    out = io.StringIO(newline="")
    csv.writer(out, lineterminator="\r\n").writerow([new_mention[k] for k in mentions_fields])
    appended = out.getvalue().encode("utf-8")
    with temp_mention.open("wb") as f:
        f.write(original_mentions)
        if not original_mentions.endswith((b"\n", b"\r")):
            f.write(b"\r\n")
        f.write(appended)

    # Validate all staged outputs before replacing any authority file.
    staged_statements = load_jsonl(temp_statement)
    staged_candidate_fields, staged_candidates = read_csv(temp_candidate)
    staged_mention_fields, staged_mentions = read_csv(temp_mention)
    if len(staged_statements) != len(statements) or len(staged_candidates) != len(candidates) or len(staged_mentions) != len(mentions):
        raise SystemExit("FAIL: staged table row count changed unexpectedly")
    if staged_candidate_fields != candidates_fields or staged_mention_fields != mentions_fields:
        raise SystemExit("FAIL: staged CSV header changed")
    os_replace = __import__("os").replace
    os_replace(temp_statement, statement_path)
    os_replace(temp_candidate, candidate_path)
    os_replace(temp_mention, mention_path)
    print("backups:", json.dumps({k: v.name for k, v in backups.items()}, ensure_ascii=True))
    print("post-state sha256:", json.dumps({name: sha256(path) for name, path in paths.items()}, ensure_ascii=True))
    print("post counts:", json.dumps({"statements": len(staged_statements), "candidates": len(staged_candidates), "mentions": len(staged_mentions)}, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
