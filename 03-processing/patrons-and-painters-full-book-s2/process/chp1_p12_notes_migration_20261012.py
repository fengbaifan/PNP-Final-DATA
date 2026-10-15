#!/usr/bin/env python3
"""Split and link the printed p.12 notes after protected S0/table checks."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
NOTE_SEG = "chp-1:01_CHP-1_sec_ii:l168-239"
BODY_SEG = "chp-1:01_CHP-1_sec_ii:l62-71"
SOURCE_FULL = ROOT / "02-sources" / "02-Markdown" / "01_CHP-1.md"
OLD_IDS = {
    "st-chp1-secii-notes-modeli-disputed",
    "st-chp1-secii-notes-bibliographic-citations",
}
BACKUP_SUFFIX = ".bak-s2-chp1-secii-p12-notes-20261012"
EXPECTED = {
    "book-statements.jsonl": "637372df7cd3cf87532dc091588cfceef0e2898805db1cc205a0c04bb3f7e7b2",
    "entity-candidates.csv": "7633e01ea64ac602d44eecf6a388a4ca5e09404a32200157bf2d98b6b0fc9b26",
    "mentions.csv": "4f135d0feb79a16699d4c585f5e04ddf7c67d7d1a81c0a728a2e70dde7e77111",
    "s2-coverage.csv": "79c18fb804d68333f777b67acd1d444c6b6ca9300ca239b546f3b4296742d205",
}
SOURCE_SHA = "2c99c1b372f756b1482d746f5714fe930b538118792b52a3de0834f585d4f3fb"
SEGMENT_SHA = "b5560e20ceb3b9b531266ac26966dd0a7f76c6ce8bbc82f6664a9a95d68af258"
SEGMENT_ASSET_SHA = "1b5890ce028c421718abcb28e4c6dc4070be1bc71597a96247b32ebee42e2268"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def normalize_with_offsets(text: str) -> tuple[str, list[int]]:
    chars: list[str] = []
    offsets: list[int] = []
    prior_space = False
    for index, char in enumerate(text):
        if char.isspace():
            if not prior_space:
                chars.append(" ")
                offsets.append(index)
            prior_space = True
        else:
            chars.append(char)
            offsets.append(index)
            prior_space = False
    return "".join(chars), offsets


def excerpt(lines: list[str], start: int, end: int, phrase: str) -> str:
    raw = "\n".join(lines[start - 1 : end])
    normalized, positions = normalize_with_offsets(raw)
    target = " ".join(phrase.split())
    offset = normalized.find(target)
    if offset < 0:
        raise ValueError(f"quote missing from S0 L{start}-{end}: {phrase}")
    return raw[positions[offset] : positions[offset + len(target) - 1] + 1]


def normalized_span(text: str, phrase: str) -> tuple[int, int, str]:
    normalized, positions = normalize_with_offsets(text)
    target = " ".join(phrase.split())
    offset = normalized.find(target)
    if offset < 0:
        raise ValueError(f"mention phrase missing from flattened source segment: {phrase}")
    start = positions[offset]
    end = positions[offset + len(target) - 1] + 1
    surface = text[start:end]
    if "\n" in surface or "\r" in surface:
        raise ValueError(f"mention surface crosses a source line: {phrase}")
    return start, end, surface


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after all protected checks pass; default is preview")
    args = parser.parse_args()

    for name, expected in EXPECTED.items():
        actual = digest(TABLES / name)
        if actual != expected:
            raise SystemExit(f"protected hash mismatch for {name}: {actual}")
    if digest(SOURCE_FULL) != SOURCE_SHA:
        raise SystemExit("immutable S0 full-chapter source hash changed")

    statements = read_jsonl(TABLES / "book-statements.jsonl")
    candidates = read_csv(TABLES / "entity-candidates.csv")
    mentions = read_csv(TABLES / "mentions.csv")
    coverage = read_csv(TABLES / "s2-coverage.csv")
    statement_by_id = {row["statement_id"]: row for row in statements}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    mention_by_id = {row["mention_id"]: row for row in mentions}

    if not OLD_IDS.issubset(statement_by_id):
        raise SystemExit(f"expected p.12 broad note rows missing: {sorted(OLD_IDS - statement_by_id.keys())}")
    if any(row["statement_id"].startswith("st-chp1-secii-p12-") for row in statements):
        raise SystemExit("p.12 replacement statement IDs already exist")
    if any(row["candidate_id"] in {"cand-11872", "cand-11873", "cand-11874"} for row in candidates):
        raise SystemExit("one or more proposed p.12 candidate IDs already exist")

    segment = next(row for row in read_jsonl(TABLES / "segments.jsonl") if row["segment_id"] == NOTE_SEG)
    segment_path = ROOT / segment["source_file"]
    if segment.get("sha256") != SEGMENT_SHA or segment.get("asset_sha256") != SEGMENT_ASSET_SHA:
        raise SystemExit("registered note segment fingerprints changed")
    if digest(segment_path) != SEGMENT_ASSET_SHA:
        raise SystemExit("p.12 source-segment asset changed")
    segment_lines = segment_path.read_text(encoding="utf-8-sig").splitlines()
    # Existing mention offsets are defined on a whitespace-flattened S0 line slice.
    segment_text = " ".join(segment_lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])
    source_lines = SOURCE_FULL.read_text(encoding="utf-8-sig").splitlines()
    if "Brigand, 1962, p. 251" not in " ".join(source_lines[460:463]):
        raise SystemExit("expected S0 OCR form of the Briganti citation not found")
    if "Mammcrtine" not in " ".join(source_lines[463:466]) or "Andrea Sacelli" not in " ".join(source_lines[465:468]):
        raise SystemExit("expected S0 OCR variants in note 1 not found")

    # Check the existing p.12 mention slice offsets before using them in new claims.
    existing_p12_mentions = [
        "m-chp1-secii-0430", "m-chp1-secii-0427", "m-chp1-secii-0431", "m-chp1-secii-0504",
        "m-chp1-secii-0437", "m-chp1-secii-0587", "m-s2-surface-e848a1b328875688", "m-chp1-secii-0432",
        "m-chp1-secii-0662", "m-chp1-secii-0434", "m-chp1-secii-0436", "m-chp1-secii-0438",
        "m-chp1-secii-0439", "m-s2-surface-ddbb7b48014b2a8d", "m-chp1-secii-0440", "m-chp1-secii-0441",
        "m-chp1-secii-0392", "m-s2-surface-6c2ec2dfdda13e14", "m-chp1-secii-0442", "m-chp1-secii-0443",
        "m-chp1-secii-0563", "m-chp1-secii-0505", "m-chp1-secii-0479", "m-chp1-secii-0507", "m-chp1-secii-0462",
    ]
    for mid in existing_p12_mentions:
        if mid not in mention_by_id:
            raise SystemExit(f"expected p.12 mention missing: {mid}")
        row = mention_by_id[mid]
        start, end = int(row["start_char"]), int(row["end_char"])
        if segment_text[start:end] != row["surface_form"]:
            raise SystemExit(f"existing p.12 mention span mismatch: {mid}")

    required_candidates = {
        "cand-2962", "cand-3489", "cand-3490", "cand-3096", "cand-4473", "cand-3511", "cand-3556",
        "cand-3118", "cand-2802", "cand-3491", "cand-0484", "cand-3464", "cand-3492", "cand-3493",
        "cand-3451", "cand-3494", "cand-3495", "cand-1494", "cand-2818", "cand-4557", "cand-3501",
        "cand-6356", "cand-3513", "cand-5467", "cand-1842", "cand-4834", "cand-4552",
    }
    if not required_candidates.issubset(candidate_by_id):
        raise SystemExit(f"required existing candidate missing: {sorted(required_candidates - candidate_by_id.keys())}")

    old_max = max(int(row["candidate_id"].removeprefix("cand-")) for row in candidates if row["candidate_id"].startswith("cand-"))
    if old_max != 11871:
        raise SystemExit(f"candidate sequence changed; expected 11871 as current maximum, found {old_max}")

    new_candidates = [
        {
            "candidate_id": "cand-11872", "index_entry_id": "",
            "canonical_name": "Alleged series of Pietro da Cortona modelli for Palazzo Doria-Pamfili gallery ceiling (disputed)",
            "index_page_range": "", "suggested_type": "work", "status": "open", "index_source_file": "", "sub_entry": "",
            "detail": "Source-defined group: Grassi's claimed Cortona attribution, explicitly said by Haskell not to have won general acceptance. Existing accepted card 04-knowledge/units/works/cortona-doria-pamfili-modelli-disputed.md is available for later S3 alignment; this S2 reference does not create a second KU.",
            "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{NOTE_SEG}#L461",
        },
        {
            "candidate_id": "cand-11873", "index_entry_id": "",
            "canonical_name": "Supposed bozzetto for the Barberini Salone (judged unconvincing; identity unresolved)",
            "index_page_range": "", "suggested_type": "work", "status": "open", "index_source_file": "", "sub_entry": "",
            "detail": "Haskell calls this the so-called Barberini Salone bozzetto, kept in the palace, and finds it unconvincing. No maker, title, catalogue number, or exact object identity is supplied. Existing accepted card 04-knowledge/units/works/barberini-salone-bozzetto-disputed.md is available for later S3 alignment; this S2 reference does not create a second KU.",
            "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{NOTE_SEG}#L463",
        },
        {
            "candidate_id": "cand-11874", "index_entry_id": "",
            "canonical_name": "Unspecified Andrea Sacchi modello for a Roman Capuchin church altarpiece (title unresolved)",
            "index_page_range": "", "suggested_type": "work", "status": "open", "index_source_file": "", "sub_entry": "",
            "detail": "One of the modelli Haskell says were recorded under Andrea Sacchi; the altarpiece and Capuchin church are not individually identified. Haskell reports a Colnaghi May-June 1961 no. 2 handling reference and Denis Mahon's collection at the time. Existing accepted card 04-knowledge/units/works/sacchi-capuchin-altarpiece-modello.md is available for later S3 alignment; this S2 reference does not create a second KU.",
            "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{NOTE_SEG}#L467",
        },
    ]
    candidates.extend(new_candidates)
    candidate_by_id.update({row["candidate_id"]: row for row in new_candidates})

    def source_claim(
        sid: str, marker: int, start: int, end: int, quote_phrase: str,
        subject: str | None, obj: str | None, predicate: str,
        claim: str, qualification: str, mentioned: list[str], body_id: str,
        *, relation: bool, extra: dict | None = None,
    ) -> dict:
        q = {
            "source_line_start": start, "source_line_end": end,
            "printed_page": 12, "pdf_physical_page": 11,
            "claim": claim, "speaker": f"Haskell footnote {marker}",
            "text_layer": "substantive footnote", "qualification": qualification,
            "relation_candidate": relation,
            "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
            "footnote_marker": marker, "footnote_number": marker,
            "footnote_segment": NOTE_SEG,
            "footnote_refs": [{"marker": marker, "segment_id": NOTE_SEG, "source_line": start}],
            "related_segment": BODY_SEG if body_id != "st-chp1-secii-l48-60-07" else "chp-1:01_CHP-1_sec_ii:l48-60",
            "related_body_statement_ids": [body_id], "linked_body_statement_ids": [body_id],
            "cited_material_not_independently_consulted": False,
            "footnote_link_status": "linked", "footnote_text_pending": False,
        }
        if relation:
            q["relation_candidate_note"] = "This remains an S2 relation candidate; no S6 formal edge is created."
        else:
            q["relation_candidate_note"] = "This records a source claim or evaluation, not a formal S6 edge."
        if extra:
            q.update(extra)
        row = {
            "statement_id": sid, "segment_id": NOTE_SEG,
            "subject_candidate_id": subject, "object_candidate_id": obj,
            "predicate": predicate, "qualifiers": q,
            "original_quote": excerpt(source_lines, start, end, quote_phrase),
            "origin": "book", "source_file": "02-sources/02-Markdown/01_CHP-1.md",
        }
        return row

    def citation_claim(
        sid: str, marker: int, start: int, end: int, quote_phrase: str,
        author_candidate: str, publication_candidate: str, locator: str,
        claim: str, body_id: str, note: str, mention_ids: list[str],
    ) -> dict:
        return source_claim(
            sid, marker, start, end, quote_phrase,
            "cand-2962", publication_candidate, "cites",
            claim,
            "The citation identifies Haskell's source locator; the publication and cited pages were not independently consulted.",
            ["cand-2962", author_candidate, publication_candidate], body_id,
            relation=True,
            extra={
                "text_layer": "bibliographic citation",
                "relation_candidate_note": "This records Haskell's citation path; it does not assert the cited publication's contents beyond the stated claim.",
                "cited_material_not_independently_consulted": True,
                "citation_candidate_id": author_candidate,
                "citation_publication_candidate_id": publication_candidate,
                "citation_locator": locator,
                "citations": [{"source_candidate_id": author_candidate, "publication_candidate_id": publication_candidate, "locator": locator}],
                "citation_note": note,
                "citation_mention_ids": mention_ids,
            },
        )

    body_for_marker = {
        1: "st-chp1-secii-l48-60-07",
        2: "st-chp1-secii-l62-71-02",
        3: "st-chp1-secii-l62-71-03",
        4: "st-chp1-secii-l62-71-11",
        5: "st-chp1-secii-l62-71-13",
    }
    body_marker_source_line = {1: 430, 2: 435, 3: 439, 4: 454, 5: 459}
    for marker, sid in body_for_marker.items():
        if sid not in statement_by_id:
            raise SystemExit(f"expected p.12 body claim missing for footnote {marker}: {sid}")

    # The five source-specific note statements preserve the note's distinctions and uncertainty.
    additions: list[dict] = []
    additions.append(source_claim(
        "st-chp1-secii-p12-n1-grassi-article-authored-by", 1, 461, 461,
        "L. Grassi published in 1957", "cand-11346", "cand-3489", "authored_by",
        "Haskell identifies L. Grassi as the author/publisher of a 1957 article about Cortona modelli.",
        "The article title and pp. 28–43 are supplied by the printed bibliography; the article itself was not independently consulted.",
        ["cand-11346", "cand-3489"], body_for_marker[1], relation=True,
        extra={"bibliographic_entry_candidate_id": "cand-11346", "cited_material_not_independently_consulted": True},
    ))
    additions.append(source_claim(
        "st-chp1-secii-p12-n1-grassi-cortona-series-claim", 1, 461, 462,
        "a series of modelli by Pietro da Cortona", "cand-11872", "cand-3096", "claimed_attributed_to",
        "Haskell reports that Grassi claimed a series of modelli for the Palazzo Doria-Pamfili gallery ceiling as works by Pietro da Cortona.",
        "This is a reported attribution, not a confirmed authorship relation; the exact members of the series are not identified.",
        ["cand-11872", "cand-3096", "cand-3490", "cand-3489"], body_for_marker[1], relation=False,
        extra={"attribution_source_candidate_id": "cand-3489", "open_group_membership": True},
    ))
    additions.append(source_claim(
        "st-chp1-secii-p12-n1-grassi-series-not-generally-accepted", 1, 462, 462,
        "but these have not won general acceptance", "cand-11872", None, "attribution_not_generally_accepted",
        "Haskell says Grassi's proposed Cortona modelli had not won general acceptance.",
        "This preserves Haskell's assessment and does not settle the attribution independently.",
        ["cand-11872"], body_for_marker[1], relation=False,
    ))
    additions.append(citation_claim(
        "st-chp1-secii-p12-n1-cites-briganti-1962-p251", 1, 462, 463,
        "Brigand, 1962, p. 251", "cand-3511", "cand-4473", "Briganti, 1962, p. 251",
        "Haskell cites Briganti's 1962 Cortona monograph at page 251 in connection with the disputed attribution.",
        body_for_marker[1], "S0 OCR reads Brigand; the print reads Briganti. Neither the book nor page 251 was independently consulted.",
        ["m-chp1-secii-p12-n1-briganti-p251"],
    ))
    additions.append(source_claim(
        "st-chp1-secii-p12-n1-barberini-bozzetto-evaluation", 1, 463, 464,
        "Nor is the so-called bozzetto for the Barberini Salone, kept in the palace, at all convincing",
        "cand-11873", None, "judged_unconvincing",
        "Haskell judges the so-called Barberini Salone bozzetto unconvincing.",
        "The note does not identify its maker, exact object, or catalogue number; “so-called” and the evaluation are retained.",
        ["cand-11873", "cand-3556", "cand-3118"], body_for_marker[1], relation=False,
    ))
    additions.append(source_claim(
        "st-chp1-secii-p12-n1-barberini-bozzetto-kept-in-palace", 1, 463, 464,
        "the Barberini Salone, kept in the palace", "cand-11873", "cand-3118", "located_at",
        "Haskell reports that the supposed Barberini Salone bozzetto was kept in the Barberini palace.",
        "This is a historical location as stated by Haskell, not a present-day location check.",
        ["cand-11873", "cand-3556", "cand-3118"], body_for_marker[1], relation=True,
        extra={"time_scope": "Haskell's account; current location not verified"},
    ))
    additions.append(source_claim(
        "st-chp1-secii-p12-n1-waterhouse-reports-camassei-modello", 1, 464, 465,
        "Professor Waterhouse has pointed out to me the existence of a modello", "cand-2802", "cand-3491", "reported_modello",
        "Haskell says E. K. Waterhouse pointed out the existence of a Camassei modello.",
        "This records the scholarly report as Haskell presents it; it is not an independent present-day object verification.",
        ["cand-2802", "cand-3491", "cand-0484"], body_for_marker[1], relation=False,
        extra={"reported_artist_candidate_id": "cand-0484"},
    ))
    additions.append(source_claim(
        "st-chp1-secii-p12-n1-camassei-modello-created-by", 1, 464, 465,
        "a modello by Camassei", "cand-3491", "cand-0484", "created_by",
        "The note attributes the reported modello to Andrea Camassei.",
        "The work is the source-defined modello described in the note; the existing accepted work card is available for S3 alignment.",
        ["cand-3491", "cand-0484"], body_for_marker[1], relation=True,
    ))
    additions.append(source_claim(
        "st-chp1-secii-p12-n1-camassei-modello-formerly-barberini", 1, 465, 466,
        "once belonging to the Barberini", "cand-3491", "cand-3464", "owned_by",
        "Haskell reports that the Camassei modello had formerly belonged to the Barberini.",
        "The family-level reference is retained; the note gives no dates for this ownership state.",
        ["cand-3491", "cand-3464"], body_for_marker[1], relation=True,
        extra={"time_scope": "former ownership; dates unspecified"},
    ))
    additions.append(source_claim(
        "st-chp1-secii-p12-n1-camassei-modello-pinacoteca-location", 1, 465, 466,
        "now in the Pinacoteca Vaticana", "cand-3491", "cand-3492", "located_at",
        "Haskell reports the Camassei modello as then being in the Pinacoteca Vaticana.",
        "“Now” is scoped to Haskell's account; the note's inventory numbers are recorded separately and not treated as current catalogue data.",
        ["cand-3491", "cand-3492"], body_for_marker[1], relation=True,
        extra={"time_scope": "Haskell's account; current location not verified"},
    ))
    additions.append(source_claim(
        "st-chp1-secii-p12-n1-camassei-modello-inventory-numbers", 1, 465, 466,
        "No. 820, formerly 539 m", "cand-3491", None, "reported_inventory_numbers",
        "Haskell gives the Pinacoteca Vaticana number as 820 and the former number as 539 m.",
        "These are the numbers as printed in Haskell; they are not independently checked against a museum catalogue.",
        ["cand-3491", "cand-3492"], body_for_marker[1], relation=False,
        extra={"inventory_number": "820", "former_inventory_number": "539 m", "time_scope": "as recorded by Haskell"},
    ))
    additions.append(source_claim(
        "st-chp1-secii-p12-n1-sacchi-modelli-recorded", 1, 466, 467,
        "A number of modelli by Andrea Sacelli are also recorded", "cand-3493", "cand-3451", "modelli_recorded_for_artist",
        "Haskell says a number of modelli by Andrea Sacchi were recorded.",
        "S0 OCR reads Sacelli; the page image reads Sacchi. The note does not enumerate these models; this is not a claim that every model is identified.",
        ["cand-3493", "cand-3451"], body_for_marker[1], relation=True,
        extra={"open_endpoint_reason": "No individual models are enumerated in this sentence."},
    ))
    additions.append(source_claim(
        "st-chp1-secii-p12-n1-sacchi-specific-modelo-for-altarpiece", 1, 467, 468,
        "One of these, for an altarpiece in the Capuchin church in Rome", "cand-11874", None, "model_for",
        "Haskell identifies one Sacchi modello as being for an altarpiece in a Capuchin church in Rome.",
        "The altarpiece title and exact church are not supplied. The model is a source-defined work candidate; no target work is inferred.",
        ["cand-11874", "cand-3493", "cand-3451", "cand-3494", "cand-3126"], body_for_marker[1], relation=True,
        extra={"open_endpoint_reason": "The altarpiece is unnamed and cannot be aligned to an individual work from this note."},
    ))
    additions.append(source_claim(
        "st-chp1-secii-p12-n1-sacchi-modelo-created-by", 1, 466, 467,
        "modelli by Andrea Sacelli", "cand-11874", "cand-3493", "created_by",
        "The specific modello is one of the works Haskell attributes to Andrea Sacchi.",
        "The scan reads Sacchi although S0 OCR has Sacelli; no separate external attribution source was consulted in this pass.",
        ["cand-11874", "cand-3493"], body_for_marker[1], relation=True,
    ))
    additions.append(source_claim(
        "st-chp1-secii-p12-n1-sacchi-modelo-handled-by-colnaghi", 1, 467, 468,
        "recently passed through a London gallery (Colnaghi’s, May-June 1961, No. 2)",
        "cand-11874", "cand-3495", "handled_by",
        "Haskell reports that the Sacchi modello passed through Colnaghi’s London gallery in May–June 1961, catalogue no. 2.",
        "This is a handling/provenance report, not evidence of a completed sale. The accepted catalogue card is a later S3 alignment target.",
        ["cand-11874", "cand-3495", "cand-1422"], body_for_marker[1], relation=True,
        extra={"time": "May-June 1961", "catalogue_number": "2", "role": "gallery handling"},
    ))
    additions.append(source_claim(
        "st-chp1-secii-p12-n1-sacchi-modelo-in-mahon-collection", 1, 468, 468,
        "now in the collection of Mr Denis Mahon", "cand-11874", "cand-1494", "owned_by",
        "Haskell reports the Sacchi modello as then being in Denis Mahon's collection.",
        "“Now” is scoped to Haskell's account and does not establish current ownership.",
        ["cand-11874", "cand-1494"], body_for_marker[1], relation=True,
        extra={"time_scope": "Haskell's account; present ownership not verified", "role": "collector"},
    ))

    citation_specs = [
        ("st-chp1-secii-p12-n2-cites-wittkower-1958-p218", 2, 469, 469, "Wittkower, 1958, p. 218", "cand-2818", "cand-4557", "Wittkower, 1958, p. 218", body_for_marker[2], "Exact locator; the cited page and publication were not independently consulted.", "m-chp1-secii-p12-n2-wittkower-p218"),
        ("st-chp1-secii-p12-n3-cites-golzio-1933-4-p301-2", 3, 470, 470, "Golzio, 1933-4, pp. 301-2", "cand-3501", "cand-6356", "Golzio, 1933–4, pp. 301–302", body_for_marker[3], "The article's full title is supplied by the printed bibliography; the article and cited pages were not independently consulted.", "m-chp1-secii-p12-n3-golzio-p301-2"),
        ("st-chp1-secii-p12-n4-cites-tacchi-venturi-1935-p147", 4, 471, 471, "Tacchi-Venturi, 1935, p. 147", "cand-3513", "cand-5467", "Tacchi-Venturi, 1935, p. 147", body_for_marker[4], "The full article citation is supplied by the printed bibliography; the article and cited page were not independently consulted.", "m-chp1-secii-p12-n4-tacchi-venturi-p147"),
        ("st-chp1-secii-p12-n5-cites-pascoli-vol1-pages", 5, 472, 472, "Pascoli, I, pp. 59, 61 and 132", "cand-1842", "cand-4834", "Pascoli, vol. I, pp. 59, 61, 132", body_for_marker[5], "The cited pages and volume were not independently consulted.", "m-chp1-secii-p12-n5-pascoli-vol1"),
        ("st-chp1-secii-p12-n5-cites-pascoli-vol2-pages", 5, 472, 472, "II, pp. 390 and 395", "cand-1842", "cand-4552", "Pascoli, vol. II, pp. 390, 395", body_for_marker[5], "The preceding “Pascoli” governs this volume locator; the cited pages and volume were not independently consulted.", "m-chp1-secii-p12-n5-pascoli-vol2"),
    ]
    # Briganti is already included above; add the remaining five bibliographic notes.
    for sid, marker, start, end, phrase, author, publication, locator, body_id, note, mention_id in citation_specs:
        additions.append(citation_claim(
            sid, marker, start, end, phrase, author, publication, locator,
            f"Haskell cites {locator} in footnote {marker}.", body_id, note, [mention_id],
        ))

    # Confirm every source quotation before modifying any table in memory.
    for row in additions:
        q = row["qualifiers"]
        if not row["original_quote"] or " ".join(row["original_quote"].split()) not in " ".join(source_lines[int(q["source_line_start"]) - 1 : int(q["source_line_end"]) ]):
            raise SystemExit(f"statement quotation check failed: {row['statement_id']}")
        if row["subject_candidate_id"] and row["subject_candidate_id"] not in candidate_by_id:
            raise SystemExit(f"unknown subject candidate in {row['statement_id']}")
        if row["object_candidate_id"] and row["object_candidate_id"] not in candidate_by_id:
            raise SystemExit(f"unknown object candidate in {row['statement_id']}")

    new_mentions_specs = [
        ("m-chp1-secii-p12-n1-cortona-modelli-group", "cand-11872", "a series of modelli", "Source-defined disputed group; Grassi's attribution is explicitly qualified."),
        ("m-chp1-secii-p12-n1-barberini-bozzetto", "cand-11873", "the so-called bozzetto", "Source-defined work reference; maker and exact object remain unknown."),
        ("m-chp1-secii-p12-n1-sacchi-one-of-these-modeli", "cand-11874", "One of these", "Source-defined individual Sacchi modello; exact altarpiece is not named."),
        ("m-chp1-secii-p12-n1-briganti-p251", "cand-4473", "Brigand, 1962, p. 251", "S0 OCR reads Brigand; the p.12 scan reads Briganti. Cited book and page were not consulted."),
        ("m-chp1-secii-p12-n2-wittkower-p218", "cand-4557", "Wittkower, 1958, p. 218", "Exact p.12 note 2 locator; the cited page and publication were not independently consulted."),
        ("m-chp1-secii-p12-n3-golzio-p301-2", "cand-6356", "Golzio, 1933-4, pp. 301-2", "Exact p.12 note 3 locator; cited pages and article were not independently consulted."),
        ("m-chp1-secii-p12-n4-tacchi-venturi-p147", "cand-5467", "Tacchi-Venturi, 1935, p. 147", "Exact p.12 note 4 locator; cited page and article were not independently consulted."),
        ("m-chp1-secii-p12-n5-pascoli-vol1", "cand-4834", "Pascoli, I, pp. 59, 61 and 132", "Exact p.12 note 5 vol. I locator; cited pages were not independently consulted."),
        ("m-chp1-secii-p12-n5-pascoli-vol2", "cand-4552", "II, pp. 390 and 395", "Exact p.12 note 5 vol. II locator; preceding Pascoli governs; cited pages were not independently consulted."),
    ]
    new_mentions: list[dict[str, str]] = []
    for mid, cid, phrase, note in new_mentions_specs:
        if mid in mention_by_id:
            raise SystemExit(f"new mention ID already exists: {mid}")
        start, end, surface = normalized_span(segment_text, phrase)
        if surface != phrase:
            raise SystemExit(f"mention surface mismatch: {mid}: {surface!r}")
        new_mentions.append({
            "mention_id": mid, "segment_id": NOTE_SEG, "candidate_id": cid,
            "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
        })
    mentions.extend(new_mentions)
    mention_by_id.update({row["mention_id"]: row for row in new_mentions})

    # Keep existing S0 mention spans, but record print-confirmed OCR corrections in S2 metadata.
    candidate_by_id["cand-3491"]["canonical_name"] = "Saints Peter and Paul baptising in the Mammertine prison"
    candidate_by_id["cand-3491"]["detail"] = (
        "Specific Camassei modello reported by Waterhouse; S0 OCR reads Mammcrtine, the p.12 scan reads Mammertine, "
        "and the existing accepted card uses Mamertine. Inventory numbers are only as reported by Haskell; "
        "existing accepted work card 04-knowledge/units/works/camassei-peter-paul-mamertine-modello.md is available for S3 alignment."
    )
    candidate_by_id["cand-3493"]["canonical_name"] = "Andrea Sacchi"
    candidate_by_id["cand-3493"]["detail"] = (
        "The p.12 note names the artist; S0 OCR reads Andrea Sacelli while the page image reads Andrea Sacchi. "
        "Identity remains an S3 alignment to existing 04-knowledge/units/persons/andrea-sacchi.md; no new KU is created here."
    )
    candidate_by_id["cand-3511"]["canonical_name"] = "Briganti"
    candidate_by_id["cand-3511"]["detail"] = (
        "Scholar named as Brigand in S0 OCR; the p.12 scan reads Briganti. The bibliography identifies the cited 1962 Cortona book, "
        "but the scholar's full identity remains open and the cited page was not independently consulted."
    )

    citation_detail_additions = {
        "cand-4473": " Haskell cites p. 251 in printed p. 12 note 1; the cited page and book were not independently consulted.",
        "cand-4557": " Haskell cites p. 218 in printed p. 12 note 2; the cited page and book were not independently consulted.",
        "cand-6356": " Haskell cites pp. 301–302 in printed p. 12 note 3; the cited pages and article were not independently consulted.",
        "cand-5467": " Haskell cites p. 147 in printed p. 12 note 4; the cited page and article were not independently consulted.",
        "cand-4834": " Haskell cites pp. 59, 61 and 132 in printed p. 12 note 5; cited pages were not independently consulted.",
        "cand-4552": " Haskell cites pp. 390 and 395 in printed p. 12 note 5; cited pages were not independently consulted.",
        "cand-11346": " Haskell's printed p. 12 note 1 describes Grassi's claimed Cortona series; the article itself was not independently consulted.",
    }
    for cid, addition in citation_detail_additions.items():
        detail = candidate_by_id[cid].get("detail", "")
        if addition.strip() not in detail:
            candidate_by_id[cid]["detail"] = detail + addition

    rebuilt = [row for row in statements if row["statement_id"] not in OLD_IDS] + additions
    statements_after = {row["statement_id"]: row for row in rebuilt}
    footnote_ids = {
        1: [row["statement_id"] for row in additions if row["qualifiers"].get("footnote_marker") == 1],
        2: ["st-chp1-secii-p12-n2-cites-wittkower-1958-p218"],
        3: ["st-chp1-secii-p12-n3-cites-golzio-1933-4-p301-2"],
        4: ["st-chp1-secii-p12-n4-cites-tacchi-venturi-1935-p147"],
        5: ["st-chp1-secii-p12-n5-cites-pascoli-vol1-pages", "st-chp1-secii-p12-n5-cites-pascoli-vol2-pages"],
    }
    for marker, body_id in body_for_marker.items():
        q = statements_after[body_id].setdefault("qualifiers", {})
        q["footnote_marker"] = marker
        q["footnote_number"] = marker
        q["footnote_markers"] = [marker]
        ref = {"marker": marker, "segment_id": NOTE_SEG, "source_line": body_marker_source_line[marker]}
        refs = q.setdefault("footnote_refs", [])
        if ref not in refs:
            refs.append(ref)
        linked = q.setdefault("footnote_statement_ids", [])
        for sid in footnote_ids[marker]:
            if sid not in linked:
                linked.append(sid)
        q["footnote_text_pending"] = False
        q["footnote_link_status"] = "linked"

    # The p.12 note replaces a broad p.12 row; the p.11 internal reference remains with p.11 note 1.
    p11_note1_ids = [
        "st-chp1-secii-p11-n1-gini-letter-authored-by",
        "st-chp1-secii-p11-n1-gini-letter-subject-cortona",
        "st-chp1-secii-p11-n1-cites-claretta-p516",
    ]
    chp2_crossref_id = "st-chp2-secii-l147-193-chapter1-crossref"
    if chp2_crossref_id not in statements_after:
        raise SystemExit("chapter 2 internal cross-reference row is missing")
    crossref_q = statements_after[chp2_crossref_id].setdefault("qualifiers", {})
    crossref_q["linked_statement_ids"] = p11_note1_ids
    for sid in p11_note1_ids:
        if sid not in statements_after:
            raise SystemExit(f"p.11 note 1 target row is missing: {sid}")
        q = statements_after[sid].setdefault("qualifiers", {})
        links = q.setdefault("linked_statement_ids", [])
        if chp2_crossref_id not in links:
            links.append(chp2_crossref_id)

    # Replace stale reciprocal p.12 link; retain any unrelated links on the p.11 body claim.
    p11_body = statements_after["st-chp1-secii-l48-60-07"]
    p11_body_q = p11_body.setdefault("qualifiers", {})
    linked_statements = [sid for sid in p11_body_q.get("linked_statement_ids", []) if sid not in OLD_IDS]
    linked_statements.extend(footnote_ids[1])
    p11_body_q["linked_statement_ids"] = list(dict.fromkeys(linked_statements))

    coverage_row = next((row for row in coverage if row.get("segment_id") == NOTE_SEG), None)
    if coverage_row is None:
        raise SystemExit("combined footnote coverage row is missing")
    coverage_addition = (
        " Printed p.12 (PDF physical p.11) notes 1–5 were checked against the page image and split into source-specific claims and exact citation locators. "
        "The Cortona series remains a disputed Grassi attribution; the Barberini bozzetto is kept separate; Camassei provenance and Sacchi's specific altarpiece modello are recorded with historical time scope and open endpoints. "
        "Existing accepted cards are noted as later S3 alignment targets; no duplicate KUs or S6 formal relations were created. "
        "S0 OCR Brigand/Mammcrtine/Sacelli is preserved while the scan reads Briganti/Mammertine/Sacchi. Cited pages and publications were not independently consulted. "
        "The p.12 body-note links are reciprocal; the Chapter 2 cross-reference to printed p.11 note 1 now points to the p.11 Gini note rather than the p.12 note."
    )
    if coverage_addition.strip() not in coverage_row.get("note", ""):
        coverage_row["note"] = coverage_row.get("note", "") + coverage_addition

    # Verify all new note references and mention spans before preview/apply.
    for row in additions:
        q = row["qualifiers"]
        for cid in q.get("mentioned_candidate_ids", []):
            if cid not in candidate_by_id:
                raise SystemExit(f"unknown mentioned candidate {cid} in {row['statement_id']}")
        for ref in q.get("footnote_refs", []):
            if ref["segment_id"] != NOTE_SEG or ref["marker"] != q["footnote_marker"]:
                raise SystemExit(f"invalid footnote reference in {row['statement_id']}")
    for row in new_mentions:
        start, end = int(row["start_char"]), int(row["end_char"])
        if segment_text[start:end] != row["surface_form"]:
            raise SystemExit(f"new mention span check failed: {row['mention_id']}")
        if row["candidate_id"] not in candidate_by_id:
            raise SystemExit(f"new mention candidate missing: {row['mention_id']}")

    print("protected four-table hashes, immutable S0 source, and registered p.12 note segment matched")
    print(f"planned: replace {len(OLD_IDS)} combined note statements with {len(additions)} source-specific statements")
    print(f"planned: add {len(new_candidates)} open S2 candidate references and {len(new_mentions)} exact mentions")
    print("planned: keep existing accepted cards as later S3 alignment targets; no KUs or formal relations are written")
    print("planned: add reciprocal p.12 body-note links and correct the Chapter 2 reference to printed p.11 note 1")
    print(f"coverage disposition/status remains {coverage_row['disposition']}/{coverage_row['migration_status']}")
    if not args.apply:
        print("preview only; no files written. Pass --apply to write after inspecting this plan.")
        return

    for name in EXPECTED:
        original = TABLES / name
        backup = original.with_name(original.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists; refusing to overwrite: {backup.name}")
    for name in EXPECTED:
        shutil.copy2(TABLES / name, TABLES / (name + BACKUP_SUFFIX))
    write_jsonl(TABLES / "book-statements.jsonl", rebuilt)
    write_csv(TABLES / "entity-candidates.csv", candidates)
    write_csv(TABLES / "mentions.csv", mentions)
    write_csv(TABLES / "s2-coverage.csv", coverage)
    print("applied; four pre-write recovery copies created with suffix " + BACKUP_SUFFIX)
    for name in EXPECTED:
        print(name, digest(TABLES / name))


if __name__ == "__main__":
    main()
