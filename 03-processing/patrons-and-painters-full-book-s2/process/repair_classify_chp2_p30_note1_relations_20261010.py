from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
MENTIONS = ROOT / "04-knowledge/tables/mentions.csv"
SOURCE = ROOT / "02-sources/02-Markdown/02_CHP-2_sec_i.md"
EXPECTED_TABLE_SHA = "e18e6e4384c08705e539a2f43968956c78d031853d1e3911b71f7dc7250efe72"
EXPECTED_MENTIONS_SHA = "c061cc51c3bcac8e78086f6950586703c97cdd133728ee7b319ce8739cfadde8"
TABLE_BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp2-p30-note1-relations-20261010")
MENTIONS_BACKUP = MENTIONS.with_name(MENTIONS.name + ".bak-s2-chp2-p30-note1-relations-20261010")
SEGMENT_ID = "chp-2:02_CHP-2_sec_i:l124-157"
SOURCE_FILE = "02-sources/02-Markdown/02_CHP-2_sec_i.md"
PUBLISHER_ID = "st-chp2-seci-l124-157-bizoni-journal-published"

CLASSIFICATIONS = {
    "st-chp2-seci-l124-157-albani-study-andrians": (
        "The note infers that Albani must have studied The Andrians after arriving in Rome in 1601–1602. Preserve 'must have' as Haskell's inference, not an established encounter.",
        "Albani's study of The Andrians is explicitly inferred in Haskell's footnote; no direct evidence of the encounter is supplied here.",
    ),
    "st-chp2-seci-l124-157-albani-study-worship": (
        "The note infers that Albani must have studied The Worship of Venus after arriving in Rome in 1601–1602. Preserve 'must have' as Haskell's inference, not an established encounter.",
        "Albani's study of The Worship of Venus is explicitly inferred in Haskell's footnote; no direct evidence of the encounter is supplied here.",
    ),
    "st-chp2-seci-l124-157-colonna-sale-letter": (
        "The note identifies a Prince Francesco Colonna letter announcing the Palestrina sale and says it was published by Michele Giustiniani. This records a source report, not independent examination of the letter.",
        "Haskell's footnote identifies the letter as Prince Francesco Colonna's and says it announced the sale; the letter's date and original location are not supplied.",
    ),
    "st-chp2-seci-l124-157-letter-1605-recipient": (
        "The footnote explicitly identifies Maffeo Barberini as the recipient of the 26 July 1605 letter in Paris; the writer remains unidentified.",
        "Haskell's note explicitly states that the 26 July 1605 letter was addressed to Maffeo Barberini in Paris; its writer is not named.",
    ),
    "st-chp2-seci-l124-157-letter-1611-described": (
        "The note describes a 30 April 1611 letter, 'presumably' from Maffeo to an unnamed architect. Retain the uncertainty and do not create a recipient or formal authorship edge.",
        "The source reports draft and completed versions of a letter presumed to be from Maffeo to an unnamed architect; the sender attribution remains qualified and the recipient unidentified.",
    ),
    "st-chp2-seci-l124-157-reni-letter-described": (
        "The footnote identifies a letter from Guido Reni dated 15 February 1614 and cites its publication in Pollak (1913), p. 44. The recipient is unnamed and the letter was not independently consulted.",
        "Haskell's note reports a letter from Guido Reni in Rome dated 15 February 1614; the recipient is not named and the cited edition was not independently consulted.",
    ),
}

EXPECTED_ENDPOINTS = {
    "st-chp2-seci-l124-157-albani-study-andrians": ("cand-0021", "cand-4249"),
    "st-chp2-seci-l124-157-albani-study-worship": ("cand-0021", "cand-4248"),
    "st-chp2-seci-l124-157-colonna-sale-letter": ("cand-0808", "cand-4387"),
    "st-chp2-seci-l124-157-letter-1605-recipient": ("cand-4364", "cand-0209"),
    "st-chp2-seci-l124-157-letter-1611-described": ("cand-0209", "cand-4363"),
    "st-chp2-seci-l124-157-reni-letter-described": ("cand-2124", "cand-4382"),
}

