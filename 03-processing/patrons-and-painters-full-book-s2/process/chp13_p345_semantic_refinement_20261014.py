#!/usr/bin/env python3
"""Controlled S2 refinement for CHP-13 printed p.345 (source lines 161-171).

Default mode is dry-run. --apply requires unchanged source tables and creates
recovery copies before writing the reviewed statements, candidates, and mentions.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
SEGMENT = "chp-13:13_CHP-13_intro:l161-171"
SOURCE_FILE = "02-sources/02-Markdown/13_CHP-13_intro.md"
BACKUP_SUFFIX = ".bak-s2-ch13-p345-semantic-review-20261014"
EXPECTED = {
    STATEMENTS: "9998eac856ad40d3bda46cea659cbf2a1948a65d63bb72d1eb3d0ecd43723b33",
    CANDIDATES: "f5a96e0e26e2759ac8a8ea69fb1bdad43fb3d95b5268cc4ae9a977e73453eb58",
    MENTIONS: "049d7ab142327849dc7ccd6f3e0ec83b3976fbcebd05a4a4823d5731ed041d17",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def dump_jsonl(rows: list[dict]) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")


def load_csv(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def dump_csv(headers: list[str], rows: list[dict]) -> bytes:
    from io import StringIO

    out = StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=headers, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    return ("\ufeff" + out.getvalue()).encode("utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write after dry-run preconditions and validations pass")
    args = ap.parse_args()

    for path, expected in EXPECTED.items():
        actual = sha(path)
        if actual != expected:
            raise SystemExit(f"precondition failed: {path.relative_to(ROOT)} sha256={actual}, expected={expected}")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(source_lines[160:171])

    def q(start: int, end: int, exact: str) -> str:
        if not (1 <= start <= end <= len(source_lines)):
            raise ValueError(f"invalid source lines: {start}-{end}")
        scoped = "\n".join(source_lines[start - 1 : end])
        if exact not in scoped:
            raise ValueError(f"quote is not exact S0 text at L{start}-L{end}: {exact!r}")
        return exact

    statement_rows = load_jsonl(STATEMENTS)
    statement_by_id = {row["statement_id"]: row for row in statement_rows}
    page_rows = [row for row in statement_rows if row.get("segment_id") == SEGMENT]
    if len(page_rows) != 28:
        raise SystemExit(f"expected 28 existing p.345 statements, found {len(page_rows)}")

    candidate_headers, candidate_rows = load_csv(CANDIDATES)
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    mention_headers, mention_rows = load_csv(MENTIONS)
    page_mentions = [row for row in mention_rows if row.get("segment_id") == SEGMENT]
    if page_mentions:
        raise SystemExit(f"expected no existing p.345 mentions, found {len(page_mentions)}")

    def refine(
        sid: str,
        *,
        start: int,
        end: int,
        exact: str,
        claim: str,
        predicate: str | None = None,
        subject: str | None = None,
        obj: str | None = None,
        relation: bool | None = None,
        speaker: str = "Haskell",
        layer: str = "authorial narrative",
        qualification: str = "",
        mentioned: list[str] | None = None,
        relation_note: str | None = None,
        extra: dict | None = None,
    ) -> None:
        row = statement_by_id[sid]
        row["original_quote"] = q(start, end, exact)
        if predicate is not None:
            row["predicate"] = predicate
        if subject is not None or "subject_candidate_id" in row:
            row["subject_candidate_id"] = subject
        if obj is not None or "object_candidate_id" in row:
            row["object_candidate_id"] = obj
        qualifiers = row.setdefault("qualifiers", {})
        qualifiers.update({
            "source_line_start": start,
            "source_line_end": end,
            "printed_page": 345,
            "pdf_physical_page": 18,
            "claim": claim,
            "speaker": speaker,
            "text_layer": layer,
            "qualification": qualification,
        })
        if relation is not None:
            qualifiers["relation_candidate"] = relation
            if relation_note:
                qualifiers["relation_candidate_note"] = relation_note
            elif "relation_candidate_note" in qualifiers:
                del qualifiers["relation_candidate_note"]
        if mentioned is not None:
            qualifiers["mentioned_candidate_ids"] = mentioned
        if extra:
            qualifiers.update(extra)

    # Complete the binary S2 classification of all nine previously unclassified rows,
    # narrow existing quotes to their actual evidentiary spans, and correct composites.
    refine("st-chp13-p345-zanetti-1752-quote-continuation", start=162, end=162,
           exact="or three times before being ready to spend it on that sort of thing...",
           claim="The 1752 letter quote from p.344 continues: the few interested patrons turned each zecchino two or three times before spending it on art.",
           relation=True, mentioned=["cand-2838", "cand-3461"],
           qualification="This line closes the sentence begun on p.344. The quote describes a reported attitude, not measured economic behavior.",
           relation_note="The reported statement has a source-defined collective subject and an expressed relation to spending on art; it is retained as a book claim, not an independently measured pattern.")
    refine("st-chp13-p345-haskell-qualifies-italian-situation", start=162, end=162,
           exact="The situation was Venetian rather than Italian",
           claim="Haskell qualifies the preceding quotation as describing the Venetian situation rather than Italy generally.",
           relation=False, mentioned=["cand-2838", "cand-2719", "cand-3461"],
           qualification="This is Haskell's geographic qualification, not a correction to Zanetti's quoted wording.")
    refine("st-chp13-p345-zanetti-death-age", start=162, end=162,
           exact="when Zanetti died in 1767 at the age of 89",
           claim="Haskell states that A. M. Zanetti died in 1767 at the reported age of 89.",
           predicate="died_in_year_at_reported_age", subject="cand-2838", obj=None,
           relation=False, mentioned=["cand-2838"],
           qualification="The reported age is retained as Haskell gives it; no external verification is claimed.")
    refine("st-chp13-p345-younger-zanetti-cousin", start=163, end=163,
           exact="his identically named younger cousin",
           claim="Haskell identifies A. M. Zanetti the Younger as the elder Zanetti's identically named younger cousin.",
           relation=True, mentioned=["cand-2854", "cand-2838"],
           qualification="Kinship and shared name are reported by Haskell; S3 identity alignment remains pending.",
           relation_note="The passage directly states a kinship relation between the two named people.")
    refine("st-chp13-p345-zanettis-collaborated-on-two-books", start=163, end=163,
           exact="he had collaborated on his two main books",
           claim="Haskell says the two cousins collaborated on their two main books.",
           relation=True, mentioned=["cand-2854", "cand-2838"],
           qualification="The passage does not identify which two books in this sentence; no titles are inferred.",
           relation_note="The source explicitly reports collaboration between the two cousins, without naming the titles here.")
    refine("st-chp13-p345-younger-zanetti-critical-role", start=163, end=163,
           exact="an extremely perceptive critic rather than a patron or connoisseur",
           claim="Haskell characterizes the younger Zanetti as an extremely perceptive critic rather than a patron or connoisseur.",
           relation=False, mentioned=["cand-2854"],
           qualification="Authorial evaluation; it is not a universal assessment of the person's activities.")
    refine("st-chp13-p345-varie-pitture-1760", start=163, end=164,
           exact="which he published as\nVaríe Pitture a Fresco in 1760",
           claim="The younger Zanetti published his copies after classic artists as Varie Pitture a Fresco in 1760.",
           relation=True, mentioned=["cand-10117", "cand-2854"],
           qualification="S0 OCR reads Varíe; the p.345 print reads Varie. Individual source artists and copies are not identified.",
           relation_note="The source identifies the 1760 publication and its publisher; the album's author alignment remains for S3.")
    refine("st-chp13-p345-ricche-miniere-edited-1733", start=164, end=164,
           exact="revision of Boschini’s Ricche Miniere edited in 1733",
           claim="Haskell reports the younger Zanetti's revision/editing of Boschini's Ricche Miniere in 1733.",
           relation=True, mentioned=["cand-10118", "cand-2854", "cand-0413"],
           qualification="The title and date are retained as Haskell gives them; no edition was independently consulted.",
           relation_note="The source directly attributes the 1733 revision/editing to the younger Zanetti.")
    refine("st-chp13-p345-della-pittura-veneziana-1771", start=164, end=164,
           exact="his own Della Pittura Veneziana of 1771",
           claim="Haskell names Della Pittura Veneziana (1771) as the younger Zanetti's own work.",
           relation=True, mentioned=["cand-9837", "cand-2854"],
           qualification="The archive candidate is reused from the p.329 bibliographic mention; source identity remains for S3.",
           relation_note="The passage attributes the 1771 work to the younger Zanetti.")
    refine("st-chp13-p345-younger-zanetti-limited-contemporary-role", start=164, end=164,
           exact="he played little part in contemporary artistic Use",
           claim="Haskell says the younger Zanetti played little part in contemporary artistic life.",
           relation=False, mentioned=["cand-2854"],
           qualification="S0 OCR reads 'Use'; the p.345 print reads 'life'. This is Haskell's authorial assessment, not an independently established measure.",
           extra={"ocr_corrections":[{"source_line":164,"ocr":"Use","print":"life","basis":"CHP-13.pdf physical page 18."}]})
    refine("st-chp13-p345-younger-zanetti-prevent-export", start=164, end=164,
           exact="he was made responsible for preventing the export of the great masterpieces of the past",
           claim="Haskell says the younger Zanetti was made responsible for preventing export of great masterpieces of the past.",
           predicate="made_responsible_for_preventing_export_of", subject="cand-2854", obj="cand-12175",
           relation=True, mentioned=["cand-2854", "cand-12175"],
           qualification="The appointing authority, office, and individual works are not named.",
           relation_note="The passage directly assigns a protective responsibility from the person to a source-defined group of works; the responsible office and works remain unidentified.")
    refine("st-chp13-p345-monaco-1743-collection", start=165, end=165,
           exact="in 1743 published a collection of fifty-five prints",
           claim="Pietro Monaco published a collection of fifty-five prints in 1743.",
           relation=True, mentioned=["cand-10115", "cand-1682"],
           qualification="The publication title is not supplied for the 1743 collection; do not equate it with a later edition without further evidence.",
           relation_note="The source directly identifies Monaco as publisher of the 1743 print collection.")
    refine("st-chp13-p345-monaco-1763-1779-editions", start=165, end=165,
           exact="in 1779, posthumously published by Viero",
           claim="Haskell says the 1779 later edition was published posthumously by Viero.",
           relation=True, mentioned=["cand-10116", "cand-2773"],
           qualification="The printed note gives the title Raccolta di centododici stampe but no edition year; its mapping to the 1763 or 1779 edition remains unresolved.",
           relation_note="The source directly identifies Viero as publisher of the posthumous 1779 edition.")
    refine("st-chp13-p345-monaco-reproduced-work-groups", start=166, end=167,
           exact="Of the contemporary works reproduced a strikingly high proportion belonged to\nMonaco himself",
           claim="Haskell says a strikingly high proportion of contemporary works reproduced in the collection belonged to Monaco.",
           predicate="some_reproduced_works_owned_by", subject="cand-12180", obj="cand-1682",
           relation=True, mentioned=["cand-12180", "cand-1682", "cand-10123", "cand-10124", "cand-10125", "cand-2569", "cand-1950", "cand-2830", "cand-1907", "cand-1727"],
           qualification="Haskell gives no full inventory or proportion; the three named groups below are the examples introduced by the colon.",
           relation_note="This records Haskell's explicitly qualified ownership statement at group level; it does not claim that every reproduced work belonged to Monaco.")
    refine("st-chp13-p345-monaco-collection-advertised-dealer", start=167, end=167,
           exact="he was almost certainly using the plates to advertise his activities as a dealer",
           claim="Haskell says Monaco was almost certainly using the plates to advertise his dealer activity.",
           relation=True, mentioned=["cand-7618", "cand-1682"],
           qualification="Preserve Haskell's 'almost certainly'; this is an authorial interpretation, not a verified statement of Monaco's intent.",
           relation_note="The text explicitly attributes use of the collection's plates to Monaco's dealer activity, while marking the interpretation as highly probable rather than certain.")
    refine("st-chp13-p345-monaco-letter-to-strange-seventeen-pictures", start=167, end=168,
           exact="a letter written in 1763 to\nJohn Strange",
           claim="Haskell says Monaco's dealer activity is documented by a letter he wrote in 1763 to John Strange.",
           predicate="authored_by", subject="cand-10119", obj="cand-1682",
           relation=True, mentioned=["cand-10119", "cand-1682", "cand-2516"],
           qualification="Linked note 2 gives the printed date notation 4 February 1763/4; retain that ambiguity and do not choose a year.",
           relation_note="The passage identifies the letter as Monaco's and names John Strange as recipient; the archive locator remains as reported in the linked note.")
    refine("st-chp13-p345-toni-born-near-modena", start=169, end=169,
           exact="was born near Modena in 1692",
           claim="Haskell says Don Pietro Antonio Toni was born near Modena in 1692.",
           relation=True, mentioned=["cand-2640", "cand-3416"],
           qualification="Retain 'near Modena'; no more precise birthplace is inferred.",
           relation_note="The source directly reports Toni's birthplace and birth year.")
    refine("st-chp13-p345-toni-settled-in-venice", start=169, end=169,
           exact="settled in Venice thirty years later",
           claim="Haskell says Toni settled in Venice thirty years after his birth.",
           relation=True, mentioned=["cand-2640", "cand-2719"],
           qualification="The source gives a relative interval; no arithmetic year is added.",
           relation_note="The passage directly identifies Venice as Toni's settlement location.")
    refine("st-chp13-p345-toni-collector", start=169, end=169,
           exact="he was a keen collector",
           claim="Haskell characterizes Toni as a keen collector.",
           predicate="characterized_as_keen_collector", subject="cand-2640", obj=None,
           relation=False, mentioned=["cand-2640"],
           qualification="This is Haskell's characterization; the passage does not enumerate Toni's collections here.")
    refine("st-chp13-p345-toni-ricci-friendship-and-care", start=169, end=169,
           exact="His closest friend was Sebastiano Ricci",
           claim="Haskell says Sebastiano Ricci was Toni's closest friend.",
           predicate="friend_of", subject="cand-2640", obj="cand-2154",
           relation=True, mentioned=["cand-2640", "cand-2154"],
           qualification="This records Haskell's description of their friendship; care during Ricci's illness is a separate statement.",
           relation_note="The source directly identifies a friendship between the two named people.")
    refine("st-chp13-p345-toni-gambled-on-ricci-behalf", start=169, end=169,
           exact="he would gamble on Ricci’s behalf",
           claim="Haskell says Toni would gamble on Ricci's behalf.",
           relation=True, mentioned=["cand-2640", "cand-2154"],
           qualification="No financial representation or specific gambling event is inferred.",
           relation_note="The passage directly reports Toni acting on Ricci's behalf in gambling.")
    refine("st-chp13-p345-toni-contact-with-pittoni", start=169, end=169,
           exact="Toni was also in close touch with Pittoni",
           claim="Haskell says Toni was in close touch with Pittoni.",
           relation=True, mentioned=["cand-2640", "cand-1950"],
           qualification="The passage gives no further description of this contact.",
           relation_note="The source directly reports a close contact between Toni and Pittoni.")
    refine("st-chp13-p345-toni-adviser-and-patron-to-novelli", start=169, end=169,
           exact="he acted as adviser",
           claim="Haskell says Toni advised the young Pietro Antonio Novelli.",
           predicate="advised", subject="cand-2640", obj="cand-1760",
           relation=True, mentioned=["cand-2640", "cand-1760"],
           qualification="The advisory role is recorded as Haskell describes it; no specific advice is inferred.",
           relation_note="The source directly assigns Toni an advisory role toward Novelli.")
    refine("st-chp13-p345-toni-collections-left-to-novelli-1748", start=170, end=170,
           exact="to whom he left his collections when he died in 1748",
           claim="Haskell says Toni left his collections to Novelli when Toni died in 1748.",
           relation=True, mentioned=["cand-10120", "cand-2640", "cand-1760"],
           qualification="The collections' contents are not specified; their type remains unresolved.",
           relation_note="The passage directly reports a bequest from Toni to Novelli; the contents of the collections remain unspecified.")
    refine("st-chp13-p345-toni-discussions-may-have-shaped-novelli", start=170, end=170,
           exact="may have played their part in bringing out the pedantry that was to be such a feature of that artist’s later years",
           claim="Haskell says Toni's discussions with Novelli and explanations of pictures they visited together may have contributed to Novelli's later pedantry.",
           relation=True, mentioned=["cand-2640", "cand-1760"],
           qualification="The source explicitly marks this as possible; it is not stated as a certain causal relation.",
           relation_note="This is a source-attributed, explicitly modal influence claim; preserve its uncertainty in any downstream review.")

    # Add source-supported, atomic assertions that were absent from the first migration.
    new_candidates = [
        {"candidate_id":"cand-12175","index_entry_id":"","canonical_name":"Great masterpieces of the past whose export A. M. Zanetti the Younger was charged to prevent","index_page_range":"","suggested_type":"work","status":"open","index_source_file":"","sub_entry":"","detail":"A source-defined, unnamed group of past masterworks. Haskell says the younger Zanetti was made responsible for preventing their export; individual works, appointing authority, and office are not named.","exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":f"{SEGMENT}#L164"},
        {"candidate_id":"cand-12176","index_entry_id":"","canonical_name":"Leading artists of Toni's day with whom he had friendships","index_page_range":"","suggested_type":"term","status":"open","index_source_file":"","sub_entry":"","detail":"An unnamed source-defined group described as all the leading artists of Toni's day. Members are not enumerated and are not inferred from nearby names.","exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":f"{SEGMENT}#L169"},
        {"candidate_id":"cand-12177","index_entry_id":"","canonical_name":"Prints amassed by Don Pietro Antonio Toni through his friendships with artists","index_page_range":"","suggested_type":"work","status":"open","index_source_file":"","sub_entry":"","detail":"A number of prints Toni was able to amass through friendships with artists. Titles, authors, and count are not given; relation to the broader collections later left to Novelli is not resolved beyond the passage's context.","exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":f"{SEGMENT}#L169"},
        {"candidate_id":"cand-12178","index_entry_id":"","canonical_name":"Religious pictures in Venetian private collections used as sources for Pietro Monaco's 1743 prints","index_page_range":"","suggested_type":"work","status":"open","index_source_file":"","sub_entry":"","detail":"An unnamed group of religious pictures from mostly Venetian private collections, from which Monaco's 1743 collection's prints were taken. Individual pictures and owners are not identified.","exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":f"{SEGMENT}#L165"},
        {"candidate_id":"cand-12179","index_entry_id":"","canonical_name":"Seventeen selected pictures owned by Pietro Monaco and offered for sale in his letter to John Strange","index_page_range":"","suggested_type":"work","status":"open","index_source_file":"","sub_entry":"","detail":"The group of seventeen pictures described in Monaco's 1763 letter as singolari e scielti, owned by him and offered for sale. No individual titles are supplied.","exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":f"{SEGMENT}#L168"},
        {"candidate_id":"cand-12180","index_entry_id":"","canonical_name":"Contemporary works reproduced in Pietro Monaco's print collection","index_page_range":"","suggested_type":"work","status":"open","index_source_file":"","sub_entry":"","detail":"A source-defined group of contemporary works reproduced in Monaco's print collection. Haskell says a strikingly high proportion belonged to Monaco; the full inventory and exact proportion are not stated.","exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":f"{SEGMENT}#L166"},
    ]
    if any(row["candidate_id"] in candidate_by_id for row in new_candidates):
        raise SystemExit("one or more planned candidate IDs already exist")
    candidate_rows.extend(new_candidates)
    candidate_by_id.update({row["candidate_id"]: row for row in new_candidates})

    def footnote_fields(from_id: str) -> dict:
        source_q = statement_by_id[from_id].get("qualifiers", {})
        return {key: source_q[key] for key in ("footnote_refs", "footnote_note_statement_ids", "footnote_text_pending", "footnote_body_link_status") if key in source_q}

    def add_statement(
        sid: str, *, start: int, end: int, exact: str, claim: str, predicate: str,
        subject: str | None = None, obj: str | None = None, relation: bool,
        mentioned: list[str], qualification: str = "", speaker: str = "Haskell",
        layer: str = "authorial narrative", relation_note: str | None = None,
        footnote_from: str | None = None, extra: dict | None = None,
    ) -> None:
        if sid in statement_by_id:
            raise ValueError(f"statement id already exists: {sid}")
        qualifiers = {
            "source_line_start": start,
            "source_line_end": end,
            "printed_page": 345,
            "pdf_physical_page": 18,
            "claim": claim,
            "speaker": speaker,
            "text_layer": layer,
            "qualification": qualification,
            "relation_candidate": relation,
            "mentioned_candidate_ids": mentioned,
        }
        if relation_note:
            qualifiers["relation_candidate_note"] = relation_note
        if footnote_from:
            qualifiers.update(footnote_fields(footnote_from))
        if extra:
            qualifiers.update(extra)
        row = {
            "statement_id": sid,
            "segment_id": SEGMENT,
            "subject_candidate_id": subject,
            "object_candidate_id": obj,
            "predicate": predicate,
            "qualifiers": qualifiers,
            "original_quote": q(start, end, exact),
            "origin": "book",
            "source_file": SOURCE_FILE,
        }
        statement_rows.append(row)
        statement_by_id[sid] = row

    add_statement("st-chp13-p345-zanetti-words-even-truer", start=162, end=162,
                  exact="his words were even truer", claim="Haskell retrospectively says Zanetti's quoted words were even truer by the time of his death.",
                  predicate="authorial_retrospective_assessment", subject="cand-2838", relation=False,
                  mentioned=["cand-2838"], qualification="This is Haskell's retrospective assessment, not an independently measured change.")
    add_statement("st-chp13-p345-younger-zanetti-copy-scope", start=163, end=163,
                  exact="His own drawings and prints were limited to copies of some of the great classic artists",
                  claim="Haskell says the younger Zanetti's own drawings and prints were limited to copies after some of the great classic artists.",
                  predicate="authorial_assessment_of_copy_based_output", subject="cand-2854", relation=False,
                  mentioned=["cand-2854"], qualification="The source does not identify the individual drawings, prints, or classic artists.")
    add_statement("st-chp13-p345-zanetti-taste-practical-use", start=164, end=164,
                  exact="his taste and scholarship were put to practical use", claim="Haskell says the younger Zanetti's taste and scholarship were put to practical use.",
                  predicate="authorial_assessment_of_practical_use", subject="cand-2854", relation=False,
                  mentioned=["cand-2854"], qualification="This is Haskell's characterization; the next clause separately states the responsibility assigned to Zanetti.")
    add_statement("st-chp13-p345-ricche-miniere-dedication", start=164, end=164,
                  exact="with a friendly dedication to his elder cousin", claim="Haskell says the 1733 Ricche Miniere revision included a friendly dedication to the younger Zanetti's elder cousin.",
                  predicate="dedicated_to", subject="cand-10118", obj="cand-2838", relation=True,
                  mentioned=["cand-10118", "cand-2838"], qualification="The dedication is reported by Haskell; neither the edition nor dedication text was independently consulted.",
                  relation_note="The source explicitly identifies the work and dedication recipient; retain it as a source-reported relation pending S3/source examination.")
    add_statement("st-chp13-p345-monaco-1743-print-count", start=165, end=165,
                  exact="a collection of fifty-five prints", claim="Haskell gives the 1743 Monaco collection as containing fifty-five prints.",
                  predicate="reported_print_count", subject="cand-10115", relation=False,
                  mentioned=["cand-10115"], qualification="Count is reported as printed; the collection was not independently consulted.")
    add_statement("st-chp13-p345-monaco-1743-source-pictures", start=165, end=165,
                  exact="prints taken from religious pictures mostly in Venetian private collections",
                  claim="Haskell says Monaco's 1743 prints were taken from religious pictures, mostly in Venetian private collections.",
                  predicate="taken_from", subject="cand-10115", obj="cand-12178", relation=True,
                  mentioned=["cand-10115", "cand-12178", "cand-2719"], qualification="The individual source pictures and their owners are not identified.",
                  relation_note="The passage explicitly reports the source material for the 1743 prints, while leaving individual pictures and owners unnamed.")
    add_statement("st-chp13-p345-monaco-1763-later-edition", start=165, end=165,
                  exact="Later editions in 1763", claim="Haskell identifies a later edition of Monaco's 1743 collection in 1763.",
                  predicate="later_edition_of", subject="cand-7618", obj="cand-10115", relation=True,
                  mentioned=["cand-7618", "cand-10115"], qualification="The passage names the edition year; the linked footnote's 112-print title is not assigned to this edition.",
                  relation_note="Haskell explicitly calls the 1763 publication a later edition of the collection.", footnote_from="st-chp13-p345-monaco-1763-1779-editions")
    add_statement("st-chp13-p345-monaco-1779-later-edition", start=165, end=165,
                  exact="then in 1779", claim="Haskell identifies a further later edition of Monaco's 1743 collection in 1779.",
                  predicate="later_edition_of", subject="cand-10116", obj="cand-10115", relation=True,
                  mentioned=["cand-10116", "cand-10115"], qualification="The linked footnote's title-to-edition mapping remains unresolved.",
                  relation_note="Haskell explicitly places the 1779 publication after the 1763 edition as part of the same collection's later editions.", footnote_from="st-chp13-p345-monaco-1763-1779-editions")
    add_statement("st-chp13-p345-monaco-plate-count-112", start=165, end=166,
                  exact="brought the number of plates up to\n112?", claim="Haskell says the later editions brought the number of plates up to 112.",
                  predicate="reported_plate_count", subject="cand-10116", relation=False,
                  mentioned=["cand-10116"], qualification="S0 OCR reads '112?'; the p.345 print reads 112 followed by note marker 1. The source does not state which edition first reached this count.",
                  extra={"ocr_corrections":[{"source_line":166,"ocr":"112?","print":"112","basis":"CHP-13.pdf physical page 18."}]},
                  footnote_from="st-chp13-p345-monaco-1763-1779-editions")
    add_statement("st-chp13-p345-monaco-patronage-interpretation", start=167, end=167,
                  exact="Such a collection might well suggest that Monaco was a patron similar to Albrizzi or Zanetti",
                  claim="Haskell says the collection might suggest patronage by Monaco similar to Albrizzi or Zanetti.",
                  predicate="authorial_interpretation_of_possible_patronage", subject="cand-7618", relation=False,
                  mentioned=["cand-7618", "cand-1682", "cand-0025", "cand-2838"],
                  qualification="Haskell immediately contrasts this possible interpretation with his view that Monaco was almost certainly using the plates to advertise dealer activity; neither reading is independently verified.",
                  footnote_from="st-chp13-p345-monaco-reproduced-work-groups")
    add_statement("st-chp13-p345-monaco-tiepolo-works-reproduced", start=167, end=167,
                  exact="eight drawings by Tiepolo", claim="Haskell lists eight Tiepolo drawings among contemporary works reproduced in Monaco's collection.",
                  predicate="reproduces", subject="cand-7618", obj="cand-10123", relation=True,
                  mentioned=["cand-7618", "cand-10123", "cand-2569"], qualification="Individual drawing titles are not supplied.",
                  relation_note="The source explicitly lists this group among works reproduced in the collection.", footnote_from="st-chp13-p345-monaco-reproduced-work-groups")
    add_statement("st-chp13-p345-monaco-pittoni-works-reproduced", start=167, end=167,
                  exact="nine paintings by Pittoni", claim="Haskell lists nine Pittoni paintings among contemporary works reproduced in Monaco's collection.",
                  predicate="reproduces", subject="cand-7618", obj="cand-10124", relation=True,
                  mentioned=["cand-7618", "cand-10124", "cand-1950"], qualification="Individual painting titles are not supplied.",
                  relation_note="The source explicitly lists this group among works reproduced in the collection.", footnote_from="st-chp13-p345-monaco-reproduced-work-groups")
    add_statement("st-chp13-p345-monaco-three-works-reproduced", start=167, end=167,
                  exact="one each by Zais, Piazzetta and Nazari", claim="Haskell lists one painting each by Zais, Piazzetta, and Nazari among contemporary works reproduced in Monaco's collection.",
                  predicate="reproduces", subject="cand-7618", obj="cand-10125", relation=True,
                  mentioned=["cand-7618", "cand-10125", "cand-2830", "cand-1907", "cand-1727"], qualification="The three painting titles are not supplied.",
                  relation_note="The source explicitly lists this group among works reproduced in the collection.", footnote_from="st-chp13-p345-monaco-reproduced-work-groups")
    add_statement("st-chp13-p345-monaco-tiepolo-works-owned", start=166, end=167,
                  exact="a strikingly high proportion belonged to\nMonaco himself: eight drawings by Tiepolo", claim="Haskell's examples of contemporary works in the high-proportion ownership statement include eight Tiepolo drawings that belonged to Monaco.",
                  predicate="owned_by", subject="cand-10123", obj="cand-1682", relation=True,
                  mentioned=["cand-10123", "cand-1682", "cand-2569"], qualification="The colon introduces the following listed work groups as examples of the high proportion; no individual drawing is identified.",
                  relation_note="The printed sentence places the named group after the statement that a strikingly high proportion belonged to Monaco; retain the report at group level.", footnote_from="st-chp13-p345-monaco-reproduced-work-groups")
    add_statement("st-chp13-p345-monaco-pittoni-works-owned", start=166, end=167,
                  exact="a strikingly high proportion belonged to\nMonaco himself: eight drawings by Tiepolo, nine paintings by Pittoni", claim="Haskell's examples of contemporary works in the high-proportion ownership statement include nine Pittoni paintings that belonged to Monaco.",
                  predicate="owned_by", subject="cand-10124", obj="cand-1682", relation=True,
                  mentioned=["cand-10124", "cand-1682", "cand-1950"], qualification="The colon introduces the following listed work groups as examples of the high proportion; no individual painting is identified.",
                  relation_note="The printed sentence places the named group after the statement that a strikingly high proportion belonged to Monaco; retain the report at group level.", footnote_from="st-chp13-p345-monaco-reproduced-work-groups")
    add_statement("st-chp13-p345-monaco-three-works-owned", start=166, end=167,
                  exact="a strikingly high proportion belonged to\nMonaco himself: eight drawings by Tiepolo, nine paintings by Pittoni, and one each by Zais, Piazzetta and Nazari", claim="Haskell's examples of contemporary works in the high-proportion ownership statement include one painting each by Zais, Piazzetta, and Nazari that belonged to Monaco.",
                  predicate="owned_by", subject="cand-10125", obj="cand-1682", relation=True,
                  mentioned=["cand-10125", "cand-1682", "cand-2830", "cand-1907", "cand-1727"], qualification="The colon introduces the following listed work groups as examples of the high proportion; no individual painting is identified.",
                  relation_note="The printed sentence places the named group after the statement that a strikingly high proportion belonged to Monaco; retain the report at group level.", footnote_from="st-chp13-p345-monaco-reproduced-work-groups")
    add_statement("st-chp13-p345-monaco-letter-addressed-to-strange", start=167, end=168,
                  exact="a letter written in 1763 to\nJohn Strange", claim="Monaco's 1763 letter was addressed to John Strange.",
                  predicate="addressed_to", subject="cand-10119", obj="cand-2516", relation=True,
                  mentioned=["cand-10119", "cand-2516"], qualification="Linked note 2 prints the date as 4 February 1763/4; retain the ambiguous year form.",
                  relation_note="The passage directly names John Strange as the letter's recipient.", footnote_from="st-chp13-p345-monaco-letter-to-strange-seventeen-pictures")
    add_statement("st-chp13-p345-monaco-letter-encloses-picture-list", start=168, end=168,
                  exact="enclosing a list of seventeen pictures", claim="Haskell says Monaco's letter enclosed a list of seventeen pictures.",
                  predicate="contains", subject="cand-10119", obj="cand-12179", relation=True,
                  mentioned=["cand-10119", "cand-12179"], qualification="The list and pictures were not independently consulted.",
                  relation_note="The source directly says the letter enclosed a list of the seventeen pictures.", footnote_from="st-chp13-p345-monaco-letter-to-strange-seventeen-pictures")
    add_statement("st-chp13-p345-monaco-pictures-owned", start=168, end=168,
                  exact="which he owned", claim="Haskell says Monaco owned the seventeen pictures listed in his letter.",
                  predicate="owned_by", subject="cand-12179", obj="cand-1682", relation=True,
                  mentioned=["cand-12179", "cand-1682"], qualification="Individual pictures and the extent of ownership are not specified beyond Haskell's wording.",
                  relation_note="The source explicitly says Monaco owned the listed pictures.", footnote_from="st-chp13-p345-monaco-letter-to-strange-seventeen-pictures")
    add_statement("st-chp13-p345-monaco-pictures-offered-for-sale", start=168, end=168,
                  exact="was anxious to sell", claim="Haskell says Monaco was anxious to sell the seventeen pictures listed in his letter.",
                  predicate="offered_for_sale_by", subject="cand-12179", obj="cand-1682", relation=True,
                  mentioned=["cand-12179", "cand-1682"], qualification="No completed sale is stated.",
                  relation_note="The source reports an intention to sell, not a completed transaction.", footnote_from="st-chp13-p345-monaco-letter-to-strange-seventeen-pictures")
    add_statement("st-chp13-p345-toni-financially-short", start=169, end=169,
                  exact="he was desperately short of money", claim="Haskell says Toni was desperately short of money.",
                  predicate="reported_financial_distress", subject="cand-2640", relation=False,
                  mentioned=["cand-2640"], qualification="Retain Haskell's description; no amount, period, or independent financial record is supplied.", footnote_from="st-chp13-p345-toni-born-near-modena")
    add_statement("st-chp13-p345-toni-friendship-with-leading-artists", start=169, end=169,
                  exact="through his friendship with all the leading artists of the day", claim="Haskell says Toni had friendships with all the leading artists of his day.",
                  predicate="friend_of_source_defined_group", subject="cand-2640", obj="cand-12176", relation=True,
                  mentioned=["cand-2640", "cand-12176"], qualification="The artists are not named; do not infer that adjacent artists in the passage are members of this group.",
                  relation_note="The source explicitly asserts friendship with a source-defined group; its members remain unknown.", footnote_from="st-chp13-p345-toni-born-near-modena")
    add_statement("st-chp13-p345-toni-amassed-prints", start=169, end=169,
                  exact="he was able to amass a number of prints", claim="Haskell says Toni was able to amass a number of prints through his friendships with leading artists.",
                  predicate="amassed_prints_through_friendships_with", subject="cand-2640", obj="cand-12177", relation=True,
                  mentioned=["cand-2640", "cand-12176", "cand-12177"], qualification="The prints, their creators, and their count are not identified; the larger collection later left to Novelli is not assumed to consist only of these prints.",
                  relation_note="The passage directly links Toni's amassing of prints to his friendships with an unnamed source-defined group.", footnote_from="st-chp13-p345-toni-born-near-modena",
                  extra={"via_candidate_id":"cand-12176"})
    add_statement("st-chp13-p345-toni-cared-for-ricci", start=169, end=169,
                  exact="whom he cared for during an illness", claim="Haskell says Toni cared for Sebastiano Ricci during an illness.",
                  predicate="cared_for_during_illness", subject="cand-2640", obj="cand-2154", relation=True,
                  mentioned=["cand-2640", "cand-2154"], qualification="The source gives no date or details of Ricci's illness.",
                  relation_note="The passage directly reports care by Toni for Ricci during an illness.", footnote_from="st-chp13-p345-toni-born-near-modena")
    add_statement("st-chp13-p345-ricci-voyeur-characterization", start=169, end=169,
                  exact="the painter was something of a ‘voyeur’ in this respect and preferred to watch others rather than take part himself",
                  claim="Haskell characterizes Ricci as something of a 'voyeur' in gambling and says he preferred watching others rather than participating.",
                  predicate="authorial_characterization_of_gambling_preference", subject="cand-2154", relation=False,
                  mentioned=["cand-2154"], qualification="Retain Haskell's qualified metaphor and context; do not treat 'voyeur' as a diagnosis.", footnote_from="st-chp13-p345-toni-born-near-modena")
    add_statement("st-chp13-p345-toni-patron-of-novelli", start=169, end=169,
                  exact="patron to his special protege the young Pietro Antonio", claim="Haskell says Toni acted as patron to the young Pietro Antonio Novelli.",
                  predicate="patron_of", subject="cand-2640", obj="cand-1760", relation=True,
                  mentioned=["cand-2640", "cand-1760"], qualification="No specific commission or payment is inferred.",
                  relation_note="The source explicitly identifies Toni as Novelli's patron; no specific commission is described.", footnote_from="st-chp13-p345-toni-adviser-and-patron-to-novelli")
    add_statement("st-chp13-p345-toni-learned", start=170, end=170,
                  exact="Toni was a learned man", claim="Haskell characterizes Toni as a learned man.",
                  predicate="characterized_as_learned", subject="cand-2640", relation=False,
                  mentioned=["cand-2640"], qualification="This is Haskell's description, not an independently assessed credential.", footnote_from="st-chp13-p345-toni-discussions-may-have-shaped-novelli")
    add_statement("st-chp13-p345-note3-manuscript-draft-date", start=171, end=171,
                  exact="it was sketched out by 1762", claim="Haskell says internal evidence indicates the manuscript life was sketched out by 1762.",
                  predicate="manuscript_life_drafted_by_year", subject="cand-10221", relation=False,
                  mentioned=["cand-10221"], speaker="Haskell, printed note 3", layer="footnote continuation",
                  qualification="The antecedent is the manuscript life identified in linked note 3 at L251; neither that manuscript nor cited page was independently consulted.",
                  footnote_from="st-chp13-p345-note3-date-continuation")

    # The note continuation's existing row becomes the separate 1790 assertion.
    refine("st-chp13-p345-note3-date-continuation", start=171, end=171,
           exact="This was written in 1790", claim="Haskell says the manuscript life described in p.345 note 3 was written in 1790.",
           predicate="manuscript_life_written_in_year", subject="cand-10221", obj=None,
           relation=False, mentioned=["cand-10221"], speaker="Haskell, printed note 3", layer="footnote continuation",
           qualification="The antecedent of 'This' is the manuscript life identified in linked note 3 at L251; neither the manuscript nor the cited page was independently consulted.")

    # The new group candidates are source mentions as well as statement endpoints.
    mention_specs = [
        ("cand-2838", "Zanetti", "The elder A. M. Zanetti named in the surrounding paragraph."),
        ("cand-2838", "elder cousin", "The younger Zanetti's elder cousin; identity follows the paragraph's explicit kinship context."),
        ("cand-2854", "identically named younger cousin", "The younger A. M. Zanetti."),
        ("cand-2854", "Antonio Maria the Younger", "Full source form for the younger A. M. Zanetti."),
        ("cand-2854", "His own drawings and prints", "Pronoun refers to A. M. Zanetti the Younger."),
        ("cand-10117", "Varíe Pitture a Fresco", "S0 OCR form; the printed reading is Varie Pitture a Fresco."),
        ("cand-0413", "Boschini’s", "Author of Ricche Miniere as named in the source."),
        ("cand-10118", "Ricche Miniere", "The work revised by the younger Zanetti."),
        ("cand-9837", "Della Pittura Veneziana", "The 1771 work named by Haskell."),
        ("cand-12175", "great masterpieces of the past", "Source-defined group; individual works are not identified."),
        ("cand-1682", "Pietro Monaco", "Pietro Monaco named as engraver and publisher."),
        ("cand-1682", "Monaco himself", "Pietro Monaco named in the ownership statement."),
        ("cand-1682", "Monaco was a patron", "Pietro Monaco in Haskell's possible patronage interpretation."),
        ("cand-10115", "a collection of fifty-five prints", "The 1743 print collection."),
        ("cand-12178", "religious pictures mostly in Venetian private collections", "Unnamed source pictures for Monaco's 1743 prints."),
        ("cand-2719", "Venetian", "Adjectival place reference to Venice."),
        ("cand-3461", "Italian", "Geographic scope named in Zanetti's quoted wording."),
        ("cand-7618", "Later editions in 1763", "The 1763 later edition candidate; title mapping remains pending."),
        ("cand-10116", "then in 1779", "The 1779 posthumous edition."),
        ("cand-2773", "Viero", "Posthumous publisher named by Haskell."),
        ("cand-10116", "the number of plates up to\n112?", "S0 OCR ends the number with a question mark; p.345 print reads 112 plus footnote marker."),
        ("cand-12180", "the contemporary works reproduced", "Source-defined group of works represented in Monaco's collection."),
        ("cand-10123", "eight drawings by Tiepolo", "Group of eight reproduced drawings."),
        ("cand-2569", "Tiepolo", "Artist named for the eight drawings."),
        ("cand-10124", "nine paintings by Pittoni", "Group of nine reproduced paintings."),
        ("cand-1950", "Pittoni", "Artist named for the nine paintings and later Toni contact."),
        ("cand-10125", "one each by Zais, Piazzetta and Nazari", "Group of three reproduced paintings."),
        ("cand-2830", "Zais", "Artist named for one painting."),
        ("cand-1907", "Piazzetta", "Artist named for one painting."),
        ("cand-1727", "Nazari", "Artist named for one painting."),
        ("cand-0025", "Albrizzi", "Patron used in Haskell's possible patronage comparison."),
        ("cand-2838", "Zanetti", "The elder A. M. Zanetti used in Haskell's possible patronage comparison."),
        ("cand-7618", "the plates", "The plates used in Haskell's dealer-advertising interpretation."),
        ("cand-10119", "a letter written in 1763", "The letter Haskell uses as evidence of dealer activity."),
        ("cand-2516", "John Strange", "Recipient of Monaco's letter."),
        ("cand-12179", "seventeen pictures", "Unnamed group listed, owned, and offered for sale."),
        ("cand-2640", "Don Pietro Antonio Toni", "Toni introduced on p.345."),
        ("cand-3416", "near Modena", "Toni's reported birthplace, stated at regional precision."),
        ("cand-2719", "Venice", "Toni's settlement location."),
        ("cand-12176", "all the leading artists of the day", "Unnamed source-defined artist group; members are not inferred."),
        ("cand-12177", "a number of prints", "Unnamed prints Toni amassed through his friendships."),
        ("cand-2154", "Sebastiano Ricci", "Toni's closest friend and painter in the following account."),
        ("cand-2154", "Ricci’s", "Ricci's works in the gift account."),
        ("cand-2154", "Ricci", "Ricci named in the gambling account."),
        ("cand-10121", "engravings after his works", "Group of engravings Ricci gave Toni; 'his' refers to Ricci."),
        ("cand-10122", "a modello of an Adoration of the Magi", "The modello Ricci gave Toni."),
        ("cand-2154", "the painter", "Anaphoric reference to Sebastiano Ricci."),
        ("cand-1950", "Pittoni", "Toni's reported close contact with the artist."),
        ("cand-1760", "the young Pietro Antonio\nNovelli", "Full name across a page line break; identified as Novelli."),
        ("cand-10120", "his collections", "Unspecified collections Toni left to Novelli."),
        ("cand-1760", "Novelli", "Recipient of Toni's collections and discussion partner."),
        ("cand-1760", "that artist’s later years", "Novelli is the artist referred to by this phrase."),
        ("cand-2640", "He was also a dealer", "The sentence continues onto p.346 and refers to Toni."),
        ("cand-10221", "This", "Demonstrative referring to the manuscript life cited in linked note 3 at L251."),
    ]
    mention_additions: list[dict] = []
    duplicate_spans: set[tuple[str, int, int]] = set()
    for candidate_id, surface, note in mention_specs:
        if candidate_id not in candidate_by_id:
            raise ValueError(f"mention references missing candidate: {candidate_id}")
        at = 0
        found = []
        while True:
            index = segment_text.find(surface, at)
            if index < 0:
                break
            found.append(index)
            at = index + 1
        if not found:
            raise ValueError(f"mention surface not found in exact segment text: {surface!r} ({candidate_id})")
        for index in found:
            key = (candidate_id, index, index + len(surface))
            if key in duplicate_spans:
                continue
            duplicate_spans.add(key)
            mention_additions.append({
                "mention_id": "", "segment_id": SEGMENT, "candidate_id": candidate_id,
                "surface_form": surface, "start_char": str(index), "end_char": str(index + len(surface)), "note": note,
            })
    # Avoid duplicate nested mentions for the same candidate while preserving
    # cross-candidate spans that anchor both an entity and a source-defined group.
    mention_additions.sort(key=lambda r: (int(r["start_char"]), -int(r["end_char"]), r["candidate_id"]))
    filtered_mentions: list[dict] = []
    for row in mention_additions:
        start, end = int(row["start_char"]), int(row["end_char"])
        if any(
            prior["candidate_id"] == row["candidate_id"]
            and int(prior["start_char"]) <= start
            and end <= int(prior["end_char"])
            for prior in filtered_mentions
        ):
            continue
        filtered_mentions.append(row)
    mention_additions = filtered_mentions
    existing_ids = {row["statement_id"] for row in load_jsonl(STATEMENTS)}
    planned_ids = [row["statement_id"] for row in statement_rows]
    if len(planned_ids) != len(set(planned_ids)):
        raise SystemExit("duplicate statement ids in proposed table")
    for index, row in enumerate(mention_additions, 1):
        row["mention_id"] = f"m-s2-ch13-p345-{index:03d}"
    if len({row["candidate_id"] for row in candidate_rows}) != len(candidate_rows):
        raise SystemExit("duplicate candidate IDs in proposed table")
    existing_mention_ids = {row["mention_id"] for row in mention_rows}
    if any(row["mention_id"] in existing_mention_ids for row in mention_additions):
        raise SystemExit("mention ID collision")
    mention_rows.extend(mention_additions)

    # Keep the bidirectional note/body pointers synchronized when source statements are split.
    linked_note_updates = {
        "st-chp13-p345-notes-note1-monaco-112-title": [
            "st-chp13-p345-monaco-1763-1779-editions", "st-chp13-p345-monaco-1763-later-edition",
            "st-chp13-p345-monaco-1779-later-edition", "st-chp13-p345-monaco-plate-count-112",
            "st-chp13-p345-monaco-reproduced-work-groups", "st-chp13-p345-monaco-tiepolo-works-reproduced",
            "st-chp13-p345-monaco-pittoni-works-reproduced", "st-chp13-p345-monaco-three-works-reproduced",
            "st-chp13-p345-monaco-tiepolo-works-owned", "st-chp13-p345-monaco-pittoni-works-owned",
            "st-chp13-p345-monaco-three-works-owned",
        ],
        "st-chp13-p345-notes-note2-monaco-strange-letter-locator": [
            "st-chp13-p345-monaco-letter-to-strange-seventeen-pictures",
            "st-chp13-p345-monaco-letter-addressed-to-strange",
            "st-chp13-p345-monaco-letter-encloses-picture-list",
            "st-chp13-p345-monaco-pictures-owned", "st-chp13-p345-monaco-pictures-offered-for-sale",
        ],
        "st-chp13-p345-notes-note3-moschini-novelli-manuscript-provenance": [
            "st-chp13-p345-toni-financially-short", "st-chp13-p345-toni-friendship-with-leading-artists",
            "st-chp13-p345-toni-amassed-prints", "st-chp13-p345-toni-cared-for-ricci",
            "st-chp13-p345-ricci-voyeur-characterization", "st-chp13-p345-toni-patron-of-novelli",
            "st-chp13-p345-toni-learned", "st-chp13-p345-note3-date-continuation",
            "st-chp13-p345-note3-manuscript-draft-date",
        ],
    }
    for sid, linked in linked_note_updates.items():
        if sid not in statement_by_id:
            raise ValueError(f"missing linked note statement {sid}")
        qualifiers = statement_by_id[sid].setdefault("qualifiers", {})
        current = qualifiers.setdefault("linked_body_statement_ids", [])
        for linked_id in linked:
            if linked_id not in statement_by_id:
                raise ValueError(f"linked statement is missing: {linked_id}")
            if linked_id not in current:
                current.append(linked_id)

    # A final local integrity pass checks exact quotes, endpoints, and mention spans.
    for row in statement_rows:
        if row.get("segment_id") != SEGMENT:
            continue
        start = row["qualifiers"]["source_line_start"]
        end = row["qualifiers"]["source_line_end"]
        q(start, end, row["original_quote"])
        for candidate_id in [row.get("subject_candidate_id"), row.get("object_candidate_id")]:
            if candidate_id and candidate_id not in candidate_by_id:
                raise ValueError(f"statement endpoint missing candidate: {row['statement_id']} -> {candidate_id}")
        if "relation_candidate" not in row["qualifiers"]:
            raise ValueError(f"unclassified statement remains: {row['statement_id']}")
    for row in mention_additions:
        start, end = int(row["start_char"]), int(row["end_char"])
        if segment_text[start:end] != row["surface_form"]:
            raise ValueError(f"mention span mismatch: {row['mention_id']}")

    print(f"p345 statements: {len(page_rows)} -> {sum(1 for row in statement_rows if row.get('segment_id') == SEGMENT)} (+{sum(1 for row in statement_rows if row.get('segment_id') == SEGMENT) - len(page_rows)})")
    print(f"new candidates: {len(new_candidates)}; p345 mentions: {len(mention_additions)}")
    print(f"relation_candidate true/false/unclassified: " + ", ".join(
        f"{value}={sum(1 for row in statement_rows if row.get('segment_id') == SEGMENT and row['qualifiers'].get('relation_candidate') is value)}"
        for value in (True, False, None)
    ))
    print("validated exact quote anchors, candidate endpoints, footnote links, and mention spans")
    if not args.apply:
        print("DRY-RUN only; no tables changed")
        return

    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"recovery copy already exists: {backup.name}")
        shutil.copy2(path, backup)
    STATEMENTS.write_bytes(dump_jsonl(statement_rows))
    CANDIDATES.write_bytes(dump_csv(candidate_headers, candidate_rows))
    MENTIONS.write_bytes(dump_csv(mention_headers, mention_rows))
    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        print(f"wrote {path.relative_to(ROOT)} sha256={sha(path)}")
    print(f"recovery copies created with suffix {BACKUP_SUFFIX}")


if __name__ == "__main__":
    main()
