#!/usr/bin/env python3
"""Resolve the ten unset S2 statements in the opening of chapter 17."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "17_CHP-17_sec_i.md"
SEGMENT_ID = "chp-17:17_CHP-17_sec_i:l3-6"
SOURCE_FILE = "02-sources/02-Markdown/17_CHP-17_sec_i.md"
EXPECTED_SEGMENT_HASH = "b5b2aba63a1ef5d99362371c82568c057e985b8f9ff46687903268faa600568d"
EXPECTED_STATEMENTS_HASH = "f5b0a13ea25ef200e1129b19d6afcab22a552cff27085422b13e187194bc6362"
BACKUP_SUFFIX = ".bak-s2-chp17-p379-opening-body-20261015"
NEW_STATEMENT_IDS = {
    "st-chp17-pi-manfrin-acquired-enormous-fortune",
    "st-chp17-pi-feeling-affected-patrons-collectors",
}
PENDING_IDS = {
    "st-chp17-pi-epoch-of-venetian-republic-ending",
    "st-chp17-pi-feeling-reached-patrons-and-collectors",
    "st-chp17-pi-men-turned-to-the-venetian-past",
    "st-chp17-pi-manfrin-caricature-of-old-order-opponent",
    "st-chp17-pi-manfrin-nouveau-riche-rise",
    "st-chp17-pi-manfrin-success-as-symbolic-trend",
    "st-chp17-pi-manfrin-aristocratic-denigrator-phrase",
    "st-chp17-pi-manfrin-accused-of-businessman-vices",
    "st-chp17-pi-manfrin-unpopular-and-acquired-fortune",
    "st-chp17-pi-manfrin-fortune-discreditable-means",
}
RATIONALES = {
    "st-chp17-pi-epoch-of-venetian-republic-ending": (
        "Broad authorial context about an unnamed population's mood and an approaching political end; "
        "no distinct relation endpoints are asserted."
    ),
    "st-chp17-pi-feeling-reached-patrons-and-collectors": (
        "This is Haskell's broad cultural synthesis; the feeling, cited texts, and affected collector group "
        "are not defined as distinct relation endpoints."
    ),
    "st-chp17-pi-men-turned-to-the-venetian-past": (
        "The sentence describes an unnamed group and qualifies its motive with 'as if'; it remains "
        "historical context rather than a relation between identified entities."
    ),
    "st-chp17-pi-manfrin-caricature-of-old-order-opponent": (
        "This is Haskell's evaluative characterization of Manfrin; the generalized conservative audience "
        "is not a bounded relation endpoint."
    ),
    "st-chp17-pi-manfrin-nouveau-riche-rise": (
        "Socio-biographical description and characterization of Manfrin, without a distinct relation endpoint."
    ),
    "st-chp17-pi-manfrin-success-as-symbolic-trend": (
        "This is Haskell's interpretation of Manfrin as symbolic of a historical trend, not a relation "
        "between identified entities."
    ),
    "st-chp17-pi-manfrin-aristocratic-denigrator-phrase": (
        "The hostile phrase is attributed to an unidentified denigrator; the source does not identify a "
        "speaker endpoint or establish the phrase as fact."
    ),
    "st-chp17-pi-manfrin-accused-of-businessman-vices": (
        "The accusation is attributed to unnamed accusers; the quoted labels are not adopted as facts, "
        "and no identified accuser endpoint is available."
    ),
    "st-chp17-pi-manfrin-unpopular-and-acquired-fortune": (
        "The reported local reception has no identified audience endpoint; the separate fortune outcome "
        "is recorded in its own statement."
    ),
    "st-chp17-pi-manfrin-fortune-discreditable-means": (
        "The source characterizes the means as somewhat discreditable but identifies no transaction, "
        "counterparty, or other relation endpoint."
    ),
}
OCR_BASIS = "CHP-17.pdf physical page 1, printed folio i."


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def correction(line: int, ocr: str, print_text: str) -> dict:
    return {
        "source_file": SOURCE_FILE,
        "source_line": line,
        "ocr": ocr,
        "print": print_text,
        "basis": OCR_BASIS,
    }


def build_output() -> tuple[Path, bytes, dict]:
    path = TABLES / "book-statements.jsonl"
    raw = path.read_bytes()
    if digest(raw) != EXPECTED_STATEMENTS_HASH:
        raise ValueError(f"Stale statement table: {digest(raw)}")
    if any(statement_id in raw.decode("utf-8-sig") for statement_id in NEW_STATEMENT_IDS):
        raise ValueError(f"A new statement ID already exists: {sorted(NEW_STATEMENT_IDS)}")

    segment_rows = [
        json.loads(line)
        for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    segment = next((row for row in segment_rows if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != EXPECTED_SEGMENT_HASH:
        raise ValueError("The chapter 17 page-i segment fingerprint changed.")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    if not source_lines[2].startswith("OR a full generation") or not source_lines[3].startswith("Ffeeling"):
        raise ValueError("The source spans for the opening paragraph changed.")
    if "turned to' the past" not in source_lines[3] or "where he made himself hated and soon acquired" not in source_lines[4]:
        raise ValueError("The source spans for the group and Manfrin statements changed.")

    updated_rows: dict[str, dict] = {}

    def set_row(
        statement_id: str,
        *,
        quote: str,
        claim: str | None = None,
        qualification: str | None = None,
        corrections: list[dict] | None = None,
        predicate: str | None = None,
        mention_ids: list[str] | None = None,
        note3: bool = False,
        remove_note2: bool = False,
    ) -> None:
        row = row_by_id[statement_id]
        q = dict(row["qualifiers"])
        q["relation_candidate"] = False
        q["relation_candidate_note"] = RATIONALES[statement_id]
        if claim is not None:
            q["claim"] = claim
        if qualification is not None:
            q["qualification"] = qualification
        if corrections is not None:
            q["ocr_corrections"] = corrections
        if mention_ids is not None:
            q["mentioned_candidate_ids"] = mention_ids
        if note3:
            q.update(
                {
                    "footnote_marker": "3",
                    "footnote_segment": "chp-17:17_CHP-17_intro:l7-13",
                    "footnote_line_range": "L10-L10",
                    "footnote_text_pending": False,
                    "footnote_body_link_status": "linked",
                    "footnote_body_line_range": "L5-L5",
                    "footnote_note_statement_ids": [
                        "st-chp17-pi-note3-pamphlet-locator",
                        "st-chp17-pi-note3-unpopularity-assessment",
                    ],
                    "footnote_link_note": (
                        "P.379 note 3 cites controversial material and explicitly discusses Manfrin's "
                        "reported unpopularity."
                    ),
                }
            )
        if remove_note2:
            for key in (
                "footnote_marker",
                "footnote_segment",
                "footnote_line_range",
                "footnote_text_pending",
                "footnote_body_link_status",
                "footnote_body_line_range",
                "footnote_note_statement_ids",
                "footnote_link_note",
            ):
                q.pop(key, None)
        change = {"qualifiers": q, "original_quote": quote}
        if predicate is not None:
            change["predicate"] = predicate
        updated_rows[statement_id] = change

    row_by_id: dict[str, dict] = {}
    for line in raw.decode("utf-8-sig").splitlines():
        if line.strip():
            item = json.loads(line)
            row_by_id[item["statement_id"]] = item
    target_rows = [
        row for row in row_by_id.values()
        if row.get("segment_id") == SEGMENT_ID
        and row.get("qualifiers", {}).get("relation_candidate") is None
    ]
    if {row["statement_id"] for row in target_rows} != PENDING_IDS:
        raise ValueError("The pending S2 statement IDs for this segment changed.")
    if len(row_by_id) != 15098:
        raise ValueError(f"Unexpected statement count: {len(row_by_id)}")

    set_row(
        "st-chp17-pi-epoch-of-venetian-republic-ending",
        quote=(
            "OR a full generation before the Republic finally collapsed there was a general\n"
            "Ffeeling that an epoch was drawing to a close."
        ),
        corrections=[correction(3, "OR a full generation", "FOR a full generation"),
                     correction(4, "Ffeeling", "feeling")],
    )
    set_row(
        "st-chp17-pi-feeling-reached-patrons-and-collectors",
        quote=(
            "Ffeeling that an epoch was drawing to a close. There are countless references to this in the "
            "political speeches and literature of the time,"
        ),
        claim="Haskell says there were countless references to this feeling in the political speeches and literature of the time.",
        qualification=(
            "The speeches and literary works are not individually named or linked to specific texts."
        ),
        corrections=[correction(4, "Ffeeling", "feeling")],
    )
    set_row(
        "st-chp17-pi-men-turned-to-the-venetian-past",
        quote=(
            "The feeling is embodied in the activities of a number of men who turned to' the past rather "
            "than the present or the future—as if anxious to give subsequent generations some impression "
            "of what Venice had been like in the great days of her independence."
        ),
        corrections=[
            correction(4, "turned to' the past", "turned to the past"),
        ],
    )
    set_row(
        "st-chp17-pi-manfrin-caricature-of-old-order-opponent",
        quote=(
            "Girolamo Manfrin was almost the caricature of a type of figure that has at all times depressed "
            "the conservative supporters of an old order.1"
        ),
    )
    set_row(
        "st-chp17-pi-manfrin-nouveau-riche-rise",
        quote=(
            "He was a nouveau-riche business man, who through sheer unscrupulous Balzacian energy and "
            "talent achieved a high position in a society where such achievements were despised in favour "
            "of the more gracious attributes of life."
        ),
    )
    set_row(
        "st-chp17-pi-manfrin-success-as-symbolic-trend",
        quote=(
            "Such men have always made their mark, but there are periods in history when their success "
            "appears symbolic of a whole trend. This was to be the case with Manfrin."
        ),
    )
    set_row(
        "st-chp17-pi-manfrin-aristocratic-denigrator-phrase",
        quote="in mezzo al fango, e dalla Merda nato in the words of one of his aristocratic denigrators2",
    )
    set_row(
        "st-chp17-pi-manfrin-accused-of-businessman-vices",
        quote=(
            "he was accused of all the characteristic evils of the successful businessman—‘iracondo’ "
            "incivil, avaro, ingrato, /Sospettoso, infedel’."
        ),
        remove_note2=True,
    )
    set_row(
        "st-chp17-pi-manfrin-unpopular-and-acquired-fortune",
        quote="where he made himself hated",
        claim="Haskell says Manfrin made himself hated in Dalmatia.",
        qualification=(
            "The audience is not identified; retain Haskell's report without converting the place name "
            "into a relation endpoint."
        ),
        predicate="reported_as_having_made_himself_hated_in_dalmatia",
        mention_ids=["cand-1512", "cand-10678"],
        note3=True,
    )
    set_row(
        "st-chp17-pi-manfrin-fortune-discreditable-means",
        quote="much of it through somewhat discreditable means",
    )

    feeling_affected = {
        "statement_id": "st-chp17-pi-feeling-affected-patrons-collectors",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": None,
        "object_candidate_id": "cand-4129",
        "predicate": "ended_era_feeling_affected_patrons_and_picture_collectors",
        "qualifiers": {
            "source_line_start": 4,
            "source_line_end": 4,
            "printed_page": None,
            "printed_folio": "i",
            "pdf_physical_page": 1,
            "claim": "Haskell says the feeling eventually affected patrons and picture collectors.",
            "speaker": "Haskell",
            "text_layer": "authorial context",
            "qualification": (
                "The feeling and affected social group are broad and not defined as distinct entities."
            ),
            "mentioned_candidate_ids": ["cand-4129"],
            "relation_candidate": False,
            "relation_candidate_note": (
                "Broad contextual effect without a defined feeling entity or bounded recipient group."
            ),
        },
        "original_quote": "and eventually it began to affect the patrons and picture collectors.",
        "origin": "book",
        "source_file": SOURCE_FILE,
    }
    fortune = {
        "statement_id": "st-chp17-pi-manfrin-acquired-enormous-fortune",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-1512",
        "object_candidate_id": None,
        "predicate": "soon_acquired_an_enormous_fortune",
        "qualifiers": {
            "source_line_start": 5,
            "source_line_end": 5,
            "printed_page": None,
            "printed_folio": "i",
            "pdf_physical_page": 1,
            "claim": "Haskell says Manfrin soon acquired an enormous fortune.",
            "speaker": "Haskell",
            "text_layer": "authorial report",
            "qualification": (
                "No amount or specific transactions are supplied; this is an economic outcome, not a "
                "separate relation to an identified person or work."
            ),
            "mentioned_candidate_ids": ["cand-1512"],
            "relation_candidate": False,
            "relation_candidate_note": "Personal wealth outcome without an identified transaction endpoint.",
        },
        "original_quote": "soon acquired an enormous fortune",
        "origin": "book",
        "source_file": SOURCE_FILE,
    }

    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    body = raw[len(bom) :]
    output: list[bytes] = []
    seen: set[str] = set()
    inserted: set[str] = set()
    for raw_line in body.splitlines(keepends=True):
        ending = b"\r\n" if raw_line.endswith(b"\r\n") else b"\n" if raw_line.endswith(b"\n") else b""
        content = raw_line[: -len(ending)] if ending else raw_line
        row = json.loads(content)
        statement_id = row.get("statement_id")
        if statement_id in updated_rows:
            row.update(updated_rows[statement_id])
            output.append(json.dumps(row, ensure_ascii=False).encode("utf-8") + ending)
            seen.add(statement_id)
        else:
            output.append(raw_line)
        insertions = {
            "st-chp17-pi-feeling-reached-patrons-and-collectors": feeling_affected,
            "st-chp17-pi-manfrin-unpopular-and-acquired-fortune": fortune,
        }
        if statement_id in insertions:
            output.append(
                json.dumps(insertions[statement_id], ensure_ascii=False).encode("utf-8")
                + (ending or b"\n")
            )
            inserted.add(insertions[statement_id]["statement_id"])
    if seen != PENDING_IDS or inserted != NEW_STATEMENT_IDS:
        raise ValueError("The update set or split insertion did not complete.")
    updated = bom + b"".join(output)
    preview = {
        "segment_id": SEGMENT_ID,
        "classified_existing": len(updated_rows),
        "all_existing_nonrelations": len(updated_rows),
        "new_statements": sorted(NEW_STATEMENT_IDS),
        "segment_source_line_corrections": 4,
        "global_statement_rows_after": 15100,
        "output_sha256": digest(updated),
        "backup": str(path.with_name(path.name + BACKUP_SUFFIX)),
    }
    return path, updated, preview


def apply_output(path: Path, data: bytes) -> None:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise FileExistsError(f"Backup already exists: {backup}")
    shutil.copy2(path, backup)
    temp: Path | None = None
    try:
        fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
        temp = Path(name)
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    except Exception:
        shutil.copy2(backup, path)
        raise
    finally:
        if temp and temp.exists():
            temp.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    path, data, preview = build_output()
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    if args.apply:
        apply_output(path, data)
        print("APPLIED")
    else:
        print("PREVIEW ONLY; no table changed.")


if __name__ == "__main__":
    main()
