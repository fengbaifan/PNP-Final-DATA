#!/usr/bin/env python3
"""Guarded S2 semantic review for chapter 5, printed page 143, lines 14-21.

Default mode is a read-only preview. Apply once only after the preview is
reviewed; table SHA-256 checks prevent applying this plan to a changed base.
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "05_CHP-5_sec_iv.md"
SEGMENT_ID = "chp-5:05_CHP-5_sec_iv:l14-21"
SOURCE_SEGMENT_SHA = "92a6b5be3ea194e86057751a2ff20161c2eeda358fa9a3a1749cc4121422c013"
EXPECTED_HASHES = {
    "book-statements.jsonl": "c02fcf5fc5ac574f70c256a7bd966b4c8c128aa150e6c864f8dd99a8b534bf84",
    "entity-candidates.csv": "5b562dabc3f6a9c3161a186e20201f5f0506f8cdcd0e647c7c1de0d3c34e8557",
    "mentions.csv": "960ed0f09028718753e2124770f1f7339dbcc7715312755774c1c2d593a997be",
    "s2-coverage.csv": "915bbd1fdd41e9a7f53d9959865952f69269f0436540590dc81bec31fcd5d25a",
}
BACKUP_SUFFIX = ".bak-s2-chp5-seciv-l14-21-20261013"


def sha256(path: Path) -> str:
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
        actual = sha256(TABLES / name)
        if actual != expected:
            raise SystemExit(f"Refusing: {name} hash changed: {actual}")

    segments = read_jsonl(TABLES / "segments.jsonl")
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SOURCE_SEGMENT_SHA:
        raise SystemExit("Refusing: S0 segment fingerprint changed or is missing")
    if segment.get("asset_sha256") != "805df7b2bdc296cf987069cb0cea829bc07ec8932e28b075e9575f0c2ac67c4f":
        raise SystemExit("Refusing: source asset fingerprint changed")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(source_lines[13:21])

    def line(n: int) -> str:
        return source_lines[n - 1]

    def line_slice(n: int, start: str, stop: str) -> str:
        text = line(n)
        a = text.index(start)
        b = text.index(stop, a)
        return text[a:b]

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

    target_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    target_ids = {row["statement_id"] for row in target_rows}
    if len(target_rows) != 23 or len(target_ids) != 23:
        raise SystemExit(f"Refusing: expected 23 distinct source statements, found {len(target_rows)}")
    if any(row.get("qualifiers", {}).get("relation_candidate") in (True, False) for row in target_rows):
        raise SystemExit("Refusing: target segment is already semantically classified")

    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    max_candidate = max(int(row["candidate_id"].split("-")[1]) for row in candidates)
    if max_candidate != 11947:
        raise SystemExit(f"Refusing: expected next candidate sequence after cand-11947, found cand-{max_candidate}")

    row_by_id = {row["statement_id"]: row for row in target_rows}
    missing = {
        "st-chp5-p143-carlo-de-rossi-greatest-roman-patron",
        "st-chp5-p143-carpegna-and-teodoli-associated_with_bambocciate",
        "st-chp5-p143-de-rossi-paid-interest-on-rosa-deposit",
        "st-chp5-p143-duke-of-modena-requested-pictures",
        "st-chp5-p143-learned-connoisseurs-rarely-interested-in-rosa-histories",
        "st-chp5-p143-paintings-recorded-ancient-heroes",
        "st-chp5-p143-plutarch-and-seneca-used-for-quotations",
        "st-chp5-p143-rosa-admired-by-wrong-audiences",
        "st-chp5-p143-rosa-and-de-rossi-quarrel-in-1667",
        "st-chp5-p143-rosa-fascinated-roman-churchmen",
        "st-chp5-p143-rosa-million-for-large-picture",
        "st-chp5-p143-rosa-potential-clients-preferred-landscapes",
        "st-chp5-p143-rosa-proverb-characterized-by-bitterness",
        "st-chp5-p143-rosa-quotation-alludes-to-stoicism",
        "st-chp5-p143-rosa-small-landscape-complaint",
        "st-chp5-p143-rosa-stoic-roast-meat-letter",
        "st-chp5-p143-rosa-studied-stoics-for-art-themes",
        "st-chp5-p143-rosa-talents-admired-in-florence",
        "st-chp5-p143-rosa-wanted-landscapes-forgotten",
        "st-chp5-p143-stoicism-appealed-to-the-disappointed",
        "st-chp5-p143-stoicism-colored-ethics-and-imagery",
        "st-chp5-p143-stoicism-gained-ground-in-europe",
        "st-chp5-p143-stoicism-suited-seventeenth-century",
    }
    if target_ids != missing:
        raise SystemExit("Refusing: target statement ID set differs from the reviewed plan")

    def update_existing(
        statement_id: str,
        *,
        relation: bool,
        note: str,
        subject: str | None | object = ...,
        obj: str | None | object = ...,
        predicate: str | None = None,
        original_quote: str | None = None,
        claim: str | None = None,
        remove_qualifiers: tuple[str, ...] = (),
        set_qualifiers: dict | None = None,
        open_reason: str | None = None,
    ) -> None:
        row = row_by_id[statement_id]
        q = row.setdefault("qualifiers", {})
        q["relation_candidate"] = relation
        q["relation_candidate_note"] = note
        if relation and open_reason:
            q["open_endpoint_reason"] = open_reason
        elif not relation:
            q.pop("open_endpoint_reason", None)
        if subject is not ...:
            row["subject_candidate_id"] = subject
        if obj is not ...:
            row["object_candidate_id"] = obj
        if predicate is not None:
            row["predicate"] = predicate
        if original_quote is not None:
            row["original_quote"] = original_quote
        if claim is not None:
            q["claim"] = claim
        for key in remove_qualifiers:
            q.pop(key, None)
        if set_qualifiers:
            q.update(set_qualifiers)

    def new_statement(
        statement_id: str,
        *,
        subject: str | None,
        obj: str | None,
        predicate: str,
        quote: str,
        claim: str,
        relation: bool,
        relation_note: str,
        line_start: int,
        line_end: int,
        speaker: str = "Haskell",
        text_layer: str = "authorial narration",
        qualification: str = "",
        mentioned: tuple[str, ...] = (),
        open_reason: str | None = None,
        extras: dict | None = None,
    ) -> dict:
        if statement_id in {r["statement_id"] for r in statements}:
            raise SystemExit(f"Refusing: new statement ID already exists: {statement_id}")
        if quote not in segment_text:
            raise SystemExit(f"Refusing: proposed quote is not a literal S0 substring: {statement_id}")
        q = {
            "source_line_start": line_start,
            "source_line_end": line_end,
            "printed_page": "143",
            "pdf_physical_page": 28,
            "claim": claim,
            "speaker": speaker,
            "text_layer": text_layer,
            "qualification": qualification,
            "relation_candidate": relation,
            "relation_candidate_note": relation_note,
        }
        if mentioned:
            q["mentioned_candidate_ids"] = list(mentioned)
        if open_reason:
            q["open_endpoint_reason"] = open_reason
        if extras:
            q.update(extras)
        return {
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

    # Split the existing compound claims and repair their endpoint direction.
    update_existing(
        "st-chp5-p143-carlo-de-rossi-greatest-roman-patron",
        relation=True,
        note="This row records only Haskell's characterization of Carlo de' Rossi as Rosa's greatest patron in Rome; the sibling and personal attributes are split below.",
        original_quote=line_slice(21, "His greatest patron in Rome", " brother"),
        claim="Haskell identifies Carlo de' Rossi as Salvator Rosa's greatest patron in Rome.",
        set_qualifiers={
            "place_candidate_id": "cand-4490",
            "mentioned_candidate_ids": ["cand-2269", "cand-2236"],
            "qualification": "Haskell's characterization; the description is not independently verified here.",
        },
    )
    update_existing(
        "st-chp5-p143-carpegna-and-teodoli-associated_with_bambocciate",
        relation=True,
        note="Haskell identifies Carpegna as one example of those specializing in bambocciate; Teodoli is split into a separate statement.",
        subject="cand-0567",
        obj="cand-6099",
        predicate="specialized_in_picture_type",
        original_quote=quote_between("those who specialised in bambocciate", "the Conte Carpegna"),
        claim="Haskell names Count Carpegna as an example of a person who specialized in bambocciate.",
        remove_qualifiers=("second_collector_candidate_id",),
        set_qualifiers={"mentioned_candidate_ids": ["cand-0567", "cand-6099"]},
    )
    update_existing(
        "st-chp5-p143-de-rossi-paid-interest-on-rosa-deposit",
        relation=True,
        note="Records the interest payment reported by Haskell; the underlying deposit is split into its own directed statement.",
        subject="cand-2269",
        obj="cand-2236",
        predicate="paid_interest_to_depositor",
        original_quote=line_slice(21, "De", " on the 4000 scudi"),
        claim="Haskell reports that Carlo de' Rossi paid Rosa regular interest at six per cent on the 4000 scudi Rosa had deposited with him.",
        set_qualifiers={
            "interest_rate_percent": 6,
            "principal": 4000,
            "currency": "scudi",
            "mentioned_candidate_ids": ["cand-2269", "cand-2236"],
            "print_reading_correction": {"source_line": 21, "source_form": "6 per cent,", "printed_reading": "6 per cent."},
        },
    )
    duke_quote = line_slice(20, "the Duke of Modena who wrote", "Pier Francesco Mola.")
    update_existing(
        "st-chp5-p143-duke-of-modena-requested-pictures",
        relation=True,
        note="Records the Duke's communication to his Roman agent; the six requested artist/type combinations are separated below and are not treated as commissions.",
        subject="cand-1675",
        obj="cand-11948",
        predicate="wrote_to_agent_requesting_pictures",
        original_quote=duke_quote,
        claim="Haskell reports that the Duke of Modena wrote to his agent in Rome with requests for pictures in specified categories by named artists.",
        set_qualifiers={
            "agent_candidate_id": "cand-11948",
            "agent_place_candidate_id": "cand-4490",
            "requested_artists": [
                {"candidate_id": "cand-2236", "picture_types": ["battles"]},
                {"candidate_id": "cand-6221", "picture_types": ["battles"]},
                {"candidate_id": "cand-1765", "picture_types": ["flower pictures"]},
                {"candidate_id": "cand-0625", "picture_types": ["flower pictures"]},
                {"candidate_id": "cand-0949", "picture_types": ["landscapes"]},
                {"candidate_id": "cand-1676", "picture_types": ["fables"]},
            ],
            "mentioned_candidate_ids": ["cand-1675", "cand-11948", "cand-4490", "cand-2236", "cand-6221", "cand-1765", "cand-0625", "cand-0949", "cand-1676"],
            "footnote_marker": 5,
            "footnote_target_line": 44,
            "footnote_printed_page": "143",
            "footnote_segment": "chp-5:05_CHP-5_sec_iv:l39-54",
            "footnote_link_status": "linked",
        },
    )
    update_existing(
        "st-chp5-p143-learned-connoisseurs-rarely-interested-in-rosa-histories",
        relation=True,
        note="The endpoint is Rosa's unnamed history paintings, not Rosa himself.",
        subject="cand-6222",
        obj=None,
        predicate="rarely_show_interest_in_rosa_history_paintings",
        original_quote=quote_between("Only rarely did the learned connoisseurs", "show any interest."),
        claim="Haskell says the learned connoisseurs whom Rosa hoped to impress rarely showed interest in his history paintings.",
        open_reason="The specific history paintings are not named in this passage; keep the artwork endpoint open.",
        set_qualifiers={"mentioned_candidate_ids": ["cand-6222", "cand-2236"]},
    )
    update_existing(
        "st-chp5-p143-paintings-recorded-ancient-heroes",
        relation=True,
        note="The sentence connects an unnamed body of paintings with their represented ancient heroes; neither group is enumerated.",
        subject=None,
        obj=None,
        predicate="depicted_deeds_of_ancient_heroes",
        open_reason="The paintings and the represented heroes are both described collectively, with no individually identifiable work or person.",
        claim="Haskell says innumerable paintings recorded the deeds of virtuous, iron-willed heroes of antiquity.",
    )
    update_existing(
        "st-chp5-p143-plutarch-and-seneca-used-for-quotations",
        relation=False,
        note="The source names two separate authors as quotation sources; it does not assert a relation between Plutarch and Seneca. Individual source-use statements are added below.",
        subject=None,
        obj=None,
        predicate="jointly_used_as_quotation_sources",
        claim="Haskell says Plutarch and Seneca were mined for quotations.",
        set_qualifiers={"mentioned_candidate_ids": ["cand-1962", "cand-2418"]},
    )
    update_existing(
        "st-chp5-p143-rosa-admired-by-wrong-audiences",
        relation=True,
        note="This general statement describes an unnamed audience; named examples are recorded separately.",
        obj=None,
        predicate="admired_by_wrong_audience",
        open_reason="Haskell does not define the full audience or identify all its members; the named examples are not an exhaustive group.",
        claim="Haskell says Rosa was keenly and rightly admired, but by the wrong people.",
    )
    update_existing(
        "st-chp5-p143-rosa-and-de-rossi-quarrel-in-1667",
        relation=True,
        note="Haskell reports a quarrel between Rosa and Carlo de' Rossi in 1667; the quoted complaint is attributed to Rosa in the source passage.",
        predicate="quarrelled_with",
        original_quote=line_slice(21, 'but in "1667', "little gratitude"),
        claim="Haskell reports that Rosa and Carlo de' Rossi quarrelled bitterly in 1667.",
        set_qualifiers={
            "date": "1667",
            "mentioned_candidate_ids": ["cand-2236", "cand-2269"],
            "print_reading_correction": {"source_line": 21, "source_form": '"1667', "printed_reading": "1667"},
        },
    )
    update_existing(
        "st-chp5-p143-rosa-fascinated-roman-churchmen",
        relation=True,
        note="Rome is the setting, not the object of fascination; the churchmen form an unnamed audience.",
        obj=None,
        predicate="fascinated_highly_placed_churchmen",
        open_reason="The churchmen are described as a number of highly placed people but are not individually identified.",
        claim="Haskell says Rosa fascinated a number of highly placed churchmen in Rome, though not in the way he wanted.",
        set_qualifiers={"place_candidate_id": "cand-3126", "mentioned_candidate_ids": ["cand-2236", "cand-3126"]},
    )
    update_existing(
        "st-chp5-p143-rosa-million-for-large-picture",
        relation=True,
        note="The price reply is directed to the unnamed prelate who asked about a large picture; the candidate is source-defined and identity remains unresolved.",
        obj="cand-11949",
        predicate="quoted_exorbitant_price_to_prelate",
        open_reason="The prelate is not named or identified beyond this passage; the requested picture is not individually specified.",
        claim="Haskell says Rosa replied 'a million' when an unnamed prelate tactfully asked the price of a large picture.",
        set_qualifiers={
            "prelate_candidate_id": "cand-11949",
            "mentioned_candidate_ids": ["cand-2236", "cand-11949"],
            "footnote_marker": 3,
            "footnote_target_line": 42,
            "footnote_printed_page": "143",
            "footnote_segment": "chp-5:05_CHP-5_sec_iv:l39-54",
            "footnote_link_status": "linked",
        },
    )
    update_existing(
        "st-chp5-p143-rosa-potential-clients-preferred-landscapes",
        relation=True,
        note="The clients and landscape works are the relational participants; neither group is specified. Rosa is retained as the artist in qualifiers.",
        subject=None,
        obj=None,
        predicate="potential_clients_preferred_rosa_landscapes",
        open_reason="The potential clients and the landscape works are not individually identified; Rosa is named as the artist but is not one endpoint of the preference relation.",
        claim="Haskell says Rosa's potential clients wanted his landscapes, especially small ones.",
        set_qualifiers={"artist_candidate_id": "cand-2236", "mentioned_candidate_ids": ["cand-2236"]},
    )
    update_existing(
        "st-chp5-p143-rosa-proverb-characterized-by-bitterness",
        relation=False,
        note="This is Haskell's stylistic evaluation of a phrase, not a relation between entities.",
        claim="Haskell characterizes the phrase as combining bitterness, assumed self-depreciation, and a homely proverb.",
    )
    update_existing(
        "st-chp5-p143-rosa-quotation-alludes-to-stoicism",
        relation=True,
        note="Haskell identifies an allusion in Rosa's quoted phrase to Stoicism.",
        predicate="quoted_phrase_alluded_to",
        subject="cand-2236",
        obj="cand-2510",
        claim="Haskell says the allusion in Rosa's phrase is to Stoicism.",
        set_qualifiers={"mentioned_candidate_ids": ["cand-2236", "cand-2510"]},
    )
    update_existing(
        "st-chp5-p143-rosa-small-landscape-complaint",
        relation=True,
        note="This preserves Rosa's reported complaint about clients' demand for small landscapes; note 2 identifies the reported letter to Ricciardi.",
        open_reason="The clients and the requested small landscapes are not individually identified; Rosa is the speaker of the reported complaint.",
        predicate="reported_demand_for_small_landscapes",
        claim="In a quoted complaint, Rosa says people repeatedly wanted his small landscapes.",
        set_qualifiers={
            "speaker_candidate_id": "cand-2236",
            "footnote_marker": 2,
            "footnote_target_line": 41,
            "footnote_printed_page": "143",
            "footnote_segment": "chp-5:05_CHP-5_sec_iv:l39-54",
            "footnote_link_status": "linked",
        },
    )
    update_existing(
        "st-chp5-p143-rosa-stoic-roast-meat-letter",
        relation=True,
        note="This is a reported letter passage; note 1 identifies the letter to Ricciardi dated 9 October 1666. The letter and cited edition were not independently examined.",
        obj="cand-2510",
        predicate="used_stoic_roast_meat_metaphor_in_letter",
        claim="Haskell quotes Rosa describing a social success to a friend through a Stoic roast-meat metaphor.",
        set_qualifiers={
            "letter_candidate_id": "cand-11572",
            "recipient_candidate_id": "cand-2187",
            "footnote_marker": 1,
            "footnote_target_line": 40,
            "footnote_printed_page": "143",
            "footnote_segment": "chp-5:05_CHP-5_sec_iv:l39-54",
            "footnote_link_status": "linked",
            "cited_material_not_independently_consulted": True,
        },
    )
    update_existing(
        "st-chp5-p143-rosa-studied-stoics-for-art-themes",
        relation=True,
        note="Haskell reports Rosa's study of Stoic writings as a source for themes in his pictures and prints.",
        predicate="studied_writings_for_art_themes",
        claim="Haskell says Rosa studied Stoic writings for themes for his pictures and prints.",
    )
    update_existing(
        "st-chp5-p143-rosa-talents-admired-in-florence",
        relation=True,
        note="The Florentine society is the unnamed audience; Florence is the setting, not the admired object.",
        obj=None,
        predicate="talents_admired_by_florentine_society",
        open_reason="The society is described as brilliant but its members are not identified; Florence is retained as the setting.",
        claim="Haskell says Rosa's conversation, music, poetry, and mime were admired in Florentine society as much as his painting.",
        set_qualifiers={
            "place_candidate_id": "cand-3397",
            "mentioned_candidate_ids": ["cand-2236", "cand-3397"],
            "context_source_line_start": 12,
            "context_source_line_end": 15,
            "context_note": "The Florence setting and first part of the list of talents begin in the preceding source segment L12.",
        },
    )
    update_existing(
        "st-chp5-p143-rosa-wanted-landscapes-forgotten",
        relation=False,
        note="This is a quoted expression of Rosa's ill-temper about the future reputation of his landscape paintings; no relation candidate is asserted.",
        claim="Haskell reports Rosa saying he was glad some pictures were deteriorating so people would forget he had painted landscapes.",
        set_qualifiers={
            "footnote_marker": 4,
            "footnote_target_line": 43,
            "footnote_printed_page": "143",
            "footnote_segment": "chp-5:05_CHP-5_sec_iv:l39-54",
            "footnote_link_status": "linked",
        },
    )
    update_existing(
        "st-chp5-p143-stoicism-appealed-to-the-disappointed",
        relation=True,
        note="Haskell describes Stoicism as appealing to an unnamed group who felt mistreated or excluded from conspicuous rewards.",
        open_reason="The people who felt mistreated or excluded are described as a group, not individually identified.",
        claim="Haskell says Stoicism particularly appealed to people who felt the world had treated them badly or denied them ostentatious prizes.",
        set_qualifiers={"print_reading_correction": {"source_line": 16, "source_form": "selfcontrol", "printed_reading": "self-control"}},
    )
    update_existing(
        "st-chp5-p143-stoicism-colored-ethics-and-imagery",
        relation=True,
        note="This records the reported influence of Stoicism on the ethics and imagery of men of action and artists; the affected group is not enumerated.",
        open_reason="The people and artists are described collectively without individual endpoints.",
        claim="Haskell says Stoicism colored the ethics and imagery of men of action and artists.",
    )
    first_clause = quote_between("All over Europe this philosophy had been gaining ground", "the late sixteenth century")
    update_existing(
        "st-chp5-p143-stoicism-gained-ground-in-europe",
        relation=True,
        note="This row records only the spread of Stoicism across Europe from the late sixteenth century; its reported replacement of Christianity is split below.",
        subject="cand-2510",
        obj="cand-3462",
        predicate="gained_ground_in_region",
        original_quote=first_clause,
        claim="Haskell says Stoicism had been gaining ground throughout Europe since the late sixteenth century.",
    )
    update_existing(
        "st-chp5-p143-stoicism-suited-seventeenth-century",
        relation=False,
        note="This is Haskell's assessment that Stoicism suited the turbulence of the seventeenth century, not a relation candidate.",
        claim="Haskell characterizes Stoicism as well suited to the storm-tossed seventeenth century.",
    )

    candidates_to_add = [
        {
            "candidate_id": "cand-11948",
            "index_entry_id": "",
            "canonical_name": "Unidentified Roman agent of the Duke of Modena (p. 143)",
            "index_page_range": "",
            "suggested_type": "person",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell says the Duke of Modena wrote to his agent in Rome requesting pictures by named artists. The agent's name and identity are not supplied; this candidate denotes only the source-defined intermediary in this request.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": "chp-5:05_CHP-5_sec_iv:l14-21#L20",
        },
        {
            "candidate_id": "cand-11949",
            "index_entry_id": "",
            "canonical_name": "Unidentified prelate who asked Rosa the price of a large picture (p. 143)",
            "index_page_range": "",
            "suggested_type": "person",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell describes an unnamed prelate who tactfully asked Rosa the price of a large picture. No name, office, or further identity evidence is supplied.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": "chp-5:05_CHP-5_sec_iv:l14-21#L18",
        },
    ]

    new_rows: list[dict] = []
    new_rows.append(new_statement(
        "st-chp5-p143-teodoli-specialized-in-bambocciate",
        subject="cand-2550", obj="cand-6099", predicate="specialized_in_picture_type",
        quote=quote_between("those who specialised in bambocciate", "the Marchese Teodoli"),
        claim="Haskell names Marchese Teodoli as an example of a person who specialized in bambocciate.",
        relation=True, relation_note="Teodoli is named as a separate example in the source's description of people specializing in bambocciate.",
        line_start=20, line_end=20, qualification="The text does not enumerate Teodoli's holdings.",
        mentioned=("cand-2550", "cand-6099"),
    ))
    new_rows.extend([
        new_statement(
            "st-chp5-p143-carlo-de-rossi-brother-of-luigi",
            subject="cand-2269", obj="cand-2271", predicate="brother_of",
            quote=line_slice(21, "brother of the famous composer Luigi", " and himself"),
            claim="Haskell identifies Luigi as the brother of Carlo de' Rossi.",
            relation=True, relation_note="The kinship relation is explicit in Haskell's sentence.",
            line_start=21, line_end=21, mentioned=("cand-2269", "cand-2271"),
            extras={"relationship_scope": "Haskell's biographical statement", "footnote_marker": 6, "footnote_target_line": 45, "footnote_printed_page": "143", "footnote_segment": "chp-5:05_CHP-5_sec_iv:l39-54", "footnote_link_status": "linked"},
        ),
        new_statement(
            "st-chp5-p143-carlo-de-rossi-banker",
            subject="cand-2269", obj=None, predicate="described_as_banker",
            quote=line_slice(21, "his banker, Carlo", " brother"),
            claim="Haskell describes Carlo de' Rossi as Rosa's banker.",
            relation=False, relation_note="This is an occupation or role attribute of Carlo, not a relation candidate in this table.",
            line_start=21, line_end=21, mentioned=("cand-2269", "cand-2236"),
            extras={"footnote_marker": 6, "footnote_target_line": 45, "footnote_printed_page": "143", "footnote_segment": "chp-5:05_CHP-5_sec_iv:l39-54", "footnote_link_status": "linked"},
        ),
        new_statement(
            "st-chp5-p143-carlo-de-rossi-talented-musician",
            subject="cand-2269", obj=None, predicate="described_as_talented_musician",
            quote=line_slice(21, "himself a talented musician", ".6"),
            claim="Haskell describes Carlo de' Rossi as a talented musician.",
            relation=False, relation_note="This is a personal attribute, not a relation candidate.",
            line_start=21, line_end=21, mentioned=("cand-2269",),
            extras={"footnote_marker": 6, "footnote_target_line": 45, "footnote_printed_page": "143", "footnote_segment": "chp-5:05_CHP-5_sec_iv:l39-54", "footnote_link_status": "linked"},
        ),
        new_statement(
            "st-chp5-p143-luigi-de-rossi-famous-composer",
            subject="cand-2271", obj=None, predicate="described_as_famous_composer",
            quote=line_slice(21, "the famous composer Luigi", " and himself"),
            claim="Haskell describes Luigi de' Rossi as a famous composer.",
            relation=False, relation_note="This is a professional attribute, not a relation candidate.",
            line_start=21, line_end=21, mentioned=("cand-2271",),
            extras={"footnote_marker": 6, "footnote_target_line": 45, "footnote_printed_page": "143", "footnote_segment": "chp-5:05_CHP-5_sec_iv:l39-54", "footnote_link_status": "linked"},
        ),
        new_statement(
            "st-chp5-p143-rosa-deposited-scudi-with-de-rossi",
            subject="cand-2236", obj="cand-2269", predicate="deposited_money_with",
            quote=line_slice(21, "the 4000 scudi that Rosa deposited with him", ", but in"),
            claim="Haskell says Rosa deposited 4000 scudi with Carlo de' Rossi.",
            relation=True, relation_note="This is the deposit relation, kept separate from De' Rossi's payment of interest.",
            line_start=21, line_end=21,
            qualification="The amount is expressed in scudi; no deposit date or term is given.",
            mentioned=("cand-2236", "cand-2269"),
            extras={"amount": 4000, "currency": "scudi"},
        ),
    ])

    requested = [
        ("cand-2236", "Rosa", "battles", "battles_by_rosa"),
        ("cand-6221", "Borgognone", "battles", "battles_by_borgognone"),
        ("cand-1765", "Mario de' Fiori", "flower pictures", "flower_pictures_by_mario_de_fiori"),
        ("cand-0625", "Cerquozzi", "flower pictures", "flower_pictures_by_cerquozzi"),
        ("cand-0949", "Gaspard Poussin", "landscapes", "landscapes_by_gaspard_poussin"),
        ("cand-1676", "Pier Francesco Mola", "fables", "fables_by_pier_francesco_mola"),
    ]
    requested_ids = []
    for artist_id, artist_label, picture_type, statement_slug in requested:
        if statement_slug == "battles_by_rosa":
            quote = "battles by Rosa"
        elif statement_slug == "battles_by_borgognone":
            quote = "battles by Rosa and Borgognone"
        elif statement_slug == "flower_pictures_by_mario_de_fiori":
            quote = quote_between("flower pictures by Mario", " and Cerquozzi")
        elif statement_slug == "flower_pictures_by_cerquozzi":
            quote = quote_between("flower pictures by Mario", "Cerquozzi")
        elif statement_slug == "landscapes_by_gaspard_poussin":
            quote = "landscapes by Gaspard Poussin"
        else:
            quote = "fables by Pier Francesco Mola"
        sid = f"st-chp5-p143-duke-request-{statement_slug.replace('_', '-')}"
        requested_ids.append(sid)
        new_rows.append(new_statement(
            sid, subject="cand-1675", obj=artist_id, predicate="requested_picture_type_by_artist_via_agent",
            quote=quote, claim=f"Haskell reports that the Duke of Modena requested {picture_type} by {artist_label} through his Roman agent.",
            relation=True, relation_note="This records a requested picture category communicated through the Duke's agent; it does not establish a commission or completed work.",
            line_start=20, line_end=20,
            qualification="The requested works are not individually identified and the agent is not named.",
            mentioned=("cand-1675", "cand-11948", "cand-4490", artist_id),
            extras={
                "picture_type": picture_type,
                "intermediary_candidate_id": "cand-11948",
                "request_place_candidate_id": "cand-4490",
                "commission_status": "not established",
                "footnote_marker": 5,
                "footnote_target_line": 44,
                "footnote_printed_page": "143",
                "footnote_segment": "chp-5:05_CHP-5_sec_iv:l39-54",
                "footnote_link_status": "linked",
            },
        ))

    audience_quote = quote_between("But always by the wrong people", "Pier Francesco Mola.")
    for slug, admirer_id, label in [
        ("carpegna", "cand-0567", "Conte Carpegna"),
        ("teodoli", "cand-2550", "Marchese Teodoli"),
        ("duke-of-modena", "cand-1675", "Duke of Modena"),
    ]:
        new_rows.append(new_statement(
            f"st-chp5-p143-rosa-admired-by-{slug}",
            subject="cand-2236", obj=admirer_id, predicate="admired_by",
            quote=audience_quote, claim=f"Haskell names {label} as an example among the people who admired Rosa.",
            relation=True, relation_note="The named person is included as an example in the source's description of Rosa's audience.",
            line_start=20, line_end=20,
            qualification="An example of the audience, not an exhaustive list or a separate commission.",
            mentioned=("cand-2236", admirer_id),
            extras={"audience_example": True},
        ))

    plutarch_quote = quote_between("Plutarch and Seneca were ransacked for quotations", "for quotations")
    new_rows.extend([
        new_statement(
            "st-chp5-p143-plutarch-used-as-quotation-source",
            subject="cand-1962", obj=None, predicate="used_as_quotation_source",
            quote=plutarch_quote, claim="Haskell says Plutarch's writings were mined for quotations.",
            relation=True, relation_note="The text identifies Plutarch as one quotation source; the cited quotations are not individually identified.",
            line_start=16, line_end=16, open_reason="No individual quotation or receiving work is named.",
            mentioned=("cand-1962",),
        ),
        new_statement(
            "st-chp5-p143-seneca-used-as-quotation-source",
            subject="cand-2418", obj=None, predicate="used_as_quotation_source",
            quote=plutarch_quote, claim="Haskell says Seneca's writings were mined for quotations.",
            relation=True, relation_note="The text identifies Seneca as one quotation source; the cited quotations are not individually identified.",
            line_start=16, line_end=16, open_reason="No individual quotation or receiving work is named.",
            mentioned=("cand-2418",),
        ),
    ])

    replaced_quote = quote_between("until for some daring thinkers", "as a guiding creed.")
    new_rows.append(new_statement(
        "st-chp5-p143-stoicism-virtually-replaced-christianity",
        subject="cand-2510", obj="cand-5855", predicate="virtually_replaced_as_guiding_creed",
        quote=replaced_quote,
        claim="Haskell says Stoicism virtually replaced Christianity as a guiding creed for some daring thinkers.",
        relation=True,
        relation_note="This is a source-attributed claim about a philosophical tradition and Christianity in the beliefs of some thinkers, not a claim about all Europeans.",
        line_start=15, line_end=16,
        qualification="Haskell limits the claim to 'some daring thinkers' and says 'virtually'; preserve both qualifications.",
        mentioned=("cand-2510", "cand-5855"),
        extras={"scope_group": "some daring thinkers"},
    ))

    new_rows.append(new_statement(
        "st-chp5-p143-rosa-hoped-to-impress-learned-connoisseurs",
        subject="cand-2236", obj="cand-6222", predicate="hoped_to_impress",
        quote=quote_between("the learned connoisseurs whom he hoped to impress", "whom he hoped to impress"),
        claim="Haskell says Rosa hoped to impress the learned connoisseurs.",
        relation=True, relation_note="The hope-to-impress relation is explicit; the unnamed connoisseur group is represented by cand-6222.",
        line_start=20, line_end=20, qualification="The statement is Haskell's report of Rosa's intended audience.",
        mentioned=("cand-2236", "cand-6222"),
    ))
    new_rows.append(new_statement(
        "st-chp5-p143-rosa-history-paintings-frigid-rhetorical-evaluation",
        subject="cand-2236", obj=None, predicate="history_paintings_evaluated_as_frigid_and_rhetorical",
        quote=quote_between("his frigid and rhetorical history paintings", "show any interest"),
        claim="Haskell characterizes Rosa's history paintings as frigid and rhetorical.",
        relation=False, relation_note="This is Haskell's evaluative characterization of a work category, not a relation candidate.",
        line_start=20, line_end=20, mentioned=("cand-2236",),
    ))

    all_new_ids = {row["statement_id"] for row in new_rows}
    if len(all_new_ids) != len(new_rows):
        raise SystemExit("Refusing: duplicate statement IDs in the proposed additions")
    if len(new_rows) != 20:
        raise SystemExit(f"Refusing: expected 20 atomic statements before the authorial evaluation, planned {len(new_rows)}")

    candidate_rows = [
        {
            "candidate_id": "cand-11948",
            "index_entry_id": "",
            "canonical_name": "Unidentified Roman agent of the Duke of Modena (p. 143)",
            "index_page_range": "",
            "suggested_type": "person",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell says the Duke of Modena wrote to his agent in Rome requesting pictures by named artists. The agent's name and identity are not supplied; this candidate denotes only the source-defined intermediary in this request.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": "chp-5:05_CHP-5_sec_iv:l14-21#L20",
        },
        {
            "candidate_id": "cand-11949",
            "index_entry_id": "",
            "canonical_name": "Unidentified prelate who asked Rosa the price of a large picture (p. 143)",
            "index_page_range": "",
            "suggested_type": "person",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell describes an unnamed prelate who tactfully asked Rosa the price of a large picture. No name, office, or further identity evidence is supplied.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": "chp-5:05_CHP-5_sec_iv:l14-21#L18",
        },
    ]
    if candidate_rows != candidates_to_add:
        raise SystemExit("Refusing: candidate plan definitions diverged")
    if any(row["candidate_id"] in candidate_by_id for row in candidate_rows):
        raise SystemExit("Refusing: proposed candidate ID already exists")

    prelate_start = segment_text.index("unfortunate prelate")
    agent_start = segment_text.index("his agent")
    mention_rows_to_add = [
        {
            "mention_id": "m-s2-chp5-p143-prelate-001",
            "segment_id": SEGMENT_ID,
            "candidate_id": "cand-11949",
            "surface_form": "unfortunate prelate",
            "start_char": str(prelate_start),
            "end_char": str(prelate_start + len("unfortunate prelate")),
            "note": "Unnamed prelate who asked Rosa the price of a large picture; identity remains unresolved.",
        },
        {
            "mention_id": "m-s2-chp5-p143-duke-agent-001",
            "segment_id": SEGMENT_ID,
            "candidate_id": "cand-11948",
            "surface_form": "his agent",
            "start_char": str(agent_start),
            "end_char": str(agent_start + len("his agent")),
            "note": "Unidentified intermediary of the Duke of Modena; Rome is captured by the adjacent existing place mention.",
        },
    ]
    existing_mention_ids = {row["mention_id"] for row in mentions}
    if any(row["mention_id"] in existing_mention_ids for row in mention_rows_to_add):
        raise SystemExit("Refusing: proposed mention ID already exists")
    for row in mention_rows_to_add:
        a, b = int(row["start_char"]), int(row["end_char"])
        if segment_text[a:b] != row["surface_form"]:
            raise SystemExit(f"Refusing: proposed mention span differs from S0: {row['mention_id']}")

    # The p.143 notes link to every atomic row extracted from the printed sentence.
    duke_id = "st-chp5-p143-duke-of-modena-requested-pictures"
    taste_id = "st-chp5-p143-duke-tastes-frivolous"
    new_rows.append(new_statement(
        taste_id, subject="cand-1675", obj=None, predicate="author_described_tastes_as_frivolous",
        quote=quote_between("whose tastes were notoriously frivolous", "who wrote"),
        claim="Haskell characterizes the Duke of Modena's tastes as frivolous.",
        relation=False, relation_note="This is Haskell's evaluative judgment, not a relation candidate.",
        line_start=20, line_end=20, mentioned=("cand-1675",),
    ))
    if len(new_rows) != 21:
        raise SystemExit(f"Refusing: expected 21 atomic statements after adding the authorial evaluation, planned {len(new_rows)}")
    requested_ids.insert(0, duke_id)

    # The printed marker follows the Duke's request; its six artist/type
    # combinations are linked to note 5 as the source for the requested list.
    footnote_map = {row["statement_id"]: row for row in statements}
    note5_id = "st-chp5-seciv-note-l44-p143-marker5"
    note6_id = "st-chp5-seciv-note-l45-p143-marker6"
    note5 = footnote_map[note5_id]["qualifiers"]
    note5["linked_body_statement_ids"] = requested_ids
    note5["citation_body_statement_ids"] = requested_ids
    note6 = footnote_map[note6_id]["qualifiers"]
    note6_body_ids = [
        "st-chp5-p143-carlo-de-rossi-greatest-roman-patron",
        "st-chp5-p143-carlo-de-rossi-brother-of-luigi",
        "st-chp5-p143-carlo-de-rossi-banker",
        "st-chp5-p143-carlo-de-rossi-talented-musician",
        "st-chp5-p143-luigi-de-rossi-famous-composer",
    ]
    note6["linked_body_statement_ids"] = note6_body_ids
    note6["citation_body_statement_ids"] = note6_body_ids

    candidates.extend(candidate_rows)
    mentions.extend(mention_rows_to_add)
    statements.extend(new_rows)

    all_candidate_ids = {row["candidate_id"] for row in candidates}
    final_target = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    if len(final_target) != 44:
        raise SystemExit(f"Refusing: expected 44 final source statements, found {len(final_target)}")
    classifications = {"true": 0, "false": 0, "unset": 0}
    for row in final_target:
        q = row.get("qualifiers", {})
        value = q.get("relation_candidate")
        classifications["true" if value is True else "false" if value is False else "unset"] += 1
        if value is None:
            raise SystemExit(f"Refusing: unset classification remains on {row['statement_id']}")
        if value is True and (row.get("subject_candidate_id") is None or row.get("object_candidate_id") is None) and not q.get("open_endpoint_reason"):
            raise SystemExit(f"Refusing: open relation lacks an endpoint reason: {row['statement_id']}")
        if value is False and not q.get("relation_candidate_note"):
            raise SystemExit(f"Refusing: nonrelation lacks its classification reason: {row['statement_id']}")
        if q.get("mentioned_candidate_ids"):
            unknown = set(q["mentioned_candidate_ids"]) - all_candidate_ids
            if unknown:
                raise SystemExit(f"Refusing: unknown mentioned candidate(s) for {row['statement_id']}: {sorted(unknown)}")
        if row.get("original_quote") and row["original_quote"] not in segment_text:
            raise SystemExit(f"Refusing: quote span is outside the source segment: {row['statement_id']}")
    if classifications != {"true": 35, "false": 9, "unset": 0}:
        raise SystemExit(f"Refusing: classification distribution differs from plan: {classifications}")

    all_mentions = [row for row in mentions if row.get("segment_id") == SEGMENT_ID]
    for row in all_mentions:
        a, b = int(row["start_char"]), int(row["end_char"])
        if segment_text[a:b] != row["surface_form"]:
            raise SystemExit(f"Refusing: existing mention span no longer matches S0: {row['mention_id']}")
    segment_mentions = sorted(all_mentions, key=lambda row: (int(row["start_char"]), int(row["end_char"])))
    for left, right in zip(segment_mentions, segment_mentions[1:]):
        if int(left["end_char"]) > int(right["start_char"]):
            raise SystemExit(f"Refusing: overlapping mention spans: {left['mention_id']} / {right['mention_id']}")

    coverage_row = next(row for row in coverage if row.get("segment_id") == SEGMENT_ID)
    coverage_row["disposition"] = "reviewed"
    coverage_row["migration_status"] = "complete"
    coverage_row["source_line_ranges"] = "L15-21"
    coverage_row["note"] = (
        "S2完成印刷p.143正文L15-21语义复核：将Rosa在Florence/罗马的受众、Stoicism的传播与作用、"
        "艺术家/顾客偏好及De’ Rossi赞助和金融断言分开；拆出公爵经匿名代理人提出的六类作品请求，"
        "补登记匿名主教与代理人候选。对照PDF物理页28记录self-control、1667、de’ Rossi及利息标点；"
        "脚注1-6保留原有引用边界并修正注5/注6正文回链。未改写S0，未写S6正式关系。"
    )

    # Check all touched footnote references resolve back to the expected notes.
    for note_id, body_ids in [(note5_id, requested_ids), (note6_id, note6_body_ids)]:
        links = footnote_map[note_id]["qualifiers"].get("linked_body_statement_ids", [])
        if links != body_ids:
            raise SystemExit(f"Refusing: p.143 footnote link set is inconsistent for {note_id}")

    print("PREVIEW" if not args.apply else "APPLY PLAN")
    print(f"segment={SEGMENT_ID}; existing=23; added={len(new_rows)}; final=44")
    print(f"classification={classifications}; candidates_added={len(candidate_rows)}; mentions_added={len(mention_rows_to_add)}")
    print("new candidate IDs: cand-11948, cand-11949")
    print("corrected: Florence/Rome setting mappings; churchmen, client, work and audience endpoints; note 5 and note 6 backlinks")
    print("S0 unchanged; every quote and mention span verified against the source segment")
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
    print("Wrote 4 tables; backups saved with suffix", BACKUP_SUFFIX)


if __name__ == "__main__":
    main()