NEW_MENTION = {
    "mention_id": "m-chp2-seci-l124-157-0082",
    "segment_id": SEGMENT_ID,
    "candidate_id": "cand-1200",
    "surface_form": "Giustiniani",
    "start_char": "2141",
    "end_char": "2152",
    "note": "Vincenzo Giustiniani in the footnote phrase 'Giustiniani’s friend'; distinguish him from Michele Giustiniani named as publisher at line 157.",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def counts(rows: list[dict]) -> dict[str, int]:
    flag = lambda row: (row.get("qualifiers") or {}).get("relation_candidate")
    complete = lambda row: bool(row.get("subject_candidate_id") and row.get("object_candidate_id"))
    true_rows = [row for row in rows if flag(row) is True]
    false_rows = [row for row in rows if flag(row) is False]
    return {
        "statements": len(rows),
        "relation_true": len(true_rows),
        "relation_true_with_two_endpoints": sum(complete(row) for row in true_rows),
        "relation_true_open": sum(not complete(row) for row in true_rows),
        "relation_false": len(false_rows),
        "double_endpoint_unclassified": sum(complete(row) and flag(row) not in (True, False) for row in rows),
    }


def build_statement(
    statement_id: str,
    subject: str,
    object_: str,
    predicate: str,
    claim: str,
    note: str,
    quote: str,
    related_ids: list[str],
) -> dict:
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": 147,
            "source_line_end": 147,
            "claim": claim,
            "speaker": "Haskell footnote",
            "text_layer": "footnote description",
            "print_page": "30",
            "pdf_page": 11,
            "footnote_marker": 1,
            "footnote_segment": SEGMENT_ID,
            "related_segment": "chp-2:02_CHP-2_sec_i:l108-119",
            "related_source_lines": [111],
            "linked_body_statement_ids": related_ids,
            "relation_candidate": True,
            "relation_candidate_note": note,
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_FILE,
    }


def load_inputs():
    statement_raw = TABLE.read_bytes()
    mentions_raw = MENTIONS.read_bytes()
    require(sha256(TABLE) == EXPECTED_TABLE_SHA, "book-statements.jsonl changed since review")
    require(sha256(MENTIONS) == EXPECTED_MENTIONS_SHA, "mentions.csv changed since review")
    statement_bom = statement_raw.startswith(b"\xef\xbb\xbf")
    statement_newline = b"\r\n" if b"\r\n" in statement_raw else b"\n"
    rows = [json.loads(line.decode("utf-8-sig")) for line in statement_raw.splitlines() if line.strip()]
    require(len({row["statement_id"] for row in rows}) == len(rows), "duplicate statement_id")
    by_id = {row["statement_id"]: row for row in rows}
    required_ids = set(CLASSIFICATIONS) | {PUBLISHER_ID}
    require(required_ids <= set(by_id), "one or more reviewed statements are absent")

    mention_bom = mentions_raw.startswith(b"\xef\xbb\xbf")
    mentions_text = mentions_raw.decode("utf-8-sig")
    mentions_newline = "\r\n" if "\r\n" in mentions_text else "\n"
    mention_rows = list(csv.DictReader(io.StringIO(mentions_text, newline="")))
    fieldnames = list(csv.DictReader(io.StringIO(mentions_text, newline="")).fieldnames or [])
    require(fieldnames and {"mention_id", "segment_id", "candidate_id", "surface_form", "start_char", "end_char", "note"} <= set(fieldnames),
            "mentions.csv columns do not satisfy the expected schema")
    existing_mention_ids = {row["mention_id"] for row in mention_rows}
    require(NEW_MENTION["mention_id"] not in existing_mention_ids, "new mention ID already exists")

    with (ROOT / "04-knowledge/tables/entity-candidates.csv").open(encoding="utf-8-sig", newline="") as handle:
        candidate_ids = {row["candidate_id"] for row in csv.DictReader(handle)}
    with (ROOT / "04-knowledge/tables/s2-coverage.csv").open(encoding="utf-8-sig", newline="") as handle:
        segment_ids = {row["segment_id"] for row in csv.DictReader(handle)}
    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    source_segment = "\n".join(source_lines[123:157])
    require(SEGMENT_ID in segment_ids, "footnote segment is absent from S2 coverage")
    require("remarkable journal kept by Giustiniani’s friend Bernardo Bizoni published by Anna Banti" in source_lines[146],
            "footnote 1 source line changed")
    require(source_segment[2114:2177] == "remarkable journal kept by Giustiniani’s friend Bernardo Bizoni",
            "existing journal mention offsets no longer match source segment")
    require(source_segment[int(NEW_MENTION["start_char"]):int(NEW_MENTION["end_char"])] == "Giustiniani",
            "new Giustiniani mention offsets do not match source segment")
    require(len(source_lines) >= 157, "source file ends before reviewed footnote")

    for statement_id, (_, expected_claim) in CLASSIFICATIONS.items():
        row = by_id[statement_id]
        q = row.get("qualifiers") or {}
        require(q.get("relation_candidate") not in (True, False), f"{statement_id} already classified")
        require((row.get("subject_candidate_id"), row.get("object_candidate_id")) == EXPECTED_ENDPOINTS[statement_id],
                f"{statement_id} endpoints changed since review")
        require(q.get("claim"), f"{statement_id} has no source claim")
        require(row.get("segment_id") == SEGMENT_ID, f"{statement_id} is outside the reviewed segment")
        start, end = q.get("source_line_start"), q.get("source_line_end")
        require(isinstance(start, int) and isinstance(end, int) and start <= end and end <= len(source_lines),
                f"{statement_id} has invalid source line anchors")
        require(all(candidate_id in candidate_ids for candidate_id in EXPECTED_ENDPOINTS[statement_id]),
                f"{statement_id} candidate endpoint is missing")

    publisher = by_id[PUBLISHER_ID]
    publisher_q = publisher.get("qualifiers") or {}
    require((publisher.get("subject_candidate_id"), publisher.get("object_candidate_id")) == ("cand-0377", "cand-4378"),
            "Bizoni publisher statement endpoints changed since review")
    require(publisher_q.get("publisher_candidate_id") == "cand-4379", "publisher candidate anchor changed")
    require(publisher_q.get("relation_candidate") not in (True, False), "publisher statement already classified")
    require(all(candidate_id in candidate_ids for candidate_id in ("cand-0377", "cand-4378", "cand-4379", "cand-1200")),
            "Bizoni journal, publisher, keeper, or Giustiniani candidate is missing")

    new_ids = {
        "st-chp2-seci-l124-157-bizoni-kept-journal",
        "st-chp2-seci-l124-157-giustiniani-friend-bizoni",
    }
    require(not new_ids & set(by_id), "one or more new statement IDs already exist")
    before = counts(rows)
    require(before == {
        "statements": 12682,
        "relation_true": 3765,
        "relation_true_with_two_endpoints": 3749,
        "relation_true_open": 16,
        "relation_false": 1760,
        "double_endpoint_unclassified": 4324,
    }, f"unexpected statement counts: {before}")
    require(len(mention_rows) == 27489, f"unexpected mention count: {len(mention_rows)}")
    return rows, by_id, mention_rows, fieldnames, statement_bom, statement_newline, mention_bom, mentions_newline, source_lines, before


