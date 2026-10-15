#!/usr/bin/env python3
"""Guarded S2 semantic review of chapter 5 section IV notes, lines 39-54."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "05_CHP-5_sec_iv.md"
SEGMENT_ID = "chp-5:05_CHP-5_sec_iv:l39-54"
SOURCE_SEGMENT_SHA = "14971fe6844ce14c0a0230cc4caea7044837392aab9fcac88c5fd5eeced26ac3"
ASSET_SHA = "805df7b2bdc296cf987069cb0cea829bc07ec8932e28b075e9575f0c2ac67c4f"
EXPECTED_HASHES = {
    "book-statements.jsonl": "e6d943ab14d695c3b38c6f1394f621a4da463ee2b264a892a367354486a4bacc",
    "entity-candidates.csv": "c92e62dff790f77d8caf30b8449956bac5007529b1e4738b126d56fbc3231143",
    "mentions.csv": "7e260c8efb413e3c3420295f6e853857994c1191f14e3b1088f7a2c27775a26d",
    "s2-coverage.csv": "f2e914ad5afbcd70d67ae9572d528be69db3855ef075d70962b66cae9fe3307b",
}
BACKUP_SUFFIX = ".bak-s2-chp5-seciv-notes-l39-54-20261013"
MISSING = object()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


def read_csv(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the reviewed changes")
    args = parser.parse_args()

    for name, expected in EXPECTED_HASHES.items():
        actual = digest(TABLES / name)
        if actual != expected:
            raise SystemExit(f"Refusing: {name} changed; current SHA-256 is {actual}")

    segment = next(
        (row for row in read_jsonl(TABLES / "segments.jsonl") if row.get("segment_id") == SEGMENT_ID),
        None,
    )
    if not segment or segment.get("sha256") != SOURCE_SEGMENT_SHA:
        raise SystemExit("Refusing: S0 segment fingerprint changed or is missing")
    if segment.get("asset_sha256") != ASSET_SHA:
        raise SystemExit("Refusing: source asset fingerprint changed")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(source_lines[38:54])

    def quote_between(start: str, end: str) -> str:
        a = segment_text.index(start)
        b = segment_text.index(end, a) + len(end)
        return segment_text[a:b]

    statement_path = TABLES / "book-statements.jsonl"
    candidate_path = TABLES / "entity-candidates.csv"
    mention_path = TABLES / "mentions.csv"
    coverage_path = TABLES / "s2-coverage.csv"
    statements = read_jsonl(statement_path)
    candidate_fields, candidates = read_csv(candidate_path)
    mention_fields, mentions = read_csv(mention_path)
    coverage_fields, coverage = read_csv(coverage_path)
    all_rows = {row["statement_id"]: row for row in statements}
    target = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    unresolved_ids = {
        "st-chp5-seciv-note-l41-p143-marker2",
        "st-chp5-seciv-note-l42-p143-marker3",
        "st-chp5-seciv-note-l43-p143-marker4",
        "st-chp5-seciv-note-l44-p143-marker5",
        "st-chp5-seciv-note-l47-p144-marker2",
        "st-chp5-seciv-note-l47-p144-marker3",
        "st-chp5-seciv-note-l52-p145-marker2",
        "st-chp5-seciv-note-l54-p145-marker4",
    }
    if len(target) != 26 or not unresolved_ids <= {row["statement_id"] for row in target}:
        raise SystemExit(f"Refusing: expected 26 note statements and the 8 identified unresolved rows; found {len(target)}")
    unresolved = {row["statement_id"] for row in target if row.get("qualifiers", {}).get("relation_candidate") not in (True, False)}
    if unresolved != unresolved_ids:
        raise SystemExit(f"Refusing: unresolved note rows changed: {sorted(unresolved)}")
    for row in target:
        if row.get("original_quote") and row["original_quote"] not in segment_text:
            raise SystemExit(f"Refusing: existing quote outside S0 segment: {row['statement_id']}")

    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    if "cand-11954" in candidate_by_id:
        raise SystemExit("Refusing: planned archive candidate cand-11954 already exists")
    numeric_ids = [int(row["candidate_id"].split("-")[1]) for row in candidates]
    if max(numeric_ids) != 11953:
        raise SystemExit(f"Refusing: candidate sequence changed; current max is {max(numeric_ids)}")

    candidate = {
        "candidate_id": "cand-11954",
        "index_entry_id": "",
        "canonical_name": "Letter from Salvator Rosa to G. B. Ricciardi, 27 May 1651",
        "index_page_range": "",
        "suggested_type": "archive",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell's p.143 footnote reports that Rosa referred to himself as a Stoic in a letter to Ricciardi dated 27 May 1651 and cites Limentani (1950), p.79. The letter and cited page were not independently examined.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L41",
    }
    candidates.append(candidate)
    candidate_by_id[candidate["candidate_id"]] = candidate

    def configure(
        statement_id: str,
        *,
        relation: bool,
        relation_note: str,
        claim: str | object = MISSING,
        subject: str | None | object = MISSING,
        obj: str | None | object = MISSING,
        predicate: str | None = None,
        original_quote: str | None = None,
        updates: dict | None = None,
    ) -> None:
        row = all_rows[statement_id]
        q = row.setdefault("qualifiers", {})
        q["relation_candidate"] = relation
        q["relation_candidate_note"] = relation_note
        if claim is not MISSING:
            q["claim"] = claim
        if subject is not MISSING:
            row["subject_candidate_id"] = subject
        if obj is not MISSING:
            row["object_candidate_id"] = obj
        if predicate:
            row["predicate"] = predicate
        if original_quote is not None:
            row["original_quote"] = original_quote
        if updates:
            q.update(updates)

    p143_note2_id = "st-chp5-seciv-note-l41-p143-marker2"
    configure(
        p143_note2_id,
        relation=True,
        relation_note="This records Haskell's citation of Baldinucci, volume VI, page 581; the separate Limentani citation and letter statement are split into their own rows.",
        subject="cand-2962",
        obj="cand-4846",
        predicate="cites",
        original_quote=quote_between("2 Baldinucci, VI, 1728, p. 581.", "2 Baldinucci, VI, 1728, p. 581."),
        claim="Haskell cites Baldinucci, volume VI (1728), page 581, in note 2 on p.143.",
        updates={
            "citation_candidate_id": "cand-4846",
            "page": 581,
            "volume": "VI",
            "footnote_marker": 2,
            "footnote_printed_page": "143",
            "linked_body_statement_ids": ["st-chp5-p143-rosa-small-landscape-complaint"],
            "citation_body_statement_ids": ["st-chp5-p143-rosa-small-landscape-complaint"],
        },
    )
    configure(
        "st-chp5-seciv-note-l42-p143-marker3",
        relation=True,
        relation_note="This records Haskell's citation of Baldinucci for the adjacent p.143 price anecdote; the citation does not independently validate the account.",
        subject="cand-2962",
        obj="cand-4846",
        predicate="cites",
        claim="Haskell cites Baldinucci, volume VI (1728), page 581, in note 3 on p.143.",
        updates={
            "citation_candidate_id": "cand-4846",
            "page": 581,
            "volume": "VI",
            "linked_body_statement_ids": ["st-chp5-p143-rosa-million-for-large-picture"],
            "citation_body_statement_ids": ["st-chp5-p143-rosa-million-for-large-picture"],
        },
    )
    configure(
        "st-chp5-seciv-note-l43-p143-marker4",
        relation=True,
        relation_note="This records Haskell's citation of de Rinaldis for the adjacent letter passage; the note supplies a year but no letter recipient or exact date.",
        subject="cand-2962",
        obj="cand-6205",
        predicate="cites",
        claim="Haskell cites de Rinaldis (1939), page 191, for the adjacent Rosa letter passage dated to 1666.",
        updates={
            "citation_candidate_id": "cand-6205",
            "page": 191,
            "date": "1666",
            "linked_body_statement_ids": ["st-chp5-p143-rosa-wanted-landscapes-forgotten"],
            "citation_body_statement_ids": ["st-chp5-p143-rosa-wanted-landscapes-forgotten"],
        },
    )
    configure(
        "st-chp5-seciv-note-l44-p143-marker5",
        relation=True,
        relation_note="This records the source citation to A. Venturi for the Duke of Modena request passage; it does not turn the requested pictures into commissions.",
        subject="cand-2962",
        obj="cand-4354",
        predicate="cites",
        claim="Haskell cites A. Venturi, pages 264-265, in note 5 on p.143.",
        updates={
            "citation_candidate_id": "cand-4354",
            "page_range": "264-265",
            "linked_body_statement_ids": [
                "st-chp5-p143-duke-of-modena-requested-pictures",
                "st-chp5-p143-duke-request-battles-by-rosa",
                "st-chp5-p143-duke-request-battles-by-borgognone",
                "st-chp5-p143-duke-request-flower-pictures-by-mario-de-fiori",
                "st-chp5-p143-duke-request-flower-pictures-by-cerquozzi",
                "st-chp5-p143-duke-request-landscapes-by-gaspard-poussin",
                "st-chp5-p143-duke-request-fables-by-pier-francesco-mola",
            ],
            "citation_body_statement_ids": [
                "st-chp5-p143-duke-of-modena-requested-pictures",
                "st-chp5-p143-duke-request-battles-by-rosa",
                "st-chp5-p143-duke-request-battles-by-borgognone",
                "st-chp5-p143-duke-request-flower-pictures-by-mario-de-fiori",
                "st-chp5-p143-duke-request-flower-pictures-by-cerquozzi",
                "st-chp5-p143-duke-request-landscapes-by-gaspard-poussin",
                "st-chp5-p143-duke-request-fables-by-pier-francesco-mola",
            ],
        },
    )
    configure(
        "st-chp5-seciv-note-l47-p144-marker2",
        relation=True,
        relation_note="This is Haskell's citation of Baldinucci, separated from the note's distinct reference to De' Rossi's collection in Bellori's Nota de Musei.",
        subject="cand-2962",
        obj="cand-4846",
        predicate="cites",
        original_quote=quote_between("2 Baldinucci, VI, 1728, p. 570.", "2 Baldinucci, VI, 1728, p. 570."),
        claim="Haskell cites Baldinucci, volume VI (1728), page 570, in note 2 on p.144.",
        updates={
            "citation_candidate_id": "cand-4846",
            "page": 570,
            "volume": "VI",
            "footnote_marker": 2,
            "linked_body_statement_ids": ["st-chp5-p144-de-rossi-private-museum-of-rosa-works"],
            "citation_body_statement_ids": ["st-chp5-p144-de-rossi-private-museum-of-rosa-works"],
        },
    )
    configure(
        "st-chp5-seciv-note-l47-p144-marker3",
        relation=True,
        relation_note="Haskell reports the location of the unnamed altarpiece group named in the immediately preceding p.144 sentence; the cited page and present location were not independently checked here.",
        subject="cand-11485",
        obj="cand-5522",
        predicate="reported_paintings_at_location",
        original_quote=quote_between("3 ibid. p. 569.", "The paintings are now at Chantilly..."),
        claim="Haskell says the paintings associated with Rosa's preceding p.144 chapel passage are now at Chantilly and cites Baldinucci, volume VI, page 569.",
        updates={
            "citation_candidate_id": "cand-4846",
            "page": 569,
            "volume": "VI",
            "work_group_candidate_id": "cand-11485",
            "location_candidate_id": "cand-5522",
            "linked_body_statement_ids": ["st-chp5-p144-rosa-painted-altarpieces-for-family-chapel"],
            "citation_body_statement_ids": ["st-chp5-p144-rosa-painted-altarpieces-for-family-chapel"],
            "qualification": "The note is anchored to the preceding altarpiece sentence. The individual paintings and their present collection history are not specified in this note.",
        },
    )
    configure(
        "st-chp5-seciv-note-l52-p145-marker2",
        relation=False,
        relation_note="This is Haskell's internal navigation to an earlier chapter, not a relationship between historical entities.",
        subject=None,
        obj=None,
        updates={"mentioned_candidate_ids": ["cand-2236"]},
    )
    configure(
        "st-chp5-seciv-note-l54-p145-marker4",
        relation=True,
        relation_note="This records Haskell's citation of De Dominici for the nested quotation; the reported metaphor remains about Giordano, not Rosa.",
        subject="cand-2962",
        obj="cand-4835",
        predicate="cites",
        claim="Haskell cites De Dominici, volume IV, page 186, for the three-brush account about Luca Giordano.",
        updates={
            "citation_candidate_id": "cand-4835",
            "page": 186,
            "volume": "IV",
            "nested_quote_subject_candidate_id": "cand-1172",
            "analogy_subject_candidate_id": "cand-2236",
            "linked_body_statement_ids": ["st-chp5-p145-giordano-three-brushes-audience-metaphor"],
            "citation_body_statement_ids": ["st-chp5-p145-giordano-three-brushes-audience-metaphor"],
        },
    )

    added: list[dict] = []

    def add_statement(
        statement_id: str,
        *,
        subject: str | None,
        obj: str | None,
        predicate: str,
        quote: str,
        claim: str,
        relation_note: str,
        line_number: int,
        mentioned: tuple[str, ...] = (),
        relation: bool = True,
        speaker: str = "Haskell",
        text_layer: str = "authorial footnote statement",
        qualification: str = "",
        extras: dict | None = None,
    ) -> None:
        if statement_id in all_rows:
            raise SystemExit(f"Refusing: new statement ID exists: {statement_id}")
        if not quote or quote not in segment_text:
            raise SystemExit(f"Refusing: new quote is not an exact S0 substring: {statement_id}")
        q = {
            "source_line_start": line_number,
            "source_line_end": line_number,
            "printed_page": "143" if line_number == 41 else "144" if line_number == 47 else "145",
            "pdf_physical_page": 28 if line_number == 41 else 29 if line_number == 47 else 30,
            "claim": claim,
            "speaker": speaker,
            "text_layer": text_layer,
            "qualification": qualification,
            "relation_candidate": relation,
            "relation_candidate_note": relation_note,
            "mentioned_candidate_ids": list(mentioned),
            "footnote_segment": SEGMENT_ID,
        }
        if extras:
            q.update(extras)
        row = {
            "statement_id": statement_id,
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": subject,
            "object_candidate_id": obj,
            "predicate": predicate,
            "qualifiers": q,
            "original_quote": quote,
            "origin": "book",
            "source_file": "02-sources/02-Markdown/05_CHP-5_sec_iv.md",
        }
        added.append(row)
        all_rows[statement_id] = row

    limentani_id = "st-chp5-seciv-note-l41-p143-cites-limentani-p79"
    stoic_claim_id = "st-chp5-seciv-note-l41-p143-rosa-described-himself-as-stoic"
    authored_id = "st-chp5-l41-letter-authored-by"
    addressed_id = "st-chp5-l41-letter-addressed-to"
    add_statement(
        limentani_id,
        subject="cand-2962", obj="cand-6239", predicate="cites",
        quote=quote_between("Limentani, 1950, p. 79.", "Limentani, 1950, p. 79."),
        claim="Haskell cites Limentani (1950), page 79, in the p.143 note reporting Rosa's self-description as a Stoic.",
        relation_note="This records the separate Limentani citation in the compound p.143 footnote; the cited page was not independently consulted.",
        line_number=41, mentioned=("cand-2236", "cand-2187", "cand-6239", "cand-11954"),
        qualification="The letter and cited edition were not independently examined.",
        extras={
            "footnote_marker": 2,
            "citation_candidate_id": "cand-6239",
            "publication_candidate_id": "cand-6239",
            "page": 79,
            "letter_report_statement_id": stoic_claim_id,
            "linked_body_statement_ids": [stoic_claim_id],
            "citation_body_statement_ids": [stoic_claim_id],
            "cited_material_not_independently_consulted": True,
        },
    )
    add_statement(
        stoic_claim_id,
        subject="cand-2236", obj="cand-2510", predicate="described_himself_as_stoic_in_letter",
        quote=quote_between("Rosa referred to himself as a Stoic", "Rosa referred to himself as a Stoic in a letter to Ricciardi dated 27 May 1651"),
        claim="Haskell's note says Rosa referred to himself as a Stoic in a letter to Ricciardi dated 27 May 1651.",
        relation_note="This records the explicit source statement linking Rosa's self-description to Stoicism; the underlying letter is represented separately and remains unexamined.",
        line_number=41, mentioned=("cand-2236", "cand-2510", "cand-2187", "cand-11954"),
        qualification="Reported in Haskell's footnote through Limentani, page 79; neither the letter nor cited page was independently consulted.",
        extras={
            "footnote_marker": 2,
            "footnote_target_line": 41,
            "letter_candidate_id": "cand-11954",
            "recipient_candidate_id": "cand-2187",
            "date": "1651-05-27",
            "publication_candidate_id": "cand-6239",
            "page": 79,
            "supporting_citation_statement_id": limentani_id,
        },
    )
    add_statement(
        authored_id,
        subject="cand-11954", obj="cand-2236", predicate="authored_by",
        quote=quote_between("Rosa referred to himself as a Stoic", "Rosa referred to himself as a Stoic in a letter to Ricciardi dated 27 May 1651"),
        claim="Haskell identifies Rosa as the author of the letter dated 27 May 1651.",
        relation_note="The footnote identifies Rosa as the letter's author; the letter and cited edition have not been independently examined.",
        line_number=41, mentioned=("cand-11954", "cand-2236", "cand-2187"),
        text_layer="reported correspondence",
        qualification="The source says Rosa referred to himself in a letter to Ricciardi; the identity of the underlying item is not independently verified.",
        extras={
            "date": "1651-05-27",
            "linked_body_statement_ids": [stoic_claim_id],
            "cited_material_not_independently_consulted": True,
        },
    )
    add_statement(
        addressed_id,
        subject="cand-11954", obj="cand-2187", predicate="addressed_to",
        quote=quote_between("Rosa referred to himself as a Stoic", "Rosa referred to himself as a Stoic in a letter to Ricciardi dated 27 May 1651"),
        claim="Haskell identifies Ricciardi as the addressee of the letter dated 27 May 1651.",
        relation_note="The footnote names Ricciardi as the letter's addressee; the letter and cited edition have not been independently examined.",
        line_number=41, mentioned=("cand-11954", "cand-2236", "cand-2187"),
        text_layer="reported correspondence",
        qualification="The source explicitly says 'to Ricciardi'; the underlying item is not independently verified.",
        extras={
            "date": "1651-05-27",
            "linked_body_statement_ids": [stoic_claim_id],
            "cited_material_not_independently_consulted": True,
        },
    )
    add_statement(
        "st-chp5-seciv-note-l47-p144-bellori-nota-refers-to-de-rossi-collection",
        subject="cand-4805", obj="cand-11484", predicate="refers_to_collection",
        quote=quote_between("There is also a reference to De’ Rossi’s collection in Bellori’s Nota de Musei.", "There is also a reference to De’ Rossi’s collection in Bellori’s Nota de Musei."),
        claim="Haskell's p.144 note says Bellori's Nota de Musei refers to De' Rossi's collection.",
        relation_note="This preserves the explicit reference from Bellori's named work to De' Rossi's source-defined collection; it does not establish ownership or present custody.",
        line_number=47, mentioned=("cand-2269", "cand-3535", "cand-4805", "cand-11484"),
        text_layer="authorial footnote statement",
        qualification="The source note identifies the reference; Bellori's work was not independently consulted in this step.",
        extras={
            "footnote_marker": 2,
            "author_candidate_id": "cand-3535",
            "referenced_work_candidate_id": "cand-4805",
            "collection_candidate_id": "cand-11484",
            "linked_body_statement_ids": ["st-chp5-p144-de-rossi-private-museum-of-rosa-works"],
            "related_segment": "chp-5:05_CHP-5_sec_iv:l23-31",
            "related_source_lines": [24],
        },
    )

    statements.extend(added)
    all_rows = {row["statement_id"]: row for row in statements}

    def add_mention(mention_id: str, candidate_id: str, surface: str, note: str) -> None:
        if any(row["mention_id"] == mention_id for row in mentions):
            raise SystemExit(f"Refusing: mention ID already exists: {mention_id}")
        start = segment_text.find(surface)
        if start < 0 or segment_text.find(surface, start + 1) >= 0:
            raise SystemExit(f"Refusing: mention surface is missing or ambiguous: {surface!r}")
        mentions.append(
            {
                "mention_id": mention_id,
                "segment_id": SEGMENT_ID,
                "candidate_id": candidate_id,
                "surface_form": surface,
                "start_char": str(start),
                "end_char": str(start + len(surface)),
                "note": note,
            }
        )

    add_mention("m-chp5-seciv-notes-41-stoic", "cand-2510", "a Stoic", "Rosa's source-reported self-description")
    add_mention("m-chp5-seciv-notes-41-letter-1651-05-27", "cand-11954", "a letter to Ricciardi dated 27 May 1651", "source-defined letter identified in Haskell's footnote")

    final_target = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    if len(added) != 5 or len(final_target) != 31:
        raise SystemExit(f"Refusing: expected 5 added note rows and 31 total; found {len(added)} / {len(final_target)}")
    expected_counts = {"true": 0, "false": 0, "unset": 0}
    for row in final_target:
        q = row.get("qualifiers", {})
        value = q.get("relation_candidate")
        expected_counts["true" if value is True else "false" if value is False else "unset"] += 1
        if value is None:
            raise SystemExit(f"Refusing: unresolved note statement remains: {row['statement_id']}")
        if set(q.get("mentioned_candidate_ids", [])) - set(candidate_by_id):
            raise SystemExit(f"Refusing: unknown candidate in note statement: {row['statement_id']}")
        if row.get("original_quote") and row["original_quote"] not in segment_text:
            raise SystemExit(f"Refusing: note quote outside S0 segment: {row['statement_id']}")
    if expected_counts["unset"] != 0:
        raise SystemExit(f"Refusing: note segment still has unresolved rows: {expected_counts}")

    note_mentions = [row for row in mentions if row.get("segment_id") == SEGMENT_ID]
    for row in note_mentions:
        start, end = int(row["start_char"]), int(row["end_char"])
        if segment_text[start:end] != row["surface_form"]:
            raise SystemExit(f"Refusing: note mention span mismatch: {row['mention_id']}")
        if row["candidate_id"] not in candidate_by_id:
            raise SystemExit(f"Refusing: note mention has unknown candidate: {row['mention_id']}")

    coverage_row = next((row for row in coverage if row.get("segment_id") == SEGMENT_ID), None)
    if not coverage_row:
        raise SystemExit("Refusing: note coverage row is missing")
    coverage_row["disposition"] = "reviewed"
    coverage_row["migration_status"] = "complete"
    coverage_row["source_line_ranges"] = "L39-54"
    coverage_row["note"] = (
        "S2语义处理：复核并分类p.143–145脚注及回链；拆分p.143注2中的Baldinucci/Limentani引证、"
        "Rosa自称Stoic的书信事实及信件作者/收信人；分列De’ Rossi藏品在Bellori《Nota de Musei》的记载；"
        "为p.144注3补齐未名祭坛画组至Chantilly的位置关系。内部章回指列为非关系。"
        "所引版本和信件均未独立查阅，未写入S6。"
    )

    print("PREVIEW" if not args.apply else "APPLY PLAN")
    print(f"segment={SEGMENT_ID}; existing={len(target)}; added={len(added)}; final={len(final_target)}")
    print(f"classified rows={expected_counts}; candidates_added=1; mentions_added=2; target_mentions={len(note_mentions)}")
    print("split the compound p.143 note 2, preserved its letter and bibliography links, and separated the Bellori collection reference")
    print("classified citations and the internal chapter cross-reference; maintained p.144/p.145 body backlinks")
    print("S0 and relations.csv unchanged; all note quotes and mention spans checked")
    if not args.apply:
        return

    for path in [statement_path, candidate_path, mention_path, coverage_path]:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"Refusing: backup already exists: {backup.name}")
        shutil.copy2(path, backup)
    write_jsonl(statement_path, statements)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions)
    write_csv(coverage_path, coverage_fields, coverage)
    print("Wrote book-statements.jsonl, entity-candidates.csv, mentions.csv, and s2-coverage.csv.")
    print("Backups saved with suffix", BACKUP_SUFFIX)


if __name__ == "__main__":
    main()