def serialize_statements(rows: list[dict], bom: bool, newline: bytes) -> bytes:
    out = []
    for i, row in enumerate(rows):
        line = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if i == 0 and bom:
            line = b"\xef\xbb\xbf" + line
        out.append(line + newline)
    return b"".join(out)


def append_mention(raw: bytes, fieldnames: list[str], mention: dict, bom: bool, newline: str) -> bytes:
    text = io.StringIO(newline="")
    writer = csv.DictWriter(text, fieldnames=fieldnames, lineterminator=newline, extrasaction="ignore")
    writer.writerow(mention)
    row_bytes = text.getvalue().encode("utf-8")
    if not raw.endswith((b"\r\n", b"\n")):
        raw += newline.encode("ascii")
    return raw + row_bytes


def write_atomic(path: Path, payload: bytes) -> Path:
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".tmp-", delete=False) as handle:
        handle.write(payload)
        temp_path = Path(handle.name)
    os.replace(temp_path, path)
    return temp_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="apply reviewed S2 repairs; default is dry-run")
    args = parser.parse_args()
    (rows, by_id, mention_rows, mention_columns, statement_bom, statement_newline,
     mention_bom, mentions_newline, source_lines, before) = load_inputs()

    for statement_id, (note, claim) in CLASSIFICATIONS.items():
        row = by_id[statement_id]
        qualifiers = dict(row.get("qualifiers") or {})
        qualifiers["relation_candidate"] = True
        qualifiers["relation_candidate_note"] = note
        row["qualifiers"] = qualifiers

    publisher = by_id[PUBLISHER_ID]
    publisher["subject_candidate_id"] = "cand-4378"
    publisher["object_candidate_id"] = "cand-4379"
    publisher_q = dict(publisher.get("qualifiers") or {})
    publisher_q.pop("publisher_candidate_id", None)
    publisher_q["relation_candidate"] = True
    publisher_q["relation_candidate_note"] = (
        "The source says Anna Banti published Bernardo Bizoni's journal; encode the archive-to-publisher direction. "
        "The publication is a book-reported bibliographic description, not independent examination of the edition."
    )
    publisher["qualifiers"] = publisher_q

    source_quote = source_lines[146]
    linked_ids = list((publisher_q.get("linked_body_statement_ids") or []))
    new_rows = [
        build_statement(
            "st-chp2-seci-l124-157-bizoni-kept-journal",
            "cand-4378",
            "cand-0377",
            "journal_kept_by_reported",
            "Haskell's footnote describes Bernardo Bizoni as keeper of the journal.",
            "The source explicitly says the journal was kept by Bizoni; it does not establish a title or edition, and its contents were not independently examined.",
            source_quote,
            linked_ids,
        ),
        build_statement(
            "st-chp2-seci-l124-157-giustiniani-friend-bizoni",
            "cand-1200",
            "cand-0377",
            "friendship_reported",
            "Haskell's footnote identifies Bernardo Bizoni as a friend of Vincenzo Giustiniani.",
            "The source calls Bizoni 'Giustiniani's friend'; the immediate book context identifies Vincenzo Giustiniani, distinct from Michele Giustiniani named as publisher in a later note. No duration or further nature of the friendship is stated.",
            source_quote,
            linked_ids,
        ),
    ]
    rows.extend(new_rows)
    after = counts(rows)
    require(after == {
        "statements": 12684,
        "relation_true": 3774,
        "relation_true_with_two_endpoints": 3758,
        "relation_true_open": 16,
        "relation_false": 1760,
        "double_endpoint_unclassified": 4317,
    }, f"unexpected projected statement counts: {after}")
    mention_rows.append(NEW_MENTION)
    require(len(mention_rows) == 27490, "unexpected projected mention count")

    print(json.dumps({
        "action": "apply" if args.apply else "dry-run",
        "classified_existing_statements": len(CLASSIFICATIONS) + 1,
        "new_statements": [row["statement_id"] for row in new_rows],
        "publisher_endpoints_corrected": ["cand-4378", "cand-4379"],
        "new_mention": NEW_MENTION,
        "before": before,
        "after": after,
        "mentions_before_after": [27489, len(mention_rows)],
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    require(not TABLE_BACKUP.exists() and not MENTIONS_BACKUP.exists(), "recovery backup already exists")
    shutil.copy2(TABLE, TABLE_BACKUP)
    shutil.copy2(MENTIONS, MENTIONS_BACKUP)
    temps: list[Path] = []
    try:
        new_table = serialize_statements(rows, statement_bom, statement_newline)
        new_mentions = append_mention(MENTIONS.read_bytes(), mention_columns, NEW_MENTION, mention_bom, mentions_newline)
        temps.append(write_atomic(TABLE, new_table))
        temps.append(write_atomic(MENTIONS, new_mentions))

        written_rows = [json.loads(line) for line in TABLE.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        require(counts(written_rows) == after, "post-write statement counts do not match preview")
        written_by_id = {row["statement_id"]: row for row in written_rows}
        require((written_by_id[PUBLISHER_ID]["subject_candidate_id"], written_by_id[PUBLISHER_ID]["object_candidate_id"]) ==
                ("cand-4378", "cand-4379"), "publisher endpoint correction was not persisted")
        require("publisher_candidate_id" not in (written_by_id[PUBLISHER_ID].get("qualifiers") or {}),
                "redundant publisher candidate field remains")
        require(all((written_by_id[sid].get("qualifiers") or {}).get("relation_candidate") is True
                    for sid in set(CLASSIFICATIONS) | {PUBLISHER_ID} | {r["statement_id"] for r in new_rows}),
                "one or more relation classifications were not persisted")
        with MENTIONS.open(encoding="utf-8-sig", newline="") as handle:
            saved_mentions = list(csv.DictReader(handle))
        saved_mention = next((m for m in saved_mentions if m["mention_id"] == NEW_MENTION["mention_id"]), None)
        require(saved_mention == {key: str(NEW_MENTION.get(key, "")) for key in mention_columns},
                "new Giustiniani mention was not persisted exactly")
        require(len(saved_mentions) == 27490, "post-write mention count is wrong")
        print(json.dumps({
            "result": "applied",
            "counts": counts(written_rows),
            "mentions": len(saved_mentions),
            "statement_sha256": sha256(TABLE),
            "mentions_sha256": sha256(MENTIONS),
            "backups": [str(TABLE_BACKUP.relative_to(ROOT)), str(MENTIONS_BACKUP.relative_to(ROOT))],
        }, ensure_ascii=False, indent=2))
    except Exception:
        shutil.copy2(TABLE_BACKUP, TABLE)
        shutil.copy2(MENTIONS_BACKUP, MENTIONS)
        raise
    finally:
        for temp in temps:
            if temp.exists():
                temp.unlink()


if __name__ == "__main__":
    main()
